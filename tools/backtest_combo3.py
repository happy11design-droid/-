#!/usr/bin/env python3
"""ミネルヴィニを外す効果が偶然でないかの確認と、同じ日の候補の優先順位のバックテスト

使い方:
  tools/backtest_combo3.py run [--out FILE]

  1. ミネルヴィニを外す: 銘柄数 3〜7 × 損切り 15%・18% × 急落の底のRSI(2) 5以下・10以下 の20通りすべてで、外す前と後を比べる
  2. 年ごとの差: 4銘柄・5銘柄で、ミネルヴィニを外す前と後の年ごとの成績
  3. 同じ日に候補が重なったときの優先順位: ランダム（基本）、RSの高い順（今のツール）、ルールの順番を決める形
1銘柄の額は資金÷銘柄数。後知恵なしの監視銘柄。設計期間 2015〜2021年 / 確認期間 2022年〜。
"""
import argparse
import datetime as dt
import itertools
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_combo2 as cb
from backtest_lib import COSTS, DEFAULT_CACHE, pct, portfolio, stats

COST = COSTS[2]
IS_END, OOS_START = cb.IS_END, cb.OOS_START
SEEDS = range(10)
med = cb.med


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/ミネルヴィニを外す確認と優先順位.md")
    a = ap.parse_args()
    ctx = cb.setup(a.cache)
    data, ind, days, trades, parts = (ctx[k] for k in ("data", "ind", "days", "trades", "parts"))
    years = sorted({d[:4] for d in days})
    di = {d: k for k, d in enumerate(days)}
    is_hi = max(d for d in days if d <= IS_END)
    oos_lo = min(d for d in days if d >= OOS_START)
    span = lambda lo, hi: (dt.date.fromisoformat(hi) - dt.date.fromisoformat(lo)).days / 365.25

    def seg(c, lo, hi):
        return c[di[hi]] / (c[di[lo] - 1] if di[lo] > 0 else 1.0)

    def one(p):
        yr = {y: seg(p["curve"], min(d for d in days if d[:4] == y), max(d for d in days if d[:4] == y)) - 1 for y in years}
        return {"all": p["cagr"], "mdd": p["mdd"], "is": seg(p["curve"], days[0], is_hi) ** (1 / span(days[0], is_hi)) - 1,
                "oos": seg(p["curve"], oos_lo, days[-1]) ** (1 / span(oos_lo, days[-1])) - 1, "yr": yr}

    def summarize(rs):
        m = lambda k: med([x[k] for x in rs])
        return {"all": m("all"), "mdd": m("mdd"), "is": m("is"), "oos": m("oos"),
                "rng": (min(x["all"] for x in rs), max(x["all"] for x in rs)),
                "yr": {y: med([x["yr"][y] for x in rs]) for y in years}}

    def evaluate(tr, slots):
        return summarize([one(portfolio(tr, COST, slots, days, data, weight=1 / slots, seed=k, group_of=ind, group_cap=2)) for k in SEEDS])

    def evaluate_prio(tr, slots, prio):
        """prio(t) の小さい順。同じ値の中はランダム（seed ごと）。prio=None ならRSなどの rank の順（ツールと同じ）"""
        rs = []
        for k in SEEDS:
            rnd = random.Random(k)
            if prio is None:
                tt = tr
            else:
                tt = [{**t, "rank": (prio(t), rnd.random())} for t in tr]
            rs.append(one(portfolio(tt, COST, slots, days, data, weight=1 / slots, group_of=ind, group_cap=2)))
            if prio is None:
                break
        return summarize(rs)

    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: ミネルヴィニを外す確認と優先順位\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_combo3.py\n---\n")
    w("# ミネルヴィニを外す効果の確認と、同じ日の候補の優先順位\n")
    w(__doc__.split("\n", 5)[5].strip() + "\n")
    w("年率・最大下落率は、同じ日の候補の選び方をランダムにした10通りの中央値。片道0.1%。\n")

    # 1
    print("1", file=sys.stderr)
    w("\n## 1. ミネルヴィニを外す前と後（20通りすべて）\n")
    w("| 組み合わせ | 年率 2015年〜 前→後 | 設計期間 前→後 | 確認期間 前→後 | 最大下落率 前→後 | 両方の期間で良くなったか |")
    w("|---|---|---|---|---|---|")
    better = 0
    res = {}
    for n, stop, rsi in itertools.product((3, 4, 5, 6, 7), (0.15, 0.18), (5, 10)):
        e0 = evaluate(trades(stop, rsi), n)
        e1 = evaluate(trades(stop, rsi, drop=("M",)), n)
        res[(n, stop, rsi)] = (e0, e1)
        ok = e1["is"] > e0["is"] and e1["oos"] > e0["oos"]
        better += ok
        w(f"| {n}銘柄・損切り{int(stop * 100)}%・RSI(2)≦{rsi} | {pct(e0['all'])}→{pct(e1['all'])} | {pct(e0['is'])}→{pct(e1['is'])} | "
          f"{pct(e0['oos'])}→{pct(e1['oos'])} | {pct(e0['mdd'])}→{pct(e1['mdd'])} | {'はい' if ok else 'いいえ'} |")
    w(f"\n- 両方の期間で良くなった組み合わせ: **20通りのうち{better}通り**")
    for n in (3, 4, 5, 6, 7):
        ks = [k for k in res if k[0] == n]
        d_is = sum(res[k][1]["is"] - res[k][0]["is"] for k in ks) / len(ks)
        d_oos = sum(res[k][1]["oos"] - res[k][0]["oos"] for k in ks) / len(ks)
        w(f"- {n}銘柄の平均の差（外した後−前）: 設計期間 {d_is * 100:+.1f}ポイント、確認期間 {d_oos * 100:+.1f}ポイント")

    # ミネルヴィニ単独の年ごとの成績
    w("\n### ミネルヴィニの買いの合図の年ごとの成績（1トレード単位、損切り15%）\n")
    w("| 年 | 件数 | 勝率 | 1トレード平均 | PF |")
    w("|---|---|---|---|---|")
    mt = parts[("M", 0.15)]
    for y in years:
        st = stats([t for t in mt if t["in"][:4] == y], COST)
        if st:
            w(f"| {y} | {st['n']} | {pct(st['win'])} | {pct(st['mean'], 2)} | {st['pf']:.2f} |")
    for k, nm in (("B", "ボリンジャーIII"), ("V", "新高値V2")):
        st = stats(parts[(k, 0.15)], COST)
        w(f"\n（参考: {nm} 全期間 {st['n']}件、勝率 {pct(st['win'])}、1トレード平均 {pct(st['mean'], 2)}、PF {st['pf']:.2f}）")
    st = stats(parts[("C", 0.15, 5)], COST)
    w(f"（参考: 急落の底 全期間 {st['n']}件、勝率 {pct(st['win'])}、1トレード平均 {pct(st['mean'], 2)}、PF {st['pf']:.2f}）")
    st = stats(mt, COST)
    w(f"（参考: ミネルヴィニ 全期間 {st['n']}件、勝率 {pct(st['win'])}、1トレード平均 {pct(st['mean'], 2)}、PF {st['pf']:.2f}）\n")

    # 2
    print("2", file=sys.stderr)
    for n in (4, 5):
        e0, e1 = res[(n, 0.15, 10)]
        w(f"\n## 2. 年ごとの成績（{n}銘柄・損切り15%・RSI(2)≦10）\n")
        w("| | " + " | ".join(years) + " |")
        w("|---|" + "---|" * len(years))
        w("| 4つのルール | " + " | ".join(pct(e0["yr"][y], 0) for y in years) + " |")
        w("| ミネルヴィニを外す | " + " | ".join(pct(e1["yr"][y], 0) for y in years) + " |")
        up = sum(e1["yr"][y] > e0["yr"][y] for y in years)
        w(f"\n- 外した方が良かった年: {len(years)}年のうち{up}年")

    # 3
    print("3", file=sys.stderr)
    rule_of = {}
    for (k, *_), tr in parts.items():
        for t in tr:
            rule_of[id(t)] = k
    order_sets = [
        ("ランダム（基本）", "random"),
        ("RSなどの並べ替えの値の順（今のツールと同じ）", None),
        ("新高値V2 → 急落の底 → ボリンジャーIII → ミネルヴィニ", "VCBM"),
        ("急落の底 → 新高値V2 → ボリンジャーIII → ミネルヴィニ", "CVBM"),
        ("ボリンジャーIII → 急落の底 → 新高値V2 → ミネルヴィニ", "BCVM"),
        ("新高値V2 → ボリンジャーIII → 急落の底 → ミネルヴィニ", "VBCM"),
    ]
    for n, drop in ((4, ()), (5, ()), (4, ("M",)), (5, ("M",))):
        tr = trades(0.15, 10, drop=drop)
        lab = f"{n}銘柄・損切り15%・RSI(2)≦10" + ("・ミネルヴィニなし" if drop else "・4つのルール")
        w(f"\n## 3. 同じ日の候補の優先順位（{lab}）\n")
        w("| 優先順位 | 年率 2015年〜（幅） | 最大下落率 | 設計期間 | 確認期間 |")
        w("|---|---|---|---|---|")
        for olab, o in order_sets:
            if o == "random":
                e = evaluate(tr, n)
            elif o is None:
                e = evaluate_prio(tr, n, None)
            else:
                e = evaluate_prio(tr, n, lambda t, o=o: o.index(rule_of[id(t)]))
            w(f"| {olab} | {pct(e['all'])}（{pct(e['rng'][0])}〜{pct(e['rng'][1])}） | {pct(e['mdd'])} | {pct(e['is'])} | {pct(e['oos'])} |")

    w("\n## 注意\n")
    w("- 「RSなどの並べ替えの値の順」は1通りだけなので幅がない。ほかの優先順位は、同じルールの中の順をランダムにした10通りの中央値。")
    w("- 業種は今のYahooの分類を過去にも使っている。NASDAQ100は含めていない。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
