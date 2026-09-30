#!/usr/bin/env python3
"""早めに売るルール（陰線の連続・MACDのデッドクロス・浅い損切り・日数）のバックテスト

使い方:
  tools/backtest_early_exit.py run [--out FILE]

今のルールの手じまい（ボリンジャーIII＝上のバンド、急落の底＝5日線を上回る、ミネルヴィニ・新高値V2＝50日線割れ、全部＝損切り15%）に、
次の条件を足す（どれも引けで判定し、翌日の寄り付きで売る。買った日の足から数える）:
  陰線（終値＜始値）が2日・3日続く／その銘柄の日足MACD(12,26)がシグナル(9)を下に抜ける（デッドクロス）／
  終値が買値の7%・10%下（浅い損切り）／買ってから10日・20日たつ（日数での打ち切り）
当てる対象: 逆張りのルール（ボリンジャーIII・急落の底）／順張りのルール（ミネルヴィニ・新高値V2）／全部
今の採用ルール: 4つのルール、4銘柄・1銘柄25%、急落の底RSI(2)≦10、同じ業種2銘柄まで。設計期間 2015〜2021年 / 確認期間 2022年〜。
"""
import argparse
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_combo2 as cb
from backtest_lib import COSTS, DEFAULT_CACHE, pct, portfolio
from backtest_market_signal import ema
from backtest_regime import srt

COST = COSTS[2]
SLOTS = 4
SEEDS = range(10)
IS_END, OOS_START = cb.IS_END, cb.OOS_START


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/早めに売るルール.md")
    a = ap.parse_args()
    ctx = cb.setup(a.cache)
    data, ind, days, parts = (ctx[k] for k in ("data", "ind", "days", "parts"))
    for s in data.values():
        m = [x - y for x, y in zip(ema(s["c"], 12), ema(s["c"], 26))]
        s["macd"], s["macd_sig"] = m, ema(m, 9)
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

    def cond(kind, n):
        def f(s, j, i0, px):
            if kind == "bear":
                return j - n + 1 >= i0 and all(s["c"][k] < s["o"][k] for k in range(j - n + 1, j + 1))
            if kind == "macd":
                return j >= 35 and s["macd"][j] < s["macd_sig"][j] and s["macd"][j - 1] >= s["macd_sig"][j - 1]
            if kind == "stop":
                return s["c"][j] <= px * (1 - n)
            if kind == "time":
                return j - i0 + 1 >= n
            return False
        return f

    def apply(tr, f, rules):
        out, diffs = [], []
        for t in tr:
            if rule_of[id(t)] not in rules:
                out.append(t)
                continue
            s, sym = data[t["sym"]], t["sym"]
            i0, i1 = idx(sym, t["in"]), idx(sym, t["out"])
            new = t
            for j in range(i0, i1 - 1):
                if f(s, j, i0, t["px"]):
                    new = {**t, "out": s["date"][j + 1], "ret": s["o"][j + 1] / t["px"] - 1, "why": "早めの手じまい"}
                    diffs.append(new["ret"] - t["ret"])
                    break
            out.append(new)
        return srt(out), diffs

    di = {d: k for k, d in enumerate(days)}
    is_hi = max(d for d in days if d <= IS_END)
    oos_lo = min(d for d in days if d >= OOS_START)
    span = lambda lo, hi: (dt.date.fromisoformat(hi) - dt.date.fromisoformat(lo)).days / 365.25
    years = sorted({d[:4] for d in days})

    def seg(c, lo, hi):
        return c[di[hi]] / (c[di[lo] - 1] if di[lo] > 0 else 1.0)

    def evaluate(tr):
        rs = []
        for k in SEEDS:
            p = portfolio(tr, COST, SLOTS, days, data, weight=1 / SLOTS, seed=k, group_of=ind, group_cap=2)
            c = p["curve"]
            yr = {y: seg(c, min(d for d in days if d[:4] == y), max(d for d in days if d[:4] == y)) - 1 for y in years}
            rs.append({"all": p["cagr"], "mdd": p["mdd"], "is": seg(c, days[0], is_hi) ** (1 / span(days[0], is_hi)) - 1,
                       "oos": seg(c, oos_lo, days[-1]) ** (1 / span(oos_lo, days[-1])) - 1, "yr": yr})
        m = lambda key: cb.med([x[key] for x in rs])
        return {"all": m("all"), "mdd": m("mdd"), "is": m("is"), "oos": m("oos"),
                "yr": {y: cb.med([x["yr"][y] for x in rs]) for y in years}}

    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: 早めに売るルール\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_early_exit.py\n---\n")
    w("# 早めに売るルール（陰線の連続・MACDのデッドクロス・浅い損切り・日数）のバックテスト\n")
    w(__doc__.split("\n", 5)[5].strip() + "\n")
    w("年率・最大下落率は同じ日の候補の選び方をランダムにした10通りの中央値。片道0.1%。後知恵なしの監視銘柄（S&P500）。"
      "「早めに売った件数」は全部の合図のうち、足した条件で今のルールより早く売ることになった件数。「差」はその売買1回ごとの損益の差の平均（プラスなら早めに売った方が良かった）。\n")
    cur = evaluate(base)
    w("| 対象 | 足した売りの条件 | 年率 | 最大下落率 | 設計期間 | 確認期間 | 2018 | 2020 | 2022 | 早めに売った件数 | 差（1回平均） | 両方の期間で上回ったか |")
    w("|---|---|---|---|---|---|---|---|---|---|---|---|")
    w(f"| | 今のルール | {pct(cur['all'])} | {pct(cur['mdd'])} | {pct(cur['is'])} | {pct(cur['oos'])} | "
      f"{pct(cur['yr']['2018'], 0)} | {pct(cur['yr']['2020'], 0)} | {pct(cur['yr']['2022'], 0)} | | | |")
    REV, TREND, ALL = ("B", "C"), ("M", "V"), ("B", "C", "M", "V")
    tests = [
        ("逆張り（ボリンジャーIII・急落の底）", REV, "陰線が2日続く", cond("bear", 2)),
        ("逆張り（ボリンジャーIII・急落の底）", REV, "陰線が3日続く", cond("bear", 3)),
        ("逆張り（ボリンジャーIII・急落の底）", REV, "MACDのデッドクロス", cond("macd", 0)),
        ("逆張り（ボリンジャーIII・急落の底）", REV, "買値の7%下（終値）", cond("stop", 0.07)),
        ("逆張り（ボリンジャーIII・急落の底）", REV, "買値の10%下（終値）", cond("stop", 0.10)),
        ("逆張り（ボリンジャーIII・急落の底）", REV, "10日たったら", cond("time", 10)),
        ("逆張り（ボリンジャーIII・急落の底）", REV, "20日たったら", cond("time", 20)),
        ("ボリンジャーIIIだけ", ("B",), "陰線が3日続く", cond("bear", 3)),
        ("ボリンジャーIIIだけ", ("B",), "買値の10%下（終値）", cond("stop", 0.10)),
        ("順張り（ミネルヴィニ・新高値V2）", TREND, "MACDのデッドクロス", cond("macd", 0)),
        ("順張り（ミネルヴィニ・新高値V2）", TREND, "陰線が3日続く", cond("bear", 3)),
        ("順張り（ミネルヴィニ・新高値V2）", TREND, "買値の10%下（終値）", cond("stop", 0.10)),
        ("全部", ALL, "MACDのデッドクロス", cond("macd", 0)),
        ("全部", ALL, "陰線が3日続く", cond("bear", 3)),
    ]
    rows = []
    for tgt, rules, lab, f in tests:
        tr, diffs = apply(base, f, rules)
        e = evaluate(tr)
        ok = e["is"] > cur["is"] and e["oos"] > cur["oos"]
        rows.append((tgt, lab, e, ok))
        avg = sum(diffs) / len(diffs) if diffs else 0
        w(f"| {tgt} | {lab} | {pct(e['all'])} | {pct(e['mdd'])} | {pct(e['is'])} | {pct(e['oos'])} | "
          f"{pct(e['yr']['2018'], 0)} | {pct(e['yr']['2020'], 0)} | {pct(e['yr']['2022'], 0)} | {len(diffs)} | {pct(avg, 2)} | {'はい' if ok else ''} |")
        print(tgt, lab, file=sys.stderr)
    ok = [x for x in rows if x[3]]
    w("\n## まとめ\n")
    w(f"- 設計期間・確認期間の両方で今のルール（設計 {pct(cur['is'])}、確認 {pct(cur['oos'])}）を上回った形: **{len(ok)}通り / {len(rows)}通り**")
    for tgt, lab, e, _ in ok:
        w(f"  - {tgt}・{lab}: 年率 {pct(e['all'])}、設計 {pct(e['is'])}、確認 {pct(e['oos'])}、最大下落率 {pct(e['mdd'])}")
    w("\n## 注意\n")
    w("- 数値（陰線の日数、MACDの期間、損切りの幅、日数）は一般的な値で、Claudeが置いたもの。多くの形を試しているので、1つだけ良い形は偶然のことがある。")
    w("- 業種は今のYahooの分類を過去にも使っている。NASDAQ100は含めていない。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
