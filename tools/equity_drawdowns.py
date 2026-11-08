#!/usr/bin/env python3
"""OPT_EQDUMP（今のルールの毎日の資金、乱数30通り）から、−X%以上の下げごとに 高値の日・底の日・下落率・底までの日数・高値を戻すまでの日数 を数える。
使い方: python3 dd_episodes.py <json> <見出し> [--th 0.20]"""
import json, sys, statistics as st, datetime as dt
path, lab = sys.argv[1], sys.argv[2]
th = float(sys.argv[sys.argv.index("--th") + 1]) if "--th" in sys.argv else 0.20
a = json.load(open(path))
days = a["days"]
s15 = next(k for k, d in enumerate(days) if d >= "2015-01-02")
E = [e for e in a["eq"]]
# 乱数30通りの中央値の資金（日ごと）
med = [st.median(e[k] for e in E if e[k] is not None) if any(e[k] is not None for e in E) else None for k in range(len(days))]

def episodes(eq):
    out, pk, pkk, trough, trk, ind = [], None, None, None, None, False
    for k in range(s15, len(days)):
        x = eq[k]
        if x is None:
            continue
        if pk is None or x >= pk:
            if ind:
                out.append((pkk, trk, 1 - trough / pk, k))
            pk, pkk, ind, trough, trk = x, k, False, x, k
        else:
            if x < trough:
                trough, trk = x, k
            if 1 - trough / pk >= th:
                ind = True
    if ind:
        out.append((pkk, trk, 1 - trough / pk, None))
    elif pk is not None and 1 - trough / pk > 0:
        out.append((pkk, trk, 1 - trough / pk, None))   # 今の下げ（目安に届かなくても出す）
    return out

mon = lambda n: f"{n / 21:.1f}か月"
print(f"### {lab}: 資金の下げ（高値から−{th:.0%}以上）と戻り（乱数30通りの中央値の資金。日数は取引日、1か月≒21取引日）\n")
print("| 高値の日 | 底の日 | 下落率 | 高値→底 | 底→高値を戻す | 高値を戻した日 | 高値から戻すまで | 乱数30通りでの 下落率の幅・戻すまでの幅 |")
print("|---|---|---|---|---|---|---|---|")
for pkk, trk, ddv, rk in episodes(med):
    if ddv < th and rk is not None:
        continue
    # 乱数ごとに、同じ高値の日の前後にある下げを探す
    rngd, rngr = [], []
    for e in E:
        for p2, t2, d2, r2 in episodes(e):
            if abs(p2 - pkk) <= 40 or (p2 <= trk <= (r2 or len(days))):
                rngd.append(d2)
                rngr.append((r2 - p2) if r2 else None)
                break
    rr = [x for x in rngr if x is not None]
    rng = f"{min(rngd) * 100:.0f}〜{max(rngd) * 100:.0f}%・" + (f"{mon(min(rr))}〜{mon(max(rr))}" if rr else "") + (f"（まだ {len(rngr) - len(rr)}通り）" if len(rr) < len(rngr) else "") if rngd else "—"
    print(f"| {days[pkk]} | {days[trk]} | −{ddv * 100:.0f}% | {mon(trk - pkk)} | {mon(rk - trk) if rk else 'まだ'} | {days[rk] if rk else 'まだ'} | {mon(rk - pkk) if rk else f'まだ（{mon(len(days) - 1 - pkk)}経過）'} | {rng} |")
cur = med[-1] / max(x for x in med[s15:] if x)
print(f"\n- 最終日（{days[-1]}）の資金は高値から {(cur - 1) * 100:+.1f}%（乱数30通りの中央値）")
