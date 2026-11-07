#!/usr/bin/env python3
"""始める日と乱数を変えた確かめ（OPT_ROLL の出力、1年＝250取引日）から、形ごとの「始める日によらない年率」を出す（2026-11-07）

1年の区切りごとの損益 r を、すべての始める日・乱数で集め、幾何平均 exp(平均(log(1+r)))−1 を年率とみなす。中央値と、悪い方・良い方から10%も出す。
使い方: python3 tools/roll_cagr.py <json> [<json> ...]
"""
import json
import math
import statistics as st
import sys

for path in sys.argv[1:]:
    a = json.load(open(path))
    days, win = a["days"], a["win"]
    pos = {d: k for k, d in enumerate(days)}
    for nm, rows in a["forms"].items():
        if nm.startswith("今のルール（傾き"):
            continue
        for lo, hi, lab in (("2015-01-01", "2099-12-31", "2015年〜"), ("2015-01-01", "2021-12-31", "2015〜2021年に始めた"), ("2022-01-01", "2099-12-31", "2022年〜に始めた")):
            R = [r[0] for d, rs in rows.items() if lo <= d <= hi and pos[d] + win <= len(days) - 1 for r in rs]
            if not R:
                continue
            g = math.exp(st.mean(math.log(1 + x) for x in R)) - 1
            q = sorted(R)
            print(f"{path.split('/')[-1]} | {nm.split('（3日間）')[-1] or '今のルール'} | {lab} | 1年の区切り {len(R)} | 幾何平均 {g * 100:.1f}% | 中央値 {st.median(R) * 100:.1f}% | 悪い方から10% {q[len(q) // 10] * 100:+.1f}% | 良い方から10% {q[-len(q) // 10] * 100:+.1f}%")
