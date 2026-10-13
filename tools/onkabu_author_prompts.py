#!/usr/bin/env python3
"""恩株ツール: 著者の確認の検証用。組み合わせの再現で倍増ツールが買った売買（trades.json）から、銘柄名と日付を伏せたプロンプトを5銘柄ずつ作る（2026-10-11）"""
import sys, json, random, os, datetime as dt
sys.path.insert(0,'/home/user/-/tools')
import numpy as np
from backtest_lib import load_prices, DEFAULT_CACHE
import backtest_onkabu_fast as bfast
trades=json.load(open('/tmp/claude-0/lmtest/trades.json'))
uni=json.load(open(DEFAULT_CACHE+'/universe.json'))
spy=load_prices(DEFAULT_CACHE,"SPY"); sp={d:k for k,d in enumerate(spy["date"])}
def sma(c,j,n): return sum(c[j-n+1:j+1])/n
def fund(sym,key,day):
    p=f"{DEFAULT_CACHE}/onkabu_fund/{sym}.json"
    if not os.path.exists(p): return []
    rows=[tuple(r) for r in json.load(open(p)).get(key,[])]
    rs=[x for x in bfast.rev_series(rows) if x[0]<=day]
    return [f"{x[1]*100:+.0f}%" for x in rs[-4:]]
rnd=random.Random(7); order=list(range(len(trades))); rnd.shuffle(order)
items=[]
for k,idx in enumerate(order):
    t=trades[idx]; d=load_prices(DEFAULT_CACHE,t["sym"]); c=d["c"]; v=d["v"]; j=d["date"].index(t["sig"])
    # weekly closes: every 5th trading day back 26 weeks
    wk=[c[j-5*i] for i in range(26,-1,-1)]; base=wk[0]; wk=[round(x/base*100) for x in wk]
    ks=sp[t["sig"]]; sc=spy["c"]
    item={"id":k,"trade":idx,
      "週足の終値（26週前=100）":wk,
      "52週高値に対する位置": f"{c[j]/max(c[j-251:j+1])*100:.0f}%",
      "6カ月の騰落率": f"{c[j]/c[j-126]*100-100:+.0f}%","3カ月": f"{c[j]/c[j-63]*100-100:+.0f}%","1カ月": f"{c[j]/c[j-21]*100-100:+.0f}%",
      "50日線からの乖離": f"{c[j]/sma(c,j,50)*100-100:+.0f}%","200日線からの乖離": f"{c[j]/sma(c,j,200)*100-100:+.0f}%",
      "50日線の傾き（20日）": f"{sma(c,j,50)/sma(c,j-20,50)*100-100:+.1f}%",
      "出来高（直近20日平均÷直近200日平均）": f"{(sum(v[j-19:j+1])/20)/(sum(v[j-199:j+1])/200):.1f}倍",
      "売上の前年同期比（古い順、直近4回の決算）": fund(t["sym"],"rev",t["sig"]) or "取得不可",
      "1株利益の前年同期比（古い順、直近4回の決算）": fund(t["sym"],"eps",t["sig"]) or "取得不可",
      "業種（大分類）": (uni.get(t["sym"]) or {}).get("sector") or "不明",
      "市場全体（S&P500）": f"200日線から{sc[ks]/sma(sc,ks,200)*100-100:+.0f}%・3カ月{sc[ks]/sc[ks-63]*100-100:+.0f}%"}
    items.append(item)
json.dump(items,open('/tmp/claude-0/lmtest/items.json','w'),ensure_ascii=False,indent=0)
letters="ABCDE"
for b in range(0,len(items),5):
    batch=items[b:b+5]
    L=["あなたはこのノートブックの本（ミネルヴィニの成長株投資法）の著者として答えてください。",
       "以下の銘柄は、私のルール（6カ月で株価が2倍以上・52週高値を更新・直近の売上が前年同期比+10%以上）で「明日の寄り付きで買う」合図が出た銘柄です。"
       "銘柄名と日付は伏せています（事前の知識に頼らず、数値だけで判断してください）。",
       "目的: 数カ月〜1年以内に株価が2倍になる銘柄を持つこと。2倍で元本分を売り、残りを長く持ちます。損切りは買値の−30%、約9カ月で2倍にならなければ売ります。",
       "質問: それぞれについて、本のルールに照らして「買い注文を止める理由」があるかだけを判定してください。止める理由がなければ【買う】、あれば【止める】としてください。",
       "答えの形（必ずこの形で、1銘柄1行）: 銘柄X: 【買う】または【止める】 理由（1行）","" ]
    for i,it in enumerate(batch):
        L.append(f"■銘柄{letters[i]}")
        for kk,vv in it.items():
            if kk in ("id","trade"): continue
            L.append(f"- {kk}: {vv if not isinstance(vv,list) else ' / '.join(map(str,vv))}")
        L.append("")
    open(f'/tmp/claude-0/lmtest/prompt_{b//5+1}.txt','w').write("\n".join(L))
print(len(items), "prompts", (len(items)+4)//5)
