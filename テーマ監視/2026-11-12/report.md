# テーマ監視 2026-11-11

# 判定のまとめ（ルールの判定と著者の判定を分けて表示）

- **ルールの判定**: 採用した売買ルール（スクリプト）が数値で決めたもの。損切りは買値の15%下の逆指値（日中に届けばその場で売れる）。
- **著者の判定**: ノートブックの著者の回答。買いは注文を止める理由があるときだけ【様子見】、保有はルールより早く手じまう理由があるときだけ【売り】。根拠は下の「著者の回答（全文）」。
- 2つが食い違うときに、どちらに従うかはユーザーが決める。

- **テーマ全体の急落（S2・記録だけ）: あり（S2）**（SOXが直近60取引日の最高値から -20.1%）。S2の日の順張りの候補には「S2なら見送る形」と付ける（売買のルールは変えない。記録してから採用を決める。2026-10-14）

- **特殊な下げ（記録だけ）: あり（特殊な下げ）**（2026-10-16から）（SOXが直近60取引日の最高値から -20.1%、前の1年の大きな上げ・雇用の弱さ・物価の再加速のうち 2つ）。1995年〜では、この形の後にSOXの下げが長引くことが多かった（後知恵を含む）。売買のルールは変えない（2026-11-03）

## 保有銘柄

| 銘柄 | ルール | 損益 | 時間外 | ルールの判定 | ルールの判定の理由 | 著者の判定 |
|---|---|---|---|---|---|---|
| SNDK | ルール外（ユーザーの判断。この日はどのルールの合図もなし） | -28.7% | -0.0% | **売り** | 終値 977.69 が損切り価格 1165.61 以下 | 【未判定】（） |
| AMD | ボリンジャーIII | +0.5% | +1.4% | 保有継続 | 損切り 467.47（終値から -15.5%） | 【保有継続】（ボリンジャー） |

## 候補の判定（並びは上の「買う順番」の表と同じ）

- 並びは上の「買う順番」の表と同じ（RSの高い順。勝率の高い順ではない）。注文の値段・株数・逆指値は上の表を見る。勝率・1回平均は、そのルールの過去の成績（後知恵なしの監視銘柄・2015年〜の全部の合図）。
- 空き枠: 3（同時保有4銘柄まで。保有2、うちルールの売り1）。著者が【様子見】の候補を見送るかはユーザーが決める。

| 順 | 銘柄 | ルール | 過去の勝率 | 過去の1回平均 | RS | 時間外 | ルールの判定 | 著者の判定 |
|---|---|---|---|---|---|---|---|---|
| 1 | NVDA（エヌビディア） | 逆張り: 急落の底（担当: コナーズ）（指値の2日目） | 65% | +2.1% | 7 | -3.9% | 買い（指値 165.51、3取引日まで） | 【様子見】（コナーズ） |

- 時間外: 前の取引日の引けから、引け後（米国東部時間16〜20時）の最後の値までの騰落率（Yahoo。±5%以上は太字）。寄り付きの値段は、表の注文の目安（前日の終値で計算）から大きくずれることがある。原因の見出しは「ニュースの見出し」の節。

# 著者の回答（全文）

## 0_テーマの局面_ワインスタイン

1. **テーマ全体の局面**: 【ステージ3】（上昇後に30週移動平均線が水平化し、指数が線を下回る典型的な天井圏 [1, 2]、第2章）

2. **グループごとの局面**:
- 半導体｜ステージ3｜30週線横ばい・線の下 [1]
- 半導体製造装置・材料・設計ソフト・計測｜ステージ3｜30週線横ばい・線の下 [1]
- AIサーバー・ストレージ・メモリ・端末｜ステージ3｜30週線横ばい・線の下 [1]
- 光・通信・ネットワーク｜ステージ3｜30週線横ばい・線の下 [1]
- データセンターの電力・冷却・部品・受託製造・建設｜ステージ3｜30週線横ばい・線の下 [1]
- AIプラットフォーム・クラウド｜ステージ3｜30週線横ばい・線近辺 [1]
- AIソフト・セキュリティ・ITサービス｜ステージ2｜30週線上昇・線の上 [3]

3. **転換の兆し**:
出ている。30週線の上昇モメンタム消失・水平化と線の下への沈下（-5.8%） [1, 4]（第2章、第6章）、および対S&P500の相対力（RS）の悪化 [5, 6]（第4章）が天井形成（ステージ3）の明確な兆候に該当する。なお、ニュース件数、独自の急落基準（S2）、マクロ経済指標（雇用・物価）はマニュアルに規定なし。

4. **テーマの外**:
**判定不能**（ヒートマップのデータが省略されており情報がないため「なし」）

（全体の版が空の応答だったため、1〜2節だけの短い版で送り直した回答。ヒートマップ・急騰急落・ニュースは渡していない）

## 1_コナーズ_prompt_1

## NVDA
1. **投資判断**: 【様子見】（200日移動平均線の下にあるため）
2. **止める理由の確認**:
   - 本が禁じる形・状況｜あり｜第4章（p.10）ルール3「株は200日移動平均線の上側で買い、下側で買ってはならない」 [1]
   - 避けるべき時期（決算など）｜なし｜マニュアルに規定なし（決算回避の規定なし。時期の否定は月初3〜8日のみ、第11章p.28） [2]
   - 悪材料｜なし｜マニュアルに規定なし（悪材料による急落・悲観は大衆心理の逆を行く買い対象、第2章p.8・第3章p.9） [3, 4]
3. **現状パターンと価格**:
   - 現状パターン: A（シグナル成立だが200日線違反）
   - 本日の発注: 見送り（発注なし）
4. **注意点**: 株価が200日線を下回った場合は、すべてを白紙に戻して仕切り直す必要があります [1]。

## 1_ボリンジャー_prompt_1

## AMD
1. **投資判断**: 【保有継続】（早期手じまいの根拠なし）[1]
2. **止める理由の確認**:
- 本が禁じる形・状況｜なし｜天井や弱気乖離なし（第13・20章）[1]
- 避けるべき時期（決算など）｜なし｜次回決算2027-02-02（規定なし）[2]
- 悪材料｜なし｜直近材料なし（第15章/23_用語集）[3]
3. **現状パターンと価格**:
- 売りの予約注文: 指値売り 602.22（現在値比 +8.9%）[1]
4. **注意点**: 上部バンド接触時の指標乖離に注意（第17章）[1]

# スキャン（数値と事実）


- 監視銘柄 87（判定できたのは 87）。
- この一覧は数値と事実だけ。売買の判断は著者のノートブックが行う。

## 1. テーマ（グループ）の強さ

| グループ | 銘柄数 | 1週 | 1カ月 | 3カ月 | 3カ月の順位 | 50日線より上の銘柄の割合 | グループ指数の30週線の局面（線との乖離、4週前からの線の傾き） |
|---|---|---|---|---|---|---|---|
| 半導体 | 16 | +3.4% | -4.0% | -9.7% | 4位 | 38% | 横ばい（-5.8%、+4.9%） |
| 半導体製造装置・材料・設計ソフト・計測 | 9 | +6.5% | -12.5% | -16.9% | 5位 | 33% | 横ばい（-10.6%、+1.2%） |
| AIサーバー・ストレージ・メモリ・端末 | 9 | -1.0% | -23.4% | -22.3% | 6位 | 11% | 横ばい（-6.1%、+6.6%） |
| 光・通信・ネットワーク | 9 | +3.4% | -18.9% | -23.9% | 7位 | 22% | 横ばい（-11.4%、+1.2%） |
| データセンターの電力・冷却・部品・受託製造・建設 | 19 | +1.2% | -7.7% | -9.6% | 3位 | 26% | 横ばい（-7.3%、+0.5%） |
| AIプラットフォーム・クラウド | 11 | +1.5% | -10.3% | +0.4% | 1位 | 45% | 横ばい（-0.2%、+1.4%） |
| AIソフト・セキュリティ・ITサービス | 14 | -3.9% | -8.4% | -5.8% | 2位 | 29% | 上昇（+7.9%、+4.9%） |

## 2. テーマ全体の状態と早めの警告

- 市場全体の30週線による局面: S&P500指数 **上昇**／NASDAQ100指数 **横ばい**（急落の底で買うルールは、過去の検証で下落相場で特に強く、横ばいの相場では負けていた）
- **2倍ETFを使う局面（案1、2026-10-13 採用）: S&P500の20週線（100日線）で 上昇** → 2倍ETFのある銘柄は2倍ETFで買う（SPY 759.81、100日線 758.69、20日前の線 755.37。上昇＝線より上かつ線が上向き）
- **テーマ全体の急落（S2、記録だけ。売買のルールは変えない）: あり（S2）**（SOX 10564.11、直近60取引日の最高値 13217.82 から -20.1%。S2＝最高値から−10%以上）。S2のときに「順張りの新しい買いだけ止める」形を記録で比べる（2026-10-14 ユーザー決定。バックテストでは年率は上がったが2つの期間ではどちらも少し下回ったため、記録してから採用を決める。`バックテスト結果/テーマ全体の急落を検知して手じまう・買いを止める.md`）
- **グループごとの悪いニュースの流れ（記録だけ。売買のルールは変えない。2026-10-29〜2026-11-11）**: 会社の名前と悪い言葉（格下げ・目標株価の引き下げ・見通しの引き下げ・予想未達・急落・信用・訴訟・輸出規制など）の両方がある見出しの数（Googleニュース、`tools/news_headlines.py`）。10取引日の1銘柄あたりが一番多いグループに印。2026年7〜11月の確かめでは、印のグループの合図は10月は成績が悪かった（1回平均 −10.6%、ほか −5.6%）が、7〜9月は逆に良かった（+11.6%、ほか +6.7%）（`バックテスト結果/実際の運用の期間の確認_2026-10-23/グループの悪いニュースの流れ.md`。2026-11-04）

| グループ | 悪いニュース 直近5取引日 | その前の5取引日 | 10取引日の1銘柄あたり | 良いニュース 10取引日（1銘柄あたり） | 印 |
|---|---|---|---|---|---|
| 半導体（16） | 43件 | 8件 | 3.2 | 28件（1.8） | **悪いニュースが続いている** |
| 光・通信・ネットワーク（9） | 16件 | 11件 | 3.0 | 9件（1.0） |  |
| AIサーバー・ストレージ・メモリ・端末（9） | 5件 | 5件 | 1.1 | 41件（4.6） | **良いニュースが多い** |
| AIプラットフォーム・クラウド（11） | 2件 | 7件 | 0.8 | 2件（0.2） |  |
| AIソフト・セキュリティ・ITサービス（14） | 1件 | 6件 | 0.5 | 11件（0.8） |  |
| 半導体製造装置・材料・設計ソフト・計測（9） | 1件 | 2件 | 0.3 | 1件（0.1） |  |
| データセンターの電力・冷却・部品・受託製造・建設（19） | 1件 | 4件 | 0.3 | 19件（1.0） |  |

印のグループ（半導体）の最近の見出し: 2026-11-11 Nvidia's Confidence Test: CoreWeave's Blowout Forecast, Baird's Downgrade and a Boardroom Inquiry Al（ad-hoc-news.de）／2026-11-11 Nvidia stock gets a rare Wall Street downgrade on supply issues（Yahoo Finance）／2026-11-11 Nvidia downgraded, Mercury Systems upgraded: Wall Street's top analyst calls（Yahoo Finance）

良いニュースが多いグループ（AIサーバー・ストレージ・メモリ・端末）の最近の見出し: 2026-11-11 Don’t Buy The New Apple TV! Upgrade Your Older Apple TV Instantly With the New Siri Remote Featuring Find My Remote For Just $59（| Cord Cutters News）／2026-11-11 Apple upgraded by China Renaissance with a new price target（Quantisnow）

- **特殊な下げ（記録だけ。売買のルールは変えない）: あり（特殊な下げ）**（2026-10-16から）。SOX は直近60取引日の最高値から -20.1%（−15%以下が条件）、●A 前の1年の上げ +111.5%（+80%以上）、・B 雇用の伸び 137千人/月（2026-10まで。10万人未満）、●C 物価 4.0%（2026-09。3か月前 3.7%。3.5%以上で再加速）＝2つ（2つ以上が条件）。1995年〜でSOXが−15%以下かつ条件2つ以上の日は、120日後にSOXが下だったのが69%・250日後が70%（中央値 −33%）、AI以外の8業種の平均は250日後 −7%。ただし条件は過去を見て選んだもの（条件が2つ以上の局面は約5回）で、2026年7〜9月にこの間テーマを買わないと、その後の戻りを逃して2026年の成績は下がった（`バックテスト結果/実際の運用の期間の確認_2026-10-23/特殊な下げと過去の似た下げ.md`。2026-11-03）
- テーマ指数（監視銘柄の等金額平均）の30週線による局面: **横ばい**（上昇＝線より上かつ上向き、下落＝線より下かつ下向き、それ以外＝横ばい。ワインスタインのステージの近似）
- テーマ指数と50日線: 50日線より下（乖離 -5.8%）
- S&P500に対する相対的な強さ: 50日平均より下（S&P500より弱い）
- 監視銘柄のうち50日線より上の割合: 30%
- 警告（割合が40%未満かつテーマ指数が50日線より下）: **出ている**
- 参考（バックテスト）: 30週線の「下落」は高値から10〜33%下げた後に出る遅い判定。50日線・割合・相対的な強さは高値から2〜8%で出るが、誤報が年15回以上ある。警告中に新しい買いを止めると、押し目買い（ボリンジャーIII）の成績は大きく下がった（`バックテスト結果/テーマ監視銘柄・直近3年.md` 11・12節）。

## 3. ヒートマップ（Finviz、全米の業種別の騰落率）

3カ月の騰落率の上位15業種（テーマの外で強くなっている業種の確認用）:

| 順位 | 業種 | 1週 | 1カ月 | 3カ月 | 6カ月 | 1年 |
|---|---|---|---|---|---|---|
| 1 | Health Information Services | -0.2% | +8.5% | +21.9% | +62.7% | +12.9% |
| 2 | Medical Distribution | +1.5% | +11.0% | +19.7% | +43.5% | +18.2% |
| 3 | Advertising Agencies | +31.4% | +35.3% | +19.3% | -4.5% | -29.9% |
| 4 | Lodging | +0.9% | +14.6% | +18.4% | +19.2% | +36.8% |
| 5 | Consumer Electronics | +1.8% | +4.3% | +16.3% | +18.8% | +29.4% |
| 6 | Paper & Paper Products | +2.4% | +11.7% | +16.3% | +11.0% | +6.9% |
| 7 | Diagnostics & Research | -1.0% | +5.5% | +15.9% | +52.7% | +24.5% |
| 8 | Insurance - Diversified | +1.4% | +12.5% | +14.7% | +20.2% | +18.2% |
| 9 | Medical Care Facilities | -0.6% | +9.7% | +13.9% | +21.6% | +23.7% |
| 10 | REIT - Hotel & Motel | +0.2% | +11.8% | +13.9% | +30.4% | +48.7% |
| 11 | Real Estate - Diversified | +3.6% | +11.7% | +13.9% | +18.4% | +8.9% |
| 12 | Financial Data & Stock Exchanges | -0.1% | +12.9% | +12.3% | +12.8% | +5.4% |
| 13 | Drug Manufacturers - General | -0.4% | +14.3% | +12.1% | +24.6% | +36.0% |
| 14 | Insurance - Reinsurance | +1.4% | +7.6% | +11.7% | +24.5% | +36.2% |
| 15 | Drug Manufacturers - Specialty & Generic | +0.8% | +9.5% | +11.5% | +11.1% | +19.9% |

テーマの業種の順位（3カ月、全144業種中）: Semiconductors 128位、Semiconductor Equipment & Materials 141位、Computer Hardware 143位、Communication Equipment 126位、Electronic Components 133位、Software - Infrastructure 68位、Software - Application 71位、Internet Content & Information 115位

## 4. 急騰・急落した銘柄（前日比±5%以上、または出来高が50日平均の2倍以上）

原因のニュースをサブエージェントが調べ、候補・保有銘柄の判定材料として著者に渡す。急騰・急落そのものは売買の合図にしない（後知恵のないS&P500全体のバックテストでは、急騰の翌日に買うルールは年率7%、急落の翌日に買うルールは年率9〜10%で、採用した3つのルールより優れていなかった）。

| 銘柄 | グループ | 前日比 | 出来高（50日平均の倍） | 終値 | 50日線 | RS | 局面 |
|---|---|---|---|---|---|---|---|
| CRWV | AIプラットフォーム・クラウド | +24.7% | 3.4倍 | 60.77 | 下 | 0 | 下落相場 |
| NBIS | AIプラットフォーム・クラウド | +15.4% | 2.0倍 | 154.69 | 下 | 38 | 下げ |
| SNDK | AIサーバー・ストレージ・メモリ・端末 | +13.7% | 1.6倍 | 977.69 | 下 | 96 | 下げ |
| ARM | 半導体 | +12.1% | 1.2倍 | 203.36 | 下 | 50 | 下げ |
| MU | 半導体 | +11.9% | 1.3倍 | 811.30 | 下 | 98 | 下げ |
| DELL | AIサーバー・ストレージ・メモリ・端末 | +11.8% | 1.1倍 | 373.68 | 下 | 99 | 下げ |
| LITE | 光・通信・ネットワーク | +10.7% | 1.2倍 | 648.06 | 下 | 70 | 下げ |
| STX | AIサーバー・ストレージ・メモリ・端末 | +10.0% | 1.5倍 | 551.72 | 下 | 38 | 下げ |
| SMCI | AIサーバー・ストレージ・メモリ・端末 | +9.5% | 1.0倍 | 30.43 | 下 | 8 | 下げ |
| MRVL | 半導体 | +9.3% | 1.4倍 | 168.80 | 下 | 88 | 下げ |
| COHR | 光・通信・ネットワーク | +9.2% | 1.4倍 | 234.51 | 下 | 13 | 下落相場 |
| MPWR | 半導体 | +8.9% | 1.2倍 | 1478.69 | 上 | 75 | レンジ |
| ORCL | AIプラットフォーム・クラウド | +8.8% | 1.0倍 | 128.38 | 下 | 2 | 下げ |
| CIEN | 光・通信・ネットワーク | +8.8% | 1.2倍 | 296.04 | 下 | 9 | 下落相場 |
| WDC | AIサーバー・ストレージ・メモリ・端末 | +8.3% | 0.9倍 | 313.31 | 下 | 26 | 下落相場 |
| TER | 半導体製造装置・材料・設計ソフト・計測 | +8.3% | 1.1倍 | 265.78 | 下 | 9 | 下落相場 |
| INTC | 半導体 | +7.5% | 1.1倍 | 62.50 | 下 | 19 | 下げ |
| GLW | 光・通信・ネットワーク | +7.4% | 1.1倍 | 120.46 | 下 | 11 | 下落相場 |
| AMD | 半導体 | +7.3% | 1.7倍 | 552.90 | 上 | 98 | 上昇相場 |
| RDDT | AIソフト・セキュリティ・ITサービス | +7.1% | 0.8倍 | 105.66 | 下 | 1 | 下落相場 |
| ALAB | 半導体 | +6.8% | 0.9倍 | 230.91 | 下 | 53 | 下げ |
| VRT | データセンターの電力・冷却・部品・受託製造・建設 | +6.3% | 1.1倍 | 206.51 | 下 | 5 | 下落相場 |
| ANET | 光・通信・ネットワーク | +6.3% | 1.3倍 | 196.68 | 上 | 83 | レンジ |
| LRCX | 半導体製造装置・材料・設計ソフト・計測 | +6.1% | 1.0倍 | 235.88 | 下 | 19 | 下落相場 |
| AMAT | 半導体製造装置・材料・設計ソフト・計測 | +6.1% | 1.0倍 | 395.08 | 下 | 46 | 下落相場 |
| SWKS | 半導体 | +6.0% | 0.5倍 | 87.64 | 上 | 91 | 上げ |
| ON | 半導体 | +5.8% | 0.8倍 | 73.62 | 下 | 32 | 下げ |
| KLAC | 半導体製造装置・材料・設計ソフト・計測 | +5.2% | 1.0倍 | 161.01 | 下 | 25 | 下落相場 |
| NVDA | 半導体 | +2.9% | 2.1倍 | 173.73 | 下 | 7 | 下げ |

- 局面（判定式はClaudeが置いたもの）: **上昇相場**＝終値 > 50日線 > 200日線、50日線が20取引日前より2%以上高い、ADX(14) ≧ 20／**下落相場**＝終値 < 50日線 < 200日線、50日線が20取引日前より2%以上低い、ADX(14) ≧ 20／**上げ**＝それ以外で終値が50日線より上、かつ50日線が10取引日前より上か20日線が5取引日前より上／**下げ**＝それ以外で終値が50日線より下、かつ50日線が10取引日前より下か20日線が5取引日前より下（急な下げの初めは50日線がまだ上向きのため20日線でも見る）／**レンジ**＝どれにも当たらない（2026-11-05 から5つ。それまでは上昇相場とレンジの2つだけで、下げている銘柄もレンジと出ていた）。

## 4-2. 監視外の注目銘柄（S&P500・NASDAQ100のうち監視銘柄に入っていない銘柄）

条件: 流動性（株価5ドル以上・50日平均出来高25万株以上）があり、(a) 前日比+8%以上かつ出来高が50日平均の2倍以上、または (b) 終値が直前1年の最高値（終値）を上回り、RS≧90。RSの高い順に5銘柄（ニュースを調べる）。監視銘柄に入れるかはユーザーが決める。

| 銘柄 | 種類 | 前日比 | 出来高（50日平均の倍） | RS | 終値 |
|---|---|---|---|---|---|
| HUM | 1年の高値更新 | +1.9% | 1.8倍 | 98 | 446.31 |
| VTRS | 1年の高値更新 | +1.0% | 1.6倍 | 97 | 21.06 |
| HAS | 1年の高値更新 | +1.8% | 0.8倍 | 95 | 124.02 |
| LLY | 1年の高値更新 | +0.3% | 0.7倍 | 94 | 1437.29 |
| KDP | 1年の高値更新 | +1.8% | 0.9倍 | 93 | 38.25 |

- ほかに5銘柄: AIZ（1年の高値更新、RS 92）、ABBV（1年の高値更新、RS 92）、CPAY（1年の高値更新、RS 92）、LH（1年の高値更新、RS 91）、CAH（1年の高値更新、RS 91）

## 5. 保有銘柄の手じまい条件（`新分析ツール/保有銘柄.md`）

| 銘柄 | ルール | 買った日 | 買値 | 終値 | 損益 | 損切り価格（買値の15%下、逆指値） | ルールの手じまい条件 | 出来高2倍の大陰線（買った後の直近5日） | 次回決算予定日 |
|---|---|---|---|---|---|---|---|---|---|
| SNDK | ルール外（ユーザーの判断。この日はどのルールの合図もなし） | 2026-10-21 | 1371.30 | 977.69 | -28.7% | 1165.61 | **損切り価格を下回った** ルールが不明（保有銘柄.md の「ルール」を確認） | **あり** 2026-11-05（実体 ATRの1.6倍・出来高3.3倍） | 2026-10-29 |
| AMD | ボリンジャーIII | 2026-10-21 | 549.97 | 552.90 | +0.5% | 467.47 | **出来高2倍の大陰線が 2026-11-05 に出た**（まだ持っていれば、次の寄り付きで全部売る） 売りの指値: 上部バンド 602.22（今夜この値に置き直す。届いた日に売れる）（2倍ETF AMUU で持っている場合も、判定は元の株 AMD の値段） | **あり** 2026-11-05（実体 ATRの1.5倍・出来高3.3倍） | 2027-02-02 |

- 出来高2倍の大陰線: 実体（始値−終値）が前日までのATR(14)の1.5倍以上、終値がその日の値幅の下25%以内、出来高が前日までの50日平均の2倍以上の日。**押し目（ボリンジャーIII）・急落の底の保有では売りのルール**: 出たら翌日の寄り付きで全部売り、空いた枠で次の合図を買う（2026-10-02 ユーザー決定。`バックテスト結果/やり直し_売りの合図の組み合わせ.md`。乱数3組とも年率が約+2ポイント、最大下落率もやや下がった）。ミネルヴィニ・新高値V2の保有では事実の表示（順張りに足しても良くならなかった）。

- 半分売りの合図（ミネルヴィニ・新高値V2の保有だけ）: 反転のローソク足（かぶせ線・弱気の包み足・宵の明星・流れ星）＋出来高が50日平均の1.5倍以上＋RSI(14)が前日か当日に70以上。買った後に最初に出た日の翌日の寄り付きで半分売り、残り半分は50日線割れ・損切り15%まで持つ（2026-10-01 ユーザー決定。`バックテスト結果/半分だけ売るとオニールの空き枠.md`）。

- かぶせ線（ミネルヴィニ・新高値V2の保有だけ）: 上昇中の陽線の翌日に、前日の高値より上で寄り付き、前日の陽線の真ん中より下（前日の始値より上）で引けた日。翌日の寄り付きで全部売り、空いた枠で次の合図を買う。半分売りより優先する（2026-10-01 ユーザー決定。`バックテスト結果/2倍ETFで売って買い直す.md`。順張りの売買の25%で出て、1回平均+2.0%、年率 21.4%→26.4%）。

## 5-2. 前日（2026-11-10の引け）の【買い（予約）】の確認

前日の【買い（予約）】はなし。

## 6. 候補（採用したルールの条件が成立＝A。予約（B）は2026-10-25から注文せず、節6-3に参考の表示だけ）

建玉の目安: 同時保有4銘柄まで、1銘柄に資金の25%（資金÷4）、損切りは買値の15%下（ユーザー決定 2026-09-29）。

パターン: A＝最新の足で採用ルールの条件が成立（押し目・ミネルヴィニ・新高値V2は翌日の寄り付きで成行、急落の底は合図の日の終値の2%下に指値で3取引日待つ。2026-11-03 ユーザー採用）。条件の成立が目前の銘柄（B）は、予約の注文をやめたので節6-3に参考として出す（2026-10-25 ユーザー決定）。

| 銘柄 | グループ | パターン | 種類 | ルールの過去の成績 | 終値 | 前日比 | RS | 50日線の傾き | 局面 | 当てはまった条件 | 次回決算予定日 | 注文の目安 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| NVDA | 半導体 | A | 逆張り: 急落の底（担当: コナーズ）（指値の2日目） | 2位（勝率65%・1回平均+2.1%） | 173.73 | +2.9% | 7 | -2.7% | 下げ | 2026-11-10の合図: 直前5日の最高値（終値）から-18.3%下落（−15%以上）、RSI(2)=7.8（≦10）、急落の前は50日線＞200日線。市場全体の局面: S&P500 上昇／NASDAQ100 横ばい。その後まだ指値に届かず、終値は5日線以下 | 2026-11-17（6日後）**決算が近い** | 指値買い 165.51（合図の日 2026-11-10 の終値 168.89 の2%下。今日から2取引日。届かなければ見送り、途中で終値が5日線を上回ったら取り消す）。損切り: 約定した値段の15%下。手じまい: 終値が5日線（今日 177.91）を上回った翌日の寄り付き（コナーズ）。**2倍ETFで買う: NVDU**（目減り 年10%。株と同じ金額。合図・損切り・手じまいは元の株 NVDA の値段で判定）。**株数の目安: NVDU 32株**（2,384ドル÷73.49）。**NVDUの注文: 指値買い 73.49、購入金額 約2,352ドル**（注文の価格をETFの値段に直した近似。損切りは約定したETFの値段の約30%下） |

- 局面（判定式はClaudeが置いたもの）: **上昇相場**＝終値 > 50日線 > 200日線、50日線が20取引日前より2%以上高い、ADX(14) ≧ 20／**下落相場**＝終値 < 50日線 < 200日線、50日線が20取引日前より2%以上低い、ADX(14) ≧ 20／**上げ**＝それ以外で終値が50日線より上、かつ50日線が10取引日前より上か20日線が5取引日前より上／**下げ**＝それ以外で終値が50日線より下、かつ50日線が10取引日前より下か20日線が5取引日前より下（急な下げの初めは50日線がまだ上向きのため20日線でも見る）／**レンジ**＝どれにも当たらない（2026-11-05 から5つ。それまでは上昇相場とレンジの2つだけで、下げている銘柄もレンジと出ていた）。

- 2倍ETF: 2倍ETFがある銘柄（ユーザーがムームー証券で買えることを確認した38銘柄のうち、目減りが年15%未満のもの）は、株の代わりに2倍ETFを買う（2026-10-04 ユーザー決定。`バックテスト結果/2倍ETFを使う決まり.md`。年率 約27%→約33%、確定した損益だけの最大下落率 約30%→約31%、含み損込みは約33%→約45%）。買う金額は株と同じ（資金の25%）。合図・損切り（元の株の買値の15%下＝ETFでは約30%下）・手じまいはすべて元の株の値段で判定する。指値・逆指値はETFの値段に直して置く。どのETFかは `新分析ツール/2倍ETFの対応表.json`（売買代金が1日500万ドル以上で、直近1年の目減りが一番小さいもの）。**2倍ETFで買うのは、S&P500が20週線（100日線）で「上昇」の局面のときだけ。横ばい・下落の局面では元の株で買う**（案1、2026-10-13 ユーザー採用。買う日に決め、買った後は局面が変わってもそのまま持つ。`バックテスト結果/流れ（市場の局面）を使う形.md`）。

- ルールの過去の成績: 今の売りのルールで、後知恵なしの監視銘柄・2015年〜の全部の合図の1回ごとの成績（2026-10-02計算、`新分析ツール/バックテスト結果/ルールごとの成績.md`）。順位は1回平均（1回の売買で平均いくら増えるか）の順。表はパターン（A→B）ごとに、この順位の良い順に並べた（表示の順番だけ。買う順番・件数の上限は変えていない。候補の選び方を変えても成績は変わらなかったため。2026-10-02 ユーザーの指示）。著者には渡さない。

- 悪いニュースが続いているグループ（半導体）の候補（記録だけ。売買のルールは変えない。著者には渡さない）: NVDA

- 候補の数: 空き枠3（同時保有4銘柄まで。保有2、うち今日ルールの売りが成立1）＋予備2件まで表に出した（2026-10-25 ユーザー決定）。省いた候補はない。

- テーマの外の候補（グループが「テーマの外」）: 監視銘柄の候補で枠が埋まらないときに使う（監視銘柄の候補を先に買う）。S&P500の今の構成銘柄のうち監視銘柄でない銘柄から、RS≧90・30週線が上向きで終値がその上・業種の3カ月の強さが上位20%の19銘柄を調べ、空き枠2つ分まで出した。バックテストでは、テーマの外の強い銘柄で空き枠を埋めると、テーマが弱い時期の成績が支えられた（`バックテスト結果/半導体・AIに特化した場合.md`。2026-10-01 ユーザー決定）。

- RS≧80の押し目（ボリンジャーIII）は、バックテストで成績がより安定していた（PF3.27、最大下落20%）。

## 6-3. 参考: 条件の成立が目前の銘柄（予約は注文しない・著者には送らない）

2026-10-25 ユーザー決定: 予約（逆指値・指値）の注文はやめ、参考の表示だけにする。毎朝のツールと同じ条件・値段で予約の約定をバックテストに入れると、どの形も年率が下がった（後知恵なし 35.7%→30.7〜34.2%、87銘柄 45.6%→34.2〜42.6%。`バックテスト結果/点検_2026-10-25/`）。引けで条件がそろえば、翌朝の節6に買いの候補（A）として出る。各ルールでRSの高い順に2件まで。

| 参考の銘柄 | グループ | 種類 | 終値 | 前日比 | RS | 当てはまった条件 | 条件がそろう目安の価格（注文はしない） |
|---|---|---|---|---|---|---|---|
| WDAY | AIソフト・セキュリティ・ITサービス | ボリンジャー メソッドIII（%bが0.05未満に近い） | 191.16 | +1.2% | 66 | %b=0.192（0.05まであと少し）、21日II%=+0.060（>0） | 187.50（この値より下で引けると翌朝の買いの候補（A）。目安） |
| CRM | AIソフト・セキュリティ・ITサービス | ボリンジャー メソッドIII（%bが0.05未満に近い） | 218.01 | +2.1% | 62 | %b=0.194（0.05まであと少し）、21日II%=+0.100（>0） | 210.89（この値より下で引けると翌朝の買いの候補（A）。目安） |


# ニュース（サブエージェントの調査）

# ニュース調査（2026-11-12 JST／米国 2026-11-11 の引け時点）

## テーマ全体の上げのきっかけ（4節で多数の銘柄が+5%以上）
- きっかけ: 11/10 引け後の CoreWeave の第3四半期決算（予想を上回り見通しを引き上げ「Beat-and-Raise」）。11/11 に CRWV は +24.7%（2025年4月以来の最大の上げ）（CNBC 11/11、The Motley Fool 11/11）。
- 広がった先: ネオクラウド（NBIS「CoreWeave Lifts AI Clouds」GuruFocus 11/11）、メモリ（Benzinga 11/11）、光（COHR +11.5% GuruFocus 11/11）、AI半導体（GuruFocus 11/11）。
- 市場全体: NY株反発・ダウ254ドル高「AI投資懸念和らぐ」（時事通信 11/11、Reuters 11/11）。Goldman Sachsが半導体株を「売られすぎ」（Yahoo Finance 11/11）。
- 信用の材料: 見出しは「Nine Proposed ETFs Would Bet on AI Credit Stress via CDS」（FourWeekMBA 11/11）の1件のみ。社債・CDSの数値は取得不可。VIX・ハイイールド債は取得不可。
- 呼び名: 日本語で「中間選挙ショック」（東洋経済 11/11）、「CPIショック／米物価ショック」（BigGo・YouTube 11/11）の見出しあり。
- 決算の数値: 検索で見つからず取得不可。

## 引け後・時間外の材料
- CRM: 時間外 +5.7%。原因の見出しは見つからなかった（検索でも該当なし。11/10 Listen Labs 買収交渉の報道 Stocktwits）。
- NVDA: 時間外 −3.9%。「Nvidia Falls Late On Latest Huang Report」（Investor's Business Daily 11/11）。報道の中身は取得不可。
- AMD +1.4%・SNDK 0.0%: 材料の見出しなし。

## NVDA（候補）
- 11/8〜9: 取締役会の独立委員会が、ジェンスン・フアンCEOが外国の情報活動の標的になった疑いを調査すると発表。11/9 に株価は下落（CNN 11/9、Dow Jones 11/9）。
- 11/11: 「Nvidia stock gets a rare Wall Street downgrade on supply issues」（Yahoo Finance 11/11）。Bairdの格下げ（ad-hoc-news.de 11/11）。詳細は取得不可。
- 11/11: 「Nvidia Just Had Its Worst 5 Days Since 2022」（24/7 Wall St. 11/11）。
- 次回決算 2026-11-17（scan.md）。公式発表の有無は確認できず。
- 悪材料: あり（CEOをめぐる取締役会の調査、格下げ、11/11引け後の新たなフアン氏関連報道で時間外−3.9%）

## AMD（保有）
- 11/9: Oppenheimer の格上げと Google Cloud のチップ採用で上昇（The Motley Fool 11/9、Investor's Business Daily 11/9）。
- 11/11: CoreWeave決算を受けたAI株の反発をNVDA・AVGOと共に主導（GuruFocus 11/11）。
- 悪材料: 確認できず

## SNDK（保有）
- 11/5: 好決算にもかかわらずAI株の売りで −20%（Yahoo Finance 11/5、MarketWatch 11/5）。11/6 にも −9%（Moomoo 11/6）。
- 11/7: 株式分割を前に下落、アナリストの評価が分かれる（Benzinga 11/7）。
- 11/11: CoreWeave CEOの「AI需要が世界の供給能力を上回る」発言でMUと共に急騰（Benzinga 11/11）。
- 悪材料: 確認できず

## CRWV / NBIS
- CRWV: 第3四半期決算で +24.7%（上記）。NBIS: 11/12 の決算を前に連れ高 +15.4%（Barron's 11/11）。

## KLAC / AMAT / KEYS（半導体製造装置、1週+6.5%）
- AMAT: 11/12 の第4四半期決算を前に上昇、装置株がそろって反発（24/7 Wall St. 11/11）。
- KLAC: 装置株全体の反発。固有の材料の見出しなし。
- KEYS: 11/9「Winning ADS Designation」で急伸（Baystreet.ca 11/9）。

## 監視外の注目銘柄（HUM・VTRS・HAS・LLY・KDP）
- 検索せず。原因は取得不可。

## テーマ全体のニュース（直近1週間）
- 先週の「historic selloff」から反発（WSJ 11/11）。Anthropic のIPO目論見書（Barron's 11/11）。
- 「AI Stocks, Neoclouds Rebound From SoftBank Bump」（Investor's Business Daily 11/11）。SoftBankの件の中身は取得不可。

# ニュースの見出し（プログラムが自動で取得）

- Googleニュース（日付を指定）とYahooファイナンスの見出しを `tools/news_headlines.py` が自動で並べたもの。日付は米国東部時間の配信日（引け後の記事は翌日付）。原因の判断・売買の判断はしていない。
- 調べた銘柄の選び方: ①保有 ②今日の候補 ③時間外に±5%以上動いた監視銘柄 は全部、④引けまでに大きく動いた銘柄（1週で±5%のグループの上位3・1日で±7%）は合計12銘柄まで。
- 1週で−5%以下のグループ: なし
- 1週で+5%以上のグループ: 半導体製造装置・材料・設計ソフト・計測（+6.5%）

## 0. 時間外（引け後）の値動き（2026-11-11 の引けから、Yahoo。±3%以上の監視銘柄と、保有・候補は全部）

| 銘柄 | 区分 | 引け | 時間外 | 騰落率 |
|---|---|---|---|---|
| CRM | 監視 | 217.98 | 230.45（16:56 ET） | **+5.7%** |
| NVDA | 候補 | 173.85 | 167.16（17:19 ET） | -3.9% |
| AMD | 保有 | 552.96 | 560.52（17:19 ET） | +1.4% |
| SNDK | 保有 | 977.90 | 977.50（17:19 ET） | -0.0% |

## 1. 市場全体（2026-11-11）

### 市場全体（英語のまとめ記事）
検索語: `stocks Wall Street close Nasdaq`
- 11/11 Eurasia Business News | Stock Market Today: Dow Jones, Nasdaq, S&P 500 Rally on November 11, 2026; Oil Rises, Gold Slips
- 11/11 Kiplinger | Nasdaq Adds 400 Points as CoreWeave Earnings Revive the AI Trade: Stock Market Today
- 11/11 Barron's | Is the Stock Market Open Today? Here Are the Trading Hours for Veterans Day.
- 11/11 Detroit Free Press | Is the stock market closed? NYSE Veterans Day hours
- 11/11 The Columbus Dispatch | Is the stock market open on Veterans Day? NYSE, Nasdaq hours today

### 市場全体（Stock Market Today）
検索語: `"stock market today"`
- 11/11 Investor's Business Daily | Stock Market Today: Stock Market News And Analysis
- 11/11 The Motley Fool | Stock Market Today, Nov. 11: CoreWeave Surges 25% on Beat-and-Raise Quarter
- 11/11 Yahoo Finance | Australian Stock Market Today: ASX Futures Dip On Housing Credit Slump And RBA Watch

### 市場全体（日本語のまとめ記事）
検索語: `米国株式市場 OR NY株`
- 11/11 Reuters | 米国株式市場＝反発、コアウィーブ決算受けＡＩ投資巡る懸念後退
- 11/11 沖縄タイムス社 | ＮＹ株反発、２５４ドル高
- 11/11 Yahoo!ファイナンス | 米国株式市場は反発、ハイテクが回復（11日）(フィスコ)
- 11/11 時事通信ニュース | ＮＹ株反発、２５４ドル高＝ＡＩ投資懸念和らぐ
- 11/11 京都新聞デジタル | ＮＹ株、小動きで始まる

### 半導体・AI株（英語）
検索語: `chip stocks OR semiconductor stocks OR AI stocks`
- 11/11 Investor's Business Daily | Chip Stocks Rally After Slide. These Names Are Leading The Charge Higher.
- 11/11 AP News | AI stocks rebound, and Wall Street nearly returns to where it was before last week’s sell-off
- 11/11 Yahoo Finance | Goldman Sachs calls chip stocks 'oversold.' Here are the names it says to buy.
- 11/11 WSJ | Investors Run Back to AI Stocks, Less Than a Week After a Historic Selloff
- 11/11 Barchart.com | Chip Stocks Rebound After a 12% Crash, But Not All Semiconductor Picks Have Staying Power

### 信用（社債・借金）
検索語: `AI debt OR bonds OR credit spreads OR CDS`
- 11/11 FourWeekMBA | Nine Proposed ETFs Would Bet on AI Credit Stress via CDS

### 「〇〇ショック」の呼び名（日本語）
検索語: `ショック 株`
- 11/11 東洋経済オンライン | 日本株は｢中間選挙ショック｣を乗り越えられるか…"7万円台"回復のカギを握る3つのポイント
- 11/11 ｄメニューニュース | 「中間選挙ショック」が私たちの資産形成に与えてくれる示唆は？
- 11/11 BigGo ファイナンス | 米物価ショックを乗り越え韓国KOSPIは2.6%急反発…外国人・機関の「買い」でKOSDAQは買いサイドカー発動
- 11/11 YouTube | 日経平均6万円台！米国株はCPIショックで反落！年末6万5,000円か再暴落か？株価の今後とNISAへの影響を徹底分析
- 11/11 BigGo ファイナンス | 米物価ショックでも韓国KOSPIは1%台高…KOSDAQは4%台急騰、半導体素材・部品・装置が疾走

### 引け後・時間外の動き（英語）
検索語: `"after hours" OR "after the bell" OR "extended trading" stocks`
- 11/11 Yahoo Finance | Rigetti Computing Stock Sinks Nearly 7% After Hours as CFO Signals Another Year of Heavy Spending: CapEx Won’t Return to 2025 Levels
- 11/11 Seeking Alpha | Stocks to watch on Wednesday after hours: EZPW, IRTC, EGP (EZPW:NASDAQ)
- 11/11 Benzinga | SHF Holdings Shares Jump 26.42% After Hours - SHF Hldgs (NASDAQ:SHFS)
- 11/11 Yahoo Finance | CoreWeave Stock Jumps Nearly 8% After Hours as CEO Courts Texas Governor-Elect Gina Hinojosa, Calls Company ‘Nonpartisan’
- 11/11 Benzinga | Suja Life (SUJA) Shares Fall 18% After-Hours: Here’s Why
- 11/11 TradingView | NEXTNRG (NXXT) Shares Plunge 25% After-Hours: Here’s Why

### 引け後・時間外の動き（日本語）
検索語: `時間外 決算 株`
- 11/11 Yahoo!ファイナンス | ブライトビュー、決算受け時間外で１３％安＝米国株個別(株探ニュース)
- 11/11 BigGo ファイナンス | 日経平均、789円高で3日続伸 急落前水準を奪回も200日線は視界外
- 11/11 Yahoo!ファイナンス | コアウィーブ、決算受け時間外で１５％高＝米国株個別(株探ニュース)
- 11/11 Moomoo | コアウィーブの決算発表を受け、米国のネオクラウド株が時間外取引で上昇
- 11/11 BigGo ファイナンス | CoreWeaveの好決算で韓国半導体株が急騰、KOSPIは2.6%高
- 11/11 株探 | ＭＰマテリアルズ、時間外で上昇＝米国株個別
- 11/11 Chosunbiz | コアウィーブ好決算で韓国株続伸
- 11/11 BigGo ファイナンス | CoreWeaveの好決算でAIへの信頼回復、TSX先物が上昇

### 買収・合併（英語）
検索語: `acquisition OR acquire OR merger OR takeover chip OR semiconductor OR AI OR optical`
- 11/11 Barron's | Airbnb and Travel Stocks Fall as OpenAI Acquisition Raises New AI Threat
- 11/11 Fierce Biotech | Valo and Montai become one as the Flagship AI-based biotechs tie the knot
- 11/11 Medical Device and Diagnostic industry | Oura to Acquire Counsel Health for $625M in AI Care Push
- 11/11 qz.com | Boomi CEO Steve Lucas on how latest acquisition brings trusted data to AI era
- 11/11 Business Insider | AI’s dealmaking frenzy
- 11/11 Yahoo Finance | Tesla (TSLA) Forms Special Committee To Review Possible All Stock Merger
- 11/11 Forbes | Phillies Acquire New Backstop After JT Realmuto Decision
- 11/11 AI Insider | OpenAI Pushes Deeper Into Consumer Discovery With ChatGPT Business Hub and Odessia Acquisition

## 2. 保有・候補・時間外で大きく動いた銘柄（2026-11-05〜2026-11-11 の見出し）

### SNDK（Sandisk Corporation、保有、AIサーバー・ストレージ・メモリ・端末、前日比 +13.7%、1週 -5.8%、時間外 -0.0%）

#### Googleニュース
検索語: `Sandisk stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/5 Yahoo Finance | SanDisk stock plunges 20% as AI selloff deepens despite strong earnings
- 11/5 MarketWatch | Micron, Sandisk and other AI stocks see steep drops: ‘Investors don’t like uncertainty’
- 11/6 Moomoo | Overnight US Stocks | Global Bond Yields Surge; S&P 500 Falls for Third Consecutive Day; SanDisk (SNDK.US) Drops 9%
- 11/7 Benzinga | SanDisk Stock Drops Ahead of Split as Wall Street Analysts Weigh In

#### Yahooファイナンス
検索語: `SNDK`
- 11/11 24/7 Wall St. | Jim Cramer Says Micron Isn’t Going Away. Here’s Why He Picks It Over Sandisk
- 11/11 Benzinga Prediction Markets | Micron, Sandisk Soar as CoreWeave CEO Says AI Demand Outpaces World's Capacity
- 11/11 GuruFocus.com | Coherent Stocks Climb 11.5% as Datacenter Optics Demand Lifts AI Suppliers

### AMD（Advanced Micro Devices, Inc.、保有、半導体、前日比 +7.3%、1週 +13.1%、時間外 +1.4%）

#### Googleニュース
検索語: `Advanced Micro Devices stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/5 Yahoo Finance | Why AMD Stock Is Down Today
- 11/9 CNN | AMD Stock Quote Price and Forecast
- 11/9 The Motley Fool | Stock Market Today, Nov. 9: AMD Jumps on Oppenheimer Upgrade and Google Cloud Chip Selection
- 11/9 Investor's Business Daily | AMD Stock Rises On Google Cloud Deal, Wall Street Upgrade

#### Yahooファイナンス
検索語: `AMD`
- 11/11 24/7 Wall St. | Nvidia Just Had Its Worst 5 Days Since 2022, Worse Than the DeepSeek Crash
- 11/11 Barrons.com | Anthropic’s IPO Prospectus by the Head-Spinning Numbers
- 11/11 GuruFocus.com | Nvidia, AMD and Broadcom Lead AI Stock Rally as CoreWeave Results Ease Spending Fears

### NVDA（NVIDIA Corporation、候補、半導体、前日比 +2.9%、1週 -13.2%、時間外 -3.9%）

#### Googleニュース
検索語: `NVIDIA stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/9 CNN | Nvidia stock falls after investigation into CEO, bucking market rally
- 11/9 NBC News | Nvidia shares sink while stock market surges
- 11/9 The New York Times | Nvidia Stock Drops Even as Broader Market Rallies
- 11/11 WSJ | U.S. Stocks Leap Despite Nvidia Slide

#### Yahooファイナンス
検索語: `NVDA`
- 11/11 BeInCrypto | Can a Single Crypto Exchange Handle All Your Trades? Zoomex Thinks So
- 11/11 Investor's Business Daily | Dow Jones Futures: CoreWeave, Sandisk, AMD, Nebius Lead Bullish Market Move; Nvidia Falls Late On Latest Huang Report

### CRM（Salesforce, Inc.、AIソフト・セキュリティ・ITサービス、前日比 +2.1%、1週 -4.0%、時間外 +5.7%）

#### Googleニュース
検索語: `Salesforce stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/9 Yahoo Finance | Salesforce Stock Outlook: Is Wall Street Bullish or Bearish?
- 11/9 JournalArta | Salesforce (CRM) Stock: $213.65, Down 3.94% Nov 6
- 11/10 Stocktwits | CRM Stock Dips 2% — Salesforce Is Reportedly In Talks To Acquire AI Research Firm Listen Labs For $2B
- 11/11 Trefis | Can Salesforce Stock Fall 30%?

#### Yahooファイナンス
検索語: `CRM`
- 11/10 Business Wire | Salesforce Announces Date of Third Quarter Fiscal 2027 Earnings Release and Webcast
- 11/10 Trefis | What Are ServiceNow Stock Bears Missing?
- 11/11 24/7 Wall St. | Prediction: Palantir Shares Could Deliver Outsized Returns Over the Next 5 Years

## 4. 引けまでに大きく上げた銘柄（2026-11-05〜2026-11-11 の見出し）

### KLAC（KLA Corporation、半導体製造装置・材料・設計ソフト・計測、前日比 +5.2%、1週 +7.5%、時間外 -0.2%）

#### Googleニュース
検索語: `KLA stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/6 StreetInsider | KLA Corporation stock jumps as buyers return after selloff
- 11/7 Yahoo Finance | What Changed For KLA Stock, And What Did Not?
- 11/9 MarketWatch | KLA Corp. stock underperforms Monday when compared to competitors despite daily gains
- 11/10 Trefis | Can KLA Stock Rally 50% After This Dip?

#### Yahooファイナンス
検索語: `KLAC`
- 11/10 24/7 Wall St. | $1,000 Invested in KLA 10 Years Ago Would Be Worth Over $21,000 Today
- 11/10 MarketBeat | Don't Let Their Low Yields Fool You: 3 Dividend Stocks Worth Watching

### AMAT（Applied Materials, Inc.、半導体製造装置・材料・設計ソフト・計測、前日比 +6.1%、1週 +7.0%、時間外 -0.0%）

#### Googleニュース
検索語: `Applied Materials stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/6 Yahoo Finance | Applied Materials Stocks Rise 4.7% as Chip Equipment Rallies Ahead of Earnings
- 11/8 Opening Bell Daily | Stock market week ahead: Cisco leads 9 big earnings reports
- 11/9 24/7 Wall St. | Applied Materials Jumps 11% Ahead of Earnings; Lam Research Surges 9%, ASML Rises 6%
- 11/10 TradingView | Applied Materials stock: death cross pattern nears ahead of earnings

#### Yahooファイナンス
検索語: `AMAT`
- 11/11 24/7 Wall St. | 3 Tech Dividend Stocks That Could Turn $300,000 Into $4,200 in Annual Income
- 11/11 24/7 Wall St. | Applied Materials Rallies 8% Ahead of Earnings as Chip Stocks Rebound; Lam Research Jumps 9%, KLA Climbs 7%
- 11/11 GuruFocus.com | Applied Materials Stocks Climb 5.72% a Day Before Fourth-Quarter Results

### KEYS（Keysight Technologies, Inc.、半導体製造装置・材料・設計ソフト・計測、前日比 +4.9%、1週 +6.9%、時間外 -0.0%）

#### Googleニュース
検索語: `Keysight stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/5 Yahoo Finance | ServiceNow CPQ helps Keysight accelerate sales and digital commerce, generating quotes 40% faster
- 11/5 MarketWatch | Keysight Technologies Inc. stock underperforms Thursday when compared to competitors
- 11/9 TradingView | Why is Keysight (KEYS) stock rocketing higher today
- 11/9 Baystreet.ca | Keysight Jumps on Winning ADS Designation

#### Yahooファイナンス
検索語: `KEYS`
- 11/8 Simply Wall St. | 3 Cash Rich AI Stocks Investors Are Watching As Debt Costs Rise
- 11/9 Business Wire | Keysight Brings Radio Frequency and Photonic Design Together for Tower Semiconductor

### CRWV（CoreWeave, Inc.、AIプラットフォーム・クラウド、前日比 +24.7%、1週 +25.5%、時間外 -2.5%）

#### Googleニュース
検索語: `CoreWeave stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/5 Yahoo Finance | What Is Driving The Fall In CoreWeave Stock?
- 11/9 Barron's | CoreWeave CEO Urges Clarity on Texas Data-Center Buildout. The Stock Rises.
- 11/11 CNBC | CoreWeave soars more than 24% for best day since April 2025 after strong Q3 report
- 11/11 investingLive | CoreWeave stock jumps nearly 13% after earnings. Buy the rally or sell into resistance?

#### Yahooファイナンス
検索語: `CRWV`
- 11/11 Investor's Business Daily | AI Stocks, Neoclouds Rebound From SoftBank Bump, Get CoreWeave Lift

### NBIS（Nebius Group N.V.、AIプラットフォーム・クラウド、前日比 +15.4%、1週 +9.3%、時間外 +0.1%）

#### Googleニュース
検索語: `Nebius stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/6 Yahoo Finance | Prediction: Nebius Stock Will Surge 95% in a Year, According to Wall Street. Should You Buy It Before Nov. 12?
- 11/6 Moomoo | Nebius Stock Soars 20% Intraday as Revenue Beat Bolsters AI Rally. Michael Burry May Be Helping
- 11/9 CNN | NBIS Stock Quote Price and Forecast
- 11/11 Barron's | Nebius Stock Jumps Ahead of Earnings. CoreWeave Gives It a Lift.

#### Yahooファイナンス
検索語: `NBIS`
- 11/11 Barrons.com | Nvidia, CoreWeave, Nebius, Teradyne, Riskified, and More Stocks That Explain Today’s Market
- 11/11 GuruFocus.com | Nebius Group Stocks Jump Nearly 17% Ahead of Thursday Results as CoreWeave Lifts AI Clouds

# 実行時の注記
- 環境に matplotlib・Pillow がなく、prepare で候補・保有銘柄の数値データが作れなかったため、入れ直して数値データを作り直した。
- 個別銘柄のプロンプトが8,000文字を超え（テーマの状態の節が長いため）送信できなかった。著者（ボリンジャー・コナーズ）へは、テーマの状態の節から「グループごとの悪いニュースの流れ（記録だけ）」の表と見出しを外して（scan_short.md）送り直した。ニュースは文字数の上限まで縮めた（2026-11-11 と同じ対応）。
- ワインスタインへのテーマの局面は、全体の版が空の応答だったため1〜2節だけの短い版で送った回答。
- SNDK（ルール外の保有）は担当の著者がいないため送っていない（著者の判定は【未判定】）。
