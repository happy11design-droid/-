#!/usr/bin/env python3
"""M2 の1段目 メタラベリング（Fableの提案 `新分析ツール/Fableの提案_確かめ方_2026-11-15.md` 2節、2026-11-15）

今の4つのルールの合図（`results/combo_feat_*.json`、src="今"）に、合図の日の引けまでに分かる8個の数値を付け、
「その合図が損で終わる（ret＜0）確率」をロジスティック回帰（L2 の強さ1.0に固定）で出す。資金の計算はしない。
  1 順張りか（ミネルヴィニ・新高値V2）  2 ATR(14)÷終値  3 終値÷直近20取引日の高値−1  4 下向き（終値＜50日線、50日線＜10取引日前）
  5 過熱（終値＞+2σかつRSI(14)＞70）  6 次の決算まで5営業日以内  7 自社の決算で下げた（手1の O1、境目 −5%）  8 VIXの対数
  2・3・8 は決める期間の平均と標準偏差でそろえる。
分け方: 決める期間＝2015-01-02〜2020-12-31 に売り終わった売買。確かめる期間＝2021年の最初の取引日から40取引日たった日より後の合図（エンバーゴ）。
閾値: 決める期間の点数の上位 20%・30%・40%（損で終わる確率が高い方）を「元の株にする合図」とする。
目安（1段目）: 確かめる期間・両方の監視銘柄で AUC≧0.55、元の株にする合図の損の割合がそれ以外より8pt以上高い、
  同じ月の中で点数を入れ替えたでたらめ（1,000回）の上位5%。あわせて、元の株にする合図の1回平均と、手4の1つずつの条件（過熱・決算5営業日・下向き）と比べる。

使い方: python3 tools/meta_label_check.py [--out FILE]
"""
import argparse
import bisect
import json
import math
import os
import random
import statistics as st
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fable_data as fd  # noqa: E402
from backtest_lib import DEFAULT_CACHE, load_prices  # noqa: E402

C = DEFAULT_CACHE


def rsi14(c):
    out = [None] * len(c)
    n = 14
    if len(c) <= n:
        return out
    g = [max(c[k] - c[k - 1], 0) for k in range(1, len(c))]
    d = [max(c[k - 1] - c[k], 0) for k in range(1, len(c))]
    ag, ad = sum(g[:n]) / n, sum(d[:n]) / n
    for k in range(n, len(c)):
        if k > n:
            ag = (ag * (n - 1) + g[k - 1]) / n
            ad = (ad * (n - 1) + d[k - 1]) / n
        out[k] = 100.0 if ad == 0 else 100 - 100 / (1 + ag / ad)
    return out


def auc(y, s):
    y = np.asarray(y)
    s = np.asarray(s)
    order = np.argsort(s)
    r = np.empty(len(s))
    r[order] = np.arange(1, len(s) + 1)
    # 同点の平均順位
    _, inv, cnt = np.unique(s, return_inverse=True, return_counts=True)
    sums = np.bincount(inv, r)
    r = sums[inv] / cnt[inv]
    n1 = y.sum()
    n0 = len(y) - n1
    return (r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0) if n1 and n0 else float("nan")


def logit_fit(X, y, l2=1.0, it=500):
    w = np.zeros(X.shape[1])
    for _ in range(it):   # ニュートン法（L2、切片は罰しない）
        p = 1 / (1 + np.exp(-X @ w))
        g = X.T @ (p - y) + l2 * np.r_[0, w[1:]]
        H = (X.T * (p * (1 - p))) @ X + l2 * np.diag(np.r_[0, np.ones(len(w) - 1)])
        step = np.linalg.solve(H, g)
        w -= step
        if np.abs(step).max() < 1e-8:
            break
    return w


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--perm", type=int, default=1000)
    ap.add_argument("--dump", help="2段目用: 毎年作り直した点数で元の株にする合図の一覧を書き出す json")
    a = ap.parse_args()
    import drop_cause_check as dc   # 手1の区分の作り方をそのまま使う（O1 だけ）
    earn = json.load(open(os.path.join(C, "earnings.json")))
    fd.L = os.path.join(C, "long/index/")
    vix = {d: v[3] for d, v in fd.load("^VIX").items()}
    vix_d = sorted(vix)
    PX = {}

    def feats(sym, sd):
        if sym not in PX:
            p = load_prices(C, sym)
            if not p:
                PX[sym] = None
            else:
                c, h, l = p["c"], p["h"], p["l"]
                n = len(c)
                tr = [h[0] - l[0]] + [max(h[k] - l[k], abs(h[k] - c[k - 1]), abs(l[k] - c[k - 1])) for k in range(1, n)]
                atr = [None] * n
                s_ = 0.0
                for k in range(n):
                    s_ += tr[k]
                    if k >= 14:
                        s_ -= tr[k - 14]
                    if k >= 13:
                        atr[k] = s_ / 14
                ma50 = [None] * n
                s_ = 0.0
                for k in range(n):
                    s_ += c[k]
                    if k >= 50:
                        s_ -= c[k - 50]
                    if k >= 49:
                        ma50[k] = s_ / 50
                bb = [None] * n
                for k in range(19, n):
                    w_ = c[k - 19:k + 1]
                    m_ = sum(w_) / 20
                    bb[k] = m_ + 2 * math.sqrt(sum((x - m_) ** 2 for x in w_) / 20)
                ek = []
                for day, _tm in earn.get(sym, []):
                    k_ = bisect.bisect_left(p["date"], day)
                    ek.append(k_)
                PX[sym] = dict(date=p["date"], pos={d: k for k, d in enumerate(p["date"])}, c=c, h=h, atr=atr, ma50=ma50, bb=bb, rsi=rsi14(c), ek=sorted(ek))
        P = PX[sym]
        if not P or sd not in P["pos"]:
            return None
        i = P["pos"][sd]
        if i < 60 or P["atr"][i] is None or P["ma50"][i - 10] is None or P["bb"][i] is None:
            return None
        c = P["c"]
        hi20 = max(P["h"][i - 19:i + 1])
        j = bisect.bisect_right(P["ek"], i)
        soon = j < len(P["ek"]) and P["ek"][j] - i <= 5
        k_ = bisect.bisect_right(vix_d, sd) - 1
        return [P["atr"][i] / c[i], c[i] / hi20 - 1,
                1.0 if (c[i] < P["ma50"][i] and P["ma50"][i] < P["ma50"][i - 10]) else 0.0,
                1.0 if (P["rsi"][i] is not None and c[i] > P["bb"][i] and P["rsi"][i] > 70) else 0.0,
                1.0 if soon else 0.0, math.log(vix[vix_d[k_]])]

    out = []
    w = out.append
    allok = True
    DUMP = {}
    for wch, lab in (("87", "87銘柄"), ("free", "全業種（後知恵なし）")):
        rows = [r for r in json.load(open(os.path.join(C, f"results/combo_feat_{wch}.json"))) if r["src"] == "今" and r["sd"] >= "2015-01-01"]
        # O1（手1の区分）を、手1の道具の考え方で付ける: 押し目・急落の底だけ
        o1 = dc_o1(dc, rows, wch)
        X, y, R, D, rule = [], [], [], [], []
        for r, isO1 in zip(rows, o1):
            f = feats(r["sym"], r["sd"])
            if f is None:
                continue
            trend = 1.0 if r["rule"] in ("M", "V") else 0.0
            X.append([trend, f[0], f[1], f[2], f[3], f[4], 1.0 if isO1 else 0.0, f[5]])
            y.append(1.0 if r["ret"] < 0 else 0.0)
            R.append(r)
            D.append(r["sd"])
            rule.append(r["rule"])
        X, y = np.array(X), np.array(y)
        dates_all = sorted(set(D))
        k21 = next(k for k, d in enumerate(dates_all) if d >= "2021-01-01")
        emb = dates_all[min(len(dates_all) - 1, k21 + 40)]
        tr = np.array([r["out"] <= "2020-12-31" for r in R])
        va = np.array([d > emb for d in D])
        mu, sd_ = X[tr].mean(axis=0), X[tr].std(axis=0)
        Z = X.copy()
        for j in (1, 2, 7):
            Z[:, j] = (X[:, j] - mu[j]) / sd_[j]
        Z1 = np.c_[np.ones(len(Z)), Z]
        wts = logit_fit(Z1[tr], y[tr])
        sc = Z1 @ wts
        A = auc(y[va], sc[va])
        A_tr = auc(y[tr], sc[tr])
        # でたらめ: 同じ月の中で点数を入れ替える
        rnd = random.Random(0)
        months = {}
        vidx = np.flatnonzero(va)
        for i in vidx:
            months.setdefault(D[i][:7], []).append(i)
        ge = 0
        for _ in range(a.perm):
            s2 = sc.copy()
            for idx in months.values():
                v = list(sc[idx])
                rnd.shuffle(v)
                s2[idx] = v
            ge += auc(y[va], s2[va]) >= A
        w(f"\n## {lab}（合図 {len(R)}件。決める期間 {tr.sum()}件・確かめる期間 {va.sum()}件。エンバーゴの境 {emb}）\n")
        nm = ["順張りか", "値動きの大きさ", "下げの深さ", "下向き", "過熱", "決算の直前", "自社の決算で下げた", "VIXの対数"]
        w("- 係数（損で終わる向きがプラス）: " + "、".join(f"{n} {c:+.2f}" for n, c in zip(nm, wts[1:])) + f"、切片 {wts[0]:+.2f}")
        w(f"- 当てる力（AUC）: 決める期間 {A_tr:.3f}、**確かめる期間 {A:.3f}**。でたらめ（同じ月の中で点数を入れ替え、{a.perm}回）で本物以上だった割合 {ge / a.perm:.1%}")
        w("\n| 元の株にする合図 | 確かめる期間の件数 | 損の割合（元の株にする／それ以外） | 差 | 1回平均（元の株にする／それ以外） |")
        w("|---|---|---|---|---|")
        okw = A >= 0.55 and ge / a.perm <= 0.05
        best_meta = None
        for q in (0.2, 0.3, 0.4):
            th = np.quantile(sc[tr], 1 - q)
            m = va & (sc >= th)
            o = va & (sc < th)
            lr_m, lr_o = y[m].mean(), y[o].mean()
            rm, ro = np.mean([R[i]["ret"] for i in np.flatnonzero(m)]), np.mean([R[i]["ret"] for i in np.flatnonzero(o)])
            w(f"| 点数の上位{int(q * 100)}% | {m.sum()} | {lr_m:.0%}／{lr_o:.0%} | {(lr_m - lr_o) * 100:+.1f}pt | {rm:+.2%}／{ro:+.2%} |")
            if q == 0.3:
                best_meta = lr_m - lr_o
        for j, nm_ in ((4, "手4① 過熱"), (5, "手4② 決算の直前（5営業日）"), (3, "手4④ 下向き")):
            m = va & (X[:, j] == 1)
            o = va & (X[:, j] == 0)
            if m.sum() == 0:
                w(f"| {nm_}（1つの条件） | 0 | — | — | — |")
                continue
            lr_m, lr_o = y[m].mean(), y[o].mean()
            rm, ro = np.mean([R[i]["ret"] for i in np.flatnonzero(m)]), np.mean([R[i]["ret"] for i in np.flatnonzero(o)])
            w(f"| {nm_}（1つの条件） | {m.sum()} | {lr_m:.0%}／{lr_o:.0%} | {(lr_m - lr_o) * 100:+.1f}pt | {rm:+.2%}／{ro:+.2%} |")
        if a.dump:   # 2段目用: 毎年1月の最初の取引日に、その日より前に売り終わった売買の全部で点数を作り直し、その年の合図に当てる（2018年〜）
            for y_ in range(2018, 2027):
                y0 = f"{y_}-01-01"
                trn = np.array([r["out"] < y0 for r in R])
                use = np.array([d[:4] == str(y_) for d in D])
                if trn.sum() < 200 or use.sum() == 0:
                    continue
                mu2, sd2 = X[trn].mean(axis=0), X[trn].std(axis=0)
                Z2 = X.copy()
                for j in (1, 2, 7):
                    Z2[:, j] = (X[:, j] - mu2[j]) / sd2[j]
                Z21 = np.c_[np.ones(len(Z2)), Z2]
                w2 = logit_fit(Z21[trn], y[trn])
                s2_ = Z21 @ w2
                for q in (0.2, 0.3, 0.4):
                    th2 = np.quantile(s2_[trn], 1 - q)
                    for i in np.flatnonzero(use & (s2_ >= th2)):
                        DUMP.setdefault(wch, {}).setdefault(f"{int(q * 100)}", []).append(f"{R[i]['sym']}|{R[i]['sd']}|{R[i]['rule']}")
        okw = okw and best_meta is not None and best_meta >= 0.08
        allok = allok and okw
        w(f"\n- 1段目の目安（AUC≧0.55、損の割合の差≧+8pt（上位30%）、でたらめの上位5%）: {'満たす' if okw else '満たさない'}")
    w(f"\n**判定: {'1段目を通った（2段目へ）' if allok else '1段目を通らなかった'}**")
    if a.dump:
        json.dump(DUMP, open(a.dump, "w"))
        print("書き出し", a.dump, {k: {q: len(v) for q, v in d.items()} for k, d in DUMP.items()}, file=sys.stderr)
    text = "\n".join(out) + "\n"
    if a.out:
        open(a.out, "w", encoding="utf-8").write(text)
    print(text)


def dc_o1(dc, rows, wch):
    """手1の区分 O1（W＝合図の日までの5取引日に、自社の決算の反応日の候補で、グループより5%以上悪い日がある）。押し目・急落の底だけ"""
    industry = json.load(open(os.path.join(dc.ROOT, "新分析ツール", "業種一覧.json"), encoding="utf-8"))
    theme = dc.theme_groups()
    earn = json.load(open(os.path.join(C, "earnings.json")))
    need = {r["sym"] for r in rows if r["rule"] in ("B", "C")}
    grp = {}
    for s in need:
        g = ("T", theme[s]) if (wch == "87" and s in theme) else ("I", industry.get(s))
        grp[s] = g
    members = {}
    for s, g in list(industry.items()):
        members.setdefault(("I", g), []).append(s)
    for s, g in theme.items():
        members.setdefault(("T", g), []).append(s)
    gs = {g for g in grp.values() if g[1]}
    R = {}
    for g in gs:
        for s in members.get(g, []):
            if s not in R:
                p = load_prices(C, s)
                if p and len(p["c"]) > 30:
                    R[s] = (p["date"], {p["date"][k]: p["c"][k] / p["c"][k - 1] - 1 for k in range(1, len(p["c"])) if p["c"][k - 1]})
    sox = {r[0]: r[2] for r in json.load(open(os.path.join(C, "long/index/^SOX.json")))}
    sd_ = sorted(sox)
    sxr = {sd_[k]: sox[sd_[k]] / sox[sd_[k - 1]] - 1 for k in range(1, len(sd_))}
    out = []
    for r in rows:
        if r["rule"] not in ("B", "C") or r["sym"] not in R:
            out.append(False)
            continue
        s = r["sym"]
        ds, rr = R[s]
        k = bisect.bisect_right(ds, r["sd"]) - 1
        W = ds[max(0, k - 4):k + 1]
        g = grp.get(s)
        peers = [j for j in members.get(g, []) if j != s and j in R]
        ec = set()
        for day, _tm in earn.get(s, []):
            kk = bisect.bisect_left(ds, day)
            if kk < len(ds):
                ec.add(ds[kk])
                if kk + 1 < len(ds):
                    ec.add(ds[kk + 1])
        hit = False
        for d in W:
            if d not in ec or d not in rr:
                continue
            vals = [R[j][1][d] for j in peers if d in R[j][1]]
            gm = sum(vals) / len(vals) if len(vals) >= 3 else sxr.get(d, 0.0)
            if rr[d] - gm <= -0.05:
                hit = True
                break
        out.append(hit)
    return out


if __name__ == "__main__":
    main()
