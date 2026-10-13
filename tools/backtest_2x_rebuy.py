#!/usr/bin/env python3
"""2倍ETFで、早めの売りの合図で売り、買いの合図で買い直す（回転売買）バックテスト

使い方:
  tools/backtest_2x_rebuy.py run [--seeds N] [--out FILE]

今の採用ルール（4つのルール、4銘柄・1銘柄25%、損切り15%、急落の底RSI(2)≦10、同じ業種2銘柄まで、
押し目は前日の上部バンドに指値で売る、順張りは反転の合図で半分売る）の買いの合図・ルールの売りの日はそのままで、
保有中の売り・買い直しを `売って買い直す.md` と同じ合図で行う。違いは、株の代わりに2倍ETFを持つこと。
  2倍ETF: 元の株の値動きの2倍だけ毎日動く（寄り付きまでと寄り付きから引けまでを分けて計算、経費 年1%、0より下にはならない）。
          `2倍ETFに置き換えた場合.md`・`リスクを足して年率を上げる.md` と同じ再現の仕方
  売りの合図（元の株で引けに判定、翌日の寄り付きで売る）: `売って買い直す.md` の10種類
  買い直し: A 売った値段より上で引けたら／B 上昇の合図（10日線を上に戻す・MACDのゴールデンクロス・SARの上向きの反転・強気の包み足）
            または底の合図（直近3日にRSI(2)≦10があり前日の高値を上に抜けて引ける／前日がたくり線で前日より上で引ける）
  その枠は、ルールが本来売る日まで確保しておく（売っている間は現金）。1回の売り・買いごとに0.1%。
当てる対象: 全部／順張り（ミネルヴィニ・新高値V2）だけ／逆張り（ボリンジャーIII・急落の底）だけ。
設計期間 2015〜2021年 / 確認期間 2022年〜。
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
import backtest_rebuy as rb
import backtest_swing as bs
from backtest_lib import COSTS, DEFAULT_CACHE, pct

COST = COSTS[2]
SLOTS = 4
STOP = 0.15
FEE = 0.01 / 252


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--seeds", type=int, default=20)
    r.add_argument("--confirm", action="store_true", help="上位の形を、別の乱数50通り・株と2倍ETF・枠を空ける形で確かめる")
    r.add_argument("--out", default="新分析ツール/バックテスト結果/2倍ETFで売って買い直す.md")
    a = ap.parse_args()
    SEEDS = range(a.seeds)
    ctx = cb.setup(a.cache, with_parts=False)
    data, members, ind, days, G, end = (ctx[k] for k in ("data", "members", "ind", "days", "G", "end"))
    pos = {}

    def idx(sym, d):
        if sym not in pos:
            pos[sym] = {x: k for k, x in enumerate(data[sym]["date"])}
        return pos[sym][d]

    def b3_exit(t):
        """押し目の指値売り。(売る日の番号, 売値) を返す"""
        s, sym = data[t["sym"]], t["sym"]
        o, h, l, c = s["o"], s["h"], s["l"], s["c"]
        i0, n, px = idx(sym, t["in"]), len(c), t["px"]
        floor, pend, j = px * (1 - STOP), False, i0
        while j < n:
            if pend:
                return j, o[j]
            if l[j] <= floor:
                return j, min(o[j] if j > i0 else px, floor)
            if j > i0 and s["bb_up"][j - 1] is not None and h[j] >= s["bb_up"][j - 1]:
                return j, max(o[j], s["bb_up"][j - 1])
            if j + 1 >= n:
                return None
            if j - i0 >= bs.MAX_HOLD or (s["pctb"][j] is not None and s["pctb"][j] >= 1.0):
                pend = True
            j += 1
        return None

    old, bs.STOP_MAX = bs.STOP_MAX, STOP
    try:
        b3_raw = bs.simulate(data, members, bs.O_method3, bs.X_upper_band, cb.START, end, ok=ctx["ok_rot"])
    finally:
        bs.STOP_MAX = old
    base = []
    for t in b3_raw:
        x = b3_exit(t)
        if x:
            base.append({"sym": t["sym"], "i0": idx(t["sym"], t["in"]), "i1": x[0], "px": t["px"], "xp": x[1], "rule": "B"})
    for rule, lst in (("C", G(ctx["CR"](10), ctx["above5"], ctx["ok_rot"], STOP, 60)),
                      ("M", G(bm2.E_base(2.0), ctx["below50"], ctx["ok_rot"], STOP)),
                      ("V", G(ctx["v2o"], ctx["below50"], ctx["ok10"], STOP))):
        for t in lst:
            i0, i1 = idx(t["sym"], t["in"]), idx(t["sym"], t["out"])
            if i1 > i0:
                base.append({"sym": t["sym"], "i0": i0, "i1": i1, "px": t["px"], "xp": t["px"] * (1 + t["ret"]), "rule": rule})
    for sym in {t["sym"] for t in base}:
        xs.prep(data[sym])
        rb.prep2(data[sym])
    print("準備ができた", file=sys.stderr)

    def sim(t, lev, sell, mode):
        """1つの枠の価値の推移。lev: 1＝株、2＝2倍ETF。mode: hold / sell / A / B。順張りは半分売り（採用ルール）も行う"""
        s = data[t["sym"]]
        o, c = s["o"], s["c"]
        i0, i1, px = t["i0"], t["i1"], t["px"]
        mv = lambda v, a_, b_: max(0.0, v * (1 + lev * (b_ / a_ - 1)))
        if i1 == i0:                                       # 買った日に損切り
            return {s["date"][i0]: mv(1 - COST, px, t["xp"]) * (1 - COST)}, 0
        e, k = mv(1 - COST, px, c[i0]), 0.0
        path = {s["date"][i0]: e}
        pend, half_done, sold_px, trips = None, t["rule"] not in ("M", "V"), None, 0
        if lev != 1:
            e *= 1 - FEE
        for j in range(i0 + 1, i1 + 1):
            d = s["date"][j]
            if j == i1:
                if e > 0:
                    e = mv(e, c[j - 1], t["xp"])
                    k += e * (1 - COST)
                    e = 0.0
                path[d] = k
                break
            if e > 0:
                e = mv(e, c[j - 1], o[j])                  # 寄り付きまで
            if pend == "sell" and e > 0:
                k, e, sold_px = k + e * (1 - COST), 0.0, o[j]
                if mode == "free":
                    path[d] = k
                    return path, trips
            elif pend == "half" and e > 0:
                k, e = k + e / 2 * (1 - COST), e / 2
            elif pend == "buy" and k > 0:
                e, k = k * (1 - COST), 0.0
                trips += 1
            pend = None
            if e > 0:
                e = mv(e, o[j], c[j])                      # 寄り付きから引けまで
                if lev != 1:
                    e *= 1 - FEE
            path[d] = k + e
            if j + 1 >= i1 or j < 2:
                continue
            try:
                if e > 0 and mode != "hold" and sell(s, j):
                    pend = "sell"
                elif e > 0 and not half_done and xc.c1(s, j):
                    pend, half_done = "half", True
                elif e == 0 and k > 0 and mode in ("A", "B"):
                    if (mode == "A" and c[j] > sold_px) or (mode == "B" and (rb.rebuy_up(s, j) or rb.rebuy_bottom(s, j))):
                        pend = "buy"
            except (TypeError, ValueError, IndexError):
                pass
        return path, trips

    def build(lev, sell, mode, rules):
        out, trips, rets = [], 0, []
        for t in base:
            path, tr_ = sim(t, lev, sell, mode if t["rule"] in rules else "hold")
            s = data[t["sym"]]
            last = max(path)
            out.append({"sym": t["sym"], "in": s["date"][t["i0"]], "out": last, "path": path})
            trips += tr_
            rets.append(path[last] - 1)
        return out, trips, sum(rets) / len(rets), sum(1 for x in rets if x > 0) / len(rets)

    is_hi = max(d for d in days if d <= cb.IS_END)
    oos_lo = min(d for d in days if d >= cb.OOS_START)

    def port(trs, seed, lo, hi):
        dd = [d for d in days if lo <= d <= hi]
        by_in = {}
        for t in trs:
            if lo <= t["in"] and t["out"] <= hi:
                by_in.setdefault(t["in"], []).append(t)
        rnd = random.Random(seed)
        cash, held, peak, mdd, eq = 1.0, [], 1.0, 0.0, 1.0
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
                held.append({"t": t, "size": size, "v": v0})
            eq = cash + sum(h["size"] * h["v"] for h in held)
            peak = max(peak, eq)
            mdd = max(mdd, 1 - eq / peak)
        yrs = (dt.date.fromisoformat(dd[-1]) - dt.date.fromisoformat(dd[0])).days / 365.25
        return max(eq, 0) ** (1 / yrs) - 1, mdd

    def evaluate(trs):
        a_ = [port(trs, 6000 + k, days[0], days[-1]) for k in SEEDS]
        i_ = [port(trs, 6000 + k, days[0], is_hi)[0] for k in SEEDS]
        o_ = [port(trs, 6000 + k, oos_lo, days[-1])[0] for k in SEEDS]
        e = {"all": cb.med([x[0] for x in a_]), "mdd": cb.med([x[1] for x in a_]), "is": cb.med(i_), "oos": cb.med(o_)}
        e["eff"] = e["all"] / e["mdd"] if e["mdd"] > 0 else 0
        return e

    if a.confirm:
        return confirm(a, build, evaluate, port, days, is_hi, oos_lo)
    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: 2倍ETFで売って買い直す\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_2x_rebuy.py\n---\n")
    w("# 2倍ETFで、早めの売りの合図で売り、買いの合図で買い直すバックテスト\n")
    w(__doc__.split("\n", 5)[5].strip() + "\n")
    w(f"年率・最大下落率は同じ日の候補の選び方をランダムにした{a.seeds}通りの中央値。「効率」は年率÷最大下落率（下落1%あたりの年率）。"
      "「1回平均・勝率」は1つの枠（買ってからルールが売るまで）の損益。\n")
    stock_tr, _, sa, sw = build(1, None, "hold", ())
    st = evaluate(stock_tr)
    etf_tr, _, ea, ew = build(2, None, "hold", ())
    cur = evaluate(etf_tr)
    w("| 土台 | 年率 | 最大下落率 | 効率 | 設計期間 | 確認期間 | 1回平均 | 勝率 |")
    w("|---|---|---|---|---|---|---|---|")
    w(f"| 株・持ち続ける（今のルール） | {pct(st['all'])} | {pct(st['mdd'])} | {st['eff']:.2f} | {pct(st['is'])} | {pct(st['oos'])} | {pct(sa, 2)} | {pct(sw, 0)} |")
    w(f"| 2倍ETF・持ち続ける | {pct(cur['all'])} | {pct(cur['mdd'])} | {cur['eff']:.2f} | {pct(cur['is'])} | {pct(cur['oos'])} | {pct(ea, 2)} | {pct(ew, 0)} |")
    print("土台", file=sys.stderr)
    groups = (("全部", ("B", "C", "M", "V")), ("順張りだけ", ("M", "V")), ("逆張りだけ", ("B", "C")))
    good = []
    for lab, sell in rb.SELLS:
        w(f"\n## {lab}\n")
        w("| 対象 | 形 | 年率 | 最大下落率 | 効率 | 設計期間 | 確認期間 | 1回平均 | 勝率 | 買い直した回数 | 2倍ETF・持ち続けると比べて |")
        w("|---|---|---|---|---|---|---|---|---|---|---|")
        for gl, rules in groups:
            for mode, ml in (("sell", "売るだけ"), ("A", "売ってAで買い直す"), ("B", "売ってBで買い直す")):
                trs, trips, avg, win = build(2, sell, mode, rules)
                e = evaluate(trs)
                both = e["is"] > cur["is"] and e["oos"] > cur["oos"]
                eff = e["eff"] > cur["eff"] and e["mdd"] < cur["mdd"]
                note = "両方の期間で年率が上" if both else ("下落が小さく効率が上" if eff else "")
                if both or eff:
                    good.append((lab, gl, ml, e, trips))
                w(f"| {gl} | {ml} | {pct(e['all'])} | {pct(e['mdd'])} | {e['eff']:.2f} | {pct(e['is'])} | {pct(e['oos'])} | "
                  f"{pct(avg, 2)} | {pct(win, 0)} | {trips} | {note} |")
                print(lab, gl, ml, file=sys.stderr)
    w("\n## まとめ（自動）\n")
    w(f"- 2倍ETF・持ち続ける: 年率 {pct(cur['all'])}、最大下落率 {pct(cur['mdd'])}、効率 {cur['eff']:.2f}（株の今のルールは効率 {st['eff']:.2f}）")
    w(f"- 両方の期間で年率が上、または下落が小さく効率が上だった形: {len(good)}通り / {len(rb.SELLS) * 9}通り")
    for lab, gl, ml, e, trips in sorted(good, key=lambda x: -x[3]["eff"]):
        w(f"  - {lab}（{gl}・{ml}）: 年率 {pct(e['all'])}、最大下落率 {pct(e['mdd'])}、効率 {e['eff']:.2f}、設計 {pct(e['is'])}、確認 {pct(e['oos'])}、買い直し {trips}回")
    w("\n## 注意\n")
    w("- 2倍ETFは元の株の値動きからの再現。実物の個別株2倍ETFは対象の銘柄が限られ、多くは2022年以降の上場。")
    w("- 売り・買い直しの合図の数値はClaudeが置いたもの。90通りを試しているので、1つだけ良い形は偶然のことがある。")
    w("- 選び方の乱数だけで年率は2〜3ポイント（2倍ETFではその倍ほど）動く。それより小さい差は偶然の範囲。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


def confirm(a, build, evaluate, port, days, is_hi, oos_lo):
    """上位の形の確認: 別の乱数50通り（5000番台）。株（1倍）と2倍ETF、売った後に枠を空ける形も比べる"""
    sells = dict(rb.SELLS)
    cands = [("かぶせ線", ("M", "V"), "順張りだけ"), ("三羽烏", ("M", "V"), "順張りだけ"), ("三羽烏", ("B", "C", "M", "V"), "全部"),
             ("パラボリックSARの反転", ("B", "C", "M", "V"), "全部"), ("出来高2倍の大陰線", ("B", "C", "M", "V"), "全部"),
             ("下放れ二本黒", ("M", "V"), "順張りだけ")]

    def ev(trs):
        a_ = [port(trs, 5000 + k, days[0], days[-1]) for k in range(50)]
        i_ = [port(trs, 5000 + k, days[0], is_hi)[0] for k in range(50)]
        o_ = [port(trs, 5000 + k, oos_lo, days[-1])[0] for k in range(50)]
        e = {"all": cb.med([x[0] for x in a_]), "mdd": cb.med([x[1] for x in a_]), "is": cb.med(i_), "oos": cb.med(o_),
             "mddmax": max(x[1] for x in a_)}
        e["eff"] = e["all"] / e["mdd"]
        return e

    L = []
    w = L.append
    w("\n## 確認: 上位の形を別の乱数50通りで（株と2倍ETF、売った後の枠の使い方）\n")
    w("「枠を確保」は売った後もルールが本来売る日まで現金で待つ形（表の上と同じ）。「枠を空ける」は売ったらその売買を終え、空いた枠で次の合図を買う形。\n")
    w("| 形 | 年率 | 最大下落率（50通りの最悪） | 効率 | 設計期間 | 確認期間 |")
    w("|---|---|---|---|---|---|")
    for lev in (1, 2):
        nm = "株" if lev == 1 else "2倍ETF"
        e = ev(build(lev, None, "hold", ())[0])
        w(f"| **{nm}・持ち続ける** | {pct(e['all'])} | {pct(e['mdd'])}（{pct(e['mddmax'])}） | {e['eff']:.2f} | {pct(e['is'])} | {pct(e['oos'])} |")
        print(nm, file=sys.stderr)
        for lab, rules, gl in cands:
            for mode, ml in (("sell", "枠を確保"), ("free", "枠を空ける")):
                e = ev(build(lev, sells[lab], mode, rules)[0])
                w(f"| {nm}・{lab}で売る（{gl}・{ml}） | {pct(e['all'])} | {pct(e['mdd'])}（{pct(e['mddmax'])}） | {e['eff']:.2f} | {pct(e['is'])} | {pct(e['oos'])} |")
                print(nm, lab, ml, file=sys.stderr)
    s = open(a.out, encoding="utf-8").read()
    i = s.find("\n## 確認:")
    j = s.find("\n## 注意")
    s = (s[:i] if i >= 0 else s[:j]) + "\n".join(L) + "\n" + s[j:]
    open(a.out, "w", encoding="utf-8").write(s)
    print(f"書き足し: {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
