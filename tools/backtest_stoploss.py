#!/usr/bin/env python3
"""損切りの幅を広げる・損切りをなくす（ルールの売りはそのまま）バックテスト（4銘柄の枠）

使い方:
  tools/backtest_stoploss.py run [--out FILE]

今の採用ルール（4つのルール、4銘柄・1銘柄25%、急落の底RSI(2)≦10、同じ業種2銘柄まで）の損切りだけを
15%（今）・20%・25%・30%・なしに変える。ルールの売り（上部バンド・50日線割れ・5日線超え）と打ち切り
（押し目・急落の底は60取引日、ミネルヴィニ・新高値V2は500取引日）はそのまま。
押し目の売りは、今の採用（2026-10-01、前日の上部バンドに指値で売る）と、以前の形（引けで上部バンド以上→翌日の寄り付き）の両方で試す。
損切りの判定は今までのバックテストと同じ（押し目は日中の安値、ほかは引け値）。片道0.1%。
選び方の乱数50通りの中央値。設計期間 2015〜2021年 / 確認期間 2022年〜。
"""
import argparse
import datetime as dt
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_combo2 as cb
import backtest_minervini2 as bm2
import backtest_swing as bs
from backtest_lib import COSTS, DEFAULT_CACHE, pct

COST = COSTS[2]
SLOTS = 4
SEEDS = range(50)
NONE_B = 0.99          # 押し目の「損切りなし」（bs.simulate は損切りの幅が必要なため、99%下に置く）


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/損切りの幅となしの比較.md")
    a = ap.parse_args()
    ctx = cb.setup(a.cache, with_parts=False)
    data, members, ind, days, G, end = (ctx[k] for k in ("data", "members", "ind", "days", "G", "end"))
    pos = {}

    def idx(sym, d):
        if sym not in pos:
            pos[sym] = {x: k for k, x in enumerate(data[sym]["date"])}
        return pos[sym][d]

    def b3(stop):
        old, bs.STOP_MAX = bs.STOP_MAX, stop
        try:
            return bs.simulate(data, members, bs.O_method3, bs.X_upper_band, cb.START, end, ok=ctx["ok_rot"])
        finally:
            bs.STOP_MAX = old

    def path_trade(t, rule, pv, why):
        i1 = max(idx(t["sym"], d) for d in pv)
        out = data[t["sym"]]["date"][i1]
        return {"sym": t["sym"], "in": t["in"], "out": out, "path": pv, "rule": rule, "ret": pv[out] - 1, "why": why}

    def plain(t, rule):
        s, sym = data[t["sym"]], t["sym"]
        i0, i1 = idx(sym, t["in"]), idx(sym, t["out"])
        sh = (1 - COST) / t["px"]
        pv = {s["date"][j]: sh * s["c"][j] for j in range(i0, i1)}
        pv[s["date"][i1]] = sh * t["px"] * (1 + t["ret"]) * (1 - COST)
        return path_trade(t, rule, pv, t.get("why", ""))

    def b3_limit(t, stop):
        """押し目: 買った日の夜から前日の上部バンドに売りの指値。損切りは日中の安値。打ち切りは60取引日。"""
        s, sym = data[t["sym"]], t["sym"]
        o, h, l, c = s["o"], s["h"], s["l"], s["c"]
        i0, n, px = idx(sym, t["in"]), len(c), t["px"]
        floor, sh, pv, pend, j, why = px * (1 - stop), (1 - COST) / px, {}, False, i0, "打ち切り"
        while j < n:
            d = s["date"][j]
            if pend:
                pv[d] = sh * o[j] * (1 - COST)
                break
            if l[j] <= floor:
                pv[d] = sh * min(o[j] if j > i0 else px, floor) * (1 - COST)
                why = "損切り"
                break
            if j > i0 and s["bb_up"][j - 1] is not None and h[j] >= s["bb_up"][j - 1]:
                pv[d] = sh * max(o[j], s["bb_up"][j - 1]) * (1 - COST)
                why = "指値"
                break
            pv[d] = sh * c[j]
            if j + 1 >= n:
                return None
            if j - i0 >= bs.MAX_HOLD or (s["pctb"][j] is not None and s["pctb"][j] >= 1.0):
                pend, why = True, "打ち切り" if j - i0 >= bs.MAX_HOLD else "条件"
            j += 1
        return path_trade(t, "B", pv, why) if pv else None

    def build(stop, limit):
        gs = stop               # None = 損切りなし
        out = []
        for t in b3(stop if stop is not None else NONE_B):
            x = b3_limit(t, stop if stop is not None else NONE_B) if limit else plain(t, "B")
            if x:
                out.append(x)
        out += [plain(t, "M") for t in G(bm2.E_base(2.0), ctx["below50"], ctx["ok_rot"], gs)]
        out += [plain(t, "V") for t in G(ctx["v2o"], ctx["below50"], ctx["ok10"], gs)]
        out += [plain(t, "C") for t in G(ctx["CR"](10), ctx["above5"], ctx["ok_rot"], gs, 60)]
        return out

    is_hi = max(d for d in days if d <= cb.IS_END)
    oos_lo = min(d for d in days if d >= cb.OOS_START)

    def port(trs, seed, lo, hi):
        dd = [d for d in days if lo <= d <= hi]
        by_in = {}
        for t in trs:
            if lo <= t["in"] and t["out"] <= hi:
                by_in.setdefault(t["in"], []).append(t)
        rnd = random.Random(seed)
        cash, held, peak, mdd, worst, eq = 1.0, [], 1.0, 0.0, 0.0, 1.0
        for d in dd:
            still = []
            for h in held:
                v = h["t"]["path"].get(d)
                if v is not None:
                    h["v"] = v
                if h["t"]["out"] == d:
                    cash += h["size"] * h["v"]
                    worst = min(worst, h["size"] * (h["v"] - 1) / h["eq0"])
                else:
                    still.append(h)
            held = still
            eq = cash + sum(h["size"] * h["v"] for h in held)
            for t in sorted(by_in.get(d, []), key=lambda t: rnd.random()):
                if any(h["t"]["sym"] == t["sym"] for h in held):
                    continue
                if len(held) >= SLOTS:
                    break
                if sum(1 for h in held if ind.get(h["t"]["sym"]) == ind.get(t["sym"])) >= 2:
                    continue
                size = min(eq / SLOTS, cash)
                if size <= 0:
                    break
                cash -= size
                v0 = t["path"].get(d, 1.0)
                if t["out"] == d:
                    cash += size * v0
                    continue
                held.append({"t": t, "size": size, "v": v0, "eq0": eq})
            eq = cash + sum(h["size"] * h["v"] for h in held)
            peak = max(peak, eq)
            mdd = max(mdd, 1 - eq / peak)
        yrs = (dt.date.fromisoformat(dd[-1]) - dt.date.fromisoformat(dd[0])).days / 365.25
        return eq ** (1 / yrs) - 1, mdd, worst

    def evaluate(trs):
        a_ = [port(trs, 7000 + k, days[0], days[-1]) for k in SEEDS]
        i_ = [port(trs, 7000 + k, days[0], is_hi)[0] for k in SEEDS]
        o_ = [port(trs, 7000 + k, oos_lo, days[-1])[0] for k in SEEDS]
        return {"all": cb.med([x[0] for x in a_]), "mdd": cb.med([x[1] for x in a_]), "worst": cb.med([x[2] for x in a_]),
                "is": cb.med(i_), "oos": cb.med(o_)}

    def stats(trs):
        rets = [t["ret"] for t in trs]
        big = sum(1 for x in rets if x <= -0.15)
        return len(trs), sum(rets) / len(rets), min(rets), big

    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: 損切りの幅となしの比較\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_stoploss.py\n---\n")
    w("# 損切りの幅を広げる・損切りをなくすバックテスト（4銘柄の枠）\n")
    w(__doc__.split("\n", 5)[5].strip() + "\n")
    w("「1回の最大の損（資金比）」は、1つの売買で失った額を、買った日の資金で割った値（乱数50通りの中央値）。"
      "「1回で−15%以上の損」は、買値から15%以上下で売った売買の件数（全部の合図、枠に入らなかったものも含む）。\n")
    for limit in (True, False):
        w(f"\n## 押し目の売り: {'前日の上部バンドに指値（今の採用）' if limit else '引けで上部バンド以上→翌日の寄り付き（以前の形）'}\n")
        w("| 損切り | 年率 | 最大下落率 | 設計期間 | 確認期間 | 1回の最大の損（資金比） | 合図の件数 | 1回平均 | 1回の最悪 | 1回で−15%以上の損 | 両方の期間で15%を上回ったか |")
        w("|---|---|---|---|---|---|---|---|---|---|---|")
        cur = None
        for stop in (0.15, 0.20, 0.25, 0.30, None):
            trs = build(stop, limit)
            e = evaluate(trs)
            n, avg, mn, big = stats(trs)
            if cur is None:
                cur = e
            ok = e is not cur and e["is"] > cur["is"] and e["oos"] > cur["oos"]
            lab = "なし" if stop is None else f"{int(stop * 100)}%" + ("（今）" if stop == 0.15 and limit else "")
            w(f"| {lab} | {pct(e['all'])} | {pct(e['mdd'])} | {pct(e['is'])} | {pct(e['oos'])} | {pct(e['worst'])} | "
              f"{n} | {pct(avg, 2)} | {pct(mn, 0)} | {big} | {'はい' if ok else ''} |")
            print(limit, lab, file=sys.stderr)
    w("\n## 注意\n")
    w("- 「損切りなし」でも、打ち切り（押し目・急落の底は60取引日、ミネルヴィニ・新高値V2は50日線割れ）で必ず売る。押し目は99%下に置いた損切り（実質なし）。")
    w("- 押し目以外の損切りは引け値で判定する（今までのバックテストと同じ）。実際の逆指値は日中に約定するので、窓を開けて下げた日は損切りの値より下で売れる。")
    w("- 選び方の乱数で年率は2〜3ポイント動くので、それ以下の差は偶然の範囲。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
