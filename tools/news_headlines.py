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
      その取引日の市場全体・半導体・信用（社債）・「〇〇ショック」の呼び名・引け後（時間外）の動き・買収と合併に加え、
      銘柄ごとの直近1週間の見出し。調べる銘柄は次の順（2026-10-29〜）:
        ① 保有銘柄（新分析ツール/保有銘柄.md）　② 今日の候補（同じフォルダの cands_meta.json）
        ③ 時間外（引け後）に±5%以上動いた監視銘柄（Yahooの引け後の値段。afterhours.json にも書く）
        ④ 引けまでに大きく動いた銘柄: 1週間で−5%以下のグループごとに下げの大きい3銘柄・1日で−7%以下、
           1週間で+5%以上のグループごとに上げの大きい3銘柄・1日で+7%以上
        ①〜③は必ず調べ、④は合計が12銘柄になるまで（下げを先に約2/3、上げを約1/3）。
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
import os
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
    # 引け後の決算で時間外に動いた銘柄（2026-10-20 のSpaceX・Super Microの決算でAI半導体が時間外に上げた。2026-10-21 ユーザーの指示）
    ("引け後・時間外の動き（英語）", '"after hours" OR "after the bell" OR "extended trading" stocks', EN, 8),
    ("引け後・時間外の動き（日本語）", "時間外 決算 株", JA, 8),
    # 買収・合併（2026-10-28 のマーベルによるルメンタム買収の報道（引け後）を、毎朝の記録が拾えなかった。2026-10-29 ユーザーの指示）
    ("買収・合併（英語）", "acquisition OR acquire OR merger OR takeover chip OR semiconductor OR AI OR optical", EN, 8),
]
AH_MIN = 0.05      # 時間外にこれ以上動いた監視銘柄は必ず見出しを調べる（2026-10-29。87銘柄で1日平均1銘柄、多い日でも9銘柄）
AH_SHOW = 0.03     # 時間外の値動きの表に出す下限
TOTAL = 12         # 銘柄ごとの見出しを調べる数の目安（①〜③は上限を超えても全部）
HOLDINGS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "新分析ツール", "保有銘柄.md")
# 銘柄のページ・予想・役員の株式の受け取りなど、原因の確認に使えない見出し
NOISE = re.compile(r"Forecast & Analyst|Price History|price, news, quote|Stock Price, News|Average Price Target|withheld for taxes|"
                   r"units vest|Real-Time Signals|Outperforming Other|Should You Buy\?|Better Buy|株価・株式情報", re.I)
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
    futs = [(m[0], m[1], pool.submit(google, m[1], m[2], day, day, m[3] if len(m) > 3 else per)) for m in MARKET]
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


def after_hours(sym, day):
    """day の引け（16:00 ET の前の最後の5分足）から、引け後（16:00〜20:00 ET）の最後の値までの騰落率。(騰落率, 引け, 時間外の値, 時刻) か None"""
    t = curl(f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(sym)}?interval=5m&range=5d&includePrePost=true")
    try:
        r = json.loads(t)["chart"]["result"][0]
        q = r["indicators"]["quote"][0]
    except Exception:
        return None
    reg, post = None, None
    for ts, c in zip(r.get("timestamp", []), q.get("close", [])):
        if not c:
            continue
        x = dt.datetime.fromtimestamp(ts, ET)
        if x.date() != day:
            continue
        if (9, 30) <= (x.hour, x.minute) < (16, 0):
            reg = c
        elif x.hour >= 16:
            post = (c, x.strftime("%H:%M"))
    if not reg or not post:
        return None
    return post[0] / reg - 1, reg, post[0], post[1]


def holdings_list():
    try:
        return [m.group(1) for m in (re.match(r"^\| ([A-Z][A-Z.]*) \| \d{4}-\d{2}-\d{2}", x) for x in open(HOLDINGS, encoding="utf-8")) if m]
    except OSError:
        return []


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
    picks, ups, info = [], [], {}

    def choose(sign, cap):
        """sign=-1: 下げ、+1: 上げ。1週の中央値が±5%を超えたグループの上位3銘柄と、1日で±7%を超えた銘柄"""
        st = [x for x in mv["stocks"] if x.get("w1") is not None]
        grp = sorted(((g, v) for g, v in mv["groups"].items() if v.get("w1") is not None and sign * v["w1"] >= 0.05),
                     key=lambda x: -sign * x[1]["w1"])
        out = []
        for g, v in grp:
            mem = sorted((x for x in st if x["group"] == g), key=lambda x: -sign * x["w1"])[:3]
            out += [x["sym"] for x in mem if x["sym"] not in out]
        one = sorted((x for x in mv["stocks"] if x.get("d1") is not None and sign * x["d1"] >= 0.07), key=lambda x: -sign * x["d1"])
        out += [x["sym"] for x in one if x["sym"] not in out]
        return out[:cap], grp

    must, ah = [], {}
    if mv:
        hold = holdings_list()
        cm = os.path.join(os.path.dirname(os.path.abspath(a.movers)), "cands_meta.json")
        try:
            cand = [k for k in json.load(open(cm, encoding="utf-8")) if re.fullmatch(r"[A-Z][A-Z.]*", k)]   # _s2 などの付記は除く
        except Exception:
            cand = []
        watch = [x["sym"] for x in mv["stocks"]]
        allsyms = list(dict.fromkeys(hold + cand + watch))
        with ThreadPoolExecutor(8) as p8:
            for s_, r_ in zip(allsyms, p8.map(lambda s_: after_hours(s_, day), allsyms)):
                if r_:
                    ah[s_] = {"pct": round(r_[0], 4), "close": r_[1], "post": r_[2], "time": r_[3]}
        json.dump(ah, open(os.path.join(os.path.dirname(os.path.abspath(a.out)), "afterhours.json"), "w", encoding="utf-8"), ensure_ascii=False)
        big = sorted((s_ for s_, v in ah.items() if abs(v["pct"]) >= AH_MIN), key=lambda s_: -abs(ah[s_]["pct"]))
        must = list(dict.fromkeys(hold + cand + big))
        down, weak = choose(-1, 12)
        up_, strong = choose(+1, 6)
        room = max(0, TOTAL - len(must))
        nd = min(len(down), -(-room * 2 // 3))
        picks = [x for x in down if x not in must][:nd]
        ups = [x for x in up_ if x not in must and x not in picks][:max(0, room - len(picks))]
        if len(picks) + len(ups) < room:
            picks += [x for x in down if x not in must and x not in picks][:room - len(picks) - len(ups)]
        grp = {x["sym"]: x for x in mv["stocks"]}
        for s_ in allsyms:
            x = grp.get(s_, {})
            role = "保有" if s_ in hold else "候補" if s_ in cand else ""
            parts_ = [p_ for p_ in (role, x.get("group"), f"前日比 {pct(x.get('d1'))}" if x else "", f"1週 {pct(x.get('w1'))}" if x else "",
                                    f"時間外 {pct(ah[s_]['pct'])}" if s_ in ah else "") if p_]
            info[s_] = "、".join(parts_)
        o.L.append(f"- 調べた銘柄の選び方: ①保有 ②今日の候補 ③時間外に±{AH_MIN * 100:.0f}%以上動いた監視銘柄 は全部、"
                   f"④引けまでに大きく動いた銘柄（1週で±5%のグループの上位3・1日で±7%）は合計{TOTAL}銘柄まで。")
        o.L.append("- 1週で−5%以下のグループ: " + ("、".join(f"{g}（{pct(v['w1'])}）" for g, v in weak) if weak else "なし"))
        o.L.append("- 1週で+5%以上のグループ: " + ("、".join(f"{g}（{pct(v['w1'])}）" for g, v in strong) if strong else "なし"))
        rows_ = sorted((s_ for s_, v in ah.items() if abs(v["pct"]) >= AH_SHOW or s_ in hold or s_ in cand), key=lambda s_: -abs(ah[s_]["pct"]))
        o.L.append(f"\n## 0. 時間外（引け後）の値動き（{day} の引けから、Yahoo。±{AH_SHOW * 100:.0f}%以上の監視銘柄と、保有・候補は全部）\n")
        o.L.append("| 銘柄 | 区分 | 引け | 時間外 | 騰落率 |")
        o.L.append("|---|---|---|---|---|")
        for s_ in rows_:
            v = ah[s_]
            mark = "**" if abs(v["pct"]) >= AH_MIN else ""
            o.L.append(f"| {s_} | {'保有' if s_ in hold else '候補' if s_ in cand else '監視'} | {v['close']:.2f} | {v['post']:.2f}（{v['time']} ET） | {mark}{pct(v['pct'])}{mark} |")
        if not rows_:
            o.L.append("| （なし） | | | | |")
        miss = [s_ for s_ in hold + cand if s_ not in ah]
        if miss:
            o.L.append(f"- 時間外の値段を取れなかった保有・候補: {'、'.join(miss)}")
    with ThreadPoolExecutor(6) as pool:
        o.L.append(f"\n## 1. 市場全体（{day}）")
        market_sections(o, day, a.per, pool)
        if must:
            o.L.append(f"\n## 2. 保有・候補・時間外で大きく動いた銘柄（{day - dt.timedelta(days=6)}〜{day} の見出し）")
            ticker_sections(o, must, day - dt.timedelta(days=6), day, 4, pool, info)
        if picks:
            o.L.append(f"\n## 3. 引けまでに大きく下げた銘柄（{day - dt.timedelta(days=6)}〜{day} の見出し）")
            ticker_sections(o, picks, day - dt.timedelta(days=6), day, 4, pool, info)
        if ups:
            o.L.append(f"\n## 4. 引けまでに大きく上げた銘柄（{day - dt.timedelta(days=6)}〜{day} の見出し）")
            ticker_sections(o, ups, day - dt.timedelta(days=6), day, 4, pool, info)
    open(a.out, "w", encoding="utf-8").write("\n".join(o.L) + "\n")
    print(f"headlines: {a.out}（保有・候補・時間外: {' '.join(must) or 'なし'}／下げ: {' '.join(picks) or 'なし'}／上げ: {' '.join(ups) or 'なし'}）")


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
