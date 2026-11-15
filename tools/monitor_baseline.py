#!/usr/bin/env python3
"""M4 効き目の見張り（Fableの提案 `新分析ツール/Fableの提案_確かめ方_2026-11-15.md` 4節、2026-11-15）

今のルールの合図（`results/combo_feat_*.json`、src="今"、枠に関係なく全部）で、次の数値の月ごとの値と、2015〜2020年の基準を作り、
CUSUM（Page 1954）で「落ちた」と知らせる月を出す（知らせるだけ。売買のルールは変えない）。
  ① 急落の底の、指数の分を除いた損益: 損益 − 感応度 × 同じ期間（合図の日〜売った日）の指数の騰落率。売った月ごとの平均（2件以上の月）
     指数は全業種がS&P500、87銘柄がSOX。感応度は2015〜2020年の合図で、損益を指数の騰落率に回帰した係数
  ② 順番の効き目: 合図が4件以上あった日ごとに、RSの高い半分の損益の平均 − 低い半分の平均。合図の月ごとの平均
     RS = 0.4×3か月 ＋ 0.2×6か月 ＋ 0.2×9か月 ＋ 0.2×12か月の騰落率（theme_scan の rs_raw と同じ。同じ日の中の順位だけを使う）
  ③（表示だけ）ルールごとの素の損益: 売った月の平均（2件以上の月）
CUSUM: z ＝（値 − 基準の平均）÷ 基準のばらつき（±3で頭打ち）、S ＝ max(0, 前の S − z − k)、S≧h で知らせて S を0に戻す。
  大きな崩れ用 k=0.5・h=3、ゆっくりした低下用 k=0.15・h=6。

使い方: python3 tools/monitor_baseline.py [--out FILE] [--json FILE]
"""
import argparse
import bisect
import json
import os
import statistics as st
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fable_data as fd  # noqa: E402
from backtest_lib import DEFAULT_CACHE, load_prices  # noqa: E402

C = DEFAULT_CACHE
RULES = {"B": "押し目", "C": "急落の底", "M": "ミネルヴィニ", "V": "新高値V2"}


def cusum(vals, mean, sd, k, h):
    S, alarms = 0.0, []
    for m, v in vals:
        z = max(-3.0, min(3.0, (v - mean) / sd)) if sd > 0 else 0.0
        S = max(0.0, S - z - k)
        if S >= h:
            alarms.append(m)
            S = 0.0
    return alarms


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--json")
    a = ap.parse_args()
    fd.L = os.path.join(C, "long/index/")
    idx = {"free": {d: v[3] for d, v in fd.load("^GSPC").items()}, "87": {d: v[3] for d, v in fd.load("^SOX").items()}}
    out = []
    w = out.append
    base_json = {}
    PX = {}

    def rs_raw(sym, sd):
        if sym not in PX:
            p = load_prices(C, sym)
            PX[sym] = (p["date"], p["c"]) if p else None
        if not PX[sym]:
            return None
        ds, c = PX[sym]
        i = bisect.bisect_right(ds, sd) - 1
        if i < 252:
            return None
        return 0.4 * (c[i] / c[i - 63] - 1) + 0.2 * (c[i] / c[i - 126] - 1) + 0.2 * (c[i] / c[i - 189] - 1) + 0.2 * (c[i] / c[i - 252] - 1)

    for wch, lab in (("free", "全業種（後知恵なし）・指数はS&P500"), ("87", "87銘柄・指数はSOX")):
        rows = [r for r in json.load(open(os.path.join(C, f"results/combo_feat_{wch}.json"))) if r["src"] == "今" and r["sd"] >= "2015-01-01"]
        ix = idx[wch]
        ixd = sorted(ix)

        def ixret(a_, b_):
            i0 = bisect.bisect_right(ixd, a_) - 1
            i1 = bisect.bisect_right(ixd, b_) - 1
            return ix[ixd[i1]] / ix[ixd[i0]] - 1
        w(f"\n## {lab}\n")
        bj = {}
        # ①
        cr = [r for r in rows if r["rule"] == "C"]
        xs = [(r, ixret(r["sd"], r["out"])) for r in cr]
        des = [(r["ret"], m) for r, m in xs if r["out"] <= "2020-12-31"]
        X_ = np.array([m for _, m in des])
        Y_ = np.array([y for y, _ in des])
        beta = float(np.polyfit(X_, Y_, 1)[0])
        by_m = {}
        for r, m in xs:
            by_m.setdefault(r["out"][:7], []).append(r["ret"] - beta * m)
        vals = [(m, st.mean(v)) for m, v in sorted(by_m.items()) if len(v) >= 2]
        bv = [v for m, v in vals if m <= "2020-12"]
        mean_, sd_ = st.mean(bv), st.stdev(bv)
        a1 = cusum(vals, mean_, sd_, 0.5, 3)
        a2 = cusum(vals, mean_, sd_, 0.15, 6)
        e1 = st.mean([r["ret"] - beta * m for r, m in xs if r["sd"] < "2021"])
        e2 = st.mean([r["ret"] - beta * m for r, m in xs if r["sd"] >= "2021"])
        w(f"- ① 急落の底: 感応度 {beta:.2f}、基準の月の平均 {mean_:+.2%}・ばらつき {sd_:.2%}（{len(bv)}か月）。指数の分を除いた1回平均 2015〜2020年 {e1:+.2%} → 2021年〜 {e2:+.2%}")
        w(f"  - 知らせた月: 大きな崩れ用（k=0.5・h=3）{', '.join(a1) or 'なし'}／ゆっくり用（k=0.15・h=6）{', '.join(a2) or 'なし'}")
        bj["crash_resid"] = dict(beta=beta, mean=mean_, sd=sd_)
        # ②
        byd = {}
        for r in rows:
            byd.setdefault(r["sd"], []).append(r)
        dv = []
        for d, rs in byd.items():
            if len(rs) < 4:
                continue
            sc = [(rs_raw(r["sym"], d), r["ret"]) for r in rs]
            sc = [x for x in sc if x[0] is not None]
            if len(sc) < 4:
                continue
            sc.sort(key=lambda x: -x[0])
            h = len(sc) // 2
            dv.append((d[:7], st.mean(x[1] for x in sc[:h]) - st.mean(x[1] for x in sc[-h:])))
        by_m2 = {}
        for m, v in dv:
            by_m2.setdefault(m, []).append(v)
        vals2 = [(m, st.mean(v)) for m, v in sorted(by_m2.items())]
        bv2 = [v for m, v in vals2 if m <= "2020-12"]
        mean2, sd2 = st.mean(bv2), st.stdev(bv2)
        t2 = mean2 / (sd2 / len(bv2) ** 0.5)
        a3 = cusum(vals2, mean2, sd2, 0.5, 3)
        a4 = cusum(vals2, mean2, sd2, 0.15, 6)
        later = [v for m, v in vals2 if m >= "2021-01"]
        w(f"- ② 順番の効き目（RSの高い半分 − 低い半分）: 基準の月の平均 {mean2:+.2%}・ばらつき {sd2:.2%}（{len(bv2)}か月、t値 {t2:.2f}）。2021年〜の月の平均 {st.mean(later):+.2%}")
        w(f"  - 知らせた月: 大きな崩れ用 {', '.join(a3) or 'なし'}／ゆっくり用 {', '.join(a4) or 'なし'}" + ("（基準が0に近い（t値が2未満）ので、この見張りは使わない方がよい）" if abs(t2) < 2 else ""))
        bj["order_effect"] = dict(mean=mean2, sd=sd2, t=t2)
        # ③ 表示だけ
        w("- ③（表示だけ）ルールごとの素の損益の見張り（大きな崩れ用）:")
        for rule, nm in RULES.items():
            by = {}
            for r in rows:
                if r["rule"] == rule:
                    by.setdefault(r["out"][:7], []).append(r["ret"])
            v3 = [(m, st.mean(v)) for m, v in sorted(by.items()) if len(v) >= 2]
            b3 = [v for m, v in v3 if m <= "2020-12"]
            if len(b3) < 6:
                continue
            w(f"  - {nm}: 基準の月の平均 {st.mean(b3):+.2%}・ばらつき {st.stdev(b3):.2%}、知らせた月 {', '.join(cusum(v3, st.mean(b3), st.stdev(b3), 0.5, 3)) or 'なし'}")
        base_json[wch] = bj
    text = "\n".join(out) + "\n"
    if a.json:
        json.dump(base_json, open(a.json, "w"), ensure_ascii=False, indent=1)
    if a.out:
        open(a.out, "w", encoding="utf-8").write(text)
    print(text)


if __name__ == "__main__":
    main()
