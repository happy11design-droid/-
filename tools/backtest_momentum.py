#!/usr/bin/env python3
"""RSの強い銘柄を毎月入れ替える方式（モメンタム）と、使っていない資金をSPYで持つ場合のバックテスト（S&P500、2015〜、後知恵なし）

使い方: tools/backtest_momentum.py > 新分析ツール/バックテスト結果/モメンタムとSPYの組み合わせ.md
"""
import sys, datetime as dt
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_swing as bs, backtest_trend as bt
from backtest_lib import COSTS, DEFAULT_CACHE, Reporter, gen_trades, load_prices, load_universe, spy_benchmark, sma
members, data = load_universe(DEFAULT_CACHE, min_bars=260)
for s in data.values(): bt.prepare(s)
bt.add_rs_rank(data, members)
spy = load_prices(DEFAULT_CACHE, "SPY"); sm200=sma(spy["c"],200); spy_up={d:(m is not None and c>m) for d,c,m in zip(spy["date"],spy["c"],sm200)}
start, end = "2015-01-02", dt.date.today().isoformat()
days = [d for d in spy["date"] if start <= d <= end]
L=[]; w=L.append
rep = Reporter(w, data, days, [("前半", start, "2020-12-31"), ("後半", "2021-01-01", end)], len(days)/252, cost=COSTS[2], risk=0.02)
rep.header()
def month_end(s,i): return i+1<len(s["date"]) and s["date"][i][:7]!=s["date"][i+1][:7]
def E(th, trend, filt):
    def f(i,s):
        if not month_end(s,i): return None
        r=s["rs"][i]
        if r is None or r<th: return None
        if trend and not (s["ma200"][i] and s["c"][i]>s["ma200"][i]): return None
        if filt and not spy_up.get(s["date"][i]): return None
        return -r
    return f
X=lambda j,s,k,px: month_end(s,j)   # 次の月末の引けで判定 → 翌月初の寄り付きで売り（まだ上位なら同じ日にまた買う）
for th in (95,98,99):
  for trend in (False,True):
    for filt in (False,True):
        tr=gen_trades(data,members,E(th,trend,filt),X,start,end,ok=bt.liquid,fill="open",max_hold=40,stop_pct=None)
        rep.line(f"RS≧{th}{'・200日線より上' if trend else ''}{'・SPYが200日線より上' if filt else ''}（月末に上位を買い、翌月末に入れ替え）",tr,0.15)
print("\n".join(L))

# ---- 使っていない資金をSPYで持つ ----
from backtest_lib import portfolio
import backtest_candle as bcd
from backtest_regime import X_BAND, X_BELOW50, srt
for s in data.values(): bs.prepare(s)
spyc = dict(zip(spy["date"], spy["c"]))
b3 = bs.simulate(data, members, bs.O_method3, bs.X_upper_band, start, end)
m50 = gen_trades(data, members, bt.E_minervini(50), X_BELOW50, start, end, ok=bt.liquid, fill="open", max_hold=500, stop_pct=0.15)
e2 = gen_trades(data, members, bcd.E2, X_BAND, start, end, ok=bt.liquid, fill="open", max_hold=120, stop_pct=0.15)
mo = gen_trades(data,members,E(95,False,False),X,start,end,ok=bt.liquid,fill="open",max_hold=40,stop_pct=None)
print("\n| 方式 | 資金の遊び: 現金 年率 / 最大下落 | 資金の遊び: SPY 年率 / 最大下落 | 前半 / 後半（SPY） |")
print("|---|---|---|---|")
half=lambda tr,lo,hi,ca: portfolio([t for t in tr if lo<=t["in"] and t["out"]<=hi],COSTS[2],7,[d for d in days if lo<=d<=hi],data,weight=0.02/0.15,seed=0,cash_asset=ca)["cagr"]
for lab,tr in (("採用中: ボリンジャーIII＋ミネルヴィニ",srt(b3+m50)),("E2 包み足",e2),("RS≧95を毎月入れ替え",mo),("採用中＋RS≧95の毎月入れ替え",srt(b3+m50+mo))):
    r=[]
    for ca in (None,spyc):
        ps=[portfolio(tr,COSTS[2],7,days,data,weight=0.02/0.15,seed=k,cash_asset=ca) for k in range(10)]
        ps.sort(key=lambda p:p["cagr"]); p=ps[5]; r.append(f"{p['cagr']*100:.1f}% / {p['mdd']*100:.1f}%")
    print(f"| {lab} | {r[0]} | {r[1]} | {half(tr,start,'2020-12-31',spyc)*100:.1f}% / {half(tr,'2021-01-01',end,spyc)*100:.1f}% |")
