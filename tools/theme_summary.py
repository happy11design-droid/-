#!/usr/bin/env python3
"""毎朝のテーマ監視の「判定のまとめ」（ルールの判定と著者の判定を分けた表）を作る（2026-10-14 ユーザーの指示）

使い方:
  tools/theme_summary.py <D>      # <D>/scan.md と <D>/record.json を読み、まとめのMarkdownを標準出力に出す

- ルールの判定: スクリプト（採用した売買ルール）が数値で決めたもの。保有銘柄は損切り・ルールの手じまい条件・半分売りの合図、
  候補はパターンA（翌日の寄り付きで買い）／B（予約注文）。
- 著者の判定: ノートブックの著者の回答（方式B: 買いは注文を止める理由があるときだけ【様子見】、保有はルールより早く手じまう理由があるときだけ【売り】）。
- Claudeの判断は入れない。
"""
import json
import os
import re
import sys

try:   # カタカナの会社名（`新分析ツール/銘柄名.json`）
    NAMES = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "新分析ツール", "銘柄名.json"), encoding="utf-8"))
except (OSError, ValueError):
    NAMES = {}
SLOTS = 4   # 同時保有の上限（theme_scan.SLOTS と同じ）


def table_rows(md, head):
    """head で始まる節の最初の表を [{列名: 値}] で返す"""
    lines = md.splitlines()
    try:
        k = next(i for i, x in enumerate(lines) if x.startswith(head))
    except StopIteration:
        return []
    rows, cols = [], None
    for x in lines[k + 1:]:
        if x.startswith("## "):
            break
        if not x.startswith("|"):
            if cols:
                break
            continue
        cells = [c.strip() for c in x.strip().strip("|").split("|")]
        if cols is None:
            cols = cells
        elif not set("".join(cells)) <= set("-: "):
            rows.append(dict(zip(cols, cells)))
    return rows


def num(x):
    try:
        return float(re.sub(r"[^0-9.\-]", "", x))
    except ValueError:
        return None


def hold_rule(r):
    """保有銘柄の行から、ルールの判定（売り／半分売り／保有継続）と理由"""
    close, stop = num(r.get("終値", "")), num(r.get("損切り価格（買値の15%下、逆指値）", ""))
    ex = r.get("ルールの手じまい条件", "")
    if close is not None and stop is not None and close <= stop:
        return "**売り**", f"終値 {close:g} が損切り価格 {stop:g} 以下"
    m = re.match(r"成立（([^）]*)）", ex)
    if m:
        return "**売り**", m.group(1)
    if "半分売りの合図: **今日**" in ex or "半分売りの合図: 今日" in ex:
        return "**半分売り**", "反転の合図（翌日の寄り付きで半分）"
    m = re.search(r"未成立（([^）]*)）", ex)
    gap = f"損切り {stop:g}（終値から {stop / close * 100 - 100:+.1f}%）" if close and stop else ""
    return "保有継続", "、".join(x for x in (gap, m.group(1) if m else "") if x)


def main():
    D = sys.argv[1]
    scan = open(os.path.join(D, "scan.md"), encoding="utf-8").read()
    rec = json.load(open(os.path.join(D, "record.json"), encoding="utf-8"))
    out = ["# 判定のまとめ（ルールの判定と著者の判定を分けて表示）", "",
           "- **ルールの判定**: 採用した売買ルール（スクリプト）が数値で決めたもの。損切りは買値の15%下の逆指値（日中に届けばその場で売れる）。",
           "- **著者の判定**: ノートブックの著者の回答。買いは注文を止める理由があるときだけ【様子見】、保有はルールより早く手じまう理由があるときだけ【売り】。根拠は下の「著者の回答（全文）」。",
           "- 2つが食い違うときに、どちらに従うかはユーザーが決める。", ""]
    s2 = rec.get("s2") or {}
    if s2:
        out += [f"- **テーマ全体の急落（S2・記録だけ）: {s2.get('label', '記録なし')}**"
                + (f"（SOXが直近60取引日の最高値から {s2['drop'] * 100:+.1f}%）" if s2.get("drop") is not None else "")
                + "。S2の日の順張りの候補には「S2なら見送る形」と付ける（売買のルールは変えない。記録してから採用を決める。2026-10-14）", ""]
    hv = {h["sym"]: h for h in rec.get("holdings", [])}
    rows = table_rows(scan, "## 5. 保有銘柄")
    out += ["## 保有銘柄", ""]
    if rows:
        out += ["| 銘柄 | ルール | 損益 | ルールの判定 | ルールの判定の理由 | 著者の判定 |", "|---|---|---|---|---|---|"]
        for r in rows:
            sym = r.get("銘柄", "")
            rv, why = hold_rule(r)
            h = hv.get(sym, {})
            av = f"【{h['verdict']}】（{h.get('author', '')}）" if h.get("verdict") else "回答なし"
            if h.get("verdict") and h["verdict"] != "保有継続" and rv == "保有継続":
                av = "**" + av + "**"
            out.append(f"| {sym} | {r.get('ルール', '')} | {r.get('損益', '')} | {rv} | {why} | {av} |")
    else:
        out.append("保有銘柄なし")
    out += ["", "## 候補の判定（並びは上の「買う順番」の表と同じ）", ""]
    cands = rec.get("candidates", [])
    if cands:
        rows6 = {r.get("銘柄", ""): r for r in table_rows(scan, "## 6. 候補")}
        held = {h["sym"] for h in rec.get("holdings", [])}
        exits = sum(1 for r in rows if hold_rule(r)[0] == "**売り**")
        free = max(0, SLOTS - len(held) + exits)
        def rs_of(c):
            if isinstance(c.get("rs"), (int, float)):
                return c["rs"]
            try:
                return float(rows6.get(c["sym"], {}).get("RS", ""))
            except ValueError:
                return None
        def key(c):   # 毎朝のツールの買う順番: 監視銘柄の候補→テーマの外、成行（A）→予約（B）、RSの高い順（2026-10-17 ユーザー決定。10-09〜10-16 は50日線の傾きが小さい順）
            r = rows6.get(c["sym"], {})
            return (r.get("グループ") == "テーマの外", c.get("pattern") != "A", -(rs_of(c) or 0))
        cands = sorted([c for c in cands if c["sym"] not in held], key=key)
        out += [f"- 並びは上の「買う順番」の表と同じ（RSの高い順。勝率の高い順ではない）。注文の値段・株数・逆指値は上の表を見る。"
                f"勝率・1回平均は、そのルールの過去の成績（後知恵なしの監視銘柄・2015年〜の全部の合図）。",
                f"- 空き枠: {free}（同時保有{SLOTS}銘柄まで。保有{len(held)}、うちルールの売り{exits}）。著者が【様子見】の候補を見送るかはユーザーが決める。", "",
                "| 順 | 銘柄 | ルール | 過去の勝率 | 過去の1回平均 | RS | ルールの判定 | 著者の判定 |", "|---|---|---|---|---|---|---|---|"]
        for k, c in enumerate(cands, 1):
            r = rows6.get(c["sym"], {})
            m = re.search(r"勝率(\d+)%・1回平均([+\-]?[\d.]+%)", r.get("ルールの過去の成績", ""))
            wr, avg = (m.group(1) + "%", m.group(2)) if m else ("—", "—")
            if c.get("pattern") == "A":
                rv = "買い（翌日の寄り付き）"
            elif c.get("pattern") == "B":
                px = c.get("stop_buy") or c.get("limit_buy") or c.get("limit")
                rv = "買い（予約）" + (f" {px:g}" if isinstance(px, (int, float)) else "")
            else:
                rv = c.get("pattern") or ""
            if c.get("s2_skip"):
                rv += "（S2なら見送る形・記録だけ）"
            av = f"【{c['verdict']}】（{c.get('author', '')}）" if c.get("verdict") else "回答なし"
            rs_ = rs_of(c)
            s50 = f"{rs_:.0f}" if rs_ is not None else "—"
            n = f"{k}" + ("" if k <= free else "（枠外）")
            out.append(f"| {n} | {c['sym']}{'（' + NAMES[c['sym']] + '）' if NAMES.get(c['sym']) else ''} | {c.get('kind', '')} | {wr} | {avg} | {s50} | {rv} | {av} |")
    else:
        out.append("候補なし")
    print("\n".join(out))


if __name__ == "__main__":
    main()
