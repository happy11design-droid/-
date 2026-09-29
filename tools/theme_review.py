#!/usr/bin/env python3
"""テーマ監視の運用記録と週次レビュー（`新分析ツール/テーマ監視_手順書.md` 手順T5・週次レビュー）

使い方:
  tools/theme_review.py record <作業ディレクトリ>
      毎朝の scan.md と著者の回答（answers/*.txt）から、候補・保有銘柄と著者の結論を record.json に書き出す（tools/theme_daily.sh send が呼ぶ）。
  tools/theme_review.py review <record.json を置いたディレクトリ> [--since YYYY-MM-DD] [--out FILE]
      記録した候補を、採用したルールどおりに売買していたらどうなったか（翌日の寄り付きで買い、損切り15%の逆指値、ルールの手じまい条件）を
      最新の株価で計算し、著者の結論（【買い】【買い（予約）】【様子見】、2026-09-27以前は【注文する】【見送る】）ごとに集計する。
      予約注文（パターンB）は、ユーザーが実際に約定した記録（保有銘柄.md・売買記録.md）があるときだけ数える（価格が届いただけでは数えない）。保有銘柄の【売り】は、ルールどおり持ち続けた場合と比べる。
計算は数値の事実だけで、Claudeの売買判断は含まない。
"""
import argparse
import datetime as dt
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_swing as bs
import backtest_trend as bt
from theme_scan import fetch_daily, load_trades

STOP, COST = 0.15, 0.001
CAPITAL = 18000   # 運用開始時の資金（ドル、2026-09-29 ユーザー）。4節の資金の増減と最大下落率の基準
TOOLS = os.path.dirname(os.path.abspath(__file__))
# バックテストの見込み（4銘柄・1銘柄25%・損切り15%・急落の底RSI(2)≦10、後知恵なしの監視銘柄 2015年〜。
# `バックテスト結果/銘柄数と損切りの組み合わせ.md`・`ユーザーの売買の仕方とペトラリア氏の手じまい.md`）
EXPECT = {"cagr": (0.10, 0.20, 0.216), "win": 0.62, "avg": 0.018, "mdd": 0.33, "mdd_worst": 0.37, "per_year": 35, "hold": 26}
MIN_N = 20   # これより少ない件数では、勝率・平均は比べない


# ---------- 記録 ----------

def table_rows(text, head):
    i = text.find(head)
    if i < 0:
        return []
    j = text.find("\n## ", i + 1)
    rows, cols = [], None
    for line in text[i:j if j > 0 else len(text)].splitlines():
        if line.startswith("| 銘柄 |"):
            cols = [c.strip() for c in line.strip("|").split("|")]
        elif cols and re.match(r"^\| [A-Z]", line):
            rows.append(dict(zip(cols, [c.strip() for c in line.strip("|").split("|")])))
    return rows


def verdicts(d):
    """answers/1_<著者>_prompt_n.txt から {(銘柄, 保有中か): (結論, 著者)}"""
    out = {}
    for f in sorted(glob.glob(os.path.join(d, "answers", "1_*.txt"))):
        author = os.path.basename(f).split("_")[1]
        sym, hold = None, False
        for line in open(f, encoding="utf-8"):
            m = re.match(r"^##\s*([A-Z][A-Z.]*)", line)
            if m:
                sym, hold = m.group(1), "保有" in line
                continue
            m = re.search(r"(?:結論|投資判断).*?【([^】]+)】", line)
            if sym and m and (sym, hold) not in out:
                out[(sym, hold)] = (m.group(1), author)
    return out


def cmd_record(a):
    d = a.dir
    scan = open(os.path.join(d, "scan.md"), encoding="utf-8").read()
    trade_date = re.search(r"（(\d{4}-\d{2}-\d{2})の引け時点）", scan).group(1)
    v = verdicts(d)
    stage = ""
    f0 = glob.glob(os.path.join(d, "answers", "0_*.txt"))
    if f0:
        for line in open(f0[0], encoding="utf-8"):
            if "テーマ全体の局面" in line:
                stage = re.sub(r"^\s*\d+\.\s*|テーマ全体の局面[:：]\s*", "", line.replace("*", "")).strip()
                break
    cands = []
    for r in table_rows(scan, "## 6."):
        od = r.get("注文の目安", "")
        lim = re.search(r"寄り付きが([0-9.]+)（ピボット", od) or re.search(r"指値の上限 ([0-9.]+)", od)
        stp = re.search(r"逆指値買い ([0-9.]+)", od)
        lmt = re.search(r"(?<!逆)指値買い ([0-9.]+)", od)
        vv = v.get((r["銘柄"], False), ("未判定", ""))
        cands.append({"sym": r["銘柄"], "kind": r["種類"], "pattern": r.get("パターン", "A"), "close": float(r["終値"]),
                      "limit": float(lim.group(1)) if lim else None,
                      "stop_buy": float(stp.group(1)) if stp else None, "limit_buy": float(lmt.group(1)) if lmt else None,
                      "verdict": vv[0], "author": vv[1]})
    holds = []
    for r in table_rows(scan, "## 5."):
        vv = v.get((r["銘柄"], True), ("未判定", ""))
        holds.append({"sym": r["銘柄"], "rule": r["ルール"], "buy_date": r["買った日"], "buy_price": float(r["買値"]),
                      "verdict": vv[0], "author": vv[1]})
    rec = {"trade_date": trade_date, "run_date": dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).date().isoformat(),
           "theme_stage": stage, "candidates": cands, "holdings": holds}
    path = os.path.join(d, "record.json")
    json.dump(rec, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(path)


# ---------- レビュー ----------

def rule_exit(rule, s, j):
    """その日の引けでルールの手じまい条件が成立したか"""
    if "新高値" in rule:
        return s["ma50"][j] is not None and s["c"][j] < s["ma50"][j]
    if "急落" in rule:   # コナーズの手じまい: 終値が5日線を上回る（2026-09-27〜）
        return j >= 4 and s["c"][j] > sum(s["c"][j - 4:j + 1]) / 5
    if "ボリンジャー" in rule:
        return s["pctb"][j] is not None and s["pctb"][j] >= 1.0
    if "ミネルヴィニ" in rule:
        return s["ma50"][j] is not None and s["c"][j] < s["ma50"][j]
    if "ワインスタイン" in rule:
        return s["wend"][j] and s["w_ma10"][j] is not None and s["w_c"][j] < s["w_ma10"][j]
    return False


def follow(rule, s, start, px, stop):
    """start 日から、損切りの逆指値（安値が届いたら）とルールの手じまい（引けで成立→翌日の寄り付き）に従って持つ。
    (手じまった日, 価格, 理由) か、まだ持っていれば (最終日, 終値, "保有中")"""
    n = len(s["c"])
    for j in range(start, n):
        if s["l"][j] <= stop:
            return s["date"][j], min(s["o"][j], stop), "損切り"
        if rule_exit(rule, s, j):
            if j + 1 < n:
                return s["date"][j + 1], s["o"][j + 1], "ルールの手じまい"
            return s["date"][j], s["c"][j], "保有中（明日の寄り付きで手じまい予定）"
    return s["date"][-1], s["c"][-1], "保有中"


def cmd_review(a):
    recs = []
    for f in sorted(glob.glob(os.path.join(a.dir, "**", "*.json"), recursive=True)):
        try:
            r = json.load(open(f, encoding="utf-8"))
        except (ValueError, OSError):
            continue
        if "trade_date" in r and r["trade_date"] >= (a.since or ""):
            recs.append(r)
    syms = sorted({c["sym"] for r in recs for c in r["candidates"]} | {h["sym"] for r in recs for h in r["holdings"]})
    data = {}
    for s in syms:
        d = fetch_daily(s)
        if d and len(d["c"]) > 260:
            bt.prepare(d)
            bs.prepare(d)
            data[s] = d
    L = []
    w = L.append
    last = max((d["date"][-1] for d in data.values()), default=max((r["trade_date"] for r in recs), default="記録なし"))
    w(f"# テーマ監視 週次レビュー（{last}の引けまで）\n")
    w(f"- 対象の記録: {len(recs)}日分（{recs[0]['trade_date'] if recs else '-'} 〜 {recs[-1]['trade_date'] if recs else '-'}）")
    w("- 【買い（予約）】は、あなたが実際に約定した記録（保有銘柄.md・売買記録.md）があるものだけを数える。記録がなければ「約定の記録なし」とし、成績に入れない。")
    w("- 【買い】などの成行の候補は、採用したルールどおり（翌日の寄り付きで買い、買値の15%下に損切りの逆指値、ルールの手じまい条件で翌日の寄り付きに売り）に売買した場合の計算。片道0.1%のコスト込み。")
    w("- 実際に注文したかどうかではなく、著者の結論ごとに「その結論に従っていたら」を比べる。数値の事実だけで、Claudeの売買判断は含まない。\n")

    w("## 1. テーマの局面（ワインスタインの回答）\n")
    for r in recs:
        w(f"- {r['trade_date']}: {r['theme_stage'] or '記録なし'}")
    w("")

    trades = load_trades()
    rows = []
    for r in recs:
        for c in r["candidates"]:
            s = data.get(c["sym"])
            if not s or r["trade_date"] not in s["date"]:
                rows.append({**c, "date": r["trade_date"], "status": "株価なし"})
                continue
            i = s["date"].index(r["trade_date"])
            if i + 1 >= len(s["c"]):
                rows.append({**c, "date": r["trade_date"], "status": "まだ寄り付き前"})
                continue
            px = s["o"][i + 1]
            if c.get("stop_buy") or c.get("limit_buy"):
                # パターンB（予約注文）: 価格が届いたかどうかではなく、ユーザーが実際に約定した記録（保有銘柄.md・売買記録.md）があるときだけ数える
                # （ユーザーの指示 2026-09-27。約定していなければ、翌日以降のスキャンで改めてエントリーを探す）
                rec = [b for b in trades if b["sym"] == c["sym"] and r["trade_date"] < b["date"] <= s["date"][min(i + 3, len(s["date"]) - 1)]]
                if not rec:
                    rows.append({**c, "date": r["trade_date"], "status": "約定の記録なし（翌日以降の条件で改めてエントリーを探す）"})
                    continue
                k = s["date"].index(rec[0]["date"]) if rec[0]["date"] in s["date"] else i + 1
                rule = "新高値" if "新高値" in c["kind"] else "急落" if "急落" in c["kind"] else "ボリンジャー" if "ボリンジャー" in c["kind"] else "ミネルヴィニ" if "ミネルヴィニ" in c["kind"] else "ワインスタイン"
                px = rec[0]["price"]
                od, op, why = follow(rule, s, k, px, px * (1 - STOP))
                rows.append({**c, "date": r["trade_date"], "entry": px, "exit_date": od, "exit": op, "status": why + "（実際の約定）",
                             "ret": op / px - 1 - 2 * COST})
                continue
            if c.get("limit") and px > c["limit"]:
                rows.append({**c, "date": r["trade_date"], "status": f"買値{px:.2f}が上限{c['limit']:.2f}を超えたため買わない"})
                continue
            rule = "新高値" if "新高値" in c["kind"] else "急落" if "急落" in c["kind"] else "ボリンジャー" if "ボリンジャー" in c["kind"] else "ミネルヴィニ" if "ミネルヴィニ" in c["kind"] else "ワインスタイン"
            od, op, why = follow(rule, s, i + 1, px, px * (1 - STOP))
            rows.append({**c, "date": r["trade_date"], "entry": px, "exit_date": od, "exit": op, "status": why,
                         "ret": op / px - 1 - 2 * COST})
    w("## 2. 候補（著者の結論ごと）\n")
    w("| 著者の結論 | 件数 | 勝ち | 平均の損益 | 合計の損益（1件＝同じ金額として） |")
    w("|---|---|---|---|---|")
    for vd in ("買い", "買い（予約）", "様子見", "注文する", "見送る", "未判定"):
        g = [x for x in rows if x["verdict"] == vd and "ret" in x]
        if g:
            w(f"| {vd} | {len(g)} | {sum(1 for x in g if x['ret'] > 0)} | {sum(x['ret'] for x in g) / len(g) * 100:+.2f}% | {sum(x['ret'] for x in g) * 100:+.1f}% |")
    if not rows:
        w("| 候補なし | 0 | | | |")
    w("\n| シグナルの日 | 銘柄 | 種類 | 著者の結論 | 買値（翌日。予約注文は約定した価格） | 手じまい | 損益 | 状態 |")
    w("|---|---|---|---|---|---|---|---|")
    for x in rows:
        if "ret" in x:
            w(f"| {x['date']} | {x['sym']} | {x['kind']} | {x['verdict']} | {x['entry']:.2f} | {x['exit_date']} {x['exit']:.2f} | {x['ret'] * 100:+.1f}% | {x['status']} |")
        else:
            w(f"| {x['date']} | {x['sym']} | {x['kind']} | {x['verdict']} | | | | {x['status']} |")

    w("\n## 3. 保有銘柄で【売り】（旧【早めに手じまう】）となったもの\n")
    w("その日の翌日の寄り付きで手じまった場合と、ルールどおり持ち続けた場合の比較。\n")
    w("| 日 | 銘柄 | ルール | 翌日の寄り付きで手じまい | ルールどおり（手じまい日・価格・理由） | 差（早めの手じまい − ルール） |")
    w("|---|---|---|---|---|---|")
    n_early = 0
    for r in recs:
        for h in r["holdings"]:
            if not ("早め" in h["verdict"] or h["verdict"].startswith("売り")):
                continue
            s = data.get(h["sym"])
            if not s or r["trade_date"] not in s["date"]:
                continue
            i = s["date"].index(r["trade_date"])
            if i + 1 >= len(s["c"]):
                continue
            n_early += 1
            early = s["o"][i + 1]
            od, op, why = follow(h["rule"], s, i + 1, early, h["buy_price"] * (1 - STOP))
            w(f"| {r['trade_date']} | {h['sym']} | {h['rule']} | {early:.2f} | {od} {op:.2f}（{why}） | {(early / op - 1) * 100:+.1f}% |")
    if not n_early:
        w("該当なし")
    actual_vs_expected(w)
    text = "\n".join(L) + "\n"
    if a.out:
        open(a.out, "w", encoding="utf-8").write(text)
    print(text)


def load_real(path):
    """保有銘柄.md・売買記録.md の表から [{sym, buy_date, buy, shares, rule, sell_date, sell}] を返す（保有中は sell_date=None）"""
    out = []
    if not os.path.exists(path):
        return out
    for line in open(path, encoding="utf-8"):
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(c) < 5 or not re.match(r"^[A-Z][A-Z.]*$", c[0]) or not re.match(r"^\d{4}-\d{2}-\d{2}$", c[1]):
            continue
        try:
            t = {"sym": c[0], "buy_date": c[1], "buy": float(c[2]), "shares": float(c[3]), "rule": c[4], "sell_date": None, "sell": None}
            if len(c) >= 7 and re.match(r"^\d{4}-\d{2}-\d{2}$", c[5]) and c[6]:
                t["sell_date"], t["sell"] = c[5], float(c[6])
        except ValueError:
            continue
        out.append(t)
    return out


def actual_vs_expected(w):
    """4節: ユーザーが実際に約定した売買（保有銘柄.md・売買記録.md）の成績と、バックテストの見込みの比較（2026-09-29 ユーザーの指示）"""
    base = os.path.join(TOOLS, "..", "新分析ツール")
    closed = [t for t in load_real(os.path.join(base, "売買記録.md")) if t["sell_date"]]
    opened = [t for t in load_real(os.path.join(base, "保有銘柄.md")) if not t["sell_date"]]
    w("\n## 4. 実際の成績とバックテストの見込みの比較\n")
    w(f"`保有銘柄.md`・`売買記録.md` に記録された実際の売買だけで計算する（株数×値段。手数料は含まない）。資金は{CAPITAL:,}ドルから始めたものとする。"
      f"勝率・1回の平均は、決済した売買が{MIN_N}件以上になってから比べる（少ないと偶然の差が大きい）。\n")
    if not closed and not opened:
        w("実際の売買の記録はまだない。")
        return
    px = {}
    for t in closed + opened:
        if t["sym"] not in px:
            d = fetch_daily(t["sym"])
            if d:
                px[t["sym"]] = dict(zip(d["date"], d["c"]))
    today = max((max(v) for v in px.values() if v), default=dt.date.today().isoformat())
    start = min(t["buy_date"] for t in closed + opened)
    # 毎日の資金（決済した損益＋保有中の含み損益、終値で評価）
    days = sorted({d for v in px.values() for d in v if start <= d <= today})
    peak, mdd, last_close = CAPITAL, 0.0, {}
    for d in days:
        eq = CAPITAL
        for t in closed + opened:
            if t["buy_date"] > d:
                continue
            if t["sell_date"] and t["sell_date"] <= d:
                eq += t["shares"] * (t["sell"] - t["buy"])
                continue
            c = px.get(t["sym"], {}).get(d)
            if c is not None:
                last_close[t["sym"]] = c
            c = last_close.get(t["sym"], t["buy"])
            eq += t["shares"] * (c - t["buy"])
        peak = max(peak, eq)
        mdd = max(mdd, 1 - eq / peak)
    realized = sum(t["shares"] * (t["sell"] - t["buy"]) for t in closed)
    unreal = sum(t["shares"] * (last_close.get(t["sym"], t["buy"]) - t["buy"]) for t in opened)
    rets = [t["sell"] / t["buy"] - 1 for t in closed]
    n = len(rets)
    win = sum(r > 0 for r in rets) / n if n else None
    avg = sum(rets) / n if n else None
    hold = sum((dt.date.fromisoformat(t["sell_date"]) - dt.date.fromisoformat(t["buy_date"])).days * 252 / 365 for t in closed) / n if n else None
    span = max(1, (dt.date.fromisoformat(today) - dt.date.fromisoformat(start)).days)
    total = (realized + unreal) / CAPITAL
    cagr = (1 + total) ** (365.25 / span) - 1 if span >= 180 else None
    per_year = n * 365.25 / span if span >= 90 else None
    E = EXPECT
    pct = lambda x, d=1: "-" if x is None else f"{x * 100:+.{d}f}%"
    w(f"- 期間: {start} 〜 {today}（{span}日）。決済した売買 {n}件、保有中 {len(opened)}銘柄")
    w(f"- 損益: 決済分 {realized:+,.0f}ドル、保有中の含み損益 {unreal:+,.0f}ドル、合計 {realized + unreal:+,.0f}ドル（資金{CAPITAL:,}ドルに対して {pct(total)}）\n")
    w("| 項目 | 実際 | バックテストの見込み | 見方 |")
    w("|---|---|---|---|")
    small = n < MIN_N

    def judge(ok, warn):
        return "件数が少なく、まだ比べない" if small else ("見込みの範囲" if ok else warn)
    w(f"| 年率（換算） | {pct(cagr) if cagr is not None else '期間が半年未満のため出さない'} | 年率10〜20%（計算上は{E['cagr'][2] * 100:.1f}%） | "
      f"{'-' if cagr is None else ('見込みの範囲以上' if cagr >= E['cagr'][0] else '見込みより低い（1年未満の差は偶然のことが多い）')} |")
    w(f"| 勝率 | {'-' if win is None else f'{win * 100:.0f}%'}（{n}件） | 約{E['win'] * 100:.0f}% | {judge(win is not None and win >= 0.50, '50%を下回っている')} |")
    w(f"| 1回の平均の損益 | {pct(avg, 2)} | 約{pct(E['avg'])} | {judge(avg is not None and avg > 0, '平均がマイナス')} |")
    w(f"| 最大下落率（資金） | {mdd * 100:.1f}% | 約{E['mdd'] * 100:.0f}%（悪い場合{E['mdd_worst'] * 100:.0f}%） | "
      f"{'バックテストの最悪を超えた（ルールの見直しを検討）' if mdd > E['mdd_worst'] else ('見込みに近い大きな下落の途中' if mdd > 0.25 else '見込みの範囲')} |")
    w(f"| 売買の件数（1年あたり） | {'-' if per_year is None else f'{per_year:.0f}件'} | 約{E['per_year']}件 | {'期間が3か月未満のため出さない' if per_year is None else ('少ない（合図を見送っている可能性）' if per_year < E['per_year'] * 0.5 else '見込みの範囲')} |")
    w(f"| 平均保有日数（取引日） | {'-' if hold is None else f'{hold:.0f}日'} | 約{E['hold']}日 | - |")
    if closed:
        w("\n| ルール | 決済件数 | 勝率 | 1回の平均 | 損益（ドル） |")
        w("|---|---|---|---|---|")
        for rule in sorted({t["rule"] for t in closed}):
            ts = [t for t in closed if t["rule"] == rule]
            rr = [t["sell"] / t["buy"] - 1 for t in ts]
            w(f"| {rule} | {len(ts)} | {sum(r > 0 for r in rr) / len(rr) * 100:.0f}% | {pct(sum(rr) / len(rr), 2)} | "
              f"{sum(t['shares'] * (t['sell'] - t['buy']) for t in ts):+,.0f} |")
    w("\n- 見込みはバックテストの数字で、実際はそれより低くなりやすい（多くの形を試して一番良いものを選んでいるため）。年率10〜20%、悪い年は−10〜−20%を目安にする。")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("record")
    r.add_argument("dir")
    v = sub.add_parser("review")
    v.add_argument("dir")
    v.add_argument("--since")
    v.add_argument("--out")
    a = ap.parse_args()
    (cmd_record if a.cmd == "record" else cmd_review)(a)


if __name__ == "__main__":
    main()
