#!/usr/bin/env python3
"""局面×指標×ニュースの組み合わせで、合図の成績を数えて決まりを作る（2026-11-13 ユーザーの指示「はい。お願いします。」）

入力: tools/backtest_retest.py の OPT_FEATDUMP で書き出した合図と状況（87銘柄・全業種）。
状況の切り口（14）: PH 銘柄の局面、SX SOXの局面、R2 RSI(2)、R14 RSI(14)、MACD（シグナル・0との位置）、MX MACDの上抜け、HIST ヒストグラム、
  EARN 個別の決算、VOL 個別の材料（出来高3倍の急騰・急落）、IND1 業界のその日、IND5 業界の5日、BIG4 大手4社の決算、VIX、CRED 信用。
1〜3つの切り口の組み合わせごとに、ルール（押し目B・急落の底C・ミネルヴィニM・新高値V2 V、今の4つまとめて *、新しい買い J・Z1・Z2）の
合図の1回平均・勝率を、**2015〜2021年（決める期間）**と2022年〜（確かめる期間。決めるのには使わない）に分けて数える。
決まりは決める期間だけで作る（両方の監視銘柄で同じ向き。全業種は後知恵なしなので、こちらで強い差を求める）:
  見送る: 今のルールの合図で、全業種 n≧30・t≦−3・平均<0、87銘柄 n≧20・平均<0
  先に買う: 今のルールの合図で、全業種 n≧30・t≧3・平均≧+3%、87銘柄 n≧20・平均>0
  足す: 新しい買い（J・Z1・Z2）で、全業種 n≧30・t≧3・平均≧+2%、87銘柄 n≧20・平均>0
使い方: python3 tools/combo_search.py <87のjson> <全業種のjson> <決まりのjson> <結果のmd> [--years N]
  --years N（2026-11-13 に最初の結果を見てから足した、参考の厳しい形）: 決める期間の合図が N 暦年以上にまたがる状況だけ使う
  （同じ出来事（2020年3月など）の合図は一緒に動くので、件数が多くても実質は1〜2回分のことがある）
"""
import itertools
import json
import sys

import numpy as np
import pandas as pd

DIMS = ["PH", "SX", "R2", "R14", "MACD", "MX", "HIST", "EARN", "VOL", "IND1", "IND5", "BIG4", "VIX", "CRED"]
LAB = {"PH": "銘柄の局面", "SX": "SOXの局面", "R2": "RSI(2)", "R14": "RSI(14)", "MACD": "MACD", "MX": "MACDの上抜け", "HIST": "MACDのヒストグラム",
       "EARN": "個別の決算", "VOL": "個別の材料", "IND1": "業界のその日", "IND5": "業界の5日", "BIG4": "大手4社の決算", "VIX": "VIX", "CRED": "信用"}
RN = {"B": "押し目", "C": "急落の底", "M": "ミネルヴィニ", "V": "新高値V2", "*": "今の4つまとめて", "J": "上昇相場に入った日", "Z1": "一人勝ち（逆行高）", "Z2": "一人勝ち（10日）"}
CUR = ("B", "C", "M", "V")


def load(p):
    df = pd.DataFrame(json.load(open(p)))
    df = df[df["sd"] >= "2015-01-01"].copy()
    df["per"] = np.where(df["sd"] < "2022-01-01", "d", "o")
    df["yr"] = df["sd"].str[:4]
    cur = df[df["rule"].isin(CUR)].copy()
    cur["rule"] = "*"
    return pd.concat([df, cur], ignore_index=True)


def stats(df, dims):
    g = df.groupby(["rule", "per"] + list(dims)).agg(n=("ret", "count"), m=("ret", "mean"), sd=("ret", "std"), win=("ret", lambda x: (x > 0).mean()),
                                                     ny=("yr", "nunique"))
    g = g.unstack("per")
    g.columns = [f"{a}_{b}" for a, b in g.columns]
    return g


def main():
    p87, pfr, pbook, pmd = sys.argv[1:5]
    MINY = int(sys.argv[sys.argv.index("--years") + 1]) if "--years" in sys.argv else 0
    A, F = load(p87), load(pfr)
    rows = []
    n_sit = set()
    for k in (1, 2, 3):
        for dims in itertools.combinations(DIMS, k):
            ga, gf = stats(A, dims), stats(F, dims)
            j = gf.join(ga, lsuffix="_f", rsuffix="_a", how="outer")
            for idx, r in j.iterrows():
                rule, vals = idx[0], idx[1:]
                n_sit.add((dims, vals))
                rows.append((rule, dims, vals, r))
    sel = {"skip": [], "prio": [], "add": []}
    det = []
    for rule, dims, vals, r in rows:
        nf, mf, sf = r.get("n_d_f", 0) or 0, r.get("m_d_f", np.nan), r.get("sd_d_f", np.nan)
        na, ma = r.get("n_d_a", 0) or 0, r.get("m_d_a", np.nan)
        if not nf or nf < 30 or np.isnan(mf) or np.isnan(sf) or sf == 0:
            continue
        if MINY and (r.get("ny_d_f", 0) or 0) < MINY:
            continue
        t = mf / (sf / np.sqrt(nf))
        rec = (rule, list(dims), [str(v) for v in vals])
        kind = None
        if rule in CUR + ("*",):
            if t <= -3 and mf < 0 and na >= 20 and ma < 0:
                kind = "skip"
            elif t >= 3 and mf >= 0.03 and na >= 20 and ma > 0:
                kind = "prio"
        elif rule in ("J", "Z1", "Z2"):
            if t >= 3 and mf >= 0.02 and na >= 20 and ma > 0:
                kind = "add"
        if kind:
            sel[kind].append(rec)
            det.append((kind, rule, dims, vals, nf, mf, t, r.get("win_d_f"), na, ma, r.get("n_o_f"), r.get("m_o_f"), r.get("n_o_a"), r.get("m_o_a")))
    sel["meta"] = {"situations": len(n_sit), "cells": len(rows)}
    json.dump(sel, open(pbook, "w"), ensure_ascii=False)

    # 確かめる期間（2022年〜）の合図で、決まりに当たった合図と当たらない合図の1回平均（決まりは決める期間だけで作った）
    def hit(df, lst, rules):
        m = pd.Series(False, index=df.index)
        for rule, dims, vals in lst:
            q = df["rule"].isin([rule] if rule != "*" else list(CUR)) & df["rule"].isin(rules)
            for d_, v_ in zip(dims, vals):
                q &= df[d_].astype(str) == v_
            m |= q
        return m
    L = []
    w = L.append
    w(f"- 調べた状況（1〜3つの切り口の組み合わせの値）: **{len(n_sit):,}通り**。ルールごとに数えたかたまり: {len(rows):,}。")
    w(f"- 決める期間（2015〜2021年）だけで選んだ決まり: 見送る {len(sel['skip'])}、先に買う {len(sel['prio'])}、足す {len(sel['add'])}。\n")
    w("### 決まりに当たった合図の、確かめる期間（2022年〜）の1回平均（決まりを作るのには使っていない期間）\n")
    w("| 決まり | 監視銘柄 | 決める期間: 当たった n・1回平均 / 当たらない | 確かめる期間: 当たった n・1回平均 / 当たらない |")
    w("|---|---|---|---|")
    for kind, rules in (("skip", CUR), ("prio", CUR), ("add", ("J", "Z1", "Z2"))):
        for lab, D in (("87銘柄", A), ("全業種", F)):
            D0 = D[(D["rule"] != "*") & D["rule"].isin(rules)]
            h = hit(D0, sel[kind], rules)
            cells = []
            for per in ("d", "o"):
                a, b = D0[h & (D0["per"] == per)]["ret"], D0[(~h) & (D0["per"] == per)]["ret"]
                cells.append(f"{len(a)}件 {a.mean() * 100:+.2f}% / {len(b)}件 {b.mean() * 100:+.2f}%" if len(a) else f"0件 / {len(b)}件 {b.mean() * 100:+.2f}%")
            w(f"| {({'skip': '見送る', 'prio': '先に買う', 'add': '足す（新しい買い）'})[kind]} | {lab} | {cells[0]} | {cells[1]} |")
    w("\n### 選んだ決まり（決める期間の全業種の1回平均の大きさの順。上位60まで）\n")
    w("| 種類 | ルール | 状況 | 全業種 決める期間 n・平均・勝率・t | 87銘柄 決める期間 n・平均 | 全業種 確かめる期間 n・平均 | 87銘柄 確かめる期間 n・平均 |")
    w("|---|---|---|---|---|---|---|")
    det.sort(key=lambda x: (x[0], -abs(x[5])))
    f_ = lambda n, m: f"{int(n)}件 {m * 100:+.1f}%" if n and n == n and not np.isnan(m) else "—"
    for kind in ("skip", "prio", "add"):
        for x in [d for d in det if d[0] == kind][:60]:
            kind_, rule, dims, vals, nf, mf, t, win, na, ma, nof, mof, noa, moa = x
            sit = "・".join(f"{LAB[d]}={v}" for d, v in zip(dims, vals))
            w(f"| {({'skip': '見送る', 'prio': '先に買う', 'add': '足す'})[kind_]} | {RN[rule]} | {sit} | {int(nf)}件 {mf * 100:+.1f}% {win * 100:.0f}% t={t:+.1f} | {f_(na, ma)} | {f_(nof, mof)} | {f_(noa, moa)} |")
    open(pmd, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L[:12]))


if __name__ == "__main__":
    main()
