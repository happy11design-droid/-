#!/usr/bin/env python3
"""策9（Fableの大胆な策）: 日本株の権利取りの前の先回り（2026-11-14）

日経225の今の構成銘柄（`long/index/n225_codes.json`、Wikipedia の英語版・日本語版から。今の構成なので良く出る向きに偏る）の日足と配当を
Yahoo から取り、`~/.cache/stock_backtest/long/jp/<コード>.T_full.json`・`_div.json` に置く（あれば取り直さない）。

決まり（Fableの策9。優待はデータがないので配当だけ）:
- 配当の権利落ち日 E（Yahooの配当の日付）ごとに、E の30取引日前の引けで買い、E の3取引日前（権利付き最終日の2日前）の引けで売る。
- 毎月、その月に権利落ち日がある銘柄のうち、買う日の直近1年の配当÷株価が高い5銘柄を同じ金額で買う。
- 次の月の買いが前の月の売りより先に来るので、資金を2つに分け（奇数月・偶数月）、それぞれ半分ずつ使う。使わない間は円の現金（0%）。
- 手数料 片道0.1%、税は年ごとに通算して20.315%。
比べる相手: 日経平均のETF（1321.T）を持ち続ける・同じ日に1321を買って同じ日に売る形。

使い方: python3 tools/fable_jp_dividend.py [--out FILE]
"""
import argparse
import bisect
import datetime as dt
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fable_data as fd  # noqa: E402

JP = os.path.expanduser("~/.cache/stock_backtest/long/jp/")
TAX, FEE = 0.20315, 0.001


def load_stock(code):
    sym = f"{code}.T"
    fd.L = JP
    if not fd.fetch(sym):
        return None
    rows = json.load(open(fd.path(sym)))
    dp = fd.path(sym).replace("_full.json", "_div.json")
    divs = json.load(open(dp)) if os.path.exists(dp) else {}
    return {"d": [r[0] for r in rows], "c": [r[4] for r in rows], "div": divs}


def metrics(curve, days):
    yrs = (dt.date.fromisoformat(days[-1]) - dt.date.fromisoformat(days[0])).days / 365.25
    pk = md = 0.0
    for v in curve:
        pk = max(pk, v)
        md = max(md, 1 - v / pk)
    return (curve[-1] / curve[0]) ** (1 / yrs) - 1, md


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--top", type=int, default=5)
    a = ap.parse_args()
    codes = json.load(open(os.path.expanduser("~/.cache/stock_backtest/long/index/n225_codes.json")))
    S = {}
    for c in codes:
        s = load_stock(c)
        if s and len(s["d"]) > 300:
            S[c] = s
    fd.L = os.path.expanduser("~/.cache/stock_backtest/long/index/")
    # 比べる相手は日経平均（^N225、配当なしの指数）。1321.T は分割の調整が入っていない日があり使わない
    etf = json.load(open(fd.path("^N225")))
    cal = [r[0] for r in etf if r[0] >= "2014-01-01"]
    etf_c = {r[0]: r[4] for r in etf if r[4] and r[4] > 0}
    etf_adj = dict(etf_c)
    # 売買の候補: (買う日, 売る日, コード, 利回り, 月のキー)
    cands = []
    for c, s in S.items():
        pos = {d: k for k, d in enumerate(s["d"])}
        dd = sorted(s["div"])
        for e in dd:
            if e < "2015-01-01":
                continue
            k = bisect.bisect_left(s["d"], e)
            if k >= len(s["d"]) or k < 31:
                continue
            kb, ks = k - 30, k - 3
            bd = s["d"][kb]
            px = s["c"][kb]
            y0 = (dt.date.fromisoformat(bd) - dt.timedelta(days=365)).isoformat()
            ann = sum(v for d_, v in s["div"].items() if y0 < d_ <= bd)
            if px <= 0 or ann <= 0:
                continue
            cands.append((bd, s["d"][ks], c, ann / px, e[:7], s["c"][ks] / px - 1))
    by_m = {}
    for x in cands:
        by_m.setdefault(x[4], []).append(x)
    picks = []
    for m, xs in sorted(by_m.items()):
        xs.sort(key=lambda x: -x[3])
        top = xs[:a.top]
        if len(top) < a.top:
            continue
        picks.append((m, top))
    # 2つの資金（奇数月・偶数月）で、各月の5銘柄の平均の損益を順につなぐ
    trades = []
    for m, top in picks:
        r = sum(x[5] for x in top) / len(top)
        r_net = (1 - FEE) * (1 + r) * (1 - FEE) - 1
        bd = min(x[0] for x in top)
        sd = max(x[1] for x in top)
        er = etf_c.get(sd, None)
        eb = etf_c.get(bd, None)
        etf_r = (er / eb - 1) if er and eb else None
        trades.append((m, bd, sd, r_net, etf_r, [x[2] for x in top]))
    # 毎日の資金（円）: 2つの半分の資金。月ごとの売買は買う日〜売る日の間、損益を直線ではなく売る日にまとめて反映
    days = [d for d in cal if d >= "2015-01-05"]
    half = {0: 0.5, 1: 0.5}
    real = {0: 0.0, 1: 0.0}
    ev = {}
    for t in trades:
        ev.setdefault(t[2], []).append(t)
    curve, year = [], days[0][:4]
    for d in days:
        if d[:4] != year:
            tot = sum(v for v in real.values())
            if tot > 0:
                # 年の税は2つの資金の損益を通算
                for i in (0, 1):
                    half[i] -= TAX * tot / 2
            real = {0: 0.0, 1: 0.0}
            year = d[:4]
        for t in ev.get(d, []):
            i = int(t[0][5:7]) % 2
            g = half[i] * t[3]
            half[i] += g
            real[i] += g
        curve.append(half[0] + half[1])
    etf_curve = [etf_adj[d] for d in days if d in etf_adj]
    edays = [d for d in days if d in etf_adj]
    out = []
    w = out.append
    w(f"- 比べる相手は日経平均（^N225）。\n- 銘柄: 日経225の今の構成銘柄 {len(S)}（Yahooで取れたもの）。配当の権利落ち日が2015年以降の売買の候補 {len(cands)}、上位{a.top}銘柄がそろった月 {len(trades)}")
    cg, md = metrics(curve, days)
    eg, em = metrics(etf_curve, edays)
    w(f"\n| 形（円） | 年率 | 最大下落率 |\n|---|---|---|\n| 策9 権利取りの前の先回り（資金の半分ずつ、税・手数料込み） | {cg:.1%} | {md:.0%} |"
      f"\n| （比べる）日経平均（指数、配当なし・税なし）を持ち続ける | {eg:.1%} | {em:.0%} |")
    rs = [t[3] for t in trades]
    es = [t[4] for t in trades if t[4] is not None]
    diff = [t[3] - t[4] for t in trades if t[4] is not None]
    w(f"\n- 1回（5銘柄・約27取引日）の平均 {sum(rs) / len(rs):+.2%}、勝った割合 {sum(1 for x in rs if x > 0) / len(rs):.0%}。"
      f"同じ日に日経平均を持った場合 {sum(es) / len(es):+.2%}。差の平均 {sum(diff) / len(diff):+.2%}（差がプラスの割合 {sum(1 for x in diff if x > 0) / len(diff):.0%}）")
    # 月ごと
    bym = {}
    for t in trades:
        bym.setdefault(t[0][5:7], []).append((t[3], t[4]))
    w("\n| 権利落ちの月 | 回数 | 1回の平均 | 同じ日の日経平均 | 差 |\n|---|---|---|---|---|")
    for m in sorted(bym):
        xs = bym[m]
        r_ = sum(x[0] for x in xs) / len(xs)
        e_ = [x[1] for x in xs if x[1] is not None]
        e_ = sum(e_) / len(e_) if e_ else float("nan")
        w(f"| {m}月 | {len(xs)} | {r_:+.2%} | {e_:+.2%} | {r_ - e_:+.2%} |")
    # 前半・後半
    for lo, hi in (("2015", "2020"), ("2021", "2026")):
        xs = [t for t in trades if lo <= t[0][:4] <= hi and t[4] is not None]
        if xs:
            w(f"- {lo}〜{hi}年: 1回の平均 {sum(t[3] for t in xs) / len(xs):+.2%}、日経平均 {sum(t[4] for t in xs) / len(xs):+.2%}（{len(xs)}回）")
    json.dump({"days": days, "curve": curve}, open(os.path.expanduser("~/.cache/stock_backtest/results/fable_jp.json"), "w"))
    text = "\n".join(out) + "\n"
    if a.out:
        open(a.out, "w").write(text)
    print(text)


if __name__ == "__main__":
    main()
