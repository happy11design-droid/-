#!/usr/bin/env python3
"""バックテストの共通部品（データ取得・指標・売買の再現・統計・ポートフォリオ）

各著者のバックテスト（tools/backtest_connors.py, tools/backtest_trend.py など）から使う。
  tools/backtest_lib.py fetch [--cache DIR]
      S&P500の過去の構成銘柄（fja05680/sp500 の日付つき構成銘柄表）と、2015年以降に一度でも構成銘柄だった
      全銘柄＋SPY・QQQ・^VIXの日足（2013年〜）をYahooから取得してキャッシュする。取得できなかった銘柄は一覧に残す。

前提（各レポートにも明記する）:
  - シグナルはその日の構成銘柄だけで出す（今の構成銘柄だけで検証したときの生存者バイアスを避けるため）。
    ただしYahooから消えた上場廃止銘柄は取得できないので、その分のバイアスは残る。
  - 価格は配当・株式分割調整済み（Yahooの調整後終値の比率で始値・高値・安値も調整）。
"""
import argparse
import csv
import datetime as dt
import json
import math
import os
import random
import subprocess
import sys
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
MEMBERS_URL = "https://raw.githubusercontent.com/fja05680/sp500/master/sp500_ticker_start_end.csv"
DEFAULT_CACHE = os.path.expanduser("~/.cache/stock_backtest")
FETCH_FROM = dt.datetime(2013, 1, 1)
MEMBER_SINCE = "2015-01-01"
COSTS = (0.0, 0.0005, 0.001)   # 片道


# ---------- 取得 ----------

def curl(url):
    # --compressed: サイトが圧縮した応答（gzip）を返すことがあり、そのままでは文字として読めず落ちた（2026-09-27）
    r = subprocess.run(["curl", "-sS", "--compressed", "--max-time", "30", "-A", UA, url], capture_output=True)
    return r.stdout.decode("utf-8", errors="replace") if r.returncode == 0 else ""


def fetch_one(symbol, path):
    if os.path.exists(path):
        return True
    p1, p2 = int(FETCH_FROM.timestamp()), int(time.time())
    for attempt in range(3):
        txt = curl(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&period1={p1}&period2={p2}")
        try:
            res = json.loads(txt)["chart"]["result"][0]
            q = res["indicators"]["quote"][0]
            adj = res["indicators"].get("adjclose", [{}])[0].get("adjclose") or q["close"]
            off = res["meta"].get("gmtoffset", 0)
            rows = []
            for i, t in enumerate(res["timestamp"]):
                o, h, l, c, v, ac = q["open"][i], q["high"][i], q["low"][i], q["close"][i], q["volume"][i], adj[i]
                if None in (o, h, l, c):
                    continue
                rows.append([dt.datetime.utcfromtimestamp(t + off).strftime("%Y-%m-%d"), o, h, l, c, v or 0, ac or c])
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
    syms = sorted(members) + ["SPY", "QQQ", "^VIX"]
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
    """始値・高値・安値・終値は配当・分割調整済み（Yahooの調整後終値÷終値の比率を掛ける）。
    特別配当やスピンオフが「暴落」に見えるのを防ぐため（例: KDP 2018年の1株103ドルの特別配当）"""
    rows = json.load(open(p))
    d = {"date": [], "o": [], "h": [], "l": [], "c": [], "v": []}
    for r in rows:
        f = r[6] / r[4] if len(r) > 6 and r[4] else 1.0
        d["date"].append(r[0])
        for k, x in zip(("o", "h", "l", "c"), r[1:5]):
            d[k].append(x * f)
        d["v"].append(r[5])
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


def sliding(x, n, better, include_today):
    """直近n本の最大（better=operator.ge）・最小（operator.le）。include_today=False なら当日を含まない"""
    out, dq = [None] * len(x), deque()
    for i, v in enumerate(x):
        if not include_today and i >= n:
            out[i] = x[dq[0]]
        while dq and better(v, x[dq[-1]]):
            dq.pop()
        dq.append(i)
        if dq[0] <= i - n:
            dq.popleft()
        if include_today:
            out[i] = x[dq[0]]
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


def is_member(spans, day):
    return any(s <= day <= e for s, e in spans)



def gen_trades(data, members, entry, exit_fn, start, end, *, ok, fill="open", allow=None, max_hold=30,
               stop_pct=None, time_stop=None, target=None, breakeven_at=None):
    """シグナルから売買を再現する。
    entry(i, s) -> シグナルなら並べ替え用の値（小さいほど優先）、なければNone
    exit_fn(j, s, k, px) -> k日目（仕掛けからの経過取引日）の引けで手じまい条件が出たか
    ok(s, i, 構成期間) -> 銘柄選定の条件を満たすか
    fill="close": シグナルの日の引けで仕掛け、手じまい条件の日の引けで手じまう。
    fill="open": 引け後に判定して翌取引日の寄り付きで仕掛け・手じまう（引け後に分析する運用で実際にできる方法）。
    allow(日付): 市場全体の条件（局面・VIX）でその日のシグナルを使うか。Noneなら常に使う。
    stop_pct: 引け値が仕掛け値×(1−stop_pct)以下で損切り。target: 引け値が仕掛け値×(1+target)以上で利確。
    breakeven_at: 引け値が仕掛け値×(1+breakeven_at)以上になった後は、損切りの位置を仕掛け値に引き上げる。
    損切り・利確とも引け値で判定する（日中の逆指値・指値ではない）。"""
    lag = 1 if fill == "open" else 0
    price = (lambda s, k: s["o"][k]) if fill == "open" else (lambda s, k: s["c"][k])
    trades = []
    for sym, s in data.items():
        n, i = len(s["c"]), 200
        while i < n - 1:
            d = s["date"][i]
            if d < start or d > end or not ok(s, i, members[sym]) or (allow and not allow(d)):
                i += 1
                continue
            rank = entry(i, s)
            if rank is None or i + lag >= n:
                i += 1
                continue
            px, j, reason = price(s, i + lag), i, "打ち切り"
            floor = px * (1 - stop_pct) if stop_pct is not None else None
            for k in range(1, max_hold + 1):
                j = i + k
                if j + lag >= n:
                    j, reason = n - 1, "データ終端"
                    break
                c = s["c"][j]
                if floor is not None and c <= floor:
                    reason = "損切り" if floor < px else "建値"
                    break
                if target is not None and c >= px * (1 + target):
                    reason = "利確"
                    break
                if exit_fn(j, s, k, px):
                    reason = "条件"
                    break
                if time_stop is not None and k >= time_stop:
                    reason = "時間"
                    break
                if breakeven_at is not None and c >= px * (1 + breakeven_at):
                    floor = max(floor or 0, px)
            if reason == "データ終端":
                break  # 手じまいが未確定のトレードは数えない
            trades.append({"sym": sym, "in": s["date"][i + lag], "out": s["date"][j + lag], "px": px,
                           "ret": price(s, j + lag) / px - 1, "days": j - i, "rank": rank, "why": reason})
            i = j + lag + 1  # 同じ銘柄は手じまい後に次のシグナルを探す
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


_IDX = {}


def portfolio(trades, cost, slots, days, data, weight=None, seed=None, cash_asset=None, group_of=None, group_cap=None,
              group2_of=None, group2_cap=None, day_cap=None):
    """同時保有数の上限つきの資金推移。資金を slots 等分し、その日のシグナルは rank の小さい順に空き枠へ入れる。
    手じまいで戻った資金はその日の引けから次に使える（複利）。保有中はその日の終値で時価評価する。
    weight を指定すると1銘柄の建玉を資金×weight にする（リスク2%・損切り幅X%なら weight=0.02/X）。
    seed を指定すると、同じ日の候補を rank ではなくランダムな順で選ぶ（並べ替えの選び方に結果が左右されていないかを見るため）。
    cash_asset（{日付: 終値}）を指定すると、使っていない資金をその銘柄（SPYなど）で持っているものとして毎日の値動きを反映する
    （入れ替えの売買コストは入れていない）。
    group_of（{銘柄: グループ}）と group_cap を指定すると、同じグループの同時保有を group_cap 銘柄までにする。
    group2_of と group2_cap で、2つ目のまとまり（セクターなど）の上限も同時にかけられる。
    day_cap を指定すると、1日に新しく買う銘柄数をその数までにする。返り値の curve は毎日の資金（最初を1とする）。"""
    weight = weight or 1 / slots
    for sym in {t["sym"] for t in trades}:
        key = id(data[sym]["date"])
        if key not in _IDX:
            _IDX[key] = {d: k for k, d in enumerate(data[sym]["date"])}
    idx = {sym: _IDX[id(data[sym]["date"])] for sym in {t["sym"] for t in trades}}
    # 同順位は銘柄名の順（trades は手じまい日の順に並んでいるため、そのままだと早く手じまう＝将来の情報で選ぶことになる）
    order = (lambda t: (t["rank"], t["sym"])) if seed is None else (lambda t, r=random.Random(seed): r.random())

    def value(h, d):
        k = idx[h["sym"]].get(d)
        return h["size"] * data[h["sym"]]["c"][k] / h["px"] if k is not None else h["last"]

    by_in = {}
    for t in trades:
        by_in.setdefault(t["in"], []).append(t)
    cash, held, eq_curve = 1.0, [], []
    peak, mdd, taken, worst_hit, exposure = 1.0, 0.0, 0, 0.0, 0.0
    prev, buy_days, busy_days, act_days = None, 0, 0, 0
    for d in days:
        if cash_asset and prev is not None and cash > 0:
            cash *= cash_asset[d] / cash_asset[prev]
        prev = d
        still, sold = [], False
        for h in held:
            if h["out"] == d:
                cash += h["size"] * (1 + h["ret"] - cost)
                worst_hit = max(worst_hit, -h["size"] * (h["ret"] - cost) / h["eq0"])
                sold = True
            else:
                still.append(h)
        held = still
        for h in held:
            h["last"] = value(h, d)
        equity = cash + sum(h["last"] for h in held)
        taken0 = taken
        for t in sorted(by_in.get(d, []), key=order):
            if len(held) >= slots or (day_cap and taken - taken0 >= day_cap):
                break
            if any(h["sym"] == t["sym"] for h in held):
                continue
            if group_cap and sum(1 for h in held if group_of.get(h["sym"]) == group_of.get(t["sym"])) >= group_cap:
                continue
            if group2_cap and sum(1 for h in held if group2_of.get(h["sym"]) == group2_of.get(t["sym"])) >= group2_cap:
                continue
            size = min(equity * weight, cash)
            if size <= 0:
                break
            cash -= size
            h = {**t, "size": size * (1 - cost), "eq0": equity, "last": size * (1 - cost)}
            taken += 1
            if t["out"] == d:   # 仕掛けた日のうちに手じまい（逆指値の損切りなど）
                cash += h["size"] * (1 + h["ret"] - cost)
                worst_hit = max(worst_hit, -h["size"] * (h["ret"] - cost) / equity)
                continue
            h["last"] = value(h, d)
            held.append(h)
        buy_days += taken > taken0
        busy_days += bool(held) or taken > taken0
        act_days += sold or taken > taken0
        eq = cash + sum(h["last"] for h in held)
        eq_curve.append(eq)
        exposure += 1 - cash / eq
        peak = max(peak, eq)
        mdd = max(mdd, 1 - eq / peak)
    years = (dt.date.fromisoformat(days[-1]) - dt.date.fromisoformat(days[0])).days / 365.25
    final = eq_curve[-1]
    return {"cagr": final ** (1 / years) - 1, "mdd": mdd, "taken": taken, "final": final, "worst_hit": worst_hit,
            "exposure": exposure / len(days), "buy_days": buy_days / len(days), "busy_days": busy_days / len(days),
            "act_days": act_days / len(days), "curve": eq_curve}


def pct(x, d=1):
    return f"{x * 100:.{d}f}%"


class Reporter:
    """戦略ごとの成績を1行にまとめる表（1トレード＝1件の統計と、リスク2%で建玉したポートフォリオ）。
    ポートフォリオの同じ日の候補の選び方はルール表にないため、rank順とランダムな順（10通りの中央値と幅）の両方を出す。"""
    SEEDS = range(10)

    def __init__(self, w, data, days, halves, years, cost, risk):
        self.w, self.data, self.days, self.halves, self.years, self.cost, self.risk = w, data, days, halves, years, cost, risk

    def port(self, tr, stop, lo=None, hi=None, seed=None):
        lo, hi = lo or self.days[0], hi or self.days[-1]
        dd = [d for d in self.days if lo <= d <= hi]
        return portfolio([t for t in tr if lo <= t["in"] and t["out"] <= hi], self.cost, max(1, int(round(stop / self.risk, 6))),
                         dd, self.data, weight=self.risk / stop, seed=seed)

    @staticmethod
    def med(xs):
        xs = sorted(xs)
        return xs[len(xs) // 2]

    def header(self, rank_label="RSの高い順"):
        self.w("| 条件 | 年平均件数 | 勝率 | 平均利益 / 平均損失 | 1トレード平均（95%区間）/ PF | 平均保有日数 | 前半 PF / 後半 PF "
               f"| 年率 ランダム順 中央値（幅） | 最大下落率 ランダム順 中央値 | 前半 / 後半 年率（ランダム順 中央値） | 年率 / 最大下落率（{rank_label}） | 平均投資比率 |")
        self.w("|---|---|---|---|---|---|---|---|---|---|---|---|")

    def line(self, label, tr, stop):
        w, cost, halves, med = self.w, self.cost, self.halves, self.med
        st = stats(tr, cost)
        if not st:
            w(f"| {label} | 0 | | | | | | | | | | |")
            return
        pfs = []
        for _, lo, hi in halves:
            sh = stats([t for t in tr if lo <= t["in"] <= hi], cost)
            pfs.append(f"{sh['pf']:.2f}" if sh else "-")
        rnd = [self.port(tr, stop, seed=k) for k in self.SEEDS]
        h1 = med([self.port(tr, stop, *halves[0][1:], seed=k)["cagr"] for k in self.SEEDS])
        h2 = med([self.port(tr, stop, *halves[1][1:], seed=k)["cagr"] for k in self.SEEDS])
        cg = [p["cagr"] for p in rnd]
        p = self.port(tr, stop)
        w(f"| {label} | {st['n'] / self.years:.0f} | {pct(st['win'])} | {pct(st['avg_win'], 1)} / {pct(st['avg_loss'], 1)} | "
          f"{pct(st['mean'], 2)}（{pct(st['mean_ci'][0], 2)}〜{pct(st['mean_ci'][1], 2)}）/ {st['pf']:.2f} | {st['days']:.0f} | "
          f"{pfs[0]} / {pfs[1]} | {pct(med(cg))}（{pct(min(cg))}〜{pct(max(cg))}） | {pct(med([q['mdd'] for q in rnd]))} | "
          f"{pct(h1)} / {pct(h2)} | {pct(p['cagr'])} / {pct(p['mdd'])} | {pct(p['exposure'], 0)} |")
        print(label, st["n"], file=sys.stderr)


def load_universe(cache, min_bars=210):
    """構成銘柄の履歴と、価格を取得できた銘柄の日足を返す"""
    members = load_members(cache)
    data = {}
    for sym in members:
        d = load_prices(cache, sym)
        if d and len(d["c"]) > min_bars:
            data[sym] = d
    return members, data


def spy_benchmark(spy, days):
    c = dict(zip(spy["date"], spy["c"]))
    cagr = (c[days[-1]] / c[days[0]]) ** (365.25 / (dt.date.fromisoformat(days[-1]) - dt.date.fromisoformat(days[0])).days) - 1
    peak = mdd = 0
    for d in days:
        peak = max(peak, c[d])
        mdd = max(mdd, 1 - c[d] / peak)
    return cagr, mdd


def coverage(members, data, start, end):
    in_period = [s for s, sp in members.items() if any(st <= end and e >= start for st, e in sp)]
    return len(in_period), sum(1 for s in in_period if s in data)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch")
    f.add_argument("--cache", default=DEFAULT_CACHE)
    cmd_fetch(ap.parse_args())


if __name__ == "__main__":
    main()
