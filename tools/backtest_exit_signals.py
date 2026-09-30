#!/usr/bin/env python3
"""代表的なチャートの形・ローソク足（酒田五法など）・テクニカル指標が出たら売る場合のバックテスト（まとめて比較）

使い方:
  tools/backtest_exit_signals.py run [--out FILE]

今の採用ルール（4つのルール、4銘柄・1銘柄25%、損切り15%、急落の底RSI(2)≦10、同じ業種2銘柄まで）で持っている銘柄に、
次の形・指標が出たら（引けで判定）翌日の寄り付きで売る。今のルールの売りの条件はそのまま残す。
形の数値はどれも本に数値がないため、Claudeが一般的な定義から置いたもの。「上昇の後」は終値が25日線より上かつ直前20日の最高値の3%以内。
当てる対象: 全部のルール／順張り（ミネルヴィニ・新高値V2）だけ／逆張り（ボリンジャーIII・急落の底）だけ。
設計期間 2015〜2021年 / 確認期間 2022年〜。
"""
import argparse
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_combo2 as cb
from backtest_lib import COSTS, DEFAULT_CACHE, pct, portfolio, sma
from backtest_market_signal import ema
from backtest_regime import srt

COST = COSTS[2]
SLOTS = 4
SEEDS = range(10)
IS_END, OOS_START = cb.IS_END, cb.OOS_START


def wilder(x, n):
    out, a = [None] * len(x), None
    for i, v in enumerate(x):
        if v is None:
            continue
        a = v if a is None else (a * (n - 1) + v) / n
        out[i] = a if i >= n else None
    return out


def prep(s):
    o, h, l, c, v, n = s["o"], s["h"], s["l"], s["c"], s["v"], len(s["c"])
    s["ma25"] = sma(c, 25)
    s["ma5"] = s.get("ma5") or sma(c, 5)
    # RSI(14)
    up = [0.0] + [max(0.0, c[i] - c[i - 1]) for i in range(1, n)]
    dn = [0.0] + [max(0.0, c[i - 1] - c[i]) for i in range(1, n)]
    au, ad = wilder(up, 14), wilder(dn, 14)
    s["rsi14"] = [None if au[i] is None else (100.0 if ad[i] == 0 else 100 - 100 / (1 + au[i] / ad[i])) for i in range(n)]
    # ストキャスティクス(14,3)
    k = [None] * n
    for i in range(13, n):
        hh, ll = max(h[i - 13:i + 1]), min(l[i - 13:i + 1])
        k[i] = 50.0 if hh == ll else 100 * (c[i] - ll) / (hh - ll)
    d = [None] * n
    for i in range(15, n):
        d[i] = (k[i] + k[i - 1] + k[i - 2]) / 3
    s["stk"], s["std"] = k, d
    # パラボリックSAR（0.02, 0.2）: True なら SAR が価格の上（下落トレンド）
    sar_dn, up_tr, sar, ep, af = [False] * n, True, l[0], h[0], 0.02
    for i in range(1, n):
        sar = sar + af * (ep - sar)
        if up_tr:
            sar = min(sar, l[i - 1], l[i - 2] if i > 1 else l[i - 1])
            if l[i] < sar:
                up_tr, sar, ep, af = False, ep, l[i], 0.02
            elif h[i] > ep:
                ep, af = h[i], min(0.2, af + 0.02)
        else:
            sar = max(sar, h[i - 1], h[i - 2] if i > 1 else h[i - 1])
            if h[i] > sar:
                up_tr, sar, ep, af = True, ep, h[i], 0.02
            elif l[i] < ep:
                ep, af = l[i], min(0.2, af + 0.02)
        sar_dn[i] = not up_tr
    s["sar_dn"] = sar_dn
    # 一目均衡表
    def mid(p, i):
        return (max(h[i - p + 1:i + 1]) + min(l[i - p + 1:i + 1])) / 2 if i >= p - 1 else None
    ten = [mid(9, i) for i in range(n)]
    kij = [mid(26, i) for i in range(n)]
    sa = [None if ten[i] is None or kij[i] is None else (ten[i] + kij[i]) / 2 for i in range(n)]
    sb = [mid(52, i) for i in range(n)]
    s["ten"], s["kij"] = ten, kij
    s["cloud_lo"] = [None] * 26 + [None if sa[i] is None or sb[i] is None else min(sa[i], sb[i]) for i in range(n - 26)]
    # DMI（14）
    pdm = [0.0] + [max(0.0, h[i] - h[i - 1]) if h[i] - h[i - 1] > l[i - 1] - l[i] else 0.0 for i in range(1, n)]
    mdm = [0.0] + [max(0.0, l[i - 1] - l[i]) if l[i - 1] - l[i] > h[i] - h[i - 1] else 0.0 for i in range(1, n)]
    tr = [h[0] - l[0]] + [max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1])) for i in range(1, n)]
    ap, am, at = wilder(pdm, 14), wilder(mdm, 14), wilder(tr, 14)
    s["pdi"] = [None if at[i] in (None, 0) else 100 * ap[i] / at[i] for i in range(n)]
    s["mdi"] = [None if at[i] in (None, 0) else 100 * am[i] / at[i] for i in range(n)]
    s["atr14"] = at
    # MACD
    m = [a - b for a, b in zip(ema(c, 12), ema(c, 26))]
    s["macd"], s["macd_sig"] = m, ema(m, 9)
    # スイングの高値（前後2日より高い）
    s["swing"] = [2 <= i < n - 2 and h[i] >= max(h[i - 2:i + 3]) for i in range(n)]


def after_up(s, j):
    m = s["ma25"][j]
    return m is not None and s["c"][j] > m and s["c"][j] >= max(s["c"][max(0, j - 20):j + 1]) * 0.97


def body(s, j):
    return abs(s["c"][j] - s["o"][j])


def cross_below(a, b, j):
    return a[j] is not None and b[j] is not None and a[j - 1] is not None and b[j - 1] is not None and a[j] < b[j] and a[j - 1] >= b[j - 1]


# ---- 形・指標（s, j = 判定する日） ----
def double_top(s, j):
    h, l, c = s["h"], s["l"], s["c"]
    if j < 60:
        return False
    peaks = [k for k in range(j - 60, j - 2) if s["swing"][k]]
    if len(peaks) < 2:
        return False
    a = max(peaks, key=lambda k: h[k])
    others = [k for k in peaks if abs(k - a) >= 10 and h[k] >= h[a] * 0.97]
    if not others:
        return False
    b = max(others, key=lambda k: h[k])
    lo, hi = min(a, b), max(a, b)
    neck = min(l[lo:hi + 1])
    return c[j] < neck <= c[j - 1] and max(h[hi + 1:j + 1] or [0]) <= h[a] * 1.01


def head_shoulders(s, j):
    h, l, c = s["h"], s["l"], s["c"]
    if j < 80:
        return False
    peaks = [k for k in range(j - 80, j - 2) if s["swing"][k]]
    if len(peaks) < 3:
        return False
    p1, p2, p3 = peaks[-3:]
    if not (h[p2] > h[p1] * 1.03 and h[p2] > h[p3] * 1.03 and abs(h[p1] - h[p3]) <= 0.05 * h[p2]):
        return False
    neck = min(min(l[p1:p2 + 1]), min(l[p2:p3 + 1]))
    return c[j] < neck <= c[j - 1]


def gap_two_black(s, j):   # 下放れ二本黒
    o, h, l, c = s["o"], s["h"], s["l"], s["c"]
    return j >= 3 and o[j - 1] < l[j - 2] and c[j - 1] < o[j - 1] and c[j] < o[j] and h[j] < l[j - 2]


def hanging_man(s, j):     # 首吊り線（翌日の下げで確定）
    o, h, l, c = s["o"], s["h"], s["l"], s["c"]
    k = j - 1
    b = body(s, k)
    lower, upper = min(o[k], c[k]) - l[k], h[k] - max(o[k], c[k])
    return after_up(s, k) and b > 0 and lower >= 2 * b and upper <= 0.3 * b + 1e-9 and c[j] < min(o[k], c[k])


def shooting_star(s, j):   # 流れ星（翌日の下げで確定）
    o, h, l, c = s["o"], s["h"], s["l"], s["c"]
    k = j - 1
    b = body(s, k)
    lower, upper = min(o[k], c[k]) - l[k], h[k] - max(o[k], c[k])
    return after_up(s, k) and b > 0 and upper >= 2 * b and lower <= 0.3 * b + 1e-9 and c[j] < min(o[k], c[k])


def three_crows(s, j):     # 三羽烏
    o, c = s["o"], s["c"]
    return (j >= 25 and after_up(s, j - 3) and all(c[k] < o[k] for k in (j - 2, j - 1, j))
            and c[j - 2] > c[j - 1] > c[j] and c[j - 1] < o[j - 1] <= o[j - 2] and o[j] <= o[j - 1])


def evening_star(s, j):    # 宵の明星（三川）
    o, c = s["o"], s["c"]
    a = s["atr14"][j - 2]
    return (a is not None and after_up(s, j - 1) and c[j - 2] - o[j - 2] >= a and body(s, j - 1) <= 0.3 * a
            and min(o[j - 1], c[j - 1]) > c[j - 2] and c[j] < o[j] and c[j] < (o[j - 2] + c[j - 2]) / 2)


def bear_engulf(s, j):     # 弱気の包み足（抱き線）
    o, c = s["o"], s["c"]
    return after_up(s, j - 1) and c[j - 1] > o[j - 1] and c[j] < o[j] and o[j] >= c[j - 1] and c[j] <= o[j - 1]


def dark_cloud(s, j):      # かぶせ線
    o, h, c = s["o"], s["h"], s["c"]
    return (after_up(s, j - 1) and c[j - 1] > o[j - 1] and o[j] > h[j - 1] and c[j] < (o[j - 1] + c[j - 1]) / 2 and c[j] > o[j - 1])


def island_top(s, j):      # アイランド・リバーサル（天井）
    h, l = s["h"], s["l"]
    for k in range(max(2, j - 10), j):
        if l[k] > h[k - 1] and h[j] < min(l[k:j]):
            return True
    return False


def three_gaps(s, j):      # 三空（三空踏み上げ）
    h, l = s["h"], s["l"]
    return j >= 12 and sum(1 for k in range(j - 9, j + 1) if l[k] > h[k - 1]) >= 3 and l[j] > h[j - 1]


def rsi_down70(s, j):
    r = s["rsi14"]
    return r[j] is not None and r[j - 1] is not None and r[j] < 70 <= r[j - 1]


def rsi_div(s, j):         # RSIの弱気ダイバージェンス（価格は20日の高値、RSIは20日の高値より5以上低い）
    r, c = s["rsi14"], s["c"]
    if j < 25 or r[j] is None or None in r[j - 20:j]:
        return False
    return c[j] >= max(c[j - 20:j]) and r[j] < max(r[j - 20:j]) - 5


def stoch_down(s, j):
    k, d = s["stk"], s["std"]
    return cross_below(k, d, j) and d[j - 1] >= 80


def sar_flip(s, j):
    return s["sar_dn"][j] and not s["sar_dn"][j - 1]


def dead_5_25(s, j):
    return cross_below(s["ma5"], s["ma25"], j)


def ichimoku_cloud(s, j):  # 雲の下に抜ける
    cl, c = s["cloud_lo"], s["c"]
    return cl[j] is not None and cl[j - 1] is not None and c[j] < cl[j] and c[j - 1] >= cl[j - 1]


def ichimoku_tk(s, j):     # 転換線が基準線を下に抜ける
    return cross_below(s["ten"], s["kij"], j)


def dmi_cross(s, j):       # −DI が +DI を上に抜ける
    return cross_below(s["pdi"], s["mdi"], j)


def below20(s, j):         # 20日線（ボリンジャーの真ん中）割れ
    m = s["bb_mid"]
    return m[j] is not None and m[j - 1] is not None and s["c"][j] < m[j] and s["c"][j - 1] >= m[j - 1]


def overheat(s, j):        # 25日線からの乖離率が+20%以上（過熱で利益確定）
    m = s["ma25"][j]
    return m is not None and s["c"][j] >= m * 1.2


def climax(s, j):          # 出来高の急増を伴う天井（出来高3倍・引けが値幅の下半分・20日で+30%以上）
    v50, h, l, c = s["vol50"][j - 1], s["h"], s["l"], s["c"]
    return (v50 and s["v"][j] >= 3 * v50 and h[j] > l[j] and (c[j] - l[j]) / (h[j] - l[j]) <= 0.5 and j >= 20 and c[j] >= c[j - 20] * 1.3)


def macd_div(s, j):        # MACDの弱気ダイバージェンス
    m, c = s["macd"], s["c"]
    return j >= 40 and c[j] >= max(c[j - 20:j]) and m[j] < max(m[j - 20:j]) * 0.8 and m[j] > 0


def donchian20(s, j):      # 直前20日の安値割れ
    return j >= 21 and s["c"][j] < min(s["l"][j - 20:j])


SIGNALS = [
    ("チャートの形", "ダブルトップ（ネックライン割れ）", double_top),
    ("チャートの形", "ヘッド・アンド・ショルダーズ＝三尊天井（ネックライン割れ）", head_shoulders),
    ("チャートの形", "アイランド・リバーサル（天井）", island_top),
    ("ローソク足（酒田五法など）", "下放れ二本黒", gap_two_black),
    ("ローソク足（酒田五法など）", "首吊り線（翌日の下げで確定）", hanging_man),
    ("ローソク足（酒田五法など）", "流れ星（翌日の下げで確定）", shooting_star),
    ("ローソク足（酒田五法など）", "三羽烏（三兵）", three_crows),
    ("ローソク足（酒田五法など）", "宵の明星（三川）", evening_star),
    ("ローソク足（酒田五法など）", "弱気の包み足（抱き線）", bear_engulf),
    ("ローソク足（酒田五法など）", "かぶせ線", dark_cloud),
    ("ローソク足（酒田五法など）", "三空（三空踏み上げ）", three_gaps),
    ("テクニカル指標", "RSI(14)が70を下に抜ける", rsi_down70),
    ("テクニカル指標", "RSIの弱気ダイバージェンス", rsi_div),
    ("テクニカル指標", "MACDの弱気ダイバージェンス", macd_div),
    ("テクニカル指標", "ストキャスティクスが80以上でデッドクロス", stoch_down),
    ("テクニカル指標", "パラボリックSARの反転", sar_flip),
    ("テクニカル指標", "5日線と25日線のデッドクロス", dead_5_25),
    ("テクニカル指標", "一目均衡表の雲の下に抜ける", ichimoku_cloud),
    ("テクニカル指標", "一目均衡表の転換線が基準線を下に抜ける", ichimoku_tk),
    ("テクニカル指標", "DMIの−DIが+DIを上に抜ける", dmi_cross),
    ("テクニカル指標", "20日線（ボリンジャーの真ん中）割れ", below20),
    ("テクニカル指標", "25日線からの乖離率+20%（過熱で利益確定）", overheat),
    ("テクニカル指標", "出来高の急増を伴う天井（出来高3倍・上ひげ）", climax),
    ("テクニカル指標", "直前20日の安値割れ（ドンチャン）", donchian20),
]


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/チャートの形と指標で売る.md")
    a = ap.parse_args()
    ctx = cb.setup(a.cache)
    data, ind, days, parts = (ctx[k] for k in ("data", "ind", "days", "parts"))
    rule_of, base = {}, []
    for key, lst in (("B", parts[("B", 0.15)]), ("M", parts[("M", 0.15)]), ("C", parts[("C", 0.15, 10)]), ("V", parts[("V", 0.15)])):
        for t in lst:
            rule_of[id(t)] = key
        base += lst
    base = srt(base)
    for sym in {t["sym"] for t in base}:
        prep(data[sym])
    print("準備ができた", file=sys.stderr)
    pos = {}

    def idx(sym, d):
        if sym not in pos:
            pos[sym] = {x: k for k, x in enumerate(data[sym]["date"])}
        return pos[sym][d]

    def apply(f, rules):
        out, diffs = [], []
        for t in base:
            if rule_of[id(t)] not in rules:
                out.append(t)
                continue
            s, sym = data[t["sym"]], t["sym"]
            i0, i1 = idx(sym, t["in"]), idx(sym, t["out"])
            new = t
            for j in range(max(i0, 2), i1 - 1):
                try:
                    hit = f(s, j)
                except (TypeError, ValueError):
                    hit = False
                if hit:
                    new = {**t, "out": s["date"][j + 1], "ret": s["o"][j + 1] / t["px"] - 1}
                    diffs.append(new["ret"] - t["ret"])
                    break
            out.append(new)
        return srt(out), diffs

    di = {d: k for k, d in enumerate(days)}
    is_hi = max(d for d in days if d <= IS_END)
    oos_lo = min(d for d in days if d >= OOS_START)
    span = lambda lo, hi: (dt.date.fromisoformat(hi) - dt.date.fromisoformat(lo)).days / 365.25

    def seg(c, lo, hi):
        return c[di[hi]] / (c[di[lo] - 1] if di[lo] > 0 else 1.0)

    def evaluate(tr):
        rs = []
        for k in SEEDS:
            p = portfolio(tr, COST, SLOTS, days, data, weight=1 / SLOTS, seed=k, group_of=ind, group_cap=2)
            c = p["curve"]
            rs.append({"all": p["cagr"], "mdd": p["mdd"], "is": seg(c, days[0], is_hi) ** (1 / span(days[0], is_hi)) - 1,
                       "oos": seg(c, oos_lo, days[-1]) ** (1 / span(oos_lo, days[-1])) - 1})
        m = lambda key: cb.med([x[key] for x in rs])
        return {"all": m("all"), "mdd": m("mdd"), "is": m("is"), "oos": m("oos")}

    cur = evaluate(base)
    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: チャートの形と指標で売る\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_exit_signals.py\n---\n")
    w("# 代表的なチャートの形・ローソク足・テクニカル指標が出たら売る場合のバックテスト\n")
    w(__doc__.split("\n", 5)[5].strip() + "\n")
    w("年率・最大下落率は同じ日の候補の選び方をランダムにした10通りの中央値。片道0.1%。後知恵なしの監視銘柄（S&P500）。"
      "「早めに売った件数」は全部の合図のうち、その形で今のルールより早く売ることになった件数。「差」はその売買1回ごとの損益の差の平均"
      "（プラスなら早めに売った方が良かった）。「戻った割合」は、売らずに持った方が良かった割合。\n")
    w(f"今のルール: 年率 {pct(cur['all'])}、最大下落率 {pct(cur['mdd'])}、設計期間 {pct(cur['is'])}、確認期間 {pct(cur['oos'])}\n")
    groups = (("全部", ("B", "C", "M", "V")), ("順張りだけ", ("M", "V")), ("逆張りだけ", ("B", "C")))
    wins = []
    cur_grp = None
    for g, lab, f in SIGNALS:
        if g != cur_grp:
            w(f"\n## {g}\n")
            w("| 形・指標 | 対象 | 年率 | 最大下落率 | 設計期間 | 確認期間 | 早めに売った件数 | 差（1回平均） | 戻った割合 | 両方の期間で上回ったか |")
            w("|---|---|---|---|---|---|---|---|---|---|")
            cur_grp = g
        for gl, rules in groups:
            tr, diffs = apply(f, rules)
            e = evaluate(tr)
            ok = e["is"] > cur["is"] and e["oos"] > cur["oos"]
            if ok:
                wins.append((lab, gl, e))
            avg = sum(diffs) / len(diffs) if diffs else 0
            back = sum(1 for x in diffs if x < 0) / len(diffs) if diffs else 0
            w(f"| {lab} | {gl} | {pct(e['all'])} | {pct(e['mdd'])} | {pct(e['is'])} | {pct(e['oos'])} | {len(diffs)} | {pct(avg, 2)} | {pct(back, 0)} | {'はい' if ok else ''} |")
            print(lab, gl, file=sys.stderr)
    w("\n## まとめ\n")
    w(f"- 試した形: {len(SIGNALS)}種類 × 対象3通り = {len(SIGNALS) * 3}通り。設計期間・確認期間の両方で今のルールを上回った形: **{len(wins)}通り**")
    for lab, gl, e in wins:
        w(f"  - {lab}（{gl}）: 年率 {pct(e['all'])}、設計 {pct(e['is'])}、確認 {pct(e['oos'])}、最大下落率 {pct(e['mdd'])}")
    w("\n## 注意\n")
    w("- 形の定義の数値（山の高さの差3%、10日以上離れる、下ひげが実体の2倍、乖離率20%、出来高3倍など）はClaudeが置いたもの。本やサイトによって定義は少しずつ違う。")
    w("- 多くの形を試しているので、1つだけ上回った形は偶然のことがある。同じ種類の形（ローソク足どうし、指標どうし）で同じ傾向かを見る。")
    w("- 業種は今のYahooの分類を過去にも使っている。NASDAQ100は含めていない。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
