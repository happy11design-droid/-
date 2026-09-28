#!/usr/bin/env python3
"""ミネルヴィニ（第10章 VCP）とワインスタイン（第3・4章）の図から読み取った形の条件のバックテスト

使い方:
  tools/backtest_figures2.py run [--out FILE]

図の書き込みを、Claudeが数値にした（本は数値を示していない、または一部だけ）:
  ミネルヴィニ 第10章
    K 振るい落としのあとの突出高: ベースの中で、それより前のベースの安値を下回ったあと（振るい落とし）10日以内に、
        出来高が50日平均の2.5倍以上で上げた日がある（図10.20〜10.24「振るい落としのあと、大きな出来高を伴って元の水準まで戻る」）
    V 右側の短縮を除く: ベースの最安値の日から上抜けまでの日数が、ピボットの日から最安値の日までの日数の半分以上（図10.15・10.16「上昇が早すぎて、右側が短縮」）
    X 指数より大きく下げたベースを除く: ベースの調整幅が、同じ期間のS&P500の下落率の2.5倍以下（本文「株価指数の2〜3倍以上も下げる銘柄は避ける」、図10.13・10.14）
  ワインスタイン 第3・4章
    O 上値のレジスタンスがない: 上抜けの日の終値が直前2年（500日）の最高値以上（図4.4 パンナム「上値に重たいレジスタンス」はCマイナス、図4.5 レイノルズ「上値にレジスタンスがない」）
    M 30週線がはっきり上向き: 150日線が20日前より1%以上高い（図3.3「移動平均線は明らかに上昇傾向を示していなければならない」）
    Z RSライン（マンスフィールド）がプラスに転じた: 株価÷S&P500 が、その52週平均を上回り、かつ13週前は下回っていた（図4.3・4.6）
対象: 後知恵なしの監視銘柄。設計期間 2015〜2021年 / 確認期間 2022年〜。業種は2銘柄まで（採用中）。
"""
import argparse
import datetime as dt
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_compare2 as c2
import backtest_crash as bcr
import backtest_figures as bf
import backtest_minervini2 as bm2
import backtest_modern as bmo
import backtest_rotation as br
import backtest_swing as bs
import backtest_trend as bt
from backtest_lib import COSTS, DEFAULT_CACHE, gen_trades, load_prices, load_universe
from backtest_regime import X_BELOW50, freq_table, srt

RISK, STOP, COST = 0.02, 0.15, COSTS[2]
IS_END, OOS_START = "2021-12-31", "2022-01-01"
SPX = {}


def prep(s):
    n, h = len(s["c"]), s["h"]
    # 直前500日の最高値（当日を含まない）
    import collections
    hi, dq = [None] * n, collections.deque()
    for i in range(1, n):
        k = i - 1
        while dq and h[dq[-1]] <= h[k]:
            dq.pop()
        dq.append(k)
        while dq[0] < i - 500:
            dq.popleft()
        hi[i] = h[dq[0]] if i >= 250 else None
    s["hi500"] = hi
    # マンスフィールドRS: 株価÷S&P500 の52週（260日）平均からの乖離
    rsl = s["rsl"]
    m, acc, cnt = [None] * n, 0.0, 0
    for i in range(n):
        if rsl[i] is not None:
            acc += rsl[i]
            cnt += 1
        if i >= 260 and rsl[i - 260] is not None:
            acc -= rsl[i - 260]
            cnt -= 1
        if i >= 259 and cnt >= 200 and rsl[i] is not None:
            m[i] = rsl[i] / (acc / cnt) - 1
    s["mrs"] = m
    s["spx"] = [SPX.get(d) for d in s["date"]]


def K(i, s):
    kh = s["piv_i"][i]
    if kh is None or i - kh < 15:
        return False
    l, c, v, v50 = s["l"], s["c"], s["v"], s["vol50"]
    for j in range(kh + 10, i):
        if l[j] < min(l[kh:j - 5]):            # 振るい落とし（それより前のベースの安値を下回る）
            for k in range(j + 1, min(j + 11, i)):
                if v50[k] and v[k] >= 2.5 * v50[k] and c[k] > c[k - 1]:
                    return True
    return False


def V(i, s):
    kh = s["piv_i"][i]
    if kh is None or i - kh < 5:
        return False
    lo = min(range(kh, i), key=lambda k: s["l"][k])
    return (i - lo) >= 0.5 * (lo - kh)


def X(i, s):
    kh = s["piv_i"][i]
    if kh is None:
        return False
    piv = s["h"][kh]
    depth = (piv - min(s["l"][kh:i])) / piv
    sp = [x for x in s["spx"][kh:i + 1] if x is not None]
    if not sp:
        return True
    sdd = (max(sp) - min(sp)) / max(sp)
    return depth <= 2.5 * max(sdd, 0.04)       # 指数がほとんど下げていない期間は、指数の下落を4%とみなす


def O(i, s):
    return s["hi500"][i] is not None and s["c"][i] >= s["hi500"][i]


def M(i, s):
    m, m20 = s["ma150"][i], s["ma150"][i - 20]
    return m is not None and m20 is not None and m >= m20 * 1.01


def Z(i, s):
    a, b = s["mrs"][i], s["mrs"][i - 65] if i >= 65 else None
    return a is not None and b is not None and a > 0 >= b


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/ミネルヴィニとワインスタインの図から読み取った形.md")
    a = ap.parse_args()
    members, data = load_universe(a.cache, min_bars=260)
    g = load_prices(a.cache, "^GSPC")
    SPX.update(zip(g["date"], g["c"]))
    for sym, d in data.items():
        c2.prep(d)
        bmo.prep(d, SPX)
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

    halves = [("設計期間", start, IS_END), ("確認期間", OOS_START, end)]
    yrs = len(days) / 252
    L = []
    w = L.append
    rep = bmo.GroupReporter(w, data, days, halves, yrs, cost=COST, risk=RISK, group_of=ind, cap=2)
    G = lambda e, x, ok, mh=500: gen_trades(data, members, e, x, start, end, ok=ok, fill="open", max_hold=mh, stop_pct=STOP)
    # 買いの条件が出た日だけ形の条件を調べる（形の条件は重いので先に調べない）
    w_ = lambda e, *fs: (lambda i, s: r if (r := e(i, s)) is not None and all(f(i, s) for f in fs) else None)

    w("---\ntype: backtest\ntitle: ミネルヴィニとワインスタインの図から読み取った形\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_figures2.py\n---\n")
    w("# ミネルヴィニ（第10章 VCP）とワインスタイン（第3・4章）の図から読み取った形のバックテスト\n")
    w(__doc__.split("\n", 5)[5].strip() + "\n")
    w("建玉はすべて同じ（1銘柄に資金の13.3%、同時に7銘柄まで、同じ業種は2銘柄まで＝採用中）。片道0.1%。表の「前半 / 後半」は設計期間 / 確認期間。\n")

    FILT = [("そのまま", ()), ("＋K 振るい落としのあとの突出高", (K,)), ("＋V 右側の短縮を除く", (V,)), ("＋X 指数より大きく下げたベースを除く", (X,)),
            ("＋O 上値のレジスタンスがない（2年の高値以上）", (O,)), ("＋M 30週線がはっきり上向き", (M,)), ("＋Z RSラインがプラスに転じた", (Z,)),
            ("＋V・X・O・M（避ける形をすべて除く）", (V, X, O, M))]
    rules = {
        "ミネルヴィニのベース（採用中、出来高2倍）": (bm2.E_base(2.0), X_BELOW50, ok_rot),
        "ベースの上抜け（出来高1.5倍・ベース2週以上・調整幅25%以内）": (bm2.E_base(1.5, depth=0.25, min_len=10), X_BELOW50, ok_rot),
        "ワインスタイン10週（採用中、週足・出来高2倍）": (bt.E_weinstein(10, ma="10"), bt.X_weekly_below("10"), ok_rot),
        "新高値V2（採用中、RS上位10）": (c2.V2, X_BELOW50, ok10),
    }
    res = {}
    for name, (e, x, ok) in rules.items():
        w(f"\n## {name}\n")
        rep.header("RSの高い順")
        for fn, fs in FILT:
            if name.startswith("新高値") and fn.startswith(("＋K", "＋V", "＋X")):
                continue          # ベースの形の条件なので、ベースのない新高値V2には当てない
            t = G(w_(e, *fs) if fs else e, x, ok)
            res[(name, fn)] = t
            rep.line(fn, t, STOP)

    tmp_ = []
    tmp = bmo.GroupReporter(tmp_.append, data, days, halves, yrs, cost=COST, risk=RISK, group_of=ind, cap=2)
    is_cagr = lambda tr: tmp.med([tmp.port(tr, STOP, start, IS_END, seed=k)["cagr"] for k in tmp.SEEDS])
    pick = {}
    for name in rules:
        cand = {fn: t for (n, fn), t in res.items() if n == name}
        best = max(cand, key=lambda k: is_cagr(cand[k]))
        pick[name] = (best, cand[best])
    b3 = bs.simulate(data, members, bs.O_method3, bs.X_upper_band, start, end, ok=ok_rot)
    k3 = G(bcr.C3, c2.X_MA5, ok_rot, 60)
    mb = "ミネルヴィニのベース（採用中、出来高2倍）"
    v2 = "新高値V2（採用中、RS上位10）"
    cur = srt(b3 + res[(mb, "そのまま")] + k3 + res[(v2, "そのまま")])
    combos = [("今の採用ルール（ボリンジャーIII＋ミネルヴィニ＋急落の底＋新高値V2、業種2銘柄まで）", cur),
              ("ミネルヴィニと新高値V2を、設計期間で選んだ形に入れ替え", srt(b3 + pick[mb][1] + k3 + pick[v2][1])),
              ("上に、ワインスタイン（設計期間で選んだ形）を加える", srt(b3 + pick[mb][1] + k3 + pick[v2][1] + pick["ワインスタイン10週（採用中、週足・出来高2倍）"][1]))]
    w("\n## 採用ルールの組み合わせ（7銘柄の枠と、同じ業種2銘柄までを共有）\n")
    w("設計期間の年率で選んだ形: " + "、".join(f"{n}＝{b}" for n, (b, _) in pick.items()) + "（確認期間の成績は選ぶときに見ていない）\n")
    rep.header("RSの高い順")
    for k, t in combos:
        rep.line(k, t, STOP)
    w("")
    freq_table(w, rep, combos, days, yrs)
    w("\n## 注意\n")
    w("- 図の書き込みを数値にしたのはClaude（2.5倍、10日、半分、2年、1%、52週・13週など）。本は数値を示していない。")
    w("- 業種は今のYahooの分類を過去にも使っている。NASDAQ100は含めていない。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
