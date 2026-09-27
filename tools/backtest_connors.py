#!/usr/bin/env python3
"""コナーズ『短期売買入門』の数値ルールのバックテスト（`新分析ツール/引き継ぎ.md` 5-1）

使い方:
  tools/backtest_connors.py fetch [--cache DIR]
      S&P500の過去の構成銘柄（fja05680/sp500 の日付つき構成銘柄表）と、2015年以降に一度でも構成銘柄だった
      全銘柄＋SPY・^VIXの日足（2013年〜）をYahooから取得してキャッシュする。取得できなかった銘柄は一覧に残す。
  tools/backtest_connors.py run [--cache DIR] [--out FILE] [--start YYYY-MM-DD] [--end YYYY-MM-DD]
      ルール表（`書籍ルール/コナーズ_ルール表.md`）の条件でシグナルを出し、成績をMarkdownで書き出す。

前提（結果の読み方に関わるので出力にも明記する）:
  - シグナルはその日の構成銘柄だけで出す（今の構成銘柄だけで検証したときの生存者バイアスを避けるため）。
    ただしYahooから消えた上場廃止銘柄は取得できないので、その分のバイアスは残る（取得率を出力する）。
  - 価格は株式分割調整済み・配当調整なし。仕掛け・手じまいとも当日の引け値（ルール表の注文方法「大引け」）。
  - 売買コストは片道の率で複数通り（0%・0.05%・0.1%）を出す。
  - 統計は1シグナル＝1トレード（資金の制約なし）と、同時保有数に上限を置いたポートフォリオの2通り。
"""
import argparse
import bisect
import csv
import datetime as dt
import json
import math
import os
import random
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
MEMBERS_URL = "https://raw.githubusercontent.com/fja05680/sp500/master/sp500_ticker_start_end.csv"
DEFAULT_CACHE = os.path.expanduser("~/.cache/backtest_connors")
FETCH_FROM = dt.datetime(2013, 1, 1)
MEMBER_SINCE = "2015-01-01"
COSTS = (0.0, 0.0005, 0.001)   # 片道
MAX_HOLD = 30                  # 手じまい条件が出ないときの打ち切り（取引日）


# ---------- 取得 ----------

def curl(url):
    r = subprocess.run(["curl", "-sS", "--max-time", "30", "-A", UA, url], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def fetch_one(symbol, path):
    if os.path.exists(path):
        return True
    p1, p2 = int(FETCH_FROM.timestamp()), int(time.time())
    for attempt in range(3):
        txt = curl(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&period1={p1}&period2={p2}")
        try:
            res = json.loads(txt)["chart"]["result"][0]
            q = res["indicators"]["quote"][0]
            off = res["meta"].get("gmtoffset", 0)
            rows = []
            for i, t in enumerate(res["timestamp"]):
                o, h, l, c, v = q["open"][i], q["high"][i], q["low"][i], q["close"][i], q["volume"][i]
                if None in (o, h, l, c):
                    continue
                rows.append([dt.datetime.utcfromtimestamp(t + off).strftime("%Y-%m-%d"), o, h, l, c, v or 0])
            if not rows:
                return False
            with open(path, "w") as f:
                json.dump(rows, f)
            return True
        except Exception:
            if '"Not Found"' in txt or "No data found" in txt:
                return False
            time.sleep(2 ** attempt)
    return False


def cmd_fetch(a):
    os.makedirs(os.path.join(a.cache, "prices"), exist_ok=True)
    mpath = os.path.join(a.cache, "members.csv")
    txt = curl(MEMBERS_URL)
    if not txt.startswith("ticker,"):
        sys.exit("構成銘柄表を取得できませんでした")
    open(mpath, "w").write(txt)
    members = load_members(a.cache)
    syms = sorted(members) + ["SPY", "^VIX"]
    ysym = lambda s: s.replace(".", "-")
    with ThreadPoolExecutor(8) as ex:
        ok = list(ex.map(lambda s: fetch_one(ysym(s), os.path.join(a.cache, "prices", s + ".json")), syms))
    missing = [s for s, k in zip(syms, ok) if not k]
    open(os.path.join(a.cache, "missing.txt"), "w").write("\n".join(missing))
    print(f"対象 {len(syms)} 銘柄、取得 {len(syms) - len(missing)}、取得不可 {len(missing)}")


def load_members(cache):
    """{ticker: [(start, end), ...]}（2015年以降に構成銘柄だったもののみ。endが空なら現在も構成銘柄）"""
    m = {}
    for r in csv.DictReader(open(os.path.join(cache, "members.csv"))):
        end = r["end_date"] or "9999-12-31"
        if end >= MEMBER_SINCE:
            m.setdefault(r["ticker"], []).append((r["start_date"], end))
    return m


def load_prices(cache, sym):
    p = os.path.join(cache, "prices", sym + ".json")
    if not os.path.exists(p):
        return None
    rows = json.load(open(p))
    d = {"date": [], "o": [], "h": [], "l": [], "c": [], "v": []}
    for r in rows:
        for k, x in zip(d, r):
            d[k].append(x)
    return d


# ---------- 指標 ----------

def sma(x, n):
    out, s = [None] * len(x), 0.0
    for i, v in enumerate(x):
        s += v
        if i >= n:
            s -= x[i - n]
        if i >= n - 1:
            out[i] = s / n
    return out


def rsi_wilder(c, n=2):
    """コナーズの2期間RSI（ワイルダーの平滑化。市販ツールと同じ計算）"""
    out = [None] * len(c)
    if len(c) <= n:
        return out
    g = [max(c[i] - c[i - 1], 0) for i in range(1, len(c))]
    l = [max(c[i - 1] - c[i], 0) for i in range(1, len(c))]
    ag, al = sum(g[:n]) / n, sum(l[:n]) / n
    for i in range(n, len(c)):
        if i > n:
            ag = (ag * (n - 1) + g[i - 1]) / n
            al = (al * (n - 1) + l[i - 1]) / n
        out[i] = 100.0 if al == 0 else 100 - 100 / (1 + ag / al)
    return out


def rolling(x, n, fn):
    return [fn(x[i - n + 1:i + 1]) if i >= n - 1 else None for i in range(len(x))]


# ---------- 局面（市場全体） ----------

def market_regime(spy):
    """SPYの30週線（≒150日線）の位置と傾きで、ワインスタインのステージを近似した3区分を日付ごとに返す。
    上昇: 終値>30週線 かつ 30週線が4週前より上 / 下落: 終値<30週線 かつ 30週線が4週前より下 / それ以外: 横ばい"""
    c = spy["c"]
    m = sma(c, 150)
    reg = {}
    for i, d in enumerate(spy["date"]):
        if m[i] is None or i < 20 or m[i - 20] is None:
            continue
        up, rising = c[i] > m[i], m[i] > m[i - 20]
        reg[d] = "上昇" if up and rising else "下落" if (not up and not rising) else "横ばい"
    return reg


# ---------- 戦略 ----------
# entry(i, s) -> シグナルなら並べ替え用の値（小さいほど優先）、なければNone
# exit(i, s, k) -> k日目（仕掛けからの経過取引日）に手じまうか

def E_rsi2(th):
    return lambda i, s: s["rsi2"][i] if s["rsi2"][i] is not None and s["rsi2"][i] <= th else None


def E_cum2(th):
    def f(i, s):
        r, q = s["rsi2"][i], s["rsi2"][i - 1]
        return r + q if r is not None and q is not None and r + q <= th else None
    return f


def E_double7(i, s):
    return s["rsi2"][i] if s["low7c"][i] is not None and s["c"][i] <= s["low7c"][i] else None


X = {
    "5日線上抜け": lambda i, s, k: s["c"][i] > s["ma5"][i],
    "10日線上抜け": lambda i, s, k: s["c"][i] > s["ma10"][i],
    "RSI(2)≧70": lambda i, s, k: s["rsi2"][i] >= 70,
    "7日最高値で引け": lambda i, s, k: s["high7c"][i] is not None and s["c"][i] >= s["high7c"][i],
    "5取引日後": lambda i, s, k: k >= 5,
}

STRATEGIES = [
    # 名前, エントリー, 手じまい, 出典
    ("RSI(2)≦5・5日線上抜けで手じまい（基本戦略）", E_rsi2(5), "5日線上抜け", "p.22, p.45"),
    ("RSI(2)≦5・RSI(2)≧70で手じまい", E_rsi2(5), "RSI(2)≧70", "p.22, p.23"),
    ("RSI(2)≦5・10日線上抜けで手じまい", E_rsi2(5), "10日線上抜け", "p.22, p.36"),
    ("RSI(2)≦5・5取引日後に手じまい", E_rsi2(5), "5取引日後", "p.22, p.36"),
    ("RSI(2)≦10・5日線上抜けで手じまい（閾値を緩めた参考）", E_rsi2(10), "5日線上抜け", "ルール表外（頻度の比較用）"),
    ("個別株2日累積RSI≦10・5日線上抜けで手じまい", E_cum2(10), "5日線上抜け", "p.24"),
    ("ダブル7（7日最安値で引け）・7日最高値で引けて手じまい", E_double7, "7日最高値で引け", "p.26"),
]

STOPS = [
    ("ストップなし（コナーズの原則）", None, None),
    ("引け値で−10%以下なら当日引けで損切り", 0.10, None),
    ("引け値で−15%以下なら当日引けで損切り", 0.15, None),
    ("10取引日たっても手じまい条件が出なければ手じまい", None, 10),
]


def prepare(d):
    c = d["c"]
    d["ma200"], d["ma5"], d["ma10"] = sma(c, 200), sma(c, 5), sma(c, 10)
    d["rsi2"] = rsi_wilder(c, 2)
    d["vol100"] = sma(d["v"], 100)
    # 直近7日（当日を含まない）の終値ベースの最安値・最高値。「7日最安値で引ける」は当日終値がそれ以下
    prev7 = lambda f: [f(c[i - 7:i]) if i >= 7 else None for i in range(len(c))]
    d["low7c"], d["high7c"] = prev7(min), prev7(max)
    return d


def is_member(spans, day):
    return any(s <= day <= e for s, e in spans)


def signal_ok(s, i, spans):
    """ルール表の銘柄選定・トレンドフィルター（p.16-17, p.22: 株価≧5ドル、100日平均出来高≧25万株、終値>200日線）"""
    return (s["ma200"][i] is not None and s["vol100"][i] is not None and s["c"][i] >= 5
            and s["vol100"][i] >= 250_000 and s["c"][i] > s["ma200"][i] and is_member(spans, s["date"][i]))


def gen_trades(data, members, entry, exit_name, stop, start, end):
    ex = X[exit_name]
    stop_pct, time_stop = stop[1], stop[2]
    trades = []
    for sym, s in data.items():
        n, i = len(s["c"]), 200
        while i < n - 1:
            d = s["date"][i]
            if d < start or d > end or not signal_ok(s, i, members[sym]):
                i += 1
                continue
            rank = entry(i, s)
            if rank is None:
                i += 1
                continue
            px, j, reason = s["c"][i], i, "打ち切り"
            for k in range(1, MAX_HOLD + 1):
                j = i + k
                if j >= n:
                    j, reason = n - 1, "データ終端"
                    break
                if stop_pct is not None and s["c"][j] <= px * (1 - stop_pct):
                    reason = "損切り"
                    break
                if ex(j, s, k):
                    reason = "条件"
                    break
                if time_stop is not None and k >= time_stop:
                    reason = "時間"
                    break
            if reason == "データ終端":
                break  # 手じまいが未確定のトレードは数えない
            trades.append({"sym": sym, "in": d, "out": s["date"][j], "ret": s["c"][j] / px - 1,
                           "days": j - i, "rank": rank, "why": reason})
            i = j + 1  # 同じ銘柄は手じまい後に次のシグナルを探す
    trades.sort(key=lambda t: (t["out"], t["sym"]))
    return trades


# ---------- 統計 ----------

def wilson(k, n, z=1.96):
    if n == 0:
        return (0, 0)
    p = k / n
    den = 1 + z * z / n
    mid = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (mid - half, mid + half)


def mean_ci(xs, seed=0):
    """平均の95%信頼区間。同じ日に多数のシグナルが出て互いに独立でないため、
    仕掛けた月ごとにまとめて抜き出すブロック・ブートストラップで出す"""
    if not xs:
        return (0, 0)
    months = {}
    for m, x in xs:
        months.setdefault(m, []).append(x)
    blocks = list(months.values())
    rnd = random.Random(seed)
    means = []
    for _ in range(1000):
        pick = [rnd.choice(blocks) for _ in blocks]
        tot, cnt = sum(sum(b) for b in pick), sum(len(b) for b in pick)
        means.append(tot / cnt)
    means.sort()
    return (means[25], means[974])


def stats(trades, cost):
    rets = [t["ret"] - 2 * cost for t in trades]
    n = len(rets)
    if n == 0:
        return None
    wins = [r for r in rets if r > 0]
    losses = [r for r in rets if r <= 0]
    streak = worst = 0
    for r in rets:
        streak = streak + 1 if r <= 0 else 0
        worst = max(worst, streak)
    gl = -sum(losses)
    return {
        "n": n, "win": len(wins) / n, "win_ci": wilson(len(wins), n),
        "mean": sum(rets) / n,
        "mean_ci": mean_ci([(t["in"][:7], r) for t, r in zip(trades, rets)]),
        "avg_win": sum(wins) / len(wins) if wins else 0, "avg_loss": sum(losses) / len(losses) if losses else 0,
        "pf": sum(wins) / gl if gl else float("inf"), "streak": worst, "min": min(rets),
        "days": sum(t["days"] for t in trades) / n,
    }


def portfolio(trades, cost, slots, days, data):
    """同時保有数の上限つきの資金推移。資金を slots 等分し、その日のシグナルは rank の小さい順に空き枠へ入れる。
    手じまいで戻った資金はその日の引けから次に使える（複利）。保有中はその日の終値で時価評価する。"""
    idx = {sym: {d: k for k, d in enumerate(data[sym]["date"])} for sym in {t["sym"] for t in trades}}

    def value(h, d):
        k = idx[h["sym"]].get(d)
        return h["size"] * data[h["sym"]]["c"][k] / h["px"] if k is not None else h["last"]

    by_in = {}
    for t in trades:
        by_in.setdefault(t["in"], []).append(t)
    cash, held, eq_curve = 1.0, [], []
    peak, mdd, taken = 1.0, 0.0, 0
    for d in days:
        still = []
        for h in held:
            if h["out"] == d:
                cash += h["size"] * (1 + h["ret"] - cost)
            else:
                still.append(h)
        held = still
        for h in held:
            h["last"] = value(h, d)
        equity = cash + sum(h["last"] for h in held)
        for t in sorted(by_in.get(d, []), key=lambda t: t["rank"]):
            if len(held) >= slots:
                break
            if any(h["sym"] == t["sym"] for h in held):
                continue
            size = min(equity / slots, cash)
            if size <= 0:
                break
            cash -= size
            sym_c = data[t["sym"]]["c"][idx[t["sym"]][d]]
            held.append({**t, "size": size * (1 - cost), "px": sym_c, "last": size * (1 - cost)})
            taken += 1
        eq = cash + sum(h["last"] for h in held)
        eq_curve.append(eq)
        peak = max(peak, eq)
        mdd = max(mdd, 1 - eq / peak)
    years = (dt.date.fromisoformat(days[-1]) - dt.date.fromisoformat(days[0])).days / 365.25
    final = eq_curve[-1]
    return {"cagr": final ** (1 / years) - 1, "mdd": mdd, "taken": taken, "final": final}


def pct(x, d=1):
    return f"{x * 100:.{d}f}%"


# ---------- 実行 ----------

def cmd_run(a):
    members = load_members(a.cache)
    missing = set(open(os.path.join(a.cache, "missing.txt")).read().split())
    data = {}
    for sym in members:
        d = load_prices(a.cache, sym)
        if d and len(d["c"]) > 210:
            data[sym] = prepare(d)
    spy, vix = load_prices(a.cache, "SPY"), load_prices(a.cache, "^VIX")
    regime = market_regime(spy)
    days = [d for d in spy["date"] if a.start <= d <= a.end]
    spy_c = dict(zip(spy["date"], spy["c"]))
    spy_cagr = (spy_c[days[-1]] / spy_c[days[0]]) ** (365.25 / (dt.date.fromisoformat(days[-1]) - dt.date.fromisoformat(days[0])).days) - 1
    peak = mdd = 0
    for d in days:
        peak = max(peak, spy_c[d]); mdd = max(mdd, 1 - spy_c[d] / peak)

    # 取得率（期間中に一度でも構成銘柄だった銘柄のうち、価格を取得できた割合）
    in_period = [s for s, sp in members.items() if any(st <= a.end and e >= a.start for st, e in sp)]
    got = [s for s in in_period if s in data]
    periods = [("2015〜2019", "2015-01-01", "2019-12-31"), ("2020〜2022", "2020-01-01", "2022-12-31"),
               ("2023〜", "2023-01-01", "9999-12-31")]

    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: コナーズ 短期売買入門 数値ルールのバックテスト\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_connors.py\n---\n")
    w("# コナーズ 数値ルールのバックテスト\n")
    w(f"- 期間: {days[0]} 〜 {days[-1]}（{len(days)}取引日）")
    w(f"- 対象: その日にS&P500の構成銘柄だった銘柄（構成銘柄の履歴: fja05680/sp500）。期間中の構成銘柄 {len(in_period)} のうち価格を取得できたのは {len(got)}（{pct(len(got) / len(in_period))}）。"
      "取得できなかったのは主に買収・上場廃止・ティッカー変更の銘柄で、上場廃止前の急落を含まない分だけ成績は良く出る方向にずれうる。")
    w("- ルール: `書籍ルール/コナーズ_ルール表.md` の条件（株価≧5ドル、100日平均出来高≧25万株、終値>200日線）＋各エントリー条件。仕掛け・手じまいとも引け値。")
    w("- 価格: 分割調整済み、配当は含まない（数日の保有なので影響は小さい）。")
    w(f"- 手じまい条件が{MAX_HOLD}取引日出ない場合はその日の引けで打ち切り。同じ銘柄の保有中は新しいシグナルを数えない。")
    w("- 局面: SPYの30週線（150日線）の位置と4週前からの傾きでワインスタインのステージを近似（上昇＝線より上かつ上向き、下落＝線より下かつ下向き、それ以外＝横ばい）。")
    w("- 平均リターンの信頼区間は、同じ日のシグナル同士が独立でないため、月単位のブロック・ブートストラップ（1000回）。")
    w(f"- 比較: 同期間のSPY買い持ち 年率 {pct(spy_cagr)}、最大下落率 {pct(mdd)}（配当なし）\n")

    w("## 1. 戦略ごとの成績（ストップなし）\n")
    w("1シグナル＝1トレード（資金の制約なし）。コストは片道。\n")
    w("| 戦略 | 出典 | 件数 | 年平均件数 | 勝率（片道0.1%、95%区間） | 平均（コスト0） | 平均（片道0.05%） | 平均（片道0.1%）（95%区間） | 平均利益/平均損失（0.1%） | PF（0.1%） | 平均保有日数 | 最大連敗 | 最悪 |")
    w("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    years = len(days) / 252
    results = {}
    for name, ent, exn, src in STRATEGIES:
        tr = gen_trades(data, members, ent, exn, STOPS[0], a.start, a.end)
        results[name] = tr
        s0, s1, s2 = (stats(tr, c) for c in COSTS)
        w(f"| {name} | {src} | {s0['n']} | {s0['n'] / years:.0f} | {pct(s2['win'])}（{pct(s2['win_ci'][0])}〜{pct(s2['win_ci'][1])}） | "
          f"{pct(s0['mean'], 2)} | {pct(s1['mean'], 2)} | {pct(s2['mean'], 2)}（{pct(s2['mean_ci'][0], 2)}〜{pct(s2['mean_ci'][1], 2)}） | "
          f"{pct(s2['avg_win'], 2)} / {pct(s2['avg_loss'], 2)} | {s2['pf']:.2f} | {s0['days']:.1f} | {s2['streak']} | {pct(s2['min'])} |")
        print(name, s0["n"], file=sys.stderr)

    base = STRATEGIES[0][0]
    w(f"\n## 2. 基本戦略の期間別・局面別（片道0.1%）\n")
    w("過去の一時期だけ良かったのではないか、局面によって成績が変わるかを見る。\n")
    w("| 区分 | 件数 | 勝率（95%区間） | 平均（95%区間） | PF | 最大連敗 | 最悪 |")
    w("|---|---|---|---|---|---|---|")
    groups = [(p, [t for t in results[base] if s <= t["in"] <= e]) for p, s, e in periods]
    groups += [(f"局面: {r}", [t for t in results[base] if regime.get(t["in"]) == r]) for r in ("上昇", "横ばい", "下落")]
    vix10 = dict(zip(vix["date"], sma(vix["c"], 10)))
    vixc = dict(zip(vix["date"], vix["c"]))
    hi = lambda t: vix10.get(t["in"]) and vixc[t["in"]] >= vix10[t["in"]] * 1.05
    lo = lambda t: vix10.get(t["in"]) and vixc[t["in"]] <= vix10[t["in"]] * 0.95
    groups += [("VIX≧10日線×1.05（p.12 買いに有利）", [t for t in results[base] if hi(t)]),
               ("VIX≦10日線×0.95（p.12 見送り）", [t for t in results[base] if lo(t)])]
    for g, tr in groups:
        s = stats(tr, COSTS[2])
        if not s:
            w(f"| {g} | 0 | | | | | |")
            continue
        w(f"| {g} | {s['n']} | {pct(s['win'])}（{pct(s['win_ci'][0])}〜{pct(s['win_ci'][1])}） | {pct(s['mean'], 2)}（{pct(s['mean_ci'][0], 2)}〜{pct(s['mean_ci'][1], 2)}） | {s['pf']:.2f} | {s['streak']} | {pct(s['min'])} |")

    w("\n## 3. 損切りの有無の比較（未決事項1の判断材料、基本戦略、片道0.1%）\n")
    w("コナーズはストップを置かない原則（p.13, p.36-37, p.45）。損切りは引け値で判定（日中の逆指値ではない）した近似。\n")
    w("| 損切りのルール | 件数 | 勝率 | 平均 | PF | 最大連敗 | 最悪 | 損切り・時間切れの件数 |")
    w("|---|---|---|---|---|---|---|---|")
    stop_results = {}
    for st in STOPS:
        tr = results[base] if st[1] is None and st[2] is None else gen_trades(data, members, STRATEGIES[0][1], STRATEGIES[0][2], st, a.start, a.end)
        stop_results[st[0]] = tr
        s = stats(tr, COSTS[2])
        cut = sum(1 for t in tr if t["why"] in ("損切り", "時間"))
        w(f"| {st[0]} | {s['n']} | {pct(s['win'])} | {pct(s['mean'], 2)} | {s['pf']:.2f} | {s['streak']} | {pct(s['min'])} | {cut} |")

    w("\n## 4. 資金に上限がある場合（同時保有数の上限つき、片道0.1%）\n")
    w("資金を等分し、同じ日のシグナルが空き枠より多いときはRSI(2)（またはその戦略の並べ替え値）の低い順に入れる。"
      "保有中は毎日の終値で時価評価している。\n")
    w("| 戦略 | 同時保有数 | 年率 | 最大下落率 | 実際に入ったトレード数 | 10年で1が何倍 |")
    w("|---|---|---|---|---|---|")
    for name in [STRATEGIES[0][0], STRATEGIES[5][0], STRATEGIES[6][0]]:
        for slots in (5, 10, 20):
            p = portfolio(results[name], COSTS[2], slots, days, data)
            w(f"| {name} | {slots} | {pct(p['cagr'])} | {pct(p['mdd'])} | {p['taken']} | {(1 + p['cagr']) ** 10:.2f} |")
    w(f"| （参考）SPY買い持ち | | {pct(spy_cagr)} | {pct(mdd)} | | {(1 + spy_cagr) ** 10:.2f} |")

    w("\n## 5. 注意\n")
    w("- 過去の成績は将来を保証しない。特に上場廃止銘柄の欠落（生存者バイアスの残り）、配当なし、引け値ちょうどで約定できる前提は、いずれも現実より良く見せる方向に働きうる。")
    w("- 1シグナル＝1トレードの統計は、同じ日に多数のシグナルが重なる（相場全体の急落時）ため、件数ほど独立ではない。信頼区間は月単位のブロックで補正した。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    open(a.out, "w").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch")
    f.add_argument("--cache", default=DEFAULT_CACHE)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/コナーズ.md")
    r.add_argument("--start", default="2015-01-02")
    r.add_argument("--end", default=dt.date.today().isoformat())
    a = ap.parse_args()
    (cmd_fetch if a.cmd == "fetch" else cmd_run)(a)


if __name__ == "__main__":
    main()
