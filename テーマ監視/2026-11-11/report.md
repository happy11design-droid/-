# テーマ監視 2026-11-10

# 判定のまとめ（ルールの判定と著者の判定を分けて表示）

- **ルールの判定**: 採用した売買ルール（スクリプト）が数値で決めたもの。損切りは買値の15%下の逆指値（日中に届けばその場で売れる）。
- **著者の判定**: ノートブックの著者の回答。買いは注文を止める理由があるときだけ【様子見】、保有はルールより早く手じまう理由があるときだけ【売り】。根拠は下の「著者の回答（全文）」。
- 2つが食い違うときに、どちらに従うかはユーザーが決める。

- **テーマ全体の急落（S2・記録だけ）: あり（S2）**（SOXが直近60取引日の最高値から -24.4%）。S2の日の順張りの候補には「S2なら見送る形」と付ける（売買のルールは変えない。記録してから採用を決める。2026-10-14）

- **特殊な下げ（記録だけ）: あり（特殊な下げ）**（2026-10-16から）（SOXが直近60取引日の最高値から -24.4%、前の1年の大きな上げ・雇用の弱さ・物価の再加速のうち 2つ）。1995年〜では、この形の後にSOXの下げが長引くことが多かった（後知恵を含む）。売買のルールは変えない（2026-11-03）

## 保有銘柄

| 銘柄 | ルール | 損益 | 時間外 | ルールの判定 | ルールの判定の理由 | 著者の判定 |
|---|---|---|---|---|---|---|
| SNDK | ルール外（ユーザーの判断。この日はどのルールの合図もなし） | -37.3% | -0.4% | **売り** | 終値 859.99 が損切り価格 1165.61 以下 | 【未判定】（） |
| AMD | ボリンジャーIII | -6.3% | -0.3% | 保有継続 | 損切り 467.47（終値から -9.3%） | 【保有継続】（ボリンジャー） |

## 候補の判定（並びは上の「買う順番」の表と同じ）

- 並びは上の「買う順番」の表と同じ（RSの高い順。勝率の高い順ではない）。注文の値段・株数・逆指値は上の表を見る。勝率・1回平均は、そのルールの過去の成績（後知恵なしの監視銘柄・2015年〜の全部の合図）。
- 空き枠: 3（同時保有4銘柄まで。保有2、うちルールの売り1）。著者が【様子見】の候補を見送るかはユーザーが決める。

| 順 | 銘柄 | ルール | 過去の勝率 | 過去の1回平均 | RS | 時間外 | ルールの判定 | 著者の判定 |
|---|---|---|---|---|---|---|---|---|
| 1 | ROK（ロックウェル・オートメーション） | 逆張り: 急落の底（担当: コナーズ）（指値の3日目） | 65% | +2.1% | 22 | -0.0% | 買い（指値 368.34、3取引日まで） | 【様子見】（コナーズ） |
| 2 | NVDA（エヌビディア） | 逆張り: 急落の底（担当: コナーズ） | 65% | +2.1% | 8 | +0.4% | 買い（指値 165.51、3取引日まで） | 【様子見】（コナーズ） |

- 時間外: 前の取引日の引けから、引け後（米国東部時間16〜20時）の最後の値までの騰落率（Yahoo。±5%以上は太字）。寄り付きの値段は、表の注文の目安（前日の終値で計算）から大きくずれることがある。原因の見出しは「ニュースの見出し」の節。

# 著者の回答（全文）

## 0_テーマの局面_ワインスタイン

1. **テーマ全体の局面**: 【ステージ3】（30週線が横ばい化し、指数が線を下回る天井圏の様相 [1, 2]。第2章）

2. **グループごとの局面**:
- 半導体｜ステージ3｜30週線横ばい・線より下 [1, 2]
- 半導体製造装置・材料・設計ソフト・計測｜ステージ3｜30週線横ばい・線より下 [1, 2]
- AIサーバー・ストレージ・メモリ・端末｜ステージ3｜30週線横ばい・線より下 [1, 2]
- 光・通信・ネットワーク｜ステージ3｜30週線横ばい・線より下 [1, 2]
- データセンターの電力・冷却・部品・受託製造・建設｜ステージ3｜30週線横ばい・線より下 [1, 2]
- AIプラットフォーム・クラウド｜ステージ3｜30週線横ばい・線より下 [1, 2]
- AIソフト・セキュリティ・ITサービス｜ステージ2｜30週線上昇・線より上 [2, 3]

3. **転換の兆し**: 出ている。主要な兆候として**30週移動平均線の上昇停止・水平化と指数の下抜け** [1, 4]（第2章、第7章）、および**市場平均（S&P500）に対するレラティブ・ストレングス（RS）の悪化** [5, 6]（第1章、第4章）が該当する。なお、50日線乖離、急落基準（S2）、ニュース見出し等はマニュアルに規定なし [7]。

4. **テーマの外**: **判定不能**（提示データでヒートマップが省略されており判定材料がないため） [7]。

（全体の版が空の応答だったため、1〜2節だけの短い版で送り直した回答。ヒートマップ・急騰急落・ニュースは渡していない）

## 1_コナーズ_prompt_1

## ROK
1. **投資判断**: 【様子見】（200日線下のため）
2. **止める理由の確認**:
- 本が禁じる形・状況｜あり｜株価が200日線の下側（第4章）[1]
- 避けるべき時期（決算など）｜なし｜決算86日後。月初外（第11章、マニュアルに規定なし）[2, 3]
- 悪材料｜なし｜見送り規定なし（第2・3章、マニュアルに規定なし）[4, 5]
3. **現状パターンと価格**:
- 現状パターン: A（指値待ち）
- 本日の発注: なし（見送り）
4. **注意点**: 200日線下では買いを見送り白紙に戻す（第4章）[1]。

## 1_コナーズ_prompt_2

## NVDA
1. **投資判断**: 【様子見】（200日線下のため買い見送り）
2. **止める理由の確認**:
   - 本が禁じる形・状況｜あり｜第4章（終値168.89が200日線204.54の下側）[1, 2]
   - 避けるべき時期（決算など）｜なし｜マニュアルに規定なし（決算回避の規定なし）[3]
   - 悪材料｜なし｜第2章・第3章（悪材料は織り込み済みとする）[4, 5]
3. **現状パターンと価格**:
   - 現状パターン: A（急落条件成立だが前提不適合）
   - 本日の発注: 見送り（発注なし）
4. **注意点**: 200日線下での買いは歴史的大暴落を招くため厳禁 [2]。

## 1_ボリンジャー_prompt_1

## AMD [1]
1. **投資判断**: 【保有継続】早期手じまう理由なし [2]。
2. **止める理由の確認**:
- 本が禁じる形・状況｜なし｜天井・乖離等の危険形なし（第13・17章） [2, 3]
- 避けるべき時期（決算など）｜なし｜次回決算2/2で遠い（第4章） [4]
- 悪材料｜なし｜固有の悪材料なし（11/10）
3. **現状パターンと価格**:
- 現状パターン: 保有中
- 保有中: 売りの予約注文: 指値 604.95（現在値比 +17.4%） [2]
4. **注意点**: 本に大陰線手じまい規定はなく、スクリプト側の条件に従うこと [5]。

# スキャン（数値と事実）


- 監視銘柄 87（判定できたのは 87）。
- この一覧は数値と事実だけ。売買の判断は著者のノートブックが行う。

## 1. テーマ（グループ）の強さ

| グループ | 銘柄数 | 1週 | 1カ月 | 3カ月 | 3カ月の順位 | 50日線より上の銘柄の割合 | グループ指数の30週線の局面（線との乖離、4週前からの線の傾き） |
|---|---|---|---|---|---|---|---|
| 半導体 | 16 | -4.0% | -8.4% | -16.5% | 4位 | 25% | 横ばい（-11.0%、+5.0%） |
| 半導体製造装置・材料・設計ソフト・計測 | 9 | -2.5% | -19.5% | -17.8% | 5位 | 33% | 横ばい（-13.9%、+1.3%） |
| AIサーバー・ストレージ・メモリ・端末 | 9 | -11.5% | -30.5% | -26.1% | 6位 | 11% | 横ばい（-12.3%、+6.8%） |
| 光・通信・ネットワーク | 9 | -4.2% | -23.9% | -31.8% | 7位 | 11% | 横ばい（-16.2%、+1.3%） |
| データセンターの電力・冷却・部品・受託製造・建設 | 19 | -5.0% | -8.9% | -11.9% | 3位 | 21% | 横ばい（-9.2%、+0.5%） |
| AIプラットフォーム・クラウド | 11 | -2.2% | -13.7% | +1.3% | 2位 | 45% | 横ばい（-4.9%、+1.4%） |
| AIソフト・セキュリティ・ITサービス | 14 | -3.5% | -8.7% | +1.8% | 1位 | 29% | 上昇（+6.0%、+4.9%） |

## 2. テーマ全体の状態と早めの警告

- 市場全体の30週線による局面: S&P500指数 **上昇**／NASDAQ100指数 **横ばい**（急落の底で買うルールは、過去の検証で下落相場で特に強く、横ばいの相場では負けていた）
- **2倍ETFを使う局面（案1、2026-10-13 採用）: S&P500の20週線（100日線）で 横ばい** → 新しく買う銘柄は、2倍ETFのある銘柄も元の株で買う（保有中のETFはそのまま）（SPY 749.92、100日線 758.52、20日前の線 755.07。上昇＝線より上かつ線が上向き）
- **テーマ全体の急落（S2、記録だけ。売買のルールは変えない）: あり（S2）**（SOX 9998.33、直近60取引日の最高値 13217.82 から -24.4%。S2＝最高値から−10%以上）。S2のときに「順張りの新しい買いだけ止める」形を記録で比べる（2026-10-14 ユーザー決定。バックテストでは年率は上がったが2つの期間ではどちらも少し下回ったため、記録してから採用を決める。`バックテスト結果/テーマ全体の急落を検知して手じまう・買いを止める.md`）
- **グループごとの悪いニュースの流れ（記録だけ。売買のルールは変えない。2026-10-28〜2026-11-10）**: 会社の名前と悪い言葉（格下げ・目標株価の引き下げ・見通しの引き下げ・予想未達・急落・信用・訴訟・輸出規制など）の両方がある見出しの数（Googleニュース、`tools/news_headlines.py`）。10取引日の1銘柄あたりが一番多いグループに印。2026年7〜11月の確かめでは、印のグループの合図は10月は成績が悪かった（1回平均 −10.6%、ほか −5.6%）が、7〜9月は逆に良かった（+11.6%、ほか +6.7%）（`バックテスト結果/実際の運用の期間の確認_2026-10-23/グループの悪いニュースの流れ.md`。2026-11-04）

| グループ | 悪いニュース 直近5取引日 | その前の5取引日 | 10取引日の1銘柄あたり | 良いニュース 10取引日（1銘柄あたり） | 印 |
|---|---|---|---|---|---|
| 光・通信・ネットワーク（9） | 14件 | 7件 | 2.3 | 8件（0.9） | **悪いニュースが続いている** |
| 半導体（16） | 12件 | 9件 | 1.3 | 25件（1.6） |  |
| AIサーバー・ストレージ・メモリ・端末（9） | 5件 | 5件 | 1.1 | 35件（3.9） | **良いニュースが多い** |
| AIプラットフォーム・クラウド（11） | 3件 | 9件 | 1.1 | 2件（0.2） |  |
| AIソフト・セキュリティ・ITサービス（14） | 5件 | 6件 | 0.8 | 16件（1.1） |  |
| データセンターの電力・冷却・部品・受託製造・建設（19） | 3件 | 6件 | 0.5 | 23件（1.2） |  |
| 半導体製造装置・材料・設計ソフト・計測（9） | 1件 | 1件 | 0.2 | 0件（0.0） |  |

印のグループ（光・通信・ネットワーク）の最近の見出し: 2026-11-09 S&P: Akamai Technologies Inc. Downgraded to '（Moomoo）／2026-11-09 Moody’s and S&P downgrade Akamai on debt-fueled AI infrastructure buildout（Investing.com）／2026-11-07 Here’s Why Lumentum (LITE) Was Downgraded（Yahoo Finance）

良いニュースが多いグループ（AIサーバー・ストレージ・メモリ・端末）の最近の見出し: 2026-11-10 iPhone 18 and iPhone 18e leaks suggest Apple has a battery upgrade up its sleeve（Stuff South Africa）／2026-11-10 Apple Hospitality REIT (NYSE:APLE) Stock Price Target Raised at Cantor Fitzgerald（MarketBeat）

- **特殊な下げ（記録だけ。売買のルールは変えない）: あり（特殊な下げ）**（2026-10-16から）。SOX は直近60取引日の最高値から -24.4%（−15%以下が条件）、●A 前の1年の上げ +118.5%（+80%以上）、・B 雇用の伸び 137千人/月（2026-10まで。10万人未満）、●C 物価 4.0%（2026-09。3か月前 3.7%。3.5%以上で再加速）＝2つ（2つ以上が条件）。1995年〜でSOXが−15%以下かつ条件2つ以上の日は、120日後にSOXが下だったのが69%・250日後が70%（中央値 −33%）、AI以外の8業種の平均は250日後 −7%。ただし条件は過去を見て選んだもの（条件が2つ以上の局面は約5回）で、2026年7〜9月にこの間テーマを買わないと、その後の戻りを逃して2026年の成績は下がった（`バックテスト結果/実際の運用の期間の確認_2026-10-23/特殊な下げと過去の似た下げ.md`。2026-11-03）
- テーマ指数（監視銘柄の等金額平均）の30週線による局面: **横ばい**（上昇＝線より上かつ上向き、下落＝線より下かつ下向き、それ以外＝横ばい。ワインスタインのステージの近似）
- テーマ指数と50日線: 50日線より下（乖離 -9.7%）
- S&P500に対する相対的な強さ: 50日平均より下（S&P500より弱い）
- 監視銘柄のうち50日線より上の割合: 25%
- 警告（割合が40%未満かつテーマ指数が50日線より下）: **出ている**
- 参考（バックテスト）: 30週線の「下落」は高値から10〜33%下げた後に出る遅い判定。50日線・割合・相対的な強さは高値から2〜8%で出るが、誤報が年15回以上ある。警告中に新しい買いを止めると、押し目買い（ボリンジャーIII）の成績は大きく下がった（`バックテスト結果/テーマ監視銘柄・直近3年.md` 11・12節）。

## 3. ヒートマップ（Finviz、全米の業種別の騰落率）

3カ月の騰落率の上位15業種（テーマの外で強くなっている業種の確認用）:

| 順位 | 業種 | 1週 | 1カ月 | 3カ月 | 6カ月 | 1年 |
|---|---|---|---|---|---|---|
| 1 | Health Information Services | +2.7% | +9.2% | +25.4% | +60.8% | +13.6% |
| 2 | Advertising Agencies | +39.3% | +34.2% | +19.7% | -11.0% | -28.6% |
| 3 | Lodging | +3.8% | +15.4% | +17.8% | +18.8% | +38.2% |
| 4 | Medical Distribution | +7.0% | +12.0% | +17.4% | +43.5% | +19.2% |
| 5 | Paper & Paper Products | +7.0% | +14.4% | +17.1% | +9.5% | +6.1% |
| 6 | Consumer Electronics | +5.0% | +2.4% | +15.2% | +18.2% | +27.3% |
| 7 | Real Estate - Diversified | +8.6% | +12.9% | +15.1% | +18.9% | +16.0% |
| 8 | Diagnostics & Research | +0.1% | +5.5% | +15.0% | +49.8% | +25.7% |
| 9 | REIT - Hotel & Motel | +1.8% | +14.7% | +14.8% | +30.3% | +51.7% |
| 10 | Financial Data & Stock Exchanges | +1.7% | +11.0% | +13.6% | +10.4% | +4.4% |
| 11 | Insurance - Diversified | +4.3% | +11.9% | +13.3% | +19.1% | +16.7% |
| 12 | Medical Care Facilities | +6.8% | +9.2% | +13.2% | +20.9% | +19.9% |
| 13 | Insurance - Reinsurance | +3.4% | +7.9% | +13.2% | +23.0% | +35.9% |
| 14 | Household & Personal Products | +4.2% | +9.8% | +12.5% | +17.6% | +13.2% |
| 15 | Drug Manufacturers - General | +2.4% | +11.8% | +12.4% | +26.3% | +38.4% |

テーマの業種の順位（3カ月、全144業種中）: Semiconductors 132位、Semiconductor Equipment & Materials 141位、Computer Hardware 143位、Communication Equipment 134位、Electronic Components 135位、Software - Infrastructure 60位、Software - Application 62位、Internet Content & Information 114位

## 4. 急騰・急落した銘柄（前日比±5%以上、または出来高が50日平均の2倍以上）

原因のニュースをサブエージェントが調べ、候補・保有銘柄の判定材料として著者に渡す。急騰・急落そのものは売買の合図にしない（後知恵のないS&P500全体のバックテストでは、急騰の翌日に買うルールは年率7%、急落の翌日に買うルールは年率9〜10%で、採用した3つのルールより優れていなかった）。

| 銘柄 | グループ | 前日比 | 出来高（50日平均の倍） | 終値 | 50日線 | RS | 局面 |
|---|---|---|---|---|---|---|---|
| NVDA | 半導体 | -5.5% | 3.5倍 | 168.89 | 下 | 8 | 下げ |
| NBIS | AIプラットフォーム・クラウド | -5.3% | 1.0倍 | 134.00 | 下 | 14 | 下げ |
| AKAM | 光・通信・ネットワーク | +4.3% | 4.2倍 | 83.71 | 下 | 3 | 下落相場 |
| GEV | データセンターの電力・冷却・部品・受託製造・建設 | -3.9% | 2.1倍 | 797.04 | 下 | 21 | 下落相場 |

- 局面（判定式はClaudeが置いたもの）: **上昇相場**＝終値 > 50日線 > 200日線、50日線が20取引日前より2%以上高い、ADX(14) ≧ 20／**下落相場**＝終値 < 50日線 < 200日線、50日線が20取引日前より2%以上低い、ADX(14) ≧ 20／**上げ**＝それ以外で終値が50日線より上、かつ50日線が10取引日前より上か20日線が5取引日前より上／**下げ**＝それ以外で終値が50日線より下、かつ50日線が10取引日前より下か20日線が5取引日前より下（急な下げの初めは50日線がまだ上向きのため20日線でも見る）／**レンジ**＝どれにも当たらない（2026-11-05 から5つ。それまでは上昇相場とレンジの2つだけで、下げている銘柄もレンジと出ていた）。

## 4-2. 監視外の注目銘柄（S&P500・NASDAQ100のうち監視銘柄に入っていない銘柄）

条件: 流動性（株価5ドル以上・50日平均出来高25万株以上）があり、(a) 前日比+8%以上かつ出来高が50日平均の2倍以上、または (b) 終値が直前1年の最高値（終値）を上回り、RS≧90。RSの高い順に5銘柄（ニュースを調べる）。監視銘柄に入れるかはユーザーが決める。

| 銘柄 | 種類 | 前日比 | 出来高（50日平均の倍） | RS | 終値 |
|---|---|---|---|---|---|
| HUM | 1年の高値更新 | +3.5% | 1.5倍 | 99 | 438.06 |
| VTRS | 1年の高値更新 | +1.8% | 1.2倍 | 97 | 20.85 |
| LLY | 1年の高値更新 | +1.4% | 1.1倍 | 95 | 1432.29 |
| HAS | 1年の高値更新 | +0.7% | 1.2倍 | 95 | 121.82 |
| KDP | 1年の高値更新 | +1.8% | 1.2倍 | 94 | 37.59 |

- ほかに5銘柄: CPAY（1年の高値更新、RS 92）、GPN（1年の高値更新、RS 92）、CAH（1年の高値更新、RS 91）、AIZ（1年の高値更新、RS 90）、TTWO（急騰、RS 28）

## 5. 保有銘柄の手じまい条件（`新分析ツール/保有銘柄.md`）

| 銘柄 | ルール | 買った日 | 買値 | 終値 | 損益 | 損切り価格（買値の15%下、逆指値） | ルールの手じまい条件 | 出来高2倍の大陰線（買った後の直近5日） | 次回決算予定日 |
|---|---|---|---|---|---|---|---|---|---|
| SNDK | ルール外（ユーザーの判断。この日はどのルールの合図もなし） | 2026-10-21 | 1371.30 | 859.99 | -37.3% | 1165.61 | **損切り価格を下回った** ルールが不明（保有銘柄.md の「ルール」を確認） | **あり** 2026-11-05（実体 ATRの1.6倍・出来高3.3倍） | 2026-10-29 |
| AMD | ボリンジャーIII | 2026-10-21 | 549.97 | 515.21 | -6.3% | 467.47 | **出来高2倍の大陰線が 2026-11-05 に出た**（まだ持っていれば、次の寄り付きで全部売る） 売りの指値: 上部バンド 604.95（今夜この値に置き直す。届いた日に売れる）（2倍ETF AMUU で持っている場合も、判定は元の株 AMD の値段） | **あり** 2026-11-05（実体 ATRの1.5倍・出来高3.3倍） | 2027-02-02 |

- 出来高2倍の大陰線: 実体（始値−終値）が前日までのATR(14)の1.5倍以上、終値がその日の値幅の下25%以内、出来高が前日までの50日平均の2倍以上の日。**押し目（ボリンジャーIII）・急落の底の保有では売りのルール**: 出たら翌日の寄り付きで全部売り、空いた枠で次の合図を買う（2026-10-02 ユーザー決定。`バックテスト結果/やり直し_売りの合図の組み合わせ.md`。乱数3組とも年率が約+2ポイント、最大下落率もやや下がった）。ミネルヴィニ・新高値V2の保有では事実の表示（順張りに足しても良くならなかった）。

- 半分売りの合図（ミネルヴィニ・新高値V2の保有だけ）: 反転のローソク足（かぶせ線・弱気の包み足・宵の明星・流れ星）＋出来高が50日平均の1.5倍以上＋RSI(14)が前日か当日に70以上。買った後に最初に出た日の翌日の寄り付きで半分売り、残り半分は50日線割れ・損切り15%まで持つ（2026-10-01 ユーザー決定。`バックテスト結果/半分だけ売るとオニールの空き枠.md`）。

- かぶせ線（ミネルヴィニ・新高値V2の保有だけ）: 上昇中の陽線の翌日に、前日の高値より上で寄り付き、前日の陽線の真ん中より下（前日の始値より上）で引けた日。翌日の寄り付きで全部売り、空いた枠で次の合図を買う。半分売りより優先する（2026-10-01 ユーザー決定。`バックテスト結果/2倍ETFで売って買い直す.md`。順張りの売買の25%で出て、1回平均+2.0%、年率 21.4%→26.4%）。

## 5-2. 前日（2026-11-09の引け）の【買い（予約）】の確認

前日の【買い（予約）】はなし。

## 6. 候補（採用したルールの条件が成立＝A。予約（B）は2026-10-25から注文せず、節6-3に参考の表示だけ）

建玉の目安: 同時保有4銘柄まで、1銘柄に資金の25%（資金÷4）、損切りは買値の15%下（ユーザー決定 2026-09-29）。

パターン: A＝最新の足で採用ルールの条件が成立（押し目・ミネルヴィニ・新高値V2は翌日の寄り付きで成行、急落の底は合図の日の終値の2%下に指値で3取引日待つ。2026-11-03 ユーザー採用）。条件の成立が目前の銘柄（B）は、予約の注文をやめたので節6-3に参考として出す（2026-10-25 ユーザー決定）。

| 銘柄 | グループ | パターン | 種類 | ルールの過去の成績 | 終値 | 前日比 | RS | 50日線の傾き | 局面 | 当てはまった条件 | 次回決算予定日 | 注文の目安 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ROK | データセンターの電力・冷却・部品・受託製造・建設 | A | 逆張り: 急落の底（担当: コナーズ）（指値の3日目） | 2位（勝率65%・1回平均+2.1%） | 397.16 | +2.0% | 22 | -1.2% | 下げ | 2026-11-06の合図: 直前5日の最高値（終値）から-15.8%下落（−15%以上）、RSI(2)=3.2（≦10）、急落の前は50日線＞200日線。市場全体の局面: S&P500 上昇／NASDAQ100 横ばい。その後まだ指値に届かず、終値は5日線以下 | 2027-02-04（86日後） | 指値買い 368.34（合図の日 2026-11-06 の終値 375.86 の2%下。今日が最後の日。届かなければ見送り、途中で終値が5日線を上回ったら取り消す）。損切り: 約定した値段の15%下。手じまい: 終値が5日線（今日 397.46）を上回った翌日の寄り付き（コナーズ）。**株数の目安: 6株**（2,384ドル÷368.34。注文の価格）、購入金額 約2,210ドル |
| NVDA | 半導体 | A | 逆張り: 急落の底（担当: コナーズ） | 2位（勝率65%・1回平均+2.1%） | 168.89 | -5.5% | 8 | -2.2% | 下げ | 直前5日の最高値（終値）から-18.3%下落（−15%以上）、RSI(2)=7.8（≦10）、急落の前は50日線＞200日線。市場全体の局面: S&P500 上昇／NASDAQ100 横ばい | 2026-11-17（7日後）**決算が近い** | 指値買い 165.51（合図の日 2026-11-10 の終値 168.89 の2%下。今日から3取引日。届かなければ見送り、途中で終値が5日線を上回ったら取り消す）。損切り: 約定した値段の15%下。手じまい: 終値が5日線（今日 183.19）を上回った翌日の寄り付き（コナーズ）。**元の株で買う**（2倍ETF NVDU のある銘柄だが、S&P500が20週線で「横ばい」の局面のため。案1）。**株数の目安: 14株**（2,384ドル÷165.51。注文の価格）、購入金額 約2,317ドル |

- 局面（判定式はClaudeが置いたもの）: **上昇相場**＝終値 > 50日線 > 200日線、50日線が20取引日前より2%以上高い、ADX(14) ≧ 20／**下落相場**＝終値 < 50日線 < 200日線、50日線が20取引日前より2%以上低い、ADX(14) ≧ 20／**上げ**＝それ以外で終値が50日線より上、かつ50日線が10取引日前より上か20日線が5取引日前より上／**下げ**＝それ以外で終値が50日線より下、かつ50日線が10取引日前より下か20日線が5取引日前より下（急な下げの初めは50日線がまだ上向きのため20日線でも見る）／**レンジ**＝どれにも当たらない（2026-11-05 から5つ。それまでは上昇相場とレンジの2つだけで、下げている銘柄もレンジと出ていた）。

- 2倍ETF: 2倍ETFがある銘柄（ユーザーがムームー証券で買えることを確認した38銘柄のうち、目減りが年15%未満のもの）は、株の代わりに2倍ETFを買う（2026-10-04 ユーザー決定。`バックテスト結果/2倍ETFを使う決まり.md`。年率 約27%→約33%、確定した損益だけの最大下落率 約30%→約31%、含み損込みは約33%→約45%）。買う金額は株と同じ（資金の25%）。合図・損切り（元の株の買値の15%下＝ETFでは約30%下）・手じまいはすべて元の株の値段で判定する。指値・逆指値はETFの値段に直して置く。どのETFかは `新分析ツール/2倍ETFの対応表.json`（売買代金が1日500万ドル以上で、直近1年の目減りが一番小さいもの）。**2倍ETFで買うのは、S&P500が20週線（100日線）で「上昇」の局面のときだけ。横ばい・下落の局面では元の株で買う**（案1、2026-10-13 ユーザー採用。買う日に決め、買った後は局面が変わってもそのまま持つ。`バックテスト結果/流れ（市場の局面）を使う形.md`）。

- ルールの過去の成績: 今の売りのルールで、後知恵なしの監視銘柄・2015年〜の全部の合図の1回ごとの成績（2026-10-02計算、`新分析ツール/バックテスト結果/ルールごとの成績.md`）。順位は1回平均（1回の売買で平均いくら増えるか）の順。表はパターン（A→B）ごとに、この順位の良い順に並べた（表示の順番だけ。買う順番・件数の上限は変えていない。候補の選び方を変えても成績は変わらなかったため。2026-10-02 ユーザーの指示）。著者には渡さない。

- 悪いニュースが続いているグループ（光・通信・ネットワーク）の候補（記録だけ。売買のルールは変えない。著者には渡さない）: なし

- 候補の数: 空き枠3（同時保有4銘柄まで。保有2、うち今日ルールの売りが成立1）＋予備2件まで表に出した（2026-10-25 ユーザー決定）。省いた候補はない。

- テーマの外の候補（グループが「テーマの外」）: 監視銘柄の候補で枠が埋まらないときに使う（監視銘柄の候補を先に買う）。S&P500の今の構成銘柄のうち監視銘柄でない銘柄から、RS≧90・30週線が上向きで終値がその上・業種の3カ月の強さが上位20%の18銘柄を調べ、空き枠2つ分まで出した。バックテストでは、テーマの外の強い銘柄で空き枠を埋めると、テーマが弱い時期の成績が支えられた（`バックテスト結果/半導体・AIに特化した場合.md`。2026-10-01 ユーザー決定）。

- RS≧80の押し目（ボリンジャーIII）は、バックテストで成績がより安定していた（PF3.27、最大下落20%）。

## 6-3. 参考: 条件の成立が目前の銘柄（予約は注文しない・著者には送らない）

2026-10-25 ユーザー決定: 予約（逆指値・指値）の注文はやめ、参考の表示だけにする。毎朝のツールと同じ条件・値段で予約の約定をバックテストに入れると、どの形も年率が下がった（後知恵なし 35.7%→30.7〜34.2%、87銘柄 45.6%→34.2〜42.6%。`バックテスト結果/点検_2026-10-25/`）。引けで条件がそろえば、翌朝の節6に買いの候補（A）として出る。各ルールでRSの高い順に2件まで。

| 参考の銘柄 | グループ | 種類 | 終値 | 前日比 | RS | 当てはまった条件 | 条件がそろう目安の価格（注文はしない） |
|---|---|---|---|---|---|---|---|
| WDAY | AIソフト・セキュリティ・ITサービス | ボリンジャー メソッドIII（%bが0.05未満に近い） | 188.89 | -0.7% | 75 | %b=0.118（0.05まであと少し）、21日II%=+0.009（>0） | 187.08（この値より下で引けると翌朝の買いの候補（A）。目安） |
| SHOP | AIソフト・セキュリティ・ITサービス | ボリンジャー メソッドIII（%bが0.05未満に近い） | 146.61 | -3.6% | 59 | %b=0.138（0.05まであと少し）、21日II%=+0.012（>0） | 142.81（この値より下で引けると翌朝の買いの候補（A）。目安） |


# ニュース（サブエージェントの調査）

# ニュース（2026-11-10 引け時点）

## テーマ全体の下げの原因
（headlines.md と銘柄名の検索で確認）
- きっかけ: 中間選挙で民主党が大勝し、データセンター規制への懸念からAI・半導体・電力株が11/5に急落した（CNBC 11/6、Fortune 11/5）。呼び名は「民主党大勝ショック」（四季報オンライン 11/10）と「midterm shock」（CNBC 11/6）。
- 広がった先: NVIDIAのCEOに対する取締役会の調査（11/8〜）と、SoftBankのデータセンター向け発電設備の37億ドルの損失（11/10）で、電力株（GEV・VRT）が下げた。
- 信用: 「AI debt faces pressure」（Reuters 11/10）、「半導体大手のCDSがクラウド企業を上回った」（Moomoo 11/10）、Akamaiの格下げ（11/9）。
- 市場全体: 10月CPIが予想を上回った（総合+0.4%、予想+0.3%）。10年債利回りは約5%（CNBC・Benzinga 11/10）。S&P500は約−0.4%、NASDAQは約−0.7%（investingLive 11/10）。

## 引け後・時間外の材料
- CoreWeaveが決算を発表し、時間外で+6〜8%と報じられた（TradingView 11/10）。Yahooの値は−3.1%で合わない。
- ±5%以上動いた監視銘柄はなし。保有・候補の銘柄は、時間外の材料の見出しが見つからなかった。

## NVDA
- 11/8 フアンCEOが不倫を認め、取締役会が「中国のスパイとされる女性」との関係を調べ始めた（Bloomberg 11/8）。
- 11/9に−4.3%、11/10はCPIも重なって−5.5%（CNBC 11/10）。
- 次回決算: 11/17の引け後（10/28に公式発表）。
- 悪材料: あり（CEOへの調査）

## NBIS
- 11/10 −5.3%: Microsoftがネオクラウドとの提携を縮小するという弱気の記事が出た（Investing.com・Seeking Alpha 11/10）。
- 決算: 11/12の寄り付き前（MarketBeat）。
- 悪材料: あり（顧客が離れるという指摘。会社の発表ではない）

## AKAM
- 11/9 22億ドルの転換社債を発表し急落。S&Pは投機的格付けに、Moody'sは投資適格の最低ランクに引き下げた（レバレッジが7倍を超える見込み。Yahoo 11/9）。
- 11/10 +4.3%（出来高4.2倍）: 転換条件から希薄化が小さいとみられて戻した（StreetInsider・Investing.com 11/10）。HSBCが目標株価を91ドルに下げた（MT Newswires 11/10）。
- 悪材料: あり（格下げ・転換社債）

## GEV
- 11/10 −3.9%（寄り付きで一時約−10%）: SoftBankが発電設備で37億ドルの損失を計上し、オハイオの計画を見直す（Seeking Alpha・TIKR 11/10）。
- GEVは「影響はない」と回答（GuruFocus 11/10）。
- 悪材料: あり（大口の顧客の計画の見直し）

## ROK（候補）
- 11/5 第4四半期: EPSは予想を上回ったが、関税の返金で売上が予想を下回り−13%（Yahoo・TIKR 11/5）。
- 次回決算（2/4）の公式発表は確認できず。
- 悪材料: あり（売上が予想を下回った）

## AMD（保有）
- 11/9 Google Cloudとの契約で+13%（Seeking Alpha）。11/10 Oppenheimerが格上げ（GuruFocus）。
- 悪材料: 確認できず

## SNDK（保有）
- 11/5 決算は強かったが、AI株の売りで−20%（TheStreet 11/5）。
- 悪材料: 確認できず

## 監視外の注目銘柄
- HUM（医療保険）: 2026年のEPSの見通しの下限を9.50ドルに上げ、がん治療の新しい仕組みを発表して+3.5%（Benzinga 11/10）。Jefferiesが目標株価を520ドルに上げた（marketscreener 11/10）。
- VTRS（ジェネリック医薬品）: 第3四半期に見通しを上げ、Paciraを買収（Yahoo 11/5）。Jefferiesが目標株価を22ドルに上げた（11/6）。
- LLY（医薬品）: 決算の後に上昇（Yahoo 11/5）。11/10の原因は見つからなかった。
- HAS（玩具）・KDP（飲料）: 11/10の原因となるニュースは見つからなかった。

# ニュースの見出し（プログラムが自動で取得）

- Googleニュース（日付を指定）とYahooファイナンスの見出しを `tools/news_headlines.py` が自動で並べたもの。日付は米国東部時間の配信日（引け後の記事は翌日付）。原因の判断・売買の判断はしていない。
- 調べた銘柄の選び方: ①保有 ②今日の候補 ③時間外に±5%以上動いた監視銘柄 は全部、④引けまでに大きく動いた銘柄（1週で±5%のグループの上位3・1日で±7%）は合計12銘柄まで。
- 1週で−5%以下のグループ: AIサーバー・ストレージ・メモリ・端末（-11.5%）、データセンターの電力・冷却・部品・受託製造・建設（-5.0%）
- 1週で+5%以上のグループ: なし

## 0. 時間外（引け後）の値動き（2026-11-10 の引けから、Yahoo。±3%以上の監視銘柄と、保有・候補は全部）

| 銘柄 | 区分 | 引け | 時間外 | 騰落率 |
|---|---|---|---|---|
| GLW | 監視 | 112.14 | 117.16（16:58 ET） | +4.5% |
| CRWV | 監視 | 48.73 | 47.22（17:23 ET） | -3.1% |
| SNDK | 保有 | 859.70 | 856.28（17:23 ET） | -0.4% |
| NVDA | 候補 | 168.79 | 169.43（17:23 ET） | +0.4% |
| AMD | 保有 | 515.42 | 513.66（17:23 ET） | -0.3% |
| ROK | 候補 | 397.22 | 397.16（16:47 ET） | -0.0% |

## 1. 市場全体（2026-11-10）

### 市場全体（英語のまとめ記事）
検索語: `stocks Wall Street close Nasdaq`
- 11/10 The Washington Post | Opinion | Wall Street is becoming the world’s stock market
- 11/10 Reuters | Wall St ends lower as hot inflation data, Fed comments heighten rate worries
- 11/10 Investor's Business Daily | Stock Market Today: Stock Market News And Analysis
- 11/10 Bergen Record | What's closed on Veterans Day? Are banks, post office or stock market open?
- 11/10 24/7 Wall St. | Stock Market Today: Hotter CPI Reading Hasn’t Deterred Stocks From Rising

### 市場全体（Stock Market Today）
検索語: `"stock market today"`
- 11/10 Benzinga | Hot CPI Pushes 10-Year Yield to 5%, Nvidia Sinks 6%: Stock Market Today
- 11/10 Yahoo Finance | Stock market today: Dow, S&P 500 slip after CPI data raises Fed rate-hike bets
- 11/10 Benzinga | Stock Market Today: Dow Futures Rise, S&P 500 and Nasdaq 100 Futures Fall as Trump Signals Iran War to En
- 11/10 Yahoo Finance | Wall Street's $1.6 trillion rebound may look like a bottom — history says it often isn't: Chart of the Day

### 市場全体（日本語のまとめ記事）
検索語: `米国株式市場 OR NY株`
- 11/10 Reuters | 米国株式市場＝反落、インフレ指標とＦＲＢ高官発言受け利上げ観測高まる
- 11/10 Yahoo!ニュース | 米国株式市場＝反落、インフレ指標とＦＲＢ高官発言受け利上げ観測高まる（ロイター）
- 11/10 OANDA証券 | ＮＹ株反落、１５７ドル安

### 半導体・AI株（英語）
検索語: `chip stocks OR semiconductor stocks OR AI stocks`
- 11/10 Yahoo Finance | Goldman Sachs calls chip stocks 'oversold.' Here are the names it says to buy.
- 11/10 CNBC | 'Markets bottom on bad news' maxim rings true as chip stocks rally amid Nvidia scandal
- 11/10 Investor's Business Daily | Chip Stocks To Watch And Semiconductor Industry News
- 11/10 MarketWatch | Ignore the wild swings in chip stocks until they reach these ‘lines in the sand’
- 11/10 Barron's | Chip Stocks and Nvidia Trade Places as Normal Service Resumes

### 信用（社債・借金）
検索語: `AI debt OR bonds OR credit spreads OR CDS`
- 11/10 Reuters | AI debt faces pressure as Democrats prepare to take over Congress
- 11/10 WSJ | Why the Credit Default Swap Market—Red Hot in the AI Trade—Is Vital for CFOs
- 11/10 Bloomberg.com | AI Debt Blowups Become Fodder for ETFs Aimed at Retail Investors
- 11/10 IndexBox | AI Debt Under Pressure: Credit Spreads Widen as Democrats Target AI Regulation - News and Statistics
- 11/10 CNBC | CoreWeave earnings put debt-fueled AI build-out under scrutiny

### 「〇〇ショック」の呼び名（日本語）
検索語: `ショック 株`
- 11/10 四季報オンライン | 民主党大勝ショックはAI相場の｢中間反落｣､戻りの主役はこれだ
- 11/10 Business Insider Japan | トランプ中間選挙ショックを経て、株価が急騰する。ウォール街がさらなる上昇を見込む理由
- 11/10 Yahoo!ニュース | リーマン・ショックで資産4000万円が目減り…総資産2.8億円の投資家が株を売らずに持ち続けた理由（みんかぶマガジン）
- 11/10 매일경제 | 最近、韓国と米国の株式市場では「アーニングショックのない株価ショック」がしばしば発生する。 実績はいいのに株価は間違いなく急落する。 特に株式市場に影響力が大きい大型株(時価総額上位銘柄)は無条件に

### 引け後・時間外の動き（英語）
検索語: `"after hours" OR "after the bell" OR "extended trading" stocks`
- 11/10 Seeking Alpha | Stocks making big moves after hours: CRWV, STUB, LAND
- 11/10 TradingView | CRWV Stock Climbs 8% After-Hours As $132B Revenue Backlog Reinforces AI Compute Demand: NBIS, IREN Tick Higher
- 11/10 Benzinga | Iambic Therapeutics Jumps 17% After-Hours as Wall Street Turns Bullish on Its AI-Powered Drug Discovery Platform

### 引け後・時間外の動き（日本語）
検索語: `時間外 決算 株`
- 11/10 Yahoo!ファイナンス | 米コアウィーブ株価、時間外で6％超上昇 四半期決算を受けて(トレーダーズ・ウェブ)
- 11/10 株探 | ロケット・ラボ、決算受け時間外で８％安＝米国株個別
- 11/10 Yahoo!ファイナンス | サンミナ、決算受け時間外で１４％高＝米国株個別(株探ニュース)
- 11/10 BigGo ファイナンス | 米HVAC機器メーカーAAON、2026年売上成長見通しを72〜75%に引き上げ—時間外取引で株価22%急騰
- 11/10 Yahoo!ファイナンス | ロケット・ラボ、決算受け時間外で８％安＝米国株個別(株探ニュース)
- 11/10 Investing.com - FX | 株式市場 | ファイナンス | 金融ニュース | マーキュリー・システムズ株が時間外取引で下落した理由
- 11/10 Investing.com - FX | 株式市場 | ファイナンス | 金融ニュース | ロケット・ラボ株が下落、第3四半期決算で損失が予想を上回る
- 11/10 Investing.com - FX | 株式市場 | ファイナンス | 金融ニュース | マーキュリー・システムズ、好決算にもかかわらず株価下落

### 買収・合併（英語）
検索語: `acquisition OR acquire OR merger OR takeover chip OR semiconductor OR AI OR optical`
- 11/10 Fierce Healthcare | Oura to acquire AI virtual primary care partner Counsel Health for $625M
- 11/10 TechCrunch | Oura to acquire AI-native primary care startup Counsel Health for $625M
- 11/10 STAT | Oura to acquire Counsel Health for $625 million, a big bet on AI care | STAT
- 11/10 Modern Healthcare | Oura to acquire AI care company Counsel Health for $625M
- 11/10 CMSWire | Claritas Launches Email Advantage, Bringing AI-Powered Optimization to Acquisition Email
- 11/10 Fitt Insider | Oura to Acquire Counsel Health for $625M
- 11/10 Bloomberg.com | Oura to Buy AI Doctor Startup for $625 Million; Posts 153% Sales Jump

## 2. 保有・候補・時間外で大きく動いた銘柄（2026-11-04〜2026-11-10 の見出し）

### SNDK（Sandisk Corporation、保有、AIサーバー・ストレージ・メモリ・端末、前日比 -3.0%、1週 -23.7%、時間外 -0.4%）

#### Googleニュース
検索語: `Sandisk stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/5 Yahoo Finance | What's Going On With Sandisk Stock Today?
- 11/5 MarketWatch | Micron, Sandisk and other AI stocks see steep drops: ‘Investors don’t like uncertainty’
- 11/5 TheStreet | SanDisk stock plunges 20% as AI selloff deepens despite strong earnings
- 11/7 Benzinga | SanDisk Stock Drops Ahead of Split as Wall Street Analysts Weigh In

#### Yahooファイナンス
検索語: `SNDK`
- 11/10 24/7 Wall St. | Micron Cratered Losing 30% in 1 Month: 240% Gains Lie Ahead According to This Wall Street Pro
- 11/10 Insider Monkey | Sandisk Corporation (SNDK) Secured Billions in Contracted Revenue: Is the Memory Boom Just Getting Started?
- 11/10 Motley Fool | Got $10,000? 3 Hot Stocks to Buy That Could Make You a Fortune

### AMD（Advanced Micro Devices, Inc.、保有、半導体、前日比 +1.3%、1週 +6.5%、時間外 -0.3%）

#### Googleニュース
検索語: `Advanced Micro Devices stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/4 Barron's | AMD Stock Jumps on Big Earnings Beat
- 11/9 Investor's Business Daily | AMD Stock Rises On Google Cloud Deal, Wall Street Upgrade
- 11/9 Seeking Alpha | Advanced Micro Devices soars 13% on Google Cloud deal, tech rally (AMD:NASDAQ)
- 11/10 Investing.com | Why is Advanced Micro Devices stock rallying today?

#### Yahooファイナンス
検索語: `AMD`
- 11/10 Benzinga Prediction Markets | AMD Gains 25% Against NVDA in 2 Days: Chip Analyst Says Lisa Su Is ‘at Her Best’
- 11/10 GuruFocus.com | AMD Stock Just Got Massive Upgrade From Oppenheimer
- 11/10 Motley Fool | Rackspace (RXT) Q3 2026 Earnings Call Transcript

### ROK（Rockwell Automation, Inc.、候補、データセンターの電力・冷却・部品・受託製造・建設、前日比 +2.0%、1週 -11.0%、時間外 -0.0%）

#### Googleニュース
検索語: `Rockwell Automation stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/5 Yahoo Finance | Rockwell Automation Q4 Earnings Beat Estimates on Margin Gains
- 11/5 MarketWatch | Rockwell Automation Inc. stock underperforms Thursday when compared to competitors
- 11/5 TIKR.com | Rockwell Automation Sinks 13% as Tariff Refunds to Customers Drag Q4 Sales Below Estimates
- 11/10 24/7 Wall St. | Rockwell’s CEO Is Buying the 14% Crash, and His Last Dip Buy Is Up 37%

#### Yahooファイナンス
検索語: `ROK`
- 11/9 MT Newswires | Rockwell Automation Insider Bought Shares Worth $1,545,450, According to a Recent SEC Filing
- 11/9 StockStory | ROK Q3 CY2026 deep dive: margin expansion and AI-driven segment growth offset flat sales
- 11/9 Zacks | Deciphering Rockwell Automation (ROK) International Revenue Trends

### NVDA（NVIDIA Corporation、候補、半導体、前日比 -5.5%、1週 -18.3%、時間外 +0.4%）

#### Googleニュース
検索語: `NVIDIA stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/9 NBC News | Nvidia shares sink while stock market surges
- 11/9 WSJ | U.S. Stocks Leap Despite Nvidia Slide
- 11/9 ABC News - Breaking News, Latest News and Videos | Nvidia stock closes lower after company opens probe into CEO Jensen Huang
- 11/9 CNN | Nvidia stock falls after investigation into CEO, bucking market rally

#### Yahooファイナンス
検索語: `NVDA`
- 11/10 CBS News | Nvidia's trillion-dollar bind: Can it afford to lose Jensen Huang?
- 11/10 Investor's Business Daily | Dow Jones Futures: Stock Market Falls On Surging Treasury Yields, Nvidia Sell-Off; CoreWeave Rises Late
- 11/10 Moby | 908 Devices Inc. Q3 2026 Earnings Call Summary

## 3. 引けまでに大きく下げた銘柄（2026-11-04〜2026-11-10 の見出し）

### DELL（Dell Technologies Inc.、AIサーバー・ストレージ・メモリ・端末、前日比 -3.4%、1週 -18.1%、時間外 +0.0%）

#### Googleニュース
検索語: `Dell stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/4 Yahoo Finance | Dell Technologies (DELL) Stock Drops Despite Market Gains: Important Facts to Note
- 11/4 Investing.com | Why is Dell Technologies stock sliding today?
- 11/5 Billionaires.Africa | American billionaire Michael Dell loses $12.3 billion as Dell stock sinks after midterms
- 11/10 MarketWatch | Dell Technologies Inc. Cl C stock falls Tuesday, underperforms market

#### Yahooファイナンス
検索語: `DELL`
- 11/9 Motley Fool | Applied Materials vs. Dell Technologies: Comparing Stable vs. Accelerating Revenue Between These Artificial Intelligence Companies
- 11/9 Zacks | Will Cisco Systems (CSCO) Deliver the Strong Results the Market Needs to See?
- 11/10 24/7 Wall St. | Here’s The AMD Data Center Number Investors Need to Know

### STX（Seagate Technology Holdings plc、AIサーバー・ストレージ・メモリ・端末、前日比 -0.9%、1週 -17.3%、時間外 -0.3%）

#### Googleニュース
検索語: `Seagate stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/4 Moomoo | Memory Chip Stocks Fall Broadly in Pre-Market Trading; Seagate Technology (STX.US) Drops Over 4%
- 11/5 Investing.com Canada | Why is Seagate Technology stock tumbling today? By Investing.com
- 11/6 Trefis | What Would It Take For Seagate Stock To Do It Again?
- 11/9 24/7 Wall St. | Micron Rises 6% as Bulls Tout Its Bargain Valuation and Buyback Firepower; Seagate and Western Digital Jump 11%

#### Yahooファイナンス
検索語: `STX`
- 11/9 Barrons.com | Review & Preview: Dip Buyers Unite
- 11/9 TIKR | Seagate Dropped 15% in a Week: Morgan Stanley Says It Could Double in the Next 12 Months
- 11/9 TIKR | Seagate Soars 10% in AI Rebound as Morgan Stanley Sees “Strong Fundamentals and Weak Sentiment”

### VRT（Vertiv Holdings Co、データセンターの電力・冷却・部品・受託製造・建設、前日比 -3.1%、1週 -17.7%、時間外 +0.1%）

#### Googleニュース
検索語: `Vertiv stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/5 Investing.com | Why is Vertiv stock plunging today?
- 11/6 Yahoo Finance | Are You Sure You Understand Vertiv Stock's Risk?
- 11/6 MarketBeat | Vertiv (NYSE:VRT) Stock Jumps 3.3% - Time to Buy?
- 11/10 TIKR.com | Vertiv Sinks 11% in a Week as Midterm Sweep Hits Data Center Stocks

#### Yahooファイナンス
検索語: `VRT`
- 11/10 24/7 Wall St. | 2 Stocks Sidestep the Data Center Backlash
- 11/10 MarketBeat | Vertiv CEO Sees Faster Pipeline Growth as AI and Cloud Demand Expand
- 11/10 Motley Fool | GE Vernova, Vertiv, and Bloom Energy Just Lost 10% to 24% in a Week. Here's What Set Off the AI Power Sell-off.

### FLEX（Flex Ltd.、データセンターの電力・冷却・部品・受託製造・建設、前日比 -2.7%、1週 -13.6%、時間外 +0.0%）

#### Googleニュース
検索語: `Flex stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/4 Yahoo Finance | Why Did Flex (FLEX) Move Today?
- 11/4 Yahoo Finance | Does Beating The Market Prove Flex Is A Great Company?
- 11/5 Barron's | The Unwinding of the AI Trade Is Taking These Stocks Down With It the Most
- 11/9 Moomoo | Flex Jumps as Spin-Off Momentum and Growth Outlook Stay in Focus

#### Yahooファイナンス
検索語: `FLEX`
- 11/4 Simply Wall St. | Flex (FLEX) Stock May Be 45% Undervalued As Spin Off Plans Loom
- 11/4 Zacks | Flex's 2027 Axiom Spin-Off: Will Two Firms Unlock Value for Investors?

### GEV（GE Vernova Inc.、データセンターの電力・冷却・部品・受託製造・建設、前日比 -3.9%、1週 -13.2%、時間外 -0.1%）

#### Googleニュース
検索語: `GE Vernova stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/4 Investing.com | Why is GE Vernova stock sliding today?
- 11/4 Seeking Alpha | GE Vernova plunges by most in nearly two years as data center-related stocks crushed (GEV:NYSE)
- 11/9 Yahoo Finance | Is the Options Market Predicting a Spike in GE Vernova Stock?
- 11/10 24/7 Wall St. | GE Vernova Declines 6% as AI Power Stocks Give Back Monday's Rally; Vertiv Drops 4%, Quanta Services Slides 2%

#### Yahooファイナンス
検索語: `GEV`
- 11/10 MT Newswires | GE Vernova Plans $34.5 Million Investment to Expand Louisiana Transformer Manufacturing Operations
- 11/10 MT Newswires | GE Vernova Shares Fall After SoftBank Discloses $3.7 Billion Charge Tied to Power-Generating Equipment
- 11/10 MT Newswires | Sector Update: Energy

# 実行時の注記
- 環境に matplotlib・Pillow がなく、prepare で候補・保有銘柄の数値データが作れなかったため、入れ直して数値データを作り直した。
- 個別銘柄のプロンプトが8,000文字を超え（テーマの状態の節が長いため）送信できなかった。著者（ボリンジャー・コナーズ）へは、テーマの状態の節から「グループごとの悪いニュースの流れ（記録だけ）」の表と見出しを外して（scan_short.md）送り直した。ニュースは文字数の上限まで縮めた。
- ワインスタインへのテーマの局面は、全体の版が空の応答だったため1〜2節だけの短い版で送った回答。
