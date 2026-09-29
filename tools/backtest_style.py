#!/usr/bin/env python3
"""ユーザーの売買の仕方（分割・買い増し・買い下がり・損切りなし・トレールストップ）と、
マット・ペトラリア氏の手じまい（損切り3〜4%・リスクリワード1〜1.5で半分利確・建値へ引き上げ）を再現するバックテスト

使い方:
  tools/backtest_style.py run [--out FILE]

買いの合図は採用中の4つのルール（ボリンジャーIII・ミネルヴィニ・急落の底 RSI(2)≦10・新高値V2）と、
ペトラリア氏の買い方をClaudeが数値にしたもの（下の P）。同時に4銘柄、1銘柄の枠は資金の25%、同じ業種は2銘柄まで。
1銘柄の枠（25%）は買った日に確保し、分割で買っていない分はその枠の中で現金のまま持つ（ほかの銘柄には使わない）。
売買は引け後に判定して翌日の寄り付き。損切り（逆指値）と部分利確（指値）だけは日中の値で判定する。片道0.1%。

形:
  S0 今のルール: 合図の日に枠の全額を買う。損切り15%、ルールの手じまい
  U  ユーザーの形: 合図の日に枠の1/3を買う。上がったら（平均の買値から +a1%・+a2%）1/3ずつ買い増し、
     下がったら（最初の買値から −d1%・−d2%）1/3ずつ買い下がる（合計3回まで）。損切りはしない（または非常時だけ）。
     売り: 平均の買値から +act% 以上になったらトレールストップ（それまでの一番高い終値から −trail%）を有効にする。
     ルールの手じまいの合図は、利益が出ているときだけ使う（下がっている間は戻るまで持つ）。最長250取引日で打ち切り
  P  ペトラリア氏の手じまい: 合図の日に全額。損切りは買値の4%下。買値から+6%（リスクの1.5倍）で半分を利確し、損切りを買値へ引き上げる。
     残りはルールの手じまい、または10取引日（本の「1日から2週間」）で手じまう
  PE ペトラリア氏の買い方（Claudeが数値にしたもの）: 20日線と50日線が上向き（5日前より上）、終値が50日線より上、
     直前15日以内の20日の最高値から4%以上押した後（旗・くさびの調整）、終値が直前3日の高値を上抜け、かつ20日線より上
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
from backtest_lib import DEFAULT_CACHE, is_member, pct

COST = 0.001
SLOTS = 4
START, IS_END, OOS_START = cb.START, cb.IS_END, cb.OOS_START
SEEDS = range(10)
MAX_HOLD = 250
med = cb.med


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/ユーザーの売買の仕方とペトラリア氏の手じまい.md")
    a = ap.parse_args()
    ctx = cb.setup(a.cache, with_parts=False)
    data, members, ind, days, end = (ctx[k] for k in ("data", "members", "ind", "days", "end"))
    ok_rot, ok10 = ctx["ok_rot"], ctx["ok10"]
    dset = set(days)

    def up5(arr, i):
        return arr[i] is not None and arr[i - 5] is not None and arr[i] > arr[i - 5]

    def E_pet(i, s):
        c, h, m20, m50 = s["c"], s["h"], s["bb_mid"], s["ma50"]
        if i < 30 or m50[i] is None or m20[i] is None or not (up5(m20, i) and up5(m50, i)) or c[i] <= m50[i] or c[i] <= m20[i]:
            return None
        k = max(range(i - 15, i - 2), key=lambda j: h[j])
        if h[k] < max(h[i - 20:i]):
            return None          # 直前15日以内に20日の最高値がない
        if min(s["l"][k:i]) > h[k] * 0.96:
            return None          # 4%以上の押しがない
        if c[i] <= max(h[i - 3:i]):
            return None
        return -(s["rs"][i] or 0)

    band = lambda j, s: s["pctb"][j] is not None and s["pctb"][j] >= 1.0
    b50 = lambda j, s: s["ma50"][j] is not None and s["c"][j] < s["ma50"][j]
    a5 = lambda j, s: s["ma5"][j] is not None and s["c"][j] > s["ma5"][j]
    RULES = {
        "B": (lambda i, s: (bs.O_method3(i, s) or {}).get("rank"), band, ok_rot),
        "M": (bm2.E_base(2.0), b50, ok_rot),
        "C": (ctx["CR"](10), a5, ok_rot),
        "V": (ctx["v2o"], b50, ok10),
        "PE": (E_pet, b50, ok_rot),
    }

    # 合図を一度だけ集める（銘柄ごとに、日付順）
    sig = {k: {} for k in RULES}
    for sym, s in data.items():
        n = len(s["c"])
        for i in range(200, n - 1):
            d = s["date"][i]
            if d < START or d > end:
                continue
            for k, (e, _, ok) in RULES.items():
                if not ok(s, i, members[sym]):
                    continue
                rk = e(i, s)
                if rk is not None:
                    sig[k].setdefault(sym, []).append((i, rk))
    print({k: sum(len(v) for v in x.values()) for k, x in sig.items()}, file=sys.stderr)

    def position(s, i, xrule, P):
        """i日の合図 → i+1日の寄り付きから。返り値: (手じまいの日のインデックス, {日付: 枠の価値（最初を1）}, 情報)"""
        o, h, l, c, n = s["o"], s["h"], s["l"], s["c"], len(s["c"])
        e = i + 1
        if e >= n:
            return None
        cash, sh, cost_sum, buys = 1.0, 0.0, 0.0, 0
        path, info = {}, {"worst": 0.0}

        def buy(px, frac):
            nonlocal cash, sh, cost_sum, buys
            amt = min(frac, cash)
            if amt <= 1e-9:
                return
            cash -= amt
            sh += amt * (1 - COST) / px
            cost_sum += amt
            buys += 1

        def sell(px, frac_sh):
            nonlocal cash, sh
            q = sh * frac_sh
            cash += q * px * (1 - COST)
            sh -= q

        first = o[e]
        buy(first, P["f0"])
        adds_up, adds_dn = list(P.get("up", ())), list(P.get("dn", ()))
        peak, stop, took = 0.0, (first * (1 - P["stop"]) if P.get("stop") else None), False
        pend = None
        j = e
        while True:
            if j > e:
                if pend == "exit":
                    sell(o[j], 1.0)
                    path[s["date"][j]] = cash
                    return j, path, info
                if isinstance(pend, float):
                    buy(o[j], pend)
                pend = None
            # 日中: 損切り・部分利確
            if sh > 0 and stop is not None and l[j] <= stop:
                sell(min(o[j], stop) if j > e else min(first, stop), 1.0)
                path[s["date"][j]] = cash
                return j, path, info
            if sh > 0 and P.get("take") and not took:
                tp = first * (1 + P["take"])
                if h[j] >= tp:
                    sell(max(o[j], tp) if j > e else tp, P.get("take_frac", 0.5))
                    took = True
                    stop = first       # 建値へ引き上げ
            val = cash + sh * c[j]
            path[s["date"][j]] = val
            avgpx = (cost_sum * (1 - COST)) / sh if sh > 0 else None
            info["worst"] = min(info["worst"], val - 1)
            k = j - e
            if j + 1 >= n:
                return j, path, info
            # 引けの判定 → 翌日の寄り付き
            peak = max(peak, c[j])
            prof = avgpx is not None and c[j] > avgpx
            ex = False
            if P.get("mode") == "user":
                if P.get("hard") and avgpx and c[j] <= avgpx * (1 - P["hard"]):
                    ex = True
                if avgpx and c[j] >= avgpx * (1 + P["act"]):
                    P_on = True
                else:
                    P_on = info.get("trail_on", False)
                if P_on:
                    info["trail_on"] = True
                    if c[j] <= peak * (1 - P["trail"]):
                        ex = True
                if P.get("rule_exit", True) and xrule(j, s) and prof:
                    ex = True
                if not ex and cash > 1e-9:
                    if adds_up and avgpx and c[j] >= first * (1 + adds_up[0]):
                        adds_up.pop(0)
                        pend = P["step"]
                    elif adds_dn and c[j] <= first * (1 - adds_dn[0]):
                        adds_dn.pop(0)
                        pend = P["step"]
            else:
                if xrule(j, s):
                    ex = True
                if P.get("days") and took and k >= P["days"]:
                    ex = True
                if P.get("days_all") and k >= P["days_all"]:
                    ex = True
            if k >= MAX_HOLD:
                ex = True
            if ex:
                pend = "exit"
            j += 1

    def trades(keys, P):
        out = []
        for k in keys:
            xrule = RULES[k][1]
            for sym, lst in sig[k].items():
                s = data[sym]
                nxt = 0
                for i, rk in lst:
                    if i < nxt:
                        continue
                    res = position(s, i, xrule, dict(P))
                    if res is None:
                        continue
                    x, path, info = res
                    out.append({"sym": sym, "in": s["date"][i + 1], "out": s["date"][x], "rank": rk, "path": path,
                                "ret": path[s["date"][x]] - 1, "worst": min(path.values()) - 1, "hold": x - i - 1, "rule": k})
                    nxt = x + 1
        return out

    def port(tr, seed=None, lo=None, hi=None):
        lo, hi = lo or days[0], hi or days[-1]
        dd = [d for d in days if lo <= d <= hi]
        tr = [t for t in tr if lo <= t["in"] and t["out"] <= hi]
        by_in = {}
        for t in tr:
            by_in.setdefault(t["in"], []).append(t)
        rnd = random.Random(seed)
        cash, held, curve, peak, mdd = 1.0, [], [], 1.0, 0.0
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
            cands = by_in.get(d, [])
            cands = sorted(cands, key=lambda t: (t["rank"], t["sym"])) if seed is None else sorted(cands, key=lambda t: rnd.random())
            for t in cands:
                if len(held) >= SLOTS:
                    break
                if any(h["t"]["sym"] == t["sym"] for h in held):
                    continue
                if sum(1 for h in held if ind.get(h["t"]["sym"]) == ind.get(t["sym"])) >= 2:
                    continue
                size = min(eq / SLOTS, cash)
                if size <= 0:
                    break
                cash -= size
                h = {"t": t, "size": size, "v": t["path"].get(d, 1.0)}
                if t["out"] == d:
                    cash += size * h["v"]
                    continue
                held.append(h)
            eq = cash + sum(h["size"] * h["v"] for h in held)
            curve.append(eq)
            peak = max(peak, eq)
            mdd = max(mdd, 1 - eq / peak)
        yrs = (dt.date.fromisoformat(dd[-1]) - dt.date.fromisoformat(dd[0])).days / 365.25
        return {"cagr": curve[-1] ** (1 / yrs) - 1, "mdd": mdd, "curve": curve, "days": dd}

    years = sorted({d[:4] for d in days})

    def evaluate(tr):
        rs = [port(tr, seed=k) for k in SEEDS]
        is_ = [port(tr, seed=k, hi=IS_END)["cagr"] for k in SEEDS]
        oos = [port(tr, seed=k, lo=OOS_START)["cagr"] for k in SEEDS]
        yr = {}
        for y in years:
            vals = []
            for p in rs:
                idx = [k for k, d in enumerate(p["days"]) if d[:4] == y]
                a0 = p["curve"][idx[0] - 1] if idx[0] > 0 else 1.0
                vals.append(p["curve"][idx[-1]] / a0 - 1)
            yr[y] = med(vals)
        rk = port(tr)
        n = len(days) / 252
        win = sum(t["ret"] > 0 for t in tr) / len(tr) if tr else 0
        return {"all": med([p["cagr"] for p in rs]), "rng": (min(p["cagr"] for p in rs), max(p["cagr"] for p in rs)),
                "mdd": med([p["mdd"] for p in rs]), "is": med(is_), "oos": med(oos), "yr": yr, "rank": rk,
                "n": len(tr) / n, "win": win, "hold": sum(t["hold"] for t in tr) / max(1, len(tr)),
                "worst": min((t["worst"] for t in tr), default=0), "long": sum(t["hold"] >= 120 for t in tr) / max(1, len(tr)),
                "avg": sum(t["ret"] for t in tr) / max(1, len(tr))}

    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: ユーザーの売買の仕方とペトラリア氏の手じまい\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_style.py\n---\n")
    w("# ユーザーの売買の仕方（分割・買い増し・買い下がり）と、ペトラリア氏の手じまいのバックテスト\n")
    w(__doc__.split("\n", 5)[5].strip() + "\n")
    w("年率・最大下落率は同じ日の候補の選び方をランダムにした10通りの中央値。後知恵なしの監視銘柄（S&P500）。"
      "「1銘柄の最大の含み損」は、1つの枠（資金の25%）が一番減ったときの割合（枠に対して）。\n")
    head = ("| 形 | 年率 2015年〜（幅） | 最大下落率 | 設計期間 | 確認期間 | 最悪の年 | RSの高い順 年率 / 最大下落率 | "
            "売買の件数/年 | 勝率 | 1回の平均（枠に対して） | 平均保有日数 | 120日以上持った割合 | 1つの枠の最大の含み損 |")
    sep = "|---|---|---|---|---|---|---|---|---|---|---|---|---|"
    summary = []

    def row(lab, e):
        wy = min(years, key=lambda y: e["yr"][y])
        summary.append((lab, e))
        return (f"| {lab} | {pct(e['all'])}（{pct(e['rng'][0])}〜{pct(e['rng'][1])}） | {pct(e['mdd'])} | {pct(e['is'])} | {pct(e['oos'])} | "
                f"{wy}年 {pct(e['yr'][wy], 0)} | {pct(e['rank']['cagr'])} / {pct(e['rank']['mdd'])} | {e['n']:.0f} | {pct(e['win'])} | "
                f"{pct(e['avg'], 2)} | {e['hold']:.0f} | {pct(e['long'])} | {pct(e['worst'])} |")

    S0 = dict(mode="rule", f0=1.0, stop=0.15)
    U = dict(mode="user", f0=1 / 3, step=1 / 3, up=(0.05, 0.10), dn=(0.07, 0.14), act=0.05, trail=0.08)
    PET = dict(mode="rule", f0=1.0, stop=0.04, take=0.06, take_frac=0.5, days=10)
    ALL, REV = ("B", "M", "C", "V"), ("B", "C")

    for title, keys in (("4つのルール", ALL), ("逆張りの2つだけ（ボリンジャーIII・急落の底）", REV)):
        print(title, file=sys.stderr)
        w(f"\n## 1. 売り方の比較（{title}）\n")
        w(head)
        w(sep)
        w(row("S0 今のルール（全額・損切り15%・ルールの手じまい）", evaluate(trades(keys, S0))))
        w(row("U ユーザーの形（1/3ずつ、+5%・+10%で買い増し、−7%・−14%で買い下がり、損切りなし、+5%からトレール8%）", evaluate(trades(keys, U))))
        w(row("U＋非常時の損切り（平均の買値から−30%）", evaluate(trades(keys, {**U, "hard": 0.30}))))
        w(row("U＋非常時の損切り（平均の買値から−20%）", evaluate(trades(keys, {**U, "hard": 0.20}))))
        w(row("U 買い下がりだけ（上がったときは買い増さない）", evaluate(trades(keys, {**U, "up": ()}))))
        w(row("U 上がったときの買い増しだけ（買い下がらない）・損切り15%", evaluate(trades(keys, {**U, "dn": (), "hard": 0.15}))))
        w(row("U 分割せず全額・損切りなし・トレール8%", evaluate(trades(keys, {**U, "f0": 1.0, "up": (), "dn": ()}))))
        w(row("P ペトラリア氏の手じまい（損切り4%・+6%で半分利確・建値へ・残りは10日かルールの手じまい）", evaluate(trades(keys, PET))))
        w(row("P 損切り3%・+3%（1倍）で半分利確", evaluate(trades(keys, {**PET, "stop": 0.03, "take": 0.03}))))
        w(row("P 残りはルールの手じまいまで持つ（10日で切らない）", evaluate(trades(keys, {**PET, "days": None}))))

    print("PE", file=sys.stderr)
    w("\n## 2. ペトラリア氏の買い方（Claudeが数値にしたもの）\n")
    w(head)
    w(sep)
    w(row("PE＋ペトラリア氏の手じまい（単独）", evaluate(trades(("PE",), PET))))
    w(row("PE＋今の手じまい（損切り15%・50日線割れ）（単独）", evaluate(trades(("PE",), S0))))
    w(row("PE＋ユーザーの形（単独）", evaluate(trades(("PE",), U))))
    w(row("4つのルール＋PE（今の手じまい）", evaluate(trades(ALL + ("PE",), S0))))
    w(row("4つのルール＋PE（ペトラリア氏の手じまい）", evaluate(trades(ALL + ("PE",), PET))))

    print("sens", file=sys.stderr)
    w("\n## 3. ユーザーの形の数値を変えた場合（4つのルール）\n")
    w(head)
    w(sep)
    for tr_ in (0.05, 0.12):
        w(row(f"トレール{int(tr_ * 100)}%", evaluate(trades(ALL, {**U, "trail": tr_}))))
    for act in (0.03, 0.10):
        w(row(f"トレールを有効にする利益 +{int(act * 100)}%", evaluate(trades(ALL, {**U, "act": act}))))
    for dn in ((0.05, 0.10), (0.10, 0.20)):
        w(row(f"買い下がり −{int(dn[0] * 100)}%・−{int(dn[1] * 100)}%", evaluate(trades(ALL, {**U, "dn": dn}))))
    w(row("ルールの手じまいを使わない（トレールだけ）", evaluate(trades(ALL, {**U, "rule_exit": False}))))

    w("\n## 注意\n")
    w("- ユーザーの形は、枠（資金の25%）を買った日に確保し、まだ買っていない分は現金のまま持つ。そのぶん資金の使われ方が少なくなる。")
    w("- 損切りしない形は、最長250取引日（約1年）で打ち切っている。実際にはもっと長く持つことになる銘柄がある。")
    w("- ペトラリア氏の買い方（PE）の数値（20日線・50日線の向き、15日・4%・3日）は、マニュアルの「上昇トレンド中の旗・くさび・下降トレンドラインの上抜け」をClaudeが数値にしたもの。マニュアルに数値はない。"
      "買い増し・買い下がり、1銘柄の資金の割合、トレールストップの数値は「マニュアルに規定なし」（NotebookLM 2026-09-29 の回答）。")
    w("- 業種は今のYahooの分類を過去にも使っている。NASDAQ100は含めていない。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
