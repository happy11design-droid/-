import json,os
import numpy as np
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"mixD.py")).read().split("for uni in")[0])
A={u:json.load(open(R+f"hold_eq_{u}.json")) for u in ("free","87")}
def get(u,cond):
    n=next(n for n in A[u] if cond(n)); return [np.array(x,float) for x in A[u][n]["eq"]]
days=A["87"][list(A["87"])[0]]["days"]
b=lambda n:n.endswith("待っている現金をQQQに置く"); al=lambda n:"2倍ETFをいつでも" in n; s2=lambda n:"30週線" in n
E8,Ef,Efa,Efs,E8s=get("87",b),get("free",b),get("free",al),get("free",s2),get("87",s2)
S8=stats(E8,days); Sf=stats(Ef,days)
W=250; st=list(range(0,len(days)-W,10)); early=np.array([days[s]<"2021-01-01" for s in st])
def show(label,Es):
    S=stats(Es,days)
    for nm,S0 in (("87銘柄",S8),("全業種",Sf)):
        df=S["r"]-S0["r"]; m=df.mean(axis=0)
        print(f"  {label:<30} 対{nm}: 1年の損益の差 {100*df.mean():+5.1f}pt（良い割合 {100*(m>0).mean():3.0f}%、〜2020年に始めた {100*m[early].mean():+5.1f}／2021年〜 {100*m[~early].mean():+5.1f}）、下落率の差 {100*(S['d']-S0['d']).mean():+.1f}pt")
    print(f"  {'':<30} 年率 {100*S['cg']:.1f}%・最大下落率 {100*S['dd']:.0f}%（最悪 {100*S['ddw']:.0f}%）・悪い5%の下落率 {100*np.percentile(S['d'],95):.1f}%・1年の損益の悪い5% {100*np.percentile(S['r'],5):+.1f}%")
show("①87今50＋全業種今50",blend([E8,Ef],[.5,.5],days))
show("②87今50＋全業種いつでも2倍50",blend([E8,Efa],[.5,.5],days))
show("③87ステージ2 50＋全業種ステージ2 50",blend([E8s,Efs],[.5,.5],days))
# 年ごとに良い方の口がどちらか
ys=sorted(set(d[:4] for d in days)); idx={y:[i for i,d in enumerate(days) if d[:4]==y] for y in ys}
yr=lambda E: np.median(np.array([[e[idx[y][-1]]/e[idx[y][0]-1 if idx[y][0]>0 else 0]-1 for y in ys] for e in E]),axis=0)
a,bb=yr(E8),yr(Ef); print("  87銘柄の方が良かった年:",[y for y,x,z in zip(ys,a,bb) if x>z])
