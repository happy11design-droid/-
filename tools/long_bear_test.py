#!/usr/bin/env python3
"""長い下げ（2000〜2002年・2008年など）の中で、今のルール（押し目B・急落の底C・ミネルヴィニM・新高値V2）が稼げていたかを、1996年〜の日足で確かめる
（2026-11-20 ユーザーの質問「アンソロピックの上場も失敗し、AI半導体株が下がり続けています。それでもなおAI半導体株を買った方が利益が出るのですか？」
→ 長い下げが2015年〜のデータにないので、1996年〜で確かめると提案 →「はい。全て検証して」）

データ: tools/long_stocks.py で取った 1990年〜の日足（~/.cache/stock_backtest/long/stocks/）。今のS&P500の構成銘柄と87銘柄（今の会社だけ＝生き残りの偏り）。
銘柄の一覧:
  A = テーマ監視銘柄（87銘柄。今の毎朝のツールと同じ固定の一覧。後知恵あり）
  O = それ以外の今のS&P500の構成銘柄。その日にS&P500の構成銘柄だった期間だけ使う（members.csv。1996年〜）
ルールの合図と手じまいは backtest_retest.py と同じ部品（bs.simulate＋b3_exit、gen_trades、損切りは日中の逆指値15%）。
**入れていないもの**: 順張りの半分売り・かぶせ線・押し目と急落の底の大陰線の売り・2倍ETF・同じ業種2銘柄までの上限以外の細かい決まり。
流動性: 株価5ドル以上の条件は、昔の株価が分割で小さく見えるので使わず、50日平均の売買代金200万ドル以上にした。
資金: 4枠・1銘柄＝その日の資金÷4、同じ業種2銘柄まで、片道0.1%。同じ日の候補は形ごとの順（下の FORMS）で、RSの高い順。
乱数: 候補の25%を乱数で見送る（取れなかった注文の代わり）×10通り。1年の区切り（250取引日、10取引日ずつずらす）は空の枠から始める。
使い方: python3 tools/long_bear_test.py [--out md] [--seeds 10]
"""
import argparse
import bisect
import csv
import datetime as dt
import json
import os
import random
import re
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_compare2 as c2
import backtest_crash as bcr
import backtest_figures2 as f2
import backtest_industry as bi
import backtest_lib as bl
import backtest_minervini2 as bm2
import backtest_modern as bmo
import backtest_swing as bs
import backtest_trend as bt
from backtest_lib import COSTS, gen_trades, sma

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = os.path.expanduser("~/.cache/stock_backtest/")
LS = C + "long/stocks/"
COST = COSTS[2]
STOP = 0.15
START = "1996-01-02"
ETFS = ("SPY", "QQQ", "SMH", "SOXX", "XLK")


def load_long(sym):
    p = LS + sym + ".json"
    if not os.path.exists(p):
        return None
    rows = json.load(open(p))
    d = {"date": [], "o": [], "h": [], "l": [], "c": [], "v": []}
    for r in rows:
        f = r[6] / r[4] if r[4] else 1.0
        d["date"].append(r[0])
        for k, x in zip(("o", "h", "l", "c"), r[1:5]):
            d[k].append(x * f)
        d["v"].append(r[5])
    return d


def watch87():
    md = open(os.path.join(ROOT, "新分析ツール", "テーマ監視銘柄.md"), encoding="utf-8").read()
    return {m.group(1) for m in re.finditer(r"(?m)^\| ([A-Z][A-Z0-9.\-]*) \|", md) if m.group(1) != "ティッカー"}


def sox_series():
    """^SOX の終値: long/index（1994年〜）に prices/（2013年〜の新しい日）を足す"""
    a = {r[0]: r[1] for r in json.load(open(C + "long/index/^SOX.json"))}
    b = bl.load_prices(C, "^SOX")
    if b:
        for d, c in zip(b["date"], b["c"]):
            if d not in a:
                a[d] = c
    return a


def gspc_series():
    a = {r[0]: r[1] for r in json.load(open(C + "long/index/^GSPC.json"))}
    b = bl.load_prices(C, "^GSPC")
    if b:
        for d, c in zip(b["date"], b["c"]):
            a.setdefault(d, c)
    return a


def fred(sid):
    out = []
    for r in list(csv.reader(open(C + f"long/index/{sid}.csv")))[1:]:
        try:
            out.append((r[0][:7], float(r[1])))
        except (ValueError, IndexError):
            pass
    return out


def special_days(sox_d, sox_c):
    """theme_scan.special_state と同じ判定を毎日に当てる: {日付: True}（その日の引けで「あり」）"""
    cpi, pay = fred("CPIAUCSL"), fred("PAYEMS")

    def avail(ym, dd):
        y, m = int(ym[:4]), int(ym[5:7]) + 1
        return f"{y + (m == 13):04d}-{(1 if m == 13 else m):02d}-{dd:02d}"
    c_av, p_av = [avail(ym, 20) for ym, _ in cpi], [avail(ym, 10) for ym, _ in pay]
    cv, pv = [v for _, v in cpi], [v for _, v in pay]
    c = sox_c
    on, out, nab = False, {}, {}
    for k in range(320, len(c)):
        d = sox_d[k]
        m50, m50p = sum(c[k - 49:k + 1]) / 50, sum(c[k - 59:k - 9]) / 50
        if not on:
            i = bisect.bisect_right(c_av, d) - 1
            j = bisect.bisect_right(p_av, d) - 1
            y, y3 = cv[i] / cv[i - 12] - 1, cv[i - 3] / cv[i - 15] - 1
            p3 = (pv[j] - pv[j - 3]) / 3
            up = c[k - 60] / c[k - 310] - 1
            n_ = (up >= 0.8) + (p3 < 100) + (y >= 0.035 and y > y3)
            if c[k] / max(c[k - 59:k + 1]) - 1 <= -0.15 and n_ >= 2:
                on = True
        elif c[k] > m50 > m50p:
            on = False
        out[d] = on
    return out


def sox_bears(sox_d, sox_c, th=0.40, rec=1.0):
    """SOXの終値の大きな下げ: [(高値の日, 底の日, 下げ, 高値を戻した日)]。
    高値から th 以上下げた局面を、底から rec（+100%）戻すか高値を戻すまでを1つとして数える
    （2026-11-20: 高値を戻すまでで区切ると 2000年の高値から2008年の底まで（17年）が1つになったため、2000〜2002年と2007〜2008年を分けた）"""
    eps, pk, pkd, k, n = [], sox_c[0], sox_d[0], 0, len(sox_c)
    while k < n:
        if sox_c[k] >= pk:
            pk, pkd = sox_c[k], sox_d[k]
            k += 1
            continue
        if sox_c[k] / pk - 1 > -th:
            k += 1
            continue
        lo, lod, j = sox_c[k], sox_d[k], k
        while j < n and sox_c[j] < pk and sox_c[j] < lo * (1 + rec):
            if sox_c[j] < lo:
                lo, lod = sox_c[j], sox_d[j]
            j += 1
        kl = sox_d.index(lod)   # 高値は底の前の3年（750取引日）の中の最高値にする（2004〜2007年の横ばいを下げに入れないため）
        kp = max(range(max(0, kl - 750), kl + 1), key=lambda x: sox_c[x])
        eps.append((sox_d[kp], lod, lo / sox_c[kp] - 1, next((sox_d[x] for x in range(kl, n) if sox_c[x] >= sox_c[kp]), None)))
        if j >= n:
            break
        pk, pkd, k = sox_c[j], sox_d[j], j   # 戻った日から新しい高値を数え直す
    return eps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="新分析ツール/バックテスト結果/実際の運用の期間の確認_2026-10-23/長い下げの中で今のルールを確かめる（1996年〜）.md")
    ap.add_argument("--seeds", type=int, default=10)
    a = ap.parse_args()
    bl.KEEP_OPEN, bl.OVERLAP = True, True
    W87 = watch87()
    mem_sp = bl.load_members(C)   # S&P500 の構成期間（1996年〜）
    syms = sorted(f[:-5] for f in os.listdir(LS) if f.endswith(".json"))
    data = {}
    for s in syms:
        d = load_long(s)
        if d and len(d["c"]) > 300:
            data[s] = d
    gs = gspc_series()
    f2.SPX.update(gs)
    for s, d in data.items():
        c2.prep(d)
        bmo.prep(d, f2.SPX)
        f2.prep(d)
        for n in (5, 50):
            d[f"ma{n}"] = d.get(f"ma{n}") or sma(d["c"], n)
        d["ma150"] = sma(d["c"], 150)
        d["sym"] = s
    members = {s: [(data[s]["date"][0], "9999-12-31")] for s in data}
    stocks = [s for s in data if s not in ETFS]
    bt.add_rs_rank({s: data[s] for s in stocks}, members)
    u = json.load(open(C + "universe.json"))
    if os.path.exists(C + "industry_extra.json"):
        u.update(json.load(open(C + "industry_extra.json")))
    ind = {s: (u.get(s) or {}).get("industry") for s in data}
    for s in data:
        data[s]["ind"] = ind.get(s)
    IR = bi.industry_ranks({s: data[s] for s in stocks}, members)
    spy = data["SPY"]
    days = [d for d in spy["date"] if d >= START]
    di = {d: k for k, d in enumerate(days)}
    prevd = {days[k]: days[k - 1] for k in range(1, len(days))}
    print(f"準備ができた: {len(data)} 銘柄、{days[0]}〜{days[-1]}", file=sys.stderr)

    A = {s for s in stocks if s in W87}
    O = {s for s in stocks if s not in W87}
    liq = lambda s_, i: s_["vol50"][i] is not None and s_["vol50"][i] * s_["c"][i] >= 2e6
    in_sp = lambda s_, i: bl.is_member(mem_sp.get(s_["sym"], []), s_["date"][i])
    okA = lambda s_, i, sp: s_["sym"] in A and liq(s_, i)
    okO = lambda s_, i, sp: s_["sym"] in O and liq(s_, i) and in_sp(s_, i)
    okAll = lambda s_, i, sp: okA(s_, i, sp) or okO(s_, i, sp)
    okE = lambda s_, i, sp: s_["sym"] in ETFS

    # テーマの外（毎朝の theme_scan.py の空き枠の候補・backtest_retest の OPT_OUTSIDE と同じ）: S&P500の構成銘柄で87銘柄でないもの、
    # RS≧90・終値＞150日線＞20日前の150日線・業種の3カ月の強さが上位20%
    elig = {}
    for s in O:
        s_ = data[s]
        c_, m150 = s_["c"], s_["ma150"]
        for i in range(170, len(c_)):
            r_ = s_["rs"][i]
            if r_ is None or r_ < 90 or m150[i] is None or m150[i - 20] is None or not (c_[i] > m150[i] > m150[i - 20]):
                continue
            if not liq(s_, i) or not in_sp(s_, i):
                continue
            rk = IR.get(s_["date"][i], {}).get(ind.get(s))
            if rk is None or rk > 0.2:
                continue
            elig.setdefault(s_["date"][i], {})[s] = r_
    okOut = lambda s_, i, sp: s_["sym"] in elig.get(s_["date"][i], ())

    # 新高値V2 の「RSの上位10銘柄」（その週の前の金曜の順位。backtest_combo2 と同じ考え方）
    fridays = [d for k, d in enumerate(days) if k + 1 == len(days) or dt.date.fromisoformat(days[k + 1]).isocalendar()[1] != dt.date.fromisoformat(d).isocalendar()[1]]
    pos = {s: {d: k for k, d in enumerate(v["date"])} for s, v in data.items()}

    def top10(pool_fn):
        out = {}
        for f in fridays:
            xs = []
            for s in stocks:
                k = pos[s].get(f)
                if k is None:
                    continue
                if pool_fn(data[s], k):
                    xs.append((data[s]["rs"][k] or 0, s))
            out[f] = {s for _, s in sorted(xs, reverse=True)[:10]}
        week_of, fi, last = {}, 0, None
        for d in days:
            while fi < len(fridays) and fridays[fi] < d:
                last = fridays[fi]
                fi += 1
            week_of[d] = last
        return lambda s_, i, sp: s_["sym"] in out.get(week_of.get(s_["date"][i]), ())
    ok10A = top10(lambda s_, k: okA(s_, k, None))
    ok10O = top10(lambda s_, k: okO(s_, k, None))
    ok10All = top10(lambda s_, k: okAll(s_, k, None))
    ok10Out = top10(lambda s_, k: okOut(s_, k, None))

    below50 = lambda j, s, k, px: s["ma50"][j] is not None and s["c"][j] < s["ma50"][j]
    above5 = lambda j, s, k, px: s["ma5"][j] is not None and s["c"][j] > s["ma5"][j]
    v2o = bmo.with_(c2.V2, f2.O)

    def CR(i, s):
        rr, r2 = bcr.drop(i, s), s["rsi2"][i]
        return rr if rr <= -0.15 and r2 is not None and r2 <= 10 and bcr.was_strong(i, s) else None

    def b3_exit(t):
        s = data[t["sym"]]
        o, h, l, c = s["o"], s["h"], s["l"], s["c"]
        i0, n, px = pos[t["sym"]][t["in"]], len(c), t["px"]
        if i0 >= n - 1:
            return None
        floor, pend, j = px * (1 - STOP), False, i0
        while j < n:
            if pend:
                return j, o[j], False
            if l[j] <= floor:
                return j, min(o[j] if j > i0 else px, floor), True
            if j > i0 and s["bb_up"][j - 1] is not None and h[j] >= s["bb_up"][j - 1]:
                return j, max(o[j], s["bb_up"][j - 1]), False
            if j + 1 >= n:
                return j, c[j], False
            if j - i0 >= bs.MAX_HOLD or (s["pctb"][j] is not None and s["pctb"][j] >= 1.0):
                pend = True
            j += 1
        return None

    def mk(sym, i0, i1, px, xp, rule, stopped):
        s = data[sym]
        if i1 == i0:
            path = {s["date"][i0]: (1 - COST) ** 2 * xp / px}
        else:
            path = {s["date"][j]: (1 - COST) * s["c"][j] / px for j in range(i0, i1)}
            path[s["date"][i1]] = (1 - COST) ** 2 * xp / px
        sd = s["date"][i0 - 1] if i0 > 0 else s["date"][i0]   # 合図の日（前の取引日の引け）
        return {"sym": sym, "rule": rule, "in": s["date"][i0], "out": s["date"][i1], "sd": sd, "path": path, "ret": path[s["date"][i1]] - 1,
                "stopped": stopped, "rs": s["rs"][i0 - 1] if i0 > 0 and s["rs"][i0 - 1] is not None else 0, "ind": ind.get(sym)}

    def gen_B(ok):
        old, bs.STOP_MAX = bs.STOP_MAX, STOP
        try:
            raw = bs.simulate(data, members, bs.O_method3, bs.X_upper_band, START, days[-1], ok=ok)
        finally:
            bs.STOP_MAX = old
        out = []
        for t in raw:
            x = b3_exit(t)
            if x:
                out.append(mk(t["sym"], pos[t["sym"]][t["in"]], x[0], t["px"], x[1], "B", x[2]))
        return out

    def gen_G(entry, exit_, ok, rule, mh=500):
        out = []
        for t in gen_trades(data, members, entry, exit_, START, days[-1], ok=ok, fill="open", max_hold=mh, stop_pct=STOP):
            s = data[t["sym"]]
            i0, i1 = pos[t["sym"]][t["in"]], pos[t["sym"]][t["out"]]
            px, xp, stopped = t["px"], t["px"] * (1 + t["ret"]), t["why"] == "損切り"
            floor = px * (1 - STOP)
            for j in range(i0, i1):   # 損切りは日中の逆指値15%（backtest_retest の intraday と同じ）
                if s["l"][j] <= floor:
                    i1, xp, stopped = j, min(s["o"][j] if j > i0 else px, floor), True
                    break
            out.append(mk(t["sym"], i0, i1, px, xp, rule, stopped))
        return out

    def gen_set(ok, ok10, tag):
        tr = gen_B(ok) + gen_G(CR, above5, ok, "C", 60) + gen_G(bm2.E_base(2.0), below50, ok, "M") + gen_G(v2o, below50, ok10, "V")
        for t in tr:
            t["set"] = tag
        print(f"{tag}: 売買 {len(tr)}（" + "、".join(f"{r} {sum(1 for t in tr if t['rule'] == r)}" for r in "BCMV") + "）", file=sys.stderr)
        return tr

    TA = gen_set(okA, ok10A, "A")
    TO = gen_set(okO, ok10O, "O")
    TOut = gen_set(okOut, ok10Out, "Out")
    VAll = [dict(t, set="All") for t in gen_G(v2o, below50, ok10All, "V")]
    TE = gen_B(okE) + gen_G(CR, above5, okE, "C", 60) + gen_G(bm2.E_base(2.0), below50, okE, "M")
    for t in TE:
        t["set"] = "ETF"

    sox_m = sox_series()
    sx_d = sorted(sox_m)
    sx_c = [sox_m[d] for d in sx_d]
    SP = special_days(sx_d, sx_c)
    sxi = {d: k for k, d in enumerate(sx_d)}

    def sox_dn50(d):   # SOXが下向きの50日線の下（その日の引け）
        k = sxi.get(d)
        if k is None or k < 60:
            return False
        m50, m50p = sum(sx_c[k - 49:k + 1]) / 50, sum(sx_c[k - 59:k - 9]) / 50
        return sx_c[k] < m50 and m50 < m50p
    sp_on = lambda d: SP.get(d, False)

    # 形: (名前, 候補を作る関数) 候補 = [(優先, 売買)]
    def F_now():
        return [(0, t) for t in TA] + [(1, t) for t in TOut]
    FORMS = [
        ("① 今のツール（87銘柄＋テーマの外、87銘柄を先に）", F_now()),
        ("② 87銘柄だけ（テーマの外なし）", [(0, t) for t in TA]),
        ("③ ほかの業種だけ（87銘柄でないS&P500。テーマを変えた場合）", [(0, t) for t in TO]),
        ("④ 全部をRSの高い順（AI半導体を先にしない）", [(0, t) for t in TA if t["rule"] != "V"] + [(0, t) for t in TO if t["rule"] != "V"] + [(0, t) for t in VAll]),
        ("⑤ 特殊な下げの間は87銘柄を買わない（テーマの外だけ）", [(0, t) for t in TA if not sp_on(t["sd"])] + [(1, t) for t in TOut]),
        ("⑥ 特殊な下げの間は何も買わない", [(0, t) for t in TA if not sp_on(t["sd"])] + [(1, t) for t in TOut if not sp_on(t["sd"])]),
        ("⑦ 特殊な下げの間はほかの業種全部から買う（テーマを変える）", [(0, t) for t in TA if not sp_on(t["sd"])] + [(1, t) for t in TOut if not sp_on(t["sd"])]
         + [(0, t) for t in TO if sp_on(t["sd"])]),
        ("⑧ SOXが下向きの50日線の下の間は87銘柄を買わない", [(0, t) for t in TA if not sox_dn50(t["sd"])] + [(1, t) for t in TOut]),
        ("⑨ 特殊な下げの間は87銘柄の順張りだけ買わない（逆張りは買う）", [(0, t) for t in TA if not (sp_on(t["sd"]) and t["rule"] in ("M", "V"))] + [(1, t) for t in TOut]),
    ]

    CBK, WCAP, WSZ, MIXES = {}, {}, {}, {}   # 形の名前 → 損切りが続いたら止める形 (件数, 損の件数, 止める取引日 or "sox20", 数え方 "loss"=損で終わった売買・"stop"=15%の損切りだけ)
    if os.environ.get("LBT_EXTRA") == "1":
        # 2026-11-22 ユーザーの指示「全て検証して最善策を考えて」: 87銘柄の固定の一覧のまま、長い下げで崩れたテーマを買い続けないための形と、止める形を比べる
        def at(t_):
            s_ = data[t_["sym"]]
            return s_, pos[t_["sym"]].get(t_["sd"])
        def up150(t_):   # 合図の日に、その銘柄の150日線（30週線）が20取引日前より上
            s_, k = at(t_)
            return k is not None and k >= 170 and s_["ma150"][k] is not None and s_["ma150"][k - 20] is not None and s_["ma150"][k] > s_["ma150"][k - 20]
        def strong(t_, n=80):  # 150日線が上向きで、RS≧n
            s_, k = at(t_)
            return up150(t_) and k is not None and (s_["rs"][k] or 0) >= n
        def dn50(t_):    # 合図の日に、その銘柄が50日線より下で、50日線が10取引日前より下（2026-11-03 の「局面に沿う④」）
            s_, k = at(t_)
            return k is not None and k >= 60 and s_["ma50"][k] is not None and s_["ma50"][k - 10] is not None and s_["c"][k] < s_["ma50"][k] < s_["ma50"][k - 10]
        rev_dn = lambda t_: t_["rule"] in ("B", "C") and dn50(t_)
        base_out = [(1, t) for t in TOut]
        FORMS = [
            FORMS[0],
            ("⑩ 87銘柄は150日線（30週線）が上向きの銘柄だけ買う", [(0, t) for t in TA if up150(t)] + base_out),
            ("⑪ 87銘柄は150日線が上向きでRS≧80の銘柄だけ買う", [(0, t) for t in TA if strong(t)] + base_out),
            ("⑫ 87銘柄の押し目・急落の底は、銘柄が下向きの50日線の下なら買わない（11/03の④）", [(0, t) for t in TA if not rev_dn(t)] + base_out),
            ("⑬ ⑩＋⑫", [(0, t) for t in TA if up150(t) and not rev_dn(t)] + base_out),
            ("⑭ ①＋損で終わった売買が3回続いたら10取引日止める", F_now()),
            ("⑮ ①＋損で終わった売買が3回続いたら20取引日止める", F_now()),
            ("⑯ ①＋15%の損切りが3回続いたら止め、SOXが20日線を上回ったら再開（⑤'）", F_now()),
            ("⑰ ⑩＋⑤'", [(0, t) for t in TA if up150(t)] + base_out),
            ("⑱ ⑫＋⑤'", [(0, t) for t in TA if not rev_dn(t)] + base_out),
            ("⑲ 87銘柄は150日線が上向きでRS≧70の銘柄だけ買う", [(0, t) for t in TA if strong(t, 70)] + base_out),
            ("⑳ 87銘柄は150日線が上向きでRS≧90の銘柄だけ買う", [(0, t) for t in TA if strong(t, 90)] + base_out),
            ("㉑ 87銘柄はRS≧80の銘柄だけ買う（150日線の条件なし）", [(0, t) for t in TA if at(t)[1] is not None and (at(t)[0]["rs"][at(t)[1]] or 0) >= 80] + base_out),
            ("㉒ ⑪＋損で終わった売買が3回続いたら10取引日止める", [(0, t) for t in TA if strong(t)] + base_out),
        ]
        WCAP, WSZ = {}, {}
        if os.environ.get("LBT_FIX") == "1":   # 2026-11-22 ユーザーの指示「検証して」: 強さの条件が2015〜2021年に効かない対策
            for t_ in TA:
                t_["weak"] = not strong(t_, 90)
            def fallen(t_, a_=90, b_=70):
                s_, k = at(t_)
                if k is None or k < 70:
                    return False
                rs_ = s_["rs"]
                return (rs_[k] or 0) < b_ and max((x or 0) for x in rs_[k - 63:k]) >= a_
            FORMS = [FORMS[0], ("⑳ 87銘柄は150日線が上向きでRS≧90の銘柄だけ買う（いつも）", [(0, t) for t in TA if strong(t, 90)] + base_out),
                     ("対策1a 弱い87銘柄（⑳を満たさない）は同時に1銘柄まで", F_now()),
                     ("対策1b 弱い87銘柄は同時に2銘柄まで", F_now()),
                     ("対策2 弱い87銘柄は半分の金額で買う", F_now()),
                     ("対策3a 崩れたリーダー（直前3か月にRS≧90、合図の日にRS<70）の87銘柄は買わない", [(0, t) for t in TA if not fallen(t, 90, 70)] + base_out),
                     ("対策3b 崩れたリーダー（直前3か月にRS≧90、合図の日にRS<80）は買わない", [(0, t) for t in TA if not fallen(t, 90, 80)] + base_out),
                     ("対策1a＋対策3a", [(0, t) for t in TA if not fallen(t, 90, 70)] + base_out)]
            WCAP = {FORMS[2][0]: 1, FORMS[3][0]: 2, FORMS[7][0]: 1}
            WSZ = {FORMS[4][0]: 0.5}
        if os.environ.get("LBT_MIX") == "1":   # 2026-11-22 ユーザーの指示「手数料とプラン以外全て検証して」: Fable の「87銘柄の口と全業種の口を半分ずつ」を長い下げで（参考）
            # 全業種の口＝その日にS&P500の構成銘柄で、RS≧90・終値＞150日線＞20取引日前の150日線・業種の3か月の強さ上位20%の銘柄（87銘柄も条件を満たせば入る。後知恵なし）
            eligA = {}
            for s in stocks:
                s_ = data[s]
                c_, m150 = s_["c"], s_["ma150"]
                for i in range(170, len(c_)):
                    r_ = s_["rs"][i]
                    if r_ is None or r_ < 90 or m150[i] is None or m150[i - 20] is None or not (c_[i] > m150[i] > m150[i - 20]):
                        continue
                    if not liq(s_, i) or not in_sp(s_, i):
                        continue
                    rk = IR.get(s_["date"][i], {}).get(ind.get(s))
                    if rk is None or rk > 0.2:
                        continue
                    eligA.setdefault(s_["date"][i], {})[s] = r_
            okAllE = lambda s_, i, sp: s_["sym"] in eligA.get(s_["date"][i], ())
            ok10AllE = top10(lambda s_, k: okAllE(s_, k, None))
            TAllE = gen_set(okAllE, ok10AllE, "AllE")
            for t_ in TA:
                t_["weak"] = not strong(t_, 90)
            FORMS = [FORMS[0], ("⑳ 87銘柄は150日線が上向きでRS≧90の銘柄だけ買う（いつも）", [(0, t) for t in TA if strong(t, 90)] + base_out),
                     ("対策2 弱い87銘柄は半分の金額で買う", F_now()),
                     ("全業種の口（その日のS&P500の強い銘柄を毎日選び直す。後知恵なし）", [(0, t) for t in TAllE]),
                     ("混ぜる: ①の口50%＋全業種の口50%（毎年1月に戻す）", []),
                     ("混ぜる: ①の口75%＋全業種の口25%（毎年1月に戻す）", []),
                     ("混ぜる: ⑳の口50%＋全業種の口50%（毎年1月に戻す）", [])]
            WSZ = {FORMS[2][0]: 0.5}
            MIXES = {FORMS[4][0]: (FORMS[0][0], FORMS[3][0], 0.5), FORMS[5][0]: (FORMS[0][0], FORMS[3][0], 0.75),
                     FORMS[6][0]: (FORMS[1][0], FORMS[3][0], 0.5)}
        if os.environ.get("LBT_REGIME") == "1":   # 2026-11-22 ユーザーの指示「検証して」: 強さの条件を下落相場の日だけ当てる形
            gs_m = gspc_series()
            gd_ = sorted(gs_m)
            gc_ = [gs_m[d] for d in gd_]
            g200 = {gd_[k] for k in range(199, len(gc_)) if gc_[k] < sum(gc_[k - 199:k + 1]) / 200}
            s200, s200dn, s2_ = set(), set(), set()
            for k in range(199, len(sx_c)):
                if sx_c[k] < sum(sx_c[k - 199:k + 1]) / 200:
                    s200.add(sx_d[k])
                    if k >= 60 and sum(sx_c[k - 49:k + 1]) < sum(sx_c[k - 59:k - 9]):
                        s200dn.add(sx_d[k])
                if k >= 59 and sx_c[k] / max(sx_c[k - 59:k + 1]) - 1 <= -0.10:
                    s2_.add(sx_d[k])
            REG = {"both200": s200 & g200, "sox200": s200, "s2": s2_, "sp15": {d for d, v in SP.items() if v}, "sox200dn": s200dn}
            RLAB = {"both200": "SOXとS&P500が両方200日線の下", "sox200": "SOXが200日線の下", "s2": "SOXが60日の最高値から−10%以下（S2）",
                    "sp15": "特殊な下げの印", "sox200dn": "SOXが200日線の下で50日線が下向き"}
            for k_, v_ in REG.items():
                print(f"{RLAB[k_]}の日: 1996年〜の{sum(1 for d in days if d in v_) / len(days):.0%}", file=sys.stderr)
            FORMS = [FORMS[0], ("⑳ 87銘柄は150日線が上向きでRS≧90の銘柄だけ買う（いつも）", [(0, t) for t in TA if strong(t, 90)] + base_out),
                     ("⑪ 同じでRS≧80（いつも）", [(0, t) for t in TA if strong(t, 80)] + base_out)]
            for k_ in REG:
                FORMS.append((f"{RLAB[k_]}の日だけ⑳", [(0, t) for t in TA if t["sd"] not in REG[k_] or strong(t, 90)] + base_out))
            for k_ in ("both200", "s2"):
                FORMS.append((f"{RLAB[k_]}の日だけ⑪（RS≧80）", [(0, t) for t in TA if t["sd"] not in REG[k_] or strong(t, 80)] + base_out))
        CBK = {} if os.environ.get("LBT_REGIME") == "1" or os.environ.get("LBT_FIX") == "1" or os.environ.get("LBT_MIX") == "1" else {FORMS[5][0]: (3, 3, 10, "loss"), FORMS[6][0]: (3, 3, 20, "loss"), FORMS[7][0]: (3, 3, "sox20", "stop"),
               FORMS[8][0]: (3, 3, "sox20", "stop"), FORMS[9][0]: (3, 3, "sox20", "stop"), FORMS[13][0]: (3, 3, 10, "loss")}
        if os.environ.get("LBT_REGIME") == "1":
            CBK = {}
    sx20 = {sx_d[k]: sum(sx_c[k - 19:k + 1]) / 20 for k in range(19, len(sx_c))}

    IDX = {}
    for nm_, cands_ in FORMS:   # 形ごとに、買う日ごとの候補（優先・RSの高い順）を先に作る
        bi_ = {}
        for p_, t in cands_:
            bi_.setdefault(t["in"], []).append((p_, t))
        for v_ in bi_.values():
            v_.sort(key=lambda x: (x[0], -x[1]["rs"]))
        IDX[nm_] = bi_

    def port(nm_, seed, lo, hi, skip=0.25, log_eq=False):
        by_in = IDX[nm_]
        rnd = random.Random(seed)
        cash, held, pk, mdd = 1.0, [], 1.0, 0.0
        eqs = {}
        cb = CBK.get(nm_)
        res, until, paused, trig = [], -1, False, -1
        for kd, d in enumerate(days[di[lo]:di[hi] + 1]):
            still = []
            for h in held:
                v = h["t"]["path"].get(d)
                if v is not None:
                    h["v"] = v
                if h["t"]["out"] == d:
                    cash += h["size"] * h["v"]
                    if cb:
                        res.append(h["t"]["stopped"] if cb[3] == "stop" else h["t"]["ret"] < 0)
                        if len(res) >= cb[0] and sum(res[-cb[0]:]) >= cb[1]:
                            if cb[2] == "sox20":
                                paused, until, trig = True, kd + 120, kd
                            else:
                                until = max(until, kd + cb[2])
                            res = []   # 止めたら数え直す
                else:
                    still.append(h)
            held = still
            eq = cash + sum(h["size"] * h["v"] for h in held)
            if cb and cb[2] == "sox20" and paused:
                pd_ = prevd.get(d)
                if kd > until or (kd > trig and pd_ in sx20 and sox_m.get(pd_, 0) > sx20[pd_]):
                    paused = False
            blocked = cb is not None and ((cb[2] == "sox20" and paused) or (cb[2] != "sox20" and kd <= until))
            for p_, t in (() if blocked else by_in.get(d, ())):
                if skip and rnd.random() < skip:
                    continue
                if len(held) >= 4 or any(h["t"]["sym"] == t["sym"] for h in held):
                    continue
                if t["ind"] and sum(1 for h in held if h["t"]["ind"] == t["ind"]) >= 2:
                    continue
                if nm_ in WCAP and t.get("weak") and sum(1 for h in held if h["t"].get("weak")) >= WCAP[nm_]:
                    continue
                size = min(eq / 4 * (WSZ.get(nm_, 1.0) if t.get("weak") else 1.0), cash)
                if size <= eq * 0.02:
                    continue
                cash -= size
                v = t["path"].get(d, 1.0)
                h = {"t": t, "size": size, "v": v}
                if t["out"] == d:
                    cash += size * v
                else:
                    held.append(h)
            eq = cash + sum(h["size"] * h["v"] for h in held)
            pk = max(pk, eq)
            mdd = min(mdd, eq / pk - 1)
            if log_eq:
                eqs[d] = eq
        return eq, mdd, eqs

    med = lambda xs: st.median(xs) if xs else float("nan")
    pc = lambda x: f"{x * 100:+.1f}%"
    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: 長い下げの中で今のルールを確かめる（1996年〜）\ncreated: " + dt.date.today().isoformat()
      + "\nscript: tools/long_stocks.py、tools/long_bear_test.py\n---\n")
    w("# 長い下げの中で今のルールを確かめる（1996年〜）\n")
    w("2026-11-20、ユーザーの質問「アンソロピックの上場も失敗し、AI半導体株が下がり続けています。それでもなおAI半導体株を買った方が利益が出るのですか？」"
      "への回答で、2015年〜のデータには2000〜2002年・2008年のような長い半導体の下げがないことを示し、1996年〜で確かめると提案 →「はい。全て検証して」。\n")
    w(f"- 株価: Yahoo の日足（1990年〜、{days[-1]}まで）。今のS&P500の構成銘柄と87銘柄の **{len(stocks)}銘柄**（87銘柄のうち1999年より前からあるのは"
      f" {sum(1 for s in A if data[s]['date'][0] < '1999-01-01')}銘柄）。**上場をやめた会社は入っていない（生き残りの偏り）**。"
      "2000〜2002年に消えた会社（ネット・通信・半導体の多く）が入らないので、特に87銘柄（今の勝ち組）の昔の成績は良く出すぎる。")
    w("- 87銘柄（A）は今の毎朝のツールと同じ固定の一覧（後知恵あり）。ほかの業種（O）は、その日にS&P500の構成銘柄だった期間だけ使う（members.csv、1996年〜）。")
    w("- ルール: 押し目（ボリンジャー メソッドIII）・急落の底・ミネルヴィニ・新高値V2（RS上位10）。手じまいは各ルールの主な手じまいと日中の逆指値15%。"
      "**順張りの半分売り・かぶせ線・大陰線の売り・2倍ETFは入れていない**（今のツールより簡単な形）。4枠・1銘柄＝資金÷4・同じ業種2銘柄まで・片道0.1%。")
    w(f"- 乱数: 同じ日の候補の25%を乱数で見送る×{a.seeds}通りの中央値。「特殊な下げ」は毎朝のツールと同じ判定（SOXが60取引日の高値から−15%以下、"
      "前の1年の上げ+80%以上・雇用の伸び10万人未満・物価の再加速のうち2つ以上。SOXが上向きの50日線を上回るまで続く）。\n")

    # 1. SOX の大きな下げと特殊な下げの期間
    bears = sox_bears(sx_d, sx_c)
    bears = [b for b in bears if b[0] >= START]
    w("## 1. 1996年〜のSOXの大きな下げ（終値で高値から−40%以上）と特殊な下げの期間\n")
    w("| 高値の日 | 底の日 | 下げ | 高値を戻した日 |")
    w("|---|---|---|---|")
    for b in bears:
        w(f"| {b[0]} | {b[1]} | {pc(b[2])} | {b[3] or 'まだ'} |")
    spans, cur = [], None
    for d in sx_d:
        if d < START:
            continue
        if SP.get(d) and cur is None:
            cur = d
        elif not SP.get(d) and cur is not None:
            spans.append((cur, d))
            cur = None
    if cur:
        spans.append((cur, None))
    w("\n特殊な下げが「あり」だった期間（その日の引けの判定）: " + "、".join(f"{x}〜{y or '今も'}" for x, y in spans) + "\n")

    # 2. 合図の1回の成績
    periods = [("1996〜1999年", "1996-01-01", "1999-12-31")]
    for b in bears:
        periods.append((f"SOXの下げ {b[0][:7]}〜{b[1][:7]}（{pc(b[2])}）", b[0], b[1]))
    periods += [("2015〜2021年", "2015-01-01", "2021-12-31"), ("2022年〜", "2022-01-01", "9999"),
                ("1996〜2014年 全部", "1996-01-01", "2014-12-31"), ("2015年〜 全部", "2015-01-01", "9999")]
    w("## 2. 合図1回の成績（期間ごと。買った日で分ける。手数料込み）\n")
    w("押し目・急落の底＝逆張り、ミネルヴィニ・新高値V2＝順張り。勝率・損切り（15%）の割合。\n")
    w("| 期間 | 87銘柄 逆張り | 87銘柄 順張り | ほかの業種 逆張り | ほかの業種 順張り | テーマの外 全部 | ETF（SPY・QQQ・SMH・SOXX・XLK）逆張り |")
    w("|---|---|---|---|---|---|---|")

    def cell(trs):
        if not trs:
            return "—"
        r = [t["ret"] for t in trs]
        return f"{len(r)}件 {sum(r) / len(r) * 100:+.1f}%・勝率{sum(x > 0 for x in r) / len(r) * 100:.0f}%・損切り{sum(t['stopped'] for t in trs) / len(trs) * 100:.0f}%"
    REV, TRD = ("B", "C"), ("M", "V")
    for lab, lo, hi in periods:
        f_ = lambda trs, rules: [t for t in trs if lo <= t["in"] <= hi and t["rule"] in rules]
        w(f"| {lab} | {cell(f_(TA, REV))} | {cell(f_(TA, TRD))} | {cell(f_(TO, REV))} | {cell(f_(TO, TRD))} | {cell(f_(TOut, REV + TRD))} | {cell(f_(TE, REV))} |")
    w("\n### 特殊な下げの日の合図と、それ以外の日の合図\n")
    w("| 期間 | 合図の日 | 87銘柄 逆張り | 87銘柄 順張り | ほかの業種 逆張り | ほかの業種 順張り | テーマの外 全部 |")
    w("|---|---|---|---|---|---|---|")
    for lab, lo, hi in (("1996〜2014年", "1996-01-01", "2014-12-31"), ("2015年〜", "2015-01-01", "9999")):
        for lab2, cond in (("特殊な下げ", True), ("それ以外", False)):
            f_ = lambda trs, rules: [t for t in trs if lo <= t["in"] <= hi and t["rule"] in rules and sp_on(t["sd"]) == cond]
            w(f"| {lab} | {lab2} | {cell(f_(TA, REV))} | {cell(f_(TA, TRD))} | {cell(f_(TO, REV))} | {cell(f_(TO, TRD))} | {cell(f_(TOut, REV + TRD))} |")
    print("合図の表", file=sys.stderr)

    # 3. 続けて運用した資金（1996年〜）: 年ごと・期間ごと
    seeds = range(a.seeds)
    curves = {}
    for nm, cands in FORMS:
        if nm in MIXES:
            continue
        curves[nm] = [port(nm, 9000 + q, days[0], days[-1], log_eq=True)[2] for q in seeds]
        print("資金", nm, file=sys.stderr)
    for nm, (ka, kb, wt) in MIXES.items():   # 口ごとの資金を、乱数の番号が同じものどうしで混ぜ、毎年1月の最初の取引日に割合へ戻す
        curves[nm] = []
        for ca, cb_ in zip(curves[ka], curves[kb]):
            va, vb, prev, out = wt, 1 - wt, None, {}
            for d in days:
                if d not in ca or d not in cb_:
                    continue
                if prev is not None:
                    va *= ca[d] / ca[prev]
                    vb *= cb_[d] / cb_[prev]
                    if d[:4] != prev[:4]:
                        tot = va + vb
                        va, vb = wt * tot, (1 - wt) * tot
                out[d] = va + vb
                prev = d
            curves[nm].append(out)
    sox_at = lambda d: sox_m.get(d) or sox_m[sx_d[bisect.bisect_right(sx_d, d) - 1]]
    spy_at = lambda d: spy["c"][pos["SPY"][d]]

    def span_ret(nm, lo, hi):
        lo_ = days[max(0, bisect.bisect_left(days, lo) - 1)]
        hi_ = days[min(len(days) - 1, bisect.bisect_right(days, hi) - 1)]
        return med([c[hi_] / c[lo_] - 1 for c in curves[nm]])

    def span_dd(nm, lo, hi):
        out = []
        for c in curves[nm]:
            pk_, m_ = None, 0.0
            for d in days:
                if d < lo or d > hi:
                    continue
                pk_ = c[d] if pk_ is None else max(pk_, c[d])
                m_ = min(m_, c[d] / pk_ - 1)
            out.append(m_)
        return med(out)

    def cagr(nm, lo, hi):
        lo_ = days[max(0, bisect.bisect_left(days, lo) - 1)]
        hi_ = days[min(len(days) - 1, bisect.bisect_right(days, hi) - 1)]
        yrs = (dt.date.fromisoformat(hi_) - dt.date.fromisoformat(lo_)).days / 365.25
        return med([(c[hi_] / c[lo_]) ** (1 / yrs) - 1 for c in curves[nm]])

    def bench(fn, lo, hi):
        lo_ = days[max(0, bisect.bisect_left(days, lo) - 1)]
        hi_ = days[min(len(days) - 1, bisect.bisect_right(days, hi) - 1)]
        return fn(hi_) / fn(lo_) - 1

    def bench_cagr(fn, lo, hi):
        lo_ = days[max(0, bisect.bisect_left(days, lo) - 1)]
        hi_ = days[min(len(days) - 1, bisect.bisect_right(days, hi) - 1)]
        yrs = (dt.date.fromisoformat(hi_) - dt.date.fromisoformat(lo_)).days / 365.25
        return (fn(hi_) / fn(lo_)) ** (1 / yrs) - 1

    def bench_dd(fn, lo, hi):
        pk_, m_ = None, 0.0
        for d in days:
            if lo <= d <= hi:
                v = fn(d)
                pk_ = v if pk_ is None else max(pk_, v)
                m_ = min(m_, v / pk_ - 1)
        return m_

    w("\n## 3. 1996年から続けて運用した資金（乱数の中央値）\n")
    w("### 年率と、含み損込みの最大下落率\n")
    w("| 形 | 1996〜2014年 年率（最大下落率） | 2015年〜 年率（最大下落率） | 1996年〜 全部 |")
    w("|---|---|---|---|")
    for nm, _ in FORMS:
        w(f"| {nm} | {pc(cagr(nm, '1996-01-01', '2014-12-31'))}（{pc(span_dd(nm, '1996-01-01', '2014-12-31'))}） | "
          f"{pc(cagr(nm, '2015-01-01', '9999'))}（{pc(span_dd(nm, '2015-01-01', '9999'))}） | {pc(cagr(nm, '1996-01-01', '9999'))}（{pc(span_dd(nm, '1996-01-01', '9999'))}） |")
    for lab, fn in (("SOX指数（持ち続ける。配当なし）", sox_at), ("SPY（持ち続ける。配当込み）", spy_at)):
        w(f"| {lab} | {pc(bench_cagr(fn, '1996-01-01', '2014-12-31'))}（{pc(bench_dd(fn, '1996-01-01', '2014-12-31'))}） | "
          f"{pc(bench_cagr(fn, '2015-01-01', '9999'))}（{pc(bench_dd(fn, '2015-01-01', '9999'))}） | {pc(bench_cagr(fn, '1996-01-01', '9999'))}（{pc(bench_dd(fn, '1996-01-01', '9999'))}） |")

    w("\n### SOXの大きな下げの間（SOXの高値の日→底の日）と、その後（底の日→1年後）の増減\n")
    hdr = []
    for b in bears:
        b1 = (dt.date.fromisoformat(b[1]) + dt.timedelta(days=365)).isoformat()
        hdr.append((f"{b[0][:7]}〜{b[1][:7]} 下げの間", b[0], b[1]))
        hdr.append((f"底→1年後", b[1], b1))
    if spans and spans[-1][1] is None:
        hdr.append((f"今回の特殊な下げ（{spans[-1][0]}〜）", spans[-1][0], days[-1]))
    w("| 形 | " + " | ".join(h[0] for h in hdr) + " |")
    w("|---|" + "---|" * len(hdr))
    for nm, _ in FORMS:
        w(f"| {nm} | " + " | ".join(f"{pc(span_ret(nm, lo, hi))}（{pc(span_dd(nm, lo, hi))}）" for _, lo, hi in hdr) + " |")
    for lab, fn in (("SOX指数", sox_at), ("SPY", spy_at)):
        w(f"| {lab} | " + " | ".join(f"{pc(bench(fn, lo, hi))}（{pc(bench_dd(fn, lo, hi))}）" for _, lo, hi in hdr) + " |")
    w("\n（かっこの中は、その期間の中の含み損込みの最大下落率）\n")

    years = sorted({d[:4] for d in days})
    w("### 年ごと（続けて持った資金の、前の年の終わりから1年の増減）\n")
    w("| 形 | " + " | ".join(years) + " |")
    w("|---|" + "---|" * len(years))
    yend = {y: max(d for d in days if d[:4] == y) for y in years}
    for nm, _ in FORMS:
        row = []
        prev = days[0]
        for y in years:
            row.append(med([c[yend[y]] / c[prev] - 1 for c in curves[nm]]))
            prev = yend[y]
        w(f"| {nm} | " + " | ".join(f"{x * 100:+.0f}%" for x in row) + " |")
    for lab, fn in (("SOX指数", sox_at), ("SPY", spy_at)):
        row, prev = [], days[0]
        for y in years:
            row.append(fn(yend[y]) / fn(prev) - 1)
            prev = yend[y]
        w(f"| {lab} | " + " | ".join(f"{x * 100:+.0f}%" for x in row) + " |")
    print("年ごと", file=sys.stderr)

    # 4. 1年の区切り（空の枠から）
    WIN, STEP = 250, 10
    starts = list(range(0, len(days) - WIN, STEP))
    roll = {nm: [] for nm, _ in FORMS}
    for k in starts:
        lo, hi = days[k], days[k + WIN]
        for nm, cands in FORMS:
            if nm in MIXES:
                continue
            roll[nm].append(st.mean(port(nm, 7000 + q, lo, hi)[0] - 1 for q in seeds))
    for nm, (ka, kb, wt) in MIXES.items():
        roll[nm] = [wt * x + (1 - wt) * y for x, y in zip(roll[ka], roll[kb])]
    print("1年の区切り", file=sys.stderr)
    ref = FORMS[0][0]
    w("\n## 4. 1年の区切り（250取引日、10取引日ずつずらして空の枠から。乱数の平均）\n")
    w(f"「①より良い」＝同じ区切りで①より年の増減が大きかった割合。\n")
    groups = [("1996〜2014年に始めた区切り", lambda d: d < "2015-01-01"), ("2015年〜に始めた区切り", lambda d: d >= "2015-01-01"),
              ("特殊な下げの日に始めた区切り", lambda d: sp_on(prevd.get(d, d))),
              ("SOXの大きな下げの間に始めた区切り", lambda d: any(b[0] <= d <= b[1] for b in bears))]
    w("| 形 | " + " | ".join(f"{g[0]} 平均（中央値）・①より良い" for g in groups) + " |")
    w("|---|" + "---|" * len(groups))
    for nm, _ in FORMS:
        cells = []
        for gl, gf in groups:
            ix = [j for j, k in enumerate(starts) if gf(days[k])]
            xs = [roll[nm][j] for j in ix]
            if not xs:
                cells.append("—")
                continue
            better = sum(roll[nm][j] > roll[ref][j] for j in ix) / len(ix)
            cells.append(f"{pc(st.mean(xs))}（{pc(med(xs))}）・{'—' if nm == ref else f'{better * 100:.0f}%'}（{len(xs)}区切り）")
        w(f"| {nm} | " + " | ".join(cells) + " |")
    out = {"forms": [nm for nm, _ in FORMS], "starts": [days[k] for k in starts], "roll": roll, "special_spans": spans, "bears": bears}
    os.makedirs(C + "results", exist_ok=True)
    json.dump(out, open(C + ("results/long_bear_roll_mix.json" if os.environ.get("LBT_MIX") == "1" else "results/long_bear_roll_fix.json" if os.environ.get("LBT_FIX") == "1" else "results/long_bear_roll_regime.json" if os.environ.get("LBT_REGIME") == "1" else "results/long_bear_roll_extra.json" if os.environ.get("LBT_EXTRA") == "1" else "results/long_bear_roll.json"), "w"), ensure_ascii=False)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
