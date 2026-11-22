import json,os
import numpy as np
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"mixD.py")).read().split("for uni in")[0])
A={u:json.load(open(R+f"hold_eq_{u}.json")) for u in ("free","87")}
def get(u,cond):
    n=next(n for n in A[u] if cond(n)); return [np.array(x,float) for x in A[u][n]["eq"]], A[u][n]["days"]
b=lambda n:n.endswith("待っている現金をQQQに置く")
Ef,days=get("free",b); E8,d8=get("87",b); assert days==d8
def show(label,Es,ref):
    S=stats(Es,days); S0=stats(ref,days); df=S["r"]-S0["r"]
    print(f"  {label:<26} 年率 {100*S['cg']:.1f}%（2015〜21 {100*S['c1']:.1f}／2022〜 {100*S['c2']:.1f}） 最大下落率 {100*S['dd']:.0f}%（最悪 {100*S['ddw']:.0f}%） 1年の区切り: 損益の平均 {100*S['r'].mean():.1f}%・悪い5% {100*np.percentile(S['r'],5):+.1f}%・悪い5%の下落率 {100*np.percentile(S['d'],95):.1f}%")
    return S
print("== 監視銘柄を混ぜる（今のルール＋QQQ、乱数30通り。同じ番号の乱数どうしを組にする）")
S8=show("87銘柄だけ",E8,E8); Sf=show("全業種だけ",Ef,E8)
for w in (0.5,0.75):
    show(f"87銘柄{int(w*100)}%＋全業種{int(100-w*100)}%（毎年戻す）",blend([E8,Ef],[w,1-w],days),E8)
show("87銘柄50%＋全業種50%（戻さない）",blend([E8,Ef],[.5,.5],days,False),E8)
r8=np.concatenate([np.diff(x)/x[:-1] for x in E8[:10]]); rf=np.concatenate([np.diff(x)/x[:-1] for x in Ef[:10]])
print(f"  毎日の損益の相関 {np.corrcoef(r8,rf)[0,1]:.2f}、1年の損益の相関 {np.corrcoef(S8['r'][:10].ravel(),Sf['r'][:10].ravel())[0,1]:.2f}、1年の損益の差（87−全業種）の標準偏差 {100*(S8['r']-Sf['r']).std():.0f}pt")
ys=sorted(set(d[:4] for d in days)); idx={y:[i for i,d in enumerate(days) if d[:4]==y] for y in ys}
def yr(E): 
    m=np.median(np.array([[e[idx[y][-1]]/e[idx[y][0]-1 if idx[y][0]>0 else 0]-1 for y in ys] for e in E]),axis=0); return " ".join(f"{100*v:+.0f}" for v in m)
print("  年ごと",ys[0],"〜",ys[-1]); print("   87銘柄:",yr(E8)); print("   全業種:",yr(Ef)); print("   半分ずつ:",yr(blend([E8,Ef],[.5,.5],days)))
