#!/usr/bin/env python3
"""恩株ツール: 毎朝の合図の通知（`恩株ツール/恩株_手順書.md`）

使い方:
  tools/onkabu_scan.py <出力ファイル.md> [--asof YYYY-MM-DD] [--rule 恩株ツール/採用ルール.json]

やること（数値の計算と、採用ルールに当てはまるかの判定だけ。ルールの外の売買の判断はしない）:
  1. S&P500の今の構成銘柄の日足（3年分）をYahooから取る（1分ほど）。
  2. 採用ルール（`恩株ツール/採用ルール.json`）の合図が、直近の取引日の終値で出た銘柄を一覧にする。
     売上の前年同期比は、株価の条件を満たした銘柄だけSECから取る。
  3. 保有銘柄（`恩株ツール/保有銘柄.md`）について、2倍・損切り・期限・乗り換えの条件に当たったかを書く。
  4. 合図に近い銘柄（株価の条件の8割以上）を参考に並べる。
取得できなかった値は「取得不可」と書き、推測で埋めない。
"""
import argparse
import csv
import datetime as dt
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backtest_lib import MEMBERS_URL, curl, DEFAULT_CACHE
from theme_scan import fetch_daily
import backtest_onkabu as ob
import onkabu_lib as ol

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RULE = os.path.join(ROOT, "恩株ツール", "採用ルール.json")
HOLD = os.path.join(ROOT, "恩株ツール", "保有銘柄.md")


def sec_rev_rows(syms):
    """売上の決算（SEC companyconcept）。取れなければ空"""
    tick = json.loads(ob.sec_get("https://www.sec.gov/files/company_tickers.json") or "{}")
    cik = {v["ticker"].upper(): v["cik_str"] for v in tick.values()}
    out = {}
    for s in syms:
        c = cik.get(s.replace(".", "-").upper())
        rows = []
        if c:
            for tag in ("Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet",
                        "RevenueFromContractWithCustomerIncludingAssessedTax", "SalesRevenueGoodsNet"):
                t = ob.sec_get(f"https://data.sec.gov/api/xbrl/companyconcept/CIK{c:010d}/us-gaap/{tag}.json")
                time.sleep(0.12)
                if t:
                    for u, fs in json.loads(t).get("units", {}).items():
                        if isinstance(fs, list):
                            rows += [(f["filed"], f["start"], f["end"], f["val"]) for f in fs
                                     if f.get("filed") and f.get("start") and f.get("val") is not None]
        out[s] = sorted(set(rows))
    return out


def load_holdings(path=HOLD):
    """| ティッカー | 買った日 | 買値 | 株数 | 状態 | の表。状態は「保有」か「恩株」"""
    rows = []
    if not os.path.exists(path):
        return rows
    for line in open(path, encoding="utf-8"):
        m = re.match(r"^\|\s*([A-Z][A-Z.]*)\s*\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*(保有|恩株)\s*\|", line)
        if m:
            rows.append({"sym": m.group(1), "date": m.group(2), "px": float(m.group(3)), "sh": float(m.group(4)), "state": m.group(5)})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--asof")
    ap.add_argument("--rule", default=RULE)
    a = ap.parse_args()
    rule = json.load(open(a.rule, encoding="utf-8"))
    sig, cfg = rule["合図"], rule["売買"]
    members_csv = curl(MEMBERS_URL)
    if not members_csv.startswith("ticker,"):
        members_csv = open(os.path.join(DEFAULT_CACHE, "members.csv")).read()
    sp = sorted(r["ticker"] for r in csv.DictReader(members_csv.splitlines()) if not r["end_date"])
    hold = load_holdings()
    syms = sorted(set(sp) | {h["sym"] for h in hold} | {"SPY"})
    with ThreadPoolExecutor(8) as ex:
        got = dict(zip(syms, ex.map(fetch_daily, syms)))
    if a.asof:
        got = {s: (None if d is None else {k: v[:sum(1 for x in d["date"] if x <= a.asof)] for k, v in d.items()}) for s, d in got.items()}
    spy = got["SPY"]
    asof = spy["date"][-1]
    sc = np.array(spy["c"])
    ma = ol.sma(sc, 200)
    spy_up = {d: bool(sc[k] > ma[k]) for k, d in enumerate(spy["date"]) if not np.isnan(ma[k])}
    missing = [s for s in sp if not got.get(s)]

    # 株価だけで判定（売上の条件は外して）→ 当てはまった銘柄だけ売上を取って、もう一度判定
    price_only = {**sig, "rev": None}
    feats, pass1, near = {}, [], []
    k, th = sig["mom"]
    for s in sp:
        d = got.get(s)
        if not d or len(d["c"]) < 260 or d["date"][-1] != asof:
            continue
        f = ol.features(d, [], spy_up)
        feats[s] = f
        if ol.signal(f, price_only)[-1]:
            pass1.append(s)
        elif f[k][-1] >= th * 0.8 and f["hi52"][-1] >= 0.85:
            near.append(s)
    rows = sec_rev_rows(sorted(set(pass1) | set(near) | {h["sym"] for h in hold if h["state"] == "保有"}))
    hits = []
    for s in pass1:
        f = ol.features(got[s], rows.get(s, []), spy_up)
        feats[s] = f
        if ol.signal(f, sig)[-1]:
            hits.append(s)

    per = {"r21": "1カ月", "r63": "3カ月", "r126": "6カ月"}[k]
    amt = cfg["資金"] / cfg["枠"]
    out = []
    w = out.append
    w(f"# 恩株ツール 合図の通知（{asof} の終値）\n")
    stop = cfg.get("損切り")
    rot = cfg.get("乗り換え")
    w(f"**採用ルール**: {ol.describe(sig)}")
    w(f"- 買い方: {cfg['買い方']}。{cfg['枠']}銘柄まで（恩株は数えない）。1銘柄 {amt:,.0f}ドル（資金 {cfg['資金']:,.0f}ドル÷{cfg['枠']}）")
    w(f"- 売り方: 終値が買値の2倍で55.7%を売って恩株に。{cfg['期限']}取引日で2倍にならなければ売る。"
      + ("損切りなし。" if stop is None else f"終値が買値の−{stop * 100:.0f}%で損切り。")
      + ("" if rot is None else f"枠が埋まっているときに新しい合図が出たら、値上がり率が一番低い保有株（{rot * 100:+.0f}%未満）を売って乗り換える。"))
    w(f"- 待っている現金の置き場所: {cfg.get('現金', '現金のまま')}\n")
    w(f"## 1. 今日の合図（{len(hits)}銘柄）\n")
    if hits:
        w(f"| ティッカー | 終値 | {per}の騰落率 | 52週高値比 | 売上の前年同期比 | 株数の目安（{amt:,.0f}ドル） | 2倍の価格 | 損切りの価格 |")
        w("|---|---|---|---|---|---|---|---|")
        for s in sorted(hits, key=lambda x: -feats[x][k][-1]):
            f = feats[s]
            c = f["c"][-1]
            rv = f["rev"][-1]
            rv_s = "取得不可" if np.isnan(rv) else f"{rv:+.0%}"
            stop_s = "なし" if stop is None else f"{c * (1 - stop):,.2f}（買値で決まる）"
            w(f"| {s} | {c:,.2f} | {f[k][-1]:+.0%} | {f['hi52'][-1]:.0%} | {rv_s} | {int(amt // c)}株 | {2 * c:,.2f}（買値で決まる） | {stop_s} |")
        w("\n価格は今日の終値を買値とした目安。実際の2倍・損切りの価格は、約定した買値から計算する。")
    else:
        w("合図は出ていない。")
    if [s for s in pass1 if s not in hits]:
        w(f"\n株価の条件は満たしたが売上の条件で外れた銘柄: " + ", ".join(
            f"{s}（売上 {'取得不可' if np.isnan(feats[s]['rev'][-1]) else format(feats[s]['rev'][-1], '+.0%')}）" for s in pass1 if s not in hits))
    w("\n## 2. 保有銘柄\n")
    act = [h for h in hold if h["state"] == "保有"]
    if act:
        w("| ティッカー | 買った日 | 買値 | 終値 | 値上がり率 | 2倍の価格 | 損切りの価格 | 期限（取引日の残り） | 条件 |")
        w("|---|---|---|---|---|---|---|---|---|")
        for h in act:
            d = got.get(h["sym"])
            if not d:
                w(f"| {h['sym']} | {h['date']} | {h['px']:,.2f} | 取得不可 | | | | | |")
                continue
            c = d["c"][-1]
            held = sum(1 for x in d["date"] if x > h["date"])
            left = cfg["期限"] - held
            r = c / h["px"] - 1
            flags = []
            if c >= 2 * h["px"]:
                flags.append(f"**2倍に到達: {h['sh'] * ob.SELL_AT_2X:.1f}株（55.7%）を売って恩株に**")
            if stop is not None and c <= h["px"] * (1 - stop):
                flags.append("**損切りの価格に到達: 全部売る**")
            if left <= 0:
                flags.append("**期限: 全部売る**")
            stop_px = "なし" if stop is None else f"{h['px'] * (1 - stop):,.2f}"
            w(f"| {h['sym']} | {h['date']} | {h['px']:,.2f} | {c:,.2f} | {r:+.1%} | {2 * h['px']:,.2f} | "
              f"{stop_px} | {left}日 | {' '.join(flags) or '―'} |")
        if rot is not None and hits and len(act) >= cfg["枠"]:
            worst = min(act, key=lambda h: (got[h["sym"]]["c"][-1] / h["px"]) if got.get(h["sym"]) else 9)
            wr = got[worst["sym"]]["c"][-1] / worst["px"] - 1 if got.get(worst["sym"]) else None
            if wr is not None and wr < rot:
                w(f"\n**乗り換えの条件に当たる**: 枠が埋まっていて新しい合図がある。値上がり率が一番低い {worst['sym']}（{wr:+.1%}）を売って、合図の銘柄に乗り換える。")
    else:
        w("保有中の銘柄はない（`恩株ツール/保有銘柄.md`）。")
    onk = [h for h in hold if h["state"] == "恩株"]
    if onk:
        w("\n恩株: " + ", ".join(f"{h['sym']}（{h['sh']:g}株）" for h in onk))
    w(f"\n## 3. 合図に近い銘柄（{per}で+{th * 0.8:.0%}以上・52週高値の85%以上。参考）\n")
    if near:
        w(f"| ティッカー | 終値 | {per}の騰落率 | 52週高値比 | 売上の前年同期比 |\n|---|---|---|---|---|")
        for s in sorted(near, key=lambda x: -feats[x][k][-1])[:15]:
            f = ol.features(got[s], rows.get(s, []), spy_up)
            rv = f["rev"][-1]
            w(f"| {s} | {f['c'][-1]:,.2f} | {f[k][-1]:+.0%} | {f['hi52'][-1]:.0%} | {'取得不可' if np.isnan(rv) else f'{rv:+.0%}'} |")
    else:
        w("なし")
    if missing:
        w(f"\n株価を取得できなかった銘柄: {', '.join(missing)}")
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(out) + "\n")
    json.dump({"asof": asof, "hits": hits, "near": near}, open(os.path.splitext(a.out)[0] + ".json", "w"))
    print("\n".join(out))


if __name__ == "__main__":
    main()
