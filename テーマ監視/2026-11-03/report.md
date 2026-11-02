# テーマ監視 2026-11-02

# 判定のまとめ（ルールの判定と著者の判定を分けて表示）

- **ルールの判定**: 採用した売買ルール（スクリプト）が数値で決めたもの。損切りは買値の15%下の逆指値（日中に届けばその場で売れる）。
- **著者の判定**: ノートブックの著者の回答。買いは注文を止める理由があるときだけ【様子見】、保有はルールより早く手じまう理由があるときだけ【売り】。根拠は下の「著者の回答（全文）」。
- 2つが食い違うときに、どちらに従うかはユーザーが決める。

- **テーマ全体の急落（S2・記録だけ）: あり（S2）**（SOXが直近60取引日の最高値から -21.9%）。S2の日の順張りの候補には「S2なら見送る形」と付ける（売買のルールは変えない。記録してから採用を決める。2026-10-14）

## 保有銘柄

| 銘柄 | ルール | 損益 | 時間外 | ルールの判定 | ルールの判定の理由 | 著者の判定 |
|---|---|---|---|---|---|---|
| SNDK | ルール外（ユーザーの判断。この日はどのルールの合図もなし） | -21.6% | +1.3% | **売り** | 終値 1075.08 が損切り価格 1165.61 以下 | 【未判定】（） |
| AMD | ボリンジャーIII | -15.1% | +0.7% | **売り** | 終値 466.84 が損切り価格 467.47 以下 | 【保有継続】（ボリンジャー） |

## 候補の判定（並びは上の「買う順番」の表と同じ）

- 並びは上の「買う順番」の表と同じ（RSの高い順。勝率の高い順ではない）。注文の値段・株数・逆指値は上の表を見る。勝率・1回平均は、そのルールの過去の成績（後知恵なしの監視銘柄・2015年〜の全部の合図）。
- 空き枠: 4（同時保有4銘柄まで。保有2、うちルールの売り2）。著者が【様子見】の候補を見送るかはユーザーが決める。

| 順 | 銘柄 | ルール | 過去の勝率 | 過去の1回平均 | RS | 時間外 | ルールの判定 | 著者の判定 |
|---|---|---|---|---|---|---|---|---|
| 1 | DELL（デル・テクノロジーズ） | 逆張り: 急落の底（担当: コナーズ） | 65% | +2.1% | 99 | +0.5% | 買い（翌日の寄り付き） | 【様子見】（コナーズ） |
| 2 | MU（マイクロン・テクノロジー） | 逆張り: 急落の底（担当: コナーズ） | 65% | +2.1% | 98 | +0.8% | 買い（翌日の寄り付き） | 【買い】（コナーズ） |
| 3 | HPE（ヒューレット・パッカード・エンタープライズ） | 逆張り: 急落の底（担当: コナーズ） | 65% | +2.1% | 97 | +0.5% | 買い（翌日の寄り付き） | 【様子見】（コナーズ） |
| 4 | LITE（ルメンタム・ホールディングス） | 逆張り: 急落の底（担当: コナーズ） | 65% | +2.1% | 96 | +1.4% | 買い（翌日の寄り付き） | 【様子見】（コナーズ） |
| 5（枠外） | PLTR（パランティア・テクノロジーズ） | 逆張り: ボリンジャー メソッドIII | 68% | +1.5% | 61 | -0.5% | 買い（翌日の寄り付き） | 【買い】（ボリンジャー） |
| 6（枠外） | TT（トレイン・テクノロジーズ） | 逆張り: ボリンジャー メソッドIII | 68% | +1.5% | 15 | +0.0% | 買い（翌日の寄り付き） | 【買い】（ボリンジャー） |

- 時間外: 前の取引日の引けから、引け後（米国東部時間16〜20時）の最後の値までの騰落率（Yahoo。±5%以上は太字）。寄り付きの値段は、表の注文の目安（前日の終値で計算）から大きくずれることがある。原因の見出しは「ニュースの見出し」の節。

# 著者の回答（全文）

## 0_テーマの局面_ワインスタイン

1. **テーマ全体の局面**: 【ステージ3】（30週線が横ばいとなり天井圏を形成 [1, 2]、第2章）
2. **グループごとの局面**:
- 半導体｜ステージ3｜30週線横ばい（乖離-6.9%） [1, 2]
- 半導体製造装置・材料・設計ソフト・計測｜ステージ3｜30週線横ばい（乖離-13.2%） [1, 2]
- AIサーバー・ストレージ・メモリ・端末｜ステージ3｜30週線横ばい（乖離-2.4%） [1, 2]
- 光・通信・ネットワーク｜ステージ3｜30週線横ばい（乖離-15.7%） [1, 2]
- データセンターの電力・冷却・部品・受託製造・建設｜ステージ3｜30週線横ばい（乖離-7.1%） [1, 2]
- AIプラットフォーム・クラウド｜ステージ3｜30週線横ばい（乖離-9.9%） [1, 2]
- AIソフト・セキュリティ・ITサービス｜ステージ2｜30週線上昇・株価線の上（乖離+10.6%） [1, 2]
3. **転換の兆し**: 出ている。テーマ指数および6グループで30週線が横ばい化（第2章）[1, 2]、RSがS&P500より弱化し株価が50日線下（-9.2%）へ下落、50日線上銘柄割合も24%へ低下しており、天井（ステージ3）から崩れ（ステージ4）への警戒基準に該当（第3章・第4章・第6章）[3-5]。
4. **テーマの外**: 判定不能（ヒートマップデータ省略のため）

（全体の版が空の応答だったため、1〜2節だけの短い版で送り直した回答。ヒートマップ・急騰急落・ニュースは渡していない）

## 1_コナーズ_prompt_1

## DELL（DELL）
1. **投資判断**: 【様子見】（月初見送り規定）
2. **止める理由の確認**:
   - 本が禁じる形・状況｜あり｜毎月3〜8日は買い見送り（第11章） [1-3]
   - 避けるべき時期（決算など）｜なし｜決算22日後。回避規定はマニュアルに規定なし [4]
   - 悪材料｜なし｜パニック急落は買いのエッジ（第2章、第3章） [5, 6]
3. **現状パターンと価格**:
   - `現状パターン: A（急落・RSI(2)成立）`
   - A: `本日の発注: なし（見送り）`
4. **注意点**: 月初通過後に再判定すること。

## 1_コナーズ_prompt_2

## MU
1. **投資判断**: 【買い】
2. **止める理由の確認**:
   - 本が禁じる形・状況｜なし｜200日線上で条件成立（第4章）[1]。
   - 避けるべき時期（決算など）｜なし｜決算51日後。月初（3〜8日）外（第11章）[2]。
   - 悪材料｜なし｜悪材料・悲観は平均回帰の買いエッジ（第2章・第5章）[3, 4]。
3. **現状パターンと価格**:
   - 現状パターン: A（条件成立）
   - 本日の発注: 翌日の寄り付きで成行
4. **注意点**: 終値で5日線上抜けか15%損切りで手じまい [5]。

## 1_コナーズ_prompt_3

## HPE
1. **投資判断**: 【様子見】（発注日11/3が本が明記する見送り時期「月初」に該当するため） [1, 2]
2. **止める理由の確認**:
   - 本が禁じる形・状況｜なし｜根拠（第3章 [3]、第4章 [4]、第9章 [5]、判定ブック [1, 6]）
   - 避けるべき時期（決算など）｜あり｜根拠（第11章 [2]、判定ブック5節 [1, 6]）
   - 悪材料｜なし｜根拠（第3章 [3]、第8章 [7]、判定ブック [6]）
3. **現状パターンと価格**:
   - 現状パターン: A（200日線上、急落・RSI成立） [1, 5, 8]
   - 本日の発注: 翌日の寄り付きで成行
4. **注意点**: 11/23の決算は問題ないが毎月3〜8日の月初は過去検証で損失傾向のため買いを見送る規定です [2]。

## 1_コナーズ_prompt_4

## LITE
1. **投資判断**: 【様子見】
2. **止める理由の確認**:
   - 本が禁じる形・状況｜あり｜株価684.40が200日線802.88の下側（第4章、ルールブック第2・5節 [1, 2]）
   - 避けるべき時期（決算など）｜あり｜翌日11/3が3〜8日月初見送りに該当（第11章、ルールブック第5節 [3, 4]）。決算回避は規定なし
   - 悪材料｜なし｜急落は買い好機とされ悪材料での停止規定なし（第3・8章 [5, 6]）
3. **現状パターンと価格**:
   - `現状パターン: A（急落底シグナル成立）`
   - `本日の発注: なし（見送りのため発注しない）`
4. **注意点**: 特になし

## 1_ボリンジャー_prompt_1

## AMD
1. **投資判断**: 【保有継続】（本基準での早期手じまい理由なし）
2. **止める理由の確認**:
   - 本が禁じる形・状況｜なし｜早期手じまいを強制する危険形状なし（第12章、第13章）[1, 2]
   - 避けるべき時期（決算など）｜なし｜決算前の手じまい規定なし（マニュアルに規定なし）[3, 4]
   - 悪材料｜なし｜本基準の危険悪材料なし（第23章、11/2ニュース）[5, 6]
3. **現状パターンと価格**:
   - `現状パターン: C（メソッドIII反転後に再下落）`[7, 8]
   - 保有中: `売りの予約注文: なし`
4. **注意点**: 明日11/3の決算発表による急変動に注意してください。[9]

## 1_ボリンジャー_prompt_2

## PLTR
1. **投資判断**: 【買い】
2. **止める理由の確認**:
   - 本が禁じる形・状況｜なし｜メソッドIIIの条件成立（第20章）
   - 避けるべき時期（決算など）｜なし｜決算直前の買い見送り規定なし（マニュアルに規定なし）
   - 悪材料｜なし｜Q3決算好調・上方修正で悪材料なし（11/2）
3. **現状パターンと価格**:
   - 現状パターン: A（メソッドIII成立）
   - 本日の発注: 翌日の寄り付きで成行
4. **注意点**: 決算直後のため寄り付きの乱高下に注意。

## 1_ボリンジャー_prompt_3

## TT
1. **投資判断**: 【買い】
2. **止める理由の確認**:
   - 本が禁じる形・状況｜なし｜第20章（%b<0.05かつ21日II%>0のメソッドIII買い条件成立） [1]
   - 避けるべき時期（決算など）｜なし｜判定用ルールブック第12節（次回決算まで87日。時期制限はマニュアルに規定なし） [2]
   - 悪材料｜なし｜2026-11-02時点（固有の悪材料なし）
3. **現状パターンと価格**:
   - 現状パターン: A（最新足でメソッドIII条件成立） [1]
   - 本日の発注: 翌日の寄り付きで成行
4. **注意点**: 利確目標となる上部バンド（本日 495.95）は毎晩更新すること（第20章） [3]。

💡 他の買い候補銘柄や保有銘柄についても同様の基準でスクリーニング・確認を行いますか？

# スキャン（数値と事実）


- 監視銘柄 87（判定できたのは 86、取得不可: Q）。
- この一覧は数値と事実だけ。売買の判断は著者のノートブックが行う。

## 1. テーマ（グループ）の強さ

| グループ | 銘柄数 | 1週 | 1カ月 | 3カ月 | 3カ月の順位 | 50日線より上の銘柄の割合 | グループ指数の30週線の局面（線との乖離、4週前からの線の傾き） |
|---|---|---|---|---|---|---|---|
| 半導体 | 16 | -5.3% | -13.6% | -6.6% | 3位 | 31% | 横ばい（-6.9%、+6.1%） |
| 半導体製造装置・材料・設計ソフト・計測 | 8 | -3.4% | -22.3% | -12.4% | 6位 | 25% | 横ばい（-13.2%、+2.6%） |
| AIサーバー・ストレージ・メモリ・端末 | 9 | -12.8% | -26.2% | -3.9% | 2位 | 11% | 横ばい（-2.4%、+8.6%） |
| 光・通信・ネットワーク | 9 | -9.7% | -25.0% | -21.3% | 7位 | 11% | 横ばい（-15.7%、+2.7%） |
| データセンターの電力・冷却・部品・受託製造・建設 | 19 | +1.1% | -6.2% | -10.3% | 4位 | 16% | 横ばい（-7.1%、+1.0%） |
| AIプラットフォーム・クラウド | 11 | -5.4% | -14.7% | -11.5% | 5位 | 18% | 横ばい（-9.9%、+1.8%） |
| AIソフト・セキュリティ・ITサービス | 14 | -7.6% | +3.2% | +8.7% | 1位 | 50% | 上昇（+10.6%、+5.2%） |

## 2. テーマ全体の状態と早めの警告

- 市場全体の30週線による局面: S&P500指数 **上昇**／NASDAQ100指数 **横ばい**（急落の底で買うルールは、過去の検証で下落相場で特に強く、横ばいの相場では負けていた）
- **2倍ETFを使う局面（案1、2026-10-13 採用）: S&P500の20週線（100日線）で 横ばい** → 新しく買う銘柄は、2倍ETFのある銘柄も元の株で買う（保有中のETFはそのまま）（SPY 752.10、100日線 758.12、20日前の線 752.63。上昇＝線より上かつ線が上向き）
- **テーマ全体の急落（S2、記録だけ。売買のルールは変えない）: あり（S2）**（SOX 10328.33、直近60取引日の最高値 13217.82 から -21.9%。S2＝最高値から−10%以上）。S2のときに「順張りの新しい買いだけ止める」形を記録で比べる（2026-10-14 ユーザー決定。バックテストでは年率は上がったが2つの期間ではどちらも少し下回ったため、記録してから採用を決める。`バックテスト結果/テーマ全体の急落を検知して手じまう・買いを止める.md`）
- テーマ指数（監視銘柄の等金額平均）の30週線による局面: **横ばい**（上昇＝線より上かつ上向き、下落＝線より下かつ下向き、それ以外＝横ばい。ワインスタインのステージの近似）
- テーマ指数と50日線: 50日線より下（乖離 -9.2%）
- S&P500に対する相対的な強さ: 50日平均より下（S&P500より弱い）
- 監視銘柄のうち50日線より上の割合: 24%
- 警告（割合が40%未満かつテーマ指数が50日線より下）: **出ている**
- 参考（バックテスト）: 30週線の「下落」は高値から10〜33%下げた後に出る遅い判定。50日線・割合・相対的な強さは高値から2〜8%で出るが、誤報が年15回以上ある。警告中に新しい買いを止めると、押し目買い（ボリンジャーIII）の成績は大きく下がった（`バックテスト結果/テーマ監視銘柄・直近3年.md` 11・12節）。

## 3. ヒートマップ（Finviz、全米の業種別の騰落率）

3カ月の騰落率の上位15業種（テーマの外で強くなっている業種の確認用）:

| 順位 | 業種 | 1週 | 1カ月 | 3カ月 | 6カ月 | 1年 |
|---|---|---|---|---|---|---|
| 1 | Health Information Services | +1.6% | +10.7% | +31.9% | +50.9% | +6.2% |
| 2 | Oil & Gas Refining & Marketing | -8.3% | -1.5% | +26.3% | +51.1% | +101.0% |
| 3 | Diagnostics & Research | -0.9% | +4.6% | +18.4% | +46.6% | +26.2% |
| 4 | Lodging | +4.6% | +14.0% | +16.3% | +16.7% | +43.5% |
| 5 | Auto Manufacturers | +3.3% | +8.4% | +15.7% | +3.0% | -8.1% |
| 6 | Drug Manufacturers - General | +5.4% | +13.5% | +15.3% | +26.1% | +39.4% |
| 7 | Oil & Gas Integrated | -3.0% | +7.6% | +14.6% | +11.4% | +54.5% |
| 8 | Medical Distribution | +1.2% | +10.1% | +13.5% | +21.0% | +17.1% |
| 9 | Oil & Gas Drilling | -4.6% | +10.8% | +13.2% | -14.1% | +44.9% |
| 10 | Discount Stores | +5.4% | +18.2% | +12.4% | +1.4% | +23.0% |
| 11 | Financial Data & Stock Exchanges | +3.0% | +15.9% | +12.4% | +9.3% | +4.5% |
| 12 | Oil & Gas E&P | -3.8% | +9.3% | +11.8% | +3.2% | +46.7% |
| 13 | Textile Manufacturing | +15.2% | +17.3% | +11.3% | +26.8% | +19.1% |
| 14 | Insurance - Reinsurance | +1.7% | +9.0% | +11.0% | +20.2% | +38.8% |
| 15 | Real Estate - Diversified | +1.8% | +8.8% | +10.8% | +12.1% | +12.4% |

テーマの業種の順位（3カ月、全144業種中）: Semiconductors 110位、Semiconductor Equipment & Materials 139位、Computer Hardware 140位、Communication Equipment 127位、Electronic Components 131位、Software - Infrastructure 57位、Software - Application 32位、Internet Content & Information 133位

## 4. 急騰・急落した銘柄（前日比±5%以上、または出来高が50日平均の2倍以上）

原因のニュースをサブエージェントが調べ、候補・保有銘柄の判定材料として著者に渡す。急騰・急落そのものは売買の合図にしない（後知恵のないS&P500全体のバックテストでは、急騰の翌日に買うルールは年率7%、急落の翌日に買うルールは年率9〜10%で、採用した3つのルールより優れていなかった）。

| 銘柄 | グループ | 前日比 | 出来高（50日平均の倍） | 終値 | 50日線 | RS | 局面 |
|---|---|---|---|---|---|---|---|
| LITE | 光・通信・ネットワーク | -18.6% | 3.2倍 | 684.40 | 下 | 96 | レンジ |
| MRVL | 半導体 | -12.7% | 2.9倍 | 171.41 | 下 | 94 | レンジ |
| CIEN | 光・通信・ネットワーク | -11.3% | 1.6倍 | 284.34 | 下 | 15 | レンジ |
| ALAB | 半導体 | -11.2% | 1.4倍 | 229.67 | 下 | 48 | レンジ |
| INTC | 半導体 | -8.8% | 2.1倍 | 59.97 | 下 | 16 | レンジ |
| ORCL | AIプラットフォーム・クラウド | -8.8% | 1.9倍 | 119.22 | 下 | 2 | レンジ |
| CRWV | AIプラットフォーム・クラウド | -8.6% | 1.2倍 | 50.15 | 下 | 0 | レンジ |
| NBIS | AIプラットフォーム・クラウド | -8.3% | 1.1倍 | 141.39 | 下 | 23 | レンジ |
| DDOG | AIソフト・セキュリティ・ITサービス | -8.1% | 1.4倍 | 216.10 | 下 | 82 | レンジ |
| STX | AIサーバー・ストレージ・メモリ・端末 | -7.9% | 1.2倍 | 593.76 | 下 | 75 | レンジ |
| SMCI | AIサーバー・ストレージ・メモリ・端末 | -7.6% | 1.1倍 | 30.44 | 下 | 18 | レンジ |
| AMD | 半導体 | -7.5% | 1.6倍 | 466.84 | 下 | 95 | レンジ |
| WDC | AIサーバー・ストレージ・メモリ・端末 | -7.5% | 0.9倍 | 338.59 | 下 | 71 | レンジ |
| DELL | AIサーバー・ストレージ・メモリ・端末 | -7.4% | 0.8倍 | 392.78 | 下 | 99 | レンジ |
| FTNT | AIソフト・セキュリティ・ITサービス | -7.3% | 2.6倍 | 126.21 | 下 | 79 | レンジ |
| HPE | AIサーバー・ストレージ・メモリ・端末 | -7.1% | 0.8倍 | 51.19 | 下 | 97 | レンジ |
| NTAP | AIサーバー・ストレージ・メモリ・端末 | -7.0% | 1.0倍 | 185.26 | 下 | 96 | レンジ |
| SNDK | AIサーバー・ストレージ・メモリ・端末 | -6.6% | 1.1倍 | 1075.08 | 下 | 99 | レンジ |
| AKAM | 光・通信・ネットワーク | -6.5% | 0.9倍 | 86.69 | 下 | 9 | レンジ |
| MU | 半導体 | -5.8% | 1.1倍 | 833.59 | 下 | 98 | レンジ |
| FFIV | 光・通信・ネットワーク | -4.1% | 2.4倍 | 324.55 | 下 | 33 | レンジ |
| RDDT | AIソフト・セキュリティ・ITサービス | -0.8% | 2.2倍 | 90.97 | 下 | 1 | レンジ |

- 局面: 終値 > 50日線 > 200日線、50日線が20取引日前より2%以上高い、ADX(14) ≧ 20 をすべて満たせば上昇相場、それ以外はレンジ（判定式はClaudeが置いたもの）。

## 4-2. 監視外の注目銘柄（S&P500・NASDAQ100のうち監視銘柄に入っていない銘柄）

条件: 流動性（株価5ドル以上・50日平均出来高25万株以上）があり、(a) 前日比+8%以上かつ出来高が50日平均の2倍以上、または (b) 終値が直前1年の最高値（終値）を上回り、RS≧90。RSの高い順に5銘柄（ニュースを調べる）。監視銘柄に入れるかはユーザーが決める。

| 銘柄 | 種類 | 前日比 | 出来高（50日平均の倍） | RS | 終値 |
|---|---|---|---|---|---|
| FDS | 1年の高値更新 | +4.3% | 1.1倍 | 94 | 343.74 |
| NUE | 1年の高値更新 | +1.4% | 1.4倍 | 93 | 277.65 |
| REGN | 1年の高値更新 | +3.6% | 2.3倍 | 93 | 961.26 |
| IFF | 1年の高値更新 | +1.7% | 1.8倍 | 92 | 94.63 |
| EXPD | 1年の高値更新 | +0.9% | 1.8倍 | 92 | 200.56 |

- ほかに3銘柄: SWK（1年の高値更新、RS 92）、MAR（1年の高値更新、RS 91）、IDXX（急騰、RS 64）

## 5. 保有銘柄の手じまい条件（`新分析ツール/保有銘柄.md`）

| 銘柄 | ルール | 買った日 | 買値 | 終値 | 損益 | 損切り価格（買値の15%下、逆指値） | ルールの手じまい条件 | 出来高2倍の大陰線（買った後の直近5日） | 次回決算予定日 |
|---|---|---|---|---|---|---|---|---|---|
| SNDK | ルール外（ユーザーの判断。この日はどのルールの合図もなし） | 2026-10-21 | 1371.30 | 1075.08 | -21.6% | 1165.61 | **損切り価格を下回った** ルールが不明（保有銘柄.md の「ルール」を確認） | なし | 2026-10-29 |
| AMD | ボリンジャーIII | 2026-10-21 | 549.97 | 466.84 | -15.1% | 467.47 | **損切り価格を下回った** 売りの指値: 上部バンド 656.32（今夜この値に置き直す。届いた日に売れる）（2倍ETF AMUU で持っている場合も、判定は元の株 AMD の値段） | なし | 2026-11-03 |

- 出来高2倍の大陰線: 実体（始値−終値）が前日までのATR(14)の1.5倍以上、終値がその日の値幅の下25%以内、出来高が前日までの50日平均の2倍以上の日。**押し目（ボリンジャーIII）・急落の底の保有では売りのルール**: 出たら翌日の寄り付きで全部売り、空いた枠で次の合図を買う（2026-10-02 ユーザー決定。`バックテスト結果/やり直し_売りの合図の組み合わせ.md`。乱数3組とも年率が約+2ポイント、最大下落率もやや下がった）。ミネルヴィニ・新高値V2の保有では事実の表示（順張りに足しても良くならなかった）。

- 半分売りの合図（ミネルヴィニ・新高値V2の保有だけ）: 反転のローソク足（かぶせ線・弱気の包み足・宵の明星・流れ星）＋出来高が50日平均の1.5倍以上＋RSI(14)が前日か当日に70以上。買った後に最初に出た日の翌日の寄り付きで半分売り、残り半分は50日線割れ・損切り15%まで持つ（2026-10-01 ユーザー決定。`バックテスト結果/半分だけ売るとオニールの空き枠.md`）。

- かぶせ線（ミネルヴィニ・新高値V2の保有だけ）: 上昇中の陽線の翌日に、前日の高値より上で寄り付き、前日の陽線の真ん中より下（前日の始値より上）で引けた日。翌日の寄り付きで全部売り、空いた枠で次の合図を買う。半分売りより優先する（2026-10-01 ユーザー決定。`バックテスト結果/2倍ETFで売って買い直す.md`。順張りの売買の25%で出て、1回平均+2.0%、年率 21.4%→26.4%）。

## 5-2. 前日（2026-10-30の引け）の【買い（予約）】の確認

前日の【買い（予約）】はなし。

## 6. 候補（採用したルールの条件が成立＝A。予約（B）は2026-10-25から注文せず、節6-3に参考の表示だけ）

建玉の目安: 同時保有4銘柄まで、1銘柄に資金の25%（資金÷4）、損切りは買値の15%下（ユーザー決定 2026-09-29）。

保有中のため候補から外した銘柄（合図は出ている）: AMD、SNDK

パターン: A＝最新の足で採用ルールの条件が成立（翌日の寄り付きで成行）。条件の成立が目前の銘柄（B）は、予約の注文をやめたので節6-3に参考として出す（2026-10-25 ユーザー決定）。

| 銘柄 | グループ | パターン | 種類 | ルールの過去の成績 | 終値 | 前日比 | RS | 50日線の傾き | 局面 | 当てはまった条件 | 次回決算予定日 | 注文の目安 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DELL | AIサーバー・ストレージ・メモリ・端末 | A | 逆張り: 急落の底（担当: コナーズ） | 2位（勝率65%・1回平均+2.1%） | 392.78 | -7.4% | 99 | +4.4% | レンジ | 直前5日の最高値（終値）から-21.8%下落（−15%以上）、RSI(2)=4.1（≦10）、急落の前は50日線＞200日線。市場全体の局面: S&P500 上昇／NASDAQ100 横ばい | 2026-11-24（22日後） | 翌日の寄り付きで買い。損切り: 買値の15%下。手じまい: 終値が5日線（今日 457.67）を上回った翌日の寄り付き（コナーズ）。**元の株で買う**（2倍ETF DLLL のある銘柄だが、S&P500が20週線で「横ばい」の局面のため。案1）。**株数の目安: 6株**（2,384ドル÷392.78。今日の終値。寄り付きの値段で変わる）、購入金額 約2,357ドル |
| MU | 半導体 | A | 逆張り: 急落の底（担当: コナーズ） | 2位（勝率65%・1回平均+2.1%） | 833.59 | -5.8% | 98 | +1.8% | レンジ | 直前5日の最高値（終値）から-15.2%下落（−15%以上）、RSI(2)=9.8（≦10）、急落の前は50日線＞200日線。市場全体の局面: S&P500 上昇／NASDAQ100 横ばい | 2026-12-23（51日後） | 翌日の寄り付きで買い。損切り: 買値の15%下。手じまい: 終値が5日線（今日 912.92）を上回った翌日の寄り付き（コナーズ）。**元の株で買う**（2倍ETF MUU のある銘柄だが、S&P500が20週線で「横ばい」の局面のため。案1）。**株数の目安: 2株**（2,384ドル÷833.59。今日の終値。寄り付きの値段で変わる）、購入金額 約1,667ドル |
| HPE | AIサーバー・ストレージ・メモリ・端末 | A | 逆張り: 急落の底（担当: コナーズ） | 2位（勝率65%・1回平均+2.1%） | 51.19 | -7.1% | 97 | +6.4% | レンジ | 直前5日の最高値（終値）から-15.9%下落（−15%以上）、RSI(2)=3.5（≦10）、急落の前は50日線＞200日線。市場全体の局面: S&P500 上昇／NASDAQ100 横ばい | 2026-11-23（21日後） | 翌日の寄り付きで買い。損切り: 買値の15%下。手じまい: 終値が5日線（今日 57.26）を上回った翌日の寄り付き（コナーズ）。**株数の目安: 46株**（2,384ドル÷51.19。今日の終値。寄り付きの値段で変わる）、購入金額 約2,355ドル |
| LITE | 光・通信・ネットワーク | A | 逆張り: 急落の底（担当: コナーズ） | 2位（勝率65%・1回平均+2.1%） | 684.40 | -18.6% | 96 | +3.8% | レンジ | 直前5日の最高値（終値）から-25.6%下落（−15%以上）、RSI(2)=6.0（≦10）、急落の前は50日線＞200日線。市場全体の局面: S&P500 上昇／NASDAQ100 横ばい | 2026-11-02（0日後）**決算が近い** | 翌日の寄り付きで買い。損切り: 買値の15%下。手じまい: 終値が5日線（今日 844.95）を上回った翌日の寄り付き（コナーズ）。**元の株で買う**（2倍ETF LITX のある銘柄だが、S&P500が20週線で「横ばい」の局面のため。案1）。**株数の目安: 3株**（2,384ドル÷684.40。今日の終値。寄り付きの値段で変わる）、購入金額 約2,053ドル |
| PLTR | AIプラットフォーム・クラウド | A | 逆張り: ボリンジャー メソッドIII | 3位（勝率68%・1回平均+1.5%） | 178.34 | -3.1% | 61 | +9.2% | レンジ | %b=-0.098（<0.05）、21日II%=+0.013（>0） | 2026-11-02（0日後）**決算が近い** | 翌日の寄り付きで買い。損切り: 買値の15%下。手じまい: 買った日の夜から、売りの指値をその日の上部バンド（今日 212.05）に置き、毎晩その日の値に置き直す。**元の株で買う**（2倍ETF PLTU のある銘柄だが、S&P500が20週線で「横ばい」の局面のため。案1）。**株数の目安: 13株**（2,384ドル÷178.34。今日の終値。寄り付きの値段で変わる）、購入金額 約2,318ドル |
| TT | データセンターの電力・冷却・部品・受託製造・建設 | A | 逆張り: ボリンジャー メソッドIII | 3位（勝率68%・1回平均+1.5%） | 413.33 | +0.8% | 15 | -0.9% | レンジ | %b=-0.066（<0.05）、21日II%=+0.037（>0） | 2027-01-28（87日後） | 翌日の寄り付きで買い。損切り: 買値の15%下。手じまい: 買った日の夜から、売りの指値をその日の上部バンド（今日 495.95）に置き、毎晩その日の値に置き直す。**株数の目安: 5株**（2,384ドル÷413.33。今日の終値。寄り付きの値段で変わる）、購入金額 約2,067ドル |

- 2倍ETF: 2倍ETFがある銘柄（ユーザーがムームー証券で買えることを確認した38銘柄のうち、目減りが年15%未満のもの）は、株の代わりに2倍ETFを買う（2026-10-04 ユーザー決定。`バックテスト結果/2倍ETFを使う決まり.md`。年率 約27%→約33%、確定した損益だけの最大下落率 約30%→約31%、含み損込みは約33%→約45%）。買う金額は株と同じ（資金の25%）。合図・損切り（元の株の買値の15%下＝ETFでは約30%下）・手じまいはすべて元の株の値段で判定する。指値・逆指値はETFの値段に直して置く。どのETFかは `新分析ツール/2倍ETFの対応表.json`（売買代金が1日500万ドル以上で、直近1年の目減りが一番小さいもの）。**2倍ETFで買うのは、S&P500が20週線（100日線）で「上昇」の局面のときだけ。横ばい・下落の局面では元の株で買う**（案1、2026-10-13 ユーザー採用。買う日に決め、買った後は局面が変わってもそのまま持つ。`バックテスト結果/流れ（市場の局面）を使う形.md`）。

- ルールの過去の成績: 今の売りのルールで、後知恵なしの監視銘柄・2015年〜の全部の合図の1回ごとの成績（2026-10-02計算、`新分析ツール/バックテスト結果/ルールごとの成績.md`）。順位は1回平均（1回の売買で平均いくら増えるか）の順。表はパターン（A→B）ごとに、この順位の良い順に並べた（表示の順番だけ。買う順番・件数の上限は変えていない。候補の選び方を変えても成績は変わらなかったため。2026-10-02 ユーザーの指示）。著者には渡さない。

- パターンBは各ルールでRSの高い順に2件まで、急落の底・新高値のAは4件（同時保有の上限）までとし、13件を省いた。

- 候補の数: 空き枠4（同時保有4銘柄まで。保有2、うち今日ルールの売りが成立2）＋予備2件まで表に出した（2026-10-25 ユーザー決定）。省いた候補はない。

- テーマの外の候補（グループが「テーマの外」）: 監視銘柄の候補で枠が埋まらないときに使う（監視銘柄の候補を先に買う）。S&P500の今の構成銘柄のうち監視銘柄でない銘柄から、RS≧90・30週線が上向きで終値がその上・業種の3カ月の強さが上位20%の17銘柄を調べ、空き枠2つ分まで出した。バックテストでは、テーマの外の強い銘柄で空き枠を埋めると、テーマが弱い時期の成績が支えられた（`バックテスト結果/半導体・AIに特化した場合.md`。2026-10-01 ユーザー決定）。

- RS≧80の押し目（ボリンジャーIII）は、バックテストで成績がより安定していた（PF3.27、最大下落20%）。

## 6-3. 参考: 条件の成立が目前の銘柄（予約は注文しない・著者には送らない）

2026-10-25 ユーザー決定: 予約（逆指値・指値）の注文はやめ、参考の表示だけにする。毎朝のツールと同じ条件・値段で予約の約定をバックテストに入れると、どの形も年率が下がった（後知恵なし 35.7%→30.7〜34.2%、87銘柄 45.6%→34.2〜42.6%。`バックテスト結果/点検_2026-10-25/`）。引けで条件がそろえば、翌朝の節6に買いの候補（A）として出る。各ルールでRSの高い順に2件まで。

| 参考の銘柄 | グループ | 種類 | 終値 | 前日比 | RS | 当てはまった条件 | 条件がそろう目安の価格（注文はしない） |
|---|---|---|---|---|---|---|---|
| WDC | AIサーバー・ストレージ・メモリ・端末 | ボリンジャー メソッドIII（%bが0.05未満に近い） | 338.59 | -7.5% | 71 | %b=0.122（0.05まであと少し）、21日II%=+0.047（>0） | 332.10（この値より下で引けると翌朝の買いの候補（A）。目安） |
| CRM | AIソフト・セキュリティ・ITサービス | ボリンジャー メソッドIII（%bが0.05未満に近い） | 226.18 | -1.3% | 62 | %b=0.161（0.05まであと少し）、21日II%=+0.042（>0） | 222.55（この値より下で引けると翌朝の買いの候補（A）。目安） |


# ニュース（サブエージェントの調査）

# ニュース調査（2026-11-02引け時点）
出典は headlines.md の見出し優先、数字の確認のみWebSearch。判断は書かない。

## テーマ全体の下げの原因
- きっかけ（10/29〜30）: Intel決算。Q4 EPS見通し25セント（予想43）、売上150〜160億ドル（予想170.5億）、PC向け前期比20%超減、メモリ不足でPC市場は今年−12%・来年−10%。10/30に約−26%（1974年以来最悪、kucoin）。「インテル・ショック」（トウシル・朝鮮日報 11/2）。
- 同日: Kioxiaの慎重な見通しでメモリ・ストレージ下落（24/7 Wall St. 10/30、11/2）。
- 広がった先: AMD（MarketWatch 10/30）、DELL・HPQ・HPE・SMCI（24/7 Wall St. 10/30）、F5（決算後−20%、Barron's 10/28）。
- 11/2: Marvell×Lumentum確定（全株式交換、1株=4.5株、企業価値約1150億ドル、プレミアム約23.9%、SEC 8-K）。MRVL・LITE・光系が下落（Yahoo Finance・IBD 11/2）。
- 信用: CoreWeave過去最安値圏（BigGo 11/2）、2032年債利回り約15%・CDS 1,000bp超（10月の報道）。Oracle追加100億ドル借入で下落（Yahoo Finance 11/2見出し、詳細は取得不可）。
- 市場全体: S&P500下落、ダウ+213ドル（Reuters・47NEWS 11/2）。VIX・ハイイールド債は取得不可。Appleは引け後決算。

## 引け後・時間外の材料
- PLTR: 時間外 −0.5%。Q3売上23.13億ドル（+96%）、調整後EPS 0.44ドル、通期見通し引き上げ（SEC 8-K、Investing.com 11/2）。
- ON: 時間外 −3.0%。原因の見出しは見つからなかった。
- LITE +1.4%、SNDK +1.3%、MU +0.8%、AMD +0.7%、HPE +0.5%、DELL +0.5%、TT 0.0%: ±5%未満、原因の見出しは見つからなかった。

## SNDK（保有）
- 10/30 決算はQ1予想超え・ガイダンス上方・8対1分割だが−9%（Yahoo Finance、24/7 Wall St.）。Kioxiaが慎重な見通し（Yahoo Finance 10/30）。11/2 Micron −4%、SNDK −3%（24/7 Wall St.）。
- 悪材料: あり（Kioxia見通し、決算の質への疑問 TradingPedia 10/30）

## AMD（保有）
- 10/30 −13%、Intel決算で2つの問題（MarketWatch、Seeking Alpha）。11/2 半導体が戻りを失う（Barron's）。次回決算 11/3。
- 悪材料: 確認できず（会社固有）

## DELL（候補）
- 10/30 −11%（Intelの警告、24/7 Wall St.）。11/2 1か月で約−20%（24/7 Wall St.）。
- 悪材料: 確認できず

## MU（候補）
- 10/28 SK Hynix好決算（Yahoo）、10/29 Samsung後の売り波及（Yahoo）、10/30 Barron's、11/2 12月に大規模自社株買い見込み（Barron's）。
- 悪材料: 確認できず

## HPE（候補）
- 10/27 Dell・HPEが1日で大幅安（Barchart）、10/30 Intel決算波及（Barron's）。固有ニュースは見つからなかった。
- 悪材料: 確認できず

## LITE（候補）
- 10/28 買収協議報道（IBD 10/29）。11/2 正式発表、LITE −14.9%（Yahoo Finance）。固定比率のためMRVL株価に連動。次回決算は11/2（scan.md）だが内容は取得不可。
- 悪材料: あり（買収の規制審査などの詳細は取得不可）

## PLTR（候補）
- 10/28 RBCが警告（Yahoo）、11/2 引け後決算は売上予想超えだが超過幅は小さい（IBD）。
- 悪材料: 確認できず

## TT（候補）
- 10/29 7か月ぶり安値・マージン縮小（TradingView）、10/30 受注の伸びの鈍化（Oppenheimer、MT Newswires）。
- 悪材料: あり（受注の鈍化）

## 急落した監視銘柄・監視外
- MRVL −12.7%: 買収発表、希薄化懸念（TIKR、technews）。CIEN −11.3%: 原因の見出しは見つからなかった。ALAB・STX・SMCI・WDC・NTAP・FTNT・DDOG: 個別原因は取得不可（NTAPは10/30格下げ、Quiver）。INTC: 決算後の下げが続く（Yahoo 11/2）。
- 監視外（FDS・NUE・REGN・IFF・EXPD）: 取得不可（調べていない）。

# ニュースの見出し（プログラムが自動で取得）

- Googleニュース（日付を指定）とYahooファイナンスの見出しを `tools/news_headlines.py` が自動で並べたもの。日付は米国東部時間の配信日（引け後の記事は翌日付）。原因の判断・売買の判断はしていない。
- 調べた銘柄の選び方: ①保有 ②今日の候補 ③時間外に±5%以上動いた監視銘柄 は全部、④引けまでに大きく動いた銘柄（1週で±5%のグループの上位3・1日で±7%）は合計12銘柄まで。
- 1週で−5%以下のグループ: AIサーバー・ストレージ・メモリ・端末（-12.8%）、光・通信・ネットワーク（-9.7%）、AIソフト・セキュリティ・ITサービス（-7.6%）、AIプラットフォーム・クラウド（-5.4%）、半導体（-5.3%）
- 1週で+5%以上のグループ: なし

## 0. 時間外（引け後）の値動き（2026-11-02 の引けから、Yahoo。±3%以上の監視銘柄と、保有・候補は全部）

| 銘柄 | 区分 | 引け | 時間外 | 騰落率 |
|---|---|---|---|---|
| ON | 監視 | 70.13 | 67.99（17:19 ET） | -3.0% |
| LITE | 候補 | 684.22 | 693.59（17:19 ET） | +1.4% |
| SNDK | 保有 | 1075.00 | 1088.51（17:19 ET） | +1.3% |
| MU | 候補 | 833.06 | 839.95（17:19 ET） | +0.8% |
| AMD | 保有 | 466.70 | 470.00（17:19 ET） | +0.7% |
| PLTR | 候補 | 178.62 | 177.66（17:19 ET） | -0.5% |
| HPE | 候補 | 51.19 | 51.45（17:16 ET） | +0.5% |
| DELL | 候補 | 392.66 | 394.54（17:09 ET） | +0.5% |
| TT | 候補 | 413.27 | 413.33（16:30 ET） | +0.0% |

## 1. 市場全体（2026-11-02）

### 市場全体（英語のまとめ記事）
検索語: `stocks Wall Street close Nasdaq`
- 11/2 Investor's Business Daily | Stock Market Today: Stock Market News And Analysis
- 11/2 STL.News | Stock Market Today: Monday, November 2, 2026
- 11/2 USA Today | Do stocks rise or fall after elections? Here's what history says
- 11/2 Benzinga | Stock Market Today: Dow Jones, S&P 500, Nasdaq 100 Futures Rise Ahead of Apple, Palantir Earnings; RYAAY
- 11/2 Arab News | Closing Bell: Saudi stock market advances 0.45% to close at 9,883

### 市場全体（Stock Market Today）
検索語: `"stock market today"`
- 11/2 Kiplinger | Dow Rises Amid More Selling for AI Stocks: Stock Market Today
- 11/2 The Motley Fool | Stock Market Today, Nov. 2: Amazon Rallies on Phillip Securities Buy Upgrade and $330 Target
- 11/2 Yahoo Finance | US Stock Market Today: S&P 500 Futures Edge Higher On ISM Manufacturing Test

### 市場全体（日本語のまとめ記事）
検索語: `米国株式市場 OR NY株`
- 11/2 Reuters | 米国株式市場＝Ｓ＆Ｐ下落、四半期決算発表控えアップル軟調
- 11/2 Yahoo!ニュース | 米国株式市場＝Ｓ＆Ｐ下落、四半期決算発表控えアップル軟調（ロイター）
- 11/2 沖縄タイムス社 | ＮＹ株３日ぶり反発、２１３ドル高
- 11/2 47NEWS | 【速報】NY株3日ぶり反発、213ドル高

### 半導体・AI株（英語）
検索語: `chip stocks OR semiconductor stocks OR AI stocks`
- 11/2 MarketWatch | Chip stocks are suffering from a ‘crisis of confidence’ — but things aren’t as gloomy as they seem
- 11/2 Yahoo Finance | The Intel stock collapse is getting worse — and the $3.5 trillion chip rout is spreading
- 11/2 Investor's Business Daily | Analog Chip Stocks Buoy Philadelphia Semiconductor Index
- 11/2 Reuters | S&P 500 ends down; Apple dips ahead of quarterly report

### 信用（社債・借金）
検索語: `AI debt OR bonds OR credit spreads OR CDS`
- 11/2 Bloomberg.com | Alphabet Is Paying Up for Euro Bonds in Test of AI Appetite
- 11/2 Yahoo Finance | Oracle stock slides as it borrows another $10 billion for AI spending
- 11/2 ThinkAdvisor | Bob Doll: Growing Risk of AI Bust
- 11/2 BigGo Finance | CoreWeave Stock Sinks to Record Low as AI Debt Fears Mount
- 11/2 Beinsure | Oracle (NYSE: ORCL) stock price forecast: $20 bn AI financing raises debt and dilution risks

### 「〇〇ショック」の呼び名（日本語）
検索語: `ショック 株`
- 11/2 トウシル | インテル＆アルファベット・ショックでAI株急落。外食株へ資金シフトし前週比15.9%高も！米中間選挙後、米国株は反転上昇に向かうのか
- 11/2 トウシル | 富士通ショック、サイバーセキュリティ株が総崩れの中、31.7%高の化学株など好業績割安株が躍進！米国中間選挙で激変する今週の注目テーマ
- 11/2 조선일보 | 懸念された「インテル・ショック」はなし、韓国総合株価指数2％台反発
- 11/2 YouTube | 【米国株】Intelショック、AIバブル崩壊なのか？グーグル・アマゾン・インテル決算を深掘り｜週間注目スケジュール 11/2〜11/6
- 11/2 みんかぶ FX/為替 | 【通貨別まとめと見通し】メキシコペソ円：米ハイテク株安と日銀タカ派会見で8.30円まで急落も、ダブルボトムを形成し8.41円台へ反発

### 引け後・時間外の動き（英語）
検索語: `"after hours" OR "after the bell" OR "extended trading" stocks`
- 11/2 CNBC | Stocks making the biggest moves after hours: Fabrinet, Clorox, Apple, Palantir & more
- 11/2 Bloomberg.com | Match Falls After Quarterly Sales, Profit Outlook Miss Estimates
- 11/2 Seeking Alpha | Stocks to watch on Monday after hours: AAPL, PLTR, ON (AAPL:NASDAQ)
- 11/2 CNBC | Apple reports after the bell. Options traders expect a big move
- 11/2 Benzinga | Bloom Energy Stock Jumps After the Bell: Here's Why
- 11/2 AskTraders.com | Apple Beats Forecasts, Stock Dips After Hours
- 11/2 marketscreener.com | Waystar Q3 Adjusted Earnings, Revenue Rise; Shares Fall After Hours
- 11/2 Stock Titan | Tech Stocks Pull the Nasdaq Lower in the Stock Market Today, November 2, as Oil Tumbles

### 引け後・時間外の動き（日本語）
検索語: `時間外 決算 株`
- 11/2 Yahoo!ファイナンス | アップル、決算受け時間外で売買交錯＝米国株個別速報(株探ニュース)
- 11/2 Investing.com - FX | 株式市場 | ファイナンス | 金融ニュース | Palantirの株価が時間外取引で上昇、第3四半期決算が市場予想を大幅に上回る 執筆
- 11/2 株探 | 修正：ダウ先物が反発 原油下落のほかＩＴ・ハイテク株も買い戻し＝米国株
- 11/2 Yahoo!ファイナンス | チェックポイント、決算受け時間外で６％安＝米国株個別(株探ニュース)
- 11/2 BigGo ファイナンス | ロク、Q3決算は市場予想超え 広告収入23%増、1株160ドルのフォックスによる買収が迫る
- 11/2 Yahoo!ファイナンス | アップル、決算を受け時間外で売買交錯 売上高の伸び鈍化 中国が予想下回る＝米国株個別(株探ニュース)
- 11/2 Moomoo | ハーフタイム点検：堅調な決算、半導体株の15%急落、そしてポジションサイジングの重要性を痛感させた高価な教訓
- 11/2 Yahoo!ファイナンス | コスモス・エナジー、決算受け時間外で８％安＝米国株個別(株探ニュース)

### 買収・合併（英語）
検索語: `acquisition OR acquire OR merger OR takeover chip OR semiconductor OR AI OR optical`
- 11/2 The New York Times | Driven by A.I. Boom, Chipmakers Announce $115 Billion Merger
- 11/2 SiliconANGLE | Marvell to acquire optical component maker Lumentum in massive $115B deal
- 11/2 Yahoo Finance | Marvell to purchase Lumentum for $115 billion in record-breaking AI tech deal, both stocks tank
- 11/2 TechCrunch | Omen AI adds liquid know-how in $16 million Aquatic Labs acquisition
- 11/2 NetApp | NetApp Completes Acquisition of PEAK:AIO to Accelerate Zettabyte-scale AI Deployments
- 11/2 Bloomberg.com | Marvell to Acquire Lumentum in Historic $115 Billion Tech Deal
- 11/2 National Mortgage Professional | Dark Matter Expands AI Ambitions With House Numbers Acquisition
- 11/2 Axios | Alphabet in talks to acquire assistant startup Howie AI

## 2. 保有・候補・時間外で大きく動いた銘柄（2026-10-27〜2026-11-02 の見出し）

### SNDK（Sandisk Corporation、保有、AIサーバー・ストレージ・メモリ・端末、前日比 -6.6%、1週 -14.4%、時間外 +1.3%）

#### Googleニュース
検索語: `Sandisk stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 10/30 Yahoo Finance | Sandisk tops Q1 estimates and guides higher, sets 8-for-1 stock split
- 10/30 24/7 Wall St. | Sandisk Sinks 9% Despite Earnings Beat, Raised Guidance and 8-for-1 Split; Western Digital Tumbles 8%, Seagate Slides 7%, Micron Falls 6%
- 10/30 TradingPedia | SanDisk Stock Falls as Investors Question Earnings Quality
- 10/30 Yahoo Finance | SanDisk stock tumbles as Kioxia warns on NAND price surge

#### Yahooファイナンス
検索語: `SNDK`
- 11/2 24/7 Wall St. | Micron Falls 4% as Kioxia’s Cautious Outlook Hits Memory Stocks; Western Digital Drops 5%, SanDisk Slides 3%
- 11/2 24/7 Wall St. | SanDisk Is Back in the Spotlight. Here’s Where I See SNDK Stock Heading Next
- 11/2 Barrons.com | Micron Stock Needs Markets to Clear These 3 Hurdles

### AMD（Advanced Micro Devices, Inc.、保有、半導体、前日比 -7.5%、1週 -12.1%、時間外 +0.7%）

#### Googleニュース
検索語: `Advanced Micro Devices stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 10/27 Investing.com | Why is Advanced Micro Devices stock rallying today?
- 10/30 Seeking Alpha | Advanced Micro Devices slides 13% as part of tech selloff (AMD:NASDAQ)
- 10/30 MarketWatch | AMD’s stock slides after Intel earnings reveal two big issues

#### Yahooファイナンス
検索語: `AMD`
- 11/2 Barrons.com | AI Rebound Loses Steam. Chip Stocks Reverse Gains.
- 11/2 Barrons.com | Active Fund Managers Staged a Big Comeback. Can It Last?
- 11/2 GuruFocus.com | AMD Heads Into Earnings With AI Guidance in the Spotlight

### DELL（Dell Technologies Inc.、候補、AIサーバー・ストレージ・メモリ・端末、前日比 -7.4%、1週 -15.9%、時間外 +0.5%）

#### Googleニュース
検索語: `Dell stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 10/29 Trefis | Has Buying Dell Stock’s Dips Paid Off?
- 10/30 24/7 Wall St. | Dell Sinks 11% as Intel's Warning on PC Slump and Memory Shortage Hits Hardware Stocks; HP Tumbles 9%, Hewlett Packard Enterprise and Super Micro Fall 7%
- 10/31 Yahoo Finance | Why Dell (DELL) shares are getting obliterated today
- 11/2 MarketWatch | Dell Technologies Inc. Cl C stock falls Monday, underperforms market

#### Yahooファイナンス
検索語: `DELL`
- 11/2 24/7 Wall St. | Dell Crashed by 20% Over The Last Month: A Respected Wall Street Analyst Says 65% Gains Are Incoming
- 11/2 24/7 Wall St. | Super Micro Drops 5% Ahead of Earnings as AI Server Selloff Extends; Dell Falls 4%, HPE Slides 3%
- 11/2 Business Wire | CrowdStrike and Dell Technologies Announce Integrated AI Security for the Dell AI Factory with NVIDIA

### MU（Micron Technology, Inc.、候補、半導体、前日比 -5.8%、1週 -7.8%、時間外 +0.8%）

#### Googleニュース
検索語: `Micron stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 10/28 Yahoo Finance | SK Hynix Jumps 8% After a 632% Profit Surge and a $45 Billion Shareholder Pledge. Micron and SanDisk Are Riding Along.
- 10/29 Yahoo Finance | Micron shares dip as Samsung’s post-earnings selloff spreads to memory peers
- 10/30 Barron's | Micron Stock Drops Again. Surging Memory Prices Aren’t All Good News.

#### Yahooファイナンス
検索語: `MU`
- 11/2 Barrons.com | Micron Expected to Launch Massive Stock Buybacks in December. What to Know.

### HPE（Hewlett Packard Enterprise Company、候補、AIサーバー・ストレージ・メモリ・端末、前日比 -7.1%、1週 -12.8%、時間外 +0.5%）

#### Googleニュース
検索語: `Hewlett Packard Enterprise stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 10/27 Barchart.com | Dell and HPE Lost Billions in a Day Over 1 Big Worry. Dell Had Already Answered It.
- 10/27 MarketBeat | Hewlett Packard Enterprise (NYSE:HPE) Stock Price Up 3.6% - Here's Why
- 10/29 MarketWatch | Hewlett Packard Enterprise Co. stock underperforms Thursday when compared to competitors

#### Yahooファイナンス
検索語: `HPE`
- 10/30 Simply Wall St. | 3 Software Stocks Retail Investors Are Watching For AI Cost Control

### LITE（Lumentum Holdings Inc.、候補、光・通信・ネットワーク、前日比 -18.6%、1週 -16.3%、時間外 +1.4%）

#### Googleニュース
検索語: `Lumentum stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 10/29 Barron's | Marvell Stock Slides. Why the Market Hates the Idea of a Lumentum Buyout.
- 10/29 Investor's Business Daily | Lumentum Jumps, Fades On Marvell Buyout Report
- 11/2 Yahoo Finance | Why Lumentum Stock Fell 14.9% Today
- 11/2 24/7 Wall St. | Marvell Slides 3%, Lumentum Drops 6% on $115 Billion All-Stock Merger Deal; Coherent Climbs 2%

#### Yahooファイナンス
検索語: `LITE`
- 11/2 Bloomberg | Lumentum Goes From $1 Billion Spinoff to $115 Billion Takeover
- 11/2 Investor's Business Daily | Dow Jones Futures: AI Trade Dives As Marvell, Lumentum Plunge; Apple Slides On Earnings With Midterm Elections Next
- 11/2 Investor's Business Daily | Stock Market Today: Dow Up, Nasdaq Dives As Seagate Sinks; These Stocks Clear Entries

### PLTR（Palantir Technologies Inc.、候補、AIプラットフォーム・クラウド、前日比 -3.1%、1週 -10.3%、時間外 -0.5%）

#### Googleニュース
検索語: `Palantir stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 10/28 Yahoo Finance | Palantir Stock Falls After RBC Delivers Fresh Warning Ahead of Earnings
- 10/28 Yahoo Finance | Palantir Technologies Inc. (PLTR) Stock Sinks As Market Gains: Here's Why
- 10/29 Barron's | Why J.P. Morgan Believes Palantir Stock Is Just Getting Going After a Lackluster 2026
- 10/29 Benzinga | Palantir Stock Drops: What's Going On? - Palantir Technologies (NASDAQ:PLTR)

#### Yahooファイナンス
検索語: `PLTR`
- 11/2 Investing.com | Palantir raises 2026 revenue outlook after quarterly revenue nearly doubles on AI
- 11/2 Investor's Business Daily | Palantir Earnings Top Views. Revenue Beat Slightly Smaller.

### TT（Trane Technologies plc、候補、データセンターの電力・冷却・部品・受託製造・建設、前日比 +0.8%、1週 -9.2%、時間外 +0.0%）

#### Googleニュース
検索語: `Trane stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 10/28 MarketWatch | Trane Technologies PLC stock underperforms Wednesday when compared to competitors
- 10/28 ChartMill | Trane Technologies (NYSE:TT): A Quality Dividend Pick for Dividend Investors
- 10/29 Investing.com | Why is Trane Technologies stock sliding today?
- 10/29 TradingView | Trane Technologies sinks to 7-mth low as margins narrow

#### Yahooファイナンス
検索語: `TT`
- 10/30 MT Newswires | Trane Technologies' Mixed Q3 Results, Booking Deceleration Weigh on Sentiment, Oppenheimer Says
- 10/30 StockStory | 3 large-cap stocks with solid fundamentals
- 10/30 Zacks | FCN Q3 Earnings & Revenues Top Estimates, Stock Gains 14.3%

## 3. 引けまでに大きく下げた銘柄（2026-10-27〜2026-11-02 の見出し）

### HPQ（HP Inc.、AIサーバー・ストレージ・メモリ・端末、前日比 -1.2%、1週 -16.6%、時間外 -0.1%）

#### Googleニュース
検索語: `HP stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 10/29 Yahoo Finance | HPQ, DELL Stocks Plunge After Intel Flags Prolonged PC Market Weakness
- 10/31 Yahoo Finance | Why HP (HPQ) shares are sliding today

#### Yahooファイナンス
検索語: `HPQ`
- 10/30 Barrons.com | Intel’s Earnings Disaster Spreads Across the Sector

### NTAP（NetApp, Inc.、AIサーバー・ストレージ・メモリ・端末、前日比 -7.0%、1週 -16.6%、時間外 +0.0%）

#### Googleニュース
検索語: `NetApp stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 10/27 Yahoo Finance | Would You Have Held NetApp Stock All The Way Up?
- 10/29 Yahoo Finance | Investors Heavily Search NetApp, Inc. (NTAP): Here is What You Need to Know
- 10/30 Quiver Quantitative | NetApp Falls as Downgrade and Valuation Concerns Weigh on Shares
- 10/31 MarketBeat | NetApp (NASDAQ:NTAP) Rating Lowered to "Buy" at Wall Street Zen

#### Yahooファイナンス
検索語: `NTAP`
- 10/30 Investor's Business Daily | Stock Market Today: Nasdaq Slumps On Weak Intel Report; NetApp Gives Sell Signal
- 10/30 Simply Wall St. | Why Is NetApp (NTAP) In Focus After A New Keystone Channel Push?
- 10/30 Trefis | What Could Lift Western Digital Stock?

### FFIV（F5, Inc.、光・通信・ネットワーク、前日比 -4.1%、1週 -29.7%、時間外 +0.0%）

#### Googleニュース
検索語: `F5 stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 10/28 Yahoo Finance | Why F5 (FFIV) stock is falling today
- 10/28 Investing.com | Why is F5 stock sliding today?
- 10/28 Barron's | F5 Stock Is Having Its Worst Day in Over a Decade. Blame Its Costly AI Push.
- 10/28 Proactive financial news | F5 stock tumbles as hardware replacement growth slows

#### Yahooファイナンス
検索語: `FFIV`
- 10/29 24/7 Wall St. | F5 Beat on Revenue and Still Dropped 20%. One Soft Guide Was All It Took for a Stock Up 80% This Year.
- 10/29 Simply Wall St. | US Stock Market Today: S&P 500 Futures Slip On Higher For Longer Rate Focus
- 10/29 StockStory | F5’s Q3 earnings call: our top 5 analyst questions

### CIEN（Ciena Corporation、光・通信・ネットワーク、前日比 -11.3%、1週 -15.4%、時間外 +1.3%）

#### Googleニュース
検索語: `Ciena stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 10/27 Yahoo Finance | Analyst explains why optical stocks are moving higher
- 10/30 Yahoo Finance | Is There A Risk Hiding In Ciena Stock's Growth?
- 10/30 Barchart.com | Ciena’s Quarterly Earnings Preview: What You Need to Know
- 11/2 Investing.com Canada | Why is Ciena stock rallying today? By Investing.com

#### Yahooファイナンス
検索語: `CIEN`
- 10/27 Barrons.com | Corning Earnings Show It’s Deeply Dependent on AI Demand. Why That Could Be Bad.
- 10/28 Motley Fool | 2 AI Stocks Down 48% to 70% to Buy Now and Hold for 10 Years
- 10/29 HR Dive | Verizon, Franklin Electric announce new HR leaders in October
