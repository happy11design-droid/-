#!/usr/bin/env python3
"""手9（Fableの提案 `新分析ツール/Fableの提案_未解決の課題_2026-11-15.md` 11節、2026-11-15）:
オニールのC（直近の四半期のEPSが前年の同じ四半期より+25%以上）とA（年間のEPSが3年続けて伸びている）を、
新高値V2・ミネルヴィニの合図に付け、合図ごとの成績を比べる（1段目だけ。資金の計算はしない）。

EPS: `~/.cache/stock_backtest/onkabu_fund/<銘柄>.json` の "eps"（SECのXBRL、[提出日, 期間の初め, 期間の終わり, 値]）。
合図の日（sd）より前に提出されたものだけを使う（先読みをしない）。同じ期間が何度も出たら、合図の日までの一番新しい提出の値。
  四半期: 期間が70〜110日。前年の同じ四半期: 期間の終わりが約1年前（±25日）。
  C: 前年の値が正で +25%以上、または前年が0以下で今が正
  A: 年間（期間が350〜380日）の直近4年の値が、3回続けて前の年を上回る
形は「C」と「CかつA」の2つ。
でたらめ: 同じ合図の日・同じルールの合図の中で、当たる・当たらないのラベルを入れ替える（1,000回）。

使い方: python3 tools/eps_ca_check.py [--out FILE]
"""
import argparse
import datetime as dt
import json
import os
import random
import statistics as st

C = os.path.expanduser("~/.cache/stock_backtest/")
D = lambda s: dt.date.fromisoformat(s)  # noqa: E731


def load_eps(sym):
    p = C + f"onkabu_fund/{sym}.json"
    if not os.path.exists(p):
        return None
    return [tuple(r) for r in json.load(open(p)).get("eps", [])]


def at(rows, sd):
    """合図の日までに提出された、期間ごとの一番新しい値: {(初め, 終わり): 値}"""
    best = {}
    for filed, a, b, v in rows:
        if filed <= sd and v is not None:
            k = (a, b)
            if k not in best or filed >= best[k][0]:
                best[k] = (filed, v)
    return {k: v for k, (f, v) in best.items()}


def tag(rows, sd):
    per = at(rows, sd)
    q = sorted(((b, a, v) for (a, b), v in per.items() if 70 <= (D(b) - D(a)).days <= 110), reverse=True)
    yr = sorted(((b, a, v) for (a, b), v in per.items() if 350 <= (D(b) - D(a)).days <= 380), reverse=True)
    c = None
    if q:
        b0, a0, v0 = q[0]
        prev = [v for b, a, v in q[1:] if abs((D(b0) - D(b)).days - 365) <= 25]
        if prev:
            p = prev[0]
            c = (p > 0 and v0 / p - 1 >= 0.25) or (p <= 0 < v0)
    aa = None
    ys = []
    for b, a, v in yr:
        if not ys or (D(ys[-1][0]) - D(b)).days >= 300:
            ys.append((b, v))
        if len(ys) == 4:
            break
    if len(ys) == 4:
        vals = [v for _, v in ys][::-1]
        aa = all(vals[i + 1] > vals[i] for i in range(3))
    return c, aa


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--perm", type=int, default=1000)
    a = ap.parse_args()
    out = []
    w = out.append
    verdict = []
    cache = {}
    for wch, lab in (("87", "87銘柄"), ("free", "全業種（後知恵なし）")):
        rows = [r for r in json.load(open(C + f"results/combo_feat_{wch}.json")) if r["src"] == "今" and r["rule"] in ("M", "V") and r["sd"] >= "2015-01-01"]
        tagged = []
        for r in rows:
            if r["sym"] not in cache:
                cache[r["sym"]] = load_eps(r["sym"])
            e = cache[r["sym"]]
            if not e:
                continue
            c, aa = tag(e, r["sd"])
            if c is None:
                continue
            tagged.append((r, c, (c and aa) if aa is not None else None))
        w(f"\n## {lab}（新高値V2・ミネルヴィニの合図 {len(rows)}件のうち、EPSで判定できた {len(tagged)}件）\n")
        w("| 形 | 期間 | 当たる 件数・1回平均・損切り | 当たらない 件数・1回平均・損切り | 差 |")
        w("|---|---|---|---|---|")
        for form, k in (("C", 1), ("CかつA", 2)):
            items = [(r, x[k]) for x in tagged for r in [x[0]] if x[k] is not None]
            for per, lo, hi in (("2015〜2020年（決める）", "2015", "2021"), ("2021〜2026年（確かめる）", "2021", "2027"), ("全期間", "2015", "2027"), ("2026-08-31まで", "2015", "2026-08-31")):
                ss = [(r, h) for r, h in items if lo <= r["sd"][:len(lo)] and (r["sd"] < hi if len(hi) == 4 else r["sd"] <= hi)]
                yes = [r for r, h in ss if h]
                no = [r for r, h in ss if not h]
                f = lambda g: f"{len(g)}・{st.mean(x['ret'] for x in g):+.2%}・{sum(1 for x in g if x['stopped']) / len(g):.0%}" if g else "0"  # noqa: E731
                dd = (st.mean(x["ret"] for x in yes) - st.mean(x["ret"] for x in no)) if yes and no else None
                w(f"| {form} | {per} | {f(yes)} | {f(no)} | {'—' if dd is None else f'{dd:+.2%}'} |")
                if per.startswith("20") and "まで" not in per and per != "全期間":
                    verdict.append((wch, form, per, dd))
            # でたらめ（全期間）
            rnd = random.Random(0)
            cells = {}
            for i, (r, h) in enumerate(items):
                cells.setdefault((r["sd"], r["rule"]), []).append(i)
            def diff(hs):
                y = [items[i][0]["ret"] for i in range(len(items)) if hs[i]]
                n = [items[i][0]["ret"] for i in range(len(items)) if not hs[i]]
                return st.mean(y) - st.mean(n) if y and n else None
            base = [h for _, h in items]
            obs = diff(base)
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
            ys = sorted({r["sd"][:4] for r, _ in items})
            ypos = 0
            for y in ys:
                yy = [r["ret"] for r, h in items if h and r["sd"][:4] == y]
                nn = [r["ret"] for r, h in items if not h and r["sd"][:4] == y]
                if yy and nn and st.mean(yy) > st.mean(nn):
                    ypos += 1
            w(f"- {form}: でたらめ（同じ日・同じルールの中で入れ替え、{a.perm}回）で本物以上だった割合 {ge / a.perm:.0%}。年ごとに当たる方が良かった年 {ypos}/{len(ys)}")
    ok = all(dd is not None and dd >= 0.02 for _, _, _, dd in verdict)
    w(f"\n**判定（両方の監視銘柄・両方の期間で、当たる合図の1回平均が +2pt 以上良いか）: {'満たす形がある' if ok else '満たさない'}**")
    text = "\n".join(out) + "\n"
    if a.out:
        open(a.out, "w", encoding="utf-8").write(text)
    print(text)


if __name__ == "__main__":
    main()
