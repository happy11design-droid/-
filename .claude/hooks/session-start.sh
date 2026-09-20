#!/bin/bash
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

if ! command -v nlm >/dev/null 2>&1; then
  go install github.com/tmc/nlm/cmd/nlm@latest
fi

# VPS (方式B) 経由でNotebookLMを操作するには、chromedpのデフォルト
# modifyURL（HTTP /json/version 参照 + IPホスト書き換え）をスキップする
# パッチ版nlmが必要（Basic認証や独自ドメインTLS証明書と両立させるため）。
NLM_PATCHED_MARKER="$(go env GOPATH)/bin/nlm-vps-patched.marker"
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

GOBIN="$(go env GOPATH)/bin"
echo "export PATH=\"$GOBIN:\$PATH\"" >> "$CLAUDE_ENV_FILE"

if [ -z "${NLM_AUTH_TOKEN:-}" ] || [ -z "${NLM_COOKIES:-}" ]; then
  echo "[session-start] 警告: NLM_AUTH_TOKEN / NLM_COOKIES が未設定です。" >&2
fi
