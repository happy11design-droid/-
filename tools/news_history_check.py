#!/usr/bin/env python3
"""ニュースの見出しで過去の下げを見分けられたかを数える（2026-11-03 ユーザーの指示）。SOXが60日の高値から−20%になった局面ごとに、高値の6週前から−20%の日の3週後まで、
週ごとのGoogleニュースの見出しの数（全体・信用の言葉・急落の言葉）を数え、平常時の8週と比べる。使い方: python3 tools/news_history_check.py 出力.json（約15分）"""
import sys, json, os, time, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import news_headlines as nh
L = os.path.expanduser("~/.cache/stock_backtest/long/analog/^SOX.json")
r = json.load(open(L)); D = [x[0] for x in r]; C = [x[1] for x in r]
trig = ["2018-12-24", "2020-03-09", "2022-03-07", "2024-08-02", "2025-03-11", "2026-07-17", "2026-10-30"]
eps = []
for t in trig:
    k = D.index(t) if t in D else next(i for i, x in enumerate(D) if x >= t)
    pk = max(range(k - 59, k + 1), key=lambda j: C[j])
    eps.append((D[pk], D[k]))
ctrl = ["2017-05-15", "2017-08-14", "2019-03-11", "2019-11-11", "2021-04-12", "2021-08-16", "2023-05-15", "2023-11-13"]
EN = "hl=en-US&gl=US&ceid=US:en"
Q = {"base": "chip stocks OR semiconductor stocks",
     "credit": "(chip OR semiconductor OR AI) stocks (credit OR CDS OR default OR debt OR bonds)",
     "shock": "(chip OR semiconductor OR AI) stocks (selloff OR plunge OR rout OR crash OR shock OR bubble)"}
def week(mon):
    s = dt.date.fromisoformat(mon); s -= dt.timedelta(days=s.weekday()); e = s + dt.timedelta(days=6)
    out = {}
    for k, q in Q.items():
        for _ in range(3):
            x = nh.google(q, EN, s, e, 300)
            if x is not None:
                break
            time.sleep(3)
        out[k] = None if x is None else len(x)
        time.sleep(0.6)
    return s.isoformat(), out
res = {"episodes": [], "control": []}
for pk, tg in eps:
    p = dt.date.fromisoformat(pk); t = dt.date.fromisoformat(tg)
    wk = []
    m = p - dt.timedelta(weeks=6)
    while m <= t + dt.timedelta(weeks=3):
        s, o = week(m.isoformat())
        ph = "前" if dt.date.fromisoformat(s) + dt.timedelta(days=6) < p else ("下げの途中" if dt.date.fromisoformat(s) <= t else "下げた後")
        wk.append({"week": s, "phase": ph, **o})
        m += dt.timedelta(weeks=1)
    res["episodes"].append({"peak": pk, "trigger": tg, "weeks": wk})
    print("episode", pk, tg, len(wk), flush=True)
    json.dump(res, open(sys.argv[1], "w"), ensure_ascii=False)
for c in ctrl:
    s, o = week(c)
    res["control"].append({"week": s, **o})
json.dump(res, open(sys.argv[1], "w"), ensure_ascii=False)
print("done", flush=True)
