#!/usr/bin/env python3
"""長い下げ（2000〜2002年・2007〜2009年）を含む期間で、テーマから外れる「静観」「上がっている業種に乗り換え」を確かめる（2026-11-22）。

ユーザーの指示「全て検証して最善策を提案して」（検証案 A）。これまでの「下げの時期に止める・乗り換えると年率が下がる」という結論は、
個別株のデータがある2015年〜（すぐ戻る下げしかない期間）から出たもので、長い下げでは確かめていなかった。
ここでは指数と業種ETF（1998年12月〜）で、銘柄の入れ替わりの偏り（生存者の偏り）なしに確かめる。

  index : テーマ（SOX、参考に NASDAQ100）を持つ形と、合図でテーマから外れる形（行き先: 短期国債／上がっている業種／守りの業種／S&P500）を比べる

データ: ~/.cache/stock_backtest/long/index/<記号>_full.json（[日付, 始値, 高値, 安値, 終値, 配当込みの調整後終値]）と CPIAUCSL.csv・PAYEMS.csv（FRED）。
売買は合図の日の引けで決め、次の取引日の終値から終値で数える（片道0.1%）。短期国債は ^IRX（13週の利回り）÷252 を毎日の利息とする。
数値の事実だけで、Claudeの売買判断は含まない。
使い方: tools/backtest_crash_mode.py index --out FILE
"""
import argparse
import bisect
import csv
import datetime as dt
import json
import os

LONG = os.path.expanduser("~/.cache/stock_backtest/long/index")
COST = 0.001
SECTORS = ["XLB", "XLE", "XLF", "XLI", "XLK", "XLP", "XLU", "XLV", "XLY"]
SEC_JA = {"XLB": "素材", "XLE": "エネルギー", "XLF": "金融", "XLI": "資本財", "XLK": "情報技術", "XLP": "生活必需品", "XLU": "公益", "XLV": "ヘルスケア", "XLY": "一般消費財"}
DEFENSIVE = ["XLP", "XLV", "XLU"]


def load(sym):
    rows = json.load(open(os.path.join(LONG, f"{sym}_full.json")))
    return {r[0]: (r[4], r[5]) for r in rows}   # 日付 → (終値, 調整後終値)


def fred(sid):
    out = []
    for r in csv.reader(open(os.path.join(LONG, f"{sid}.csv"))):
        try:
            out.append((r[0][:7], float(r[1])))
        except (ValueError, IndexError):
            pass
    return out


def sma_list(x, n):
    out, s = [None] * len(x), 0.0
    for i, v in enumerate(x):
        s += v
        if i >= n:
            s -= x[i - n]
        if i >= n - 1:
            out[i] = s / n
    return out


class Market:
    def __init__(self, start="1999-11-01"):
        raw = {s: load(s) for s in ["^SOX", "^GSPC", "SPY", "QQQ", "^IRX"] + SECTORS}
        cal = sorted(d for d in raw["SPY"] if d >= "1998-12-22" and all(d in raw[s] for s in ["^SOX", "^GSPC"] + SECTORS))
        self.cal = cal
        self.px = {s: [raw[s][d][0] if d in raw[s] else None for d in cal] for s in raw}
        self.tr = {s: [raw[s][d][1] if d in raw[s] else None for d in cal] for s in raw}
        # 前の値で埋める（短期国債・QQQ の欠け）
        for s in raw:
            for arr in (self.px[s], self.tr[s]):
                for i in range(1, len(arr)):
                    if arr[i] is None:
                        arr[i] = arr[i - 1]
        # SOX・S&P500 の長い線は、カレンダーより前の日も使って計算する
        self.ma = {}
        for s in ("^SOX", "^GSPC"):
            ds = sorted(raw[s])
            c = [raw[s][d][0] for d in ds]
            m200, m50 = sma_list(c, 200), sma_list(c, 50)
            pos = {d: k for k, d in enumerate(ds)}
            self.ma[s] = {"m200": [m200[pos[d]] for d in cal], "m50": [m50[pos[d]] for d in cal],
                          "m200p": [m200[pos[d] - 20] if pos[d] >= 220 else None for d in cal],
                          "m50p": [m50[pos[d] - 10] if pos[d] >= 60 else None for d in cal],
                          "hi60": [max(c[max(0, pos[d] - 59):pos[d] + 1]) for d in cal],
                          "up1y": [c[pos[d] - 60] / c[pos[d] - 310] - 1 if pos[d] >= 310 else None for d in cal]}
        self.sec_m200 = {s: sma_list(self.tr[s], 200) for s in SECTORS}
        self.i0 = next(i for i, d in enumerate(cal) if d >= start)
        self.special = self._special()

    def _special(self):
        """theme_scan.special_state と同じ定義の「特殊な下げ」（あり／なし）を毎日"""
        cpi, pay = fred("CPIAUCSL"), fred("PAYEMS")
        def avail(ym, dd):
            y, m = int(ym[:4]), int(ym[5:7]) + 1
            return f"{y + (m == 13):04d}-{(1 if m == 13 else m):02d}-{dd:02d}"
        c_av, p_av = [avail(ym, 20) for ym, _ in cpi], [avail(ym, 10) for ym, _ in pay]
        cv, pv = [v for _, v in cpi], [v for _, v in pay]
        c, M = self.px["^SOX"], self.ma["^SOX"]
        on, out = False, []
        for k, d in enumerate(self.cal):
            if not on:
                i = bisect.bisect_right(c_av, d) - 1
                j = bisect.bisect_right(p_av, d) - 1
                y, y3 = cv[i] / cv[i - 12] - 1, cv[i - 3] / cv[i - 15] - 1
                p3 = (pv[j] - pv[j - 3]) / 3
                up = M["up1y"][k]
                n = (up is not None and up >= 0.8) + (p3 < 100) + (y >= 0.035 and y > y3)
                if c[k] / M["hi60"][k] - 1 <= -0.15 and n >= 2:
                    on = True
            elif M["m50"][k] is not None and M["m50p"][k] is not None and c[k] > M["m50"][k] > M["m50p"][k]:
                on = False
            out.append(on)
        return out

    def ret(self, s, k):
        a, b = self.tr[s][k - 1], self.tr[s][k]
        return b / a - 1 if a and b else 0.0

    def cash(self, k):
        return (self.px["^IRX"][k - 1] or 0) / 100 / 252


def signals(m):
    S, G = m.ma["^SOX"], m.ma["^GSPC"]
    c, g = m.px["^SOX"], m.px["^GSPC"]
    below = lambda M, x, k: M["m200"][k] is not None and x[k] < M["m200"][k]
    falling = lambda M, k: M["m200p"][k] is not None and M["m200"][k] < M["m200p"][k]
    out = {
        "①SOXとS&P500が両方200日線の下": lambda k: below(S, c, k) and below(G, g, k),
        "②①かつS&P500の200日線が下向き": lambda k: below(S, c, k) and below(G, g, k) and falling(G, k),
        "③特殊な下げの印": lambda k: m.special[k],
        "④SOXが60日の最高値から−25%以下": lambda k: c[k] / S["hi60"][k] - 1 <= -0.25,
        "⑤SOXが200日線の下で200日線が下向き": lambda k: below(S, c, k) and falling(S, k),
    }
    back = {
        "SOXが200日線を上回る": lambda k: S["m200"][k] is not None and c[k] > S["m200"][k],
        "SOXが上向きの50日線を上回る": lambda k: S["m50p"][k] is not None and c[k] > S["m50"][k] > S["m50p"][k],
    }
    return out, back


def dest_weights(m, kind, k):
    """テーマから外れている間の持ち方（その日の引けで決める）"""
    if kind == "短期国債":
        return {}
    if kind == "S&P500":
        return {"SPY": 1.0}
    if kind == "守りの業種":
        return {s: 1 / 3 for s in DEFENSIVE}
    # 上がっている業種: 9業種のうち、3か月（63取引日）の上げが大きい順に2つ。200日線より下・3か月がマイナスの業種は短期国債
    sc = []
    for s in SECTORS:
        a, b, mm = m.tr[s][k - 63], m.tr[s][k], m.sec_m200[s][k]
        if a and mm and b > mm and b / a - 1 > 0:
            sc.append((b / a - 1, s))
    sc.sort(reverse=True)
    return {s: 0.5 for _, s in sc[:2]}


def run(m, theme="^SOX", out_sig=None, back_sig=None, dest="短期国債", lo=None, hi=None, log=None):
    """テーマを持ち、out_sig が出たら dest に移り、back_sig で戻る。(日付の列, 資金の列, 外れていた日の割合, 切り替えの回数)"""
    lo = lo or m.i0
    hi = hi or len(m.cal) - 1
    eq, curve, out, w, nsw, n_out, month = 1.0, [], False, {theme: 1.0}, 0, 0, None
    for k in range(lo, hi + 1):
        if k > lo:
            r = sum(wt * m.ret(s, k) for s, wt in w.items()) + (1 - sum(w.values())) * m.cash(k)
            eq *= 1 + r
        curve.append(eq)
        if out_sig is None:
            continue
        # 引けで決める
        new_out = out
        if not out and out_sig(k):
            new_out = True
        elif out and back_sig(k):
            new_out = False
        mo = m.cal[k][:7]
        if new_out != out or (new_out and mo != month):
            nw = dest_weights(m, dest, k) if new_out else {theme: 1.0}
            turn = sum(abs(nw.get(s, 0) - w.get(s, 0)) for s in set(nw) | set(w))
            eq *= 1 - COST * turn
            if new_out != out:
                nsw += 1
                if log is not None:
                    log.append((m.cal[k], "外れる" if new_out else "戻る", ",".join(f"{SEC_JA.get(s, s)}" for s in nw) if new_out else ""))
            w, month = nw, mo
        out = new_out
        n_out += out
    return curve, n_out / max(1, hi - lo + 1), nsw


def stats(m, curve, lo):
    n = len(curve)
    yrs = (dt.date.fromisoformat(m.cal[lo + n - 1]) - dt.date.fromisoformat(m.cal[lo])).days / 365.25
    cagr = curve[-1] ** (1 / yrs) - 1 if yrs > 0 else 0
    peak, mdd = 0, 0
    for v in curve:
        peak = max(peak, v)
        mdd = max(mdd, 1 - v / peak)
    return cagr, mdd


def window(m, curve, lo, a, b):
    ka = next(i for i, d in enumerate(m.cal) if d >= a) - lo
    kb = max(i for i, d in enumerate(m.cal) if d <= b) - lo
    return curve[kb] / curve[ka] - 1


EPIS = [("2000〜02年（ITバブルの崩壊）", "2000-03-10", "2002-10-09", "長い"), ("2007〜09年（金融危機）", "2007-10-09", "2009-03-09", "長い"),
        ("2015〜16年", "2015-06-01", "2016-02-11", "すぐ戻る"), ("2018年秋", "2018-09-14", "2018-12-24", "すぐ戻る"),
        ("2020年（コロナ）", "2020-02-19", "2020-03-23", "すぐ戻る"), ("2022年", "2021-12-27", "2022-10-14", "長め"),
        ("2024年夏", "2024-07-10", "2024-08-07", "すぐ戻る"), ("2025年春", "2025-02-18", "2025-04-08", "すぐ戻る"),
        ("2026年7月", "2026-06-18", "2026-07-29", "すぐ戻る"), ("今回（10/9〜11/20）", "2026-10-09", "2026-11-20", "?")]
# 戻りを取り逃すかを見るため、下げの底から1年（取引日250日）の成績も出す
RECOV = [("2002-10-09", "ITバブルの底から1年"), ("2009-03-09", "金融危機の底から1年"), ("2016-02-11", "2016年の底から1年"), ("2018-12-24", "2018年の底から1年"),
         ("2020-03-23", "コロナの底から1年"), ("2022-10-14", "2022年の底から1年"), ("2024-08-07", "2024年夏の底から1年"), ("2025-04-08", "2025年春の底から半年")]


def cmd_index(a):
    m = Market()
    lo = m.i0
    out, back = signals(m)
    forms = [("SOXを持ち続ける", dict(theme="^SOX")), ("NASDAQ100（QQQ）を持ち続ける", dict(theme="QQQ")), ("S&P500（SPY）を持ち続ける", dict(theme="SPY"))]
    for on, of in out.items():
        backs = [("特殊な下げの印が消える", lambda k: not m.special[k])] if on.startswith("③") else []
        backs += list(back.items())
        for bn, bf in backs:
            for dn in ("短期国債", "上がっている業種", "守りの業種", "S&P500"):
                forms.append((f"{on} → {dn}（戻す: {bn}）", dict(theme="^SOX", out_sig=of, back_sig=bf, dest=dn)))
    res = []
    split = next(i for i, d in enumerate(m.cal) if d >= "2013-01-01")
    for nm, kw in forms:
        curve, frac, nsw = run(m, **kw)
        cagr, mdd = stats(m, curve, lo)
        c1, d1 = stats(m, curve[:split - lo + 1], lo)
        c2_, d2 = stats(m, [v / curve[split - lo] for v in curve[split - lo:]], split)
        res.append(dict(nm=nm, kw=kw, curve=curve, cagr=cagr, mdd=mdd, c1=c1, d1=d1, c2=c2_, d2=d2, frac=frac, nsw=nsw))
    base = res[0]
    L = []
    w = L.append
    w("# 長い下げを含む期間で、テーマから外れる「静観」「乗り換え」を確かめる（指数と業種ETF、1999年11月〜2026年11月20日）\n")
    w("2026-11-22 ユーザーの指示「全て検証して最善策を提案して」（検証案A）。これまでの「止める・乗り換えると年率が下がる」という結論は、個別株のデータがある"
      "2015年〜（すぐ戻る下げしかない期間）から出たもので、2000〜2002年・2007〜2009年のような長い下げでは確かめていなかった。ここでは指数と業種ETF"
      "（S&P500の9業種のSPDR、1998年12月〜）で、銘柄の入れ替わりの偏りなしに確かめる。テーマはSOX（半導体指数）で代用する（ツールの個別株の売買そのものではない。"
      "個別株は検証案B）。\n")
    w("- 外れる合図はその日の引けで判定し、次の取引日から持ち方を変える（終値から終値。片道0.1%）。外れている間は毎月の初めに持ち方を決め直す。")
    w("- 行き先: 短期国債（^IRX の利回り）／上がっている業種（9業種のうち3か月の上げが大きい順に2つ、200日線より上で3か月がプラスのものだけ。足りない分は短期国債）／"
      "守りの業種（生活必需品・ヘルスケア・公益を3分の1ずつ）／S&P500（SPY）。")
    w("- 特殊な下げの印は毎朝のツールと同じ定義（SOXが60日の最高値から−15%以下、かつ「前の1年の上げ+80%以上・雇用の伸び10万人未満・物価3.5%以上で再加速」のうち2つ以上。"
      "条件は過去の下げを見て選んだもので後知恵を含む）。\n")
    w("## 1. 全部の形（年率の高い順）\n")
    w("| 形 | 年率（1999/11〜） | 最大下落率 | 1999〜2012年 年率 / 最大下落率 | 2013年〜 年率 / 最大下落率 | テーマの外にいた日 | 切り替えの回数 |")
    w("|---|---|---|---|---|---|---|")
    for x in sorted(res, key=lambda x: -x["cagr"]):
        w(f"| {x['nm']} | {x['cagr'] * 100:+.1f}% | {x['mdd'] * 100:.0f}% | {x['c1'] * 100:+.1f}% / {x['d1'] * 100:.0f}% | {x['c2'] * 100:+.1f}% / {x['d2'] * 100:.0f}% | "
          f"{x['frac'] * 100:.0f}% | {x['nsw']} |")
    # 両方の期間でSOXを持ち続けるより年率が高く、最大下落率も小さい形
    good = [x for x in res[3:] if x["c1"] > base["c1"] and x["c2"] > base["c2"] and x["mdd"] < base["mdd"]]
    w(f"\n両方の期間（1999〜2012年・2013年〜）で SOX を持ち続けるより年率が高く、全期間の最大下落率も小さい形: **{len(good)}形 / {len(res) - 3}形**\n")
    top = sorted(good, key=lambda x: -(x["c1"] + x["c2"]))[:3] or sorted(res[3:], key=lambda x: -x["cagr"])[:3]
    # 合図（①〜⑤）ごと・行き先ごとに、全期間の年率が一番高い形も並べる
    fam = {}
    for x in res[3:]:
        key = (x["nm"][0], x["kw"]["dest"])
        if key not in fam or x["cagr"] > fam[key]["cagr"]:
            fam[key] = x
    best_sig = [max((x for (s_, _), x in fam.items() if s_ == s0), key=lambda x: x["cagr"]) for s0 in "①②③④⑤" if any(k[0] == s0 for k in fam)]
    show = [base, res[1], res[2]] + [x for x in best_sig if x not in top] + top
    w("## 1-2. 行き先ごとの平均（合図と戻し方の全部の形の平均）\n")
    w("| 行き先 | 形の数 | 年率 | 最大下落率 | 1999〜2012年 年率 | 2013年〜 年率 |")
    w("|---|---|---|---|---|---|")
    for dn in ("短期国債", "上がっている業種", "守りの業種", "S&P500"):
        g_ = [x for x in res[3:] if x["kw"]["dest"] == dn]
        w(f"| {dn} | {len(g_)} | {sum(x['cagr'] for x in g_) / len(g_) * 100:+.1f}% | {sum(x['mdd'] for x in g_) / len(g_) * 100:.0f}% | "
          f"{sum(x['c1'] for x in g_) / len(g_) * 100:+.1f}% | {sum(x['c2'] for x in g_) / len(g_) * 100:+.1f}% |")
    w("")
    w("## 2. 下げの時期ごとの損益（上の良い形と、持ち続ける形）\n")
    w("| 形 | " + " | ".join(f"{e[0]}（{e[3]}）" for e in EPIS) + " |")
    w("|---|" + "---|" * len(EPIS))
    for x in show:
        w(f"| {x['nm']} | " + " | ".join(f"{window(m, x['curve'], lo, e[1], e[2]) * 100:+.0f}%" for e in EPIS) + " |")
    w("\n## 3. 下げの底からの戻り（取り逃しの大きさ）\n")
    w("| 形 | " + " | ".join(r[1] for r in RECOV) + " |")
    w("|---|" + "---|" * len(RECOV))
    for x in show:
        cells = []
        for d0, _ in RECOV:
            k0 = next(i for i, d in enumerate(m.cal) if d >= d0)
            k1 = min(len(m.cal) - 1, k0 + (125 if "半年" in _ else 250))
            cells.append(f"{(x['curve'][k1 - lo] / x['curve'][k0 - lo] - 1) * 100:+.0f}%")
        w(f"| {x['nm']} | " + " | ".join(cells) + " |")
    w("\n## 4. 年ごとの損益\n")
    yrs = sorted({d[:4] for d in m.cal[lo:]})
    w("| 形 | " + " | ".join(yrs) + " |")
    w("|---|" + "---|" * len(yrs))
    for x in show:
        cells = []
        for y in yrs:
            ks = [i for i in range(lo, len(m.cal)) if m.cal[i][:4] == y]
            k0 = ks[0] - 1 if ks[0] > lo else ks[0]
            cells.append(f"{(x['curve'][ks[-1] - lo] / x['curve'][k0 - lo] - 1) * 100:+.0f}")
        w(f"| {x['nm']} | " + " | ".join(cells) + " |")
    w("\n## 5. 良い形の切り替えの記録（直近）\n")
    for x in top[:4]:
        lg = []
        run(m, log=lg, **x["kw"])
        w(f"- {x['nm']}: " + "、".join(f"{d} {act}{'（' + to + '）' if to else ''}" for d, act, to in lg[-8:]))
    k = len(m.cal) - 1
    S = m.ma["^SOX"]
    w(f"\n## 6. 今（{m.cal[k]}）の合図\n")
    for on, of in out.items():
        w(f"- {on}: {'**出ている**' if of(k) else '出ていない'}")
    w(f"- SOX {m.px['^SOX'][k]:,.0f}（200日線 {S['m200'][k]:,.0f}、50日線 {S['m50'][k]:,.0f}、60日の最高値から {(m.px['^SOX'][k] / S['hi60'][k] - 1) * 100:+.1f}%）")
    dw = dest_weights(m, "上がっている業種", k)
    w(f"- 上がっている業種（200日線より上で3か月がプラス、上げの大きい順に2つ）: " + ("、".join(f"{SEC_JA[s]}（{s}、3か月 {(m.tr[s][k] / m.tr[s][k - 63] - 1) * 100:+.1f}%）" for s in dw) or "なし（短期国債）"))
    w("\n- この結果は数値を条件どおりに計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    txt = "\n".join(L) + "\n"
    if a.out:
        open(a.out, "w", encoding="utf-8").write(txt)
    print(txt)


def special_dates(dates, c):
    """毎朝のツール（theme_scan.special_state）と同じ「特殊な下げ」の印が出ている日の集合。dates・c は SOX の日付と終値（310日以上前から）"""
    cpi, pay = fred("CPIAUCSL"), fred("PAYEMS")
    def avail(ym, dd):
        y, m = int(ym[:4]), int(ym[5:7]) + 1
        return f"{y + (m == 13):04d}-{(1 if m == 13 else m):02d}-{dd:02d}"
    c_av, p_av = [avail(ym, 20) for ym, _ in cpi], [avail(ym, 10) for ym, _ in pay]
    cv, pv = [v for _, v in cpi], [v for _, v in pay]
    m50 = sma_list(c, 50)
    on, out = False, set()
    for k in range(320, len(c)):
        d = dates[k]
        if not on:
            i = bisect.bisect_right(c_av, d) - 1
            j = bisect.bisect_right(p_av, d) - 1
            y, y3 = cv[i] / cv[i - 12] - 1, cv[i - 3] / cv[i - 15] - 1
            p3 = (pv[j] - pv[j - 3]) / 3
            up = c[k - 60] / c[k - 310] - 1
            n = (up >= 0.8) + (p3 < 100) + (y >= 0.035 and y > y3)
            if c[k] / max(c[k - 59:k + 1]) - 1 <= -0.15 and n >= 2:
                on = True
        elif c[k] > m50[k] > m50[k - 10]:
            on = False
        if on:
            out.add(d)
    return out


def market_flags(cache):
    """{名前: 合図が出ている日の集合}（その日の引けで判定）。①SOXとS&P500が両方200日線の下、⑤SOXが下向きの200日線の下、③特殊な下げの印"""
    from backtest_lib import load_prices
    sx, gs = load_prices(cache, "^SOX"), load_prices(cache, "^GSPC")
    def below(d):
        m = sma_list(d["c"], 200)
        return {d["date"][k]: (m[k] is not None and d["c"][k] < m[k], m[k] is not None and k >= 220 and m[k - 20] is not None and m[k] < m[k - 20])
                for k in range(len(d["c"]))}
    bs_, bg_ = below(sx), below(gs)
    f1 = {d for d, (b, _) in bs_.items() if b and bg_.get(d, (False, False))[0]}
    f5 = {d for d, (b, f) in bs_.items() if b and f}
    return {"①": f1, "⑤": f5, "③": special_dates(sx["date"], sx["c"])}


def irx_daily():
    rows = json.load(open(os.path.join(LONG, "^IRX_full.json")))
    return {r[0]: r[4] / 100 / 252 for r in rows}


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("index")
    p.add_argument("--out")
    a = ap.parse_args()
    {"index": cmd_index}[a.cmd](a)


if __name__ == "__main__":
    main()
