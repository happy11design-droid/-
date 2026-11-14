#!/usr/bin/env python3
"""Fable 5.2 の大胆な策（`新分析ツール/Fableの提案_2026-11-13.md` 8節）のバックテスト（2026-11-14 ユーザーの指示「全てテストして」）

各策を「足（そで）」＝別の資金の毎日の価値として作り、今の新分析ツール・恩株ツールの税込みの毎日の資金と組み合わせる。
- 新分析ツール: `~/.cache/stock_backtest/results/tax_87.json`・`tax_free.json`（backtest_retest.py の OPT_TAX=1 の書き出し、
  今のルール＝RSの高い順・急落の底は2%下の指値、乱数30通り、2015-01-02〜2026-11-06）
- 恩株ツール: `results/fable_onkabu.json`（tools/fable_onkabu_curve.py、1銘柄・4,500ドル・待っている現金はQQQ、課税口座とNISA）
- 指数・ETF・金利・為替: tools/fable_data.py（long/index/<記号>_full.json）

税: どの足も、売って確定した損益（利息を含む）をその足の中で暦年ごとに通算し、年末に利益の20.315%を払う（損失の繰越なし。
最後に持っているものには税をかけない＝今までの記録と同じ）。足の間の損益の通算はしない（実際は通算できるので少し厳しめ）。
手数料: 片道0.132%（ムームー証券）。

使い方: python3 tools/fable_ideas.py [--out FILE]
"""
import argparse
import bisect
import datetime as dt
import json
import math
import os
import pickle
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fable_data as fd  # noqa: E402

CACHE = os.path.expanduser("~/.cache/stock_backtest/")
TAX = 0.20315
FEE = 0.00132
LEV_FEE = {2: 0.0095, 3: 0.0095}   # 2倍・3倍ETFの年の経費（QLD 0.95%、TQQQ 0.84〜0.95%、SOXL 0.75〜0.95%）
SPREAD = 0.004                      # レバレッジETFの借り入れの上乗せ（年、短期金利に足す。作った値段を実物に合わせるため）


# ---------------- データ ----------------

def series(sym):
    """{日付: 調整後終値}, {日付: 調整後始値}"""
    d = fd.load(sym)
    return {k: v[3] for k, v in d.items()}, {k: v[0] for k, v in d.items()}


class Mkt:
    def __init__(self):
        self.ndx_c, _ = series("^NDX")
        self.days = sorted(d for d in self.ndx_c if d >= "1986-01-02")
        self.q_c, self.q_o = series("QQQ")
        irx, _ = series("^IRX")
        self.sox_c, self.sox_o = series("^SOX")
        self.vxn, _ = series("^VXN")
        self.jpy, _ = series("JPY=X")
        self.gld, _ = series("GLD")
        self.tlt, _ = series("TLT")
        self.xle, _ = series("XLE")
        self.real = {s: series(s) for s in ("QLD", "TQQQ", "SOXL")}
        D = self.days
        # 前の値で埋める
        def ff(m):
            out, last = [], None
            for d in D:
                last = m.get(d, last)
                out.append(last)
            return out
        self.NDX = ff(self.ndx_c)
        self.QQQc = ff(self.q_c)
        self.SOX = ff(self.sox_c)
        self.VXN = ff(self.vxn)
        self.JPY = ff(self.jpy)
        self.IRX = [x if x is not None else 5.0 for x in ff(irx)]
        self.idx = {d: k for k, d in enumerate(D)}
        n = len(D)
        # 指数の1日の騰落（配当込み）: QQQがある日はQQQの調整後終値、ない日はNDX＋配当0.8%/年
        self.r_q = [0.0] * n
        for k in range(1, n):
            a, b = D[k - 1], D[k]
            if a in self.q_c and b in self.q_c:
                self.r_q[k] = self.q_c[b] / self.q_c[a] - 1
            else:
                self.r_q[k] = self.NDX[k] / self.NDX[k - 1] - 1 + 0.008 / 252
        self.r_sox = [0.0] + [self.SOX[k] / self.SOX[k - 1] - 1 if self.SOX[k] and self.SOX[k - 1] else 0.0 for k in range(1, n)]
        self.rf = [x / 100 / 252 for x in self.IRX]   # 短期国債（13週）の利回りの1日分
        self.cash_r = [max(0.0, x - 0.0014 / 252) for x in self.rf]   # 短期国債のETF（BIL）相当
        # 移動平均・RSI(2)・20日の値動き
        self.q_sma200 = sma(self.NDX, 200)
        self.q_sma5 = sma(self.NDX, 5)
        self.sox_sma5 = sma([x or 0 for x in self.SOX], 5)
        self.q_rsi2 = rsi(self.NDX, 2)
        self.q_vol20 = [None] * n
        for k in range(21, n):
            xs = self.r_q[k - 19:k + 1]
            m = sum(xs) / 20
            self.q_vol20[k] = math.sqrt(sum((x - m) ** 2 for x in xs) / 19 * 252)
        self.sox_hi60 = [None] * n
        for k in range(60, n):
            w = [x for x in self.SOX[k - 59:k + 1] if x]
            self.sox_hi60[k] = max(w) if w else None

    def lev_ret(self, k, und, L):
        """倍率Lの1日の騰落。実物があればそれ、なければ指数から作る"""
        sym = {("q", 2): "QLD", ("q", 3): "TQQQ", ("s", 3): "SOXL"}.get((und, L))
        D = self.days
        if sym and k > 0:
            c = self.real[sym][0]
            if D[k - 1] in c and D[k] in c:
                return c[D[k]] / c[D[k - 1]] - 1
        r = self.r_q[k] if und == "q" else self.r_sox[k]
        return L * r - (L - 1) * (self.rf[k] + SPREAD / 252) - LEV_FEE.get(L, 0.0095) / 252


def sma(x, n):
    out, s = [None] * len(x), 0.0
    for k in range(len(x)):
        s += x[k] or 0
        if k >= n:
            s -= x[k - n] or 0
        if k >= n - 1:
            out[k] = s / n
    return out


def rsi(x, n=2):
    out = [None] * len(x)
    ag = al = None
    for k in range(1, len(x)):
        ch = x[k] - x[k - 1]
        g, l_ = max(ch, 0), max(-ch, 0)
        if k == n:
            ag = sum(max(x[j] - x[j - 1], 0) for j in range(1, n + 1)) / n
            al = sum(max(x[j - 1] - x[j], 0) for j in range(1, n + 1)) / n
        elif k > n:
            ag = (ag * (n - 1) + g) / n
            al = (al * (n - 1) + l_) / n
        if ag is not None:
            out[k] = 100.0 if al == 0 else 100 - 100 / (1 + ag / al)
    return out


# ---------------- 税の帳簿（足ごと） ----------------

class Book:
    """1つの足の資金。pos: {名前: [価値, 取得額]}、cash。年末に確定した損益の20.315%を払う"""

    def __init__(self, v=1.0, tax=True):
        self.cash, self.pos, self.real, self.tax = v, {}, 0.0, tax

    def value(self):
        return self.cash + sum(p[0] for p in self.pos.values())

    def grow(self, name, r):
        if name in self.pos:
            self.pos[name][0] *= 1 + r

    def interest(self, r):
        it = self.cash * r
        self.cash += it
        self.real += it

    def buy(self, name, amt):
        amt = min(amt, self.cash)
        if amt <= 0:
            return
        self.cash -= amt
        net = amt * (1 - FEE)
        p = self.pos.setdefault(name, [0.0, 0.0])
        p[0] += net
        p[1] += amt

    def sell(self, name, frac=1.0):
        if name not in self.pos:
            return
        v, c = self.pos[name]
        sv, sc = v * frac, c * frac
        self.cash += sv * (1 - FEE)
        self.real += sv * (1 - FEE) - sc
        if frac >= 1.0 - 1e-12:
            del self.pos[name]
        else:
            self.pos[name] = [v - sv, c - sc]

    def year_end(self):
        if self.tax and self.real > 0:
            self.cash -= TAX * self.real
        self.real = 0.0


def year_ends(days):
    return {k for k in range(len(days)) if k + 1 == len(days) or days[k + 1][:4] != days[k][:4]}


# ---------------- 策1・策5: トレンドに乗る核 ----------------

def core(M, start, end, L=2, vol_cap=0.30, off="cash", tax=True, confirm=2):
    """QQQ（NDX）の終値が200日線を confirm 日続けて上回ったら倍率Lの指数ETF、下回ったら off（cash＝短期国債、dm＝策5）。
    上にある間でも20日の値動きが年率 vol_cap を超えたら1倍（QQQ）。判断は引け、売買は翌日の引け。"""
    D = M.days
    k0, k1 = M.idx[start], M.idx[end]
    B = Book(1.0, tax)
    ye = year_ends(D)
    state = None      # "L"・"1"・"off"
    hold = None       # 持っているものの名前
    above = below = 0
    target = None
    out = []
    dm_pick = None
    for k in range(k0, k1 + 1):
        if k > k0:
            # その日の値動き
            for nm in list(B.pos):
                if nm == "LEV":
                    B.grow(nm, M.lev_ret(k, "q", L))
                elif nm == "QQQ":
                    B.grow(nm, M.r_q[k])
                else:
                    B.grow(nm, dm_ret(M, nm, k))
            B.interest(M.cash_r[k])
            # 前の日に決めた形に、この日の引けで入れ替える
            if target is not None and target != state_key(state, dm_pick):
                for nm in list(B.pos):
                    B.sell(nm)
                tk, tdm = target
                if tk == "L":
                    B.buy("LEV", B.cash)
                elif tk == "1":
                    B.buy("QQQ", B.cash)
                elif tk == "off" and tdm and tdm != "CASH":
                    B.buy(tdm, B.cash)
                state, dm_pick = tk, tdm
        # この日の引けで、明日の形を決める
        ma = M.q_sma200[k]
        if ma:
            if M.NDX[k] > ma:
                above, below = above + 1, 0
            else:
                above, below = 0, below + 1
        cur = state or "off"
        if cur == "off" and above >= confirm:
            cur = "L"
        elif cur in ("L", "1") and below >= confirm:
            cur = "off"
        if cur in ("L", "1"):
            v = M.q_vol20[k]
            cur = "1" if (vol_cap and v and v > vol_cap) else "L"
        pick = dm_pick
        if cur == "off":
            if off == "dm":
                if is_month_end(D, k) or state != "off" or dm_pick is None:
                    pick = dm_choose(M, k)
            else:
                pick = "CASH"
        else:
            pick = None
        target = (cur, pick)
        if k in ye:
            B.year_end()
        out.append(B.value())
    return out


def state_key(state, pick):
    return (state, pick if state == "off" else None)


def is_month_end(D, k):
    return k + 1 == len(D) or D[k + 1][5:7] != D[k][5:7]


DM_ASSETS = ("GLD", "XLE", "TLT")


def dm_ret(M, nm, k):
    src = {"GLD": M.gld, "XLE": M.xle, "TLT": M.tlt}[nm]
    a, b = M.days[k - 1], M.days[k]
    if a in src and b in src:
        return src[b] / src[a] - 1
    return 0.0


def dm_choose(M, k):
    """直近6か月（126取引日）の騰落率が一番高いもの。短期国債（現金）に負けるなら現金"""
    if k < 126:
        return "CASH"
    D = M.days
    best, bv = "CASH", math.prod(1 + x for x in M.cash_r[k - 125:k + 1]) - 1
    for nm in DM_ASSETS:
        src = {"GLD": M.gld, "XLE": M.xle, "TLT": M.tlt}[nm]
        a, b = D[k - 126], D[k]
        if a in src and b in src:
            r = src[b] / src[a] - 1
            if r > bv:
                best, bv = nm, r
    return best


# ---------------- 策2・策3: 待機の資金で指数の逆張り ----------------

def bs_put(S, K, T, r, s):
    if T <= 0 or s <= 0:
        return max(K - S, 0.0)
    d1 = (math.log(S / K) + (r + s * s / 2) * T) / (s * math.sqrt(T))
    d2 = d1 - s * math.sqrt(T)
    N = lambda x: 0.5 * (1 + math.erf(x / math.sqrt(2)))  # noqa: E731
    return K * math.exp(-r * T) * N(-d2) - S * N(-d1)


def waiting(M, start, end, sigcount=None, use_a=True, use_b=True, mode="etf", iv_mult=1.0, tax=True, cal=None):
    """待機の資金（ふだんは短期国債）。
    (a) QQQが200日線の上で RSI(2)≦5 → 資金の半分でTQQQ（3倍）
    (b) SOXが60日の高値から−15%以下で、その日の押し目・急落の底の合図が10件以上 → 資金の半分でSOXL（3倍）
    手じまい: 指数の終値が5日線を上回った翌日、または10取引日。損切りなし。売買は翌日（始値の代わりに翌日の引け）。
    mode: "etf"（策2）、"put"（策3: 3倍ETFのプットを売る。期限15取引日・行使価格は終値の5%下・値段は理論値）、
          "both"（策2＋策3: ETFで半分、残りの現金を担保にプット）
    cal: 策8（日付で決まる短い持ち方）を同じ資金で行う {日付のk: True（その日の引けにTQQQを持つ）}"""
    D = M.days
    k0, k1 = M.idx[start], M.idx[end]
    B = Book(1.0, tax)
    ye = year_ends(D)
    live = {}     # 'a'/'b' -> {"k": 入った日, "nm": ETFの名前}
    puts = []     # [{"und", "K", "n"（株数）, "exp"（k）, "prem"}]
    pend = []     # 翌日の引けでする売買 [(種類, 名前, 引数)]
    cal_on = False
    out = []
    trades = {"a": 0, "b": 0, "put": 0}
    for k in range(k0, k1 + 1):
        if k > k0:
            for nm in list(B.pos):
                und = "q" if nm in ("TQQQ_a", "CAL") else "s"
                B.grow(nm, M.lev_ret(k, und, 3))
            B.interest(M.cash_r[k])
            for kind, nm, arg in pend:
                if kind == "buy":
                    B.buy(nm, arg * B.value())
                else:
                    B.sell(nm)
            pend = []
            # 期限が来たプットの決済（理論値の差額を現金で）
            keep = []
            for p in puts:
                if k >= p["exp"]:
                    S = p["S0"] * p["acc"]
                    pay = max(p["K"] - S, 0.0) * p["n"]
                    B.cash -= pay
                    B.real -= pay
                else:
                    keep.append(p)
            puts = keep
            for p in puts:   # 3倍ETFの値段を追う
                p["acc"] *= 1 + M.lev_ret(k, p["und"], 3)
        # 手じまいの判定
        for key in list(live):
            x = live[key]
            und_c, und_ma = (M.NDX[k], M.q_sma5[k]) if key == "a" else (M.SOX[k], M.sox_sma5[k])
            if (und_ma and und_c > und_ma) or k - x["k"] >= 10:
                if x.get("nm"):
                    pend.append(("sell", x["nm"], None))
                del live[key]
        # 引き金
        trig = []
        if use_a and "a" not in live and M.q_sma200[k] and M.NDX[k] > M.q_sma200[k] and M.q_rsi2[k] is not None and M.q_rsi2[k] <= 5:
            trig.append(("a", "q"))
        if use_b and "b" not in live and sigcount is not None and M.sox_hi60[k] and M.SOX[k] <= 0.85 * M.sox_hi60[k] \
                and sigcount.get(D[k], 0) >= 10:
            trig.append(("b", "s"))
        for key, und in trig:
            trades[key] += 1
            x = {"k": k}
            if mode in ("etf", "both"):
                x["nm"] = "TQQQ_a" if key == "a" else "SOXL_b"
                pend.append(("buy", x["nm"], 0.5))
            if mode in ("put", "both"):
                # 担保: 資金の半分（both のときは、ETFに使わない残りの半分のうちの半分）
                coll = B.value() * (0.5 if mode == "put" else 0.25)
                S0 = 100.0
                if und == "q":
                    iv = 3 * (M.VXN[k] or 25) / 100 * iv_mult
                else:
                    xs = M.r_sox[k - 19:k + 1]
                    m = sum(xs) / 20
                    iv = 3 * math.sqrt(sum((y - m) ** 2 for y in xs) / 19 * 252) * 1.15 * iv_mult
                Kp = 0.95 * S0
                prem = bs_put(S0, Kp, 15 / 252, M.rf[k] * 252, iv)
                n = coll / Kp
                B.cash += prem * n * (1 - 0.001)
                B.real += prem * n * (1 - 0.001)
                puts.append({"und": und, "K": Kp, "n": n, "exp": k + 15, "S0": S0, "acc": 1.0, "prem": prem})
                trades["put"] += 1
            live[key] = x
        # 策8
        if cal is not None:
            want = cal.get(k, False)
            if want and not cal_on:
                pend.append(("buy", "CAL", 0.999))
                cal_on = True
            elif not want and cal_on:
                pend.append(("sell", "CAL", None))
                cal_on = False
        if k in ye:
            B.year_end()
        out.append(B.value())
    return out, trades


def calendar_days(M, start, end, month_end=True, fomc=True):
    """策8: その日の引けにTQQQを持っているかどうか（判断は前の日の引け→翌日の引けで売買するので1日前にずらして返す）
    (a) 毎月、最後の取引日の3日前の引けで買い、翌月の3取引日目の引けで売る
    (b) FOMCの結果発表の前の日の引けで買い、発表の日の引けで売る"""
    D = M.days
    hold = set()
    if month_end:
        for k in range(len(D)):
            if is_month_end(D, k):
                # 買い: k-3 の引け、売り: 翌月の3取引日目（k+3）の引け → 持つのは k-2〜k+3 の値動き
                for j in range(k - 3, min(k + 3, len(D) - 1)):
                    hold.add(j)
    if fomc:
        fo = json.load(open(os.path.join(CACHE, "long/index/fomc_dates.json")))
        for d in fo:
            if d in M.idx:
                k = M.idx[d]
                hold.add(k - 1)
    # waiting() は「この日の引けで決め、翌日の引けで売買」するので、持ちたい日の前の日に True にする
    return {j - 1: True for j in hold}


# ---------------- 策4: 円建ての指数（証拠金取引）で核を持つ ----------------

def core_cfd(M, start, end, L=2, vol_cap=0.30, confirm=2, spread=0.002, fee=0.0005):
    """策1と同じ合図で、円建てのNASDAQ100の証拠金取引（くりっく株365を想定）を資金のL倍持つ。値は円で見た資金。
    1日の損益 = L×（QQQの配当込みの騰落 − ドルの短期金利 − spread/年）。ドルの短期金利の分は、円建てにする費用（金利に当たる費用）の近似。
    円の金利は0%とした（少し厳しめ）。降りている間は円の現金（0%）。
    税: 証拠金取引は株と別の区分。年1回の強制決済（リセット）があると仮定し、毎年の損益（含み益を含む）が利益なら20.315%"""
    D = M.days
    k0, k1 = M.idx[start], M.idx[end]
    ye = year_ends(D)
    V, y0 = 1.0, 1.0
    state, target = "off", None
    above = below = 0
    out = []
    for k in range(k0, k1 + 1):
        if k > k0:
            if state == "L":
                V *= 1 + L * (M.r_q[k] - M.rf[k] - spread / 252)
            elif state == "1":
                V *= 1 + (M.r_q[k] - M.rf[k] - spread / 252)
            if target is not None and target != state:
                V *= 1 - fee * (L if state != "off" else 0) - fee * (L if target != "off" else 0)
                state = target
        ma = M.q_sma200[k]
        if ma:
            if M.NDX[k] > ma:
                above, below = above + 1, 0
            else:
                above, below = 0, below + 1
        cur = state
        if cur == "off" and above >= confirm:
            cur = "L"
        elif cur in ("L", "1") and below >= confirm:
            cur = "off"
        if cur in ("L", "1"):
            v = M.q_vol20[k]
            cur = "1" if (vol_cap and v and v > vol_cap) else "L"
        target = cur
        if k in ye:
            if V > y0:
                V -= TAX * (V - y0)
            y0 = V
        out.append(V)
    return out


# ---------------- 策7: 入金の決まり ----------------

def deposits(ncur, days, park, trig, tax_park=True):
    """毎月の最初の取引日に1を足す（2015年2月〜）。park=None ならすぐ新分析ツールへ。
    park があればそこに置き、新分析ツールの資金（この乱数の通しの資金）が今までの最高値から trig 以上下げた日に、置いた分を全部新分析ツールへ移す。
    QQQから移すときは値上がり分に20.315%（核・短期国債の資金は足の中で税を払っているので、移すときの税は数えない）"""
    units, pu, pcost = 0.0, 0.0, 0.0
    flows = []
    peak = 0.0
    for k, d in enumerate(days):
        peak = max(peak, ncur[k])
        if k > 0 and d[:7] != days[k - 1][:7] and d >= "2015-02-01":
            flows.append((d, 1.0))
            if park is None:
                units += 1.0 / ncur[k]
            else:
                pu += 1.0 / park[k]
                pcost += 1.0
        if park is not None and pu > 0 and ncur[k] <= (1 - trig) * peak:
            val = pu * park[k]
            if tax_park and park is not None and val > pcost and park_is_qqq(park):
                val -= TAX * (val - pcost)
            units += val / ncur[k]
            pu, pcost = 0.0, 0.0
    fv = units * ncur[-1] + (pu * park[-1] if park is not None else 0.0)
    # 内部の利回り（年率）
    end = dt.date.fromisoformat(days[-1])

    def fvr(r):
        return sum(a * (1 + r) ** ((end - dt.date.fromisoformat(d)).days / 365.25) for d, a in flows)
    lo, hi = -0.9, 3.0
    for _ in range(80):
        mid = (lo + hi) / 2
        if fvr(mid) > fv:
            hi = mid
        else:
            lo = mid
    return fv, (lo + hi) / 2


_QQQ_ID = []


def park_is_qqq(park):
    return any(park is x for x in _QQQ_ID)


def onkabu_buys():
    p = os.path.join(CACHE, "results/fable_onkabu.json")
    d = json.load(open(p))
    return [(x["buy"], x["sym"]) for x in d.get("log_tax_all", [])]


# ---------------- 組み合わせ ----------------

def combine(curves, weights, days, rebalance=True):
    """足ごとの毎日の価値（同じ長さ）を割合で合わせる。rebalance=True なら毎年1月の最初の取引日に割合を戻す（税は数えない）"""
    n = len(days)
    tot = []
    hold = [w for w in weights]
    for k in range(n):
        if k > 0:
            for i, c in enumerate(curves):
                hold[i] *= c[k] / c[k - 1] if c[k - 1] else 1.0
            if rebalance and days[k][:4] != days[k - 1][:4]:
                s = sum(hold)
                hold = [s * w for w in weights]
        tot.append(sum(hold))
    return tot


def metrics(curve, days):
    yrs = (dt.date.fromisoformat(days[-1]) - dt.date.fromisoformat(days[0])).days / 365.25
    peak = mdd = 0.0
    for v in curve:
        peak = max(peak, v)
        mdd = max(mdd, 1 - v / peak)
    return (curve[-1] / curve[0]) ** (1 / yrs) - 1, mdd


def cagr_between(curve, days, lo, hi):
    ks = [k for k, d in enumerate(days) if lo <= d <= hi]
    if len(ks) < 2:
        return None
    return metrics([curve[k] for k in ks], [days[k] for k in ks])[0]


def yearly(curve, days):
    ye, prev, out = {}, curve[0], {}
    for d, v in zip(days, curve):
        ye[d[:4]] = v
    for y in sorted(ye):
        out[y] = ye[y] / prev - 1
        prev = ye[y]
    return out


def rolling(curve, base, step=10, win=250):
    """1年の区切り（250取引日、step日ごと）: 1年の損益の差の平均と、上回った割合"""
    diffs = []
    for s in range(0, len(curve) - win, step):
        a = curve[s + win] / curve[s] - 1
        b = base[s + win] / base[s] - 1
        diffs.append(a - b)
    good = sum(1 for x in diffs if x > 1e-9) / max(1, sum(1 for x in diffs if abs(x) > 1e-9))
    return sum(diffs) / len(diffs), good


# ---------------- 本体 ----------------

def load_new(watch, form_idx):
    d = json.load(open(os.path.join(CACHE, f"results/tax_{watch}.json")))
    keys = list(d.keys())
    v = d[keys[form_idx]]
    return keys[form_idx], v["days"], v["eq"]


def signal_counts(M):
    """押し目（B）・急落の底（C）の合図の数（合図の日＝買う日の前の取引日）。
    新分析ツールの売買の一覧（`backtest_onkabu_combined.py newtrades`、後知恵なしの監視銘柄・枠に関係なく全部の候補）から数える"""
    p = os.path.join(CACHE, "newtool_trades_fixed_c0.00132.pkl")
    if not os.path.exists(p):
        return None
    nt = pickle.load(open(p, "rb"))
    out = {}
    for t in nt["trades"]:
        if t.get("rule") in ("B", "C") and t["in"] in M.idx:
            d = M.days[M.idx[t["in"]] - 1]
            out[d] = out.get(d, 0) + 1
    return out


def st_median_curve(cs):
    return [st.median(c[k] for c in cs) for k in range(len(cs[0]))]


def align(curve_days, curve, days):
    m = dict(zip(curve_days, curve))
    out, last = [], None
    for d in days:
        last = m.get(d, last)
        out.append(last)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    a = ap.parse_args()
    M = Mkt()
    out = []
    w = out.append
    sc = signal_counts(M)
    print("合図の数がある日", len(sc) if sc else 0, "10件以上の日", sum(1 for v in (sc or {}).values() if v >= 10), file=sys.stderr)
    # ---- 今の新分析ツール（税込み）
    nk, ndays, n87 = load_new("87", 2)     # 待っている現金はQQQ（今の実際の形）
    _, _, nfree = load_new("free", 2)
    _, _, n87c = load_new("87", 1)         # 待っている現金は現金のまま
    _, _, nfreec = load_new("free", 1)
    days = [d for d in ndays if d in M.idx]
    start, end = days[0], days[-1]
    onk = json.load(open(os.path.join(CACHE, "results/fable_onkabu.json")))
    O = {k: align(onk["days"], onk[k], days) for k in ("tax_all", "nisa_all", "tax_noNVDA", "nisa_noNVDA")}
    N87 = [align(ndays, c, days) for c in n87]
    NFR = [align(ndays, c, days) for c in nfree]
    N87c = [align(ndays, c, days) for c in n87c]
    NFRc = [align(ndays, c, days) for c in nfreec]
    k0 = M.idx[start]
    QQQ = [M.QQQc[M.idx[d]] for d in days]
    _QQQ_ID.append(QQQ)
    # 足
    C1 = core(M, start, end)                  # 策1
    C1dm = core(M, start, end, off="dm")      # 策1＋策5
    C1nv = core(M, start, end, vol_cap=None)  # 値動きで1倍に落とさない
    W2, t2 = waiting(M, start, end, sc)
    W2a, _ = waiting(M, start, end, sc, use_b=False)
    W3, t3 = waiting(M, start, end, sc, mode="put")
    W3lo, _ = waiting(M, start, end, sc, mode="put", iv_mult=0.8)
    W23, _ = waiting(M, start, end, sc, mode="both")
    cal = calendar_days(M, start, end)
    W8, _ = waiting(M, start, end, sc, use_a=False, use_b=False, cal=cal)
    W8m, _ = waiting(M, start, end, sc, use_a=False, use_b=False, cal=calendar_days(M, start, end, fomc=False))
    W8f, _ = waiting(M, start, end, sc, use_a=False, use_b=False, cal=calendar_days(M, start, end, month_end=False))
    W238, _ = waiting(M, start, end, sc, mode="both", cal=cal)
    CASH = waiting(M, start, end, sc, use_a=False, use_b=False)[0]
    sleeves = {"策1 核（QLD・200日線、下は短期国債）": C1, "策1＋策5 核（下は強い資産へ）": C1dm, "策1 値動きで1倍に落とさない形": C1nv,
               "策2 待機の資金（3倍ETFの逆張り）": W2, "策2のうち(a)だけ（QQQのRSI(2)）": W2a,
               "策3 待機の資金（プットを売る、理論値）": W3, "策3（プットの値段を2割安く見た場合）": W3lo, "策2＋策3": W23,
               "策8 日付で決まる持ち方（月末＋FOMC）": W8, "策8 月末だけ": W8m, "策8 FOMCだけ": W8f,
               "策2＋策3＋策8（Fableの待機の資金）": W238, "（比べる）短期国債だけ": CASH, "（比べる）QQQを持ち続ける": QQQ,
               "恩株ツール（課税口座）": O["tax_all"], "恩株ツール（NISA・2倍で50%売る）": O["nisa_all"],
               "恩株ツール NVDAを除く（課税口座）": O["tax_noNVDA"], "恩株ツール NVDAを除く（NISA）": O["nisa_noNVDA"]}
    w("## 足ごとの成績（2015-01-02〜" + end + "、税込み）\n")
    w("| 足 | 年率 | 最大下落率 | 2015〜2021年 | 2022年〜 |")
    w("|---|---|---|---|---|")
    for nm, c in sleeves.items():
        cg, md = metrics(c, days)
        w(f"| {nm} | {cg:.1%} | {md:.0%} | {cagr_between(c, days, '2015-01-01', '2021-12-31'):.1%} | {cagr_between(c, days, '2022-01-01', '9999'):.1%} |")
    w("\n### 足の年ごと（税込み）\n")
    ys = sorted({d[:4] for d in days})
    w("| 足 | " + " | ".join(ys) + " |")
    w("|---|" + "---|" * len(ys))
    for nm in ("策1 核（QLD・200日線、下は短期国債）", "策1＋策5 核（下は強い資産へ）", "（比べる）QQQを持ち続ける", "策2 待機の資金（3倍ETFの逆張り）",
               "策3 待機の資金（プットを売る、理論値）", "策8 日付で決まる持ち方（月末＋FOMC）"):
        yy = yearly(sleeves[nm], days)
        w(f"| {nm} | " + " | ".join(f"{yy[y]:.0%}" for y in ys) + " |")
    nyy = yearly(st_median_curve(N87c), days)
    w("| （参考）新分析ツール 87銘柄（乱数の中央値の資金） | " + " | ".join(f"{nyy[y]:.0%}" for y in ys) + " |")
    w(f"\n- 待機の資金の売買の回数: (a) {t2['a']}回・(b) {t2['b']}回、プット {t3['put']}回")
    # ---- 組み合わせ
    w("\n## 組み合わせ（新分析ツールは乱数30通りの中央値）\n")
    combos = [
        ("今の実際の形（新分析12,000ドル・恩株4,500ドル、別々の口座）", [("N", 12 / 16.5), ("O", 4.5 / 16.5)], False),
        ("今の形を毎年戻す（比べる土台）", [("N", 12 / 16.5), ("O", 4.5 / 16.5)], True),
        ("策6だけ: 恩株ツールをNISAに", [("N", 12 / 16.5), ("ON", 4.5 / 16.5)], False),
        ("策1（Fableの割合）: 核50%・新分析35%・恩株15%、毎年戻す", [("C1", 0.5), ("N", 0.35), ("O", 0.15)], True),
        ("策1＋策5: 核50%・新分析35%・恩株15%、毎年戻す", [("C1dm", 0.5), ("N", 0.35), ("O", 0.15)], True),
        ("策1を今の形に足す: 核1/3・新分析・恩株は今の比率で2/3、毎年戻す", [("C1", 1 / 3), ("N", 2 / 3 * 12 / 16.5), ("O", 2 / 3 * 4.5 / 16.5)], True),
        ("（比べる）QQQを今の形に足す: QQQ 1/3・残りは今の比率、毎年戻す", [("Q", 1 / 3), ("N", 2 / 3 * 12 / 16.5), ("O", 2 / 3 * 4.5 / 16.5)], True),
        ("策2を足す: 待機の資金15%・新分析・恩株は今の比率で85%、毎年戻す", [("W2", 0.15), ("N", 0.85 * 12 / 16.5), ("O", 0.85 * 4.5 / 16.5)], True),
        ("（比べる）短期国債15%・残りは今の比率、毎年戻す", [("CASH", 0.15), ("N", 0.85 * 12 / 16.5), ("O", 0.85 * 4.5 / 16.5)], True),
        ("策9を足す: 日本株の足10%・残りは今の比率、毎年戻す", [("J9", 0.10), ("N", 0.9 * 12 / 16.5), ("O", 0.9 * 4.5 / 16.5)], True),
        ("Fableの全部の組み合わせ: 核（策1＋5）40%・新分析30%・待機（策2＋3＋8）15%・恩株NISA 15%、毎年戻す",
         [("C1dm", 0.4), ("N", 0.3), ("W238", 0.15), ("ON", 0.15)], True),
    ]
    jp = json.load(open(os.path.join(CACHE, "results/fable_jp.json")))
    jpm = dict(zip(jp["days"], jp["curve"]))
    J9, last = [], None
    for d in days:
        last = jpm.get(d, last) if jpm.get(d) is not None else last
        J9.append((last if last is not None else jp["curve"][0]) / M.JPY[M.idx[d]])   # 円の資金をドルに直す
    src = {"J9": J9, "C1": C1, "C1dm": C1dm, "W2": W2, "W238": W238, "CASH": CASH, "Q": QQQ, "O": O["tax_all"], "ON": O["nisa_all"]}
    ref = {}
    for watch, NN in (("87銘柄", N87), ("全業種", NFR)):
        w(f"\n### 監視銘柄: {watch}\n")
        w("| 形 | 年率 | 最大下落率 | 2015〜2021年 | 2022年〜 | 1年の区切り: 今の形（割合を戻すかどうかをそろえる）との差の平均 | 上回った割合 | 円で見た年率 | 円で見た最大下落率 |")
        w("|---|---|---|---|---|---|---|---|---|")
        for label, parts, reb in combos:
            res = []
            for s, ncur in enumerate(NN):
                cs = [ncur if p == "N" else src[p] for p, _ in parts]
                c = combine(cs, [x for _, x in parts], days, reb)
                cur = combine([ncur, O["tax_all"]], [12 / 16.5, 4.5 / 16.5], days, reb)   # 比べる土台は、割合を戻すかどうかをそろえる
                cg, md = metrics(c, days)
                rd, rg = rolling(c, cur)
                cy = [v * M.JPY[M.idx[d]] for v, d in zip(c, days)]
                cgy, mdy = metrics(cy, days)
                res.append((cg, md, cagr_between(c, days, "2015-01-01", "2021-12-31"), cagr_between(c, days, "2022-01-01", "9999"), rd, rg, cgy, mdy))
                if s == 0:
                    ref.setdefault(watch, {})[label] = yearly(c, days)
            med = [st.median(r[i] for r in res) for i in range(8)]
            w(f"| {label} | {med[0]:.1%} | {med[1]:.0%} | {med[2]:.1%} | {med[3]:.1%} | {med[4]:+.1%} | {med[5]:.0%} | {med[6]:.1%} | {med[7]:.0%} |")
    # 年ごと
    for watch in ref:
        w(f"\n### 年ごと（{watch}、乱数1通り）\n")
        labs = list(ref[watch])
        ys = sorted(ref[watch][labs[0]])
        w("| 形 | " + " | ".join(ys) + " |")
        w("|---|" + "---|" * len(ys))
        for lb in labs:
            w(f"| {lb[:40]} | " + " | ".join(f"{ref[watch][lb][y]:.0%}" for y in ys) + " |")
    # ---- 策4: 核を円建ての指数の証拠金取引（くりっく株365）で持つ
    w("\n## 策4: 核を円建ての指数（証拠金取引）で持つ（円で見た成績）\n")
    C4 = core_cfd(M, start, end)
    C1y = [v * M.JPY[M.idx[d]] for v, d in zip(C1, days)]
    QQy = [v * M.JPY[M.idx[d]] for v, d in zip(QQQ, days)]
    w("| 足（円で見る） | 年率 | 最大下落率 | 2015〜2021年 | 2022年〜 |")
    w("|---|---|---|---|---|")
    for nm, c in (("策1 核をQLD（ドル）で持つ", C1y), ("策4 核を円建ての指数で持つ", C4), ("（比べる）QQQ（ドル）を持ち続ける", QQy)):
        cg, md = metrics(c, days)
        w(f"| {nm} | {cg:.1%} | {md:.0%} | {cagr_between(c, days, '2015-01-01', '2021-12-31'):.1%} | {cagr_between(c, days, '2022-01-01', '9999'):.1%} |")
    w("\n円高を伴う下げ（ドル円が60取引日で−7%以上の日を含む期間）の、核の下げ幅（円で見る）:\n")
    w("| 期間 | ドル円 | QLDの核（円） | 円建ての核 |")
    w("|---|---|---|---|")
    for lo, hi in (("2016-01-01", "2016-08-31"), ("2020-02-15", "2020-04-30"), ("2022-10-15", "2023-01-31"), ("2024-07-01", "2024-09-30"), ("2025-01-01", "2025-05-31")):
        ks = [k for k, d in enumerate(days) if lo <= d <= hi]
        if not ks:
            continue
        def dd(c):
            pk = c[ks[0]]
            m = 0.0
            for k in ks:
                pk = max(pk, c[k])
                m = max(m, 1 - c[k] / pk)
            return m
        fx = M.JPY[M.idx[days[ks[-1]]]] / M.JPY[M.idx[days[ks[0]]]] - 1
        w(f"| {lo}〜{hi} | {fx:+.0%} | −{dd(C1y):.0%} | −{dd(C4):.0%} |")
    # ---- 策7: 入金の決まり
    w("\n## 策7: 入金の決まり（毎月500ドルを足す。2015年2月〜）\n")
    w("| 形 | 87銘柄: 最後の資産（毎月すぐ入れる＝100） | 内部の利回り | 全業種: 最後の資産 | 内部の利回り |")
    w("|---|---|---|---|---|")
    rows7 = {}
    for watch, NN in (("87", N87c), ("free", NFRc)):
        for s, ncur in enumerate(NN):
            for lab, park, trig in (("毎月すぐ新分析ツールに入れる（今の考え方）", None, None),
                                    ("QQQに置き、新分析ツールが高値から−25%以下の日に全部移す", QQQ, 0.25),
                                    ("核（策1）に置き、−25%以下の日に全部移す", C1, 0.25),
                                    ("QQQに置き、−15%以下の日に全部移す", QQQ, 0.15),
                                    ("短期国債に置き、−25%以下の日に全部移す", CASH, 0.25)):
                fv, irr = deposits(ncur, days, park, trig)
                rows7.setdefault(lab, {}).setdefault(watch, []).append((fv, irr))
    base = {wch: [x[0] for x in rows7["毎月すぐ新分析ツールに入れる（今の考え方）"][wch]] for wch in ("87", "free")}
    for lab, d in rows7.items():
        cells = []
        for wch in ("87", "free"):
            rel = st.median(x[0] / b * 100 for x, b in zip(d[wch], base[wch]))
            irr = st.median(x[1] for x in d[wch])
            cells += [f"{rel:.0f}", f"{irr:.1%}"]
        w(f"| {lab} | " + " | ".join(cells) + " |")
    # ---- 策6: NISAの枠
    w("\n## 策6: 恩株ツールをNISAで買うときの1回の金額（課税口座の資金の推移から。1ドル＝その日のドル円）\n")
    lg = onkabu_buys()
    w("| 買った日 | 銘柄 | 1回の金額（ドル） | 円 | 年240万円の枠に |")
    w("|---|---|---|---|---|")
    oc = dict(zip(onk["days"], onk["tax_all"]))
    for d, sym in lg:
        v = oc.get(d)
        if v is None:
            continue
        yen = v * M.JPY[M.idx[d]] if d in M.idx else float("nan")
        w(f"| {d} | {sym} | {v:,.0f} | {yen / 1e4:,.0f}万円 | {'収まる' if yen <= 2.4e6 else '超える'} |")
    # ---- 長い期間（2014年以前を含む）
    w("\n## 長い期間での足の成績（作った値段を含む。下落率を見るため）\n")
    w("| 足 | 期間 | 年率 | 最大下落率 | QQQを持ち続ける 年率 | 最大下落率 |")
    w("|---|---|---|---|---|---|")
    for lo, hi in (("1990-01-02", "2026-11-06"), ("2000-01-03", "2014-12-31"), ("2005-01-03", "2014-12-31")):
        lo_, hi_ = next(d for d in M.days if d >= lo), max(d for d in M.days if d <= hi)
        dd_ = [d for d in M.days if lo_ <= d <= hi_]
        qq = [M.QQQc[M.idx[d]] or M.NDX[M.idx[d]] for d in dd_]
        # QQQがない日はNDXで作った値
        qv, qq = [1.0], None
        for k in range(M.idx[lo_] + 1, M.idx[hi_] + 1):
            qv.append(qv[-1] * (1 + M.r_q[k]))
        qg, qm = metrics(qv, dd_)
        for nm, c in (("策1 核", core(M, lo_, hi_)), ("策1＋策5", core(M, lo_, hi_, off="dm") if lo_ >= "2005" else None),
                      ("策2(a) QQQのRSI(2)を3倍で", waiting(M, lo_, hi_, None, use_b=False)[0]),
                      ("策8 月末＋FOMC" if lo_ >= "2008" else "策8 月末だけ",
                       waiting(M, lo_, hi_, None, use_a=False, use_b=False, cal=calendar_days(M, lo_, hi_, fomc=lo_ >= "2008"))[0])):
            if c is None:
                continue
            cg, md = metrics(c, dd_)
            w(f"| {nm} | {lo_[:4]}〜{hi_[:4]} | {cg:.1%} | {md:.0%} | {qg:.1%} | {qm:.0%} |")
    text = "\n".join(out) + "\n"
    if a.out:
        open(a.out, "w").write(text)
    print(text)


if __name__ == "__main__":
    main()
