# テーマ監視 2026-10-30

# 判定のまとめ（ルールの判定と著者の判定を分けて表示）

- **ルールの判定**: 採用した売買ルール（スクリプト）が数値で決めたもの。損切りは買値の15%下の逆指値（日中に届けばその場で売れる）。
- **著者の判定**: ノートブックの著者の回答。買いは注文を止める理由があるときだけ【様子見】、保有はルールより早く手じまう理由があるときだけ【売り】。根拠は下の「著者の回答（全文）」。
- 2つが食い違うときに、どちらに従うかはユーザーが決める。

- **テーマ全体の急落（S2・記録だけ）: あり（S2）**（SOXが直近60取引日の最高値から -19.1%）。S2の日の順張りの候補には「S2なら見送る形」と付ける（売買のルールは変えない。記録してから採用を決める。2026-10-14）

## 保有銘柄

| 銘柄 | ルール | 損益 | 時間外 | ルールの判定 | ルールの判定の理由 | 著者の判定 |
|---|---|---|---|---|---|---|
| SNDK | ルール外（ユーザーの判断。この日はどのルールの合図もなし） | -16.1% | +0.7% | **売り** | 終値 1150.89 が損切り価格 1165.61 以下 | 【未判定】（） |
| AMD | ボリンジャーIII | -8.2% | +0.6% | 保有継続 | 損切り 467.47（終値から -7.4%） | 【保有継続】（ボリンジャー） |

## 候補の判定（並びは上の「買う順番」の表と同じ）

- 並びは上の「買う順番」の表と同じ（RSの高い順。勝率の高い順ではない）。注文の値段・株数・逆指値は上の表を見る。勝率・1回平均は、そのルールの過去の成績（後知恵なしの監視銘柄・2015年〜の全部の合図）。
- 空き枠: 3（同時保有4銘柄まで。保有2、うちルールの売り1）。著者が【様子見】の候補を見送るかはユーザーが決める。

| 順 | 銘柄 | ルール | 過去の勝率 | 過去の1回平均 | RS | 時間外 | ルールの判定 | 著者の判定 |
|---|---|---|---|---|---|---|---|---|
| 1 | DELL（デル・テクノロジーズ） | 逆張り: 急落の底（担当: コナーズ） | 65% | +2.1% | 99 | +0.1% | 買い（翌日の寄り付き） | 【買い】（コナーズ） |
| 2 | MRVL（マーベル・テクノロジー） | 逆張り: 急落の底（担当: コナーズ） | 65% | +2.1% | 97 | +0.8% | 買い（翌日の寄り付き） | 【買い】（コナーズ） |
| 3 | NTAP（ネットアップ） | 逆張り: ボリンジャー メソッドIII | 68% | +1.5% | 96 | -0.4% | 買い（翌日の寄り付き） | 【買い】（ボリンジャー） |
| 4（枠外） | DDOG（データドッグ） | 逆張り: 急落の底（担当: コナーズ） | 65% | +2.1% | 93 | +0.2% | 買い（翌日の寄り付き） | 【買い】（コナーズ） |
| 5（枠外） | FTNT（フォーティネット） | 逆張り: ボリンジャー メソッドIII | 68% | +1.5% | 90 | +0.3% | 買い（翌日の寄り付き） | 【買い】（ボリンジャー） |

- 時間外: 前の取引日の引けから、引け後（米国東部時間16〜20時）の最後の値までの騰落率（Yahoo。±5%以上は太字）。寄り付きの値段は、表の注文の目安（前日の終値で計算）から大きくずれることがある。原因の見出しは「ニュースの見出し」の節。

# 著者の回答（全文）

## 0_テーマの局面_ワインスタイン

1. **テーマ全体の局面**: 【ステージ1またはステージ3】（30週線が横ばいのため、第2章）
2. **グループごとの局面**:
- 半導体｜ステージ1または3｜30週線が横ばい（第2章）
- 半導体製造装置・材料・設計ソフト・計測｜ステージ1または3｜30週線が横ばい（第2章）
- AIサーバー・ストレージ・メモリ・端末｜ステージ2｜30週線が上昇（第2章）
- 光・通信・ネットワーク｜ステージ1または3｜30週線が横ばい（第2章）
- データセンターの電力・冷却・部品・受託製造・建設｜ステージ1または3｜30週線が横ばい（第2章）
- AIプラットフォーム・クラウド｜ステージ1または3｜30週線が横ばい（第2章）
- AIソフト・セキュリティ・ITサービス｜ステージ2｜30週線が上昇（第2章）
3. **転換の兆し**: 出ている。30週線の横ばい推移、指数が移動平均線を下回り、対S&P500の相対的強さ（RS）が劣後する状態は天井（ステージ3）の兆しに当たる（第2章、第4章）。※提示された「50日線」や「割合40%未満」等の数値条件はマニュアルに規定なし。
4. **テーマの外**: なし

（全体の版が空の応答だったため、1〜2節だけの短い版で送り直した回答。ヒートマップ・急騰急落・ニュースは渡していない）

## 1_コナーズ_prompt_1

## DELL
1. **投資判断**: 【買い】
2. **止める理由の確認**:
   - 本が禁じる形・状況｜なし｜200日線の上側かつ急落後のため（第3章・第4章）
   - 避けるべき時期（決算など）｜なし｜決算回避の規定なし。禁止の月初3〜8日でもない（第11章）
   - 悪材料｜なし｜悪報道による急落こそ買いの好機（第2章・第3章・第8章）
3. **現状パターンと価格**:
   - 現状パターン: A（直近5日高値比-15.5%、RSI(2)=7.8で買い条件成立）
   - 本日の発注: 翌日の寄り付きで成行
4. **注意点**: 特になし

## 1_コナーズ_prompt_2

## MRVL
1. **投資判断**: 【買い】（止める理由なし）
2. **止める理由の確認**:
   - 本が禁じる形・状況｜なし｜株価は200日線（183.19）の上側に位置（第4章）
   - 避けるべき時期（決算など）｜なし｜次回決算32日後（マニュアルに規定なし）
   - 悪材料｜なし｜悲観的なニュースや悪材料での急落買いを推奨（第2章・第8章）
3. **現状パターンと価格**:
   - 現状パターン: A（急落の底・条件成立）
   - 本日の発注: 翌日の寄り付きで成行
4. **注意点**: 特になし

## 1_コナーズ_prompt_3

## DDOG
1. **投資判断**: 【買い】（注文を止める理由なし）
2. **止める理由の確認**:
   - 本が禁じる形・状況｜なし｜200日線上側で急落を買う形（第4章、判定用ルールブック5節）
   - 避けるべき時期（決算など）｜なし｜決算直前の見送り規定なし（判定用ルールブック12節）
   - 悪材料｜なし｜悪材料下のパニック急落は買いのエッジ（第2・3・8章、10/30ニュース）
3. **現状パターンと価格**:
   - 現状パターン: A（最新足で条件成立）
   - 本日の発注: 翌日の寄り付きで成行
4. **注意点**: 11/04に決算発表を控えているため跨ぎのボラティリティに注意

## 1_ボリンジャー_prompt_1

## AMD
1. **投資判断**: 【保有継続】
2. **止める理由の確認**:
   - 本が禁じる形・状況｜なし｜第5章p.1441、第17章p.1557（一律損切り否定、下部バンド未達）
   - 避けるべき時期（決算など）｜なし｜マニュアルに規定なし（第15章p.1540）
   - 悪材料｜なし｜マニュアルに規定なし（23_用語集p.1632）
3. **現状パターンと価格**:
   - 保有中: `売りの予約注文: 指値 658.39（現在値比 +30.4%）`
4. **注意点**: 大陰線での下落だが一律損切りは否定（第5章p.1441）。設定した損切り価格（467.47）と指値ルールを遵守。

## 1_ボリンジャー_prompt_2

## NTAP
1. **投資判断**: 【買い】（ルール成立・見送り理由なし）
2. **止める理由の確認**:
   - 本が禁じる形・状況｜なし｜第20章, 判定用ルールブック
   - 避けるべき時期（決算など）｜なし｜マニュアルに規定なし（決算まで32日）
   - 悪材料｜判定不能｜ニュース省略のため（判定用ルールブック）
3. **現状パターンと価格**:
   - 現状パターン: A（%b=0.010、21日II%=+0.016でメソッドIII成立）
   - 本日の発注: 翌日の寄り付きで成行
4. **注意点**: 直近安値付近に損切りストップを設定しリスクを限定する（第20章）。

## 1_ボリンジャー_prompt_3

## FTNT
1. **投資判断**: 【買い】
2. **止める理由の確認**:
   - 本が禁じる形・状況｜なし｜メソッドIIIの条件を満たし否定条件なし（第20章）
   - 避けるべき時期（決算など）｜なし｜マニュアルに規定なし（決算は通過済み）
   - 悪材料｜なし｜マニュアルに規定なし
3. **現状パターンと価格**:
   - 現状パターン: A（%b=-0.175, 21日II%=+0.071で成立）
   - 本日の発注: 翌日の寄り付きで成行
4. **注意点**: 特になし

# スキャン（数値と事実）


- 監視銘柄 87（判定できたのは 86、取得不可: Q）。
- この一覧は数値と事実だけ。売買の判断は著者のノートブックが行う。

## 1. テーマ（グループ）の強さ

| グループ | 銘柄数 | 1週 | 1カ月 | 3カ月 | 3カ月の順位 | 50日線より上の銘柄の割合 | グループ指数の30週線の局面（線との乖離、4週前からの線の傾き） |
|---|---|---|---|---|---|---|---|
| 半導体 | 16 | +0.8% | -10.5% | +3.4% | 3位 | 31% | 横ばい（-3.1%、+6.2%） |
| 半導体製造装置・材料・設計ソフト・計測 | 8 | +3.6% | -17.8% | -4.6% | 4位 | 25% | 横ばい（-10.7%、+2.7%） |
| AIサーバー・ストレージ・メモリ・端末 | 9 | -2.8% | -20.9% | +7.2% | 1位 | 11% | 上昇（+4.1%、+8.8%） |
| 光・通信・ネットワーク | 9 | -0.3% | -17.4% | -15.8% | 7位 | 11% | 横ばい（-10.5%、+2.8%） |
| データセンターの電力・冷却・部品・受託製造・建設 | 19 | +3.5% | -2.5% | -10.9% | 6位 | 21% | 横ばい（-6.5%、+1.0%） |
| AIプラットフォーム・クラウド | 11 | -2.9% | -5.0% | -7.5% | 5位 | 27% | 横ばい（-7.2%、+1.9%） |
| AIソフト・セキュリティ・ITサービス | 14 | -5.8% | +3.7% | +6.3% | 2位 | 50% | 上昇（+12.3%、+5.3%） |

## 2. テーマ全体の状態と早めの警告

- 市場全体の30週線による局面: S&P500指数 **上昇**／NASDAQ100指数 **横ばい**（急落の底で買うルールは、過去の検証で下落相場で特に強く、横ばいの相場では負けていた）
- **2倍ETFを使う局面（案1、2026-10-13 採用）: S&P500の20週線（100日線）で 横ばい** → 新しく買う銘柄は、2倍ETFのある銘柄も元の株で買う（保有中のETFはそのまま）（SPY 755.72、100日線 757.82、20日前の線 752.22。上昇＝線より上かつ線が上向き）
- **テーマ全体の急落（S2、記録だけ。売買のルールは変えない）: あり（S2）**（SOX 10688.80、直近60取引日の最高値 13217.82 から -19.1%。S2＝最高値から−10%以上）。S2のときに「順張りの新しい買いだけ止める」形を記録で比べる（2026-10-14 ユーザー決定。バックテストでは年率は上がったが2つの期間ではどちらも少し下回ったため、記録してから採用を決める。`バックテスト結果/テーマ全体の急落を検知して手じまう・買いを止める.md`）
- テーマ指数（監視銘柄の等金額平均）の30週線による局面: **横ばい**（上昇＝線より上かつ上向き、下落＝線より下かつ下向き、それ以外＝横ばい。ワインスタインのステージの近似）
- テーマ指数と50日線: 50日線より下（乖離 -6.6%）
- S&P500に対する相対的な強さ: 50日平均より下（S&P500より弱い）
- 監視銘柄のうち50日線より上の割合: 27%
- 警告（割合が40%未満かつテーマ指数が50日線より下）: **出ている**
- 参考（バックテスト）: 30週線の「下落」は高値から10〜33%下げた後に出る遅い判定。50日線・割合・相対的な強さは高値から2〜8%で出るが、誤報が年15回以上ある。警告中に新しい買いを止めると、押し目買い（ボリンジャーIII）の成績は大きく下がった（`バックテスト結果/テーマ監視銘柄・直近3年.md` 11・12節）。

## 3. ヒートマップ（Finviz、全米の業種別の騰落率）

3カ月の騰落率の上位15業種（テーマの外で強くなっている業種の確認用）:

| 順位 | 業種 | 1週 | 1カ月 | 3カ月 | 6カ月 | 1年 |
|---|---|---|---|---|---|---|
| 1 | Health Information Services | +0.9% | +10.2% | +35.4% | +52.2% | +4.7% |
| 2 | Oil & Gas Refining & Marketing | -3.0% | +2.1% | +31.2% | +59.5% | +107.2% |
| 3 | Oil & Gas Drilling | +6.3% | +20.8% | +25.4% | -4.3% | +60.6% |
| 4 | Diagnostics & Research | +1.6% | +7.1% | +20.2% | +48.1% | +28.6% |
| 5 | Oil & Gas Integrated | -0.2% | +12.6% | +17.5% | +16.9% | +58.9% |
| 6 | Auto Manufacturers | +6.1% | +10.5% | +16.1% | +2.0% | -12.5% |
| 7 | Drug Manufacturers - General | +6.2% | +13.4% | +15.7% | +26.2% | +42.1% |
| 8 | Oil & Gas E&P | +1.3% | +15.2% | +15.6% | +10.2% | +53.7% |
| 9 | Consumer Electronics | -1.0% | +4.4% | +13.5% | +23.0% | +24.9% |
| 10 | Information Technology Services | +0.8% | +11.9% | +12.7% | +10.1% | -15.3% |
| 11 | Medical Distribution | -0.2% | +8.8% | +12.2% | +19.4% | +21.5% |
| 12 | Lodging | +2.5% | +11.4% | +12.1% | +10.3% | +38.7% |
| 13 | Real Estate - Diversified | +4.2% | +8.3% | +10.8% | +13.0% | +15.2% |
| 14 | Marine Shipping | +1.7% | +0.5% | +10.8% | +13.7% | +70.1% |
| 15 | Chemicals | +6.4% | +17.4% | +10.1% | -19.0% | +31.6% |

テーマの業種の順位（3カ月、全144業種中）: Semiconductors 69位、Semiconductor Equipment & Materials 129位、Computer Hardware 124位、Communication Equipment 88位、Electronic Components 116位、Software - Infrastructure 28位、Software - Application 19位、Internet Content & Information 135位

## 4. 急騰・急落した銘柄（前日比±5%以上、または出来高が50日平均の2倍以上）

原因のニュースをサブエージェントが調べ、候補・保有銘柄の判定材料として著者に渡す。急騰・急落そのものは売買の合図にしない（後知恵のないS&P500全体のバックテストでは、急騰の翌日に買うルールは年率7%、急落の翌日に買うルールは年率9〜10%で、採用した3つのルールより優れていなかった）。

| 銘柄 | グループ | 前日比 | 出来高（50日平均の倍） | 終値 | 50日線 | RS | 局面 |
|---|---|---|---|---|---|---|---|
| RDDT | AIソフト・セキュリティ・ITサービス | -29.2% | 7.0倍 | 91.73 | 下 | 0 | レンジ |
| INTC | 半導体 | -28.6% | 4.5倍 | 65.76 | 下 | 41 | レンジ |
| SNDK | AIサーバー・ストレージ・メモリ・端末 | -13.5% | 1.9倍 | 1150.89 | 下 | 99 | レンジ |
| DDOG | AIソフト・セキュリティ・ITサービス | -11.5% | 1.8倍 | 235.27 | 下 | 93 | レンジ |
| COHR | 光・通信・ネットワーク | -11.3% | 1.8倍 | 210.32 | 下 | 19 | レンジ |
| QCOM | 半導体 | -11.1% | 2.0倍 | 164.79 | 下 | 45 | レンジ |
| ALAB | 半導体 | -10.9% | 1.9倍 | 258.70 | 下 | 83 | レンジ |
| AMD | 半導体 | -10.9% | 2.0倍 | 504.80 | 下 | 96 | レンジ |
| DELL | AIサーバー・ストレージ・メモリ・端末 | -10.8% | 1.3倍 | 424.30 | 下 | 99 | レンジ |
| NBIS | AIプラットフォーム・クラウド | -10.4% | 1.2倍 | 154.14 | 下 | 61 | レンジ |
| APP | AIプラットフォーム・クラウド | -10.4% | 2.0倍 | 228.50 | 下 | 0 | レンジ |
| MRVL | 半導体 | -10.0% | 2.0倍 | 196.40 | 下 | 97 | レンジ |
| ARM | 半導体 | -10.0% | 2.2倍 | 205.97 | 下 | 76 | レンジ |
| CRWV | AIプラットフォーム・クラウド | -9.7% | 1.4倍 | 54.87 | 下 | 1 | レンジ |
| HPQ | AIサーバー・ストレージ・メモリ・端末 | -9.6% | 2.1倍 | 28.78 | 下 | 85 | レンジ |
| NTAP | AIサーバー・ストレージ・メモリ・端末 | -8.8% | 1.1倍 | 199.18 | 下 | 96 | レンジ |
| LITE | 光・通信・ネットワーク | -8.6% | 1.6倍 | 840.70 | 下 | 98 | レンジ |
| ANET | 光・通信・ネットワーク | -8.3% | 1.6倍 | 168.86 | 下 | 37 | レンジ |
| CIEN | 光・通信・ネットワーク | -8.2% | 1.1倍 | 320.72 | 下 | 46 | レンジ |
| STX | AIサーバー・ストレージ・メモリ・端末 | -8.0% | 1.3倍 | 644.58 | 下 | 89 | レンジ |
| AMAT | 半導体製造装置・材料・設計ソフト・計測 | -7.5% | 1.6倍 | 390.09 | 下 | 56 | レンジ |
| WDC | AIサーバー・ストレージ・メモリ・端末 | -7.4% | 1.1倍 | 366.11 | 下 | 87 | レンジ |
| TER | 半導体製造装置・材料・設計ソフト・計測 | -7.4% | 3.2倍 | 274.37 | 下 | 35 | レンジ |
| FLEX | データセンターの電力・冷却・部品・受託製造・建設 | -7.1% | 1.0倍 | 86.48 | 下 | 40 | レンジ |
| FFIV | 光・通信・ネットワーク | -6.9% | 3.9倍 | 338.34 | 下 | 49 | レンジ |
| CDW | AIソフト・セキュリティ・ITサービス | -6.9% | 1.6倍 | 153.79 | 上 | 60 | 上昇相場 |
| KEYS | 半導体製造装置・材料・設計ソフト・計測 | -6.9% | 1.6倍 | 307.20 | 下 | 80 | レンジ |
| AKAM | 光・通信・ネットワーク | -6.7% | 1.1倍 | 92.72 | 下 | 21 | レンジ |
| ASML | 半導体製造装置・材料・設計ソフト・計測 | -6.6% | 1.6倍 | 1565.90 | 下 | 66 | レンジ |
| HPE | AIサーバー・ストレージ・メモリ・端末 | -6.4% | 0.8倍 | 55.09 | 下 | 98 | レンジ |
| ORCL | AIプラットフォーム・クラウド | -6.4% | 1.3倍 | 130.67 | 下 | 5 | レンジ |
| PLTR | AIプラットフォーム・クラウド | -6.3% | 1.1倍 | 184.11 | 下 | 88 | レンジ |
| ETN | データセンターの電力・冷却・部品・受託製造・建設 | -6.0% | 1.7倍 | 369.97 | 下 | 18 | レンジ |
| LRCX | 半導体製造装置・材料・設計ソフト・計測 | -6.0% | 2.0倍 | 239.11 | 下 | 39 | レンジ |
| JCI | データセンターの電力・冷却・部品・受託製造・建設 | -5.8% | 1.4倍 | 149.03 | 上 | 69 | レンジ |
| KLAC | 半導体製造装置・材料・設計ソフト・計測 | -5.7% | 2.3倍 | 157.91 | 下 | 37 | レンジ |
| SHOP | AIソフト・セキュリティ・ITサービス | -5.6% | 1.2倍 | 157.49 | 上 | 80 | レンジ |
| AVGO | 半導体 | -5.5% | 1.5倍 | 326.08 | 下 | 11 | レンジ |
| VRT | データセンターの電力・冷却・部品・受託製造・建設 | -5.5% | 1.3倍 | 232.50 | 下 | 30 | レンジ |
| MU | 半導体 | -5.3% | 1.2倍 | 884.74 | 下 | 98 | レンジ |
| JBL | データセンターの電力・冷却・部品・受託製造・建設 | -5.2% | 1.0倍 | 272.72 | 下 | 30 | レンジ |
| MCHP | 半導体 | -4.7% | 2.2倍 | 77.34 | 上 | 46 | レンジ |
| NOW | AIソフト・セキュリティ・ITサービス | -4.1% | 2.4倍 | 105.12 | 下 | 15 | レンジ |
| ADI | 半導体 | -3.7% | 2.3倍 | 417.11 | 上 | 90 | 上昇相場 |
| TXN | 半導体 | -3.4% | 2.1倍 | 300.84 | 上 | 93 | レンジ |
| NXPI | 半導体 | -2.4% | 2.5倍 | 259.61 | 上 | 69 | レンジ |
| AMZN | AIプラットフォーム・クラウド | -1.4% | 2.9倍 | 240.35 | 下 | 20 | レンジ |
| GOOGL | AIプラットフォーム・クラウド | -1.4% | 2.3倍 | 279.84 | 下 | 8 | レンジ |
| DLR | データセンターの電力・冷却・部品・受託製造・建設 | -1.2% | 2.1倍 | 180.70 | 下 | 37 | レンジ |
| MPWR | 半導体 | +1.1% | 3.0倍 | 1211.63 | 下 | 24 | レンジ |

- 局面: 終値 > 50日線 > 200日線、50日線が20取引日前より2%以上高い、ADX(14) ≧ 20 をすべて満たせば上昇相場、それ以外はレンジ（判定式はClaudeが置いたもの）。

## 4-2. 監視外の注目銘柄（S&P500・NASDAQ100のうち監視銘柄に入っていない銘柄）

条件: 流動性（株価5ドル以上・50日平均出来高25万株以上）があり、(a) 前日比+8%以上かつ出来高が50日平均の2倍以上、または (b) 終値が直前1年の最高値（終値）を上回り、RS≧90。RSの高い順に5銘柄（ニュースを調べる）。監視銘柄に入れるかはユーザーが決める。

| 銘柄 | 種類 | 前日比 | 出来高（50日平均の倍） | RS | 終値 |
|---|---|---|---|---|---|
| APA | 1年の高値更新 | +2.5% | 0.8倍 | 97 | 52.82 |
| TRGP | 1年の高値更新 | +1.2% | 1.3倍 | 95 | 314.99 |
| COP | 1年の高値更新 | +2.7% | 1.1倍 | 95 | 154.03 |
| LLY | 1年の高値更新 | +3.2% | 2.2倍 | 95 | 1417.54 |
| AMGN | 1年の高値更新 | +1.1% | 1.2倍 | 94 | 466.01 |

- ほかに7銘柄: XOM（1年の高値更新、RS 92）、CVX（1年の高値更新、RS 92）、GILD（1年の高値更新、RS 92）、EOG（1年の高値更新、RS 91）、ABBV（1年の高値更新、RS 90）、REGN（急騰、RS 89）、GPN（急騰、RS 85）

## 5. 保有銘柄の手じまい条件（`新分析ツール/保有銘柄.md`）

| 銘柄 | ルール | 買った日 | 買値 | 終値 | 損益 | 損切り価格（買値の15%下、逆指値） | ルールの手じまい条件 | 出来高2倍の大陰線（買った後の直近5日） | 次回決算予定日 |
|---|---|---|---|---|---|---|---|---|---|
| SNDK | ルール外（ユーザーの判断。この日はどのルールの合図もなし） | 2026-10-21 | 1371.30 | 1150.89 | -16.1% | 1165.61 | **損切り価格を下回った** ルールが不明（保有銘柄.md の「ルール」を確認） | なし | 2026-10-29 |
| AMD | ボリンジャーIII | 2026-10-21 | 549.97 | 504.80 | -8.2% | 467.47 | 売りの指値: 上部バンド 658.39（今夜この値に置き直す。届いた日に売れる）（2倍ETF AMUU で持っている場合も、判定は元の株 AMD の値段） | なし | 2026-11-03 |

- 出来高2倍の大陰線: 実体（始値−終値）が前日までのATR(14)の1.5倍以上、終値がその日の値幅の下25%以内、出来高が前日までの50日平均の2倍以上の日。**押し目（ボリンジャーIII）・急落の底の保有では売りのルール**: 出たら翌日の寄り付きで全部売り、空いた枠で次の合図を買う（2026-10-02 ユーザー決定。`バックテスト結果/やり直し_売りの合図の組み合わせ.md`。乱数3組とも年率が約+2ポイント、最大下落率もやや下がった）。ミネルヴィニ・新高値V2の保有では事実の表示（順張りに足しても良くならなかった）。

- 半分売りの合図（ミネルヴィニ・新高値V2の保有だけ）: 反転のローソク足（かぶせ線・弱気の包み足・宵の明星・流れ星）＋出来高が50日平均の1.5倍以上＋RSI(14)が前日か当日に70以上。買った後に最初に出た日の翌日の寄り付きで半分売り、残り半分は50日線割れ・損切り15%まで持つ（2026-10-01 ユーザー決定。`バックテスト結果/半分だけ売るとオニールの空き枠.md`）。

- かぶせ線（ミネルヴィニ・新高値V2の保有だけ）: 上昇中の陽線の翌日に、前日の高値より上で寄り付き、前日の陽線の真ん中より下（前日の始値より上）で引けた日。翌日の寄り付きで全部売り、空いた枠で次の合図を買う。半分売りより優先する（2026-10-01 ユーザー決定。`バックテスト結果/2倍ETFで売って買い直す.md`。順張りの売買の25%で出て、1回平均+2.0%、年率 21.4%→26.4%）。

## 5-2. 前日（2026-10-29の引け）の【買い（予約）】の確認

前日の【買い（予約）】はなし。

## 6. 候補（採用したルールの条件が成立＝A。予約（B）は2026-10-25から注文せず、節6-3に参考の表示だけ）

建玉の目安: 同時保有4銘柄まで、1銘柄に資金の25%（資金÷4）、損切りは買値の15%下（ユーザー決定 2026-09-29）。

保有中のため候補から外した銘柄（合図は出ている）: AMD

パターン: A＝最新の足で採用ルールの条件が成立（翌日の寄り付きで成行）。条件の成立が目前の銘柄（B）は、予約の注文をやめたので節6-3に参考として出す（2026-10-25 ユーザー決定）。

| 銘柄 | グループ | パターン | 種類 | ルールの過去の成績 | 終値 | 前日比 | RS | 50日線の傾き | 局面 | 当てはまった条件 | 次回決算予定日 | 注文の目安 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DELL | AIサーバー・ストレージ・メモリ・端末 | A | 逆張り: 急落の底（担当: コナーズ） | 2位（勝率65%・1回平均+2.1%） | 424.30 | -10.8% | 99 | +5.1% | レンジ | 直前5日の最高値（終値）から-15.5%下落（−15%以上）、RSI(2)=7.8（≦10）、急落の前は50日線＞200日線。市場全体の局面: S&P500 上昇／NASDAQ100 横ばい | 2026-11-24（25日後） | 翌日の寄り付きで買い。損切り: 買値の15%下。手じまい: 終値が5日線（今日 472.53）を上回った翌日の寄り付き（コナーズ）。**元の株で買う**（2倍ETF DLLL のある銘柄だが、S&P500が20週線で「横ばい」の局面のため。案1）。**株数の目安: 5株**（2,384ドル÷424.30。今日の終値。寄り付きの値段で変わる）、購入金額 約2,121ドル |
| MRVL | 半導体 | A | 逆張り: 急落の底（担当: コナーズ） | 2位（勝率65%・1回平均+2.1%） | 196.40 | -10.0% | 97 | +7.0% | レンジ | 直前5日の最高値（終値）から-22.0%下落（−15%以上）、RSI(2)=8.9（≦10）、急落の前は50日線＞200日線。市場全体の局面: S&P500 上昇／NASDAQ100 横ばい | 2026-12-01（32日後） | 翌日の寄り付きで買い。損切り: 買値の15%下。手じまい: 終値が5日線（今日 228.75）を上回った翌日の寄り付き（コナーズ）。**元の株で買う**（2倍ETF MRVU のある銘柄だが、S&P500が20週線で「横ばい」の局面のため。案1）。**株数の目安: 12株**（2,384ドル÷196.40。今日の終値。寄り付きの値段で変わる）、購入金額 約2,357ドル |
| DDOG | AIソフト・セキュリティ・ITサービス | A | 逆張り: 急落の底（担当: コナーズ） | 2位（勝率65%・1回平均+2.1%） | 235.27 | -11.5% | 93 | +2.7% | レンジ | 直前5日の最高値（終値）から-16.2%下落（−15%以上）、RSI(2)=3.2（≦10）、急落の前は50日線＞200日線。市場全体の局面: S&P500 上昇／NASDAQ100 横ばい | 2026-11-04（5日後）**決算が近い** | 翌日の寄り付きで買い。損切り: 買値の15%下。手じまい: 終値が5日線（今日 268.12）を上回った翌日の寄り付き（コナーズ）。**株数の目安: 10株**（2,384ドル÷235.27。今日の終値。寄り付きの値段で変わる）、購入金額 約2,353ドル |
| NTAP | AIサーバー・ストレージ・メモリ・端末 | A | 逆張り: ボリンジャー メソッドIII | 3位（勝率68%・1回平均+1.5%） | 199.18 | -8.8% | 96 | +6.8% | レンジ | %b=0.010（<0.05）、21日II%=+0.016（>0） | 2026-12-01（32日後） | 翌日の寄り付きで買い。損切り: 買値の15%下。手じまい: 買った日の夜から、売りの指値をその日の上部バンド（今日 243.93）に置き、毎晩その日の値に置き直す。**株数の目安: 11株**（2,384ドル÷199.18。今日の終値。寄り付きの値段で変わる）、購入金額 約2,191ドル |
| FTNT | AIソフト・セキュリティ・ITサービス | A | 逆張り: ボリンジャー メソッドIII | 3位（勝率68%・1回平均+1.5%） | 136.08 | -2.2% | 90 | +4.7% | レンジ | %b=-0.175（<0.05）、21日II%=+0.071（>0） | 2026-10-28（-2日後） | 翌日の寄り付きで買い。損切り: 買値の15%下。手じまい: 買った日の夜から、売りの指値をその日の上部バンド（今日 208.57）に置き、毎晩その日の値に置き直す。**株数の目安: 17株**（2,384ドル÷136.08。今日の終値。寄り付きの値段で変わる）、購入金額 約2,313ドル |

- 2倍ETF: 2倍ETFがある銘柄（ユーザーがムームー証券で買えることを確認した38銘柄のうち、目減りが年15%未満のもの）は、株の代わりに2倍ETFを買う（2026-10-04 ユーザー決定。`バックテスト結果/2倍ETFを使う決まり.md`。年率 約27%→約33%、確定した損益だけの最大下落率 約30%→約31%、含み損込みは約33%→約45%）。買う金額は株と同じ（資金の25%）。合図・損切り（元の株の買値の15%下＝ETFでは約30%下）・手じまいはすべて元の株の値段で判定する。指値・逆指値はETFの値段に直して置く。どのETFかは `新分析ツール/2倍ETFの対応表.json`（売買代金が1日500万ドル以上で、直近1年の目減りが一番小さいもの）。**2倍ETFで買うのは、S&P500が20週線（100日線）で「上昇」の局面のときだけ。横ばい・下落の局面では元の株で買う**（案1、2026-10-13 ユーザー採用。買う日に決め、買った後は局面が変わってもそのまま持つ。`バックテスト結果/流れ（市場の局面）を使う形.md`）。

- ルールの過去の成績: 今の売りのルールで、後知恵なしの監視銘柄・2015年〜の全部の合図の1回ごとの成績（2026-10-02計算、`新分析ツール/バックテスト結果/ルールごとの成績.md`）。順位は1回平均（1回の売買で平均いくら増えるか）の順。表はパターン（A→B）ごとに、この順位の良い順に並べた（表示の順番だけ。買う順番・件数の上限は変えていない。候補の選び方を変えても成績は変わらなかったため。2026-10-02 ユーザーの指示）。著者には渡さない。

- 同じ銘柄に押し目（ボリンジャーIII）と急落の底（コナーズ）の両方の合図が出た銘柄（ミネルヴィニと新高値V2が両方出た銘柄も、ミネルヴィニの1行）は、1行にまとめた（枠も1銘柄1つ。2026-10-30 ユーザー決定。バックテストでは、同じ場面の1回平均が押し目+8.1%・急落の底+1.5%で、急落の底を優先すると年率が下がった）: FTNT（もう一方の合図は省いた）

- 同じ業種は同時に2銘柄まで（ユーザー決定 2026-09-28）のため見送った候補（保有中の銘柄と、買う順番で先に残した候補で数える）: PLTR（A・逆張り: ボリンジャー メソッドIII。Software - Infrastructure: NTAP・FTNT）、HPQ（A・逆張り: 急落の底。Computer Hardware: SNDK・DELL）、QCOM（A・逆張り: ボリンジャー メソッドIII。Semiconductors: AMD・MRVL）

- パターンBは各ルールでRSの高い順に2件まで、急落の底・新高値のAは4件（同時保有の上限）までとし、4件を省いた。

- 候補の数: 空き枠3（同時保有4銘柄まで。保有2、うち今日ルールの売りが成立1）＋予備2件まで表に出した（2026-10-25 ユーザー決定）。ほかの6件は枠に入らないので、著者の判定とニュース調査に回さない: SHOP（A・ボリンジャー メソッドIII、RS 80）、AMZN（A・ボリンジャー メソッドIII、RS 20）、TT（A・ボリンジャー メソッドIII、RS 17）、HUBB（A・ボリンジャー メソッドIII、RS 14）、CARR（A・ボリンジャー メソッドIII、RS 12）、LLY（A・新高値、RS 95）

- テーマの外の候補（グループが「テーマの外」）: 監視銘柄の候補で枠が埋まらないときに使う（監視銘柄の候補を先に買う）。S&P500の今の構成銘柄のうち監視銘柄でない銘柄から、RS≧90・30週線が上向きで終値がその上・業種の3カ月の強さが上位20%の20銘柄を調べ、空き枠2つ分まで出した。バックテストでは、テーマの外の強い銘柄で空き枠を埋めると、テーマが弱い時期の成績が支えられた（`バックテスト結果/半導体・AIに特化した場合.md`。2026-10-01 ユーザー決定）。

- RS≧80の押し目（ボリンジャーIII）は、バックテストで成績がより安定していた（PF3.27、最大下落20%）。

## 6-2. 参考: ワインスタイン10週の合図（売買には使わない・著者には送らない）

後知恵なしのバックテストで、今の4つのルールに加えると年率が下がった（27.1%→22.9〜26.3%。`バックテスト結果/ワインスタイン10週を加えるか.md`）ため、2026-10-04 から参考の表示だけにした（ユーザー決定）。強い銘柄が10週の高値に近づいている、という事実として見る。

| 参考の銘柄 | グループ | パターン | 種類 | 終値 | 前日比 | RS | 当てはまった条件 |
|---|---|---|---|---|---|---|---|
| NXPI | 半導体 | A | 順張り: ワインスタイン（10週の高値上抜け） | 259.61 | -2.4% | 69 | 週足の終値が直前10週の高値248.86を出来高2.1倍で上抜け、10週線が上向き |
| ACN | AIソフト・セキュリティ・ITサービス | B | 予約: ワインスタイン（10週の高値の手前） | 258.24 | +4.5% | 93 | 直前10週の高値259.39まで0.4%、10週線が上向き |
| ADI | 半導体 | B | 予約: ワインスタイン（10週の高値の手前） | 417.11 | -3.7% | 90 | 直前10週の高値422.67まで1.3%、10週線が上向き |
| AAPL | AIサーバー・ストレージ・メモリ・端末 | B | 予約: ワインスタイン（10週の高値の手前） | 344.63 | -1.2% | 84 | 直前10週の高値351.73まで2.1%、10週線が上向き |
| MSI | 光・通信・ネットワーク | B | 予約: ワインスタイン（10週の高値の手前） | 491.53 | -0.1% | 73 | 直前10週の高値493.57まで0.4%、10週線が上向き |
| EMR | データセンターの電力・冷却・部品・受託製造・建設 | B | 予約: ワインスタイン（10週の高値の手前） | 164.94 | -3.4% | 70 | 直前10週の高値165.24まで0.2%、10週線が上向き |
| TEL | データセンターの電力・冷却・部品・受託製造・建設 | B | 予約: ワインスタイン（10週の高値の手前） | 213.03 | -4.4% | 34 | 直前10週の高値223.52まで4.9%、10週線が上向き |
| BIIB | テーマの外（Drug Manufacturers - General） | B | 予約: ワインスタイン（10週の高値の手前） | 253.62 | +1.6% | 95 | 直前10週の高値254.41まで0.3%、10週線が上向き |
| IT | テーマの外（Information Technology Services） | B | 予約: ワインスタイン（10週の高値の手前） | 228.79 | +1.7% | 91 | 直前10週の高値234.74まで2.6%、10週線が上向き |
| A | テーマの外（Diagnostics & Research） | B | 予約: ワインスタイン（10週の高値の手前） | 174.87 | -3.5% | 91 | 直前10週の高値179.10まで2.4%、10週線が上向き |
| WAT | テーマの外（Diagnostics & Research） | B | 予約: ワインスタイン（10週の高値の手前） | 462.72 | -3.6% | 90 | 直前10週の高値465.36まで0.6%、10週線が上向き |


## 6-3. 参考: 条件の成立が目前の銘柄（予約は注文しない・著者には送らない）

2026-10-25 ユーザー決定: 予約（逆指値・指値）の注文はやめ、参考の表示だけにする。毎朝のツールと同じ条件・値段で予約の約定をバックテストに入れると、どの形も年率が下がった（後知恵なし 35.7%→30.7〜34.2%、87銘柄 45.6%→34.2〜42.6%。`バックテスト結果/点検_2026-10-25/`）。引けで条件がそろえば、翌朝の節6に買いの候補（A）として出る。各ルールでRSの高い順に2件まで。

| 参考の銘柄 | グループ | 種類 | 終値 | 前日比 | RS | 当てはまった条件 | 条件がそろう目安の価格（注文はしない） |
|---|---|---|---|---|---|---|---|
| MSFT | AIプラットフォーム・クラウド | ボリンジャー メソッドIII（%bが0.05未満に近い） | 521.91 | -1.6% | 67 | %b=0.118（0.05まであと少し）、21日II%=+0.001（>0） | 520.31（この値より下で引けると翌朝の買いの候補（A）。目安） |
| ANET | 光・通信・ネットワーク | ボリンジャー メソッドIII（%bが0.05未満に近い） | 168.86 | -8.3% | 37 | %b=0.140（0.05まであと少し）、21日II%=+0.004（>0） | 163.17（この値より下で引けると翌朝の買いの候補（A）。目安） |


# ニュース（サブエージェントの調査）

# ニュース調査（2026-10-30の引け時点。調査日 2026-11-02 JST）
確認方法: 主に headlines.md の見出し。見出しで分からない監視外銘柄とDDOG決算日のみ検索。

## テーマ全体の下げの原因
- 当たる日（監視銘柄3銘柄以上が−5%以下、S2あり、早めの警告あり）。headlines.md の見出しで5観点を確認。
- きっかけ: 10/29 引け後の Intel 決算（PC不振で弱い売上見通し、10/30 −28.6%、1974年以来最悪の日。Bloomberg/Yahoo Finance 10/30）と Amazon 決算（休暇期の見通しが予想未達、時間外−7%。Investing.com/株探 10/30）。「AIの現金流出（cash burn）懸念」でハイテク売り（Reuters 10/30）。
- 広がった先: Dell・HPQ（PC低迷・メモリ不足、24/7 Wall St. 10/30）、Sandisk（好決算でも−9%時間外、Kioxiaが警告、Yahoo Finance/24/7 Wall St. 10/30）、光学（AAOI−15%、COHR−13%、LITE・MRVL−10%、24/7 Wall St. 10/30）、Datadog−12%、Reddit−29%（GoogleのAI検索でトラフィック減、CNBC/Reuters 10/30）。
- 市場全体: Nasdaq 100が3%超下落し10月は2025年以来最悪の月、時価総額約1兆ドル消失、NY Times「6月以来最悪の日」（Business Insider/NBC/NYT 10/30）。Nasdaq 100は一時調整局面入り（24/7 Wall St. 10/31）。S&P500は下落するが下げは小さい。VIX・ハイイールド債の数値は見出しでは確認できず（取得不可）。
- 信用: 「AI債務」関連の見出しあり（Bloomberg 10/30「AI Debt Drives Wedge Between Corporate Bonds and Credit Hedges」、WSJ経由 10/31 ヘッジ需要、Barclays 10/31 AI CDS取引）。個別の格下げ・社債急落の見出しは今回なし。
- 呼び名: 日本の報道は10月の下げを「コアウィーブ・ショック」と呼ぶ（日経 10/30、東洋経済 10/30、マネーフォワード 10/31）。10/30の下げ自体はIntel・Amazon決算が直接の材料。
- 経済指標・金利: 「エネルギー価格インフレと賃金リスク」で先物下落（Yahoo Finance 10/30）、金利上昇懸念で不動産株急落（野村證券 10/30）。個別の指標名・数値は見出しでは不明。
- 大手決算: Nvidia・Salesforce決算通過後（野村證券 10/30）。TSMC・ASMLの当日材料は見出しになし。

## 引け後・時間外の材料
- MRVL: 時間外 +0.8%。材料の新規見出しなし。10/28以降、Lumentum買収報道で下落（Barron's/Motley Fool 10/29）。10/31時点でも後期協議の報道（Yahoo Finance）。
- SNDK: 時間外 +0.7%（引け後）。10/29引け後の決算後は−9%（株探 10/30）。
- 保有・候補の±5%超の時間外はなし（AMD +0.6%、NTAP −0.4%、FTNT +0.3%、DDOG +0.2%、DELL +0.1%）。
- 10/30引け後のその他: Okta がS&P500採用決定で急伸（Yahoo Finance 10/30）。Intel時間外−1.5%。10/31の先物はNasdaq −3.45%、メモリ株は逆行（BigGo 10/31）。

## SNDK（保有）
- 10/29引け後決算: Q1予想上振れ・ガイダンス引き上げ・8対1の株式分割発表（Yahoo Finance 10/30）。
- 10/30 −13.5%: 決算の質への疑問（TradingPedia 10/30）、Kioxiaが NAND価格急騰に警告（Yahoo Finance 10/30）。WDC−8%、STX−7%、MU−6%も同時に下落（24/7 Wall St. 10/30）。
- 決算: 直近（10/29発表）EPS Beat、ガイダンス 上回る（見出し）。売上は見出しで未確認。
- 悪材料: あり（Kioxiaの警告、決算の質への疑問）。

## AMD（保有）
- 10/30 −10.9〜−13%: Intel決算の「2つの大きな問題」で下落（MarketWatch/Seeking Alpha 10/30）。Intelは10月に−45%で史上最悪の月（24/7 Wall St. 10/31）。
- 次回決算は11/3（scan.md）。決算前に利益確定すべきかとの記事（Motley Fool 10/31）。
- 悪材料: あり（Intel警告の波及。AMD固有の悪材料は確認できず）。

## DELL（候補）
- 10/29〜10/30: Intelの長引くPC低迷の警告でDELL・HPQが急落（Yahoo Finance 10/29）。メモリ不足も重荷、Dell−11%、HP−9%、HPE・Super Micro−7%（24/7 Wall St. 10/30）。
- 悪材料: あり（業界全体の需要・メモリ不足懸念。Dell固有は確認できず）。

## MRVL（候補）
- 10/28〜10/29: LumentumをMarvellが買収する後期協議との報道で売り（Investing.com 10/28、Barron's 10/29「市場は買収案を嫌う」）。プレミアムは限定的との報道（GuruFocus 10/30）。
- 10/30: ARM・QCOMと共に下落、MRVL−8〜10%（24/7 Wall St. 10/30）。
- 悪材料: あり（大型買収報道による売り。公式発表は確認できず）。

## NTAP（候補）
- 10/30 −8.8%: 固有の原因の見出しは見つからなかった。IBDが「NetApp Gives Sell Signal」と報じ（IBD 10/30）、ストレージ・メモリ株全体の下げ（SNDK・WDC・STX）に連動。
- 悪材料: 確認できず。

## DDOG（候補）
- 10/30 −11.5〜−12%: サイバー・ソフト株の下げ（CrowdStrike−4%、Palo Alto・Fortinet−3%。Binance 63億ドルのハッキング話題、24/7 Wall St. 10/30）。10/29にもWells Fargoが維持するも−5.5%（AlphaStreet 10/29）。
- 次回決算: 11/4 寄り付き前、電話会議8:00 ET（Datadog公式発表 10/14、Finviz経由）。8月ガイダンスEPS 0.63〜0.65ドル（予想0.52）。
- 悪材料: 確認できず（決算前のソフト株売りの波及）。

## FTNT（候補）
- 10/28決算後に急落: サービス売上の見通しが予想未達（Yahoo Finance 10/29）、2日間の下げは過去最大級（Barron's 10/29）。10/30は −2.2%。
- 悪材料: あり（サービス売上ガイダンス未達）。

## 監視外の注目銘柄
- APA・COP・TRGP（エネルギー）: 原油高が背景。Trumpがイランを再攻撃と発言した際にAPA +4.7%、COP +3.6%の報道（Stockopedia、日付不明）。ConocoPhillipsが原油高で上場来高値との報道（goldesel.de、日付不明）。10/30当日の個別材料は確認できず。TRGPは材料なし。10/30は Exxon 関連の言及あり（Barron's 10/30）。
- LLY: 10/23頃から1週で約10%上昇し52週高値、Goldman Sachsが目標株価を1,413ドルに引き上げ（TIKR、日付は10/下旬）。Q3決算は10/29予定（検索結果）。10/30当日の値動きの原因は確認できず。
- AMGN: 原因となる見出しは見つからなかった（製薬・ヘルスケア全般が上げ、業種表で Drug Manufacturers 1週+6.2%）。

## 保有・候補以外のテーマ関連
- RDDT −29.2%: 弱い見通し、GoogleのAI検索がトラフィックを圧迫（CNBC・Reuters 10/30）。
- NOW: 10/28決算で売上見通しがAI懸念を再燃、翌日−18%台（Bloomberg 10/28、Yahoo Finance 10/29）。
- COHR・LITE・ANET・CIEN: ハイパースケーラーの設備投資懸念で光学株が下落（24/7 Wall St. 10/30）。
- 大手AI関連: BBC「AI支出が1兆ドルに迫る」(10/30)。TechCrunch「AI投資ブームにひび」(10/30)。Kioxia 2.2兆円の最高益でも株価下落（ANN 10/30）。
- ミネルヴィニの候補・保有銘柄はなし。決算評価は対象外。

# ニュースの見出し（プログラムが自動で取得）

- Googleニュース（日付を指定）とYahooファイナンスの見出しを `tools/news_headlines.py` が自動で並べたもの。日付は米国東部時間の配信日（引け後の記事は翌日付）。原因の判断・売買の判断はしていない。
- 調べた銘柄の選び方: ①保有 ②今日の候補 ③時間外に±5%以上動いた監視銘柄 は全部、④引けまでに大きく動いた銘柄（1週で±5%のグループの上位3・1日で±7%）は合計12銘柄まで。
- 1週で−5%以下のグループ: AIソフト・セキュリティ・ITサービス（-5.8%）
- 1週で+5%以上のグループ: なし

## 0. 時間外（引け後）の値動き（2026-10-30 の引けから、Yahoo。±3%以上の監視銘柄と、保有・候補は全部）

| 銘柄 | 区分 | 引け | 時間外 | 騰落率 |
|---|---|---|---|---|
| MRVL | 候補 | 196.40 | 197.91（19:59 ET） | +0.8% |
| SNDK | 保有 | 1150.12 | 1157.58（19:59 ET） | +0.7% |
| AMD | 保有 | 505.18 | 508.22（19:59 ET） | +0.6% |
| NTAP | 候補 | 199.25 | 198.40（17:53 ET） | -0.4% |
| FTNT | 候補 | 136.08 | 136.44（19:57 ET） | +0.3% |
| DDOG | 候補 | 235.35 | 235.87（18:54 ET） | +0.2% |
| DELL | 候補 | 423.93 | 424.18（19:59 ET） | +0.1% |

## 1. 市場全体（2026-10-30）

### 市場全体（英語のまとめ記事）
検索語: `stocks Wall Street close Nasdaq`
- 10/30 Reuters | Wall Street closes sharply lower as AI cash burn fears spark tech selloff
- 10/30 NBC News | Tech stocks wipe out $1 trillion in value as concerns deepen about the AI boom
- 10/30 CBS News | Nasdaq sheds more than 700 points as jittery investors pull back from tech stocks
- 10/30 The New York Times | Tech Stocks See Worst Day Since June, Pressuring Broader Market
- 10/31 24/7 Wall St. | The Nasdaq 100 Briefly Fell Into a Correction as the AI Trade Cracks

### 市場全体（Stock Market Today）
検索語: `"stock market today"`
- 10/30 Business Insider | Nasdaq 100 plunges more than 3% to cap its worst month since 2025 after dismal tech earnings
- 10/30 Yahoo Finance | US Stock Market Today: S&P 500 Futures Drop On Energy Inflation And Wage Risks
- 10/30 Yahoo Finance | Stock Market Today: Nasdaq, S&P 500 Futures Slide as Amazon and Intel Plunge After Earnings
- 10/30 Yahoo Finance | US Stock Futures Fall As AMZN, INTC Earnings Trigger Tech Sell-Off: NVDA, RDDT, RIVN, SFM In Focus
- 10/31 Yahoo Finance | Why Intel (INTC) stock is trading lower today

### 市場全体（日本語のまとめ記事）
検索語: `米国株式市場 OR NY株`
- 10/30 Reuters | 米国株式市場＝急落、ナスダックは6月以来の下落率 ＡＩ投資に懸念 | ロイター
- 10/30 野村證券 | エヌビディア、好決算でも時間外で株価下落 米国株式市場への影響と今後の注目点 野村證券・村山誠
- 10/30 産経ニュース | NY株が4営業日ぶりに反落、132ドル安 AI関連銘柄の大きな売りが重荷
- 10/30 ニューズウィーク日本版 | 米国株式市場＝急落、ナスダックは6月以来の下落率 ＡＩ投資に懸念
- 10/31 株探 | 米国株式市場見通し：中間選挙後も当面は中東情勢の変化などリスク要因残る

### 半導体・AI株（英語）
検索語: `chip stocks OR semiconductor stocks OR AI stocks`
- 10/30 Yahoo Finance | 'Worrisome': Jim Cramer warns chip stocks have gone 'parabolic' — here are the defensive moves he's making now
- 10/30 Investor's Business Daily | Chip Stocks Plunge After Intel’s Q4 Warning
- 10/30 BBC | US tech stocks see sharp falls as AI spending nears $1tn
- 10/30 Bloomberg.com | Big Tech’s Deepening AI Funding Concerns Sink Asian Chip Stocks
- 10/30 24/7 Wall St. | If AI Spending Slows in 2027, These Semiconductor Stocks Could Hold Up Best

### 信用（社債・借金）
検索語: `AI debt OR bonds OR credit spreads OR CDS`
- 10/30 Bloomberg.com | AI Debt Drives Wedge Between Corporate Bonds and Credit Hedges
- 10/31 Yahoo Finance UK | AI investors rush to hedge against potential tech market downturn - WSJ
- 10/31 The Dark Side Of The Boom | The AI Credit Default Trade Has Arrived: Barclays Maps the Next Fault Lines in Wall Street's Financing Boom
- 10/31 BigGo Finance | Wall Street's AI Trade Gets a Hedge: Put Options, CDS and Even Chip-Rental Derivatives
- 10/31 Action Forex | AI Sell-Off Spreads Beyond Tech as Credit Risks Rise — Is a Deeper Market Correction Building?

### 「〇〇ショック」の呼び名（日本語）
検索語: `ショック 株`
- 10/30 日本経済新聞 | 際立つApple株の安定感 コアウィーブ・ショック後の「安全資産」に
- 10/30 野村證券 | 金利上昇懸念で不動産株が急落 行き過ぎ感も、銀行株には追い風期待 野村證券ストラテジストが解説
- 10/30 東洋経済オンライン | コアウィーブ･ショックに金利上昇…10月に大きく下げた日経平均株価の行方とアメリカ中間選挙後の焦点
- 10/30 トウシル | ［動画］米中間選挙後の米国株市場 経験則（アノマリー）は今回も通用するか？
- 10/31 マネーフォワード | コアウィーブショックは氷山の一角──AI相場が問われ始めた「お金の問題」

### 引け後・時間外の動き（英語）
検索語: `"after hours" OR "after the bell" OR "extended trading" stocks`
- 10/30 Yahoo Finance | Okta jumps after-hours following tapped inclusion in the S&P 500
- 10/30 Euronext Markets: Real-time Stock Market Data | live | Intel shares tumble after hours, hit by chip supply constraints, big cash burn
- 10/30 Investing.com | Erste Group initiates Nasdaq stock with buy on extended trading
- 10/30 Yahoo Finance | PGEN Stock Craters 27% After-Hours After Rival Inovio's Rare Disease Drug Receives FDA Approval
- 10/30 BeInCrypto | Amazon's After-Hours Drop Leaves It Below Wall Street's Lowest Price Target
- 10/30 Investing.com | Amazon shares drop as holiday forecast misses Wall Street targets
- 10/30 Gotrade | Intel Plunges 21% on Weak PC Guidance, Chip Stocks Sell Off
- 10/31 BigGo Finance | US Stock Futures Fall Across the Board After Hours; Nasdaq Futures Plunge 3.45% as Memory Chip Stocks Buck the Trend

### 引け後・時間外の動き（日本語）
検索語: `時間外 決算 株`
- 10/30 野村證券 | エヌビディア・セールスフォース決算通過 AI半導体市場へのインプリケーション 野村證券・村山誠
- 10/30 株探 | サンディスク、好決算も時間外で９％安＝米国株個別
- 10/30 Yahoo!ファイナンス | サンディスク、好決算も時間外で９％安＝米国株個別(株探ニュース)
- 10/30 Yahoo!ファイナンス | インテル、決算受け時間外で２５％安＝米国株個別(株探ニュース)
- 10/30 Yahoo!ファイナンス | アマゾン、決算受け時間外で７％安＝米国株個別(株探ニュース)
- 10/30 Yahoo!ニュース | インテル株が決算受け「29％急落」、AI投資への懸念でハイテク株売りが加速
- 10/30 Yahoo!ニュース | キオクシア2.2兆円最高益も株価大きく下落 専門家「市場の期待を満たすことが難しい」（テレビ朝日系（ANN））

### 買収・合併（英語）
検索語: `acquisition OR acquire OR merger OR takeover chip OR semiconductor OR AI OR optical`
- 10/30 The Verge | All the drama around AI’s takeover of mathematics
- 10/30 FF News | Intuit to Acquire Sequence: Boosting AI-Native Revenue Management for Mid-Market Businesses
- 10/30 Gadget Review | Nvidia’s $13 Billion AI Takeover Reportedly Has the Justice Department Asking Questions
- 10/30 9to5Mac | Apple acquires Ascend․io, an agentic AI engineering startup
- 10/30 Yahoo Finance | Salesforce to Acquire Defense Tech Firm Rune Technologies to Expand Military AI Logistics Capabilities
- 10/31 Yahoo Finance | Lumentum Jumped on Reports Marvell Is in Late-Stage Talks to Acquire the Company. LITE Stock Is a Buy No Matter What.
- 10/31 https://tech-insider.org/ | SpaceX-Tesla Merger: 50% Hurdle, Not a Chip Fab [2026]
- 10/31 remio | Dark Matter House Numbers Acquisition Brings AI Agents Deeper Into Mortgage Workflows

## 2. 保有・候補・時間外で大きく動いた銘柄（2026-10-24〜2026-10-30 の見出し）

### SNDK（Sandisk Corporation、保有、AIサーバー・ストレージ・メモリ・端末、前日比 -13.5%、1週 -7.0%、時間外 +0.7%）

#### Googleニュース
検索語: `Sandisk stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 10/30 Yahoo Finance | Sandisk tops Q1 estimates and guides higher, sets 8-for-1 stock split
- 10/30 24/7 Wall St. | Sandisk Sinks 9% Despite Earnings Beat, Raised Guidance and 8-for-1 Split; Western Digital Tumbles 8%, Seagate Slides 7%, Micron Falls 6%
- 10/30 TradingPedia | SanDisk Stock Falls as Investors Question Earnings Quality
- 10/30 Yahoo Finance | SanDisk stock tumbles as Kioxia warns on NAND price surge

#### Yahooファイナンス
検索語: `SNDK`
- 10/30 Investor's Business Daily | Stock Market Today: Nasdaq Slumps On Weak Intel Report; NetApp Gives Sell Signal
- 10/31 Motley Fool | Sandisk Is Splitting Its Stock 8-for-1. History Says What Usually Happens to Stocks After a Split Announcement.
- 10/31 Motley Fool | Sandisk: 3 Key Takeaways for Long-Term Investors

### AMD（Advanced Micro Devices, Inc.、保有、半導体、前日比 -10.9%、1週 -2.3%、時間外 +0.6%）

#### Googleニュース
検索語: `Advanced Micro Devices stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 10/26 Yahoo Finance | Advanced Micro Devices (AMD) Rises Higher Than Market: Key Facts
- 10/27 Investing.com | Why is Advanced Micro Devices stock rallying today?
- 10/30 Seeking Alpha | Advanced Micro Devices slides 13% as part of tech selloff (AMD:NASDAQ)
- 10/30 MarketWatch | AMD’s stock slides after Intel earnings reveal two big issues

#### Yahooファイナンス
検索語: `AMD`
- 10/31 24/7 Wall St. | Intel Is Down 45% in October, Its Worst Month Ever
- 10/31 Barchart | What to Expect From AMD’s Q3 Earnings
- 10/31 Motley Fool | Intel Has a Massive Warning for AMD Stock Investors. Is It Time to Book Profits Before Nov. 3?

### DELL（Dell Technologies Inc.、候補、AIサーバー・ストレージ・メモリ・端末、前日比 -10.8%、1週 -7.0%、時間外 +0.1%）

#### Googleニュース
検索語: `Dell stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 10/29 Yahoo Finance | HPQ, DELL Stocks Plunge After Intel Flags Prolonged PC Market Weakness
- 10/29 MarketWatch | Dell Technologies Inc. Cl C stock falls Thursday, underperforms market
- 10/29 Trefis | Has Buying Dell Stock’s Dips Paid Off?
- 10/30 24/7 Wall St. | Dell Sinks 11% as Intel's Warning on PC Slump and Memory Shortage Hits Hardware Stocks; HP Tumbles 9%, Hewlett Packard Enterprise and Super Micro Fall 7%

#### Yahooファイナンス
検索語: `DELL`
- 10/30 Barrons.com | Intel, Amazon, Nvidia, ExxonMobil, Sandisk, FedEx Freight, and More Stocks That Explain Today’s Market
- 10/30 Barrons.com | Intel’s Earnings Disaster Spreads Across the Sector

### MRVL（Marvell Technology, Inc.、候補、半導体、前日比 -10.0%、1週 -14.1%、時間外 +0.8%）

#### Googleニュース
検索語: `Marvell stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 10/28 Investing.com | Why is Marvell Technology stock sliding today?
- 10/29 Yahoo Finance | Why Is Marvell Technology Stock Falling 9.5% in Premarket Trading?
- 10/29 Barron's | Marvell Stock Slides. Why the Market Hates the Idea of a Lumentum Buyout.
- 10/29 The Motley Fool | Why Marvell Stock Is Down Today

#### Yahooファイナンス
検索語: `MRVL`
- 10/30 24/7 Wall St. | 8 Months Ago, A Major Wall Street Bank Said Buy Marvell. It’s Up More Than 150%. Here’s Where We See the Stock Going
- 10/30 GuruFocus.com | Marvell-Lumentum Deal Reportedly Would Carry Limited Premium
- 10/30 TheStreet | Marvell may buy its own laser supplier as investors pull back

### NTAP（NetApp, Inc.、候補、AIサーバー・ストレージ・メモリ・端末、前日比 -8.8%、1週 -7.6%、時間外 -0.4%）

#### Googleニュース
検索語: `NetApp stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 10/26 Yahoo Finance | NetApp (NTAP) stock is up, what you need to know
- 10/27 Trefis | Would You Have Held NetApp Stock All The Way Up?
- 10/27 Forbes | NetApp
- 10/29 Yahoo Finance | Investors Heavily Search NetApp, Inc. (NTAP): Here is What You Need to Know

#### Yahooファイナンス
検索語: `NTAP`
- 10/29 24/7 Wall St. | Western Digital Plummted 20% in The Last 3 Months: Two Wall Street Ratings Firms Expect Nearly 130% Returns Within 12 Months
- 10/29 Trefis | Western Digital Stock Tripled: What Changed And What Did Not?

### DDOG（Datadog, Inc.、候補、AIソフト・セキュリティ・ITサービス、前日比 -11.5%、1週 -12.7%、時間外 +0.2%）

#### Googleニュース
検索語: `Datadog stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 10/26 Yahoo Finance | Datadog Set for 'Strong' Q3 Results, Oppenheimer Says
- 10/27 Investing.com | Why is Datadog stock slipping today?
- 10/29 AlphaStreet | Why Datadog Is Dropping 5.5%: Wells Fargo Maintains Overweight
- 10/30 Benzinga | Datadog Inc (DDOG) Stock Price, Quote, News & History

#### Yahooファイナンス
検索語: `DDOG`
- 10/30 24/7 Wall St. | Datadog Sinks 12%, CrowdStrike Falls 4% Despite $6.3 Billion Binance Hack Spotlighting Cyber Defense; Palo Alto and Fortinet Slide 3%
- 10/30 GuruFocus.com | iShares Russell Mid-Cap ETF (IWR) Adds Marathon Petroleum and Snowflake on Oct. 28
- 10/30 Motley Fool | Axon Enterprise vs. Datadog: Does Physical Security or Cyber Security Make for a Better Stock Buy in 2026?

### FTNT（Fortinet, Inc.、候補、AIソフト・セキュリティ・ITサービス、前日比 -2.2%、1週 -24.4%、時間外 +0.3%）

#### Googleニュース
検索語: `Fortinet stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 10/28 Investing.com | Why is Fortinet stock plunging today?
- 10/28 MarketWatch | Fortinet’s stock is taking a dive after earnings. Here’s why.
- 10/29 Yahoo Finance | Fortinet drags down cybersecurity stocks as the company's service revenue forecast misses estimates
- 10/29 Barron's | Fortinet Stock Heads for Record Two-Day Rout. A Key Revenue Driver May Be to Blame.

#### Yahooファイナンス
検索語: `FTNT`
- 10/30 GlobeNewswire | Virtualization Security - Capitalize on a 16.5% CAGR to Secure the US$4.9 Billion 2032 Market as Cisco, Fortinet, Checkpoint, Dell EMC, and Huawei Disrupt Defenses
- 10/30 Insider Monkey | Darktrace and Fortinet Strengthen Climb Global’s (CLMB) Growth Profile

## 3. 引けまでに大きく下げた銘柄（2026-10-24〜2026-10-30 の見出し）

### RDDT（Reddit, Inc.、AIソフト・セキュリティ・ITサービス、前日比 -29.2%、1週 -36.4%、時間外 +0.6%）

#### Googleニュース
検索語: `Reddit stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 10/30 CNBC | Reddit stock plunges 29% after weak outlook, wrapping its worst day ever
- 10/30 Reuters | Reddit shares plunge as Google's AI search squeezes traffic
- 10/30 Investor's Business Daily | Why Reddit Stock Is Tumbling Toward Its Worst Single Day Decline
- 10/31 Yahoo Finance | Why Reddit (RDDT) stock is trading lower today

#### Yahooファイナンス
検索語: `RDDT`
- 10/31 Barchart | Reddit Sinks as Google's AI Shift Takes a Bite Out of Search Traffic. What's Next for RDDT Stock.
- 10/31 Insider Monkey | 5 Best High Growth Stocks Outside Big Tech
- 10/31 Simply Wall St. | 3 AI Infrastructure Stocks Retail Investors Are Watching After Google Search Shift

### NOW（ServiceNow, Inc.、AIソフト・セキュリティ・ITサービス、前日比 -4.1%、1週 -33.9%、時間外 +0.2%）

#### Googleニュース
検索語: `ServiceNow stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 10/28 Bloomberg.com | ServiceNow Falls After Quarterly Sales Outlook Revives AI Fears
- 10/28 MarketWatch | ServiceNow’s stock slides as earnings miss overshadows a raised AI outlook
- 10/29 Yahoo Finance | Why Is ServiceNow Stock Falling 18.7% in Premarket Trading?
- 10/29 Investing.com | ServiceNow stock tumbles after earnings: Buy the dip or stay put?

#### Yahooファイナンス
検索語: `NOW`
- 10/31 GuruFocus.com | InfoBeans Technologies Ltd (NSE:INFOBEAN) (Q2 2027) Earnings Call Highlights: 22% Constant ...
- 10/31 Simply Wall St. | 3 AI Stocks With Earnings Growth Over 30%
- 10/31 Simply Wall St. | 3 Cybersecurity Stocks Investors May Revisit After The Binance Hack

### INTC（Intel Corporation、半導体、前日比 -28.6%、1週 -24.4%、時間外 -1.5%）

#### Googleニュース
検索語: `Intel stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 10/29 CNBC | Intel stock plunges 21% as chipmaker blames PC slowdown for weak guidance
- 10/29 Financial Times | Intel shares fall 22% as weak sales outlook dents turnaround
- 10/30 Yahoo Finance | Intel stock plunges nearly 29%, its worst day since 1974
- 10/30 Bloomberg | Intel Suffers Worst Stock Thrashing in Decades on Weak Forecast

#### Yahooファイナンス
検索語: `INTC`
- （新しい見出しなし）

### COHR（Coherent Corp.、光・通信・ネットワーク、前日比 -11.3%、1週 +0.5%、時間外 +1.1%）

#### Googleニュース
検索語: `Coherent stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 10/26 StreetInsider | Coherent stock jumps on new buy rating from StoneX and sector strength
- 10/29 Investing.com | Why is Coherent stock gaining today?
- 10/30 24/7 Wall St. | Applied Optoelectronics Plunges 15%, Coherent Tumbles 13% as Hyperscaler Spending Fears Hit AI Optics Stocks; Lumentum and Marvell Sink 10%
- 10/31 Yahoo Finance | Coherent Stock Fell 11% as Intel and Amazon Earnings Hit AI Hardware Stocks. Here’s Where the Stock Could Go

#### Yahooファイナンス
検索語: `COHR`
- 10/29 Investor's Business Daily | Lumentum Jumps, Fades On Marvell Buyout Report
- 10/29 Simply Wall St. | Coherent (COHR) Stock May Be About Right As Analyst Interest Builds
- 10/29 TIKR | AXT Soars 10% on $545 Million Tongmei Financing as Indium Phosphide Demand Is “Outpacing Supply”

### QCOM（QUALCOMM Incorporated、半導体、前日比 -11.1%、1週 -6.3%、時間外 +0.2%）

#### Googleニュース
検索語: `QUALCOMM stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 10/26 Yahoo Finance | Qualcomm (QCOM) Laps the Stock Market: Here's Why
- 10/30 Investing.com | Why is Qualcomm stock tumbling today?
- 10/30 Seeking Alpha | QUALCOMM drops 12% as tech stocks fall (QCOM:NASDAQ)
- 10/30 24/7 Wall St. | Broadcom Falls 5% Despite DA Davidson Upgrade on Anthropic and OpenAI IPO Hopes; Arm and Qualcomm Sink 10%, Marvell Drops 8%

#### Yahooファイナンス
検索語: `QCOM`
- 10/30 Barchart | Qualcomm Is Teaming Up With Anduril to Produce U.S.-Made Laptops. Don’t Expect It to Move the Needle for QCOM Stock.
- 10/30 TechCrunch | Cracks are emerging in the AI spending boom
