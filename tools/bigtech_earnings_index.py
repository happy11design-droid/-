#!/usr/bin/env python3
"""大手4社（MSFT・GOOGL・AMZN・META）の決算の翌日の値動きで止める・売る形を、2004年〜の指数（SOX）で確かめる
（2026-11-08 ユーザーの指示「3で」＝採用はまだせず、2015年より前の指数で回数を増やして確かめる。
`新分析ツール/バックテスト結果/実際の運用の期間の確認_2026-10-23/大手4社の決算で止める・売る.md`）

決算の発表日: SECの決算の8-K（項目 2.02）の受付時刻（米国東部時間）。16時以降なら翌取引日、9時30分より前ならその日の値動き。
  キャッシュ（~/.cache/stock_backtest/long/sec/）になければ data.sec.gov から取って置く。
株価: Yahoo の日足（調整後終値）。~/.cache/stock_backtest/long/index/ になければ取って置く（MSFT・GOOGL・AMZN・META・^SOX）。
決算の季節: 前の決算から20取引日以上あいたら新しい季節。その時点で上場していた会社（METAは2012-05-18〜）がそろった日に平均を見る。
SOXでの形（引けで判定し、翌取引日の終値で売り買いする近似）:
  持ち続ける / 半分: 条件の日の翌日から20取引日はSOXを半分 / 売る: 20取引日は持たない（現金の利息なし）
使い方: python3 tools/bigtech_earnings_index.py [--out ファイル]
"""
import argparse
import bisect
import datetime as dt
import json
import os
import statistics as st
import subprocess
import time
from zoneinfo import ZoneInfo

C = os.path.expanduser("~/.cache/stock_backtest/long/")
UA_SEC = "stock-backtest-script contact@example.com"
ET = ZoneInfo("America/New_York")
CIKS = {"MSFT": ["0000789019"], "GOOGL": ["0001288776", "0001652044"], "AMZN": ["0001018724"], "META": ["0001326801"]}


def curl(url, ua):
    for i in range(4):
        r = subprocess.run(["curl", "-sS", "--max-time", "60", "-A", ua, url], capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip().startswith(("{", "[")):
            return r.stdout
        time.sleep(2 ** (i + 1))
    raise SystemExit(f"取れなかった: {url}")


def sec_json(name):
    os.makedirs(C + "sec", exist_ok=True)
    p = C + "sec/" + name
    if not os.path.exists(p):
        open(p, "w").write(curl("https://data.sec.gov/submissions/" + name, UA_SEC))
        time.sleep(0.3)
    return json.load(open(p))


def earnings_times(sym):
    """[(受付の東部時間の datetime)]。決算の8-K（2.02）"""
    out = []
    for cik in CIKS[sym]:
        a = sec_json(f"CIK{cik}.json")
        parts = [a["filings"]["recent"]] + [sec_json(f["name"]) for f in a["filings"].get("files", [])]
        for r in parts:
            for f, it, acc in zip(r["form"], r["items"], r["acceptanceDateTime"]):
                if f == "8-K" and "2.02" in (it or "") and acc:
                    t = dt.datetime.fromisoformat(acc.replace("Z", "+00:00")).astimezone(ET)
                    out.append(t)
    out.sort()
    keep = []
    for t in out:   # 同じ四半期の2通目（訂正など）は除く: 前の決算から45日以内は数えない
        if not keep or (t - keep[-1]).days > 45:
            keep.append(t)
    return keep


def yahoo(sym):
    os.makedirs(C + "index", exist_ok=True)
    p = C + "index/" + sym + ".json"
    if not os.path.exists(p):
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d&period1=0&period2={int(time.time()) + 86400}"
        res = json.loads(curl(url, "Mozilla/5.0"))["chart"]["result"][0]
        q = res["indicators"]["quote"][0]
        adj = (res["indicators"].get("adjclose") or [{}])[0].get("adjclose") or q["close"]
        rows = [[(dt.datetime(1970, 1, 1) + dt.timedelta(seconds=t) - dt.timedelta(hours=5)).date().isoformat(), c, a]
                for t, c, a in zip(res["timestamp"], q["close"], adj) if c and a]
        json.dump(rows, open(p, "w"))
    return {r[0]: r[2] for r in json.load(open(p))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    a = ap.parse_args()
    px = {s: yahoo(s) for s in CIKS}
    sox = yahoo("^SOX")
    days = sorted(d for d in sox if d >= "2004-01-01")
    di = {d: k for k, d in enumerate(days)}
    rx = []
    for s in CIKS:
        p = px[s]
        ks = sorted(p)
        for t in earnings_times(s):
            d = t.date().isoformat()
            i = bisect.bisect_left(ks, d)
            if i >= len(ks) or i < 1:
                continue
            if ks[i] != d:   # 休みの日の受付は、次の取引日の寄り付きの前とみなす
                r_, rd = p[ks[i]] / p[ks[i - 1]] - 1, ks[i]
            elif t.hour * 60 + t.minute >= 16 * 60 - 5:   # 引け後（15:55以降）→ 翌日
                if i + 1 >= len(ks):
                    continue
                r_, rd = p[ks[i + 1]] / p[ks[i]] - 1, ks[i + 1]
            else:   # 寄り付き前・取引時間中 → その日
                r_, rd = p[ks[i]] / p[ks[i - 1]] - 1, ks[i]
            if rd in di and rd >= "2004-07-01":
                rx.append((rd, s, r_, t.strftime("%Y-%m-%d %H:%M")))
    rx.sort()
    seas, cur = [], []
    for r in rx:
        if cur and di[r[0]] - di[cur[-1][0]] > 20:
            seas.append(cur)
            cur = []
        cur.append(r)
    seas.append(cur)
    listed = lambda s, d: min(px[s]) <= d   # その日に上場していたか
    rows = []
    for sz in seas:
        d_end = sz[-1][0]
        need = {s for s in CIKS if listed(s, sz[0][0])}
        got = {r[1] for r in sz}
        avg = st.mean(r[2] for r in sz)
        bad = [r for r in sz if r[2] <= -0.05]
        rows.append({"start": sz[0][0], "end": d_end, "n": len(got), "complete": need <= got, "avg": avg,
                     "e2n": bad[1][0] if len(bad) >= 2 else None, "items": [(r[1], r[0], round(r[2], 4), r[3]) for r in sz]})
    P = [sox[d] for d in days]

    def fwd(d, n=20):
        k = di[d]
        if k + n >= len(P):
            return None, None
        w = P[k:k + n + 1]
        pk, mdd = w[0], 0.0
        for x in w:
            pk = max(pk, x)
            mdd = min(mdd, x / pk - 1)
        return P[k + n] / P[k] - 1, mdd

    def strat(trig, w_, n=20, lo="2004-07-01", hi="2099"):
        """trig の日の翌日の終値から n 取引日、SOXの持ち分を w_ にする（それ以外は1）。年率と最大下落率"""
        wt = [1.0] * len(P)
        for d in trig:
            k = di[d]
            for j in range(k + 1, min(len(P), k + 1 + n)):
                wt[j] = w_   # j の日の終値→j+1 の日の終値の持ち分
        eq, pk, mdd = 1.0, 1.0, 0.0
        ks = [k for k, d in enumerate(days) if lo <= d < hi and k + 1 < len(P)]
        for k in ks:
            eq *= 1 + wt[k] * (P[k + 1] / P[k] - 1)
            pk = max(pk, eq)
            mdd = min(mdd, eq / pk - 1)
        yrs = len(ks) / 252
        return eq ** (1 / yrs) - 1 if yrs > 0 else 0.0, mdd

    out = []
    w = out.append
    w("## 決算の季節ごとの大手4社の決算の翌日の値動き（2004年〜、SECの8-Kの受付時刻で判定）\n")
    w("| 季節 | " + " | ".join(CIKS) + " | 平均 | 2社以上−5% | SOX 20取引日後 | 20取引日の中の最大の下げ |")
    w("|---|" + "---|" * (len(CIKS) + 4))
    for r in rows:
        cells = []
        for s in CIKS:
            v = [x for x in r["items"] if x[0] == s]
            cells.append(f"{v[0][2] * 100:+.1f}%" if v else "—")
        f20, m20 = fwd(r["end"])
        w(f"| {r['start'][:7]} | " + " | ".join(cells) + f" | {r['avg'] * 100:+.1f}%{'' if r['complete'] else '（そろわず）'} | "
          f"{'●' if r['e2n'] else ''} | {'—' if f20 is None else f'{f20 * 100:+.1f}%'} | {'—' if m20 is None else f'{m20 * 100:+.1f}%'} |")
    summ = {}
    w("\n## 条件ごとの、SOXの20取引日後（条件の日の終値から）\n")
    w("| 条件 | 期間 | 当てはまった回 | 20取引日後の中央値（平均） | 下げた回 | 20取引日の中の最大の下げの中央値 | 当てはまらない季節の20取引日後の中央値 |")
    w("|---|---|---|---|---|---|---|")
    conds = {"平均−2%以下": lambda r: r["complete"] and r["avg"] <= -0.02, "平均−3%以下": lambda r: r["complete"] and r["avg"] <= -0.03,
             "平均−4%以下": lambda r: r["complete"] and r["avg"] <= -0.04, "2社以上−5%以下": lambda r: bool(r["e2n"])}
    trigd = {}
    for nm, f in conds.items():
        trigd[nm] = [(r["e2n"] if nm.startswith("2社") else r["end"]) for r in rows if f(r)]
        for lab, lo, hi in (("2004〜2014年", "2004-07-01", "2015-01-01"), ("2015年〜", "2015-01-01", "2099")):
            ev = [d for d in trigd[nm] if lo <= d < hi]
            other = [r["end"] for r in rows if not f(r) and lo <= r["end"] < hi]
            fr = [fwd(d) for d in ev]
            fr = [x for x in fr if x[0] is not None]
            fo = [fwd(d)[0] for d in other if fwd(d)[0] is not None]
            if not fr:
                w(f"| {nm} | {lab} | 0 | — | — | — | — |")
                continue
            w(f"| {nm} | {lab} | {len(fr)}（{'・'.join(d[:7] for d in ev)}） | {st.median(x[0] for x in fr) * 100:+.1f}%（{st.mean(x[0] for x in fr) * 100:+.1f}%） | "
              f"{sum(x[0] < 0 for x in fr)}/{len(fr)} | {st.median(x[1] for x in fr) * 100:+.1f}% | {st.median(fo) * 100:+.1f}% |")
    w("\n## SOXで持ち続ける・半分・売る（条件の日の翌日の終値から20取引日。年率・最大下落率）\n")
    w("| 条件 | 形 | 2004〜2014年 年率 | 最大下落率 | 2015年〜 年率 | 最大下落率 |")
    w("|---|---|---|---|---|---|")
    b1, b2 = strat([], 1.0, lo="2004-07-01", hi="2015-01-01"), strat([], 1.0, lo="2015-01-01")
    w(f"| — | 持ち続ける | {b1[0] * 100:.1f}% | {b1[1] * 100:.1f}% | {b2[0] * 100:.1f}% | {b2[1] * 100:.1f}% |")
    for nm in conds:
        for lab, wt in (("半分", 0.5), ("売る", 0.0)):
            s1, s2 = strat(trigd[nm], wt, lo="2004-07-01", hi="2015-01-01"), strat(trigd[nm], wt, lo="2015-01-01")
            summ[f"{nm}・{lab}"] = (s1, s2)
            w(f"| {nm} | {lab} | {s1[0] * 100:.1f}% | {s1[1] * 100:.1f}% | {s2[0] * 100:.1f}% | {s2[1] * 100:.1f}% |")
    txt = "\n".join(out) + "\n"
    rp = os.path.expanduser("~/.cache/stock_backtest/results/")
    os.makedirs(rp, exist_ok=True)
    json.dump(rows, open(rp + "bigtech_earnings_seasons.json", "w"), ensure_ascii=False)
    if a.out:
        open(a.out, "w", encoding="utf-8").write(txt)
    print(txt)


if __name__ == "__main__":
    main()
