#!/usr/bin/env python3
"""画像フォルダを Claude API で一括OCRする

使い方:
  pip install anthropic pillow          # 初回のみ
  export ANTHROPIC_API_KEY=sk-ant-...   # APIキー
  python3 tools/ocr.py <画像フォルダ> [--out 出力フォルダ] [--workers 5] [--effort medium]

出力（既定は <画像フォルダ>/ocr_output/）:
  <画像名>.md   … 画像ごとの読み取り結果
  all.md        … 全画像の結果をファイル名順につないだもの
  failed.txt    … 失敗した画像の一覧（失敗がなければ作られない）

途中で止まったり一部が失敗したりしても、同じコマンドをもう一度実行すれば、
結果が既にある画像は飛ばして残りだけを処理する（--force で全部やり直す）。
ファイル名は 001.png, 002.png … のように連番にしておくと all.md の並び順が崩れない。
"""
import argparse
import base64
import io
import re
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import anthropic

MODEL = "claude-opus-5"
EXTS = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".webp": "image/webp", ".gif": "image/gif"}
MAX_BYTES = 5 * 1024 * 1024   # API の1画像あたりの上限
MAX_EDGE = 7900               # API の長辺上限（8000px）より少し小さく

SYSTEM = """あなたはOCRエンジンです。渡された画像に写っている文字を、一字一句そのまま書き起こしてください。

- 要約・言い換え・誤字の修正・補足説明をしない。画像にある文字だけを出力する。
- 見出し・段落・箇条書き・改行はできるだけ元のレイアウトどおりに再現する。
- 表は Markdown の表にする。数値・単位・記号・桁区切りは画像のまま写す。
- 縦書きは読む順に横書きへ直す。段組みは左の段（縦書きなら右の段）から順に書く。
- 読めない文字は [判読不能] と書く。推測で埋めない。
- 文字がない画像には「（文字なし）」とだけ書く。
- 前置きや「以下が書き起こしです」のような文は付けない。"""


def natural_key(p: Path):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", p.name)]


def load_image(path: Path):
    """画像を API に送れる形（media_type, base64）にする。上限を超える場合だけ縮小する。"""
    data = path.read_bytes()
    media_type = EXTS[path.suffix.lower()]
    try:
        from PIL import Image
    except ImportError:
        if len(data) > MAX_BYTES:
            raise RuntimeError("5MBを超えています。pip install pillow すると自動で縮小します")
        return media_type, base64.standard_b64encode(data).decode()

    img = Image.open(io.BytesIO(data))
    if len(data) <= MAX_BYTES and max(img.size) <= MAX_EDGE:
        return media_type, base64.standard_b64encode(data).decode()
    img = img.convert("RGB")
    if max(img.size) > MAX_EDGE:
        img.thumbnail((MAX_EDGE, MAX_EDGE))
    for quality in (92, 85, 75, 65):
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=quality)
        if buf.tell() <= MAX_BYTES:
            return "image/jpeg", base64.standard_b64encode(buf.getvalue()).decode()
        img.thumbnail((int(img.width * 0.8), int(img.height * 0.8)))
    raise RuntimeError("縮小しても5MB以下にできませんでした")


def ocr_one(client, path: Path, effort: str) -> str:
    media_type, b64 = load_image(path)
    response = client.beta.messages.create(
        model=MODEL,
        max_tokens=16000,
        system=SYSTEM,
        output_config={"effort": effort},
        # 安全フィルタの誤判定で断られた場合、API側で別モデルに自動で回す
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        messages=[{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": b64}},
            {"type": "text", "text": "この画像の文字を書き起こしてください。"},
        ]}],
    )
    if response.stop_reason == "refusal":
        raise RuntimeError("APIが処理を断りました（refusal）")
    if response.stop_reason == "max_tokens":
        raise RuntimeError("出力が長すぎて途中で切れました。画像を分割してください")
    text = "".join(b.text for b in response.content if b.type == "text").strip()
    if not text:
        raise RuntimeError("結果が空でした")
    return text


def main():
    ap = argparse.ArgumentParser(description="画像フォルダを Claude API で一括OCRする")
    ap.add_argument("input", type=Path, help="画像が入ったフォルダ")
    ap.add_argument("--out", type=Path, help="出力フォルダ（既定: <画像フォルダ>/ocr_output）")
    ap.add_argument("--workers", type=int, default=5, help="同時に処理する枚数（既定: 5）")
    ap.add_argument("--effort", default="medium", choices=["low", "medium", "high", "xhigh", "max"],
                    help="読み取りの丁寧さ。上げるほど遅く高くなる（既定: medium）")
    ap.add_argument("--force", action="store_true", help="結果が既にある画像もやり直す")
    args = ap.parse_args()

    if not args.input.is_dir():
        sys.exit(f"フォルダが見つかりません: {args.input}")
    out = args.out or args.input / "ocr_output"
    out.mkdir(parents=True, exist_ok=True)

    images = sorted((p for p in args.input.iterdir() if p.suffix.lower() in EXTS), key=natural_key)
    skipped = [p for p in args.input.iterdir() if p.suffix.lower() in {".heic", ".heif", ".tif", ".tiff", ".bmp"}]
    if skipped:
        print(f"※ 対応していない形式のため飛ばします（JPEGかPNGに変換してください）: {', '.join(p.name for p in skipped)}")
    if not images:
        sys.exit(f"画像がありません（対応形式: {', '.join(EXTS)}）: {args.input}")

    todo = [p for p in images if args.force or not (out / f"{p.stem}.md").exists()]
    print(f"画像 {len(images)} 枚 / 今回処理 {len(todo)} 枚 / 出力先 {out}")

    client = anthropic.Anthropic(max_retries=5)
    failed, lock, done = {}, threading.Lock(), 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(ocr_one, client, p, args.effort): p for p in todo}
        for fut in as_completed(futures):
            p = futures[fut]
            try:
                (out / f"{p.stem}.md").write_text(fut.result() + "\n", encoding="utf-8")
                status = "OK"
            except anthropic.AuthenticationError:
                pool.shutdown(cancel_futures=True)
                sys.exit("APIキーが無効です。ANTHROPIC_API_KEY を確認してください")
            except (anthropic.APIError, RuntimeError, OSError) as e:
                failed[p.name] = str(e)
                status = f"失敗: {e}"
            with lock:
                done += 1
                print(f"[{done}/{len(todo)}] {p.name} {status}", flush=True)

    parts = []
    for p in images:
        md = out / f"{p.stem}.md"
        body = md.read_text(encoding="utf-8").strip() if md.exists() else "（未処理または失敗）"
        parts.append(f"## {p.name}\n\n{body}\n")
    (out / "all.md").write_text("\n".join(parts), encoding="utf-8")

    fail_file = out / "failed.txt"
    if failed:
        fail_file.write_text("".join(f"{n}\t{e}\n" for n, e in sorted(failed.items())), encoding="utf-8")
        print(f"\n完了（失敗 {len(failed)} 枚。同じコマンドをもう一度実行すると失敗分だけ再処理します）: {fail_file}")
    else:
        fail_file.unlink(missing_ok=True)
        print(f"\n完了: {out / 'all.md'}")


if __name__ == "__main__":
    main()
