#!/usr/bin/env python3
"""相場天気予報の「景気後退・スタグフレーションの目安」の節を作る（FRED の公開データ。無料・APIキー不要。WebSearch を使わない）
（2026-11-23 ユーザーの質問「これだけ全体的に株価が下がっても利上げするのはまだ景気が良いから？リセッションやスタフグレーションなどの懸念はあるの？」
→ 毎朝の天気予報に数字で並べると提案 →「天気予報に追加して」）

並べる指標と、比べる相手（2000年5月＝ITバブルの崩壊の中でFRBが利上げした月、2008年9月＝リーマン・ショック）:
  物価: CPI・コアCPIの前年比、コアPCEの前年比（FRBの目標は2%）
  雇用: 失業率、サームの指標（失業率の3か月平均が直近12か月の最低から何ポイント上がったか。0.5以上が景気後退の目安）、
        雇用者数の3か月平均の増減、新規失業保険の申請（4週平均と半年前との比）
  景気: 実質GDP（前期比年率）、鉱工業生産の前年比、小売売上高の前年比（物価の分を引いた実質）
  金利・信用: 政策金利の上限、長短金利差（10年−3か月・10年−2年。マイナス＝逆転は景気後退の前触れとされる）、社債の利回り差（Baa−10年国債）
  心理: ミシガン大学の消費者心理
景気後退の目安（5つ）とスタグフレーションの目安は、よく使われる目安を Claude が選んで置いたもの（予測の確かさは確かめていない）。
取ったデータは ~/.cache/stock_backtest/long/index/<系列>.csv に置き、12時間以内に取ったものはそれを使う。
使い方: python3 tools/macro_dashboard.py [--front]   --front: レポートの先頭（frontmatter）に足す2行も出す
"""
import argparse
import bisect
import csv
import datetime as dt
import io
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

CACHE = os.path.expanduser("~/.cache/stock_backtest/long/index/")
SERIES = ["CPIAUCSL", "CPILFESL", "PCEPILFE", "UNRATE", "SAHMREALTIME", "PAYEMS", "ICSA", "GDPC1", "INDPRO", "RSAFS",
          "DFEDTARU", "DFEDTAR", "T10Y3M", "T10Y2Y", "BAA10Y", "UMCSENT"]
COMPARE = [("2000年5月", "2000-05-31"), ("2008年9月", "2008-09-30")]


def fetch(sid):
    p = CACHE + sid + ".csv"
    if os.path.exists(p) and time.time() - os.path.getmtime(p) < 12 * 3600:
        txt = open(p).read()
    else:
        txt = ""
        for i in range(3):   # FRED は User-Agent や圧縮を付けると途中で切ることがある（theme_scan.fred_monthly と同じ取り方）
            r = subprocess.run(["curl", "-sS", "--max-time", "60", f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}"],
                               capture_output=True, text=True)
            if r.returncode == 0 and r.stdout.startswith(("observation_date", "DATE")):
                txt = r.stdout
                break
            time.sleep(2 * (i + 1))
        if txt:
            os.makedirs(CACHE, exist_ok=True)
            open(p, "w").write(txt)
        elif os.path.exists(p):   # 取れなければ古いキャッシュ
            txt = open(p).read()
    out = []
    for r in list(csv.reader(io.StringIO(txt)))[1:]:
        try:
            out.append((r[0], float(r[1])))
        except (ValueError, IndexError):
            pass
    return out


def upto(s, d):
    """d 以前の観測"""
    k = bisect.bisect_right([x[0] for x in s], d)
    return s[:k]


def metrics(S, d):
    """日付 d の時点（その日までの観測）での指標。取れないものは None"""
    m = {}

    def last(sid):
        x = upto(S.get(sid, []), d)
        return x[-1] if x else None

    def yoy(sid, back=0):
        x = upto(S.get(sid, []), d)
        if len(x) < 13 + back:
            return None, None
        i = len(x) - 1 - back
        return x[i][1] / x[i - 12][1] - 1, x[i][0]
    m["cpi"], m["cpi_d"] = yoy("CPIAUCSL")
    m["cpi3"], _ = yoy("CPIAUCSL", 3)
    m["core"], m["core_d"] = yoy("CPILFESL")
    m["pce"], m["pce_d"] = yoy("PCEPILFE")
    u = last("UNRATE")
    m["un"], m["un_d"] = (u[1], u[0]) if u else (None, None)
    x = upto(S.get("UNRATE", []), d)
    m["un_min12"] = min(v for _, v in x[-13:]) if len(x) >= 13 else None
    s_ = last("SAHMREALTIME")
    m["sahm"], m["sahm_d"] = (s_[1], s_[0]) if s_ else (None, None)
    x = upto(S.get("PAYEMS", []), d)
    m["pay3"], m["pay_d"] = ((x[-1][1] - x[-4][1]) / 3, x[-1][0]) if len(x) >= 4 else (None, None)
    x = upto(S.get("ICSA", []), d)
    if len(x) >= 30:
        a4 = sum(v for _, v in x[-4:]) / 4
        b4 = sum(v for _, v in x[-30:-26]) / 4
        m["icsa"], m["icsa_ch"], m["icsa_d"] = a4, a4 / b4 - 1, x[-1][0]
    else:
        m["icsa"] = m["icsa_ch"] = m["icsa_d"] = None
    x = upto(S.get("GDPC1", []), d)
    m["gdp"], m["gdp_d"] = (((x[-1][1] / x[-2][1]) ** 4 - 1), x[-1][0]) if len(x) >= 2 else (None, None)
    m["ip"], m["ip_d"] = yoy("INDPRO")
    rs, rs_d = yoy("RSAFS")
    cpi_same = None
    if rs_d:
        xc = upto(S.get("CPIAUCSL", []), rs_d)
        if len(xc) >= 13 and xc[-1][0] == rs_d:
            cpi_same = xc[-1][1] / xc[-13][1] - 1
    m["retail"], m["retail_d"] = (rs - cpi_same, rs_d) if rs is not None and cpi_same is not None else (None, None)
    f = last("DFEDTARU") if d >= "2008-12-16" else last("DFEDTAR")
    m["ff"], m["ff_d"] = (f[1], f[0]) if f else (None, None)
    for k_, sid in (("c3m", "T10Y3M"), ("c2y", "T10Y2Y"), ("baa", "BAA10Y")):
        x = upto(S.get(sid, []), d)
        if d[:7] != dt.date.today().isoformat()[:7] and x:   # 比べる相手の月は、その月の平均
            mon = [v for t, v in x if t[:7] == d[:7]]
            m[k_], m[k_ + "_d"] = (sum(mon) / len(mon), d[:7]) if mon else (None, None)
        else:
            m[k_], m[k_ + "_d"] = (x[-1][1], x[-1][0]) if x else (None, None)
    x = upto(S.get("BAA10Y", []), d)
    m["baa_ch"] = x[-1][1] - x[-64][1] if len(x) >= 64 else None
    um = last("UMCSENT")
    m["um"], m["um_d"] = (um[1], um[0]) if um else (None, None)
    allum = S.get("UMCSENT", [])
    m["um_min"] = min(allum, key=lambda z: z[1]) if allum else None
    # 景気後退の目安（5つ）
    chk = [("サームの指標が0.5以上", m["sahm"] is not None and m["sahm"] >= 0.5),
           ("長短金利差（10年−3か月）が逆転（マイナス）", m["c3m"] is not None and m["c3m"] < 0),
           ("実質GDPが前期比マイナス", m["gdp"] is not None and m["gdp"] < 0),
           ("新規失業保険の4週平均が半年前より+20%以上", m["icsa_ch"] is not None and m["icsa_ch"] >= 0.20),
           ("社債の利回り差（Baa−10年）が3か月で+0.5ポイント以上広がった", m["baa_ch"] is not None and m["baa_ch"] >= 0.5)]
    m["chk"] = chk
    m["infl"] = m["cpi"] is not None and m["cpi3"] is not None and m["cpi"] >= 0.035 and m["cpi"] > m["cpi3"]
    m["weak"] = [lab for lab, ok in (("サームの指標0.5以上", chk[0][1]), ("実質GDPマイナス", chk[2][1]),
                                      ("実質の小売売上高が前年比マイナス", m["retail"] is not None and m["retail"] < 0),
                                      ("鉱工業生産が前年比マイナス", m["ip"] is not None and m["ip"] < 0)) if ok]
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--front", action="store_true")
    a = ap.parse_args()
    with ThreadPoolExecutor(4) as ex:
        S = dict(zip(SERIES, ex.map(fetch, SERIES)))
    miss = [k for k, v in S.items() if not v and k != "DFEDTAR"]
    today = dt.date.today().isoformat()
    now = metrics(S, today)
    old = [(lab, metrics(S, d)) for lab, d in COMPARE]
    pc = lambda x, nd=1: "取得不可" if x is None else f"{x * 100:+.{nd}f}%".replace("+", "") if x >= 0 else f"{x * 100:.{nd}f}%"
    pcs = lambda x, nd=1: "取得不可" if x is None else f"{x * 100:+.{nd}f}%"
    num = lambda x, f="{:.2f}": "取得不可" if x is None else f.format(x)
    mo = lambda d_: "" if not d_ else f"（{d_[:7].replace('-', '/')}）" if len(d_) >= 7 else ""
    dy = lambda d_: "" if not d_ else f"（{d_[5:].replace('-', '/')}）"
    rows = [
        ("CPI 前年比", lambda m: pc(m["cpi"]) + (f"（3か月前 {pc(m['cpi3'])}）" if m is now else ""), mo(now["cpi_d"]), "FRBの目標は2%"),
        ("コアCPI 前年比", lambda m: pc(m["core"]), mo(now["core_d"]), ""),
        ("コアPCE 前年比", lambda m: pc(m["pce"]), mo(now["pce_d"]), "FRBが重く見る物価"),
        ("失業率", lambda m: num(m["un"], "{:.1f}%") + (f"（直近12か月の最低 {m['un_min12']:.1f}%）" if m is now and m["un_min12"] else ""), mo(now["un_d"]), ""),
        ("サームの指標", lambda m: num(m["sahm"]), mo(now["sahm_d"]), "0.5以上で景気後退の目安"),
        ("雇用者数の増減（3か月平均）", lambda m: "取得不可" if m["pay3"] is None else f"{m['pay3']:+.0f}千人/月", mo(now["pay_d"]), "10万人未満で弱い"),
        ("新規失業保険の申請（4週平均・半年前との比）", lambda m: "取得不可" if m["icsa"] is None else f"{m['icsa'] / 1000:.0f}千件（{pcs(m['icsa_ch'], 0)}）", dy(now["icsa_d"]), "+20%以上で悪化の目安"),
        ("実質GDP（前期比年率）", lambda m: pcs(m["gdp"]), "" if not now["gdp_d"] else f"（{now['gdp_d'][:4]}年{(int(now['gdp_d'][5:7]) - 1) // 3 + 1}Q）", "マイナスで景気後退の目安"),
        ("鉱工業生産 前年比", lambda m: pcs(m["ip"]), mo(now["ip_d"]), ""),
        ("小売売上高 前年比（物価の分を引いた実質）", lambda m: pcs(m["retail"]), mo(now["retail_d"]), "マイナスで消費が弱い"),
        ("政策金利（上限）", lambda m: num(m["ff"], "{:.2f}%"), dy(now["ff_d"]), ""),
        ("長短金利差（10年−3か月）", lambda m: num(m["c3m"], "{:+.2f}"), dy(now["c3m_d"]), "マイナス（逆転）は景気後退の前触れ"),
        ("長短金利差（10年−2年）", lambda m: num(m["c2y"], "{:+.2f}"), dy(now["c2y_d"]), ""),
        ("社債の利回り差（Baa−10年国債）", lambda m: num(m["baa"], "{:.2f}%") + (f"（3か月で {m['baa_ch']:+.2f}）" if m is now and m["baa_ch"] is not None else ""), dy(now["baa_d"]), "広がると信用の悪化"),
        ("消費者心理（ミシガン大学）", lambda m: num(m["um"], "{:.1f}"), mo(now["um_d"]), "" if not now["um_min"] else f"1952年以降の最低 {now['um_min'][1]:.1f}（{now['um_min'][0][:7]}）"),
    ]
    L = []
    w = L.append
    nch = sum(ok for _, ok in now["chk"])
    if a.front:
        w(f"recession_signals: {nch}")
        w(f"stagflation: {'あり' if now['infl'] and now['weak'] else '物価だけ' if now['infl'] else '景気の弱さだけ' if now['weak'] else 'なし'}")
        w("")
    w("## 景気後退・スタグフレーションの目安（FREDの公開データ。プログラム（tools/macro_dashboard.py）が自動で取得）")
    w("")
    w("| 指標 | 今 | 目安 | " + " | ".join(lab for lab, _ in COMPARE) + " |")
    w("|---|---|---|" + "---|" * len(COMPARE))
    for lab, fn, when, note in rows:
        w(f"| {lab}{when} | {fn(now)} | {note} | " + " | ".join(fn(m) for _, m in old) + " |")
    w("")
    w(f"- **景気後退の目安: {nch}/5**（" + "、".join(f"{lab} {'●' if ok else '・'}" for lab, ok in now["chk"]) + "）。"
      + "比べる相手: " + "、".join(f"{lab} {sum(ok for _, ok in m['chk'])}/5" for lab, m in old)
      + f"（2000年5月は{sum(ok for _, ok in old[0][1]['chk'])}/5で、10か月後の2001年3月に景気後退に入った。目安が少ないことは、景気後退が来ないことを意味しない）")
    if now["infl"] and now["weak"]:
        st_ = f"あり**（物価が高く上がっている＋景気の弱さ: {'・'.join(now['weak'])}）"
    elif now["infl"]:
        st_ = "物価だけ**（物価は高く上がっているが、景気の弱さの目安（サームの指標・実質GDP・実質の小売・鉱工業生産のマイナス）はまだ出ていない）"
    elif now["weak"]:
        st_ = f"景気の弱さだけ**（{'・'.join(now['weak'])}）"
    else:
        st_ = "なし**"
    w(f"- **スタグフレーションの目安: {st_}。物価の条件＝CPI前年比3.5%以上で3か月前より上（{pc(now['cpi'])}、3か月前 {pc(now['cpi3'])}）。")
    w("- 目安はよく使われるものを Claude が選んで置いたもので、当たる確かさは確かめていない。数字は発表済みの最新値（月次・四半期は1〜2か月遅れ）。"
      "比べる相手は、その月（GDPはその月を含む四半期）の後から発表された値で、金利・社債の差はその月の平均。" + (f"取得できなかった系列: {'・'.join(miss)}。" if miss else ""))
    print("\n".join(L))


if __name__ == "__main__":
    main()
