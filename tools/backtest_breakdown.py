#!/usr/bin/env python3
"""今の採用ルールの成績を、ルール・セクター・テーマ・相場の局面ごとに分けて見る

使い方:
  tools/backtest_breakdown.py run [--out FILE]

今の採用ルール: ボリンジャーIII＋ミネルヴィニ＋急落の底（RSI(2)≦10）＋新高値V2（RS上位10・2年の最高値以上）、
同時に4銘柄・1銘柄に資金の25%、損切り15%、同じ業種は2銘柄まで。後知恵なしの監視銘柄（S&P500）、2015年〜。
  1. ルールごと
  2. セクター（Yahooの大きな分類）ごと
  3. テーマ（監視リストの7グループに近い業種のまとまり）ごと。テーマの外の銘柄はまとめて「テーマの外」
  4. 相場の局面（買った日のS&P500・NASDAQ100の30週線）ごと。資金の増え方も局面の日ごとに分ける
  5. ルール × 相場の局面
「全部の合図」はルールの条件が成立したすべての売買（1回ごとの成績）。「実際に買えたもの」は4つの枠に入った売買
（同じ日の候補の選び方をランダムにした10通りを合わせたもの）。
"""
import argparse
import collections
import datetime as dt
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_caps as bcp
import backtest_combo2 as cb
from backtest_lib import COSTS, DEFAULT_CACHE, load_prices, pct, portfolio, sma

COST = COSTS[2]
SLOTS = 4
SEEDS = range(10)
IS_END, OOS_START = cb.IS_END, cb.OOS_START
NAMES = {"B": "ボリンジャーIII（押し目）", "M": "ミネルヴィニ（ベースの上抜け）", "C": "急落の底", "V": "新高値V2"}
THEME_GROUP = {  # 監視リストの7グループに近いまとまり（業種で近似）
    "半導体": "半導体", "製造装置": "半導体製造装置", "ハード・端末": "AIサーバー・ストレージ・端末",
    "通信機器・部品・計測": "光・通信・電子部品", "ソフト・ITサービス": "ソフト・ITサービス", "ネット": "ネット・クラウド",
}


def regime_of(prices):
    """{日付: 上昇／横ばい／下落}。30週線（150日線）より上かつ4週前より上向き＝上昇、下かつ下向き＝下落、それ以外＝横ばい"""
    c = prices["c"]
    m = sma(c, 150)
    out = {}
    for i, d in enumerate(prices["date"]):
        if m[i] is None or i < 20 or m[i - 20] is None:
            continue
        up = m[i] > m[i - 20]
        out[d] = "上昇" if c[i] > m[i] and up else ("下落" if c[i] < m[i] and not up else "横ばい")
    return out


def st(ts):
    if not ts:
        return None
    r = [t["ret"] - 2 * COST for t in ts]
    win = [x for x in r if x > 0]
    loss = [-x for x in r if x <= 0]
    return {"n": len(r), "win": len(win) / len(r), "avg": sum(r) / len(r),
            "pf": sum(win) / sum(loss) if loss else float("inf")}


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/ルール・テーマ・相場の局面ごとの成績.md")
    a = ap.parse_args()
    ctx = cb.setup(a.cache)
    data, ind, days, parts = (ctx[k] for k in ("data", "ind", "days", "parts"))
    import json
    u = json.load(open(os.path.join(a.cache, "universe.json")))
    ex = os.path.join(a.cache, "industry_extra.json")
    if os.path.exists(ex):
        u.update(json.load(open(ex)))
    sec = {s: (u.get(s) or {}).get("sector") or "不明" for s in data}
    theme = {s: THEME_GROUP.get(bcp.THEME.get(ind.get(s)), "テーマの外") for s in data}
    spx = regime_of(load_prices(a.cache, "^GSPC"))
    ndx = regime_of(load_prices(a.cache, "^NDX"))

    rule_of = {}
    tr = []
    for key, lst in (("B", parts[("B", 0.15)]), ("M", parts[("M", 0.15)]), ("C", parts[("C", 0.15, 10)]), ("V", parts[("V", 0.15)])):
        for t in lst:
            rule_of[id(t)] = key
        tr += lst
    tr.sort(key=lambda t: (t["in"], t["sym"]))
    years = len(days) / 252

    # 実際に買えたもの（10通り）と、毎日の資金
    taken, curves = [], []
    for k in SEEDS:
        log = []
        p = portfolio(tr, COST, SLOTS, days, data, weight=1 / SLOTS, seed=k, group_of=ind, group_cap=2, log=log)
        taken += log
        curves.append(p["curve"])

    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: ルール・テーマ・相場の局面ごとの成績\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_breakdown.py\n---\n")
    w("# 今の採用ルールの成績を、ルール・セクター・テーマ・相場の局面ごとに分けて見る\n")
    w(__doc__.split("\n", 5)[5].strip() + "\n")
    w("1回の成績は片道0.1%のコスト込み。PF＝利益の合計÷損失の合計。「前半 / 後半」は設計期間（2015〜2021年）/ 確認期間（2022年〜）の1回平均。\n")

    def table(title, key, order=None, note=""):
        w(f"\n## {title}\n")
        if note:
            w(note + "\n")
        w("| 分け方 | 全部の合図 件数/年 | 勝率 | 1回平均 | PF | 前半 / 後半 1回平均 | 実際に買えたもの 件数/年 | 勝率 | 1回平均 | PF |")
        w("|---|---|---|---|---|---|---|---|---|---|")
        g_all, g_tk = collections.defaultdict(list), collections.defaultdict(list)
        for t in tr:
            g_all[key(t)].append(t)
        for t in taken:
            g_tk[key(t)].append(t)
        ks = order or sorted(g_all, key=lambda k: -len(g_all[k]))
        for k in ks:
            a_, b_ = st(g_all.get(k, [])), st(g_tk.get(k, []))
            if not a_:
                continue
            h1 = st([t for t in g_all[k] if t["in"] <= IS_END])
            h2 = st([t for t in g_all[k] if t["in"] >= OOS_START])
            bt_ = (f"{b_['n'] / years / len(SEEDS):.1f} | {pct(b_['win'], 0)} | {pct(b_['avg'], 2)} | {b_['pf']:.2f}" if b_ else "0 | | | ")
            w(f"| {k} | {a_['n'] / years:.1f} | {pct(a_['win'], 0)} | {pct(a_['avg'], 2)} | {a_['pf']:.2f} | "
              f"{pct(h1['avg'], 2) if h1 else '-'} / {pct(h2['avg'], 2) if h2 else '-'} | {bt_} |")

    table("1. ルールごと", lambda t: NAMES[rule_of[id(t)]], [NAMES[k] for k in "BMCV"])
    table("2. セクターごと", lambda t: sec.get(t["sym"], "不明"))
    table("3. テーマごと", lambda t: theme.get(t["sym"], "テーマの外"),
          note="テーマは業種で近似（半導体＝Semiconductors、半導体製造装置＝Semiconductor Equipment & Materials など）。監視リストの「データセンターの電力・冷却」などは業種が幅広いため「テーマの外」に入る。")
    table("4-1. 買った日のS&P500の局面ごと", lambda t: spx.get(t["in"], "不明"), ["上昇", "横ばい", "下落"],
          note="局面: 30週線（150日線）より上かつ4週前より上向き＝上昇、下かつ下向き＝下落、それ以外＝横ばい（毎朝のscan.mdと同じ考え方）。")
    table("4-2. 買った日のNASDAQ100の局面ごと", lambda t: ndx.get(t["in"], "不明"), ["上昇", "横ばい", "下落"])

    # 局面ごとの資金の増え方（その局面の日だけをつないだ年率）
    w("\n### 4-3. 局面ごとの資金の増え方（S&P500の局面の日だけをつないだ年率、ランダム順10通りの中央値）\n")
    w("| 局面 | 日数の割合 | 年率 |")
    w("|---|---|---|")
    for rg in ("上昇", "横ばい", "下落"):
        vals = []
        n = 0
        for c in curves:
            g, n = 1.0, 0
            for k in range(1, len(days)):
                if spx.get(days[k]) == rg:
                    g *= c[k] / c[k - 1]
                    n += 1
            vals.append(g ** (252 / n) - 1 if n else 0)
        w(f"| {rg} | {pct(n / (len(days) - 1), 0)} | {pct(cb.med(vals))} |")

    w("\n## 5. ルール × S&P500の局面（全部の合図の1回平均 / 勝率 / 件数）\n")
    w("| ルール | 上昇 | 横ばい | 下落 |")
    w("|---|---|---|---|")
    for k in "BMCV":
        cells = []
        for rg in ("上昇", "横ばい", "下落"):
            s_ = st([t for t in tr if rule_of[id(t)] == k and spx.get(t["in"]) == rg])
            cells.append(f"{pct(s_['avg'], 2)} / {pct(s_['win'], 0)} / {s_['n']}件" if s_ else "-")
        w(f"| {NAMES[k]} | " + " | ".join(cells) + " |")

    w("\n## 注意\n")
    w("- セクター・業種は今のYahooの分類を過去にも使っている。テーマは業種で近似したもので、監視リストの7グループとは一致しない。NASDAQ100は含めていない。")
    w("- 件数の少ない分け方（年に数件）の差は、偶然の影響が大きい。前半・後半の両方で同じ傾向かを見る。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
