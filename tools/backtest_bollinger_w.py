#!/usr/bin/env python3
"""ボリンジャー『ボリンジャーバンド入門』の図（第12章 W型ボトム、第20章 メソッドIII）から読み取った買い方のバックテスト

使い方:
  tools/backtest_bollinger_w.py run [--out FILE]

今の採用ルール（メソッドIII）: %b < 0.05 かつ 21日II% > 0 の翌日の寄り付きで買い、引けで上のバンド以上になったら手じまう。
図から読み取った形（数値はClaudeが図と本文から置いたもの）:
  W型ボトム（図12.1〜12.7）:
    1つ目の安値: 直近40日のうち、%b ≦ 0.05（下のバンドの上か外）の日の最安値
    その後、高値が真ん中の線（20日線）に届く（図12.5「中央バンドに接したり突きぬいたり」）
    2つ目の安値: その後の最安値。価格は1つ目より低くてもよいが、%b は1つ目より高く、かつ 0 以上（バンドの内側。図12.6 の外に抜けた形は無効）
    出来高の確認（図20.3）: 2つ目の安値の日の21日II% が1つ目の安値の日より高い（W4）… 付けた形と付けない形を比べる
  買い（図12.8）: W型の後、出来高が50日平均より多く、値幅（高値−安値）が20日平均より大きく、終値が前日より上の日の翌日の寄り付き（2つ目の安値から10日以内）
  損切り（図12.8の本文）: 2つ目の安値の少し下（安値×0.99）。上限は買値の15%下
  手じまい: 引けで上のバンド以上（今のルールと同じ）／パラボリックSARで損切りを引き上げる（本文「トレイリング・ストップ」）
対象: 後知恵なしの監視銘柄。設計期間 2015〜2021年 / 確認期間 2022年〜。
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
import backtest_modern as bmo
import backtest_rotation as br
import backtest_swing as bs
import backtest_trend as bt
from backtest_lib import COSTS, DEFAULT_CACHE, gen_trades, load_prices, load_universe
from backtest_regime import X_BELOW50, freq_table, srt

RISK, STOP, COST = 0.02, 0.15, COSTS[2]
IS_END, OOS_START = "2021-12-31", "2022-01-01"


def rng20(s):
    h, l, n = s["h"], s["l"], len(s["c"])
    r = [h[k] - l[k] for k in range(n)]
    out, acc = [None] * n, 0.0
    for k in range(n):
        acc += r[k]
        if k >= 20:
            acc -= r[k - 20]
        if k >= 19:
            out[k] = acc / 20
    s["rng20"] = out


def w_bottom(i, s, need_ii=True, look=40):
    """i日（引け）までにW型ボトムができているなら (1つ目の安値の日, 2つ目の安値の日) を返す"""
    pb, l, h, mid, ii = s["pctb"], s["l"], s["h"], s["bb_mid"], s["ii21"]
    if i < look + 5:
        return None
    lows = [k for k in range(i - look, i - 4) if pb[k] is not None and pb[k] <= 0.05]
    if not lows:
        return None
    a = min(lows, key=lambda k: l[k])
    m = next((k for k in range(a + 1, i) if mid[k] is not None and h[k] >= mid[k]), None)
    if m is None or m >= i - 1:
        return None
    b = min(range(m + 1, i + 1), key=lambda k: l[k])
    if pb[b] is None or pb[b] <= pb[a] or pb[b] < 0:
        return None
    if any(pb[k] is not None and pb[k] < 0 for k in range(m + 1, i + 1)):
        return None          # 2つ目の安値の側で下のバンドの外に出た（図12.6 は無効）
    if need_ii and (ii[b] is None or ii[a] is None or ii[b] <= ii[a]):
        return None
    return a, b


def O_w(need_ii=True, trigger=True, within=10, tight=True):
    def f(i, s):
        w = w_bottom(i, s, need_ii)
        if w is None:
            return None
        a, b = w
        if i - b > within or i == b:
            return None
        if not trigger and s["c"][i] <= s["c"][i - 1]:
            return None          # 強い上げの日を待たず、2つ目の安値の後の最初の上げた日に買う
        if trigger:
            c, o, v, v50, r20 = s["c"], s["o"], s["v"], s["vol50"][i], s["rng20"][i]
            if v50 is None or r20 is None or not (c[i] > c[i - 1] and v[i] > v50 and s["h"][i] - s["l"][i] > r20):
                return None
        return {"rank": s["pctb"][b], "kind": "open", "stop": s["l"][b] * 0.99 if tight else None}
    return f


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/ボリンジャーの図から読み取ったW型.md")
    a = ap.parse_args()
    members, data = load_universe(a.cache, min_bars=260)
    for sym, d in data.items():
        c2.prep(d)
        rng20(d)
        d["sym"] = sym
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
    lists = br.build_lists(data, members, fridays, ind)
    pos = {s: {d: k for k, d in enumerate(v["date"])} for s, v in data.items()}
    ranks = {f: {s: k + 1 for k, (_, s) in enumerate(sorted(((data[s]["rs"][pos[s][f]] or 0, s) for s in l if f in pos[s]), reverse=True))}
             for f, l in lists.items()}
    week_of, fi, last = {}, 0, None
    for d in days:
        while fi < len(fridays) and fridays[fi] < d:
            last = fridays[fi]
            fi += 1
        week_of[d] = last
    ok_rot = lambda s, i, sp: bt.liquid(s, i, sp) and week_of.get(s["date"][i]) is not None and s["sym"] in lists[week_of[s["date"][i]]]
    ok10 = lambda s, i, sp: bt.liquid(s, i, sp) and week_of.get(s["date"][i]) is not None and ranks[week_of[s["date"][i]]].get(s["sym"], 10 ** 9) <= 10

    halves = [("設計期間", start, IS_END), ("確認期間", OOS_START, end)]
    yrs = len(days) / 252
    L = []
    w = L.append
    rep = bmo.GroupReporter(w, data, days, halves, yrs, cost=COST, risk=RISK, group_of=ind, cap=2)
    sim = lambda od, x, trail=None: bs.simulate(data, members, od, x, start, end, ok=ok_rot, trail=trail)

    w("---\ntype: backtest\ntitle: ボリンジャーの図から読み取ったW型\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_bollinger_w.py\n---\n")
    w("# ボリンジャーの図（第12章 W型ボトム、第20章 メソッドIII）から読み取った買い方のバックテスト\n")
    w(__doc__.split("\n", 5)[5].strip() + "\n")
    w("建玉はすべて同じ（1銘柄に資金の13.3%、同時に7銘柄まで、同じ業種は2銘柄まで＝採用中のルール）。片道0.1%。表の「前半 / 後半」は設計期間 / 確認期間。\n")
    w("\n## 1. ボリンジャーIIIの買い方の比較（後知恵なしの監視銘柄）\n")
    rep.header("%bの低い順")
    V = {
        "今のルール（%b<0.05・II%>0の翌日に買う、上のバンドで手じまい）": sim(bs.O_method3, bs.X_upper_band),
        "W型＋II%の確認＋強い上げの日に買う（図のとおり）・上のバンド": sim(O_w(True, True), bs.X_upper_band),
        "W型＋強い上げの日（II%の確認なし）・上のバンド": sim(O_w(False, True), bs.X_upper_band),
        "W型（図のとおり）・損切りは買値の15%下（2つ目の安値にしない）・上のバンド": sim(O_w(True, True, tight=False), bs.X_upper_band),
        "W型（II%の確認なし）・損切りは買値の15%下・上のバンド": sim(O_w(False, True, tight=False), bs.X_upper_band),
        "W型＋II%の確認（強い上げの日を待たない）・上のバンド": sim(O_w(True, False, within=3), bs.X_upper_band),
        "W型（図のとおり）・パラボリックSARで損切りを引き上げ、上のバンドでも手じまい": sim(O_w(True, True), bs.X_upper_band, bs.trail_sar),
        "W型（図のとおり）・パラボリックSARだけで手じまい": sim(O_w(True, True), lambda j, s, k, t: None, bs.trail_sar),
        "今のルール・パラボリックSARで損切りを引き上げ": sim(bs.O_method3, bs.X_upper_band, bs.trail_sar),
    }
    for k, t in V.items():
        rep.line(k, t, STOP)

    # 組み合わせ（設計期間で一番良いW型を選ぶ）
    tmp_ = []
    tmp = bmo.GroupReporter(tmp_.append, data, days, halves, yrs, cost=COST, risk=RISK, group_of=ind, cap=2)
    is_cagr = lambda tr: tmp.med([tmp.port(tr, STOP, start, IS_END, seed=k)["cagr"] for k in tmp.SEEDS])
    wk = [k for k in V if not k.startswith("今")]
    best = max(wk, key=lambda k: is_cagr(V[k]))
    G = lambda e, x, ok, mh=500: gen_trades(data, members, e, x, start, end, ok=ok, fill="open", max_hold=mh, stop_pct=STOP)
    others = G(bm2.E_base(2.0), X_BELOW50, ok_rot) + G(bcr.C3, c2.X_MA5, ok_rot, 60) + G(c2.V2, X_BELOW50, ok10)
    b3 = V["今のルール（%b<0.05・II%>0の翌日に買う、上のバンドで手じまい）"]
    combos = [("今の採用ルール（ボリンジャーIII＋ミネルヴィニ＋急落の底＋新高値V2、業種2銘柄まで）", srt(b3 + others)),
              (f"ボリンジャーIIIを、設計期間で選んだW型（{best}）に入れ替え", srt(V[best] + others)),
              ("今の採用ルールに、W型（図のとおり）を加える", srt(b3 + V["W型＋II%の確認＋強い上げの日に買う（図のとおり）・上のバンド"] + others))]
    w("\n## 2. 採用ルールの組み合わせ（7銘柄の枠と、同じ業種2銘柄までを共有）\n")
    w(f"設計期間の年率で選んだW型: {best}（確認期間の成績は選ぶときに見ていない）\n")
    rep.header("RSの高い順")
    for k, t in combos:
        rep.line(k, t, STOP)
    w("")
    freq_table(w, rep, combos, days, yrs)
    w("\n## 注意\n")
    w("- W型の数値（40日、%b≦0.05、10日以内、出来高と値幅の平均との比較、安値×0.99）はClaudeが図と本文から置いたもの。本は数値を示していない。")
    w("- 業種は今のYahooの分類を過去にも使っている。NASDAQ100は含めていない。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
