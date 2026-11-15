#!/usr/bin/env python3
"""M1 選びすぎの確率（Fableの提案 `新分析ツール/Fableの提案_確かめ方_2026-11-15.md` 1節、2026-11-15）

1つの手で試した形の全部と今のルールを1つの組にして、「選んだ形が、別の半分の期間で今のルールを下回る確率」などを出す。
  eq   : OPT_EQDUMP（OPT_EQDUMP_ALL=1）の毎日の資金（形ごと・乱数30通り）。本命
  roll : OPT_ROLL の1年の区切り（形ごと・始める日ごと・乱数ごとの1年の損益）。毎日の資金がないとき

eq の手順（提案の1-1）:
  r_k(d) = 乱数30通りの資金の、日ごとの対数の騰落率の平均。x_k(d) = r_k(d) − r_今(d)
  2015年〜の取引日を続いた16個のブロックに分け、16個から8個を選ぶ全部の分け方（12,870通り）で、
  選ぶ側の x の合計が一番大きい形 k*（今のルールを除く）を選び、確かめる側で
   (a) k* の x の合計が0以下の割合 ＝ 選びすぎの確率（主に使う）
   (b) k* の順位が組（今のルールを含む）の中央より下の割合（参考。Bailey ほか 2014 の PBO）
   選ぶ側 → 確かめる側の差（年あたりのポイント）の平均
  t値: x の平均 ÷ その誤差（前後20日のつながりを直した Newey-West）。偶然の一番の t値（K個の形が全部偶然のときの一番の t値の平均と上位5%）と比べる。
  まとめての検定: 毎日の x を平均20日のブロックで並べ直して作り直し（3,000回）、t値の一番大きい値の分布の上位何%か（White 2000）。
   ハンセンの形（Hansen 2005）は、大きく負けている形を分布の中心に戻さない。
roll の手順: 260取引日おきの重ならない区切りだけを取り、取り始めをずらした組ごとに、区切りを半分ずつに分ける全部の分け方で同じ数字を出し、平均する。

使い方:
  python3 tools/pbo_check.py eq <json> [--ref 名前の一部] [--exclude 名前の一部] [--only 名前の一部]
  python3 tools/pbo_check.py roll <json> [--ref 名前の一部] [--exclude 名前の一部] [--only 名前の一部]
  --ref を省くと、「今のルール（傾き」で始まらない最初の形を今のルールとする。
"""
import argparse
import itertools
import json
import math
import sys

import numpy as np


def nw_t(x, lag=20):
    x = np.asarray(x, float)
    n = len(x)
    m = x.mean()
    e = x - m
    g0 = (e @ e) / n
    s = g0
    for l_ in range(1, min(lag, n - 1) + 1):
        s += 2 * (1 - l_ / (lag + 1)) * (e[l_:] @ e[:-l_]) / n
    se = math.sqrt(max(s, 1e-300) / n)
    return m / se, se


def chance_max_t(K, reps=20000, seed=0):
    if K <= 0:
        return None, None
    rng = np.random.default_rng(seed)
    mx = rng.standard_normal((reps, K)).max(axis=1)
    return float(mx.mean()), float(np.quantile(mx, 0.95))


def pick(names, ref, exclude, only):
    base = None
    if ref:
        base = next(n for n in names if ref in n)
    else:
        base = next(n for n in names if not n.startswith("今のルール（傾き"))
    cand = [n for n in names if n != base]
    if not ref:
        cand = [n for n in cand if not n.startswith("今のルール（傾き")]
    if exclude:
        cand = [n for n in cand if not any(e in n for e in exclude)]
    if only:
        cand = [n for n in cand if any(o in n for o in only)]
    return base, cand


def splits_stats(S, n_per_block, half):
    """S: 形×ブロックの x の合計（行0は今のルール＝0）。全部の分け方で (a)・(b)・選ぶ側→確かめる側（1日あたりの平均）"""
    K1, B = S.shape
    a = b = 0
    isd, osd = [], []
    cnt = 0
    for c in itertools.combinations(range(B), half):
        mask = np.zeros(B, bool)
        mask[list(c)] = True
        IS = S[:, mask].sum(axis=1)
        OS = S[:, ~mask].sum(axis=1)
        k = 1 + int(np.argmax(IS[1:]))
        cnt += 1
        a += OS[k] <= 0
        rk = (OS < OS[k]).sum() + 0.5 * ((OS == OS[k]).sum() - 1)
        b += rk / (K1 - 1) < 0.5
        isd.append(IS[k] / n_per_block[mask].sum())
        osd.append(OS[k] / n_per_block[~mask].sum())
    return a / cnt, b / cnt, float(np.mean(isd)), float(np.mean(osd)), cnt


def boot_max(X, block=20, reps=3000, seed=0, hansen=False):
    """X: 形×日の x。定常ブートストラップで t値の一番大きい値の分布を作り、本物以上の割合"""
    rng = np.random.default_rng(seed)
    K, n = X.shape
    mu = X.mean(axis=1)
    se = np.array([nw_t(X[k])[1] for k in range(K)])
    t_obs = (mu / se).max()
    if hansen:
        thr = -se * math.sqrt(2 * math.log(math.log(n)))
        cen = np.where(mu >= thr, mu, 0.0)
    else:
        cen = mu
    p_cont = 1.0 / block
    ge = 0
    jj = np.arange(n)
    for _ in range(reps):
        restart = rng.random(n) < p_cont
        restart[0] = True
        sp = np.flatnonzero(restart)
        seg = np.cumsum(restart) - 1
        st0 = rng.integers(n, size=len(sp))
        idx = (st0[seg] + (jj - sp[seg])) % n
        mb = X[:, idx].mean(axis=1)
        tb = ((mb - cen) / se).max() if hansen else ((mb - mu) / se).max()
        ge += tb >= t_obs
    return ge / reps, float(t_obs)


def run_eq(a):
    d = json.load(open(a.path))
    names = list(d)
    base, cand = pick(names, a.ref, a.exclude, a.only)
    days = d[base]["days"]

    def rmean(n):
        eqs = np.array([[v if v is not None else np.nan for v in s] for s in d[n]["eq"]], float)
        for s in eqs:   # 前の値で埋める
            for j in range(1, len(s)):
                if not np.isfinite(s[j]):
                    s[j] = s[j - 1]
        lr = np.diff(np.log(eqs), axis=1)
        return np.nanmean(lr, axis=0)
    r0 = rmean(base)
    X = np.array([rmean(n) - r0 for n in cand])
    n = X.shape[1]
    blocks = np.array_split(np.arange(n), 16)
    nb = np.array([len(b) for b in blocks])
    S = np.vstack([np.zeros(16), np.array([[X[k, b].sum() for b in blocks] for k in range(len(cand))])])
    pa, pb, isd, osd, cnt = splits_stats(S, nb, 8)
    K = len(cand)
    cm, c95 = chance_max_t(K)
    ts = [nw_t(X[k])[0] for k in range(K)]
    out = []
    w = out.append
    w(f"- ファイル: `{a.path.split('/')[-1]}`、今のルール: {base[:80]}")
    w(f"- 組の形の数 K={K}（今のルールを除く）、日数 {n}、ブロック16個・分け方 {cnt}通り")
    w(f"- **選びすぎの確率（選んだ形が別の半分で今のルールを下回る）: {pa:.1%}**、参考の PBO（順位が中央より下）: {pb:.1%}")
    w(f"- 選んだ形の今のルールとの差（年あたり）: 選ぶ側 {isd * 252 * 100:+.1f}pt → 確かめる側 {osd * 252 * 100:+.1f}pt")
    w(f"- 偶然の一番の t値（K={K}）: 平均 {cm:.2f}、上位5% {c95:.2f}")
    if K <= 60 and not a.noboot:
        pw, tmax = boot_max(X, reps=a.reps)
        ph, _ = boot_max(X, reps=a.reps, hansen=True)
        w(f"- まとめての検定（一番良い形の t値 {tmax:.2f}）: ホワイトの形 p={pw:.3f}、ハンセンの形 p={ph:.3f}")
    w("\n| 形 | 毎日の差の t値 | 年あたりの差 |\n|---|---|---|")
    for k in np.argsort(ts)[::-1]:
        w(f"| {cand[k].split('＋')[-1][:70]} | {ts[k]:.2f} | {X[k].mean() * 252 * 100:+.1f}pt |")
    return "\n".join(out)


def run_roll(a):
    d = json.load(open(a.path))
    F, days, win = d["forms"], d["days"], d["win"]
    pos = {x: k for k, x in enumerate(days)}
    names = list(F)
    base, cand = pick(names, a.ref, a.exclude, a.only)
    starts = sorted(s for s in F[base] if pos[s] + win <= len(days) - 1)
    if len(starts) < 2:
        return "区切りが足りない"
    step = pos[starts[1]] - pos[starts[0]]
    m = max(1, round(260 / step))
    K = len(cand)
    res = []
    tsum = np.zeros(K)
    for off in range(m):
        st_ = starts[off::m][:a.nwin] if a.nwin else starts[off::m]   # 提案の1-1: 取り方ごとに10個（5個ずつに分ける252通り）
        if len(st_) < 4:
            continue
        b0 = np.array([np.mean([r[0] for r in F[base][s]]) for s in st_])
        M = np.array([[np.mean([r[0] for r in F[nm][s]]) for s in st_] for nm in cand]) - b0
        for k in range(K):
            x = M[k]
            sd = x.std(ddof=1)
            tsum[k] += (x.mean() / (sd / math.sqrt(len(x))) if sd > 0 else 0.0)
        S = np.vstack([np.zeros(len(st_)), M])
        half = len(st_) // 2
        pa, pb, isd, osd, cnt = splits_stats(S, np.ones(len(st_)), half)
        res.append((pa, pb, isd, osd, len(st_)))
    if not res:
        return "区切りが足りない"
    tmean = tsum / len(res)
    cm, c95 = chance_max_t(K)
    out = []
    w = out.append
    w(f"- ファイル: `{a.path.split('/')[-1]}`、今のルール: {base[:80]}")
    w(f"- 組の形の数 K={K}、区切りの間隔 {step}取引日、重ならない区切りの取り方 {len(res)}通り（1つあたり {res[0][4]}個前後）")
    w(f"- **選びすぎの確率: {np.mean([r[0] for r in res]):.1%}**（取り方ごとに {min(r[0] for r in res):.0%}〜{max(r[0] for r in res):.0%}）、参考の PBO: {np.mean([r[1] for r in res]):.1%}")
    w(f"- 選んだ形の今のルールとの差（1年の損益）: 選ぶ側 {np.mean([r[2] for r in res]) * 100:+.1f}pt → 確かめる側 {np.mean([r[3] for r in res]) * 100:+.1f}pt")
    w(f"- 偶然の一番の t値（K={K}）: 平均 {cm:.2f}、上位5% {c95:.2f}")
    if K <= 40:
        w("\n| 形 | 重ならない区切りの t値（取り方の平均） |\n|---|---|")
        for k in np.argsort(tmean)[::-1]:
            w(f"| {cand[k].split('＋')[-1][:70]} | {tmean[k]:.2f} |")
    else:
        top = np.argsort(tmean)[::-1][:5]
        w("- t値の上位5つ: " + "、".join(f"{cand[k].split('＋')[-1][:40]} {tmean[k]:.2f}" for k in top))
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", choices=("eq", "roll"))
    ap.add_argument("path")
    ap.add_argument("--ref")
    ap.add_argument("--exclude", action="append")
    ap.add_argument("--only", action="append")
    ap.add_argument("--reps", type=int, default=3000)
    ap.add_argument("--noboot", action="store_true")
    ap.add_argument("--nwin", type=int, default=10, help="roll: 重ならない区切りの数（取り方ごと）。0なら全部")
    a = ap.parse_args()
    print(run_eq(a) if a.kind == "eq" else run_roll(a))


if __name__ == "__main__":
    main()
