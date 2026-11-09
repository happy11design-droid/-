#!/usr/bin/env python3
"""市場全体が大きく動いた日の「材料」を、市場まとめ記事以外の分野の見出しで調べる（2026-11-10 ユーザーの指示）。

背景: 2026-11-09（月）の米国株の急反発（ダウ+1,104ドル、SOX+6.9%）の理由を、天気予報が
「売られ過ぎからの買い戻し」「原油の下げの理由は特定できず」としか書けなかった。実際は、週末から月曜にかけての
「トランプ氏がイランへの再攻撃の可能性を否定」（原油が約5%急落→インフレ・利上げ観測が後退）が主因だった。
tools/news_headlines.py の見出しは「その取引日の株の市場まとめ・半導体・信用・ショックの呼び名」しか取らず、
原油・地政学・金利・為替・政治の見出しと、月曜の動きを決める土日の見出しを取っていなかった。

使い方:
  tools/news_macro.py day <日付>      その日の見出し。月曜なら前の土日の分も含める（月曜の動きは土日の出来事で決まるため）
  tools/news_macro.py range <開始> <終了>

見出しを並べるだけで、原因の判断・売買の判断はしない（tools/news_headlines.py と同じ）。
"""
import argparse
import datetime as dt
import sys
import os
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from news_headlines import google, Out, EN, JA  # noqa: E402

# (見出し, 検索語, 言語, 件数)
MACRO = [
    ("原油・地政学（英語）", "oil prices Iran OR Hormuz OR OPEC OR crude", EN, 8),
    ("原油・地政学（日本語）", "原油 OR NY原油 イラン OR ホルムズ OR OPEC", JA, 8),
    ("トランプ氏・政権・議会の発言（英語）", "Trump says OR Trump signals OR Congress OR White House markets", EN, 8),
    ("金利・FRB・インフレ（英語）", "Fed rate hike OR Treasury yields OR CPI OR inflation OR Warsh", EN, 6),
    ("金利・FRB・インフレ（日本語）", "米利上げ OR 米長期金利 OR FRB OR 米CPI", JA, 6),
    ("為替・ドル円（日本語）", "ドル円 為替 NY外為", JA, 6),
    ("金・ドル（英語）", "gold prices dollar", EN, 4),
    ("アジア・欧州の市場まとめ（英語）", "Asian stocks OR European stocks markets wrap", EN, 6),
    ("日本市場（日本語）", "日経平均 大引け OR 東京株式 OR 日銀", JA, 6),
]


def run(start, end):
    o = Out()
    o.L.append(f"# 市場全体の材料の見出し（{start}〜{end}）\n")
    o.L.append("- Googleニュース（日付を指定）の見出しを `tools/news_macro.py` が並べたもの。日付は米国東部時間の配信日。"
               "原油・地政学・政権の発言・金利・為替・アジア欧州・日本市場。月曜は前の土日を含む。")
    with ThreadPoolExecutor(6) as pool:
        futs = [(m, pool.submit(google, m[1], m[2], start, end, m[3])) for m in MACRO]
        for m, f in futs:
            o.section(m[0], m[1], f.result())
    print("\n".join(o.L))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("day"); p.add_argument("date")
    p = sub.add_parser("range"); p.add_argument("start"); p.add_argument("end")
    a = ap.parse_args()
    if a.cmd == "day":
        d = dt.date.fromisoformat(a.date)
        run(d - dt.timedelta(days=2) if d.weekday() == 0 else d, d)
    else:
        run(dt.date.fromisoformat(a.start), dt.date.fromisoformat(a.end))


if __name__ == "__main__":
    main()
