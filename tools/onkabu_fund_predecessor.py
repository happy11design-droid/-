#!/usr/bin/env python3
"""ティッカーを変えた会社で、後継の会社のSECの記録（CIK）に変更前の売上がないものに、変更前の会社の売上を足す（2026-10-18）

恩株ツールは、構成銘柄の一覧で古いティッカーを後継のティッカーに付け替えて読む（backtest_lib.TICKER_ALIAS）。
売上は後継のティッカーの CIK から取るので、持ち株会社を作り直した会社などは変更前の期間の売上がない。
例: HollyFrontier（HFC, CIK 48039）→ HF Sinclair（DINO, 2022年〜の新しい CIK）。DINO は2021年5月に6カ月で+113%上げていて、
売上がないと恩株ツールの「売上≧10%」の条件で必ず外れていた。

使い方:
  tools/onkabu_fund_predecessor.py          # PRED の会社の売上を取り、後継のファイル（onkabu_fund/<後継>.json）に、
                                           # 後継の記録より前に提出されたものだけを足す。元のファイルは <後継>.json.orig に残す
"""
import json
import os
import shutil
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_onkabu as ob
from backtest_lib import DEFAULT_CACHE
from backtest_onkabu_features import CONCEPTS

# 後継のティッカー: (変更前のティッカー, 変更前の会社の CIK)。後継の CIK に変更前の期間の売上がないもの（2026-10-18 に確かめた）
PRED = {
    "DINO": ("HFC", 48039),        # HollyFrontier → HF Sinclair（2022-03 に持ち株会社を新設）
    "VTRS": ("MYL", 1623613),      # Mylan N.V. → Viatris（2020-11 に Upjohn と合併）
}


def rows_of(cik, tags):
    out = []
    for tag in tags:
        t = ob.sec_get(f"https://data.sec.gov/api/xbrl/companyconcept/CIK{cik:010d}/us-gaap/{tag}.json")
        time.sleep(0.15)
        if not t:
            continue
        for u, fs in json.loads(t).get("units", {}).items():
            if not isinstance(fs, list):
                continue
            for f in fs:
                if f.get("filed") and f.get("start") and f.get("val") is not None:
                    out.append((f["filed"], f["start"], f["end"], f["val"]))
    return sorted(set(out))


def main():
    d = os.path.join(DEFAULT_CACHE, "onkabu_fund")
    for new, (old, cik) in PRED.items():
        p = os.path.join(d, new + ".json")
        orig = p + ".orig"
        if not os.path.exists(orig):
            shutil.copy(p, orig)
        cur = json.load(open(orig))
        res = {}
        for key, tags in CONCEPTS.items():
            mine = [tuple(r) for r in cur.get(key, [])]
            first = min((r[0] for r in mine), default="9999")
            prev = [r for r in rows_of(cik, tags) if r[0] < first]   # 後継の最初の提出より前のものだけ
            res[key] = sorted(set(mine + prev))
            print(f"{new}（{old} CIK {cik}）{key}: 後継 {len(mine)}件（最初の提出 {first}）＋変更前 {len(prev)}件")
        json.dump(res, open(p, "w"))


if __name__ == "__main__":
    main()
