#!/usr/bin/env python3
"""1990年〜の長い日足を Yahoo から取って ~/.cache/stock_backtest/long/stocks/<銘柄>.json に置く（あれば取り直さない）
（2026-11-20 ユーザーの指示「はい。全て検証して」＝長い下げ（2000〜2002年・2008年）の中で今のルールを確かめるため）

対象: 今のS&P500の構成銘柄（members.csv で終わりの日がないもの）＋テーマ監視銘柄（87銘柄）＋ ETF（SPY・QQQ・SMH・SOXX・XLK）。
形式は prices/ と同じ [日付, 始値, 高値, 安値, 終値, 出来高, 調整後終値]。大きさを抑えるため値は有効数字7桁に丸める。
今の会社のティッカーで取るので、上場をやめた会社は入らない（生き残りの偏り）。
使い方: python3 tools/long_stocks.py [--workers 6] [--refresh]   --refresh: 最終日が古いファイルを取り直す
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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_lib as bl

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = os.path.expanduser("~/.cache/stock_backtest/")
OUT = C + "long/stocks/"
ETFS = ["SPY", "QQQ", "SMH", "SOXX", "XLK"]


def watch87():
    md = open(os.path.join(ROOT, "新分析ツール", "テーマ監視銘柄.md"), encoding="utf-8").read()
    return sorted({m.group(1) for m in re.finditer(r"(?m)^\| ([A-Z][A-Z0-9.\-]*) \|", md) if m.group(1) != "ティッカー"})


def symbols():
    cur = {r["ticker"] for r in csv.DictReader(open(C + "members.csv")) if not r["end_date"]}
    return sorted(cur | set(watch87()) | set(ETFS))


def open_day():
    """まだ確定していない日（米国東部時間で今日。ただし17時を過ぎたら明日）。この日以降の行は保存しない"""
    from zoneinfo import ZoneInfo
    now = dt.datetime.now(ZoneInfo("America/New_York"))
    d = now.date() + dt.timedelta(days=1 if now.hour >= 17 else 0)
    return d.isoformat()


def g7(x):
    return float(f"{x:.7g}") if x is not None else None


def fetch(sym, refresh=False):
    p = OUT + sym + ".json"
    if os.path.exists(p) and not refresh:
        return "あり"
    if os.path.exists(p) and refresh:
        last = json.load(open(p))[-1][0]
        if last >= (dt.date.today() - dt.timedelta(days=4)).isoformat():
            return "あり"
    p1, p2 = int(dt.datetime(1990, 1, 1).timestamp()), int(time.time())
    ys = sym.replace(".", "-")
    for attempt in range(4):
        txt = bl.curl(f"https://query1.finance.yahoo.com/v8/finance/chart/{ys}?interval=1d&period1={p1}&period2={p2}")
        try:
            res = json.loads(txt)["chart"]["result"][0]
            q = res["indicators"]["quote"][0]
            adj = res["indicators"].get("adjclose", [{}])[0].get("adjclose") or q["close"]
            off = res["meta"].get("gmtoffset", 0)
            rows = []
            for i, t in enumerate(res["timestamp"]):
                o, h, l, c, v, ac = q["open"][i], q["high"][i], q["low"][i], q["close"][i], q["volume"][i], adj[i]
                if None in (o, h, l, c) or c <= 0:
                    continue
                rows.append([dt.datetime.utcfromtimestamp(t + off).strftime("%Y-%m-%d"), g7(o), g7(h), g7(l), g7(c), int(v or 0), g7(ac or c)])
            rows = [r for r in rows if r[0] < open_day()]   # 取引中・引け前の今日の行は入れない（2026-11-20: 取引中の値が入っていた）
            if not rows:
                return "なし"
            json.dump(rows, open(p, "w"), separators=(",", ":"))
            return "取った"
        except Exception:
            if '"Not Found"' in txt or "No data found" in txt:
                return "なし"
            time.sleep(2 ** (attempt + 1))
    return "失敗"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--refresh", action="store_true")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    syms = symbols()
    with ThreadPoolExecutor(a.workers) as ex:
        res = list(ex.map(lambda s: fetch(s, a.refresh), syms))
    cnt = {}
    for r in res:
        cnt[r] = cnt.get(r, 0) + 1
    bad = [s for s, r in zip(syms, res) if r in ("なし", "失敗")]
    print(f"対象 {len(syms)} 銘柄: {cnt}。取れなかった: {' '.join(bad)}")


if __name__ == "__main__":
    main()
