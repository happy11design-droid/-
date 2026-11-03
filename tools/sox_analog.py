#!/usr/bin/env python3
"""今回の半導体の下げを、1994年〜の似た下げと比べる（2026-11-03 ユーザーの指示「過去に同じような下落の時と比較して…数値化して確認できませんか」）

SOX（フィラデルフィア半導体指数）が直近60取引日の最高値から−20%以下になった局面を1994年〜で抜き出し、その日に分かっていた条件で分けて、
その後のSOX・S&P500・AI以外の業種の動きを比べる。

  条件A: 下げの前の1年（60取引日前までの250取引日）のSOXの上げが+80%以上（大きく上げた後の下げ）
  条件B: 雇用の伸び（PAYEMSの3か月平均）が10万人未満（発表の遅れを見て40日前の月まで）
  条件C: 物価（CPIAUCSLの前年比）が3.5%以上で、3か月前より高い（再加速。45日前の月まで）
  ※ 条件は、過去の下げを見てから選んだもの（後知恵を含む）。長い下げの局面は約5回しかない。

データ: Yahooファイナンスの日足（^SOX・^GSPC・SPY・業種ETF・^TNX・^VIX）と FRED（CPIAUCSL・PAYEMS・BAA10Y）。無料・APIキー不要。
保存先: ~/.cache/stock_backtest/long/analog/（1日1回取り直す）

使い方: python3 tools/sox_analog.py [--th 0.20]
"""
import argparse
import bisect
import csv
import datetime as dt
import json
import os
import statistics as st
import subprocess
import time
import urllib.parse

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
DIR = os.path.expanduser("~/.cache/stock_backtest/long/analog")
SECT = ["XLE", "XLV", "XLU", "XLP", "XLF", "XLI", "XLB", "XLY"]   # AI以外の8業種（1998年12月〜）


def fresh(p):
    return os.path.exists(p) and time.time() - os.path.getmtime(p) < 86400


def yahoo(sym):
    """[(日付, 終値, 配当込みの終値)]"""
    p = os.path.join(DIR, sym + ".json")
    if not fresh(p):
        url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(sym)}"
               f"?interval=1d&period1=0&period2={int(time.time()) + 86400}&events=div%2Csplit")
        r = subprocess.run(["curl", "-sS", "--max-time", "60", "-A", UA, url], capture_output=True, text=True)
        res = json.loads(r.stdout)["chart"]["result"][0]
        q = res["indicators"]["quote"][0]
        adj = (res["indicators"].get("adjclose") or [{}])[0].get("adjclose") or q["close"]
        rows = [((dt.datetime.utcfromtimestamp(t) - dt.timedelta(hours=5)).date().isoformat(), c, a)
                for t, c, a in zip(res["timestamp"], q["close"], adj) if c is not None and a is not None]
        json.dump(rows, open(p, "w"))
    return json.load(open(p))


def fred(sid):
    p = os.path.join(DIR, sid + ".csv")
    if not fresh(p):
        txt = subprocess.run(["curl", "-sS", "--max-time", "60", f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}"],
                             capture_output=True, text=True).stdout
        open(p, "w").write(txt)
    out = {}
    for r in csv.reader(open(p)):
        try:
            out[r[0]] = float(r[1])
        except (ValueError, IndexError):
            pass
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--th", type=float, default=0.20, help="SOXの直近60取引日の最高値からの下げ（既定 0.20）")
    a = ap.parse_args()
    os.makedirs(DIR, exist_ok=True)
    sox = {d: c for d, c, _ in yahoo("^SOX")}
    spy = {d: x for d, _, x in yahoo("SPY")}
    sect = {s: {d: x for d, _, x in yahoo(s)} for s in SECT}
    baa, cpi, pay = fred("BAA10Y"), fred("CPIAUCSL"), fred("PAYEMS")
    bk, ck, pk = sorted(baa), sorted(cpi), sorted(pay)
    days = [d for d in sorted(sox) if d in spy]
    P = [sox[d] for d in days]
    Q = [spy[d] for d in days]

    def back(d, n):
        return (dt.date.fromisoformat(d) - dt.timedelta(days=n)).isoformat()

    def cpi_f(d):
        k = bisect.bisect_right(ck, back(d, 45)) - 1
        y, y3 = cpi[ck[k]] / cpi[ck[k - 12]] - 1, cpi[ck[k - 3]] / cpi[ck[k - 15]] - 1
        return y, y3

    def pay_f(d):
        k = bisect.bisect_right(pk, back(d, 40)) - 1
        return (pay[pk[k]] - pay[pk[k - 3]]) / 3

    def feats(k):
        y, y3 = cpi_f(days[k])
        A = k >= 310 and P[k - 60] / P[k - 310] - 1 >= 0.8
        B = pay_f(days[k]) < 100
        C = y >= 0.035 and y > y3
        return A, B, C

    def asof(ser, keys, d):
        i = bisect.bisect_right(keys, d) - 1
        return ser[keys[i]] if i >= 0 else None

    k0 = next(k for k, d in enumerate(days) if d >= "1995-06-01")
    th = a.th
    dd60 = lambda k: P[k] / max(P[k - 59:k + 1]) - 1
    pc = lambda x: "—" if x is None else f"{x * 100:+.0f}%"

    # 1. 局面ごと（その前の60取引日に−X%の日がない最初の日）
    eps, last = [], -999
    for k in range(310, len(P)):
        if dd60(k) <= -th:
            if k - last > 60:
                eps.append(k)
            last = k
    print(f"## 1. SOXが直近60取引日の最高値から−{th:.0%}以下になった局面（1995年〜）と今日\n")
    print("| 始まり | 60日の高値から | 1年の高値から | 前の1年の上げ | 雇用（千人/月） | 物価（前年比・3か月前との差） | 社債の差の60日の変化 | A | B | C | 120日後 | 250日後 | その後の最安値 | 高値を戻すまで（取引日） |")
    print("|" + "---|" * 14)
    for k in eps + [len(P) - 1]:
        hi = max(range(k - 59, k + 1), key=lambda j: P[j])
        y, y3 = cpi_f(days[k])
        A, B, C = feats(k)
        b0, b1 = asof(baa, bk, days[k]), asof(baa, bk, days[k - 60])
        w = P[k:k + 251]
        rec = next((j - k for j in range(k, len(P)) if P[j] >= P[hi]), None)
        r = lambda n: P[k + n] / P[k] - 1 if k + n < len(P) else None
        print(f"| {days[k]}{'（今日）' if k == len(P) - 1 else ''} | {pc(dd60(k))} | {pc(P[k] / max(P[k - 249:k + 1]) - 1)} | {pc(P[k - 60] / P[k - 310] - 1)} | "
              f"{pay_f(days[k]):.0f} | {y * 100:.1f}%（{(y - y3) * 100:+.1f}） | {b0 - b1:+.2f} | {'●' if A else '・'} | {'●' if B else '・'} | {'●' if C else '・'} | "
              f"{pc(r(120))} | {pc(r(250))} | {pc(min(w) / P[k] - 1)} | {rec if rec is not None else 'まだ'} |")

    # 2. 日ごと（条件の数で分ける）
    grp = {}
    for k in range(k0, len(P)):
        if dd60(k) <= -th:
            grp.setdefault(min(sum(feats(k)), 2), []).append(k)
    print(f"\n## 2. SOXが−{th:.0%}以下の日のその後（日ごと。1995年〜）\n")
    print("| 条件の数 | 日数 | 60日後に下 | 120日後に下 | 250日後に下 | 120日後（中央値） | 250日後（中央値） | 120日以内の最安値（中央値） | 年 |")
    print("|---|---|---|---|---|---|---|---|---|")
    for g in sorted(grp):
        ks = grp[g]
        fw = lambda n: [P[k + n] / P[k] - 1 for k in ks if k + n < len(P)]
        lo = [min(P[k:k + 121]) / P[k] - 1 for k in ks if k + 120 < len(P)]
        down = lambda n: f"{sum(x < 0 for x in fw(n)) / len(fw(n)) * 100:.0f}%"
        print(f"| {g}つ{'以上' if g == 2 else ''} | {len(ks)} | {down(60)} | {down(120)} | {down(250)} | {pc(st.median(fw(120)))} | {pc(st.median(fw(250)))} | "
              f"{pc(st.median(lo))} | {'・'.join(sorted({days[k][:4] for k in ks}))} |")

    # 3. 同じ日からの、SOX・S&P500・AI以外の業種
    print(f"\n## 3. 同じ日から（1999年〜）: SOX・S&P500・AI以外の8業種\n")
    print("| 条件の数 | 日数 | SOX 120日後 | S&P500 120日後 | 8業種の平均 120日後 | SOX 250日後 | S&P500 250日後 | 8業種の平均 250日後 | 一番良かった業種 250日後 |")
    print("|---|---|---|---|---|---|---|---|---|")
    for g in sorted(grp):
        ks = [k for k in grp[g] if days[k] >= "1999-01-04"]
        row = []
        for n in (120, 250):
            kk = [k for k in ks if k + n < len(P)]
            row += [pc(st.median(P[k + n] / P[k] - 1 for k in kk)), pc(st.median(Q[k + n] / Q[k] - 1 for k in kk)),
                    pc(st.median(st.mean(sect[s][days[k + n]] / sect[s][days[k]] - 1 for s in SECT) for k in kk))]
        kk = [k for k in ks if k + 250 < len(P)]
        per = {s: st.median(sect[s][days[k + 250]] / sect[s][days[k]] - 1 for k in kk) for s in SECT}
        b = max(per, key=per.get)
        print(f"| {g}つ{'以上' if g == 2 else ''} | {len(ks)} | " + " | ".join(row) + f" | {b} {pc(per[b])} |")

    # 4. 指数での乗り換え（条件の日の引けで判定し、翌日から。戻すのはSOXが50日線より上で50日線が10取引日前より上）
    ma = lambda k, n: sum(P[k - n + 1:k + 1]) / n
    def run(need, dest):
        eq, peak, mdd, out, n = 1.0, 1.0, 0.0, False, 0
        for k in range(k0, len(P) - 1):
            if need is not None and not out and dd60(k) <= -th and sum(feats(k)) >= need:
                out, n = True, n + 1
            elif out and P[k] > ma(k, 50) > ma(k - 10, 50):
                out = False
            eq *= (Q[k + 1] / Q[k] if dest == "spy" else 1.0) if out else P[k + 1] / P[k]
            peak = max(peak, eq)
            mdd = max(mdd, 1 - eq / peak)
        yrs = (dt.date.fromisoformat(days[-1]) - dt.date.fromisoformat(days[k0])).days / 365.25
        return eq ** (1 / yrs) - 1, mdd, n
    print(f"\n## 4. 指数で乗り換えた場合（1995年6月〜。SOXは配当なしの指数、S&P500はSPYの配当込み）\n")
    print("| 形 | 年率 | 最大下落率 | 乗り換えた回数 |")
    print("|---|---|---|---|")
    g, m, _ = run(None, "spy")
    print(f"| SOXを持ち続ける | {g * 100:.1f}% | {m * 100:.0f}% | 0 |")
    for need in (0, 1, 2):
        for dest in ("spy", "cash"):
            g, m, n = run(need, dest)
            print(f"| −{th:.0%}かつ条件{need}つ以上で{'S&P500' if dest == 'spy' else '現金'}へ | {g * 100:.1f}% | {m * 100:.0f}% | {n} |")


if __name__ == "__main__":
    main()
