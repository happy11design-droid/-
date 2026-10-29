#!/usr/bin/env python3
"""株式分割（Yahooファイナンスの chart API の events=split）で、記録した値段を今の株価の基準に直す（2026-10-30 ユーザーの指示）

SNDK の 1→8 の分割（2026-11-20 の寄り付きから分割後の値段）で、保有銘柄.md の分割前の買値（1,371.30）と分割後の株価（約170）を
比べると、毎朝のツールが誤って「損切り」と出し、週次レビューの損益も大きくずれる。Yahooの過去の株価は分割に合わせて調整されるので、
記録した買値・売値も「その日より後に起きた分割の倍率」で割って、今の基準にそろえる。

  factor(sym, after)        : after（YYYY-MM-DD）より後に起きた分割の倍率の積（なければ 1.0）
  adjust(sym, price, date)  : date の値段を今の基準に直した値段（price ÷ factor）

使い方（確かめる用）:
  tools/splits.py NVDA AVGO SMCI     # 分割の一覧
"""
import datetime as dt
import json
import subprocess
import sys
import urllib.parse
from zoneinfo import ZoneInfo

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
ET = ZoneInfo("America/New_York")
_CACHE = {}


def splits(sym):
    """[(分割後の最初の取引日 YYYY-MM-DD, 倍率)]。倍率は 1→8 の分割なら 8.0、併合（1株を1/10）なら 0.1。取れなければ None"""
    if sym in _CACHE:
        return _CACHE[sym]
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(sym.replace('.', '-'))}"
           f"?interval=1mo&range=10y&events=split")
    r = subprocess.run(["curl", "-sS", "--max-time", "20", "-A", UA, url], capture_output=True, text=True)
    try:
        res = json.loads(r.stdout)["chart"]["result"][0]
    except Exception:
        _CACHE[sym] = None
        return None
    out = []
    for v in (res.get("events") or {}).get("splits", {}).values():
        try:
            d = dt.datetime.fromtimestamp(v["date"], ET).date().isoformat()
            k = float(v["numerator"]) / float(v["denominator"])
        except (KeyError, ValueError, ZeroDivisionError):
            continue
        if k > 0 and k != 1:
            out.append((d, k))
    _CACHE[sym] = sorted(out)
    return _CACHE[sym]


def factor(sym, after, until=None):
    """after より後（after の翌日〜until）に起きた分割の倍率の積。分割の情報が取れなければ 1.0"""
    f = 1.0
    for d, k in splits(sym) or []:
        if d > after and (until is None or d <= until):
            f *= k
    return f


def adjust(sym, price, date):
    """date の値段を、今の株価の基準（その後の分割で割った値段）に直す"""
    return price / factor(sym, date)


if __name__ == "__main__":
    for s in sys.argv[1:] or ["NVDA"]:
        print(s, splits(s))
