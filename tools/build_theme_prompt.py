#!/usr/bin/env python3
"""テーマ監視の候補を著者ノートブックへ送るプロンプトの組み立て（`新分析ツール/テーマ監視_手順書.md` 手順T4）

使い方:
  tools/build_theme_prompt.py <scan.md> <出力ディレクトリ> <種類の語> <ティッカー>:<データファイル> [...]
    <scan.md>: tools/theme_scan.py の出力
    <種類の語>: 候補の表の「種類」の列に含まれる語（例: 「ボリンジャー」「ミネルヴィニ」「ワインスタイン」）。その種類の候補だけを入れる
    <データファイル>: tools/market_data.py ticker が書き出した <ティッカー>_data.txt（ニュースを足したファイルでもよい）

`新分析ツール/テーマ監視_送信プロンプト雛形.txt` の {{THEME}} と {{CANDIDATES}} だけを差し込み、雛形のほかの文言は変えない。
NotebookLM の1回の送信は12,000文字までなので、候補を分けて <出力ディレクトリ>/prompt_1.txt, prompt_2.txt ... に書き出す。
"""
import os
import re
import sys

LIMIT = 12000
TEMPLATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "新分析ツール", "テーマ監視_送信プロンプト雛形.txt")


def main():
    if len(sys.argv) < 5:
        sys.exit(__doc__)
    scan, outdir, kind = sys.argv[1], sys.argv[2], sys.argv[3]
    files = dict(x.split(":", 1) for x in sys.argv[4:])
    text = open(scan, encoding="utf-8").read()
    # テーマの状態＝1・2節（ヒートマップの表は長いので送らない）
    theme = text[text.index("## 1."):text.index("## 3.")].strip()
    rows = {}
    head = None
    for line in text[text.index("## 4."):].splitlines():
        if line.startswith("| 銘柄 |"):
            head = [c.strip() for c in line.strip("|").split("|")]
        elif head and re.match(r"^\| [A-Z]", line):
            cells = [c.strip() for c in line.strip("|").split("|")]
            row = dict(zip(head, cells))
            if kind in row["種類"]:
                rows.setdefault(row["銘柄"], []).append(row)
    template = open(TEMPLATE, encoding="utf-8").read()
    blocks = []
    for sym, rs in rows.items():
        if sym not in files:
            sys.exit(f"{sym} のデータファイルが指定されていません")
        b = [f"## {sym}（{rs[0]['グループ']}）"]
        for r in rs:
            b.append(f"- 種類: {r['種類']}／当てはまった条件: {r['当てはまった条件']}／RS: {r['RS']}／次回決算予定日: {r['次回決算予定日']}")
            b.append(f"- 注文の目安（スクリプトの計算。採否は著者が判定）: {r['注文の目安']}")
        b.append(open(files[sym], encoding="utf-8").read().strip())
        blocks.append("\n".join(b))
    if not blocks:
        print("該当する候補なし")
        return
    os.makedirs(outdir, exist_ok=True)
    fill = lambda cands: template.replace("{{THEME}}", theme).replace("{{CANDIDATES}}", "\n\n".join(cands))
    batches, cur = [], []
    for b in blocks:
        if cur and len(fill(cur + [b])) > LIMIT:
            batches.append(cur)
            cur = []
        cur.append(b)
    batches.append(cur)
    for k, bt in enumerate(batches, 1):
        p = fill(bt)
        if len(p) > LIMIT:
            sys.exit(f"1銘柄だけでも{LIMIT}文字を超えます（{len(p)}文字）。データファイルを短くしてください")
        path = os.path.join(outdir, f"prompt_{k}.txt")
        open(path, "w", encoding="utf-8").write(p)
        print(f"{path}: {len(p)}文字、{len(bt)}銘柄")


if __name__ == "__main__":
    main()
