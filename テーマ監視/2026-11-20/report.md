# テーマ監視 2026-11-19

# 判定のまとめ（ルールの判定と著者の判定を分けて表示）

- **ルールの判定**: 採用した売買ルール（スクリプト）が数値で決めたもの。損切りは買値の15%下の逆指値（日中に届けばその場で売れる）。
- **著者の判定**: ノートブックの著者の回答。買いは注文を止める理由があるときだけ【様子見】、保有はルールより早く手じまう理由があるときだけ【売り】。根拠は下の「著者の回答（全文）」。
- 2つが食い違うときに、どちらに従うかはユーザーが決める。

- **テーマ全体の急落（S2・記録だけ）: あり（S2）**（SOXが直近60取引日の最高値から -28.7%）。S2の日の順張りの候補には「S2なら見送る形」と付ける（売買のルールは変えない。記録してから採用を決める。2026-10-14）

- **特殊な下げ（記録だけ）: あり（特殊な下げ）**（2026-10-16から）（SOXが直近60取引日の最高値から -28.7%、前の1年の大きな上げ・雇用の弱さ・物価の再加速のうち 2つ）。1995年〜では、この形の後にSOXの下げが長引くことが多かった（後知恵を含む）。売買のルールは変えない（2026-11-03）

## 保有銘柄

| 銘柄 | ルール | 損益 | 時間外 | ルールの判定 | ルールの判定の理由 | 著者の判定 |
|---|---|---|---|---|---|---|
| SNDK | ルール外（ユーザーの判断。この日はどのルールの合図もなし） |  | +0.0% | 保有継続 |  | **【未判定】（）** |
| AMD | ボリンジャーIII | -11.1% | -1.6% | 保有継続 | 損切り 467.47（終値から -4.4%） | 【保有継続】（ボリンジャー） |

## 候補の判定（並びは上の「買う順番」の表と同じ）

- 並びは上の「買う順番」の表と同じ（RSの高い順。勝率の高い順ではない）。注文の値段・株数・逆指値は上の表を見る。勝率・1回平均は、そのルールの過去の成績（後知恵なしの監視銘柄・2015年〜の全部の合図）。
- 空き枠: 2（同時保有4銘柄まで。保有2、うちルールの売り0）。著者が【様子見】の候補を見送るかはユーザーが決める。

| 順 | 銘柄 | ルール | 過去の勝率 | 過去の1回平均 | RS | 時間外 | ルールの判定 | 著者の判定 |
|---|---|---|---|---|---|---|---|---|
| 1 | SWKS（スカイワークス・ソリューションズ） | 逆張り: ボリンジャー メソッドIII | 68% | +1.5% | 88 | -0.7% | 買い（翌日の寄り付き） | 【買い】（ボリンジャー） |
| 2 | CRM（セールスフォース） | 逆張り: 急落の底（担当: コナーズ） | 65% | +2.1% | 23 | -0.5% | 買い（指値 179.64、3取引日まで） | 【様子見】（コナーズ） |
| 3（枠外） | SMCI（スーパー・マイクロ・コンピューター） | 逆張り: 急落の底（担当: コナーズ）（指値の3日目） | 65% | +2.1% | 3 | -0.3% | 買い（指値 23.66、3取引日まで） | 【様子見】（コナーズ） |
| 4（枠外） | NBIS（ネビウス・グループ） | 逆張り: 急落の底（担当: コナーズ） | 65% | +2.1% | 3 | +0.0% | 買い（指値 94.98、3取引日まで） | 【様子見】（コナーズ） |

- 時間外: 前の取引日の引けから、引け後（米国東部時間16〜20時）の最後の値までの騰落率（Yahoo。±5%以上は太字）。寄り付きの値段は、表の注文の目安（前日の終値で計算）から大きくずれることがある。原因の見出しは「ニュースの見出し」の節。

# 著者の回答（全文）

## 0_テーマの局面_ワインスタイン

1. **テーマ全体の局面**: 【ステージ3】（大上昇を経て30週移動平均線が水平化し、指数が下抜けた天井圏の様相 [1-4]、第2章・第8章）

2. **グループごとの局面**:
- 半導体｜ステージ3｜30週線横ばい・線の下 [2]
- 半導体製造装置・材料・設計ソフト・計測｜ステージ3｜30週線横ばい・線の下 [2]
- AIサーバー・ストレージ・メモリ・端末｜ステージ3｜30週線横ばい・線の下 [2]
- 光・通信・ネットワーク｜ステージ3｜30週線横ばい・線の下 [2]
- データセンターの電力・冷却・部品・受託製造・建設｜ステージ4｜30週線が下向き・線の下 [5, 6]
- AIプラットフォーム・クラウド｜ステージ3｜30週線横ばい・線の下 [2]
- AIソフト・セキュリティ・ITサービス｜ステージ3｜30週線横ばい・線の下 [2]

3. **転換の兆し**: 出ている。30週線の水平化と下抜け（第2章 [2]）、対S&P500のRS悪化（第4章 [7]）、電力・冷却グループのステージ4転落（第3章 [8]）。※50日線警告やS2等はマニュアルに規定なし。

4. **テーマの外**: 判定不能（騰落率のみで、30週移動平均線・出来高・チャート形状のデータが読み取れないため）

## 1_コナーズ_prompt_1

## CRM
1. **投資判断**: 【様子見】（200日線下側のため買い見送り [1, 2]）
2. **止める理由の確認**:
- 本が禁じる形・状況｜あり｜第4章（現在値183.31が200日線197.81の下側に位置 [1, 2]）
- 避けるべき時期（決算など）｜なし｜マニュアルに規定なし [3]
- 悪材料｜なし｜第2章・第3章（悪材料による急落は買いの好機であり見送り規定なし [4, 5]）
3. **現状パターンと価格**:
- 現状パターン: A（急落条件合致だが200日線割れ [1, 2]）
- 本日の発注: なし（見送り [1, 2]）
4. **注意点**: 200日線を下回った株の急落買いは大きな損失を招くため、すべて白紙に戻してください [1, 2]。

## 1_コナーズ_prompt_2

## SMCI
1. **投資判断**: 【様子見】（200日線割れのため見送り）
2. **止める理由の確認**:
- 本が禁じる形・状況｜あり｜終値23.84が200日線32.42の下にあり買い厳禁（第4章）[1]
- 避けるべき時期（決算など）｜なし｜決算75日後。避けるべき月初（3〜8日）でもない（第11章）[2]
- 悪材料｜なし｜悪材料による急落は本来買い好機であり見送り規定なし（第2・3章）[3, 4]
3. **現状パターンと価格**:
- `現状パターン: A（指値3日目の期限日）`
- A: `本日の発注: 見送り（注文取消）`
4. **注意点**: 200日線を下回った株は底狙いをせず白紙に戻すのが鉄則[1]。

## 1_コナーズ_prompt_3

## NBIS
1. **投資判断**: 【様子見】（200日線下で見送り）
2. **止める理由の確認**:
- 本が禁じる形・状況｜あり｜第4章 [1]（96.92＜MA200 179.71）
- 避けるべき時期（決算など）｜なし｜決算84日後、月初外 [2]
- 悪材料｜なし｜織込み済みで規定外 [3]
3. **現状パターンと価格**:
- 現状パターン: A（条件成立も200日線下）
- 本日の発注: なし（見送り）
4. **注意点**: 200日線下での買いは厳禁 [1]。

## 1_ボリンジャー_prompt_1

## AMD
1. **投資判断**: 【保有継続】早期手仕舞い理由なし。
2. **止める理由の確認**:
   - 本が禁じる形・状況｜なし｜第20章[1]
   - 避けるべき時期（決算など）｜なし｜マニュアルに規定なし[2]
   - 悪材料｜なし｜マニュアルに規定なし（11/19）[2]
3. **現状パターンと価格**:
   - 売りの予約注文: 〈指値売り〉600.35（現在値比 +22.7%）
4. **注意点**: 損切り467.47はスクリプトに従うこと。

## 1_ボリンジャー_prompt_2

## SWKS
1. **投資判断**: 【買い】（止める理由なし）
2. **止める理由の確認**:
- 本が禁じる形・状況｜なし｜第20章（%b<0.05かつ21日II%>0成立）[1]
- 避けるべき時期（決算など）｜なし｜次回決算まで75日（マニュアルに規定なし）[2]
- 悪材料｜判定不能｜ニュース記述省略のため
3. **現状パターンと価格**:
- 現状パターン: A（メソッドIII成立）[1]
- 本日の発注: 翌日の寄り付きで成行
4. **注意点**: 買値15%下の逆指値と上部バンド指値の更新を徹底すること [3, 4]。

# スキャン（数値と事実）


- 監視銘柄 87（判定できたのは 86、取得不可: SNDK）。
- この一覧は数値と事実だけ。売買の判断は著者のノートブックが行う。

## 1. テーマ（グループ）の強さ

| グループ | 銘柄数 | 1週 | 1カ月 | 3カ月 | 3カ月の順位 | 50日線より上の銘柄の割合 | グループ指数の30週線の局面（線との乖離、4週前からの線の傾き） |
|---|---|---|---|---|---|---|---|
| 半導体 | 16 | -9.0% | -11.5% | -5.7% | 2位 | 25% | 横ばい（-15.8%、+3.9%） |
| 半導体製造装置・材料・設計ソフト・計測 | 9 | -9.4% | -17.1% | -23.0% | 7位 | 0% | 横ばい（-20.1%、+0.4%） |
| AIサーバー・ストレージ・メモリ・端末 | 8 | -4.6% | -21.7% | -14.7% | 5位 | 12% | 横ばい（-12.7%、+5.5%） |
| 光・通信・ネットワーク | 9 | -7.4% | -11.7% | -17.3% | 6位 | 11% | 横ばい（-16.8%、+0.3%） |
| データセンターの電力・冷却・部品・受託製造・建設 | 19 | -5.2% | -9.1% | -10.6% | 3位 | 5% | 下落（-12.3%、-0.1%） |
| AIプラットフォーム・クラウド | 11 | -8.5% | -14.4% | -4.3% | 1位 | 18% | 横ばい（-12.2%、+0.9%） |
| AIソフト・セキュリティ・ITサービス | 14 | -8.9% | -13.1% | -12.2% | 4位 | 14% | 横ばい（-0.8%、+4.4%） |

## 2. テーマ全体の状態と早めの警告

- 市場全体の30週線による局面: S&P500指数 **横ばい**／NASDAQ100指数 **横ばい**（急落の底で買うルールは、過去の検証で下落相場で特に強く、横ばいの相場では負けていた）
- **2倍ETFを使う局面（案1、2026-10-13 採用）: S&P500の20週線（100日線）で 横ばい** → 新しく買う銘柄は、2倍ETFのある銘柄も元の株で買う（保有中のETFはそのまま）（SPY 715.87、100日線 758.92、20日前の線 756.51。上昇＝線より上かつ線が上向き）
- **テーマ全体の急落（S2、記録だけ。売買のルールは変えない）: あり（S2）**（SOX 9419.72、直近60取引日の最高値 13217.82 から -28.7%。S2＝最高値から−10%以上）。S2のときに「順張りの新しい買いだけ止める」形を記録で比べる（2026-10-14 ユーザー決定。バックテストでは年率は上がったが2つの期間ではどちらも少し下回ったため、記録してから採用を決める。`バックテスト結果/テーマ全体の急落を検知して手じまう・買いを止める.md`）
- **グループごとの悪いニュースの流れ（記録だけ。売買のルールは変えない。2026-11-06〜2026-11-19）**: 会社の名前と悪い言葉（格下げ・目標株価の引き下げ・見通しの引き下げ・予想未達・急落・信用・訴訟・輸出規制など）の両方がある見出しの数（Googleニュース、`tools/news_headlines.py`）。10取引日の1銘柄あたりが一番多いグループに印。2026年7〜11月の確かめでは、印のグループの合図は10月は成績が悪かった（1回平均 −10.6%、ほか −5.6%）が、7〜9月は逆に良かった（+11.6%、ほか +6.7%）（`バックテスト結果/実際の運用の期間の確認_2026-10-23/グループの悪いニュースの流れ.md`。2026-11-04）

| グループ | 悪いニュース 直近5取引日 | その前の5取引日 | 10取引日の1銘柄あたり | 良いニュース 10取引日（1銘柄あたり） | 印 |
|---|---|---|---|---|---|
| 半導体（16） | 24件 | 13件 | 2.3 | 30件（1.9） | **悪いニュースが続いている** |
| 光・通信・ネットワーク（9） | 5件 | 10件 | 1.7 | 13件（1.4） |  |
| AIサーバー・ストレージ・メモリ・端末（9） | 7件 | 1件 | 0.9 | 18件（2.0） | **良いニュースが多い** |
| AIプラットフォーム・クラウド（11） | 4件 | 3件 | 0.6 | 2件（0.2） |  |
| データセンターの電力・冷却・部品・受託製造・建設（19） | 1件 | 1件 | 0.1 | 11件（0.6） |  |
| AIソフト・セキュリティ・ITサービス（14） | 1件 | 0件 | 0.1 | 7件（0.5） |  |
| 半導体製造装置・材料・設計ソフト・計測（9） | 0件 | 0件 | 0.0 | 7件（0.8） |  |

印のグループ（半導体）の最近の見出し: 2026-11-19 Analysts Upgrade Nvidia and Nebius, Downgrade Shopify and GM（www.tokenpost.com）／2026-11-19 Analysts Upgrade Nvidia, Downgrade Shopify, GM（Wisevoter）／2026-11-19 Broadcom's revenue and AI chip sales soar, but stock remains flat amid downgrade concerns.（Pluang）

良いニュースが多いグループ（AIサーバー・ストレージ・メモリ・端末）の最近の見出し: 2026-11-19 Apple Reportedly Won’t Upgrade iPhone Air 2 Display（The Mac Observer）／2026-11-19 Apple Maps Gets Major Upgrade Across India With 3D Landmarks, Look Around, and More（The Mac Observer）

- **特殊な下げ（記録だけ。売買のルールは変えない）: あり（特殊な下げ）**（2026-10-16から）。SOX は直近60取引日の最高値から -28.7%（−15%以下が条件）、●A 前の1年の上げ +99.3%（+80%以上）、・B 雇用の伸び 137千人/月（2026-10まで。10万人未満）、●C 物価 4.0%（2026-09。3か月前 3.7%。3.5%以上で再加速）＝2つ（2つ以上が条件）。1995年〜でSOXが−15%以下かつ条件2つ以上の日は、120日後にSOXが下だったのが69%・250日後が70%（中央値 −33%）、AI以外の8業種の平均は250日後 −7%。ただし条件は過去を見て選んだもの（条件が2つ以上の局面は約5回）で、2026年7〜9月にこの間テーマを買わないと、その後の戻りを逃して2026年の成績は下がった（`バックテスト結果/実際の運用の期間の確認_2026-10-23/特殊な下げと過去の似た下げ.md`。2026-11-03）
- テーマ指数（監視銘柄の等金額平均）の30週線による局面: **横ばい**（上昇＝線より上かつ上向き、下落＝線より下かつ下向き、それ以外＝横ばい。ワインスタインのステージの近似）
- テーマ指数と50日線: 50日線より下（乖離 -12.4%）
- S&P500に対する相対的な強さ: 50日平均より下（S&P500より弱い）
- 監視銘柄のうち50日線より上の割合: 13%
- 警告（割合が40%未満かつテーマ指数が50日線より下）: **出ている**
- 参考（バックテスト）: 30週線の「下落」は高値から10〜33%下げた後に出る遅い判定。50日線・割合・相対的な強さは高値から2〜8%で出るが、誤報が年15回以上ある。警告中に新しい買いを止めると、押し目買い（ボリンジャーIII）の成績は大きく下がった（`バックテスト結果/テーマ監視銘柄・直近3年.md` 11・12節）。

## 3. ヒートマップ（Finviz、全米の業種別の騰落率）

3カ月の騰落率の上位15業種（テーマの外で強くなっている業種の確認用）:

| 順位 | 業種 | 1週 | 1カ月 | 3カ月 | 6カ月 | 1年 |
|---|---|---|---|---|---|---|
| 1 | Discount Stores | +0.1% | +7.8% | +18.0% | +6.2% | +26.0% |
| 2 | Medical Distribution | -1.8% | +3.5% | +16.8% | +34.0% | +15.9% |
| 3 | Advertising Agencies | -3.1% | +28.7% | +15.6% | -13.4% | -21.6% |
| 4 | Insurance - Diversified | -3.0% | +4.9% | +13.0% | +16.6% | +13.0% |
| 5 | Consumer Electronics | -1.5% | +1.7% | +12.8% | +14.6% | +28.3% |
| 6 | Lodging | -2.0% | +2.4% | +11.9% | +11.2% | +36.3% |
| 7 | Insurance - Reinsurance | -1.8% | +1.3% | +10.1% | +18.3% | +35.3% |
| 8 | Household & Personal Products | -1.6% | +4.0% | +8.3% | +14.6% | +11.7% |
| 9 | REIT - Hotel & Motel | -2.6% | +0.3% | +6.4% | +19.9% | +50.3% |
| 10 | Waste Management | -3.2% | +3.9% | +6.4% | +13.0% | +9.8% |
| 11 | Insurance - Property & Casualty | -1.3% | +3.1% | +6.2% | +15.6% | +14.9% |
| 12 | Diagnostics & Research | -2.7% | -3.7% | +5.6% | +42.6% | +18.5% |
| 13 | Grocery Stores | -3.9% | -0.4% | +4.7% | -7.7% | -8.3% |
| 14 | Utilities - Regulated Water | -1.5% | -2.6% | +4.6% | +5.9% | +8.0% |
| 15 | Real Estate - Diversified | -6.6% | +3.0% | +4.2% | +9.7% | +6.4% |

テーマの業種の順位（3カ月、全144業種中）: Semiconductors 128位、Semiconductor Equipment & Materials 134位、Computer Hardware 138位、Communication Equipment 122位、Electronic Components 118位、Software - Infrastructure 53位、Software - Application 102位、Internet Content & Information 114位

## 4. 急騰・急落した銘柄（前日比±5%以上、または出来高が50日平均の2倍以上）

原因のニュースをサブエージェントが調べ、候補・保有銘柄の判定材料として著者に渡す。急騰・急落そのものは売買の合図にしない（後知恵のないS&P500全体のバックテストでは、急騰の翌日に買うルールは年率7%、急落の翌日に買うルールは年率9〜10%で、採用した3つのルールより優れていなかった）。

| 銘柄 | グループ | 前日比 | 出来高（50日平均の倍） | 終値 | 50日線 | RS | 局面 |
|---|---|---|---|---|---|---|---|
| NBIS | AIプラットフォーム・クラウド | -9.4% | 1.6倍 | 96.92 | 下 | 3 | 下げ |
| AMD | 半導体 | -7.7% | 2.6倍 | 489.19 | 下 | 98 | 下げ |
| PANW | AIソフト・セキュリティ・ITサービス | +6.4% | 3.1倍 | 361.73 | 下 | 98 | 下げ |
| CRWV | AIプラットフォーム・クラウド | -6.1% | 1.4倍 | 44.91 | 下 | 0 | 下落相場 |
| SHOP | AIソフト・セキュリティ・ITサービス | -5.3% | 0.8倍 | 131.97 | 下 | 44 | 下げ |

- 局面（判定式はClaudeが置いたもの）: **上昇相場**＝終値 > 50日線 > 200日線、50日線が20取引日前より2%以上高い、ADX(14) ≧ 20／**下落相場**＝終値 < 50日線 < 200日線、50日線が20取引日前より2%以上低い、ADX(14) ≧ 20／**上げ**＝それ以外で終値が50日線より上、かつ50日線が10取引日前より上か20日線が5取引日前より上／**下げ**＝それ以外で終値が50日線より下、かつ50日線が10取引日前より下か20日線が5取引日前より下（急な下げの初めは50日線がまだ上向きのため20日線でも見る）／**レンジ**＝どれにも当たらない（2026-11-05 から5つ。それまでは上昇相場とレンジの2つだけで、下げている銘柄もレンジと出ていた）。

## 4-2. 監視外の注目銘柄（S&P500・NASDAQ100のうち監視銘柄に入っていない銘柄）

条件: 流動性（株価5ドル以上・50日平均出来高25万株以上）があり、(a) 前日比+8%以上かつ出来高が50日平均の2倍以上、または (b) 終値が直前1年の最高値（終値）を上回り、RS≧90。RSの高い順に5銘柄（ニュースを調べる）。監視銘柄に入れるかはユーザーが決める。

| 銘柄 | 種類 | 前日比 | 出来高（50日平均の倍） | RS | 終値 |
|---|---|---|---|---|---|
| PDD | 急騰 | +11.0% | 3.9倍 | 15 | 86.00 |

## 5. 保有銘柄の手じまい条件（`新分析ツール/保有銘柄.md`）

| 銘柄 | ルール | 買った日 | 買値 | 終値 | 損益 | 損切り価格（買値の15%下、逆指値） | ルールの手じまい条件 | 出来高2倍の大陰線（買った後の直近5日） | 次回決算予定日 |
|---|---|---|---|---|---|---|---|---|---|
| SNDK | ルール外（ユーザーの判断。この日はどのルールの合図もなし） | 2026-10-21 | 1371.3 | 取得不可 | | | | | |
| AMD | ボリンジャーIII | 2026-10-21 | 549.97 | 489.19 | -11.1% | 467.47 | **出来高2倍の大陰線が 2026-11-05 に出た**（まだ持っていれば、次の寄り付きで全部売る） 売りの指値: 上部バンド 600.35（今夜この値に置き直す。届いた日に売れる）（2倍ETF AMUU で持っている場合も、判定は元の株 AMD の値段） | なし | 2027-02-02 |

- 出来高2倍の大陰線: 実体（始値−終値）が前日までのATR(14)の1.5倍以上、終値がその日の値幅の下25%以内、出来高が前日までの50日平均の2倍以上の日。**押し目（ボリンジャーIII）・急落の底の保有では売りのルール**: 出たら翌日の寄り付きで全部売り、空いた枠で次の合図を買う（2026-10-02 ユーザー決定。`バックテスト結果/やり直し_売りの合図の組み合わせ.md`。乱数3組とも年率が約+2ポイント、最大下落率もやや下がった）。ミネルヴィニ・新高値V2の保有では事実の表示（順張りに足しても良くならなかった）。

- 半分売りの合図（ミネルヴィニ・新高値V2の保有だけ）: 反転のローソク足（かぶせ線・弱気の包み足・宵の明星・流れ星）＋出来高が50日平均の1.5倍以上＋RSI(14)が前日か当日に70以上。買った後に最初に出た日の翌日の寄り付きで半分売り、残り半分は50日線割れ・損切り15%まで持つ（2026-10-01 ユーザー決定。`バックテスト結果/半分だけ売るとオニールの空き枠.md`）。

- かぶせ線（ミネルヴィニ・新高値V2の保有だけ）: 上昇中の陽線の翌日に、前日の高値より上で寄り付き、前日の陽線の真ん中より下（前日の始値より上）で引けた日。翌日の寄り付きで全部売り、空いた枠で次の合図を買う。半分売りより優先する（2026-10-01 ユーザー決定。`バックテスト結果/2倍ETFで売って買い直す.md`。順張りの売買の25%で出て、1回平均+2.0%、年率 21.4%→26.4%）。

## 5-2. 前日（2026-11-18の引け）の【買い（予約）】の確認

前日の【買い（予約）】はなし。

## 6. 候補（採用したルールの条件が成立＝A。予約（B）は2026-10-25から注文せず、節6-3に参考の表示だけ）

建玉の目安: 同時保有4銘柄まで、1銘柄に資金の25%（資金÷4）、損切りは買値の15%下（ユーザー決定 2026-09-29）。

パターン: A＝最新の足で採用ルールの条件が成立（押し目・ミネルヴィニ・新高値V2は翌日の寄り付きで成行、急落の底は合図の日の終値の2%下に指値で3取引日待つ。2026-11-03 ユーザー採用）。条件の成立が目前の銘柄（B）は、予約の注文をやめたので節6-3に参考として出す（2026-10-25 ユーザー決定）。

| 銘柄 | グループ | パターン | 種類 | ルールの過去の成績 | 終値 | 前日比 | RS | 50日線の傾き | 局面 | 当てはまった条件 | 次回決算予定日 | 注文の目安 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CRM | AIソフト・セキュリティ・ITサービス | A | 逆張り: 急落の底（担当: コナーズ） | 2位（勝率65%・1回平均+2.1%） | 183.31 | -3.7% | 23 | -1.2% | 下げ | 直前5日の最高値（終値）から-15.9%下落（−15%以上）、RSI(2)=0.6（≦10）、急落の前は50日線＞200日線。市場全体の局面: S&P500 横ばい／NASDAQ100 横ばい | 2026-12-02（13日後）**決算が近い** | 指値買い 179.64（合図の日 2026-11-19 の終値 183.31 の2%下。今日から3取引日。届かなければ見送り、途中で終値が5日線を上回ったら取り消す）。損切り: 約定した値段の15%下。手じまい: 終値が5日線（今日 200.18）を上回った翌日の寄り付き（コナーズ）。**元の株で買う**（2倍ETF CRMG のある銘柄だが、S&P500が20週線で「横ばい」の局面のため。案1）。**株数の目安: 13株**（2,384ドル÷179.64。注文の価格）、購入金額 約2,335ドル |
| SMCI | AIサーバー・ストレージ・メモリ・端末 | A | 逆張り: 急落の底（担当: コナーズ）（指値の3日目） | 2位（勝率65%・1回平均+2.1%） | 23.84 | -2.2% | 3 | -8.6% | 下げ | 2026-11-17の合図: 直前5日の最高値（終値）から-20.7%下落（−15%以上）、RSI(2)=7.2（≦10）、急落の前は50日線＞200日線。市場全体の局面: S&P500 横ばい／NASDAQ100 横ばい。その後まだ指値に届かず、終値は5日線以下 | 2027-02-02（75日後） | 指値買い 23.66（合図の日 2026-11-17 の終値 24.14 の2%下。今日が最後の日。届かなければ見送り、途中で終値が5日線を上回ったら取り消す）。損切り: 約定した値段の15%下。手じまい: 終値が5日線（今日 24.85）を上回った翌日の寄り付き（コナーズ）。**株数の目安: 100株**（2,384ドル÷23.66。注文の価格）、購入金額 約2,366ドル |
| NBIS | AIプラットフォーム・クラウド | A | 逆張り: 急落の底（担当: コナーズ） | 2位（勝率65%・1回平均+2.1%） | 96.92 | -9.4% | 3 | -16.2% | 下げ | 直前5日の最高値（終値）から-24.7%下落（−15%以上）、RSI(2)=6.1（≦10）、急落の前は50日線＞200日線。市場全体の局面: S&P500 横ばい／NASDAQ100 横ばい | 2027-02-11（84日後） | 指値買い 94.98（合図の日 2026-11-19 の終値 96.92 の2%下。今日から3取引日。届かなければ見送り、途中で終値が5日線を上回ったら取り消す）。損切り: 約定した値段の15%下。手じまい: 終値が5日線（今日 106.58）を上回った翌日の寄り付き（コナーズ）。**元の株で買う**（2倍ETF NBIL のある銘柄だが、S&P500が20週線で「横ばい」の局面のため。案1）。**株数の目安: 25株**（2,384ドル÷94.98。注文の価格）、購入金額 約2,374ドル |
| SWKS | 半導体 | A | 逆張り: ボリンジャー メソッドIII | 3位（勝率68%・1回平均+1.5%） | 78.66 | -4.6% | 88 | +7.7% | レンジ | %b=-0.029（<0.05）、21日II%=+0.104（>0） | 2027-02-02（75日後） | 翌日の寄り付きで買い。損切り: 買値の15%下。手じまい: 買った日の夜から、売りの指値をその日の上部バンド（今日 91.00）に置き、毎晩その日の値に置き直す。**株数の目安: 30株**（2,384ドル÷78.66。今日の終値。寄り付きの値段で変わる）、購入金額 約2,360ドル |

- 局面（判定式はClaudeが置いたもの）: **上昇相場**＝終値 > 50日線 > 200日線、50日線が20取引日前より2%以上高い、ADX(14) ≧ 20／**下落相場**＝終値 < 50日線 < 200日線、50日線が20取引日前より2%以上低い、ADX(14) ≧ 20／**上げ**＝それ以外で終値が50日線より上、かつ50日線が10取引日前より上か20日線が5取引日前より上／**下げ**＝それ以外で終値が50日線より下、かつ50日線が10取引日前より下か20日線が5取引日前より下（急な下げの初めは50日線がまだ上向きのため20日線でも見る）／**レンジ**＝どれにも当たらない（2026-11-05 から5つ。それまでは上昇相場とレンジの2つだけで、下げている銘柄もレンジと出ていた）。

- 2倍ETF: 2倍ETFがある銘柄（ユーザーがムームー証券で買えることを確認した38銘柄のうち、目減りが年15%未満のもの）は、株の代わりに2倍ETFを買う（2026-10-04 ユーザー決定。`バックテスト結果/2倍ETFを使う決まり.md`。年率 約27%→約33%、確定した損益だけの最大下落率 約30%→約31%、含み損込みは約33%→約45%）。買う金額は株と同じ（資金の25%）。合図・損切り（元の株の買値の15%下＝ETFでは約30%下）・手じまいはすべて元の株の値段で判定する。指値・逆指値はETFの値段に直して置く。どのETFかは `新分析ツール/2倍ETFの対応表.json`（売買代金が1日500万ドル以上で、直近1年の目減りが一番小さいもの）。**2倍ETFで買うのは、S&P500が20週線（100日線）で「上昇」の局面のときだけ。横ばい・下落の局面では元の株で買う**（案1、2026-10-13 ユーザー採用。買う日に決め、買った後は局面が変わってもそのまま持つ。`バックテスト結果/流れ（市場の局面）を使う形.md`）。

- ルールの過去の成績: 今の売りのルールで、後知恵なしの監視銘柄・2015年〜の全部の合図の1回ごとの成績（2026-10-02計算、`新分析ツール/バックテスト結果/ルールごとの成績.md`）。順位は1回平均（1回の売買で平均いくら増えるか）の順。表はパターン（A→B）ごとに、この順位の良い順に並べた（表示の順番だけ。買う順番・件数の上限は変えていない。候補の選び方を変えても成績は変わらなかったため。2026-10-02 ユーザーの指示）。著者には渡さない。

- 同じ業種は同時に2銘柄まで（ユーザー決定 2026-09-28）のため見送った候補（保有中の銘柄と、買う順番で先に残した候補で数える）: MRVL（A・逆張り: 急落の底。Semiconductors: AMD・SWKS）

- 悪いニュースが続いているグループ（半導体）の候補（記録だけ。売買のルールは変えない。著者には渡さない）: SWKS

- 候補の数: 空き枠2（同時保有4銘柄まで。保有2、うち今日ルールの売りが成立0）＋予備2件まで表に出した（2026-10-25 ユーザー決定）。ほかの1件は枠に入らないので、著者の判定とニュース調査に回さない: FDS（A・ボリンジャー メソッドIII、RS 92）

- テーマの外の候補（グループが「テーマの外」）: 監視銘柄の候補で枠が埋まらないときに使う（監視銘柄の候補を先に買う）。S&P500の今の構成銘柄のうち監視銘柄でない銘柄から、RS≧90・30週線が上向きで終値がその上・業種の3カ月の強さが上位20%の17銘柄を調べ、空き枠2つ分まで出した。バックテストでは、テーマの外の強い銘柄で空き枠を埋めると、テーマが弱い時期の成績が支えられた（`バックテスト結果/半導体・AIに特化した場合.md`。2026-10-01 ユーザー決定）。

- RS≧80の押し目（ボリンジャーIII）は、バックテストで成績がより安定していた（PF3.27、最大下落20%）。

## 6-3. 参考: 条件の成立が目前の銘柄（予約は注文しない・著者には送らない）

2026-10-25 ユーザー決定: 予約（逆指値・指値）の注文はやめ、参考の表示だけにする。毎朝のツールと同じ条件・値段で予約の約定をバックテストに入れると、どの形も年率が下がった（後知恵なし 35.7%→30.7〜34.2%、87銘柄 45.6%→34.2〜42.6%。`バックテスト結果/点検_2026-10-25/`）。引けで条件がそろえば、翌朝の節6に買いの候補（A）として出る。各ルールでRSの高い順に2件まで。

| 参考の銘柄 | グループ | 種類 | 終値 | 前日比 | RS | 当てはまった条件 | 条件がそろう目安の価格（注文はしない） |
|---|---|---|---|---|---|---|---|
| TXN | 半導体 | ボリンジャー メソッドIII（%bが0.05未満に近い） | 285.75 | -2.3% | 94 | %b=0.198（0.05まであと少し）、21日II%=+0.067（>0） | 279.27（この値より下で引けると翌朝の買いの候補（A）。目安） |
| SNPS | 半導体製造装置・材料・設計ソフト・計測 | ボリンジャー メソッドIII（%bが0.05未満に近い） | 430.91 | -0.7% | 51 | %b=0.111（0.05まであと少し）、21日II%=+0.098（>0） | 426.86（この値より下で引けると翌朝の買いの候補（A）。目安） |


# ニュース（サブエージェントの調査）

# ニュース調査（2026-11-19 米国引け時点、JST 2026-11-20 作成）
出典は headlines.md の見出し（媒体・日付）。見出しだけで分からないものはWeb検索したが、11/19当日の記事は見つからなかったものがある。

## テーマ全体の下げの原因
当たる日（1節で6グループの1週が-5%以下、S2あり、4節で複数銘柄が-5%以下）。
- きっかけ: 11/19 Anthropic が Nasdaq に上場（初日 +27%、Benzinga 11/19）したが、AI熱は戻らず主要指数が急落（Reuters 11/19「Wall Street ends sharply lower as Anthropic's debut fails to revive AI fervor」）。Nasdaq -2.25%（bloomingbit 11/19）、ダウ約-1,084〜1,100ドル、S&P500は6営業日続落（Motley Fool 11/19）。NY株は6カ月半ぶり安値（京都新聞 11/19）。
- 広がった先: ソフト株は11/17にすでに下落（Salesforce -9%、Yahoo Finance 11/17。「AI企業がSalesforceを破壊する」との投資家発言）。Intuitも11/18に -7%（Startup Fortune 11/18。ClaudeのBank連携金融ツールがTurboTax懸念）。半導体では AMD が11/19に空売りレポート（中国との関係を指摘、会社は否定）で約-7%（Barron's・IBT 11/19）。Druckenmillerが半導体株を縮小（Barron's 11/19）。
- 信用・金利: Fed議事録がAI設備投資を理由に追加利上げを示唆（Startup Fortune 11/19）。ECBがAI関連の簿外債務4兆ドル超をサブプライムに例える（Tech Times 11/19）。CoreWeaveは1カ月で約25%下落（24/7 Wall St. 11/19）。11/19当日の社債利回り・CDS・格付けの具体的な数字は見出し・検索とも見つからなかった（検索語: AI debt OR bonds OR credit spreads OR CDS、CoreWeave stock 11/19）。ハイイールド債・VIXの数値は取得不可。
- 同日に一緒に下げた別業界: ソフト・クラウド（NBIS -9.4%、CRWV -6.1%、SHOP -5.3%）。共通の原因として、Anthropic上場によるAI関連の資金の受け皿・評価の見直しが見出し上に出ている（確定した原因の記事はなし）。
- 経済指標・要人発言: Fed議事録（上記）。主要決算は PANW・INTU・Walmartが引け後（下記）。
- 「〇〇ショック」の呼び名: 日本語検索「ショック 株」で該当する呼び名は見つからなかった。メモリ・HDD系（Seagate/WDC +4%、SanDisk小幅高）は同日に上げた（24/7 Wall St. 11/19）。

## 引け後・時間外の材料
- INTU: 時間外 -9.8%。第1四半期は予想を上回ったが、売上見通しが予想に届かず、Mailchimpを Bending Spoons に売却すると発表（Benzinga・Barron's・Business Wire 11/19）。
- PANW: 決算を受け時間外 +9%（株探 11/19）。Applied Compute を45億ドルで買収（CSO Online・American Bazaar 11/19）。同社は11/19の通常取引でも +6.4%。
- AMD: 時間外 -1.6%、新しい材料の見出しなし。
- SWKS -0.7%、CRM -0.5%、SMCI -0.3%、NBIS +0.0%、SNDK +0.0%: 原因の見出しは見つからなかった（動きが小さい）。

## AMD（保有）
- 11/19 前日比 -7.7%、出来高2.6倍。空売り投資家のレポートが「NvidiaのAMD代替にならない」「中国との関係」を指摘、会社は否定（Barron's・Intl Business Times・IBD 11/19）。
- 11/13 Yahoo Finance: 下落、11/14 Motley Fool: 同週は上昇（週の中で大きく振れた）。
- 11/18 GuruFocus: Supermicroが AMDチップでAI技術を発表（好材料）。
- 次回決算 2027-02-02（scan.md）。
- 悪材料: あり（空売りレポート。内容の真偽は未確認）

## CRM（候補）
- 11/17 Salesforce -9%、ソフト株の下げを主導（Yahoo Finance・MarketWatch・Benzinga 11/17）。Anthropic上場前のソフト株売り。
- 11/19 Salesforceが米国のSIコンソーシアムを主導（Business Wire）。Barron's 11/19: ソフト株が上げる中でSalesforceは出遅れ。
- 次回決算 2026-12-02（scan.md）。
- 悪材料: 確認できず（株価の下げ以外に会社固有の不祥事・下方修正は見出しになし）

## CRWV
- 11/19 -6.1%。当日の原因記事は見つからなかった（検索: CoreWeave CRWV stock November 19 2026 why down。当日分は出ず）。24/7 Wall St. 11/19: 1カ月で約25%下落、$40か$50のどちらが先かという記事。
- 一般的な市場の下げ・AI関連の信用不安の流れの中の動き（上の節）。会社固有の新しい発表は確認できなかった。
- 悪材料: 確認できず（原因となるニュースは見つからなかった）

## INTU
- 11/18 -7%（Claudeの金融ツールがTurboTaxを脅かすとの懸念、Startup Fortune）。
- 11/19 引け後 決算: 予想は上回ったが見通しが弱く時間外 -9.8%（上記）。
- 決算: 11/19発表 EPS・売上とも予想を上回る（Barron's）、ガイダンスは予想に届かず。
- 悪材料: あり（見通し未達、Mailchimp売却）

## NBIS
- 11/19 -9.4%。11/16 Zacks: Q3決算後に10%下落。11/15 Motley Fool: 急落の理由と買い場かの記事。11/19 Benzinga に「上昇」の見出しもあったが、終値は下落。当日の下げの具体的な原因の見出しは見つからなかった。
- 24/7 Wall St. 11/19: 顧客の前払いが設備投資の100%超との強気記事。
- 悪材料: 確認できず（原因となるニュースは見つからなかった）

## PANW
- 11/19 +6.4%、出来高3.1倍。決算（時間外 +9%）と Applied Compute の45億ドル買収（11/19 CSO Online、CTech）。11/19寄り前から急騰（Investing.com 11/19）。
- 検索では別時期（2026年2月、Q2）の記事が出たため、当日の決算数値は取得不可。
- 悪材料: 確認できず

## PDD
- 11/19 +11.0%、出来高3.9倍、RS 15。見出しに原因なし。検索でも11/19の記事は見つからず（直近は2026年8月の第2四半期決算の記事のみ）。決算の可能性はあるが未確認。原因となるニュースは見つからなかった。
- テーマ（業界）: 中国のEコマース（Temu親会社）。AI半導体テーマとは別。

## SHOP
- 11/19 -5.3%。Analysts Downgrade Shopify（TokenPost・Wisevoter 11/19の見出し「Analysts Upgrade Nvidia and Nebius, Downgrade Shopify and GM」）。格下げした会社名は取得不可。
- 11/3 Q3決算日に -8.7%、10/22 ATB Cormark が格下げ（Sector Perform）。11/17 -4.3%。
- 悪材料: あり（格下げ。内容は上記）

## SMCI
- 11/17 下落（Investing.com・Yahoo Finance 11/17）。11/18 GuruFocus: AMDチップでAI技術を発表、PCIe Gen 6 サーバー出荷。11/18 24/7 Wall St.: 3カ月で40%下落。
- 11/19 -2.2%、原因となるニュースは見つからなかった。次回決算 2027-02-02。
- 悪材料: 確認できず

## SNDK（保有）
- 11/13 Yahoo Finance「Why Sandisk Stock Is Falling Today」、11/17 Motley Fool「下げ続ける理由」。11/18 Barchart: 11月20日の日付に注目という記事（内容は取得不可）。
- 11/19 24/7 Wall St.: SanDisk は小幅高、Seagate・WDC +4%。時間外 +0.0%（754.99）。scan.md の終値は取得不可だが、Yahoo時間外表の引け値は754.99。
- 悪材料: 確認できず

## SWKS
- 11/16 TradingView: 売上 -3.1%、JPMorgan が目標株価を$77に引き上げ。11/19 MarketBeat: 50日線を下回る。11/19 -4.6%、会社固有の原因は見つからなかった。次回決算 2027-02-02。
- 悪材料: 確認できず

## テーマ全体のその他のニュース（直近1週間）
- 半導体製造装置: Teradyne（11/16 Advantestの東京-11%安が検査装置に波及、TradingView）、Lam Research -7%（11/17 Yahoo Finance。サイクルのピークの懸念、Insider Monkey 11/18）。Bernstein は半導体製造装置の市場$279B拡大を指摘（GuruFocus 11/18）。
- Micron: 11/16 米政権が中国向け先端チップの抜け道を閉じる報道で下落（Boise Dev）。12/17に決算予定（GlobeNewswire 11/19）。
- Broadcom: 売上・AIチップ販売は好調だが株は横ばい、格下げ懸念（Pluang 11/19）。
- Nvidia: 暫定CEOに関する報道（TIKR 11/19）。決算をめぐる解説（野村證券 11/19）。
- Lumentum: 売上137%増なのに株が急落（Investing.com 11/19）。

# ニュースの見出し（プログラムが自動で取得）

- Googleニュース（日付を指定）とYahooファイナンスの見出しを `tools/news_headlines.py` が自動で並べたもの。日付は米国東部時間の配信日（引け後の記事は翌日付）。原因の判断・売買の判断はしていない。
- 調べた銘柄の選び方: ①保有 ②今日の候補 ③時間外に±5%以上動いた監視銘柄 は全部、④引けまでに大きく動いた銘柄（1週で±5%のグループの上位3・1日で±7%）は合計12銘柄まで。
- 1週で−5%以下のグループ: 半導体製造装置・材料・設計ソフト・計測（-9.4%）、半導体（-9.0%）、AIソフト・セキュリティ・ITサービス（-8.9%）、AIプラットフォーム・クラウド（-8.5%）、光・通信・ネットワーク（-7.4%）、データセンターの電力・冷却・部品・受託製造・建設（-5.2%）
- 1週で+5%以上のグループ: なし

## 0. 時間外（引け後）の値動き（2026-11-19 の引けから、Yahoo。±3%以上の監視銘柄と、保有・候補は全部）

| 銘柄 | 区分 | 引け | 時間外 | 騰落率 |
|---|---|---|---|---|
| INTU | 監視 | 310.02 | 279.72（17:18 ET） | **-9.8%** |
| AMD | 保有 | 489.17 | 481.56（17:17 ET） | -1.6% |
| SWKS | 候補 | 78.67 | 78.15（16:42 ET） | -0.7% |
| CRM | 候補 | 183.41 | 182.40（17:07 ET） | -0.5% |
| SMCI | 候補 | 23.84 | 23.78（17:17 ET） | -0.3% |
| NBIS | 候補 | 96.85 | 96.88（17:17 ET） | +0.0% |
| SNDK | 保有 | 754.99 | 755.16（17:17 ET） | +0.0% |

## 1. 市場全体（2026-11-19）

### 市場全体（英語のまとめ記事）
検索語: `stocks Wall Street close Nasdaq`
- 11/19 Reuters | Wall Street ends sharply lower as Anthropic's debut fails to revive AI fervor
- 11/19 The Washington Post | Anthropic shares soar in stock market debut
- 11/19 bloomingbit | New York Stocks Close Lower; Nasdaq Falls 2.25%
- 11/19 Benzinga | Stock Market Today: Dow, S&P 500, Nasdaq 100 Futures Rise as Wall Street Awaits Anthropic’s Listing— PANW
- 11/19 24/7 Wall St. | Stock Market Today: Anthropic IPO Revives the AI Trade, but Fear Is Growing

### 市場全体（Stock Market Today）
検索語: `"stock market today"`
- 11/19 Eurasia Business News | Stock Market Today, November 19, 2026: Dow Sinks 1,084 Points, Nasdaq Drops 2.2% After Anthropic Debut
- 11/19 The Motley Fool | Stock Market Today, Nov. 19: Dow Plunges 1,100 Points as the S&P 500 Suffers Its 6th Straight Day of Losses
- 11/19 Benzinga | Anthropic Jumps 27% in Record Debut, S&P 500 Eyes Sixth Straight Loss: Stock Market Today
- 11/19 Investor's Business Daily | Dow Jones Futures Fall After Ugly Market Reversal To New Lows; Anthropic IPO Debuts, AMD Dives
- 11/19 The Motley Fool | Stock Market Today, Nov. 19: Alphabet Shares Fall as Anthropic Nasdaq Debut Puts Fresh Value on Google's Stake

### 市場全体（日本語のまとめ記事）
検索語: `米国株式市場 OR NY株`
- 11/19 日本経済新聞 | NY株ハイライト アンソロピック、一時急騰も波乱の船出 主要指数は下落
- 11/19 Reuters | 米国株式市場＝急落、アンソロピック上場でもＡＩ熱戻らず
- 11/19 外為どっとコム | 【見通し】NY株見通しー堅調な展開か アンソロピックのIPOに注目
- 11/19 Yahoo!ニュース | NY株5万ドル割れ 5カ月ぶり、アンソロ上場で（時事通信）
- 11/19 京都新聞デジタル | ＮＹ株１１０１ドル下落、６カ月半ぶり安値

### 半導体・AI株（英語）
検索語: `chip stocks OR semiconductor stocks OR AI stocks`
- 11/19 Yahoo Finance | 5 Best Affordable Blue Chip Stocks to Buy Now
- 11/19 Investor's Business Daily | Chip Stocks Waver On Anthropic IPO, AI Prospects
- 11/19 Barron's | Druckenmiller Retreats From Chip Stocks in Pivot to Gold Miners and SpaceX
- 11/19 Fast Company | Why Big Tech and memory chip stocks are getting a boost today
- 11/19 The Motley Fool | Semiconductor Sell-Off: These Artificial Intelligence (AI) Chip Stocks Are Screaming Buys Before They Go Parabolic

### 信用（社債・借金）
検索語: `AI debt OR bonds OR credit spreads OR CDS`
- 11/19 International Financing Review | Credit derivatives are back, but this time is different
- 11/19 BigGo Finance | Druckenmiller Liquidates Stocks, Flips to Shorting Copper, Admits He "Can't See" the Next 12 Months
- 11/19 Institutional Investor | Druckenmiller Prunes His Portfolio
- 11/19 Tech Times | ECB Draws Subprime Parallels as Over $4 Trillion in AI Debt-Like Commitments Stay Off Balance Sheets
- 11/19 Startup Fortune | Fed minutes name the AI buildout as a reason more rate hikes are coming

### 「〇〇ショック」の呼び名（日本語）
検索語: `ショック 株`
- 11/19 週刊エコノミスト Online | 2027年に上がる株：暗雲迫るAI投資は買いの好機か
- 11/19 週刊エコノミスト Online | 2027年に上がる株：エヌビディアは悪材料 トランプ敗北は好材料 伊藤奈々恵・編集部
- 11/19 ｄメニューニュース | データセンターハブに成長も！ ブラジル株はAI時代のワイルドカードか？
- 11/19 トウシル | 円換算で約56兆円を超えるバークシャーの潤沢な現金残高
- 11/19 ライブドアニュース | 【JT株が暴落】日本の巨額資金がロシアへ流出で2連続ストップ安！

### 引け後・時間外の動き（英語）
検索語: `"after hours" OR "after the bell" OR "extended trading" stocks`
- 11/19 TradingView | Stocks making big moves after hours: INTU, BULL, GAP
- 11/19 Seeking Alpha | Stocks making big moves after hours: INTU, BULL, GAP (SP500:)
- 11/19 AskTraders.com | Intuit Stock Plunges After Hours as Revenue Guidance Trails Consensus
- 11/19 Benzinga | VisionWave Holdings (VWAV) Stock Falls 18.74% After Hours: Here's Why
- 11/19 kalkine.ca | Why Are Magnera (NYSE:MAGN) Shares Surging 15% in Extended Trading as Fiscal 2027 Guidance Lands?
- 11/19 Benzinga | SciSparc (SPRC) Stock Jumps 39% After Hours as Agentic AI Strategy Draws Attention
- 11/19 Benzinga | Red Robin (NASDAQ: RRGB) Shares Fall 17.48% After Hours: Here's Why
- 11/19 Benzinga | Inno Holdings (INHD) Stock Soars Over 75% After Hours on Merger Agreement Announcement

### 引け後・時間外の動き（日本語）
検索語: `時間外 決算 株`
- 11/19 野村證券 | AI規制が注目される中でのエヌビディア決算 マーケットへの影響と今後の注目点を解説 野村證券・村山誠
- 11/19 Yahoo!ファイナンス | ユニバーサル・テクニカル、決算受け時間外で５％安＝米国株個別(株探ニュース)
- 11/19 株探 | パロアルト、決算受け時間外で９％高＝米国株個別
- 11/19 BigGo ファイナンス | 米ウォルマート、第3四半期決算を前に時間外で株価下落－高い市場予想のハードル試す
- 11/19 Yahoo!ファイナンス | パロアルト、決算受け時間外で９％高＝米国株個別(株探ニュース)
- 11/19 Investing.com - FX | 株式市場 | ファイナンス | 金融ニュース | ギャップ株が時間外取引で約4%上昇、第3四半期決算がアナリスト予想を上回る
- 11/19 BigGo ファイナンス | 中国・NetEase、第3四半期売上高279億元で微減 ゲーム収入は2年ぶりにマイナス成長

### 買収・合併（英語）
検索語: `acquisition OR acquire OR merger OR takeover chip OR semiconductor OR AI OR optical`
- 11/19 MeriTalk | SOCOM Seeks Commercial AI Platform to Unify Acquisition Workflows
- 11/19 PEI Private Equity | TowerBrook, CD&R-backed R1 to acquire prior-authorization AI firm Humata
- 11/19 Investor's Business Daily | Elon Musk's Latest Calls For Tesla-SpaceX Merger; Explains Pay Package
- 11/19 CSO Online | Palo Alto Networks bets $4.5B on enterprise AI with Applied Compute acquisition
- 11/19 ExecutiveBiz | USSOCOM Seeks AI-Powered Commercial Acquisition Workflow Platforms
- 11/19 CTech | Palo Alto's $4.5 billion acquisition exposes a missed opportunity for Israeli AI startups
- 11/19 The Daily Review | DataMEDS AI Agrees to Acquire TBIA Cancer AI Blood Test Platform From Todos Medical Estate for Subsidiary Helomics, Inc.
- 11/19 The American Bazaar | Palo Alto Networks bets $4.5 billion on AI startup Applied Compute as shares jump 9%

## 2. 保有・候補・時間外で大きく動いた銘柄（2026-11-13〜2026-11-19 の見出し）

### SNDK（Sandisk Corporation、保有、時間外 +0.0%）

#### Googleニュース
検索語: `Sandisk stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/13 Yahoo Finance | Why Sandisk Stock Is Falling Today
- 11/17 The Motley Fool | Why Sandisk Stock Keeps On Going Down
- 11/17 CNN | SNDK Stock Quote Price and Forecast
- 11/18 Barchart.com | Dear Sandisk Stock Fans, Mark Your Calendars for November 20

#### Yahooファイナンス
検索語: `SNDK`
- 11/19 24/7 Wall St. | Billionaire Stanley Druckenmiller Cut TSMC 94% in One Quarter, Leaving Just $14.9 Million
- 11/19 24/7 Wall St. | Micron Cratered 20% This Month: This Wall Street Pro is Ardent That It Quadruples in Price From Here
- 11/19 24/7 Wall St. | Micron’s Next $100 Billion Growth Opportunity Could Surprise Wall Street

### AMD（Advanced Micro Devices, Inc.、保有、半導体、前日比 -7.7%、1週 -16.4%、時間外 -1.6%）

#### Googleニュース
検索語: `Advanced Micro Devices stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/13 Yahoo Finance | Why Advanced Micro Devices Stock Is Down Today
- 11/14 The Motley Fool | Why Advanced Micro Devices Stock Surged This Week
- 11/17 CNN | AMD Stock Quote Price and Forecast
- 11/19 Barron's | AMD Stock Drops After Short Report Says It Isn’t an Nvidia Replacement

#### Yahooファイナンス
検索語: `AMD`
- 11/19 Barrons.com | Anthropic, AMD, Alphabet, Palo Alto, Take-Two, Walmart, and More Stocks That Explain Today’s Market
- 11/19 International Business Times | AMD Shares Tumble 7% After Short Seller Questions China Ties. Chipmaker Denies Allegations.
- 11/19 Investor's Business Daily | Chip Stocks Waver On Anthropic IPO, AI Prospects, AMD Short

### SWKS（Skyworks Solutions, Inc.、候補、半導体、前日比 -4.6%、1週 -12.6%、時間外 -0.7%）

#### Googleニュース
検索語: `Skyworks Solutions stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/16 TradingView | Weekly Recap: Revenue falls 3.1% and JPMorgan raises target to $77
- 11/18 Orange County Business Journal | Midday Stock Roundup: Alignment Health Drops 9%
- 11/19 MarketWatch | Skyworks Solutions Inc. stock underperforms Thursday when compared to competitors
- 11/19 MarketBeat | Skyworks Solutions (NASDAQ:SWKS) Share Price Crosses Below 50 Day Moving Average - Here's What Happened

#### Yahooファイナンス
検索語: `SWKS`
- 11/13 24/7 Wall St. | The Chip Index Has Been Slashed, but These 3 Stocks Have a Path Back
- 11/17 PR Newswire | Netlist Announces Appointment of Noel Whitley as General Counsel and James Hickey to Board of Directors

### CRM（Salesforce, Inc.、候補、AIソフト・セキュリティ・ITサービス、前日比 -3.7%、1週 -15.7%、時間外 -0.5%）

#### Googleニュース
検索語: `Salesforce stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/17 Yahoo Finance | Salesforce Sinks 9% as Software Slides Before Anthropic IPO: Investor Warns AI Companies Seek to “Destroy Salesforce Entirely”
- 11/17 MarketWatch | Why Salesforce’s stock led the S&P 500’s decliners amid tech jitters
- 11/17 Investing.com | Why is Salesforce stock sliding today?
- 11/17 Benzinga | Dow Slides 1.4% as Salesforce Leads Software Rout Before Anthropic IPO: Stock Market Today

#### Yahooファイナンス
検索語: `CRM`
- 11/19 Barrons.com | Software Stocks Are Throwing a Party. Salesforce Didn’t Get the Invite—Yet.
- 11/19 Business Wire | Salesforce to Lead Consortium Bringing Trusted American SI to Global Markets
- 11/19 GlobeNewswire | Software as a Service (SaaS) Market to Reach USD 1,367.68 Billion by 2035 as AI Agents Reshape Pricing and Salesforce, Adobe, ServiceNow and Workday Build New AI Revenue Lines

### SMCI（Super Micro Computer, Inc.、候補、AIサーバー・ストレージ・メモリ・端末、前日比 -2.2%、1週 -11.7%、時間外 -0.3%）

#### Googleニュース
検索語: `Super Micro Computer stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/17 Investing.com | Why is Super Micro Computer stock sliding today?
- 11/17 Yahoo Finance | What Is Driving The Move In Super Micro Computer Stock?
- 11/18 Trefis | Can Super Micro Computer Stock Jump 50%?
- 11/18 24/7 Wall St. | Super Micro Computer's 40% 3 Month Downturn: A Great Entry Point Says This Wall Street Pro Who Predicts 165% Returns

#### Yahooファイナンス
検索語: `SMCI`
- 11/18 GuruFocus.com | Supermicro Has an AI Bottleneck and Is Turning to AMD
- 11/18 GuruFocus.com | Supermicro Unveils Major AI Technology Breakthrough With AMD Chips
- 11/18 Simply Wall St. | Super Micro Computer (SMCI) Ships PCIe Gen 6 Servers, Is It 57% Below Fair Value?

### NBIS（Nebius Group N.V.、候補、AIプラットフォーム・クラウド、前日比 -9.4%、1週 -24.7%、時間外 +0.0%）

#### Googleニュース
検索語: `Nebius stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/15 The Motley Fool | Why Is Nebius Stock Crashing, and is it a Buying Opportunity?
- 11/16 Zacks Investment Research | Nebius Stock Falls 10% After Q3 Earnings: Should You Buy Now?
- 11/19 Yahoo Finance | Nebius Stock’s (NBIS) Q3 Sell-Off Looks Like an Opportunity
- 11/19 Benzinga | Why Is Nebius Stock Surging on Thursday? - Nebius Group (NASDAQ:NBIS)

#### Yahooファイナンス
検索語: `NBIS`
- 11/19 24/7 Wall St. | CoreWeave Just Dropped 25% in a Month. Will CRWV Stock Hit $40 or $50 First?
- 11/19 24/7 Wall St. | Why Wall Street Is Wrong: Buy Nebius as Customers Prepay Over 100% of Its CapEx
- 11/19 Motley Fool | CoreWeave vs. Nebius: Which Artificial Intelligence (AI) Stock Will Deliver Bigger Gains by 2028?

### INTU（Intuit Inc.、AIソフト・セキュリティ・ITサービス、前日比 -1.0%、1週 -8.9%、時間外 -9.8%）

#### Googleニュース
検索語: `Intuit stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/18 Startup Fortune | Intuit stock drops 7% ahead of earnings as Claude's bank-linked finance tool raises TurboTax fears
- 11/19 Barron's | Intuit Earnings Beat Wasn’t Enough to Boost the Stock
- 11/19 Benzinga | Intuit Stock Tumbles On Q1 Earnings, Soft Outlook, Mailchimp Divestiture

#### Yahooファイナンス
検索語: `INTU`
- 11/19 Barrons.com | Bending Spoons to Buy Marketing Platform from Intuit as It Beats Expectations
- 11/19 Barrons.com | Intuit Stock Tumbles After Earnings Beat. It’s Selling Mailchimp.
- 11/19 Business Wire | Intuit Reports First-Quarter Results and Enters Agreement to Sell Mailchimp to Bending Spoons

## 3. 引けまでに大きく下げた銘柄（2026-11-13〜2026-11-19 の見出し）

### TER（Teradyne, Inc.、半導体製造装置・材料・設計ソフト・計測、前日比 -3.3%、1週 -13.8%、時間外 -1.1%）

#### Googleニュース
検索語: `Teradyne stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/13 Traders Union | Teradyne stock drops as oversold signals increase rebound risk
- 11/16 TradingView | Teradyne Stocks Drop 6.14% as Advantest's 11% Tokyo Plunge Hits Chip Testers
- 11/16 StockStory | Axcelis Technologies, FormFactor, ACM Research, Teradyne, and Applied Materials shares plummet, what you need to know
- 11/18 Yahoo Finance | Why Jefferies Calls Teradyne (TER) a “Compute Test Company”

#### Yahooファイナンス
検索語: `TER`
- 11/13 Zacks | Teradyne Benefits From Strong Test Demand: Can It Beat KLAC & COHU?
- 11/16 Business Wire | Teradyne to Present at the 2026 UBS Global Technology and AI Conference

### LRCX（Lam Research Corporation、半導体製造装置・材料・設計ソフト・計測、前日比 -3.8%、1週 -12.9%、時間外 -0.1%）

#### Googleニュース
検索語: `Lam Research stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/13 Benzinga | What's Going On With Lam Research Stock Friday?
- 11/13 ChartMill | LRCX News | LAM RESEARCH CORP (NASDAQ:LRCX)
- 11/16 24/7 Wall St. | Jim Cramer Says Lam Research Has Come Down Enough. It’s ‘Absolutely My Favorite’
- 11/17 Yahoo Finance | Lam Research Stock Fell Nearly 7%. What Happened?

#### Yahooファイナンス
検索語: `LRCX`
- 11/18 GuruFocus.com | Bernstein Spots 4 Ways to Play the $279 Billion Chip Tool Boom
- 11/18 Insider Monkey | Lam Research Corporation (LRCX) Retreated Amid Cyclical Peak Concerns
- 11/18 TIKR | A $2.8 Billion Fund Dumps These 3 Stocks

### AMAT（Applied Materials, Inc.、半導体製造装置・材料・設計ソフト・計測、前日比 -3.8%、1週 -11.0%、時間外 +0.0%）

#### Googleニュース
検索語: `Applied Materials stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/13 Proactive financial news | Applied Materials Inc Share Price - AMAT, RNS News, Articles, Quotes, & Charts (NASDAQ:AMAT)
- 11/17 Yahoo Finance | Why Is Applied Materials Stock Down Over 5%?
- 11/19 24/7 Wall St. | Applied Materials Is Still Up 35% This Year. Will AMAT Stock Hit $300 or $400 First?
- 11/19 Investing.com South Africa | Why is Applied Materials stock rallying today? By Investing.com

#### Yahooファイナンス
検索語: `AMAT`
- 11/19 Insider Monkey | Here’s What Underpins Long-Term Outlook for Applied Materials (AMAT)
- 11/19 Insider Monkey | Multiple Compression Weighs on Applied Materials (AMAT) in Q3
- 11/19 Investing.com | Premarket movers: Palo Alto soars, chip stocks rally ahead of Anthropic debut

### MRVL（Marvell Technology, Inc.、半導体、前日比 -4.9%、1週 -15.8%、時間外 +0.3%）

#### Googleニュース
検索語: `Marvell stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/13 Yahoo Finance | Marvell Stock Could Have a Bigger AI Opportunity Than Investors Realize
- 11/17 Trefis | What Sent Marvell Stock Down Over 7%?
- 11/18 Schaeffer's Investment Research | Marvell Technology Stock Slides Despite Brief Nvidia Respite

#### Yahooファイナンス
検索語: `MRVL`
- 11/19 24/7 Wall St. | Broadcom’s $13.67B Quarterly FCF Beats Marvell’s Scaling Story, Plain and Simple
- 11/19 Investing.com | Lumentum’s sales surged 137%—so why is its stock crashing?
- 11/19 TIKR | Cathie Wood Says Nvidia’s Interim CEO Is “Not a Tech Expert.” Kevin O’Leary Disagrees. Who’s Right?

### MU（Micron Technology, Inc.、半導体、前日比 -2.1%、1週 -13.5%、時間外 -0.6%）

#### Googleニュース
検索語: `Micron stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/16 Boise Dev | Micron stock tumbles as Trump admin. cuts a loophole allowing China access to advanced chips
- 11/17 Yahoo Finance | Why Is Micron Stock Down Nearly 8%?
- 11/17 Barron's | Micron Drops Again. What Hedge Funds Are Doing With the Stock.
- 11/17 The Motley Fool | Why Micron Stock Keeps On Going Down

#### Yahooファイナンス
検索語: `MU`
- 11/19 24/7 Wall St. | Seagate and Western Digital Climb 4% Despite Tech Profit-Taking After Anthropic’s IPO Debut; SanDisk Edges Higher
- 11/19 GlobeNewswire | Micron Technology to Report Fiscal First Quarter Results on December 17, 2026
- 11/19 GuruFocus.com | Micron CEO Has a Stark Message for Memory Chip Buyers

# 実行上の注記（Routineの記録）
- 実行環境に matplotlib がなく、最初の `prepare` で6銘柄の数値データが取得不可になった。インストール後、5銘柄（AMD CRM NBIS SMCI SWKS）を取り直した。**SNDK（保有）は取り直しでも取得不可のため、著者には送っていない（著者の判定なし）。**
- 著者へのプロンプトが8000文字の上限を超えたため、著者に送るテーマの状態から「グループごとの悪いニュースの流れ」の節（記録だけの項目）を除いて送った。ニュースは各銘柄で上限まで縮められている（SWKSの悪材料は「ニュース記述省略のため判定不能」）。このレポートのスキャンの節には元のまま全文が残っている。
