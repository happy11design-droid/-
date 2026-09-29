#!/usr/bin/env python3
"""相場の局面が「横ばい」のときの扱いを変えるバックテスト

使い方:
  tools/backtest_regime_filter.py run [--out FILE]

局面（引けで判定、S&P500またはNASDAQ100の30週線＝150日線）:
  上昇＝線より上かつ4週前より上向き／下落＝線より下かつ下向き／
  崩れ始め＝線より下だが線はまだ上向き／回復途中＝線より上だが線はまだ下向き（崩れ始めと回復途中を合わせて「横ばい」）
試す形（今の採用ルール: 4つのルール、4銘柄・1銘柄25%、損切り15%、急落の底RSI(2)≦10、同じ業種2銘柄まで）:
  ① 横ばいの日は新しく買わない
  ② 崩れ始めの日だけ新しく買わない（回復途中は買う）
  ③ 崩れ始めに変わった日に、持っている銘柄を翌日の寄り付きで売る（a 全部／b 含み損の銘柄だけ／c 順張りのルール（ミネルヴィニ・新高値V2）だけ）
  ④ ②と③aを合わせる
崩れ始めが何日か続いたときだけ判定する形（2日・5日続いたら）も試す（線の近くで判定が毎日入れ替わるのを避ける）。
設計期間 2015〜2021年 / 確認期間 2022年〜。
"""
import argparse
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_combo2 as cb
from backtest_lib import COSTS, DEFAULT_CACHE, load_prices, pct, portfolio, sma
from backtest_regime import srt

COST = COSTS[2]
SLOTS = 4
SEEDS = range(10)
IS_END, OOS_START = cb.IS_END, cb.OOS_START


def regimes(prices, confirm=1):
    """{日付: 上昇／下落／崩れ始め／回復途中}。confirm 日続いたときだけ局面を切り替える"""
    c, m = prices["c"], sma(prices["c"], 150)
    raw = {}
    for i, d in enumerate(prices["date"]):
        if m[i] is None or i < 20 or m[i - 20] is None:
            continue
        up, above = m[i] > m[i - 20], c[i] > m[i]
        raw[d] = "上昇" if above and up else "下落" if not above and not up else "崩れ始め" if up else "回復途中"
    out, cur, run, last = {}, None, 0, None
    for d in sorted(raw):
        r = raw[d]
        run = run + 1 if r == last else 1
        last = r
        if cur is None or run >= confirm:
            cur = r
        out[d] = cur
    return out


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/横ばいの相場の扱い.md")
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

    def sig_day(t):
        s = data[t["sym"]]
        return s["date"][idx(t["sym"], t["in"]) - 1]

    def no_buy(tr, reg, bad):
        return [t for t in tr if reg.get(sig_day(t)) not in bad]

    def sell_on(tr, reg, which="all"):
        out = []
        for t in tr:
            if which == "trend" and rule_of.get(id(t)) not in ("M", "V"):
                out.append(t)
                continue
            s, sym = data[t["sym"]], t["sym"]
            i0, i1 = idx(sym, t["in"]), idx(sym, t["out"])
            new = t
            for j in range(i0, i1 - 1):
                d, p = s["date"][j], s["date"][j - 1]
                if reg.get(d) == "崩れ始め" and reg.get(p) != "崩れ始め":
                    if which == "loss" and s["c"][j] >= t["px"]:
                        continue
                    new = {**t, "out": s["date"][j + 1], "ret": s["o"][j + 1] / t["px"] - 1, "why": "崩れ始め"}
                    break
            out.append(new)
        return srt(out)

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
                       "oos": seg(c, oos_lo, days[-1]) ** (1 / span(oos_lo, days[-1])) - 1, "yr": yr, "taken": p["taken"]})
        m = lambda key: cb.med([x[key] for x in rs])
        return {"all": m("all"), "mdd": m("mdd"), "is": m("is"), "oos": m("oos"), "taken": m("taken") / (len(days) / 252),
                "rng": (min(x["all"] for x in rs), max(x["all"] for x in rs)),
                "yr": {y: cb.med([x["yr"][y] for x in rs]) for y in years}}

    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: 横ばいの相場の扱い\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_regime_filter.py\n---\n")
    w("# 相場の局面が「横ばい」のときの扱いを変えるバックテスト\n")
    w(__doc__.split("\n", 5)[5].strip() + "\n")
    w("年率・最大下落率は同じ日の候補の選び方をランダムにした10通りの中央値（幅は最小〜最大）。片道0.1%。後知恵なしの監視銘柄（S&P500）。\n")
    head = "| 形 | 年率 2015年〜（幅） | 最大下落率 | 設計期間 | 確認期間 | 2018 | 2020 | 2022 | 2025 | 買った件数/年 |"
    sep = "|---|---|---|---|---|---|---|---|---|---|"
    rows = []

    def row(lab, tr):
        e = evaluate(tr)
        rows.append((lab, e))
        w(f"| {lab} | {pct(e['all'])}（{pct(e['rng'][0])}〜{pct(e['rng'][1])}） | {pct(e['mdd'])} | {pct(e['is'])} | {pct(e['oos'])} | "
          + " | ".join(pct(e["yr"][y], 0) for y in ("2018", "2020", "2022", "2025")) + f" | {e['taken']:.0f} |")
        print(lab, file=sys.stderr)

    spx_p, ndx_p = load_prices(a.cache, "^GSPC"), load_prices(a.cache, "^NDX")
    cur = None
    for name, pr in (("S&P500", spx_p), ("NASDAQ100", ndx_p)):
        for conf in (1, 2, 5):
            reg = regimes(pr, conf)
            n_turn = sum(1 for k, d in enumerate(days[1:], 1) if reg.get(d) == "崩れ始め" and reg.get(days[k - 1]) != "崩れ始め")
            share = {g: sum(reg.get(d) == g for d in days) / len(days) for g in ("上昇", "崩れ始め", "回復途中", "下落")}
            w(f"\n## {name}の局面（{conf}日続いたら切り替え）\n")
            w("日数の割合: " + "、".join(f"{g} {pct(v, 0)}" for g, v in share.items()) + f"。崩れ始めに変わった回数: {n_turn}回（{n_turn / (len(days) / 252):.1f}回/年）\n")
            w(head)
            w(sep)
            if cur is None:
                row("今のルール（局面で何も変えない）", base)
                cur = rows[-1][1]
            else:
                w(f"| 今のルール（局面で何も変えない） | {pct(cur['all'])} | {pct(cur['mdd'])} | {pct(cur['is'])} | {pct(cur['oos'])} | "
                  + " | ".join(pct(cur["yr"][y], 0) for y in ("2018", "2020", "2022", "2025")) + f" | {cur['taken']:.0f} |")
            row(f"① 横ばいの日は新しく買わない（{name}・{conf}日）", no_buy(base, reg, {"崩れ始め", "回復途中"}))
            row(f"② 崩れ始めの日だけ新しく買わない（{name}・{conf}日）", no_buy(base, reg, {"崩れ始め"}))
            row(f"③a 崩れ始めに変わったら全部売る（{name}・{conf}日）", sell_on(base, reg, "all"))
            row(f"③b 崩れ始めに変わったら含み損の銘柄だけ売る（{name}・{conf}日）", sell_on(base, reg, "loss"))
            row(f"③c 崩れ始めに変わったら順張りのルールの銘柄だけ売る（{name}・{conf}日）", sell_on(base, reg, "trend"))
            row(f"④ ②＋③a（{name}・{conf}日）", sell_on(no_buy(base, reg, {"崩れ始め"}), reg, "all"))

    ok = [(lab, e) for lab, e in rows[1:] if e["is"] > cur["is"] and e["oos"] > cur["oos"]]
    w("\n## まとめ\n")
    w(f"- 今のルール: 設計期間 {pct(cur['is'])}、確認期間 {pct(cur['oos'])}、最大下落率 {pct(cur['mdd'])}")
    w(f"- 設計期間・確認期間の両方で今のルールを上回った形: {len(ok)}通り / {len(rows) - 1}通り")
    for lab, e in sorted(ok, key=lambda x: -x[1]["is"]):
        w(f"  - {lab}: 設計 {pct(e['is'])}、確認 {pct(e['oos'])}、最大下落率 {pct(e['mdd'])}")
    w("\n## 注意\n")
    w("- 局面の判定（30週線＝150日線、4週前との比較）は毎朝のscan.mdと同じ考え方。数値はClaudeが置いたもの。")
    w("- 多くの形を試しているので、1つだけ良い形は偶然のことがある。S&P500とNASDAQ100、1日・2日・5日のどれでも同じ傾向かを見る。")
    w("- 業種は今のYahooの分類を過去にも使っている。NASDAQ100の構成銘柄は含めていない（局面の判定にだけNASDAQ100指数を使う）。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
