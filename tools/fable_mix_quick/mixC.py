import json,os,itertools
import numpy as np
R=os.path.expanduser("~/.cache/stock_backtest/results/")
def load(f):
    a=json.load(open(R+f)); F=a["forms"]; days=a["days"]; win=a["win"]; pos={d:k for k,d in enumerate(days)}
    base=next(n for n in F if not n.startswith("今のルール（傾き"))
    done=[d for d in F[base] if pos[d]+win<=len(days)-1]
    return F,base,done
arr=lambda F,done,n,j=0: np.array([[x[j] for x in F[n][d]] for d in done])
print("### 3. 両方の監視銘柄で良い形だけを選ぶ決まり（今の目安に近い）で上位K形を混ぜる: 選ぶ側→確かめる側")
Ff,bf,df=load("allforms_screen_free.json"); F8,b8,d8=load("allforms_screen_87.json")
done=[d for d in df if d in set(d8)]
kf={n[len(bf):]:n for n in Ff if n.startswith(bf) and n!=bf}; k8={n[len(b8):]:n for n in F8 if n.startswith(b8) and n!=b8}
keys=[k for k in kf if k in k8]; print("  両方にある形:",len(keys))
Df=(np.array([arr(Ff,done,kf[k]) for k in keys])-arr(Ff,done,bf)[None]).mean(axis=2)
D8=(np.array([arr(F8,done,k8[k]) for k in keys])-arr(F8,done,b8)[None]).mean(axis=2)
nS=len(done); step=13; out={k:[] for k in (1,5,14,30)}
for off in range(step):
    idx=list(range(off,nS,step))
    if len(idx)%2: idx=idx[:-1]
    m=len(idx)
    for IS in itertools.combinations(range(m),m//2):
        OS=[i for i in range(m) if i not in IS]; I=[idx[i] for i in IS]; O=[idx[i] for i in OS]
        mf,m8=Df[:,I].mean(axis=1),D8[:,I].mean(axis=1)
        wf,w8=(Df[:,I]>0).mean(axis=1),(D8[:,I]>0).mean(axis=1)
        score=np.minimum(mf,m8); score[(wf<0.55)|(w8<0.55)]-=1   # 両方でプラス・良い割合55%以上を先に
        order=np.argsort(-score)
        for k in out:
            t=order[:k]; out[k].append((np.minimum(mf,m8)[t].mean(), Df[t][:,O].mean(), D8[t][:,O].mean()))
for k,v in out.items():
    v=np.array(v); print(f"  上位{k:>2}形を等しく: 選ぶ側（悪い方の監視銘柄） {100*v[:,0].mean():+.1f}pt → 確かめる側 全業種 {100*v[:,1].mean():+.1f}pt（下回る割合 {100*(v[:,1]<0).mean():.0f}%）・87銘柄 {100*v[:,2].mean():+.1f}pt（{100*(v[:,2]<0).mean():.0f}%）、確かめる側のばらつき（標準偏差） {100*v[:,1].std():.1f}・{100*v[:,2].std():.1f}pt")
print()
print("### 4. 候補を見送らない形（実際の運用に近い）と、候補の25%を乱数で見送る形（乱数の平均）の1年の損益")
for uni in ("free","87"):
    a=json.load(open(R+f"v_noskip_{uni}.json")); F=a["forms"]; days=a["days"]; pos={d:k for k,d in enumerate(days)}
    base=next(n for n in F if not n.startswith("今のルール（傾き")); 
    F2,b2,done2=load(f"troll_{uni}.json")
    done=[d for d in F[base] if d in F2[b2] and pos[d]+250<=len(days)-1]
    A=arr(F,done,base); B=arr(F2,done,b2)
    print(f"  {uni}: 見送らない {100*A.mean():+.1f}%（乱数 {A.shape[1]}通り、乱数による揺れ {100*A.std(axis=1).mean():.1f}pt）、25%見送る {100*B.mean():+.1f}%（揺れ {100*B.std(axis=1).mean():.1f}pt）、始める日 {len(done)}")
