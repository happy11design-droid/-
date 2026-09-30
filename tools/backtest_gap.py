#!/usr/bin/env python3
"""窓を開けた日（3%以上）に買うルールのバックテスト（`今後3〜5日の上げ下げの確率.md` の続き）

使い方:
  tools/backtest_gap.py run [--out FILE]

形（数値はClaudeが置いたもの。結果を見る前に決めた）:
  共通: 引け後に判定し、翌日の寄り付きで買う。5日たったら翌日の寄り付きで売る（3日の形もある）。損切りは買値の15%下（引けで判定）
  G1 下の窓: 寄り付きが前日の終値の−3%以下
  G2 下の窓＋VIX≧20: G1 で、その日のVIXの終値が20以上（市場が荒れている）
  G3 下の窓＋市場が30週線の下: G1 で、S&P500（SPY）の終値が30週線（150日線）より下
  G4 上の窓＋出来高2倍: 寄り付きが前日の終値の+3%以上、出来高が50日平均の2倍以上（決算などの材料）
  G5 窓＋点数の上位30%: 上か下に3%以上の窓の日で、`swing_odds.py` の点数（5日・翌寄り→引け、全部）が、
     設計期間（2015〜2021年）の窓の日の点数の上位30%に入る
  G6 G5 を3日で売る
今の採用ルール: 4つのルール、4銘柄・1銘柄25%、損切り15%、急落の底RSI(2)≦10、同じ業種2銘柄まで。
後知恵なしの監視銘柄（S&P500）。設計期間 2015〜2021年 / 確認期間 2022年〜。
点数（G5・G6）の作り方は2015〜2021年のS&P500だけで決めたもの（`tools/swing_odds_model.json`）。
"""
import argparse
import datetime as dt
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_combo2 as cb
import swing_odds as so
from backtest_lib import COSTS, DEFAULT_CACHE, gen_trades, load_prices, pct, portfolio, sma, stats
from backtest_regime import srt
from daily_odds import market_feats, to_design
from earnings_history import load_earnings

COST = COSTS[2]
SLOTS = 4
SEEDS = range(10)
STOP = 0.15
IS_END, OOS_START = cb.IS_END, cb.OOS_START
GAP = 0.03
SCORE_GAP = 0.02   # 点数は2%以上の窓の日に付ける（両隣の値の確認で2%の窓も試すため）


def add_scores(data, cache):
    """窓の日だけ、swing_odds の点数（5日・翌寄り→引け、全部）を s["gscore"][i] に入れる"""
    model = json.load(open(so.MODEL))
    lm = model["labels"]["oc5"]["全部"]
    edges = [np.array(e) for e in model["edges"]]
    wts = np.array(lm["w"])
    spy, vix = load_prices(cache, "SPY"), load_prices(cache, "^VIX")
    mk = market_feats(spy, vix)
    m150 = sma(spy["c"], 150)
    for i, d in enumerate(spy["date"]):
        if d in mk and m150[i]:
            mk[d] = mk[d] + (spy["c"][i] / m150[i] - 1,)
    spy_c = dict(zip(spy["date"], spy["c"]))
    earn = load_earnings(cache)
    K = so.KEYS
    for n_done, (sym, s) in enumerate(data.items()):
        n = len(s["c"])
        s["gscore"] = [None] * n
        gaps = [i for i in range(261, n) if abs(s["o"][i] / s["c"][i - 1] - 1) >= SCORE_GAP]
        if not gaps:
            continue
        f = so.stock_features(s, spy_c, earn.get(sym))
        for i in gaps:
            m = mk.get(s["date"][i])
            if not m or len(m) < 5:
                continue
            x = [f[k][i] if k in f else None for k in K]
            x[K.index("spy_rsi")], x[K.index("spy_r1")], x[K.index("vix")], x[K.index("spy_ma")] = m[0], m[1], m[2], m[4]
            if any(v is None or not np.isfinite(v) for v in x):
                continue
            s["gscore"][i] = float(to_design(np.array([x], float), edges)[0][lm["cols"]] @ wts)
        if n_done % 100 == 0:
            print("点数", n_done, file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/窓を開けた日に買うルール.md")
    a = ap.parse_args()
    ctx = cb.setup(a.cache)
    data, members, ind, days, parts, end, ok_rot = (ctx[k] for k in ("data", "members", "ind", "days", "parts", "end", "ok_rot"))
    base = srt(parts[("B", 0.15)] + parts[("M", 0.15)] + parts[("C", 0.15, 10)] + parts[("V", 0.15)])
    print("採用ルールの準備", file=sys.stderr)
    add_scores(data, a.cache)

    vix = dict(zip(*(lambda v: (v["date"], v["c"]))(load_prices(a.cache, "^VIX"))))
    spy = load_prices(a.cache, "SPY")
    m150 = sma(spy["c"], 150)
    spy_below = {d: m150[i] is not None and spy["c"][i] < m150[i] for i, d in enumerate(spy["date"])}
    # G5 の境目: 設計期間の窓の日（監視銘柄に限らず S&P500 全体）の点数の70パーセンタイル
    def cut_of(g, q):
        sc = [s["gscore"][i] for s in data.values() for i in range(261, len(s["c"]))
              if s["gscore"][i] is not None and s["date"][i] <= IS_END and abs(s["o"][i] / s["c"][i - 1] - 1) >= g]
        return float(np.percentile(sc, q))
    cut70 = cut_of(GAP, 70)

    gap = lambda i, s: s["o"][i] / s["c"][i - 1] - 1
    rank = lambda i, s: -(s["rs"][i] or 0)

    def E(cond):
        def f(i, s):
            return rank(i, s) if cond(i, s) else None
        return f

    G1 = E(lambda i, s: gap(i, s) <= -GAP)
    G2 = E(lambda i, s: gap(i, s) <= -GAP and vix.get(s["date"][i], 0) >= 20)
    G3 = E(lambda i, s: gap(i, s) <= -GAP and spy_below.get(s["date"][i], False))
    G4 = E(lambda i, s: gap(i, s) >= GAP and s["vol50"][i] and s["v"][i] >= 2 * s["vol50"][i])
    G5 = E(lambda i, s: s["gscore"][i] is not None and s["gscore"][i] >= cut70)
    after = lambda n: (lambda j, s, k, px: k >= n)
    rules = {
        "G1 下の窓": (G1, after(5)),
        "G2 下の窓＋VIX≧20": (G2, after(5)),
        "G3 下の窓＋市場が30週線の下": (G3, after(5)),
        "G4 上の窓＋出来高2倍": (G4, after(5)),
        "G5 窓＋点数の上位30%（5日）": (G5, after(5)),
        "G6 窓＋点数の上位30%（3日）": (G5, after(3)),
    }
    liquid_ok = lambda s, i, sp: cb.bt.liquid(s, i, sp)
    tr_w = {k: gen_trades(data, members, e, x, cb.START, end, ok=ok_rot, fill="open", max_hold=30, stop_pct=STOP) for k, (e, x) in rules.items()}
    tr_all = {k: gen_trades(data, members, e, x, cb.START, end, ok=liquid_ok, fill="open", max_hold=30, stop_pct=STOP) for k, (e, x) in rules.items()}
    print("売買の再現", file=sys.stderr)

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
    w("---\ntype: backtest\ntitle: 窓を開けた日に買うルール\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_gap.py\n---\n")
    w("# 窓を開けた日（3%以上）に買うルールのバックテスト\n")
    w(__doc__.split("\n", 4)[4].strip() + "\n")
    w("年率・最大下落率は同じ日の候補の選び方をランダムにした10通りの中央値。片道0.1%。1回平均は全部の合図の1回ごとの損益（コスト込み）。"
      f"G5・G6の点数の境目は {cut70:.3f}（設計期間の窓の日の70パーセンタイル）。\n")

    yrs = len(days) / 252

    def single(title, trs):
        w(f"\n## {title}\n")
        w("| 形 | 件数/年 | 勝率 | 1回平均 | PF | 設計 / 確認 1回平均 | 設計 / 確認 勝率 | 買った日の数（確認） |")
        w("|---|---|---|---|---|---|---|---|")
        for k, t in trs.items():
            st = stats(t, COST)
            if not st:
                w(f"| {k} | 0 | — | — | — | — | — | — |")
                continue
            h1 = stats([x for x in t if x["in"] <= IS_END], COST)
            h2 = stats([x for x in t if x["in"] >= OOS_START], COST)
            nd = len({x["in"] for x in t if x["in"] >= OOS_START})
            w(f"| {k} | {st['n'] / yrs:.0f} | {pct(st['win'])} | {pct(st['mean'], 2)} | {st['pf']:.2f} | "
              f"{pct(h1['mean'], 2) if h1 else '—'} / {pct(h2['mean'], 2) if h2 else '—'} | "
              f"{pct(h1['win']) if h1 else '—'} / {pct(h2['win']) if h2 else '—'} | {nd} |")

    single("1. 単独・1回ごと（後知恵なしの監視銘柄）", tr_w)
    single("2. 単独・1回ごと（参考: S&P500全体。株価5ドル以上・出来高25万株以上）", tr_all)

    cur = evaluate(base)
    w("\n## 3. 今の採用ルールとの組み合わせ（4銘柄の枠を共有）\n")
    w("| 形 | 年率 | 最大下落率 | 設計期間 | 確認期間 | 2018 | 2020 | 2022 | 2024 | 2025 | 両方の期間で上回ったか |")
    w("|---|---|---|---|---|---|---|---|---|---|---|")
    oks = []

    def line(lab, e, cmp=True):
        ok = cmp and e["is"] > cur["is"] and e["oos"] > cur["oos"]
        w(f"| {lab} | {pct(e['all'])} | {pct(e['mdd'])} | {pct(e['is'])} | {pct(e['oos'])} | "
          + " | ".join(pct(e["yr"].get(y, float('nan')), 0) for y in ("2018", "2020", "2022", "2024", "2025")) + f" | {'はい' if ok else ''} |")
        print(lab, file=sys.stderr)
        return ok

    line("今のルール", cur, False)
    for k, t in tr_w.items():
        if line(f"今のルール＋{k}", evaluate(srt(base + t))):
            oks.append(k)
    # 4. G5 の両隣の値（窓の大きさ・点数の境目・窓の向き）
    def G5v(g, q, side=0):
        c = cut_of(g, q)
        def f(i, s):
            x = gap(i, s)
            if abs(x) < g or (side > 0 and x < 0) or (side < 0 and x > 0):
                return None
            return rank(i, s) if s["gscore"][i] is not None and s["gscore"][i] >= c else None
        return f
    variants = {
        "窓2%・上位30%": G5v(0.02, 70), "窓4%・上位30%": G5v(0.04, 70),
        "窓3%・上位20%": G5v(0.03, 80), "窓3%・上位40%": G5v(0.03, 60),
        "窓3%・上位30%・上の窓だけ": G5v(0.03, 70, 1), "窓3%・上位30%・下の窓だけ": G5v(0.03, 70, -1),
    }
    tr_v = {k: gen_trades(data, members, e, after(5), cb.START, end, ok=ok_rot, fill="open", max_hold=30, stop_pct=STOP)
            for k, e in variants.items()}
    single("4. G5 の両隣の値（単独・1回ごと、後知恵なしの監視銘柄、5日）", tr_v)
    w("\n組み合わせ（4銘柄の枠を共有）:\n")
    w("| 形 | 年率 | 最大下落率 | 設計期間 | 確認期間 | 2018 | 2020 | 2022 | 2024 | 2025 | 両方の期間で上回ったか |")
    w("|---|---|---|---|---|---|---|---|---|---|---|")
    line("今のルール", cur, False)
    nv = 0
    for k, t in tr_v.items():
        nv += line(f"今のルール＋G5（{k}）", evaluate(srt(base + t)))
    w(f"\n両隣の値6通りのうち、両方の期間で今のルールを上回ったのは {nv}通り。")
    w("\n## まとめ\n")
    w(f"- 今のルール: 設計 {pct(cur['is'])}、確認 {pct(cur['oos'])}、最大下落率 {pct(cur['mdd'])}")
    w(f"- 設計期間・確認期間の両方で今のルールを上回った形: {len(oks)}通り" + (f"（{'、'.join(oks)}）" if oks else ""))
    w("\n## 注意\n")
    w("- 窓の大きさ（3%）・VIX 20・保有日数（3日・5日）・点数の上位30%はClaudeが置いたもの。結果を見る前に決めた。")
    w("- 損切り・手じまいは引けで判定し、翌日の寄り付きで売る（採用ルールと同じ）。")
    w("- 業種は今のYahooの分類を過去にも使っている。NASDAQ100は含めていない。決算の時間帯の記載がない発表は、窓の大きさから反応日を推定している（G5・G6の点数の一部）。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
