#!/usr/bin/env python3
"""Fableの次の策（2026-11-14）の通しの成績を、OPT_EQDUMP_ALL の毎日の資金（乱数30通り）から集計する

使い方: python3 tools/fable2_summary.py <87銘柄のjson> <全業種のjson>
相手: 策1 は「売るたびに引かれる（源泉徴収あり＝今の口座）」、策2 は「ベーシック（片道0.132%）」、策3・策5 は今のルール（最初の形）。
"""
import datetime as dt
import json
import statistics as st
import sys


def metrics(c, days):
    yrs = (dt.date.fromisoformat(days[-1]) - dt.date.fromisoformat(days[0])).days / 365.25
    pk = md = 0.0
    for v in c:
        pk = max(pk, v)
        md = max(md, 1 - v / pk)
    return (c[-1] / c[0]) ** (1 / yrs) - 1, md


def between(c, days, lo, hi):
    ks = [k for k, d in enumerate(days) if lo <= d <= hi and c[k] is not None]
    return metrics([c[k] for k in ks], [days[k] for k in ks])[0]


def summ(F, n):
    days = F[n]["days"]
    out = []
    for c in F[n]["eq"]:
        ks = [k for k, v in enumerate(c) if v is not None]
        cc, dd = [c[k] for k in ks], [days[k] for k in ks]
        g, m = metrics(cc, dd)
        out.append((g, m, between(c, days, "2015-01-01", "2021-12-31"), between(c, days, "2022-01-01", "9999")))
    return [st.median(x[i] for x in out) for i in range(4)]


def ref_of(n, names):
    if "策1" in n:
        return next(x for x in names if "源泉徴収あり＝今の口座" in x)
    if "策2" in n:
        return next(x for x in names if "ベーシック" in x)
    return names[0]


def main():
    A = {"87銘柄": json.load(open(sys.argv[1])), "全業種": json.load(open(sys.argv[2]))}
    print("| 形 | 監視銘柄 | 年率 | 最大下落率 | 2015〜2021年 | 2022年〜 | 比べる相手との年率の差 |")
    print("|---|---|---|---|---|---|---|")
    for wch, F in A.items():
        names = [n for n in F if not n.startswith("今のルール（傾き")]
        S = {n: summ(F, n) for n in names}
        for n in names:
            r = ref_of(n, names)
            lab = n.split("＋")[-1] if n != names[0] else "今のルール（待っている現金はQQQ、手数料0.1%・年末に税）"
            diff = "" if r == n else f"{S[n][0] - S[r][0]:+.1f}pt（相手: {'今のルール' if r == names[0] else r.split('＋')[-1]}）".replace("pt", "")
            diff = "" if r == n else f"{(S[n][0] - S[r][0]) * 100:+.1f}pt（相手: {'今のルール' if r == names[0] else r.split('＋')[-1][:20]}）"
            print(f"| {lab} | {wch} | {S[n][0]:.1%} | {S[n][1]:.0%} | {S[n][2]:.1%} | {S[n][3]:.1%} | {diff} |")


if __name__ == "__main__":
    main()
