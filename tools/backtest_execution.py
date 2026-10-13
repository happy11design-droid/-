#!/usr/bin/env python3
"""同じ買い・売りの合図のまま、注文の出し方と枠の使い方を工夫するバックテスト

使い方:
  tools/backtest_execution.py run [--out FILE]

今の採用ルール（4つのルール、4銘柄・1銘柄25%、損切り15%、急落の底RSI(2)≦10、同じ業種2銘柄まで）に対して:
  1. 候補が枠より多い日の選び方: ランダム（基本）／RSの高い順（今のツール）／値動き（ATR÷株価）の大きい順
  2. 押し目（ボリンジャーIII）・急落の底を、寄り付きの1%・2%・3%下の指値で買う（その日の安値が届かなければ買わない）
  3. 押し目の売りを、前日の引け時点の上のバンドの値段に指値を置いて、届いた日に売る（今は引けで上のバンド以上→翌日の寄り付き）
  4. 押し目の利益を半分だけ上のバンドで確定し、残り半分は20日線割れ・50日線割れ（引けで判定、翌日の寄り付き）まで持つ
  5. 枠が埋まっている日に新しい合図が出たら、含み損が一番大きい保有銘柄（−5%・−10%より悪いもの）を売って入れ替える
売買の値段は日足で再現する（指値は、その日の値幅に入れば約定したとみなす）。損切りは今と同じ（押し目は日中の安値で買値の15%下、ほかは引け値）。
片道0.1%。選び方の乱数50通りの中央値。設計期間 2015〜2021年 / 確認期間 2022年〜。
"""
import argparse
import datetime as dt
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_combo2 as cb
import backtest_swing as bs
from backtest_lib import COSTS, DEFAULT_CACHE, pct
from backtest_regime import srt

COST = COSTS[2]
SLOTS = 4
SEEDS = range(50)
STOP = 0.15


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/注文の出し方と枠の使い方.md")
    a = ap.parse_args()
    ctx = cb.setup(a.cache)
    data, ind, days, parts = (ctx[k] for k in ("data", "ind", "days", "parts"))
    rule_of, base = {}, []
    for key, lst in (("B", parts[("B", 0.15)]), ("M", parts[("M", 0.15)]), ("C", parts[("C", 0.15, 10)]), ("V", parts[("V", 0.15)])):
        for t in lst:
            rule_of[id(t)] = key
        base += lst
    base = srt(base)
    pos = {}

    def idx(sym, d):
        if sym not in pos:
            pos[sym] = {x: k for k, x in enumerate(data[sym]["date"])}
        return pos[sym][d]

    def path_of(sym, i0, i1, px, exit_px, frac=None):
        """買った日 i0 の寄り付き px から、i1 に exit_px で売るまでの、枠の価値の推移（最初を1、コスト込み）"""
        s = data[sym]
        sh = (1 - COST) / px
        pv = {s["date"][j]: sh * s["c"][j] for j in range(i0, i1)}
        pv[s["date"][i1]] = sh * exit_px * (1 - COST)
        return pv

    def make(t, px=None, out_i=None, exit_px=None, pv=None):
        s, sym = data[t["sym"]], t["sym"]
        i0, i1 = idx(sym, t["in"]), idx(sym, t["out"])
        px = px or t["px"]
        if pv is None:
            i1 = out_i if out_i is not None else i1
            exit_px = exit_px if exit_px is not None else t["px"] * (1 + t["ret"])
            pv = path_of(sym, i0, i1, px, exit_px)
        else:
            i1 = max(idx(sym, d) for d in pv)
        s_ = data[sym]
        atr = sum(max(s_["h"][k] - s_["l"][k], abs(s_["h"][k] - s_["c"][k - 1]), abs(s_["l"][k] - s_["c"][k - 1])) for k in range(i0 - 14, i0)) / 14 / s_["c"][i0 - 1]
        return {"sym": sym, "in": t["in"], "out": s["date"][i1], "path": pv, "rank": t["rank"], "rule": rule_of[id(t)], "atrp": atr,
                "ret": pv[s["date"][i1]] - 1}

    cur_tr = [make(t) for t in base]

    # 2. 指値で買う（押し目・急落の底）
    def limit_entry(x):
        out = []
        for t in base:
            if rule_of[id(t)] not in ("B", "C"):
                out.append(make(t))
                continue
            s = data[t["sym"]]
            i0 = idx(t["sym"], t["in"])
            lim = s["o"][i0] * (1 - x)
            if s["l"][i0] > lim:
                continue            # 届かなければ買わない
            if t["out"] == t["in"]:
                continue
            out.append(make(t, px=lim))
        return out

    # 3・4. 押し目の売り方
    def b3_exit(mode, k=1.0):
        out = []
        for t in base:
            if rule_of[id(t)] != "B":
                out.append(make(t))
                continue
            s, sym = data[t["sym"]], t["sym"]
            o, h, l, c = s["o"], s["h"], s["l"], s["c"]
            i0 = idx(sym, t["in"])
            px = t["px"]
            stop = px * (1 - STOP)
            n = len(c)
            sh, cash, pv, half_done, pend = (1 - COST) / px, 0.0, {}, False, None
            rest_ma = {"half20": "bb_mid", "half50": "ma50"}.get(mode)
            j = i0
            while j < n:
                d = s["date"][j]
                if pend == "all":
                    cash += sh * o[j] * (1 - COST)
                    sh = 0.0
                    pv[d] = cash
                    break
                pend = None
                if l[j] <= stop and sh > 0:
                    cash += sh * min(o[j] if j > i0 else px, stop) * (1 - COST)
                    sh = 0.0
                    pv[d] = cash
                    break
                if mode == "limit" and j > i0:
                    lv = s["bb_up"][j - 1]
                    lv = lv * k if lv is not None else None
                    if lv is not None and h[j] >= lv:
                        cash += sh * max(o[j], lv) * (1 - COST)
                        sh = 0.0
                        pv[d] = cash
                        break
                pv[d] = cash + sh * c[j]
                if j + 1 >= n or j - i0 >= (250 if half_done else bs.MAX_HOLD):
                    if j + 1 < n:
                        pend = "all"
                        j += 1
                        continue
                    break
                if not half_done:
                    if s["pctb"][j] is not None and s["pctb"][j] >= 1.0:
                        if rest_ma:
                            half_done = True
                            pend = "half"
                        else:
                            pend = "all"
                else:
                    m = s[rest_ma][j]
                    if m is not None and c[j] < m:
                        pend = "all"
                if pend == "half":
                    j += 1
                    if j >= n:
                        break
                    cash += sh / 2 * o[j] * (1 - COST)
                    sh /= 2
                    stop = max(stop, px)        # 半分を売った後は、残りの損切りを買値に引き上げる
                    pend = None
                    continue
                j += 1
            if not pv:
                continue
            out.append(make(t, pv=pv))
        return out

    di = {d: k for k, d in enumerate(days)}
    is_hi = max(d for d in days if d <= cb.IS_END)
    oos_lo = min(d for d in days if d >= cb.OOS_START)

    SEED0 = [5000]

    def port(trs, seed, lo, hi, order="random", swap=None):
        dd = [d for d in days if lo <= d <= hi]
        by_in = {}
        for t in trs:
            if lo <= t["in"] and t["out"] <= hi:
                by_in.setdefault(t["in"], []).append(t)
        rnd = random.Random(seed)
        key = {"random": lambda t: rnd.random(), "rs": lambda t: (t["rank"] if t["rule"] == "V" else 0, rnd.random()),
               "atr": lambda t: (-t["atrp"], rnd.random())}[order]
        cash, held, curve, peak, mdd = 1.0, [], [], 1.0, 0.0
        for d in dd:
            still = []
            for h in held:
                v = h["t"]["path"].get(d)
                if v is not None:
                    h["prev"], h["v"] = h["v"], v
                if h["t"]["out"] == d:
                    cash += h["size"] * h["v"]
                else:
                    still.append(h)
            held = still
            eq = cash + sum(h["size"] * h["v"] for h in held)
            for t in sorted(by_in.get(d, []), key=key):
                if any(h["t"]["sym"] == t["sym"] for h in held):
                    continue
                if len(held) >= SLOTS:
                    if swap is None:
                        break
                    worst = min(held, key=lambda h: h["prev"] / h["base"])
                    if worst["prev"] / worst["base"] - 1 > -swap:
                        break
                    cash += worst["size"] * worst["prev"] * (1 - COST)   # 前日の引けの値段で売ったとみなす（近似）
                    held.remove(worst)
                if sum(1 for h in held if ind.get(h["t"]["sym"]) == ind.get(t["sym"])) >= 2:
                    continue
                size = min(eq / SLOTS, cash)
                if size <= 0:
                    break
                cash -= size
                v0 = t["path"].get(d, 1.0)
                h = {"t": t, "size": size, "v": v0, "prev": v0, "base": v0}
                if t["out"] == d:
                    cash += size * v0
                    continue
                held.append(h)
            eq = cash + sum(h["size"] * h["v"] for h in held)
            curve.append(eq)
            peak = max(peak, eq)
            mdd = max(mdd, 1 - eq / peak)
        yrs = (dt.date.fromisoformat(dd[-1]) - dt.date.fromisoformat(dd[0])).days / 365.25
        return curve[-1] ** (1 / yrs) - 1, mdd

    def evaluate(trs, order="random", swap=None):
        seeds = SEEDS if order == "random" else range(10)
        a_ = [port(trs, SEED0[0] + k, days[0], days[-1], order, swap) for k in seeds]
        i_ = [port(trs, SEED0[0] + k, days[0], is_hi, order, swap)[0] for k in seeds]
        o_ = [port(trs, SEED0[0] + k, oos_lo, days[-1], order, swap)[0] for k in seeds]
        return {"all": cb.med([x[0] for x in a_]), "mdd": cb.med([x[1] for x in a_]), "is": cb.med(i_), "oos": cb.med(o_)}

    def avg_b(trs):
        b = [t["ret"] for t in trs if t["rule"] == "B"]
        return sum(b) / len(b), len(b)

    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: 注文の出し方と枠の使い方\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_execution.py\n---\n")
    w("# 注文の出し方と枠の使い方を工夫するバックテスト\n")
    w(__doc__.split("\n", 5)[5].strip() + "\n")
    w("| 番号 | 形 | 年率 | 最大下落率 | 設計期間 | 確認期間 | 押し目の1回平均（件数） | 両方の期間で上回ったか |")
    w("|---|---|---|---|---|---|---|---|")
    cur = evaluate(cur_tr)
    ab, nb = avg_b(cur_tr)
    w(f"| ― | 今のルール（ランダム順） | {pct(cur['all'])} | {pct(cur['mdd'])} | {pct(cur['is'])} | {pct(cur['oos'])} | {pct(ab, 2)}（{nb}） | |")

    def row(no, lab, trs, **kw):
        e = evaluate(trs, **kw)
        ok = e["is"] > cur["is"] and e["oos"] > cur["oos"]
        ab, nb = avg_b(trs)
        w(f"| {no} | {lab} | {pct(e['all'])} | {pct(e['mdd'])} | {pct(e['is'])} | {pct(e['oos'])} | {pct(ab, 2)}（{nb}） | {'はい' if ok else ''} |")
        print(no, lab, file=sys.stderr)

    row(1, "選び方: RSの高い順（今のツール。新高値V2はRS、ほかは同じ順位でランダム）", cur_tr, order="rs")
    row(1, "選び方: 値動き（ATR÷株価）の大きい順", cur_tr, order="atr")
    for x in (0.01, 0.02, 0.03):
        row(2, f"押し目・急落の底を寄り付きの{int(x * 100)}%下の指値で買う", limit_entry(x))
    row(3, "押し目の売り: 前日の上のバンドの値段に指値", b3_exit("limit"))
    row(4, "押し目: 上のバンドで半分売り、残りは20日線割れまで持つ（残りの損切りは買値）", b3_exit("half20"))
    row(4, "押し目: 上のバンドで半分売り、残りは50日線割れまで持つ（残りの損切りは買値）", b3_exit("half50"))
    for sw in (0.05, 0.10):
        row(5, f"枠が埋まっていたら、含み損が{int(sw * 100)}%より悪い保有銘柄と入れ替える", cur_tr, swap=sw)
    w("\n## 3の確認: 指値の位置を変える・乱数を変える\n")
    w("| 乱数 | 形 | 年率 | 最大下落率 | 設計期間 | 確認期間 | 押し目の1回平均（件数） | 両方の期間で上回ったか |")
    w("|---|---|---|---|---|---|---|---|")
    for sd in (5000, 7000):
        SEED0[0] = sd
        c0 = evaluate(cur_tr)
        ab, nb = avg_b(cur_tr)
        w(f"| {sd} | 今のルール | {pct(c0['all'])} | {pct(c0['mdd'])} | {pct(c0['is'])} | {pct(c0['oos'])} | {pct(ab, 2)}（{nb}） | |")
        for k in ((0.97, 0.98, 0.99, 1.0, 1.01, 1.02) if sd == 5000 else (0.98, 1.0, 1.02)):
            trs = b3_exit("limit", k)
            e = evaluate(trs)
            ok = e["is"] > c0["is"] and e["oos"] > c0["oos"]
            ab, nb = avg_b(trs)
            w(f"| {sd} | 押し目の売り: 前日の上のバンド×{k}に指値 | {pct(e['all'])} | {pct(e['mdd'])} | {pct(e['is'])} | {pct(e['oos'])} | {pct(ab, 2)}（{nb}） | {'はい' if ok else ''} |")
            print("確認", sd, k, file=sys.stderr)
    w("\n## 注意\n")
    w("- 指値の約定は日足の値幅で判定した近似（実際には同じ値段で約定しないこともある）。入れ替えの売値は前日の引けで近似。")
    w("- 押し目の売り方（3・4）は、元のルールの売り（引けで上のバンド以上→翌日の寄り付き）を、日足で作り直して比べている。")
    w("- 「RSの高い順」と「値動きの大きい順」は選び方の乱数の影響が小さいため10通り、ほかは50通りの中央値。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
