# テーマ監視 2026-10-28

# 判定のまとめ（ルールの判定と著者の判定を分けて表示）

- **ルールの判定**: 採用した売買ルール（スクリプト）が数値で決めたもの。損切りは買値の15%下の逆指値（日中に届けばその場で売れる）。
- **著者の判定**: ノートブックの著者の回答。買いは注文を止める理由があるときだけ【様子見】、保有はルールより早く手じまう理由があるときだけ【売り】。根拠は下の「著者の回答（全文）」。
- 2つが食い違うときに、どちらに従うかはユーザーが決める。

- **テーマ全体の急落（S2・記録だけ）: あり（S2）**（SOXが直近60取引日の最高値から -11.6%）。S2の日の順張りの候補には「S2なら見送る形」と付ける（売買のルールは変えない。記録してから採用を決める。2026-10-14）

## 保有銘柄

| 銘柄 | ルール | 損益 | ルールの判定 | ルールの判定の理由 | 著者の判定 |
|---|---|---|---|---|---|
| SNDK | ルール外（ユーザーの判断。この日はどのルールの合図もなし） | +2.4% | 保有継続 | 損切り 1165.61（終値から -17.0%） | **【未判定】（）** |
| AMD | ボリンジャーIII | +5.2% | 保有継続 | 損切り 467.47（終値から -19.2%） | 【保有継続】（ボリンジャー） |

## 候補の判定（並びは上の「買う順番」の表と同じ）

- 並びは上の「買う順番」の表と同じ（RSの高い順。勝率の高い順ではない）。注文の値段・株数・逆指値は上の表を見る。勝率・1回平均は、そのルールの過去の成績（後知恵なしの監視銘柄・2015年〜の全部の合図）。
- 空き枠: 2（同時保有4銘柄まで。保有2、うちルールの売り0）。著者が【様子見】の候補を見送るかはユーザーが決める。

| 順 | 銘柄 | ルール | 過去の勝率 | 過去の1回平均 | RS | ルールの判定 | 著者の判定 |
|---|---|---|---|---|---|---|---|
| 1 | VLO | 逆張り: ボリンジャー メソッドIII | 68% | +1.5% | 96 | 買い（翌日の寄り付き） | 【買い】（ボリンジャー） |
| 2 | FFIV（F5（エフファイブ）） | 逆張り: 急落の底（担当: コナーズ） | 65% | +2.1% | 64 | 買い（翌日の寄り付き） | 【買い】（コナーズ） |
| 3（枠外） | HUBB（ハベル） | 逆張り: ボリンジャー メソッドIII | 68% | +1.5% | 18 | 買い（翌日の寄り付き） | 【買い】（ボリンジャー） |

# 著者の回答（全文）

## 0_テーマの局面_ワインスタイン

1. **テーマ全体の局面**: 【ステージ2】（テーマ指数の30週線上昇・線より上。第2章）[1, 2]
2. **グループごとの局面**:
- 半導体｜ステージ2｜30週線上昇・上 [1]
- 半導体製造装置・材料・設計ソフト・計測｜ステージ3｜30週線横ばい・下 [3]
- AIサーバー・ストレージ・メモリ・端末｜ステージ2｜30週線上昇・上 [1]
- 光・通信・ネットワーク｜ステージ3｜30週線横ばい・下 [3]
- データセンターの電力・冷却・部品・受託製造・建設｜ステージ3｜30週線横ばい・下 [3]
- AIプラットフォーム・クラウド｜ステージ2｜30週線上昇・上 [1]
- AIソフト・セキュリティ・ITサービス｜ステージ2｜30週線上昇・上 [1]
3. **転換の兆し**: 出ている。①3グループの30週線横ばい化（第3ステージ移行。第2章）[3]、②対S&P500のRS悪化（第1章・第4章）[4, 5]、③50日線上割合45%と内部劣化（第3章）[6]。
4. **テーマの外**: 判定不能（ヒートマップ省略のため）[7]。

（全体の版が空の応答だったため、1〜2節だけの短い版で送り直した回答。ヒートマップ・急騰急落・ニュースは渡していない）

## 1_コナーズ_prompt_1

## FFIV
1. **投資判断**: 【買い】（注文を止める理由なし）
2. **止める理由の確認**:
   - 本が禁じる形・状況｜なし｜株価365.53は200日線362.44の上で、高値追いではなく急落後（第2章・第4章）
   - 避けるべき時期（決算など）｜なし｜次回決算は90日後で直前でない。月初（3〜8日）でもない（第11章）
   - 悪材料｜なし｜悪材料や急落によるパニックは平均回帰の買い機会（第2章・第8章、10/28）
3. **現状パターンと価格**:
   - 現状パターン: A（条件成立）
   - 本日の発注: 翌日の寄り付きで成行
4. **注意点**: 200日線に非常に近いため下回ったら白紙化・手じまい（第4章）

## 1_ボリンジャー_prompt_1

## AMD
1. **投資判断**: 【保有継続】（ルールより早く手じまう理由なし）
2. **止める理由の確認**:
   - 本が禁じる形・状況｜なし｜M型トップや上部バンドでの売りシグナルなし（第13章, 第17章）
   - 避けるべき時期（決算など）｜なし｜次回決算は11/03。発表前の手じまい規定なし（23_用語集）
   - 悪材料｜なし｜特筆すべき悪材料なし（ニュース 10/28）
3. **現状パターンと価格**:
   - 現状パターン: 保有中（ボリンジャーIIIエントリー済み）
   - 売りの予約注文: 指値 667.50（現在値比 +15.4%）
4. **注意点**: 次回決算（11/03）に向けた株価上昇と+2σ目標値（667.50）到達を注視。

💡 次に、AMDのチャートや指標（%bや出来高オシレーター）の最新推移を分析し、目標価格変更の検討や詳細なリスク評価を行いましょうか？

## 1_ボリンジャー_prompt_2

## HUBB
1. **投資判断**: 【買い】
2. **止める理由の確認**:
   - 本が禁じる形・状況｜なし｜%b<0.05・21日II%>0で反転条件成立（第20章）
   - 避けるべき時期（決算など）｜なし｜決算時期の買い見送り規定なし（マニュアルに規定なし）
   - 悪材料｜判定不能｜個別ニュースの調査なし
3. **現状パターンと価格**:
   - 現状パターン: A（メソッドIIIの買い条件成立）
   - 本日の発注: 翌日の寄り付きで成行
4. **注意点**: 買った日の夜から上部バンドに売り指値を置き毎晩更新する（第20章）。

## 1_ボリンジャー_prompt_3

## VLO
1. **投資判断**: 【買い】
2. **止める理由の確認**:
   - 本が禁じる形・状況｜なし｜%b<0.05かつ21日II%>0でメソッドIII適合（第20章、判定用ルールブック第4・5節）
   - 避けるべき時期（決算など）｜なし｜決算発表通過済み（2026-10-22）（第4章・第15章）
   - 悪材料｜なし｜悪材料の記載なし（2026-10-28）
3. **現状パターンと価格**:
   - 現状パターン: A（%b=-0.014、21日II%=+0.005で条件成立）
   - 本日の発注: 翌日の寄り付きで成行
4. **注意点**: 直近安値付近に損切り（ストップ）を設定しリスクを限定すること（第20章）。

# スキャン（数値と事実）


- 監視銘柄 87（判定できたのは 86、取得不可: Q）。
- この一覧は数値と事実だけ。売買の判断は著者のノートブックが行う。

## 1. テーマ（グループ）の強さ

| グループ | 銘柄数 | 1週 | 1カ月 | 3カ月 | 3カ月の順位 | 50日線より上の銘柄の割合 | グループ指数の30週線の局面（線との乖離、4週前からの線の傾き） |
|---|---|---|---|---|---|---|---|
| 半導体 | 16 | +3.8% | -0.9% | +10.6% | 4位 | 62% | 上昇（+6.5%、+6.4%） |
| 半導体製造装置・材料・設計ソフト・計測 | 8 | -0.7% | -9.2% | +0.8% | 5位 | 25% | 横ばい（-5.0%、+2.9%） |
| AIサーバー・ストレージ・メモリ・端末 | 9 | +1.9% | -8.4% | +22.0% | 1位 | 44% | 上昇（+16.1%、+9.2%） |
| 光・通信・ネットワーク | 9 | +1.3% | -8.0% | -2.5% | 6位 | 22% | 横ばい（-3.4%、+3.1%） |
| データセンターの電力・冷却・部品・受託製造・建設 | 19 | +1.2% | -1.6% | -3.8% | 7位 | 21% | 横ばい（-3.6%、+1.0%） |
| AIプラットフォーム・クラウド | 11 | -0.4% | +3.2% | +13.7% | 3位 | 45% | 上昇（+0.1%、+1.9%） |
| AIソフト・セキュリティ・ITサービス | 14 | +0.1% | +8.0% | +21.1% | 2位 | 86% | 上昇（+23.5%、+5.2%） |

## 2. テーマ全体の状態と早めの警告

- 市場全体の30週線による局面: S&P500指数 **上昇**／NASDAQ100指数 **上昇**（急落の底で買うルールは、過去の検証で下落相場で特に強く、横ばいの相場では負けていた）
- **2倍ETFを使う局面（案1、2026-10-13 採用）: S&P500の20週線（100日線）で 上昇** → 2倍ETFのある銘柄は2倍ETFで買う（SPY 772.31、100日線 757.25、20日前の線 751.58。上昇＝線より上かつ線が上向き）
- **テーマ全体の急落（S2、記録だけ。売買のルールは変えない）: あり（S2）**（SOX 11684.00、直近60取引日の最高値 13217.82 から -11.6%。S2＝最高値から−10%以上）。S2のときに「順張りの新しい買いだけ止める」形を記録で比べる（2026-10-14 ユーザー決定。バックテストでは年率は上がったが2つの期間ではどちらも少し下回ったため、記録してから採用を決める。`バックテスト結果/テーマ全体の急落を検知して手じまう・買いを止める.md`）
- テーマ指数（監視銘柄の等金額平均）の30週線による局面: **上昇**（上昇＝線より上かつ上向き、下落＝線より下かつ下向き、それ以外＝横ばい。ワインスタインのステージの近似）
- テーマ指数と50日線: 50日線より上（乖離 +0.2%）
- S&P500に対する相対的な強さ: 50日平均より下（S&P500より弱い）
- 監視銘柄のうち50日線より上の割合: 45%
- 警告（割合が40%未満かつテーマ指数が50日線より下）: **出ていない**
- 参考（バックテスト）: 30週線の「下落」は高値から10〜33%下げた後に出る遅い判定。50日線・割合・相対的な強さは高値から2〜8%で出るが、誤報が年15回以上ある。警告中に新しい買いを止めると、押し目買い（ボリンジャーIII）の成績は大きく下がった（`バックテスト結果/テーマ監視銘柄・直近3年.md` 11・12節）。

## 3. ヒートマップ（Finviz、全米の業種別の騰落率）

3カ月の騰落率の上位15業種（テーマの外で強くなっている業種の確認用）:

| 順位 | 業種 | 1週 | 1カ月 | 3カ月 | 6カ月 | 1年 |
|---|---|---|---|---|---|---|
| 1 | Health Information Services | +1.8% | +11.0% | +35.6% | +60.0% | +2.5% |
| 2 | Oil & Gas Refining & Marketing | -7.9% | +5.5% | +25.8% | +57.2% | +102.4% |
| 3 | Oil & Gas Drilling | +8.9% | +20.0% | +23.0% | -8.1% | +55.8% |
| 4 | Diagnostics & Research | +2.7% | +5.5% | +23.0% | +54.0% | +28.6% |
| 5 | Software - Infrastructure | +1.7% | +3.6% | +19.9% | +29.1% | +0.2% |
| 6 | Auto Manufacturers | +3.7% | +10.9% | +19.3% | +5.8% | -10.9% |
| 7 | Software - Application | -0.5% | +9.8% | +16.9% | +27.0% | -15.6% |
| 8 | Oil & Gas Integrated | +0.1% | +10.9% | +14.1% | +13.6% | +55.6% |
| 9 | Oil & Gas E&P | +2.0% | +15.0% | +13.5% | +6.6% | +48.9% |
| 10 | Information Technology Services | +0.2% | +15.7% | +12.6% | +8.8% | -20.9% |
| 11 | Marine Shipping | +2.3% | +4.1% | +12.3% | +15.0% | +78.9% |
| 12 | Gold | -2.9% | -4.8% | +11.2% | -2.7% | +23.2% |
| 13 | Medical Instruments & Supplies | +1.8% | +5.4% | +11.0% | +9.0% | -3.6% |
| 14 | Shell Companies | -1.7% | +5.0% | +10.7% | +19.7% | +15.8% |
| 15 | Real Estate - Diversified | +2.6% | +3.7% | +9.4% | +7.0% | +10.3% |

テーマの業種の順位（3カ月、全144業種中）: Semiconductors 17位、Semiconductor Equipment & Materials 109位、Computer Hardware 60位、Communication Equipment 36位、Electronic Components 76位、Software - Infrastructure 5位、Software - Application 7位、Internet Content & Information 58位

## 4. 急騰・急落した銘柄（前日比±5%以上、または出来高が50日平均の2倍以上）

原因のニュースをサブエージェントが調べ、候補・保有銘柄の判定材料として著者に渡す。急騰・急落そのものは売買の合図にしない（後知恵のないS&P500全体のバックテストでは、急騰の翌日に買うルールは年率7%、急落の翌日に買うルールは年率9〜10%で、採用した3つのルールより優れていなかった）。

| 銘柄 | グループ | 前日比 | 出来高（50日平均の倍） | 終値 | 50日線 | RS | 局面 |
|---|---|---|---|---|---|---|---|
| FFIV | 光・通信・ネットワーク | -20.4% | 6.5倍 | 365.53 | 下 | 64 | レンジ |
| VRT | データセンターの電力・冷却・部品・受託製造・建設 | +16.5% | 3.6倍 | 242.94 | 下 | 61 | レンジ |
| FLEX | データセンターの電力・冷却・部品・受託製造・建設 | +11.6% | 3.3倍 | 93.03 | 下 | 65 | レンジ |
| ORCL | AIプラットフォーム・クラウド | +10.7% | 2.8倍 | 144.54 | 上 | 16 | レンジ |
| SNDK | AIサーバー・ストレージ・メモリ・端末 | +7.7% | 0.9倍 | 1404.77 | 下 | 99 | レンジ |
| CRWV | AIプラットフォーム・クラウド | +7.3% | 1.6倍 | 63.93 | 下 | 2 | レンジ |
| NBIS | AIプラットフォーム・クラウド | +7.0% | 1.3倍 | 182.34 | 下 | 90 | レンジ |
| FTNT | AIソフト・セキュリティ・ITサービス | -5.9% | 2.5倍 | 174.08 | 上 | 96 | 上昇相場 |
| MU | 半導体 | +5.9% | 1.2倍 | 983.23 | 上 | 98 | 上昇相場 |
| LITE | 光・通信・ネットワーク | +5.5% | 1.0倍 | 913.95 | 下 | 98 | レンジ |
| LRCX | 半導体製造装置・材料・設計ソフト・計測 | +5.4% | 1.2倍 | 253.82 | 下 | 59 | レンジ |
| AMAT | 半導体製造装置・材料・設計ソフト・計測 | +5.1% | 1.1倍 | 416.00 | 下 | 76 | レンジ |
| STX | AIサーバー・ストレージ・メモリ・端末 | +4.5% | 2.4倍 | 697.97 | 下 | 95 | レンジ |
| GEV | データセンターの電力・冷却・部品・受託製造・建設 | -1.9% | 2.6倍 | 878.03 | 下 | 56 | レンジ |
| TEL | データセンターの電力・冷却・部品・受託製造・建設 | -1.8% | 2.1倍 | 221.24 | 上 | 48 | レンジ |
| GOOGL | AIプラットフォーム・クラウド | +1.3% | 2.2倍 | 324.89 | 下 | 39 | レンジ |
| NXPI | 半導体 | -0.7% | 2.7倍 | 251.69 | 上 | 45 | レンジ |
| HUBB | データセンターの電力・冷却・部品・受託製造・建設 | +0.7% | 2.2倍 | 437.33 | 下 | 18 | レンジ |

- 局面: 終値 > 50日線 > 200日線、50日線が20取引日前より2%以上高い、ADX(14) ≧ 20 をすべて満たせば上昇相場、それ以外はレンジ（判定式はClaudeが置いたもの）。

## 4-2. 監視外の注目銘柄（S&P500・NASDAQ100のうち監視銘柄に入っていない銘柄）

条件: 流動性（株価5ドル以上・50日平均出来高25万株以上）があり、(a) 前日比+8%以上かつ出来高が50日平均の2倍以上、または (b) 終値が直前1年の最高値（終値）を上回り、RS≧90。RSの高い順に5銘柄（ニュースを調べる）。監視銘柄に入れるかはユーザーが決める。

| 銘柄 | 種類 | 前日比 | 出来高（50日平均の倍） | RS | 終値 |
|---|---|---|---|---|---|
| CRL | 1年の高値更新 | +4.2% | 1.3倍 | 97 | 373.98 |
| RVTY | 1年の高値更新 | +2.1% | 1.1倍 | 96 | 165.33 |
| TRGP | 1年の高値更新 | +1.1% | 0.8倍 | 94 | 305.90 |
| WST | 1年の高値更新 | +1.3% | 1.4倍 | 93 | 403.64 |
| A | 1年の高値更新 | +2.2% | 0.6倍 | 93 | 181.48 |

- ほかに5銘柄: VTRS（1年の高値更新、RS 92）、WAT（1年の高値更新、RS 92）、HAS（1年の高値更新、RS 92）、AMGN（1年の高値更新、RS 91）、LH（急騰、RS 88）

## 5. 保有銘柄の手じまい条件（`新分析ツール/保有銘柄.md`）

| 銘柄 | ルール | 買った日 | 買値 | 終値 | 損益 | 損切り価格（買値の15%下、逆指値） | ルールの手じまい条件 | 出来高2倍の大陰線（買った後の直近5日） | 次回決算予定日 |
|---|---|---|---|---|---|---|---|---|---|
| SNDK | ルール外（ユーザーの判断。この日はどのルールの合図もなし） | 2026-10-21 | 1371.30 | 1404.77 | +2.4% | 1165.61 | ルールが不明（保有銘柄.md の「ルール」を確認） | なし | 2026-10-29 |
| AMD | ボリンジャーIII | 2026-10-21 | 549.97 | 578.44 | +5.2% | 467.47 | 売りの指値: 上部バンド 667.50（今夜この値に置き直す。届いた日に売れる）（2倍ETF AMUU で持っている場合も、判定は元の株 AMD の値段） | なし | 2026-11-03 |

- 出来高2倍の大陰線: 実体（始値−終値）が前日までのATR(14)の1.5倍以上、終値がその日の値幅の下25%以内、出来高が前日までの50日平均の2倍以上の日。**押し目（ボリンジャーIII）・急落の底の保有では売りのルール**: 出たら翌日の寄り付きで全部売り、空いた枠で次の合図を買う（2026-10-02 ユーザー決定。`バックテスト結果/やり直し_売りの合図の組み合わせ.md`。乱数3組とも年率が約+2ポイント、最大下落率もやや下がった）。ミネルヴィニ・新高値V2の保有では事実の表示（順張りに足しても良くならなかった）。

- 半分売りの合図（ミネルヴィニ・新高値V2の保有だけ）: 反転のローソク足（かぶせ線・弱気の包み足・宵の明星・流れ星）＋出来高が50日平均の1.5倍以上＋RSI(14)が前日か当日に70以上。買った後に最初に出た日の翌日の寄り付きで半分売り、残り半分は50日線割れ・損切り15%まで持つ（2026-10-01 ユーザー決定。`バックテスト結果/半分だけ売るとオニールの空き枠.md`）。

- かぶせ線（ミネルヴィニ・新高値V2の保有だけ）: 上昇中の陽線の翌日に、前日の高値より上で寄り付き、前日の陽線の真ん中より下（前日の始値より上）で引けた日。翌日の寄り付きで全部売り、空いた枠で次の合図を買う。半分売りより優先する（2026-10-01 ユーザー決定。`バックテスト結果/2倍ETFで売って買い直す.md`。順張りの売買の25%で出て、1回平均+2.0%、年率 21.4%→26.4%）。

## 5-2. 前日（2026-10-27の引け）の【買い（予約）】の確認

前日の【買い（予約）】はなし。

## 6. 候補（採用したルールの条件が成立＝A。予約（B）は2026-10-25から注文せず、節6-3に参考の表示だけ）

建玉の目安: 同時保有4銘柄まで、1銘柄に資金の25%（資金÷4）、損切りは買値の15%下（ユーザー決定 2026-09-29）。

パターン: A＝最新の足で採用ルールの条件が成立（翌日の寄り付きで成行）。条件の成立が目前の銘柄（B）は、予約の注文をやめたので節6-3に参考として出す（2026-10-25 ユーザー決定）。

| 銘柄 | グループ | パターン | 種類 | ルールの過去の成績 | 終値 | 前日比 | RS | 50日線の傾き | 局面 | 当てはまった条件 | 次回決算予定日 | 注文の目安 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| FFIV | 光・通信・ネットワーク | A | 逆張り: 急落の底（担当: コナーズ） | 2位（勝率65%・1回平均+2.1%） | 365.53 | -20.4% | 64 | +5.0% | レンジ | 直前5日の最高値（終値）から-20.8%下落（−15%以上）、RSI(2)=2.5（≦10）、急落の前は50日線＞200日線。市場全体の局面: S&P500 上昇／NASDAQ100 上昇 | 2027-01-26（90日後） | 翌日の寄り付きで買い。損切り: 買値の15%下。手じまい: 終値が5日線（今日 438.40）を上回った翌日の寄り付き（コナーズ）。**株数の目安: 6株**（2,384ドル÷365.53。今日の終値。寄り付きの値段で変わる）、購入金額 約2,193ドル |
| HUBB | データセンターの電力・冷却・部品・受託製造・建設 | A | 逆張り: ボリンジャー メソッドIII | 3位（勝率68%・1回平均+1.5%） | 437.33 | +0.7% | 18 | -2.4% | レンジ | %b=0.007（<0.05）、21日II%=+0.071（>0） | 2026-10-27（-1日後） | 翌日の寄り付きで買い。損切り: 買値の15%下。手じまい: 買った日の夜から、売りの指値をその日の上部バンド（今日 492.49）に置き、毎晩その日の値に置き直す。**株数の目安: 5株**（2,384ドル÷437.33。今日の終値。寄り付きの値段で変わる）、購入金額 約2,187ドル |
| VLO | テーマの外（Oil & Gas Refining & Marketing） | A | 逆張り: ボリンジャー メソッドIII | 3位（勝率68%・1回平均+1.5%） | 388.48 | +0.3% | 96 | +12.7% | レンジ | %b=-0.014（<0.05）、21日II%=+0.005（>0） | 2026-10-22（-6日後） | 翌日の寄り付きで買い。損切り: 買値の15%下。手じまい: 買った日の夜から、売りの指値をその日の上部バンド（今日 465.18）に置き、毎晩その日の値に置き直す。**株数の目安: 6株**（2,384ドル÷388.48。今日の終値。寄り付きの値段で変わる）、購入金額 約2,331ドル |

- 2倍ETF: 2倍ETFがある銘柄（ユーザーがムームー証券で買えることを確認した38銘柄のうち、目減りが年15%未満のもの）は、株の代わりに2倍ETFを買う（2026-10-04 ユーザー決定。`バックテスト結果/2倍ETFを使う決まり.md`。年率 約27%→約33%、確定した損益だけの最大下落率 約30%→約31%、含み損込みは約33%→約45%）。買う金額は株と同じ（資金の25%）。合図・損切り（元の株の買値の15%下＝ETFでは約30%下）・手じまいはすべて元の株の値段で判定する。指値・逆指値はETFの値段に直して置く。どのETFかは `新分析ツール/2倍ETFの対応表.json`（売買代金が1日500万ドル以上で、直近1年の目減りが一番小さいもの）。**2倍ETFで買うのは、S&P500が20週線（100日線）で「上昇」の局面のときだけ。横ばい・下落の局面では元の株で買う**（案1、2026-10-13 ユーザー採用。買う日に決め、買った後は局面が変わってもそのまま持つ。`バックテスト結果/流れ（市場の局面）を使う形.md`）。

- ルールの過去の成績: 今の売りのルールで、後知恵なしの監視銘柄・2015年〜の全部の合図の1回ごとの成績（2026-10-02計算、`新分析ツール/バックテスト結果/ルールごとの成績.md`）。順位は1回平均（1回の売買で平均いくら増えるか）の順。表はパターン（A→B）ごとに、この順位の良い順に並べた（表示の順番だけ。買う順番・件数の上限は変えていない。候補の選び方を変えても成績は変わらなかったため。2026-10-02 ユーザーの指示）。著者には渡さない。

- 候補の数: 空き枠2（同時保有4銘柄まで。保有2、うち今日ルールの売りが成立0）＋予備2件まで表に出した（2026-10-25 ユーザー決定）。省いた候補はない。

- テーマの外の候補（グループが「テーマの外」）: 監視銘柄の候補で枠が埋まらないときに使う（監視銘柄の候補を先に買う）。S&P500の今の構成銘柄のうち監視銘柄でない銘柄から、RS≧90・30週線が上向きで終値がその上・業種の3カ月の強さが上位20%の16銘柄を調べ、空き枠2つ分まで出した。バックテストでは、テーマの外の強い銘柄で空き枠を埋めると、テーマが弱い時期の成績が支えられた（`バックテスト結果/半導体・AIに特化した場合.md`。2026-10-01 ユーザー決定）。

- RS≧80の押し目（ボリンジャーIII）は、バックテストで成績がより安定していた（PF3.27、最大下落20%）。

## 6-3. 参考: 条件の成立が目前の銘柄（予約は注文しない・著者には送らない）

2026-10-25 ユーザー決定: 予約（逆指値・指値）の注文はやめ、参考の表示だけにする。毎朝のツールと同じ条件・値段で予約の約定をバックテストに入れると、どの形も年率が下がった（後知恵なし 35.7%→30.7〜34.2%、87銘柄 45.6%→34.2〜42.6%。`バックテスト結果/点検_2026-10-25/`）。引けで条件がそろえば、翌朝の節6に買いの候補（A）として出る。各ルールでRSの高い順に2件まで。

| 参考の銘柄 | グループ | 種類 | 終値 | 前日比 | RS | 当てはまった条件 | 条件がそろう目安の価格（注文はしない） |
|---|---|---|---|---|---|---|---|
| ADI | 半導体 | ミネルヴィニ（ピボットの手前） | 428.27 | +0.7% | 90 | ピボット（ベースの高値、2026-06-22）444.56まで3.8%、ベース90日・調整幅22% | 444.56（この値を上回って引け、ほかの条件もそろうと翌朝の買いの候補（A）。目安） |
| JCI | データセンターの電力・冷却・部品・受託製造・建設 | ミネルヴィニ（ピボットの手前） | 157.35 | +0.9% | 84 | ピボット（ベースの高値、2026-10-06）160.41まで1.9%、ベース16日・調整幅12% | 160.41（この値を上回って引け、ほかの条件もそろうと翌朝の買いの候補（A）。目安） |
| TT | データセンターの電力・冷却・部品・受託製造・建設 | ボリンジャー メソッドIII（%bが0.05未満に近い） | 448.47 | -2.7% | 47 | %b=0.100（0.05まであと少し）、21日II%=+0.006（>0） | 446.49（この値より下で引けると翌朝の買いの候補（A）。目安） |


# ニュース（サブエージェントの調査）

# ニュース調査（2026-10-28の引け時点）

調査方法: headlines.md の見出しを先に読み、見出しで分からないものだけWebSearch（5回。結果は古い記事が多く、当日の確認は限定的）。

## テーマ全体の下げの原因
- 下げの追加調査の対象日ではない（1週−5%以下のグループなし、前日比−5%以下の監視銘柄はFFIV・FTNTの2銘柄、S2は継続中: SOXが60日高値から−11.6%）。
- 参考: 信用の材料は継続。Morningstar（10/28）「CoreWeaveの信用不安がAI取引に示すもの」、Bloomberg（10/28）「AI債券の大量発行で信用市場が消化不良」。CoreWeaveは10月に−38%（Yahoo Finance 10/26）、社債利回りの上昇（CNBC 10/23）。

## 上げの材料（テーマ全体が上げた日）
- 4節で+5%以上が10銘柄（VRT・FLEX・ORCL・SNDK・CRWV・NBIS・MU・LITE・LRCX・AMAT）。
- メモリ: SK Hynixが過去最高の第3四半期決算を発表（Motley Fool／Business Insider／TradingView、10/28）。Micron・Nvidia・AI半導体が上昇。Yahoo Finance（10/28）は「AMD・Broadcom・Micronが3日続けて半導体を押し上げ」。
- Oracle: 分析家向け説明会で2030年度売上$2,250億の目標、キャッシュフローの黒字回復を提示（Yahoo Finance／Bloomberg／Investopedia、10/28）。
- データセンター関連の決算: Vertiv（受注が倍増）、Flex、Amphenol（IBD 10/28）。
- 市場全体: FRBは金利据え置き、NY株は3日続伸（+97ドル、Reuters／共同通信 10/28）。Barchart（10/28）は「半導体株は2008年以来で最大の変動」。

## 引け後・時間外の材料
- Alphabet: 決算後の時間外で6〜9%安。フリーキャッシュフローの赤字が予想超え、巨額投資に見合う収益への懸念（Reuters／株探 10/28）。
- Microsoft: Azureが好調で決算が予想超え、時間外で+2%超（Investing.com 10/28）。
- Fortinet・ServiceNow: 決算後の時間外で下落、サイバーセキュリティ株が連れ安（Benzinga／IBD 10/28）。
- 備考: scan.md ではFTNTが引けで−5.9%。時間外の下げとの前後関係は見出しだけでは確認できなかった。

## FFIV
- 10/28 決算（2026年度第4四半期）後に−20%、10年以上で最悪の日（GeekWire／Barron's 10/28）。
- 理由: 2027年度の成長見通しが弱い、AI投資の費用負担、ハードウェア更新の伸びの鈍化（Proactive／Barron's／GuruFocus 10/28）。
- 次回決算日: 2027-01-26（scan.md）。
- 悪材料: あり（見通しの下方、上記）。

## VRT
- 決算で受注（オーガニック）が倍増以上、好調な見通し（Barron's／IBD／Yahoo Finance／GuruFocus 10/28）。同日にAmphenolも決算で上昇（IBD）。
- 悪材料: 確認できず。

## FLEX
- 2027年度第2四半期は過去最高のEPS、見通し引き上げ（Yahoo Finance／GuruFocus 10/28）。AIインフラ部門の分離（スピンオフ）計画（Barron's 10/28）。
- 悪材料: 確認できず。

## ORCL
- 上記の分析家説明会。2030年度売上$2,250億（Yahoo Finance 10/28）、NvidiaのVera CPUがOracle Cloudで利用可能に（GuruFocus 10/28）。
- 悪材料: 確認できず。

## SNDK（保有）
- 10/22 メモリ株の下げで−8%（24/7 Wall St.）、AI費用への懸念（Benzinga）。10/28 +7.7%はSK Hynix決算を受けたメモリ株の上げ（Barron's 10/28）。
- 次回決算 2026-10-29（scan.md）。決算前の期待を書いた記事あり（Seeking Alpha 10/26）。
- 悪材料: 確認できず（過去1カ月で−23%、24/7 Wall St. 10/28）。

## CRWV / NBIS
- CRWVは10/22に2026年の安値、10/23に社債利回りが急上昇（CNBC）。10/25 Bernsteinは「底を打っていない」（Barchart）。10/26 Muskが「ネオクラウドは小魚のような死」と発言（Yahoo Finance）。10/28は反発（IBD）。NBISは10/22に−7%（Opening Bell Daily）。
- 悪材料: あり（社債の利回り上昇・信用不安。上記）。

## AMD（保有）
- 10/28 Yahoo Finance: AMDが半導体の上げを3日続けて牽引。個別の悪材料は見つからなかった。次回決算 2026-11-03（scan.md）。
- 悪材料: 確認できず。

## HUBB（候補）
- 第3四半期決算を10/27 寄り付き前に発表予定だったが（会社発表 10/13）、結果の記事は検索で見つからなかった。コンセンサスはEPS $5.77、売上約$18.5億。
- 悪材料: 確認できず（決算内容は未確認）。

## VLO / ADI / JCI / TT
- VLO: 業種（石油精製）は3カ月+25.8%（scan.md）。個別のニュースは今回調べていない（見出し・検索に出ず）。決算は10/22に発表済み。
- ADI・JCI・TT: 調べていない。いずれも悪材料は確認できず（未調査）。

## 監視外の注目銘柄
- CRL: 10/23終値$345、10月に高値更新を続ける（stockanalysis.com）。8月に決算後の高値更新（MarketBeat）。業種はヘルスケア（受託研究）。10/28の個別の原因は見つからなかった。
- RVTY・WST・A: ヘルスケア・診断・研究機器の業種で、ヘルスケア系の強さが続く（scan.md 3節: Diagnostics & Research 3カ月+23.0%）。個別の原因は未調査。
- TRGP: 石油・ガス関連の高値更新（業種の強さはscan.md 3節）。個別の原因は未調査。

## テーマ全体のその他
- 市場全体の材料: Boston Scientificがサイバー攻撃の影響で見通しを下方修正（Motley Fool 10/28）。Anthropic IPOへの懸念は後退（マネクリ 10/28）。

# ニュースの見出し（プログラムが自動で取得）

- Googleニュース（日付を指定）とYahooファイナンスの見出しを `tools/news_headlines.py` が自動で並べたもの。日付は米国東部時間の配信日（引け後の記事は翌日付）。原因の判断・売買の判断はしていない。
- 調べた銘柄の選び方: 1週の騰落率（中央値）が−5%以下のグループごとに下げの大きい3銘柄＋1日で−7%以下の銘柄（最大12）と、+5%以上のグループごとに上げの大きい3銘柄＋1日で+7%以上の銘柄（最大6）。
- 1週で−5%以下のグループ: なし
- 1週で+5%以上のグループ: なし

## 1. 市場全体（2026-10-28）

### 市場全体（英語のまとめ記事）
検索語: `stocks Wall Street close Nasdaq`
- 10/28 24/7 Wall St. | American Households Own More of the Stock Market Than at Any Time Since the Dot-Com Era
- 10/28 Arab News | Closing Bell: Saudi stock market rise gaining 0.37% to close above 10,000
- 10/28 Investor's Business Daily | Stock Market Today: Stock Market News And Analysis
- 10/28 24/7 Wall St. | Oct. 27 Has Historically Marked the Stock Market’s Autumn Bottom
- 10/28 Stock Titan | Stocks Rose a Little After the Fed, Then Fortinet and Alphabet Fell After Their Results

### 市場全体（Stock Market Today）
検索語: `"stock market today"`
- 10/28 The Motley Fool | Stock Market Today, Oct. 28: SK Hynix Surges on Record Q3 Results and AI-Memory Demand
- 10/28 Investor's Business Daily | Tech Futures Fall On Google, These Huge Losers
- 10/28 The Motley Fool | Stock Market Today, Oct. 28: Boston Scientific Slips 6% After Cutting Q4 Sales and Full-Year EPS Guidance on Cyberattack Impact
- 10/28 Yahoo Finance | Stock Market Today, Oct. 28: Oracle Surges on Fiscal 2030 Revenue Guidance of $225 Billion

### 市場全体（日本語のまとめ記事）
検索語: `米国株式市場 OR NY株`
- 10/28 Reuters | 米国株式市場＝続伸、半導体株が高い ＦＲＢは据え置き
- 10/28 Yahoo!ニュース | NY株3日続伸、97ドル高 米金利据え置きで買い優勢（共同通信）
- 10/28 沖縄タイムス社 | ＮＹ株３日続伸、９７ドル高 米金利据え置きで買い優勢
- 10/28 京都新聞デジタル | ＮＹ株３日続伸、９７ドル高
- 10/28 47NEWS | 【速報】NY株3日続伸、97ドル高

### 半導体・AI株（英語）
検索語: `chip stocks OR semiconductor stocks OR AI stocks`
- 10/28 Yahoo Finance | AMD, Broadcom, and Micron stocks lead chip sector higher for third day in a row
- 10/28 Barchart.com | Chip Stocks Experienced Their Most Intense Volatility Since 2008. Trade the Rebound or the Retreat With 3X ETFs
- 10/28 Fast Company | Memory chip stocks are back on the rise today: What's driving the upswing for Micron, Sandisk, and SK Hynix?
- 10/28 TradingView | SK Hynix Record Profit Lifts Micron, Nvidia and AI Chip Stocks
- 10/28 Business Insider | SK Hynix's earnings smash sends AI chip stocks up as investors cheer strong demand

### 信用（社債・借金）
検索語: `AI debt OR bonds OR credit spreads OR CDS`
- 10/28 Morningstar | Here’s What CoreWeave’s Credit Woes Tell Investors About the AI Trade
- 10/28 Bloomberg.com | Japan Credit Risk Jumps Most Since 2022, Pressuring Bond Market
- 10/28 https://economy.ac/ | “Overinvestment Fears Turn Into Credit Concerns”: Debt-Fueled AI Data Centers Face Tests From Financing to Survival
- 10/28 Tri-City Herald | AI worries expose dollar's hot-money problem
- 10/28 Bloomberg.com | AI Debt Deluge Gives Credit Market Indigestion

### 「〇〇ショック」の呼び名（日本語）
検索語: `ショック 株`
- 10/28 Yahoo!ファイナンス | ＦＲＢ、供給ショックの「一過性」に柔軟な見方を＝米財務長官(ロイター)
- 10/28 マネクリ | 【米国株・動画解説】アンソロピックIPOに対する懸念は後退、米国株のブル相場は5年目へ
- 10/28 毎日新聞 | オリコンニュース：投資家の桐谷さん、保有株にネット衝撃 先週買った株が株価上昇「タイミングがすごい」
- 10/28 日本経済新聞 | SK、株主還元で7兆円を追加 キオクシア株利益活用し現金も配当
- 10/28 トウシル | 安踏体育用品（アンタ・スポーツ・プロダクツ）

### 引け後・時間外の動き（英語）
検索語: `"after hours" OR "after the bell" OR "extended trading" stocks`
- 10/28 CNBC | Stocks making the biggest moves after hours: Alphabet, Microsoft, Chipotle, ServiceNow, Fortinet & more
- 10/28 Yahoo Finance | Google misses revenue expectations, Alphabet stock sinks in early after-hours trading
- 10/28 Seeking Alpha | Stocks to watch on Wednesday after hours: GOOG, EBAY, FTNT, NOW (GOOG:NASDAQ)
- 10/28 Investing.com | Microsoft stock up over 2% after hours as Azure strength drives FQ1 results beat
- 10/28 Benzinga | Cybersecurity Stocks Drop After Hours: Here's Why

### 引け後・時間外の動き（日本語）
検索語: `時間外 決算 株`
- 10/28 Yahoo!ファイナンス | アルファベット、決算受け時間外で７％安＝米国株個別速報(株探ニュース)
- 10/28 株探 | アルファベット、決算受け時間外で７％安＝米国株個別速報
- 10/28 Reuters | アルファベット、フリーキャッシュフロー赤字が予想超え 時間外で株価6％超安
- 10/28 Investing.com - FX | 株式市場 | ファイナンス | 金融ニュース | マイクロソフト株が急騰、好決算で時間外取引に大幅上昇 執筆
- 10/28 Yahoo!ファイナンス | アルファベット、決算受け時間外で９％安 巨額投資に見合う収益を生み出せていないとの懸念強まる＝米国株個別(株探ニュース)

## 2. 大きく下げた銘柄（2026-10-22〜2026-10-28 の見出し）

### FFIV（F5, Inc.、光・通信・ネットワーク、前日比 -20.4%、1週 -20.3%）

#### Googleニュース
検索語: `F5 stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 10/28 Yahoo Finance | Why F5 Stock Is Getting Crushed Today
- 10/28 GeekWire | F5 stock suffers worst day in more than a decade as AI spending shakes investors
- 10/28 Proactive financial news | F5 stock tumbles as hardware replacement growth slows
- 10/28 Barron's | F5 Stock Is Having Its Worst Day in Over a Decade. Blame Its Costly AI Push.

#### Yahooファイナンス
検索語: `FFIV`
- 10/28 Associated Press | F5: Fiscal Q4 Earnings Snapshot
- 10/28 GuruFocus.com | F5 Stocks Decline 19.34% After Its FY2027 Growth Outlook

## 3. 大きく上げた銘柄（2026-10-22〜2026-10-28 の見出し）

### VRT（Vertiv Holdings Co、データセンターの電力・冷却・部品・受託製造・建設、前日比 +16.5%、1週 +14.5%）

#### Googleニュース
検索語: `Vertiv stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 10/28 Barron's | Vertiv Earnings Set a New Bar for AI Stocks
- 10/28 Yahoo Finance | Vertiv stock surges as orders double amid AI build-out: 'Evolving faster than ever'
- 10/28 Investor's Business Daily | Nvidia Partner Vertiv Soars After Blowout Earnings, Strong Guidance
- 10/28 Moomoo | Vertiv Stock Jumps 14% as Earnings Show Another Way to Play the AI Boom

#### Yahooファイナンス
検索語: `VRT`
- 10/28 GuruFocus.com | Vertiv Stock Rises as Organic Orders More Than Double
- 10/28 Investor's Business Daily | AI Data Center Supplier Amphenol Jumps On Earnings Beat
- 10/28 Investor's Business Daily | Neocloud Stocks Like CoreWeave Rebound Despite Elon Musk Predicting 'Guppy-Level Death'

### FLEX（Flex Ltd.、データセンターの電力・冷却・部品・受託製造・建設、前日比 +11.6%、1週 +7.9%）

#### Googleニュース
検索語: `Flex stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 10/28 Yahoo Finance | Flex (NASDAQ:FLEX) delivers strong Q3 CY2026 numbers, stock soars
- 10/28 Benzinga | Why Is Flex Stock Soaring Wednesday? - Flex (NASDAQ:FLEX)
- 10/28 Seeking Alpha | Flex soars 12% on quarterly results (FLEX:NASDAQ)
- 10/28 Barron's | Flex Stock Rises on Earnings. Its Upcoming AI Infrastructure Spinoff May Be the Real Winner.

#### Yahooファイナンス
検索語: `FLEX`
- 10/28 Associated Press | Flex: Fiscal Q2 Earnings Snapshot
- 10/28 Barrons.com | Flex Stock Rise on Earnings. Its Upcoming AI Infrastructure Spinoff May Be the Real Winner.
- 10/28 GuruFocus.com | Flex Ltd (FLEX) (Q2 2027) Earnings Call Highlights: Record EPS, Raised Guidance and the Axiom ...

### ORCL（Oracle Corporation、AIプラットフォーム・クラウド、前日比 +10.7%、1週 +11.9%）

#### Googleニュース
検索語: `Oracle stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 10/28 Yahoo Finance | Oracle stock soars as it promises the AI spending will start paying for itself
- 10/28 Investopedia | Oracle Stock Jumps 11% on Rosy Long-Term Targets
- 10/28 Bloomberg.com | Oracle Jumps After Projecting Return to Positive Cash Flow
- 10/28 Seeking Alpha | Oracle jumps as company provides long-term guidance at analyst day (ORCL:NYSE)

#### Yahooファイナンス
検索語: `ORCL`
- 10/28 GuruFocus.com | Nvidia Stocks Rise With Vera CPUs Available on Oracle Cloud
- 10/28 Investor's Business Daily | Dow Jones Futures: Microsoft Rises Late, But Google, ServiceNow And Fortinet Dive On Earnings

### SNDK（Sandisk Corporation、AIサーバー・ストレージ・メモリ・端末、前日比 +7.7%、1週 +1.9%）

#### Googleニュース
検索語: `Sandisk stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 10/22 24/7 Wall St. | SanDisk Sinks 8% as Memory Selloff Deepens Ahead of Earnings; Western Digital Drops 7%, Micron Falls 6%
- 10/22 Benzinga | SanDisk Stock Drops as AI Cost Worries Mount
- 10/26 Yahoo Finance | SanDisk Stock Is Back on Wall Street’s Radar. Here’s Where I See It Going
- 10/26 Seeking Alpha | Sandisk: Prepare For Another Jaw-Dropping Blowout (Earnings Preview) (NASDAQ:SNDK)

#### Yahooファイナンス
検索語: `SNDK`
- 10/28 24/7 Wall St. | Sandisk Is Still Down 23% in the Past Month. Did Today Just Mark the Bottom for SNDK Stock?
- 10/28 Barrons.com | Nasdaq Lags Despite Memory Chip Surge. Tech Earnings Can't Come Soon Enough.
- 10/28 CryptoProwl | JPMorgan, Coca-Cola Join Pushback Against OKX-ICE Tokenized Stock Trading

### CRWV（CoreWeave, Inc.、AIプラットフォーム・クラウド、前日比 +7.3%、1週 +3.4%）

#### Googleニュース
検索語: `CoreWeave stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 10/22 Opening Bell Daily | CoreWeave and IREN stock fall to 2026 lows as Nebius drops 7%
- 10/23 CNBC | CoreWeave’s market confidence erodes as bond yields spike and stock sinks
- 10/25 Barchart.com | CRWV Stock Warning: Why Bernstein Says CoreWeave Shares Haven’t Bottomed Out Yet
- 10/26 Yahoo Finance | Musk Predicts “Guppy-Level Death” For Neocloud Companies As CoreWeave Stock Falls 38% In October

#### Yahooファイナンス
検索語: `CRWV`
- 10/28 24/7 Wall St. | CoreWeave Just Fell 31% in a Month: What Will It Take to Get CRWV Stock Back Above $70?
- 10/28 24/7 Wall St. | CoreWeave Vs. Nebius: One Runs the U.S. Government’s Debt Playbook, The Other is Like Norway
- 10/28 24/7 Wall St. | CoreWeave’s Debt Service is The True Neocloud Litmus Test
