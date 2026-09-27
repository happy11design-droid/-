#!/usr/bin/env python3
"""テーマ（業種）で銘柄を選ぶための対象銘柄一覧と、業種ごとの強さの順位（ヒートマップの代わり）

使い方:
  tools/theme_universe.py fetch [--cache DIR] [--min-cap 1e9]
      米国上場の普通株のうち時価総額が min-cap 以上の銘柄を NASDAQ のスクリーナーから取り、Yahoo の業種（industry）を付けて
      <cache>/universe.json に保存する。あわせて日足（backtest_lib と同じ形式）を <cache>/prices/ に取得する。
  tools/theme_universe.py heatmap [--cache DIR] [--asof YYYY-MM-DD] [--top 15]
      業種ごとの強さ（構成銘柄の騰落率の中央値）を、1週・1カ月・3カ月で並べて表示する。

SBI証券のヒートマップはログインが必要で自動取得できないため、同じ考え方（業種ごとの騰落率）を価格データから計算する。
業種の分類は Yahoo Finance の industry（例: Semiconductors, Communication Equipment, Computer Hardware）。
注意: 対象銘柄は「いま上場していて時価総額が大きい銘柄」なので、過去の検証では生き残った銘柄に偏る（生存者バイアス）。
"""
import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backtest_lib import DEFAULT_CACHE, curl, fetch_one, load_prices

SCREENER = "https://api.nasdaq.com/api/screener/stocks?tableonly=true&limit=25000&download=true"


def yahoo_profile(sym):
    try:
        q = json.loads(curl(f"https://query1.finance.yahoo.com/v1/finance/search?q={sym}&quotesCount=3&newsCount=0"))["quotes"]
        for x in q:
            if x.get("symbol") == sym and x.get("quoteType") == "EQUITY":
                return {"sector": x.get("sector", ""), "industry": x.get("industry", ""), "name": x.get("longname") or x.get("shortname", "")}
    except Exception:
        pass
    return None


def cmd_fetch(a):
    os.makedirs(os.path.join(a.cache, "prices"), exist_ok=True)
    rows = json.loads(curl(SCREENER))["data"]["rows"]
    def cap(r):
        try:
            return float(r["marketCap"] or 0)
        except ValueError:
            return 0.0
    syms = sorted({r["symbol"].strip() for r in rows if cap(r) >= a.min_cap and r["symbol"].strip().isalpha()})
    path = os.path.join(a.cache, "universe.json")
    uni = json.load(open(path)) if os.path.exists(path) else {}
    todo = [s for s in syms if s not in uni]
    with ThreadPoolExecutor(8) as ex:
        for s, p in zip(todo, ex.map(yahoo_profile, todo)):
            if p and p["industry"]:
                uni[s] = p
    caps = {r["symbol"].strip(): cap(r) for r in rows}
    for s in uni:
        uni[s]["cap"] = caps.get(s, uni[s].get("cap", 0))
    json.dump(uni, open(path, "w"), ensure_ascii=False, indent=0)
    with ThreadPoolExecutor(8) as ex:
        ok = list(ex.map(lambda s: fetch_one(s, os.path.join(a.cache, "prices", s + ".json")), sorted(uni)))
    print(f"時価総額{a.min_cap / 1e8:.0f}億ドル以上 {len(syms)} 銘柄、業種を取得 {len(uni)}、日足を取得 {sum(ok)}")


def load_universe_theme(cache, min_bars=260):
    uni = json.load(open(os.path.join(cache, "universe.json")))
    data = {}
    for s, p in uni.items():
        d = load_prices(cache, s)
        if d and len(d["c"]) > min_bars:
            d["sym"], d["industry"], d["sector"] = s, p["industry"], p["sector"]
            data[s] = d
    return uni, data


def industry_strength(data, lookbacks=(5, 21, 63, 126, 252), min_members=3, min_dollar_vol=20e6):
    """日付ごと・業種ごとの騰落率の中央値。{日付: {業種: {5: x, 21: y, 63: z, "n": 件数}}}
    その日に売買代金（50日平均）が min_dollar_vol 以上の銘柄だけで計算する"""
    by = {}
    for s in data.values():
        c, v = s["c"], s["v"]
        dv = [None] * len(c)
        acc = 0.0
        for i in range(len(c)):
            acc += c[i] * v[i]
            if i >= 50:
                acc -= c[i - 50] * v[i - 50]
            if i >= 49:
                dv[i] = acc / 50
        maxlb = max(lookbacks)
        for i in range(maxlb, len(c)):
            if dv[i] is None or dv[i] < min_dollar_vol:
                continue
            rets = tuple(c[i] / c[i - k] - 1 for k in lookbacks)
            by.setdefault(s["date"][i], {}).setdefault(s["industry"], []).append(rets)
    out = {}
    for d, inds in by.items():
        out[d] = {}
        for ind, rs in inds.items():
            if len(rs) < min_members:
                continue
            row = {"n": len(rs)}
            for j, k in enumerate(lookbacks):
                xs = sorted(r[j] for r in rs)
                row[k] = xs[len(xs) // 2]
            out[d][ind] = row
    return out


def leading(strength, day, top, key=63):
    """その日の上位業種（key日の騰落率の中央値が高い順に top 業種）"""
    inds = strength.get(day, {})
    return set(sorted(inds, key=lambda x: -inds[x][key])[:top])


def cmd_heatmap(a):
    uni, data = load_universe_theme(a.cache, min_bars=70)
    st = industry_strength(data)
    day = a.asof or max(st)
    day = max(d for d in st if d <= day)
    inds = st[day]
    print(f"業種ごとの騰落率の中央値（{day}時点、売買代金2000万ドル以上・3銘柄以上の業種、3カ月の順）")
    print(f"{'順位':>4} {'業種':<40} {'銘柄数':>4} {'1週':>7} {'1カ月':>7} {'3カ月':>7}")
    for k, ind in enumerate(sorted(inds, key=lambda x: -inds[x][63])[:a.top], 1):
        r = inds[ind]
        print(f"{k:>4} {ind:<40} {r['n']:>4} {r[5] * 100:>6.1f}% {r[21] * 100:>6.1f}% {r[63] * 100:>6.1f}%")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch")
    f.add_argument("--cache", default=DEFAULT_CACHE)
    f.add_argument("--min-cap", type=float, default=1e9)
    h = sub.add_parser("heatmap")
    h.add_argument("--cache", default=DEFAULT_CACHE)
    h.add_argument("--asof")
    h.add_argument("--top", type=int, default=15)
    a = ap.parse_args()
    (cmd_fetch if a.cmd == "fetch" else cmd_heatmap)(a)


if __name__ == "__main__":
    main()
