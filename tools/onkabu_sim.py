#!/usr/bin/env python3
"""恩株ツールの資金の再現（速い版）。合図は前もって日ごとの銘柄の一覧にしておく。

決まり:
  - 合図はその日の終値で判定。買い方（entry）:
      "open"    翌日の寄り付きで買う
      "dip5"    10取引日以内に、合図の日の終値の−5%まで下がったら買う（指値）。下がらなければ買わない
      "dip10"   20取引日以内に −10%（同上）
      "confirm" 翌日の終値が合図の日の終値より高ければ、その次の日の寄り付きで買う
      "half"    翌日の寄り付きで半分、買値の+10%になったら残り半分（枠は1つ）
  - 1回に買う金額 = （待っている現金＋持っている株の買値の合計）÷ 枠の数
  - 2倍（買値の2倍の終値）で税引き後に元本が戻る株数（55.7%）を売り、残りは恩株（枠から外れる）
  - 損切り stop: 終値が買値の (1−stop) 以下で売る。時間 T: T取引日たっても2倍にならなければ売る
  - 乗り換え rot: 枠が埋まっているときに新しい合図が出たら、持っている株のうち値上がり率が一番低いものが rot 未満なら売って乗り換える
  - 売りは終値。売買コスト片道0.1%。利益に20.315%の税（損失との通算はしない）
  - 待っている現金は cash_px（日付→価格）に置く（値上がりへの税は考えない）。None なら0%
"""
import random

TAX = 0.20315
SELL_AT_2X = 1 / (2 - TAX)
COST = 0.001


def simulate(feats, days, sig_by_day, slots=4, stop=None, T=252, rot=None, entry="open", cash_px=None, seed=0,
             capital=6000.0, collect=False, order="random"):
    """order: 枠より多く合図が出たときの選び方。"random"・"mom_desc"（6カ月の上昇が大きい順）・"mom_asc"（小さい順）・
    "rev_desc"（売上の伸びが大きい順）・"vol_asc"（直近1カ月の上昇が小さい順）"""
    rnd = random.Random(seed)
    pos = {}
    for s, f in feats.items():
        pos[s] = {d: k for k, d in enumerate(f["date"])}
    cash = capital
    active = {}      # sym -> dict(sh, px, t, add)
    onk = {}         # sym -> 株数
    pending = []     # (sym, kind, 価格, 期限のt)
    curve, log = [], []
    n_onk = 0

    def price(s, d, key="c"):
        k = pos[s].get(d)
        return None if k is None else feats[s][key][k]

    def sell(s, d, px, why, frac=1.0):
        nonlocal cash
        p = active[s]
        sh = p["sh"] * frac
        proceeds = sh * px * (1 - COST)
        cash += proceeds - TAX * max(0.0, proceeds - sh * p["px"])
        if collect:
            log.append((s, p["d0"], d, px / p["px"], why))
        if frac < 1.0:
            onk[s] = onk.get(s, 0.0) + p["sh"] - sh
        del active[s]

    def buy(s, d, px, t, amt=None):
        nonlocal cash
        basis = cash + sum(p["sh"] * p["px"] for p in active.values())
        a = min(cash, amt if amt is not None else basis / slots)
        if a < 50:
            return
        px *= (1 + COST)
        if s in active:     # half の買い増し
            p = active[s]
            tot = p["sh"] * p["px"] + a
            p["sh"] += a / px
            p["px"] = tot / p["sh"]
            p["add"] = False
        else:
            active[s] = {"sh": a / px, "px": px, "t": t, "add": entry == "half", "d0": d}
        cash -= a

    for t, d in enumerate(days):
        if cash_px and t > 0 and cash > 0 and d in cash_px and days[t - 1] in cash_px:
            cash *= cash_px[d] / cash_px[days[t - 1]]
        # 1) 寄り付き・指値の約定
        keep = []
        for s, kind, lim, exp in pending:
            if s in active or (len(active) >= slots and kind != "add"):
                continue
            o, l = price(s, d, "o"), price(s, d, "l")
            if o is None:
                continue
            if kind == "open":
                buy(s, d, o, t)
            elif kind == "half":
                basis = cash + sum(p["sh"] * p["px"] for p in active.values())
                buy(s, d, o, t, amt=basis / slots / 2)
            elif kind == "limit":
                if l <= lim:
                    buy(s, d, min(o, lim), t)
                elif t < exp:
                    keep.append((s, kind, lim, exp))
            elif kind == "confirm":
                keep.append((s, kind, lim, exp))      # 終値で判定する（下の 2b）
        pending = keep
        # 2) 終値で 2倍・損切り・時間・買い増し・上場廃止
        for s in list(active):
            p = active[s]
            c = price(s, d)
            if c is None:
                if d > feats[s]["date"][-1]:
                    sell(s, d, feats[s]["c"][-1], "上場廃止")
                continue
            if c >= 2 * p["px"]:
                sell(s, d, c, "2倍", SELL_AT_2X)
                n_onk += 1
            elif stop is not None and c <= p["px"] * (1 - stop):
                sell(s, d, c, "損切り")
            elif t - p["t"] >= T:
                sell(s, d, c, "時間")
            elif p.get("add") and c >= p["px"] * 1.10:
                # 残り半分（簡単のため、翌日の寄り付きでなく今日の終値で買う）
                basis = cash + sum(q["sh"] * q["px"] for q in active.values())
                buy(s, d, c, p["t"], amt=basis / slots / 2)
        # 2b) confirm: 合図の翌日の終値が合図の日の終値より高ければ、次の日の寄り付きで買う
        keep = []
        for q in pending:
            if q[1] == "confirm":
                c = price(q[0], d)
                if c is not None and c > q[2]:
                    keep.append((q[0], "open", 0, t + 1))
            else:
                keep.append(q)
        pending = keep
        for s in list(onk):
            if d > feats[s]["date"][-1]:
                c = feats[s]["c"][-1]
                cash += onk[s] * c * (1 - COST) * (1 - TAX)
                del onk[s]
        # 3) 合図
        today = [s for s in sig_by_day.get(d, ()) if s not in active and not any(q[0] == s for q in pending)]
        rnd.shuffle(today)
        if order != "random":
            key = {"mom_desc": ("r126", -1), "mom_asc": ("r126", 1), "rev_desc": ("rev", -1), "vol_asc": ("r21", 1)}[order]
            def kv(x):
                v = feats[x][key[0]][pos[x][d]]
                return 9e9 if v != v else key[1] * v
            today.sort(key=kv)
        free = slots - len(active) - sum(1 for q in pending if q[1] != "add")
        for s in today:
            if free <= 0 and rot is not None and active:
                worst = min(active, key=lambda x: (price(x, d) or active[x]["px"]) / active[x]["px"])
                wc = price(worst, d)
                if wc is not None and wc / active[worst]["px"] - 1 < rot:
                    sell(worst, d, wc, "乗り換え")
                    free += 1
            if free <= 0:
                break
            c = price(s, d)
            if entry == "open":
                pending.append((s, "open", 0, t + 1))
            elif entry == "half":
                pending.append((s, "half", 0, t + 1))
            elif entry == "dip5":
                pending.append((s, "limit", c * 0.95, t + 10))
            elif entry == "dip10":
                pending.append((s, "limit", c * 0.90, t + 20))
            elif entry == "confirm":
                pending.append((s, "confirm", c, t + 1))   # 翌日の終値で判定
            free -= 1
        eq = cash
        for s, p in active.items():
            c = price(s, d)
            eq += p["sh"] * (c if c is not None else feats[s]["c"][-1])
        for s, sh in onk.items():
            c = price(s, d)
            eq += sh * (c if c is not None else feats[s]["c"][-1])
        curve.append(eq)
    return {"curve": curve, "n_onk": n_onk, "log": log, "onk": onk}


def metrics(curve, days):
    import datetime as dt
    yrs = (dt.date.fromisoformat(days[-1]) - dt.date.fromisoformat(days[0])).days / 365.25
    peak = mdd = 0.0
    for v in curve:
        peak = max(peak, v)
        mdd = max(mdd, 1 - v / peak)
    return (curve[-1] / curve[0]) ** (1 / yrs) - 1, mdd
