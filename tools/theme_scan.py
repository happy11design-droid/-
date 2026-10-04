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
from backtest_regime import up as regime_up
from backtest_minervini2 import add_pivot
from backtest_lib import DEFAULT_CACHE, MEMBERS_URL, curl, market_regime, rsi_wilder, sma
import backtest_crash as bcr
import backtest_compare2 as c2

SLOTS, STOP = 4, 0.15   # 同時保有4銘柄・1銘柄に資金÷4（2026-09-29 ユーザー決定。以前はリスク2%→13.3%×7銘柄）
BUY_USD = 4500          # 1銘柄に買う金額（資金18,000ドル÷4）。株数の目安に使う。資金が変わったらここを直す（2026-10-04 ユーザーの指示）
NDX_URL = "https://api.nasdaq.com/api/quote/list-type/nasdaq100"
OUT_MAX = 5   # 監視外の注目銘柄（ニュースを調べる）はRSの高い順にこの件数まで
V2_TOP = 10   # 新高値V2を当てる銘柄: 監視銘柄のうちその日のRSが上位この数まで
B_MAX = 5   # パターンB（予約注文の候補）は各ルールでこの件数まで
CRASH_MAX = 4   # 同時保有の上限（2026-09-29 に7→4）。急落の底の候補（市場全体の急落の日は20件を超えることがある）はRSの高い順にこの件数まで
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"


def fetch_daily(sym):
    """直近3年の日足（配当・分割調整済み）。取得できなければ None（新高値V2の「直前2年の最高値」に2年分以上が必要）"""
    try:
        res = json.loads(curl(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym.replace('.', '-')}?interval=1d&range=3y"))["chart"]["result"][0]
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


def load_holdings(path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "新分析ツール", "保有銘柄.md")):
    """保有銘柄.md の表（| ティッカー | 買った日 | 買値 | 株数 | ルール |）を読む"""
    out = []
    if not os.path.exists(path):
        return out
    for line in open(path, encoding="utf-8"):
        m = re.match(r"^\| ([A-Z][A-Z.]*) \| (\d{4}-\d{2}-\d{2}) \| ([0-9.]+) \| ([0-9.]*) \| ([^|]*)\|", line)
        if m:
            out.append({"sym": m.group(1), "date": m.group(2), "price": float(m.group(3)), "rule": m.group(5).strip()})
    return out


def load_trades(path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "新分析ツール", "売買記録.md")):
    """売買記録.md（売った銘柄）と保有銘柄.md（保有中）から、実際に買った記録 [{sym, date, price}] を返す"""
    out = [{"sym": h["sym"], "date": h["date"], "price": h["price"]} for h in load_holdings()]
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            m = re.match(r"^\| ([A-Z][A-Z.]*) \| (\d{4}-\d{2}-\d{2}) \| ([0-9.]+) \|", line)
            if m:
                out.append({"sym": m.group(1), "date": m.group(2), "price": float(m.group(3))})
    return out


GROUP_CAP = 2   # 同じ業種（Yahooの分類）は同時に2銘柄まで（2026-09-28 ユーザー決定。`バックテスト結果/本のルールの追加と現代風のアレンジ.md` 4節）


def bear_candles(d, since, look=5):
    """買った日以降の直近 look 取引日で、出来高2倍を伴った大陰線の日を返す（`backtest_bear_exit.py` の実体ATR1.5倍・出来高2倍と同じ定義）"""
    o, h, l, c, v, n = d["o"], d["h"], d["l"], d["c"], d["v"], len(d["c"])
    tr = [h[0] - l[0]] + [max(h[k] - l[k], abs(h[k] - c[k - 1]), abs(l[k] - c[k - 1])) for k in range(1, n)]
    atr, x = [None] * n, None
    for k in range(n):
        x = tr[k] if x is None else (x * 13 + tr[k]) / 14
        atr[k] = x if k >= 14 else None
    out = []
    for j in range(max(1, n - look), n):
        if d["date"][j] < since:
            continue
        a, v50 = atr[j - 1], d["vol50"][j]
        if a is None or not v50 or h[j] <= l[j]:
            continue
        if o[j] - c[j] >= 1.5 * a and (c[j] - l[j]) / (h[j] - l[j]) <= 0.25 and v[j] >= 2 * v50:
            out.append(f"{d['date'][j]}（実体 ATRの{(o[j] - c[j]) / a:.1f}倍・出来高{v[j] / v50:.1f}倍）")
    return "**あり** " + "、".join(out) if out else "なし"


def half_signal(d, since):
    """順張り（ミネルヴィニ・新高値V2）の半分売りの合図（2026-10-01 ユーザー決定。`バックテスト結果/半分だけ売るとオニールの空き枠.md`）。
    反転のローソク足（かぶせ線・弱気の包み足・宵の明星・流れ星）＋出来高が50日平均の1.5倍以上＋RSI(14)が前日か当日に70以上。
    買った日以降で最初に合図が出た日を返す（なければ None）"""
    import backtest_exit_combo as xc
    import backtest_exit_signals as xs
    if "rsi14" not in d:
        xs.prep(d)
    for j in range(2, len(d["c"])):
        if d["date"][j] >= since and xc.c1(d, j):
            return d["date"][j]
    return None


def dark_cloud_signal(d, since):
    """順張り（ミネルヴィニ・新高値V2）の全部売りの合図＝かぶせ線（2026-10-01 ユーザー決定。`バックテスト結果/2倍ETFで売って買い直す.md`）。
    上昇中（終値が25日線より上で、直近20日の最高値の97%以上）の陽線の翌日に、前日の高値より上で寄り付き、前日の陽線の真ん中より下・前日の始値より上で引ける。
    買った日の翌日以降で最初に出た日を返す（なければ None）"""
    import backtest_exit_signals as xs
    if "ma25" not in d:
        xs.prep(d)
    for j in range(2, len(d["c"])):
        if d["date"][j] > since and xs.dark_cloud(d, j):
            return d["date"][j]
    return None


def big_bear_signal(d, since):
    """逆張り（ボリンジャーIII・急落の底）の全部売りの合図＝出来高2倍の大陰線（2026-10-02 ユーザー決定。`バックテスト結果/やり直し_売りの合図の組み合わせ.md`）。
    実体（始値−終値）が前日までのATR(14)の1.5倍以上、終値がその日の値幅の下25%以内、出来高が前日までの50日平均の2倍以上。
    買った日の翌日以降で最初に出た日を返す（なければ None）"""
    import backtest_rebuy as rb
    import backtest_exit_signals as xs
    if "atr14" not in d:
        xs.prep(d)
    for j in range(2, len(d["c"])):
        if d["date"][j] > since:
            try:
                if rb.big_bear(d, j):
                    return d["date"][j]
            except (TypeError, ValueError, IndexError):
                pass
    return None


def rule_stats():
    """ルールごとの過去の成績（今のルールで計算。`tools/backtest_retest.py --stage stats` が書く `新分析ツール/ルールの成績.json`）"""
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "新分析ツール", "ルールの成績.json")
    try:
        return json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError):
        return {}


ETF_MAX_DRAG = 0.15   # 目減りが年15%以上の2倍ETFは使わない（2026-10-04 ユーザー決定。`バックテスト結果/2倍ETFを使う決まり.md`）
ETF_ALIAS = {"GOOG": "GOOGL"}


_ETF_TAB = None


def etf_table():
    """2倍ETFの対応表。リポジトリの表が8日より古ければ、その場で測り直した表を使う（約2分、`tools/leveraged_etf_check.py`。
    目減りが変わって条件を満たした銘柄は自動で復活する。2026-10-04 ユーザーの指示）"""
    global _ETF_TAB
    if _ETF_TAB is not None:
        return _ETF_TAB
    here = os.path.dirname(os.path.abspath(__file__))
    p = os.path.join(here, "..", "新分析ツール", "2倍ETFの対応表.json")
    try:
        tab = json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError):
        tab = {}
    upd = (tab.get("_meta") or {}).get("updated", "2000-01-01")
    if (dt.date.today() - dt.date.fromisoformat(upd)).days > 8:
        fresh = "/tmp/etf2x_table.json"
        try:
            if not (os.path.exists(fresh) and json.load(open(fresh)).get("_meta", {}).get("updated") == str(dt.date.today())):
                subprocess.run([sys.executable, os.path.join(here, "leveraged_etf_check.py"), "--json", fresh, "--out", "/tmp/etf2x_table.md"],
                               capture_output=True, timeout=600)
            tab = json.load(open(fresh, encoding="utf-8"))
        except (OSError, ValueError, subprocess.TimeoutExpired):
            pass
    _ETF_TAB = tab
    return tab


def etf2x_of(sym):
    """2倍ETFを使う銘柄なら (ETFのティッカー, 目減り) を返す。`新分析ツール/2倍ETFの対応表.json`（`tools/leveraged_etf_check.py` が作る、直近1年の実測）"""
    tab = etf_table()
    if not tab:
        return None
    x = tab.get(ETF_ALIAS.get(sym, sym))
    if not x or -x["drag"] >= ETF_MAX_DRAG:
        return None
    return x["etf"], -x["drag"]


def shares_note(x, ex_):
    """4,500ドル分の株数の目安。値段は、予約注文ならその価格、寄り付きの成行なら今日の終値（寄り付きの値段で変わる）"""
    m = re.match(r"(逆指値買い|指値買い) ([\d.]+)", x["order"])
    p = float(m.group(2)) if m else x["close"]
    basis = "注文の価格" if m else "今日の終値。寄り付きの値段で変わる"
    if ex_:
        e = fetch_daily(ex_[0])
        if not e or not e["c"]:
            return f"。**株数の目安: {ex_[0]}の値段が取れず計算できない**"
        ep = e["c"][-1] * (1 + 2 * (p / x["close"] - 1))     # 元の株の注文価格を、2倍ETFの値段に直す
        return f"。**株数の目安: {ex_[0]} {int(BUY_USD // ep)}株**（{BUY_USD:,}ドル÷{ep:.2f}。{basis}をETFの値段に直した近似）"
    return f"。**株数の目安: {int(BUY_USD // p)}株**（{BUY_USD:,}ドル÷{p:.2f}。{basis}）"


def rule_key(kind):
    if "ボリンジャー" in kind:
        return "B"
    if "急落" in kind:
        return "C"
    if "新高値" in kind:
        return "V"
    if "ミネルヴィニ" in kind:
        return "M"
    return None


def load_industries():
    """{ティッカー: 業種}。テーマ監視銘柄.md の表の3列目（Yahoo Financeの業種）。監視銘柄にない銘柄はバックテストのキャッシュから補う"""
    out = {}
    for f in ("universe.json", "industry_extra.json"):
        p = os.path.join(DEFAULT_CACHE, f)
        if os.path.exists(p):
            try:
                out.update({k: (v or {}).get("industry") for k, v in json.load(open(p)).items() if (v or {}).get("industry")})
            except Exception:
                pass
    for line in open(bth.WATCHLIST, encoding="utf-8"):
        m = re.match(r"^\| ([A-Z][A-Z.]*) \| [^|]* \| ([^|]+?) \|", line)
        if m and m.group(2) != "業種":
            out[m.group(1)] = m.group(2).strip()
    # 「Software—Infrastructure」と「Software - Infrastructure」のような書き方の違いをそろえる
    return {k: re.sub(r"\s*[—–-]\s*", " - ", v) for k, v in out.items()}


def hi2y(d, i):
    """直前2年（500取引日、当日を含まない）の最高値（高値）。新高値V2の「上値のレジスタンスがない」条件（2026-09-28 ユーザー採用）"""
    return max(d["h"][max(0, i - 500):i]) if i > 0 else None


def pct(x, d=1):
    return "取得不可" if x is None else f"{x * 100:+.{d}f}%"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--prev", help="前回の record.json（前日の予約注文が約定したかを確認し、約定していなければ改めて判定する）")
    ap.add_argument("--asof", help="この日の引けまでのデータで判定する（検証用）")
    a = ap.parse_args()

    wl = bth.load_watchlist()
    members_csv = curl(MEMBERS_URL)
    if not members_csv.startswith("ticker,"):
        p = os.path.join(DEFAULT_CACHE, "members.csv")
        members_csv = open(p).read() if os.path.exists(p) else "ticker,start_date,end_date\n"
    sp = [r["ticker"] for r in csv.DictReader(members_csv.splitlines()) if not r["end_date"]]
    try:   # NASDAQ100の今の構成銘柄（監視外の注目銘柄を探すため）
        ndx_m = [r["symbol"].replace("/", ".") for r in json.loads(curl(NDX_URL))["data"]["data"]["rows"]]
    except Exception:
        ndx_m = []
    syms = sorted(set(sp) | set(ndx_m) | set(wl) | {"SPY", "^GSPC", "^NDX"})
    with ThreadPoolExecutor(8) as ex:
        got = dict(zip(syms, ex.map(fetch_daily, syms)))
    got = {s: cut(d, a.asof) for s, d in got.items() if d}
    spy = got.pop("SPY")
    gspc = got.pop("^GSPC", None)
    ndx = got.pop("^NDX", None)
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
        add_pivot(d)
        d["rsi2"] = rsi_wilder(d["c"], 2)
        c2.add_udvr(d)
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
    w("| グループ | 銘柄数 | 1週 | 1カ月 | 3カ月 | 3カ月の順位 | 50日線より上の銘柄の割合 | グループ指数の30週線の局面（線との乖離、4週前からの線の傾き） |")
    w("|---|---|---|---|---|---|---|---|")
    groups = list(dict.fromkeys(wl.values()))
    med = lambda xs: sorted(xs)[len(xs) // 2] if xs else None
    rows = []
    for g in groups:
        mem = [d for s, d in data.items() if wl[s] == g]
        r = [med([d["c"][-1] / d["c"][-1 - k] - 1 for d in mem]) for k in (5, 21, 63)]
        ab = sum(1 for d in mem if d["ma50"][-1] and d["c"][-1] > d["ma50"][-1]) / len(mem) if mem else None
        gi = bth.theme_index({s: d for s, d in data.items() if wl[s] == g}, spy["date"])
        m30 = sma(gi["c"], 150)
        st = market_regime(gi).get(day, "判定不能")
        desc = f"{st}（{pct(gi['c'][-1] / m30[-1] - 1)}、{pct(m30[-1] / m30[-21] - 1)}）" if m30[-1] and m30[-21] else st
        rows.append((g, len(mem), r, ab, desc))
    order = sorted(rows, key=lambda x: -(x[2][2] or -9))
    for g, n, r, ab, desc in rows:
        w(f"| {g} | {n} | {pct(r[0])} | {pct(r[1])} | {pct(r[2])} | {[x[0] for x in order].index(g) + 1}位 | {pct(ab, 0).lstrip('+')} | {desc} |")

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
    mkt = market_regime(gspc).get(day, "判定不能") if gspc else "取得不可"
    mkt_n = market_regime(ndx).get(day, "判定不能") if ndx else "取得不可"
    w(f"- 市場全体の30週線による局面: S&P500指数 **{mkt}**／NASDAQ100指数 **{mkt_n}**（急落の底で買うルールは、過去の検証で下落相場で特に強く、横ばいの相場では負けていた）")
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

    # ---- 急騰・急落 ----
    w("## 4. 急騰・急落した銘柄（前日比±5%以上、または出来高が50日平均の2倍以上）\n")
    w("原因のニュースをサブエージェントが調べ、候補・保有銘柄の判定材料として著者に渡す。急騰・急落そのものは売買の合図にしない"
      "（後知恵のないS&P500全体のバックテストでは、急騰の翌日に買うルールは年率7%、急落の翌日に買うルールは年率9〜10%で、採用した3つのルールより優れていなかった）。\n")
    mv = []
    for s_, d in data.items():
        i = len(d["c"]) - 1
        ch = d["c"][i] / d["c"][i - 1] - 1
        vr = d["v"][i] / d["vol50"][i] if d["vol50"][i] else None
        if abs(ch) >= 0.05 or (vr and vr >= 2):
            mv.append((s_, ch, vr))
    if mv:
        w("| 銘柄 | グループ | 前日比 | 出来高（50日平均の倍） | 終値 | 50日線 | RS | 局面 |")
        w("|---|---|---|---|---|---|---|---|")
        for s_, ch, vr in sorted(mv, key=lambda x: -abs(x[1])):
            d = data[s_]
            rs = d["rs"][-1]
            w(f"| {s_} | {wl[s_]} | {pct(ch)} | {vr:.1f}倍 | {d['c'][-1]:.2f} | {'上' if d['ma50'][-1] and d['c'][-1] > d['ma50'][-1] else '下'} | {'取得不可' if rs is None else f'{rs:.0f}'} | {'上昇相場' if regime_up(len(d['c']) - 1, d) else 'レンジ'} |")
        w("\n- 局面: 終値 > 50日線 > 200日線、50日線が20取引日前より2%以上高い、ADX(14) ≧ 20 をすべて満たせば上昇相場、それ以外はレンジ（判定式はClaudeが置いたもの）。")
    else:
        w("該当なし")
    w("")

    # ---- 監視外の注目銘柄 ----
    w("## 4-2. 監視外の注目銘柄（S&P500・NASDAQ100のうち監視銘柄に入っていない銘柄）\n")
    w("条件: 流動性（株価5ドル以上・50日平均出来高25万株以上）があり、(a) 前日比+8%以上かつ出来高が50日平均の2倍以上、"
      f"または (b) 終値が直前1年の最高値（終値）を上回り、RS≧90。RSの高い順に{OUT_MAX}銘柄（ニュースを調べる）。監視銘柄に入れるかはユーザーが決める。\n")
    outs = []
    for s_, d in got.items():
        if s_ in wl or s_.startswith("^") or len(d["c"]) < 254 or d["date"][-1] != day:
            continue
        c_, v_ = d["c"], d["v"]
        v50 = sum(v_[-51:-1]) / 50
        if c_[-1] < 5 or v50 < 250_000:
            continue
        ch, vr = c_[-1] / c_[-2] - 1, v_[-1] / v50 if v50 else 0
        rs_ = 99 * bisect.bisect_left(pool, rs_raw(c_)) / (len(pool) - 1) if len(pool) > 50 else None
        surge = ch >= 0.08 and vr >= 2
        newhi = c_[-1] > max(c_[-253:-1]) and rs_ is not None and rs_ >= 90
        if surge or newhi:
            outs.append((s_, ch, vr, rs_, "急騰" if surge and not newhi else "1年の高値更新" if newhi and not surge else "急騰・1年の高値更新", c_[-1]))
    outs.sort(key=lambda x: -(x[3] or 0))
    if outs:
        w("| 銘柄 | 種類 | 前日比 | 出来高（50日平均の倍） | RS | 終値 |")
        w("|---|---|---|---|---|---|")
        for s_, ch, vr, rs_, kd, cl in outs[:OUT_MAX]:
            w(f"| {s_} | {kd} | {pct(ch)} | {vr:.1f}倍 | {'取得不可' if rs_ is None else f'{rs_:.0f}'} | {cl:.2f} |")
        if len(outs) > OUT_MAX:
            w(f"\n- ほかに{len(outs) - OUT_MAX}銘柄: " + "、".join(f"{x[0]}（{x[4]}、RS {x[3]:.0f}）" for x in outs[OUT_MAX:OUT_MAX + 15] if x[3] is not None))
    else:
        w("該当なし")
    w("")

    # ---- 保有銘柄 ----
    hold = load_holdings()
    w("## 5. 保有銘柄の手じまい条件（`新分析ツール/保有銘柄.md`）\n")
    if not hold:
        w("保有銘柄なし（または一覧が空）\n")
    else:
        w("| 銘柄 | ルール | 買った日 | 買値 | 終値 | 損益 | 損切り価格（買値の15%下、逆指値） | ルールの手じまい条件 | 出来高2倍の大陰線（買った後の直近5日） | 次回決算予定日 |")
        w("|---|---|---|---|---|---|---|---|---|---|")
        for h in hold:
            d = data.get(h["sym"])
            if not d:
                w(f"| {h['sym']} | {h['rule']} | {h['date']} | {h['price']} | 取得不可 | | | | | |")
                continue
            i = len(d["c"]) - 1
            c = d["c"][i]
            if "新高値" in h["rule"]:
                ex = "成立（引けで50日線割れ → 翌日の寄り付きで手じまい）" if c < d["ma50"][i] else f"未成立（50日線 {d['ma50'][i]:.2f}）"
            elif "急落" in h["rule"]:
                ma5 = sum(d["c"][i - 4:i + 1]) / 5
                ex = "成立（終値が5日線を上回った → 翌日の寄り付きで手じまい）" if c > ma5 else f"未成立（5日線 {ma5:.2f}）"
            elif "ボリンジャー" in h["rule"]:
                ex = ("成立（引けで上部バンド以上なのに指値が届かなかった → 翌日の寄り付きで手じまい）" if d["pctb"][i] is not None and d["pctb"][i] >= 1
                      else f"売りの指値: 上部バンド {d['bb_up'][i]:.2f}（今夜この値に置き直す。届いた日に売れる）")
            elif "ミネルヴィニ" in h["rule"]:
                ex = "成立（引けで50日線割れ → 翌日の寄り付きで手じまい）" if c < d["ma50"][i] else f"未成立（50日線 {d['ma50'][i]:.2f}）"
            elif "ワインスタイン" in h["rule"]:
                wk = dt.date.fromisoformat(day).weekday() == 4
                ex = ("成立（週足の終値が10週線割れ → 翌取引日の寄り付きで手じまい）" if wk and d["w_c"][i] < d["w_ma10"][i]
                      else f"未成立（10週線 {d['w_ma10'][i]:.2f}、判定は週の最終取引日）" if wk else "判定は週の最終取引日")
            else:
                ex = "ルールが不明（保有銘柄.md の「ルール」を確認）"
            if "ボリンジャー" in h["rule"] or "急落" in h["rule"]:
                bb_ = big_bear_signal(d, h["date"])
                if bb_ == day:
                    ex = "**成立（出来高2倍の大陰線 → 翌日の寄り付きで全部売る）** " + ex
                elif bb_:
                    ex = f"**出来高2倍の大陰線が {bb_} に出た**（まだ持っていれば、次の寄り付きで全部売る） " + ex
            if "新高値" in h["rule"] or "ミネルヴィニ" in h["rule"]:
                hd = half_signal(d, h["date"])
                dc = dark_cloud_signal(d, h["date"])
                if dc == day:
                    ex = "**成立（かぶせ線 → 翌日の寄り付きで全部売る）** " + ex
                elif dc:
                    ex = f"**かぶせ線が {dc} に出た**（まだ持っていれば、次の寄り付きで全部売る） " + ex
                if hd == day:
                    ex += "。**半分売りの合図: 今日**（翌日の寄り付きで半分売る。残りはルールの手じまいまで持つ）"
                elif hd:
                    ex += f"。半分売りの合図: {hd} に出た（半分売っていなければ、次の寄り付きで半分売る）"
                else:
                    ex += "。半分売りの合図: まだ出ていない"
            ex2 = etf2x_of(h["sym"])
            if ex2:
                ex += f"（2倍ETF {ex2[0]} で持っている場合も、判定は元の株 {h['sym']} の値段）"
            stop = h["price"] * (1 - STOP)
            if c <= stop:
                ex = "**損切り価格を下回った** " + ex
            w(f"| {h['sym']} | {h['rule']} | {h['date']} | {h['price']:.2f} | {c:.2f} | {pct(c / h['price'] - 1)} | {stop:.2f} | {ex} | {bear_candles(d, h['date'])} | {earnings_date(h['sym'])} |")
        w("")
        w("- 出来高2倍の大陰線: 実体（始値−終値）が前日までのATR(14)の1.5倍以上、終値がその日の値幅の下25%以内、出来高が前日までの50日平均の2倍以上の日。"
          "**押し目（ボリンジャーIII）・急落の底の保有では売りのルール**: 出たら翌日の寄り付きで全部売り、空いた枠で次の合図を買う（2026-10-02 ユーザー決定。"
          "`バックテスト結果/やり直し_売りの合図の組み合わせ.md`。乱数3組とも年率が約+2ポイント、最大下落率もやや下がった）。"
          "ミネルヴィニ・新高値V2の保有では事実の表示（順張りに足しても良くならなかった）。\n")
        w("- 半分売りの合図（ミネルヴィニ・新高値V2の保有だけ）: 反転のローソク足（かぶせ線・弱気の包み足・宵の明星・流れ星）＋出来高が50日平均の1.5倍以上＋RSI(14)が前日か当日に70以上。"
          "買った後に最初に出た日の翌日の寄り付きで半分売り、残り半分は50日線割れ・損切り15%まで持つ（2026-10-01 ユーザー決定。`バックテスト結果/半分だけ売るとオニールの空き枠.md`）。\n")
        w("- かぶせ線（ミネルヴィニ・新高値V2の保有だけ）: 上昇中の陽線の翌日に、前日の高値より上で寄り付き、前日の陽線の真ん中より下（前日の始値より上）で引けた日。"
          "翌日の寄り付きで全部売り、空いた枠で次の合図を買う。半分売りより優先する（2026-10-01 ユーザー決定。`バックテスト結果/2倍ETFで売って買い直す.md`。順張りの売買の25%で出て、1回平均+2.0%、年率 21.4%→26.4%）。\n")

    # ---- 前日の予約注文 ----
    if a.prev and os.path.exists(a.prev):
        prev = json.load(open(a.prev, encoding="utf-8"))
        res = [c for c in prev.get("candidates", []) if c.get("verdict", "").startswith("買い（予約")]
        w(f"## 5-2. 前日（{prev.get('trade_date', '?')}の引け）の【買い（予約）】の確認\n")
        if not res:
            w("前日の【買い（予約）】はなし。\n")
        else:
            bought = load_trades()
            w("約定したかどうかは、ユーザーの `保有銘柄.md`・`売買記録.md` に記録があるかで判断する（価格が届いても、記録がなければ約定していないものとして扱う）。"
              "約定していない銘柄は、今日の条件で改めてエントリーを探す（節6）。\n")
            w("| 銘柄 | 種類 | 予約の価格 | 今日の高値／安値 | 価格は届いたか | ユーザーの約定の記録 | 扱い |")
            w("|---|---|---|---|---|---|---|")
            for c in res:
                d = data.get(c["sym"])
                p = c.get("stop_buy") or c.get("limit_buy")
                rec = [b for b in bought if b["sym"] == c["sym"] and b["date"] > prev.get("trade_date", "")]
                if d:
                    hi, lo = d["h"][-1], d["l"][-1]
                    touch = ("届いた" if (c.get("stop_buy") and hi >= p) or (c.get("limit_buy") and lo <= p) else "届かず") if p else "価格不明"
                    hl = f"{hi:.2f}／{lo:.2f}"
                else:
                    touch, hl = "株価なし", ""
                how = f"約定（{rec[0]['date']} {rec[0]['price']:.2f}）→ 節5で保有として確認" if rec else f"約定の記録なし → {{{{今日:{c['sym']}}}}}"
                w(f"| {c['sym']} | {c['kind']} | {'' if p is None else f'{p:.2f}'} | {hl} | {touch} | {'あり' if rec else 'なし'} | {how} |")
            w("")

    # ---- 候補 ----
    w("## 6. 候補（採用したルールの条件が成立＝A、成立が目前＝B）\n")
    w(f"建玉の目安: 同時保有{SLOTS}銘柄まで、1銘柄に資金の{100 / SLOTS:.0f}%（資金÷{SLOTS}）、損切りは買値の{STOP * 100:.0f}%下（ユーザー決定 2026-09-29）。\n")
    cands = []
    refs = []     # 参考の表示だけの合図（ワインスタイン10週）
    # 新高値V2は、監視銘柄のうちその日のRSが上位10銘柄だけに当てる（後知恵なしの検証で、絞らないと効かなかった。2026-09-27 ユーザー決定）
    rs_sorted = sorted(((d["rs"][-1] or 0), s) for s, d in data.items())[::-1]
    v2_top = {s for _, s in rs_sorted[:V2_TOP]}
    v2_rank = {s: k + 1 for k, (_, s) in enumerate(rs_sorted)}
    # テーマの外の強い銘柄（空き枠の候補。2026-10-01 ユーザー決定。`バックテスト結果/半導体・AIに特化した場合.md` の形3'）:
    # S&P500の今の構成銘柄のうち監視銘柄でないもので、RS≧90、30週線（150日線）の局面が上昇、流動性あり、
    # 業種（Yahoo）の3カ月の騰落率の中央値が上位20%（後知恵なしの監視銘柄 `backtest_rotation.build_lists` と同じ考え方）
    inds_all = load_industries()
    free = max(0, SLOTS - len(load_holdings()))
    outside, out_rank, out_top = {}, {}, set()
    if free and not a.asof:
        rows = {}
        for s_ in sp:
            d = got.get(s_)
            if s_ in wl or not d or d["date"][-1] != day or len(d["c"]) < 260:
                continue
            c_ = d["c"]
            m150 = sum(c_[-150:]) / 150
            m150p = sum(c_[-170:-20]) / 150
            v50 = sum(d["v"][-51:-1]) / 50
            rs_ = 99 * bisect.bisect_left(pool, rs_raw(c_)) / (len(pool) - 1) if len(pool) > 50 else None
            rows[s_] = (rs_, c_[-1] > m150 > m150p, c_[-1] / c_[-64] - 1, c_[-1] >= 5 and v50 >= 250_000)
        by = {}
        for s_, x in rows.items():
            if inds_all.get(s_):
                by.setdefault(inds_all[s_], []).append(x[2])
        medr = {k: sorted(v)[len(v) // 2] for k, v in by.items() if len(v) >= 3}
        top_ind = set(sorted(medr, key=lambda k: -medr[k])[:max(1, len(medr) // 5)])
        for s_, (rs_, up, _, liq) in rows.items():
            if rs_ is not None and rs_ >= 90 and up and liq and inds_all.get(s_) in top_ind:
                d = got[s_]
                bt.prepare(d)
                bs.prepare(d)
                add_pivot(d)
                d["rsi2"] = rsi_wilder(d["c"], 2)
                c2.add_udvr(d)
                d["sym"] = s_
                d["rs"][-1] = rs_
                outside[s_] = d
        o_sorted = sorted(((d["rs"][-1] or 0), s_) for s_, d in outside.items())[::-1]
        out_top = {s_ for _, s_ in o_sorted[:V2_TOP]}
        out_rank = {s_: k + 1 for k, (_, s_) in enumerate(o_sorted)}
    universe = [(s, d, wl[s], False) for s, d in data.items()] + [(s, d, f"テーマの外（{inds_all.get(s, '業種不明')}）", True) for s, d in outside.items()]
    for s, d, grp, is_out in universe:
        i = len(d["c"]) - 1
        if not bt.liquid(d, i, [("0000", "9999")]):
            continue
        rs = d["rs"][i]
        if is_out:   # 新高値V2のRS上位10は、テーマの外の候補の中で数える
            v2_top_, v2_rank_, where = out_top, out_rank, "テーマの外の強い銘柄"
        else:
            v2_top_, v2_rank_, where = v2_top, v2_rank, "監視銘柄"
        base = {"sym": s, "group": grp, "outside": is_out, "close": d["c"][i], "rs": rs, "chg": d["c"][i] / d["c"][i - 1] - 1,
                "regime": "上昇相場" if regime_up(i, d) else "レンジ"}
        pb, ii = d["pctb"][i], d["ii21"][i]
        lvl05 = d["bb_dn"][i] + 0.05 * (d["bb_up"][i] - d["bb_dn"][i])
        if bs.O_method3(i, d):
            cands.append({**base, "pat": "A", "kind": "逆張り: ボリンジャー メソッドIII",
                          "why": f"%b={pb:.3f}（<0.05）、21日II%={ii:+.3f}（>0）",
                          "order": f"翌日の寄り付きで買い。損切り: 買値の15%下。手じまい: 買った日の夜から、売りの指値をその日の上部バンド（今日 {d['bb_up'][i]:.2f}）に置き、毎晩その日の値に置き直す"})
        elif pb is not None and ii is not None and ii > 0 and pb < 0.2:
            cands.append({**base, "pat": "B", "kind": "予約: ボリンジャー メソッドIII（%bが0.05未満に近い）",
                          "why": f"%b={pb:.3f}（0.05まであと少し）、21日II%={ii:+.3f}（>0）",
                          "order": f"指値買い {lvl05:.2f}（今日のバンドで%b=0.05になる価格。本のルールは引け値で判定するので近似）。損切り: 買値の15%下。手じまい: 買った日の夜から、売りの指値をその日の上部バンドに置き、毎晩置き直す"})
        kh = d["piv_i"][i]
        tt = bt.trend_template(d, i)
        if kh is not None and i - kh >= 15 and tt:
            piv = d["h"][kh]
            depth = (piv - min(d["l"][kh:i + 1])) / piv
            vr = d["v"][i] / d["vol50"][i]
            if depth <= 0.35 and d["c"][i] > piv and vr >= 2:
                cands.append({**base, "pat": "A", "kind": "順張り: ミネルヴィニ（トレンドテンプレート＋ベースの上抜け）",
                              "why": f"ピボット（ベースの高値、{d['date'][kh]}）{piv:.2f}を出来高{vr:.1f}倍で上抜け、ベース{i - kh}日・調整幅{depth * 100:.0f}%",
                              "order": f"翌日の寄り付きで買い。ただし寄り付きが{piv * 1.03:.2f}（ピボット+3%）を超えたら見送り。損切り: 買値の15%下。手じまい: 引けで50日線を割った翌日の寄り付き"})
            elif depth <= 0.35 and piv * 0.95 <= d["c"][i] <= piv:
                cands.append({**base, "pat": "B", "kind": "予約: ミネルヴィニ（ピボットの手前）",
                              "why": f"ピボット（ベースの高値、{d['date'][kh]}）{piv:.2f}まで{(piv / d['c'][i] - 1) * 100:.1f}%、ベース{i - kh}日・調整幅{depth * 100:.0f}%",
                              "order": f"逆指値買い {piv:.2f}（指値の上限 {piv * 1.03:.2f}＝ピボット+3%）。本は上抜けの日の出来高が50日平均の2倍以上（{2 * d['vol50'][i] / 1e4:,.0f}万株）を求める。損切り: 買値の15%下。手じまい: 引けで50日線割れ"})
        # 新高値（V2、担当: ミネルヴィニ）。2026-09-27 採用
        uv, h20 = d["udvr"][i], d["hi20c"][i]
        h2y = hi2y(d, i)
        trig = max(h20 or 0, h2y or 0)
        if s in v2_top_ and c2.V2(i, d) is not None and h2y is not None and d["c"][i] >= h2y:
            cands.append({**base, "pat": "A", "kind": "順張り: 新高値（V2、担当: ミネルヴィニ）",
                          "why": f"{where}のRS上位{V2_TOP}以内（{v2_rank_[s]}位）、トレンドテンプレート8条件、RS {rs:.0f}（≧90）、終値が直前20日の最高値（終値）{h20:.2f}を上回る、上げ下げの出来高比（50日）{uv:.2f}（≧1.3）、終値が直前2年の最高値{h2y:.2f}以上（上値のレジスタンスなし）",
                          "order": "翌日の寄り付きで買い。損切り: 買値の15%下。手じまい: 引けで50日線を割った翌日の寄り付き"})
        elif s in v2_top_ and h20 and h2y and uv and uv >= 1.3 and (rs or 0) >= 90 and bt.trend_template(d, i) and trig * 0.97 <= d["c"][i] < trig:
            cands.append({**base, "pat": "B", "kind": "予約: 新高値（V2、担当: ミネルヴィニ）",
                          "why": f"{where}のRS上位{V2_TOP}以内（{v2_rank_[s]}位）、トレンドテンプレート8条件、RS {rs:.0f}、上げ下げの出来高比 {uv:.2f}、直前20日の最高値（終値）{h20:.2f}・直前2年の最高値{h2y:.2f}の高い方まで{(trig / d['c'][i] - 1) * 100:.1f}%",
                          "order": f"逆指値買い {trig:.2f}（直前20日の最高値（終値）と直前2年の最高値の高い方。本来は終値で判定するルールなので近似）。損切り: 買値の15%下。手じまい: 引けで50日線割れ"})
        if bcr.C3R10(i, d) is not None:
            cands.append({**base, "pat": "A", "kind": "逆張り: 急落の底（担当: コナーズ）",
                          "why": f"直前5日の最高値（終値）から{bcr.drop(i, d) * 100:.1f}%下落（−15%以上）、RSI(2)={d['rsi2'][i]:.1f}（≦10）、急落の前は50日線＞200日線。市場全体の局面: S&P500 {mkt}／NASDAQ100 {mkt_n}",
                          "order": f"翌日の寄り付きで買い。損切り: 買値の15%下。手じまい: 終値が5日線（今日 {sum(d['c'][i - 4:i + 1]) / 5:.2f}）を上回った翌日の寄り付き（コナーズ）"})
        # ワインスタイン10週は参考の表示だけ（後知恵なしのバックテストで、加えると年率が下がった。著者には送らない。2026-10-04 ユーザー決定）
        if dt.date.fromisoformat(day).weekday() == 4:
            if bt.E_weinstein(10, ma="10")(i, d) is not None:
                refs.append({**base, "pat": "A", "kind": "順張り: ワインスタイン（10週の高値上抜け）",
                              "why": f"週足の終値が直前10週の高値{d['w_hi_prev'][10][i]:.2f}を出来高{d['w_vol'][i] / d['w_vol4'][i]:.1f}倍で上抜け、10週線が上向き",
                              "order": "翌日の寄り付きで買い。損切り: 買値の15%下。手じまい: 週足の終値が10週線を割った翌取引日の寄り付き"})
            else:
                h10, m10, m10p = d["w_hi_prev"][10][i], d["w_ma10"][i], d["w_ma10_1"][i]
                if h10 and m10 and m10p and m10 > m10p and h10 * 0.95 <= d["c"][i] <= h10:
                    refs.append({**base, "pat": "B", "kind": "予約: ワインスタイン（10週の高値の手前）",
                                  "why": f"直前10週の高値{h10:.2f}まで{(h10 / d['c'][i] - 1) * 100:.1f}%、10週線が上向き",
                                  "order": f"逆指値買い {h10:.2f}（本のルールは週足の終値で判定するので近似。上抜けの週の出来高は直前4週の平均の2倍以上）。損切り: 買値の15%下。手じまい: 週足の終値が10週線割れ"})
    if not cands:
        w("本日は該当なし（著者への送信は不要）。\n")
    else:
        # 監視銘柄（テーマ）の候補を先に、テーマの外の候補は後に並べる
        cands.sort(key=lambda x: (x["outside"], x["pat"], -(x["rs"] or 0)))
        # テーマの外の候補は、空き枠の数（同時保有の上限 − 保有銘柄の数）まで（Aを先に、RSの高い順）
        n_out, kept_ = 0, []
        for x in cands:
            if x["outside"]:
                n_out += 1
                if n_out > free:
                    continue
            kept_.append(x)
        out_dropped = n_out - min(n_out, free)
        cands = kept_
        # Bはルールごとに RSの高い順で5件まで（NotebookLMの1日の上限とニュース調査の時間のため）
        nb, kept = {}, []
        for x in cands:
            if x["outside"]:
                kept.append(x)
                continue
            if x["pat"] == "B" or "急落" in x["kind"] or "新高値" in x["kind"]:
                k = x["kind"].split("（")[0]
                nb[k] = nb.get(k, 0) + 1
                if nb[k] > (B_MAX if x["pat"] == "B" else CRASH_MAX):
                    continue
            kept.append(x)
        dropped = len(cands) - len(kept)
        cands = kept
        # 同じ業種は同時に GROUP_CAP 銘柄まで: 保有中の銘柄と、RSの高い順に先に残した候補（A→Bの順）で数える
        inds = load_industries()
        held_by = {}
        for h in load_holdings():
            if inds.get(h["sym"]):
                held_by.setdefault(inds[h["sym"]], []).append(h["sym"])
        cnt, kept, capped = {k: list(v) for k, v in held_by.items()}, [], []
        for x in cands:
            g = inds.get(x["sym"])
            cur = [t for t in cnt.get(g, []) if t != x["sym"]] if g else []
            if g and len(cur) >= GROUP_CAP:
                capped.append((x, g, cur))
                continue
            kept.append(x)
            if g and x["sym"] not in cnt.setdefault(g, []):
                cnt[g].append(x["sym"])
        cands = kept
        with ThreadPoolExecutor(4) as ex:
            eds = dict(zip([x["sym"] for x in cands], ex.map(earnings_date, [x["sym"] for x in cands])))
        for k_, v in eds.items():
            if re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
                n = (dt.date.fromisoformat(v) - dt.date.fromisoformat(day)).days
                eds[k_] = f"{v}（{n}日後）" + ("**決算が近い**" if 0 <= n <= 14 else "")
        w("パターン: A＝最新の足で採用ルールの条件が成立（翌日の寄り付きで成行）、B＝条件の成立が目前（引け後に予約注文を置く）。\n")
        st_ = rule_stats()
        def perf(x):
            r = st_.get(rule_key(x["kind"]) or "")
            return f"{r['rank']}位（勝率{r['win'] * 100:.0f}%・1回平均{r['avg'] * 100:+.1f}%）" if r else "成績なし（バックテストの組み合わせ外）"
        # 表示の順番だけ、ルールの過去の成績（1回平均）の良い順にする。買う順番・件数の上限・同じ業種の上限は上の並び（RSの高い順）で決めたまま
        show = sorted(cands, key=lambda x: (x["outside"], x["pat"], (st_.get(rule_key(x["kind"]) or "") or {}).get("rank", 9), -(x["rs"] or 0)))
        w("| 銘柄 | グループ | パターン | 種類 | ルールの過去の成績 | 終値 | 前日比 | RS | 局面 | 当てはまった条件 | 次回決算予定日 | 注文の目安 |")
        w("|---|---|---|---|---|---|---|---|---|---|---|---|")
        for x in show:
            rs_ = "取得不可" if x["rs"] is None else f"{x['rs']:.0f}"
            ex_ = etf2x_of(x["sym"])
            od_ = x["order"] + (f"。**2倍ETFで買う: {ex_[0]}**（目減り 年{ex_[1] * 100:.0f}%。株と同じ金額。合図・損切り・手じまいは元の株 {x['sym']} の値段で判定）" if ex_ else "") + shares_note(x, ex_)
            w(f"| {x['sym']} | {x['group']} | {x['pat']} | {x['kind']} | {perf(x)} | {x['close']:.2f} | {pct(x['chg'])} | {rs_} | {x['regime']} | {x['why']} | {eds[x['sym']]} | {od_} |")
        w("\n- 2倍ETF: 2倍ETFがある銘柄（ユーザーがムームー証券で買えることを確認した38銘柄のうち、目減りが年15%未満のもの）は、株の代わりに2倍ETFを買う（2026-10-04 ユーザー決定。"
          "`バックテスト結果/2倍ETFを使う決まり.md`。年率 約27%→約33%、確定した損益だけの最大下落率 約30%→約31%、含み損込みは約33%→約45%）。"
          "買う金額は株と同じ（資金の25%）。合図・損切り（元の株の買値の15%下＝ETFでは約30%下）・手じまいはすべて元の株の値段で判定する。指値・逆指値はETFの値段に直して置く。"
          "どのETFかは `新分析ツール/2倍ETFの対応表.json`（売買代金が1日500万ドル以上で、直近1年の目減りが一番小さいもの）。")
        if st_:
            m_ = st_.get("_meta", {})
            w(f"\n- ルールの過去の成績: 今の売りのルールで、後知恵なしの監視銘柄・2015年〜の全部の合図の1回ごとの成績（{m_.get('updated', '?')}計算、`{m_.get('source', '')}`）。"
              "順位は1回平均（1回の売買で平均いくら増えるか）の順。表はパターン（A→B）ごとに、この順位の良い順に並べた（表示の順番だけ。買う順番・件数の上限は変えていない。"
              "候補の選び方を変えても成績は変わらなかったため。2026-10-02 ユーザーの指示）。著者には渡さない。")
        if capped:
            w(f"\n- 同じ業種は同時に{GROUP_CAP}銘柄まで（ユーザー決定 2026-09-28）のため見送った候補（保有中の銘柄と、RSの高い順に先に残した候補で数える）: "
              + "、".join(f"{x['sym']}（{x['pat']}・{x['kind'].split('（')[0]}。{g}: {'・'.join(c)}）" for x, g, c in capped))
        if dropped:
            w(f"\n- パターンBは各ルールでRSの高い順に{B_MAX}件まで、急落の底・新高値のAは{CRASH_MAX}件（同時保有の上限）までとし、{dropped}件を省いた。")
        w(f"\n- テーマの外の候補（グループが「テーマの外」）: 監視銘柄の候補で枠が埋まらないときに使う（監視銘柄の候補を先に買う）。"
          f"S&P500の今の構成銘柄のうち監視銘柄でない銘柄から、RS≧90・30週線が上向きで終値がその上・業種の3カ月の強さが上位20%の{len(outside)}銘柄を調べ、"
          f"空き枠{free}つ分まで出した" + (f"（ほかに{out_dropped}件を省いた）" if out_dropped else "") +
          "。バックテストでは、テーマの外の強い銘柄で空き枠を埋めると、テーマが弱い時期の成績が支えられた（`バックテスト結果/半導体・AIに特化した場合.md`。2026-10-01 ユーザー決定）。")
        w("\n- RS≧80の押し目（ボリンジャーIII）は、バックテストで成績がより安定していた（PF3.27、最大下落20%）。")
    if refs:
        w("\n## 6-2. 参考: ワインスタイン10週の合図（売買には使わない・著者には送らない）\n")
        w("後知恵なしのバックテストで、今の4つのルールに加えると年率が下がった（27.1%→22.9〜26.3%。`バックテスト結果/ワインスタイン10週を加えるか.md`）ため、"
          "2026-10-04 から参考の表示だけにした（ユーザー決定）。強い銘柄が10週の高値に近づいている、という事実として見る。\n")
        w("| 参考の銘柄 | グループ | パターン | 種類 | 終値 | 前日比 | RS | 当てはまった条件 |")
        w("|---|---|---|---|---|---|---|---|")
        rs_sorted = sorted(refs, key=lambda x: (x["outside"], x["pat"], -(x["rs"] or 0)))
        shown = [x for x in rs_sorted if x["pat"] == "A"] + [x for x in rs_sorted if x["pat"] == "B"][:10]
        if len(shown) < len(refs):
            w(f"（Bは監視銘柄を先に、RSの高い順に10件まで。ほかに{len(refs) - len(shown)}件）\n")
        for x in shown:
            rs_ = "取得不可" if x["rs"] is None else f"{x['rs']:.0f}"
            w(f"| {x['sym']} | {x['group']} | {x['pat']} | {x['kind']} | {x['close']:.2f} | {pct(x['chg'])} | {rs_} | {x['why']} |")
        w("")
    text = "\n".join(L) + "\n"
    today_pat = {}
    for x in cands:
        today_pat.setdefault(x["sym"], []).append(f"{x['pat']}（{x['kind']}）")
    text = re.sub(r"\{\{今日:([A-Z.]+)\}\}", lambda m: ("今日の条件で改めて判定: 節6の候補 " + "・".join(today_pat[m.group(1)]))
                  if m.group(1) in today_pat else "今日の条件では候補なし（新しいエントリーの条件がそろうまで待つ）", text)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    open(a.out, "w").write(text)
    print(text)


if __name__ == "__main__":
    main()
