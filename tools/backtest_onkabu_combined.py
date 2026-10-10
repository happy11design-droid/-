#!/usr/bin/env python3
"""恩株ツール（倍増ツール）と新分析ツールを同じ資金で組み合わせたときの成績

使い方:
  tools/backtest_onkabu_combined.py newtrades     # 新分析ツールの今の採用ルールの売買の一覧を作って保存（数分）
  tools/backtest_onkabu_combined.py run [--seeds 10] [--out FILE]

新分析ツールの売買は tools/backtest_retest.py の「今のルール」（cur_tr = build()）と同じ作り方（そのファイルは変えずに、必要な部分を写した）。
4つのルール（ボリンジャーIII・急落の底・ミネルヴィニ・新高値V2）、損切り15%、反転の合図で半分売り・かぶせ線で全部売り、逆張りの大陰線で全部売り。
新分析ツールの枠への割り当ては backtest_retest.port と同じ（4銘柄・1銘柄＝その時の資産÷4・同じ業種は2銘柄まで・優先度→乱数の順）。

倍増ツールは 恩株ツール/採用ルール.json と同じ（6カ月+100%・52週高値・売上≧10%、3銘柄、−30%損切り、189取引日、2倍で55.7%売って恩株）。

税: 両方のツールとも、売って確定した損益を暦年ごとに通算し、年末に利益の20.315%を払う（損失の繰越はしない）。
最後に持っている株・QQQには税をかけない。QQQの売買の損益には税をかけない（簡単のため）。
"""
import argparse
import datetime as dt
import json
import os
import pickle
import random
import statistics as st
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backtest_lib import DEFAULT_CACHE, load_prices

TAX = 0.20315
SELL_AT_2X = 1 / (2 - TAX)
COST = 0.001
NEW_PKL = os.path.join(DEFAULT_CACHE, "newtool_trades.pkl")


# ---------- 新分析ツールの売買の一覧（backtest_retest.py から写した） ----------

def cmd_newtrades(a):
    import backtest_combo2 as cb
    import backtest_exit_combo as xc
    import backtest_exit_signals as xs
    import backtest_minervini2 as bm2
    import backtest_rebuy as rb
    import backtest_swing as bs
    STOP, R_COST = 0.15, 0.001
    ctx = cb.setup(DEFAULT_CACHE, with_parts=False)
    data, members, ind, days, G, end = (ctx[k] for k in ("data", "members", "ind", "days", "G", "end"))
    pos = {}

    def idx(sym, d):
        if sym not in pos:
            pos[sym] = {x: k for k, x in enumerate(data[sym]["date"])}
        return pos[sym][d]

    def b3_exit(t):
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

    def rec(sym, i0, i1, px, xp, rule, prio=0):
        return {"sym": sym, "i0": i0, "i1": i1, "px": px, "xp": xp, "rule": rule, "prio": prio}

    base = []
    for t in b3_raw:
        x = b3_exit(t)
        if x:
            base.append(rec(t["sym"], idx(t["sym"], t["in"]), x[0], t["px"], x[1], "B"))

    def from_gen(lst, rule, prio=0):
        return [rec(t["sym"], idx(t["sym"], t["in"]), idx(t["sym"], t["out"]), t["px"], t["px"] * (1 + t["ret"]), rule, prio) for t in lst]

    base += from_gen(G(ctx["CR"](10), ctx["above5"], ctx["ok_rot"], STOP, 60), "C")
    base += from_gen(G(bm2.E_base(2.0), ctx["below50"], ctx["ok_rot"], STOP), "M")
    base += from_gen(G(ctx["v2o"], ctx["below50"], ctx["ok10"], STOP), "V")
    import backtest_retest as brt
    for sym in sorted({t["sym"] for t in base}):
        brt.prep_more(data[sym])

    def safe(f, s, j):
        try:
            return bool(f(s, j))
        except (TypeError, ValueError, IndexError, ZeroDivisionError, KeyError):
            return False

    TREND = ("M", "V")

    def sim(t):
        s = data[t["sym"]]
        o, c = s["o"], s["c"]
        i0, i1, px = t["i0"], t["i1"], t["px"]
        if i1 == i0:
            return {s["date"][i0]: (1 - R_COST) * t["xp"] / px * (1 - R_COST)}
        sh, k = (1 - R_COST) / px, 0.0
        path = {s["date"][i0]: sh * c[i0]}
        pend, half_done = None, t["rule"] not in TREND
        trend = t["rule"] in TREND
        for j in range(i0 + 1, i1 + 1):
            d = s["date"][j]
            if j == i1:
                path[d] = k + sh * t["xp"] * (1 - R_COST)
                break
            if pend == "sell":
                path[d] = k + sh * o[j] * (1 - R_COST)
                break
            if pend == "half":
                k += sh / 2 * o[j] * (1 - R_COST)
                sh /= 2
            pend = None
            path[d] = k + sh * c[j]
            if j + 1 >= i1:
                continue
            if trend and safe(xs.dark_cloud, s, j):
                pend = "sell"
                continue
            if not trend and safe(rb.big_bear, s, j):
                pend = "sell"
                continue
            if not half_done and safe(xc.c1, s, j):
                pend, half_done = "half", True
        return path

    out = []
    for t in base:
        p = sim(t)
        out.append({"sym": t["sym"], "in": data[t["sym"]]["date"][t["i0"]], "out": max(p), "path": p, "prio": t["prio"], "rule": t["rule"]})
    pickle.dump({"trades": out, "ind": ind, "days": days}, open(NEW_PKL, "wb"))
    print(f"新分析ツールの売買 {len(out)}件を保存（{NEW_PKL}）")


def upgrade_trades(trades, cache=DEFAULT_CACHE):
    """新分析ツールの今の形にする（2026-10-09〜）: 同じ日の候補は50日線の傾き（20日前からの上昇率、買う前の日）が小さい順、
    2倍ETFの対応表で目減り年15%未満の銘柄は2倍ETF（実測の目減り）。backtest_retest.slope3_stage と同じ作り方"""
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    tab = json.load(open(os.path.join(root, "新分析ツール", "2倍ETFの対応表.json"), encoding="utf-8"))
    drag = {u: -x["drag"] for u, x in tab.items() if isinstance(x, dict) and "drag" in x}
    has = {u for u, d in drag.items() if d < 0.15}
    px = {}
    out = []
    for t in trades:
        s = t["sym"]
        if s not in px:
            d = load_prices(cache, s)
            px[s] = (d["c"], {x: k for k, x in enumerate(d["date"])})
        c, pos = px[s]
        j = pos[t["in"]] - 1
        prio = (sum(c[j - 49:j + 1]) / 50) / (sum(c[j - 69:j - 19]) / 50) - 1 if j >= 70 else 0.0
        path = t["path"]
        if s in has:
            fee = drag[s] / 252
            e, prev, pv = 1 - COST, 1 - COST, {}
            for d in sorted(path):
                g_ = path[d]
                e = max(0.0, e * (1 + 2 * (g_ / prev - 1)) * (1 - fee))
                prev = g_
                pv[d] = e
            path = pv
        out.append({**t, "prio": prio, "path": path, "out": max(path)})
    return out, has


# ---------- 組み合わせの再現 ----------

STATS = {}


class Account:
    """1つの口座（共有なら1つ、分けるなら2つ）。cash は待っている現金（QQQに置くなら QQQ の値動きで増減）"""

    def __init__(self, cash):
        self.cash = cash
        self.dbl = {}     # sym -> {sh, px, t}
        self.new = {}     # sym -> {t: trade, size, v}
        self.onk = {}     # sym -> 株数
        self.onk_cost = {}  # sym -> 恩株の買値の合計
        self.realized = 0.0


def run(feats, new_trades, ind, days, dbl_sig, mode, seed=0, cash_px=None, split=None, fund="free", slots_d=3, slots_n=4,
        use_new=True, use_dbl=True, capital=6000.0, dedup=True, dbl_frac=None, adopt=False, lev_info=None):
    """dbl_frac: 倍増ツールの1銘柄の金額（資金に対する割合）。None なら 1/slots_d。
    adopt: 倍増ツールの合図の銘柄を新分析ツールで持っていたら、売らずに（2倍ETFならETFのまま）倍増ツールの売りのルールに切り替える。
      2倍・−30%は、その持ち株の金額（新分析ツールで買った額に対して）で判定し、189取引日は切り替えた日から数える。
    lev_info: {銘柄: (倍率, 1日の目減り)}（2倍ETFの銘柄）。結果の数（見送り・重なり）は STATS に入る"""
    """dedup: 同じ銘柄は倍増ツールを優先（新分析ツールで持っていたら倍増ツールに移し、新分析ツールは倍増ツールの銘柄を買わない）。
    False なら両方のツールが同じ銘柄を別々に持ってよい"""
    """mode: "pool"（同じ資金。倍増ツールを優先）か "split"（split＝倍増ツールの割合で口座を分ける）
    fund（pool のとき）: "free" 倍増ツールは空いている現金だけで買う／"sell" 足りなければ新分析ツールの値上がり率が低い順に売って作る"""
    rnd = random.Random(seed)
    pos = {s: {d: k for k, d in enumerate(f["date"])} for s, f in feats.items()}
    if mode == "split":
        A = Account(capital * split)       # 倍増ツール
        B = Account(capital * (1 - split))  # 新分析ツール
    else:
        A = B = Account(capital)
    accts = [A] if A is B else [A, B]
    by_in = {}
    for t in new_trades:
        by_in.setdefault(t["in"], []).append(t)
    pending = []
    curve, rcurve = [], []
    n_onk = 0
    year = days[0][:4]
    lev_info = lev_info or {}
    frac = dbl_frac if dbl_frac is not None else 1 / slots_d
    adopted = {}   # sym -> {cost, v, lev, fee, t}（倍増ツールのルールに切り替えた新分析ツールの持ち株）
    onk_v = []     # [{sym, v, lev, fee, cost}]（切り替えた持ち株が2倍になった後の恩株）
    STATS.clear()
    STATS.update({"signals": 0, "skipped": 0, "partial": 0, "overlap": 0, "adopted": 0})

    def px(s, d, k="c"):
        i = pos[s].get(d) if s in pos else None
        return None if i is None else feats[s][k][i]

    def work(acc):
        return acc.cash + sum(p["sh"] * p["px"] for p in acc.dbl.values()) + sum(h["size"] * h["v"] for h in acc.new.values())

    def close_new(acc, s, d):
        h = acc.new.pop(s)
        acc.cash += h["size"] * h["v"]
        acc.realized += h["size"] * (h["v"] - 1)

    for t, d in enumerate(days):
        if d[:4] != year:      # 年が変わった: 前の年の確定した利益に税
            for acc in accts:
                if acc.realized > 0:
                    acc.cash -= TAX * acc.realized
                acc.realized = 0.0
            year = d[:4]
        if cash_px and t > 0 and d in cash_px and days[t - 1] in cash_px:
            for acc in accts:
                if acc.cash > 0:
                    acc.cash *= cash_px[d] / cash_px[days[t - 1]]
        # 1) 倍増ツール: 寄り付きで買う
        if use_dbl:
            for s in pending:
                o = px(s, d, "o")
                if o is None or s in A.dbl or s in adopted or len(A.dbl) + len(adopted) >= slots_d:
                    continue
                STATS["signals"] += 1
                if adopt and s in B.new:
                    h = B.new.pop(s)
                    lev, fee = lev_info.get(s, (1, 0.0))
                    adopted[s] = {"cost": h["size"], "v": h["size"] * h["v"], "lev": lev, "fee": fee, "t": t}
                    STATS["adopted"] += 1
                    continue
                if s in B.new:
                    STATS["overlap"] += 1
                size = (work(A) + sum(x["v"] for x in adopted.values())) * frac
                if dedup and s in A.new:        # 同じ銘柄を新分析ツールで持っていたら、倍増ツールに移す（寄り付きの値で）
                    close_new(A, s, d)
                if A.cash < size and mode == "pool" and fund == "sell":
                    for s2 in sorted(A.new, key=lambda x: A.new[x]["v"]):
                        if A.cash >= size:
                            break
                        close_new(A, s2, d)
                amt = min(A.cash, size)
                if amt < 50:
                    STATS["skipped"] += 1
                    continue
                if amt < size * 0.5:
                    STATS["partial"] += 1
                A.dbl[s] = {"sh": amt / (o * (1 + COST)), "px": o * (1 + COST), "t": t}
                A.cash -= amt
            pending = []
        # 2) 新分析ツール: その日の値動きと手じまい
        if use_new:
            for s in list(B.new):
                h = B.new[s]
                v = h["t"]["path"].get(d)
                if v is not None:
                    h["v"] = v
                if h["t"]["out"] == d:
                    close_new(B, s, d)
            # 新しい売買（その日に買う）
            todays = sorted(by_in.get(d, []), key=lambda x: (x["prio"], rnd.random()))
            eqB = work(B)
            for tr in todays:
                s = tr["sym"]
                if s in B.new or (dedup and s in A.dbl):
                    continue
                if len(B.new) >= slots_n:
                    break
                if sum(1 for x in B.new if ind.get(x) == ind.get(s)) >= 2:
                    continue
                size = min(eqB / slots_n, B.cash)
                if size <= 50:
                    break
                B.cash -= size
                v0 = tr["path"].get(d, 1.0)
                if tr["out"] == d:
                    B.cash += size * v0
                    B.realized += size * (v0 - 1)
                    continue
                B.new[s] = {"t": tr, "size": size, "v": v0}
        # 3) 倍増ツール: 終値で 2倍・損切り・期限
        if use_dbl:
            for s in list(A.dbl):
                p = A.dbl[s]
                c = px(s, d)
                if c is None:
                    if d > feats[s]["date"][-1]:
                        c = feats[s]["c"][-1]
                        A.cash += p["sh"] * c * (1 - COST)
                        A.realized += p["sh"] * (c * (1 - COST) - p["px"])
                        del A.dbl[s]
                    continue
                if c >= 2 * p["px"]:
                    sell = p["sh"] * SELL_AT_2X
                    A.cash += sell * c * (1 - COST)
                    A.realized += sell * (c * (1 - COST) - p["px"])
                    A.onk[s] = A.onk.get(s, 0.0) + p["sh"] - sell
                    A.onk_cost[s] = A.onk_cost.get(s, 0.0) + (p["sh"] - sell) * p["px"]
                    n_onk += 1
                    del A.dbl[s]
                elif c <= p["px"] * 0.7 or t - p["t"] >= 189:
                    A.cash += p["sh"] * c * (1 - COST)
                    A.realized += p["sh"] * (c * (1 - COST) - p["px"])
                    del A.dbl[s]
            # 切り替えた持ち株（倍増ツールのルール）
            for s in list(adopted):
                x = adopted[s]
                c, i = px(s, d), pos[s].get(d) if s in pos else None
                if c is not None and i:
                    r = c / feats[s]["c"][i - 1] - 1
                    x["v"] = max(0.0, x["v"] * (1 + x["lev"] * r) * (1 - x["fee"]))
                if x["v"] >= 2 * x["cost"]:
                    sv = x["v"] * SELL_AT_2X
                    A.cash += sv * (1 - COST)
                    A.realized += sv * (1 - COST) - SELL_AT_2X * x["cost"]
                    onk_v.append({"sym": s, "v": x["v"] - sv, "lev": x["lev"], "fee": x["fee"], "cost": x["cost"] * (1 - SELL_AT_2X)})
                    n_onk += 1
                    del adopted[s]
                elif x["v"] <= 0.7 * x["cost"] or t - x["t"] >= 189 or (c is None and d > feats[s]["date"][-1]):
                    A.cash += x["v"] * (1 - COST)
                    A.realized += x["v"] * (1 - COST) - x["cost"]
                    del adopted[s]
            for x in onk_v:
                c, i = px(x["sym"], d), pos[x["sym"]].get(d) if x["sym"] in pos else None
                if c is not None and i:
                    x["v"] = max(0.0, x["v"] * (1 + x["lev"] * (c / feats[x["sym"]]["c"][i - 1] - 1)) * (1 - x["fee"]))
            # 合図（翌日の寄り付きで買う。6カ月の上昇が大きい順）
            free = slots_d - len(A.dbl) - len(adopted)
            if free > 0:
                hits = [s for s in dbl_sig.get(d, ()) if s not in A.dbl and s not in adopted]
                hits.sort(key=lambda s: -feats[s]["r126"][pos[s][d]])
                pending = hits[:free]
        eq = 0.0
        for acc in accts:
            eq += acc.cash + sum(h["size"] * h["v"] for h in acc.new.values())
            for s, p in acc.dbl.items():
                c = px(s, d)
                eq += p["sh"] * (c if c is not None else feats[s]["c"][-1])
            for s, sh in acc.onk.items():
                c = px(s, d)
                eq += sh * (c if c is not None else feats[s]["c"][-1])
        eq += sum(x["v"] for x in adopted.values()) + sum(x["v"] for x in onk_v)
        curve.append(eq)
        # 確定した損益だけ: 持っている株・恩株は買った額のまま（恩株は2倍で売った残りの株の買値）
        req = 0.0
        for acc in accts:
            req += acc.cash + sum(h["size"] for h in acc.new.values()) + sum(p["sh"] * p["px"] for p in acc.dbl.values())
            req += sum(acc.onk_cost.get(s, 0.0) for s in acc.onk)
        req += sum(x["cost"] for x in adopted.values()) + sum(x["cost"] for x in onk_v)
        rcurve.append(req)
    return curve, n_onk, rcurve


def metrics(curve, days):
    yrs = (dt.date.fromisoformat(days[-1]) - dt.date.fromisoformat(days[0])).days / 365.25
    peak = mdd = 0.0
    for v in curve:
        peak = max(peak, v)
        mdd = max(mdd, 1 - v / peak)
    return (curve[-1] / curve[0]) ** (1 / yrs) - 1, mdd


CONDS = [("2015〜2020年", "2015-01-02", "2020-12-31", ()), ("2021年〜", "2021-01-04", "9999", ()),
         ("2015年〜 NVDAを除く", "2015-01-02", "9999", ("NVDA",)), ("2019年〜 NVDAを除く", "2019-01-02", "9999", ("NVDA",))]

VARIANTS = [
    ("倍増ツールだけ（待っている現金はQQQ）", dict(mode="pool", use_new=False, cash="QQQ")),
    ("倍増ツールだけ（待っている現金は0%）", dict(mode="pool", use_new=False, cash=None)),
    ("新分析ツールだけ（待っている現金は0%）", dict(mode="pool", use_dbl=False, cash=None)),
    ("新分析ツールだけ（待っている現金はQQQ）", dict(mode="pool", use_dbl=False, cash="QQQ")),
    ("同じ資金・倍増優先（空いた現金だけで買う）・残りは新分析・それでも余る現金は0%", dict(mode="pool", fund="free", cash=None)),
    ("同じ資金・倍増優先（空いた現金だけで買う）・残りは新分析・余る現金はQQQ", dict(mode="pool", fund="free", cash="QQQ")),
    ("同じ資金・倍増優先（足りなければ新分析を売って買う）・余る現金は0%", dict(mode="pool", fund="sell", cash=None)),
    ("同じ資金・倍増優先（足りなければ新分析を売って買う）・余る現金はQQQ", dict(mode="pool", fund="sell", cash="QQQ")),
    ("資金を分ける 倍増50%・新分析50%（余る現金はQQQ）", dict(mode="split", split=0.5, cash="QQQ")),
    ("資金を分ける 倍増33%・新分析67%（余る現金はQQQ）", dict(mode="split", split=1 / 3, cash="QQQ")),
    ("資金を分ける 倍増67%・新分析33%（余る現金はQQQ）", dict(mode="split", split=2 / 3, cash="QQQ")),
    ("資金を分ける 倍増50%・新分析50%（余る現金は0%）", dict(mode="split", split=0.5, cash=None)),
    ("同じ資金・同じ銘柄も両方で持つ・倍増の資金が足りなければ新分析を売る・余る現金はQQQ", dict(mode="pool", fund="sell", cash="QQQ", dedup=False)),
    ("同じ資金・同じ銘柄も両方で持つ・倍増は空いた現金だけで買う・余る現金はQQQ", dict(mode="pool", fund="free", cash="QQQ", dedup=False)),
    ("資金を分ける 倍増50%・新分析50%・同じ銘柄も両方で持つ（余る現金はQQQ）", dict(mode="split", split=0.5, cash="QQQ", dedup=False)),
    ("資金を分ける 倍増33%・新分析67%・同じ銘柄も両方で持つ（余る現金はQQQ）", dict(mode="split", split=1 / 3, cash="QQQ", dedup=False)),
    ("資金を分ける 倍増67%・新分析33%・同じ銘柄も両方で持つ（余る現金はQQQ）", dict(mode="split", split=2 / 3, cash="QQQ", dedup=False)),
    ("資金を分ける 倍増20%・新分析80%・同じ銘柄も両方で持つ（余る現金はQQQ）", dict(mode="split", split=0.2, cash="QQQ", dedup=False)),
]


VARIANTS18 = [("新分析ツールだけ（余る現金はQQQ）", dict(mode="pool", use_dbl=False, cash="QQQ")),
              ("倍増ツールだけ（余る現金はQQQ）", dict(mode="pool", use_new=False, cash="QQQ"))]
for _n, _f in ((4, 1 / 3), (5, 1 / 3), (6, 1 / 3), (4, 1 / 4), (5, 1 / 4), (6, 1 / 4), (4, 1 / 5)):
    for _ad in (False, True):
        VARIANTS18.append((f"新分析 資金÷{_n}・倍増 資金÷{round(1 / _f)}・" + ("同じ銘柄は新分析の持ち株を倍増のルールに切り替え" if _ad else "同じ銘柄も両方で持つ"),
                           dict(mode="pool", fund="free", cash="QQQ", dedup=False, slots_n=_n, dbl_frac=_f, adopt=_ad)))


def cmd_run(a):
    import backtest_onkabu_search as bs_
    import onkabu_lib as ol
    members, spy, feats = bs_.load_all()
    nt = pickle.load(open(NEW_PKL, "rb"))
    new_trades, ind = nt["trades"], nt["ind"]
    has2x = set()
    if a.form == "current":
        new_trades, has2x = upgrade_trades(new_trades)
    # 倍増ツールの株価に新分析ツールの銘柄も要る（同じ銘柄の移し替えで使うのは倍増側だけなので不要）
    sig = {"mom": ("r126", 1.0), "hi": "nh", "rev": 0.1, "extra": None}
    q = load_prices(DEFAULT_CACHE, "QQQ")
    qqq = dict(zip(q["date"], q["c"]))

    def sig_by_day(ex):
        out = {}
        for s, f in feats.items():
            if s in ex:
                continue
            m = ol.signal(f, sig) & f["member"]
            m[:260] = False
            for i in np.nonzero(m)[0]:
                out.setdefault(f["date"][i], []).append(s)
        return out

    sbd = {(): sig_by_day(()), ("NVDA",): sig_by_day(("NVDA",))}
    bench = {}
    for name, lo, hi, ex in CONDS:
        days = [d for d in spy["date"] if lo <= d <= hi]
        for sym in ("SPY", "QQQ"):
            d0 = load_prices(DEFAULT_CACHE, sym)
            c = [d0["c"][d0["date"].index(x)] for x in days]
            bench[(name, sym)] = metrics(c, days)
    rows = []
    VS = VARIANTS18 if a.set == "18000" else VARIANTS
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    tab = json.load(open(os.path.join(root, "新分析ツール", "2倍ETFの対応表.json"), encoding="utf-8"))
    lev_info = {u: (2, -x["drag"] / 252) for u, x in tab.items() if isinstance(x, dict) and "drag" in x and u in has2x}
    cap = 18000.0 if a.set == "18000" else 6000.0
    stats_rows = []
    for label, kw in (VS[-a.last:] if a.last else VS):
        cells = []
        for name, lo, hi, ex in CONDS:
            days = [d for d in spy["date"] if lo <= d <= hi]
            nts = [t for t in new_trades if lo <= t["in"] and t["sym"] not in ex]
            res = []
            for seed in range(a.seeds):
                kw2 = {k: v for k, v in kw.items() if k != "cash"}
                curve, n_onk, rcurve = run(feats, nts, ind, days, sbd[ex], seed=seed, cash_px=qqq if kw.get("cash") == "QQQ" else None,
                                           capital=cap, lev_info=lev_info, **kw2)
                c, m = metrics(curve, days)
                res.append((c, m, n_onk, metrics(rcurve, days)[1]))
                if seed == 0 and name == "2015年〜 NVDAを除く" and kw.get("use_new", True) and kw.get("use_dbl", True):
                    stats_rows.append((label, dict(STATS)))
            cells.append(tuple(st.median(r[k] for r in res) for k in range(4)))
        rows.append((label, cells))
        print(label, [f"{c:.1%}/{m:.0%}/{rm:.0%}" for c, m, _, rm in cells], flush=True)
    out = []
    w = out.append
    w("---\ntype: backtest\ntitle: 倍増ツールと新分析ツールの組み合わせ\n"
      f"created: {dt.date.today().isoformat()}\nscript: tools/backtest_onkabu_combined.py\n---\n")
    w("# 倍増ツール（恩株ツール）と新分析ツールの組み合わせ（資金6,000ドル）\n")
    if a.summary and os.path.exists(a.summary):
        w(open(a.summary).read())
    w("## 前提\n")
    w("- 倍増ツール: `恩株ツール/採用ルール.json`（6カ月+100%・52週高値・売上≧10%、3銘柄、−30%損切り、189取引日、2倍で55.7%売って恩株）")
    w("- 新分析ツール: 今の採用ルール（ボリンジャーIII・急落の底・ミネルヴィニ・新高値V2、4銘柄、損切り15%、半分売り・かぶせ線・大陰線）。"
      "`tools/backtest_retest.py` の「今のルール」と同じ売買の一覧（後知恵なしの監視銘柄）"
      + ("。**2026-10-09〜の今の形: 同じ日の候補は50日線の傾きが小さい順、2倍ETFの対応表で目減り年15%未満の"
         f"{len(has2x)}銘柄は2倍ETF（実測の目減り）**（`backtest_retest.py --stage slope3` と同じ作り方）" if a.form == "current" else "（株だけ・ランダムな順の古い形）"))
    w("- 同じ資金のときは倍増ツールを優先: 倍増ツールの合図の銘柄を新分析ツールで持っていたら、倍増ツールに移す。新分析ツールは倍増ツールが持っている銘柄を買わない")
    w("- 税: 両方とも、売って確定した損益を暦年ごとに通算して年末に20.315%（損失の繰越なし）。最後に持っている株・QQQには税をかけない。売買コスト片道0.1%")
    w(f"- 新分析ツールの買う順番は乱数で、{a.seeds}通りの中央値\n")
    w("## 結果（年率（含み損込みの最大下落率・確定した損益だけの最大下落率））\n")
    w("| 組み合わせ | " + " | ".join(c[0] for c in CONDS) + " |")
    w("|---|" + "---|" * len(CONDS))
    w("| （比べる相手）SPYを持ち続ける | " + " | ".join(f"{bench[(c[0], 'SPY')][0]:.1%}（{bench[(c[0], 'SPY')][1]:.0%}）" for c in CONDS) + " |")
    w("| （比べる相手）QQQを持ち続ける | " + " | ".join(f"{bench[(c[0], 'QQQ')][0]:.1%}（{bench[(c[0], 'QQQ')][1]:.0%}）" for c in CONDS) + " |")
    for label, cells in rows:
        w(f"| {label} | " + " | ".join(f"{c:.1%}（{m:.0%}・確定{rm:.0%}）" for c, m, _, rm in cells) + " |")
    if stats_rows:
        w("\n## 倍増ツールの合図の扱い（2015年〜 NVDAを除く・乱数1通り）\n")
        w("| 組み合わせ | 倍増ツールの合図（枠が空いていた回数） | 現金がなく見送り | 半分未満しか買えず | 同じ銘柄を両方で持った | 新分析の持ち株を倍増のルールに切り替え |")
        w("|---|---|---|---|---|---|")
        for label, st_ in stats_rows:
            w(f"| {label} | {st_['signals']} | {st_['skipped']} | {st_['partial']} | {st_['overlap']} | {st_['adopted']} |")
    text = "\n".join(out) + "\n"
    if a.out:
        open(a.out, "w").write(text)
    print(text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("newtrades", "run"))
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--out")
    ap.add_argument("--summary")
    ap.add_argument("--last", type=int, default=0, help="最後のN通りだけ計算する")
    ap.add_argument("--set", default="", help="18000: 資金18,000ドルで、1銘柄の金額の決め方と切り替えの形を比べる")
    ap.add_argument("--form", default="current", choices=("current", "old"), help="新分析ツールの形。current: 50日線の傾きが小さい順・2倍ETF（今の形）")
    a = ap.parse_args()
    {"newtrades": cmd_newtrades, "run": cmd_run}[a.cmd](a)


if __name__ == "__main__":
    main()
