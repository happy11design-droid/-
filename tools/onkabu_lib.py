#!/usr/bin/env python3
"""恩株ツールの共通部品: 日ごとの特徴（numpy）、合図の判定、結果（何日で2倍か）の計算

backtest_onkabu_search.py（合図・買い方・売り方の探索）と onkabu_scan.py（毎朝の合図の通知）から使う。
特徴はすべてその日の終値までに分かる値。売上の前年同期比はSECへの提出日から使う。
"""
import bisect
import datetime as dt
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backtest_lib import DEFAULT_CACHE
import backtest_onkabu_fast as bfast

H2 = 252   # 2倍を待つ最長の取引日数


def roll_max(x, n):
    return np.array(bfast.rolling_max(list(x), n))


def sma(x, n):
    out = np.full(len(x), np.nan)
    if len(x) >= n:
        cs = np.cumsum(np.insert(x, 0, 0.0))
        out[n - 1:] = (cs[n:] - cs[:-n]) / n
    return out


def ret(c, n):
    out = np.full(len(c), np.nan)
    out[n:] = c[n:] / c[:-n] - 1
    return out


def rev_by_day(dates, rows):
    """日ごとの売上の前年同期比と、その加速（前の決算との差）。決算が120日より古ければ NaN"""
    rs = bfast.rev_series(rows)
    rd = [x[0] for x in rs]
    yoy = np.full(len(dates), np.nan)
    acc = np.full(len(dates), np.nan)
    for i, d in enumerate(dates):
        j = bisect.bisect_right(rd, d) - 1
        if j >= 0 and (dt.date.fromisoformat(d) - dt.date.fromisoformat(rd[j])).days <= 120:
            yoy[i] = rs[j][1]
            if j >= 1:
                acc[i] = rs[j][1] - rs[j - 1][1]
    return yoy, acc


def features(d, rows, spy_up_by_date=None):
    """d: load_prices の日足。rows: 売上の決算（SEC）。返り値は numpy 配列の辞書"""
    c = np.array(d["c"], float)
    v = np.array(d["v"], float)
    f = {"c": c, "o": np.array(d["o"], float), "l": np.array(d["l"], float), "date": d["date"]}
    for n in (5, 21, 63, 126):
        f[f"r{n}"] = ret(c, n)
    hi = roll_max(c, 252)
    f["hi52"] = c / hi
    f["nh"] = c >= hi * 0.999
    f["ma50"] = c / sma(c, 50)
    f["dd20"] = c / roll_max(c, 20)
    dr = np.insert(c[1:] / c[:-1] - 1, 0, 0.0)
    f["gap63"] = roll_max(dr, 63)
    v20, v100 = sma(v, 20), sma(v, 100)
    with np.errstate(divide="ignore", invalid="ignore"):
        f["vr"] = v20 / v100
    f["rev"], f["racc"] = rev_by_day(d["date"], rows)
    if spy_up_by_date is not None:
        f["spy_up"] = np.array([spy_up_by_date.get(x, False) for x in d["date"]])
    return f


def outcomes(c):
    """各日の終値で買ったとき、何取引日で終値が2倍になるか（252日以内。ならなければ大きな数）"""
    n = len(c)
    t2 = np.full(n, 10 ** 6)
    for k in range(H2, 0, -1):
        hit = np.zeros(n, bool)
        hit[:n - k] = c[k:] >= 2 * c[:n - k]
        t2[hit] = k
    return t2


def trade_value(c, t2, T):
    """2倍になったら2倍で、ならなければ T 取引日後の終値で手じまったときの倍率（T日後のデータがなければ NaN）"""
    n = len(c)
    v = np.full(n, np.nan)
    v[:n - T] = c[T:] / c[:n - T]
    v[t2 <= T] = 2.0
    return v


def load_rev_rows(sym, cache=DEFAULT_CACHE):
    p = os.path.join(cache, "onkabu_fund", sym + ".json")
    return [tuple(r) for r in json.load(open(p)).get("rev", [])] if os.path.exists(p) else []


# ---------- 合図 ----------
# 合図は辞書で表す: {"mom": ("r126", 1.0), "hi": "nh"|"near10"|"pull"|None, "rev": None|0.1|0.2|0.3|"acc", "extra": None|"vr"|"gap"|"spy"}

def signal(f, s):
    k, th = s["mom"]
    with np.errstate(invalid="ignore"):
        m = f[k] >= th
        h = s.get("hi")
        if h == "nh":
            m &= f["nh"]
        elif h == "near10":
            m &= f["hi52"] >= 0.90
        elif h == "pull":        # 強い上昇の途中の押し目: 20日高値から−10〜−25%、50日線より上
            m &= (f["dd20"] <= 0.90) & (f["dd20"] >= 0.75) & (f["ma50"] >= 1.0)
        r = s.get("rev")
        if r == "acc":
            m &= f["racc"] >= 0.10
        elif r is not None:
            m &= f["rev"] >= r
        e = s.get("extra")
        if e == "vr":
            m &= f["vr"] >= 1.5
        elif e == "gap":
            m &= f["gap63"] >= 0.10
        elif e == "spy":
            m &= f["spy_up"]
    return m


def describe(s):
    k, th = s["mom"]
    per = {"r21": "1カ月", "r63": "3カ月", "r126": "6カ月"}[k]
    out = [f"{per}で+{th * 100:.0f}%以上"]
    out.append({"nh": "52週高値を更新", "near10": "52週高値の10%以内", "pull": "20日高値から−10〜−25%の押し目（50日線より上）", None: None}[s.get("hi")])
    r = s.get("rev")
    out.append("売上の伸びが加速（+10ポイント以上）" if r == "acc" else f"売上の伸び≧{r * 100:.0f}%" if r is not None else None)
    out.append({"vr": "出来高が増加（20日÷100日≧1.5）", "gap": "3カ月以内に1日+10%以上", "spy": "SPY＞200日線", None: None}[s.get("extra")])
    return "・".join(x for x in out if x)
