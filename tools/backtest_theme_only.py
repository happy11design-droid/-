#!/usr/bin/env python3
"""ツールを半導体・AI関連の銘柄に特化させた場合のバックテスト

使い方:
  tools/backtest_theme_only.py run [--out FILE]

後知恵を避けるため、S&P500の後知恵なしの監視銘柄（毎週その時点の数値で選び直す）の中から、業種で絞る。
  1. 今のルール（全業種）
  2. 半導体・AI関連の業種だけ: 半導体、半導体製造装置、コンピューター機器、家電（端末）、通信機器、電子部品、計測機器、
     ソフトウェア（アプリ・インフラ）、ITサービス、インターネット（コンテンツ・小売）
  2'. 2に、データセンター関連の業種（電気機器、特殊な産業機械、建設、建材、独立系の発電、特殊REIT）を足す（監視リストの7グループに近い）
  3. 全業種を使うが、同じ日の候補は半導体・AI関連を先に買う（テーマの外は枠が空いたときだけ）
今の採用ルール: 4つのルール、4銘柄・1銘柄25%、損切り15%、急落の底RSI(2)≦10、同じ業種2銘柄まで。
設計期間 2015〜2021年 / 確認期間 2022年〜。
"""
import argparse
import datetime as dt
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_caps as bcp
import backtest_combo2 as cb
from backtest_lib import COSTS, DEFAULT_CACHE, pct, portfolio, stats
from backtest_regime import srt

COST = COSTS[2]
SLOTS = 4
SEEDS = range(10)
IS_END, OOS_START = cb.IS_END, cb.OOS_START
DC = {"Electrical Equipment & Parts", "Specialty Industrial Machinery", "Engineering & Construction", "Building Products & Equipment",
      "Utilities—Independent Power Producers", "REIT—Specialty"}


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/半導体・AIに特化した場合.md")
    a = ap.parse_args()
    ctx = cb.setup(a.cache)
    data, ind, days, parts = (ctx[k] for k in ("data", "ind", "days", "parts"))
    base = srt(parts[("B", 0.15)] + parts[("M", 0.15)] + parts[("C", 0.15, 10)] + parts[("V", 0.15)])
    theme = {s for s in data if ind.get(s) in bcp.THEME}
    theme_dc = theme | {s for s in data if ind.get(s) in DC}

    di = {d: k for k, d in enumerate(days)}
    is_hi = max(d for d in days if d <= IS_END)
    oos_lo = min(d for d in days if d >= OOS_START)
    span = lambda lo, hi: (dt.date.fromisoformat(hi) - dt.date.fromisoformat(lo)).days / 365.25
    years = sorted({d[:4] for d in days})

    def seg(c, lo, hi):
        return c[di[hi]] / (c[di[lo] - 1] if di[lo] > 0 else 1.0)

    def summarize(ps):
        rs = []
        for p in ps:
            c = p["curve"]
            yr = {y: seg(c, min(d for d in days if d[:4] == y), max(d for d in days if d[:4] == y)) - 1 for y in years}
            rs.append({"all": p["cagr"], "mdd": p["mdd"], "exp": p["exposure"],
                       "is": seg(c, days[0], is_hi) ** (1 / span(days[0], is_hi)) - 1,
                       "oos": seg(c, oos_lo, days[-1]) ** (1 / span(oos_lo, days[-1])) - 1, "yr": yr})
        m = lambda key: cb.med([x[key] for x in rs])
        return {"all": m("all"), "mdd": m("mdd"), "is": m("is"), "oos": m("oos"), "exp": m("exp"),
                "rng": (min(x["all"] for x in rs), max(x["all"] for x in rs)),
                "yr": {y: cb.med([x["yr"][y] for x in rs]) for y in years}}

    def evaluate(tr):
        return summarize([portfolio(tr, COST, SLOTS, days, data, weight=1 / SLOTS, seed=k, group_of=ind, group_cap=2) for k in SEEDS])

    def evaluate_prio(tr, first):
        ps = []
        for k in SEEDS:
            rnd = random.Random(k)
            tt = [{**t, "rank": (0 if t["sym"] in first else 1, rnd.random())} for t in tr]
            ps.append(portfolio(tt, COST, SLOTS, days, data, weight=1 / SLOTS, group_of=ind, group_cap=2))
        return summarize(ps)

    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: 半導体・AIに特化した場合\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_theme_only.py\n---\n")
    w("# ツールを半導体・AI関連の銘柄に特化させた場合のバックテスト\n")
    w(__doc__.split("\n", 5)[5].strip() + "\n")
    w("年率・最大下落率は同じ日の候補の選び方をランダムにした10通りの中央値（幅は最小〜最大）。片道0.1%。「投資比率」は資金のうち株を持っていた割合の平均。\n")
    yrs = len(days) / 252
    rows = [("1. 今のルール（全業種）", base, None), ("2. 半導体・AI関連の業種だけ", [t for t in base if t["sym"] in theme], None),
            ("2'. 半導体・AI＋データセンター関連の業種", [t for t in base if t["sym"] in theme_dc], None),
            ("3. 全業種、半導体・AI関連を先に買う", base, theme), ("3'. 全業種、半導体・AI＋データセンターを先に買う", base, theme_dc)]
    w("| 形 | 合図の件数/年 | 1回平均（勝率） | 前半 / 後半 1回平均 | 年率（幅） | 最大下落率 | 設計期間 | 確認期間 | 投資比率 | 2018 | 2020 | 2022 | 2024 | 2025 |")
    w("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for lab, tr, first in rows:
        st = stats(tr, COST)
        h1 = stats([t for t in tr if t["in"] <= IS_END], COST)
        h2 = stats([t for t in tr if t["in"] >= OOS_START], COST)
        e = evaluate(tr) if first is None else evaluate_prio(tr, first)
        w(f"| {lab} | {st['n'] / yrs:.0f} | {pct(st['mean'], 2)}（{pct(st['win'], 0)}） | {pct(h1['mean'], 2)} / {pct(h2['mean'], 2)} | "
          f"{pct(e['all'])}（{pct(e['rng'][0])}〜{pct(e['rng'][1])}） | {pct(e['mdd'])} | {pct(e['is'])} | {pct(e['oos'])} | {pct(e['exp'], 0)} | "
          + " | ".join(pct(e["yr"][y], 0) for y in ("2018", "2020", "2022", "2024", "2025")) + " |")
        print(lab, file=sys.stderr)
    w("\n## 注意\n")
    w("- 新高値V2の「RS上位10」は、全業種の後知恵なしの監視銘柄の中の順位のまま（業種で絞った後に順位を付け直していない）。")
    w("- 業種は今のYahooの分類を過去にも使っている。NASDAQ100は含めていない（NASDAQ100だけに入っている半導体・AI銘柄は入らない）。")
    w("- 毎朝のツールが見ている87銘柄（テーマ監視銘柄）は今の時点で選んだものなので、過去の検証には使っていない。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
