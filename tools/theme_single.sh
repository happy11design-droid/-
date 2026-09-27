#!/usr/bin/env bash
# 指定した1銘柄を新分析ツールの著者（ボリンジャー・ミネルヴィニ・ワインスタイン）に分析させる（`新分析ツール/テーマ監視_手順書.md` 2-4）
#
# 使い方:
#   tools/theme_single.sh prepare <ティッカー> <作業ディレクトリ> [--hold <買値> <買った日> <ルール>]
#       採用ルールへの当てはめ（rules.md）と数値データ（<ティッカー>_data.txt）を作る。
#   （ここでメインが、`新分析ツール/ニュース調査指示.md` を読ませた単一のサブエージェントに <作業ディレクトリ>/news.md を書かせる）
#   tools/theme_single.sh send <ティッカー> <作業ディレクトリ>
#       チャート画像（日足・分足）を3冊のノートブックに差し替えてから3人の著者へ並列に送り（回答後に画像は外す）、回答を <作業ディレクトリ>/answers/ に書き出して全文を表示する。
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CMD="${1:-}"; T="${2:-}"; D="${3:-}"
[[ -n "$CMD" && -n "$T" && -n "$D" ]] || { sed -n '2,10p' "$0"; exit 2; }
T="${T^^}"
mkdir -p "$D"

if [[ "$CMD" == prepare ]]; then
  shift 3
  python3 "$ROOT/tools/theme_single.py" "$T" "$D/rules.md" "$@" > /dev/null
  python3 "$ROOT/tools/market_data.py" ticker "$T" "$D" > /dev/null 2>&1 || echo "数値データ（market_data）を取得できませんでした" >&2
  echo "rules: $D/rules.md"
  echo "data: $D/${T}_data.txt"
  exit 0
fi
[[ "$CMD" == send ]] || { echo "prepare か send を指定してください" >&2; exit 2; }

if [[ -f /root/.nlm/env ]]; then   # Cookie値に `$` が含まれるため source は使わない
  while IFS='=' read -r key value; do
    [[ "$key" == NLM_* ]] || continue
    value="${value#\"}"; value="${value%\"}"
    export "$key=$value"
  done < /root/.nlm/env
fi

python3 - "$D" "$T" "$ROOT/新分析ツール/個別分析_送信プロンプト雛形.txt" <<'PY'
import os, sys
d, t, tpl = sys.argv[1:4]
rules = open(os.path.join(d, "rules.md"), encoding="utf-8").read().strip()
data = ""
p = os.path.join(d, f"{t}_data.txt")
if os.path.exists(p):
    data = open(p, encoding="utf-8").read().strip()
n = os.path.join(d, "news.md")
data += "\n\nニュース（サブエージェントの調査）:\n" + (open(n, encoding="utf-8").read().strip() if os.path.exists(n) else "調査なし")
out = open(tpl, encoding="utf-8").read().replace("{{RULES}}", rules).replace("{{DATA}}", data)
if len(out) > 12000:
    out = out[:12000]
open(os.path.join(d, "prompt.txt"), "w", encoding="utf-8").write(out)
PY

mkdir -p "$D/answers"
declare -A NB=([ボリンジャー]=3dc5edc5-7808-438c-abf0-9c0e5ca6cef9 [ミネルヴィニ]=e09b765e-4f20-496a-ae2f-6d991c488d0d [ワインスタイン]=69875bdb-8d0d-474e-9b1a-c6c1b7bc82a1)
# チャート画像（日足・直近の分足。prepare の market_data.py が作る）をノートブックのソースに差し替える。
# 既存ツールの tools/run_notebooks.sh と同じ方法: 画像拡張子のソースだけを削除し、新しい画像を追加する（本のソースには触れない）。
IMAGES=()
for f in "$D/${T}_chart.png" "$D/${T}_intraday.png"; do [[ -f "$f" ]] && IMAGES+=("$f"); done
del_images() {   # $1 = ノートブックID。画像拡張子で終わるソースを1回でまとめて削除（-y は必須）
  local ids
  ids=$(nlm source list "$1" 2>&1 | awk -F'\t' 'NR>1 && tolower($2) ~ /\.(png|jpg|jpeg)$/ {print $1}' | paste -sd, -)
  [[ -z "$ids" ]] || nlm source delete -y "$1" "$ids" > /dev/null 2>&1
}

PIDS=()
for k in ボリンジャー ミネルヴィニ ワインスタイン; do
  ( del_images "${NB[$k]}" || true
    if [[ ${#IMAGES[@]} -gt 0 ]] && ! nlm source add "${NB[$k]}" "${IMAGES[@]}" > "$D/answers/$k.img" 2>&1; then
      echo "（チャート画像を追加できませんでした: $(tail -1 "$D/answers/$k.img")）" > "$D/answers/$k.imgerr"
    fi
    nlm generate-chat --citations off --prompt-file "$D/prompt.txt" "${NB[$k]}" > "$D/answers/$k.txt" 2> "$D/answers/$k.err" \
      || echo "送信に失敗: $(tail -1 "$D/answers/$k.err")" >> "$D/answers/$k.txt"
    # 毎朝のRoutine（テキストのみ）がこの銘柄の図を見て別の銘柄を判定しないよう、回答後に画像を外す
    del_images "${NB[$k]}" || true ) &
  PIDS+=($!)
done
for p in "${PIDS[@]}"; do wait "$p" || true; done
for k in ボリンジャー ミネルヴィニ ワインスタイン; do
  echo "===== $k ====="
  [[ -f "$D/answers/$k.imgerr" ]] && cat "$D/answers/$k.imgerr"
  cat "$D/answers/$k.txt"
  echo
done
