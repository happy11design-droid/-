#!/usr/bin/env python3
"""急落の底で買う逆張りのバックテスト

使い方:
  tools/backtest_crash.py run [--out FILE]

背景（2026-09-27）: SNDKの大きく動いた日の再現で、急落の底（7/28 −14.2%、7/29 −7.3%）に採用ルールの合図が出なかった
（ボリンジャーIIIの 21日II%>0 が、売りが続くとマイナスになるため）。翌日の寄り付きで買っていれば5日後 +27.5%／+19.0% だった。
急落の底で買うルールを数値で作り、後知恵なしで検証する。数値はClaudeが置いたもので、本のルール表の値ではない。

強い銘柄（急落の前）: 急落が始まる前（6取引日前）に 50日線 > 200日線 だった
仕掛け（引け後に判定し、翌日の寄り付きで買う。C2・C4は反発を確認して買う）:
  C1 急落: 終値が直前5日の最高値（終値）から20%以上下げた
  C2 急落の後の最初の陽線: C1の急落から5日以内に、陽線（終値>始値）かつ前日より高く引けた日
  C3 急落＋RSI(2)≦5: 直前5日の最高値から15%以上下げ、RSI(2)≦5
  C4 3日続落で下のバンドの外: 3日続けて下げ、終値がボリンジャーバンド（20日、−2σ）より下（ボリンジャーIIIから出来高の条件を外したもの）
手じまい: 引けで20日線以上（平均への戻り）／引けで上のバンド以上／10取引日後。損切り: 買値の15%下（引け値）
"""
import argparse
import csv
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_connors as bc
import backtest_swing as bs
import backtest_theme as bth
import backtest_trend as bt
from backtest_lib import COSTS, DEFAULT_CACHE, Reporter, gen_trades, load_prices, load_universe, market_regime, stats
from backtest_regime import X_BAND, X_BELOW50, freq_table, srt

RISK, STOP, COST = 0.02, 0.15, COSTS[2]


def was_strong(i, s):
    k = i - 6
    m50, m200 = s["ma50"][k], s["ma200"][k]
    return k > 0 and m50 is not None and m200 is not None and m50 > m200


def drop(i, s, n=5):
    return s["c"][i] / max(s["c"][i - n:i]) - 1 if i > n else 0


def C1(i, s):
    r = drop(i, s)
    return r if r <= -0.20 and was_strong(i, s) else None


def C2(i, s):
    c, o = s["c"], s["o"]
    if not (c[i] > o[i] and c[i] > c[i - 1]):
        return None
    for k in range(i - 1, max(i - 6, 6), -1):
        if C1(k, s) is not None:
            return drop(k, s)
        if c[k] > o[k] and c[k] > c[k - 1]:
            return None    # 急落の後、すでに陽線が出ていた
    return None


def C3(i, s):
    r, r2 = drop(i, s), s["rsi2"][i]
    return r if r <= -0.15 and r2 is not None and r2 <= 5 and was_strong(i, s) else None


def C4(i, s):
    c, dn = s["c"], s["bb_dn"][i]
    ok = dn is not None and c[i] < dn and c[i] < c[i - 1] < c[i - 2] < c[i - 3]
    return s["pctb"][i] if ok and was_strong(i, s) else None


X_MID = lambda j, s, k, px: s["bb_mid"][j] is not None and s["c"][j] >= s["bb_mid"][j]
X_TIME10 = lambda j, s, k, px: k >= 10
ENTRIES = [("C1 急落（5日で−20%）", C1), ("C2 急落の後の最初の陽線", C2), ("C3 急落（5日で−15%）＋RSI(2)≦5", C3),
           ("C4 3日続落で下のバンドの外", C4)]
EXITS = [("20日線まで戻ったら", X_MID), ("上のバンド", X_BAND), ("10日後", X_TIME10)]


def prep(s):
    bt.prepare(s)
    bs.prepare(s)
    bc.prepare(s)


def by_regime(w, tr, data, mreg):
    g = {}
    for t in tr:
        s = data[t["sym"]]
        i = s["date"].index(t["in"]) - 1
        g.setdefault(mreg.get(s["date"][i], "判定不能"), []).append(t)
    return "／".join(f"{k} {st['n']}件 平均{st['mean'] * 100:+.2f}% PF{st['pf']:.2f}"
                    for k in ("上昇", "横ばい", "下落") if (st := stats(g.get(k, []), COST)))


def section(w, rep, data, mem, start, end, days, years, title, mreg, show=()):
    w(title)
    g = lambda e, x: gen_trades(data, mem, e, x, start, end, ok=bt.liquid, fill="open", max_hold=60, stop_pct=STOP)
    res = {}
    rep.header("下げの大きい順")
    for en, ef in ENTRIES:
        for xn, xf in EXITS:
            res[(en, xn)] = g(ef, xf)
            rep.line(f"{en}・{xn}", res[(en, xn)], STOP)
    w("\n**市場全体の局面別（S&P500の30週線で近似したワインスタインのステージ。仕掛けの前日）**\n")
    for (en, xn), tr in res.items():
        if xn == "20日線まで戻ったら":
            w(f"- {en}・{xn}: {by_regime(w, tr, data, mreg)}")
    b3 = bs.simulate(data, mem, bs.O_method3, bs.X_upper_band, start, end)
    m50 = gen_trades(data, mem, bt.E_minervini(50), X_BELOW50, start, end, ok=bt.liquid, fill="open", max_hold=500, stop_pct=STOP)
    best = sorted(res, key=lambda k: -(stats(res[k], COST) or {"mean": -1})["mean"])[:3]
    combos = [("採用中: ボリンジャーIII＋ミネルヴィニ", srt(b3 + m50))] + \
             [(f"採用中＋{k[0]}・{k[1]}", srt(b3 + m50 + res[k])) for k in best]
    w("\n**採用中のルールとの組み合わせ（7銘柄の枠を共有）。1トレード平均の上位3つを足した**\n")
    rep.header("下げの大きい順")
    for lab, tr in combos:
        rep.line(lab, tr, STOP)
    w("")
    freq_table(w, rep, combos, days, years)
    for sym in show:
        w(f"\n**{sym}（直近6カ月）**\n")
        n = 0
        for (en, xn), tr in res.items():
            xs = [t for t in tr if t["sym"] == sym and t["in"] >= "2026-03-27"]
            if xs:
                n += 1
                w(f"- {en}・{xn}: " + "、".join(f"{t['in']} {t['px']:.2f}→{t['out']} {t['ret'] * 100:+.1f}%（{t['why']}）" for t in xs))
        if not n:
            w("- シグナルなし（または保有中）")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/急落の底で買う逆張り.md")
    a = ap.parse_args()
    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: 急落の底で買う逆張り\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_crash.py\n---\n")
    w("# 急落の底で買う逆張りのバックテスト\n")
    w(__doc__.split("\n", 5)[5].strip() + "\n")
    w("損切り15%・片道0.1%・リスク2%で建玉（13.3%×7銘柄）。データの最終日に保有中の売買は数えない。\n")
    members, data = load_universe(a.cache, min_bars=260)
    for s in data.values():
        prep(s)
    spy = load_prices(a.cache, "SPY")
    mreg = market_regime(spy)
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
            "## 1. テーマ監視銘柄（直近3年。監視銘柄を今の時点で選んでいるため後知恵あり）\n", mreg, show=("SNDK", "DELL"))
    bt.add_rs_rank(data, members)
    start = "2015-01-02"
    days = [d for d in spy["date"] if start <= d <= end]
    y = len(days) / 252
    rep = Reporter(w, data, days, [("前半", start, "2020-12-31"), ("後半", "2021-01-01", end)], y, cost=COST, risk=RISK)
    section(w, rep, data, members, start, end, days, y, "\n## 2. S&P500の構成銘柄（その日の構成銘柄、2015年〜。後知恵なし）\n", mreg)
    w("\n## 3. 注意\n")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
