#!/usr/bin/env python3
"""恩株ツールの調査4: 短い期間（3カ月〜1年）で2倍になる直前に、どんな合図が出ていたか

使い方（先に backtest_lib.py・backtest_onkabu.py・backtest_onkabu_features.py の fetch を済ませる）:
  tools/backtest_onkabu_fast.py [--cache DIR] [--out FILE] [--summary FILE]

やり方:
  - 毎週の最後の取引日に、その日のS&P500の構成銘柄それぞれについて、その日までに分かる特徴を計算する。
  - その日の終値から、63取引日（約3カ月）・126取引日（約6カ月）・252取引日（約1年）以内に終値で2倍になったかを数える。
  - 特徴ごと・組み合わせごとに「2倍になった割合」を、合図なし（全体）と比べる（何倍になったか＝リフト）。
決算の数値は提出日から使う（後知恵なし）。業種は今のYahooの分類を過去にも使う。
"""
import argparse
import bisect
import datetime as dt
import json
import os
import statistics as st
import sys
from collections import deque

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backtest_lib import DEFAULT_CACHE, load_universe, load_prices, is_member, sma
import backtest_onkabu as ob
import backtest_onkabu_features as bf

HS = (63, 126, 252)


def rolling_max(x, n):
    out, dq = [], deque()
    for i, v in enumerate(x):
        while dq and x[dq[-1]] <= v:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - n:
            dq.popleft()
        out.append(x[dq[0]])
    return out


def rev_series(rows):
    """[(提出日, 売上の前年同期比)]（提出日の順）。四半期決算のみ"""
    filed = sorted({r[0] for r in rows})
    out = []
    for f in filed:
        y = bf.yoy(rows, f)
        if y and y[0] is not None:
            out.append((f, y[0]))
    return out


def build(a):
    members, data = load_universe(a.cache, min_bars=300)
    spy = load_prices(a.cache, "SPY")
    for k in ("SPY", "QQQ", "^VIX"):
        data.pop(k, None)
    ind = json.load(open(os.path.join(a.cache, "onkabu", "industry.json")))
    spy_c = spy["c"]
    spy_ma200 = sma(spy_c, 200)
    spy_pos = {d: k for k, d in enumerate(spy["date"])}
    # 週の最後の取引日
    weeks = []
    for k, d in enumerate(spy["date"]):
        if d < "2014-06-01":
            continue
        if k + 1 == len(spy["date"]) or dt.date.fromisoformat(spy["date"][k + 1]).isocalendar()[1] != dt.date.fromisoformat(d).isocalendar()[1]:
            weeks.append(d)
    pre = {}
    for s, v in data.items():
        c, vol = v["c"], v["v"]
        p = os.path.join(a.cache, "onkabu_fund", s + ".json")
        rows = [tuple(r) for r in json.load(open(p)).get("rev", [])] if os.path.exists(p) else []
        pre[s] = {
            "pos": {d: k for k, d in enumerate(v["date"])},
            "hi252": rolling_max(c, 252), "hi_all": rolling_max(c, 10 ** 6),
            "ma50": sma(c, 50), "ma200": sma(c, 200),
            "v20": sma(vol, 20), "v100": sma(vol, 100),
            "rev": rev_series(rows),
        }
    recs = []
    for d in weeks:
        mem = [s for s, sp in members.items() if s in data and is_member(sp, d) and d in pre[s]["pos"]]
        day = []
        for s in mem:
            P, c = pre[s], data[s]["c"]
            i = P["pos"][d]
            if i < 260:
                continue
            f = {
                "r21": c[i] / c[i - 21] - 1, "r63": c[i] / c[i - 63] - 1, "r126": c[i] / c[i - 126] - 1,
                "r252": c[i] / c[i - 252] - 1,
                "hi52": c[i] / P["hi252"][i], "new_hi": c[i] >= P["hi252"][i] * 0.999,
                "ath": c[i] >= P["hi_all"][i] * 0.999,
                "above_ma": P["ma50"][i] is not None and P["ma200"][i] is not None and c[i] > P["ma50"][i] > P["ma200"][i],
                "vratio": P["v20"][i] / P["v100"][i] if P["v100"][i] else None,
                "gap": max(c[k] / c[k - 1] - 1 for k in range(i - 62, i + 1)),
                "spy_up": spy_ma200[spy_pos[d]] is not None and spy_c[spy_pos[d]] > spy_ma200[spy_pos[d]],
                "ind": ind.get(s, ""),
            }
            r = P["rev"]
            j = bisect.bisect_right([x[0] for x in r], d) - 1
            if j >= 0 and (dt.date.fromisoformat(d) - dt.date.fromisoformat(r[j][0])).days <= 120:
                f["rev"] = r[j][1]
                f["rev_acc"] = r[j][1] - r[j - 1][1] if j >= 1 else None
            out = {}
            for h in HS:
                if i + h >= len(c) and d > data[s]["date"][-1]:
                    continue
                end = min(i + h, len(c) - 1)
                if spy_pos[d] + h > len(spy_c) - 1:
                    continue
                path = c[i + 1:end + 1]
                t2 = next((k for k, x in enumerate(path) if x >= 2 * c[i]), None)
                low = min([1.0] + [x / c[i] for x in (path[:t2] if t2 is not None else path)])
                out[h] = {"dbl": t2 is not None, "low": low, "ret": c[end] / c[i]}
            day.append({"d": d, "s": s, "f": f, "o": out})
        # 業種の勢い（その日の同じ業種の63日騰落率の中央値、3銘柄以上）と、勢いの順位
        by = {}
        for x in day:
            by.setdefault(x["f"]["ind"], []).append(x["f"]["r63"])
        for x in day:
            xs = by.get(x["f"]["ind"], [])
            x["f"]["ind63"] = st.median(xs) if len(xs) >= 3 and x["f"]["ind"] else None
        for key in ("r63", "r126", "ind63"):
            xs = sorted((x["f"][key], k) for k, x in enumerate(day) if x["f"].get(key) is not None)
            for j, (_, k) in enumerate(xs):
                day[k]["f"][key + "_p"] = j / max(1, len(xs) - 1)
        recs += day
    return recs, weeks


def summarize(xs):
    m = {"n": len(xs)}
    for h in HS:
        o = [x["o"][h] for x in xs if h in x["o"]]
        m[h] = (sum(q["dbl"] for q in o) / len(o)) if o else None
        m[f"n{h}"] = len(o)
    o = [x["o"][252] for x in xs if 252 in x["o"]]
    m["dd30"] = sum(q["low"] <= 0.7 for q in o) / len(o) if o else None
    m["ret_med"] = st.median(q["ret"] for q in o) if o else None
    m["ret_mean"] = st.mean(q["ret"] for q in o) if o else None
    for lab, lo, hi in (("early", "", "2020-01-01"), ("late", "2020-01-01", "9999")):
        q = [x["o"][126]["dbl"] for x in xs if 126 in x["o"] and lo <= x["d"] < hi]
        m[lab] = sum(q) / len(q) if q else None
    m["syms"] = len({x["s"] for x in xs})
    m["weeks"] = len({x["d"] for x in xs})
    return m


def pct(x, d=1):
    return "―" if x is None else f"{x * 100:.{d}f}%"


HEAD = ("| 合図 | 件数（銘柄数） | 3カ月以内に2倍 | 6カ月以内に2倍 | 1年以内に2倍（全体の何倍） | 2倍前に−30%（1年） | "
        "1年後の値上がり 中央値 / 平均 | 6カ月以内に2倍（2014〜19年 / 2020年〜） |\n|---|---|---|---|---|---|---|---|")


def row(label, m, base):
    lift = m[252] / base[252] if m[252] and base[252] else None
    v = lambda x: "―" if x is None else f"{(x - 1) * 100:+.0f}%"
    return (f"| {label} | {m['n']:,}（{m['syms']}） | {pct(m[63])} | {pct(m[126])} | {pct(m[252])}（{lift:.1f}倍） | {pct(m['dd30'])} | "
            f"{v(m['ret_med'])} / {v(m['ret_mean'])} | {pct(m['early'])} / {pct(m['late'])} |") if lift else f"| {label} | {m['n']} | ― |"


def g(f, k, lo=None, hi=None):
    v = f.get(k)
    return v is not None and v is not False and (lo is None or v >= lo) and (hi is None or v <= hi)


SINGLE = [
    ("3カ月で+30%以上", lambda f: g(f, "r63", 0.30)),
    ("3カ月で+50%以上", lambda f: g(f, "r63", 0.50)),
    ("3カ月で+100%以上（すでに2倍）", lambda f: g(f, "r63", 1.0)),
    ("6カ月で+50%以上", lambda f: g(f, "r126", 0.50)),
    ("6カ月で+100%以上", lambda f: g(f, "r126", 1.0)),
    ("3カ月の勢い 上位5%", lambda f: g(f, "r63_p", 0.95)),
    ("52週高値を更新", lambda f: f["new_hi"]),
    ("上場来高値（2013年以降）を更新", lambda f: f["ath"]),
    ("株価＞50日線＞200日線", lambda f: f["above_ma"]),
    ("出来高が増えている（20日÷100日≧1.5）", lambda f: g(f, "vratio", 1.5)),
    ("3カ月以内に1日で+10%以上の日がある（決算などの急騰）", lambda f: g(f, "gap", 0.10)),
    ("3カ月以内に1日で+20%以上の日がある", lambda f: g(f, "gap", 0.20)),
    ("売上の前年同期比 ≧20%", lambda f: g(f, "rev", 0.20)),
    ("売上の前年同期比 ≧40%", lambda f: g(f, "rev", 0.40)),
    ("売上の伸びが加速（前の決算より+10ポイント以上）", lambda f: g(f, "rev_acc", 0.10)),
    ("業種の勢い 上位10%（同じ業種の3カ月騰落率の中央値）", lambda f: g(f, "ind63_p", 0.90)),
    ("業種の3カ月騰落率の中央値 ≧+20%", lambda f: g(f, "ind63", 0.20)),
    ("相場全体が上昇局面（SPY＞200日線）", lambda f: f["spy_up"]),
    ("（逆）3カ月で−30%以上（急落後）", lambda f: g(f, "r63", None, -0.30)),
]

COMBOS = [
    ("① 3カ月で+50%以上 かつ 52週高値を更新",
     lambda f: g(f, "r63", 0.5) and f["new_hi"]),
    ("② ①＋売上の前年同期比≧20%",
     lambda f: g(f, "r63", 0.5) and f["new_hi"] and g(f, "rev", 0.2)),
    ("③ ①＋売上の伸びが加速",
     lambda f: g(f, "r63", 0.5) and f["new_hi"] and g(f, "rev_acc", 0.10)),
    ("④ ①＋業種の3カ月騰落率の中央値≧+20%",
     lambda f: g(f, "r63", 0.5) and f["new_hi"] and g(f, "ind63", 0.20)),
    ("⑤ 3カ月で+30%以上 かつ 52週高値 かつ 業種の中央値≧+20%",
     lambda f: g(f, "r63", 0.3) and f["new_hi"] and g(f, "ind63", 0.20)),
    ("⑥ 3カ月で+30%以上 かつ 52週高値 かつ 売上≧20% かつ 業種の中央値≧+15%",
     lambda f: g(f, "r63", 0.3) and f["new_hi"] and g(f, "rev", 0.2) and g(f, "ind63", 0.15)),
    ("⑦ 6カ月で+100%以上 かつ 52週高値（2倍の後の2倍）",
     lambda f: g(f, "r126", 1.0) and f["new_hi"]),
    ("⑧ ⑦＋売上≧20%",
     lambda f: g(f, "r126", 1.0) and f["new_hi"] and g(f, "rev", 0.2)),
    ("⑨ 3カ月で+50%以上 かつ 52週高値 かつ SPY＞200日線",
     lambda f: g(f, "r63", 0.5) and f["new_hi"] and f["spy_up"]),
    ("⑩ 3カ月で+50%以上 かつ 52週高値 かつ 売上≧20% かつ 業種≧+20% かつ SPY＞200日線",
     lambda f: g(f, "r63", 0.5) and f["new_hi"] and g(f, "rev", 0.2) and g(f, "ind63", 0.2) and f["spy_up"]),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default=DEFAULT_CACHE)
    ap.add_argument("--out")
    ap.add_argument("--summary")
    a = ap.parse_args()
    recs, weeks = build(a)
    base = summarize(recs)
    out = []
    w = out.append
    w("---\ntype: backtest\ntitle: 短い期間で2倍になる前の合図\n"
      f"created: {dt.date.today().isoformat()}\nscript: tools/backtest_onkabu_fast.py\n---\n")
    w("# 短い期間（3カ月〜1年）で2倍になる前の合図\n")
    if a.summary and os.path.exists(a.summary):
        w(open(a.summary).read())
    w("## 前提\n")
    w(f"- 毎週の最後の取引日（{weeks[0]}〜{weeks[-1]}）に、その日のS&P500の構成銘柄を数える（1銘柄1週＝1件）")
    w("- その日の終値で買ったとして、3カ月（63取引日）・6カ月（126取引日）・1年（252取引日）以内に終値で2倍になったか")
    w("- 特徴はすべてその日までに分かる値。売上は直近の四半期決算の前年同期比（SECへの提出日から使う）。業種は今のYahooの分類")
    w("- 同じ銘柄の上昇は何週も続けて数えるので、件数ほど独立した例はない。銘柄数と、前半（2014〜19年）・後半（2020年〜）の差で確かさを見る")
    w("- S&P500に入る前の銘柄は数えない（例: SNDKは2025年11月の採用から。採用前の上昇は入らない）。上場廃止の銘柄はデータがなく入らない\n")
    w("## 1. 合図ごとの比較\n")
    w(HEAD)
    w(row("**全体（合図なし）**", base, base))
    for label, fn in SINGLE:
        xs = [x for x in recs if fn(x["f"])]
        if xs:
            w(row(label, summarize(xs), base))
    w("\n## 2. 組み合わせ\n")
    w(HEAD)
    w(row("**全体（合図なし）**", base, base))
    for label, fn in COMBOS:
        xs = [x for x in recs if fn(x["f"])]
        if xs:
            w(row(label, summarize(xs), base))
    w("\n## 3. 例に挙げた銘柄で、合図②・⑤が最初に出た週\n")
    w("| 銘柄 | 合図 | 最初に出た週（その後の各上昇の始まり） |\n|---|---|---|")
    for s in ("MU", "SNDK", "DELL", "WDC", "STX", "NVDA", "AVGO", "PLTR"):
        for label, fn in COMBOS:
            if not (label.startswith("②") or label.startswith("⑤")):
                continue
            ds = sorted(x["d"] for x in recs if x["s"] == s and fn(x["f"]))
            firsts, prev = [], None
            for d in ds:
                if prev is None or (dt.date.fromisoformat(d) - dt.date.fromisoformat(prev)).days > 60:
                    firsts.append(d)
                prev = d
            w(f"| {s} | {label[:1]} | {', '.join(firsts[-8:]) if firsts else '出ていない'} |")
    text = "\n".join(out) + "\n"
    if a.out:
        os.makedirs(os.path.dirname(a.out), exist_ok=True)
        open(a.out, "w").write(text)
    print(text)


if __name__ == "__main__":
    main()
