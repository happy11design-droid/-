#!/usr/bin/env python3
"""著者の本の「数値のはっきりしないルール」を加えた形と、効かなかったルールを現代風にアレンジした形のバックテスト

使い方:
  tools/backtest_modern.py run [--out FILE]

過去に合わせすぎないよう、期間を2つに分ける:
  設計期間 2015-01-02〜2021-12-31: この期間の成績だけを見て形を選ぶ
  確認期間 2022-01-01〜今: 選んだ形がこの期間でも効くかを確かめる（表の「前半 / 後半 年率」の後半）
対象: 後知恵なしの監視銘柄（毎週その時点の数値で選び直す）。新高値V2はそのうちRS上位10。

1. 今の採用ルールに加える候補（数値はClaudeが本の文章から置いたもの）
  ① RSライン: 株価÷S&P500 が、直近5日のうちに直前250日の最高値を上回った（オニール p.122、ミネルヴィニ）
  ② VCP（値幅と出来高の縮み）: 上抜けの前10日の値幅（高値−安値）がピボットの10%以内、その10日の平均出来高 ≦ 50日平均×0.85（ミネルヴィニ）
  ③ 利益が乗ったら損切りを引き上げる: 含み益が30%（損切り幅15%の2倍）になったら損切りを買値へ（ミネルヴィニ）／
     含み益が30%を超えたら、含み益の30%を失ったら売る（タープの利益の戻り p.〇 のルール表「2R到達後、含み益の30%減少」）
  ⑤ 同じ業種は同時に2銘柄まで（ミネルヴィニ・ワインスタイン）
  （④ 買い増しは、資金の計算の仕組みが1銘柄1回の売買を前提にしているため、今回は試していない）
2. 効かなかったルールの現代風のアレンジ
  ミネルヴィニのベース: ベースを2週（10日）以上・調整幅25%以内に、出来高を1.5倍に緩め、①②を加える。手じまいを20日線割れ・③に
  ワインスタイン: 週足を日足に置き換え（50日の高値の上抜け、50日線が上向き、出来高1.5倍）、①を加える
  オニール: 出来高1.2倍、ベース5週以上・調整幅25%以内、①を加える。損切りを値動きの大きさ（ATR14の3倍）に
"""
import argparse
import collections
import datetime as dt
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_compare2 as c2
import backtest_crash as bcr
import backtest_minervini2 as bm2
import backtest_oneil as bo
import backtest_rotation as br
import backtest_swing as bs
import backtest_trend as bt
from backtest_lib import COSTS, DEFAULT_CACHE, Reporter, gen_trades, load_prices, load_universe, portfolio
from backtest_regime import X_BELOW50, freq_table, srt

RISK, STOP, COST = 0.02, 0.15, COSTS[2]
IS_END, OOS_START = "2021-12-31", "2022-01-01"


class GroupReporter(Reporter):
    """同じ業種の同時保有を cap 銘柄までにして資金を計算する Reporter"""
    def __init__(self, *a, group_of=None, cap=None, **k):
        super().__init__(*a, **k)
        self.group_of, self.cap = group_of, cap

    def port(self, tr, stop, lo=None, hi=None, seed=None):
        lo, hi = lo or self.days[0], hi or self.days[-1]
        dd = [d for d in self.days if lo <= d <= hi]
        return portfolio([t for t in tr if lo <= t["in"] and t["out"] <= hi], self.cost, max(1, int(round(stop / self.risk, 6))),
                         dd, self.data, weight=self.risk / stop, seed=seed, group_of=self.group_of, group_cap=self.cap)


def prep(s, spx):
    c, h, l, n = s["c"], s["h"], s["l"], len(s["c"])
    tr = [h[0] - l[0]] + [max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1])) for i in range(1, n)]
    atr, a = [None] * n, None
    for i in range(n):
        a = tr[i] if a is None else (a * 13 + tr[i]) / 14
        atr[i] = a if i >= 14 else None
    s["atr"] = atr
    rsl = [c[i] / spx[d] if d in spx else None for i, d in enumerate(s["date"])]
    s["rsl"] = rsl
    hi, dq = [None] * n, collections.deque()
    for i in range(1, n):
        k = i - 1                      # 前日までの250日の最高値（当日と直近4日は ok_rsl で見る）
        if rsl[k] is not None:
            while dq and rsl[dq[-1]] <= rsl[k]:
                dq.pop()
            dq.append(k)
        while dq and dq[0] < i - 250:
            dq.popleft()
        hi[i] = rsl[dq[0]] if dq and i >= 250 else None
    s["rsl_hi"] = hi


# ---------- 条件 ----------
def ok_rsl(i, s):
    """① RSラインが直近5日のうちに、その前の250日の最高値を上回った"""
    ref = s["rsl_hi"][i - 4] if i >= 4 else None
    return ref is not None and any(x is not None and x > ref for x in s["rsl"][i - 4:i + 1])


def ok_vcp(i, s):
    """② 上抜けの前10日の値幅がピボットの10%以内、平均出来高 ≦ 50日平均×0.85"""
    kh = s["piv_i"][i]
    if kh is None or i < 11 or s["vol50"][i - 1] is None:
        return False
    piv = s["h"][kh]
    rng = max(s["h"][i - 10:i]) - min(s["l"][i - 10:i])
    return rng / piv <= 0.10 and sum(s["v"][i - 10:i]) / 10 <= 0.85 * s["vol50"][i - 1]


def with_(entry, *conds):
    return lambda i, s: entry(i, s) if all(f(i, s) for f in conds) else None


# ---------- 手じまい ----------
X_BELOW20 = lambda j, s, k, px: s["bb_mid"][j] is not None and s["c"][j] < s["bb_mid"][j]


def X_giveback(start=0.30, keep=0.70):
    """③ タープ: 含み益が start を超えた後、含み益の (1−keep) を失ったら売る"""
    def f(j, s, k, px):
        mx = max(s["c"][j - k + 1:j + 1])
        return mx >= px * (1 + start) and s["c"][j] <= px + keep * (mx - px)
    return f


def X_atr(mult=3.0):
    """損切りを値動きの大きさに合わせる: 引け値 ≦ 買値 − 買った日の前日のATR14×mult"""
    def f(j, s, k, px):
        a = s["atr"][j - k]
        return a is not None and s["c"][j] <= px - mult * a
    return f


def X_or(*fs):
    return lambda j, s, k, px: any(f(j, s, k, px) for f in fs)


# ---------- アレンジした買い ----------
def E_weinstein_daily(win=50, vol=1.5):
    """ワインスタインを日足に: 終値 > 直前 win 日の高値、50日線が20日前より上、終値 > 50日線、出来高 ≧ 50日平均×vol"""
    def f(i, s):
        if i < win + 1 or s["ma50"][i] is None or s["ma50"][i - 20] is None or s["vol50"][i] is None:
            return None
        if s["c"][i] <= max(s["h"][i - win:i]) or s["ma50"][i] <= s["ma50"][i - 20] or s["c"][i] <= s["ma50"][i]:
            return None
        if s["v"][i] < vol * s["vol50"][i]:
            return None
        return -(s["rs"][i] or 0)
    return f


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--out", default="新分析ツール/バックテスト結果/本のルールの追加と現代風のアレンジ.md")
    a = ap.parse_args()
    members, data = load_universe(a.cache, min_bars=260)
    g = load_prices(a.cache, "^GSPC")
    spx = dict(zip(g["date"], g["c"]))
    for sym, d in data.items():
        c2.prep(d)
        prep(d, spx)
        d["sym"] = sym
    bt.add_rs_rank(data, members)
    IDX = [load_prices(a.cache, k) for k in ("^GSPC", "^IXIC")]
    mk = bo.market_ok(IDX)
    allow_m = lambda d: mk.get(d, True)

    u = json.load(open(os.path.join(a.cache, "universe.json")))
    ex = os.path.join(a.cache, "industry_extra.json")
    if os.path.exists(ex):
        u.update(json.load(open(ex)))
    ind = {s: (u.get(s) or {}).get("industry") for s in data}
    spy = load_prices(a.cache, "SPY")
    end = dt.date.today().isoformat()
    start = "2015-01-02"
    days = [d for d in spy["date"] if start <= d <= end]
    fridays = [d for k, d in enumerate(days) if k + 1 == len(days) or dt.date.fromisoformat(days[k + 1]).isocalendar()[1] != dt.date.fromisoformat(d).isocalendar()[1]]
    lists = br.build_lists(data, members, fridays, ind)
    pos = {s: {d: k for k, d in enumerate(v["date"])} for s, v in data.items()}
    ranks = {}
    for f, lst in lists.items():
        rs = sorted(((data[s]["rs"][pos[s][f]] or 0, s) for s in lst if f in pos[s]), reverse=True)
        ranks[f] = {s: k + 1 for k, (_, s) in enumerate(rs)}
    week_of, fi, last = {}, 0, None
    for d in days:
        while fi < len(fridays) and fridays[fi] < d:
            last = fridays[fi]
            fi += 1
        week_of[d] = last

    def ok_rot(s, i, spans):
        wk = week_of.get(s["date"][i])
        return bt.liquid(s, i, spans) and wk is not None and s["sym"] in lists[wk]

    def ok_top10(s, i, spans):
        wk = week_of.get(s["date"][i])
        return bt.liquid(s, i, spans) and wk is not None and ranks[wk].get(s["sym"], 10 ** 9) <= 10

    halves = [("設計期間", start, IS_END), ("確認期間", OOS_START, end)]
    yrs = len(days) / 252
    L = []
    w = L.append
    rep = Reporter(w, data, days, halves, yrs, cost=COST, risk=RISK)
    G = lambda e, x, ok, stop=STOP, mh=500, allow=None, be=None: gen_trades(
        data, members, e, x, start, end, ok=ok, fill="open", max_hold=mh, stop_pct=stop, allow=allow, breakeven_at=be)

    w("---\ntype: backtest\ntitle: 本のルールの追加と現代風のアレンジ\n"
      f"created: {dt.date.today()}\nscript: tools/backtest_modern.py\n---\n")
    w("# 本のルールの追加と、効かなかったルールの現代風のアレンジ\n")
    w(__doc__.split("\n", 5)[5].strip() + "\n")
    w("建玉はすべて同じ（1銘柄に資金の13.3%、同時に7銘柄まで）。片道0.1%。表の「前半 / 後半」は設計期間 / 確認期間。"
      "**形は設計期間の成績で選び、確認期間の成績で本当に効くかを判断する。**\n")

    # ---------- 1. 今の採用ルールに加える ----------
    w("\n## 1. 今の採用ルールに加える候補\n")
    w("\n### 新高値V2（RS上位10）\n")
    rep.header("RSの高い順")
    V = {
        "今のルール": G(c2.V2, X_BELOW50, ok_top10),
        "＋① RSラインの新高値": G(with_(c2.V2, ok_rsl), X_BELOW50, ok_top10),
        "＋③ 含み益30%で損切りを買値へ": G(c2.V2, X_BELOW50, ok_top10, be=0.30),
        "＋③ 含み益30%の後、含み益の30%を失ったら売る": G(c2.V2, X_or(X_BELOW50, X_giveback()), ok_top10),
    }
    for k, t in V.items():
        rep.line(k, t, STOP)
    w("\n### ミネルヴィニのベースの上抜け（出来高2倍）\n")
    rep.header("RSの高い順")
    base2 = bm2.E_base(2.0)
    MB = {
        "今のルール": G(base2, X_BELOW50, ok_rot),
        "＋① RSラインの新高値": G(with_(base2, ok_rsl), X_BELOW50, ok_rot),
        "＋② VCP（値幅と出来高の縮み）": G(with_(base2, ok_vcp), X_BELOW50, ok_rot),
        "＋①②": G(with_(base2, ok_rsl, ok_vcp), X_BELOW50, ok_rot),
        "＋③ 含み益30%で損切りを買値へ": G(base2, X_BELOW50, ok_rot, be=0.30),
        "＋③ 含み益30%の後、含み益の30%を失ったら売る": G(base2, X_or(X_BELOW50, X_giveback()), ok_rot),
    }
    for k, t in MB.items():
        rep.line(k, t, STOP)
    w("\n### 急落の底（手じまいは5日線のまま。③の損切りの引き上げだけ）\n")
    rep.header("RSI(2)の低い順")
    K = {
        "今のルール": G(bcr.C3, c2.X_MA5, ok_rot, mh=60),
        "＋③ 含み益15%で損切りを買値へ": G(bcr.C3, c2.X_MA5, ok_rot, mh=60, be=0.15),
    }
    for k, t in K.items():
        rep.line(k, t, STOP)

    # ---------- 2. 現代風のアレンジ ----------
    w("\n## 2. 効かなかったルールの現代風のアレンジ\n")
    w("\n### ミネルヴィニのベースの上抜け\n")
    rep.header("RSの高い順")
    mod = bm2.E_base(1.5, depth=0.25, min_len=10)
    MM = {
        "今のルール（ベース3週以上・35%以内・出来高2倍・50日線割れ）": MB["今のルール"],
        "A ベース2週以上・25%以内・出来高1.5倍": G(mod, X_BELOW50, ok_rot),
        "B Aに②VCP": G(with_(mod, ok_vcp), X_BELOW50, ok_rot),
        "C Aに①RSライン": G(with_(mod, ok_rsl), X_BELOW50, ok_rot),
        "D Aに①②": G(with_(mod, ok_rsl, ok_vcp), X_BELOW50, ok_rot),
        "E Dを20日線割れで手じまい": G(with_(mod, ok_rsl, ok_vcp), X_BELOW20, ok_rot),
        "F Dに③含み益の戻りで売る": G(with_(mod, ok_rsl, ok_vcp), X_or(X_BELOW50, X_giveback()), ok_rot),
        "G Dに市場の方向（オニール）": G(with_(mod, ok_rsl, ok_vcp), X_BELOW50, ok_rot, allow=allow_m),
    }
    for k, t in MM.items():
        rep.line(k, t, STOP)
    w("\n### ワインスタイン\n")
    rep.header("RSの高い順")
    wd = E_weinstein_daily()
    WW = {
        "今のルール（週足・10週の高値の上抜け・出来高2倍・10週線割れ）": G(bt.E_weinstein(10, ma="10"), bt.X_weekly_below("10"), ok_rot),
        "A 日足（50日の高値の上抜け・50日線が上向き・出来高1.5倍）・50日線割れ": G(wd, X_BELOW50, ok_rot),
        "B Aに①RSライン": G(with_(wd, ok_rsl), X_BELOW50, ok_rot),
        "C Bを20日線割れで手じまい": G(with_(wd, ok_rsl), X_BELOW20, ok_rot),
        "D Bに③含み益の戻りで売る": G(with_(wd, ok_rsl), X_or(X_BELOW50, X_giveback()), ok_rot),
        "E Bを監視銘柄のRS上位10だけ": G(with_(wd, ok_rsl), X_BELOW50, ok_top10),
    }
    for k, t in WW.items():
        rep.line(k, t, STOP)
    w("\n### オニール\n")
    rep.header("RSの高い順")
    keep = dict(bo.P)
    oneil_book = G(bo.E_oneil, bo.X_oneil(), ok_rot, stop=bo.P["stop"], allow=allow_m)
    bo.P.update(vol=1.2, base_min=25, depth=0.25)
    OO = {
        "本のとおり（前回の結果）": oneil_book,
        "A 出来高1.2倍・ベース5週以上・25%以内": G(bo.E_oneil, bo.X_oneil(), ok_rot, stop=bo.P["stop"], allow=allow_m),
        "B Aに①RSライン": G(with_(bo.E_oneil, ok_rsl), bo.X_oneil(), ok_rot, stop=bo.P["stop"], allow=allow_m),
        "C Bの損切りをATR14×3に（上限15%）": G(with_(bo.E_oneil, ok_rsl), X_or(bo.X_oneil(), X_atr(3.0)), ok_rot, stop=STOP, allow=allow_m),
        "D Bの売りを50日線割れに（損切り15%）": G(with_(bo.E_oneil, ok_rsl), X_BELOW50, ok_rot, allow=allow_m),
        "E Dから市場の方向を外す": G(with_(bo.E_oneil, ok_rsl), X_BELOW50, ok_rot),
    }
    bo.P.clear()
    bo.P.update(keep)
    for k, t in OO.items():
        rep.line(k, t, STOP)

    # ---------- 3. 組み合わせ ----------
    w("\n## 3. 採用ルールの組み合わせ（7銘柄の枠を共有）\n")
    w("設計期間の年率で、各ルールの中から一番良かった形を選んで入れ替えた組み合わせも並べる（確認期間の成績は選ぶときに見ていない）。\n")
    b3 = bs.simulate(data, members, bs.O_method3, bs.X_upper_band, start, end, ok=ok_rot)
    w_ = []
    tmp = Reporter(w_.append, data, days, halves, yrs, cost=COST, risk=RISK)

    def is_cagr(tr):
        return tmp.med([tmp.port(tr, STOP, start, IS_END, seed=k)["cagr"] for k in tmp.SEEDS])

    pick = {}
    for name, grp in (("新高値V2", V), ("ミネルヴィニ", {**MB, **{k: v for k, v in MM.items() if not k.startswith("今")}}),
                      ("急落の底", K), ("ワインスタイン", WW), ("オニール", OO)):
        best = max(grp, key=lambda k: is_cagr(grp[k]))
        pick[name] = (best, grp[best])
    w("設計期間で選ばれた形: " + "、".join(f"{n}＝{b}" for n, (b, _) in pick.items()) + "\n")
    cur = srt(b3 + MB["今のルール"] + K["今のルール"] + V["今のルール"])
    combos = [
        ("今の採用ルール（ボリンジャーIII＋ミネルヴィニ＋急落の底＋新高値V2）", cur),
        ("設計期間で選んだ形に入れ替え（ボリンジャーIII＋ミネルヴィニ・急落の底・新高値V2を入れ替え）",
         srt(b3 + pick["ミネルヴィニ"][1] + pick["急落の底"][1] + pick["新高値V2"][1])),
        ("上に、ワインスタインのアレンジ（設計期間で選んだ形）を加える",
         srt(b3 + pick["ミネルヴィニ"][1] + pick["急落の底"][1] + pick["新高値V2"][1] + pick["ワインスタイン"][1])),
        ("上に、オニールのアレンジ（設計期間で選んだ形）を加える",
         srt(b3 + pick["ミネルヴィニ"][1] + pick["急落の底"][1] + pick["新高値V2"][1] + pick["ワインスタイン"][1] + pick["オニール"][1])),
    ]
    rep.header("RSの高い順")
    for k, t in combos:
        rep.line(k, t, STOP)
    w("\n**⑤ 同じ業種は同時に2銘柄まで**\n")
    grep_ = GroupReporter(w, data, days, halves, yrs, cost=COST, risk=RISK, group_of=ind, cap=2)
    grep_.header("RSの高い順")
    for k, t in combos[:2]:
        grep_.line(k + "・同じ業種は2銘柄まで", t, STOP)
    w("")
    freq_table(w, rep, combos, days, yrs)
    w("\n## 注意\n")
    w("- ①②③⑤の数値と、アレンジの数値はClaudeが本の文章から置いたもの（本に数値がない、または本の数値を変えたもの）。")
    w("- 業種は今のYahooの分類を過去にも使っている。NASDAQ100は含めていない。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"書き出し: {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
