#!/usr/bin/env python3
"""コナーズ『短期売買入門』の数値ルールのバックテスト（`新分析ツール/引き継ぎ.md` 5-1）

使い方:
  tools/backtest_lib.py fetch [--cache DIR]
      データの取得（共通。先に1回実行する）
  tools/backtest_connors.py run [--cache DIR] [--out FILE] [--start YYYY-MM-DD] [--end YYYY-MM-DD]
      ルール表（`書籍ルール/コナーズ_ルール表.md`）の条件でシグナルを出し、成績をMarkdownで書き出す。

前提（結果の読み方に関わるので出力にも明記する）:
  - シグナルはその日の構成銘柄だけで出す（今の構成銘柄だけで検証したときの生存者バイアスを避けるため）。
    ただしYahooから消えた上場廃止銘柄は取得できないので、その分のバイアスは残る（取得率を出力する）。
  - 価格は配当・株式分割調整済み。1〜4節は当日の引け値（ルール表の注文方法「大引け」）、5節以降は翌日の寄り付きで売買。
  - 売買コストは片道の率で複数通り（0%・0.05%・0.1%）を出す。
  - 統計は1シグナル＝1トレード（資金の制約なし）と、同時保有数に上限を置いたポートフォリオの2通り。
"""
import argparse
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_lib as lib
from backtest_lib import (COSTS, DEFAULT_CACHE, is_member, load_members, load_prices, market_regime, pct,
                          portfolio, rsi_wilder, sma, stats)

MAX_HOLD = 30                  # 手じまい条件が出ないときの打ち切り（取引日）

# ---------- 戦略 ----------
# entry(i, s) -> シグナルなら並べ替え用の値（小さいほど優先）、なければNone
# exit(i, s, k) -> k日目（仕掛けからの経過取引日）に手じまうか

def E_rsi2(th):
    return lambda i, s: s["rsi2"][i] if s["rsi2"][i] is not None and s["rsi2"][i] <= th else None


def E_cum2(th):
    def f(i, s):
        r, q = s["rsi2"][i], s["rsi2"][i - 1]
        return r + q if r is not None and q is not None and r + q <= th else None
    return f


def E_double7(i, s):
    return s["rsi2"][i] if s["low7c"][i] is not None and s["c"][i] <= s["low7c"][i] else None


X = {
    "5日線上抜け": lambda i, s, k: s["c"][i] > s["ma5"][i],
    "10日線上抜け": lambda i, s, k: s["c"][i] > s["ma10"][i],
    "RSI(2)≧70": lambda i, s, k: s["rsi2"][i] >= 70,
    "7日最高値で引け": lambda i, s, k: s["high7c"][i] is not None and s["c"][i] >= s["high7c"][i],
    "5取引日後": lambda i, s, k: k >= 5,
}

STRATEGIES = [
    # 名前, エントリー, 手じまい, 出典
    ("RSI(2)≦5・5日線上抜けで手じまい（基本戦略）", E_rsi2(5), "5日線上抜け", "p.22, p.45"),
    ("RSI(2)≦5・RSI(2)≧70で手じまい", E_rsi2(5), "RSI(2)≧70", "p.22, p.23"),
    ("RSI(2)≦5・10日線上抜けで手じまい", E_rsi2(5), "10日線上抜け", "p.22, p.36"),
    ("RSI(2)≦5・5取引日後に手じまい", E_rsi2(5), "5取引日後", "p.22, p.36"),
    ("RSI(2)≦10・5日線上抜けで手じまい（閾値を緩めた参考）", E_rsi2(10), "5日線上抜け", "ルール表外（頻度の比較用）"),
    ("個別株2日累積RSI≦10・5日線上抜けで手じまい", E_cum2(10), "5日線上抜け", "p.24"),
    ("ダブル7（7日最安値で引け）・7日最高値で引けて手じまい", E_double7, "7日最高値で引け", "p.26"),
]

STOPS = [
    ("ストップなし（コナーズの原則）", None, None),
    ("引け値で−10%以下なら当日引けで損切り", 0.10, None),
    ("引け値で−15%以下なら当日引けで損切り", 0.15, None),
    ("10取引日たっても手じまい条件が出なければ手じまい", None, 10),
]


def prepare(d):
    c = d["c"]
    d["ma200"], d["ma5"], d["ma10"] = sma(c, 200), sma(c, 5), sma(c, 10)
    d["rsi2"] = rsi_wilder(c, 2)
    d["vol100"] = sma(d["v"], 100)
    # 直近7日（当日を含まない）の終値ベースの最安値・最高値。「7日最安値で引ける」は当日終値がそれ以下
    prev7 = lambda f: [f(c[i - 7:i]) if i >= 7 else None for i in range(len(c))]
    d["low7c"], d["high7c"] = prev7(min), prev7(max)
    return d



def signal_ok(s, i, spans):
    """ルール表の銘柄選定・トレンドフィルター（p.16-17, p.22: 株価≧5ドル、100日平均出来高≧25万株、終値>200日線）"""
    return (s["ma200"][i] is not None and s["vol100"][i] is not None and s["c"][i] >= 5
            and s["vol100"][i] >= 250_000 and s["c"][i] > s["ma200"][i] and is_member(spans, s["date"][i]))


def gen_trades(data, members, entry, exit_name, stop, start, end, fill="close", allow=None):
    ex = X[exit_name]
    return lib.gen_trades(data, members, entry, lambda j, s, k, px: ex(j, s, k), start, end, ok=signal_ok, fill=fill,
                          allow=allow, max_hold=MAX_HOLD, stop_pct=stop[1], time_stop=stop[2])



# ---------- 実行 ----------

def cmd_run(a):
    members = load_members(a.cache)
    data = {}
    for sym in members:
        d = load_prices(a.cache, sym)
        if d and len(d["c"]) > 210:
            data[sym] = prepare(d)
    spy, vix = load_prices(a.cache, "SPY"), load_prices(a.cache, "^VIX")
    regime = market_regime(spy)
    days = [d for d in spy["date"] if a.start <= d <= a.end]
    spy_c = dict(zip(spy["date"], spy["c"]))
    spy_cagr = (spy_c[days[-1]] / spy_c[days[0]]) ** (365.25 / (dt.date.fromisoformat(days[-1]) - dt.date.fromisoformat(days[0])).days) - 1
    peak = mdd = 0
    for d in days:
        peak = max(peak, spy_c[d]); mdd = max(mdd, 1 - spy_c[d] / peak)

    # 取得率（期間中に一度でも構成銘柄だった銘柄のうち、価格を取得できた割合）
    in_period = [s for s, sp in members.items() if any(st <= a.end and e >= a.start for st, e in sp)]
    got = [s for s in in_period if s in data]
    periods = [("2015〜2019", "2015-01-01", "2019-12-31"), ("2020〜2022", "2020-01-01", "2022-12-31"),
               ("2023〜", "2023-01-01", "9999-12-31")]

    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: コナーズ 短期売買入門 数値ルールのバックテスト\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_connors.py\n---\n")
    w("# コナーズ 数値ルールのバックテスト\n")
    w(f"- 期間: {days[0]} 〜 {days[-1]}（{len(days)}取引日）")
    w(f"- 対象: その日にS&P500の構成銘柄だった銘柄（構成銘柄の履歴: fja05680/sp500）。期間中の構成銘柄 {len(in_period)} のうち価格を取得できたのは {len(got)}（{pct(len(got) / len(in_period))}）。"
      "取得できなかったのは主に買収・上場廃止・ティッカー変更の銘柄で、上場廃止前の急落を含まない分だけ成績は良く出る方向にずれうる。")
    w("- ルール: `書籍ルール/コナーズ_ルール表.md` の条件（株価≧5ドル、100日平均出来高≧25万株、終値>200日線）＋各エントリー条件。仕掛け・手じまいとも引け値。")
    w("- 価格: 配当・分割調整済み（Yahooの調整後終値）。")
    w(f"- 手じまい条件が{MAX_HOLD}取引日出ない場合はその日の引けで打ち切り。同じ銘柄の保有中は新しいシグナルを数えない。")
    w("- 局面: SPYの30週線（150日線）の位置と4週前からの傾きでワインスタインのステージを近似（上昇＝線より上かつ上向き、下落＝線より下かつ下向き、それ以外＝横ばい）。")
    w("- 平均リターンの信頼区間は、同じ日のシグナル同士が独立でないため、月単位のブロック・ブートストラップ（1000回）。")
    w(f"- 比較: 同期間のSPY買い持ち 年率 {pct(spy_cagr)}、最大下落率 {pct(mdd)}（配当込み）\n")

    w("## 1. 戦略ごとの成績（ストップなし）\n")
    w("1シグナル＝1トレード（資金の制約なし）。コストは片道。\n")
    w("| 戦略 | 出典 | 件数 | 年平均件数 | 勝率（片道0.1%、95%区間） | 平均（コスト0） | 平均（片道0.05%） | 平均（片道0.1%）（95%区間） | 平均利益/平均損失（0.1%） | PF（0.1%） | 平均保有日数 | 最大連敗 | 最悪 |")
    w("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    years = len(days) / 252
    results = {}
    for name, ent, exn, src in STRATEGIES:
        tr = gen_trades(data, members, ent, exn, STOPS[0], a.start, a.end)
        results[name] = tr
        s0, s1, s2 = (stats(tr, c) for c in COSTS)
        w(f"| {name} | {src} | {s0['n']} | {s0['n'] / years:.0f} | {pct(s2['win'])}（{pct(s2['win_ci'][0])}〜{pct(s2['win_ci'][1])}） | "
          f"{pct(s0['mean'], 2)} | {pct(s1['mean'], 2)} | {pct(s2['mean'], 2)}（{pct(s2['mean_ci'][0], 2)}〜{pct(s2['mean_ci'][1], 2)}） | "
          f"{pct(s2['avg_win'], 2)} / {pct(s2['avg_loss'], 2)} | {s2['pf']:.2f} | {s0['days']:.1f} | {s2['streak']} | {pct(s2['min'])} |")
        print(name, s0["n"], file=sys.stderr)

    base = STRATEGIES[0][0]
    w("\n## 2. 基本戦略の期間別・局面別（片道0.1%）\n")
    w("過去の一時期だけ良かったのではないか、局面によって成績が変わるかを見る。\n")
    w("| 区分 | 件数 | 勝率（95%区間） | 平均（95%区間） | PF | 最大連敗 | 最悪 |")
    w("|---|---|---|---|---|---|---|")
    groups = [(p, [t for t in results[base] if s <= t["in"] <= e]) for p, s, e in periods]
    groups += [(f"局面: {r}", [t for t in results[base] if regime.get(t["in"]) == r]) for r in ("上昇", "横ばい", "下落")]
    vix10 = dict(zip(vix["date"], sma(vix["c"], 10)))
    vixc = dict(zip(vix["date"], vix["c"]))
    hi = lambda t: vix10.get(t["in"]) and vixc[t["in"]] >= vix10[t["in"]] * 1.05
    lo = lambda t: vix10.get(t["in"]) and vixc[t["in"]] <= vix10[t["in"]] * 0.95
    groups += [("VIX≧10日線×1.05（p.12 買いに有利）", [t for t in results[base] if hi(t)]),
               ("VIX≦10日線×0.95（p.12 見送り）", [t for t in results[base] if lo(t)])]
    for g, tr in groups:
        s = stats(tr, COSTS[2])
        if not s:
            w(f"| {g} | 0 | | | | | |")
            continue
        w(f"| {g} | {s['n']} | {pct(s['win'])}（{pct(s['win_ci'][0])}〜{pct(s['win_ci'][1])}） | {pct(s['mean'], 2)}（{pct(s['mean_ci'][0], 2)}〜{pct(s['mean_ci'][1], 2)}） | {s['pf']:.2f} | {s['streak']} | {pct(s['min'])} |")

    w("\n## 3. 損切りの有無の比較（未決事項1の判断材料、基本戦略、片道0.1%）\n")
    w("コナーズはストップを置かない原則（p.13, p.36-37, p.45）。損切りは引け値で判定（日中の逆指値ではない）した近似。\n")
    w("| 損切りのルール | 件数 | 勝率 | 平均 | PF | 最大連敗 | 最悪 | 損切り・時間切れの件数 |")
    w("|---|---|---|---|---|---|---|---|")
    stop_results = {}
    for st in STOPS:
        tr = results[base] if st[1] is None and st[2] is None else gen_trades(data, members, STRATEGIES[0][1], STRATEGIES[0][2], st, a.start, a.end)
        stop_results[st[0]] = tr
        s = stats(tr, COSTS[2])
        cut = sum(1 for t in tr if t["why"] in ("損切り", "時間"))
        w(f"| {st[0]} | {s['n']} | {pct(s['win'])} | {pct(s['mean'], 2)} | {s['pf']:.2f} | {s['streak']} | {pct(s['min'])} | {cut} |")

    w("\n## 4. 資金に上限がある場合（同時保有数の上限つき、片道0.1%）\n")
    w("資金を等分し、同じ日のシグナルが空き枠より多いときはRSI(2)（またはその戦略の並べ替え値）の低い順に入れる。"
      "保有中は毎日の終値で時価評価している。\n")
    w("| 戦略 | 同時保有数 | 年率 | 最大下落率 | 実際に入ったトレード数 | 10年で1が何倍 |")
    w("|---|---|---|---|---|---|")
    for name in [STRATEGIES[0][0], STRATEGIES[5][0], STRATEGIES[6][0]]:
        for slots in (5, 10, 20):
            p = portfolio(results[name], COSTS[2], slots, days, data)
            w(f"| {name} | {slots} | {pct(p['cagr'])} | {pct(p['mdd'])} | {p['taken']} | {(1 + p['cagr']) ** 10:.2f} |")
    w(f"| （参考）SPY買い持ち | | {pct(spy_cagr)} | {pct(mdd)} | | {(1 + spy_cagr) ** 10:.2f} |")

    # ---- 5〜7: 引け後に判定して翌日の寄り付きで売買する運用（実際にできる方法）----
    vlo_d = lambda d: vix10.get(d) and vixc[d] <= vix10[d] * 0.95
    vhi_d = lambda d: vix10.get(d) and vixc[d] >= vix10[d] * 1.05
    not_down = lambda d: regime.get(d) != "下落"
    filters = [
        ("なし", None),
        ("下落局面は買わない", not_down),
        ("VIX≦10日線×0.95の日は買わない（p.12）", lambda d: not vlo_d(d)),
        ("下落局面は買わない＋VIX≦10日線×0.95の日は買わない", lambda d: not_down(d) and not vlo_d(d)),
        ("下落局面は買わない＋VIX≧10日線×1.05の日だけ買う（p.12）", lambda d: not_down(d) and bool(vhi_d(d))),
    ]
    main3 = [STRATEGIES[0], STRATEGIES[5], STRATEGIES[6]]
    halves = [("前半 2015〜2020", a.start, "2020-12-31"), ("後半 2021〜", "2021-01-01", a.end)]

    def pf_line(tr):
        st = stats(tr, COSTS[2])
        return f"{pct(st['mean'], 2)}（{pct(st['mean_ci'][0], 2)}〜{pct(st['mean_ci'][1], 2)}）/ {st['pf']:.2f}" if st else "0件"

    def port(tr, lo, hi, **kw):
        dd = [d for d in days if lo <= d <= hi]
        return portfolio([t for t in tr if lo <= t["in"] and t["out"] <= hi], COSTS[2], kw.pop("slots", 10), dd, data, **kw)

    w("\n## 5. 引け値で売買した場合と、翌日の寄り付きで売買した場合（フィルターなし、片道0.1%）\n")
    w("引け後に分析する運用では、シグナルの日の引けでは買えない。引け後に判定し、翌取引日の寄り付きで仕掛け・手じまう場合と比べる。ポートフォリオは同時保有10銘柄。\n")
    w("| 戦略 | 売買のタイミング | 件数 | 勝率 | 1トレード平均（95%区間）/ PF | 年率 | 最大下落率 |")
    w("|---|---|---|---|---|---|---|")
    opened = {}
    for name, ent, exn, src in main3:
        opened[name] = gen_trades(data, members, ent, exn, STOPS[0], a.start, a.end, fill="open")
        for lab, tr in (("当日の引け", results[name]), ("翌日の寄り付き", opened[name])):
            st, p = stats(tr, COSTS[2]), portfolio(tr, COSTS[2], 10, days, data)
            w(f"| {name} | {lab} | {st['n']} | {pct(st['win'])} | {pf_line(tr)} | {pct(p['cagr'])} | {pct(p['mdd'])} |")

    same_day = {}
    for t in opened[STRATEGIES[0][0]]:
        same_day[t["in"]] = same_day.get(t["in"], 0) + 1
    w("\n基本戦略（翌日の寄り付き）を、同じ日に仕掛けたシグナルの数で分けた1トレード平均。"
      "1トレード平均のプラスは相場全体が売られた日（多数の銘柄が同時にシグナルを出す日）に集中しており、"
      "同時保有数に上限があるとその日に一部しか買えないため、ポートフォリオの年率が伸びない。\n")
    w("| 同じ日のシグナル数 | 件数 | 1トレード平均（95%区間）/ PF |")
    w("|---|---|---|")
    for lo_n, hi_n in ((1, 3), (4, 10), (11, 30), (31, 10 ** 6)):
        g = [t for t in opened[STRATEGIES[0][0]] if lo_n <= same_day[t["in"]] <= hi_n]
        w(f"| {lo_n}〜{'' if hi_n > 1000 else hi_n} | {len(g)} | {pf_line(g)} |")

    w("\n## 6. 市場全体の条件（局面・VIX）を足した場合（翌日の寄り付きで売買、片道0.1%）\n")
    w("条件はどれも本のルール（ワインスタインの局面、コナーズのVIXルール p.12）で、数値を調整していない。"
      "過去データに合わせ込んでいないかを見るため、前半（2015〜2020）と後半（2021〜）の両方で効くかを確認する。"
      "「1トレード平均」は1シグナル＝1トレード、年率・最大下落率は同時保有10銘柄のポートフォリオ。\n")
    w("| 戦略 | 市場全体の条件 | 年平均件数 | 前半 1トレード平均 / PF | 後半 1トレード平均 / PF | 前半 年率 / 最大下落 | 後半 年率 / 最大下落 | 全期間 年率 / 最大下落 |")
    w("|---|---|---|---|---|---|---|---|")
    filtered = {}
    for name, ent, exn, src in main3:
        for fl, fn in filters:
            tr = opened[name] if fn is None else gen_trades(data, members, ent, exn, STOPS[0], a.start, a.end, fill="open", allow=fn)
            filtered[(name, fl)] = tr
            cells = [pf_line([t for t in tr if lo <= t["in"] <= hi]) for _, lo, hi in halves]
            ports = [port(tr, lo, hi) for _, lo, hi in halves] + [portfolio(tr, COSTS[2], 10, days, data)]
            w(f"| {name} | {fl} | {len(tr) / years:.0f} | {cells[0]} | {cells[1]} | "
              + " | ".join(f"{pct(p['cagr'])} / {pct(p['mdd'])}" for p in ports) + " |")
        print("filters", name, file=sys.stderr)
    w(f"| （参考）SPY買い持ち | | | | | | | {pct(spy_cagr)} / {pct(mdd)} |")

    w("\n## 7. 1トレードのリスクを資金の2%にした場合（翌日の寄り付きで売買、片道0.1%）\n")
    w("コナーズの手法にはストップがないため、リスク2%を決めるには非常時の損切り幅が必要になる。"
      "損切り幅X%なら1銘柄の建玉は資金の 2%÷X%（10%→20%、15%→13.3%、20%→10%）、同時保有数は資金が足りる範囲（X÷2 銘柄）。"
      "損切りは引け値で判定し翌日の寄り付きで手じまうため、窓開けで2%を超えて負けることがある（「1トレードの最大損失」）。"
      "市場全体の条件は「下落局面は買わない＋VIX≦10日線×0.95の日は買わない」。\n")
    w("| 戦略 | 非常時の損切り幅 | 建玉 / 同時保有数 | 年率 | 最大下落率 | 1トレードの最大損失（資金比） | 損切りになった件数 |")
    w("|---|---|---|---|---|---|---|")
    both = filters[3][1]
    for name, ent, exn, src in main3:
        for x in (0.10, 0.15, 0.20):
            tr = gen_trades(data, members, ent, exn, (None, x, None), a.start, a.end, fill="open", allow=both)
            wt, slots = 0.02 / x, int(round(x / 0.02, 6))
            p = portfolio(tr, COSTS[2], slots, days, data, weight=wt)
            cut = sum(1 for t in tr if t["why"] == "損切り")
            w(f"| {name} | {pct(x, 0)} | {pct(wt)} / {slots} | {pct(p['cagr'])} | {pct(p['mdd'])} | {pct(p['worst_hit'], 2)} | {cut} |")
        print("risk2", name, file=sys.stderr)

    # ---- 8: 指数ETF ----
    w("\n## 8. 指数ETF（SPY・QQQ）のルール（片道0.1%）\n")
    w("コナーズの指数・ETF向けのルール（ルール表 p.23, p.24, p.30, p.33）。どれも終値>200日線のときだけ買う。"
      "ポートフォリオは資金を2等分してSPY・QQQに1つずつ割り当て、シグナルがない間は現金（利息なし）。件数が少ないので信頼区間は広い。\n")
    etf_m = {"SPY": [("0000-00-00", "9999-12-31")], "QQQ": [("0000-00-00", "9999-12-31")]}
    etf = {k: prepare(load_prices(a.cache, k)) for k in etf_m}
    vix_up3 = {}
    run = 0
    for d in vix["date"]:
        run = run + 1 if vhi_d(d) else 0
        vix_up3[d] = run >= 3

    def E_cumn(nd, th):
        def f(i, s):
            v = s["rsi2"][i - nd + 1:i + 1]
            return sum(v) if None not in v and sum(v) <= th else None
        return f
    X["RSI(2)≧65"] = lambda i, s, k: s["rsi2"][i] >= 65
    etf_rules = [
        ("2期間RSI≦5・5日線上抜けで手じまい", E_rsi2(5), "5日線上抜け", None, "p.22"),
        ("2日累積RSI≦35・RSI(2)≧65で手じまい", E_cumn(2, 35), "RSI(2)≧65", None, "p.23"),
        ("2日累積RSI≦50・RSI(2)≧65で手じまい", E_cumn(2, 50), "RSI(2)≧65", None, "p.23-24"),
        ("3日累積RSI≦45・RSI(2)≧70で手じまい", E_cumn(3, 45), "RSI(2)≧70", None, "p.33"),
        ("VIXストレッチ（VIX≧10日線×1.05が3日以上）・RSI(2)≧65で手じまい", lambda i, s: 0, "RSI(2)≧65", lambda d: vix_up3.get(d, False), "p.30"),
    ]
    w("| ルール | 出典 | 売買のタイミング | 件数（SPY+QQQ） | 年平均件数 | 勝率 | 1トレード平均（95%区間）/ PF | 平均保有日数 | 年率 | 最大下落率 | 保有している日の割合 |")
    w("|---|---|---|---|---|---|---|---|---|---|---|")
    for name, ent, exn, allow, src in etf_rules:
        for fill, lab in (("close", "当日の引け"), ("open", "翌日の寄り付き")):
            tr = gen_trades(etf, etf_m, ent, exn, STOPS[0], a.start, a.end, fill=fill, allow=allow)
            st = stats(tr, COSTS[2])
            if not st:
                continue
            p = portfolio(tr, COSTS[2], 2, days, etf)
            held = sum(t["days"] for t in tr) / (2 * len(days))
            w(f"| {name} | {src} | {lab} | {st['n']} | {st['n'] / years:.1f} | {pct(st['win'])} | {pf_line(tr)} | {st['days']:.1f} | {pct(p['cagr'])} | {pct(p['mdd'])} | {pct(held, 0)} |")
    w(f"| （参考）SPY買い持ち | | | | | | | | {pct(spy_cagr)} | {pct(mdd)} | 100% |")

    w("\n## 9. 注意\n")
    w("- 過去の成績は将来を保証しない。特に上場廃止銘柄の欠落（生存者バイアスの残り）、引け値ちょうどで約定できる前提（1〜4）、寄り付きの気配値のすべりを入れていないこと（5〜7）は、いずれも現実より良く見せる方向に働きうる。")
    w("- 1シグナル＝1トレードの統計は、同じ日に多数のシグナルが重なる（相場全体の急落時）ため、件数ほど独立ではない。信頼区間は月単位のブロックで補正した。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    open(a.out, "w").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/コナーズ.md")
    r.add_argument("--start", default="2015-01-02")
    r.add_argument("--end", default=dt.date.today().isoformat())
    a = ap.parse_args()
    cmd_run(a)


if __name__ == "__main__":
    main()
