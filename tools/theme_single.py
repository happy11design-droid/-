#!/usr/bin/env python3
"""指定した1銘柄を、新分析ツールで採用した3つのルールに当てはめる（`新分析ツール/テーマ監視_手順書.md` 2-4 個別分析）

使い方:
  tools/theme_single.py <ティッカー> <出力.md> [--hold <買値> <買った日> <ルール>]
    --hold: 保有中なら、買値・買った日（YYYY-MM-DD）・ルール（ボリンジャーIII／ミネルヴィニ／ワインスタイン10週）

各ルールの条件の成否と数値、条件がそろうまでの距離（ピボットの価格など）、保有中なら損切り価格と手じまい条件を書き出す。
数値と事実だけで、売買の判断はしない（判断は著者のノートブック）。監視銘柄に入っていない銘柄でもよい。
"""
import argparse
import bisect
import csv
import datetime as dt
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_swing as bs
import backtest_trend as bt
from backtest_regime import up
from backtest_minervini2 import add_pivot
import backtest_crash as bcr
import backtest_compare2 as c2
from fundamentals import text as fund_text
from backtest_lib import MEMBERS_URL, curl, rsi_wilder
from theme_scan import buy_usd, cut, earnings_date, etf2x_of, fetch_daily, pct, shares_note

STOP = 0.15


def mark(ok):
    return "満たす" if ok else "満たさない"


RAW = lambda c: 0.4 * (c[-1] / c[-64] - 1) + 0.2 * (c[-1] / c[-127] - 1) + 0.2 * (c[-1] / c[-190] - 1) + 0.2 * (c[-1] / c[-253] - 1)


def load_pool():
    """RSランキングの母集団: S&P500の今の構成銘柄の日足（直近2年）"""
    txt = curl(MEMBERS_URL)
    sp = [r["ticker"] for r in csv.DictReader(txt.splitlines()) if not r["end_date"]] if txt.startswith("ticker,") else []
    with ThreadPoolExecutor(8) as ex:
        return [x for x in ex.map(fetch_daily, sp) if x]


def who(rules):
    """rules.md から、送る著者（合図 A・B が出ているルールの著者＋保有中のルールの著者）を返す"""
    authors = ("ボリンジャー", "ミネルヴィニ", "ワインスタイン", "コナーズ")
    m = re.search(r"ボリンジャーIII: (\S+?)／ミネルヴィニ: (\S+?)／ワインスタイン10週: (\S+?)(?:／急落の底: (\S+?))?(?:／新高値: (\S+?))?（", rules)
    if m:
        pats = dict(zip(("ボリンジャー", "ミネルヴィニ", "ワインスタイン", "コナーズ", "新高値"), m.groups()))   # 急落の底はコナーズ、新高値はミネルヴィニ
        # ワインスタイン10週の合図だけでは送らない（参考の表示だけ。2026-10-04 ユーザー決定）。保有中なら下で加える
        out = [a for a in authors if a != "ワインスタイン" and (pats[a] in ("A", "B") or (a == "ミネルヴィニ" and pats["新高値"] in ("A", "B")))]
    else:
        out = list(authors)
    h = re.search(r"## \d\. 保有中の確認\n\n- ルール: ([^／]+)", rules)
    if h:
        out += [a for a in authors if (a in h.group(1) or (a == "コナーズ" and "急落" in h.group(1)) or (a == "ミネルヴィニ" and "新高値" in h.group(1))) and a not in out]
    return out


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--who":
        for x in who(open(sys.argv[2], encoding="utf-8").read()):
            print(x)
        return
    ap = argparse.ArgumentParser()
    ap.add_argument("ticker")
    ap.add_argument("out")
    ap.add_argument("--hold", nargs=3, metavar=("買値", "買った日", "ルール"))
    ap.add_argument("--asof", help="その日の引け時点で見えていたデータだけで当てはめる（過去の判定の再現用）")
    a = ap.parse_args()
    sym = a.ticker.upper()
    d = fetch_daily(sym)
    if not d or len(d["c"]) < 260:
        sys.exit(f"{sym} の日足を取得できませんでした（1年分以上が必要）")
    pool = load_pool()
    text = report(sym, d, pool, asof=a.asof, hold=a.hold, wl_rs10=None if a.asof else watchlist_rs10(pool))
    open(a.out, "w", encoding="utf-8").write(text)
    print(text)


def watchlist_rs10(pool):
    """監視銘柄のうち、今日のRSが10番目に高い銘柄のRS（新高値V2は、この値以上＝上位10以内の銘柄だけに当てる）"""
    import backtest_theme as bth
    raws = sorted(RAW(x["c"]) for x in pool if len(x["c"]) > 253)
    wl = bth.load_watchlist()
    with ThreadPoolExecutor(8) as ex:
        ws = [x for x in ex.map(fetch_daily, wl) if x and len(x["c"]) > 253]
    rs = sorted((99 * bisect.bisect_left(raws, RAW(x["c"])) / (len(raws) - 1) for x in ws), reverse=True)
    return rs[9] if len(rs) >= 10 else None


def report(sym, d, pool_series, asof=None, hold=None, earn=None, wl_rs10=None):
    """d（日足）を asof の引けまでに切って3つのルールに当てはめた文章を返す。RSは pool_series（S&P500の日足）の中での百分位"""
    if asof:
        d = cut(d, asof)
        if not d["date"] or d["date"][-1] != asof:
            raise ValueError(f"{sym}: {asof} は取引日ではないか、データがありません")
    pool = sorted(RAW(x["c"]) for x in (cut(y, asof) for y in pool_series) if len(x["c"]) > 253 and (not asof or x["date"][-1] == asof))
    d = {k: list(v) for k, v in d.items()}
    bt.prepare(d)
    bs.prepare(d)
    add_pivot(d)
    i = len(d["c"]) - 1
    if len(pool) > 50:
        d["rs"][i] = 99 * bisect.bisect_left(pool, RAW(d["c"])) / (len(pool) - 1)
    c, day = d["c"][i], d["date"][i]
    rs = d["rs"][i]
    earn = earn or ("取得不可（過去時点の再現のため）" if asof else earnings_date(sym))

    L = []
    w = L.append
    w(f"# {sym} を採用ルールに当てはめた結果（{day}の引け時点）\n")
    w(f"- 終値 {c:.2f}（前日比 {pct(c / d['c'][i - 1] - 1)}）、RSランキング {'取得不可' if rs is None else f'{rs:.0f}'}（S&P500の中での百分位）、次回決算予定日 {earn}")
    w(f"- 50日平均出来高 {d['vol50'][i] / 1e4:,.0f}万株、流動性の条件（株価5ドル以上・50日平均出来高25万株以上）: {mark(bt.liquid(d, i, [('0000', '9999')]))}")
    w(f"- 銘柄の局面（判定式: 終値 > 50日線 > 200日線、50日線が20取引日前より2%以上高い、ADX(14) ≧ 20 をすべて満たせば上昇相場、それ以外はレンジ）: "
      f"**{'上昇相場' if up(i, d) else 'レンジ'}**（50日線 {d['ma50'][i]:.2f}、200日線 {d['ma200'][i]:.2f}、50日線の20日前比 {pct(d['ma50'][i] / d['ma50'][i - 20] - 1)}、ADX(14) {d['adx14'][i]:.1f}）\n")

    # ボリンジャーIII
    pb, ii = d["pctb"][i], d["ii21"][i]
    b3 = bs.O_method3(i, d) is not None
    lvl05 = d['bb_dn'][i] + 0.05 * (d['bb_up'][i] - d['bb_dn'][i])
    pat_b = "A" if b3 else ("B" if ii > 0 and pb < 0.2 else "該当なし")
    w("## 1. 押し目: ボリンジャー メソッドIII\n")
    w(f"- 条件: %b < 0.05 かつ 21日II% > 0 → **{mark(b3)}**（%b = {pb:.3f}、21日II% = {ii:+.3f}）")
    w(f"- ボリンジャーバンド(20日, 2σ): 上 {d['bb_up'][i]:.2f}／中 {d['bb_mid'][i]:.2f}／下 {d['bb_dn'][i]:.2f}。%bが0.05になる価格の目安 {lvl05:.2f}")
    w(f"- スクリプトのパターン判定: **{pat_b}**（A=条件成立、B=%bが0.2未満かつII%>0で成立が目前）")
    if b3:
        w("- 注文の目安（A）: 翌日の寄り付きで買い、損切りは買値の15%下、手じまいは買った日の夜から売りの指値をその日の上部バンドに置き、毎晩その日の値に置き直す")
    elif pat_b == "B":
        w(f"- 予約注文の目安（B）: 指値買い {lvl05:.2f}（今日のバンドで%b=0.05になる価格。本のルールは引け値で判定するので近似）")
    w("")

    # ミネルヴィニ
    m50, m150, m200 = d["ma50"][i], d["ma150"][i], d["ma200"][i]
    hi, lo = d["hi"][50][i], d["lo"][50][i]
    conds = [
        ("1 株価 > 150日線・200日線", c > m150 and c > m200, f"{c:.2f} / {m150:.2f} / {m200:.2f}"),
        ("2 150日線 > 200日線", m150 > m200, f"{m150:.2f} / {m200:.2f}"),
        ("3 200日線が1カ月前より上", m200 > d["ma200"][i - 21], f"{m200:.2f} / {d['ma200'][i - 21]:.2f}"),
        ("4 50日線 > 150日線・200日線", m50 > m150 and m50 > m200, f"{m50:.2f}"),
        ("5 株価 > 50日線", c > m50, f"{c:.2f} / {m50:.2f}"),
        ("6 52週安値より25%以上高い", c >= d["lo252"][i] * 1.25, f"52週安値 {d['lo252'][i]:.2f}（{pct(c / d['lo252'][i] - 1)}）"),
        ("7 52週高値から25%以内", c >= d["hi252"][i] * 0.75, f"52週高値 {d['hi252'][i]:.2f}（{pct(c / d['hi252'][i] - 1)}）"),
        ("8 RSランキング70以上", rs is not None and rs >= 70, "取得不可" if rs is None else f"{rs:.0f}"),
    ]
    tt = all(x[1] for x in conds)
    kh = d["piv_i"][i]
    piv = d["h"][kh]
    blen = i - kh
    depth = (piv - min(d["l"][kh:i + 1])) / piv
    vr = d["v"][i] / d["vol50"][i]
    base_ok = blen >= 15 and depth <= 0.35
    brk = base_ok and c > piv and vr >= 2
    pat_m = "A" if tt and brk else ("B" if tt and base_ok and piv * 0.95 <= c <= piv else "該当なし")
    w("## 2. 上抜け: ミネルヴィニ（トレンドテンプレート＋ベースの上抜け）\n")
    w("| トレンドテンプレート | 成否 | 数値 |")
    w("|---|---|---|")
    for name, ok, val in conds:
        w(f"| {name} | {mark(ok)} | {val} |")
    w(f"\n- トレンドテンプレート8条件: **{mark(tt)}**")
    w(f"- ベース（ルール表 p.98・p.104: 直前65週の最高値の日から今日まで）: ピボット {piv:.2f}（{d['date'][kh]}）、長さ {blen}日（3週＝15日以上が条件）、"
      f"ピボットからの調整幅 {depth * 100:.0f}%（35%以内が条件）→ **{mark(base_ok)}**。終値からピボットまで {pct(piv / c - 1)}")
    w(f"- 本日の上抜け（終値 > ピボット、出来高が50日平均の2倍以上 = 今日 {vr:.1f}倍）: **{mark(tt and brk)}**")
    w(f"- スクリプトのパターン判定: **{pat_m}**（A=条件成立、B=テンプレートとベースを満たし、終値がピボットの−5%以内）")
    if pat_m == "A":
        w(f"- 注文の目安（A）: 翌日の寄り付きで買い（寄り付きが {piv * 1.03:.2f}＝ピボット+3% を超えたら見送り）、損切りは買値の15%下、引けで50日線割れの翌日の寄り付きで手じまい\n")
    elif pat_m == "B":
        w(f"- 予約注文の目安（B）: 逆指値買い {piv:.2f}（指値の上限 {piv * 1.03:.2f}）。本は上抜けの日の出来高が50日平均の2倍以上（{2 * d['vol50'][i] / 1e4:,.0f}万株）を求める。損切りは買値の15%下\n")
    else:
        w(f"- 次に条件がそろう目安: ピボット {piv:.2f} を出来高2倍で上抜けること（ベースが{max(0, 15 - blen)}日以上続き、調整幅35%以内のまま）\n")

    # ワインスタイン10週
    wk = dt.date.fromisoformat(day).weekday() == 4
    w10 = bt.E_weinstein(10, ma="10")(i, d) is not None if wk else False
    w("## 3. 参考: ワインスタイン10週（売買には使わない・著者には送らない。後知恵なしのバックテストで成績が下がったため。2026-10-04）\n")
    w(f"- 週足の終値 {d['w_c'][i] or c:.2f}、直前10週の高値 {d['w_hi_prev'][10][i] or float('nan'):.2f}、10週線 {d['w_ma10'][i] or float('nan'):.2f}（前週 {d['w_ma10_1'][i] or float('nan'):.2f}）、30週線 {d['w_ma30'][i] or float('nan'):.2f}")
    w(f"- 条件（週足の終値が直前10週の高値を出来高2倍で上抜け、10週線が上向き）: **{mark(w10)}**" + ("" if wk else "（判定は週の最終取引日だけ。今日の値は週の途中の参考）"))
    h10, m10, m10p = d["w_hi_prev"][10][i], d["w_ma10"][i], d["w_ma10_1"][i]
    pat_w = "A" if w10 else ("B" if h10 and m10 and m10p and m10 > m10p and h10 * 0.95 <= c <= h10 else "該当なし")
    w(f"- スクリプトのパターン判定: **{pat_w}**（A=条件成立、B=10週線が上向きで、終値が直前10週の高値の−5%以内）")
    if pat_w == "B":
        w(f"- 予約注文の目安（B）: 逆指値買い {h10:.2f}（本のルールは週足の終値で判定するので近似。上抜けの週の出来高は直前4週の平均の2倍以上）")
    w("")
    # 決算の中身（ミネルヴィニの本の銘柄選定。過去の日付での再現では、その時点で発表済みか分からないため渡さない）
    w("## 決算の中身\n")
    w("過去の日付での再現のため渡さない（その時点で発表済みだったか分からない）\n" if asof else fund_text(sym) + "\n")

    # 急落の底（逆張り、担当: コナーズ）。2026-09-27 採用
    d["rsi2"] = rsi_wilder(d["c"], 2)
    crash = bcr.C3R10(i, d) is not None
    dr, r2 = bcr.drop(i, d), d["rsi2"][i]
    pat_c = "A" if crash else "該当なし"
    w("## 4. 逆張り: 急落の底（担当: コナーズ）\n")
    w(f"- 条件: 急落の前（6日前）に50日線＞200日線、直前5日の最高値（終値）から15%以上下落、RSI(2)≦10 → **{mark(crash)}**"
      f"（6日前の50日線／200日線 {d['ma50'][i - 6]:.2f}／{d['ma200'][i - 6]:.2f}、下落率 {dr * 100:+.1f}%、RSI(2) {r2:.1f}）")
    w(f"- 直前5日の最高値（終値）{max(d['c'][i - 5:i]):.2f} の15%下は {max(d['c'][i - 5:i]) * 0.85:.2f}")
    w(f"- スクリプトのパターン判定: **{pat_c}**（A=条件成立。終値で判定するルールのため予約注文（B）はない）")
    if crash:
        w(f"- 注文の目安（A）: 翌日の寄り付きで買い、損切りは買値の15%下、終値が5日線（今日 {sum(d['c'][i - 4:i + 1]) / 5:.2f}）を上回った翌日の寄り付きで手じまい（コナーズ）。"
          "過去の検証では、市場全体（S&P500）が下落相場のときに特に強く、横ばいの相場では負けていた")
    w("")
    # 新高値（V2、担当: ミネルヴィニ）。2026-09-27 採用
    c2.add_udvr(d)
    uv, h20 = d["udvr"][i], d["hi20c"][i]
    top10 = wl_rs10 is None or (rs is not None and rs >= wl_rs10)
    import theme_scan as ts
    h2y = ts.hi2y(d, i)
    trig = max(h20 or 0, h2y or 0)
    o2y = h2y is not None and c >= h2y
    v2 = top10 and c2.V2(i, d) is not None and o2y
    pre = top10 and bool(h20 and h2y and uv and uv >= 1.3 and (rs or 0) >= 90 and tt and trig * 0.97 <= c < trig)
    pat_n = "A" if v2 else ("B" if pre else "該当なし")
    w("## 5. 順張り: 新高値（V2、担当: ミネルヴィニ）\n")
    w(f"- 条件: トレンドテンプレート8条件、RS≧90、終値が直前20日の最高値（終値）を上回る、上げ下げの出来高比（直近50日、上げた日の出来高÷下げた日の出来高）≧1.3 → **{mark(v2)}**"
      f"（テンプレート {mark(tt)}、RS {'取得不可' if rs is None else f'{rs:.0f}'}、直前20日の最高値 {h20:.2f}、出来高比 {'取得不可' if uv is None else f'{uv:.2f}'}）")
    w(f"- 追加の条件（2026-09-28 採用）: 終値が直前2年の最高値以上（上値のレジスタンスがない。ワインスタインの図） → **{mark(o2y)}**（直前2年の最高値 {'取得不可' if h2y is None else f'{h2y:.2f}'}）")
    w("- 追加の条件: 監視銘柄のうち、その日のRSが上位10銘柄に入ること（" + ("過去の日付での再現では確認していない" if wl_rs10 is None else f"10位の銘柄のRS {wl_rs10:.0f}、この銘柄のRS {'取得不可' if rs is None else f'{rs:.0f}'} → **{mark(top10)}**") + "）")
    w(f"- スクリプトのパターン判定: **{pat_n}**（A=条件成立、B=ほかの条件を満たし、終値が直前20日の最高値（終値）と直前2年の最高値の高い方の−3%以内）")
    if v2:
        w("- 注文の目安（A）: 翌日の寄り付きで買い、損切りは買値の15%下、引けで50日線割れの翌日の寄り付きで手じまい")
    elif pre:
        w(f"- 予約注文の目安（B）: 逆指値買い {trig:.2f}（直前20日の最高値（終値）と直前2年の最高値の高い方。本来は終値で判定するルールなので近似）")
    w("- このルールは、ミネルヴィニのトレンドテンプレート、ドンチャンの4週ルール（ボリンジャーの本で紹介）、オニールの「機関投資家の買い集め」の考え方を、Claudeが組み合わせて数値にしたもの（ユーザー採用 2026-09-27）")
    w("")
    w(f"## まとめ（スクリプトのパターン判定）\n\n- ボリンジャーIII: {pat_b}／ミネルヴィニ: {pat_m}／ワインスタイン10週: {pat_w}／急落の底: {pat_c}／新高値: {pat_n}（A=条件成立、B=成立が目前で予約注文の候補）\n")
    if not asof and not hold:
        # 同じ業種は同時に2銘柄まで（2026-09-28 ユーザー決定）。保有銘柄.md の同じ業種の銘柄を数える
        try:
            import theme_scan as ts
            inds = ts.load_industries()
            g = inds.get(sym)
            same = [h["sym"] for h in ts.load_holdings() if h["sym"] != sym and g and inds.get(h["sym"]) == g]
            if g:
                w(f"- 同じ業種（{g}）の保有: " + ("、".join(same) if same else "なし") + f"（上限{ts.GROUP_CAP}銘柄）"
                  + (" → **上限に達しているため、買いの合図が出ても見送り**" if len(same) >= ts.GROUP_CAP else "") + "\n")
        except Exception as e:
            w(f"- 同じ業種の保有数を確認できませんでした（{e}）\n")

    if hold:
        px, bd, rule = float(hold[0]), hold[1], hold[2]
        stop = px * (1 - STOP)
        w("## 6. 保有中の確認\n")
        w(f"- ルール: {rule}／買った日: {bd}／買値: {px:.2f}／損益: {pct(c / px - 1)}／損切り価格（買値の15%下）: {stop:.2f}" + ("（**下回っている**）" if c <= stop else ""))
        if "新高値" in rule:
            w(f"- 手じまい条件（引けで50日線割れ）: {mark(c < m50)}（50日線 {m50:.2f}）")
        elif "急落" in rule:
            ma5 = sum(d["c"][i - 4:i + 1]) / 5
            w(f"- 手じまい条件（終値が5日線を上回る。コナーズ）: {mark(c > ma5)}（5日線 {ma5:.2f}）")
        elif "ボリンジャー" in rule:
            w(f"- 手じまい: 売りの指値を上部バンド {d['bb_up'][i]:.2f} に置く（毎晩その日の値に置き直す。届いた日に売れる）。引けで上部バンド以上: {mark(pb >= 1)}")
        elif "ミネルヴィニ" in rule:
            w(f"- 手じまい条件（引けで50日線割れ）: {mark(c < m50)}（50日線 {m50:.2f}）")
        elif "ワインスタイン" in rule:
            w(f"- 手じまい条件（週足の終値が10週線割れ、週の最終取引日に判定）: {mark(wk and d['w_c'][i] < d['w_ma10'][i])}（10週線 {d['w_ma10'][i]:.2f}）")
        if "ボリンジャー" in rule or "急落" in rule:
            import theme_scan as ts_
            bb_ = ts_.big_bear_signal(d, bd)
            w("- 全部売りの合図＝出来高2倍の大陰線（2026-10-02 採用）: "
              + ("まだ出ていない" if not bb_ else f"**{bb_} に出た**（まだ持っていれば、次の寄り付きで全部売る）"))
        if "新高値" in rule or "ミネルヴィニ" in rule:
            import theme_scan as ts_
            hd = ts_.half_signal(d, bd)
            dc = ts_.dark_cloud_signal(d, bd)
            w("- 全部売りの合図＝かぶせ線（2026-10-01 採用。半分売りより優先）: "
              + ("まだ出ていない" if not dc else f"**{dc} に出た**（まだ持っていれば、次の寄り付きで全部売る）"))
            w("- 半分売りの合図（反転のローソク足＋出来高1.5倍＋RSI70。2026-10-01 採用）: "
              + ("まだ出ていない" if not hd else f"**{hd} に出た**（半分売っていなければ、次の寄り付きで半分売る。残りはルールの手じまいまで持つ）"))
        w("")
    if not asof:
        L += shares_section(sym, c, L)
    return "\n".join(L) + "\n"


SHARES_HEAD = "## 株数の目安"   # theme_single.sh send はこの見出しから後を著者に渡さない


def shares_section(sym, close, lines):
    """合図（A・B）が出ているルールごとに、buy_usd()（資金÷4）で買える株数の目安（2026-10-04 ユーザーの指示）。参考のワインスタイン10週は除く"""
    out, sec = [], ""
    ex_ = etf2x_of(sym)
    for l in lines:
        if l.startswith("## "):
            sec = l[3:].split("（")[0].strip()
        m = re.match(r"- (?:予約)?注文の目安（([AB])）: (.*)", l)
        if m and "ワインスタイン" not in sec:
            out.append(f"- {sec}（{m.group(1)}）: {shares_note({'order': m.group(2), 'close': close}, ex_).lstrip('。')}")
    if not out:
        return []
    return [f"\n{SHARES_HEAD}（{buy_usd():,}ドル分＝資金÷4。著者には渡さない）\n"] + out + (
        [f"- 2倍ETFで買う銘柄（{ex_[0]}）なので、ETFの株数。合図・損切り・手じまいは元の株 {sym} の値段で判定する"] if ex_ else [])


if __name__ == "__main__":
    main()
