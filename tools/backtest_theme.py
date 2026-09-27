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
from backtest_lib import COSTS, DEFAULT_CACHE, Reporter, gen_trades, load_prices, market_regime, pct, stats

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
            ("ラシュキ: 聖杯（ADX≧30・20EMAへの押し）・2日チャネル", lambda f=None: S(bs.O_holy_grail, trail=bs.trail_2day, allow=f)),
            ("ラシュキ: NR7（翌日高値に逆指値買い）・2日チャネル", lambda f=None: S(bs.O_nr7, trail=bs.trail_2day, allow=f)),
        ]),
        ("逆張り", [
            ("ボリンジャー: メソッドIII 反転（%b<0.05かつ21日II%>0）・上部バンドで手じまい", lambda f=None: S(bs.O_method3, bs.X_upper_band, allow=f)),
            ("コナーズ: RSI(2)≦5（200日線より上）・5日線上抜けで手じまい", lambda f=None: C(bc.E_rsi2(5), "5日線上抜け", allow=f)),
            ("コナーズ: 個別株2日累積RSI≦10・5日線上抜けで手じまい", lambda f=None: C(bc.E_cum2(10), "5日線上抜け", allow=f)),
            ("コナーズ: ダブル7（7日最安値で引け）・7日最高値で手じまい", lambda f=None: C(bc.E_double7, "7日最高値で引け", allow=f)),
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
