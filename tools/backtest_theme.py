#!/usr/bin/env python3
"""「今旬のテーマ・銘柄だけに絞る」と成績が上がるかの検証（直近3年、個別株のみ）

使い方:
  tools/theme_universe.py fetch          # 対象銘柄（時価総額10億ドル以上の米国株）と業種・日足の取得
  tools/backtest_theme.py run [--cache DIR] [--out FILE] [--start YYYY-MM-DD] [--end YYYY-MM-DD]

「今から見て勝った銘柄（NVDA・MU・SNDKなど）」を選んで過去を検証すると必ず良い結果になる（後知恵）。
そのため「旬」は各時点で分かっていた情報だけで機械的に決める:
  - 旬の銘柄: その日のRSランキング（直近3カ月40%・6/9/12カ月各20%の加重リターンの百分位）が90以上
  - 旬の業種: その日の業種ごとの騰落率の中央値（6カ月）が上位10業種に入る業種の銘柄（ヒートマップの代わり）
売買のルールは tools/backtest_trend.py（ミネルヴィニ）・tools/backtest_swing.py（ボリンジャー）・tools/backtest_connors.py（コナーズ）と同じ。
"""
import argparse
import datetime as dt
import operator
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_connors as bc
import backtest_swing as bs
import backtest_trend as bt
import theme_universe as tu
from backtest_lib import (COSTS, DEFAULT_CACHE, Reporter, gen_trades, load_prices, market_regime, pct, rsi_wilder, sliding, sma,
                          spy_benchmark, stats)

RISK, STOP, COST = 0.02, 0.15, COSTS[2]


def prepare(d, since):
    """この検証で使う指標だけを計算する（約2,700銘柄を扱うため、各スクリプトの prepare より軽くしている。計算式は同じ）"""
    k0 = next((k for k, x in enumerate(d["date"]) if x >= since), len(d["date"]))
    for key in ("date", "o", "h", "l", "c", "v"):
        d[key] = d[key][k0:]
    c, h, l, v = d["c"], d["h"], d["l"], d["v"]
    n = len(c)
    d["ma5"], d["ma50"], d["ma150"], d["ma200"] = sma(c, 5), sma(c, 50), sma(c, 150), sma(c, 200)
    d["vol50"], d["vol100"] = [None] + sma(v, 50)[:-1], sma(v, 100)
    d["hi252"], d["lo252"] = sliding(h, 252, operator.ge, True), sliding(l, 252, operator.le, True)
    d["hi"], d["lo"] = {50: sliding(h, 50, operator.ge, False)}, {50: sliding(l, 50, operator.le, False)}
    ret = lambda k: [c[i] / c[i - k] - 1 if i >= k else None for i in range(n)]
    r63, r126, r189, r252 = ret(63), ret(126), ret(189), ret(252)
    d["rs_raw"] = [0.4 * r63[i] + 0.2 * r126[i] + 0.2 * r189[i] + 0.2 * r252[i] if r252[i] is not None else None for i in range(n)]
    d["rs"] = [None] * n
    d["rsi2"] = rsi_wilder(c, 2)
    mid, sd = sma(c, 20), bs.stdev(c, 20)
    up = [m + 2 * x if m is not None else None for m, x in zip(mid, sd)]
    dn = [m - 2 * x if m is not None else None for m, x in zip(mid, sd)]
    d["pctb"] = [(c[i] - dn[i]) / (up[i] - dn[i]) if mid[i] is not None and up[i] > dn[i] else None for i in range(n)]
    ii = [((2 * c[i] - h[i] - l[i]) / (h[i] - l[i]) * v[i]) if h[i] > l[i] else 0.0 for i in range(n)]
    d["ii21"] = [None] * n
    si = sv = 0.0
    for i in range(n):
        si, sv = si + ii[i], sv + v[i]
        if i >= 21:
            si, sv = si - ii[i - 21], sv - v[i - 21]
        if i >= 20 and sv:
            d["ii21"][i] = si / sv


def cmd_run(a):
    uni, data = tu.load_universe_theme(a.cache)
    since = (dt.date.fromisoformat(a.start) - dt.timedelta(days=int(365.25 * 2))).isoformat()
    strength = tu.industry_strength(data)       # 業種の強さは全期間の日足で先に計算する
    members = {s: [("0000-00-00", "9999-12-31")] for s in data}
    for s in data.values():
        prepare(s, since)
    data = {k: s for k, s in data.items() if len(s["c"]) > 260}
    members = {k: members[k] for k in data}
    bt.add_rs_rank(data, members)
    lead = {d: tu.leading(strength, d, 10, key=126) for d in strength}
    spy = load_prices(a.cache, "SPY")
    regime = market_regime(spy)
    days = [d for d in spy["date"] if a.start <= d <= a.end]
    years = len(days) / 252
    mid = "2025-01-01"
    halves = [("前半", a.start, "2024-12-31"), ("後半", mid, a.end)]
    spy_cagr, spy_mdd = spy_benchmark(spy, days)

    base_ok = bt.liquid
    filters = [
        ("全銘柄", lambda s, i, sp: base_ok(s, i, sp)),
        ("旬の銘柄（RS≧90）", lambda s, i, sp: base_ok(s, i, sp) and s["rs"][i] is not None and s["rs"][i] >= 90),
        ("旬の業種（6カ月の上位10業種）", lambda s, i, sp: base_ok(s, i, sp) and s["industry"] in lead.get(s["date"][i], ())),
        ("旬の業種かつ旬の銘柄", lambda s, i, sp: base_ok(s, i, sp) and s["industry"] in lead.get(s["date"][i], ())
         and s["rs"][i] is not None and s["rs"][i] >= 90),
    ]

    def connors_ok(f):
        # コナーズの銘柄選定（株価≧5ドル、100日平均出来高≧25万株、終値>200日線）に旬の条件を重ねる
        return lambda s, i, sp: bc.signal_ok(s, i, sp) and f(s, i, sp)

    strategies = [
        ("順張り: ミネルヴィニ（トレンドテンプレート＋出来高を伴う上抜け、損切り15%・利確20%）",
         lambda ok: gen_trades(data, members, bt.E_minervini(50), bt.X_NONE, a.start, a.end, ok=ok, fill="open",
                               max_hold=500, stop_pct=STOP, target=0.20)),
        ("逆張り: ボリンジャー メソッドIII（%b<0.05かつ21日II%>0、上部バンドで手じまい）",
         lambda ok: bs.simulate(data, members, bs.O_method3, bs.X_upper_band, a.start, a.end, ok=ok)),
        ("逆張り: コナーズ 個別株2日累積RSI≦10（200日線より上、5日線上抜けで手じまい、損切り15%）",
         lambda ok: gen_trades(data, members, bc.E_cum2(10), lambda j, s, k, px: s["c"][j] > s["ma5"][j], a.start, a.end,
                               ok=connors_ok(ok), fill="open", max_hold=30, stop_pct=STOP)),
    ]

    L = []
    w = L.append
    rep = Reporter(w, data, days, halves, years, cost=COST, risk=RISK)
    w("---\ntype: backtest\ntitle: 旬のテーマ・銘柄に絞った場合の検証（直近3年）\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_theme.py\n---\n")
    w("# 旬のテーマ・銘柄に絞った場合の検証（直近3年）\n")
    w(f"- 期間: {days[0]} 〜 {days[-1]}（{len(days)}取引日）。前半＝〜2024年、後半＝2025年〜。")
    w(f"- 対象: いま米国に上場している時価総額10億ドル以上の普通株 {len(data)} 銘柄（NASDAQのスクリーナー、業種はYahoo Finance）。ETFは含めない。"
      "**いま上場していて時価総額が大きい＝この3年を生き残った・値上がりした銘柄なので、どの手法も実際より良く出る（生存者バイアス）**。手法どうし・絞り方どうしの比較に使うこと。")
    w("- 「旬」は各時点で分かっていた情報だけで決める（今から見て勝った銘柄を選ぶと後知恵になるため）: "
      "旬の銘柄＝その日のRSランキング≧90、旬の業種＝その日の6カ月騰落率の中央値が上位10の業種（ヒートマップの代わり）。")
    w("- 売買: 翌日の寄り付き、またはパターンB（予約注文）を日足で再現。片道0.1%、損切り15%、リスク2%で建玉（13.3%×7銘柄）。価格は配当・分割調整済み。")
    w(f"- 参考（採用はしない。相場全体の強さの目安）: 同期間のSPY買い持ち 年率 {pct(spy_cagr)}、最大下落率 {pct(spy_mdd)}\n")

    results = {}
    for k, (sname, fn) in enumerate(strategies, 1):
        w(f"## {k}. {sname}\n")
        rep.header("ルールの強さの順")
        for fname, f in filters:
            tr = fn(f)
            results[(sname, fname)] = tr
            rep.line(fname, tr, STOP)
        w("")

    w("## 4. 局面別（1トレード＝1件、旬の業種かつ旬の銘柄、片道0.1%）\n")
    w("| 手法 | 上昇: 件数 / 平均 / PF | 横ばい: 件数 / 平均 / PF | 下落: 件数 / 平均 / PF |")
    w("|---|---|---|---|")
    for sname, _ in strategies:
        tr = results[(sname, filters[3][0])]
        cells = []
        for r in ("上昇", "横ばい", "下落"):
            st = stats([t for t in tr if regime.get(t["in"]) == r], COST)
            cells.append(f"{st['n']} / {pct(st['mean'], 2)} / {st['pf']:.2f}" if st else "0")
        w(f"| {sname.split('（')[0]} | " + " | ".join(cells) + " |")

    w("\n## 5. 注意\n")
    w("- 3年は短く、AI・半導体の上昇相場が大半を占める。件数が少ない条件は信頼区間が広い。")
    w("- 生存者バイアス（上の対象の説明）に加え、寄り付きの気配値のすべりを入れていないことも、現実より良く見せる方向に働く。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/旬のテーマ・直近3年.md")
    three = dt.date.today().replace(year=dt.date.today().year - 3).isoformat()
    r.add_argument("--start", default=three)
    r.add_argument("--end", default=dt.date.today().isoformat())
    cmd_run(ap.parse_args())


if __name__ == "__main__":
    main()
