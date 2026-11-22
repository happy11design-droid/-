#!/usr/bin/env python3
"""いくつかの形（または監視銘柄）の毎日の資金を、決めた割合で後から混ぜて数える（2026-11-22）

Fable 5.2 の提案 `新分析ツール/Fableの提案_混ぜて持つ形_2026-11-15.md`（ブランチ claude/friendly-maxwell-vbfvfl）の7節の5通りを確かめる。
土台は Fable の試し計算 `tools/fable_mix_quick/mixD.py`〜`mixG.py`。backtest_retest.py は変えずに、書き出した毎日の資金（OPT_EQDUMP・OPT_EQDUMP_ALL=1）を使う。

混ぜ方: 乱数の番号が同じ資金どうしを組にし、口ごとの毎日の騰落率で増減させる。毎年1月の最初の取引日に決めた割合へ戻す（--norebal で戻さない）。
  2つの口は別々の資金なので、口に分けた運用はこの計算で正確に出る（税は口ごとに数える。口の間で通算しない）。
物差し:
  年率・2015〜21年・2022年〜（乱数の中央値）、最大下落率（中央値と乱数の最悪）
  1年の区切り（毎日の資金から250取引日を10取引日ごと）: 損益の平均、悪い5%、1年の中の下落率の悪い5%
  年ごと（乱数の中央値）、今回の期間（2026-10-02 の引けに空の枠から始めた資金 live。口は戻さない）
  半分ずつの期間の確かめ（M1と同じ16ブロック・12,870通り）: 乱数の平均の毎日の対数の騰落率をつないだ道で、
    (i) 混ぜた形の年率が、その半分の期間で悪かった方の口を上回る割合
    (ii) 混ぜた形の最大下落率が、その半分の期間で年率の良かった方の口より小さい割合

使い方: python3 tools/mix_check.py [--out FILE]
"""
import argparse
import itertools
import json
import os

import numpy as np

R = os.path.expanduser("~/.cache/stock_backtest/results/")
BASE = "待っている現金をQQQに置く"


def load(f):
    p = f if os.path.isabs(f) else R + f
    return json.load(open(p))


def pick(d, cond):
    n = next(n for n in d if cond(n))
    live = []
    for x in d[n].get("live", []):   # 運用の開始の前は None
        k = next(i for i, v in enumerate(x) if v is not None)
        live.append(np.array(x[k:], float))
    return [np.array(x, float) for x in d[n]["eq"]], live, d[n]["days"]


def mdd(e):
    p = np.maximum.accumulate(e)
    return float((1 - e / p).max())


def blend(Es, w, days, rebal=True):
    out = []
    for k in range(len(Es[0])):
        rets = [np.diff(E[k]) / E[k][:-1] for E in Es]
        val = np.array(w, float)
        tot = [1.0]
        for t in range(len(rets[0])):
            if rebal and days[t + 1][:4] != days[t][:4]:
                val = np.array(w, float) * val.sum()
            val = val * (1 + np.array([r[t] for r in rets]))
            tot.append(val.sum())
        out.append(np.array(tot))
    return out


def stats(E, days, live=None):
    yrs = (np.datetime64(days[-1]) - np.datetime64(days[0])).astype(int) / 365.25
    i22 = next(i for i, d in enumerate(days) if d >= "2022-01-01")
    y1 = (np.datetime64(days[i22]) - np.datetime64(days[0])).astype(int) / 365.25
    W = 250
    st = range(0, len(days) - W, 10)
    r = np.array([[e[s + W] / e[s] - 1 for s in st] for e in E])
    dw = np.array([[mdd(e[s:s + W + 1]) for s in st] for e in E])
    ys = sorted({d[:4] for d in days})
    idx = {y: [i for i, d in enumerate(days) if d[:4] == y] for y in ys}
    yr = np.median(np.array([[e[idx[y][-1]] / e[max(idx[y][0] - 1, 0)] - 1 for y in ys] for e in E]), axis=0)
    out = dict(cg=np.median([(e[-1] / e[0]) ** (1 / yrs) - 1 for e in E]),
               c1=np.median([(e[i22] / e[0]) ** (1 / y1) - 1 for e in E]),
               c2=np.median([(e[-1] / e[i22]) ** (1 / (yrs - y1)) - 1 for e in E]),
               dd=np.median([mdd(e) for e in E]), ddw=max(mdd(e) for e in E),
               r=r, dw=dw, rmean=r.mean(), r5=np.percentile(r, 5), d95=np.percentile(dw, 95), years=dict(zip(ys, yr)))
    if live is not None:
        out["live"] = np.median([x[-1] / x[0] - 1 for x in live])
    return out


def row(lab, S):
    return (f"| {lab} | {S['cg'] * 100:.1f}% | {S['c1'] * 100:.1f}% / {S['c2'] * 100:.1f}% | {S['dd'] * 100:.0f}%（{S['ddw'] * 100:.0f}%） | "
            f"{S['rmean'] * 100:.1f}% | {S['r5'] * 100:+.1f}% | {S['d95'] * 100:.1f}% | " + (f"{S['live'] * 100:+.1f}%" if "live" in S else "—") + " |")


HEAD = ("| 形 | 年率 | 2015〜21年 / 2022年〜 | 最大下落率（乱数の最悪） | 1年の区切り: 損益の平均 | 損益の悪い5% | 下落率の悪い5% | 今回の期間（10/2の引け〜11/10） |\n"
        "|---|---|---|---|---|---|---|---|")


def split_check(Ea, Eb, Em, days, nblk=16):
    """(i) 混ぜた形の年率が悪かった方の口を上回る割合、(ii) 混ぜた形の最大下落率が年率の良かった方の口より小さい割合（12,870通り）"""
    lr = [np.mean([np.diff(np.log(e)) for e in E], axis=0) for E in (Ea, Eb, Em)]
    blocks = np.array_split(np.arange(len(lr[0])), nblk)
    n1 = n2 = n3 = cnt = 0
    for c in itertools.combinations(range(nblk), nblk // 2):
        ix = np.concatenate([blocks[i] for i in c])
        cg, dd = [], []
        for x in lr:
            path = np.exp(np.concatenate([[0.0], np.cumsum(x[ix])]))
            cg.append(x[ix].mean() * 252)
            dd.append(mdd(path))
        good = 0 if cg[0] >= cg[1] else 1
        n1 += cg[2] > min(cg[0], cg[1])
        n2 += dd[2] < dd[good]
        cal = [c / d if d > 0 else 0 for c, d in zip(cg, dd)]
        n3 += cal[2] > max(cal[0], cal[1])
        cnt += 1
    return n1 / cnt, n2 / cnt, n3 / cnt, cnt


def years_table(rows_):
    ys = list(rows_[0][1]["years"])
    t = ["| | " + " | ".join(ys) + " |", "|---|" + "---|" * len(ys)]
    for lab, S in rows_:
        t.append(f"| {lab} | " + " | ".join(f"{S['years'][y] * 100:+.0f}" for y in ys) + " |")
    return "\n".join(t)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    a = ap.parse_args()
    L = []
    w = L.append
    # ---------- 案1（#1・#2）: 87銘柄の口と全業種の口 ----------
    H8, Hf = load("hold_eq_87.json"), load("hold_eq_free.json")
    E8, l8, days = pick(H8, lambda n: n.endswith(BASE))
    Ef, lf, d2 = pick(Hf, lambda n: n.endswith(BASE))
    assert days == d2
    w("## 1. 案1: 監視銘柄を混ぜる（今のルール＋QQQ、税込み、手数料は今までの片道0.1%）\n")
    w(HEAD)
    S8, Sf = stats(E8, days, l8), stats(Ef, days, lf)
    rows_ = [("87銘柄だけ（今の毎朝の形）", S8), ("全業種だけ（後知恵なし）", Sf)]
    w(row(*rows_[0]))
    w(row(*rows_[1]))
    mixes = {}
    for lab, wt, rb in (("#1 半分ずつ・毎年1月に戻す", (.5, .5), True), ("#2 87銘柄75%・全業種25%・毎年1月に戻す", (.75, .25), True), ("（参考）半分ずつ・戻さない", (.5, .5), False)):
        Em = blend([E8, Ef], wt, days, rb)
        Lm = blend([l8, lf], wt, [d for d in days if d >= "2026-10-02"][:len(l8[0])], False)
        S = stats(Em, days, Lm)
        mixes[lab] = (Em, S)
        rows_.append((lab, S))
        w(row(lab, S))
    w("\n年ごと（乱数の中央値、%）:\n")
    w(years_table(rows_[:3]))
    for lab in ("#1 半分ずつ・毎年1月に戻す", "#2 87銘柄75%・全業種25%・毎年1月に戻す"):
        p1, p2, p3, cnt = split_check(E8, Ef, mixes[lab][0], days)
        w(f"\n- {lab}: 半分ずつの期間の確かめ（{cnt}通り）: (i) 年率が悪かった方の口を上回る割合 **{p1:.1%}**、(ii) 最大下落率が年率の良かった方の口より小さい割合 **{p2:.1%}**（効かない条件: (ii) が70%未満）、"
          f"(iii) 年率÷最大下落率が両方の口を上回る割合 **{p3:.1%}**（(i)・(ii) は2つの口の間に入るだけでも満たしやすい。(iii) は混ぜること自体の得を見る）")
    nb = sum(1 for y in S8["years"] if mixes["#1 半分ずつ・毎年1月に戻す"][1]["years"][y] > min(S8["years"][y], Sf["years"][y]))
    w(f"- #1 が悪い方の口を上回った年: {nb}/{len(S8['years'])}")
    # 手数料
    if os.path.exists(R + "mixfee_eq_87.json") and os.path.exists(R + "mixfee_eq_free.json"):
        F8, Ff = load("mixfee_eq_87.json"), load("mixfee_eq_free.json")
        w("\n## 2. 案1の手数料（1回の金額が半分の1,500ドルになる）\n")
        w("アドバンスの率は、直近1年の候補1,986件の株価で計算した平均（1株0.0049ドル・最低0.99ドル＋税、システム利用料1株0.005ドル・最低1ドル＋税、清算1株0.006ドル）: "
          "1回3,000ドル 0.082%、1回1,500ドル 0.169%。ベーシックは0.132%（最低なし）。1回1,500ドルでは、アドバンスよりベーシックの方が安い。\n")
        w(HEAD)
        g = lambda D, key: pick(D, lambda n: key in n)  # noqa: E731
        sets = {}
        for key, lab in (("ベーシック（片道0.132%）", "ベーシック"), ("1回3,000ドル", "アドバンス3,000ドル"), ("1回1,500ドル", "アドバンス1,500ドル")):
            a8, b8, dd8 = g(F8, key)
            af, bf, ddf = g(Ff, key)
            sets[lab] = (a8, b8, af, bf)
            for nm_, E_, L_ in (("87銘柄だけ", a8, b8), ("全業種だけ", af, bf)):
                w(row(f"{nm_}・{lab}", stats(E_, dd8, L_)))
        for lab_, k8, kf in (("#1 半分ずつ・どちらの口もベーシック", "ベーシック", "ベーシック"), ("（参考）#1 半分ずつ・どちらの口もアドバンス1,500ドル", "アドバンス1,500ドル", "アドバンス1,500ドル")):
            Em = blend([sets[k8][0], sets[kf][2]], (.5, .5), dd8, True)
            Lm = blend([sets[k8][1], sets[kf][3]], (.5, .5), [d for d in dd8 if d >= "2026-10-02"][:len(sets[k8][1][0])], False)
            w(row(lab_, stats(Em, dd8, Lm)))
        w("\n- 比べ方: 今のまま（87銘柄だけ）でアドバンスに変える（策2）と、87銘柄だけ・アドバンス3,000ドル。案1にすると、1回1,500ドルでベーシックが一番安いので、#1 半分ずつ・どちらの口もベーシック。")
    # ---------- 案2（#3・#4）: 保留の形を割合で持つ ----------
    w("\n## 3. 案2: 保留の形を割合で持つ（毎日の資金 `hold_eq_*.json`、毎年1月に戻す）\n")
    for wch, H in (("87銘柄", H8), ("全業種", Hf)):
        b, bl, dy = pick(H, lambda n: n.endswith(BASE))
        s2, s2l, _ = pick(H, lambda n: "30週線" in n)
        al, all_, _ = pick(H, lambda n: "2倍ETFをいつでも" in n)
        Sb, Ss, Sa = stats(b, dy, bl), stats(s2, dy, s2l), stats(al, dy, all_)
        w(f"\n### {wch}\n")
        w(HEAD)
        for lab, S in (("今のルール（QQQ）", Sb), ("QQQ＋ステージ2の後40日は2倍ETF", Ss), ("2倍ETFをいつでも使う", Sa)):
            w(row(lab, S))
        m3 = stats(blend([b, s2], (.5, .5), dy), dy)
        m4 = stats(blend([b, s2, al], (1 / 3,) * 3, dy), dy)
        w(row("#3 今50%＋ステージ2 50%", m3))
        w(row("#4 今・ステージ2・いつでも2倍 1/3ずつ", m4))
        mid3 = (Sb["cg"] + Ss["cg"]) / 2
        mid4 = (Sb["cg"] + Ss["cg"] + Sa["cg"]) / 3
        w(f"\n- 中間からのずれ（年率）: #3 {(m3['cg'] - mid3) * 100:+.2f}pt（中間 {mid3 * 100:.1f}%）、#4 {(m4['cg'] - mid4) * 100:+.2f}pt（中間 {mid4 * 100:.1f}%）。"
          f"効かない条件: ずれが0.3pt未満（混ぜること自体の上乗せがない）")
        w(f"- 1年の区切りの今のルールとの差: #3 {(m3['r'] - Sb['r']).mean() * 100:+.1f}pt（良い割合 {((m3['r'] - Sb['r']).mean(axis=0) > 0).mean():.0%}）、"
          f"#4 {(m4['r'] - Sb['r']).mean() * 100:+.1f}pt（{((m4['r'] - Sb['r']).mean(axis=0) > 0).mean():.0%}）")
    # ---------- 案3（#5）と案1の空の枠から始めた1年（st2roll） ----------
    w("\n## 4. 空の枠から始めた1年（`st2roll_*.json`、始める日×乱数10、候補の25%を乱数で見送る形）\n")
    A = {u: load(f"st2roll_{u}.json") for u in ("free", "87")}

    def lr_(u):
        F, days_ = A[u]["forms"], A[u]["days"]
        pos = {d: k for k, d in enumerate(days_)}
        base = next(n for n in F if not n.startswith("今のルール（傾き"))
        return F, base, [d for d in F[base] if pos[d] + A[u]["win"] <= len(days_) - 1]
    Ffr, bfr, dfr = lr_("free")
    F87, b87, d87 = lr_("87")
    done = [d for d in dfr if d in set(d87)]
    arr = lambda F, n, j=0: np.array([[x[j] for x in F[n][d]] for d in done])  # noqa: E731
    q = lambda F, s: next(x for x in F if x.endswith(s))  # noqa: E731
    A8, Af = arr(F87, q(F87, BASE)), arr(Ffr, q(Ffr, BASE))
    early = np.array([d < "2021-01-01" for d in done])
    w("| 形 | 1年の損益の平均（〜2020年に始めた / 2021年〜） | 悪い5% | 悪い1% | マイナスで終わる割合 |\n|---|---|---|---|---|")
    for lab, X in (("87銘柄だけ", A8), ("全業種だけ", Af), ("#1 半分ずつ（1年のあいだ戻さない）", (A8 + Af) / 2), ("#2 87銘柄75%・全業種25%", .75 * A8 + .25 * Af)):
        w(f"| {lab} | {X.mean() * 100:.1f}%（{X[early].mean() * 100:.1f}% / {X[~early].mean() * 100:.1f}%） | {np.percentile(X, 5) * 100:+.1f}% | {np.percentile(X, 1) * 100:+.1f}% | {(X < 0).mean() * 100:.1f}% |")
    keys = ["待っている現金をQQQに置く＋底の後40日は2倍ETF", "損切り18%", "一目", "決算㉒", "RSI(2)≦15"]
    w("\n案3（#5 中身で選んだ5形を等しく。比べる元は今のルール＝QQQなし）:\n")
    w("| 監視銘柄 | 今のルールとの差 | 良い割合 | 〜2020年 / 2021年〜 | 1年の損益の悪い5%（今） | 選びすぎを割り引いた見込み（Fableの2-1） |\n|---|---|---|---|---|---|")
    for u, F, b, disc in (("全業種", Ffr, bfr, "−0.9pt"), ("87銘柄", F87, b87, "−0.4pt")):
        B = arr(F, b)
        ns = [next(n for n in F if k in n and "銘柄数3" not in n) for k in keys]
        X = np.mean([arr(F, n) for n in ns], axis=0)
        d = X - B
        m = d.mean(axis=1)
        w(f"| {u} | {d.mean() * 100:+.1f}pt | {(m > 0).mean():.0%} | {d[early].mean() * 100:+.1f}pt / {d[~early].mean() * 100:+.1f}pt | {np.percentile(X, 5) * 100:+.1f}%（{np.percentile(B, 5) * 100:+.1f}%） | {disc} |")
    text = "\n".join(L) + "\n"
    if a.out:
        open(a.out, "w", encoding="utf-8").write(text)
    print(text)


if __name__ == "__main__":
    main()
