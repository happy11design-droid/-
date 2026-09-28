#!/usr/bin/env python3
"""オニール『オニールの成長株発掘法』の図（第1・2・14章のチャート）から読み取った形の条件のバックテスト

使い方:
  tools/backtest_figures.py run [--out FILE]

図の書き込み（文字の本文には出てこない、または数値のないもの）を、Claudeが数値にした:
  T 終値の横ばい: 上抜けの直前の週足の終値が3週続けてほぼ同じ（「3週連続で終値がほぼ同じ」「6週連続で終値がほぼ同じで短小線」p.69・70・81、第14章）。
      3週の終値の最高÷最安−1 ≦ 1.5%（2.5%も比べる）
  D 取っ手での出来高の減少: 上抜けの前5日の平均出来高 ≦ 50日平均×0.8（「取っ手部分で出来高減少」「安値での出来高減少は売りがまったくないことを示す」p.65・69・80、第14章）
  A 買い集めの週: ベースの中で、出来高が10週平均より多い週のうち上げた週の数 > 下げた週の数（「上昇週に大商い」「出来高増加がカギ」p.69、第14章）
  W 幅の広いルーズな形を除く: ベースの中の週足の値幅（高値−安値）÷終値の平均 ≦ 10%（「下落しやすい幅の広いルーズな構造」p.82・84）
  S 急落のあとのベースを除く: ベースの中で、15日のうちに40%以上下げた場面がない（「株価が3週間で57%下落」「12週間で50%下落」は買ってはいけない p.84）
  R RSラインの高値更新（「レラティブストレングスラインが高値更新」第14章）。株価÷S&P500 が直近5日に直前250日の最高値を上回る
  買いの形 DB ダブルボトム: ベースの中で、2つ目の安値が1つ目の安値を下回り（振るい落とし）、その間の高値を上抜けた日に買う（p.72〜74、第14章）
対象: 後知恵なしの監視銘柄。期間は 設計期間 2015〜2021年 / 確認期間 2022年〜（形は設計期間の成績で選ぶ）。
"""
import argparse
import bisect
import datetime as dt
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_compare2 as c2
import backtest_crash as bcr
import backtest_minervini2 as bm2
import backtest_modern as bmo
import backtest_oneil as bo
import backtest_rotation as br
import backtest_swing as bs
import backtest_trend as bt
from backtest_lib import COSTS, DEFAULT_CACHE, Reporter, gen_trades, load_prices, load_universe
from backtest_regime import X_BELOW50, freq_table, srt

RISK, STOP, COST = 0.02, 0.15, COSTS[2]
IS_END, OOS_START = "2021-12-31", "2022-01-01"


def prep(s):
    """週足（週の最終取引日ごと）の終値・高値・安値・出来高"""
    n = len(s["c"])
    we = [k for k in range(n) if s["wend"][k]]
    s["we"] = we
    wc, wh, wl, wv, start = [], [], [], [], 0
    for k in we:
        wc.append(s["c"][k])
        wh.append(max(s["h"][start:k + 1]))
        wl.append(min(s["l"][start:k + 1]))
        wv.append(sum(s["v"][start:k + 1]))
        start = k + 1
    s["wk"] = (wc, wh, wl, wv)


def weeks_before(i, s):
    """i日より前に終わった週の番号の範囲の終わり（その週は含まない）"""
    return bisect.bisect_right(s["we"], i - 1)


def T(n=3, tol=0.015):
    def f(i, s):
        e = weeks_before(i, s)
        if e < n:
            return False
        cs = s["wk"][0][e - n:e]
        return max(cs) / min(cs) - 1 <= tol
    return f


def D(i, s):
    v50 = s["vol50"][i - 1]
    return v50 is not None and i >= 6 and sum(s["v"][i - 5:i]) / 5 <= 0.8 * v50


def base_weeks(i, s):
    kh = s["piv_i"][i]
    if kh is None:
        return None
    a = bisect.bisect_right(s["we"], kh)   # ピボットの日より後に終わった週から
    e = weeks_before(i, s)
    return (a, e) if e - a >= 2 else None


def A(i, s):
    r = base_weeks(i, s)
    if r is None:
        return False
    wc, _, _, wv = s["wk"]
    up = dn = 0
    for k in range(max(r[0], 10), r[1]):
        avg = sum(wv[k - 10:k]) / 10
        if wv[k] > avg:
            if wc[k] > wc[k - 1]:
                up += 1
            elif wc[k] < wc[k - 1]:
                dn += 1
    return up > dn


def W(lim=0.10):
    def f(i, s):
        r = base_weeks(i, s)
        if r is None:
            return False
        wc, wh, wl, _ = s["wk"]
        rng = [(wh[k] - wl[k]) / wc[k] for k in range(r[0], r[1])]
        return sum(rng) / len(rng) <= lim
    return f


def S(i, s):
    kh = s["piv_i"][i]
    if kh is None:
        return False
    c = s["c"]
    for j in range(max(kh, 15), i):
        if c[j] <= 0.6 * max(c[j - 15:j]):
            return False
    return True


def E_db(vol=1.4, depth=0.33, rs_min=80):
    """ダブルボトム: ピボット（直前65週の最高値）からのベースが7週以上。直近25日の安値Dが、それより前のベースの安値Bを下回り、
    BとDの間の高値Cを終値で上抜けた日（前日の終値はC以下）。出来高 ≧ 50日平均×vol、調整幅 ≦ depth、RS ≧ rs_min"""
    def f(i, s):
        kh = s["piv_i"][i]
        if kh is None or i - kh < 35 or (s["rs"][i] or 0) < rs_min or s["vol50"][i] is None:
            return None
        l, h, c = s["l"], s["h"], s["c"]
        d_i = min(range(i - 25, i), key=lambda k: l[k])
        if d_i - kh < 15:
            return None
        b_i = min(range(kh + 1, d_i - 5), key=lambda k: l[k])
        if l[d_i] >= l[b_i]:
            return None
        cc = max(h[b_i:d_i + 1])
        piv = h[kh]
        if (piv - l[d_i]) / piv > depth or not (c[i] > cc >= c[i - 1]) or s["v"][i] < vol * s["vol50"][i]:
            return None
        return -s["rs"][i]
    return f


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/オニールの図から読み取った形.md")
    a = ap.parse_args()
    members, data = load_universe(a.cache, min_bars=260)
    g = load_prices(a.cache, "^GSPC")
    spx = dict(zip(g["date"], g["c"]))
    for sym, d in data.items():
        c2.prep(d)
        bmo.prep(d, spx)
        prep(d)
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
    G = lambda e, x, ok, stop=STOP: gen_trades(data, members, e, x, start, end, ok=ok, fill="open", max_hold=500, stop_pct=stop)
    w_ = bmo.with_

    w("---\ntype: backtest\ntitle: オニールの図から読み取った形\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_figures.py\n---\n")
    w("# オニールの図（第1・2・14章のチャート）から読み取った形のバックテスト\n")
    w(__doc__.split("\n", 5)[5].strip() + "\n")
    w("建玉はすべて同じ（1銘柄に資金の13.3%、同時に7銘柄まで、同じ業種は2銘柄まで＝採用中のルール）。片道0.1%。表の「前半 / 後半」は設計期間 / 確認期間。\n")

    tt, tt25, ww = T(3, 0.015), T(3, 0.025), W(0.10)
    bases = {
        "ミネルヴィニのベース（採用中、出来高2倍）": bm2.E_base(2.0),
        "ベースの上抜け（出来高1.5倍・ベース2週以上・調整幅25%以内）": bm2.E_base(1.5, depth=0.25, min_len=10),
        "オニール（本の数値、出来高1.5倍・ベース7週以上・33%以内・RS85）": bo.E_oneil,
    }
    FILT = [("そのまま", ()), ("＋T 終値の横ばい（1.5%）", (tt,)), ("＋T 終値の横ばい（2.5%）", (tt25,)), ("＋D 出来高の減少", (D,)),
            ("＋A 買い集めの週", (A,)), ("＋W 幅の広い形を除く", (ww,)), ("＋S 急落のあとを除く", (S,)), ("＋R RSライン", (bmo.ok_rsl,)),
            ("＋T・A・W・S（図の良い形をすべて）", (tt25, A, ww, S))]
    res = {}
    for bname, e in bases.items():
        w(f"\n## {bname}\n")
        rep.header("RSの高い順")
        for fname, fs in FILT:
            t = G(w_(e, *fs) if fs else e, X_BELOW50, ok_rot)
            res[(bname, fname)] = t
            rep.line(fname, t, STOP)
    w("\n## 新しい買いの形: ダブルボトム（振るい落としの後の上抜け）\n")
    rep.header("RSの高い順")
    DB = {
        "ダブルボトム・50日線割れで手じまい": G(E_db(), X_BELOW50, ok_rot),
        "ダブルボトム＋T 終値の横ばい（2.5%）": G(w_(E_db(), tt25), X_BELOW50, ok_rot),
        "ダブルボトム＋R RSライン": G(w_(E_db(), bmo.ok_rsl), X_BELOW50, ok_rot),
        "ダブルボトム・オニールの売り（損切り8%・20%で利益確定・8週ルール）": G(E_db(), bo.X_oneil(), ok_rot, stop=0.08),
    }
    for k, t in DB.items():
        rep.line(k, t, STOP)
    w("\n## 新高値V2（RS上位10）に図の条件を加える\n")
    rep.header("RSの高い順")
    V = {"今のルール": G(c2.V2, X_BELOW50, ok10), "＋T 終値の横ばい（2.5%）": G(w_(c2.V2, tt25), X_BELOW50, ok10),
         "＋D 出来高の減少": G(w_(c2.V2, D), X_BELOW50, ok10)}
    for k, t in V.items():
        rep.line(k, t, STOP)

    # 組み合わせ: 設計期間で一番良い形を選ぶ
    w_tmp = []
    tmp = bmo.GroupReporter(w_tmp.append, data, days, halves, yrs, cost=COST, risk=RISK, group_of=ind, cap=2)
    is_cagr = lambda tr: tmp.med([tmp.port(tr, STOP, start, IS_END, seed=k)["cagr"] for k in tmp.SEEDS])
    cand = {f"{b}・{f}": t for (b, f), t in res.items()}
    cand.update({f"ダブルボトム: {k}": t for k, t in DB.items()})
    best = max(cand, key=lambda k: is_cagr(cand[k]))
    bestv = max(V, key=lambda k: is_cagr(V[k]))
    b3 = bs.simulate(data, members, bs.O_method3, bs.X_upper_band, start, end, ok=ok_rot)
    k3 = G(bcr.C3, c2.X_MA5, ok_rot)
    cur = srt(b3 + res[("ミネルヴィニのベース（採用中、出来高2倍）", "そのまま")] + k3 + V["今のルール"])
    w("\n## 採用ルールの組み合わせ（7銘柄の枠と、同じ業種2銘柄までを共有）\n")
    w(f"設計期間の年率で選んだ形: ベースの上抜け系＝{best}、新高値V2＝{bestv}（確認期間の成績は選ぶときに見ていない）\n")
    combos = [("今の採用ルール（ボリンジャーIII＋ミネルヴィニ＋急落の底＋新高値V2、業種2銘柄まで）", cur),
              ("ミネルヴィニを、設計期間で選んだ形に入れ替え", srt(b3 + cand[best] + k3 + V["今のルール"])),
              ("さらに新高値V2を、設計期間で選んだ形に入れ替え", srt(b3 + cand[best] + k3 + V[bestv])),
              ("今の採用ルールに、ダブルボトムを加える", srt(cur + DB["ダブルボトム・50日線割れで手じまい"]))]
    rep.header("RSの高い順")
    for k, t in combos:
        rep.line(k, t, STOP)
    w("")
    freq_table(w, rep, combos, days, yrs)
    w("\n## 注意\n")
    w("- 図の書き込みを数値にしたのはClaude（本は「ほぼ同じ」「幅が広い」などと書き、数値を示していない）。")
    w("- 業種は今のYahooの分類を過去にも使っている。NASDAQ100は含めていない。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
