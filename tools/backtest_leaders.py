#!/usr/bin/env python3
"""強い銘柄（リーダー）を押し目・反発・上抜けの予約注文で買い、トレンドが崩れるまで持つ型のバックテスト

使い方:
  tools/backtest_leaders.py run [--out FILE]

狙い: SNDK（2026年3〜9月 +196%）のように高値を更新し続ける銘柄は、ベースの上抜けを待つ型では買えず、
上のバンドで手じまう型では上昇の一部しか取れない。強い銘柄を押し目や反発で買い、50日線を割るまで持つ型を検証する。
数値はClaudeが置いたもので、本のルール表の値ではない（ミネルヴィニの予約注文型のみ、ルール表のベースの定義を使う）。

リーダーの条件: RSランキング ≧ 90、終値 > 200日線、50日線 > 200日線
仕掛け（L1〜L4 は引け後に判定し翌日の寄り付きで買う。L5 は予約注文）:
  L1 大陽線の反発: リーダー・押し・出来高の減少の後の大陽線（backtest_candle.E1 と同じ形）
  L2 包み足: リーダー・押しの後の包み足
  L3 50日線の押し: リーダーで、安値が50日線の+3%以内、終値が50日線の−3%より上
  L4 20日線の押しからの陽線: リーダーで、前日の安値が20日線の+1%以内、当日が陽線かつ前日より高く引け
  L5 ピボットへの逆指値買い（予約注文）: トレンドテンプレート、ベース（最高値から3週以上、調整幅≦35%）、終値がピボットの−5%以内
     → 翌日、高値がピボット以上なら max(始値, ピボット) で買い（出来高の条件は事前に分からないので付けない）
手じまい: 50日線割れ／20日線割れ／上のバンド（比較）。損切りは買値の15%下。
"""
import argparse
import csv
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_candle as bcd
import backtest_minervini2 as bm2
import backtest_swing as bs
import backtest_theme as bth
import backtest_trend as bt
from backtest_lib import COSTS, DEFAULT_CACHE, Reporter, gen_trades, load_prices, load_universe, spy_benchmark, stats
from backtest_regime import X_BAND, X_BELOW20, X_BELOW50, freq_table, srt, to_sim

RISK, STOP, COST = 0.02, 0.15, COSTS[2]


def leader(i, s, rs_min=90):
    r, m50, m200 = s["rs"][i], s["ma50"][i], s["ma200"][i]
    return r is not None and r >= rs_min and m50 is not None and m200 is not None and s["c"][i] > m200 and m50 > m200


def L1(i, s):
    return -s["rs"][i] if leader(i, s) and bcd.pulled(i, s) and bcd.dry(i, s) and bcd.big_bull(i, s) else None


def L2(i, s):
    return -s["rs"][i] if leader(i, s) and bcd.E2(i, s) is not None else None


def L3(i, s):
    m = s["ma50"][i]
    return -s["rs"][i] if leader(i, s) and m and s["l"][i] <= m * 1.03 and s["c"][i] >= m * 0.97 else None


def L4(i, s):
    m1 = s["bb_mid"][i - 1]
    ok = m1 and s["l"][i - 1] <= m1 * 1.01 and s["c"][i] > s["o"][i] and s["c"][i] > s["c"][i - 1]
    return -s["rs"][i] if ok and leader(i, s) else None


def O_L5(i, s):
    kh = s["piv_i"][i]
    if kh is None or i - kh < 15 or not bt.trend_template(s, i):
        return None
    piv = s["h"][kh]
    c = s["c"][i]
    if not (piv * 0.95 <= c <= piv) or (piv - min(s["l"][kh:i + 1])) / piv > 0.35:
        return None
    return {"rank": -s["rs"][i], "kind": "stop", "trigger": piv, "stop": None}


ENTRIES = [("L1 大陽線の反発", L1), ("L2 包み足", L2), ("L3 50日線の押し", L3), ("L4 20日線の押しからの陽線", L4)]
EXITS = [("50日線割れ", X_BELOW50), ("20日線割れ", X_BELOW20), ("上のバンド", X_BAND)]


def section(w, rep, data, mem, start, end, days, years, title, show=()):
    w(title)
    g = lambda e, x: gen_trades(data, mem, e, x, start, end, ok=bt.liquid, fill="open", max_hold=500, stop_pct=STOP)
    res = {}
    rep.header("RSの高い順")
    for en, ef in ENTRIES:
        for xn, xf in EXITS:
            res[(en, xn)] = g(ef, xf)
            rep.line(f"{en}・{xn}", res[(en, xn)], STOP)
    for xn, xf in EXITS:
        res[("L5 ピボットへの逆指値買い（予約注文）", xn)] = tr = bs.simulate(data, mem, O_L5, to_sim(xf), start, end, max_hold=500)
        rep.line(f"L5 ピボットへの逆指値買い（予約注文）・{xn}", tr, STOP)
    b3 = bs.simulate(data, mem, bs.O_method3, bs.X_upper_band, start, end)
    m50 = gen_trades(data, mem, bt.E_minervini(50), X_BELOW50, start, end, ok=bt.liquid, fill="open", max_hold=500, stop_pct=STOP)
    best = sorted(res, key=lambda k: -(stats(res[k], COST) or {"mean": -1})["mean"])[:3]
    combos = [("採用中: ボリンジャーIII＋ミネルヴィニ", srt(b3 + m50))]
    combos += [(f"ボリンジャーIII＋{k[0]}・{k[1]}", srt(b3 + res[k])) for k in best]
    combos += [(f"{k[0]}・{k[1]}（単独）", res[k]) for k in best[:1]]
    w("\n**組み合わせ（7銘柄の枠を共有）。1トレード平均の上位3つをボリンジャーIIIと組み合わせた**\n")
    rep.header("RSの高い順")
    for lab, tr in combos:
        rep.line(lab, tr, STOP)
    w("")
    freq_table(w, rep, combos, days, years)
    for sym in show:
        w(f"\n**{sym}（直近6カ月）**\n")
        for (en, xn), tr in res.items():
            xs = [t for t in tr if t["sym"] == sym and t["in"] >= "2026-03-27"]
            if xs:
                w(f"- {en}・{xn}: " + "、".join(f"{t['in']} {t['px']:.2f}→{t['out']} {t['ret'] * 100:+.1f}%" for t in xs))
    return res


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/リーダーを押し目で買って持つ.md")
    a = ap.parse_args()
    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: リーダーを押し目・反発・予約注文で買って持つ型\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_leaders.py\n---\n")
    w("# 強い銘柄（リーダー）を押し目・反発・上抜けの予約注文で買い、トレンドが崩れるまで持つ型\n")
    w(__doc__.split("\n", 5)[5].strip() + "\n")
    w("注意: 同じ銘柄は手じまうまで次の買いをしない。データの最終日に保有中の売買は数えない（成績に入らない）。\n")
    members, data = load_universe(a.cache, min_bars=260)
    for s in data.values():
        bt.prepare(s)
        bs.prepare(s)
        bm2.add_pivot(s)
    spy = load_prices(a.cache, "SPY")
    end = dt.date.today().isoformat()
    wl = bth.load_watchlist()
    tdata = {s: data[s] for s in wl if s in data}
    for s in wl:
        if s not in tdata:
            d = load_prices(a.cache, s)
            if d and len(d["c"]) > 260:
                bt.prepare(d)
                bs.prepare(d)
                bm2.add_pivot(d)
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
    section(w, rep, data, members, start, end, days, y, "\n## 2. S&P500全体（その日の構成銘柄、2015年〜。後知恵なし）\n")
    sc, sm = spy_benchmark(spy, days)
    w("## 3. 注意\n")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
