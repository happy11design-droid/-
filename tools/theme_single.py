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
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_swing as bs
import backtest_trend as bt
from backtest_regime import up
from backtest_minervini2 import add_pivot
from backtest_lib import MEMBERS_URL, curl
from theme_scan import earnings_date, fetch_daily, pct

STOP = 0.15


def mark(ok):
    return "満たす" if ok else "満たさない"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ticker")
    ap.add_argument("out")
    ap.add_argument("--hold", nargs=3, metavar=("買値", "買った日", "ルール"))
    a = ap.parse_args()
    sym = a.ticker.upper()
    d = fetch_daily(sym)
    if not d or len(d["c"]) < 260:
        sys.exit(f"{sym} の日足を取得できませんでした（1年分以上が必要）")
    # RSランキング: S&P500の構成銘柄の中での百分位
    txt = curl(MEMBERS_URL)
    sp = [r["ticker"] for r in csv.DictReader(txt.splitlines()) if not r["end_date"]] if txt.startswith("ticker,") else []
    raw = lambda c: 0.4 * (c[-1] / c[-64] - 1) + 0.2 * (c[-1] / c[-127] - 1) + 0.2 * (c[-1] / c[-190] - 1) + 0.2 * (c[-1] / c[-253] - 1)
    with ThreadPoolExecutor(8) as ex:
        pool = sorted(raw(x["c"]) for x in ex.map(fetch_daily, sp) if x and len(x["c"]) > 253)
    bt.prepare(d)
    bs.prepare(d)
    add_pivot(d)
    i = len(d["c"]) - 1
    if len(pool) > 50:
        d["rs"][i] = 99 * bisect.bisect_left(pool, raw(d["c"])) / (len(pool) - 1)
    c, day = d["c"][i], d["date"][i]
    rs = d["rs"][i]

    L = []
    w = L.append
    w(f"# {sym} を採用ルールに当てはめた結果（{day}の引け時点）\n")
    w(f"- 終値 {c:.2f}（前日比 {pct(c / d['c'][i - 1] - 1)}）、RSランキング {'取得不可' if rs is None else f'{rs:.0f}'}（S&P500の中での百分位）、次回決算予定日 {earnings_date(sym)}")
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
        w("- 注文の目安（A）: 翌日の寄り付きで買い、損切りは買値の15%下、引けで上部バンド以上になった翌日の寄り付きで手じまい")
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
    w("## 3. 上抜け: ワインスタイン10週\n")
    w(f"- 週足の終値 {d['w_c'][i] or c:.2f}、直前10週の高値 {d['w_hi_prev'][10][i] or float('nan'):.2f}、10週線 {d['w_ma10'][i] or float('nan'):.2f}（前週 {d['w_ma10_1'][i] or float('nan'):.2f}）、30週線 {d['w_ma30'][i] or float('nan'):.2f}")
    w(f"- 条件（週足の終値が直前10週の高値を出来高2倍で上抜け、10週線が上向き）: **{mark(w10)}**" + ("" if wk else "（判定は週の最終取引日だけ。今日の値は週の途中の参考）"))
    h10, m10, m10p = d["w_hi_prev"][10][i], d["w_ma10"][i], d["w_ma10_1"][i]
    pat_w = "A" if w10 else ("B" if h10 and m10 and m10p and m10 > m10p and h10 * 0.95 <= c <= h10 else "該当なし")
    w(f"- スクリプトのパターン判定: **{pat_w}**（A=条件成立、B=10週線が上向きで、終値が直前10週の高値の−5%以内）")
    if pat_w == "B":
        w(f"- 予約注文の目安（B）: 逆指値買い {h10:.2f}（本のルールは週足の終値で判定するので近似。上抜けの週の出来高は直前4週の平均の2倍以上）")
    w("")
    w(f"## まとめ（スクリプトのパターン判定）\n\n- ボリンジャーIII: {pat_b}／ミネルヴィニ: {pat_m}／ワインスタイン10週: {pat_w}（A=条件成立、B=成立が目前で予約注文の候補）\n")

    if a.hold:
        px, bd, rule = float(a.hold[0]), a.hold[1], a.hold[2]
        stop = px * (1 - STOP)
        w("## 4. 保有中の確認\n")
        w(f"- ルール: {rule}／買った日: {bd}／買値: {px:.2f}／損益: {pct(c / px - 1)}／損切り価格（買値の15%下）: {stop:.2f}" + ("（**下回っている**）" if c <= stop else ""))
        if "ボリンジャー" in rule:
            w(f"- 手じまい条件（引けで上部バンド以上）: {mark(pb >= 1)}（上部バンド {d['bb_up'][i]:.2f}）")
        elif "ミネルヴィニ" in rule:
            w(f"- 手じまい条件（引けで50日線割れ）: {mark(c < m50)}（50日線 {m50:.2f}）")
        elif "ワインスタイン" in rule:
            w(f"- 手じまい条件（週足の終値が10週線割れ、週の最終取引日に判定）: {mark(wk and d['w_c'][i] < d['w_ma10'][i])}（10週線 {d['w_ma10'][i]:.2f}）")
        w("")
    text = "\n".join(L) + "\n"
    open(a.out, "w", encoding="utf-8").write(text)
    print(text)


if __name__ == "__main__":
    main()
