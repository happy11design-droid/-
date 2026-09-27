#!/usr/bin/env python3
"""Claudeが置いた数値の頑健さの確認: 急落の底（下げ幅・日数）と V2（上抜けの日数・RS・出来高比）の数値を変えて成績を並べる

使い方:
  tools/backtest_sensitivity.py run [--out FILE]

数値を少し変えても成績が同じように良ければ、その数値は「たまたま」ではない。特定の値だけ良ければ、過去のデータに合わせすぎている。
(1) 急落の底: 急落の前（6日前）に50日線＞200日線、直前N日の最高値（終値）から X% 以上下落、RSI(2) ≦ 5。
    X = 10・12・15・20・25%、N = 3・5・10日。手じまいは「引けで20日線以上」と「終値が5日線を上回る（コナーズ）」の2通り。
(2) V2 ベースを待たない新高値: トレンドテンプレート、RS ≧ R、終値が直前N日の最高値（終値）を上回る、上げ下げの出来高比（50日）≧ U。
    N = 10・20・50日、R = 80・90、U = 1.0・1.2・1.3・1.5。手じまいは引けで50日線割れ。
損切りはどれも買値の15%下。片道0.1%、リスク2%・損切り15%で建玉（13.3%×7銘柄）。
"""
import argparse
import csv
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_compare2 as c2
import backtest_crash as bcr
import backtest_theme as bth
import backtest_trend as bt
from backtest_lib import COSTS, DEFAULT_CACHE, Reporter, gen_trades, load_prices, load_universe
from backtest_regime import X_BELOW50

RISK, STOP, COST = 0.02, 0.15, COSTS[2]


def crash(x, n):
    def f(i, s):
        if i <= n:
            return None
        r, r2 = s["c"][i] / max(s["c"][i - n:i]) - 1, s["rsi2"][i]
        return r if r <= -x and r2 is not None and r2 <= 5 and bcr.was_strong(i, s) else None
    return f


def v2(n, rs_min, u):
    def f(i, s):
        if i <= n or s["c"][i] <= max(s["c"][i - n:i]) or (s["rs"][i] or 0) < rs_min:
            return None
        uv = s["udvr"][i]
        if u > 0 and (uv is None or uv < u):
            return None
        return -s["rs"][i] if bt.trend_template(s, i, rs_min=min(70, rs_min)) else None
    return f


def section(w, rep, data, mem, start, end, title):
    w(title)
    g = lambda e, x, mh: gen_trades(data, mem, e, x, start, end, ok=bt.liquid, fill="open", max_hold=mh, stop_pct=STOP)
    w("\n### (1) 急落の底（★が今の形）\n")
    rep.header("下げの大きい順")
    for xn, xf in (("20日線で手じまい", c2.X_MID), ("5日線で手じまい（コナーズ）", c2.X_MA5)):
        for n in (3, 5, 10):
            for x in (0.10, 0.12, 0.15, 0.20, 0.25):
                star = "★" if (n, x) == (5, 0.15) else ""
                rep.line(f"{star}{n}日で−{x * 100:.0f}%・{xn}", g(crash(x, n), xf, 60), STOP)
    w("\n### (2) V2 ベースを待たない新高値（★が今の形。手じまいは50日線割れ）\n")
    rep.header("RSの高い順")
    for n in (10, 20, 50):
        for r in (80, 90):
            for u in (1.0, 1.2, 1.3, 1.5):
                star = "★" if (n, r, u) == (20, 90, 1.3) else ""
                rep.line(f"{star}{n}日の高値・RS≧{r}・出来高比≧{u}", g(v2(n, r, u), X_BELOW50, 500), STOP)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/数値の頑健さの確認.md")
    a = ap.parse_args()
    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: 数値の頑健さの確認\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_sensitivity.py\n---\n")
    w("# Claudeが置いた数値の頑健さの確認（急落の底・V2）\n")
    w(__doc__.split("\n", 5)[5].strip() + "\n")
    members, data = load_universe(a.cache, min_bars=260)
    for s in data.values():
        c2.prep(s)
    spy = load_prices(a.cache, "SPY")
    end = dt.date.today().isoformat()
    wl = bth.load_watchlist()
    tdata = {s: data[s] for s in wl if s in data}
    for s in wl:
        if s not in tdata:
            d = load_prices(a.cache, s)
            if d and len(d["c"]) > 260:
                c2.prep(d)
                tdata[s] = d
    tmem = {s: [("0000-00-00", "9999-12-31")] for s in tdata}
    sp_now = [r["ticker"] for r in csv.DictReader(open(os.path.join(a.cache, "members.csv"))) if not r["end_date"]]
    bth.rs_ranks(a.cache, sorted(set(sp_now) | set(tdata)), tdata)
    today = dt.date.today()
    start3 = today.replace(year=today.year - 3).isoformat()
    days3 = [d for d in spy["date"] if start3 <= d <= end]
    rep3 = Reporter(w, tdata, days3, [("前半", start3, "2024-12-31"), ("後半", "2025-01-01", end)], len(days3) / 252, cost=COST, risk=RISK)
    section(w, rep3, tdata, tmem, start3, end, f"## 1. テーマ監視銘柄（今の{len(tdata)}銘柄、直近3年。今の時点で選んでいるため後知恵あり）\n")
    bt.add_rs_rank(data, members)
    start = "2015-01-02"
    days = [d for d in spy["date"] if start <= d <= end]
    rep = Reporter(w, data, days, [("前半", start, "2020-12-31"), ("後半", "2021-01-01", end)], len(days) / 252, cost=COST, risk=RISK)
    section(w, rep, data, members, start, end, "\n## 2. S&P500の構成銘柄（その日の構成銘柄、2015年〜。後知恵なし）\n")
    w("\n## 3. 注意\n")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
