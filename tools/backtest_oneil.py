#!/usr/bin/env python3
"""オニール『オニールの成長株発掘法』のルール（CAN-SLIM）を新分析ツールに採用するかのバックテスト

使い方:
  tools/backtest_oneil.py run [--out FILE]

数値は `書籍ルール/オニール_ルール表.md` と章ごとの抽出の値（P の各項目の出典を参照）。本にない値はClaudeが置いたもので、その旨を注記する。
  買い（O）: ベース（直前65週の最高値＝ピボットの日から前日まで）の長さ ≧ P["base_min"] 日、調整幅 ≦ P["depth"]、
            終値がピボットを上回り、出来高 ≧ 50日平均 × P["vol"]、RS ≧ P["rs"]、翌日の寄り付き ≦ ピボット ×（1 ＋ P["chase"]）
  M（市場の方向）: 指数の売り抜けの日（前日比 −P["dist_drop"] 以下の下げで出来高が前日より多い日）が直近 P["dist_win"] 日に
            P["dist_max"] 日以上 → 調整局面（新しい買いをしない）。調整局面の安値の後、反発の P["ftd_day"] 日目以降に
            指数が P["ftd_up"] 以上上げて出来高が前日より多い日（フォロースルー）→ 上昇局面に戻す
  損切り: 買値の P["stop"] 下（引け値で判定）
  利益確定: 買値の P["take"] 上で売る。ただし上抜けから P["fast_days"] 日以内に P["fast_gain"] 上げたら、上抜けから P["hold_days"] 日は持つ
  C・A（四半期・年間のEPS）: 過去の決算の数値が5四半期分しか取れないため、バックテストでは確かめられない（毎朝のスキャンの確認項目にとどめる）
比較: 今の採用ルール（新高値V2・ミネルヴィニのベース）と、その組み合わせ
対象: (1) 後知恵なしの監視銘柄（毎週選び直す、2015年〜と直近3年）、(2) 今の監視銘柄（直近3年、後知恵あり）
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
import backtest_rotation as br
import backtest_swing as bs
import backtest_theme as bth
import backtest_trend as bt
from backtest_lib import COSTS, DEFAULT_CACHE, Reporter, gen_trades, load_prices, load_universe
from backtest_regime import X_BELOW50, freq_table, srt

RISK, STOP15, COST = 0.02, 0.15, COSTS[2]
P = {
    # 買い（第2章 p.63・65・67、第19章 p.274）
    "base_min": 35,      # ベースの長さ ≧ 7週（取っ手付きカップ 7〜65週）
    "depth": 0.33,       # 調整幅 ≦ 33%（取っ手付きカップ 12〜15%〜33%）
    "prior": 0.30,       # ベースの前の上昇 ≧ 30%（ピボット ≧ ベースの前の安値×1.3。安値を探す期間 prior_win はClaudeが置いた）
    "prior_win": 130,
    "vol": 1.5,          # 上抜けの日の出来高 ≧ 平均×1.5（40〜50%増、第19章は50%以上）
    "rs": 85,            # RS ≧ 85（第19章）
    "chase": 0.05,       # ピボットから5%より上では買わない
    "min_price": 15,     # 株価 ≧ 15ドル（ナスダック15〜300ドル、NYSE 20〜300ドル。10ドル以下は避ける）
    # 市場の方向（第9章 p.139・147）。どれか1つの指数で売り抜けが4〜5日あれば調整局面、どれか1つの指数でフォロースルーがあれば上昇局面
    "dist_drop": 0.002,  # 売り抜けの日: 出来高が前日より多く、指数が下げた日（下げ幅0.2%はClaudeが置いた。本は「失速」も含む）
    "dist_win": 25,      # 4〜5週
    "dist_max": 5,       # 4〜5日
    "dist_expire": None, # 売り抜けの日を、その後の上昇で消す（本にない。None＝使わない）
    "ftd_day": 4,        # 反発の4日目以降
    "ftd_up": 0.01,      # フォロースルーの上げ幅（本は昔の1%から「大幅に引き上げた」とし、新しい値を書いていない）
    # 売り（第10章 p.164、第11章 p.178・187）
    "stop": 0.08,        # 買値から8%下で損切り
    "take": 0.20,        # 20%で利益確定
    "fast_days": 15,     # 1〜3週間で
    "fast_gain": 0.20,   # 20%上げた銘柄は
    "hold_days": 40,     # 最低8週間持つ
}


# ---------- 市場の方向（M） ----------
def market_ok(idxs):
    """{日付: 新しい買いをしてよいか}。idxs は指数の株価の一覧。
    上昇局面で、どれか1つの指数の売り抜けの日が直近 dist_win 日に dist_max 日以上 → 調整局面。
    調整局面で、どれか1つの指数が安値の後の反発 ftd_day 日目以降に ftd_up 以上上げ、出来高が前日より多い → 上昇局面"""
    dates = sorted(set.intersection(*(set(x["date"]) for x in idxs)))
    pos = [{d: k for k, d in enumerate(x["date"])} for x in idxs]
    out, up = {}, True
    dist = [[] for _ in idxs]
    low = [None] * len(idxs)
    rally = [None] * len(idxs)
    for d in dates:
        flip = False
        for n, x in enumerate(idxs):
            i = pos[n][d]
            if i == 0:
                continue
            c, v = x["c"], x["v"]
            chg = c[i] / c[i - 1] - 1
            if up:
                if chg <= -P["dist_drop"] and v[i] > v[i - 1]:
                    dist[n].append(i)
                dist[n] = [k for k in dist[n] if k > i - P["dist_win"] and (not P["dist_expire"] or c[i] < c[k] * (1 + P["dist_expire"]))]
                if len(dist[n]) >= P["dist_max"]:
                    flip = True
            else:
                if low[n] is None or c[i] < c[low[n]]:
                    low[n], rally[n] = i, None     # 安値を更新したら反発の数え直し
                elif rally[n] is None and chg > 0:
                    rally[n] = i                   # 反発の1日目
                if rally[n] is not None and i - rally[n] + 1 >= P["ftd_day"] and chg >= P["ftd_up"] and v[i] > v[i - 1]:
                    flip = True
        if flip:
            up = not up
            dist = [[] for _ in idxs]
            low = [None] * len(idxs)
            rally = [None] * len(idxs)
        out[d] = up
    return out


# ---------- 買い ----------
def E_oneil(i, s):
    kh = s["piv_i"][i]
    if kh is None or i + 1 >= len(s["c"]) or i - kh < P["base_min"] or (s["rs"][i] or 0) < P["rs"] or s["c"][i] < P["min_price"]:
        return None
    piv = s["h"][kh]
    if kh < P["prior_win"] or piv < min(s["l"][kh - P["prior_win"]:kh]) * (1 + P["prior"]):
        return None
    if s["c"][i] <= piv or s["o"][i + 1] > piv * (1 + P["chase"]):
        return None
    if (piv - min(s["l"][kh:i])) / piv > P["depth"]:
        return None
    if s["vol50"][i] is None or s["v"][i] < P["vol"] * s["vol50"][i]:
        return None
    return -s["rs"][i]


# ---------- 手じまい ----------
def X_oneil(after=None):
    """利益確定（買値の+take）。上抜けからfast_days日以内に+fast_gainなら hold_days 日は持ち、その後は after（なければ即売り）"""
    def f(j, s, k, px):
        i = j - k
        fast = max(s["c"][i + 1:i + 1 + min(k, P["fast_days"])], default=0) >= px * (1 + P["fast_gain"])
        if fast:
            if k < P["hold_days"]:
                return False
            return True if after is None else after(j, s, k, px)
        return s["c"][j] >= px * (1 + P["take"])
    return f


def X_after_weeks(n):
    return lambda j, s, k, px: k >= n * 5


def X_or(*fs):
    return lambda j, s, k, px: any(f(j, s, k, px) for f in fs)


def X_market(allow):
    return lambda j, s, k, px: not allow(s["date"][j])


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/オニールの成長株発掘法.md")
    a = ap.parse_args()
    members, data = load_universe(a.cache, min_bars=260)
    for s, d in data.items():
        c2.prep(d)
        d["sym"] = s
    bt.add_rs_rank(data, members)
    IDX = {k: load_prices(a.cache, k) for k in ("^GSPC", "^IXIC")}
    M = {"S&P500": market_ok([IDX["^GSPC"]]), "両方": market_ok(list(IDX.values()))}
    allow_sp = lambda d: M["S&P500"].get(d, True)
    allow_m = lambda d: M["両方"].get(d, True)   # 本のとおり（どれか1つの指数で判断）

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
    ranks = {}
    for f, lst in lists.items():
        rs = sorted(((data[s]["rs"][pos[s][f]] or 0, s) for s in lst if f in pos[s]), reverse=True)
        ranks[f] = {s: k + 1 for k, (_, s) in enumerate(rs)}
    week_of, fi, last = {}, 0, None
    for d in days:
        while fi < len(fridays) and fridays[fi] < d:
            last = fridays[fi]
            fi += 1
        week_of[d] = last

    def ok_rot(s, i, spans):
        wk = week_of.get(s["date"][i])
        return bt.liquid(s, i, spans) and wk is not None and s["sym"] in lists[wk]

    def ok_top(n):
        def f(s, i, spans):
            wk = week_of.get(s["date"][i])
            return bt.liquid(s, i, spans) and wk is not None and ranks[wk].get(s["sym"], 10 ** 9) <= n
        return f

    up_days = {k: sum(1 for d in days if v.get(d, True)) / len(days) for k, v in M.items()}

    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: オニールの成長株発掘法\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_oneil.py\n---\n")
    w("# オニール『オニールの成長株発掘法』のルールを採用するかのバックテスト\n")
    w(__doc__.split("\n", 5)[5].strip() + "\n")
    w("使った数値: " + "、".join(f"{k}={v}" for k, v in P.items()) + "\n")
    w(f"市場の方向が上昇局面だった日の割合（2015年〜）: S&P500だけで見る {up_days['S&P500'] * 100:.0f}%、S&P500とNASDAQ総合のどちらかで見る（本のとおり） {up_days['両方'] * 100:.0f}%\n")
    w("建玉はすべて同じ（1銘柄に資金の13.3%、同時に7銘柄まで。損切りが8%のオニールでも同じ建玉にそろえて比べる）。片道0.1%。データの最終日に保有中の売買は数えない。\n")
    for lab, lo in (("2015年〜", start), ("直近3年", dt.date.today().replace(year=dt.date.today().year - 3).isoformat())):
        dd = [d for d in days if d >= lo]
        mid = "2020-12-31" if lo == start else "2024-12-31"
        rep = Reporter(w, data, dd, [("前半", lo, mid), ("後半", (dt.date.fromisoformat(mid) + dt.timedelta(days=1)).isoformat(), end)],
                       len(dd) / 252, cost=COST, risk=RISK)
        g = lambda e, x, ok, stop, allow=None, mh=500: gen_trades(data, members, e, x, lo, end, ok=ok, fill="open", allow=allow, max_hold=mh, stop_pct=stop)
        w(f"\n## 後知恵なしの監視銘柄（{lab}）\n")
        w("\n### 1. オニールの買いと売り\n")
        rep.header("RSの高い順")
        res = {}
        res["O 本のとおり"] = g(E_oneil, X_oneil(), ok_rot, P["stop"], allow_m)
        for rs in (80, 90):
            P["rs"] = rs
            res[f"O RS≧{rs}（ルール表 p.122-123。本のとおりは85）"] = g(E_oneil, X_oneil(), ok_rot, P["stop"], allow_m)
        P["rs"] = 85
        res["O 市場の方向をS&P500だけで見る"] = g(E_oneil, X_oneil(), ok_rot, P["stop"], allow_sp)
        res["O 市場の方向なし"] = g(E_oneil, X_oneil(), ok_rot, P["stop"])
        res["O 8週持った後は50日線割れまで持つ"] = g(E_oneil, X_oneil(X_BELOW50), ok_rot, P["stop"], allow_m)
        res["O 13週たっても利益確定・損切りにならなければ売る"] = g(E_oneil, X_or(X_oneil(), X_after_weeks(13)), ok_rot, P["stop"], allow_m)
        res["O 市場が調整局面に変わったら持ち株も売る"] = g(E_oneil, X_or(X_oneil(), X_market(allow_m)), ok_rot, P["stop"], allow_m)
        res["O 買いだけオニール、売りは今のルール（50日線割れ・損切り15%）"] = g(E_oneil, X_BELOW50, ok_rot, STOP15, allow_m)
        res["O 監視銘柄のRS上位10だけ"] = g(E_oneil, X_oneil(), ok_top(10), P["stop"], allow_m)
        res["O 監視銘柄に限らずS&P500全体から探す"] = g(E_oneil, X_oneil(), bt.liquid, P["stop"], allow_m)
        for k, t in res.items():
            rep.line(k, t, STOP15)
        w("\n### 2. 今の採用ルールに、オニールの売り・市場の方向を当てる\n")
        rep.header("RSの高い順")
        v2 = g(c2.V2, X_BELOW50, ok_top(10), STOP15)
        mb = g(bm2.E_base(2.0), X_BELOW50, ok_rot, STOP15)
        cmp_ = {
            "新高値V2（今のルール: RS上位10・50日線割れ・損切り15%）": v2,
            "新高値V2＋市場の方向（オニール）": g(c2.V2, X_BELOW50, ok_top(10), STOP15, allow_m),
            "新高値V2・売りをオニール（+20%利確・8週・損切り8%）": g(c2.V2, X_oneil(), ok_top(10), P["stop"]),
            "ミネルヴィニのベース（今のルール）": mb,
            "ミネルヴィニのベース＋市場の方向（オニール）": g(bm2.E_base(2.0), X_BELOW50, ok_rot, STOP15, allow_m),
        }
        for k, t in cmp_.items():
            rep.line(k, t, STOP15)
        b3 = bs.simulate(data, members, bs.O_method3, bs.X_upper_band, lo, end, ok=ok_rot)
        k3 = g(bcr.C3, c2.X_MA5, ok_rot, STOP15, mh=60)
        base = b3 + mb + k3
        combos = [("今の採用ルール（ボリンジャーIII＋ミネルヴィニ＋急落の底＋新高値V2）", srt(base + v2)),
                  ("今の採用ルール＋オニール（本のとおり）", srt(base + v2 + res["O 本のとおり"])),
                  ("新高値V2をオニール（本のとおり）に置き換え", srt(base + res["O 本のとおり"])),
                  ("新高値V2をオニール（RS上位10）に置き換え", srt(base + res["O 監視銘柄のRS上位10だけ"])),
                  ("今の採用ルール＋オニール（S&P500全体から探す）", srt(base + v2 + res["O 監視銘柄に限らずS&P500全体から探す"])),
                  ("今の採用ルールの新高値V2に市場の方向（オニール）を当てる", srt(base + cmp_["新高値V2＋市場の方向（オニール）"]))]
        w("\n### 3. ほかの採用ルールとの組み合わせ（7銘柄の枠を共有）\n")
        rep.header("RSの高い順")
        for k, t in combos:
            rep.line(k, t, STOP15)
        w("")
        freq_table(w, rep, combos, dd, len(dd) / 252)

    # 市場の方向の数値を変えた場合（本は売り抜けを「4〜5日」とし、フォロースルーの上げ幅の新しい値を書いていない）
    w("\n## 市場の方向の数値を変えた場合（後知恵なしの監視銘柄、2015年〜）\n")
    rep = Reporter(w, data, days, [("前半", start, "2020-12-31"), ("後半", "2021-01-01", end)], len(days) / 252, cost=COST, risk=RISK)
    rep.header("RSの高い順")
    keep = dict(P)
    for dm in (4, 5):
        for fu in (0.01, 0.017):
            P["dist_max"], P["ftd_up"] = dm, fu
            mm = market_ok(list(IDX.values()))
            al = lambda d, mm=mm: mm.get(d, True)
            share = sum(1 for d in days if mm.get(d, True)) / len(days)
            tag = f"売り抜け{dm}日・フォロースルー+{fu * 100:.1f}%（上昇局面 {share * 100:.0f}%）"
            rep.line(f"O 本のとおり・{tag}", gen_trades(data, members, E_oneil, X_oneil(), start, end, ok=ok_rot, fill="open", allow=al, max_hold=500, stop_pct=P["stop"]), STOP15)
            rep.line(f"新高値V2＋市場の方向・{tag}", gen_trades(data, members, c2.V2, X_BELOW50, start, end, ok=ok_top(10), fill="open", allow=al, max_hold=500, stop_pct=STOP15), STOP15)
    P.update(keep)

    # 今の監視銘柄（後知恵あり）
    wl = bth.load_watchlist()
    tdata = {s: data[s] for s in wl if s in data}
    for s in wl:
        if s not in tdata:
            d = load_prices(a.cache, s)
            if d and len(d["c"]) > 260:
                c2.prep(d)
                d["sym"] = s
                tdata[s] = d
    import csv
    sp_now = [r["ticker"] for r in csv.DictReader(open(os.path.join(a.cache, "members.csv"))) if not r["end_date"]]
    bth.rs_ranks(a.cache, sorted(set(sp_now) | set(tdata)), tdata)
    tmem = {s: [("0000-00-00", "9999-12-31")] for s in tdata}
    start3 = dt.date.today().replace(year=dt.date.today().year - 3).isoformat()
    d3 = [d for d in days if d >= start3]
    rep = Reporter(w, tdata, d3, [("前半", start3, "2024-12-31"), ("後半", "2025-01-01", end)], len(d3) / 252, cost=COST, risk=RISK)
    g = lambda e, x, stop, allow=None: gen_trades(tdata, tmem, e, x, start3, end, ok=bt.liquid, fill="open", allow=allow, max_hold=500, stop_pct=stop)
    w(f"\n## 今の監視銘柄（{len(tdata)}銘柄、直近3年。後知恵あり）\n")
    rep.header("RSの高い順")
    rep.line("O 本のとおり", g(E_oneil, X_oneil(), P["stop"], allow_m), STOP15)
    rep.line("O 市場の方向なし", g(E_oneil, X_oneil(), P["stop"]), STOP15)
    rep.line("O 8週持った後は50日線割れまで持つ", g(E_oneil, X_oneil(X_BELOW50), P["stop"], allow_m), STOP15)
    rep.line("新高値V2（RS上位10の絞りなし）", g(c2.V2, X_BELOW50, STOP15), STOP15)
    rep.line("ミネルヴィニのベース", g(bm2.E_base(2.0), X_BELOW50, STOP15), STOP15)
    w("\n## 注意\n")
    w("- C・A（EPSの伸び）、I（機関投資家の保有）は過去の数値が取れないため、バックテストに入っていない。")
    w("- 業種は今のYahooの分類を過去にも使っている。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
