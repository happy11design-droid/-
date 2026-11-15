#!/usr/bin/env python3
"""手1の1段目（Fableの提案 `新分析ツール/Fableの提案_未解決の課題_2026-11-15.md` 3節、2026-11-15）:
押し目（B）・急落の底（C）の合図を「下げの理由」で4つに分け、区分ごとの成績を数える（資金の計算はしない）。

区分（合図の日 t の引けまでに分かることだけで決める。t−4〜t の5取引日の窓 W）:
  r_i(d) = 銘柄 i の日 d の騰落率、g_i(d) = 同じグループの i を除いた銘柄の平均（3銘柄に満たなければSOX）、e_i(d) = r_i(d) − g_i(d)
  決算の反応日の候補 = 発表日（取引日でなければ次の取引日）とその次の取引日（時刻が分からないため両方。翌日の値動きで決めない）
  O1 自社の決算で下げた: W の中に自社の反応日の候補 d があり e_i(d) ≦ −a
  O2 自社だけ下げた: O1でなく、W の中に e_i(d) ≦ −b の日がある
  P  同業の決算の巻き添え: O1・O2でなく、W の中に同じグループの別の銘柄 j の反応日の候補 d があり、e_j(d) ≦ −c かつ r_i(d) ≦ −2%
  M  全体の下げ: 残り
  （a, b, c）＝（5, 7, 7）%を中心に、（4, 6, 6）と（6, 8, 8）
グループ: 87銘柄はテーマの7グループ（`テーマ監視銘柄.md`。テーマの外の銘柄は業種）、全業種は業種（`業種一覧.json`）。
合図: `~/.cache/stock_backtest/results/combo_feat_87.json`・`combo_feat_free.json`（今のルールの合図、src="今"、rule が B・C）。
でたらめ: 同じ合図の日・同じルールの合図の中で区分のラベルを入れ替える（1,000回）。P の1回平均 − O1 の1回平均が、その上位5%に入るか。

使い方: python3 tools/drop_cause_check.py [--out FILE] [--perm 1000]
"""
import argparse
import bisect
import json
import os
import random
import re
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backtest_lib import DEFAULT_CACHE, load_prices  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
VARIANTS = [(0.05, 0.07, 0.07), (0.04, 0.06, 0.06), (0.06, 0.08, 0.08)]
CLASSES = ("P", "M", "O2", "O1")


def theme_groups():
    t = open(os.path.join(ROOT, "新分析ツール", "テーマ監視銘柄.md"), encoding="utf-8").read()
    groups, cur = {}, None
    for line in t.split("\n"):
        m = re.match(r"^## (.+?)（\d+）", line)
        if m and "対象外" not in line:
            cur = m.group(1)
            continue
        if line.startswith("## "):
            cur = None
        if cur and line.startswith("| ") and not line.startswith("| ティッカー") and not line.startswith("|---"):
            sym = line.split("|")[1].strip()
            if re.match(r"^[A-Z.\-]+$", sym):
                groups[sym] = cur
    return groups


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--perm", type=int, default=1000)
    a = ap.parse_args()
    industry = json.load(open(os.path.join(ROOT, "新分析ツール", "業種一覧.json"), encoding="utf-8"))
    theme = theme_groups()
    earn = json.load(open(os.path.join(DEFAULT_CACHE, "earnings.json")))
    sox = {r[0]: r[2] for r in json.load(open(os.path.join(DEFAULT_CACHE, "long/index/^SOX.json")))}
    sox_d = sorted(sox)
    sox_r = {sox_d[k]: sox[sox_d[k]] / sox[sox_d[k - 1]] - 1 for k in range(1, len(sox_d))}
    # 騰落率
    R, DATES = {}, {}
    syms = set(industry) | set(theme)
    for s in sorted(syms):
        p = load_prices(DEFAULT_CACHE, s)
        if not p or len(p["c"]) < 30:
            continue
        c, d = p["c"], p["date"]
        R[s] = {d[k]: c[k] / c[k - 1] - 1 for k in range(1, len(c)) if c[k - 1]}
        DATES[s] = d
    print("株価", len(R), file=sys.stderr)

    def group_of(s, watch):
        if watch == "87" and s in theme:
            return ("T", theme[s])
        return ("I", industry.get(s))

    # グループごと・日ごとの騰落率の合計と数
    G = {}
    for s in R:
        for watch in ("87", "free"):
            g = group_of(s, watch)
            if g[1] is None:
                continue
            if watch == "87" and g[0] == "I" and s in theme:
                continue
            G.setdefault(g, {})
        g_t = ("T", theme[s]) if s in theme else None
        g_i = ("I", industry.get(s)) if industry.get(s) else None
        for g in (g_t, g_i):
            if g is None:
                continue
            tab = G.setdefault(g, {})
            for d, r in R[s].items():
                x = tab.setdefault(d, [0.0, 0])
                x[0] += r
                x[1] += 1
    members = {}
    for s in R:
        if s in theme:
            members.setdefault(("T", theme[s]), []).append(s)
        if industry.get(s):
            members.setdefault(("I", industry[s]), []).append(s)

    def g_ex(s, g, d):
        tab = G.get(g, {}).get(d)
        r = R[s].get(d)
        if tab and r is not None and tab[1] - 1 >= 3:
            return (tab[0] - r) / (tab[1] - 1)
        return sox_r.get(d, 0.0)

    def e_of(s, g, d):
        r = R[s].get(d)
        return None if r is None else r - g_ex(s, g, d)

    # 決算の反応日の候補
    EC = {}
    for s, evs in earn.items():
        if s not in DATES:
            continue
        ds = DATES[s]
        cs = set()
        for day, _tm in evs:
            k = bisect.bisect_left(ds, day)
            if k < len(ds):
                cs.add(ds[k])
                if k + 1 < len(ds):
                    cs.add(ds[k + 1])
        EC[s] = cs

    out = []
    w = out.append
    summary = {}
    for watch in ("87", "free"):
        rows = [r for r in json.load(open(os.path.join(DEFAULT_CACHE, f"results/combo_feat_{watch}.json")))
                if r["src"] == "今" and r["rule"] in ("B", "C") and r["sd"] >= "2015-01-01" and r["sym"] in R]
        labs = {v: [] for v in VARIANTS}
        for r in rows:
            s, sd = r["sym"], r["sd"]
            ds = DATES[s]
            k = bisect.bisect_right(ds, sd) - 1
            W = ds[max(0, k - 4):k + 1]
            g = ("T", theme[s]) if (watch == "87" and s in theme) else ("I", industry.get(s))
            peers = [j for j in members.get(g, []) if j != s]
            own_e = {d: e_of(s, g, d) for d in W}
            for v in VARIANTS:
                aa, bb, cc = v
                lab = "M"
                if any(d in EC.get(s, ()) and own_e[d] is not None and own_e[d] <= -aa for d in W):
                    lab = "O1"
                elif any(own_e[d] is not None and own_e[d] <= -bb for d in W):
                    lab = "O2"
                else:
                    for d in W:
                        ri = R[s].get(d)
                        if ri is None or ri > -0.02:
                            continue
                        hit = False
                        for j in peers:
                            if d in EC.get(j, ()):
                                ej = e_of(j, g, d)
                                if ej is not None and ej <= -cc:
                                    hit = True
                                    break
                        if hit:
                            lab = "P"
                            break
                labs[v].append(lab)
        summary[watch] = (rows, labs)

    def stats(rs):
        if not rs:
            return (0, None, None, None)
        return (len(rs), st.mean(r["ret"] for r in rs), sum(1 for r in rs if r["ret"] > 0) / len(rs), sum(1 for r in rs if r["stopped"]) / len(rs))

    def diff_po(rows, lab, filt=lambda r: True):
        p = [r["ret"] for r, l in zip(rows, lab) if l == "P" and filt(r)]
        o = [r["ret"] for r, l in zip(rows, lab) if l == "O1" and filt(r)]
        if not p or not o:
            return None
        return st.mean(p) - st.mean(o)

    def perm_p(rows, lab, n, seed=0):
        rnd = random.Random(seed)
        obs = diff_po(rows, lab)
        if obs is None:
            return None, None
        cells = {}
        for i, r in enumerate(rows):
            cells.setdefault((r["sd"], r["rule"]), []).append(i)
        ge = 0
        for _ in range(n):
            lab2 = list(lab)
            for idxs in cells.values():
                if len(idxs) > 1:
                    vals = [lab[i] for i in idxs]
                    rnd.shuffle(vals)
                    for i, v in zip(idxs, vals):
                        lab2[i] = v
            dd = diff_po(rows, lab2)
            if dd is not None and dd >= obs:
                ge += 1
        return obs, ge / n

    W_ = {"87": "87銘柄", "free": "全業種（後知恵なし）"}
    verdict = {}
    for watch, (rows, labs) in summary.items():
        w(f"\n## {W_[watch]}（押し目・急落の底の合図 {len(rows)}件、2015年〜）\n")
        for v in VARIANTS:
            lab = labs[v]
            w(f"\n### 区分の境目（自社の決算 −{v[0]:.0%}・自社だけ −{v[1]:.0%}・同業の決算 −{v[2]:.0%}）\n")
            w("| 区分 | 期間 | 件数 | 1回平均 | 勝率 | 損切りの割合 |")
            w("|---|---|---|---|---|---|")
            for c in CLASSES:
                for per, lo, hi in (("全期間", "2015", "2027"), ("2015〜2020年（決める）", "2015", "2021"), ("2021〜2026年（確かめる）", "2021", "2027")):
                    rs = [r for r, l in zip(rows, lab) if l == c and lo <= r["sd"][:4] < hi]
                    n, m, wr, sr = stats(rs)
                    w(f"| {c} | {per} | {n} | {'' if m is None else f'{m:+.2%}'} | {'' if wr is None else f'{wr:.0%}'} | {'' if sr is None else f'{sr:.0%}'} |")
            # ルールごと
            for rule in ("B", "C"):
                parts = []
                for c in CLASSES:
                    n, m, _, sr = stats([r for r, l in zip(rows, lab) if l == c and r["rule"] == rule])
                    parts.append(f"{c} {n}件 {'' if m is None else f'{m:+.2%}'}")
                w(f"- {'押し目' if rule == 'B' else '急落の底'}: " + "、".join(parts))
            d1 = diff_po(rows, lab, lambda r: r["sd"] < "2021")
            d2 = diff_po(rows, lab, lambda r: r["sd"] >= "2021")
            dcut = diff_po(rows, lab, lambda r: r["sd"] <= "2026-08-31")
            ys = sorted({r["sd"][:4] for r in rows})
            yd = [diff_po(rows, lab, lambda r, y=y: r["sd"][:4] == y) for y in ys]
            ypos = sum(1 for x in yd if x is not None and x > 0)
            yn = sum(1 for x in yd if x is not None)
            ev = [diff_po(rows, lab, lambda r: int(r["sd"][:4]) % 2 == 0), diff_po(rows, lab, lambda r: int(r["sd"][:4]) % 2 == 1)]
            obs, pp = perm_p(rows, lab, a.perm) if v == VARIANTS[0] else (diff_po(rows, lab), None)
            fmt = lambda x: "—" if x is None else f"{x:+.2%}"  # noqa: E731
            w(f"- P − O1 の1回平均の差: 全期間 {fmt(obs)}、2015〜2020年 {fmt(d1)}、2021〜2026年 {fmt(d2)}、2026-08-31まで {fmt(dcut)}、偶数年 {fmt(ev[0])}・奇数年 {fmt(ev[1])}。"
              f"年ごとに P＞O1 だった年 {ypos}/{yn}" + (f"。でたらめ（同じ日・同じルールの中で入れ替え、{a.perm}回）で本物以上だった割合 {pp:.1%}" if pp is not None else ""))
            verdict[(watch, v)] = dict(d1=d1, d2=d2, dcut=dcut, ypos=ypos, yn=yn, pp=pp, obs=obs)
    # 通す目安
    w("\n## 通す目安（提案の3-4）\n")
    v0 = VARIANTS[0]
    c1 = all(verdict[(wt, v0)]["d1"] is not None and verdict[(wt, v0)]["d1"] >= 0.02 and verdict[(wt, v0)]["d2"] is not None and verdict[(wt, v0)]["d2"] >= 0.02 for wt in ("87", "free"))
    c2 = all(verdict[(wt, v0)]["pp"] is not None and verdict[(wt, v0)]["pp"] <= 0.05 for wt in ("87", "free"))
    c3 = all(verdict[(wt, v0)]["ypos"] >= 8 for wt in ("87", "free"))
    c4 = all(verdict[(wt, v)]["obs"] is not None and verdict[(wt, v)]["obs"] > 0 for wt in ("87", "free") for v in VARIANTS)
    c5 = all(verdict[(wt, v0)]["dcut"] is not None and verdict[(wt, v0)]["dcut"] > 0 for wt in ("87", "free"))
    for lab_, ok in (("① 両方の監視銘柄・両方の期間で P − O1 が +2pt 以上", c1), ("② でたらめの上位5%（両方の監視銘柄）", c2),
                     ("③ 12年のうち8年以上で P＞O1（両方の監視銘柄）", c3), ("④ 数値違いの3通りとも P＞O1（両方の監視銘柄）", c4),
                     ("⑤ 2026-08-31までで切っても P＞O1", c5)):
        w(f"- {lab_}: {'満たす' if ok else '満たさない'}")
    w(f"\n**判定: {'通った（2段目へ）' if all((c1, c2, c3, c4, c5)) else '通らなかった'}**")
    text = "\n".join(out) + "\n"
    if a.out:
        open(a.out, "w", encoding="utf-8").write(text)
    print(text)


if __name__ == "__main__":
    main()
