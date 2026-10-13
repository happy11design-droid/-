#!/usr/bin/env python3
"""恩株ツールの調査7: 対象をS&P500の外（今の時価総額20億ドル以上の米国株）に広げたときの合図⑦・⑧

使い方:
  tools/theme_universe.py fetch --cache ~/.cache/stock_backtest_wide --min-cap 2e9   # 銘柄一覧と日足
  tools/backtest_onkabu_wide.py fund  [--wide DIR]       # 合図⑦が一度でも出た銘柄の売上（SEC）を取る
  tools/backtest_onkabu_wide.py event [--wide DIR]       # 合図ごとの「1年以内に2倍」の割合（S&P500だけの場合と比べる）
  tools/backtest_onkabu_wide.py pf --start 2015-01-01 [--exclude NVDA] [--seeds 15]

注意（大きな偏り）: 対象は「今も上場していて、今の時価総額が20億ドル以上」の銘柄。途中で上場廃止・暴落して小さくなった銘柄は入らない。
S&P500の過去の構成銘柄で調べた結果より、良く見えやすい。
その日の売買代金（50日平均）が2,000万ドル以上・株価5ドル以上の銘柄だけを合図の対象にする（その時点で分かる値）。
"""
import argparse
import datetime as dt
import json
import os
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backtest_lib import DEFAULT_CACHE, load_prices, load_members, is_member, sma
import backtest_onkabu_portfolio as bp
import backtest_onkabu_fast as bfast
import backtest_onkabu_fast_variants as bv
import backtest_onkabu_features as bf

WIDE = os.path.expanduser("~/.cache/stock_backtest_wide")
MIN_DV = 20e6
MIN_PX = 5.0


def load_wide(wide, exclude=()):
    uni = json.load(open(os.path.join(wide, "universe.json")))
    data = {}
    for s in uni:
        if s in exclude:
            continue
        d = load_prices(wide, s)
        if d and len(d["c"]) > 300:
            d["dv50"] = sma([c * v for c, v in zip(d["c"], d["v"])], 50)
            data[s] = d
    return uni, data


def liquid(d, i):
    return d["dv50"][i] is not None and d["dv50"][i] >= MIN_DV and d["c"][i] >= MIN_PX


def cmd_fund(a):
    uni, data = load_wide(a.wide)
    pre = {s: {"hi": bfast.rolling_max(d["c"], 252)} for s, d in data.items()}
    hit = set()
    for s, d in data.items():
        c = d["c"]
        for i in range(126, len(c)):
            if c[i] / c[i - 126] >= 2 and c[i] >= pre[s]["hi"][i] * 0.999 and liquid(d, i):
                hit.add(s)
                break
    todo = [s for s in sorted(hit) if not os.path.exists(os.path.join(DEFAULT_CACHE, "onkabu_fund", s + ".json"))]
    print(f"合図⑦が出た銘柄 {len(hit)}、売上を新しく取る {len(todo)}", flush=True)
    bf.cmd_fetch(argparse.Namespace(cache=DEFAULT_CACHE), syms=todo)


def cmd_event(a):
    """毎週、流動性のある銘柄について合図を数え、1年以内に2倍になった割合を出す"""
    members = load_members(DEFAULT_CACHE)
    uni, data = load_wide(a.wide)
    pre = bv.prep(data, DEFAULT_CACHE)
    spy = load_prices(DEFAULT_CACHE, "SPY")
    weeks = []
    for k, d in enumerate(spy["date"]):
        if d >= "2014-06-01" and (k + 1 == len(spy["date"]) or dt.date.fromisoformat(spy["date"][k + 1]).isocalendar()[1] != dt.date.fromisoformat(d).isocalendar()[1]):
            weeks.append(d)
    sigs = {"⑦ 6カ月で+100%・52週高値": bv.make_signal(data, pre, 126, 1.0), "⑧ ⑦＋売上≧20%": bv.make_signal(data, pre, 126, 1.0, rev_min=0.2)}
    pos = {s: {d: k for k, d in enumerate(v["date"])} for s, v in data.items()}
    res = {}
    for d in weeks:
        for s, v in data.items():
            i = pos[s].get(d)
            if i is None or i < 260 or not liquid(v, i):
                continue
            c = v["c"]
            if i + 252 >= len(c):
                continue
            inside = s in members and is_member(members[s], d)
            dbl = any(x >= 2 * c[i] for x in c[i + 1:i + 253])
            for g in ("全体（合図なし）",) + tuple(k for k, f in sigs.items() if f(s, i)):
                for scope in ("S&P500の中", "S&P500の外"):
                    if (scope == "S&P500の中") == inside:
                        r = res.setdefault((g, scope), [0, 0, set()])
                        r[0] += 1
                        r[1] += dbl
                        r[2].add(s)
    print("| 合図 | 範囲 | 件数（銘柄数） | 1年以内に2倍 |\n|---|---|---|---|")
    for (g, scope), (n, k, ss) in sorted(res.items()):
        print(f"| {g} | {scope} | {n:,}（{len(ss)}） | {k / n:.1%} |")


def cmd_pf(a):
    uni, data = load_wide(a.wide, exclude=a.exclude.split(","))
    members = load_members(DEFAULT_CACHE)
    spy = load_prices(DEFAULT_CACHE, "SPY")
    pre = bv.prep(data, DEFAULT_CACHE)
    days = [d for d in spy["date"] if d >= a.start]
    k0 = spy["date"].index(days[0])
    spy_end, spy_cagr, spy_mdd = bp.metrics([spy["c"][spy["date"].index(d)] / spy["c"][k0] * bp.CAPITAL for d in days], days)
    print(f"<!-- 条件: {a.start}〜 除く:{a.exclude or 'なし'} SPY 年率{spy_cagr:.1%} -->")
    sp_only = {}
    for d in days:
        if d[:7] not in sp_only:
            sp_only[d[:7]] = [s for s, sp in members.items() if s in data and is_member(sp, d)]
    everyone = {m: list(data) for m in sp_only}
    for label, look, up, rv in (("⑦", 126, 1.0, None), ("⑧", 126, 1.0, 0.2)):
        base = bv.make_signal(data, pre, look, up, rev_min=rv)
        sig = lambda s, i, base=base: liquid(data[s], i) and base(s, i)
        for scope, cbm in (("S&P500の中だけ（今も上場している銘柄）", sp_only), ("時価総額20億ドル以上の米国株", everyone)):
            res = []
            for seed in range(a.seeds):
                curve, trades, n_onk, onk, act, cs = bp.simulate(data, spy, days, cbm, sig, None, 252, seed)
                e, c, m = bp.metrics(curve, days)
                res.append((e, c, m, n_onk, cs))
            med = lambda k: st.median(r[k] for r in res)
            print(f"ROW\t{label}\t{scope}\t{med(1):.1%}\t{med(2):.1%}\t{med(3):.0f}\t{med(4):.0%}\t{sum(r[0] > spy_end for r in res)}/{a.seeds}\t{spy_cagr:.1%}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("fund", "event", "pf"))
    ap.add_argument("--wide", default=WIDE)
    ap.add_argument("--start", default="2015-01-01")
    ap.add_argument("--exclude", default="")
    ap.add_argument("--seeds", type=int, default=15)
    a = ap.parse_args()
    {"fund": cmd_fund, "event": cmd_event, "pf": cmd_pf}[a.cmd](a)


if __name__ == "__main__":
    main()
