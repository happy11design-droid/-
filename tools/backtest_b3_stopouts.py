#!/usr/bin/env python3
"""押し目（ボリンジャーIII）が15%の損切りになりやすい売買の共通点を探し、それを避ける条件を確かめるバックテスト

使い方:
  tools/backtest_b3_stopouts.py run [--out FILE]

1. 押し目の買いの合図（後知恵なしの監視銘柄、2015年〜）を、合図の日の特徴で分け、15%の損切りになった割合・1回の平均を比べる。
   特徴: RS、200日線からの距離、50日線と200日線の並び、直前20日・5日の下げの大きさ、%b、21日II%、市場全体（S&P500）の局面、
   セクター、値動きの大きさ（ATR÷株価）、合図の日の出来高、合図の日の窓開け、続けて下げた日数
2. 設計期間（2015〜2021年）で「1回の平均が一番悪く、損切りの割合が高い」特徴（件数50以上）を上から3つ選び、
   その合図を見送る形を、4銘柄の枠の資金の推移（選び方の乱数50通りの中央値）で設計期間・確認期間（2022年〜）に分けて確かめる。
今の採用ルール: 4つのルール、4銘柄・1銘柄25%、損切り15%、急落の底RSI(2)≦10、同じ業種2銘柄まで。
"""
import argparse
import collections
import datetime as dt
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_combo2 as cb
from backtest_lib import COSTS, DEFAULT_CACHE, load_prices, pct, portfolio
from backtest_regime import srt
from backtest_regime_filter import regimes

COST = COSTS[2]
SLOTS = 4
SEEDS = range(50)


def bucket(x, edges, labels):
    if x is None:
        return "不明"
    for e, lb in zip(edges, labels):
        if x < e:
            return lb
    return labels[-1]


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/押し目の損切りの共通点.md")
    a = ap.parse_args()
    ctx = cb.setup(a.cache)
    data, ind, days, parts = (ctx[k] for k in ("data", "ind", "days", "parts"))
    rule_of, base = {}, []
    for key, lst in (("B", parts[("B", 0.15)]), ("M", parts[("M", 0.15)]), ("C", parts[("C", 0.15, 10)]), ("V", parts[("V", 0.15)])):
        for t in lst:
            rule_of[id(t)] = key
        base += lst
    base = srt(base)
    u = json.load(open(os.path.join(a.cache, "universe.json")))
    ex = os.path.join(a.cache, "industry_extra.json")
    if os.path.exists(ex):
        u.update(json.load(open(ex)))
    sec = {s: (u.get(s) or {}).get("sector") or "不明" for s in data}
    reg = regimes(load_prices(a.cache, "^GSPC"), 1)
    pos = {}

    def idx(sym, d):
        if sym not in pos:
            pos[sym] = {x: k for k, x in enumerate(data[sym]["date"])}
        return pos[sym][d]

    def feats(t):
        s = data[t["sym"]]
        i = idx(t["sym"], t["in"]) - 1
        c, o, h, l = s["c"], s["o"], s["h"], s["l"]
        m50, m200 = s["ma50"][i], s["ma200"][i]
        tr = [max(h[k] - l[k], abs(h[k] - c[k - 1]), abs(l[k] - c[k - 1])) for k in range(i - 13, i + 1)]
        atrp = sum(tr) / 14 / c[i]
        v50 = s["vol50"][i]
        down = 0
        while down < 15 and c[i - down] < c[i - down - 1]:
            down += 1
        return {
            "RS": bucket(s["rs"][i], (50, 70, 80, 90), ("50未満", "50〜70", "70〜80", "80〜90", "90以上")),
            "200日線からの距離": bucket(None if m200 is None else c[i] / m200 - 1, (-0.10, 0, 0.10, 0.25), ("−10%より下", "−10〜0%", "0〜+10%", "+10〜25%", "+25%より上")),
            "50日線と200日線": "不明" if m50 is None or m200 is None else ("50日線＞200日線" if m50 > m200 else "50日線＜200日線"),
            "直前20日の高値からの下げ": bucket(c[i] / max(c[i - 20:i]) - 1, (-0.25, -0.15, -0.08), ("−25%より大きい", "−15〜−25%", "−8〜−15%", "−8%より小さい")),
            "直前5日の下げ": bucket(c[i] / c[i - 5] - 1, (-0.15, -0.08, -0.03), ("−15%より大きい", "−8〜−15%", "−3〜−8%", "−3%より小さい")),
            "%b": bucket(s["pctb"][i], (-0.2, 0, 0.05), ("−0.2より下", "−0.2〜0", "0〜0.05", "0.05以上")),
            "21日II%": bucket(s["ii21"][i], (0.05, 0.15), ("0〜0.05", "0.05〜0.15", "0.15以上")),
            "市場全体（S&P500）の局面": reg.get(s["date"][i], "不明"),
            "セクター": sec.get(t["sym"], "不明"),
            "値動きの大きさ（ATR÷株価）": bucket(atrp, (0.02, 0.03, 0.045), ("2%未満", "2〜3%", "3〜4.5%", "4.5%以上")),
            "合図の日の出来高": bucket(None if not v50 else s["v"][i] / v50, (0.8, 1.5, 2.5), ("0.8倍未満", "0.8〜1.5倍", "1.5〜2.5倍", "2.5倍以上")),
            "合図の日の窓開け": "窓を開けて下げた" if o[i] < l[i - 1] else "窓なし",
            "続けて下げた日数": bucket(down, (2, 4, 6), ("0〜1日", "2〜3日", "4〜5日", "6日以上")),
        }

    b3 = [t for t in base if rule_of[id(t)] == "B"]
    F = {id(t): feats(t) for t in b3}

    def st(ts):
        if not ts:
            return None
        rets = [t["ret"] - 2 * COST for t in ts]
        stop = sum(1 for t in ts if t["why"] == "損切り") / len(ts)
        win = [x for x in rets if x > 0]
        loss = [-x for x in rets if x <= 0]
        return {"n": len(ts), "stop": stop, "avg": sum(rets) / len(rets), "pf": sum(win) / sum(loss) if loss else 9.99}

    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: 押し目の損切りの共通点\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_b3_stopouts.py\n---\n")
    w("# 押し目（ボリンジャーIII）が15%の損切りになりやすい売買の共通点\n")
    w(__doc__.split("\n", 5)[5].strip() + "\n")
    des = [t for t in b3 if t["in"] <= cb.IS_END]
    oos = [t for t in b3 if t["in"] >= cb.OOS_START]
    s0, s1 = st(des), st(oos)
    w(f"押し目の全部の合図: 設計期間 {s0['n']}件（損切り {pct(s0['stop'], 0)}、1回平均 {pct(s0['avg'], 2)}）、"
      f"確認期間 {s1['n']}件（損切り {pct(s1['stop'], 0)}、1回平均 {pct(s1['avg'], 2)}）\n")
    cands = []
    for fk in F[id(b3[0])]:
        w(f"\n## {fk}\n")
        w("| 区分 | 設計期間 件数 | 損切りの割合 | 1回平均 | PF | 確認期間 件数 | 損切りの割合 | 1回平均 | PF |")
        w("|---|---|---|---|---|---|---|---|---|")
        groups = collections.defaultdict(list)
        for t in b3:
            groups[F[id(t)][fk]].append(t)
        for gv in sorted(groups):
            d_ = st([t for t in groups[gv] if t["in"] <= cb.IS_END])
            o_ = st([t for t in groups[gv] if t["in"] >= cb.OOS_START])
            cell = lambda x: f"{x['n']} | {pct(x['stop'], 0)} | {pct(x['avg'], 2)} | {x['pf']:.2f}" if x else "0 | | | "
            w(f"| {gv} | {cell(d_)} | {cell(o_)} |")
            if d_ and d_["n"] >= 50:
                cands.append((fk, gv, d_))
    # 設計期間で一番悪い特徴（1回平均が低い順、損切りの割合が全体より高いもの）
    bad = sorted([c for c in cands if c[2]["stop"] > s0["stop"] and c[2]["avg"] < s0["avg"]], key=lambda c: c[2]["avg"])[:3]
    w("\n## 2. 設計期間で一番悪かった特徴の合図を見送る\n")
    w("設計期間で選んだ特徴（1回平均が低く、損切りの割合が全体より高い。件数50以上）: "
      + "、".join(f"{fk}が「{gv}」（1回平均 {pct(d['avg'], 2)}、損切り {pct(d['stop'], 0)}、{d['n']}件）" for fk, gv, d in bad) + "\n")

    di = {d: k for k, d in enumerate(days)}
    is_hi = max(d for d in days if d <= cb.IS_END)
    oos_lo = min(d for d in days if d >= cb.OOS_START)
    span = lambda lo, hi: (dt.date.fromisoformat(hi) - dt.date.fromisoformat(lo)).days / 365.25

    def seg(c, lo, hi):
        return c[di[hi]] / (c[di[lo] - 1] if di[lo] > 0 else 1.0)

    def evaluate(tr):
        rs = []
        for k in SEEDS:
            p = portfolio(tr, COST, SLOTS, days, data, weight=1 / SLOTS, seed=3000 + k, group_of=ind, group_cap=2)
            c = p["curve"]
            rs.append((p["cagr"], p["mdd"], seg(c, days[0], is_hi) ** (1 / span(days[0], is_hi)) - 1,
                       seg(c, oos_lo, days[-1]) ** (1 / span(oos_lo, days[-1])) - 1))
        return [cb.med([x[k] for x in rs]) for k in range(4)]

    w("| 形 | 年率 | 最大下落率 | 設計期間 | 確認期間 | 両方の期間で上回ったか |")
    w("|---|---|---|---|---|---|")
    cur = evaluate(base)
    w(f"| 今のルール | {pct(cur[0])} | {pct(cur[1])} | {pct(cur[2])} | {pct(cur[3])} | |")
    tests = [([b], f"{b[0]}が「{b[1]}」を見送る") for b in bad]
    if len(bad) > 1:
        tests.append((bad, "3つのどれかに当たる合図を見送る"))
    for conds, lab in tests:
        tr = [t for t in base if not (rule_of[id(t)] == "B" and any(F[id(t)][fk] == gv for fk, gv, _ in conds))]
        e = evaluate(tr)
        ok = e[2] > cur[2] and e[3] > cur[3]
        w(f"| {lab} | {pct(e[0])} | {pct(e[1])} | {pct(e[2])} | {pct(e[3])} | {'はい' if ok else ''} |")
        print(lab, file=sys.stderr)
    w("\n## 注意\n")
    w("- 特徴の区切り（RS 50・70・80・90、200日線から±10%など）はClaudeが置いたもの。")
    w("- 決算発表をまたいだかは、過去の決算日のデータがないため調べていない。")
    w("- 年率は選び方の乱数を50通り変えた中央値（ほかの表の10通りとは値が少し違う）。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
