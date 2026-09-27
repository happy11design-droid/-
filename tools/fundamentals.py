#!/usr/bin/env python3
"""四半期のEPS・売上・純利益（Yahoo Finance の fundamentals-timeseries。認証なしで直近5四半期）

使い方:
  tools/fundamentals.py <ティッカー>        … 著者に渡す形の文章を表示する

ミネルヴィニの本が銘柄選定に求める決算の中身（四半期EPS増益率 20〜25%以上 p.68、売上の連続増加 p.70、利益率の改善 p.84）を
判定する材料として、数値の事実だけを渡す（判定は著者）。Beat/Miss とアナリスト予想の修正は、ニュース調査のサブエージェントが調べる。
過去の日付での再現（--asof）では、その時点で発表済みだったか分からないため渡さない。
"""
import datetime as dt
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backtest_lib import curl

URL = ("https://query2.finance.yahoo.com/ws/fundamentals-timeseries/v1/finance/timeseries/{sym}"
       "?type=quarterlyDilutedEPS,quarterlyTotalRevenue,quarterlyNetIncome&period1=1577836800&period2={now}")


def quarterly(sym):
    """[(四半期末, EPS, 売上, 純利益)]（古い順）。取れなければ []"""
    try:
        j = json.loads(curl(URL.format(sym=sym.replace(".", "-"), now=int(time.time()))))
        rows = {}
        for r in j["timeseries"]["result"]:
            t = r["meta"]["type"][0]
            for x in r.get(t) or []:
                if x:
                    rows.setdefault(x["asOfDate"], {})[t] = x["reportedValue"]["raw"]
        return [(d, v.get("quarterlyDilutedEPS"), v.get("quarterlyTotalRevenue"), v.get("quarterlyNetIncome")) for d, v in sorted(rows.items())]
    except Exception:
        return []


def text(sym):
    q = quarterly(sym)
    if not q:
        return "【決算の中身（四半期）】取得できず"
    pc = lambda a, b: f"{(a / b - 1) * 100:+.0f}%" if a is not None and b not in (None, 0) and b > 0 else "—"
    L = ["【決算の中身（四半期、Yahoo Finance。発表済みの直近5四半期）】",
         "| 四半期末 | 希薄化EPS | 前の四半期比 | 売上 | 前の四半期比 | 純利益率 |", "|---|---|---|---|---|---|"]
    for k, (d, e, r, n) in enumerate(q):
        pe = q[k - 1][1] if k else None
        pr = q[k - 1][2] if k else None
        L.append(f"| {d} | {'—' if e is None else f'{e:.2f}'} | {pc(e, pe) if k else '—'} | "
                 f"{'—' if r is None else f'{r / 1e8:,.0f}億ドル'} | "
                 f"{pc(r, pr) if k else '—'} | {'—' if not (r and n is not None) else f'{n / r * 100:.1f}%'} |")
    if len(q) >= 5:
        (d0, e0, r0, _), (d4, e4, r4, _) = q[-5], q[-1]
        L.append(f"- 直近の四半期（{d4}）の前年同期（{d0}）比: EPS {pc(e4, e0)}、売上 {pc(r4, r0)}")
    return "\n".join(L)


if __name__ == "__main__":
    print(text(sys.argv[1].upper()))
