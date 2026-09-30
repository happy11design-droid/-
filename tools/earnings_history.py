#!/usr/bin/env python3
"""米国株の過去の決算発表日とEPSのサプライズ（NasdaqのEarnings Calendar）を日付ごとに取得してキャッシュする

使い方:
  tools/earnings_history.py fetch [--from 2014-01-01] [--cache DIR]   # 平日ごとに1回。取得済みの日は飛ばす（初回は約10分）
  （読み込みは load_earnings(cache) → {ティッカー: [(発表日, 時間帯, サプライズ%), ...]}）

時間帯: "pre"（寄り付き前）/ "after"（引け後）/ "?"（記載なし）。サプライズ%は (実績EPS−予想)/|予想|×100（記載がなければ None）。
"""
import argparse
import datetime as dt
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backtest_lib import DEFAULT_CACHE, UA

import subprocess

URL = "https://api.nasdaq.com/api/calendar/earnings?date={}"


def get(day, path):
    if os.path.exists(path):
        return True
    for attempt in range(4):
        r = subprocess.run(["curl", "-sS", "--compressed", "--max-time", "30", "-A", UA, "-H", "Accept: application/json", URL.format(day)],
                           capture_output=True)
        try:
            data = json.loads(r.stdout.decode("utf-8", errors="replace"))["data"]
            rows = (data or {}).get("rows") or []
            out = [[x.get("symbol"), {"time-pre-market": "pre", "time-after-hours": "after"}.get(x.get("time"), "?"),
                    x.get("surprise")] for x in rows if x.get("symbol")]
            json.dump(out, open(path, "w"))
            return True
        except Exception:
            time.sleep(2 ** attempt)
    return False


def cmd_fetch(a):
    d = os.path.join(a.cache, "earnings")
    os.makedirs(d, exist_ok=True)
    day, end, days = dt.date.fromisoformat(a.start), dt.date.today(), []
    while day <= end:
        if day.weekday() < 5:
            days.append(day.isoformat())
        day += dt.timedelta(days=1)
    with ThreadPoolExecutor(6) as ex:
        ok = list(ex.map(lambda x: get(x, os.path.join(d, x + ".json")), days))
    print(f"{len(days)} 日、取得できなかった日 {ok.count(False)}")


def refresh(cache=DEFAULT_CACHE, back=120, ahead=8):
    """直近 back 日のうち未取得の日を取得し、今日から ahead 日先までの予定（キャッシュしない）を足した load_earnings を返す"""
    import tempfile
    d = os.path.join(cache, "earnings")
    os.makedirs(d, exist_ok=True)
    today = dt.date.today()
    past = [(today - dt.timedelta(days=k)).isoformat() for k in range(back, 0, -1)]
    past = [x for x in past if dt.date.fromisoformat(x).weekday() < 5]
    futs = [(today + dt.timedelta(days=k)).isoformat() for k in range(0, ahead + 1)]
    futs = [x for x in futs if dt.date.fromisoformat(x).weekday() < 5]
    tmp = tempfile.mkdtemp()
    with ThreadPoolExecutor(6) as ex:
        list(ex.map(lambda x: get(x, os.path.join(d, x + ".json")), past))
        list(ex.map(lambda x: get(x, os.path.join(tmp, x + ".json")), futs))
    out = load_earnings(cache)
    for f in sorted(os.listdir(tmp)):
        for sym, tm, sp in json.load(open(os.path.join(tmp, f))):
            lst = out.setdefault(sym.replace("/", ".").replace("-", "."), [])
            if not any(x[0] == f[:10] for x in lst):
                lst.append((f[:10], tm, None))   # 予定（サプライズは未定）
    return out


def load_earnings(cache=DEFAULT_CACHE):
    d = os.path.join(cache, "earnings")
    out = {}
    if not os.path.isdir(d):
        return out
    for f in sorted(os.listdir(d)):
        for sym, tm, sp in json.load(open(os.path.join(d, f))):
            try:
                sp = float(sp)
            except (TypeError, ValueError):
                sp = None
            out.setdefault(sym.replace("/", ".").replace("-", "."), []).append((f[:10], tm, sp))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch")
    f.add_argument("--from", dest="start", default="2014-01-01")
    f.add_argument("--cache", default=DEFAULT_CACHE)
    cmd_fetch(ap.parse_args())
