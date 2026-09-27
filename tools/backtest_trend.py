#!/usr/bin/env python3
"""ミネルヴィニ・ワインスタインの数値ルールのバックテスト（`新分析ツール/引き継ぎ.md` 5-2）

使い方:
  tools/backtest_lib.py fetch            # データの取得（共通。先に1回実行する）
  tools/backtest_trend.py run [--cache DIR] [--out FILE] [--start YYYY-MM-DD] [--end YYYY-MM-DD]

ルールの出典は `書籍ルール/ミネルヴィニ_ルール表.md` と `書籍ルール/ワインスタイン_ルール表.md`。
VCPの形・ベースの数え方・ステージの見極めなど著者の判断が要る部分は含めず、数値にできる部分だけで検証する。
ルール表に数値がない部分（ベースの長さ、RSランキングの計算式など）はClaudeが決めた値で、1つに絞らず複数の値で結果が変わるかを示す。
売買はすべて「引け後に判定して翌取引日の寄り付き」。損切り・利確は引け値で判定する（日中の逆指値ではない）。
建玉はリスク2%・損切り幅から逆算する（ユーザー決定: リスク2%、損切り15%）。
"""
import argparse
import bisect
import datetime as dt
import operator
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backtest_lib import (COSTS, DEFAULT_CACHE, Reporter, coverage, sliding, gen_trades, is_member, load_prices, load_universe,
                          market_regime, pct, sma, spy_benchmark, stats)

RISK = 0.02
COST = COSTS[2]  # 片道0.1%


# ---------- 指標 ----------

def rolling_max(x, n):
    return sliding(x, n, operator.ge, False)  # 当日を含まない直近n日


def rolling_min(x, n):
    return sliding(x, n, operator.le, False)


def prepare(d):
    c, h, l, v = d["c"], d["h"], d["l"], d["v"]
    n = len(c)
    d["ma50"], d["ma150"], d["ma200"] = sma(c, 50), sma(c, 150), sma(c, 200)
    d["vol50"] = [None] + sma(v, 50)[:-1]            # 前日までの50日平均出来高
    d["hi252"], d["lo252"] = sliding(h, 252, operator.ge, True), sliding(l, 252, operator.le, True)  # 当日を含む52週
    d["hi"] = {w: rolling_max(h, w) for w in PIVOT_WINDOWS}
    d["lo"] = {w: rolling_min(l, w) for w in PIVOT_WINDOWS}
    ret = lambda k: [c[i] / c[i - k] - 1 if i >= k else None for i in range(n)]
    r63, r126, r189, r252 = ret(63), ret(126), ret(189), ret(252)
    d["rs_raw"] = [0.4 * r63[i] + 0.2 * r126[i] + 0.2 * r189[i] + 0.2 * r252[i] if r252[i] is not None else None for i in range(n)]
    d["rs"] = [None] * n
    weekly(d)
    return d


def weekly(d):
    """日足から週足（週の最終取引日で区切る）を作り、週の最終日の添字に週足の値を載せる"""
    n = len(d["c"])
    wk = [dt.date.fromisoformat(x).isocalendar()[:2] for x in d["date"]]
    ends = [i for i in range(n) if i == n - 1 or wk[i + 1] != wk[i]]
    starts = [0] + [e + 1 for e in ends[:-1]]
    wc = [d["c"][e] for e in ends]
    wh = [max(d["h"][s:e + 1]) for s, e in zip(starts, ends)]
    wv = [sum(d["v"][s:e + 1]) for s, e in zip(starts, ends)]
    ma30, ma10 = sma(wc, 30), sma(wc, 10)
    d["wend"] = [False] * n
    for key in ("w_c", "w_ma30", "w_ma30_4", "w_ma10", "w_ma10_1", "w_vol", "w_vol4"):
        d[key] = [None] * n
    d["w_hi_prev"] = {w: [None] * n for w in W_WINDOWS}
    for k, e in enumerate(ends):
        d["wend"][e] = True
        d["w_c"][e], d["w_ma30"][e], d["w_ma10"][e], d["w_vol"][e] = wc[k], ma30[k], ma10[k], wv[k]
        d["w_ma30_4"][e] = ma30[k - 4] if k >= 4 else None
        d["w_ma10_1"][e] = ma10[k - 1] if k >= 1 else None
        d["w_vol4"][e] = sum(wv[k - 4:k]) / 4 if k >= 4 else None
        for w in W_WINDOWS:
            d["w_hi_prev"][w][e] = max(wh[k - w:k]) if k >= w else None


def add_rs_rank(data, members):
    """RSランキング（1〜99）: その日の構成銘柄の中での rs_raw の百分位。
    ルール表にRSの計算式はないため、IBD式に近い加重（直近3カ月40%、6・9・12カ月各20%）をClaudeが選んだ"""
    by_day = {}
    for sym, s in data.items():
        for i, d in enumerate(s["date"]):
            r = s["rs_raw"][i]
            if r is not None and is_member(members[sym], d):
                by_day.setdefault(d, []).append(r)
    for v in by_day.values():
        v.sort()
    for sym, s in data.items():
        for i, d in enumerate(s["date"]):
            r = s["rs_raw"][i]
            if r is not None and d in by_day and len(by_day[d]) > 50:
                s["rs"][i] = 99 * bisect.bisect_left(by_day[d], r) / (len(by_day[d]) - 1)


# ---------- ミネルヴィニ ----------

PIVOT_WINDOWS = (15, 50, 100)    # ベースの長さ（取引日）。本は「3〜65週」で1つに決まらないため3通り（約3週・10週・20週）
W_WINDOWS = (10, 26, 52)         # ワインスタインの抵抗線（直前の何週の高値を上抜けるか）。ルール表に数値なし


def liquid(s, i, spans):
    """流動性（全戦略共通の最低限）: 株価≧5ドル、50日平均出来高≧25万株、その日の構成銘柄"""
    return (s["vol50"][i] is not None and s["c"][i] >= 5 and s["vol50"][i] >= 250_000
            and is_member(spans, s["date"][i]))


def trend_template(s, i, rs_min=70):
    """ミネルヴィニのトレンドテンプレート1〜8（p.44, p.37）"""
    c, m50, m150, m200 = s["c"][i], s["ma50"][i], s["ma150"][i], s["ma200"][i]
    if None in (m50, m150, m200, s["rs"][i]) or i < 221 or s["ma200"][i - 21] is None:
        return False
    return (c > m150 and c > m200                       # 1
            and m150 > m200                             # 2
            and m200 > s["ma200"][i - 21]               # 3 200日線が1カ月以上上昇（1カ月前より上で近似）
            and m50 > m150 and m50 > m200               # 4
            and c > m50                                 # 5
            and c >= s["lo252"][i] * 1.25               # 6 52週安値より25%以上高い
            and c >= s["hi252"][i] * 0.75               # 7 52週高値から25%以内
            and s["rs"][i] >= rs_min)                   # 8 RSランキング≧70


def E_minervini(win, vol_mult=2.0, depth=0.35, rs_min=70):
    """トレンドテンプレートを満たし、直前win日のベース（高値−安値の幅が depth 以内）の高値を出来高を伴って上抜けた。
    ・ベースの調整幅 ≦ 25〜35%（p.98ほか。上限の35%を使う）
    ・ブレイク当日の出来高 ≧ 50日平均 × 2〜3倍（p.121。下限の2倍を使う）
    ・買値 ≦ ピボット × 1.02〜1.03（p.118-122。翌日の寄り付きがピボット×1.03を超えたら買わない＝上限の3%を使う）"""
    def f(i, s):
        hi, lo = s["hi"][win][i], s["lo"][win][i]
        if hi is None or i + 1 >= len(s["c"]) or not trend_template(s, i, rs_min):
            return None
        if not (s["c"][i] > hi and (hi - lo) / hi <= depth):
            return None
        if vol_mult and s["v"][i] < vol_mult * s["vol50"][i]:
            return None
        if s["o"][i + 1] > hi * 1.03:
            return None
        return -s["rs"][i]   # 同じ日はRSの高い順に買う
    return f


X_NONE = lambda j, s, k, px: False
X_BELOW50 = lambda j, s, k, px: s["c"][j] < s["ma50"][j]


# ---------- ワインスタイン ----------

def E_weinstein(wwin, vol_mult=2.0, ma="30"):
    """週足で、終値が30週線（トレーダーは10週線）より上、線が水平または上向き、直前wwin週の高値を上抜け、
    その週の出来高 ≧ 前月（直前4週）の週平均 × 2（p.67）。週の最終取引日の引け後に判定し翌取引日の寄り付きで買う"""
    def f(i, s):
        if not s["wend"][i]:
            return None
        wc, hi, v, v4 = s["w_c"][i], s["w_hi_prev"][wwin][i], s["w_vol"][i], s["w_vol4"][i]
        if ma == "30":
            m, m_prev = s["w_ma30"][i], s["w_ma30_4"][i]      # 30週線が4週前以上＝水平または上昇
        else:
            m, m_prev = s["w_ma10"][i], s["w_ma10_1"][i]      # 10週線が前週より上＝上昇基調
            if m is not None and m_prev is not None and m <= m_prev:
                return None
        if None in (wc, hi, v, v4, m, m_prev) or wc <= m or m < m_prev or wc <= hi:
            return None
        if vol_mult and v < vol_mult * v4:
            return None
        return -(s["rs"][i] or 0)
    return f


def X_weekly_below(ma):
    key = "w_ma30" if ma == "30" else "w_ma10"
    return lambda j, s, k, px: s["wend"][j] and s[key][j] is not None and s["w_c"][j] < s[key][j]


# ---------- 実行 ----------

def cmd_run(a):
    members, data = load_universe(a.cache, min_bars=260)
    for s in data.values():
        prepare(s)
    add_rs_rank(data, members)
    spy = load_prices(a.cache, "SPY")
    regime = market_regime(spy)
    not_down = lambda d: regime.get(d) != "下落"
    days = [d for d in spy["date"] if a.start <= d <= a.end]
    spy_cagr, spy_mdd = spy_benchmark(spy, days)
    n_in, n_got = coverage(members, data, a.start, a.end)
    years = len(days) / 252
    halves = [("前半", a.start, "2020-12-31"), ("後半", "2021-01-01", a.end)]

    def run(entry, exit_fn, stop, allow=None, **kw):
        return gen_trades(data, members, entry, exit_fn, a.start, a.end, ok=liquid, fill="open", allow=allow,
                          max_hold=kw.pop("max_hold", 500), stop_pct=stop, **kw)

    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: ミネルヴィニ・ワインスタイン 数値ルールのバックテスト\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_trend.py\n---\n")
    w("# ミネルヴィニ・ワインスタイン 数値ルールのバックテスト\n")
    w(f"- 期間: {days[0]} 〜 {days[-1]}（{len(days)}取引日）。前半＝〜2020年、後半＝2021年〜。")
    w(f"- 対象: その日にS&P500の構成銘柄だった銘柄。期間中の構成銘柄 {n_in} のうち価格を取得できたのは {n_got}（{pct(n_got / n_in)}）。上場廃止銘柄の欠落で成績は良く出る方向にずれうる。")
    w("- 価格: 配当・分割調整済み（Yahooの調整後終値）。")
    w("- 売買: 引け後に判定し、翌取引日の寄り付きで仕掛け・手じまう。損切り・利確は引け値で判定（日中の逆指値ではないため、実際の逆指値より損失が大きくなる日がある）。片道0.1%のコスト込み。")
    w("- 建玉: 1トレードのリスクを資金の2%とし、損切り幅から逆算（損切り15%→1銘柄に資金の13.3%、同時保有7銘柄まで。7%→28.6%・3銘柄、10%→20%・5銘柄）。")
    w("- 同じ日の候補が空き枠より多いときの選び方はルール表にないため、「RSの高い順」と「ランダムな順（10通り）の中央値と幅」の両方を出す。"
      "RSの高い順はランダムな順より悪くなることが多かった（伸び切った銘柄を選びやすいため）。")
    w("- VCPの形・ベースの数え方・ステージの見極めなど、著者の判断が要る部分は含めていない（新ツールでは著者ペルソナが判定する部分）。")
    w("- RSランキング: ルール表に計算式がないため、直近3カ月40%・6/9/12カ月各20%の加重リターンを、その日の構成銘柄の中で百分位（1〜99）にした（Claudeの選択）。")
    w(f"- 比較: 同期間のSPY買い持ち 年率 {pct(spy_cagr)}、最大下落率 {pct(spy_mdd)}（配当込み）\n")

    rep = Reporter(w, data, days, halves, years, cost=COST, risk=RISK)
    header, line = rep.header, rep.line

    # ---- ミネルヴィニ ----
    w("## 1. ミネルヴィニ: トレンドテンプレート＋出来高を伴うベース上抜け\n")
    w("エントリーは `書籍ルール/ミネルヴィニ_ルール表.md` のトレンドテンプレート1〜8（p.44）、ベースの調整幅≦35%（p.98ほか）、"
      "ブレイク当日の出来高≧50日平均×2（p.121）、買値≦ピボット×1.03（p.118-122）。ベースの長さは50日（約10週）。\n")
    w("### 1-1. 手じまい方法の比較\n")
    header()
    E50 = E_minervini(50)
    exits = [
        ("損切り15%・利確20%（p.167 通常相場の目標）", dict(stop=0.15, target=0.20)),
        ("損切り15%・50日線割れで手じまい（ルール表外: トレンドテンプレート5の崩れ）", dict(stop=0.15, exit_fn=X_BELOW50)),
        ("損切り15%・含み益45%（許容リスク×3、p.149）で損切りを建値へ・50日線割れで手じまい", dict(stop=0.15, exit_fn=X_BELOW50, breakeven_at=0.45)),
        ("（本の数値）損切り7%・利確20%（p.150, p.167）", dict(stop=0.07, target=0.20)),
        ("（本の数値）損切り10%・含み益30%で建値へ・50日線割れで手じまい（p.150, p.149）", dict(stop=0.10, exit_fn=X_BELOW50, breakeven_at=0.30)),
    ]
    m_results = {}
    for label, kw in exits:
        kw = dict(kw)
        stop = kw.pop("stop")
        tr = run(E50, kw.pop("exit_fn", X_NONE), stop, **kw)
        m_results[label] = tr
        line(label, tr, stop)

    base_exit = exits[1]
    w("\n### 1-2. 条件を変えた場合（手じまいは「損切り15%・50日線割れ」）\n")
    w("本に数値の幅がある部分・数値がない部分で結果が大きく変わらないかを見る。\n")
    header()
    variants = [
        ("ベース15日（約3週）", E_minervini(15), None),
        ("ベース50日（約10週）＝1-1と同じ", E50, None),
        ("ベース100日（約20週）", E_minervini(100), None),
        ("ベース50日・出来高条件なし（参考）", E_minervini(50, vol_mult=0), None),
        ("ベース50日・調整幅≦25%（本の幅の下限）", E_minervini(50, depth=0.25), None),
        ("ベース50日・RS≧80（本の「望ましくは80〜90台」）", E_minervini(50, rs_min=80), None),
        ("ベース50日・下落局面は買わない（市場全体の条件）", E50, not_down),
    ]
    for label, ent, allow in variants:
        tr = m_results[base_exit[0]] if ent is E50 and allow is None else run(ent, X_BELOW50, 0.15, allow=allow)
        line(label, tr, 0.15)

    # ---- ワインスタイン ----
    w("\n## 2. ワインスタイン: 週足の30週線より上での抵抗線ブレイク（ステージ2入り）\n")
    w("エントリーは週足で、終値>30週線、30週線が4週前以上（水平または上昇）、直前の高値（何週分かはルール表に数値がないため3通り）を上抜け、"
      "その週の出来高≧直前4週の週平均×2（p.67）。手じまいは週足の終値が30週線を割ったとき（ステージ3・4入り）または損切り。"
      "`書籍ルール/ワインスタイン_ルール表.md`。\n")
    header()
    X30, X10 = X_weekly_below("30"), X_weekly_below("10")
    w_results = {}
    wv = [
        ("抵抗線26週・損切り15%・30週線割れで手じまい（投資家）", E_weinstein(26), X30, 0.15, None),
        ("抵抗線10週・損切り15%・30週線割れで手じまい", E_weinstein(10), X30, 0.15, None),
        ("抵抗線52週・損切り15%・30週線割れで手じまい", E_weinstein(52), X30, 0.15, None),
        ("抵抗線26週・出来高条件なし（参考）", E_weinstein(26, vol_mult=0), X30, 0.15, None),
        ("抵抗線26週・下落局面は買わない", E_weinstein(26), X30, 0.15, not_down),
        ("（本の数値）抵抗線26週・損切り10%（p.121 買値の8〜12%下）・30週線割れ", E_weinstein(26), X30, 0.10, None),
        ("（トレーダー）抵抗線10週・10週線が上向き・損切り15%・10週線割れで手じまい（p.12-13）", E_weinstein(10, ma="10"), X10, 0.15, None),
    ]
    for label, ent, ex, stop, allow in wv:
        tr = run(ent, ex, stop, allow=allow)
        w_results[label] = tr
        line(label, tr, stop)

    # ---- 局面別 ----
    w("\n## 3. 市場全体の局面別（1トレード＝1件、片道0.1%）\n")
    w("仕掛けた日の局面（SPYの30週線で近似したワインスタインのステージ）で分ける。\n")
    w("| 戦略 | 局面 | 件数 | 勝率 | 1トレード平均（95%区間）/ PF |")
    w("|---|---|---|---|---|")
    for label, tr in ((base_exit[0], m_results[base_exit[0]]), (wv[0][0], w_results[wv[0][0]])):
        for r in ("上昇", "横ばい", "下落"):
            g = [t for t in tr if regime.get(t["in"]) == r]
            st = stats(g, COST)
            if st:
                w(f"| {label} | {r} | {st['n']} | {pct(st['win'])} | {pct(st['mean'], 2)}（{pct(st['mean_ci'][0], 2)}〜{pct(st['mean_ci'][1], 2)}）/ {st['pf']:.2f} |")

    w(f"\n（参考）SPY買い持ち: 年率 {pct(spy_cagr)}、最大下落率 {pct(spy_mdd)}\n")
    w("## 4. 注意\n")
    w("- 過去の成績は将来を保証しない。上場廃止銘柄の欠落、寄り付きの気配値のすべりを入れていないことは、いずれも現実より良く見せる方向に働きうる。")
    w("- 損切りを引け値で判定しているため、実際に逆指値を置く場合より損失が大きいトレードがある一方、日中だけ割り込んで戻る日に振り落とされない分は有利になっている。")
    w("- 同じ条件を何通りも試すと、偶然良かった条件を選んでしまう（過剰適合）。前半・後半の両方で成り立つかを重視すること。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/ミネルヴィニ・ワインスタイン.md")
    r.add_argument("--start", default="2015-01-02")
    r.add_argument("--end", default=dt.date.today().isoformat())
    cmd_run(ap.parse_args())


if __name__ == "__main__":
    main()
