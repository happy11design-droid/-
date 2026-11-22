#!/usr/bin/env python3
"""87銘柄の週ごとの悪材料の見出しを、2023年〜についてGoogleニュースから取り、言葉で悪材料を判定する
（2026-11-19 ユーザーの指示「悪材料ありの場合でもエントリーしたら利益出るのかの検証はしたことある？」→「検証して」）

- 銘柄ごと・週ごと（月〜日）に「会社名 (悪材料の言葉 OR …)」で検索し、見出しを最大10件取る。
  取った見出しは tools/news_headlines.py の google() が ~/.cache/stock_backtest/news/ に置くので、2回目からは取り直さない。
- 悪材料の判定（見出しの言葉。Claudeが置いたもの）: 格下げ、目標株価・見通しの引き下げ、決算の未達、訴訟、当局の調査、不正・会計、
  空売りの報告、リコール、輸出規制・禁止・制裁、増資・転換社債・希薄化、経営者の辞任、遅れ・停止、人員削減、債務不履行・破綻、警告。
  「格上げ（upgrade）」の見出しは数えない。2026-11-19 に「slash」「restriction」「crackdown」「tighten」を足した（最初の試しで見落としたため）。見出しに会社名かティッカーがあるものだけ。
- 結果: ~/.cache/stock_backtest/news/history_87.json  {銘柄: {日付: [見出し, ...]}}（悪材料と判定した見出しだけ、配信日ごと）
使い方: python3 tools/news_history.py [--start 2023-01-02] [--workers 6]
"""
import argparse
import datetime as dt
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import news_headlines as nh

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.expanduser("~/.cache/stock_backtest/news/history_87.json")
Q_WORDS = ("downgrade OR downgraded OR lawsuit OR sued OR probe OR investigation OR subpoena OR guidance OR outlook OR offering OR recall "
           "OR fraud OR \"short seller\" OR resigns OR ban OR restrictions OR delay OR misses OR warns OR layoffs")
BAD = re.compile(r"(?i)downgrad|\bcuts?\b.{0,25}(target|guidance|outlook|forecast|rating)|\blower(s|ed)?\b.{0,20}(guidance|outlook|forecast|target)|"
                 r"\bweak(er)?\b.{0,15}(guidance|outlook|forecast|demand|results)|\bmiss(es|ed)?\b|below (estimates|expectations)|"
                 r"lawsuit|\bsue[sd]?\b|class action|\bprobe|investigat|subpoena|\bSEC\b.{0,15}(charge|fine|settle)|fraud|accounting|restat|"
                 r"short[- ]seller|short report|\brecall|\bban(s|ned)?\b|export (curb|restriction|control|ban)|sanction|"
                 r"\boffering\b|dilut|convertible|resign|steps down|ousted|\bdelay(s|ed)?\b|\bhalt(s|ed)?\b|layoff|job cuts|"
                 r"default|bankrupt|\bwarns?\b|\bwarning\b|\bslash(es|ed)?\b|restriction|crackdown|\btighten")
GOOD = re.compile(r"(?i)upgrad")


def names():
    md = open(os.path.join(ROOT, "新分析ツール", "テーマ監視銘柄.md"), encoding="utf-8").read()
    out = {}
    for m in re.finditer(r"(?m)^\| ([A-Z][A-Z0-9.\-]*) \| ([^|]+) \|", md):
        if m.group(1) != "ティッカー":
            out[m.group(1)] = nh.short_name(m.group(2).strip())
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2023-01-02")
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    nm = names()
    d0 = dt.date.fromisoformat(a.start)
    last = dt.date.today() - dt.timedelta(days=4)
    weeks = []
    while d0 + dt.timedelta(days=6) <= last:
        weeks.append(d0)
        d0 += dt.timedelta(days=7)
    jobs = [(s, w) for s in nm for w in weeks]
    print(f"{len(nm)}銘柄 × {len(weeks)}週 = {len(jobs)}回", file=sys.stderr)

    def one(job):
        s, w = job
        short = nm[s]
        q = f'"{short}" ({Q_WORDS})'
        rows = nh.google(q, nh.EN, w, w + dt.timedelta(days=6), 10)
        if rows is None:
            return s, w, None
        hit = []
        for d, src, title in rows:
            if (short.lower() in title.lower() or re.search(rf"\b{re.escape(s)}\b", title)) and BAD.search(title) and not GOOD.search(title):
                hit.append((d.isoformat(), title))
        return s, w, hit

    res, fail = {}, 0
    with ThreadPoolExecutor(a.workers) as pool:
        for i, (s, w, hit) in enumerate(pool.map(one, jobs)):
            if hit is None:
                fail += 1
                continue
            for d, t in hit:
                res.setdefault(s, {}).setdefault(d, []).append(t)
            if i % 1000 == 0:
                print(f"{i}/{len(jobs)} 取れなかった {fail}", file=sys.stderr, flush=True)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump({"names": nm, "weeks": [w.isoformat() for w in weeks], "failed": fail, "bad": res}, open(OUT, "w"), ensure_ascii=False)
    n = sum(len(v) for v in res.values())
    print(f"悪材料の見出しがあった日: {n}（銘柄×日）、取れなかった検索 {fail}", file=sys.stderr)


if __name__ == "__main__":
    main()
