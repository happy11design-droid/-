#!/usr/bin/env python3
"""今後3〜5日で上がる確率（銘柄ごと）を、オシレーター・本のルールの合図・決算などの材料から出し、当たるかを確かめる（検討中）

使い方:
  tools/backtest_lib.py fetch                  # S&P500の構成銘柄の日足（共通）
  tools/earnings_history.py fetch              # 過去の決算発表日とEPSのサプライズ（初回は約1時間）
  tools/swing_odds.py backtest [--out FILE]    # 2015〜2021年で点数の作り方を決め、2022年以降で確かめる（約15分）
                                               # 点数の表（tools/swing_odds_model.json）とレポートを書く
  tools/swing_odds.py today <出力.md> [--asof YYYY-MM-DD] [--tickers A,B]   # 監視銘柄の今日の確率（約2分）

「上がる」の決め方（3日・5日のそれぞれ）:
  引け→引け   … h日後の終値 > 今日の終値
  翌寄り→引け … h日後の終値 > 翌日の始値（朝の結果を見て翌日の寄り付きで買い、h日目の引けで売る。実際に売買できる形）
  対市場       … h日間の騰落率（引け→引け）> SPYの同じ期間の騰落率

使う数値（すべて今日の引けまでに分かるもの）:
  - 値動き・位置: daily_odds.py の12個（RSI(2)・引けの位置・連続日数・5日線/50日線からの離れ・出来高・20日の騰落率・
    値動きの大きさ・S&P500のRSI(2)と騰落率・VIX）
  - オシレーター: RSI(14)・MACD（線とヒストグラム）・週足相当のMACDヒストグラム・ストキャスティクス・%b・バンド幅・ADX(14)・
    MFI(10)・II%(21)・RS順位・上げ下げの出来高比・52週高値からの離れ・30週線（150日線）からの離れと傾き・窓の大きさ
  - 採用ルールの合図: ボリンジャーIII（A・B）・ミネルヴィニのベースの上抜け・ワインスタイン10週・急落の底・新高値V2・トレンドテンプレート
  - 採用していない本のルール: ポケットピボット・買える窓開け・聖杯・アンチ・NR7・ID/NR4・窓空けの失敗・ボリンジャーのメソッドI/II・
    ドンチャン4週・コナーズのRSI(2)≦5（200日線の上）・出来高2倍の大陰線・RSラインの52週高値
  - 材料（決算）: 決算の反応日（発表後の最初の取引）・前回の決算からの日数・前回のサプライズ%・前回の決算の反応・次の決算が5日以内か
  - 材料（値動き）: 3%以上の窓（上・下）・出来高2倍・ATR2本分以上の大陽線・大陰線

点数は2通り:
  全部   … すべての数値（段階ごとのロジスティック回帰）
  安定   … 設計期間を前半（2015〜2018年）と後半（2019〜2021年）に分け、どちらでも同じ向きに効いた数値だけ
数値と事実だけで、売買の判断はしない。NotebookLMは使わない。
"""
import argparse
import bisect
import datetime as dt
import json
import os
import sys
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_connors as bc
import backtest_minervini2 as bm2
import backtest_swing as bs
import backtest_trend as bt
from backtest_compare2 import add_udvr
from backtest_crash import C3R10
from backtest_lib import DEFAULT_CACHE, is_member, load_members, load_prices, rsi_wilder, sma
from daily_odds import auc, fit, market_feats, to_design
from earnings_history import load_earnings

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
MODEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "swing_odds_model.json")
REPORT = os.path.join(ROOT, "新分析ツール", "バックテスト結果", "今後3〜5日の上げ下げの確率.md")
DESIGN_END, VERIFY_START, HALF = "2021-12-31", "2022-01-01", "2018-12-31"
COST = 0.001
HORIZONS = (3, 5)

CONT = [  # (キー, 表示名, 区分)
    ("rsi", "RSI(2)", "値動き"), ("r1", "今日の値動き（ATR）", "値動き"), ("clv", "引けの位置", "値動き"),
    ("streak", "連続の上昇・下落の日数", "値動き"), ("d5", "5日線からの離れ（ATR）", "値動き"), ("d50", "50日線からの離れ（ATR）", "値動き"),
    ("vr", "出来高（50日平均の何倍）", "値動き"), ("r20", "20日の騰落率", "値動き"), ("atrp", "値動きの大きさ（ATR÷株価）", "値動き"),
    ("spy_rsi", "S&P500のRSI(2)", "市場"), ("spy_r1", "S&P500の今日の騰落率", "市場"), ("vix", "VIX", "市場"),
    ("spy_ma", "S&P500の30週線からの離れ", "市場"),
    ("rsi14", "RSI(14)", "オシレーター"), ("macd", "MACD（ATR）", "オシレーター"), ("macd_h", "MACDヒストグラム（ATR）", "オシレーター"),
    ("wmacd_h", "週足相当のMACDヒストグラム（ATR）", "オシレーター"), ("stoch", "ストキャスティクス", "オシレーター"),
    ("pctb", "%b", "オシレーター"), ("bwr", "バンド幅（6カ月の最小の何倍）", "オシレーター"), ("adx", "ADX(14)", "オシレーター"),
    ("mfi", "MFI(10)", "オシレーター"), ("ii", "II%(21)", "オシレーター"), ("rs", "RS順位", "オシレーター"),
    ("udvr", "上げ下げの出来高比（50日）", "オシレーター"), ("hi52", "52週高値からの離れ", "オシレーター"),
    ("d150", "30週線からの離れ", "オシレーター"), ("s150", "30週線の傾き（20日）", "オシレーター"), ("gap", "今日の窓（ATR）", "値動き"),
    ("since_earn", "前回の決算からの日数", "決算"), ("surprise", "前回のEPSサプライズ%", "決算"), ("earn_react", "前回の決算の反応（ATR）", "決算"),
]
FLAGS = [
    ("tt", "トレンドテンプレート", "採用ルール"), ("boll3", "ボリンジャーIII（A）", "採用ルール"), ("boll3b", "ボリンジャーIII（B）", "採用ルール"),
    ("mnv", "ミネルヴィニのベースの上抜け", "採用ルール"), ("wein", "ワインスタイン10週", "採用ルール"), ("crash", "急落の底", "採用ルール"),
    ("v2", "新高値V2", "採用ルール"),
    ("pp", "ポケットピボット", "未採用の本"), ("bgu", "買える窓開け", "未採用の本"), ("grail", "聖杯（ラシュキ）", "未採用の本"),
    ("anti", "アンチ（ラシュキ）", "未採用の本"), ("nr7", "NR7", "未採用の本"), ("nr4", "ID/NR4", "未採用の本"),
    ("gapfail", "窓空けの失敗", "未採用の本"), ("m1", "ボリンジャーのメソッドI（スクイーズ）", "未採用の本"),
    ("m2", "ボリンジャーのメソッドII", "未採用の本"), ("donch", "ドンチャン4週", "未採用の本"), ("k1", "コナーズRSI(2)≦5（200日線の上）", "未採用の本"),
    ("bear", "出来高2倍の大陰線", "未採用の本"), ("rsl", "RSラインの52週高値", "未採用の本"),
    ("earn_day", "決算の反応日", "材料"), ("earn_soon", "次の決算が5日以内", "材料"), ("gap_up", "3%以上の上の窓", "材料"),
    ("gap_dn", "3%以上の下の窓", "材料"), ("vol2", "出来高2倍", "材料"), ("big_up", "大陽線（ATR2本分以上）", "材料"),
    ("big_dn", "大陰線（ATR2本分以上）", "材料"),
]
KEYS = [k for k, _, _ in CONT] + [k for k, _, _ in FLAGS]
NAME = {k: n for k, n, _ in CONT + FLAGS}
KIND = {k: g for k, n, g in CONT + FLAGS}
EVENTS = ["earn_day", "gap_up", "gap_dn", "vol2", "big_up", "big_dn"]


def ema(x, n):
    out, a, e = np.full(len(x), np.nan), 2 / (n + 1), None
    for i, v in enumerate(x):
        if np.isnan(v):
            continue
        e = v if e is None else e + a * (v - e)
        out[i] = e
    return out


def arr(x):
    return np.array([np.nan if v is None else v for v in x], float)


# ---------- 1銘柄の数値 ----------

def earn_arrays(dates, ev):
    """決算の反応日（寄り付き前の発表はその日、引け後はその次の取引日、記載なしは発表日とその次の日の窓の大きい方）"""
    n = len(dates)
    react = np.zeros(n, bool)
    surprise_at = {}
    for day, tm, sp in ev or []:
        k = bisect.bisect_left(dates, day)
        if k >= n:
            continue
        if tm == "after" or (dates[k] != day and tm != "pre"):
            k = k + 1 if dates[k] == day else k
        react[min(k, n - 1)] = True
        surprise_at[min(k, n - 1)] = sp
    return react, surprise_at


def fix_unknown(react, surprise_at, ev, dates, gapabs):
    """時間帯の記載がない発表: 発表日と次の取引日の窓の大きい方を反応日にする"""
    for day, tm, sp in ev or []:
        if tm != "?":
            continue
        k = bisect.bisect_left(dates, day)
        if k + 1 >= len(dates) or dates[k] != day:
            continue
        if gapabs[k + 1] > gapabs[k] and react[k]:
            react[k], react[k + 1] = False, True
            surprise_at[k + 1] = surprise_at.pop(k, sp)


def stock_features(s, spy_c_by_date, ev):
    """s は bt/bs/bc/bm2/udvr の prepare 済み（s["rs"] も入っている）。{キー: 配列}"""
    c, o, h, l, v = (np.array(s[k], float) for k in ("c", "o", "h", "l", "v"))
    n = len(c)
    pc = np.r_[c[0], c[:-1]]
    tr = np.maximum.reduce([h - l, np.abs(h - pc), np.abs(l - pc)])
    atr = arr(sma(list(tr), 14))
    f = {}
    with np.errstate(divide="ignore", invalid="ignore"):
        streak = np.zeros(n)
        for i in range(1, n):
            streak[i] = max(streak[i - 1], 0) + 1 if c[i] > c[i - 1] else min(streak[i - 1], 0) - 1 if c[i] < c[i - 1] else 0
        m150 = arr(s["ma150"])
        e12, e26 = ema(c, 12), ema(c, 26)
        macd = e12 - e26
        sig = ema(macd, 9)
        w1, w2 = ema(c, 60), ema(c, 130)
        wm = w1 - w2
        wsig = ema(wm, 45)
        vol50 = arr(s["vol50"])
        f.update({
            "rsi": arr(s["rsi2"]), "r1": (c - pc) / atr, "clv": np.where(h > l, (c - l) / (h - l), 0.5),
            "streak": np.clip(streak, -5, 5), "d5": (c - arr(s["ma5"])) / atr, "d50": (c - arr(s["ma50"])) / atr,
            "vr": v / vol50, "r20": np.r_[[np.nan] * 20, c[20:] / c[:-20] - 1], "atrp": atr / c,
            "rsi14": arr(rsi_wilder(list(c), 14)), "macd": macd / atr, "macd_h": (macd - sig) / atr, "wmacd_h": (wm - wsig) / atr,
            "stoch": arr(s["stk"]), "pctb": arr(s["pctb"]), "bwr": arr(s["bw"]) / arr(s["bw_min126"]), "adx": arr(s["adx14"]),
            "mfi": arr(s["mfi10"]), "ii": arr(s["ii21"]), "rs": arr(s["rs"]), "udvr": arr(s["udvr"]),
            "hi52": c / arr(s["hi252"]) - 1, "d150": c / m150 - 1, "s150": m150 / np.r_[[np.nan] * 20, m150[:-20]] - 1,
            "gap": (o - pc) / atr,
        })
    f["r1"][0] = f["gap"][0] = np.nan
    for k in ("vr", "bwr", "udvr"):
        f[k][~np.isfinite(f[k])] = np.nan
    gapabs = np.abs(np.nan_to_num(f["gap"]))
    react, sur = earn_arrays(s["date"], ev)
    fix_unknown(react, sur, ev, s["date"], gapabs)
    since, surprise, earn_react, soon = np.full(n, np.nan), np.full(n, np.nan), np.full(n, np.nan), np.zeros(n)
    last = None
    react_idx = np.flatnonzero(react)
    for i in range(n):
        if react[i]:
            last = i
        if last is not None:
            since[i] = min(i - last, 70)
            sp = sur.get(last)
            surprise[i] = np.clip(sp, -50, 50) if sp is not None else 0.0
            earn_react[i] = (c[last] - pc[last]) / atr[last] if atr[last] else np.nan
        k = np.searchsorted(react_idx, i + 1)
        soon[i] = float(k < len(react_idx) and react_idx[k] - i <= 5)
    if ev:   # 決算の記録がある銘柄だけ。記録のない銘柄は「前回から70日」「サプライズ0」とみなす
        f["since_earn"], f["surprise"], f["earn_react"] = np.nan_to_num(since, nan=70), np.nan_to_num(surprise), np.nan_to_num(earn_react)
    else:
        f["since_earn"], f["surprise"], f["earn_react"] = np.full(n, 70.0), np.zeros(n), np.zeros(n)

    # 合図（その日の引けで判定）
    flag = {k: np.zeros(n) for k, _, _ in FLAGS}
    rsl_ratio = np.array([c[i] / spy_c_by_date.get(s["date"][i], np.nan) for i in range(n)])
    hi2y = np.array([h[max(0, i - 500):i].max() if i >= 500 else np.nan for i in range(n)])
    for i in range(260, n):
        tt = bt.trend_template(s, i)
        flag["tt"][i] = tt
        pb, ii = s["pctb"][i], s["ii21"][i]
        if pb is not None and ii is not None and ii > 0:
            flag["boll3"][i] = pb < 0.05
            flag["boll3b"][i] = 0.05 <= pb < 0.2
        kh = s["piv_i"][i]
        if tt and kh is not None and i - kh >= 15 and s["vol50"][i]:
            piv = s["h"][kh]
            flag["mnv"][i] = c[i] > piv and (piv - l[kh:i].min()) / piv <= 0.35 and v[i] >= 2 * s["vol50"][i]
        flag["wein"][i] = bt.E_weinstein(10, ma="10")(i, s) is not None
        flag["crash"][i] = C3R10(i, s) is not None
        hc, u = s["hi20c"][i], s["udvr"][i]
        flag["v2"][i] = (tt and hc is not None and c[i] > hc and u is not None and u >= 1.3 and (s["rs"][i] or 0) >= 90
                         and np.isfinite(hi2y[i]) and c[i] >= hi2y[i])
        up = s["ma50"][i] is not None and s["ma200"][i] is not None and c[i] > s["ma50"][i] > s["ma200"][i]
        if up and (s["rs"][i] or 0) >= 80:
            m10 = np.mean(c[i - 9:i + 1])
            downs = [v[k] for k in range(i - 10, i) if c[k] < c[k - 1]]
            flag["pp"][i] = c[i] > c[i - 1] and c[i] <= m10 * 1.05 and bool(downs) and v[i] > max(downs)
            a40 = tr[i - 39:i + 1].mean()
            flag["bgu"][i] = o[i] - c[i - 1] >= 0.75 * a40 and s["vol50"][i] and v[i] >= 1.5 * s["vol50"][i]
        flag["grail"][i] = bs.O_holy_grail(i, s) is not None
        flag["anti"][i] = bs.O_anti(i, s) is not None
        flag["nr7"][i] = bs.O_nr7(i, s) is not None
        flag["nr4"][i] = bs.O_nr4_id(i, s) is not None
        flag["gapfail"][i] = bs.O_gap_failure(i, s) is not None
        flag["m1"][i] = bs.O_squeeze(i, s) is not None
        flag["m2"][i] = bs.O_method2(i, s) is not None
        flag["donch"][i] = s["hi20"][i] is not None and c[i] > s["hi20"][i]
        m200, r2 = s["ma200"][i], s["rsi2"][i]
        flag["k1"][i] = m200 is not None and r2 is not None and c[i] > m200 and r2 <= 5
        if np.isfinite(atr[i - 1]) and h[i] > l[i] and s["vol50"][i]:
            flag["bear"][i] = o[i] - c[i] >= 1.5 * atr[i - 1] and (c[i] - l[i]) / (h[i] - l[i]) <= 0.25 and v[i] >= 2 * s["vol50"][i]
        w = rsl_ratio[i - 251:i + 1]
        flag["rsl"][i] = np.isfinite(rsl_ratio[i]) and rsl_ratio[i] >= np.nanmax(w)
        g = o[i] / c[i - 1] - 1
        flag["gap_up"][i], flag["gap_dn"][i] = g >= 0.03, g <= -0.03
        flag["vol2"][i] = bool(s["vol50"][i]) and v[i] >= 2 * s["vol50"][i]
        flag["big_up"][i] = f["r1"][i] >= 2
        flag["big_dn"][i] = f["r1"][i] <= -2
    flag["earn_day"] = react.astype(float)
    flag["earn_soon"] = soon
    f.update(flag)
    return f


def prep(s):
    bt.prepare(s)
    bs.prepare(s)
    bc.prepare(s)
    bm2.add_pivot(s)
    add_udvr(s)


# ---------- データ集め（並列） ----------

_G = {}


def _init(cache, members, rs_rank, spy_c, mk, earnings):
    _G.update(cache=cache, members=members, rs=rs_rank, spy_c=spy_c, mk=mk, earn=earnings)


def rs_raw_of(args):
    cache, sym = args
    d = load_prices(cache, sym)
    if not d or len(d["c"]) < 260:
        return sym, None
    c = d["c"]
    return sym, {d["date"][i]: 0.4 * (c[i] / c[i - 63] - 1) + 0.2 * (c[i] / c[i - 126] - 1) + 0.2 * (c[i] / c[i - 189] - 1)
                 + 0.2 * (c[i] / c[i - 252] - 1) for i in range(252, len(c))}


def rows_of(sym):
    s = load_prices(_G["cache"], sym)
    if not s or len(s["c"]) < 300:
        return None
    prep(s)
    rk = _G["rs"]
    s["rs"] = [rk.get((sym, d)) for d in s["date"]]
    f = stock_features(s, _G["spy_c"], _G["earn"].get(sym))
    c, o = np.array(s["c"]), np.array(s["o"])
    spy_c = _G["spy_c"]
    mk, spans = _G["mk"], _G["members"].get(sym)
    days, X, Y = [], [], []
    n = len(c)
    for i in range(260, n - 1):
        day = s["date"][i]
        if day < "2015-01-01" or day not in mk or (spans is not None and not is_member(spans, day)):
            continue
        m = mk[day]
        x = [f[k][i] if k in f else None for k in KEYS]
        x[KEYS.index("spy_rsi")], x[KEYS.index("spy_r1")], x[KEYS.index("vix")], x[KEYS.index("spy_ma")] = m[0], m[1], m[2], m[4]
        if any(v is None or not np.isfinite(v) for v in x):
            continue
        y = []
        for hz in HORIZONS:
            j = i + hz
            if j >= n or s["date"][j] not in spy_c:
                y += [np.nan] * 3
                continue
            spy_r = spy_c[s["date"][j]] / spy_c[day] - 1
            y += [c[j] / c[i] - 1, c[j] / o[i + 1] - 1, c[j] / c[i] - 1 - spy_r]
        days.append(day)
        X.append(x)
        Y.append(y)
    if not days:
        return None
    return sym, np.array(days), np.array(X, np.float32), np.array(Y, np.float32)


def build(cache, syms, members, watch=False):
    spy = load_prices(cache, "SPY")
    vix = load_prices(cache, "^VIX")
    mk = market_feats(spy, vix)
    m150 = sma(spy["c"], 150)
    for i, d in enumerate(spy["date"]):
        if d in mk:
            mk[d] = mk[d] + ((spy["c"][i] / m150[i] - 1) if m150[i] else np.nan,)
    mk = {d: v for d, v in mk.items() if len(v) == 5 and np.isfinite(v[4])}
    spy_c = dict(zip(spy["date"], spy["c"]))
    # RS順位（その日の構成銘柄の中での百分位。監視銘柄は構成銘柄の中に入れて数える）
    base = sorted(set(members) | set(syms))
    with Pool(4) as p:
        raws = dict(p.map(rs_raw_of, [(cache, s) for s in base]))
    by_day = {}
    for sym, r in raws.items():
        if not r:
            continue
        for d, x in r.items():
            if sym not in members or is_member(members[sym], d):
                by_day.setdefault(d, []).append(x)
    for v in by_day.values():
        v.sort()
    rank = {}
    for sym in syms:
        for d, x in (raws.get(sym) or {}).items():
            b = by_day.get(d)
            if b and len(b) > 50:
                rank[(sym, d)] = 99 * bisect.bisect_left(b, x) / (len(b) - 1)
    earn = load_earnings(cache)
    mem = {} if watch else members
    with Pool(4, initializer=_init, initargs=(cache, mem, rank, spy_c, mk, earn)) as p:
        res = [r for r in p.imap_unordered(rows_of, syms, chunksize=4) if r]
    syms_out = np.concatenate([np.full(len(r[1]), r[0]) for r in res])
    return (syms_out, np.concatenate([r[1] for r in res]), np.concatenate([r[2] for r in res]),
            np.concatenate([r[3] for r in res]))


# ---------- 点数 ----------

def edges_for(X, tr):
    out = []
    for j, k in enumerate(KEYS):
        if k in NAME and any(k == f for f, _, _ in FLAGS):
            out.append(np.array([0.5]))
        else:
            out.append(np.unique(np.percentile(X[tr, j], [20, 40, 60, 80])))
    return out


def one_feature(X, y, r, days, edges):
    """数値ごとの効き目: 連続の数値は上位20%と下位20%、合図は出た日と出ていない日の、上がった割合の差（設計の前半・後半・確認）"""
    per = {"前半": days <= HALF, "後半": (days > HALF) & (days <= DESIGN_END), "確認": days >= VERIFY_START}
    out = {}
    for j, k in enumerate(KEYS):
        x = X[:, j]
        if len(edges[j]) == 1:
            hi, lo = x > 0.5, x <= 0.5
        else:
            hi, lo = x >= edges[j][-1], x < edges[j][0]
        row = {}
        for pn, m in per.items():
            a, b = m & hi, m & lo
            row[pn] = (float(y[a].mean() - y[b].mean()) if a.any() and b.any() else np.nan,
                       float(r[a].mean() - r[b].mean()) if a.any() and b.any() else np.nan, int(a.sum()))
        out[k] = row
    return out


def pc(x, d=1):
    return "—" if not np.isfinite(x) else f"{x * 100:.{d}f}%"


def pt(x):
    return "—" if not np.isfinite(x) else f"{x * 100:+.1f}"


def cmd_backtest(a):
    members = load_members(a.cache)
    syms = sorted(s for s in members if os.path.exists(os.path.join(a.cache, "prices", s + ".json")))[:a.limit]
    t0 = dt.datetime.now()
    syms_a, days, X, Y = build(a.cache, syms, members)
    print("S&P500", len(days), dt.datetime.now() - t0, file=sys.stderr)
    from backtest_theme import load_watchlist
    wl = list(load_watchlist())
    _, wdays, wX, wY = build(a.cache, wl, members, watch=True)
    wsel = wdays >= VERIFY_START
    wdays, wX, wY = wdays[wsel], wX[wsel], wY[wsel]
    tr, te = days <= DESIGN_END, days >= VERIFY_START
    edges = edges_for(X, tr)
    A = to_design(X, edges).astype(np.float32)
    wA = to_design(wX, edges).astype(np.float32)
    col_of, pos = [], 1
    for j, e in enumerate(edges):
        col_of.append(list(range(pos, pos + len(e))))
        pos += len(e)
    labels = []
    for hz in HORIZONS:
        labels += [(f"cc{hz}", f"{hz}日・引け→引け"), (f"oc{hz}", f"{hz}日・翌寄り→引け"), (f"rel{hz}", f"{hz}日・対市場")]
    model = {"made": dt.date.today().isoformat(), "keys": KEYS, "edges": [e.tolist() for e in edges], "labels": {},
             "verify_to": max(days[te].tolist())}
    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: 今後3〜5日の上げ下げの確率（銘柄ごと）\n" f"updated: {dt.date.today().isoformat()}\n---\n")
    w("# 今後3〜5日の上げ下げの確率（銘柄ごと）— オシレーター・本のルール・材料を加えて\n")
    w(f"作成: `tools/swing_odds.py backtest`。S&P500（その日の構成銘柄）{len(set(syms_a.tolist()))}銘柄の {len(days):,} 日分。"
      f"点数の作り方は **2015〜2021年（{tr.sum():,}）だけで決め**、**2022年〜{model['verify_to']}（{te.sum():,}）で確かめた**。"
      f"監視銘柄（今の{len(wl)}銘柄、2022年以降 {len(wdays):,}）は後知恵ありの参考。"
      "決算はNasdaqのEarnings Calendar（発表日・時間帯・EPSのサプライズ%）。\n")
    w("日をまたいで期間が重なるため（5日なら隣の日と4日分が同じ）、件数ほどの独立した試行ではない。\n")
    w("使った数値: " + "、".join(f"**{g}**: " + "・".join(n for k, n, gg in CONT + FLAGS if gg == g)
                               for g in ("値動き", "市場", "オシレーター", "決算", "採用ルール", "未採用の本", "材料")) + "\n")
    summary = []
    for li, (lab, name) in enumerate(labels):
        hz = int(lab[-1])
        col = HORIZONS.index(hz) * 3 + ("cc", "oc", "rel").index(lab[:-1])
        r = Y[:, col].astype(float)
        ok = np.isfinite(r)
        y = (r > 0).astype(float)
        if lab.startswith("oc"):
            y = (r > 2 * COST).astype(float)     # 手数料（往復0.2%）を引いてプラス
        wr = wY[:, col].astype(float)
        wok = np.isfinite(wr)
        wy = (wr > (2 * COST if lab.startswith("oc") else 0)).astype(float)
        eff = one_feature(X[ok], y[ok], r[ok], days[ok], edges)
        stable = [k for k in KEYS if all(np.isfinite(eff[k][p][0]) for p in ("前半", "後半"))
                  and np.sign(eff[k]["前半"][0]) == np.sign(eff[k]["後半"][0]) and min(abs(eff[k]["前半"][0]), abs(eff[k]["後半"][0])) >= 0.01]
        res_l = {}
        for mname, use in (("全部", KEYS), ("安定", stable)):
            cols = [0] + [cc for j, k in enumerate(KEYS) if k in use for cc in col_of[j]]
            fitm = tr & ok
            wgt = fit(A[fitm][:, cols].astype(float), y[fitm])
            s = A[:, cols].astype(float) @ wgt
            ws = wA[:, cols].astype(float) @ wgt
            cuts = np.percentile(s[fitm], np.arange(10, 100, 10))
            dec, wdec = np.digitize(s, cuts), np.digitize(ws, cuts)
            tm = te & ok
            calib = [{"n": int((tm & (dec == k)).sum()), "up": float(y[tm & (dec == k)].mean()), "mean": float(r[tm & (dec == k)].mean())}
                     for k in range(10)]
            res_l[mname] = {"cols": cols, "w": wgt.tolist(), "cuts": cuts.tolist(), "calib": calib, "base": float(y[tm].mean()),
                            "auc_design": float(auc(s[fitm], y[fitm])), "auc_verify": float(auc(s[tm], y[tm])),
                            "use": use, "dec": dec, "wdec": wdec, "s": s}
        model["labels"][lab] = {k: {kk: vv for kk, vv in v.items() if kk not in ("dec", "wdec", "s")} for k, v in res_l.items()}
        w(f"\n## {name}\n")
        up_word = "手数料（往復0.2%）を引いてプラスになった割合" if lab.startswith("oc") else "上がった割合"
        w(f"- {up_word}（全体）: 設計期間 {pc(y[tr & ok].mean())}、確認期間 {pc(y[te & ok].mean())}")
        for mname in ("全部", "安定"):
            m = res_l[mname]
            w(f"- 点数「{mname}」（{len(m['use'])}個の数値）の当てる力（AUC）: 設計 {m['auc_design']:.3f}、確認 **{m['auc_verify']:.3f}**")
        w(f"- 「安定」に残った数値: {'・'.join(NAME[k] for k in stable) or 'なし'}\n")
        w("確認期間（2022年〜）の10段階ごとの実績（段階の境目は設計期間で決めた）:\n")
        w(f"| 段階 | 全部: {up_word} | 全部: 平均 | 全部: 件数 | 安定: {up_word} | 安定: 平均 | 監視銘柄（全部）: {up_word} | 監視銘柄: 平均 | 監視銘柄: 件数 |")
        w("|---|---|---|---|---|---|---|---|---|")
        for k in range(10):
            ca, cs = res_l["全部"]["calib"][k], res_l["安定"]["calib"][k]
            wm = wok & (res_l["全部"]["wdec"] == k)
            w(f"| {k + 1} | {pc(ca['up'])} | {ca['mean'] * 100:+.2f}% | {ca['n']:,} | {pc(cs['up'])} | {cs['mean'] * 100:+.2f}% | "
              f"{pc(wy[wm].mean()) if wm.any() else '—'} | {wr[wm].mean() * 100:+.2f}% | {int(wm.sum()):,} |" if wm.any() else
              f"| {k + 1} | {pc(ca['up'])} | {ca['mean'] * 100:+.2f}% | {ca['n']:,} | {pc(cs['up'])} | {cs['mean'] * 100:+.2f}% | — | — | 0 |")
        # 年ごと
        dec = res_l["全部"]["dec"]
        parts = []
        for yr in sorted({d[:4] for d in days[te].tolist()}):
            m = te & ok & (np.char.startswith(days.astype(str), yr))
            hi, lo = m & (dec == 9), m & (dec == 0)
            parts.append(f"{yr}: {pt(y[hi].mean() - y[lo].mean())}pt / {(r[hi].mean() - r[lo].mean()) * 100:+.2f}%")
        w("\n年ごと（全部の段階10と段階1の差。割合 / 平均）: " + "、".join(parts))
        # 材料のある日
        w("\n材料のある日だけで見た確認期間の実績（その日の点数「全部」の上位30%と下位30%）:\n")
        w(f"| 材料 | 件数 | {up_word} | 平均 | AUC | 上位30%: 割合 / 平均 | 下位30%: 割合 / 平均 |")
        w("|---|---|---|---|---|---|---|")
        sc = res_l["全部"]["s"]
        for ev in EVENTS:
            m = te & ok & (X[:, KEYS.index(ev)] > 0.5)
            if m.sum() < 100:
                continue
            q3, q7 = np.percentile(sc[m], [30, 70])
            hi, lo = m & (sc >= q7), m & (sc <= q3)
            w(f"| {NAME[ev]} | {int(m.sum()):,} | {pc(y[m].mean())} | {r[m].mean() * 100:+.2f}% | {auc(sc[m], y[m]):.3f} | "
              f"{pc(y[hi].mean())} / {r[hi].mean() * 100:+.2f}% | {pc(y[lo].mean())} / {r[lo].mean() * 100:+.2f}% |")
        summary.append((name, res_l["全部"]["auc_verify"], res_l["安定"]["auc_verify"], res_l["全部"]["calib"][9], res_l["全部"]["calib"][0],
                        res_l["全部"]["base"]))
        if lab == "oc5":
            w("\n### 数値1つずつの効き目（5日・翌寄り→引け。上位20%−下位20%、合図は出た日−出ていない日。割合の差pt / 平均の差%）\n")
            w("| 区分 | 数値 | 設計の前半（2015〜2018） | 設計の後半（2019〜2021） | 確認（2022〜） | 確認の件数（上位/出た日） |")
            w("|---|---|---|---|---|---|")
            for k in KEYS:
                e = eff[k]
                w(f"| {KIND[k]} | {NAME[k]} | " + " | ".join(f"{pt(e[p][0])} / {e[p][1] * 100:+.2f}%" if np.isfinite(e[p][1]) else "—"
                                                           for p in ("前半", "後半", "確認")) + f" | {e['確認'][2]:,} |")
    # 決算の後の値動き（決算の反応日の翌日から5日。サプライズと反応の向き）
    w("\n## 決算の後の5日（決算の反応日の引け → 翌日の寄りで買い5日目の引け。手数料前）\n")
    ed = X[:, KEYS.index("earn_day")] > 0.5
    col = HORIZONS.index(5) * 3 + 1
    r5 = Y[:, col].astype(float)
    sur, rct = X[:, KEYS.index("surprise")], X[:, KEYS.index("r1")]
    w("| 決算の結果と反応 | 設計: 件数 / プラスの割合 / 平均 | 確認: 件数 / プラスの割合 / 平均 |")
    w("|---|---|---|")
    for nm, m in (("サプライズ+10%以上・反応が上（ATR1本以上）", (sur >= 10) & (rct >= 1)),
                  ("サプライズ+でも反応が下（ATR−1本以下）", (sur > 0) & (rct <= -1)),
                  ("サプライズ−・反応が下（ATR−1本以下）", (sur < 0) & (rct <= -1)),
                  ("サプライズ−でも反応が上（ATR1本以上）", (sur < 0) & (rct >= 1)),
                  ("決算の反応日すべて", np.ones(len(sur), bool))):
        cells = []
        for per in (tr, te):
            mm = ed & m & per & np.isfinite(r5)
            cells.append(f"{int(mm.sum()):,} / {pc((r5[mm] > 0).mean())} / {r5[mm].mean() * 100:+.2f}%" if mm.any() else "—")
        w(f"| {nm} | " + " | ".join(cells) + " |")
    w("\n## まとめ（数値）\n")
    w("| 決め方 | AUC 全部 | AUC 安定 | 段階10の割合 / 平均 | 段階1の割合 / 平均 | 全体の割合 |")
    w("|---|---|---|---|---|---|")
    for nm, a1, a2, c10, c1, base in summary:
        w(f"| {nm} | {a1:.3f} | {a2:.3f} | {pc(c10['up'])} / {c10['mean'] * 100:+.2f}% | {pc(c1['up'])} / {c1['mean'] * 100:+.2f}% | {pc(base)} |")
    json.dump(model, open(MODEL, "w"), ensure_ascii=False)
    out = a.out or REPORT
    open(out, "w").write("\n".join(L) + "\n")
    print(out)


# ---------- 今日の確率 ----------

def live_rows(syms, asof=None):
    """監視銘柄の今日の引けの数値。RS順位の母集団は S&P500の今の構成銘柄と監視銘柄（theme_single.load_pool と同じ）"""
    import csv
    from concurrent.futures import ThreadPoolExecutor
    from backtest_lib import MEMBERS_URL, curl
    from daily_odds import open_day
    from earnings_history import refresh
    from theme_scan import cut, fetch_daily
    txt = curl(MEMBERS_URL)
    sp = [r["ticker"] for r in csv.DictReader(txt.splitlines()) if not r["end_date"]] if txt.startswith("ticker,") else []
    allsyms = sorted(set(sp) | set(syms) | {"SPY", "^VIX"})
    with ThreadPoolExecutor(8) as ex:
        got = dict(zip(allsyms, ex.map(fetch_daily, allsyms)))
    asof = asof or open_day()
    got = {k: cut(v, asof) for k, v in got.items() if v}
    spy, vix = got["SPY"], got["^VIX"]
    day = spy["date"][-1]
    mk = market_feats(spy, vix)
    m150 = sma(spy["c"], 150)
    mkt = mk[day] + (spy["c"][-1] / m150[-1] - 1,)
    spy_c = dict(zip(spy["date"], spy["c"]))
    raw = {}
    for k, d in got.items():
        c = d["c"]
        if len(c) > 253 and d["date"][-1] == day:
            raw[k] = 0.4 * (c[-1] / c[-64] - 1) + 0.2 * (c[-1] / c[-127] - 1) + 0.2 * (c[-1] / c[-190] - 1) + 0.2 * (c[-1] / c[-253] - 1)
    pool = sorted(raw.values())
    earn = refresh()
    out, skipped = [], []
    for sym in syms:
        s = got.get(sym)
        if not s or len(s["c"]) < 300 or s["date"][-1] != day:
            skipped.append(sym)
            continue
        prep(s)
        # RS順位は過去の日も要る（トレンドテンプレート・V2）。過去の日は今日の母集団の分布で近似する
        c = s["c"]
        s["rs"] = [None] * len(c)
        for i in range(252, len(c)):
            r = 0.4 * (c[i] / c[i - 63] - 1) + 0.2 * (c[i] / c[i - 126] - 1) + 0.2 * (c[i] / c[i - 189] - 1) + 0.2 * (c[i] / c[i - 252] - 1)
            s["rs"][i] = 99 * bisect.bisect_left(pool, r) / (len(pool) - 1)
        f = stock_features(s, spy_c, earn.get(sym))
        x = [f[k][-1] if k in f else None for k in KEYS]
        x[KEYS.index("spy_rsi")], x[KEYS.index("spy_r1")], x[KEYS.index("vix")], x[KEYS.index("spy_ma")] = mkt[0], mkt[1], mkt[2], mkt[4]
        if any(v is None or not np.isfinite(v) for v in x):
            skipped.append(sym)
            continue
        out.append((sym, s["c"][-1], x))
    return day, mkt, out, skipped


def model_score(model, lm, x):
    A = to_design(np.array([x], float), [np.array(e) for e in model["edges"]])[0]
    return float(A[lm["cols"]] @ np.array(lm["w"]))


def cmd_today(a):
    from backtest_theme import load_watchlist
    model = json.load(open(MODEL))
    wl = load_watchlist()
    syms = a.tickers.upper().split(",") if a.tickers else list(wl)
    day, mkt, rows, skipped = live_rows(syms, a.asof)
    show = [("oc5", "5日・翌寄り→引け"), ("oc3", "3日・翌寄り→引け"), ("rel5", "5日・対市場"), ("cc5", "5日・引け→引け")]
    pick = {lab: max(model["labels"][lab], key=lambda m: model["labels"][lab][m]["auc_verify"]) for lab, _ in show}
    res = []
    for sym, close, x in rows:
        r = {"sym": sym, "group": wl.get(sym, "—"), "close": close, "x": x}
        for lab, _ in show:
            lm = model["labels"][lab][pick[lab]]
            b = int(np.digitize([model_score(model, lm, x)], lm["cuts"])[0])
            r[lab] = (b, lm["calib"][b]["up"], lm["calib"][b]["mean"])
        r["sig"] = [NAME[k] for k, _, g in FLAGS if x[KEYS.index(k)] > 0.5 and g in ("採用ルール", "未採用の本", "材料")]
        res.append(r)
    res.sort(key=lambda r: (-r["oc5"][0], -r["oc5"][2]))
    L = []
    w = L.append
    w(f"# 今後3〜5日の上げ下げの確率（{day} の引け → 次の取引日から）\n")
    w(f"作成: `tools/swing_odds.py today`（{dt.datetime.now().strftime('%Y-%m-%d %H:%M')}）。数値と過去の統計だけで、売買の判断ではない。\n")
    w("## 読み方（先に読む）\n")
    for lab, name in show:
        lm = model["labels"][lab][pick[lab]]
        w(f"- {name}（点数「{pick[lab]}」）: 確認期間のAUC {lm['auc_verify']:.3f}、全体の割合 {pc(lm['base'])}、"
          f"段階10 {pc(lm['calib'][9]['up'])}（平均 {lm['calib'][9]['mean'] * 100:+.2f}%）、段階1 {pc(lm['calib'][0]['up'])}（平均 {lm['calib'][0]['mean'] * 100:+.2f}%）")
    w("- 確率は「2022年以降に、同じくらいの点数（10段階）だった日の実績」。翌寄り→引けは手数料（往復0.2%）を引いてプラスになった割合。")
    w("- 詳しい検証は `新分析ツール/バックテスト結果/今後3〜5日の上げ下げの確率.md`。\n")
    w(f"## 市場全体（{day}）\n")
    w(f"- S&P500のRSI(2) {mkt[0]:.0f}、今日の騰落率 {mkt[1]:+.1%}、VIX {mkt[2]:.1f}、30週線からの離れ {mkt[4]:+.1%}\n")
    w("## 銘柄ごと（5日・翌寄り→引けの段階の高い順）\n")
    w("段階は1（下がりやすい）〜10（上がりやすい）。\n")
    w("| 銘柄 | グループ | 終値 | " + " | ".join(f"{n}: 段階 / 確率 / 平均" for _, n in show) + " | 今日出た合図・材料 |")
    w("|---|---|---|" + "---|" * len(show) + "---|")
    for r in res:
        w(f"| {r['sym']} | {r['group']} | {r['close']:.2f} | " + " | ".join(f"{r[l][0] + 1} / {pc(r[l][1])} / {r[l][2] * 100:+.2f}%" for l, _ in show)
          + f" | {'・'.join(r['sig']) or '—'} |")
    if skipped:
        w(f"\n{day} の日足を取得できなかった（または上場から約1年2カ月未満の）銘柄: {', '.join(skipped)}")
    open(a.out, "w").write("\n".join(L) + "\n")
    print(a.out)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("backtest")
    b.add_argument("--cache", default=DEFAULT_CACHE)
    b.add_argument("--out")
    b.add_argument("--limit", type=int)
    t = sub.add_parser("today")
    t.add_argument("out")
    t.add_argument("--asof")
    t.add_argument("--tickers")
    a = ap.parse_args()
    cmd_backtest(a) if a.cmd == "backtest" else cmd_today(a)


if __name__ == "__main__":
    main()
