#!/usr/bin/env python3
"""ページごとの.txtを、ページ番号入りの章ごとの.mdに結合する。

使い方:
    python3 merge_chapters.py <ページtxtのフォルダ> <章リスト.txt> <出力フォルダ>

章リスト.txt は1行に「開始ページ 章タイトル」（ページはファイル名の番号）:
    1 はじめに
    15 第1章 〇〇〇〇
"""
import re
import sys
from pathlib import Path


def read(p):
    for enc in ("utf-8-sig", "cp932"):
        try:
            return p.read_text(encoding=enc)
        except UnicodeDecodeError:
            pass
    return p.read_text(encoding="utf-8", errors="replace")


def page_no(p):
    nums = re.findall(r"\d+", p.stem)
    if not nums:
        sys.exit(f"ファイル名からページ番号が読み取れません: {p.name}")
    return int(nums[-1])


src, toc, out = map(Path, sys.argv[1:4])
pages = sorted(src.glob("*.txt"), key=page_no)
chapters = sorted((int(s), t.strip()) for s, t in
                  (l.split(maxsplit=1) for l in read(toc).splitlines() if l.strip()))
out.mkdir(parents=True, exist_ok=True)
for i, (start, title) in enumerate(chapters):
    end = chapters[i + 1][0] if i + 1 < len(chapters) else float("inf")
    body = [f"<!-- p.{page_no(p)} -->\n{read(p).strip()}\n" for p in pages if start <= page_no(p) < end]
    safe = re.sub(r'[\\/:*?"<>|]', "_", title)
    name = f"{i + 1:02d}_{safe}.md"
    (out / name).write_text(f"# {title}\n\n" + "\n".join(body), encoding="utf-8")
    print(f"{name}: p.{start}〜 {len(body)}ページ")
missing = [p.name for p in pages if page_no(p) < chapters[0][0]]
if missing:
    print(f"注意: 最初の章より前のページ {len(missing)}件は含まれていません")
