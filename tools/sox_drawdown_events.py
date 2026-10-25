#!/usr/bin/env python3
"""半導体指数（SOX）の急落の後、どう戻ったかの統計（2026-10-25 ユーザーの指示。ムームー証券のAIの「同じような下落は過去にあったか」「いつ頃戻るか」をデータで確かめる）

使い方:
  tools/sox_drawdown_events.py [--drop 0.15] [--window 10] [--out FILE]

急落の日: 終値が直前 window 取引日（当日を含む）の最高値（終値）から drop 以上下げた最初の日。40取引日続けて急落の日がなければ、新しい急落として数える。
急落の日の終値から、その後の値動きを測る:
  さらに下げた幅（120取引日の中の最安値、終値）と、その日までの取引日数
  20日線を上回るまで（終値が20日線より上の最初の日）、20日線を2日続けて上回るまで、急落の前の高値（終値）に戻るまでの取引日数
  5・20・60・120取引日後の騰落
急落の日の局面: SOXが200日線より上か、10年金利（^TNX）が50日線より上で、50日線が20取引日前より上（金利の上昇局面）か。
株価は Yahoo Finance の日足（SOXは1994-05〜）。~/.cache/stock_backtest/long/ に置く。
"""
import argparse
import datetime as dt
import json
import os
import statistics as st
import subprocess
import time

CACHE = os.path.expanduser("~/.cache/stock_backtest/long")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "新分析ツール", "バックテスト結果", "半導体指数の急落の後の戻り.md")


def fetch(sym, max_age_h=12):
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, sym.replace("^", "_") + ".json")
    if not os.path.exists(p) or time.time() - os.path.getmtime(p) > max_age_h * 3600:
        r = subprocess.run(["curl", "-sS", "--compressed", "--max-time", "60", "-A", "Mozilla/5.0",
                            f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d&period1=0&period2={int(time.time())}"],
                           capture_output=True)
        res = json.loads(r.stdout)["chart"]["result"][0]
        q = res["indicators"]["quote"][0]
        rows = [(dt.datetime.utcfromtimestamp(t + res["meta"].get("gmtoffset", 0)).strftime("%Y-%m-%d"), c)
                for t, c in zip(res["timestamp"], q["close"]) if c]
        json.dump(rows, open(p, "w"))
    rows = json.load(open(p))
    return [r[0] for r in rows], [r[1] for r in rows]


def sma(c, n):
    out, s = [None] * len(c), 0.0
    for i, v in enumerate(c):
        s += v
        if i >= n:
            s -= c[i - n]
        if i >= n - 1:
            out[i] = s / n
    return out


def first(cond, lo, hi):
    for k in range(lo, hi):
        if cond(k):
            return k
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--drop", type=float, default=0.15)
    ap.add_argument("--window", type=int, default=10)
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args()
    d, c = fetch("^SOX")
    td, tc = fetch("^TNX")
    tmap = dict(zip(td, tc))
    tser, last = [], None
    for x in d:
        last = tmap.get(x, last)
        tser.append(last)
    m20, m200 = sma(c, 20), sma(c, 200)
    t50 = [None] * len(tser)
    for i in range(49, len(tser)):
        w = [v for v in tser[i - 49:i + 1] if v is not None]
        t50[i] = sum(w) / len(w) if len(w) == 50 else None
    n = len(c)
    ev, lastev = [], -10 ** 9
    for i in range(a.window, n):
        k0 = max(range(i - a.window + 1, i + 1), key=lambda k: c[k])
        if c[i] / c[k0] - 1 <= -a.drop:
            if i - lastev > 40:
                ev.append((i, k0))
            lastev = i
    rows = []
    for i, k0 in ev:
        hi = min(n, i + 121)
        low_k = min(range(i, hi), key=lambda k: c[k])
        r = {"date": d[i], "peak": d[k0], "days": i - k0, "drop": c[i] / c[k0] - 1,
             "above200": m200[i] is not None and c[i] > m200[i], "d200": c[i] / m200[i] - 1 if m200[i] else None,
             "rate_up": tser[i] is not None and t50[i] is not None and t50[i - 20] is not None and tser[i] > t50[i] and t50[i] > t50[i - 20],
             "more": c[low_k] / c[i] - 1, "low_days": low_k - i, "total": c[low_k] / c[k0] - 1,
             "ma20": first(lambda k: m20[k] is not None and c[k] > m20[k], i + 1, n),
             "ma20x2": first(lambda k: m20[k] is not None and m20[k - 1] is not None and c[k] > m20[k] and c[k - 1] > m20[k - 1], i + 2, n),
             "back": first(lambda k: c[k] >= c[k0], i + 1, n), "n_after": n - 1 - i}
        for h in (5, 20, 60, 120):
            r[f"r{h}"] = c[i + h] / c[i] - 1 if i + h < n else None
        for k in ("ma20", "ma20x2", "back"):
            r[k] = None if r[k] is None else r[k] - i
        rows.append(r)

    pct = lambda x: "—" if x is None else f"{x * 100:+.1f}%"
    dd = lambda x: "未回復" if x is None else f"{x}"
    L = [f"---\ntype: backtest\ntitle: 半導体指数の急落の後の戻り\ncreated: {dt.date.today()}\nscript: tools/sox_drawdown_events.py\n---\n",
         "# 半導体指数（SOX）の急落の後、どう戻ったか\n", __doc__.split("\n", 5)[5].strip() + "\n",
         f"株価は {d[0]}〜{d[-1]}。急落の条件: 直前{a.window}取引日の最高値から−{a.drop * 100:.0f}%以上（終値）。\n",
         f"## 1. 急落の一覧（{len(rows)}回）\n",
         "| 急落の日 | 前の高値の日 | 下げの日数 | 急落の日までの下げ | 200日線 | 金利 | その後さらに下げた幅 | 最安値までの日数 | 高値からの下げの合計 | 20日線を上回るまで | 20日線を2日続けて上回るまで | 前の高値に戻るまで | 5日後 | 20日後 | 60日後 | 120日後 |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['date']} | {r['peak']} | {r['days']} | {pct(r['drop'])} | {'上' if r['above200'] else '下'}（{pct(r['d200'])}） | {'上昇' if r['rate_up'] else '—'} | "
                 f"{pct(r['more'])} | {r['low_days']} | {pct(r['total'])} | {dd(r['ma20'])} | {dd(r['ma20x2'])} | {dd(r['back'])} | "
                 f"{pct(r['r5'])} | {pct(r['r20'])} | {pct(r['r60'])} | {pct(r['r120'])} |")

    def summ(lab, rs):
        if not rs:
            return f"| {lab} | 0 | | | | | | | | | |"
        med = lambda k: st.median([r[k] for r in rs if r[k] is not None]) if any(r[k] is not None for r in rs) else None
        up = lambda k: sum(1 for r in rs if r[k] is not None and r[k] > 0) / max(1, sum(1 for r in rs if r[k] is not None))
        back_n = sum(1 for r in rs if r["back"] is not None)
        return (f"| {lab} | {len(rs)} | {pct(med('more'))}（最悪 {pct(min(r['more'] for r in rs))}） | {med('low_days'):.0f} | {med('ma20'):.0f} | {med('ma20x2'):.0f} | "
                f"{(med('back') or 0):.0f}（{back_n}/{len(rs)}回が回復） | {pct(med('r20'))}（上げ{up('r20') * 100:.0f}%） | {pct(med('r60'))}（上げ{up('r60') * 100:.0f}%） | {pct(med('r120'))}（上げ{up('r120') * 100:.0f}%） |")
    done = [r for r in rows if r["n_after"] >= 120]
    L += ["\n## 2. まとめ（中央値。120取引日後まで分かる急落だけ）\n",
          "| 区分 | 回数 | その後さらに下げた幅 | 最安値までの日数 | 20日線を上回るまで | 20日線を2日続けて上回るまで | 前の高値に戻るまで（日） | 20日後 | 60日後 | 120日後 |",
          "|---|---|---|---|---|---|---|---|---|---|",
          summ("全部", done),
          summ("SOXが200日線より上の急落", [r for r in done if r["above200"]]),
          summ("SOXが200日線より下の急落", [r for r in done if not r["above200"]]),
          summ("10年金利が上昇局面の急落", [r for r in done if r["rate_up"]]),
          summ("10年金利が上昇局面でない急落", [r for r in done if not r["rate_up"]]),
          summ("2010年以降", [r for r in done if r["date"] >= "2010"])]
    if done:
        m10, m20 = sum(1 for r in done if r["more"] <= -0.10), sum(1 for r in done if r["more"] <= -0.20)
        L.append(f"\n- 急落の日の後（120取引日の中で）さらに−10%以上下げたのは {m10}/{len(done)}回、−20%以上下げたのは {m20}/{len(done)}回。"
                 f"20日後に急落の日より上だったのは {sum(1 for r in done if r['r20'] > 0)}/{len(done)}回。")
    cur = [r for r in rows if r["n_after"] < 120]
    if cur:
        L.append("\n## 3. 120取引日が経っていない急落（今回を含む）\n")
        for r in cur:
            L.append(f"- {r['date']}（前の高値 {r['peak']}、{r['days']}取引日で {pct(r['drop'])}）: {r['n_after']}取引日が経過。"
                     f"その後の最安値まで {pct(r['more'])}（{r['low_days']}取引日目）、20日線を上回るまで {dd(r['ma20'])}、前の高値に戻るまで {dd(r['back'])}。"
                     f"200日線より{'上' if r['above200'] else '下'}（{pct(r['d200'])}）、金利は{'上昇局面' if r['rate_up'] else '上昇局面でない'}。")
    L += ["\n## 注意\n",
          "- 指数の統計で、個別銘柄（SNDK・DELL・LITE・MRVL など）の値動きは指数より大きい。個別銘柄の売買の判断ではない。",
          "- 急落の回数が少ない（数十回）ので、中央値は目安。1998・2000〜2002・2008年のような長い下落相場も含む。",
          "- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。"]
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(a.out)
    print("\n".join(L[-20:]))


if __name__ == "__main__":
    main()
