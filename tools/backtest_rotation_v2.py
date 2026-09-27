#!/usr/bin/env python3
"""新高値V2を、後知恵なしの監視銘柄の中でRSの特に高い銘柄だけに絞ると効くか

使い方:
  tools/backtest_rotation_v2.py run [--out FILE]

監視銘柄の作り方は tools/backtest_rotation.py と同じ（毎週末、その時点の数値だけで選び直す。平均約84銘柄）。
V2（トレンドテンプレート、RS≧90、直前20日の最高値（終値）を上回る、上げ下げの出来高比≧1.3、50日線割れで手じまい）を、
  (a) その週末の監視銘柄の中でRSが上位N銘柄（N = 10・20・30・50）に入っている銘柄だけ
  (b) RSの基準そのものを 95・97・98・99 以上に上げる
に絞って当てる。あわせて、ほかの採用ルール（ボリンジャーIII・ミネルヴィニ・急落の底（5日線で手じまい））と組み合わせた成績も出す。
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
import backtest_trend as bt
from backtest_lib import COSTS, DEFAULT_CACHE, Reporter, gen_trades, load_prices, load_universe
from backtest_regime import X_BELOW50, freq_table, srt

RISK, STOP, COST = 0.02, 0.15, COSTS[2]


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/新高値V2を絞る.md")
    a = ap.parse_args()
    members, data = load_universe(a.cache, min_bars=260)
    for s, d in data.items():
        c2.prep(d)
        d["sym"] = s
    bt.add_rs_rank(data, members)
    u = json.load(open(os.path.join(a.cache, "universe.json")))
    ex = os.path.join(a.cache, "industry_extra.json")
    if os.path.exists(ex):
        u.update(json.load(open(ex)))
    ind = {s: (u.get(s) or {}).get("industry") for s in data}
    spy = load_prices(a.cache, "SPY")
    end = dt.date.today().isoformat()
    start = "2015-01-02"
    days = [d for d in spy["date"] if start <= d <= end]
    fridays = [d for k, d in enumerate(days) if k + 1 == len(days) or dt.date.fromisoformat(days[k + 1]).isocalendar()[1] != dt.date.fromisoformat(d).isocalendar()[1]]
    lists = br.build_lists(data, members, fridays, ind)
    pos = {s: {d: k for k, d in enumerate(v["date"])} for s, v in data.items()}
    # 週末ごとの監視銘柄のRSの順位
    ranks = {}
    for f, lst in lists.items():
        rs = sorted(((data[s]["rs"][pos[s][f]] or 0, s) for s in lst if f in pos[s]), reverse=True)
        ranks[f] = {s: k + 1 for k, (_, s) in enumerate(rs)}
    week_of, fi, last = {}, 0, None
    for d in days:
        while fi < len(fridays) and fridays[fi] < d:
            last = fridays[fi]
            fi += 1
        week_of[d] = last

    def ok_top(n):
        def f(s, i, spans):
            wk = week_of.get(s["date"][i])
            return bt.liquid(s, i, spans) and wk is not None and ranks[wk].get(s["sym"], 10 ** 9) <= n
        return f

    def ok_rot(s, i, spans):
        wk = week_of.get(s["date"][i])
        return bt.liquid(s, i, spans) and wk is not None and s["sym"] in lists[wk]

    def v2_rs(th):
        return lambda i, s: c2.V2(i, s) if (s["rs"][i] or 0) >= th else None

    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: 新高値V2を絞る\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_rotation_v2.py\n---\n")
    w("# 新高値V2を、後知恵なしの監視銘柄の中でRSの特に高い銘柄だけに絞ると効くか\n")
    w(__doc__.split("\n", 5)[5].strip() + "\n")
    w("片道0.1%、リスク2%・損切り15%で建玉（13.3%×7銘柄）。データの最終日に保有中の売買は数えない。\n")
    for lab, lo in (("2015年〜", start), ("直近3年", dt.date.today().replace(year=dt.date.today().year - 3).isoformat())):
        dd = [d for d in days if d >= lo]
        mid = "2020-12-31" if lo == start else "2024-12-31"
        rep = Reporter(w, data, dd, [("前半", lo, mid), ("後半", (dt.date.fromisoformat(mid) + dt.timedelta(days=1)).isoformat(), end)],
                       len(dd) / 252, cost=COST, risk=RISK)
        g = lambda e, x, mh, ok: gen_trades(data, members, e, x, lo, end, ok=ok, fill="open", max_hold=mh, stop_pct=STOP)
        w(f"\n## {lab}\n")
        w("\n### V2だけ\n")
        rep.header("RSの高い順")
        v2s = {}
        v2s["監視銘柄すべて（前回の結果）"] = g(c2.V2, X_BELOW50, 500, ok_rot)
        for n in (10, 20, 30, 50):
            v2s[f"監視銘柄のRS上位{n}銘柄だけ"] = g(c2.V2, X_BELOW50, 500, ok_top(n))
        for th in (95, 97, 98, 99):
            v2s[f"監視銘柄すべて・RS≧{th}"] = g(v2_rs(th), X_BELOW50, 500, ok_rot)
        for k, t in v2s.items():
            rep.line(k, t, STOP)
        b3 = bs.simulate(data, members, bs.O_method3, bs.X_upper_band, lo, end, ok=ok_rot)
        m = g(bm2.E_base(2.0), X_BELOW50, 500, ok_rot)
        k3 = g(bcr.C3, c2.X_MA5, 60, ok_rot)
        base = b3 + m + k3
        combos = [("ボリンジャーIII＋ミネルヴィニ＋急落の底（V2なし）", srt(base))]
        combos += [(f"＋V2（{k}）", srt(base + t)) for k, t in v2s.items()]
        w("\n### ほかの採用ルールとの組み合わせ（後知恵なしの監視銘柄、7銘柄の枠を共有）\n")
        rep.header("RSの高い順")
        for k, t in combos:
            rep.line(k, t, STOP)
        w("")
        freq_table(w, rep, combos, dd, len(dd) / 252)
    w("\n## 注意\n")
    w("- 業種は今のYahooの分類を過去にも使っている。NASDAQ100は含めていない。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
