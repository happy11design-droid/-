#!/usr/bin/env python3
"""毎朝のテーマ監視と候補の抽出（`新分析ツール/テーマ監視_手順書.md` 手順T1〜T3）

使い方:
  tools/theme_scan.py <出力ファイル.md> [--asof YYYY-MM-DD]

やること（数値の計算と事実の一覧だけ。売買の判断はしない）:
  1. 監視銘柄（`新分析ツール/テーマ監視銘柄.md`）とS&P500の構成銘柄の日足（2年分）をYahooから取得する（1分ほど）。
  2. テーマの強さ: グループごとの騰落率（1週・1カ月・3カ月）と順位、テーマ指数（監視銘柄の等金額平均）のステージ（30週線）、
     早めの警告（監視銘柄のうち50日線より上の割合、テーマ指数の50日線、S&P500に対する相対的な強さ）。
  3. ヒートマップ: Finvizの業種別の騰落率（S&P500以外も含む全米の業種）で、テーマの外で強くなっている業種。
  4. 候補: バックテストで採用した条件に当てはまった銘柄（ボリンジャー メソッドIII、ミネルヴィニのトレンドテンプレート＋上抜け、
     ワインスタイン10週の上抜け〔週の最終取引日のみ〕）と、注文の目安（指値・損切り・建玉の割合）。
取得できなかった値は「取得不可」と書き、推測で埋めない。
"""
import argparse
import bisect
import csv
import datetime as dt
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_swing as bs
import backtest_theme as bth
import backtest_trend as bt
from backtest_lib import DEFAULT_CACHE, MEMBERS_URL, curl, market_regime, sma

RISK, STOP = 0.02, 0.15
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"


def fetch_daily(sym):
    """直近2年の日足（配当・分割調整済み）。取得できなければ None"""
    try:
        res = json.loads(curl(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym.replace('.', '-')}?interval=1d&range=2y"))["chart"]["result"][0]
        q, off = res["indicators"]["quote"][0], res["meta"].get("gmtoffset", 0)
        adj = res["indicators"].get("adjclose", [{}])[0].get("adjclose") or q["close"]
        d = {"date": [], "o": [], "h": [], "l": [], "c": [], "v": []}
        for i, t in enumerate(res["timestamp"]):
            o, h, l, c = q["open"][i], q["high"][i], q["low"][i], q["close"][i]
            if None in (o, h, l, c):
                continue
            f = (adj[i] or c) / c
            d["date"].append(dt.datetime.utcfromtimestamp(t + off).strftime("%Y-%m-%d"))
            for k, x in zip("ohlc", (o, h, l, c)):
                d[k].append(x * f)
            d["v"].append(q["volume"][i] or 0)
        return d if len(d["c"]) > 60 else None
    except Exception:
        return None


def cut(d, asof):
    if not asof:
        return d
    n = sum(1 for x in d["date"] if x <= asof)
    return {k: v[:n] for k, v in d.items()}


def finviz_industries():
    """Finvizの業種別の騰落率。[(業種, 1週, 1カ月, 3カ月, 6カ月, 1年), ...]。取得できなければ空"""
    r = subprocess.run(["curl", "-sSL", "--max-time", "30", "-A", UA, "https://finviz.com/groups.ashx?g=industry&v=140&o=name"],
                       capture_output=True, text=True)
    html = r.stdout if r.returncode == 0 else ""
    out = []
    for r in re.findall(r"<tr[^>]*styled-row[^>]*>(.*?)</tr>", html, re.S):
        cells = [re.sub("<[^>]+>", "", c).strip() for c in re.findall(r"<td[^>]*>(.*?)</td>", r, re.S)]
        try:
            out.append((cells[1],) + tuple(float(x.rstrip("%")) / 100 for x in cells[2:7]))
        except (ValueError, IndexError):
            continue
    return out


def earnings_date(sym):
    h = curl(f"https://finance.yahoo.com/quote/{sym}/").replace('\\"', '"')
    m = re.search(r'"earningsDate":\[\{"raw":\d+,"fmt":"([0-9-]+)"', h)
    return m.group(1) if m else "取得不可"


def pct(x, d=1):
    return "取得不可" if x is None else f"{x * 100:+.{d}f}%"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--asof", help="この日の引けまでのデータで判定する（検証用）")
    a = ap.parse_args()

    wl = bth.load_watchlist()
    members_csv = curl(MEMBERS_URL)
    if not members_csv.startswith("ticker,"):
        p = os.path.join(DEFAULT_CACHE, "members.csv")
        members_csv = open(p).read() if os.path.exists(p) else "ticker,start_date,end_date\n"
    sp = [r["ticker"] for r in csv.DictReader(members_csv.splitlines()) if not r["end_date"]]
    syms = sorted(set(sp) | set(wl) | {"SPY"})
    with ThreadPoolExecutor(8) as ex:
        got = dict(zip(syms, ex.map(fetch_daily, syms)))
    got = {s: cut(d, a.asof) for s, d in got.items() if d}
    spy = got.pop("SPY")
    day = spy["date"][-1]
    data = {s: got[s] for s in wl if s in got and got[s]["date"] and got[s]["date"][-1] == day and len(got[s]["c"]) > 260}
    missing = sorted(set(wl) - set(data))

    # RSランキング（S&P500＋監視銘柄の中での百分位、最新日のみ）
    def rs_raw(c):
        return 0.4 * (c[-1] / c[-64] - 1) + 0.2 * (c[-1] / c[-127] - 1) + 0.2 * (c[-1] / c[-190] - 1) + 0.2 * (c[-1] / c[-253] - 1)
    pool = sorted(rs_raw(d["c"]) for s, d in got.items() if len(d["c"]) > 253 and d["date"][-1] == day)
    for s, d in data.items():
        bt.prepare(d)
        bs.prepare(d)
        d["sym"] = s
        if len(pool) > 50:
            d["rs"][-1] = 99 * bisect.bisect_left(pool, rs_raw(d["c"])) / (len(pool) - 1)

    L = []
    w = L.append
    w(f"# テーマ監視（{day}の引け時点）\n")
    w(f"- 監視銘柄 {len(wl)}（判定できたのは {len(data)}" + (f"、取得不可: {', '.join(missing)}" if missing else "") + "）。")
    w("- この一覧は数値と事実だけ。売買の判断は著者のノートブックが行う。\n")

    # ---- テーマの強さ ----
    w("## 1. テーマ（グループ）の強さ\n")
    w("| グループ | 銘柄数 | 1週 | 1カ月 | 3カ月 | 3カ月の順位 | 50日線より上の銘柄の割合 |")
    w("|---|---|---|---|---|---|---|")
    groups = list(dict.fromkeys(wl.values()))
    med = lambda xs: sorted(xs)[len(xs) // 2] if xs else None
    rows = []
    for g in groups:
        mem = [d for s, d in data.items() if wl[s] == g]
        r = [med([d["c"][-1] / d["c"][-1 - k] - 1 for d in mem]) for k in (5, 21, 63)]
        ab = sum(1 for d in mem if d["ma50"][-1] and d["c"][-1] > d["ma50"][-1]) / len(mem) if mem else None
        rows.append((g, len(mem), r, ab))
    order = sorted(rows, key=lambda x: -(x[2][2] or -9))
    for g, n, r, ab in rows:
        w(f"| {g} | {n} | {pct(r[0])} | {pct(r[1])} | {pct(r[2])} | {[x[0] for x in order].index(g) + 1}位 | {pct(ab, 0).lstrip('+')} |")

    idx = bth.theme_index(data, [d for d in spy["date"] if d >= spy["date"][0]])
    stage = market_regime(idx)
    c = idx["c"]
    ma50 = sma(c, 50)
    spy_c = dict(zip(spy["date"], spy["c"]))
    ratio = [x / spy_c[d] for x, d in zip(c, idx["date"])]
    rma = sma(ratio, 50)
    br = sum(1 for d in data.values() if d["ma50"][-1] and d["c"][-1] > d["ma50"][-1]) / len(data)
    warn = br < 0.4 and ma50[-1] is not None and c[-1] < ma50[-1]
    w("\n## 2. テーマ全体の状態と早めの警告\n")
    w(f"- テーマ指数（監視銘柄の等金額平均）の30週線による局面: **{stage.get(day, '判定不可')}**（上昇＝線より上かつ上向き、下落＝線より下かつ下向き、それ以外＝横ばい。ワインスタインのステージの近似）")
    w(f"- テーマ指数と50日線: {'50日線より上' if ma50[-1] and c[-1] > ma50[-1] else '50日線より下'}（乖離 {pct(c[-1] / ma50[-1] - 1) if ma50[-1] else '取得不可'}）")
    w(f"- S&P500に対する相対的な強さ: {'50日平均より上（S&P500より強い）' if rma[-1] and ratio[-1] > rma[-1] else '50日平均より下（S&P500より弱い）'}")
    w(f"- 監視銘柄のうち50日線より上の割合: {br * 100:.0f}%")
    w(f"- 警告（割合が40%未満かつテーマ指数が50日線より下）: **{'出ている' if warn else '出ていない'}**")
    w("- 参考（バックテスト）: 30週線の「下落」は高値から10〜33%下げた後に出る遅い判定。50日線・割合・相対的な強さは高値から2〜8%で出るが、誤報が年15回以上ある。"
      "警告中に新しい買いを止めると、押し目買い（ボリンジャーIII）の成績は大きく下がった（`バックテスト結果/テーマ監視銘柄・直近3年.md` 11・12節）。\n")

    # ---- ヒートマップ ----
    ind = finviz_industries()
    w("## 3. ヒートマップ（Finviz、全米の業種別の騰落率）\n")
    if a.asof:
        w(f"（注意: Finvizの値は取得した時点のもので、{a.asof}時点の値ではない）\n")
    if ind:
        w("3カ月の騰落率の上位15業種（テーマの外で強くなっている業種の確認用）:\n")
        w("| 順位 | 業種 | 1週 | 1カ月 | 3カ月 | 6カ月 | 1年 |")
        w("|---|---|---|---|---|---|---|")
        for k, r in enumerate(sorted(ind, key=lambda x: -x[3])[:15], 1):
            w(f"| {k} | {r[0]} | {pct(r[1])} | {pct(r[2])} | {pct(r[3])} | {pct(r[4])} | {pct(r[5])} |")
        rank = {r[0]: k for k, r in enumerate(sorted(ind, key=lambda x: -x[3]), 1)}
        th = ["Semiconductors", "Semiconductor Equipment & Materials", "Computer Hardware", "Communication Equipment",
              "Electronic Components", "Software - Infrastructure", "Software - Application", "Internet Content & Information"]
        w("\nテーマの業種の順位（3カ月、全" + str(len(ind)) + "業種中）: " + "、".join(f"{t} {rank[t]}位" for t in th if t in rank) + "\n")
    else:
        w("取得不可\n")

    # ---- 候補 ----
    w("## 4. 候補（バックテストで採用した条件に当てはまった銘柄）\n")
    w(f"建玉の目安: 1トレードのリスク2%・損切り15% → 1銘柄に資金の{RISK / STOP * 100:.1f}%、同時保有{int(STOP / RISK)}銘柄まで（ユーザー決定）。\n")
    cands = []
    for s, d in data.items():
        i = len(d["c"]) - 1
        if not bt.liquid(d, i, [("0000", "9999")]):
            continue
        rs = d["rs"][i]
        base = {"sym": s, "group": wl[s], "close": d["c"][i], "rs": rs, "chg": d["c"][i] / d["c"][i - 1] - 1}
        if bs.O_method3(i, d):
            cands.append({**base, "kind": "逆張り: ボリンジャー メソッドIII",
                          "why": f"%b={d['pctb'][i]:.3f}（<0.05）、21日II%={d['ii21'][i]:+.3f}（>0）",
                          "order": f"翌日の寄り付きで買い。損切り: 買値の15%下。手じまい: 引けで上部バンド（今日 {d['bb_up'][i]:.2f}）以上になった翌日の寄り付き"})
        hi, lo = d["hi"][50][i], d["lo"][50][i]
        if bt.trend_template(d, i) and hi and d["c"][i] > hi and (hi - lo) / hi <= 0.35 and d["v"][i] >= 2 * d["vol50"][i]:
            cands.append({**base, "kind": "順張り: ミネルヴィニ（トレンドテンプレート＋上抜け）",
                          "why": f"ピボット（直前50日の高値）{hi:.2f}を出来高{d['v'][i] / d['vol50'][i]:.1f}倍で上抜け、ベースの幅{(hi - lo) / hi * 100:.0f}%",
                          "order": f"翌日の寄り付きで買い。ただし寄り付きが{hi * 1.03:.2f}（ピボット+3%）を超えたら見送り。損切り: 買値の15%下。手じまい: 引けで50日線を割った翌日の寄り付き"})
        if dt.date.fromisoformat(day).weekday() == 4 and bt.E_weinstein(10, ma="10")(i, d) is not None:
            cands.append({**base, "kind": "順張り: ワインスタイン（10週の高値上抜け）",
                          "why": f"週足の終値が直前10週の高値{d['w_hi_prev'][10][i]:.2f}を出来高{d['w_vol'][i] / d['w_vol4'][i]:.1f}倍で上抜け、10週線が上向き",
                          "order": "翌日の寄り付きで買い。損切り: 買値の15%下。手じまい: 週足の終値が10週線を割った翌取引日の寄り付き"})
    if not cands:
        w("本日は該当なし（著者への送信は不要）。\n")
    else:
        cands.sort(key=lambda x: -(x["rs"] or 0))
        with ThreadPoolExecutor(4) as ex:
            eds = dict(zip([x["sym"] for x in cands], ex.map(earnings_date, [x["sym"] for x in cands])))
        for k_, v in eds.items():
            if re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
                n = (dt.date.fromisoformat(v) - dt.date.fromisoformat(day)).days
                eds[k_] = f"{v}（{n}日後）" + ("**決算が近い**" if 0 <= n <= 14 else "")
        w("| 銘柄 | グループ | 種類 | 終値 | 前日比 | RS | 当てはまった条件 | 次回決算予定日 | 注文の目安 |")
        w("|---|---|---|---|---|---|---|---|---|")
        for x in cands:
            w(f"| {x['sym']} | {x['group']} | {x['kind']} | {x['close']:.2f} | {pct(x['chg'])} | {x['rs']:.0f} | {x['why']} | {eds[x['sym']]} | {x['order']} |"
              if x["rs"] is not None else
              f"| {x['sym']} | {x['group']} | {x['kind']} | {x['close']:.2f} | {pct(x['chg'])} | 取得不可 | {x['why']} | {eds[x['sym']]} | {x['order']} |")
        w("\n- RS≧80の押し目（ボリンジャーIII）は、バックテストで成績がより安定していた（PF3.27、最大下落20%）。")
    text = "\n".join(L) + "\n"
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    open(a.out, "w").write(text)
    print(text)


if __name__ == "__main__":
    main()
