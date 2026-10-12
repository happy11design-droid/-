#!/usr/bin/env python3
"""恩株ツールの合図（6カ月で+100%・52週高値・売上≧10%）で買い、上昇の流れが続く限り持つ形（恩株にはしない）と、
新分析ツールだけの形を、同じ資金（12,000ドル）・同じ税の計算で比べる。

使い方（Yahoo と SEC に接続できる環境で）:
  tools/backtest_lib.py fetch ; tools/backtest_onkabu.py fetch ; tools/backtest_onkabu_features.py fetch   # データ（初回だけ）
  tools/backtest_onkabu_combined.py newtrades                                                             # 新分析ツールの売買の一覧（数分）
  tools/backtest_onkabu_trend_hold.py run [--seeds 10] [--out FILE]

ユーザーの希望（2026-10-12）: 恩株化は無視。上昇の流れがあれば利確せず長めに持ち、上昇が落ち着いた合図で売る。4銘柄まで。2倍ETFも使う。

試す形（結果を見る前に決めた。売りの判定はすべて元の株の値段）:
  A 50日線割れで売る
  B 新高値V2の売り（50日線割れ・かぶせ線で全部、反転の合図で半分）
  C 保有中の最高値（終値）から−20%で売る
  D 保有中の最高値（終値）から−25%で売る
  参考 E 元の株が2倍で全部売る・189取引日で売る（今の恩株ツールの売り方から恩株をなくした形）
  参考 B・C を株だけ（2倍ETFを使わない）で
共通: 4銘柄・1銘柄＝（現金＋持ち株の買値）÷4、合図の翌日の寄り付きで買う、元の株の終値が買値の−30%で損切り（その日の終値で売る）、
      500取引日で打ち切り、同じ日の合図が空き枠より多いときは乱数（N通りの中央値）、待っている資金はQQQ。
      売りの合図（A〜D）は引けで判定し翌日の寄り付きで売る。
2倍ETF: `新分析ツール/2倍ETFの対応表.json` で目減り年15%未満の銘柄は、元の株の1日の値動きの2倍から実測の目減りを引いて再現する
       （新分析ツールの今の形と同じ作り方。多くの個別株2倍ETFは2022年以降にできたので、それ以前は仮の値動き。銘柄の一覧は後知恵を含む）。
税: 売って確定した損益を暦年ごとに通算し、年末に利益の20.315%（損失の繰越なし）。最後に持っている株・QQQには税をかけない
    （backtest_onkabu_combined.py と同じ）。売買コスト片道0.1%。
新分析ツールだけ: backtest_onkabu_combined.py の run（mode="pool", use_dbl=False, 待っている資金はQQQ、今の形）を資金12,000ドルで。
"""
import argparse
import datetime as dt
import json
import os
import pickle
import random
import statistics as st
import sys
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backtest_lib import DEFAULT_CACHE, load_prices, sma
import backtest_onkabu_search as bos
import backtest_onkabu_early_exit as bee

TAX = 0.20315
COST = 0.001
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SIG = bee.SIG
CONDS = bos.CONDS

VARIANTS = [
    ("A 50日線割れで売る（2倍ETF）", {"exit": "ma50"}),
    ("B 新高値V2の売り（50日線割れ・かぶせ線・反転で半分、2倍ETF）", {"exit": "v2"}),
    ("C 最高値から−20%で売る（2倍ETF）", {"exit": "trail", "trail": 0.20}),
    ("D 最高値から−25%で売る（2倍ETF）", {"exit": "trail", "trail": 0.25}),
    ("参考 E 2倍で全部売る・189日（2倍ETF）", {"exit": "x2", "T": 189}),
    ("参考 B を株だけで", {"exit": "v2", "etf": False}),
    ("参考 C を株だけで", {"exit": "trail", "trail": 0.20, "etf": False}),
]
BASE = {"exit": "ma50", "trail": None, "T": 500, "stop": 0.30, "etf": True}


def lev_table():
    tab = json.load(open(os.path.join(ROOT, "新分析ツール", "2倍ETFの対応表.json"), encoding="utf-8"))
    return {u: -x["drag"] / 252 for u, x in tab.items() if isinstance(x, dict) and "drag" in x and -x["drag"] < 0.15}


def simulate(feats, flags, days, sbd, cfg, lev, capital, qqq, seed, slots=4):
    rnd = random.Random(seed)
    pos = {s: {d: k for k, d in enumerate(f["date"])} for s, f in feats.items()}
    cash = capital
    act = {}           # sym -> dict(v, cost, upx, peak, t, half, fee, d0)
    pend_buy, pend_sell = [], {}
    realized, curve, log = 0.0, [], []
    full_days = 0
    year = days[0][:4]

    def ux(s, d, key="c"):
        k = pos[s].get(d)
        return None if k is None else feats[s][key][k]

    def close_out(s, d, frac, why, at_value):
        nonlocal cash, realized
        p = act[s]
        proceeds = at_value * frac * (1 - COST)
        basis = p["cost"] * frac
        cash += proceeds
        realized += proceeds - basis
        p["real"] += proceeds
        p["v"] *= 1 - frac
        p["cost"] -= basis
        if frac >= 1.0:
            log.append({"sym": s, "d0": p["d0"], "d1": d, "why": why, "cost0": p["cost0"], "real": p["real"],
                        "hold": days.index(d) - p["t"], "etf": p["fee"] is not None})
            del act[s]
        else:
            p["half"] = True
            log.append({"partial": True, "why": why + "（半分）"})

    for t, d in enumerate(days):
        # 年が変わったら前の年の税を払う
        if d[:4] != year:
            cash -= TAX * max(0.0, realized)
            realized, year = 0.0, d[:4]
        if t > 0 and cash > 0 and d in qqq and days[t - 1] in qqq:
            cash *= qqq[d] / qqq[days[t - 1]]
        # 寄り付き: 持ち株の値を寄り付きまで動かす → 売り → 買い
        for s, p in act.items():
            o, pc = ux(s, d, "o"), p["last"]
            if o is not None and pc:
                m = (1 + p["lev"] * (o / pc - 1))
                p["v"] = max(0.0, p["v"] * m)
                p["last"] = o
        for s, (frac, why) in list(pend_sell.items()):
            if s in act and ux(s, d, "o") is not None:
                close_out(s, d, frac, why, act[s]["v"])
        pend_sell = {}
        for s in pend_buy:
            o = ux(s, d, "o")
            if o is None or s in act or len(act) >= slots:
                continue
            basis = cash + sum(p["cost"] for p in act.values())
            a = min(cash, basis / slots)
            if a < 50:
                continue
            use_etf = cfg["etf"] and s in lev
            act[s] = {"v": a * (1 - COST), "cost": a, "cost0": a, "real": 0.0, "upx": o, "peak": o, "t": t, "half": False,
                      "fee": lev[s] if use_etf else None, "lev": 2 if use_etf else 1, "last": o, "d0": d}
            cash -= a
        pend_buy = []
        # 引け: 値を引けまで動かす → 損切り・2倍・期限（引けで売る）→ 売りの合図（翌日の寄り付き）
        for s in list(act):
            p = act[s]
            c = ux(s, d)
            if c is None:
                if d > feats[s]["date"][-1]:
                    close_out(s, d, 1.0, "上場廃止", p["v"])
                continue
            p["v"] = max(0.0, p["v"] * (1 + p["lev"] * (c / p["last"] - 1)) * (1 - (p["fee"] or 0.0)))
            p["last"] = c
            p["peak"] = max(p["peak"], c)
            k = pos[s][d]
            fl = flags[s]
            if c <= p["upx"] * (1 - cfg["stop"]):
                close_out(s, d, 1.0, "損切り", p["v"])
            elif cfg["exit"] == "x2" and c >= 2 * p["upx"]:
                close_out(s, d, 1.0, "2倍", p["v"])
            elif t - p["t"] >= cfg["T"]:
                close_out(s, d, 1.0, "期限", p["v"])
            elif cfg["exit"] == "ma50" and fl["ma50"][k]:
                pend_sell[s] = (1.0, "50日線割れ")
            elif cfg["exit"] == "v2":
                if fl["ma50"][k]:
                    pend_sell[s] = (1.0, "50日線割れ")
                elif fl["dc"][k]:
                    pend_sell[s] = (1.0, "かぶせ線")
                elif fl["rev"][k] and not p["half"]:
                    pend_sell[s] = (0.5, "反転の合図")
            elif cfg["exit"] == "trail" and c <= p["peak"] * (1 - cfg["trail"]):
                pend_sell[s] = (1.0, f"最高値から−{cfg['trail'] * 100:.0f}%")
        # 合図 → 翌日の寄り付きで買う
        today = [s for s in sbd.get(d, ()) if s not in act]
        rnd.shuffle(today)
        free = slots - len(act) + sum(1 for fr, _ in pend_sell.values() if fr >= 1.0)
        pend_buy = today[:max(0, free)]
        if len(act) >= slots:
            full_days += 1
        curve.append(cash + sum(p["v"] for p in act.values()))
    return {"curve": curve, "log": log, "full": full_days / len(days)}


def episodes(sbd, days):
    """合図の回数: 同じ銘柄で直前20取引日に合図がなければ1回と数える（年ごと）"""
    last, per_year = {}, {}
    for t, d in enumerate(days):
        for s in sbd.get(d, ()):
            if s not in last or t - last[s] > 20:
                per_year[d[:4]] = per_year.get(d[:4], 0) + 1
            last[s] = t
    return per_year


G = {}


def _run(job):
    name, cfg, seeds, capital = job
    out = []
    for cname, a, b, ex in CONDS:
        days = [d for d in G["spy"]["date"] if a <= d <= b]
        cs, ms, fulls, logs = [], [], [], None
        for seed in range(seeds):
            r = simulate(G["feats"], G["flags"], days, G["sbd"][ex], cfg, G["lev"], capital, G["qqq"], seed)
            c, m = bee.metrics(r["curve"], days)
            cs.append(c); ms.append(m); fulls.append(r["full"])
            if seed == 0:
                logs = r["log"]
        out.append({"cond": cname, "cagr": st.median(cs), "mdd": st.median(ms), "full": st.median(fulls), "log": logs})
    return name, out


def newtool_only(feats, spy, qqq, capital, seeds):
    import backtest_onkabu_combined as bc
    if not os.path.exists(bc.NEW_PKL):
        return None
    nt = pickle.load(open(bc.NEW_PKL, "rb"))
    trades, has2x = bc.upgrade_trades(nt["trades"])
    tab = json.load(open(os.path.join(ROOT, "新分析ツール", "2倍ETFの対応表.json"), encoding="utf-8"))
    lev_info = {u: (2, -x["drag"] / 252) for u, x in tab.items() if isinstance(x, dict) and "drag" in x and u in has2x}
    out = []
    for cname, a, b, ex in CONDS:
        days = [d for d in spy["date"] if a <= d <= b]
        nts = [x for x in trades if a <= x["in"] and x["sym"] not in ex]
        res = []
        for seed in range(seeds):
            curve, _, _ = bc.run(feats, nts, nt["ind"], days, {}, mode="pool", use_dbl=False, seed=seed, cash_px=qqq,
                                 capital=capital, lev_info=lev_info)
            res.append(bc.metrics(curve, days))
        out.append((st.median(r[0] for r in res), st.median(r[1] for r in res)))
    return out


def cmd_run(a):
    members, spy, feats = bos.load_all(a.cache)
    qd = load_prices(a.cache, "QQQ")
    qqq = dict(zip(qd["date"], qd["c"]))
    bos._init(feats, spy, qqq)
    sbd = {ex: bos.sig_by_day(SIG, ex) for ex in {c[3] for c in CONDS}}
    syms = sorted({s for m in sbd.values() for lst in m.values() for s in lst})
    print(f"合図の出た銘柄 {len(syms)}。売りの合図を計算中…", file=sys.stderr)
    with Pool() as pool:
        res = pool.starmap(bee.exit_flags, [(s, a.cache) for s in syms])
    flags = {s: fl for s, _, fl in res}
    lev = lev_table()
    G.update(feats=feats, flags=flags, spy=spy, qqq=qqq, sbd=sbd, lev=lev)
    jobs = [(n, {**BASE, **v}, a.seeds, a.capital) for n, v in VARIANTS]
    with Pool() as pool:
        results = dict(pool.map(_run, jobs))
    print("新分析ツールだけを計算中…", file=sys.stderr)
    nto = newtool_only(feats, spy, qqq, a.capital, a.seeds)

    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: 恩株ツールの合図で買い、上昇の流れが続く限り持つ（4銘柄・2倍ETF）\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_onkabu_trend_hold.py\n---\n")
    w("# 恩株ツールの合図で買い、上昇の流れが続く限り持つ（4銘柄・2倍ETF）と新分析ツールの比較\n")
    w("## 前提\n")
    w(f"- 資金 {a.capital:,.0f}ドル・4銘柄（1銘柄＝資金÷4）。合図: {bee.ol.describe(SIG)}。翌日の寄り付きで買う。恩株にはしない")
    w(f"- 2倍ETF: 対応表で目減り年15%未満の{len(lev)}銘柄（{', '.join(sorted(lev))}）。売りの判定は元の株の値段")
    w("- 損切り: 元の株の終値が買値の−30%。500取引日で打ち切り。売りの合図は引けで判定し翌日の寄り付き")
    w(f"- 税は暦年で通算して20.315%（損失の繰越なし）。売買コスト片道0.1%。待っている資金はQQQ。乱数{a.seeds}通りの中央値")
    w("- 新分析ツールだけ: 今の採用ルール・今の形（2倍ETF・50日線の傾きの順）、同じ資金・同じ税の計算\n")
    w("## 結果（年率（含み損込みの最大下落率）・4枠が埋まっていた日の割合）\n")
    w("| 形 | " + " | ".join(c[0] for c in CONDS) + " |")
    w("|---|" + "---|" * len(CONDS))
    for lab, px in (("（比べる相手）SPYを持ち続ける", spy), ("（比べる相手）QQQを持ち続ける", qd)):
        w(f"| {lab} | " + " | ".join(f"{bee.bench(px, c[1], c[2]) * 100:.1f}%" for c in CONDS) + " |")
    if nto:
        w("| **新分析ツールだけ（今の形）** | " + " | ".join(f"{c * 100:.1f}%（{m * 100:.0f}%）" for c, m in nto) + " |")
    else:
        w("| 新分析ツールだけ | （先に `backtest_onkabu_combined.py newtrades` が必要） |" + " |" * (len(CONDS) - 1))
    for n, _ in VARIANTS:
        w(f"| {n} | " + " | ".join(f"{r['cagr'] * 100:.1f}%（{r['mdd'] * 100:.0f}%）・満{r['full'] * 100:.0f}%" for r in results[n]) + " |")

    w("\n## 合図の回数（同じ銘柄で20取引日あいたら1回と数える。NVDAを含む）\n")
    days_all = [d for d in spy["date"] if d >= "2015-01-02"]
    ep = episodes(sbd[()], days_all)
    w("| " + " | ".join(sorted(ep)) + " | 合計 |")
    w("|" + "---|" * (len(ep) + 1))
    w("| " + " | ".join(str(ep[y]) for y in sorted(ep)) + f" | {sum(ep.values())} |")

    w("\n## 売買の中身（2015年〜 NVDAを除く・乱数1通り）\n")
    w("| 形 | 買った回数 | 1回平均 | 勝率 | 保有日数の中央値 | 売った理由 |")
    w("|---|---|---|---|---|---|")
    for n, _ in VARIANTS:
        lg_all = results[n][2]["log"]
        lg = [x for x in lg_all if not x.get("partial")]
        if not lg:
            continue
        rets = [x["real"] / x["cost0"] - 1 for x in lg]
        why = {}
        for x in lg_all:
            why[x["why"]] = why.get(x["why"], 0) + 1
        w(f"| {n} | {len(lg)} | {st.mean(rets) * 100:+.1f}% | {sum(r > 0 for r in rets) / len(rets) * 100:.0f}% | "
          f"{st.median(x['hold'] for x in lg):.0f}日 | " + "・".join(f"{k}{v}" for k, v in sorted(why.items(), key=lambda kv: -kv[1])) + " |")
    txt = "\n".join(L) + "\n"
    if a.out:
        open(a.out, "w").write(txt)
    print(txt)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run"])
    ap.add_argument("--cache", default=DEFAULT_CACHE)
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--capital", type=float, default=12000.0)
    ap.add_argument("--out")
    cmd_run(ap.parse_args())


if __name__ == "__main__":
    main()
