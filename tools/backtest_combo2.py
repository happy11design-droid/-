#!/usr/bin/env python3
"""銘柄数・損切り・急落の底のRSI(2)の組み合わせと、ルールを外した場合のバックテスト

使い方:
  tools/backtest_combo2.py run [--out FILE]

資金ルール（1トレードのリスク2%）をやめ、同時に持つ銘柄数で1銘柄の額を決める（資金÷銘柄数）。
  1. 組み合わせ: 銘柄数 4・5・6・7 × 損切り 15%・18% × 急落の底のRSI(2) 5以下・10以下
  2. 外す確認: 銘柄数4・5で、4つの買いのルールを1つずつ外す／業種の上限を外す・1銘柄にする
  3. 同じ日の候補の選び方: ランダム順（表の基本）と、ツールと同じRSの高い順
当てはめすぎの確認: 設計期間（2015〜2021年）で選び、確認期間（2022年〜）で確かめる。
ずらしながらの確認（2018年から毎年、前の年までで一番良かった組み合わせを使う）も出す。
"""
import argparse
import datetime as dt
import itertools
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_compare2 as c2
import backtest_crash as bcr
import backtest_figures2 as f2
import backtest_minervini2 as bm2
import backtest_modern as bmo
import backtest_rotation as br
import backtest_swing as bs
import backtest_trend as bt
from backtest_lib import COSTS, DEFAULT_CACHE, gen_trades, load_prices, load_universe, pct, portfolio, sma
from backtest_regime import srt

COST = COSTS[2]
START, IS_END, OOS_START, WF_FROM = "2015-01-02", "2021-12-31", "2022-01-01", "2018"
SEEDS = range(10)
CAPITAL = 18000


def med(xs):
    xs = sorted(xs)
    return xs[len(xs) // 2]


def setup(cache, with_parts=True):
    a = argparse.Namespace(cache=cache)
    members, data = load_universe(a.cache, min_bars=260)
    g = load_prices(a.cache, "^GSPC")
    f2.SPX.update(zip(g["date"], g["c"]))
    for sym, d in data.items():
        c2.prep(d)
        bmo.prep(d, f2.SPX)
        f2.prep(d)
        for n in (5, 50):
            d[f"ma{n}"] = d.get(f"ma{n}") or sma(d["c"], n)
        d["sym"] = sym
    bt.add_rs_rank(data, members)
    u = json.load(open(os.path.join(a.cache, "universe.json")))
    ex = os.path.join(a.cache, "industry_extra.json")
    if os.path.exists(ex):
        u.update(json.load(open(ex)))
    ind = {s: (u.get(s) or {}).get("industry") for s in data}
    spy = load_prices(a.cache, "SPY")
    end = dt.date.today().isoformat()
    days = [d for d in spy["date"] if START <= d <= end]
    fridays = [d for k, d in enumerate(days) if k + 1 == len(days) or dt.date.fromisoformat(days[k + 1]).isocalendar()[1] != dt.date.fromisoformat(d).isocalendar()[1]]
    lists = br.build_lists(data, members, fridays, ind)
    sets = {f: set(l) for f, l in lists.items()}
    pos = {s: {d: k for k, d in enumerate(v["date"])} for s, v in data.items()}
    ranks = {f: {s: k + 1 for k, (_, s) in enumerate(sorted(((data[s]["rs"][pos[s][f]] or 0, s) for s in l if f in pos[s]), reverse=True))}
             for f, l in lists.items()}
    week_of, fi, last = {}, 0, None
    for d in days:
        while fi < len(fridays) and fridays[fi] < d:
            last = fridays[fi]
            fi += 1
        week_of[d] = last
    ok_rot = lambda s, i, sp: bt.liquid(s, i, sp) and week_of.get(s["date"][i]) is not None and s["sym"] in sets[week_of[s["date"][i]]]
    ok10 = lambda s, i, sp: (bt.liquid(s, i, sp) and week_of.get(s["date"][i]) is not None
                             and ranks[week_of[s["date"][i]]].get(s["sym"], 10 ** 9) <= 10)
    below50 = lambda j, s, k, px: s["ma50"][j] is not None and s["c"][j] < s["ma50"][j]
    above5 = lambda j, s, k, px: s["ma5"][j] is not None and s["c"][j] > s["ma5"][j]
    v2o = bmo.with_(c2.V2, f2.O)

    def CR(rsi):
        def f(i, s):
            rr, r2 = bcr.drop(i, s), s["rsi2"][i]
            return rr if rr <= -0.15 and r2 is not None and r2 <= rsi and bcr.was_strong(i, s) else None
        return f

    def B3(stop):
        old, bs.STOP_MAX = bs.STOP_MAX, stop
        try:
            return bs.simulate(data, members, bs.O_method3, bs.X_upper_band, START, end, ok=ok_rot)
        finally:
            bs.STOP_MAX = old

    G = lambda e, x, ok, stop, mh=500: gen_trades(data, members, e, x, START, end, ok=ok, fill="open", max_hold=mh, stop_pct=stop)
    parts = {}
    for stop in ((0.15, 0.18) if with_parts else ()):
        parts[("B", stop)] = B3(stop)
        parts[("M", stop)] = G(bm2.E_base(2.0), below50, ok_rot, stop)
        parts[("V", stop)] = G(v2o, below50, ok10, stop)
        for rsi in (5, 10):
            parts[("C", stop, rsi)] = G(CR(rsi), above5, ok_rot, stop, 60)

    def trades(stop, rsi, drop=()):
        tr = []
        for k in ("B", "M", "V"):
            if k not in drop:
                tr += parts[(k, stop)]
        if "C" not in drop:
            tr += parts[("C", stop, rsi)]
        return srt(tr)

    return dict(members=members, data=data, ind=ind, days=days, parts=parts, trades=trades, ok_rot=ok_rot, G=G, end=end,
                ok10=ok10, CR=CR, v2o=v2o, below50=below50, above5=above5)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/銘柄数と損切りの組み合わせ.md")
    a = ap.parse_args()
    ctx = setup(a.cache)
    members, data, ind, days, trades = (ctx[k] for k in ("members", "data", "ind", "days", "trades"))
    years = sorted({d[:4] for d in days})
    di = {d: k for k, d in enumerate(days)}
    is_hi = max(d for d in days if d <= IS_END)
    oos_lo = min(d for d in days if d >= OOS_START)
    span = lambda lo, hi: (dt.date.fromisoformat(hi) - dt.date.fromisoformat(lo)).days / 365.25

    def seg(c, lo_d, hi_d):
        a0 = c[di[lo_d] - 1] if di[lo_d] > 0 else 1.0
        return c[di[hi_d]] / a0

    def one(p):
        yr = {}
        for y in years:
            lo, hi = min(d for d in days if d[:4] == y), max(d for d in days if d[:4] == y)
            yr[y] = seg(p["curve"], lo, hi) - 1
        return {"all": p["cagr"], "mdd": p["mdd"], "is": seg(p["curve"], days[0], is_hi) ** (1 / span(days[0], is_hi)) - 1,
                "oos": seg(p["curve"], oos_lo, days[-1]) ** (1 / span(oos_lo, days[-1])) - 1, "yr": yr,
                "taken": p["taken"], "worst": p["worst_hit"]}

    def evaluate(tr, slots, weight=None, cap=2):
        weight = weight or 1 / slots
        kw = dict(group_of=ind, group_cap=cap) if cap else {}
        rs = [one(portfolio(tr, COST, slots, days, data, weight=weight, seed=k, **kw)) for k in SEEDS]
        rk = one(portfolio(tr, COST, slots, days, data, weight=weight, **kw))
        m = lambda key: med([x[key] for x in rs])
        return {"all": m("all"), "rng": (min(x["all"] for x in rs), max(x["all"] for x in rs)), "mdd": m("mdd"),
                "is": m("is"), "oos": m("oos"), "yr": {y: med([x["yr"][y] for x in rs]) for y in years},
                "taken": m("taken"), "worst": m("worst"), "rank": rk, "slots": slots, "weight": weight}

    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: 銘柄数と損切りの組み合わせ\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_combo2.py\n---\n")
    w("# 銘柄数・損切り・急落の底のRSI(2)の組み合わせと、ルールを外した場合\n")
    w(__doc__.split("\n", 5)[5].strip() + "\n")
    w("年率・最大下落率は同じ日の候補の選び方をランダムにした10通りの中央値（幅は最小〜最大）。片道0.1%。後知恵なしの監視銘柄（S&P500）。"
      f"金額は資金{CAPITAL:,}ドルで始めた場合。\n")
    head = ("| 条件 | 年率 2015年〜（幅） | 最大下落率（金額） | 設計期間 | 確認期間 | 最悪の年 | RSの高い順 年率 / 最大下落率 | 買った件数/年 | "
            "1回の最大の損（資金比） | 1銘柄の額 |")
    sep = "|---|---|---|---|---|---|---|---|---|---|"

    def row(lab, e):
        wy = min(years, key=lambda y: e["yr"][y])
        n = len(days) / 252
        return (f"| {lab} | {pct(e['all'])}（{pct(e['rng'][0])}〜{pct(e['rng'][1])}） | {pct(e['mdd'])}（約{e['mdd'] * CAPITAL:,.0f}ドル） | "
                f"{pct(e['is'])} | {pct(e['oos'])} | {wy}年 {pct(e['yr'][wy], 0)} | {pct(e['rank']['all'])} / {pct(e['rank']['mdd'])} | "
                f"{e['taken'] / n:.0f} | {pct(e['worst'])} | 約{e['weight'] * CAPITAL:,.0f}ドル |")

    # 1. 組み合わせ
    print("1. 組み合わせ", file=sys.stderr)
    cur = evaluate(trades(0.15, 5), 7, 0.02 / 0.15)
    grid = {}
    for n, stop, rsi in itertools.product((4, 5, 6, 7), (0.15, 0.18), (5, 10)):
        grid[(n, stop, rsi)] = evaluate(trades(stop, rsi), n)
    lab = lambda k: f"{k[0]}銘柄・損切り{int(k[1] * 100)}%・RSI(2)≦{k[2]}"
    w("\n## 1. 組み合わせ（16通り）\n")
    w(head)
    w(sep)
    w(row("**今のルール（7銘柄・1銘柄13.3%・損切り15%・RSI(2)≦5）**", cur))
    for k, e in grid.items():
        w(row(lab(k), e))

    best = max(grid, key=lambda k: grid[k]["is"])
    by_oos = sorted(grid, key=lambda k: -grid[k]["oos"])
    rk_is = sorted(grid, key=lambda k: -grid[k]["is"])
    w(f"\n- 設計期間で一番良い組み合わせ: **{lab(best)}**（設計 {pct(grid[best]['is'])} / 確認 {pct(grid[best]['oos'])}。"
      f"今のルールは 設計 {pct(cur['is'])} / 確認 {pct(cur['oos'])}）")
    w(f"- 設計期間の順位で上位の組み合わせが確認期間でも上位か: 設計期間の上位5 = "
      + "、".join(f"{lab(k)}（確認期間 {by_oos.index(k) + 1}位）" for k in rk_is[:5]))

    def best_before(y, keys):
        def sc(k):
            p = 1.0
            for yy in years:
                if yy < y:
                    p *= 1 + grid[k]["yr"][yy]
            return p
        return max(keys, key=sc)

    def chain(pick):
        eq = 1.0
        for y in years:
            if y >= WF_FROM:
                eq *= 1 + pick(y)["yr"][y]
        return eq ** (1 / span(f"{WF_FROM}-01-01", days[-1])) - 1

    keys = list(grid)
    picks = {y: best_before(y, keys) for y in years if y >= WF_FROM}
    w(f"- ずらしながらの確認（2018年から毎年、前の年までで一番良い組み合わせを使う）: 年率 {pct(chain(lambda y: grid[picks[y]]))}。"
      f"今のルールに固定すると {pct(chain(lambda y: cur))}、設計期間で一番良い組み合わせに固定すると {pct(chain(lambda y: grid[best]))}。")
    w("  - 選ばれた組み合わせ: " + "、".join(f"{y}年 {lab(k)}" for y, k in picks.items()))

    # 各数値の効果（ほかの数値の全組み合わせで平均）
    w("\n### 各数値の効果（ほかの数値のすべての組み合わせでの平均）\n")
    w("| 数値 | 値 | 設計期間 | 確認期間 | 最大下落率 |")
    w("|---|---|---|---|---|")
    avg = lambda ks, key: sum(grid[k][key] for k in ks) / len(ks)
    for name, idx, vals, fmt in (("銘柄数", 0, (4, 5, 6, 7), lambda v: f"{v}銘柄"), ("損切り", 1, (0.15, 0.18), lambda v: f"{int(v * 100)}%"),
                                 ("RSI(2)の上限", 2, (5, 10), lambda v: f"{v}")):
        for v in vals:
            ks = [k for k in grid if k[idx] == v]
            w(f"| {name} | {fmt(v)} | {pct(avg(ks, 'is'))} | {pct(avg(ks, 'oos'))} | {pct(avg(ks, 'mdd'))} |")

    # 2. 外す確認
    print("2. 外す確認", file=sys.stderr)
    names = {"B": "ボリンジャーIII", "M": "ミネルヴィニ", "C": "急落の底", "V": "新高値V2"}
    for n in (4, 5):
        stop, rsi = 0.18, 10
        w(f"\n## 2. ルールを外す確認（{n}銘柄・損切り18%・RSI(2)≦10 を基準に）\n")
        w(head)
        w(sep)
        basee = evaluate(trades(stop, rsi), n)
        w(row(f"基準（{n}銘柄・4つのルール・業種2銘柄まで）", basee))
        for k, nm in names.items():
            w(row(f"{nm}を外す", evaluate(trades(stop, rsi, drop=(k,)), n)))
        for k1, k2 in (("B", "M"), ("B", "C"), ("M", "C")):
            w(row(f"{names[k1]}と{names[k2]}を外す", evaluate(trades(stop, rsi, drop=(k1, k2)), n)))
        w(row("業種の上限を外す", evaluate(trades(stop, rsi), n, cap=None)))
        w(row("同じ業種は1銘柄まで", evaluate(trades(stop, rsi), n, cap=1)))

    w("\n## 注意\n")
    w("- 組み合わせを多く試すほど、偶然良かったものを選ぶ危険が増える。設計期間で選んだものが確認期間でも良いか、ずらしながらの確認で今のルールより良いかで判断する。")
    w("- 1銘柄の額は資金÷銘柄数（全額を使う）。今のルールだけは1銘柄13.3%×7銘柄。")
    w("- 損切りは引け値で判定（ボリンジャーIIIだけは日中の安値）。株数の端数は考えていない（1株の値段が高い銘柄は、18,000ドルでは額が少しずれる）。")
    w("- 業種は今のYahooの分類を過去にも使っている。NASDAQ100は含めていない。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
