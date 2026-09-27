#!/usr/bin/env python3
"""銘柄ごとの局面（上昇相場／レンジ）で手じまいを変えるバックテストと、売買の頻度の集計

使い方:
  tools/backtest_regime.py run [--out FILE]

ユーザーの考え方（2026-09-27）: 「レンジ相場なら最初の陰線ですぐ手じまう。上昇相場ならそんなことはしない（持ち続ける）」。
これをルールにして、採用中のルール（ボリンジャーIII・ミネルヴィニ）と押し目・短い押しの仕掛けで検証する。

局面の判定（数値はClaudeが置いたもので、本のルール表の値ではない）:
  上昇相場: 終値 > 50日線 > 200日線、50日線が20取引日前より2%以上高い、ADX(14) ≧ 20
  レンジ: それ以外
手じまい（局面別）:
  上昇相場のとき: 引けで50日線割れ（または20日線割れ）の翌日の寄り付き（持ち続ける）
  レンジのとき: 引けで上のバンド（+2σ）以上、または買値より上で引けた後の最初の下落の日（終値が前日より下）の翌日の寄り付き
  局面は「毎日判定し直す」と「仕掛けた日の局面で固定」の2通り。損切りは買値の15%下（ユーザー決定）。
"""
import argparse
import csv
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_connors as bc
import backtest_pullback as bp
import backtest_swing as bs
import backtest_theme as bth
import backtest_trend as bt
from backtest_lib import COSTS, DEFAULT_CACHE, Reporter, gen_trades, load_prices, load_universe, portfolio, spy_benchmark

RISK, STOP, COST = 0.02, 0.15, COSTS[2]
SLOTS = int(round(STOP / RISK, 6))


def up(i, s):
    """上昇相場: 終値 > 50日線 > 200日線、50日線が20日前より2%以上高い、ADX(14) ≧ 20"""
    if i < 20:
        return False
    c, m50, m200, a, m50p = s["c"][i], s["ma50"][i], s["ma200"][i], s["adx14"][i], s["ma50"][i - 20]
    if None in (m50, m200, a, m50p):
        return False
    return c > m50 > m200 and m50 >= m50p * 1.02 and a >= 20


# --- 手じまい（gen_trades の形: j, s, k, px。仕掛けのシグナルの日は j−k） ---
X_BAND = lambda j, s, k, px: s["pctb"][j] is not None and s["pctb"][j] >= 1.0
X_FIRST_DOWN = lambda j, s, k, px: s["c"][j] < s["c"][j - 1] and s["c"][j - 1] > px     # 上がった後の最初の下落
X_BELOW50 = lambda j, s, k, px: s["c"][j] < s["ma50"][j]
X_BELOW20 = lambda j, s, k, px: s["bb_mid"][j] is not None and s["c"][j] < s["bb_mid"][j]
X_MA5 = lambda j, s, k, px: s["c"][j] > s["ma5"][j]                                       # コナーズ: 5日線上抜け


def regime_exit(x_up, x_range, fixed):
    """上昇相場なら x_up、レンジなら x_range で手じまう。fixed=True なら仕掛けのシグナルの日の局面で固定"""
    return lambda j, s, k, px: (x_up if up(j - k if fixed else j, s) else x_range)(j, s, k, px)


def to_sim(x):
    """gen_trades 形の手じまいを backtest_swing.simulate 形に変換（simulate の仕掛けの日は t["entry"]、シグナルはその前日）"""
    return lambda j, s, k, t: ("open", "条件") if x(j, s, j - t["entry"] + 1, t["px"]) else None


def E_rsi2_up(i, s):
    """上昇相場の銘柄の短い押し: 局面が上昇相場で RSI(2) ≦ 10（コナーズの閾値を緩めた値）"""
    r = s["rsi2"][i]
    return r if r is not None and r <= 10 and up(i, s) else None


EXITS = [   # 名前, 手じまい, 局面を固定するか
    ("上昇相場は50日線割れ／レンジは上のバンド（毎日判定）", regime_exit(X_BELOW50, X_BAND, False)),
    ("上昇相場は50日線割れ／レンジは上がった後の最初の下落（毎日判定）", regime_exit(X_BELOW50, X_FIRST_DOWN, False)),
    ("上昇相場は20日線割れ／レンジは上のバンド（毎日判定）", regime_exit(X_BELOW20, X_BAND, False)),
    ("上昇相場は20日線割れ／レンジは上がった後の最初の下落（毎日判定）", regime_exit(X_BELOW20, X_FIRST_DOWN, False)),
    ("上昇相場は50日線割れ／レンジは上のバンド（仕掛けた日の局面で固定）", regime_exit(X_BELOW50, X_BAND, True)),
    ("上昇相場は50日線割れ／レンジは上がった後の最初の下落（仕掛けた日の局面で固定）", regime_exit(X_BELOW50, X_FIRST_DOWN, True)),
]


def rule_sets(data, mem, start, end):
    """{仕掛けの名前: [(手じまいの名前, トレード)]}。最初の要素が今の手じまい（比較の基準）"""
    g = lambda e, x, mh=120: gen_trades(data, mem, e, x, start, end, ok=bt.liquid, fill="open", max_hold=mh, stop_pct=STOP)
    out = {}
    out["ボリンジャーIII（%b<0.05かつII%>0）"] = [("今の手じまい: 上のバンド", bs.simulate(data, mem, bs.O_method3, bs.X_upper_band, start, end))] + \
        [(n, bs.simulate(data, mem, bs.O_method3, to_sim(x), start, end, max_hold=120)) for n, x in EXITS]
    out["ミネルヴィニ（トレンドテンプレート＋ベースの上抜け）"] = [("今の手じまい: 50日線割れ", g(bt.E_minervini(50), X_BELOW50, 500))] + \
        [(n, g(bt.E_minervini(50), x)) for n, x in EXITS]
    bp.LOOSE = True
    out["50日線の押し目（【緩めた条件】押しの日の翌日）"] = [("手じまい: 上のバンド", g(bp.E_touch, bp.with_break(X_BAND)))] + \
        [(n, g(bp.E_touch, x)) for n, x in EXITS]
    bp.LOOSE = False
    out["上昇相場の短い押し（RSI(2)≦10）"] = [("手じまい: 5日線上抜け（コナーズ）", g(E_rsi2_up, X_MA5, 30))] + \
        [(n, g(E_rsi2_up, x)) for n, x in EXITS]
    return out


def srt(tr):
    return sorted(tr, key=lambda t: (t["out"], t["sym"]))


def freq_table(w, rep, combos, days, years):
    """売買の頻度: 候補（シグナル）の件数、7銘柄の枠で実際に買った件数、買った日・売買した日・何か持っている日の割合"""
    w("| 組み合わせ | 候補の件数／年 | 候補が出た日の割合 | 実際に買った件数／年（ランダム順 中央値） | 買った日の割合 | 売買（買いか売り）した日の割合 | 何か持っている日の割合 | 年率（ランダム順 中央値） | 最大下落率（同） |")
    w("|---|---|---|---|---|---|---|---|---|")
    for lab, tr in combos:
        ps = [rep.port(tr, STOP, seed=k) for k in rep.SEEDS]
        med = lambda key: rep.med([p[key] for p in ps])
        sig_days = len({t["in"] for t in tr}) / len(days)
        w(f"| {lab} | {len(tr) / years:.0f} | {sig_days * 100:.0f}% | {med('taken') / years:.0f} | {med('buy_days') * 100:.0f}% | "
          f"{med('act_days') * 100:.0f}% | {med('busy_days') * 100:.0f}% | {med('cagr') * 100:.1f}% | {med('mdd') * 100:.1f}% |")


def section(w, rep, data, mem, start, end, days, years, title):
    w(title)
    rs = rule_sets(data, mem, start, end)
    for en, lst in rs.items():
        w(f"\n**{en}**\n")
        rep.header("シグナルの強い順")
        for xn, tr in lst:
            rep.line(xn, tr, STOP)
    b3, m50, pb, r2 = (rs[k] for k in rs)
    combos = [
        ("採用中: ボリンジャーIII＋ミネルヴィニ（今の手じまい）", srt(b3[0][1] + m50[0][1])),
        ("採用中の仕掛け＋局面別の手じまい（50日線／上がった後の最初の下落、毎日判定）", srt(b3[2][1] + m50[2][1])),
        ("採用中の仕掛け＋局面別の手じまい（50日線／上のバンド、毎日判定）", srt(b3[1][1] + m50[1][1])),
        ("採用中＋50日線の押し目（局面別: 50日線／上がった後の最初の下落）", srt(b3[0][1] + m50[0][1] + pb[2][1])),
        ("採用中＋上昇相場の短い押し（コナーズの手じまい）", srt(b3[0][1] + m50[0][1] + r2[0][1])),
        ("採用中＋上昇相場の短い押し（局面別: 50日線／上がった後の最初の下落）", srt(b3[0][1] + m50[0][1] + r2[2][1])),
        ("4つの仕掛けすべて（局面別: 50日線／上がった後の最初の下落）", srt(b3[2][1] + m50[2][1] + pb[2][1] + r2[2][1])),
    ]
    w("\n**組み合わせ（7銘柄の枠を共有）と売買の頻度**\n")
    rep.header("シグナルの強い順")
    for lab, tr in combos:
        rep.line(lab, tr, STOP)
    w("")
    freq_table(w, rep, combos, days, years)
    return rs


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/局面別の手じまいと売買の頻度.md")
    r.add_argument("--skip-sp500", action="store_true")
    a = ap.parse_args()

    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: 局面別の手じまいと売買の頻度\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_regime.py\n---\n")
    w("# 銘柄ごとの局面（上昇相場／レンジ）で手じまいを変えるバックテストと、売買の頻度\n")
    w("ユーザーの考え方「レンジ相場なら最初の陰線ですぐ手じまう、上昇相場なら持ち続ける」をルールにして検証した。"
      "局面の判定の数値はClaudeが置いたもので、本のルール表の値ではない。\n")
    w("- 上昇相場: 終値 > 50日線 > 200日線、50日線が20取引日前より2%以上高い、ADX(14) ≧ 20。レンジ: それ以外。")
    w("- 手じまい（局面別）: 上昇相場なら引けで50日線割れ（または20日線割れ）、レンジなら引けで上のバンド以上、または買値より上で引けた後の最初の下落の日。いずれも翌日の寄り付きで手じまう。")
    w("- 局面は毎日判定し直す（保有中に上昇相場からレンジに変われば手じまいも変わる）場合と、仕掛けた日の局面で固定する場合の2通り。")
    w("- 損切りは買値の15%下、片道0.1%、リスク2%で建玉（13.3%×7銘柄）。")
    w("- 「上昇相場の短い押し」は頻度を上げる候補として加えた: 局面が上昇相場の銘柄で RSI(2) ≦ 10（コナーズ『短期売買戦略のギャップとトレンド』の閾値5を10に緩めた値）の翌日の寄り付きで買う。\n")

    members, data = load_universe(a.cache, min_bars=260)
    for s in data.values():
        bt.prepare(s)
        bs.prepare(s)
        bc.prepare(s)
    spy = load_prices(a.cache, "SPY")
    end = dt.date.today().isoformat()

    # --- テーマ監視銘柄（直近3年） ---
    wl = bth.load_watchlist()
    tdata = {s: data[s] for s in wl if s in data}
    for s in wl:
        if s not in tdata:
            d = load_prices(a.cache, s)
            if d and len(d["c"]) > 260:
                bt.prepare(d)
                bs.prepare(d)
                bc.prepare(d)
                tdata[s] = d
    tmem = {s: [("0000-00-00", "9999-12-31")] for s in tdata}
    sp_now = [r["ticker"] for r in csv.DictReader(open(os.path.join(a.cache, "members.csv"))) if not r["end_date"]]
    bth.rs_ranks(a.cache, sorted(set(sp_now) | set(tdata)), tdata)   # 監視銘柄のRS（この後S&P500全体のRSで上書きされない順に実行）
    today = dt.date.today()
    start3 = today.replace(year=today.year - 3).isoformat()
    days3 = [d for d in spy["date"] if start3 <= d <= end]
    y3 = len(days3) / 252
    rep3 = Reporter(w, tdata, days3, [("前半", start3, "2024-12-31"), ("後半", "2025-01-01", end)], y3, cost=COST, risk=RISK)
    rs3 = section(w, rep3, tdata, tmem, start3, end, days3, y3,
                  "## 1. テーマ監視銘柄（直近3年。監視銘柄を今の時点で選んでいるため後知恵あり）\n")

    # --- SNDK（2026年8〜9月） ---
    s = tdata.get("SNDK")
    if s:
        w("\n## 2. SNDK（2026年8〜9月）の局面と、各ルールの売買\n")
        w("| 日付 | 終値 | 前日比 | 50日線 | 50日線の20日前比 | ADX(14) | %b | 局面 |")
        w("|---|---|---|---|---|---|---|---|")
        for i, d in enumerate(s["date"]):
            if "2026-08-15" <= d:
                m50, m50p = s["ma50"][i], s["ma50"][i - 20]
                w(f"| {d} | {s['c'][i]:.2f} | {(s['c'][i] / s['c'][i - 1] - 1) * 100:+.1f}% | {m50:.2f} | {(m50 / m50p - 1) * 100:+.1f}% | "
                  f"{s['adx14'][i]:.1f} | {s['pctb'][i]:.2f} | {'上昇相場' if up(i, s) else 'レンジ'} |")
        w("")
        for en, lst in rs3.items():
            for xn, tr in lst:
                for t in tr:
                    if t["sym"] == "SNDK" and t["in"] >= "2026-08-15":
                        w(f"- {en}・{xn}: 買い {t['in']} {t['px']:.2f} → 売り {t['out']}（{t['why']}） 損益 {t['ret'] * 100:+.1f}%")
        w("")

    # --- S&P500全体（2015〜） ---
    if not a.skip_sp500:
        bt.add_rs_rank(data, members)
        start = "2015-01-02"
        days = [d for d in spy["date"] if start <= d <= end]
        y = len(days) / 252
        rep = Reporter(w, data, days, [("前半", start, "2020-12-31"), ("後半", "2021-01-01", end)], y, cost=COST, risk=RISK)
        section(w, rep, data, members, start, end, days, y, "\n## 3. S&P500全体（その日の構成銘柄、2015年〜。後知恵なし）\n")
        sc, sm = spy_benchmark(spy, days)

    w("## 4. 注意\n")
    w("- 局面の判定の数値（50日線の2%上昇、ADX 20）は1通りしか試していない。前半・後半の両方で成り立つかを重視すること。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
