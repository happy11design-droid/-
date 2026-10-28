# テーマ監視 2026-10-27
（2026-10-28 夜にユーザーの指示で手動実行。10/28朝のRoutineがNotebookLM認証の失敗で止まったため。10/27の米国引け時点のデータ、ニュース調査あり）

# 判定のまとめ（ルールの判定と著者の判定を分けて表示）

- **ルールの判定**: 採用した売買ルール（スクリプト）が数値で決めたもの。損切りは買値の15%下の逆指値（日中に届けばその場で売れる）。
- **著者の判定**: ノートブックの著者の回答。買いは注文を止める理由があるときだけ【様子見】、保有はルールより早く手じまう理由があるときだけ【売り】。根拠は下の「著者の回答（全文）」。
- 2つが食い違うときに、どちらに従うかはユーザーが決める。

- **テーマ全体の急落（S2・記録だけ）: あり（S2）**（SOXが直近60取引日の最高値から -13.1%）。S2の日の順張りの候補には「S2なら見送る形」と付ける（売買のルールは変えない。記録してから採用を決める。2026-10-14）

## 保有銘柄

| 銘柄 | ルール | 損益 | ルールの判定 | ルールの判定の理由 | 著者の判定 |
|---|---|---|---|---|---|
| SNDK | ルール外（ユーザーの判断。この日はどのルールの合図もなし） | -4.8% | 保有継続 | 損切り 1165.61（終値から -10.7%） | **【未判定】（）** |
| AMD | ボリンジャーIII | +1.9% | 保有継続 | 損切り 467.47（終値から -16.6%） | 【保有継続】（ボリンジャー） |

## 候補の判定（並びは上の「買う順番」の表と同じ）

- 並びは上の「買う順番」の表と同じ（RSの高い順。勝率の高い順ではない）。注文の値段・株数・逆指値は上の表を見る。勝率・1回平均は、そのルールの過去の成績（後知恵なしの監視銘柄・2015年〜の全部の合図）。
- 空き枠: 2（同時保有4銘柄まで。保有2、うちルールの売り0）。著者が【様子見】の候補を見送るかはユーザーが決める。

| 順 | 銘柄 | ルール | 過去の勝率 | 過去の1回平均 | RS | ルールの判定 | 著者の判定 |
|---|---|---|---|---|---|---|---|
| 1 | VLO | 逆張り: ボリンジャー メソッドIII | 68% | +1.5% | 96 | 買い（翌日の寄り付き） | 【買い】（ボリンジャー） |
| 2 | HUBB（ハベル） | 逆張り: ボリンジャー メソッドIII | 68% | +1.5% | 20 | 買い（翌日の寄り付き） | 【買い】（ボリンジャー） |

# 著者の回答（全文）

## 0_テーマの局面_ワインスタイン

1. **テーマ全体の局面**: 【ステージ2】（テーマ指数の30週移動平均線が上向きかつ指数が線より上にあるため。第2章、第8章）
2. **グループごとの局面**:
- 半導体｜ステージ2｜30週線上昇・線より上（第2章）
- 半導体製造装置・材料・設計ソフト・計測｜ステージ1/3｜30週線横ばい・線より下（第2章）
- AIサーバー・ストレージ・メモリ・端末｜ステージ2｜30週線上昇・線より上（第2章）
- 光・通信・ネットワーク｜ステージ1/3｜30週線横ばい・線より下（第2章）
- データセンターの電力・冷却・部品・受託製造・建設｜ステージ1/3｜30週線横ばい・線より下（第2章）
- AIプラットフォーム・クラウド｜ステージ1/3｜30週線横ばい・線より下（第2章）
- AIソフト・セキュリティ・ITサービス｜ステージ2｜30週線上昇・線より上（第2章）
3. **転換の兆し**: 本の基準である30週線の水平化や割れは未発生で、ステージ3・4への確定シグナルはない（第2章、第8章）。ただし、S&P500対比の相対的強さ低下やSOX指数-13.1%調整は警戒すべき変化（第3章、第8章）。
4. **テーマの外**: なし（ヒートマップ省略のため判定不能）

（全体の版が空の応答だったため、1〜2節だけの短い版で送り直した回答。ヒートマップ・急騰急落・ニュースは渡していない）

## 1_ボリンジャー_prompt_1

## AMD
1. **投資判断**: 【保有継続】（危険な形や悪材料はなく保有継続）
2. **止める理由の確認**:
   - 本が禁じる形・状況｜なし｜M型トップ等危険な形は未発生（第13章）
   - 避けるべき時期（決算など）｜なし｜次回決算（11/03）まで間があり規定なし（第15章）
   - 悪材料｜なし｜個別の悪材料報道なし（10/27）
3. **現状パターンと価格**:
   - `現状パターン: C（10/21買付済み・保有中）`
   - `売りの予約注文: 指値売り 670.29（現在値比 +19.6%）`
4. **注意点**: 上部バンドへの到達および11/03の決算発表に留意。

## 1_ボリンジャー_prompt_2

## HUBB
1. **投資判断**: 【買い】（注文を止めるべき本に基づく理由がないため）
2. **止める理由の確認**:
   - 本が禁じる形・状況｜なし｜メソッドIII条件成立（第20章、ルールブック5節）
   - 避けるべき時期（決算など）｜なし｜決算期の制限なし（マニュアルに規定なし）
   - 悪材料｜なし｜確認されず（マニュアルに規定なし・10/27）
3. **現状パターンと価格**:
   - 現状パターン: A（最新足で条件成立）
   - 本日の発注: 翌日の寄り付きで成行
4. **注意点**: 逆張りトレードのため、直近安値下への損切り設定の徹底に留意。

## 1_ボリンジャー_prompt_3

## VLO
1. **投資判断**: 【買い】（メソッドIIIの条件成立）
2. **止める理由の確認**:
   - 本が禁じる形・状況｜なし｜判定用ルールブック 第5節・第20章
   - 避けるべき時期（決算など）｜なし｜マニュアルに規定なし
   - 悪材料｜なし｜マニュアルに規定なし（ニュース：10/27調査なし）
3. **現状パターンと価格**:
   - `現状パターン: A（%b<0.05かつ21日II%>0成立）`
   - `本日の発注: 翌日の寄り付きで成行`
4. **注意点**: 取引実行場所の直近安値付近にストップ（損切り）を設定しリスクを限定すること（第20章） [1, 2]。

# スキャン（数値と事実）


- 監視銘柄 87（判定できたのは 86、取得不可: Q）。
- この一覧は数値と事実だけ。売買の判断は著者のノートブックが行う。

## 1. テーマ（グループ）の強さ

| グループ | 銘柄数 | 1週 | 1カ月 | 3カ月 | 3カ月の順位 | 50日線より上の銘柄の割合 | グループ指数の30週線の局面（線との乖離、4週前からの線の傾き） |
|---|---|---|---|---|---|---|---|
| 半導体 | 16 | +4.0% | -2.4% | +14.8% | 3位 | 56% | 上昇（+5.4%、+6.4%） |
| 半導体製造装置・材料・設計ソフト・計測 | 8 | +0.4% | -7.5% | +3.1% | 6位 | 25% | 横ばい（-6.5%、+2.9%） |
| AIサーバー・ストレージ・メモリ・端末 | 9 | +7.6% | -7.5% | +28.4% | 1位 | 44% | 上昇（+15.3%、+9.3%） |
| 光・通信・ネットワーク | 9 | +3.2% | -6.0% | +6.3% | 5位 | 33% | 横ばい（-2.4%、+3.2%） |
| データセンターの電力・冷却・部品・受託製造・建設 | 19 | +0.6% | -1.2% | -0.4% | 7位 | 37% | 横ばい（-5.4%、+1.0%） |
| AIプラットフォーム・クラウド | 11 | -0.6% | -1.2% | +11.3% | 4位 | 36% | 横ばい（-1.9%、+2.0%） |
| AIソフト・セキュリティ・ITサービス | 14 | +0.7% | +8.9% | +22.3% | 2位 | 86% | 上昇（+24.5%、+5.2%） |

## 2. テーマ全体の状態と早めの警告

- 市場全体の30週線による局面: S&P500指数 **上昇**／NASDAQ100指数 **上昇**（急落の底で買うルールは、過去の検証で下落相場で特に強く、横ばいの相場では負けていた）
- **2倍ETFを使う局面（案1、2026-10-13 採用）: S&P500の20週線（100日線）で 上昇** → 2倍ETFのある銘柄は2倍ETFで買う（SPY 769.66、100日線 756.87、20日前の線 751.23。上昇＝線より上かつ線が上向き）
- **テーマ全体の急落（S2、記録だけ。売買のルールは変えない）: あり（S2）**（SOX 11482.50、直近60取引日の最高値 13217.82 から -13.1%。S2＝最高値から−10%以上）。S2のときに「順張りの新しい買いだけ止める」形を記録で比べる（2026-10-14 ユーザー決定。バックテストでは年率は上がったが2つの期間ではどちらも少し下回ったため、記録してから採用を決める。`バックテスト結果/テーマ全体の急落を検知して手じまう・買いを止める.md`）
- テーマ指数（監視銘柄の等金額平均）の30週線による局面: **上昇**（上昇＝線より上かつ上向き、下落＝線より下かつ下向き、それ以外＝横ばい。ワインスタインのステージの近似）
- テーマ指数と50日線: 50日線より下（乖離 -0.8%）
- S&P500に対する相対的な強さ: 50日平均より下（S&P500より弱い）
- 監視銘柄のうち50日線より上の割合: 48%
- 警告（割合が40%未満かつテーマ指数が50日線より下）: **出ていない**
- 参考（バックテスト）: 30週線の「下落」は高値から10〜33%下げた後に出る遅い判定。50日線・割合・相対的な強さは高値から2〜8%で出るが、誤報が年15回以上ある。警告中に新しい買いを止めると、押し目買い（ボリンジャーIII）の成績は大きく下がった（`バックテスト結果/テーマ監視銘柄・直近3年.md` 11・12節）。

## 3. ヒートマップ（Finviz、全米の業種別の騰落率）

3カ月の騰落率の上位15業種（テーマの外で強くなっている業種の確認用）:

| 順位 | 業種 | 1週 | 1カ月 | 3カ月 | 6カ月 | 1年 |
|---|---|---|---|---|---|---|
| 1 | Health Information Services | -1.0% | +8.1% | +32.0% | +55.8% | -0.3% |
| 2 | Oil & Gas Refining & Marketing | -7.5% | +6.0% | +26.4% | +58.0% | +103.4% |
| 3 | Auto Manufacturers | +4.9% | +12.2% | +20.8% | +7.1% | -9.9% |
| 4 | Diagnostics & Research | +0.3% | +3.0% | +20.1% | +50.4% | +25.6% |
| 5 | Software - Infrastructure | +1.2% | +3.2% | +19.4% | +28.5% | -0.2% |
| 6 | Oil & Gas Drilling | +4.4% | +15.1% | +18.0% | -11.8% | +49.4% |
| 7 | Software - Application | -1.1% | +9.2% | +16.2% | +26.2% | -16.1% |
| 8 | Oil & Gas E&P | +2.3% | +15.3% | +13.8% | +6.8% | +49.3% |
| 9 | Oil & Gas Integrated | -0.3% | +10.5% | +13.7% | +13.2% | +55.0% |
| 10 | Marine Shipping | +1.6% | +3.4% | +11.6% | +14.2% | +77.6% |
| 11 | Real Estate - Diversified | +4.5% | +5.6% | +11.3% | +9.0% | +12.3% |
| 12 | Shell Companies | -1.6% | +5.1% | +10.8% | +19.8% | +15.9% |
| 13 | Information Technology Services | -1.7% | +13.4% | +10.5% | +6.7% | -22.4% |
| 14 | Coking Coal | +4.4% | +0.7% | +10.1% | -5.4% | +1.4% |
| 15 | Gold | -4.0% | -5.9% | +9.9% | -3.9% | +21.8% |

テーマの業種の順位（3カ月、全144業種中）: Semiconductors 22位、Semiconductor Equipment & Materials 119位、Computer Hardware 64位、Communication Equipment 33位、Electronic Components 75位、Software - Infrastructure 5位、Software - Application 7位、Internet Content & Information 59位

## 4. 急騰・急落した銘柄（前日比±5%以上、または出来高が50日平均の2倍以上）

原因のニュースをサブエージェントが調べ、候補・保有銘柄の判定材料として著者に渡す。急騰・急落そのものは売買の合図にしない（後知恵のないS&P500全体のバックテストでは、急騰の翌日に買うルールは年率7%、急落の翌日に買うルールは年率9〜10%で、採用した3つのルールより優れていなかった）。

| 銘柄 | グループ | 前日比 | 出来高（50日平均の倍） | 終値 | 50日線 | RS | 局面 |
|---|---|---|---|---|---|---|---|
| NBIS | AIプラットフォーム・クラウド | +11.2% | 1.1倍 | 170.47 | 下 | 92 | レンジ |
| ALAB | 半導体 | +10.5% | 1.2倍 | 286.69 | 下 | 94 | レンジ |
| FLEX | データセンターの電力・冷却・部品・受託製造・建設 | +8.3% | 3.0倍 | 83.35 | 下 | 44 | レンジ |
| CRWV | AIプラットフォーム・クラウド | +7.9% | 1.4倍 | 59.57 | 下 | 2 | レンジ |
| DELL | AIサーバー・ストレージ・メモリ・端末 | +7.5% | 0.8倍 | 501.96 | 下 | 99 | レンジ |
| SMCI | AIサーバー・ストレージ・メモリ・端末 | +7.3% | 0.8倍 | 35.09 | 下 | 78 | レンジ |
| WDC | AIサーバー・ストレージ・メモリ・端末 | +6.9% | 1.1倍 | 380.88 | 下 | 93 | レンジ |
| CDNS | 半導体製造装置・材料・設計ソフト・計測 | +6.5% | 1.9倍 | 343.08 | 上 | 46 | レンジ |
| COHR | 光・通信・ネットワーク | +6.5% | 0.9倍 | 235.79 | 下 | 76 | レンジ |
| ON | 半導体 | +6.2% | 0.9倍 | 78.67 | 上 | 70 | レンジ |
| LITE | 光・通信・ネットワーク | +5.9% | 1.2倍 | 866.18 | 下 | 98 | レンジ |
| JCI | データセンターの電力・冷却・部品・受託製造・建設 | +5.7% | 1.8倍 | 155.88 | 上 | 84 | レンジ |
| MCHP | 半導体 | +5.6% | 1.3倍 | 80.17 | 上 | 68 | レンジ |
| ANET | 光・通信・ネットワーク | +5.5% | 1.1倍 | 187.00 | 下 | 82 | レンジ |
| HUBB | データセンターの電力・冷却・部品・受託製造・建設 | -5.5% | 3.6倍 | 434.28 | 下 | 20 | レンジ |
| AMD | 半導体 | +5.5% | 1.0倍 | 560.26 | 上 | 97 | 上昇相場 |
| TEL | データセンターの電力・冷却・部品・受託製造・建設 | +5.4% | 2.1倍 | 225.35 | 上 | 51 | レンジ |
| STX | AIサーバー・ストレージ・メモリ・端末 | +3.7% | 2.1倍 | 667.85 | 下 | 95 | レンジ |
| META | AIプラットフォーム・クラウド | -1.6% | 2.5倍 | 620.19 | 下 | 27 | レンジ |
| FFIV | 光・通信・ネットワーク | -0.5% | 3.1倍 | 459.36 | 上 | 94 | レンジ |

- 局面: 終値 > 50日線 > 200日線、50日線が20取引日前より2%以上高い、ADX(14) ≧ 20 をすべて満たせば上昇相場、それ以外はレンジ（判定式はClaudeが置いたもの）。

## 4-2. 監視外の注目銘柄（S&P500・NASDAQ100のうち監視銘柄に入っていない銘柄）

条件: 流動性（株価5ドル以上・50日平均出来高25万株以上）があり、(a) 前日比+8%以上かつ出来高が50日平均の2倍以上、または (b) 終値が直前1年の最高値（終値）を上回り、RS≧90。RSの高い順に5銘柄（ニュースを調べる）。監視銘柄に入れるかはユーザーが決める。

| 銘柄 | 種類 | 前日比 | 出来高（50日平均の倍） | RS | 終値 |
|---|---|---|---|---|---|
| CRL | 1年の高値更新 | +0.4% | 1.1倍 | 96 | 358.84 |
| RVTY | 1年の高値更新 | +0.9% | 0.8倍 | 95 | 161.86 |
| VTRS | 1年の高値更新 | +2.4% | 0.7倍 | 91 | 18.72 |
| WST | 1年の高値更新 | +0.9% | 1.5倍 | 91 | 398.29 |
| HAS | 1年の高値更新 | +0.3% | 1.2倍 | 91 | 118.33 |

- ほかに3銘柄: EXPD（1年の高値更新、RS 91）、AMGN（1年の高値更新、RS 90）、PNR（急騰、RS 5）

## 5. 保有銘柄の手じまい条件（`新分析ツール/保有銘柄.md`）

| 銘柄 | ルール | 買った日 | 買値 | 終値 | 損益 | 損切り価格（買値の15%下、逆指値） | ルールの手じまい条件 | 出来高2倍の大陰線（買った後の直近5日） | 次回決算予定日 |
|---|---|---|---|---|---|---|---|---|---|
| SNDK | ルール外（ユーザーの判断。この日はどのルールの合図もなし） | 2026-10-21 | 1371.30 | 1304.84 | -4.8% | 1165.61 | ルールが不明（保有銘柄.md の「ルール」を確認） | なし | 2026-10-29 |
| AMD | ボリンジャーIII | 2026-10-21 | 549.97 | 560.26 | +1.9% | 467.47 | 売りの指値: 上部バンド 670.29（今夜この値に置き直す。届いた日に売れる）（2倍ETF AMUU で持っている場合も、判定は元の株 AMD の値段） | なし | 2026-11-03 |

- 出来高2倍の大陰線: 実体（始値−終値）が前日までのATR(14)の1.5倍以上、終値がその日の値幅の下25%以内、出来高が前日までの50日平均の2倍以上の日。**押し目（ボリンジャーIII）・急落の底の保有では売りのルール**: 出たら翌日の寄り付きで全部売り、空いた枠で次の合図を買う（2026-10-02 ユーザー決定。`バックテスト結果/やり直し_売りの合図の組み合わせ.md`。乱数3組とも年率が約+2ポイント、最大下落率もやや下がった）。ミネルヴィニ・新高値V2の保有では事実の表示（順張りに足しても良くならなかった）。

- 半分売りの合図（ミネルヴィニ・新高値V2の保有だけ）: 反転のローソク足（かぶせ線・弱気の包み足・宵の明星・流れ星）＋出来高が50日平均の1.5倍以上＋RSI(14)が前日か当日に70以上。買った後に最初に出た日の翌日の寄り付きで半分売り、残り半分は50日線割れ・損切り15%まで持つ（2026-10-01 ユーザー決定。`バックテスト結果/半分だけ売るとオニールの空き枠.md`）。

- かぶせ線（ミネルヴィニ・新高値V2の保有だけ）: 上昇中の陽線の翌日に、前日の高値より上で寄り付き、前日の陽線の真ん中より下（前日の始値より上）で引けた日。翌日の寄り付きで全部売り、空いた枠で次の合図を買う。半分売りより優先する（2026-10-01 ユーザー決定。`バックテスト結果/2倍ETFで売って買い直す.md`。順張りの売買の25%で出て、1回平均+2.0%、年率 21.4%→26.4%）。

## 5-2. 前日（2026-10-26の引け）の【買い（予約）】の確認

前日の【買い（予約）】はなし。

## 6. 候補（採用したルールの条件が成立＝A。予約（B）は2026-10-25から注文せず、節6-3に参考の表示だけ）

建玉の目安: 同時保有4銘柄まで、1銘柄に資金の25%（資金÷4）、損切りは買値の15%下（ユーザー決定 2026-09-29）。

パターン: A＝最新の足で採用ルールの条件が成立（翌日の寄り付きで成行）。条件の成立が目前の銘柄（B）は、予約の注文をやめたので節6-3に参考として出す（2026-10-25 ユーザー決定）。

| 銘柄 | グループ | パターン | 種類 | ルールの過去の成績 | 終値 | 前日比 | RS | 50日線の傾き | 局面 | 当てはまった条件 | 次回決算予定日 | 注文の目安 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| HUBB | データセンターの電力・冷却・部品・受託製造・建設 | A | 逆張り: ボリンジャー メソッドIII | 3位（勝率68%・1回平均+1.5%） | 434.28 | -5.5% | 20 | -2.3% | レンジ | %b=-0.117（<0.05）、21日II%=+0.027（>0） | 2026-10-27（0日後）**決算が近い** | 翌日の寄り付きで買い。損切り: 買値の15%下。手じまい: 買った日の夜から、売りの指値をその日の上部バンド（今日 490.89）に置き、毎晩その日の値に置き直す。**株数の目安: 5株**（2,384ドル÷434.28。今日の終値。寄り付きの値段で変わる）、購入金額 約2,171ドル |
| VLO | テーマの外（Oil & Gas Refining & Marketing） | A | 逆張り: ボリンジャー メソッドIII | 3位（勝率68%・1回平均+1.5%） | 387.34 | -9.2% | 96 | +13.0% | レンジ | %b=-0.026（<0.05）、21日II%=+0.032（>0） | 2026-10-22（-5日後） | 翌日の寄り付きで買い。損切り: 買値の15%下。手じまい: 買った日の夜から、売りの指値をその日の上部バンド（今日 465.32）に置き、毎晩その日の値に置き直す。**株数の目安: 6株**（2,384ドル÷387.34。今日の終値。寄り付きの値段で変わる）、購入金額 約2,324ドル |

- 2倍ETF: 2倍ETFがある銘柄（ユーザーがムームー証券で買えることを確認した38銘柄のうち、目減りが年15%未満のもの）は、株の代わりに2倍ETFを買う（2026-10-04 ユーザー決定。`バックテスト結果/2倍ETFを使う決まり.md`。年率 約27%→約33%、確定した損益だけの最大下落率 約30%→約31%、含み損込みは約33%→約45%）。買う金額は株と同じ（資金の25%）。合図・損切り（元の株の買値の15%下＝ETFでは約30%下）・手じまいはすべて元の株の値段で判定する。指値・逆指値はETFの値段に直して置く。どのETFかは `新分析ツール/2倍ETFの対応表.json`（売買代金が1日500万ドル以上で、直近1年の目減りが一番小さいもの）。**2倍ETFで買うのは、S&P500が20週線（100日線）で「上昇」の局面のときだけ。横ばい・下落の局面では元の株で買う**（案1、2026-10-13 ユーザー採用。買う日に決め、買った後は局面が変わってもそのまま持つ。`バックテスト結果/流れ（市場の局面）を使う形.md`）。

- ルールの過去の成績: 今の売りのルールで、後知恵なしの監視銘柄・2015年〜の全部の合図の1回ごとの成績（2026-10-02計算、`新分析ツール/バックテスト結果/ルールごとの成績.md`）。順位は1回平均（1回の売買で平均いくら増えるか）の順。表はパターン（A→B）ごとに、この順位の良い順に並べた（表示の順番だけ。買う順番・件数の上限は変えていない。候補の選び方を変えても成績は変わらなかったため。2026-10-02 ユーザーの指示）。著者には渡さない。

- 候補の数: 空き枠2（同時保有4銘柄まで。保有2、うち今日ルールの売りが成立0）＋予備2件まで表に出した（2026-10-25 ユーザー決定）。省いた候補はない。

- テーマの外の候補（グループが「テーマの外」）: 監視銘柄の候補で枠が埋まらないときに使う（監視銘柄の候補を先に買う）。S&P500の今の構成銘柄のうち監視銘柄でない銘柄から、RS≧90・30週線が上向きで終値がその上・業種の3カ月の強さが上位20%の16銘柄を調べ、空き枠2つ分まで出した。バックテストでは、テーマの外の強い銘柄で空き枠を埋めると、テーマが弱い時期の成績が支えられた（`バックテスト結果/半導体・AIに特化した場合.md`。2026-10-01 ユーザー決定）。

- RS≧80の押し目（ボリンジャーIII）は、バックテストで成績がより安定していた（PF3.27、最大下落20%）。

## 6-3. 参考: 条件の成立が目前の銘柄（予約は注文しない・著者には送らない）

2026-10-25 ユーザー決定: 予約（逆指値・指値）の注文はやめ、参考の表示だけにする。毎朝のツールと同じ条件・値段で予約の約定をバックテストに入れると、どの形も年率が下がった（後知恵なし 35.7%→30.7〜34.2%、87銘柄 45.6%→34.2〜42.6%。`バックテスト結果/点検_2026-10-25/`）。引けで条件がそろえば、翌朝の節6に買いの候補（A）として出る。各ルールでRSの高い順に2件まで。

| 参考の銘柄 | グループ | 種類 | 終値 | 前日比 | RS | 当てはまった条件 | 条件がそろう目安の価格（注文はしない） |
|---|---|---|---|---|---|---|---|
| ADI | 半導体 | ミネルヴィニ（ピボットの手前） | 425.35 | +4.3% | 92 | ピボット（ベースの高値、2026-06-22）444.56まで4.5%、ベース89日・調整幅22% | 444.56（この値を上回って引け、ほかの条件もそろうと翌朝の買いの候補（A）。目安） |
| JCI | データセンターの電力・冷却・部品・受託製造・建設 | ミネルヴィニ（ピボットの手前） | 155.88 | +5.7% | 84 | ピボット（ベースの高値、2026-10-06）160.41まで2.9%、ベース15日・調整幅12% | 160.41（この値を上回って引け、ほかの条件もそろうと翌朝の買いの候補（A）。目安） |
| PWR | データセンターの電力・冷却・部品・受託製造・建設 | ボリンジャー メソッドIII（%bが0.05未満に近い） | 578.83 | +2.6% | 65 | %b=0.198（0.05まであと少し）、21日II%=+0.066（>0） | 547.53（この値より下で引けると翌朝の買いの候補（A）。目安） |
| GLW | 光・通信・ネットワーク | ボリンジャー メソッドIII（%bが0.05未満に近い） | 126.30 | -1.1% | 63 | %b=0.187（0.05まであと少し）、21日II%=+0.064（>0） | 118.35（この値より下で引けると翌朝の買いの候補（A）。目安） |


# ニュース（サブエージェントの調査）

# ニュース調査（2026-10-27の米国引け時点。調査日 2026-10-28）

注: 出典は headlines.md の見出し（媒体・日付）を優先。WebSearchは2026-10-27付の記事がほぼ出ず、確認できなかった項目は「見つからなかった」と書く。

## テーマ全体の上げのきっかけ（4節で3銘柄以上が+5%以上、SOX 4%高）
- 市場全体: 「AI株に勢い、SOX4%高」（10/27 日本経済新聞）、「続伸、AI関連のハイテク株高がけん引」（10/27 Reuters）、「Nasdaq +1.2%、Anthropic rallyが2日目」（10/27 Eurasia Business News）、「Wall Street ends higher on revived AI momentum」（10/27 Reuters）。
- 信用: 「AI debt fears ease ahead of Oracle, Alphabet and Amazon updates」（10/27 CNBC）、「AI Debt Fears Ease After Meta Stock Offering」（10/28 JournalArta）。一方「Oracle Bonds Are Sliding as AI Debt Worries Grow」（10/27 24/7 Wall St.）、「AI Debt Deluge Gives Credit Market Indigestion」（10/28 Bloomberg）。
- ネオクラウド: 「Nebius rises 11% along with other neocloud stocks」（10/27 Seeking Alpha）、「CoreWeave adds Denmark capacity: CoreWeave and Nebius climb 4%」（10/27 24/7 Wall St.）。
- 呼び名: 「〇〇ショック」でAI関連の下げを指す報道は見つからなかった（10/27 日経は「AI株安で信用評価損益率が1年半ぶり低水準」）。
- 今夜の予定: FOMC結果（10/28）、Microsoft・Google決算（10/28 IBD、ChartMill「Super Wednesday」）。

## 引け後・時間外の材料
- SK Hynixの3Q決算が予想超、100兆ウォン還元へ。米時間外でSK Hynix 8%超高、SanDisk 5%高、Micron 4%超高、Seagate 3%超安（10/28 Moomoo。IBDは「Memory Giant Crushes Views」）。
- Seagate: FY27 1Q売上61%増・過去最高、生産能力は2028年まで確保済み（10/27 BigGo）。ただし時間外は3%超安（10/28 Moomoo）。CNBCの時間外の動き一覧にNXP・Seagate（10/27 CNBC）。
- F5: 4Q決算が予想を上回り時間外で上昇（10/27 Investing.com）。Alphabet: 決算前に時間外で1%超上昇、OpenAIのTPU計画に注目（10/27 TradingKey）。
- Visa決算、Robinhood（決算後に約9%安）、Whirlpool（7%安）、Enphase急落（10/27-28 CNBC/Moomoo/Yahoo）。テーマ外。

## SNDK（保有）
- 10/27は前日比+3.9%、出来高50日平均の0.72倍（data）。次回決算 2026-10-29（scan.md）。
- 時間外でSK Hynix決算を受け5%高（10/28 Moomoo）。
- 直近1週間の個別の悪材料となる報道は見つからなかった（WebSearchは2026年4月以前の記事のみ）。
- 悪材料: 確認できず

## AMD（保有）
- 10/27 前日比+5.5%。AIモメンタムの再燃（SOX 4%高）の中での上げ。AMD個別の材料は見つからなかった。
- 10/23時点でAMDは10/6の最高値649.42から約20%下げており、「チップ株の売りで、AMD固有の材料ではない」と説明（WebSearchで出た記事、媒体名未確認）。
- 次回決算 2026-11-03（scan.md。売上130億ドルのガイダンスとの記事あり）。
- 悪材料: 確認できず

## HUBB（候補A、前日比-5.5%、出来高3.6倍）
- scan.mdの次回決算日が2026-10-27で、当日が決算発表日。下げは決算への反応の可能性が高い。ただし2026年Q3の結果（売上・EPS・ガイダンス）を載せた記事は見つからなかった（検索は過去年の記事のみ）。
- 10/27 Barron's に "Stocks That Explain Today's Market" の記事があるが中身は未確認。
- 悪材料: 確認できず（決算内容は未確認）

## VLO（候補A、テーマ外、前日比-9.2%）
- 決算は10/22（scan.md）、Barchartの予告は10/23朝（Barchart）で日付が食い違い、直近の決算反応かは確認できなかった。
- 10/27の-9.2%の原因となるニュースは見つからなかった。セクター（Oil & Gas Refining & Marketing）は1週-7.5%（scan.md 3節）で、業種全体の下げ。
- 悪材料: 確認できず

## 急騰した銘柄（4節）
- FLEX +8.3%（出来高3.0倍）: 決算発表。「Flex delivers strong Q3 CY2026 numbers, stock soars」（10/28 FinancialContent）、「Why is Flex stock surging today?」（10/28 Investing.com India）。数値は未確認。
- DELL +7.5%・SMCI +7.3%・WDC +6.9%・STX +3.7%: AIサーバー・ストレージ群が1週+7.6%。10/27 Barchart「Dell and HPE Lost Billions in a Day Over 1 Big Worry. Dell Had Already Answered It.」（直前の下げの原因は中身未確認）。10/21にSuper Microの暫定売上が予想超でDell +7%（10/21 24/7 Wall St.）。
- NBIS +11.2%・CRWV +7.9%: ネオクラウド全体の上げ。「AI Cloud Financing Debate Continues」（10/27 GuruFocus）、CoreWeaveがデンマークの容量を追加（10/27 24/7 Wall St.）。
- ALAB +10.5%: 個別の原因は見つからなかった。決算は来週（10/27 Yahoo Finance）。
- CDNS +6.5%（出来高1.9倍）: 10/26引け後に決算予定との情報（The Right Trader）。結果の記事は見つからなかった。
- COHR +6.5%・LITE +5.9%・ANET +5.5%・ON +6.2%・MCHP +5.6%: 個別の原因は見つからなかった。SOX高に連動。
- JCI +5.7%（出来高1.8倍）・TEL +5.4%（2.1倍）: 原因となるニュースは見つからなかった。
- META -1.6%（出来高2.5倍）: 「AI Debt Fears Ease After Meta Stock Offering」（10/28 JournalArta）。Metaの株式の売り出しの報道。内容は未確認。
- FFIV -0.5%（出来高3.1倍）: 引け後の決算で上昇（10/27 Investing.com「F5株、時間外で上昇」）。

## 監視外の注目銘柄（4-2節、すべて1年の高値更新）
- CRL・RVTY・VTRS・WST・HAS: 10/27付の原因となるニュースは見つからなかった。CRL・RVTY・WSTはライフサイエンスのツール・受託、HASは玩具、VTRSは後発薬。（Health Information Services・Diagnostics & Researchが3カ月上位の業種。scan.md 3節）

## 候補（参考）
- ADI・JCI（ミネルヴィニ、ピボット手前）: 決算の評価（Beat/Miss、ガイダンス、予想の修正）は検索で確認できなかった。確認できず。
- 悪材料: 確認できず

# ニュースの見出し（プログラムが自動で取得）

- Googleニュース（日付を指定）とYahooファイナンスの見出しを `tools/news_headlines.py` が自動で並べたもの。日付は米国東部時間の配信日（引け後の記事は翌日付）。原因の判断・売買の判断はしていない。
- 調べた銘柄の選び方: 1週の騰落率（中央値）が−5%以下のグループごとに下げの大きい3銘柄＋1日で−7%以下の銘柄（最大12）と、+5%以上のグループごとに上げの大きい3銘柄＋1日で+7%以上の銘柄（最大6）。
- 1週で−5%以下のグループ: なし
- 1週で+5%以上のグループ: AIサーバー・ストレージ・メモリ・端末（+7.6%）

## 1. 市場全体（2026-10-27）

### 市場全体（英語のまとめ記事）
検索語: `stocks Wall Street close Nasdaq`
- 10/27 Reuters | Wall Street ends higher on revived AI momentum
- 10/27 Eurasia Business News | Stock Market Today: Nasdaq Rises 1.2% as Anthropic Rally Extends Into Second Day
- 10/27 24/7 Wall St. | Here Are Tuesday’s Top Wall Street Analyst Research Calls: Broadcom, Conoco Phillips, HubSpot, MercadoLibre, Moderna, Occidental Petroleum, PNC Financial, Trimble, and More
- 10/27 Yahoo Finance | Wall St rises as AI momentum holds heading into key earnings, Fed decision
- 10/28 Benzinga | Stock Market Today: S&P 500, Dow Jones Futures Trade Mixed Ahead of Federal Reserve Interest Rate Decisio

### 市場全体（Stock Market Today）
検索語: `"stock market today"`
- 10/27 Bloomberg.com | US Stocks Drift as Caution Sets In Ahead of Fed: Markets Wrap
- 10/28 ChartMill | Stock Market Today: AI Trade Rebounds as Wall Street Braces for a Fed-and-Big-Tech Super Wednesday
- 10/28 Investor's Business Daily | Futures Mixed, Memory Giant Crushes Views; Microsoft, Google Due
- 10/28 Yahoo Finance | Stock Market: Will S&P 500 Open Up or Down Today?
- 10/28 Yahoo Finance | UK Stock Market Today: FTSE 100 Futures Climb On Retail Resilience And Inflation Test

### 市場全体（日本語のまとめ記事）
検索語: `米国株式市場 OR NY株`
- 10/27 日本経済新聞 | NY株ハイライト AI株に勢い、SOX4%高 上がる「好決算」のハードル
- 10/27 Reuters | 米国株式市場＝続伸、ＡＩ関連のハイテク株高がけん引
- 10/27 株探 | 27日の米国市場ダイジェスト：米国株式市場は続伸、AI関連や良好な経済指標がけん引
- 10/27 47NEWS | 【速報】NY株小幅続伸、15ドル高
- 10/28 Yahoo!ファイナンス | 今晩のＮＹ株の読み筋＝ＦＯＭＣ結果を見極め、様子見ムードか(ウエルスアドバイザー)

### 半導体・AI株（英語）
検索語: `chip stocks OR semiconductor stocks OR AI stocks`
- 10/27 MarketWatch | Retail traders buy the dip on chip stocks — but Robinhood gets burned by the crypto market
- 10/27 Investor's Business Daily | Two Chip Stocks Upgraded To Buy On AI Data-Center Business
- 10/28 Seeking Alpha | Semiconductor stocks in focus after SK Hynix results; Micron, Nvidia top Quant list (SMH:NASDAQ)
- 10/28 Moomoo | SK Hynix Drives Chip Stocks Higher Premarket -- WSJ

### 信用（社債・借金）
検索語: `AI debt OR bonds OR credit spreads OR CDS`
- 10/27 CNBC | AI debt fears ease ahead of Oracle, Alphabet and Amazon updates. Here's what to watch.
- 10/27 24/7 Wall St. | Oracle Bonds Are Sliding as AI Debt Worries Grow. At 62, She Discovers the "Safe" Side of Her 401(k) Can Lose Money Too
- 10/28 Bloomberg.com | AI Debt Deluge Gives Credit Market Indigestion
- 10/28 Oz Arab Media | AI Debt Tests Loom for Oracle and Hyperscalers
- 10/28 JournalArta | AI Debt Fears Ease After Meta Stock Offering, but Oracle, Alphabet and Amazon Updates Loom

### 「〇〇ショック」の呼び名（日本語）
検索語: `ショック 株`
- 10/27 日本経済新聞 | 信用評価損益率、AI株安で1年半ぶり低水準 トランプショック以来
- 10/27 みんかぶ FX/為替 | 【通貨別まとめと見通し】南アランド円：10月高値9.67円から株安ショックで9.42円へ急落、9.50円の戻り売り抵抗を意識した下値固めの局面へ
- 10/27 CAMPFIRE (キャンプファイヤー) | 千代田区「5年転売禁止」ショックと6社偏重相場の急所 by 【hinaの株プレミアム】 - 株ブロガー“hina”のプレミアムコンテンツ
- 10/27 BigGo ファイナンス | ムーディーズ、FRB会合直前に暗号資産暴落を短期的な主要ショックとして指摘
- 10/27 Moomoo | エネルギーショックのシナリオ変化、構造的な供給不足が資産価格決定を書き換えつつある

### 引け後・時間外の動き（英語）
検索語: `"after hours" OR "after the bell" OR "extended trading" stocks`
- 10/27 CNBC | Stocks making the biggest moves after hours: Visa, Robinhood, NXP, Seagate and more
- 10/27 ChartMill | After-Hours Market Movers for Oct. 27, 2026: Gainers and Losers
- 10/27 Investing.com | Earnings call transcript: Visa tops Q4 2026 estimates, shares slip after hours
- 10/28 Yahoo Finance | ENPH Stock Plunges Sharply After-Hours On Lower Residential Demand: Here's Why Retail Is Holding Tight
- 10/28 Benzinga | Braiin Shares Climb 56% After Hours as Force AI Launches - Braiin (NASDAQ:BRAI)

### 引け後・時間外の動き（日本語）
検索語: `時間外 決算 株`
- 10/27 TradingKey | 決算発表を前にアルファベット株が時間外取引で1%超上昇、OpenAIのTPU計画に注目集まる
- 10/27 Investing.com - FX | 株式市場 | ファイナンス | 金融ニュース | F5株、時間外取引で上昇――第4四半期決算が市場予想を上回る 執筆
- 10/27 BigGo ファイナンス | シーゲイト、2027年度第1四半期の売上高が61%急増し過去最高を更新、生産能力は2028年まで確保済み
- 10/27 Yahoo!ファイナンス | ワールプール、決算受け時間外で７％安＝米国株個別(株探ニュース)
- 10/28 Moomoo | 【米株プレマーケット】SKハイニックスが米株時間外で8％超上昇 3Q決算予想超、100兆ウォン還元へ サンディスクが5％高 マイクロンは4％超高 ロビンフッドが決算後に9％近く安 シーゲイト・テクノロジーは3％超安

## 3. 大きく上げた銘柄（2026-10-21〜2026-10-27 の見出し）

### DELL（Dell Technologies Inc.、AIサーバー・ストレージ・メモリ・端末、前日比 +7.5%、1週 +8.8%）

#### Googleニュース
検索語: `Dell stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 10/21 Yahoo Finance | Why Is Dell Technologies Stock Rising in Pre-Market Trading?
- 10/21 Barchart.com | Why Dell (DELL) stock is trading up today
- 10/21 24/7 Wall St. | Super Micro Surges 12% as Preliminary Revenue Tops Guidance Range; Dell Jumps 7%, Hewlett Packard Enterprise Climbs 5%
- 10/22 Benzinga | Dell Stock Drops in Tech Sell-Off: Profit-Taking Hits AI Server Giant

#### Yahooファイナンス
検索語: `DELL`
- 10/27 Barrons.com | Broadcom, Nvidia, Boeing, GM, UPS, JetBlue, and More Stocks That Explain Today’s Market
- 10/27 GlobeNewswire | Global Edge Infrastructure Market Report 2026: Size, Share, Trends and Forecast to 2030 | Capitalize on 5G, AI and IoT with Microsoft, AWS, Dell, NVIDIA and Cisco
- 10/27 GlobeNewswire | Global Green Information Technology (IT) for Insurers Market Report 2026 | Capitalize on 13.6% CAGR as Microsoft, AWS, Google, and Dell Scale Green Cloud Adoption

### HPE（Hewlett Packard Enterprise Company、AIサーバー・ストレージ・メモリ・端末、前日比 +3.6%、1週 +8.5%）

#### Googleニュース
検索語: `Hewlett Packard Enterprise stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 10/21 Yahoo Finance | Hewlett Packard Enterprise (HPE) stock is up, what you need to know
- 10/21 Yahoo Finance | How Much Downside Is Left In HPE Stock?
- 10/23 MarketBeat | Hewlett Packard Enterprise (NYSE:HPE) Stock Price Up 2.3% - Here's Why

#### Yahooファイナンス
検索語: `HPE`
- 10/27 Barchart | Dell and HPE Lost Billions in a Day Over 1 Big Worry. Dell Had Already Answered It.
- 10/27 Trefis | What Are Cisco Investors Betting On?
- 10/27 Zacks | Can SMCI's DCBBS and DLC Improve its Financial Outlook in 2026?

### NTAP（NetApp, Inc.、AIサーバー・ストレージ・メモリ・端末、前日比 +2.5%、1週 +8.4%）

#### Googleニュース
検索語: `NetApp stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 10/22 Forbes | NetApp
- 10/22 Investor's Business Daily | Tech Stocks Hit, Yields Plunge As AI Trade Fizzles: NetApp, Amgen, Nasdaq In Focus
- 10/26 Yahoo Finance | NetApp (NTAP) stock is up, what you need to know
- 10/27 Trefis | Would You Have Held NetApp Stock All The Way Up?

#### Yahooファイナンス
検索語: `NTAP`
- 10/27 Barchart | Earnings Preview: What to Expect From NetApp’s Report
- 10/27 Simply Wall St. | How AI Coverage At NetApp (NTAP) Has Changed Its Investment Story
- 10/27 Trefis | What Did NetApp Do That HP Did Not?

### NBIS（Nebius Group N.V.、AIプラットフォーム・クラウド、前日比 +11.2%、1週 -0.6%）

#### Googleニュース
検索語: `Nebius stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 10/21 24/7 Wall St. | AI Cloud Stocks Rise as Musk Calls Overcapacity Talk 'Ridiculous': Nebius and CoreWeave Gain 3%, Oracle Edges Higher
- 10/22 Yahoo Finance | Nebius Stock Alert: I’m Watching This 43% Crash as AI Bubble Fears Return
- 10/22 Yahoo Finance | Nebius Declines 6% Despite Fresh Citi Financing; CoreWeave Drops 5%, Cloudflare Edges Higher
- 10/27 Seeking Alpha | Nebius Group rises 11% along with other neocloud stocks (NBIS:NASDAQ)

#### Yahooファイナンス
検索語: `NBIS`
- 10/27 24/7 Wall St. | AI Cloud Stocks Rise as CoreWeave Adds Denmark Capacity: CoreWeave and Nebius Climb 4%, Oracle Ticks Up
- 10/27 GuruFocus.com | Nebius Stocks Rally 10.3% as AI Cloud Financing Debate Continues
- 10/27 Insider Monkey | Nebius Group (NBIS) vs. CRWV and ORCL: Can AI Infrastructure Demand Turn Nebius Into the Next Cloud Powerhouse?

### ALAB（Astera Labs, Inc.、半導体、前日比 +10.5%、1週 +0.7%）

#### Googleニュース
検索語: `Astera Labs stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 10/21 Yahoo Finance | Astera Labs, Inc. (ALAB) Outpaces Stock Market Gains: What You Should Know
- 10/22 TIKR.com | Astera Labs Gains Ahead of Q3 as Scorpio Switches Set Up a 40% Sequential Jump
- 10/24 MarketBeat | Atlatl Advisers LLC Purchases New Shares in Astera Labs, Inc. $ALAB
- 10/27 Yahoo Finance | Astera Labs, Inc. (ALAB) Earnings Expected to Grow: What to Know Ahead of Next Week's Release

#### Yahooファイナンス
検索語: `ALAB`
- 10/23 GuruFocus.com | ETFs Bought $31.1 Million of Astera Labs (ALAB) on Oct. 21
- 10/23 TIKR | Credo Soars 7% as Super Micro’s $4 Billion Forecast Hike Signals “Increased Demand for AI Platforms”
- 10/23 The Wall Street Journal | Here Are This Week’s Biggest Losers After the Tech Selloff

### FLEX（Flex Ltd.、データセンターの電力・冷却・部品・受託製造・建設、前日比 +8.3%、1週 -4.7%）

#### Googleニュース
検索語: `Flex stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 10/21 Yahoo Finance | BOK Financial (BOKF) Stock Jumps As Q3 Earnings Flex Margin Strength
- 10/21 The Motley Fool | Breakfast News: A $5.7 Billion Flex or Genius?
- 10/28 FinancialContent | Flex (NASDAQ:FLEX) delivers strong Q3 CY2026 numbers, stock soars
- 10/28 Investing.com India | Why is Flex stock surging today? By Investing.com

#### Yahooファイナンス
検索語: `FLEX`
- 10/22 Barchart | Flex Earnings Preview: What to Expect
- 10/23 Trefis | Is Celestica Stock Safer Or Riskier Than A Year Ago?
- 10/24 Simply Wall St. | What Flex Bulls Got Right
