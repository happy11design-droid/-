#!/usr/bin/env python3
"""王道のシグナル（一目均衡表・酒田五法・ボリンジャーバンド・移動平均線・MACD・RSI・ストキャスティクス・SAR・DMI・出来高など）から、
「売りの合図」と「買い直しの合図」の一番良い組み合わせを探すバックテスト

使い方:
  tools/backtest_signal_search.py run [--out FILE]

今の採用ルール（4つのルール、4銘柄・1銘柄25%、損切り15%、急落の底RSI(2)≦10、同じ業種2銘柄まで）で買った銘柄について、
ルールが本来売る日までの間、売りの合図で売り、買い直しの合図で買い直すことを繰り返す（引けで判定し翌日の寄り付きで売買、片道0.1%）。
その銘柄の枠は、ルールが本来売る日まで確保する（売っている間は現金）。

探し方（当てはめすぎを避けるため、選ぶのは設計期間 2015〜2021年 の成績だけ。確認期間 2022年〜 は最後に1回だけ見る）:
  対象は順張り（ミネルヴィニ・新高値V2）と逆張り（ボリンジャーIII・急落の底）で別々に探す。
  1. 売りの合図: 1つだけの形（約30種類）を、買い直し「売値より上で引けたら」と組み合わせて比べ、上位8つを選ぶ。
     上位8つの2つずつの組み合わせ（3日以内に両方が出る）と、出来高1.5倍・RSI70以上との組み合わせも比べる。
  2. 買い直しの合図: 売りの上位5つそれぞれについて、1つだけの形（約20種類）を比べて上位6つを選び、その2つずつの組み合わせも比べる。
  3. 売り×買い直しの上位の組み合わせを、4銘柄の枠の資金の推移（年率）で設計期間と確認期間に分けて確かめる。
  比べる物差し（1〜2）: 設計期間の売買1回ごとの損益の平均（1つの枠、買ってからルールが売るまで）。
"""
import argparse
import datetime as dt
import itertools
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_combo2 as cb
import backtest_exit_signals as xs
from backtest_lib import COSTS, DEFAULT_CACHE, pct, sma
from backtest_regime import srt
from backtest_rebuy import big_bear, macd_dc, prep2, two_black

COST = COSTS[2]
SLOTS = 4
SEEDS = range(10)


# ---- 買いの合図（強気） ----
def bull_engulf(s, j):
    o, c = s["o"], s["c"]
    return c[j - 1] < o[j - 1] and c[j] > o[j] and o[j] <= c[j - 1] and c[j] >= o[j - 1]


def hammer(s, j):          # たくり線（翌日の上げで確定）
    o, h, l, c = s["o"], s["h"], s["l"], s["c"]
    k = j - 1
    b = abs(c[k] - o[k])
    return b > 0 and min(o[k], c[k]) - l[k] >= 2 * b and h[k] - max(o[k], c[k]) <= 0.3 * b and c[j] > c[k]


def morning_star(s, j):    # 明けの明星
    o, c = s["o"], s["c"]
    a = s["atr14"][j - 2]
    return (a is not None and o[j - 2] - c[j - 2] >= a and abs(c[j - 1] - o[j - 1]) <= 0.3 * a
            and max(o[j - 1], c[j - 1]) < c[j - 2] and c[j] > o[j] and c[j] > (o[j - 2] + c[j - 2]) / 2)


def piercing(s, j):        # 切り込み線
    o, l, c = s["o"], s["l"], s["c"]
    return c[j - 1] < o[j - 1] and o[j] < l[j - 1] and c[j] > (o[j - 1] + c[j - 1]) / 2 and c[j] < o[j - 1]


def three_white(s, j):     # 赤三兵
    o, c = s["o"], s["c"]
    return all(c[k] > o[k] for k in (j - 2, j - 1, j)) and c[j - 2] < c[j - 1] < c[j] and o[j - 2] < o[j - 1] < o[j]


def three_gaps_down(s, j):  # 三空叩き込み
    h, l = s["h"], s["l"]
    return j >= 12 and sum(1 for k in range(j - 9, j + 1) if h[k] < l[k - 1]) >= 3


def cross_up(a, b, j):
    return xs.cross_below(b, a, j)


def ma10_up(s, j):
    return cross_up(s["c"], s["ma10x"], j)


def ma20_up(s, j):
    return cross_up(s["c"], s["bb_mid"], j)


def gc_5_25(s, j):
    return cross_up(s["ma5"], s["ma25"], j)


def macd_gc(s, j):
    return cross_up(s["macd"], s["macd_sig"], j)


def sar_up(s, j):
    return s["sar_dn"][j - 1] and not s["sar_dn"][j]


def cloud_up(s, j):
    cl = s["cloud_hi"]
    return cl[j] is not None and cl[j - 1] is not None and s["c"][j] > cl[j] and s["c"][j - 1] <= cl[j - 1]


def tk_up(s, j):
    return cross_up(s["ten"], s["kij"], j)


def dmi_up(s, j):
    return cross_up(s["pdi"], s["mdi"], j)


def bb_reentry(s, j):      # 下のバンドの外から内側に戻る
    p = s["pctb"]
    return p[j] is not None and p[j - 1] is not None and p[j] >= 0 > p[j - 1]


def rsi2_bounce(s, j):
    r2 = s["rsi2x"]
    return any(x is not None and x <= 10 for x in r2[max(0, j - 3):j]) and s["c"][j] > s["h"][j - 1]


def rsi_up30(s, j):
    r = s["rsi14"]
    return r[j] is not None and r[j - 1] is not None and r[j] > 30 >= r[j - 1]


def stoch_gc(s, j):
    k, d = s["stk"], s["std"]
    return cross_up(k, d, j) and d[j - 1] is not None and d[j - 1] <= 20


def high20(s, j):
    return j >= 21 and s["c"][j] > max(s["c"][j - 20:j])


def vol15(s, j):
    v50 = s["vol50"][j - 1]
    return bool(v50) and s["v"][j] >= 1.5 * v50


def rsi70(s, j):
    r = s["rsi14"]
    return r[j] is not None and r[j] >= 70


def bb_upper(s, j):
    p = s["pctb"]
    return p[j] is not None and p[j] >= 1.0


def bb_back(s, j):         # 上のバンドの外から内側に戻る
    p = s["pctb"]
    return p[j] is not None and p[j - 1] is not None and p[j] < 1.0 <= p[j - 1]


SELLS = [("ダブルトップ", xs.double_top), ("三尊天井", xs.head_shoulders), ("アイランド（天井）", xs.island_top),
         ("下放れ二本黒", xs.gap_two_black), ("首吊り線", xs.hanging_man), ("流れ星", xs.shooting_star), ("三羽烏", xs.three_crows),
         ("宵の明星", xs.evening_star), ("弱気の包み足", xs.bear_engulf), ("かぶせ線", xs.dark_cloud), ("三空踏み上げ", xs.three_gaps),
         ("RSIの70割れ", xs.rsi_down70), ("RSIの弱気ダイバージェンス", xs.rsi_div), ("MACDの弱気ダイバージェンス", xs.macd_div),
         ("MACDのデッドクロス", macd_dc), ("ストキャス80以上のデッドクロス", xs.stoch_down), ("SARの反転（下）", xs.sar_flip),
         ("5日線と25日線のデッドクロス", xs.dead_5_25), ("一目の雲の下に抜ける", xs.ichimoku_cloud), ("一目の転換線と基準線のデッドクロス", xs.ichimoku_tk),
         ("DMIの−DIが上", xs.dmi_cross), ("20日線割れ", xs.below20), ("25日線乖離+20%", xs.overheat), ("出来高急増の天井", xs.climax),
         ("20日安値割れ", xs.donchian20), ("ボリンジャーの上のバンド以上", bb_upper), ("上のバンドの外から内側に戻る", bb_back),
         ("陰線が2日続く", two_black), ("出来高2倍の大陰線", big_bear)]
BUYS = [("強気の包み足", bull_engulf), ("たくり線", hammer), ("明けの明星", morning_star), ("切り込み線", piercing), ("赤三兵", three_white),
        ("三空叩き込み", three_gaps_down), ("10日線を上に抜ける", ma10_up), ("20日線を上に抜ける", ma20_up), ("5日線と25日線のゴールデンクロス", gc_5_25),
        ("MACDのゴールデンクロス", macd_gc), ("SARの反転（上）", sar_up), ("一目の雲の上に抜ける", cloud_up), ("一目の転換線と基準線のゴールデンクロス", tk_up),
        ("DMIの+DIが上", dmi_up), ("ボリンジャーの下のバンドの外から内側に戻る", bb_reentry), ("RSI(2)≦10の後に前日の高値を抜ける", rsi2_bounce),
        ("RSI(14)が30を上に抜ける", rsi_up30), ("ストキャス20以下のゴールデンクロス", stoch_gc), ("20日の高値を更新", high20)]
QUAL = [("出来高1.5倍", vol15), ("RSI70以上", rsi70)]


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/王道のシグナルの組み合わせ探し.md")
    a = ap.parse_args()
    ctx = cb.setup(a.cache)
    data, ind, days, parts = (ctx[k] for k in ("data", "ind", "days", "parts"))
    rule_of, base = {}, []
    for key, lst in (("B", parts[("B", 0.15)]), ("M", parts[("M", 0.15)]), ("C", parts[("C", 0.15, 10)]), ("V", parts[("V", 0.15)])):
        for t in lst:
            rule_of[id(t)] = key
        base += lst
    base = srt(base)
    pos = {}

    def idx(sym, d):
        if sym not in pos:
            pos[sym] = {x: k for k, x in enumerate(data[sym]["date"])}
        return pos[sym][d]

    # 保有期間の日だけ、全部の合図を前もって判定しておく（flags[名前][銘柄] = 合図が出た日の集合）
    need = {}
    for t in base:
        need.setdefault(t["sym"], set()).update(range(max(3, idx(t["sym"], t["in"]) - 3), idx(t["sym"], t["out"]) + 1))
    allsig = SELLS + BUYS + QUAL
    flags = {nm: {} for nm, _ in allsig}
    for sym, js in need.items():
        s = data[sym]
        xs.prep(s)
        prep2(s)
        cl = s["cloud_lo"]
        # 雲の上限（一目）
        h, l, n = s["h"], s["l"], len(s["c"])
        def mid(p, i):
            return (max(h[i - p + 1:i + 1]) + min(l[i - p + 1:i + 1])) / 2 if i >= p - 1 else None
        ten, kij = s["ten"], s["kij"]
        sa = [None if ten[i] is None or kij[i] is None else (ten[i] + kij[i]) / 2 for i in range(n)]
        sb = [mid(52, i) for i in range(n)]
        s["cloud_hi"] = [None] * 26 + [None if sa[i] is None or sb[i] is None else max(sa[i], sb[i]) for i in range(n - 26)]
        for nm, f in allsig:
            hit = set()
            for j in js:
                try:
                    if f(s, j):
                        hit.add(j)
                except (TypeError, ValueError, IndexError):
                    pass
            flags[nm][sym] = hit
    print("合図の判定ができた", file=sys.stderr)

    def single(nm):
        return lambda sym, j: j in flags[nm][sym]

    def pair(n1, n2):
        f1, f2 = flags[n1], flags[n2]
        def f(sym, j):
            a_, b_ = f1[sym], f2[sym]
            if j not in a_ and j not in b_:
                return False
            return any(j - k in a_ for k in range(3)) and any(j - k in b_ for k in range(3))
        return f

    def sim(t, sell, buy, path=False):
        s, sym = data[t["sym"]], t["sym"]
        o, c = s["o"], s["c"]
        i0, i1 = idx(sym, t["in"]), idx(sym, t["out"])
        exit_px = t["px"] * (1 + t["ret"])
        cash, sh, pend, sold_px, trips = 0.0, (1 - COST) / t["px"], None, None, 0
        pv = {}
        for j in range(i0, i1 + 1):
            if j == i1:
                if sh > 0:
                    cash += sh * exit_px * (1 - COST)
                    sh = 0.0
                if path:
                    pv[s["date"][j]] = cash
                break
            if pend == "sell" and j > i0:
                cash, sh, sold_px = sh * o[j] * (1 - COST), 0.0, o[j]
            elif pend == "buy":
                sh, cash = cash * (1 - COST) / o[j], 0.0
                trips += 1
            pend = None
            if path:
                pv[s["date"][j]] = cash + sh * c[j]
            if sell is None:
                continue
            if sh > 0:
                if sell(sym, j):
                    pend = "sell"
            elif buy == "price":
                if c[j] > sold_px:
                    pend = "buy"
            elif buy is not None and buy(sym, j):
                pend = "buy"
        return (cash - 1, trips, pv) if path else (cash - 1, trips)

    def score(trs, sell, buy):
        rs = [sim(t, sell, buy)[0] for t in trs]
        return sum(rs) / len(rs)

    groups = (("順張り（ミネルヴィニ・新高値V2）", ("M", "V")), ("逆張り（ボリンジャーIII・急落の底）", ("B", "C")))
    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: 王道のシグナルの組み合わせ探し\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_signal_search.py\n---\n")
    w("# 王道のシグナルから、売りと買い直しの一番良い組み合わせを探すバックテスト\n")
    w(__doc__.split("\n", 5)[5].strip() + "\n")
    w(f"売りの合図 {len(SELLS)}種類: " + "、".join(nm for nm, _ in SELLS) + "\n")
    w(f"買い直しの合図 {len(BUYS)}種類＋「売値より上で引けたら」: " + "、".join(nm for nm, _ in BUYS) + "\n")
    w("組み合わせに使う条件: 出来高1.5倍以上、RSI(14)70以上\n")
    best = {}
    for gl, rules in groups:
        tr_is = [t for t in base if rule_of[id(t)] in rules and t["in"] <= cb.IS_END]
        hold = score(tr_is, None, None)
        w(f"\n## {gl}\n")
        w(f"設計期間の売買 {len(tr_is)}件。持ち続けた場合の1回平均: **{pct(hold, 2)}**\n")
        # 1. 売り（単独、買い直しは売値より上で引けたら）
        res = [(nm, score(tr_is, single(nm), "price")) for nm, _ in SELLS]
        res.sort(key=lambda x: -x[1])
        w("### 1. 売りの合図（1つだけ、買い直しは「売値より上で引けたら」）の上位10\n")
        w("| 順位 | 売りの合図 | 設計期間の1回平均 |")
        w("|---|---|---|")
        for k, (nm, v) in enumerate(res[:10], 1):
            w(f"| {k} | {nm} | {pct(v, 2)} |")
        top = [nm for nm, _ in res[:8]]
        cands = [(nm, single(nm)) for nm in top]
        cands += [(f"{x}＋{y}", pair(x, y)) for x, y in itertools.combinations(top, 2)]
        cands += [(f"{x}＋{q}", pair(x, q)) for x in top for q, _ in QUAL]
        res2 = [(nm, f, score(tr_is, f, "price")) for nm, f in cands]
        res2.sort(key=lambda x: -x[2])
        w("\n### 1'. 売りの合図の組み合わせ（上位8つの2つずつ・出来高・RSI70）を含めた上位10\n")
        w("| 順位 | 売りの合図 | 設計期間の1回平均 |")
        w("|---|---|---|")
        for k, (nm, _, v) in enumerate(res2[:10], 1):
            w(f"| {k} | {nm} | {pct(v, 2)} |")
        print(gl, "売りを選んだ", file=sys.stderr)
        # 2. 買い直し
        combos = []
        for snm, sf, _ in res2[:5]:
            rb = [(bnm, single(bnm), score(tr_is, sf, single(bnm))) for bnm, _ in BUYS] + [("売値より上で引けたら", "price", score(tr_is, sf, "price"))]
            rb.sort(key=lambda x: -x[2])
            topb = [x for x in rb if x[1] != "price"][:6]
            rb2 = list(rb) + [(f"{x[0]}＋{y[0]}", pair(x[0], y[0]), None) for x, y in itertools.combinations(topb, 2)]
            rb2 += [(f"{x[0]}＋出来高1.5倍", pair(x[0], "出来高1.5倍"), None) for x in topb]
            rb2 = [(bnm, bf, v if v is not None else score(tr_is, sf, bf)) for bnm, bf, v in rb2]
            rb2.sort(key=lambda x: -x[2])
            for bnm, bf, v in rb2[:3]:
                combos.append((snm, sf, bnm, bf, v))
            print(gl, snm, "買い直しを選んだ", file=sys.stderr)
        combos.sort(key=lambda x: -x[4])
        w("\n### 2. 売り×買い直しの組み合わせの上位（設計期間の1回平均）\n")
        w("| 順位 | 売りの合図 | 買い直しの合図 | 設計期間の1回平均 | 持ち続けた場合との差 |")
        w("|---|---|---|---|---|")
        for k, (snm, _, bnm, _, v) in enumerate(combos[:10], 1):
            w(f"| {k} | {snm} | {bnm} | {pct(v, 2)} | {pct(v - hold, 2)} |")
        best[gl] = (rules, combos[:5], hold)

    # 3. 資金の推移で確かめる
    di = {d: k for k, d in enumerate(days)}
    is_hi = max(d for d in days if d <= cb.IS_END)
    oos_lo = min(d for d in days if d >= cb.OOS_START)

    def port(trs, seed, lo, hi):
        dd = [d for d in days if lo <= d <= hi]
        by_in = {}
        for t in trs:
            if lo <= t["in"] and t["out"] <= hi:
                by_in.setdefault(t["in"], []).append(t)
        rnd = random.Random(seed)
        cash, held, curve, peak, mdd = 1.0, [], [], 1.0, 0.0
        for d in dd:
            still = []
            for h in held:
                v = h["t"]["path"].get(d)
                if v is not None:
                    h["v"] = v
                if h["t"]["out"] == d:
                    cash += h["size"] * h["v"]
                else:
                    still.append(h)
            held = still
            eq = cash + sum(h["size"] * h["v"] for h in held)
            for t in sorted(by_in.get(d, []), key=lambda t: rnd.random()):
                if len(held) >= SLOTS:
                    break
                if any(h["t"]["sym"] == t["sym"] for h in held):
                    continue
                if sum(1 for h in held if ind.get(h["t"]["sym"]) == ind.get(t["sym"])) >= 2:
                    continue
                size = min(eq / SLOTS, cash)
                if size <= 0:
                    break
                cash -= size
                h = {"t": t, "size": size, "v": t["path"].get(d, 1.0)}
                if t["out"] == d:
                    cash += size * h["v"]
                    continue
                held.append(h)
            eq = cash + sum(h["size"] * h["v"] for h in held)
            curve.append(eq)
            peak = max(peak, eq)
            mdd = max(mdd, 1 - eq / peak)
        yrs = (dt.date.fromisoformat(dd[-1]) - dt.date.fromisoformat(dd[0])).days / 365.25
        return curve[-1] ** (1 / yrs) - 1, mdd

    def evaluate(choice):
        """choice: {グループのルール: (売り, 買い直し)}（なければ持ち続ける）"""
        trs, trips = [], 0
        for t in base:
            sb = next((v for k, v in choice.items() if rule_of[id(t)] in k), None)
            ret, tp, pv = sim(t, sb[0], sb[1], path=True) if sb else sim(t, None, None, path=True)
            trips += tp
            trs.append({"sym": t["sym"], "in": t["in"], "out": t["out"], "path": pv})
        a_ = [port(trs, k, days[0], days[-1]) for k in SEEDS]
        i_ = [port(trs, k, days[0], is_hi)[0] for k in SEEDS]
        o_ = [port(trs, k, oos_lo, days[-1])[0] for k in SEEDS]
        return {"all": cb.med([x[0] for x in a_]), "mdd": cb.med([x[1] for x in a_]), "is": cb.med(i_), "oos": cb.med(o_), "trips": trips}

    w("\n## 3. 資金の推移で確かめる（4銘柄の枠、設計期間で選んだ組み合わせを確認期間で確かめる）\n")
    w("| 形 | 年率 | 最大下落率 | 設計期間 | 確認期間 | 買い直した回数 | 両方の期間で上回ったか |")
    w("|---|---|---|---|---|---|---|")
    cur = evaluate({})
    w(f"| 今のルール（持ち続ける） | {pct(cur['all'])} | {pct(cur['mdd'])} | {pct(cur['is'])} | {pct(cur['oos'])} | 0 | |")
    rows = []
    for gl, (rules, top5, _) in best.items():
        for snm, sf, bnm, bf, _ in top5[:3]:
            e = evaluate({rules: (sf, bf)})
            ok = e["is"] > cur["is"] and e["oos"] > cur["oos"]
            rows.append(ok)
            w(f"| {gl}: 売り「{snm}」・買い直し「{bnm}」 | {pct(e['all'])} | {pct(e['mdd'])} | {pct(e['is'])} | {pct(e['oos'])} | {e['trips']} | {'はい' if ok else ''} |")
            print(gl, snm, bnm, file=sys.stderr)
    (r1, t1, _), (r2, t2, _) = best.values()
    e = evaluate({r1: (t1[0][1], t1[0][3]), r2: (t2[0][1], t2[0][3])})
    ok = e["is"] > cur["is"] and e["oos"] > cur["oos"]
    w(f"| 両方の1位を合わせる（順張り: {t1[0][0]}／{t1[0][2]}、逆張り: {t2[0][0]}／{t2[0][2]}） | {pct(e['all'])} | {pct(e['mdd'])} | {pct(e['is'])} | {pct(e['oos'])} | {e['trips']} | {'はい' if ok else ''} |")
    w("\n## 注意\n")
    w("- 合図の数値（形の定義、3日以内、出来高1.5倍、RSI70など）はClaudeが一般的な定義から置いたもの。")
    w("- 何百通りの中から一番良いものを選んでいるため、設計期間の成績は実際より良く出る。確認期間（選ぶときに見ていない）の成績で判断する。")
    w("- 選び方の乱数だけで年率は2〜3ポイント動く。それより小さい差は偶然の範囲。")
    w("- 買い直した後の損切りは、元の買値の15%下のまま（ルールが本来売る日を変えない）。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
