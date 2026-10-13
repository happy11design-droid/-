#!/usr/bin/env python3
"""恩株ツールの調査8: もっと早く2倍になる合図を探す（後知恵を避けるため、2020年までで選び、2021年以降で確かめる）

使い方:
  tools/backtest_onkabu_search.py signals [--out FILE]

毎週の最後の取引日に、その日のS&P500の構成銘柄で、合図の組み合わせ（720通り）ごとに数える:
  - 3カ月（63取引日）・6カ月（126取引日）以内に終値で2倍になった割合
  - 「2倍で手じまい、ならなければ6カ月後に手じまい」の1トレードの平均と、同じ期間のSPYとの差
選ぶ期間（2014年6月〜2020年12月）で良かった組み合わせを、確かめる期間（2021年1月〜）でも数える。
"""
import argparse
import datetime as dt
import itertools
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backtest_lib import DEFAULT_CACHE, load_prices, load_members, is_member, sma
import onkabu_lib as ol

SPLIT = "2021-01-01"
MOMS = [("r21", 0.3), ("r21", 0.5), ("r63", 0.3), ("r63", 0.5), ("r63", 0.8),
        ("r126", 0.5), ("r126", 0.75), ("r126", 1.0), ("r126", 1.5)]
HIS = ["nh", "near10", "pull", None]
REVS = [None, 0.1, 0.2, 0.3, "acc"]
EXTRAS = [None, "vr", "gap", "spy"]


def grid():
    for m, h, r, e in itertools.product(MOMS, HIS, REVS, EXTRAS):
        yield {"mom": m, "hi": h, "rev": r, "extra": e}


def load_all(cache=DEFAULT_CACHE, exclude=()):
    """{sym: 特徴} と SPY。特徴には outcomes（t2）も入れる"""
    members = load_members(cache)
    spy = load_prices(cache, "SPY")
    sc = np.array(spy["c"])
    ma = ol.sma(sc, 200)
    spy_up = {d: bool(sc[k] > ma[k]) for k, d in enumerate(spy["date"]) if not np.isnan(ma[k])}
    feats = {}
    for s in members:
        if s in exclude:
            continue
        d = load_prices(cache, s)
        if not d or len(d["c"]) < 300:
            continue
        f = ol.features(d, ol.load_rev_rows(s, cache), spy_up)
        f["t2"] = ol.outcomes(f["c"])
        f["member"] = np.array([is_member(members[s], x) for x in d["date"]])
        feats[s] = f
    return members, spy, feats


def weekly_events(spy, feats):
    """週の最後の取引日・構成銘柄の日を集めて、特徴を1本の配列にまとめる"""
    weeks = set()
    for k, d in enumerate(spy["date"]):
        if d >= "2014-06-01" and k + 1 < len(spy["date"]) and \
                dt.date.fromisoformat(spy["date"][k + 1]).isocalendar()[1] != dt.date.fromisoformat(d).isocalendar()[1]:
            weeks.add(d)
    spy_pos = {d: k for k, d in enumerate(spy["date"])}
    sc = np.array(spy["c"])
    keys = ["r21", "r63", "r126", "hi52", "nh", "ma50", "dd20", "gap63", "vr", "rev", "racc", "spy_up"]
    cols = {k: [] for k in keys + ["t2", "v63", "v126", "spy126", "date", "sym"]}
    for s, f in feats.items():
        idx = [i for i, d in enumerate(f["date"]) if d in weeks and f["member"][i] and i >= 260]
        if not idx:
            continue
        idx = np.array(idx)
        for k in keys:
            cols[k].append(f[k][idx])
        cols["t2"].append(f["t2"][idx])
        cols["v63"].append(ol.trade_value(f["c"], f["t2"], 63)[idx])
        cols["v126"].append(ol.trade_value(f["c"], f["t2"], 126)[idx])
        sp = []
        for i in idx:
            k = spy_pos[f["date"][i]]
            sp.append(sc[k + 126] / sc[k] if k + 126 < len(sc) else np.nan)
        cols["spy126"].append(np.array(sp))
        cols["date"].append(np.array([f["date"][i] for i in idx]))
        cols["sym"].append(np.array([s] * len(idx)))
    return {k: np.concatenate(v) for k, v in cols.items()}


def stats(ev, m):
    ok = m & ~np.isnan(ev["v126"]) & ~np.isnan(ev["spy126"])
    n = int(ok.sum())
    if n == 0:
        return None
    t2 = ev["t2"][ok]
    return {"n": n, "syms": len(set(ev["sym"][ok])), "p63": float((t2 <= 63).mean()), "p126": float((t2 <= 126).mean()),
            "v126": float(ev["v126"][ok].mean() - 1), "ex126": float((ev["v126"][ok] - ev["spy126"][ok]).mean()),
            "days": float(np.median(t2[t2 <= 126])) if (t2 <= 126).any() else None}


def pct(x, d=1):
    return "―" if x is None else f"{x * 100:.{d}f}%"


def cmd_signals(a):
    members, spy, feats = load_all()
    ev = weekly_events(spy, feats)
    ins = ev["date"] < SPLIT
    oos = ~ins
    base_in, base_out = stats(ev, ins), stats(ev, oos)
    res = []
    for s in grid():
        m = ol.signal(ev, s)
        si, so = stats(ev, m & ins), stats(ev, m & oos)
        if si and si["n"] >= 30 and si["syms"] >= 10:
            res.append((s, si, so))
    out = []
    w = out.append
    w("---\ntype: backtest\ntitle: もっと早く2倍になる合図の探索\n"
      f"created: {dt.date.today().isoformat()}\nscript: tools/backtest_onkabu_search.py\n---\n")
    w("# もっと早く2倍になる合図の探索（2020年までで選び、2021年以降で確かめる）\n")
    if a.summary and os.path.exists(a.summary):
        w(open(a.summary).read())
    w("## 前提\n")
    w("- 毎週の最後の取引日に、その日のS&P500の構成銘柄を数える。合図の組み合わせは720通り（勢い9×高値4×売上5×その他4）")
    w(f"- **選ぶ期間**: 2014年6月〜2020年12月。**確かめる期間**: 2021年1月〜（6カ月後まで株価がある週）")
    w("- 「6カ月の平均」は、2倍になったら2倍で、ならなければ6カ月後の終値で手じまったときの1トレードの平均。「SPYとの差」は同じ6カ月のSPYとの差の平均")
    w("- 選ぶ期間で30件以上・10銘柄以上あった組み合わせだけを並べる。同じ上昇を何週も数えるので、件数ほど独立していない\n")
    w(f"- **合図なし**: 選ぶ期間 3カ月以内に2倍 {pct(base_in['p63'])}・6カ月以内 {pct(base_in['p126'])}・6カ月の平均 {pct(base_in['v126'])}（SPYとの差 {pct(base_in['ex126'])}）／"
      f"確かめる期間 {pct(base_out['p63'])}・{pct(base_out['p126'])}・{pct(base_out['v126'])}（{pct(base_out['ex126'])}）\n")
    head = ("| 合図 | 選ぶ期間 件数（銘柄） | 3カ月で2倍 | 6カ月で2倍 | 6カ月の平均（SPYとの差） | "
            "確かめる期間 件数（銘柄） | 3カ月で2倍 | 6カ月で2倍 | 6カ月の平均（SPYとの差） | 2倍までの日数（確かめる期間・中央値） |\n"
            "|---|---|---|---|---|---|---|---|---|---|")

    def line(s, si, so):
        if so:
            days = f"{so['days']:.0f}日" if so["days"] else "―"
            o = f"{so['n']}（{so['syms']}） | {pct(so['p63'])} | {pct(so['p126'])} | {pct(so['v126'])}（{pct(so['ex126'])}） | {days}"
        else:
            o = "0 | ― | ― | ― | ―"
        return f"| {ol.describe(s)} | {si['n']}（{si['syms']}） | {pct(si['p63'])} | {pct(si['p126'])} | {pct(si['v126'])}（{pct(si['ex126'])}） | {o} |"

    for title, key in (("6カ月以内に2倍の割合が高い順", "p126"), ("6カ月の平均（SPYとの差）が高い順", "ex126")):
        w(f"## 選ぶ期間で{title}（上位20）\n")
        w(head)
        for s, si, so in sorted(res, key=lambda x: -x[1][key])[:20]:
            w(line(s, si, so))
        w("")
    text = "\n".join(out) + "\n"
    if a.out:
        os.makedirs(os.path.dirname(a.out), exist_ok=True)
        open(a.out, "w").write(text)
    print(text)
    # 次の段階（資金で回す）に使う上位の組み合わせを保存
    top = sorted(res, key=lambda x: -x[1]["ex126"])[:40]
    import json
    json.dump([{"sig": s, "in": si, "out": so} for s, si, so in top],
              open(os.path.join(DEFAULT_CACHE, "onkabu_top_signals.json"), "w"), ensure_ascii=False)


# ---------- 資金で回す探索 ----------

CONDS = [("2015〜2020年", "2015-01-02", "2020-12-31", ()), ("2021年〜", "2021-01-04", "9999", ()),
         ("2015年〜 NVDAを除く", "2015-01-02", "9999", ("NVDA",)), ("2019年〜 NVDAを除く", "2019-01-02", "9999", ("NVDA",))]
SIG_BASE = {"mom": ("r126", 1.0), "hi": "nh", "rev": None, "extra": None}
SIGS2 = [
    SIG_BASE,
    {**SIG_BASE, "rev": 0.1}, {**SIG_BASE, "rev": 0.2}, {**SIG_BASE, "rev": 0.3}, {**SIG_BASE, "rev": "acc"},
    {"mom": ("r126", 1.0), "hi": "near10", "rev": None, "extra": "gap"},
    {"mom": ("r126", 0.75), "hi": "nh", "rev": 0.1, "extra": "gap"},
    {"mom": ("r126", 1.5), "hi": None, "rev": None, "extra": None},
    {"mom": ("r126", 1.0), "hi": "near10", "rev": "acc", "extra": None},
    {"mom": ("r63", 0.5), "hi": "nh", "rev": None, "extra": "gap"},
    {"mom": ("r126", 1.0), "hi": "pull", "rev": None, "extra": None},
]
G = {}


def _init(feats, spy, qqq):
    G["feats"], G["spy"], G["qqq"] = feats, spy, qqq
    G["sig"] = {}


def sig_by_day(sig, exclude=()):
    key = (json.dumps(sig, sort_keys=True), exclude)
    if key not in G["sig"]:
        out = {}
        for sym, f in G["feats"].items():
            if sym in exclude:
                continue
            m = ol.signal(f, sig) & f["member"]
            m[:260] = False
            for i in np.nonzero(m)[0]:
                out.setdefault(f["date"][i], []).append(sym)
        G["sig"][key] = out
    return G["sig"][key]


def _run(job):
    import onkabu_sim as sim
    sig, cfg, seeds = job
    spy = G["spy"]
    res = []
    for name, a, b, ex in CONDS:
        days = [d for d in spy["date"] if a <= d <= b]
        k0, k1 = spy["date"].index(days[0]), spy["date"].index(days[-1])
        spy_c = (spy["c"][k1] / spy["c"][k0]) ** (365.25 / (dt.date.fromisoformat(days[-1]) - dt.date.fromisoformat(days[0])).days) - 1
        sbd = sig_by_day(sig, ex)
        cs, ms, ns = [], [], []
        for seed in range(seeds):
            r = sim.simulate(G["feats"], days, sbd, cash_px=G["qqq"] if cfg.get("cash", "QQQ") == "QQQ" else G.get(cfg.get("cash")), seed=seed,
                             **{k: v for k, v in cfg.items() if k != "cash"})
            c, m = sim.metrics(r["curve"], days)
            cs.append(c); ms.append(m); ns.append(r["n_onk"])
        res.append({"cond": name, "cagr": float(np.median(cs)), "mdd": float(np.median(ms)), "onk": float(np.median(ns)), "spy": spy_c})
    return sig, cfg, res


def fmt_cfg(c):
    out = [f"{c.get('slots', 4)}銘柄"]
    out.append("損切りなし" if c.get("stop") is None else f"−{c['stop'] * 100:.0f}%で損切り")
    out.append(f"{c.get('T', 252)}取引日で売る")
    out.append("乗り換えなし" if c.get("rot") is None else f"乗り換え（一番弱い株が{c['rot'] * 100:+.0f}%未満なら）")
    out.append({"open": "翌日の寄り付き", "dip5": "−5%の押し目を待つ（10日）", "dip10": "−10%の押し目を待つ（20日）",
                "confirm": "翌日も上がったら買う", "half": "半分ずつ（+10%で買い増し）"}[c.get("entry", "open")])
    return "・".join(out)


def score(res):
    ex = [r["cagr"] - r["spy"] for r in res]
    return min(ex), float(np.mean(ex))


def cmd_portfolio(a):
    from multiprocessing import Pool
    members, spy, feats = load_all()
    qd = load_prices(DEFAULT_CACHE, "QQQ")
    qqq = dict(zip(qd["date"], qd["c"]))
    head = ("| 順位 | 合図 | 買い方・売り方 | " + " | ".join(f"{c[0]}" for c in CONDS) + " | SPYとの差の最小 |\n|---|---|---|" + "---|" * (len(CONDS) + 1))

    def row(k, sig, cfg, res):
        cells = [f"{r['cagr']:.1%}（{r['mdd']:.0%}・恩株{r['onk']:.0f}）" for r in res]
        return f"| {k} | {ol.describe(sig)} | {fmt_cfg(cfg)} | " + " | ".join(cells) + f" | {score(res)[0]:+.1%} |"

    out = []
    w = out.append
    with Pool(4, initializer=_init, initargs=(feats, spy, qqq)) as pool:
        # 段階1: 売り方・枠の数（合図は基準の⑦、買い方は翌日の寄り付き）
        grid1 = [{"slots": n, "stop": st_, "T": T, "rot": r, "entry": "open"}
                 for n in (2, 3, 4, 6, 8) for st_ in (None, 0.08, 0.12, 0.15, 0.2, 0.3) for T in (63, 126, 189, 252) for r in (None, -0.05, 0.0, 0.1)]
        r1 = pool.map(_run, [(SIG_BASE, c, a.seeds) for c in grid1], chunksize=4)
        r1.sort(key=lambda x: score(x[2]), reverse=True)
        print("段階1 完了", flush=True)
        top_cfgs = [c for _, c, _ in r1[:8]]
        # 段階2: 合図×買い方（段階1の上位8の売り方で）
        jobs = [(sg, {**c, "entry": e}) for sg in SIGS2 for c in top_cfgs for e in ("open", "dip5", "dip10", "confirm", "half")]
        r2 = pool.map(_run, [(sg, c, a.seeds) for sg, c in jobs], chunksize=4)
        r2.sort(key=lambda x: score(x[2]), reverse=True)
        print("段階2 完了", flush=True)
        # 段階3: 上位5を、順番30通り・現金の置き場所4通りで
        G2 = {}
        for sym in ("SPY", "BIL"):
            d = load_prices(DEFAULT_CACHE, sym)
            G2[sym] = dict(zip(d["date"], d["c"]))
    _init(feats, spy, qqq)
    G.update(G2)
    G["none"] = None
    r3 = []
    for sig, cfg, _ in r2[:5]:
        for cash in ("QQQ", "SPY", "BIL", "none"):
            r3.append(_run((sig, {**cfg, "cash": cash}, 30)))
    w("## 段階1: 売り方・枠の数（合図は⑦、翌日の寄り付きで買う、現金はQQQ）上位20\n")
    w("各条件の年率（最大下落率・恩株の数）。SPYの年率: " + " / ".join(f"{r['cond']} {r['spy']:.1%}" for r in r1[0][2]) + "\n")
    w(head)
    for k, (sig, cfg, res) in enumerate(r1[:20], 1):
        w(row(k, sig, cfg, res))
    w("\n段階1の下位5（参考）\n")
    w(head)
    for k, (sig, cfg, res) in enumerate(r1[-5:], len(r1) - 4):
        w(row(k, sig, cfg, res))
    w("\n## 段階2: 合図×買い方（段階1の上位8の売り方で）上位30\n")
    w(head)
    for k, (sig, cfg, res) in enumerate(r2[:30], 1):
        w(row(k, sig, cfg, res))
    w("\n### 合図ごとの一番良い成績（売上の条件の比較など）\n")
    w(head)
    seen = set()
    for k, (sig, cfg, res) in enumerate(r2, 1):
        key = json.dumps(sig, sort_keys=True)
        if key not in seen:
            seen.add(key)
            w(row(k, sig, cfg, res))
    w("\n### 買い方ごとの一番良い成績\n")
    w(head)
    seen = set()
    for k, (sig, cfg, res) in enumerate(r2, 1):
        if cfg["entry"] not in seen:
            seen.add(cfg["entry"])
            w(row(k, sig, cfg, res))
    w("\n## 段階3: 上位5を順番30通りで、待っている現金の置き場所を変えて\n")
    w(head.replace("| 順位 |", "| 現金 |"))
    for sig, cfg, res in r3:
        w(row({"QQQ": "QQQ", "SPY": "SPY", "BIL": "短期国債", "none": "現金0%"}[cfg["cash"]], sig, {k: v for k, v in cfg.items() if k != "cash"}, res))
    text = "\n".join(out) + "\n"
    open(a.out, "w").write(text)
    json.dump([{"sig": s_, "cfg": c_, "res": r_} for s_, c_, r_ in r2[:10]], open(os.path.join(DEFAULT_CACHE, "onkabu_best.json"), "w"), ensure_ascii=False)
    print(text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("signals", "portfolio"))
    ap.add_argument("--seeds", type=int, default=6)
    ap.add_argument("--out")
    ap.add_argument("--summary")
    a = ap.parse_args()
    {"signals": cmd_signals, "portfolio": cmd_portfolio}[a.cmd](a)


if __name__ == "__main__":
    main()
