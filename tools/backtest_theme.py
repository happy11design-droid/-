#!/usr/bin/env python3
"""テーマ監視銘柄（`新分析ツール/テーマ監視銘柄.md`）での直近3年のバックテスト（個別株のスイングのみ）

使い方:
  tools/backtest_lib.py fetch            # S&P500の構成銘柄・日足の取得（共通）
  tools/theme_universe.py fetch          # 業種と、S&P500に入っていない銘柄の日足の取得
  tools/backtest_theme.py run [--cache DIR] [--out FILE] [--start YYYY-MM-DD] [--end YYYY-MM-DD]

監視銘柄は `テーマ監視銘柄.md` の表の1列目を読む（ユーザーが編集した一覧がそのまま使われる）。
売買のルールは各スクリプトと同じ（ミネルヴィニ・ワインスタイン: backtest_trend.py、ラシュキ・ボリンジャー: backtest_swing.py、コナーズ: backtest_connors.py）。
**監視銘柄は今の時点で「伸びたテーマ」から選んでいるため、過去3年の成績は実際より良く出る（後知恵）。手法どうしの比較に使う。**
"""
import argparse
import bisect
import csv
import datetime as dt
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_connors as bc
import backtest_swing as bs
import backtest_trend as bt
from backtest_lib import COSTS, DEFAULT_CACHE, Reporter, gen_trades, load_prices, market_regime, pct, portfolio, sma, stats

RISK, STOP, COST = 0.02, 0.15, COSTS[2]
WATCHLIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "新分析ツール", "テーマ監視銘柄.md")


def load_watchlist(path=WATCHLIST):
    """{ティッカー: グループ名}。見出し「## グループ名（件数）」の下の表の1列目を読む"""
    out, group = {}, None
    for line in open(path, encoding="utf-8"):
        m = re.match(r"^## (.+?)（\d+）", line)
        if m:
            group = m.group(1)
            continue
        if line.startswith("## "):
            group = None
        m = re.match(r"^\| ([A-Z][A-Z.]*) \|", line)
        if m and group:
            out[m.group(1)] = group
    return out


def rs_ranks(cache, syms_base, data):
    """RSランキング（1〜99）は、S&P500の構成銘柄＋監視銘柄の中での百分位（backtest_trend.add_rs_rank と同じ計算）"""
    raw_by_day = {}
    for sym in syms_base:
        d = data.get(sym) or load_prices(cache, sym)
        if not d or len(d["c"]) < 260:
            continue
        c = d["c"]
        for i in range(252, len(c)):
            r = 0.4 * (c[i] / c[i - 63] - 1) + 0.2 * (c[i] / c[i - 126] - 1) + 0.2 * (c[i] / c[i - 189] - 1) + 0.2 * (c[i] / c[i - 252] - 1)
            raw_by_day.setdefault(d["date"][i], []).append(r)
    for v in raw_by_day.values():
        v.sort()
    for s in data.values():
        for i, d in enumerate(s["date"]):
            r, pool = s["rs_raw"][i], raw_by_day.get(d)
            if r is not None and pool and len(pool) > 50:
                s["rs"][i] = 99 * bisect.bisect_left(pool, r) / (len(pool) - 1)


def theme_index(data, dates):
    """監視銘柄の等金額平均の指数（毎日の騰落率の平均を積み上げる）"""
    pos = {s: {d: k for k, d in enumerate(v["date"])} for s, v in data.items()}
    lvl, c = 1.0, []
    for k, d in enumerate(dates):
        if k:
            rets = []
            for s, v in data.items():
                j = pos[s].get(d)
                if j and v["date"][j - 1] == dates[k - 1]:
                    rets.append(v["c"][j] / v["c"][j - 1] - 1)
            if rets:
                lvl *= 1 + sum(rets) / len(rets)
        c.append(lvl)
    return {"date": dates, "c": c}


def E_surge(i, s):
    c = s["c"]
    if i < 1 or s["vol50"][i] is None or s["ma50"][i] is None:
        return None
    ch = c[i] / c[i - 1] - 1
    return -ch if ch >= 0.05 and s["v"][i] >= 2 * s["vol50"][i] and c[i] > s["ma50"][i] else None


def E_plunge(th):
    def f(i, s):
        ch = s["c"][i] / s["c"][i - 1] - 1 if i >= 1 else 0
        return ch if ch <= -th else None
    return f


X_UPPER = lambda j, s, k, px: s["pctb"][j] is not None and s["pctb"][j] >= 1.0


def group_strength(data, wl, lookback=63):
    """{日付: [グループ名, ...]}（直近 lookback 日の騰落率の中央値が高い順）"""
    by = {}
    for sym, v in data.items():
        c = v["c"]
        for i in range(lookback, len(c)):
            by.setdefault(v["date"][i], {}).setdefault(wl[sym], []).append(c[i] / c[i - lookback] - 1)
    out = {}
    for d, g in by.items():
        med = {k: sorted(x)[len(x) // 2] for k, x in g.items() if len(x) >= 3}
        out[d] = sorted(med, key=lambda k: -med[k])
    return out


def warn_table(w, data, spy, theme_index, market_regime, pct, start="2016-01-01"):
    dates = [d for d in spy["date"] if d >= "2015-01-01"]
    idx = theme_index(data, dates)
    c = idx["c"]
    ma50 = sma(c, 50)
    spy_c = dict(zip(spy["date"], spy["c"]))
    ratio = [x / spy_c[d] for x, d in zip(c, dates)]
    rma = sma(ratio, 50)
    stage = market_regime(idx)
    # 監視銘柄のうち50日線より上の割合
    above = {}
    for v in data.values():
        m = sma(v["c"], 50)
        for i, d in enumerate(v["date"]):
            if m[i] is not None and d >= "2015-01-01":
                a_ = above.setdefault(d, [0, 0])
                a_[0] += v["c"][i] > m[i]
                a_[1] += 1
    br = {d: x[0] / x[1] for d, x in above.items() if x[1] >= 20}
    inds = {
        "テーマ指数が30週線で「下落」ステージ（ワインスタイン）": lambda i, d: stage.get(d) == "下落",
        "テーマ指数が50日線（10週線）より下": lambda i, d: ma50[i] is not None and c[i] < ma50[i],
        "テーマ指数のS&P500に対する相対的な強さが50日平均より下": lambda i, d: rma[i] is not None and ratio[i] < rma[i],
        "監視銘柄のうち50日線より上の割合が50%未満": lambda i, d: d in br and br[d] < 0.5,
        "上の割合が40%未満かつテーマ指数が50日線より下": lambda i, d: d in br and br[d] < 0.4 and ma50[i] is not None and c[i] < ma50[i],
    }
    s0 = next(k for k, d in enumerate(dates) if d >= start)
    # テーマ指数が高値から20%以上下げた局面
    eps, pk, k = [], s0, s0
    while k < len(c):
        if c[k] > c[pk]:
            pk = k
        if c[k] <= c[pk] * 0.8:
            r = k
            while r < len(c) and c[r] < c[pk]:   # 高値を取り戻すまでを1つの局面とする
                r += 1
            lo = min(range(pk, r), key=lambda j: c[j])
            eps.append((pk, lo))
            k = pk = min(r, len(c) - 1)
            if r >= len(c):
                break
        k += 1
    years = (len(c) - s0) / 252
    bh = (c[-1] / c[s0]) ** (1 / years) - 1
    peak = mdd = 0
    for x in c[s0:]:
        peak = max(peak, x)
        mdd = max(mdd, 1 - x / peak)
    w("| 警告の条件 | 年率（警告中は持たない） | 最大下落率 | 持っていた日の割合 | 切り替えの回数（年平均） | "
      + " | ".join(f"{dates[p]}の高値→安値{pct(c[l] / c[p] - 1, 0)}: 警告が出た時点の下落" for p, l in eps) + " |")
    w("|---|---|---|---|---|" + "---|" * len(eps))
    w(f"| （参考）テーマ指数を持ち続けた場合 | {pct(bh)} | {pct(mdd)} | 100% | 0 | " + " | ".join("-" for _ in eps) + " |")
    for name, f in inds.items():
        lvl, held, sw, peak, mdd2, prev = 1.0, 0, 0, 1.0, 0.0, None
        for k in range(s0 + 1, len(c)):
            on = not f(k - 1, dates[k - 1])      # 前日の引けの判定で今日を持つか
            if prev is not None and on != prev:
                sw += 1
                lvl *= 1 - 0.001
            if on:
                lvl *= c[k] / c[k - 1]
                held += 1
            prev = on
            peak = max(peak, lvl)
            mdd2 = max(mdd2, 1 - lvl / peak)
        cells = []
        for p, l in eps:
            hit = next((j for j in range(p, l + 1) if f(j, dates[j])), None)
            cells.append(f"{dates[hit]}（{pct(c[hit] / c[p] - 1, 0)}）" if hit is not None else "出ず")
        w(f"| {name} | {pct(lvl ** (1 / years) - 1)} | {pct(mdd2)} | {pct(held / (len(c) - s0 - 1), 0)} | {sw / years:.1f} | " + " | ".join(cells) + " |")
    w("")


def warn_dates(data, spy, theme_index):
    """警告の日の集合: 監視銘柄のうち50日線より上の割合が40%未満、かつテーマ指数が50日線より下"""
    dates = [d for d in spy["date"] if d >= "2015-01-01"]
    idx = theme_index(data, dates)
    ma50 = sma(idx["c"], 50)
    above = {}
    for v in data.values():
        m = sma(v["c"], 50)
        for i, d in enumerate(v["date"]):
            if m[i] is not None and d >= "2015-01-01":
                x = above.setdefault(d, [0, 0])
                x[0] += v["c"][i] > m[i]
                x[1] += 1
    return {d for i, d in enumerate(dates) if ma50[i] is not None and idx["c"][i] < ma50[i]
            and d in above and above[d][1] >= 20 and above[d][0] / above[d][1] < 0.4}


def cmd_run(a):
    wl = load_watchlist()
    data = {}
    for s in wl:
        d = load_prices(a.cache, s)
        if d and len(d["c"]) > 260:
            data[s] = d
    missing = sorted(set(wl) - set(data))
    members = {s: [("0000-00-00", "9999-12-31")] for s in data}
    for s in data.values():
        bt.prepare(s)
        bs.prepare(s)
        bc.prepare(s)
    sp_now = [r["ticker"] for r in csv.DictReader(open(os.path.join(a.cache, "members.csv"))) if not r["end_date"]]
    rs_ranks(a.cache, sorted(set(sp_now) | set(data)), data)

    spy = load_prices(a.cache, "SPY")
    days = [d for d in spy["date"] if a.start <= d <= a.end]
    years = len(days) / 252
    halves = [("前半", a.start, "2024-12-31"), ("後半", "2025-01-01", a.end)]
    market = market_regime(spy)
    tidx = theme_index(data, [d for d in spy["date"] if d >= "2021-01-01"])
    theme = market_regime(tidx)       # テーマ指数の30週線の位置と傾き（ワインスタインのステージの近似）
    ti = dict(zip(tidx["date"], tidx["c"]))
    t_cagr = (ti[days[-1]] / ti[days[0]]) ** (365.25 / (dt.date.fromisoformat(days[-1]) - dt.date.fromisoformat(days[0])).days) - 1
    peak = t_mdd = 0
    for d in days:
        peak = max(peak, ti[d])
        t_mdd = max(t_mdd, 1 - ti[d] / peak)
    theme_ok = lambda d: theme.get(d) != "下落"

    ok = bt.liquid
    def G(entry, exit_fn, stop=STOP, allow=None, **kw):
        return gen_trades(data, members, entry, exit_fn, a.start, a.end, ok=ok, fill="open", allow=allow,
                          max_hold=kw.pop("max_hold", 500), stop_pct=stop, **kw)

    def S(order, exit_fn=bs.X_NONE, trail=None, allow=None):
        return bs.simulate(data, members, order, exit_fn, a.start, a.end, allow=allow, trail=trail)

    def C(entry, exit_name, allow=None):
        return bc.gen_trades(data, members, entry, exit_name, (None, STOP, None), a.start, a.end, fill="open", allow=allow)

    rows = [
        ("順張り", [
            ("ミネルヴィニ: トレンドテンプレート＋ベース50日の上抜け＋出来高2倍・損切り15%・利確20%", lambda f=None: G(bt.E_minervini(50), bt.X_NONE, target=0.20, allow=f)),
            ("ミネルヴィニ: 同じ仕掛け・損切り15%・50日線割れで手じまい", lambda f=None: G(bt.E_minervini(50), bt.X_BELOW50, allow=f)),
            ("ミネルヴィニ: 同じ仕掛け・（本の数値）損切り7%・利確20%", lambda f=None: G(bt.E_minervini(50), bt.X_NONE, stop=0.07, target=0.20, allow=f)),
            ("ミネルヴィニ: ベース15日（約3週）・損切り15%・利確20%", lambda f=None: G(bt.E_minervini(15), bt.X_NONE, target=0.20, allow=f)),
            ("ワインスタイン: 週足26週の高値を出来高2倍で上抜け・30週線割れで手じまい・損切り15%", lambda f=None: G(bt.E_weinstein(26), bt.X_weekly_below("30"), allow=f)),
            ("ワインスタイン（トレーダー）: 10週の高値上抜け・10週線割れで手じまい", lambda f=None: G(bt.E_weinstein(10, ma="10"), bt.X_weekly_below("10"), allow=f)),
            ("ボリンジャー: ドンチャン4週ルール（20日高値上抜け・20日安値割れで手じまい）", lambda f=None: S(bs.O_donchian, bs.X_donchian_low, allow=f)),
            ("ボリンジャー: メソッドI スクイーズ・パラボリックSAR", lambda f=None: S(bs.O_squeeze, trail=bs.trail_sar, allow=f)),
            ("ボリンジャー: メソッドII（%b>0.8かつMFI>80の後の最初の押し）・パラボリックSAR", lambda f=None: S(bs.O_method2, trail=bs.trail_sar, allow=f)),
            ("参考（本のルールではない）: 急騰（前日比+5%以上・出来高2倍・50日線より上）の翌日寄り付きで買い・50日線割れで手じまい", lambda f=None: G(E_surge, bt.X_BELOW50, allow=f)),
            ("ラシュキ: 聖杯（ADX≧30・20EMAへの押し）・2日チャネル", lambda f=None: S(bs.O_holy_grail, trail=bs.trail_2day, allow=f)),
            ("ラシュキ: NR7（翌日高値に逆指値買い）・2日チャネル", lambda f=None: S(bs.O_nr7, trail=bs.trail_2day, allow=f)),
        ]),
        ("逆張り", [
            ("ボリンジャー: メソッドIII 反転（%b<0.05かつ21日II%>0）・上部バンドで手じまい", lambda f=None: S(bs.O_method3, bs.X_upper_band, allow=f)),
            ("ボリンジャー: メソッドIII・シグナル後の最初の反発の陽線を待って買う（著者の確認シグナルの近似）・上部バンドで手じまい", lambda f=None: S(bs.O_method3_confirm, bs.X_upper_band, allow=f)),
            ("コナーズ: RSI(2)≦5（200日線より上）・5日線上抜けで手じまい", lambda f=None: C(bc.E_rsi2(5), "5日線上抜け", allow=f)),
            ("コナーズ: 個別株2日累積RSI≦10・5日線上抜けで手じまい", lambda f=None: C(bc.E_cum2(10), "5日線上抜け", allow=f)),
            ("コナーズ: ダブル7（7日最安値で引け）・7日最高値で手じまい", lambda f=None: C(bc.E_double7, "7日最高値で引け", allow=f)),
            ("参考（本のルールではない）: 急落（前日比-5%以下）の翌日寄り付きで買い・上部バンドで手じまい", lambda f=None: G(E_plunge(0.05), X_UPPER, allow=f, max_hold=60)),
            ("参考（本のルールではない）: 急落（前日比-2.5%以下）の翌日寄り付きで買い・上部バンドで手じまい", lambda f=None: G(E_plunge(0.025), X_UPPER, allow=f, max_hold=60)),
            ("ラシュキ: タートルスープ（20日安値割れからの戻り）", lambda f=None: S(bs.O_turtle_soup, trail=bs.trail_turtle, allow=f)),
            ("ラシュキ: アンチ（%D上向き・%Kが3日下落）・2日チャネル", lambda f=None: S(bs.O_anti, trail=bs.trail_2day, allow=f)),
        ]),
    ]

    L = []
    w = L.append
    rep = Reporter(w, data, days, halves, years, cost=COST, risk=RISK)
    w("---\ntype: backtest\ntitle: テーマ監視銘柄での直近3年のバックテスト\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_theme.py\n---\n")
    w("# テーマ監視銘柄での直近3年のバックテスト\n")
    w(f"- 期間: {days[0]} 〜 {days[-1]}（{len(days)}取引日）。前半＝〜2024年、後半＝2025年〜。")
    w(f"- 対象: `新分析ツール/テーマ監視銘柄.md` の {len(wl)} 銘柄のうち、1年分以上の日足がある {len(data)} 銘柄"
      + (f"（日足が足りない: {', '.join(missing)}）" if missing else "") + "。ETFは含めない。")
    w("- **監視銘柄は、今の時点で「この3年に伸びたテーマ」から選んでいる。どの手法も実際より良く出る（後知恵）ため、手法どうし・条件どうしの比較に使うこと。**")
    w("- 売買: 翌日の寄り付き、またはパターンB（引け後に出す翌日の予約注文）を日足で再現。片道0.1%、損切り15%（本の数値の比較を除く）、リスク2%で建玉（1銘柄に資金の13.3%、7銘柄まで）。価格は配当・分割調整済み。")
    w("- RSランキングは、S&P500の構成銘柄＋監視銘柄の中での百分位。")
    w(f"- **比較の基準（テーマ銘柄を全部持ち続けた場合）**: 監視銘柄の等金額平均の指数 年率 {pct(t_cagr)}、最大下落率 {pct(t_mdd)}。"
      "手法がこれを下回るなら、その手法でタイミングを計るより、テーマ銘柄を持ち続けた方が良かったことになる。\n")

    results = {}
    k = 0
    for kind, strategies in rows:
        k += 1
        w(f"## {k}. {kind}\n")
        rep.header("ルールの強さの順")
        for name, fn in strategies:
            tr = fn()
            results[name] = tr
            rep.line(name, tr, 0.07 if "損切り7%" in name else STOP)
        w("")

    # 上位の手法に、テーマ指数のステージの条件を足す
    k += 1
    w(f"## {k}. テーマ指数が「下落」のステージでは買わない場合\n")
    w("テーマ指数（監視銘柄の等金額平均）の週足30週線の位置と傾きで、ワインスタインのステージを近似する"
      "（上昇＝線より上かつ上向き、下落＝線より下かつ下向き、それ以外＝横ばい）。テーマの崩れを避けられるかを見る。\n")
    days_by = {r: sum(1 for d in days if theme.get(d) == r) for r in ("上昇", "横ばい", "下落")}
    w(f"期間中のテーマ指数のステージ: 上昇 {days_by['上昇']}日、横ばい {days_by['横ばい']}日、下落 {days_by['下落']}日。\n")
    rep.header("ルールの強さの順")
    for name, fn in [x for _, s in rows for x in s]:
        st = stats(results[name], COST)
        if st and st["pf"] >= 1.2 and st["n"] >= 30:
            tr = fn(theme_ok)
            rep.line(name + "（テーマが下落のときは買わない）", tr, 0.07 if "損切り7%" in name else STOP)
    w("")

    k += 1
    w(f"## {k}. 局面別（1トレード＝1件、片道0.1%）\n")
    w("仕掛けた日の、テーマ指数のステージと、相場全体（SPYの30週線）のステージで分ける。\n")
    w("| 手法 | テーマ上昇 | テーマ横ばい | テーマ下落 | 相場全体 上昇 | 相場全体 横ばい | 相場全体 下落 |")
    w("|---|---|---|---|---|---|---|")
    for name, tr in results.items():
        cells = []
        for reg in (theme, market):
            for r in ("上昇", "横ばい", "下落"):
                st = stats([t for t in tr if reg.get(t["in"]) == r], COST)
                cells.append(f"{st['n']}件 / {pct(st['mean'], 2)} / PF{st['pf']:.2f}" if st else "0件")
        w(f"| {name.split('・')[0]} | " + " | ".join(cells) + " |")

    k += 1
    w(f"\n## {k}. グループ別（1トレード＝1件、片道0.1%）\n")
    w("| 手法 | " + " | ".join(dict.fromkeys(wl.values())) + " |")
    w("|---|" + "---|" * len(set(wl.values())))
    for name, tr in results.items():
        cells = []
        for g in dict.fromkeys(wl.values()):
            st = stats([t for t in tr if wl.get(t["sym"]) == g], COST)
            cells.append(f"{st['n']}件 / {pct(st['mean'], 2)} / PF{st['pf']:.2f}" if st else "0件")
        w(f"| {name.split('・')[0]} | " + " | ".join(cells) + " |")

    # テーマの崩れにどれだけ早く気づけたか（過去10年のテーマ指数）
    k += 1
    w(f"\n## {k}. テーマ指数のステージの切り替わり（過去10年、テーマの崩れにどれだけ早く気づけたか）\n")
    w("監視銘柄の等金額平均の指数に、ワインスタインのステージの近似（週足30週線の位置と傾き、日々判定）を当てた。"
      "「下落」に変わった日が、指数の高値からどれだけ下がった後だったか、その後さらにどれだけ下がったかを見る。"
      "監視銘柄は今の銘柄なので、古い期間ほど当時のテーマとずれる（例: 2016年ごろはAIが主役ではない）。\n")
    lidx = theme_index(data, [d for d in spy["date"] if d >= "2015-01-01"])
    lst = market_regime(lidx)
    lc = dict(zip(lidx["date"], lidx["c"]))
    w("| 「下落」に変わった日 | 「下落」が終わった日 | 直前の高値の日 | 高値から変わった日までの下落 | 変わった日からその後の安値までの下落 | 「下落」の期間中の騰落 |")
    w("|---|---|---|---|---|---|")
    ds = [d for d in lidx["date"] if d in lst]
    k2 = 0
    while k2 < len(ds):
        if lst[ds[k2]] == "下落" and (k2 == 0 or lst[ds[k2 - 1]] != "下落"):
            st_d = ds[k2]
            e = k2
            while e + 1 < len(ds) and lst[ds[e + 1]] == "下落":
                e += 1
            if e - k2 + 1 >= 5:   # 5日未満の一時的な切り替わりは省く
                end_d = ds[e]
                pk_d = max((d for d in ds[:k2] if d >= ds[max(0, k2 - 260)]), key=lambda d: lc[d])
                after = [lc[d] for d in ds[k2:min(len(ds), e + 60)]]
                w(f"| {st_d} | {end_d} | {pk_d} | {pct(lc[st_d] / lc[pk_d] - 1)} | {pct(min(after) / lc[st_d] - 1)} | {pct(lc[end_d] / lc[st_d] - 1)} |")
            k2 = e + 1
        else:
            k2 += 1
    w("")

    # ---- 見落としの確認: 監視銘柄の中での絞り込み・グループの上限・組み合わせ・コスト ----
    for sym, v in data.items():
        v["sym"] = sym
    grp_rank = group_strength(data, wl)
    top3 = lambda d: grp_rank.get(d, ())[:3]
    f_all = lambda s_, i, sp: True
    f_rs = lambda s_, i, sp: s_["rs"][i] is not None and s_["rs"][i] >= 80
    f_grp = lambda s_, i, sp: wl[s_["sym"]] in top3(s_["date"][i])
    f_both = lambda s_, i, sp: f_rs(s_, i, sp) and f_grp(s_, i, sp)
    lib_ok = lambda f: (lambda s_, i, sp: bt.liquid(s_, i, sp) and f(s_, i, sp))
    X7 = bc.X["7日最高値で引け"]
    cands = {
        "ボリンジャーIII（押し目）": lambda f: bs.simulate(data, members, bs.O_method3, bs.X_upper_band, a.start, a.end, ok=lib_ok(f)),
        "コナーズ ダブル7（押し目）": lambda f: gen_trades(data, members, bc.E_double7, lambda j, s_, k_, px: X7(j, s_, k_), a.start, a.end,
                                                   ok=lambda s_, i, sp: bc.signal_ok(s_, i, sp) and f(s_, i, sp), fill="open", max_hold=30, stop_pct=STOP),
        "ワインスタイン10週（上抜け）": lambda f: gen_trades(data, members, bt.E_weinstein(10, ma="10"), bt.X_weekly_below("10"), a.start, a.end,
                                                   ok=lib_ok(f), fill="open", max_hold=500, stop_pct=STOP),
        "ドンチャン4週（上抜け）": lambda f: bs.simulate(data, members, bs.O_donchian, bs.X_donchian_low, a.start, a.end, ok=lib_ok(f)),
        "ミネルヴィニ・50日線割れで手じまい（上抜け）": lambda f: gen_trades(data, members, bt.E_minervini(50), bt.X_BELOW50, a.start, a.end,
                                                   ok=lib_ok(f), fill="open", max_hold=500, stop_pct=STOP),
    }
    slots = int(round(STOP / RISK, 6))

    def pr(tr, cost=COST, cap=None, lo=None, hi=None, seed=0):
        lo, hi = lo or a.start, hi or a.end
        dd = [d for d in days if lo <= d <= hi]
        return portfolio([t for t in tr if lo <= t["in"] and t["out"] <= hi], cost, slots, dd, data, weight=RISK / STOP,
                         seed=seed, group_of=wl, group_cap=cap)

    def row(label, tr, cost=COST, cap=None):
        st = stats(tr, cost)
        if not st:
            w(f"| {label} | 0 | | | | | |")
            return
        rnd = [pr(tr, cost, cap, seed=k_) for k_ in range(10)]
        cg = sorted(p["cagr"] for p in rnd)
        md = sorted(p["mdd"] for p in rnd)[5]
        h = [sorted(pr(tr, cost, cap, lo, hi, seed=k_)["cagr"] for k_ in range(10))[5] for _, lo, hi in halves]
        w(f"| {label} | {st['n'] / years:.0f} | {st['pf']:.2f} | {pct(cg[5])}（{pct(cg[0])}〜{pct(cg[-1])}） | {pct(md)} | {pct(h[0])} / {pct(h[1])} | {pct(st['mean'], 2)} |")

    hdr = ("| 条件 | 年平均件数 | PF | 年率 ランダム順 中央値（幅） | 最大下落率 中央値 | 前半 / 後半 年率 | 1トレード平均 |",
           "|---|---|---|---|---|---|---|")
    base = {}
    k += 1
    w(f"## {k}. 監視銘柄の中で、その時点で強い銘柄・強いグループだけに絞る（旬の中の旬）\n")
    w("RS≧80＝その日のRSランキングが80以上の銘柄だけ。上位3グループ＝その日の直近3カ月の騰落率（中央値）で7グループ中の上位3グループの銘柄だけ（ヒートマップで今の主役を追う考え方を、その時点の情報だけで再現）。\n")
    for name, fn in cands.items():
        w(f"**{name}**\n")
        w(hdr[0]); w(hdr[1])
        for lab, f in (("絞り込みなし", f_all), ("RS≧80", f_rs), ("上位3グループ", f_grp), ("RS≧80かつ上位3グループ", f_both)):
            tr = fn(f)
            if lab == "絞り込みなし":
                base[name] = tr
            row(lab, tr)
        w("")
        print("filter", name, file=sys.stderr)

    k += 1
    w(f"## {k}. 同じグループの同時保有に上限を置く（集中の回避）\n")
    w("7銘柄の枠のうち、同じグループ（半導体、光・通信など）は2銘柄まで・3銘柄までにした場合。\n")
    w(hdr[0]); w(hdr[1])
    for name, tr in base.items():
        for cap in (None, 3, 2):
            row(f"{name}・" + ("上限なし" if cap is None else f"同じグループ{cap}銘柄まで"), tr, cap=cap)

    k += 1
    w(f"\n## {k}. 逆張りと順張りを組み合わせる（7銘柄の枠を共有）\n")
    w("同じ日の候補はランダムな順で選ぶ（手法の優先順位はルール表にないため）。\n")
    w(hdr[0]); w(hdr[1])
    B3, D7, W10, DC, M50 = (base[n] for n in cands)
    for lab, tr in (("ボリンジャーIII＋ワインスタイン10週", B3 + W10), ("ボリンジャーIII＋ドンチャン4週", B3 + DC),
                    ("ボリンジャーIII＋ミネルヴィニ", B3 + M50), ("ボリンジャーIII＋ダブル7＋ワインスタイン10週", B3 + D7 + W10),
                    ("ボリンジャーIII＋ミネルヴィニ・同じグループ2銘柄まで", B3 + M50),
                    ("ボリンジャーIII（RS≧80）＋ミネルヴィニ", cands["ボリンジャーIII（押し目）"](f_rs) + M50),
                    ("ボリンジャーIII（RS≧80）＋ワインスタイン10週", cands["ボリンジャーIII（押し目）"](f_rs) + W10)):
        tr = sorted(tr, key=lambda t: (t["out"], t["sym"]))
        row(lab, tr, cap=2 if "2銘柄まで" in lab else None)

    k += 1
    w(f"\n## {k}. 売買コストを片道0.3%にした場合（値動きの大きい銘柄の寄り付きのすべりを厳しめに見る）\n")
    w(hdr[0]); w(hdr[1])
    for name, tr in base.items():
        row(name, tr, cost=0.003)

    # ---- 早めの警告の指標（過去10年） ----
    k += 1
    w(f"\n## {k}. テーマの崩れの早めの警告（過去10年、テーマ指数で検証）\n")
    w("警告が出ている間はテーマ指数を持たず、消えたら持つ（翌日に切り替え、片道0.1%）とした場合の成績と、"
      "テーマ指数が高値から20%以上下げた局面で、警告が高値から何%下げた時点で出たか。警告が少ないほど・遅いほど下落を避けられず、"
      "多いほど・早いほど上昇を取り逃がす（誤報）。\n")
    warn_table(w, data, spy, theme_index, market_regime, pct)

    k += 1
    wd = warn_dates(data, spy, theme_index)
    no_warn = lambda d: d not in wd
    w(f"## {k}. 警告中は新しい買いだけを止める（保有は各手法の手じまいに任せる）\n")
    w("警告＝監視銘柄のうち50日線より上の割合が40%未満、かつテーマ指数が50日線より下。"
      f"直近3年のうち警告が出ていた日: {sum(1 for d in days if d in wd)}日／{len(days)}日。\n")
    w(hdr[0]); w(hdr[1])
    M50w = gen_trades(data, members, bt.E_minervini(50), bt.X_BELOW50, a.start, a.end, ok=bt.liquid, fill="open", max_hold=500,
                      stop_pct=STOP, allow=no_warn)
    B3w = bs.simulate(data, members, bs.O_method3, bs.X_upper_band, a.start, a.end, allow=no_warn)
    W10w = gen_trades(data, members, bt.E_weinstein(10, ma="10"), bt.X_weekly_below("10"), a.start, a.end, ok=bt.liquid,
                      fill="open", max_hold=500, stop_pct=STOP, allow=no_warn)
    for lab, tr in (("ボリンジャーIII", B3w), ("ミネルヴィニ・50日線割れで手じまい", M50w), ("ワインスタイン10週", W10w),
                    ("ボリンジャーIII＋ミネルヴィニ", sorted(B3w + M50w, key=lambda t: (t["out"], t["sym"]))),
                    ("ボリンジャーIII＋ワインスタイン10週", sorted(B3w + W10w, key=lambda t: (t["out"], t["sym"])))):
        row(lab + "（警告中は買わない）", tr)

    k += 1
    w(f"\n## {k}. 注意\n")
    w("- 監視銘柄を今の時点で選んでいる（後知恵）ため、どの手法も実際より良く出る。3年は短く、件数が少ない手法は信頼区間が広い。")
    w("- 寄り付きの気配値のすべりを入れていない。日足だけで逆指値の約定を再現しているため、同じ日の値動きの順番は分からない（不利な側に倒している）。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/テーマ監視銘柄・直近3年.md")
    today = dt.date.today()
    r.add_argument("--start", default=today.replace(year=today.year - 3).isoformat())
    r.add_argument("--end", default=today.isoformat())
    cmd_run(ap.parse_args())


if __name__ == "__main__":
    main()
