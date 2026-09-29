#!/usr/bin/env python3
"""持っている銘柄に「出来高を伴った大きな陰線」が出たら売るバックテスト

使い方:
  tools/backtest_bear_exit.py run [--out FILE]

大きな陰線（引けで判定し、翌日の寄り付きで売る）:
  実体（始値−終値）がその銘柄のふだんの値幅（前日までのATR(14)）の k 倍以上、終値がその日の値幅の下25%以内（安値に近い）、
  出来高が前日までの50日平均の m 倍以上（m=0 は出来高を見ない）
売る対象: 全部の保有銘柄／利益が出ている銘柄だけ（その日の終値が買値より上）／順張りのルール（ミネルヴィニ・新高値V2）の銘柄だけ
今の採用ルール: 4つのルール、4銘柄・1銘柄25%、損切り15%、急落の底RSI(2)≦10、同じ業種2銘柄まで。
設計期間 2015〜2021年 / 確認期間 2022年〜。
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
SEEDS = range(10)
IS_END, OOS_START = cb.IS_END, cb.OOS_START


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/出来高を伴った大陰線で売る.md")
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

    def bear(s, j, k, m):
        o, h, l, c, v = s["o"][j], s["h"][j], s["l"][j], s["c"][j], s["v"][j]
        atr, v50 = s["atr"][j - 1], s["vol50"][j - 1]
        if atr is None or h <= l or o - c < k * atr or (c - l) / (h - l) > 0.25:
            return False
        return m == 0 or (v50 is not None and v >= m * v50)

    def sell_on(tr, k, m, target):
        out, diffs = [], []
        for t in tr:
            if target == "trend" and rule_of[id(t)] not in ("M", "V"):
                out.append(t)
                continue
            s, sym = data[t["sym"]], t["sym"]
            i0, i1 = idx(sym, t["in"]), idx(sym, t["out"])
            new = t
            for j in range(max(i0, 1), i1 - 1):
                if not bear(s, j, k, m):
                    continue
                if target == "profit" and s["c"][j] <= t["px"]:
                    continue
                new = {**t, "out": s["date"][j + 1], "ret": s["o"][j + 1] / t["px"] - 1, "why": "大陰線"}
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
    w("---\ntype: backtest\ntitle: 出来高を伴った大陰線で売る\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_bear_exit.py\n---\n")
    w("# 持っている銘柄に「出来高を伴った大きな陰線」が出たら売るバックテスト\n")
    w(__doc__.split("\n", 5)[5].strip() + "\n")
    w("年率・最大下落率は同じ日の候補の選び方をランダムにした10通りの中央値。片道0.1%。後知恵なしの監視銘柄（S&P500）。"
      "「売った件数」は全部の合図のうち大陰線で早めに売ることになった件数。「売らずに持った場合との差」は、その売買1回ごとの損益の差の平均"
      "（プラスなら早めに売った方が良かった）。\n")
    cur = evaluate(base)
    w("| 形 | 年率 | 最大下落率 | 設計期間 | 確認期間 | 2018 | 2020 | 2022 | 売った件数 | 売らずに持った場合との差（1回平均） | 両方の期間で上回ったか |")
    w("|---|---|---|---|---|---|---|---|---|---|---|")
    w(f"| 今のルール | {pct(cur['all'])} | {pct(cur['mdd'])} | {pct(cur['is'])} | {pct(cur['oos'])} | "
      f"{pct(cur['yr']['2018'], 0)} | {pct(cur['yr']['2020'], 0)} | {pct(cur['yr']['2022'], 0)} | | | |")
    tl = {"all": "全部", "profit": "利益が出ている銘柄だけ", "trend": "順張りの銘柄だけ"}
    rows = []
    for m in (1.5, 2.0, 0):
        for k in ((1.0, 1.5, 2.0) if m else (1.5,)):
            for target in ("all", "profit", "trend"):
                tr, diffs = sell_on(base, k, m, target)
                e = evaluate(tr)
                ok = e["is"] > cur["is"] and e["oos"] > cur["oos"]
                lab = f"実体 ATRの{k}倍・出来高{'を見ない' if m == 0 else f'{m}倍'}・{tl[target]}"
                rows.append((lab, e, ok))
                avg = sum(diffs) / len(diffs) if diffs else 0
                w(f"| {lab} | {pct(e['all'])} | {pct(e['mdd'])} | {pct(e['is'])} | {pct(e['oos'])} | "
                  f"{pct(e['yr']['2018'], 0)} | {pct(e['yr']['2020'], 0)} | {pct(e['yr']['2022'], 0)} | {len(diffs)} | {pct(avg, 2)} | {'はい' if ok else ''} |")
                print(lab, file=sys.stderr)
    ok = [x for x in rows if x[2]]
    w("\n## まとめ\n")
    w(f"- 設計期間・確認期間の両方で今のルール（設計 {pct(cur['is'])}、確認 {pct(cur['oos'])}）を上回った形: **{len(ok)}通り / {len(rows)}通り**")
    for lab, e, _ in ok:
        w(f"  - {lab}: 年率 {pct(e['all'])}、設計 {pct(e['is'])}、確認 {pct(e['oos'])}、最大下落率 {pct(e['mdd'])}")
    w("\n## 注意\n")
    w("- 大陰線の数値（ATRの倍数、安値からの位置25%、出来高の倍数）はClaudeが置いたもの。多くの形を試しているので、1つだけ良い形は偶然のことがある。")
    w("- 業種は今のYahooの分類を過去にも使っている。NASDAQ100は含めていない。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
