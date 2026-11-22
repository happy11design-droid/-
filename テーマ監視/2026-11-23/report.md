# テーマ監視 2026-11-20

# 判定のまとめ（ルールの判定と著者の判定を分けて表示）

- **ルールの判定**: 採用した売買ルール（スクリプト）が数値で決めたもの。損切りは買値の15%下の逆指値（日中に届けばその場で売れる）。
- **著者の判定**: ノートブックの著者の回答。買いは注文を止める理由があるときだけ【様子見】、保有はルールより早く手じまう理由があるときだけ【売り】。根拠は下の「著者の回答（全文）」。
- 2つが食い違うときに、どちらに従うかはユーザーが決める。

- **テーマ全体の急落（S2・記録だけ）: あり（S2）**（SOXが直近60取引日の最高値から -36.4%）。S2の日の順張りの候補には「S2なら見送る形」と付ける（売買のルールは変えない。記録してから採用を決める。2026-10-14）

- **特殊な下げ（記録だけ）: あり（特殊な下げ）**（2026-10-16から）（SOXが直近60取引日の最高値から -36.4%、前の1年の大きな上げ・雇用の弱さ・物価の再加速のうち 2つ）。1995年〜では、この形の後にSOXの下げが長引くことが多かった（後知恵を含む）。売買のルールは変えない（2026-11-03）

## 保有銘柄

| 銘柄 | ルール | 損益 | 時間外 | ルールの判定 | ルールの判定の理由 | 著者の判定 |
|---|---|---|---|---|---|---|
| SNDK | ルール外（ユーザーの判断。この日はどのルールの合図もなし） |  | +2.6% | 保有継続 |  | **【未判定】（）** |
| AMD | ボリンジャーIII | -22.8% | +3.6% | **売り** | 終値 424.39 が損切り価格 467.47 以下 | 【保有継続】（ボリンジャー） |

## 候補の判定（並びは上の「買う順番」の表と同じ）

- 並びは上の「買う順番」の表と同じ（RSの高い順。勝率の高い順ではない）。注文の値段・株数・逆指値は上の表を見る。勝率・1回平均は、そのルールの過去の成績（後知恵なしの監視銘柄・2015年〜の全部の合図）。
- 空き枠: 3（同時保有4銘柄まで。保有2、うちルールの売り1）。著者が【様子見】の候補を見送るかはユーザーが決める。

| 順 | 銘柄 | ルール | 過去の勝率 | 過去の1回平均 | RS | 時間外 | ルールの判定 | 著者の判定 |
|---|---|---|---|---|---|---|---|---|
| 1 | DELL（デル・テクノロジーズ） | 逆張り: 急落の底（担当: コナーズ） | 65% | +2.1% | 98 | +2.9% | 買い（指値 272.46、3取引日まで） | 【様子見】（コナーズ） |
| 2 | HPE（ヒューレット・パッカード・エンタープライズ） | 逆張り: 急落の底（担当: コナーズ） | 65% | +2.1% | 96 | +2.7% | 買い（指値 40.09、3取引日まで） | 【様子見】（コナーズ） |
| 3 | MU（マイクロン・テクノロジー） | 逆張り: 急落の底（担当: コナーズ） | 65% | +2.1% | 92 | +2.7% | 買い（指値 582.62、3取引日まで） | 【様子見】（コナーズ） |
| 4（枠外） | SNPS（シノプシス） | 逆張り: ボリンジャー メソッドIII | 68% | +1.5% | 33 | +1.6% | 買い（翌日の寄り付き） | 【買い】（ボリンジャー） |
| 5（枠外） | DLR（デジタル・リアルティ・トラスト） | 逆張り: ボリンジャー メソッドIII | 68% | +1.5% | 28 | -0.8% | 買い（翌日の寄り付き） | 【買い】（ボリンジャー） |

- 時間外: 前の取引日の引けから、引け後（米国東部時間16〜20時）の最後の値までの騰落率（Yahoo。±5%以上は太字）。寄り付きの値段は、表の注文の目安（前日の終値で計算）から大きくずれることがある。原因の見出しは「ニュースの見出し」の節。

# 著者の回答（全文）

## 0_テーマの局面_ワインスタイン

1. **テーマ全体の局面**: 【ステージ3】（急騰後、30週線が横ばい化し株価が下回る天井圏。第2章）[1, 2]
2. **グループごとの局面**:
- 半導体｜ステージ3｜30週線横ばい[2]
- 半導体製造装置・材料・設計ソフト・計測｜ステージ3｜30週線横ばい[2]
- AIサーバー・ストレージ・メモリ・端末｜ステージ3｜30週線横ばい[2]
- 光・通信・ネットワーク｜ステージ3｜30週線横ばい[2]
- データセンターの電力・冷却・部品・受託製造・建設｜ステージ4｜30週線下向き・線の下[2]
- AIプラットフォーム・クラウド｜ステージ3｜30週線横ばい[2]
- AIソフト・セキュリティ・ITサービス｜ステージ3｜30週線横ばい[2]
3. **転換の兆し**: 出ている。対S&P500のRS悪化（第4章）[3]、30週線下抜け（第2章）[4]、電力等の第4ステージ転落（第3章）[5]が該当。50日線や警告率、雇用・物価はマニュアルに規定なし[6]。
4. **テーマの外**: なし（判定不能：ヒートマップ省略のため読み取れず）

（全体の版が空の応答だったため、1〜2節だけの短い版で送り直した回答。ヒートマップ・急騰急落・ニュースは渡していない）

## 1_コナーズ_prompt_1

## DELL
1. **投資判断**: 【様子見】（200日線下で見送り）
2. **止める理由の確認**:
- 本が禁じる形・状況｜あり｜終値が200日線下（第4章） [1]
- 避けるべき時期（決算など）｜なし｜マニュアルに規定なし（第11章） [2]
- 悪材料｜なし｜マニュアルに規定なし（第3章） [2]
3. **現状パターンと価格**:
- 現状パターン: A（急落条件成立）
- 本日の発注: 見送り（発注なし）
4. **注意点**: 200日線回復まで買い厳禁。

## 1_コナーズ_prompt_2

## HPE
1. **投資判断**: 【様子見】（株価が200日線の下にあるため）[1]
2. **止める理由の確認**:
- 本が禁じる形・状況｜あり｜終値40.91が200日線42.71の下側にある（第4章）[1]
- 避けるべき時期（決算など）｜なし（マニュアルに規定なし）｜決算前の取引を避ける規定なし（第11・14章）[2, 3]
- 悪材料｜なし（マニュアルに規定なし）｜悪材料による見送り規定なし（第2・3章）[4, 5]
3. **現状パターンと価格**:
- 現状パターン: A（条件成立だが200日線下）[1, 6]
- 本日の発注: 翌日の寄り付きで成行は見送り[1]
4. **注意点**: 株が200日線を下回った場合はすべてを白紙に戻すのが鉄則であり、上回るまで手を出さないこと[1]。

## 1_コナーズ_prompt_3

## MU
1. **投資判断**: 【様子見】（200日線割れのため見送り）
2. **止める理由の確認**:
- 本が禁じる形・状況｜あり｜第4章（株価が200日線の下）[1, 2]
- 避けるべき時期（決算など）｜なし｜第11章・規定なし[3, 4]
- 悪材料｜なし｜第2・3章（悪材料は見送り規定なし）[5, 6]
3. **現状パターンと価格**:
- 現状パターン: A（条件成立）
- 本日の発注: なし（200日線下で見送り）
4. **注意点**: 200日線を下回った株の急落買いは厳禁、白紙に戻すこと[1, 2]。

## 1_ボリンジャー_prompt_1

## AMD
1. **投資判断**: 【保有継続】（本基準でルールより早く手じまう理由なし）[1]
2. **止める理由の確認**:
- 本が禁じる形・状況｜なし｜マニュアルに規定なし（第20章）[1]
- 避けるべき時期（決算など）｜なし｜マニュアルに規定なし（次回2027-02-02）[1]
- 悪材料｜なし｜マニュアルに規定なし（11/19空売り報道への早期手仕舞い規定なし）[1, 2]
3. **現状パターンと価格**:
保有中: `売りの予約注文: なし`
4. **注意点**: スクリプト側の手じまい条件（損切り等）に従い規律通り執行すること[3]。

## 1_ボリンジャー_prompt_2

## SNPS
1. **投資判断**: 【買い】（メソッドIIIの条件成立、止める理由なし [1]）
2. **止める理由の確認**:
   - 本が禁じる形・状況｜なし｜第20章（%b<0.05かつ21日II%>0を満たす正当な反転セットアップ [1-3]）
   - 避けるべき時期（決算など）｜なし｜マニュアルに規定なし（決算回避の明記なし、次回決算は18日後 [4, 5]）
   - 悪材料｜なし｜マニュアルに規定なし（個別悪材料の記載なし [4, 5]）
3. **現状パターンと価格**:
   - 現状パターン: A（最新足で%b=-0.219、21日II%=+0.105が成立 [1, 3]）
   - 本日の発注: 翌日の寄り付きで成行
4. **注意点**: 初期の損切り（買値の15%下）を厳守し、手じまい目標である上部バンドの更新を毎晩確認すること [6, 7]。

## 1_ボリンジャー_prompt_3

## DLR
1. **投資判断**: 【買い】（メソッドIII条件成立、止める理由なし）
2. **止める理由の確認**:
- 本が禁じる形・状況｜なし｜第20章（買い条件成立）
- 避けるべき時期（決算など）｜なし｜マニュアルに規定なし（決算通過済）
- 悪材料｜なし｜ニュースで個別悪材料なし
3. **現状パターンと価格**:
- 現状パターン: A（メソッドIII成立）
- 本日の発注: 翌日の寄り付きで成行
4. **注意点**: 直近安値付近にストップを置きリスクを限定すること（第20章）。

# スキャン（数値と事実）


- 監視銘柄 87（判定できたのは 86、取得不可: SNDK）。
- この一覧は数値と事実だけ。売買の判断は著者のノートブックが行う。

## 1. テーマ（グループ）の強さ

| グループ | 銘柄数 | 1週 | 1カ月 | 3カ月 | 3カ月の順位 | 50日線より上の銘柄の割合 | グループ指数の30週線の局面（線との乖離、4週前からの線の傾き） |
|---|---|---|---|---|---|---|---|
| 半導体 | 16 | -14.4% | -16.4% | -15.0% | 4位 | 0% | 横ばい（-24.4%、+3.6%） |
| 半導体製造装置・材料・設計ソフト・計測 | 9 | -15.3% | -16.1% | -27.1% | 7位 | 0% | 横ばい（-27.0%、+0.2%） |
| AIサーバー・ストレージ・メモリ・端末 | 8 | -13.1% | -26.2% | -21.8% | 6位 | 12% | 横ばい（-19.7%、+5.2%） |
| 光・通信・ネットワーク | 9 | -14.2% | -13.6% | -19.8% | 5位 | 11% | 横ばい（-23.8%、+0.1%） |
| データセンターの電力・冷却・部品・受託製造・建設 | 19 | -9.7% | -9.5% | -14.5% | 3位 | 0% | 下落（-17.5%、-0.3%） |
| AIプラットフォーム・クラウド | 11 | -12.6% | -13.6% | -5.8% | 1位 | 9% | 横ばい（-18.0%、+0.7%） |
| AIソフト・セキュリティ・ITサービス | 14 | -11.2% | -19.5% | -13.5% | 2位 | 21% | 横ばい（-4.5%、+4.2%） |

## 2. テーマ全体の状態と早めの警告

- 市場全体の30週線による局面: S&P500指数 **横ばい**／NASDAQ100指数 **横ばい**（急落の底で買うルールは、過去の検証で下落相場で特に強く、横ばいの相場では負けていた）
- **2倍ETFを使う局面（案1、2026-10-13 採用）: S&P500の20週線（100日線）で 横ばい** → 新しく買う銘柄は、2倍ETFのある銘柄も元の株で買う（保有中のETFはそのまま）（SPY 689.81、100日線 758.38、20日前の線 756.55。上昇＝線より上かつ線が上向き）
- **テーマ全体の急落（S2、記録だけ。売買のルールは変えない）: あり（S2）**（SOX 8408.59、直近60取引日の最高値 13217.82 から -36.4%。S2＝最高値から−10%以上）。S2のときに「順張りの新しい買いだけ止める」形を記録で比べる（2026-10-14 ユーザー決定。バックテストでは年率は上がったが2つの期間ではどちらも少し下回ったため、記録してから採用を決める。`バックテスト結果/テーマ全体の急落を検知して手じまう・買いを止める.md`）
- **特殊な下げ（記録だけ。売買のルールは変えない）: あり（特殊な下げ）**（2026-10-16から）。SOX は直近60取引日の最高値から -36.4%（−15%以下が条件）、●A 前の1年の上げ +103.0%（+80%以上）、・B 雇用の伸び 137千人/月（2026-10まで。10万人未満）、●C 物価 4.1%（2026-10。3か月前 3.5%。3.5%以上で再加速）＝2つ（2つ以上が条件）。1995年〜でSOXが−15%以下かつ条件2つ以上の日は、120日後にSOXが下だったのが69%・250日後が70%（中央値 −33%）、AI以外の8業種の平均は250日後 −7%。ただし条件は過去を見て選んだもの（条件が2つ以上の局面は約5回）で、2026年7〜9月にこの間テーマを買わないと、その後の戻りを逃して2026年の成績は下がった（`バックテスト結果/実際の運用の期間の確認_2026-10-23/特殊な下げと過去の似た下げ.md`。2026-11-03）
- テーマ指数（監視銘柄の等金額平均）の30週線による局面: **横ばい**（上昇＝線より上かつ上向き、下落＝線より下かつ下向き、それ以外＝横ばい。ワインスタインのステージの近似）
- テーマ指数と50日線: 50日線より下（乖離 -18.4%）
- S&P500に対する相対的な強さ: 50日平均より下（S&P500より弱い）
- 監視銘柄のうち50日線より上の割合: 7%
- 警告（割合が40%未満かつテーマ指数が50日線より下）: **出ている**
- 参考（バックテスト）: 30週線の「下落」は高値から10〜33%下げた後に出る遅い判定。50日線・割合・相対的な強さは高値から2〜8%で出るが、誤報が年15回以上ある。警告中に新しい買いを止めると、押し目買い（ボリンジャーIII）の成績は大きく下がった（`バックテスト結果/テーマ監視銘柄・直近3年.md` 11・12節）。

## 3. ヒートマップ（Finviz、全米の業種別の騰落率）

3カ月の騰落率の上位15業種（テーマの外で強くなっている業種の確認用）:

| 順位 | 業種 | 1週 | 1カ月 | 3カ月 | 6カ月 | 1年 |
|---|---|---|---|---|---|---|
| 1 | Discount Stores | -0.2% | +6.0% | +16.1% | +8.6% | +28.2% |
| 2 | Medical Distribution | -3.6% | +4.1% | +15.1% | +33.0% | +16.5% |
| 3 | Insurance - Diversified | -3.8% | +3.1% | +10.8% | +15.0% | +13.2% |
| 4 | Consumer Electronics | -3.7% | -1.5% | +10.4% | +11.2% | +25.6% |
| 5 | Advertising Agencies | -12.2% | +20.8% | +9.6% | -18.7% | -26.6% |
| 6 | Lodging | -3.8% | +2.1% | +9.0% | +10.1% | +34.4% |
| 7 | Insurance - Reinsurance | -2.1% | -0.8% | +8.4% | +19.5% | +36.6% |
| 8 | Household & Personal Products | -1.9% | -0.0% | +7.5% | +14.8% | +13.2% |
| 9 | Waste Management | -3.2% | -1.0% | +5.6% | +12.8% | +7.9% |
| 10 | REIT - Hotel & Motel | -3.3% | -0.1% | +5.1% | +19.2% | +50.5% |
| 11 | Insurance - Property & Casualty | -1.4% | +0.9% | +4.7% | +16.1% | +16.1% |
| 12 | Medical Care Facilities | -5.6% | -1.0% | +3.6% | +18.9% | +13.7% |
| 13 | Diagnostics & Research | -5.1% | -5.0% | +3.5% | +38.6% | +15.2% |
| 14 | Drug Manufacturers - Specialty & Generic | -4.7% | -1.0% | +3.0% | +7.2% | +16.3% |
| 15 | Medical Instruments & Supplies | -5.8% | -3.2% | +2.8% | +8.5% | -4.2% |

テーマの業種の順位（3カ月、全144業種中）: Semiconductors 130位、Semiconductor Equipment & Materials 138位、Computer Hardware 140位、Communication Equipment 123位、Electronic Components 124位、Software - Infrastructure 67位、Software - Application 104位、Internet Content & Information 118位

## 4. 急騰・急落した銘柄（前日比±5%以上、または出来高が50日平均の2倍以上）

原因のニュースをサブエージェントが調べ、候補・保有銘柄の判定材料として著者に渡す。急騰・急落そのものは売買の合図にしない（後知恵のないS&P500全体のバックテストでは、急騰の翌日に買うルールは年率7%、急落の翌日に買うルールは年率9〜10%で、採用した3つのルールより優れていなかった）。

| 銘柄 | グループ | 前日比 | 出来高（50日平均の倍） | 終値 | 50日線 | RS | 局面 |
|---|---|---|---|---|---|---|---|
| NBIS | AIプラットフォーム・クラウド | -16.1% | 2.1倍 | 81.31 | 下 | 1 | 下げ |
| ALAB | 半導体 | -14.8% | 1.7倍 | 180.35 | 下 | 26 | 下げ |
| ARM | 半導体 | -14.1% | 1.9倍 | 152.20 | 下 | 14 | 下げ |
| NVDA | 半導体 | -14.0% | 3.7倍 | 125.53 | 下 | 2 | 下げ |
| LITE | 光・通信・ネットワーク | -13.9% | 1.1倍 | 460.54 | 下 | 11 | 下げ |
| MU | 半導体 | -13.9% | 2.1倍 | 594.51 | 下 | 92 | 下げ |
| AMD | 半導体 | -13.2% | 2.4倍 | 424.39 | 下 | 97 | 下げ |
| COHR | 光・通信・ネットワーク | -12.9% | 1.7倍 | 187.22 | 下 | 9 | 下落相場 |
| INTU | AIソフト・セキュリティ・ITサービス | -12.8% | 3.0倍 | 270.44 | 下 | 5 | 下げ |
| STX | AIサーバー・ストレージ・メモリ・端末 | -12.3% | 1.1倍 | 457.01 | 下 | 29 | 下げ |
| AVGO | 半導体 | -12.2% | 2.4倍 | 304.41 | 下 | 16 | 下げ |
| CRWV | AIプラットフォーム・クラウド | -12.0% | 1.4倍 | 39.51 | 下 | 0 | 下落相場 |
| WDC | AIサーバー・ストレージ・メモリ・端末 | -12.0% | 1.3倍 | 261.11 | 下 | 20 | 下落相場 |
| MPWR | 半導体 | -11.9% | 2.0倍 | 1142.05 | 下 | 35 | レンジ |
| MRVL | 半導体 | -11.7% | 1.7倍 | 122.28 | 下 | 35 | 下げ |
| ANET | 光・通信・ネットワーク | -11.6% | 2.0倍 | 167.62 | 下 | 75 | 下げ |
| DELL | AIサーバー・ストレージ・メモリ・端末 | -11.0% | 1.6倍 | 278.02 | 下 | 98 | 下げ |
| GLW | 光・通信・ネットワーク | -10.9% | 1.8倍 | 94.38 | 下 | 6 | 下落相場 |
| CIEN | 光・通信・ネットワーク | -10.8% | 1.3倍 | 234.37 | 下 | 6 | 下落相場 |
| FLEX | データセンターの電力・冷却・部品・受託製造・建設 | -10.8% | 1.4倍 | 66.24 | 下 | 10 | 下落相場 |
| AMAT | 半導体製造装置・材料・設計ソフト・計測 | -10.7% | 1.9倍 | 302.63 | 下 | 13 | 下落相場 |
| KLAC | 半導体製造装置・材料・設計ソフト・計測 | -10.3% | 1.9倍 | 126.87 | 下 | 12 | 下落相場 |
| VRT | データセンターの電力・冷却・部品・受託製造・建設 | -10.1% | 1.8倍 | 166.24 | 下 | 5 | 下落相場 |
| HPE | AIサーバー・ストレージ・メモリ・端末 | -10.1% | 1.1倍 | 40.91 | 下 | 96 | 下げ |
| LRCX | 半導体製造装置・材料・設計ソフト・計測 | -10.0% | 2.1倍 | 183.27 | 下 | 8 | 下落相場 |
| TER | 半導体製造装置・材料・設計ソフト・計測 | -10.0% | 1.7倍 | 204.78 | 下 | 5 | 下落相場 |
| SMCI | AIサーバー・ストレージ・メモリ・端末 | -9.2% | 1.2倍 | 21.65 | 下 | 3 | 下げ |
| Q | 半導体製造装置・材料・設計ソフト・計測 | -8.9% | 1.5倍 | 103.47 | 下 | 25 | 下げ |
| ORCL | AIプラットフォーム・クラウド | -8.5% | 1.3倍 | 101.19 | 下 | 3 | 下げ |
| JBL | データセンターの電力・冷却・部品・受託製造・建設 | -8.4% | 0.9倍 | 225.77 | 下 | 14 | 下落相場 |
| ADI | 半導体 | -8.4% | 2.6倍 | 345.92 | 下 | 63 | 下げ |
| APP | AIプラットフォーム・クラウド | -8.1% | 0.9倍 | 348.29 | 上 | 29 | 上げ |
| SNPS | 半導体製造装置・材料・設計ソフト・計測 | -8.1% | 1.1倍 | 396.17 | 下 | 33 | 下げ |
| INTC | 半導体 | -8.0% | 1.7倍 | 51.28 | 下 | 16 | 下げ |
| APH | データセンターの電力・冷却・部品・受託製造・建設 | -7.8% | 1.5倍 | 69.72 | 下 | 39 | 下げ |
| TXN | 半導体 | -7.7% | 2.3倍 | 263.75 | 下 | 85 | レンジ |
| CDNS | 半導体製造装置・材料・設計ソフト・計測 | -7.6% | 1.2倍 | 281.58 | 下 | 23 | 下げ |
| TSLA | AIプラットフォーム・クラウド | -7.6% | 1.3倍 | 345.82 | 下 | 25 | 下げ |
| GEV | データセンターの電力・冷却・部品・受託製造・建設 | -7.5% | 1.9倍 | 699.33 | 下 | 15 | 下落相場 |
| QCOM | 半導体 | -7.5% | 1.7倍 | 149.94 | 下 | 26 | 下げ |
| ON | 半導体 | -7.4% | 1.3倍 | 60.84 | 下 | 21 | 下げ |
| NTAP | AIサーバー・ストレージ・メモリ・端末 | -7.4% | 1.0倍 | 157.65 | 下 | 87 | 下げ |
| AKAM | 光・通信・ネットワーク | -7.2% | 1.1倍 | 85.11 | 下 | 13 | 下落相場 |
| VST | データセンターの電力・冷却・部品・受託製造・建設 | -7.2% | 1.3倍 | 115.25 | 下 | 8 | 下げ |
| KEYS | 半導体製造装置・材料・設計ソフト・計測 | -7.1% | 2.4倍 | 261.51 | 下 | 49 | 下げ |
| DLR | データセンターの電力・冷却・部品・受託製造・建設 | -6.6% | 1.6倍 | 162.46 | 下 | 28 | 下げ |
| ASML | 半導体製造装置・材料・設計ソフト・計測 | -6.6% | 2.1倍 | 1266.22 | 下 | 18 | 下げ |
| PLTR | AIプラットフォーム・クラウド | -6.6% | 1.5倍 | 143.49 | 下 | 30 | 下げ |
| NXPI | 半導体 | -6.6% | 2.3倍 | 235.15 | 下 | 58 | レンジ |
| NRG | データセンターの電力・冷却・部品・受託製造・建設 | -6.4% | 1.4倍 | 87.80 | 下 | 3 | 下げ |
| SHOP | AIソフト・セキュリティ・ITサービス | -6.3% | 1.6倍 | 123.72 | 下 | 34 | 下げ |
| SWKS | 半導体 | -6.0% | 0.5倍 | 73.91 | 下 | 77 | 下げ |
| META | AIプラットフォーム・クラウド | -5.9% | 1.2倍 | 560.84 | 下 | 34 | 下げ |
| ETN | データセンターの電力・冷却・部品・受託製造・建設 | -5.8% | 1.8倍 | 311.33 | 下 | 14 | 下落相場 |
| CEG | データセンターの電力・冷却・部品・受託製造・建設 | -5.8% | 1.4倍 | 237.41 | 下 | 12 | 下げ |
| CRWD | AIソフト・セキュリティ・ITサービス | -5.8% | 1.3倍 | 229.44 | 下 | 99 | 下げ |
| ROK | データセンターの電力・冷却・部品・受託製造・建設 | -5.5% | 1.5倍 | 361.93 | 下 | 22 | 下げ |
| DDOG | AIソフト・セキュリティ・ITサービス | -5.5% | 1.3倍 | 157.37 | 下 | 25 | 下げ |
| FTNT | AIソフト・セキュリティ・ITサービス | -5.2% | 1.3倍 | 124.56 | 下 | 84 | 下げ |
| MCHP | 半導体 | -5.2% | 2.8倍 | 55.44 | 下 | 10 | 下落相場 |
| PANW | AIソフト・セキュリティ・ITサービス | -5.1% | 1.9倍 | 343.32 | 下 | 98 | 下げ |
| RDDT | AIソフト・セキュリティ・ITサービス | -5.1% | 1.1倍 | 85.33 | 下 | 1 | 下落相場 |
| EQIX | データセンターの電力・冷却・部品・受託製造・建設 | -4.9% | 2.2倍 | 968.22 | 下 | 55 | レンジ |

- 局面（判定式はClaudeが置いたもの）: **上昇相場**＝終値 > 50日線 > 200日線、50日線が20取引日前より2%以上高い、ADX(14) ≧ 20／**下落相場**＝終値 < 50日線 < 200日線、50日線が20取引日前より2%以上低い、ADX(14) ≧ 20／**上げ**＝それ以外で終値が50日線より上、かつ50日線が10取引日前より上か20日線が5取引日前より上／**下げ**＝それ以外で終値が50日線より下、かつ50日線が10取引日前より下か20日線が5取引日前より下（急な下げの初めは50日線がまだ上向きのため20日線でも見る）／**レンジ**＝どれにも当たらない（2026-11-05 から5つ。それまでは上昇相場とレンジの2つだけで、下げている銘柄もレンジと出ていた）。

## 4-2. 監視外の注目銘柄（S&P500・NASDAQ100のうち監視銘柄に入っていない銘柄）

条件: 流動性（株価5ドル以上・50日平均出来高25万株以上）があり、(a) 前日比+8%以上かつ出来高が50日平均の2倍以上、または (b) 終値が直前1年の最高値（終値）を上回り、RS≧90。RSの高い順に5銘柄（ニュースを調べる）。監視銘柄に入れるかはユーザーが決める。

| 銘柄 | 種類 | 前日比 | 出来高（50日平均の倍） | RS | 終値 |
|---|---|---|---|---|---|
| GPN | 急騰 | +9.9% | 3.3倍 | 80 | 91.83 |

## 5. 保有銘柄の手じまい条件（`新分析ツール/保有銘柄.md`）

| 銘柄 | ルール | 買った日 | 買値 | 終値 | 損益 | 損切り価格（買値の15%下、逆指値） | ルールの手じまい条件 | 出来高2倍の大陰線（買った後の直近5日） | 次回決算予定日 |
|---|---|---|---|---|---|---|---|---|---|
| SNDK | ルール外（ユーザーの判断。この日はどのルールの合図もなし） | 2026-10-21 | 171.4125 | 取得不可 | | | | | |
| AMD | ボリンジャーIII | 2026-10-21 | 549.97 | 424.39 | -22.8% | 467.47 | **損切り価格を下回った**（2026-11-02 の安値 466.07。逆指値なら約定済み。まだ持っていれば次の寄り付きで売る） **成立（出来高2倍の大陰線が 2026-11-05 に出た → まだ持っていれば次の寄り付きで全部売る）** 売りの指値: 上部バンド 604.03（今夜この値に置き直す。届いた日に売れる）（2倍ETF AMUU で持っている場合も、判定は元の株 AMD の値段） | なし | 2027-02-02 |

- 出来高2倍の大陰線: 実体（始値−終値）が前日までのATR(14)の1.5倍以上、終値がその日の値幅の下25%以内、出来高が前日までの50日平均の2倍以上の日。**押し目（ボリンジャーIII）・急落の底の保有では売りのルール**: 出たら翌日の寄り付きで全部売り、空いた枠で次の合図を買う（2026-10-02 ユーザー決定。`バックテスト結果/やり直し_売りの合図の組み合わせ.md`。乱数3組とも年率が約+2ポイント、最大下落率もやや下がった）。ミネルヴィニ・新高値V2の保有では事実の表示（順張りに足しても良くならなかった）。

- 半分売りの合図（ミネルヴィニ・新高値V2の保有だけ）: 反転のローソク足（かぶせ線・弱気の包み足・宵の明星・流れ星）＋出来高が50日平均の1.5倍以上＋RSI(14)が前日か当日に70以上。買った後に最初に出た日の翌日の寄り付きで半分売り、残り半分は50日線割れ・損切り15%まで持つ（2026-10-01 ユーザー決定。`バックテスト結果/半分だけ売るとオニールの空き枠.md`）。

- かぶせ線（ミネルヴィニ・新高値V2の保有だけ）: 上昇中の陽線の翌日に、前日の高値より上で寄り付き、前日の陽線の真ん中より下（前日の始値より上）で引けた日。翌日の寄り付きで全部売り、空いた枠で次の合図を買う。半分売りより優先する（2026-10-01 ユーザー決定。`バックテスト結果/2倍ETFで売って買い直す.md`。順張りの売買の25%で出て、1回平均+2.0%、年率 21.4%→26.4%）。

## 5-2. 前日（2026-11-19の引け）の【買い（予約）】の確認

前日の【買い（予約）】はなし。

## 6. 候補（採用したルールの条件が成立＝A。予約（B）は2026-10-25から注文せず、節6-3に参考の表示だけ）

建玉の目安: 同時保有4銘柄まで、1銘柄に資金の25%（資金÷4）、損切りは買値の15%下（ユーザー決定 2026-09-29）。

保有中のため候補から外した銘柄（合図は出ている）: AMD

**急落の底の指値に届いた銘柄（注文していれば約定。保有銘柄.md に買った日・値段を記録する。今日の候補には出さない）**: MRVL（2026-11-19の合図、指値 135.70、2026-11-20の安値 120.56。寄り付き 132.89 が指値より下だったので寄り付きで約定）、NBIS（2026-11-19の合図、指値 94.98、2026-11-20の安値 80.67。寄り付き 93.69 が指値より下だったので寄り付きで約定）

パターン: A＝最新の足で採用ルールの条件が成立（押し目・ミネルヴィニ・新高値V2は翌日の寄り付きで成行、急落の底は合図の日の終値の2%下に指値で3取引日待つ。2026-11-03 ユーザー採用）。条件の成立が目前の銘柄（B）は、予約の注文をやめたので節6-3に参考として出す（2026-10-25 ユーザー決定）。

| 銘柄 | グループ | パターン | 種類 | ルールの過去の成績 | 終値 | 前日比 | RS | 50日線の傾き | 局面 | 当てはまった条件 | 次回決算予定日 | 注文の目安 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DELL | AIサーバー・ストレージ・メモリ・端末 | A | 逆張り: 急落の底（担当: コナーズ） | 2位（勝率65%・1回平均+2.1%） | 278.02 | -11.0% | 98 | -8.1% | 下げ | 直前5日の最高値（終値）から-19.3%下落（−15%以上）、RSI(2)=1.6（≦10）、急落の前は50日線＞200日線。市場全体の局面: S&P500 横ばい／NASDAQ100 横ばい | 2026-11-24（4日後）**決算が近い** | 指値買い 272.46（合図の日 2026-11-20 の終値 278.02 の2%下。今日から3取引日。届かなければ見送り、途中で終値が5日線を上回ったら取り消す）。損切り: 約定した値段の15%下。手じまい: 終値が5日線（今日 309.40）を上回った翌日の寄り付き（コナーズ）。**元の株で買う**（2倍ETF DLLL のある銘柄だが、S&P500が20週線で「横ばい」の局面のため。案1）。**株数の目安: 8株**（2,384ドル÷272.46。注文の価格）、購入金額 約2,180ドル |
| HPE | AIサーバー・ストレージ・メモリ・端末 | A | 逆張り: 急落の底（担当: コナーズ） | 2位（勝率65%・1回平均+2.1%） | 40.91 | -10.1% | 96 | -2.8% | 下げ | 直前5日の最高値（終値）から-15.3%下落（−15%以上）、RSI(2)=0.5（≦10）、急落の前は50日線＞200日線。市場全体の局面: S&P500 横ばい／NASDAQ100 横ばい | 2026-11-23（3日後）**決算が近い** | 指値買い 40.09（合図の日 2026-11-20 の終値 40.91 の2%下。今日から3取引日。届かなければ見送り、途中で終値が5日線を上回ったら取り消す）。損切り: 約定した値段の15%下。手じまい: 終値が5日線（今日 44.97）を上回った翌日の寄り付き（コナーズ）。**株数の目安: 59株**（2,384ドル÷40.09。注文の価格）、購入金額 約2,365ドル |
| MU | 半導体 | A | 逆張り: 急落の底（担当: コナーズ） | 2位（勝率65%・1回平均+2.1%） | 594.51 | -13.9% | 92 | -7.2% | 下げ | 直前5日の最高値（終値）から-23.6%下落（−15%以上）、RSI(2)=0.7（≦10）、急落の前は50日線＞200日線。市場全体の局面: S&P500 横ばい／NASDAQ100 横ばい | 2026-12-17（27日後） | 指値買い 582.62（合図の日 2026-11-20 の終値 594.51 の2%下。今日から3取引日。届かなければ見送り、途中で終値が5日線を上回ったら取り消す）。損切り: 約定した値段の15%下。手じまい: 終値が5日線（今日 684.33）を上回った翌日の寄り付き（コナーズ）。**元の株で買う**（2倍ETF MUU のある銘柄だが、S&P500が20週線で「横ばい」の局面のため。案1）。**株数の目安: 4株**（2,384ドル÷582.62。注文の価格）、購入金額 約2,330ドル |
| SNPS | 半導体製造装置・材料・設計ソフト・計測 | A | 逆張り: ボリンジャー メソッドIII | 3位（勝率68%・1回平均+1.5%） | 396.17 | -8.1% | 33 | +4.1% | 下げ | %b=-0.219（<0.05）、21日II%=+0.105（>0） | 2026-12-08（18日後） | 翌日の寄り付きで買い。損切り: 買値の15%下。手じまい: 買った日の夜から、売りの指値をその日の上部バンド（今日 495.56）に置き、毎晩その日の値に置き直す。**株数の目安: 6株**（2,384ドル÷396.17。今日の終値。寄り付きの値段で変わる）、購入金額 約2,377ドル |
| DLR | データセンターの電力・冷却・部品・受託製造・建設 | A | 逆張り: ボリンジャー メソッドIII | 3位（勝率68%・1回平均+1.5%） | 162.46 | -6.6% | 28 | -2.4% | 下げ | %b=-0.329（<0.05）、21日II%=+0.039（>0） | 2026-10-29（-22日後） | 翌日の寄り付きで買い。損切り: 買値の15%下。手じまい: 買った日の夜から、売りの指値をその日の上部バンド（今日 187.57）に置き、毎晩その日の値に置き直す。**株数の目安: 14株**（2,384ドル÷162.46。今日の終値。寄り付きの値段で変わる）、購入金額 約2,274ドル |

- 局面（判定式はClaudeが置いたもの）: **上昇相場**＝終値 > 50日線 > 200日線、50日線が20取引日前より2%以上高い、ADX(14) ≧ 20／**下落相場**＝終値 < 50日線 < 200日線、50日線が20取引日前より2%以上低い、ADX(14) ≧ 20／**上げ**＝それ以外で終値が50日線より上、かつ50日線が10取引日前より上か20日線が5取引日前より上／**下げ**＝それ以外で終値が50日線より下、かつ50日線が10取引日前より下か20日線が5取引日前より下（急な下げの初めは50日線がまだ上向きのため20日線でも見る）／**レンジ**＝どれにも当たらない（2026-11-05 から5つ。それまでは上昇相場とレンジの2つだけで、下げている銘柄もレンジと出ていた）。

- 2倍ETF: 2倍ETFがある銘柄（ユーザーがムームー証券で買えることを確認した38銘柄のうち、目減りが年15%未満のもの）は、株の代わりに2倍ETFを買う（2026-10-04 ユーザー決定。`バックテスト結果/2倍ETFを使う決まり.md`。年率 約27%→約33%、確定した損益だけの最大下落率 約30%→約31%、含み損込みは約33%→約45%）。買う金額は株と同じ（資金の25%）。合図・損切り（元の株の買値の15%下＝ETFでは約30%下）・手じまいはすべて元の株の値段で判定する。指値・逆指値はETFの値段に直して置く。どのETFかは `新分析ツール/2倍ETFの対応表.json`（売買代金が1日500万ドル以上で、直近1年の目減りが一番小さいもの）。**2倍ETFで買うのは、S&P500が20週線（100日線）で「上昇」の局面のときだけ。横ばい・下落の局面では元の株で買う**（案1、2026-10-13 ユーザー採用。買う日に決め、買った後は局面が変わってもそのまま持つ。`バックテスト結果/流れ（市場の局面）を使う形.md`）。

- ルールの過去の成績: 今の売りのルールで、後知恵なしの監視銘柄・2015年〜の全部の合図の1回ごとの成績（2026-10-02計算、`新分析ツール/バックテスト結果/ルールごとの成績.md`）。順位は1回平均（1回の売買で平均いくら増えるか）の順。表はパターン（A→B）ごとに、この順位の良い順に並べた（表示の順番だけ。買う順番・件数の上限は変えていない。候補の選び方を変えても成績は変わらなかったため。2026-10-02 ユーザーの指示）。著者には渡さない。

- 同じ銘柄に押し目（ボリンジャーIII）と急落の底（コナーズ）の両方の合図が出た銘柄（ミネルヴィニと新高値V2が両方出た銘柄も、ミネルヴィニの1行）は、1行にまとめた（枠も1銘柄1つ。2026-10-30 ユーザー決定。バックテストでは、同じ場面の1回平均が押し目+8.1%・急落の底+1.5%で、急落の底を優先すると年率が下がった）: SWKS（もう一方の合図は省いた）

- 同じ業種は同時に2銘柄まで（ユーザー決定 2026-09-28）のため見送った候補（保有中の銘柄と、買う順番で先に残した候補で数える）: TXN（A・逆張り: ボリンジャー メソッドIII。Semiconductors: AMD・MU）、SWKS（A・逆張り: ボリンジャー メソッドIII。Semiconductors: AMD・MU）、ANET（A・逆張り: 急落の底。Computer Hardware: SNDK・DELL）、QCOM（A・逆張り: ボリンジャー メソッドIII。Semiconductors: AMD・MU）

- パターンBは各ルールでRSの高い順に2件まで、急落の底・新高値のAは4件（同時保有の上限）までとし、11件を省いた。

- 悪いニュースが続いているグループ（光・通信・ネットワーク）の候補（記録だけ。売買のルールは変えない。著者には渡さない）: なし

- 候補の数: 空き枠3（同時保有4銘柄まで。保有2、うち今日ルールの売りが成立1）＋予備2件まで表に出した（2026-10-25 ユーザー決定）。ほかの5件は枠に入らないので、著者の判定とニュース調査に回さない: Q（A・ボリンジャー メソッドIII、RS 25）、CDNS（A・ボリンジャー メソッドIII、RS 23）、CEG（A・ボリンジャー メソッドIII、RS 12）、CRWV（A・ボリンジャー メソッドIII、RS 0）、TMO（A・ボリンジャー メソッドIII、RS 91）

- テーマの外の候補（グループが「テーマの外」）: 監視銘柄の候補で枠が埋まらないときに使う（監視銘柄の候補を先に買う）。S&P500の今の構成銘柄のうち監視銘柄でない銘柄から、RS≧90・30週線が上向きで終値がその上・業種の3カ月の強さが上位20%の16銘柄を調べ、空き枠2つ分まで出した。バックテストでは、テーマの外の強い銘柄で空き枠を埋めると、テーマが弱い時期の成績が支えられた（`バックテスト結果/半導体・AIに特化した場合.md`。2026-10-01 ユーザー決定）。

- RS≧80の押し目（ボリンジャーIII）は、バックテストで成績がより安定していた（PF3.27、最大下落20%）。

## 6-2. 参考: ワインスタイン10週の合図（売買には使わない・著者には送らない）

後知恵なしのバックテストで、今の4つのルールに加えると年率が下がった（27.1%→22.9〜26.3%。`バックテスト結果/ワインスタイン10週を加えるか.md`）ため、2026-10-04 から参考の表示だけにした（ユーザー決定）。強い銘柄が10週の高値に近づいている、という事実として見る。

| 参考の銘柄 | グループ | パターン | 種類 | 終値 | 前日比 | RS | 当てはまった条件 |
|---|---|---|---|---|---|---|---|
| TGT | テーマの外（Discount Stores） | B | 予約: ワインスタイン（10週の高値の手前） | 165.83 | -1.0% | 97 | 直前10週の高値166.43まで0.4%、10週線が上向き |
| AIZ | テーマの外（Insurance - Property & Casualty） | B | 予約: ワインスタイン（10週の高値の手前） | 316.65 | +0.2% | 95 | 直前10週の高値326.20まで3.0%、10週線が上向き |
| LH | テーマの外（Diagnostics & Research） | B | 予約: ワインスタイン（10週の高値の手前） | 367.13 | -0.5% | 94 | 直前10週の高値375.10まで2.2%、10週線が上向き |
| PTC | テーマの外（Software - Application） | B | 予約: ワインスタイン（10週の高値の手前） | 195.10 | -0.3% | 94 | 直前10週の高値196.79まで0.9%、10週線が上向き |
| CAH | テーマの外（Medical Distribution） | B | 予約: ワインスタイン（10週の高値の手前） | 272.81 | +0.2% | 94 | 直前10週の高値286.29まで4.9%、10週線が上向き |
| ADP | テーマの外（Software - Application） | B | 予約: ワインスタイン（10週の高値の手前） | 301.71 | +0.2% | 93 | 直前10週の高値311.89まで3.4%、10週線が上向き |
| MCK | テーマの外（Medical Distribution） | B | 予約: ワインスタイン（10週の高値の手前） | 1069.43 | +0.7% | 93 | 直前10週の高値1121.50まで4.9%、10週線が上向き |
| DGX | テーマの外（Diagnostics & Research） | B | 予約: ワインスタイン（10週の高値の手前） | 258.28 | -0.3% | 92 | 直前10週の高値262.00まで1.4%、10週線が上向き |


## 6-3. 参考: 条件の成立が目前の銘柄（予約は注文しない・著者には送らない）

2026-10-25 ユーザー決定: 予約（逆指値・指値）の注文はやめ、参考の表示だけにする。毎朝のツールと同じ条件・値段で予約の約定をバックテストに入れると、どの形も年率が下がった（後知恵なし 35.7%→30.7〜34.2%、87銘柄 45.6%→34.2〜42.6%。`バックテスト結果/点検_2026-10-25/`）。引けで条件がそろえば、翌朝の節6に買いの候補（A）として出る。各ルールでRSの高い順に2件まで。

| 参考の銘柄 | グループ | 種類 | 終値 | 前日比 | RS | 当てはまった条件 | 条件がそろう目安の価格（注文はしない） |
|---|---|---|---|---|---|---|---|
| EQIX | データセンターの電力・冷却・部品・受託製造・建設 | ボリンジャー メソッドIII（%bが0.05未満に近い） | 968.22 | -4.9% | 55 | %b=0.052（0.05まであと少し）、21日II%=+0.037（>0） | 967.95（この値より下で引けると翌朝の買いの候補（A）。目安） |


# ニュース（サブエージェントの調査）

# ニュース調査（2026-11-20の引け時点。調査日 2026-11-22）

出典は headlines.md の見出し（媒体・日付）を優先。検索で確かめたものは「検索」と記す。売買の判断は書かない。

## テーマ全体の下げの原因
- 当たる日（監視銘柄3銘柄以上が-5%以下、2グループ以上の1週が-5%以下、S2あり）。headlines.md で確認。
- きっかけ: Nvidia CEOの辞任（The Motley Fool 11/14「Nvidia Stock Falls Below $165 After Its CEO Resigns」）。MarketWatch 11/19「6取引日でNvidiaは6,690億ドル失った」。11/20 CNBC「Nvidia plunges 14%、2008年金融危機以来で最長の週間連続下落」。検索でも、AIハード売りがNvidia CEO退任から始まったとのMotley Fool 11/13の記載あり。
- 11/20の広がり: Reuters 11/20「Wall St ends sharply lower on AI selloff, S&P 500, Dow in correction」、NPR 11/20「S&P500 -3.7%、Nasdaqは年初来マイナスに」、Kiplinger 11/20「Nasdaq 1,261ポイント安、AnthropicとAI株が下落」、MarketWatch 11/20「チップ株は週間で2.3兆ドルが消えた」。Amazon・大型テックも下落（Motley Fool 11/21）。
- 追加材料（見出し）: 米国のAIチップ規制強化（Reuters 11/20）、NYT 11/21「中国のスパイがNvidia不祥事の数年前からAIチップを狙った」、Cisco 15.5%安（24/7 Wall St. 11/21）、Anthropic関連（Yahoo Finance 11/20「Anthropic dips after-hours」。11/19にAnthropicのIPO上場の見出しあり、Investing.com 11/19）。
- 呼び名: 「Blue Tsunami」（IBD 11/20）、「ブラックマンデー」への警戒（Barron's 11/21、朝鮮日報 11/21）。「リーマン・ショックが頭をよぎる」（みんかぶ 11/21）。単一の「〇〇ショック」の名は確認できず。
- 市場全体: S&P500・Dowは調整局面入り（Reuters 11/20）。VIX・ハイイールド債の数値は取得不可。
- 信用: 見出しでは、データセンター債務が今年4,660億ドル、信用市場はAI借り手を格付けより低く評価（CEO Economy 11/20）、「AI資金調達の鎖はどこで切れるか」（MacroMicro 11/20）、Crash Signals: Credit Stress（Financial Sense 11/20）。検索では10月中旬にAI企業のCDSが過去最高（BusinessDay 10/15、Semafor 10/15）、CoreWeave 5年CDSは11/6に約1,155bp（11/5に1,289bp超）、Oracle CDS約305bp（11月初め、IFR）。11/20当日の社債・CDSの数値は取得不可。
- 経済指標・金利・要人発言: 11/20当日の特定の指標は確認できず。Trump氏のイラン判断に先物が下落（Benzinga 11/20）。
- 大手の決算: NvidiaとSalesforceの決算は通過済み。好決算でも時間外で下落（野村證券 11/20）。
- 検索した語句: 「Nasdaq dives Anthropic AI stocks sink November 20」「AI data center debt credit spreads CoreWeave bonds Oracle CDS」。

## 引け後・時間外の材料
- CRWD: 時間外 -4.8%。Zscalerの買収協議報道（約2,650億ドルとの見出し）。ZSは時間外で急騰（Yahoo Finance 11/20、Unite.AI 11/20「CrowdStrike Reportedly in Talks to Acquire Zscaler」）。
- FLEX: 時間外 +4.0%。原因の見出しは見つからなかった。
- NBIS: 時間外 +3.9%。原因の見出しは見つからなかった（3%台のため参考）。
- AMD（保有）: 時間外 +3.6%（TradingView 11/20 に「AMD +1.3% 時間外」の見出し。数値は見出しと表で異なる）。材料は見つからず、全体の時間外反発とみられるが断定しない。
- 候補 DELL +2.9%、MU +2.7%、HPE +2.7%、SNPS +1.6%、DLR -0.8%。個別の材料は見つからなかった。±5%以上はなし。

## SNDK（保有。scan.md では価格が取得不可。headlines の表では引け79.30、時間外+2.6%）
- 11/20 Benzinga「Why Sandisk Stock Is Falling Today?」、Investing.com「Why is SanDisk stock sliding today?」、24/7 Wall St.「Pulled Back」。内容は取得不可（見出しのみ）。
- 11/17 The Motley Fool「Why Sandisk Stock Keeps On Going Down」。11/13のMotley Foolは、AIハード売り（Nvidia CEO退任発端）で下落と報じた（検索）。
- 11/21 24/7 Wall St.: Renaissance TechnologiesがSanDisk保有を55倍超に増やし4.81億ドル。SK HynixがKioxiaの筆頭株主になる見通し。
- 11/16 BigGo Finance: BernsteinはDell・SanDiskなどを「不当に売られた」と指摘。
- 悪材料: 業界全体の下落以外に個別の不祥事は確認できず。

## AMD（保有）
- 11/19 CNBC「AMD dives on short seller report of alleged China exposure」。Hunterbrook Capitalが空売りを開示し、AMDのファームウェアが米国が制裁済みの中国IEIT系サーバーメーカーで見つかったと指摘（IBTimes、Motley Fool 11/19、検索）。中国・香港向け売上は22.4%、組立・テストを中国Tongfu系の合弁に依存と報告書は記す。報告書自身は、輸出規制違反の証明にはならないと書いている。AMDの回答の内容は確認できず。
- 11/20 Forbes: 報告を受けプレマーケットで大きく下落。11/20の-13.2%は市場全体の下げと重なる。
- 11/14 Motley Fool: 前週は上昇。
- 決算: 次回 2027-02-02（scan.md）。公式発表の確認は取得不可。
- 悪材料: あり（空売りレポートの中国関連の指摘。違法の証明はなしと報告書自身が記載）。

## DELL（候補、決算 2026-11-24）
- 11/20 24/7 Wall St.: AI売りで10%安、2018年の再上場以降で最悪の月に向かう。決算は火曜（11/24）。
- 11/20 Benzinga「Why Is Dell Stock Falling on Friday?」。11/16 Trefis「Falling Again?」。11/18 Yahoo Finance「Surging Today」。11/16 Barron's「DellとHPEは売られすぎの可能性」。
- 11/20 BigGo: 決算を前にAIハード売りが深刻化。11/17 24/7 Wall St.: 米国の新たな輸出規制がSuper Microの中国問題を深める懸念。
- 次回決算日: 11/24（scan.md。公式発表の確認は取得不可）。決算は引け後か不明。
- 悪材料: 業界の下落と輸出規制の懸念。個別の不祥事は確認できず。

## HPE（候補、決算 2026-11-23）
- 11/20 TradingView: IonQ、HPE、Everpure、Super Microなどが急落。11/18 Yahoo Finance「Rising Today」。
- 11/16 Barron's: DellとHPEは叩かれたが売られすぎの可能性。
- 11/21 24/7 Wall St.: Ciscoが過去15年で最強の成長にもかかわらず15.5%安。
- 次回決算日: 11/23（scan.md。公式発表の確認は取得不可）。
- 悪材料: 個別の不祥事は確認できず。

## MU（候補、決算 2026-12-17）
- 11/20 Motley Fool「Why Micron Stock Crashed Today」。11/19 Yahoo Finance「Why Micron Stock Finally Popped Today」。11/17 Barron's「Drops Again」。
- 11/16 BoiseDev: トランプ政権が中国のAI先端チップ利用の抜け穴を塞ぎ、株が下落。
- 11/21 Motley Fool: 5月以来の安値。SK Hynix・中国メーカーとの競争の見出しもあるが内容は取得不可。
- 悪材料: 輸出規制の強化（11/16）。個別の不祥事は確認できず。

## SNPS（候補、決算 2026-12-08）
- 11/20 Barchart.com: 新たに強気の格付け。11/19 Investing.com: BarclaysがOverweightで新規カバー（AI研究開発の追い風とEDAの優位）。
- 11/20 Yahoo Finance: 見通しの改善。割高との見方もあり。11/16 MarketWatch: 小幅安。
- 11/20の-8.1%は半導体全体の下げと同時（個別材料なし）。
- 悪材料: 確認できず。

## DLR（候補、前回決算 2026-10-29）
- 11/20 24/7 Wall St.: 5.1%安。11/20 TradingView: Truistが目標株価を220ドルから215ドルへ引き下げ、評価はBuy維持。
- 11/16 GlobeNewswire / MT Newswires: OVHcloudとのソブリンクラウド拡大、欧州のクラウド接続拡大。
- 11/17 24/7 Wall St.: Eisman氏は地方自治体によるデータセンター建設の遅れが最大のAIリスクと発言。
- 悪材料: 確認できず（目標株価の小幅引き下げのみ）。

## 監視外の注目銘柄
- GPN: 前日比+9.9%、出来高3.3倍。原因は調べていない（候補・保有ではなく検索対象外、見出しにもなし）。取得不可。

## テーマ全体のニュース（直近1週間）
- 米国のAIチップ輸出規制の強化（Reuters 11/20。MU・SMCI・DELLに関連する見出しは11/16〜17）。
- Anthropic上場前後の動き（Investing.com 11/19「Anthropic debut」前のプレマーケット上昇、11/20に下落）。
- Nvidia CEO退任（11/14）と、決算後も続く下落（野村證券 11/20）。
- Amazonが約75億ドルでDecart買収に近いとの報道（BigGo 11/21）。Nvidia、Inceptionを5億ドル超で買収交渉（Tech Funding News 11/20）。

# ニュースの見出し（プログラムが自動で取得）

- Googleニュース（日付を指定）とYahooファイナンスの見出しを `tools/news_headlines.py` が自動で並べたもの。日付は米国東部時間の配信日（引け後の記事は翌日付）。原因の判断・売買の判断はしていない。
- 調べた銘柄の選び方: ①保有 ②今日の候補 ③時間外に±5%以上動いた監視銘柄 は全部、④引けまでに大きく動いた銘柄（1週で±5%のグループの上位3・1日で±7%）は合計12銘柄まで。
- 1週で−5%以下のグループ: 半導体製造装置・材料・設計ソフト・計測（-15.3%）、半導体（-14.4%）、光・通信・ネットワーク（-14.2%）、AIサーバー・ストレージ・メモリ・端末（-13.1%）、AIプラットフォーム・クラウド（-12.6%）、AIソフト・セキュリティ・ITサービス（-11.2%）、データセンターの電力・冷却・部品・受託製造・建設（-9.7%）
- 1週で+5%以上のグループ: なし

## 0. 時間外（引け後）の値動き（2026-11-20 の引けから、Yahoo。±3%以上の監視銘柄と、保有・候補は全部）

| 銘柄 | 区分 | 引け | 時間外 | 騰落率 |
|---|---|---|---|---|
| CRWD | 監視 | 229.46 | 218.34（19:59 ET） | -4.8% |
| FLEX | 監視 | 66.22 | 68.86（19:58 ET） | +4.0% |
| NBIS | 監視 | 81.33 | 84.53（19:59 ET） | +3.9% |
| AMD | 保有 | 424.26 | 439.39（19:59 ET） | +3.6% |
| AMAT | 監視 | 302.15 | 312.66（19:46 ET） | +3.5% |
| TER | 監視 | 204.86 | 211.99（19:58 ET） | +3.5% |
| COHR | 監視 | 187.24 | 193.56（19:59 ET） | +3.4% |
| NVDA | 監視 | 125.79 | 130.01（19:59 ET） | +3.4% |
| PWR | 監視 | 559.28 | 577.58（18:42 ET） | +3.3% |
| INTC | 監視 | 51.37 | 53.03（19:59 ET） | +3.2% |
| CRWV | 監視 | 39.56 | 40.84（19:59 ET） | +3.2% |
| ALAB | 監視 | 180.27 | 186.00（19:57 ET） | +3.2% |
| MCHP | 監視 | 55.44 | 57.18（18:35 ET） | +3.1% |
| ANET | 監視 | 167.65 | 172.74（19:56 ET） | +3.0% |
| DELL | 候補 | 278.13 | 286.18（19:59 ET） | +2.9% |
| MU | 候補 | 594.39 | 610.60（19:59 ET） | +2.7% |
| HPE | 候補 | 40.87 | 41.97（19:59 ET） | +2.7% |
| SNDK | 保有 | 79.30 | 81.40（19:59 ET） | +2.6% |
| SNPS | 候補 | 396.66 | 402.90（17:32 ET） | +1.6% |
| DLR | 候補 | 162.51 | 161.20（16:56 ET） | -0.8% |

## 1. 市場全体（2026-11-20）

### 市場全体（英語のまとめ記事）
検索語: `stocks Wall Street close Nasdaq`
- 11/20 Nasdaq | Bell Ringing Ceremony
- 11/20 Reuters | Wall St ends sharply lower on AI selloff, S&P 500, Dow in correction
- 11/20 NPR | S&P 500 sinks 3.7% and the Nasdaq composite goes negative for the year
- 11/21 Fortune | Stock market correction? This chief investment officer sees the S&P 500 soaring 45% to 10,000
- 11/21 Barron's | Worried About Black Monday? What Wall Street Says Could Happen.

### 市場全体（Stock Market Today）
検索語: `"stock market today"`
- 11/20 Investor's Business Daily | Stock Market Today: Stock Market News And Analysis
- 11/20 The Motley Fool | Stock Market Today, Nov. 20: Stocks Plunge as AI Trade Unwinds
- 11/20 Kiplinger | Nasdaq Dives 1,261 Points as Anthropic, AI Stocks Sink: Stock Market Today
- 11/20 Benzinga | Stock Market Today: Dow Jones, S&P 500, Nasdaq 100 Futures Fall as Trump Weighs Iran Decision— INTU, ROST
- 11/21 The Motley Fool | Stock Market Today, Nov. 20: Amazon Shares Slide on AI and Mega-Cap Tech Sell-Off

### 市場全体（日本語のまとめ記事）
検索語: `米国株式市場 OR NY株`
- 11/20 外為どっとコム | 【見通し】NY株見通しー軟調か AI関連株への警戒続く
- 11/20 Reuters | 米国株式市場、ＡＩ懸念で売り加速：識者はこうみる
- 11/20 野村證券 | エヌビディア、好決算でも時間外で株価下落 米国株式市場への影響と今後の注目点 野村證券・村山誠
- 11/21 BigGo ファイナンス | 韓国政府、ニューヨーク株安を受け緊急F4会議を招集…23日寄り付き前に安定策を協議
- 11/21 株探 | 米国株式市場見通し：テクノロジー株のバリュエーション調整進み反転余地広がる

### 半導体・AI株（英語）
検索語: `chip stocks OR semiconductor stocks OR AI stocks`
- 11/20 CNBC | A massive bearish trade just happened in the chip stocks
- 11/20 Reuters | US AI chip curbs hit China tech stocks, spur self-sufficiency push
- 11/20 Investor's Business Daily | Chip Stocks To Watch And Semiconductor Industry News
- 11/20 MarketWatch | Chip stocks see $2.3 trillion weekly wipeout as panic grips the AI trade
- 11/20 Investor's Business Daily | AI Stocks' Wild Ride Gets Bumpier As Nvidia Chaos, Blue Tsunami Spook Investors

### 信用（社債・借金）
検索語: `AI debt OR bonds OR credit spreads OR CDS`
- 11/20 Bloomberg.com | Vanguard, TCW Eye Hidden Upside in MBS Over Corporate Bonds
- 11/20 MacroMicro | Outlook 2027 Series | III. From the Most Crowded Trade to the Top Financial Risk: Where Will the AI Funding Chain Break First?
- 11/20 BigGo Finance | AI Infrastructure Boom Pushes European Bond Issuance Past €2 Trillion for First Time, Setting Record
- 11/20 Financial Sense | Crash Signals: Tech Wreck, Credit Stress, and the Fed’s Dilemma
- 11/20 CEO Economy | Credit markets price AI borrowers below their ratings as data-center debt reaches $466 billion this year

### 「〇〇ショック」の呼び名（日本語）
検索語: `ショック 株`
- 11/20 野村證券 | 原油高が続く局面で、相場連動性の低い銘柄に偏重すべきでない理由 野村證券ストラテジストが解説
- 11/20 野村證券 | 金利上昇懸念で不動産株が急落 行き過ぎ感も、銀行株には追い風期待 野村證券ストラテジストが解説
- 11/21 조선일보 | 米ハイテク株投げ売りショック、韓国株式市場に「ブラックマンデー」来るか
- 11/21 Yahoo!ニュース | 「リーマン・ショックが頭をよぎる」米国在住投資家がAI株を減らし、代わりに買った“意外な銘柄”（みんかぶマガジン）
- 11/21 note | 3連休から始まる「冬の書き入れ時」…日本スキー場開発（6040）が"インバウンド×雪"で化ける可能性、半導体ショックと無縁の季節株を今見ておくべき理由｜日本個別株デューデリジェンスセンター

### 引け後・時間外の動き（英語）
検索語: `"after hours" OR "after the bell" OR "extended trading" stocks`
- 11/20 Yahoo Finance | ZS Stock Soars After-Hours While CRWD Slips On Reported $265B Takeover Talks
- 11/20 CNN | NVDA Stock Quote Price and Forecast
- 11/20 TradingView | Intuit Stocks Drop 9.52% After Hours on Credit Karma Guide Cut and Mailchimp Sale
- 11/20 Yahoo Finance | Anthropic dips after-hours as AI jitters persist - what’s moving markets
- 11/20 ChartMill | S&P 500 After-Hours Gainers: DDOG, HBAN Lead Postmarket Session
- 11/20 TradingView | Theriva Biologics sets 1-for-30 reverse split; stock crashes after-hours
- 11/20 TradingView | Oracle Gains 2.3% and AMD Rises 1.3% in After-Hours AI Stock Trading
- 11/20 Benzinga | Onfolio Holdings (ONFO) Stock Drops 16.80% After Hours: Here's What Investors Should Know

### 引け後・時間外の動き（日本語）
検索語: `時間外 決算 株`
- 11/20 株探 | ロス・ストアーズ、決算受け時間外で５％安＝米国株個別
- 11/20 野村證券 | エヌビディア・セールスフォース決算通過 AI半導体市場へのインプリケーション 野村證券・村山誠
- 11/20 BigGo ファイナンス | デル株、決算発表を前に下落 AIハードウェア売りが深刻化
- 11/20 野村證券 | AI規制が注目される中でのエヌビディア決算 マーケットへの影響と今後の注目点を解説 野村證券・村山誠
- 11/20 BigGo ファイナンス | ヤルデニ氏、AI株売りは買い場と指摘 アンソロピック決算に期待
- 11/21 株探 | 国内株式市場見通し：短期的にはAI・半導体関連株中心に売られ過ぎ感への意識強まる
- 11/21 TradingKey | ターゲット、第3四半期の業績上振れと見通し引き上げも時間外で2％超下落 アパレル事業の圧迫続く

### 買収・合併（英語）
検索語: `acquisition OR acquire OR merger OR takeover chip OR semiconductor OR AI OR optical`
- 11/20 FeedNavigator.com | John Deere continues agtech acquisition streak, purchases Orchard AI
- 11/20 Unite.AI | CrowdStrike Reportedly in Talks to Acquire AI Security Partner Zscaler
- 11/20 OrangeSlices AI | Acquisition Professionals secures Department of Labor Acquisition and Administrative Management Support BPA
- 11/20 Benzinga | SpaceX Stock Drops Nearly 6% During AI Pullback, Anthropic Ties, Tesla Merger Talk
- 11/20 Tech Funding News | Report: Nvidia in advanced talks to acquire Stanford-led diffusion AI startup Inception for $500M+
- 11/21 The New York Times | China’s Spies Set Sights on A.I. Chips Years Before Nvidia Scandal
- 11/21 shattered.io | Amazon Decart Acquisition: Up to $7.5B Deal Explained
- 11/21 BigGo Finance | Amazon Reportedly Near $7.5 Billion Deal to Acquire Decart, Taking Aim at Nvidia With AI Chip Efficiency Push

## 2. 保有・候補・時間外で大きく動いた銘柄（2026-11-14〜2026-11-20 の見出し）

### SNDK（Sandisk Corporation、保有、時間外 +2.6%）

#### Googleニュース
検索語: `Sandisk stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/17 The Motley Fool | Why Sandisk Stock Keeps On Going Down
- 11/20 Benzinga | Why Sandisk Stock Is Falling Today?
- 11/20 24/7 Wall St. | SanDisk Stock Has Pulled Back. Here’s Where Shares Could Be Headed Next
- 11/20 Investing.com | Why is SanDisk stock sliding today?

#### Yahooファイナンス
検索語: `SNDK`
- 11/21 24/7 Wall St. | Renaissance Technologies Grew Its SanDisk Stake More Than 55-Fold to $481 Million
- 11/21 24/7 Wall St. | SK Hynix Is About to Become the Biggest Shareholder of Rival Kioxia
- 11/21 Motley Fool | Micron Stock Just Hit Its Lowest Price Since May. I'd Buy More Now.

### AMD（Advanced Micro Devices, Inc.、保有、半導体、前日比 -13.2%、1週 -20.5%、時間外 +3.6%）

#### Googleニュース
検索語: `Advanced Micro Devices stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/14 The Motley Fool | Why Advanced Micro Devices Stock Surged This Week
- 11/19 CNBC | AMD dives on short seller report of alleged China exposure
- 11/20 CNN | AMD Stock Quote Price and Forecast
- 11/20 Forbes | Nvidia Rival AMD’s Stock Slides Sharply In Premarket After Report Alleges China Ties

#### Yahooファイナンス
検索語: `AMD`
- （新しい見出しなし）

### DELL（Dell Technologies Inc.、候補、AIサーバー・ストレージ・メモリ・端末、前日比 -11.0%、1週 -19.3%、時間外 +2.9%）

#### Googleニュース
検索語: `Dell stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/16 Trefis | Why Is Dell Stock Falling Again?
- 11/18 Yahoo Finance | Why Is Dell Technologies Stock Surging Today?
- 11/20 Benzinga | Why Is Dell Stock Falling on Friday?
- 11/20 24/7 Wall St. | Dell Stock Plunges 10% in the AI Selloff and Heads for Its Worst Month Since Its 2018 Return to the Stock Market. Earnings Are Tuesday

#### Yahooファイナンス
検索語: `DELL`
- 11/21 24/7 Wall St. | Billionaire Daniel Loeb’s ‘Bear Math’: AI’s $7 Trillion Spending Boom Faces a $3 Trillion Reality Check
- 11/21 24/7 Wall St. | Jim Cramer Says the Market “Sliced Right Through” His S&P 500 Target
- 11/21 TIKR | Stanley Druckenmiller and 11 Other Big Funds Bought Western Digital Last Quarter. Ken Fisher and 13 Others Sold. Who’s Right?

### HPE（Hewlett Packard Enterprise Company、候補、AIサーバー・ストレージ・メモリ・端末、前日比 -10.1%、1週 -15.3%、時間外 +2.7%）

#### Googleニュース
検索語: `Hewlett Packard Enterprise stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/16 Barron's | Dell and HPE Stocks Are Getting Hammered. Why the Selloff May Be Overdone.
- 11/17 24/7 Wall St. | Super Micro Falls 4%, Dell and Hewlett Packard Enterprise Slide 2%: Do New U.S. Export Curbs Deepen Super Micro's China Problem?
- 11/18 Yahoo Finance | Why Is Hewlett Packard Enterprise Stock Rising Today?
- 11/20 TradingView | IonQ, Hewlett Packard Enterprise, Everpure, Infleqtion, and Super Micro shares plummet, what you need to know

#### Yahooファイナンス
検索語: `HPE`
- 11/21 24/7 Wall St. | Cisco Stock Fell 15.5% Despite Its Strongest Growth in 15 Years. Is the Dividend Safe?
- 11/21 Simply Wall St. | 3 AI Infrastructure Stocks With Up To 68% Revenue Growth

### MU（Micron Technology, Inc.、候補、半導体、前日比 -13.9%、1週 -23.6%、時間外 +2.7%）

#### Googleニュース
検索語: `Micron stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/16 BoiseDev | Micron stock tumbles as Trump admin. cuts a loophole allowing China access to advanced chips
- 11/17 Barron's | Micron Drops Again. What Hedge Funds Are Doing With the Stock.
- 11/19 Yahoo Finance | Why Micron Stock Finally Popped Today
- 11/20 The Motley Fool | Why Micron Stock Crashed Today

#### Yahooファイナンス
検索語: `MU`
- 11/21 24/7 Wall St. | Nvidia Stock Has Crashed 48% and Now Trades at 15 Times Earnings, Its Cheapest in More Than a Decade and Cheaper Than Microsoft and Broadcom
- 11/21 Motley Fool | Billionaire David Tepper Just Made a Massive AI Chip Rotation — Will It Pay Off?
- 11/21 Motley Fool | Should You Forget Nvidia and Buy These 2 AI Memory Stocks Instead?

### SNPS（Synopsys, Inc.、候補、半導体製造装置・材料・設計ソフト・計測、前日比 -8.1%、1週 -13.0%、時間外 +1.6%）

#### Googleニュース
検索語: `Synopsys stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/16 MarketWatch | Synopsys Inc. stock outperforms competitors despite losses on the day
- 11/20 Barchart.com | Synopsys Stock Just Scored a New Bullish Rating. Here's Why.
- 11/20 StockInvest.us | Synopsys Stock Price Forecast. Should You Buy SNPS?
- 11/20 Yahoo Finance | Synopsys (SNPS) Stock May Be 17% Overvalued As Guidance Improves

#### Yahooファイナンス
検索語: `SNPS`
- 11/19 Investing.com | Barclays starts Synopsys at Overweight, cites AI R&D tailwinds and EDA dominance
- 11/19 Investing.com | Synopsys vs Cadence: value and quality compared

### DLR（Digital Realty Trust, Inc.、候補、データセンターの電力・冷却・部品・受託製造・建設、前日比 -6.6%、1週 -9.7%、時間外 -0.8%）

#### Googleニュース
検索語: `Digital Realty Trust stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/15 Yahoo Finance | Why Equinix and Digital Realty Benefit From Data Center Zoning Battles
- 11/16 BigGo Finance | Bernstein: AI Hardware Stocks Caught in Indiscriminate Selloff; Dell, SanDisk and Others "Unfairly Punished"
- 11/20 24/7 Wall St. | Digital Realty Trust (DLR) Stock Falls 5.1% Today
- 11/20 TradingView | Truist Securities maintains Digital Realty Trust at Buy, lowers price target to $215 from $220

#### Yahooファイナンス
検索語: `DLR`
- 11/16 GlobeNewswire | Digital Realty Expands Sovereign Cloud Ecosystem with Four New OVHcloud Deployments
- 11/16 MT Newswires | Digital Realty Trust Expands Direct Cloud Connectivity in Europe
- 11/17 24/7 Wall St. | Steve Eisman Says the Biggest AI Risk Is Local Governments Slowing Data Center Construction

## 3. 引けまでに大きく下げた銘柄（2026-11-14〜2026-11-20 の見出し）

### LRCX（Lam Research Corporation、半導体製造装置・材料・設計ソフト・計測、前日比 -10.0%、1週 -18.9%、時間外 +3.0%）

#### Googleニュース
検索語: `Lam Research stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/16 24/7 Wall St. | Jim Cramer Says Lam Research Has Come Down Enough. It’s ‘Absolutely My Favorite’
- 11/17 Yahoo Finance | Lam Research Stock Fell Nearly 7%. What Happened?
- 11/19 StockInvest.us | Lam Research Stock Price Forecast. Should You Buy LRCX?
- 11/20 Investing.com | Why is Lam Research stock tumbling today?

#### Yahooファイナンス
検索語: `LRCX`
- 11/19 Barrons.com | Druckenmiller Retreats From Chip Stocks in Pivot to Gold Miners and SpaceX
- 11/19 Investing.com | Premarket movers: Palo Alto soars, chip stocks rally ahead of Anthropic debut
- 11/19 Simply Wall St. | 3 US AI Infrastructure Stocks Retail Investors Are Watching After Anthropic IPO

### AMAT（Applied Materials, Inc.、半導体製造装置・材料・設計ソフト・計測、前日比 -10.7%、1週 -18.2%、時間外 +3.5%）

#### Googleニュース
検索語: `Applied Materials stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/17 Yahoo Finance | Why Is Applied Materials Stock Down Over 5%?
- 11/19 24/7 Wall St. | Applied Materials Is Still Up 35% This Year. Will AMAT Stock Hit $300 or $400 First?
- 11/20 Seeking Alpha | Applied Materials sinks 11% amid broad chip stock pullback (AMAT:NASDAQ)
- 11/20 Global Banking & Finance Review | Applied Materials falls 10.71% in Friday's session

#### Yahooファイナンス
検索語: `AMAT`
- 11/19 TIKR | Susquehanna’s $600 Target Says TSMC’s Selloff Went Too Far
- 11/20 MT Newswires | Daiwa Securities Adjusts Price Target on Applied Materials to $370 From $515
- 11/20 Motley Fool | Nvidia and Micron Can't Make AI Chips Without This Growth Stock. Here's Why It Could Soar.

### TER（Teradyne, Inc.、半導体製造装置・材料・設計ソフト・計測、前日比 -10.0%、1週 -17.9%、時間外 +3.5%）

#### Googleニュース
検索語: `Teradyne stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/16 StockStory | Axcelis Technologies, FormFactor, ACM Research, Teradyne, and Applied Materials shares plummet, what you need to know
- 11/18 Yahoo Finance | Why Jefferies Calls Teradyne (TER) a “Compute Test Company”
- 11/19 Yahoo Finance | Is Teradyne (TER) a Solid Growth Stock? 3 Reasons to Think "Yes"
- 11/20 TradingView | FormFactor, Amkor, Himax, Teradyne, and Entegris shares are falling, what you need to know

#### Yahooファイナンス
検索語: `TER`
- 11/17 Insider Monkey | 5 Highest Short Interest Large-Cap Tech Stocks Right Now

### NVDA（NVIDIA Corporation、半導体、前日比 -14.0%、1週 -22.9%、時間外 +3.4%）

#### Googleニュース
検索語: `NVIDIA stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/14 The Motley Fool | Nvidia Stock Falls Below $165 After Its CEO Resigns: Is It a Bargain Buy?
- 11/17 AP News | Wall Street shakes again as Nvidia and other jittery AI stocks swing lower
- 11/19 MarketWatch | Nvidia’s stock falls further. It has lost $669 billion in six trading days.
- 11/20 CNBC | Nvidia stock plunges 14%, wraps up longest weekly losing streak since 2008 financial crisis

#### Yahooファイナンス
検索語: `NVDA`
- （新しい見出しなし）

### MRVL（Marvell Technology, Inc.、半導体、前日比 -11.7%、1週 -22.0%、時間外 +2.8%）

#### Googleニュース
検索語: `Marvell stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/16 Yahoo Finance | Why Marvell Stock Is Down Today
- 11/17 Trefis | What Sent Marvell Stock Down Over 7%?
- 11/18 Schaeffer's Investment Research | Marvell Technology Stock Slides Despite Brief Nvidia Respite
- 11/20 Investing.com | Why is Marvell Technology stock sliding today?

#### Yahooファイナンス
検索語: `MRVL`
- 11/20 24/7 Wall St. | Data Center AI Chips Could Change the Winners: Broadcom and Marvell
- 11/20 Motley Fool | Marvell Reports Dec. 1. History Says What Its Stock Usually Does Next.
- 11/21 Barchart | Why It’s Time to Buy the Pullback in Broadcom Stock

## 実行メモ（Routine）
- 送信文字数の上限を超えたため（この日は値動きが大きく数値データが長い）、①各銘柄の数値データから「チャート表示期間内の大きな値動き」の節を外し、②送信用のscan.mdから「グループごとの悪いニュースの流れ」の表を外し、③1回の上限を9,200文字に上げて送信した（この記録の元データには残っていない）。ワインスタインは全体の版が空の応答だったため短い版で送り直した。
- SNDKは株価が取得できず、ルール・著者とも未判定。
- 保存はリポジトリのブランチ。時間外データ・時刻はYahoo取得。
