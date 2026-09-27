#!/usr/bin/env python3
"""ラシュキ（魔術師リンダ・ラリーの短期売買入門）とボリンジャー（ボリンジャーバンド入門）の数値ルールのバックテスト
（`新分析ツール/引き継ぎ.md` 5-2）

使い方:
  tools/backtest_lib.py fetch            # データの取得（共通。先に1回実行する）
  tools/backtest_swing.py run [--cache DIR] [--out FILE] [--start YYYY-MM-DD] [--end YYYY-MM-DD]

ルールの出典は `書籍ルール/ラシュキ_ルール表.md` と `書籍ルール/ボリンジャー_ルール表.md`。買いのルールのうち、日足で再現できるものだけを検証する
（寄り付き1時間の高値を使うモメンタムピンボール、デイトレードの80-20's、先物・債券・通貨・ティック・TRINのルールは対象外）。

売買の再現（パターンB＝引け後に翌日の予約注文を出す運用）:
  - 「翌日、前日高値の上に逆指値買い」などの注文は、翌日の高値が注文価格に届いたら約定とし、約定値は注文価格（寄り付きが上に窓を開けたら寄り付き）。
  - 「大引けで買い」は当日の引け値、「翌日の寄り付き」は翌日の始値。
  - 損切りの逆指値は、安値が損切り価格に届いたら約定とし、約定値は損切り価格（寄り付きが下に窓を開けたら寄り付き）。
  - 同じ日に仕掛けの逆指値と損切りの両方に届いた場合は、損切りも約定したとみなす（不利な側に倒す）。
損切りは本のルールがあればそれを使い、どの戦略も仕掛け値の15%下（ユーザー決定）を上限とする。建玉はリスク2%・損切り15%から逆算（資金の13.3%、7銘柄まで）。
"""
import argparse
import datetime as dt
import operator
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backtest_lib import (COSTS, DEFAULT_CACHE, Reporter, coverage, is_member, sliding, load_prices, load_universe, market_regime,
                          pct, sma, spy_benchmark, stats)

RISK = 0.02
STOP_MAX = 0.15
COST = COSTS[2]
MAX_HOLD = 60


# ---------- 指標 ----------

def ema(x, n):
    out, k, e = [None] * len(x), 2 / (n + 1), None
    for i, v in enumerate(x):
        e = v if e is None else e + k * (v - e)
        if i >= n - 1:
            out[i] = e
    return out


def wilder(x, n):
    """ワイルダーの平滑化（最初のn本は単純平均）"""
    out, s = [None] * len(x), None
    for i in range(len(x)):
        if i == n - 1:
            s = sum(x[:n]) / n
        elif i >= n:
            s = (s * (n - 1) + x[i]) / n
        out[i] = s
    return out


def adx_di(h, l, c, n_adx, n_di=None):
    """ADX（n_adx期間）と +DI・−DI（n_di期間、省略時はn_adx）"""
    n_di = n_di or n_adx
    m = len(c)
    tr, pdm, mdm = [0.0] * m, [0.0] * m, [0.0] * m
    for i in range(1, m):
        tr[i] = max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1]))
        up, dn = h[i] - h[i - 1], l[i - 1] - l[i]
        pdm[i] = up if up > dn and up > 0 else 0.0
        mdm[i] = dn if dn > up and dn > 0 else 0.0

    def di(n):
        a, p, q = wilder(tr[1:], n), wilder(pdm[1:], n), wilder(mdm[1:], n)
        pdi = [None] + [100 * p[i] / a[i] if a[i] else None for i in range(m - 1)]
        mdi = [None] + [100 * q[i] / a[i] if a[i] else None for i in range(m - 1)]
        return pdi, mdi

    pdi, mdi = di(n_adx)
    dx = [abs(p - q) / (p + q) * 100 if p is not None and q is not None and p + q else None for p, q in zip(pdi, mdi)]
    first = next(i for i, v in enumerate(dx) if v is not None)
    adx = [None] * first + wilder([v or 0 for v in dx[first:]], n_adx)
    if n_di != n_adx:
        pdi, mdi = di(n_di)
    return adx, pdi, mdi


def stdev(x, n):
    out = [None] * len(x)
    for i in range(n - 1, len(x)):
        w = x[i - n + 1:i + 1]
        mu = sum(w) / n
        out[i] = (sum((v - mu) ** 2 for v in w) / n) ** 0.5
    return out


def rsi_simple(x, n):
    """ラシュキの3日RSI（ROCRSI）用。ワイルダーの平滑化"""
    out = [None] * len(x)
    g = [0.0] + [max(x[i] - x[i - 1], 0) for i in range(1, len(x))]
    lo = [0.0] + [max(x[i - 1] - x[i], 0) for i in range(1, len(x))]
    ag, al = wilder(g[1:], n), wilder(lo[1:], n)
    for i in range(1, len(x)):
        a, b = ag[i - 1], al[i - 1]
        if a is not None:
            out[i] = 100.0 if b == 0 else 100 - 100 / (1 + a / b)
    return out


def parabolic(h, l, step=0.02, cap=0.2):
    """パラボリックSAR（買い側だけを使う）。反転した日は売り側のSARを返す。
    ルール表の上限は「2.0」だが、ボリンジャーが引くワイルダーの標準（加速因子の上限0.2）で計算する"""
    m = len(h)
    sar, up = [None] * m, True
    ep, af, s = h[0], step, l[0]
    for i in range(1, m):
        s = s + af * (ep - s)
        if up:
            s = min(s, l[i - 1], l[i - 2] if i >= 2 else l[i - 1])
            if l[i] < s:
                up, s, ep, af = False, ep, l[i], step
            elif h[i] > ep:
                ep, af = h[i], min(af + step, cap)
        else:
            s = max(s, h[i - 1], h[i - 2] if i >= 2 else h[i - 1])
            if h[i] > s:
                up, s, ep, af = True, ep, h[i], step
            elif l[i] < ep:
                ep, af = l[i], min(af + step, cap)
        sar[i] = (s, up)
    return sar


def prepare(d):
    h, l, c, v = d["h"], d["l"], d["c"], d["v"]
    n = len(c)
    d["vol50"] = [None] + sma(v, 50)[:-1]
    d["ma200"] = sma(c, 200)
    d["ema20"] = ema(c, 20)
    d["adx14"], _, _ = adx_di(h, l, c, 14)
    d["adx12"], d["pdi28"], d["mdi28"] = adx_di(h, l, c, 12, 28)
    # ストキャスティクス（アンチ）: 7期間%Kを4期間で平滑化、%Dはその10期間平均
    raw = [None] * n
    for i in range(6, n):
        hh, ll = max(h[i - 6:i + 1]), min(l[i - 6:i + 1])
        raw[i] = 100 * (c[i] - ll) / (hh - ll) if hh > ll else 50.0
    k = [None] * n
    for i in range(9, n):
        k[i] = sum(raw[i - 3:i + 1]) / 4
    dd = [None] * n
    for i in range(18, n):
        dd[i] = sum(k[i - 9:i + 1]) / 10
    d["stk"], d["std"] = k, dd
    d["lo20"] = sliding(l, 20, operator.le, False)                                      # 前日までの20日安値
    d["lo20_age"] = [None] * n                                                          # その安値が何日前か
    for i in range(20, n):
        w = l[i - 20:i]
        d["lo20_age"][i] = 20 - max(j for j in range(20) if w[j] == min(w))
    d["hi20"] = sliding(h, 20, operator.ge, False)
    roc1 = [0.0] + [c[i] / c[i - 1] - 1 for i in range(1, n)]
    d["rocrsi"] = rsi_simple(roc1, 3)
    # ボリンジャー
    mid, sd = sma(c, 20), stdev(c, 20)
    d["bb_mid"] = mid
    d["bb_up"] = [m + 2 * s if m is not None else None for m, s in zip(mid, sd)]
    d["bb_dn"] = [m - 2 * s if m is not None else None for m, s in zip(mid, sd)]
    d["pctb"] = [(c[i] - d["bb_dn"][i]) / (d["bb_up"][i] - d["bb_dn"][i]) if mid[i] is not None and d["bb_up"][i] > d["bb_dn"][i] else None for i in range(n)]
    d["bw"] = [(d["bb_up"][i] - d["bb_dn"][i]) / mid[i] if mid[i] else None for i in range(n)]
    bw = [x if x is not None else float("inf") for x in d["bw"]]
    d["bw_min126"] = [x if i >= 145 else None for i, x in enumerate(sliding(bw, 126, operator.le, True))]   # 過去6カ月（約126日）の最小
    tp = [(h[i] + l[i] + c[i]) / 3 for i in range(n)]
    mfi = [None] * n
    for i in range(11, n):
        pos = sum(tp[j] * v[j] for j in range(i - 9, i + 1) if tp[j] > tp[j - 1])
        neg = sum(tp[j] * v[j] for j in range(i - 9, i + 1) if tp[j] < tp[j - 1])
        mfi[i] = 100.0 if neg == 0 else 100 - 100 / (1 + pos / neg)
    d["mfi10"] = mfi
    ii = [((2 * c[i] - h[i] - l[i]) / (h[i] - l[i]) * v[i]) if h[i] > l[i] else 0.0 for i in range(n)]
    d["ii21"] = [sum(ii[i - 20:i + 1]) / sum(v[i - 20:i + 1]) if i >= 20 and sum(v[i - 20:i + 1]) else None for i in range(n)]
    d["sar"] = parabolic(h, l)
    return d


# ---------- 売買の再現 ----------
# order(i, s) -> None または dict:
#   rank: 並べ替え用の値（小さいほど優先）
#   kind: "stop"（翌日 trigger 以上で逆指値買い）/ "stop_after_break"（翌日の安値が trigger を割った後に trigger へ戻したら買い＝タートルスープ）
#         / "open"（翌日の寄り付き）/ "close"（当日の引け）
#   trigger: 逆指値の価格、need_open_below: 翌日の寄り付きがこの価格以下のときだけ有効（ADXギャッパー）
#   stop: 本の損切り価格（なければNone。15%下が上限）
# exit(j, s, k, t) -> None / ("open", 理由)＝翌日の寄り付きで手じまい / ("close", 理由)＝当日の引けで手じまい
#   t は保有中の状態（px, stop など）。trail(j, s, t) があれば毎日引け後に損切り価格を更新する


def simulate(data, members, order, exit_fn, start, end, allow=None, trail=None, max_hold=MAX_HOLD):
    trades = []
    for sym, s in data.items():
        o, h, l, c, dates = s["o"], s["h"], s["l"], s["c"], s["date"]
        n, i = len(c), 200
        while i < n - 1:
            d = dates[i]
            if d < start or d > end or not liquid(s, i, members[sym]) or (allow and not allow(d)):
                i += 1
                continue
            od = order(i, s)
            if od is None:
                i += 1
                continue
            kind = od["kind"]
            if kind == "close":
                e, px = i, c[i]
            else:
                e = i + 1
                if kind == "open":
                    px = o[e]
                elif kind == "stop":
                    if od.get("need_open_below") is not None and o[e] > od["need_open_below"]:
                        i += 1
                        continue
                    if h[e] < od["trigger"]:
                        i += 1
                        continue
                    px = max(o[e], od["trigger"])
                else:  # stop_after_break
                    if not (l[e] < od["trigger"] <= h[e]):
                        i += 1
                        continue
                    px = od["trigger"]
            floor = px * (1 - STOP_MAX)
            stop = max(od["stop"], floor) if od.get("stop") is not None else floor
            t = {"px": px, "stop": stop, "entry": e}
            j, out_px, why = e, None, "打ち切り"
            # 仕掛けた日に損切りにも届いたか（寄り付き・逆指値で入った日の安値が損切り以下）
            if kind != "close" and l[e] <= stop:
                j, out_px, why = e, min(stop, px), "損切り"
            else:
                r = exit_fn(e, s, 0, t)          # 仕掛けた日の引けで手じまい条件が出たか（翌日の寄り付きで手じまう）
                if r:
                    t["pending"] = r[1]
                if trail:
                    trail(e, s, t)
                for k in range(1, max_hold + 1):
                    j = e + k
                    if j >= n:
                        break
                    if pend := t.get("pending"):
                        j, out_px, why = j, o[j], pend
                        break
                    if l[j] <= t["stop"]:
                        out_px, why = min(o[j], t["stop"]), "損切り"
                        break
                    r = exit_fn(j, s, k, t)
                    if r:
                        if r[0] == "close":
                            out_px, why = c[j], r[1]
                            break
                        t["pending"] = r[1]
                    if trail:
                        trail(j, s, t)
                else:
                    j = min(e + max_hold, n - 1)
                    out_px = c[j]
            if out_px is None:
                break  # データ終端で手じまいが未確定
            trades.append({"sym": sym, "in": dates[e], "out": dates[j], "px": px, "ret": out_px / px - 1,
                           "days": j - e, "rank": od["rank"], "why": why})
            i = j + 1
    trades.sort(key=lambda t: (t["out"], t["sym"]))
    return trades


def liquid(s, i, spans):
    return (s["vol50"][i] is not None and s["c"][i] >= 5 and s["vol50"][i] >= 250_000
            and is_member(spans, s["date"][i]))


# ---------- 手じまい ----------

def X_next_open(j, s, k, t):
    return ("open", "翌日寄り付き") if k == 0 else None


def X_open_after(n_days):
    return lambda j, s, k, t: ("open", "時間") if k >= n_days else None


def trail_2day(j, s, t):
    """非常時ストップ（2日チャネル、p.120）: 直近2日間の安値を割ったら手じまい。損切り価格を毎日引き上げる"""
    if j >= 1:
        t["stop"] = max(t["stop"], min(s["l"][j], s["l"][j - 1]))


def trail_sar(j, s, t):
    """パラボリックSARで損切り価格を引き上げる（ボリンジャー p.1518ほか）"""
    v = s["sar"][j]
    if v and v[1]:
        t["stop"] = max(t["stop"], v[0])


def X_nr4_time(j, s, k, t):
    """値幅収縮: 仕掛けから2日で利が乗らなければ大引けで手じまい（p.81）"""
    return ("close", "時間") if k == 2 and s["c"][j] <= t["px"] else None


def X_upper_band(j, s, k, t):
    return ("open", "上部バンド") if s["pctb"][j] is not None and s["pctb"][j] >= 1.0 else None


def X_donchian_low(j, s, k, t):
    return ("open", "4週安値割れ") if s["lo20"][j] is not None and s["c"][j] < s["lo20"][j] else None


X_NONE = lambda j, s, k, t: None


# ---------- ラシュキ ----------

def O_holy_grail(i, s):
    """聖杯（p.45, p.47）: 14期間ADX≧30かつ上昇中、価格が20期間EMAまで押した日の翌日、その日の高値に逆指値買い。
    損切りは押した日の安値の下（ルール表に位置の記載がないため、非常時ストップ＝2日チャネルと15%で代用）"""
    a, a1, e = s["adx14"][i], s["adx14"][i - 1], s["ema20"][i]
    if None in (a, a1, e) or a < 30 or a <= a1 or s["l"][i] > e:
        return None
    return {"rank": -a, "kind": "stop", "trigger": s["h"][i], "stop": None}


def O_adx_gapper(i, s):
    """ADXギャッパー（p.49-51）: 12期間ADX≧30、28期間+DI>−DI。翌日、前日安値より下に寄り付いたら、前日安値に逆指値買い"""
    a, p, m = s["adx12"][i], s["pdi28"][i], s["mdi28"][i]
    if None in (a, p, m) or a < 30 or p <= m:
        return None
    return {"rank": -a, "kind": "stop", "trigger": s["l"][i], "need_open_below": s["l"][i], "stop": None}


def O_anti(i, s):
    """アンチ（p.40-41）: %D（10期間）が上向きで、%K（7期間・4期間平滑化）が3日以上下落。翌日、前日高値に逆指値買い"""
    k, dd = s["stk"], s["std"]
    if i < 22 or None in (dd[i], dd[i - 1], k[i - 3]):
        return None
    if not (dd[i] > dd[i - 1] and k[i] < k[i - 1] < k[i - 2] < k[i - 3]):
        return None
    return {"rank": k[i], "kind": "stop", "trigger": s["h"][i], "stop": None}


def O_turtle_soup(i, s):
    """タートルスープ（p.17-19）: 前日までの20日安値が今日を含めて4営業日以上前。翌日、安値がその20日安値を割った後に
    20日安値まで戻したら買い。損切りはその日の安値の下（翌日以降、安値を割ったら手じまい）"""
    lo, age = s["lo20"][i + 1] if i + 1 < len(s["c"]) else None, s["lo20_age"][i + 1] if i + 1 < len(s["c"]) else None
    if lo is None or age is None or age < 4:
        return None
    return {"rank": 0, "kind": "stop_after_break", "trigger": lo, "stop": None, "day_low_stop": True}


def trail_turtle(j, s, t):
    """タートルスープの損切り: 仕掛けた日の安値の1ティック下（p.17-18）。その後は2日チャネル（p.120）"""
    if j == t["entry"]:
        t["stop"] = max(t["stop"], s["l"][j] - 0.01)
    else:
        trail_2day(j, s, t)


def O_nr4_id(i, s):
    """値幅収縮（ID・NR4、p.80-81）: はらみ足かつ直近4日で最小の値幅。翌日、高値に逆指値買い、損切りはその日の安値の下"""
    h, l = s["h"], s["l"]
    if i < 4:
        return None
    rng = [h[k] - l[k] for k in range(i - 3, i + 1)]
    if not (h[i] < h[i - 1] and l[i] > l[i - 1] and rng[-1] == min(rng)):
        return None
    return {"rank": rng[-1] / s["c"][i], "kind": "stop", "trigger": h[i], "stop": l[i] - 0.01}


def O_nr7(i, s):
    """NR7（p.84）: 直近7日で最小の値幅。翌日、高値に逆指値買い（ブレイクアウト）、損切りはその日の安値の下"""
    h, l = s["h"], s["l"]
    if i < 7:
        return None
    rng = [h[k] - l[k] for k in range(i - 6, i + 1)]
    if rng[-1] != min(rng):
        return None
    return {"rank": rng[-1] / s["c"][i], "kind": "stop", "trigger": h[i], "stop": l[i] - 0.01}


def O_gap_failure(i, s):
    """窓空けの失敗（鞭打ち p.54／付録 p.119）: 前日安値より下に寄り付き、値幅の上半分で引けたら大引けで買い"""
    o, h, l, c = s["o"][i], s["h"][i], s["l"][i], s["c"][i]
    if not (o < s["l"][i - 1] and h > l and c >= l + 0.5 * (h - l) and c > o):
        return None
    return {"rank": (c - o) / o * -1, "kind": "close", "stop": None}


def O_rocrsi(i, s):
    """ROCRSI（付録 p.111）: 1日ROCの3日RSI＜30で、翌日の寄り付きで買う"""
    r = s["rocrsi"][i]
    if r is None or r >= 30:
        return None
    return {"rank": r, "kind": "open", "stop": None}


def O_adx_pullback(i, s):
    """ADX単体（付録 p.117）: 14期間ADX≧30で上昇中、終値が2日前の終値より下で引けたら大引けで買い"""
    a, a1 = s["adx14"][i], s["adx14"][i - 1]
    if None in (a, a1) or a < 30 or a <= a1 or s["c"][i] >= s["c"][i - 2]:
        return None
    return {"rank": -a, "kind": "close", "stop": None}


# ---------- ボリンジャー ----------

def O_squeeze(i, s):
    """メソッドI（スクイーズ、p.1477ほか）: バンド幅が過去6カ月の最低で、終値が上部バンドを上抜けたら翌日の寄り付きで買う。
    ルール表の「スクイーズ非発生時は見送り」（p.1547）に従い、上抜けの前日までの5日以内にバンド幅が6カ月最低だったことを条件にする"""
    bw, mn = s["bw"], s["bw_min126"]
    if mn[i] is None or s["c"][i] <= s["bb_up"][i]:
        return None
    if not any(bw[k] is not None and mn[k] is not None and bw[k] <= mn[k] for k in range(i - 5, i + 1)):
        return None
    return {"rank": -s["pctb"][i], "kind": "open", "stop": None}


def O_method2(i, s):
    """メソッドII（p.1579-1583）: %b>0.8かつMFI(10)>80のシグナルの後、最初の押し（前日比下落）を待ち、
    次に上昇した日の翌日の寄り付きで買う（シグナルから10日以内）"""
    c = s["c"]
    if i < 25 or c[i] <= c[i - 1] or c[i - 1] >= c[i - 2]:
        return None                       # 今日が上昇、前日が下落（押しの後の最初の上昇日）
    p = i - 1
    while p > i - 10 and c[p - 1] < c[p - 2]:
        p -= 1                            # 押しの始まりの日
    for m in range(p - 1, p - 11, -1):    # 押しの前10日以内にシグナル、その間に別の押しがない（最初の押し）
        pb, mf = s["pctb"][m], s["mfi10"][m]
        if pb is not None and mf is not None and pb > 0.8 and mf > 80:
            return {"rank": -mf, "kind": "open", "stop": None}
        if c[m] < c[m - 1]:
            return None
    return None


def O_method3(i, s):
    """メソッドIII（反転、p.1589-1590）: %b<0.05かつ21日II%>0で翌日の寄り付きで買う"""
    pb, ii = s["pctb"][i], s["ii21"][i]
    if pb is None or ii is None or pb >= 0.05 or ii <= 0:
        return None
    return {"rank": pb, "kind": "open", "stop": None}


def O_donchian(i, s):
    """ドンチャンの4週ルール（p.1450）: 終値が過去4週（20日）の高値を上抜けたら翌日の寄り付きで買い、4週安値割れで手じまい"""
    hi = s["hi20"][i]
    if hi is None or s["c"][i] <= hi:
        return None
    return {"rank": 0, "kind": "open", "stop": None}


# ---------- 実行 ----------

def cmd_run(a):
    members, data = load_universe(a.cache, min_bars=260)
    for s in data.values():
        prepare(s)
    spy = load_prices(a.cache, "SPY")
    regime = market_regime(spy)
    days = [d for d in spy["date"] if a.start <= d <= a.end]
    spy_cagr, spy_mdd = spy_benchmark(spy, days)
    n_in, n_got = coverage(members, data, a.start, a.end)
    years = len(days) / 252
    halves = [("前半", a.start, "2020-12-31"), ("後半", "2021-01-01", a.end)]

    L = []
    w = L.append
    rep = Reporter(w, data, days, halves, years, cost=COST, risk=RISK)
    w("---\ntype: backtest\ntitle: ラシュキ・ボリンジャー 数値ルールのバックテスト\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_swing.py\n---\n")
    w("# ラシュキ・ボリンジャー 数値ルールのバックテスト\n")
    w(f"- 期間: {days[0]} 〜 {days[-1]}（{len(days)}取引日）。前半＝〜2020年、後半＝2021年〜。")
    w(f"- 対象: その日にS&P500の構成銘柄だった銘柄（株価≧5ドル、50日平均出来高≧25万株）。期間中の構成銘柄 {n_in} のうち価格を取得できたのは {n_got}（{pct(n_got / n_in)}）。")
    w("- 価格: 配当・分割調整済み。片道0.1%のコスト込み。")
    w("- 売買: 引け後に翌日の予約注文を出す運用（パターンB）を日足で再現。逆指値買いは翌日の高値が注文価格に届いたら約定（上に窓を開けたら寄り付き）、"
      "損切りの逆指値は安値が届いたら約定（下に窓を開けたら寄り付き）。仕掛けた日に損切りにも届いたら損切りとみなす。")
    w("- 損切り: 本のルールがあればそれを使い、どの戦略も仕掛け値の15%下（ユーザー決定）を上限とする。"
      f"手じまい条件が{MAX_HOLD}取引日出なければ打ち切り。建玉はリスク2%・損切り15%から逆算（資金の13.3%、7銘柄まで）。")
    w("- 同じ日の候補の選び方はルール表にないため、「ルールの強さの順（ADXの高い順など。タートルスープ・ドンチャンは強さの基準がないので銘柄名の順）」と「ランダムな順（10通りの中央値と幅）」の両方を出す。")
    w("- 対象外: 寄り付き1時間の値動きを使うルール（モメンタムピンボール）、デイトレード（80-20's）、先物・債券・通貨・ティック・TRIN・ブレドス指標のルール、売り（空売り）のルール。")
    w(f"- 比較: 同期間のSPY買い持ち 年率 {pct(spy_cagr)}、最大下落率 {pct(spy_mdd)}（配当込み）\n")

    def run(order, exit_fn=X_NONE, trail=None, allow=None, max_hold=MAX_HOLD):
        return simulate(data, members, order, exit_fn, a.start, a.end, allow=allow, trail=trail, max_hold=max_hold)

    not_up = lambda d: regime.get(d) != "上昇"

    raschke = [
        ("聖杯（ADX≧30上昇中・20EMAへの押し → 翌日高値に逆指値買い）・2日チャネルで手じまい", O_holy_grail, X_NONE, trail_2day, None),
        ("ADXギャッパー（ADX≧30・+DI>−DI・前日安値の下に寄り付き → 前日安値に逆指値買い）・2日チャネル", O_adx_gapper, X_NONE, trail_2day, None),
        ("アンチ（%D上向き・%Kが3日下落 → 翌日高値に逆指値買い）・2日チャネル", O_anti, X_NONE, trail_2day, None),
        ("タートルスープ（20日安値割れからの戻り）・当日安値の下で損切り→2日チャネル", O_turtle_soup, X_NONE, trail_turtle, None),
        ("値幅収縮 ID・NR4（翌日高値に逆指値買い）・安値の下で損切り・2日で利が乗らなければ手じまい→2日チャネル", O_nr4_id, X_nr4_time, trail_2day, None),
        ("NR7（翌日高値に逆指値買い）・安値の下で損切り・2日チャネル", O_nr7, X_NONE, trail_2day, None),
        ("窓空けの失敗（前日安値の下で寄り付き・上半分で引け → 大引けで買い）・翌日寄り付きで手じまい（p.119）", O_gap_failure, X_next_open, None, None),
        ("ROCRSI（1日ROCの3日RSI<30 → 翌日寄り付きで買い）・翌日寄り付きで手じまい（p.111）", O_rocrsi, X_next_open, None, None),
        ("ADX単体（ADX≧30上昇中・2日前より安く引け → 大引けで買い）・2日チャネル", O_adx_pullback, X_NONE, trail_2day, None),
    ]
    bollinger = [
        ("メソッドI スクイーズ（6カ月最低のバンド幅から上部バンド上抜け）・パラボリックSARで手じまい", O_squeeze, X_NONE, trail_sar, None),
        ("メソッドII（%b>0.8かつMFI>80の後の最初の押しから上昇）・パラボリックSAR", O_method2, X_NONE, trail_sar, None),
        ("メソッドIII 反転（%b<0.05かつ21日II%>0）・上部バンドで手じまい", O_method3, X_upper_band, None, None),
        ("メソッドIII 反転・上部バンドで手じまい・上昇局面以外だけ（ボリンジャーの役割＝レンジ相場）", O_method3, X_upper_band, None, not_up),
        ("ドンチャンの4週ルール（20日高値上抜け）・4週安値割れで手じまい", O_donchian, X_donchian_low, None, None),
    ]

    results = {}
    for title, rows in (("1. ラシュキ（魔術師リンダ・ラリーの短期売買入門）", raschke), ("2. ボリンジャー（ボリンジャーバンド入門）", bollinger)):
        w(f"## {title}\n")
        rep.header("ルールの強さの順")
        for label, order, ex, tr_fn, allow in rows:
            tr = run(order, ex, tr_fn, allow)
            results[label] = tr
            rep.line(label, tr, STOP_MAX)
        w("")

    w("## 3. 市場全体の局面別（1トレード＝1件、片道0.1%）\n")
    w("仕掛けた日の局面（SPYの30週線で近似したワインスタインのステージ）で分ける。1トレード平均が区間ごとプラスの局面があるかを見る。\n")
    w("| 戦略 | 上昇: 件数 / 平均（95%区間）/ PF | 横ばい: 件数 / 平均 / PF | 下落: 件数 / 平均 / PF |")
    w("|---|---|---|---|")
    for label, tr in results.items():
        cells = []
        for r in ("上昇", "横ばい", "下落"):
            st = stats([t for t in tr if regime.get(t["in"]) == r], COST)
            cells.append(f"{st['n']} / {pct(st['mean'], 2)}（{pct(st['mean_ci'][0], 2)}〜{pct(st['mean_ci'][1], 2)}）/ {st['pf']:.2f}" if st else "0")
        w(f"| {label} | " + " | ".join(cells) + " |")

    w("\n## 4. 注意\n")
    w("- 日足だけで逆指値の約定を再現しているため、同じ日の値動きの順番（先に高値か安値か）は分からない。仕掛けと損切りの両方に届いた日は損切りとみなして不利側に倒した。")
    w("- パラボリックSARの加速因子の上限は、ルール表の「2.0」ではなくワイルダーの標準の0.2で計算した（2.0だと損切り価格がすぐ株価に追いつき、実用にならないため。原本の確認が必要）。")
    w("- 聖杯・ADXギャッパー・アンチなど、本では手じまい方法が「目標値」「トレーリング」などで数値化されていないものは、ルール表にある非常時ストップ（2日チャネル、p.120）で統一した。")
    w("- 同じ条件を何通りも試すと、偶然良かった条件を選んでしまう（過剰適合）。前半・後半の両方で成り立つかを重視すること。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/ラシュキ・ボリンジャー.md")
    r.add_argument("--start", default="2015-01-02")
    r.add_argument("--end", default=dt.date.today().isoformat())
    cmd_run(ap.parse_args())


if __name__ == "__main__":
    main()
