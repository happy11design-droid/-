#!/usr/bin/env python3
"""売りの合図を組み合わせる（いくつか重なったときだけ売る）バックテスト

使い方:
  tools/backtest_exit_combo.py run [--out FILE]

組み合わせは試す前に決めた4つ（当てはめすぎを避けるため、たくさんの組み合わせから選ばない）:
  1. 反転のローソク足（かぶせ線・弱気の包み足・宵の明星・流れ星のどれか）＋ 出来高が50日平均の1.5倍以上 ＋ RSI(14)が前日か当日に70以上
  2. ダブルトップのネックライン割れ ＋ 出来高が50日平均の1.5倍以上
  3. MACDの弱気ダイバージェンスが出た後、10日以内に終値が10日線を下に抜ける
  4. 反転の合図（下の18種類）が直近5日に2つ以上（4'は3つ以上）重なる
     ダブルトップ、三尊天井、アイランド、下放れ二本黒、首吊り線、流れ星、三羽烏、宵の明星、弱気の包み足、かぶせ線、
     RSIの70割れ、RSIの弱気ダイバージェンス、MACDの弱気ダイバージェンス、ストキャスのデッドクロス、SARの反転、5日線と25日線のデッドクロス、
     一目の転換線と基準線のデッドクロス、DMIの交差
各合図の定義は `backtest_exit_signals.py` と同じ。引けで判定し、翌日の寄り付きで売る。今のルールの売りの条件はそのまま残す。
当てる対象: 順張り（ミネルヴィニ・新高値V2）だけ／全部。設計期間 2015〜2021年 / 確認期間 2022年〜。
"""
import argparse
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_combo2 as cb
import backtest_exit_signals as xs
from backtest_lib import COSTS, DEFAULT_CACHE, pct, portfolio, sma
from backtest_regime import srt

COST = COSTS[2]
SLOTS = 4
SEEDS = range(10)
REV = [xs.double_top, xs.head_shoulders, xs.island_top, xs.gap_two_black, xs.hanging_man, xs.shooting_star, xs.three_crows,
       xs.evening_star, xs.bear_engulf, xs.dark_cloud, xs.rsi_down70, xs.rsi_div, xs.macd_div, xs.stoch_down, xs.sar_flip,
       xs.dead_5_25, xs.ichimoku_tk, xs.dmi_cross]


def safe(f, s, j):
    try:
        return bool(f(s, j))
    except (TypeError, ValueError, IndexError):
        return False


def vol_up(s, j, k=1.5):
    v50 = s["vol50"][j - 1]
    return bool(v50) and s["v"][j] >= k * v50


def c1(s, j):
    rev = any(safe(f, s, j) for f in (xs.dark_cloud, xs.bear_engulf, xs.evening_star, xs.shooting_star))
    r = s["rsi14"]
    return rev and vol_up(s, j) and max(x or 0 for x in (r[j], r[j - 1])) >= 70


def c2(s, j):
    return safe(xs.double_top, s, j) and vol_up(s, j)


def c3(s, j):
    m10 = s["ma10x"]
    if m10[j] is None or m10[j - 1] is None or not (s["c"][j] < m10[j] and s["c"][j - 1] >= m10[j - 1]):
        return False
    return any(safe(xs.macd_div, s, k) for k in range(max(1, j - 10), j + 1))


def make_count(need):
    def f(s, j):
        memo = s.setdefault("_rev", {})
        n = 0
        for k in range(max(2, j - 4), j + 1):
            if k not in memo:
                memo[k] = sum(1 for g in REV if safe(g, s, k))
            n += memo[k]
        return n >= need
    return f


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/売りの合図の組み合わせ.md")
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
        data[sym]["ma10x"] = sma(data[sym]["c"], 10)
    pos = {}

    def idx(sym, d):
        if sym not in pos:
            pos[sym] = {x: k for k, x in enumerate(data[sym]["date"])}
        return pos[sym][d]

    def apply(f, rules):
        out, diffs = [], []
        for t in base:
            if rule_of[id(t)] not in rules:
                out.append(t)
                continue
            s, sym = data[t["sym"]], t["sym"]
            i0, i1 = idx(sym, t["in"]), idx(sym, t["out"])
            new = t
            for j in range(max(i0, 2), i1 - 1):
                if safe(f, s, j):
                    new = {**t, "out": s["date"][j + 1], "ret": s["o"][j + 1] / t["px"] - 1}
                    diffs.append(new["ret"] - t["ret"])
                    break
            out.append(new)
        return srt(out), diffs

    di = {d: k for k, d in enumerate(days)}
    is_hi = max(d for d in days if d <= cb.IS_END)
    oos_lo = min(d for d in days if d >= cb.OOS_START)
    span = lambda lo, hi: (dt.date.fromisoformat(hi) - dt.date.fromisoformat(lo)).days / 365.25

    def seg(c, lo, hi):
        return c[di[hi]] / (c[di[lo] - 1] if di[lo] > 0 else 1.0)

    def evaluate(tr):
        rs = []
        for k in SEEDS:
            p = portfolio(tr, COST, SLOTS, days, data, weight=1 / SLOTS, seed=k, group_of=ind, group_cap=2)
            c = p["curve"]
            rs.append({"all": p["cagr"], "mdd": p["mdd"], "is": seg(c, days[0], is_hi) ** (1 / span(days[0], is_hi)) - 1,
                       "oos": seg(c, oos_lo, days[-1]) ** (1 / span(oos_lo, days[-1])) - 1})
        m = lambda key: cb.med([x[key] for x in rs])
        return {"all": m("all"), "mdd": m("mdd"), "is": m("is"), "oos": m("oos")}

    cur = evaluate(base)
    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: 売りの合図の組み合わせ\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_exit_combo.py\n---\n")
    w("# 売りの合図を組み合わせる（いくつか重なったときだけ売る）バックテスト\n")
    w(__doc__.split("\n", 5)[5].strip() + "\n")
    w("年率・最大下落率は同じ日の候補の選び方をランダムにした10通りの中央値。片道0.1%。「差」は早めに売った売買1回ごとの損益の差の平均"
      "（プラスなら早めに売った方が良かった）。「戻った割合」は、売らずに持った方が良かった割合。\n")
    w(f"今のルール: 年率 {pct(cur['all'])}、最大下落率 {pct(cur['mdd'])}、設計期間 {pct(cur['is'])}、確認期間 {pct(cur['oos'])}\n")
    w("| 組み合わせ | 対象 | 年率 | 最大下落率 | 設計期間 | 確認期間 | 早めに売った件数 | 差（1回平均） | 戻った割合 | 両方の期間で上回ったか |")
    w("|---|---|---|---|---|---|---|---|---|---|")
    tests = [("1. 反転のローソク足＋出来高1.5倍＋RSI70以上", c1), ("2. ダブルトップ＋出来高1.5倍", c2),
             ("3. MACDの弱気ダイバージェンスの後に10日線割れ", c3), ("4. 反転の合図が5日に2つ以上", make_count(2)),
             ("4'. 反転の合図が5日に3つ以上", make_count(3))]
    n_ok = 0
    for lab, f in tests:
        for gl, rules in (("順張りだけ", ("M", "V")), ("全部", ("B", "C", "M", "V"))):
            tr, diffs = apply(f, rules)
            e = evaluate(tr)
            ok = e["is"] > cur["is"] and e["oos"] > cur["oos"]
            n_ok += ok
            avg = sum(diffs) / len(diffs) if diffs else 0
            back = sum(1 for x in diffs if x < 0) / len(diffs) if diffs else 0
            w(f"| {lab} | {gl} | {pct(e['all'])} | {pct(e['mdd'])} | {pct(e['is'])} | {pct(e['oos'])} | {len(diffs)} | {pct(avg, 2)} | {pct(back, 0)} | {'はい' if ok else ''} |")
            print(lab, gl, file=sys.stderr)
    w(f"\n- 両方の期間で上回った組み合わせ: {n_ok}通り / {len(tests) * 2}通り")
    w("\n## 注意\n")
    w("- 組み合わせの数値（出来高1.5倍、RSI70、10日以内、5日に2つ・3つ）はClaudeが置いたもの。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
