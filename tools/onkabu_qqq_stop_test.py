#!/usr/bin/env python3
"""恩株ツールの待っている現金（QQQ）に損切りを付ける形と、株を損切りした後しばらく現金で待つ形を、今の形と比べる
（2026-11-08 ユーザーの指示「qqqの損失が30%？の損切りに達した時損切りするの？そのまま？損切りしても候補の銘柄が損切りした直後にqqqをまた買うの？」→「はい。テストして。」）

今の採用ルール（恩株ツール/採用ルール.json）: 1銘柄ずつ（資金4,500ドル）、2倍で55.7%を売って恩株、終値で−30%の損切り、189取引日で売る、
待っている現金はQQQ（損切りなし。株を売った代金はすぐQQQに戻す）、合図が多いときは6か月の上昇が大きい順。
QQQの税・手数料（qtax）を入れた表と入れない表を出す（入れない表は今までの恩株ツールのバックテストと同じ数え方）。
使い方: python3 tools/onkabu_qqq_stop_test.py [--seeds 3] [--out ファイル]
"""
import argparse
import os
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_onkabu_search as bs
import onkabu_sim as sim
from backtest_lib import DEFAULT_CACHE, load_prices

SIG = {"mom": ("r126", 1.0), "hi": "nh", "rev": 0.1, "extra": None}
FORMS = [
    ("今の形（QQQに損切りなし・損切りの代金はすぐQQQ）", {}),
    ("QQQを買値の平均から−20%で売り、上向きの50日線で買い直す", {"qstop": (0.20, "cost")}),
    ("QQQを買値の平均から−30%で売り、上向きの50日線で買い直す", {"qstop": (0.30, "cost")}),
    ("QQQを持ってからの高値から−20%で売り、上向きの50日線で買い直す", {"qstop": (0.20, "peak")}),
    ("QQQを持ってからの高値から−30%で売り、上向きの50日線で買い直す", {"qstop": (0.30, "peak")}),
    ("株を損切りした後20取引日は現金（QQQを買わない）", {"qoff": 20}),
    ("株を損切りした後60取引日は現金（QQQを買わない）", {"qoff": 60}),
    ("株を損切りした後20取引日は現金で、新しい合図も買わない", {"qoff": 20, "skip": 20}),
]


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
    for qtax in (False, True):
        w(f"\n### {'QQQの税・手数料込み' if qtax else 'QQQの税・手数料なし（今までの恩株ツールのバックテストと同じ数え方）'}\n")
        w("| 形 | " + " | ".join(f"{c[0]} 年率（最大下落率）" for c in bs.CONDS) + " | 株の損切り（2015年〜NVDAを除く） | QQQの損切り |")
        w("|---|" + "---|" * (len(bs.CONDS) + 2))
        for nm, extra in FORMS:
            cfg = {"slots": 1, "stop": 0.3, "T": 189, "rot": None, "entry": "open", "order": "mom_desc", "capital": 4500.0, "qtax": qtax, **extra}
            cells, nstop, nq = [], 0, 0
            for name, s0, s1, ex in bs.CONDS:
                days = [d for d in spy["date"] if s0 <= d <= s1]
                sbd = bs.sig_by_day(SIG, ex)
                cs, ms = [], []
                for seed in range(a.seeds):
                    col = name == "2015年〜 NVDAを除く" and seed == 0
                    r = sim.simulate(feats, days, sbd, cash_px=qqq, seed=seed, collect=col, **cfg)
                    c, m = sim.metrics(r["curve"], days)
                    cs.append(c)
                    ms.append(m)
                    if col:
                        nstop = sum(1 for x in r["log"] if x[4] == "損切り")
                        nq = r["nq"]
                cells.append(f"{st.median(cs) * 100:.1f}%（{st.median(ms) * 100:.0f}%）")
            w(f"| {nm} | " + " | ".join(cells) + f" | {nstop} | {nq} |")
            print(L[-1], flush=True)
    w("\n（QQQを持ち続けた場合の年率・最大下落率は、恩株ツールの今までの結果の比べる相手の行を参照）")
    txt = "\n".join(L) + "\n"
    if a.out:
        open(a.out, "w", encoding="utf-8").write(txt)
    print(txt)


if __name__ == "__main__":
    main()
