"""空の枠から始めた1年の区切り（st2roll）で、監視銘柄を半分ずつ混ぜた形と、中身で選んだ5形を等しく混ぜた形を数える"""
import json,os
import numpy as np
R=os.path.expanduser("~/.cache/stock_backtest/results/")
def load(f):
    a=json.load(open(R+f)); F=a["forms"]; days=a["days"]; pos={d:k for k,d in enumerate(days)}
    base=next(n for n in F if not n.startswith("今のルール（傾き")); done=[d for d in F[base] if pos[d]+a["win"]<=len(days)-1]
    return F,base,done
arr=lambda F,done,n,j=0: np.array([[x[j] for x in F[n][d]] for d in done])
Ff,bf,df=load("st2roll_free.json"); F8,b8,d8=load("st2roll_87.json"); done=[d for d in df if d in set(d8)]
q=lambda n,F: next(x for x in F if x.endswith(n))
nm="待っている現金をQQQに置く"
A8,Af=arr(F8,done,q(nm,F8)),arr(Ff,done,q(nm,Ff)); D8,Dfd=arr(F8,done,q(nm,F8),1),arr(Ff,done,q(nm,Ff),1)
early=np.array([d<"2021-01-01" for d in done])
print(f"空の枠から始めた1年（始める日{len(done)}×乱数10、候補の25%を見送る形。今のルール＋QQQ）")
for lab,X in (("87銘柄だけ",A8),("全業種だけ",Af),("半分ずつ（1年のあいだ戻さない）",(A8+Af)/2),("87銘柄75%・全業種25%",0.75*A8+0.25*Af)):
    print(f"  {lab:<22} 損益の平均 {100*X.mean():5.1f}%（〜2020年 {100*X[early].mean():5.1f}／2021年〜 {100*X[~early].mean():5.1f}） 悪い5% {100*np.percentile(X,5):+6.1f}% 悪い1% {100*np.percentile(X,1):+6.1f}% マイナスで終わる割合 {100*(X<0).mean():4.1f}% 乱数による揺れ {100*X.std(axis=1).mean():.1f}pt")
print(f"  1年の中の最大下落率の平均: 87 {100*D8.mean():.1f}%・全業種 {100*Dfd.mean():.1f}%（半分ずつはこの平均 {100*(D8+Dfd).mean()/2:.1f}% が上限）、悪い5%: {100*np.percentile(D8,95):.1f}%・{100*np.percentile(Dfd,95):.1f}%")
m8,mf=A8.mean(axis=1),Af.mean(axis=1); print(f"  始める日ごとの1年の損益の相関 {np.corrcoef(m8,mf)[0,1]:.2f}、87銘柄の方が良かった始める日 {100*(m8>mf).mean():.0f}%、差の標準偏差 {100*(m8-mf).std():.0f}pt")
keys=["待っている現金をQQQに置く＋底の後40日は2倍ETF","損切り18%","一目","決算㉒","RSI(2)≦15"]
for uni,F,b in (("全業種",Ff,bf),("87銘柄",F8,b8)):
    B=arr(F,done,b); ns=[next(n for n in F if k in n and "銘柄数3" not in n) for k in keys]
    X=np.mean([arr(F,done,n) for n in ns],axis=0); d=X-B; m=d.mean(axis=1)
    print(f"  案3 {uni}: 中身で選んだ5形を等しく（今のルールとの差） {100*d.mean():+.1f}pt、良い割合 {100*(m>0).mean():.0f}%、〜2020年 {100*d[early].mean():+.1f}／2021年〜 {100*d[~early].mean():+.1f}、悪い5% {100*np.percentile(X,5):+.1f}%（今 {100*np.percentile(B,5):+.1f}%）")
