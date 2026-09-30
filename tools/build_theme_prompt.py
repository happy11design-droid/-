#!/usr/bin/env python3
"""テーマ監視の候補を著者ノートブックへ送るプロンプトの組み立て（`新分析ツール/テーマ監視_手順書.md` 手順T4）

使い方:
  tools/build_theme_prompt.py <scan.md> <出力ディレクトリ> <種類の語> [--news news.md] <ティッカー>:<データファイル> [...]
    <scan.md>: tools/theme_scan.py の出力
    <種類の語>: 「ボリンジャー」「ミネルヴィニ」「ワインスタイン」「コナーズ」のどれか。候補の表の「種類」と、保有銘柄の表の「ルール」にこの語を含む銘柄だけを入れる
    --news: サブエージェントが書いた news.md（`新分析ツール/ニュース調査指示.md`）。銘柄ごとの節とテーマ全体の節を差し込む
    <データファイル>: tools/market_data.py ticker が書き出した <ティッカー>_data.txt（ニュースを足したファイルでもよい）

`新分析ツール/テーマ監視_送信プロンプト雛形.txt` の {{THEME}} と {{CANDIDATES}} だけを差し込み、雛形のほかの文言は変えない。
NotebookLM の1回の送信は8,000文字までなので、候補を分けて <出力ディレクトリ>/prompt_1.txt, prompt_2.txt ... に書き出す。
分けるのは銘柄の単位で、銘柄のデータは削らない。1銘柄だけでも上限を超えるときに限り、その銘柄のニュース
（それでも足りなければテーマ全体のニュース）を末尾から縮める。雛形（出力形式の指示を含む）は削らない。
"""
import os
import re
import sys

# 2026-09-30 実測: 8,000文字は成功、9,500文字（約18KB）・9,800文字（ASCII、9.8KB）は即座に空の応答（exit 6）。
# 文字数で数える上限で、ノートブックによらない（9/23 には12,000文字が通っていたので、上限が下がった）
LIMIT = 8000
CUT = "（文字数の上限のため、ここから後を省略）"
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
            rule = row.get("ルール", "")
            if kind in rule or (kind == "コナーズ" and "急落" in rule) or (kind == "ミネルヴィニ" and "新高値" in rule):   # 急落の底はコナーズ、新高値はミネルヴィニが担当
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
                b.append(f"- ルールの手じまい条件: {h['ルールの手じまい条件']}／出来高2倍の大陰線（買った後の直近5日）: {h.get('出来高2倍の大陰線（買った後の直近5日）', '記載なし')}／次回決算予定日: {h['次回決算予定日']}")
            else:
                if not any(x.startswith(f"## {sym}（候補") for x in b):
                    b.append(f"## {sym}（候補、{r['グループ']}）")
                b.append(f"- パターン: {r.get('パターン', 'A')}（A＝条件成立、B＝成立が目前で予約注文の候補）／種類: {r['種類']}／当てはまった条件: {r['当てはまった条件']}／RS: {r['RS']}／銘柄の局面: {r.get('局面', '記載なし')}／次回決算予定日: {r['次回決算予定日']}")
                b.append(f"- 注文の目安（スクリプトの計算）: {r['注文の目安']}")
        blocks.append(("\n".join(b), news.get(sym, "調査なし"), open(files[sym], encoding="utf-8").read().strip()))
    if not blocks:
        print("該当する候補なし")
        return
    os.makedirs(outdir, exist_ok=True)
    block = lambda head, nw, data: f"{head}\n- ニュース（サブエージェントの調査）:\n{nw}\n{data}"
    fill = lambda cands, th=theme: template.replace("{{THEME}}", th).replace("{{CANDIDATES}}", "\n\n".join(block(*c) for c in cands))
    batches, cur = [], []
    for b in blocks:
        if cur and len(fill(cur + [b])) > LIMIT:
            batches.append(cur)
            cur = []
        cur.append(b)
    batches.append(cur)
    for k, bt in enumerate(batches, 1):
        th = theme
        if len(fill(bt)) > LIMIT:   # 1銘柄だけで超える（bt は1銘柄）: ニュース → テーマ全体のニュースの順に末尾から縮める
            head, nw, data = bt[0]
            over = len(fill(bt)) - LIMIT + len(CUT)
            if len(nw) > over:
                bt = [(head, nw[:len(nw) - over] + CUT, data)]
            elif "テーマ全体のニュース" in th:
                bt = [(head, "（文字数の上限のため省略）", data)]
                over = len(fill(bt, th)) - LIMIT + len(CUT)
                i = th.index("テーマ全体のニュース")
                if over > 0 and len(th) - i > over:
                    th = th[:len(th) - over] + CUT
            print(f"{head.splitlines()[0][3:]}: 1銘柄で{LIMIT}文字を超えるため、ニュースを縮めました", file=sys.stderr)
        p = fill(bt, th)
        if len(p) > LIMIT:
            sys.exit(f"1銘柄だけでも{LIMIT}文字を超えます（{len(p)}文字）。データファイルを短くしてください")
        path = os.path.join(outdir, f"prompt_{k}.txt")
        open(path, "w", encoding="utf-8").write(p)
        print(f"{path}: {len(p)}文字、{len(bt)}銘柄")


if __name__ == "__main__":
    main()
