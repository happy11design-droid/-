#!/usr/bin/env python3
"""Fable 5.2 の大胆な策（2026-11-13、`新分析ツール/Fableの提案_2026-11-13.md` 8節）を確かめるための長い日足

キャッシュの決まり（CLAUDE.md「バックテストのデータ」）どおり、`~/.cache/stock_backtest/long/index/<記号>_full.json` に
[日付, 始値, 高値, 安値, 終値, 調整後終値] で置く。ファイルがあれば取り直さない（--refresh で取り直す）。

使い方:
  python3 tools/fable_data.py fetch [--refresh]
"""
import datetime as dt
import json
import os
import subprocess
import sys
import time
import urllib.parse

L = os.path.expanduser("~/.cache/stock_backtest/long/index/")
UA = "Mozilla/5.0"

# 指数・ETF・金利・為替（Yahoo）
SYMS = ["^NDX", "QQQ", "QLD", "TQQQ", "SOXL", "^SOX", "SOXX", "GLD", "TLT", "XLE", "BIL", "^IRX", "JPY=X", "^VXN",
        "^VIX", "SPY", "^GSPC", "^N225", "1321.T"]


def path(sym):
    return os.path.join(L, sym.replace("/", "_") + "_full.json")


def fetch(sym, refresh=False):
    p = path(sym)
    if os.path.exists(p) and not refresh:
        return True
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(sym)}?interval=1d&period1=0"
           f"&period2={int(time.time()) + 86400}&events=div%2Csplit")
    for k in range(4):
        r = subprocess.run(["curl", "-sS", "--compressed", "--max-time", "60", "-A", UA, url], capture_output=True)
        try:
            res = json.loads(r.stdout.decode("utf-8", "replace"))["chart"]["result"][0]
            q = res["indicators"]["quote"][0]
            adj = (res["indicators"].get("adjclose") or [{}])[0].get("adjclose") or q["close"]
            off = res["meta"].get("gmtoffset", 0)
            rows = []
            for i, t in enumerate(res["timestamp"]):
                o, h, l, c = q["open"][i], q["high"][i], q["low"][i], q["close"][i]
                if c is None:
                    continue
                o = o if o is not None else c
                h = h if h is not None else c
                l = l if l is not None else c
                rows.append([dt.datetime.utcfromtimestamp(t + off).strftime("%Y-%m-%d"), o, h, l, c, adj[i] if adj[i] is not None else c])
            # 同じ日付が2つあるとき（取引中の行）は後のものを残す
            d = {}
            for x in rows:
                d[x[0]] = x
            rows = [d[k_] for k_ in sorted(d)]
            divs = {dt.datetime.utcfromtimestamp(int(t) + off).strftime("%Y-%m-%d"): v["amount"]
                    for t, v in (res.get("events", {}).get("dividends") or {}).items()}
            os.makedirs(L, exist_ok=True)
            json.dump(rows, open(p, "w"))
            if divs:
                json.dump(divs, open(p.replace("_full.json", "_div.json"), "w"))
            print(sym, len(rows), rows[0][0], rows[-1][0], file=sys.stderr)
            return True
        except Exception as e:  # noqa: BLE001
            print("retry", sym, e, file=sys.stderr)
            time.sleep(2 ** k)
    return False


def load(sym):
    """{日付: (始値, 高値, 安値, 終値, 調整後終値)}。始値〜終値は調整後終値÷終値の比率を掛けた値（配当・分割込み）"""
    rows = json.load(open(path(sym)))
    out = {}
    for d, o, h, l, c, a in rows:
        f = a / c if c else 1.0
        out[d] = (o * f, h * f, l * f, c * f, a)
    return out


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "fetch":
        ref = "--refresh" in sys.argv
        bad = [s for s in SYMS if not fetch(s, ref)]
        print("取れなかった:", bad or "なし")
