#!/usr/bin/env python3
"""売りの合図で売り、買いの合図で買い直す（同じ銘柄の売り買いを繰り返す）バックテスト

使い方:
  tools/backtest_rebuy.py run [--out FILE]

今の採用ルール（4つのルール、4銘柄・1銘柄25%、損切り15%、急落の底RSI(2)≦10、同じ業種2銘柄まで）で買った銘柄について、
ルールが本来売る日までの間、次を繰り返す（引けで判定し、翌日の寄り付きで売買。1回の売り・買いごとに0.1%）。
その銘柄の枠（資金の25%）は、ルールが本来売る日まで確保しておく（売っている間は現金）。
  売りの合図（これまで「売ったら終わり」で試して成績が下がったもの。定義は backtest_exit_signals.py などと同じ）:
    組み合わせ（反転のローソク足＋出来高1.5倍＋RSI70以上）、下放れ二本黒、三羽烏、パラボリックSARの反転、陰線が2日続く、
    MACDのデッドクロス、出来高2倍の大陰線、5日線と25日線のデッドクロス、20日線割れ、かぶせ線
  買い直しの合図:
    A 売った値段より上で引けたら（一番単純な形）
    B 上昇の合図（10日線を上に戻す・MACDのゴールデンクロス・SARの上向きの反転・強気の包み足のどれか）、
      または底の合図（直近3日にRSI(2)≦10があり、前日の高値を上に抜けて引ける／前日がたくり線で、前日より上で引ける）
  比べる形: 今のルール（持ち続ける）／売るだけ（買い直さない）／売ってAで買い直す／売ってBで買い直す
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
from backtest_lib import COSTS, DEFAULT_CACHE, pct, sma
from backtest_regime import srt

COST = COSTS[2]
SLOTS = 4
SEEDS = range(10)


def prep2(s):
    c, n = s["c"], len(s["c"])
    s["ma10x"] = sma(c, 10)
    up = [0.0] + [max(0.0, c[i] - c[i - 1]) for i in range(1, n)]
    dn = [0.0] + [max(0.0, c[i - 1] - c[i]) for i in range(1, n)]
    au, ad = xs.wilder(up, 2), xs.wilder(dn, 2)
    s["rsi2x"] = [None if au[i] is None else (100.0 if ad[i] == 0 else 100 - 100 / (1 + au[i] / ad[i])) for i in range(n)]


def two_black(s, j):
    o, c = s["o"], s["c"]
    return c[j] < o[j] and c[j - 1] < o[j - 1]


def macd_dc(s, j):
    return xs.cross_below(s["macd"], s["macd_sig"], j)


def big_bear(s, j):
    o, h, l, c, v = s["o"], s["h"], s["l"], s["c"], s["v"]
    a, v50 = s["atr14"][j - 1], s["vol50"][j - 1]
    return a is not None and v50 and h[j] > l[j] and o[j] - c[j] >= 1.5 * a and (c[j] - l[j]) / (h[j] - l[j]) <= 0.25 and v[j] >= 2 * v50


SELLS = [("組み合わせ（反転のローソク足＋出来高＋RSI70）", xc.c1), ("下放れ二本黒", xs.gap_two_black), ("三羽烏", xs.three_crows),
         ("パラボリックSARの反転", xs.sar_flip), ("陰線が2日続く", two_black), ("MACDのデッドクロス", macd_dc),
         ("出来高2倍の大陰線", big_bear), ("5日線と25日線のデッドクロス", xs.dead_5_25), ("20日線割れ", xs.below20), ("かぶせ線", xs.dark_cloud)]


def rebuy_up(s, j):
    m, c, o = s["ma10x"], s["c"], s["o"]
    if m[j] is not None and m[j - 1] is not None and c[j] > m[j] and c[j - 1] <= m[j - 1]:
        return True
    if xs.cross_below(s["macd_sig"], s["macd"], j):          # MACDがシグナルを上に抜ける
        return True
    if s["sar_dn"][j - 1] and not s["sar_dn"][j]:
        return True
    return c[j - 1] < o[j - 1] and c[j] > o[j] and o[j] <= c[j - 1] and c[j] >= o[j - 1]   # 強気の包み足


def rebuy_bottom(s, j):
    o, h, l, c, r2 = s["o"], s["h"], s["l"], s["c"], s["rsi2x"]
    if any(x is not None and x <= 10 for x in r2[max(0, j - 3):j]) and c[j] > h[j - 1]:
        return True
    k = j - 1
    b = abs(c[k] - o[k])
    lower, upper = min(o[k], c[k]) - l[k], h[k] - max(o[k], c[k])
    return b > 0 and lower >= 2 * b and upper <= 0.3 * b and c[j] > c[k]


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/売って買い直す.md")
    a = ap.parse_args()
    ctx = cb.setup(a.cache)
    data, ind, days, parts = (ctx[k] for k in ("data", "ind", "days", "parts"))
    rule_of, base = {}, []
    for key, lst in (("B", parts[("B", 0.15)]), ("M", parts[("M", 0.15)]), ("C", parts[("C", 0.15, 10)]), ("V", parts[("V", 0.15)])):
        for t in lst:
            rule_of[id(t)] = key
        base += lst
    base = srt(base)
    for sym in {t["sym"] for t in base}:
        xs.prep(data[sym])
        prep2(data[sym])
    print("準備ができた", file=sys.stderr)
    pos = {}

    def idx(sym, d):
        if sym not in pos:
            pos[sym] = {x: k for k, x in enumerate(data[sym]["date"])}
        return pos[sym][d]

    def sim(t, sell, mode):
        """1つの売買の枠の価値の推移 {日付: 価値（最初を1）} と、往復の情報を返す。mode: hold / sell / A / B"""
        s, sym = data[t["sym"]], t["sym"]
        o, c = s["o"], s["c"]
        i0, i1 = idx(sym, t["in"]), idx(sym, t["out"])
        exit_px = t["px"] * (1 + t["ret"])
        cash, sh = 1.0, (1 - COST) / t["px"]
        cash = 0.0
        path, trips, gaps, pend, sold_px = {}, 0, [], None, None
        for j in range(i0, i1 + 1):
            d = s["date"][j]
            if j == i1:
                if sh > 0:
                    cash += sh * exit_px * (1 - COST)
                    sh = 0.0
                path[d] = cash
                break
            if pend == "sell" and j > i0:
                cash, sh, sold_px = sh * o[j] * (1 - COST), 0.0, o[j]
            elif pend == "buy":
                sh, cash = cash * (1 - COST) / o[j], 0.0
                trips += 1
                gaps.append(o[j] / sold_px - 1)
            pend = None
            path[d] = cash + sh * c[j]
            if mode == "hold" or j < max(i0, 2):
                continue
            try:
                if sh > 0:
                    if sell(s, j):
                        pend = "sell"
                elif mode in ("A", "B"):
                    if mode == "A" and c[j] > sold_px:
                        pend = "buy"
                    elif mode == "B" and (rebuy_up(s, j) or rebuy_bottom(s, j)):
                        pend = "buy"
            except (TypeError, ValueError, IndexError):
                pass
        return path, trips, gaps

    di = {d: k for k, d in enumerate(days)}
    years = sorted({d[:4] for d in days})

    def port(trs, seed, lo, hi):
        dd = [d for d in days if lo <= d <= hi]
        by_in = {}
        for t in trs:
            if lo <= t["in"] and t["out"] <= hi:
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
            for t in sorted(by_in.get(d, []), key=lambda t: rnd.random()):
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
        return curve[-1] ** (1 / yrs) - 1, mdd

    is_hi = max(d for d in days if d <= cb.IS_END)
    oos_lo = min(d for d in days if d >= cb.OOS_START)

    def evaluate(trs):
        a_ = [port(trs, k, days[0], days[-1]) for k in SEEDS]
        i_ = [port(trs, k, days[0], is_hi)[0] for k in SEEDS]
        o_ = [port(trs, k, oos_lo, days[-1])[0] for k in SEEDS]
        return {"all": cb.med([x[0] for x in a_]), "mdd": cb.med([x[1] for x in a_]), "is": cb.med(i_), "oos": cb.med(o_)}

    def build(sell, mode, rules):
        out, trips, gaps, rets = [], 0, [], []
        for t in base:
            m = mode if rule_of[id(t)] in rules else "hold"
            path, tr_, g = sim(t, sell, m)
            nt = {"sym": t["sym"], "in": t["in"], "out": t["out"], "path": path}
            out.append(nt)
            trips += tr_
            gaps += g
            rets.append(path[t["out"]] - 1)
        win = sum(1 for x in rets if x > 0) / len(rets)
        return out, trips, gaps, sum(rets) / len(rets), win

    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: 売って買い直す\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_rebuy.py\n---\n")
    w("# 売りの合図で売り、買いの合図で買い直すバックテスト（これまでの売りの合図の振り返り）\n")
    w(__doc__.split("\n", 5)[5].strip() + "\n")
    w("年率・最大下落率は同じ日の候補の選び方をランダムにした10通りの中央値。「1回平均・勝率」は、1つの枠（買ってからルールが売るまで）の損益。"
      "「買い直した回数」は全部の合図での合計、「買い直しの値段」は、売った値段に比べて買い直した値段が平均で何%高かったか（プラスなら高く買い直している）。\n")
    hold_tr, _, _, hold_avg, hold_win = build(None, "hold", ())
    cur = evaluate(hold_tr)
    w(f"今のルール（持ち続ける）: 年率 {pct(cur['all'])}、最大下落率 {pct(cur['mdd'])}、設計期間 {pct(cur['is'])}、確認期間 {pct(cur['oos'])}、"
      f"1回平均 {pct(hold_avg, 2)}、勝率 {pct(hold_win, 0)}\n")
    groups = (("全部", ("B", "C", "M", "V")), ("順張りだけ", ("M", "V")), ("逆張りだけ", ("B", "C")))
    wins = []
    for lab, sell in SELLS:
        w(f"\n## {lab}\n")
        w("| 対象 | 形 | 年率 | 最大下落率 | 設計期間 | 確認期間 | 1回平均 | 勝率 | 買い直した回数 | 買い直しの値段（売値比） | 両方の期間で上回ったか |")
        w("|---|---|---|---|---|---|---|---|---|---|---|")
        for gl, rules in groups:
            for mode, ml in (("sell", "売るだけ"), ("A", "売ってAで買い直す（売値より上で引けたら）"), ("B", "売ってBで買い直す（上昇・底の合図）")):
                trs, trips, gaps, avg, win = build(sell, mode, rules)
                e = evaluate(trs)
                ok = e["is"] > cur["is"] and e["oos"] > cur["oos"]
                if ok:
                    wins.append((lab, gl, ml, e))
                g = pct(sum(gaps) / len(gaps), 2) if gaps else "-"
                w(f"| {gl} | {ml} | {pct(e['all'])} | {pct(e['mdd'])} | {pct(e['is'])} | {pct(e['oos'])} | {pct(avg, 2)} | {pct(win, 0)} | {trips} | {g} | {'はい' if ok else ''} |")
                print(lab, gl, ml, file=sys.stderr)
    w("\n## まとめ\n")
    w(f"- 設計期間・確認期間の両方で今のルールを上回った形: **{len(wins)}通り / {len(SELLS) * 9}通り**")
    for lab, gl, ml, e in wins:
        w(f"  - {lab}（{gl}・{ml}）: 年率 {pct(e['all'])}、設計 {pct(e['is'])}、確認 {pct(e['oos'])}、最大下落率 {pct(e['mdd'])}")
    w("\n## 注意\n")
    w("- 売り・買い直しの合図の数値はClaudeが置いたもの。多くの形を試しているので、1つだけ良い形は偶然のことがある。")
    w("- 選び方の乱数だけで年率は2〜3ポイント動く（`売りの合図の組み合わせ.md`）。それより小さい差は偶然の範囲。")
    w("- 買い直した後の損切りは、元の買値の15%下のまま（ルールが本来売る日を変えない）。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
