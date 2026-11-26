#!/usr/bin/env python3
"""局面×指標の組み合わせを「年率が上がる見方」で使い直す（2026-11-26 ユーザーの指示「RSIやMACD…デッドクロス・ゴールデンクロス・出来高などで様々な組み合わせで検証したと思います。
その検証結果から今回のような年率が上がる見方をしたときに採用できそうな良い合図や合図の組み合わせが見つかるのではないですか？検証してください」）。

2026-11-13 の tools/combo_search.py は、状況で「見送る・先に買う・足す」を決め、2022年〜で逆になった。今回は、年率が上がった形（強さの条件＋待っている現金をQQQ）の上で、
状況を次の3つに使う（どれも2015〜2021年＝決める期間の成績だけで決め、2022年〜は確かめるのに使う）:
  boost: 良い状況の合図は2倍ETFで買う（S&P500の局面にかかわらず）。全業種 n≧30・1回平均≧+3%・t≧3・損切り≦20%、87銘柄 n≧20・平均≧+2%・損切り≦20%
  admit: 強さの条件で止める87銘柄の合図（弱い87銘柄）でも、良い状況なら買う。87銘柄の弱い合図 n≧30・平均≧+3%・t≧3・損切り≦20%、全業種の同じ状況 n≧20・平均>0
  skip2: 強さの条件の上で買う合図（強い銘柄とテーマの外）のうち、悪い状況は見送る。全業種の強い合図 n≧30・t≦−3・平均<0、87銘柄 n≧20・平均<0
どれも、決める期間の合図が3暦年以上にまたがる状況だけ使う（同じ出来事の合図が一緒に動くため。2026-11-13 の参考の厳しい形）。
切り口: combo_search.py の14に、GC（50日線と200日線のゴールデンクロス・デッドクロス）・VR（合図の日の出来高÷50日平均）・ST（強さの条件）を足した17。1〜3つの組み合わせ。
入力: backtest_retest.py の OPT_FEATDUMP（OPT_REF＝今のルール）の87銘柄・全業種。出力: OPT_BOOK に渡す決まりのjsonと、確かめる期間の成績のmd。
使い方: tools/combo_boost.py <87のjson> <全業種のjson> <決まりのjson> <結果のmd>
数値の事実だけで、Claudeの売買判断は含まない。
"""
import itertools
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import combo_search as cs

DIMS = cs.DIMS + ["GC", "VR", "ST"]
LAB = {**cs.LAB, "GC": "50日線と200日線", "VR": "出来高", "ST": "強さの条件"}
RN = cs.RN
CUR = cs.CUR
MINY = 3


def load(p):
    df = pd.DataFrame(json.load(open(p)))
    df = df[(df["sd"] >= "2015-01-01") & (df["src"] == "今") & df["rule"].isin(CUR)].copy()
    df["per"] = np.where(df["sd"] < "2022-01-01", "d", "o")
    df["yr"] = df["sd"].str[:4]
    df["stp"] = df["stopped"].astype(float)
    for d in DIMS:
        df[d] = df[d].astype(str)
    cur = df.copy()
    cur["rule"] = "*"
    return pd.concat([df, cur], ignore_index=True)


def stats(df, dims):
    if df.empty:
        return pd.DataFrame()
    g = df.groupby(["rule", "per"] + list(dims)).agg(n=("ret", "count"), m=("ret", "mean"), sd=("ret", "std"), stp=("stp", "mean"), ny=("yr", "nunique"))
    g = g.unstack("per")
    g.columns = [f"{a}_{b}" for a, b in g.columns]
    return g


def tval(m, sd, n):
    return m / (sd / np.sqrt(n)) if n and sd and sd == sd and sd > 0 else np.nan


def search(P, Q, dims_all, crit):
    """P: 決める側（主）、Q: 確かめの向きを見る側。crit(r) が True の状況を返す"""
    out = []
    for k in (1, 2, 3):
        for dims in itertools.combinations(dims_all, k):
            gp, gq = stats(P, dims), stats(Q, dims)
            if gp.empty:
                continue
            j = gp.join(gq, lsuffix="_p", rsuffix="_q", how="left")
            for idx, r in j.iterrows():
                if crit(r):
                    out.append((idx[0], list(dims), [str(v) for v in idx[1:]], r))
    return out


def g(r, k, default=0):
    v = r.get(k, default)
    return default if v is None or (isinstance(v, float) and np.isnan(v)) else v


def main():
    p87, pall, pbook, pmd = sys.argv[1:5]
    A, F = load(p87), load(pall)
    # boost: 今のルールの合図全部（全業種で決め、87銘柄で向きを見る）
    def c_boost(r):
        n, m, sd = g(r, "n_d_p"), g(r, "m_d_p", np.nan), g(r, "sd_d_p", np.nan)
        return (n >= 30 and m >= 0.03 and tval(m, sd, n) >= 3 and g(r, "stp_d_p", 1) <= 0.20 and g(r, "ny_d_p") >= MINY
                and g(r, "n_d_q") >= 20 and g(r, "m_d_q", -1) >= 0.02 and g(r, "stp_d_q", 1) <= 0.20)
    boost = search(F, A, DIMS, c_boost)
    # admit: 87銘柄の弱い合図（テーマの外でない）で決め、全業種の同じ状況（合図全部）で向きを見る
    Aw = A[(A["ST"] == "弱い") & (A["x"] != "out")]
    dims_w = [d for d in DIMS if d != "ST"]
    def c_admit(r):
        n, m, sd = g(r, "n_d_p"), g(r, "m_d_p", np.nan), g(r, "sd_d_p", np.nan)
        return (n >= 30 and m >= 0.03 and tval(m, sd, n) >= 3 and g(r, "stp_d_p", 1) <= 0.20 and g(r, "ny_d_p") >= MINY
                and g(r, "n_d_q") >= 20 and g(r, "m_d_q", -1) > 0)
    admit = search(Aw, F, dims_w, c_admit)
    # skip2: 強さの条件の上で買う合図（全業種は強い合図、87銘柄は強い合図とテーマの外）
    Fs = F[F["ST"] != "弱い"]
    As = A[(A["ST"] != "弱い") | (A["x"] == "out")]
    def c_skip(r):
        n, m, sd = g(r, "n_d_p"), g(r, "m_d_p", np.nan), g(r, "sd_d_p", np.nan)
        return (n >= 30 and m < 0 and tval(m, sd, n) <= -3 and g(r, "ny_d_p") >= MINY and g(r, "n_d_q") >= 20 and g(r, "m_d_q", 1) < 0)
    skip2 = search(Fs, As, dims_w, c_skip)
    book = {k: [(r, d, v) for r, d, v, _ in lst] for k, lst in (("boost", boost), ("admit", admit), ("skip2", skip2))}
    json.dump(book, open(pbook, "w"), ensure_ascii=False)

    def hit(df, lst):
        mk = pd.Series(False, index=df.index)
        for rule, dims, vals in lst:
            q = df["rule"].isin(list(CUR) if rule == "*" else [rule])
            for d_, v_ in zip(dims, vals):
                q &= df[d_] == v_
            mk |= q
        return mk
    L = []
    w = L.append
    w(f"- 切り口17（{'・'.join(LAB[d] for d in DIMS)}）の1〜3つの組み合わせ。決める期間（2015〜2021年）だけで選んだ状況: "
      f"2倍ETFで買う {len(boost)}、弱い87銘柄でも買う {len(admit)}、見送る {len(skip2)}。\n")
    w("### 選んだ状況に当たった合図の成績（決める期間と、決めるのに使っていない確かめる期間 2022年〜。1回平均・15%の損切りの割合）\n")
    w("| 決まり | 合図 | 決める期間: 当たった / 当たらない | 確かめる期間: 当たった / 当たらない |")
    w("|---|---|---|---|")
    for kind, lab, sets in (("boost", "良い状況は2倍ETF", (("87銘柄（全部）", A), ("全業種（全部）", F))),
                            ("admit", "弱い87銘柄でも買う", (("87銘柄の弱い合図", Aw), ("全業種の弱い合図", F[F["ST"] == "弱い"]))),
                            ("skip2", "悪い状況は見送る", (("87銘柄の強い合図とテーマの外", As), ("全業種の強い合図", Fs)))):
        for nm, D in sets:
            D0 = D[D["rule"] != "*"]
            h = hit(D0, book[kind])
            cells = []
            for per in ("d", "o"):
                a, b = D0[h & (D0["per"] == per)], D0[(~h) & (D0["per"] == per)]
                cells.append((f"{len(a)}件 {a['ret'].mean() * 100:+.2f}%・{a['stp'].mean() * 100:.0f}%" if len(a) else "0件")
                             + f" / {len(b)}件 {b['ret'].mean() * 100:+.2f}%・{b['stp'].mean() * 100:.0f}%")
            w(f"| {lab} | {nm} | {cells[0]} | {cells[1]} |")
    for kind, lab, lst in (("boost", "良い状況は2倍ETF", boost), ("admit", "弱い87銘柄でも買う", admit), ("skip2", "悪い状況は見送る", skip2)):
        w(f"\n### {lab}（決める期間の1回平均の大きさの順、上位40）\n")
        w("| ルール | 状況 | 決める期間 n・平均・損切り・t・年の数 | 向きを見た側 決める期間 n・平均 | 確かめる期間 n・平均 | 向きを見た側 確かめる期間 n・平均 |")
        w("|---|---|---|---|---|---|")
        for rule, dims, vals, r in sorted(lst, key=lambda x: -abs(g(x[3], "m_d_p")))[:40]:
            sit = "・".join(f"{LAB[d]}={v}" for d, v in zip(dims, vals))
            fm = lambda n, m: f"{int(n)}件 {m * 100:+.1f}%" if n and m == m else "—"
            w(f"| {RN[rule]} | {sit} | {int(g(r, 'n_d_p'))}件 {g(r, 'm_d_p') * 100:+.1f}%・{g(r, 'stp_d_p') * 100:.0f}%・t={tval(g(r, 'm_d_p'), g(r, 'sd_d_p'), g(r, 'n_d_p')):+.1f}・{int(g(r, 'ny_d_p'))}年 | "
              f"{fm(g(r, 'n_d_q'), g(r, 'm_d_q', np.nan))} | {fm(g(r, 'n_o_p'), g(r, 'm_o_p', np.nan))} | {fm(g(r, 'n_o_q'), g(r, 'm_o_q', np.nan))} |")
    w("\n- この結果は数値を条件どおりに計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    open(pmd, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L[:14]))


if __name__ == "__main__":
    main()
