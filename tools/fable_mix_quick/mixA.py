import json,os,itertools,statistics as st,sys
import numpy as np
R=os.path.expanduser("~/.cache/stock_backtest/results/")
def load(f):
    a=json.load(open(R+f)); F=a["forms"]; days=a["days"]; win=a["win"]; pos={d:k for k,d in enumerate(days)}
    base=next(n for n in F if not n.startswith("今のルール（傾き"))
    done=[d for d in F[base] if pos[d]+win<=len(days)-1]
    return F,base,done
def mat(F,done,names):
    # [form, start, seed] の1年の損益
    return np.array([[[x[0] for x in F[n][d]] for d in done] for n in names])
for uni in ("free","87"):
    F,base,done=load(f"allforms_screen_{uni}.json")
    names=[n for n in F if n!=base and not n.startswith("今のルール（傾き")]
    X=mat(F,done,names); B=mat(F,done,[base])[0]
    D=(X-B[None]).mean(axis=2)   # form x start: 同じ乱数どうしの差の平均
    nS=len(done); step=13
    res={k:[] for k in (1,3,5,10,20,50,len(names))}; pbo=[]
    for off in range(step):
        idx=list(range(off,nS,step))
        if len(idx)<8: continue
        if len(idx)%2: idx=idx[:-1]
        Dn=D[:,idx]; m=len(idx)
        for IS in itertools.combinations(range(m),m//2):
            OS=[i for i in range(m) if i not in IS]
            mi=Dn[:,list(IS)].mean(axis=1); mo=Dn[:,OS].mean(axis=1)
            order=np.argsort(-mi)
            for k in res:
                top=order[:k]; res[k].append((mi[top].mean(), mo[top].mean()))
            pbo.append(mo[order[0]]<0)
    print(f"== {uni}: 形 {len(names)}、始める日 {nS}（重ならない取り方 {step}通り）")
    print(f"   上位1形: 別の半分で今のルールを下回る割合 {100*np.mean(pbo):.1f}%")
    for k,v in res.items():
        v=np.array(v); print(f"   選ぶ側の上位{k:>3}形を等しく混ぜる: 選ぶ側 {100*v[:,0].mean():+.1f}pt → 確かめる側 {100*v[:,1].mean():+.1f}pt、確かめる側で今のルールを下回る割合 {100*(v[:,1]<0).mean():.0f}%")
    # 形どうしの差の相関（全部の始める日）
    C=np.corrcoef(D); iu=np.triu_indices(len(names),1); c=C[iu]; c=c[~np.isnan(c)]
    print(f"   今のルールとの差どうしの相関: 中央値 {np.median(c):.2f}、四分位 {np.percentile(c,25):.2f}〜{np.percentile(c,75):.2f}")
    # 乱数による揺れ（同じ形・同じ始める日の乱数3通りの標準偏差）と、形の違いによる揺れ
    sd_seed=B.std(axis=1).mean(); print(f"   今のルールの1年の損益: 乱数の違いによる揺れ（標準偏差の平均） {100*sd_seed:.1f}pt、始める日の違いによる揺れ {100*B.mean(axis=1).std():.1f}pt")
