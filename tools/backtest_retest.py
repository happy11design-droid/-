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
import backtest_lib as bl
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
    r.add_argument("--etf", default=None, help="etf2x: 2倍ETFにする銘柄（カンマ区切り）。省略すると backtest_2x.HAS_2X")
    r.add_argument("--drag", default=None, help="etf2x: 2倍ETFの目減り（年率）。数値なら全部同じ、'measured' なら 新分析ツール/2倍ETFの対応表.json の実測（ないものは0.12）")
    r.add_argument("--tag", default="", help="etf2x: 結果のファイル名と見出しに付ける名前（例: ムームー証券）")
    r.add_argument("--stage", default="all", choices=("sell", "combo", "half", "filter", "rule", "stats", "dd", "robust", "earn", "realized", "etf2x", "etfrule", "weinstein", "rsi", "pivot", "exits", "pullback", "recover", "prio", "slope", "slope2", "slope3", "swap", "premium", "hot", "hotyear", "ideas", "theme", "halfadd", "replay", "stopcheck", "actual", "stopfreq", "themedrop", "crashstops", "ddsize", "shock", "parity", "audit", "opt1", "opt2", "all"))
    r.add_argument("--keep-open", action="store_true", help="データの最終日までに売りが来ていない売買も最終日の終値で数える（2026-10-16 の点検。以前は数えなかった）")
    r.add_argument("--overlap", action="store_true", help="同じ銘柄の売買を持っている間の合図も数える（2026-10-16 の点検。以前は数えなかった）")
    r.add_argument("--recdir", default=None, help="parity: 毎朝の record.json を置いたディレクトリ")
    r.add_argument("--watch87", action="store_true", help="actual: 監視銘柄を後知恵なしの一覧ではなく 新分析ツール/テーマ監視銘柄.md の銘柄に固定する（後知恵あり。S&P500の構成銘柄かどうかは問わない）")
    a = ap.parse_args()
    bl.KEEP_OPEN, bl.OVERLAP = a.keep_open, a.overlap
    ctx = cb.setup(a.cache, with_parts=False)
    data, members, ind, days, G, end = (ctx[k] for k in ("data", "members", "ind", "days", "G", "end"))
    if a.watch87:   # 今のテーマ監視銘柄（87銘柄）だけにルールを当てる（2026-10-14 ユーザーの指示。後知恵あり）
        import re as re_
        md = open(os.path.join(os.path.dirname(OUTDIR.rstrip("/")), "テーマ監視銘柄.md"), encoding="utf-8").read()
        W87 = {m.group(1) for m in re_.finditer(r"(?m)^\| ([A-Z][A-Z0-9.\-]*) \|", md) if m.group(1) != "ティッカー"} & set(data)
        print(f"テーマ監視銘柄 {len(W87)} 銘柄（データあり）", file=sys.stderr)
        liq = lambda s_, i: s_["vol50"][i] is not None and s_["c"][i] >= 5 and s_["vol50"][i] >= 250_000
        rank10 = {}
        posm = {x: {d_: k for k, d_ in enumerate(data[x]["date"])} for x in W87}
        for d_ in days:
            rk = sorted(((data[x]["rs"][posm[x][d_]] or 0, x) for x in W87 if d_ in posm[x]), reverse=True)
            rank10[d_] = {x for _, x in rk[:10]}
        ctx["ok_rot"] = lambda s_, i, sp: s_["sym"] in W87 and liq(s_, i)
        ctx["ok10"] = lambda s_, i, sp: s_["sym"] in W87 and liq(s_, i) and s_["sym"] in rank10.get(s_["date"][i], ())
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
                return (j, c[j]) if bl.KEEP_OPEN else None   # データの最終日: 以前は数えなかった（2026-10-16 の点検）
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
            out.append({"sym": t["sym"], "in": data[t["sym"]]["date"][t["i0"]], "out": max(p), "path": p, "prio": t["prio"], "rule": t["rule"], "w": t.get("w", 1.0)})
        return out

    is_hi = max(d for d in days if d <= cb.IS_END)
    oos_lo = min(d for d in days if d >= cb.OOS_START)

    def port(trs, seed, lo, hi, curve=None, rcurve=None, closed=None):
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
                    if closed is not None:
                        closed.append((d, h["t"]["path"][d] - 1, h["size"] * (h["v"] - 1)))
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
                size = min(eq / SLOTS * t.get("w", 1.0), cash)
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
            if curve is not None:
                curve.append(eq)
            if rcurve is not None:
                rcurve.append(cash + sum(h["size"] for h in held))   # 持っている株は買った額のまま（確定した損益だけ）
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

    if a.stage == "weinstein":
        import backtest_trend as bt_
        for d_ in data.values():
            if "wend" not in d_:
                bt_.weekly(d_)
        wt = gen_trades(data, members, bt_.E_weinstein(10, ma="10"), bt_.X_weekly_below("10"), cb.START, end, ok=ctx["ok_rot"],
                        fill="open", max_hold=500, stop_pct=STOP)
        W_plain = from_gen(wt, "W")
        W_trend = from_gen(wt, "M")            # 順張りと同じ売り（かぶせ線で全部・反転の合図で半分）も当てる
        W_low = from_gen(wt, "M", prio=1)      # 空き枠だけ
        for t in W_plain + W_trend + W_low:
            prep_more(data[t["sym"]]) if "rsi14" not in data[t["sym"]] else None
        L = []
        w = L.append
        w(f"---\ntype: backtest\ntitle: ワインスタイン10週を加えるか\ncreated: {dt.date.today()}\nscript: tools/backtest_retest.py --stage weinstein\n---\n")
        w("# ワインスタイン10週を5つ目のルールとして加えるか（今の測り方）\n")
        w("ワインスタイン10週: 金曜（週の最終取引日）の引けで、週足の終値が10週線より上・10週線が前週より上・直前10週の高値を上抜け・その週の出来高が直前4週の平均の2倍以上"
          "→ 翌取引日の寄り付きで買う。手じまいは週足の終値が10週線割れ（翌取引日の寄り付き）、損切り15%。後知恵なしの監視銘柄（2015年〜）。"
          f"合図 {len(wt)}件（年{len(wt) / 11.7:.0f}件）。以前は今の87銘柄（後知恵あり）の直近3年だけで試していた（`テーマ監視銘柄・直近3年.md`）。\n")
        tr_ = build(add=W_plain)
        wr = [t["path"][t["out"]] - 1 for t in tr_ if t["rule"] == "W"]
        if wr:
            des = [t["path"][t["out"]] - 1 for t in tr_ if t["rule"] == "W" and t["in"] <= is_hi]
            con = [t["path"][t["out"]] - 1 for t in tr_ if t["rule"] == "W" and t["in"] >= oos_lo]
            w(f"ワインスタイン10週の全部の合図: 勝率 {pct(sum(1 for x in wr if x > 0) / len(wr), 0)}、1回平均 {pct(sum(wr) / len(wr), 2)}"
              f"（設計期間 {pct(sum(des) / len(des), 2) if des else '-'}／確認期間 {pct(sum(con) / len(con), 2) if con else '-'}）\n")
        items = [("今の4つ＋ワインスタイン10週（売りは10週線割れだけ）", lambda: build(add=W_plain)),
                 ("今の4つ＋ワインスタイン10週（順張りと同じく、かぶせ線・反転の合図でも売る）", lambda: build(add=W_trend)),
                 ("今の4つ＋ワインスタイン10週を空き枠だけ（順張りと同じ売り）", lambda: build(add=W_low))]
        screen_and_confirm("ワインスタイン10週を加える", items, w)
        w("\n- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
        open(OUTDIR + "ワインスタイン10週を加えるか.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
        print("書き出し", file=sys.stderr)
        return
    if a.stage == "etfrule":
        return etf_rule_stage(build, port, ev, (SCREEN, CONF1, CONF2), days, set(a.etf.split(",")))
    if a.stage == "etf2x":
        return etf2x_stage(build, port, ev, CUR, (SCREEN, CONF1, CONF2), days, is_hi, oos_lo,
                           set(a.etf.split(",")) if a.etf else None, a.tag, a.drag)
    if a.stage == "realized":
        import statistics
        tr = build()
        S0, NS = CONF1
        rows = []
        for k in range(NS):
            c, rc, cl = [], [], []
            port(tr, S0 + k, days[0], days[-1], curve=c, rcurve=rc, closed=cl)
            def mdd_of(x):
                pk, m, start, worst = x[0], 0.0, 0, (0, 0, 0)
                for i, v in enumerate(x):
                    if v > pk:
                        pk, start = v, i
                    if 1 - v / pk > m:
                        m, worst = 1 - v / pk, (start, i)
                return m, worst
            m1, w1 = mdd_of(c)
            m2, w2 = mdd_of(rc)
            loss = [x for x in cl if x[1] < 0]
            stop = [x for x in cl if x[1] <= -0.14]
            rows.append({"mtm": m1, "real": m2, "w1": w1, "w2": w2, "n": len(cl), "loss": len(loss), "stop": len(stop),
                         "loss_amt": -sum(x[2] for x in loss), "stop_amt": -sum(x[2] for x in stop)})
        med = lambda key: statistics.median(r[key] for r in rows)
        srt_ = sorted(rows, key=lambda r: r["mtm"])
        mid = srt_[len(srt_) // 2]
        yrs = (dt.date.fromisoformat(days[-1]) - dt.date.fromisoformat(days[0])).days / 365.25
        L = []
        w = L.append
        w(f"---\ntype: backtest\ntitle: 含み損を入れた下落率と、確定した損益だけの下落率\ncreated: {dt.date.today()}\nscript: tools/backtest_retest.py --stage realized\n---\n")
        w("# 含み損を入れた最大下落率と、売って確定した損益だけの最大下落率\n")
        w("今のルール、2015年〜、乱数50通り。\n")
        w("- 含み損を入れた下落率: 毎日の引け値で「現金＋持っている株の時価」を計算し、それまでの最高から一番下がった割合（今までの表の最大下落率）。")
        w("- 確定した損益だけの下落率: 持っている株は買った額のまま数え、売って損益が確定したときだけ資金が増減するとした場合の、最高から一番下がった割合。"
          "損切りだけでなく、ルールの売り（50日線割れ・かぶせ線・大陰線など）で損が出た売買も含む。利益が出た売買は資金を増やす。\n")
        w("| | 中央値 | 50通りの中で一番悪い |")
        w("|---|---|---|")
        w(f"| 含み損を入れた最大下落率 | {pct(med('mtm'))} | {pct(max(r['mtm'] for r in rows))} |")
        w(f"| 確定した損益だけの最大下落率 | {pct(med('real'))} | {pct(max(r['real'] for r in rows))} |")
        d_ = lambda ij: f"{days[ij[0]]}〜{days[ij[1]]}"
        w(f"\n中央値の1通りで、一番大きく下がった期間: 含み損を入れると {d_(mid['w1'])}（{pct(mid['mtm'])}）、確定した損益だけだと {d_(mid['w2'])}（{pct(mid['real'])}）。\n")
        w("## 売買の内訳（50通りの中央値、11.7年の合計）\n")
        w(f"- 実際に買えた売買: {med('n'):.0f}回（年{med('n') / yrs:.0f}回）")
        w(f"- そのうち損で終わった売買: {med('loss'):.0f}回（年{med('loss') / yrs:.0f}回）")
        w(f"- そのうち損切り（買値の約15%下）: {med('stop'):.0f}回（年{med('stop') / yrs:.1f}回）")
        w(f"- 損で終わった売買の損の合計のうち、損切りの分: {pct(med('stop_amt') / med('loss_amt'), 0)}")
        w("\n- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
        open(OUTDIR + "含み損と確定した損益の下落率.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
        print("書き出し", file=sys.stderr)
        return
    if a.stage in ("robust", "earn"):
        return robust(a.stage, data, base, build, port, ev, CUR, CONF1, days, is_hi, oos_lo, sim, TREND, REV, safe)
    if a.stage == "dd":
        # 銘柄の直近1年（252取引日）の最大下落率（合図の日まで。後知恵なし）
        def dd1y(t):
            c = data[t["sym"]]["c"]
            i = t["i0"] - 1
            pk, mx = 0.0, 0.0
            for k in range(max(0, i - 251), i + 1):
                pk = max(pk, c[k])
                mx = max(mx, 1 - c[k] / pk)
            return mx
        for t in base:
            t["dd"] = dd1y(t)
        des = sorted(t["dd"] for t in base if data[t["sym"]]["date"][t["i0"]] <= is_hi)
        q = lambda p_: des[int(len(des) * p_)]        # 区切りは設計期間の合図だけで決める（後知恵なし）
        t70, t80, med = q(0.7), q(0.8), q(0.5)

        def with_(fn):
            saved = [(t, t["prio"], t.get("w")) for t in base]
            try:
                for t in base:
                    fn(t)
                return build()
            finally:
                for t, pr, w_ in saved:
                    t["prio"] = pr
                    if w_ is None:
                        t.pop("w", None)
                    else:
                        t["w"] = w_
        L = []
        w = L.append
        w(f"---\ntype: backtest\ntitle: 銘柄の下落率で見送る・優先する・額を変える\ncreated: {dt.date.today()}\nscript: tools/backtest_retest.py --stage dd\n---\n")
        w("# 銘柄の直近1年の最大下落率で、見送る・優先する・額を変える\n")
        w("合図の日までの直近1年（252取引日）で、その銘柄が高値から一番下がった割合（最大下落率）を使う。区切りの値は設計期間（2015〜2021年）の合図だけで決めた"
          f"（中央値 {pct(med, 0)}、上位30%の境 {pct(t70, 0)}、上位20%の境 {pct(t80, 0)}）。土台は今のルール。判定は乱数3組（20通り・50通り×2）。\n")
        items = [
            (f"1. 下落率が上位20%（{pct(t80, 0)}以上）の合図を見送る", lambda: build(drop=lambda t: t["dd"] >= t80)),
            (f"1. 下落率が上位30%（{pct(t70, 0)}以上）の合図を見送る", lambda: build(drop=lambda t: t["dd"] >= t70)),
            ("1'. 押し目・急落の底だけ、上位20%を見送る", lambda: build(drop=lambda t: t["rule"] in REV and t["dd"] >= t80)),
            ("1'. 順張りだけ、上位20%を見送る", lambda: build(drop=lambda t: t["rule"] in TREND and t["dd"] >= t80)),
            ("2. 枠が足りない日は、下落率の小さい銘柄を先に買う", lambda: with_(lambda t: t.__setitem__("prio", t["dd"]))),
            ("2'. （比較）枠が足りない日は、下落率の大きい銘柄を先に買う", lambda: with_(lambda t: t.__setitem__("prio", -t["dd"]))),
            (f"3. 下落率が上位20%の銘柄は額を半分（12.5%）", lambda: with_(lambda t: t.__setitem__("w", 0.5 if t["dd"] >= t80 else 1.0))),
            (f"3. 下落率が上位30%の銘柄は額を3分の2（約17%）", lambda: with_(lambda t: t.__setitem__("w", 2 / 3 if t["dd"] >= t70 else 1.0))),
        ]
        screen_and_confirm("銘柄の下落率で見送る・優先する・額を変える", items, w)
        # 下落率ごとの1回の成績
        tr = build()
        by = {}
        for t0, t1 in zip(base, tr):
            b = "上位20%" if t0["dd"] >= t80 else "上位20〜30%" if t0["dd"] >= t70 else "中央値〜上位30%" if t0["dd"] >= med else "中央値より下"
            by.setdefault(b, []).append(t1["path"][t1["out"]] - 1)
        w("\n## 下落率ごとの1回の成績（全部の合図）\n")
        w("| 直近1年の最大下落率 | 件数 | 勝率 | 1回平均 | 15%以上の損の割合 |")
        w("|---|---|---|---|---|")
        for b in ("中央値より下", "中央値〜上位30%", "上位20〜30%", "上位20%"):
            r_ = by.get(b, [])
            if r_:
                w(f"| {b} | {len(r_)} | {pct(sum(1 for x in r_ if x > 0) / len(r_), 0)} | {pct(sum(r_) / len(r_), 2)} | {pct(sum(1 for x in r_ if x <= -0.15) / len(r_), 0)} |")
        w("\n- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
        open(OUTDIR + "銘柄の下落率で見送る・優先する.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
        print("書き出し", file=sys.stderr)
        return
    if a.stage in ("opt1", "opt2"):
        if not (a.keep_open and a.overlap):
            sys.exit("opt は --keep-open --overlap で動かす")
        return opt_stage(base, data, sim, days, ind, a.cache, int(a.stage[-1]))
    if a.stage == "audit":
        return audit_stage(base, data, sim, days, ind, a.cache, "fixed" if (a.keep_open and a.overlap) else "old")
    if a.stage == "parity":
        fns = {"V": (ctx["v2o"], ctx["ok10"]), "C": (ctx["CR"](10), ctx["ok_rot"]), "M": (bm2.E_base(2.0), ctx["ok_rot"]), "B": (bs.O_method3, ctx["ok_rot"])}
        return parity_stage(base, data, days, a.recdir, fns, members)
    if a.stage == "shock":
        return shock_stage(base, data, sim, days, ind, members, a.cache, a.watch87)
    if a.stage == "ddsize":
        return ddsize_stage(base, data, sim, days, ind, a.cache)
    if a.stage == "crashstops":
        if a.watch87:   # 実際の運用（2026-10-05〜）の再現（2026-10-15 ユーザーの指示）
            return crashstops_stage(base, data, sim, days, ind, a.cache, lo="2026-09-21", hi=days[-1], out="今回の売買の再現（87銘柄）.md",
                                    note="。**監視銘柄を今の87銘柄に固定（`--watch87`）**して、実際の運用（2026-10-05に開始）と同じ期間を再現した。毎朝のツールが空き枠に使うテーマの外の銘柄は入っていない")
        return crashstops_stage(base, data, sim, days, ind, a.cache)
    if a.stage == "themedrop":
        return themedrop_stage(base, data, sim, days, ind, members, a.cache)
    if a.stage == "stopfreq":
        return stopfreq_stage(base, data, sim, days, ind, a.cache)
    if a.stage == "actual":
        return actual_stage(base, data, sim, port, days, ind, a.watch87, a.cache)
    if a.stage == "stopcheck":
        return stopcheck_stage(base, data, sim, port, days, a.cache)
    if a.stage == "replay":
        return replay_stage(base, data, build, ind, days)
    if a.stage == "halfadd":
        return halfadd_stage(base, data, build, port, days)
    if a.stage == "theme":
        return theme_stage(base, data, build, ind, days, a.cache)
    if a.stage == "ideas":
        return ideas_stage(cur_tr, base, data, build, ind, days, is_hi, oos_lo, ctx, G, from_gen, a.cache)
    if a.stage == "hotyear":
        return hotyear_stage(base, data, build, port, days)
    if a.stage == "hot":
        return hot_stage(base, data, build, ev, rec, days)
    if a.stage == "premium":
        return premium_stage(cur_tr, base, data, ind, days, is_hi, oos_lo)
    if a.stage == "swap":
        return swap_stage(cur_tr, base, data, build, ind, days, is_hi, oos_lo)
    if a.stage == "slope3":
        return slope3_stage(base, data, build, port, days)
    if a.stage == "slope2":
        return slope2_stage(base, data, build, port, ev, screen_and_confirm, days)
    if a.stage == "slope":
        return slope_stage(cur_tr, base, data, build, screen_and_confirm, is_hi)
    if a.stage == "prio":
        return prio_stage(build, screen_and_confirm)
    if a.stage == "recover":
        return recover_stage(cur_tr)
    if a.stage == "pullback":
        return pullback_stage(cur_tr, base, data, build, screen_and_confirm, rec, idx)
    if a.stage == "exits":
        return exits_stage(cur_tr)
    if a.stage == "pivot":
        return pivot_stage(cur_tr, base, data, build, screen_and_confirm)
    if a.stage == "rsi":
        return rsi_stage(cur_tr, base, data, build, ev, CUR, screen_and_confirm, TREND, REV)
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


def swap_port(trs, seed, lo, hi, ind, days, prem=None, th=0.0, stats=None, curve=None, pick="gain"):
    """port と同じ資金の計算に、乗り換えを足したもの。枠が埋まっている日に prem(t) の合図が出たら、含み益が th より大きい保有のうち
    含み益が一番大きいものを、その日の寄り付き（前日の終値で近似、片道の手数料込み）で売って、その合図を買う"""
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
            h["vp"] = h["v"]
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
                if not (prem and prem(t)):
                    continue
                if pick == "gain":   # 含み益が th より大きい保有のうち、一番大きいもの
                    gain = [h for h in held if h["vp"] / h["v0"] - 1 > th]
                    if not gain:
                        continue
                    h = max(gain, key=lambda h: h["vp"] / h["v0"])
                else:                # 含み損の保有のうち、一番損の大きいもの（弱っている保有を売る）
                    gain = [h for h in held if h["vp"] / h["v0"] - 1 < -th]
                    if not gain:
                        continue
                    h = min(gain, key=lambda h: h["vp"] / h["v0"])
                cash += h["size"] * h["vp"] * (1 - COST)
                held.remove(h)
                if stats is not None:
                    stats.append(h["vp"] / h["v0"] - 1)
            if sum(1 for h in held if ind.get(h["t"]["sym"]) == ind.get(t["sym"])) >= 2:
                continue
            size = min(eq / SLOTS * t.get("w", 1.0), cash)
            if size <= 0:
                break
            cash -= size
            v0 = t["path"].get(d, 1.0)
            if t["out"] == d:
                cash += size * v0
                continue
            held.append({"t": t, "size": size, "v": v0, "vp": v0, "v0": 1.0})
        eq = cash + sum(h["size"] * h["v"] for h in held)
        peak = max(peak, eq)
        mdd = max(mdd, 1 - eq / peak)
        if curve is not None:
            curve.append(eq)
    yrs = (dt.date.fromisoformat(dd[-1]) - dt.date.fromisoformat(dd[0])).days / 365.25
    return eq ** (1 / yrs) - 1, mdd


def ideas_stage(cur_tr, base, data, build, ind, days, is_hi, oos_lo, ctx, G, from_gen, cache):
    """効率を上げる案（2026-10-10 ユーザーの指示）: ①待っている現金をQQQに置く ②QQQの短期の逆張り（待っている現金で）
    ③決算後のドリフト（空いた枠で買う新しいルール）。今の運用（50日線の傾きが小さい順・2倍ETF込み）を土台に、資金全体で比べる"""
    import json
    from backtest_lib import load_prices
    sma = lambda c, j, n: sum(c[j - n + 1:j + 1]) / n
    def s50(sym, j):
        c = data[sym]["c"]
        return sma(c, j, 50) / sma(c, j - 20, 50) - 1 if j >= 70 else 0.0
    # ③ 決算後のドリフト: 決算の反応の日（決算日かその翌日）に、寄り付きが前日の終値より5%以上高く、陽線で、出来高が50日平均の2倍以上 → 翌日の寄り付きで買う。
    #    手じまいは引けで50日線割れ・損切り15%・最長40取引日
    earn = json.load(open(os.path.join(cache, "earnings.json"), encoding="utf-8"))
    edays = {sym: {x[0] for x in v} for sym, v in earn.items()}
    def E_pead(i, s):
        sym = s.get("_sym")
        ed = edays.get(sym)
        if not ed or i < 1:
            return None
        if s["date"][i] not in ed and s["date"][i - 1] not in ed:
            return None
        gap = s["o"][i] / s["c"][i - 1] - 1
        v50 = s["vol50"][i - 1] if s.get("vol50") else None
        if gap >= 0.05 and s["c"][i] >= s["o"][i] and v50 and s["v"][i] >= 2 * v50:
            return -gap
        return None
    for sym, s in data.items():
        s["_sym"] = sym
    pead = from_gen(G(E_pead, ctx["below50"], ctx["ok_rot"], STOP, 40), "E", prio=1)
    print("決算後のドリフトの合図", len(pead), file=sys.stderr)
    bmap = {(data[t["sym"]]["date"][t["i0"]], t["sym"], t["rule"]): t for t in base + pead}
    def prio(trs):
        out = []
        for t in trs:
            b = bmap.get((t["in"], t["sym"], t["rule"]))
            v = s50(t["sym"], b["i0"] - 1) if b else 0.0
            out.append({**t, "prio": (1 if t["rule"] == "E" else 0, v)})
        return out
    tab = json.load(open(os.path.join(os.path.dirname(OUTDIR.rstrip("/")), "2倍ETFの対応表.json"), encoding="utf-8"))
    drag = {u: -x["drag"] for u, x in tab.items() if isinstance(x, dict) and "drag" in x}
    HAS = {u for u, d in drag.items() if d < 0.15}
    def to2x(trs):
        out = []
        for t in trs:
            if t["sym"] not in HAS:
                out.append(t)
                continue
            fee = drag[t["sym"]] / 252
            e, prev, pv = 1 - COST, 1 - COST, {}
            for d in sorted(t["path"]):
                g_ = t["path"][d]
                e = max(0.0, e * (1 + 2 * (g_ / prev - 1)) * (1 - fee))
                prev = g_
                pv[d] = e
            out.append({**t, "path": pv})
        return out
    tool = to2x(prio(build()))
    tool_e = to2x(prio(build(add=pead)))
    # QQQの日ごとの値動き（配当込み）と、短期の逆張りの合図（引けで RSI(2)≦10 かつ 200日線より上 → 翌日から持つ、引けで5日線より上になったら翌日から持たない）
    q = load_prices(cache, "QQQ")
    qc, qd = q["c"], q["date"]
    qret = {qd[k]: qc[k] / qc[k - 1] - 1 for k in range(1, len(qc))}
    r2 = rsi_wilder(qc, 2)
    hold, on = {}, False
    for k in range(200, len(qc) - 1):
        if not on and r2[k] is not None and r2[k] <= 10 and qc[k] > sma(qc, k, 200):
            on = True
        elif on and qc[k] > sma(qc, k, 5):
            on = False
        hold[qd[k + 1]] = on
    mr_days = sum(1 for d in days if hold.get(d))
    def ret_q(lev, only_signal):
        r = {}
        for d in days:
            x = qret.get(d, 0.0)
            if only_signal and not hold.get(d):
                x = 0.0
            r[d] = (lev * x - (0.0095 / 252 if lev == 2 else 0.0)) if (not only_signal or hold.get(d)) else 0.0
        return r
    R_qqq, R_mr, R_mr2 = ret_q(1, False), ret_q(1, True), ret_q(2, True)
    def sim(trs, seed, lo, hi, cret=None):
        dd = [d for d in days if lo <= d <= hi]
        by_in = {}
        for t in trs:
            if lo <= t["in"] and t["out"] <= hi:
                by_in.setdefault(t["in"], []).append(t)
        rnd = random.Random(seed)
        cash, held, peak, mdd, eq = 1.0, [], 1.0, 0.0, 1.0
        for d in dd:
            if cret:
                cash *= 1 + cret.get(d, 0.0)
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
    forms = [("新分析ツールだけ（待っている現金は現金のまま＝今）", tool, None),
             ("① 待っている現金をQQQに置く", tool, R_qqq),
             ("② 待っている現金で、QQQの短期の逆張り（合図のときだけQQQ）", tool, R_mr),
             ("② 同じ・2倍（QLD相当）", tool, R_mr2),
             ("③ 決算後のドリフトを、空いた枠で買う新しいルールとして足す", tool_e, None),
             ("③＋① 決算後のドリフト＋待っている現金をQQQ", tool_e, R_qqq),
             ("③＋② 決算後のドリフト＋QQQの短期の逆張り", tool_e, R_mr)]
    med = lambda xs: sorted(xs)[len(xs) // 2]
    L = []
    w = L.append
    w(f"---\ntype: backtest\ntitle: 効率を上げる案（QQQ・指数の逆張り・決算後のドリフト）\ncreated: {dt.date.today()}\nscript: tools/backtest_retest.py --stage ideas\n---\n")
    w("# 効率を上げる案: ①待っている現金をQQQ ②QQQの短期の逆張り ③決算後のドリフト\n")
    w("2026-10-10、ユーザーの指示。土台は今の運用（新分析ツール、同じ日の候補は50日線の傾きが小さい順、目減り年15%未満の2倍ETFがある銘柄は2倍ETF、4銘柄・1銘柄25%）。"
      "後知恵なしの監視銘柄、2015年〜、片道0.1%込み、**税は引かない**（恩株ツールの記録は税引き後なので数字を直接は比べない）。乱数50通り×2組の中央値。\n")
    w(f"- ② QQQの短期の逆張り: 引けで RSI(2)≦10 かつ 200日線より上なら翌日から持ち、引けで5日線より上になったら翌日から持たない（コナーズの形）。持つ日は{mr_days}日（全体の{mr_days / len(days) * 100:.0f}%）。")
    pe = [t["path"][t["out"]] - 1 for t in build(add=pead) if t["rule"] == "E"]
    if pe:
        w(f"- ③ 決算後のドリフト: 決算の反応の日に寄り付きが+5%以上の窓・陽線・出来高2倍 → 翌日の寄り付きで買う。手じまいは引けで50日線割れ・損切り15%・最長40取引日。"
          f"合図 {len(pe)}回（年{len(pe) / 11.7:.0f}回）、勝率 {pct(sum(1 for x in pe if x > 0) / len(pe), 0)}、1回平均 {pct(sum(pe) / len(pe), 2)}（株、1回ごと）。今の4つのルールの候補より後に買う（空いた枠だけ）。")
    w("")
    w("| 形 | 1組目 年率 | 最大下落率（含み損込み） | 2015〜2021年 | 2022年〜 | 2組目 年率 | 最大下落率 | 2015〜2021年 | 2022年〜 |")
    w("|---|---|---|---|---|---|---|---|---|")
    for nm, trs, cr in forms:
        cells = []
        for s0 in (5000, 7300):
            a_, m_, i_, o_ = [], [], [], []
            for k in range(50):
                g, m = sim(trs, s0 + k, days[0], days[-1], cr)
                a_.append(g); m_.append(m)
                i_.append(sim(trs, s0 + k, days[0], is_hi, cr)[0])
                o_.append(sim(trs, s0 + k, oos_lo, days[-1], cr)[0])
            cells += [pct(med(a_)), pct(med(m_)), pct(med(i_)), pct(med(o_))]
        w(f"| {nm} | " + " | ".join(cells) + " |")
        print(nm, cells, file=sys.stderr)
    w("\n- QQQの売買のコストと、QQQを売って株を買うときのずれは入れていない（毎日の値動きをそのまま現金に掛けた近似）。2倍（QLD相当）は2倍の値動きから年0.95%の経費を引いた。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(OUTDIR, exist_ok=True)
    open(OUTDIR + "効率を上げる案_QQQ・指数の逆張り・決算後のドリフト.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("書き出し", file=sys.stderr)


def hotyear_stage(base, data, build, port, days):
    """過熱した順張りの合図を見送る形の、年ごとの成績（2026-10-10 ユーザーの指示）。乱数50通り（5000〜5049）の中央値"""
    sma = lambda c, j, n: sum(c[j - n + 1:j + 1]) / n
    rsis = {}
    def hot(t):
        s, j = data[t["sym"]], t["i0"] - 1
        if t["sym"] not in rsis:
            rsis[t["sym"]] = rsi_wilder(s["c"], 14)
        r = rsis[t["sym"]][j]
        return t["rule"] in ("V", "M") and s["bb_up"][j] is not None and s["c"][j] > s["bb_up"][j] and r is not None and r > 70
    def s50(sym, j):
        c = data[sym]["c"]
        return sma(c, j, 50) / sma(c, j - 20, 50) - 1 if j >= 70 else 0.0
    bmap = {(data[t["sym"]]["date"][t["i0"]], t["sym"], t["rule"]): t for t in base}
    prio = lambda trs: [{**t, "prio": s50(t["sym"], bmap[(t["in"], t["sym"], t["rule"])]["i0"] - 1)} for t in trs]
    hot_ids = {id(t) for t in base if hot(t)}
    forms = [("今のルール", prio(build())), ("過熱した合図は見送る", prio(build(drop=lambda t: id(t) in hot_ids)))]
    yrs = sorted({d[:4] for d in days})
    med = lambda xs: sorted(xs)[len(xs) // 2]
    rows = {}
    for nm, trs in forms:
        per = {y: [] for y in yrs}
        for k in range(50):
            curve = []
            port(trs, 5000 + k, days[0], days[-1], curve=curve)
            ends = {}
            for d, e in zip(days, curve):
                ends[d[:4]] = e
            prev = 1.0
            for y in yrs:
                if y in ends:
                    per[y].append(ends[y] / prev - 1)
                    prev = ends[y]
        rows[nm] = {y: med(v) for y, v in per.items() if v}
    nh = {y: sum(1 for t in base if id(t) in hot_ids and data[t["sym"]]["date"][t["i0"]][:4] == y) for y in yrs}
    L = []
    w = L.append
    w(f"---\ntype: backtest\ntitle: 過熱した順張りの合図を見送る形の年ごとの成績\ncreated: {dt.date.today()}\nscript: tools/backtest_retest.py --stage hotyear\n---\n")
    w("# 過熱した順張りの合図（+2σより上かつRSI(14)>70）を見送る形の、年ごとの成績\n")
    w("今のルール（同じ日の候補は50日線の傾きが小さい順）と比べる。株だけ、4銘柄・1銘柄25%、乱数50通りの中央値。2026年は10月まで。\n")
    w("| 年 | 今のルール | 過熱した合図は見送る | 差 | 過熱した合図の数 |")
    w("|---|---|---|---|---|")
    better = 0
    for y in yrs:
        a, b = rows["今のルール"].get(y), rows["過熱した合図は見送る"].get(y)
        if a is None or b is None:
            continue
        better += b > a
        w(f"| {y} | {pct(a, 0)} | {pct(b, 0)} | {(b - a) * 100:+.0f}ポイント | {nh[y]} |")
    w(f"\n- 見送る方が良かった年: {better} / {len(yrs)}")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(OUTDIR, exist_ok=True)
    open(OUTDIR + "過熱した順張りの合図を見送る形の年ごとの成績.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("書き出し", file=sys.stderr)


def hot_stage(base, data, build, ev, rec, days):
    """順張り（新高値V2・ミネルヴィニ）で、合図の日に終値が+2σより上かつRSI(14)が70超え（過熱）のとき、見送る・数日待つ・中心線まで待つ（2026-10-10 ユーザーの指示）。
    比べる元は今のルール（同じ日の候補は50日線の傾きが小さい順）"""
    sma = lambda c, j, n: sum(c[j - n + 1:j + 1]) / n
    rsis = {}
    def rsi14(sym, j):
        if sym not in rsis:
            rsis[sym] = rsi_wilder(data[sym]["c"], 14)
        return rsis[sym][j]
    def s50(sym, j):
        c = data[sym]["c"]
        return sma(c, j, 50) / sma(c, j - 20, 50) - 1 if j >= 70 else 0.0
    def hot(t):
        s, j = data[t["sym"]], t["i0"] - 1
        r = rsi14(t["sym"], j)
        return t["rule"] in ("V", "M") and s["bb_up"][j] is not None and s["c"][j] > s["bb_up"][j] and r is not None and r > 70
    def exit_from(s, k, px):
        c, floor = s["c"], px * (1 - STOP)
        for jj in range(k, len(c) - 1):
            if c[jj] <= floor or (s["ma50"][jj] is not None and c[jj] < s["ma50"][jj]):
                return jj + 1
        return None
    hots = [t for t in base if hot(t)]
    def delayed(n):
        out = []
        for t in hots:
            s, sym, i0 = data[t["sym"]], t["sym"], t["i0"]
            k = i0 + n
            if k >= len(s["c"]) - 1:
                continue
            j = i0 - 1
            lvl = max(s["c"][max(0, j - 20):j])   # 抜けた水準（合図の日の直前20日の最高値（終値））
            if s["c"][k - 1] < lvl:              # 待つ間にこの水準より下に戻ったら見送る
                continue
            px = s["o"][k]
            x = exit_from(s, k, px)
            if x:
                out.append({**rec(sym, k, x, px, s["o"][x], t["rule"]), "prio": s50(sym, j), "add": True})
        return out
    def to_mid(days_):
        out = []
        for t in hots:
            s, sym, i0 = data[t["sym"]], t["sym"], t["i0"]
            k = next((k for k in range(i0, min(len(s["c"]) - 1, i0 + days_)) if s["bb_mid"][k - 1] and s["l"][k] <= s["bb_mid"][k - 1]), None)
            if k is None:
                continue
            px = min(s["o"][k], s["bb_mid"][k - 1])
            x = exit_from(s, k, px)
            if x:
                out.append({**rec(sym, k, x, px, s["o"][x], t["rule"]), "prio": s50(sym, i0 - 1), "add": True})
        return out
    bmap = {(data[t["sym"]]["date"][t["i0"]], t["sym"], t["rule"]): t for t in base}
    def prio(trs):
        out = []
        for t in trs:
            b = bmap.get((t["in"], t["sym"], t["rule"]))
            out.append({**t, "prio": s50(t["sym"], b["i0"] - 1)} if b and not t.get("add") else t)
        return out
    hot_ids = {id(t) for t in hots}
    drop_hot = lambda t: id(t) in hot_ids
    forms = [("今のルール（50日線の傾きが小さい順）", lambda: prio(build()))]
    forms.append(("1. 過熱した合図は見送る", lambda: prio(build(drop=drop_hot))))
    for n in (1, 2, 3):
        forms.append((f"2. 過熱した合図は{n}日待ち、抜けた水準より上なら{n}日後の寄り付きで買う", (lambda n=n: prio(build(drop=drop_hot, add=delayed(n))))))
    for d_ in (5, 10):
        forms.append((f"3. 過熱した合図は、{d_}日以内に20日線（バンドの中心）まで下がったら指値で買う", (lambda d_=d_: prio(build(drop=drop_hot, add=to_mid(d_))))))
    L = []
    w = L.append
    nV = sum(1 for t in hots if t["rule"] == "V"); nM = len(hots) - nV
    allT = sum(1 for t in base if t["rule"] in ("V", "M"))
    w(f"---\ntype: backtest\ntitle: 過熱した順張りの合図を見送る・待つ\ncreated: {dt.date.today()}\nscript: tools/backtest_retest.py --stage hot\n---\n")
    w("# 順張りの合図が過熱している（+2σより上かつRSI(14)が70超え）とき、見送る・数日待つ・中心線まで待つ\n")
    w(f"2026-10-10、ユーザーの指示（保有4銘柄がどれも+2σ付近で買い、2つは20日線まで下げたことから）。過熱した合図: 合図の日の終値がボリンジャーの+2σより上、かつRSI(14)が70超え。"
      f"順張りの合図{allT}件のうち{len(hots)}件（新高値V2 {nV}件・ミネルヴィニ {nM}件）。押し目・急落の底はそのまま。"
      "比べる元は今のルール（同じ日の候補は50日線の傾きが小さい順）。後知恵なしの監視銘柄、2015年〜、4銘柄・1銘柄25%、株だけ、片道0.1%込み。乱数20通り・50通り×2組の中央値。\n")
    sets = ((1000, 20), (5000, 50), (7300, 50))
    res = {}
    for nm, fn in forms:
        trs = fn()
        res[nm] = [ev(trs, sd) for sd in sets]
        print(nm, [round(e["all"], 3) for e in res[nm]], file=sys.stderr)
    b0 = res[forms[0][0]]
    w("| 形 | 年率（3組） | 最大下落率（組2） | 2015〜2021年（3組） | 2022年〜（3組） | 3組とも両方の期間で今のルールを上回ったか |")
    w("|---|---|---|---|---|---|")
    for nm, _ in forms:
        r = res[nm]
        ok = all(r[k]["is"] > b0[k]["is"] and r[k]["oos"] > b0[k]["oos"] for k in range(3)) if nm != forms[0][0] else None
        w(f"| {nm} | {'／'.join(pct(e['all']) for e in r)} | {pct(r[1]['mdd'])} | {'／'.join(pct(e['is']) for e in r)} | {'／'.join(pct(e['oos']) for e in r)} | {'—' if ok is None else ('**確か**' if ok else 'いいえ')} |")
    w("\n- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(OUTDIR, exist_ok=True)
    open(OUTDIR + "過熱した順張りの合図を見送る・待つ.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("書き出し", file=sys.stderr)


def side_sim(trs, lo, hi, days, slots, cap=None, tool_curve=None, tool_cap=1.0, rate=0.0):
    """良い合図だけを買う別の枠。cap があれば、その現金で同時に slots 銘柄まで（1銘柄＝その枠の時価÷slots）。
    cap が None なら信用取引: 全体（ツール＋この枠の損益）の時価÷4 を借りて買い、年 rate の金利を日割りで払う。日ごとの価値（損益の累計）を返す"""
    dd = [d for d in days if lo <= d <= hi]
    by_in = {}
    for t in trs:
        if lo <= t["in"] and t["out"] <= hi:
            by_in.setdefault(t["in"], []).append(t)
    cash = cap if cap is not None else 0.0
    held, out = [], []
    for k, d in enumerate(dd):
        still = []
        for h in held:
            v = h["t"]["path"].get(d)
            if v is not None:
                h["v"] = v
            if cap is None:
                cash -= h["size"] * rate / 252
            if h["t"]["out"] == d:
                cash += h["size"] * (h["v"] - (0 if cap is not None else 1))
            else:
                still.append(h)
        held = still
        for t in sorted(by_in.get(d, []), key=lambda t: t["prio"]):
            if len(held) >= slots or any(h["t"]["sym"] == t["sym"] for h in held):
                continue
            if cap is not None:
                eq = cash + sum(h["size"] * h["v"] for h in held)
                size = min(eq / slots, cash)
                if size <= 0:
                    break
                cash -= size
            else:
                tot = tool_cap * tool_curve[k] + cash + sum(h["size"] * (h["v"] - 1) for h in held)
                size = tot / 4
            v0 = t["path"].get(d, 1.0)
            if t["out"] == d:
                cash += size * (v0 - (0 if cap is not None else 1))
                continue
            held.append({"t": t, "size": size, "v": v0})
        out.append(cash + sum(h["size"] * (h["v"] - (0 if cap is not None else 1)) for h in held))
    return out


def premium_stage(cur_tr, base, data, ind, days, is_hi, oos_lo):
    """良い合図（急落の底のうち50日線の傾きが小さい20%）をうまく使う案1〜4と、余剰の現金を全部ツールに入れる形を、同じ資金（18,000ドル＝1.5）で比べる（2026-10-10 ユーザーの指示）"""
    import json
    sma = lambda c, j, n: sum(c[j - n + 1:j + 1]) / n
    def s50(b):
        c, j = data[b["sym"]]["c"], b["i0"] - 1
        return sma(c, j, 50) / sma(c, j - 20, 50) - 1 if j >= 70 else 0.0
    bmap = {(data[t["sym"]]["date"][t["i0"]], t["sym"], t["rule"]): t for t in base}
    B = lambda t: bmap[(t["in"], t["sym"], t["rule"])]
    trs = [{**t, "prio": s50(B(t))} for t in cur_tr]
    cs = sorted(t["prio"] for t in trs if t["rule"] == "C" and t["in"] <= is_hi)
    c20 = cs[len(cs) // 5]   # 境目は設計期間（2015〜2021年）の急落の底の下位20%
    prem = lambda t: t["rule"] == "C" and t["prio"] <= c20
    ptrs = [t for t in trs if prem(t)]
    tab = json.load(open(os.path.join(os.path.dirname(OUTDIR.rstrip("/")), "2倍ETFの対応表.json"), encoding="utf-8"))
    drag = {u: -x["drag"] for u, x in tab.items() if isinstance(x, dict) and "drag" in x}
    HAS = {u for u, d in drag.items() if d < 0.15}
    def to2x(xs, only=None):
        out = []
        for t in xs:
            if t["sym"] not in HAS or (only and not only(t)):
                out.append(t)
                continue
            fee = drag[t["sym"]] / 252
            e, prev, pv = 1 - COST, 1 - COST, {}
            for d in sorted(t["path"]):
                g_ = t["path"][d]
                e = max(0.0, e * (1 + 2 * (g_ / prev - 1)) * (1 - fee))
                prev = g_
                pv[d] = e
            out.append({**t, "path": pv})
        return out
    trs2, ptrs2 = to2x(trs), to2x(ptrs)
    TOT = 1.5   # 18,000ドル（ツール12,000ドル＝1.0＋余剰6,000ドル＝0.5）
    RATE = 0.07  # 信用取引の金利（年。仮定）
    def total(seed, lo, hi, form, etf):
        dd = [d for d in days if lo <= d <= hi]
        tt = trs2 if etf else trs
        pt = ptrs2 if (etf or form == "1x2") else ptrs
        tc = []
        if form == "all":         # 全部（1.5）をツールに
            swap_port(tt, seed, lo, hi, ind, days, curve=tc)
            tot = [TOT * x for x in tc]
        elif form == "big":       # 全部ツール、良い合図だけ1銘柄の金額を1.5倍
            swap_port([{**t, "w": 1.5} if prem(t) else t for t in tt], seed, lo, hi, ind, days, curve=tc)
            tot = [TOT * x for x in tc]
        elif form == "swaploss":  # 全部ツール、枠が埋まっていれば含み損が一番大きい保有を売って乗り換える
            swap_port(tt, seed, lo, hi, ind, days, prem=prem, th=0.0, curve=tc, pick="loss")
            tot = [TOT * x for x in tc]
        elif form == "margin":    # 全部ツール、良い合図は信用取引で別に買う
            swap_port(tt, seed, lo, hi, ind, days, curve=tc)
            side = side_sim(pt, lo, hi, days, 1, None, tc, TOT, RATE)
            tot = [TOT * x + y for x, y in zip(tc, side)]
        else:                     # ツールは1.0、余剰の0.5は idle（何もしない）か、良い合図専用の枠
            swap_port(tt, seed, lo, hi, ind, days, curve=tc)
            side = [0.5] * len(dd) if form == "idle" else side_sim(pt, lo, hi, days, 2, 0.5)
            tot = [x + y for x, y in zip(tc, side)]
        yrs = (dt.date.fromisoformat(dd[-1]) - dt.date.fromisoformat(dd[0])).days / 365.25
        pk, m = 0.0, 0.0
        for x in tot:
            pk = max(pk, x)
            m = max(m, 1 - x / pk)
        return (tot[-1] / TOT) ** (1 / yrs) - 1, m
    forms = [("余剰の6,000ドルは現金のまま（今の形）", "idle"),
             ("全部（18,000ドル）をツールに入れる", "all"),
             ("案1: 余剰の6,000ドルを良い合図専用の枠に（同時に2銘柄、株）", "side"),
             ("案1＋2: 専用の枠を2倍ETFで（2倍ETFがある銘柄）", "1x2"),
             ("案2: 全部ツールに入れ、良い合図だけ1銘柄の金額を1.5倍", "big"),
             ("案3: 全部ツールに入れ、良い合図は信用取引で別に買う（金利 年7%と仮定）", "margin"),
             ("案4: 全部ツールに入れ、枠が埋まっていれば含み損が一番大きい保有を売って乗り換える", "swaploss")]
    med = lambda xs: sorted(xs)[len(xs) // 2]
    L = []
    w = L.append
    w(f"---\ntype: backtest\ntitle: 良い合図をうまく使う案と余剰の現金\ncreated: {dt.date.today()}\nscript: tools/backtest_retest.py --stage premium\n---\n")
    w("# 良い合図（急落の底のうち50日線の傾きが小さい20%）をうまく使う案と、余剰の現金の使い方\n")
    w(f"2026-10-10、ユーザーの指示。資金は全部で18,000ドル（ツール12,000ドル＋余剰6,000ドル）として、資金全体の年率・最大下落率（含み損込み）で比べる。"
      f"良い合図の境目は、設計期間の急落の底の合図のうち50日線の傾きの下位20%（{pct(c20, 1)}以下）。年に約{len(ptrs) / 11.7:.0f}回。"
      "ツールは今のルール（同じ日の候補は50日線の傾きが小さい順、4銘柄・1銘柄25%）。後知恵なしの監視銘柄、2015年〜、片道0.1%込み。乱数50通り×2組の中央値。\n")
    for etf in (False, True):
        w(f"## {'2倍ETF込み（今の運用）' if etf else '株だけ'}\n")
        w("| 形 | 1組目 年率 | 最大下落率 | 2015〜2021年 | 2022年〜 | 2組目 年率 | 最大下落率 | 2015〜2021年 | 2022年〜 |")
        w("|---|---|---|---|---|---|---|---|---|")
        for nm, fm in forms:
            if etf and fm == "1x2":
                continue
            cells = []
            for s0 in (5000, 7300):
                a_, m_, i_, o_ = [], [], [], []
                for k in range(50):
                    g, m = total(s0 + k, days[0], days[-1], fm, etf)
                    a_.append(g); m_.append(m)
                    i_.append(total(s0 + k, days[0], is_hi, fm, etf)[0])
                    o_.append(total(s0 + k, oos_lo, days[-1], fm, etf)[0])
                cells += [pct(med(a_)), pct(med(m_)), pct(med(i_)), pct(med(o_))]
            w(f"| {nm} | " + " | ".join(cells) + " |")
            print(nm, etf, cells, file=sys.stderr)
        w("")
    w("- 案1の専用の枠: 余剰の6,000ドルで同時に2銘柄まで（1銘柄＝その枠の時価÷2）。良い合図は年に十数回で、保有は4取引日ほどなので、ほとんどの日は現金。")
    w("- 案3の信用取引: 全体の時価÷4 を借りて買い、金利は年7%を日割りで払うと仮定（ムームー証券の実際の金利は要確認）。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(OUTDIR, exist_ok=True)
    open(OUTDIR + "良い合図をうまく使う案と余剰の現金.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("書き出し", file=sys.stderr)


def swap_stage(cur_tr, base, data, build, ind, days, is_hi, oos_lo):
    """出る回数は少ないが勝率が高く下落が小さい合図が出たら、含み益の保有を利確して乗り換えるか（2026-10-10 ユーザーの指示）"""
    sma = lambda c, j, n: sum(c[j - n + 1:j + 1]) / n
    def s50(b):
        c, j = data[b["sym"]]["c"], b["i0"] - 1
        return sma(c, j, 50) / sma(c, j - 20, 50) - 1 if j >= 70 else 0.0
    bmap = {(data[t["sym"]]["date"][t["i0"]], t["sym"], t["rule"]): t for t in base}
    B = lambda t: bmap[(t["in"], t["sym"], t["rule"])]
    rs = lambda t: data[t["sym"]]["rs"][B(t)["i0"] - 1] or 0
    yrs = 11.7
    groups = {
        "新高値V2（全部）": lambda t: t["rule"] == "V",
        "ミネルヴィニ（全部）": lambda t: t["rule"] == "M",
        "押し目（全部）": lambda t: t["rule"] == "B",
        "押し目・RS≧80": lambda t: t["rule"] == "B" and rs(t) >= 80,
        "押し目・RS≧90": lambda t: t["rule"] == "B" and rs(t) >= 90,
        "急落の底（全部）": lambda t: t["rule"] == "C",
        "急落の底・RS≧80": lambda t: t["rule"] == "C" and rs(t) >= 80,
        "急落の底・50日線の傾きが小さい20%": None,
    }
    cs = sorted(s50(B(t)) for t in cur_tr if t["rule"] == "C")
    c20 = cs[len(cs) // 5]
    groups["急落の底・50日線の傾きが小さい20%"] = lambda t: t["rule"] == "C" and s50(B(t)) <= c20
    L = []
    w = L.append
    w(f"---\ntype: backtest\ntitle: 良い合図が出たら含み益の保有を利確して乗り換える\ncreated: {dt.date.today()}\nscript: tools/backtest_retest.py --stage swap\n---\n")
    w("# 出る回数は少ないが勝率が高く下落が小さい合図が出たら、含み益の保有を利確して乗り換えるか\n")
    w("2026-10-10、ユーザーの指示。後知恵なしの監視銘柄、2015年〜、今のルール（同じ日の候補は50日線の傾きが小さい順）、4銘柄・1銘柄25%、株だけ、片道0.1%込み。\n")
    w("## 1. 合図の種類ごとの成績（全部の合図、1回ごと）\n")
    w("「保有中の一番深い下げ」は、買ってから売るまでの終値で一番下がった割合の平均。\n")
    w("| 合図 | 回数（年あたり） | 勝率 | 1回平均 | 保有中の一番深い下げ（平均） | 1回の最悪 | 保有日数（中央値、取引日） |")
    w("|---|---|---|---|---|---|---|")
    for nm, f in groups.items():
        ts = [t for t in cur_tr if f(t)]
        if not ts:
            continue
        r = [t["path"][t["out"]] - 1 for t in ts]
        mae = [min(v for d, v in t["path"].items() if d <= t["out"]) - 1 for t in ts]
        hold = sorted(len([d for d in t["path"] if d <= t["out"]]) for t in ts)
        w(f"| {nm} | {len(ts)}（年{len(ts) / yrs:.0f}回） | {pct(sum(1 for x in r if x > 0) / len(r), 0)} | {pct(sum(r) / len(r), 2)} | {pct(sum(mae) / len(mae), 1)} | {pct(min(r), 0)} | {hold[len(hold) // 2]}日 |")
    trs = [{**t, "prio": s50(B(t))} for t in cur_tr]
    w("\n## 2. 乗り換えを資金全体で試す（今のルールと比べる）\n")
    w("枠（4つ）が埋まっている日に、下の合図が出たら、含み益（前日の終値で、買値から）が条件を超える保有のうち一番大きいものを、その日の寄り付きで売り、その合図を買う。"
      "乗り換えの合図が出なければ今のルールと同じ。乱数50通り×2組の中央値。\n")
    w("| 乗り換える合図 | 利確する保有の条件 | 1組目 年率 | 最大下落率 | 設計 | 確認 | 2組目 年率 | 最大下落率 | 設計 | 確認 | 乗り換えの回数（年あたり）・売った保有の含み益の平均 |")
    w("|---|---|---|---|---|---|---|---|---|---|---|")
    med = lambda xs: sorted(xs)[len(xs) // 2]
    def run(prem, th):
        out = []
        for s0 in (5000, 7300):
            a_, m_, i_, o_ = [], [], [], []
            st = []
            for k in range(50):
                g, m = swap_port(trs, s0 + k, days[0], days[-1], ind, days, prem, th, st if s0 == 5000 else None)
                a_.append(g); m_.append(m)
                i_.append(swap_port(trs, s0 + k, days[0], is_hi, ind, days, prem, th)[0])
                o_.append(swap_port(trs, s0 + k, oos_lo, days[-1], ind, days, prem, th)[0])
            out.append((med(a_), med(m_), med(i_), med(o_), st))
        return out
    base_r = run(None, 0)
    def row(nm, cond, r):
        st = r[0][4]
        n = f"年{len(st) / 50 / yrs:.1f}回・{pct(sum(st) / len(st), 1)}" if st else "—"
        w(f"| {nm} | {cond} | {pct(r[0][0])} | {pct(r[0][1])} | {pct(r[0][2])} | {pct(r[0][3])} | {pct(r[1][0])} | {pct(r[1][1])} | {pct(r[1][2])} | {pct(r[1][3])} | {n} |")
    row("（乗り換えなし＝今のルール）", "—", base_r)
    for nm in ("急落の底（全部）", "急落の底・RS≧80", "急落の底・50日線の傾きが小さい20%", "押し目・RS≧90", "押し目・RS≧80"):
        for th in (0.0, 0.10):
            row(nm, f"含み益 {'+' + str(int(th * 100)) + '%超' if th else 'プラス'}", run(groups[nm], th))
    w("\n- 「設計」は2015〜2021年、「確認」は2022年〜。採用の目安は、今のルールより両方の期間で上回ること（2組とも）。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(OUTDIR, exist_ok=True)
    open(OUTDIR + "良い合図が出たら含み益の保有を利確して乗り換える.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("書き出し", file=sys.stderr)


def slope3_stage(base, data, build, port, days):
    """50日線の傾きが小さい順に買う形の、確定した損益だけの最大下落率（株だけ・2倍ETF込み）。2026-10-09 ユーザーの指示"""
    import json
    sma = lambda c, j, n: sum(c[j - n + 1:j + 1]) / n
    def s50(b):
        c, j = data[b["sym"]]["c"], b["i0"] - 1
        return sma(c, j, 50) / sma(c, j - 20, 50) - 1 if j >= 70 else 0.0
    bmap = {(data[t["sym"]]["date"][t["i0"]], t["sym"], t["rule"]): t for t in base}
    REV = ("B", "C")
    def with_prio(trs, key):
        return [{**t, "prio": key(bmap[(t["in"], t["sym"], t["rule"])])} for t in trs]
    tab = json.load(open(os.path.join(os.path.dirname(OUTDIR.rstrip("/")), "2倍ETFの対応表.json"), encoding="utf-8"))
    drag = {u: -x["drag"] for u, x in tab.items() if isinstance(x, dict) and "drag" in x}
    HAS = {u for u, d in drag.items() if d < 0.15}
    def to2x(trs):
        out = []
        for t in trs:
            if t["sym"] not in HAS:
                out.append(t)
                continue
            fee = drag[t["sym"]] / 252
            e, prev, pv = 1 - COST, 1 - COST, {}
            for d in sorted(t["path"]):
                g_ = t["path"][d]
                e = max(0.0, e * (1 + 2 * (g_ / prev - 1)) * (1 - fee))
                prev = g_
                pv[d] = e
            out.append({**t, "path": pv})
        return out
    forms = [("今のルール（ランダムな順）", lambda: build()),
             ("50日線の傾きが小さい順", lambda: with_prio(build(), s50)),
             ("押し目・急落の底を先に傾きが小さい順、順張りは後に傾きが大きい順（ユーザー案）",
              lambda: with_prio(build(), lambda b: (0, s50(b)) if b["rule"] in REV else (1, -s50(b))))]
    L = []
    w = L.append
    w(f"---\ntype: backtest\ntitle: 50日線の傾きが小さい順の確定した損益の下落率\ncreated: {dt.date.today()}\nscript: tools/backtest_retest.py --stage slope3\n---\n")
    w("# 50日線の傾きが小さい順に買う形の、確定した損益だけの最大下落率\n")
    w("確定した損益だけの下落率: 持っている株は買った額のまま数え、売って損益が確定したときだけ資金が増減するとした場合の、最高から一番下がった割合（実際に資産が減った大きさ）。"
      "含み損込み: 毎日の時価で数えた場合。乱数50通り（5000〜5049）。2015年〜、4銘柄・1銘柄25%、片道0.1%込み。\n")
    w("| 形 | 年率（中央値） | 含み損込みの最大下落率（中央値／最悪） | **確定した損益だけの最大下落率（中央値／最悪）** | 2015〜2021年 | 2022年〜 |")
    w("|---|---|---|---|---|---|")
    is_hi = max(d for d in days if d <= cb.IS_END)
    oos_lo = min(d for d in days if d >= cb.OOS_START)
    med = lambda xs: sorted(xs)[len(xs) // 2]
    for etf in (False, True):
        for nm, fn in forms:
            trs = fn()
            if etf:
                trs = to2x(trs)
            cg, mm, rm, ii, oo = [], [], [], [], []
            for k in range(50):
                rc = []
                g, m = port(trs, 5000 + k, days[0], days[-1], rcurve=rc)
                pk, r = 0.0, 0.0
                for x in rc:
                    pk = max(pk, x)
                    r = max(r, 1 - x / pk)
                cg.append(g); mm.append(m); rm.append(r)
                ii.append(port(trs, 5000 + k, days[0], is_hi)[0]); oo.append(port(trs, 5000 + k, oos_lo, days[-1])[0])
            w(f"| {nm}{'（2倍ETF込み）' if etf else '（株だけ）'} | {pct(med(cg))} | {pct(med(mm))}／{pct(max(mm))} | **{pct(med(rm))}／{pct(max(rm))}** | {pct(med(ii))} | {pct(med(oo))} |")
    w("\n- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(OUTDIR, exist_ok=True)
    open(OUTDIR + "50日線の傾きが小さい順の確定した損益の下落率.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("書き出し", file=sys.stderr)


def theme_stage(base, data, build, ind, days, cache):
    """保有が同じテーマ・セクターに固まったときの成績と、テーマ・セクターの上限を足す形（2026-10-12 ユーザーの指示）。
    今のルール（50日線の傾きが小さい順・2倍ETF込み・同じ業種2銘柄まで）が土台"""
    import json
    from backtest_caps import THEME
    u = json.load(open(os.path.join(cache, "universe.json")))
    ex = os.path.join(cache, "industry_extra.json")
    if os.path.exists(ex):
        u.update(json.load(open(ex)))
    sec = {s: (u.get(s) or {}).get("sector") for s in data}
    theme = {s: THEME.get(ind.get(s), ind.get(s)) for s in data}
    sma_ = lambda c, j, n: sum(c[j - n + 1:j + 1]) / n
    def s50(b):
        c, j = data[b["sym"]]["c"], b["i0"] - 1
        return sma_(c, j, 50) / sma_(c, j - 20, 50) - 1 if j >= 70 else 0.0
    bmap = {(data[t["sym"]]["date"][t["i0"]], t["sym"], t["rule"]): t for t in base}
    tab = json.load(open(os.path.join(os.path.dirname(OUTDIR.rstrip("/")), "2倍ETFの対応表.json"), encoding="utf-8"))
    drag = {s: -x["drag"] for s, x in tab.items() if isinstance(x, dict) and "drag" in x}
    HAS = {s for s, d in drag.items() if d < 0.15}
    def to2x(trs):
        out = []
        for t in trs:
            if t["sym"] not in HAS:
                out.append(t)
                continue
            fee = drag[t["sym"]] / 252
            e, prev, pv = 1 - COST, 1 - COST, {}
            for d in sorted(t["path"]):
                g_ = t["path"][d]
                e = max(0.0, e * (1 + 2 * (g_ / prev - 1)) * (1 - fee))
                prev = g_
                pv[d] = e
            out.append({**t, "path": pv})
        return out
    trs = to2x([{**t, "prio": s50(bmap[(t["in"], t["sym"], t["rule"])])} for t in build()])
    is_hi = max(d for d in days if d <= cb.IS_END)
    oos_lo = min(d for d in days if d >= cb.OOS_START)

    def port(seed, lo, hi, caps=(), buys=None, rcurve=None, ddinfo=None):
        """今の port と同じ（業種2銘柄まで）に caps=[(銘柄→まとまり, 上限)] を足したもの。
        buys: 買うたびに (同じセクターの数, 同じテーマの数, その売買の損益) を足す（数は買う銘柄を含む）"""
        dd = [d for d in days if lo <= d <= hi]
        by_in = {}
        for t in trs:
            if lo <= t["in"] and t["out"] <= hi:
                by_in.setdefault(t["in"], []).append(t)
        rnd = random.Random(seed)
        cash, held, peak, mdd, eq = 1.0, [], 1.0, 0.0, 1.0
        pk_d, best = None, None
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
                if any(sum(1 for h in held if g.get(h["t"]["sym"]) == g.get(t["sym"])) >= n for g, n in caps):
                    continue
                size = min(eq / SLOTS * t.get("w", 1.0), cash)
                if size <= 0:
                    break
                if buys is not None:
                    buys.append((1 + sum(1 for h in held if sec.get(h["t"]["sym"]) == sec.get(t["sym"])),
                                 1 + sum(1 for h in held if theme.get(h["t"]["sym"]) == theme.get(t["sym"])),
                                 t["path"][t["out"]] - 1))
                cash -= size
                v0 = t["path"].get(d, 1.0)
                if t["out"] == d:
                    cash += size * v0
                    continue
                held.append({"t": t, "size": size, "v": v0})
            eq = cash + sum(h["size"] * h["v"] for h in held)
            if eq > peak:
                peak, pk_d = eq, d
                pk_sec = max([sum(1 for x in held if sec.get(x["t"]["sym"]) == sec.get(h["t"]["sym"])) for h in held] or [0])
            if 1 - eq / peak > mdd:
                mdd = 1 - eq / peak
                best = (pk_d, d, pk_sec if pk_d else 0)
            if rcurve is not None:
                rcurve.append(cash + sum(h["size"] for h in held))
        if ddinfo is not None:
            ddinfo.append(best)
        yrs = (dt.date.fromisoformat(dd[-1]) - dt.date.fromisoformat(dd[0])).days / 365.25
        return eq ** (1 / yrs) - 1, mdd

    med = lambda xs: sorted(xs)[len(xs) // 2]
    L = []
    w = L.append
    w(f"---\ntype: backtest\ntitle: 同じテーマ・セクターに固まったとき\ncreated: {dt.date.today()}\nscript: tools/backtest_retest.py --stage theme\n---\n")
    w("# 保有が同じテーマ・セクターに固まったときの成績と、上限を足す形\n")
    w("2026-10-12、保有4銘柄（LITE・NVDA・HPE・AMD）がすべてAI・半導体関連で一緒に下げたのを受けて、ユーザーの指示で調べた。"
      "土台は今のルール（4銘柄・1銘柄25%、同じ業種2銘柄まで、50日線の傾きが小さい順、2倍ETFがある銘柄は2倍ETF〔実測の目減り〕、損切り15%）。"
      "後知恵なしの監視銘柄、2015年〜、片道0.1%込み。セクターはYahooの大きな分類（Technologyなど11種）、テーマは `backtest_caps.THEME`"
      "（半導体／製造装置／ハード・端末／通信機器・部品・計測／ソフト・ITサービス／ネット。それ以外は業種のまま）。\n")

    # 1. 固まったときの売買の成績（今のルール、乱数50通りの全部の売買）
    buys, ddi = [], []
    for k in range(50):
        port(5000 + k, days[0], days[-1], buys=buys, ddinfo=ddi)
    for no, name, col in (("1-1", "セクター", 0), ("1-2", "テーマ", 1)):
        w(f"\n## {no}. 買ったとき、同じ{name}の保有が何銘柄になったか（買う銘柄を含む）と、その売買の成績（今のルール、乱数50通りの全部の売買）\n")
        w("| 同じ" + name + "の数 | 売買の数（割合） | 勝率 | 1回平均（2倍ETFはETFの損益） | 1回の中央値 |")
        w("|---|---|---|---|---|")
        for n in (1, 2, 3, 4):
            xs = [b[2] for b in buys if b[col] == n]
            if not xs:
                continue
            w(f"| {n}銘柄 | {len(xs)}（{len(xs) / len(buys) * 100:.0f}%） | {sum(x > 0 for x in xs) / len(xs) * 100:.0f}% | {pct(sum(xs) / len(xs))} | {pct(med(xs))} |")
    w("\n## 2. 一番大きい下落（含み損込み）が始まった日に、同じセクターの保有が最も多くて何銘柄だったか（乱数50通り）\n")
    cnt = {}
    for b in ddi:
        if b:
            cnt[b[2]] = cnt.get(b[2], 0) + 1
    w("| 同じセクターの数 | 回数 |")
    w("|---|---|")
    for n in sorted(cnt):
        w(f"| {n}銘柄 | {cnt[n]} |")
    starts = {}
    for b in ddi:
        if b:
            starts[(b[0], b[1])] = starts.get((b[0], b[1]), 0) + 1
    top = sorted(starts.items(), key=lambda x: -x[1])[:3]
    w("\nよく出た下落の期間（始まり→底、乱数50通りのうちの回数）: " + "、".join(f"{a}→{b}（{n}回）" for (a, b), n in top) + "\n")

    # 3. 上限を足す形
    forms = [("今のルール（同じ業種2銘柄まで）", ()),
             ("＋同じテーマ2銘柄まで", ((theme, 2),)),
             ("＋同じテーマ3銘柄まで", ((theme, 3),)),
             ("＋同じセクター2銘柄まで", ((sec, 2),)),
             ("＋同じセクター3銘柄まで", ((sec, 3),))]
    w("\n## 3. テーマ・セクターの上限を足す形（乱数50通り×2組の中央値）\n")
    w("確定した損益だけの下落率: 持っている株は買った額のまま数え、売って損益が確定したときだけ資金が増減するとした場合。\n")
    w("| 形 | 組 | 年率 | 含み損込みの最大下落率（中央値／最悪） | 確定した損益だけの最大下落率（中央値／最悪） | 2015〜2021年 | 2022年〜 |")
    w("|---|---|---|---|---|---|---|")
    res = {}
    for nm, caps in forms:
        for s0 in (5000, 7300):
            cg, mm, rm, ii, oo = [], [], [], [], []
            for k in range(50):
                rc = []
                g, m = port(s0 + k, days[0], days[-1], caps, rcurve=rc)
                pk, r = 0.0, 0.0
                for x in rc:
                    pk = max(pk, x)
                    r = max(r, 1 - x / pk)
                cg.append(g); mm.append(m); rm.append(r)
                ii.append(port(s0 + k, days[0], is_hi, caps)[0]); oo.append(port(s0 + k, oos_lo, days[-1], caps)[0])
            res[(nm, s0)] = (med(ii), med(oo))
            w(f"| {nm} | {'1組目' if s0 == 5000 else '2組目'} | {pct(med(cg))} | {pct(med(mm))}／{pct(max(mm))} | {pct(med(rm))}／{pct(max(rm))} | {pct(med(ii))} | {pct(med(oo))} |")
            print(nm, s0, file=sys.stderr)
    w("\n両方の組で、2015〜2021年・2022年〜の両方とも今のルールを上回った形: " +
      ("、".join(nm for nm, _ in forms[1:] if all(res[(nm, s)][0] > res[(forms[0][0], s)][0] and res[(nm, s)][1] > res[(forms[0][0], s)][1] for s in (5000, 7300))) or "なし") + "\n")
    w("- 後知恵なしの監視銘柄は全業種から選ばれる。実際の監視銘柄（87銘柄）はAI・半導体のテーマに絞っているため、実際の運用ではこの表より同じテーマに固まりやすい。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(OUTDIR, exist_ok=True)
    open(OUTDIR + "同じテーマ・セクターに固まったとき.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("書き出し", file=sys.stderr)


def etf_up_days(cache):
    """案1（2026-10-13 採用）の局面: S&P500（SPY）の終値が100日線（20週線）より上かつ線が20取引日前より上の日。
    買う日の前の取引日（引け後に判定する日）がこの集合に入っていれば2倍ETFで買う。(上昇の日の集合, 前の取引日を返す関数)"""
    from backtest_lib import load_prices
    g = load_prices(cache, "SPY")
    c, ds = g["c"], g["date"]
    up = set()
    for i in range(120, len(c)):
        m = sum(c[i - 99:i + 1]) / 100
        m20 = sum(c[i - 119:i - 19]) / 100
        if c[i] > m and m > m20:
            up.add(ds[i])
    k = {d: i for i, d in enumerate(ds)}
    return up, (lambda d: ds[k[d] - 1] if k.get(d, 0) > 0 else None)


def actual_stage(base, data, sim, port, days, ind, watch87, cache):
    """実際の運用に近い条件での今のルールの成績（2026-10-14 ユーザーの指示）。
    今のルール: 4銘柄・1銘柄25%、同じ業種2銘柄まで、50日線の傾きが小さい順、2倍ETF（実測の目減り）、損切りは全部のルールで日中の逆指値15%。
    watch87=False: 後知恵なしの監視銘柄で ①全業種（今までの基準） ②AI・半導体・データセンター関連の業種を先に買う ③その業種だけ。
    watch87=True : 監視銘柄を今のテーマ監視銘柄（87銘柄）に固定（後知恵あり）。結果は同じファイルの後ろに足す"""
    import json
    from backtest_caps import THEME
    DC = {"Electrical Equipment & Parts", "Specialty Industrial Machinery", "Engineering & Construction", "Building Products & Equipment",
          "Utilities—Independent Power Producers", "REIT—Specialty"}   # backtest_theme_only.DC と同じ
    AI = set(THEME) | DC
    sma_ = lambda c, j, n: sum(c[j - n + 1:j + 1]) / n
    def s50(b):
        c, j = data[b["sym"]]["c"], b["i0"] - 1
        return sma_(c, j, 50) / sma_(c, j - 20, 50) - 1 if j >= 70 else 0.0
    tab = json.load(open(os.path.join(os.path.dirname(OUTDIR.rstrip("/")), "2倍ETFの対応表.json"), encoding="utf-8"))
    drag = {s: -x["drag"] for s, x in tab.items() if isinstance(x, dict) and "drag" in x}
    HAS = {s for s, d in drag.items() if d < 0.15}
    def to2x(trs, reg=None):   # reg=(上昇の日, 前の取引日) なら案1（上昇の局面の日に買う売買だけ2倍ETF）
        out = []
        for t in trs:
            if t["sym"] not in HAS or (reg and reg[1](t["in"]) not in reg[0]):
                out.append(t)
                continue
            fee = drag[t["sym"]] / 252
            e, prev, pv = 1 - COST, 1 - COST, {}
            for d in sorted(t["path"]):
                g_ = t["path"][d]
                e = max(0.0, e * (1 + 2 * (g_ / prev - 1)) * (1 - fee))
                prev = g_
                pv[d] = e
            out.append({**t, "path": pv})
        return out
    def intraday(b):   # 損切りを日中の逆指値15%に（押し目は元から）。stopcheck_stage.restop と同じ
        if b["rule"] == "B":
            return b
        s = data[b["sym"]]
        floor = b["px"] * (1 - STOP)
        for j in range(b["i0"], b["i1"]):
            if s["l"][j] <= floor:
                return {**b, "i1": j, "xp": min(s["o"][j] if j > b["i0"] else b["px"], floor)}
        return b
    stock = []
    for b in base:
        b2 = intraday(b)
        p = sim(b2, half=xc.c1)
        stock.append({"sym": b2["sym"], "in": data[b2["sym"]]["date"][b2["i0"]], "out": max(p), "path": p,
                      "s50": s50(b2), "rule": b2["rule"], "w": 1.0, "ai": ind.get(b2["sym"]) in AI})
    reg = etf_up_days(cache)
    trs0 = to2x(stock)        # 2倍ETFをいつでも使う（案1の前）
    trs = to2x(stock, reg)    # 案1（今のルール）
    last3 = (dt.date.fromisoformat(days[-1]) - dt.timedelta(days=365 * 3)).isoformat()
    l3 = min(d for d in days if d >= last3)
    is_hi = max(d for d in days if d <= cb.IS_END)
    oos_lo = min(d for d in days if d >= cb.OOS_START)
    med = lambda xs: sorted(xs)[len(xs) // 2]
    if watch87:
        forms = [("③ 監視銘柄を今の87銘柄に固定（後知恵あり）・案1", [{**t, "prio": t["s50"]} for t in trs]),
                 ("③ 監視銘柄を今の87銘柄に固定（後知恵あり）・2倍ETFをいつでも使う（案1の前）", [{**t, "prio": t["s50"]} for t in trs0])]
    else:
        forms = [("① 後知恵なしの監視銘柄・全業種（今までの基準）・案1", [{**t, "prio": t["s50"]} for t in trs]),
                 ("② 後知恵なしの監視銘柄・AI・半導体・データセンター関連を先に買う（実際の運用に近い）・案1", [{**t, "prio": (0 if t["ai"] else 1, t["s50"])} for t in trs]),
                 ("②' 後知恵なしの監視銘柄・AI・半導体・データセンター関連だけ（参考）・案1", [{**t, "prio": t["s50"]} for t in trs if t["ai"]]),
                 ("① 全業種・2倍ETFをいつでも使う（案1の前）", [{**t, "prio": t["s50"]} for t in trs0]),
                 ("② AI・半導体を先に買う・2倍ETFをいつでも使う（案1の前）", [{**t, "prio": (0 if t["ai"] else 1, t["s50"])} for t in trs0])]
    L = []
    w = L.append
    path = OUTDIR + "実際の運用に近い条件での成績" + os.environ.get("OUT_SUFFIX", "") + ".md"
    if watch87:
        w("\n## ③ 監視銘柄を今の87銘柄に固定（`--watch87`、後知恵あり）\n")
        w("| 形 | 組 | 2015年〜 年率 | 含み損込みの最大下落率（中央値／最悪） | 確定した損益だけの最大下落率（中央値／最悪） | 2015〜2021年 | 2022年〜 | **直近3年 年率** | 直近3年 含み損込みの最大下落率 |")
        w("|---|---|---|---|---|---|---|---|---|")
    else:
        w(f"---\ntype: backtest\ntitle: 実際の運用に近い条件での成績\ncreated: {dt.date.today()}\nscript: tools/backtest_retest.py --stage actual（③は --watch87）\n---\n")
        w("# 実際の運用に近い条件での今のルールの成績\n")
        w("2026-10-14、ユーザーの指摘「実際と同じ状況でないとバックテストの意味がない」（バックテストの監視銘柄は全業種から選ぶ後知恵なしの一覧で、実際は87銘柄のAI・半導体が中心）を受けて確かめた。"
          "今のルール: 4銘柄・1銘柄25%、同じ業種2銘柄まで、同じ日の候補は50日線の傾きが小さい順、2倍ETFがある銘柄は2倍ETF（実測の目減り）、"
          "**損切りは全部のルールで日中の逆指値15%（実際の運用どおり）**、手じまい・半分売りは今のとおり。"
          "**案1（2026-10-13 採用）: 2倍ETFは、買う日の前の取引日にS&P500（SPY）が100日線（20週線）より上かつ線が20取引日前より上（上昇の局面）のときだけ。それ以外は元の株**。"
          "比べるため、案1の前（2倍ETFをいつでも使う）も載せる。片道0.1%込み。乱数50通り×2組の中央値。\n")
        w("- ①②: 後知恵なしの監視銘柄（毎週その時点のS&P500の構成銘柄から、その時点の数値で最大100銘柄を選び直す）。"
          "②は実際の毎朝のスキャン（87銘柄＝AI・半導体を中心に、空き枠があるときだけテーマの外も買う）に近づけた形で、同じ日の候補はAI・半導体・データセンター関連の業種"
          "（`backtest_caps.THEME` と `backtest_theme_only.DC`）を先に買う。②'はその業種だけを買う参考。")
        w("- ③: 監視銘柄を今のテーマ監視銘柄（87銘柄、S&P500の構成銘柄かどうかを問わない）に固定。**今の時点で伸びた銘柄を選んでいるので後知恵があり、実際より良く出る上限の目安。**"
          "新高値V2の「RS上位10」は87銘柄の中での順位。テーマの外の銘柄は買わない。\n")
        w(f"直近3年 = {l3}〜{days[-1]}。\n")
        w("| 形 | 組 | 2015年〜 年率 | 含み損込みの最大下落率（中央値／最悪） | 確定した損益だけの最大下落率（中央値／最悪） | 2015〜2021年 | 2022年〜 | **直近3年 年率** | 直近3年 含み損込みの最大下落率 |")
        w("|---|---|---|---|---|---|---|---|---|")
    for nm, tr_ in forms:
        for s0 in (5000, 7300):
            cg, mm, rm, ii, oo, g3, m3 = [], [], [], [], [], [], []
            for k in range(50):
                rc = []
                g, m = port(tr_, s0 + k, days[0], days[-1], rcurve=rc)
                pk, r = 0.0, 0.0
                for x in rc:
                    pk = max(pk, x)
                    r = max(r, 1 - x / pk)
                cg.append(g); mm.append(m); rm.append(r)
                ii.append(port(tr_, s0 + k, days[0], is_hi)[0]); oo.append(port(tr_, s0 + k, oos_lo, days[-1])[0])
                a3, b3 = port(tr_, s0 + k, l3, days[-1])
                g3.append(a3); m3.append(b3)
            w(f"| {nm} | {'1組目' if s0 == 5000 else '2組目'} | {pct(med(cg))} | {pct(med(mm))}／{pct(max(mm))} | {pct(med(rm))}／{pct(max(rm))} | {pct(med(ii))} | {pct(med(oo))} | **{pct(med(g3))}** | {pct(med(m3))} |")
            print(nm, s0, file=sys.stderr)
    w("")
    w("| 形 | 合図の数（2015年〜、年あたり） | うち直近3年 | 勝率 | 1回平均（株） |")
    w("|---|---|---|---|---|")
    yrs = (dt.date.fromisoformat(days[-1]) - dt.date.fromisoformat(days[0])).days / 365.25
    for nm, tr_ in forms:
        st = [t for t in stock if not nm.startswith("②'") or t["ai"]]
        rr = [t["path"][t["out"]] - 1 for t in st]
        w(f"| {nm} | {len(st)}（{len(st) / yrs:.0f}） | {sum(1 for t in st if t['in'] >= l3)} | {sum(x > 0 for x in rr) / max(1, len(rr)) * 100:.0f}% | {pct(sum(rr) / max(1, len(rr)))} |")
    if watch87:
        w("\n- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
        open(path, "a", encoding="utf-8").write("\n".join(L) + "\n")
    else:
        open(path, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("書き出し", file=sys.stderr)


def opt_stage(base, data, sim, days, ind, cache, part):
    """直した数え方（--keep-open --overlap）で、年率を上げる形を探す（2026-10-16 ユーザーの指示「年率が下がるならきちんと上がるルールを作って」）。
    part: 1 = 決まりを1つずつ変える、2 = 良かった形の組み合わせ（環境変数 OPT_COMBO に形の名前をカンマ区切り）。
    判定: 乱数30通り×2組の中央値で、2015〜2021年・2022年〜の両方とも、2組とも今のルールを上回ったら「上回った」"""
    import json
    from backtest_caps import THEME
    DC = {"Electrical Equipment & Parts", "Specialty Industrial Machinery", "Engineering & Construction", "Building Products & Equipment",
          "Utilities—Independent Power Producers", "REIT—Specialty"}
    AI = set(THEME) | DC
    sma_ = lambda c, j, n: sum(c[j - n + 1:j + 1]) / n
    def s50(b):
        c, j = data[b["sym"]]["c"], b["i0"] - 1
        return sma_(c, j, 50) / sma_(c, j - 20, 50) - 1 if j >= 70 else 0.0
    tab = json.load(open(os.path.join(os.path.dirname(OUTDIR.rstrip("/")), "2倍ETFの対応表.json"), encoding="utf-8"))
    drag = {s: -x["drag"] for s, x in tab.items() if isinstance(x, dict) and "drag" in x}
    HAS = {s for s, d in drag.items() if d < 0.15}
    up, prev = etf_up_days(cache)
    di = {d: k for k, d in enumerate(days)}
    # 同じ銘柄・同じルールの合図が、前の取引日にも出ていたか（続けての合図）
    sig = {(b["sym"], b["rule"], data[b["sym"]]["date"][b["i0"]]) for b in base}
    def streak_first(b):
        d = data[b["sym"]]["date"][b["i0"]]
        k = di.get(d)
        return not (k and (b["sym"], b["rule"], days[k - 1]) in sig)

    from backtest_lib import load_prices
    g_ = load_prices(cache, "^SOX")
    sm = dict(zip(g_["date"], g_["c"]))
    sox, last = [], None
    for d in days:
        last = sm.get(d, last)
        sox.append(last)
    sdd20 = {d: (sox[i] / max(x for x in sox[max(0, i - 19):i + 1] if x) - 1) if sox[i] else 0.0 for i, d in enumerate(days)}
    cache_tr = {}
    def stock_trades(stop, rel8=False):
        if (stop, rel8) in cache_tr:
            return cache_tr[(stop, rel8)]
        out = []
        for b in base:
            s = data[b["sym"]]
            floor = b["px"] * (1 - stop)
            if b["rule"] != "B" or stop < STOP:
                for j in range(b["i0"], b["i1"]):
                    if s["l"][j] <= floor:
                        b = {**b, "i1": j, "xp": min(s["o"][j] if j > b["i0"] else b["px"], floor)}
                        break
            if rel8:   # P: 保有が買値から−8%以下かつSOXが20日の最高値から−5%以上下の日の翌朝に手じまう（shock_stage と同じ）。rel8=(株, SOX) で値を変えられる
                lv, sv = rel8 if isinstance(rel8, tuple) else (0.08, 0.05)
                for j in range(b["i0"], b["i1"] - 1):
                    if s["c"][j] <= b["px"] * (1 - lv) and sdd20.get(s["date"][j], 0.0) <= -sv:
                        b = {**b, "i1": j + 1, "xp": s["o"][j + 1]}
                        break
            p = sim(b, half=xc.c1)
            out.append({"sym": b["sym"], "in": s["date"][b["i0"]], "out": max(p), "path": p, "rule": b["rule"], "ret": p[max(p)] - 1,
                        "s50": s50(b), "rs": s["rs"][b["i0"] - 1] or 0, "ai": ind.get(b["sym"]) in AI, "first": streak_first(b)})
        cache_tr[(stop, rel8)] = out
        return out

    def lev(trs, mode):
        out = []
        for t in trs:
            if t["sym"] not in HAS or mode == "none" or (mode == "reg" and prev(t["in"]) not in up):
                out.append(t)
                continue
            fee = drag[t["sym"]] / 252
            e, pr, pv = 1 - COST, 1 - COST, {}
            for d in sorted(t["path"]):
                e = max(0.0, e * (1 + 2 * (t["path"][d] / pr - 1)) * (1 - fee))
                pr = t["path"][d]
                pv[d] = e
            out.append({**t, "path": pv})
        return out

    def port(trs, seed, lo, hi, slots=4, cap=2):
        by_in = {}
        for t in trs:
            if lo <= t["in"] and t["out"] <= hi:
                by_in.setdefault(t["in"], []).append(t)
        rnd = random.Random(seed)
        cash, held, peak, mdd, eq = 1.0, [], 1.0, 0.0, 1.0
        dd = days[di[lo]:di[hi] + 1]
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
                if len(held) >= slots:
                    break
                if cap and sum(1 for h in held if ind.get(h["t"]["sym"]) == ind.get(t["sym"])) >= cap:
                    continue
                size = min(eq / slots, cash)
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

    PR = {"slope": lambda t: (0 if t["ai"] else 1, t["s50"]),
          "rs": lambda t: (0 if t["ai"] else 1, -t["rs"]),
          "rs_noai": lambda t: -t["rs"],
          "first_rs": lambda t: (0 if t["ai"] else 1, 0 if t["first"] else 1, -t["rs"]),
          "trend_rs": lambda t: (0 if t["ai"] else 1, 0 if t["rule"] in ("M", "V") else 1, -t["rs"]),
          "rev_rs": lambda t: (0 if t["ai"] else 1, 0 if t["rule"] in ("B", "C") else 1, -t["rs"]),
          "slope_big": lambda t: (0 if t["ai"] else 1, -t["s50"])}
    # 形: 名前 → 決まり（変えない項目は今のルール）
    BASE = {"rules": ("B", "C", "M", "V"), "prio": "slope", "streak": None, "slots": 4, "cap": 2, "etf": "reg", "stop": STOP, "rel8": False}
    V1 = {"今のルール（傾きの小さい順）": {},
          "買う順番: RSの高い順": {"prio": "rs"},
          "買う順番: RSの高い順（AI半導体を先にしない）": {"prio": "rs_noai"},
          "買う順番: 続けての合図より初日の合図を先に、その中はRSの高い順": {"prio": "first_rs"},
          "買う順番: 順張りを先に、その中はRSの高い順": {"prio": "trend_rs"},
          "買う順番: 逆張りを先に、その中はRSの高い順": {"prio": "rev_rs"},
          "買う順番: 傾きの大きい順": {"prio": "slope_big"},
          "続けての合図は買わない（全部のルール、初日だけ）": {"streak": "all"},
          "続けての合図は買わない（押し目・急落の底だけ初日だけ）": {"streak": "rev"},
          "続けての合図は買わない（順張りだけ初日だけ）": {"streak": "trend"},
          "銘柄数3": {"slots": 3}, "銘柄数5": {"slots": 5}, "銘柄数6": {"slots": 6},
          "同じ業種1銘柄まで": {"cap": 1}, "同じ業種の上限なし": {"cap": 0},
          "2倍ETFを使わない": {"etf": "none"}, "2倍ETFをいつでも使う": {"etf": "all"},
          "損切り10%（日中の逆指値）": {"stop": 0.10}, "損切り12%（日中の逆指値）": {"stop": 0.12},
          "ミネルヴィニを外す": {"rules": ("B", "C", "V")}, "急落の底を外す": {"rules": ("B", "M", "V")},
          "P（保有が−8%かつSOXが20日の最高値から−5%で手じまう）": {"rel8": True},
          "P（保有が−6%かつSOXが−5%）": {"rel8": (0.06, 0.05)}, "P（保有が−10%かつSOXが−5%）": {"rel8": (0.10, 0.05)},
          "P（保有が−8%かつSOXが−3%）": {"rel8": (0.08, 0.03)}, "P（保有が−8%かつSOXが−7%）": {"rel8": (0.08, 0.07)},
          "P（保有が−8%、SOXの条件なし）": {"rel8": (0.08, -1.0)}}
    combos = [x for x in os.environ.get("OPT_COMBO", "").split(";") if x]
    forms = list(V1.items()) if part == 1 else [("今のルール（傾きの小さい順）", {})] + [
        (c, {k: v for nm in c.split("＋") for k, v in V1[nm].items()}) for c in combos]

    def make(spec):
        sp = {**BASE, **spec}
        trs = [t for t in stock_trades(sp["stop"], sp["rel8"]) if t["rule"] in sp["rules"]]
        if sp["streak"]:
            keep = {"all": ("B", "C", "M", "V"), "rev": ("B", "C"), "trend": ("M", "V")}[sp["streak"]]
            trs = [t for t in trs if t["first"] or t["rule"] not in keep]
        trs = [{**t, "prio": PR[sp["prio"]](t)} for t in trs]
        return lev(trs, sp["etf"]), sp

    last3 = (dt.date.fromisoformat(days[-1]) - dt.timedelta(days=365 * 3)).isoformat()
    l3 = min(d for d in days if d >= last3)
    is_hi = max(d for d in days if d <= cb.IS_END)
    oos_lo = min(d for d in days if d >= cb.OOS_START)
    med = lambda xs: sorted(xs)[len(xs) // 2]
    L = []
    w = L.append
    w(f"---\ntype: backtest\ntitle: 直した数え方で年率を上げる形を探す（{part}）\ncreated: {dt.date.today()}\nscript: tools/backtest_retest.py --stage opt{part} --keep-open --overlap\n---\n")
    w(f"# 直した数え方で、年率を上げる形を探す（{'決まりを1つずつ変える' if part == 1 else '良かった形の組み合わせ'}）\n")
    w("2026-10-16、ユーザーの指示「時間は掛かっても良いので正確に調査して。年率が下がるならきちんと上がるルールを作って」。"
      "**売買の数え方は直した形**（同じ銘柄に続けて出る合図も数える・最終日に持っている売買も最終日の終値で数える）。"
      "今のルール: 後知恵なしの監視銘柄でAI・半導体・データセンター関連の業種を先に買う、4つのルール、4銘柄・1銘柄＝その日の資金÷4、同じ業種2銘柄まで、"
      "同じ日の候補は50日線の傾きが小さい順、案1、損切りは全部のルールで日中の逆指値15%。2015年〜（株価は2026-10-15まで）、片道0.1%込み。乱数30通り×2組の中央値。"
      "「続けての合図」＝同じ銘柄・同じルールの合図が前の取引日にも出ていた合図（毎朝のスキャンでは前日の record.json と比べれば分かる）。\n")
    w("| 形 | 組 | 年率 | 含み損込みの最大下落率 | 2015〜2021年 | 2022年〜 | 直近3年 | 判定 |")
    w("|---|---|---|---|---|---|---|---|")
    res = {}
    for nm, spec in forms:
        trs, sp = make(spec)
        for s0 in (5000, 7300):
            cg, mm, ii, oo, g3 = [], [], [], [], []
            for q in range(30):
                g, m = port(trs, s0 + q, days[0], days[-1], sp["slots"], sp["cap"])
                cg.append(g); mm.append(m)
                ii.append(port(trs, s0 + q, days[0], is_hi, sp["slots"], sp["cap"])[0])
                oo.append(port(trs, s0 + q, oos_lo, days[-1], sp["slots"], sp["cap"])[0])
                g3.append(port(trs, s0 + q, l3, days[-1], sp["slots"], sp["cap"])[0])
            res[(nm, s0)] = (med(cg), med(mm), med(ii), med(oo))
            b0 = res.get(("今のルール（傾きの小さい順）", s0))
            ok = b0 and nm != "今のルール（傾きの小さい順）" and med(ii) > b0[2] and med(oo) > b0[3]
            w(f"| {nm} | {'1組目' if s0 == 5000 else '2組目'} | {pct(med(cg))} | {pct(med(mm))} | {pct(med(ii))} | {pct(med(oo))} | {pct(med(g3))} | {'両方の期間で上' if ok else ''} |")
            print(nm, s0, file=sys.stderr)
    if os.environ.get("OPT_YEARLY"):   # 年ごと（その年の初めに空の枠から始めた1年の増減。乱数30通りの中央値）
        years = sorted({d[:4] for d in days})
        w("\n## 年ごとの成績（その年の初めに空の枠から始めた1年の増減、乱数30通りの中央値）\n")
        w("| 形 | " + " | ".join(years) + " |")
        w("|---|" + "---|" * len(years))
        for nm, spec in forms:
            trs, sp = make(spec)
            row = []
            for y in years:
                ds = [d for d in days if d[:4] == y]
                xs = [port(trs, 5000 + q, ds[0], ds[-1], sp["slots"], sp["cap"]) for q in range(30)]
                yrs_ = (dt.date.fromisoformat(ds[-1]) - dt.date.fromisoformat(ds[0])).days / 365.25
                row.append(pct(med([(1 + g) ** yrs_ - 1 for g, _ in xs])))
            w(f"| {nm} | " + " | ".join(row) + " |")
            print("年ごと", nm, file=sys.stderr)
    good = [nm for nm, _ in forms[1:] if all(res[(nm, s)][2] > res[("今のルール（傾きの小さい順）", s)][2] and res[(nm, s)][3] > res[("今のルール（傾きの小さい順）", s)][3] for s in (5000, 7300))]
    w("\n2組とも、2015〜2021年・2022年〜の両方で今のルールを上回った形: " + ("、".join(good) or "なし") + "\n")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    open(OUTDIR + f"直した数え方で年率を上げる形を探す_{part}" + os.environ.get("OUT_SUFFIX", "") + ".md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("書き出し", file=sys.stderr)


def audit_stage(base, data, sim, days, ind, cache, flags):
    """点検（2026-10-16）: 今まで採用した主な決まり（ルールの組み合わせ・買う順番・2倍ETFの使い方）が、直した数え方でも成り立つか。
    flags: 売買の数え方（'old' = 以前、'fixed' = --keep-open --overlap）。結果は OUT_SUFFIX 付きの別ファイル"""
    import json
    from backtest_caps import THEME
    DC = {"Electrical Equipment & Parts", "Specialty Industrial Machinery", "Engineering & Construction", "Building Products & Equipment",
          "Utilities—Independent Power Producers", "REIT—Specialty"}
    AI = set(THEME) | DC
    sma_ = lambda c, j, n: sum(c[j - n + 1:j + 1]) / n
    def s50(b):
        c, j = data[b["sym"]]["c"], b["i0"] - 1
        return sma_(c, j, 50) / sma_(c, j - 20, 50) - 1 if j >= 70 else 0.0
    tab = json.load(open(os.path.join(os.path.dirname(OUTDIR.rstrip("/")), "2倍ETFの対応表.json"), encoding="utf-8"))
    drag = {s: -x["drag"] for s, x in tab.items() if isinstance(x, dict) and "drag" in x}
    HAS = {s for s, d in drag.items() if d < 0.15}
    up, prev = etf_up_days(cache)
    di = {d: k for k, d in enumerate(days)}
    stock = []
    for b in base:
        s = data[b["sym"]]
        floor = b["px"] * (1 - STOP)
        if b["rule"] != "B":
            for j in range(b["i0"], b["i1"]):
                if s["l"][j] <= floor:
                    b = {**b, "i1": j, "xp": min(s["o"][j] if j > b["i0"] else b["px"], floor)}
                    break
        p = sim(b, half=xc.c1)
        stock.append({"sym": b["sym"], "in": s["date"][b["i0"]], "out": max(p), "path": p, "rule": b["rule"], "ret": p[max(p)] - 1,
                      "s50": s50(b), "rs": s["rs"][b["i0"] - 1] or 0, "ai": ind.get(b["sym"]) in AI})
    def lev(trs, mode):
        out = []
        for t in trs:
            if t["sym"] not in HAS or mode == "none" or (mode == "reg" and prev(t["in"]) not in up):
                out.append(t)
                continue
            fee = drag[t["sym"]] / 252
            e, pr, pv = 1 - COST, 1 - COST, {}
            for d in sorted(t["path"]):
                e = max(0.0, e * (1 + 2 * (t["path"][d] / pr - 1)) * (1 - fee))
                pr = t["path"][d]
                pv[d] = e
            out.append({**t, "path": pv})
        return out

    def port(trs, seed, lo, hi):
        by_in = {}
        for t in trs:
            if lo <= t["in"] and t["out"] <= hi:
                by_in.setdefault(t["in"], []).append(t)
        rnd = random.Random(seed)
        cash, held, peak, mdd, eq = 1.0, [], 1.0, 0.0, 1.0
        dd = days[di[lo]:di[hi] + 1]
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

    is_hi = max(d for d in days if d <= cb.IS_END)
    oos_lo = min(d for d in days if d >= cb.OOS_START)
    med = lambda xs: sorted(xs)[len(xs) // 2]
    yrs = (dt.date.fromisoformat(days[-1]) - dt.date.fromisoformat(days[0])).days / 365.25
    P = {"slope": lambda t: (0 if t["ai"] else 1, t["s50"]), "random": lambda t: (0 if t["ai"] else 1, 0), "rs": lambda t: (0 if t["ai"] else 1, -t["rs"]),
         "slope_all": lambda t: t["s50"]}
    def mk(rules=("B", "C", "M", "V"), prio="slope", etf="reg"):
        return lev([{**t, "prio": P[prio](t)} for t in stock if t["rule"] in rules], etf)
    forms = [("今のルール（4つのルール・AI半導体を先に・傾きの小さい順・案1）", mk()),
             ("押し目を外す", mk(("C", "M", "V"))), ("急落の底を外す", mk(("B", "M", "V"))),
             ("ミネルヴィニを外す", mk(("B", "C", "V"))), ("新高値V2を外す", mk(("B", "C", "M"))),
             ("押し目だけ", mk(("B",))), ("急落の底だけ", mk(("C",))), ("順張りだけ（ミネルヴィニ・新高値V2）", mk(("M", "V"))),
             ("買う順番: ランダム（AI半導体は先）", mk(prio="random")), ("買う順番: RSの高い順（AI半導体は先）", mk(prio="rs")),
             ("2倍ETFを使わない（株だけ）", mk(etf="none")), ("2倍ETFをいつでも使う（案1の前）", mk(etf="all"))]
    L = []
    w = L.append
    lab = "以前の数え方" if flags == "old" else "直した数え方（--keep-open --overlap）"
    w(f"---\ntype: backtest\ntitle: 点検 採用した決まりの確かめ直し（{lab}）\ncreated: {dt.date.today()}\nscript: tools/backtest_retest.py --stage audit{'' if flags == 'old' else ' --keep-open --overlap'}\n---\n")
    w(f"# 点検: 今まで採用した決まりが、{lab}でも成り立つか\n")
    w("2026-10-16、ユーザーの指示「今まで行った全てのバックテストで不備がないか確認して」。後知恵なしの監視銘柄、損切りは全部のルールで日中の逆指値15%、4銘柄・1銘柄＝その日の資金÷4、同じ業種2銘柄まで、2015年〜（株価は2026-10-15まで）、片道0.1%込み。乱数30通り×2組の中央値。\n")
    w("## 1. ルールごとの合図の成績（株の値段、枠に入らなかった合図も含む）\n")
    w("| ルール | 合図の数（年） | 勝率 | 1回平均 | 1回の中央値 |")
    w("|---|---|---|---|---|")
    for r, nm in (("B", "押し目"), ("C", "急落の底"), ("M", "ミネルヴィニ"), ("V", "新高値V2")):
        xs = [t["ret"] for t in stock if t["rule"] == r]
        if xs:
            w(f"| {nm} | {len(xs)}（{len(xs) / yrs:.0f}） | {sum(x > 0 for x in xs) / len(xs) * 100:.0f}% | {pct(sum(xs) / len(xs))} | {pct(med(xs))} |")
    w("\n## 2. 資金全体\n")
    w("| 形 | 組 | 年率 | 含み損込みの最大下落率 | 2015〜2021年 | 2022年〜 |")
    w("|---|---|---|---|---|---|")
    for nm, trs in forms:
        for s0 in (5000, 7300):
            cg, mm, ii, oo = [], [], [], []
            for q in range(30):
                g, m = port(trs, s0 + q, days[0], days[-1])
                cg.append(g); mm.append(m)
                ii.append(port(trs, s0 + q, days[0], is_hi)[0]); oo.append(port(trs, s0 + q, oos_lo, days[-1])[0])
            w(f"| {nm} | {'1組目' if s0 == 5000 else '2組目'} | {pct(med(cg))} | {pct(med(mm))} | {pct(med(ii))} | {pct(med(oo))} |")
            print(nm, s0, file=sys.stderr)
    w("\n- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    open(OUTDIR + "点検_採用した決まりの確かめ直し" + os.environ.get("OUT_SUFFIX", "") + ".md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("書き出し", file=sys.stderr)


def parity_stage(base, data, days, recdir, fns, members):
    """バックテストの合図と、毎朝の実際のスキャン（record.json）の候補（パターンA）が一致するかの点検（2026-10-16 ユーザーの指示「全部のバックテストに不備がないか」）。
    --watch87 で、監視銘柄を今の87銘柄に固定して使う。バックテストは合図の日の翌取引日の寄り付きで買うので、合図の日＝買った日の前の取引日"""
    import glob
    import json
    KIND = lambda k: "B" if "ボリンジャー" in k else "C" if "急落の底" in k else "V" if "新高値" in k else "M" if "ミネルヴィニ" in k else "?"
    RN = {"B": "押し目", "C": "急落の底", "M": "ミネルヴィニ", "V": "新高値V2"}
    di = {d: k for k, d in enumerate(days)}
    bt = {}
    for b in base:
        d_in = data[b["sym"]]["date"][b["i0"]]
        k = di.get(d_in)
        if k:
            bt.setdefault(days[k - 1], set()).add((b["sym"], b["rule"]))
    L = []
    w = L.append
    w(f"---\ntype: backtest\ntitle: バックテストの合図と毎朝のスキャンの一致\ncreated: {dt.date.today()}\nscript: tools/backtest_retest.py --stage parity --watch87\n---\n")
    w("# バックテストの合図と、毎朝の実際のスキャン（`record.json`）の候補が一致するか\n")
    w("監視銘柄を今の87銘柄に固定したバックテストの合図（急落の底・押し目・ミネルヴィニ・新高値V2）と、毎朝のスキャンのパターンA（翌日の寄り付きで買う候補）を、合図の日（米国の引けの日）ごとに比べた。"
      "毎朝のスキャンは件数の上限（急落の底・新高値は4件、新高値V2はRS上位10）・同じ業種2銘柄まで・保有中の銘柄を外すので、バックテストの合図の方が多いのは正常。"
      "**毎朝のスキャンにあってバックテストにない合図**があれば、計算の食い違い。\n")
    w("| 合図の日 | 毎朝のスキャンのA | バックテストの合図 | スキャンにあってバックテストにない | バックテストにあってスキャンにない |")
    w("|---|---|---|---|---|")
    miss_total, live_total, why_ = 0, 0, []
    for f in sorted(glob.glob(os.path.join(recdir, "*.json"))):
        r = json.load(open(f, encoding="utf-8"))
        d = r["trade_date"]
        if d not in di:
            continue
        live = {(c["sym"], KIND(c["kind"])) for c in r["candidates"] if c.get("pattern") == "A"}
        held = {h["sym"] for h in r.get("holdings", [])}
        b_ = set()   # バックテストの合図の関数と銘柄選びの条件を、その日の引けで直接当てた結果（売買の数え方の影響を受けない）
        for sym, s_ in data.items():
            if d not in s_["date"]:
                continue
            i = s_["date"].index(d)
            for k, (f, okf) in fns.items():
                try:
                    if okf(s_, i, members[sym]) and f(i, s_) is not None:
                        b_.add((sym, k))
                except (TypeError, ValueError, IndexError, ZeroDivisionError, KeyError):
                    pass
        miss = live - b_
        extra = {x for x in b_ - live if x[0] not in held}
        miss_total += len(miss)
        live_total += len(live)
        fmt = lambda xs: "、".join(f"{s}（{RN.get(k, k)}）" for s, k in sorted(xs)) or "—"
        w(f"| {d} | {fmt(live)} | {fmt(b_)} | **{fmt(miss)}** | {fmt(extra)} |")
    w(f"\n毎朝のスキャンのAの合図 {live_total} 件のうち、バックテストにない合図: **{miss_total} 件**\n")
    w("## 売買の数え方の不備（2026-10-16 の点検で見つかった）\n")
    w("- 合図そのものは一致していても、バックテストの売買の一覧（`backtest_lib.gen_trades`・押し目の `b3_exit`）は、**データの最終日までに売りが来ていない売買を数えない**。"
      "そのため、最終日の近くで買って、まだ持っている（損をしている）売買が、成績から抜けていた。2015年〜の成績への影響は最後の数週間だけだが、"
      "「直近」「2026年9月〜」などの短い期間の数字と、今の下落の大きさは、実際より良く出ていた。")
    w("- 同じ銘柄・同じルールの売買を持っている間は、その銘柄の次の合図を数えない（実際に枠に入らなかった合図も、持っている扱いになる）。\n")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    open(OUTDIR + "バックテストの合図と毎朝のスキャンの一致.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("書き出し", miss_total, live_total, file=sys.stderr)


def shock_stage(base, data, sim, days, ind, members, cache, watch87=False):
    """通常とは違う急な下げ（ショック）を早く察知して、15%の損切りより前に手じまう形と、底を確かめるまで新しい買いを止める形（2026-10-16 ユーザーの指示）。
    土台は今のルール（AI・半導体・データセンター関連を先に買う、4銘柄、同じ業種2銘柄まで、50日線の傾きが小さい順、案1、損切りは全部のルールで日中の逆指値15%）。
    判定はその日の引けで行い、翌取引日の寄り付きで手じまう・その日の買いを止める（後知恵なし）"""
    import json
    from backtest_caps import THEME
    from backtest_lib import is_member, load_prices
    DC = {"Electrical Equipment & Parts", "Specialty Industrial Machinery", "Engineering & Construction", "Building Products & Equipment",
          "Utilities—Independent Power Producers", "REIT—Specialty"}
    AI = set(THEME) | DC
    sma_ = lambda c, j, n: sum(c[j - n + 1:j + 1]) / n
    def s50(b):
        c, j = data[b["sym"]]["c"], b["i0"] - 1
        return sma_(c, j, 50) / sma_(c, j - 20, 50) - 1 if j >= 70 else 0.0
    tab = json.load(open(os.path.join(os.path.dirname(OUTDIR.rstrip("/")), "2倍ETFの対応表.json"), encoding="utf-8"))
    drag = {s: -x["drag"] for s, x in tab.items() if isinstance(x, dict) and "drag" in x}
    HAS = {s for s, d in drag.items() if d < 0.15}
    up, prev = etf_up_days(cache)
    di = {d: k for k, d in enumerate(days)}

    # --- 指標: SOX、VIX、AI関連の業種のS&P500構成銘柄の等金額平均と、その日に−3%以上下げた銘柄の割合 ---
    def series(sym):
        g = load_prices(cache, sym)
        m = dict(zip(g["date"], g["c"]))
        out, last = [], None
        for d in days:
            last = m.get(d, last)
            out.append(last)
        return out
    sox, vix = series("^SOX"), series("^VIX")
    ai_syms = [s for s in data if ind.get(s) in AI]
    pos_ = {s: {d: k for k, d in enumerate(data[s]["date"])} for s in ai_syms}
    aidx, down3 = [1.0], [0.0]
    for n, d in enumerate(days[1:], 1):
        rs, dn = [], 0
        for s in ai_syms:
            k = pos_[s].get(d)
            if k is None or k < 1 or not is_member(members[s], d):
                continue
            r = data[s]["c"][k] / data[s]["c"][k - 1] - 1
            rs.append(r)
            dn += r <= -0.03
        aidx.append(aidx[-1] * (1 + (sum(rs) / len(rs) if rs else 0.0)))
        down3.append(dn / len(rs) if len(rs) >= 10 else 0.0)
    N = len(days)
    def chg(x, i, k):
        return x[i] / x[i - k] - 1 if i >= k and x[i] and x[i - k] else 0.0
    D = {"A": set(), "B": set(), "C": set(), "V": set(), "D": set()}
    sdd20 = {}   # SOXの直近20取引日の最高値（終値）からの下落率
    for i in range(25, N):
        d = days[i]
        if chg(aidx, i, 3) <= -0.06:
            D["A"].add(d)   # AI関連の等金額平均が3取引日で−6%以上
        if chg(sox, i, 3) <= -0.07:
            D["B"].add(d)   # SOXが3取引日で−7%以上
        if down3[i] >= 0.5:
            D["C"].add(d)   # AI関連の銘柄の半分以上がその日に−3%以上（一斉の急落の日）
        if vix[i] and (vix[i] >= 25 or chg(vix, i, 5) >= 0.40):
            D["V"].add(d)   # VIXが25以上、または5日で+40%以上
        sdd20[d] = sox[i] / max(x for x in sox[i - 19:i + 1] if x) - 1 if sox[i] else 0.0
        if sdd20[d] <= -0.07:
            D["D"].add(d)   # SOXが直近20取引日の最高値から−7%以上（じわじわ下げる形もとらえる）
    DN = {"A": "AI関連の等金額平均が3日で−6%以上", "B": "SOXが3日で−7%以上", "C": "AI関連の半分以上が同じ日に−3%以上", "V": "VIXが25以上か5日で+40%以上",
          "D": "SOXが直近20取引日の最高値から−7%以上（じわじわ下げる形も入る）"}

    def blocked(shock, how):
        """ショックの日から、底の確認ができた日まで（その日を含まない）新しい買いを止める日の集合"""
        out, on, low_i, t0 = set(), False, None, None
        for i in range(25, N):
            d = days[i]
            if d in shock:
                on, t0 = True, i
                if low_i is None:
                    low_i = i
            if on:
                if how == "sox10":   # SOXの終値が10日線より上
                    ok = sox[i] > sum(sox[i - 9:i + 1]) / 10 and d not in shock
                elif how == "rebound":   # AI関連の等金額平均が、ショックの後の一番安い終値から+5%
                    low_i = i if aidx[i] < aidx[low_i] else low_i
                    ok = aidx[i] / aidx[low_i] - 1 >= 0.05
                else:   # 10取引日たったら
                    ok = i - t0 >= 10
                if ok:
                    on, low_i = False, None
                else:
                    out.add(d)
        return out

    def build(shock=None, exit_mode=None, block=None, block_rules=("B", "C", "M", "V")):
        out = []
        for b in base:
            s = data[b["sym"]]
            d_in = s["date"][b["i0"]]
            if block is not None and b["rule"] in block_rules and prev(d_in) in block:
                continue
            floor = b["px"] * (1 - STOP)
            if b["rule"] != "B":
                for j in range(b["i0"], b["i1"]):
                    if s["l"][j] <= floor:
                        b = {**b, "i1": j, "xp": min(s["o"][j] if j > b["i0"] else b["px"], floor)}
                        break
            if exit_mode == "rel8":   # 保有ごとの判定: 買値から−8%以下かつSOXが20日の最高値から−5%以上下の日の翌朝に手じまう（テーマと一緒に下げている保有だけ）
                for j in range(b["i0"], b["i1"] - 1):
                    if s["c"][j] <= b["px"] * 0.92 and sdd20.get(s["date"][j], 0.0) <= -0.05:
                        b = {**b, "i1": j + 1, "xp": s["o"][j + 1]}
                        break
            elif shock is not None and exit_mode:
                for j in range(b["i0"], b["i1"] - 1):
                    if s["date"][j] not in shock:
                        continue
                    if exit_mode == "loser" and s["c"][j] >= b["px"]:
                        continue
                    if exit_mode == "tight":   # ショックの日から損切りを買値の7%下に引き上げる
                        f2 = b["px"] * 0.93
                        if s["c"][j] <= f2:
                            b = {**b, "i1": j + 1, "xp": s["o"][j + 1]}
                        else:
                            for k in range(j + 1, b["i1"]):
                                if s["l"][k] <= f2:
                                    b = {**b, "i1": k, "xp": min(s["o"][k], f2)}
                                    break
                        break
                    b = {**b, "i1": j + 1, "xp": s["o"][j + 1]}
                    break
            p = sim(b, half=xc.c1)
            t = {"sym": b["sym"], "in": d_in, "out": max(p), "path": p, "rule": b["rule"], "ret": p[max(p)] - 1,
                 "prio": (0 if ind.get(b["sym"]) in AI else 1, -(s["rs"][b["i0"] - 1] or 0) if os.environ.get("PRIO") == "rs" else s50(b))}
            if b["sym"] in HAS and prev(d_in) in up:
                fee = drag[b["sym"]] / 252
                e, pr, pv = 1 - COST, 1 - COST, {}
                for d in sorted(p):
                    e = max(0.0, e * (1 + 2 * (p[d] / pr - 1)) * (1 - fee))
                    pr = p[d]
                    pv[d] = e
                t["path"] = pv
            out.append(t)
        return out

    def port(trs, seed, lo, hi, taken=None):
        by_in = {}
        for t in trs:
            if lo <= t["in"] and t["out"] <= hi:
                by_in.setdefault(t["in"], []).append(t)
        rnd = random.Random(seed)
        cash, held, peak, mdd, eq = 1.0, [], 1.0, 0.0, 1.0
        dd = days[di[lo]:di[hi] + 1]
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
                if taken is not None:
                    taken.append(t)
                v0 = t["path"].get(d, 1.0)
                if t["out"] == d:
                    cash += size * v0
                    continue
                held.append({"t": t, "size": size, "v": v0})
            eq = cash + sum(h["size"] * h["v"] for h in held)
            peak = max(peak, eq)
            mdd = max(mdd, 1 - eq / peak)
        yrs = (dt.date.fromisoformat(dd[-1]) - dt.date.fromisoformat(dd[0])).days / 365.25
        return eq ** (1 / yrs) - 1, mdd, eq

    last3 = (dt.date.fromisoformat(days[-1]) - dt.timedelta(days=365 * 3)).isoformat()
    l3 = min(d for d in days if d >= last3)
    oct_lo = min(d for d in days if d >= "2026-09-01")
    is_hi = max(d for d in days if d <= cb.IS_END)
    oos_lo = min(d for d in days if d >= cb.OOS_START)
    yrs = (dt.date.fromisoformat(days[-1]) - dt.date.fromisoformat(days[0])).days / 365.25
    med = lambda xs: sorted(xs)[len(xs) // 2]
    forms = [("今のルール", None, None, None, None)]
    forms += [("P: 保有が買値から−8%かつSOXが20日の最高値から−5%の日に、その保有を翌朝に手じまう", "D", "rel8", None, None),
              ("P＋D: Pの手じまい＋SOXが10日線を上回るまで新しい買いを止める（Dの日から）", "D", "rel8", "sox10", None)]
    for k in ("A", "B", "C", "V", "D"):
        forms += [(f"{k}: 損の出ている保有を翌朝に手じまう", k, "loser", None, None),
                  (f"{k}: 全部の保有を翌朝に手じまう", k, "all", None, None),
                  (f"{k}: 損切りを買値の7%下に引き上げる", k, "tight", None, None),
                  (f"{k}: SOXが10日線を上回るまで新しい買いを止める", k, None, "sox10", None),
                  (f"{k}: AI関連が安値から+5%戻るまで新しい買いを止める", k, None, "rebound", None),
                  (f"{k}: 10取引日、新しい買いを止める", k, None, "days10", None),
                  (f"{k}: 損の出ている保有を手じまい＋SOXが10日線を上回るまで買いを止める", k, "loser", "sox10", None),
                  (f"{k}: 損切りを7%に引き上げ＋AI関連が+5%戻るまで買いを止める", k, "tight", "rebound", None)]
    L = []
    w = L.append
    tag = "（87銘柄に固定・後知恵あり）" if watch87 else ""
    w(f"---\ntype: backtest\ntitle: ショックを早く察知して手じまう・底を確かめてから買う{tag}\ncreated: {dt.date.today()}\nscript: tools/backtest_retest.py --stage shock{' --watch87' if watch87 else ''}\n---\n")
    w(f"# 通常と違う急な下げ（ショック）を早く察知して、15%の損切りより前に手じまう形と、底を確かめるまで新しい買いを止める形{tag}\n")
    w("2026-10-16、ユーザーの指示「ショックなどの通常と違う下落をいち早く察知し、ルールの損切りに達する前に早く損切りして被害を少なくするルールを作って。"
      "こんな状態で買い判定はおかしい。もっと様子を見て底を確認すべき」。"
      "土台は今のルール（" + ("監視銘柄を今の87銘柄に固定" if watch87 else "後知恵なしの監視銘柄で、AI・半導体・データセンター関連の業種を先に買う")
      + "。4銘柄・1銘柄＝その日の資金÷4、同じ業種2銘柄まで、" + ("**同じ日の候補はRSの高い順**" if os.environ.get("PRIO") == "rs" else "50日線の傾きが小さい順") + "、案1、損切りは全部のルールで日中の逆指値15%）。"
      + ("**売買の数え方は直した形（--keep-open --overlap）**。" if bl.KEEP_OPEN and bl.OVERLAP else "売買の数え方は以前の形。")
      + "判定はその日の引けで行い、翌取引日の寄り付きで手じまう・その日の買いを止める。2015年〜（株価は2026-10-15まで）、片道0.1%込み。乱数50通り×2組の中央値。\n")
    w("ショックの判定（2015年〜でその状態だった日の割合と、2026年10月に出た日）:\n")
    for k, v in D.items():
        octd = sorted(d for d in v if d >= "2026-09-28")
        w(f"- {k}: {DN[k]}（{len(v) / N * 100:.1f}%の日）。2026-09-28以降: {('、'.join(octd)) or 'なし'}")
    w("")
    w("対応: 損の出ている保有を手じまう＝ショックの日の終値が買値より下の保有を翌朝の寄り付きで売る／全部の保有を手じまう／損切りを7%に引き上げる＝ショックの日から損切りを買値の7%下（日中の逆指値）にする。"
      "底の確認: ショックの日から、(a) SOXの終値が10日線を上回る、(b) AI関連の等金額平均が、ショックの後の一番安い終値から+5%戻る、(c) 10取引日たつ、のどれかまで、全部のルールの新しい買いを止める。\n")
    w("| 形 | 組 | 年率 | 含み損込みの最大下落率 | 2015〜2021年 | 2022年〜 | 直近3年 | 2026年9月〜（10/15まで） | 損で終わった（年） | 勝率 |")
    w("|---|---|---|---|---|---|---|---|---|---|")
    res = {}
    for nm, k, em, bh, _ in forms:
        trs = build(D[k] if (k and em != "rel8") else None, em, blocked(D[k], bh) if (k and bh) else None)
        for s0 in (5000, 7300):
            cg, mm, ii, oo, g3, go, nl, wr = [], [], [], [], [], [], [], []
            for q in range(50):
                tk = []
                g, m, _ = port(trs, s0 + q, days[0], days[-1], tk)
                cg.append(g); mm.append(m)
                ii.append(port(trs, s0 + q, days[0], is_hi)[0]); oo.append(port(trs, s0 + q, oos_lo, days[-1])[0])
                g3.append(port(trs, s0 + q, l3, days[-1])[0])
                go.append(port(trs, s0 + q, oct_lo, days[-1])[2] - 1)
                nl.append(sum(t["ret"] < 0 for t in tk)); wr.append(sum(t["ret"] > 0 for t in tk) / max(1, len(tk)))
            res[(nm, s0)] = (med(ii), med(oo))
            w(f"| {nm} | {'1組目' if s0 == 5000 else '2組目'} | {pct(med(cg))} | {pct(med(mm))} | {pct(med(ii))} | {pct(med(oo))} | {pct(med(g3))} | {pct(med(go))} | {med(nl) / yrs:.1f} | {med(wr) * 100:.0f}% |")
            print(nm, s0, file=sys.stderr)
    good = [nm for nm, *_ in forms[1:] if all(res[(nm, s)][0] > res[(forms[0][0], s)][0] and res[(nm, s)][1] > res[(forms[0][0], s)][1] for s in (5000, 7300))]
    w("\n両方の組で、2015〜2021年・2022年〜の両方とも今のルールを上回った形: " + ("、".join(good) or "なし") + "\n")
    w("- 「2026年9月〜」は、2026-09-01に空の4枠から始めて10/15までの資金の増減（今回の下げをどれだけ避けられたか）。")
    w("- 損で終わった・勝率は、4枠で実際に買えた売買を、売りの合図を含む株の損益で数えた（手じまいの損も損に入る）。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    fn = "ショックを早く察知して手じまう・底を確かめてから買う" + ("（87銘柄）" if watch87 else "") + os.environ.get("OUT_SUFFIX", "") + ".md"
    open(OUTDIR + fn, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("書き出し", file=sys.stderr)


def ddsize_stage(base, data, sim, days, ind, cache):
    """資金が最高値から大きく減ったら、戻るまで1銘柄の金額を小さくする形（2026-10-15 ユーザーの指示。運用を始めて2週間で資金が−20.5%）。
    今のルール（実際の運用に近い形・案1・日中の逆指値15%）が土台。下落率は毎日の時価（含み損込み）の最高値から"""
    import json
    from backtest_caps import THEME
    DC = {"Electrical Equipment & Parts", "Specialty Industrial Machinery", "Engineering & Construction", "Building Products & Equipment",
          "Utilities—Independent Power Producers", "REIT—Specialty"}
    AI = set(THEME) | DC
    sma_ = lambda c, j, n: sum(c[j - n + 1:j + 1]) / n
    def s50(b):
        c, j = data[b["sym"]]["c"], b["i0"] - 1
        return sma_(c, j, 50) / sma_(c, j - 20, 50) - 1 if j >= 70 else 0.0
    tab = json.load(open(os.path.join(os.path.dirname(OUTDIR.rstrip("/")), "2倍ETFの対応表.json"), encoding="utf-8"))
    drag = {s: -x["drag"] for s, x in tab.items() if isinstance(x, dict) and "drag" in x}
    HAS = {s for s, d in drag.items() if d < 0.15}
    up, prev = etf_up_days(cache)
    trs = []
    for b in base:
        s = data[b["sym"]]
        floor = b["px"] * (1 - STOP)
        if b["rule"] != "B":
            for j in range(b["i0"], b["i1"]):
                if s["l"][j] <= floor:
                    b = {**b, "i1": j, "xp": min(s["o"][j] if j > b["i0"] else b["px"], floor)}
                    break
        p = sim(b, half=xc.c1)
        t = {"sym": b["sym"], "in": s["date"][b["i0"]], "out": max(p), "path": p, "prio": (0 if ind.get(b["sym"]) in AI else 1, s50(b))}
        if b["sym"] in HAS and prev(t["in"]) in up:
            fee = drag[b["sym"]] / 252
            e, pr, pv = 1 - COST, 1 - COST, {}
            for d in sorted(p):
                e = max(0.0, e * (1 + 2 * (p[d] / pr - 1)) * (1 - fee))
                pr = p[d]
                pv[d] = e
            t["path"] = pv
        trs.append(t)
    by_in = {}
    for t in trs:
        by_in.setdefault(t["in"], []).append(t)
    di = {d: k for k, d in enumerate(days)}

    def port(seed, lo, hi, cut=None, back=None, mult=0.5):
        """cut: 最高値からの下落がこれ以上になったら1銘柄の金額を mult 倍にする。back: 下落がこれ未満に戻ったら元に戻す"""
        rnd = random.Random(seed)
        cash, held, peak, mdd, eq, small = 1.0, [], 1.0, 0.0, 1.0, False
        dd = days[di[lo]:di[hi] + 1]
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
                if not (lo <= t["in"] and t["out"] <= hi):
                    continue
                if any(h["t"]["sym"] == t["sym"] for h in held):
                    continue
                if len(held) >= SLOTS:
                    break
                if sum(1 for h in held if ind.get(h["t"]["sym"]) == ind.get(t["sym"])) >= 2:
                    continue
                size = min(eq / SLOTS * (mult if small else 1.0), cash)
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
            ddn = 1 - eq / peak
            mdd = max(mdd, ddn)
            if cut is not None:
                if not small and ddn >= cut:
                    small = True
                elif small and ddn < back:
                    small = False
        yrs = (dt.date.fromisoformat(dd[-1]) - dt.date.fromisoformat(dd[0])).days / 365.25
        return eq ** (1 / yrs) - 1, mdd

    last3 = (dt.date.fromisoformat(days[-1]) - dt.timedelta(days=365 * 3)).isoformat()
    l3 = min(d for d in days if d >= last3)
    is_hi = max(d for d in days if d <= cb.IS_END)
    oos_lo = min(d for d in days if d >= cb.OOS_START)
    med = lambda xs: sorted(xs)[len(xs) // 2]
    forms = [("今のルール（いつも資金÷4）", None, None, 1.0),
             ("最高値から−20%で半分に、−10%まで戻ったら元に", 0.20, 0.10, 0.5),
             ("最高値から−20%で半分に、最高値に戻ったら元に", 0.20, 0.0001, 0.5),
             ("最高値から−15%で半分に、−5%まで戻ったら元に", 0.15, 0.05, 0.5),
             ("最高値から−10%で半分に、−5%まで戻ったら元に", 0.10, 0.05, 0.5),
             ("最高値から−20%で4分の3に、−10%まで戻ったら元に", 0.20, 0.10, 0.75)]
    L = []
    w = L.append
    w(f"---\ntype: backtest\ntitle: 資金が減ったら1銘柄の金額を小さくする\ncreated: {dt.date.today()}\nscript: tools/backtest_retest.py --stage ddsize\n---\n")
    w("# 資金が最高値から大きく減ったら、戻るまで1銘柄の金額を小さくする形\n")
    w("2026-10-15、運用を始めて8取引日で4銘柄すべてが損で終わり、資金が−20.5%になったのを受けて、ユーザーの指示で確かめた。"
      "今のルール（実際の運用に近い形: 後知恵なしの監視銘柄でAI・半導体・データセンター関連を先に買う、4銘柄、同じ業種2銘柄まで、50日線の傾きが小さい順、案1、損切りは全部のルールで日中の逆指値15%）"
      "で、1銘柄の金額（ふだんは資金÷4）だけを変える。下落率は毎日の時価（含み損込み）の最高値から。小さくしている間も4銘柄まで買う（使わない分は現金）。2015年〜、片道0.1%込み。乱数50通り×2組の中央値。\n")
    w("| 形 | 組 | 年率 | 含み損込みの最大下落率（中央値／最悪） | 2015〜2021年 | 2022年〜 | 直近3年 |")
    w("|---|---|---|---|---|---|---|")
    res = {}
    for nm, cut, back, mult in forms:
        for s0 in (5000, 7300):
            cg, mm, ii, oo, g3 = [], [], [], [], []
            for k in range(50):
                g, m = port(s0 + k, days[0], days[-1], cut, back, mult)
                cg.append(g); mm.append(m)
                ii.append(port(s0 + k, days[0], is_hi, cut, back, mult)[0]); oo.append(port(s0 + k, oos_lo, days[-1], cut, back, mult)[0])
                g3.append(port(s0 + k, l3, days[-1], cut, back, mult)[0])
            res[(nm, s0)] = (med(ii), med(oo))
            w(f"| {nm} | {'1組目' if s0 == 5000 else '2組目'} | {pct(med(cg))} | {pct(med(mm))}／{pct(max(mm))} | {pct(med(ii))} | {pct(med(oo))} | {pct(med(g3))} |")
            print(nm, s0, file=sys.stderr)
    good = [nm for nm, *_ in forms[1:] if all(res[(nm, s)][0] > res[(forms[0][0], s)][0] and res[(nm, s)][1] > res[(forms[0][0], s)][1] for s in (5000, 7300))]
    w("\n両方の組で、2015〜2021年・2022年〜の両方とも今のルールを上回った形: " + ("、".join(good) or "なし") + "\n")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    open(OUTDIR + "資金が減ったら1銘柄の金額を小さくする.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("書き出し", file=sys.stderr)


def crashstops_stage(base, data, sim, days, ind, cache, lo="2026-06-01", hi="2026-09-30", out="急落の期間の損切りの回数と続けての損切り.md", note=""):
    """今のルールで、テーマ全体の急落の期間（S2）と平常時の損切りの回数、損切りの後に買った売買がまた損切りになる割合、
    2026年6〜9月の売買の一覧（2026-10-14 ユーザーの指示「今のルールに置き換えて」）。
    今のルール: 実際の運用に近い形（後知恵なしの監視銘柄でAI・半導体・データセンター関連を先に買う）、4銘柄・1銘柄＝その日の資金÷4、
    同じ業種2銘柄まで、50日線の傾きが小さい順、案1、損切りは全部のルールで日中の逆指値15%"""
    import json
    from backtest_caps import THEME
    from backtest_lib import load_prices
    DC = {"Electrical Equipment & Parts", "Specialty Industrial Machinery", "Engineering & Construction", "Building Products & Equipment",
          "Utilities—Independent Power Producers", "REIT—Specialty"}
    AI = set(THEME) | DC
    sma_ = lambda c, j, n: sum(c[j - n + 1:j + 1]) / n
    def s50(b):
        c, j = data[b["sym"]]["c"], b["i0"] - 1
        return sma_(c, j, 50) / sma_(c, j - 20, 50) - 1 if j >= 70 else 0.0
    tab = json.load(open(os.path.join(os.path.dirname(OUTDIR.rstrip("/")), "2倍ETFの対応表.json"), encoding="utf-8"))
    drag = {s: -x["drag"] for s, x in tab.items() if isinstance(x, dict) and "drag" in x}
    etf = {s: x.get("etf", "") for s, x in tab.items() if isinstance(x, dict) and "drag" in x and -x["drag"] < 0.15}
    up, prev = etf_up_days(cache)
    sox = load_prices(cache, "^SOX")
    S2 = {sox["date"][i] for i in range(60, len(sox["c"])) if sox["c"][i] / max(sox["c"][i - 59:i + 1]) - 1 <= -0.10}
    trs = []
    for b in base:
        s = data[b["sym"]]
        floor = b["px"] * (1 - STOP)
        stop = b["rule"] == "B" and b["xp"] <= floor * 1.0001
        if b["rule"] != "B":
            for j in range(b["i0"], b["i1"]):
                if s["l"][j] <= floor:
                    b = {**b, "i1": j, "xp": min(s["o"][j] if j > b["i0"] else b["px"], floor)}
                    stop = True
                    break
        p = sim(b, half=xc.c1)
        t = {"sym": b["sym"], "in": s["date"][b["i0"]], "out": max(p), "path": p, "rule": b["rule"], "stop": stop,
             "prio": (0 if ind.get(b["sym"]) in AI else 1, s50(b)), "ret": p[max(p)] - 1, "etf": ""}   # 株の損益（半分売り・かぶせ線・大陰線の売りと手数料を含む）
        if b["sym"] in etf and prev(t["in"]) in up:
            fee = drag[b["sym"]] / 252
            e, pr, pv = 1 - COST, 1 - COST, {}
            for d in sorted(p):
                e = max(0.0, e * (1 + 2 * (p[d] / pr - 1)) * (1 - fee))
                pr = p[d]
                pv[d] = e
            t["path"], t["etf"] = pv, etf[b["sym"]]
        trs.append(t)
    by_in = {}
    for t in trs:
        by_in.setdefault(t["in"], []).append(t)
    di = {d: k for k, d in enumerate(days)}

    def run(seed, log=None, curve=None):
        rnd = random.Random(seed)
        cash, held, taken, eq = 1.0, [], [], 1.0
        for d in days:
            still = []
            for h in held:
                v = h["t"]["path"].get(d)
                if v is not None:
                    h["v"] = v
                if h["t"]["out"] == d:
                    cash += h["size"] * h["v"]
                    if log is not None:
                        log.append(("売り", d, h["t"], h["size"] * (h["v"] - 1), eq))
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
                taken.append(t)
                if log is not None:
                    log.append(("買い", d, t, size, eq))
                v0 = t["path"].get(d, 1.0)
                if t["out"] == d:
                    cash += size * v0
                    continue
                held.append({"t": t, "size": size, "v": v0})
            eq = cash + sum(h["size"] * h["v"] for h in held)
            if curve is not None:
                curve[d] = (eq, [h["t"]["sym"] + ("（" + h["t"]["etf"] + "）" if h["t"]["etf"] else "") for h in held])
        yrs = (dt.date.fromisoformat(days[-1]) - dt.date.fromisoformat(days[0])).days / 365.25
        return eq ** (1 / yrs) - 1, taken

    med = lambda xs: sorted(xs)[len(xs) // 2]
    n_s2 = sum(1 for d in days if d in S2)
    n_no = len(days) - n_s2
    yrs = (dt.date.fromisoformat(days[-1]) - dt.date.fromisoformat(days[0])).days / 365.25
    KINDS = (("損で終わった売買（ルールの手じまいの損を含む。ユーザーの数え方の「損切り」）", lambda t: t["ret"] < 0),
             ("うち日中の逆指値15%の損切り", lambda t: t["stop"]))
    M = {k: {"s2": [], "no": [], "again": [], "base": [], "cl": [], "cls2": [], "yr": []} for k, _ in KINDS}
    runs = []
    for k in range(50):
        g, taken = run(5000 + k)
        runs.append((g, 5000 + k))
        for nm, f in KINDS:
            m = M[nm]
            bad = [t for t in taken if f(t)]
            ds_ = sorted(t["out"] for t in bad)
            m["yr"].append(len(bad) / yrs)
            m["s2"].append(sum(1 for d in ds_ if d in S2) / n_s2 * 21)
            m["no"].append(sum(1 for d in ds_ if d not in S2) / n_no * 21)
            after = [t for t in taken if any(0 < di[t["in"]] - di[x] <= 20 for x in ds_)]   # 損の後20取引日以内に買った売買
            m["again"].append(sum(1 for t in after if f(t)) / max(1, len(after)))
            m["base"].append(len(bad) / max(1, len(taken)))
            c2 = c2s = 0
            for i in range(1, len(ds_)):
                if di[ds_[i]] - di[ds_[i - 1]] <= 10:
                    c2 += 1
                    c2s += ds_[i] in S2
            m["cl"].append(c2)
            m["cls2"].append(c2s)
    seed = sorted(runs)[len(runs) // 2][1]
    log, curve = [], {}
    run(seed, log, curve)
    RN = {"B": "押し目（ボリンジャーIII）", "C": "急落の底", "M": "ミネルヴィニ", "V": "新高値V2"}
    L = []
    w = L.append
    w(f"---\ntype: backtest\ntitle: 急落の期間の損切りの回数と続けての損切り\ncreated: {dt.date.today()}\nscript: tools/backtest_retest.py --stage crashstops\n---\n")
    w("# テーマ全体の急落の期間の損切りの回数と、損切りの後に買った売買がまた損切りになる割合（今のルール）\n")
    w("2026-10-14、ユーザーの指示「7月の急落のときの損切りの回数を今のルールに置き換えて数え直して。途中で手じまいして損をしたのも損切りとして扱って」。"
      "今のルール: 実際の運用に近い形（後知恵なしの監視銘柄で、AI・半導体・データセンター関連の業種を先に買う）、4銘柄・1銘柄＝その日の資金÷4、同じ業種2銘柄まで、50日線の傾きが小さい順、"
      "案1（S&P500が20週線で上昇の局面の日だけ2倍ETF）、**損切りは全部のルールで日中の逆指値15%**（元の株の値段で判定）。2015年〜、片道0.1%込み。乱数50通りの中央値。"
      f"テーマ全体の急落の期間＝S2（SOXが直近60取引日の最高値から10%以上下）の日。2015年〜で {n_s2 / len(days) * 100:.0f}% の日。"
      "損で終わった＝元の株の買値より安く売った売買（2倍ETFで持った売買も、元の株の値段で判定）。\n")
    for nm, _ in KINDS:
        m = M[nm]
        w(f"## {nm}\n")
        w("| 期間 | 1か月（21取引日）あたり | 年に直すと |")
        w("|---|---|---|")
        w(f"| 全期間 | {med(m['yr']) / 12:.2f}回 | {med(m['yr']):.1f}回 |")
        w(f"| 平常時（S2でない日） | {med(m['no']):.2f}回 | {med(m['no']) * 12:.1f}回 |")
        w(f"| テーマ全体の急落の期間（S2の日） | **{med(m['s2']):.2f}回** | {med(m['s2']) * 12:.1f}回 |")
        w(f"| 倍率（S2÷平常時） | **{med(m['s2']) / max(1e-9, med(m['no'])):.1f}倍** | |\n")
        w(f"- 買った売買のうちの割合（全体）: {pct(med(m['base']))}")
        w(f"- その後20取引日以内に買った売買のうち、また同じ終わり方をした割合: **{pct(med(m['again']))}**")
        w(f"- 10取引日以内に2回続いたこと: 2015年〜で {med(m['cl'])} 回（年 {med(m['cl']) / yrs:.1f} 回）、そのうちS2の期間 {med(m['cls2'])} 回\n")
    w(f"## 3. {lo}〜{hi}の売買（乱数50通りのうち2015年〜の年率が中央値の1通り、{seed}）{note}\n")
    win = [d for d in days if lo <= d <= hi]
    e0 = curve[win[0]][0]
    pk = max((d for d in win if d <= "2026-07-31") if hi <= "2026-09-30" else win, key=lambda d: curve[d][0])
    tr = min((d for d in win if d >= pk), key=lambda d: curve[d][0])
    w(f"- 資金（{win[0]}＝100）: 一番高い日 {pk}（{curve[pk][0] / e0 * 100:.1f}）→ 一番低い日 {tr}（{curve[tr][0] / e0 * 100:.1f}、{(1 - curve[tr][0] / curve[pk][0]) * 100:.1f}%の下落）→ {win[-1]}（{curve[win[-1]][0] / e0 * 100:.1f}）\n")
    w("| 日付 | 売買 | 銘柄 | ルール | 2倍ETF | 買った日 | 売った日 | 株の損益 | 1枠の損益 | 売りの理由 | S2の日か |")
    w("|---|---|---|---|---|---|---|---|---|---|---|")
    ns = nsell = 0
    for kind, d, t, x, eq in log:
        if not (lo <= d <= hi):
            continue
        r1 = t["path"][t["out"]] - 1
        why = "—"
        if kind == "売り":
            nsell += 1
            ns += t["ret"] < 0
            why = "**損切り（日中の逆指値15%）**" if t["stop"] else ("**損で手じまい**" if t["ret"] < 0 else "ルールの売り（利益）")
            if d == days[-1] and not t["stop"]:
                why = "（データの最終日。まだ持っている扱い）"
        w(f"| {d} | {kind} | {t['sym']} | {RN[t['rule']]} | {t['etf']} | {t['in']} | {t['out']} | {pct(t['ret'])} | {pct(r1)} | {why} | {'S2' if d in S2 else ''} |")
    w(f"\n期間中に売った {nsell} 件のうち、損で終わった（損切り）{ns} 件、そのうち日中の逆指値15% {sum(1 for k_, d_, t_, *_ in log if k_ == '売り' and lo <= d_ <= hi and t_['stop'])} 件。\n")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    open(OUTDIR + out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("書き出し", seed, file=sys.stderr)


def themedrop_stage(base, data, sim, days, ind, members, cache):
    """テーマ全体の急落を検知したら、順張りを早めに手じまう・新しい買いを止める・逆張りだけ買う形（2026-10-14 ユーザーの指示）。
    土台は今のルール（実際の運用に近い形: 後知恵なしの監視銘柄でAI・半導体・データセンター関連を先に買う、案1、損切りは全部のルールで日中の逆指値15%）。
    テーマ全体の急落の判定（その日の引けで判定し、翌取引日から使う）:
      S1 SOX（フィラデルフィア半導体指数）が50日線より下、かつ直近10取引日で8%以上下げた
      S2 SOXが直近60取引日の最高値（終値）から10%以上下
      S3 AI・半導体・データセンター関連の業種のS&P500構成銘柄のうち50日線より上が40%未満、かつその等金額平均が50日線より下（毎朝のツールの「早めの警告」に近い形）
      S4 SOXが50日線より下（一番ゆるい）"""
    import json
    from backtest_caps import THEME
    from backtest_lib import is_member, load_prices
    DC = {"Electrical Equipment & Parts", "Specialty Industrial Machinery", "Engineering & Construction", "Building Products & Equipment",
          "Utilities—Independent Power Producers", "REIT—Specialty"}
    AI = set(THEME) | DC
    sma_ = lambda c, j, n: sum(c[j - n + 1:j + 1]) / n
    def s50(b):
        c, j = data[b["sym"]]["c"], b["i0"] - 1
        return sma_(c, j, 50) / sma_(c, j - 20, 50) - 1 if j >= 70 else 0.0
    tab = json.load(open(os.path.join(os.path.dirname(OUTDIR.rstrip("/")), "2倍ETFの対応表.json"), encoding="utf-8"))
    drag = {s: -x["drag"] for s, x in tab.items() if isinstance(x, dict) and "drag" in x}
    HAS = {s for s, d in drag.items() if d < 0.15}
    up, prev = etf_up_days(cache)

    # --- テーマ全体の急落の判定（日付の集合） ---
    sox = load_prices(cache, "^SOX")
    sc, sd = sox["c"], sox["date"]
    S = {"S1": set(), "S2": set(), "S3": set(), "S4": set()}
    for i in range(60, len(sc)):
        m50 = sum(sc[i - 49:i + 1]) / 50
        if sc[i] < m50:
            S["S4"].add(sd[i])
            if sc[i] / sc[i - 10] - 1 <= -0.08:
                S["S1"].add(sd[i])
        if sc[i] / max(sc[i - 59:i + 1]) - 1 <= -0.10:
            S["S2"].add(sd[i])
    ai_syms = [s for s in data if ind.get(s) in AI]
    pos_ = {s: {d: k for k, d in enumerate(data[s]["date"])} for s in ai_syms}
    idx_v, idx_d = [], []
    for d in days:
        n_up = n_all = 0
        rets = []
        for s in ai_syms:
            k = pos_[s].get(d)
            if k is None or k < 50 or not is_member(members[s], d):
                continue
            c = data[s]["c"]
            n_all += 1
            n_up += c[k] > sum(c[k - 49:k + 1]) / 50
            rets.append(c[k] / c[k - 1] - 1)
        idx_v.append((idx_v[-1] if idx_v else 1.0) * (1 + (sum(rets) / len(rets) if rets else 0.0)))
        idx_d.append(d)
        if len(idx_v) >= 50 and n_all >= 10:
            if n_up / n_all < 0.40 and idx_v[-1] < sum(idx_v[-50:]) / 50:
                S["S3"].add(d)
    di = {d: k for k, d in enumerate(days)}
    on_days = {k: sum(1 for d in days if d in v) / len(days) for k, v in S.items()}

    def build(sig=None, exit_rules=(), skip_rules=()):
        """sig: 判定の日の集合。exit_rules のルールの保有は、sig の日の翌日の寄り付きで手じまう。
        skip_rules のルールは、買う日の前の取引日が sig の日なら買わない"""
        out = []
        for b in base:
            s = data[b["sym"]]
            d_in = s["date"][b["i0"]]
            if sig is not None and b["rule"] in skip_rules and prev(d_in) in sig:
                continue
            floor = b["px"] * (1 - STOP)
            stop = b["rule"] == "B" and b["xp"] <= floor * 1.0001
            early = False
            if b["rule"] != "B":
                for j in range(b["i0"], b["i1"]):
                    if s["l"][j] <= floor:
                        b = {**b, "i1": j, "xp": min(s["o"][j] if j > b["i0"] else b["px"], floor)}
                        stop = True
                        break
            if sig is not None and b["rule"] in exit_rules:
                for j in range(b["i0"], b["i1"] - 1):
                    if s["date"][j] in sig:
                        b = {**b, "i1": j + 1, "xp": s["o"][j + 1]}
                        stop, early = False, True
                        break
            p = sim(b, half=xc.c1)
            t = {"sym": b["sym"], "in": d_in, "out": max(p), "path": p, "rule": b["rule"], "stop": stop, "early": early,
                 "prio": (0 if ind.get(b["sym"]) in AI else 1, s50(b)), "ret": p[max(p)] - 1}   # 株の損益（売りの合図・手数料を含む）
            if b["sym"] in HAS and prev(d_in) in up:
                fee = drag[b["sym"]] / 252
                e, pr, pv = 1 - COST, 1 - COST, {}
                for d in sorted(p):
                    e = max(0.0, e * (1 + 2 * (p[d] / pr - 1)) * (1 - fee))
                    pr = p[d]
                    pv[d] = e
                t["path"] = pv
            out.append(t)
        return out

    def port(trs, seed, lo, hi, taken=None):
        by_in = {}
        for t in trs:
            if lo <= t["in"] and t["out"] <= hi:
                by_in.setdefault(t["in"], []).append(t)
        rnd = random.Random(seed)
        cash, held, peak, mdd, eq = 1.0, [], 1.0, 0.0, 1.0
        dd = days[di[lo]:di[hi] + 1]
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
                if taken is not None:
                    taken.append(t)
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

    last3 = (dt.date.fromisoformat(days[-1]) - dt.timedelta(days=365 * 3)).isoformat()
    l3 = min(d for d in days if d >= last3)
    is_hi = max(d for d in days if d <= cb.IS_END)
    oos_lo = min(d for d in days if d >= cb.OOS_START)
    yrs = (dt.date.fromisoformat(days[-1]) - dt.date.fromisoformat(days[0])).days / 365.25
    med = lambda xs: sorted(xs)[len(xs) // 2]
    TR, REV, ALL = ("M", "V"), ("B", "C"), ("B", "C", "M", "V")
    forms = [("今のルール", None, (), ())]
    for sg in ("S1", "S2", "S3", "S4"):
        forms += [(f"{sg}: 順張りの保有を早めに手じまう", sg, TR, ()),
                  (f"{sg}: 順張りの新しい買いを止める（逆張りは買う）", sg, (), TR),
                  (f"{sg}: 順張りを早めに手じまい、新しい買いも止める（逆張りだけ買う）", sg, TR, TR),
                  (f"{sg}: 全部の新しい買いを止める（様子見）", sg, (), ALL),
                  (f"{sg}: 全部の保有を手じまい、全部の新しい買いを止める（現金で待つ）", sg, ALL, ALL)]
    L = []
    w = L.append
    w(f"---\ntype: backtest\ntitle: テーマ全体の急落を検知して手じまう・買いを止める\ncreated: {dt.date.today()}\nscript: tools/backtest_retest.py --stage themedrop\n---\n")
    w("# テーマ全体の急落を検知したら、順張りを早めに手じまう・新しい買いを止める・逆張りだけ買う\n")
    w("2026-10-14、ユーザーの指示「テーマ全体で急落を伴った場合、早めに手じまいして逆張りのエントリーをした方が勝率は上がらないか。流れを検知してルールに加えると年率は上がらないか。"
      "一部の銘柄ではなくテーマ全体が下がっているときは様子を見て入った方が良いと感じる」。"
      "土台は今のルール（実際の運用に近い形: 後知恵なしの監視銘柄で、AI・半導体・データセンター関連の業種を先に買う。4銘柄・1銘柄＝その日の資金÷4、同じ業種2銘柄まで、50日線の傾きが小さい順、"
      "案1〔S&P500が20週線で上昇の局面の日だけ2倍ETF〕、損切りは全部のルールで日中の逆指値15%）。2015年〜、片道0.1%込み。乱数50通り×2組の中央値。\n")
    w("テーマ全体の急落の判定（その日の引けで判定し、翌取引日の寄り付きで手じまう・その日の買いを止める）と、2015年〜でその状態だった日の割合:\n")
    w(f"- S1: SOX（半導体指数）が50日線より下、かつ直近10取引日で8%以上下げた（{on_days['S1'] * 100:.0f}%の日）")
    w(f"- S2: SOXが直近60取引日の最高値（終値）から10%以上下（{on_days['S2'] * 100:.0f}%）")
    w(f"- S3: AI・半導体・データセンター関連の業種のS&P500構成銘柄のうち50日線より上が40%未満、かつその等金額平均が50日線より下（毎朝のツールの「早めの警告」に近い形）（{on_days['S3'] * 100:.0f}%）")
    w(f"- S4: SOXが50日線より下（一番ゆるい）（{on_days['S4'] * 100:.0f}%）")
    w(f"- 10/14の引けの状態: " + "、".join(f"{k} {'あり' if days[-1] in v else 'なし'}" for k, v in S.items()) + f"（{days[-1]}）\n")
    w("| 形 | 組 | 年率 | 含み損込みの最大下落率 | 2015〜2021年 | 2022年〜 | 直近3年 | 買えた売買（年） | 勝率 | 損で終わった（年） | 15%の損切り（年） |")
    w("|---|---|---|---|---|---|---|---|---|---|---|")
    res = {}
    for nm, sg, ex_r, sk_r in forms:
        trs = build(S[sg] if sg else None, ex_r, sk_r)
        for s0 in (5000, 7300):
            cg, mm, ii, oo, g3, nt, nw, nl, ns = [], [], [], [], [], [], [], [], []
            for k in range(50):
                tk = []
                g, m = port(trs, s0 + k, days[0], days[-1], tk)
                cg.append(g); mm.append(m)
                ii.append(port(trs, s0 + k, days[0], is_hi)[0]); oo.append(port(trs, s0 + k, oos_lo, days[-1])[0])
                g3.append(port(trs, s0 + k, l3, days[-1])[0])
                nt.append(len(tk)); nw.append(sum(t["ret"] > 0 for t in tk)); nl.append(sum(t["ret"] <= 0 for t in tk)); ns.append(sum(t["stop"] for t in tk))
            res[(nm, s0)] = (med(ii), med(oo))
            w(f"| {nm} | {'1組目' if s0 == 5000 else '2組目'} | {pct(med(cg))} | {pct(med(mm))} | {pct(med(ii))} | {pct(med(oo))} | {pct(med(g3))} | "
              f"{med(nt) / yrs:.1f} | {med(nw) / max(1, med(nt)) * 100:.0f}% | {med(nl) / yrs:.1f} | {med(ns) / yrs:.1f} |")
            print(nm, s0, file=sys.stderr)
    base_nm = forms[0][0]
    good = [nm for nm, *_ in forms[1:] if all(res[(nm, s)][0] > res[(base_nm, s)][0] and res[(nm, s)][1] > res[(base_nm, s)][1] for s in (5000, 7300))]
    w("\n両方の組で、2015〜2021年・2022年〜の両方とも今のルールを上回った形: " + ("、".join(good) or "なし") + "\n")
    w("- 勝率・損で終わった数・損切りの数は、4枠で実際に買えた売買の数え方（株の値段の損益。手じまいの損も「損で終わった」に入る）。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    open(OUTDIR + "テーマ全体の急落を検知して手じまう・買いを止める.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("書き出し", file=sys.stderr)


def stopfreq_stage(base, data, sim, days, ind, cache):
    """4枠の実際の運用で、日中の逆指値15%の損切りが年に何回起きるかと、運用を始めた直後に損切りが重なる確率（2026-10-14 ユーザーの指示）。
    今のルール: 実際の運用に近い形（後知恵なしの監視銘柄でAI・半導体・データセンター関連を先に買う）、案1、損切りは全部のルールで日中の逆指値15%"""
    import json
    from backtest_caps import THEME
    DC = {"Electrical Equipment & Parts", "Specialty Industrial Machinery", "Engineering & Construction", "Building Products & Equipment",
          "Utilities—Independent Power Producers", "REIT—Specialty"}
    AI = set(THEME) | DC
    sma_ = lambda c, j, n: sum(c[j - n + 1:j + 1]) / n
    def s50(b):
        c, j = data[b["sym"]]["c"], b["i0"] - 1
        return sma_(c, j, 50) / sma_(c, j - 20, 50) - 1 if j >= 70 else 0.0
    tab = json.load(open(os.path.join(os.path.dirname(OUTDIR.rstrip("/")), "2倍ETFの対応表.json"), encoding="utf-8"))
    drag = {s: -x["drag"] for s, x in tab.items() if isinstance(x, dict) and "drag" in x}
    HAS = {s for s, d in drag.items() if d < 0.15}
    up, prev = etf_up_days(cache)
    trs = []
    for b in base:
        s = data[b["sym"]]
        floor = b["px"] * (1 - STOP)
        stop = b["rule"] == "B" and b["xp"] <= floor * 1.0001
        if b["rule"] != "B":
            for j in range(b["i0"], b["i1"]):
                if s["l"][j] <= floor:
                    b = {**b, "i1": j, "xp": min(s["o"][j] if j > b["i0"] else b["px"], floor)}
                    stop = True
                    break
        p = sim(b, half=xc.c1)
        t = {"sym": b["sym"], "in": s["date"][b["i0"]], "out": max(p), "path": p, "rule": b["rule"], "stop": stop,
             "prio": (0 if ind.get(b["sym"]) in AI else 1, s50(b)), "etf": False}
        if b["sym"] in HAS and prev(t["in"]) in up:   # 案1
            fee = drag[b["sym"]] / 252
            e, pr, pv = 1 - COST, 1 - COST, {}
            for d in sorted(p):
                e = max(0.0, e * (1 + 2 * (p[d] / pr - 1)) * (1 - fee))
                pr = p[d]
                pv[d] = e
            t["path"], t["etf"] = pv, True
        trs.append(t)
    by_in = {}
    for t in trs:
        by_in.setdefault(t["in"], []).append(t)
    di = {d: k for k, d in enumerate(days)}

    def run(seed, lo, hi):
        """lo から空の4枠で始める。買った売買の一覧（買った順）と、日ごとの資金を返す"""
        rnd = random.Random(seed)
        cash, held, taken, curve = 1.0, [], [], {}
        for d in days[di[lo]:di[hi] + 1]:
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
                taken.append(t)
                v0 = t["path"].get(d, 1.0)
                if t["out"] == d:
                    cash += size * v0
                    continue
                held.append({"t": t, "size": size, "v": v0})
            curve[d] = cash + sum(h["size"] * h["v"] for h in held)
        return taken, curve

    yrs = (dt.date.fromisoformat(days[-1]) - dt.date.fromisoformat(days[0])).days / 365.25
    med = lambda xs: sorted(xs)[len(xs) // 2]
    RN = {"B": "押し目", "C": "急落の底", "M": "ミネルヴィニ", "V": "新高値V2"}
    L = []
    w = L.append
    w(f"---\ntype: backtest\ntitle: 実際の4枠での損切りの回数と始めた直後の損\ncreated: {dt.date.today()}\nscript: tools/backtest_retest.py --stage stopfreq\n---\n")
    w("# 実際の4枠の運用で、損切りは年に何回か。運用を始めた直後に損切りが重なる確率\n")
    w("2026-10-14、ユーザーの指摘「運用を始めてまもないのに、最初の売買で損切りになり、ほかの銘柄も損切り間近。確率の計算がおかしいのでは」を受けて確かめた。"
      "今のルール（実際の運用に近い形: 後知恵なしの監視銘柄で、AI・半導体・データセンター関連を先に買う。4銘柄・1銘柄＝その日の資金÷4、同じ業種2銘柄まで、50日線の傾きが小さい順、"
      "案1〔S&P500が20週線で上昇の局面の日だけ2倍ETF〕、損切りは全部のルールで日中の逆指値15%）。損切りは、日中に元の株の買値の15%下に届いて売った売買。"
      "2015年〜、片道0.1%込み。\n")
    # 1. 年あたりの回数（2015年〜を通しで、乱数50通り）
    tk, st, rs = [], [], {}
    for k in range(50):
        taken, _ = run(5000 + k, days[0], days[-1])
        tk.append(len(taken))
        st.append(sum(t["stop"] for t in taken))
        for t in taken:
            rs.setdefault(t["rule"], [0, 0])
            rs[t["rule"]][0] += 1
            rs[t["rule"]][1] += t["stop"]
    w("## 1. 4枠で実際に買えた売買と損切りの回数（2015年〜を通しで、乱数50通りの中央値）\n")
    w(f"- 買えた売買: 年 {med(tk) / yrs:.1f} 回、そのうち損切り: **年 {med(st) / yrs:.1f} 回**（買えた売買の {med(st) / med(tk) * 100:.0f}%）\n")
    w("| ルール | 買えた売買のうちの割合 | そのルールの損切りの割合 |")
    w("|---|---|---|")
    tot = sum(v[0] for v in rs.values())
    for r, (n, s_) in sorted(rs.items()):
        w(f"| {RN[r]} | {n / tot * 100:.0f}% | {s_ / n * 100:.0f}% |")
    # 2. 始めた直後（5取引日ごとに始める日をずらす）
    starts = [d for k, d in enumerate(days) if k % 5 == 0 and k + 130 < len(days)]
    first = {1: [], 2: [], 3: [], 4: []}
    r1m, r3m, worst = [], [], []
    for k, d in enumerate(starts):
        hi = days[min(len(days) - 1, di[d] + 130)]
        taken, curve = run(9000 + k, d, hi)
        f4 = taken[:4]
        if len(f4) < 4:
            continue
        ns = sum(t["stop"] for t in f4)
        for n in first:
            first[n].append(ns >= n)
        ds = sorted(curve)
        r1m.append(curve[ds[min(len(ds) - 1, 21)]] - 1)
        r3m.append(curve[ds[min(len(ds) - 1, 63)]] - 1)
        worst.append(min(curve[x] for x in ds[:64]) - 1)
    n = len(first[1])
    w(f"\n## 2. 運用を始めた直後（2015年〜、5取引日ごとに始める日をずらした {n} 通り。空の4枠から始める）\n")
    w("| 最初に買った4回の売買のうち | 起きた割合 |")
    w("|---|---|")
    for k_ in (1, 2, 3, 4):
        w(f"| 損切りが{k_}回以上 | {sum(first[k_]) / n * 100:.0f}% |")
    w("")
    w("| 始めてから | 資金がマイナスだった割合 | −10%以下だった割合 | 中央値 |")
    w("|---|---|---|---|")
    for lab, xs_ in (("1か月後（21取引日）", r1m), ("3か月後（63取引日）", r3m)):
        w(f"| {lab} | {sum(x < 0 for x in xs_) / len(xs_) * 100:.0f}% | {sum(x <= -0.10 for x in xs_) / len(xs_) * 100:.0f}% | {pct(med(xs_))} |")
    w(f"\n- 始めてから3か月の間に一番下がったところ（始めた日の資金に対して）: 中央値 {pct(med(worst))}、−10%以下まで下がった割合 {sum(x <= -0.10 for x in worst) / len(worst) * 100:.0f}%、−20%以下 {sum(x <= -0.20 for x in worst) / len(worst) * 100:.0f}%\n")
    w("- 損切りの回数は、日中の逆指値で売った売買だけを数えた（ルールの手じまい〔50日線割れなど〕で損で終わった売買は入らない）。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    open(OUTDIR + "実際の4枠での損切りの回数と始めた直後の損.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("書き出し", file=sys.stderr)


def stopcheck_stage(base, data, sim, port, days, cache):
    """損切りの判定の仕方（引け値か、日中の逆指値か）と幅（15%・10%）を比べる（2026-10-14 ユーザーの指示）。
    これまでのバックテストは、急落の底・ミネルヴィニ・新高値V2の損切りを「引け値が買値の15%下以下 → 翌日の寄り付きで売る」で計算していた
    （backtest_lib.gen_trades）。実際の運用は日中の逆指値（買値の15%下に届いたらその場で売る）。押し目は前から日中の逆指値"""
    import json
    sma_ = lambda c, j, n: sum(c[j - n + 1:j + 1]) / n
    def s50(b):
        c, j = data[b["sym"]]["c"], b["i0"] - 1
        return sma_(c, j, 50) / sma_(c, j - 20, 50) - 1 if j >= 70 else 0.0
    tab = json.load(open(os.path.join(os.path.dirname(OUTDIR.rstrip("/")), "2倍ETFの対応表.json"), encoding="utf-8"))
    drag = {s: -x["drag"] for s, x in tab.items() if isinstance(x, dict) and "drag" in x}
    HAS = {s for s, d in drag.items() if d < 0.15}
    def to2x(trs, reg=None):   # reg=(上昇の日, 前の取引日) なら案1（上昇の局面の日に買う売買だけ2倍ETF）
        out = []
        for t in trs:
            if t["sym"] not in HAS or (reg and reg[1](t["in"]) not in reg[0]):
                out.append(t)
                continue
            fee = drag[t["sym"]] / 252
            e, prev, pv = 1 - COST, 1 - COST, {}
            for d in sorted(t["path"]):
                g_ = t["path"][d]
                e = max(0.0, e * (1 + 2 * (g_ / prev - 1)) * (1 - fee))
                prev = g_
                pv[d] = e
            out.append({**t, "path": pv})
        return out

    def restop(b, pct, intraday):
        """買った日から元の売る日の前日までに、より早く損切りが出れば売る日と値段を差し替える（元の損切りより狭いか同じ幅だけ）"""
        s = data[b["sym"]]
        o, l, c = s["o"], s["l"], s["c"]
        floor = b["px"] * (1 - pct)
        for j in range(b["i0"], b["i1"]):
            if intraday and l[j] <= floor:
                return {**b, "i1": j, "xp": min(o[j] if j > b["i0"] else b["px"], floor)}
            if not intraday and c[j] <= floor and j + 1 <= b["i1"]:
                return {**b, "i1": j + 1, "xp": o[j + 1]}
        return b

    def make(spec):
        out = []
        for b in base:
            pct, intra = spec.get(b["rule"], (0.15, b["rule"] == "B"))
            b2 = b if (pct, intra) == (0.15, b["rule"] == "B") else restop(b, pct, intra)
            p = sim(b2, half=xc.c1)
            out.append({"sym": b2["sym"], "in": data[b2["sym"]]["date"][b2["i0"]], "out": max(p), "path": p,
                        "prio": s50(b2), "rule": b2["rule"], "w": 1.0, "ret": b2["xp"] / b2["px"] - 1, "pct": pct})
        return out

    reg = etf_up_days(cache)
    T15C, T15I, T10C, T10I = (0.15, False), (0.15, True), (0.10, False), (0.10, True)
    forms = [("今までのバックテスト（押し目は日中の逆指値15%、ほかは引け値で15%）", {}),
             ("実際の運用どおり（全部のルールで日中の逆指値15%）", {"C": T15I, "M": T15I, "V": T15I}),
             ("順張りだけ引け値で10%（ほかは今までどおり）", {"M": T10C, "V": T10C}),
             ("順張りだけ日中の逆指値10%（ほかは日中の逆指値15%）", {"C": T15I, "M": T10I, "V": T10I})]
    is_hi = max(d for d in days if d <= cb.IS_END)
    oos_lo = min(d for d in days if d >= cb.OOS_START)
    med = lambda xs: sorted(xs)[len(xs) // 2]
    yrs = (dt.date.fromisoformat(days[-1]) - dt.date.fromisoformat(days[0])).days / 365.25
    L = []
    w = L.append
    w(f"---\ntype: backtest\ntitle: 損切りの判定の仕方と幅\ncreated: {dt.date.today()}\nscript: tools/backtest_retest.py --stage stopcheck\n---\n")
    w("# 損切りを引け値で判定するか日中の逆指値にするかと、順張りの損切りを10%にする形\n")
    w("2026-10-14、LITEが買って7取引日で損切り（日中の逆指値、930.48ドル）になり、ミネルヴィニのノートブックが「10%以内の損切りは絶対ルール」と答えたのを受けて、ユーザーの指示で確かめた。"
      "**これまでのバックテストは、急落の底・ミネルヴィニ・新高値V2の損切りを「引け値が買値の15%下以下になったら翌日の寄り付きで売る」で計算していた**（`backtest_lib.gen_trades`）。"
      "実際の運用は日中の逆指値（買値の15%下に届いたらその場で売る）で、押し目（ボリンジャーIII）だけが前から日中の逆指値で計算されていた。"
      "日中の逆指値は、届いた日に買値の15%下（寄り付きで下に窓を開けたら寄り付きの値段）で売る。損切りの後は枠が空き、次の合図を買う。"
      "土台は今のルール（4銘柄・1銘柄25%、同じ業種2銘柄まで、50日線の傾きが小さい順、2倍ETFがある銘柄は2倍ETF〔実測の目減り〕で**案1〔S&P500が20週線で上昇の局面の日に買うときだけ2倍ETF〕**。損切り・手じまいは元の株の値段で判定）。"
      "後知恵なしの監視銘柄、2015年〜、片道0.1%込み。乱数50通り×2組の中央値。\n")
    w("## 1. 資金全体\n")
    w("| 形 | 組 | 年率 | 含み損込みの最大下落率（中央値／最悪） | 確定した損益だけの最大下落率（中央値／最悪） | 2015〜2021年 | 2022年〜 |")
    w("|---|---|---|---|---|---|---|")
    res, per = {}, {}
    for nm, spec in forms:
        stock = make(spec)
        per[nm] = stock
        trs = to2x(stock, reg)   # 案1（2026-10-13 採用）
        for s0 in (5000, 7300):
            cg, mm, rm, ii, oo = [], [], [], [], []
            for k in range(50):
                rc = []
                g, m = port(trs, s0 + k, days[0], days[-1], rcurve=rc)
                pk, r = 0.0, 0.0
                for x in rc:
                    pk = max(pk, x)
                    r = max(r, 1 - x / pk)
                cg.append(g); mm.append(m); rm.append(r)
                ii.append(port(trs, s0 + k, days[0], is_hi)[0]); oo.append(port(trs, s0 + k, oos_lo, days[-1])[0])
            res[(nm, s0)] = (med(ii), med(oo))
            w(f"| {nm} | {'1組目' if s0 == 5000 else '2組目'} | {pct(med(cg))} | {pct(med(mm))}／{pct(max(mm))} | {pct(med(rm))}／{pct(max(rm))} | {pct(med(ii))} | {pct(med(oo))} |")
            print(nm, s0, file=sys.stderr)
    base_nm = forms[0][0]
    w("\n両方の組で、2015〜2021年・2022年〜の両方とも今までのバックテストを上回った形: " +
      ("、".join(nm for nm, _ in forms[1:] if all(res[(nm, s)][0] > res[(base_nm, s)][0] and res[(nm, s)][1] > res[(base_nm, s)][1] for s in (5000, 7300))) or "なし") + "\n")
    RN = {"B": "押し目", "C": "急落の底", "M": "ミネルヴィニ", "V": "新高値V2"}
    w("\n## 2. ルールごとの成績（全部の合図、株の値段で。枠に入らなかった合図も含む）\n")
    w("「損切り」は、損切りの幅以上の損（1回の損益が −幅＋1ポイント以下）で終わった売買。\n")
    w("| 形 | ルール | 合図の数 | 勝率 | 1回平均 | 損切りの数（年あたり） | 損切りの割合 |")
    w("|---|---|---|---|---|---|---|")
    for nm, _ in forms:
        for r in "CMV":
            xs = [t for t in per[nm] if t["rule"] == r]
            if not xs:
                continue
            st = [t for t in xs if t["ret"] <= -t["pct"] + 0.01]
            w(f"| {nm} | {RN[r]} | {len(xs)} | {sum(t['ret'] > 0 for t in xs) / len(xs) * 100:.0f}% | {pct(sum(t['ret'] for t in xs) / len(xs))} | {len(st)}（{len(st) / yrs:.1f}） | {len(st) / len(xs) * 100:.0f}% |")
    w("\n- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(OUTDIR, exist_ok=True)
    open(OUTDIR + "損切りの判定の仕方と幅.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("書き出し", file=sys.stderr)


def replay_stage(base, data, build, ind, days, lo="2026-06-01", hi="2026-09-30"):
    """一斉の下げの期間（2026-06-22〜07-29の半導体の下げ）の売買を1件ずつ並べる（2026-10-13 ユーザーの指示）。
    今のルール（50日線の傾きが小さい順・2倍ETF込み・同じ業種2銘柄まで）、乱数50通りのうち2015年〜の年率が中央値の1通り"""
    import json
    sma_ = lambda c, j, n: sum(c[j - n + 1:j + 1]) / n
    def s50(b):
        c, j = data[b["sym"]]["c"], b["i0"] - 1
        return sma_(c, j, 50) / sma_(c, j - 20, 50) - 1 if j >= 70 else 0.0
    bmap = {(data[t["sym"]]["date"][t["i0"]], t["sym"], t["rule"]): t for t in base}
    tab = json.load(open(os.path.join(os.path.dirname(OUTDIR.rstrip("/")), "2倍ETFの対応表.json"), encoding="utf-8"))
    drag = {s: -x["drag"] for s, x in tab.items() if isinstance(x, dict) and "drag" in x}
    etf = {s: x.get("etf") or x.get("ticker") or "2倍ETF" for s, x in tab.items() if isinstance(x, dict) and "drag" in x and -x["drag"] < 0.15}
    stock = [{**t, "prio": s50(bmap[(t["in"], t["sym"], t["rule"])])} for t in build()]
    trs = []
    for t in stock:
        t = {**t, "stock_ret": t["path"][t["out"]] - 1}
        if t["sym"] in etf:
            fee = drag[t["sym"]] / 252
            e, prev, pv = 1 - COST, 1 - COST, {}
            for d in sorted(t["path"]):
                g_ = t["path"][d]
                e = max(0.0, e * (1 + 2 * (g_ / prev - 1)) * (1 - fee))
                prev = g_
                pv[d] = e
            t["path"] = pv
        trs.append(t)
    RN = {"B": "押し目（ボリンジャーIII）", "C": "急落の底", "M": "ミネルヴィニ", "V": "新高値V2"}

    def port(seed, log=None, curve=None):
        dd = days
        by_in = {}
        for t in trs:
            by_in.setdefault(t["in"], []).append(t)
        rnd = random.Random(seed)
        cash, held, eq = 1.0, [], 1.0
        for d in dd:
            still = []
            for h in held:
                v = h["t"]["path"].get(d)
                if v is not None:
                    h["v"] = v
                if h["t"]["out"] == d:
                    cash += h["size"] * h["v"]
                    if log is not None:
                        log.append(("売り", d, h["t"], h["size"] * (h["v"] - 1), eq))
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
                size = min(eq / SLOTS * t.get("w", 1.0), cash)
                if size <= 0:
                    break
                cash -= size
                if log is not None:
                    log.append(("買い", d, t, size, eq))
                v0 = t["path"].get(d, 1.0)
                if t["out"] == d:
                    cash += size * v0
                    continue
                held.append({"t": t, "size": size, "v": v0})
            eq = cash + sum(h["size"] * h["v"] for h in held)
            if curve is not None:
                curve[d] = (eq, [h["t"]["sym"] for h in held])
        yrs = (dt.date.fromisoformat(dd[-1]) - dt.date.fromisoformat(dd[0])).days / 365.25
        return eq ** (1 / yrs) - 1

    g = sorted((port(5000 + k), 5000 + k) for k in range(50))
    seed = g[len(g) // 2][1]
    log, curve = [], {}
    port(seed, log, curve)
    win = [d for d in days if lo <= d <= hi]
    e0 = curve[win[0]][0]
    pk_d = max((d for d in win if d <= "2026-07-31"), key=lambda d: curve[d][0])
    tr_d = min((d for d in win if d >= pk_d), key=lambda d: curve[d][0])
    L = []
    w = L.append
    w(f"---\ntype: backtest\ntitle: 一斉の下げのときの売買（2026年6〜9月）\ncreated: {dt.date.today()}\nscript: tools/backtest_retest.py --stage replay\n---\n")
    w("# 一斉の下げのとき、ツールは何を売り、何を買ったか（2026年6〜9月の再現）\n")
    w("2026-10-13、ユーザーの質問「一斉に下げたとき、すぐ損切りが始まり、また買ってもすぐ損切りする感じか」から確かめた。"
      "バックテストで一番大きい下落が出た2026-06-22〜07-29（半導体の一斉の下げ）の前後を、今のルール"
      "（4銘柄・1銘柄25%、同じ業種2銘柄まで、50日線の傾きが小さい順、2倍ETFがある銘柄は2倍ETF〔実測の目減り〕、損切り15%）で1件ずつ並べた。"
      f"後知恵なしの監視銘柄（全業種。実際の87銘柄とは違う）、片道0.1%込み。同じ日の候補の順番の乱数は、50通りのうち2015年〜の年率が中央値の1通り（{seed}、年率 {pct(g[len(g) // 2][0])}）。\n")
    w(f"## 1. 資金の動き（{win[0]} を100とする）\n")
    w(f"- この期間の一番高い日: {pk_d}（{curve[pk_d][0] / e0 * 100:.1f}）→ 一番低い日: {tr_d}（{curve[tr_d][0] / e0 * 100:.1f}、"
      f"{(1 - curve[tr_d][0] / curve[pk_d][0]) * 100:.1f}%の下落）→ {win[-1]}（{curve[win[-1]][0] / e0 * 100:.1f}）\n")
    w("| 週の最後の日 | 資金 | 持っている銘柄 |")
    w("|---|---|---|")
    for k, d in enumerate(win):
        if k + 1 == len(win) or dt.date.fromisoformat(win[k + 1]).isocalendar()[1] != dt.date.fromisoformat(d).isocalendar()[1]:
            w(f"| {d} | {curve[d][0] / e0 * 100:.1f} | {'・'.join(curve[d][1]) or '（なし）'} |")
    w("\n## 2. 売買の一覧（期間中に売った・買ったもの）\n")
    w("損益は1枠の損益（2倍ETFはETFの損益）。「資金比」は、その売買の損益を売った日の資金で割った値。売りの理由は、株の損益が−14%以下なら損切り、それ以外はルールの売り"
      "（順張りは50日線割れ・かぶせ線・半分売り、押し目は上部バンドの指値・大陰線、急落の底は5日線超え・大陰線）。\n")
    w("| 日付 | 売買 | 銘柄 | ルール | 2倍ETF | 買った日 | 売った日 | 株の損益 | 1枠の損益 | 資金比 | 売りの理由 |")
    w("|---|---|---|---|---|---|---|---|---|---|---|")
    n_stop, n_sell, by_rule = 0, 0, {}
    for kind, d, t, x, eq in log:
        if not (lo <= d <= hi):
            continue
        r1 = t["path"][t["out"]] - 1
        if kind == "売り":
            n_sell += 1
            stop = t["stock_ret"] <= -0.14
            n_stop += stop
            by_rule.setdefault(t["rule"], []).append(r1)
            w(f"| {d} | 売り | {t['sym']} | {RN[t['rule']]} | {etf.get(t['sym'], '')} | {t['in']} | {t['out']} | {pct(t['stock_ret'])} | {pct(r1)} | {pct(x / eq)} | {'**損切り**' if stop else 'ルールの売り'} |")
        else:
            w(f"| {d} | 買い | {t['sym']} | {RN[t['rule']]} | {etf.get(t['sym'], '')} | {t['in']} | {t['out']} | {pct(t['stock_ret'])} | {pct(r1)} | — | — |")
    w(f"\n期間中に売った売買 {n_sell} 件、うち損切り {n_stop} 件。\n")
    w("| ルール | 売った件数 | 勝ち | 1回平均（1枠） |")
    w("|---|---|---|---|")
    for r, xs in sorted(by_rule.items()):
        w(f"| {RN[r]} | {len(xs)} | {sum(x > 0 for x in xs)} | {pct(sum(xs) / len(xs))} |")
    w("\n## 3. 出た合図の数（枠に入らなかったものも含む、月ごと）\n")
    w("| 月 | " + " | ".join(RN[r] for r in "BCMV") + " |")
    w("|---|---|---|---|---|")
    for m in sorted({d[:7] for d in win}):
        w(f"| {m} | " + " | ".join(str(sum(1 for t in trs if t["in"][:7] == m and t["rule"] == r)) for r in "BCMV") + " |")
    w("\n- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(OUTDIR, exist_ok=True)
    open(OUTDIR + "一斉の下げのときの売買.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("書き出し", seed, file=sys.stderr)


def halfadd_stage(base, data, build, port, days):
    """合図で半分買い、残りの半分は決めた日数のうちに決めた値段まで下がったら指値で買い足す（下がらなければ半分のまま）。
    2026-10-12 ユーザーの指示。手じまいは今と同じ（買い足した分も同じ日に売る）。今のルール（50日線の傾きが小さい順・2倍ETF込み）と比べる"""
    import json
    sma_ = lambda c, j, n: sum(c[j - n + 1:j + 1]) / n
    def s50(b):
        c, j = data[b["sym"]]["c"], b["i0"] - 1
        return sma_(c, j, 50) / sma_(c, j - 20, 50) - 1 if j >= 70 else 0.0
    bmap = {(data[t["sym"]]["date"][t["i0"]], t["sym"], t["rule"]): t for t in base}
    tab = json.load(open(os.path.join(os.path.dirname(OUTDIR.rstrip("/")), "2倍ETFの対応表.json"), encoding="utf-8"))
    drag = {s: -x["drag"] for s, x in tab.items() if isinstance(x, dict) and "drag" in x}
    HAS = {s for s, d in drag.items() if d < 0.15}
    def to2x(trs):
        out = []
        for t in trs:
            if t["sym"] not in HAS:
                out.append(t)
                continue
            fee = drag[t["sym"]] / 252
            e, prev, pv = 1 - COST, 1 - COST, {}
            for d in sorted(t["path"]):
                g_ = t["path"][d]
                e = max(0.0, e * (1 + 2 * (g_ / prev - 1)) * (1 - fee))
                prev = g_
                pv[d] = e
            out.append({**t, "path": pv})
        return out
    cur = [{**t, "prio": s50(bmap[(t["in"], t["sym"], t["rule"])])} for t in build()]
    TREND = ("M", "V")
    stats = {}

    def halfadd(trs, level, wait, rules, key):
        """level(b, s) → 指値の値段。買い足しは買った翌日から wait 取引日のうち、売る日の前日まで"""
        out, n_sig, n_add, rets = [], 0, 0, []
        for t in trs:
            if t["rule"] not in rules:
                out.append(t)
                continue
            b = bmap[(t["in"], t["sym"], t["rule"])]
            s = data[t["sym"]]
            lim = level(b, s)
            ds = s["date"]
            io = ds.index(t["out"])
            fill, fd = None, None
            for j in range(b["i0"] + 1, min(b["i0"] + wait, io - 1) + 1):
                if s["l"][j] <= lim:
                    fill, fd = min(s["o"][j], lim), ds[j]
                    break
            n_sig += 1
            p, mult = t["path"], None
            if fill:
                n_add += 1
                mult = b["px"] / fill * (1 - COST)   # 買い足した分は、買った分の値動きを買値の比で引き伸ばしたもの
            pv = {}
            for d in sorted(p):
                pv[d] = 0.5 * p[d] + (0.5 * p[d] * mult if mult and d >= fd else 0.5)
            rets.append(pv[t["out"]] - 1)
            out.append({**t, "path": pv})
        stats[key] = (n_sig, n_add, sum(rets) / max(1, len(rets)))
        return out

    pct_lv = lambda x: (lambda b, s: b["px"] * (1 - x))
    ma20 = lambda b, s: sma_(s["c"], b["i0"] - 1, 20)
    forms = [("今のルール（合図で全部買う）", None),
             ("順張り: 半分＋買値の3%下に指値（10日）", (pct_lv(0.03), 10, TREND)),
             ("順張り: 半分＋買値の5%下に指値（10日）", (pct_lv(0.05), 10, TREND)),
             ("順張り: 半分＋買値の5%下に指値（20日）", (pct_lv(0.05), 20, TREND)),
             ("順張り: 半分＋買値の8%下に指値（20日）", (pct_lv(0.08), 20, TREND)),
             ("順張り: 半分＋合図の日の20日線に指値（10日）", (ma20, 10, TREND)),
             ("順張り: 半分＋合図の日の20日線に指値（20日）", (ma20, 20, TREND)),
             ("全部のルール: 半分＋買値の5%下に指値（10日）", (pct_lv(0.05), 10, ("B", "C", "M", "V")))]
    is_hi = max(d for d in days if d <= cb.IS_END)
    oos_lo = min(d for d in days if d >= cb.OOS_START)
    med = lambda xs: sorted(xs)[len(xs) // 2]
    L = []
    w = L.append
    w(f"---\ntype: backtest\ntitle: 半分は合図で買い残りは下がったら買い足す\ncreated: {dt.date.today()}\nscript: tools/backtest_retest.py --stage halfadd\n---\n")
    w("# 合図で半分買い、残りの半分は下がったら買い足す（下がらなければ半分のまま）\n")
    w("2026-10-12、ユーザーの質問「買った後に半分以上の売買で下がると分かっているなら、最適なルールは作れないか」から確かめた。"
      "今は合図で1枠（資金の25%）を全部買う。比べる形は、合図で半分（12.5%）を買い、残りの半分はその枠に取っておき、買った翌日から決めた日数のうちに"
      "日中の安値が決めた値段に届いたら指値で買い足す（寄り付きで下に窓を開けたら寄り付きの値段）。届かなければ半分のまま持つ。"
      "手じまい・損切り・半分売りは今と同じ（買い足した分も同じ日に同じ割合で売る。損切りは最初の買値で判定）。買い足しは売る日の前日まで。"
      "土台は今のルール（4銘柄・1銘柄25%、同じ業種2銘柄まで、50日線の傾きが小さい順、2倍ETFがある銘柄は2倍ETF〔実測の目減り〕）。"
      "後知恵なしの監視銘柄、2015年〜、片道0.1%込み。乱数50通り×2組の中央値。\n")
    w("| 形 | 組 | 年率 | 含み損込みの最大下落率（中央値／最悪） | 確定した損益だけの最大下落率（中央値／最悪） | 2015〜2021年 | 2022年〜 |")
    w("|---|---|---|---|---|---|---|")
    res = {}
    for nm, spec in forms:
        trs = to2x(cur if spec is None else halfadd(cur, *spec, nm))
        for s0 in (5000, 7300):
            cg, mm, rm, ii, oo = [], [], [], [], []
            for k in range(50):
                rc = []
                g, m = port(trs, s0 + k, days[0], days[-1], rcurve=rc)
                pk, r = 0.0, 0.0
                for x in rc:
                    pk = max(pk, x)
                    r = max(r, 1 - x / pk)
                cg.append(g); mm.append(m); rm.append(r)
                ii.append(port(trs, s0 + k, days[0], is_hi)[0]); oo.append(port(trs, s0 + k, oos_lo, days[-1])[0])
            res[(nm, s0)] = (med(ii), med(oo))
            w(f"| {nm} | {'1組目' if s0 == 5000 else '2組目'} | {pct(med(cg))} | {pct(med(mm))}／{pct(max(mm))} | {pct(med(rm))}／{pct(max(rm))} | {pct(med(ii))} | {pct(med(oo))} |")
            print(nm, s0, file=sys.stderr)
    base_nm = forms[0][0]
    w("\n両方の組で、2015〜2021年・2022年〜の両方とも今のルールを上回った形: " +
      ("、".join(nm for nm, _ in forms[1:] if all(res[(nm, s)][0] > res[(base_nm, s)][0] and res[(nm, s)][1] > res[(base_nm, s)][1] for s in (5000, 7300))) or "なし") + "\n")
    w("\n## 買い足しが入った割合（全部の合図、株の値段で）\n")
    w("| 形 | 対象の合図 | 買い足した合図（割合） | 1枠あたりの1回平均（株） |")
    w("|---|---|---|---|")
    c_tr = [t for t in cur if t["rule"] in TREND]
    w(f"| 今のルール（順張り） | {len(c_tr)} | — | {pct(sum(t['path'][t['out']] - 1 for t in c_tr) / len(c_tr))} |")
    for nm, (n, a_, r_) in stats.items():
        w(f"| {nm} | {n} | {a_}（{a_ / n * 100:.0f}%） | {pct(r_)} |")
    w("\n- 1枠あたりの1回平均は、1枠（資金の25%）に対する損益。半分のまま終わった売買は、使わなかった半分を0%として数える。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(OUTDIR, exist_ok=True)
    open(OUTDIR + "半分は合図で買い残りは下がったら買い足す.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("書き出し", file=sys.stderr)


def slope2_stage(base, data, build, port, ev, screen_and_confirm, days):
    """傾きの小さい順に買う形の確かめ（年ごと・2倍ETF込み）と、ルールごとに向きを変える形・似た案（2026-10-09 ユーザーの指示）"""
    import json
    import math
    med = lambda xs: sorted(xs)[len(xs) // 2]
    sma = lambda c, j, n: sum(c[j - n + 1:j + 1]) / n if j >= n - 1 else None
    rsis = {}

    def feat(t, kind):
        s, j = data[t["sym"]], t["i0"] - 1
        c = s["c"]
        if kind == "s50":
            return sma(c, j, 50) / sma(c, j - 20, 50) - 1 if j >= 70 else 0.0
        if kind == "s20":
            return sma(c, j, 20) / sma(c, j - 10, 20) - 1 if j >= 30 else 0.0
        if kind == "dev20":
            return c[j] / sma(c, j, 20) - 1 if j >= 20 else 0.0
        if kind == "r5":
            return c[j] / c[j - 5] - 1 if j >= 5 else 0.0
        if kind == "rsi14":
            if t["sym"] not in rsis:
                rsis[t["sym"]] = rsi_wilder(c, 14)
            v = rsis[t["sym"]][j]
            return v if v is not None else 50.0
    cache = {}

    def f(t, kind):
        k = (id(t), kind)
        if k not in cache:
            cache[k] = feat(t, kind)
        return cache[k]
    bmap = {(data[t["sym"]]["date"][t["i0"]], t["sym"], t["rule"]): t for t in base}
    REV = ("B", "C")

    def with_prio(trs, key):
        return [{**t, "prio": key(bmap[(t["in"], t["sym"], t["rule"])])} for t in trs]
    is_hi = max(d for d in days if d <= cb.IS_END)
    mid = {}
    for k in ("V", "M", "B", "C"):
        xs = [f(t, "s50") for t in base if t["rule"] == k and data[t["sym"]]["date"][t["i0"]] <= is_hi]
        mid[k] = med(xs) if xs else 0.0
    forms = [
        ("今のルール（同じ日の候補はランダムな順）", lambda: build()),
        ("① 50日線の傾きが小さい順", lambda: with_prio(build(), lambda b: f(b, "s50"))),
        ("② 20日線の傾きが小さい順", lambda: with_prio(build(), lambda b: f(b, "s20"))),
        ("③ 押し目・急落の底を先に（その中はランダム）、順張りは後", lambda: with_prio(build(), lambda b: 0 if b["rule"] in REV else 1)),
        ("④ 押し目・急落の底を先に50日線の傾きが小さい順、順張りは後に傾きが大きい順",
         lambda: with_prio(build(), lambda b: (0, f(b, "s50")) if b["rule"] in REV else (1, -f(b, "s50")))),
        ("⑤ 順張りを先に50日線の傾きが大きい順、押し目・急落の底は後に傾きが小さい順",
         lambda: with_prio(build(), lambda b: (1, f(b, "s50")) if b["rule"] in REV else (0, -f(b, "s50")))),
        ("⑥ 選ぶ: 順張りは50日線の傾きが大きい半分、押し目・急落の底は小さい半分だけ買う",
         lambda: build(drop=lambda b: (f(b, "s50") < mid[b["rule"]]) if b["rule"] not in REV else (f(b, "s50") >= mid[b["rule"]]))),
        ("⑦ 20日線からの乖離が小さい順（20日線より下に離れているほど先）", lambda: with_prio(build(), lambda b: f(b, "dev20"))),
        ("⑧ 直近5日の値動きが小さい順（5日で大きく下げたほど先）", lambda: with_prio(build(), lambda b: f(b, "r5"))),
        ("⑨ RSI(14)が低い順", lambda: with_prio(build(), lambda b: f(b, "rsi14"))),
    ]
    L = []
    w = L.append
    w(f"---\ntype: backtest\ntitle: 傾きの小さい順に買う形の確かめと似た案\ncreated: {dt.date.today()}\nscript: tools/backtest_retest.py --stage slope2\n---\n")
    w("# 傾きの小さい順に買う形の確かめ（年ごと・2倍ETF込み）と、似た案\n")
    w("2026-10-09、`傾きの大きさで選ぶ・優先する.md` で「同じ日の候補を傾きの小さい順に買う」が確かだったのを受けて、ユーザーの指示で確かめた。"
      "③は、効いているのが「傾き」なのか「逆張りの候補を先に買うこと」なのかを分けるための比べる形。後知恵なしの監視銘柄、2015年〜、4銘柄・1銘柄25%、片道0.1%込み。\n")
    w("## 1. 株だけで比べる\n")
    screen_and_confirm("候補の順番（株だけ）", forms[1:], w)
    # 2倍ETF込み（今の運用: 目減りが年15%未満の2倍ETFがある銘柄は2倍ETF）
    tab = json.load(open(os.path.join(os.path.dirname(OUTDIR.rstrip("/")), "2倍ETFの対応表.json"), encoding="utf-8"))
    drag = {u: -x["drag"] for u, x in tab.items() if isinstance(x, dict) and "drag" in x}
    HAS = {u for u, d in drag.items() if d < 0.15}

    def to2x(trs):
        out = []
        for t in trs:
            if t["sym"] not in HAS:
                out.append(t)
                continue
            fee = drag[t["sym"]] / 252
            e, prev, pv = 1 - COST, 1 - COST, {}
            for d in sorted(t["path"]):
                g_ = t["path"][d]
                e = max(0.0, e * (1 + 2 * (g_ / prev - 1)) * (1 - fee))
                prev = g_
                pv[d] = e
            out.append({**t, "path": pv})
        return out
    w(f"\n## 2. 2倍ETF込み（今の運用。目減りが年15%未満の2倍ETFがある{len(HAS)}銘柄は2倍ETF）\n")
    pick = [forms[0], forms[1], forms[2], forms[3], forms[4]]
    w("2倍ETF込みの今のルールと比べる（乱数50通り×2組の中央値。比べる元が株だけの表とは違うので、ふるいは使わない）。\n")
    w("| 形 | 1組目 年率 | 最大下落率 | 設計 | 確認 | 2組目 年率 | 最大下落率 | 設計 | 確認 |")
    w("|---|---|---|---|---|---|---|---|---|")
    for nm, fn in pick:
        trs = to2x(fn())
        e1, e2 = ev(trs, CONF1), ev(trs, CONF2)
        w(f"| {nm}（2倍ETF込み） | {pct(e1['all'])} | {pct(e1['mdd'])} | {pct(e1['is'])} | {pct(e1['oos'])} | {pct(e2['all'])} | {pct(e2['mdd'])} | {pct(e2['is'])} | {pct(e2['oos'])} |")
    # 年ごと（乱数50通りの中央値）
    w("\n## 3. 年ごとの成績（株だけ・乱数50通りの中央値）\n")
    yrs = sorted({d[:4] for d in days})
    rows = {}
    for nm, fn in pick:
        trs = fn()
        per = {y: [] for y in yrs}
        for k in range(50):
            curve = []
            port(trs, 5000 + k, days[0], days[-1], curve=curve)
            ends = {}
            for d, e in zip(days, curve):
                ends[d[:4]] = e
            prev = 1.0
            for y in yrs:
                if y in ends:
                    per[y].append(ends[y] / prev - 1)
                    prev = ends[y]
        rows[nm] = {y: med(v) for y, v in per.items() if v}
    w("| 年 | " + " | ".join(nm.split("（")[0] for nm, _ in pick) + " |")
    w("|---" * (len(pick) + 1) + "|")
    for y in yrs:
        w(f"| {y} | " + " | ".join(pct(rows[nm].get(y), 0) if rows[nm].get(y) is not None else "—" for nm, _ in pick) + " |")
    base_nm = pick[0][0]
    for nm, _ in pick[1:]:
        win = sum(1 for y in yrs if rows[nm].get(y) is not None and rows[base_nm].get(y) is not None and rows[nm][y] > rows[base_nm][y])
        w(f"\n- {nm.split('（')[0]}: 今のルールより良かった年 {win} / {len(yrs)}")
    w("\n- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(OUTDIR, exist_ok=True)
    open(OUTDIR + "傾きの小さい順に買う形の確かめと似た案.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("書き出し", file=sys.stderr)


def slope_stage(cur_tr, base, data, build, screen_and_confirm, is_hi):
    """傾き（角度）の大きさで合図を選ぶ・優先するか（2026-10-09 ユーザーの指示「傾きの角度が大きいほど値動きが大きい。うまく使って年率を上げられないか」）。
    傾きは合図の日（買う前の日）の値。選ぶ境目は、ルールごとに設計期間（2015〜2021年）の合図の中央値（確認期間の値は使わない）"""
    import math

    def sma(c, j, n):
        return sum(c[j - n + 1:j + 1]) / n if j >= n - 1 else None

    def reg(c, j, n=60):   # 直近n日の終値（対数）の回帰直線の傾き（年率）
        if j < n:
            return None
        ys = [math.log(x) for x in c[j - n + 1:j + 1]]
        xm, ym = (n - 1) / 2, sum(ys) / n
        b = sum((k - xm) * (y - ym) for k, y in enumerate(ys)) / sum((k - xm) ** 2 for k in range(n))
        return b * 252

    def bbup(c, j):
        def up(k):
            m = sma(c, k, 20)
            return m + 2 * (sum((x - m) ** 2 for x in c[k - 19:k + 1]) / 20) ** 0.5
        return up(j) / up(j - 5) - 1 if j >= 25 else None

    fns = {
        "50日線の傾き（20日前からの上昇率）": lambda c, j: (sma(c, j, 50) / sma(c, j - 20, 50) - 1) if j >= 70 else None,
        "20日線の傾き（10日前からの上昇率）": lambda c, j: (sma(c, j, 20) / sma(c, j - 10, 20) - 1) if j >= 30 else None,
        "ボリンジャーの上のバンドの傾き（5日前からの上昇率）": bbup,
        "トレンドライン（直近60日の回帰直線）の角度": reg,
    }
    names = {"V": "新高値V2", "M": "ミネルヴィニ", "B": "押し目", "C": "急落の底"}
    key = {(t["sym"], data[t["sym"]]["date"][t["i0"]], t["rule"]): t for t in base}
    val = {}
    for nm, f in fns.items():
        for t in base:
            val[(nm, id(t))] = f(data[t["sym"]]["c"], t["i0"] - 1)
    med = {}
    for nm in fns:
        for k in names:
            xs = sorted(v for t in base if t["rule"] == k and data[t["sym"]]["date"][t["i0"]] <= is_hi
                        for v in [val[(nm, id(t))]] if v is not None)
            med[(nm, k)] = xs[len(xs) // 2] if xs else 0.0
    L = []
    w = L.append
    w(f"---\ntype: backtest\ntitle: 傾きの大きさで選ぶ・優先する\ncreated: {dt.date.today()}\nscript: tools/backtest_retest.py --stage slope\n---\n")
    w("# 傾き（角度）の大きさで合図を選ぶ・優先する\n")
    w("2026-10-09、ユーザーの質問「トレンドライン・ローソク足・ボリンジャーバンドなどの傾きの角度が大きいほど値動きが大きく動く。うまく使って年率を上げられないか」から確かめた。"
      "傾きは合図の日（買う前の日）の値。「大きい半分」「小さい半分」の境目は、ルールごとに設計期間（2015〜2021年）の合図の中央値。"
      "後知恵なしの監視銘柄、2015年〜、今の売りのルール、4銘柄・1銘柄25%、株だけ、片道0.1%込み。\n")
    w("## 1. 傾きの大きさ別の1回ごとの成績（全部の合図）\n")
    avg = lambda xs: pct(sum(xs) / len(xs), 2) if xs else "—"
    for nm in fns:
        w(f"### {nm}\n")
        w("| ルール | 傾きが小さい半分: 回数・勝率・1回平均 | 傾きが大きい半分: 回数・勝率・1回平均 | 一番大きい20%: 1回平均 |")
        w("|---|---|---|---|")
        for k in ("V", "M", "B", "C"):
            lo, hi, rows = [], [], []
            for t in cur_tr:
                if t["rule"] != k:
                    continue
                b = key[(t["sym"], t["in"], t["rule"])]
                v = val[(nm, id(b))]
                if v is None:
                    continue
                r = t["path"][t["out"]] - 1
                rows.append((v, r))
                (hi if v >= med[(nm, k)] else lo).append(r)
            rows.sort()
            top = [r for _, r in rows[len(rows) * 4 // 5:]]
            f_ = lambda xs: f"{len(xs)}・{pct(sum(1 for x in xs if x > 0) / len(xs), 0)}・{avg(xs)}" if xs else "—"
            w(f"| {names[k]} | {f_(lo)} | {f_(hi)} | {avg(top)} |")
        w("")
    w("## 2. 資金全体（今の買い方と比べる）\n")
    items = []
    for nm in fns:
        get = lambda t, nm=nm: val.get((nm, id(t)))
        items.append((f"{nm}が大きい半分だけ買う",
                      (lambda nm=nm, get=get: build(drop=lambda t: get(t) is None or get(t) < med[(nm, t["rule"])]))))
        items.append((f"{nm}が小さい半分だけ買う",
                      (lambda nm=nm, get=get: build(drop=lambda t: get(t) is None or get(t) >= med[(nm, t["rule"])]))))

        def pr(sign, nm=nm, get=get):
            out = build()
            bmap = {(data[t["sym"]]["date"][t["i0"]], t["sym"], t["rule"]): t for t in base}
            res = []
            for t in out:
                v = get(bmap[(t["in"], t["sym"], t["rule"])])
                res.append({**t, "prio": sign * (v if v is not None else 0.0)})
            return res
        items.append((f"同じ日の候補を、{nm}が大きい順に買う", (lambda pr=pr: pr(-1))))
        items.append((f"同じ日の候補を、{nm}が小さい順に買う", (lambda pr=pr: pr(1))))
    screen_and_confirm("傾きの大きさで選ぶ・優先する", items, w)
    w("\n- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(OUTDIR, exist_ok=True)
    open(OUTDIR + "傾きの大きさで選ぶ・優先する.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("書き出し", file=sys.stderr)


def prio_stage(build, screen_and_confirm):
    """同じ日の候補を、ルールの期待値（1回平均）の高い順に買うか、ミネルヴィニを外すか（2026-10-09 ユーザーの指示。9/29は売りの改善前のルールで確かめた）"""
    ev_rank = {"V": 0, "C": 1, "B": 2, "M": 3}   # ルールごとの成績.md の1回平均の順（V 2.08%・C 2.07%・B 1.51%・M 0.07%）

    def ranked(trs):
        return [{**t, "prio": ev_rank[t["rule"]]} for t in trs]

    def rev(trs):   # 比べるため、逆の順（期待値の低い順）も
        return [{**t, "prio": 3 - ev_rank[t["rule"]]} for t in trs]
    items = [("同じ日の候補を、ルールの期待値の高い順に買う（新高値V2→急落の底→押し目→ミネルヴィニ）", lambda: ranked(build())),
             ("（比べるため）期待値の低い順に買う（ミネルヴィニ→押し目→急落の底→新高値V2）", lambda: rev(build())),
             ("ミネルヴィニを外す", lambda: build(drop=lambda t: t["rule"] == "M")),
             ("ミネルヴィニを外し、期待値の高い順に買う", lambda: ranked(build(drop=lambda t: t["rule"] == "M")))]
    L = []
    w = L.append
    w(f"---\ntype: backtest\ntitle: 期待値の高いルールを優先する・ミネルヴィニを外す（今のルール）\ncreated: {dt.date.today()}\nscript: tools/backtest_retest.py --stage prio\n---\n")
    w("# 期待値の高いルールを優先する・ミネルヴィニを外す（今のルールでのやり直し）\n")
    w("2026-10-09、ユーザーの質問「期待値が高い銘柄を優先的に買えば成績が良くなるのでは」から、今のルール（売りの改善後）で確かめ直した。"
      "今のルールの比べる元は、同じ日の候補をランダムな順に買う形（乱数で何通りも試す）。9/29に売りの改善前のルールで試したときは、どの順でも差はランダムの幅の中だった（`ミネルヴィニを外す確認と優先順位.md`）。"
      "後知恵なしの監視銘柄、2015年〜、4銘柄・1銘柄25%、株だけ、片道0.1%込み。\n")
    screen_and_confirm("候補の優先順位とミネルヴィニ", items, w)
    w("\n- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(OUTDIR, exist_ok=True)
    open(OUTDIR + "期待値の高いルールを優先する・ミネルヴィニを外す.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("書き出し", file=sys.stderr)


def recover_stage(cur_tr):
    """買った後に買値を下回った売買が、何日後に買値まで戻ったか（2026-10-08 ユーザーの質問「下がった後、大体何日後に上がっているか」）"""
    names = {"V": "新高値V2", "M": "ミネルヴィニ", "B": "押し目（ボリンジャーIII）", "C": "急落の底"}
    med = lambda xs: sorted(xs)[len(xs) // 2] if xs else None
    L = []
    w = L.append
    w(f"---\ntype: backtest\ntitle: 下がった後に買値まで戻るまでの日数\ncreated: {dt.date.today()}\nscript: tools/backtest_retest.py --stage recover\n---\n")
    w("# 買った後に下がった売買は、何日後に買値まで戻ったか\n")
    w("後知恵なしの監視銘柄、2015年〜、今の売りのルール、片道0.1%込み。ルールの全部の合図の1回ごと。日数は取引日（土日・祝日を除く。20取引日≒1か月）。"
      "「下がった」＝保有中の引け値が一度でも買値の97%以下（-3%以下）になった売買。「戻った」＝その後、売る前に引け値が買値以上に戻った。\n")
    w("| ルール | 合図の数 | -3%以下に下がった | そのうち売る前に買値まで戻った | 戻るまでの日数（中央値／4分の3が戻るまで） | 戻らずに売った（その平均の損益） | 一番下がるまでの日数（中央値） |")
    w("|---|---|---|---|---|---|---|")
    for k in ("V", "M", "B", "C"):
        ts = [t for t in cur_tr if t["rule"] == k]
        dip, rec_days, norec, bottom = 0, [], [], []
        for t in ts:
            ds = sorted(d for d in t["path"] if d <= t["out"])
            v = [t["path"][d] for d in ds]
            first = next((i for i, x in enumerate(v) if x <= 0.97), None)
            if first is None:
                continue
            dip += 1
            bottom.append(min(range(len(v)), key=lambda i: v[i]))
            back = next((i for i in range(first + 1, len(v) - 1) if v[i] >= 1.0), None)
            if back is None:
                norec.append(v[-1] - 1)
            else:
                rec_days.append(back - first)
        q3 = sorted(rec_days)[len(rec_days) * 3 // 4] if rec_days else None
        w(f"| {names[k]} | {len(ts)} | {dip}（{pct(dip / len(ts), 0)}） | {len(rec_days)}（{pct(len(rec_days) / dip, 0) if dip else '—'}） | "
          f"{med(rec_days)}日／{q3}日 | {len(norec)}（{pct(sum(norec) / len(norec), 1) if norec else '—'}） | {med(bottom)}日 |")
    w("\n- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(OUTDIR, exist_ok=True)
    open(OUTDIR + "下がった後に買値まで戻るまでの日数.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("書き出し", file=sys.stderr)


def pullback_stage(cur_tr, base, data, build, screen_and_confirm, rec, idx):
    """新高値V2の合図の後、すぐ買わずに、ピボット（抜けた高値）近くまで下がるのを待って指値で買うか（2026-10-08 ユーザーの指示）。
    指値は合図の翌日から毎晩置き直し、待つ日数のうちに届かなければ見送る。手じまいは今と同じ（引けで50日線割れ・引けで買値の15%下→翌日の寄り付き、かぶせ線・半分売り）"""
    def trig(t):
        s, j = data[t["sym"]], t["i0"] - 1
        return max(max(s["c"][max(0, j - 20):j]), max(s["h"][max(0, j - 500):j]))

    def wait_trades(above, days):
        out, info = [], {"signals": 0, "filled": 0, "miss": []}
        vb = [t for t in base if t["rule"] == "V"]
        cur = {(t["sym"], t["in"]): t for t in cur_tr if t["rule"] == "V"}
        for t in vb:
            s, sym = data[t["sym"]], t["sym"]
            o, l, c, n = s["o"], s["l"], s["c"], len(s["c"])
            lim = trig(t) * (1 + above)
            info["signals"] += 1
            k = next((k for k in range(t["i0"], min(n - 1, t["i0"] + days)) if l[k] <= lim), None)
            if k is None:
                ct = cur.get((sym, s["date"][t["i0"]]))
                if ct:
                    info["miss"].append(ct["path"][ct["out"]] - 1)
                continue
            px = min(o[k], lim)
            floor, j = px * (1 - STOP), None
            for jj in range(k, n - 1):
                if c[jj] <= floor or (s["ma50"][jj] is not None and c[jj] < s["ma50"][jj]):
                    j = jj
                    break
            if j is None:
                continue
            info["filled"] += 1
            out.append({**rec(sym, k, j + 1, px, o[j + 1], "V"), "pb": True})   # 待って買った売買（drop で今の買い方の分だけ外すための印）
        return out, info

    L = []
    w = L.append
    w(f"---\ntype: backtest\ntitle: 新高値V2で下がるのを待って買う\ncreated: {dt.date.today()}\nscript: tools/backtest_retest.py --stage pullback\n---\n")
    w("# 新高値V2の合図の後、ピボット近くまで下がるのを待って買う\n")
    w("2026-10-08、ユーザーの質問「損で終わる方が多い（下がる）なら、下がった時に買った方が効率が良いのでは」から確かめた。"
      "今は合図の翌日の寄り付き（または逆指値）で買う。比べる形は、合図の後、ピボット（直前20日の最高値（終値）と直前2年の最高値の高い方）"
      "の近くに指値の買いを置き、決めた日数のうちに届いたら買い、届かなければ見送る。手じまいは今と同じ。後知恵なしの監視銘柄、2015年〜、片道0.1%込み。\n")
    combos = [(0.0, 10), (0.0, 20), (0.02, 10), (0.02, 20), (0.05, 10)]
    w("## 1. 1回ごとの成績（新高値V2の全部の合図）\n")
    r0 = [t["path"][t["out"]] - 1 for t in cur_tr if t["rule"] == "V"]
    avg = lambda xs: pct(sum(xs) / len(xs), 2) if xs else "—"
    w(f"今の買い方（合図の翌日に買う）: {len(r0)}回、勝率 {pct(sum(1 for x in r0 if x > 0) / len(r0), 0)}、1回平均 {avg(r0)}\n")
    w("| 待つ形 | 買えた回数（合図に対する割合） | 勝率 | 1回平均 | 買えなかった合図を今の買い方で買った場合の1回平均 |")
    w("|---|---|---|---|---|")
    items = []
    for above, days in combos:
        tr, info = wait_trades(above, days)
        lab = f"ピボット{'+' + str(int(above * 100)) + '%' if above else ''}まで下がったら買う（{days}日待つ）"
        built = build(drop=lambda t: t["rule"] == "V" and not t.get("pb"), add=tr)
        rr = [t["path"][t["out"]] - 1 for t in built if t["rule"] == "V"]
        w(f"| {lab} | {len(rr)}（{pct(len(rr) / info['signals'], 0)}） | {pct(sum(1 for x in rr if x > 0) / len(rr), 0) if rr else '—'} | {avg(rr)} | {avg(info['miss'])}（{len(info['miss'])}回） |")
        items.append((lab, (lambda tr=tr: build(drop=lambda t: t["rule"] == "V" and not t.get("pb"), add=tr))))
    w("")
    w("## 2. 資金全体（今の買い方と比べる）\n")
    screen_and_confirm("新高値V2で下がるのを待って買う", items, w)
    w("\n- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(OUTDIR, exist_ok=True)
    open(OUTDIR + "新高値V2で下がるのを待って買う.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("書き出し", file=sys.stderr)


def exits_stage(cur_tr):
    """ルールごとに、損で終わった売買のうち損切り（買値の15%下）まで行った回数と割合（2026-10-08 ユーザーの質問）"""
    names = {"V": "新高値V2", "M": "ミネルヴィニ（ベースの上抜け）", "B": "押し目（ボリンジャーIII）", "C": "急落の底"}
    yrs = 11.7
    L = []
    w = L.append
    w(f"---\ntype: backtest\ntitle: 損切りまで行った回数\ncreated: {dt.date.today()}\nscript: tools/backtest_retest.py --stage exits\n---\n")
    w("# 損切り（買値の15%下）まで行った回数と、損で終わった売買の内訳\n")
    w("後知恵なしの監視銘柄、2015年〜（約11.7年）、今の売りのルール、片道0.1%込み。ルールの全部の合図の1回ごと（資金の枠に入らなかった合図も含む）。"
      "1回の損益が-14%以下を「損切りまで行った」とした（損切り15%に、手数料と、損切り前に半分売った分のずれを見込んだ近似。窓を開けて15%より大きく下げた回も入る）。\n")
    w("| ルール | 合図の数 | 勝ち | 損で終わった | 0〜-5% | -5〜-10% | -10〜-14% | **損切りまで（-14%以下）** | 損切りの割合（全部の売買に対して） | 損の合計のうち損切りの分 |")
    w("|---|---|---|---|---|---|---|---|---|---|")
    for k in ("V", "M", "B", "C"):
        r = [t["path"][t["out"]] - 1 for t in cur_tr if t["rule"] == k]
        if not r:
            continue
        lose = [x for x in r if x <= 0]
        b1 = sum(1 for x in lose if x > -0.05)
        b2 = sum(1 for x in lose if -0.10 < x <= -0.05)
        b3 = sum(1 for x in lose if -0.14 < x <= -0.10)
        st = [x for x in lose if x <= -0.14]
        w(f"| {names[k]} | {len(r)}（年{len(r) / yrs:.0f}回） | {len(r) - len(lose)}（{pct((len(r) - len(lose)) / len(r), 0)}） | {len(lose)}（{pct(len(lose) / len(r), 0)}） | "
          f"{b1} | {b2} | {b3} | **{len(st)}（年{len(st) / yrs:.1f}回）** | {pct(len(st) / len(r), 0)} | {pct(sum(st) / sum(lose), 0) if lose else '—'} |")
    w("\n- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(OUTDIR, exist_ok=True)
    open(OUTDIR + "損切りまで行った回数.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("書き出し", file=sys.stderr)


def pivot_stage(cur_tr, base, data, build, screen_and_confirm):
    """新高値V2で、ピボット（直前20日の最高値（終値）と直前2年の最高値の高い方）から離れすぎた買いを見送るか
    （2026-10-05 ミネルヴィニがHPEを「ピボット67.10から+3.3%の高値追い（第10章）」で【様子見】にしたため。ユーザーの指示）"""
    def trig(t):
        s, j = data[t["sym"]], t["i0"] - 1
        return max(max(s["c"][max(0, j - 20):j]), max(s["h"][max(0, j - 500):j]))
    vb = [t for t in base if t["rule"] == "V"]
    key = {(t["sym"], data[t["sym"]]["date"][t["i0"]]): t for t in vb}
    L = []
    w = L.append
    w(f"---\ntype: backtest\ntitle: 新高値V2でピボットから離れた買いを見送るか\ncreated: {dt.date.today()}\nscript: tools/backtest_retest.py --stage pivot\n---\n")
    w("# 新高値V2で、ピボットから離れすぎた買いを見送るか\n")
    w("2026-10-05、ミネルヴィニがHPE（新高値V2、10/2の終値69.33）を「ピボット67.10から+3.3%の高値追い（第10章）」で【様子見】にした。"
      "前日（10/4）の同じデータでは【買い】だった。ルールにこの見送りを入れた方が良いかを確かめた。"
      "ピボット＝直前20日の最高値（終値）と直前2年の最高値（高値）の高い方（毎朝のツールの逆指値の価格と同じ）。後知恵なしの監視銘柄、2015年〜、今の売りのルール、片道0.1%込み。\n")
    w("## 1. ピボットからの離れ具合ごとの成績（新高値V2の全部の合図、1回ごと）\n")
    for basis, f in (("合図の日の終値", lambda t, b: data[t["sym"]]["c"][b["i0"] - 1]), ("買った値段（翌日の寄り付き）", lambda t, b: b["px"])):
        w(f"### {basis}がピボットから何%上か\n")
        w("| 離れ具合 | 回数 | 勝率 | 1回平均 | 設計／確認の1回平均 |")
        w("|---|---|---|---|---|")
        bins = (("+1%未満", -1, 0.01), ("+1〜2%", 0.01, 0.02), ("+2〜3%", 0.02, 0.03), ("+3〜5%", 0.03, 0.05), ("+5%以上", 0.05, 9))
        for lab, lo, hi in bins:
            g = []
            for t in cur_tr:
                if t["rule"] != "V":
                    continue
                b = key[(t["sym"], t["in"])]
                x = f(t, b) / trig(b) - 1
                if lo <= x < hi:
                    g.append(t)
            if not g:
                continue
            r = [t["path"][t["out"]] - 1 for t in g]
            de = [t["path"][t["out"]] - 1 for t in g if t["in"] <= cb.IS_END]
            co = [t["path"][t["out"]] - 1 for t in g if t["in"] >= cb.OOS_START]
            avg = lambda xs: pct(sum(xs) / len(xs), 2) if xs else "—"
            w(f"| {lab} | {len(g)} | {pct(sum(1 for x in r if x > 0) / len(r), 0)} | {avg(r)} | {avg(de)}／{avg(co)} |")
        w("")
    w("## 2. 見送りをルールに入れて、資金全体で試す（今のルールと比べる）\n")
    items = []
    for lim in (0.03, 0.05):
        items.append((f"合図の日の終値がピボット+{lim * 100:.0f}%を超えたら見送り",
                      (lambda lim=lim: build(drop=lambda t: t["rule"] == "V" and data[t["sym"]]["c"][t["i0"] - 1] > trig(t) * (1 + lim)))))
        items.append((f"翌日の寄り付きがピボット+{lim * 100:.0f}%を超えたら見送り",
                      (lambda lim=lim: build(drop=lambda t: t["rule"] == "V" and t["px"] > trig(t) * (1 + lim)))))
    screen_and_confirm("新高値V2で、ピボットから離れた買いを見送る", items, w)
    w("\n- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(OUTDIR, exist_ok=True)
    open(OUTDIR + "新高値V2でピボットから離れた買いを見送るか.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("書き出し", file=sys.stderr)


def rsi_wilder(c, n):
    """終値の列からワイルダーのRSI(n)を作る（moomooの既定はRSI 6/12/24）"""
    out = [None] * len(c)
    if len(c) <= n:
        return out
    g = [max(c[k] - c[k - 1], 0) for k in range(1, len(c))]
    d = [max(c[k - 1] - c[k], 0) for k in range(1, len(c))]
    ag, ad = sum(g[:n]) / n, sum(d[:n]) / n
    for k in range(n, len(c)):
        if k > n:
            ag = (ag * (n - 1) + g[k - 1]) / n
            ad = (ad * (n - 1) + d[k - 1]) / n
        out[k] = 100.0 if ad == 0 else 100 - 100 / (1 + ag / ad)
    return out


def rsi_stage(cur_tr, base, data, build, ev, CUR, screen_and_confirm, TREND, REV):
    """買う前の日（合図の日）のRSIが80を超えていた売買は、成績が悪いのか（2026-10-04 ユーザーの質問。HPEのRSI(6)が81.6）"""
    for sym in {t["sym"] for t in base}:
        s = data[sym]
        for n in (6, 14):
            if f"rsi{n}" not in s:
                s[f"rsi{n}"] = rsi_wilder(s["c"], n)
    key = {(t["sym"], data[t["sym"]]["date"][t["i0"]], t["rule"]): t for t in base}
    names = {"B": "押し目", "C": "急落の底", "M": "ミネルヴィニ", "V": "新高値V2"}
    is_hi, oos_lo = cb.IS_END, cb.OOS_START

    def rsi_at(t, n):
        b = key[(t["sym"], t["in"], t["rule"])]
        return data[t["sym"]][f"rsi{n}"][b["i0"] - 1]

    L = []
    w = L.append
    w(f"---\ntype: backtest\ntitle: 買う日のRSIが80を超えていたとき\ncreated: {dt.date.today()}\nscript: tools/backtest_retest.py --stage rsi\n---\n")
    w("# 買う日のRSIが80を超えていたとき（過熱して見える日に買った成績）\n")
    w("2026-10-04、HPE（新高値V2で【買い】、合図の日のRSI(6) 81.6）について、ユーザーから「RSIが80を超えていて、すぐ下がりそう。バックテストでは下がってもまた上がる方が多いのか」と質問があり、確かめた。")
    w("RSIは合図の日（買う前の日）の終値で計算（ワイルダー方式。moomooの既定のRSI 6/12/24と同じ計算）。後知恵なしの監視銘柄、2015年〜、今の売りのルール、片道0.1%込み。\n")
    for n in (6, 14):
        w(f"## 1. ルールごと・RSI({n})の高さ別の成績（全部の合図、1回ごと）\n")
        w("| ルール | RSI | 回数 | 勝率 | 1回平均 | 設計／確認の1回平均 | 途中で買値から5%以上下げた割合 | そのうち最後は勝った割合 |")
        w("|---|---|---|---|---|---|---|---|")
        for k in ("V", "M", "B", "C"):
            ts = [t for t in cur_tr if t["rule"] == k and rsi_at(t, n) is not None]
            for lab, f in ((f"{n}: 70未満", lambda x: x < 70), ("70〜80", lambda x: 70 <= x < 80), ("80以上", lambda x: x >= 80)):
                g = [t for t in ts if f(rsi_at(t, n))]
                if not g:
                    continue
                r = [t["path"][t["out"]] - 1 for t in g]
                de = [t["path"][t["out"]] - 1 for t in g if t["in"] <= is_hi]
                co = [t["path"][t["out"]] - 1 for t in g if t["in"] >= oos_lo]
                dip = [t for t in g if min(t["path"].values()) <= 0.95]
                dip_win = [t for t in dip if t["path"][t["out"]] > 1]
                avg = lambda xs: pct(sum(xs) / len(xs), 2) if xs else "—"
                w(f"| {names[k]} | {lab.split(': ')[-1]} | {len(g)} | {pct(sum(1 for x in r if x > 0) / len(r), 0)} | {avg(r)} | {avg(de)}／{avg(co)} | "
                  f"{pct(len(dip) / len(g), 0)} | {pct(len(dip_win) / len(dip), 0) if dip else '—'} |")
        w("")
    w("「途中で買値から5%以上下げた」は、保有中の終値ベースの値（半分売った後は残りの分も含めた資金の値）が、一度でも買値の95%以下になった売買。\n")
    w("## 2. RSIが80以上の日は買わない、を資金全体で試す（今のルールと比べる）\n")
    items = []
    for n in (6, 14):
        for rl, lab in ((TREND, "順張り（ミネルヴィニ・新高値V2）"), (TREND + REV, "全部のルール")):
            items.append((f"{lab}で、合図の日のRSI({n})が80以上なら買わない",
                          (lambda n=n, rl=rl: build(drop=lambda t: t["rule"] in rl and data[t["sym"]][f"rsi{n}"][t["i0"] - 1] is not None
                                                     and data[t["sym"]][f"rsi{n}"][t["i0"] - 1] >= 80))))
    screen_and_confirm("RSIが80以上なら買わない", items, w)
    w("\n- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    os.makedirs(OUTDIR, exist_ok=True)
    open(OUTDIR + "買う日のRSIが80を超えていたとき.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("書き出し", file=sys.stderr)


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


def robust(stage, data, base, build, port, ev, CUR, CONF, days, is_hi, oos_lo, sim, TREND, REV, safe):
    """Geminiの指摘に応える頑健さの確認（2026-10-03）: 1 取引コスト 2 モンテカルロ 3 年ごと・ウォークフォワード 4 生存者バイアス ／ earn: 5 決算"""
    import json
    import math
    g = globals()
    L = []
    w = L.append
    years = sorted({d[:4] for d in days})
    yrs_all = (dt.date.fromisoformat(days[-1]) - dt.date.fromisoformat(days[0])).days / 365.25
    S0, NS = CONF
    if stage == "earn":
        return earnings_stage(data, base, build, ev, CUR, CONF, safe)

    def curves(trs):
        out = []
        for k in range(NS):
            c = []
            port(trs, S0 + k, days[0], days[-1], curve=c)
            out.append(c)
        return out

    def yearly(cs):
        di = {d: k for k, d in enumerate(days)}
        res = {}
        for y in years:
            ks = [di[d] for d in days if d[:4] == y]
            vals = sorted(c[ks[-1]] / (c[ks[0] - 1] if ks[0] > 0 else 1.0) - 1 for c in cs)
            res[y] = (vals[len(vals) // 2], vals[0], vals[-1])
        return res

    w(f"---\ntype: backtest\ntitle: 頑健さの確認（コスト・モンテカルロ・年ごと・生存者バイアス）\ncreated: {dt.date.today()}\nscript: tools/backtest_retest.py --stage robust\n---\n")
    w("# 頑健さの確認（Geminiの第三者検証の指摘に応える）\n")
    w("Gemini ディープリサーチの検証（2026-10-03）で勧められた追加の検証。土台は今のルール（2026-10-02 時点）。乱数50通り。\n")

    # ---- 1. 取引コスト ----
    w("## 1. 取引コスト（片道）を上げたらどうなるか\n")
    w("| 片道のコスト | 年率 | 最大下落率 | 設計期間 | 確認期間 |")
    w("|---|---|---|---|---|")
    old = g["COST"]
    be = None
    try:
        for c_ in (0.001, 0.002, 0.003, 0.005, 0.0075, 0.01, 0.015):
            g["COST"] = c_
            e = ev(build(), CONF)
            w(f"| {c_ * 100:.2f}% | {pct(e['all'])} | {pct(e['mdd'])} | {pct(e['is'])} | {pct(e['oos'])} |")
            if be is None and e["is"] <= 0:
                be = c_
            print("コスト", c_, file=sys.stderr)
    finally:
        g["COST"] = old
    w(f"\n設計期間（2015〜2021年）の年率が0以下になる片道コスト: {'1.5%でもプラス' if be is None else f'{be * 100:.2f}%'}。"
      "片道0.1%は、手数料0〜0.05%＋値段のずれ（スリッページ）を見込んだ仮定。\n")

    # ---- 2. モンテカルロ ----
    base_tr = build()
    cs = curves(base_tr)
    rets = [[c[i] / (c[i - 1] if i else 1.0) - 1 for i in range(len(c))] for c in cs]
    n, B, R = len(days), 20, random.Random(42)
    sims = []
    for _ in range(10000):
        r_ = rets[R.randrange(NS)]
        eq, pk, mdd, k = 1.0, 1.0, 0.0, 0
        while k < n:
            st = R.randrange(0, n - B)
            for x in r_[st:st + B]:
                eq *= 1 + x
                pk = max(pk, eq)
                mdd = max(mdd, 1 - eq / pk)
            k += B
        sims.append((eq ** (1 / yrs_all) - 1, mdd))
    ca = sorted(x[0] for x in sims)
    md = sorted(x[1] for x in sims)
    q = lambda v, p: v[min(len(v) - 1, int(len(v) * p))]
    w("## 2. モンテカルロ（日々の損益の順番をばらばらにして10,000通りの11.7年を作る）\n")
    w("今のルールの資金の推移（乱数50通り）から、20日ずつのかたまりを、ランダムに選んでつなぎ直した（ブロック・ブートストラップ）。"
      "連敗の続き方・大きな下げの重なり方が変わったとき、年率と最大下落率がどこまでぶれるかを見る。\n")
    w("| | 5%の確率でこれより悪い | 中央値 | 5%の確率でこれより良い |")
    w("|---|---|---|---|")
    w(f"| 年率 | {pct(q(ca, 0.05))} | {pct(q(ca, 0.5))} | {pct(q(ca, 0.95))} |")
    w(f"| 最大下落率 | {pct(q(md, 0.95))} | {pct(q(md, 0.5))} | {pct(q(md, 0.05))} |")
    w("")
    for th in (0.3, 0.4, 0.5, 0.6):
        w(f"- 最大下落率が{int(th * 100)}%を超える確率: {pct(sum(1 for x in md if x > th) / len(md), 1)}")
    w(f"- 11.7年の年率がマイナスになる確率: {pct(sum(1 for x in ca if x < 0) / len(ca), 1)}")
    w(f"- 年率が10%に届かない確率: {pct(sum(1 for x in ca if x < 0.10) / len(ca), 1)}\n")
    print("モンテカルロ", file=sys.stderr)

    # ---- 3. 年ごと・ウォークフォワード ----
    yr = yearly(cs)
    w("## 3-1. 年ごとの成績（乱数50通りの中央値と、一番悪い・良い通り）\n")
    w("| 年 | 中央値 | 一番悪い通り | 一番良い通り |")
    w("|---|---|---|---|")
    for y in years:
        m_, lo_, hi_ = yr[y]
        w(f"| {y}{'（9月まで）' if y == years[-1] else ''} | {pct(m_, 0)} | {pct(lo_, 0)} | {pct(hi_, 0)} |")
    neg = [y for y in years if yr[y][0] < 0]
    w(f"\nマイナスの年（中央値）: {'、'.join(neg) if neg else 'なし'}。\n")
    roll = []
    for k in range(len(years) - 3):
        g3 = 1.0
        for y in years[k:k + 3]:
            g3 *= 1 + yr[y][0]
        roll.append((f"{years[k]}〜{years[k + 2]}", g3 ** (1 / 3) - 1))
    w("3年ずつの年率（中央値の年の成績をつないだもの）: " + "、".join(f"{a_} {pct(b_, 0)}" for a_, b_ in roll) + "\n")

    variants = [("今のルール", {}), ("かぶせ線なし", {"full_dc": False}), ("半分売りなし", {"half": None}),
                ("大陰線なし", {"bear_rev": False}), ("3つともなし（10-01より前の売り）", {"full_dc": False, "half": None, "bear_rev": False})]
    vy = {}
    for lab, kw in variants:
        vy[lab] = yearly(curves(build(**kw)))
        print("ウォークフォワード", lab, file=sys.stderr)
    w("## 3-2. ウォークフォワード（その時点で分かっていた成績だけで、売りの改善を使うかを毎年選び直す）\n")
    w("毎年の初めに、直前3年の成績が一番良かった形（今のルール／かぶせ線なし／半分売りなし／大陰線なし／3つともなし）を選び、その年に使う。"
      "後から見て一番良い形を選ぶのではなく、その時点で選べた形の成績になる。\n")
    w("| 年 | 選ばれた形（直前3年で一番） | その年の成績 | 今のルールのその年の成績 |")
    w("|---|---|---|---|")
    wf, cur_g, chosen = 1.0, 1.0, {}
    for k, y in enumerate(years):
        if k < 3:
            continue
        best = max(vy, key=lambda lb: math.prod(1 + vy[lb][yy][0] for yy in years[k - 3:k]))
        chosen[best] = chosen.get(best, 0) + 1
        r1, r0 = vy[best][y][0], vy["今のルール"][y][0]
        wf *= 1 + r1
        cur_g *= 1 + r0
        w(f"| {y} | {best} | {pct(r1, 0)} | {pct(r0, 0)} |")
    span = (dt.date.fromisoformat(days[-1]) - dt.date.fromisoformat(f"{years[3]}-01-01")).days / 365.25
    w(f"\n{years[3]}年〜の年率: ウォークフォワード {pct(wf ** (1 / span) - 1)}、今のルールをずっと使う {pct(cur_g ** (1 / span) - 1)}。"
      "選ばれた回数: " + "、".join(f"{a_} {b_}回" for a_, b_ in chosen.items()) + "\n")
    w("各形の年ごとの成績（中央値）:\n")
    w("| 形 | " + " | ".join(years) + " |")
    w("|---|" + "---|" * len(years))
    for lab, _ in variants:
        w(f"| {lab} | " + " | ".join(pct(vy[lab][y][0], 0) for y in years) + " |")

    # ---- 4. 生存者バイアス ----
    w("\n## 4. 生存者バイアス\n")
    w("過去のS&P500構成銘柄のうち、Yahooから株価が取れない約150銘柄の多くは、買収（買収価格で上場廃止。損は小さい）か、ティッカーの変更（新しいティッカーでデータがある。例: ABC→COR、ANTM→ELV）。"
      "Claudeの知識で、構成銘柄の期間（2015年〜）に倒産・株価の崩壊があった銘柄を挙げると: SVB（SIVB、2023年3月）、シグネチャー銀行（SBNY、2023年3月）、ファースト・リパブリック（FRC、2023年5月）、"
      "エンド（ENDP）、マリンクロット（MNK）、フロンティア（FTR）、チェサピーク（CHK）、ダイヤモンド・オフショア（DO）、サウスウエスタン（SWN）、ウィンドストリーム（WIN）、デンベリー（DNR）など。"
      "このうち **FRC（OTCのFRCBの株価）とセンチュリーリンク（CTL、今のLUMEN）は、2026-10-03に株価を取れたのでデータに加えた**。ほかは取れない。\n")
    fx = [t for t in base_tr if t["sym"] in ("FRC", "CTL")]
    w(f"- 加えたFRC・CTLの合図: {len(fx)}件" + ("（" + "、".join(f"{t['sym']} {t['in']}〜{t['out']} {pct(t['path'][t['out']] - 1, 1)}" for t in fx[:10]) + "）" if fx else "") + "。")
    e_with = CUR[CONF]
    e_wo = ev(build(drop=lambda t: t["sym"] in ("FRC", "CTL")), CONF)
    w(f"- FRC・CTLを入れた年率 {pct(e_with['all'])}（最大下落率 {pct(e_with['mdd'])}）、入れない年率 {pct(e_wo['all'])}（{pct(e_wo['mdd'])}）。\n")
    w("**取れない倒産銘柄の影響の見積もり（ストレステスト）**: 倒産で1枠（資金の25%）を丸ごと失う出来事が、11.7年の間にランダムな日に起きたとしたら。"
      "実際には損切り（買値の15%下）があるので、丸ごと失うのは、取引が止まって売れない場合（2023年のSVB・シグネチャー銀行）だけ。\n")
    w("| 1枠を丸ごと失う回数 | 年率 | 最大下落率 |")
    w("|---|---|---|")
    R2 = random.Random(7)
    for kk in (0, 1, 2, 3):
        cag, mds = [], []
        for c in cs:
            hits = sorted(R2.randrange(len(c)) for _ in range(kk))
            eq_, pk, md_, f = 1.0, 1.0, 0.0, 1.0
            for i, v in enumerate(c):
                while hits and hits[0] == i:
                    f *= 0.75
                    hits.pop(0)
                eq_ = v * f
                pk = max(pk, eq_)
                md_ = max(md_, 1 - eq_ / pk)
            cag.append(eq_ ** (1 / yrs_all) - 1)
            mds.append(md_)
        w(f"| {kk}回 | {pct(sorted(cag)[len(cag) // 2])} | {pct(sorted(mds)[len(mds) // 2])} |")
    w("\n- 2023年の銀行の破綻（SVB・シグネチャー・FRC）は、どれも2022年から株価が大きく下がり（RSが低く、30週線も下向き）、後知恵なしの監視銘柄の条件（RS≧90・上昇トレンド）から外れていた可能性が高い（FRCはデータで確認できる）。"
      "2015〜2017年の製薬・エネルギーの崩壊（ENDP・MNK・CHKなど）も、崩壊の前から下げていた銘柄が多い。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    open(OUTDIR + "頑健さの確認.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("書き出し: 頑健さの確認.md", file=sys.stderr)


def etf2x_stage(build, port, ev, CUR, SEEDSETS, days, is_hi, oos_lo, only_set=None, tag="", drag=None):
    """2倍ETFがある銘柄だけ2倍ETFにした場合（今のルール、2026-10-03）。株の値動きの2倍で再現（毎日合わせ直し、経費 年1%、0より下にならない）"""
    import backtest_2x as b2
    import json
    meas = {}
    if drag == "measured":
        meas = {u: -x["drag"] for u, x in json.load(open(os.path.join(os.path.dirname(OUTDIR.rstrip("/")), "2倍ETFの対応表.json"), encoding="utf-8")).items()}
    dflt = 0.01 if drag is None else 0.12 if drag == "measured" else float(drag)
    fee_of = lambda sym: meas.get(sym, dflt) / 252

    def to2x(trs, only):
        out = []
        for t in trs:
            if only is not None and t["sym"] not in only:
                out.append(t)
                continue
            ds = sorted(t["path"])
            e, prev, pv = 1 - COST, 1 - COST, {}
            FEE = fee_of(t["sym"])
            for d in ds:
                g_ = t["path"][d]
                e = max(0.0, e * (1 + 2 * (g_ / prev - 1)) * (1 - FEE))
                prev = g_
                pv[d] = e
            out.append({**t, "path": pv})
        return out

    HAS = only_set or b2.HAS_2X
    base = build()
    forms = [("株（今のルール）", base), (f"2倍ETFがある銘柄（{len(HAS)}銘柄{'・' + tag if tag else ''}）だけ2倍ETF、ほかは株", to2x(base, HAS)),
             ("（参考）全部の銘柄を2倍ETF", to2x(base, None))]
    n_etf = sum(1 for t in base if t["sym"] in HAS)
    yrs = (dt.date.fromisoformat(days[-1]) - dt.date.fromisoformat(days[0])).days / 365.25
    years = sorted({d[:4] for d in days})
    di = {d: k for k, d in enumerate(days)}
    L = []
    w = L.append
    w(f"---\ntype: backtest\ntitle: 2倍ETFがある銘柄だけ2倍ETFにする（今のルール{'・' + tag if tag else ''}）\ncreated: {dt.date.today()}\nscript: tools/backtest_retest.py --stage etf2x\n---\n")
    w(f"# 2倍ETFがある銘柄だけ2倍ETFにする（今のルール{'・' + tag if tag else ''}）\n")
    w("買い・売りの合図と日付は今のルールのまま（元の株で判定）。2倍ETFがある銘柄（Claudeが把握している2026年時点の個別株2倍ETFの対象: "
      + "・".join(sorted(HAS)) + "。実際に買えるかは証券会社で確認が必要）だけ、株の代わりに2倍ETFを持つ。"
      f"2倍ETFは元の株の日々の値動きの2倍で再現（毎日合わせ直し、0より下にならない）。目減り（経費・借入のコストなど）は{'直近1年の実測（`個別株2倍ETFの比べ方.md`、ないものは年12%）' if meas else f'年{dflt * 100:.0f}%'}。損切りは株の15%下のまま（ETFでは約30%下）。"
      f"1枠は資金の25%。全部の合図 {len(base)}件のうち、2倍ETFがある銘柄の合図は {n_etf}件。片道0.1%。\n")
    w("## 1. 乱数3組の結果（含み損を入れた最大下落率）\n")
    w("| 形 | 組 | 年率 | 最大下落率 | 設計期間 | 確認期間 |")
    w("|---|---|---|---|---|---|")
    res = {}
    for lab, trs in forms:
        for sd in SEEDSETS:
            e = ev(trs, sd)
            res[(lab, sd)] = e
            w(f"| {lab} | {sd[0]}番台・{sd[1]}通り | {pct(e['all'])} | {pct(e['mdd'])} | {pct(e['is'])} | {pct(e['oos'])} |")
        print("ETF", lab, file=sys.stderr)
    w("\n## 2. 確定した損益だけの最大下落率・年ごとの成績・モンテカルロ（乱数50通り）\n")
    S0, NS = SEEDSETS[1]
    w("| 形 | 確定した損益だけの最大下落率（中央値／最悪） | 含み損込み（中央値／最悪） | 一番悪い年 | 2022年 | モンテカルロ 年率の悪い方5% | 最大下落率が50%を超える確率 | 60%を超える確率 |")
    w("|---|---|---|---|---|---|---|---|")
    ytab = {}
    for lab, trs in forms:
        rm, mm, cs = [], [], []
        for k in range(NS):
            c, rc = [], []
            port(trs, S0 + k, days[0], days[-1], curve=c, rcurve=rc)
            cs.append(c)
            for arr, x in ((mm, c), (rm, rc)):
                pk, m = x[0], 0.0
                for v in x:
                    pk = max(pk, v)
                    m = max(m, 1 - v / pk)
                arr.append(m)
        yr = {}
        for y in years:
            ks = [di[d] for d in days if d[:4] == y]
            vals = sorted(c[ks[-1]] / (c[ks[0] - 1] if ks[0] > 0 else 1.0) - 1 for c in cs)
            yr[y] = vals[len(vals) // 2]
        ytab[lab] = yr
        rets = [[c[i] / (c[i - 1] if i else 1.0) - 1 for i in range(len(c))] for c in cs]
        R, n, B, sims = random.Random(42), len(days), 20, []
        for _ in range(5000):
            r_ = rets[R.randrange(NS)]
            eq, pk, md, k = 1.0, 1.0, 0.0, 0
            while k < n:
                st = R.randrange(0, n - B)
                for x in r_[st:st + B]:
                    eq *= 1 + x
                    pk = max(pk, eq)
                    md = max(md, 1 - eq / pk)
                k += B
            sims.append((max(eq, 1e-9) ** (1 / yrs) - 1, md))
        ca = sorted(x[0] for x in sims)
        md_ = [x[1] for x in sims]
        med = lambda v: sorted(v)[len(v) // 2]
        worst_y = min(yr, key=yr.get)
        w(f"| {lab} | {pct(med(rm))}／{pct(max(rm))} | {pct(med(mm))}／{pct(max(mm))} | {worst_y} {pct(yr[worst_y], 0)} | {pct(yr['2022'], 0)} | "
          f"{pct(ca[int(len(ca) * 0.05)])} | {pct(sum(1 for x in md_ if x > 0.5) / len(md_), 1)} | {pct(sum(1 for x in md_ if x > 0.6) / len(md_), 1)} |")
        print("ETF2", lab, file=sys.stderr)
    w("\n## 3. 年ごとの成績（乱数50通りの中央値）\n")
    w("| 形 | " + " | ".join(years) + " |")
    w("|---|" + "---|" * len(years))
    for lab, _ in forms:
        w(f"| {lab} | " + " | ".join(pct(ytab[lab][y], 0) for y in years) + " |")
    st_ = forms[0][0]
    e0 = res[(forms[1][0], SEEDSETS[1])]
    w(f"\n18,000ドルが最後にいくらになるか（組2の年率で計算）: 株 {18000 * (1 + res[(st_, SEEDSETS[1])]['all']) ** yrs:,.0f}ドル、"
      f"2倍ETFがある銘柄だけETF {18000 * (1 + e0['all']) ** yrs:,.0f}ドル（約{yrs:.1f}年）。\n")
    w("- 2倍ETFの多くは2022年以降の上場で、それより前は実在しない。元の株の値動きから作った仮の値。")
    w("- 実物の2倍ETFは、値段の差（スプレッド）や、毎日の合わせ直しのずれで、ここより少し悪くなることがある。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    open(OUTDIR + f"2倍ETFがある銘柄だけ2倍ETF（今のルール{'・' + tag if tag else ''}）.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("書き出し", file=sys.stderr)


def etf_rule_stage(build, port, ev, SEEDSETS, days, HAS):
    """2倍ETFを使う例外の決まり（ルールごと・目減りの大きいETFを除く）を比べる（2026-10-04）。目減りは実測（2倍ETFの対応表.json）"""
    import json
    tab = json.load(open(os.path.join(os.path.dirname(OUTDIR.rstrip("/")), "2倍ETFの対応表.json"), encoding="utf-8"))
    drag = {u: -x["drag"] for u, x in tab.items()}

    def to2x(trs, ok):
        out = []
        for t in trs:
            if t["sym"] not in HAS or not ok(t):
                out.append(t)
                continue
            FEE = drag.get(t["sym"], 0.12) / 252
            ds = sorted(t["path"])
            e, prev, pv = 1 - COST, 1 - COST, {}
            for d in ds:
                g_ = t["path"][d]
                e = max(0.0, e * (1 + 2 * (g_ / prev - 1)) * (1 - FEE))
                prev = g_
                pv[d] = e
            out.append({**t, "path": pv})
        return out

    base = build()
    dg = lambda t: drag.get(t["sym"], 0.12)
    forms = [("株だけ（今のルール）", lambda t: False),
             ("A. 2倍ETFがある銘柄は全部ETF", lambda t: True),
             ("B. 急落の底だけETF", lambda t: t["rule"] == "C"),
             ("C. 押し目・急落の底（逆張り）だけETF", lambda t: t["rule"] in ("B", "C")),
             ("D. 順張り（ミネルヴィニ・新高値V2）だけETF", lambda t: t["rule"] in ("M", "V")),
             ("E. 目減りが年20%以上のETFは使わない", lambda t: dg(t) < 0.20),
             ("F. 目減りが年15%以上のETFは使わない", lambda t: dg(t) < 0.15),
             ("G. 逆張りだけETF、目減り年20%以上は使わない", lambda t: t["rule"] in ("B", "C") and dg(t) < 0.20)]
    S0, NS = SEEDSETS[1]
    L = []
    w = L.append
    w(f"---\ntype: backtest\ntitle: 2倍ETFを使う決まり\ncreated: {dt.date.today()}\nscript: tools/backtest_retest.py --stage etfrule\n---\n")
    w("# 2倍ETFを使う決まり（ルールごと・目減りの大きいETFを除く）\n")
    w(f"2倍ETFがある{len(HAS)}銘柄（ユーザーがムームー証券で買えることを確認）: " + "・".join(sorted(HAS)) + "。"
      "目減りは直近1年の実測（`個別株2倍ETFの比べ方.md`、表にないものは年12%）。合図・売る日は今のルールのまま。乱数3組。\n")
    w("| 形 | 年率（3組） | 設計期間（3組） | 確認期間（3組） | 含み損込みの最大下落率（組2） | 確定した損益だけの最大下落率（組2の中央値／最悪） | ETFで買った合図の数 |")
    w("|---|---|---|---|---|---|---|")
    rows = []
    for lab, ok in forms:
        trs = to2x(base, ok)
        es = [ev(trs, sd) for sd in SEEDSETS]
        rm = []
        for k in range(NS):
            rc = []
            port(trs, S0 + k, days[0], days[-1], rcurve=rc)
            pk, m = rc[0], 0.0
            for v in rc:
                pk = max(pk, v)
                m = max(m, 1 - v / pk)
            rm.append(m)
        rm.sort()
        n_ = sum(1 for t in base if t["sym"] in HAS and ok(t))
        rows.append((lab, es, rm))
        f3 = lambda key: "／".join(pct(e[key]) for e in es)
        w(f"| {lab} | {f3('all')} | {f3('is')} | {f3('oos')} | {pct(es[1]['mdd'])} | {pct(rm[len(rm) // 2])}／{pct(rm[-1])} | {n_} |")
        print("ETF決まり", lab, file=sys.stderr)
    w("\n- 確定した損益だけの最大下落率は、持っている株（ETF）を買った額のまま数え、売って確定した損益だけで資金が増減するとした場合。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    open(OUTDIR + "2倍ETFを使う決まり.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("書き出し", file=sys.stderr)


def earnings_stage(data, base, build, ev, CUR, CONF, safe):
    """5. 決算をまたぐか（Nasdaqの決算カレンダーから取った過去の決算日。`tools/fetch_earnings_history.py`）"""
    import json
    earn = json.load(open(os.path.join(DEFAULT_CACHE, "earnings.json")))
    nd = 0
    for sym, s in data.items():
        ev_ = earn.get(sym) or earn.get(sym.replace(".", "-")) or []
        pos = {d: k for k, d in enumerate(s["date"])}
        rset = set()
        for d, tm in ev_:
            # 反応する日: 寄り付き前・時刻不明はその日、引け後は翌営業日
            k = pos.get(d)
            if k is None:
                import bisect
                k = bisect.bisect_right(s["date"], d)
                if k >= len(s["date"]) or k == 0:
                    continue
            elif tm == "time-after-hours":
                k += 1
            rset.add(k)
        s["earn_r"] = rset
        nd += bool(rset)
    have = sum(1 for t in base if data[t["sym"]]["earn_r"])
    L = []
    w = L.append
    w(f"---\ntype: backtest\ntitle: 決算をまたぐかどうか\ncreated: {dt.date.today()}\nscript: tools/backtest_retest.py --stage earn\n---\n")
    w("# 決算をまたぐかどうか\n")
    w(f"過去の決算日は Nasdaq の決算カレンダー（1日ごと、2015年〜）から取った（`tools/fetch_earnings_history.py`）。決算日のある銘柄 {nd}、"
      f"決算日が分かる銘柄の合図 {have}件 / {len(base)}件。決算が寄り付き前・時刻不明ならその日、引け後なら翌営業日を「決算で株価が動く日」とした。\n")
    tr = build()
    cross, nocross = [], []
    for t0, t1 in zip(base, tr):
        rs_ = data[t0["sym"]]["earn_r"]
        i1 = data[t0["sym"]]["date"].index(t1["out"])
        r = t1["path"][t1["out"]] - 1
        (cross if any(t0["i0"] <= k <= i1 for k in rs_) else nocross).append((t0["rule"], r))
    w("## 決算をまたいだ売買と、またがなかった売買（今のルール、全部の合図）\n")
    w("| | 件数 | 勝率 | 1回平均 | 15%以上の損の割合 |")
    w("|---|---|---|---|---|")
    for lab, xs_ in (("決算をまたいだ", cross), ("またがなかった", nocross)):
        r_ = [x for _, x in xs_]
        if r_:
            w(f"| {lab} | {len(r_)} | {pct(sum(1 for x in r_ if x > 0) / len(r_), 0)} | {pct(sum(r_) / len(r_), 2)} | {pct(sum(1 for x in r_ if x <= -0.15) / len(r_), 0)} |")
    w("")

    def soon(t, n_):
        rs_ = data[t["sym"]]["earn_r"]
        return any(t["i0"] <= k <= t["i0"] + n_ for k in rs_)

    def pre_earn(s, j):
        return (j + 2) in s.get("earn_r", ())

    items = [("決算の5営業日前までに入る合図は買わない", lambda: build(drop=lambda t: soon(t, 5))),
             ("決算の10営業日前までに入る合図は買わない", lambda: build(drop=lambda t: soon(t, 10))),
             ("決算の20営業日前までに入る合図は買わない", lambda: build(drop=lambda t: soon(t, 20))),
             ("保有中は決算の前日の寄り付きで全部売る（全部のルール）", lambda: build(extra=(pre_earn,), extra_rules=TREND_ALL)),
             ("保有中は決算の前日の寄り付きで全部売る（順張りだけ）", lambda: build(extra=(pre_earn,), extra_rules=("M", "V"))),
             ("保有中は決算の前日の寄り付きで全部売る（押し目・急落の底だけ）", lambda: build(extra=(pre_earn,), extra_rules=("B", "C")))]
    w("## 決算の前に買わない・決算の前に売る\n")
    c0 = CUR[CONF]
    w(f"今のルール: 年率 {pct(c0['all'])}、最大下落率 {pct(c0['mdd'])}、設計期間 {pct(c0['is'])}、確認期間 {pct(c0['oos'])}（乱数50通り）\n")
    w("| 形 | 年率 | 最大下落率 | 設計期間 | 確認期間 | 両方の期間で上回ったか |")
    w("|---|---|---|---|---|---|")
    for lab, mk in items:
        e = ev(mk(), CONF)
        ok = e["is"] > c0["is"] and e["oos"] > c0["oos"]
        w(f"| {lab} | {pct(e['all'])} | {pct(e['mdd'])} | {pct(e['is'])} | {pct(e['oos'])} | {'はい' if ok else ''} |")
        print("決算", lab, file=sys.stderr)
    w("\n- 決算の前日の寄り付きで売る形は、決算の2営業日前の引けで判定する（引け後の決算なら決算日の寄り付き、寄り付き前の決算なら前日の寄り付きで売ることになる）。")
    w("- この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    open(OUTDIR + "決算をまたぐかどうか.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("書き出し: 決算をまたぐかどうか.md", file=sys.stderr)


TREND_ALL = ("B", "C", "M", "V")


if __name__ == "__main__":
    main()
