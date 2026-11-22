#!/usr/bin/env python3
"""並行記録（仮の資金）: 同じ日に同じ金額で始めた仮の資金を、今のルール・静観・乗り換えで比べる（2026-11-22 ユーザーの指示「全て検証して」の検証案D）。

今回の下げが過去のデータで確かめられない種類のものなら、過去の検証より「これからの記録」が判断材料になる。毎週の週次レビュー（累計の方の節7）で、
同じ日（既定 2026-11-23）から始めた次の仮の資金を並べる。どれも決まりはプログラムが機械的に当てはめ、著者の判定もClaudeの判断も使わない。

  ① 今のルール: 毎朝の記録の合図を4銘柄の枠・2倍ETF込みでルールどおりに売買（tools/theme_replay.py と同じ計算）
  ② 今のルール＋「損で終わった売買が3回続いたら10取引日（②'は20取引日）新しい買いを止める」（検証案Cの形。長い下げを含む期間でも最大下落率が下がった）
  ③ 静観: 短期国債（^IRX の利回りを毎日の利息にする）
  ④ 上がっている業種: S&P500の9業種のETFのうち、3か月の上げが大きい順に2つ（200日線より上で3か月がプラスのものだけ。足りない分は短期国債）。
     毎月の最初の取引日に入れ替える（tools/backtest_crash_mode.py の行き先と同じ決まり）
  ⑤ 上がっている銘柄: S&P500の今の構成銘柄で、終値＞150日線＞20取引日前の150日線、終値＞50日線、RS≧90 の銘柄のうちRSの高い4銘柄を、
     毎週の最初の取引日の寄り付きで1銘柄＝資金÷4で買う。損切りは買値の15%下（日中）、引けで50日線割れなら次の寄り付きで売る。空いた枠は次の週に埋める
  参考: S&P500（SPY、配当込み）

使い方: tools/paper_track.py <record.json を置いたディレクトリ> [--start 2026-11-23] [--capital 12000] [--out FILE]
"""
import argparse
import csv
import datetime as dt
import os
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import theme_replay as tr
import theme_scan as ts
from backtest_lib import DEFAULT_CACHE, MEMBERS_URL, curl

START = "2026-11-23"   # 並行記録を始めた日（2026-11-22 ユーザーの指示「全て検証して最善策を提案して」の翌取引日）
SECTORS = ["XLB", "XLE", "XLF", "XLI", "XLK", "XLP", "XLU", "XLV", "XLY"]
SEC_JA = {"XLB": "素材", "XLE": "エネルギー", "XLF": "金融", "XLI": "資本財", "XLK": "情報技術", "XLP": "生活必需品", "XLU": "公益", "XLV": "ヘルスケア", "XLY": "一般消費財"}
COST, STOP = 0.001, 0.15


def sma(c, j, n):
    return sum(c[j - n + 1:j + 1]) / n if j >= n - 1 else None


def tbill(irx, cal):
    """短期国債の資金の比（cal[0]＝1）"""
    pos = {d: k for k, d in enumerate(irx["date"])}
    v, out = 1.0, [1.0]
    for a, b in zip(cal, cal[1:]):
        k = max(i for i, d in enumerate(irx["date"]) if d <= a) if a not in pos else pos[a]
        v *= 1 + irx["c"][k] / 100 / 252
        out.append(v)
    return out


def sectors(cal, etf, irx):
    """④ 上がっている業種（毎月の最初の取引日に入れ替え。決めるのは前の取引日の引け）"""
    tb = tbill(irx, cal)
    v, w, out, log = 1.0, {}, [1.0], []
    for k in range(1, len(cal)):
        d, p = cal[k], cal[k - 1]
        r = 0.0
        for s, wt in w.items():
            e = etf[s]
            i, j = e["date"].index(p), e["date"].index(d)
            r += wt * (e["c"][j] / e["c"][i] - 1)
        r += (1 - sum(w.values())) * (tb[k] / tb[k - 1] - 1)
        v *= 1 + r
        if k == 1 or d[:7] != p[:7]:   # 月が変わった日（と始めの日）に、その日の引けで次の持ち方を決める
            sc = []
            for s in SECTORS:
                e = etf[s]
                j = e["date"].index(d)
                m200 = sma(e["c"], j, 200)
                if m200 and e["c"][j] > m200 and e["c"][j] / e["c"][j - 63] - 1 > 0:
                    sc.append((e["c"][j] / e["c"][j - 63] - 1, s))
            sc.sort(reverse=True)
            nw = {s: 0.5 for _, s in sc[:2]}
            v *= 1 - COST * sum(abs(nw.get(s, 0) - w.get(s, 0)) for s in set(nw) | set(w))
            if nw != w:
                log.append((d, "・".join(SEC_JA[s] for s in nw) or "短期国債"))
            w = nw
        out.append(v)
    return out, log


def rising_stocks(cal, got, spy_dates):
    """⑤ 上がっている銘柄（S&P500、RSの高い4銘柄、毎週の最初の取引日に空き枠を埋める）"""
    rs_raw = lambda c, j: (0.4 * (c[j] / c[j - 63] - 1) + 0.2 * (c[j] / c[j - 126] - 1) + 0.2 * (c[j] / c[j - 189] - 1)
                           + 0.2 * (c[j] / c[j - 252] - 1))
    pos = {s: {d: k for k, d in enumerate(x["date"])} for s, x in got.items()}
    cash, held, out, log = 1.0, [], [], []
    for k, d in enumerate(cal):
        p = cal[k - 1] if k else None
        # 売り（寄り付き: 前の日に50日線割れ）と損切り（日中）
        still = []
        for h in held:
            x, j = got[h["s"]], pos[h["s"]].get(d)
            if j is None:
                still.append(h)
                continue
            if h.get("sell"):
                cash += h["sh"] * x["o"][j] * (1 - COST)
                log.append((d, f"{h['s']} 売り（50日線割れ）{x['o'][j] / h['px'] - 1:+.1%}"))
                continue
            if x["l"][j] <= h["px"] * (1 - STOP):
                fill = min(x["o"][j], h["px"] * (1 - STOP))
                cash += h["sh"] * fill * (1 - COST)
                log.append((d, f"{h['s']} 損切り {fill / h['px'] - 1:+.1%}"))
                continue
            m50 = sma(x["c"], j, 50)
            h["sell"] = m50 is not None and x["c"][j] < m50
            h["v"] = x["c"][j]
            still.append(h)
        held = still
        # 週の最初の取引日の寄り付きで買う（決めるのは前の取引日の引け）
        week_start = k == 0 or dt.date.fromisoformat(d).isocalendar()[1] != dt.date.fromisoformat(p).isocalendar()[1]
        if week_start and p and len(held) < 4:
            pool, cand = [], []
            for s, x in got.items():
                j = pos[s].get(p)
                if j is None or j < 260:
                    continue
                pool.append(rs_raw(x["c"], j))
            pool.sort()
            import bisect
            for s, x in got.items():
                j = pos[s].get(p)
                if j is None or j < 260 or s in {h["s"] for h in held}:
                    continue
                c = x["c"]
                m150, m150p, m50 = sma(c, j, 150), sma(c, j - 20, 150), sma(c, j, 50)
                rs = 99 * bisect.bisect_left(pool, rs_raw(c, j)) / max(1, len(pool) - 1)
                if m150 and m150p and m50 and c[j] > m150 > m150p and c[j] > m50 and rs >= 90 and pos[s].get(d) is not None:
                    cand.append((rs, s))
            eq = cash + sum(h["sh"] * h["v"] for h in held)
            for rs, s in sorted(cand, reverse=True)[:4 - len(held)]:
                x, j = got[s], pos[s][d]
                amt = min(eq / 4, cash)
                if amt <= 0:
                    break
                px = x["o"][j]
                held.append({"s": s, "px": px, "sh": amt * (1 - COST) / px, "v": x["c"][j]})
                cash -= amt
                log.append((d, f"{s} 買い（RS {rs:.0f}）"))
        out.append(cash + sum(h["sh"] * h["v"] for h in held))
    return out, log, held


def section(rec_dir, start=START, capital=12000.0, title="## 7. 並行記録（同じ日に始めた仮の資金。著者の判定もClaudeの判断も使わない）"):
    L = [title, ""]
    w = L.append
    spy = ts.fetch_daily("SPY")
    cal = [d for d in spy["date"] if d >= start]
    if len(cal) < 2:
        w(f"記録は {start} から始まる（まだ取引日が1日以下）。\n")
        return "\n".join(L)
    irx = ts.fetch_daily("^IRX")
    w(f"{start} から {cal[-1]} まで（{len(cal)}取引日）。資金はどれも {capital:,.0f}ドルから。決まりは `tools/paper_track.py` の説明のとおり。"
      "今回の下げが過去のデータで確かめられない種類のものかもしれないため、過去の検証と別に、これからの成績を同じ条件で並べる（2026-11-22 ユーザーの指示）。\n")
    rows = []
    # ①② 今のルール（記録の合図）
    recs = [r for r in tr.load_records(rec_dir) if r["trade_date"] >= spy["date"][spy["date"].index(cal[0]) - 1]]
    if recs:
        rp = tr.Replay(recs, capital)
        x = rp.simulate(True)
        rows.append(("① 今のルール（記録の合図、2倍ETF込み）", x["final"] / capital, x["mdd"], f"売った{len(x['done'])}・保有{len(x['open'])}"))
        for n_, lab_ in ((10, "②"), (20, "②'")):
            x2 = rp.simulate(True, cbk=(3, 3, n_))
            rows.append((f"{lab_} 今のルール＋損で終わった売買が3回続いたら{n_}取引日新しい買いを止める", x2["final"] / capital, x2["mdd"],
                         f"止めた: {'、'.join(a_[5:] + '〜' + (b_[5:] if b_[:2] == '20' else b_) for a_, b_ in rp.paused) or 'なし'}・売った{len(x2['done'])}・保有{len(x2['open'])}"))
    else:
        rows.append(("① 今のルール（記録の合図、2倍ETF込み）", None, None, "まだ記録がない"))
    tb = tbill(irx, cal)
    rows.append(("③ 静観（短期国債）", tb[-1], 0.0, ""))
    with ThreadPoolExecutor(8) as ex:
        etf = dict(zip(SECTORS, ex.map(ts.fetch_daily, SECTORS)))
    sv, slog = sectors(cal, etf, irx)
    pk, md = 0, 0
    for v in sv:
        pk = max(pk, v)
        md = max(md, 1 - v / pk)
    rows.append(("④ 上がっている業種（ETF 2つ、毎月入れ替え）", sv[-1], md, "今: " + (slog[-1][1] if slog else "短期国債")))
    mc = curl(MEMBERS_URL)
    if not mc.startswith("ticker,"):
        p = os.path.join(DEFAULT_CACHE, "members.csv")
        mc = open(p).read() if os.path.exists(p) else "ticker,start_date,end_date\n"
    sp = sorted({r["ticker"] for r in csv.DictReader(mc.splitlines()) if not r["end_date"]})
    with ThreadPoolExecutor(8) as ex:
        got = {s: d for s, d in zip(sp, ex.map(ts.fetch_daily, sp)) if d and len(d["c"]) > 260}
    rv, rlog, rheld = rising_stocks(cal, got, spy["date"])
    pk, md = 0, 0
    for v in rv:
        pk = max(pk, v)
        md = max(md, 1 - v / pk)
    rows.append(("⑤ 上がっている銘柄（S&P500のRS上位4銘柄、毎週）", rv[-1], md, "保有: " + ("、".join(h["s"] for h in rheld) or "なし")))
    j0 = spy["date"].index(cal[0])
    spyv = [spy["c"][spy["date"].index(d)] / spy["c"][j0] for d in cal]
    pk, md = 0, 0
    for v in spyv:
        pk = max(pk, v)
        md = max(md, 1 - v / pk)
    rows.append(("参考: S&P500（SPY）", spyv[-1], md, ""))
    w("| 仮の資金 | 今の資金 | 損益 | 最大下落率 | 備考 |")
    w("|---|---|---|---|---|")
    for nm, r, m, note in rows:
        w(f"| {nm} | {'-' if r is None else f'{capital * r:,.0f}ドル'} | {'-' if r is None else f'{(r - 1) * 100:+.1f}%'} | "
          f"{'-' if m is None else f'{m * 100:.1f}%'} | {note} |")
    if rlog:
        w("\n⑤の直近の売買: " + "、".join(f"{d[5:]} {t}" for d, t in rlog[-8:]))
    if slog:
        w("\n④の入れ替え: " + "、".join(f"{d[5:]} {t}" for d, t in slog[-6:]))
    w("\n- 仮の資金は、決まりを機械的に当てはめた計算で、Claudeによる個別銘柄の売買判断ではない。②〜⑤を採用するかはユーザーが決める。")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--start", default=START)
    ap.add_argument("--capital", type=float, default=12000)
    ap.add_argument("--out")
    a = ap.parse_args()
    text = section(a.dir, a.start, a.capital, "# 並行記録（同じ日に始めた仮の資金）") + "\n"
    if a.out:
        open(a.out, "w", encoding="utf-8").write(text)
    print(text)


if __name__ == "__main__":
    main()
