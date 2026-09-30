#!/usr/bin/env python3
"""その日（次の取引日）に株価が上がりやすい銘柄・下がりやすい銘柄を、過去の統計から出す（新分析ツールの派生。検討中）

使い方:
  tools/backtest_lib.py fetch                       # S&P500の構成銘柄の日足（共通。初回だけ、約1分）
  tools/daily_odds.py backtest [--out FILE]         # 点数の作り方を決め（2015〜2021年）、2022年以降で確かめる（約3分）。
                                                    # 点数の表（tools/daily_odds_model.json）とレポートを書く
  tools/daily_odds.py today <出力.md> [--asof YYYY-MM-DD] [--tickers A,B,...]
                                                    # 監視銘柄（テーマ監視銘柄.md）の、次の取引日の上がる・下がる確率（約1分）

考え方:
  - 引け後に分かる数値（RSI(2)・引けの位置・連続上昇/下落の日数・移動平均からの離れ・出来高・値動きの大きさ・
    S&P500のRSI(2)とその日の騰落率・VIX）を、それぞれ5段階に分け、段階ごとの点数をロジスティック回帰で決める。
  - 点数の作り方は 2015〜2021年のS&P500（その日の構成銘柄）だけで決め、2022年以降は一切使っていない。
  - 表示する確率は「2022年以降に、同じくらいの点数だった日に実際に上がった割合」（確認期間の実績）。
    モデルの計算値そのものは、確認期間では外れる方向にずれた（強気に出すぎた）ため、表示には使わない。
  - 3つの「上がる」を別々に出す:
      前日比   … 次の取引日の終値 > 今日の終値（証券会社の「前日比」。寄り付きの窓を含むので、この通りには売買できない）
      寄り引け … 次の取引日の終値 > 次の取引日の始値（朝7時の結果を見て寄り付きで買う・引けで売るなら、こちら）
      対市場   … 次の取引日の騰落率（前日比）> S&P500（SPY）の騰落率（市場全体の上げ下げを除いた、銘柄の強さ）

数値と事実だけで、売買の判断はしない。採用ルール（テーマ監視）とは別の、検討中のツール。NotebookLMは使わない。
"""
import argparse
import datetime as dt
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backtest_lib import DEFAULT_CACHE, is_member, load_prices, load_universe, rsi_wilder, sma
from backtest_theme import load_watchlist

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
MODEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "daily_odds_model.json")
REPORT = os.path.join(ROOT, "新分析ツール", "バックテスト結果", "その日の上げ下げの確率.md")
DESIGN_END, VERIFY_START = "2021-12-31", "2022-01-01"
COST = 0.001   # 片道（backtest_lib.COSTS の一番厳しい値）

FEATS = [  # (キー, 表示名, 表示の書式)
    ("rsi", "RSI(2)", "{:.0f}"),
    ("r1", "今日の値動き（ATR何本分）", "{:+.1f}"),
    ("clv", "引けの位置（今日の値幅の中、0=安値・1=高値）", "{:.2f}"),
    ("streak", "連続の上昇(+)・下落(−)の日数", "{:+.0f}"),
    ("d5", "5日線からの離れ（ATR何本分）", "{:+.1f}"),
    ("d50", "50日線からの離れ（ATR何本分）", "{:+.1f}"),
    ("vr", "出来高（50日平均の何倍）", "{:.1f}"),
    ("r20", "20日の騰落率", "{:+.1%}"),
    ("atrp", "値動きの大きさ（ATR÷株価）", "{:.1%}"),
    ("spy_rsi", "S&P500のRSI(2)", "{:.0f}"),
    ("spy_r1", "S&P500の今日の騰落率", "{:+.1%}"),
    ("vix", "VIX", "{:.1f}"),
]
KEYS = [k for k, _, _ in FEATS]
LABELS = [("cc", "前日比"), ("oc", "寄り引け"), ("rel", "対市場")]


# ---------- 数値 ----------

def arr(x):
    return np.array([np.nan if v is None else v for v in x], float)


def stock_feats(d):
    """銘柄の数値（引け後に分かるものだけ）と、次の取引日の結果。配列の i 番目は i 日目の引け後の値"""
    c, o, h, l, v = (np.array(d[k], float) for k in ("c", "o", "h", "l", "v"))
    n = len(c)
    pc = np.r_[c[0], c[:-1]]
    tr = np.maximum.reduce([h - l, np.abs(h - pc), np.abs(l - pc)])
    atr = arr(sma(list(tr), 14))
    with np.errstate(divide="ignore", invalid="ignore"):
        streak = np.zeros(n)
        for i in range(1, n):
            streak[i] = max(streak[i - 1], 0) + 1 if c[i] > c[i - 1] else min(streak[i - 1], 0) - 1 if c[i] < c[i - 1] else 0
        f = {
            "rsi": arr(rsi_wilder(list(c), 2)),
            "r1": (c - pc) / atr,
            "clv": np.where(h > l, (c - l) / (h - l), 0.5),
            "streak": np.clip(streak, -5, 5),
            "d5": (c - arr(sma(list(c), 5))) / atr,
            "d50": (c - arr(sma(list(c), 50))) / atr,
            "vr": v / arr(sma(list(v), 50)),
            "r20": np.r_[[np.nan] * 20, c[20:] / c[:-20] - 1],
            "atrp": atr / c,
        }
        out = {
            "cc": np.r_[c[1:] / c[:-1] - 1, np.nan],
            "oc": np.r_[c[1:] / o[1:] - 1, np.nan],
        }
    f["vr"][~np.isfinite(f["vr"])] = np.nan
    f["r1"][0] = np.nan
    return f, out


def market_feats(spy, vix):
    """{日付: (S&P500のRSI(2), S&P500の今日の騰落率, VIX, S&P500の次の取引日の騰落率)}"""
    rs = rsi_wilder(spy["c"], 2)
    vx = dict(zip(vix["date"], vix["c"])) if vix else {}
    c, out = spy["c"], {}
    for i in range(1, len(c)):
        day = spy["date"][i]
        if rs[i] is None or day not in vx:
            continue
        out[day] = (rs[i], c[i] / c[i - 1] - 1, vx[day], c[i + 1] / c[i] - 1 if i + 1 < len(c) else np.nan)
    return out


def rows_for(d, mk, keep=lambda day: True, start="2015-01-01", last_only=False):
    """[(日付, 数値の列, 前日比, 寄り引け, SPYの翌日)]"""
    f, out = stock_feats(d)
    rng = [len(d["c"]) - 1] if last_only else range(260, len(d["c"]) - 1)
    res = []
    for i in rng:
        day = d["date"][i]
        if day < start or day not in mk or not keep(day):
            continue
        m = mk[day]
        x = [f[k][i] for k in KEYS[:9]] + [m[0], m[1], m[2]]
        if any(not np.isfinite(v) for v in x):
            continue
        res.append((day, x, out["cc"][i], out["oc"][i], m[3]))
    return res


# ---------- 点数（段階ごとのロジスティック回帰） ----------

def to_design(X, edges):
    cols = [np.ones(len(X))]
    for j, e in enumerate(edges):
        b = np.digitize(X[:, j], e)
        cols += [(b == k).astype(float) for k in range(1, len(e) + 1)]
    return np.column_stack(cols)


def fit(A, y, lam=10.0, it=25):
    w = np.zeros(A.shape[1])
    reg = lam * np.r_[0, np.ones(len(w) - 1)]
    for _ in range(it):
        p = 1 / (1 + np.exp(-A @ w))
        g = A.T @ (p - y) + reg * w
        H = (A * (p * (1 - p))[:, None]).T @ A + np.diag(reg)
        step = np.linalg.solve(H, g)
        w -= step
        if np.abs(step).max() < 1e-7:
            break
    return w


def auc(p, y):
    o = np.argsort(p, kind="mergesort")
    r = np.empty(len(p))
    r[o] = np.arange(1, len(p) + 1)
    n1 = y.sum()
    return (r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * (len(y) - n1))


def score(edges, lm, x):
    A = to_design(np.array([x], float), [np.array(e) for e in edges])
    return float(A[0] @ np.array(lm["w"]))


def contributions(edges, lm, x):
    """数値ごとの寄与（点数の上げ下げ。段階の重み。一番下の段階を0とする）"""
    out, pos = [], 1
    for j, e in enumerate(edges):
        b = int(np.digitize([x[j]], e)[0])
        out.append(lm["w"][pos + b - 1] if b >= 1 else 0.0)
        pos += len(e)
    return out


# ---------- バックテスト ----------

def build_dataset(cache):
    members, data = load_universe(cache, 260)
    mk = market_feats(load_prices(cache, "SPY"), load_prices(cache, "^VIX"))
    days, X, cc, oc, spyn, syms = [], [], [], [], [], []
    for sym, d in data.items():
        for day, x, a, b, s in rows_for(d, mk, keep=lambda day, sp=members[sym]: is_member(sp, day)):
            days.append(day); X.append(x); cc.append(a); oc.append(b); spyn.append(s); syms.append(sym)
    days = np.array(days)
    cc, oc, spyn = np.array(cc), np.array(oc), np.array(spyn)
    return days, np.array(X, float), {"cc": cc, "oc": oc, "rel": cc - spyn}, np.array(syms)


def watch_dataset(cache, mk):
    """監視銘柄（今の一覧、2022年以降）。今の時点で伸びたテーマを選んでいるため後知恵あり"""
    days, X, ret = [], [], {"cc": [], "oc": [], "rel": []}
    for sym in load_watchlist():
        d = load_prices(cache, sym)
        if not d:
            continue
        for day, x, a, b, s in rows_for(d, mk, start=VERIFY_START):
            days.append(day); X.append(x)
            ret["cc"].append(a); ret["oc"].append(b); ret["rel"].append(a - s)
    return np.array(days), np.array(X, float), {k: np.array(v) for k, v in ret.items()}


def pc(x, d=1):
    return f"{x * 100:.{d}f}%"


def bp(x):
    return f"{x * 1e4:+.1f}"


def cmd_backtest(a):
    days, X, rets, syms = build_dataset(a.cache)
    mk = market_feats(load_prices(a.cache, "SPY"), load_prices(a.cache, "^VIX"))
    wdays, wX, wrets = watch_dataset(a.cache, mk)
    ok = np.isfinite(rets["cc"]) & np.isfinite(rets["oc"])
    days, X, syms = days[ok], X[ok], syms[ok]
    rets = {k: v[ok] for k, v in rets.items()}
    wok = np.isfinite(wrets["cc"]) & np.isfinite(wrets["oc"])
    wdays, wX, wrets = wdays[wok], wX[wok], {k: v[wok] for k, v in wrets.items()}
    tr, te = days <= DESIGN_END, days >= VERIFY_START
    edges = [np.unique(np.percentile(X[tr, j], [20, 40, 60, 80])) for j in range(X.shape[1])]
    A = to_design(X, edges)
    wA = to_design(wX, edges)
    model = {"made": dt.date.today().isoformat(), "design": f"2015-01-01〜{DESIGN_END}", "verify_from": VERIFY_START,
             "verify_to": max(days[te].tolist()), "keys": KEYS, "edges": [e.tolist() for e in edges], "labels": {}}
    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: その日の上げ下げの確率（銘柄ごと）\n"
      f"updated: {dt.date.today().isoformat()}\n---\n")
    w("# その日の上げ下げの確率（銘柄ごと）— 過去の統計でどこまで当たるか\n")
    w(f"作成: `tools/daily_odds.py backtest`。S&P500（その日の構成銘柄）の日足 {len(days):,} 日分（銘柄×日）。"
      f"点数の作り方は **2015〜2021年（{tr.sum():,}）だけで決め**、**2022年〜{model['verify_to']}（{te.sum():,}）で確かめた**。"
      f"監視銘柄（今の{len(load_watchlist())}銘柄、2022年以降 {len(wdays):,}）は後知恵ありの参考。\n")
    w("使った数値（引け後に分かるもの、それぞれ5段階）: " + "・".join(n for _, n, _ in FEATS) + "\n")
    w("- 前日比: 次の取引日の終値 > 今日の終値（寄り付きの窓を含む。この通りには売買できない）\n"
      "- 寄り引け: 次の取引日の終値 > 始値（朝の結果を見て寄り付きで買い、引けで売る場合）\n"
      "- 対市場: 次の取引日の騰落率 > SPYの騰落率（市場全体の動きを除いた強さ）\n")
    for lab, name in LABELS:
        r = rets[lab]
        y = (r > 0).astype(float)
        wgt = fit(A[tr], y[tr])
        s = A @ wgt
        cuts = np.percentile(s[tr], np.arange(10, 100, 10))
        dec = np.digitize(s, cuts)
        wdec = np.digitize(wA @ wgt, cuts)
        wy = (wrets[lab] > 0).astype(float)
        calib = []
        for k in range(10):
            m = te & (dec == k)
            calib.append({"n": int(m.sum()), "up": float(y[m].mean()), "mean": float(r[m].mean()),
                          "model": float((1 / (1 + np.exp(-s[m]))).mean())})
        model["labels"][lab] = {"w": wgt.tolist(), "cuts": cuts.tolist(), "calib": calib,
                                "base": float(y[te].mean()), "auc_design": float(auc(s[tr], y[tr])), "auc_verify": float(auc(s[te], y[te]))}
        mm = model["labels"][lab]
        w(f"\n## {name}\n")
        w(f"- 上がった割合（全体）: 設計期間 {pc(y[tr].mean())}、確認期間 {pc(y[te].mean())}")
        w(f"- 当てる力（AUC、0.5=でたらめ、1.0=完全）: 設計期間 {mm['auc_design']:.3f}、確認期間 **{mm['auc_verify']:.3f}**\n")
        w("点数の順に10段階（段階の境目は設計期間で決めた。1=下がりやすい 〜 10=上がりやすい）。確認期間（2022年〜）の実績:\n")
        w("| 段階 | モデルの計算値 | 実際に上がった割合 | 次の日の平均（bp=0.01%） | 件数 | 監視銘柄: 上がった割合 | 監視銘柄: 平均 | 監視銘柄: 件数 |")
        w("|---|---|---|---|---|---|---|---|")
        for k, cb in enumerate(calib):
            wm = wdec == k
            w(f"| {k + 1} | {pc(cb['model'])} | {pc(cb['up'])} | {bp(cb['mean'])} | {cb['n']:,} | "
              f"{pc(wy[wm].mean()) if wm.any() else '—'} | {bp(wrets[lab][wm].mean()) if wm.any() else '—'} | {int(wm.sum()):,} |")
        # 年ごとの上位10%と下位10%の差
        w("\n年ごと（段階10と段階1の、上がった割合の差 / 平均の差）:\n")
        yrs = sorted({d[:4] for d in days[te]})
        parts = []
        for yr in yrs:
            m = te & np.char.startswith(days.astype(str), yr)
            hi, lo = m & (dec == 9), m & (dec == 0)
            parts.append(f"{yr}: {(y[hi].mean() - y[lo].mean()) * 100:+.1f}pt / {bp(r[hi].mean() - r[lo].mean())}bp")
        w("- " + "、".join(parts))
        if lab == "oc":
            hi = te & (dec == 9)
            net = r[hi] - 2 * COST
            w(f"\n売買の目安（寄り引け）: 段階10だけを寄り付きで買い引けで売ると、1回平均 {bp(r[hi].mean())}bp、"
              f"手数料・スプレッド（片道{COST * 100:.1f}%）を引くと **{bp(net.mean())}bp**、勝率（手数料後）{pc((net > 0).mean())}。")
    w("\n## まとめ（2026-09-30 の実行時に読み取ったもの。数値は上の表が正）\n")
    w("- 確認期間（2022年〜）の当てる力（AUC）: " + "、".join(f"{n} {model['labels'][k]['auc_verify']:.3f}" for k, n in LABELS)
      + "。0.5がでたらめなので、**どれもほぼ当たっていない**。設計期間（2015〜2021年）では少し効いていた"
      "（短期の逆張り: RSI(2)が低い・安値引け・連続下落・S&P500のRSI(2)が低いと、翌日は上がりやすい）が、2022年以降は消えた。")
    w("- 年ごとに見ると効いた年（2025年）と逆になった年（2022・2023・2026年）があり、安定しない。")
    w("- 寄り付きで買い引けで売る形は、上がりやすい段階でも手数料の前からマイナス。手数料を引くとさらに悪い。")
    w("- 監視銘柄（後知恵あり）でも同じで、段階の並びと実際の上がり方はそろわない。")
    json.dump(model, open(MODEL, "w"), ensure_ascii=False, indent=1)
    out = a.out or REPORT
    open(out, "w").write("\n".join(L) + "\n")
    print(out)
    print(MODEL)


# ---------- 今日の確率 ----------

def fetch_all(syms):
    from theme_scan import fetch_daily
    with ThreadPoolExecutor(8) as ex:
        return dict(zip(syms, ex.map(fetch_daily, syms)))


def open_day():
    """米国の取引時間中（16:10 ET まで）に実行したら、途中の今日の足を使わず前の取引日までにする"""
    from zoneinfo import ZoneInfo
    now = dt.datetime.now(ZoneInfo("America/New_York"))
    if now.weekday() < 5 and now.time() < dt.time(16, 10):
        return (now.date() - dt.timedelta(days=1)).isoformat()
    return None


def band(lm, s):
    return int(np.digitize([s], lm["cuts"])[0])


def cmd_today(a):
    if not os.path.exists(MODEL):
        sys.exit("点数の表がありません。先に tools/daily_odds.py backtest を実行してください")
    model = json.load(open(MODEL))
    wl = load_watchlist()
    syms = a.tickers.upper().split(",") if a.tickers else list(wl)
    from theme_scan import cut
    got = fetch_all(syms + ["SPY", "^VIX"])
    asof_cut = a.asof or open_day()
    spy, vix = cut(got.pop("SPY"), asof_cut), cut(got.pop("^VIX"), asof_cut)
    mk = market_feats(spy, vix)
    asof = spy["date"][-1]
    res, skipped = [], []
    for sym in syms:
        d = got.get(sym)
        d = cut(d, asof_cut) if d else None
        r = rows_for(d, mk, start="0000", last_only=True) if d and len(d["c"]) > 260 else []
        if not r or r[0][0] != asof:
            skipped.append(sym)
            continue
        x = r[0][1]
        row = {"sym": sym, "group": wl.get(sym, "—"), "x": x, "close": d["c"][-1]}
        for lab, _ in LABELS:
            lm = model["labels"][lab]
            b = band(lm, score(model["edges"], lm, x))
            row[lab] = (b, lm["calib"][b]["up"], lm["calib"][b]["n"])
        row["con"] = contributions(model["edges"], model["labels"]["cc"], x)
        res.append(row)
    res.sort(key=lambda r: (-r["cc"][0], -r["cc"][1], -r["rel"][0]))
    L = []
    w = L.append
    cc, oc, rel = (model["labels"][k] for k in ("cc", "oc", "rel"))
    w(f"# その日の上げ下げの確率（{asof} の引け → 次の取引日）\n")
    w(f"作成: `tools/daily_odds.py today`（{dt.datetime.now().strftime('%Y-%m-%d %H:%M')}）。数値と過去の統計だけで、売買の判断ではない。\n")
    w("## 読み方（先に読む）\n")
    w(f"- 確率は「{model['verify_from'][:4]}年以降に、同じくらいの点数（10段階）だった日に、実際に上がった割合」。"
      f"全体の平均は 前日比 {pc(cc['base'])}・寄り引け {pc(oc['base'])}・対市場 {pc(rel['base'])}。")
    w(f"- 当てる力は弱い（確認期間のAUC 前日比 {cc['auc_verify']:.3f}・寄り引け {oc['auc_verify']:.3f}・対市場 {rel['auc_verify']:.3f}。0.5がでたらめ）。"
      f"一番上がりやすい段階でも、前日比で上がったのは {pc(cc['calib'][9]['up'])}、一番下がりやすい段階でも {pc(cc['calib'][0]['up'])} は上がった。"
      "**1銘柄・1日の上げ下げはほぼ五分五分**で、差が出るのは多数の銘柄・日数を重ねたときだけ。")
    w("- 詳しい検証は `新分析ツール/バックテスト結果/その日の上げ下げの確率.md`。\n")
    w(f"## 市場全体（{asof}）\n")
    m = mk[asof]
    w(f"- S&P500のRSI(2) {m[0]:.0f}、今日の騰落率 {m[1]:+.1%}、VIX {m[2]:.1f}")
    w("- 個別銘柄の上げ下げの大部分は市場全体と一緒に動くため、下の「前日比」はどの銘柄も似た値になりやすい。銘柄の違いは「対市場」を見る。\n")
    w("## 銘柄ごと（前日比の上がる確率の高い順）\n")
    w("段階は1（下がりやすい）〜10（上がりやすい）。確率は上がる確率（下がる確率は 100% − これ）。\n")
    w("| 銘柄 | グループ | 終値 | 前日比: 段階 / 上がる確率 | 寄り引け: 段階 / 上がる確率 | 対市場: 段階 / 市場より強い確率 | 上げの理由 | 下げの理由 |")
    w("|---|---|---|---|---|---|---|---|")
    for r in res:
        order = np.argsort(r["con"])
        fmt = lambda j: f"{FEATS[j][1].split('（')[0]} {FEATS[j][2].format(r['x'][j])}"
        ups = [fmt(j) for j in order[::-1][:2] if r["con"][j] > 0.01]
        dns = [fmt(j) for j in order[:2] if r["con"][j] < -0.01]
        cell = lambda t: f"{t[0] + 1} / {pc(t[1])}"
        w(f"| {r['sym']} | {r['group']} | {r['close']:.2f} | {cell(r['cc'])} | {cell(r['oc'])} | {cell(r['rel'])} | "
          f"{'・'.join(ups) or '—'} | {'・'.join(dns) or '—'} |")
    if skipped:
        w(f"\n{asof} の日足を取得できなかった（または上場から1年未満の）銘柄: {', '.join(skipped)}")
    w("\n理由は前日比の点数への寄与の大きい順（2つまで）。数値の意味: " + "、".join(f"{n}" for _, n, _ in FEATS) + "。")
    open(a.out, "w").write("\n".join(L) + "\n")
    print(a.out)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("backtest")
    b.add_argument("--cache", default=DEFAULT_CACHE)
    b.add_argument("--out")
    t = sub.add_parser("today")
    t.add_argument("out")
    t.add_argument("--asof")
    t.add_argument("--tickers")
    a = ap.parse_args()
    cmd_backtest(a) if a.cmd == "backtest" else cmd_today(a)


if __name__ == "__main__":
    main()
