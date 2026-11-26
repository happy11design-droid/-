#!/usr/bin/env python3
"""静観（新しい買いを止める）の後、いつ買いを再開すると良かったかを、1996年〜の日足で比べる
（2026-11-23 ユーザーの質問「このまま買い続けても下げるだけだと思うけど、あなたの見解はどう？静観」→ 再開の合図の検証を提案 →「検証して」）

土台は tools/long_bear_test.py（今のルールを簡単にした形・今のS&P500と87銘柄の生き残りだけ・4枠・候補の25%を乱数で見送る×10通り）。
比べる相手は ① 今のツール（87銘柄＋テーマの外、87銘柄を先に。止めない）。
止める合図（その日の引けで判定し、その日の合図から買わない）:
  T1 特殊な下げ（毎朝のツールと同じ判定）が「なし」→「あり」になった日
  T2 SOXの終値が直近60取引日の最高値から−20%以下になった日（2022年のように特殊な下げにならない下げも入る）
再開の合図（止めた翌日から毎日の引けで判定し、その日の合図から買う）:
  end50 SOXが上向きの50日線を上回る（特殊な下げの終わりと同じ）／ ma20 SOXが20日線を上回る ／
  vix VIXが止めてからの最高値から−30%以下 ／ up15・up25 SOXが止めてからの最安値から+15%・+25% ／
  ftd SOXのフォロースルー（止めてからの最安値の日から4取引日以上たって、1日に+2%以上上げた日）／ d60 止めてから60取引日 ／
  off 止める合図の状態が終わる（T1: 特殊な下げが「なし」、T2: SOXが60取引日の最高値から−10%より上に戻る）
止める範囲: 全部（静観）／ 87銘柄だけ（テーマの外は買う）。持っている銘柄はルールどおり（売らない）。
使い方: python3 tools/long_resume_test.py run --trig T1|T2   → results/long_resume_<T>.json
        python3 tools/long_resume_test.py report [--out md]
"""
import argparse
import bisect
import datetime as dt
import json
import os
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import long_bear_test as lb

C = lb.C
RULES = [("end50", "SOXが上向きの50日線を上回る（特殊な下げの終わり）"), ("ma20", "SOXが20日線を上回る"), ("vix", "VIXが止めてからの最高値から−30%"),
         ("up15", "SOXが止めてからの安値から+15%"), ("up25", "SOXが止めてからの安値から+25%"), ("ftd", "SOXのフォロースルー（安値から4日目以降に+2%）"),
         ("d60", "止めてから60取引日"), ("off", "止める合図の状態が終わる")]
TRIG = {"T1": "特殊な下げになった日", "T2": "SOXが60取引日の高値から−20%になった日"}
SCOPE = {"all": "全部止める（静観）", "A": "87銘柄だけ止める（テーマの外は買う）"}


def series():
    sox = lb.sox_series()
    sx_d = sorted(sox)
    sx_c = [sox[d] for d in sx_d]
    vx = {r[0]: r[4] for r in json.load(open(lb.LS + "^VIX.json"))}
    return sx_d, sx_c, vx


def stop_periods(trig, rule, sx_d, sx_c, vx, SP):
    """[(止めた日, 再開した日 or None)]。止めた日の引けの合図から買わず、再開した日の引けの合図から買う"""
    n = len(sx_c)

    def state(k):
        if trig == "T1":
            return SP.get(sx_d[k], False)
        return k >= 59 and sx_c[k] / max(sx_c[k - 59:k + 1]) - 1 <= -0.20

    def off(k):
        if trig == "T1":
            return not SP.get(sx_d[k], False)
        return sx_c[k] / max(sx_c[k - 59:k + 1]) - 1 > -0.10
    out, k, prev = [], 320, state(319)
    while k < n:
        s_ = state(k)
        if s_ and not prev and sx_d[k] >= "1996-01-01":
            ks, lo, klo, vmax = k, sx_c[k], k, vx.get(sx_d[k], 0)
            j = k + 1
            res = None
            while j < n:
                c = sx_c[j]
                if c < lo:
                    lo, klo = c, j
                vmax = max(vmax, vx.get(sx_d[j], 0))
                m20 = sum(sx_c[j - 19:j + 1]) / 20
                m50, m50p = sum(sx_c[j - 49:j + 1]) / 50, sum(sx_c[j - 59:j - 9]) / 50
                ok = {"end50": c > m50 > m50p, "ma20": c > m20, "vix": vx.get(sx_d[j], 99) <= 0.7 * vmax,
                      "up15": c >= lo * 1.15, "up25": c >= lo * 1.25, "ftd": j - klo >= 4 and c / sx_c[j - 1] - 1 >= 0.02,
                      "d60": j - ks >= 60, "off": off(j)}[rule]
                if ok:
                    res = j
                    break
                j += 1
            out.append((sx_d[ks], sx_d[res] if res is not None else None))
            if res is None:
                break
            k = res + 1
            prev = state(res)   # 再開した後は、合図の状態がいったん終わって、また始まった日に止める（「なし」→「あり」の日だけ止める）
            continue
        prev = s_
        k += 1
    return out


def blocked_fn(periods):
    st_ = [a for a, _ in periods]
    en_ = [b or "9999" for _, b in periods]

    def f(d):
        i = bisect.bisect_right(st_, d) - 1
        return i >= 0 and d < en_[i]
    return f


def cmd_run(a):
    z = lb.build_trades()
    TA, TOut, days = z["TA"], z["TOut"], z["days"]
    di = {d: k for k, d in enumerate(days)}
    sx_d, sx_c, vx = series()
    SP = lb.special_days(sx_d, sx_c)
    forms = [("base", "① 今のツール（止めない）", None, [(0, t) for t in TA] + [(1, t) for t in TOut])]
    pers = {}
    for rk, rn in RULES:
        per = stop_periods(a.trig, rk, sx_d, sx_c, vx, SP)
        pers[rk] = per
        bl_ = blocked_fn(per)
        forms.append((f"{a.trig}_{rk}_all", f"{TRIG[a.trig]}に止め、{rn}で再開・{SCOPE['all']}", rk,
                      [(0, t) for t in TA if not bl_(t["sd"])] + [(1, t) for t in TOut if not bl_(t["sd"])]))
        forms.append((f"{a.trig}_{rk}_A", f"{TRIG[a.trig]}に止め、{rn}で再開・{SCOPE['A']}", rk,
                      [(0, t) for t in TA if not bl_(t["sd"])] + [(1, t) for t in TOut]))
    IDX = {k: lb.make_index(c) for k, _, _, c in forms}
    seeds = range(a.seeds)
    res = {"trig": a.trig, "days": [days[0], days[-1]], "periods": pers, "forms": {}}
    for k, nm, rk, _ in forms:
        curves = [lb.port(IDX[k], days, di, 9000 + q, days[0], days[-1], log_eq=True)[2] for q in seeds]
        # 資金は日ごとの中央値だけ残す（大きさを抑える）
        med_curve = [st.median(c[d] for c in curves) for d in days]
        res["forms"][k] = {"name": nm, "rule": rk, "curve_med": med_curve}
        print("資金", nm, file=sys.stderr, flush=True)
    WIN, STEP = 250, 10
    starts = list(range(0, len(days) - WIN, STEP))
    for k, nm, rk, _ in forms:
        res["forms"][k]["roll"] = [st.mean(lb.port(IDX[k], days, di, 7000 + q, days[j], days[j + WIN])[0] - 1 for q in seeds) for j in starts]
        print("1年の区切り", nm, file=sys.stderr, flush=True)
    res["roll_starts"] = [days[j] for j in starts]
    res["all_days"] = days
    os.makedirs(C + "results", exist_ok=True)
    json.dump(res, open(C + f"results/long_resume_{a.trig}.json", "w"), ensure_ascii=False)
    print("書き出し", file=sys.stderr)


def cmd_report(a):
    sx_d, sx_c, vx = series()
    sxm = dict(zip(sx_d, sx_c))
    SP = lb.special_days(sx_d, sx_c)
    R = {t: json.load(open(C + f"results/long_resume_{t}.json")) for t in ("T1", "T2")}
    days = R["T1"]["all_days"]
    di = {d: k for k, d in enumerate(days)}
    pc = lambda x: f"{x * 100:+.1f}%"
    med = lambda xs: st.median(xs) if xs else float("nan")

    def at(d):   # その日（なければ前の取引日）の位置
        return max(0, min(len(days) - 1, bisect.bisect_right(days, d) - 1))

    def span(f, lo, hi):
        c = f["curve_med"]
        a_, b_ = at(lo), at(hi)
        a_ = max(0, a_ - 1) if days[a_] >= lo else a_
        return c[b_] / c[a_] - 1

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
    base = R["T1"]["forms"]["base"]
    L = []
    w = L.append
    w("---\ntype: backtest\ntitle: 静観の後、いつ買いを再開すると良かったか（1996年〜）\ncreated: " + dt.date.today().isoformat()
      + "\nscript: tools/long_resume_test.py（土台は tools/long_bear_test.py）\n---\n")
    w("# 静観（新しい買いを止める）の後、いつ買いを再開すると良かったか（1996年〜）\n")
    w("2026-11-23、ユーザーの質問「このまま買い続けても下げるだけだと思うけど、あなたの見解はどう？静観」への回答で、再開の合図を1996年〜で比べると提案 →「検証して」。\n")
    w(f"- 土台は `長い下げの中で今のルールを確かめる（1996年〜）.md` と同じ（今のルールを簡単にした形、今のS&P500と87銘柄の生き残りだけ、4枠、候補の25%を乱数で見送る×10通り、{days[0]}〜{days[-1]}）。"
      "**生き残りの偏り**があり、87銘柄の昔の成績は良く出すぎる。")
    w("- 止める合図: T1＝特殊な下げになった日（毎朝のツールと同じ判定）、T2＝SOXが60取引日の高値から−20%になった日。止めた日の引けの合図から買わない。持っている銘柄はルールどおり。")
    w("- 再開の合図は止めた翌日から毎日の引けで判定し、その日の合図から買う。比べる相手は ① 止めない今のツール。\n")

    # 1. 止めた期間
    w("## 1. 止めた日と再開した日（主な下げ）\n")
    w("SOXの値動き: 「止めた日→再開の日」（マイナスなら止めている間に下げた＝避けた下げ）、「止めてからの安値→再開の日」（再開までに取り逃がした戻り）、「再開の日→1年後」。\n")
    focus = [("2000年", "2000-03-01", "2003-06-30"), ("2008年", "2007-07-01", "2009-12-31"), ("2022年", "2021-12-01", "2023-06-30"),
             ("2026年7月", "2026-06-01", "2026-10-15"), ("今回（2026年10月〜）", "2026-10-15", "9999")]
    for t in ("T1", "T2"):
        w(f"### {TRIG[t]}に止めた場合\n")
        w("| 再開の合図 | " + " | ".join(f[0] for f in focus) + " | 1996年〜で止めた回数・平均の日数 |")
        w("|---|" + "---|" * (len(focus) + 1))
        for rk, rn in RULES:
            per = R[t]["periods"][rk]
            cells = []
            for lab, lo, hi in focus:
                ps = [p for p in per if lo <= p[0] <= hi]
                if not ps:
                    cells.append("止めず")
                    continue
                txt = []
                for s0, e0 in ps[:3]:
                    k0 = sx_d.index(s0)
                    k1 = sx_d.index(e0) if e0 else len(sx_d) - 1
                    lo_ = min(sx_c[k0:k1 + 1])
                    a1 = sx_c[k1] / sx_c[k0] - 1
                    b1 = sx_c[k1] / lo_ - 1
                    k2 = min(len(sx_c) - 1, k1 + 250)
                    c1 = sx_c[k2] / sx_c[k1] - 1 if e0 and k1 + 250 < len(sx_c) else None
                    txt.append(f"{s0[2:]}→{(e0 or 'まだ')[2:] if e0 else 'まだ'}（{pc(a1)}・安値から{pc(b1)}" + (f"・1年後{pc(c1)}" if c1 is not None else "") + "）")
                if len(ps) > 3:
                    txt.append(f"ほか{len(ps) - 3}回")
                cells.append("<br>".join(txt))
            lens = []
            for s0, e0 in per:
                k0 = days.index(s0) if s0 in di else at(s0)
                k1 = di.get(e0, len(days) - 1) if e0 else len(days) - 1
                lens.append(k1 - k0)
            w(f"| {rn} | " + " | ".join(cells) + f" | {len(per)}回・{st.mean(lens):.0f}取引日 |")
        w("")

    # 2. 資金
    eps = [("2000-03〜2002-10", "2000-03-10", "2002-10-09"), ("2002-10の底→1年", "2002-10-09", "2003-10-09"), ("2006-01〜2008-11", "2006-01-27", "2008-11-20"),
           ("2008-11の底→1年", "2008-11-20", "2009-11-20"), ("2021-12〜2022-10", "2021-12-27", "2022-10-14"), ("2022-10の底→1年", "2022-10-14", "2023-10-13"),
           ("2026-07-07〜10-15", "2026-07-07", "2026-10-15"), ("今回 2026-10-16〜", "2026-10-16", days[-1])]
    w("## 2. 続けて運用した資金（乱数10通りの日ごとの中央値）\n")
    w("| 形 | 1996〜2014年 年率（最大下落率） | 2015年〜 年率（最大下落率） | " + " | ".join(e[0] for e in eps) + " |")
    w("|---|---|---|" + "---|" * len(eps))
    rows = [("T1", "base", base)] + [(t, k, f) for t in ("T1", "T2") for k, f in R[t]["forms"].items() if k != "base"]
    for t, k, f in rows:
        w(f"| {f['name']} | {pc(cagr(f, '1996-01-01', '2014-12-31'))}（{pc(mdd(f, '1996-01-01', '2014-12-31'))}） | {pc(cagr(f, '2015-01-01', '9999'))}（{pc(mdd(f, '2015-01-01', '9999'))}） | "
          + " | ".join(pc(span(f, lo, hi)) for _, lo, hi in eps) + " |")
    sxs = lambda lo, hi: (sxm[sx_d[max(0, bisect.bisect_left(sx_d, lo) - 1)]], sxm[sx_d[bisect.bisect_right(sx_d, hi) - 1]])
    w("| SOX指数 | | | " + " | ".join(pc(sxs(lo, hi)[1] / sxs(lo, hi)[0] - 1) for _, lo, hi in eps) + " |")

    # 3. 1年の区切り
    w("\n## 3. 1年の区切り（250取引日、10取引日ずつずらして空の枠から。乱数10通りの平均）で①と比べた差\n")
    w("差は1年の増減の平均の差（ポイント）。良・悪・同は、①より良かった・悪かった・同じだった区切りの数。\n")
    S = R["T1"]["roll_starts"]
    rb = base["roll"]
    groups = [("1996〜2014年に始めた", lambda d: d < "2015"), ("2015年〜に始めた", lambda d: d >= "2015"),
              ("2000〜2002年に始めた", lambda d: "2000-03-10" <= d <= "2002-10-09"), ("2007〜2009年に始めた", lambda d: "2007-07-01" <= d <= "2009-03-09")]
    w("| 形 | " + " | ".join(g[0] for g in groups) + " |")
    w("|---|" + "---|" * len(groups))
    summ = []
    for t, k, f in rows[1:]:
        cells = []
        sc = []
        for gl, gf in groups:
            ix = [j for j, d in enumerate(S) if gf(d)]
            df = [f["roll"][j] - rb[j] for j in ix]
            b = sum(x > 1e-9 for x in df)
            wv = sum(x < -1e-9 for x in df)
            cells.append(f"{st.mean(df) * 100:+.1f}pt（良{b}・悪{wv}・同{len(df) - b - wv}）")
            sc.append(st.mean(df))
        summ.append((f["name"], sc))
        w(f"| {f['name']} | " + " | ".join(cells) + " |")
    good = [nm for nm, sc in summ if sc[0] > 0 and sc[1] > 0]
    w("\n1996〜2014年と2015年〜の両方で①より平均が上だった形: " + ("、".join(good) if good else "**なし**") + "\n")

    # 4. 今の状態
    k = len(sx_c) - 1
    k0 = sx_d.index("2026-10-16")
    lo_ = min(sx_c[k0:k + 1])
    m20 = sum(sx_c[k - 19:k + 1]) / 20
    m50, m50p = sum(sx_c[k - 49:k + 1]) / 50, sum(sx_c[k - 59:k - 9]) / 50
    vmax = max(vx.get(d, 0) for d in sx_d[k0:k + 1])
    w(f"## 4. 今の状態（{sx_d[k]}の引け）\n")
    w(f"- SOX {sx_c[k]:,.2f}。20日線 {m20:,.0f}（{'上' if sx_c[k] > m20 else '下'}）、50日線 {m50:,.0f}（{'上向き' if m50 > m50p else '下向き'}、終値は{'上' if sx_c[k] > m50 else '下'}）。"
          f"10/16からの安値 {lo_:,.2f}（今は安値から {pc(sx_c[k] / lo_ - 1)}）。60取引日の高値から {pc(sx_c[k] / max(sx_c[k - 59:k + 1]) - 1)}。")
    w(f"- VIX {vx.get(sx_d[k]):.2f}（10/16からの最高値 {vmax:.2f}、そこから {pc(vx.get(sx_d[k]) / vmax - 1)}）。特殊な下げ: {'あり' if SP.get(sx_d[k]) else 'なし'}。")
    for t in ("T1", "T2"):
        st_ = []
        for rk, rn in RULES:
            per = R[t]["periods"][rk]
            last = per[-1] if per else None
            st_.append(f"{rn}: " + ("止めている（再開の合図はまだ）" if last and last[1] is None else f"再開済み（{last[1]}）" if last and last[1] >= "2026-10-01" else "止めていない"))
        w(f"- {TRIG[t]}に止めた場合: " + "／".join(st_))
    w("\n- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--trig", choices=("T1", "T2"), required=True)
    r.add_argument("--seeds", type=int, default=10)
    p = sub.add_parser("report")
    p.add_argument("--out", default="新分析ツール/バックテスト結果/実際の運用の期間の確認_2026-10-23/静観の後いつ買いを再開すると良かったか（1996年〜）.md")
    a = ap.parse_args()
    {"run": cmd_run, "report": cmd_report}[a.cmd](a)


if __name__ == "__main__":
    main()
