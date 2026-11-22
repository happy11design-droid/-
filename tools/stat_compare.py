#!/usr/bin/env python3
"""形の比べ方を統計で確かめる（2026-11-22 ユーザーの指示「2014年以前のデータは参考程度。何か数値的な統計によって検証ができれば良い」）。

backtest_retest.py の毎日の資金（OPT_EQDUMP・OPT_EQDUMP_ALL=1、形ごと・乱数30通り、2015年〜）から:
  1. 通しの成績（年率・最大下落率・2015〜2021年・2022年〜、乱数の中央値）と、今回の期間（OPT_EQDUMP_START から空の枠で始めた資金）
  2. 口を混ぜる形（87銘柄の口と全業種の口を割合で持ち、毎年1月の最初の取引日に割合へ戻す。乱数の番号が同じ資金どうし）
  3. 1年の区切り（250取引日を10取引日ごと）: 1年の損益の平均・悪い5%、1年の中の最大下落率の悪い5%
  4. ブロック・ブートストラップ（Politis–Romano の定常ブートストラップ、平均20日のブロック、3,000回）: 乱数の平均の毎日の対数の騰落率を、
     今のルールと同じ日の組で並べ直し、「年率の差」「最大下落率の差」の分布から、今のルールより良い確率と95%の範囲を出す
  5. 合成した長い下げ: 2015年〜のうち SOX が200日線の下だった日（下げの局面）から、20日続けてその局面だった区間を
     ランダムにつないで250取引日（約1年）の道を3,000本作り、形ごとの損益と最大下落率の分布を出す（同じ日を全部の形に使う）
  6. 選びすぎの確率（Fable の M1、tools/pbo_check.py）のための json を書き出す（混ぜる形も1つの形として入れる）

使い方: tools/stat_compare.py --eq87 FILE --eqall FILE --out FILE [--pbo-json FILE]
数値の事実だけで、Claudeの売買判断は含まない。
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backtest_lib import DEFAULT_CACHE, load_prices, sma

RNG = np.random.default_rng(20261122)


def ffill(a):
    a = np.array([[v if v is not None else np.nan for v in s] for s in a], float)
    for s in a:
        for j in range(1, len(s)):
            if not np.isfinite(s[j]):
                s[j] = s[j - 1]
        first = np.argmax(np.isfinite(s))
        s[:first] = s[first] if np.isfinite(s[first]) else 1.0
    return a


def mix(eqA, eqB, w, days):
    """乱数ごとに、口Aを w・口Bを 1−w で持ち、毎年1月の最初の取引日に割合へ戻す"""
    out = np.empty_like(eqA)
    for q in range(eqA.shape[0]):
        a, b = eqA[q], eqB[q]
        va, vb = w, 1 - w
        out[q, 0] = 1.0
        for j in range(1, len(days)):
            va *= a[j] / a[j - 1]
            vb *= b[j] / b[j - 1]
            if days[j][:4] != days[j - 1][:4]:
                t = va + vb
                va, vb = w * t, (1 - w) * t
            out[q, j] = va + vb
    return out


def mix_sw(eqA, eqB, target, days, j0=0):
    """切り替えて混ぜる形（2026-11-22 ユーザーの指示「全て検証して」）: target[j] はその日の引けで決まる口Aの割合。
    前の日の引けで決まった割合が変わった日（1日遅れ）と、毎年1月の最初の取引日に、その割合へ資金を移す（口の間で資金を移す近似。株を売る手間は入れない）"""
    out = np.full_like(eqA, np.nan)
    for q in range(eqA.shape[0]):
        a, b = eqA[q], eqB[q]
        w = target[j0]
        va, vb = w, 1 - w
        out[q, j0] = 1.0
        for j in range(j0 + 1, len(days)):
            va *= a[j] / a[j - 1]
            vb *= b[j] / b[j - 1]
            tw = target[j - 1]
            if tw != w or (days[j][:4] != days[j - 1][:4] and 0 < tw < 1):
                t = va + vb
                va, vb, w = tw * t, (1 - tw) * t, tw
            out[q, j] = va + vb
    return out


def slot_use(trades, days):
    """売買の記録（乱数10通り）から、年ごとの枠の使い方（87銘柄・テーマの外・空き）の割合と、1年の売買の数（2026-11-22 ユーザーの質問への答えの数値）"""
    di = {d: i for i, d in enumerate(days)}
    yrs = sorted({d[:4] for d in days})
    nd = {y: sum(1 for d in days if d[:4] == y) for y in yrs}
    res = {y: [0.0, 0.0, 0] for y in yrs}
    nseed = max(1, len(trades))
    cnt = {y: [0, 0] for y in yrs}
    for tl in trades:
        for x in tl:
            i0 = di.get(x[0])
            i1 = di.get(x[1]) if x[1] else len(days) - 1
            if i0 is None or i1 is None:
                continue
            sz = x[7] if len(x) > 7 and x[7] else 1.0
            out_ = len(x) > 6 and x[6] == 1
            cnt[x[0][:4]][1 if out_ else 0] += 1
            for j in range(i0, max(i0 + 1, i1)):
                res[days[j][:4]][1 if out_ else 0] += sz
    tab = {}
    for y in yrs:
        tot = 4 * nd[y] * nseed
        a87, aout = res[y][0] / tot, res[y][1] / tot
        tab[y] = (a87, aout, max(0.0, 1 - a87 - aout), cnt[y][0] / nseed, cnt[y][1] / nseed)
    return tab


def mix_live(lA, lB, w):
    out = np.empty_like(lA)
    for q in range(lA.shape[0]):
        out[q] = w * lA[q] / lA[q][0] + (1 - w) * lB[q] / lB[q][0]
    return out


def mdd(x):
    pk = np.maximum.accumulate(x)
    return float(np.max(1 - x / pk))


def cagr(x, n_days):
    return (x[-1] / x[0]) ** (252 / max(1, n_days)) - 1


def stats(eq, days):
    n = len(days)
    i21 = max(k for k, d in enumerate(days) if d <= "2021-12-31")
    cg = [cagr(s, n - 1) for s in eq]
    c1 = [cagr(s[:i21 + 1], i21) for s in eq]
    c2 = [cagr(s[i21:], n - 1 - i21) for s in eq]
    md = [mdd(s) for s in eq]
    # 1年の区切り（続けた資金から250取引日を10取引日ごと）
    r1, m1 = [], []
    for k in range(0, n - 250, 10):
        seg = eq[:, k:k + 251]
        r1.append(float(np.median(seg[:, -1] / seg[:, 0] - 1)))
        m1.append(float(np.median([mdd(s) for s in seg])))
    return {"cagr": float(np.median(cg)), "c1": float(np.median(c1)), "c2": float(np.median(c2)), "mdd": float(np.median(md)),
            "mdd_worst": float(np.max(md)), "r1": np.array(r1), "m1": np.array(m1)}


def mean_logret(eq):
    return np.nanmean(np.diff(np.log(eq), axis=1), axis=0)


def stationary_idx(n, mean_block=20):
    idx = np.empty(n, int)
    j = RNG.integers(n)
    p = 1.0 / mean_block
    for i in range(n):
        idx[i] = j
        j = RNG.integers(n) if RNG.random() < p else (j + 1) % n
    return idx


def path_mdd(lr):
    x = np.exp(np.cumsum(lr))
    x = np.concatenate([[1.0], x])
    return mdd(x)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--eq87", required=True)
    ap.add_argument("--eqall", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--pbo-json")
    ap.add_argument("--reps", type=int, default=3000)
    a = ap.parse_args()
    d87, dall = json.load(open(a.eq87)), json.load(open(a.eqall))
    n87 = [k for k in d87 if not k.startswith(("今のルール（傾き", "_"))]   # 古い今のルール（傾きの小さい順）と、日の集合（_regs・_breadth）は使わない
    nall = [k for k in dall if not k.startswith(("今のルール（傾き", "_"))]
    days = d87[n87[0]]["days"]
    assert days == dall[nall[0]]["days"]
    short = lambda nm: (nm.replace("買う順番: RSの高い順＋遅らせて買う 急落の底 合図の日の終値の2%下の指値（3日間）", "今のルール")
                        .replace("＋テーマの外の強い銘柄で空き枠を埋める（OPT_OUTSIDE=1、毎朝のツールと同じ）", "").replace("強さの条件: ", "")
                        .replace("（150日線が上向きでRS≧90を満たさない）", "").replace("87銘柄は150日線が上向きでRS≧90の銘柄だけ買う", "強さの条件")
                        .replace("底の後40日は2倍ETF: SOXが上向きの30週線の上（ワインスタインのステージ2）", "SOXのステージ2の後40日は2倍ETF")
                        .replace("待っている現金をQQQに置く", "待っている現金をQQQ"))
    F = {}
    for nm in n87:
        F["87銘柄: " + short(nm)] = (ffill(d87[nm]["eq"]), ffill(d87[nm]["live"]))
    for nm in nall:
        F["全業種: " + short(nm)] = (ffill(dall[nm]["eq"]), ffill(dall[nm]["live"]))
    base87, baseall = "87銘柄: " + short(n87[0]), "全業種: " + short(nall[0])
    strong87 = next((k for k in F if k.startswith("87銘柄") and "RS≧90の銘柄だけ" in k and "200日線" not in k), None)
    for w, lab in ((0.5, "混ぜる: 87銘柄の口50%＋全業種の口50%（毎年1月に戻す）"), (0.75, "混ぜる: 87銘柄の口75%＋全業種の口25%（毎年1月に戻す）")):
        F[lab] = (mix(F[base87][0], F[baseall][0], w, days), mix_live(F[base87][1], F[baseall][1], w))
    if strong87:
        F["混ぜる: 強さの条件の87銘柄の口50%＋全業種の口50%"] = (mix(F[strong87][0], F[baseall][0], 0.5, days), mix_live(F[strong87][1], F[baseall][1], 0.5))
    # 2026-11-22: 待っている現金をQQQに置く口どうしを混ぜる形と、87銘柄の割合で守りに入ったら全業種の口へ資金を移す形
    q87 = next((k for k in F if k.startswith("87銘柄") and k.endswith("強さの条件＋待っている現金をQQQ")), None)
    qall = next((k for k in F if k.startswith("全業種") and k.endswith("今のルール＋待っている現金をQQQ")), None)
    if q87 and qall:
        F["混ぜる: 強さの条件＋QQQの87銘柄の口50%＋全業種＋QQQの口50%"] = (mix(F[q87][0], F[qall][0], 0.5, days), mix_live(F[q87][1], F[qall][1], 0.5))
    REGS = d87.get("_regs", {})
    live_from0 = next(i for i, x in enumerate(d87[n87[0]]["live"][0]) if x is not None)
    for rg, rlab in (("b50h", "50日線より上が30%未満で守り・50%以上で戻す"), ("b200h", "200日線より上が40%未満で守り・55%以上で戻す")):
        if rg not in REGS:
            continue
        rs_ = set(REGS[rg])
        for a_, alab in ((base87, "今のルールの87銘柄の口"), (strong87, "強さの条件の87銘柄の口")):
            if not a_:
                continue
            for wd, wlab in ((0.5, "半分"), (0.0, "全部")):
                tg = np.array([wd if d in rs_ else 1.0 for d in days])
                F[f"切り替えて混ぜる: {alab}、87銘柄の{rlab}間は{wlab}を全業種の口へ"] = (
                    mix_sw(F[a_][0], F[baseall][0], tg, days), mix_sw(F[a_][1], F[baseall][1], tg, days, live_from0)[:, :] )
    S = {k: stats(v[0], days) for k, v in F.items()}
    live_from = next(i for i, x in enumerate(d87[n87[0]]["live"][0]) if x is not None)
    L = []
    w_ = L.append
    w_("# 形の比べ方を統計で確かめる（2015年〜、毎朝のツールと同じ形）\n")
    w_(f"- 期間 {days[0]}〜{days[-1]}、乱数30通り。今回の期間は {days[live_from]} の引けに空の枠から始めた資金。税・手数料は今までのバックテストと同じ（片道0.1%、税なし）。")
    w_("- 混ぜる形は、2つの口を別々の資金として持ち、毎年1月の最初の取引日に決めた割合へ戻す（Fable の案1と同じ）。\n")
    w_("## 1. 通しの成績と1年の区切り\n")
    w_("| 形 | 年率 | 最大下落率（乱数の最悪） | 2015〜2021年 | 2022年〜 | 1年の損益の平均 | 1年の損益の悪い5% | 1年の中の下落率の悪い5% | 今回の期間 |")
    w_("|---|---|---|---|---|---|---|---|---|")
    for k, s in S.items():
        lv = F[k][1][:, -1] / F[k][1][:, live_from] - 1
        w_(f"| {k} | {s['cagr'] * 100:.1f}% | {s['mdd'] * 100:.0f}%（{s['mdd_worst'] * 100:.0f}%） | {s['c1'] * 100:.1f}% | {s['c2'] * 100:.1f}% | "
           f"{s['r1'].mean() * 100:+.1f}% | {np.quantile(s['r1'], 0.05) * 100:+.1f}% | {np.quantile(s['m1'], 0.95) * 100:.0f}% | {np.median(lv) * 100:+.1f}% |")

    # 4. ブロック・ブートストラップ
    LR = {k: mean_logret(v[0]) for k, v in F.items()}
    n = len(LR[base87])
    w_("\n## 2. ブロック・ブートストラップ（今のルール〔87銘柄〕と同じ日の組で並べ直す、平均20日のブロック、"
       f"{a.reps}回）\n")
    w_("「良い確率」は、並べ直した道のうち、その形の方が今のルールより年率が高かった（最大下落率が小さかった）割合。95%の範囲は年率の差（年あたりのポイント、対数）。\n")
    w_("| 形 | 年率の差の中央値 | 95%の範囲 | 年率が良い確率 | 最大下落率の差の中央値 | 最大下落率が小さい確率 |")
    w_("|---|---|---|---|---|---|")
    keys = [k for k in F if k != base87]
    diffs = {k: [] for k in keys}
    ddiffs = {k: [] for k in keys}
    for _ in range(a.reps):
        idx = stationary_idx(n)
        b0 = LR[base87][idx]
        m0 = path_mdd(b0)
        for k in keys:
            bk = LR[k][idx]
            diffs[k].append((bk.sum() - b0.sum()) / n * 252)
            ddiffs[k].append(path_mdd(bk) - m0)
    for k in keys:
        x, y = np.array(diffs[k]), np.array(ddiffs[k])
        w_(f"| {k} | {np.median(x) * 100:+.1f}pt | {np.quantile(x, 0.025) * 100:+.1f}〜{np.quantile(x, 0.975) * 100:+.1f}pt | {np.mean(x > 0) * 100:.0f}% | "
           f"{np.median(y) * 100:+.1f}pt | {np.mean(y < 0) * 100:.0f}% |")

    # 5. 合成した長い下げ
    sx = load_prices(DEFAULT_CACHE, "^SOX")
    m200 = sma(sx["c"], 200)
    down = {sx["date"][i] for i in range(len(sx["c"])) if m200[i] is not None and sx["c"][i] < m200[i]}
    isd = np.array([d in down for d in days[1:]])
    starts = [i for i in range(n - 20) if isd[i:i + 20].all()]
    w_("\n## 3. 合成した長い下げ（2015年〜の「SOXが200日線の下」が20日続いた区間をつないだ250取引日の道）\n")
    w_(f"- 下げの局面の日は2015年〜の {isd.mean() * 100:.0f}%。20日続いた区間の始まりの候補 {len(starts)}日（2016年・2018〜2019年・2020年・2022年・2025年・2026年など）。"
       f"道を{a.reps}本作り、全部の形に同じ日を使う。")
    w_("- 実際の長い下げ（2000〜2002年）では、下げが長く続くほど銘柄のRSや150日線が崩れていくが、この道は短い下げの区間をつないだものなので、その変化は入らない"
       "（強さの条件の効きは小さく出やすい）。\n")
    w_("| 形 | 1年の損益の中央値 | 悪い5% | 最大下落率の中央値 | 最大下落率の悪い5% | −30%より悪い割合 | 今のルールより損が小さい割合 |")
    w_("|---|---|---|---|---|---|---|")
    syn = {k: [] for k in F}
    syn_m = {k: [] for k in F}
    if starts:
        for _ in range(a.reps):
            idx = np.concatenate([np.arange(s, s + 20) for s in RNG.choice(starts, size=13)])[:250]
            for k in F:
                lr = LR[k][idx]
                syn[k].append(np.exp(lr.sum()) - 1)
                syn_m[k].append(path_mdd(lr))
        b = np.array(syn[base87])
        for k in F:
            x, y = np.array(syn[k]), np.array(syn_m[k])
            w_(f"| {k} | {np.median(x) * 100:+.1f}% | {np.quantile(x, 0.05) * 100:+.1f}% | {np.median(y) * 100:.0f}% | {np.quantile(y, 0.95) * 100:.0f}% | "
               f"{np.mean(x < -0.3) * 100:.0f}% | {'—' if k == base87 else f'{np.mean(x > b) * 100:.0f}%'} |")
    # 6. 枠の使い方（2026-11-22 ユーザーの質問「強さの条件は、枠が空けばテーマの外の銘柄を選択するの？」）
    tr_ = [(("87銘柄: " + short(nm)), d87[nm]["trades"], d87[nm].get("live_trades")) for nm in n87 if d87[nm].get("trades")]
    if tr_:
        w_("\n## 4. 枠の使い方（4枠のうち、87銘柄・テーマの外の強い銘柄・空き〔現金。QQQの形はQQQ〕で持っていた日の割合と、1年の買いの数。乱数10通りの平均）\n")
        yrs = sorted({d[:4] for d in days})
        w_("| 形 | 年 | " + " | ".join(yrs) + " | 全期間 |")
        w_("|---|---|" + "---|" * (len(yrs) + 1))
        for k, trs_, lt_ in tr_:
            tab = slot_use(trs_, days)
            nd = {y: sum(1 for d in days if d[:4] == y) for y in yrs}
            tot = sum(nd.values())
            agg = [sum(tab[y][i] * nd[y] for y in yrs) / tot for i in range(3)]
            w_(f"| {k} | 87銘柄 | " + " | ".join(f"{tab[y][0] * 100:.0f}%" for y in yrs) + f" | {agg[0] * 100:.0f}% |")
            w_(f"| | テーマの外 | " + " | ".join(f"{tab[y][1] * 100:.0f}%" for y in yrs) + f" | {agg[1] * 100:.0f}% |")
            w_(f"| | 空き | " + " | ".join(f"{tab[y][2] * 100:.0f}%" for y in yrs) + f" | {agg[2] * 100:.0f}% |")
            w_(f"| | 買いの数（87銘柄／テーマの外） | " + " | ".join(f"{tab[y][3]:.0f}／{tab[y][4]:.0f}" for y in yrs) + " | |")
        w_("\n今回の期間（空の枠から）の買いの数（乱数30通りの中央値。87銘柄／テーマの外）: " + "、".join(
            f"{k} {np.median([sum(1 for x in tl if x[6] == 0) for tl in lt_]):.0f}／{np.median([sum(1 for x in tl if x[6] == 1) for tl in lt_]):.0f}"
            for k, _, lt_ in tr_ if lt_ and len(lt_[0][0] if lt_[0] else []) > 6))
    w_("\n- この結果は数値を条件どおりに計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))
    if a.pbo_json:   # pbo_check.py eq 用（87銘柄の今のルールを今のルールとして、ほかの形を並べる）
        out = {}
        for k, v in F.items():
            if k.startswith("全業種"):
                continue
            out[k] = {"days": days, "eq": v[0].tolist()}
        json.dump(out, open(a.pbo_json, "w"), ensure_ascii=False)


if __name__ == "__main__":
    main()
