#!/usr/bin/env python3
"""恩株ツールの調査3: 資金6,000ドル・4銘柄で、下がったときに買う場合の資産の増え方（SPYとの比較）

使い方（先に backtest_onkabu.py・backtest_onkabu_features.py の fetch を済ませる）:
  tools/backtest_onkabu_portfolio.py [--cache DIR] [--out FILE] [--summary FILE] [--seeds 30]

やり方:
  - 毎月の最初の取引日に「候補」を決める（その時点で分かる数値だけ。後知恵なし）。
  - 毎日、候補のうち「下がった」合図が出た銘柄を、次の日の寄り付きで買う。枠は4つ（資金÷4ずつ）。
    同じ日に枠より多く合図が出たら、ランダムな順で選ぶ（順番を変えて何度も回し、中央値を出す）。
  - 終値が買値の2倍になったら、その終値で55.7%を売る（税引き後で元本が戻る）。残りは「恩株」として最後まで持ち、枠から外れる。
    戻ったお金で、また次の合図を待つ。
  - 2倍にならない銘柄の扱い（手じまい）を何通りか比べる。
  - 税: 売って利益が出たら20.315%（損失との通算は考えない）。最後まで持っている株は売らずに評価する（SPYも同じ）。
  - 待っている間の現金は利息なし（0%）。
"""
import argparse
import datetime as dt
import os
import random
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backtest_lib import DEFAULT_CACHE, load_prices, sma
import backtest_onkabu as ob
import backtest_onkabu_features as bf

CAPITAL = 6000.0
SLOTS = 4
TAX = ob.TAX
COST = 0.001   # 片道の売買コスト（約定のずれを含む）


# ---------- 候補 ----------

CANDIDATES = [
    ("A 売上の伸び≧15%・時価総額上位100・値動き上位40%",
     lambda f: bf.g(f, "rev_yoy", 0.15) and f["rank"] <= 100 and bf.g(f, "vol60_p", 0.6)),
    ("B 売上の伸び≧15%・時価総額上位100",
     lambda f: bf.g(f, "rev_yoy", 0.15) and f["rank"] <= 100),
    ("C S&P500全部（選ばない）", lambda f: True),
]


# ---------- 下がった合図 ----------

def make_dips(data, spy):
    """合図の関数 {名前: fn(sym, i) -> bool}。i はその銘柄の日足の位置（その日の終値で判定し、翌日の寄り付きで買う）"""
    hi252, ma200 = {}, {}
    for s, d in data.items():
        c = d["c"]
        h, out = [], []
        from collections import deque
        dq = deque()
        for i, v in enumerate(c):
            while dq and c[dq[-1]] <= v:
                dq.pop()
            dq.append(i)
            if dq[0] <= i - 252:
                dq.popleft()
            out.append(c[dq[0]])
        hi252[s] = out
        ma200[s] = sma(c, 200)
    spy_hi = []
    m = 0
    from collections import deque
    dq = deque()
    sc = spy["c"]
    for i, v in enumerate(sc):
        while dq and sc[dq[-1]] <= v:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - 252:
            dq.popleft()
        spy_hi.append(sc[dq[0]])
    spy_pos = {d: k for k, d in enumerate(spy["date"])}

    def spy_dd(day):
        k = spy_pos[day]
        return sc[k] / spy_hi[k] - 1

    return {
        "すぐ買う（下がるのを待たない）": lambda s, i: True,
        "52週高値から−15%以上": lambda s, i: data[s]["c"][i] <= hi252[s][i] * 0.85,
        "52週高値から−25%以上": lambda s, i: data[s]["c"][i] <= hi252[s][i] * 0.75,
        "52週高値から−35%以上": lambda s, i: data[s]["c"][i] <= hi252[s][i] * 0.65,
        "200日線を下回った": lambda s, i: ma200[s][i] is not None and data[s]["c"][i] < ma200[s][i],
        "相場全体（SPY）が52週高値から−10%以上": lambda s, i: spy_dd(data[s]["date"][i]) <= -0.10,
        "SPYが−10%以上 または 52週高値から−25%以上":
            lambda s, i: spy_dd(data[s]["date"][i]) <= -0.10 or data[s]["c"][i] <= hi252[s][i] * 0.75,
    }


# ---------- 手じまい（2倍にならない銘柄） ----------

EXITS = [
    ("持ち続ける", None, None),
    ("3年で2倍にならなければ売る", None, 3 * 252),
    ("買値の−50%で売る", 0.5, None),
]


def simulate(data, spy, days, cand_by_month, dip, stop, max_days, seed):
    rnd = random.Random(seed)
    pos = {s: {d: k for k, d in enumerate(v["date"])} for s, v in data.items()}
    cash = CAPITAL
    active = {}     # sym -> {"sh", "px"（買値）, "day"（買った日の位置）}
    onkabu = {}     # sym -> 株数
    trades = []     # (結果, 保有日数)
    pending = []    # 翌日の寄り付きで買う銘柄
    curve = []
    cash_share = []
    n_onk = 0
    month_cands = []
    for t, day in enumerate(days):
        if day[:7] in cand_by_month and (t == 0 or days[t - 1][:7] != day[:7]):
            month_cands = cand_by_month[day[:7]]
        # 1) 寄り付きで買う
        for s in pending:
            k = pos[s].get(day)
            if k is None or s in active or len(active) >= SLOTS:
                continue
            capital_active = cash + sum(p["sh"] * p["px"] for p in active.values())
            amt = min(cash, capital_active / SLOTS)
            if amt < 100:
                continue
            px = data[s]["o"][k] * (1 + COST)
            active[s] = {"sh": amt / px, "px": px, "t": t}
            cash -= amt
        pending = []

        # 2) 終値で、2倍・手じまい・上場廃止
        for s in list(active):
            p = active[s]
            k = pos[s].get(day)
            last = data[s]["date"][-1]
            if k is None:
                if day > last:     # 上場廃止: 最後の終値で売る
                    c = data[s]["c"][-1] * (1 - COST)
                    gain = p["sh"] * (c - p["px"])
                    cash += p["sh"] * c - max(0, gain) * TAX
                    trades.append((c / p["px"], t - p["t"], "上場廃止"))
                    del active[s]
                continue
            c = data[s]["c"][k]
            if c >= 2 * p["px"]:
                sell = p["sh"] * ob.SELL_AT_2X
                proceeds = sell * c * (1 - COST)
                cash += proceeds - TAX * max(0, proceeds - sell * p["px"])
                onkabu[s] = onkabu.get(s, 0) + p["sh"] - sell
                trades.append((2.0, t - p["t"], "2倍"))
                n_onk += 1
                del active[s]
            elif (stop and c <= p["px"] * stop) or (max_days and t - p["t"] >= max_days):
                proceeds = p["sh"] * c * (1 - COST)
                cash += proceeds - TAX * max(0, proceeds - p["sh"] * p["px"])
                trades.append((c / p["px"], t - p["t"], "手じまい"))
                del active[s]

        # 恩株の上場廃止は現金に
        for s in list(onkabu):
            if day > data[s]["date"][-1]:
                c = data[s]["c"][-1]
                cash += onkabu[s] * c * (1 - COST)   # 恩株の簿価はほぼ0なので、ここでは税を引く
                cash -= onkabu[s] * c * TAX
                del onkabu[s]

        # 3) 合図（その日の終値で判定し、翌日買う）
        free = SLOTS - len(active)
        if free > 0 and month_cands:
            hits = []
            for s in month_cands:
                if s in active:
                    continue
                k = pos[s].get(day)
                if k is not None and k >= 252 and dip(s, k):
                    hits.append(s)
            rnd.shuffle(hits)
            pending = hits[:free]

        def val(s, sh):
            k = pos[s].get(day)
            return sh * (data[s]["c"][k] if k is not None else data[s]["c"][-1])
        eq = cash + sum(val(s, p["sh"]) for s, p in active.items()) + sum(val(s, sh) for s, sh in onkabu.items())
        curve.append(eq)
        cash_share.append(cash / eq if eq > 0 else 0)
    return curve, trades, n_onk, onkabu, active, st.mean(cash_share)


def metrics(curve, days):
    yrs = (dt.date.fromisoformat(days[-1]) - dt.date.fromisoformat(days[0])).days / 365.25
    peak = mdd = 0
    for v in curve:
        peak = max(peak, v)
        mdd = max(mdd, 1 - v / peak)
    return curve[-1], (curve[-1] / curve[0]) ** (1 / yrs) - 1, mdd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default=DEFAULT_CACHE)
    ap.add_argument("--out")
    ap.add_argument("--summary")
    ap.add_argument("--seeds", type=int, default=30)
    a = ap.parse_args()

    recs, entries = bf.build(a, all_months=True)
    spy = load_prices(a.cache, "SPY")
    syms = {x["s"] for x in recs}
    data = {s: load_prices(a.cache, s) for s in syms}
    start = entries[0]
    days = [d for d in spy["date"] if d >= start]
    dips = make_dips(data, spy)
    spy_curve = [CAPITAL * spy["c"][spy["date"].index(d)] / spy["c"][spy["date"].index(start)] for d in days]
    spy_end, spy_cagr, spy_mdd = metrics(spy_curve, days)

    out = []
    w = out.append
    w("---\ntype: backtest\ntitle: 資金6,000ドル・4銘柄で、下がったときに買う恩株の再現\n"
      f"created: {dt.date.today().isoformat()}\nscript: tools/backtest_onkabu_portfolio.py\n---\n")
    w("# 資金6,000ドル・4銘柄で、下がったときに買う恩株の再現\n")
    if a.summary and os.path.exists(a.summary):
        w(open(a.summary).read())
    w("## 前提\n")
    w(f"- 期間: {days[0]}〜{days[-1]}（約{(len(days) / 252):.1f}年）。最初の資金 {CAPITAL:,.0f}ドル、枠は{SLOTS}つ（恩株になった株は枠から外れる）")
    w("- 候補は毎月の最初の取引日に、その時点で分かる数値だけで決める（売上の伸びはSECへの提出日から。時価総額の順位・値動きの大きさはS&P500の構成銘柄の中で）")
    w("- 合図が出た日の終値で判定し、**翌日の寄り付き**で買う。1回に買う金額は（現金＋持っている株の買値の合計）÷4")
    w("- 終値が買値の2倍になったら、その終値で55.7%を売る（税20.315%を引いて元本が戻る割合）。残りは恩株として最後まで持つ")
    w(f"- 売買コストは片道{COST:.1%}。利益の出た売りに20.315%の税（損失との通算はしない＝少し厳しめ）。最後に持っている株は売らずに評価（SPYも同じ）")
    w("- 待っている間の現金は0%。同じ日に合図が枠より多いときはランダムに選び、順番を変えて"
      f"{a.seeds}回回した中央値（かっこ内は下位10%〜上位10%）")
    w("- 株価は配当込み。上場廃止になった銘柄はデータが取れず数に入らない（前の調査と同じ偏り）")
    w(f"- **比べる相手（SPYを最初に{CAPITAL:,.0f}ドル買って持ち続ける）**: 最後 {spy_end:,.0f}ドル、年率 {spy_cagr:.1%}、最大下落率 {spy_mdd:.1%}\n")

    for cname, cfn in CANDIDATES:
        cand_by_month = {}
        for x in recs:
            if cfn(x["f"]):
                cand_by_month.setdefault(x["d"][:7], []).append(x["s"])
        avg = st.mean(len(v) for v in cand_by_month.values())
        w(f"## 候補: {cname}（1カ月の候補 平均{avg:.0f}銘柄）\n")
        for ename, stop, maxd in EXITS:
            w(f"### 2倍にならない株: {ename}\n")
            w("| 買う合図 | 最後の資産（中央値） | 年率 | 最大下落率 | 恩株の数 | 2倍にならず売った・廃止（平均の値上がり） | "
              "現金の割合（平均） | SPYに勝った回数 |")
            w("|---|---|---|---|---|---|---|---|")
            for dname, dfn in dips.items():
                ends, cagrs, mdds, onks, others, cashr = [], [], [], [], [], []
                for seed in range(a.seeds):
                    curve, trades, n_onk, onk, act, cs = simulate(data, spy, days, cand_by_month, dfn, stop, maxd, seed)
                    e, c, m = metrics(curve, days)
                    ends.append(e); cagrs.append(c); mdds.append(m); onks.append(n_onk); cashr.append(cs)
                    oth = [r for r, _, k in trades if k != "2倍"]
                    others.append((len(oth), st.mean(oth) - 1 if oth else 0))
                q = lambda xs, p: sorted(xs)[int(p * (len(xs) - 1))]
                beat = sum(e > spy_end for e in ends)
                w(f"| {dname} | {st.median(ends):,.0f}ドル（{q(ends, 0.1):,.0f}〜{q(ends, 0.9):,.0f}） | {st.median(cagrs):.1%} | "
                  f"{st.median(mdds):.1%} | {st.median(onks):.0f} | {st.median(o[0] for o in others):.0f}件（{st.median(o[1] for o in others):+.0%}） | "
                  f"{st.median(cashr):.0%} | {beat}/{a.seeds} |")
            w("")
    text = "\n".join(out) + "\n"
    if a.out:
        os.makedirs(os.path.dirname(a.out), exist_ok=True)
        open(a.out, "w").write(text)
    print(text)


if __name__ == "__main__":
    main()
