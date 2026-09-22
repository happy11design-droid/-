#!/usr/bin/env bash
# 送信プロンプトの組み立て（`チャート分析.txt` 手順5-3 用）
#
# `送信プロンプト雛形.txt` の {{FUNDAMENTALS}} と {{ECONOMIC_DATA}} を、
# 手順3・手順2で取得したデータで置き換えたプロンプトファイルを生成する。
# 雛形の他の文言は一切変更されないため、手作業での転記ミスが起こらない。
#
# 使い方:
#   tools/build_prompt.sh <ファンダメンタルズ情報のファイル> <経済指標・市場データのファイル> <出力先>
#
# 証券コードの指定がない依頼では、ファンダメンタルズ情報のファイルに「特になし」とだけ書く。

set -euo pipefail

if [[ $# -ne 3 ]]; then
  echo "使い方: tools/build_prompt.sh <ファンダメンタルズ情報ファイル> <経済指標ファイル> <出力先>" >&2
  exit 2
fi

FUNDAMENTALS="$1"
ECONOMIC="$2"
OUT="$3"
TEMPLATE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/送信プロンプト雛形.txt"
[[ -f "$TEMPLATE" ]] || { echo "雛形が見つかりません: $TEMPLATE" >&2; exit 1; }

export FUNDAMENTALS ECONOMIC OUT TEMPLATE
python3 - <<'PY'
import os

def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read().strip()

template = read(os.environ["TEMPLATE"])
for marker, path in (("{{FUNDAMENTALS}}", os.environ["FUNDAMENTALS"]),
                     ("{{ECONOMIC_DATA}}", os.environ["ECONOMIC"])):
    if marker not in template:
        raise SystemExit(f"雛形に {marker} が見つかりません")
    template = template.replace(marker, read(path))

with open(os.environ["OUT"], "w", encoding="utf-8") as f:
    f.write(template + "\n")
PY

echo "プロンプトを生成しました: $OUT"
