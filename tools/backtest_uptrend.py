#!/usr/bin/env python3
"""上昇中の押し目で買うルールと、同じ銘柄への買い増し（ピラミッディング）のバックテスト

使い方:
  tools/backtest_uptrend.py run [--out FILE]

① 上昇中の押し目（数値はClaudeが置いたもの）:
   ミネルヴィニのトレンドテンプレート8条件、RS≧90（または80）の銘柄が、安値で20日線（または50日線）の+1%以内まで下がり、
   終値が線より上で引けた日の翌日の寄り付きで買う。
   手じまい: 引けで50日線割れ（上昇に乗り続ける）／上のバンド（早めに利益確定）。50日線の押し目は50日線の−3%割れ。損切りは買値の15%下
② 同じ銘柄への買い増し: 持っている銘柄に別のルールの合図が出たら、2枠目で買う（1銘柄に2枠＝資金の50%まで）
今の採用ルール: 4つのルール、4銘柄・1銘柄25%、損切り15%、急落の底RSI(2)≦10、同じ業種2銘柄まで。
後知恵なしの監視銘柄（S&P500）。設計期間 2015〜2021年 / 確認期間 2022年〜。
"""
import argparse
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_combo2 as cb
import backtest_trend as bt
from backtest_lib import COSTS, DEFAULT_CACHE, gen_trades, pct, portfolio, stats
from backtest_regime import srt

COST = COSTS[2]
SLOTS = 4
SEEDS = range(10)
STOP = 0.15
IS_END, OOS_START = cb.IS_END, cb.OOS_START


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/上昇中の押し目と買い増し.md")
    a = ap.parse_args()
    ctx = cb.setup(a.cache)
    data, members, ind, days, parts, end, ok_rot = (ctx[k] for k in ("data", "members", "ind", "days", "parts", "end", "ok_rot"))
    base = srt(parts[("B", 0.15)] + parts[("M", 0.15)] + parts[("C", 0.15, 10)] + parts[("V", 0.15)])

    def E_pull(ma, rs_min, tol=0.01):
        def f(i, s):
            m = s[ma][i]
            if m is None or (s["rs"][i] or 0) < rs_min or not (s["l"][i] <= m * (1 + tol) and s["c"][i] > m):
                return None
            if not bt.trend_template(s, i):
                return None
            return -(s["rs"][i] or 0)
        return f

    below50 = lambda j, s, k, px: s["ma50"][j] is not None and s["c"][j] < s["ma50"][j]
    below50x = lambda j, s, k, px: s["ma50"][j] is not None and s["c"][j] < s["ma50"][j] * 0.97
    band = lambda j, s, k, px: s["pctb"][j] is not None and s["pctb"][j] >= 1.0
    G = lambda e, x: gen_trades(data, members, e, x, cb.START, end, ok=ok_rot, fill="open", max_hold=500, stop_pct=STOP)

    di = {d: k for k, d in enumerate(days)}
    is_hi = max(d for d in days if d <= IS_END)
    oos_lo = min(d for d in days if d >= OOS_START)
    span = lambda lo, hi: (dt.date.fromisoformat(hi) - dt.date.fromisoformat(lo)).days / 365.25
    years = sorted({d[:4] for d in days})

    def seg(c, lo, hi):
        return c[di[hi]] / (c[di[lo] - 1] if di[lo] > 0 else 1.0)

    def evaluate(tr, per_sym=1):
        rs = []
        for k in SEEDS:
            p = portfolio(tr, COST, SLOTS, days, data, weight=1 / SLOTS, seed=k, group_of=ind, group_cap=2, per_sym=per_sym)
            c = p["curve"]
            yr = {y: seg(c, min(d for d in days if d[:4] == y), max(d for d in days if d[:4] == y)) - 1 for y in years}
            rs.append({"all": p["cagr"], "mdd": p["mdd"], "is": seg(c, days[0], is_hi) ** (1 / span(days[0], is_hi)) - 1,
                       "oos": seg(c, oos_lo, days[-1]) ** (1 / span(oos_lo, days[-1])) - 1, "yr": yr})
        m = lambda key: cb.med([x[key] for x in rs])
        return {"all": m("all"), "mdd": m("mdd"), "is": m("is"), "oos": m("oos"),
                "yr": {y: cb.med([x["yr"][y] for x in rs]) for y in years}}

    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: 上昇中の押し目と買い増し\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_uptrend.py\n---\n")
    w("# 上昇中の押し目で買うルールと、同じ銘柄への買い増しのバックテスト\n")
    w(__doc__.split("\n", 5)[5].strip() + "\n")
    w("年率・最大下落率は同じ日の候補の選び方をランダムにした10通りの中央値。片道0.1%。1回平均は全部の合図の1回ごとの損益（コスト込み）。\n")
    head = "| 形 | 年率 | 最大下落率 | 設計期間 | 確認期間 | 2018 | 2022 | 2024 | 2025 | 両方の期間で上回ったか |"
    sep = "|---|---|---|---|---|---|---|---|---|---|"
    cur = evaluate(base)

    def line(lab, e, cmp=True):
        ok = cmp and e["is"] > cur["is"] and e["oos"] > cur["oos"]
        w(f"| {lab} | {pct(e['all'])} | {pct(e['mdd'])} | {pct(e['is'])} | {pct(e['oos'])} | "
          + " | ".join(pct(e["yr"][y], 0) for y in ("2018", "2022", "2024", "2025")) + f" | {'はい' if ok else ''} |")
        print(lab, file=sys.stderr)
        return ok

    pulls = {
        "20日線の押し目・RS≧90・50日線割れで手じまい": (E_pull("bb_mid", 90), below50),
        "20日線の押し目・RS≧80・50日線割れで手じまい": (E_pull("bb_mid", 80), below50),
        "20日線の押し目・RS≧90・上のバンドで手じまい": (E_pull("bb_mid", 90), band),
        "50日線の押し目・RS≧90・50日線の−3%割れで手じまい": (E_pull("ma50", 90), below50x),
    }
    tr_p = {k: G(e, x) for k, (e, x) in pulls.items()}

    w("\n## 1. 上昇中の押し目（単独・1回ごと）\n")
    w("| 形 | 件数/年 | 勝率 | 1回平均 | PF | 前半 / 後半 1回平均 |")
    w("|---|---|---|---|---|---|")
    yrs = len(days) / 252
    for k, t in tr_p.items():
        st = stats(t, COST)
        h1 = stats([x for x in t if x["in"] <= IS_END], COST)
        h2 = stats([x for x in t if x["in"] >= OOS_START], COST)
        w(f"| {k} | {st['n'] / yrs:.0f} | {pct(st['win'])} | {pct(st['mean'], 2)} | {st['pf']:.2f} | {pct(h1['mean'], 2)} / {pct(h2['mean'], 2)} |")

    w("\n## 2. 今の採用ルールとの組み合わせ（4銘柄の枠を共有）\n")
    w(head)
    w(sep)
    line("今のルール", cur, False)
    oks = []
    for k, t in tr_p.items():
        if line(f"今のルール＋{k}", evaluate(srt(base + t))):
            oks.append(k)
    if line("今のルール・同じ銘柄に別のルールの合図が出たら2枠目で買い増す", evaluate(base, per_sym=2)):
        oks.append("買い増し")
    k0 = "20日線の押し目・RS≧90・50日線割れで手じまい"
    if line(f"今のルール＋{k0}＋買い増し", evaluate(srt(base + tr_p[k0]), per_sym=2)):
        oks.append("押し目＋買い増し")

    w("\n## まとめ\n")
    w(f"- 今のルール: 設計 {pct(cur['is'])}、確認 {pct(cur['oos'])}、最大下落率 {pct(cur['mdd'])}")
    w(f"- 設計期間・確認期間の両方で今のルールを上回った形: {len(oks)}通り" + (f"（{'、'.join(oks)}）" if oks else ""))
    w("\n## 注意\n")
    w("- 押し目の数値（20日線・50日線、+1%以内、RS≧90・80、50日線の−3%）はClaudeが置いたもの。SNDKの4〜7月のチャートを見て決めたものではない。")
    w("- 買い増しでは、同じ銘柄の2枠も「同じ業種は2銘柄まで」に数える（1銘柄で2枠を使うと、同じ業種の別の銘柄は買えない）。")
    w("- 業種は今のYahooの分類を過去にも使っている。NASDAQ100は含めていない。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
