#!/usr/bin/env python3
"""恩株ツールの調査2: 2倍になった銘柄は、買った時点でどんな特徴を持っていたか

使い方:
  tools/backtest_lib.py fetch ; tools/backtest_onkabu.py fetch   # 先に日足・株式数を取得
  tools/backtest_onkabu_features.py fetch [--cache DIR]           # 売上・利益（SEC）を取得
  tools/backtest_onkabu_features.py run [--cache DIR] [--out FILE]

毎月の最初の取引日に、その日のS&P500の構成銘柄それぞれについて、その日までに分かる特徴を計算し、
特徴の強さで5つの組に分けて（毎月の銘柄の中での順位）、組ごとの「3年以内に2倍」「5年後の恩株の価値」などを比べる。
決算の数値は提出日から使う（後知恵なし）。
"""
import argparse
import datetime as dt
import json
import os
import statistics as st
import sys
import time
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backtest_lib import DEFAULT_CACHE, load_universe, load_prices, is_member, sma
import backtest_onkabu as ob

REV_TAGS = ("Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet",
            "RevenueFromContractWithCustomerIncludingAssessedTax", "SalesRevenueGoodsNet")
CONCEPTS = {"rev": REV_TAGS, "ni": ("NetIncomeLoss",), "eps": ("EarningsPerShareDiluted", "EarningsPerShareBasic")}


def cmd_fetch(a, syms=None):
    """syms を渡すとその銘柄だけ取る（S&P500の外の銘柄用）。保存先は a.cache/onkabu_fund"""
    if syms is None:
        members, data = load_universe(a.cache)
    out_dir = os.path.join(a.cache, "onkabu_fund")
    os.makedirs(out_dir, exist_ok=True)
    tick = json.loads(ob.sec_get("https://www.sec.gov/files/company_tickers.json"))
    cik = {v["ticker"].upper(): v["cik_str"] for v in tick.values()}

    def facts_of(units):
        rows = []
        for u, fs in units.items():
            if not isinstance(fs, list):
                continue
            for f in fs:
                if f.get("filed") and f.get("start") and f.get("val") is not None:
                    rows.append((f["filed"], f["start"], f["end"], f["val"]))
        return rows

    def one(sym):
        path = os.path.join(out_dir, sym + ".json")
        if os.path.exists(path):
            return True
        c = cik.get(sym.replace(".", "-").upper())
        res = {}
        if c:
            for key, tags in CONCEPTS.items():
                rows = []
                for tag in tags:   # 会社によって使う項目名が違い、年によって変わることもあるので全部合わせる
                    t = ob.sec_get(f"https://data.sec.gov/api/xbrl/companyconcept/CIK{c:010d}/us-gaap/{tag}.json")
                    time.sleep(0.12)
                    if t:
                        rows += facts_of(json.loads(t).get("units", {}))
                res[key] = sorted(set(map(tuple, rows)))
            if not any(res.values()):   # companyconcept が空を返す会社（KOなど）
                t = ob.sec_get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{c:010d}.json")
                gaap = json.loads(t or "{}").get("facts", {}).get("us-gaap", {})
                for key, tags in CONCEPTS.items():
                    rows = []
                    for tag in tags:
                        rows += facts_of(gaap.get(tag, {}).get("units", {}))
                    res[key] = sorted(set(map(tuple, rows)))
        json.dump(res, open(path, "w"))
        return True

    syms = sorted(syms if syms is not None else data)
    with ThreadPoolExecutor(2) as ex:
        list(ex.map(one, syms))
    n = {k: sum(1 for s in syms if json.load(open(os.path.join(out_dir, s + ".json"))).get(k)) for k in CONCEPTS}
    print(f"{len(syms)} 銘柄、取得できた数: {n}")


# ---------- 特徴の計算 ----------

def yoy(rows, day, take=max):
    """day までに提出された決算のうち一番新しい期（四半期か通期）の、前年同期比。(伸び率, 今期の値, "q"/"y")
    売上は複数の項目名（Revenues など）を合わせて取っているため、同じ期間に部分的な売上（サービス売上など）が混ざる。
    同じ期間の値は一番大きいもの（＝合計の売上）を使う"""
    per = {}
    for filed, start, end, val in rows:
        if filed > day:
            continue
        n = (dt.date.fromisoformat(end) - dt.date.fromisoformat(start)).days
        kind = "q" if 80 <= n <= 100 else "y" if 350 <= n <= 380 else None
        if kind:
            per.setdefault((end, kind), []).append(val)
    if not per:
        return None
    end, kind = max(per, key=lambda k: (k[0], k[1] == "q"))
    e = dt.date.fromisoformat(end)
    if (dt.date.fromisoformat(day) - e).days > 200:    # 決算が古すぎる
        return None
    val = take(per[(end, kind)])
    prev = [(abs((e - dt.date.fromisoformat(e2)).days - 365), take(v)) for (e2, k2), v in per.items()
            if k2 == kind and 345 <= (e - dt.date.fromisoformat(e2)).days <= 385]
    pv = min(prev)[1] if prev else None
    g = val / pv - 1 if pv and pv > 0 else None
    return g, val, kind


def price_features(s, i, ma200, ma150, ma50):
    c = s["c"]
    if i < 260 or ma200[i] is None or ma200[i - 20] is None:
        return None
    rets = [c[k] / c[k - 1] - 1 for k in range(i - 59, i + 1)]
    m = sum(rets) / len(rets)
    return {
        "mom12_1": c[i - 21] / c[i - 252] - 1,
        "mom6": c[i] / c[i - 126] - 1,
        "mom1": c[i] / c[i - 21] - 1,
        "hi52": c[i] / max(c[i - 251:i + 1]),
        "ma200": c[i] / ma200[i] - 1,
        "ma200_slope": ma200[i] / ma200[i - 20] - 1,
        "vol60": (sum((r - m) ** 2 for r in rets) / (len(rets) - 1)) ** 0.5 * 252 ** 0.5,
        "stage2": float(c[i] > ma150[i] and ma150[i] > ma150[i - 20] and ma50[i] > ma150[i]),
    }


FEATURES = [
    ("mom12_1", "株価の勢い（12カ月、直近1カ月を除く）", "高いほど上昇が強い"),
    ("mom6", "株価の勢い（6カ月）", ""),
    ("mom1", "直近1カ月の値動き", ""),
    ("hi52", "52週高値に対する位置", "1.0＝高値"),
    ("ma200", "200日線からの乖離", ""),
    ("ma200_slope", "200日線の傾き（20日）", ""),
    ("vol60", "値動きの大きさ（60日、年率）", ""),
    ("cap", "時価総額", ""),
    ("rev_yoy", "売上の前年同期比", "直近の決算"),
    ("eps_yoy", "1株利益の前年同期比", "前年が黒字のときだけ"),
    ("ps", "株価売上高倍率（PSR）", "時価総額÷年換算の売上"),
    ("pe", "株価収益率（PER）", "黒字のときだけ。年換算"),
]


def build(a, all_months=False):
    """all_months=True なら、3年後の株価がない最近の月も含める（資金の再現用。結果の o は空のことがある）"""
    members, data = load_universe(a.cache, min_bars=60)
    spy = data.pop("SPY", None) or load_prices(a.cache, "SPY")
    for k in ("QQQ", "^VIX"):
        data.pop(k, None)
    spy_c, spy_pos = spy["c"], {d: k for k, d in enumerate(spy["date"])}
    shares, fund = {}, {}
    for sym in data:
        p = os.path.join(a.cache, "onkabu", sym + ".json")
        if os.path.exists(p):
            shares[sym] = ob.clean_shares(json.load(open(p)), data[sym], ob.BRK_A_TO_B if sym == "BRK.B" else 1.0)
        p = os.path.join(a.cache, "onkabu_fund", sym + ".json")
        if os.path.exists(p):
            fund[sym] = {k: [tuple(r) for r in v] for k, v in json.load(open(p)).items()}
    pos = {s: {d: k for k, d in enumerate(v["date"])} for s, v in data.items()}
    mas = {s: (sma(v["c"], 200), sma(v["c"], 150), sma(v["c"], 50)) for s, v in data.items()}
    entries = [d for d in ob.first_days_of_month(spy["date"]) if d >= "2015-01-01" and (all_months or spy_pos[d] + 3 * ob.TD <= len(spy_c) - 1)]
    recs = []
    for d in entries:
        mem = [s for s, sp in members.items() if is_member(sp, d) and s in data and d in pos[s] and s in shares]
        month = []
        for s in mem:
            i = pos[s][d]
            sh = ob.shares_asof(shares[s], d)
            f = price_features(data[s], i, *mas[s])
            if not sh or not f:
                continue
            cap = sh * data[s]["c"][i]
            f["cap"] = cap
            fd = fund.get(s, {})
            r = yoy(fd.get("rev", []), d)
            f["rev_yoy"] = r[0] if r else None
            if r and r[1] > 0:
                f["ps"] = cap / (r[1] * (4 if r[2] == "q" else 1))
            e = yoy(fd.get("ni", []), d)
            if e and e[1] > 0:
                f["pe"] = cap / (e[1] * (4 if e[2] == "q" else 1))
            ep = yoy(fd.get("eps", []), d)
            f["eps_yoy"] = ep[0] if ep else None
            out = {}
            for h in (3, 5):
                if spy_pos[d] + h * ob.TD > len(spy_c) - 1:
                    continue
                fw = ob.forward(data[s], i, spy_c, spy_pos, h * ob.TD)
                out[h] = {"dbl": fw["t2"] is not None, "dd30": fw["low_before"] <= 0.7, "ret": fw["ret"],
                          "onk": ob.onkabu_value(data[s], i, fw, spy_c, spy_pos),
                          "spy": ob.spy_ret(spy_c, spy_pos, d, ob.nearest(spy_pos, fw["end_date"]))}
            month.append({"d": d, "s": s, "f": f, "o": out})
        month.sort(key=lambda x: -x["f"]["cap"])
        for r, x in enumerate(month, 1):
            x["f"]["rank"] = r
        for key, _, _ in FEATURES:   # その月の中での順位（0〜1、1が一番大きい）
            xs = sorted((x["f"][key], k) for k, x in enumerate(month) if x["f"].get(key) is not None)
            for j, (_, k) in enumerate(xs):
                month[k]["f"][key + "_p"] = j / max(1, len(xs) - 1)
        recs += month
    return recs, entries


def quintiles(recs, key):
    """毎月の中で key の順位を5つに分ける。{1..5: [rec]}（5が一番大きい）"""
    by_month = {}
    for x in recs:
        v = x["f"].get(key)
        if v is not None:
            by_month.setdefault(x["d"], []).append((v, x))
    q = {k: [] for k in range(1, 6)}
    for d, xs in by_month.items():
        xs.sort(key=lambda t: t[0])
        n = len(xs)
        for j, (v, x) in enumerate(xs):
            q[min(5, j * 5 // n + 1)].append(x)
    return q


def pct(x, d=1):
    return "―" if x is None else f"{x * 100:.{d}f}%"


def summarize(xs):
    """3年以内に2倍・2倍前に−30%・5年後の恩株の価値（中央値・平均）・SPYに勝った割合・前半後半の2倍の割合"""
    o3 = [x["o"][3] for x in xs if 3 in x["o"]]
    o5 = [x["o"][5] for x in xs if 5 in x["o"]]
    early = [x["o"][3]["dbl"] for x in xs if 3 in x["o"] and x["d"] < "2020-01-01"]
    late = [x["o"][3]["dbl"] for x in xs if 3 in x["o"] and x["d"] >= "2020-01-01"]
    fr = lambda b: sum(b) / len(b) if b else None
    return {
        "n": len(o3),
        "dbl3": fr([o["dbl"] for o in o3]),
        "dd30": fr([o["dd30"] for o in o3]),
        "onk5_med": st.median([o["onk"] for o in o5]) if o5 else None,
        "onk5_mean": st.mean([o["onk"] for o in o5]) if o5 else None,
        "beat5": fr([o["onk"] > o["spy"] for o in o5]),
        "dbl3_early": fr(early), "dbl3_late": fr(late),
        "spy5": st.median([o["spy"] for o in o5]) if o5 else None,
    }


HEAD = ("| 組 | 件数 | 3年以内に2倍 | 2倍前に−30% | 5年後の恩株の価値 中央値 / 平均 | 5年後にSPYに勝った | "
        "3年以内に2倍（2015〜19年に買った / 2020〜23年） |\n|---|---|---|---|---|---|---|")


def row(label, m):
    v = lambda x: "―" if x is None else f"{x:.2f}倍"
    return (f"| {label} | {m['n']:,} | {pct(m['dbl3'])} | {pct(m['dd30'])} | {v(m['onk5_med'])} / {v(m['onk5_mean'])} | "
            f"{pct(m['beat5'], 0)} | {pct(m['dbl3_early'])} / {pct(m['dbl3_late'])} |")


def cmd_run(a):
    recs, entries = build(a)
    out = []
    w = out.append
    w("---\ntype: backtest\ntitle: 2倍になった銘柄の、買った時点の特徴\n"
      f"created: {dt.date.today().isoformat()}\nscript: tools/backtest_onkabu_features.py\n---\n")
    w("# 2倍になった銘柄の、買った時点の特徴\n")
    if a.summary and os.path.exists(a.summary):
        w(open(a.summary).read())
    allm = summarize(recs)
    w("## 前提\n")
    w("- `2倍株の基礎調査.md` と同じ対象・同じ数え方（毎月の最初の取引日に、その日のS&P500の構成銘柄を買ったことにする。株価は配当込み、判定は終値）")
    w(f"- 買う日: {entries[0]}〜{entries[-1]}（3年後まで株価がある月）。5年後の値は 〜{max(x['d'] for x in recs if 5 in x['o'])} に買った分だけ")
    w("- 特徴はすべて、買う日までに分かる値（決算はSECへの提出日から使う）。毎月、その月の銘柄の中で特徴の小さい順に5つの組に分ける（組1が一番小さい、組5が一番大きい）")
    w("- 恩株の価値: 2倍になった日に55.7%を売り（税引き後で元本が戻る）、売ったお金はSPYへ。残りは5年後まで持つ")
    w("- 決算の数値は会社によって取れないものがある（銀行の売上など）。その銘柄はその特徴の表に入らない")
    w(f"- **全体（選ばない場合）**: 件数 {allm['n']:,}、3年以内に2倍 {pct(allm['dbl3'])}、2倍前に−30% {pct(allm['dd30'])}、"
      f"5年後の恩株の価値 中央値 {allm['onk5_med']:.2f}倍 / 平均 {allm['onk5_mean']:.2f}倍、SPYに勝った {pct(allm['beat5'], 0)}。"
      f"同じ期間のSPYは5年で 中央値 {allm['spy5']:.2f}倍\n")
    w("## 1. 特徴ごとの比較（5つの組）\n")
    for key, name, note in FEATURES:
        q = quintiles(recs, key)
        w(f"### {name}" + (f"（{note}）" if note else "") + "\n")
        w(HEAD)
        for k in range(1, 6):
            xs = q[k]
            if not xs:
                continue
            vals = sorted(x["f"][key] for x in xs)
            mid = vals[len(vals) // 2]
            shown = (f"{mid / 1e8:,.0f}億ドル" if key == "cap" else
                     f"{mid:.1f}倍" if key in ("ps", "pe") else f"{mid:.2f}" if key == "hi52" else pct(mid, 0))
            w(row(f"組{k}（中央値 {shown}）", summarize(xs)))
        w("")
    if a.combos:
        w("## 2. 特徴の組み合わせ\n")
        w(HEAD)
        w(row("全体（選ばない）", allm))
        for label, fn in COMBOS:
            xs = [x for x in recs if fn(x["f"])]
            if xs:
                w(row(label, summarize(xs)))
        w("")
    text = "\n".join(out) + "\n"
    if a.out:
        os.makedirs(os.path.dirname(a.out), exist_ok=True)
        open(a.out, "w").write(text)
    print(text)


def g(f, k, lo=None, hi=None):
    v = f.get(k)
    return v is not None and (lo is None or v >= lo) and (hi is None or v <= hi)


COMBOS = [
    ("売上の伸び≧15%", lambda f: g(f, "rev_yoy", 0.15)),
    ("値動きの大きさ 上位40%", lambda f: g(f, "vol60_p", 0.6)),
    ("時価総額 上位100", lambda f: f["rank"] <= 100),
    ("売上の伸び≧15% かつ 値動き上位40%", lambda f: g(f, "rev_yoy", 0.15) and g(f, "vol60_p", 0.6)),
    ("売上の伸び≧15% かつ 200日線より上で200日線が上向き", lambda f: g(f, "rev_yoy", 0.15) and g(f, "ma200", 0) and g(f, "ma200_slope", 0)),
    ("売上の伸び≧15% かつ 1株利益の伸び≧15% かつ 200日線より上（オニール風）",
     lambda f: g(f, "rev_yoy", 0.15) and g(f, "eps_yoy", 0.15) and g(f, "ma200", 0)),
    ("売上の伸び≧15% かつ 時価総額 上位100", lambda f: g(f, "rev_yoy", 0.15) and f["rank"] <= 100),
    ("売上の伸び≧15% かつ 時価総額 上位100 かつ 値動き上位40%",
     lambda f: g(f, "rev_yoy", 0.15) and f["rank"] <= 100 and g(f, "vol60_p", 0.6)),
    ("売上の伸び≧20% かつ 値動き上位40% かつ 勢い（12カ月）上位40%",
     lambda f: g(f, "rev_yoy", 0.2) and g(f, "vol60_p", 0.6) and g(f, "mom12_1_p", 0.6)),
    ("売上の伸び≧20% かつ 値動き上位40% かつ 52週高値の85%以下（押し目）",
     lambda f: g(f, "rev_yoy", 0.2) and g(f, "vol60_p", 0.6) and g(f, "hi52", None, 0.85)),
    ("売上の伸び≧25%", lambda f: g(f, "rev_yoy", 0.25)),
    ("売上の伸び≧25% かつ 値動き上位40%", lambda f: g(f, "rev_yoy", 0.25) and g(f, "vol60_p", 0.6)),
    ("売上の伸び≧25% かつ 時価総額 上位150", lambda f: g(f, "rev_yoy", 0.25) and f["rank"] <= 150),
]


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("fetch", "run"):
        p = sub.add_parser(name)
        p.add_argument("--cache", default=DEFAULT_CACHE)
        if name == "run":
            p.add_argument("--out")
            p.add_argument("--summary")
            p.add_argument("--combos", action="store_true")
    a = ap.parse_args()
    {"fetch": cmd_fetch, "run": cmd_run}[a.cmd](a)


if __name__ == "__main__":
    main()
