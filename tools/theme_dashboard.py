#!/usr/bin/env python3
"""テーマ監視の結果を携帯で見るための1枚のWebページ（HTML）を作る（`新分析ツール/テーマ監視_手順書.md` 手順8）

使い方:
  tools/theme_dashboard.py <report.md> <record.json> <出力.html> [--history <記録のディレクトリ>]
    --history: 過去の record.json を置いたディレクトリ（ブランチ claude/ecstatic-tesla-660dhs の テーマ監視/ を取り出したもの）。
               直近20日分の局面と著者の結論の推移を載せる。

ページの中身は report.md（著者の回答の全文・スキャン・ニュース）をそのまま変換したもので、Claudeの見解は加えない。
Routine が毎朝このページを同じURLへ公開し直す（Artifact）。
"""
import argparse
import glob
import html
import json
import os
import re

FONTS = "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+JP:wght@400;500;700&family=IBM+Plex+Mono:wght@500&display=swap"

CSS = """
:root{--bg:#f4f6f8;--surface:#ffffff;--ink:#16202a;--muted:#5b6876;--line:#dde3ea;--accent:#1d6a86;
--good:#177245;--good-bg:#e3f3ea;--bad:#b3261e;--bad-bg:#fbe6e4;--warn:#9a5b00;--warn-bg:#fdf0da;--neutral-bg:#eceff3;
--font:"IBM Plex Sans JP",system-ui,-apple-system,"Hiragino Sans","Noto Sans JP",sans-serif;--mono:"IBM Plex Mono",ui-monospace,Menlo,monospace}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){color-scheme:dark;--bg:#0f151b;--surface:#172029;--ink:#e6ebf0;--muted:#9aa7b4;--line:#2a3642;--accent:#5fb3d3;
--good:#5fd39a;--good-bg:#12342a;--bad:#ff8a80;--bad-bg:#3a1a1a;--warn:#f0b760;--warn-bg:#3a2c12;--neutral-bg:#222c36}}
:root[data-theme="dark"]{color-scheme:dark;--bg:#0f151b;--surface:#172029;--ink:#e6ebf0;--muted:#9aa7b4;--line:#2a3642;--accent:#5fb3d3;
--good:#5fd39a;--good-bg:#12342a;--bad:#ff8a80;--bad-bg:#3a1a1a;--warn:#f0b760;--warn-bg:#3a2c12;--neutral-bg:#222c36}
body{background:var(--bg);color:var(--ink);font-family:var(--font);font-size:15px;line-height:1.65;padding-inline:16px;padding-block:12px 40px}
main{max-width:760px;margin:0 auto;display:flex;flex-direction:column;gap:18px;min-width:0}
main>*,section>*,.answer>*{min-width:0;max-width:100%}
body{overflow-wrap:anywhere}
.row>span:last-child{flex:1 1 12em;min-width:0}
header{display:flex;flex-direction:column;gap:6px}
.kicker{font-size:12px;letter-spacing:.08em;color:var(--muted)}
h1{font-size:22px;margin:0;text-wrap:balance}
.date{font-family:var(--mono);font-variant-numeric:tabular-nums;color:var(--muted);font-size:13px}
.summary{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:14px 16px;display:flex;flex-direction:column;gap:10px}
.row{display:flex;flex-wrap:wrap;gap:8px;align-items:baseline}
.label{font-size:12px;color:var(--muted);min-width:5.5em}
.pill{display:inline-block;border-radius:999px;padding:2px 10px;font-size:13px;font-weight:500;background:var(--neutral-bg);color:var(--ink)}
.pill.good{background:var(--good-bg);color:var(--good)}.pill.bad{background:var(--bad-bg);color:var(--bad)}.pill.warn{background:var(--warn-bg);color:var(--warn)}
.stage{font-weight:700;color:var(--accent)}
nav{display:flex;gap:8px;overflow-x:auto;padding-bottom:2px}
nav a{white-space:nowrap;font-size:13px;color:var(--accent);text-decoration:none;border:1px solid var(--line);border-radius:999px;padding:4px 12px;background:var(--surface)}
section{display:flex;flex-direction:column;gap:10px}
h2{font-size:17px;margin:8px 0 0;padding-top:8px;border-top:1px solid var(--line)}
h3{font-size:15px;margin:6px 0 0;color:var(--accent)}
p,ul{margin:0}ul{padding-left:1.2em}
.answer{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:10px 14px}
.tbl{overflow-x:auto;background:var(--surface);border:1px solid var(--line);border-radius:10px}
table{border-collapse:collapse;font-size:13px;min-width:100%}
th,td{padding:6px 10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
th{color:var(--muted);font-weight:500;white-space:nowrap}
td{overflow-wrap:normal;word-break:normal;min-width:4em}
td{font-variant-numeric:tabular-nums}
tr:last-child td{border-bottom:none}
details{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:8px 14px}
summary{cursor:pointer;color:var(--accent);font-weight:500}
details[open] summary{margin-bottom:8px}
.note{font-size:12px;color:var(--muted)}
a:focus-visible,summary:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
"""


def inline(t):
    t = html.escape(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"【([^】]+)】", lambda m: f'<span class="pill {verdict_class(m.group(1))}">{m.group(1)}</span>', t)
    return t


def verdict_class(v):
    if any(x in v for x in ("注文する", "保有を続ける", "ステージ2")):
        return "good"
    if any(x in v for x in ("早めに手じまう", "ステージ4")):
        return "bad"
    if any(x in v for x in ("見送る", "ステージ3")):
        return "warn"
    return ""


def md_to_html(text, shift=1):
    """report.md の範囲だけを想定した簡単な変換（見出し・表・箇条書き・段落）"""
    out, lines, i = [], text.splitlines(), 0
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            i += 1
            continue
        m = re.match(r"^(#+)\s+(.*)", ln)
        if m:
            lv = min(len(m.group(1)) + shift, 4)
            out.append(f"<h{lv}>{inline(m.group(2))}</h{lv}>")
            i += 1
            continue
        if ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                if not re.match(r"^\|[\s|:-]+\|?$", lines[i]):
                    rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            if rows:
                h = "".join(f"<th>{inline(c)}</th>" for c in rows[0])
                b = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows[1:])
                out.append(f'<div class="tbl"><table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>')
            continue
        if re.match(r"^\s*([-*]|\d+\.)\s+", ln):
            items = []
            while i < len(lines) and re.match(r"^\s*([-*]|\d+\.)\s+", lines[i]):
                items.append(re.sub(r"^\s*([-*]|\d+\.)\s+", "", lines[i]))
                i += 1
            out.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ul>")
            continue
        para = []
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#|\||\s*([-*]|\d+\.)\s)", lines[i]):
            para.append(lines[i])
            i += 1
        out.append(f"<p>{inline(' '.join(para))}</p>")
    return "\n".join(out)


def split_top(md):
    """report.md を「# 見出し」ごとに分ける"""
    keys = ("著者の回答（全文）", "スキャン（数値と事実）", "ニュース（サブエージェントの調査）")
    parts, cur, buf = {}, None, []
    for ln in md.splitlines():
        m = re.match(r"^# (.+)", ln)
        if m and (m.group(1).strip() in keys or cur is None):
            if cur:
                parts[cur] = "\n".join(buf)
            cur, buf = m.group(1).strip(), []
        else:
            buf.append(ln)
    if cur:
        parts[cur] = "\n".join(buf)
    return parts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("report")
    ap.add_argument("record")
    ap.add_argument("out")
    ap.add_argument("--history")
    a = ap.parse_args()
    md = open(a.report, encoding="utf-8").read()
    rec = json.load(open(a.record, encoding="utf-8"))
    parts = split_top(md)
    answers = parts.get("著者の回答（全文）", "")
    scan = parts.get("スキャン（数値と事実）", "")
    news = parts.get("ニュース（サブエージェントの調査）", "")

    warn = re.search(r"警告（[^）]*）:\s*\*\*([^*]+)\*\*", scan)
    orders = [c for c in rec["candidates"] if "注文" in c["verdict"]]
    skips = [c for c in rec["candidates"] if "見送" in c["verdict"]]
    exits = [h for h in rec["holdings"] if "早め" in h["verdict"]]

    def names(xs):
        return "、".join(x["sym"] for x in xs) if xs else "なし"

    S = []
    w = S.append
    w(f'<title>テーマ監視</title><link rel="preconnect" href="https://fonts.googleapis.com">'
      f'<link rel="stylesheet" href="{FONTS}"><style>{CSS}</style>')
    w("<main>")
    w('<header><div class="kicker">半導体・AI・光通信 テーマ監視</div>'
      f'<h1>{html.escape(rec["trade_date"])} の引け時点</h1>'
      f'<div class="date">更新 {html.escape(rec["run_date"])}（日本時間）</div></header>')
    stage = rec.get("theme_stage") or "記録なし"
    w('<div class="summary">')
    w(f'<div class="row"><span class="label">テーマの局面</span><span>{inline(stage)}</span></div>')
    if warn:
        cls = "bad" if "出ている" in warn.group(1) and "出ていない" not in warn.group(1) else "good"
        w(f'<div class="row"><span class="label">早めの警告</span><span class="pill {cls}">{html.escape(warn.group(1))}</span></div>')
    w(f'<div class="row"><span class="label">注文する</span><span class="pill {"good" if orders else ""}">{html.escape(names(orders))}</span></div>')
    w(f'<div class="row"><span class="label">見送る</span><span class="pill {"warn" if skips else ""}">{html.escape(names(skips))}</span></div>')
    w(f'<div class="row"><span class="label">早めに手じまう</span><span class="pill {"bad" if exits else ""}">{html.escape(names(exits))}</span></div>')
    for c in orders:
        m = re.search(r"\| " + re.escape(c["sym"]) + r" \|[^\n]*", scan[scan.find("## 6."):] if "## 6." in scan else "")
        if m:
            order = m.group(0).strip("|").split("|")[-1].strip()
            w(f'<p class="note"><strong>{html.escape(c["sym"])}</strong>: {html.escape(order)}</p>')
    w('<p class="note">買いの条件は採用したルールが決め、著者は注文を止める理由だけを判定しています。下に著者の回答の全文があります。</p>')
    w("</div>")
    w('<nav><a href="#answers">著者の回答</a><a href="#groups">テーマの強さ</a><a href="#moves">急騰・急落</a>'
      '<a href="#news">ニュース</a><a href="#history">推移</a><a href="#heatmap">業種ランキング</a></nav>')

    w('<section id="answers"><h2>著者の回答（全文）</h2>')
    for blk in re.split(r"(?m)^## (?=\d+_)", answers)[1:]:
        title, _, body = blk.partition("\n")
        t = re.sub(r"^\d+_", "", title.strip()).replace("_prompt_", " ").replace("_", " ")
        w(f'<div class="answer"><h3>{html.escape(t)}</h3>{md_to_html(body, shift=2)}</div>')
    w("</section>")

    def scan_part(head, nxt):
        i = scan.find(head)
        if i < 0:
            return ""
        j = scan.find(nxt, i + 1) if nxt else -1
        return scan[i:j if j > 0 else len(scan)]

    w('<section id="groups"><h2>テーマの強さと警告</h2>')
    w(md_to_html(re.sub(r"^## .*\n", "", scan_part("## 1.", "## 2.")), 2))
    w(md_to_html(re.sub(r"^## .*\n", "", scan_part("## 2.", "## 3.")), 2))
    w("</section>")
    w('<section id="moves"><h2>急騰・急落・保有銘柄・候補</h2>')
    for head, nxt in (("## 4.", "## 5."), ("## 5.", "## 6."), ("## 6.", None)):
        w(md_to_html(scan_part(head, nxt), 1))
    w("</section>")
    w('<section id="news"><h2>ニュース（調査）</h2>' + (md_to_html(news, 1) if news.strip() else "<p>調査なし</p>") + "</section>")

    w('<section id="history"><h2>推移（直近20日）</h2>')
    hist = []
    if a.history:
        for f in glob.glob(os.path.join(a.history, "**", "record.json"), recursive=True):
            try:
                hist.append(json.load(open(f, encoding="utf-8")))
            except (ValueError, OSError):
                pass
    hist = sorted({h["trade_date"]: h for h in hist + [rec]}.values(), key=lambda h: h["trade_date"], reverse=True)[:20]
    rows = ["| 引けの日 | テーマの局面 | 候補（著者の結論） | 保有（著者の結論） |"]
    for h in hist:
        st = re.search(r"【[^】]+】", h.get("theme_stage", ""))
        cs = "、".join(f"{c['sym']}【{c['verdict']}】" for c in h["candidates"]) or "なし"
        hs = "、".join(f"{x['sym']}【{x['verdict']}】" for x in h["holdings"]) or "なし"
        rows.append(f"| {h['trade_date']} | {st.group(0) if st else '-'} | {cs} | {hs} |")
    w(md_to_html("\n".join(rows), 1))
    w("</section>")

    w('<section id="heatmap"><details><summary>業種ランキング（Finviz、全米）</summary>')
    w(md_to_html(re.sub(r"^## .*\n", "", scan_part("## 3.", "## 4.")), 2))
    w("</details></section>")
    w('<p class="note">数値はスクリプトの計算、判定は各著者のノートブックの回答です。売買の最終判断はご自身で行ってください。</p>')
    w("</main>")
    open(a.out, "w", encoding="utf-8").write("\n".join(S))
    print(a.out)


if __name__ == "__main__":
    main()
