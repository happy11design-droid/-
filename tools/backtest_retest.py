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
    r.add_argument("--etf", default=None, help="etf2x: 2倍ETFにする銘柄（カンマ区切り）。省略すると backtest_2x.HAS_2X")
    r.add_argument("--drag", default=None, help="etf2x: 2倍ETFの目減り（年率）。数値なら全部同じ、'measured' なら 新分析ツール/2倍ETFの対応表.json の実測（ないものは0.12）")
    r.add_argument("--tag", default="", help="etf2x: 結果のファイル名と見出しに付ける名前（例: ムームー証券）")
    r.add_argument("--stage", default="all", choices=("sell", "combo", "half", "filter", "rule", "stats", "dd", "robust", "earn", "realized", "etf2x", "etfrule", "weinstein", "rsi", "pivot", "exits", "pullback", "recover", "prio", "slope", "slope2", "slope3", "all"))
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
