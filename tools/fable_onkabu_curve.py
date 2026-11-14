#!/usr/bin/env python3
"""恩株ツールだけの毎日の資金（税込み・待っている現金はQQQ）を書き出す（Fableの策6・組み合わせの土台、2026-11-14）

`tools/backtest_onkabu_combined.py` の run() をそのまま使う（今の実際の形: 1銘柄・資金4,500ドル・待っている現金はQQQ）。
- tax: 課税口座（今の形）。売って確定した損益を年ごとに通算して20.315%。2倍で約55.7%を売る
- nisa: NISA（策6）。税なし、2倍で50%を売る
NVDA あり・なしの両方。結果は ~/.cache/stock_backtest/results/fable_onkabu.json（あれば作り直さない。--force で作り直す）

使い方: BT_QQQ_TAX=1 BT_COST=0.00132 python3 tools/fable_onkabu_curve.py [--force]
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_onkabu_combined as C  # noqa: E402
import backtest_onkabu_search as bs_  # noqa: E402
import onkabu_lib as ol  # noqa: E402
from backtest_lib import DEFAULT_CACHE, load_prices  # noqa: E402

OUT = os.path.join(DEFAULT_CACHE, "results", "fable_onkabu.json")


def main():
    if os.path.exists(OUT) and "--force" not in sys.argv:
        print("既にある:", OUT)
        return
    members, spy, feats = bs_.load_all()
    sig = {"mom": ("r126", 1.0), "hi": "nh", "rev": 0.1, "extra": None}

    def sig_by_day(ex):
        out = {}
        for s, f in feats.items():
            if s in ex:
                continue
            m = ol.signal(f, sig) & f["member"]
            m[:260] = False
            for i in np.nonzero(m)[0]:
                out.setdefault(f["date"][i], []).append(s)
        return out

    q = load_prices(DEFAULT_CACHE, "QQQ")
    qqq = dict(zip(q["date"], q["c"]))
    days = [d for d in spy["date"] if d >= "2015-01-02"]
    res = {"days": days}
    for ex_name, ex in (("all", ()), ("noNVDA", ("NVDA",))):
        sb = sig_by_day(ex)
        for acct, tax, sell in (("tax", 0.20315, 1 / (2 - 0.20315)), ("nisa", 0.0, 0.5)):
            C.TAX, C.SELL_AT_2X = tax, sell
            curve, n_onk, _ = C.run(feats, [], {}, days, sb, mode="pool", use_new=False, cash_px=qqq, capital=4500.0,
                                    slots_d=1, dbl_frac=1.0, dedup=False, seed=0)
            res[f"{acct}_{ex_name}"] = curve
            res[f"log_{acct}_{ex_name}"] = [{k: (float(v) if not isinstance(v, str) else v) for k, v in x.items()} for x in C.STATS.get("log", [])]
            cg, mdd = C.metrics(curve, days)
            print(acct, ex_name, f"年率 {cg:.1%} 最大下落率 {mdd:.0%} 恩株 {n_onk}", dict(C.STATS), flush=True)
    json.dump(res, open(OUT, "w"))
    print("書き出し", OUT)


if __name__ == "__main__":
    main()
