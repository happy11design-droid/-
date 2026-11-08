#!/usr/bin/env python3
"""底の合図の当たりやすさ（SOXの1・3・6か月後、本当の底からのずれ）。入力は OPT_SIGDUMP の出力（既定 ~/.cache/stock_backtest/results/sig.json）。2026-11-06"""
import json, os, statistics as st, sys
S="/tmp/claude-0/-home-user--/edd7edf3-5b7b-5ba2-9fef-25e6fc170250/scratchpad"
a=json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/.cache/stock_backtest/results/sig.json"))); days=a["days"]; P=a["sox"]; B=a["bottom"]
idx={d:k for k,d in enumerate(days)}
k15=next(k for k,d in enumerate(days) if d>="2015-01-02")
def fw(k,n):
    return P[k+n]/P[k]-1 if k+n<len(P) and P[k] and P[k+n] else None
base={n:[fw(k,n) for k in range(k15,len(P)) if fw(k,n) is not None] for n in (21,63,126)}
pc=lambda x: "—" if x is None else f"{x*100:+.1f}%"
N={"FTD_N":"フォロースルー・デー（ナスダック）","FTD_S":"フォロースルー・デー（SOX）","ZBT":"ブレス・スラスト","P50":"50日線より上の割合 15%→30%","D90":"90%の日",
   "NLPK":"新安値のピークアウト","MCC":"マクレラン −100→0","VIXPK":"VIXのピークアウト","RSI_S":"SOXのRSI(14) 30→50","MACD0":"SOXのMACD 0超え","MAUP":"SOXの移動平均の並び",
   "W30":"ワインスタインのステージ2","MI":"モメンタム指数 0超え","NHNL":"新高値−新安値がプラス","WB":"W型の底（ボリンジャー）","CONR2":"コナーズ RSI(2)≦5","VIXS":"コナーズ VIXの伸び"}
print("| 合図 | 2015年〜の回数 | 1か月後にSOXが上 | 3か月後 | 6か月後 | 3か月後（中央値） | 6か月後（中央値） | 本当の底からのずれ（中央値、取引日） | 底から10日以内 | 直近（2026年8月〜） |")
print("|---|---|---|---|---|---|---|---|---|---|")
print(f"| （参考）すべての日 | — | {sum(x>0 for x in base[21])/len(base[21]):.0%} | {sum(x>0 for x in base[63])/len(base[63]):.0%} | {sum(x>0 for x in base[126])/len(base[126]):.0%} | {pc(st.median(base[63]))} | {pc(st.median(base[126]))} | — | — | — |")
for nm,ds in B.items():
    ks=[idx[d] for d in ds if d>="2015-01-02"]
    r={n:[fw(k,n) for k in ks if fw(k,n) is not None] for n in (21,63,126)}
    lag=[]
    for k in ks:
        lo=min(range(max(0,k-60),min(len(P),k+61)), key=lambda j: P[j] if P[j] else 9e9)
        lag.append(k-lo)
    near=sum(1 for x in lag if -10<=x<=10)/len(lag) if lag else 0
    rec=[d for d in ds if d>="2026-08-01"]
    f=lambda n: f"{sum(x>0 for x in r[n])/len(r[n]):.0%}" if r[n] else "—"
    print(f"| {N[nm]} | {len(ks)} | {f(21)} | {f(63)} | {f(126)} | {pc(st.median(r[63]) if r[63] else None)} | {pc(st.median(r[126]) if r[126] else None)} | {st.median(lag) if lag else '—'} | {near:.0%} | {'、'.join(x[5:] for x in rec) or 'なし'} |")
print("\n待つ形で買わない日数（2015年〜）: " + "、".join(f"{N[k]} {v}日" for k,v in a["wait"].items() if k not in ('CONR2','VIXS')))
