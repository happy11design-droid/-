#!/usr/bin/env python3
"""特殊な下げ（tools/sox_analog.py の条件）の間はSOXから乗り換え、戻す合図（上向きの50日線・20日線・5日線を上回る）でSOXに戻す形を、指数で比べる（2026-11-03 ユーザーの指示）。
乗り換えのたびに0.1%の手数料。データは tools/sox_analog.py が保存したもの（~/.cache/stock_backtest/long/analog/）。使い方: python3 tools/sox_switch_back.py"""
import json, csv, os, sys, bisect, datetime as dt
L = os.path.expanduser("~/.cache/stock_backtest/long/analog")
def ld(sym, adj=True): return {d: (a if adj else c) for d, c, a in json.load(open(os.path.join(L, sym + ".json")))}
def fred(sid):
    out = {}
    for r in csv.reader(open(os.path.join(L, sid + ".csv"))):
        try: out[r[0]] = float(r[1])
        except: pass
    return out
sox, spy = ld("^SOX", False), ld("SPY")
SECT = ["XLE","XLV","XLU","XLP","XLF","XLI","XLB","XLY"]; sect = {s: ld(s) for s in SECT}
cpi, pay = fred("CPIAUCSL"), fred("PAYEMS"); ck, pk = sorted(cpi), sorted(pay)
days = [d for d in sorted(sox) if d in spy]; P = [sox[d] for d in days]; Q = [spy[d] for d in days]
def avail(ym, dd):
    y, m = int(ym[:4]), int(ym[5:7]) + 1
    return f"{y + (m == 13):04d}-{(1 if m == 13 else m):02d}-{dd:02d}"
c_av = [avail(k[:7], 20) for k in ck]; p_av = [avail(k[:7], 10) for k in pk]
def n_(k):
    d = days[k]; i = bisect.bisect_right(c_av, d) - 1; j = bisect.bisect_right(p_av, d) - 1
    y, y3 = cpi[ck[i]] / cpi[ck[i-12]] - 1, cpi[ck[i-3]] / cpi[ck[i-15]] - 1
    return int(P[k-60] / P[k-310] - 1 >= 0.8) + int((pay[pk[j]] - pay[pk[j-3]]) / 3 < 100) + int(y >= 0.035 and y > y3)
ma = lambda k, n: sum(P[k-n+1:k+1]) / n
NN = [n_(k) if k >= 320 else 0 for k in range(len(P))]
def state(x, th=0.15):
    on, st_ = False, [False] * len(P)
    for k in range(320, len(P)):
        if not on:
            if P[k] / max(P[k-59:k+1]) - 1 <= -th and NN[k] >= 2 and (x == 50 or P[k] < ma(k, x)):
                on = True
        elif (P[k] > ma(k, 50) > sum(P[k-59:k-9]) / 50) if x == 50 else (P[k] > ma(k, x)):
            on = False
        st_[k] = on
    return st_
COST = 0.001
def run(st_, dest, start, end="9999"):
    k0 = next(k for k, d in enumerate(days) if d >= start); k1 = max(k for k, d in enumerate(days) if d <= end)
    eq, pk_, mdd, n, prev = 1.0, 1.0, 0.0, 0, False
    for k in range(k0, k1):
        out = st_[k] if st_ else False
        if out != prev:
            eq *= 1 - COST * (2 if dest != "cash" else 1); n += out
        prev = out
        if out:
            r = {"spy": Q[k+1] / Q[k], "cash": 1.0, "sect": sum(sect[s][days[k+1]] / sect[s][days[k]] for s in SECT) / len(SECT)}[dest]
        else:
            r = P[k+1] / P[k]
        eq *= r; pk_ = max(pk_, eq); mdd = max(mdd, 1 - eq / pk_)
    yrs = (dt.date.fromisoformat(days[k1]) - dt.date.fromisoformat(days[k0])).days / 365.25
    return eq ** (1 / yrs) - 1, mdd, n, eq - 1
S_ = {x: state(x) for x in (50, 20, 5)}
nm = {50: "上向きの50日線を上回る（今の形）", 20: "20日線を上回る", 5: "5日線を上回る"}
print("| 戻す合図 | 特殊な下げの間 | 年率 1999〜 | 最大下落率 | 乗り換えた回数 | 2000〜2002年 | 2007〜2009年 | 2026年 |")
print("|---|---|---|---|---|---|---|---|")
g, m, n, _ = run(None, "spy", "1999-01-04")
per = lambda st_, dest, a, b: run(st_, dest, a, b)[3]
print(f"| — | SOXを持ち続ける | {g*100:.1f}% | {m*100:.0f}% | 0 | {per(None,'spy','2000-01-03','2002-12-31')*100:+.0f}% | {per(None,'spy','2007-01-03','2009-12-31')*100:+.0f}% | {per(None,'spy','2026-01-02','2026-12-31')*100:+.0f}% |")
for x in (50, 20, 5):
    for dest, dn in (("sect", "AI以外の8業種（テーマの外の代わり）"), ("spy", "S&P500"), ("cash", "現金")):
        g, m, n, _ = run(S_[x], dest, "1999-01-04")
        print(f"| {nm[x]} | {dn} | {g*100:.1f}% | {m*100:.0f}% | {n} | {per(S_[x],dest,'2000-01-03','2002-12-31')*100:+.0f}% | {per(S_[x],dest,'2007-01-03','2009-12-31')*100:+.0f}% | {per(S_[x],dest,'2026-01-02','2026-12-31')*100:+.0f}% |")
print()
for x in (50, 20, 5):
    on_days = [days[k] for k in range(len(P)) if S_[x][k]]
    eps = []; prev = None
    for k in range(len(P)):
        if S_[x][k] and not (k and S_[x][k-1]): eps.append([days[k], None])
        if not S_[x][k] and k and S_[x][k-1]: eps[-1][1] = days[k]
    print(f"{nm[x]}: {len(eps)}回、" + "、".join(f"{a}〜{b or '今'}" for a, b in eps[-12:]))
