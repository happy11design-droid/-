#!/usr/bin/env python3
"""値動きの大きさに合わせて1銘柄の額を変える（値動きに合わせた建玉）バックテスト

使い方:
  tools/backtest_vol_sizing.py run [--out FILE]

今の採用ルール（4つのルール、同時に4銘柄、損切り15%、急落の底RSI(2)≦10、同じ業種2銘柄まで）の買いの合図・売りはそのままで、
1銘柄の額だけを変える。値動きの大きさ＝合図の日までの14日のATR÷株価（ATR%）。
  今のルール: どの銘柄も資金の25%
  逆数で配分: 額＝25% ×（基準のATR% ÷ その銘柄のATR%）。基準は全部の合図のATR%の中央値。上限・下限を付ける（10〜40%／12.5〜35%／15〜30%）
  値動きの大きい銘柄だけ減らす: 額＝25% ×（基準 ÷ ATR%）、ただし25%を超えない（下限10%）
  ルールごと: 押し目（ボリンジャーIII）だけ逆数で配分、ほかは25%
資金が足りないときは、ある分だけで買う。同時に持つのは4銘柄まで。片道0.1%。
選び方の乱数50通りの中央値。設計期間 2015〜2021年 / 確認期間 2022年〜。
"""
import argparse
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_combo2 as cb
from backtest_lib import COSTS, DEFAULT_CACHE, pct, portfolio
from backtest_regime import srt

COST = COSTS[2]
SLOTS = 4
SEEDS = range(50)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/値動きに合わせた建玉.md")
    a = ap.parse_args()
    ctx = cb.setup(a.cache)
    data, ind, days, parts = (ctx[k] for k in ("data", "ind", "days", "parts"))
    rule_of, base = {}, []
    for key, lst in (("B", parts[("B", 0.15)]), ("M", parts[("M", 0.15)]), ("C", parts[("C", 0.15, 10)]), ("V", parts[("V", 0.15)])):
        for t in lst:
            rule_of[id(t)] = key
        base += lst
    base = srt(base)
    pos = {}

    def idx(sym, d):
        if sym not in pos:
            pos[sym] = {x: k for k, x in enumerate(data[sym]["date"])}
        return pos[sym][d]

    atrp = {}
    for t in base:
        s = data[t["sym"]]
        i = idx(t["sym"], t["in"]) - 1
        h, l, c = s["h"], s["l"], s["c"]
        tr = [max(h[k] - l[k], abs(h[k] - c[k - 1]), abs(l[k] - c[k - 1])) for k in range(i - 13, i + 1)]
        atrp[id(t)] = sum(tr) / 14 / c[i]
    ref = sorted(atrp.values())[len(atrp) // 2]

    def sized(lo, hi, rules=("B", "C", "M", "V")):
        out = []
        for t in base:
            wgt = 0.25
            if rule_of[id(t)] in rules:
                wgt = min(hi, max(lo, 0.25 * ref / atrp[id(t)]))
            out.append({**t, "w": wgt})
        return out

    di = {d: k for k, d in enumerate(days)}
    is_hi = max(d for d in days if d <= cb.IS_END)
    oos_lo = min(d for d in days if d >= cb.OOS_START)
    span = lambda lo, hi: (dt.date.fromisoformat(hi) - dt.date.fromisoformat(lo)).days / 365.25
    years = sorted({d[:4] for d in days})

    def seg(c, lo, hi):
        return c[di[hi]] / (c[di[lo] - 1] if di[lo] > 0 else 1.0)

    def evaluate(tr):
        rs = []
        for k in SEEDS:
            p = portfolio(tr, COST, SLOTS, days, data, weight=0.25, seed=4000 + k, group_of=ind, group_cap=2)
            c = p["curve"]
            yr = {y: seg(c, min(d for d in days if d[:4] == y), max(d for d in days if d[:4] == y)) - 1 for y in years}
            rs.append({"all": p["cagr"], "mdd": p["mdd"], "is": seg(c, days[0], is_hi) ** (1 / span(days[0], is_hi)) - 1,
                       "oos": seg(c, oos_lo, days[-1]) ** (1 / span(oos_lo, days[-1])) - 1, "exp": p["exposure"],
                       "worst": p["worst_hit"], "yr": yr})
        m = lambda key: cb.med([x[key] for x in rs])
        return {"all": m("all"), "mdd": m("mdd"), "is": m("is"), "oos": m("oos"), "exp": m("exp"), "worst": m("worst"),
                "yr": {y: cb.med([x["yr"][y] for x in rs]) for y in years}}

    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: 値動きに合わせた建玉\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_vol_sizing.py\n---\n")
    w("# 値動きの大きさに合わせて1銘柄の額を変えるバックテスト\n")
    w(__doc__.split("\n", 5)[5].strip() + "\n")
    w(f"基準のATR%（全部の合図の中央値）: {pct(ref, 2)}。ATR%が基準の2倍の銘柄は額が半分、半分の銘柄は額が2倍（上限・下限の範囲で）。\n")
    w("| 形 | 年率 | 最大下落率 | 設計期間 | 確認期間 | 2018 | 2020 | 2022 | 平均の投資比率 | 1回の最大の損（資金比） | 両方の期間で上回ったか |")
    w("|---|---|---|---|---|---|---|---|---|---|---|")
    rows = [("今のルール（どの銘柄も25%）", base),
            ("逆数で配分（10〜40%）", sized(0.10, 0.40)),
            ("逆数で配分（12.5〜35%）", sized(0.125, 0.35)),
            ("逆数で配分（15〜30%）", sized(0.15, 0.30)),
            ("値動きの大きい銘柄だけ減らす（10〜25%）", sized(0.10, 0.25)),
            ("押し目だけ逆数で配分（10〜40%）、ほかは25%", sized(0.10, 0.40, ("B",))),
            ("押し目だけ、値動きの大きい銘柄を減らす（10〜25%）", sized(0.10, 0.25, ("B",)))]
    cur = None
    for lab, tr in rows:
        e = evaluate(tr)
        if cur is None:
            cur = e
        ok = e is not cur and e["is"] > cur["is"] and e["oos"] > cur["oos"]
        w(f"| {lab} | {pct(e['all'])} | {pct(e['mdd'])} | {pct(e['is'])} | {pct(e['oos'])} | "
          + " | ".join(pct(e["yr"][y], 0) for y in ("2018", "2020", "2022")) + f" | {pct(e['exp'], 0)} | {pct(e['worst'])} | {'はい' if ok else ''} |")
        print(lab, file=sys.stderr)
    w("\n## 注意\n")
    w("- 基準のATR%と上限・下限はClaudeが置いたもの。上限・下限を3通り変えて、同じ傾向かを見る。")
    w("- 値動きの小さい銘柄の額を増やすと、4銘柄の合計が資金を超えることがある。そのときは、ある資金の分だけで買う。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
