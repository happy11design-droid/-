# テーマ監視 2026-11-17

# 判定のまとめ（ルールの判定と著者の判定を分けて表示）

- **ルールの判定**: 採用した売買ルール（スクリプト）が数値で決めたもの。損切りは買値の15%下の逆指値（日中に届けばその場で売れる）。
- **著者の判定**: ノートブックの著者の回答。買いは注文を止める理由があるときだけ【様子見】、保有はルールより早く手じまう理由があるときだけ【売り】。根拠は下の「著者の回答（全文）」。
- 2つが食い違うときに、どちらに従うかはユーザーが決める。

- **テーマ全体の急落（S2・記録だけ）: あり（S2）**（SOXが直近60取引日の最高値から -27.0%）。S2の日の順張りの候補には「S2なら見送る形」と付ける（売買のルールは変えない。記録してから採用を決める。2026-10-14）

- **特殊な下げ（記録だけ）: あり（特殊な下げ）**（2026-10-16から）（SOXが直近60取引日の最高値から -27.0%、前の1年の大きな上げ・雇用の弱さ・物価の再加速のうち 2つ）。1995年〜では、この形の後にSOXの下げが長引くことが多かった（後知恵を含む）。売買のルールは変えない（2026-11-03）

## 保有銘柄

| 銘柄 | ルール | 損益 | 時間外 | ルールの判定 | ルールの判定の理由 | 著者の判定 |
|---|---|---|---|---|---|---|
| SNDK | ルール外（ユーザーの判断。この日はどのルールの合図もなし） | -41.9% | **+5.5%** | **売り** | 終値 797.24 が損切り価格 1165.61 以下 | 【未判定】（） |
| AMD | ボリンジャーIII | -8.5% | +3.7% | 保有継続 | 損切り 467.47（終値から -7.1%） | 【保有継続】（ボリンジャー） |

## 候補の判定（並びは上の「買う順番」の表と同じ）

- 並びは上の「買う順番」の表と同じ（RSの高い順。勝率の高い順ではない）。注文の値段・株数・逆指値は上の表を見る。勝率・1回平均は、そのルールの過去の成績（後知恵なしの監視銘柄・2015年〜の全部の合図）。
- 空き枠: 3（同時保有4銘柄まで。保有2、うちルールの売り1）。著者が【様子見】の候補を見送るかはユーザーが決める。

| 順 | 銘柄 | ルール | 過去の勝率 | 過去の1回平均 | RS | 時間外 | ルールの判定 | 著者の判定 |
|---|---|---|---|---|---|---|---|---|
| 1 | IBM（IBM（アイ・ビー・エム）） | 逆張り: ボリンジャー メソッドIII | 68% | +1.5% | 23 | +0.3% | 買い（翌日の寄り付き） | 【買い】（ボリンジャー） |
| 2 | INTU（イントゥイット） | 逆張り: ボリンジャー メソッドIII | 68% | +1.5% | 7 | -0.0% | 買い（翌日の寄り付き） | 【買い】（ボリンジャー） |
| 3 | SMCI（スーパー・マイクロ・コンピューター） | 逆張り: 急落の底（担当: コナーズ） | 65% | +2.1% | 3 | **+5.2%** | 買い（指値 23.66、3取引日まで） | 【様子見】（コナーズ） |

- 時間外: 前の取引日の引けから、引け後（米国東部時間16〜20時）の最後の値までの騰落率（Yahoo。±5%以上は太字）。寄り付きの値段は、表の注文の目安（前日の終値で計算）から大きくずれることがある。原因の見出しは「ニュースの見出し」の節。

# 著者の回答（全文）

## 0_テーマの局面_ワインスタイン

1. **テーマ全体の局面**: 【ステージ3】（大上昇後に30週線が横ばい化し線下推移の天井圏。第2・8章）[1, 2]
2. **グループごとの局面**:
- 半導体｜ステージ3｜30週線横ばい[1]
- 半導体製造装置・材料・設計ソフト・計測｜ステージ3｜30週線横ばい[1]
- AIサーバー・ストレージ・メモリ・端末｜ステージ3｜30週線横ばい[1]
- 光・通信・ネットワーク｜ステージ3｜30週線横ばい[1]
- データセンターの電力・冷却・部品・受託製造・建設｜ステージ3｜30週線横ばい[1]
- AIプラットフォーム・クラウド｜ステージ3｜30週線横ばい[1]
- AIソフト・セキュリティ・ITサービス｜ステージ2｜30週線上かつ線上昇[3]
3. **転換の兆し**: あり。30週線横ばいと下抜け（6群で乖離-8.8〜-18.7%）は天井・崩れの兆候（第2・8章）[1, 2]。対市場RS劣後も弱気転換（第1・4章）[4, 5]（50日線等はマニュアルに規定なし[6]）。
4. **テーマの外**: 判定不能（ヒートマップ省略のため）

（全体の版が空の応答だったため、1〜2節だけの短い版で送り直した回答。ヒートマップ・急騰急落・ニュースは渡していない）

## 1_コナーズ_prompt_1

## SMCI
1. **投資判断**: 【様子見】（200日線下での買いは厳禁）[1]
2. **止める理由の確認**:
- 本が禁じる形・状況｜あり｜株価が200日線の下側にあるため買い不可（第4章）[1]
- 避けるべき時期（決算など）｜なし｜決算発表まで77日。避けるべき月初（3〜8日）でもない（第11章、決算自体の見送り規定はマニュアルに規定なし）[2, 3]
- 悪材料｜なし｜悪材料による急落は市場に織り込み済みとみなす（第2章、第3章）[4, 5]
3. **現状パターンと価格**:
- 現状パターン: A（直近5日高値から急落、RSI(2)≦10成立）
- 本日の発注: 見送り（200日線下のため発注なし）[1]
4. **注意点**: 200日線を下回った株は、どれほど急落した底であっても買いを見送り白紙に戻すのが絶対のルールである（第4章）[1]。

## 1_ボリンジャー_prompt_1

## AMD
1. **投資判断**: 【保有継続】（早期手じまい理由なし）
2. **止める理由の確認**:
   - 本が禁じる形・状況｜なし｜M型トップや上部乖離等の売りシグナルなし（第13章、第20章）[1, 2]
   - 避けるべき時期（決算など）｜なし｜次回決算は2027/2/2で先（時期回避の規定なし、第4章）[3]
   - 悪材料｜なし｜早期売却を指示する悪材料の規定なし（23_用語集）[3, 4]
3. **現状パターンと価格**:
   - 現状パターン: 保有中（10/21買付）
   - 売りの予約注文: 〈指値売り〉603.11（現在値比 +19.8%）[2]
4. **注意点**: スクリプトが検知した11/5大陰線手じまい条件に従うか要判断。

## 1_ボリンジャー_prompt_2

## IBM
1. **投資判断**: 【買い】（メソッドIIIの買い条件成立 [1, 2]）
2. **止める理由の確認**:
- 本が禁じる形・状況｜なし｜第20章の買い条件合致 [1, 2]
- 避けるべき時期（決算など）｜なし｜次回決算まで71日（マニュアルに規定なし）
- 悪材料｜なし｜個別悪材料なし（マニュアルに規定なし）
3. **現状パターンと価格**:
- 現状パターン: A（%b・II%条件成立 [1]）
- 本日の発注: 翌日の寄り付きで成行
4. **注意点**: 手じまい目標は上部バンド到達（第20章 [3, 4]）。

## 1_ボリンジャー_prompt_3

## INTU
1. **投資判断**: 【買い】（メソッドIIIの条件成立、止める理由なし）
2. **止める理由の確認**:
- 本が禁じる形・状況｜なし｜第20章（%b<0.05かつ21日II%>0が成立）
- 避けるべき時期（決算など）｜なし｜マニュアルに規定なし
- 悪材料｜なし｜マニュアルに規定なし
3. **現状パターンと価格**:
- 現状パターン: A（最新足で条件成立）
- 本日の発注: 翌日の寄り付きで成行
4. **注意点**: 2日後に決算発表があるため、直近安値付近にストップを置き想定外の急変に備えること

# スキャン（数値と事実）


- 監視銘柄 87（判定できたのは 87）。
- この一覧は数値と事実だけ。売買の判断は著者のノートブックが行う。

## 1. テーマ（グループ）の強さ

| グループ | 銘柄数 | 1週 | 1カ月 | 3カ月 | 3カ月の順位 | 50日線より上の銘柄の割合 | グループ指数の30週線の局面（線との乖離、4週前からの線の傾き） |
|---|---|---|---|---|---|---|---|
| 半導体 | 16 | -2.3% | -6.4% | -5.6% | 2位 | 25% | 横ばい（-13.4%、+4.3%） |
| 半導体製造装置・材料・設計ソフト・計測 | 9 | -5.4% | -15.3% | -20.9% | 5位 | 0% | 横ばい（-18.7%、+0.7%） |
| AIサーバー・ストレージ・メモリ・端末 | 9 | -2.0% | -19.6% | -26.1% | 7位 | 11% | 横ばい（-15.8%、+5.8%） |
| 光・通信・ネットワーク | 9 | -2.7% | -10.7% | -25.0% | 6位 | 11% | 横ばい（-17.6%、+0.6%） |
| データセンターの電力・冷却・部品・受託製造・建設 | 19 | -3.0% | -7.5% | -10.7% | 4位 | 5% | 横ばい（-11.4%、+0.1%） |
| AIプラットフォーム・クラウド | 11 | -3.5% | -11.3% | -3.0% | 1位 | 27% | 横ばい（-8.8%、+1.2%） |
| AIソフト・セキュリティ・ITサービス | 14 | -3.7% | -6.4% | -7.9% | 3位 | 29% | 上昇（+0.5%、+4.7%） |

## 2. テーマ全体の状態と早めの警告

- 市場全体の30週線による局面: S&P500指数 **横ばい**／NASDAQ100指数 **横ばい**（急落の底で買うルールは、過去の検証で下落相場で特に強く、横ばいの相場では負けていた）
- **2倍ETFを使う局面（案1、2026-10-13 採用）: S&P500の20週線（100日線）で 横ばい** → 新しく買う銘柄は、2倍ETFのある銘柄も元の株で買う（保有中のETFはそのまま）（SPY 732.44、100日線 759.30、20日前の線 756.22。上昇＝線より上かつ線が上向き）
- **テーマ全体の急落（S2、記録だけ。売買のルールは変えない）: あり（S2）**（SOX 9642.88、直近60取引日の最高値 13217.82 から -27.0%。S2＝最高値から−10%以上）。S2のときに「順張りの新しい買いだけ止める」形を記録で比べる（2026-10-14 ユーザー決定。バックテストでは年率は上がったが2つの期間ではどちらも少し下回ったため、記録してから採用を決める。`バックテスト結果/テーマ全体の急落を検知して手じまう・買いを止める.md`）
- **グループごとの悪いニュースの流れ（記録だけ。売買のルールは変えない。2026-11-04〜2026-11-17）**: 会社の名前と悪い言葉（格下げ・目標株価の引き下げ・見通しの引き下げ・予想未達・急落・信用・訴訟・輸出規制など）の両方がある見出しの数（Googleニュース、`tools/news_headlines.py`）。10取引日の1銘柄あたりが一番多いグループに印。2026年7〜11月の確かめでは、印のグループの合図は10月は成績が悪かった（1回平均 −10.6%、ほか −5.6%）が、7〜9月は逆に良かった（+11.6%、ほか +6.7%）（`バックテスト結果/実際の運用の期間の確認_2026-10-23/グループの悪いニュースの流れ.md`。2026-11-04）

| グループ | 悪いニュース 直近5取引日 | その前の5取引日 | 10取引日の1銘柄あたり | 良いニュース 10取引日（1銘柄あたり） | 印 |
|---|---|---|---|---|---|
| 光・通信・ネットワーク（9） | 9件 | 15件 | 2.7 | 11件（1.2） | **悪いニュースが続いている** |
| 半導体（16） | 29件 | 9件 | 2.4 | 24件（1.5） |  |
| AIサーバー・ストレージ・メモリ・端末（9） | 8件 | 1件 | 1.0 | 15件（1.7） | **良いニュースが多い** |
| AIプラットフォーム・クラウド（11） | 9件 | 0件 | 0.8 | 3件（0.3） |  |
| AIソフト・セキュリティ・ITサービス（14） | 1件 | 1件 | 0.1 | 12件（0.9） |  |
| 半導体製造装置・材料・設計ソフト・計測（9） | 0件 | 1件 | 0.1 | 5件（0.6） |  |
| データセンターの電力・冷却・部品・受託製造・建設（19） | 1件 | 1件 | 0.1 | 13件（0.7） |  |

印のグループ（光・通信・ネットワーク）の最近の見出し: 2026-11-17 Cisco upgraded, PepsiCo downgraded: Wall Street's top analyst calls（Yahoo Finance）／2026-11-16 Akamai Technologies, Inc. Stock 12‑Month Price Target Cut to $128.85, Implies 51% Upside（TradingView）／2026-11-16 Cisco: I Downgraded It At The Top, Look At It Now (Rating Upgrade) (NASDAQ:CSCO)（Seeking Alpha）

良いニュースが多いグループ（AIサーバー・ストレージ・メモリ・端末）の最近の見出し: 2026-11-16 Apple upgrades the iPhone Duo: New features（SecNews.gr）／2026-11-16 Apple iPad Upgrade Inspired by $1,999 iPhone Pair, No New Device Needed（RS Web Solutions）

- **特殊な下げ（記録だけ。売買のルールは変えない）: あり（特殊な下げ）**（2026-10-16から）。SOX は直近60取引日の最高値から -27.0%（−15%以下が条件）、●A 前の1年の上げ +98.4%（+80%以上）、・B 雇用の伸び 137千人/月（2026-10まで。10万人未満）、●C 物価 4.0%（2026-09。3か月前 3.7%。3.5%以上で再加速）＝2つ（2つ以上が条件）。1995年〜でSOXが−15%以下かつ条件2つ以上の日は、120日後にSOXが下だったのが69%・250日後が70%（中央値 −33%）、AI以外の8業種の平均は250日後 −7%。ただし条件は過去を見て選んだもの（条件が2つ以上の局面は約5回）で、2026年7〜9月にこの間テーマを買わないと、その後の戻りを逃して2026年の成績は下がった（`バックテスト結果/実際の運用の期間の確認_2026-10-23/特殊な下げと過去の似た下げ.md`。2026-11-03）
- テーマ指数（監視銘柄の等金額平均）の30週線による局面: **横ばい**（上昇＝線より上かつ上向き、下落＝線より下かつ下向き、それ以外＝横ばい。ワインスタインのステージの近似）
- テーマ指数と50日線: 50日線より下（乖離 -11.9%）
- S&P500に対する相対的な強さ: 50日平均より下（S&P500より弱い）
- 監視銘柄のうち50日線より上の割合: 16%
- 警告（割合が40%未満かつテーマ指数が50日線より下）: **出ている**
- 参考（バックテスト）: 30週線の「下落」は高値から10〜33%下げた後に出る遅い判定。50日線・割合・相対的な強さは高値から2〜8%で出るが、誤報が年15回以上ある。警告中に新しい買いを止めると、押し目買い（ボリンジャーIII）の成績は大きく下がった（`バックテスト結果/テーマ監視銘柄・直近3年.md` 11・12節）。

## 3. ヒートマップ（Finviz、全米の業種別の騰落率）

3カ月の騰落率の上位15業種（テーマの外で強くなっている業種の確認用）:

| 順位 | 業種 | 1週 | 1カ月 | 3カ月 | 6カ月 | 1年 |
|---|---|---|---|---|---|---|
| 1 | Medical Distribution | +0.5% | +6.9% | +19.4% | +37.8% | +20.1% |
| 2 | Advertising Agencies | +0.5% | +34.4% | +19.1% | -7.9% | -21.8% |
| 3 | Insurance - Diversified | +0.3% | +8.9% | +14.9% | +19.5% | +14.6% |
| 4 | Lodging | -1.1% | +8.2% | +12.9% | +17.0% | +38.2% |
| 5 | Insurance - Reinsurance | -1.2% | +3.2% | +12.7% | +19.8% | +35.4% |
| 6 | Discount Stores | +2.0% | +8.4% | +12.3% | -0.5% | +25.0% |
| 7 | Grocery Stores | +1.6% | +5.8% | +12.2% | -8.0% | -3.9% |
| 8 | Paper & Paper Products | -1.8% | +12.5% | +11.8% | +15.9% | +3.6% |
| 9 | Medical Care Facilities | -1.7% | +7.5% | +11.8% | +22.9% | +20.8% |
| 10 | Household & Personal Products | +0.1% | +6.2% | +11.6% | +19.2% | +14.1% |
| 11 | Health Information Services | -7.3% | -0.9% | +11.3% | +49.9% | +7.8% |
| 12 | Consumer Electronics | +0.9% | +2.7% | +11.1% | +17.6% | +26.8% |
| 13 | REIT - Hotel & Motel | -1.3% | +7.5% | +10.3% | +27.8% | +51.1% |
| 14 | Real Estate - Diversified | -4.7% | +8.6% | +8.2% | +15.9% | +8.0% |
| 15 | Diagnostics & Research | -4.3% | -0.2% | +7.9% | +45.7% | +18.3% |

テーマの業種の順位（3カ月、全144業種中）: Semiconductors 128位、Semiconductor Equipment & Materials 137位、Computer Hardware 141位、Communication Equipment 124位、Electronic Components 123位、Software - Infrastructure 58位、Software - Application 85位、Internet Content & Information 108位

## 4. 急騰・急落した銘柄（前日比±5%以上、または出来高が50日平均の2倍以上）

原因のニュースをサブエージェントが調べ、候補・保有銘柄の判定材料として著者に渡す。急騰・急落そのものは売買の合図にしない（後知恵のないS&P500全体のバックテストでは、急騰の翌日に買うルールは年率7%、急落の翌日に買うルールは年率9〜10%で、採用した3つのルールより優れていなかった）。

| 銘柄 | グループ | 前日比 | 出来高（50日平均の倍） | 終値 | 50日線 | RS | 局面 |
|---|---|---|---|---|---|---|---|
| CRM | AIソフト・セキュリティ・ITサービス | -9.5% | 1.5倍 | 194.52 | 下 | 29 | 下げ |
| INTU | AIソフト・セキュリティ・ITサービス | -7.2% | 1.0倍 | 320.79 | 上 | 7 | 上げ |
| NOW | AIソフト・セキュリティ・ITサービス | -6.5% | 1.6倍 | 92.90 | 下 | 4 | 下げ |
| WDAY | AIソフト・セキュリティ・ITサービス | -5.8% | 1.3倍 | 182.80 | 下 | 56 | 下げ |
| NVDA | 半導体 | -0.4% | 2.4倍 | 155.46 | 下 | 4 | 下げ |

- 局面（判定式はClaudeが置いたもの）: **上昇相場**＝終値 > 50日線 > 200日線、50日線が20取引日前より2%以上高い、ADX(14) ≧ 20／**下落相場**＝終値 < 50日線 < 200日線、50日線が20取引日前より2%以上低い、ADX(14) ≧ 20／**上げ**＝それ以外で終値が50日線より上、かつ50日線が10取引日前より上か20日線が5取引日前より上／**下げ**＝それ以外で終値が50日線より下、かつ50日線が10取引日前より下か20日線が5取引日前より下（急な下げの初めは50日線がまだ上向きのため20日線でも見る）／**レンジ**＝どれにも当たらない（2026-11-05 から5つ。それまでは上昇相場とレンジの2つだけで、下げている銘柄もレンジと出ていた）。

## 4-2. 監視外の注目銘柄（S&P500・NASDAQ100のうち監視銘柄に入っていない銘柄）

条件: 流動性（株価5ドル以上・50日平均出来高25万株以上）があり、(a) 前日比+8%以上かつ出来高が50日平均の2倍以上、または (b) 終値が直前1年の最高値（終値）を上回り、RS≧90。RSの高い順に5銘柄（ニュースを調べる）。監視銘柄に入れるかはユーザーが決める。

該当なし

## 5. 保有銘柄の手じまい条件（`新分析ツール/保有銘柄.md`）

| 銘柄 | ルール | 買った日 | 買値 | 終値 | 損益 | 損切り価格（買値の15%下、逆指値） | ルールの手じまい条件 | 出来高2倍の大陰線（買った後の直近5日） | 次回決算予定日 |
|---|---|---|---|---|---|---|---|---|---|
| SNDK | ルール外（ユーザーの判断。この日はどのルールの合図もなし） | 2026-10-21 | 1371.30 | 797.24 | -41.9% | 1165.61 | **損切り価格を下回った** ルールが不明（保有銘柄.md の「ルール」を確認） | なし | 2026-10-29 |
| AMD | ボリンジャーIII | 2026-10-21 | 549.97 | 503.41 | -8.5% | 467.47 | **出来高2倍の大陰線が 2026-11-05 に出た**（まだ持っていれば、次の寄り付きで全部売る） 売りの指値: 上部バンド 603.11（今夜この値に置き直す。届いた日に売れる）（2倍ETF AMUU で持っている場合も、判定は元の株 AMD の値段） | なし | 2027-02-02 |

- 出来高2倍の大陰線: 実体（始値−終値）が前日までのATR(14)の1.5倍以上、終値がその日の値幅の下25%以内、出来高が前日までの50日平均の2倍以上の日。**押し目（ボリンジャーIII）・急落の底の保有では売りのルール**: 出たら翌日の寄り付きで全部売り、空いた枠で次の合図を買う（2026-10-02 ユーザー決定。`バックテスト結果/やり直し_売りの合図の組み合わせ.md`。乱数3組とも年率が約+2ポイント、最大下落率もやや下がった）。ミネルヴィニ・新高値V2の保有では事実の表示（順張りに足しても良くならなかった）。

- 半分売りの合図（ミネルヴィニ・新高値V2の保有だけ）: 反転のローソク足（かぶせ線・弱気の包み足・宵の明星・流れ星）＋出来高が50日平均の1.5倍以上＋RSI(14)が前日か当日に70以上。買った後に最初に出た日の翌日の寄り付きで半分売り、残り半分は50日線割れ・損切り15%まで持つ（2026-10-01 ユーザー決定。`バックテスト結果/半分だけ売るとオニールの空き枠.md`）。

- かぶせ線（ミネルヴィニ・新高値V2の保有だけ）: 上昇中の陽線の翌日に、前日の高値より上で寄り付き、前日の陽線の真ん中より下（前日の始値より上）で引けた日。翌日の寄り付きで全部売り、空いた枠で次の合図を買う。半分売りより優先する（2026-10-01 ユーザー決定。`バックテスト結果/2倍ETFで売って買い直す.md`。順張りの売買の25%で出て、1回平均+2.0%、年率 21.4%→26.4%）。

## 5-2. 前日（2026-11-16の引け）の【買い（予約）】の確認

前日の【買い（予約）】はなし。

## 6. 候補（採用したルールの条件が成立＝A。予約（B）は2026-10-25から注文せず、節6-3に参考の表示だけ）

建玉の目安: 同時保有4銘柄まで、1銘柄に資金の25%（資金÷4）、損切りは買値の15%下（ユーザー決定 2026-09-29）。

パターン: A＝最新の足で採用ルールの条件が成立（押し目・ミネルヴィニ・新高値V2は翌日の寄り付きで成行、急落の底は合図の日の終値の2%下に指値で3取引日待つ。2026-11-03 ユーザー採用）。条件の成立が目前の銘柄（B）は、予約の注文をやめたので節6-3に参考として出す（2026-10-25 ユーザー決定）。

| 銘柄 | グループ | パターン | 種類 | ルールの過去の成績 | 終値 | 前日比 | RS | 50日線の傾き | 局面 | 当てはまった条件 | 次回決算予定日 | 注文の目安 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SMCI | AIサーバー・ストレージ・メモリ・端末 | A | 逆張り: 急落の底（担当: コナーズ） | 2位（勝率65%・1回平均+2.1%） | 24.14 | -3.6% | 3 | -7.2% | 下げ | 直前5日の最高値（終値）から-20.7%下落（−15%以上）、RSI(2)=7.2（≦10）、急落の前は50日線＞200日線。市場全体の局面: S&P500 横ばい／NASDAQ100 横ばい | 2027-02-02（77日後） | 指値買い 23.66（合図の日 2026-11-17 の終値 24.14 の2%下。今日から3取引日。届かなければ見送り、途中で終値が5日線を上回ったら取り消す）。損切り: 約定した値段の15%下。手じまい: 終値が5日線（今日 26.69）を上回った翌日の寄り付き（コナーズ）。**株数の目安: 100株**（2,384ドル÷23.66。注文の価格）、購入金額 約2,366ドル |
| IBM | AIプラットフォーム・クラウド | A | 逆張り: ボリンジャー メソッドIII | 3位（勝率68%・1回平均+1.5%） | 231.09 | -4.7% | 23 | +2.7% | レンジ | %b=-0.272（<0.05）、21日II%=+0.147（>0） | 2027-01-27（71日後） | 翌日の寄り付きで買い。損切り: 買値の15%下。手じまい: 買った日の夜から、売りの指値をその日の上部バンド（今日 258.88）に置き、毎晩その日の値に置き直す。**株数の目安: 10株**（2,384ドル÷231.09。今日の終値。寄り付きの値段で変わる）、購入金額 約2,311ドル |
| INTU | AIソフト・セキュリティ・ITサービス | A | 逆張り: ボリンジャー メソッドIII | 3位（勝率68%・1回平均+1.5%） | 320.79 | -7.2% | 7 | -0.8% | 上げ | %b=-0.057（<0.05）、21日II%=+0.032（>0） | 2026-11-19（2日後）**決算が近い** | 翌日の寄り付きで買い。損切り: 買値の15%下。手じまい: 買った日の夜から、売りの指値をその日の上部バンド（今日 359.33）に置き、毎晩その日の値に置き直す。**株数の目安: 7株**（2,384ドル÷320.79。今日の終値。寄り付きの値段で変わる）、購入金額 約2,246ドル |

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
| ACN | AIソフト・セキュリティ・ITサービス | ボリンジャー メソッドIII（%bが0.05未満に近い） | 239.28 | -3.4% | 87 | %b=0.115（0.05まであと少し）、21日II%=+0.056（>0） | 237.15（この値より下で引けると翌朝の買いの候補（A）。目安） |
| SHOP | AIソフト・セキュリティ・ITサービス | ボリンジャー メソッドIII（%bが0.05未満に近い） | 141.90 | -4.0% | 64 | %b=0.166（0.05まであと少し）、21日II%=+0.045（>0） | 137.09（この値より下で引けると翌朝の買いの候補（A）。目安） |


# ニュース（サブエージェントの調査）

# ニュース調査（2026-11-17の引け時点／作成 2026-11-18 JST）
出典は headlines.md の見出し（媒体・日付）。

## テーマ全体の下げの原因
当たる条件: 監視銘柄の3銘柄以上が前日比−5%以下（CRM・INTU・NOW・WDAY）、S2あり。
- きっかけ（見出しより）: NVDAのCEOジェンスン・フアン氏の辞任（11/12 Yahoo Finance）と、決算（11/17の引け後）前の警戒。「Nvidiaの26%下落」（24/7 Wall St. 11/17）、日経「エヌビディア・ショックに追い打ち」（11/17）。11/17は「NSA障害でDow 848ドル下落」（Kiplinger 11/17）、NY株一時1000ドル超安・5カ月ぶり安値（四国新聞 11/17）。
- 広がった先: 米国の中国向け計算資源の新規制（Bloomberg 11/17「Chip Stocks Slide as US Sets New Curbs on China's Compute Access」）。Muddy WatersがNVDAを空売り（Investing.com 11/17）。ソフト株の下げ（TradingView 11/17「Adobe, DocuSign, Intuit, MongoDB, Workday shares are falling」）。CRM・NOWの個別の原因となる見出しは見つからなかった。
- 信用: Apolloのローワン氏「ネオクラウドの資金調達の道が消えるかもしれない」（CNBC 11/17）。Pimco「データセンター建設の鈍化でAI債のスプレッドは縮小しうる」（Bloomberg 11/17）。社債の利回り・CDS・格付け変更の具体的な数字は取得不可。
- 市場全体（S&P500・VIX・ハイイールド債）: 見出しでは市場全体も続落（Reuters 11/17）。VIX・ハイイールド債の数値は取得不可。

## 引け後・時間外の材料
- NVDA: 時間外 +4.4%（一時+4%超の報道）。決算（第3四半期）売上 1158億ドル（+103%）、次四半期の見通し 1300億ドル、自社株買い枠 2270億ドルに拡大（Yahoo Finance／TradingKey／BigGo 11/17）。フアン氏抜きの最初の決算。
- テーマ全体: NBIS +11.2%、CRWV +8.8%、ALAB +6.5%、LITE +6.2%、ARM +6.1%、COHR +6.1%、MRVL +5.5%、VRT +5.5%、DELL +5.4%、HPE +5.2%（headlines.md 0節）。NVDA決算が材料とする見出し（Motley Fool 11/17「Nvidia ... Soars in After Hours」）。個別の材料は見つからなかった。
- SNDK（保有）: 時間外 +5.5%。個別の材料の見出しは見つからなかった（NVDA決算後の上げの中）。
- SMCI（候補）: 時間外 +5.2%。個別の材料の見出しは見つからなかった。

## SNDK
- 時間外 +5.5%。個別の材料の見出しは見つからなかった。
- 11/13 Yahoo Finance「Why Sandisk Stock Is Falling Today」、11/17 Motley Fool「Why Sandisk Stock Keeps On Going Down」（中身は未確認）。ドラッケンミラーのファンドがSandiskを手放した（Benzinga 11/17）。
- 悪材料: あり（上記の下落報道。内容は未確認）

## AMD
- 時間外 +3.7%。11/16 Trefis「Why Did AMD Stock Fall Nearly 9%?」（原因は未確認）。
- 悪材料: 確認できず（上記は規制・大口の売却の報道）

## SMCI
- 11/12 Barron's「Super Micro Stock Falls as DOJ Probes Smuggling Allegations」（司法省が密輸疑惑を調査）。
- 11/17 24/7 Wall St.「Super Micro Falls 4% ... New U.S. Export Curbs Deepen China Problem?」。次回決算 2027-02-02（scan.md、公式発表の有無は取得不可）。
- 悪材料: あり（DOJの調査、輸出規制）

## IBM
- 悪材料: 確認できず

## INTU
- 決算は11/19（Investing.com 11/12「stock may move 5.2%」）。11/17 TradingView: ソフト株（Adobe・DocuSign・MongoDB・Workdayなど）と一緒に下落。個別の原因は見つからなかった。
- 決算: 直近の四半期のBeat/Miss・ガイダンス・予想の修正は取得不可（検索で確認できず）。予想の修正（直近30日）: 確認できず。
- 悪材料: 確認できず（決算が2日後）

## 急落3社（CRM・NOW・WDAY）
- 個別の原因となる見出しは見つからなかった。同日にソフト株が一斉に下落（TradingView 11/17）。

## テーマ全体に関わる大きなニュース（直近1週間）
- フアン氏の辞任（11/12）とNVDAの後任探し（BigGo 11/13）。
- WebSearch5回（ソフト株下落・NSA障害・NVDA決算・AAOI・INTU決算）は11/17当日の記事が得られず取得不可。

# ニュースの見出し（プログラムが自動で取得）

- Googleニュース（日付を指定）とYahooファイナンスの見出しを `tools/news_headlines.py` が自動で並べたもの。日付は米国東部時間の配信日（引け後の記事は翌日付）。原因の判断・売買の判断はしていない。
- 調べた銘柄の選び方: ①保有 ②今日の候補 ③時間外に±5%以上動いた監視銘柄 は全部、④引けまでに大きく動いた銘柄（1週で±5%のグループの上位3・1日で±7%）は合計12銘柄まで。
- 1週で−5%以下のグループ: 半導体製造装置・材料・設計ソフト・計測（-5.4%）
- 1週で+5%以上のグループ: なし

## 0. 時間外（引け後）の値動き（2026-11-17 の引けから、Yahoo。±3%以上の監視銘柄と、保有・候補は全部）

| 銘柄 | 区分 | 引け | 時間外 | 騰落率 |
|---|---|---|---|---|
| NBIS | 監視 | 105.99 | 117.90（18:03 ET） | **+11.2%** |
| CRWV | 監視 | 49.92 | 54.32（18:03 ET） | **+8.8%** |
| ALAB | 監視 | 211.81 | 225.60（18:02 ET） | **+6.5%** |
| LITE | 監視 | 560.27 | 595.00（18:02 ET） | **+6.2%** |
| ARM | 監視 | 183.33 | 194.55（18:02 ET） | **+6.1%** |
| COHR | 監視 | 210.94 | 223.80（18:02 ET） | **+6.1%** |
| SNDK | 保有 | 797.60 | 841.85（18:02 ET） | **+5.5%** |
| MRVL | 監視 | 148.81 | 157.06（18:02 ET） | **+5.5%** |
| VRT | 監視 | 190.32 | 200.77（18:02 ET） | **+5.5%** |
| DELL | 監視 | 322.90 | 340.24（18:02 ET） | **+5.4%** |
| HPE | 監視 | 46.08 | 48.50（18:00 ET） | **+5.2%** |
| SMCI | 候補 | 24.15 | 25.40（18:02 ET） | **+5.2%** |
| LRCX | 監視 | 210.68 | 220.77（18:02 ET） | +4.8% |
| TER | 監視 | 234.80 | 246.00（18:02 ET） | +4.8% |
| GLW | 監視 | 108.47 | 113.63（18:02 ET） | +4.8% |
| CIEN | 監視 | 264.60 | 277.01（18:02 ET） | +4.7% |
| MU | 監視 | 712.42 | 745.58（18:02 ET） | +4.7% |
| FLEX | 監視 | 73.11 | 76.45（17:59 ET） | +4.6% |
| NVDA | 監視 | 155.46 | 162.30（18:02 ET） | +4.4% |
| STX | 監視 | 503.99 | 526.00（18:00 ET） | +4.4% |
| AMAT | 監視 | 349.22 | 364.00（18:02 ET） | +4.2% |
| WDC | 監視 | 283.53 | 294.65（18:02 ET） | +3.9% |
| ORCL | 監視 | 115.05 | 119.55（18:02 ET） | +3.9% |
| ASML | 監視 | 1383.91 | 1435.00（18:02 ET） | +3.7% |
| AMD | 保有 | 503.69 | 522.18（18:02 ET） | +3.7% |
| KLAC | 監視 | 144.41 | 149.50（18:01 ET） | +3.5% |
| ANET | 監視 | 186.49 | 193.00（18:02 ET） | +3.5% |
| MPWR | 監視 | 1319.34 | 1362.99（18:01 ET） | +3.3% |
| IBM | 候補 | 231.14 | 231.75（17:59 ET） | +0.3% |
| INTU | 候補 | 320.73 | 320.68（17:40 ET） | -0.0% |

## 1. 市場全体（2026-11-17）

### 市場全体（英語のまとめ記事）
検索語: `stocks Wall Street close Nasdaq`
- 11/17 Reuters | Wall Street ends lower ahead of Nvidia results, focus turns to Anthropic debut
- 11/17 Investor's Business Daily | Stock Market Today: Dow Dives, Nvidia Falls Amid This Jensen Huang Offer; Cyber Plays Mixed
- 11/17 Eurasia Business News | Stock Market Today, November 17, 2026 : Nvidia Earnings Loom as Wall Street Awaits First Report Without Jensen Huan, Dow and Nasdaq Slide
- 11/17 Kiplinger | Dow Dives 848 Points as NSA Outage Wrecks Tech: Stock Market Today
- 11/17 24/7 Wall St. | Stock Market Today: Nvidia's 26% Plunge Puts Wall Street on Edge Ahead of Earnings Tonight

### 市場全体（Stock Market Today）
検索語: `"stock market today"`
- 11/17 Bloomberg.com | Stocks Fall in Countdown to Nvidia’s Earnings Test: Markets Wrap

### 市場全体（日本語のまとめ記事）
検索語: `米国株式市場 OR NY株`
- 11/17 日本経済新聞 | NY株ハイライト 市場心理冷やすインフラ障害 エヌビディア・ショックに追い打ち
- 11/17 Yahoo!ニュース | 米国株式市場＝続落、エヌビディア決算・アンソロピック上場控え（ロイター）
- 11/17 Reuters | 米国株式市場＝続落、エヌビディア決算後はアンソロピック上場に焦点
- 11/17 四国新聞 | ＮＹ株一時１０００ドル超安／ＡＩ懸念で５カ月ぶり安値
- 11/17 ニューズウィーク日本版 | 米国株式市場＝続落、エヌビディア決算・アンソロピック上場控え

### 半導体・AI株（英語）
検索語: `chip stocks OR semiconductor stocks OR AI stocks`
- 11/17 Yahoo Finance | 5 Best Blue Chip Stocks to Buy and Hold for 3 Years
- 11/17 AFP.com | Stocks slide ahead of Nvidia's post-scandal earnings report
- 11/17 Bloomberg.com | Chip Stocks Slide as US Sets New Curbs on China’s Compute Access
- 11/17 Benzinga | Druckenmiller's Duquesne Gives Chip Stocks the Boot: Exits AMD, Sandisk and More
- 11/17 Seeking Alpha | Chip stocks pare losses after Huang says he would return as Nvidia CEO if asked (NVDA:NASDAQ)

### 信用（社債・借金）
検索語: `AI debt OR bonds OR credit spreads OR CDS`
- 11/17 Bloomberg.com | Pimco Says AI Bond Spreads May Tighten as Data Center Boom Slows
- 11/17 CNBC | Apollo CEO Marc Rowan warns neocloud financing access could 'disappear'
- 11/17 The Dark Side Of The Boom | The $545 Billion AI Financing Problem: Who Carries the Risk?
- 11/17 Moomoo | PIMCO: As the data center construction boom cools, AI bond spreads may narrow
- 11/17 Forbes | The Best CD Rates Of November 2026 (Up To 5.30% APY)

### 「〇〇ショック」の呼び名（日本語）
検索語: `ショック 株`
- 11/17 山陽新聞 | 投資家の桐谷さん、新たに買った株を発表 画像で紹介「株価を見ると」
- 11/17 Moomoo | 速報：FRBのタカ派シグナルがAI株に打撃

### 引け後・時間外の動き（英語）
検索語: `"after hours" OR "after the bell" OR "extended trading" stocks`
- 11/17 The Motley Fool | Stock Market Today, Nov. 17: Nvidia Slides Ahead of Earnings but Soars in After Hours Trading
- 11/17 Yahoo Finance | Nvidia’s First Report Without Jensen Huang: $115.8 Billion in Revenue, a $130 Billion Forecast, and the Stock Is Up 2.3% After Hours
- 11/17 ChartMill | After-Hours Small-Cap Movers: Gainers and Losers After Today's US Close
- 11/17 Benzinga | Applied Optoelectronics Stock Tumbles After Hours: Here's Why
- 11/17 Banyan Hill Publishing | One Of The Top-5 Craziest Charts I’ve EVER Seen
- 11/17 TradingKey | Nvidia Q3 Revenue Surges 103%, Next-Quarter Revenue Guidance Reaches $130 Billion, Shares Briefly Rise Over 4% After Hours
- 11/17 Livewire Markets | Live blog - NVIDIA stock rises in after-hours trading after revenue soars 103%

### 引け後・時間外の動き（日本語）
検索語: `時間外 決算 株`
- 11/17 Yahoo!ファイナンス | エヌビディア、決算受け時間外で株価上昇＝米国株個別速報(株探ニュース)
- 11/17 BigGo ファイナンス | エヌビディア、市場予想を上回る決算 自社株買い枠を2,270億ドルに拡大、時間外で株価上昇
- 11/17 日本経済新聞 | NVIDIA株、時間外で一時3%超高 業績拡大を好感
- 11/17 株探 | １８日の株式相場見通し＝反発、エヌビディアは決算後に時間外で上昇
- 11/17 Investing.com - FX | 株式市場 | ファイナンス | 金融ニュース | NVIDIA株、時間外で一時3%超高、第3四半期は売上高2倍で市場予想超え
- 11/17 Yahoo!ファイナンス | エヌビディア、決算受け時間外で上昇 数字に関してはひとまず一定の安心感＝米国株個別(株探ニュース)
- 11/17 BeInCrypto | ジェンスン・フアン氏最後の四半期好決算 エヌビディア株は氏抜きで回復可能か

### 買収・合併（英語）
検索語: `acquisition OR acquire OR merger OR takeover chip OR semiconductor OR AI OR optical`
- 11/17 OrangeSlices AI | USSOCOM Seeks Commercial Acquisition Platform with Embedded Super Intelligence
- 11/17 Fierce Healthcare | HLTH 2026 Daily Tracker: Oura, Counsel Health CEOs talk $625M acquisition; HHS' Chris Klomp on the leap from startups to Medicare
- 11/17 Digital Music News | ElevenLabs Finalizes $100M Acquisition of Kotoba Voice AI
- 11/17 Reuters | Foxconn plans to acquire Sony Semiconductor Solutions' automotive camera module business
- 11/17 Traders Union | SoundHound AI completes LivePerson acquisition and announces job cuts: Can SOUN continue to fall?
- 11/17 TradingView | Abits Group Signs Letter of Intent to Acquire Boston Solar, Advancing Vertically Integrated AI Infrastructure Strategy
- 11/17 Bloomberg.com | Google Buys AI Scheduling Tool Howie in Latest Agents Push
- 11/17 OC3D | AMD strengthens its AI stack with Taalas acquisition

## 2. 保有・候補・時間外で大きく動いた銘柄（2026-11-11〜2026-11-17 の見出し）

### SNDK（Sandisk Corporation、保有、AIサーバー・ストレージ・メモリ・端末、前日比 -1.5%、1週 -7.3%、時間外 +5.5%）

#### Googleニュース
検索語: `Sandisk stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/11 Barron's | Why Sandisk and Lumentum Are Leading the AI Comeback
- 11/13 Yahoo Finance | Why Sandisk Stock Is Falling Today
- 11/13 Trefis | SanDisk Stock At $937: Why So Cheap?
- 11/17 The Motley Fool | Why Sandisk Stock Keeps On Going Down

#### Yahooファイナンス
検索語: `SNDK`
- 11/17 Barrons.com | Nvidia, Intel, Salesforce, SpaceX, Anthropic, Sandisk, Home Depot, and More That Explain Today’s Market
- 11/17 GuruFocus.com | Hedge Fund That Lost 67% Makes New Bets on 3 Popular AI Stocks
- 11/17 GuruFocus.com | Micron, SanDisk and SK Hynix Face New Warning From Wall Street

### AMD（Advanced Micro Devices, Inc.、保有、半導体、前日比 -0.2%、1週 -2.3%、時間外 +3.7%）

#### Googleニュース
検索語: `Advanced Micro Devices stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/14 The Motley Fool | Why Advanced Micro Devices Stock Surged This Week
- 11/14 Moomoo | Advanced Micro Devices (AMD) Stock Sinks 9%: What the Options Flow and Dark Pools Say Now
- 11/15 CNN | AMD Stock Quote Price and Forecast
- 11/16 Trefis | Why Did AMD Stock Fall Nearly 9%?

#### Yahooファイナンス
検索語: `AMD`
- 11/17 24/7 Wall St. | Billionaire David Tepper Grew His SpaceX Stake 17-Fold While Dumping AMD and Broadcom
- 11/17 Business Wire | ASUS Showcases Full-Stack AI Infrastructure at SC26, Featuring Intel and AMD Platforms
- 11/17 GuruFocus.com | AMD Stocks Decrease 1.62% as New US Rule Requires Licenses for Five Chip Hubs

### IBM（International Business Machines Corporation、候補、AIプラットフォーム・クラウド、前日比 -4.7%、1週 -5.5%、時間外 +0.3%）

#### Googleニュース
検索語: `International Business Machines stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/12 MarketBeat | International Business Machines (NYSE:IBM) Stock Falls 1.3% - Time to Sell?
- 11/16 Benzinga | IBM Stock Moves Lower: What's Going On?
- 11/17 Yahoo Finance | Is Trending Stock International Business Machines Corporation (IBM) a Buy Now?
- 11/17 Traders Union | Why is IBM stock down 1.9% today?

#### Yahooファイナンス
検索語: `IBM`
- 11/17 24/7 Wall St. | IBM Is Down 21% This Year. What Will It Take to Get IBM Stock Back to $250?
- 11/17 CIO Dive | Chief AI officers lack control over enterprise AI investment decisions
- 11/17 GlobeNewswire | Fresche Solutions and Amdocs Partner to Accelerate IBM i and IBM z Modernization

### INTU（Intuit Inc.、候補、AIソフト・セキュリティ・ITサービス、前日比 -7.2%、1週 -5.8%、時間外 -0.0%）

#### Googleニュース
検索語: `Intuit stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/12 Yahoo Finance | Intuit (INTU) Expected to Beat Earnings Estimates: Can the Stock Move Higher?
- 11/12 Investing.com | Intuit stock may move 5.2% on Nov. 19 earnings release
- 11/13 Benzinga | Intuit Inc (INTU) Stock Price, Quote, News & History
- 11/17 TradingView | Adobe, DocuSign, Intuit, MongoDB, and Workday shares are falling, what you need to know

#### Yahooファイナンス
検索語: `INTU`
- 11/16 Simply Wall St. | UiPath Stock And Other Software Picks Built For Higher AI Costs
- 11/17 Barrons.com | Boom Goes the Stock Market
- 11/17 Barrons.com | Broad Selloff Leaves Few Places to Hide

### SMCI（Super Micro Computer, Inc.、候補、AIサーバー・ストレージ・メモリ・端末、前日比 -3.6%、1週 -13.1%、時間外 +5.2%）

#### Googleニュース
検索語: `Super Micro Computer stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/12 Barron's | Super Micro Stock Falls as DOJ Probes Smuggling Allegations
- 11/12 Benzinga | What's Going On With Super Micro Computer Stock Thursday?
- 11/17 Yahoo Finance | What Is Driving The Move In Super Micro Computer Stock?
- 11/17 Investing.com | Why is Super Micro Computer stock sliding today?

#### Yahooファイナンス
検索語: `SMCI`
- 11/17 24/7 Wall St. | Super Micro Falls 4%, Dell and Hewlett Packard Enterprise Slide 2%: Do New U.S. Export Curbs Deepen Super Micro’s China Problem?
- 11/17 Investing.com | Muddy Waters shorts Nvidia, raises questions about possible executive connection
- 11/17 Investing.com | SMCI support and resistance as stock trades near key levels

### NBIS（Nebius Group N.V.、AIプラットフォーム・クラウド、前日比 -1.0%、1週 -20.9%、時間外 +11.2%）

#### Googleニュース
検索語: `Nebius stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/12 Barron's | Nebius Stock Plummets After Earnings as CEO Warns of Revenue Delay
- 11/12 CNBC | Nebius falls 16% as company expects increased 2026 capex spend, issues weak outlook
- 11/12 Yahoo Finance | Nebius shares fall despite beating Q3 estimates
- 11/15 The Motley Fool | Why Is Nebius Stock Crashing, and is it a Buying Opportunity?

#### Yahooファイナンス
検索語: `NBIS`
- 11/17 24/7 Wall St. | Michael Burry Closed His Oracle Puts, but Oracle Is Still Down 38% This Year. What Will It Take to Get ORCL Stock Back to $200?
- 11/17 24/7 Wall St. | Nebius Will Reach True Profitability Just Before CoreWeave But Here’s Who Grows Faster After That
- 11/17 Barrons.com | Nvidia Sold a Quarter of Its Intel Stake

### CRWV（CoreWeave, Inc.、AIプラットフォーム・クラウド、前日比 +0.0%、1週 +2.4%、時間外 +8.8%）

#### Googleニュース
検索語: `CoreWeave stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/11 CNBC | CoreWeave soars more than 24% for best day since April 2025 after strong Q3 report
- 11/12 Yahoo Finance | CoreWeave stock sinks as resignation of Jensen Huang ripples through AI trade
- 11/12 Barron's | CoreWeave Stock Dives. It's in the Nvidia Danger Zone With These Other AI Plays.
- 11/12 Trefis | CoreWeave Stock Jumps 25%: Does The Anthropic IPO Help?

#### Yahooファイナンス
検索語: `CRWV`
- 11/17 Barrons.com | Nvidia Bet Big on AI Stocks. Now They’re Getting Hit.
- 11/17 Barrons.com | Nvidia's Complex Orbit
- 11/17 Barrons.com | Why Goldman Sachs Thinks the Bull Market Will Keep Raging

### ALAB（Astera Labs, Inc.、半導体、前日比 +4.6%、1週 -2.1%、時間外 +6.5%）

#### Googleニュース
検索語: `Astera Labs stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/14 Yahoo Finance | Astera Labs (ALAB) Stock May Be 21% Below Fair Value Despite Strong Q4 Guidance
- 11/16 TradingView | Astera Labs Stocks Sink 6.95% Despite Guiding Revenue Up 26% Next Quarter
- 11/16 Quiver Quantitative | Astera Labs Slides as Chip Selloff and Post-Earnings Profit-Taking Weigh on Shares
- 11/17 Yahoo Finance | Why Is Astera Labs Stock Falling Again?

#### Yahooファイナンス
検索語: `ALAB`
- 11/16 GuruFocus.com | Lee Ainslie's Top Q3 2026 Move: Astera Labs Inc at a -4.54% Portfolio Impact
- 11/16 MT Newswires | Astera Labs, TD Synnex Unit Expand Collaboration to Speed Up AI Inference Deployments

### LITE（Lumentum Holdings Inc.、光・通信・ネットワーク、前日比 +2.6%、1週 -4.4%、時間外 +6.2%）

#### Googleニュース
検索語: `Lumentum stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/11 Benzinga | Why Is Lumentum Stock Soaring Today?
- 11/16 Yahoo Finance | Lumentum (LITE) Got a Takeover Offer. What Does It Mean for Holders? (
- 11/17 Investing.com | Why is Lumentum stock rallying today?

#### Yahooファイナンス
検索語: `LITE`
- 11/17 24/7 Wall St. | Coherent Jumps 8%, Applied Optoelectronics Climbs 7% as U.S. Pushes Ahead With Curbs on Chinese Optical Gear; Lumentum Gains 4%
- 11/17 24/7 Wall St. | Nvidia Isn’t the Whole AI Story. This Stock Could Prove It
- 11/17 GuruFocus.com | AXT Faces Supplier Switch Risk if US-China Tensions Flare

### ARM（Arm Holdings plc、半導体、前日比 +4.8%、1週 +1.0%、時間外 +6.1%）

#### Googleニュース
検索語: `Arm stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/13 Traders Union | ARM slides over 5% as the stock trades below key moving averages and faces ongoing selling pressure
- 11/13 BigGo Finance | Arm Stock Tumbles 6% as Nvidia Board Courts CEO Rene Haas to Replace Jensen Huang
- 11/13 AOL.com | Why Arm Holdings Stock Was Pulling Back Today
- 11/17 Investing.com | Why is Arm stock rallying today?

#### Yahooファイナンス
検索語: `ARM`
- 11/16 GuruFocus.com | Arm Stocks Slide 6.72% as Nvidia CEO Search Keeps Rene Haas in Focus
- 11/16 Motley Fool | Why Arm Holdings Plunged Today
- 11/16 Simply Wall St. | Arm Holdings (ARM) Stock Dropped, So What Is Driving Attention Now?

### COHR（Coherent Corp.、光・通信・ネットワーク、前日比 +3.7%、1週 -1.8%、時間外 +6.1%）

#### Googleニュース
検索語: `Coherent stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/11 24/7 Wall St. | Applied Optoelectronics Surges 12%, Lumentum Jumps 11% as CoreWeave's Results Revive AI Trade; Coherent Climbs 7%
- 11/13 Investing.com | Why is Coherent stock tumbling today?
- 11/13 StreetInsider | Coherent stock falls amid Nvidia leadership change

#### Yahooファイナンス
検索語: `COHR`
- 11/17 24/7 Wall St. | Sam Altman Just Delivered a Warning to Investors Betting on Endless AI Growth
- 11/17 Insider Monkey | 5 Highest Short Interest Large-Cap Tech Stocks Right Now

### MRVL（Marvell Technology, Inc.、半導体、前日比 +2.3%、1週 -3.7%、時間外 +5.5%）

#### Googleニュース
検索語: `Marvell stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/12 Yahoo Finance | Marvell Technology, Inc. (MRVL) is Attracting Investor Attention: Here is What You Should Know
- 11/13 Yahoo Finance | Marvell Stock Could Have a Bigger AI Opportunity Than Investors Realize
- 11/17 Trefis | What Sent Marvell Stock Down Over 7%?

#### Yahooファイナンス
検索語: `MRVL`
- 11/17 24/7 Wall St. | Wall Street Is Watching Nvidia. This AI Stock Deserves Attention Too

### VRT（Vertiv Holdings Co、データセンターの電力・冷却・部品・受託製造・建設、前日比 +0.9%、1週 -2.0%、時間外 +5.5%）

#### Googleニュース
検索語: `Vertiv stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/11 Benzinga | Why Is Vertiv Stock Surging Wednesday? - Vertiv Holdings (NYSE:VRT)
- 11/13 Yahoo Finance | Why Should Vertiv Stock Holders Keep Watching This Number?
- 11/17 Barron's | Why Vertiv’s Big AI Data Center Power Breakthrough Couldn’t Save the Stock Today
- 11/17 Trefis | What Moved Vertiv Stock Nearly 7% Lower?

#### Yahooファイナンス
検索語: `VRT`
- 11/17 24/7 Wall St. | Steve Eisman Says the Biggest AI Risk Is Local Governments Slowing Data Center Construction
- 11/17 GlobeNewswire | Data Centre HVAC Markets and Competition Analysis Report 2026-2030 | Capitalize on 9.2% CAGR and $6 Billion in Revenue Growth with Schneider Electric, Daikin, Vertiv and LG

### DELL（Dell Technologies Inc.、AIサーバー・ストレージ・メモリ・端末、前日比 +0.7%、1週 -3.5%、時間外 +5.4%）

#### Googleニュース
検索語: `Dell stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/16 Trefis | Why Is Dell Stock Falling Again?
- 11/16 Barron's | Dell and HPE Stocks Are Getting Hammered. Why the Selloff May Be Overdone.
- 11/17 Yahoo Finance | What Triggered Dell Stock's 7% Drop?
- 11/17 Barchart.com | GF Securities Just Slashed Its Price Target on Dell Stock. Here's Why.

#### Yahooファイナンス
検索語: `DELL`
- 11/17 24/7 Wall St. | Jensen Huang Offered to Come Back and Nvidia Gained $90 Billion in 10 Minutes. Here’s What the Stock Did the Last Four Times a Board Took the Boss Back
- 11/17 24/7 Wall St. | Michael Dell Gave 25 Million American Kids $6.25 Billion. More Than 90% Still Haven’t Claimed It.

### HPE（Hewlett Packard Enterprise Company、AIサーバー・ストレージ・メモリ・端末、前日比 -1.0%、1週 -3.8%、時間外 +5.2%）

#### Googleニュース
検索語: `Hewlett Packard Enterprise stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/12 Yahoo Finance | How Risky Is Hewlett Packard Enterprise Stock?
- 11/13 Moomoo | HPE Slides as AI Infrastructure Stocks Face Fresh Pressure

#### Yahooファイナンス
検索語: `HPE`
- 11/17 Business Wire | Sparxity Appoints former Cray CEO Peter Ungaro and Semiconductor Veteran Daniel Armbrust to its Advisory Board
- 11/17 MT Newswires | Update: Market Chatter: FAA Halts Juniper Router Installations After Flight Outage
