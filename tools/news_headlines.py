#!/usr/bin/env python3
"""株価が動いた原因を調べるためのニュースの見出しを、無料の仕組みで日付を指定して取る（2026-10-20 ユーザー決定）

検索（WebSearch）は数ページの要約しか返さず、広い言葉では1社ごとの出来事を見落とした
（2026-10 の東芝のHDD増産・CXMT・Anthropic・Broadcomの「カジノ」発言）。
Googleニュースの見出し（RSS。after:/before: で日付を指定できる。英語・日本語）と、
Yahooファイナンスの銘柄ごとの見出しを、日付・媒体名付きで並べる。APIキー・料金は不要。
どの銘柄・グループを調べるかはプログラムが決める（Claudeの読み違いを入れないため）。
見出しを並べるだけで、原因の判断・売買の判断はしない。

使い方:
  tools/news_headlines.py daily <movers.json> <出力.md>
      毎朝のテーマ監視（tools/theme_daily.sh prepare が呼ぶ。movers.json は tools/theme_scan.py が書く）。
      その取引日の市場全体・半導体・信用（社債）・「〇〇ショック」の呼び名に加え、
      1週間で−5%以下のグループごとに下げの大きい3銘柄と、1日で−7%以下の銘柄（合わせて最大12）の直近1週間の見出し。
  tools/news_headlines.py day <YYYY-MM-DD> [--tickers A,B] [--per N]
  tools/news_headlines.py range <開始 YYYY-MM-DD> <終了 YYYY-MM-DD> [--tickers A,B] [--per N]
      質問を受けたとき（CLAUDE.md「相場の急な下げについて質問されたとき」）。取引日（平日）ごとに市場全体などの見出しと、
      指定した銘柄の見出し。日付は米国の取引日。
"""
import argparse
import datetime as dt
import email.utils
import html
import json
import re
import subprocess
import sys
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from zoneinfo import ZoneInfo

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
ET = ZoneInfo("America/New_York")
EN = "hl=en-US&gl=US&ceid=US:en"
JA = "hl=ja&gl=JP&ceid=JP:ja"
# (見出し, 検索語, 言語)。2026-10-16 の見出しで、ロイター・CNBC・株探などのまとめ記事と「コアウィーブ・ショック」が取れた語
MARKET = [
    ("市場全体（英語のまとめ記事）", "stocks Wall Street close Nasdaq", EN),
    ("市場全体（Stock Market Today）", '"stock market today"', EN),
    ("市場全体（日本語のまとめ記事）", "米国株式市場 OR NY株", JA),
    ("半導体・AI株（英語）", "chip stocks OR semiconductor stocks OR AI stocks", EN),
    ("信用（社債・借金）", "AI debt OR bonds OR credit spreads OR CDS", EN),
    ("「〇〇ショック」の呼び名（日本語）", "ショック 株", JA),
]
# 銘柄のページ・予想・役員の株式の受け取りなど、原因の確認に使えない見出し
NOISE = re.compile(r"Forecast & Analyst|Price History|price, news, quote|Stock Price, News|Average Price Target|withheld for taxes|"
                   r"units vest|Real-Time Signals|Outperforming Other|Should You Buy\?|Better Buy", re.I)
# 銘柄の検索語。「〇〇 stock」だけでは株価のページが多いので、下げ・上げの理由を書いた記事を探す語を足す（2026-10-20 に比べた）
TICKER_Q = "{name} stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)"
SUFFIX = re.compile(r"[,.]?\s+(Inc|Incorporated|Corporation|Corp|Co|Company|Holdings?|Group|plc|PLC|N\.?V|Ltd|Limited|S\.?A|SE|AG|"
                    r"Technologies|Technology|Class [A-C])\.?$")


def curl(url):
    r = subprocess.run(["curl", "-sS", "--max-time", "20", "-A", UA, url], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def google(q, lang, start, end, n):
    """start〜end（米国の日付、両端を含む）に配信された見出し [(日付, 媒体, 見出し)]。取れなければ None"""
    full = f"{q} after:{start - dt.timedelta(days=1)} before:{end + dt.timedelta(days=2)}"
    t = curl(f"https://news.google.com/rss/search?q={urllib.parse.quote(full)}&{lang}")
    if "<rss" not in t:
        return None
    out = []
    for item in re.findall(r"<item>(.*?)</item>", t, re.S):
        title = html.unescape((re.search(r"<title>(.*?)</title>", item, re.S) or [None, ""])[1])
        src = html.unescape((re.search(r"<source[^>]*>(.*?)</source>", item, re.S) or [None, ""])[1])
        pub = re.search(r"<pubDate>(.*?)</pubDate>", item)
        if not pub:
            continue
        d = email.utils.parsedate_to_datetime(pub.group(1)).astimezone(ET).date()
        if not (start <= d <= end + dt.timedelta(days=1)):   # 引け後の記事は翌日付になるので1日足す
            continue
        if src and title.endswith(" - " + src):
            title = title[: -len(src) - 3]
        if NOISE.search(title):
            continue
        out.append((d, src, title))
    return sorted(out[:n], key=lambda x: x[0])   # Googleの関連の高い順に n 件を取り、日付の順に並べる


def yahoo(sym, start, end, n):
    """銘柄の名前と、start〜end のYahooファイナンスの見出し"""
    t = curl(f"https://query1.finance.yahoo.com/v1/finance/search?q={urllib.parse.quote(sym)}&quotesCount=1&newsCount=10")
    try:
        j = json.loads(t)
    except Exception:
        return sym, None
    q = (j.get("quotes") or [{}])[0]
    name = q.get("longname") or q.get("shortname") or sym
    if q.get("symbol", "").upper() != sym.upper():
        name = sym
    out = []
    for x in j.get("news", []):
        d = dt.datetime.fromtimestamp(x.get("providerPublishTime", 0), ET).date()
        if start <= d <= end + dt.timedelta(days=1):
            out.append((d, x.get("publisher", ""), x.get("title", "")))
    return name, sorted(out)[:n]


def short_name(name):
    prev = None
    while prev != name:
        prev = name
        m = SUFFIX.sub("", name).strip()
        name = m if m else name
    return name.replace("&amp;", "&")


class Out:
    def __init__(self):
        self.L, self.seen = [], set()

    def section(self, head, query, rows, level="###"):
        self.L.append(f"\n{level} {head}\n検索語: `{query}`")
        if rows is None:
            self.L.append("- （取得できなかった）")
            return
        new = []
        for d, src, title in rows:
            k = re.sub(r"\W+", "", title.lower())[:80]
            if k in self.seen:
                continue
            self.seen.add(k)
            new.append(f"- {d.month}/{d.day} {src} | {title}")
        self.L += new or ["- （新しい見出しなし）"]


def market_sections(o, day, per, pool):
    futs = [(h, q, pool.submit(google, q, lang, day, day, per)) for h, q, lang in MARKET]
    for h, q, f in futs:
        o.section(h, q, f.result())


def ticker_sections(o, tickers, start, end, per, pool, info=None, use_yahoo=True):
    """use_yahoo: Yahooの見出しは直近の約10件だけなので、過去の日付（range）では出さない（名前の取得には使う）"""
    ys = {s: pool.submit(yahoo, s, start, end, 3) for s in tickers}
    gs = {}
    for s in tickers:
        name, _ = ys[s].result()
        q = TICKER_Q.format(name=short_name(name))
        gs[s] = (q, pool.submit(google, q, EN, start, end, per))
    for s in tickers:
        name, yrows = ys[s].result()
        q, f = gs[s]
        o.L.append(f"\n### {s}（{name}{'、' + info[s] if info and s in info else ''}）")
        o.section("Googleニュース", q, f.result(), "####")
        if use_yahoo:
            o.section("Yahooファイナンス", s, [r for r in (yrows or []) if not NOISE.search(r[2])] if yrows is not None else None, "####")


def pct(x):
    return "—" if x is None else f"{x * 100:+.1f}%"


def cmd_daily(a):
    o = Out()
    try:
        mv = json.load(open(a.movers, encoding="utf-8"))
    except Exception as e:
        mv = None
        print(f"movers.json を読めない（{e}）。市場全体の見出しだけ取る", file=sys.stderr)
    day = dt.date.fromisoformat(mv["day"]) if mv else dt.date.today() - dt.timedelta(days=1)
    o.L.append(f"# ニュースの見出し（{day} の値動きの原因の確認用）\n")
    o.L.append("- Googleニュース（日付を指定）とYahooファイナンスの見出しを `tools/news_headlines.py` が自動で並べたもの。"
               "日付は米国東部時間の配信日（引け後の記事は翌日付）。原因の判断・売買の判断はしていない。")
    picks, info = [], {}
    if mv:
        st = [x for x in mv["stocks"] if x.get("w1") is not None]
        weak = sorted(((g, v) for g, v in mv["groups"].items() if v.get("w1") is not None and v["w1"] <= -0.05), key=lambda x: x[1]["w1"])
        for g, v in weak:
            mem = sorted((x for x in st if x["group"] == g), key=lambda x: x["w1"])[:3]
            picks += [x["sym"] for x in mem if x["sym"] not in picks]
        one = sorted((x for x in mv["stocks"] if x.get("d1") is not None and x["d1"] <= -0.07), key=lambda x: x["d1"])
        picks += [x["sym"] for x in one if x["sym"] not in picks]
        picks = picks[:12]
        for x in mv["stocks"]:
            info[x["sym"]] = f"{x['group']}、前日比 {pct(x['d1'])}、1週 {pct(x['w1'])}"
        o.L.append("- 調べた銘柄の選び方: 1週の騰落率（中央値）が−5%以下のグループごとに、1週で下げの大きい3銘柄＋1日で−7%以下の銘柄（最大12）。")
        o.L.append("- 1週で−5%以下のグループ: " + ("、".join(f"{g}（{pct(v['w1'])}）" for g, v in weak) if weak else "なし"))
    with ThreadPoolExecutor(6) as pool:
        o.L.append(f"\n## 1. 市場全体（{day}）")
        market_sections(o, day, a.per, pool)
        if picks:
            o.L.append(f"\n## 2. 大きく下げた銘柄（{day - dt.timedelta(days=6)}〜{day} の見出し）")
            ticker_sections(o, picks, day - dt.timedelta(days=6), day, 4, pool, info)
    open(a.out, "w", encoding="utf-8").write("\n".join(o.L) + "\n")
    print(f"headlines: {a.out}（銘柄: {' '.join(picks) or 'なし'}）")


def cmd_range(a, start, end):
    o = Out()
    tick = [t.strip().upper() for t in (a.tickers or "").split(",") if t.strip()]
    o.L.append(f"# ニュースの見出し（{start}〜{end}）\n")
    o.L.append("- Googleニュース（日付を指定）とYahooファイナンスの見出しを `tools/news_headlines.py` が並べたもの。日付は米国東部時間の配信日。")
    d = start
    with ThreadPoolExecutor(6) as pool:
        while d <= end:
            if d.weekday() < 5:
                o.L.append(f"\n## {d}（{'月火水木金'[d.weekday()]}）")
                market_sections(o, d, a.per, pool)
                if tick:
                    ticker_sections(o, tick, d, d, a.per, pool, use_yahoo=(dt.date.today() - d).days <= 3)
            d += dt.timedelta(days=1)
    print("\n".join(o.L))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("daily"); p.add_argument("movers"); p.add_argument("out"); p.add_argument("--per", type=int, default=5)
    p = sub.add_parser("day"); p.add_argument("date"); p.add_argument("--tickers"); p.add_argument("--per", type=int, default=5)
    p = sub.add_parser("range"); p.add_argument("start"); p.add_argument("end"); p.add_argument("--tickers"); p.add_argument("--per", type=int, default=3)
    a = ap.parse_args()
    if a.cmd == "daily":
        cmd_daily(a)
    elif a.cmd == "day":
        cmd_range(a, dt.date.fromisoformat(a.date), dt.date.fromisoformat(a.date))
    else:
        cmd_range(a, dt.date.fromisoformat(a.start), dt.date.fromisoformat(a.end))


if __name__ == "__main__":
    main()
