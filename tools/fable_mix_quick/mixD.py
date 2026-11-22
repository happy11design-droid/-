import json,os
import numpy as np
R=os.path.expanduser("~/.cache/stock_backtest/results/")
def mdd(e): 
    p=np.maximum.accumulate(e); return float((1-e/p).max())
def stats(E,days,B=None):
    yrs=(np.datetime64(days[-1])-np.datetime64(days[0])).astype(int)/365.25
    cg=[(e[-1]/e[0])**(1/yrs)-1 for e in E]; dd=[mdd(e) for e in E]
    i22=next(i for i,d in enumerate(days) if d>="2022-01-01"); y1=(np.datetime64(days[i22])-np.datetime64(days[0])).astype(int)/365.25
    c1=[(e[i22]/e[0])**(1/y1)-1 for e in E]; c2=[(e[-1]/e[i22])**(1/(yrs-y1))-1 for e in E]
    # 1年の区切り（10取引日ごと）
    W=250; st=range(0,len(days)-W,10)
    r=np.array([[e[s+W]/e[s]-1 for s in st] for e in E]); d=np.array([[mdd(e[s:s+W+1]) for s in st] for e in E])
    return dict(cg=np.median(cg),dd=np.median(dd),ddw=max(dd),c1=np.median(c1),c2=np.median(c2),r=r,d=d)
def blend(Es,w,days,rebal=True):
    out=[]
    for k in range(len(Es[0])):
        rets=[np.diff(E[k])/E[k][:-1] for E in Es]; val=np.array(w,float); tot=[1.0]
        for t in range(len(rets[0])):
            if rebal and days[t+1][:4]!=days[t][:4]: val=np.array(w)*val.sum()
            val=val*(1+np.array([r[t] for r in rets])); tot.append(val.sum())
        out.append(np.array(tot))
    return out
for uni in ("free","87"):
    a=json.load(open(R+f"hold_eq_{uni}.json")); names=list(a); days=a[names[0]]["days"]
    E={n:[np.array(x,float) for x in a[n]["eq"]] for n in names}
    key=lambda s: next(n for n in names if s(n))
    base=key(lambda n: n.endswith("待っている現金をQQQに置く")); s2=key(lambda n:"30週線" in n); al=key(lambda n:"2倍ETFをいつでも" in n); mg=key(lambda n:"信用①" in n)
    S0=stats(E[base],days)
    def show(label,Es):
        S=stats(Es,days); df=S["r"]-S0["r"]; m=df.mean(axis=0); nz=np.abs(m)>1e-9
        print(f"  {uni} {label:<34} 年率 {100*S['cg']:.1f}%（2015〜21 {100*S['c1']:.1f}／2022〜 {100*S['c2']:.1f}） 最大下落率 {100*S['dd']:.0f}%（乱数の最悪 {100*S['ddw']:.0f}%） 1年の区切り: 差 {100*df.mean():+.1f}pt・良い割合 {100*(m[nz]>0).mean() if nz.any() else 0:.0f}%・下落率の差 {100*(S['d']-S0['d']).mean():+.1f}pt・悪い5%の下落率 {100*np.percentile(S['d'],95):.1f}%")
    print(f"== {uni}（毎日の資金、乱数{len(E[base])}通り、{days[0]}〜{days[-1]}。口は毎年1月に戻す）")
    show("今のルール（QQQ）",E[base]); show("QQQ＋ステージ2",E[s2]); show("いつでも2倍ETF",E[al]); show("信用1.5倍・6銘柄",E[mg])
    show("今50%＋ステージ2 50%",blend([E[base],E[s2]],[.5,.5],days))
    show("今50%＋いつでも2倍 50%",blend([E[base],E[al]],[.5,.5],days))
    show("今・ステージ2・いつでも2倍 1/3ずつ",blend([E[base],E[s2],E[al]],[1/3]*3,days))
    show("今75%＋信用 25%",blend([E[base],E[mg]],[.75,.25],days))
    show("4つを1/4ずつ",blend([E[base],E[s2],E[al],E[mg]],[.25]*4,days))
    show("今50%＋ステージ2 50%（戻さない）",blend([E[base],E[s2]],[.5,.5],days,False))
    # 毎日の損益の差の大きさ（年率の標準偏差）
    for n,l in ((s2,"ステージ2"),(al,"いつでも2倍"),(mg,"信用")):
        te=np.mean([np.std(np.diff(x)/x[:-1]-np.diff(b)/b[:-1])*np.sqrt(252) for x,b in zip(E[n],E[base])]); print(f"     今のルールとの毎日の差の大きさ（年率）: {l} {100*te:.1f}%")
