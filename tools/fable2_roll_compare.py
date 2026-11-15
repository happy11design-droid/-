#!/usr/bin/env python3
"""Fableの次の策（2026-11-14）の1年の区切り（backtest_retest.py の OPT_ROLL の出力）を、決めた相手の形と比べる

使い方: python3 tools/fable2_roll_compare.py <87銘柄のjson> <全業種のjson>
相手: 策1 は「売るたびに引かれる（源泉徴収あり＝今の口座）」、策2 は「ベーシック（片道0.132%）」、策3・策5 は今のルール（OPT_COMBO の最初の形）。
同じ始める日・同じ乱数どうしで1年の損益の差をとり、平均・差が出た区切りのうち良い割合・2015〜2021年と2022年〜に始めた区切りの平均、
1年の中の最大下落率の差の平均・悪い方から5%の下落率を出す。
"""
import json
import statistics as st
import sys


def q(xs, p):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, max(0, int(round(p * (len(xs) - 1)))))]


def load(path):
    a = json.load(open(path))
    days, win = a["days"], a["win"]
    pos = {d: k for k, d in enumerate(days)}
    F = {n: {d: r for d, r in rows.items() if pos[d] + win <= len(days) - 1} for n, rows in a["forms"].items()
         if not n.startswith("今のルール（傾き")}
    return F


def ref_of(name, names):
    base = names[0]
    if "策1" in name:
        return next(n for n in names if "源泉徴収あり＝今の口座" in n)
    if "策2" in name:
        return next(n for n in names if "ベーシック" in n)
    return base


def comp(F, n, r):
    D, D1, D2, M, W, Wr = [], [], [], [], [], []
    for d, rows in F[n].items():
        for x, y in zip(rows, F[r][d]):
            D.append(x[0] - y[0])
            (D1 if d < "2022-01-01" else D2).append(x[0] - y[0])
            M.append(x[1] - y[1])
            W.append(x[1])
            Wr.append(y[1])
    nz = [x for x in D if abs(x) > 1e-9]
    return (st.mean(D), sum(1 for x in nz if x > 0) / max(1, len(nz)), st.mean(D1), st.mean(D2), st.mean(M), q(W, 0.95), q(Wr, 0.95))


def main():
    A = {"87銘柄": load(sys.argv[1]), "全業種": load(sys.argv[2])}
    print("| 形 | 比べる相手 | 監視銘柄 | 1年の損益の差の平均 | 良い割合 | 2015〜2021年に始めた | 2022年〜に始めた | 1年の中の最大下落率の差 | 悪い方から5%の下落率（相手） |")
    print("|---|---|---|---|---|---|---|---|---|")
    names = list(A["87銘柄"])
    for n in names[1:]:
        r = ref_of(n, names)
        if r == n:
            continue
        for wch, F in A.items():
            nn = n if n in F else next(x for x in F if x.split("＋")[-1] == n.split("＋")[-1])
            rr = r if r in F else next(x for x in F if x.split("＋")[-1] == r.split("＋")[-1])
            m = comp(F, nn, rr)
            print(f"| {n.split('＋')[-1]} | {rr.split('＋')[-1] if rr != list(F)[0] else '今のルール'} | {wch} | {m[0]:+.1%} | {m[1]:.0%} | {m[2]:+.1%} | {m[3]:+.1%} | {m[4]:+.1%} | {m[5]:.1%}（{m[6]:.1%}） |")


if __name__ == "__main__":
    main()
