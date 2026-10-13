#!/usr/bin/env python3
"""恩株ツールの調査6: 合図⑦・⑧の数字をずらしたときと、待っている現金の置き場所を変えたときの成績

使い方:
  tools/backtest_onkabu_fast_variants.py params --start 2015-01-01 [--exclude NVDA] [--seeds 15]
  tools/backtest_onkabu_fast_variants.py cash   --start 2015-01-01 [--exclude NVDA] [--seeds 15]
売買の決まりは backtest_onkabu_fast_pf.py と同じ（資金6,000ドル・4枠・翌日の寄り付きで買う・2倍で55.7%売って恩株・1年で2倍にならなければ売る）。
出力は表の行だけ（Markdown）。4通りの条件を並べてまとめるのは呼び出す側。
"""
import argparse
import bisect
import datetime as dt
import json
import os
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backtest_lib import DEFAULT_CACHE, load_prices, load_members, is_member
import backtest_onkabu_portfolio as bp
import backtest_onkabu_fast as bfast


def prep(data, cache):
    pre = {}
    for s, v in data.items():
        p = os.path.join(cache, "onkabu_fund", s + ".json")
        rows = [tuple(r) for r in json.load(open(p)).get("rev", [])] if os.path.exists(p) else []
        rs = bfast.rev_series(rows)
        pre[s] = {"hi": bfast.rolling_max(v["c"], 252), "rd": [x[0] for x in rs], "rv": [x[1] for x in rs]}
    return pre


def make_signal(data, pre, look, up, near_hi=0.999, rev_min=None):
    """look 取引日で +up 以上上がり、終値が52週高値の near_hi 倍以上。rev_min があれば売上の前年同期比もその値以上"""
    def rev(s, i):
        P = pre[s]
        d = data[s]["date"][i]
        j = bisect.bisect_right(P["rd"], d) - 1
        if j < 0 or (dt.date.fromisoformat(d) - dt.date.fromisoformat(P["rd"][j])).days > 120:
            return None
        return P["rv"][j]

    def fn(s, i):
        c = data[s]["c"]
        if i < look or c[i] / c[i - look] - 1 < up or c[i] < pre[s]["hi"][i] * near_hi:
            return False
        return rev_min is None or (rev(s, i) or -9) >= rev_min
    return fn


PARAMS = [
    ("⑦ 6カ月で+100%・52週高値（基準）", 126, 1.0, 0.999, None),
    ("6カ月で+80%・52週高値", 126, 0.8, 0.999, None),
    ("6カ月で+120%・52週高値", 126, 1.2, 0.999, None),
    ("6カ月で+100%・52週高値の95%以上", 126, 1.0, 0.95, None),
    ("3カ月で+60%・52週高値", 63, 0.6, 0.999, None),
    ("3カ月で+80%・52週高値", 63, 0.8, 0.999, None),
    ("9カ月で+100%・52週高値", 189, 1.0, 0.999, None),
    ("9カ月で+150%・52週高値", 189, 1.5, 0.999, None),
    ("⑧ 6カ月で+100%・52週高値・売上≧20%（基準）", 126, 1.0, 0.999, 0.2),
    ("6カ月で+80%・52週高値・売上≧20%", 126, 0.8, 0.999, 0.2),
    ("6カ月で+120%・52週高値・売上≧20%", 126, 1.2, 0.999, 0.2),
    ("6カ月で+100%・52週高値・売上≧10%", 126, 1.0, 0.999, 0.1),
    ("6カ月で+100%・52週高値・売上≧40%", 126, 1.0, 0.999, 0.4),
]

CASH = [("現金のまま（0%）", None), ("短期国債ETF（BIL）", "BIL"), ("S&P500（SPY）", "SPY"), ("NASDAQ100（QQQ）", "QQQ")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("params", "cash"))
    ap.add_argument("--cache", default=DEFAULT_CACHE)
    ap.add_argument("--start", default="2015-01-01")
    ap.add_argument("--exclude", default="")
    ap.add_argument("--seeds", type=int, default=15)
    a = ap.parse_args()
    members = load_members(a.cache)
    spy = load_prices(a.cache, "SPY")
    data = {s: d for s in members if s not in a.exclude.split(",") and (d := load_prices(a.cache, s)) and len(d["c"]) > 300}
    days = [d for d in spy["date"] if d >= a.start]
    cbm = {}
    for d in days:
        if d[:7] not in cbm:
            cbm[d[:7]] = [s for s, sp in members.items() if s in data and is_member(sp, d)]
    pre = prep(data, a.cache)
    k0 = spy["date"].index(days[0])
    spy_end, spy_cagr, spy_mdd = bp.metrics([spy["c"][spy["date"].index(d)] / spy["c"][k0] * bp.CAPITAL for d in days], days)
    print(f"<!-- 条件: {a.start}〜 除く:{a.exclude or 'なし'} SPY 年率{spy_cagr:.1%} 最大下落率{spy_mdd:.1%} -->")
    runs = []
    if a.mode == "params":
        for label, look, up, nh, rv in PARAMS:
            runs.append((label, make_signal(data, pre, look, up, nh, rv), None))
    else:
        for base, rv in (("⑦", None), ("⑧", 0.2)):
            sig = make_signal(data, pre, 126, 1.0, 0.999, rv)
            for cl, sym in CASH:
                px = None
                if sym:
                    d = load_prices(a.cache, sym)
                    px = dict(zip(d["date"], d["c"]))
                runs.append((f"{base}・{cl}", sig, px))
    for label, sig, px in runs:
        res = []
        for seed in range(a.seeds):
            curve, trades, n_onk, onk, act, cs = bp.simulate(data, spy, days, cbm, sig, None, 252, seed, cash_px=px)
            e, c, m = bp.metrics(curve, days)
            res.append((e, c, m, n_onk, cs))
        med = lambda k: st.median(r[k] for r in res)
        print(f"ROW\t{label}\t{med(1):.1%}\t{med(2):.1%}\t{med(3):.0f}\t{med(4):.0%}\t{sum(r[0] > spy_end for r in res)}/{a.seeds}\t{spy_cagr:.1%}", flush=True)


if __name__ == "__main__":
    main()
