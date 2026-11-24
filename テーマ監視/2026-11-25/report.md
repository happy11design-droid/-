# テーマ監視 2026-11-24

# 判定のまとめ（ルールの判定と著者の判定を分けて表示）

- **ルールの判定**: 採用した売買ルール（スクリプト）が数値で決めたもの。損切りは買値の15%下の逆指値（日中に届けばその場で売れる）。
- **著者の判定**: ノートブックの著者の回答。買いは注文を止める理由があるときだけ【様子見】、保有はルールより早く手じまう理由があるときだけ【売り】。根拠は下の「著者の回答（全文）」。
- 2つが食い違うときに、どちらに従うかはユーザーが決める。

- **テーマ全体の急落（S2・記録だけ）: あり（S2）**（SOXが直近60取引日の最高値から -33.2%）。S2の日の順張りの候補には「S2なら見送る形」と付ける（売買のルールは変えない。記録してから採用を決める。2026-10-14）

- **特殊な下げ（記録だけ）: あり（特殊な下げ）**（2026-10-16から）（SOXが直近60取引日の最高値から -33.2%、前の1年の大きな上げ・雇用の弱さ・物価の再加速のうち 2つ）。1995年〜では、この形の後にSOXの下げが長引くことが多かった（後知恵を含む）。売買のルールは変えない（2026-11-03）

## 保有銘柄

| 銘柄 | ルール | 損益 | 時間外 | ルールの判定 | ルールの判定の理由 | 著者の判定 |
|---|---|---|---|---|---|---|
| SNDK | ルール外（ユーザーの判断。この日はどのルールの合図もなし） | -54.5% | +0.2% | **売り** | 終値 77.95 が損切り価格 145.7 以下 | 【未判定】（） |
| AMD | ボリンジャーIII | -24.9% | +1.1% | **売り** | 終値 413.27 が損切り価格 467.47 以下 | 【保有継続】（ボリンジャー） |

## 候補の判定（並びは上の「買う順番」の表と同じ）

- 並びは上の「買う順番」の表と同じ（RSの高い順。勝率の高い順ではない）。注文の値段・株数・逆指値は上の表を見る。勝率・1回平均は、そのルールの過去の成績（後知恵なしの監視銘柄・2015年〜の全部の合図）。
- 空き枠: 4（同時保有4銘柄まで。保有2、うちルールの売り2）。著者が【様子見】の候補を見送るかはユーザーが決める。

| 順 | 銘柄 | ルール | 過去の勝率 | 過去の1回平均 | RS | 時間外 | ルールの判定 | 著者の判定 |
|---|---|---|---|---|---|---|---|---|
| 1 | DLTR | 順張り: 新高値（V2、担当: ミネルヴィニ） | 45% | +2.1% | 96 | -0.5% | 買い（翌日の寄り付き）（S2なら見送る形・記録だけ） | 【様子見】（ミネルヴィニ） |
| 2 | ANET（アリスタ・ネットワークス） | 逆張り: 急落の底（担当: コナーズ）（指値の3日目） | 65% | +2.1% | 66 | -0.2% | 買い（指値 164.27、3取引日まで） | 【様子見】（コナーズ） |
| 3 | NBIS（ネビウス・グループ） | 逆張り: 急落の底（担当: コナーズ）（指値の3日目） | 65% | +2.1% | 2 | +0.8% | 買い（指値 79.68、3取引日まで） | 【様子見】（コナーズ） |

- 時間外: 前の取引日の引けから、引け後（米国東部時間16〜20時）の最後の値までの騰落率（Yahoo。±5%以上は太字）。寄り付きの値段は、表の注文の目安（前日の終値で計算）から大きくずれることがある。原因の見出しは「ニュースの見出し」の節。

# 著者の回答（全文）

## 0_テーマの局面_ワインスタイン

1. **テーマ全体の局面**: 【ステージ3】（急騰後の大幅調整、30週線横ばいかつ線の下で推移、第2章）
2. **グループごとの局面**:
- 半導体｜ステージ3｜30週線横ばい・線の下（第2章）
- 半導体製造装置・材料・設計ソフト・計測｜ステージ4｜30週線下落・線の下（第2・7章）
- AIサーバー・ストレージ・メモリ・端末｜ステージ3｜30週線横ばい・線の下（第2章）
- 光・通信・ネットワーク｜ステージ4｜30週線下落・線の下（第2・7章）
- データセンターの電力・冷却・部品・受託製造・建設｜ステージ4｜30週線下落・線の下（第2・7章）
- AIプラットフォーム・クラウド｜ステージ3｜30週線横ばい・線の下（第2章）
- AIソフト・セキュリティ・ITサービス｜ステージ3｜30週線横ばい・線の下（第2章）
3. **転換の兆し**: 出ている。30週線割れ（第2章）、3群の30週線下落（第2・7章）、対S&P500のRS悪化（第4章）、50日線超が9%の内部崩壊（第3・8章）。※ニュース等は規定なし。
4. **テーマの外**: 判定不能（データ省略のため）

（全体の版が空の応答だったため、1〜2節だけの短い版で送り直した回答。ヒートマップ・急騰急落・ニュースは渡していない）

## 1_コナーズ_prompt_1

## ANET
1. **投資判断**: 【様子見】（200日移動平均線を下回ったため）
2. **止める理由の確認**:
- 本が禁じる形・状況｜あり｜終値168.56が200日線168.92下のため白紙（第4章）
- 避けるべき時期（決算など）｜なし｜決算まで77日、禁止時期外（第11章）
- 悪材料｜なし｜報道による見送り規定なし・織り込み済み（第2・3章）
3. **現状パターンと価格**:
- 現状パターン: A（条件成立中だが200日線割れ）
- 本日の発注: なし（見送り）
4. **注意点**: 再び200日線の上側で引けるまで買いエントリーは厳禁。

## 1_コナーズ_prompt_2

## NBIS
1. **投資判断**: 【様子見】（株価が200日線の下側にあるため）
2. **止める理由の確認**:
- 本が禁じる形・状況｜あり｜第4章：株価が200日移動平均線の下側にある株の買いは厳禁（MA200乖離-51.4%） [1-3]
- 避けるべき時期（決算など）｜なし｜決算まで79日。第11章の月初（3〜8日）にも非該当 [2, 4]
- 悪材料｜なし｜マニュアルに規定なし。悪材料やパニックによる急落はむしろ好機（第2・3章） [5-8]
3. **現状パターンと価格**:
- 現状パターン: A（条件成立済・指値3日目）
- 本日の発注: なし（見送り）
4. **注意点**: 200日線の下にある銘柄を「底値」と見込んで買うと大暴落に巻き込まれるため、取引は白紙に戻すこと（第4章） [2, 3]。

## 1_ボリンジャー_prompt_1

## AMD
1. **投資判断**: 【保有継続】（本基準での早期手じまい理由なし）
2. **止める理由の確認**:
- 本が禁じる形・状況｜なし｜第13章・第17章等の危険な天井形なし [1, 2]
- 避けるべき時期（決算など）｜なし｜マニュアルに規定なし [3]
- 悪材料｜なし｜マニュアルに規定なし [3]
3. **現状パターンと価格**:
- 現状パターン: 保有中（ボリンジャーIII）
- 保有中: `売りの予約注文: なし`
4. **注意点**: スクリプト設定の手じまいルールに従うこと。

## 1_ミネルヴィニ_prompt_1

## DLTR
1. **投資判断**: 【様子見】（高値追いのため）
2. **止める理由の確認**:
- 本が禁じる形・状況｜あり｜第10章（追いかけ買い禁止）
- 避けるべき時期（決算など）｜なし｜マニュアルに規定なし
- 悪材料｜なし｜該当なし
3. **現状パターンと価格**:
現状パターン: C（高値超え伸長で追随）
押し目監視価格: 153.00（現在値比 -1.1%）／再エントリー条件: ピボット+3%以内へ反落
4. **注意点**: 決算当日のため発表後の株価反応に注意。

# スキャン（数値と事実）


- 監視銘柄 87（判定できたのは 87）。
- この一覧は数値と事実だけ。売買の判断は著者のノートブックが行う。

## 1. テーマ（グループ）の強さ

| グループ | 銘柄数 | 1週 | 1カ月 | 3カ月 | 3カ月の順位 | 50日線より上の銘柄の割合 | グループ指数の30週線の局面（線との乖離、4週前からの線の傾き） |
|---|---|---|---|---|---|---|---|
| 半導体 | 16 | -9.6% | -22.2% | -15.6% | 4位 | 0% | 横ばい（-21.0%、+3.1%） |
| 半導体製造装置・材料・設計ソフト・計測 | 9 | -4.8% | -15.9% | -23.4% | 6位 | 0% | 下落（-22.9%、-0.1%） |
| AIサーバー・ストレージ・メモリ・端末 | 9 | -5.8% | -26.6% | -36.2% | 7位 | 11% | 横ばい（-21.0%、+4.4%） |
| 光・通信・ネットワーク | 9 | -6.1% | -14.7% | -20.7% | 5位 | 11% | 下落（-20.5%、-0.3%） |
| データセンターの電力・冷却・部品・受託製造・建設 | 19 | -3.8% | -7.1% | -12.3% | 3位 | 0% | 下落（-14.3%、-0.5%） |
| AIプラットフォーム・クラウド | 11 | -2.2% | -6.7% | -3.1% | 1位 | 27% | 横ばい（-12.0%、+0.5%） |
| AIソフト・セキュリティ・ITサービス | 14 | -1.2% | -17.8% | -6.0% | 2位 | 21% | 横ばい（-1.0%、+3.8%） |

## 2. テーマ全体の状態と早めの警告

- 市場全体の30週線による局面: S&P500指数 **横ばい**／NASDAQ100指数 **横ばい**（急落の底で買うルールは、過去の検証で下落相場で特に強く、横ばいの相場では負けていた）
- **2倍ETFを使う局面（案1、2026-10-13 採用）: S&P500の20週線（100日線）で 横ばい** → 新しく買う銘柄は、2倍ETFのある銘柄も元の株で買う（保有中のETFはそのまま）（SPY 718.78、100日線 757.87、20日前の線 756.87。上昇＝線より上かつ線が上向き）
- **テーマ全体の急落（S2、記録だけ。売買のルールは変えない）: あり（S2）**（SOX 8832.50、直近60取引日の最高値 13217.82 から -33.2%。S2＝最高値から−10%以上）。S2のときに「順張りの新しい買いだけ止める」形を記録で比べる（2026-10-14 ユーザー決定。バックテストでは年率は上がったが2つの期間ではどちらも少し下回ったため、記録してから採用を決める。`バックテスト結果/テーマ全体の急落を検知して手じまう・買いを止める.md`）
- **グループごとの悪いニュースの流れ（記録だけ。売買のルールは変えない。2026-11-11〜2026-11-24）**: 会社の名前と悪い言葉（格下げ・目標株価の引き下げ・見通しの引き下げ・予想未達・急落・信用・訴訟・輸出規制など）の両方がある見出しの数（Googleニュース、`tools/news_headlines.py`）。10取引日の1銘柄あたりが一番多いグループに印。2026年7〜11月の確かめでは、印のグループの合図は10月は成績が悪かった（1回平均 −10.6%、ほか −5.6%）が、7〜9月は逆に良かった（+11.6%、ほか +6.7%）（`バックテスト結果/実際の運用の期間の確認_2026-10-23/グループの悪いニュースの流れ.md`。2026-11-04）

| グループ | 悪いニュース 直近5取引日 | その前の5取引日 | 10取引日の1銘柄あたり | 良いニュース 10取引日（1銘柄あたり） | 印 |
|---|---|---|---|---|---|
| 半導体（16） | 27件 | 53件 | 5.0 | 47件（2.9） | **悪いニュースが続いている** |
| 光・通信・ネットワーク（9） | 3件 | 14件 | 1.9 | 5件（0.6） |  |
| AIサーバー・ストレージ・メモリ・端末（9） | 7件 | 3件 | 1.1 | 37件（4.1） | **良いニュースが多い** |
| AIプラットフォーム・クラウド（11） | 5件 | 4件 | 0.8 | 4件（0.4） |  |
| 半導体製造装置・材料・設計ソフト・計測（9） | 5件 | 1件 | 0.7 | 10件（1.1） |  |
| データセンターの電力・冷却・部品・受託製造・建設（19） | 4件 | 3件 | 0.4 | 6件（0.3） |  |
| AIソフト・セキュリティ・ITサービス（14） | 1件 | 1件 | 0.1 | 12件（0.9） |  |

印のグループ（半導体）の最近の見出し: 2026-11-24 Micron Shares Plunge 11% Following BNP Paribas Downgrade on Memory Oversupply Concerns（재경일보）／2026-11-24 Micron Drops Over 7% on Wall Street Following Brokerage Downgrade : 기업주식정보 : JKN（재경일보）／2026-11-24 Micron Shares Fall After BNP Paribas Downgrade（marketscreener.com）

良いニュースが多いグループ（AIサーバー・ストレージ・メモリ・端末）の最近の見出し: 2026-11-24 Major Banks Block AI Agents Ahead of Apple’s Siri Upgrade（The Mac Observer）／2026-11-24 I changed 5 settings and it was like a free upgrade for my Apple TV 4K（Pocket-lint）

- **特殊な下げ（記録だけ。売買のルールは変えない）: あり（特殊な下げ）**（2026-10-16から）。SOX は直近60取引日の最高値から -33.2%（−15%以下が条件）、●A 前の1年の上げ +105.8%（+80%以上）、・B 雇用の伸び 137千人/月（2026-10まで。10万人未満）、●C 物価 4.1%（2026-10。3か月前 3.5%。3.5%以上で再加速）＝2つ（2つ以上が条件）。1995年〜でSOXが−15%以下かつ条件2つ以上の日は、120日後にSOXが下だったのが69%・250日後が70%（中央値 −33%）、AI以外の8業種の平均は250日後 −7%。ただし条件は過去を見て選んだもの（条件が2つ以上の局面は約5回）で、2026年7〜9月にこの間テーマを買わないと、その後の戻りを逃して2026年の成績は下がった（`バックテスト結果/実際の運用の期間の確認_2026-10-23/特殊な下げと過去の似た下げ.md`。2026-11-03）
- テーマ指数（監視銘柄の等金額平均）の30週線による局面: **横ばい**（上昇＝線より上かつ上向き、下落＝線より下かつ下向き、それ以外＝横ばい。ワインスタインのステージの近似）
- テーマ指数と50日線: 50日線より下（乖離 -14.5%）
- S&P500に対する相対的な強さ: 50日平均より下（S&P500より弱い）
- 監視銘柄のうち50日線より上の割合: 9%
- 警告（割合が40%未満かつテーマ指数が50日線より下）: **出ている**
- 参考（バックテスト）: 30週線の「下落」は高値から10〜33%下げた後に出る遅い判定。50日線・割合・相対的な強さは高値から2〜8%で出るが、誤報が年15回以上ある。警告中に新しい買いを止めると、押し目買い（ボリンジャーIII）の成績は大きく下がった（`バックテスト結果/テーマ監視銘柄・直近3年.md` 11・12節）。

## 3. ヒートマップ（Finviz、全米の業種別の騰落率）

3カ月の騰落率の上位15業種（テーマの外で強くなっている業種の確認用）:

| 順位 | 業種 | 1週 | 1カ月 | 3カ月 | 6カ月 | 1年 |
|---|---|---|---|---|---|---|
| 1 | Discount Stores | +3.3% | +10.9% | +22.3% | +13.9% | +28.1% |
| 2 | Advertising Agencies | -3.3% | +32.6% | +16.4% | -22.9% | -20.3% |
| 3 | Medical Distribution | -0.4% | +8.2% | +14.8% | +37.4% | +17.1% |
| 4 | Consumer Electronics | +0.7% | +3.0% | +13.0% | +14.2% | +28.6% |
| 5 | Insurance - Diversified | -1.4% | +4.4% | +12.1% | +18.2% | +14.0% |
| 6 | Lodging | -1.6% | +5.6% | +11.4% | +8.2% | +33.4% |
| 7 | Household & Personal Products | +0.3% | +5.1% | +10.6% | +15.1% | +12.4% |
| 8 | Insurance - Reinsurance | +0.6% | +3.3% | +9.5% | +24.8% | +39.2% |
| 9 | Waste Management | +0.5% | +0.7% | +9.2% | +17.3% | +9.9% |
| 10 | REIT - Hotel & Motel | -1.7% | +1.5% | +9.2% | +17.3% | +49.7% |
| 11 | Medical Instruments & Supplies | +1.5% | +2.0% | +9.0% | +17.3% | -0.5% |
| 12 | Drug Manufacturers - General | +0.5% | +5.8% | +7.5% | +20.4% | +26.4% |
| 13 | Diagnostics & Research | +1.9% | -1.7% | +7.4% | +43.7% | +16.5% |
| 14 | Auto Manufacturers | +0.5% | -0.6% | +7.2% | -10.4% | -2.5% |
| 15 | Grocery Stores | -1.0% | -0.5% | +6.6% | -2.7% | -3.6% |

テーマの業種の順位（3カ月、全144業種中）: Semiconductors 129位、Semiconductor Equipment & Materials 136位、Computer Hardware 141位、Communication Equipment 124位、Electronic Components 125位、Software - Infrastructure 69位、Software - Application 110位、Internet Content & Information 108位

## 4. 急騰・急落した銘柄（前日比±5%以上、または出来高が50日平均の2倍以上）

原因のニュースをサブエージェントが調べ、候補・保有銘柄の判定材料として著者に渡す。急騰・急落そのものは売買の合図にしない（後知恵のないS&P500全体のバックテストでは、急騰の翌日に買うルールは年率7%、急落の翌日に買うルールは年率9〜10%で、採用した3つのルールより優れていなかった）。

| 銘柄 | グループ | 前日比 | 出来高（50日平均の倍） | 終値 | 50日線 | RS | 局面 |
|---|---|---|---|---|---|---|---|
| SNDK | AIサーバー・ストレージ・メモリ・端末 | -17.4% | 1.2倍 | 77.95 | 下 | 28 | 下げ |
| ADI | 半導体 | -17.4% | 3.1倍 | 312.95 | 下 | 27 | 下げ |
| HPE | AIサーバー・ストレージ・メモリ・端末 | -16.3% | 2.5倍 | 40.19 | 下 | 95 | 下げ |
| ALAB | 半導体 | -13.9% | 1.4倍 | 191.30 | 下 | 28 | 下げ |
| CRWV | AIプラットフォーム・クラウド | -11.8% | 1.1倍 | 42.60 | 下 | 0 | 下落相場 |
| DELL | AIサーバー・ストレージ・メモリ・端末 | -11.8% | 2.5倍 | 295.28 | 下 | 97 | 下げ |
| TXN | 半導体 | -11.2% | 1.8倍 | 258.44 | 下 | 76 | 下げ |
| MU | 半導体 | -11.0% | 1.3倍 | 629.79 | 下 | 95 | 下げ |
| MPWR | 半導体 | -10.8% | 1.4倍 | 1190.16 | 下 | 36 | レンジ |
| NBIS | AIプラットフォーム・クラウド | -10.7% | 1.1倍 | 87.31 | 下 | 2 | 下落相場 |
| LITE | 光・通信・ネットワーク | -10.5% | 0.9倍 | 487.12 | 下 | 12 | 下落相場 |
| FLEX | データセンターの電力・冷却・部品・受託製造・建設 | -10.1% | 1.3倍 | 66.44 | 下 | 7 | 下落相場 |
| CIEN | 光・通信・ネットワーク | -9.6% | 1.0倍 | 239.27 | 下 | 4 | 下落相場 |
| MRVL | 半導体 | -9.1% | 1.1倍 | 131.57 | 下 | 46 | 下げ |
| COHR | 光・通信・ネットワーク | -9.1% | 0.8倍 | 196.24 | 下 | 9 | 下げ |
| AMD | 半導体 | -8.9% | 1.5倍 | 413.27 | 下 | 95 | 下げ |
| TER | 半導体製造装置・材料・設計ソフト・計測 | -8.7% | 1.2倍 | 213.22 | 下 | 5 | 下落相場 |
| ARM | 半導体 | -8.6% | 1.0倍 | 161.56 | 下 | 14 | 下げ |
| KLAC | 半導体製造装置・材料・設計ソフト・計測 | -8.4% | 1.3倍 | 133.65 | 下 | 13 | 下落相場 |
| INTC | 半導体 | -8.1% | 1.0倍 | 54.80 | 下 | 18 | 下げ |
| MCHP | 半導体 | -7.9% | 1.5倍 | 56.36 | 下 | 9 | 下落相場 |
| ON | 半導体 | -7.9% | 1.4倍 | 61.49 | 下 | 16 | 下げ |
| WDC | AIサーバー・ストレージ・メモリ・端末 | -7.8% | 0.8倍 | 273.95 | 下 | 23 | 下落相場 |
| SMCI | AIサーバー・ストレージ・メモリ・端末 | -7.8% | 0.9倍 | 22.62 | 下 | 2 | 下げ |
| STX | AIサーバー・ストレージ・メモリ・端末 | -7.2% | 0.7倍 | 482.48 | 下 | 34 | 下落相場 |
| NRG | データセンターの電力・冷却・部品・受託製造・建設 | -7.0% | 1.1倍 | 90.90 | 下 | 3 | 下げ |
| VRT | データセンターの電力・冷却・部品・受託製造・建設 | -6.7% | 0.9倍 | 173.82 | 下 | 4 | 下落相場 |
| AMAT | 半導体製造装置・材料・設計ソフト・計測 | -6.7% | 1.1倍 | 323.76 | 下 | 16 | 下落相場 |
| NXPI | 半導体 | -6.5% | 1.3倍 | 239.40 | 下 | 54 | レンジ |
| LRCX | 半導体製造装置・材料・設計ソフト・計測 | -6.5% | 1.2倍 | 196.16 | 下 | 10 | 下落相場 |
| JBL | データセンターの電力・冷却・部品・受託製造・建設 | -6.4% | 0.9倍 | 226.69 | 下 | 10 | 下落相場 |
| KEYS | 半導体製造装置・材料・設計ソフト・計測 | -6.0% | 1.1倍 | 272.22 | 下 | 38 | 下げ |
| GLW | 光・通信・ネットワーク | -5.9% | 1.0倍 | 101.87 | 下 | 6 | 下落相場 |
| NVDA | 半導体 | -5.9% | 2.0倍 | 155.38 | 下 | 7 | 下げ |
| ANET | 光・通信・ネットワーク | -5.5% | 1.0倍 | 168.56 | 下 | 66 | 下げ |
| APH | データセンターの電力・冷却・部品・受託製造・建設 | -5.1% | 1.2倍 | 73.47 | 下 | 39 | 下げ |
| ETN | データセンターの電力・冷却・部品・受託製造・建設 | -5.1% | 1.1倍 | 319.27 | 下 | 12 | 下落相場 |
| NTAP | AIサーバー・ストレージ・メモリ・端末 | -5.0% | 0.9倍 | 163.00 | 下 | 86 | 下げ |

- 局面（判定式はClaudeが置いたもの）: **上昇相場**＝終値 > 50日線 > 200日線、50日線が20取引日前より2%以上高い、ADX(14) ≧ 20／**下落相場**＝終値 < 50日線 < 200日線、50日線が20取引日前より2%以上低い、ADX(14) ≧ 20／**上げ**＝それ以外で終値が50日線より上、かつ50日線が10取引日前より上か20日線が5取引日前より上／**下げ**＝それ以外で終値が50日線より下、かつ50日線が10取引日前より下か20日線が5取引日前より下（急な下げの初めは50日線がまだ上向きのため20日線でも見る）／**レンジ**＝どれにも当たらない（2026-11-05 から5つ。それまでは上昇相場とレンジの2つだけで、下げている銘柄もレンジと出ていた）。

## 4-2. 監視外の注目銘柄（S&P500・NASDAQ100のうち監視銘柄に入っていない銘柄）

条件: 流動性（株価5ドル以上・50日平均出来高25万株以上）があり、(a) 前日比+8%以上かつ出来高が50日平均の2倍以上、または (b) 終値が直前1年の最高値（終値）を上回り、RS≧90。RSの高い順に5銘柄（ニュースを調べる）。監視銘柄に入れるかはユーザーが決める。

| 銘柄 | 種類 | 前日比 | 出来高（50日平均の倍） | RS | 終値 |
|---|---|---|---|---|---|
| TGT | 1年の高値更新 | +4.7% | 1.2倍 | 98 | 176.06 |
| BIIB | 1年の高値更新 | +4.8% | 1.1倍 | 96 | 269.11 |
| DLTR | 急騰・1年の高値更新 | +11.2% | 2.7倍 | 96 | 154.65 |
| A | 1年の高値更新 | +4.2% | 1.5倍 | 96 | 183.52 |
| REGN | 1年の高値更新 | +4.8% | 1.1倍 | 95 | 987.09 |

- ほかに5銘柄: BDX（1年の高値更新、RS 95）、LH（1年の高値更新、RS 94）、GILD（1年の高値更新、RS 94）、ABBV（1年の高値更新、RS 93）、DGX（1年の高値更新、RS 91）

## 5. 保有銘柄の手じまい条件（`新分析ツール/保有銘柄.md`）

| 銘柄 | ルール | 買った日 | 買値 | 終値 | 損益 | 損切り価格（買値の15%下、逆指値） | ルールの手じまい条件 | 出来高2倍の大陰線（買った後の直近5日） | 次回決算予定日 |
|---|---|---|---|---|---|---|---|---|---|
| SNDK | ルール外（ユーザーの判断。この日はどのルールの合図もなし） | 2026-10-21 | 171.41（株式分割 1→8 に合わせて直した値。記録は 1371.30） | 77.95 | -54.5% | 145.70 | **損切り価格を下回った**（2026-10-30 の安値 139.40。逆指値なら約定済み。まだ持っていれば次の寄り付きで売る） ルールが不明（保有銘柄.md の「ルール」を確認） | なし | 2027-02-15 |
| AMD | ボリンジャーIII | 2026-10-21 | 549.97 | 413.27 | -24.9% | 467.47 | **損切り価格を下回った**（2026-11-02 の安値 466.07。逆指値なら約定済み。まだ持っていれば次の寄り付きで売る） **成立（出来高2倍の大陰線が 2026-11-05 に出た → まだ持っていれば次の寄り付きで全部売る）** 売りの指値: 上部バンド 599.54（今夜この値に置き直す。届いた日に売れる）（2倍ETF AMUU で持っている場合も、判定は元の株 AMD の値段） | なし | 2027-02-02 |

- 出来高2倍の大陰線: 実体（始値−終値）が前日までのATR(14)の1.5倍以上、終値がその日の値幅の下25%以内、出来高が前日までの50日平均の2倍以上の日。**押し目（ボリンジャーIII）・急落の底の保有では売りのルール**: 出たら翌日の寄り付きで全部売り、空いた枠で次の合図を買う（2026-10-02 ユーザー決定。`バックテスト結果/やり直し_売りの合図の組み合わせ.md`。乱数3組とも年率が約+2ポイント、最大下落率もやや下がった）。ミネルヴィニ・新高値V2の保有では事実の表示（順張りに足しても良くならなかった）。

- 半分売りの合図（ミネルヴィニ・新高値V2の保有だけ）: 反転のローソク足（かぶせ線・弱気の包み足・宵の明星・流れ星）＋出来高が50日平均の1.5倍以上＋RSI(14)が前日か当日に70以上。買った後に最初に出た日の翌日の寄り付きで半分売り、残り半分は50日線割れ・損切り15%まで持つ（2026-10-01 ユーザー決定。`バックテスト結果/半分だけ売るとオニールの空き枠.md`）。

- かぶせ線（ミネルヴィニ・新高値V2の保有だけ）: 上昇中の陽線の翌日に、前日の高値より上で寄り付き、前日の陽線の真ん中より下（前日の始値より上）で引けた日。翌日の寄り付きで全部売り、空いた枠で次の合図を買う。半分売りより優先する（2026-10-01 ユーザー決定。`バックテスト結果/2倍ETFで売って買い直す.md`。順張りの売買の25%で出て、1回平均+2.0%、年率 21.4%→26.4%）。

## 5-2. 前日（2026-11-23の引け）の【買い（予約）】の確認

前日の【買い（予約）】はなし。

## 6. 候補（採用したルールの条件が成立＝A。予約（B）は2026-10-25から注文せず、節6-3に参考の表示だけ）

建玉の目安: 同時保有4銘柄まで、1銘柄に資金の25%（資金÷4）、損切りは買値の15%下（ユーザー決定 2026-09-29）。

保有中のため候補から外した銘柄（合図は出ている）: SNDK

**急落の底の指値に届いた銘柄（注文していれば約定。保有銘柄.md に買った日・値段を記録する。今日の候補には出さない）**: HPE（2026-11-20の合図、指値 40.09、2026-11-24の安値 39.42）

パターン: A＝最新の足で採用ルールの条件が成立（押し目・ミネルヴィニ・新高値V2は翌日の寄り付きで成行、急落の底は合図の日の終値の2%下に指値で3取引日待つ。2026-11-03 ユーザー採用）。条件の成立が目前の銘柄（B）は、予約の注文をやめたので節6-3に参考として出す（2026-10-25 ユーザー決定）。

| 銘柄 | グループ | パターン | 種類 | ルールの過去の成績 | 終値 | 前日比 | RS | 50日線の傾き | 局面 | 当てはまった条件 | 次回決算予定日 | 注文の目安 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ANET | 光・通信・ネットワーク | A | 逆張り: 急落の底（担当: コナーズ）（指値の3日目） | 2位（勝率65%・1回平均+2.1%） | 168.56 | -5.5% | 66 | -2.2% | 下げ | 2026-11-20の合図: 直前5日の最高値（終値）から-15.0%下落（−15%以上）、RSI(2)=7.9（≦10）、急落の前は50日線＞200日線。市場全体の局面: S&P500 横ばい／NASDAQ100 横ばい。その後まだ指値に届かず、終値は5日線以下 | 2027-02-09（77日後） | 指値買い 164.27（合図の日 2026-11-20 の終値 167.62 の2%下。今日が最後の日。届かなければ見送り、途中で終値が5日線を上回ったら取り消す）。損切り: 約定した値段の15%下。手じまい: 終値が5日線（今日 179.60）を上回った翌日の寄り付き（コナーズ）。**株数の目安: 14株**（2,384ドル÷164.27。注文の価格）、購入金額 約2,300ドル |
| NBIS | AIプラットフォーム・クラウド | A | 逆張り: 急落の底（担当: コナーズ）（指値の3日目） | 2位（勝率65%・1回平均+2.1%） | 87.31 | -10.7% | 2 | -17.2% | 下落相場 | 2026-11-20の合図: 直前5日の最高値（終値）から-29.8%下落（−15%以上）、RSI(2)=1.9（≦10）、急落の前は50日線＞200日線。市場全体の局面: S&P500 横ばい／NASDAQ100 横ばい。その後まだ指値に届かず、終値は5日線以下 | 2027-02-11（79日後） | 指値買い 79.68（合図の日 2026-11-20 の終値 81.31 の2%下。今日が最後の日。届かなければ見送り、途中で終値が5日線を上回ったら取り消す）。損切り: 約定した値段の15%下。手じまい: 終値が5日線（今日 94.06）を上回った翌日の寄り付き（コナーズ）。**元の株で買う**（2倍ETF NBIL のある銘柄だが、S&P500が20週線で「横ばい」の局面のため。案1）。**株数の目安: 29株**（2,384ドル÷79.68。注文の価格）、購入金額 約2,311ドル |
| DLTR | テーマの外（Discount Stores） | A | 順張り: 新高値（V2、担当: ミネルヴィニ） | 1位（勝率45%・1回平均+2.1%） | 154.65 | +11.2% | 96 | +3.8% | 上昇相場 | テーマの外の強い銘柄のRS上位10以内（6位）、トレンドテンプレート8条件、RS 96（≧90）、終値が直前20日の最高値（終値）147.00を上回る、上げ下げの出来高比（50日）1.62（≧1.3）、終値が直前2年の最高値148.54以上（上値のレジスタンスなし） | 2026-11-24（0日後）**決算が近い** | 翌日の寄り付きで買い。損切り: 買値の15%下。手じまい: 引けで50日線を割った翌日の寄り付き。**株数の目安: 15株**（2,384ドル÷154.65。今日の終値。寄り付きの値段で変わる）、購入金額 約2,320ドル |

- 局面（判定式はClaudeが置いたもの）: **上昇相場**＝終値 > 50日線 > 200日線、50日線が20取引日前より2%以上高い、ADX(14) ≧ 20／**下落相場**＝終値 < 50日線 < 200日線、50日線が20取引日前より2%以上低い、ADX(14) ≧ 20／**上げ**＝それ以外で終値が50日線より上、かつ50日線が10取引日前より上か20日線が5取引日前より上／**下げ**＝それ以外で終値が50日線より下、かつ50日線が10取引日前より下か20日線が5取引日前より下（急な下げの初めは50日線がまだ上向きのため20日線でも見る）／**レンジ**＝どれにも当たらない（2026-11-05 から5つ。それまでは上昇相場とレンジの2つだけで、下げている銘柄もレンジと出ていた）。

- 2倍ETF: 2倍ETFがある銘柄（ユーザーがムームー証券で買えることを確認した38銘柄のうち、目減りが年15%未満のもの）は、株の代わりに2倍ETFを買う（2026-10-04 ユーザー決定。`バックテスト結果/2倍ETFを使う決まり.md`。年率 約27%→約33%、確定した損益だけの最大下落率 約30%→約31%、含み損込みは約33%→約45%）。買う金額は株と同じ（資金の25%）。合図・損切り（元の株の買値の15%下＝ETFでは約30%下）・手じまいはすべて元の株の値段で判定する。指値・逆指値はETFの値段に直して置く。どのETFかは `新分析ツール/2倍ETFの対応表.json`（売買代金が1日500万ドル以上で、直近1年の目減りが一番小さいもの）。**2倍ETFで買うのは、S&P500が20週線（100日線）で「上昇」の局面のときだけ。横ばい・下落の局面では元の株で買う**（案1、2026-10-13 ユーザー採用。買う日に決め、買った後は局面が変わってもそのまま持つ。`バックテスト結果/流れ（市場の局面）を使う形.md`）。

- ルールの過去の成績: 今の売りのルールで、後知恵なしの監視銘柄・2015年〜の全部の合図の1回ごとの成績（2026-10-02計算、`新分析ツール/バックテスト結果/ルールごとの成績.md`）。順位は1回平均（1回の売買で平均いくら増えるか）の順。表はパターン（A→B）ごとに、この順位の良い順に並べた（表示の順番だけ。買う順番・件数の上限は変えていない。候補の選び方を変えても成績は変わらなかったため。2026-10-02 ユーザーの指示）。著者には渡さない。

- 悪いニュースが続いているグループ（半導体）の候補（記録だけ。売買のルールは変えない。著者には渡さない）: なし

- 候補の数: 空き枠4（同時保有4銘柄まで。保有2、うち今日ルールの売りが成立2）＋予備2件まで表に出した（2026-10-25 ユーザー決定）。省いた候補はない。

- テーマの外の候補（グループが「テーマの外」）: 監視銘柄の候補で枠が埋まらないときに使う（監視銘柄の候補を先に買う）。S&P500の今の構成銘柄のうち監視銘柄でない銘柄から、RS≧90・30週線が上向きで終値がその上・業種の3カ月の強さが上位20%の21銘柄を調べ、空き枠2つ分まで出した。バックテストでは、テーマの外の強い銘柄で空き枠を埋めると、テーマが弱い時期の成績が支えられた（`バックテスト結果/半導体・AIに特化した場合.md`。2026-10-01 ユーザー決定）。

- RS≧80の押し目（ボリンジャーIII）は、バックテストで成績がより安定していた（PF3.27、最大下落20%）。

## 6-3. 参考: 条件の成立が目前の銘柄（予約は注文しない・著者には送らない）

2026-10-25 ユーザー決定: 予約（逆指値・指値）の注文はやめ、参考の表示だけにする。毎朝のツールと同じ条件・値段で予約の約定をバックテストに入れると、どの形も年率が下がった（後知恵なし 35.7%→30.7〜34.2%、87銘柄 45.6%→34.2〜42.6%。`バックテスト結果/点検_2026-10-25/`）。引けで条件がそろえば、翌朝の節6に買いの候補（A）として出る。各ルールでRSの高い順に2件まで。

| 参考の銘柄 | グループ | 種類 | 終値 | 前日比 | RS | 当てはまった条件 | 条件がそろう目安の価格（注文はしない） |
|---|---|---|---|---|---|---|---|
| SNPS | 半導体製造装置・材料・設計ソフト・計測 | ボリンジャー メソッドIII（%bが0.05未満に近い） | 414.82 | -2.9% | 30 | %b=0.100（0.05まであと少し）、21日II%=+0.013（>0） | 410.37（この値より下で引けると翌朝の買いの候補（A）。目安） |
| CDNS | 半導体製造装置・材料・設計ソフト・計測 | ボリンジャー メソッドIII（%bが0.05未満に近い） | 296.60 | -2.5% | 21 | %b=0.138（0.05まであと少し）、21日II%=+0.024（>0） | 291.01（この値より下で引けると翌朝の買いの候補（A）。目安） |


# ニュース（サブエージェントの調査）

# ニュース調査（2026-11-24引け。主に headlines.md の見出し。本文未確認のものが多い）

## テーマ全体の下げの原因
確かめた手段: headlines.md の見出し。WebSearch（Nvidia・Micron格下げ・ADI決算）は同日記事がヒットせず取得不可。
- きっかけ候補: Nvidiaが前日の上げの後に-7%（Benzinga 11/24）、Anthropicが上場価格割れ（Benzinga・株探 11/24）。Nasdaq・S&P500は反落、Dowは+423ドル（Reuters・Kiplinger・時事 11/24）。
- 広がった先: メモリ（MicronがBNP Paribas格下げで-11%、재경일보・marketscreener 11/24）、アナログ半導体（ADI -17%「2020年以来最悪」Barron's 11/24、決算 Tops Views/Mixed Outlook IBD 11/24）、ネオクラウド（IREN -15%、CoreWeave -14%、24/7 Wall St. 11/24）。
- 信用: CNBC 11/24「AI debt markets shudder as Nvidia's top "banker" returns」、MarketWatch 11/24「AI debt market isn't convinced the worst is over」。社債利回り・CDS・VIX・ハイイールド債の数値は取得不可。
- 呼び名: 「〇〇ショック」に当たる日本語の報道なし。IBD 11/24「Data Center Spending Fears Return」。
- 指標: IBD 11/24 Fed関連のインフレ指標が控える。Benzinga 11/24 Bessentがイラン関連の制裁を発表。

## 引け後・時間外の材料
- WDAY: 時間外 -6.8%。Q3決算は強いが株は下落（Benzinga 11/24）。
- ADSK: 時間外 -3.1%。Q3決算は予想超えだが約4%下落（Investing.com 11/24）。
- DELL: 時間外 +2.9%。Q3は予想超え・見通しも予想超え（IBD・Business Wire 11/24）。HPE: 売上+50%・見通し引き上げだが通常取引で-16%、見通しは最も強気な予想に届かず（Bloomberg・Yahoo 11/24）。
- 保有・候補（AMD +1.1%、NBIS +0.8%、DLTR -0.5%、SNDK +0.2%、ANET -0.2%）は±5%未満で、原因の見出しは見つからなかった。
- 買収: CrowdStrikeがZscalerを439億ドルの全株式で買収（Industrial Cyber 11/24）。

## AMD（保有）
- 11/19 Hunterbrook Capitalが空売りを開示。AMDのファームウェアが米国のブラックリスト入りの中国サーバー企業IEITに渡っていると指摘。AMDは輸出規制を順守と反論（Motley Fool・IBTimes 11/19）。レポートは販売の証拠ではないと断っている。
- 11/24 -8.9%: GuruFocus「Hunterbrook Short Report Hits Shares」、Yahoo「Nvidia, AMD, Broadcom lead chip stocks lower」（11/24）。
- 次回決算: Yahoo表示 2027-02-02（公式発表は取得不可）。
- 悪材料: あり（上記の空売りレポート。AMDは否定）。

## ANET（候補）
- 11/20 Arista -12%、テックとAI株の売り（Seeking Alpha 11/20）。11/24 BNP Paribasが目標株価を290→260ドル（MT Newswires）。
- 次回決算: Yahoo表示 2027-02-09（推定。公式は取得不可）。
- 悪材料: 確認できず。

## NBIS（候補）
- 11/20 Burryがネオクラウド下落に言及、NBIS -7%（Yahoo Finance 11/20）。11/24 ネオクラウド全体が月曜の上げを戻して下落（24/7 Wall St.）。個社の本文は未確認。
- 次回決算: Yahoo表示 2027-02-11（公式は取得不可）。
- 悪材料: 個社固有は確認できず。

## DLTR（候補・監視外の注目）
- 11/24 Q3決算が予想超えで通期見通しを引き上げ（Investing.com・Startup Fortune 11/24）。決算数値の詳細は取得不可。Five Below・Target・Ollie'sも連れ高（GuruFocus 11/24）。
- 悪材料: 確認できず。

## SNDK（保有）
- 11/24 -17.4%。Yahoo「Why Sandisk Stock Plunged Today」「Plunges 44% in a Month」（本文未確認）。同日Micronが格下げで-10〜11%（24/7 Wall St. 11/24）。
- 悪材料: 個社固有は確認できず。

## 監視外の注目銘柄
- TGT: DLTR決算を受けた同業高（GuruFocus 11/24）。A: 引け後に初の20億ドル四半期、時間外+6〜7%（株探・Startup Fortune 11/24）。BIIB・REGN: 原因の見出しは見つからなかった（市場はヘルスケア株に買い、時事 11/24）。

## テーマ全体のニュース（直近1週間）
- Applied Optoelectronicsが22億ドルのハイパースケーラー向け供給契約（24/7 Wall St. 11/24）。輸出規制・設備投資計画の新規見出しは取得不可。

# ニュースの見出し（プログラムが自動で取得）

- Googleニュース（日付を指定）とYahooファイナンスの見出しを `tools/news_headlines.py` が自動で並べたもの。日付は米国東部時間の配信日（引け後の記事は翌日付）。原因の判断・売買の判断はしていない。
- 調べた銘柄の選び方: ①保有 ②今日の候補 ③時間外に±5%以上動いた監視銘柄 は全部、④引けまでに大きく動いた銘柄（1週で±5%のグループの上位3・1日で±7%）は合計12銘柄まで。
- 1週で−5%以下のグループ: 半導体（-9.6%）、光・通信・ネットワーク（-6.1%）、AIサーバー・ストレージ・メモリ・端末（-5.8%）
- 1週で+5%以上のグループ: なし

## 0. 時間外（引け後）の値動き（2026-11-24 の引けから、Yahoo。±3%以上の監視銘柄と、保有・候補は全部）

| 銘柄 | 区分 | 引け | 時間外 | 騰落率 |
|---|---|---|---|---|
| WDAY | 監視 | 179.12 | 167.00（17:16 ET） | **-6.8%** |
| ADSK | 監視 | 255.43 | 247.44（16:56 ET） | -3.1% |
| AMD | 保有 | 413.24 | 417.90（17:17 ET） | +1.1% |
| NBIS | 候補 | 87.30 | 87.98（17:18 ET） | +0.8% |
| DLTR | 候補 | 154.66 | 153.83（16:55 ET） | -0.5% |
| SNDK | 保有 | 77.90 | 78.09（17:18 ET） | +0.2% |
| ANET | 候補 | 168.60 | 168.30（16:45 ET） | -0.2% |

## 1. 市場全体（2026-11-24）

### 市場全体（英語のまとめ記事）
検索語: `stocks Wall Street close Nasdaq`
- 11/24 Reuters | Nasdaq, S&P 500 end lower following Monday's Nvidia-fueled rally
- 11/24 Kiplinger | Dow Brushes Off Tech Rout, Tariff Worries to Add 423 Points: Stock Market Today
- 11/24 Eurasia Business News | Stock Market Today, November 24, 2026: Nasdaq Falls as Nvidia and Anthropic Slide, Oil price at $89, Gold Drops to $3,620
- 11/24 24/7 Wall St. | Stock Market Today: Jensen’s Return to Nvidia Is Causing Index Indigestion
- 11/24 Benzinga | Stock Market Today: Dow Jones, S&P 500, Nasdaq 100 Futures Fall After Scott Bessent Unveils Fresh Iran Sa

### 市場全体（Stock Market Today）
検索語: `"stock market today"`
- 11/24 Benzinga | Anthropic Drops Below IPO Prices, Nvidia Sinks 7% After Record Rally: Stock Market Today
- 11/24 The Motley Fool | Stock Market Today, Nov. 24: Nvidia Gives Back $240 Billion in Market Value Despite Wall Street Upgrade Signaling 29% Upside

### 市場全体（日本語のまとめ記事）
検索語: `米国株式市場 OR NY株`
- 11/24 Reuters | 米国株式市場＝ナスダック・Ｓ＆Ｐ反落、エヌビディア主導の上昇一服
- 11/24 Yahoo!ニュース | 米国株式市場＝ナスダック・Ｓ＆Ｐ反落、エヌビディア主導の上昇一服（ロイター）
- 11/24 京都新聞デジタル | ＮＹ株４２３ドル高、５万ドル台回復
- 11/24 時事通信ニュース | ＮＹ株続伸、４２３ドル高＝ヘルスケア株に買い

### 半導体・AI株（英語）
検索語: `chip stocks OR semiconductor stocks OR AI stocks`
- 11/24 Yahoo Finance | Nvidia, AMD, Broadcom lead chip stocks lower as AI trade comes under pressure
- 11/24 Investor's Business Daily | Nvidia, Chip Stocks Fall As Data Center Spending Fears Return
- 11/24 Seeking Alpha | AI and chip stocks pull back sharply following Nvidia-driven rally (NVDA:NASDAQ)
- 11/24 Centre Daily Times | Wall St futures dip as chip stocks cool after Nvidia-fueled rally

### 信用（社債・借金）
検索語: `AI debt OR bonds OR credit spreads OR CDS`
- 11/24 CNBC | AI debt markets shudder as Nvidia's top "banker" returns
- 11/24 Forbes | What The Bond Market Says Investors Should Do During The Stock Market Correction
- 11/24 MarketWatch | The AI debt market isn’t convinced the worst is over for investors
- 11/24 Yahoo Finance | AI market whipsaw puts Kevin Warsh's rate-hike strategy to the test
- 11/24 The Dark Side Of The Boom | Risk Appetite Collapses: Wall Street's 2027 Outlook — The Bull Market Needs a Different Playbook

### 「〇〇ショック」の呼び名（日本語）
検索語: `ショック 株`
- 11/24 ダイヤモンド・オンライン | 【情報・通信27社】倒産危険度ランキング2027最新版！22位フジ・メディアHD、11位「株探」運営会社、1位は？
- 11/24 四季報オンライン | 任天堂だけじゃない！これが注目のIP関連の17銘柄だ
- 11/24 山陽新聞 | 資産7億円の桐谷さん、保有株を紹介「凄い総合利回りです」
- 11/24 Yahoo!ファイナンス | インデックスファンドSOX指数(米国上場半導体株式)【02313239】：基準価格・投資信託情報
- 11/24 文化放送 | エヌビディアCEO復帰でも残る安全保障リスクとAI業界の信用不安

### 引け後・時間外の動き（英語）
検索語: `"after hours" OR "after the bell" OR "extended trading" stocks`
- 11/24 Yahoo Finance | HPE Stock Falls 7% After Hours Despite 50% Revenue Growth and a Raised Outlook
- 11/24 Investing.com | HP stock reverses course after hours despite quarterly results beat, dividend bump
- 11/24 Startup Fortune | Agilent posts its first $2 billion quarter and the stock jumps after hours
- 11/24 Benzinga | Alta Equipment Group Stock Climbs 15.84% After-Hours: What's Going On?
- 11/24 Investing.com | HPE delivers quarterly results beat, raises guidance; stock falls after big rally
- 11/24 Benzinga | Fluence Energy (FLNC) Stock Jumps Over 17% After Hours: What's Going On?
- 11/24 FourWeekMBA | Agilent Sales Rise 9.6% to $2.04B; Stock Up 7% After Hours

### 引け後・時間外の動き（日本語）
検索語: `時間外 決算 株`
- 11/24 Yahoo!ファイナンス | ＨＰ、決算受け時間外で上昇 コスト増への対応力改善を示唆＝米国株個別(株探ニュース)
- 11/24 株探 | アジレント、決算受け時間外で６％高＝米国株個別
- 11/24 Investing.com - FX | 株式市場 | ファイナンス | 金融ニュース | オートデスク株、第3四半期決算がコンセンサス超えも時間外取引で約4%下落
- 11/24 BigGo ファイナンス | 米ディックス・スポーティング・グッズ、通期見通しを引き上げ フットロッカーの既存店売上がプラス転換で株価17%急騰
- 11/24 Yahoo!ファイナンス | セムテック、好決算も時間外で１０％安＝米国株個別(株探ニュース)
- 11/24 Investing.com - FX | 株式市場 | ファイナンス | 金融ニュース | HPが時間外取引で急騰、四半期決算が予想を上回る
- 11/24 株探 | ダウ先物が反落 上げ維持できず アンソロピックがＩＰＯ価格割れ＝米国株
- 11/24 BigGo ファイナンス | 米フルエンス・エナジー、過去最高の89億ドル受注残と第4四半期決算を受け株価急騰

### 買収・合併（英語）
検索語: `acquisition OR acquire OR merger OR takeover chip OR semiconductor OR AI OR optical`
- 11/24 TechCrunch | Amazon’s Decart acquisition is a bet on using software to narrow the silicon gap with Nvidia
- 11/24 Barron's | Tesla-SpaceX Merger: The AI Logic, Valuation Math, and Risks
- 11/24 Industrial Cyber | CrowdStrike to acquire Zscaler in $43.9 billion all-stock deal to expand Zero Trust security and AI protection
- 11/24 The American Bazaar | Amazon’s Decart acquisition aims to narrow AI chip gap with Nvidia
- 11/24 The Media Line | Amazon To Acquire Israeli AI Startup Decart’s Technology in Deal Valued at $7.5 Billion
- 11/24 Yahoo Finance | Amazon to acquire Decart’s AI optimisation technology
- 11/24 citybiz | Automation Anywhere Completes Boost.ai Acquisition, Expanding Enterprise Customer Service Automation
- 11/24 Dealroom | FrenchFry, Tavia set $500M SPAC merger to build AI holding company

## 2. 保有・候補・時間外で大きく動いた銘柄（2026-11-18〜2026-11-24 の見出し）

### SNDK（Sandisk Corporation、保有、AIサーバー・ストレージ・メモリ・端末、前日比 -17.4%、1週 -29.5%、時間外 +0.2%）

#### Googleニュース
検索語: `Sandisk stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/19 Yahoo Finance | Why Sandisk Stock Finally Popped Today
- 11/20 Investing.com | Why is SanDisk stock sliding today?
- 11/24 Yahoo Finance | Why Sandisk Stock Plunged Today
- 11/24 Yahoo Finance | Sandisk Plunges 44% in a Month: Buy, Sell or Hold the Stock?

#### Yahooファイナンス
検索語: `SNDK`
- 11/24 24/7 Wall St. | Micron Just Hit a $700 Ceiling, Caught a Downgrade, and Is Down 10% Today. Is MU a Toxic Stock or a Prime Bargain?
- 11/24 Barrons.com | AI Stocks Are Getting Clobbered
- 11/24 GuruFocus.com | Nvidia, AMD and Micron Lead AI Selloff as Chip Stocks Slide

### AMD（Advanced Micro Devices, Inc.、保有、半導体、前日比 -8.9%、1週 -17.9%、時間外 +1.1%）

#### Googleニュース
検索語: `Advanced Micro Devices stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/18 Yahoo Finance | Why Is Advanced Micro Devices Stock Rising Today?
- 11/19 CNBC | AMD dives on short seller report of alleged China exposure
- 11/19 Bloomberg.com | AMD Shares Slump After Shortseller Raises China Concerns
- 11/20 Forbes | Nvidia Rival AMD’s Stock Slides Sharply In Premarket After Report Alleges China Ties

#### Yahooファイナンス
検索語: `AMD`
- 11/24 GuruFocus.com | Why MaxLinear (MXL) Stock Is Plunging Today: Chip Stocks Sell Off
- 11/24 GuruFocus.com | nVent Electric (NVT) Stock Is Down 8.4% Today: AI Chip Selloff Drags Power Peers
- 11/24 Investor's Business Daily | Dow Jones Futures: Nvidia, Anthropic Lead AI Retreat But Many Sectors Strong; Fed Inflation Data Due

### ANET（Arista Networks, Inc.、候補、光・通信・ネットワーク、前日比 -5.5%、1週 -9.6%、時間外 -0.2%）

#### Googleニュース
検索語: `Arista Networks stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/20 Benzinga | Why Is Arista Networks Stock Plunging Friday?
- 11/20 Traders Union | Arista Networks stock falls amid weak momentum and downward price move
- 11/20 Seeking Alpha | Arista Networks sinks 12% amid tech and AI selloff (ANET:NYSE)
- 11/23 Trefis | What Moved Arista Networks Stock?

#### Yahooファイナンス
検索語: `ANET`
- 11/23 Trefis | Own HP Stock? Memory Costs Are The Risk
- 11/24 MT Newswires | BNP Paribas Adjusts Price Target on Arista Networks to $260 From $290
- 11/24 TIKR | Could Meta Actually Climb 30%? Or Is J.P. Morgan Totally Wrong?

### NBIS（Nebius Group N.V.、候補、AIプラットフォーム・クラウド、前日比 -10.7%、1週 -17.7%、時間外 +0.8%）

#### Googleニュース
検索語: `Nebius stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/20 Yahoo Finance | Nebius Drops 7% as Michael Burry Takes a Victory Lap on Neocloud Rout; IREN Falls 5%, Oracle Slides 4%
- 11/20 StreetInsider | Nebius stock drops as Anthropic rally fades
- 11/24 Benzinga | Why Is Nebius Stock Falling on Tuesday?
- 11/24 Investing.com | Why is Nebius stock sliding today?

#### Yahooファイナンス
検索語: `NBIS`
- 11/24 24/7 Wall St. | Anthropic Tumbles 9%, Trades Below IPO Price Despite Canaccord’s $135 Target; CoreWeave and Nebius Drop 8%
- 11/24 24/7 Wall St. | IREN Sinks 15%, CoreWeave Tumbles 14% as Neocloud Stocks Backtrack Monday’s Rally; Nebius Drops 13%
- 11/24 MT Newswires | Sector Update: Tech Stocks Fall Tuesday Afternoon

### DLTR（Dollar Tree, Inc.、候補、時間外 -0.5%）

#### Googleニュース
検索語: `Dollar Tree stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/24 Yahoo Finance | Why Dollar Tree Stock Popped Today
- 11/24 Investing.com | Dollar Tree stock jumps on earnings beat and raised outlook
- 11/24 Barron's | Dollar Tree Is Today’s Best S&P 500 Stock. It’s Ready for a Holiday Run.
- 11/24 Startup Fortune | Dollar Tree stock jumps after Q3 beat and a raised 2026 profit outlook

#### Yahooファイナンス
検索語: `DLTR`
- 11/24 GuruFocus.com | Why Five Below (FIVE) Stock Is Up Today: Strong Retail Earnings Lift Peers
- 11/24 GuruFocus.com | Why Is Target (TGT) Stock Up Today? Dollar Tree's Strong Q3 Lifts Discount Retailers
- 11/24 GuruFocus.com | Why Ollie's (OLLI) Stock Is Up Today: Dollar Tree Earnings Boost Discounters

### WDAY（Workday, Inc.、AIソフト・セキュリティ・ITサービス、前日比 +1.8%、1週 -2.0%、時間外 -6.8%）

#### Googleニュース
検索語: `Workday stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/18 Trefis | What Just Happened To Workday Stock?
- 11/18 Traders Union | Workday stock falls 5.6% after intent to acquire Honeydew
- 11/19 Yahoo Finance | Workday (WDAY) Expands Payroll Reach, Is The Stock Now Cheap?
- 11/24 Benzinga | Workday Stock Slides Despite Strong Q3 Results: Details

#### Yahooファイナンス
検索語: `WDAY`
- 11/24 GlobeNewswire | Global Career Development Software Market 2026: Size, Trends, and Forecast to 2030 | Capitalize on AI, Cloud, and Internal Mobility with Oracle, SAP, Workday, and Eightfold AI
- 11/24 GlobeNewswire | Global Succession Planning and Management Software Market Report 2026 | Capitalize on AI and Cloud Growth to $8.64B by 2030 with Oracle, SAP, Workday, Paycom, and Eightfold AI
- 11/24 GlobeNewswire | Motivosity Joins the Workday Partner Program, Tying Recognition to Performance Outcomes

## 3. 引けまでに大きく下げた銘柄（2026-11-18〜2026-11-24 の見出し）

### ADI（Analog Devices, Inc.、半導体、前日比 -17.4%、1週 -18.4%、時間外 +0.2%）

#### Googleニュース
検索語: `Analog Devices stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/24 Yahoo Finance | Why Is Analog Devices Stock Falling 7.6% Today?
- 11/24 Barron's | Why Analog Devices Stock Is Taking Its Worst Beating Since 2020
- 11/24 Benzinga | Analog Devices Stock Plunges Nearly 17%: What's Going On?
- 11/24 Investor's Business Daily | Analog Devices Tops Fiscal Q4 Views, Gives Mixed Outlook

#### Yahooファイナンス
検索語: `ADI`
- 11/24 GuruFocus.com | Why Is Vishay (VSH) Stock Down Today? Chip Selloff Drags Semiconductors
- 11/24 Investing.com | Analog Devices earnings analysis: questions answered and next catalysts

### TXN（Texas Instruments Incorporated、半導体、前日比 -11.2%、1週 -12.6%、時間外 +0.5%）

#### Googleニュース
検索語: `Texas Instruments stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/19 Trefis | Is Texas Instruments’ Sales Boom Its Biggest Risk?
- 11/20 Yahoo Finance | Texas Instruments (TXN) Up 2.2% Since Last Earnings Report: Can It Continue?
- 11/23 TradingView | Why Texas Instruments stock is trading up today
- 11/24 Investing.com | Why is Texas Instruments stock sliding today?

#### Yahooファイナンス
検索語: `TXN`
- 11/24 GuruFocus.com | Texas Instruments (TXN) Stock Is Down 8.1% Today: Chip Sector Sell-Off
- 11/24 GuruFocus.com | Why Is AMD (AMD) Stock Down Today? Hunterbrook Short Report Hits Shares
- 11/24 GuruFocus.com | Why Is CEVA (CEVA) Stock Down Today? AI Chip Selloff Drags Shares

### LITE（Lumentum Holdings Inc.、光・通信・ネットワーク、前日比 -10.5%、1週 -13.0%、時間外 +0.7%）

#### Googleニュース
検索語: `Lumentum stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/18 Yahoo Finance | Lumentum Is Down 33% in a Month as Marvell’s Slide Shrinks Its Buyout Value. Can LITE Stock Get Back to Bernstein’s $700 Target?
- 11/20 24/7 Wall St. | Applied Optoelectronics Sinks 7% as Optics Stocks Reverse Thursday's Rally; Coherent Declines 4%, Lumentum Slides 5%
- 11/24 Yahoo Finance | Lumentum (LITE) Stock Looks Richly Priced As Its Three Year Run Continues
- 11/24 Investing.com | Why is Lumentum stock sliding today?

#### Yahooファイナンス
検索語: `LITE`
- 11/24 24/7 Wall St. | Applied Optoelectronics Climbs 5% on $2.2 Billion Hyperscaler Supply Deal; Lumentum and Coherent Drop 6%
- 11/24 24/7 Wall St. | Wall Street May Not Be Ready for What’s Coming Next for This Little-Known AI Stock
- 11/24 Barrons.com | Megadeals Are Back. Why More Takeovers Could Be Coming.

### CIEN（Ciena Corporation、光・通信・ネットワーク、前日比 -9.6%、1週 -9.6%、時間外 -0.1%）

#### Googleニュース
検索語: `Ciena stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/20 Seeking Alpha | Ciena slides 9% amid broad tech weakness (CIEN:NYSE)
- 11/20 AlphaStreet | Ciena Drops 8.6% Amid Sector-Wide Selling
- 11/20 Global Banking & Finance Review | Ciena falls 10.76% in Friday's session
- 11/20 TradingView | Arista Networks, Ciena, Nokia, Applied Digital, and CoreWeave shares are falling, what you need to know

#### Yahooファイナンス
検索語: `CIEN`
- 11/20 TIKR | An $11 Billion Fund Just Bought These 3 Stocks
- 11/21 TIKR | A $10 Billion Fund Bought These 3 Stocks Last Quarter
- 11/22 Insider Monkey | Missed the First AI Rally? 5 Oversold Stocks With 50%+ Upside Potential

### HPE（Hewlett Packard Enterprise Company、AIサーバー・ストレージ・メモリ・端末、前日比 -16.3%、1週 -12.8%、時間外 -0.2%）

#### Googleニュース
検索語: `Hewlett Packard Enterprise stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/18 Yahoo Finance | Why Is Hewlett Packard Enterprise Stock Rising Today?
- 11/23 SiliconANGLE | HPE’s stock slides despite record revenue growth and upbeat forecast
- 11/24 Bloomberg.com | HPE Gives Outlook That Falls Short of the Most Optimistic Estimates
- 11/24 Barron's | HPE Stock Drops After Earnings Beat. Here’s Why.

#### Yahooファイナンス
検索語: `HPE`
- 11/24 24/7 Wall St. | Super Micro Just Fell 32% in a Month: Is SMCI an Unbeatable Bargain or a Toxic Stock?
- 11/24 Insider Monkey | Is HPE One of the Morgan Stanley’s 8 Best Semiconductor and Server Stocks to Buy for 2027?
- 11/24 Investor's Business Daily | Dell Technologies Smashes Q3 Estimates, Guides Above Views

### DELL（Dell Technologies Inc.、AIサーバー・ストレージ・メモリ・端末、前日比 -11.8%、1週 -8.5%、時間外 +2.9%）

#### Googleニュース
検索語: `Dell stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/20 Benzinga | Why Is Dell Stock Falling on Friday?
- 11/20 24/7 Wall St. | Dell Stock Plunges 10% in the AI Selloff and Heads for Its Worst Month Since Its 2018 Return to the Stock Market. Earnings Are Tuesday
- 11/24 Yahoo Finance | Why Is Dell Technologies Stock Falling 5.9% Today?

#### Yahooファイナンス
検索語: `DELL`
- 11/24 Business Wire | Dell Technologies Delivers Third Quarter Fiscal 2027 Financial Results
- 11/24 Investing.com | Dell, HP, Autodesk and Workday earnings: what to watch today
