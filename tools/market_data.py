#!/usr/bin/env python3
"""価格・テクニカル指標・チャート画像の生成（`チャート分析.txt` 手順1・手順2-1・手順3 用）

使い方:
  tools/market_data.py macro  <出力ファイル>
      株価指数・為替・金利（逆イールド計算込み）と CNN Fear & Greed Index を取得する。
  tools/market_data.py ticker <ティッカー> <出力ディレクトリ> [--asof YYYY-MM-DD]
      --asof を付けると、その日の終値時点で見えていたチャートとデータを再現する（過去の判定の検証用。ファイル名に日付が付く）。
      日足2年分を取得し、<出力ディレクトリ>/<ティッカー>_chart.png（チャート画像）と
      <出力ディレクトリ>/<ティッカー>_data.txt（指標値・直近日足・大きな値動き・銘柄ページの数値）を書き出す。

どちらも書き出した内容を標準出力にも出す。取得できなかった項目は「取得不可」と出力し、推測で埋めない。
指標の計算式は moomoo の表示値と小数第3位まで一致することを確認済み（SNDK 2026-09-09 の MA/BOLL/MACD/RSI）。
"""
import datetime as dt
import json
import os
import re
import statistics
import subprocess
import sys

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
CHART_BARS = 180          # チャートの表示本数（約9ヶ月）
RECENT_BARS = 10          # テキストで渡す直近日足の本数
MAX_BIG_MOVES = 15


def fetch(url, headers=()):
    cmd = ["curl", "-sS", "--max-time", "20", "-H", f"User-Agent: {UA}"]
    for h in headers:
        cmd += ["-H", h]
    r = subprocess.run(cmd + [url], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def chart_json(symbol, rng, interval="1d"):
    try:
        return json.loads(fetch(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval={interval}&range={rng}"))["chart"]["result"][0]
    except Exception:
        return None


def intraday_bars(symbol):
    """5分足（通常取引時間のみ、Yahooの上限は直近60日）を日付ごとに返す。取得できなければ空の辞書。"""
    r = chart_json(symbol, "60d", "5m")
    days = {}
    if not r or "timestamp" not in r:
        return days
    q, off = r["indicators"]["quote"][0], r["meta"].get("gmtoffset", 0)
    for i, t in enumerate(r["timestamp"]):
        o, h, l, c, v = q["open"][i], q["high"][i], q["low"][i], q["close"][i], q["volume"][i]
        if None in (o, h, l, c) or not v:
            continue
        ts = dt.datetime.utcfromtimestamp(t + off)
        days.setdefault(ts.date(), []).append({"t": ts, "o": o, "h": h, "l": l, "c": c, "v": v})
    return days


def running_vwap(bars5):
    pv = vol = 0.0
    out = []
    for b in bars5:
        pv += (b["h"] + b["l"] + b["c"]) / 3 * b["v"]
        vol += b["v"]
        out.append(pv / vol)
    return out


def fmt(x, d=2):
    return "取得不可" if x is None else f"{x:,.{d}f}"


# ---------------------------------------------------------------- macro
def macro(out_path):
    lines = []
    vals = {}
    for sym, name in [("%5EDJI", "NYダウ"), ("%5EIXIC", "NASDAQ"), ("%5ESOX", "SOX指数"),
                      ("NIY=F", "日経平均先物(CME円建)"), ("1357.T", "日経ダブルインバース(1357)"),
                      ("JPY=X", "ドル円"), ("%5ETNX", "米10年債利回り"), ("2YY=F", "米2年債利回り")]:
        r = chart_json(sym, "1d")
        try:
            m = r["meta"]
            price, prev = m["regularMarketPrice"], m.get("chartPreviousClose") or m.get("previousClose")
            chg = (price - prev) / prev * 100 if prev else None
            vals[name] = price
            lines.append(f"- {name}: {price:,.3f}" + (f"（前日比 {chg:+.2f}%）" if chg is not None else ""))
        except Exception:
            lines.append(f"- {name}: 取得不可")
    if "米10年債利回り" in vals and "米2年債利回り" in vals:
        s = vals["米10年債利回り"] - vals["米2年債利回り"]
        lines.append(f"- 米10年債−米2年債: {s:+.3f}pt → " + ("逆イールド発生中（リセッション警戒）" if s < 0 else "順イールド"))
    else:
        lines.append("- 米10年債−米2年債: 取得不可")

    try:
        fg = json.loads(fetch("https://production.dataviz.cnn.io/index/fearandgreed/graphdata",
                              ["Referer: https://edition.cnn.com/", "Origin: https://edition.cnn.com"]))["fear_and_greed"]
        lines.append(f"- CNN Fear & Greed Index: {fg['score']:.1f}（{fg['rating']}、{fg['timestamp'][:10]}時点）"
                     f"／1週間前 {fg['previous_1_week']:.1f}／1ヶ月前 {fg['previous_1_month']:.1f}")
    except Exception:
        lines.append("- CNN Fear & Greed Index: 取得不可")

    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).strftime("%Y-%m-%d %H:%M JST")
    text = f"（取得: {now}、Yahoo Finance v8 / CNN API）\n" + "\n".join(lines)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text + "\n")
    print(text)


# ---------------------------------------------------------------- ticker
def load_bars(symbol):
    r = chart_json(symbol, "2y")
    if not r:
        sys.exit(f"{symbol}: 日足データを取得できませんでした")
    m, q = r["meta"], r["indicators"]["quote"][0]
    off = m.get("gmtoffset", 0)
    bars = []
    for i, t in enumerate(r["timestamp"]):
        bars.append({"date": dt.datetime.utcfromtimestamp(t + off).date(),
                     "o": q["open"][i], "h": q["high"][i], "l": q["low"][i], "c": q["close"][i], "v": q["volume"][i]})
    # 最終日の足は終値がnullのまま返ることがある（2026-09-23に実際に発生）。meta の当日値で補う。
    last, mt = bars[-1], m.get("regularMarketTime")
    if last["c"] is None and mt and dt.datetime.utcfromtimestamp(mt + off).date() == last["date"]:
        last["c"] = m.get("regularMarketPrice")
        last["h"] = last["h"] or m.get("regularMarketDayHigh")
        last["l"] = last["l"] or m.get("regularMarketDayLow")
        last["v"] = last["v"] or m.get("regularMarketVolume")
    bars = [b for b in bars if None not in (b["o"], b["h"], b["l"], b["c"])]
    for b in bars:
        b["v"] = b["v"] or 0

    period = m.get("currentTradingPeriod", {}).get("regular", {})
    now = dt.datetime.now(dt.timezone.utc).timestamp()
    intraday = bool(period) and period["start"] <= now < period["end"] and bars[-1]["date"] == dt.datetime.utcfromtimestamp(period["start"] + off).date()
    return bars, m, intraday


def sma(a, n):
    return [None if i < n - 1 else sum(a[i - n + 1:i + 1]) / n for i in range(len(a))]


def ema(a, n):
    k, out = 2 / (n + 1), [a[0]]
    for x in a[1:]:
        out.append(x * k + out[-1] * (1 - k))
    return out


def rsi(c, n):
    out, up, dn = [None], None, None
    for i in range(1, len(c)):
        g, l = max(c[i] - c[i - 1], 0), max(c[i - 1] - c[i], 0)
        up = g if up is None else (g + (n - 1) * up) / n
        dn = l if dn is None else (l + (n - 1) * dn) / n
        out.append(100 * up / (up + dn) if up + dn else 50.0)
    return out


def indicators(bars):
    c = [b["c"] for b in bars]
    ind = {"MA20": sma(c, 20), "MA50": sma(c, 50), "MA200": sma(c, 200)}
    for k in ("+3σ", "+2σ", "-2σ", "-3σ"):
        ind[k] = []
    for i in range(len(c)):
        if i < 19:
            for k in ("+3σ", "+2σ", "-2σ", "-3σ"):
                ind[k].append(None)
            continue
        w = c[i - 19:i + 1]
        mid, sd = sum(w) / 20, statistics.pstdev(w)
        ind["+3σ"].append(mid + 3 * sd); ind["+2σ"].append(mid + 2 * sd)
        ind["-2σ"].append(mid - 2 * sd); ind["-3σ"].append(mid - 3 * sd)
    dif = [a - b for a, b in zip(ema(c, 12), ema(c, 26))]
    dea = ema(dif, 9)
    ind.update({"DIF": dif, "DEA": dea, "HIST": [2 * (a - b) for a, b in zip(dif, dea)],
                "RSI6": rsi(c, 6), "RSI12": rsi(c, 12), "RSI24": rsi(c, 24),
                "VMA50": sma([b["v"] for b in bars], 50)})
    return ind


def draw_intraday(days, symbol, path, n_days=2):
    """直近n_days営業日の5分足と日中VWAP（日ごとにリセット）。"""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    keys = sorted(days)[-n_days:]
    B, V, starts = [], [], []
    for k in keys:
        starts.append(len(B))
        B += days[k]
        V += running_vwap(days[k])
    x = list(range(len(B)))
    up, dn = "#e0294a", "#10a37f"
    col = [up if b["c"] >= b["o"] else dn for b in B]

    fig, (p, pv) = plt.subplots(2, 1, figsize=(15, 7), dpi=100, sharex=True,
                                gridspec_kw={"height_ratios": [4, 1.3], "hspace": 0.06})
    fig.subplots_adjust(top=0.9)
    fig.suptitle(f"{symbol}  5-min  |  last {len(keys)} sessions ({keys[0]} to {keys[-1]}, US Eastern time, regular hours)\n"
                 f"VWAP = intraday volume-weighted average price, resets each session. Last session VWAP {V[-1]:,.2f}",
                 fontsize=12, x=0.01, ha="left")
    p.vlines(x, [b["l"] for b in B], [b["h"] for b in B], colors=col, linewidth=1)
    p.bar(x, [abs(b["c"] - b["o"]) or 0.0005 * b["c"] for b in B], bottom=[min(b["o"], b["c"]) for b in B], color=col, width=0.7)
    for j, s0 in enumerate(starts):
        e = starts[j + 1] if j + 1 < len(starts) else len(B)
        p.plot(x[s0:e], V[s0:e], color="#7c3aed", lw=1.6, label="VWAP (intraday)" if j == 0 else None)
        if s0:
            for a in (p, pv):
                a.axvline(s0 - 0.5, color="#9ca3af", lw=0.8, ls="--")
    p.legend(loc="upper left", fontsize=9); p.grid(alpha=0.25)
    pv.bar(x, [b["v"] / 1e3 for b in B], color=col, width=0.7)
    pv.set_ylabel("Vol (K)"); pv.grid(alpha=0.25)
    ticks = [i for i in x if (B[i]["t"].minute == 0 and B[i]["t"].hour in (11, 13)) or i in starts]
    pv.set_xticks(ticks)
    pv.set_xticklabels([B[i]["t"].strftime("%m-%d %H:%M" if i in starts else "%H:%M") for i in ticks])
    pv.set_xlim(-1, len(B))
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def draw_chart(bars, ind, symbol, path, label, vwap):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    s = max(0, len(bars) - CHART_BARS)
    B = bars[s:]
    x = list(range(len(B)))
    sl = lambda k: ind[k][s:]
    up, dn = "#e0294a", "#10a37f"
    col = [up if b["c"] >= b["o"] else dn for b in B]
    L = len(bars) - 1

    fig, ax = plt.subplots(4, 1, figsize=(15, 11), dpi=100, sharex=True,
                           gridspec_kw={"height_ratios": [5, 1.4, 1.4, 1.4], "hspace": 0.06})
    fig.subplots_adjust(top=0.93)
    p, pv, pm, pr = ax
    last = B[-1]
    chg = (last["c"] - bars[-2]["c"]) / bars[-2]["c"] * 100
    fig.suptitle(f"{symbol}  Daily  |  {label}  {last['date']}  Close {last['c']:,.2f} ({chg:+.2f}%)  "
                 f"O {last['o']:,.2f}  H {last['h']:,.2f}  L {last['l']:,.2f}  Vol {last['v']/1e6:,.2f}M\n"
                 f"All indicator values in legends are as of {last['date']} (the last bar).", fontsize=12, x=0.01, ha="left")

    p.vlines(x, [b["l"] for b in B], [b["h"] for b in B], colors=col, linewidth=1)
    p.bar(x, [abs(b["c"] - b["o"]) or 0.001 * b["c"] for b in B], bottom=[min(b["o"], b["c"]) for b in B], color=col, width=0.7)
    for k, cl, ls in [("MA20", "#16a34a", "-"), ("MA50", "#dc2626", "-"), ("MA200", "#2563eb", "-"),
                      ("+2σ", "#f59e0b", "-"), ("-2σ", "#0d9488", "-"), ("+3σ", "#b45309", "--"), ("-3σ", "#115e59", "--")]:
        v = sl(k)
        if any(y is not None for y in v):
            name = k if k.startswith("MA") else f"BOLL(20) {k}"
            p.plot(x, [y if y is not None else float("nan") for y in v], color=cl, lw=1.1, ls=ls, label=f"{name} {fmt(ind[k][L])}")
    vx = [i for i, b in enumerate(B) if b["date"] in vwap]
    if vx:
        p.scatter(vx, [vwap[B[i]["date"]] for i in vx], marker="_", s=60, color="#7c3aed", zorder=5,
                  label=f"Daily VWAP (from 5-min) {fmt(vwap.get(last['date']))}")
    p.legend(loc="upper left", fontsize=9, ncol=4, framealpha=0.85)
    p.grid(alpha=0.25)

    pv.bar(x, [b["v"] / 1e6 for b in B], color=col, width=0.7)
    pv.plot(x, [y / 1e6 if y else float("nan") for y in sl("VMA50")], color="#6b7280", lw=1, label=f"Vol MA50 {fmt((ind['VMA50'][L] or 0)/1e6)}M")
    pv.set_ylabel("Vol (M)"); pv.legend(loc="upper left", fontsize=9); pv.grid(alpha=0.25)

    h = sl("HIST")
    pm.bar(x, h, color=[up if y >= 0 else dn for y in h], width=0.7)
    pm.plot(x, sl("DIF"), color="#f97316", lw=1.1, label=f"DIF {ind['DIF'][L]:,.2f}")
    pm.plot(x, sl("DEA"), color="#0ea5e9", lw=1.1, label=f"DEA {ind['DEA'][L]:,.2f}")
    pm.axhline(0, color="#9ca3af", lw=0.8)
    pm.set_ylabel("MACD(12,26,9)"); pm.legend(loc="upper left", fontsize=9, ncol=2); pm.grid(alpha=0.25)

    for k, cl in [("RSI6", "#f97316"), ("RSI12", "#0ea5e9"), ("RSI24", "#d946ef")]:
        pr.plot(x, sl(k), color=cl, lw=1.1, label=f"{k} {ind[k][L]:.1f}")
    for y in (80, 50, 20):
        pr.axhline(y, color="#9ca3af", lw=0.7, ls="--")
    pr.set_ylim(0, 100); pr.set_ylabel("RSI"); pr.legend(loc="upper left", fontsize=9, ncol=3); pr.grid(alpha=0.25)

    ticks = [i for i in range(len(B)) if i == 0 or B[i]["date"].month != B[i - 1]["date"].month]
    pr.set_xticks(ticks)
    pr.set_xticklabels([B[i]["date"].strftime("%Y-%m") for i in ticks])
    pr.set_xlim(-1, len(B) + 1)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def quote_page(symbol):
    h = fetch(f"https://finance.yahoo.com/quote/{symbol}/").replace('\\"', '"')

    def raw(k):
        m = re.search(r'"' + k + r'":\s*\{"raw":\s*([-0-9.e]+)', h)
        return float(m.group(1)) if m else None

    rec = re.search(r'"recommendationKey":\s*"([a-z_]+)"', h)
    ed = re.search(r'"earningsDate":\[\{"raw":\d+,"fmt":"([0-9-]+)"', h)
    est = re.search(r'"isEarningsDateEstimate":\s*(true|false)', h)
    n = raw("numberOfAnalystOpinions")
    mc = raw("marketCap")
    return [
        f"- 時価総額: {fmt(mc / 1e8, 0) + '億ドル' if mc else '取得不可'}",
        f"- PER（実績/LTM）: {fmt(raw('trailingPE'))}倍",
        f"- 予想PER（FWD PER）: {fmt(raw('forwardPE'))}倍",
        f"- アナリスト: レーティング {rec.group(1) if rec else '取得不可'}（{int(n) if n else '取得不可'}名）"
        f"／目標株価 平均 {fmt(raw('targetMeanPrice'))}・高 {fmt(raw('targetHighPrice'))}・安 {fmt(raw('targetLowPrice'))}",
        f"- 次回決算予定日（Yahoo表示）: {ed.group(1) if ed else '取得不可'}"
        + ("（Yahoo上は推定値。公式発表日はWebSearchで要確認）" if est and est.group(1) == "true" else ""),
    ]


def ticker(symbol, outdir, asof=None):
    """asof（datetime.date）を指定すると、その日の終値時点で見えていたチャートとデータを再現する（過去の判定の検証用）。"""
    os.makedirs(outdir, exist_ok=True)
    bars, meta, intraday = load_bars(symbol)
    days5 = intraday_bars(symbol)
    if asof:
        bars = [b for b in bars if b["date"] <= asof]
        days5 = {d: v for d, v in days5.items() if d <= asof}
        intraday = False
        if not bars or bars[-1]["date"] != asof:
            sys.exit(f"{symbol}: {asof} は取引日ではないか、データがありません")
    ind = indicators(bars)
    L = len(bars) - 1
    last, prev = bars[L], bars[L - 1]
    label = "INTRADAY (provisional)" if intraday else "Close"
    vwap = {d: running_vwap(b)[-1] for d, b in days5.items()}
    name = f"{symbol}_{asof}" if asof else symbol
    png = os.path.join(outdir, f"{name}_chart.png")
    draw_chart(bars, ind, symbol, png, label, vwap)
    png5 = os.path.join(outdir, f"{name}_intraday.png")
    if days5:
        draw_intraday(days5, symbol, png5)

    pct = lambda a, b: (a - b) / b * 100
    basis = "取引時間中の暫定値" if intraday else "終値"
    start = bars[max(0, len(bars) - CHART_BARS)]["date"]
    vma = ind["VMA50"][L]
    out = [f"【チャート画像・テクニカル指標】（{last['date']} {basis}時点。チャート画像は同じ日足データから生成、表示期間 {start}〜{last['date']}）"
           + ("\n※過去時点の再現: この日の終値時点で見えていたデータのみ。これより後の値動きは含まない" if asof else "")]
    out.append(f"- 現在値: {last['c']:,.2f}（{last['date']} {basis}、前日比 {last['c'] - prev['c']:+,.2f}／{pct(last['c'], prev['c']):+.2f}%）"
               f"／始値 {last['o']:,.2f}／高値 {last['h']:,.2f}／安値 {last['l']:,.2f}／出来高 {last['v'] / 1e4:,.1f}万株"
               + (f"（50日平均の{last['v'] / vma:.2f}倍）" if vma else ""))
    ma = "／".join(f"{k} {fmt(ind[k][L])}" + (f"（終値の乖離率 {pct(last['c'], ind[k][L]):+.1f}%）" if ind[k][L] else "") for k in ("MA20", "MA50", "MA200"))
    out.append(f"- 移動平均（単純）: {ma}")
    out.append("- ボリンジャーバンド(20日): " + "／".join(f"{k} {fmt(ind[k][L])}" for k in ("+3σ", "+2σ", "-2σ", "-3σ")))
    out.append(f"- MACD(12,26,9): DIF {ind['DIF'][L]:,.2f}／DEA {ind['DEA'][L]:,.2f}／ヒストグラム {ind['HIST'][L]:,.2f}"
               f"（前日 DIF {ind['DIF'][L - 1]:,.2f}／DEA {ind['DEA'][L - 1]:,.2f}）")
    out.append(f"- RSI: RSI(6) {ind['RSI6'][L]:.1f}／RSI(12) {ind['RSI12'][L]:.1f}／RSI(24) {ind['RSI24'][L]:.1f}")
    if last["date"] in vwap:
        v = vwap[last["date"]]
        out.append(f"- VWAP（{last['date']}の日中VWAP。通常取引時間の5分足から算出、日ごとにリセット）: {v:,.2f}"
                   f"（終値のVWAP乖離率 {pct(last['c'], v):+.2f}%）。当日の値動きは5分足チャート画像を参照")
    else:
        out.append("- VWAP（日中VWAP）: 取得不可")
    yr = bars[-252:]
    hi, lo = max(yr, key=lambda b: b["h"]), min(yr, key=lambda b: b["l"])
    out.append(f"- 52週高値 {hi['h']:,.2f}（{hi['date']}）／52週安値 {lo['l']:,.2f}（{lo['date']}）")

    out.append(f"\n【直近{RECENT_BARS}営業日の日足】（日付｜始値｜高値｜安値｜終値｜前日比｜出来高｜陽線/陰線｜日中VWAP）")
    for i in range(len(bars) - RECENT_BARS, len(bars)):
        b = bars[i]
        out.append(f"- {b['date']}｜{b['o']:,.2f}｜{b['h']:,.2f}｜{b['l']:,.2f}｜{b['c']:,.2f}｜{pct(b['c'], bars[i - 1]['c']):+.2f}%｜{b['v'] / 1e4:,.1f}万"
                   f"｜{'陽線' if b['c'] >= b['o'] else '陰線'}｜{fmt(vwap.get(b['date']))}")

    # チャート表示期間内の大きな値動き（手順3(a)の調査対象日）。閾値は銘柄のボラティリティに合わせる。
    s = max(1, len(bars) - CHART_BARS)
    rets = [pct(bars[i]["c"], bars[i - 1]["c"]) for i in range(s, len(bars))]
    th = max(5.0, 2 * statistics.pstdev(rets))
    moves = []
    for i in range(s, len(bars)):
        r = pct(bars[i]["c"], bars[i - 1]["c"])
        vr = bars[i]["v"] / ind["VMA50"][i] if ind["VMA50"][i] else 0
        if abs(r) >= th or vr >= 2.0:
            moves.append((i, r, vr))
    if len(moves) > MAX_BIG_MOVES:
        moves = sorted(sorted(moves, key=lambda m: -abs(m[1]))[:MAX_BIG_MOVES])
    out.append(f"\n【チャート表示期間内の大きな値動き】（|前日比| {th:.1f}%以上、または出来高が50日平均の2倍以上。{len(moves)}件）")
    for i, r, vr in moves:
        out.append(f"- {bars[i]['date']}: 前日比 {r:+.2f}%、終値 {bars[i]['c']:,.2f}、出来高 50日平均の{vr:.1f}倍")

    if not asof:  # 銘柄ページの値（時価総額・PER・目標株価）は現在値しか取れないため、過去時点の再現では出さない
        now = dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).strftime("%Y-%m-%d %H:%M JST")
        out.append(f"\n【Yahoo Finance 銘柄ページ】（取得: {now}）")
        out += quote_page(symbol)

    text = "\n".join(out)
    with open(os.path.join(outdir, f"{name}_data.txt"), "w", encoding="utf-8") as f:
        f.write(text + "\n")
    print(f"チャート画像: {png}")
    print(f"5分足チャート画像: {png5 if days5 else '取得不可（5分足データなし）'}\n")
    print(text)


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "macro":
        macro(sys.argv[2])
    elif len(sys.argv) == 4 and sys.argv[1] == "ticker":
        ticker(sys.argv[2].upper(), sys.argv[3])
    elif len(sys.argv) == 6 and sys.argv[1] == "ticker" and sys.argv[4] == "--asof":
        ticker(sys.argv[2].upper(), sys.argv[3], dt.date.fromisoformat(sys.argv[5]))
    else:
        sys.exit(__doc__)
