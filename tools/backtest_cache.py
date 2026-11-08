#!/usr/bin/env python3
"""バックテストのデータ（株価・業種・決算日）を作り直す・GitHubに保存する・戻す（2026-11-06 ユーザーの指示
「何度も検証で使うのだからどのセッションでも使用できるようきちんと保存して」）

データは ~/.cache/stock_backtest/ に置く（backtest_lib.DEFAULT_CACHE）。この場所はセッションの作業環境（コンテナ）の中にあり、
環境が入れ替わると消える。そこで、ファイルのまま GitHub のデータ用ブランチ（DATA_BRANCH）に普通のコミットで保存し、次のセッションで戻す。
（強制の上書きはしない。2回目以降の保存は変わった分だけが増える）

使い方:
  tools/backtest_cache.py restore            # GitHubから戻す（約1分）。バックテストを始める前にまずこれ
  tools/backtest_cache.py build              # インターネットから全部作り直す（約30〜60分）
  tools/backtest_cache.py refresh [--until YYYY-MM-DD]
                                             # 株価を最新に取り直す（until の日を含めない。米国の引け前は今日を入れない）
  tools/backtest_cache.py save               # 今のデータをGitHubのデータ用ブランチに保存（普通のコミット）
  tools/backtest_cache.py status             # 今のデータの中身（銘柄数・最終日）

作り直す中身（build）:
  1. S&P500の2015年以降の構成銘柄と日足（backtest_lib fetch）＋ SPY・QQQ・^VIX
  2. 時価総額10億ドル以上の米国株の業種（universe.json）と日足（theme_universe fetch）
  3. 指数・ETF（^GSPC・^SOX・^NDX・^TNX・SOXX・HYG・IEI・LQD・BKLN・業種ETF）と監視銘柄（テーマ監視銘柄.md）の日足
  4. universe.json にないS&P500の構成銘柄の業種（industry_extra.json。Yahoo から取れたものだけ）
  5. 過去の決算発表日（fetch_earnings_history）
  6. 恩株ツールの売上（SECの決算データ。backtest_onkabu_features fetch・onkabu_fund_predecessor）
"""
import argparse
import datetime as dt
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import backtest_lib as bl

CACHE = bl.DEFAULT_CACHE
DATA_BRANCH = "data/backtest-cache"
EXTRA = ["SPY", "QQQ", "^VIX", "^GSPC", "^SOX", "^NDX", "^IXIC", "^TNX", "^MOVE", "SOXX", "SMH", "TQQQ", "HYG", "IEI", "LQD", "BKLN", "JNK", "TLT",
         "XLE", "XLV", "XLU", "XLP", "XLF", "XLI", "XLB", "XLY", "XLK", "XLC", "XLRE"]


def run(cmd):
    print("$", " ".join(cmd), flush=True)
    r = subprocess.run(cmd, cwd=ROOT)
    if r.returncode:
        print(f"（終了コード {r.returncode}。続ける）", flush=True)


def watch_syms():
    out = []
    for line in open(os.path.join(ROOT, "新分析ツール", "テーマ監視銘柄.md"), encoding="utf-8"):
        m = re.match(r"^\| ([A-Z][A-Z.]*) \|", line)
        if m:
            out.append(m.group(1))
    return sorted(set(out))


def fetch_syms(syms, force=False, until=None):
    os.makedirs(os.path.join(CACHE, "prices"), exist_ok=True)
    def one(s):
        p = os.path.join(CACHE, "prices", s + ".json")
        tmp = p + ".new"
        if os.path.exists(tmp):
            os.remove(tmp)
        if os.path.exists(p) and not force:
            return True
        ok = bl.fetch_one(s.replace(".", "-") if not s.startswith("^") else s, tmp)
        if not ok or not os.path.exists(tmp):
            return os.path.exists(p)
        if until:
            rows = [r for r in json.load(open(tmp)) if r[0] < until]
            json.dump(rows, open(tmp, "w"))
        os.replace(tmp, p)
        return True
    with ThreadPoolExecutor(8) as ex:
        ok = list(ex.map(one, syms))
    return sum(ok), len(syms)


def cmd_build(a):
    t0 = time.time()
    os.makedirs(CACHE, exist_ok=True)
    run([sys.executable, "tools/backtest_lib.py", "fetch"])
    run([sys.executable, "tools/theme_universe.py", "fetch"])
    n, m = fetch_syms(EXTRA + watch_syms())
    print(f"指数・ETF・監視銘柄の日足 {n}/{m}", flush=True)
    # universe.json にない構成銘柄の業種
    uni = json.load(open(os.path.join(CACHE, "universe.json")))
    have = {os.path.basename(p)[:-5] for p in glob.glob(os.path.join(CACHE, "prices", "*.json"))}
    members = bl.load_members(CACHE)
    todo = sorted(s for s in members if s in have and s not in uni)
    sys.path.insert(0, HERE)
    import theme_universe as tu
    extra = {}
    with ThreadPoolExecutor(8) as ex:
        for s, p in zip(todo, ex.map(lambda s: tu.yahoo_profile(s.replace(".", "-")), todo)):
            if p and p["industry"]:
                extra[s] = p
    json.dump(extra, open(os.path.join(CACHE, "industry_extra.json"), "w"), ensure_ascii=False, indent=0)
    print(f"universe.json にない構成銘柄 {len(todo)} 銘柄のうち、業種が取れた {len(extra)}", flush=True)
    run([sys.executable, "tools/fetch_earnings_history.py"])
    run([sys.executable, "tools/backtest_onkabu_features.py", "fetch"])   # 恩株ツールの売上（SECの決算データ、S&P500の構成銘柄）
    run([sys.executable, "tools/onkabu_fund_predecessor.py"])          # ティッカーを変えた会社の、変更前の売上を足す
    trim_open_day()
    print(f"作り直し {time.time() - t0:.0f}秒", flush=True)
    cmd_status(a)


def open_day():
    """米国の引け（16:30 ET）前なら今日の日付（その日の行は途中の値なので入れない）、引け後なら None"""
    from zoneinfo import ZoneInfo
    now = dt.datetime.now(ZoneInfo("America/New_York"))
    return now.date().isoformat() if now.hour * 60 + now.minute < 16 * 60 + 30 else None


def trim_open_day():
    d = open_day()
    if not d:
        return
    n = 0
    for p in glob.glob(os.path.join(CACHE, "prices", "*.json")):
        rows = json.load(open(p))
        if rows and rows[-1][0] >= d:
            json.dump([r for r in rows if r[0] < d], open(p + ".new", "w"))
            os.replace(p + ".new", p)
            n += 1
    print(f"引け前のため {d} の行を外した: {n} 銘柄", flush=True)


def cmd_refresh(a):
    syms = sorted(os.path.basename(p)[:-5] for p in glob.glob(os.path.join(CACHE, "prices", "*.json")))
    until = a.until or open_day() or "9999-12-31"
    n, m = fetch_syms(syms, force=True, until=until)
    print(f"取り直し {n}/{m}（{until} より前まで）")
    cmd_status(a)


def cmd_status(a):
    ps = glob.glob(os.path.join(CACHE, "prices", "*.json"))
    last = {}
    for s in ("SPY", "^SOX", "NVDA"):
        p = os.path.join(CACHE, "prices", s + ".json")
        if os.path.exists(p):
            last[s] = json.load(open(p))[-1][0]
    files = {f: os.path.exists(os.path.join(CACHE, f)) for f in ("members.csv", "universe.json", "industry_extra.json", "earnings.json")}
    print(f"データ: {CACHE}  株価 {len(ps)} 銘柄、最終日 {last}、{files}")


def git_url():
    return subprocess.run(["git", "remote", "get-url", "origin"], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def _clone(dst):
    """データ用ブランチを浅く取る。ブランチがまだなければ False"""
    for attempt in range(4):
        r = subprocess.run(["git", "clone", "-q", "--depth", "1", "--single-branch", "--branch", DATA_BRANCH, git_url(), dst],
                           capture_output=True, text=True)
        if r.returncode == 0:
            return True
        if "not found" in (r.stderr or "").lower() or "couldn't find remote ref" in (r.stderr or "").lower():
            return False
        shutil.rmtree(dst, ignore_errors=True)
        time.sleep(2 ** (attempt + 1))
    sys.exit(f"GitHubのデータ用ブランチ {DATA_BRANCH} を取れませんでした")


IGNORE = shutil.ignore_patterns("*.pkl", "*.new", "long")   # long はその日に取り直す一時データ


def cmd_save(a):
    """ファイルのまま（圧縮せず）データ用ブランチに普通のコミットで保存する。強制の上書きはしない（2回目以降は変わった分だけ増える）"""
    for attempt in range(3):
        tmp = tempfile.mkdtemp()
        try:
            repo = os.path.join(tmp, "repo")
            if not _clone(repo):
                os.makedirs(repo)
                subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
                subprocess.run(["git", "checkout", "-q", "--orphan", "data"], cwd=repo, check=True)
            dst = os.path.join(repo, "cache")
            shutil.rmtree(dst, ignore_errors=True)
            shutil.copytree(CACHE, dst, ignore=IGNORE)
            ps = glob.glob(os.path.join(dst, "prices", "*.json"))
            spy = os.path.join(dst, "prices", "SPY.json")
            man = {"saved_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "prices": len(ps),
                   "last_day": json.load(open(spy))[-1][0] if os.path.exists(spy) else None}
            json.dump(man, open(os.path.join(repo, "manifest.json"), "w"), ensure_ascii=False, indent=1)
            open(os.path.join(repo, "README.md"), "w", encoding="utf-8").write(
                "# バックテストのデータ（`tools/backtest_cache.py` が書くブランチ）\n\n"
                "`cache/` は ~/.cache/stock_backtest/ の中身（株価・業種・決算日）。戻すのは `python3 tools/backtest_cache.py restore`、"
                "保存は `save`。手で編集しない。\n")
            g = lambda *c: subprocess.run(["git", *c], cwd=repo, check=True)
            g("add", "-A")
            if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=repo).returncode == 0:
                print("変わったところがないので保存しない")
                return
            g("-c", "user.name=Claude", "-c", "user.email=noreply@anthropic.com", "commit", "-q", "-m",
              f"バックテストのデータ（株価 {man['prices']} 銘柄、最終日 {man['last_day']}）")
            r = subprocess.run(["git", "push", "-q", git_url(), f"HEAD:refs/heads/{DATA_BRANCH}"], cwd=repo)
            if r.returncode == 0:
                print(f"保存しました: {DATA_BRANCH}（株価 {man['prices']} 銘柄、最終日 {man['last_day']}）")
                return
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        time.sleep(2 ** (attempt + 1))
    sys.exit("GitHubへの保存に3回失敗しました")


def cmd_restore(a):
    tmp = tempfile.mkdtemp()
    try:
        repo = os.path.join(tmp, "repo")
        if not _clone(repo):
            sys.exit(f"データ用ブランチ {DATA_BRANCH} がまだありません（build してから save）")
        man = json.load(open(os.path.join(repo, "manifest.json")))
        if os.path.exists(CACHE) and not a.keep:
            shutil.rmtree(CACHE)
        shutil.copytree(os.path.join(repo, "cache"), CACHE, dirs_exist_ok=True)
        print(f"戻しました: 保存 {man['saved_at']}、株価 {man['prices']} 銘柄、最終日 {man['last_day']}")
        cmd_status(a)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build")
    r = sub.add_parser("refresh")
    r.add_argument("--until", help="この日付より前の行だけ入れる（既定: 今日。米国の引け前に取ると今日の値が途中の値になるため）")
    sub.add_parser("save")
    rs = sub.add_parser("restore")
    rs.add_argument("--keep", action="store_true", help="今のデータを消さずに上書きする")
    sub.add_parser("status")
    a = ap.parse_args()
    {"build": cmd_build, "refresh": cmd_refresh, "save": cmd_save, "restore": cmd_restore, "status": cmd_status}[a.cmd](a)


if __name__ == "__main__":
    main()
