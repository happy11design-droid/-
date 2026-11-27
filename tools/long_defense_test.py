#!/usr/bin/env python3
"""下げの間に「守り」（ディフェンシブ株・守りの業種ETF・現金）へ移る形を、1996年〜の日足で今のツールと比べる
（2026-11-27 ユーザーの質問「下落して機関投資家などのプロなど、ディフェンシブ銘柄に移行したりしてると思うが私達はそれにならわないのか？
…リセッションの懸念がある今、プロが行なっている取引に便乗すべきでは無いのか？」→ 検証を提案 →「はい検証して」）

土台は tools/long_bear_test.py（今のルールを簡単にした形・今のS&P500と87銘柄の生き残りだけ・4枠・候補の25%を乱数で見送る×10通り）。
守りに移る合図（その日の引けで判定し、次の取引日から）:
  SP 特殊な下げ（毎朝のツールと同じ判定）の間
  RC 景気後退の目安（tools/macro_dashboard.py の5つ）が2つ以上の間。発表の遅れを入れて、その日に分かっていた値だけで判定する
     （月次は翌月10日、新規失業保険は週の終わりの5日後、GDPは四半期の初めから4か月後、金利・社債の差はその日）
形（合図の間だけ。それ以外の日は ① と同じ）:
  ① 今のツール（87銘柄＋テーマの外。待っている現金は0%）
  ② 87銘柄を買わず、守りの3業種（生活必需品・ヘルスケア・公益。Yahoo の業種分類）の株を今の4つのルールで先に買う（テーマの外も買う）
  ③ 新しい買いを止め、待っている現金を守りの業種ETF（XLP・XLV・XLU を3分の1ずつ。1998-12 より前は現金）に置く
  ④ 新しい買いを止め、待っている現金を短期国債（^IRX の利回り）に置く
  ⑤ 新しい買いを止めるだけ（現金は0%）
持っている銘柄はルールどおり（売らない）。ETF・短期国債への出し入れは、合図の始まりと終わりに片道0.1%。
使い方: python3 tools/long_defense_test.py run --trig SP|RC → results/long_defense_<T>.json
        python3 tools/long_defense_test.py report [--out md]
"""
import argparse
import bisect
import csv
import datetime as dt
import json
import os
import random
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import long_bear_test as lb

C = lb.C
COST = lb.COST
DEF = {"Consumer Defensive", "Healthcare", "Utilities"}
TRIG = {"SP": "特殊な下げの間", "RC": "景気後退の目安が2つ以上の間"}
FORMS = [("base", "① 今のツール（止めない・現金は0%）"), ("def", "② 87銘柄の代わりに守りの3業種の株を4つのルールで買う"),
         ("etf", "③ 新しい買いを止め、現金を守りの業種ETF（XLP・XLV・XLU）に置く"), ("bill", "④ 新しい買いを止め、現金を短期国債に置く"),
         ("stop", "⑤ 新しい買いを止めるだけ（現金は0%）")]


def closes(sym):
    return {r[0]: r[4] for r in json.load(open(lb.LS + sym + ".json"))}


def adj(sym):
    return {r[0]: r[6] for r in json.load(open(lb.LS + sym + ".json"))}


def fred(sid):
    out = []
    for r in list(csv.reader(open(C + f"long/index/{sid}.csv")))[1:]:
        try:
            out.append((r[0], float(r[1])))
        except (ValueError, IndexError):
            pass
    return out


def recession_days(days):
    """{日付: 目安の数}（その日に分かっていた値だけ）"""
    def nxt_month(d, day):
        y, m = int(d[:4]), int(d[5:7]) + 1
        return f"{y + (m == 13):04d}-{(1 if m == 13 else m):02d}-{day:02d}"

    def add_days(d, n):
        return (dt.date.fromisoformat(d) + dt.timedelta(days=n)).isoformat()

    def add_months(d, n):
        y, m = int(d[:4]), int(d[5:7]) - 1 + n
        return f"{y + m // 12:04d}-{m % 12 + 1:02d}-01"
    sahm = [(nxt_month(d, 10), v) for d, v in fred("SAHMREALTIME")]
    gdp_raw = fred("GDPC1")
    gdp = [(add_months(gdp_raw[i][0], 4), (gdp_raw[i][1] / gdp_raw[i - 1][1]) ** 4 - 1) for i in range(1, len(gdp_raw))]
    ic = fred("ICSA")
    icsa = []
    for i in range(30, len(ic)):
        a4 = sum(v for _, v in ic[i - 3:i + 1]) / 4
        b4 = sum(v for _, v in ic[i - 29:i - 25]) / 4
        icsa.append((add_days(ic[i][0], 5), a4 / b4 - 1))
    t3 = fred("T10Y3M")
    baa = fred("BAA10Y")
    baa_ch = [(baa[i][0], baa[i][1] - baa[i - 63][1]) for i in range(63, len(baa))]

    def at(seq, d):
        k = bisect.bisect_right([x[0] for x in seq], d) - 1
        return seq[k][1] if k >= 0 else None
    keys = {n: [x[0] for x in s] for n, s in (("sahm", sahm), ("gdp", gdp), ("icsa", icsa), ("t3", t3), ("baa", baa_ch))}

    def at2(n, seq, d):
        k = bisect.bisect_right(keys[n], d) - 1
        return seq[k][1] if k >= 0 else None
    out = {}
    for d in days:
        s_, g_, i_, t_, b_ = at2("sahm", sahm, d), at2("gdp", gdp, d), at2("icsa", icsa, d), at2("t3", t3, d), at2("baa", baa_ch, d)
        out[d] = sum([s_ is not None and s_ >= 0.5, t_ is not None and t_ < 0, g_ is not None and g_ < 0,
                      i_ is not None and i_ >= 0.20, b_ is not None and b_ >= 0.5])
    return out


def port(by_in, days, di, seed, lo, hi, on=None, cash_ret=None, skip=0.25, log_eq=False):
    """lb.port と同じ。on（日付→合図の状態。前の取引日の引けの判定）の日は、待っている現金に cash_ret（日付→その日の倍率）を掛ける"""
    rnd = random.Random(seed)
    cash, held, pk, mdd = 1.0, [], 1.0, 0.0
    eqs, eq, prev_on = {}, 1.0, False
    for k in range(di[lo], di[hi] + 1):
        d = days[k]
        st_on = bool(on and k > 0 and on.get(days[k - 1]))
        if cash_ret is not None:
            if st_on != prev_on and cash > 0:
                cash *= 1 - COST   # 現金を ETF・短期国債に出し入れする
            if st_on and cash > 0:
                cash *= cash_ret.get(d, 1.0)
        prev_on = st_on
        still = []
        for h in held:
            v = h["t"]["path"].get(d)
            if v is not None:
                h["v"] = v
            if h["t"]["out"] == d:
                cash += h["size"] * h["v"]
            else:
                still.append(h)
        held = still
        eq = cash + sum(h["size"] * h["v"] for h in held)
        for p_, t in by_in.get(d, ()):
            if skip and rnd.random() < skip:
                continue
            if len(held) >= 4 or any(h["t"]["sym"] == t["sym"] for h in held):
                continue
            if t["ind"] and sum(1 for h in held if h["t"]["ind"] == t["ind"]) >= 2:
                continue
            size = min(eq / 4, cash)
            if size <= eq * 0.02:
                continue
            cash -= size
            v = t["path"].get(d, 1.0)
            h = {"t": t, "size": size, "v": v}
            if t["out"] == d:
                cash += size * v
            else:
                held.append(h)
        eq = cash + sum(h["size"] * h["v"] for h in held)
        pk = max(pk, eq)
        mdd = min(mdd, eq / pk - 1)
        if log_eq:
            eqs[d] = eq
    return eq, mdd, eqs


def cmd_run(a):
    z = lb.build_trades()
    TA, TO, TOut, days = z["TA"], z["TO"], z["TOut"], z["days"]
    di = {d: k for k, d in enumerate(days)}
    u = json.load(open(C + "universe.json"))
    if os.path.exists(C + "industry_extra.json"):
        u.update(json.load(open(C + "industry_extra.json")))
    sec = lambda s: (u.get(s) or {}).get("sector")
    TD = [t for t in TO if sec(t["sym"]) in DEF]
    if a.trig == "SP":
        sx = lb.sox_series()
        sx_d = sorted(sx)
        SPd = lb.special_days(sx_d, [sx[d] for d in sx_d])
        on = {d: bool(SPd.get(d)) for d in days}
    else:
        rc = recession_days(days)
        on = {d: rc[d] >= 2 for d in days}
    # 守りの業種ETF（3分の1ずつ、毎日つり合わせる近似）と短期国債（^IRX の年利 ÷ 252）の、その日の倍率（前の取引日の終値→その日の終値）
    E = [adj(s) for s in ("XLP", "XLV", "XLU")]
    irx = closes("^IRX")
    etf_r, bill_r = {}, {}
    for k in range(1, len(days)):
        d, p = days[k], days[k - 1]
        rs = [e[d] / e[p] for e in E if d in e and p in e]
        etf_r[d] = sum(rs) / len(rs) if len(rs) == 3 else 1.0
        y = irx.get(p)
        bill_r[d] = 1 + (y / 100 / 252 if y else 0.0)
    off = lambda t: not on.get(t["sd"], False)
    cand = {"base": [(0, t) for t in TA] + [(1, t) for t in TOut],
            "def": [(0, t) for t in TA if off(t)] + [(0, t) for t in TD if not off(t)] + [(1, t) for t in TOut],
            "etf": [(0, t) for t in TA if off(t)] + [(1, t) for t in TOut if off(t)],
            "bill": [(0, t) for t in TA if off(t)] + [(1, t) for t in TOut if off(t)],
            "stop": [(0, t) for t in TA if off(t)] + [(1, t) for t in TOut if off(t)]}
    cr = {"etf": etf_r, "bill": bill_r}
    IDX = {k: lb.make_index(v) for k, v in cand.items()}
    seeds = range(a.seeds)
    spans, cur = [], None
    for d in days:
        if on[d] and cur is None:
            cur = d
        elif not on[d] and cur is not None:
            spans.append((cur, d))
            cur = None
    if cur:
        spans.append((cur, None))
    res = {"trig": a.trig, "all_days": days, "spans": spans, "on_share": sum(on.values()) / len(days), "n_def": len({t["sym"] for t in TD}), "forms": {}}
    for k, nm in FORMS:
        o_ = on if k in ("etf", "bill") else None
        curves = [port(IDX[k], days, di, 9000 + q, days[0], days[-1], on=o_, cash_ret=cr.get(k), log_eq=True)[2] for q in seeds]
        res["forms"][k] = {"name": nm, "curve_med": [st.median(c[d] for c in curves) for d in days]}
        print("資金", nm, file=sys.stderr, flush=True)
    WIN, STEP = 250, 10
    starts = list(range(0, len(days) - WIN, STEP))
    for k, nm in FORMS:
        o_ = on if k in ("etf", "bill") else None
        res["forms"][k]["roll"] = [st.mean(port(IDX[k], days, di, 7000 + q, days[j], days[j + WIN], on=o_, cash_ret=cr.get(k))[0] - 1 for q in seeds) for j in starts]
        print("1年の区切り", nm, file=sys.stderr, flush=True)
    res["roll_starts"] = [days[j] for j in starts]
    json.dump(res, open(C + f"results/long_defense_{a.trig}.json", "w"), ensure_ascii=False)
    print("書き出し", file=sys.stderr)


def cmd_report(a):
    R = {t: json.load(open(C + f"results/long_defense_{t}.json")) for t in ("SP", "RC")}
    days = R["SP"]["all_days"]
    pc = lambda x: f"{x * 100:+.1f}%"

    def at(d):
        return max(0, min(len(days) - 1, bisect.bisect_right(days, d) - 1))

    def span(f, lo, hi):
        c = f["curve_med"]
        a_ = at(lo)
        a_ = max(0, a_ - 1) if days[a_] >= lo else a_
        return c[at(hi)] / c[a_] - 1

    def cagr(f, lo, hi):
        c = f["curve_med"]
        a_, b_ = max(0, at(lo) - 1), at(hi)
        y = (dt.date.fromisoformat(days[b_]) - dt.date.fromisoformat(days[a_])).days / 365.25
        return (c[b_] / c[a_]) ** (1 / y) - 1

    def mdd(f, lo, hi):
        c = f["curve_med"]
        pk, m = None, 0.0
        for k in range(at(lo), at(hi) + 1):
            pk = c[k] if pk is None else max(pk, c[k])
            m = min(m, c[k] / pk - 1)
        return m
    sox = lb.sox_series()
    sx_d = sorted(sox)
    spy = adj("SPY")
    defe = [adj(s) for s in ("XLP", "XLV", "XLU")]
    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: 下げの間に守り（ディフェンシブ株・守りの業種ETF・現金）へ移る形（1996年〜）\ncreated: " + dt.date.today().isoformat()
      + "\nscript: tools/long_defense_test.py（土台は tools/long_bear_test.py）\n---\n")
    w("# 下げの間に守り（ディフェンシブ株・守りの業種ETF・現金）へ移る形（1996年〜）\n")
    w("2026-11-27、ユーザーの質問「プロなど、ディフェンシブ銘柄に移行したりしてると思うが私達はそれにならわないのか？…リセッションの懸念がある今、プロが行なっている取引に便乗すべきでは無いのか？」"
      "への回答で、個別株のデータで確かめると提案 →「はい検証して」。\n")
    w(f"- 土台は `長い下げの中で今のルールを確かめる（1996年〜）.md` と同じ（今のルールを簡単にした形、今のS&P500と87銘柄の生き残りだけ、4枠、候補の25%を乱数で見送る×10通り、{days[0]}〜{days[-1]}）。"
      "**生き残りの偏り**があり、87銘柄の昔の成績は良く出すぎる。守りの3業種の株も今のS&P500の銘柄（その日に構成銘柄だった期間だけ）。")
    w(f"- 守りの3業種の株: Yahoo の業種分類で生活必需品・ヘルスケア・公益の {R['SP']['n_def']} 銘柄。新高値V2 は「87銘柄でないS&P500の中のRS上位10」の合図だけ（守りの株の中の上位10ではない）。")
    for t in ("SP", "RC"):
        sp_ = R[t]["spans"]
        w(f"- {TRIG[t]}だった日: 1996年〜の {R[t]['on_share'] * 100:.0f}%。期間: " + "、".join(f"{x}〜{y or '今も'}" for x, y in sp_[:25]) + (f" ほか{len(sp_) - 25}回" if len(sp_) > 25 else ""))
    w("")
    eps = [("2000-03〜2002-10", "2000-03-10", "2002-10-09"), ("2006-01〜2008-11", "2006-01-27", "2008-11-20"), ("2008-11の底→1年", "2008-11-20", "2009-11-20"),
           ("2021-12〜2022-10", "2021-12-27", "2022-10-14"), ("2026-07-07〜10-15", "2026-07-07", "2026-10-15"), ("今回 2026-10-16〜", "2026-10-16", days[-1])]
    w("## 1. 続けて運用した資金（乱数10通りの日ごとの中央値）\n")
    w("| 合図 | 形 | 1996〜2014年 年率（最大下落率） | 2015年〜 年率（最大下落率） | " + " | ".join(e[0] for e in eps) + " |")
    w("|---|---|---|---|" + "---|" * len(eps))
    for t in ("SP", "RC"):
        for k, nm in FORMS:
            if t == "RC" and k == "base":
                continue
            f = R[t]["forms"][k]
            w(f"| {'—' if k == 'base' else TRIG[t]} | {nm} | {pc(cagr(f, '1996-01-01', '2014-12-31'))}（{pc(mdd(f, '1996-01-01', '2014-12-31'))}） | "
              f"{pc(cagr(f, '2015-01-01', '9999'))}（{pc(mdd(f, '2015-01-01', '9999'))}） | " + " | ".join(pc(span(f, lo, hi)) for _, lo, hi in eps) + " |")

    def bret(px, lo, hi):
        ks = sorted(px)
        a_ = ks[max(0, bisect.bisect_left(ks, lo) - 1)]
        b_ = ks[bisect.bisect_right(ks, hi) - 1]
        return px[b_] / px[a_] - 1
    w("| 比べる相手 | SOX指数 | | | " + " | ".join(pc(bret(sox, lo, hi)) for _, lo, hi in eps) + " |")
    w("| 比べる相手 | SPY（配当込み） | | | " + " | ".join(pc(bret(spy, lo, hi)) for _, lo, hi in eps) + " |")
    w("| 比べる相手 | 守りの業種ETF（3分の1ずつ・配当込み） | | | " + " | ".join(
        pc(st.mean(bret(e, max(lo, "1998-12-23"), hi) for e in defe)) for _, lo, hi in eps) + " |")
    w("\n## 2. 1年の区切り（250取引日、10取引日ずつずらして空の枠から。乱数10通りの平均）で①と比べた差\n")
    w("差は1年の増減の平均の差（ポイント）。良・悪・同は、①より良かった・悪かった・同じだった区切りの数。\n")
    S = R["SP"]["roll_starts"]
    rb = R["SP"]["forms"]["base"]["roll"]
    groups = [("1996〜2014年に始めた", lambda d: d < "2015"), ("2015年〜に始めた", lambda d: d >= "2015"),
              ("2000〜2002年に始めた", lambda d: "2000-03-10" <= d <= "2002-10-09"), ("2007〜2009年に始めた", lambda d: "2007-07-01" <= d <= "2009-03-09")]
    w("| 合図 | 形 | " + " | ".join(g[0] for g in groups) + " |")
    w("|---|---|" + "---|" * len(groups))
    good = []
    for t in ("SP", "RC"):
        for k, nm in FORMS[1:]:
            f = R[t]["forms"][k]
            cells, sc = [], []
            for gl, gf in groups:
                ix = [j for j, d in enumerate(S) if gf(d)]
                df = [f["roll"][j] - rb[j] for j in ix]
                b = sum(x > 1e-9 for x in df)
                wv = sum(x < -1e-9 for x in df)
                cells.append(f"{st.mean(df) * 100:+.1f}pt（良{b}・悪{wv}・同{len(df) - b - wv}）")
                sc.append(st.mean(df))
            if sc[0] > 0 and sc[1] > 0:
                good.append(f"{TRIG[t]}・{nm}")
            w(f"| {TRIG[t]} | {nm} | " + " | ".join(cells) + " |")
    w("\n1996〜2014年と2015年〜の両方で①より平均が上だった形: " + ("、".join(good) if good else "**なし**") + "\n")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--trig", choices=("SP", "RC"), required=True)
    r.add_argument("--seeds", type=int, default=10)
    p = sub.add_parser("report")
    p.add_argument("--out", default="新分析ツール/バックテスト結果/実際の運用の期間の確認_2026-10-23/下げの間に守りへ移る形（1996年〜）.md")
    a = ap.parse_args()
    {"run": cmd_run, "report": cmd_report}[a.cmd](a)


if __name__ == "__main__":
    main()
