#!/usr/bin/env python3
"""手3（Fableの提案 `新分析ツール/Fableの提案_未解決の課題_2026-11-15.md` 7節、2026-11-15）:
底の合図を「投げ売り→確認」の2段の組み合わせにして、ツールにとっての当たり（T1）・底への近さ（T2）・60日後（T3）で、
下げの局面の中のでたらめな日と比べる（資金の計算はしない）。

合図（指数 X = SOX・NDX・S&P500。VIX と市場の広がりは共通）:
  S1_X: X の RSI(14) ≦ 30
  S2  : VIX の終値 ≧ 30、または VIX÷VIX3M ≧ 1.0
  C1_X: フォロースルー・デー（SOX・NDX は今の合図 FTD_S・FTD_N。S&P500 は、60日の高値から−8%以下の後の安値から4日目以降に +1.25% 以上で引けた最初の日）
  C2  : 50日線より上の銘柄の割合が 15%以下から30%以上（今の P50）
  C3  : VIXのピークアウト（今の VIXPK）
  ① S1_X の日から25取引日以内の最初の C1_X
  ② S2 の日から25取引日以内の最初の C1_X
  ③ S1_X と S2 が10取引日以内に両方出た後、VIX÷VIX3M が 0.95 未満に戻った最初の日
  ④ C1_X・C2・C3 のうち2つ以上が10取引日以内にそろった日
  ⑤ SOXのRSI(14) 30→50（今の RSI_S）と VIXPK が15取引日以内に両方出た日（後の方）
  比べる相手: 今の17種類（`results/sig.json`）、上下判定の「いつ」の点数（市場の数値だけのロジスティック回帰、2015〜2020年で作り、上位10%の日。手8の(3)）
的: T1 その後20取引日の押し目・急落の底の合図（枠に関係なく全部、`combo_feat_*.json`）の1回平均と損切りの割合、T2 前後60取引日の X の最安値から±10取引日以内、T3 X の60取引日後の騰落率
でたらめ: X が60日の高値から−10%以下の日から、本物と同じ回数・同じ年ごとの回数で選ぶ（1,000回）。本物が上位何%か。
期間: 決める 2015〜2020年（T1 の良い順に並べ、上位2つ）、確かめる 2021〜2026年。2015年〜だけ（ユーザーの決定）。

使い方: python3 tools/bottom_combo_check.py [--out FILE] [--n 1000]
"""
import argparse
import bisect
import csv
import datetime as dt
import json
import math
import os
import random
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fable_data as fd  # noqa: E402

C = os.path.expanduser("~/.cache/stock_backtest/")


def rsi(x, n=14):
    out = [None] * len(x)
    if len(x) <= n:
        return out
    g = [max(x[k] - x[k - 1], 0) for k in range(1, len(x))]
    d = [max(x[k - 1] - x[k], 0) for k in range(1, len(x))]
    ag, ad = sum(g[:n]) / n, sum(d[:n]) / n
    for k in range(n, len(x)):
        if k > n:
            ag = (ag * (n - 1) + g[k - 1]) / n
            ad = (ad * (n - 1) + d[k - 1]) / n
        out[k] = 100.0 if ad == 0 else 100 - 100 / (1 + ag / ad)
    return out


def dedupe(ks, gap=20):
    out, last = [], -10 ** 9
    for k in sorted(ks):
        if k - last > gap:
            out.append(k)
        last = k if k - last > gap else last
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--n", type=int, default=1000)
    a = ap.parse_args()
    sig = json.load(open(C + "results/sig.json"))
    days = sig["days"]
    pos = {d: k for k, d in enumerate(days)}
    N = len(days)
    fd.L = C + "long/index/"
    ser = {}
    for nm, sym in (("SOX", "^SOX"), ("NDX", "^NDX"), ("SPX", "^GSPC"), ("VIX", "^VIX")):
        m = {d: v[3] for d, v in fd.load(sym).items()}
        last, xs = None, []
        for d in days:
            last = m.get(d, last)
            xs.append(last)
        ser[nm] = xs
    v3 = {}
    for r in csv.DictReader(open(C + "long/index/VIX3M_History.csv")):
        mo, da, yr = r["DATE"].split("/")
        v3[f"{yr}-{mo}-{da}"] = float(r["CLOSE"])
    last, V3 = None, []
    for d in days:
        last = v3.get(d, last)
        V3.append(last)
    ratio = [ser["VIX"][k] / V3[k] if V3[k] else None for k in range(N)]
    bottom = {k: {pos[d] for d in v if d in pos} for k, v in sig["bottom"].items()}

    # S&P500 のフォロースルー・デー（出来高なし）
    spx = ser["SPX"]
    ftd_spx = set()
    k = 60
    while k < N:
        hi = max(spx[k - 60:k + 1])
        if spx[k] <= 0.92 * hi:
            lowk = k
            j = k + 1
            while j < N and j - lowk <= 40:
                if spx[j] < spx[lowk]:
                    lowk = j
                elif j - lowk >= 3 and spx[j] / spx[j - 1] - 1 >= 0.0125:
                    ftd_spx.add(j)
                    break
                j += 1
            k = j + 1
        else:
            k += 1
    C1 = {"SOX": bottom["FTD_S"], "NDX": bottom["FTD_N"], "SPX": ftd_spx}
    S2 = {k for k in range(N) if (ser["VIX"][k] or 0) >= 30 or (ratio[k] is not None and ratio[k] >= 1.0)}
    sigs = {}
    for X in ("SOX", "NDX", "SPX"):
        r14 = rsi(ser[X], 14)
        S1 = {k for k in range(N) if r14[k] is not None and r14[k] <= 30}
        def first_after(starts, cset, win):
            out = set()
            for s0 in sorted(starts):
                for k in range(s0, min(N, s0 + win + 1)):
                    if k in cset:
                        out.add(k)
                        break
            return out
        sigs[f"①{X}"] = (X, first_after(S1, C1[X], 25))
        sigs[f"②{X}"] = (X, first_after(S2, C1[X], 25))
        both = set()
        for k in range(N):
            if k in S1 and any(j in S2 for j in range(k - 10, k + 11)):
                both.add(k)
        out3 = set()
        for s0 in sorted(both):
            for k in range(s0, min(N, s0 + 60)):
                if ratio[k] is not None and ratio[k] < 0.95:
                    out3.add(k)
                    break
        sigs[f"③{X}"] = (X, out3)
        out4 = set()
        for k in range(N):
            cnt = sum(1 for cs in (C1[X], bottom["P50"], bottom["VIXPK"]) if any(j in cs for j in range(k - 9, k + 1)))
            if cnt >= 2:
                out4.add(k)
        sigs[f"④{X}"] = (X, out4)
    out5 = set()
    for k in range(N):
        if k in bottom["RSI_S"] and any(j in bottom["VIXPK"] for j in range(k - 15, k + 1)):
            out5.add(k)
        if k in bottom["VIXPK"] and any(j in bottom["RSI_S"] for j in range(k - 15, k)):
            out5.add(k)
    sigs["⑤SOX"] = ("SOX", out5)
    for k_, v in bottom.items():
        sigs[f"今の合図 {k_}"] = ("NDX" if k_ == "FTD_N" else "SOX", v)
    # 手8の(3): 市場の数値だけの「いつ」の点数（ロジスティック回帰。2015〜2020年で作る。的は S&P500 の5日後の上げ下げ）
    try:
        import numpy as np
        spx_r = [0.0] + [spx[k] / spx[k - 1] - 1 for k in range(1, N)]
        r2 = rsi(spx, 2)
        ma150 = [None] * N
        for k in range(149, N):
            ma150[k] = sum(spx[k - 149:k + 1]) / 150
        X_, y_, ks_ = [], [], []
        for k in range(150, N - 5):
            X_.append([1.0, ser["VIX"][k] / 20, (r2[k] or 50) / 100, spx_r[k] * 10, spx[k] / ma150[k] - 1])
            y_.append(1.0 if spx[k + 5] > spx[k] else 0.0)
            ks_.append(k)
        X_, y_ = np.array(X_), np.array(y_)
        des = np.array([days[k] < "2021-01-01" for k in ks_])
        w = np.zeros(X_.shape[1])
        for _ in range(3000):
            p = 1 / (1 + np.exp(-X_[des] @ w))
            w += 0.5 * X_[des].T @ (y_[des] - p) / des.sum()
        sc = X_ @ w
        th = float(np.quantile(sc[des], 0.9))
        sigs["手8 「いつ」の点数（上位10%）"] = ("SPX", {k for k, v in zip(ks_, sc) if v >= th})
    except Exception as e:  # noqa: BLE001
        print("手8の点数は作れなかった", e, file=sys.stderr)

    # 的
    feats = {}
    for wch in ("87", "free"):
        rows = [r for r in json.load(open(C + f"results/combo_feat_{wch}.json")) if r["src"] == "今" and r["rule"] in ("B", "C") and r["sd"] in pos]
        byk = {}
        for r in rows:
            byk.setdefault(pos[r["sd"]], []).append(r)
        feats[wch] = byk

    def t1(ks, wch):
        rs = [r for k in ks for j in range(k + 1, min(N, k + 21)) for r in feats[wch].get(j, [])]
        if not rs:
            return None, None
        return st.mean(r["ret"] for r in rs), sum(1 for r in rs if r["stopped"]) / len(rs)

    def t2(ks, X):
        xs = ser[X]
        hit = 0
        for k in ks:
            lo, hi = max(0, k - 60), min(N, k + 61)
            b = min(range(lo, hi), key=lambda j: xs[j])
            hit += abs(b - k) <= 10
        return hit / len(ks) if ks else None

    def t3(ks, X):
        xs = ser[X]
        v = [xs[k + 60] / xs[k] - 1 for k in ks if k + 60 < N]
        return st.mean(v) if v else None

    pools = {}
    for X in ("SOX", "NDX", "SPX"):
        xs = ser[X]
        pools[X] = [k for k in range(60, N) if xs[k] <= 0.9 * max(xs[k - 60:k + 1])]

    def rand_pct(ks, X, fn, rnd):
        """でたらめ（同じ回数・同じ年ごと）の中で、本物以上だった割合"""
        real = fn(ks)
        if real is None:
            return None
        by_y = {}
        for k in ks:
            by_y.setdefault(days[k][:4], 0)
            by_y[days[k][:4]] += 1
        pool_y = {}
        for k in pools[X]:
            pool_y.setdefault(days[k][:4], []).append(k)
        ge = 0
        cnt = 0
        for _ in range(a.n):
            pick = []
            for y, c in by_y.items():
                src = pool_y.get(y) or pools[X]
                pick += [rnd.choice(src) for _ in range(c)]
            v = fn(pick)
            if v is None:
                continue
            cnt += 1
            ge += v >= real
        return ge / cnt if cnt else None

    rnd = random.Random(0)
    out = []
    w = out.append
    rows = []
    for name, (X, kset) in sigs.items():
        allk = dedupe([k for k in kset if days[k] >= "2015-01-01"])
        for per, lo, hi in (("2015〜2020年（決める）", "2015", "2021"), ("2021〜2026年（確かめる）", "2021", "2027")):
            ks = [k for k in allk if lo <= days[k][:4] < hi]
            if not ks:
                rows.append((name, per, 0, None, None, None, None, None, None, None))
                continue
            a87 = t1(ks, "87")
            afr = t1(ks, "free")
            p87 = rand_pct(ks, X, lambda kk: t1(kk, "87")[0], rnd)
            pfr = rand_pct(ks, X, lambda kk: t1(kk, "free")[0], rnd)
            rows.append((name, per, len(ks), a87, afr, p87, pfr, t2(ks, X), t3(ks, X), X))
    w("| 合図 | 期間 | 出来事の数 | T1 87銘柄（1回平均・損切り） | でたらめで本物以上 | T1 全業種 | でたらめで本物以上 | T2 底から±10日 | T3 60日後 |")
    w("|---|---|---|---|---|---|---|---|---|")
    f = lambda x: "—" if x is None else f"{x:+.2%}"  # noqa: E731
    for r in rows:
        name, per, n, a87, afr, p87, pfr, tt2, tt3, X = r
        if n == 0:
            w(f"| {name} | {per} | 0 | — | — | — | — | — | — |")
            continue
        w(f"| {name} | {per} | {n} | {f(a87[0])}・{'—' if a87[1] is None else f'{a87[1]:.0%}'} | {'—' if p87 is None else f'{p87:.0%}'} | "
          f"{f(afr[0])}・{'—' if afr[1] is None else f'{afr[1]:.0%}'} | {'—' if pfr is None else f'{pfr:.0%}'} | {'—' if tt2 is None else f'{tt2:.0%}'} | {f(tt3)} |")
    # 決める期間で T1（両方の監視銘柄の平均）の良い順に上位2つ（新しい合図①〜⑤だけ）→ 確かめる期間
    des = {r[0]: r for r in rows if r[1].startswith("2015") and r[2] >= 3 and r[0][0] in "①②③④⑤"}
    val = {r[0]: r for r in rows if r[1].startswith("2021")}
    rank = sorted(des.values(), key=lambda r: -((r[3][0] or 0) + (r[4][0] or 0)) / 2)[:2]
    w("\n## 決める期間（2015〜2020年）の T1 の上位2つを、確かめる期間（2021〜2026年）で見る\n")
    passed = []
    for r in rank:
        v = val.get(r[0])
        allk = dedupe([k for k in sigs[r[0]][1] if days[k] >= "2015-01-01"])
        ok = (v and v[2] > 0 and r[5] is not None and r[6] is not None and v[5] is not None and v[6] is not None
              and max(r[5], r[6]) <= 0.10 and max(v[5], v[6]) <= 0.10 and (v[7] or 0) >= 0.5 and (r[7] or 0) >= 0.5 and len(allk) >= 10)
        w(f"- {r[0]}: 決める期間 T1 {f(r[3][0])}・{f(r[4][0])}（でたらめで本物以上 {r[5]:.0%}・{r[6]:.0%}、T2 {r[7]:.0%}）／"
          + (f"確かめる期間 T1 {f(v[3][0])}・{f(v[4][0])}（でたらめで本物以上 {v[5]:.0%}・{v[6]:.0%}、T2 {v[7]:.0%}）" if v and v[2] else "確かめる期間 出来事なし")
          + f"／出来事の数 {len(allk)} → **{'通った' if ok else '通らなかった'}**")
        if ok:
            passed.append(r[0])
    w("\n通す目安（提案の7-4）: 両方の期間・両方の監視銘柄で T1 がでたらめの上位10%（でたらめで本物以上の割合が10%以下）、かつ T2 が50%以上、出来事の数が10回以上。")
    w(f"\n**判定: {'通った合図 ' + '、'.join(passed) if passed else '通った合図はなし'}**")
    text = "\n".join(out) + "\n"
    if a.out:
        open(a.out, "w", encoding="utf-8").write(text)
    print(text)


if __name__ == "__main__":
    main()
