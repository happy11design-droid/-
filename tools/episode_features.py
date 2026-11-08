#!/usr/bin/env python3
"""SOXの大きな下げを1995年〜全部集め、警報の日（SOXが直近60取引日の最高値から−15%以下になった最初の日。前の警報の後、−5%以内まで戻ってからを新しい回とする）の時点の値が、
その後に下げが長引いた回とすぐ戻った回を見分けられていたかを確かめる（2026-11-08 ユーザーの指示「7月の下げと今の下げは同じ扱いなのですか？…厳密に検証して」→「全て検証して」）

警報の日の時点の値（どれもその日の引けまでに分かる値。経済指標は発表の遅れを見て古い月を使う）:
  speed     60日の高値から警報の日までの取引日数（速い下げほど小さい）
  spx       S&P500の直近60取引日の最高値からの下げ
  vix       VIXの終値、vix20 は20取引日前からの変化
  baa60     Baa社債と10年国債の利回り差の、60取引日前からの変化（%ポイント。1986年〜）
  hy20      ハイイールド債ETF（HYG）÷中期国債ETF（IEI）の、直近20取引日の最高値からの下げ（2007年〜）
  ig20      投資適格債ETF（LQD）÷中期国債ETF（IEF）の同じもの（2002年〜）
  curve     10年−2年の金利差
  cond      特殊な下げの3つの条件（A 前の1年のSOXの上げ+80%以上、B 雇用の伸び10万人未満、C 物価3.5%以上で再加速）のうち当てはまった数
その後: SOXの60・120取引日後の騰落、120取引日のうちの最安値（警報の日から）。「長引いた」＝120取引日後もSOXが警報の日より下。

データ: ~/.cache/stock_backtest/long/index/（^SOX・^GSPC・^VIX・HYG・IEI・LQD・IEF は Yahoo、BAA10Y・T10Y2Y・CPIAUCSL・PAYEMS は FRED）。
足りなければ取ってそこに置く（tools/backtest_cache.py save で保存）。
使い方: python3 tools/episode_features.py [--out ファイル]
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

L = os.path.expanduser("~/.cache/stock_backtest/long/index/")
UA = "Mozilla/5.0"


def yahoo(sym):
    p = L + sym + ".json"
    if not os.path.exists(p):
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d&period1=0&period2={int(time.time()) + 86400}"
        res = json.loads(subprocess.run(["curl", "-sS", "--max-time", "60", "-A", UA, url], capture_output=True, text=True).stdout)["chart"]["result"][0]
        q = res["indicators"]["quote"][0]
        adj = (res["indicators"].get("adjclose") or [{}])[0].get("adjclose") or q["close"]
        rows = [[(dt.datetime(1970, 1, 1) + dt.timedelta(seconds=t) - dt.timedelta(hours=5)).date().isoformat(), c, a] for t, c, a in zip(res["timestamp"], q["close"], adj) if c and a]
        json.dump(rows, open(p, "w"))
    return {r[0]: r[2] for r in json.load(open(p))}


def fred(sid):
    p = L + sid + ".csv"
    if not os.path.exists(p):
        open(p, "w").write(subprocess.run(["curl", "-sS", "--max-time", "60", f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}"], capture_output=True, text=True).stdout)
    out = {}
    for r in csv.reader(open(p)):
        try:
            out[r[0]] = float(r[1])
        except (ValueError, IndexError):
            pass
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    a = ap.parse_args()
    os.makedirs(L, exist_ok=True)
    sox, spx, vix = yahoo("^SOX"), yahoo("^GSPC"), yahoo("^VIX")
    hyg, iei, lqd, ief = yahoo("HYG"), yahoo("IEI"), yahoo("LQD"), yahoo("IEF")
    baa, curve, cpi, pay = fred("BAA10Y"), fred("T10Y2Y"), fred("CPIAUCSL"), fred("PAYEMS")
    days = sorted(sox)
    P = [sox[d] for d in days]
    asof = lambda ser, keys, d: (lambda i: ser[keys[i]] if i >= 0 else None)(bisect.bisect_right(keys, d) - 1)
    bk, ck, pk, cvk = sorted(baa), sorted(cpi), sorted(pay), sorted(curve)
    spk, vxk = sorted(spx), sorted(vix)
    def back(d, n):
        return (dt.date.fromisoformat(d) - dt.timedelta(days=n)).isoformat()
    def ratio_dd(x, y, d, n):
        ds = [k for k in days if k <= d and k in x and k in y][-n:]
        if len(ds) < n:
            return None
        v = [x[k] / y[k] for k in ds]
        return v[-1] / max(v) - 1
    def cond(k):
        d = days[k]
        A = k >= 310 and P[k - 60] / P[k - 310] - 1 >= 0.8
        i = bisect.bisect_right(pk, back(d, 40)) - 1
        B = i >= 3 and (pay[pk[i]] - pay[pk[i - 3]]) / 3 < 100
        j = bisect.bisect_right(ck, back(d, 45)) - 1
        y, y3 = cpi[ck[j]] / cpi[ck[j - 12]] - 1, cpi[ck[j - 3]] / cpi[ck[j - 15]] - 1
        C = y >= 0.035 and y > y3
        return int(A) + int(B) + int(C)
    dd60 = lambda k: P[k] / max(P[k - 59:k + 1]) - 1
    # 新しい回: 前の警報の後、SOXが直近60取引日の最高値から−5%以内まで戻ってから、再び−15%以下になった最初の日
    eps, armed = [], True
    for k in range(310, len(P)):
        x = dd60(k)
        if x > -0.05:
            armed = True
        if x <= -0.15 and armed:
            eps.append(k)
            armed = False
    rows = []
    for k in eps:
        d = days[k]
        hi = max(range(k - 59, k + 1), key=lambda j: P[j])
        sp_ds = [x for x in spk if x <= d][-60:]
        spx_dd = spx[sp_ds[-1]] / max(spx[x] for x in sp_ds) - 1
        vx_ds = [x for x in vxk if x <= d][-21:]
        v_now, v_20 = vix[vx_ds[-1]], vix[vx_ds[0]]
        b_now, b_60 = asof(baa, bk, d), asof(baa, bk, days[k - 60])
        m200 = sum(P[k - 199:k + 1]) / 200
        m200p = sum(P[k - 219:k - 19]) / 200
        prev = [e for e in eps if e < k and k - e <= 126]
        r = {"day": d, "dd": dd60(k), "speed": k - hi, "dd252": P[k] / max(P[k - 251:k + 1]) - 1,
             "m200": P[k] / m200 - 1, "m200s": m200 / m200p - 1, "second": int(bool(prev)), "up1y": P[k - 60] / P[k - 310] - 1, "spx": spx_dd, "vix": v_now, "vix20": v_now - v_20,
             "baa60": (b_now - b_60) if b_now is not None and b_60 is not None else None,
             "hy20": ratio_dd(hyg, iei, d, 20), "ig20": ratio_dd(lqd, ief, d, 20), "curve": asof(curve, cvk, d), "cond": cond(k),
             "r60": P[k + 60] / P[k] - 1 if k + 60 < len(P) else None, "r120": P[k + 120] / P[k] - 1 if k + 120 < len(P) else None,
             "low120": min(P[k:k + 121]) / P[k] - 1}
        rows.append(r)
    pc = lambda x, d=0: "—" if x is None else f"{x * 100:+.{d}f}%"
    out = []
    w = out.append
    w("| 警報の日 | SOXの下げ | 1年の高値から | 200日線から（線の20日の傾き） | 半年以内の2回目 | 高値からの日数 | S&P500の下げ | VIX（20日の変化） | Baa社債の差の60日の変化 | HYG/IEI 20日の高値から | LQD/IEF 20日の高値から | 10年−2年 | 条件の数 | 60日後 | 120日後 | 120日以内の最安値 | 長引いた |")
    w("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        long_ = None if r["r120"] is None else r["r120"] < 0
        w(f"| {r['day']} | {pc(r['dd'])} | {pc(r['dd252'])} | {pc(r['m200'])}（{pc(r['m200s'], 1)}） | {'はい' if r['second'] else '—'} | {r['speed']} | {pc(r['spx'], 1)} | {r['vix']:.1f}（{r['vix20']:+.1f}） | "
          f"{'—' if r['baa60'] is None else f'{r['baa60']:+.2f}'} | {pc(r['hy20'], 2)} | {pc(r['ig20'], 2)} | {'—' if r['curve'] is None else f'{r['curve']:+.2f}'} | {r['cond']} | "
          f"{pc(r['r60'])} | {pc(r['r120'])} | {pc(r['low120'])} | {'—' if long_ is None else ('はい' if long_ else 'いいえ')} |")
    past = [r for r in rows if r["day"] < "2026-01-01" and r["r120"] is not None]
    w(f"\n## 2026年より前の {len(past)} 回で、警報の日の値が「長引いた回」を見分けられたか\n")
    w("値で2つに分け（境目は、2026年より前の回の中央値か、ふつう使われる値）、長引いた割合と120取引日後の中央値を比べる。順位の相関は、値と120取引日後の騰落の順位の相関（−1〜+1。マイナスなら「値が大きいほど下げが長引く」）。\n")
    w("| 値 | 境目 | 値が大きい回: 長引いた割合（120日後の中央値） | 値が小さい回: 長引いた割合（120日後の中央値） | 順位の相関 | 2026年7月 | 2026年10月 |")
    w("|---|---|---|---|---|---|---|")
    def spearman(xs, ys):
        n = len(xs)
        rx = {i: r for r, i in enumerate(sorted(range(n), key=lambda i: xs[i]))}
        ry = {i: r for r, i in enumerate(sorted(range(n), key=lambda i: ys[i]))}
        mx = my = (n - 1) / 2
        num = sum((rx[i] - mx) * (ry[i] - my) for i in range(n))
        den = (sum((rx[i] - mx) ** 2 for i in range(n)) * sum((ry[i] - my) ** 2 for i in range(n))) ** 0.5
        return num / den if den else 0.0
    jul = next((r for r in rows if "2026-06-15" <= r["day"] <= "2026-08-31"), None)
    # 2026年7月の回は120取引日がまだ経っていない
    octo = next((r for r in rows if r["day"] >= "2026-10-01"), None)
    labels = {"dd252": ("1年の高値からの下げ（小さいほど深い）", None, "{:+.1%}"), "m200": ("200日線からの離れ", 0.0, "{:+.1%}"),
              "m200s": ("200日線の20日の傾き", 0.0, "{:+.1%}"), "second": ("半年以内の2回目の下げ", 0.5, "{:.0f}"), "up1y": ("前の1年のSOXの上げ", None, "{:+.0%}"),
              "speed": ("高値からの日数", None, "{:.0f}"), "spx": ("S&P500の下げ（小さいほど深い）", None, "{:+.1%}"), "vix": ("VIX", 25.0, "{:.1f}"),
              "vix20": ("VIXの20日の変化", None, "{:+.1f}"), "baa60": ("Baa社債の差の60日の変化", 0.0, "{:+.2f}"), "hy20": ("HYG/IEIの20日の高値からの下げ（小さいほど悪い）", -0.01, "{:+.2%}"),
              "ig20": ("LQD/IEFの20日の高値からの下げ", -0.01, "{:+.2%}"), "curve": ("10年−2年の金利差", 0.0, "{:+.2f}"), "cond": ("特殊な下げの条件の数", 1.5, "{:.0f}")}
    summary = {}
    for key, (lab, thr, fmt) in labels.items():
        xs = [(r[key], r) for r in past if r[key] is not None]
        if len(xs) < 6:
            continue
        th = thr if thr is not None else st.median(v for v, _ in xs)
        hi_ = [r for v, r in xs if v > th]
        lo_ = [r for v, r in xs if v <= th]
        f = lambda g: f"{sum(1 for r in g if r['r120'] < 0)}/{len(g)}（{pc(st.median(r['r120'] for r in g))}）" if g else "—"
        rho = spearman([v for v, _ in xs], [r["r120"] for _, r in xs])
        summary[key] = rho
        w(f"| {lab} | {fmt.format(th)} | {f(hi_)} | {f(lo_)} | {rho:+.2f}（{len(xs)}回） | {'—' if not jul or jul[key] is None else fmt.format(jul[key])} | {'—' if not octo or octo[key] is None else fmt.format(octo[key])} |")
    txt = "\n".join(out) + "\n"
    if a.out:
        open(a.out, "w", encoding="utf-8").write(txt)
        rp = os.path.expanduser("~/.cache/stock_backtest/results/")
        os.makedirs(rp, exist_ok=True)
        json.dump(rows, open(rp + "episode_features.json", "w"), ensure_ascii=False)
    print(txt)


if __name__ == "__main__":
    main()
