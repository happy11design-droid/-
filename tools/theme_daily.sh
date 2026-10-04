#!/usr/bin/env bash
# 毎朝のテーマ監視（`新分析ツール/テーマ監視_手順書.md` 手順T1〜T5）の機械的な部分
#
# 使い方:
#   tools/theme_daily.sh prepare <作業ディレクトリ>
#       スキャン（scan.md）と、候補・保有銘柄の数値データ（<ティッカー>_data.txt）を作り、
#       ニュースを調べる銘柄の一覧（news_targets.txt）を書き出す。
#   （ここでメインが、`新分析ツール/ニュース調査指示.md` を読ませた単一のサブエージェントに <作業ディレクトリ>/news.md を書かせる）
#   tools/theme_daily.sh send <作業ディレクトリ>
#       著者ごとのプロンプトとテーマの局面のプロンプトを組み立て、NotebookLMへ並列に送り、
#       回答をまとめた report.md（スキャン・ニュース・回答の全文）を書き出す。
#
# ノートブックごとにサブエージェントを起動しない（`CLAUDE.md` と同じ理由。シェルで並列に送る）。
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT/tools/nlm_chat.sh"
CMD="${1:-}"; D="${2:-}"
[[ -n "$CMD" && -n "$D" ]] || { sed -n '2,14p' "$0"; exit 2; }
mkdir -p "$D"

# 著者とノートブックID（種類の語はスキャンの「種類」「ルール」の列に含まれる語）
declare -A NB=(
  [ボリンジャー]=3dc5edc5-7808-438c-abf0-9c0e5ca6cef9
  [ミネルヴィニ]=e09b765e-4f20-496a-ae2f-6d991c488d0d
  [ワインスタイン]=69875bdb-8d0d-474e-9b1a-c6c1b7bc82a1
  [コナーズ]=56852e48-e64b-4b7d-871e-748abb263d13   # 急落の底（2026-09-27〜）
)

tickers() {  # scan.md の指定した節の表の1列目
  python3 - "$D/scan.md" "$1" <<'PY'
import re, sys
text = open(sys.argv[1], encoding="utf-8").read()
i = text.find(sys.argv[2])
if i >= 0:
    j = text.find("\n## ", i + 1)
    for line in text[i:j if j > 0 else len(text)].splitlines():
        m = re.match(r"^\| ([A-Z][A-Z.]*) \|", line)
        if m:
            print(m.group(1))
PY
}

if [[ "$CMD" == prepare ]]; then
  # 前日の記録（Routine用ブランチの テーマ監視/<日付>/record.json の最新）: 前日の【買い（予約）】が約定したかを確認し、していなければ改めて判定する
  PREV=()
  if git -C "$ROOT" fetch -q origin claude/ecstatic-tesla-660dhs 2>/dev/null; then
    last=$(git -C "$ROOT" -c core.quotepath=false ls-tree --name-only origin/claude/ecstatic-tesla-660dhs "テーマ監視/" | grep -E '/[0-9]{4}-[0-9]{2}-[0-9]{2}$' | grep -v "/$(TZ=Asia/Tokyo date +%F)$" | sort | tail -1)
    if [[ -n "$last" ]] && git -C "$ROOT" show "origin/claude/ecstatic-tesla-660dhs:$last/record.json" > "$D/prev_record.json" 2>/dev/null; then
      PREV=(--prev "$D/prev_record.json")
    fi
  fi
  python3 "$ROOT/tools/theme_scan.py" "$D/scan.md" "${PREV[@]}" > /dev/null
  { tickers "## 4."; tickers "## 4-2."; tickers "## 5."; tickers "## 6."; } | sort -u > "$D/news_targets.txt"
  { tickers "## 5."; tickers "## 6."; } | sort -u > "$D/data_targets.txt"
  while read -r t; do
    python3 "$ROOT/tools/market_data.py" ticker "$t" "$D" > /dev/null 2>&1 || echo "$t の数値データを取得できませんでした" >&2
    # 決算の中身（四半期のEPS・売上・純利益率。ミネルヴィニの本の銘柄選定の材料）を数値データの後ろに足す
    [[ -f "$D/${t}_data.txt" ]] && { echo; python3 "$ROOT/tools/fundamentals.py" "$t"; } >> "$D/${t}_data.txt"
  done < "$D/data_targets.txt"
  echo "scan: $D/scan.md"
  echo "ニュースを調べる銘柄（急騰・急落・監視外の注目・保有・候補）: $(tr '\n' ' ' < "$D/news_targets.txt")"
  echo "候補・保有銘柄: $(tr '\n' ' ' < "$D/data_targets.txt")"
  exit 0
fi

[[ "$CMD" == send ]] || { echo "prepare か send を指定してください" >&2; exit 2; }
# 認証情報の読み込み（Cookie値に `$` が含まれるため source は使わない。tools/run_notebooks.sh と同じ方法）
if [[ -f /root/.nlm/env ]]; then
  while IFS='=' read -r key value; do
    [[ "$key" == NLM_* ]] || continue
    value="${value#\"}"; value="${value%\"}"
    export "$key=$value"
  done < /root/.nlm/env
fi
NEWS=(); [[ -s "$D/news.md" ]] && NEWS=(--news "$D/news.md")
mkdir -p "$D/answers"
rm -f "$D"/answers/*.txt

# テーマの局面（ワインスタイン）: scan.md の1〜4節とテーマ全体のニュース
python3 - "$D" "$ROOT/新分析ツール/テーマ局面_送信プロンプト雛形.txt" <<'PY'
import os, re, sys
d, tpl = sys.argv[1], sys.argv[2]
text = open(os.path.join(d, "scan.md"), encoding="utf-8").read()
theme = text[text.index("## 1."):text.index("## 5.")].strip() if "## 5." in text else text
news = os.path.join(d, "news.md")
if os.path.exists(news):
    body, cur = [], False
    for line in open(news, encoding="utf-8"):
        if line.startswith("## "):
            cur = not re.fullmatch(r"[A-Z][A-Z.]*", line[3:].strip())
        elif cur:
            body.append(line.rstrip())
    if body:
        theme += "\n\nテーマ全体のニュース（サブエージェントの調査）:\n" + "\n".join(body)
# NotebookLM の1回の送信は8,000文字まで（2026-09-30 実測、tools/build_theme_prompt.py の LIMIT）。
# 超えるときは雛形（出力形式の指示）を削らず、テーマ全体のニュース → ヒートマップ（3節）の下位の行の順に縮める
# ワインスタインのノートブックは、ほかの著者より短い文字数で空の応答になる（2026-10-05: 7,450・6,000文字は空、1,944文字は回答）。
# 6,000文字までに縮め、それでも空の応答なら、1〜2節（テーマの強さ・全体の状態）だけの短い版（prompt_theme_short.txt）で送り直す
LIMIT, CUT = 6000, "（文字数の上限のため、ここから後を省略）"
t = open(tpl, encoding="utf-8").read()
short = theme[:theme.index("## 3.")] if "## 3." in theme else theme
open(os.path.join(d, "prompt_theme_short.txt"), "w", encoding="utf-8").write(
    t.replace("{{THEME}}", short.rstrip() + "\n\n（ヒートマップ・急騰急落・ニュースは、文字数の都合で省略）"))
fill = lambda th: t.replace("{{THEME}}", th)
over = len(fill(theme)) - LIMIT
if over > 0 and "テーマ全体のニュース" in theme:
    i = theme.index("テーマ全体のニュース")
    keep = max(i, len(theme) - over - len(CUT))
    theme = theme[:keep] + CUT
    over = len(fill(theme)) - LIMIT
if over > 0 and "## 3." in theme:
    a = theme.index("## 3.")
    b = theme.find("\n## ", a + 1)
    rows = theme[a:b].split("\n")
    while over > 0 and len(rows) > 3 and rows[-1].startswith("| "):
        over -= len(rows.pop()) + 1
    theme = theme[:a] + "\n".join(rows) + theme[b:]
    over = len(fill(theme)) - LIMIT
if over > 0:   # ここで止めると他の著者への送信まで止まるので、警告だけ出して送る（送信失敗は report.md に残る）
    print(f"テーマの局面のプロンプトが{LIMIT}文字を超えます（{len(fill(theme))}文字）", file=sys.stderr)
p = fill(theme)
open(os.path.join(d, "prompt_theme.txt"), "w", encoding="utf-8").write(p)
PY

JOBS=()
# --web は付けない: 同じノートブックへ複数のプロンプトを並列に送るため、サーバー側の同じ会話に混ざると
# 別の銘柄のやり取りが判定に影響しうる。結果は毎朝のページ（Artifact）で見る（個別分析 theme_single.sh は --web を付ける）。
send() {  # $1=ノートブックID $2=プロンプト $3=回答ファイル
  ( nlm_chat "$1" "$2" "$3" "$3.err" || echo "送信に失敗: $(tail -1 "$3.err")" >> "$3" ) &
  JOBS+=($!)
}
# テーマの局面: まず全体の版を1回だけ送り、空の応答なら短い版で送り直す
( A="$D/answers/0_テーマの局面_ワインスタイン.txt"
  if ! NLM_RETRY_EMPTY=0 nlm_chat "${NB[ワインスタイン]}" "$D/prompt_theme.txt" "$A" "$A.err"; then
    if grep -q "exit 6" "$A.err" && nlm_chat "${NB[ワインスタイン]}" "$D/prompt_theme_short.txt" "$A" "$A.err"; then
      printf '\n（全体の版が空の応答だったため、1〜2節だけの短い版で送り直した回答。ヒートマップ・急騰急落・ニュースは渡していない）\n' >> "$A"
    else
      echo "送信に失敗: $(tail -1 "$A.err")" >> "$A"
    fi
  fi ) &
JOBS+=($!)

for KIND in ボリンジャー ミネルヴィニ ワインスタイン コナーズ; do
  ARGS=()
  while read -r t; do
    [[ -f "$D/${t}_data.txt" ]] && ARGS+=("$t:$D/${t}_data.txt")
  done < "$D/data_targets.txt"
  [[ ${#ARGS[@]} -gt 0 ]] || continue
  out=$(python3 "$ROOT/tools/build_theme_prompt.py" "$D/scan.md" "$D/out_$KIND" "$KIND" "${NEWS[@]}" "${ARGS[@]}" 2>&1) || { echo "$out" >&2; continue; }
  for p in "$D/out_$KIND"/prompt_*.txt; do
    [[ -f "$p" ]] || continue
    send "${NB[$KIND]}" "$p" "$D/answers/1_${KIND}_$(basename "$p" .txt).txt"
  done
done
for j in "${JOBS[@]}"; do wait "$j" || true; done

{
  echo "# テーマ監視 $(sed -n 's/^# テーマ監視（\(.*\)の引け時点）/\1/p' "$D/scan.md")"
  echo
  echo "# 著者の回答（全文）"
  for f in "$D"/answers/*.txt; do
    echo
    echo "## $(basename "$f" .txt)"
    echo
    cat "$f"
  done
  echo
  echo "# スキャン（数値と事実）"
  echo
  sed '1d' "$D/scan.md"
  if [[ -s "$D/news.md" ]]; then
    echo
    echo "# ニュース（サブエージェントの調査）"
    echo
    cat "$D/news.md"
  fi
} > "$D/report.md"
# 週次レビュー用の記録（候補・保有銘柄と著者の結論）
python3 "$ROOT/tools/theme_review.py" record "$D" > /dev/null
echo "report: $D/report.md"
echo "record: $D/record.json"
