#!/usr/bin/env python3
"""新しめの本の手法を、公開されている定義でバックテストする（本を買う前の下調べ。本を手に入れたら本の数値で検証し直す）

使い方:
  tools/backtest_newbooks.py run [--out FILE]

1. ポケットピボット（モラレス＆キャッチャー『Trade Like an O'Neil Disciple』2010）
   上げた日の出来高が、直前10日のうち下げた日の最大の出来高より多い。上昇トレンドの中（終値＞50日線＞200日線）で、
   10日線の近く（終値 ≦ 10日線×1.05、伸びすぎていない）。RS ≧ 80。翌日の寄り付きで買う
   手じまい: 引けで50日線割れ（今のルールと同じ）／引けで10日線割れ（本の短い方の売り）
2. 買える窓開け Buyable Gap-up（同じ本）
   寄り付きが前日の終値より 40日ATR×0.75 以上高く、その日の出来高が50日平均の1.5倍以上。上昇トレンドの中、RS ≧ 80。
   翌日の寄り付きで買い、損切りは窓を開けた日の安値（上限は買値の15%下）。手じまい: 引けで50日線割れ
3. クレノー『Stocks on the Move』2015
   順位: 直近90日の株価の対数の回帰の傾き（年率）×決定係数。条件: 終値＞100日線、直近90日に15%以上の窓がない。
   市場の条件: S&P500 が200日線より上のときだけ新しく買う。毎週金曜に判定し、順位が上位20%（その日の対象銘柄の中）の銘柄を買う。
   手じまい: 金曜に上位20%から外れた、100日線を割った、15%以上の窓が出た
   本は資金の0.1%のリスクで値動きに合わせて建玉を決めるが、ここでは比べやすいよう今のルールと同じ建玉（13.3%×7銘柄）にした
対象: 後知恵なしの監視銘柄（クレノーはS&P500全体も）。設計期間 2015〜2021年 / 確認期間 2022年〜。業種は2銘柄まで（採用中）。
"""
import argparse
import datetime as dt
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_compare2 as c2
import backtest_crash as bcr
import backtest_figures2 as f2
import backtest_minervini2 as bm2
import backtest_modern as bmo
import backtest_rotation as br
import backtest_swing as bs
import backtest_trend as bt
from backtest_lib import COSTS, DEFAULT_CACHE, gen_trades, load_prices, load_universe, sma
from backtest_regime import X_BELOW50, freq_table, srt, to_sim

RISK, STOP, COST = 0.02, 0.15, COSTS[2]
IS_END, OOS_START = "2021-12-31", "2022-01-01"


def prep(s):
    c, h, l, n = s["c"], s["h"], s["l"], len(s["c"])
    s["ma10"] = sma(c, 10)
    s["ma100"] = sma(c, 100)
    tr = [h[0] - l[0]] + [max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1])) for i in range(1, n)]
    a40, acc = [None] * n, 0.0
    for i in range(n):
        acc += tr[i]
        if i >= 40:
            acc -= tr[i - 40]
        if i >= 39:
            a40[i] = acc / 40
    s["atr40"] = a40
    # クレノーの順位: 90日の対数価格の回帰の傾き（年率）×決定係数
    y = np.log(np.array(c, dtype=float))
    N = 90
    x = np.arange(N, dtype=float)
    xm, sxx = x.mean(), ((x - x.mean()) ** 2).sum()
    score = [None] * n
    if n > N:
        win = np.lib.stride_tricks.sliding_window_view(y, N)          # (n-N+1, N)
        ym = win.mean(axis=1)
        b = ((win - ym[:, None]) * (x - xm)).sum(axis=1) / sxx
        fit = ym[:, None] + b[:, None] * (x - xm)
        ss_res = ((win - fit) ** 2).sum(axis=1)
        ss_tot = ((win - ym[:, None]) ** 2).sum(axis=1)
        r2 = np.where(ss_tot > 0, 1 - ss_res / ss_tot, 0)
        ann = np.exp(b * 252) - 1
        sc = ann * r2
        for k in range(len(sc)):
            score[k + N - 1] = float(sc[k])
    s["clenow"] = score
    gap = [False] * n
    for i in range(1, n):
        gap[i] = abs(s["o"][i] / c[i - 1] - 1) >= 0.15
    s["gap90"] = [any(gap[max(0, i - 89):i + 1]) for i in range(n)]


def up(i, s):
    m50, m200 = s["ma50"][i], s["ma200"][i]
    return m50 is not None and m200 is not None and s["c"][i] > m50 > m200


def E_pp(i, s):
    """ポケットピボット"""
    if i < 12 or not up(i, s) or (s["rs"][i] or 0) < 80 or s["ma10"][i] is None:
        return None
    c, v = s["c"], s["v"]
    if c[i] <= c[i - 1] or c[i] > s["ma10"][i] * 1.05:
        return None
    downs = [v[k] for k in range(i - 10, i) if c[k] < c[k - 1]]
    if not downs or v[i] <= max(downs):
        return None
    return -(s["rs"][i] or 0)


def O_bgu(i, s):
    """買える窓開け（simulate 用の注文）。損切りは窓を開けた日の安値"""
    a, v50 = s["atr40"][i], s["vol50"][i]
    if i < 1 or a is None or v50 is None or not up(i, s) or (s["rs"][i] or 0) < 80:
        return None
    if s["o"][i] - s["c"][i - 1] < 0.75 * a or s["v"][i] < 1.5 * v50:
        return None
    return {"rank": -(s["rs"][i] or 0), "kind": "open", "stop": s["l"][i]}


X_BELOW10 = lambda j, s, k, px: s["ma10"][j] is not None and s["c"][j] < s["ma10"][j]


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/新しい本の手法の下調べ.md")
    a = ap.parse_args()
    members, data = load_universe(a.cache, min_bars=260)
    g = load_prices(a.cache, "^GSPC")
    f2.SPX.update(zip(g["date"], g["c"]))
    gma200 = dict(zip(g["date"], sma(g["c"], 200)))
    mkt_ok = lambda d: gma200.get(d) is not None and f2.SPX.get(d, 0) > gma200[d]
    for sym, d in data.items():
        c2.prep(d)
        bmo.prep(d, f2.SPX)
        f2.prep(d)
        prep(d)
        d["sym"] = sym
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
    fri_set = set(fridays)
    lists = br.build_lists(data, members, fridays, ind)
    pos = {s: {d: k for k, d in enumerate(v["date"])} for s, v in data.items()}
    ranks = {f: {s: k + 1 for k, (_, s) in enumerate(sorted(((data[s]["rs"][pos[s][f]] or 0, s) for s in l if f in pos[s]), reverse=True))}
             for f, l in lists.items()}
    week_of, fi, last = {}, 0, None
    for d in days:
        while fi < len(fridays) and fridays[fi] < d:
            last = fridays[fi]
            fi += 1
        week_of[d] = last
    ok_rot = lambda s, i, sp: bt.liquid(s, i, sp) and week_of.get(s["date"][i]) is not None and s["sym"] in lists[week_of[s["date"][i]]]
    ok10 = lambda s, i, sp: bt.liquid(s, i, sp) and week_of.get(s["date"][i]) is not None and ranks[week_of[s["date"][i]]].get(s["sym"], 10 ** 9) <= 10

    # クレノーの週ごとの順位（上位20%の境目）: S&P500全体と、後知恵なしの監視銘柄の中で
    def clenow_cut(pool_of):
        cut = {}
        for f in fridays:
            xs = []
            for s in pool_of(f):
                k = pos[s].get(f)
                if k is None:
                    continue
                d = data[s]
                sc = d["clenow"][k]
                if sc is None or d["ma100"][k] is None or d["c"][k] <= d["ma100"][k] or d["gap90"][k] or not bt.liquid(d, k, members[s]):
                    continue
                xs.append(sc)
            xs.sort(reverse=True)
            cut[f] = xs[max(0, int(len(xs) * 0.2) - 1)] if xs else None
        return cut
    from backtest_lib import is_member
    cut_all = clenow_cut(lambda f: [s for s in data if is_member(members[s], f)])
    cut_rot = clenow_cut(lambda f: lists[f])

    def E_cl(cut):
        def f(i, s):
            d = s["date"][i]
            if d not in fri_set or not mkt_ok(d):
                return None
            sc, cu = s["clenow"][i], cut.get(d)
            if sc is None or cu is None or sc < cu or s["ma100"][i] is None or s["c"][i] <= s["ma100"][i] or s["gap90"][i]:
                return None
            return -sc
        return f

    def X_cl(cut):
        def f(j, s, k, px):
            d = s["date"][j]
            if s["ma100"][j] is not None and s["c"][j] < s["ma100"][j]:
                return True
            if s["gap90"][j] and abs(s["o"][j] / s["c"][j - 1] - 1) >= 0.15:
                return True
            if d in fri_set:
                sc, cu = s["clenow"][j], cut.get(d)
                return sc is None or cu is None or sc < cu
            return False
        return f

    halves = [("設計期間", start, IS_END), ("確認期間", OOS_START, end)]
    yrs = len(days) / 252
    L = []
    w = L.append
    rep = bmo.GroupReporter(w, data, days, halves, yrs, cost=COST, risk=RISK, group_of=ind, cap=2)
    G = lambda e, x, ok, stop=STOP, mh=500: gen_trades(data, members, e, x, start, end, ok=ok, fill="open", max_hold=mh, stop_pct=stop)
    ok_all = lambda s, i, sp: bt.liquid(s, i, sp)

    w("---\ntype: backtest\ntitle: 新しい本の手法の下調べ\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_newbooks.py\n---\n")
    w("# 新しめの本の手法を、公開されている定義でバックテストする（本を買う前の下調べ）\n")
    w(__doc__.split("\n", 5)[5].strip() + "\n")
    w("建玉はすべて同じ（1銘柄に資金の13.3%、同時に7銘柄まで、同じ業種は2銘柄まで＝採用中）。片道0.1%。表の「前半 / 後半」は設計期間 / 確認期間。\n")
    w("\n## 1. 単独の成績\n")
    rep.header("RSまたは順位の高い順")
    R = {
        "ポケットピボット・50日線割れ（監視銘柄）": G(E_pp, X_BELOW50, ok_rot),
        "ポケットピボット・10日線割れ（監視銘柄）": G(E_pp, X_BELOW10, ok_rot),
        "ポケットピボット・50日線割れ（監視銘柄のRS上位10）": G(E_pp, X_BELOW50, ok10),
        "買える窓開け・損切りは窓の日の安値・50日線割れ（監視銘柄）": bs.simulate(data, members, O_bgu, to_sim(X_BELOW50), start, end, ok=ok_rot),
        "買える窓開け（S&P500全体）": bs.simulate(data, members, O_bgu, to_sim(X_BELOW50), start, end, ok=ok_all),
        "クレノー（監視銘柄の中の上位20%）": G(E_cl(cut_rot), X_cl(cut_rot), ok_rot),
        "クレノー（S&P500全体の上位20%。本のとおり）": G(E_cl(cut_all), X_cl(cut_all), ok_all),
    }
    for k, t in R.items():
        rep.line(k, t, STOP)

    b3 = bs.simulate(data, members, bs.O_method3, bs.X_upper_band, start, end, ok=ok_rot)
    v2o = bmo.with_(c2.V2, f2.O)
    cur = srt(b3 + G(bm2.E_base(2.0), X_BELOW50, ok_rot) + G(bcr.C3, c2.X_MA5, ok_rot, mh=60) + G(v2o, X_BELOW50, ok10))
    tmp_ = []
    tmp = bmo.GroupReporter(tmp_.append, data, days, halves, yrs, cost=COST, risk=RISK, group_of=ind, cap=2)
    is_cagr = lambda tr: tmp.med([tmp.port(tr, STOP, start, IS_END, seed=k)["cagr"] for k in tmp.SEEDS])
    best = max(R, key=lambda k: is_cagr(R[k]))
    w("\n## 2. 今の採用ルールとの組み合わせ（7銘柄の枠と、同じ業種2銘柄までを共有）\n")
    w(f"今の採用ルール = ボリンジャーIII＋ミネルヴィニ＋急落の底＋新高値V2（RS上位10・2年の最高値以上）。設計期間の年率で一番良かった手法: {best}\n")
    rep.header("RSの高い順")
    combos = [("今の採用ルール", cur)] + [(f"今の採用ルール＋{k}", srt(cur + t)) for k, t in R.items()]
    for k, t in combos:
        rep.line(k, t, STOP)
    w("")
    freq_table(w, rep, [combos[0]] + [c for c in combos if best in c[0]], days, yrs)
    w("\n## 注意\n")
    w("- 定義は公開されている説明にもとづき、Claudeが数値にしたもの（本の正確な数値ではない）。本を手に入れたら本の数値で検証し直す。")
    w("- 業種は今のYahooの分類を過去にも使っている。NASDAQ100は含めていない。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
