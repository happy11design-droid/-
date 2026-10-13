#!/usr/bin/env python3
"""採用ルールの買い・売りの合図はそのままで、株の代わりに2倍ETFを売買した場合のバックテスト

使い方:
  tools/backtest_2x.py run [--out FILE]

2倍ETFは実物のデータがない（多くは2022年以降の上場）ため、元の株の値動きから再現する:
  毎日、前日の終値からの株の値動きの2倍だけ動く（毎日2倍に合わせ直す）。経費は年1%（毎日 1%/252 を引く）。
  寄り付きで買う・売るときも、前日の終値からの株の値動きの2倍の値段とする。株が1日で50%以上下がるとETFは0になる。
合図: 今の採用ルール（4つのルール、急落の底RSI(2)≦10）を元の株で判定し、同じ日に売買する。4銘柄、同じ業種2銘柄まで。
比べる形:
  株（今のルール）: 1枠25%、損切りは株の15%
  2倍ETF・損切りはETFの15%（株の約7.5%）: 1枠25%
  2倍ETF・損切りはETFの30%（株の約15%と同じ）: 1枠25%
  2倍ETF・1枠の半分の額（12.5%、株を1枠持つのとほぼ同じ大きさ）・損切りはETFの30%
  2倍ETFがある銘柄だけETFにする（Claudeが把握している2026年時点の個別株2倍ETFの対象。実際の有無は証券会社で確認が必要）
損切りは引けで判定し、翌日の寄り付きで売る。片道0.1%。設計期間 2015〜2021年 / 確認期間 2022年〜。
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
FEE = 0.01 / 252
HAS_2X = {"NVDA", "AMD", "TSLA", "AAPL", "MSFT", "AMZN", "GOOGL", "GOOG", "META", "AVGO", "MU", "SMCI", "PLTR", "NFLX",
          "ORCL", "CRWD", "COIN", "INTC", "QCOM", "UBER", "LLY", "BA", "PANW", "ANET", "DELL", "HOOD", "MRVL", "APP"}


def etf_series(s):
    c, o, n = s["c"], s["o"], len(s["c"])
    L = [1.0] * n
    for t in range(1, n):
        L[t] = max(0.0, L[t - 1] * (1 + 2 * (c[t] / c[t - 1] - 1) - FEE))
    at_open = [None] + [max(0.0, L[t - 1] * (1 + 2 * (o[t] / c[t - 1] - 1))) for t in range(1, n)]
    return L, at_open


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/2倍ETFに置き換えた場合.md")
    a = ap.parse_args()
    ctx = cb.setup(a.cache)
    data, ind, days, parts = (ctx[k] for k in ("data", "ind", "days", "parts"))
    base = srt(parts[("B", 0.15)] + parts[("M", 0.15)] + parts[("C", 0.15, 10)] + parts[("V", 0.15)])
    syms = {t["sym"] for t in base}
    etf, etf_open, pos = {}, {}, {}
    for sym in syms:
        L, Lo = etf_series(data[sym])
        etf[sym], etf_open[sym] = L, Lo
        pos[sym] = {d: k for k, d in enumerate(data[sym]["date"])}
    # ポートフォリオの時価評価に使う「銘柄ごとの終値」を、ETFの値に置き換えたデータ
    edata = {sym: {"date": data[sym]["date"], "c": etf[sym]} for sym in syms}

    def to_etf(tr, stop, only=None):
        out, n_stop = [], 0
        for t in tr:
            sym = t["sym"]
            if only is not None and sym not in only:
                # ETFがない銘柄は株のまま（評価用に、株の値を ETF と同じ形の系列として持たせる）
                out.append({**t, "src": "stock"})
                continue
            s, L, Lo = data[sym], etf[sym], etf_open[sym]
            i0, i1 = pos[sym][t["in"]], pos[sym][t["out"]]
            px = Lo[i0]
            if not px:
                continue
            x = i1
            for j in range(i0, i1):
                if L[j] <= px * (1 - stop) and j + 1 <= i1:
                    x = j + 1
                    break
            if x < i1:
                n_stop += 1
                sell = Lo[x]
            else:
                # 元のルールどおりの手じまい（寄り付き、または日中の損切り）の株の値段を、ETFの値段に直す
                p_exit = t["px"] * (1 + t["ret"])
                sell = max(0.0, L[i1 - 1] * (1 + 2 * (p_exit / s["c"][i1 - 1] - 1)))
            out.append({**t, "out": s["date"][x], "px": px, "ret": sell / px - 1, "src": "etf"})
        return srt(out), n_stop

    di = {d: k for k, d in enumerate(days)}
    is_hi = max(d for d in days if d <= IS_END)
    oos_lo = min(d for d in days if d >= OOS_START)
    span = lambda lo, hi: (dt.date.fromisoformat(hi) - dt.date.fromisoformat(lo)).days / 365.25
    years = sorted({d[:4] for d in days})

    def seg(c, lo, hi):
        return c[di[hi]] / (c[di[lo] - 1] if di[lo] > 0 else 1.0)

    def evaluate(tr, dat, weight=1 / SLOTS):
        rs = []
        for k in SEEDS:
            p = portfolio(tr, COST, SLOTS, days, dat, weight=weight, seed=k, group_of=ind, group_cap=2)
            c = p["curve"]
            yr = {y: seg(c, min(d for d in days if d[:4] == y), max(d for d in days if d[:4] == y)) - 1 for y in years}
            rs.append({"all": p["cagr"], "mdd": p["mdd"], "is": seg(c, days[0], is_hi) ** (1 / span(days[0], is_hi)) - 1,
                       "oos": seg(c, oos_lo, days[-1]) ** (1 / span(oos_lo, days[-1])) - 1, "yr": yr})
        m = lambda key: cb.med([x[key] for x in rs])
        return {"all": m("all"), "mdd": m("mdd"), "is": m("is"), "oos": m("oos"),
                "rng": (min(x["all"] for x in rs), max(x["all"] for x in rs)),
                "yr": {y: cb.med([x["yr"][y] for x in rs]) for y in years}}

    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: 2倍ETFに置き換えた場合\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_2x.py\n---\n")
    w("# 採用ルールの合図のまま、株の代わりに2倍ETFを売買した場合のバックテスト\n")
    w(__doc__.split("\n", 5)[5].strip() + "\n")
    w("年率・最大下落率は同じ日の候補の選び方をランダムにした10通りの中央値（幅は最小〜最大）。後知恵なしの監視銘柄（S&P500）。\n")
    w("| 形 | 年率 2015年〜（幅） | 最大下落率 | 設計期間 | 確認期間 | 2018 | 2020 | 2022 | 2024 | 2025 | 損切りで早めに売った件数 |")
    w("|---|---|---|---|---|---|---|---|---|---|---|")

    def row(lab, e, n=""):
        w(f"| {lab} | {pct(e['all'])}（{pct(e['rng'][0])}〜{pct(e['rng'][1])}） | {pct(e['mdd'])} | {pct(e['is'])} | {pct(e['oos'])} | "
          + " | ".join(pct(e["yr"][y], 0) for y in ("2018", "2020", "2022", "2024", "2025")) + f" | {n} |")
        print(lab, file=sys.stderr)

    row("株（今のルール）", evaluate(base, data))
    t15, n15 = to_etf(base, 0.15)
    row("2倍ETF・損切りはETFの15%（株の約7.5%）", evaluate(t15, edata), n15)
    t30, n30 = to_etf(base, 0.30)
    row("2倍ETF・損切りはETFの30%（株の約15%）", evaluate(t30, edata), n30)
    row("2倍ETF・1枠の半分の額（12.5%）・損切りはETFの30%", evaluate(t30, edata, weight=1 / (2 * SLOTS)), n30)

    # ETFがある銘柄だけETF、それ以外は株（評価用のデータを銘柄ごとに切り替える）
    only = HAS_2X & syms
    mixed, nm = to_etf(base, 0.30, only)
    mdata = {sym: (edata[sym] if sym in only else data[sym]) for sym in syms}
    n_in = sum(1 for t in base if t["sym"] in only)
    row(f"2倍ETFがある銘柄（{len(only)}銘柄）だけETF・損切りはETFの30%、ほかは株", evaluate(mixed, mdata), nm)
    w(f"\n- 2倍ETFがあるとした銘柄: {', '.join(sorted(only))}（全部の合図 {len(base)}件のうち {n_in}件）")
    w("\n## 注意\n")
    w("- 2倍ETFの値動きは、元の株の値動きから計算した再現。実際のETFは、価格のずれ（乖離）、売買の差額（スプレッド）、配当の扱いなどで少し違う。")
    w("- 2倍ETFがある銘柄の一覧は、Claudeが把握している範囲のもので、実際にあるか・いつからあるかは証券会社で確認が必要。多くは2022年以降の上場で、それ以前の期間は「もしあったら」の計算。")
    w("- ユーザーの決定「ETFは下落相場のとき以外は使わない」（`現状まとめ.md` 2節）があるため、採用する場合はこの決定の変更になる。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
