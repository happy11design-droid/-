#!/usr/bin/env python3
"""成績が前半・後半とも安定していた手法の組み合わせと、使っていない資金の置き場所の検証

使い方:
  tools/backtest_lib.py fetch            # データの取得（共通。先に1回実行する）
  tools/backtest_combo.py run [--cache DIR] [--out FILE] [--start YYYY-MM-DD] [--end YYYY-MM-DD]

組み合わせる手法（ルールは各スクリプトと同じ。どれも翌日の寄り付きまたは予約注文で売買、片道0.1%）:
  A. ミネルヴィニ: トレンドテンプレート＋出来高を伴うベース上抜け、損切り15%・利確20%（tools/backtest_trend.py）
  B. ボリンジャー: メソッドIII 反転（%b<0.05かつ21日II%>0）、上部バンドで手じまい（tools/backtest_swing.py）
  C. コナーズ: SPY・QQQの2期間RSI≦5、5日線上抜けで手じまい（tools/backtest_connors.py 8節）
資金配分・同時保有の枠の共有・現金の置き場所は本のルールではなく、Claudeが設計の判断材料として試したもの。
"""
import argparse
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_connors as bc
import backtest_swing as bs
import backtest_trend as bt
from backtest_lib import COSTS, DEFAULT_CACHE, gen_trades, load_prices, load_universe, market_regime, pct, portfolio, spy_benchmark, stats

RISK, STOP, COST = 0.02, 0.15, COSTS[2]


def cmd_run(a):
    members, data = load_universe(a.cache, min_bars=260)
    for s in data.values():
        bt.prepare(s)
        bs.prepare(s)
    bt.add_rs_rank(data, members)
    spy = load_prices(a.cache, "SPY")
    days = [d for d in spy["date"] if a.start <= d <= a.end]
    spy_c = dict(zip(spy["date"], spy["c"]))
    spy_cagr, spy_mdd = spy_benchmark(spy, days)
    regime = market_regime(spy)

    A = gen_trades(data, members, bt.E_minervini(50), bt.X_NONE, a.start, a.end, ok=bt.liquid, fill="open",
                   max_hold=500, stop_pct=STOP, target=0.20)
    B = bs.simulate(data, members, bs.O_method3, bs.X_upper_band, a.start, a.end)
    etf_m = {k: [("0000-00-00", "9999-12-31")] for k in ("SPY", "QQQ")}
    etf = {k: bc.prepare(load_prices(a.cache, k)) for k in etf_m}
    C = bc.gen_trades(etf, etf_m, bc.E_rsi2(5), "5日線上抜け", (None, STOP, None), a.start, a.end, fill="open")
    allp = {**data, **etf}
    # 同じ日に複数の手法の候補があるときの優先順位（C→A→Bの順。C・Aは1トレード平均の大きい順、Bは件数が多く1件あたりが小さい）
    for pri, tr in ((0, C), (1, A), (2, B)):
        for t in tr:
            t["rank"] = (pri, t["rank"] if not isinstance(t["rank"], tuple) else t["rank"][1])

    halves = [("前半", a.start, "2020-12-31"), ("後半", "2021-01-01", a.end)]
    slots = int(round(STOP / RISK, 6))

    def port(tr, lo=None, hi=None, seed=None, cash=None):
        lo, hi = lo or a.start, hi or a.end
        dd = [d for d in days if lo <= d <= hi]
        return portfolio([t for t in tr if lo <= t["in"] and t["out"] <= hi], COST, slots, dd, allp, weight=RISK / STOP,
                         seed=seed, cash_asset=cash)

    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: 手法の組み合わせと現金の置き場所\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_combo.py\n---\n")
    w("# 手法の組み合わせと現金の置き場所\n")
    w(f"- 期間: {days[0]} 〜 {days[-1]}。前半＝〜2020年、後半＝2021年〜。価格は配当・分割調整済み、片道0.1%のコスト込み。")
    w("- 組み合わせる手法（前半・後半ともPFが1.4前後以上で、1トレード平均の95%区間がプラスだったもの）:")
    w("  - A. ミネルヴィニ: トレンドテンプレート＋出来高を伴うベース上抜け、損切り15%・利確20%")
    w("  - B. ボリンジャー: メソッドIII 反転（%b<0.05かつ21日II%>0）、上部バンドで手じまい、損切り15%")
    w("  - C. コナーズ: SPY・QQQの2期間RSI≦5、5日線上抜けで手じまい、損切り15%")
    w("- 建玉: リスク2%・損切り15%から逆算（1件に資金の13.3%、同時保有7件まで）。手法どうしで枠を共有し、同じ日はC→A→Bの順（ランダムな順の結果も併記）。")
    w("- 「現金をSPYで持つ」は、どの手法も保有していない資金をSPYで持ち、仕掛けるときにSPYを売って資金を作る想定（SPYの入れ替えの売買コストは入れていない）。")
    w("- 資金配分・枠の共有・現金の置き場所は本のルールではなく、新ツールの設計の判断材料としてClaudeが試したもの。\n")

    w("## 1. 手法ごとの件数と1トレードの成績（片道0.1%）\n")
    w("| 手法 | 件数 | 年平均件数 | 勝率 | 1トレード平均（95%区間）/ PF | 平均保有日数 |")
    w("|---|---|---|---|---|---|")
    years = len(days) / 252
    for name, tr in (("A. ミネルヴィニ", A), ("B. ボリンジャー メソッドIII", B), ("C. コナーズ SPY・QQQ", C)):
        st = stats(tr, COST)
        w(f"| {name} | {st['n']} | {st['n'] / years:.0f} | {pct(st['win'])} | {pct(st['mean'], 2)}（{pct(st['mean_ci'][0], 2)}〜{pct(st['mean_ci'][1], 2)}）/ {st['pf']:.2f} | {st['days']:.0f} |")

    w("\n## 2. 組み合わせのポートフォリオ\n")
    w("| 組み合わせ | 現金の置き場所 | 年率 | 最大下落率 | 前半 / 後半 年率 | ランダム順 年率 中央値（幅） | 平均投資比率（手法の保有分） | 実際に入った件数 |")
    w("|---|---|---|---|---|---|---|---|")
    combos = [("Aのみ", A), ("Bのみ", B), ("A＋B", A + B), ("A＋B＋C", A + B + C), ("A＋C", A + C)]
    for name, tr in combos:
        tr = sorted(tr, key=lambda t: (t["out"], t["sym"]))
        for cash_label, cash in (("現金（利息なし）", None), ("SPY", spy_c)):
            p = port(tr, cash=cash)
            h = [port(tr, lo, hi, cash=cash)["cagr"] for _, lo, hi in halves]
            rnd = sorted(port(tr, seed=k, cash=cash)["cagr"] for k in range(10))
            w(f"| {name} | {cash_label} | {pct(p['cagr'])} | {pct(p['mdd'])} | {pct(h[0])} / {pct(h[1])} | "
              f"{pct(rnd[5])}（{pct(rnd[0])}〜{pct(rnd[-1])}） | {pct(p['exposure'], 0)} | {p['taken']} |")
            print(name, cash_label, file=sys.stderr)
    h = []
    for _, lo, hi in halves:
        dd = [d for d in days if lo <= d <= hi]
        h.append(spy_benchmark(spy, dd)[0])
    w(f"| （参考）SPY買い持ち | | {pct(spy_cagr)} | {pct(spy_mdd)} | {pct(h[0])} / {pct(h[1])} | | 100% | |")

    w("\n## 3. 局面別（1トレード＝1件、片道0.1%）\n")
    w("| 手法 | 上昇: 件数 / 平均 / PF | 横ばい: 件数 / 平均 / PF | 下落: 件数 / 平均 / PF |")
    w("|---|---|---|---|")
    for name, tr in (("A. ミネルヴィニ", A), ("B. ボリンジャー メソッドIII", B), ("C. コナーズ SPY・QQQ", C)):
        cells = []
        for r in ("上昇", "横ばい", "下落"):
            st = stats([t for t in tr if regime.get(t["in"]) == r], COST)
            cells.append(f"{st['n']} / {pct(st['mean'], 2)} / {st['pf']:.2f}" if st else "0")
        w(f"| {name} | " + " | ".join(cells) + " |")

    w("\n## 4. 注意\n")
    w("- 組み合わせる手法は、同じ期間の検証結果を見て選んでいる。選んだ期間の成績は、将来より良く見える（選択による過大評価）。")
    w("- 上場廃止銘柄の欠落、寄り付きの気配値のすべり、SPY入れ替えのコストを入れていないことは、いずれも現実より良く見せる方向に働きうる。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/組み合わせ.md")
    r.add_argument("--start", default="2015-01-02")
    r.add_argument("--end", default=dt.date.today().isoformat())
    cmd_run(ap.parse_args())


if __name__ == "__main__":
    main()
