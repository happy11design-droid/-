#!/usr/bin/env python3
"""2022年のハイテクの下げが2倍の深さだった場合の試算（2026-10-11 ユーザーの指示）。
2021-11-19〜2022-12-30 の間、すべての値動き（新分析ツールの売買・倍増ツールの株・QQQ）の1日の騰落率を2倍にして、
新分析ツールだけ（現金のまま）／新分析＋QQQ／新分析＋恩株25%＋QQQ の資産の減り方を比べる。税引き後、資金18,000ドル、乱数20通りの中央値。
売買の日付・合図は実際のまま（下げが深くても、損切りや合図の日はずれない近似）"""
import os, sys, pickle, statistics as st
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_onkabu_combined as oc
import backtest_onkabu_search as bs_
import onkabu_lib as ol
from backtest_lib import DEFAULT_CACHE, load_prices
import json

LO, HI = "2021-11-19", "2022-12-30"

def stress_series(dates, vals):
    out = [vals[0]]
    for k in range(1, len(vals)):
        r = vals[k] / vals[k - 1] - 1 if vals[k - 1] else 0.0
        if LO < dates[k] <= HI:
            r = max(2 * r, -0.95)
        out.append(out[-1] * (1 + r))
    return out

def main():
    members, spy, feats = bs_.load_all()
    nt = pickle.load(open(oc.NEW_PKL, "rb"))
    new_trades, has2x = oc.upgrade_trades(nt["trades"])
    ind = nt["ind"]
    sig = {"mom": ("r126", 1.0), "hi": "nh", "rev": 0.1, "extra": None}
    sbd = {}
    for s, f in feats.items():
        m = ol.signal(f, sig) & f["member"]
        m[:260] = False
        for i in np.nonzero(m)[0]:
            sbd.setdefault(f["date"][i], []).append(s)
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    tab = json.load(open(os.path.join(root, "新分析ツール", "2倍ETFの対応表.json"), encoding="utf-8"))
    lev_info = {u: (2, -x["drag"] / 252) for u, x in tab.items() if isinstance(x, dict) and "drag" in x and u in has2x}
    q = load_prices(DEFAULT_CACHE, "QQQ")
    qqq = dict(zip(q["date"], q["c"]))
    # 2倍の深さにしたもの
    s_feats = {}
    for s, f in feats.items():
        g = dict(f)
        for k in ("c", "o"):
            g[k] = np.array(stress_series(f["date"], list(f[k])))
        s_feats[s] = g
    s_trades = []
    for t in new_trades:
        ds = sorted(t["path"])
        vals = stress_series(ds, [t["path"][d] for d in ds]) if ds else []
        s_trades.append({**t, "path": dict(zip(ds, vals))})
    qd = sorted(qqq)
    s_qqq = dict(zip(qd, stress_series(qd, [qqq[d] for d in qd])))
    days = [d for d in spy["date"] if d >= "2015-01-02"]
    forms = [("新分析ツールだけ（待っている現金は現金のまま）", dict(mode="pool", use_dbl=False), None),
             ("新分析ツールだけ（待っている現金はQQQ）", dict(mode="pool", use_dbl=False), "Q"),
             ("新分析＋恩株ツール（倍増用に25%を取っておく・待っている現金はQQQ）", dict(mode="pool", fund="free", dedup=False, dbl_frac=0.25, reserve=0.25), "Q")]
    rows = []
    for stress in (False, True):
        fe, tr, qq = (s_feats, s_trades, s_qqq) if stress else (feats, new_trades, qqq)
        for nm, kw, cash in forms:
            res = []
            for seed in range(20):
                curve, _, rcurve = oc.run(fe, tr, ind, days, sbd, seed=seed, cash_px=(qq if cash else None), capital=18000.0, lev_info=lev_info, **kw)
                c, m = oc.metrics(curve, days)
                rm = oc.metrics(rcurve, days)[1]
                # 2021-11-19 の直前の最高値から、2022年末までの一番の下げ（含み損込み・確定した損だけ）
                k0 = next(i for i, d in enumerate(days) if d > LO); k1 = max(i for i, d in enumerate(days) if d <= HI)
                pk = max(curve[:k0 + 1]); low = min(curve[k0:k1 + 1])
                rpk = max(rcurve[:k0 + 1]); rlow = min(rcurve[k0:k1 + 1])
                res.append((c, m, rm, 1 - low / pk, 1 - rlow / rpk, curve[k1] / curve[k0] - 1))
            med = [st.median(r[k] for r in res) for k in range(6)]
            worst = [max(r[k] for r in res) for k in (3, 4)]
            rows.append((("2倍の深さ" if stress else "実際の2022年"), nm, med, worst))
            print(rows[-1], flush=True)
    L = ["---\ntype: backtest\ntitle: 2022年の下げが2倍の深さだった場合\ncreated: 2026-10-11\nscript: tools/stress_2022.py（恩株ツールのブランチの backtest_onkabu_combined.run を使用）\n---\n",
         "# 2022年のハイテクの下げが2倍の深さだった場合（新分析ツールだけ／＋QQQ／＋恩株ツール）\n",
         __doc__.split("\n", 1)[1].strip() + "\n",
         "| 相場 | 形 | 2015年〜の年率 | 2022年の下げ（含み損込み、中央値／最悪） | 2022年の下げ（確定した損だけ、中央値／最悪） | 2021-11-19〜2022年末の資産の増減 | 期間全体の最大下落率（含み損込み・確定） |",
         "|---|---|---|---|---|---|---|"]
    for sc, nm, m, wst in rows:
        L.append(f"| {sc} | {nm} | {m[0]:.1%} | {m[3]:.0%}／{wst[0]:.0%} | {m[4]:.0%}／{wst[1]:.0%} | {m[5]:+.0%} | {m[1]:.0%}・{m[2]:.0%} |")
    L.append("\n- 実際の2022年: NASDAQ100（QQQ）は高値から約−35%。2倍の深さの試算ではQQQが約−60%前後になる。")
    L.append("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    open(sys.argv[1], "w", encoding="utf-8").write("\n".join(L) + "\n")

if __name__ == "__main__":
    main()
