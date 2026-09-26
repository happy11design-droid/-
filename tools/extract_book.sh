#!/usr/bin/env bash
# 書籍のNotebookLMノートブックから、判定用ルールブックを作る（tools/書籍抽出/ のプロンプトを使う）。
#
# 前提: ノートブックに tools/merge_chapters.py で作った章ファイル（「01_〜.md」のように数字2桁_で始まる名前）が
#       ソースとして登録されていること。認証は `チャート分析.txt` 手順Aで更新しておく。
#
# 使い方:
#   tools/extract_book.sh <フェーズ> --notebook <ノートブック名> --out <作業ディレクトリ> [--book <書籍名>] [--only <章番号,...>]
#
# フェーズ:
#   chapters  手順1: 章ごとに抽出し、「抽出_〈章ファイル名〉」としてソースに登録する（--only 01,05 で章を限定）
#   rulebook  手順2: 抽出結果を統合し、「判定用ルールブック」としてソースに登録する
#   verify    手順3: 原本とルールブックを照合し、食い違い・漏れの一覧を標準出力に出す
#   table     手順4: 数値ルールの表を <作業ディレクトリ>/ルール表.md に出力する
#
# 長い章（CHUNK_PAGES ページ超）はページ範囲で分割して依頼する。回答の最終行に「未出力の節」があれば続きを依頼し、
# 最終行そのものが無い（途中で打ち切られた）場合は範囲を半分に分けて依頼し直す。
set -uo pipefail

PROMPTS="$(cd "$(dirname "$0")" && pwd)/書籍抽出"
CHUNK_PAGES=18
JOBS=3

PHASE="${1:-}"; shift || true
NOTEBOOK=""; OUT=""; BOOK=""; ONLY=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --notebook) NOTEBOOK="$2"; shift 2 ;;
    --out)      OUT="$2"; shift 2 ;;
    --book)     BOOK="$2"; shift 2 ;;
    --only)     ONLY="$2"; shift 2 ;;
    *) echo "不明な引数: $1" >&2; exit 2 ;;
  esac
done
[[ -n "$PHASE" && -n "$NOTEBOOK" && -n "$OUT" ]] || { sed -n '2,20p' "$0" >&2; exit 2; }
BOOK="${BOOK:-$NOTEBOOK}"
mkdir -p "$OUT"

# 認証情報の読み込み（run_notebooks.sh と同じ方式。Cookie値に `$` が含まれるため source は使わない）
if [[ -f /root/.nlm/env ]]; then
  while IFS='=' read -r key value; do
    [[ "$key" == NLM_* ]] || continue
    value="${value#\"}"; value="${value%\"}"
    export "$key=$value"
  done < /root/.nlm/env
fi

NB=$(nlm notebook list | awk -F'\t' -v t="$NOTEBOOK" '$2 == t {print $1; exit}') || {
  echo "nlm notebook list に失敗しました。手順Aの再認証を実行してください。" >&2; exit 1; }
[[ -n "$NB" ]] || { echo "ノートブック「$NOTEBOOK」が見つかりません" >&2; exit 1; }

# ID<TAB>タイトル の一覧
sources() { nlm source list "$NB" | awk -F'\t' 'NR > 1 {print $1 "\t" $2}'; }
ids_matching() { sources | awk -F'\t' -v re="$1" '$2 ~ re {print $1}' | paste -sd, -; }

# テンプレートの {{KEY}} を置換する（値に記号が含まれても壊れないよう python で行う）
fill() {
  local tmpl="$1"; shift
  python3 - "$tmpl" "$@" <<'PY'
import sys
text = open(sys.argv[1], encoding="utf-8").read()
for kv in sys.argv[2:]:
    k, v = kv.split("=", 1)
    text = text.replace("{{" + k + "}}", v)
sys.stdout.write(text)
PY
}

# chat <出力ファイル> <ソースID(カンマ区切り)> <プロンプトファイル>
chat() {
  local out="$1" ids="$2" prompt="$3" try
  for try in 1 2 3; do
    if nlm generate-chat --citations off --source-ids "$ids" --prompt-file "$prompt" "$NB" >"$out" 2>"$out.err" && [[ -s "$out" ]]; then
      # 回答中の引用番号（[2] や [1-8]、[1, 3, 4]）は、ソースとして登録すると意味を失うので取り除く
      sed -i -E 's/ ?\[[0-9]+([-–, ]+[0-9]+)*\]//g' "$out"
      return 0
    fi
    sleep $((try * 10))
  done
  echo "送信に失敗しました: $(tail -3 "$out.err")" >&2
  return 1
}

# 回答の最終行（空行を除く）
last_line() { awk 'NF {l = $0} END {print l}' "$1"; }

# add_source <ソース名> <ファイル>: 同名のソースがあれば差し替える
add_source() {
  local name="$1" file="$2" old
  old=$(sources | awk -F'\t' -v t="$name" '$2 == t {print $1; exit}')
  if [[ -n "$old" ]]; then
    nlm source add --name "$name" --replace "$old" "$NB" "$file" >/dev/null
  else
    nlm source add --name "$name" "$NB" "$file" >/dev/null
  fi
}

# extract_range <出力ファイル> <ソースID> <ソース名> <開始ページ> <終了ページ> <分割の深さ>
extract_range() {
  local out="$1" id="$2" name="$3" a="$4" b="$5" depth="$6" range last p n
  if [[ -z "$a" ]]; then range="全体"; else range="p.${a}〜p.${b}の範囲"; fi
  fill "$PROMPTS/1_章抽出.txt" "SOURCE=$name" "RANGE=$range" >"$out.prompt"
  chat "$out" "$id" "$out.prompt" || return 1
  last=$(last_line "$out")
  if [[ "$last" != *"未出力の節"* ]]; then
    # 最終行が無い＝途中で打ち切られた。範囲を半分に分けて依頼し直す
    if [[ -n "$a" && $depth -lt 2 && $b -gt $a ]]; then
      local mid=$(( (a + b) / 2 ))
      extract_range "$out.1" "$id" "$name" "$a" "$mid" $((depth + 1)) || return 1
      extract_range "$out.2" "$id" "$name" $((mid + 1)) "$b" $((depth + 1)) || return 1
      cat "$out.1" "$out.2" >"$out"
      return 0
    fi
    echo "警告: $name（$range）の回答が途中で打ち切られた可能性があります" >&2
    return 0
  fi
  n=0
  while [[ "$last" != *"未出力の節: なし"* && $n -lt 2 ]]; do
    n=$((n + 1))
    fill "$PROMPTS/1b_続き.txt" "SOURCE=$name" "SECTIONS=${last#*未出力の節: }" >"$out.cont$n.prompt"
    chat "$out.cont$n" "$id" "$out.cont$n.prompt" || return 1
    printf '\n\n' >>"$out"; cat "$out.cont$n" >>"$out"
    last=$(last_line "$out.cont$n")
  done
  [[ "$last" == *"未出力の節: なし"* ]] || echo "警告: $name（$range）に未出力の節が残っています: $last" >&2
  return 0
}

extract_chapter() {
  local id="$1" name="$2" base="${2%.md}" dir="$OUT/chapters" pages first lastp total a parts=()
  mkdir -p "$dir"
  pages=$(nlm source read --format text "$NB" "$id" | grep -oE '<!-- p\.[0-9]+ -->' | grep -oE '[0-9]+')
  first=$(head -1 <<<"$pages"); lastp=$(tail -1 <<<"$pages"); total=$(grep -c . <<<"$pages")
  if [[ -z "$first" || $total -le $CHUNK_PAGES ]]; then
    extract_range "$dir/$base.part1" "$id" "$name" "" "" 0 || return 1
    parts=("$dir/$base.part1")
  else
    local k=0 chunks=$(( (total + CHUNK_PAGES - 1) / CHUNK_PAGES )) size
    size=$(( (total + chunks - 1) / chunks ))
    for ((a = first; a <= lastp; a += size)); do
      k=$((k + 1))
      local b=$(( a + size - 1 )); (( b > lastp )) && b=$lastp
      extract_range "$dir/$base.part$k" "$id" "$name" "$a" "$b" 0 || return 1
      parts+=("$dir/$base.part$k")
    done
  fi
  { echo "# 抽出: $base"; echo; for p in "${parts[@]}"; do cat "$p"; echo; done; } >"$dir/抽出_$base.md"
  add_source "抽出_$base" "$dir/抽出_$base.md" || { echo "ソース登録に失敗: 抽出_$base" >&2; return 1; }
  echo "完了: 抽出_$base（${total}ページ、${#parts[@]}回に分けて依頼）"
}

case "$PHASE" in
  chapters)
    mapfile -t rows < <(sources | awk -F'\t' '$2 ~ /^[0-9][0-9]_/')
    running=0; fail=0
    for row in "${rows[@]}"; do
      id="${row%%$'\t'*}"; name="${row#*$'\t'}"
      if [[ -n "$ONLY" && ",$ONLY," != *",${name:0:2},"* ]]; then continue; fi
      extract_chapter "$id" "$name" &
      running=$((running + 1))
      if (( running >= JOBS )); then wait -n || fail=1; running=$((running - 1)); fi
    done
    while (( running > 0 )); do wait -n || fail=1; running=$((running - 1)); done
    exit $fail
    ;;
  rulebook)
    ids=$(ids_matching '^抽出_')
    [[ -n "$ids" ]] || { echo "「抽出_」で始まるソースがありません。先に chapters を実行してください" >&2; exit 1; }
    fill "$PROMPTS/2_ルールブック.txt" "BOOK=$BOOK" "PART=前半（項目1〜6）" "ITEMS=項目1〜6" >"$OUT/rulebook1.prompt"
    fill "$PROMPTS/2_ルールブック.txt" "BOOK=$BOOK" "PART=後半（項目7〜12）" "ITEMS=項目7〜12" >"$OUT/rulebook2.prompt"
    chat "$OUT/rulebook1.txt" "$ids" "$OUT/rulebook1.prompt" || exit 1
    chat "$OUT/rulebook2.txt" "$ids" "$OUT/rulebook2.prompt" || exit 1
    for f in rulebook1 rulebook2; do
      l=$(last_line "$OUT/$f.txt")
      [[ "$l" == *"未出力の項目: なし"* ]] || echo "警告: $f の最終行: $l" >&2
    done
    { echo "# 判定用ルールブック（$BOOK）"; echo; cat "$OUT/rulebook1.txt"; echo; cat "$OUT/rulebook2.txt"; } >"$OUT/判定用ルールブック.md"
    add_source "判定用ルールブック" "$OUT/判定用ルールブック.md" || exit 1
    echo "完了: 判定用ルールブック（$OUT/判定用ルールブック.md、$(wc -m <"$OUT/判定用ルールブック.md")文字）"
    ;;
  verify)
    ids=$(ids_matching '^([0-9][0-9]_|判定用ルールブック$)')
    chat "$OUT/照合結果.md" "$ids" "$PROMPTS/3_照合.txt" || exit 1
    cat "$OUT/照合結果.md"
    ;;
  table)
    ids=$(ids_matching '^判定用ルールブック$')
    [[ -n "$ids" ]] || { echo "判定用ルールブックがありません。先に rulebook を実行してください" >&2; exit 1; }
    fill "$PROMPTS/4_ルール表.txt" "BOOK=$BOOK" >"$OUT/table.prompt"
    chat "$OUT/ルール表.md" "$ids" "$OUT/table.prompt" || exit 1
    echo "完了: $OUT/ルール表.md（$(grep -c '^|' "$OUT/ルール表.md")行）"
    ;;
  *)
    echo "フェーズは chapters / rulebook / verify / table のいずれかを指定してください" >&2; exit 2 ;;
esac
