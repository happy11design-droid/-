#!/usr/bin/env python3
"""「強い銘柄が50日線まで押したところを買う」押し目のバックテスト（ユーザーのSNDK 2026-09の売買の考え方をルール化して検証）

使い方:
  tools/backtest_pullback.py run [--out FILE]

ルール（数値はClaudeが置いたもので、本のルール表の値ではない。ユーザーの考え方の検証用）:
  銘柄の条件: ミネルヴィニのトレンドテンプレート8条件（上昇トレンドの強い銘柄）
  押しの日: 安値が50日線の+3%以内まで下げ、終値は50日線の−3%より上（50日線で下げ止まっている）
  仕掛け:
    A. 押しの日の翌日の寄り付きで買う（打診買いに相当）
    B. 押しの日から5日以内に最初の反発の陽線（終値が前日より上かつ始値より上）が出た日の翌日の寄り付きで買う（陽線反発を確認して買う）
  手じまい:
    1. 引けで上のボリンジャーバンド（+2σ）以上 → 翌日の寄り付き（急伸したら利確）
    2. 買値より上で引けた後、最初の陰線（終値が前日より下）→ 翌日の寄り付き（陰線の下落を確認して手じまい）
  損切り: 引けで50日線の−5%を割ったら翌日の寄り付き（押し目が崩れた）、買値の15%下（ユーザー決定）
S&P500全体（その日の構成銘柄、2015〜）と、テーマ監視銘柄（直近3年、後知恵あり）の両方で調べる。
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
from backtest_lib import COSTS, DEFAULT_CACHE, Reporter, gen_trades, load_prices, load_universe, spy_benchmark

RISK, STOP, COST = 0.02, 0.15, COSTS[2]


LOOSE = False   # True: 銘柄の条件を「終値が200日線より上、50日線が200日線より上」に緩める（トレンドテンプレートの52週高値から25%以内などを外す）


def strong(i, s):
    if LOOSE:
        m50, m200 = s["ma50"][i], s["ma200"][i]
        return m50 is not None and m200 is not None and s["c"][i] > m200 and m50 > m200
    return bt.trend_template(s, i)


def touch(i, s):
    m = s["ma50"][i]
    return m is not None and s["l"][i] <= m * 1.03 and s["c"][i] >= m * 0.97 and strong(i, s)


def E_touch(i, s):
    return -(s["rs"][i] or 0) if touch(i, s) else None


def E_reversal(i, s):
    c, o = s["c"], s["o"]
    if i < 2 or not (c[i] > c[i - 1] and c[i] > o[i]):
        return None
    for k in range(i - 1, max(i - 6, 0), -1):
        if touch(k, s):
            return -(s["rs"][i] or 0)
        if c[k] > c[k - 1] and c[k] > o[k]:
            return None       # 押しの後、すでに反発の陽線が出ていた
    return None


def X_band(j, s, k, px):
    return s["pctb"][j] is not None and s["pctb"][j] >= 1.0


def X_first_down(j, s, k, px):
    return s["c"][j] < s["c"][j - 1] and s["c"][j - 1] > px


def with_break(ex):
    return lambda j, s, k, px: ex(j, s, k, px) or (s["ma50"][j] is not None and s["c"][j] < s["ma50"][j] * 0.95)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/50日線の押し目.md")
    a = ap.parse_args()

    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: 50日線の押し目のバックテスト\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_pullback.py\n---\n")
    w("# 強い銘柄が50日線まで押したところを買う（押し目）のバックテスト\n")
    w("ユーザーのSNDK（2026年9月）の売買の考え方（50日線までの押しで打診買い、陽線の反発で追加、急伸後の陰線で手じまい）をルールにして検証した。"
      "数値（50日線の±3%、5日以内、50日線の−5%など）はClaudeが置いたもので、本のルール表の値ではない。\n")
    w("- 銘柄の条件: ミネルヴィニのトレンドテンプレート8条件（【緩めた条件】は、終値が200日線より上かつ50日線が200日線より上だけ）。押しの日: 安値が50日線の+3%以内、終値が50日線の−3%より上。")
    w("- 仕掛けA: 押しの日の翌日の寄り付き（打診買いに相当）。仕掛けB: 押しの後5日以内の最初の反発の陽線の翌日の寄り付き（反発を確認して買う）。")
    w("- 手じまい1: 引けで上のバンド（+2σ）以上の翌日の寄り付き。手じまい2: 買値より上で引けた後の最初の下落の日の翌日の寄り付き。")
    w("- 損切り: 引けで50日線の−5%割れの翌日の寄り付き、または買値の15%下（引け値で判定）。片道0.1%、リスク2%・損切り15%で建玉（13.3%×7銘柄）。\n")

    exits = [("手じまい1（上のバンド）", with_break(X_band)), ("手じまい2（最初の下落）", with_break(X_first_down))]
    entries = [("仕掛けA（押しの日の翌日）", E_touch), ("仕掛けB（反発の陽線の翌日）", E_reversal)]

    # --- S&P500全体（その日の構成銘柄、2015〜） ---
    members, data = load_universe(a.cache, min_bars=260)
    for s in data.values():
        bt.prepare(s)
        bs.prepare(s)
    bt.add_rs_rank(data, members)
    spy = load_prices(a.cache, "SPY")
    start, end = "2015-01-02", dt.date.today().isoformat()
    days = [d for d in spy["date"] if start <= d <= end]
    rep = Reporter(w, data, days, [("前半", start, "2020-12-31"), ("後半", "2021-01-01", end)], len(days) / 252, cost=COST, risk=RISK)
    w("## 1. S&P500全体（その日の構成銘柄、2015年〜。後知恵なし）\n")
    rep.header("RSの高い順")
    global LOOSE
    for loose in (False, True):
        LOOSE = loose
        for en, ef in entries:
            for xn, xf in exits:
                tr = gen_trades(data, members, ef, xf, start, end, ok=bt.liquid, fill="open", max_hold=60, stop_pct=STOP)
                rep.line(("【緩めた条件】" if loose else "") + f"{en}・{xn}", tr, STOP)
    LOOSE = False
    sc, sm = spy_benchmark(spy, days)

    # --- テーマ監視銘柄（直近3年） ---
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
    rep3 = Reporter(w, tdata, days3, [("前半", start3, "2024-12-31"), ("後半", "2025-01-01", end)], len(days3) / 252, cost=COST, risk=RISK)
    w("## 2. テーマ監視銘柄（直近3年。監視銘柄を今の時点で選んでいるため後知恵あり）\n")
    rep3.header("RSの高い順")
    for loose in (False, True):
        LOOSE = loose
        for en, ef in entries:
            for xn, xf in exits:
                tr = gen_trades(tdata, tmem, ef, xf, start3, end, ok=bt.liquid, fill="open", max_hold=60, stop_pct=STOP)
                rep3.line(("【緩めた条件】" if loose else "") + f"{en}・{xn}", tr, STOP)
    LOOSE = False
    # 採用中の2つのルールに、押し目のルールを足した場合（7銘柄の枠を共有）
    w("\n**採用中のルールとの組み合わせ（7銘柄の枠を共有、同じ日の候補はランダムな順）**\n")
    rep3.header("RSの高い順")
    B3 = bs.simulate(tdata, tmem, bs.O_method3, bs.X_upper_band, start3, end)
    M50 = gen_trades(tdata, tmem, bt.E_minervini(50), bt.X_BELOW50, start3, end, ok=bt.liquid, fill="open", max_hold=500, stop_pct=STOP)
    LOOSE = True
    PB = gen_trades(tdata, tmem, E_touch, with_break(X_band), start3, end, ok=bt.liquid, fill="open", max_hold=60, stop_pct=STOP)
    LOOSE = False
    srt = lambda x: sorted(x, key=lambda t: (t["out"], t["sym"]))
    for lab, tr in (("ボリンジャーIII＋ミネルヴィニ（採用中）", B3 + M50),
                    ("ボリンジャーIII＋ミネルヴィニ＋50日線の押し目（【緩めた条件】仕掛けA・手じまい1）", B3 + M50 + PB),
                    ("ミネルヴィニ＋50日線の押し目（ボリンジャーIIIの代わりに押し目）", M50 + PB)):
        rep3.line(lab, srt(tr), STOP)
    w("\n比較（同じ条件の直近3年、`テーマ監視銘柄・直近3年.md`）: ボリンジャーIII 年率43%・最大下落25%、ミネルヴィニ（50日線割れで手じまい）年率28%・最大下落12%、両者の組み合わせ 年率57%・最大下落25%。\n")

    # --- SNDKの2026年9月 ---
    s = tdata.get("SNDK")
    if s:
        w("## 3. SNDK（2026年9月）でこのルールがどう動いたか\n")
        for loose in (False, True):
          LOOSE = loose
          for en, ef in entries:
            for xn, xf in exits:
                tr = [t for t in gen_trades({"SNDK": s}, {"SNDK": tmem["SNDK"]}, ef, xf, "2026-08-15", end, ok=bt.liquid, fill="open",
                                            max_hold=60, stop_pct=STOP)]
                for t in tr:
                    w(f"- {'【緩めた条件】' if loose else ''}{en}・{xn}: 買い {t['in']} {t['px']:.2f} → 売り {t['out']}（{t['why']}） 損益 {t['ret'] * 100:+.1f}%")
        w("")
    w("## 4. 注意\n")
    w("- 数値の置き方（±3%、5日以内、−5%）は1通りしか試していない。前半・後半の両方で成り立つかを重視すること。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
