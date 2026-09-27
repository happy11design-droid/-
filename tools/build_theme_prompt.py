#!/usr/bin/env python3
"""テーマ監視の候補を著者ノートブックへ送るプロンプトの組み立て（`新分析ツール/テーマ監視_手順書.md` 手順T4）

使い方:
  tools/build_theme_prompt.py <scan.md> <出力ディレクトリ> <種類の語> [--news news.md] <ティッカー>:<データファイル> [...]
    <scan.md>: tools/theme_scan.py の出力
    <種類の語>: 「ボリンジャー」「ミネルヴィニ」「ワインスタイン」のどれか。候補の表の「種類」と、保有銘柄の表の「ルール」にこの語を含む銘柄だけを入れる
    --news: サブエージェントが書いた news.md（`新分析ツール/ニュース調査指示.md`）。銘柄ごとの節とテーマ全体の節を差し込む
    <データファイル>: tools/market_data.py ticker が書き出した <ティッカー>_data.txt（ニュースを足したファイルでもよい）

`新分析ツール/テーマ監視_送信プロンプト雛形.txt` の {{THEME}} と {{CANDIDATES}} だけを差し込み、雛形のほかの文言は変えない。
NotebookLM の1回の送信は12,000文字までなので、候補を分けて <出力ディレクトリ>/prompt_1.txt, prompt_2.txt ... に書き出す。
"""
import os
import re
import sys

LIMIT = 12000
TEMPLATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "新分析ツール", "テーマ監視_送信プロンプト雛形.txt")


def section(text, head):
    """「## 5.」のような見出しから次の「## 」までを返す（見出しがなければ空）"""
    i = text.find(head)
    if i < 0:
        return ""
    j = text.find("\n## ", i + 1)
    return text[i:j if j > 0 else len(text)]


def parse_news(path):
    """news.md を {ティッカー: 本文, "テーマ全体": 本文} に分ける（見出しが大文字のティッカーでない節はテーマ全体とみなす）"""
    out, cur = {}, None
    for line in open(path, encoding="utf-8"):
        m = re.match(r"^## (.+)", line)
        if m:
            t = m.group(1).strip()
            cur = t if re.fullmatch(r"[A-Z][A-Z.]*", t) else "テーマ全体"
            out.setdefault(cur, "")
        elif cur:
            out[cur] += line
    return {k: v.strip() for k, v in out.items()}


def main():
    if len(sys.argv) < 5:
        sys.exit(__doc__)
    scan, outdir, kind = sys.argv[1], sys.argv[2], sys.argv[3]
    rest = sys.argv[4:]
    news = {}
    if rest and rest[0] == "--news":
        news = parse_news(rest[1])
        rest = rest[2:]
    files = dict(x.split(":", 1) for x in rest)
    text = open(scan, encoding="utf-8").read()
    # テーマの状態＝1・2節（ヒートマップの表は長いので送らない）
    theme = text[text.index("## 1."):text.index("## 3.")].strip()
    if news.get("テーマ全体"):
        theme += "\n\nテーマ全体のニュース（サブエージェントの調査）:\n" + news["テーマ全体"]
    rows = {}
    head = None
    for line in section(text, "## 5.").splitlines():
        if line.startswith("| 銘柄 |"):
            head = [c.strip() for c in line.strip("|").split("|")]
        elif head and re.match(r"^\| [A-Z]", line):
            row = dict(zip(head, [c.strip() for c in line.strip("|").split("|")]))
            if kind in row.get("ルール", ""):
                rows.setdefault(row["銘柄"], []).append({"保有": row})
    head = None
    for line in section(text, "## 6.").splitlines():
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
            print(f"{sym} の数値データがないため送信から外しました", file=sys.stderr)
            continue
        b = []
        for r in rs:
            if "保有" in r:
                h = r["保有"]
                b.append(f"## {sym}（保有中）")
                b.append(f"- ルール: {h['ルール']}／買った日: {h['買った日']}／買値: {h['買値']}／終値: {h['終値']}（{h['損益']}）／損切り価格: {h['損切り価格（買値の15%下、逆指値）']}")
                b.append(f"- ルールの手じまい条件: {h['ルールの手じまい条件']}／次回決算予定日: {h['次回決算予定日']}")
            else:
                if not any(x.startswith(f"## {sym}（候補") for x in b):
                    b.append(f"## {sym}（候補、{r['グループ']}）")
                b.append(f"- パターン: {r.get('パターン', 'A')}（A＝条件成立、B＝成立が目前で予約注文の候補）／種類: {r['種類']}／当てはまった条件: {r['当てはまった条件']}／RS: {r['RS']}／銘柄の局面: {r.get('局面', '記載なし')}／次回決算予定日: {r['次回決算予定日']}")
                b.append(f"- 注文の目安（スクリプトの計算）: {r['注文の目安']}")
        b.append("- ニュース（サブエージェントの調査）:\n" + news.get(sym, "調査なし"))
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
