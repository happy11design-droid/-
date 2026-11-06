#!/usr/bin/env python3
"""始める日と乱数を変えた確かめ（backtest_retest.py の OPT_ROLL の出力）を、形ごとに今のルール（OPT_COMBO の最初の形）と比べる（2026-11-06）

使い方: python3 tools/roll_summary.py <87銘柄のjson> <全業種のjson> [--top N]
  1年の区切り（2015年〜で1年が終わっているもの）ごとに、同じ始める日・同じ乱数で今のルールと比べ、
  1年の損益の差の平均・差が出た区切りのうち良い割合（2015〜2021年・2022年〜も）・1年の中の最大下落率の差・悪い方から5%の下落率を出す。
  厳しい目安（改善のまとめ 5節7・8）: 年率は「両方の監視銘柄で差がプラス・良い割合55%以上・両方の期間で差がプラス」、
  下落率は「両方で下落率の差がマイナス・悪い5%の下落率が小さい・損益の差が −1pt 以上」。
"""
import json
import statistics as st
import sys


def q(xs, p):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, max(0, int(round(p * (len(xs) - 1)))))]


def load(path):
    a = json.load(open(path))
    F = a["forms"]
    base = next(n for n in F if not n.startswith("今のルール（傾き"))
    days, win = a["days"], a["win"]
    pos = {d: k for k, d in enumerate(days)}
    done = [d for d in F[base] if pos[d] + win <= len(days) - 1]
    return a, F, base, done


def stats(F, base, n, ds):
    pr = [(F[n][d][i], F[base][d][i]) for d in ds for i in range(len(F[n][d]))]
    nb = sum(x[0] > y[0] + 1e-9 for x, y in pr)
    nw = sum(x[0] < y[0] - 1e-9 for x, y in pr)
    return {"dr": st.mean(x[0] - y[0] for x, y in pr), "good": nb / (nb + nw) if nb + nw else None,
            "dm": st.mean(x[1] - y[1] for x, y in pr), "w95": q([x[1] for x, _ in pr], 0.95), "b95": q([y[1] for _, y in pr], 0.95)}


def main():
    paths = [p for p in sys.argv[1:] if not p.startswith("--")]
    top = int(sys.argv[sys.argv.index("--top") + 1]) if "--top" in sys.argv else None
    res = {}
    for path, lab in zip(paths, ("87銘柄", "全業種")):
        a, F, base, done = load(path)
        e = [d for d in done if d < "2022-01-01"]
        l = [d for d in done if d >= "2022-01-01"]
        for n in F:
            if n == base or n.startswith("今のルール（傾き"):
                continue
            nm = n.replace(base + "＋", "")
            res.setdefault(nm, {})[lab] = (stats(F, base, n, done), stats(F, base, n, e), stats(F, base, n, l))
    rows = []
    for nm, v in res.items():
        if len(v) < 2:
            continue
        ret_ok = all(a_["dr"] > 0 and (a_["good"] or 0) >= 0.55 and e_["dr"] > 0 and l_["dr"] > 0 for a_, e_, l_ in v.values())
        dd_ok = all(a_["dm"] < 0 and a_["w95"] < a_["b95"] and a_["dr"] >= -0.01 for a_, e_, l_ in v.values())
        score = sum(a_["dr"] for a_, _, _ in v.values())
        rows.append((score, nm, v, ret_ok, dd_ok))
    rows.sort(key=lambda r: -r[0])
    pc = lambda x: f"{x * 100:+.1f}"
    print("| 形 | 87銘柄 1年の損益の差 | 良い割合 | 2015〜21 / 2022〜 | 下落率の差 | 悪い5%の下落率 | 全業種 1年の損益の差 | 良い割合 | 2015〜21 / 2022〜 | 下落率の差 | 悪い5%の下落率 | 年率の目安 | 下落率の目安 |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for score, nm, v, ro, do in rows[:top] if top else rows:
        cells = []
        for lab in ("87銘柄", "全業種"):
            a_, e_, l_ = v[lab]
            cells += [f"{pc(a_['dr'])}pt", f"{(a_['good'] or 0) * 100:.0f}%", f"{pc(e_['dr'])} / {pc(l_['dr'])}", f"{pc(a_['dm'])}pt",
                      f"{a_['w95'] * 100:.1f}%（今 {a_['b95'] * 100:.1f}%）"]
        print(f"| {nm} | " + " | ".join(cells) + f" | {'**満たす**' if ro else '—'} | {'**満たす**' if do else '—'} |")


if __name__ == "__main__":
    main()
