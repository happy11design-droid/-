#!/usr/bin/env python3
"""恩株ツールの合図の後、下がるのを待って買う形と、今の「合図の翌日の寄り付きで買う」形を比べる（2026-11-08 ユーザーの指示「恩株ツールのバックテストして」）

今の採用ルール（恩株ツール/採用ルール.json）: 合図＝6か月で+100%以上・52週高値の更新・売上の前年同期比≧10%、1銘柄ずつ（資金4,500ドル）、
2倍で55.7%を売って恩株、終値で−30%の損切り、189取引日で売る、乗り換えなし、待っている現金はQQQ、合図が多いときは6か月の上昇が大きい順。
買い方だけを変える: open（今）、dipX_N（N取引日以内に合図の日の終値の−X%まで下がったら指値で買う。下がらなければ買わない。待っている間は枠を使う）。
使い方: python3 tools/onkabu_dip_test.py [--seeds 3] [--out ファイル]
"""
import argparse
import datetime as dt
import statistics as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import backtest_onkabu_search as bs
import onkabu_sim as sim
from backtest_lib import DEFAULT_CACHE, load_prices

SIG = {"mom": ("r126", 1.0), "hi": "nh", "rev": 0.1, "extra": None}
ENTRIES = ["open", "dip5", "dip10", "dip20_60", "dip20_126", "dip30_126", "dip30_250", "dip40_126", "dip40_250"]
LAB = {"open": "合図の翌日の寄り付き（今）", "dip5": "−5%まで待つ（10日）", "dip10": "−10%まで待つ（20日）"}


def lab(e):
    if e in LAB:
        return LAB[e]
    x, n = e[3:].split("_")
    return f"−{x}%まで待つ（{n}日）"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--out")
    a = ap.parse_args()
    members, spy, feats = bs.load_all()
    qd = load_prices(DEFAULT_CACHE, "QQQ")
    qqq = dict(zip(qd["date"], qd["c"]))
    bs._init(feats, spy, qqq)
    L = []
    w = L.append
    w("| 買い方 | " + " | ".join(f"{c[0]} 年率（最大下落率）" for c in bs.CONDS) + " | 売買の数（2015年〜） | 2倍になった | 損切り | 期限で売った | 1回平均 |")
    w("|---|" + "---|" * (len(bs.CONDS) + 5))
    for e in ENTRIES:
        cfg = {"slots": 1, "stop": 0.3, "T": 189, "rot": None, "entry": e, "order": "mom_desc", "capital": 4500.0}
        cells = []
        logs = None
        for name, s0, s1, ex in bs.CONDS:
            days = [d for d in spy["date"] if s0 <= d <= s1]
            sbd = bs.sig_by_day(SIG, ex)
            cs, ms = [], []
            for seed in range(a.seeds):
                r = sim.simulate(feats, days, sbd, cash_px=qqq, seed=seed, collect=(name == "2015年〜 NVDAを除く" and seed == 0), **cfg)
                c, m = sim.metrics(r["curve"], days)
                cs.append(c); ms.append(m)
                if r["log"]:
                    logs = r["log"]
            cells.append(f"{st.median(cs) * 100:.1f}%（{st.median(ms) * 100:.0f}%）")
        lg = logs or []
        n = len([x for x in lg])
        why = lambda k: sum(1 for x in lg if x[4] == k)
        avg = st.mean(x[3] - 1 for x in lg) if lg else 0
        w(f"| {lab(e)} | " + " | ".join(cells) + f" | {n} | {why('2倍')}（{why('2倍') / n * 100:.0f}%） | {why('損切り')}（{why('損切り') / n * 100:.0f}%） | {why('時間')}（{why('時間') / n * 100:.0f}%） | {avg * 100:+.1f}% |" if n else f"| {lab(e)} | " + " | ".join(cells) + " | 0 | — | — | — | — |")
        print(L[-1], flush=True)
    txt = "\n".join(L) + "\n"
    if a.out:
        open(a.out, "w", encoding="utf-8").write(txt)
    print(txt)


if __name__ == "__main__":
    main()
