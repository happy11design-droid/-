#!/usr/bin/env python3
"""MACD・ボリンジャーバンド・VIXで市場全体の「危ない時期」を判定し、買いを止める／売る効果を見るバックテスト

使い方:
  tools/backtest_market_signal.py run [--out FILE]

判定（すべて引けで判定。指数は S&P500 と NASDAQ100、VIX はそのまま）:
  MACD: 日足 MACD(12,26) がシグナル(9)より下／日足 MACD が0より下／週足相当 MACD(60,130,45 日) がシグナルより下
  ボリンジャーバンド（指数、20日・2σ）: 終値が真ん中の線（20日線）より下／真ん中より下かつバンド幅が5日前より広がっている（下への拡大）／
      終値が下のバンドより下（%b<0）／週足相当（100日・2σ）の真ん中より下
  VIX: 終値が 20・25・30 以上
それぞれの「危ない」状態で次を試す（今の採用ルール: 4つのルール、4銘柄・1銘柄25%、損切り15%、急落の底RSI(2)≦10、同じ業種2銘柄まで）:
  ① 新しく買わない（全部のルール）
  ①' 順張りのルール（ミネルヴィニ・新高値V2）だけ新しく買わない（押し目・急落の底は買う）
  ③a 危ない状態に変わった日に、持っている銘柄を全部、翌日の寄り付きで売る
  ③c 危ない状態に変わった日に、順張りのルールの銘柄だけ売る
設計期間 2015〜2021年 / 確認期間 2022年〜。
"""
import argparse
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_combo2 as cb
from backtest_lib import COSTS, DEFAULT_CACHE, load_prices, pct, portfolio, sma
from backtest_regime import srt

COST = COSTS[2]
SLOTS = 4
SEEDS = range(10)
IS_END, OOS_START = cb.IS_END, cb.OOS_START


def ema(x, n):
    out, e, k = [], None, 2 / (n + 1)
    for v in x:
        e = v if e is None else e + k * (v - e)
        out.append(e)
    return out


def macd_states(p, f, s, g):
    c = p["c"]
    m = [a - b for a, b in zip(ema(c, f), ema(c, s))]
    sig = ema(m, g)
    warm = s + g
    below_sig = {d: m[i] < sig[i] for i, d in enumerate(p["date"]) if i >= warm}
    below0 = {d: m[i] < 0 for i, d in enumerate(p["date"]) if i >= warm}
    return below_sig, below0


def bb_states(p, n, k=2.0):
    c = p["c"]
    mid = sma(c, n)
    out_mid, out_expand, out_low = {}, {}, {}
    width = [None] * len(c)
    for i in range(len(c)):
        if mid[i] is None:
            continue
        w = c[i - n + 1:i + 1]
        sd = (sum((x - mid[i]) ** 2 for x in w) / n) ** 0.5
        width[i] = 2 * k * sd / mid[i]
        d = p["date"][i]
        out_mid[d] = c[i] < mid[i]
        out_low[d] = c[i] < mid[i] - k * sd
        if i >= 5 and width[i - 5] is not None:
            out_expand[d] = c[i] < mid[i] and width[i] > width[i - 5]
    return out_mid, out_expand, out_low


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/MACD・ボリンジャー・VIXで市場全体を判定.md")
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

    def sig_day(t):
        return data[t["sym"]]["date"][idx(t["sym"], t["in"]) - 1]

    def no_buy(tr, bad, trend_only=False):
        return srt([t for t in tr if not (bad.get(sig_day(t)) and (not trend_only or rule_of[id(t)] in ("M", "V")))])

    def sell_on(tr, bad, trend_only=False):
        out = []
        for t in tr:
            if trend_only and rule_of[id(t)] not in ("M", "V"):
                out.append(t)
                continue
            s, sym = data[t["sym"]], t["sym"]
            i0, i1 = idx(sym, t["in"]), idx(sym, t["out"])
            new = t
            for j in range(i0, i1 - 1):
                if bad.get(s["date"][j]) and not bad.get(s["date"][j - 1]):
                    new = {**t, "out": s["date"][j + 1], "ret": s["o"][j + 1] / t["px"] - 1, "why": "市場の判定"}
                    break
            out.append(new)
        return srt(out)

    di = {d: k for k, d in enumerate(days)}
    is_hi = max(d for d in days if d <= IS_END)
    oos_lo = min(d for d in days if d >= OOS_START)
    span = lambda lo, hi: (dt.date.fromisoformat(hi) - dt.date.fromisoformat(lo)).days / 365.25
    years = sorted({d[:4] for d in days})

    def seg(c, lo, hi):
        return c[di[hi]] / (c[di[lo] - 1] if di[lo] > 0 else 1.0)

    def evaluate(tr):
        rs = []
        for k in SEEDS:
            p = portfolio(tr, COST, SLOTS, days, data, weight=1 / SLOTS, seed=k, group_of=ind, group_cap=2)
            c = p["curve"]
            yr = {y: seg(c, min(d for d in days if d[:4] == y), max(d for d in days if d[:4] == y)) - 1 for y in years}
            rs.append({"all": p["cagr"], "mdd": p["mdd"], "is": seg(c, days[0], is_hi) ** (1 / span(days[0], is_hi)) - 1,
                       "oos": seg(c, oos_lo, days[-1]) ** (1 / span(oos_lo, days[-1])) - 1, "yr": yr})
        m = lambda key: cb.med([x[key] for x in rs])
        return {"all": m("all"), "mdd": m("mdd"), "is": m("is"), "oos": m("oos"),
                "yr": {y: cb.med([x["yr"][y] for x in rs]) for y in years}}

    spx, ndx, vix = load_prices(a.cache, "^GSPC"), load_prices(a.cache, "^NDX"), load_prices(a.cache, "^VIX")
    states = []
    for name, p in (("S&P500", spx), ("NASDAQ100", ndx)):
        s1, s2 = macd_states(p, 12, 26, 9)
        s3, _ = macd_states(p, 60, 130, 45)
        b1, b2, b3 = bb_states(p, 20)
        b4, _, _ = bb_states(p, 100)
        states += [("MACD", f"{name} 日足MACDがシグナルより下", s1), ("MACD", f"{name} 日足MACDが0より下", s2),
                   ("MACD", f"{name} 週足相当MACDがシグナルより下", s3),
                   ("ボリンジャー", f"{name} 20日線（真ん中）より下", b1), ("ボリンジャー", f"{name} 真ん中より下かつバンドが広がる", b2),
                   ("ボリンジャー", f"{name} 下のバンドより下（%b<0）", b3), ("ボリンジャー", f"{name} 週足相当（100日）の真ん中より下", b4)]
    for th in (20, 25, 30):
        states.append(("VIX", f"VIX {th}以上", {d: v >= th for d, v in zip(vix["date"], vix["c"])}))

    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: MACD・ボリンジャー・VIXで市場全体を判定\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_market_signal.py\n---\n")
    w("# MACD・ボリンジャーバンド・VIXで市場全体の「危ない時期」を判定するバックテスト\n")
    w(__doc__.split("\n", 5)[5].strip() + "\n")
    w("年率・最大下落率は同じ日の候補の選び方をランダムにした10通りの中央値。片道0.1%。後知恵なしの監視銘柄（S&P500）。"
      "「危ない日の割合」は2015年以降の取引日のうち、その状態だった日の割合。「切り替わり」は危ない状態に変わった回数（1年あたり）。\n")
    cur = evaluate(base)
    w(f"今のルール: 年率 {pct(cur['all'])}、設計期間 {pct(cur['is'])}、確認期間 {pct(cur['oos'])}、最大下落率 {pct(cur['mdd'])}、"
      f"2018年 {pct(cur['yr']['2018'], 0)}、2022年 {pct(cur['yr']['2022'], 0)}\n")
    rows = []
    acts = (("①", lambda b: no_buy(base, b)), ("①'", lambda b: no_buy(base, b, True)),
            ("③a", lambda b: sell_on(base, b)), ("③c", lambda b: sell_on(base, b, True)))
    for grp in ("MACD", "ボリンジャー", "VIX"):
        w(f"\n## {grp}\n")
        w("| 判定 | 危ない日の割合 / 切り替わり | 形 | 年率 | 最大下落率 | 設計期間 | 確認期間 | 2018 | 2022 | 両方の期間で上回ったか |")
        w("|---|---|---|---|---|---|---|---|---|---|")
        for g, lab, b in states:
            if g != grp:
                continue
            share = sum(bool(b.get(d)) for d in days) / len(days)
            turns = sum(1 for k in range(1, len(days)) if b.get(days[k]) and not b.get(days[k - 1])) / (len(days) / 252)
            for act, f in acts:
                e = evaluate(f(b))
                ok = e["is"] > cur["is"] and e["oos"] > cur["oos"]
                rows.append((lab, act, e, ok))
                w(f"| {lab} | {pct(share, 0)} / {turns:.1f}回/年 | {act} | {pct(e['all'])} | {pct(e['mdd'])} | {pct(e['is'])} | {pct(e['oos'])} | "
                  f"{pct(e['yr']['2018'], 0)} | {pct(e['yr']['2022'], 0)} | {'はい' if ok else ''} |")
                print(lab, act, file=sys.stderr)

    ok = [x for x in rows if x[3]]
    w("\n## まとめ\n")
    w(f"- 設計期間・確認期間の両方で今のルール（設計 {pct(cur['is'])}、確認 {pct(cur['oos'])}）を上回った形: **{len(ok)}通り / {len(rows)}通り**")
    for lab, act, e, _ in sorted(ok, key=lambda x: -(x[2]["is"] + x[2]["oos"])):
        w(f"  - {lab} {act}: 年率 {pct(e['all'])}、設計 {pct(e['is'])}、確認 {pct(e['oos'])}、最大下落率 {pct(e['mdd'])}")
    w("\n## 注意\n")
    w("- 数値（MACDの期間、バンドの期間と幅、VIXの水準）は一般的な値で、Claudeが置いたもの。多くの形を試しているので、1つだけ良い形は偶然のことがある。"
      "S&P500とNASDAQ100の両方、近い判定どうしで同じ傾向かを見る。")
    w("- 業種は今のYahooの分類を過去にも使っている。NASDAQ100の構成銘柄は含めていない（判定にだけNASDAQ100指数を使う）。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
