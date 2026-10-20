#!/usr/bin/env python3
"""恩株ツールの scan.md（tools/onkabu_scan.py の出力）を、アーティファクト用のHTMLに変換する。

使い方: python3 tools/onkabu_page.py scan.md page.html
内容は scan.md の文言をそのまま整形するだけで、判断や要約は加えない。
"""
import html
import re
import sys


def inline(text):
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    return text


def parse(md):
    """見出しごとのブロックに分ける。戻り値: (title, [(heading, [lines])])"""
    title, sections, cur = "", [], None
    for line in md.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
        elif line.startswith("## "):
            cur = (line[3:].strip(), [])
            sections.append(cur)
        else:
            if cur is None:
                cur = ("", [])
                sections.append(cur)
            cur[1].append(line)
    return title, sections


def render_lines(lines):
    out, i = [], 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            head, body = rows[0], rows[1:]
            t = ["<div class='scroll'><table><thead><tr>"]
            t += [f"<th>{inline(c)}</th>" for c in head]
            t.append("</tr></thead><tbody>")
            for r in body:
                t.append("<tr>")
                for n, c in enumerate(r):
                    t.append(f"<{'th scope=row' if n == 0 else 'td'}>{inline(c)}</{'th' if n == 0 else 'td'}>")
                t.append("</tr>")
            t.append("</tbody></table></div>")
            out.append("".join(t))
            continue
        if line.startswith("- "):
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append(f"<li>{inline(lines[i][2:])}</li>")
                i += 1
            out.append("<ul>" + "".join(items) + "</ul>")
            continue
        if line.strip():
            out.append(f"<p>{inline(line)}</p>")
        i += 1
    return "\n".join(out)


def main(src, dst):
    md = open(src, encoding="utf-8").read()
    title, sections = parse(md)
    date = re.search(r"（(\d{4}-\d{2}-\d{2})", title)
    asof = date.group(1) if date else ""

    signal_n, held_text, rules, rest = None, "", "", []
    signal_body = held_body = ""
    for head, lines in sections:
        if head.startswith("1."):
            m = re.search(r"（(\d+)銘柄）", head)
            signal_n = int(m.group(1)) if m else None
            signal_body = render_lines(lines)
        elif head.startswith("2."):
            held_text = " ".join(l for l in lines if l.strip())
            held_body = render_lines(lines)
        elif head == "":
            rules = render_lines(lines)
        else:
            rest.append((head, render_lines(lines)))

    if signal_n is None:
        status, state = "合図の件数を読み取れませんでした", "unknown"
    elif signal_n == 0:
        status, state = "今日の合図: 0銘柄", "none"
    else:
        status, state = f"今日の合図: {signal_n}銘柄", "hit"

    parts = [f"""<title>恩株ツール 毎朝の通知</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
/* 上に結論、下に全文。数字は等幅で縦にそろえる */
:root {{
  --bg: #f3f5f7; --surface: #ffffff; --ink: #1b2430; --muted: #5d6b7a; --line: #d9e0e7;
  --hit: #b45309; --hit-bg: #fdf0dc; --none: #2f6f5e; --none-bg: #e3f1ec;
  --sans: "Noto Sans JP", "Hiragino Sans", "Yu Gothic", sans-serif;
  --mono: "IBM Plex Mono", ui-monospace, Menlo, monospace;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg: #11171e; --surface: #19212b; --ink: #e6ebf0; --muted: #93a1b0; --line: #2b3745;
  --hit: #f2b25c; --hit-bg: #3a2a12; --none: #7ccbb2; --none-bg: #16322b; color-scheme: dark; }} }}
:root[data-theme="dark"] {{
  --bg: #11171e; --surface: #19212b; --ink: #e6ebf0; --muted: #93a1b0; --line: #2b3745;
  --hit: #f2b25c; --hit-bg: #3a2a12; --none: #7ccbb2; --none-bg: #16322b; color-scheme: dark; }}
body {{ background: var(--bg); color: var(--ink); font-family: var(--sans); line-height: 1.7;
  padding-block: 20px 40px; padding-left: max(16px, env(safe-area-inset-left, 0px));
  padding-right: max(16px, env(safe-area-inset-right, 0px)); }}
main {{ max-width: 760px; margin: 0 auto; display: grid; gap: 20px; }}
header .asof {{ font-family: var(--mono); font-size: 12px; color: var(--muted); letter-spacing: .04em; }}
h1 {{ font-size: 20px; margin: 2px 0 0; text-wrap: balance; }}
.status {{ border-radius: 6px; padding: 16px 18px; font-weight: 700; font-size: 18px; }}
.status small {{ display: block; font-weight: 400; font-size: 13px; margin-top: 4px; }}
.status.none {{ background: var(--none-bg); color: var(--none); }}
.status.hit, .status.unknown {{ background: var(--hit-bg); color: var(--hit); }}
section {{ background: var(--surface); border: 1px solid var(--line); border-radius: 6px; padding: 14px 18px; min-width: 0; }}
h2 {{ font-size: 13px; letter-spacing: .06em; color: var(--muted); margin: 0 0 8px; text-wrap: balance; }}
p, li {{ font-size: 14px; margin: 4px 0; overflow-wrap: anywhere; }}
ul {{ padding-left: 1.2em; margin: 4px 0; }}
code {{ font-family: var(--mono); font-size: 12.5px; }}
.scroll {{ overflow-x: auto; }}
table {{ border-collapse: collapse; width: 100%; font-size: 13.5px; font-variant-numeric: tabular-nums; }}
th, td {{ text-align: right; padding: 7px 10px; border-bottom: 1px solid var(--line); white-space: nowrap; }}
th:first-child, td:first-child {{ text-align: left; }}
thead th {{ font-size: 12px; color: var(--muted); font-weight: 500; }}
tbody th {{ font-family: var(--mono); font-weight: 500; }}
td {{ font-family: var(--mono); }}
details summary {{ cursor: pointer; font-size: 13px; color: var(--muted); }}
details summary:focus-visible {{ outline: 2px solid var(--ink); outline-offset: 2px; }}
footer {{ font-size: 12px; color: var(--muted); }}
</style>
<main>
<header><div class="asof">{html.escape(asof)} 終値時点</div><h1>恩株ツール 毎朝の通知</h1></header>
<div class="status {state}">{html.escape(status)}<small>{html.escape(held_text)}</small></div>
<section><h2>今日の合図</h2>{signal_body if signal_n is not None else ''}</section>
<section><h2>保有銘柄</h2>{held_body}</section>"""]
    for head, body in rest:
        label = html.escape(re.sub(r"^\d+\.\s*", "", head))
        parts.append(f"<section><h2>{label}</h2>{body}</section>")
    parts.append(f"<section><details><summary>採用ルールと資金（全文）</summary>{rules}</details></section>")
    parts.append("<footer>合図と売りの条件はルール（tools/onkabu_scan.py）が決めています。この画面は通知の整形だけで、売買の判断は加えていません。</footer></main>")
    open(dst, "w", encoding="utf-8").write("\n".join(parts))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
