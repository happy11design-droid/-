---
type: research
title: 個別株2倍ETFの比べ方
created: 2026-10-04
script: tools/leveraged_etf_check.py
---

# 個別株2倍ETFの比べ方（同じ元の株に複数あるとき、どれを買うか）

--prev   : 前回の対応表。渡すと、復活・除外・ETFの変更を --changes に書く（週次レビュー用）

Yahoo Finance の直近1年の日足で、ETFごとに次を出す。
  名前（Yahooの正式名）、取引日数、1日平均の売買代金、元の株の値動きに対する倍率（回帰の傾き）・相関、
  目減り（年率）＝ ETFの実際の増え方 ÷「元の株の毎日の値動きの2倍」を毎日つないだ増え方。経費・借入コスト・ずれをまとめた差。
倍率が1.8〜2.2・相関0.95以上のものを「本物の2倍ETF」とし、同じ元の株の中で、目減りが小さく売買代金が十分（1日500万ドル以上）なものを勧める。
候補のティッカーはClaudeの知識によるもので、存在しないものはデータが取れずに外れる。

| 元の株 | ETF | 名前 | 日数 | 1日の売買代金 | 倍率 | 相関 | 目減り（年率） | 判定 |
|---|---|---|---|---|---|---|---|---|
| NVDA | NVDL | GraniteShares 2x Long NVDA Daily ETF | 252 | 445.9百万ドル | 1.99 | 1.00 | -10.2% | 2倍ETF |
| NVDA | NVDU | Direxion Daily Nvda Bull 2X Shares | 252 | 43.6百万ドル | 1.98 | 1.00 | -10.1% | **おすすめ** |
| NVDA | NVDX | T-Rex 2X Long NVIDIA Daily Target ETF | 252 | 108.7百万ドル | 1.99 | 1.00 | -14.9% | 2倍ETF |
| NVDA | NVDB | ProShares Ultra NVDA | 252 | 0.7百万ドル | 1.98 | 1.00 | -11.7% | 2倍ETF（売買が少ない） |
| AVGO | AVL | Direxion Daily AVGO Bull 2X Shares | 252 | 34.2百万ドル | 2.00 | 1.00 | -9.9% | **おすすめ** |
| AVGO | AVGU | GraniteShares 2x Long AVGO Daily ETF | 252 | 4.5百万ドル | 2.00 | 1.00 | -10.9% | 2倍ETF（売買が少ない） |
| AVGO | AVGG | Leverage Shares 2X Long AVGO Daily ETF | 252 | 6.9百万ドル | 1.99 | 1.00 | -11.8% | 2倍ETF |
| AVGO | AVGX | Defiance Daily Target 2X Long AVGO ETF | 252 | 28.9百万ドル | 2.00 | 1.00 | -13.4% | 2倍ETF |
| MU | MUU | Direxion Daily MU Bull 2X Shares | 252 | 1,043.7百万ドル | 1.99 | 1.00 | -12.4% | **おすすめ** |
| MU | MULL | GraniteShares 2x Long MU Daily ETF | 252 | 141.4百万ドル | 2.00 | 1.00 | -17.0% | 2倍ETF |
| AMD | AMDL | GraniteShares 2x Long AMD Daily ETF | 252 | 159.9百万ドル | 2.00 | 1.00 | -11.4% | 2倍ETF |
| AMD | AMUU | Direxion Daily AMD Bull 2X Shares | 252 | 15.5百万ドル | 2.00 | 1.00 | -9.7% | **おすすめ** |
| AMD | AMDG | Leverage Shares 2X Long AMD Daily ETF | 252 | 5.0百万ドル | 2.01 | 1.00 | -12.1% | 2倍ETF（売買が少ない） |
| INTC | INTW | GraniteShares 2x Long INTC Daily ETF | 252 | 114.6百万ドル | 2.00 | 1.00 | -11.6% | 2倍ETF |
| INTC | LINT | Direxion Daily INTC Bull 2X ETF | 218 | 14.7百万ドル | 2.01 | 1.00 | -10.5% | **おすすめ** |
| ARM | ARMG | Leverage Shares 2X Long ARM Daily ETF | 252 | 22.0百万ドル | 2.00 | 1.00 | -13.3% | **おすすめ** |
| MRVL | MVLL | GraniteShares 2x Long MRVL Daily ETF | 252 | 94.5百万ドル | 2.00 | 1.00 | -17.8% | 2倍ETF |
| MRVL | MRVU | Direxion Daily MRVL Bull 2X ETF | 161 | 19.2百万ドル | 2.01 | 1.00 | -10.5% | **おすすめ** |
| QCOM | QCMU | Direxion Daily QCOM Bull 2X Shares | 252 | 2.7百万ドル | 2.03 | 1.00 | -11.3% | 2倍ETF（売買が少ない） |
| ASML | ASMG | Leverage Shares 2X Long ASML Daily ETF | 252 | 2.5百万ドル | 2.00 | 1.00 | -11.8% | 2倍ETF（売買が少ない） |
| SMCI | SMCX | Defiance Daily Target 2X Long SMCI ETF | 252 | 69.0百万ドル | 1.99 | 1.00 | -27.9% | 2倍ETF |
| SMCI | SMCL | GraniteShares 2x Long SMCI Daily ETF | 252 | 12.8百万ドル | 1.99 | 1.00 | -22.8% | **おすすめ** |
| DELL | DLLL | GraniteShares 2x Long DELL Daily ETF | 252 | 52.2百万ドル | 1.99 | 1.00 | -7.7% | **おすすめ** |
| AAPL | AAPU | Direxion Daily AAPL Bull 2X Shares | 252 | 72.3百万ドル | 1.99 | 1.00 | -8.7% | **おすすめ** |
| AAPL | AAPB | GraniteShares 2x Long AAPL Daily ETF | 252 | 2.4百万ドル | 2.03 | 1.00 | -7.1% | 2倍ETF（売買が少ない） |
| AAPL | AAPX | T-Rex 2X Long Apple Daily Target ETF | 252 | 2.5百万ドル | 1.99 | 1.00 | -11.8% | 2倍ETF（売買が少ない） |
| ANET | ANEL | Defiance Daily Target 2X Long ANET ETF | 252 | 1.9百万ドル | 1.99 | 1.00 | -13.8% | 2倍ETF（売買が少ない） |
| VRT | VRTL | GraniteShares 2x Long VRT Daily ETF | 252 | 5.1百万ドル | 1.99 | 1.00 | -15.3% | **おすすめ** |
| CEG | CEGX | Tradr 2X Long CEG Daily ETF | 252 | 1.4百万ドル | 1.99 | 1.00 | -8.6% | 2倍ETF（売買が少ない） |
| VST | VSTL | Defiance Daily Target 2X Long VST ETF | 252 | 2.5百万ドル | 1.98 | 1.00 | -17.4% | 2倍ETF（売買が少ない） |
| GEV | GEVX | Tradr 2X Long GEV Daily ETF | 252 | 3.3百万ドル | 2.00 | 1.00 | -7.8% | 2倍ETF（売買が少ない） |
| GOOGL | GGLL | Direxion Daily GOOGL Bull 2X Shares | 252 | 145.4百万ドル | 2.00 | 1.00 | -9.4% | **おすすめ** |
| GOOGL | GOOX | T-Rex 2X Long Alphabet Daily Target ETF | 252 | 7.7百万ドル | 1.96 | 1.00 | -12.4% | 2倍ETF |
| MSFT | MSFU | Direxion Daily MSFT Bull 2X Shares | 252 | 148.2百万ドル | 1.98 | 1.00 | -9.4% | 2倍ETF |
| MSFT | MSFL | GraniteShares 2x Long MSFT Daily ETF | 252 | 16.7百万ドル | 1.98 | 1.00 | -8.3% | **おすすめ** |
| MSFT | MSFX | T-Rex 2X Long Microsoft Daily Target ETF | 252 | 3.4百万ドル | 1.97 | 1.00 | -12.5% | 2倍ETF（売買が少ない） |
| META | METU | Direxion Daily META Bull 2X ETF | 252 | 143.2百万ドル | 2.00 | 1.00 | -10.3% | 2倍ETF |
| META | FBL | GraniteShares 2x Long META Daily ETF | 252 | 29.5百万ドル | 2.00 | 1.00 | -9.5% | **おすすめ** |
| AMZN | AMZU | Direxion Daily AMZN Bull 2X Shares | 252 | 90.4百万ドル | 1.99 | 1.00 | -10.2% | **おすすめ** |
| AMZN | AMZZ | GraniteShares 2x Long AMZN Daily ETF | 252 | 4.7百万ドル | 1.98 | 1.00 | -7.3% | 2倍ETF（売買が少ない） |
| ORCL | ORCX | Defiance Daily Target 2X Long ORCL ETF | 252 | 58.5百万ドル | 2.00 | 1.00 | -13.2% | 2倍ETF |
| ORCL | ORCU | Direxion Daily ORCL Bull 2X ETF | 218 | 41.6百万ドル | 2.01 | 1.00 | -11.4% | **おすすめ** |
| PLTR | PLTU | Direxion Daily PLTR Bull 2X Shares | 252 | 70.0百万ドル | 1.99 | 1.00 | -9.1% | **おすすめ** |
| PLTR | PTIR | GraniteShares 2x Long PLTR Daily ETF | 252 | 63.2百万ドル | 1.99 | 1.00 | -9.2% | 2倍ETF |
| PLTR | PLTG | Leverage Shares 2X Long PLTR Daily ETF | 252 | 3.0百万ドル | 1.99 | 1.00 | -13.9% | 2倍ETF（売買が少ない） |
| NBIS | NEBX | Tradr 2X Long NBIS Daily ETF | 252 | 69.7百万ドル | 2.00 | 1.00 | -13.3% | 2倍ETF |
| NBIS | NBIL | GraniteShares 2x Long NBIS Daily ETF | 249 | 100.2百万ドル | 2.00 | 1.00 | -11.8% | **おすすめ** |
| CRWV | CWVX | Tradr 2X Long CRWV Daily ETF | 252 | 19.4百万ドル | 1.99 | 1.00 | -11.9% | **おすすめ** |
| CRWV | CRWG | Leverage Shares 2X Long CRWV Daily ETF | 252 | 34.7百万ドル | 2.00 | 1.00 | -16.2% | 2倍ETF |
| TSLA | TSLL | Direxion Daily TSLA Bull 2X Shares | 252 | 757.6百万ドル | 1.99 | 1.00 | -11.8% | 2倍ETF |
| TSLA | TSLR | Graniteshares 2x Long TSLA Daily ETF | 252 | 21.9百万ドル | 2.01 | 1.00 | -10.2% | **おすすめ** |
| TSLA | TSLT | T-Rex 2X Long Tesla Daily Target ETF | 252 | 31.2百万ドル | 1.99 | 1.00 | -14.3% | 2倍ETF |
| APP | APPX | Tradr 2X Long APP Daily ETF | 252 | 21.0百万ドル | 1.99 | 1.00 | -10.6% | **おすすめ** |
| CRWD | CRWL | GraniteShares 2x Long CRWD Daily ETF | 252 | 11.8百万ドル | 2.00 | 1.00 | -17.9% | **おすすめ** |
| CRWD | CRWU | T-REX 2X Long CRWV Daily Target ETF | 252 | 18.6百万ドル | 0.59 | 0.17 | -95.7% | 2倍ではない／別物 |
| PANW | PALU | Direxion Daily PANW Bull 2X Shares | 252 | 6.6百万ドル | 2.00 | 1.00 | -10.0% | **おすすめ** |
| SHOP | SHPU | Direxion Daily SHOP Bull 2X ETF | 252 | 2.1百万ドル | 2.01 | 1.00 | -9.2% | 2倍ETF（売買が少ない） |
| RDDT | RDTL | GraniteShares 2x Long RDDT Daily ETF | 252 | 11.8百万ドル | 1.98 | 1.00 | -14.8% | **おすすめ** |
| TSM | TSMX | Direxion Daily TSM Bull 2X Shares | 252 | 44.3百万ドル | 2.00 | 1.00 | -10.9% | **おすすめ** |
| TSM | TSMU | GraniteShares 2x Long TSM Daily ETF | 252 | 3.8百万ドル | 2.00 | 1.00 | -14.9% | 2倍ETF（売買が少ない） |
| TSM | TSMG | Leverage Shares 2X Long TSM Daily ETF | 252 | 2.5百万ドル | 2.02 | 1.00 | -11.0% | 2倍ETF（売買が少ない） |
| COIN | CONL | GraniteShares 2x Long COIN Daily ETF | 252 | 119.7百万ドル | 1.99 | 1.00 | -15.9% | **おすすめ** |
| COIN | CONX | Direxion Daily COIN Bull 2X ETF | 218 | 1.0百万ドル | 2.00 | 1.00 | -14.4% | 2倍ETF（売買が少ない） |
| MSTR | MSTU | T-Rex 2X Long MSTR Daily Target ETF | 252 | 237.1百万ドル | 1.98 | 1.00 | -27.4% | **おすすめ** |
| MSTR | MSTX | Defiance Daily Target 2X Long MSTR ETF | 252 | 104.8百万ドル | 1.99 | 1.00 | -28.3% | 2倍ETF |
| SNDK | SNXX | Tradr 2X Long Sndk Daily ETF | 173 | 1,226.1百万ドル | 1.98 | 1.00 | -13.7% | **おすすめ** |
| SNDK | SNDU | T-REX 2X Long SNDK Daily Target ETF | 142 | 191.8百万ドル | 2.00 | 1.00 | -21.8% | 2倍ETF |
| NOW | NOWL | GraniteShares 2x Long NOW Daily ETF | 252 | 64.5百万ドル | 2.00 | 1.00 | -15.3% | **おすすめ** |
| CRM | CRMG | Leverage Shares 2X Long CRM Daily ETF | 252 | 22.7百万ドル | 1.98 | 1.00 | -12.1% | **おすすめ** |
| LITE | LITX | Tradr 2X Long Lite Daily ETF | 173 | 88.2百万ドル | 1.99 | 1.00 | -13.7% | **おすすめ** |
| IBM | IBMX | iShares iBonds Dec 2035 Term Muni Bond E | 118 | 0.2百万ドル | 0.01 | 0.17 | +119.8% | 2倍ではない／別物 |
| ADBE | ADBG | Leverage Shares 2X Long ADBE Daily ETF | 252 | 18.1百万ドル | 2.00 | 1.00 | -12.7% | **おすすめ** |
| HOOD | ROBN | T-REX 2X Long HOOD Daily Target ETF | 252 | 24.2百万ドル | 2.01 | 1.00 | -16.2% | **おすすめ** |
| HOOD | HOOG | Leverage Shares 2X Long HOOD Daily ETF | 252 | 12.0百万ドル | 2.00 | 1.00 | -16.4% | 2倍ETF |
| NFLX | NFXL | Direxion Daily NFLX Bull 2X Shares | 252 | 21.7百万ドル | 2.00 | 1.00 | -10.3% | **おすすめ** |
| UBER | UBRL | GraniteShares 2x Long UBER Daily ETF | 252 | 3.3百万ドル | 1.99 | 1.00 | -7.3% | 2倍ETF（売買が少ない） |
| LLY | ELIL | Direxion Daily LLY Bull 2X Shares | 252 | 2.5百万ドル | 1.97 | 1.00 | -8.9% | 2倍ETF（売買が少ない） |
| BA | BOEU | Direxion Daily BA Bull 2X Shares | 252 | 1.6百万ドル | 1.99 | 1.00 | -10.3% | 2倍ETF（売買が少ない） |
| WDC | WDCX | Tradr 2X Long WDC Daily ETF | 173 | 38.7百万ドル | 2.02 | 1.00 | -9.9% | **おすすめ** |
| WDC | WDCC | Corgi WDC 2x Daily ETF | 60 | 0.3百万ドル | 2.01 | 1.00 | -11.7% | 2倍ETF（売買が少ない） |
| STX | STXX | Tradr 2X Long STX Daily ETF | 112 | 3.9百万ドル | 2.01 | 1.00 | -7.4% | 2倍ETF（売買が少ない） |
| STX | STXU | Leverage Shares 2X Long STX Daily ETF | 100 | 1.1百万ドル | 1.99 | 1.00 | -13.9% | 2倍ETF（売買が少ない） |

## おすすめの一覧（元の株 → ETF）

NVDA→NVDU, AVGO→AVL, MU→MUU, AMD→AMUU, INTC→LINT, ARM→ARMG, MRVL→MRVU, SMCI→SMCL, DELL→DLLL, AAPL→AAPU, VRT→VRTL, GOOGL→GGLL, MSFT→MSFL, META→FBL, AMZN→AMZU, ORCL→ORCU, PLTR→PLTU, NBIS→NBIL, CRWV→CWVX, TSLA→TSLR, APP→APPX, CRWD→CRWL, PANW→PALU, RDDT→RDTL, TSM→TSMX, COIN→CONL, MSTR→MSTU, SNDK→SNXX, NOW→NOWL, CRM→CRMG, LITE→LITX, ADBE→ADBG, HOOD→ROBN, NFLX→NFXL, WDC→WDCX

- 目減りは、経費率・借入のコスト・毎日の合わせ直しのずれをまとめた、直近1年の実際の差。マイナスが小さいほど資金効率が良い。
- 売買代金が多いほど、買値と売値の差（スプレッド）が小さく、寄り付きで売買しても値段がずれにくい。
- ムームー証券で買えるかは、アプリで確かめる（取引可能な米国ETF一覧 https://www.moomoo.com/ja/quote/us-tradable-etf ）。
