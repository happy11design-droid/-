#!/usr/bin/env python3
"""`backtest_exit_signals.py` で両方の期間で上回った形（MACDの弱気ダイバージェンス・かぶせ線・宵の明星）が、
数値を少し変えても同じ傾向かを確かめる（当てはめすぎの確認）

使い方:
  tools/backtest_exit_signals2.py run [--out FILE]

  MACDの弱気ダイバージェンス: 価格が直前 N 日（15・20・30）の最高値、MACDが直前 N 日の最高値の r 倍（0.7・0.8・0.9）未満、MACD>0
  かぶせ線: 前日の陽線の実体の中心より下で引ける（今の定義）／実体の 1/3・2/3 より下で引ける
  組み合わせ: MACDの弱気ダイバージェンス・かぶせ線・宵の明星のどれかが出たら売る
当てる対象は順張り（ミネルヴィニ・新高値V2）と全部。設計期間 2015〜2021年 / 確認期間 2022年〜。
"""
import argparse
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_combo2 as cb
import backtest_exit_signals as xs
from backtest_lib import COSTS, DEFAULT_CACHE, pct, portfolio
from backtest_regime import srt

COST = COSTS[2]
SLOTS = 4
SEEDS = range(10)


def macd_div(n, r):
    def f(s, j):
        m, c = s["macd"], s["c"]
        return j >= n + 20 and c[j] >= max(c[j - n:j]) and m[j] < max(m[j - n:j]) * r and m[j] > 0
    return f


def dark_cloud(frac):
    def f(s, j):
        o, h, c = s["o"], s["h"], s["c"]
        return (xs.after_up(s, j - 1) and c[j - 1] > o[j - 1] and o[j] > h[j - 1]
                and c[j] < o[j - 1] + (c[j - 1] - o[j - 1]) * frac and c[j] > o[j - 1])
    return f


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/チャートの形と指標で売る_数値の確認.md")
    a = ap.parse_args()
    ctx = cb.setup(a.cache)
    data, ind, days, parts = (ctx[k] for k in ("data", "ind", "days", "parts"))
    rule_of, base = {}, []
    for key, lst in (("B", parts[("B", 0.15)]), ("M", parts[("M", 0.15)]), ("C", parts[("C", 0.15, 10)]), ("V", parts[("V", 0.15)])):
        for t in lst:
            rule_of[id(t)] = key
        base += lst
    base = srt(base)
    for sym in {t["sym"] for t in base}:
        xs.prep(data[sym])
    pos = {}

    def idx(sym, d):
        if sym not in pos:
            pos[sym] = {x: k for k, x in enumerate(data[sym]["date"])}
        return pos[sym][d]

    def apply(f, rules):
        out, diffs = [], []
        for t in base:
            if rule_of[id(t)] not in rules:
                out.append(t)
                continue
            s, sym = data[t["sym"]], t["sym"]
            i0, i1 = idx(sym, t["in"]), idx(sym, t["out"])
            new = t
            for j in range(max(i0, 2), i1 - 1):
                try:
                    hit = f(s, j)
                except (TypeError, ValueError):
                    hit = False
                if hit:
                    new = {**t, "out": s["date"][j + 1], "ret": s["o"][j + 1] / t["px"] - 1}
                    diffs.append(new["ret"] - t["ret"])
                    break
            out.append(new)
        return srt(out), diffs

    di = {d: k for k, d in enumerate(days)}
    is_hi = max(d for d in days if d <= cb.IS_END)
    oos_lo = min(d for d in days if d >= cb.OOS_START)
    span = lambda lo, hi: (dt.date.fromisoformat(hi) - dt.date.fromisoformat(lo)).days / 365.25

    def seg(c, lo, hi):
        return c[di[hi]] / (c[di[lo] - 1] if di[lo] > 0 else 1.0)

    def evaluate(tr):
        rs = []
        for k in SEEDS:
            p = portfolio(tr, COST, SLOTS, days, data, weight=1 / SLOTS, seed=k, group_of=ind, group_cap=2)
            c = p["curve"]
            rs.append({"all": p["cagr"], "mdd": p["mdd"], "is": seg(c, days[0], is_hi) ** (1 / span(days[0], is_hi)) - 1,
                       "oos": seg(c, oos_lo, days[-1]) ** (1 / span(oos_lo, days[-1])) - 1})
        m = lambda key: cb.med([x[key] for x in rs])
        return {"all": m("all"), "mdd": m("mdd"), "is": m("is"), "oos": m("oos")}

    cur = evaluate(base)
    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: チャートの形と指標で売る_数値の確認\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_exit_signals2.py\n---\n")
    w("# 上回った形の数値を変えても同じ傾向かの確認\n")
    w(__doc__.split("\n", 5)[5].strip() + "\n")
    w(f"今のルール: 年率 {pct(cur['all'])}、最大下落率 {pct(cur['mdd'])}、設計期間 {pct(cur['is'])}、確認期間 {pct(cur['oos'])}\n")
    w("| 形 | 対象 | 年率 | 最大下落率 | 設計期間 | 確認期間 | 早めに売った件数 | 差（1回平均） | 両方の期間で上回ったか |")
    w("|---|---|---|---|---|---|---|---|---|")
    tests = []
    for n in (15, 20, 30):
        for rr in (0.7, 0.8, 0.9):
            tests.append((f"MACDの弱気ダイバージェンス（{n}日・{rr}倍）", macd_div(n, rr)))
    for fr, lab in ((0.5, "中心"), (1 / 3, "下1/3"), (2 / 3, "上1/3")):
        tests.append((f"かぶせ線（前日の実体の{lab}より下で引ける）", dark_cloud(fr)))
    combo = lambda s, j: macd_div(20, 0.8)(s, j) or xs.dark_cloud(s, j) or xs.evening_star(s, j)
    tests.append(("組み合わせ（MACDの弱気ダイバージェンス・かぶせ線・宵の明星のどれか）", combo))
    n_ok = 0
    for lab, f in tests:
        for gl, rules in (("順張りだけ", ("M", "V")), ("全部", ("B", "C", "M", "V"))):
            tr, diffs = apply(f, rules)
            e = evaluate(tr)
            ok = e["is"] > cur["is"] and e["oos"] > cur["oos"]
            n_ok += ok
            avg = sum(diffs) / len(diffs) if diffs else 0
            w(f"| {lab} | {gl} | {pct(e['all'])} | {pct(e['mdd'])} | {pct(e['is'])} | {pct(e['oos'])} | {len(diffs)} | {pct(avg, 2)} | {'はい' if ok else ''} |")
            print(lab, gl, file=sys.stderr)
    w(f"\n- 両方の期間で上回った形: {n_ok}通り / {len(tests) * 2}通り")
    w("\n## 注意\n")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
