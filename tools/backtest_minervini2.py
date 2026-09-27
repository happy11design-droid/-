#!/usr/bin/env python3
"""ミネルヴィニの「ベースの上抜け」をルール表どおりの定義に直したバックテスト

使い方:
  tools/backtest_minervini2.py run [--out FILE]

これまでの定義（backtest_trend.E_minervini）の問題: ベースの調整幅を「直前50日の高値−安値」で測っていたため、
上昇トレンドの途中の銘柄ではトレンドの上昇幅そのもの（SNDKの2026年4〜6月で42〜69%）になり、35%以内の条件をほぼ満たさなかった。
直した定義（`書籍ルール/ミネルヴィニ_ルール表.md` p.98, p.103, p.104）:
  ベース: 直前65週（325取引日）の最高値を付けた日から前日までの期間。長さは3週（15取引日）以上
  調整幅: その最高値（ピボット）から、ベースの中の最安値までの下落率 ≦ 35%
  上抜け: 終値 > ピボット、トレンドテンプレート8条件、翌日の寄り付き ≦ ピボット×1.03、出来高 ≧ 50日平均×N倍
  手じまい: 引けで50日線割れの翌日の寄り付き。損切り: 買値の15%下
出来高の倍率は本の2倍（p.121）と、本の値より緩めた1.5倍・条件なし（参考、ルール表外）を比べる。
"""
import argparse
import collections
import csv
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_swing as bs
import backtest_theme as bth
import backtest_trend as bt
from backtest_lib import COSTS, DEFAULT_CACHE, Reporter, gen_trades, load_prices, load_universe, spy_benchmark
from backtest_regime import X_BELOW50, freq_table, srt

RISK, STOP, COST = 0.02, 0.15, COSTS[2]
LOOK = 325


def add_pivot(s):
    """piv_i[i]: 直前LOOK日（当日を含まない）の最高値の日の位置（同じ値なら新しい方）"""
    h, n = s["h"], len(s["h"])
    out, dq = [None] * n, collections.deque()
    for i in range(1, n):
        k = i - 1
        while dq and h[dq[-1]] <= h[k]:
            dq.pop()
        dq.append(k)
        while dq[0] < i - LOOK:
            dq.popleft()
        out[i] = dq[0]
    s["piv_i"] = out


def E_base(vol_mult=2.0, depth=0.35, min_len=15):
    def f(i, s):
        kh = s["piv_i"][i]
        if kh is None or i + 1 >= len(s["c"]) or i - kh < min_len:
            return None
        piv = s["h"][kh]
        if s["c"][i] <= piv or s["o"][i + 1] > piv * 1.03:
            return None
        if (piv - min(s["l"][kh:i])) / piv > depth:
            return None
        if vol_mult and s["v"][i] < vol_mult * s["vol50"][i]:
            return None
        if not bt.trend_template(s, i):
            return None
        return -s["rs"][i]
    return f


VARIANTS = [("出来高2倍（本の値 p.121）", 2.0), ("出来高1.5倍（ルール表外）", 1.5), ("出来高の条件なし（ルール表外）", None)]


def section(w, rep, data, mem, start, end, days, years, title):
    w(title)
    g = lambda e, mh=500: gen_trades(data, mem, e, X_BELOW50, start, end, ok=bt.liquid, fill="open", max_hold=mh, stop_pct=STOP)
    rep.header("RSの高い順")
    old = g(bt.E_minervini(50))
    rep.line("これまでの定義（直前50日の高値−安値≦35%・出来高2倍）", old, STOP)
    new = {}
    for lab, vm in VARIANTS:
        new[lab] = g(E_base(vm))
        rep.line(f"直した定義・{lab}", new[lab], STOP)
    b3 = bs.simulate(data, mem, bs.O_method3, bs.X_upper_band, start, end)
    w("\n**ボリンジャーIIIとの組み合わせ（7銘柄の枠を共有）**\n")
    combos = [("採用中: ボリンジャーIII＋これまでのミネルヴィニ", srt(b3 + old))] + \
        [(f"ボリンジャーIII＋直した定義のミネルヴィニ・{lab}", srt(b3 + new[lab])) for lab, _ in VARIANTS]
    rep.header("RSの高い順")
    for lab, tr in combos:
        rep.line(lab, tr, STOP)
    w("")
    freq_table(w, rep, combos, days, years)
    return old, new


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/ミネルヴィニのベースの定義の修正.md")
    a = ap.parse_args()
    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: ミネルヴィニのベースの定義の修正\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_minervini2.py\n---\n")
    w("# ミネルヴィニの「ベースの上抜け」をルール表どおりの定義に直したバックテスト\n")
    w(__doc__.split("\n", 5)[5].strip() + "\n")

    members, data = load_universe(a.cache, min_bars=260)
    for s in data.values():
        bt.prepare(s)
        bs.prepare(s)
        add_pivot(s)
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
                add_pivot(d)
                tdata[s] = d
    tmem = {s: [("0000-00-00", "9999-12-31")] for s in tdata}
    sp_now = [r["ticker"] for r in csv.DictReader(open(os.path.join(a.cache, "members.csv"))) if not r["end_date"]]
    bth.rs_ranks(a.cache, sorted(set(sp_now) | set(tdata)), tdata)
    today = dt.date.today()
    start3 = today.replace(year=today.year - 3).isoformat()
    days3 = [d for d in spy["date"] if start3 <= d <= end]
    y3 = len(days3) / 252
    rep3 = Reporter(w, tdata, days3, [("前半", start3, "2024-12-31"), ("後半", "2025-01-01", end)], y3, cost=COST, risk=RISK)
    old3, new3 = section(w, rep3, tdata, tmem, start3, end, days3, y3,
                         "## 1. テーマ監視銘柄（直近3年。監視銘柄を今の時点で選んでいるため後知恵あり）\n")
    w("\n## 2. SNDK（直近6カ月）\n")
    for lab, tr in [("これまでの定義", old3)] + [(f"直した定義・{k}", v) for k, v in new3.items()]:
        xs = [t for t in tr if t["sym"] == "SNDK" and t["in"] >= "2026-03-27"]
        w(f"- {lab}: " + ("、".join(f"{t['in']} {t['px']:.2f}で買い → {t['out']} {t['ret'] * 100:+.1f}%（{t['why']}）" for t in xs) or "シグナルなし（または保有中）"))
    w("")

    bt.add_rs_rank(data, members)
    start = "2015-01-02"
    days = [d for d in spy["date"] if start <= d <= end]
    y = len(days) / 252
    rep = Reporter(w, data, days, [("前半", start, "2020-12-31"), ("後半", "2021-01-01", end)], y, cost=COST, risk=RISK)
    section(w, rep, data, members, start, end, days, y, "\n## 3. S&P500全体（その日の構成銘柄、2015年〜。後知恵なし）\n")
    sc, sm = spy_benchmark(spy, days)
    w("## 4. 注意\n")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
