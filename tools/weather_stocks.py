#!/usr/bin/env python3
"""相場天気（晴れ・曇り・雨・雷雨）と同じ向きに動く監視銘柄の調査（当日）と、天気の後の値動き（翌日・3日・5日）

使い方:
  tools/backtest_lib.py fetch など（監視銘柄・^GSPC・^NDX・^VIX・^TNX の日足がキャッシュにあること）
  tools/weather_stocks.py run [--out FILE]

天気の決め方（数値のルール。`相場天気予報.txt` 手順W-2の目安を、これまでのClaudeの判定13日分に合わせて数値にしたもの）:
  r = S&P500指数の騰落率、q = NASDAQ100指数の騰落率、v = VIXの変化率、b = 米10年債利回りの変化（bp）
  雷雨: r ≦ −2%、または VIX ≧ 30 かつ v ≧ +15%
  雨  : r ≦ −0.5%、または r < +0.1% かつ v ≧ +3% かつ b ≧ +3bp（金利と恐怖指数がそろって上がった日）
  晴れ: r・q の大きい方 ≧ +0.4% かつ r > −0.3% かつ v < +5%
  曇り: それ以外
  Fear&Greed・日経VIは過去のデータがないため使わない。毎朝の天気予報（Claudeの総合判断）とは別物。

「同じように動く」: 晴れの日に上がった・雨と雷雨の日に下がった日の割合（曇りの日は数えない）。
天気予報の日付（日本時間の朝）は、その前の米国の取引日の値動きを指す（例: 2026-09-28 の予報 = 9/25 の値動き）。
数値と事実だけで、売買の判断はしない。NotebookLMは使わない。
"""
import argparse
import datetime as dt
import os
import re
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backtest_lib import DEFAULT_CACHE, load_prices
from backtest_theme import load_watchlist

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "新分析ツール", "バックテスト結果", "相場天気と同じように動く銘柄.md")
WEATHER_BRANCH = "origin/claude/ecstatic-tesla-660dhs"   # 毎朝の天気予報が保存されるRoutine用ブランチ
DESIGN_END, VERIFY_START, START = "2021-12-31", "2022-01-01", "2015-01-01"
KINDS = ("晴れ", "曇り", "雨", "雷雨")


def weather(r, q, v, b, vix):
    if r <= -0.02 or (vix >= 30 and v >= 0.15):
        return "雷雨"
    if r <= -0.005 or (r < 0.001 and v >= 0.03 and b >= 3):
        return "雨"
    if max(r, q) >= 0.004 and r > -0.003 and v < 0.05:
        return "晴れ"
    return "曇り"


def market(cache):
    """{日付: (天気, r, q, v, b, VIX)}"""
    g = {s: load_prices(cache, s) for s in ("^GSPC", "^NDX", "^VIX", "^TNX")}
    pos = {s: {d: i for i, d in enumerate(v["date"])} for s, v in g.items()}
    out = {}
    for i in range(1, len(g["^GSPC"]["date"])):
        d = g["^GSPC"]["date"][i]
        if not all(d in pos[s] and pos[s][d] > 0 for s in g):
            continue
        ch = lambda s: g[s]["c"][pos[s][d]] / g[s]["c"][pos[s][d] - 1] - 1
        b = (g["^TNX"]["c"][pos["^TNX"][d]] - g["^TNX"]["c"][pos["^TNX"][d] - 1]) * 100
        vix = g["^VIX"]["c"][pos["^VIX"][d]]
        r, q, v = ch("^GSPC"), ch("^NDX"), ch("^VIX")
        out[d] = (weather(r, q, v, b, vix), r, q, v, b, vix)
    return out


def actual_forecasts():
    """毎朝の天気予報（Claudeの判定）。[(予報の日付, 天気の先頭の語, 天気の全文)]"""
    def git(*a):
        return subprocess.run(["git", "-C", ROOT, "-c", "core.quotepath=false", *a], capture_output=True, text=True).stdout
    files = [f for f in git("ls-tree", "-r", "--name-only", WEATHER_BRANCH).split() if f.startswith("相場天気予報/") and f.endswith(".md")]
    out = []
    for f in sorted(files):
        m = re.search(r"^weather: (.*)$", git("show", f"{WEATHER_BRANCH}:{f}"), re.M)
        if m:
            full = m.group(1).strip()
            out.append((os.path.basename(f)[:10], next((k for k in ("雷雨", "晴れ", "曇り", "雨") if full.startswith(k)), full), full))
    return out


def pc(x, d=0):
    return "—" if x is None or not np.isfinite(x) else f"{x * 100:.{d}f}%"


def sg(x, d=1):
    return "—" if x is None or not np.isfinite(x) else f"{x * 100:+.{d}f}%"


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default=OUT)
    a = ap.parse_args()
    mk = market(a.cache)
    mdays = sorted(mk)
    wl = load_watchlist()
    fc = actual_forecasts()
    fc_day = {}
    for rd, k, full in fc:
        prev = [d for d in mdays if d < rd]
        if prev:
            fc_day[prev[-1]] = (rd, k, full)

    # 銘柄ごとの当日・翌日以降の騰落率
    rows = {}
    for sym in wl:
        d = load_prices(a.cache, sym)
        if not d:
            continue
        c = d["c"]
        rec = []
        for i in range(1, len(c)):
            day = d["date"][i]
            if day < START or day not in mk:
                continue
            fut = {h: (c[i + h] / c[i] - 1 if i + h < len(c) else np.nan) for h in (1, 3, 5)}
            rec.append((day, mk[day][0], c[i] / c[i - 1] - 1, fut[1], fut[3], fut[5]))
        rows[sym] = rec
    last = max(r[-1][0] for r in rows.values() if r)

    def agg(rec, per):
        sel = [x for x in rec if per(x[0])]
        res = {}
        for k in KINDS:
            xs = [x for x in sel if x[1] == k]
            same = np.array([x[2] for x in xs])
            res[k] = {"n": len(xs), "up": (same > 0).mean() if len(xs) else np.nan, "mean": same.mean() if len(xs) else np.nan}
            for h, j in ((1, 3), (3, 4), (5, 5)):
                f = np.array([x[j] for x in xs if np.isfinite(x[j])])
                res[k][f"up{h}"] = (f > 0).mean() if len(f) else np.nan
                res[k][f"mean{h}"] = f.mean() if len(f) else np.nan
        hit = [(x[2] > 0) if x[1] == "晴れ" else (x[2] < 0) for x in sel if x[1] in ("晴れ", "雨", "雷雨")]
        res["match"] = np.mean(hit) if hit else np.nan
        res["match_n"] = len(hit)
        return res

    P = {"全期間": lambda d: True, "設計": lambda d: d <= DESIGN_END, "確認": lambda d: d >= VERIFY_START}
    st = {sym: {p: agg(rec, f) for p, f in P.items()} for sym, rec in rows.items()}
    # 実際の天気予報（Claudeの判定）の日
    act = {}
    for sym, rec in rows.items():
        by = {x[0]: x for x in rec}
        hit, tot = 0, 0
        for day, (rd, k, _) in fc_day.items():
            if day in by and k in ("晴れ", "雨", "雷雨"):
                tot += 1
                hit += (by[day][2] > 0) if k == "晴れ" else (by[day][2] < 0)
        act[sym] = (hit, tot)

    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: 相場天気と同じように動く銘柄\n" f"updated: {dt.date.today()}\nscript: tools/weather_stocks.py\n---\n")
    w("# 相場天気（晴れ・曇り・雨・雷雨）と同じように動く監視銘柄、天気の後の値動き\n")
    w(__doc__.split("\n", 4)[4].split("数値と事実だけで")[0].strip() + "\n")
    w(f"対象: 監視銘柄（今の{len(wl)}銘柄）。期間 2015-01〜{last}（上場の後から）。設計期間 2015〜2021年 / 確認期間 2022年〜。"
      "監視銘柄は今の時点で選んでいるため、上がった割合などの水準には後知恵が入る（銘柄どうしの比べ方には影響が小さい）。\n")

    # 1. ルールとClaudeの判定の一致
    w("## 1. 数値のルールと、毎朝の天気予報（Claudeの判定）の一致\n")
    w("| 予報の日 | 値動きの日 | Claudeの判定 | ルール | S&P500 | NASDAQ100 | VIX（変化） | 10年債（変化） |")
    w("|---|---|---|---|---|---|---|---|")
    agree = 0
    for day, (rd, k, full) in sorted(fc_day.items(), key=lambda x: x[1][0]):
        wk, rr, q, v, b, vix = mk[day]
        agree += wk == k
        w(f"| {rd} | {day} | {full} | {wk}{'' if wk == k else ' ✗'} | {sg(rr, 2)} | {sg(q, 2)} | {vix:.1f}（{sg(v)}） | {b:+.1f}bp |")
    w(f"\n一致 {agree}/{len(fc_day)}日。ルールの数値はこの{len(fc_day)}日に合わせて決めたので、一致は独立した確認ではない。"
      "Claudeの判定は金利やニュースも見ているため、ルールと合わない日がある。\n")
    cnt = {p: {k: sum(1 for d in mdays if f(d) and d >= START and mk[d][0] == k) for k in KINDS} for p, f in P.items()}
    w("天気の日数（2015年〜）: " + "、".join(f"{k} {cnt['全期間'][k]}日" for k in KINDS)
      + f"（確認期間: " + "、".join(f"{k} {cnt['確認'][k]}日" for k in KINDS) + "）\n")

    # 2. 監視銘柄全体: 当日と、天気の後
    w("## 2. 天気ごとの値動き（監視銘柄の全体）\n")
    w("| 天気 | 期間 | 当日 上がった割合 / 平均 | 翌日 上がった割合 / 平均 | 3日後 | 5日後 |")
    w("|---|---|---|---|---|---|")
    for k in KINDS:
        for p in ("設計", "確認"):
            xs = [x for rec in rows.values() for x in rec if x[1] == k and P[p](x[0])]
            if not xs:
                continue
            A = np.array([x[2:] for x in xs], float)
            cells = []
            for j in range(4):
                col = A[:, j][np.isfinite(A[:, j])]
                cells.append(f"{pc((col > 0).mean())} / {sg(col.mean(), 2)}")
            w(f"| {k} | {p} | " + " | ".join(cells) + " |")
    allx = np.array([x[2:] for rec in rows.values() for x in rec if P['確認'](x[0])], float)
    w(f"\n参考（確認期間の全日）: 当日 {pc((allx[:, 0] > 0).mean())} / {sg(allx[:, 0].mean(), 2)}、"
      f"5日後 {pc((allx[:, 3][np.isfinite(allx[:, 3])] > 0).mean())} / {sg(np.nanmean(allx[:, 3]), 2)}\n")

    # 3. 銘柄ごと
    syms = sorted(st, key=lambda s: -(st[s]["確認"]["match"] if np.isfinite(st[s]["確認"]["match"]) else -1))
    dm = np.array([st[s]["設計"]["match"] for s in syms], float)
    vm = np.array([st[s]["確認"]["match"] for s in syms], float)
    ok = np.isfinite(dm) & np.isfinite(vm)
    rank = lambda x: np.argsort(np.argsort(x))
    rho = np.corrcoef(rank(dm[ok]), rank(vm[ok]))[0, 1] if ok.sum() > 5 else np.nan
    w("## 3. 銘柄ごと: 天気と同じように動く割合（当日）\n")
    w(f"同じように動く割合 = 晴れの日に上がった＋雨・雷雨の日に下がった日 ÷ 晴れ・雨・雷雨の日。"
      f"設計期間と確認期間の順位の相関（スピアマン）: **{rho:.2f}**（{ok.sum()}銘柄。1に近いほど、同じ銘柄が毎回よく天気に沿って動く）。"
      "直近13日は毎朝の天気予報（Claudeの判定）との一致（晴れ・雨の日だけ）。\n")
    w("| 銘柄 | グループ | 同じように動く割合 確認（設計） | 晴れの日: 上がった割合 / 平均 | 雨の日: 下がった割合 / 平均 | 雷雨の日: 平均 | 曇りの日: 平均 | "
      "直近の予報との一致 | 晴れの後5日 平均 | 雨の後5日 平均 | 確認期間の日数 |")
    w("|---|---|---|---|---|---|---|---|---|---|---|")
    for s in syms:
        v, d0 = st[s]["確認"], st[s]["設計"]
        h, t = act[s]
        w(f"| {s} | {wl[s]} | **{pc(v['match'])}**（{pc(d0['match'])}） | {pc(v['晴れ']['up'])} / {sg(v['晴れ']['mean'])} | "
          f"{pc(1 - v['雨']['up']) if np.isfinite(v['雨']['up']) else '—'} / {sg(v['雨']['mean'])} | {sg(v['雷雨']['mean'])} | {sg(v['曇り']['mean'])} | "
          f"{h}/{t} | {sg(v['晴れ']['mean5'])} | {sg(v['雨']['mean5'])} | {v['match_n']} |")

    # 4. グループごと
    w("\n## 4. グループごと（確認期間、銘柄の平均）\n")
    w("| グループ | 銘柄数 | 同じように動く割合 | 晴れの日 平均 | 雨の日 平均 | 雷雨の日 平均 | 雨の後5日 平均 |")
    w("|---|---|---|---|---|---|---|")
    for gname in dict.fromkeys(wl.values()):
        ss = [s for s in st if wl[s] == gname and np.isfinite(st[s]["確認"]["match"])]
        if not ss:
            continue
        m = lambda f: np.nanmean([f(st[s]["確認"]) for s in ss])
        w(f"| {gname} | {len(ss)} | {pc(m(lambda v: v['match']))} | {sg(m(lambda v: v['晴れ']['mean']))} | {sg(m(lambda v: v['雨']['mean']))} | "
          f"{sg(m(lambda v: v['雷雨']['mean']))} | {sg(m(lambda v: v['雨']['mean5']))} |")

    # 5. 直近の日（予報があった日）の当日の結果
    w("\n## 5. 直近の天気予報の日の結果（当日の騰落率）\n")
    w("天気と逆に動いた銘柄（晴れなのに下げた・雨なのに上げた）を挙げる。\n")
    w("| 値動きの日 | Claudeの判定 | 天気どおり | 逆に動いた銘柄（騰落率） |")
    w("|---|---|---|---|")
    for day, (rd, k, full) in sorted(fc_day.items()):
        moves = [(s, x[2]) for s, rec in rows.items() for x in rec if x[0] == day]
        if k in ("晴れ", "雨", "雷雨"):
            good = [m for m in moves if (m[1] > 0) == (k == "晴れ")]
            bad = sorted([m for m in moves if (m[1] > 0) != (k == "晴れ")], key=lambda m: -abs(m[1]))
            w(f"| {day} | {k} | {len(good)}/{len(moves)} | " + "、".join(f"{s} {sg(r_)}" for s, r_ in bad[:12])
              + (f" ほか{len(bad) - 12}" if len(bad) > 12 else "") + " |")
        else:
            up = sum(1 for m in moves if m[1] > 0)
            w(f"| {day} | {k} | 上げ {up}・下げ {len(moves) - up} | — |")

    w("\n## 注意\n")
    w("- 天気のルールの数値は、毎朝の天気予報13日分（2026-09-21〜）に合わせてClaudeが置いたもの。過去の毎朝の判定そのものではない。")
    w("- 「同じように動く割合」が高い銘柄は、市場全体と一緒に動きやすい（いわゆるベータが大きい・指数の比重が大きい）銘柄。予測ではなく、当日の動き方の性質。")
    w("- この結果は天気予報（Claudeの相場観）とは別に扱い、NotebookLMへのプロンプトや手順6の総合見解には使わない（CLAUDE.md）。")
    w("- 数値と過去の統計だけで、個別銘柄の売買の判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(a.out)


if __name__ == "__main__":
    main()
