#!/usr/bin/env python3
"""恩株ツールの調査5: 短い期間で2倍になりやすい合図で買い、1年以内に2倍にならなければ売る（資金6,000ドル・4銘柄）

使い方: tools/backtest_onkabu_fast_pf.py [--cache DIR] [--out FILE] [--summary FILE] [--seeds 30]
売買の決まりは backtest_onkabu_portfolio.py と同じ（合図の翌日の寄り付きで買う、2倍で55.7%を売って恩株に、税・コスト込み）。
候補はその日のS&P500の構成銘柄すべて。合図は毎日の終値で判定する。
"""
import argparse
import bisect
import datetime as dt
import json
import os
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backtest_lib import DEFAULT_CACHE, load_prices, load_members, is_member
import backtest_onkabu as ob
import backtest_onkabu_portfolio as bp
import backtest_onkabu_fast as bfast


def make_signals(data, spy):
    pre = {}
    for s, v in data.items():
        c = v["c"]
        p = os.path.join(DEFAULT_CACHE, "onkabu_fund", s + ".json")
        rows = [tuple(r) for r in json.load(open(p)).get("rev", [])] if os.path.exists(p) else []
        rs = bfast.rev_series(rows)
        gap = [0.0] * len(c)
        from collections import deque
        dq = deque()
        for i in range(1, len(c)):     # 直近63日の1日の最大上昇率
            r = c[i] / c[i - 1] - 1
            while dq and dq[-1][1] <= r:
                dq.pop()
            dq.append((i, r))
            if dq[0][0] <= i - 63:
                dq.popleft()
            gap[i] = dq[0][1]
        pre[s] = {"hi": bfast.rolling_max(c, 252), "gap": gap, "rd": [x[0] for x in rs], "rv": [x[1] for x in rs]}

    def rev(s, i):
        P = pre[s]
        d = data[s]["date"][i]
        j = bisect.bisect_right(P["rd"], d) - 1
        if j < 0 or (dt.date.fromisoformat(d) - dt.date.fromisoformat(P["rd"][j])).days > 120:
            return None
        return P["rv"][j]

    def r(s, i, n):
        c = data[s]["c"]
        return c[i] / c[i - n] - 1

    nh = lambda s, i: data[s]["c"][i] >= pre[s]["hi"][i] * 0.999
    return {
        "3カ月で+50%以上": lambda s, i: r(s, i, 63) >= 0.5,
        "① 3カ月で+50%以上 かつ 52週高値": lambda s, i: r(s, i, 63) >= 0.5 and nh(s, i),
        "② ①＋売上≧20%": lambda s, i: r(s, i, 63) >= 0.5 and nh(s, i) and (rev(s, i) or 0) >= 0.2,
        "⑦ 6カ月で+100%以上 かつ 52週高値": lambda s, i: r(s, i, 126) >= 1.0 and nh(s, i),
        "⑧ ⑦＋売上≧20%": lambda s, i: r(s, i, 126) >= 1.0 and nh(s, i) and (rev(s, i) or 0) >= 0.2,
        "1日で+20%以上の急騰（3カ月以内）": lambda s, i: pre[s]["gap"][i] >= 0.2,
        "1日で+20%以上の急騰（3カ月以内） かつ 売上≧20%": lambda s, i: pre[s]["gap"][i] >= 0.2 and (rev(s, i) or 0) >= 0.2,
        "（逆）3カ月で−30%以上（急落後）": lambda s, i: r(s, i, 63) <= -0.3,
    }


EXITS = [
    ("1年で2倍にならなければ売る", None, 252),
    ("6カ月で2倍にならなければ売る", None, 126),
    ("1年で売る＋買値の−30%で売る", 0.7, 252),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default=DEFAULT_CACHE)
    ap.add_argument("--out")
    ap.add_argument("--summary")
    ap.add_argument("--seeds", type=int, default=30)
    ap.add_argument("--start", default="2015-01-01")
    ap.add_argument("--exclude", default="", help="除く銘柄（カンマ区切り）。1銘柄に頼っていないかの確認用")
    a = ap.parse_args()
    members = load_members(a.cache)
    spy = load_prices(a.cache, "SPY")
    data = {}
    for s in members:
        d = load_prices(a.cache, s)
        if d and len(d["c"]) > 300 and s not in a.exclude.split(","):
            data[s] = d
    days = [d for d in spy["date"] if d >= a.start]
    cbm = {}
    for d in days:
        if d[:7] not in cbm:
            cbm[d[:7]] = [s for s, sp in members.items() if s in data and is_member(sp, d)]
    sig = make_signals(data, spy)
    k0 = spy["date"].index(days[0])
    spy_curve = [bp.CAPITAL * spy["c"][spy["date"].index(d)] / spy["c"][k0] for d in days]
    spy_end, spy_cagr, spy_mdd = bp.metrics(spy_curve, days)
    out = []
    w = out.append
    w("---\ntype: backtest\ntitle: 短い期間で2倍の合図で買う（資金6,000ドル・4銘柄・1年以内）\n"
      f"created: {dt.date.today().isoformat()}\nscript: tools/backtest_onkabu_fast_pf.py\n---\n")
    w("# 短い期間で2倍の合図で買う（資金6,000ドル・4銘柄・長くても1年）\n")
    if a.summary and os.path.exists(a.summary):
        w(open(a.summary).read())
    w("## 前提\n")
    w(f"- 期間 {days[0]}〜{days[-1]}。資金{bp.CAPITAL:,.0f}ドル、枠{bp.SLOTS}つ（恩株は枠から外れる）。候補はその日のS&P500の構成銘柄すべて")
    w("- 合図はその日の終値で判定し、翌日の寄り付きで買う。2倍になったら55.7%を売って恩株に。売買コスト片道0.1%、利益に20.315%の税")
    w(f"- 同じ日に枠より多く合図が出たらランダムに選び、{a.seeds}回の中央値（かっこ内は下位10%〜上位10%）。待っている間の現金は0%")
    if a.exclude:
        w(f"- **除いた銘柄: {a.exclude}**（1銘柄の大当たりに頼っていないかの確認）")
    w(f"- **比べる相手（SPYを持ち続ける）**: 最後 {spy_end:,.0f}ドル、年率 {spy_cagr:.1%}、最大下落率 {spy_mdd:.1%}\n")
    for ename, stop, maxd in EXITS:
        w(f"## 2倍にならない株: {ename}\n")
        w("| 買う合図 | 最後の資産（中央値） | 年率 | 最大下落率 | 恩株の数 | 2倍にならず売った（平均の値上がり） | 現金の割合 | SPYに勝った回数 |")
        w("|---|---|---|---|---|---|---|---|")
        for sname, sfn in sig.items():
            ends, cagrs, mdds, onks, oth_n, oth_r, cashr = [], [], [], [], [], [], []
            for seed in range(a.seeds):
                curve, trades, n_onk, onk, act, cs = bp.simulate(data, spy, days, cbm, sfn, stop, maxd, seed)
                e, c, m = bp.metrics(curve, days)
                ends.append(e); cagrs.append(c); mdds.append(m); onks.append(n_onk); cashr.append(cs)
                o = [r for r, _, k in trades if k != "2倍"]
                oth_n.append(len(o)); oth_r.append(st.mean(o) - 1 if o else 0)
            q = lambda xs, p: sorted(xs)[int(p * (len(xs) - 1))]
            w(f"| {sname} | {st.median(ends):,.0f}ドル（{q(ends, .1):,.0f}〜{q(ends, .9):,.0f}） | {st.median(cagrs):.1%} | {st.median(mdds):.1%} | "
              f"{st.median(onks):.0f} | {st.median(oth_n):.0f}件（{st.median(oth_r):+.0%}） | {st.median(cashr):.0%} | {sum(e > spy_end for e in ends)}/{a.seeds} |")
        w("")
    text = "\n".join(out) + "\n"
    if a.out:
        os.makedirs(os.path.dirname(a.out), exist_ok=True)
        open(a.out, "w").write(text)
    print(text)


if __name__ == "__main__":
    main()
