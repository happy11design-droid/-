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
                rule = "ボリンジャー" if "ボリンジャー" in c["kind"] else "ミネルヴィニ" if "ミネルヴィニ" in c["kind"] else "ワインスタイン"
                px = rec[0]["price"]
                od, op, why = follow(rule, s, k, px, px * (1 - STOP))
                rows.append({**c, "date": r["trade_date"], "entry": px, "exit_date": od, "exit": op, "status": why + "（実際の約定）",
                             "ret": op / px - 1 - 2 * COST})
                continue
            if c.get("limit") and px > c["limit"]:
                rows.append({**c, "date": r["trade_date"], "status": f"買値{px:.2f}が上限{c['limit']:.2f}を超えたため買わない"})
                continue
            rule = "ボリンジャー" if "ボリンジャー" in c["kind"] else "ミネルヴィニ" if "ミネルヴィニ" in c["kind"] else "ワインスタイン"
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
    text = "\n".join(L) + "\n"
    if a.out:
        open(a.out, "w", encoding="utf-8").write(text)
    print(text)


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
