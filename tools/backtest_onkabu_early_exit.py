#!/usr/bin/env python3
"""恩株ツールの合図（6カ月で+100%・52週高値・売上≧10%）で買い、2倍を待つ前に早めに利確したらどうなるか。
早めの売りは、新分析ツールの順張り（ミネルヴィニ・新高値V2）・逆張りで使っている売りの合図を当てる。

使い方（Yahoo と SEC に接続できる環境で）:
  tools/backtest_lib.py fetch ; tools/backtest_onkabu.py fetch ; tools/backtest_onkabu_features.py fetch   # データ（初回だけ）
  tools/backtest_onkabu_early_exit.py run [--seeds 10] [--slots 1] [--capital 4500] [--out FILE]

試す形は、結果を見る前に決めた13通り（たくさんの形から選ばないため）:
  今のルール      : 2倍で55.7%を売って残りは恩株・−30%で損切り・189取引日で売る（`恩株ツール/採用ルール.json`）
  期限を短く      : 126日・63日
  新分析の売り    : かぶせ線で全部／反転の合図で半分／50日線割れで全部／出来高2倍の大陰線で全部／
                    新高値V2の売りをそのまま（50日線割れ・かぶせ線で全部・反転の合図で半分）／それに損切り15%
  決まった利確    : +30%・+50%で全部売る
  組み合わせ      : 反転の合図で半分＋期限126日
どの形も「2倍で55.7%を売って恩株」「−30%の損切り（15%の形を除く）」「期限」は残す。

決まり:
  - 合図はその日の終値で判定し、翌日の寄り付きで買う。1回に買う金額は（現金＋持っている株の買値）÷枠
  - 2倍・損切り・期限・決まった利確は、その日の終値で売る（onkabu_sim.py と同じ）
  - 新分析ツールの売りの合図（かぶせ線・反転の合図・50日線割れ・大陰線）は、引けで判定して翌日の寄り付きで売る（新分析ツールと同じ）
  - 半分売りは1回だけ。残りは2倍（残りの55.7%を売って恩株）・損切り・期限・全部売りの合図で売る
  - 売買コスト片道0.1%。利益に20.315%の税（売るたび。損との通算はしない＝onkabu_sim.py と同じ）
  - 待っている現金は QQQ に置く。新分析ツールとは資金を分けるので（2026-10-12 ユーザー決定）、恩株ツールだけを計算する
  - 合図の定義は backtest_exit_signals.py（かぶせ線）・backtest_exit_combo.py（反転の合図 c1）・backtest_rebuy.py（大陰線）と同じ
"""
import argparse
import datetime as dt
import json
import os
import random
import statistics as st
import sys
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backtest_lib import DEFAULT_CACHE, load_prices, sma
import backtest_onkabu_search as bos
import onkabu_lib as ol

TAX = 0.20315
SELL_AT_2X = 1 / (2 - TAX)
COST = 0.001
RULE = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "恩株ツール", "採用ルール.json")))
SIG = {**RULE["合図"], "mom": tuple(RULE["合図"]["mom"])}
BASE = {"T": RULE["売買"]["期限"], "stop": RULE["売買"]["損切り"], "full": (), "half": (), "tp": None}

VARIANTS = [
    ("今のルール（2倍で恩株・−30%・189日）", {}),
    ("期限を126日（6カ月）", {"T": 126}),
    ("期限を63日（3カ月）", {"T": 63}),
    ("かぶせ線で全部売る", {"full": ("dc",)}),
    ("反転の合図で半分売る", {"half": ("rev",)}),
    ("50日線割れで全部売る", {"full": ("ma50",)}),
    ("出来高2倍の大陰線で全部売る", {"full": ("bear",)}),
    ("新高値V2の売り（50日線割れ・かぶせ線で全部・反転の合図で半分）", {"full": ("ma50", "dc"), "half": ("rev",)}),
    ("新高値V2の売り＋損切り15%", {"full": ("ma50", "dc"), "half": ("rev",), "stop": 0.15}),
    ("+30%で全部売る", {"tp": 0.30}),
    ("+50%で全部売る", {"tp": 0.50}),
    ("反転の合図で半分＋期限126日", {"half": ("rev",), "T": 126}),
    ("かぶせ線で全部＋反転の合図で半分", {"full": ("dc",), "half": ("rev",)}),
]
NAMES = {"dc": "かぶせ線", "rev": "反転の合図", "ma50": "50日線割れ", "bear": "大陰線"}


# ---------- 売りの合図（日ごとの True/False） ----------

def _safe(f, s, j):
    try:
        return bool(f(s, j))
    except (TypeError, ValueError, IndexError, ZeroDivisionError):
        return False


def big_bear(s, j):
    """出来高2倍の大陰線（backtest_rebuy.py と同じ定義）"""
    o, h, l, c, v = s["o"], s["h"], s["l"], s["c"], s["v"]
    a, v50 = s["atr14"][j - 1], s["vol50"][j - 1]
    return a is not None and v50 and h[j] > l[j] and o[j] - c[j] >= 1.5 * a and (c[j] - l[j]) / (h[j] - l[j]) <= 0.25 and v[j] >= 2 * v50


def exit_flags(sym, cache):
    import backtest_exit_combo as xc
    import backtest_exit_signals as xs
    s = load_prices(cache, sym)
    xs.prep(s)
    v = s["v"]
    s["vol50"] = [None] + sma(v, 50)[:-1]          # 前日までの50日平均出来高（backtest_swing.py と同じ）
    m50 = sma(s["c"], 50)
    n = len(s["c"])
    out = {k: np.zeros(n, bool) for k in NAMES}
    for j in range(30, n):
        out["dc"][j] = _safe(xs.dark_cloud, s, j)
        out["rev"][j] = _safe(xc.c1, s, j)
        out["bear"][j] = _safe(big_bear, s, j)
        out["ma50"][j] = m50[j] is not None and s["c"][j] < m50[j]
    return sym, s["date"], out


# ---------- 資金の再現 ----------

def simulate(feats, flags, days, sbd, cfg, slots, capital, cash_px, seed):
    rnd = random.Random(seed)
    pos = {s: {d: k for k, d in enumerate(f["date"])} for s, f in feats.items()}
    cash = capital
    active, onk, buys, sells = {}, {}, [], {}
    curve, log = [], []
    n_onk = 0

    def px_of(s, d, key="c"):
        k = pos[s].get(d)
        return None if k is None else feats[s][key][k]

    def sell(s, d, px, why, frac=1.0, to_onk=False):
        nonlocal cash
        p = active[s]
        sh = p["sh"] * frac
        proceeds = sh * px * (1 - COST)
        cash += proceeds - TAX * max(0.0, proceeds - sh * p["px"])
        p["real"] += proceeds
        p["sh"] -= sh
        if to_onk:
            onk[s] = onk.get(s, 0.0) + p["sh"]
            p["onk_sh"], p["onk_val"] = p["sh"], p["sh"] * px
            p["sh"] = 0.0
        if p["sh"] <= 1e-12 or frac >= 1.0:
            log.append({"sym": s, "d0": p["d0"], "d1": d, "why": why, "cost": p["cost"], "real": p["real"],
                        "onk_sh": p.get("onk_sh", 0.0), "onk_val": p.get("onk_val", 0.0), "hold": days.index(d) - p["t"]})
            del active[s]
        else:
            log.append({"sym": s, "d0": p["d0"], "d1": d, "why": why + "（半分）", "partial": True})

    for t, d in enumerate(days):
        if cash_px and t > 0 and cash > 0 and d in cash_px and days[t - 1] in cash_px:
            cash *= cash_px[d] / cash_px[days[t - 1]]
        # 1) 寄り付き: 前日の引けで決まった売り → 買い
        for s, (frac, why) in list(sells.items()):
            o = px_of(s, d, "o")
            if s in active and o is not None:
                sell(s, d, o, why, frac)
                if s in active:
                    active[s]["half_done"] = True
        sells = {}
        for s in buys:
            o = px_of(s, d, "o")
            if o is None or s in active or len(active) >= slots:
                continue
            basis = cash + sum(p["cost"] for p in active.values())
            a = min(cash, basis / slots)
            if a < 50:
                continue
            bp = o * (1 + COST)
            active[s] = {"sh": a / bp, "px": bp, "t": t, "d0": d, "cost": a, "real": 0.0, "half_done": False}
            cash -= a
        buys = []
        # 2) 引け: 2倍・損切り・期限・利確（終値で売る）、新分析の合図（翌日の寄り付きで売る）
        for s in list(active):
            p = active[s]
            c = px_of(s, d)
            if c is None:
                if d > feats[s]["date"][-1]:
                    sell(s, d, feats[s]["c"][-1], "上場廃止")
                continue
            if c >= 2 * p["px"]:
                sell(s, d, c, "2倍", SELL_AT_2X, to_onk=True)
                n_onk += 1
            elif c <= p["px"] * (1 - cfg["stop"]):
                sell(s, d, c, "損切り")
            elif t - p["t"] >= cfg["T"]:
                sell(s, d, c, "期限")
            elif cfg["tp"] is not None and c >= p["px"] * (1 + cfg["tp"]):
                sell(s, d, c, f"+{cfg['tp'] * 100:.0f}%で利確")
            else:
                k = pos[s][d]
                hit_full = [x for x in cfg["full"] if flags[s][x][k]]
                hit_half = [x for x in cfg["half"] if flags[s][x][k]] if not p["half_done"] else []
                if hit_full:
                    sells[s] = (1.0, NAMES[hit_full[0]])
                elif hit_half:
                    sells[s] = (0.5, NAMES[hit_half[0]])
        for s in list(onk):
            if d > feats[s]["date"][-1]:
                cash += onk[s] * feats[s]["c"][-1] * (1 - COST) * (1 - TAX)
                del onk[s]
        # 3) 合図（翌日の寄り付きで買う）
        today = [s for s in sbd.get(d, ()) if s not in active]
        rnd.shuffle(today)
        free = slots - len(active) + sum(1 for s, (fr, _) in sells.items() if fr >= 1.0)
        buys = today[:max(0, free)]
        eq = cash
        for s, p in active.items():
            c = px_of(s, d)
            eq += p["sh"] * (c if c is not None else feats[s]["c"][-1])
        for s, sh in onk.items():
            c = px_of(s, d)
            eq += sh * (c if c is not None else feats[s]["c"][-1])
        curve.append(eq)
    return {"curve": curve, "n_onk": n_onk, "log": log}


def metrics(curve, days):
    yrs = (dt.date.fromisoformat(days[-1]) - dt.date.fromisoformat(days[0])).days / 365.25
    peak = mdd = 0.0
    for v in curve:
        peak = max(peak, v)
        mdd = max(mdd, 1 - v / peak)
    return (curve[-1] / curve[0]) ** (1 / yrs) - 1, mdd


G = {}


def _run(job):
    name, cfg, seeds, slots, capital = job
    out = []
    for cname, a, b, ex in bos.CONDS:
        days = [d for d in G["spy"]["date"] if a <= d <= b]
        sbd = G["sbd"][ex]
        cs, ms, ns, logs = [], [], [], []
        for seed in range(seeds):
            r = simulate(G["feats"], G["flags"], days, sbd, cfg, slots, capital, G["qqq"], seed)
            c, m = metrics(r["curve"], days)
            cs.append(c); ms.append(m); ns.append(r["n_onk"])
            if seed == 0:
                logs = r["log"]
        out.append({"cond": cname, "cagr": st.median(cs), "mdd": st.median(ms), "onk": st.median(ns), "log": logs})
    return name, out


def bench(px, a, b):
    ds = [d for d in px["date"] if a <= d <= b]
    k0, k1 = px["date"].index(ds[0]), px["date"].index(ds[-1])
    yrs = (dt.date.fromisoformat(ds[-1]) - dt.date.fromisoformat(ds[0])).days / 365.25
    return (px["c"][k1] / px["c"][k0]) ** (1 / yrs) - 1


def cmd_run(a):
    members, spy, feats = bos.load_all(a.cache)
    qd = load_prices(a.cache, "QQQ")
    bos._init(feats, spy, dict(zip(qd["date"], qd["c"])))
    sbd = {ex: bos.sig_by_day(SIG, ex) for ex in {c[3] for c in bos.CONDS}}
    syms = sorted({s for m in sbd.values() for lst in m.values() for s in lst})
    print(f"合図の出た銘柄 {len(syms)}。売りの合図を計算中…", file=sys.stderr)
    with Pool() as pool:
        res = pool.starmap(exit_flags, [(s, a.cache) for s in syms])
    flags = {}
    for s, dates, fl in res:
        assert dates == list(feats[s]["date"]), s
        flags[s] = fl
    G.update(feats=feats, flags=flags, spy=spy, qqq=dict(zip(qd["date"], qd["c"])), sbd=sbd)
    jobs = [(n, {**BASE, **v}, a.seeds, a.slots, a.capital) for n, v in VARIANTS]
    with Pool() as pool:
        results = dict(pool.map(_run, jobs))

    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: 恩株ツールの合図で買い、新分析ツールの売りで早めに利確する\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_onkabu_early_exit.py\n---\n")
    w("# 恩株ツールの合図で買い、新分析ツールの売りで早めに利確する\n")
    w("## 前提\n")
    w(f"- 合図: {ol.describe(SIG)}（`恩株ツール/採用ルール.json`）。翌日の寄り付きで買う")
    w(f"- 資金 {a.capital:,.0f}ドル・{a.slots}銘柄。待っている現金はQQQ。恩株ツールだけを計算（新分析ツールとは資金を分ける）")
    w("- どの形も「2倍で55.7%を売って恩株」「損切り（−30%、指定した形は−15%）」「期限」は残す。新分析ツールの売りの合図は引けで判定して翌日の寄り付き")
    w(f"- 税は売るたびに20.315%（損との通算なし）。売買コスト片道0.1%。同じ日の合図が枠より多いときは乱数で選び、{a.seeds}通りの中央値\n")
    w("## 結果（年率（含み損込みの最大下落率・恩株の数））\n")
    w("| 形 | " + " | ".join(c[0] for c in bos.CONDS) + " |")
    w("|---|" + "---|" * len(bos.CONDS))
    qp = load_prices(a.cache, "QQQ")
    for lab, px in (("（比べる相手）SPYを持ち続ける", spy), ("（比べる相手）QQQを持ち続ける", qp)):
        w(f"| {lab} | " + " | ".join(f"{bench(px, c[1], c[2]) * 100:.1f}%" for c in bos.CONDS) + " |")
    for n, _ in VARIANTS:
        w(f"| {n} | " + " | ".join(f"{r['cagr'] * 100:.1f}%（{r['mdd'] * 100:.0f}%・恩株{r['onk']:.0f}）" for r in results[n]) + " |")
    w("\n## 売買の中身（2015年〜 NVDAを除く・乱数1通り）\n")
    w("| 形 | 買った回数 | 1回平均（恩株は2倍の時点の値で計算） | 保有日数の中央値 | 売った理由 |")
    w("|---|---|---|---|---|")
    for n, _ in VARIANTS:
        lg = [x for x in results[n][2]["log"] if not x.get("partial")]
        if not lg:
            w(f"| {n} | 0 | ― | ― | ― |")
            continue
        # 恩株にした分は、2倍で売った日の終値で評価する（税・コスト前）
        rets = [(x["real"] + x["onk_val"]) / x["cost"] - 1 for x in lg]
        why = {}
        for x in results[n][2]["log"]:
            why[x["why"]] = why.get(x["why"], 0) + 1
        w(f"| {n} | {len(lg)} | {st.mean(rets) * 100:+.1f}% | {st.median(x['hold'] for x in lg):.0f}日 | "
          + "・".join(f"{k}{v}" for k, v in sorted(why.items(), key=lambda kv: -kv[1])) + " |")
    txt = "\n".join(L) + "\n"
    if a.out:
        open(a.out, "w").write(txt)
    print(txt)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run"])
    ap.add_argument("--cache", default=DEFAULT_CACHE)
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--slots", type=int, default=RULE["売買"]["枠"])
    ap.add_argument("--capital", type=float, default=RULE["売買"]["資金"])
    ap.add_argument("--out")
    a = ap.parse_args()
    cmd_run(a)


if __name__ == "__main__":
    main()
