#!/usr/bin/env python3
"""Yahooの日足が途中で切れて返ってくるときの予備（2026-11-20 ユーザーの指示「全て実行して」の (a)）

2026-11-19、SNDK の 1→8 の株式分割（11/20 の寄り付きから）の直前に、Yahoo の日足（interval=1d）が直近3日分しか返らなくなった。
毎朝のツールは SNDK（保有中）を「取得不可」とし、損切りの確認と著者への質問から外れ、週次レビューの実際の成績からも SNDK の損が抜けた
（−67% が −26.6% と出た）。同じ日でも1時間足（interval=1h、Yahoo の上限は直近730日）は全期間返ってきたので、
日足が上場日から見て明らかに足りないときは、1時間足から日足を作って代わりに使う。

  looks_truncated(res, years) : chart API の結果（日足）が、上場日と期間から見て明らかに足りないか
  hourly_daily(symbol, fetch) : 1時間足（通常の取引時間）から作った日足 [(YYYY-MM-DD, 始値, 高値, 安値, 終値, 出来高)]。取れなければ []

1時間足の日足は、寄り付き＝最初の1時間足の始値、引け＝最後の1時間足の終値（公式の終値と少しずれることがある）。配当の調整はしない。
"""
import datetime as dt
import json
import time

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"


def looks_truncated(res, years):
    """日足の本数が、上場日（firstTradeDate）か期間の始まりの遅い方から今日までの取引日の見込みの8割に満たなければ True"""
    try:
        n = len(res.get("timestamp") or [])
        first = res["meta"].get("firstTradeDate")
    except (AttributeError, KeyError, TypeError):
        return False
    now = time.time()
    start = now - years * 365.25 * 86400
    if first and first > start:
        start = first
    expected = (now - start) / 86400 * 5 / 7 * 0.96   # 平日の数から祝日の分を引いた目安
    return expected >= 20 and n < 0.8 * expected


def hourly_daily(symbol, fetch):
    """fetch(url) -> 応答の文字列。1時間足（直近2年）から日足を作る"""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1h&range=2y"
    try:
        res = json.loads(fetch(url))["chart"]["result"][0]
        q, off = res["indicators"]["quote"][0], res["meta"].get("gmtoffset", 0)
    except Exception:
        return []
    days = {}
    for i, t in enumerate(res.get("timestamp") or []):
        o, h, l, c, v = q["open"][i], q["high"][i], q["low"][i], q["close"][i], q["volume"][i]
        if None in (o, h, l, c):
            continue
        k = dt.datetime.fromtimestamp(t + off, dt.timezone.utc).strftime("%Y-%m-%d")
        x = days.get(k)
        if x is None:
            days[k] = [o, h, l, c, v or 0]
        else:
            x[1], x[2], x[3], x[4] = max(x[1], h), min(x[2], l), c, x[4] + (v or 0)
    return [(k, *days[k]) for k in sorted(days)]
