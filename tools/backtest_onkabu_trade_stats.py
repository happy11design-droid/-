#!/usr/bin/env python3
"""恩株ツールの調査6: 合図ごとの1トレードの平均（毎週、S&P500の構成銘柄で合図が出たら買い、1年以内に2倍なら2倍で、ならなければ1年後に手じまいとして数える）"""
import sys, datetime as dt, statistics as st
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backtest_lib import DEFAULT_CACHE, load_prices, load_members, is_member
import backtest_onkabu_fast_variants as bv
members=load_members(DEFAULT_CACHE); spy=load_prices(DEFAULT_CACHE,"SPY")
data={s:d for s in members if (d:=load_prices(DEFAULT_CACHE,s)) and len(d["c"])>300}
pre=bv.prep(data,DEFAULT_CACHE)
pos={s:{d:k for k,d in enumerate(v["date"])} for s,v in data.items()}
sp={d:k for k,d in enumerate(spy["date"])}
weeks=[d for k,d in enumerate(spy["date"]) if d>="2014-06-01" and k+1<len(spy["date"]) and dt.date.fromisoformat(spy["date"][k+1]).isocalendar()[1]!=dt.date.fromisoformat(d).isocalendar()[1]]
print("| 合図 | 件数（銘柄数） | 1年以内に2倍 | 1トレードの平均（2倍で手じまい扱い）| 同じ期間のSPY | NVDAを除く 1年以内に2倍 / 平均 | 2014〜19年 / 2020年〜 の平均 |")
print("|---|---|---|---|---|---|---|")
for label,look,up,nh,rv in bv.PARAMS:
    f=bv.make_signal(data,pre,look,up,nh,rv); out=[]
    for d in weeks:
        for s,sp_ in members.items():
            if s not in data or not is_member(sp_,d): continue
            i=pos[s].get(d)
            if i is None or i<look+1 or i+252>=len(data[s]["c"]) or not f(s,i): continue
            c=data[s]["c"]; fut=c[i+1:i+253]
            k=next((j for j,x in enumerate(fut) if x>=2*c[i]),None)
            r=2.0 if k is not None else fut[-1]/c[i]
            out.append((s,d,k is not None,r,spy["c"][sp[d]+252]/spy["c"][sp[d]]))
    if not out: print(f"| {label} | 0 |"); continue
    nv=[o for o in out if o[0]!="NVDA"]
    m=lambda xs: st.mean(o[3] for o in xs)-1 if xs else float('nan')
    e=[o for o in out if o[1]<"2020"]; l=[o for o in out if o[1]>="2020"]
    print(f"| {label} | {len(out):,}（{len({o[0] for o in out})}） | {sum(o[2] for o in out)/len(out):.1%} | {m(out):+.1%} | {st.mean(o[4] for o in out)-1:+.1%} | {sum(o[2] for o in nv)/len(nv):.1%} / {m(nv):+.1%} | {m(e):+.1%} / {m(l):+.1%} |")
