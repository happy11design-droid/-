import json,os,itertools
import numpy as np
R=os.path.expanduser("~/.cache/stock_backtest/results/")
def q(x,p): return np.percentile(x,p)
def load(f):
    a=json.load(open(R+f)); F=a["forms"]; days=a["days"]; win=a["win"]; pos={d:k for k,d in enumerate(days)}
    base=next(n for n in F if not n.startswith("今のルール（傾き"))
    done=[d for d in F[base] if pos[d]+win<=len(days)-1]
    return F,base,done
def arr(F,done,n,j=0): return np.array([[x[j] for x in F[n][d]] for d in done])
print("### 1. 本番の14形（st2roll、始める日×乱数10通り）: 2口・全部を等しく混ぜる（口は1年のあいだ戻さない）")
for uni in ("free","87"):
    F,base,done=load(f"st2roll_{uni}.json")
    names=[n for n in F if n!=base and not n.startswith("今のルール（傾き")]
    short=lambda n: n.split("（3日間）")[-1].lstrip("＋")[:44] or "今のルール"
    B=arr(F,done,base); Bd=arr(F,done,base,1)
    y=np.array([d[:4] for d in done]); e=(y<="2020")   # 始める日が2021年より前（1年の区切りの大半が2015〜2021年）
    def stat(Xr,Xd,label):
        d=Xr-B; m=d.mean(axis=1); nz=np.abs(m)>1e-9
        print(f"  {uni} {label:<46} 差 {100*d.mean():+5.1f}pt（良い割合 {100*(m[nz]>0).mean() if nz.any() else 0:3.0f}%、〜2020年に始めた {100*d[e].mean():+5.1f}／2021年〜 {100*d[~e].mean():+5.1f}） 1年の損益の悪い5% {100*q(Xr,5):+6.1f}%（今 {100*q(B,5):+6.1f}%） 下落率の平均 {100*Xd.mean():.1f}%（今 {100*Bd.mean():.1f}%）※混ぜた形の下落率は上限")
    allr=np.mean([arr(F,done,n) for n in names],axis=0); alld=np.mean([arr(F,done,n,1) for n in names],axis=0)
    stat(allr,alld,"14形を等しく（15口。今のルールを含まない）")
    for key in ("銘柄数3","QQQに置く＋底の後40日","一目","損切り18%","決算㉒"):
        nn=[n for n in names if key in n and ("銘柄数3＋" not in n or key=="銘柄数3＋")]
        if not nn: continue
        n=nn[0]; stat((arr(F,done,n)+B)/2,(arr(F,done,n,1)+Bd)/2,"今のルール50%＋"+short(n)[:30])
    # 乱数の違う2口（同じ形）: 運の揺れ
    sd1=B.std(axis=1).mean(); pair=(B[:,:5]+B[:,5:])/2; sd2=pair.std(axis=1).mean()
    print(f"  {uni} 今のルールの1年の損益の、乱数による揺れ: 1口 {100*sd1:.1f}pt → 乱数の違う2口を半分ずつ {100*sd2:.1f}pt。悪い5%: {100*q(B,5):+.1f}% → {100*q(pair,5):+.1f}%。乱数どうしの相関 {np.mean([np.corrcoef(B[:,i],B[:,j])[0,1] for i in range(10) for j in range(i+1,10)]):.2f}")
print()
print("### 2. 候補を見送らない形との差（v_noskip）")
for uni in ("free","87"):
    try:
        a=json.load(open(R+f"v_noskip_{uni}.json")); print("  ",uni,list(a.keys())[:6], {k:(len(v) if hasattr(v,'__len__') else v) for k,v in list(a.items())[:6]})
    except Exception as ex: print(ex)
