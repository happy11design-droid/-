#!/usr/bin/env bash
# 銘柄メモ（過去の調査結果のキャッシュ）の読み書き（`チャート分析.txt` 手順1・手順5-3の後）
#
# 過去の急騰・急落の原因や決算のBeat/Miss実績は後から変わらないため、銘柄ごとに保存して次回以降は
# 新しい日付・新しい四半期だけを調べる。保存先はデータ用ブランチの `銘柄メモ/<ティッカー>.md`。
# どのセッション（手動の分析・Routine）からも同じ場所を読み書きできるよう、作業ブランチではなくこのブランチに置く。
#
# 使い方:
#   tools/research_cache.sh get <ティッカー> <出力ファイル>   # なければ出力ファイルを作らず終了コード1
#   tools/research_cache.sh put <ティッカー> <入力ファイル>   # データ用ブランチへコミット・プッシュ

set -uo pipefail

BRANCH="claude/ecstatic-tesla-660dhs"
MODE="${1:-}"; TICKER="$(echo "${2:-}" | tr '[:lower:]' '[:upper:]')"; FILE="${3:-}"
[[ -n "$MODE" && -n "$TICKER" && -n "$FILE" ]] || { sed -n '2,10p' "$0" >&2; exit 2; }
cd "$(dirname "${BASH_SOURCE[0]}")/.."
PATH_IN_REPO="銘柄メモ/${TICKER}.md"

case "$MODE" in
  get)
    git fetch -q origin "$BRANCH" 2>/dev/null
    if git show "origin/${BRANCH}:${PATH_IN_REPO}" > "$FILE" 2>/dev/null; then
      echo "銘柄メモあり: $FILE"
    else
      rm -f "$FILE"; echo "銘柄メモなし（${TICKER}は初回）"; exit 1
    fi
    ;;
  put)
    [[ -f "$FILE" ]] || { echo "入力ファイルがありません: $FILE" >&2; exit 2; }
    SRC="$(cd "$(dirname "$FILE")" && pwd)/$(basename "$FILE")"
    # 天気予報Routineが同じブランチへ同時にプッシュする可能性があるため、失敗したら取り直して再試行する
    for attempt in 1 2 3; do
      git fetch -q origin "$BRANCH" || { sleep $((attempt * 2)); continue; }
      TMP="$(mktemp -d)"
      git worktree add -q --detach "$TMP" "origin/${BRANCH}" || { rm -rf "$TMP"; exit 1; }
      mkdir -p "$TMP/銘柄メモ"
      cp "$SRC" "$TMP/$PATH_IN_REPO"
      git -C "$TMP" add "$PATH_IN_REPO"
      if git -C "$TMP" diff --cached --quiet; then
        echo "銘柄メモに変更なし: $PATH_IN_REPO"; git worktree remove --force "$TMP"; exit 0
      fi
      git -C "$TMP" commit -q -m "銘柄メモ ${TICKER} を更新"
      if git -C "$TMP" push -q origin "HEAD:${BRANCH}"; then
        echo "銘柄メモを保存: ${BRANCH}:${PATH_IN_REPO}（$(git -C "$TMP" rev-parse --short HEAD)）"
        git worktree remove --force "$TMP"; exit 0
      fi
      git worktree remove --force "$TMP"; sleep $((attempt * 2))
    done
    echo "銘柄メモのプッシュに3回失敗しました" >&2; exit 1
    ;;
  *) echo "get または put を指定してください" >&2; exit 2 ;;
esac
