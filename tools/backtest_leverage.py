#!/usr/bin/env python3
"""値動きに合わせた建玉で損失を小さくした分、リスクを足して年率を上げられるか（3銘柄・信用取引・2倍ETF）のバックテスト

使い方:
  tools/backtest_leverage.py run [--out FILE]

土台は今の採用ルール（4つのルール、4銘柄・1銘柄25%、損切り15%、急落の底RSI(2)≦10、同じ業種2銘柄まで、
押し目は前日の上部バンドに指値で売る、順張りは反転の合図で半分売る〔どちらも2026-10-01 採用〕）。比べる形:
  値動きに合わせた建玉: 押し目（ボリンジャーIII）だけ、額＝25%×（基準のATR%÷その銘柄のATR%）、10〜40%（`値動きに合わせた建玉.md` と同じ）
  3銘柄: 1銘柄の額を4/3倍（基準33%）にして、同時に3銘柄まで
  信用取引: 1銘柄の額を1.2倍・1.3倍にする（買える額の合計は資金の1.2倍・1.3倍まで）。借りた分に年6.5%の金利（毎日）
  2倍ETF: 合図・売りの日は元の株のまま、毎日、株の値動きの2倍だけ動く（毎日合わせ直す、経費 年1%、0より下にはならない）。
          損切りは株の15%下のまま（ETFでは約30%）。`2倍ETFに置き換えた場合.md` と同じ再現の仕方
片道0.1%。選び方の乱数50通りの中央値。設計期間 2015〜2021年 / 確認期間 2022年〜。
「倍になった年」「半分近く（−40%以下）になった年」は、暦年ごとの資金の増減（50通りの中央値）で数える。
"""
import argparse
import datetime as dt
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_combo2 as cb
import backtest_exit_combo as xc
import backtest_exit_signals as xs
import backtest_minervini2 as bm2
import backtest_swing as bs
from backtest_lib import COSTS, DEFAULT_CACHE, pct

COST = COSTS[2]
SEEDS = range(50)
STOP = 0.15
RATE = 0.065
FEE = 0.01 / 252


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default=None)
    r.add_argument("--set", default="vol", choices=("vol", "slots"),
                   help="vol: 値動きに合わせた建玉にリスクを足す／slots: 今のルール（株）のまま銘柄数と信用取引を変える")
    a = ap.parse_args()
    a.out = a.out or ("新分析ツール/バックテスト結果/リスクを足して年率を上げる.md" if a.set == "vol" else "新分析ツール/バックテスト結果/銘柄数と信用取引.md")
    ctx = cb.setup(a.cache, with_parts=False)
    data, members, ind, days, G, end = (ctx[k] for k in ("data", "members", "ind", "days", "G", "end"))
    pos = {}

    def idx(sym, d):
        if sym not in pos:
            pos[sym] = {x: k for k, x in enumerate(data[sym]["date"])}
        return pos[sym][d]

    def atrp(sym, d):
        s = data[sym]
        i = idx(sym, d) - 1
        h, l, c = s["h"], s["l"], s["c"]
        return sum(max(h[k] - l[k], abs(h[k] - c[k - 1]), abs(l[k] - c[k - 1])) for k in range(i - 13, i + 1)) / 14 / c[i]

    def path_trade(t, rule, pv):
        i1 = max(idx(t["sym"], d) for d in pv)
        out = data[t["sym"]]["date"][i1]
        return {"sym": t["sym"], "in": t["in"], "out": out, "path": pv, "rule": rule, "ret": pv[out] - 1, "atrp": atrp(t["sym"], t["in"])}

    def plain(t, rule):
        s, sym = data[t["sym"]], t["sym"]
        i0, i1 = idx(sym, t["in"]), idx(sym, t["out"])
        sh = (1 - COST) / t["px"]
        pv = {s["date"][j]: sh * s["c"][j] for j in range(i0, i1)}
        pv[s["date"][i1]] = sh * t["px"] * (1 + t["ret"]) * (1 - COST)
        return path_trade(t, rule, pv)

    def b3_limit(t):
        s, sym = data[t["sym"]], t["sym"]
        o, h, l, c = s["o"], s["h"], s["l"], s["c"]
        i0, n, px = idx(sym, t["in"]), len(c), t["px"]
        floor, sh, pv, pend, j = px * (1 - STOP), (1 - COST) / px, {}, False, i0
        while j < n:
            d = s["date"][j]
            if pend:
                pv[d] = sh * o[j] * (1 - COST)
                break
            if l[j] <= floor:
                pv[d] = sh * min(o[j] if j > i0 else px, floor) * (1 - COST)
                break
            if j > i0 and s["bb_up"][j - 1] is not None and h[j] >= s["bb_up"][j - 1]:
                pv[d] = sh * max(o[j], s["bb_up"][j - 1]) * (1 - COST)
                break
            pv[d] = sh * c[j]
            if j + 1 >= n:
                return None
            if j - i0 >= bs.MAX_HOLD or (s["pctb"][j] is not None and s["pctb"][j] >= 1.0):
                pend = True
            j += 1
        return path_trade(t, "B", pv) if pv else None

    def half(t, rule):
        s, sym = data[t["sym"]], t["sym"]
        i0, i1 = idx(sym, t["in"]), idx(sym, t["out"])
        px = t["px"]
        sh, cash, pv, done = (1 - COST) / px, 0.0, {}, False
        for j in range(i0, i1):
            pv[s["date"][j]] = cash + sh * s["c"][j]
            if not done and j >= 2 and j + 1 < i1 and xc.c1(s, j):
                done = True
                cash += sh / 2 * s["o"][j + 1] * (1 - COST)
                sh /= 2
        pv[s["date"][i1]] = cash + sh * px * (1 + t["ret"]) * (1 - COST)
        return path_trade(t, rule, pv)

    old, bs.STOP_MAX = bs.STOP_MAX, STOP
    try:
        b3_raw = bs.simulate(data, members, bs.O_method3, bs.X_upper_band, cb.START, end, ok=ctx["ok_rot"])
    finally:
        bs.STOP_MAX = old
    M_raw = G(bm2.E_base(2.0), ctx["below50"], ctx["ok_rot"], STOP)
    V_raw = G(ctx["v2o"], ctx["below50"], ctx["ok10"], STOP)
    for sym in {t["sym"] for t in M_raw + V_raw}:
        xs.prep(data[sym])
    base = ([x for x in (b3_limit(t) for t in b3_raw) if x]
            + [plain(t, "C") for t in G(ctx["CR"](10), ctx["above5"], ctx["ok_rot"], STOP, 60)]
            + [half(t, "M") for t in M_raw] + [half(t, "V") for t in V_raw])
    ref = sorted(t["atrp"] for t in base)[len(base) // 2]

    def sized(trs, mult=1.0, vol=True):
        return [{**t, "w": mult * (min(0.40, max(0.10, 0.25 * ref / t["atrp"])) if vol and t["rule"] == "B" else 0.25)} for t in trs]

    def to2x(trs, rules=("B", "C", "M", "V")):
        out = []
        for t in trs:
            if t["rule"] not in rules:
                out.append(t)
                continue
            ds = sorted(t["path"])
            e, prev, pv = 1.0 - COST, 1.0 - COST, {}
            for d in ds:
                g = t["path"][d]
                e = max(0.0, e * (1 + 2 * (g / prev - 1)) * (1 - FEE))
                prev = g
                pv[d] = e
            out.append({**t, "path": pv, "ret": pv[ds[-1]] - 1})
        return out

    is_hi = max(d for d in days if d <= cb.IS_END)
    oos_lo = min(d for d in days if d >= cb.OOS_START)
    years = sorted({d[:4] for d in days})

    def port(trs, seed, lo, hi, slots=4, lev=1.0):
        dd = [d for d in days if lo <= d <= hi]
        by_in = {}
        for t in trs:
            if lo <= t["in"] and t["out"] <= hi:
                by_in.setdefault(t["in"], []).append(t)
        rnd = random.Random(seed)
        cash, held, peak, mdd, eq, ye = 1.0, [], 1.0, 0.0, 1.0, {}
        for d in dd:
            if cash < 0:
                cash *= 1 + RATE / 252
            still = []
            for h in held:
                v = h["t"]["path"].get(d)
                if v is not None:
                    h["v"] = v
                if h["t"]["out"] == d:
                    cash += h["size"] * h["v"]
                else:
                    still.append(h)
            held = still
            eq = cash + sum(h["size"] * h["v"] for h in held)
            for t in sorted(by_in.get(d, []), key=lambda t: rnd.random()):
                if any(h["t"]["sym"] == t["sym"] for h in held):
                    continue
                if len(held) >= slots:
                    break
                if sum(1 for h in held if ind.get(h["t"]["sym"]) == ind.get(t["sym"])) >= 2:
                    continue
                size = min(eq * t["w"], cash + (lev - 1) * max(eq, 0))
                if size <= 0 or eq <= 0:
                    break
                cash -= size
                v0 = t["path"].get(d, 1.0)
                if t["out"] == d:
                    cash += size * v0
                    continue
                held.append({"t": t, "size": size, "v": v0})
            eq = cash + sum(h["size"] * h["v"] for h in held)
            ye[d[:4]] = eq
            peak = max(peak, eq)
            mdd = max(mdd, 1 - eq / peak) if peak > 0 else 1.0
        yrs = (dt.date.fromisoformat(dd[-1]) - dt.date.fromisoformat(dd[0])).days / 365.25
        prev, yr = 1.0, {}
        for y in sorted(ye):
            yr[y] = ye[y] / prev - 1 if prev > 0 else -1.0
            prev = ye[y]
        return (max(eq, 0) ** (1 / yrs) - 1), mdd, yr

    def evaluate(trs, **kw):
        a_ = [port(trs, 9500 + k, days[0], days[-1], **kw) for k in SEEDS]
        i_ = [port(trs, 9500 + k, days[0], is_hi, **kw)[0] for k in SEEDS]
        o_ = [port(trs, 9500 + k, oos_lo, days[-1], **kw)[0] for k in SEEDS]
        yr = {y: cb.med([x[2].get(y, 0) for x in a_]) for y in years}
        return {"all": cb.med([x[0] for x in a_]), "mdd": cb.med([x[1] for x in a_]), "is": cb.med(i_), "oos": cb.med(o_), "yr": yr,
                "mddmax": max(x[1] for x in a_)}

    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: " + ("リスクを足して年率を上げる" if a.set == "vol" else "銘柄数と信用取引") + "\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_leverage.py\n---\n")
    w("# 値動きに合わせた建玉で損失を小さくした分、リスクを足して年率を上げられるか\n" if a.set == "vol" else "# 今のルール（株）のまま、銘柄数と信用取引を変える\n")
    w(__doc__.split("\n", 5)[5].strip() + "\n")
    w("| 形 | 年率 | 最大下落率 | 最大下落率（50通りの最悪） | 設計期間 | 確認期間 | 一番良い年 | 一番悪い年 | 倍になった年 | −40%以下の年 | 18,000ドルが最後にいくら |")
    w("|---|---|---|---|---|---|---|---|---|---|---|")
    yrs_all = (dt.date.fromisoformat(days[-1]) - dt.date.fromisoformat(days[0])).days / 365.25
    stock, etf = base, to2x(base)
    rows = [
        ("今のルール（株、全部25%）", sized(stock, vol=False), {}),
        ("押し目だけ値動きに合わせた建玉", sized(stock), {}),
        ("押し目だけ値動き＋3銘柄（基準33%）", sized(stock, 4 / 3), {"slots": 3}),
        ("押し目だけ値動き＋信用取引1.2倍", sized(stock, 1.2), {"lev": 1.2}),
        ("押し目だけ値動き＋信用取引1.3倍", sized(stock, 1.3), {"lev": 1.3}),
        ("今のルールを全部2倍ETF（25%）", sized(etf, vol=False), {}),
        ("押し目だけ値動き＋全部2倍ETF", sized(etf), {}),
        ("押し目だけ2倍ETF、ほかは株", sized(to2x(stock, ("B",)), vol=False), {}),
        ("順張りだけ2倍ETF、ほかは株", sized(to2x(stock, ("M", "V")), vol=False), {}),
        ("今のルールを2倍ETF・3銘柄（33%）", sized(etf, 4 / 3, vol=False), {"slots": 3}),
    ]
    if a.set == "slots":
        p = sized(stock, vol=False)
        rows = [("今のルール（4銘柄・25%）", p, {})]
        for n in (3, 2):
            rows.append((f"{n}銘柄（1銘柄{100 // n}%）", sized(stock, 4 / n, vol=False), {"slots": n}))
        for lev in (1.2, 1.3, 1.5):
            rows.append((f"4銘柄・信用取引{lev}倍（1銘柄{25 * lev:.1f}%）", sized(stock, lev, vol=False), {"lev": lev}))
        for lev in (1.2, 1.5):
            rows.append((f"3銘柄・信用取引{lev}倍（1銘柄{100 / 3 * lev:.0f}%）", sized(stock, 4 / 3 * lev, vol=False), {"slots": 3, "lev": lev}))
        rows.append(("5銘柄・信用取引1.25倍（1銘柄25%）", sized(stock, vol=False), {"slots": 5, "lev": 1.25}))
        rows.append(("6銘柄・信用取引1.5倍（1銘柄25%）", sized(stock, vol=False), {"slots": 6, "lev": 1.5}))
    for lab, trs, kw in rows:
        e = evaluate(trs, **kw)
        best = max(e["yr"], key=e["yr"].get)
        worst = min(e["yr"], key=e["yr"].get)
        dbl = [y for y in years if e["yr"][y] >= 1.0]
        bad = [y for y in years if e["yr"][y] <= -0.40]
        w(f"| {lab} | {pct(e['all'])} | {pct(e['mdd'])} | {pct(e['mddmax'])} | {pct(e['is'])} | {pct(e['oos'])} | "
          f"{best} {pct(e['yr'][best], 0)} | {worst} {pct(e['yr'][worst], 0)} | {len(dbl)}回{'（' + '・'.join(dbl) + '）' if dbl else ''} | "
          f"{len(bad)}回{'（' + '・'.join(bad) + '）' if bad else ''} | {18000 * (1 + e['all']) ** yrs_all:,.0f}ドル |")
        print(lab, file=sys.stderr)
    w(f"\n期間: {days[0]}〜{days[-1]}（約{yrs_all:.1f}年）。{years[-1]}年は途中まで。\n")
    w("## 注意\n")
    w("- 2倍ETFは元の株の値動きからの再現。実物の2倍ETFは多くが2022年以降の上場で、ない銘柄も多い。")
    w("- 信用取引は、追加の保証金（追い証）や強制決済を考えていない。下落が大きいときは、実際にはここより悪くなりうる。")
    w("- 倒産・上場廃止になった銘柄の株価はデータにない（`損切りの幅となしの比較.md`）。損切りで売るので影響は小さいが、2倍ETFでは株の下げが2倍になる。")
    w("- 年ごとの数字は50通りの中央値なので、実際の1通りでは、これより良い年・悪い年がありうる（「50通りの最悪」の最大下落率を参照）。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
