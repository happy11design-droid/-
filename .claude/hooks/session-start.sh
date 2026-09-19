#!/bin/bash
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

if ! command -v nlm >/dev/null 2>&1; then
  go install github.com/tmc/nlm/cmd/nlm@latest
fi

GOBIN="$(go env GOPATH)/bin"
echo "export PATH=\"$GOBIN:\$PATH\"" >> "$CLAUDE_ENV_FILE"

if [ -z "${NLM_AUTH_TOKEN:-}" ] || [ -z "${NLM_COOKIES:-}" ]; then
  echo "[session-start] 警告: NLM_AUTH_TOKEN / NLM_COOKIES が未設定です。" >&2
fi
