#!/usr/bin/env python3
"""採用ルールの数値を1つずつ動かして、当てはめすぎに気をつけながら良い値を探すバックテスト

使い方:
  tools/backtest_tune.py run [--out FILE]

今の採用ルールの組み合わせ（ボリンジャーIII＋ミネルヴィニ＋急落の底＋新高値V2（RS上位10・2年の最高値以上）、
同時に7銘柄・1銘柄13.3%、同じ業種は2銘柄まで）で、次の数値を1つずつ動かす（ほかは今の値のまま）。
  1. 手じまい: ミネルヴィニの手じまいの線（今は50日線）、新高値V2の手じまいの線（今は50日線）、損切りの幅（今は15%）、
     ボリンジャーIIIの手じまい（今は%b≧1.0＝上のバンド）、急落の底の手じまい（今は5日線の上抜け）
  2. 資金の分け方: 同時に持つ銘柄数（今は7。合計の投資額は同じ93%で、1銘柄の額を変える）
  3. 新高値V2の候補数（今はRS上位10）
  4. 急落の底: 合図になる5日間の下落（今は−15%）、RSI(2)の上限（今は5）
  5. 1日に新しく買う銘柄数の上限（今はなし）。予約注文の件数の上限（B_MAX）の代わりに、同じ日に買いが集中するのを抑える効果を見る
当てはめすぎを防ぐ方法:
  - 値は設計期間（2015〜2021年）の成績で選び、確認期間（2022年〜）はその後で見る
  - ずらしながらの確認: 各年について「その前の年までの成績が一番良い値」を選び、その年の成績をつなげる（毎年選び直した場合の成績）
  - 採用の目安: 設計期間で今の値より良く、両隣の値も今の値以上（1つの値だけが良いのは偶然とみなす）、
    確認期間でも、ずらしながらの確認でも今の値を下回らないこと
"""
import argparse
import datetime as dt
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_compare2 as c2
import backtest_crash as bcr
import backtest_figures2 as f2
import backtest_minervini2 as bm2
import backtest_modern as bmo
import backtest_rotation as br
import backtest_swing as bs
import backtest_trend as bt
from backtest_lib import COSTS, DEFAULT_CACHE, gen_trades, load_prices, load_universe, pct, portfolio, sma
from backtest_regime import srt

RISK, STOP, COST = 0.02, 0.15, COSTS[2]
START, IS_END, OOS_START = "2015-01-02", "2021-12-31", "2022-01-01"
SEEDS = range(10)
SLOTS, WEIGHT = 7, RISK / STOP


def med(xs):
    xs = sorted(xs)
    return xs[len(xs) // 2]


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/数値の調整.md")
    a = ap.parse_args()
    members, data = load_universe(a.cache, min_bars=260)
    g = load_prices(a.cache, "^GSPC")
    f2.SPX.update(zip(g["date"], g["c"]))
    MAS = (3, 5, 7, 10, 20, 30, 40, 50, 70, 100)
    for sym, d in data.items():
        c2.prep(d)
        bmo.prep(d, f2.SPX)
        f2.prep(d)
        for n in MAS:
            d[f"ma{n}"] = d.get(f"ma{n}") or sma(d["c"], n)
        d["sym"] = sym
    bt.add_rs_rank(data, members)
    u = json.load(open(os.path.join(a.cache, "universe.json")))
    ex = os.path.join(a.cache, "industry_extra.json")
    if os.path.exists(ex):
        u.update(json.load(open(ex)))
    ind = {s: (u.get(s) or {}).get("industry") for s in data}
    spy = load_prices(a.cache, "SPY")
    end = dt.date.today().isoformat()
    days = [d for d in spy["date"] if START <= d <= end]
    fridays = [d for k, d in enumerate(days) if k + 1 == len(days) or dt.date.fromisoformat(days[k + 1]).isocalendar()[1] != dt.date.fromisoformat(d).isocalendar()[1]]
    lists = br.build_lists(data, members, fridays, ind)
    sets = {f: set(l) for f, l in lists.items()}
    pos = {s: {d: k for k, d in enumerate(v["date"])} for s, v in data.items()}
    ranks = {f: {s: k + 1 for k, (_, s) in enumerate(sorted(((data[s]["rs"][pos[s][f]] or 0, s) for s in l if f in pos[s]), reverse=True))}
             for f, l in lists.items()}
    week_of, fi, last = {}, 0, None
    for d in days:
        while fi < len(fridays) and fridays[fi] < d:
            last = fridays[fi]
            fi += 1
        week_of[d] = last
    ok_rot = lambda s, i, sp: bt.liquid(s, i, sp) and week_of.get(s["date"][i]) is not None and s["sym"] in sets[week_of[s["date"][i]]]
    okN = lambda n: (lambda s, i, sp: bt.liquid(s, i, sp) and week_of.get(s["date"][i]) is not None
                     and ranks[week_of[s["date"][i]]].get(s["sym"], 10 ** 9) <= n)

    G = lambda e, x, ok, stop=STOP, mh=500: gen_trades(data, members, e, x, START, end, ok=ok, fill="open", max_hold=mh, stop_pct=stop)
    below = lambda n: (lambda j, s, k, px: s[f"ma{n}"][j] is not None and s["c"][j] < s[f"ma{n}"][j])
    above = lambda n: (lambda j, s, k, px: s[f"ma{n}"][j] is not None and s["c"][j] > s[f"ma{n}"][j])
    v2o = bmo.with_(c2.V2, f2.O)

    def B3(th=1.0, stop=STOP):
        x = lambda j, s, k, t: ("open", "手じまい") if s["pctb"][j] is not None and s["pctb"][j] >= th else None
        old, bs.STOP_MAX = bs.STOP_MAX, stop
        try:
            return bs.simulate(data, members, bs.O_method3, x, START, end, ok=ok_rot)
        finally:
            bs.STOP_MAX = old

    def CR(dropv=-0.15, rsi=5):
        def f(i, s):
            rr, r2 = bcr.drop(i, s), s["rsi2"][i]
            return rr if rr <= dropv and r2 is not None and r2 <= rsi and bcr.was_strong(i, s) else None
        return f

    base = {
        "B": B3(),
        "M": G(bm2.E_base(2.0), below(50), ok_rot),
        "C": G(CR(), above(5), ok_rot, mh=60),
        "V": G(v2o, below(50), okN(10)),
    }
    years = sorted({d[:4] for d in days})
    yr_last = {y: max(d for d in days if d[:4] == y) for y in years}
    di = {d: k for k, d in enumerate(days)}

    def evaluate(tr, slots=SLOTS, weight=WEIGHT, day_cap=None):
        res = [portfolio(tr, COST, slots, days, data, weight=weight, seed=k, group_of=ind, group_cap=2, day_cap=day_cap) for k in SEEDS]
        def seg(c, lo_d, hi_d):
            a0 = c[di[lo_d] - 1] if di[lo_d] > 0 else 1.0
            return c[di[hi_d]] / a0
        span = lambda lo, hi: (dt.date.fromisoformat(hi) - dt.date.fromisoformat(lo)).days / 365.25
        is_hi = max(d for d in days if d <= IS_END)
        oos_lo = min(d for d in days if d >= OOS_START)
        yr = {}
        for y in years:
            lo = min(d for d in days if d[:4] == y)
            yr[y] = med([seg(p["curve"], lo, yr_last[y]) - 1 for p in res])
        return {
            "all": med([p["cagr"] for p in res]),
            "rng": (min(p["cagr"] for p in res), max(p["cagr"] for p in res)),
            "mdd": med([p["mdd"] for p in res]),
            "is": med([seg(p["curve"], days[0], is_hi) ** (1 / span(days[0], is_hi)) - 1 for p in res]),
            "oos": med([seg(p["curve"], oos_lo, days[-1]) ** (1 / span(oos_lo, days[-1])) - 1 for p in res]),
            "yr": yr,
            "n": len(tr),
        }

    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: 数値の調整\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_tune.py\n---\n")
    w("# 採用ルールの数値の調整（当てはめすぎに気をつけて）\n")
    w(__doc__.split("\n", 5)[5].strip() + "\n")
    w("年率・最大下落率は、同じ日の候補の選び方をランダムにした10通りの中央値。片道0.1%。後知恵なしの監視銘柄。\n")
    w("「ずらしながら」は、2018年から毎年「その前の年までで一番良かった値」を使ってつなげた年率（今の値を固定した場合と比べる）。\n")

    WF_FROM = "2018"
    summary = []

    def study(title, cur, variants):
        """variants: [(値のラベル, 組み合わせのトレード, evaluate の追加引数)]"""
        print(title, file=sys.stderr)
        R = [(lab, evaluate(tr, **kw)) for lab, tr, kw in variants]
        labs = [x[0] for x in R]
        ci = labs.index(cur)
        cr = R[ci][1]
        # ずらしながらの確認
        def chain(pick):
            eq = 1.0
            for y in years:
                if y < WF_FROM:
                    continue
                eq *= 1 + R[pick(y)][1]["yr"][y]
            n = (dt.date.fromisoformat(days[-1]) - dt.date(int(WF_FROM), 1, 1)).days / 365.25
            return eq ** (1 / n) - 1

        def best_before(y):
            def score(k):
                p = 1.0
                for yy in years:
                    if yy < y:
                        p *= 1 + R[k][1]["yr"][yy]
                return p
            return max(range(len(R)), key=score)
        wf_pick = {y: labs[best_before(y)] for y in years if y >= WF_FROM}
        wf = chain(best_before)
        fixed = chain(lambda y: ci)
        w(f"\n## {title}\n")
        w("| 値 | 件数 | 年率 2015年〜（幅） | 最大下落率 | 設計期間 | 確認期間 | " + " | ".join(y for y in years) + " |")
        w("|---|---|---|---|---|---|" + "---|" * len(years))
        for lab, e in R:
            mark = "**" if lab == cur else ""
            w(f"| {mark}{lab}{mark} | {e['n']} | {pct(e['all'])}（{pct(e['rng'][0])}〜{pct(e['rng'][1])}） | {pct(e['mdd'])} | {pct(e['is'])} | {pct(e['oos'])} | "
              + " | ".join(pct(e["yr"][y], 0) for y in years) + " |")
        bi = max(range(len(R)), key=lambda k: R[k][1]["is"])
        nb = [R[k][1]["is"] for k in (bi - 1, bi + 1) if 0 <= k < len(R)]
        plateau = all(x >= cr["is"] for x in nb)
        verdict = (bi != ci and R[bi][1]["is"] > cr["is"] and plateau and R[bi][1]["oos"] >= cr["oos"] and wf >= fixed)
        w(f"\n- 設計期間で一番良い値: **{labs[bi]}**（{pct(R[bi][1]['is'])}。今の値 {cur} は {pct(cr['is'])}）。両隣も今の値以上か: {'はい' if plateau else 'いいえ'}。"
          f"確認期間: {pct(R[bi][1]['oos'])}（今の値 {pct(cr['oos'])}）")
        w(f"- ずらしながらの確認: 毎年選び直すと年率 {pct(wf)}、今の値に固定すると {pct(fixed)}。選ばれた値: "
          + "、".join(f"{y}年 {v}" for y, v in wf_pick.items()))
        w(f"- 目安での判定: **{'変える候補（' + labs[bi] + '）' if verdict else '今の値のまま'}**")
        summary.append((title, cur, labs[bi], verdict, cr, R[bi][1], wf, fixed))

    others = lambda *keys: [t for k in ("B", "M", "C", "V") if k not in keys for t in base[k]]
    comb = lambda extra, *drop: srt(others(*drop) + extra)
    cur_all = comb([])

    study("1-1. ミネルヴィニの手じまいの線", "50日線",
          [(f"{n}日線", comb(G(bm2.E_base(2.0), below(n), ok_rot), "M"), {}) for n in (20, 30, 40, 50, 70, 100)])
    study("1-2. 新高値V2の手じまいの線", "50日線",
          [(f"{n}日線", comb(G(v2o, below(n), okN(10)), "V"), {}) for n in (20, 30, 40, 50, 70, 100)])
    study("1-3. 損切りの幅（全部のルール。1銘柄の額は13.3%のまま）", "15%",
          [(f"{int(x * 100)}%", srt(B3(stop=x) + G(bm2.E_base(2.0), below(50), ok_rot, stop=x)
                                   + G(CR(), above(5), ok_rot, stop=x, mh=60) + G(v2o, below(50), okN(10), stop=x)), {})
           for x in (0.08, 0.10, 0.12, 0.15, 0.18, 0.20, 0.25)])
    study("1-4. ボリンジャーIIIの手じまい（%bがこの値以上）", "1.0",
          [(f"{x}", comb(B3(th=x), "B"), {}) for x in (0.5, 0.7, 0.8, 0.9, 1.0, 1.1)])
    study("1-5. 急落の底の手じまい（終値がこの線を上抜け）", "5日線",
          [(f"{n}日線", comb(G(CR(), above(n), ok_rot, mh=60), "C"), {}) for n in (3, 5, 7, 10, 20)])
    study("2. 同時に持つ銘柄数（合計の投資額は93%のまま）", "7銘柄",
          [(f"{n}銘柄", cur_all, {"slots": n, "weight": SLOTS * WEIGHT / n}) for n in (4, 5, 6, 7, 8, 9, 10, 12)])
    study("3. 新高値V2の候補数（監視銘柄のRSの高い順）", "上位10",
          [(f"上位{n}", comb(G(v2o, below(50), okN(n)), "V"), {}) for n in (3, 5, 7, 10, 15, 20, 30)])
    study("4-1. 急落の底の合図になる5日間の下落", "−15%",
          [(f"−{x}%", comb(G(CR(-x / 100), above(5), ok_rot, mh=60), "C"), {}) for x in (10, 12, 15, 18, 20, 25)])
    study("4-2. 急落の底のRSI(2)の上限", "5",
          [(f"{x}", comb(G(CR(rsi=x), above(5), ok_rot, mh=60), "C"), {}) for x in (2, 5, 10, 15, 25)])
    study("5. 1日に新しく買う銘柄数の上限", "上限なし",
          [(f"{n}銘柄", cur_all, {"day_cap": n}) for n in (1, 2, 3, 4)] + [("上限なし", cur_all, {})])

    w("\n## まとめ\n")
    w("| 数値 | 今の値 | 設計期間で一番良い値 | 設計期間（今→一番良い） | 確認期間（今→一番良い） | ずらしながら（固定→毎年選び直し） | 判定 |")
    w("|---|---|---|---|---|---|---|")
    for t, cur, b, v, cr, br_, wf, fx in summary:
        w(f"| {t} | {cur} | {b} | {pct(cr['is'])}→{pct(br_['is'])} | {pct(cr['oos'])}→{pct(br_['oos'])} | {pct(fx)}→{pct(wf)} | {'変える候補' if v else '今のまま'} |")
    w("\n## 注意\n")
    w("- 1つずつ動かしているので、2つ以上を同時に変えたときの効果は確かめていない。変える候補が複数あれば、組み合わせてもう一度確かめる。")
    w("- 業種は今のYahooの分類を過去にも使っている。NASDAQ100は含めていない。損切りは引け値で判定（ボリンジャーIIIだけは日中の安値）。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
