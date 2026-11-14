#!/usr/bin/env python3
"""策4（Fableの次の策、2026-11-14）: 恩株ツールの1回の金額をNISAの枠（1回80万円・年240万円）に固定し、それ以外の資金は新分析ツールに置く

比べる形（資金16,500ドル、2015-01-02〜）:
- 今の形: 新分析ツール12,000ドル＋恩株ツール4,500ドル（恩株ツールは利益を上乗せして口座全体で1銘柄、課税口座、待っている現金はQQQ）
- 策4（NISA）: 16,500ドルを全部新分析ツールに置き、恩株ツールの合図の日だけ、1回80万円（その日のドル円で直す。年240万円の枠の残りまで）を
  新分析ツールから出して、NISAでその銘柄を買う。2倍で50%を売り（税なし）、残りは恩株としてNISAで持ち続ける。期限・損切りは全部売る。
  売った代金は新分析ツールに戻す。
- 策4（課税口座）: 同じで、恩株ツールの売買を課税口座で行う（2倍で55.7%を売る。確定した利益に、売った時に20.315%）
- （参考）全部を新分析ツールに置く

恩株ツールの売買（合図・買った日・売った日・理由）は `results/fable_onkabu.json` の記録（tools/fable_onkabu_curve.py）をそのまま使う。
新分析ツールは `results/tax_87.json`・`tax_free.json` の「今のルール＋待っている現金をQQQ」（税込み、乱数30通り）。
新分析ツールからの出し入れは、その日の資金の割合で売り買いしたとみなす（出し入れの税と手数料は数えない）。NISAの生涯の枠（1,800万円）は、
ユーザーが中長期の分で使っている量が分からないので数えない（使った量は表に出す）。

使い方: python3 tools/fable_onkabu_nisa_cap.py [--out FILE]
"""
import argparse
import json
import os
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fable_data as fd  # noqa: E402
from backtest_lib import DEFAULT_CACHE, load_prices  # noqa: E402

R = os.path.join(DEFAULT_CACHE, "results")
TAX = 0.20315
FEE = 0.00132


def metrics(c, days):
    import datetime as dt
    yrs = (dt.date.fromisoformat(days[-1]) - dt.date.fromisoformat(days[0])).days / 365.25
    pk = md = 0.0
    for v in c:
        pk = max(pk, v)
        md = max(md, 1 - v / pk)
    return (c[-1] / c[0]) ** (1 / yrs) - 1, md


def cagr_between(c, days, lo, hi):
    ks = [k for k, d in enumerate(days) if lo <= d <= hi]
    return metrics([c[k] for k in ks], [days[k] for k in ks])[0]


def rolling(c, base, step=10, win=250):
    diffs = [(c[s + win] / c[s]) - (base[s + win] / base[s]) for s in range(0, len(c) - win, step)]
    nz = [x for x in diffs if abs(x) > 1e-9]
    return sum(diffs) / len(diffs), sum(1 for x in nz if x > 0) / max(1, len(nz))


def simulate(N, days, log, jpy, px, nisa=True, per_buy_yen=800000, year_cap_yen=2400000, capital=16500.0, onk_share=None):
    """N: 新分析ツールの1単位の資金の推移。log: 恩株ツールの売買。戻り値: 毎日の資金、NISAの使用"""
    units = capital / N[0]
    pos = []        # 持っている恩株ツールの株: {"sym","sh","cost","onk"}
    ev_buy, ev_out = {}, {}
    for x in log:
        ev_buy.setdefault(x["buy"], []).append(x)
        ev_out.setdefault(x["out"], []).append(x)
    used = {}
    curve = []
    nisa_rows = []
    taxable_real = 0.0
    for k, d in enumerate(days):
        # 売り（その日の引け）
        for x in ev_out.get(d, []):
            for p in [p for p in pos if p["sym"] == x["sym"] and not p["onk"] and p["buy"] == x["buy"]]:
                c_ = px[p["sym"]]["c"].get(d)
                if c_ is None:
                    continue
                val = p["sh"] * c_
                if x["why"] == "2倍":
                    f = 0.5 if nisa else 1 / (2 - TAX)
                else:
                    f = 1.0
                proceeds = val * f
                gain = proceeds - p["cost"] * f
                if not nisa:
                    proceeds *= 1 - FEE
                    if gain > 0:
                        proceeds -= TAX * gain   # 源泉徴収あり（売った時に引かれる。同じ年の損との通算は簡単のため数えない）
                units += proceeds / N[k]
                if f >= 1.0:
                    pos.remove(p)
                else:
                    p["sh"] *= 1 - f
                    p["cost"] *= 1 - f
                    p["onk"] = True
        # 買い（その日の寄り付き。新分析ツールの資金はその日の引けの値で出したとみなす）
        for x in ev_buy.get(d, []):
            o_ = px[x["sym"]]["o"].get(d)
            if o_ is None:
                continue
            y = d[:4]
            room = year_cap_yen - used.get(y, 0.0) if nisa else float("inf")
            yen = min(per_buy_yen, room) if nisa else per_buy_yen
            if yen <= 0:
                continue
            usd = yen / jpy[d]
            usd = min(usd, units * N[k] * 0.5)
            units -= usd / N[k]
            amt = usd * (1 - (0.0 if nisa else FEE))
            pos.append({"sym": x["sym"], "sh": amt / o_, "cost": usd, "onk": False, "buy": x["buy"]})
            used[y] = used.get(y, 0.0) + yen
            nisa_rows.append((d, x["sym"], yen, x["why"]))
        val = units * N[k] + sum(p["sh"] * px[p["sym"]]["c"].get(d, p.get("last", 0.0)) for p in pos)
        for p in pos:
            if d in px[p["sym"]]["c"]:
                p["last"] = px[p["sym"]]["c"][d]
        curve.append(val)
    return curve, nisa_rows, pos


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    a = ap.parse_args()
    onk = json.load(open(os.path.join(R, "fable_onkabu.json")))
    fd.L = os.path.expanduser("~/.cache/stock_backtest/long/index/")
    jr = fd.load("JPY=X")
    out = []
    w = out.append
    w("| 監視銘柄 | 恩株ツールの合図 | 形 | 年率 | 最大下落率 | 2015〜2021年 | 2022年〜 | 1年の区切り: 今の形との差の平均 | 上回った割合 |")
    w("|---|---|---|---|---|---|---|---|---|")
    keep_rows = None
    for watch in ("87", "free"):
        T = json.load(open(os.path.join(R, f"tax_{watch}.json")))
        key = list(T)[2]   # 今のルール＋待っている現金をQQQ
        days = T[key]["days"]
        jpy, last = {}, None
        for d in days:
            last = jr.get(d, (None, None, None, (last or 150.0)))[3]
            jpy[d] = last
        for ex in ("all", "noNVDA"):
            log = onk[f"log_tax_{ex}"]
            px = {}
            for x in log:
                if x["sym"] not in px:
                    p = load_prices(DEFAULT_CACHE, x["sym"])
                    px[x["sym"]] = {"o": dict(zip(p["date"], p["o"])), "c": dict(zip(p["date"], p["c"]))}
            oc = dict(zip(onk["days"], onk[f"tax_{ex}"]))
            O = []
            lo_ = None
            for d in days:
                lo_ = oc.get(d, lo_)
                O.append(lo_)
            res = {}
            for s, N in enumerate(T[key]["eq"]):
                N = [x if x is not None else N[0] for x in N]
                cur = [12000 * n / N[0] + 4500 * o / O[0] for n, o in zip(N, O)]
                allN = [16500 * n / N[0] for n in N]
                c4, rows4, pos4 = simulate(N, days, log, jpy, px, nisa=True)
                c4t, _, _ = simulate(N, days, log, jpy, px, nisa=False)
                if s == 0 and watch == "87" and ex == "all":
                    keep_rows = (rows4, pos4, days, px)
                for lab, c in (("今の形（新分析12,000ドル＋恩株4,500ドル、恩株は利益を上乗せ）", cur),
                               ("策4: 恩株ツールはNISAで1回80万円、ほかは全部新分析ツール", c4),
                               ("策4を課税口座で（1回80万円、ほかは全部新分析ツール）", c4t),
                               ("（参考）全部を新分析ツールに置く", allN)):
                    cg, md = metrics(c, days)
                    rd, rg = rolling(c, cur)
                    res.setdefault(lab, []).append((cg, md, cagr_between(c, days, "2015-01-01", "2021-12-31"),
                                                    cagr_between(c, days, "2022-01-01", "9999"), rd, rg))
            for lab, xs in res.items():
                m = [st.median(x[i] for x in xs) for i in range(6)]
                w(f"| {'87銘柄' if watch == '87' else '全業種'} | {'NVDAを含む' if ex == 'all' else 'NVDAを除く'} | {lab} | {m[0]:.1%} | {m[1]:.0%} | {m[2]:.1%} | {m[3]:.1%} | {m[4]:+.1%} | {m[5]:.0%} |")
    rows4, pos4, days, px = keep_rows
    w("\n策4（NISA）の買い付けと枠の使い方（87銘柄・NVDAを含む・乱数1通り）:\n")
    w("| 買った日 | 銘柄 | 金額 | 結果 |\n|---|---|---|---|")
    for d, sym, yen, why in rows4:
        w(f"| {d} | {sym} | {yen / 1e4:.0f}万円 | {why} |")
    held = [p for p in pos4 if p["onk"]]
    w(f"\n- 最後に持っている恩株（NISA）: {', '.join(p['sym'] for p in held) or 'なし'}。買った金額の合計（生涯の枠を使う分）は約{sum(p['cost'] for p in held) * jpy[days[-1]] / 1e4:.0f}万円")
    text = "\n".join(out) + "\n"
    if a.out:
        open(a.out, "w").write(text)
    print(text)


if __name__ == "__main__":
    main()
