#!/usr/bin/env python3
"""勝率の高い売りの合図で半分だけ売る／オニールを空き枠の候補にだけ使う バックテスト

使い方:
  tools/backtest_half_oneil.py run [--out FILE]

今の採用ルール（4つのルール、4銘柄・1銘柄25%、損切り15%、急落の底RSI(2)≦10、同じ業種2銘柄まで、
押し目は前日の上部バンドに指値で売る〔2026-10-01 採用〕）に対して:
  1. 順張り（ミネルヴィニ・新高値V2）の保有中に「反転のローソク足（かぶせ線・弱気の包み足・宵の明星・流れ星）＋
     出来高が50日平均の1.5倍以上＋RSI(14)が前日か当日に70以上」（`売りの合図の組み合わせ.md` の1番、売った後に下がった割合76%）が
     出たら、翌日の寄り付きで半分だけ売る。残り半分は今のルール（50日線割れ・損切り15%）で売る。
     1'. 同じ合図で、利益が出ているとき（引けが買値より上）だけ半分売る
  2. オニール（`オニールの成長株発掘法.md` の本のとおりの買い・売り・市場の方向。損切り8%・利益確定20%）を、
     ほかの4つのルールの候補で枠が埋まらなかった日の空き枠にだけ入れる（候補の順番を一番後ろにする）。
     探す範囲: 後知恵なしの監視銘柄／S&P500全体（流動性の条件だけ）
     2'. オニールの買いで、売りは今のルール（50日線割れ・損切り15%）
片道0.1%。選び方の乱数50通りの中央値。設計期間 2015〜2021年 / 確認期間 2022年〜。
"""
import argparse
import datetime as dt
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_combo2 as cb
import backtest_exit_combo as xc
import backtest_exit_signals as xs
import backtest_minervini2 as bm2
import backtest_oneil as bo
import backtest_swing as bs
import backtest_trend as bt
from backtest_lib import COSTS, DEFAULT_CACHE, gen_trades, load_prices, pct
from backtest_regime import X_BELOW50

COST = COSTS[2]
SLOTS = 4
SEEDS = range(50)
STOP = 0.15


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/半分だけ売るとオニールの空き枠.md")
    a = ap.parse_args()
    ctx = cb.setup(a.cache, with_parts=False)
    data, members, ind, days, G, end = (ctx[k] for k in ("data", "members", "ind", "days", "G", "end"))
    pos = {}

    def idx(sym, d):
        if sym not in pos:
            pos[sym] = {x: k for k, x in enumerate(data[sym]["date"])}
        return pos[sym][d]

    def path_trade(t, rule, pv, prio=0):
        i1 = max(idx(t["sym"], d) for d in pv)
        out = data[t["sym"]]["date"][i1]
        return {"sym": t["sym"], "in": t["in"], "out": out, "path": pv, "rule": rule, "ret": pv[out] - 1, "prio": prio}

    def plain(t, rule, prio=0):
        s, sym = data[t["sym"]], t["sym"]
        i0, i1 = idx(sym, t["in"]), idx(sym, t["out"])
        sh = (1 - COST) / t["px"]
        pv = {s["date"][j]: sh * s["c"][j] for j in range(i0, i1)}
        pv[s["date"][i1]] = sh * t["px"] * (1 + t["ret"]) * (1 - COST)
        return path_trade(t, rule, pv, prio)

    def b3_limit(t):
        s, sym = data[t["sym"]], t["sym"]
        o, h, l, c = s["o"], s["h"], s["l"], s["c"]
        i0, n, px = idx(sym, t["in"]), len(c), t["px"]
        floor, sh, pv, pend, j = px * (1 - STOP), (1 - COST) / px, {}, False, i0
        while j < n:
            d = s["date"][j]
            if pend:
                pv[d] = sh * o[j] * (1 - COST)
                break
            if l[j] <= floor:
                pv[d] = sh * min(o[j] if j > i0 else px, floor) * (1 - COST)
                break
            if j > i0 and s["bb_up"][j - 1] is not None and h[j] >= s["bb_up"][j - 1]:
                pv[d] = sh * max(o[j], s["bb_up"][j - 1]) * (1 - COST)
                break
            pv[d] = sh * c[j]
            if j + 1 >= n:
                return None
            if j - i0 >= bs.MAX_HOLD or (s["pctb"][j] is not None and s["pctb"][j] >= 1.0):
                pend = True
            j += 1
        return path_trade(t, "B", pv) if pv else None

    def half(t, rule, need_gain):
        """合図の翌日の寄り付きで半分売る。残りは元の売り（t の out・ret）"""
        s, sym = data[t["sym"]], t["sym"]
        i0, i1 = idx(sym, t["in"]), idx(sym, t["out"])
        px = t["px"]
        sh, cash, pv, done = (1 - COST) / px, 0.0, {}, False
        for j in range(i0, i1):
            pv[s["date"][j]] = cash + sh * s["c"][j]
            if not done and j >= 2 and j + 1 < i1 and xc.c1(s, j) and (not need_gain or s["c"][j] > px):
                done = True
                cash += sh / 2 * s["o"][j + 1] * (1 - COST)
                sh /= 2
        pv[s["date"][i1]] = cash + sh * px * (1 + t["ret"]) * (1 - COST)
        return path_trade(t, rule, pv), done

    b3_raw = []
    old, bs.STOP_MAX = bs.STOP_MAX, STOP
    try:
        b3_raw = bs.simulate(data, members, bs.O_method3, bs.X_upper_band, cb.START, end, ok=ctx["ok_rot"])
    finally:
        bs.STOP_MAX = old
    B = [x for x in (b3_limit(t) for t in b3_raw) if x]
    M_raw = G(bm2.E_base(2.0), ctx["below50"], ctx["ok_rot"], STOP)
    V_raw = G(ctx["v2o"], ctx["below50"], ctx["ok10"], STOP)
    C = [plain(t, "C") for t in G(ctx["CR"](10), ctx["above5"], ctx["ok_rot"], STOP, 60)]
    for sym in {t["sym"] for t in M_raw + V_raw}:
        xs.prep(data[sym])
    base = B + C + [plain(t, "M") for t in M_raw] + [plain(t, "V") for t in V_raw]

    def half_set(need_gain):
        out, n = B + C, 0
        for t, rule in [(t, "M") for t in M_raw] + [(t, "V") for t in V_raw]:
            x, done = half(t, rule, need_gain)
            out.append(x)
            n += done
        return out, n

    IDX = [load_prices(a.cache, k) for k in ("^GSPC", "^IXIC")]
    mk = bo.market_ok(IDX)
    allow_m = lambda d: mk.get(d, True)
    ok_liquid = lambda s, i, spans: bt.liquid(s, i, spans)

    def oneil(ok, own_exit):
        if own_exit:
            tr = gen_trades(data, members, bo.E_oneil, bo.X_oneil(), cb.START, end, ok=ok, fill="open", allow=allow_m,
                            max_hold=500, stop_pct=bo.P["stop"])
        else:
            tr = gen_trades(data, members, bo.E_oneil, X_BELOW50, cb.START, end, ok=ok, fill="open", allow=allow_m,
                            max_hold=500, stop_pct=STOP)
        return [plain(t, "O", prio=1) for t in tr]

    is_hi = max(d for d in days if d <= cb.IS_END)
    oos_lo = min(d for d in days if d >= cb.OOS_START)

    def port(trs, seed, lo, hi):
        dd = [d for d in days if lo <= d <= hi]
        by_in = {}
        for t in trs:
            if lo <= t["in"] and t["out"] <= hi:
                by_in.setdefault(t["in"], []).append(t)
        rnd = random.Random(seed)
        cash, held, peak, mdd, eq, n_o = 1.0, [], 1.0, 0.0, 1.0, 0
        for d in dd:
            still = []
            for h in held:
                v = h["t"]["path"].get(d)
                if v is not None:
                    h["v"] = v
                if h["t"]["out"] == d:
                    cash += h["size"] * h["v"]
                else:
                    still.append(h)
            held = still
            eq = cash + sum(h["size"] * h["v"] for h in held)
            for t in sorted(by_in.get(d, []), key=lambda t: (t["prio"], rnd.random())):
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
                n_o += t["rule"] == "O"
                v0 = t["path"].get(d, 1.0)
                if t["out"] == d:
                    cash += size * v0
                    continue
                held.append({"t": t, "size": size, "v": v0})
            eq = cash + sum(h["size"] * h["v"] for h in held)
            peak = max(peak, eq)
            mdd = max(mdd, 1 - eq / peak)
        yrs = (dt.date.fromisoformat(dd[-1]) - dt.date.fromisoformat(dd[0])).days / 365.25
        return eq ** (1 / yrs) - 1, mdd, n_o / yrs

    def evaluate(trs):
        a_ = [port(trs, 8000 + k, days[0], days[-1]) for k in SEEDS]
        i_ = [port(trs, 8000 + k, days[0], is_hi)[0] for k in SEEDS]
        o_ = [port(trs, 8000 + k, oos_lo, days[-1])[0] for k in SEEDS]
        return {"all": cb.med([x[0] for x in a_]), "mdd": cb.med([x[1] for x in a_]), "no": cb.med([x[2] for x in a_]),
                "is": cb.med(i_), "oos": cb.med(o_)}

    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: 半分だけ売るとオニールの空き枠\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_half_oneil.py\n---\n")
    w("# 勝率の高い売りの合図で半分だけ売る／オニールを空き枠の候補にだけ使う\n")
    w(__doc__.split("\n", 5)[5].strip() + "\n")
    w("| 番号 | 形 | 年率 | 最大下落率 | 設計期間 | 確認期間 | 補足 | 両方の期間で上回ったか |")
    w("|---|---|---|---|---|---|---|---|")
    cur = evaluate(base)
    w(f"| ― | 今のルール | {pct(cur['all'])} | {pct(cur['mdd'])} | {pct(cur['is'])} | {pct(cur['oos'])} | | |")

    def row(no, lab, trs, note=""):
        e = evaluate(trs)
        ok = e["is"] > cur["is"] and e["oos"] > cur["oos"]
        if "{no}" in note:
            note = note.format(no=f"{e['no']:.1f}")
        w(f"| {no} | {lab} | {pct(e['all'])} | {pct(e['mdd'])} | {pct(e['is'])} | {pct(e['oos'])} | {note} | {'はい' if ok else ''} |")
        print(no, lab, file=sys.stderr)

    for no, lab, need in (("1", "順張りを合図で半分売る", False), ("1'", "順張りを合図で半分売る（利益が出ているときだけ）", True)):
        trs, n = half_set(need)
        row(no, lab, trs, f"半分売った売買 {n}件（順張り {len(M_raw) + len(V_raw)}件のうち）")
    for lab, ok in (("後知恵なしの監視銘柄", ctx["ok_rot"]), ("S&P500全体", ok_liquid)):
        o1 = oneil(ok, True)
        row("2", f"オニール（本のとおり）を空き枠だけ・{lab}", base + o1, f"合図 {len(o1)}件、買えたのは年{{no}}回")
        o2 = oneil(ok, False)
        row("2'", f"オニールの買い・今のルールの売りを空き枠だけ・{lab}", base + o2, f"合図 {len(o2)}件、買えたのは年{{no}}回")
    w("\n## 注意\n")
    w("- 合図の数値（出来高1.5倍・RSI70）とオニールの数値は、以前のバックテストと同じ（`売りの合図の組み合わせ.md`・`オニールの成長株発掘法.md`）。今回のために選び直していない。")
    w("- 選び方の乱数で年率は2〜3ポイント動くので、それ以下の差は偶然の範囲。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
