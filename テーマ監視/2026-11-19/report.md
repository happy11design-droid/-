# テーマ監視 2026-11-18

# 判定のまとめ（ルールの判定と著者の判定を分けて表示）

- **ルールの判定**: 採用した売買ルール（スクリプト）が数値で決めたもの。損切りは買値の15%下の逆指値（日中に届けばその場で売れる）。
- **著者の判定**: ノートブックの著者の回答。買いは注文を止める理由があるときだけ【様子見】、保有はルールより早く手じまう理由があるときだけ【売り】。根拠は下の「著者の回答（全文）」。
- 2つが食い違うときに、どちらに従うかはユーザーが決める。

- **テーマ全体の急落（S2・記録だけ）: あり（S2）**（SOXが直近60取引日の最高値から -27.0%）。S2の日の順張りの候補には「S2なら見送る形」と付ける（売買のルールは変えない。記録してから採用を決める。2026-10-14）

- **特殊な下げ（記録だけ）: あり（特殊な下げ）**（2026-10-16から）（SOXが直近60取引日の最高値から -27.0%、前の1年の大きな上げ・雇用の弱さ・物価の再加速のうち 2つ）。1995年〜では、この形の後にSOXの下げが長引くことが多かった（後知恵を含む）。売買のルールは変えない（2026-11-03）

## 保有銘柄

| 銘柄 | ルール | 損益 | 時間外 | ルールの判定 | ルールの判定の理由 | 著者の判定 |
|---|---|---|---|---|---|---|
| SNDK | ルール外（ユーザーの判断。この日はどのルールの合図もなし） | -43.4% | -1.1% | **売り** | 終値 776.22 が損切り価格 1165.61 以下 | 【未判定】（） |
| AMD | ボリンジャーIII | -3.6% | -1.1% | 保有継続 | 損切り 467.47（終値から -11.8%） | 【保有継続】（ボリンジャー） |

## 候補の判定（並びは上の「買う順番」の表と同じ）

- 並びは上の「買う順番」の表と同じ（RSの高い順。勝率の高い順ではない）。注文の値段・株数・逆指値は上の表を見る。勝率・1回平均は、そのルールの過去の成績（後知恵なしの監視銘柄・2015年〜の全部の合図）。
- 空き枠: 3（同時保有4銘柄まで。保有2、うちルールの売り1）。著者が【様子見】の候補を見送るかはユーザーが決める。

| 順 | 銘柄 | ルール | 過去の勝率 | 過去の1回平均 | RS | 時間外 | ルールの判定 | 著者の判定 |
|---|---|---|---|---|---|---|---|---|
| 1 | ACN（アクセンチュア） | 逆張り: ボリンジャー メソッドIII | 68% | +1.5% | 80 | -0.0% | 買い（翌日の寄り付き） | 【買い】（ボリンジャー） |
| 2 | IBM（IBM（アイ・ビー・エム）） | 逆張り: ボリンジャー メソッドIII | 68% | +1.5% | 23 | +0.0% | 買い（翌日の寄り付き） | 【買い】（ボリンジャー） |
| 3 | INTU（イントゥイット） | 逆張り: ボリンジャー メソッドIII | 68% | +1.5% | 7 | -0.2% | 買い（翌日の寄り付き） | 【買い】（ボリンジャー） |
| 4（枠外） | SMCI（スーパー・マイクロ・コンピューター） | 逆張り: 急落の底（担当: コナーズ）（指値の2日目） | 65% | +2.1% | 3 | -0.2% | 買い（指値 23.66、3取引日まで） | 【様子見】（コナーズ） |

- 時間外: 前の取引日の引けから、引け後（米国東部時間16〜20時）の最後の値までの騰落率（Yahoo。±5%以上は太字）。寄り付きの値段は、表の注文の目安（前日の終値で計算）から大きくずれることがある。原因の見出しは「ニュースの見出し」の節。

# 著者の回答（全文）

## 0_テーマの局面_ワインスタイン

1. **テーマ全体の局面**: 【ステージ3】（急騰後に30週線が横ばい化し指数が下回る天井圏。第2章 [1]）
2. **グループごとの局面**:
- 半導体｜ステージ3｜30週線横ばい
- 半導体製造装置・材料・設計ソフト・計測｜ステージ3｜30週線横ばい
- AIサーバー・ストレージ・メモリ・端末｜ステージ3｜30週線横ばい
- 光・通信・ネットワーク｜ステージ3｜30週線横ばい
- データセンターの電力・冷却・部品・受託製造・建設｜ステージ4｜30週線下落
- AIプラットフォーム・クラウド｜ステージ3｜30週線横ばい
- AIソフト・セキュリティ・ITサービス｜ステージ2｜30週線上昇
3. **転換の兆し**: 出ている。①30週線横ばい・乖離-11.3%でステージ4転落危機（第2章 [2]）②RS悪化（第4章 [3]）③50日線上17%と内部崩壊（第8章 [4]）④データセンターが第4ステージ入り（第7章 [5]）。※雇用・物価・ニュースはマニュアルに規定なし（第1章 [6]）。
4. **テーマの外**: 判定不能（ヒートマップ省略のため）。

（全体の版が空の応答だったため、1〜2節だけの短い版で送り直した回答。ヒートマップ・急騰急落・ニュースは渡していない）

## 1_コナーズ_prompt_1

## SMCI
1. **投資判断**: 【様子見】（200日線下のため見送り）
2. **止める理由の確認**:
- 本が禁じる形・状況｜あり｜第4章（現在値24.37が200日線32.47の下 [1, 2]）
- 避けるべき時期（決算など）｜なし｜第11章（決算76日後、月初3〜8日外 [1, 3]）
- 悪材料｜なし｜マニュアルに規定なし（第2・3章、報道は織り込み済み [4, 5]）
3. **現状パターンと価格**:
- 現状パターン: A（急落条件成立だが禁止状況）
- 本日の発注: 見送り（注文なし）
4. **注意点**: 200日移動平均線の上側に復帰するまで買いは厳禁 [1, 2]。

## 1_ボリンジャー_prompt_1

## AMD
1. **投資判断**: 【保有継続】（ルールより早期に手仕舞うべき根拠なし）[1, 2]
2. **止める理由の確認**:
   - 本が禁じる形・状況｜なし｜天井型Mトップ未形成、上部バンド未到達（第13章、第20章）[2, 3]
   - 避けるべき時期（決算など）｜なし｜次回決算（2027/02/02）まで日数あり（マニュアルに規定なし）[4]
   - 悪材料｜なし｜個別の悪材料は見当たらず（マニュアルに規定なし）[4]
3. **現状パターンと価格**:
   - 保有中: `売りの予約注文: 〈指値売り〉600.61（現在値比 +13.3%）`
4. **注意点**: 目標の上部バンド到達（第20章）[2]まで指値を維持し、設定済みの損切りラインを厳守してください[1]。

## 1_ボリンジャー_prompt_2

## ACN
1. **投資判断**: 【買い】（止める理由なし） [1, 2]
2. **止める理由の確認**:
- 本が禁じる形・状況｜なし｜第20章（%b<0.05かつ21日II%>0の買いセットアップ成立） [1, 2]
- 避けるべき時期（決算など）｜なし｜次回決算まで29日（マニュアルに規定なし） [3]
- 悪材料｜判定不能｜ニュース情報省略のため判定不能
3. **現状パターンと価格**:
- 現状パターン: A（%b・II%条件合致） [1, 2]
- 本日の発注: 翌日の寄り付きで成行
4. **注意点**: 目標は上部バンドのタグ、損切りは直近安値付近に設定すること（第20章） [4-6]。

## 1_ボリンジャー_prompt_3

## IBM
1. **投資判断**: 【買い】（メソッドIII成立）
2. **止める理由の確認**:
- 本が禁じる形・状況｜なし｜第20章（%b<0.05かつ21日II%>0に合致）
- 避けるべき時期（決算など）｜なし｜次回決算まで70日（第4章）
- 悪材料｜なし｜個別悪材料なし（マニュアルに規定なし）
3. **現状パターンと価格**:
- 現状パターン: A（%b・II%条件成立）
- 本日の発注: 翌日の寄り付きで成行
4. **注意点**: 直近安値に損切りを置き、上部バンド到達を手じまい目標とすること（第20章）。

## 1_ボリンジャー_prompt_4

## INTU
1. **投資判断**: 【買い】（セットアップ成立、阻止理由なし）
2. **止める理由の確認**:
- 本が禁じる形・状況｜なし｜第20章（%b<0.05かつ21日II%>0成立）
- 避けるべき時期（決算など）｜なし｜マニュアルに規定なし
- 悪材料｜判定不能｜ニュース省略のため判定不能
3. **現状パターンと価格**:
- 現状パターン: A（メソッドIII条件成立）
- 本日の発注: 翌日の寄り付きで成行
4. **注意点**: 翌日決算に伴う場外ギャップや指標の歪み（第22章）に留意。

# スキャン（数値と事実）


- 監視銘柄 87（判定できたのは 87）。
- この一覧は数値と事実だけ。売買の判断は著者のノートブックが行う。

## 1. テーマ（グループ）の強さ

| グループ | 銘柄数 | 1週 | 1カ月 | 3カ月 | 3カ月の順位 | 50日線より上の銘柄の割合 | グループ指数の30週線の局面（線との乖離、4週前からの線の傾き） |
|---|---|---|---|---|---|---|---|
| 半導体 | 16 | -6.6% | -9.0% | -2.6% | 2位 | 25% | 横ばい（-13.8%、+4.1%） |
| 半導体製造装置・材料・設計ソフト・計測 | 9 | -9.1% | -13.0% | -20.2% | 6位 | 0% | 横ばい（-18.3%、+0.5%） |
| AIサーバー・ストレージ・メモリ・端末 | 9 | -8.0% | -20.9% | -27.9% | 7位 | 11% | 横ばい（-16.1%、+5.5%） |
| 光・通信・ネットワーク | 9 | -3.6% | -8.9% | -16.7% | 5位 | 22% | 横ばい（-15.8%、+0.4%） |
| データセンターの電力・冷却・部品・受託製造・建設 | 19 | -3.9% | -6.4% | -8.9% | 4位 | 11% | 下落（-10.7%、-0.0%） |
| AIプラットフォーム・クラウド | 11 | -3.8% | -11.2% | -1.5% | 1位 | 27% | 横ばい（-8.9%、+1.1%） |
| AIソフト・セキュリティ・ITサービス | 14 | -6.6% | -11.9% | -7.2% | 3位 | 21% | 上昇（+0.9%、+4.6%） |

## 2. テーマ全体の状態と早めの警告

- 市場全体の30週線による局面: S&P500指数 **横ばい**／NASDAQ100指数 **横ばい**（急落の底で買うルールは、過去の検証で下落相場で特に強く、横ばいの相場では負けていた）
- **2倍ETFを使う局面（案1、2026-10-13 採用）: S&P500の20週線（100日線）で 横ばい** → 新しく買う銘柄は、2倍ETFのある銘柄も元の株で買う（保有中のETFはそのまま）（SPY 730.20、100日線 759.21、20日前の線 756.42。上昇＝線より上かつ線が上向き）
- **テーマ全体の急落（S2、記録だけ。売買のルールは変えない）: あり（S2）**（SOX 9652.80、直近60取引日の最高値 13217.82 から -27.0%。S2＝最高値から−10%以上）。S2のときに「順張りの新しい買いだけ止める」形を記録で比べる（2026-10-14 ユーザー決定。バックテストでは年率は上がったが2つの期間ではどちらも少し下回ったため、記録してから採用を決める。`バックテスト結果/テーマ全体の急落を検知して手じまう・買いを止める.md`）
- **グループごとの悪いニュースの流れ（記録だけ。売買のルールは変えない。2026-11-05〜2026-11-18）**: 会社の名前と悪い言葉（格下げ・目標株価の引き下げ・見通しの引き下げ・予想未達・急落・信用・訴訟・輸出規制など）の両方がある見出しの数（Googleニュース、`tools/news_headlines.py`）。10取引日の1銘柄あたりが一番多いグループに印。2026年7〜11月の確かめでは、印のグループの合図は10月は成績が悪かった（1回平均 −10.6%、ほか −5.6%）が、7〜9月は逆に良かった（+11.6%、ほか +6.7%）（`バックテスト結果/実際の運用の期間の確認_2026-10-23/グループの悪いニュースの流れ.md`。2026-11-04）

| グループ | 悪いニュース 直近5取引日 | その前の5取引日 | 10取引日の1銘柄あたり | 良いニュース 10取引日（1銘柄あたり） | 印 |
|---|---|---|---|---|---|
| 半導体（16） | 27件 | 13件 | 2.5 | 27件（1.7） | **悪いニュースが続いている** |
| 光・通信・ネットワーク（9） | 5件 | 12件 | 1.9 | 13件（1.4） |  |
| AIプラットフォーム・クラウド（11） | 10件 | 5件 | 1.4 | 2件（0.2） |  |
| AIサーバー・ストレージ・メモリ・端末（9） | 8件 | 0件 | 0.9 | 17件（1.9） | **良いニュースが多い** |
| 半導体製造装置・材料・設計ソフト・計測（9） | 0件 | 1件 | 0.1 | 5件（0.6） |  |
| データセンターの電力・冷却・部品・受託製造・建設（19） | 2件 | 0件 | 0.1 | 12件（0.6） |  |
| AIソフト・セキュリティ・ITサービス（14） | 1件 | 0件 | 0.1 | 5件（0.4） |  |

印のグループ（半導体）の最近の見出し: 2026-11-18 NVIDIA Corporation Stock 12‑Month Price Target Cut to $269.74, Implies 74% Upside（TradingView）／2026-11-18 NVIDIA Corporation Stock 12‑Month Price Target Cut to $258.53, Implies 66% Upside（TradingView）／2026-11-18 Why Nvidia Stock Is Losing Its Post-Earnings Gains — and Why Another Wall Street Analyst Just Downgraded It（TipRanks）

良いニュースが多いグループ（AIサーバー・ストレージ・メモリ・端末）の最近の見出し: 2026-11-18 Apple Maps gets major upgrade in India: 3D landmarks, street views and smarter directions（News9live）／2026-11-18 Apple iPhone 18 Pro Max review: Better cameras, powerful hardware, but is it time to upgrade?（Moneycontrol.com）

- **特殊な下げ（記録だけ。売買のルールは変えない）: あり（特殊な下げ）**（2026-10-16から）。SOX は直近60取引日の最高値から -27.0%（−15%以下が条件）、●A 前の1年の上げ +99.5%（+80%以上）、・B 雇用の伸び 137千人/月（2026-10まで。10万人未満）、●C 物価 4.0%（2026-09。3か月前 3.7%。3.5%以上で再加速）＝2つ（2つ以上が条件）。1995年〜でSOXが−15%以下かつ条件2つ以上の日は、120日後にSOXが下だったのが69%・250日後が70%（中央値 −33%）、AI以外の8業種の平均は250日後 −7%。ただし条件は過去を見て選んだもの（条件が2つ以上の局面は約5回）で、2026年7〜9月にこの間テーマを買わないと、その後の戻りを逃して2026年の成績は下がった（`バックテスト結果/実際の運用の期間の確認_2026-10-23/特殊な下げと過去の似た下げ.md`。2026-11-03）
- テーマ指数（監視銘柄の等金額平均）の30週線による局面: **横ばい**（上昇＝線より上かつ上向き、下落＝線より下かつ下向き、それ以外＝横ばい。ワインスタインのステージの近似）
- テーマ指数と50日線: 50日線より下（乖離 -11.3%）
- S&P500に対する相対的な強さ: 50日平均より下（S&P500より弱い）
- 監視銘柄のうち50日線より上の割合: 17%
- 警告（割合が40%未満かつテーマ指数が50日線より下）: **出ている**
- 参考（バックテスト）: 30週線の「下落」は高値から10〜33%下げた後に出る遅い判定。50日線・割合・相対的な強さは高値から2〜8%で出るが、誤報が年15回以上ある。警告中に新しい買いを止めると、押し目買い（ボリンジャーIII）の成績は大きく下がった（`バックテスト結果/テーマ監視銘柄・直近3年.md` 11・12節）。

## 3. ヒートマップ（Finviz、全米の業種別の騰落率）

3カ月の騰落率の上位15業種（テーマの外で強くなっている業種の確認用）:

| 順位 | 業種 | 1週 | 1カ月 | 3カ月 | 6カ月 | 1年 |
|---|---|---|---|---|---|---|
| 1 | Medical Distribution | +0.0% | +4.8% | +20.9% | +38.2% | +18.4% |
| 2 | Discount Stores | +1.1% | +8.6% | +19.8% | +1.5% | +24.9% |
| 3 | Advertising Agencies | -2.5% | +31.1% | +18.8% | -9.7% | -20.5% |
| 4 | Lodging | -0.3% | +6.4% | +14.8% | +14.2% | +40.4% |
| 5 | Insurance - Diversified | -2.3% | +5.4% | +13.5% | +17.1% | +13.8% |
| 6 | Consumer Electronics | -0.9% | +3.9% | +13.2% | +16.5% | +29.2% |
| 7 | Household & Personal Products | +0.1% | +4.3% | +11.8% | +17.3% | +14.2% |
| 8 | Insurance - Reinsurance | -2.0% | +1.5% | +10.2% | +17.6% | +36.2% |
| 9 | Grocery Stores | -1.5% | +3.0% | +9.9% | -8.1% | -5.5% |
| 10 | REIT - Hotel & Motel | -1.3% | +4.2% | +9.6% | +23.7% | +54.1% |
| 11 | Paper & Paper Products | -2.2% | +11.4% | +8.7% | +10.2% | +0.5% |
| 12 | Real Estate - Diversified | -3.8% | +5.9% | +8.6% | +13.1% | +10.4% |
| 13 | Diagnostics & Research | -3.1% | -0.3% | +7.9% | +44.5% | +21.2% |
| 14 | Medical Instruments & Supplies | -3.1% | +2.7% | +7.9% | +12.5% | +1.0% |
| 15 | Health Information Services | -9.4% | -5.5% | +7.8% | +44.2% | +9.7% |

テーマの業種の順位（3カ月、全144業種中）: Semiconductors 129位、Semiconductor Equipment & Materials 136位、Computer Hardware 141位、Communication Equipment 122位、Electronic Components 120位、Software - Infrastructure 50位、Software - Application 97位、Internet Content & Information 105位

## 4. 急騰・急落した銘柄（前日比±5%以上、または出来高が50日平均の2倍以上）

原因のニュースをサブエージェントが調べ、候補・保有銘柄の判定材料として著者に渡す。急騰・急落そのものは売買の合図にしない（後知恵のないS&P500全体のバックテストでは、急騰の翌日に買うルールは年率7%、急落の翌日に買うルールは年率9〜10%で、採用した3つのルールより優れていなかった）。

| 銘柄 | グループ | 前日比 | 出来高（50日平均の倍） | 終値 | 50日線 | RS | 局面 |
|---|---|---|---|---|---|---|---|
| PANW | AIソフト・セキュリティ・ITサービス | +9.9% | 2.7倍 | 339.92 | 下 | 97 | 下げ |
| AKAM | 光・通信・ネットワーク | +8.3% | 1.4倍 | 91.70 | 下 | 10 | 下落相場 |
| CRWD | AIソフト・セキュリティ・ITサービス | +7.9% | 1.2倍 | 237.03 | 下 | 98 | 下げ |
| FTNT | AIソフト・セキュリティ・ITサービス | +5.9% | 1.0倍 | 131.81 | 下 | 83 | 下げ |
| AMD | 半導体 | +5.3% | 1.2倍 | 530.14 | 下 | 99 | 下げ |
| FFIV | 光・通信・ネットワーク | +5.2% | 1.0倍 | 321.04 | 下 | 43 | 下げ |
| NVDA | 半導体 | -2.9% | 2.2倍 | 150.96 | 下 | 3 | 下げ |

- 局面（判定式はClaudeが置いたもの）: **上昇相場**＝終値 > 50日線 > 200日線、50日線が20取引日前より2%以上高い、ADX(14) ≧ 20／**下落相場**＝終値 < 50日線 < 200日線、50日線が20取引日前より2%以上低い、ADX(14) ≧ 20／**上げ**＝それ以外で終値が50日線より上、かつ50日線が10取引日前より上か20日線が5取引日前より上／**下げ**＝それ以外で終値が50日線より下、かつ50日線が10取引日前より下か20日線が5取引日前より下（急な下げの初めは50日線がまだ上向きのため20日線でも見る）／**レンジ**＝どれにも当たらない（2026-11-05 から5つ。それまでは上昇相場とレンジの2つだけで、下げている銘柄もレンジと出ていた）。

## 4-2. 監視外の注目銘柄（S&P500・NASDAQ100のうち監視銘柄に入っていない銘柄）

条件: 流動性（株価5ドル以上・50日平均出来高25万株以上）があり、(a) 前日比+8%以上かつ出来高が50日平均の2倍以上、または (b) 終値が直前1年の最高値（終値）を上回り、RS≧90。RSの高い順に5銘柄（ニュースを調べる）。監視銘柄に入れるかはユーザーが決める。

| 銘柄 | 種類 | 前日比 | 出来高（50日平均の倍） | RS | 終値 |
|---|---|---|---|---|---|
| TJX | 急騰 | +8.0% | 2.3倍 | 26 | 140.30 |

## 5. 保有銘柄の手じまい条件（`新分析ツール/保有銘柄.md`）

| 銘柄 | ルール | 買った日 | 買値 | 終値 | 損益 | 損切り価格（買値の15%下、逆指値） | ルールの手じまい条件 | 出来高2倍の大陰線（買った後の直近5日） | 次回決算予定日 |
|---|---|---|---|---|---|---|---|---|---|
| SNDK | ルール外（ユーザーの判断。この日はどのルールの合図もなし） | 2026-10-21 | 1371.30 | 776.22 | -43.4% | 1165.61 | **損切り価格を下回った** ルールが不明（保有銘柄.md の「ルール」を確認） | なし | 2026-10-29 |
| AMD | ボリンジャーIII | 2026-10-21 | 549.97 | 530.14 | -3.6% | 467.47 | **出来高2倍の大陰線が 2026-11-05 に出た**（まだ持っていれば、次の寄り付きで全部売る） 売りの指値: 上部バンド 600.61（今夜この値に置き直す。届いた日に売れる）（2倍ETF AMUU で持っている場合も、判定は元の株 AMD の値段） | なし | 2027-02-02 |

- 出来高2倍の大陰線: 実体（始値−終値）が前日までのATR(14)の1.5倍以上、終値がその日の値幅の下25%以内、出来高が前日までの50日平均の2倍以上の日。**押し目（ボリンジャーIII）・急落の底の保有では売りのルール**: 出たら翌日の寄り付きで全部売り、空いた枠で次の合図を買う（2026-10-02 ユーザー決定。`バックテスト結果/やり直し_売りの合図の組み合わせ.md`。乱数3組とも年率が約+2ポイント、最大下落率もやや下がった）。ミネルヴィニ・新高値V2の保有では事実の表示（順張りに足しても良くならなかった）。

- 半分売りの合図（ミネルヴィニ・新高値V2の保有だけ）: 反転のローソク足（かぶせ線・弱気の包み足・宵の明星・流れ星）＋出来高が50日平均の1.5倍以上＋RSI(14)が前日か当日に70以上。買った後に最初に出た日の翌日の寄り付きで半分売り、残り半分は50日線割れ・損切り15%まで持つ（2026-10-01 ユーザー決定。`バックテスト結果/半分だけ売るとオニールの空き枠.md`）。

- かぶせ線（ミネルヴィニ・新高値V2の保有だけ）: 上昇中の陽線の翌日に、前日の高値より上で寄り付き、前日の陽線の真ん中より下（前日の始値より上）で引けた日。翌日の寄り付きで全部売り、空いた枠で次の合図を買う。半分売りより優先する（2026-10-01 ユーザー決定。`バックテスト結果/2倍ETFで売って買い直す.md`。順張りの売買の25%で出て、1回平均+2.0%、年率 21.4%→26.4%）。

## 5-2. 前日（2026-11-17の引け）の【買い（予約）】の確認

前日の【買い（予約）】はなし。

## 6. 候補（採用したルールの条件が成立＝A。予約（B）は2026-10-25から注文せず、節6-3に参考の表示だけ）

建玉の目安: 同時保有4銘柄まで、1銘柄に資金の25%（資金÷4）、損切りは買値の15%下（ユーザー決定 2026-09-29）。

保有中のため候補から外した銘柄（合図は出ている）: SNDK

パターン: A＝最新の足で採用ルールの条件が成立（押し目・ミネルヴィニ・新高値V2は翌日の寄り付きで成行、急落の底は合図の日の終値の2%下に指値で3取引日待つ。2026-11-03 ユーザー採用）。条件の成立が目前の銘柄（B）は、予約の注文をやめたので節6-3に参考として出す（2026-10-25 ユーザー決定）。

| 銘柄 | グループ | パターン | 種類 | ルールの過去の成績 | 終値 | 前日比 | RS | 50日線の傾き | 局面 | 当てはまった条件 | 次回決算予定日 | 注文の目安 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SMCI | AIサーバー・ストレージ・メモリ・端末 | A | 逆張り: 急落の底（担当: コナーズ）（指値の2日目） | 2位（勝率65%・1回平均+2.1%） | 24.37 | +1.0% | 3 | -8.1% | 下げ | 2026-11-17の合図: 直前5日の最高値（終値）から-20.7%下落（−15%以上）、RSI(2)=7.2（≦10）、急落の前は50日線＞200日線。市場全体の局面: S&P500 横ばい／NASDAQ100 横ばい。その後まだ指値に届かず、終値は5日線以下 | 2027-02-02（76日後） | 指値買い 23.66（合図の日 2026-11-17 の終値 24.14 の2%下。今日から2取引日。届かなければ見送り、途中で終値が5日線を上回ったら取り消す）。損切り: 約定した値段の15%下。手じまい: 終値が5日線（今日 25.48）を上回った翌日の寄り付き（コナーズ）。**株数の目安: 100株**（2,384ドル÷23.66。注文の価格）、購入金額 約2,366ドル |
| ACN | AIソフト・セキュリティ・ITサービス | A | 逆張り: ボリンジャー メソッドIII | 3位（勝率68%・1回平均+1.5%） | 227.49 | -4.9% | 80 | +14.6% | 上昇相場 | %b=-0.127（<0.05）、21日II%=+0.042（>0） | 2026-12-17（29日後） | 翌日の寄り付きで買い。損切り: 買値の15%下。手じまい: 買った日の夜から、売りの指値をその日の上部バンド（今日 270.32）に置き、毎晩その日の値に置き直す。**株数の目安: 10株**（2,384ドル÷227.49。今日の終値。寄り付きの値段で変わる）、購入金額 約2,275ドル |
| IBM | AIプラットフォーム・クラウド | A | 逆張り: ボリンジャー メソッドIII | 3位（勝率68%・1回平均+1.5%） | 228.53 | -1.1% | 23 | +2.5% | レンジ | %b=-0.167（<0.05）、21日II%=+0.064（>0） | 2027-01-27（70日後） | 翌日の寄り付きで買い。損切り: 買値の15%下。手じまい: 買った日の夜から、売りの指値をその日の上部バンド（今日 260.67）に置き、毎晩その日の値に置き直す。**株数の目安: 10株**（2,384ドル÷228.53。今日の終値。寄り付きの値段で変わる）、購入金額 約2,285ドル |
| INTU | AIソフト・セキュリティ・ITサービス | A | 逆張り: ボリンジャー メソッドIII | 3位（勝率68%・1回平均+1.5%） | 313.24 | -2.4% | 7 | -0.8% | 下げ | %b=-0.113（<0.05）、21日II%=+0.015（>0） | 2026-11-19（1日後）**決算が近い** | 翌日の寄り付きで買い。損切り: 買値の15%下。手じまい: 買った日の夜から、売りの指値をその日の上部バンド（今日 361.81）に置き、毎晩その日の値に置き直す。**株数の目安: 7株**（2,384ドル÷313.24。今日の終値。寄り付きの値段で変わる）、購入金額 約2,193ドル |

- 局面（判定式はClaudeが置いたもの）: **上昇相場**＝終値 > 50日線 > 200日線、50日線が20取引日前より2%以上高い、ADX(14) ≧ 20／**下落相場**＝終値 < 50日線 < 200日線、50日線が20取引日前より2%以上低い、ADX(14) ≧ 20／**上げ**＝それ以外で終値が50日線より上、かつ50日線が10取引日前より上か20日線が5取引日前より上／**下げ**＝それ以外で終値が50日線より下、かつ50日線が10取引日前より下か20日線が5取引日前より下（急な下げの初めは50日線がまだ上向きのため20日線でも見る）／**レンジ**＝どれにも当たらない（2026-11-05 から5つ。それまでは上昇相場とレンジの2つだけで、下げている銘柄もレンジと出ていた）。

- 2倍ETF: 2倍ETFがある銘柄（ユーザーがムームー証券で買えることを確認した38銘柄のうち、目減りが年15%未満のもの）は、株の代わりに2倍ETFを買う（2026-10-04 ユーザー決定。`バックテスト結果/2倍ETFを使う決まり.md`。年率 約27%→約33%、確定した損益だけの最大下落率 約30%→約31%、含み損込みは約33%→約45%）。買う金額は株と同じ（資金の25%）。合図・損切り（元の株の買値の15%下＝ETFでは約30%下）・手じまいはすべて元の株の値段で判定する。指値・逆指値はETFの値段に直して置く。どのETFかは `新分析ツール/2倍ETFの対応表.json`（売買代金が1日500万ドル以上で、直近1年の目減りが一番小さいもの）。**2倍ETFで買うのは、S&P500が20週線（100日線）で「上昇」の局面のときだけ。横ばい・下落の局面では元の株で買う**（案1、2026-10-13 ユーザー採用。買う日に決め、買った後は局面が変わってもそのまま持つ。`バックテスト結果/流れ（市場の局面）を使う形.md`）。

- ルールの過去の成績: 今の売りのルールで、後知恵なしの監視銘柄・2015年〜の全部の合図の1回ごとの成績（2026-10-02計算、`新分析ツール/バックテスト結果/ルールごとの成績.md`）。順位は1回平均（1回の売買で平均いくら増えるか）の順。表はパターン（A→B）ごとに、この順位の良い順に並べた（表示の順番だけ。買う順番・件数の上限は変えていない。候補の選び方を変えても成績は変わらなかったため。2026-10-02 ユーザーの指示）。著者には渡さない。

- 悪いニュースが続いているグループ（半導体）の候補（記録だけ。売買のルールは変えない。著者には渡さない）: なし

- 候補の数: 空き枠3（同時保有4銘柄まで。保有2、うち今日ルールの売りが成立1）＋予備2件まで表に出した（2026-10-25 ユーザー決定）。省いた候補はない。

- テーマの外の候補（グループが「テーマの外」）: 監視銘柄の候補で枠が埋まらないときに使う（監視銘柄の候補を先に買う）。S&P500の今の構成銘柄のうち監視銘柄でない銘柄から、RS≧90・30週線が上向きで終値がその上・業種の3カ月の強さが上位20%の15銘柄を調べ、空き枠2つ分まで出した。バックテストでは、テーマの外の強い銘柄で空き枠を埋めると、テーマが弱い時期の成績が支えられた（`バックテスト結果/半導体・AIに特化した場合.md`。2026-10-01 ユーザー決定）。

- RS≧80の押し目（ボリンジャーIII）は、バックテストで成績がより安定していた（PF3.27、最大下落20%）。

## 6-3. 参考: 条件の成立が目前の銘柄（予約は注文しない・著者には送らない）

2026-10-25 ユーザー決定: 予約（逆指値・指値）の注文はやめ、参考の表示だけにする。毎朝のツールと同じ条件・値段で予約の約定をバックテストに入れると、どの形も年率が下がった（後知恵なし 35.7%→30.7〜34.2%、87銘柄 45.6%→34.2〜42.6%。`バックテスト結果/点検_2026-10-25/`）。引けで条件がそろえば、翌朝の節6に買いの候補（A）として出る。各ルールでRSの高い順に2件まで。

| 参考の銘柄 | グループ | 種類 | 終値 | 前日比 | RS | 当てはまった条件 | 条件がそろう目安の価格（注文はしない） |
|---|---|---|---|---|---|---|---|
| SHOP | AIソフト・セキュリティ・ITサービス | ボリンジャー メソッドIII（%bが0.05未満に近い） | 139.42 | -1.7% | 57 | %b=0.136（0.05まであと少し）、21日II%=+0.027（>0） | 135.97（この値より下で引けると翌朝の買いの候補（A）。目安） |
| SNPS | 半導体製造装置・材料・設計ソフト・計測 | ボリンジャー メソッドIII（%bが0.05未満に近い） | 434.01 | -0.3% | 46 | %b=0.179（0.05まであと少し）、21日II%=+0.104（>0） | 425.11（この値より下で引けると翌朝の買いの候補（A）。目安） |


# ニュース（サブエージェントの調査）

# ニュース調査（2026-11-18引け時点。出典は headlines.md の見出し。Web検索6件は当日記事が出ず）

## テーマ全体の下げの原因
- 市場: NY株続落（ダウ561ドル安、5カ月ぶり安値、S&P500は5日続落）（時事通信・アジア経済 11/18）。NVIDIA決算は売上1000億ドル超で時間外+3%超（BigGo 11/18）だが、通常取引で上げが消えた（Bloomberg・Reuters・WSJ 11/18。Motley Fool 11/18は後継者問題・中国事業リスクを指摘）。
- 金利: FOMC議事録で12月の大幅利上げ観測が上昇（Moomoo 11/18）、ドルは19カ月ぶり高値（Benzinga 11/18）。
- 半導体: SOX ETFは2008年以来で最悪の2カ月の下げ（Benzinga 11/18）。
- 信用: ネオクラウド（IREN・CoreWeave・Nebius）が最大79%下落、AIの資金調達が厳しい（BigGo 11/18）。AI債務のCDS・ETF空売り（WSJ・CNBC 11/18）。当日の個別の格下げ・増資の見出しは見つからなかった。ハイイールド債・VIXの数値は取得不可。
- 同日に別業界の下げ: 見出しでは確認できず（セキュリティ・AKAM・FFIVは上昇）。
- 「〇〇ショック」の呼び名: 見つからなかった（検索語「ショック 株」。IBD 11/18に Fed 'Shock' の語のみ）。
- その他: Anthropic IPOが高めの価格で決定（IBD・Kiplinger 11/18）。イランがクウェートの米軍基地を標的にしたとの報道（Newsquawk 11/18）。

## 引け後・時間外の材料
- PANW: 時間外 +7.2%。決算で売上・見通しが予想超え、Applied Computeを45億ドルで買収（WSJ・PR Newswire・IBD 11/18）。
- CRWD: 時間外 +4.6%（5%未満）。個別の見出しは確認できず。
- NVIDIA決算後、Nebiusなどが時間外に上昇（TradingView 11/18）。
- 保有・候補（SNDK・AMD・SMCI・INTU・ACN・IBM）: 時間外±5%未満。

## PANW（+9.9%）
- 11/18 決算が予想超え、AIでセキュリティの重要性が増したとの評価（MarketWatch・IBD）。Applied Compute買収45億ドル（WSJ）。
- 11/17 下落（Benzinga）。CRWD +7.9%・FTNT +5.9%が同時に上昇（波及とみられるが、見出しでの明記なし）。

## AKAM（+8.3%）
- 原因となる見出しは見つからなかった（Traders Union 11/18はテクニカル記事のみ）。
- 11/12 高値から約46%下落（Anthropic向け116億ドル契約があるのに）（BigGo・Investing.com）。11/14 CEOが260万ドルの自社株購入（TIKR）。

## CRWD / FTNT / FFIV
- CRWD +7.9%、FTNT +5.9%、FFIV +5.2%: 個別の原因となるニュースは見つからなかった（PANW決算日の同時上昇）。

## AMD（保有、+5.3%）
- 11/18 上昇の見出し（Yahoo Finance）。SMCIがAMDチップでAI技術を発表（GuruFocus 11/18）。11/18 インサイダーが約3,549万ドル売却（MT Newswires）。
- 決算 Beat/Miss・予想修正: 確認できず。
- 悪材料: インサイダー売却（上記）以外は確認できず。

## SNDK（保有、-2.6%）
- 11/18 8対1の株式分割を前に4%安、NANDの供給過剰懸念、MicronとSeagateも下落（24/7 Wall St.）。分割後の取引は11/20開始の見込み（nai500 11月）。
- 11/17 高値から62%下落（Barchart）。10/29 決算は予想超えも下落、BofAは目標株価を2,500→2,000ドル（買い維持）。
- 11/18 Aschenbrenner氏のAIファンドが保有を92%削減（24/7 Wall St.）。
- 悪材料: 業界の供給増による価格下落懸念。訴訟等は確認できず。

## SMCI（候補、+1.0%）
- 11/12 司法省が密輸疑惑を調査との報道で下落（Barron's・Yahoo・Benzinga）。11/17 下落（Investing.com）。11/18 AMDチップでのAI技術発表（GuruFocus）。
- 次回決算の公式発表: 確認できず。
- 悪材料: あり（司法省の密輸疑惑の調査）。

## ACN（候補、-4.9%）
- 11/18 売り圧力との記事のみ、具体的な原因は見つからなかった（Traders Union）。11/13 845億ドルの契約獲得（Investing.com）。11/17 MicrosoftとSalesforceがCopilotforce提携（MT Newswires）。
- 悪材料: 確認できず。

## IBM（候補、-1.1%）
- 11/17 1.9%下落（Traders Union）、年初来-21%（24/7 Wall St.）。11/18 個別の材料は見つからなかった。
- 悪材料: 確認できず。

## INTU（候補、-2.4%）
- 11/17 約7%下落（Motley Fool・Global Banking & Finance Review）。11/18 決算前に、AnthropicのClaudeが銀行連携の家計ツールを出しTurboTaxへの懸念（Startup Fortune）。
- 決算は11/19（Barchart 11/18）。
- 悪材料: あり（AIによるTurboTax代替の懸念、決算直前）。

## NVDA（-2.9%）
- 11/18 好決算後に下落、目標株価の引き下げが相次ぎ（TradingView）、アナリストの格下げ（TipRanks）。52週安値付近（24/7 Wall St.）。

## TJX（+8.0%、監視外）
- 11/18 Barron's「Stocks That Explain Today's Market」に掲載。決算とみられるが数値・ガイダンスは確認できず。業種は小売（Discount Stores、3カ月 +19.8%、scan.md）。

## テーマ全体のニュース（直近1週）
- 製造装置: AMATは決算でガイダンス上方も下落、TER・AMATが1週で15〜21%安（Benzinga・TIKR 11/12）。
- AIサーバー: DELL・HPEが決算前に下落、Citi等が目標株価を引き下げ（Barron's 11/16、GuruFocus 11/18）。
- 輸出規制・大手の設備投資の新発表: 確認できず。

# ニュースの見出し（プログラムが自動で取得）

- Googleニュース（日付を指定）とYahooファイナンスの見出しを `tools/news_headlines.py` が自動で並べたもの。日付は米国東部時間の配信日（引け後の記事は翌日付）。原因の判断・売買の判断はしていない。
- 調べた銘柄の選び方: ①保有 ②今日の候補 ③時間外に±5%以上動いた監視銘柄 は全部、④引けまでに大きく動いた銘柄（1週で±5%のグループの上位3・1日で±7%）は合計12銘柄まで。
- 1週で−5%以下のグループ: 半導体製造装置・材料・設計ソフト・計測（-9.1%）、AIサーバー・ストレージ・メモリ・端末（-8.0%）、半導体（-6.6%）、AIソフト・セキュリティ・ITサービス（-6.6%）
- 1週で+5%以上のグループ: なし

## 0. 時間外（引け後）の値動き（2026-11-18 の引けから、Yahoo。±3%以上の監視銘柄と、保有・候補は全部）

| 銘柄 | 区分 | 引け | 時間外 | 騰落率 |
|---|---|---|---|---|
| PANW | 監視 | 341.41 | 365.85（17:19 ET） | **+7.2%** |
| CRWD | 監視 | 236.92 | 247.78（17:19 ET） | +4.6% |
| SNDK | 保有 | 776.06 | 767.57（17:19 ET） | -1.1% |
| AMD | 保有 | 530.81 | 525.01（17:19 ET） | -1.1% |
| SMCI | 候補 | 24.36 | 24.30（17:12 ET） | -0.2% |
| INTU | 候補 | 313.22 | 312.60（16:56 ET） | -0.2% |
| ACN | 候補 | 227.49 | 227.49（17:01 ET） | -0.0% |
| IBM | 候補 | 228.53 | 228.53（16:30 ET） | +0.0% |

## 1. 市場全体（2026-11-18）

### 市場全体（英語のまとめ記事）
検索語: `stocks Wall Street close Nasdaq`
- 11/18 Kiplinger | Nasdaq Finds a Path Higher Ahead of Anthropic IPO: Stock Market Today
- 11/18 24/7 Wall St. | Stock Market Today: Nvidia Earnings Are Driving the Market, but Uncertainty Still Reigns
- 11/18 The Motley Fool | Stock Market Correction: 2 AI Stocks With 130% and 160% Upside, According to Wall Street.
- 11/18 Benzinga | Stock Market Today: Dow Jones, S&P 500 Futures Rise Ahead of FOMC Minutes— NVDA, AAOI, PANW in Focus
- 11/18 아시아경제 | [New York Stock Market] Mixed Close Despite Nvidia's Strong Results; S&P 500 Falls for Fifth Straight Session

### 市場全体（Stock Market Today）
検索語: `"stock market today"`
- 11/18 Bloomberg.com | Stocks Fall as Nvidia’s Earnings Rally Sputters: Markets Wrap
- 11/18 Eurasia Business News | Stock Market Today, November 18, 2026: Nvidia Earnings Fail to Calm Investors as Gold and Oil Fall
- 11/18 Benzinga | Dow Drops as Nvidia Slips After Earnings, Dollar Hits 19-Month High: Stock Market Today
- 11/18 The Motley Fool | Stock Market Today, Nov. 18: Nvidia Slips on Strong Results as Succession and China Business Risks Weigh

### 市場全体（日本語のまとめ記事）
検索語: `米国株式市場 OR NY株`
- 11/18 Yahoo!ニュース | NY株、5カ月ぶり安値 エヌビディアが安い（時事通信）
- 11/18 沖縄タイムス社 | ＮＹ株続落、５６１ドル安 エヌビディア混乱を懸念
- 11/18 京都新聞デジタル | ＮＹ株３日続落、５６１ドル安
- 11/18 BigGo ファイナンス | Nvidia好決算もNY株はまちまち…ダウ1.1%安、FRB引き締め警戒が再燃
- 11/18 大分合同新聞 | ＮＹ株続落、５６１ドル安

### 半導体・AI株（英語）
検索語: `chip stocks OR semiconductor stocks OR AI stocks`
- 11/18 Yahoo Finance | The 3 Best AI Stocks to Buy Now (Yes, Nvidia Is One of Them)
- 11/18 Reuters | Nvidia retreats as strong outlook fails to dispel uncertainty
- 11/18 WSJ | U.S. Stocks Mostly Lower After Nvidia Earnings Fail to Soothe Nerves
- 11/18 Benzinga | Chip Stocks Eye Worst Two-Month Drop Since 2008 - iShares PHLX SOX Semiconductor Sector Index Fund (NASDA
- 11/18 The Motley Fool | Got $500? Buy This Top Artificial Intelligence (AI) Chip Stock Following the Latest Sell-Off

### 信用（社債・借金）
検索語: `AI debt OR bonds OR credit spreads OR CDS`
- 11/18 WSJ | Why the Credit Default Swap Market—Red Hot in the AI Trade—Is Vital for CFOs
- 11/18 CNBC | Big bets against AI debt, from CoreWeave to Oracle and the Mag 7, could soon hit the ETF market
- 11/18 BigGo Finance | Neocloud Stocks IREN, CoreWeave and Nebius Shed Up to 79% as AI Funding Tightens
- 11/18 NAI500 | AI debt is the new subprime test
- 11/18 TradingView | Market strain brewing as AI revaluation collides with budget deficits - TS Lombard

### 「〇〇ショック」の呼び名（日本語）
検索語: `ショック 株`
- 11/18 Yahoo!ファイナンス | 「とてもショック」災害時も安心して過ごせると期待したのに…50歳女性が買って後悔した3万円のもの
- 11/18 Moomoo | 速報：FOMC議事録により、12月の大幅利上げの可能性が上昇
- 11/18 BigGo ファイナンス | カナダ銀行、貿易ショックで先行き不透明感強まる中、より多くのシナリオを公表＝グラベル副総裁
- 11/18 BigGo ファイナンス | コインシェアーズ、イーサリアム準備金を全売却、ソラナの半分も売却し1,930万ドルを調達、自社株買いの資金に

### 引け後・時間外の動き（英語）
検索語: `"after hours" OR "after the bell" OR "extended trading" stocks`
- 11/18 Benzinga | Ardent Health Stock Tumbles 14.61% After Hours: Here's Why
- 11/18 TradingView | Nebius Shares Jump After Hours as Nvidia’s Strong Quarterly Numbers Lift AI Infrastructure Stocks
- 11/18 Newsquawk | EU Market Open: NVIDIA beats and shares jump after-hours, but APAC stocks mixed as Iran targets US base in Kuwait; UK CPI and FOMC Minutes ahead
- 11/18 BigGo Finance | Entertainment, Tourism Stocks Surge in After-Hours Trading on South Korea-China FTA Deal; SM Entertainment Hits 29% Limit Up
- 11/18 Kalkine | Why Are i3 Verticals (NASDAQ:IIIV) Shares Up 10% After Hours on a Fiscal Fourth-Quarter Earnings Beat?
- 11/18 Benzinga | Abits Group Stock Jumps 45.79% After Hours - Abits Group (NASDAQ:ABTS)
- 11/18 Benzinga | Iridex (NASDAQ: IRIX) Shares Fall 26.96% After Hours: What Investors Should Know
- 11/18 Seoul Economic Daily | Korean Entertainment Stocks Surge After Hours on China Hopes

### 引け後・時間外の動き（日本語）
検索語: `時間外 決算 株`
- 11/18 Yahoo!ファイナンス | ロウズ、好決算も時間外で下落＝米国株個別(株探ニュース)
- 11/18 BigGo ファイナンス | エヌビディア、第3四半期売上高が1000億ドル突破 時間外株価は3%超上昇
- 11/18 みんかぶ FX/為替 | アジア株 買いの勢い続かず、エヌビディア好決算も拭えぬ先行き不安

### 買収・合併（英語）
検索語: `acquisition OR acquire OR merger OR takeover chip OR semiconductor OR AI OR optical`
- 11/18 WSJ | Exclusive | Palo Alto Networks to Buy AI-Startup Applied Compute for $4.5 Billion
- 11/18 PR Newswire | Palo Alto Networks to Acquire Applied Compute, Bringing Secure Open-Weight AI to the Enterprise
- 11/18 CTech | Palo Alto Networks jumps after earnings beat and $4.5 billion AI acquisition
- 11/18 The Information | Palo Alto Networks to Acquire AI Firm Applied Compute for $4.5 Billion
- 11/18 The Futurum Group | Dropbox Bets on AI Infrastructure With Tigris Data Acquisition
- 11/18 Yahoo Finance | Omega Systems Establishes Midwest Presence and Expands Managed AI Capabilities with Acquisition of Framework IT
- 11/18 Unite.AI | Workday Plans Honeydew Acquisition to Unify AI Business Definitions

## 2. 保有・候補・時間外で大きく動いた銘柄（2026-11-12〜2026-11-18 の見出し）

### SNDK（Sandisk Corporation、保有、AIサーバー・ストレージ・メモリ・端末、前日比 -2.6%、1週 -20.6%、時間外 -1.1%）

#### Googleニュース
検索語: `Sandisk stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/13 Yahoo Finance | Why Sandisk Stock Is Falling Today
- 11/17 The Motley Fool | Why Sandisk Stock Keeps On Going Down
- 11/17 Barchart.com | Why Sandisk Stock’s 62% Drop Is a Buying Opportunity

#### Yahooファイナンス
検索語: `SNDK`
- 11/18 24/7 Wall St. | 3 Reasons Keep Me Buying SanDisk at $795
- 11/18 24/7 Wall St. | Leopold Aschenbrenner’s AI Fund Cut Its Reported Holdings 92% in One Quarter
- 11/18 24/7 Wall St. | SanDisk Slides 4% Ahead of 8-for-1 Stock Split as NAND Glut Worries Linger; Micron Drops 3%, Seagate Edges Lower

### AMD（Advanced Micro Devices, Inc.、保有、半導体、前日比 +5.3%、1週 -4.1%、時間外 -1.1%）

#### Googleニュース
検索語: `Advanced Micro Devices stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/13 Yahoo Finance | Why Advanced Micro Devices Stock Is Down Today
- 11/14 The Motley Fool | Why Advanced Micro Devices Stock Surged This Week
- 11/14 Moomoo | Advanced Micro Devices (AMD) Stock Sinks 9%: What the Options Flow and Dark Pools Say Now
- 11/18 Yahoo Finance | Why Is Advanced Micro Devices Stock Rising Today?

#### Yahooファイナンス
検索語: `AMD`
- 11/18 24/7 Wall St. | NVIDIA Is Near Its 52-Week Low. Will NVDA Stock Hit $100 or $200 First?
- 11/18 MT Newswires | Advanced Micro Devices Insider Sold Shares Worth $35,489,904, According to a Recent SEC Filing
- 11/18 MT Newswires | Update: Advanced Micro Devices Insider Sold Shares Worth $35,489,904, According to a Recent SEC Filing

### ACN（Accenture plc、候補、AIソフト・セキュリティ・ITサービス、前日比 -4.9%、1週 -10.3%、時間外 -0.0%）

#### Googleニュース
検索語: `Accenture stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/12 Yahoo Finance | Is Wall Street Bullish or Bearish on Accenture Stock?
- 11/12 Yahoo Finance | Accenture PLC (ACN) Is a Trending Stock: Facts to Know Before Betting on It
- 11/13 Investing.com | AI software is sinking, why is Accenture winning $84.5B deals?
- 11/18 Traders Union | Accenture stock falls as seller pressure dominates the market

#### Yahooファイナンス
検索語: `ACN`
- 11/17 24/7 Wall St. | IBM Is Down 21% This Year. What Will It Take to Get IBM Stock Back to $250?
- 11/17 CNW Group | Microsoft and organizations across industries launch AI Transparency Initiative to strengthen enterprise trust in AI models and agents
- 11/17 MT Newswires | Salesforce, Microsoft Launch Copilotforce Partnership

### IBM（International Business Machines Corporation、候補、AIプラットフォーム・クラウド、前日比 -1.1%、1週 -7.9%、時間外 +0.0%）

#### Googleニュース
検索語: `International Business Machines stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/12 MarketBeat | International Business Machines (NYSE:IBM) Stock Falls 1.3% - Time to Sell?
- 11/16 Benzinga | IBM Stock Moves Lower: What's Going On?
- 11/17 Yahoo Finance | Is Trending Stock International Business Machines Corporation (IBM) a Buy Now?
- 11/17 Traders Union | Why is IBM stock down 1.9% today?

#### Yahooファイナンス
検索語: `IBM`
- 11/18 24/7 Wall St. | Forget Market Crashes: These Dow Jones Giants Have Recession-Proof Dividends
- 11/18 GlobeNewswire | Artificial Intelligence (AI) in Reverse Logistics Market Report 2026 | Capitalize on AI Returns and Circular Commerce Through 2030 with Microsoft, IBM, Oracle, SAP and Honeywell
- 11/18 GlobeNewswire | Global Core Network Equipment Market Report 2026-2030 | Capitalize on 7.2% CAGR as 5G Standalone and Cloud-Native Cores Accelerate; Ericsson, Huawei, Nokia, Cisco, and Samsung Lead

### INTU（Intuit Inc.、候補、AIソフト・セキュリティ・ITサービス、前日比 -2.4%、1週 -8.6%、時間外 -0.2%）

#### Googleニュース
検索語: `Intuit stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/12 Yahoo Finance | Intuit (INTU) Expected to Beat Earnings Estimates: Can the Stock Move Higher?
- 11/17 Global Banking & Finance Review | Intuit falls 7.17% in Tuesday's session
- 11/18 Startup Fortune | Intuit stock drops 7% ahead of earnings as Claude's bank-linked finance tool raises TurboTax fears
- 11/18 Barchart.com | Dear Intuit Stock Fans, Mark Your Calendars for November 19

#### Yahooファイナンス
検索語: `INTU`
- 11/17 Barrons.com | Boom Goes the Stock Market
- 11/17 Barrons.com | Broad Selloff Leaves Few Places to Hide
- 11/17 Motley Fool | Why Intuit Stock Is Falling Fast Today

### SMCI（Super Micro Computer, Inc.、候補、AIサーバー・ストレージ・メモリ・端末、前日比 +1.0%、1週 -19.9%、時間外 -0.2%）

#### Googleニュース
検索語: `Super Micro Computer stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/12 Barron's | Super Micro Stock Falls as DOJ Probes Smuggling Allegations
- 11/12 Yahoo Finance | Super Micro (SMCI) Takes Another Hit as Fresh Probe Weighs on Shares
- 11/12 Benzinga | What's Going On With Super Micro Computer Stock Thursday?
- 11/17 Investing.com | Why is Super Micro Computer stock sliding today?

#### Yahooファイナンス
検索語: `SMCI`
- 11/18 GuruFocus.com | Supermicro Has an AI Bottleneck and Is Turning to AMD
- 11/18 GuruFocus.com | Supermicro Unveils Major AI Technology Breakthrough With AMD Chips
- 11/18 Investing.com | Was Nvidia’s strong report a clearing event for the wider chip sector?

### PANW（Palo Alto Networks, Inc.、AIソフト・セキュリティ・ITサービス、前日比 +9.9%、1週 +1.6%、時間外 +7.2%）

#### Googleニュース
検索語: `Palo Alto Networks stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/15 Yahoo Finance | Palo Alto Networks Stock Outlook: Is Wall Street Bullish or Bearish?
- 11/17 Benzinga | Why Palo Alto Networks Is Falling Tuesday
- 11/18 MarketWatch | Palo Alto Networks’ stock soars as earnings show AI has upped the stakes for cybersecurity
- 11/18 Investor's Business Daily | Palo Alto Jumps On Earnings Beat, Strong Revenue Outlook

#### Yahooファイナンス
検索語: `PANW`
- 11/18 Barrons.com | Nvidia, Take-Two, Palo Alto, Applied Optoelectronics, TJX, and More Stocks That Explain Today’s Market
- 11/18 Investing.com | Palo Alto to buy Applied Compute for $4.5 billion, while Q1 results beat estimates
- 11/18 Investor's Business Daily | Dow Jones Futures: Anthropic IPO Prices High, Palo Alto, Everpure Rally; Market Mixed On Nvidia, Target, UnitedHealth, Fed 'Shock'

## 3. 引けまでに大きく下げた銘柄（2026-11-12〜2026-11-18 の見出し）

### TER（Teradyne, Inc.、半導体製造装置・材料・設計ソフト・計測、前日比 +0.4%、1週 -11.5%、時間外 -0.5%）

#### Googleニュース
検索語: `Teradyne stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/12 Yahoo Finance | Cathie Wood Dumps the Last of Teradyne From Her Flagship Fund
- 11/12 TIKR.com | Teradyne Stock Falls 21% in a Week as Applied Materials Drops 15%. Is the Chip-Equipment Selloff Overdone?
- 11/13 Traders Union | Teradyne stock drops as oversold signals increase rebound risk
- 11/13 Barchart.com | Teradyne Stock: Analyst Estimates & Ratings

#### Yahooファイナンス
検索語: `TER`
- 11/13 Zacks | CBRS Q3 Earnings Beat Estimates, Revenues Rise on Strong Cloud Growth
- 11/13 Zacks | Teradyne Benefits From Strong Test Demand: Can It Beat KLAC & COHU?
- 11/16 Business Wire | Teradyne to Present at the 2026 UBS Global Technology and AI Conference

### AMAT（Applied Materials, Inc.、半導体製造装置・材料・設計ソフト・計測、前日比 +0.9%、1週 -10.8%、時間外 -0.7%）

#### Googleニュース
検索語: `Applied Materials stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/12 Benzinga | Applied Materials Reports Q4 Earnings, Raises Guidance as AI Drives Strong Chip Demand (CORRECTED)
- 11/13 Proactive financial news | Applied Materials Inc Share Price - AMAT, RNS News, Articles, Quotes, & Charts (NASDAQ:AMAT)
- 11/15 TradingKey | Applied Materials Stock Breaks Wedge as Rising Fab Forecasts Put $493 in Focus
- 11/17 Yahoo Finance | Why Is Applied Materials Stock Down Over 5%?

#### Yahooファイナンス
検索語: `AMAT`
- 11/18 24/7 Wall St. | Billionaires Split on Lam Research. Is the Stock a Buy, Sell or Hold?
- 11/18 GuruFocus.com | Bernstein Spots 4 Ways to Play the $279 Billion Chip Tool Boom
- 11/18 Insider Monkey | Sell Alert: 5 Stocks Analysts Downgraded on Friday

### LRCX（Lam Research Corporation、半導体製造装置・材料・設計ソフト・計測、前日比 +0.5%、1週 -10.3%、時間外 -0.4%）

#### Googleニュース
検索語: `Lam Research stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/12 Yahoo Finance | Lam Research (LRCX) Lost About 34% in a Month. Here’s Why Bernstein’s Rasgon Still Likes It
- 11/12 Trefis | Is Lam Research Stock Paying You Enough For The Swings?
- 11/13 Investing.com | Why is Lam Research stock sliding today?
- 11/17 Yahoo Finance | Lam Research Stock Fell Nearly 7%. What Happened?

#### Yahooファイナンス
検索語: `LRCX`
- 11/17 PR Newswire | Lam Research Corporation Announces Participation at Upcoming Conference
- 11/17 Zacks | KLAC is Overvalued at 9.37X P/S: Buy, Sell or Hold the Stock?

### DELL（Dell Technologies Inc.、AIサーバー・ストレージ・メモリ・端末、前日比 -3.0%、1週 -16.2%、時間外 -0.3%）

#### Googleニュース
検索語: `Dell stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/13 TradingView | Dell stock falls before earnings: strong AI demand will not alone sustain 250% rally
- 11/16 Trefis | Why Is Dell Stock Falling Again?
- 11/16 Barron's | Dell and HPE Stocks Are Getting Hammered. Why the Selloff May Be Overdone.
- 11/17 Yahoo Finance | GF Securities Just Slashed Its Price Target on Dell Stock. Here's Why.

#### Yahooファイナンス
検索語: `DELL`
- 11/18 Business Wire | Dell Technologies to Present at Investor Conferences in December
- 11/18 GuruFocus.com | Citi Bank Slashes Dell And HPE Price Targets Ahead Of Earnings
- 11/18 GuruFocus.com | Sandisk Leads Tech Stocks in Earnings Surprises Ahead of 8-for-1 Split

## 4. 引けまでに大きく上げた銘柄（2026-11-12〜2026-11-18 の見出し）

### AKAM（Akamai Technologies, Inc.、光・通信・ネットワーク、前日比 +8.3%、1週 +5.8%、時間外 +0.8%）

#### Googleニュース
検索語: `Akamai stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/12 BigGo Finance | Akamai Stock Falls 46% Despite $11.6 Billion Anthropic Cloud Deal
- 11/12 Investing.com | CrowdStrike chose Akamai for security, yet the stock plunged 46%
- 11/13 TradingView | Key facts: CADL Drops 38%; AURORA Phase 3 Starts; $50M Stock Sale
- 11/18 Traders Union | Akamai stock price prediction: Upward price move targets $94.49 resistance

#### Yahooファイナンス
検索語: `AKAM`
- 11/14 TIKR | Akamai’s CEO Bought $2.6 Million of Stock 48% Below Its High. The Delays? “Not a Big Deal”
- 11/14 TIKR | Cloudflare Jumps 12% as Its “Even Higher Gear” Delivers the Fastest Growth in Nearly Four Years
- 11/16 GlobeNewswire | Trapped by Design: 50% of Enterprises Run Workloads in the Wrong Place
