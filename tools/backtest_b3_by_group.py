#!/usr/bin/env python3
"""押し目（ボリンジャーIII）の合図を、銘柄のグループ（半導体・ソフト/ITサービスなど）に分けて成績を比べる（2026-11-19 ユーザーの指示）

使い方:
  python3 tools/backtest_b3_by_group.py [--out FILE]

- 売買は今の押し目のルール（%b<0.05かつ21日II%>0で翌日の寄り付きで買う、上部バンドで売る、損切り15%）。
  `backtest_combo2.setup` の parts[("B", 0.15)] と同じ `backtest_swing.simulate(O_method3, X_upper_band)`。
  保有中の出来高2倍の大陰線で売るルールは入っていない（`ルールごとの成績.md` の押し目と同じ形）。
- 監視銘柄は2通り:
  (1) 後知恵なしの監視銘柄（`backtest_combo2` の毎週の一覧）。グループはYahooの業種で分ける。
  (2) 今の87銘柄（`新分析ツール/テーマ監視銘柄.md` のグループ。今から選んだ一覧なので後知恵を含む）。
- 1回ごとの成績（片道0.1%込み）と、そのグループの合図だけで4銘柄の枠を回した年率・最大下落率（同じ日の候補はランダムな順、乱数20通りの中央値）。
"""
import argparse
import collections
import datetime as dt
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_combo2 as cb
import backtest_swing as bs
import backtest_trend as bt
from backtest_lib import COSTS, DEFAULT_CACHE, pct, portfolio
from backtest_regime import srt

COST = COSTS[2]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

IND_GROUP = {
    "Semiconductors": "半導体",
    "Semiconductor Equipment & Materials": "半導体製造装置・材料",
    "Software—Application": "ソフト・ITサービス", "Software - Application": "ソフト・ITサービス",
    "Software—Infrastructure": "ソフト・ITサービス", "Software - Infrastructure": "ソフト・ITサービス",
    "Information Technology Services": "ソフト・ITサービス",
}


def watch87():
    g, cur = {}, None
    for line in open(os.path.join(ROOT, "新分析ツール/テーマ監視銘柄.md"), encoding="utf-8"):
        m = re.match(r"## (.+?)（\d+）", line)
        if m:
            cur = m.group(1)
            continue
        if line.startswith("## "):
            cur = None
        m = re.match(r"\| ([A-Z.\-]+) \|", line)
        if cur and m and m.group(1) != "ティッカー":
            g[m.group(1)] = cur
    return g


def stats(ts):
    if not ts:
        return None
    r = [t["ret"] - 2 * COST for t in ts]
    win = [x for x in r if x > 0]
    loss = [-x for x in r if x <= 0]
    stop = sum(1 for t in ts if t.get("why") == "損切り")
    return {"n": len(ts), "win": len(win) / len(r), "avg": sum(r) / len(r),
            "pf": sum(win) / sum(loss) if loss else 9.99, "stop": stop / len(ts)}


def cell(s):
    return f"{s['n']} | {pct(s['win'], 0)} | {pct(s['avg'], 2)} | {s['pf']:.2f} | {pct(s['stop'], 0)}" if s else "0 | | | | "


def port(ts, data, days, lo, hi):
    ts = [t for t in ts if lo <= t["in"] <= hi]
    dd = [d for d in days if lo <= d <= hi]
    if not ts:
        return None
    rs = [portfolio(ts, COST, 4, dd, data, seed=k) for k in range(20)]
    med = lambda xs: sorted(xs)[len(xs) // 2]
    return med([x["cagr"] for x in rs]), med([x["mdd"] for x in rs])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default=DEFAULT_CACHE)
    ap.add_argument("--out", default="新分析ツール/バックテスト結果/押し目のグループ別の成績.md")
    a = ap.parse_args()
    ctx = cb.setup(a.cache, with_parts=False)
    data, members, ind, days = ctx["data"], ctx["members"], ctx["ind"], ctx["days"]
    end = days[-1]
    bs.STOP_MAX = 0.15   # 今の損切り15%（backtest_combo2.setup の B3(0.15) と同じ）
    # (1) 後知恵なしの監視銘柄
    base = srt(bs.simulate(data, members, bs.O_method3, bs.X_upper_band, cb.START, end, ok=ctx["ok_rot"]))
    g1 = lambda t: IND_GROUP.get(ind.get(t["sym"]) or "", "その他（電力・機器・ネット・通信など）")
    # (2) 今の87銘柄
    w87 = watch87()
    ok87 = lambda s, i, sp: bt.liquid(s, i, sp) and s["sym"] in w87
    b87 = srt(bs.simulate(data, members, bs.O_method3, bs.X_upper_band, cb.START, end, ok=ok87))
    g2 = lambda t: w87[t["sym"]]

    periods = [("2015〜2021年", cb.START, cb.IS_END), ("2022年〜", cb.OOS_START, end), ("2025年〜", "2025-01-01", end)]
    L = []
    w = L.append
    w(f"---\ntype: backtest\ntitle: 押し目のグループ別の成績\ncreated: {dt.date.today()}\nscript: tools/backtest_b3_by_group.py\n---\n")
    w("# 押し目（ボリンジャーIII）の合図をグループに分けた成績\n")
    w("2026-11-19、テーマ監視の候補がアクセンチュア・IBM・イントゥイット（どれもAIソフト・ITサービスのグループ）だったのを受けて、"
      "ユーザーの指示で「押し目の合図は、半導体とソフト・ITサービスのどちらで成績が良いか」を確かめた。\n")
    w(__doc__.split("\n", 4)[4].strip() + "\n")
    w(f"データの最終日: {end}。\n")
    for title, trades, gf in (("1. 後知恵なしの監視銘柄（グループはYahooの業種）", base, g1),
                              ("2. 今の87銘柄（グループは監視銘柄の一覧。後知恵を含む）", b87, g2)):
        w(f"\n## {title}\n")
        groups = collections.defaultdict(list)
        for t in trades:
            groups[gf(t)].append(t)
        names = sorted(groups, key=lambda k: -len(groups[k]))
        w("### 1回ごとの成績（件数｜勝率｜1回平均｜PF｜損切りの割合）\n")
        w("| グループ | " + " | ".join(f"{p} 件数 | 勝率 | 1回平均 | PF | 損切り" for p, _, _ in periods) + " |")
        w("|---|" + "---|" * (5 * len(periods)))
        for g in ["全体"] + names:
            ts = trades if g == "全体" else groups[g]
            w(f"| {g} | " + " | ".join(cell(stats([t for t in ts if lo <= t['in'] <= hi])) for _, lo, hi in periods) + " |")
        w("\n### そのグループの合図だけで4銘柄の枠を回した場合（年率／含み損込みの最大下落率、乱数20通りの中央値）\n")
        w("| グループ | " + " | ".join(p for p, _, _ in periods) + " |")
        w("|---|" + "---|" * len(periods))
        for g in ["全体"] + names:
            ts = trades if g == "全体" else groups[g]
            row = []
            for _, lo, hi in periods:
                r = port(ts, data, days, lo, hi)
                row.append(f"{pct(r[0])}／{pct(r[1], 0)}" if r else "")
            w(f"| {g} | " + " | ".join(row) + " |")
            print(title[:2], g, file=sys.stderr)
        w("\n### 年ごとの1回平均（件数）\n")
        yrs = sorted({t["in"][:4] for t in trades})
        w("| グループ | " + " | ".join(yrs) + " |")
        w("|---|" + "---|" * len(yrs))
        for g in ["全体"] + names:
            ts = trades if g == "全体" else groups[g]
            row = []
            for y in yrs:
                s = stats([t for t in ts if t["in"][:4] == y])
                row.append(f"{pct(s['avg'], 1)}（{s['n']}）" if s else "")
            w(f"| {g} | " + " | ".join(row) + " |")
    w("\n- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("書き出し", a.out, file=sys.stderr)


if __name__ == "__main__":
    main()
