#!/usr/bin/env python3
"""監視銘柄の入れ替え案（毎週土曜の週次レビューで使う。`新分析ツール/テーマ監視_手順書.md` 2-3）

使い方:
  tools/watchlist_review.py <出力.md> [--add 15]

S&P500とNASDAQ100の今の構成銘柄（ETFは含めない）から、次を数値で選んで表にする（入れ替えるかどうかはユーザーが決める）。
  追加の候補: 監視銘柄に入っていない銘柄のうち、RSランキング≧90、株価の30週線の局面が「上昇」、業種（Yahoo）の3カ月の強さが上位20%、
             流動性（株価5ドル以上・50日平均出来高25万株以上）。RSの高い順に最大 --add 件。
             業種が今の監視銘柄に1つもない場合は「テーマの外（新しいテーマの兆し）」と書く。
  外す候補: 監視銘柄のうち、株価の30週線の局面が「下落」（線より下かつ線が下向き、ワインスタインのステージ4の近似）で、RSランキング<50。
  注意: 監視銘柄のうち、局面が「下落」だがRS≧50、またはRS<20（局面は下落ではない）。
RSランキングは、S&P500・NASDAQ100・監視銘柄をあわせた中での百分位（0.4×3カ月＋0.2×6・9・12カ月の騰落率）。
数値と事実だけで、売買の判断はしない。
"""
import argparse
import bisect
import csv
import datetime as dt
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_theme as bth
from backtest_lib import DEFAULT_CACHE, MEMBERS_URL, curl, market_regime, sma
from theme_scan import fetch_daily, pct
from theme_universe import yahoo_profile

NDX_URL = "https://api.nasdaq.com/api/quote/list-type/nasdaq100"


def ndx_members():
    try:
        return [r["symbol"].replace("/", ".") for r in json.loads(curl(NDX_URL))["data"]["data"]["rows"]]
    except Exception:
        return []


def industries(syms, cache=DEFAULT_CACHE):
    u = {}
    for f in ("universe.json", "industry_extra.json"):
        p = os.path.join(cache, f)
        if os.path.exists(p):
            u.update(json.load(open(p)))
    miss = [s for s in syms if not (u.get(s) or {}).get("industry")]
    with ThreadPoolExecutor(8) as ex:
        for s, r in zip(miss, ex.map(yahoo_profile, miss)):
            if r:
                u[s] = r
    return {s: (u.get(s) or {}).get("industry") or "不明" for s in syms}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--add", type=int, default=15)
    a = ap.parse_args()
    wl = bth.load_watchlist()
    txt = curl(MEMBERS_URL)
    sp = [r["ticker"] for r in csv.DictReader(txt.splitlines()) if not r["end_date"]] if txt.startswith("ticker,") else []
    ndx = ndx_members()
    syms = sorted(set(sp) | set(ndx) | set(wl))
    with ThreadPoolExecutor(8) as ex:
        data = {s: d for s, d in zip(syms, ex.map(fetch_daily, syms)) if d and len(d["c"]) > 253}
    day = max(d["date"][-1] for d in data.values())
    data = {s: d for s, d in data.items() if d["date"][-1] == day}
    raw = lambda c: 0.4 * (c[-1] / c[-64] - 1) + 0.2 * (c[-1] / c[-127] - 1) + 0.2 * (c[-1] / c[-190] - 1) + 0.2 * (c[-1] / c[-253] - 1)
    pool = sorted(raw(d["c"]) for d in data.values())
    info = {}
    for s, d in data.items():
        v50 = sma(d["v"], 50)[-1]
        info[s] = {"rs": 99 * bisect.bisect_left(pool, raw(d["c"])) / (len(pool) - 1),
                   "stage": market_regime(d).get(day, "判定不能"), "r3": d["c"][-1] / d["c"][-64] - 1,
                   "liquid": d["c"][-1] >= 5 and (v50 or 0) >= 250_000, "close": d["c"][-1]}
    ind = industries(list(data))
    by_ind = {}
    for s in data:
        if s not in wl:
            by_ind.setdefault(ind[s], []).append(info[s]["r3"])
    med = {k: sorted(v)[len(v) // 2] for k, v in by_ind.items() if len(v) >= 3}
    order = sorted(med, key=lambda k: -med[k])
    top = set(order[:max(1, len(order) // 5)])
    theme_inds = {ind[s] for s in wl if s in ind}

    adds = [s for s in data if s not in wl and info[s]["liquid"] and info[s]["rs"] >= 90 and info[s]["stage"] == "上昇" and ind[s] in top]
    adds = sorted(adds, key=lambda s: -info[s]["rs"])[:a.add]
    drops = [s for s in wl if s in info and info[s]["stage"] == "下落" and info[s]["rs"] < 50]
    warns = [s for s in wl if s in info and s not in drops and (info[s]["stage"] == "下落" or info[s]["rs"] < 20)]

    L = [f"## 監視銘柄の入れ替え案（{day}の引け時点）\n",
         f"- 対象: S&P500（{len(sp)}）とNASDAQ100（{len(ndx)}）の今の構成銘柄。監視銘柄は {len(wl)}（上限は100程度）。入れ替えるかどうかはユーザーが決める。",
         "- 追加の候補: 監視外で、RS≧90、株価の30週線の局面が上昇、業種の3カ月の強さが上位20%、流動性あり。外す候補: 監視銘柄で、局面が下落（ワインスタインのステージ4の近似）かつRS<50。",
         "- 数値と事実だけで、売買の判断ではない。\n",
         f"### 追加の候補（{len(adds)}銘柄、RSの高い順）\n"]
    if adds:
        L += ["| 銘柄 | 業種 | 業種の3カ月の順位 | テーマ | RS | 株価の局面 | 3カ月 | 終値 |", "|---|---|---|---|---|---|---|---|"]
        for s in adds:
            x = info[s]
            L.append(f"| {s} | {ind[s]} | {order.index(ind[s]) + 1}位／{len(order)} | {'今のテーマ内' if ind[s] in theme_inds else '**テーマの外（新しいテーマの兆し）**'} | "
                     f"{x['rs']:.0f} | {x['stage']} | {pct(x['r3'])} | {x['close']:.2f} |")
    else:
        L.append("該当なし")
    L.append(f"\n### 外す候補（{len(drops)}銘柄）\n")
    if drops:
        L += ["| 銘柄 | グループ | RS | 株価の局面 | 3カ月 |", "|---|---|---|---|---|"]
        for s in sorted(drops, key=lambda s: info[s]["rs"]):
            L.append(f"| {s} | {wl[s]} | {info[s]['rs']:.0f} | {info[s]['stage']} | {pct(info[s]['r3'])} |")
    else:
        L.append("該当なし")
    L.append(f"\n### 注意（外す候補ではないが弱い、{len(warns)}銘柄）\n")
    L.append("、".join(f"{s}（RS {info[s]['rs']:.0f}・{info[s]['stage']}）" for s in sorted(warns, key=lambda s: info[s]['rs'])) or "なし")
    L.append(f"\n### 業種の3カ月の強さ（上位10、監視外の銘柄の中央値）\n")
    for k in order[:10]:
        L.append(f"- {order.index(k) + 1}. {k}（{pct(med[k])}）" + ("" if k in theme_inds else " ← 今の監視銘柄にない業種"))
    text = "\n".join(L) + "\n"
    open(a.out, "w", encoding="utf-8").write(text)
    print(text)


if __name__ == "__main__":
    main()
