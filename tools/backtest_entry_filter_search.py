#!/usr/bin/env python3
"""今の買いのルールに、王道のシグナル（日足と週足）を「この条件もそろっているときだけ買う」として重ね、一番良い組み合わせを探すバックテスト

使い方:
  tools/backtest_entry_filter_search.py run [--out FILE]

今の採用ルール（4つのルール、4銘柄・1銘柄25%、損切り15%、急落の底RSI(2)≦10、同じ業種2銘柄まで）の買いの合図が出た日（引け）に、
次の条件のどれか（または2つ）がそろっているときだけ買う。そろわない合図は見送る（枠は他の合図に回る）。
  日足の状態: 終値が20日線・50日線・200日線より上、5日線＞25日線、MACD＞シグナル、MACD＞0、一目（終値が雲の上、転換線＞基準線、
    遅行スパン＝終値が26日前より上）、+DI＞−DI、ADX≧25、RSI(14)が50以上、RSI(14)が40以下、SARが上向き、ボリンジャーのバンド幅が5日前より縮む、
    出来高が50日平均の1.5倍以上、出来高が50日平均の0.7倍以下
  日足のローソク足（直近3日に出た）: 強気の包み足、たくり線、明けの明星、切り込み線、赤三兵、三空叩き込み
  週足（直前に終わった週まで）: 終値が10週線より上、10週線が上向き、30週線が上向き（ワインスタインのステージ2）、週足のMACD＞シグナル、週足のRSI(14)が50以上
探し方: 順張り（ミネルヴィニ・新高値V2）と逆張り（ボリンジャーIII・急落の底）で別々に。
  1. 1つの条件を重ねた形を、設計期間（2015〜2021年）の年率（4銘柄の枠、ランダム順10通りの中央値）で並べ、上位8つを選ぶ
  2. 上位8つの2つずつの組み合わせも設計期間の年率で並べる
  3. 設計期間の上位5つを、確認期間（2022年〜）で確かめる。最後に順張り・逆張りの1位を合わせて確かめる
"""
import argparse
import datetime as dt
import itertools
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_combo2 as cb
import backtest_exit_signals as xs
import backtest_signal_search as ss
from backtest_lib import COSTS, DEFAULT_CACHE, pct, portfolio, sma
from backtest_market_signal import ema
from backtest_rebuy import prep2
from backtest_regime import srt

COST = COSTS[2]
SLOTS = 4
SEEDS = range(10)


def prep_weekly(s):
    """週の最後の取引日ごとの週足の値を、その週の最後の日以降の日に割り当てる（まだ終わっていない週は使わない）"""
    d, c, n = s["date"], s["c"], len(s["c"])
    ends = [k for k in range(n) if k + 1 == n or dt.date.fromisoformat(d[k + 1]).isocalendar()[1] != dt.date.fromisoformat(d[k]).isocalendar()[1]]
    wc = [c[k] for k in ends]
    m10, m30 = sma(wc, 10), sma(wc, 30)
    me = [a - b for a, b in zip(ema(wc, 12), ema(wc, 26))]
    ms = ema(me, 9)
    up = [0.0] + [max(0.0, wc[i] - wc[i - 1]) for i in range(1, len(wc))]
    dn = [0.0] + [max(0.0, wc[i - 1] - wc[i]) for i in range(1, len(wc))]
    au, ad = xs.wilder(up, 14), xs.wilder(dn, 14)
    wr = [None if au[i] is None else (100.0 if ad[i] == 0 else 100 - 100 / (1 + au[i] / ad[i])) for i in range(len(wc))]
    keys = ("w_above10", "w_up10", "w_up30", "w_macd", "w_rsi50")
    for k in keys:
        s[k] = [None] * n
    wi = -1
    for i in range(n):
        while wi + 1 < len(ends) and ends[wi + 1] <= i:
            wi += 1
        if wi < 1:
            continue
        s["w_above10"][i] = m10[wi] is not None and wc[wi] > m10[wi]
        s["w_up10"][i] = m10[wi] is not None and m10[wi - 1] is not None and m10[wi] > m10[wi - 1]
        s["w_up30"][i] = m30[wi] is not None and wi >= 4 and m30[wi - 4] is not None and m30[wi] > m30[wi - 4]
        s["w_macd"][i] = wi >= 35 and me[wi] > ms[wi]
        s["w_rsi50"][i] = wr[wi] is not None and wr[wi] >= 50


def recent(f, k=3):
    return lambda s, i: any(ss_safe(f, s, j) for j in range(i - k + 1, i + 1))


def ss_safe(f, s, j):
    try:
        return bool(f(s, j))
    except (TypeError, ValueError, IndexError):
        return False


def adx_of(s):
    pdi, mdi = s["pdi"], s["mdi"]
    dx = [None if p is None or m is None or p + m == 0 else 100 * abs(p - m) / (p + m) for p, m in zip(pdi, mdi)]
    return xs.wilder(dx, 14)


def bw_shrink(s, i):
    up, dn, mid = s["bb_up"], s["bb_dn"], s["bb_mid"]
    if i < 5 or None in (up[i], dn[i], mid[i], up[i - 5], dn[i - 5], mid[i - 5]):
        return False
    return (up[i] - dn[i]) / mid[i] < (up[i - 5] - dn[i - 5]) / mid[i - 5]


FILTERS = [
    ("終値が20日線より上", lambda s, i: s["bb_mid"][i] is not None and s["c"][i] > s["bb_mid"][i]),
    ("終値が50日線より上", lambda s, i: s["ma50"][i] is not None and s["c"][i] > s["ma50"][i]),
    ("終値が200日線より上", lambda s, i: s["ma200"][i] is not None and s["c"][i] > s["ma200"][i]),
    ("5日線＞25日線", lambda s, i: s["ma25"][i] is not None and s["ma5"][i] > s["ma25"][i]),
    ("MACD＞シグナル", lambda s, i: s["macd"][i] > s["macd_sig"][i]),
    ("MACD＞0", lambda s, i: s["macd"][i] > 0),
    ("一目: 終値が雲の上", lambda s, i: s["cloud_hi"][i] is not None and s["c"][i] > s["cloud_hi"][i]),
    ("一目: 転換線＞基準線", lambda s, i: s["ten"][i] is not None and s["kij"][i] is not None and s["ten"][i] > s["kij"][i]),
    ("一目: 遅行スパンが上（終値＞26日前）", lambda s, i: i >= 26 and s["c"][i] > s["c"][i - 26]),
    ("+DI＞−DI", lambda s, i: s["pdi"][i] is not None and s["pdi"][i] > s["mdi"][i]),
    ("ADX≧25", lambda s, i: s["adx"][i] is not None and s["adx"][i] >= 25),
    ("RSI(14)≧50", lambda s, i: s["rsi14"][i] is not None and s["rsi14"][i] >= 50),
    ("RSI(14)≦40", lambda s, i: s["rsi14"][i] is not None and s["rsi14"][i] <= 40),
    ("SARが上向き", lambda s, i: not s["sar_dn"][i]),
    ("ボリンジャーのバンド幅が縮む", bw_shrink),
    ("出来高1.5倍以上", lambda s, i: bool(s["vol50"][i - 1]) and s["v"][i] >= 1.5 * s["vol50"][i - 1]),
    ("出来高0.7倍以下（売りが細る）", lambda s, i: bool(s["vol50"][i - 1]) and s["v"][i] <= 0.7 * s["vol50"][i - 1]),
    ("強気の包み足（3日以内）", recent(ss.bull_engulf)),
    ("たくり線（3日以内）", recent(ss.hammer)),
    ("明けの明星（3日以内）", recent(ss.morning_star)),
    ("切り込み線（3日以内）", recent(ss.piercing)),
    ("赤三兵（3日以内）", recent(ss.three_white)),
    ("三空叩き込み（3日以内）", recent(ss.three_gaps_down)),
    ("週足: 終値が10週線より上", lambda s, i: s["w_above10"][i]),
    ("週足: 10週線が上向き", lambda s, i: s["w_up10"][i]),
    ("週足: 30週線が上向き（ステージ2）", lambda s, i: s["w_up30"][i]),
    ("週足: MACD＞シグナル", lambda s, i: s["w_macd"][i]),
    ("週足: RSI(14)≧50", lambda s, i: s["w_rsi50"][i]),
]


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/買いの合図に条件を重ねる組み合わせ探し.md")
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

    for sym in {t["sym"] for t in base}:
        s = data[sym]
        xs.prep(s)
        prep2(s)
        s["adx"] = adx_of(s)
        h, l, n = s["h"], s["l"], len(s["c"])
        def mid(p, i):
            return (max(h[i - p + 1:i + 1]) + min(l[i - p + 1:i + 1])) / 2 if i >= p - 1 else None
        ten, kij = s["ten"], s["kij"]
        sa = [None if ten[i] is None or kij[i] is None else (ten[i] + kij[i]) / 2 for i in range(n)]
        sb = [mid(52, i) for i in range(n)]
        s["cloud_hi"] = [None] * 26 + [None if sa[i] is None or sb[i] is None else max(sa[i], sb[i]) for i in range(n - 26)]
        prep_weekly(s)
    # 合図の日ごとに、全部の条件を前もって判定
    ok = {}
    for t in base:
        s = data[t["sym"]]
        i = idx(t["sym"], t["in"]) - 1
        ok[id(t)] = {nm for nm, f in FILTERS if ss_safe(f, s, i)}
    print("条件の判定ができた", file=sys.stderr)

    di = {d: k for k, d in enumerate(days)}
    is_hi = max(d for d in days if d <= cb.IS_END)
    oos_lo = min(d for d in days if d >= cb.OOS_START)
    span = lambda lo, hi: (dt.date.fromisoformat(hi) - dt.date.fromisoformat(lo)).days / 365.25

    def seg(c, lo, hi):
        return c[di[hi]] / (c[di[lo] - 1] if di[lo] > 0 else 1.0)

    def ev_is(tr):
        return cb.med([portfolio([t for t in tr if t["out"] <= is_hi], COST, SLOTS, [d for d in days if d <= is_hi], data, weight=1 / SLOTS,
                                 seed=k, group_of=ind, group_cap=2)["cagr"] for k in SEEDS])

    def ev_full(tr):
        rs = []
        for k in SEEDS:
            p = portfolio(tr, COST, SLOTS, days, data, weight=1 / SLOTS, seed=k, group_of=ind, group_cap=2)
            c = p["curve"]
            rs.append({"all": p["cagr"], "mdd": p["mdd"], "is": seg(c, days[0], is_hi) ** (1 / span(days[0], is_hi)) - 1,
                       "oos": seg(c, oos_lo, days[-1]) ** (1 / span(oos_lo, days[-1])) - 1})
        m = lambda key: cb.med([x[key] for x in rs])
        return {"all": m("all"), "mdd": m("mdd"), "is": m("is"), "oos": m("oos")}

    def apply(rules, names):
        return [t for t in base if rule_of[id(t)] not in rules or all(nm in ok[id(t)] for nm in names)]

    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: 買いの合図に条件を重ねる組み合わせ探し\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_entry_filter_search.py\n---\n")
    w("# 今の買いのルールに、王道のシグナル（日足・週足）を条件として重ねる組み合わせ探し\n")
    w(__doc__.split("\n", 5)[5].strip() + "\n")
    cur_is = ev_is(base)
    cur = ev_full(base)
    w(f"今のルール: 年率 {pct(cur['all'])}、最大下落率 {pct(cur['mdd'])}、設計期間 {pct(cur['is'])}（探すときの物差しでは {pct(cur_is)}）、確認期間 {pct(cur['oos'])}\n")
    groups = (("順張り（ミネルヴィニ・新高値V2）", ("M", "V")), ("逆張り（ボリンジャーIII・急落の底）", ("B", "C")))
    best = {}
    for gl, rules in groups:
        n0 = sum(1 for t in base if rule_of[id(t)] in rules and t["in"] <= cb.IS_END)
        singles = []
        for nm, _ in FILTERS:
            tr = apply(rules, (nm,))
            kept = sum(1 for t in tr if rule_of[id(t)] in rules and t["in"] <= cb.IS_END) / max(1, n0)
            singles.append(((nm,), ev_is(tr), kept))
        singles.sort(key=lambda x: -x[1])
        top = [x[0][0] for x in singles[:8]]
        pairs = []
        for x, y in itertools.combinations(top, 2):
            tr = apply(rules, (x, y))
            kept = sum(1 for t in tr if rule_of[id(t)] in rules and t["in"] <= cb.IS_END) / max(1, n0)
            pairs.append(((x, y), ev_is(tr), kept))
        allc = sorted(singles + pairs, key=lambda x: -x[1])
        w(f"\n## {gl}\n")
        w(f"設計期間の買いの合図 {n0}件。\n")
        w("### 1. 条件を1つ重ねた形（設計期間の年率の上位10）\n")
        w("| 順位 | 条件 | 設計期間の年率 | 残った合図の割合 |")
        w("|---|---|---|---|")
        for k, (nm, v, kept) in enumerate(singles[:10], 1):
            w(f"| {k} | {'＋'.join(nm)} | {pct(v)} | {pct(kept, 0)} |")
        w(f"\n（今のルールは {pct(cur_is)}。下位5つ: " + "、".join(f"{'＋'.join(nm)} {pct(v)}" for nm, v, _ in singles[-5:]) + "）\n")
        w("### 2. 1つ・2つの組み合わせを合わせた上位5を、確認期間で確かめる\n")
        w("| 順位 | 条件 | 残った合図の割合 | 年率 | 最大下落率 | 設計期間 | 確認期間 | 両方の期間で上回ったか |")
        w("|---|---|---|---|---|---|---|---|")
        res = []
        for k, (nm, v, kept) in enumerate(allc[:5], 1):
            e = ev_full(apply(rules, nm))
            okk = e["is"] > cur["is"] and e["oos"] > cur["oos"]
            res.append((nm, e, okk))
            w(f"| {k} | {'＋'.join(nm)} | {pct(kept, 0)} | {pct(e['all'])} | {pct(e['mdd'])} | {pct(e['is'])} | {pct(e['oos'])} | {'はい' if okk else ''} |")
            print(gl, nm, file=sys.stderr)
        best[gl] = (rules, allc[0][0])
    (r1, n1), (r2, n2) = best.values()
    e = ev_full([t for t in base if (rule_of[id(t)] not in r1 or all(x in ok[id(t)] for x in n1))
                 and (rule_of[id(t)] not in r2 or all(x in ok[id(t)] for x in n2))])
    okk = e["is"] > cur["is"] and e["oos"] > cur["oos"]
    w("\n## 3. 順張り・逆張りの1位を合わせる\n")
    w("| 形 | 年率 | 最大下落率 | 設計期間 | 確認期間 | 両方の期間で上回ったか |")
    w("|---|---|---|---|---|---|")
    w(f"| 今のルール | {pct(cur['all'])} | {pct(cur['mdd'])} | {pct(cur['is'])} | {pct(cur['oos'])} | |")
    w(f"| 順張り: {'＋'.join(n1)}／逆張り: {'＋'.join(n2)} | {pct(e['all'])} | {pct(e['mdd'])} | {pct(e['is'])} | {pct(e['oos'])} | {'はい' if okk else ''} |")
    w("\n## 注意\n")
    w("- 条件の数値はClaudeが一般的な定義から置いたもの。何十通りから一番良いものを選んでいるため、設計期間の成績は実際より良く出る。確認期間で判断する。")
    w("- 週足は、合図の日より前に終わった週（その日が週の最後の日ならその週）までの値を使う。")
    w("- 選び方の乱数だけで年率は2〜3ポイント動く。それより小さい差は偶然の範囲。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
