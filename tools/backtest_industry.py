#!/usr/bin/env python3
"""その日の時点で強い業種だけにルールを当てるバックテスト（テーマ選びを後知恵なしで再現する）

使い方:
  tools/backtest_industry.py run [--out FILE]

テーマ監視銘柄での検証（年率57%など）は、今の時点で勝っている銘柄を選んでいるため後知恵を含む。
ここでは、S&P500のその日の構成銘柄を Yahoo の業種（industry）で分け、業種ごとの直近3カ月（63取引日）の騰落率の中央値で順位を付け、
その日に上位の業種に入っている銘柄だけに、採用中のルール（ボリンジャーIII・ミネルヴィニ）やローソク足の形を当てる。
業種は今の分類を過去にも使う（業種が変わった銘柄はずれる）。上場廃止銘柄の一部は株価データがない（backtest_lib の注意と同じ）。
"""
import argparse
import datetime as dt
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_candle as bcd
import backtest_swing as bs
import backtest_trend as bt
from backtest_lib import COSTS, DEFAULT_CACHE, Reporter, gen_trades, is_member, load_prices, load_universe, spy_benchmark
from backtest_regime import X_BAND, X_BELOW50, freq_table, srt

RISK, STOP, COST = 0.02, 0.15, COSTS[2]


def industry_ranks(data, members, look=63, min_n=3):
    """{日付: {業種: 順位の百分位（0=最強〜1=最弱）}}"""
    by_day = {}
    for sym, s in data.items():
        ind = s.get("ind")
        if not ind:
            continue
        c = s["c"]
        for i in range(look, len(c)):
            d = s["date"][i]
            if is_member(members[sym], d):
                by_day.setdefault(d, {}).setdefault(ind, []).append(c[i] / c[i - look] - 1)
    out = {}
    for d, g in by_day.items():
        med = {k: sorted(v)[len(v) // 2] for k, v in g.items() if len(v) >= min_n}
        order = sorted(med, key=lambda k: -med[k])
        n = len(order)
        out[d] = {k: j / max(n - 1, 1) for j, k in enumerate(order)}
    return out


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/強い業種だけに当てる.md")
    a = ap.parse_args()

    members, data = load_universe(a.cache, min_bars=260)
    u = json.load(open(os.path.join(a.cache, "universe.json")))
    extra = os.path.join(a.cache, "industry_extra.json")
    if os.path.exists(extra):
        u.update(json.load(open(extra)))
    for sym, s in data.items():
        bt.prepare(s)
        bs.prepare(s)
        s["ind"] = (u.get(sym) or {}).get("industry")
    bt.add_rs_rank(data, members)
    ranks = industry_ranks(data, members)
    spy = load_prices(a.cache, "SPY")
    start, end = "2015-01-02", dt.date.today().isoformat()
    days = [d for d in spy["date"] if start <= d <= end]
    years = len(days) / 252

    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: 強い業種だけにルールを当てるバックテスト\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_industry.py\n---\n")
    w("# その日の時点で強い業種だけにルールを当てる（テーマ選びを後知恵なしで再現）\n")
    w(__doc__.split("\n", 5)[5].strip() + "\n")
    n_ind = sum(1 for s in data.values() if s["ind"])
    w(f"- 業種が分かった銘柄: {n_ind} / {len(data)}。1日あたりの業種の数（構成銘柄3以上）: 約{sum(len(v) for v in ranks.values()) / max(len(ranks), 1):.0f}\n")
    rep = Reporter(w, data, days, [("前半", start, "2020-12-31"), ("後半", "2021-01-01", end)], years, cost=COST, risk=RISK)

    def ok_top(q):
        def f(s, i, spans):
            if not bt.liquid(s, i, spans):
                return False
            if q is None:
                return True
            rk = ranks.get(s["date"][i], {}).get(s["ind"])
            return rk is not None and rk <= q
        return f

    for q, lab in ((None, "すべての業種"), (0.2, "上位20%の業種"), (0.1, "上位10%の業種"), (0.05, "上位5%の業種")):
        ok = ok_top(q)
        g = lambda e, x, mh=120: gen_trades(data, members, e, x, start, end, ok=ok, fill="open", max_hold=mh, stop_pct=STOP)
        b3 = bs.simulate(data, members, bs.O_method3, bs.X_upper_band, start, end, ok=ok)
        m50 = g(bt.E_minervini(50), X_BELOW50, 500)
        e1 = g(bcd.E1, X_BAND)
        e2 = g(bcd.E2, X_BAND)
        w(f"\n## {lab}\n")
        rep.header("シグナルの強い順")
        combos = [("ボリンジャーIII（上のバンド）", b3), ("ミネルヴィニ（50日線割れ）", m50),
                  ("E1 大陽線の反発（上のバンド）", e1), ("E2 包み足（上のバンド）", e2),
                  ("採用中: ボリンジャーIII＋ミネルヴィニ", srt(b3 + m50)),
                  ("採用中＋E1＋E2", srt(b3 + m50 + e1 + e2))]
        for n, tr in combos:
            rep.line(n, tr, STOP)
        w("")
        freq_table(w, rep, combos[4:], days, years)
    sc, sm = spy_benchmark(spy, days)
    w("## 注意\n")
    w("- 業種の順位（3カ月、上位X%）の置き方は数通りしか試していない。前半・後半の両方で成り立つかを重視すること。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
