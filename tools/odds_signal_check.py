#!/usr/bin/env python3
"""手8の(4)（Fableの提案 `新分析ツール/Fableの提案_未解決の課題_2026-11-15.md` 9節、2026-11-15）:
押し目・急落の底の合図の日に、その銘柄の上下判定ツール（3〜5日版 `tools/swing_odds.py`）の点数が上位30%か下位30%かで、
合図の1回平均を比べる（1段目だけ。資金の計算はしない）。

点数: `tools/swing_odds_model.json` の「5日後の前日比・全部」（cc5・全部）。点数の表は2015〜2021年で作ったもの（2022年以降は確かめる期間）。
数値は swing_odds.build（S&P500の構成銘柄・その日の構成）で作り直す（点検 2026-10-16 の3: 決算の反応日に少し先読みが残っている）。
上位・下位30%の境目は、2015〜2020年のすべての銘柄の日の点数で決める。
でたらめ: 同じ合図の日・同じルールの合図の中で、上位30%・下位30%のラベルを入れ替える（1,000回）。
目安: 確かめる期間（2022年〜）で差が +1.5pt 以上、かつでたらめの上位5%、両方の監視銘柄。

使い方: python3 tools/odds_signal_check.py [--out FILE]
"""
import argparse
import json
import os
import random
import statistics as st
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import swing_odds as so  # noqa: E402
from backtest_lib import DEFAULT_CACHE, load_members  # noqa: E402

C = DEFAULT_CACHE


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--perm", type=int, default=1000)
    a = ap.parse_args()
    model = json.load(open(so.MODEL))
    lm = model["labels"]["cc5"]["全部"]
    edges = [np.array(e) for e in model["edges"]]
    members = load_members(C)
    sig = {}
    for wch in ("87", "free"):
        sig[wch] = [r for r in json.load(open(os.path.join(C, f"results/combo_feat_{wch}.json"))) if r["src"] == "今" and r["rule"] in ("B", "C") and r["sd"] >= "2015-01-01"]
    syms = sorted(set(members))
    S, Dd, X, _ = so.build(C, syms, members)
    A = so.to_design(X, edges)
    score = A[:, lm["cols"]] @ np.array(lm["w"])
    des = Dd < "2021-01-01"
    lo_th, hi_th = np.quantile(score[des], 0.3), np.quantile(score[des], 0.7)
    sc = {(s, d): v for s, d, v in zip(S, Dd, score)}
    out = []
    w = out.append
    w(f"- 点数のある銘柄の日 {len(score):,}。下位30%の境目 {lo_th:.3f}、上位30%の境目 {hi_th:.3f}（2015〜2020年で決めた）")
    ok_all = True
    for wch, lab in (("87", "87銘柄"), ("free", "全業種（後知恵なし）")):
        items = []
        for r in sig[wch]:
            v = sc.get((r["sym"], r["sd"]))
            if v is None:
                continue
            if v >= hi_th:
                items.append((r, True))
            elif v <= lo_th:
                items.append((r, False))
        w(f"\n## {lab}（押し目・急落の底の合図 {len(sig[wch])}件のうち、点数が上位30%・下位30%の {len(items)}件）\n")
        w("| 期間 | 上位30% 件数・1回平均・損切り | 下位30% 件数・1回平均・損切り | 差 |")
        w("|---|---|---|---|")
        res = {}
        for per, lo, hi in (("2015〜2021年（点数を作った期間）", "2015", "2022"), ("2022〜2026年（確かめる）", "2022", "2027"), ("全期間", "2015", "2027")):
            ss = [(r, h) for r, h in items if lo <= r["sd"][:4] < hi]
            y = [r for r, h in ss if h]
            n = [r for r, h in ss if not h]
            f = lambda g: f"{len(g)}・{st.mean(x['ret'] for x in g):+.2%}・{sum(1 for x in g if x['stopped']) / len(g):.0%}" if g else "0"  # noqa: E731
            dd = (st.mean(x["ret"] for x in y) - st.mean(x["ret"] for x in n)) if y and n else None
            res[per] = dd
            w(f"| {per} | {f(y)} | {f(n)} | {'—' if dd is None else f'{dd:+.2%}'} |")
        ver = [(r, h) for r, h in items if r["sd"] >= "2022"]
        cells = {}
        for i, (r, h) in enumerate(ver):
            cells.setdefault((r["sd"], r["rule"]), []).append(i)

        def diff(hs):
            y = [ver[i][0]["ret"] for i in range(len(ver)) if hs[i]]
            n = [ver[i][0]["ret"] for i in range(len(ver)) if not hs[i]]
            return st.mean(y) - st.mean(n) if y and n else None
        base = [h for _, h in ver]
        obs = diff(base)
        rnd = random.Random(0)
        ge = 0
        for _ in range(a.perm):
            hs = list(base)
            for idx in cells.values():
                if len(idx) > 1:
                    v = [base[i] for i in idx]
                    rnd.shuffle(v)
                    for i, x in zip(idx, v):
                        hs[i] = x
            d2 = diff(hs)
            if d2 is not None and obs is not None and d2 >= obs:
                ge += 1
        pp = ge / a.perm
        w(f"- 確かめる期間のでたらめ（同じ日・同じルールの中で入れ替え、{a.perm}回）で本物以上だった割合 {pp:.0%}")
        ok = obs is not None and obs >= 0.015 and pp <= 0.05
        ok_all = ok_all and ok
    w(f"\n**判定: {'通った' if ok_all else '通らなかった'}**（目安: 両方の監視銘柄で、確かめる期間の差が +1.5pt 以上、かつでたらめの上位5%）")
    text = "\n".join(out) + "\n"
    if a.out:
        open(a.out, "w", encoding="utf-8").write(text)
    print(text)


if __name__ == "__main__":
    main()
