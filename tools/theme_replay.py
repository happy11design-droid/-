#!/usr/bin/env python3
"""運用期間の毎朝の記録（record.json）から、ルールの合図だけで売買した場合を再現する（著者の判定は使わない）。

2026-11-20 ユーザーの指示「著者？これは私の予備の判断材料ではないですか？著者は含まずに確認して」→「全て実行して」。
方式Bでは、買うかどうかは採用ルールの合図が決め、著者は注文を止める理由だけを判定する（ユーザーの予備の判断材料）。
週次レビュー（`tools/theme_review.py review`、累計の方）の節6に入り、毎週「ルールどおりに売買していたら資金はいくらか」を確かめる。

- 候補: 毎朝の記録の候補（表に出したもの）＋枠外で表に出さなかった候補（record.json の omitted、2026-10-23〜）。パターンA だけ。
  予約（B）は2026-10-25に注文をやめたので入れない。ワインスタイン10週は参考の表示だけなので入れない。
- 買う順番: 記録の順番（監視銘柄→テーマの外、RSの高い順）。4銘柄の枠、1銘柄＝前の日の引けの資金÷4、同じ業種2銘柄まで、同じ銘柄は重ねて持たない。
- 買い方: 合図の翌取引日の寄り付き（ミネルヴィニは上限を超えたら見送り）。急落の底は、記録に指値（合図の日の終値の2%下、3取引日。
  2026-11-03〜）がある日からは指値（枠外の候補は終値の2%下で計算）。それより前は翌日の寄り付き（その日のルールのまま）。
- 売り方: 損切り15%（日中の逆指値、元の株の値段）。押し目＝前の日の上部バンドに売りの指値、引けで上部バンド以上なら翌日の寄り付き、
  出来高2倍の大陰線の翌日の寄り付き。急落の底＝終値が5日線を上回った翌日の寄り付き、大陰線。新高値V2・ミネルヴィニ＝引けで50日線割れ・
  かぶせ線の翌日の寄り付き（半分売りは入れない）。
- 2倍ETF: 2倍ETFの対応表で目減り年15%未満の銘柄は、合図の日にS&P500が20週線で「上昇」なら2倍ETFで持つ（案1）。ETFの値段は実際の日足。
  日中の損切り・指値の売りのETFの値段は「前の日のETFの終値×(1＋2×元の株の前の日の終値からの変化)」で近似する。片道0.1%。
数値の事実だけで、Claudeの売買判断は含まない。

使い方: tools/theme_replay.py <record.json を置いたディレクトリ> [--out FILE] [--capital 12000] [--asof YYYY-MM-DD]
"""
import argparse
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_swing as bs
import backtest_trend as bt
import theme_scan as ts

STOP, COST, SLOTS, GCAP = 0.15, 0.001, 4, 2
HERE = os.path.dirname(os.path.abspath(__file__))


def load_records(d):
    byd = {}
    for f in sorted(glob.glob(os.path.join(d, "**", "record.json"), recursive=True)):
        try:
            r = json.load(open(f, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if "trade_date" in r and r.get("candidates") is not None:
            byd[r["trade_date"]] = r   # 同じ日が2つあれば後の方
    return [byd[k] for k in sorted(byd)]


def rule_of(kind):
    return ("新高値V2" if "新高値" in kind else "急落の底" if "急落" in kind else "押し目" if "ボリンジャー" in kind
            else "ミネルヴィニ" if "ミネルヴィニ" in kind else "ワインスタイン")


class Replay:
    def __init__(self, recs, capital, asof=None):
        self.recs, self.cap0, self.asof = [r for r in recs if not asof or r["trade_date"] <= asof], capital, asof
        self.limit_from = min((r["trade_date"] for r in recs for c in r["candidates"]
                               if c.get("limit_buy") and "急落" in c["kind"] and c.get("pattern", "A") == "A"), default="9999")
        syms = sorted({c["sym"] for r in recs for c in self.sigs(r)})
        self.data = {}
        for s in syms:
            d = self.get(s)
            if d and len(d["c"]) > 200:
                bt.prepare(d)
                bs.prepare(d)
                self.data[s] = d
        self.spy, self.sox = self.get("SPY"), self.get("^SOX")
        self.ind = ts.load_industries()
        self.etf = {}
        self.last = max((d["date"][-1] for d in self.data.values()), default="-")
        self.group = {}
        g = None
        for line in open(os.path.join(HERE, "..", "新分析ツール", "テーマ監視銘柄.md"), encoding="utf-8"):
            if line.startswith("## "):
                g = None if "対象外" in line else re.sub(r"（\d+）", "", line[3:].strip())
            m = re.match(r"^\| ([A-Z][A-Z.]*) \|", line)
            if m and g:
                self.group[m.group(1)] = g

    def get(self, sym):
        d = ts.fetch_daily(sym)
        return ts.cut(d, self.asof) if d and self.asof else d

    def sigs(self, r):
        out = []
        n_shown = len(r["candidates"])
        for idx, c in enumerate(list(r["candidates"]) + list(r.get("omitted") or [])):
            if c.get("pattern", "A") != "A" or "日目）" in c["kind"] or "ワインスタイン" in c["kind"]:
                continue
            c = dict(c, shown=idx < n_shown)
            if "急落" in c["kind"]:
                c["limit_buy"] = ((c.get("limit_buy") or round(c["close"] * (1 - ts.C_LIMIT), 2))
                                  if r["trade_date"] >= getattr(self, "limit_from", "9999") else None)
            out.append(c)
        return out

    # ---- 1回の売買 ----
    def run_trade(self, rule, s, k, px):
        """k日に px で買った後。(手じまいのindex, 値段, 理由, 寄り付きで売ったか)。持ち続けていれば (最後のindex, 終値, '保有中…', False)"""
        stop, n, since = px * (1 - STOP), len(s["c"]), s["date"][k]
        bb = ts.big_bear_signal(s, since) if rule in ("押し目", "急落の底") else None
        dc = ts.dark_cloud_signal(s, since) if rule in ("新高値V2", "ミネルヴィニ") else None
        for j in range(k, n):
            if j > k and s["o"][j] <= stop:
                return j, s["o"][j], "損切り", True
            if s["l"][j] <= stop:
                return j, stop, "損切り", False
            if rule == "押し目" and j > k and s["bb_up"][j - 1] and s["h"][j] >= s["bb_up"][j - 1]:
                lim = s["bb_up"][j - 1]
                return j, max(s["o"][j], lim), "上部バンドの指値", s["o"][j] >= lim
            ex = None
            if rule == "押し目":
                ex = "引けで上部バンド以上" if s["pctb"][j] is not None and s["pctb"][j] >= 1.0 else "出来高2倍の大陰線" if s["date"][j] == bb else None
            elif rule == "急落の底":
                ex = ("終値が5日線を上回った" if j >= 4 and s["c"][j] > sum(s["c"][j - 4:j + 1]) / 5
                      else "出来高2倍の大陰線" if s["date"][j] == bb else None)
            else:
                ex = ("50日線割れ" if s["ma50"][j] is not None and s["c"][j] < s["ma50"][j]
                      else "かぶせ線" if s["date"][j] == dc else None)
            if ex:
                if j + 1 < n:
                    return j + 1, s["o"][j + 1], ex, True
                return j, s["c"][j], f"保有中（次の寄り付きで売る: {ex}）", False
        return n - 1, s["c"][-1], "保有中", False

    def etf_px(self, etf, s, j, stock_px, at_open):
        e = self.etf.get(etf)
        if e is None:
            e = self.etf[etf] = self.get(etf) or {}
        if not e or s["date"][j] not in e["date"]:
            return None
        i = e["date"].index(s["date"][j])
        if at_open:
            return e["o"][i] * (1 + 2 * (stock_px / s["o"][j] - 1))
        return e["c"][i - 1] * (1 + 2 * (stock_px / s["c"][j - 1] - 1))

    def plan(self, r, c, use_etf=True):
        s = self.data.get(c["sym"])
        if not s or r["trade_date"] not in s["date"]:
            return None
        i = s["date"].index(r["trade_date"])
        if i + 1 >= len(s["c"]):
            return None
        rule = rule_of(c["kind"])
        if rule == "急落の底" and c.get("limit_buy"):
            k = None
            for j in range(i + 1, min(i + 1 + ts.C_LIMIT_DAYS, len(s["c"]))):
                if s["l"][j] <= c["limit_buy"]:
                    k = j
                    break
                if s["c"][j] > sum(s["c"][j - 4:j + 1]) / 5:
                    break
            if k is None:
                return None
            px = min(s["o"][k], c["limit_buy"])
        else:
            if c.get("limit") and s["o"][i + 1] > c["limit"]:
                return None
            k, px = i + 1, s["o"][i + 1]
        xj, xp, why, at_open = self.run_trade(rule, s, k, px)
        t = {"sym": c["sym"], "rule": rule, "sig": r["trade_date"], "buy": s["date"][k], "px": px, "exit_date": s["date"][xj],
             "exit": xp, "why": why, "ret": xp / px - 1 - 2 * COST, "stock_ret": xp / px - 1 - 2 * COST, "etf": None, "shown": c.get("shown")}
        ex = ts.etf2x_of(c["sym"]) if use_etf else None
        if ex and ts.etf_regime(spy=self.spy, asof=r["trade_date"])[0] == "上昇":
            e_in = self.etf_px(ex[0], s, k, px, True)
            if why.startswith("保有中"):
                e = self.etf.get(ex[0]) or {}
                e_out = e["c"][e["date"].index(s["date"][xj])] if e and s["date"][xj] in e["date"] else None
            else:
                e_out = self.etf_px(ex[0], s, xj, xp, at_open)
            if e_in and e_out:
                t.update(etf=ex[0], e_in=e_in, ret=e_out / e_in - 1 - 2 * COST)
        return t

    def ratio(self, t, day):
        """保有中の t の、day の終値での値段の比（買値に対する）"""
        s = self.data[t["sym"]]
        if t["etf"]:
            e = self.etf[t["etf"]]
            jj = max(i for i, d in enumerate(e["date"]) if d <= day)
            return e["c"][jj] / t["e_in"]
        j = max(i for i, d in enumerate(s["date"]) if d <= day)
        return s["c"][j] / t["px"]

    # ---- 4銘柄の枠 ----
    def simulate(self, use_etf, cbk=None):
        """cbk=(件数, 損の件数, 止める取引日): 売った売買の直近の件数のうち損で終わった件数が届いたら、次の日から新しい買いを止める（2026-11-22 の検証の形）"""
        cal = sorted({d for s in self.data.values() for d in s["date"] if d >= self.recs[0]["trade_date"]})
        rec_by = {r["trade_date"]: r for r in self.recs}
        cash, pos, done, curve, until, self.paused = self.cap0, [], [], [], -1, []
        for di, day in enumerate(cal):
            for p in sorted(pos, key=lambda p: p["sym"]):
                if p["exit_date"] == day and not p["why"].startswith("保有中"):
                    cash += p["amt"] * (1 + p["ret"] + 2 * COST) * (1 - COST)
                    pos.remove(p)
                    done.append(p)
                    if cbk and len(done) >= cbk[0] and sum(1 for q in done[-cbk[0]:] if q["ret"] < 0) >= cbk[1] and di + cbk[2] > until:
                        until = di + cbk[2]
                        self.paused.append((day, cal[min(until, len(cal) - 1)] if until < len(cal) else f"{cbk[2]}取引日後"))
            prev = cal[di - 1] if di else None
            if di <= until:
                curve.append((day, cash + sum(p["amt"] * self.ratio(p, day) for p in pos)))
                continue
            for back in cal[max(0, di - ts.C_LIMIT_DAYS):di]:   # 急落の底の指値は合図の日から3取引日のうちに約定する
                r = rec_by.get(back)
                if not r:
                    continue
                for c in self.sigs(r):
                    if len(pos) >= SLOTS or any(p["sym"] == c["sym"] for p in pos):
                        continue
                    t = self.plan(r, c, use_etf)
                    if not t or t["buy"] != day:
                        continue
                    g = self.ind.get(c["sym"])
                    if g and sum(1 for p in pos if self.ind.get(p["sym"]) == g) >= GCAP:
                        continue
                    eq = cash + sum(p["amt"] * self.ratio(p, prev) for p in pos)
                    amt = min(eq / SLOTS, cash)
                    if amt <= 1:
                        continue
                    cash -= amt
                    pos.append({**t, "amt": amt * (1 - COST)})
            curve.append((day, cash + sum(p["amt"] * self.ratio(p, day) for p in pos)))
        peak, mdd = 0, 0
        for _, v in curve:
            peak = max(peak, v)
            mdd = max(mdd, 1 - v / peak)
        return {"final": curve[-1][1] if curve else self.cap0, "mdd": mdd, "done": done, "open": pos, "curve": curve}

    def per_signal(self):
        """枠の制限なし・元の株。同じ銘柄・同じルールは、前の売買を持っている間に出た合図を数えない（1回の売買）"""
        rows, seen = [], {}
        for r in self.recs:
            for c in self.sigs(r):
                t = self.plan(r, c, False)
                if not t:
                    continue
                key = (c["sym"], t["rule"])
                if key in seen and seen[key] >= r["trade_date"]:
                    continue
                seen[key] = t["exit_date"]
                i = max(k for k, d in enumerate(self.sox["date"]) if d <= r["trade_date"]) if self.sox else None
                t["sox"] = self.sox["c"][i] / max(self.sox["c"][max(0, i - 59):i + 1]) - 1 if i is not None else None
                t["grp"] = self.group.get(c["sym"], "テーマの外")
                rows.append(t)
        return rows


def section(rec_dir, capital=12000, title="## 6. ルールの合図だけで売買した場合（著者の判定は使わない）", asof=None):
    recs = [r for r in load_records(rec_dir) if not asof or r["trade_date"] <= asof]
    L = [title, ""]
    w = L.append
    if not recs:
        w("記録なし\n")
        return "\n".join(L)
    rp = Replay(recs, capital, asof)
    w(f"方式Bでは買うかどうかはルールの合図が決め、著者の判定はユーザーの予備の判断材料。ここでは著者の結論を使わず、毎朝の記録の合図"
      f"（表に出した候補＋枠外で省いた候補。パターンAだけ）をルールどおりに売買した場合を、記録の始め（{recs[0]['trade_date']}）から"
      f"{rp.last}の引けまで再現する（`tools/theme_replay.py`）。資金{capital:,}ドル、4銘柄の枠、1銘柄＝資金÷4、同じ業種2銘柄まで、"
      "記録の買う順番どおり。損切り15%（日中の逆指値）とルールの手じまい（押し目は上部バンドの指値・大陰線、急落の底は5日線・大陰線、"
      "順張りは50日線割れ・かぶせ線。半分売りは入れない）。2倍ETFは案1（合図の日にS&P500が20週線で上昇なら）。片道0.1%。\n")
    res = [("2倍ETFも使う（今のルール）", rp.simulate(True)), ("元の株だけ", rp.simulate(False))]
    w("| 形 | 今の資金 | 損益 | 最大下落率 | 売った売買（勝ち/件数） | 保有中（含み益/件数） |")
    w("|---|---|---|---|---|---|")
    for k, x in res:
        w(f"| {k} | {x['final']:,.0f}ドル | {(x['final'] / capital - 1) * 100:+.1f}% | {x['mdd'] * 100:.1f}% | "
          f"{sum(1 for p in x['done'] if p['ret'] > 0)}/{len(x['done'])} | {sum(1 for p in x['open'] if p['ret'] > 0)}/{len(x['open'])} |")
    x = res[0][1]
    w("\n2倍ETFも使う形の売買:\n")
    w("| 合図の日 | 銘柄 | ルール | 2倍ETF | 買った日 | 買値（株） | 売った日（保有中は最新） | 値段（株） | 株の損益 | 枠の損益 | 理由 |")
    w("|---|---|---|---|---|---|---|---|---|---|---|")
    for p in sorted(x["done"] + x["open"], key=lambda p: (p["buy"], p["sym"])):
        w(f"| {p['sig']} | {p['sym']} | {p['rule']} | {p['etf'] or ''} | {p['buy']} | {p['px']:.2f} | {p['exit_date']} | {p['exit']:.2f} | "
          f"{p['stock_ret'] * 100:+.1f}% | {p['ret'] * 100:+.1f}% | {p['why']} |")
    pts = x["curve"][::5] + ([x["curve"][-1]] if x["curve"] and (len(x["curve"]) - 1) % 5 else [])
    w("\n資金の推移（5取引日ごと）: " + "、".join(f"{d[5:]} {v:,.0f}" for d, v in pts))

    rows = rp.per_signal()
    w(f"\n合図ごと（枠の制限なし・元の株。同じ銘柄・同じルールは1回の売買として数える）: {len(rows)}回、"
      f"プラス {sum(1 for t in rows if t['ret'] > 0)}回、損切り {sum(1 for t in rows if t['why'] == '損切り')}回、"
      f"1回平均 {sum(t['ret'] for t in rows) / max(1, len(rows)) * 100:+.1f}%（バックテストの見込み: 勝率約62%・1回平均約+1.8%）\n")

    def table(head, keyf, order=None):
        ks = {}
        for t in rows:
            ks.setdefault(keyf(t), []).append(t)
        w(f"| {head} | 回数 | プラス | 損切り | 1回平均 |")
        w("|---|---|---|---|---|")
        for k in (order or sorted(ks)):
            g = ks.get(k)
            if g:
                st = sum(1 for t in g if t["why"] == "損切り")
                w(f"| {k} | {len(g)} | {sum(1 for t in g if t['ret'] > 0)} | {st}（{st / len(g) * 100:.0f}%） | {sum(t['ret'] for t in g) / len(g) * 100:+.1f}% |")
        w("")

    if rows:
        table("ルール", lambda t: t["rule"])
        table("合図の日のSOX（直近60日の最高値から）",
              lambda t: "不明" if t["sox"] is None else "0〜−10%" if t["sox"] > -0.10 else "−10〜−20%" if t["sox"] > -0.20 else "−20%より深い",
              ["0〜−10%", "−10〜−20%", "−20%より深い", "不明"])
        table("監視銘柄のグループ", lambda t: t["grp"])
        table("毎朝の表", lambda t: "表に出した" if t["shown"] else "枠外で省いた")
        plus = [t for t in rows if t["ret"] > 0]
        w("プラスの売買: " + ("、".join(f"{t['sym']}（{t['sig'][5:]} {t['rule']} {t['ret'] * 100:+.1f}%"
                                       + ("・含み益" if t["why"].startswith("保有中") else "") + "）" for t in plus) or "なし"))
    w("\n- ボリンジャーの指値の売り・日中の損切りの2倍ETFの値段は近似。この結果はルールの条件どおりに機械的に計算したもので、Claudeによる個別銘柄の売買判断ではない。")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--out")
    ap.add_argument("--capital", type=float, default=12000)
    ap.add_argument("--asof", help="この日の引けまでの株価で計算する（YYYY-MM-DD）")
    a = ap.parse_args()
    text = section(a.dir, a.capital, "# ルールの合図だけで売買した場合（著者の判定は使わない）", a.asof) + "\n"
    if a.out:
        open(a.out, "w", encoding="utf-8").write(text)
    print(text)


if __name__ == "__main__":
    main()
