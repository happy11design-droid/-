# テーマ監視 2026-11-04

> 運用メモ(自動): 今朝は matplotlib が壊れていて銘柄別データが取れず、入れ直して再実行した。コナーズ宛の4件は文字数のため、2節を市場全体の局面の1行に縮めた版で送った（空の応答が続いたため）。ワインスタインは1〜2節のみの短い版。


# 判定のまとめ（ルールの判定と著者の判定を分けて表示）

- **ルールの判定**: 採用した売買ルール（スクリプト）が数値で決めたもの。損切りは買値の15%下の逆指値（日中に届けばその場で売れる）。
- **著者の判定**: ノートブックの著者の回答。買いは注文を止める理由があるときだけ【様子見】、保有はルールより早く手じまう理由があるときだけ【売り】。根拠は下の「著者の回答（全文）」。
- 2つが食い違うときに、どちらに従うかはユーザーが決める。

- **テーマ全体の急落（S2・記録だけ）: あり（S2）**（SOXが直近60取引日の最高値から -22.3%）。S2の日の順張りの候補には「S2なら見送る形」と付ける（売買のルールは変えない。記録してから採用を決める。2026-10-14）

- **特殊な下げ（記録だけ）: あり（特殊な下げ）**（2026-10-16から）（SOXが直近60取引日の最高値から -22.3%、前の1年の大きな上げ・雇用の弱さ・物価の再加速のうち 3つ）。1995年〜では、この形の後にSOXの下げが長引くことが多かった（後知恵を含む）。売買のルールは変えない（2026-11-03）

## 保有銘柄

| 銘柄 | ルール | 損益 | 時間外 | ルールの判定 | ルールの判定の理由 | 著者の判定 |
|---|---|---|---|---|---|---|
| SNDK | ルール外（ユーザーの判断。この日はどのルールの合図もなし） | -24.3% | +0.3% | **売り** | 終値 1037.4 が損切り価格 1165.61 以下 | 【未判定】（） |
| AMD | ボリンジャーIII | -11.1% | +0.8% | 保有継続 | 損切り 467.47（終値から -4.4%） | 【保有継続】（ボリンジャー） |

## 候補の判定（並びは上の「買う順番」の表と同じ）

- 並びは上の「買う順番」の表と同じ（RSの高い順。勝率の高い順ではない）。注文の値段・株数・逆指値は上の表を見る。勝率・1回平均は、そのルールの過去の成績（後知恵なしの監視銘柄・2015年〜の全部の合図）。
- 空き枠: 3（同時保有4銘柄まで。保有2、うちルールの売り1）。著者が【様子見】の候補を見送るかはユーザーが決める。

| 順 | 銘柄 | ルール | 過去の勝率 | 過去の1回平均 | RS | 時間外 | ルールの判定 | 著者の判定 |
|---|---|---|---|---|---|---|---|---|
| 1 | NTAP（ネットアップ） | 逆張り: 急落の底（担当: コナーズ）（指値の3日目） | 65% | +2.1% | 96 | +0.0% | 買い（翌日の寄り付き） | 【買い】（コナーズ） |
| 2 | LITE（ルメンタム・ホールディングス） | 逆張り: 急落の底（担当: コナーズ） | 65% | +2.1% | 92 | +0.4% | 買い（翌日の寄り付き） | 【様子見】（コナーズ） |
| 3 | MRVL（マーベル・テクノロジー） | 逆張り: 急落の底（担当: コナーズ） | 65% | +2.1% | 89 | +0.1% | 買い（翌日の寄り付き） | 【様子見】（コナーズ） |
| 4（枠外） | FTNT（フォーティネット） | 逆張り: 急落の底（担当: コナーズ）（指値の3日目） | 65% | +2.1% | 82 | +0.2% | 買い（翌日の寄り付き） | 【買い】（コナーズ） |
| 5（枠外） | WDC（ウエスタン・デジタル） | 逆張り: ボリンジャー メソッドIII | 68% | +1.5% | 48 | +0.8% | 買い（翌日の寄り付き） | 【買い】（ボリンジャー） |

- 時間外: 前の取引日の引けから、引け後（米国東部時間16〜20時）の最後の値までの騰落率（Yahoo。±5%以上は太字）。寄り付きの値段は、表の注文の目安（前日の終値で計算）から大きくずれることがある。原因の見出しは「ニュースの見出し」の節。

# 著者の回答（全文）

## 0_テーマの局面_ワインスタイン

1. **テーマ全体の局面**: 【ステージ3】
30週移動平均線が上昇を停止して「横ばい」となり、指数が線の下に位置しているため、天井圏である第3ステージと判定する[1, 2]。

2. **グループごとの局面**:
- AIソフト・セキュリティ・ITサービス｜ステージ2｜30週線が上昇中かつ乖離プラス[3]
- AIプラットフォーム・クラウド｜ステージ3｜30週線が横ばい[1]
- AIサーバー・ストレージ・メモリ・端末｜ステージ3｜30週線が横ばい[1]
- 半導体｜ステージ3｜30週線が横ばい[1]
- データセンターの電力・冷却・部品・受託製造・建設｜ステージ3｜30週線が横ばい[1]
- 半導体製造装置・材料・設計ソフト・計測｜ステージ3｜30週線が横ばい[1]
- 光・通信・ネットワーク｜ステージ3｜30週線が横ばい[1]

3. **転換の兆し**:
30週線の横ばい移行[1]1. **テーマ全体の局面**: 【ステージ3】
30週移動平均線が上昇を停止して「横ばい」となり、指数が線の下に位置しているため、天井圏である第3ステージと判定する[1, 2]。

2. **グループごとの局面**:
- AIソフト・セキュリティ・ITサービス｜ステージ2｜30週線が上昇中かつ乖離プラス[3]
- AIプラットフォーム・クラウド｜ステージ3｜30週線が横ばい[1]
- AIサーバー・ストレージ・メモリ・端末｜ステージ3｜30週線が横ばい[1]
- 半導体｜ステージ3｜30週線が横ばい[1]
- データセンターの電力・冷却・部品・受託製造・建設｜ステージ3｜30週線が横ばい[1]
- 半導体製造装置・材料・設計ソフト・計測｜ステージ3｜30週線が横ばい[1]
- 光・通信・ネットワーク｜ステージ3｜30週線が横ばい[1]

3. **転換の兆し**:
30週線の横ばい移行[1, 2]およびS&P500に対する相対的強さ（RS）の悪化[4]が天井（ステージ3）の兆しである。なお、50日線・2倍ETF・ニュース件数・マクロ指標による警告はマニュアルに規定なし。

4. **テーマの外**:
なし（ヒートマップデータ省略のため判定不能）

（全体の版が空の応答だったため、1〜2節だけの短い版で送り直した回答。ヒートマップ・急騰急落・ニュースは渡していない）

## 1_コナーズ_prompt_1

## NTAP
1. **投資判断**: 【買い】
2. **止める理由の確認**:
   - 本が禁じる形・状況｜なし｜株価は200日線の上で急落した状態。高値更新や200日線下ではない [1, 2]。
   - 避けるべき時期（決算など）｜なし｜次回決算は27日後。本に決算期の見送り規定なし [3]。
   - 悪材料｜判定不能｜ニュース省略のため判定不能。なお本は悪材料による急落こそ買えと規定 [1, 4]。
3. **現状パターンと価格**:
   - `現状パターン: A（急落後買いシグナル成立）`
   - A: `本日の発注: 翌日の寄り付きで成行`
4. **注意点**: 指値3日目の最終日。終値が5日線を上回ったら注文取り消し。

## 1_コナーズ_prompt_2

## LITE
1. **投資判断**: 【様子見】
2. **止める理由の確認**:
   - 本が禁じる形・状況｜あり｜株価626.75が200日線806.01下で買い不可（第4章 [1, 2]）
   - 避けるべき時期（決算など）｜なし｜次回決算90日後（第11章 [3]）
   - 悪材料｜判定不能｜ニュース本文省略（第2章 [4]）
3. **現状パターンと価格**:
   - `現状パターン: A（条件成立）`
   - `本日の発注: なし（見送り）`
4. **注意点**: 200日線下の買いは本で厳禁（第4章 [2]）。

## 1_コナーズ_prompt_3

## MRVL
1. **投資判断**: 【様子見】
2. **止める理由の確認**:
   - 本が禁じる形・状況｜あり｜200日線184.51の下側（第4章）[1, 2]
   - 避けるべき時期（決算など）｜あり｜発注日11/4は月初3〜8日（第11章）[1, 3]
   - 悪材料｜なし｜悪材料規定なし。パニックは買い機会（第3, 5章）[4, 5]
3. **現状パターンと価格**:
   - 現状パターン: A（シグナル点灯だが見送り）
   - A: 本日の発注: 翌日の寄り付きで成行
4. **注意点**: 200日線復帰まで見送り。

## 1_コナーズ_prompt_4

## FTNT
1. **投資判断**: 【買い】
2. **止める理由の確認**:
   - 本が禁じる形・状況｜なし｜現在値129.39は200日線129.17の上にあり、急落後の買いルールに適合 [1, 2]。
   - 避けるべき時期（決算など）｜なし｜決算（10/28）は通過済み。本に事前回避規定もなし [3]。
   - 悪材料｜なし｜悪材料によるパニック急落こそ平均回帰の大きな買いエッジとなる [4, 5]。
3. **現状パターンと価格**:
   - 現状パターン: A（11/2に急落条件が成立）
   - 本日の発注: 翌日の寄り付きで成行
4. **注意点**: 終値が5日移動平均線（131.78）を上回った翌営業日の寄り付きで必ず手じまうこと [6]。

## 1_ボリンジャー_prompt_1

## AMD
1. **投資判断**: 【保有継続】（早期手じまい理由なし）
2. **止める理由の確認**:
   - 本が禁じる形・状況｜なし｜下部バンド未到達・M型等なし（第8,13,20章）
   - 避けるべき時期（決算など）｜なし｜次回決算2027/2/2・規定なし（第1〜22章）
   - 悪材料｜なし｜早期売却の悪材料規定なし（用語集）
3. **現状パターンと価格**:
   - 保有中: `売りの予約注文: 指値 630.92（現在値比 +29.1%）`
4. **注意点**: 損切り467.47と下部バンド461.21への接近に注意。

## 1_ボリンジャー_prompt_2

## WDC
1. **投資判断**: 【買い】
2. **止める理由の確認**:
   - 本が禁じる形・状況｜なし｜%b<0.05・21日II%>0でメソッドIIIの条件成立 [1, 2]（第20章）
   - 避けるべき時期（決算など）｜なし｜次回決算まで85日あり禁止規定なし [3, 4]（第4章）
   - 悪材料｜なし｜買いを見送るべき悪材料の規定なし [1]（第20章）
3. **現状パターンと価格**:
   - 現状パターン: A（最新足で条件成立）
   - 本日の発注: 翌日の寄り付きで成行
4. **注意点**: 特になし

# スキャン（数値と事実）


- 監視銘柄 87（判定できたのは 86、取得不可: Q）。
- この一覧は数値と事実だけ。売買の判断は著者のノートブックが行う。

## 1. テーマ（グループ）の強さ

| グループ | 銘柄数 | 1週 | 1カ月 | 3カ月 | 3カ月の順位 | 50日線より上の銘柄の割合 | グループ指数の30週線の局面（線との乖離、4週前からの線の傾き） |
|---|---|---|---|---|---|---|---|
| 半導体 | 16 | -5.8% | -14.4% | -7.1% | 4位 | 25% | 横ばい（-7.6%、+5.7%） |
| 半導体製造装置・材料・設計ソフト・計測 | 8 | -10.0% | -24.1% | -15.2% | 6位 | 25% | 横ばい（-15.1%、+2.2%） |
| AIサーバー・ストレージ・メモリ・端末 | 9 | -17.3% | -28.9% | -4.2% | 3位 | 11% | 横ばい（-4.4%、+8.0%） |
| 光・通信・ネットワーク | 9 | -9.8% | -29.7% | -24.3% | 7位 | 11% | 横ばい（-16.2%、+2.3%） |
| データセンターの電力・冷却・部品・受託製造・建設 | 19 | -4.8% | -13.8% | -13.1% | 5位 | 26% | 横ばい（-9.4%、+0.9%） |
| AIプラットフォーム・クラウド | 11 | -4.7% | -10.6% | -2.3% | 2位 | 36% | 横ばい（-7.0%、+1.7%） |
| AIソフト・セキュリティ・ITサービス | 14 | -6.2% | +0.9% | +11.3% | 1位 | 43% | 上昇（+11.9%、+5.2%） |

## 2. テーマ全体の状態と早めの警告

- 市場全体の30週線による局面: S&P500指数 **上昇**／NASDAQ100指数 **横ばい**（急落の底で買うルールは、過去の検証で下落相場で特に強く、横ばいの相場では負けていた）
- **2倍ETFを使う局面（案1、2026-10-13 採用）: S&P500の20週線（100日線）で 上昇** → 2倍ETFのある銘柄は2倍ETFで買う（SPY 766.81、100日線 758.61、20日前の線 753.36。上昇＝線より上かつ線が上向き）
- **テーマ全体の急落（S2、記録だけ。売買のルールは変えない）: あり（S2）**（SOX 10268.65、直近60取引日の最高値 13217.82 から -22.3%。S2＝最高値から−10%以上）。S2のときに「順張りの新しい買いだけ止める」形を記録で比べる（2026-10-14 ユーザー決定。バックテストでは年率は上がったが2つの期間ではどちらも少し下回ったため、記録してから採用を決める。`バックテスト結果/テーマ全体の急落を検知して手じまう・買いを止める.md`）
- **グループごとの悪いニュースの流れ（記録だけ。売買のルールは変えない。2026-10-22〜2026-11-04）**: 会社の名前と悪い言葉（格下げ・目標株価の引き下げ・見通しの引き下げ・予想未達・急落・信用・訴訟・輸出規制など）の両方がある見出しの数（Googleニュース、`tools/news_headlines.py`）。10取引日の1銘柄あたりが一番多いグループに印。2026年7〜11月の確かめでは、印のグループの合図は10月は成績が悪かった（1回平均 −10.6%、ほか −5.6%）が、7〜9月は逆に良かった（+11.6%、ほか +6.7%）（`バックテスト結果/実際の運用の期間の確認_2026-10-23/グループの悪いニュースの流れ.md`。2026-11-04）

| グループ | 直近5取引日 | その前の5取引日 | 10取引日の1銘柄あたり | 印 |
|---|---|---|---|---|
| AIサーバー・ストレージ・メモリ・端末（9） | 19件 | 4件 | 2.6 | **悪いニュースが続いている** |
| 半導体（16） | 26件 | 6件 | 2.0 |  |
| AIプラットフォーム・クラウド（11） | 13件 | 9件 | 2.0 |  |
| 光・通信・ネットワーク（9） | 9件 | 4件 | 1.4 |  |
| データセンターの電力・冷却・部品・受託製造・建設（19） | 8件 | 5件 | 0.7 |  |
| AIソフト・セキュリティ・ITサービス（14） | 6件 | 3件 | 0.6 |  |
| 半導体製造装置・材料・設計ソフト・計測（9） | 1件 | 1件 | 0.2 |  |

印のグループ（AIサーバー・ストレージ・メモリ・端末）の最近の見出し: 2026-11-03 Stock Market Today: Dow Futures Drop as Apple Sinks After Earnings; Chip Stocks Rebound as AMD Results Loom（Yahoo Finance）／2026-11-03 Apple (NASDAQ:AAPL) Stock Price Target Cut by JPMorgan Chase & Co.（MarketBeat）／2026-11-03 Apple (NASDAQ:AAPL) Stock Falls 1.9% Following Analyst Downgrade（MarketBeat）

- **特殊な下げ（記録だけ。売買のルールは変えない）: あり（特殊な下げ）**（2026-10-16から）。SOX は直近60取引日の最高値から -22.3%（−15%以下が条件）、●A 前の1年の上げ +107.2%（+80%以上）、●B 雇用の伸び 51千人/月（2026-09まで。10万人未満）、●C 物価 4.0%（2026-09。3か月前 3.7%。3.5%以上で再加速）＝3つ（2つ以上が条件）。1995年〜でSOXが−15%以下かつ条件2つ以上の日は、120日後にSOXが下だったのが69%・250日後が70%（中央値 −33%）、AI以外の8業種の平均は250日後 −7%。ただし条件は過去を見て選んだもの（条件が2つ以上の局面は約5回）で、2026年7〜9月にこの間テーマを買わないと、その後の戻りを逃して2026年の成績は下がった（`バックテスト結果/実際の運用の期間の確認_2026-10-23/特殊な下げと過去の似た下げ.md`。2026-11-03）
- テーマ指数（監視銘柄の等金額平均）の30週線による局面: **横ばい**（上昇＝線より上かつ上向き、下落＝線より下かつ下向き、それ以外＝横ばい。ワインスタインのステージの近似）
- テーマ指数と50日線: 50日線より下（乖離 -9.2%）
- S&P500に対する相対的な強さ: 50日平均より下（S&P500より弱い）
- 監視銘柄のうち50日線より上の割合: 27%
- 警告（割合が40%未満かつテーマ指数が50日線より下）: **出ている**
- 参考（バックテスト）: 30週線の「下落」は高値から10〜33%下げた後に出る遅い判定。50日線・割合・相対的な強さは高値から2〜8%で出るが、誤報が年15回以上ある。警告中に新しい買いを止めると、押し目買い（ボリンジャーIII）の成績は大きく下がった（`バックテスト結果/テーマ監視銘柄・直近3年.md` 11・12節）。

## 3. ヒートマップ（Finviz、全米の業種別の騰落率）

3カ月の騰落率の上位15業種（テーマの外で強くなっている業種の確認用）:

| 順位 | 業種 | 1週 | 1カ月 | 3カ月 | 6カ月 | 1年 |
|---|---|---|---|---|---|---|
| 1 | Health Information Services | +1.9% | +11.6% | +35.6% | +56.5% | +8.1% |
| 2 | Oil & Gas Refining & Marketing | -7.5% | -9.7% | +21.7% | +47.4% | +87.5% |
| 3 | Diagnostics & Research | -1.2% | +7.3% | +20.4% | +45.9% | +26.7% |
| 4 | Medical Instruments & Supplies | +6.8% | +14.3% | +16.0% | +17.3% | +7.1% |
| 5 | Financial Data & Stock Exchanges | +7.4% | +15.7% | +15.8% | +12.7% | +6.3% |
| 6 | Medical Care Facilities | +7.8% | +13.6% | +15.8% | +24.6% | +21.8% |
| 7 | Lodging | +7.9% | +16.3% | +15.7% | +15.7% | +46.6% |
| 8 | Auto Manufacturers | -2.1% | +2.8% | +14.9% | -1.7% | -14.6% |
| 9 | Medical Distribution | +9.4% | +13.6% | +14.9% | +40.0% | +23.8% |
| 10 | Drug Manufacturers - General | +6.9% | +15.2% | +14.4% | +26.9% | +41.2% |
| 11 | Discount Stores | +8.3% | +17.0% | +13.6% | +3.2% | +24.8% |
| 12 | Consumer Electronics | +1.7% | +4.8% | +11.8% | +21.6% | +26.9% |
| 13 | REIT - Hotel & Motel | +2.7% | +14.9% | +11.7% | +28.5% | +61.3% |
| 14 | Tobacco | +5.0% | +13.2% | +11.4% | +16.0% | +36.6% |
| 15 | Insurance - Reinsurance | +5.6% | +9.4% | +11.4% | +19.5% | +40.3% |

テーマの業種の順位（3カ月、全144業種中）: Semiconductors 121位、Semiconductor Equipment & Materials 142位、Computer Hardware 138位、Communication Equipment 130位、Electronic Components 136位、Software - Infrastructure 36位、Software - Application 35位、Internet Content & Information 126位

## 4. 急騰・急落した銘柄（前日比±5%以上、または出来高が50日平均の2倍以上）

原因のニュースをサブエージェントが調べ、候補・保有銘柄の判定材料として著者に渡す。急騰・急落そのものは売買の合図にしない（後知恵のないS&P500全体のバックテストでは、急騰の翌日に買うルールは年率7%、急落の翌日に買うルールは年率9〜10%で、採用した3つのルールより優れていなかった）。

| 銘柄 | グループ | 前日比 | 出来高（50日平均の倍） | 終値 | 50日線 | RS | 局面 |
|---|---|---|---|---|---|---|---|
| DDOG | AIソフト・セキュリティ・ITサービス | -14.4% | 3.9倍 | 188.72 | 下 | 67 | レンジ |
| VST | データセンターの電力・冷却・部品・受託製造・建設 | -13.8% | 3.5倍 | 120.29 | 下 | 4 | レンジ |
| NRG | データセンターの電力・冷却・部品・受託製造・建設 | -13.5% | 3.5倍 | 83.25 | 下 | 1 | レンジ |
| VRT | データセンターの電力・冷却・部品・受託製造・建設 | -12.9% | 2.2倍 | 205.55 | 下 | 9 | レンジ |
| CDW | AIソフト・セキュリティ・ITサービス | +12.7% | 2.2倍 | 168.75 | 上 | 87 | 上昇相場 |
| FLEX | データセンターの電力・冷却・部品・受託製造・建設 | -12.3% | 1.8倍 | 77.24 | 下 | 10 | レンジ |
| PWR | データセンターの電力・冷却・部品・受託製造・建設 | -11.7% | 3.1倍 | 580.44 | 下 | 29 | レンジ |
| APP | AIプラットフォーム・クラウド | +10.7% | 2.8倍 | 271.75 | 下 | 1 | レンジ |
| CRWV | AIプラットフォーム・クラウド | -9.9% | 1.5倍 | 48.42 | 下 | 0 | レンジ |
| ETN | データセンターの電力・冷却・部品・受託製造・建設 | -9.9% | 2.7倍 | 353.08 | 下 | 9 | レンジ |
| GEV | データセンターの電力・冷却・部品・受託製造・建設 | -9.3% | 2.5倍 | 832.83 | 下 | 27 | レンジ |
| CIEN | 光・通信・ネットワーク | -9.3% | 1.4倍 | 272.24 | 下 | 10 | レンジ |
| DELL | AIサーバー・ストレージ・メモリ・端末 | -8.8% | 1.3倍 | 372.36 | 下 | 99 | レンジ |
| STX | AIサーバー・ストレージ・メモリ・端末 | -8.1% | 1.5倍 | 557.06 | 下 | 53 | レンジ |
| SNDK | AIサーバー・ストレージ・メモリ・端末 | -7.9% | 1.2倍 | 1037.40 | 下 | 99 | レンジ |
| LITE | 光・通信・ネットワーク | -7.9% | 1.9倍 | 626.75 | 下 | 92 | レンジ |
| SHOP | AIソフト・セキュリティ・ITサービス | +7.3% | 1.4倍 | 153.03 | 上 | 67 | 上昇相場 |
| MRVL | 半導体 | -7.1% | 2.1倍 | 159.80 | 下 | 89 | レンジ |
| ADSK | AIソフト・セキュリティ・ITサービス | +7.0% | 1.8倍 | 270.09 | 上 | 47 | レンジ |
| MU | 半導体 | -7.0% | 1.4倍 | 795.23 | 下 | 98 | レンジ |
| TER | 半導体製造装置・材料・設計ソフト・計測 | -6.8% | 1.5倍 | 250.99 | 下 | 9 | レンジ |
| WDC | AIサーバー・ストレージ・メモリ・端末 | -6.8% | 0.9倍 | 323.83 | 下 | 48 | レンジ |
| CEG | データセンターの電力・冷却・部品・受託製造・建設 | -6.7% | 2.0倍 | 245.72 | 下 | 9 | レンジ |
| MSFT | AIプラットフォーム・クラウド | +6.7% | 2.3倍 | 555.80 | 上 | 78 | 上昇相場 |
| NBIS | AIプラットフォーム・クラウド | -6.7% | 1.3倍 | 141.52 | 下 | 35 | レンジ |
| KEYS | 半導体製造装置・材料・設計ソフト・計測 | -6.3% | 1.8倍 | 285.86 | 下 | 45 | レンジ |
| JCI | データセンターの電力・冷却・部品・受託製造・建設 | -6.3% | 2.5倍 | 140.53 | 下 | 39 | レンジ |
| APH | データセンターの電力・冷却・部品・受託製造・建設 | -6.2% | 1.6倍 | 79.01 | 下 | 47 | レンジ |
| AMZN | AIプラットフォーム・クラウド | +6.1% | 2.5倍 | 266.03 | 上 | 36 | レンジ |
| COHR | 光・通信・ネットワーク | -6.0% | 1.7倍 | 195.09 | 下 | 6 | レンジ |
| RDDT | AIソフト・セキュリティ・ITサービス | +6.0% | 1.5倍 | 101.89 | 下 | 1 | レンジ |
| HPQ | AIサーバー・ストレージ・メモリ・端末 | +5.9% | 1.2倍 | 29.93 | 下 | 87 | レンジ |
| GLW | 光・通信・ネットワーク | -5.8% | 1.6倍 | 118.77 | 下 | 16 | レンジ |
| SMCI | AIサーバー・ストレージ・メモリ・端末 | -5.7% | 2.4倍 | 29.60 | 下 | 10 | レンジ |
| HPE | AIサーバー・ストレージ・メモリ・端末 | -5.7% | 1.0倍 | 50.09 | 下 | 98 | レンジ |
| QCOM | 半導体 | +5.3% | 1.7倍 | 173.19 | 下 | 43 | レンジ |
| AAPL | AIサーバー・ストレージ・メモリ・端末 | +5.3% | 2.1倍 | 349.51 | 上 | 79 | レンジ |
| ARM | 半導体 | -5.3% | 1.7倍 | 191.80 | 下 | 36 | レンジ |
| MPWR | 半導体 | -5.1% | 1.6倍 | 1261.08 | 下 | 28 | レンジ |
| ANET | 光・通信・ネットワーク | +5.0% | 3.4倍 | 178.48 | 下 | 58 | レンジ |
| ALAB | 半導体 | -4.4% | 2.1倍 | 223.27 | 下 | 35 | レンジ |
| EQIX | データセンターの電力・冷却・部品・受託製造・建設 | +3.9% | 2.2倍 | 1054.09 | 上 | 59 | レンジ |
| DLR | データセンターの電力・冷却・部品・受託製造・建設 | +2.6% | 2.7倍 | 184.88 | 上 | 36 | レンジ |
| ORCL | AIプラットフォーム・クラウド | -1.9% | 3.3倍 | 123.73 | 下 | 2 | レンジ |
| AMD | 半導体 | +1.0% | 2.4倍 | 488.78 | 下 | 96 | レンジ |

- 局面: 終値 > 50日線 > 200日線、50日線が20取引日前より2%以上高い、ADX(14) ≧ 20 をすべて満たせば上昇相場、それ以外はレンジ（判定式はClaudeが置いたもの）。

## 4-2. 監視外の注目銘柄（S&P500・NASDAQ100のうち監視銘柄に入っていない銘柄）

条件: 流動性（株価5ドル以上・50日平均出来高25万株以上）があり、(a) 前日比+8%以上かつ出来高が50日平均の2倍以上、または (b) 終値が直前1年の最高値（終値）を上回り、RS≧90。RSの高い順に5銘柄（ニュースを調べる）。監視銘柄に入れるかはユーザーが決める。

| 銘柄 | 種類 | 前日比 | 出来高（50日平均の倍） | RS | 終値 |
|---|---|---|---|---|---|
| MRNA | 1年の高値更新 | +13.1% | 0.8倍 | 99 | 258.38 |
| CNC | 急騰・1年の高値更新 | +12.6% | 3.2倍 | 97 | 76.01 |
| BBY | 1年の高値更新 | +8.0% | 1.1倍 | 96 | 101.36 |
| SWK | 急騰・1年の高値更新 | +13.1% | 4.0倍 | 95 | 118.33 |
| HAS | 1年の高値更新 | +3.1% | 0.8倍 | 95 | 121.58 |

- ほかに24銘柄: VTRS（1年の高値更新、RS 94）、BIIB（1年の高値更新、RS 94）、AMGN（1年の高値更新、RS 94）、LLY（1年の高値更新、RS 93）、HST（1年の高値更新、RS 93）、BDX（1年の高値更新、RS 93）、GILD（1年の高値更新、RS 92）、MCK（1年の高値更新、RS 91）、MAR（1年の高値更新、RS 91）、DLTR（1年の高値更新、RS 91）、TRV（1年の高値更新、RS 90）、EBAY（1年の高値更新、RS 90）、EXPE（急騰、RS 83）、XYZ（急騰、RS 83）、ZBH（急騰、RS 77）

## 5. 保有銘柄の手じまい条件（`新分析ツール/保有銘柄.md`）

| 銘柄 | ルール | 買った日 | 買値 | 終値 | 損益 | 損切り価格（買値の15%下、逆指値） | ルールの手じまい条件 | 出来高2倍の大陰線（買った後の直近5日） | 次回決算予定日 |
|---|---|---|---|---|---|---|---|---|---|
| SNDK | ルール外（ユーザーの判断。この日はどのルールの合図もなし） | 2026-10-21 | 1371.30 | 1037.40 | -24.3% | 1165.61 | **損切り価格を下回った** ルールが不明（保有銘柄.md の「ルール」を確認） | なし | 2026-10-29 |
| AMD | ボリンジャーIII | 2026-10-21 | 549.97 | 488.78 | -11.1% | 467.47 | 売りの指値: 上部バンド 630.92（今夜この値に置き直す。届いた日に売れる）（2倍ETF AMUU で持っている場合も、判定は元の株 AMD の値段） | なし | 2027-02-02 |

- 出来高2倍の大陰線: 実体（始値−終値）が前日までのATR(14)の1.5倍以上、終値がその日の値幅の下25%以内、出来高が前日までの50日平均の2倍以上の日。**押し目（ボリンジャーIII）・急落の底の保有では売りのルール**: 出たら翌日の寄り付きで全部売り、空いた枠で次の合図を買う（2026-10-02 ユーザー決定。`バックテスト結果/やり直し_売りの合図の組み合わせ.md`。乱数3組とも年率が約+2ポイント、最大下落率もやや下がった）。ミネルヴィニ・新高値V2の保有では事実の表示（順張りに足しても良くならなかった）。

- 半分売りの合図（ミネルヴィニ・新高値V2の保有だけ）: 反転のローソク足（かぶせ線・弱気の包み足・宵の明星・流れ星）＋出来高が50日平均の1.5倍以上＋RSI(14)が前日か当日に70以上。買った後に最初に出た日の翌日の寄り付きで半分売り、残り半分は50日線割れ・損切り15%まで持つ（2026-10-01 ユーザー決定。`バックテスト結果/半分だけ売るとオニールの空き枠.md`）。

- かぶせ線（ミネルヴィニ・新高値V2の保有だけ）: 上昇中の陽線の翌日に、前日の高値より上で寄り付き、前日の陽線の真ん中より下（前日の始値より上）で引けた日。翌日の寄り付きで全部売り、空いた枠で次の合図を買う。半分売りより優先する（2026-10-01 ユーザー決定。`バックテスト結果/2倍ETFで売って買い直す.md`。順張りの売買の25%で出て、1回平均+2.0%、年率 21.4%→26.4%）。

## 5-2. 前日（2026-11-03の引け）の【買い（予約）】の確認

前日の【買い（予約）】はなし。

## 6. 候補（採用したルールの条件が成立＝A。予約（B）は2026-10-25から注文せず、節6-3に参考の表示だけ）

建玉の目安: 同時保有4銘柄まで、1銘柄に資金の25%（資金÷4）、損切りは買値の15%下（ユーザー決定 2026-09-29）。

保有中のため候補から外した銘柄（合図は出ている）: AMD

**急落の底の指値に届いた銘柄（注文していれば約定。保有銘柄.md に買った日・値段を記録する。今日の候補には出さない）**: MU（2026-11-02の合図、指値 816.92、2026-11-04の安値 791.03）、INTC（2026-11-03の合図、指値 59.34、2026-11-04の安値 56.77。寄り付き 58.67 が指値より下だったので寄り付きで約定）、ARM（2026-11-02の合図、指値 192.85、2026-11-04の安値 189.89）、MRVL（2026-11-03の合図、指値 168.53、2026-11-04の安値 154.78。寄り付き 165.26 が指値より下だったので寄り付きで約定）、ALAB（2026-11-02の合図、指値 225.08、2026-11-04の安値 208.43。寄り付き 217.97 が指値より下だったので寄り付きで約定）、TER（2026-11-02の合図、指値 255.79、2026-11-04の安値 245.94）、DELL（2026-11-02の合図、指値 384.92、2026-11-04の安値 366.63。寄り付き 384.69 が指値より下だったので寄り付きで約定）、STX（2026-11-02の合図、指値 581.88、2026-11-04の安値 555.80。寄り付き 569.59 が指値より下だったので寄り付きで約定）、HPE（2026-11-02の合図、指値 50.17、2026-11-04の安値 49.16）、HPQ（2026-11-02の合図、指値 27.86、2026-11-03の安値 27.81）、LITE（2026-11-03の合図、指値 666.56、2026-11-04の安値 598.70。寄り付き 640.94 が指値より下だったので寄り付きで約定）、NOW（2026-11-02の合図、指値 103.89、2026-11-03の安値 103.72）、DDOG（2026-11-02の合図、指値 211.78、2026-11-03の安値 211.65）

パターン: A＝最新の足で採用ルールの条件が成立（翌日の寄り付きで成行）。条件の成立が目前の銘柄（B）は、予約の注文をやめたので節6-3に参考として出す（2026-10-25 ユーザー決定）。

| 銘柄 | グループ | パターン | 種類 | ルールの過去の成績 | 終値 | 前日比 | RS | 50日線の傾き | 局面 | 当てはまった条件 | 次回決算予定日 | 注文の目安 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| NTAP | AIサーバー・ストレージ・メモリ・端末 | A | 逆張り: 急落の底（担当: コナーズ）（指値の3日目） | 2位（勝率65%・1回平均+2.1%） | 187.67 | -1.6% | 96 | +4.8% | レンジ | 2026-11-02の合図: 直前5日の最高値（終値）から-18.6%下落（−15%以上）、RSI(2)=2.4（≦10）、急落の前は50日線＞200日線。市場全体の局面: S&P500 上昇／NASDAQ100 横ばい。その後まだ指値に届かず、終値は5日線以下 | 2026-12-01（27日後） | 指値買い 181.55（合図の日 2026-11-02 の終値 185.26 の2%下。今日が最後の日。届かなければ見送り、途中で終値が5日線を上回ったら取り消す）。損切り: 約定した値段の15%下。手じまい: 終値が5日線（今日 196.26）を上回った翌日の寄り付き（コナーズ）。**株数の目安: 13株**（2,384ドル÷181.55。注文の価格）、購入金額 約2,360ドル |
| LITE | 光・通信・ネットワーク | A | 逆張り: 急落の底（担当: コナーズ） | 2位（勝率65%・1回平均+2.1%） | 626.75 | -7.9% | 92 | +0.9% | レンジ | 直前5日の最高値（終値）から-31.8%下落（−15%以上）、RSI(2)=2.9（≦10）、急落の前は50日線＞200日線。市場全体の局面: S&P500 上昇／NASDAQ100 横ばい | 2027-02-02（90日後） | 指値買い 614.22（合図の日 2026-11-04 の終値 626.75 の2%下。今日から3取引日。届かなければ見送り、途中で終値が5日線を上回ったら取り消す）。損切り: 約定した値段の15%下。手じまい: 終値が5日線（今日 750.31）を上回った翌日の寄り付き（コナーズ）。**2倍ETFで買う: LITX**（目減り 年14%。株と同じ金額。合図・損切り・手じまいは元の株 LITE の値段で判定）。**株数の目安: LITX 205株**（2,384ドル÷11.61）。**LITXの注文: 指値買い 11.61、購入金額 約2,379ドル**（注文の価格をETFの値段に直した近似。損切りは約定したETFの値段の約30%下） |
| MRVL | 半導体 | A | 逆張り: 急落の底（担当: コナーズ） | 2位（勝率65%・1回平均+2.1%） | 159.80 | -7.1% | 89 | +2.6% | レンジ | 直前5日の最高値（終値）から-36.5%下落（−15%以上）、RSI(2)=3.1（≦10）、急落の前は50日線＞200日線。市場全体の局面: S&P500 上昇／NASDAQ100 横ばい | 2026-12-01（27日後） | 指値買い 156.60（合図の日 2026-11-04 の終値 159.80 の2%下。今日から3取引日。届かなければ見送り、途中で終値が5日線を上回ったら取り消す）。損切り: 約定した値段の15%下。手じまい: 終値が5日線（今日 183.58）を上回った翌日の寄り付き（コナーズ）。**2倍ETFで買う: MRVU**（目減り 年11%。株と同じ金額。合図・損切り・手じまいは元の株 MRVL の値段で判定）。**株数の目安: MRVU 51株**（2,384ドル÷46.20）。**MRVUの注文: 指値買い 46.20、購入金額 約2,356ドル**（注文の価格をETFの値段に直した近似。損切りは約定したETFの値段の約30%下） |
| FTNT | AIソフト・セキュリティ・ITサービス | A | 逆張り: 急落の底（担当: コナーズ）（指値の3日目） | 2位（勝率65%・1回平均+2.1%） | 129.39 | +1.0% | 82 | +2.4% | レンジ | 2026-11-02の合図: 直前5日の最高値（終値）から-31.8%下落（−15%以上）、RSI(2)=1.5（≦10）、急落の前は50日線＞200日線。市場全体の局面: S&P500 上昇／NASDAQ100 横ばい。その後まだ指値に届かず、終値は5日線以下 | 2026-10-28（-7日後） | 指値買い 123.69（合図の日 2026-11-02 の終値 126.21 の2%下。今日が最後の日。届かなければ見送り、途中で終値が5日線を上回ったら取り消す）。損切り: 約定した値段の15%下。手じまい: 終値が5日線（今日 131.78）を上回った翌日の寄り付き（コナーズ）。**株数の目安: 19株**（2,384ドル÷123.69。注文の価格）、購入金額 約2,350ドル |
| WDC | AIサーバー・ストレージ・メモリ・端末 | A | 逆張り: ボリンジャー メソッドIII | 3位（勝率68%・1回平均+1.5%） | 323.83 | -6.8% | 48 | -10.2% | レンジ | %b=0.025（<0.05）、21日II%=+0.032（>0） | 2027-01-28（85日後） | 翌日の寄り付きで買い。損切り: 買値の15%下。手じまい: 買った日の夜から、売りの指値をその日の上部バンド（今日 409.23）に置き、毎晩その日の値に置き直す。**2倍ETFで買う: WDCX**（目減り 年11%。株と同じ金額。合図・損切り・手じまいは元の株 WDC の値段で判定）。**株数の目安: WDCX 294株**（2,384ドル÷8.10）。**WDCXの注文: 翌日の寄り付きで成行（今日の終値 8.10）、購入金額 約2,381ドル**（ETFの今日の終値で計算。寄り付きの値段で変わる。損切りは約定したETFの値段の約30%下） |

- 2倍ETF: 2倍ETFがある銘柄（ユーザーがムームー証券で買えることを確認した38銘柄のうち、目減りが年15%未満のもの）は、株の代わりに2倍ETFを買う（2026-10-04 ユーザー決定。`バックテスト結果/2倍ETFを使う決まり.md`。年率 約27%→約33%、確定した損益だけの最大下落率 約30%→約31%、含み損込みは約33%→約45%）。買う金額は株と同じ（資金の25%）。合図・損切り（元の株の買値の15%下＝ETFでは約30%下）・手じまいはすべて元の株の値段で判定する。指値・逆指値はETFの値段に直して置く。どのETFかは `新分析ツール/2倍ETFの対応表.json`（売買代金が1日500万ドル以上で、直近1年の目減りが一番小さいもの）。**2倍ETFで買うのは、S&P500が20週線（100日線）で「上昇」の局面のときだけ。横ばい・下落の局面では元の株で買う**（案1、2026-10-13 ユーザー採用。買う日に決め、買った後は局面が変わってもそのまま持つ。`バックテスト結果/流れ（市場の局面）を使う形.md`）。

- ルールの過去の成績: 今の売りのルールで、後知恵なしの監視銘柄・2015年〜の全部の合図の1回ごとの成績（2026-10-02計算、`新分析ツール/バックテスト結果/ルールごとの成績.md`）。順位は1回平均（1回の売買で平均いくら増えるか）の順。表はパターン（A→B）ごとに、この順位の良い順に並べた（表示の順番だけ。買う順番・件数の上限は変えていない。候補の選び方を変えても成績は変わらなかったため。2026-10-02 ユーザーの指示）。著者には渡さない。

- 同じ業種は同時に2銘柄まで（ユーザー決定 2026-09-28）のため見送った候補（保有中の銘柄と、買う順番で先に残した候補で数える）: MSFT（A・順張り: ミネルヴィニ。Software - Infrastructure: NTAP・FTNT）、PLTR（A・逆張り: ボリンジャー メソッドIII。Software - Infrastructure: NTAP・FTNT）

- パターンBは各ルールでRSの高い順に2件まで、急落の底・新高値のAは4件（同時保有の上限）までとし、5件を省いた。

- 悪いニュースが続いているグループ（AIサーバー・ストレージ・メモリ・端末）の候補（記録だけ。売買のルールは変えない。著者には渡さない）: NTAP、WDC

- 候補の数: 空き枠3（同時保有4銘柄まで。保有2、うち今日ルールの売りが成立1）＋予備2件まで表に出した（2026-10-25 ユーザー決定）。ほかの2件は枠に入らないので、著者の判定とニュース調査に回さない: JCI（A・ボリンジャー メソッドIII、RS 39）、MPC（A・ボリンジャー メソッドIII、RS 98）

- テーマの外の候補（グループが「テーマの外」）: 監視銘柄の候補で枠が埋まらないときに使う（監視銘柄の候補を先に買う）。S&P500の今の構成銘柄のうち監視銘柄でない銘柄から、RS≧90・30週線が上向きで終値がその上・業種の3カ月の強さが上位20%の20銘柄を調べ、空き枠2つ分まで出した。バックテストでは、テーマの外の強い銘柄で空き枠を埋めると、テーマが弱い時期の成績が支えられた（`バックテスト結果/半導体・AIに特化した場合.md`。2026-10-01 ユーザー決定）。

- RS≧80の押し目（ボリンジャーIII）は、バックテストで成績がより安定していた（PF3.27、最大下落20%）。

## 6-3. 参考: 条件の成立が目前の銘柄（予約は注文しない・著者には送らない）

2026-10-25 ユーザー決定: 予約（逆指値・指値）の注文はやめ、参考の表示だけにする。毎朝のツールと同じ条件・値段で予約の約定をバックテストに入れると、どの形も年率が下がった（後知恵なし 35.7%→30.7〜34.2%、87銘柄 45.6%→34.2〜42.6%。`バックテスト結果/点検_2026-10-25/`）。引けで条件がそろえば、翌朝の節6に買いの候補（A）として出る。各ルールでRSの高い順に2件まで。

| 参考の銘柄 | グループ | 種類 | 終値 | 前日比 | RS | 当てはまった条件 | 条件がそろう目安の価格（注文はしない） |
|---|---|---|---|---|---|---|---|
| SHOP | AIソフト・セキュリティ・ITサービス | ボリンジャー メソッドIII（%bが0.05未満に近い） | 153.03 | +7.3% | 67 | %b=0.093（0.05まであと少し）、21日II%=+0.045（>0） | 151.51（この値より下で引けると翌朝の買いの候補（A）。目安） |
| CRM | AIソフト・セキュリティ・ITサービス | ボリンジャー メソッドIII（%bが0.05未満に近い） | 227.11 | +2.2% | 65 | %b=0.192（0.05まであと少し）、21日II%=+0.097（>0） | 222.44（この値より下で引けると翌朝の買いの候補（A）。目安） |


# ニュース（サブエージェントの調査）

# ニュース調査（2026-11-05 JST、2026-11-04 米国引け時点）
確認方法: headlines.md の見出しを先に読み、見出しで分からない点だけ検索した（検索語は各節に記載）。

## テーマ全体の下げの原因
- 当日の市場全体は上げた。S&P500・ダウは大幅高（ダウ +1,569ドル）。米中間選挙で民主党が議会の主導権を奪い、政治の不確実性が後退した（Reuters・NBC News・NYT 11/4、京都新聞 11/4）。
- 一方でデータセンター関連は下げた。Reuters 11/4「Wall Street ends higher after Democrats win Congress; data center stocks tumble」、同日の日本語版「データセンターは安い」。MarketWatch 11/4「Micron and other chip stocks slip as election results strike at the core of data-center optimism」、IBD 11/4「Chip Stocks Feeling Blue After Democratic Party Victories」、Quartz 11/4「…clouds the outlook for data centers」。きっかけは選挙結果によるデータセンター規制・電力料金への懸念とみられる（見出しの表現。中身の詳細は未確認）。
- 広がった先: 電力・冷却・建設（VST −13.8%、NRG −13.5%、VRT −12.9%、PWR −11.7%、ETN −9.9%、GEV −9.3%）、メモリ・ストレージ（SNDK −7.9%、MU −7.0%、STX −8.1%）。24/7 Wall St. 11/4 は「Super Micro Falls 4% Despite Blowout Quarter as Margin Worries and Data Center Backlash Weigh; Dell Sinks 8%, HPE Drops 6%」、別記事で「SanDisk Retreats 9%, Micron and Western Digital Fall 7% as Election and Memory Price Worries Weigh」。
- 先行した流れ: 10/28 のマーベルによるルメンタム買収報道・ServiceNow/Fortinet決算、10/29 のIntelのPC市況警告（Yahoo Finance 10/29、24/7 Wall St. 10/30）、10/30 のハイパースケーラー投資への懸念で光関連が急落（24/7 Wall St. 10/30）。1週のグループ下落はこの連続の結果。
- 市場全体: S&P500は上昇。VIX・ハイイールド債の数値は見出し・検索では取得できなかった。
- 検索した語句: 「Vistra NRG Vertiv Quanta stocks plunge Democrats data center」「CoreWeave stock falls bonds debt」。検索は選挙とデータセンターの関係を確認できなかった（見出し以外の裏付けなし）。

## 5項目の確認
1. 大きく下げた3銘柄: VST・NRG（電力、選挙後のデータセンター懸念と見出しにあるが銘柄固有の記事は見出しになし）、DDOG −14.4%（原因の見出しなし。検索「Datadog stock plunge earnings November 4 2026」でも当日の記事は見つからなかった）。
2. 信用（借金）: headlines.md の信用の検索は取得できず。CRWV −9.9%（終値48.42）の当日の社債・格付けの記事は見つからなかった。CoreWeaveの債務懸念は10/14〜16に報じられている（検索で確認、当日分ではない）。当日の信用の材料は確認できず。
3. 同日に別の業界: ソフト（DDOG −14.4%）は下げ、CDW +12.7%、ADSK +7.0%、SHOP +7.3%、MSFT +6.7%（IBD 11/4「Microsoft Leaps Nearly 7%」）、AMZN +6.1%、APP +10.7%は上げ。データセンター関連だけが売られ、市場全体は上げた。
4. 経済指標・大手決算: 当日は選挙結果が主材料。AMD決算（11/3引け後、CNBC 11/3「データセンター売上がほぼ倍増、CEOはさらなる加速を予想」）でチップ株が反発（ChartMill 11/4）。Apple決算後の下げと目標株価引き下げ（Yahoo 11/3、MarketWatch 11/3）。
5. 呼び名: 「blue tsunami」（NBC News 11/4、政治の不確実性の解消の文脈）。株の下げに付いた「〇〇ショック」の呼び名は見つからなかった（headlines.md 日本語検索は取得不可）。

## 引け後・時間外の材料
- APP: 時間外 +21.8%。第3四半期の決算（売上 21.8億ドル、前年比+55%、純利益 14.4億ドル。会社発表 8-K 11/4）。IBD 11/4「AppLovin Stock Surges As Earnings Beat」。ガイダンスの数字は未確認。
- QCOM: 時間外 −8.5%。決算とガイダンス。CNBC 11/4「弱い業績予想、メモリ不足でスマホ販売が重い」、Barron's 11/4「供給コストが利益見通しを圧迫」。
- COHR: 時間外 +8.3%。会計第1四半期の決算（AP 11/4）。内容の数字は見出しになく未確認。
- ARM: 時間外 約−5%。決算は予想超えだが見通しが予想を少し上回る程度（investingLive・Investing.com 11/4）。
- 保有・候補は ±5%未満（AMD +0.8%、WDC +0.8%、LITE +0.4%、SNDK +0.3%、FTNT +0.2%、MRVL +0.1%、NTAP +0.0%）。

## AMD（保有）
- 11/3 引け後に決算。データセンター売上がほぼ倍増、CEOは成長の加速を予想（CNBC 11/3）。当日 +1.0%。
- 1週は −15.5%。AMD固有の悪材料は見出しになし。24/7 Wall St. 11/4「Nvidia is Far From The Only Threat to AMD」（競合の記事）。
- 次回決算 2027-02-02（scan.md）。
- 悪材料: 確認できず

## SNDK（保有）
- 10/30 TradingPedia「決算の質に疑問」で下げ。11/3 Yahoo Finance「10月に24%下落」。
- 11/4 24/7 Wall St.「選挙とメモリ価格の懸念でSanDisk −9%、Micron・WDC −7%」。同日「Appleの苦境はMicronに追い風、メモリ価格急騰」。
- 悪材料: あり（決算の質への疑問、データセンター関連の売り）

## NTAP（候補）
- 銘柄固有の見出しは取得できず（Yahoo の見出しは他社中心）。1週 −16.1%はストレージ全体の下げと同じ動き。
- 次回決算 2026-12-01（scan.md）。
- 悪材料: 確認できず

## LITE（候補）
- 10/28〜29 マーベルによる買収報道（Barron's・IBD 10/29「Marvell Stock Slides」）。11/2 は約1,150億ドルの全株式合併として報じられ LITE −6〜14.9%（24/7 Wall St.・Yahoo Finance 11/2）。
- 10/30 光関連が急落（AAOI −15%、COHR −13%、LITE・MRVL −10%、24/7 Wall St. 10/30）。
- 時間外 +0.4%（材料なし）。次回決算 2027-02-02（scan.md）。
- 悪材料: あり（買収の条件・株式交換への市場の反発）

## MRVL（候補）
- LITE買収の発表後に大幅下落。Motley Fool 11/4「ジェンセン・ファンが次の1兆ドル企業と呼んで以降46%下落」。24/7 Wall St. 11/4「ルメンタム発表で急落」。
- 時間外 +0.1%。次回決算 2026-12-01（scan.md）。
- 悪材料: あり（大型買収への反発。取引は未完了）

## FTNT（候補）
- 10/29 決算後に急落（Yahoo Finance・Zacks・Barron's 10/29「記録的な2日間の下げ、主要な収益源が原因か」）。TIKR 11/3「予想・ガイダンスを上回ったが1週で31%下落」。
- 11/4 24/7 Wall St. の格上げ・格下げ一覧に掲載（内容は見出しのみで未確認）。
- 次回決算日 2026-10-28は発表済み（scan.md）。
- 悪材料: あり（決算後の売り、ソフト株全体の下げ）

## WDC（候補）
- 11/3 Yahoo Finance「好決算」、11/4 は SNDK・MU とともに −7%（24/7 Wall St. 11/4）。
- 次回決算 2027-01-28（scan.md）。
- 悪材料: 確認できず（決算は好調と報じられている）

## 監視外の注目銘柄（MRNA・CNC・BBY・SWK・HAS）
- 見出し・検索では原因を確認していない（headlines.md に対象外）。確認できず。

# ニュースの見出し（プログラムが自動で取得）

- Googleニュース（日付を指定）とYahooファイナンスの見出しを `tools/news_headlines.py` が自動で並べたもの。日付は米国東部時間の配信日（引け後の記事は翌日付）。原因の判断・売買の判断はしていない。
- 調べた銘柄の選び方: ①保有 ②今日の候補 ③時間外に±5%以上動いた監視銘柄 は全部、④引けまでに大きく動いた銘柄（1週で±5%のグループの上位3・1日で±7%）は合計12銘柄まで。
- 1週で−5%以下のグループ: AIサーバー・ストレージ・メモリ・端末（-17.3%）、半導体製造装置・材料・設計ソフト・計測（-10.0%）、光・通信・ネットワーク（-9.8%）、AIソフト・セキュリティ・ITサービス（-6.2%）、半導体（-5.8%）
- 1週で+5%以上のグループ: なし

## 0. 時間外（引け後）の値動き（2026-11-04 の引けから、Yahoo。±3%以上の監視銘柄と、保有・候補は全部）

| 銘柄 | 区分 | 引け | 時間外 | 騰落率 |
|---|---|---|---|---|
| APP | 監視 | 271.30 | 330.50（17:21 ET） | **+21.8%** |
| QCOM | 監視 | 173.73 | 159.00（17:21 ET） | **-8.5%** |
| COHR | 監視 | 195.24 | 211.50（17:21 ET） | **+8.3%** |
| AMD | 保有 | 488.85 | 492.92（17:21 ET） | +0.8% |
| WDC | 候補 | 323.71 | 326.14（17:20 ET） | +0.8% |
| LITE | 候補 | 626.76 | 629.19（17:21 ET） | +0.4% |
| SNDK | 保有 | 1037.29 | 1040.50（17:21 ET） | +0.3% |
| FTNT | 候補 | 129.39 | 129.66（17:19 ET） | +0.2% |
| MRVL | 候補 | 159.91 | 160.11（17:21 ET） | +0.1% |
| NTAP | 候補 | 187.62 | 187.67（17:04 ET） | +0.0% |

## 1. 市場全体（2026-11-04）

### 市場全体（英語のまとめ記事）
検索語: `stocks Wall Street close Nasdaq`
- 11/4 Reuters | Wall Street ends higher after Democrats win Congress; data center stocks tumble
- 11/4 NBC News | Stocks surge as ‘blue tsunami’ puts political uncertainty to rest
- 11/4 The New York Times | Stocks Rise as Democrats Flip Control of Congress
- 11/4 Investor's Business Daily | Stock Market Today: Stock Market News And Analysis
- 11/4 Yahoo Finance | Stock Market News for Nov 4, 2026

### 市場全体（Stock Market Today）
検索語: `"stock market today"`
- 11/4 Bloomberg | Stocks and Bonds Rise, Dollar Slides After US Vote: Markets Wrap
- 11/4 Bergen Record | How has the stock market fared day after midterm elections?
- 11/4 Beinsure | Stock Market Today: S&P 500, Nasdaq, Dow Jones jump after Democratic election win
- 11/4 ChartMill | Stock Market Today: Democrats Take Congress as AMD’s Blowout Quarter Pulls Chip Stocks Back Into the Light

### 市場全体（日本語のまとめ記事）
検索語: `米国株式市場 OR NY株`
- 11/4 Reuters | 米国株式市場＝ダウ1500ドル超高、民主圧勝受け データセンターは安い
- 11/4 産経ニュース | NY株反発、一時千ドル超高 米中間選挙の不確実性後退、政治混乱への警戒和らぐ
- 11/4 47NEWS | 【速報】NY株、一時1200ドル超高
- 11/4 京都新聞デジタル | ＮＹ株急反発、１５６９ドル高

### 半導体・AI株（英語）
検索語: `chip stocks OR semiconductor stocks OR AI stocks`
- 11/4 Yahoo Finance | Semiconductor Sell-Off: The Best Chip Stocks to Buy Right Now Before They Skyrocket Once Again
- 11/4 MarketWatch | Micron and other chip stocks slip as election results strike at the core of data-center optimism
- 11/4 Investor's Business Daily | Chip Stocks Feeling Blue After Democratic Party Victories
- 11/4 Quartz | Chip stocks slip as Democrats' election sweep clouds the outlook for data centers

### 信用（社債・借金）
検索語: `AI debt OR bonds OR credit spreads OR CDS`
- （取得できなかった）

### 「〇〇ショック」の呼び名（日本語）
検索語: `ショック 株`
- （取得できなかった）

### 引け後・時間外の動き（英語）
検索語: `"after hours" OR "after the bell" OR "extended trading" stocks`
- 11/4 Investing.com | Arm stock slips after hours as lack of blowout guidance offsets quarterly results
- 11/4 Seeking Alpha | Stocks to watch on Wednesday after hours: COST, EXPE, VJET, ALL (COST:NASDAQ)
- 11/4 24/7 Wall St. | Duolingo Is Up 11% After Hours as Its User Growth Speeds Up Again
- 11/4 investingLive | Arm shares fall 5% after hours despite Q2 beat as outlook only edges past forecasts
- 11/4 Moomoo | November 4, 2026 Morning Report: US Stock Market After-Hours Analysis
- 11/4 AskTraders.com | Arm Beats Forecasts but Stock Slips After Hours
- 11/4 TradingView | Limbach Holdings (LMB) Shares Jump 19% After-Hours Tuesday: Here’s Why

### 引け後・時間外の動き（日本語）
検索語: `時間外 決算 株`
- （取得できなかった）

### 買収・合併（英語）
検索語: `acquisition OR acquire OR merger OR takeover chip OR semiconductor OR AI OR optical`
- 11/4 Axios | Exclusive: Meta buys AI startup, joins race to own coding in show of outsized ambition
- 11/4 OpenAI | OpenAI to acquire Pierre Computer Company, Inc.
- 11/4 CSO Online | CrowdStrike to acquire Fiddler, Dreadnode to extend AI security across agent lifecycle
- 11/4 Built In | What Is the AI Takeover Theory? Risks, Possibilities and Prevention
- 11/4 Investing.com | SiTime faces earnings test on AI timing demand, acquisition gains
- 11/4 Morningstar | Jobber Integrates with AI Mode in Google Search, Opening a New Customer Acquisition Channel for Home and Commercial Service Businesses
- 11/4 citybiz | Agilent Completes Proscia Acquisition for Up to $270M, Expanding AI-Powered Digital Pathology Capabilities
- 11/4 TradingView | PCOR Q3 2026 deep dive: AI advances and DroneDeploy acquisition fuel broad-based growth

## 2. 保有・候補・時間外で大きく動いた銘柄（2026-10-29〜2026-11-04 の見出し）

### SNDK（Sandisk Corporation、保有、AIサーバー・ストレージ・メモリ・端末、前日比 -7.9%、1週 -26.2%、時間外 +0.3%）

#### Googleニュース
検索語: `Sandisk stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 10/30 TradingPedia | SanDisk Stock Falls as Investors Question Earnings Quality
- 11/3 Yahoo Finance | Why Sandisk Stock Dropped 24% in October
- 11/3 Investing.com | Why is SanDisk stock rallying today?

#### Yahooファイナンス
検索語: `SNDK`
- 11/4 24/7 Wall St. | Apple’s Pain Could Be Micron’s Gain as Memory Prices Surge
- 11/4 24/7 Wall St. | Prediction: This Could Be the Best AI Stock You’re Not Talking About
- 11/4 24/7 Wall St. | SanDisk Retreats 9%, Micron and Western Digital Fall 7% as Election and Memory Price Worries Weigh

### AMD（Advanced Micro Devices, Inc.、保有、半導体、前日比 +1.0%、1週 -15.5%、時間外 +0.8%）

#### Googleニュース
検索語: `Advanced Micro Devices stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 10/30 Yahoo Finance | Investors Heavily Search Advanced Micro Devices, Inc. (AMD): Here is What You Need to Know
- 11/2 CNN | AMD Stock Quote Price and Forecast
- 11/3 CNBC | AMD's data center revenue nearly doubles in Q3 and CEO Su expects growth to accelerate
- 11/3 Investing.com | Why is Advanced Micro Devices stock rallying today?

#### Yahooファイナンス
検索語: `AMD`
- 11/4 Barrons.com | SpaceX, Tesla, Micron, AMD, Lockheed, CVS, DJT, and More Stocks That Explain Today’s Market
- 11/4 Investor's Business Daily | Stock Market Today: Dow Soars 1,569 Points In Post-Election Rally; Microsoft Leaps Nearly 7% Off New Entry
- 11/4 Motley Fool | AMD Stock Rebounds. Is Its AI Edge Built to Last?

### NTAP（NetApp, Inc.、候補、AIサーバー・ストレージ・メモリ・端末、前日比 -1.6%、1週 -16.1%、時間外 +0.0%）

#### Googleニュース
検索語: `NetApp stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- （取得できなかった）

#### Yahooファイナンス
検索語: `NTAP`
- 11/4 Trefis | Does The Move In Hewlett Packard Enterprise Stock Change Anything?
- 11/4 Trefis | What Could Go Wrong With Western Digital Stock?
- 11/4 Trefis | What Did SanDisk's Quarter Change For Its Stock?

### LITE（Lumentum Holdings Inc.、候補、光・通信・ネットワーク、前日比 -7.9%、1週 -31.4%、時間外 +0.4%）

#### Googleニュース
検索語: `Lumentum stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 10/29 Barron's | Marvell Stock Slides. Why the Market Hates the Idea of a Lumentum Buyout.
- 10/29 Investor's Business Daily | Lumentum Jumps, Fades On Marvell Buyout Report
- 11/2 Yahoo Finance | Why Lumentum Stock Fell 14.9% Today
- 11/2 24/7 Wall St. | Marvell Slides 3%, Lumentum Drops 6% on $115 Billion All-Stock Merger Deal; Coherent Climbs 2%

#### Yahooファイナンス
検索語: `LITE`
- 11/4 24/7 Wall St. | If You Invest $1,000 in Marvell Today, Here’s What It Could Be Worth by 2030
- 11/4 24/7 Wall St. | Marvell Slipped Over The Last Month and Then Crashed Massively on the Lumentum Announcement: This Wall Street Desk Doubled Down on Its 130% Gains Prediction
- 11/4 Motley Fool | Marvell Stock Has Plunged 46% Since Jensen Huang Called It the Next $1 Trillion Company. Here's Why.

### MRVL（Marvell Technology, Inc.、候補、半導体、前日比 -7.1%、1週 -36.5%、時間外 +0.1%）

#### Googleニュース
検索語: `Marvell stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- （取得できなかった）

#### Yahooファイナンス
検索語: `MRVL`
- 11/4 24/7 Wall St. | Nvidia is Far From The Only Threat to AMD
- 11/4 Motley Fool | Marvell's Deal to Acquire Lumentum Could Be a Game Changer for the Stock

### FTNT（Fortinet, Inc.、候補、AIソフト・セキュリティ・ITサービス、前日比 +1.0%、1週 -25.7%、時間外 +0.2%）

#### Googleニュース
検索語: `Fortinet stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 10/29 Yahoo Finance | ServiceNow stock sinks in worst day ever, Fortinet shares drop as Q3 earnings reports send software sector lower
- 10/29 Barron's | Fortinet Stock Heads for Record 2-Day Rout. A Key Revenue Driver May Be to Blame.
- 10/29 Zacks Investment Research | Fortinet (FTNT) Stock Plunges After Q3 Earnings: Time to Buy the Dip?
- 10/29 Yahoo Finance | Why Fortinet Stock Plunged More Than 20% Today

#### Yahooファイナンス
検索語: `FTNT`
- 11/3 TIKR | “Share Donor”: Fortinet Sinks 31% in a Week Despite Beating and Raising Guidance
- 11/4 24/7 Wall St. | Buy, Sell, or Hold? Wednesday’s Top Upgrades and Downgrades: Adobe, Apple, Duolingo, Exxon Mobil, Fiserv, Fortinet, Gartner, Lockheed Martin, Skyworks Solutions, Visa and More
- 11/4 CNW Group | Earnings Gaps and a Lost 50-Day Line Set the Levels Chart Watchers Have Circled

### WDC（Western Digital Corporation、候補、AIサーバー・ストレージ・メモリ・端末、前日比 -6.8%、1週 -18.3%、時間外 +0.8%）

#### Googleニュース
検索語: `Western Digital stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/2 The Motley Fool | Prediction: This Will Be Western Digital's Stock Price in 2030
- 11/3 Yahoo Finance | Why Western Digital’s (WDC) Massive Quarter Is Only the Beginning (ready)
- 11/3 Investing.com | Why is Western Digital stock rallying today?

#### Yahooファイナンス
検索語: `WDC`
- 11/4 Insider Monkey | 5 Cheapest AI Data Center Stocks to Buy According to Billionaires

### APP（AppLovin Corporation、AIプラットフォーム・クラウド、前日比 +10.7%、1週 +4.5%、時間外 +21.8%）

#### Googleニュース
検索語: `AppLovin stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/1 Trefis | What Just Happened To AppLovin Stock?
- 11/4 Yahoo Finance | AppLovin Stocks Jump 8.8% While Tonight's Earnings Face a $2.08 Billion Test
- 11/4 Investor's Business Daily | AppLovin Stock Surges As Earnings Beat Provides Much-Needed Boost
- 11/4 24/7 Wall St. | AppLovin Is Still Down 60% This Year: Did Today Just Mark the Bottom for APP Stock?

#### Yahooファイナンス
検索語: `APP`
- 11/4 Associated Press | AppLovin: Q3 Earnings Snapshot
- 11/4 Barchart | Dear AppLovin Stock Fans, Mark Your Calendars for November 4

### QCOM（QUALCOMM Incorporated、半導体、前日比 +5.3%、1週 -5.3%、時間外 -8.5%）

#### Googleニュース
検索語: `QUALCOMM stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 10/30 Investing.com | Why is Qualcomm stock tumbling today?
- 10/30 Seeking Alpha | QUALCOMM drops 12% as tech stocks fall (QCOM:NASDAQ)
- 11/3 Yahoo Finance | Should You Buy Qualcomm Stock Before Its Nov. 4 Report?
- 11/4 CNBC | Qualcomm stock drops 6% on weak earnings forecast as memory shortage weighs on smartphone sales

#### Yahooファイナンス
検索語: `QCOM`
- 11/4 Associated Press | Qualcomm: Fiscal Q4 Earnings Snapshot
- 11/4 Barrons.com | Qualcomm’s Stock Falls as Supply Costs Eat Into Profit Outlook

### COHR（Coherent Corp.、光・通信・ネットワーク、前日比 -6.0%、1週 -18.6%、時間外 +8.3%）

#### Googleニュース
検索語: `Coherent stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 10/29 Investing.com | Why is Coherent stock gaining today?
- 10/30 24/7 Wall St. | Applied Optoelectronics Plunges 15%, Coherent Tumbles 13% as Hyperscaler Spending Fears Hit AI Optics Stocks; Lumentum and Marvell Sink 10%
- 10/31 Yahoo Finance | Coherent Stock Fell 11% as Intel and Amazon Earnings Hit AI Hardware Stocks. Here’s Where the Stock Could Go
- 11/3 TIKR.com | Coherent Soars 6% as Fabrinet’s 51% Revenue Jump Lifts Optics Stocks Ahead of Earnings

#### Yahooファイナンス
検索語: `COHR`
- 11/4 Associated Press | Coherent: Fiscal Q1 Earnings Snapshot
- 11/4 Barchart | Dear Coherent Stock Fans, Mark Your Calendars for November 4
- 11/4 Benzinga Prediction Markets | Coherent Earnings Prediction Market Preview: What Will Jim Anderson Say?

## 3. 引けまでに大きく下げた銘柄（2026-10-29〜2026-11-04 の見出し）

### DELL（Dell Technologies Inc.、AIサーバー・ストレージ・メモリ・端末、前日比 -8.8%、1週 -24.6%、時間外 +0.3%）

#### Googleニュース
検索語: `Dell stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 10/29 Yahoo Finance | HPQ, DELL Stocks Plunge After Intel Flags Prolonged PC Market Weakness
- 10/30 24/7 Wall St. | Dell Sinks 11% as Intel's Warning on PC Slump and Memory Shortage Hits Hardware Stocks; HP Tumbles 9%, Hewlett Packard Enterprise and Super Micro Fall 7%
- 10/31 Yahoo Finance | Why Dell (DELL) shares are getting obliterated today
- 11/2 MarketWatch | Dell Technologies Inc. Cl C stock falls Monday, underperforms market

#### Yahooファイナンス
検索語: `DELL`
- 11/4 24/7 Wall St. | Nike Climbs 7% as Dow Rally Lifts Consumer Stocks; Deckers Gains 7%, Lululemon Rises 6%
- 11/4 24/7 Wall St. | Super Micro Falls 4% Despite Blowout Quarter as Margin Worries and Data Center Backlash Weigh; Dell Sinks 8%, Hewlett Packard Enterprise Drops 6%

### STX（Seagate Technology Holdings plc、AIサーバー・ストレージ・メモリ・端末、前日比 -8.1%、1週 -20.2%、時間外 +0.8%）

#### Googleニュース
検索語: `Seagate stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 10/30 Seeking Alpha | Seagate Technology dragged down by tech retreat, falls 8% (STX:NASDAQ)
- 10/31 shattered.io | Seagate Stock Falls 8% as Tech Retreat Hits Storage [2026]
- 10/31 https://tech-insider.org/ | Seagate Stock Drop: Falls 8% to $641.81 [2026]
- 11/2 Investing.com | Why is Seagate Technology stock sliding today?

#### Yahooファイナンス
検索語: `STX`
- 11/3 MT Newswires | Seagate Technology Holdings Insider Sold Shares Worth $14,024,766, According to a Recent SEC Filing
- 11/3 MT Newswires | Seagate Technology Holdings Insider Sold Shares Worth $4,185,349, According to a Recent SEC Filing
