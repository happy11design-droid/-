#!/usr/bin/env python3
"""過去の決算発表日を Nasdaq の決算カレンダー（1日ごと）から取って、キャッシュに保存する

使い方:
  tools/fetch_earnings_history.py [--from 2015-01-01] [--to 今日]

保存先: <キャッシュ>/earnings.json  {ティッカー: [[日付, 時刻], ...]}
時刻: "time-pre-market"（寄り付き前）／"time-after-hours"（引け後）／"time-not-supplied"（不明）
取った日は <キャッシュ>/earnings_days.json に記録し、2回目以降は取っていない日だけを取る。
"""
import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backtest_lib import DEFAULT_CACHE

UA = "Mozilla/5.0"


def one(day):
    for _ in range(3):
        r = subprocess.run(["curl", "-sS", "--compressed", "--max-time", "30", "-A", UA, "-H", "Accept: application/json",
                            f"https://api.nasdaq.com/api/calendar/earnings?date={day}"], capture_output=True)
        try:
            js = json.loads(r.stdout.decode("utf-8", "replace"))
            rows = ((js.get("data") or {}).get("rows")) or []
            return day, [(x.get("symbol"), x.get("time")) for x in rows if x.get("symbol")]
        except ValueError:
            continue
    return day, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="lo", default="2015-01-01")
    ap.add_argument("--to", dest="hi", default=dt.date.today().isoformat())
    ap.add_argument("--cache", default=DEFAULT_CACHE)
    a = ap.parse_args()
    pe, pd_ = os.path.join(a.cache, "earnings.json"), os.path.join(a.cache, "earnings_days.json")
    earn = json.load(open(pe)) if os.path.exists(pe) else {}
    done = set(json.load(open(pd_))) if os.path.exists(pd_) else set()
    d, days = dt.date.fromisoformat(a.lo), []
    while d <= dt.date.fromisoformat(a.hi):
        if d.weekday() < 5 and d.isoformat() not in done:
            days.append(d.isoformat())
        d += dt.timedelta(days=1)
    print(f"取る日: {len(days)}", file=sys.stderr)
    n = 0
    with ThreadPoolExecutor(6) as ex:
        for day, rows in ex.map(one, days):
            n += 1
            if rows is None:
                continue
            for sym, tm in rows:
                earn.setdefault(sym.replace("/", "-").replace(".", "-"), []).append([day, tm])
            done.add(day)
            if n % 200 == 0:
                print(n, day, file=sys.stderr)
                json.dump(earn, open(pe, "w"))
                json.dump(sorted(done), open(pd_, "w"))
    for k in earn:
        earn[k] = sorted({tuple(x) for x in earn[k]})
    json.dump(earn, open(pe, "w"))
    json.dump(sorted(done), open(pd_, "w"))
    print(f"保存: {pe}（{len(earn)}銘柄、{len(done)}日）", file=sys.stderr)


if __name__ == "__main__":
    main()
