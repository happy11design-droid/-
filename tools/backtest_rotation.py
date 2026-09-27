#!/usr/bin/env python3
"""後知恵なしの監視銘柄: 過去の毎週、入れ替え案（tools/watchlist_review.py）と同じ基準で監視銘柄を選び直しながら、採用ルールを当てる

使い方:
  tools/backtest_rotation.py run [--out FILE]

今の87銘柄（今の時点で勝ち組を選んでいるため後知恵あり）の代わりに、その時点で分かる数値だけで監視銘柄を作る。
  対象: その日のS&P500の構成銘柄（NASDAQ100は過去の構成銘柄のデータがないため含めない）
  毎週の最終取引日に:
    追加: 監視銘柄でない銘柄のうち、RSランキング≧90、株価の30週線の局面が「上昇」（終値＞150日線、150日線が20取引日前より上）、
          業種（Yahoo、今の分類を過去にも使う）の3カ月の騰落率の中央値が上位20%、流動性あり
    外す: 監視銘柄のうち、株価の30週線の局面が「下落」（終値＜150日線、150日線が20取引日前より下）かつ RSランキング<50
    上限: 100銘柄（超えたらRSの低い順に外す）
  翌週の各取引日は、直前の週末の監視銘柄だけにルールを当てる。
当てるルール（採用中）: ボリンジャーIII／ミネルヴィニ（本どおりのベース）／急落の底（20日線・5日線の2通り）／新高値V2
比較: 同じ期間のS&P500全体（監視銘柄で絞らない）
"""
import argparse
import datetime as dt
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_compare2 as c2
import backtest_crash as bcr
import backtest_minervini2 as bm2
import backtest_swing as bs
import backtest_trend as bt
from backtest_lib import COSTS, DEFAULT_CACHE, Reporter, gen_trades, is_member, load_prices, load_universe
from backtest_regime import X_BELOW50, freq_table, srt

RISK, STOP, COST = 0.02, 0.15, COSTS[2]
CAP = 100


def build_lists(data, members, fridays, ind):
    """{週末の日付: 監視銘柄の集合}"""
    pos = {s: {d: k for k, d in enumerate(v["date"])} for s, v in data.items()}
    cur, out = set(), {}
    for f in fridays:
        rows = {}
        for s, d in data.items():
            i = pos[s].get(f)
            if i is None or i < 253 or not is_member(members[s], f):
                continue
            m, m20, rs = d["ma150"][i], d["ma150"][i - 20], d["rs"][i]
            if m is None or m20 is None or rs is None:
                continue
            stage = "上昇" if d["c"][i] > m and m > m20 else "下落" if d["c"][i] < m and m < m20 else "横ばい"
            rows[s] = (rs, stage, d["c"][i] / d["c"][i - 63] - 1, bt.liquid(d, i, members[s]))
        by = {}
        for s, x in rows.items():
            if ind.get(s):
                by.setdefault(ind[s], []).append(x[2])
        med = {k: sorted(v)[len(v) // 2] for k, v in by.items() if len(v) >= 3}
        order = sorted(med, key=lambda k: -med[k])
        top = set(order[:max(1, len(order) // 5)])
        cur = {s for s in cur if s in rows and not (rows[s][1] == "下落" and rows[s][0] < 50)}
        cur |= {s for s, x in rows.items() if x[0] >= 90 and x[1] == "上昇" and x[3] and ind.get(s) in top}
        if len(cur) > CAP:
            cur = set(sorted(cur, key=lambda s: -rows[s][0])[:CAP])
        out[f] = frozenset(cur)
    return out


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/後知恵なしの監視銘柄.md")
    a = ap.parse_args()
    members, data = load_universe(a.cache, min_bars=260)
    for s, d in data.items():
        c2.prep(d)
        d["sym"] = s
    bt.add_rs_rank(data, members)
    u = json.load(open(os.path.join(a.cache, "universe.json")))
    ex = os.path.join(a.cache, "industry_extra.json")
    if os.path.exists(ex):
        u.update(json.load(open(ex)))
    ind = {s: (u.get(s) or {}).get("industry") for s in data}
    spy = load_prices(a.cache, "SPY")
    end = dt.date.today().isoformat()
    start = "2015-01-02"
    days = [d for d in spy["date"] if start <= d <= end]
    fridays = [d for k, d in enumerate(days) if k + 1 == len(days) or dt.date.fromisoformat(days[k + 1]).isocalendar()[1] != dt.date.fromisoformat(d).isocalendar()[1]]
    lists = build_lists(data, members, fridays, ind)
    week_of, last = {}, None
    fi = 0
    for d in days:   # その日に使う監視銘柄 = 直前の週末（その日より前）の一覧
        while fi < len(fridays) and fridays[fi] < d:
            last = fridays[fi]
            fi += 1
        week_of[d] = lists.get(last, frozenset())

    def ok_rot(s, i, spans):
        return bt.liquid(s, i, spans) and s["sym"] in week_of.get(s["date"][i], ())

    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: 後知恵なしの監視銘柄\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_rotation.py\n---\n")
    w("# 後知恵なしの監視銘柄（毎週、その時点の数値だけで選び直す）で採用ルールを当てる\n")
    w(__doc__.split("\n", 5)[5].strip() + "\n")
    sizes = [len(v) for v in lists.values()]
    w(f"- 監視銘柄の数（週末ごと）: 平均 {sum(sizes) / len(sizes):.0f}、最小 {min(sizes)}、最大 {max(sizes)}")
    for probe in ("SNDK", "DELL", "NVDA", "MU", "AVGO"):
        first = next((f for f in fridays if probe in lists[f]), None)
        w(f"- {probe}: 最初に監視銘柄に入った週 {first or '入らなかった'}")
    w("")

    for lab, lo in (("2015年〜", start), ("直近3年", dt.date.today().replace(year=dt.date.today().year - 3).isoformat())):
        dd = [d for d in days if d >= lo]
        mid = "2020-12-31" if lo == start else "2024-12-31"
        rep = Reporter(w, data, dd, [("前半", lo, mid), ("後半", (dt.date.fromisoformat(mid) + dt.timedelta(days=1)).isoformat(), end)],
                       len(dd) / 252, cost=COST, risk=RISK)
        w(f"\n## {lab}\n")
        res = {}
        for uni, ok in (("後知恵なしの監視銘柄", ok_rot), ("S&P500全体（絞らない）", bt.liquid)):
            g = lambda e, x, mh: gen_trades(data, members, e, x, lo, end, ok=ok, fill="open", max_hold=mh, stop_pct=STOP)
            b3 = bs.simulate(data, members, bs.O_method3, bs.X_upper_band, lo, end, ok=ok)
            m = g(bm2.E_base(2.0), X_BELOW50, 500)
            k2 = g(bcr.C3, c2.X_MID, 60)
            k3 = g(bcr.C3, c2.X_MA5, 60)
            v2 = g(c2.V2, X_BELOW50, 500)
            res[uni] = [("ボリンジャーIII", b3), ("ミネルヴィニ", m), ("急落の底（20日線で手じまい）", k2),
                        ("急落の底（5日線で手じまい）", k3), ("新高値V2", v2),
                        ("採用中の4つ（ボリンジャーIII＋ミネルヴィニ＋急落の底20日線＋V2）", srt(b3 + m + k2 + v2)),
                        ("採用中の4つ（急落の底は5日線）", srt(b3 + m + k3 + v2))]
        for uni, lst in res.items():
            w(f"\n**{uni}**\n")
            rep.header("ルールごとの順")
            for n, t in lst:
                rep.line(n, t, STOP)
            w("")
            freq_table(w, rep, lst[-2:], dd, len(dd) / 252)
    w("\n## 注意\n")
    w("- 業種は今のYahooの分類を過去にも使っている。上場廃止銘柄の一部は株価データがない（生存者バイアスが少し残る）。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
