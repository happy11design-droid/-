#!/usr/bin/env python3
"""大きく動いた日の前後で、新ツールの著者が順張り・逆張りを正しく判定できるかを再現する（過去の日付での判定の検証）

使い方:
  tools/replay_moves.py <ティッカー> <出力ディレクトリ> plan  [--months 6] [--top 3] [--earnings 日付,日付,...]
      直近Nカ月の上昇・下落の大きい日（それぞれ上位top件）と、その前後2取引日の一覧を出す（送信しない）。
  tools/replay_moves.py <ティッカー> <出力ディレクトリ> run   [同じオプション]
      各日の引け時点のデータとチャートだけで、3人の著者（ボリンジャー・ミネルヴィニ・ワインスタイン）に判定させ、
      その後の値動き（予約注文が約定したか、5日後・10日後の損益）と並べて <出力>/replay.md に書く。
  tools/replay_moves.py <ティッカー> <出力ディレクトリ> report [同じオプション]
      送信済みの回答から replay.md とチャートを作り直す（送信しない）。

後知恵を防ぐための決まり:
  - 株価・指標・チャートは、その日の引けまでのデータだけ（market_data.py --asof、theme_single.report(asof=...)）。
  - ニュースは、既存ツールの銘柄メモ（データ用ブランチの 銘柄メモ/<ティッカー>.md）のうち、その日以前の日付の項目だけを渡す。
  - 決算日は --earnings で渡した過去の決算日から、その日以降の最初の日を「次回決算予定日」として渡す。
  - NotebookLMへは --web を付けずに1回ずつ独立して送る（同じ会話に続けて送ると、後の日付の情報が前の判定に混ざるため）。
著者ノートブックへの質問は 日数×3回（1日の上限は約175回）。
"""
import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from theme_scan import fetch_daily
from theme_single import load_pool, report

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(ROOT, "新分析ツール", "個別分析_送信プロンプト雛形.txt")
MEMO_BRANCH = "origin/claude/ecstatic-tesla-660dhs"
NB = {"ボリンジャー": "3dc5edc5-7808-438c-abf0-9c0e5ca6cef9", "ミネルヴィニ": "e09b765e-4f20-496a-ae2f-6d991c488d0d",
      "ワインスタイン": "69875bdb-8d0d-474e-9b1a-c6c1b7bc82a1"}
OFFSETS = (-2, -1, 0, 1, 2)


def events(d, months, top, extra=()):
    last = dt.date.fromisoformat(d["date"][-1])
    start = (last - dt.timedelta(days=int(months * 30.44))).isoformat()
    ch = [(d["c"][i] / d["c"][i - 1] - 1, i) for i in range(1, len(d["c"])) if d["date"][i] >= start]
    ups = sorted(ch, reverse=True)[:top]
    downs = sorted(ch)[:top]
    ev = [("上昇", r, i) for r, i in ups] + [("下落", r, i) for r, i in downs]
    for x in extra:   # ユーザーが指定した日（大きさの上位に入らなくても加える）
        i = d["date"].index(x)
        if all(e[2] != i for e in ev):
            r = d["c"][i] / d["c"][i - 1] - 1
            ev.append(("上昇" if r > 0 else "下落", r, i))
    ev = sorted(ev, key=lambda x: x[2])
    plan = {}
    for kind, r, i in ev:
        for off in OFFSETS:
            j = i + off
            if 0 <= j < len(d["c"]) and d["date"][j] not in plan:
                plan[d["date"][j]] = {"event": f"{d['date'][i]} {kind} {r * 100:+.1f}%", "offset": off, "j": j}
    return ev, dict(sorted(plan.items()))


def memo_lines(sym):
    r = subprocess.run(["git", "-C", ROOT, "show", f"{MEMO_BRANCH}:銘柄メモ/{sym}.md"], capture_output=True, text=True)
    return r.stdout.splitlines() if r.returncode == 0 else []


def news_asof(lines, asof, days=45):
    lo = (dt.date.fromisoformat(asof) - dt.timedelta(days=days)).isoformat()
    out = []
    for ln in lines:
        m = re.match(r"^\s*- (\d{4}-\d{2}-\d{2})", ln)
        if m and lo <= m.group(1) <= asof:
            out.append(ln.strip())
    return "\n".join(out) or "この期間の記録なし"


def next_earnings(earn, asof):
    later = [e for e in earn if e >= asof]
    return f"{later[0]}（過去の実際の決算日）" if later else "取得不可"


def nlm_env():
    env = dict(os.environ)
    for ln in open("/root/.nlm/env", encoding="utf-8"):
        k, _, v = ln.rstrip("\n").partition("=")
        if k.startswith("NLM_"):
            env[k] = v.strip('"')
    return env


def nlm(env, *args):
    return subprocess.run(["nlm", *args], capture_output=True, text=True, env=env, timeout=600)


def del_images(env, nb):
    r = nlm(env, "source", "list", nb)
    ids = [ln.split("\t")[0] for ln in r.stdout.splitlines()[1:] if re.search(r"\.(png|jpg|jpeg)$", ln.split("\t")[1].lower() if "\t" in ln else "")]
    if ids:
        nlm(env, "source", "delete", "-y", nb, ",".join(ids))


def ask(env, author, images, prompt, out):
    nb = NB[author]
    del_images(env, nb)
    if images:
        r = nlm(env, "source", "add", nb, *images)
        if r.returncode:
            open(out + ".err", "w").write("画像の追加に失敗: " + r.stderr[-300:])
    r = nlm(env, "generate-chat", "--citations", "off", "--prompt-file", prompt, nb)
    open(out, "w", encoding="utf-8").write(r.stdout if r.returncode == 0 else f"送信に失敗: {r.stderr[-300:]}")
    del_images(env, nb)


def prepare_day(sym, d, pool, memo, earn, day, outdir):
    dd = os.path.join(outdir, day)
    os.makedirs(dd, exist_ok=True)
    rules = report(sym, d, pool, asof=day, earn=next_earnings(earn, day))
    open(os.path.join(dd, "rules.md"), "w", encoding="utf-8").write(rules)
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "market_data.py"), "ticker", sym, dd, "--asof", day],
                   capture_output=True, text=True)
    data_f = os.path.join(dd, f"{sym}_{day}_data.txt")
    data = open(data_f, encoding="utf-8").read().strip() if os.path.exists(data_f) else "取得不可"
    data += ("\n\nニュース（既存ツールの銘柄メモのうち、この日以前の日付の項目だけ。過去時点の再現のため、これより後の情報は含まない）:\n"
             + news_asof(memo, day))
    p = open(TEMPLATE, encoding="utf-8").read().replace("{{RULES}}", rules.strip()).replace("{{DATA}}", data)
    open(os.path.join(dd, "prompt.txt"), "w", encoding="utf-8").write(p[:12000])
    return dd, [f for f in (os.path.join(dd, f"{sym}_{day}_chart.png"), os.path.join(dd, f"{sym}_{day}_intraday.png")) if os.path.exists(f)]


# ---------- 集計 ----------

def parse(text):
    v = re.search(r"【([^】]+)】", text)
    pat = re.search(r"現状パターン[^A-Z該]*([ABC]|該当なし)", text)
    res = re.search(r"予約注文[:：]\s*`?\s*〈?([^〉0-9]*)〉?\s*([0-9][0-9,]*\.?[0-9]*)", text)
    kind = res.group(1) if res else ""
    return {"verdict": v.group(1) if v else "不明", "pattern": pat.group(1) if pat else "",
            "order_kind": "逆指値" if "逆指値" in kind else ("指値" if "指値" in kind else ""),
            "price": float(res.group(2).replace(",", "")) if res else None}


def outcome(d, j, a):
    """判定の日 j の翌日に注文した場合。買い＝翌日の寄り付き、買い（予約）＝翌日の高値・安値が届けば約定"""
    n = len(d["c"])
    if j + 1 >= n:
        return "翌日のデータなし", None
    o, h, l = d["o"][j + 1], d["h"][j + 1], d["l"][j + 1]
    v = a["verdict"]
    if v.startswith("買い（予約"):
        p = a["price"]
        if p is None:
            return "予約価格を読み取れず", None
        if a["order_kind"] == "指値" or (a["order_kind"] == "" and p < d["c"][j]):
            if l > p:
                return f"指値{p:,.2f}に届かず", None
            px = min(o, p)
        else:
            if h < p:
                return f"逆指値{p:,.2f}に届かず", None
            px = max(o, p)
    elif v.startswith("買い"):
        px = o
    else:
        px = o   # 様子見でも、翌日の寄り付きで買っていたらどうだったか（見送った値動き）を参考に出す
    r5 = d["c"][min(j + 5, n - 1)] / px - 1
    r10 = d["c"][min(j + 10, n - 1)] / px - 1
    lab = "約定" if v.startswith("買い") else "（参考: 翌日の寄り付きで買っていたら）"
    return f"{lab} {px:,.2f} → 5日後 {r5 * 100:+.1f}%／10日後 {r10 * 100:+.1f}%", r5


def write_report(sym, d, ev, plan, outdir):
    idx = {x: k for k, x in enumerate(d["date"])}
    L = [f"# {sym}: 大きく動いた日の前後で、新ツールの著者はどう判定したか（過去の日付での再現）\n",
         "- 各日の引け時点で見えていたデータ・チャート・ニュース（銘柄メモのその日以前の項目）・過去の決算日だけで判定させた。送信は1回ずつ独立（--webなし）。",
         "- 「その後」は、翌営業日に注文した場合。【買い】＝翌日の寄り付き、【買い（予約）】＝翌日の高値（逆指値）・安値（指値）が届いたときだけ約定。【様子見】は参考として翌日の寄り付きで買っていた場合の値動き。",
         "- スクリプトのパターン: ボリンジャーIII／ミネルヴィニ／ワインスタイン10週の順（A=条件成立、B=成立が目前、−=該当なし）。",
         "- この表は著者（NotebookLM）の回答を機械的に読み取ったもので、Claudeによる売買判断ではない。全文は各日のフォルダの <著者>.txt。\n"]
    stats = {k: [] for k in NB}
    for kind, r, i in ev:
        L.append(f"## {d['date'][i]} {kind} {r * 100:+.1f}%\n")
        L.append("| 日（大きく動いた日からの位置） | 終値（前日比） | スクリプトのパターン | " + " | ".join(NB) + " |")
        L.append("|---|---|---|" + "---|" * len(NB))
        for off in OFFSETS:
            j = i + off
            if not (0 <= j < len(d["c"])):
                continue
            day = d["date"][j]
            dd = os.path.join(outdir, day)
            rules = open(os.path.join(dd, "rules.md"), encoding="utf-8").read() if os.path.exists(os.path.join(dd, "rules.md")) else ""
            m = re.search(r"ボリンジャーIII: (\S+)／ミネルヴィニ: (\S+)／ワインスタイン10週: (\S+?)（", rules)
            sp = "／".join(x.replace("該当なし", "−") for x in m.groups()) if m else "?"
            cells = []
            for au in NB:
                f = os.path.join(dd, f"{au}.txt")
                if not os.path.exists(f):
                    cells.append("未送信")
                    continue
                raw = open(f, encoding="utf-8").read()
                if raw.startswith("送信に失敗"):
                    cells.append("取得できず（NotebookLMの応答が空。1日の使用量の上限と思われる）")
                    continue
                a = parse(raw)
                txt, r5 = outcome(d, j, a)
                if a["verdict"].startswith("買い") and r5 is not None and plan.get(day, {}).get("event", "").startswith(f"{d['date'][i]}"):
                    stats[au].append(r5)
                price = f" {a['order_kind']}{a['price']:,.2f}" if a["verdict"].startswith("買い（予約") and a["price"] else ""
                cells.append(f"【{a['verdict']}】{a['pattern'] and '（' + a['pattern'] + '）'}{price}<br>{txt}")
            pos = "当日" if off == 0 else f"{off:+d}日"
            L.append(f"| {day}（{pos}） | {d['c'][j]:,.2f}（{(d['c'][j] / d['c'][j - 1] - 1) * 100:+.1f}%） | {sp} | " + " | ".join(cells) + " |")
        L.append("")
    L.append("## まとめ（著者ごと。【買い】【買い（予約）】で約定した判定の5日後の損益）\n")
    L.append("| 著者 | 約定した買い | 5日後にプラス | 5日後の平均 |")
    L.append("|---|---|---|---|")
    for au, xs in stats.items():
        L.append(f"| {au} | {len(xs)} | {sum(1 for x in xs if x > 0)} | {(sum(xs) / len(xs) * 100 if xs else 0):+.1f}% |")
    open(os.path.join(outdir, "replay.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


def draw(sym, d, ev, plan, outdir):
    """株価（終値）の上に、判定した日ごとに3人の結論を印で描く。買い＝塗りの丸、買い（予約）＝上向きの三角、様子見＝小さな灰色の点"""
    import matplotlib
    matplotlib.use("Agg")
    import logging
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
    plt.rcParams.update({"font.family": "WenQuanYi Zen Hei", "font.size": 12})
    first = min(plan)
    i0 = max(0, d["date"].index(first) - 10)
    x = list(range(len(d["c"]) - i0))
    C = d["c"][i0:]
    fig, ax = plt.subplots(figsize=(15, 8), dpi=160)
    ax.plot(x, C, color="#5b5b57", lw=1.3)
    colors = {"ボリンジャー": "#2a78d6", "ミネルヴィニ": "#eb6834", "ワインスタイン": "#1baf7a"}
    span = max(C) - min(C)
    for kind, r, i in ev:
        ax.axvline(i - i0, color="#e34948" if kind == "下落" else "#008300", alpha=0.15, lw=8)
    for day in plan:
        j = d["date"].index(day)
        for n, au in enumerate(colors):
            f = os.path.join(outdir, day, f"{au}.txt")
            if not os.path.exists(f):
                continue
            v = parse(open(f, encoding="utf-8").read())["verdict"]
            y = d["c"][j] - span * (0.06 + 0.05 * n)
            if v.startswith("買い（予約"):
                ax.scatter(j - i0, y, marker="^", s=150, color=colors[au], edgecolor="white", lw=1.5, zorder=5)
            elif v.startswith("買い"):
                ax.scatter(j - i0, y, marker="o", s=150, color=colors[au], edgecolor="white", lw=1.5, zorder=5)
            else:
                ax.scatter(j - i0, y, marker="o", s=18, color="#b0b0aa", zorder=4)
    hs = [Line2D([], [], marker="o", ls="", color=c, markersize=10, label=f"{au}（上から{n + 1}段目）") for n, (au, c) in enumerate(colors.items())]
    hs += [Line2D([], [], marker="o", ls="", color="#8a8a85", markersize=10, label="丸＝買い（翌日の寄り付き）"),
           Line2D([], [], marker="^", ls="", color="#8a8a85", markersize=10, label="三角＝買い（予約）"),
           Line2D([], [], marker="o", ls="", color="#b0b0aa", markersize=4, label="小さな灰色の点＝様子見"),
           Line2D([], [], color="#008300", alpha=0.3, lw=8, label="大きく上昇した日"),
           Line2D([], [], color="#e34948", alpha=0.3, lw=8, label="大きく下落した日")]
    ax.legend(handles=hs, loc="upper left", fontsize=10, framealpha=0.9)
    ticks = [k for k in x if k >= 5 and d["date"][i0 + k][:7] != d["date"][i0 + k - 1][:7]]
    ax.set_xticks(ticks, [d["date"][i0 + k][:7] for k in ticks])
    ax.grid(alpha=0.2)
    ax.set_title(f"{sym} 大きく動いた日の前後2日の、著者の判定（その日の引け時点のデータだけで判定させた再現）", loc="left", fontsize=14)
    png = os.path.join(outdir, f"{sym}_replay.png")
    fig.savefig(png, bbox_inches="tight")
    return png


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ticker")
    ap.add_argument("outdir")
    ap.add_argument("cmd", choices=["plan", "run", "report"])
    ap.add_argument("--months", type=int, default=6)
    ap.add_argument("--top", type=int, default=3)
    ap.add_argument("--earnings", default="")
    ap.add_argument("--extra", default="", help="加える日（カンマ区切り）")
    a = ap.parse_args()
    sym = a.ticker.upper()
    d = fetch_daily(sym)
    ev, plan = events(d, a.months, a.top, [x for x in a.extra.split(",") if x])
    earn = sorted(x for x in a.earnings.split(",") if x)
    os.makedirs(a.outdir, exist_ok=True)
    if a.cmd == "plan":
        for kind, r, i in ev:
            print(f"{d['date'][i]} {kind} {r * 100:+.1f}%")
        print(f"判定する日: {len(plan)}日（著者への質問 {len(plan) * 3}回）: {', '.join(plan)}")
        return
    if a.cmd == "run":
        pool = load_pool()
        memo = memo_lines(sym)
        env = nlm_env()
        for k, day in enumerate(plan, 1):
            done = [os.path.join(a.outdir, day, f"{au}.txt") for au in NB]
            if all(os.path.exists(f) and not open(f, encoding="utf-8").read().startswith("送信に失敗") for f in done):
                continue
            dd, images = prepare_day(sym, d, pool, memo, earn, day, a.outdir)
            with ThreadPoolExecutor(3) as ex:
                list(ex.map(lambda au: ask(env, au, images, os.path.join(dd, "prompt.txt"), os.path.join(dd, f"{au}.txt")), NB))
            print(f"[{k}/{len(plan)}] {day} 送信済み", file=sys.stderr, flush=True)
    write_report(sym, d, ev, plan, a.outdir)
    print("チャート:", draw(sym, d, ev, plan, a.outdir), file=sys.stderr)


if __name__ == "__main__":
    main()
