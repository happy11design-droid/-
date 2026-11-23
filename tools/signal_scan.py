#!/usr/bin/env python3
"""早めの合図を探す（2026-11-23 ユーザーの指示「合図が遅いならニュースで判定したら？これは以前少し検証してると思う。もっと何かシグナルを掴めないか検証して」）。

2015年〜の日ごとに、その日の引けまでに分かる値だけで「テーマ（87銘柄）が崩れ始めた」合図を約20通り作り、次を確かめる。
  1. 予測力: 合図の日から20取引日の「87銘柄の口（今のルール）−全業種の口」の損益の差と、87銘柄の口の損益（どちらも乱数30通りの平均の毎日の騰落から）。
     合図の日とそうでない日の平均の差を、合図の並びを丸ごとずらして作った2,000通りと比べた片側のp値（ずらし検定。合図の続き方と相場の続き方をそのまま残す）。
     2015〜2021年・2022年〜の別々の差も出す（向きがそろうか）。
  2. 早さ: 87銘柄の等金額の平均が高値から−20%以上下げた回ごとに、高値から何取引日目に合図が出たか、その時点で下げの何割が済んでいたか。
  3. だまし: 合図が出始めた回のうち、その後40取引日の間に87銘柄の平均がそれ以上5%も下げなかった割合。
  4. 今回の下げ（2026年6月〜）で合図が出始めた日。
ニュースの合図は見出しがある2023年〜だけ（`~/.cache/stock_backtest/news/history_87.json`、tools/news_history.py）。ほかの合図も2023年〜の数値を並べる。
GDELT（2017年〜のニュースの調子）は 2026-11-23 に試したが、回数の制限（5秒に1回）と長い問い合わせの切断で取れなかった。

入力: backtest_retest.py の毎日の資金（OPT_EQDUMP_ALL=1、87銘柄と全業種）。合図の日の集合は --regs-out に書き出し、tools/stat_compare.py --regs で切り替えの形に使う。
データはキャッシュ（~/.cache/stock_backtest/）にあるものだけを使い、新しく取らない。
使い方: tools/signal_scan.py --eq87 FILE(.json/.json.gz) --eqall FILE --out FILE --regs-out FILE
数値の事実だけで、Claudeの売買判断は含まない。
"""
import argparse
import bisect
import csv
import datetime as dt
import gzip
import json
import os
import re
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backtest_lib import DEFAULT_CACHE, load_prices
import backtest_crash_mode as bcm

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LI = os.path.expanduser("~/.cache/stock_backtest/long/index/")
RNG = np.random.default_rng(20261123)
H = 20
# 大手4社（MSFT・GOOGL・AMZN・META）の決算の翌日の値動き（backtest_retest.py が SEC の8-Kの時刻から作った日。2015年〜）
BIG4_AVG2 = ["2018-07-27", "2020-10-30", "2021-07-30", "2022-10-28", "2024-08-02", "2025-02-07", "2026-10-30"]
BIG4_TWO5 = ["2016-04-22", "2016-11-03", "2020-10-30", "2022-10-26", "2024-08-02", "2025-02-05", "2026-02-06", "2026-07-30", "2026-10-29"]


def jload(p):
    return json.load(gzip.open(p, "rt") if p.endswith(".gz") else open(p))


def watch87():
    md = open(os.path.join(ROOT, "新分析ツール", "テーマ監視銘柄.md"), encoding="utf-8").read()
    out, cur = [], None
    for ln in md.splitlines():
        if ln.startswith("## "):
            m = re.match(r"^## (.+?)（", ln)
            cur = None if (not m or ln.startswith("## 指数に入っていない")) else m.group(1)
            continue
        m = re.match(r"^\| ([A-Z][A-Z0-9.\-]*) \|", ln)
        if m and cur and m.group(1) != "ティッカー":
            out.append(m.group(1))
    return out


def long_close(name):
    """long/index の日足（[日付, 終値, 調整後] か [日付, 始, 高, 安, 終, 調整後]）→ {日付: 調整後の終値}"""
    rows = json.load(open(LI + name))
    return {r[0]: (r[2] if len(r) == 3 else r[-1]) for r in rows if r[-1]}


def csv_close(name, fmt, col):
    out = {}
    for r in csv.reader(open(LI + name)):
        try:
            d = dt.datetime.strptime(r[0], fmt).date().isoformat()
            out[d] = float(r[col])
        except (ValueError, IndexError):
            pass
    return out


def on_days(days, m, lag=0):
    """日付 → 値 の辞書を days に合わせる（ない日は前の値。lag=1 は前の日までの値＝発表の遅れの分）"""
    ks = sorted(m)
    out = []
    for d in days:
        i = bisect.bisect_right(ks, d) - 1 - lag
        out.append(m[ks[i]] if i >= 0 else None)
    return out


def sma(x, n, k):
    w = x[k - n + 1:k + 1]
    return None if k < n - 1 or any(v is None for v in w) else sum(w) / n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--eq87", required=True)
    ap.add_argument("--eqall", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--regs-out", required=True)
    ap.add_argument("--shifts", type=int, default=2000)
    a = ap.parse_args()
    d87, dall = jload(a.eq87), jload(a.eqall)
    k87 = [k for k in d87 if not k.startswith(("今のルール（傾き", "_"))]
    kall = [k for k in dall if not k.startswith(("今のルール（傾き", "_"))]
    days = d87[k87[0]]["days"]
    n = len(days)
    di = {d: i for i, d in enumerate(days)}

    def curve(eq):
        x = np.array([[v if v is not None else np.nan for v in s] for s in eq], float)
        lr = np.nanmean(np.diff(np.log(x), axis=1), axis=0)
        return np.concatenate([[0.0], np.cumsum(np.nan_to_num(lr))])
    E87, EALL = curve(d87[k87[0]]["eq"]), curve(dall[kall[0]]["eq"])
    BR = d87["_breadth"]
    assert BR["days"] == days
    br50, br200, brnl = BR["b50"], BR["b200"], BR["nl"]

    # 87銘柄の等金額の平均（その日にデータのある銘柄の騰落の平均）と、毎日の「下げた銘柄の割合」
    syms = watch87()
    px = {}
    for s in syms:
        p = load_prices(DEFAULT_CACHE, s)
        if p:
            px[s] = dict(zip(p["date"], p["c"]))
    bret, bdown = [0.0] * n, [None] * n
    for k in range(1, n):
        rs = [px[s][days[k]] / px[s][days[k - 1]] - 1 for s in px if days[k] in px[s] and days[k - 1] in px[s] and px[s][days[k - 1]]]
        if len(rs) >= 20:
            bret[k] = float(np.mean(rs))
            bdown[k] = sum(1 for r in rs if r < 0) / len(rs)
    BI = list(np.cumprod([1 + r for r in bret]))
    # 主導株: 87銘柄の126取引日の騰落の上位10銘柄のうち、50日線より下の割合
    cl = {s: [px[s].get(d) for d in days] for s in px}
    ldr = [None] * n
    for k in range(200, n):
        sc = []
        for s, c in cl.items():
            if c[k] is None or c[k - 126] is None or any(v is None for v in c[k - 49:k + 1]):
                continue
            sc.append((c[k] / c[k - 126] - 1, c[k] < sum(c[k - 49:k + 1]) / 50))
        if len(sc) >= 30:
            top = sorted(sc, reverse=True)[:10]
            ldr[k] = sum(1 for _, b in top if b) / 10
    # 指数・信用・恐怖指数
    sox = on_days(days, long_close("^SOX.json"))
    spx = on_days(days, long_close("^GSPC.json"))
    hyg, iei = on_days(days, long_close("HYG.json")), on_days(days, long_close("IEI.json"))
    vix = on_days(days, long_close("^VIX.json"))
    vxn = on_days(days, long_close("^VXN_full.json"))
    v3m_m = csv_close("VIX3M_History.csv", "%m/%d/%Y", 4)
    v3m = on_days(days, v3m_m)
    oas = on_days(days, csv_close("BAMLH0A0HYM2.csv", "%Y-%m-%d", 1), lag=1)   # FRED は1日遅れで出るので前の日の値
    soxx, qqq = load_prices(DEFAULT_CACHE, "SOXX"), load_prices(DEFAULT_CACHE, "QQQ")

    def dist(p):   # オニールの売り抜けの日: 0.2%以上下げて、出来高が前の日より多い日の、直近25取引日の数
        m = {d: i for i, d in enumerate(p["date"])}
        out = [None] * n
        for k, d in enumerate(days):
            i = m.get(d)
            if i is None or i < 26:
                continue
            out[k] = sum(1 for j in range(i - 24, i + 1) if p["c"][j] / p["c"][j - 1] - 1 <= -0.002 and p["v"][j] > p["v"][j - 1])
        return out
    dsoxx, dqqq = dist(soxx), dist(qqq)
    # ツール自身の成績: 87銘柄の口（今のルール、乱数10通り）の、直近20取引日に手じまった売買のうち15%の損切りの割合
    ex_stop, ex_all = np.zeros(n), np.zeros(n)
    for tl in d87[k87[0]]["trades"]:
        for x in tl:
            if x[1] and x[1] in di:
                ex_all[di[x[1]]] += 1
                ex_stop[di[x[1]]] += x[2] == "stop"
    cs_s, cs_a = np.concatenate([[0], np.cumsum(ex_stop)]), np.concatenate([[0], np.cumsum(ex_all)])
    own = [None] * n
    for k in range(20, n):
        tot = cs_a[k + 1] - cs_a[k - 19]
        own[k] = (cs_s[k + 1] - cs_s[k - 19]) / tot if tot >= 10 else None
    # 特殊な下げの印（毎朝のツールと同じ判定）
    sxm = long_close("^SOX.json")
    sxd = sorted(sxm)
    SP = bcm.special_dates(sxd, [sxm[d] for d in sxd])
    # ニュース: 87銘柄のうち、前の7日に悪材料の見出しがあった銘柄の数（2023年〜）
    NH = json.load(open(os.path.expanduser("~/.cache/stock_backtest/news/history_87.json")))["bad"]
    bad_dates = {s: sorted(v) for s, v in NH.items() if isinstance(v, dict)}
    news = [None] * n
    for k, d in enumerate(days):
        if d < "2023-01-09":
            continue
        lo = (dt.date.fromisoformat(d) - dt.timedelta(days=7)).isoformat()
        news[k] = sum(1 for s, v in bad_dates.items() if bisect.bisect_right(v, d) - bisect.bisect_right(v, lo) > 0)

    def ev_window(evs, w=H):
        S = set()
        for e in evs:
            if e in di:
                for j in range(di[e], min(n, di[e] + w)):
                    S.add(j)
        return S
    sigs = {}
    def add(key, lab, cond):
        sigs[key] = (lab, np.array([bool(cond(k)) for k in range(n)]))
    add("b50", "87銘柄の50日線より上が30%未満", lambda k: br50[k] is not None and br50[k] < 0.30)
    add("b200", "87銘柄の200日線より上が40%未満", lambda k: br200[k] is not None and br200[k] < 0.40)
    add("nl10", "87銘柄の60日安値の銘柄が10%以上", lambda k: brnl[k] is not None and brnl[k] >= 0.10)
    add("bsk50", "87銘柄の平均が下向きの50日線の下", lambda k: k >= 60 and BI[k] < sum(BI[k - 49:k + 1]) / 50 < sum(BI[k - 59:k - 9]) / 50)
    add("bsk10", "87銘柄の平均が60日の高値から−10%以下", lambda k: k >= 60 and BI[k] / max(BI[k - 59:k + 1]) - 1 <= -0.10)
    add("bsk5", "87銘柄の平均が20日の高値から−7%以下", lambda k: k >= 20 and BI[k] / max(BI[k - 19:k + 1]) - 1 <= -0.07)
    add("broad", "87銘柄の一斉安（85%以上が下げ、平均−2%以下）が10日に2回以上",
        lambda k: k >= 10 and sum(1 for j in range(k - 9, k + 1) if bdown[j] is not None and bdown[j] >= 0.85 and bret[j] <= -0.02) >= 2)
    add("ldr", "主導株（87銘柄の半年の上げの上位10）の6割以上が50日線の下", lambda k: ldr[k] is not None and ldr[k] >= 0.6)
    add("soxrel", "SOX÷S&P500が下向きの50日線の下",
        lambda k: k >= 60 and None not in (sox[k], spx[k]) and (lambda r: r[-1] < sum(r[-50:]) / 50 < sum(r[-60:-10]) / 50)([sox[j] / spx[j] for j in range(k - 59, k + 1)]))
    add("dsoxx", "SOXXの売り抜けの日が25日に6回以上", lambda k: dsoxx[k] is not None and dsoxx[k] >= 6)
    add("dqqq", "QQQの売り抜けの日が25日に6回以上", lambda k: dqqq[k] is not None and dqqq[k] >= 6)
    add("hy", "ハイイールド債÷中期国債が20日の高値から−1%以下",
        lambda k: k >= 20 and None not in hyg[k - 19:k + 1] and None not in iei[k - 19:k + 1] and (hyg[k] / iei[k]) / max(hyg[j] / iei[j] for j in range(k - 19, k + 1)) - 1 <= -0.01)
    add("oas", "ハイイールド債の利回り差が20日で+0.5%ポイント以上", lambda k: k >= 21 and None not in (oas[k], oas[k - 20]) and oas[k] - oas[k - 20] >= 0.5)
    add("vix25", "VIXが25以上", lambda k: vix[k] is not None and vix[k] >= 25)
    add("vixbk", "VIX÷VIX3Mが1以上（目先の不安が強い）", lambda k: None not in (vix[k], v3m[k]) and days[k] <= max(v3m_m) and vix[k] / v3m[k] >= 1.0)
    add("vxn", "ナスダックの恐怖指数（VXN）が20日の最安値の1.4倍以上", lambda k: k >= 20 and None not in vxn[k - 19:k + 1] and vxn[k] >= 1.4 * min(vxn[k - 19:k + 1]))
    add("own", "87銘柄の口の直近20取引日の手じまいのうち損切りが40%以上", lambda k: own[k] is not None and own[k] >= 0.4)
    w1, w2 = ev_window(BIG4_AVG2), ev_window(BIG4_TWO5)
    add("big4a", "大手4社の決算の翌日の平均が−2%以下（その後20取引日）", lambda k: k in w1)
    add("big4b", "大手4社のうち2社以上が決算の翌日に−5%以下（その後20取引日）", lambda k: k in w2)
    add("sp15", "特殊な下げの印", lambda k: days[k] in SP)
    nthr = [None] * n
    for k in range(n):
        if news[k] is None:
            continue
        past = [x for x in news[max(0, k - 250):k] if x is not None]
        nthr[k] = max(3, np.quantile(past, 0.8)) if len(past) >= 60 else None
    add("news", "悪材料の見出しがあった87銘柄の数が、前の1年の上位20%以上（3銘柄以上、2023年〜）",
        lambda k: news[k] is not None and nthr[k] is not None and news[k] >= nthr[k])
    add("news5", "悪材料の見出しがあった87銘柄が前の7日に5銘柄以上（2023年〜）", lambda k: news[k] is not None and news[k] >= 5)
    # 組み合わせ（どちらかが出たら）
    for k1, k2 in (("b50", "hy"), ("bsk5", "hy"), ("bsk5", "own"), ("ldr", "hy")):
        sigs[k1 + "|" + k2] = (sigs[k1][0] + " または " + sigs[k2][0], sigs[k1][1] | sigs[k2][1])

    # 1. 予測力
    F = np.full(n, np.nan)
    A = np.full(n, np.nan)
    for k in range(n - H):
        F[k] = (E87[k + H] - E87[k]) - (EALL[k + H] - EALL[k])
        A[k] = E87[k + H] - E87[k]
    valid = ~np.isnan(F)
    i21 = max(i for i, d in enumerate(days) if d <= "2021-12-31")
    i23 = min(i for i, d in enumerate(days) if d >= "2023-01-09")

    def diff(S, X, lo=0, hi=None):
        hi = n if hi is None else hi
        m = valid.copy()
        m[:lo] = False
        m[hi:] = False
        s1, s0 = m & S, m & ~S
        if s1.sum() < 10 or s0.sum() < 10:
            return None
        return float(np.nanmean(X[s1]) - np.nanmean(X[s0]))

    def shift_p(S, X, lo=0, hi=None):
        obs = diff(S, X, lo, hi)
        if obs is None:
            return None, None
        hi = n if hi is None else hi
        seg = np.arange(lo, hi)
        Ss = S[lo:hi]
        L_ = len(seg)
        cnt = 0
        for _ in range(a.shifts):
            t = int(RNG.integers(60, L_ - 60))
            Sh = np.zeros(n, bool)
            Sh[lo:hi] = np.roll(Ss, t)
            dv = diff(Sh, X, lo, hi)
            cnt += dv is not None and dv <= obs
        return obs, cnt / a.shifts

    # 2. 早さ: 87銘柄の平均の高値から−20%以上の下げの回
    eps, pk, pki = [], BI[0], 0
    lowk, low = None, None
    for k in range(1, n):
        if BI[k] > pk:
            if lowk is not None and low / pk - 1 <= -0.20:
                eps.append((pki, lowk))
            pk, pki, lowk, low = BI[k], k, None, None
        elif low is None or BI[k] < low:
            low, lowk = BI[k], k
    if lowk is not None and low / pk - 1 <= -0.20:
        eps.append((pki, lowk))
    L = []
    w = L.append
    w("# 早めの合図を探す（2015年〜、合図の予測力・早さ・だまし）\n")
    w(f"- 期間 {days[0]}〜{days[-1]}。87銘柄の口＝毎朝のツールと同じ形の今のルール（87銘柄＋テーマの外、2倍ETF込み、乱数30通りの平均の毎日の騰落）、全業種の口＝毎週選び直す監視銘柄の今のルール。")
    w(f"- 予測力: 合図の日から{H}取引日の「87銘柄の口−全業種の口」の損益の差（対数、%ポイント）と、87銘柄の口の損益。合図の日の平均−そうでない日の平均。"
      f"p値は合図の並びを丸ごとずらした{a.shifts}通りと比べた片側（合図の日の方が悪い向き）。0.05より小さければ偶然では起こりにくい。")
    w("- 早さ: 87銘柄の等金額の平均が高値から−20%以上下げた回（" + "、".join(f"{days[p]}〜{days[t]}（{(BI[t] / BI[p] - 1) * 100:.0f}%）" for p, t in eps) + "）で、高値から底までの間に合図が最初に出た日。"
      "「済んだ割合」はその日までに下げの何割が済んでいたか（0%＝高値の日、100%＝底の日）。")
    w("- だまし: 合図が出始めた日（前の日は出ていない）のうち、その後40取引日の間に87銘柄の平均がその日の値から5%以上下げなかった割合。\n")
    w("## 1. 合図ごとの結果\n")
    w("| 合図 | 出ていた日 | 出始めた回 | 87銘柄の口−全業種の口（20日）の差・p値 | 2015〜21 / 2022〜 | 87銘柄の口（20日）の差・p値 | 2023年〜の87−全業種の差 | 早さ: 高値から何日目（中央値）・済んだ割合（中央値）・合図が出た回 | だまし | 今回（2026-06〜）出始めた日 |")
    w("|---|---|---|---|---|---|---|---|---|---|")
    res = {}
    for key, (lab, S) in sigs.items():
        lo = i23 if key.startswith("news") else 0
        f_, pf = shift_p(S, F, lo)
        a_, pa = shift_p(S, A, lo)
        f1, f2 = diff(S, F, lo, i21 + 1), diff(S, F, max(lo, i21 + 1))
        f23 = diff(S, F, i23)
        starts = [k for k in range(max(1, lo), n) if S[k] and not S[k - 1]]
        fa = [k for k in starts if k + 40 < n and min(BI[k:k + 41]) / BI[k] - 1 > -0.05]
        ear = []
        for p, t in eps:
            if p < lo:
                continue
            hit = next((k for k in range(p, t + 1) if S[k]), None)
            if hit is not None:
                ear.append((hit - p, (BI[p] - BI[hit]) / (BI[p] - BI[t])))
        now = [days[k] for k in starts if days[k] >= "2026-06-01"]
        res[key] = dict(lab=lab, f=f_, pf=pf, a=a_, pa=pa, f1=f1, f2=f2, f23=f23)
        fmt = lambda x: "—" if x is None else f"{x * 100:+.1f}"
        w(f"| {lab} | {S[lo:].mean() * 100:.0f}% | {len(starts)} | {fmt(f_)}pt・{'—' if pf is None else f'{pf:.2f}'} | {fmt(f1)} / {fmt(f2)} | "
          f"{fmt(a_)}pt・{'—' if pa is None else f'{pa:.2f}'} | {fmt(f23)} | "
          + (f"{np.median([e[0] for e in ear]):.0f}日・{np.median([e[1] for e in ear]) * 100:.0f}%・{len(ear)}/{sum(1 for p, t in eps if p >= lo)}回" if ear else "—")
          + f" | {len(fa) / max(1, len([k for k in starts if k + 40 < n])) * 100:.0f}% | " + ("、".join(now[:6]) + ("…" if len(now) > 6 else "") if now else "なし") + " |")
    # 今回の下げの値
    w("\n## 2. 今回の下げの主な日の値（引け）\n")
    w("| 日 | 87銘柄の平均（高値から） | 50日線より上 | 200日線より上 | 60日安値 | 主導株の50日線割れ | HYG÷IEI（20日の高値から） | VIX | VIX÷VIX3M | 悪材料の見出しの銘柄数（7日） | 口の損切りの割合（20日） |")
    w("|---|---|---|---|---|---|---|---|---|---|---|")
    pkk = max(range(di.get("2026-06-01", 0), n), key=lambda k: BI[k] if days[k] <= "2026-10-31" else -1)
    for d in ("2026-06-22", "2026-07-10", "2026-07-29", "2026-08-20", "2026-09-25", "2026-10-07", "2026-10-14", "2026-10-16", "2026-10-22", "2026-10-30", "2026-11-05", "2026-11-13", "2026-11-20"):
        k = di.get(d)
        if k is None:
            continue
        hk = max(range(max(0, k - 120), k + 1), key=lambda j: BI[j])
        r = (hyg[k] / iei[k]) / max(hyg[j] / iei[j] for j in range(k - 19, k + 1)) - 1 if None not in hyg[k - 19:k + 1] else None
        w(f"| {d} | {(BI[k] / BI[hk] - 1) * 100:+.0f}% | {br50[k] * 100:.0f}% | {br200[k] * 100:.0f}% | {brnl[k] * 100:.0f}% | "
          f"{'—' if ldr[k] is None else f'{ldr[k] * 100:.0f}%'} | {'—' if r is None else f'{r * 100:+.1f}%'} | {vix[k]:.1f} | "
          f"{'—' if (v3m[k] is None or d > max(v3m_m)) else f'{vix[k] / v3m[k]:.2f}'} | {news[k] if news[k] is not None else '—'} | {'—' if own[k] is None else f'{own[k] * 100:.0f}%'} |")
    w(f"\n87銘柄の平均の今回の高値: {days[pkk]}")
    w("\n- この結果は数値を条件どおりに計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))
    json.dump({"labels": {k: v[0] for k, v in sigs.items()}, "sets": {k: [days[i] for i in np.nonzero(v[1])[0]] for k, v in sigs.items()},
               "res": res}, open(a.regs_out, "w"), ensure_ascii=False)


if __name__ == "__main__":
    main()
