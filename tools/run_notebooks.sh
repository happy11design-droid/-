#!/usr/bin/env bash
# NotebookLM 一括処理スクリプト（`チャート分析.txt` 手順5 および 手順9 用）
#
# 対象ノートブックは `nlm notebook list` のタイトルに "Claude" を含む全件（大文字小文字は問わない）。
# 全件を並列実行するため、所要時間は最も遅い1件とほぼ同じになる。
#
# 使い方:
#   画像の差し替え（手順5-1・5-2。データ収集の完了を待たずに先行実行してよい）
#     tools/run_notebooks.sh --phase images --image <画像パス> [--image <画像パス2> ...] [--exclude <正規表現>]
#
#   プロンプト送信と回答取得（手順5-3・5-4 / 手順9-2）
#     tools/run_notebooks.sh --phase chat --prompt <プロンプトファイル> --out <出力ディレクトリ> [--exclude <正規表現>]
#
# 送信は常に `nlm generate-chat --web` で行う。--web はサーバー側の会話を使うため、
# やり取りがNotebookLMの画面に履歴として残り、ユーザーが後からUIで追加の依頼（図解画像の生成など）をできる。
#
# --only には対象を絞り込むノートブック名の拡張正規表現、--exclude には除外する正規表現を渡す（手順0の段階分析用）。
#   段階1: --only '株価チャート分析|マット・ペトラリア|テクニカル分析 最強の組み合わせ術'
#   段階2: --exclude '株価チャート分析|マット・ペトラリア|テクニカル分析 最強の組み合わせ術'
#
# --phase chat は各ノートブックの回答を <出力ディレクトリ>/<ノートブック名>.txt へ保存し、
# 全件完了後に「=== ノートブック名 ===」の見出し付きで標準出力へまとめて出力する。
# 失敗したノートブックは回答の代わりにエラー内容を出力するため、取りこぼしに気づける。

set -uo pipefail

PHASE=""
PROMPT=""
OUTDIR=""
EXCLUDE=""
ONLY=""
IMAGES=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --phase)    PHASE="${2:-}"; shift 2 ;;
    --prompt)   PROMPT="${2:-}"; shift 2 ;;
    --out)      OUTDIR="${2:-}"; shift 2 ;;
    --exclude)  EXCLUDE="${2:-}"; shift 2 ;;
    --only)     ONLY="${2:-}"; shift 2 ;;
    --image)    IMAGES+=("${2:-}"); shift 2 ;;
    *) echo "不明な引数: $1" >&2; exit 2 ;;
  esac
done

case "$PHASE" in
  images)
    [[ ${#IMAGES[@]} -gt 0 ]] || { echo "--phase images には --image が必要です" >&2; exit 2; }
    ;;
  chat)
    [[ -n "$PROMPT" && -n "$OUTDIR" ]] || { echo "--phase chat には --prompt と --out が必要です" >&2; exit 2; }
    [[ -f "$PROMPT" ]] || { echo "プロンプトファイルが見つかりません: $PROMPT" >&2; exit 2; }
    mkdir -p "$OUTDIR"
    ;;
  *)
    echo "--phase は images または chat を指定してください" >&2; exit 2 ;;
esac

# 認証情報の読み込み（`nlm auth -cdp-url ...` が書き出した内容。手順Aを参照）
# Cookie値に `$` が含まれるため `source` は使わない（シェルが変数展開しようとして失敗する）。
if [[ -f /root/.nlm/env ]]; then
  while IFS='=' read -r key value; do
    [[ "$key" == NLM_* ]] || continue
    value="${value#\"}"; value="${value%\"}"   # 値は二重引用符で囲まれている
    export "$key=$value"
  done < /root/.nlm/env
fi

LIST=$(nlm notebook list) || {
  echo "nlm notebook list に失敗しました。手順Aの再認証を実行してください。" >&2; exit 1; }

# ID<TAB>TITLE の行を取り出す（1行目はヘッダ）
mapfile -t ROWS < <(printf '%s\n' "$LIST" | awk -F'\t' 'NR>1 && tolower($2) ~ /claude/ {print $1"\t"$2}')

if [[ -n "$ONLY" ]]; then
  KEPT=()
  for row in "${ROWS[@]}"; do
    title="${row#*$'\t'}"
    [[ "$title" =~ $ONLY ]] && KEPT+=("$row")
  done
  ROWS=("${KEPT[@]}")
fi

if [[ -n "$EXCLUDE" ]]; then
  KEPT=()
  for row in "${ROWS[@]}"; do
    title="${row#*$'\t'}"
    [[ "$title" =~ $EXCLUDE ]] || KEPT+=("$row")
  done
  ROWS=("${KEPT[@]}")
fi

[[ ${#ROWS[@]} -gt 0 ]] || { echo "対象ノートブックが0件です（--only / --exclude の指定を確認してください）" >&2; exit 1; }

# 既存の画像ソースを削除し、新しい画像を追加する（テキスト等の非画像ソースには触れない）
swap_images() {
  local id="$1" title="$2" sources ids out

  sources=$(nlm source list "$id" 2>&1) || {
    echo "[$title] ソース一覧の取得に失敗: $sources" >&2; return 1; }

  # 削除対象はTITLEが画像拡張子で終わるソースのみ。複数まとめて1回で削除する。
  # `-y` は必須（端末がない環境では確認プロンプトで止まり、削除されないまま画像が重複する）。
  ids=$(printf '%s\n' "$sources" | awk -F'\t' 'NR>1 && tolower($2) ~ /\.(png|jpg|jpeg)$/ {print $1}' | paste -sd, -)
  if [[ -n "$ids" ]]; then
    out=$(nlm source delete -y "$id" "$ids" 2>&1) || {
      echo "[$title] 既存画像の削除に失敗: $out" >&2; return 1; }
  fi

  out=$(nlm source add "$id" "${IMAGES[@]}" 2>&1) || {
    echo "[$title] 画像の追加に失敗: $out" >&2; return 1; }
}

# プロンプトを送信し、回答をファイルへ保存する
run_chat() {
  local id="$1" title="$2"
  local out="$OUTDIR/${title//\//_}.txt"
  local err="$out.err"
  # --web は「サーバー側の最新の会話を使う」。これを付けないと generate-chat は one-shot 扱いとなり、
  # やり取りが手元にしか残らず、NotebookLMの画面には履歴が一切現れない（2026-09-22に実際に発生）。
  # ユーザーが後からUIで「直前の判定を図解して」等と追加依頼できるよう、常に付けること。
  if ! nlm generate-chat --citations off --web --prompt-file "$PROMPT" "$id" >"$out" 2>"$err"; then
    { echo "【エラー: 回答を取得できませんでした】"; cat "$err"; } >"$out"
  fi
  rm -f "$err"
}

PIDS=()
TITLES=()
for row in "${ROWS[@]}"; do
  id="${row%%$'\t'*}"
  title="${row#*$'\t'}"
  if [[ "$PHASE" == "images" ]]; then
    swap_images "$id" "$title" &
  else
    run_chat "$id" "$title" &
  fi
  PIDS+=("$!")
  TITLES+=("$title")
done

# 失敗を握り潰さない。1件でも失敗したら最後に非ゼロで終了し、どのノートブックかを明示する。
FAILED=0
for i in "${!PIDS[@]}"; do
  if ! wait "${PIDS[$i]}"; then
    echo "失敗: ${TITLES[$i]}" >&2
    FAILED=$((FAILED + 1))
  fi
done

if [[ "$PHASE" == "images" ]]; then
  if (( FAILED > 0 )); then
    echo "画像の差し替えに失敗したノートブックが ${FAILED} 件あります（対象 ${#ROWS[@]} 件）" >&2
    exit 1
  fi
  echo "画像の差し替えが完了しました（対象 ${#ROWS[@]} 件）"
  exit 0
fi

for row in "${ROWS[@]}"; do
  title="${row#*$'\t'}"
  echo "=== ${title} ==="
  cat "$OUTDIR/${title//\//_}.txt"
  echo
done

# 回答が取得できなかったノートブックがある場合、手順5-4で黙って表示から漏らさないよう非ゼロで終了する
(( FAILED == 0 )) || exit 1
