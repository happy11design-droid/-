#!/bin/bash
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# GOBINを先にこのスクリプト自身のPATHへ反映しておく。これをせずに
# command -v nlm を評価すると、過去のセッションで既にインストール済み
# でも「見つからない」と誤判定し、毎回 go install で無印版に上書きして
# しまう（パッチ版が居座っているように見えて実は消えている、というバグ
# の原因だった）。
GOBIN="$(go env GOPATH)/bin"
export PATH="$GOBIN:$PATH"
echo "export PATH=\"$GOBIN:\$PATH\"" >> "$CLAUDE_ENV_FILE"

NLM_PATCHED_MARKER="$GOBIN/nlm-vps-patched.marker"

if [ ! -f "$NLM_PATCHED_MARKER" ] && ! command -v nlm >/dev/null 2>&1; then
  go install github.com/tmc/nlm/cmd/nlm@latest
fi

# VPS (方式B) 経由でNotebookLMを操作するには、chromedpのデフォルト
# modifyURL（HTTP /json/version 参照 + IPホスト書き換え）をスキップする
# パッチ版nlmが必要（Basic認証や独自ドメインTLS証明書と両立させるため）。
if [ ! -f "$NLM_PATCHED_MARKER" ]; then
  NLM_BUILD_DIR="$(mktemp -d)"
  if git clone --depth 1 https://github.com/tmc/nlm.git "$NLM_BUILD_DIR" >/dev/null 2>&1; then
    if git -C "$NLM_BUILD_DIR" apply "$(dirname "${BASH_SOURCE[0]}")/../../tools/nlm-nomodifyurl.patch" 2>/dev/null; then
      if (cd "$NLM_BUILD_DIR" && go build -o "$(go env GOPATH)/bin/nlm" ./cmd/nlm) 2>/dev/null; then
        touch "$NLM_PATCHED_MARKER"
        echo "[session-start] パッチ版nlm（VPS対応）をビルドしました。" >&2
      else
        echo "[session-start] 警告: パッチ版nlmのビルドに失敗しました。標準版を使用します。" >&2
      fi
    else
      echo "[session-start] 警告: nlmパッチの適用に失敗しました。標準版を使用します。" >&2
    fi
  else
    echo "[session-start] 警告: nlmソースのクローンに失敗しました。標準版を使用します。" >&2
  fi
  rm -rf "$NLM_BUILD_DIR"
fi

if [ -z "${NLM_AUTH_TOKEN:-}" ] || [ -z "${NLM_COOKIES:-}" ]; then
  echo "[session-start] 警告: NLM_AUTH_TOKEN / NLM_COOKIES が未設定です。" >&2
fi
