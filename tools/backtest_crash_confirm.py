#!/usr/bin/env python3
"""急落の底: 著者6人の共通点に沿った「確認してから買う」形と、今の形（確認なし）の比較

使い方:
  tools/backtest_crash_confirm.py run [--out FILE]

著者の回答（`バックテスト結果/急落の底_著者の見解.md`）: 6冊とも「落ちている途中では買わず、下げ止まり・反発を確認してから買う」。
その共通点を数値にした形（数値はClaudeが置いたもの）:
  場面（setup）: 上昇トレンド（終値＞200日線、または50日線が20日前より上）の銘柄が、終値がボリンジャーバンド−2σより下、またはRSI(14)≦30
  確認（setup の日から5日以内。setup と同じ日でもよい）: 次のどれか
    H 下ヒゲ: 下ヒゲが実体の2倍以上、終値が値幅の上半分（ちょる子・株価チャート分析）
    E 陽の抱き線: 前日が陰線、当日が陽線で前日の実体を包む（ちょる子・株価チャート分析）
    U 前日の高値を上回る陽線（反発の陽線の確定。株価チャート分析・マット）
    ANY 上のどれか
  買い: 確認の翌日の寄り付き。損切り: 確認した足の安値（寄り付きがそれより下なら買値の10%下を上限。新高値ブレイク投資術・株価チャート分析の最大−10%）
  恐怖指数: VIX＞25 の日の場面だけに絞る場合も比べる（おーちゃん）
手じまい: 終値が5日線を上回る（コナーズ、今のルール）／引けで20日線以上
比較: 今の形（5日で−15%・RSI(2)≦5・確認なし、損切り15%、5日線で手じまい）
対象: (1) 今の監視銘柄（直近3年、後知恵あり）、(2) 後知恵なしの監視銘柄（毎週選び直す、直近3年と2015年〜）
"""
import argparse
import datetime as dt
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_compare2 as c2
import backtest_crash as bcr
import backtest_minervini2 as bm2
import backtest_rotation as br
import backtest_swing as bs
import backtest_theme as bth
import backtest_trend as bt
from backtest_lib import COSTS, DEFAULT_CACHE, Reporter, gen_trades, load_prices, load_universe, rsi_wilder
from backtest_regime import X_BELOW50, freq_table, srt, to_sim

RISK, STOP, COST = 0.02, 0.15, COSTS[2]
VIX = {}


def prep(s):
    c2.prep(s)
    s["rsi14"] = rsi_wilder(s["c"], 14)


def setup(k, s, vix=False):
    if k < 21:
        return False
    c, m200, m50, m50p = s["c"][k], s["ma200"][k], s["ma50"][k], s["ma50"][k - 20]
    trend = (m200 is not None and c > m200) or (m50 is not None and m50p is not None and m50 > m50p)
    over = (s["bb_dn"][k] is not None and c < s["bb_dn"][k]) or (s["rsi14"][k] is not None and s["rsi14"][k] <= 30)
    return trend and over and (not vix or VIX.get(s["date"][k], 0) > 25)


def hammer(i, s):
    o, h, l, c = s["o"][i], s["h"][i], s["l"][i], s["c"][i]
    r = h - l
    return r > 0 and (min(o, c) - l) >= 2 * max(abs(c - o), 1e-9) and (c - l) / r >= 0.5


def engulf(i, s):
    return s["c"][i - 1] < s["o"][i - 1] and s["c"][i] > s["o"][i] and s["o"][i] <= s["c"][i - 1] and s["c"][i] >= s["o"][i - 1]


def upday(i, s):
    return s["c"][i] > s["o"][i] and s["c"][i] > s["h"][i - 1]


CONF = {"H 下ヒゲ": [hammer], "E 陽の抱き線": [engulf], "U 前日の高値を上回る陽線": [upday], "ANY どれか": [hammer, engulf, upday]}


def order(conf, vix, candle_stop=True):
    fs = CONF[conf]

    def f(i, s):
        if i < 22 or not any(g(i, s) for g in fs):
            return None
        if not any(setup(k, s, vix) for k in range(i - 5, i + 1)):
            return None
        return {"rank": s["rsi14"][i] or 50, "kind": "open", "stop": s["l"][i] if candle_stop else None}
    return f


def run_set(w, rep, data, mem, lo, end, ok, title):
    w(title)
    rep.header("RSI(14)の低い順")
    res = {}
    cur = gen_trades(data, mem, bcr.C3, c2.X_MA5, lo, end, ok=ok, fill="open", max_hold=60, stop_pct=STOP)
    res["今の形（5日で−15%・RSI(2)≦5・確認なし・5日線）"] = cur
    rep.line("今の形（5日で−15%・RSI(2)≦5・確認なし・損切り15%・5日線で手じまい）", cur, STOP)
    bs.STOP_MAX = 0.10   # 確認型の損切りは、確認した足の安値。ただし買値の10%下を上限
    for xn, xf in (("5日線", c2.X_MA5), ("20日線", c2.X_MID)):
        for vix in (False, True):
            for cn in CONF:
                t = bs.simulate(data, mem, order(cn, vix), to_sim(xf), lo, end, ok=ok, max_hold=60)
                lab = f"確認型 {cn}{'・VIX>25' if vix else ''}・{xn}で手じまい"
                res[lab] = t
                rep.line(lab, t, STOP)   # 建玉は今の形と同じ（13.3%×7銘柄）にそろえて比べる
    # 追加: 確認の足ですぐ手じまい・損切りにならないよう、損切りを買値の10%下に固定し、手じまいを20日線・上のバンドにした形
    w("\n**追加: 損切りを買値の10%下に固定（確認した足の安値にしない）した確認型**\n")
    rep.header("RSI(14)の低い順")
    for xn, xf in (("20日線", c2.X_MID), ("上のバンド", lambda j, s, k, px: s["pctb"][j] is not None and s["pctb"][j] >= 1.0)):
        for vix in (False, True):
            for cn in ("H 下ヒゲ", "ANY どれか"):
                t = bs.simulate(data, mem, order(cn, vix, candle_stop=False), to_sim(xf), lo, end, ok=ok, max_hold=60)
                lab = f"確認型（損切り10%固定） {cn}{'・VIX>25' if vix else ''}・{xn}で手じまい"
                res[lab] = t
                rep.line(lab, t, STOP)
    bs.STOP_MAX = 0.15
    return res


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/急落の底_確認してから買う.md")
    a = ap.parse_args()
    v = load_prices(a.cache, "^VIX")
    VIX.update(zip(v["date"], v["c"]))
    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: 急落の底 確認してから買う形\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_crash_confirm.py\n---\n")
    w("# 急落の底: 著者の共通点に沿った「確認してから買う」形と、今の形の比較\n")
    w(__doc__.split("\n", 5)[5].strip() + "\n")
    w("建玉はすべて同じ（1銘柄に資金の13.3%、同時に7銘柄まで）。確認型は損切りが浅い（確認した足の安値、最大10%）ので、1トレードのリスクは2%より小さい。片道0.1%。\n")
    members, data = load_universe(a.cache, min_bars=260)
    for s, d in data.items():
        prep(d)
        d["sym"] = s
    bt.add_rs_rank(data, members)
    spy = load_prices(a.cache, "SPY")
    end = dt.date.today().isoformat()
    today = dt.date.today()
    start3 = today.replace(year=today.year - 3).isoformat()
    days_all = [d for d in spy["date"] if "2015-01-02" <= d <= end]

    # (1) 今の監視銘柄
    wl = bth.load_watchlist()
    tdata = {s: data[s] for s in wl if s in data}
    for s in wl:
        if s not in tdata:
            d = load_prices(a.cache, s)
            if d and len(d["c"]) > 260:
                prep(d)
                d["sym"] = s
                tdata[s] = d
    tmem = {s: [("0000-00-00", "9999-12-31")] for s in tdata}
    import csv
    sp_now = [r["ticker"] for r in csv.DictReader(open(os.path.join(a.cache, "members.csv"))) if not r["end_date"]]
    days3 = [d for d in days_all if d >= start3]
    rep = Reporter(w, tdata, days3, [("前半", start3, "2024-12-31"), ("後半", "2025-01-01", end)], len(days3) / 252, cost=COST, risk=RISK)
    run_set(w, rep, tdata, tmem, start3, end, bt.liquid, f"## 1. 今の監視銘柄（{len(tdata)}銘柄、直近3年。後知恵あり）\n")

    # (2) 後知恵なしの監視銘柄
    u = json.load(open(os.path.join(a.cache, "universe.json")))
    ex = os.path.join(a.cache, "industry_extra.json")
    if os.path.exists(ex):
        u.update(json.load(open(ex)))
    ind = {s: (u.get(s) or {}).get("industry") for s in data}
    fridays = [d for k, d in enumerate(days_all) if k + 1 == len(days_all) or dt.date.fromisoformat(days_all[k + 1]).isocalendar()[1] != dt.date.fromisoformat(d).isocalendar()[1]]
    lists = br.build_lists(data, members, fridays, ind)
    week_of, fi, last = {}, 0, None
    for d in days_all:
        while fi < len(fridays) and fridays[fi] < d:
            last = fridays[fi]
            fi += 1
        week_of[d] = lists.get(last, frozenset())
    ok_rot = lambda s, i, spans: bt.liquid(s, i, spans) and s["sym"] in week_of.get(s["date"][i], ())
    for lab, lo, mid in (("直近3年", start3, "2024-12-31"), ("2015年〜", "2015-01-02", "2020-12-31")):
        dd = [d for d in days_all if d >= lo]
        rep = Reporter(w, data, dd, [("前半", lo, mid), ("後半", (dt.date.fromisoformat(mid) + dt.timedelta(days=1)).isoformat(), end)],
                       len(dd) / 252, cost=COST, risk=RISK)
        run_set(w, rep, data, members, lo, end, ok_rot, f"\n## 2. 後知恵なしの監視銘柄（{lab}）\n")
    w("\n## 注意\n")
    w("- 確認の形・場面の数値はClaudeが著者の回答を数値にしたもので、著者の値そのものではない（本は下落率やRSI(2)を定めていない）。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
