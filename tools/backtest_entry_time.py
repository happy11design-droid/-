#!/usr/bin/env python3
"""買う時刻（寄り付き／1時間後／2時間後／引け）で成績がどう変わるかのバックテスト

使い方:
  tools/backtest_entry_time.py run [--out FILE]

今の採用ルール（4つのルール、4銘柄・1銘柄25%、損切り15%、急落の底RSI(2)≦10、同じ業種2銘柄まで）の合図の翌日に買う時刻だけを変える。
売る日と売値は今のルールのまま（売りの判定は引けで行い、翌日の寄り付きで売る）。
  ① 日足（2015年〜）: 翌日の寄り付きで買う（今）／翌日の引けで買う
  ② 1時間足（直近2年、Yahooの60分足）: 寄り付き／1時間後（10:30 ET）／2時間後（11:30 ET）／引け
買う時刻を遅らせた場合は、その日のうちに損切りの値段まで下がっていても損切りはせず、買った値段から計算し直さない（近似）。
買った日のうちに売った売買（日中の損切り）は、遅く買う形では買わなかったものとして外す。
"""
import argparse
import concurrent.futures as cf
import datetime as dt
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_combo2 as cb
from backtest_lib import COSTS, DEFAULT_CACHE, pct, portfolio, stats
from backtest_regime import srt
from theme_scan import curl

COST = COSTS[2]
SLOTS = 4
SEEDS = range(10)
NAMES = {"B": "ボリンジャーIII", "M": "ミネルヴィニ", "C": "急落の底", "V": "新高値V2"}


def fetch_hourly(sym):
    """{日付: [(時刻HH:MM, 始値, 終値), ...]}（ニューヨーク時間）。取れなければ {}"""
    try:
        res = json.loads(curl(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym.replace('.', '-')}?interval=60m&range=730d"))["chart"]["result"][0]
        q, off = res["indicators"]["quote"][0], res["meta"].get("gmtoffset", 0)
        out = {}
        for i, t in enumerate(res["timestamp"]):
            o, c = q["open"][i], q["close"][i]
            if None in (o, c):
                continue
            x = dt.datetime.utcfromtimestamp(t + off)
            out.setdefault(x.strftime("%Y-%m-%d"), []).append((x.strftime("%H:%M"), o, c))
        return out
    except Exception:
        return {}


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/買う時刻の比較.md")
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

    def shift(tr, ratio_of):
        """ratio_of(t) = 遅らせて買った値段 ÷ 寄り付きの値段（None なら外す）"""
        out = []
        for t in tr:
            if t["out"] == t["in"]:
                continue
            rr = ratio_of(t)
            if rr is None:
                continue
            nt = {**t, "px": t["px"] * rr, "ret": (1 + t["ret"]) / rr - 1}
            rule_of[id(nt)] = rule_of[id(t)]
            out.append(nt)
        return srt(out)

    def evaluate(tr, lo, hi):
        dd = [d for d in days if lo <= d <= hi]
        rs = [portfolio([t for t in tr if lo <= t["in"] and t["out"] <= hi], COST, SLOTS, dd, data, weight=1 / SLOTS, seed=k,
                        group_of=ind, group_cap=2) for k in SEEDS]
        return cb.med([p["cagr"] for p in rs]), cb.med([p["mdd"] for p in rs])

    def by_rule(tr):
        cells = []
        for k in "BCVM":
            st = stats([t for t in tr if rule_of[id(t)] == k], COST)
            cells.append(f"{pct(st['mean'], 2)}（{pct(st['win'], 0)}）" if st else "-")
        st = stats(tr, COST)
        return cells, st

    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: 買う時刻の比較\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_entry_time.py\n---\n")
    w("# 買う時刻（寄り付き／1時間後／2時間後／引け）の比較\n")
    w(__doc__.split("\n", 5)[5].strip() + "\n")
    w("表の「1回平均（勝率）」は全部の合図の1回ごとの損益（片道0.1%込み）。年率・最大下落率は4銘柄の枠で、同じ日の候補の選び方をランダムにした10通りの中央値。\n")

    # ① 日足
    w("\n## ① 日足（2015年〜）\n")
    w("| 買う時刻 | 件数 | 全体の1回平均（勝率） | " + " | ".join(NAMES[k] for k in "BCVM") + " | 年率 | 最大下落率 | 設計期間 | 確認期間 |")
    w("|---|---|---|---|---|---|---|---|---|---|---|")
    opn = shift(base, lambda t: 1.0)
    cls = shift(base, lambda t: data[t["sym"]]["c"][idx(t["sym"], t["in"])] / data[t["sym"]]["o"][idx(t["sym"], t["in"])])
    for lab, tr in (("翌日の寄り付き（今）", opn), ("翌日の引け", cls)):
        cells, st = by_rule(tr)
        a_, m_ = evaluate(tr, days[0], days[-1])
        i_, _ = evaluate(tr, days[0], cb.IS_END)
        o_, _ = evaluate(tr, cb.OOS_START, days[-1])
        w(f"| {lab} | {st['n']} | {pct(st['mean'], 2)}（{pct(st['win'], 0)}） | " + " | ".join(cells) + f" | {pct(a_)} | {pct(m_)} | {pct(i_)} | {pct(o_)} |")
        print(lab, file=sys.stderr)
    w("\n（買った日のうちに売った売買は、どちらの形からも外している。そのため「今」の数字は他の表と少し違う）")

    # ② 1時間足
    lo2 = (dt.date.fromisoformat(days[-1]) - dt.timedelta(days=725)).isoformat()
    recent = [t for t in base if t["in"] >= lo2 and t["out"] != t["in"]]
    syms = sorted({t["sym"] for t in recent})
    print(f"1時間足を取得: {len(syms)}銘柄", file=sys.stderr)
    with cf.ThreadPoolExecutor(8) as ex:
        hourly = dict(zip(syms, ex.map(fetch_hourly, syms)))

    def ratio(t, k):
        bars = sorted(hourly.get(t["sym"], {}).get(t["in"], []))
        if len(bars) < 3 or bars[0][0] != "09:30":
            return None
        o = bars[0][1]
        p = {"open": o, "1h": bars[0][2], "2h": bars[1][2], "close": bars[-1][2]}[k]
        return p / o

    usable = [t for t in recent if ratio(t, "open") is not None]
    w(f"\n## ② 1時間足（直近2年、{lo2}〜）\n")
    w(f"この期間の合図 {len(recent)}件のうち、1時間足が取れた {len(usable)}件で比べる（件数が少ないので参考値）。\n")
    w("| 買う時刻 | 件数 | 全体の1回平均（勝率） | " + " | ".join(NAMES[k] for k in "BCVM") + " | 年率（4銘柄の枠） | 最大下落率 |")
    w("|---|---|---|---|---|---|---|---|---|")
    for lab, k in (("寄り付き（9:30 ET、今）", "open"), ("1時間後（10:30 ET）", "1h"), ("2時間後（11:30 ET）", "2h"), ("引け（16:00 ET）", "close")):
        tr = shift(usable, lambda t, k=k: ratio(t, k))
        cells, st = by_rule(tr)
        a_, m_ = evaluate(tr, lo2, days[-1])
        w(f"| {lab} | {st['n']} | {pct(st['mean'], 2)}（{pct(st['win'], 0)}） | " + " | ".join(cells) + f" | {pct(a_)} | {pct(m_)} |")
        print(lab, file=sys.stderr)
    w("\n- 日本時間では、寄り付きが22:30（冬時間23:30）、1時間後が23:30（0:30）、2時間後が0:30（1:30）、引けが5:00（6:00）。")
    w("\n## 注意\n")
    w("- 1時間足は直近2年しか取れず、件数が少ないため、差の多くは偶然の範囲。①の日足（2015年〜）の結果と同じ向きかを見る。")
    w("- 1時間足は配当・分割の調整をしていないが、同じ日の中の値段の比だけを使うので影響しない。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
