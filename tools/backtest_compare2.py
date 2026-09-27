#!/usr/bin/env python3
"""(1) 急落の底: コナーズの本どおりの形と、今の形（5日で−15%）の比較
   (2) 一直線に上がる銘柄を取る方式: 出来高の条件を「上げた日と下げた日の出来高の比」に替える方式と、リーダーの押し目の比較

使い方:
  tools/backtest_compare2.py run [--out FILE]

(1) 急落の底（損切りはどれも買値の15%下。コナーズの本は損切りを置かないが、ユーザーの資金管理に合わせる）
  K1 コナーズの本どおり: 終値 > 200日線 かつ RSI(2) ≦ 5 → 終値が5日線を上回ったら手じまい（ルール表 p.22, p.45）
  K2 今の形: 急落の前（6日前）に50日線＞200日線、直前5日の最高値から−15%以上、RSI(2) ≦ 5 → 引けで20日線以上で手じまい
  K3 今の入口＋コナーズの手じまい: K2 の入口 → 終値が5日線を上回ったら手じまい
  K4 コナーズの入口＋今の手じまい: K1 の入口 → 引けで20日線以上で手じまい
(2) 一直線に上がる銘柄（手じまいはどれも引けで50日線割れ、損切り15%）
  M  今のミネルヴィニ: トレンドテンプレート、ベース（最高値から3週以上・調整幅35%以内）の上抜け、出来高が50日平均の2倍以上
  V1 出来高の条件を替える: M の「出来高2倍」を「直近50日の上げた日の出来高÷下げた日の出来高 ≧ 1.3」（機関投資家の買い集め。オニールの考え方を数値にしたもの）に替える
  V2 ベースを待たない新高値: トレンドテンプレート、RS≧90、終値が直前20日の最高値（終値）を上回る、上げ下げの出来高比 ≧ 1.3
  L4 リーダーの押し目: RS≧90・終値>200日線・50日線>200日線、前日の安値が20日線の+1%以内、当日が陽線かつ前日より高く引け
  L4V L4 に 上げ下げの出来高比 ≧ 1.3 を足す
数値（1.3、20日、+1%）はClaudeが置いたもので、本のルール表の値ではない。
"""
import argparse
import csv
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_connors as bc
import backtest_crash as bcr
import backtest_leaders as bl
import backtest_minervini2 as bm2
import backtest_swing as bs
import backtest_theme as bth
import backtest_trend as bt
from backtest_lib import COSTS, DEFAULT_CACHE, Reporter, gen_trades, load_prices, load_universe, market_regime, stats
from backtest_regime import X_BELOW50, freq_table, srt

RISK, STOP, COST = 0.02, 0.15, COSTS[2]


def prep(s):
    bt.prepare(s)
    bs.prepare(s)
    bc.prepare(s)
    bm2.add_pivot(s)
    c, v, n = s["c"], s["v"], len(s["c"])
    up = [v[i] if i and c[i] > c[i - 1] else 0 for i in range(n)]
    dn = [v[i] if i and c[i] < c[i - 1] else 0 for i in range(n)]
    s["udvr"] = [None] * n
    su = sd = 0.0
    for i in range(n):
        su += up[i]
        sd += dn[i]
        if i >= 50:
            su -= up[i - 50]
            sd -= dn[i - 50]
        if i >= 50 and sd > 0:
            s["udvr"][i] = su / sd
    s["hi20c"] = [max(c[i - 20:i]) if i >= 20 else None for i in range(n)]


# ---- (1) 急落の底 ----
def K1(i, s):
    m, r = s["ma200"][i], s["rsi2"][i]
    return r if m is not None and r is not None and s["c"][i] > m and r <= 5 else None


X_MA5 = lambda j, s, k, px: s["ma5"][j] is not None and s["c"][j] > s["ma5"][j]
X_MID = lambda j, s, k, px: s["bb_mid"][j] is not None and s["c"][j] >= s["bb_mid"][j]
CRASH = [("K1 コナーズの本どおり（200日線より上・RSI(2)≦5・5日線を上回ったら手じまい）", K1, X_MA5),
         ("K2 今の形（5日で−15%・RSI(2)≦5・20日線で手じまい）", bcr.C3, X_MID),
         ("K3 今の入口＋コナーズの手じまい（5日線）", bcr.C3, X_MA5),
         ("K4 コナーズの入口＋今の手じまい（20日線）", K1, X_MID)]


# ---- (2) 一直線に上がる銘柄 ----
def udvr_ok(i, s, th=1.3):
    u = s["udvr"][i]
    return u is not None and u >= th


def V1(i, s):
    kh = s["piv_i"][i]
    if kh is None or i + 1 >= len(s["c"]) or i - kh < 15:
        return None
    piv = s["h"][kh]
    if s["c"][i] <= piv or s["o"][i + 1] > piv * 1.03 or (piv - min(s["l"][kh:i])) / piv > 0.35:
        return None
    return -s["rs"][i] if udvr_ok(i, s) and bt.trend_template(s, i) else None


def V2(i, s):
    h = s["hi20c"][i]
    if h is None or s["c"][i] <= h or not udvr_ok(i, s) or not bt.trend_template(s, i) or (s["rs"][i] or 0) < 90:
        return None
    return -s["rs"][i]


def L4V(i, s):
    return bl.L4(i, s) if udvr_ok(i, s) else None


TREND = [("M 今のミネルヴィニ（ベース3週以上・出来高2倍）", bm2.E_base(2.0)),
         ("V1 ミネルヴィニの出来高2倍を上げ下げの出来高比≧1.3に替える", V1),
         ("V2 ベースを待たない新高値（RS≧90・出来高比≧1.3）", V2),
         ("L4 リーダーの押し目（20日線の押しからの陽線）", bl.L4),
         ("L4V リーダーの押し目＋出来高比≧1.3", L4V)]


def section(w, rep, data, mem, start, end, days, years, title, show=()):
    w(title)
    g = lambda e, x, mh: gen_trades(data, mem, e, x, start, end, ok=bt.liquid, fill="open", max_hold=mh, stop_pct=STOP)
    w("\n### (1) 急落の底\n")
    rep.header("RSI(2)の低い順")
    cr = {}
    for n, e, x in CRASH:
        cr[n] = g(e, x, 60)
        rep.line(n, cr[n], STOP)
    w("\n### (2) 一直線に上がる銘柄を取る方式（手じまいは50日線割れ）\n")
    rep.header("RSの高い順")
    tr = {}
    for n, e in TREND:
        tr[n] = g(e, X_BELOW50, 500)
        rep.line(n, tr[n], STOP)
    b3 = bs.simulate(data, mem, bs.O_method3, bs.X_upper_band, start, end)
    now = srt(b3 + tr[TREND[0][0]] + cr[CRASH[1][0]])
    combos = [("今の採用ルール: ボリンジャーIII＋ミネルヴィニ（M）＋急落の底（K2）", now)]
    combos += [(f"ボリンジャーIII＋M＋{n.split(' ')[0]}（急落の底を替える）", srt(b3 + tr[TREND[0][0]] + cr[n])) for n, _, _ in (CRASH[0], CRASH[2], CRASH[3])]
    combos += [(f"今の採用ルール＋{n.split(' ')[0]}", srt(now + tr[n])) for n, _ in TREND[1:]]
    combos += [(f"ボリンジャーIII＋K2＋{n.split(' ')[0]}（ミネルヴィニを替える）", srt(b3 + cr[CRASH[1][0]] + tr[n])) for n, _ in TREND[1:3]]
    w("\n### 組み合わせ（7銘柄の枠を共有）\n")
    rep.header("RSの高い順")
    for lab, t in combos:
        rep.line(lab, t, STOP)
    w("")
    freq_table(w, rep, combos, days, years)
    for sym in show:
        w(f"\n**{sym}（直近6カ月）**\n")
        for n, t in list(cr.items()) + list(tr.items()):
            xs = [x for x in t if x["sym"] == sym and x["in"] >= "2026-03-27"]
            if xs:
                w(f"- {n.split(' ')[0]}: " + "、".join(f"{x['in']} {x['px']:.2f}→{x['out']} {x['ret'] * 100:+.1f}%" for x in xs))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/急落の底と一直線の上昇の比較.md")
    a = ap.parse_args()
    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: 急落の底と一直線の上昇の比較\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_compare2.py\n---\n")
    w("# 急落の底（コナーズの本どおり vs 今の形）と、一直線に上がる銘柄を取る方式の比較\n")
    w(__doc__.split("\n", 5)[5].strip() + "\n")
    w("片道0.1%、リスク2%・損切り15%で建玉（13.3%×7銘柄）。データの最終日に保有中の売買は数えない。\n")
    members, data = load_universe(a.cache, min_bars=260)
    for s in data.values():
        prep(s)
    spy = load_prices(a.cache, "SPY")
    end = dt.date.today().isoformat()
    wl = bth.load_watchlist()
    tdata = {s: data[s] for s in wl if s in data}
    for s in wl:
        if s not in tdata:
            d = load_prices(a.cache, s)
            if d and len(d["c"]) > 260:
                prep(d)
                tdata[s] = d
    tmem = {s: [("0000-00-00", "9999-12-31")] for s in tdata}
    sp_now = [r["ticker"] for r in csv.DictReader(open(os.path.join(a.cache, "members.csv"))) if not r["end_date"]]
    bth.rs_ranks(a.cache, sorted(set(sp_now) | set(tdata)), tdata)
    today = dt.date.today()
    start3 = today.replace(year=today.year - 3).isoformat()
    days3 = [d for d in spy["date"] if start3 <= d <= end]
    y3 = len(days3) / 252
    rep3 = Reporter(w, tdata, days3, [("前半", start3, "2024-12-31"), ("後半", "2025-01-01", end)], y3, cost=COST, risk=RISK)
    section(w, rep3, tdata, tmem, start3, end, days3, y3,
            "## 1. テーマ監視銘柄（直近3年。監視銘柄を今の時点で選んでいるため後知恵あり）\n", show=("SNDK", "DELL"))
    bt.add_rs_rank(data, members)
    start = "2015-01-02"
    days = [d for d in spy["date"] if start <= d <= end]
    y = len(days) / 252
    rep = Reporter(w, data, days, [("前半", start, "2020-12-31"), ("後半", "2021-01-01", end)], y, cost=COST, risk=RISK)
    section(w, rep, data, members, start, end, days, y, "\n## 2. S&P500の構成銘柄（その日の構成銘柄、2015年〜。後知恵なし）\n")
    w("\n## 3. 注意\n")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
