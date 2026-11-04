#!/usr/bin/env python3
"""テーマの7グループごとの悪いニュースの見出しの数を週ごとに数える（2026-11-04 ユーザーの指示）。使い方: python3 tools/group_news_weekly.py 出力.json（約10分）"""
import sys, json, datetime as dt, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import news_headlines as nh
gs = nh.theme_groups()
out = json.load(open(sys.argv[1])) if os.path.exists(sys.argv[1]) else {}
m = dt.date(2026, 6, 22)
while m <= dt.date(2026, 11, 2):
    k = m.isoformat()
    if k not in out:
        r = nh.group_bad_news(m, m + dt.timedelta(days=6), gs)
        out[k] = {g: (None if v is None else [(d.isoformat(), s_, t) for d, s_, t in v]) for g, v in r.items()}
        json.dump(out, open(sys.argv[1], "w"), ensure_ascii=False)
        print(k, {g[:6]: (None if v is None else len(v)) for g, v in out[k].items()}, flush=True)
    m += dt.timedelta(days=7)
print("done", flush=True)
