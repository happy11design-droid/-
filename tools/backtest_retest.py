#!/usr/bin/env python3
"""売り・買いの合図を、今の測り方（売ったら枠を空ける・乱数を3通り）で全部やり直すバックテスト

使い方:
  tools/backtest_retest.py run --stage {sell,combo,half,filter,rule,all} [--out FILE]

今の採用ルール（4つのルール、4銘柄・1銘柄25%、損切り15%、急落の底RSI(2)≦10、同じ業種2銘柄まで、押し目は前日の上部バンドに指値で売る、
順張りは反転の合図で半分売り・かぶせ線で全部売る〔2026-10-01 採用〕、押し目・急落の底は出来高2倍の大陰線で全部売る〔2026-10-02 採用〕）を土台に:
  sell  : 売りの合図（これまでの約30種類＋まだ試していない酒田五法・ボリンジャー・その他の指標・週足）を1つずつ足す。
          合図の翌日の寄り付きで全部売り、空いた枠で次の合図を買う。対象は順張り（ミネルヴィニ・新高値V2）／逆張り（押し目・急落の底）
  combo : sell で良かった合図を2つ組み合わせる（どちらかが出たら売る）
  half  : 半分売り（反転のローソク足＋出来高＋RSI70）とかぶせ線の役割分担
  filter: 買いの合図に条件を重ねる（9/30〜10/1に試した日足・週足の28条件＋まだ試していない条件）。条件を満たさない合図は買わない
  rule  : まだ試していない買いのルールを、空き枠を埋める候補として足す（今の4つのルールの候補が優先）
判定: 乱数20通りで全部をふるいにかけ、設計期間（2015〜2021年）・確認期間（2022年〜）の両方で今のルールを上回った形を、
別の乱数50通り×2組で確かめる。3組とも両方の期間で上回った形だけを「確か」とする。片道0.1%。
"""
import argparse
import datetime as dt
import itertools
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_combo2 as cb
import backtest_entry_filter_search as ef
import backtest_exit_combo as xc
import backtest_exit_signals as xs
import backtest_minervini2 as bm2
import backtest_rebuy as rb
import backtest_signal_search as ss
import backtest_swing as bs
from backtest_lib import COSTS, DEFAULT_CACHE, gen_trades, pct, sma
from backtest_market_signal import ema

COST = COSTS[2]
SLOTS = 4
STOP = 0.15
SCREEN, CONF1, CONF2 = (1000, 20), (5000, 50), (7300, 50)
OUTDIR = "新分析ツール/バックテスト結果/"


# ---------- まだ試していない売りの合図 ----------
def _up(s, j):
    return xs.after_up(s, j)


def tweezer_top(s, j):         # 毛抜き天井
    h, o, c = s["h"], s["o"], s["c"]
    return _up(s, j - 1) and abs(h[j] - h[j - 1]) <= 0.002 * h[j] and c[j - 1] > o[j - 1] and c[j] < o[j]


def bear_harami(s, j):         # 陰のはらみ線
    o, c, a = s["o"], s["c"], s["atr14"][j - 1]
    return (a is not None and _up(s, j - 1) and c[j - 1] - o[j - 1] >= a and c[j] < o[j]
            and o[j] < c[j - 1] and c[j] > o[j - 1])


def doji_top(s, j):            # 天井の十字線（翌日の下げで確定）
    o, h, l, c = s["o"], s["h"], s["l"], s["c"]
    k = j - 1
    return _up(s, k) and h[k] > l[k] and abs(c[k] - o[k]) <= 0.1 * (h[k] - l[k]) and c[j] < min(o[k], c[k])


def bear_marubozu(s, j):       # 陰の大引け坊主（上昇の後の大きな陰線、ひげが短い）
    o, h, l, c, a = s["o"], s["h"], s["l"], s["c"], s["atr14"][j - 1]
    return (a is not None and _up(s, j - 1) and o[j] - c[j] >= 1.2 * a and h[j] > l[j]
            and (o[j] - c[j]) >= 0.85 * (h[j] - l[j]))


def advance_block(s, j):       # 行き詰まり線（三兵の先詰まり）
    o, c, h = s["o"], s["c"], s["h"]
    if not _up(s, j - 3) or not all(c[k] > o[k] for k in (j - 2, j - 1, j)):
        return False
    b = [c[k] - o[k] for k in (j - 2, j - 1, j)]
    up = [h[k] - c[k] for k in (j - 2, j - 1, j)]
    return c[j - 2] < c[j - 1] < c[j] and b[0] > b[1] > b[2] and up[2] > b[2]


def two_crows(s, j):           # 上放れ二羽烏
    o, c = s["o"], s["c"]
    return (_up(s, j - 2) and c[j - 2] > o[j - 2] and c[j - 1] < o[j - 1] and min(o[j - 1], c[j - 1]) > c[j - 2]
            and c[j] < o[j] and o[j] > o[j - 1] and c[j] < c[j - 1] and c[j] > c[j - 2])


def gap_down(s, j):            # 窓を開けて下げる（2%以上、出来高1.5倍）
    v50 = s["vol50"][j - 1]
    return s["h"][j] < s["l"][j - 1] * 0.98 and bool(v50) and s["v"][j] >= 1.5 * v50


def pb_exit08(s, j):           # ボリンジャー: 上のバンドの外（%b≧1）の後、10日以内に%bが0.8を下に抜ける
    pb = s["pctb"]
    if pb[j] is None or pb[j - 1] is None or not (pb[j] < 0.8 <= pb[j - 1]):
        return False
    return any(x is not None and x >= 1 for x in pb[max(0, j - 10):j])


def pb_div(s, j):              # ボリンジャー: %bの弱気ダイバージェンス（終値は20日の高値、%bは前の高値の時より低い・0.8未満）
    c, pb = s["c"], s["pctb"]
    if j < 25 or pb[j] is None or c[j] < max(c[j - 20:j + 1]):
        return False
    k = max(range(j - 20, j - 3), key=lambda x: c[x])
    return pb[k] is not None and pb[k] >= 1 and pb[j] < 0.8


def bw_peak(s, j):             # ボリンジャー: バンド幅が直前の最大から縮み始め、終値が20日線割れ（トレンドの終わり）
    up, dn, mid = s["bb_up"], s["bb_dn"], s["bb_mid"]
    if j < 25 or None in (up[j], dn[j], mid[j], up[j - 1], dn[j - 1]):
        return False
    bw = lambda k: (up[k] - dn[k]) / mid[k] if None not in (up[k], dn[k], mid[k]) else 0
    return bw(j) < bw(j - 1) and bw(j - 1) >= max(bw(k) for k in range(j - 20, j)) * 0.95 and s["c"][j] < mid[j]


def chandelier(s, j):          # シャンデリア・エグジット（直近22日の高値−ATR×3を引けで割る）
    a = s["atr14"][j]
    return a is not None and s["c"][j] < max(s["h"][j - 21:j + 1]) - 3 * a


def willr_down(s, j):          # ウィリアムズ%R が −20 を下に抜ける
    h, l, c = s["h"], s["l"], s["c"]
    def wr(k):
        hh, ll = max(h[k - 13:k + 1]), min(l[k - 13:k + 1])
        return -50 if hh == ll else -100 * (hh - c[k]) / (hh - ll)
    return j >= 15 and wr(j) < -20 <= wr(j - 1)


def cci_down(s, j):            # CCI(20) が +100 を下に抜ける
    return s["cci"][j] is not None and s["cci"][j - 1] is not None and s["cci"][j] < 100 <= s["cci"][j - 1]


def mfi_div(s, j):             # MFI(14)の弱気ダイバージェンス（終値は20日の高値、MFIは前の高値の時より10以上低い）
    c, m = s["c"], s["mfi14"]
    if j < 25 or m[j] is None or c[j] < max(c[j - 20:j + 1]):
        return False
    k = max(range(j - 20, j - 3), key=lambda x: c[x])
    return m[k] is not None and m[k] >= 70 and m[j] <= m[k] - 10


def obv_div(s, j):             # OBVの弱気ダイバージェンス（終値は20日の高値、OBVは20日の高値に届かない）
    c, ob = s["c"], s["obv"]
    return j >= 25 and c[j] >= max(c[j - 20:j + 1]) and ob[j] < max(ob[j - 20:j])


def chikou_down(s, j):         # 一目: 遅行スパンが価格を下に抜ける（終値が26日前を下回る）
    c = s["c"]
    return j >= 27 and c[j] < c[j - 26] and c[j - 1] >= c[j - 27]


def adx_turn(s, j):            # ADXが40以上から下向きに（トレンドの勢いの頂点）
    a = s["adx"]
    return a[j] is not None and a[j - 1] is not None and a[j - 1] >= 40 and a[j] < a[j - 1] and (a[j - 2] or 0) <= a[j - 1]


def ha_bear(s, j):             # 平均足が陽線から陰線に変わる
    return s["ha_bull"][j - 1] and not s["ha_bull"][j]


def below10(s, j):             # 10日線割れ
    m = s["ma10x"]
    return m[j] is not None and m[j - 1] is not None and s["c"][j] < m[j] and s["c"][j - 1] >= m[j - 1]


def lower_lows3(s, j):         # 3日続けて安値を切り下げる
    l = s["l"]
    return l[j] < l[j - 1] < l[j - 2] < l[j - 3]


def weekly(name):
    return lambda s, j: s["wsig"][name][j]


NEW_SELLS = [("毛抜き天井", tweezer_top), ("陰のはらみ線", bear_harami), ("天井の十字線（翌日の下げで確定）", doji_top),
             ("陰の大引け坊主", bear_marubozu), ("行き詰まり線（三兵の先詰まり）", advance_block), ("上放れ二羽烏", two_crows),
             ("窓を開けて下げる（2%・出来高1.5倍）", gap_down),
             ("ボリンジャー: 上のバンドの外の後、%bが0.8割れ", pb_exit08), ("ボリンジャー: %bの弱気ダイバージェンス（Mトップ）", pb_div),
             ("ボリンジャー: バンド幅の頂点から縮み20日線割れ", bw_peak),
             ("シャンデリア・エグジット（22日高値−ATR×3）", chandelier), ("ウィリアムズ%Rが−20割れ", willr_down), ("CCIが+100割れ", cci_down),
             ("MFIの弱気ダイバージェンス", mfi_div), ("OBVの弱気ダイバージェンス", obv_div), ("一目: 遅行スパンが価格を下に抜ける", chikou_down),
             ("ADXが40以上から下向き", adx_turn), ("平均足が陰線に変わる", ha_bear), ("10日線割れ", below10), ("3日続けて安値を切り下げる", lower_lows3)]
WEEKLY = [("週足: かぶせ線", xs.dark_cloud), ("週足: 弱気の包み足", xs.bear_engulf), ("週足: 流れ星", xs.shooting_star),
          ("週足: 宵の明星", xs.evening_star), ("週足: 三羽烏", xs.three_crows), ("週足: 終値が10週線割れ", None),
          ("週足: MACDのデッドクロス", "macd")]
OLD_SELLS = [x for x in ss.SELLS if x[0] != "かぶせ線"]


# ---------- まだ試していない買いの条件 ----------
NEW_FILTERS = [
    ("一目: 三役好転（転換線＞基準線・終値が雲の上・遅行スパンが上）",
     lambda s, i: s["ten"][i] is not None and s["kij"][i] is not None and s["ten"][i] > s["kij"][i]
     and s["cloud_hi"][i] is not None and s["c"][i] > s["cloud_hi"][i] and s["c"][i] > s["c"][i - 26]),
    ("OBVが20日前より上", lambda s, i: s["obv"][i] > s["obv"][i - 20]),
    ("平均足が陽線", lambda s, i: s["ha_bull"][i]),
    ("CCI(20)＞100", lambda s, i: s["cci"][i] is not None and s["cci"][i] > 100),
    ("CCI(20)＜−100", lambda s, i: s["cci"][i] is not None and s["cci"][i] < -100),
    ("MFI(14)≦20", lambda s, i: s["mfi14"][i] is not None and s["mfi14"][i] <= 20),
    ("ADX≧40", lambda s, i: s["adx"][i] is not None and s["adx"][i] >= 40),
    ("ボリンジャー: バンド幅が6か月で一番狭い近く（下位20%）", lambda s, i: s["bw_rank"][i] is not None and s["bw_rank"][i] <= 0.2),
    ("ボリンジャー: %b≦0（下のバンドの外）", lambda s, i: s["pctb"][i] is not None and s["pctb"][i] <= 0),
    ("酒田: 下げ三法・切り込み線・たくり線・包み足・明けの明星のどれか（3日以内）",
     lambda s, i: any(ef.ss_safe(f, s, j) for f in (ss.bull_engulf, ss.hammer, ss.morning_star, ss.piercing) for j in range(i - 2, i + 1))),
    ("酒田: 窓を開けて上げる（1%以上）", lambda s, i: s["l"][i] > s["h"][i - 1] * 1.01),
]


# ---------- まだ試していない買いのルール（空き枠を埋める） ----------
def E_sanyaku(i, s):           # 一目の三役好転が今日そろった
    t, k, ch, c = s["ten"], s["kij"], s["cloud_hi"], s["c"]
    def ok(x):
        return None not in (t[x], k[x], ch[x]) and t[x] > k[x] and c[x] > ch[x] and c[x] > c[x - 26]
    return -s["rs"][i] if i > 30 and ok(i) and not ok(i - 1) else None


def E_gc50_200(i, s):          # 50日線と200日線のゴールデンクロス
    a, b = s["ma50"], s["ma200"]
    return -s["rs"][i] if None not in (a[i], b[i], a[i - 1], b[i - 1]) and a[i] > b[i] and a[i - 1] <= b[i - 1] else None


def E_three_white_up(i, s):    # 50日線の上で赤三兵
    return -s["rs"][i] if s["ma50"][i] is not None and s["c"][i] > s["ma50"][i] and ef.ss_safe(ss.three_white, s, i) else None


def E_bb_candle(i, s):         # 下のバンドの近く（%b≦0.1、直近3日）で強気の包み足・たくり線・明けの明星・切り込み線（酒田×ボリンジャー）
    pb = s["pctb"]
    if not any(x is not None and x <= 0.1 for x in pb[i - 2:i + 1]):
        return None
    return pb[i] if any(ef.ss_safe(f, s, i) for f in (ss.bull_engulf, ss.hammer, ss.morning_star, ss.piercing)) else None


def E_macd_zero(i, s):         # 200日線の上で、MACDが0を上に抜ける
    m, b = s["macd"], s["ma200"]
    return -s["rs"][i] if b[i] is not None and s["c"][i] > b[i] and m[i] > 0 >= m[i - 1] else None


def E_donchian55(i, s):        # タートルの55日ブレイク
    c = s["c"]
    return -s["rs"][i] if i > 56 and c[i] > max(s["h"][i - 55:i]) else None


def E_squeeze(i, s):           # ボリンジャー メソッドI（スクイーズの上抜け）
    r = bs.O_squeeze(i, s)
    return r["rank"] if r else None


def E_holy(i, s):              # ラシュキの聖杯を、翌日の寄り付きで買う形に近似（ADX≧30・上昇中・20日EMAまで押す）
    a, a1, e = s["adx14"][i], s["adx14"][i - 1], s["ema20"][i]
    return -a if None not in (a, a1, e) and a >= 30 and a > a1 and s["l"][i] <= e < s["c"][i] else None


def E_ha_turn(i, s):           # 50日線の上で平均足が陰線から陽線に変わる
    return -s["rs"][i] if s["ma50"][i] is not None and s["c"][i] > s["ma50"][i] and s["ha_bull"][i] and not s["ha_bull"][i - 1] else None


def E_nr7(i, s):               # NR7（直近7日で一番小さい値幅）の翌日、上に抜けたら（寄り付きで買う形に近似: 当日の終値が前日の高値を上抜け）
    h, l = s["h"], s["l"]
    rng = [h[k] - l[k] for k in range(i - 7, i)]
    return -s["rs"][i] if i > 8 and rng[-1] == min(rng) and s["c"][i] > h[i - 1] else None


BELOW50 = lambda j, s, k, px: s["ma50"][j] is not None and s["c"][j] < s["ma50"][j]
UPPER = lambda j, s, k, px: s["pctb"][j] is not None and s["pctb"][j] >= 1.0
RULES = [("一目の三役好転（50日線割れで手じまい）", E_sanyaku, BELOW50, 500), ("50日線と200日線のゴールデンクロス（50日線割れ）", E_gc50_200, BELOW50, 500),
         ("50日線の上で赤三兵（50日線割れ）", E_three_white_up, BELOW50, 500),
         ("下のバンドの近くで強気のローソク足（酒田×ボリンジャー、上のバンドで手じまい）", E_bb_candle, UPPER, 60),
         ("200日線の上でMACDが0を上抜け（50日線割れ）", E_macd_zero, BELOW50, 500), ("タートルの55日ブレイク（50日線割れ）", E_donchian55, BELOW50, 500),
         ("ボリンジャー メソッドI＝スクイーズの上抜け（50日線割れ）", E_squeeze, BELOW50, 500),
         ("ラシュキの聖杯に近い押し目（上のバンドで手じまい）", E_holy, UPPER, 60), ("50日線の上で平均足が陽線に変わる（50日線割れ）", E_ha_turn, BELOW50, 500),
         ("NR7の上抜け（50日線割れ）", E_nr7, BELOW50, 500)]


def prep_more(s):
    o, h, l, c, v, n = s["o"], s["h"], s["l"], s["c"], s["v"], len(s["c"])
    xs.prep(s)
    rb.prep2(s)
    s["adx"] = ef.adx_of(s)
    def mid(p, i):
        return (max(h[i - p + 1:i + 1]) + min(l[i - p + 1:i + 1])) / 2 if i >= p - 1 else None
    ten, kij = s["ten"], s["kij"]
    sa = [None if ten[i] is None or kij[i] is None else (ten[i] + kij[i]) / 2 for i in range(n)]
    sb = [mid(52, i) for i in range(n)]
    s["cloud_hi"] = [None] * 26 + [None if sa[i] is None or sb[i] is None else max(sa[i], sb[i]) for i in range(n - 26)]
    ef.prep_weekly(s)
    # OBV・CCI・MFI・平均足・バンド幅の順位
    ob = [0.0] * n
    for i in range(1, n):
        ob[i] = ob[i - 1] + (v[i] if c[i] > c[i - 1] else -v[i] if c[i] < c[i - 1] else 0)
    s["obv"] = ob
    tp = [(h[i] + l[i] + c[i]) / 3 for i in range(n)]
    cci = [None] * n
    for i in range(19, n):
        w = tp[i - 19:i + 1]
        m = sum(w) / 20
        md = sum(abs(x - m) for x in w) / 20
        cci[i] = 0.0 if md == 0 else (tp[i] - m) / (0.015 * md)
    s["cci"] = cci
    mfi = [None] * n
    for i in range(15, n):
        pos_ = sum(tp[k] * v[k] for k in range(i - 13, i + 1) if tp[k] > tp[k - 1])
        neg_ = sum(tp[k] * v[k] for k in range(i - 13, i + 1) if tp[k] < tp[k - 1])
        mfi[i] = 100.0 if neg_ == 0 else 100 - 100 / (1 + pos_ / neg_)
    s["mfi14"] = mfi
    hc, ho = [0.0] * n, [0.0] * n
    hc[0], ho[0] = (o[0] + h[0] + l[0] + c[0]) / 4, (o[0] + c[0]) / 2
    for i in range(1, n):
        hc[i] = (o[i] + h[i] + l[i] + c[i]) / 4
        ho[i] = (ho[i - 1] + hc[i - 1]) / 2
    s["ha_bull"] = [hc[i] > ho[i] for i in range(n)]
    up, dn, md_ = s["bb_up"], s["bb_dn"], s["bb_mid"]
    bw = [None if None in (up[i], dn[i], md_[i]) else (up[i] - dn[i]) / md_[i] for i in range(n)]
    s["bw_rank"] = [None] * n
    for i in range(130, n):
        win = [x for x in bw[i - 125:i + 1] if x is not None]
        if bw[i] is not None and win:
            s["bw_rank"][i] = sum(1 for x in win if x < bw[i]) / len(win)
    if "adx14" not in s or "ema20" not in s:
        s["adx14"] = s["adx"]
        s["ema20"] = ema(c, 20)
    # 週足の合図（週の最後の取引日に判定）
    ends = [k for k in range(n) if k + 1 == n or dt.date.fromisoformat(s["date"][k + 1]).isocalendar()[1] != dt.date.fromisoformat(s["date"][k]).isocalendar()[1]]
    starts = [0] + [e + 1 for e in ends[:-1]]
    ws = {"o": [o[a] for a in starts], "h": [max(h[a:b + 1]) for a, b in zip(starts, ends)], "l": [min(l[a:b + 1]) for a, b in zip(starts, ends)],
          "c": [c[b] for b in ends], "v": [sum(v[a:b + 1]) for a, b in zip(starts, ends)], "date": [s["date"][b] for b in ends]}
    xs.prep(ws)
    wm10 = sma(ws["c"], 10)
    s["wsig"] = {}
    for nm, f in WEEKLY:
        arr = [False] * n
        for w_, e in enumerate(ends):
            if w_ < 30:
                continue
            if f is None:
                val = wm10[w_] is not None and wm10[w_ - 1] is not None and ws["c"][w_] < wm10[w_] and ws["c"][w_ - 1] >= wm10[w_ - 1]
            elif f == "macd":
                val = xs.cross_below(ws["macd"], ws["macd_sig"], w_)
            else:
                val = ef.ss_safe(f, ws, w_)
            arr[e] = bool(val)
        s["wsig"][nm] = arr


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cache", default=DEFAULT_CACHE)
    r.add_argument("--stage", default="all", choices=("sell", "combo", "half", "filter", "rule", "stats", "all"))
    a = ap.parse_args()
    ctx = cb.setup(a.cache, with_parts=False)
    data, members, ind, days, G, end = (ctx[k] for k in ("data", "members", "ind", "days", "G", "end"))
    pos = {}

    def idx(sym, d):
        if sym not in pos:
            pos[sym] = {x: k for k, x in enumerate(data[sym]["date"])}
        return pos[sym][d]

    def b3_exit(t):
        s, sym = data[t["sym"]], t["sym"]
        o, h, l, c = s["o"], s["h"], s["l"], s["c"]
        i0, n, px = idx(sym, t["in"]), len(c), t["px"]
        floor, pend, j = px * (1 - STOP), False, i0
        while j < n:
            if pend:
                return j, o[j]
            if l[j] <= floor:
                return j, min(o[j] if j > i0 else px, floor)
            if j > i0 and s["bb_up"][j - 1] is not None and h[j] >= s["bb_up"][j - 1]:
                return j, max(o[j], s["bb_up"][j - 1])
            if j + 1 >= n:
                return None
            if j - i0 >= bs.MAX_HOLD or (s["pctb"][j] is not None and s["pctb"][j] >= 1.0):
                pend = True
            j += 1
        return None

    old, bs.STOP_MAX = bs.STOP_MAX, STOP
    try:
        b3_raw = bs.simulate(data, members, bs.O_method3, bs.X_upper_band, cb.START, end, ok=ctx["ok_rot"])
    finally:
        bs.STOP_MAX = old

    def rec(sym, i0, i1, px, xp, rule, prio=0):
        return {"sym": sym, "i0": i0, "i1": i1, "px": px, "xp": xp, "rule": rule, "prio": prio}

    base = []
    for t in b3_raw:
        x = b3_exit(t)
        if x:
            base.append(rec(t["sym"], idx(t["sym"], t["in"]), x[0], t["px"], x[1], "B"))

    def from_gen(lst, rule, prio=0):
        return [rec(t["sym"], idx(t["sym"], t["in"]), idx(t["sym"], t["out"]), t["px"], t["px"] * (1 + t["ret"]), rule, prio) for t in lst]

    base += from_gen(G(ctx["CR"](10), ctx["above5"], ctx["ok_rot"], STOP, 60), "C")
    base += from_gen(G(bm2.E_base(2.0), ctx["below50"], ctx["ok_rot"], STOP), "M")
    base += from_gen(G(ctx["v2o"], ctx["below50"], ctx["ok10"], STOP), "V")
    need = {t["sym"] for t in base} if a.stage not in ("rule", "all") else set(data)
    for k, sym in enumerate(sorted(need)):
        prep_more(data[sym])
    print(f"準備ができた（{len(need)}銘柄）", file=sys.stderr)

    def safe(f, s, j):
        try:
            return bool(f(s, j))
        except (TypeError, ValueError, IndexError, ZeroDivisionError, KeyError):
            return False

    TREND, REV = ("M", "V"), ("B", "C")

    def sim(t, extra=(), extra_rules=(), half="c1", half_rules=TREND, full_dc=True, dc_half=False, bear_rev=True):
        """1つの枠の価値の推移（最初を1）。extra の合図は extra_rules の売買に当て、翌日の寄り付きで全部売って枠を空ける"""
        s = data[t["sym"]]
        o, c = s["o"], s["c"]
        i0, i1, px = t["i0"], t["i1"], t["px"]
        if i1 == i0:
            return {s["date"][i0]: (1 - COST) * t["xp"] / px * (1 - COST)}
        sh, k = (1 - COST) / px, 0.0
        path = {s["date"][i0]: sh * c[i0]}
        pend, half_done = None, t["rule"] not in half_rules
        trend = t["rule"] in TREND
        fns = list(extra) if t["rule"] in extra_rules else []
        for j in range(i0 + 1, i1 + 1):
            d = s["date"][j]
            if j == i1:
                path[d] = k + sh * t["xp"] * (1 - COST)
                break
            if pend == "sell":
                path[d] = k + sh * o[j] * (1 - COST)
                break
            if pend == "half":
                k += sh / 2 * o[j] * (1 - COST)
                sh /= 2
            pend = None
            path[d] = k + sh * c[j]
            if j + 1 >= i1:
                continue
            if trend and full_dc and safe(xs.dark_cloud, s, j):
                if dc_half and not half_done:
                    pend, half_done = "half", True
                    continue
                if not dc_half:
                    pend = "sell"
                    continue
            if bear_rev and not trend and safe(rb.big_bear, s, j):     # 逆張りの大陰線（2026-10-02 採用）
                pend = "sell"
                continue
            if any(safe(f, s, j) for f in fns):
                pend = "sell"
            elif not half_done and half and safe(half, s, j):
                pend, half_done = "half", True
        return path

    def build(extra=(), extra_rules=(), drop=None, add=(), **kw):
        out = []
        half = kw.pop("half", "c1")
        hf = xc.c1 if half == "c1" else half
        for t in list(base) + list(add):
            if drop and drop(t):
                continue
            p = sim(t, extra, extra_rules, half=hf, **kw)
            out.append({"sym": t["sym"], "in": data[t["sym"]]["date"][t["i0"]], "out": max(p), "path": p, "prio": t["prio"], "rule": t["rule"]})
        return out

    is_hi = max(d for d in days if d <= cb.IS_END)
    oos_lo = min(d for d in days if d >= cb.OOS_START)

    def port(trs, seed, lo, hi):
        dd = [d for d in days if lo <= d <= hi]
        by_in = {}
        for t in trs:
            if lo <= t["in"] and t["out"] <= hi:
                by_in.setdefault(t["in"], []).append(t)
        rnd = random.Random(seed)
        cash, held, peak, mdd, eq = 1.0, [], 1.0, 0.0, 1.0
        for d in dd:
            still = []
            for h in held:
                v = h["t"]["path"].get(d)
                if v is not None:
                    h["v"] = v
                if h["t"]["out"] == d:
                    cash += h["size"] * h["v"]
                else:
                    still.append(h)
            held = still
            eq = cash + sum(h["size"] * h["v"] for h in held)
            for t in sorted(by_in.get(d, []), key=lambda t: (t["prio"], rnd.random())):
                if any(h["t"]["sym"] == t["sym"] for h in held):
                    continue
                if len(held) >= SLOTS:
                    break
                if sum(1 for h in held if ind.get(h["t"]["sym"]) == ind.get(t["sym"])) >= 2:
                    continue
                size = min(eq / SLOTS, cash)
                if size <= 0:
                    break
                cash -= size
                v0 = t["path"].get(d, 1.0)
                if t["out"] == d:
                    cash += size * v0
                    continue
                held.append({"t": t, "size": size, "v": v0})
            eq = cash + sum(h["size"] * h["v"] for h in held)
            peak = max(peak, eq)
            mdd = max(mdd, 1 - eq / peak)
        yrs = (dt.date.fromisoformat(dd[-1]) - dt.date.fromisoformat(dd[0])).days / 365.25
        return eq ** (1 / yrs) - 1, mdd

    def ev(trs, seeds):
        s0, n = seeds
        a_ = [port(trs, s0 + k, days[0], days[-1]) for k in range(n)]
        i_ = [port(trs, s0 + k, days[0], is_hi)[0] for k in range(n)]
        o_ = [port(trs, s0 + k, oos_lo, days[-1])[0] for k in range(n)]
        return {"all": cb.med([x[0] for x in a_]), "mdd": cb.med([x[1] for x in a_]), "is": cb.med(i_), "oos": cb.med(o_)}

    cur_tr = build()
    CUR = {sd: ev(cur_tr, sd) for sd in (SCREEN, CONF1, CONF2)}
    print("土台", {k[0]: (round(v["all"], 3), round(v["is"], 3), round(v["oos"], 3)) for k, v in CUR.items()}, file=sys.stderr)

    def better(e, sd):
        return e["is"] > CUR[sd]["is"] and e["oos"] > CUR[sd]["oos"]

    def cell(e):
        return f"{pct(e['all'])} | {pct(e['mdd'])} | {pct(e['is'])} | {pct(e['oos'])}"

    def screen_and_confirm(title, items, w):
        """items: [(ラベル, 売買の一覧を作る関数)]。ふるい→確認"""
        w(f"\n## {title}\n")
        c0 = CUR[SCREEN]
        w(f"今のルール（乱数20通り）: 年率 {pct(c0['all'])}、最大下落率 {pct(c0['mdd'])}、設計期間 {pct(c0['is'])}、確認期間 {pct(c0['oos'])}\n")
        w("| 形 | 年率 | 最大下落率 | 設計期間 | 確認期間 | ふるい |")
        w("|---|---|---|---|---|---|")
        res, passed = [], []
        for lab, mk in items:
            trs = mk()
            e = ev(trs, SCREEN)
            ok = better(e, SCREEN)
            res.append((lab, e, trs))
            w(f"| {lab} | {cell(e)} | {'通過' if ok else ''} |")
            if ok:
                passed.append((lab, e, trs))
            print(title, lab, "通過" if ok else "", file=sys.stderr)
        w(f"\n通過: {len(passed)}通り / {len(items)}通り\n")
        sure = []
        if passed:
            w("### 確認（別の乱数50通り×2組）\n")
            c1_, c2_ = CUR[CONF1], CUR[CONF2]
            w(f"今のルール: 1組目 年率 {pct(c1_['all'])}・最大下落率 {pct(c1_['mdd'])}・設計 {pct(c1_['is'])}・確認 {pct(c1_['oos'])}／"
              f"2組目 {pct(c2_['all'])}・{pct(c2_['mdd'])}・{pct(c2_['is'])}・{pct(c2_['oos'])}\n")
            w("| 形 | 1組目 年率 | 最大下落率 | 設計 | 確認 | 2組目 年率 | 最大下落率 | 設計 | 確認 | 3組とも両方の期間で上回ったか |")
            w("|---|---|---|---|---|---|---|---|---|---|")
            for lab, e0, trs in passed:
                e1, e2 = ev(trs, CONF1), ev(trs, CONF2)
                ok = better(e1, CONF1) and better(e2, CONF2)
                w(f"| {lab} | {cell(e1)} | {cell(e2)} | {'**確か**' if ok else ''} |")
                if ok:
                    sure.append((lab, e0, e1, e2, trs))
                print(title, lab, "確か" if ok else "×", file=sys.stderr)
        return res, sure

    if a.stage == "stats":
        return rule_stats(cur_tr, days, port, ev, CUR, CONF1, is_hi, oos_lo)
    stages = ("sell", "combo", "half", "filter", "rule") if a.stage == "all" else (a.stage,)
    groups = (("順張り", TREND), ("逆張り", REV))
    sell_all = [(nm, f) for nm, f in OLD_SELLS] + [(nm, f) for nm, f in NEW_SELLS] + [(nm, weekly(nm)) for nm, _ in WEEKLY]
    new_names = {nm for nm, _ in NEW_SELLS} | {nm for nm, _ in WEEKLY}
    sell_res = {}
    for st in stages:
        L = []
        w = L.append
        title = {"sell": "売りの合図のやり直し", "combo": "売りの合図の組み合わせ", "half": "半分売りとかぶせ線の役割分担",
                 "filter": "買いの条件のやり直し", "rule": "まだ試していない買いのルール"}[st]
        w(f"---\ntype: backtest\ntitle: {title}\ncreated: {dt.date.today()}\nscript: tools/backtest_retest.py --stage {st}\n---\n")
        w(f"# {title}（今の測り方でのやり直し）\n")
        w(__doc__.split("\n", 5)[5].strip() + "\n")
        if st in ("sell", "combo"):
            for gl, rules in groups:
                if gl not in sell_res:
                    items = [((("★" if nm in new_names else "") + nm), (lambda f=f, rules=rules: build(extra=(f,), extra_rules=rules)))
                             for nm, f in sell_all]
                    res, sure = screen_and_confirm(f"{gl}（{'・'.join(rules)}）に売りの合図を足す", items, w)
                    sell_res[gl] = res
                    if st == "sell":
                        continue
                ranked = sorted(sell_res[gl], key=lambda x: -min(x[1]["is"] - CUR[SCREEN]["is"], x[1]["oos"] - CUR[SCREEN]["oos"]))[:6]
                fmap = dict((("★" if nm in new_names else "") + nm, f) for nm, f in sell_all)
                items = []
                for (l1, _, _), (l2, _, _) in itertools.combinations(ranked, 2):
                    items.append((f"{l1} または {l2}", (lambda f1=fmap[l1], f2=fmap[l2], rules=rules: build(extra=(f1, f2), extra_rules=rules))))
                screen_and_confirm(f"{gl}: ふるいの上位6つの合図を2つずつ組み合わせる", items, w)
        if st == "half":
            items = [("半分売りをやめる（かぶせ線の全部売りだけ）", lambda: build(half=None)),
                     ("かぶせ線も半分売りにする（2つとも半分）", lambda: build(dc_half=True)),
                     ("反転の合図でも全部売る（2つとも全部）", lambda: build(extra=(xc.c1,), extra_rules=TREND, half=None)),
                     ("かぶせ線をやめる（半分売りだけ）", lambda: build(full_dc=False)),
                     ("半分売り・かぶせ線を逆張りにも当てる", lambda: build(extra=(xs.dark_cloud,), extra_rules=REV, half_rules=TREND + REV))]
            screen_and_confirm("半分売りとかぶせ線の役割分担", items, w)
        if st == "filter":
            pos_i = lambda t: t["i0"] - 1
            filt = [(nm, f) for nm, f in ef.FILTERS] + [("★" + nm, f) for nm, f in NEW_FILTERS]
            for gl, rules in (("全部", TREND + REV),) + groups:
                items = [(nm, (lambda f=f, rules=rules: build(drop=lambda t: t["rule"] in rules and not safe(f, data[t["sym"]], pos_i(t)))))
                         for nm, f in filt]
                screen_and_confirm(f"{gl}の買いの合図に条件を重ねる", items, w)
        if st == "rule":
            items = []
            for nm, e_, x_, mh in RULES:
                tr = from_gen(gen_trades(data, members, e_, x_, cb.START, end, ok=ctx["ok_rot"], fill="open", max_hold=mh, stop_pct=STOP), "N", prio=1)
                items.append((f"{nm}（{len(tr)}件）", (lambda tr=tr: build(add=tr))))
            screen_and_confirm("空き枠を埋める買いのルールを足す（今の4つのルールの候補が優先）", items, w)
        w("\n## 注意\n")
        w("- ★はこれまで試していなかった合図・条件。数値（出来高1.5倍、ATRの倍数、日数など）はClaudeが置いたもの。")
        w("- たくさんの形を試すと、偶然良く見える形が混ざる。乱数を変えた3組すべてで、設計・確認の両方の期間で上回った形だけを「確か」とした。")
        w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
        out = OUTDIR + f"やり直し_{title}.md"
        os.makedirs(OUTDIR, exist_ok=True)
        open(out, "w", encoding="utf-8").write("\n".join(L) + "\n")
        print(f"書き出し: {out}", file=sys.stderr)


def rule_stats(trs, days, port, ev, CUR, seeds, is_hi, oos_lo):
    """今のルール（売りの改善後）で、ルールごとの成績を出す。毎朝のレポートの「過去の成績」の列に使う（`新分析ツール/ルールの成績.json`）"""
    import json
    yrs = (dt.date.fromisoformat(days[-1]) - dt.date.fromisoformat(days[0])).days / 365.25
    names = {"B": "押し目（ボリンジャーIII）", "C": "急落の底", "M": "ミネルヴィニ（ベースの上抜け）", "V": "新高値V2"}
    out, L = {}, []
    w = L.append
    w(f"---\ntype: backtest\ntitle: ルールごとの成績（今のルール）\ncreated: {dt.date.today()}\nscript: tools/backtest_retest.py --stage stats\n---\n")
    w("# ルールごとの成績（売りの改善後の今のルール）\n")
    w("後知恵なしの監視銘柄、2015年〜。今の売りのルール（押し目の指値売り・押し目と急落の底の大陰線、順張りのかぶせ線・半分売り、損切り15%）で計算した、"
      "全部の合図の1回ごとの成績（枠に入らなかった合図も含む）。片道0.1%込み。「設計／確認」は 2015〜2021年／2022年〜 に買った合図の1回平均。\n")
    w("| 順位 | ルール | 合図の数（年あたり） | 勝率 | 1回平均 | PF（利益÷損失） | 1回平均 設計／確認 | 保有日数（中央値） |")
    w("|---|---|---|---|---|---|---|---|")
    rows = []
    for k, nm in names.items():
        ts = [t for t in trs if t["rule"] == k]
        rets = [t["path"][t["out"]] - 1 for t in ts]
        win = [x for x in rets if x > 0]
        loss = [-x for x in rets if x <= 0]
        des = [t["path"][t["out"]] - 1 for t in ts if t["in"] <= is_hi]
        con = [t["path"][t["out"]] - 1 for t in ts if t["in"] >= oos_lo]
        hold = sorted((dt.date.fromisoformat(t["out"]) - dt.date.fromisoformat(t["in"])).days for t in ts)
        r = {"name": nm, "n_per_year": round(len(ts) / yrs, 1), "win": round(len(win) / len(rets), 3), "avg": round(sum(rets) / len(rets), 4),
             "pf": round(sum(win) / sum(loss), 2) if loss else None, "avg_design": round(sum(des) / len(des), 4) if des else None,
             "avg_confirm": round(sum(con) / len(con), 4) if con else None, "hold_days": hold[len(hold) // 2]}
        rows.append((k, r))
    rows.sort(key=lambda x: -x[1]["avg"])
    for rank, (k, r) in enumerate(rows, 1):
        r["rank"] = rank
        out[k] = r
        w(f"| {rank} | {r['name']} | {r['n_per_year']} | {pct(r['win'], 0)} | {pct(r['avg'], 2)} | {r['pf']} | "
          f"{pct(r['avg_design'], 2)}／{pct(r['avg_confirm'], 2)} | {r['hold_days']}日 |")
    c = CUR[seeds]
    w(f"\n資金全体（4銘柄・25%、乱数50通りの中央値）: 年率 {pct(c['all'])}、最大下落率 {pct(c['mdd'])}、設計期間 {pct(c['is'])}、確認期間 {pct(c['oos'])}\n")
    w("順位は1回平均（1回の売買で平均いくら増えるか）の順。勝率だけでは、勝つと大きいルール（新高値V2など）を低く見てしまうため。")
    w("保有日数は暦日。最大下落率は、期間全体（2015年〜）で資金全体が直前の最高値から一番下がった割合。")
    w("\n- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    out["_meta"] = {"updated": str(dt.date.today()), "source": "新分析ツール/バックテスト結果/ルールごとの成績.md",
                    "cagr": round(c["all"], 4), "mdd": round(c["mdd"], 4)}
    open("新分析ツール/ルールの成績.json", "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    open(OUTDIR + "ルールごとの成績.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("書き出し: 新分析ツール/ルールの成績.json・ルールごとの成績.md", file=sys.stderr)


if __name__ == "__main__":
    main()
