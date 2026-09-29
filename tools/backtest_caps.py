#!/usr/bin/env python3
"""業種の上限の広げ方と、ディフェンシブ業種の有無を比べるバックテスト

使い方:
  tools/backtest_caps.py run [--out FILE]

今の採用ルール: ボリンジャーIII＋ミネルヴィニ＋急落の底＋新高値V2（RS上位10・2年の最高値以上）、同時に7銘柄まで、
同じ業種（Yahooの細かい業種）は2銘柄まで。これに次を加えて比べる。
  1. セクターの上限: Yahooの大きな分類（テクノロジー、資本財など11種）ごとに3・4・5銘柄まで（業種2銘柄までは残す）
  2. テーマのまとまりの上限: 監視リストの7グループに近い形で、似た業種をまとめて2・3銘柄まで
     （半導体／製造装置／ハード・端末／通信機器・電子部品・計測／ソフト・ITサービス／ネット。それ以外は業種のまま）
  3. ディフェンシブ業種を監視銘柄から外す: 生活必需品・ヘルスケア・公益・通信サービス・不動産のセクターを除く
対象: 後知恵なしの監視銘柄。設計期間 2015〜2021年 / 確認期間 2022年〜。
"""
import argparse
import collections
import datetime as dt
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_compare2 as c2
import backtest_crash as bcr
import backtest_figures2 as f2
import backtest_minervini2 as bm2
import backtest_modern as bmo
import backtest_rotation as br
import backtest_swing as bs
import backtest_trend as bt
from backtest_lib import COSTS, DEFAULT_CACHE, gen_trades, load_prices, load_universe, pct
from backtest_regime import X_BELOW50, srt

RISK, STOP, COST = 0.02, 0.15, COSTS[2]
IS_END, OOS_START = "2021-12-31", "2022-01-01"
DEFENSIVE = {"Consumer Defensive", "Healthcare", "Utilities", "Communication Services", "Real Estate"}
THEME = {
    "Semiconductors": "半導体",
    "Semiconductor Equipment & Materials": "製造装置",
    "Computer Hardware": "ハード・端末", "Consumer Electronics": "ハード・端末",
    "Communication Equipment": "通信機器・部品・計測", "Electronic Components": "通信機器・部品・計測",
    "Scientific & Technical Instruments": "通信機器・部品・計測",
    "Software—Application": "ソフト・ITサービス", "Software—Infrastructure": "ソフト・ITサービス",
    "Information Technology Services": "ソフト・ITサービス",
    "Internet Content & Information": "ネット", "Internet Retail": "ネット",
}



def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/業種の上限とディフェンシブ業種.md")
    a = ap.parse_args()
    members, data = load_universe(a.cache, min_bars=260)
    g = load_prices(a.cache, "^GSPC")
    f2.SPX.update(zip(g["date"], g["c"]))
    for sym, d in data.items():
        c2.prep(d)
        bmo.prep(d, f2.SPX)
        f2.prep(d)
        d["sym"] = sym
    bt.add_rs_rank(data, members)
    u = json.load(open(os.path.join(a.cache, "universe.json")))
    ex = os.path.join(a.cache, "industry_extra.json")
    if os.path.exists(ex):
        u.update(json.load(open(ex)))
    ind = {s: (u.get(s) or {}).get("industry") for s in data}
    sec = {s: (u.get(s) or {}).get("sector") for s in data}
    theme = {s: THEME.get(ind[s], ind[s]) for s in data}
    spy = load_prices(a.cache, "SPY")
    end = dt.date.today().isoformat()
    start = "2015-01-02"
    days = [d for d in spy["date"] if start <= d <= end]
    last3 = (dt.date.fromisoformat(end) - dt.timedelta(days=365 * 3)).isoformat()
    fridays = [d for k, d in enumerate(days) if k + 1 == len(days) or dt.date.fromisoformat(days[k + 1]).isocalendar()[1] != dt.date.fromisoformat(d).isocalendar()[1]]
    lists_all = br.build_lists(data, members, fridays, ind)
    pos = {s: {d: k for k, d in enumerate(v["date"])} for s, v in data.items()}
    week_of, fi, last = {}, 0, None
    for d in days:
        while fi < len(fridays) and fridays[fi] < d:
            last = fridays[fi]
            fi += 1
        week_of[d] = last

    def filters(lists):
        sets = {f: set(l) for f, l in lists.items()}
        ranks = {f: {s: k + 1 for k, (_, s) in enumerate(sorted(((data[s]["rs"][pos[s][f]] or 0, s) for s in l if f in pos[s]), reverse=True))}
                 for f, l in lists.items()}
        ok_rot = lambda s, i, sp: bt.liquid(s, i, sp) and week_of.get(s["date"][i]) is not None and s["sym"] in sets[week_of[s["date"][i]]]
        ok10 = lambda s, i, sp: bt.liquid(s, i, sp) and week_of.get(s["date"][i]) is not None and ranks[week_of[s["date"][i]]].get(s["sym"], 10 ** 9) <= 10
        return ok_rot, ok10

    G = lambda e, x, ok, mh=500: gen_trades(data, members, e, x, start, end, ok=ok, fill="open", max_hold=mh, stop_pct=STOP)
    v2o = bmo.with_(c2.V2, f2.O)

    def combo(lists):
        ok_rot, ok10 = filters(lists)
        b3 = bs.simulate(data, members, bs.O_method3, bs.X_upper_band, start, end, ok=ok_rot)
        return srt(b3 + G(bm2.E_base(2.0), X_BELOW50, ok_rot) + G(bcr.C3, c2.X_MA5, ok_rot, 60) + G(v2o, X_BELOW50, ok10))

    cur = combo(lists_all)
    lists_nd = {f: [s for s in l if sec.get(s) not in DEFENSIVE] for f, l in lists_all.items()}
    nodef = combo(lists_nd)

    halves = [("設計期間", start, IS_END), ("確認期間", OOS_START, end)]
    yrs = len(days) / 252
    L = []
    w = L.append
    R = lambda **k: bmo.GroupReporter(w, data, days, halves, yrs, cost=COST, risk=RISK, **k)

    def recent(rep, tr):
        rs = [rep.port(tr, STOP, last3, end, seed=k) for k in rep.SEEDS]
        return rep.med([p["cagr"] for p in rs]), rep.med([p["mdd"] for p in rs])

    w("---\ntype: backtest\ntitle: 業種の上限とディフェンシブ業種\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_caps.py\n---\n")
    w("# 業種の上限の広げ方と、ディフェンシブ業種の有無のバックテスト\n")
    w(__doc__.split("\n", 5)[5].strip() + "\n")
    w("建玉はすべて同じ（1銘柄に資金の13.3%、同時に7銘柄まで）。片道0.1%。表の「前半 / 後半」は設計期間 / 確認期間。\n")

    # 0. 監視銘柄と買いの合図のセクター内訳
    w("\n## 0. 後知恵なしの監視銘柄と、買いの合図のセクター内訳\n")
    w("| セクター | 監視銘柄に入った延べ週数の割合 | 買いの合図の割合（設計期間） | 買いの合図の割合（確認期間） |")
    w("|---|---|---|---|")
    wk = collections.Counter(sec.get(s) for l in lists_all.values() for s in l)
    tot = sum(wk.values())
    sig1 = collections.Counter(sec.get(t["sym"]) for t in cur if t["in"] <= IS_END)
    sig2 = collections.Counter(sec.get(t["sym"]) for t in cur if t["in"] >= OOS_START)
    n1, n2 = sum(sig1.values()), sum(sig2.values())
    for k, v in wk.most_common():
        mark = "（ディフェンシブ）" if k in DEFENSIVE else ""
        w(f"| {k}{mark} | {pct(v / tot)} | {pct(sig1[k] / n1)} | {pct(sig2[k] / n2)} |")

    w("\n## 1〜3. 上限とディフェンシブ業種の比較（今の採用ルールの組み合わせ）\n")
    w("「直近3年」は ランダム順10通りの年率の中央値 / 最大下落率の中央値。\n")
    rows = [
        ("今の採用ルール（業種2銘柄まで）", cur, dict(group_of=ind, cap=2)),
        ("上限なし（参考）", cur, dict()),
        ("業種2＋セクター3銘柄まで", cur, dict(group_of=ind, cap=2, group2_of=sec, cap2=3)),
        ("業種2＋セクター4銘柄まで", cur, dict(group_of=ind, cap=2, group2_of=sec, cap2=4)),
        ("業種2＋セクター5銘柄まで", cur, dict(group_of=ind, cap=2, group2_of=sec, cap2=5)),
        ("業種2＋テーマのまとまり2銘柄まで", cur, dict(group_of=ind, cap=2, group2_of=theme, cap2=2)),
        ("業種2＋テーマのまとまり3銘柄まで", cur, dict(group_of=ind, cap=2, group2_of=theme, cap2=3)),
        ("テーマのまとまり2銘柄まで（業種の上限の代わり）", cur, dict(group_of=theme, cap=2)),
        ("ディフェンシブ業種を外す（業種2銘柄まで）", nodef, dict(group_of=ind, cap=2)),
        ("ディフェンシブ業種を外す＋セクター4銘柄まで", nodef, dict(group_of=ind, cap=2, group2_of=sec, cap2=4)),
    ]
    first = True
    rec = []
    for k, tr, kw in rows:
        rep = R(**kw)
        if first:
            rep.header("RSの高い順")
            first = False
        rep.line(k, tr, STOP)
        rec.append((k, *recent(rep, tr)))
    w("\n| 条件 | 直近3年 年率 | 直近3年 最大下落率 |")
    w("|---|---|---|")
    for k, c, m in rec:
        w(f"| {k} | {pct(c)} | {pct(m)} |")
    w("\n## 注意\n")
    w("- セクター・業種は今のYahooの分類を過去にも使っている。テーマのまとまりは監視リストの7グループに合わせてClaudeが業種をまとめたもの。NASDAQ100は含めていない。")
    w("- 上限の数（3・4・5、2・3）は比べるために置いた値。確認期間の成績を見て選び直すと当てはめすぎになる。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
