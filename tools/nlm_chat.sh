#!/usr/bin/env bash
# NotebookLMへの1回の質問（nlm generate-chat）を、新しいnlm（2026-09-28〜、chromedp更新版）の終了コードに合わせて扱う共通関数。
# 各スクリプトから `source "$ROOT/tools/nlm_chat.sh"` して使う。
#
#   nlm_chat <ノートブックID> <プロンプトファイル> <回答ファイル> <エラーファイル> [generate-chat の追加オプション...]
#     例: nlm_chat "$id" "$PROMPT" "$out" "$err" --web
#   成功で 0。失敗すると 0 以外（回答ファイルは空か途中まで）。
#
# - exit 8（stale-output）: 回答が流れている途中で書き直された。正しい回答は会話に保存されているので、
#   `nlm chat show` から [ASSISTANT] 以降を取り出して回答ファイルにする。
# - exit 3（認証切れ）: `チャート分析.txt` 手順Aで再認証し、1回だけ送り直す。

nlm_load_env() {
  [[ -f /root/.nlm/env ]] || return 0
  local key value
  while IFS='=' read -r key value; do
    [[ "$key" == NLM_* ]] || continue
    value="${value#\"}"; value="${value%\"}"
    export "$key=$value"
  done < /root/.nlm/env
}

# 並行して動く他の質問と重ならないようロックする。ロックを待つ間に別の質問が更新していればそれを使う
nlm_reauth() {
  [[ -n "${NLM_VPS_CDP_BASE:-}" ]] || return 1
  local mark="$1"
  (
    flock -w 300 9 || exit 1
    if [[ -n "$mark" && /root/.nlm/env -nt "$mark" ]]; then exit 0; fi
    http="${NLM_VPS_CDP_BASE/wss:/https:}"
    uuid=$(curl -sS -m 30 "$http/json/version" | grep -oE '/devtools/browser/[a-f0-9-]+' | head -1 | sed 's#/devtools/browser/##')
    [[ -n "$uuid" ]] && timeout 150 nlm auth -cdp-url "${NLM_VPS_CDP_BASE}/devtools/browser/${uuid}" >/dev/null 2>&1
  ) 9>/tmp/nlm-reauth.lock
  nlm_load_env
}

nlm_chat() {
  local nb="$1" prompt="$2" out="$3" err="$4"; shift 4
  local try rc conv
  for try in 1 2; do
    rc=0
    nlm generate-chat --citations off "$@" --prompt-file "$prompt" "$nb" >"$out" 2>"$err" || rc=$?
    if [[ $rc -eq 8 ]]; then
      conv=$(grep -oE "chat show $nb [0-9a-f-]+" "$err" | tail -1 | awk '{print $4}')
      if [[ -n "$conv" ]] && nlm chat show --citations off "$nb" "$conv" 2>/dev/null | awk 'f; /^\[ASSISTANT\]$/ {f = 1}' >"$out.show" && [[ -s "$out.show" ]]; then
        mv "$out.show" "$out"
        rc=0
      fi
      rm -f "$out.show"
    fi
    if [[ $rc -eq 3 && $try -eq 1 ]]; then
      touch "$out.authmark"
      nlm_reauth "$out.authmark"
      rm -f "$out.authmark"
      continue
    fi
    break
  done
  [[ $rc -eq 0 && -s "$out" ]]
}
