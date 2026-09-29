#!/usr/bin/env python3
"""1銘柄の直近Nカ月で、各ルールがどこで買い・売りになったかをチャートに印を付けて描く（ルールの機械的な再現。Claudeの判断ではない）

使い方:
  tools/entry_chart.py <ティッカー> <出力ディレクトリ> [--months 6]
    <出力>/<ティッカー>_entries.png（チャート）と <ティッカー>_entries.md（売買の一覧）を書く。

ルール（すべて引け後に判定し、翌日の寄り付きで売買。損切りは買値の15%下＝引け値で判定）:
  B  ボリンジャー メソッドIII（%b<0.05かつ21日II%>0）→ 引けで上のバンド以上で手じまい           …採用中
  M  ミネルヴィニ（トレンドテンプレート＋ベース（最高値から3週以上・調整幅35%以内）の高値を出来高2倍で上抜け）→ 50日線割れで手じまい …採用中
  W  ワインスタイン10週（週足で直前10週の高値を出来高2倍で上抜け、10週線が上向き）→ 週足の終値が10週線割れ …採用中
  C  急落の底（急落の前に50日線>200日線、5日で−15%以上、RSI(2)≦10）→ 終値が5日線を上回ったら手じまい（コナーズ） …採用中（2026-09-27、RSI(2)は2026-09-29に≦5から≦10）
  E1 大陽線の反発（強い銘柄・押し・出来高の減少の後の大陽線）→ 上のバンドで手じまい           …検証中（採用していない）
  E2 包み足（強い銘柄・押しの後）→ 上のバンドで手じまい                                         …検証中（採用していない）
RSランキングはS&P500の構成銘柄の中での百分位（キャッシュの株価で計算）。
"""
import argparse
import csv
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_candle as bcd
import backtest_connors as bc
import backtest_crash as bcr
import backtest_compare2 as c2
import backtest_minervini2 as bm2
import backtest_swing as bs
import backtest_theme as bth
import backtest_trend as bt
from backtest_lib import DEFAULT_CACHE, load_prices

STOP = 0.15
BAND = lambda j, s, k, px: s["pctb"][j] is not None and s["pctb"][j] >= 1.0
RULES = [  # 記号, 名前, 仕掛け, 手じまい, 手じまいの名前, 色（カテゴリの固定順）
    ("B", "ボリンジャーIII（採用中）", lambda i, s: bs.O_method3(i, s), BAND, "上のバンド", "#2a78d6"),
    ("M", "ミネルヴィニ（採用中）", bm2.E_base(2.0), bt.X_BELOW50, "50日線割れ", "#eb6834"),
    ("W", "ワインスタイン10週（採用中）", bt.E_weinstein(10, ma="10"), bt.X_weekly_below("10"), "10週線割れ", "#1baf7a"),
    ("C", "急落の底（採用中）", lambda i, s: bcr.C3R10(i, s), lambda j, s, k, px: s["ma5"][j] is not None and s["c"][j] > s["ma5"][j], "5日線を上回る", "#e34948"),
    ("N", "新高値V2（採用中）", lambda i, s: c2.V2(i, s), bt.X_BELOW50, "50日線割れ", "#4a3aa7"),
    ("E1", "大陽線の反発（検証中）", bcd.E1, BAND, "上のバンド", "#eda100"),
    ("E2", "包み足（検証中）", bcd.E2, BAND, "上のバンド", "#e87ba4"),
]


def trades_of(s, entry, exit_fn, start):
    """1銘柄の売買。まだ手じまっていない建玉も「保有中」として返す"""
    out, n, i = [], len(s["c"]), 200
    while i < n - 1:
        if s["date"][i] < start or entry(i, s) is None:
            i += 1
            continue
        e, px = i + 1, s["o"][i + 1]
        t = {"sig": s["date"][i], "in": s["date"][e], "ie": e, "px": px, "out": None, "io": None, "why": "保有中"}
        for j in range(i + 1, n):
            k = j - i
            if s["c"][j] <= px * (1 - STOP):
                t["why"] = "損切り"
            elif exit_fn(j, s, k, px):
                t["why"] = "手じまい条件"
            else:
                continue
            if j + 1 < n:
                t.update(out=s["date"][j + 1], io=j + 1, sell=s["o"][j + 1])
            else:
                t["why"] += "（翌日の寄り付きで売り）"
            break
        last = t["sell"] if t["out"] else s["c"][-1]
        t["ret"] = last / px - 1
        out.append(t)
        if t["io"] is None:
            break
        i = t["io"]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ticker")
    ap.add_argument("outdir")
    ap.add_argument("--months", type=int, default=6)
    ap.add_argument("--cache", default=DEFAULT_CACHE)
    a = ap.parse_args()
    sym = a.ticker.upper()
    s = load_prices(a.cache, sym)
    if not s or len(s["c"]) < 260:
        sys.exit(f"{sym} の株価が足りません（1年分以上が必要）。先に backtest_lib のキャッシュを更新してください")
    bt.prepare(s)
    bs.prepare(s)
    bm2.add_pivot(s)
    bc.prepare(s)
    c2.add_udvr(s)
    sp = [r["ticker"] for r in csv.DictReader(open(os.path.join(a.cache, "members.csv"))) if not r["end_date"]]
    bth.rs_ranks(a.cache, sorted(set(sp) | {sym}), {sym: s})
    last = dt.date.fromisoformat(s["date"][-1])
    start = (last - dt.timedelta(days=int(a.months * 30.44))).isoformat()
    res = [(r, trades_of(s, r[2], r[3], start)) for r in RULES]

    # ---- チャート ----
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    plt.rcParams.update({"font.family": "WenQuanYi Zen Hei", "font.size": 12})
    import logging
    logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
    i0 = next(i for i, d in enumerate(s["date"]) if d >= start)
    x = list(range(len(s["c"]) - i0))
    rng = range(i0, len(s["c"]))
    O, H, Lo, C = ([s[k][i] for i in rng] for k in ("o", "h", "l", "c"))
    fig, (p, pv) = plt.subplots(2, 1, figsize=(15, 10), dpi=160, sharex=True, gridspec_kw={"height_ratios": [4, 1], "hspace": 0.05})
    ink, muted, up_c, dn_c = "#1f1f1f", "#8a8a85", "#9a9a95", "#3d3d3a"
    for k in x:
        col = up_c if C[k] >= O[k] else dn_c
        p.vlines(k, Lo[k], H[k], color=col, lw=0.9)
        p.bar(k, abs(C[k] - O[k]) or H[k] * 0.001, bottom=min(O[k], C[k]), color=col, width=0.7)
    for key, lab, ls in (("bb_up", "ボリンジャー +2σ", ":"), ("bb_dn", "ボリンジャー −2σ", ":"), ("bb_mid", "20日線", "-"), ("ma50", "50日線", "-")):
        p.plot(x, [s[key][i] for i in rng], color=muted if key.startswith("bb_") else ("#5b5b57" if key == "ma50" else "#b0b0aa"),
               lw=1.2 if key == "ma50" else 1, ls=ls)
    span = max(H) - min(Lo)
    handles = []
    for n, (r, trs) in enumerate(res):
        tag, name, _, _, xname, color = r
        for t in trs:
            ke = t["ie"] - i0
            yb = Lo[ke] - span * (0.03 + 0.035 * n)
            p.scatter(ke, yb, s=170, facecolor=color, edgecolor="white", lw=2, zorder=5)
            p.annotate(tag, (ke, yb), xytext=(0, -17), textcoords="offset points", ha="center", fontsize=11, color=ink, weight="bold")
            if t["io"] is not None:
                ko = t["io"] - i0
                ys = H[ko] + span * (0.03 + 0.035 * n)
                p.scatter(ko, ys, s=150, marker="X", facecolor=color, edgecolor="white", lw=1.5, zorder=5)
                p.annotate(f"{tag} {t['ret'] * 100:+.0f}%", (ko, ys), xytext=(9, -4), textcoords="offset points", ha="left",
                           fontsize=10, color=ink)
        handles.append(Line2D([], [], marker="o", ls="", markerfacecolor=color, markeredgecolor="white", markersize=12,
                              label=f"{tag} {name}・{xname}（{len(trs)}回）"))
    handles += [Line2D([], [], marker="o", ls="", color=muted, markersize=11, label="丸＝買い（シグナルの翌日の寄り付き。下の文字はルール）"),
                Line2D([], [], marker="X", ls="", color=muted, markersize=11, label="バツ＝売り（翌日の寄り付き。数字は損益）")]
    p.legend(handles=handles, loc="upper left", fontsize=10.5, framealpha=0.9)
    p.set_ylim(min(Lo) - span * 0.25, max(H) + span * 0.25)
    p.grid(alpha=0.2)
    p.set_title(f"{sym} 直近{a.months}カ月（{s['date'][i0]}〜{s['date'][-1]}）の各ルールの買い・売り（ルールの機械的な再現）",
                loc="left", fontsize=14, color=ink)
    V, V50 = [s["v"][i] / 1e6 for i in rng], [(s["vol50"][i] or 0) / 1e6 for i in rng]
    pv.bar(x, V, color=[up_c if C[k] >= O[k] else dn_c for k in x], width=0.7)
    pv.plot(x, V50, color=ink, lw=1, label="50日平均出来高")
    pv.set_ylabel("出来高（百万株）")
    pv.legend(loc="upper left", fontsize=10)
    pv.grid(alpha=0.2)
    ticks = [k for k in x if k >= 8 and s["date"][i0 + k][:7] != s["date"][i0 + k - 1][:7]]
    pv.set_xticks(ticks, [s["date"][i0 + k][:7] for k in ticks])
    os.makedirs(a.outdir, exist_ok=True)
    png = os.path.join(a.outdir, f"{sym}_entries.png")
    fig.savefig(png, bbox_inches="tight")

    # ---- 一覧 ----
    L = [f"# {sym} 直近{a.months}カ月の各ルールの売買（{s['date'][i0]}〜{s['date'][-1]}）\n",
         "ルールの条件どおりに機械的に再現したもの（Claudeによる売買判断ではない）。シグナルの日の引け後に判定し、翌日の寄り付きで売買。"
         "損切りは買値の15%下（引け値で判定）。同じルールでは、手じまうまで次の買いはしない。\n",
         "| ルール | シグナルの日 | 買った日 | 買値 | 売った日 | 売値 | 理由 | 損益 |", "|---|---|---|---|---|---|---|---|"]
    for r, trs in res:
        if not trs:
            L.append(f"| {r[0]} {r[1]} | この期間はシグナルなし | | | | | | |")
        for t in trs:
            L.append(f"| {r[0]} {r[1]} | {t['sig']} | {t['in']} | {t['px']:,.2f} | {t['out'] or '—'} | "
                     f"{t['sell']:,.2f} | {t['why']} | {t['ret'] * 100:+.1f}% |" if t["out"] else
                     f"| {r[0]} {r[1]} | {t['sig']} | {t['in']} | {t['px']:,.2f} | 保有中 | （{s['date'][-1]}の終値 {s['c'][-1]:,.2f}） | {t['why']} | {t['ret'] * 100:+.1f}%（含み） |")
    closed = [t for _, trs in res for t in trs]
    L.append(f"\n- 売買の回数（すべてのルールの合計）: {len(closed)}回（うち保有中 {sum(1 for t in closed if t['out'] is None)}）")
    L.append(f"- 同じ期間の買い持ち（{s['date'][i0]}の寄り付き → {s['date'][-1]}の終値）: {(s['c'][-1] / s['o'][i0] - 1) * 100:+.1f}%")
    md = os.path.join(a.outdir, f"{sym}_entries.md")
    open(md, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))
    print(f"チャート: {png}", file=sys.stderr)


if __name__ == "__main__":
    main()
