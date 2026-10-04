#!/usr/bin/env python3
"""個別株の2倍ETFの候補を、実際の株価で確かめて比べる（どのETFが資金の目減りが小さいか）

使い方:
  tools/leveraged_etf_check.py [--out FILE]

Yahoo Finance の直近1年の日足で、ETFごとに次を出す。
  名前（Yahooの正式名）、取引日数、1日平均の売買代金、元の株の値動きに対する倍率（回帰の傾き）・相関、
  目減り（年率）＝ ETFの実際の増え方 ÷「元の株の毎日の値動きの2倍」を毎日つないだ増え方。経費・借入コスト・ずれをまとめた差。
倍率が1.8〜2.2・相関0.95以上のものを「本物の2倍ETF」とし、同じ元の株の中で、目減りが小さく売買代金が十分（1日500万ドル以上）なものを勧める。
候補のティッカーはClaudeの知識によるもので、存在しないものはデータが取れずに外れる。
"""
import argparse
import datetime as dt
import json
import math
import os
import subprocess
import sys

CANDS = {
    "NVDA": ["NVDL", "NVDU", "NVDX", "NVDB"], "AVGO": ["AVL", "AVGU", "AVGG", "AVGX"], "MU": ["MUU", "MULL"],
    "AMD": ["AMDL", "AMUU", "AMDG"], "INTC": ["INTW", "LINT"], "ARM": ["ARMG"], "MRVL": ["MVLL", "MRVU"], "QCOM": ["QCMU"],
    "ASML": ["ASMG"], "SMCI": ["SMCX", "SMCL"], "DELL": ["DLLL"], "AAPL": ["AAPU", "AAPB", "AAPX"], "ANET": ["ANEL"],
    "VRT": ["VRTL"], "CEG": ["CEGX"], "VST": ["VSTL"], "GEV": ["GEVX"], "GOOGL": ["GGLL", "GOOX"], "MSFT": ["MSFU", "MSFL", "MSFX"],
    "META": ["METU", "FBL", "METX"], "AMZN": ["AMZU", "AMZZ", "AMZX"], "ORCL": ["ORCX", "ORCU"], "PLTR": ["PLTU", "PTIR", "PLTG"],
    "NBIS": ["NEBX", "NBIL"], "CRWV": ["CORW", "CWVX", "CRWG"], "TSLA": ["TSLL", "TSLR", "TSLT"], "APP": ["APPX"],
    "CRWD": ["CRWL", "CRWU"], "PANW": ["PALU"], "SHOP": ["SHPU"], "RDDT": ["RDTL", "RDTX"], "TSM": ["TSMX", "TSMU", "TSMG"],
    "COIN": ["CONL", "CONX"], "MSTR": ["MSTU", "MSTX"], "SNDK": ["SNXX", "SNDU"], "NOW": ["NOWL"], "CRM": ["CRMG"],
    "LITE": ["LITX"], "IBM": ["IBMX"], "ADBE": ["ADBG"], "HOOD": ["ROBN", "HOOG"], "NFLX": ["NFXL"], "UBER": ["UBRL"],
    "LLY": ["ELIL"], "BA": ["BOEU"],
}


def fetch(sym):
    p2 = int(dt.datetime.now().timestamp())
    p1 = p2 - 400 * 86400
    r = subprocess.run(["curl", "-sS", "--compressed", "--max-time", "30", "-A", "Mozilla/5.0",
                        f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d&period1={p1}&period2={p2}"], capture_output=True)
    try:
        res = json.loads(r.stdout.decode("utf-8", "replace"))["chart"]["result"][0]
    except (ValueError, KeyError, TypeError, IndexError):
        return None
    q = res["indicators"]["quote"][0]
    adj = (res["indicators"].get("adjclose") or [{}])[0].get("adjclose") or q["close"]
    out = {}
    for t, c, a, v in zip(res["timestamp"], q["close"], adj, q["volume"]):
        if c and a:
            out[dt.datetime.utcfromtimestamp(t).strftime("%Y-%m-%d")] = (a, c * (v or 0))
    return {"name": res["meta"].get("longName") or res["meta"].get("shortName") or "", "rows": out}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="新分析ツール/バックテスト結果/個別株2倍ETFの比べ方.md")
    a = ap.parse_args()
    L = []
    w = L.append
    w(f"---\ntype: research\ntitle: 個別株2倍ETFの比べ方\ncreated: {dt.date.today()}\nscript: tools/leveraged_etf_check.py\n---\n")
    w("# 個別株2倍ETFの比べ方（同じ元の株に複数あるとき、どれを買うか）\n")
    w(__doc__.split("\n", 5)[5].strip() + "\n")
    w("| 元の株 | ETF | 名前 | 日数 | 1日の売買代金 | 倍率 | 相関 | 目減り（年率） | 判定 |")
    w("|---|---|---|---|---|---|---|---|---|")
    best = {}
    for u, etfs in CANDS.items():
        ud = fetch(u)
        if not ud:
            continue
        rows = []
        for e in etfs:
            ed = fetch(e)
            if not ed or len(ed["rows"]) < 40:
                continue
            ds = sorted(set(ud["rows"]) & set(ed["rows"]))[-252:]
            if len(ds) < 40:
                continue
            ru = [ud["rows"][ds[i]][0] / ud["rows"][ds[i - 1]][0] - 1 for i in range(1, len(ds))]
            re_ = [ed["rows"][ds[i]][0] / ed["rows"][ds[i - 1]][0] - 1 for i in range(1, len(ds))]
            mu, me = sum(ru) / len(ru), sum(re_) / len(re_)
            cov = sum((x - mu) * (y - me) for x, y in zip(ru, re_))
            vu = sum((x - mu) ** 2 for x in ru)
            ve = sum((y - me) ** 2 for y in re_)
            beta = cov / vu if vu else 0
            corr = cov / math.sqrt(vu * ve) if vu and ve else 0
            ideal = math.prod(1 + 2 * x for x in ru)
            real = ed["rows"][ds[-1]][0] / ed["rows"][ds[0]][0]
            drag = (real / ideal) ** (252 / len(ru)) - 1 if ideal > 0 and real > 0 else float("nan")
            dv = sum(ed["rows"][d][1] for d in ds[-60:]) / min(60, len(ds))
            ok = 1.8 <= beta <= 2.2 and corr >= 0.95
            rows.append({"e": e, "name": ed["name"], "n": len(ds), "dv": dv, "beta": beta, "corr": corr, "drag": drag, "ok": ok})
            print(u, e, round(beta, 2), round(drag, 4), file=sys.stderr)
        good = [r for r in rows if r["ok"] and r["dv"] >= 5e6]
        pick = max(good, key=lambda r: (r["drag"], r["dv"])) if good else None
        if pick:
            best[u] = {"etf": pick["e"], "drag": round(pick["drag"], 4), "dollar_volume": round(pick["dv"])}
        for r in rows:
            mark = "**おすすめ**" if pick and r is pick else ("2倍ETF" if r["ok"] else "2倍ではない／別物")
            if r["ok"] and r["dv"] < 5e6:
                mark = "2倍ETF（売買が少ない）"
            w(f"| {u} | {r['e']} | {r['name'][:40]} | {r['n']} | {r['dv'] / 1e6:,.1f}百万ドル | {r['beta']:.2f} | {r['corr']:.2f} | {r['drag'] * 100:+.1f}% | {mark} |")
    w("\n## おすすめの一覧（元の株 → ETF）\n")
    w(", ".join(f"{u}→{x['etf']}" for u, x in best.items()) + "\n")
    w("- 目減りは、経費率・借入のコスト・毎日の合わせ直しのずれをまとめた、直近1年の実際の差。マイナスが小さいほど資金効率が良い。")
    w("- 売買代金が多いほど、買値と売値の差（スプレッド）が小さく、寄り付きで売買しても値段がずれにくい。")
    w("- ムームー証券で買えるかは、アプリで確かめる（取引可能な米国ETF一覧 https://www.moomoo.com/ja/quote/us-tradable-etf ）。")
    json.dump(best, open(os.path.join(os.path.dirname(a.out), "..", "2倍ETFの対応表.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("書き出し", a.out, file=sys.stderr)


if __name__ == "__main__":
    main()
