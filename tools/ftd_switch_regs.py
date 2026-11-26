#!/usr/bin/env python3
"""守りに入る合図と、フォロースルー・デーなどの「攻めに戻す合図」から、守りの間の日の集合を作る
（2026-11-26 ユーザーの指示「検証して」: 底の確認のフォロースルー・デーを、2つの口を切り替える形の戻す合図に使う）。

守りに入る合図（tools/signal_scan.py の --regs-out の sets）: bsk50＝87銘柄の平均が下向きの50日線の下、b50＝87銘柄の50日線より上が30%未満。
攻めに戻す合図（backtest_retest.py の OPT_EQDUMP の _regs）: bot_FTD_N＝フォロースルー・デー（ナスダック、オニール）、bot_FTD_S＝同（SOX）、
bot_W30＝SOXが上向きの30週線の上に戻った日（ワインスタインのステージ2）。
守りに入った日の後（同じ日は数えない）に戻す合図が出たら、その日の引けで守りを終える。「または10日」は、守りに入る合図が10取引日続けて消えても終える形。
出力は tools/stat_compare.py --regs に渡す形（labels・sets）。
使い方: tools/ftd_switch_regs.py --signals FILE --eq87 FILE --out FILE
数値の事実だけで、Claudeの売買判断は含まない。
"""
import argparse
import gzip
import json


def jload(p):
    return json.load(gzip.open(p, "rt") if p.endswith(".gz") else open(p))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--signals", required=True)
    ap.add_argument("--eq87", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    sg = json.load(open(a.signals))
    d87 = jload(a.eq87)
    regs = d87["_regs"]
    days = d87[next(k for k in d87 if not k.startswith("_"))]["days"]
    ENT = {"bsk50": "87銘柄の平均が下向きの50日線の下", "b50": "87銘柄の50日線より上が30%未満"}
    EXT = {"bot_FTD_N": "ナスダックのフォロースルー・デー", "bot_FTD_S": "SOXのフォロースルー・デー", "bot_W30": "SOXのステージ2"}
    labels, sets = {}, {}
    for ek, el in ENT.items():
        E = set(sg["sets"][ek])
        labels[ek], sets[ek] = el + "（戻す合図なし）", sorted(E)
        for xk, xl in EXT.items():
            X = set(regs[xk])
            for tm in (None, 10):
                on, t0, off_run, out = False, -1, 0, []
                for k, d in enumerate(days):
                    if not on and d in E:
                        on, t0, off_run = True, k, 0
                    elif on:
                        off_run = 0 if d in E else off_run + 1
                        if (d in X and k > t0) or (tm and off_run >= tm):
                            on = False
                    if on:
                        out.append(d)
                key = f"{ek}>{xk}" + (f"|{tm}" if tm else "")
                labels[key] = f"{el}で守り・{xl}で戻す" + (f"（または合図が{tm}日消えたら戻す）" if tm else "")
                sets[key] = out
    for k, v in sets.items():
        n_sw = sum(1 for j in range(1, len(days)) if (days[j] in set(v)) != (days[j - 1] in set(v)))
        print(f"{labels[k]}: 守りの日 {len(v) / len(days):.0%}、切り替え {n_sw}回、2026-06〜の守りの日 {sum(1 for d in v if d >= '2026-06-01')}")
    json.dump({"labels": labels, "sets": sets}, open(a.out, "w"), ensure_ascii=False)


if __name__ == "__main__":
    main()
