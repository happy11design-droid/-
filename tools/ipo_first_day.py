"""過去の大型米国IPOの「初日に始値で買う」検証。
データ: ~/.cache/stock_backtest/long/ipo/<銘柄>.csv（日足・未調整。無ければ取得して置く）
日足しかないので、同じ日に利確と損切りの両方の値に届いた場合は、どちらが先かは分からない。
その日は「良い方（利確が先）」と「悪い方（損切りが先）」の両方で集計する。
"""
import os, json, sys, time
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from market_data import fetch

D = os.path.expanduser("~/.cache/stock_backtest/long/ipo")
# 銘柄: 初日の取引日（KLARはYahooに初日のデータが無いので入れていない）
IPOS = {"META":"2012-05-18","BABA":"2014-09-19","SHOP":"2015-05-21","SNAP":"2017-03-02","DBX":"2018-03-23","ZS":"2018-03-16","SPOT":"2018-04-03","DOCU":"2018-04-27",
"LYFT":"2019-03-29","PINS":"2019-04-18","ZM":"2019-04-18","BYND":"2019-05-02","UBER":"2019-05-10","CRWD":"2019-06-12","CHWY":"2019-06-14","NET":"2019-09-13","DDOG":"2019-09-19","PTON":"2019-09-26",
"SNOW":"2020-09-16","U":"2020-09-18","PLTR":"2020-09-30","DASH":"2020-12-09","ABNB":"2020-12-10","AFRM":"2021-01-13","BMBL":"2021-02-11","RBLX":"2021-03-10","CPNG":"2021-03-11","COIN":"2021-04-14","PATH":"2021-04-21",
"S":"2021-06-30","DUOL":"2021-07-28","HOOD":"2021-07-29","TOST":"2021-09-22","GFS":"2021-10-28","RIVN":"2021-11-10","NU":"2021-12-09","CAVA":"2023-06-15","ARM":"2023-09-14","CART":"2023-09-19","KVYO":"2023-09-20","BIRK":"2023-10-11",
"ALAB":"2024-03-20","RDDT":"2024-03-21","CRWV":"2025-03-28","CRCL":"2025-06-05","FIG":"2025-07-31"}

def load(t, d):
    p = f"{D}/{t}.csv"
    if not os.path.exists(p):
        os.makedirs(D, exist_ok=True)
        a = int(pd.Timestamp(d).timestamp()) - 5*86400
        r = json.loads(fetch(f"https://query1.finance.yahoo.com/v8/finance/chart/{t}?interval=1d&period1={a}&period2={a+50*86400}"))["chart"]["result"][0]
        q = r["indicators"]["quote"][0]
        pd.DataFrame({k: q[k] for k in ["open","high","low","close","volume"]},
                     index=pd.to_datetime(r["timestamp"], unit="s").normalize()).dropna().to_csv(p)
        time.sleep(0.3)
    df = pd.read_csv(p, index_col=0, parse_dates=True)
    df = df[df.volume > 0]
    assert str(df.index[0].date()) == d, (t, df.index[0])
    return df

rows = []
for t, d in IPOS.items():
    df = load(t, d); o, h, l, c = df.iloc[0][["open","high","low","close"]]
    c2 = df.iloc[1]["close"]
    rows.append(dict(銘柄=t, 日=d, 始値=o, 高値まで=h/o-1, 安値まで=l/o-1, 終値=c/o-1, 翌日終値=c2/o-1))
R = pd.DataFrame(rows)
pct = lambda x: f"{x*100:+.1f}%"
print(f"対象 {len(R)} 社（{R.日.min()}〜{R.日.max()}）\n")
print("■始値で買い、その日の終値で売る")
print(f"  勝ち {(R.終値>0).mean():.0%}  平均 {pct(R.終値.mean())}  中央値 {pct(R.終値.median())}  最良 {pct(R.終値.max())}  最悪 {pct(R.終値.min())}")
print(f"  （参考: 翌日の終値で売る → 勝ち {(R.翌日終値>0).mean():.0%}  平均 {pct(R.翌日終値.mean())}  中央値 {pct(R.翌日終値.median())}）")
print("\n■その日のうちに、始値から何%上まで行ったか（高値）")
for x in [.03,.05,.10,.20]: print(f"  +{x:.0%}以上: {(R.高値まで>=x).mean():.0%}")
print("■その日のうちに、始値から何%下まで行ったか（安値）")
for x in [.03,.05,.10,.20]: print(f"  -{x:.0%}以下: {(R.安値まで<=-x).mean():.0%}")
print("\n■利確+X%・損切り-Y%の指値／逆指値を入れ、どちらにも届かなければ終値で売る")
print("   （両方に届いた日は順番が分からない → 良い方／悪い方の両方）")
for tp in [.05,.10,.20]:
    for sl in [.05,.10]:
        good=[];bad=[];both=0
        for _,r in R.iterrows():
            ht, lt = r.高値まで>=tp, r.安値まで<=-sl
            if ht and lt: both+=1; good.append(tp); bad.append(-sl)
            elif ht: good.append(tp); bad.append(tp)
            elif lt: good.append(-sl); bad.append(-sl)
            else: good.append(r.終値); bad.append(r.終値)
        g,b=pd.Series(good),pd.Series(bad)
        print(f"  +{tp:.0%}/-{sl:.0%}: 平均 {pct(b.mean())}〜{pct(g.mean())}  勝ち {(b>0).mean():.0%}〜{(g>0).mean():.0%}  （両方に届いた日 {both}社）")
print("\n■1社ずつ（始値に対する%）")
print(R.assign(**{k: R[k].map(pct) for k in ["高値まで","安値まで","終値","翌日終値"]}, 始値=R.始値.round(2)).to_string(index=False))
