#!/usr/bin/env python3
"""恩株ツールの基礎調査: S&P500の構成銘柄を買ったとき、どれくらいの確率で・どれくらいの期間で2倍になるか

使い方:
  tools/backtest_lib.py fetch                  # 先に日足を取得しておく（S&P500の過去の構成銘柄）
  tools/backtest_onkabu.py fetch [--cache DIR] # 発行済株式数（SEC）と株式分割（Yahoo）を取得
  tools/backtest_onkabu.py run [--cache DIR] [--out FILE]

考え方:
  - 毎月の最初の取引日に、その日のS&P500の構成銘柄を全部買ったことにする（銘柄を選ばない「素の確率」）。
  - 時価総額の順位は、その日までにSECに提出された決算書の発行済株式数（加重平均・基本）×その日の株価で決める。
    決算書の数は提出日から使う（後知恵なし）。株式分割は提出日より後のものだけを掛けて、今の株価の単位に直す。
  - 株価は配当・分割調整済み（配当を再投資した場合の値動き）。2倍・下落の判定は終値。
  - 途中で上場廃止（買収など）になった銘柄は、最後の終値で手じまったことにする。
  - 恩株: 2倍になった日の終値で、税（20.315%）を引いて元本が戻る株数（55.65%）を売る。残りはそのまま持つ。
    売ったお金・損切りしたお金はS&P500（SPY）に入れておく。最後に残った株・SPYは売らずに評価する（含み益に税をかけない）。
"""
import argparse
import datetime as dt
import json
import os
import statistics as st
import sys
import time
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backtest_lib import DEFAULT_CACHE, UA, curl, load_universe, load_prices, is_member

SEC_UA = "stock-backtest-script contact@example.com"
TAX = 0.20315
SELL_AT_2X = 1 / (2 - TAX)          # 2倍で売って、税を引いて元本が戻る割合（約55.65%）
HORIZONS = (1, 2, 3, 5)             # 年
TD = 252                            # 1年の取引日数
GROUPS = (("1〜50位", 1, 50), ("51〜150位", 51, 150), ("151〜300位", 151, 300), ("301位〜", 301, 9999))
BRK_A_TO_B = 1500                   # バークシャーは決算書の株数がA株換算


def sec_get(url):
    import subprocess
    for attempt in range(4):
        r = subprocess.run(["curl", "-sS", "--compressed", "--max-time", "60", "-A", SEC_UA, url], capture_output=True)
        txt = r.stdout.decode("utf-8", errors="replace")
        if r.returncode == 0 and txt.startswith("{"):
            return txt
        if "NoSuchKey" in txt or "Not Found" in txt:
            return ""
        time.sleep(1 + attempt * 2)
    return ""


def cmd_fetch(a):
    members, data = load_universe(a.cache)
    out_dir = os.path.join(a.cache, "onkabu")
    os.makedirs(out_dir, exist_ok=True)
    tick = json.loads(sec_get("https://www.sec.gov/files/company_tickers.json"))
    cik = {v["ticker"].upper(): v["cik_str"] for v in tick.values()}

    def one(sym):
        path = os.path.join(out_dir, sym + ".json")
        if os.path.exists(path):
            return True
        res = {"splits": [], "shares": []}
        txt = curl(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym.replace('.', '-')}?interval=1mo&range=max&events=split")
        try:
            ev = json.loads(txt)["chart"]["result"][0].get("events", {}).get("splits", {})
            res["splits"] = sorted((dt.datetime.utcfromtimestamp(x["date"]).strftime("%Y-%m-%d"), x["numerator"] / x["denominator"]) for x in ev.values())
        except Exception:
            return False
        c = cik.get(sym.replace(".", "-").upper())
        if c:
            # companyconcept が空を返すことがある（KOなど）ので、そのときは companyfacts（全項目、数MB）から取る
            for url in (None, f"https://data.sec.gov/api/xbrl/companyfacts/CIK{c:010d}.json"):
                allf = json.loads(sec_get(url) or "{}").get("facts", {}) if url else None
                for concept in ("us-gaap/WeightedAverageNumberOfSharesOutstandingBasic", "dei/EntityCommonStockSharesOutstanding"):
                    if allf is None:
                        t = sec_get(f"https://data.sec.gov/api/xbrl/companyconcept/CIK{c:010d}/{concept}.json")
                        time.sleep(0.15)
                        units = json.loads(t)["units"] if t else {}
                    else:
                        tx, tag = concept.split("/")
                        units = allf.get(tx, {}).get(tag, {}).get("units", {})
                    facts = units.get("shares") or []
                    if not isinstance(facts, list):
                        continue
                    # us-gaap は期間の平均株数（start あり）。9カ月の累計なども平均なので使える
                    rows = [(f["filed"], f["end"], f["val"]) for f in facts
                            if f.get("filed") and f.get("val") and (f.get("start") or concept.startswith("dei"))]
                    if rows:
                        res["shares"] = sorted(rows)
                        res["concept"] = concept
                        break
                if res["shares"]:
                    break
        json.dump(res, open(path, "w"))
        return True

    syms = sorted(data)
    with ThreadPoolExecutor(2) as ex:
        ok = list(ex.map(one, syms))
    have = sum(1 for s in syms if json.load(open(os.path.join(out_dir, s + ".json"))).get("shares")) if all(ok) else None
    print(f"{len(syms)} 銘柄、取得 {sum(ok)}、株式数あり {have}")


# ---------- 計算 ----------

def clean_shares(info, px, mult=1.0):
    """株式数を今の株価の単位（分割後）に直し、桁の誤りを直して返す。[(提出日, 期末, 株式数)]（提出日の順）
    SECのデータには株式数が1000倍・1000分の1になっているものがある（例: SHW・AMG は1000倍、DLTR・LUV は1000分の1）。
    時価総額÷売買代金（60日平均）は普通40〜800程度なので、0.5未満なら1000倍、30000超なら1000分の1に直す。
    そのうえで、直前の値の3倍超・3分の1未満に飛んだ値は捨てる。mult はA株換算の補正（BRK.B）"""
    pos = {d: k for k, d in enumerate(px["date"])}
    dv60 = {}

    def turnover_ratio(day, v):
        while day not in pos and day > px["date"][0]:
            day = (dt.date.fromisoformat(day) - dt.timedelta(days=1)).isoformat()
        i = pos.get(day)
        if i is None or i < 60:
            return None
        if i not in dv60:
            dv60[i] = sum(px["c"][k] * px["v"][k] for k in range(i - 60, i)) / 60
        return v * px["c"][i] / dv60[i] if dv60[i] > 0 else None

    def adj(filed, val):
        f = mult
        for d, r in info["splits"]:
            if d > filed:
                f *= r
        return val * f
    rows = []
    for filed, end, val in info["shares"]:
        v = adj(filed, val)
        r = turnover_ratio(filed, v)
        if r is None:      # 株価データ（2013年〜）より前の提出は確かめられないので使わない
            continue
        while r < 0.5:
            v, r = v * 1000, r * 1000
        while r > 30000:
            v, r = v / 1000, r / 1000
        rows.append((end, filed, v))
    rows.sort()
    if not rows:
        return []
    ref = st.median(v for _, _, v in rows[:8])
    out = []
    for end, filed, v in rows:
        if ref / 3 <= v <= ref * 3:
            out.append((filed, end, v))
            ref = v
    return sorted(out)


def shares_asof(clean, day):
    """day までに提出された決算書のうち、期末が一番新しい株式数（今の株価の単位）"""
    best = None
    for filed, end, v in clean:
        if filed > day:
            break
        if best is None or end >= best[0]:
            best = (end, v)
    return best[1] if best else None


def first_days_of_month(days):
    out, seen = [], set()
    for d in days:
        if d[:7] not in seen:
            seen.add(d[:7])
            out.append(d)
    return out


def forward(s, i, spy_c, spy_pos, horizon_days):
    """i日目の終値で買ったときの、horizon_days 先までの結果"""
    c, dates = s["c"], s["date"]
    p0 = c[i]
    last = min(i + horizon_days, len(c) - 1)
    delisted = i + horizon_days > len(c) - 1
    t2 = None
    low_before = 1.0   # 2倍になる前（ならなければ期間中）の最安値（買値に対する比率）
    low_all = 1.0
    for k in range(i + 1, last + 1):
        r = c[k] / p0
        low_all = min(low_all, r)
        if t2 is None:
            low_before = min(low_before, r)
            if r >= 2:
                t2 = k
    return {"i": i, "p0": p0, "last": last, "delisted": delisted, "t2": t2, "low_before": low_before, "low_all": low_all,
            "ret": c[last] / p0, "end_date": dates[last]}


def spy_ret(spy_c, spy_pos, d0, d1):
    return spy_c[spy_pos[d1]] / spy_c[spy_pos[d0]]


def onkabu_value(s, i, f, spy_c, spy_pos, stop=None, sell_frac=SELL_AT_2X):
    """1ドル買って、期間の終わりの価値（税引き後の現金化分＋含みのまま）。f は forward() の結果"""
    c, dates = s["c"], s["date"]
    p0, last = c[i], f["last"]
    end_d = f["end_date"]
    # 損切り（2倍になる前に買値の stop 倍以下）
    if stop is not None:
        for k in range(i + 1, (f["t2"] or last) + 1):
            if c[k] / p0 <= stop:
                cash = c[k] / p0   # 損失には税なし（損益通算は考えない）
                return cash * spy_ret(spy_c, spy_pos, nearest(spy_pos, dates[k]), nearest(spy_pos, end_d))
    if f["t2"] is None or sell_frac == 0:
        return f["ret"]
    k = f["t2"]
    r2 = c[k] / p0
    proceeds = sell_frac * r2
    tax = TAX * sell_frac * (r2 - 1)
    cash = (proceeds - tax) * spy_ret(spy_c, spy_pos, nearest(spy_pos, dates[k]), nearest(spy_pos, end_d))
    return cash + (1 - sell_frac) * f["ret"]


def nearest(pos, d):
    while d not in pos:
        d = (dt.date.fromisoformat(d) - dt.timedelta(days=1)).isoformat()
    return d


def pct(x, d=1):
    return f"{x * 100:.{d}f}%"


def med(xs):
    return st.median(xs) if xs else float("nan")


def cmd_run(a):
    members, data = load_universe(a.cache, min_bars=60)
    spy = data.pop("SPY", None) or load_prices(a.cache, "SPY")
    for k in ("QQQ", "^VIX"):
        data.pop(k, None)
    spy_c, spy_pos = spy["c"], {d: k for k, d in enumerate(spy["date"])}
    info = {}
    for sym in data:
        p = os.path.join(a.cache, "onkabu", sym + ".json")
        if os.path.exists(p):
            info[sym] = clean_shares(json.load(open(p)), data[sym], BRK_A_TO_B if sym == "BRK.B" else 1.0)
    pos = {s: {d: k for k, d in enumerate(v["date"])} for s, v in data.items()}
    last_day = spy["date"][-1]
    entries = [d for d in first_days_of_month(spy["date"]) if "2015-01-01" <= d]

    # 各月の構成銘柄と時価総額の順位
    rows = []          # (entry, sym, rank, i)
    cover = []
    for d in entries:
        mem = [s for s, sp in members.items() if is_member(sp, d)]
        caps = []
        for s in mem:
            if s not in data or d not in pos[s] or s not in info:
                continue
            sh = shares_asof(info[s], d)
            if not sh:
                continue
            i = pos[s][d]
            caps.append((sh * data[s]["c"][i], s, i))
        caps.sort(reverse=True)
        cover.append((d, len(mem), len(caps)))
        for r, (cap, s, i) in enumerate(caps, 1):
            rows.append((d, s, r, i, cap))

    def group_of(r):
        for name, lo, hi in GROUPS:
            if lo <= r <= hi:
                return name

    out = []
    w = out.append
    w("---\ntype: backtest\ntitle: 2倍株の基礎調査（銘柄を選ばない素の確率）\n"
      f"created: {dt.date.today().isoformat()}\nscript: tools/backtest_onkabu.py\n---\n")
    w("# 2倍株の基礎調査（銘柄を選ばない素の確率）\n")
    w("毎月の最初の取引日に、その日のS&P500の構成銘柄を**全部**買ったことにして、その後の値動きを数えた。"
      "銘柄を選ぶルールはまだ入れていない。ここで出る数字が「何もしないで当たる確率」で、今後つくるルールはこれを上回る必要がある。\n")
    avg_mem = st.mean(x[1] for x in cover)
    avg_cov = st.mean(x[2] for x in cover)
    if a.summary and os.path.exists(a.summary):
        w(open(a.summary).read())
    w("## 前提\n")
    w(f"- 期間: 買う日 {entries[0]}〜（期間の長さの分だけデータがある月まで）、データの最終日 {last_day}")
    w(f"- 対象: その日のS&P500の構成銘柄。1カ月あたり平均 {avg_mem:.0f} 銘柄のうち、株価と株式数がそろった {avg_cov:.0f} 銘柄（{avg_cov / avg_mem:.0%}）。"
      "NASDAQ100は過去の構成銘柄のデータがないため含めない（NASDAQ100の大半はS&P500にも入っている）")
    w("- 時価総額の順位: その日までにSECに提出された決算書の株式数（加重平均・基本）×その日の株価。後知恵なし")
    w("- 株価は配当込み（配当を再投資した値動き）。2倍・下落の判定は終値")
    w("- **残る偏り**: Yahooから消えた銘柄（主に買収された会社、ほかに破綻した会社）は株価が取れず、数に入らない。"
      "買収はプレミアムつきで終わることが多く、破綻は大きな損失なので、偏りの向きは一方ではない")
    w("- 期間中に上場廃止になった銘柄は、最後の終値で手じまったことにする")
    w("- 1カ月ごとに同じ銘柄を何度も数えているので、件数は多く見えるが独立した試行ではない。時期ごとの差（下の表）で確かさを見る\n")

    # ---------- 表1: 2倍になる確率 ----------
    w("## 1. 何%が2倍になったか（期間の長さ別・時価総額の順位別）\n")
    w("「2倍前に−30%」は、2倍になる前に（2倍にならなかったものは期間中に）一度でも買値の30%下まで下がった割合。"
      "「SPYに勝った」は、期間の終わりの値上がりが同じ期間のS&P500（SPY）を上回った割合。\n")
    cache_f = {}
    for h in HORIZONS:
        hd = h * TD
        w(f"### {h}年以内\n")
        w("| 時価総額の順位 | 件数 | 2倍になった | 2倍までの取引日数（中央値） | 2倍前に−30% | 期間中に−50% | 期間の終わりの値上がり（中央値） | 同 平均 | SPYに勝った |")
        w("|---|---|---|---|---|---|---|---|---|")
        spy_rets = []
        by = {}
        for d, s, r, i, cap in rows:
            if spy_pos[d] + hd > len(spy_c) - 1:
                continue
            key = (d, s, h)
            f = forward(data[s], i, spy_c, spy_pos, hd)
            cache_f[key] = f
            sr = spy_c[spy_pos[d] + hd] / spy_c[spy_pos[d]]
            if f["delisted"]:
                sr = spy_ret(spy_c, spy_pos, d, nearest(spy_pos, f["end_date"]))
            for g in (group_of(r), "51位〜（合計）" if r > 50 else None, "全体"):
                if g:
                    by.setdefault(g, []).append((f, sr))
        order = [g[0] for g in GROUPS[:1]] + ["51位〜（合計）"] + [g[0] for g in GROUPS[1:]] + ["全体"]
        for g in order:
            xs = by.get(g, [])
            if not xs:
                continue
            n = len(xs)
            dbl = [f for f, _ in xs if f["t2"] is not None]
            w(f"| {g} | {n:,} | {pct(len(dbl) / n)} | {med([f['t2'] - f['i'] for f in dbl]):.0f}日 | "
              f"{pct(sum(f['low_before'] <= 0.7 for f, _ in xs) / n)} | {pct(sum(f['low_all'] <= 0.5 for f, _ in xs) / n)} | "
              f"{pct(med([f['ret'] - 1 for f, _ in xs]))} | {pct(st.mean(f['ret'] - 1 for f, _ in xs))} | "
              f"{pct(sum(f['ret'] > sr for f, sr in xs) / n)} |")
        spy_list = [spy_c[spy_pos[d] + hd] / spy_c[spy_pos[d]] for d in entries if spy_pos[d] + hd <= len(spy_c) - 1]
        w(f"| （参考）SPY | {len(spy_list)} | {pct(sum(x >= 2 for x in spy_list) / len(spy_list))} | | | | "
          f"{pct(med([x - 1 for x in spy_list]))} | {pct(st.mean(x - 1 for x in spy_list))} | |\n")

    # ---------- 表2: 時期ごと ----------
    w("## 2. 時期ごとの差（3年以内に2倍になった割合）\n")
    w("買った年ごと。相場の良し悪しでどれだけ変わるか。\n")
    w("| 買った年 | 1〜50位 | 51位〜 | 全体 | SPYの3年の値上がり |")
    w("|---|---|---|---|---|")
    hd = 3 * TD
    years = sorted({d[:4] for d, *_ in rows})
    for y in years:
        xs = [(r, cache_f[(d, s, 3)]) for d, s, r, i, cap in rows if d[:4] == y and (d, s, 3) in cache_f]
        if not xs:
            continue
        top = [f for r, f in xs if r <= 50]
        rest = [f for r, f in xs if r > 50]
        sp = [spy_c[spy_pos[d] + hd] / spy_c[spy_pos[d]] - 1 for d in entries if d[:4] == y and spy_pos[d] + hd <= len(spy_c) - 1]
        frac = lambda fs: pct(sum(f["t2"] is not None for f in fs) / len(fs)) if fs else "―"
        w(f"| {y} | {frac(top)} | {frac(rest)} | {frac([f for _, f in xs])} | {pct(st.mean(sp))} |")
    w("")

    # ---------- 表3: 恩株のやり方の比較 ----------
    w("## 3. 恩株にした場合と、ただ持ち続けた場合とSPYの比較（1銘柄に1ドル）\n")
    w(f"恩株: 2倍になった日に {pct(SELL_AT_2X)} を売る（税20.315%を引いて元本が戻る割合）。残りは期間の終わりまで持つ。"
      "売ったお金・損切りしたお金はSPYに入れておく。期間の終わりの含み益には税をかけない（SPYも同じ）。\n")
    for h in (3, 5):
        w(f"### {h}年後の価値（中央値 / 平均 / SPYに勝った割合）\n")
        w("| 時価総額の順位 | 件数 | ただ持ち続ける | 恩株 | 恩株＋2倍前に−30%で損切り | 恩株＋2倍前に−50%で損切り | SPY |")
        w("|---|---|---|---|---|---|---|")
        hd = h * TD
        res = {}
        for d, s, r, i, cap in rows:
            f = cache_f.get((d, s, h))
            if not f:
                continue
            sr = spy_ret(spy_c, spy_pos, d, nearest(spy_pos, f["end_date"]))
            vals = (f["ret"], onkabu_value(data[s], i, f, spy_c, spy_pos),
                    onkabu_value(data[s], i, f, spy_c, spy_pos, stop=0.7),
                    onkabu_value(data[s], i, f, spy_c, spy_pos, stop=0.5), sr)
            for g in ("1〜50位" if r <= 50 else "51位〜（合計）", "全体"):
                res.setdefault(g, []).append(vals)
        for g in ("1〜50位", "51位〜（合計）", "全体"):
            xs = res.get(g, [])
            if not xs:
                continue
            cells = []
            for k in range(5):
                col = [v[k] for v in xs]
                cell = f"{med(col):.2f}倍 / {st.mean(col):.2f}倍"
                if k < 4:
                    cell += f" / {pct(sum(v[k] > v[4] for v in xs) / len(xs), 0)}"
                cells.append(cell)
            w(f"| {g} | {len(xs):,} | " + " | ".join(cells) + " |")
        w("")

    w("## 読み方の注意\n")
    w("- これは**銘柄を選ばない**場合の数字。恩株ツールの価値は、ここから選び方（ルール・著者）でどれだけ上積みできるかで決まる")
    w("- 平均が中央値より大きいのは、一部の銘柄が何倍にもなって平均を引き上げるため（少数の大当たりが成績を決める）")
    w("- 2倍の判定は終値。途中で一瞬2倍を超えても、終値で届かなければ数えない")
    w("- 税は日本の課税口座（20.315%）。為替と円での損益は考えていない")
    text = "\n".join(out) + "\n"
    if a.out:
        os.makedirs(os.path.dirname(a.out), exist_ok=True)
        open(a.out, "w").write(text)
    print(text)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("fetch", "run"):
        p = sub.add_parser(name)
        p.add_argument("--cache", default=DEFAULT_CACHE)
        if name == "run":
            p.add_argument("--out")
            p.add_argument("--summary", help="レポートの冒頭に入れる「まとめ」（Markdown）")
    a = ap.parse_args()
    {"fetch": cmd_fetch, "run": cmd_run}[a.cmd](a)


if __name__ == "__main__":
    main()
