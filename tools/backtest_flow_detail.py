#!/usr/bin/env python3
"""流れ（市場の局面）を使う形の詳しい比較: 年ごとの成績と、信用取引で借りた日数・最大の額・金利（2026-10-13 ユーザーの指示）

使い方:
  tools/backtest_onkabu_combined.py newtrades    # 先に新分析ツールの売買の一覧を作っておく
  tools/backtest_flow_detail.py [--seeds 10] [--out FILE]

期間は 2015年〜（NVDAを含む）。形は backtest_onkabu_combined.VARIANTS_FLOW3 と同じ（今の形・案1・案5・案5'）。
年ごとの数値は乱数（同じ日の候補の順）10通りの中央値。資金は新分析ツール12,000ドル・恩株ツール4,500ドル（合計16,500ドル）。
"""
import argparse
import datetime as dt
import json
import os
import pickle
import statistics as st
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_onkabu_combined as m
from backtest_lib import DEFAULT_CACHE, load_prices

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "新分析ツール", "バックテスト結果", "流れ（市場の局面）を使う形_信用取引の詳しい比較.md")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args()
    import backtest_onkabu_search as bs_
    import onkabu_lib as ol
    members, spy, feats = bs_.load_all()
    nt = pickle.load(open(m.NEW_PKL, "rb"))
    trades, has = m.upgrade_trades(nt["trades"])
    ind = nt["ind"]
    sig = {"mom": ("r126", 1.0), "hi": "nh", "rev": 0.1, "extra": None}
    sb = {}
    for s, f in feats.items():
        mm = ol.signal(f, sig) & f["member"]
        mm[:260] = False
        for i in np.nonzero(mm)[0]:
            sb.setdefault(f["date"][i], []).append(s)
    q = load_prices(DEFAULT_CACHE, "QQQ")
    qqq = dict(zip(q["date"], q["c"]))
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    tab = json.load(open(os.path.join(root, "新分析ツール", "2倍ETFの対応表.json"), encoding="utf-8"))
    lev = {u: (2, -x["drag"] / 252) for u, x in tab.items() if isinstance(x, dict) and "drag" in x and u in has}
    regs = m.regimes()
    days = [d for d in spy["date"] if d >= "2015-01-02"]
    years = sorted({d[:4] for d in days})
    di = {d: k for k, d in enumerate(days)}
    res = {}
    for label, kw in m.VARIANTS_FLOW3:
        kw2 = {k: v for k, v in kw.items() if k not in ("cash", "reg")}
        if "reg" in kw:
            kw2["reg"] = regs[kw["reg"]]
        rows = []
        for seed in range(a.seeds):
            curve, _, rcurve = m.run(feats, trades, ind, days, sb, seed=seed, cash_px=qqq, capital=16500.0, lev_info=lev, **kw2)
            yr = {}
            for y in years:
                lo, hi = min(d for d in days if d[:4] == y), max(d for d in days if d[:4] == y)
                start = curve[di[lo] - 1] if di[lo] else 16500.0
                yr[y] = curve[di[hi]] / start - 1
            mg = m.STATS.get("mg", {})
            rows.append({"yr": yr, "cagr": m.metrics(curve, days)[0], "mdd": m.metrics(curve, days)[1], "rmdd": m.metrics(rcurve, days)[1],
                         "final": curve[-1], "mg": {y: mg.get(y, [0, 0.0, 0.0, 0.0]) for y in years}})
        med = lambda f: st.median(f(r) for r in rows)
        res[label] = {"cagr": med(lambda r: r["cagr"]), "mdd": med(lambda r: r["mdd"]), "rmdd": med(lambda r: r["rmdd"]),
                      "final": med(lambda r: r["final"]),
                      "yr": {y: med(lambda r, y=y: r["yr"][y]) for y in years},
                      "mg": {y: [med(lambda r, y=y, k=k: r["mg"][y][k]) for k in range(4)] for y in years},
                      "mg_max": max(max(r["mg"][y][3] for y in years) for r in rows)}
        print(label, f"{res[label]['cagr']:.1%}", flush=True)

    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: 流れ（市場の局面）を使う形・信用取引の詳しい比較\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_flow_detail.py\n---\n")
    w("# 流れ（市場の局面）を使う形・信用取引の詳しい比較（2015年〜、NVDAを含む）\n")
    w(__doc__.split("\n", 6)[6].strip() + "\n")
    w("## 1. 全期間\n")
    w("| 形 | 年率 | 含み損込みの最大下落率 | 確定した損の最大下落率 | 最後の資産（16,500ドルから） | 借りた額の最大（新分析ツールの資産比、乱数10通りの最悪） |")
    w("|---|---|---|---|---|---|")
    for label, r in res.items():
        w(f"| {label} | {r['cagr']:.1%} | {r['mdd']:.0%} | {r['rmdd']:.0%} | {r['final']:,.0f}ドル | {r['mg_max']:.0%} |")
    w("\n## 2. 年ごとの成績（その年の資産の増減）\n")
    w("| 年 | " + " | ".join(res) + " |")
    w("|---|" + "---|" * len(res))
    for y in years:
        w(f"| {y} | " + " | ".join(f"{r['yr'][y]:+.0%}" for r in res.values()) + " |")
    for label, r in res.items():
        if not any(v[0] for v in r["mg"].values()):
            continue
        w(f"\n## 3. 信用取引の中身: {label}\n")
        w("| 年 | 借りていた日数（取引日） | 借りた額の最大 | 最大のときの新分析ツールの資産比 | 金利の合計（年7%と仮定） |")
        w("|---|---|---|---|---|")
        for y in years:
            v = r["mg"][y]
            w(f"| {y} | {v[0]:.0f} | {v[1]:,.0f}ドル | {v[3]:.0%} | {v[2]:,.0f}ドル |")
        tot = sum(v[2] for v in r["mg"].values())
        w(f"\n金利の合計（全期間）: 約{tot:,.0f}ドル")
    w("\n## 注意\n")
    w("- 借りた額・金利は、資金16,500ドル（新分析ツール12,000ドル）で始めた場合。資産が増えると1銘柄の額も増えるので、後の年ほど金額が大きくなる。")
    w("- 追加の証拠金（株価が下がったときに求められる入金）や、証券会社が信用で買えない銘柄・2倍ETFは考えていない。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(a.out)


if __name__ == "__main__":
    main()
