#!/usr/bin/env python3
"""ローソク足と出来高の形（需要の戻り）を仕掛けにしたバックテストと、ボリンジャーIIIの局面別の成績

使い方:
  tools/backtest_candle.py run [--out FILE] [--skip-sp500]

ユーザーの問題提起（2026-09-27）: 採用ルールにローソク足・出来高（プロの買いの痕跡）・下落相場が入っていない。
SNDKの2026-09の反発（出来高の少ない押しの後の大陽線）のような形を、数値のルールにして後知恵なしで検証する。
数値はClaudeが置いたもので、本のルール表の値ではない（SNDKを見た後に作ったので、SNDKに合いすぎている可能性がある。
判定は後知恵なしのS&P500全体（2015〜）を重視する）。

仕掛け（すべて引け後に判定し、翌日の寄り付きで買う）:
  共通の銘柄の条件（強い銘柄）: 終値 > 200日線、50日線 > 200日線
  押し: 前日の終値が直前20日の高値より10%以上下、または前日の%b < 0.2
  出来高の減少: 直前5日の平均出来高 < 50日平均の0.8倍（売りが細っている）
  E1 大陽線の反発: 強い銘柄・押し・出来高の減少 ＋ 当日が大陽線（前日比+3%以上、実体が値幅の60%以上、高値寄りで引け＝値幅の上位20%）
  E2 包み足: 強い銘柄・押し ＋ 前日が陰線、当日が陽線で前日の実体を包む
  E3 下ひげ（ハンマー）: 強い銘柄 ＋ %b < 0.2 ＋ 下ひげが実体の2倍以上、値幅の上半分で引け、安値が直前10日の安値以下
  E4 ポケットピボット: 強い銘柄 ＋ 終値が50日線より上かつ50日線の+10%以内 ＋ 上げた日の出来高が直前10日の下げた日の最大出来高を上回る
  E5 窓を空けた急騰: 寄り付きが前日終値の+4%以上、出来高が50日平均の2倍以上、値幅の上半分で引け
手じまい: 引けで上のバンド以上／20日線割れ／50日線割れ の翌日の寄り付き。損切りは買値の15%下。
"""
import argparse
import csv
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_swing as bs
import backtest_theme as bth
import backtest_trend as bt
from backtest_lib import COSTS, DEFAULT_CACHE, Reporter, gen_trades, load_prices, load_universe, market_regime, spy_benchmark, stats
from backtest_regime import X_BAND, X_BELOW20, X_BELOW50, freq_table, srt

RISK, STOP, COST = 0.02, 0.15, COSTS[2]


def strong(i, s):
    m50, m200 = s["ma50"][i], s["ma200"][i]
    return m50 is not None and m200 is not None and s["c"][i] > m200 and m50 > m200


def pulled(i, s):
    if i < 21:
        return False
    hi20 = max(s["h"][i - 21:i - 1])
    pb = s["pctb"][i - 1]
    return s["c"][i - 1] <= hi20 * 0.9 or (pb is not None and pb < 0.2)


def dry(i, s):
    v50 = s["vol50"][i]
    return v50 is not None and sum(s["v"][i - 5:i]) / 5 < 0.8 * v50


def big_bull(i, s):
    o, h, l, c = s["o"][i], s["h"][i], s["l"][i], s["c"][i]
    r = h - l
    return r > 0 and c >= s["c"][i - 1] * 1.03 and (c - o) / r >= 0.6 and (c - l) / r >= 0.8


def E1(i, s):
    return -(s["c"][i] / s["c"][i - 1]) if strong(i, s) and pulled(i, s) and dry(i, s) and big_bull(i, s) else None


def E2(i, s):
    o, c, o1, c1 = s["o"][i], s["c"][i], s["o"][i - 1], s["c"][i - 1]
    ok = c1 < o1 and c > o and o <= c1 and c >= o1
    return -(c / c1) if ok and strong(i, s) and pulled(i, s) else None


def E3(i, s):
    o, h, l, c = s["o"][i], s["h"][i], s["l"][i], s["c"][i]
    r, body = h - l, abs(c - o)
    pb = s["pctb"][i]
    if r <= 0 or pb is None or pb >= 0.2 or not strong(i, s):
        return None
    ok = (min(o, c) - l) >= 2 * max(body, 1e-9) and (c - l) / r >= 0.5 and l <= min(s["l"][i - 10:i])
    return pb if ok else None


def E4(i, s):
    c, m50 = s["c"][i], s["ma50"][i]
    if m50 is None or not strong(i, s) or not (m50 < c <= m50 * 1.10) or c <= s["c"][i - 1]:
        return None
    downs = [s["v"][k] for k in range(i - 10, i) if s["c"][k] < s["c"][k - 1]]
    return -(s["v"][i] / s["vol50"][i]) if downs and s["v"][i] > max(downs) else None


def E5(i, s):
    o, h, l, c, v50 = s["o"][i], s["h"][i], s["l"][i], s["c"][i], s["vol50"][i]
    r = h - l
    ok = v50 and r > 0 and o >= s["c"][i - 1] * 1.04 and s["v"][i] >= 2 * v50 and (c - l) / r >= 0.5
    return -(s["v"][i] / v50) if ok else None


ENTRIES = [
    ("E1 大陽線の反発（強い銘柄・押し・出来高の減少の後）", E1),
    ("E2 包み足（強い銘柄・押しの後）", E2),
    ("E3 下ひげ（強い銘柄・%b<0.2）", E3),
    ("E4 ポケットピボット（強い銘柄・50日線の近く）", E4),
    ("E5 窓を空けた急騰（出来高2倍）", E5),
]
EXITS = [("上のバンド", X_BAND), ("20日線割れ", X_BELOW20), ("50日線割れ", X_BELOW50)]


def stock_regime(i, s):
    c, m50, m200 = s["c"][i], s["ma50"][i], s["ma200"][i]
    if m50 is None or m200 is None:
        return "判定不能"
    if c > m50 > m200:
        return "上昇"
    if c < m50 < m200:
        return "下落"
    return "横ばい"


def regime_split(w, name, tr, data, mreg):
    """ボリンジャーIIIのトレードを、仕掛けた前日（シグナルの日）の市場の局面・銘柄の局面で分ける"""
    w(f"\n**{name}: 局面別（1トレード＝1件）**\n")
    w("| 分け方 | 局面 | 件数 | 勝率 | 1トレード平均（95%区間） | PF |")
    w("|---|---|---|---|---|---|")
    for label, f in (("市場（SPYの30週線）", lambda t, s, i: mreg.get(s["date"][i], "判定不能")),
                     ("銘柄（終値・50日線・200日線の並び）", lambda t, s, i: stock_regime(i, s))):
        groups = {}
        for t in tr:
            s = data[t["sym"]]
            i = s["date"].index(t["in"]) - 1
            groups.setdefault(f(t, s, i), []).append(t)
        for k in ("上昇", "横ばい", "下落"):
            st = stats(groups.get(k, []), COST)
            if st:
                w(f"| {label} | {k} | {st['n']} | {st['win'] * 100:.1f}% | {st['mean'] * 100:.2f}%（{st['mean_ci'][0] * 100:.2f}%〜{st['mean_ci'][1] * 100:.2f}%） | {st['pf']:.2f} |")


def section(w, rep, data, mem, start, end, days, years, title, mreg):
    w(title)
    g = lambda e, x: gen_trades(data, mem, e, x, start, end, ok=bt.liquid, fill="open", max_hold=120, stop_pct=STOP)
    res = {}
    rep.header("シグナルの強い順")
    for en, ef in ENTRIES:
        for xn, xf in EXITS:
            tr = g(ef, xf)
            res[(en, xn)] = tr
            rep.line(f"{en}・{xn}", tr, STOP)
    b3 = bs.simulate(data, mem, bs.O_method3, bs.X_upper_band, start, end)
    m50 = gen_trades(data, mem, bt.E_minervini(50), X_BELOW50, start, end, ok=bt.liquid, fill="open", max_hold=500, stop_pct=STOP)
    regime_split(w, "ボリンジャーIII（上のバンドで手じまい）", b3, data, mreg)
    for en, ef in ENTRIES[:1]:
        regime_split(w, f"{en}・上のバンド", res[(en, "上のバンド")], data, mreg)
    w("\n**採用中のルールとの組み合わせ（7銘柄の枠を共有）**\n")
    combos = [("採用中: ボリンジャーIII＋ミネルヴィニ", srt(b3 + m50))]
    for en, _ in ENTRIES:
        best = max(EXITS, key=lambda x: (stats(res[(en, x[0])], COST) or {"pf": 0})["pf"])[0]
        combos.append((f"採用中＋{en}・{best}", srt(b3 + m50 + res[(en, best)])))
    rep.header("シグナルの強い順")
    for lab, tr in combos:
        rep.line(lab, tr, STOP)
    w("")
    freq_table(w, rep, combos, days, years)
    return res


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/ローソク足と出来高.md")
    r.add_argument("--skip-sp500", action="store_true")
    a = ap.parse_args()

    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: ローソク足と出来高の形のバックテスト\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_candle.py\n---\n")
    w("# ローソク足と出来高の形（需要の戻り）を仕掛けにしたバックテスト\n")
    w(__doc__.split("\n", 4)[4].replace("\n  ", "\n- ").strip() + "\n")

    members, data = load_universe(a.cache, min_bars=260)
    for s in data.values():
        bt.prepare(s)
        bs.prepare(s)
    spy = load_prices(a.cache, "SPY")
    mreg = market_regime(spy)
    end = dt.date.today().isoformat()

    wl = bth.load_watchlist()
    tdata = {s: data[s] for s in wl if s in data}
    for s in wl:
        if s not in tdata:
            d = load_prices(a.cache, s)
            if d and len(d["c"]) > 260:
                bt.prepare(d)
                bs.prepare(d)
                tdata[s] = d
    tmem = {s: [("0000-00-00", "9999-12-31")] for s in tdata}
    sp_now = [r["ticker"] for r in csv.DictReader(open(os.path.join(a.cache, "members.csv"))) if not r["end_date"]]
    bth.rs_ranks(a.cache, sorted(set(sp_now) | set(tdata)), tdata)
    today = dt.date.today()
    start3 = today.replace(year=today.year - 3).isoformat()
    days3 = [d for d in spy["date"] if start3 <= d <= end]
    y3 = len(days3) / 252
    rep3 = Reporter(w, tdata, days3, [("前半", start3, "2024-12-31"), ("後半", "2025-01-01", end)], y3, cost=COST, risk=RISK)
    res3 = section(w, rep3, tdata, tmem, start3, end, days3, y3,
                   "## 1. テーマ監視銘柄（直近3年。監視銘柄を今の時点で選んでいるため後知恵あり）\n", mreg)

    w("\n## 2. SNDK（2026年8〜9月）での各ルールの売買\n")
    for (en, xn), tr in res3.items():
        for t in tr:
            if t["sym"] == "SNDK" and t["in"] >= "2026-08-01":
                w(f"- {en}・{xn}: 買い {t['in']} {t['px']:.2f} → 売り {t['out']}（{t['why']}） 損益 {t['ret'] * 100:+.1f}%")
    w("")

    if not a.skip_sp500:
        bt.add_rs_rank(data, members)
        start = "2015-01-02"
        days = [d for d in spy["date"] if start <= d <= end]
        y = len(days) / 252
        rep = Reporter(w, data, days, [("前半", start, "2020-12-31"), ("後半", "2021-01-01", end)], y, cost=COST, risk=RISK)
        section(w, rep, data, members, start, end, days, y, "\n## 3. S&P500全体（その日の構成銘柄、2015年〜。後知恵なし）\n", mreg)
        sc, sm = spy_benchmark(spy, days)

    w("## 4. 注意\n")
    w("- 形の数値（+3%、実体60%、出来高0.8倍など）は1通りしか試していない。SNDKを見た後に作ったため、後知恵なしのS&P500全体の成績と前半・後半の安定を重視すること。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
