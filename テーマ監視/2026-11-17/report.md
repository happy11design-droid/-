# テーマ監視 2026-11-16

# 判定のまとめ（ルールの判定と著者の判定を分けて表示）

- **ルールの判定**: 採用した売買ルール（スクリプト）が数値で決めたもの。損切りは買値の15%下の逆指値（日中に届けばその場で売れる）。
- **著者の判定**: ノートブックの著者の回答。買いは注文を止める理由があるときだけ【様子見】、保有はルールより早く手じまう理由があるときだけ【売り】。根拠は下の「著者の回答（全文）」。
- 2つが食い違うときに、どちらに従うかはユーザーが決める。

- **テーマ全体の急落（S2・記録だけ）: あり（S2）**（SOXが直近60取引日の最高値から -27.3%）。S2の日の順張りの候補には「S2なら見送る形」と付ける（売買のルールは変えない。記録してから採用を決める。2026-10-14）

- **特殊な下げ（記録だけ）: あり（特殊な下げ）**（2026-10-16から）（SOXが直近60取引日の最高値から -27.3%、前の1年の大きな上げ・雇用の弱さ・物価の再加速のうち 2つ）。1995年〜では、この形の後にSOXの下げが長引くことが多かった（後知恵を含む）。売買のルールは変えない（2026-11-03）

## 保有銘柄

| 銘柄 | ルール | 損益 | 時間外 | ルールの判定 | ルールの判定の理由 | 著者の判定 |
|---|---|---|---|---|---|---|
| SNDK | ルール外（ユーザーの判断。この日はどのルールの合図もなし） | -41.0% | +0.5% | **売り** | 終値 809.11 が損切り価格 1165.61 以下 | 【未判定】（） |
| AMD | ボリンジャーIII | -8.3% | -0.0% | 保有継続 | 損切り 467.47（終値から -7.3%） | 【保有継続】（ボリンジャー） |

## 候補の判定（並びは上の「買う順番」の表と同じ）

候補なし

- 時間外: 前の取引日の引けから、引け後（米国東部時間16〜20時）の最後の値までの騰落率（Yahoo。±5%以上は太字）。寄り付きの値段は、表の注文の目安（前日の終値で計算）から大きくずれることがある。原因の見出しは「ニュースの見出し」の節。

# 著者の回答（全文）

## 0_テーマの局面_ワインスタイン

1. **テーマ全体の局面**: 【ステージ3】（大幅上昇後に30週線が横ばい化し天井圏、第2・8章 [1, 2]）

2. **グループごとの局面**:
- 半導体｜ステージ3｜30週線横ばい
- 半導体製造装置・材料・設計ソフト・計測｜ステージ3｜30週線横ばい
- AIサーバー・ストレージ・メモリ・端末｜ステージ3｜30週線横ばい
- 光・通信・ネットワーク｜ステージ3｜30週線横ばい
- データセンターの電力・冷却・部品・受託製造・建設｜ステージ3｜30週線横ばい
- AIプラットフォーム・クラウド｜ステージ3｜30週線横ばい
- AIソフト・セキュリティ・ITサービス｜ステージ2｜30週線上昇・株価線上

3. **転換の兆し**:
出ている。30週線の水平化（第2・8章 [1, 2]）や対S&P500のRS悪化（第1・4章 [3, 4]）は天井・崩れの基準に合致。50日線、警告、S2、ニュース、雇用・物価はマニュアルに規定なし [5]。

4. **テーマの外**:
判定不能（ヒートマップ省略のため判定不能）

（全体の版が空の応答だったため、1〜2節だけの短い版で送り直した回答。ヒートマップ・急騰急落・ニュースは渡していない）

## 1_ボリンジャー_prompt_1

## AMD
1. **投資判断**: 【保有継続】（早期手じまい不要）
2. **止める理由の確認**:
   - 本が禁じる形・状況｜なし｜第13・20章未抵触 [1, 2]
   - 避けるべき時期（決算など）｜なし｜マニュアルに規定なし [3]
   - 悪材料｜なし｜マニュアルに規定なし（11/12-16） [3]
3. **現状パターンと価格**:
   - 保有中: 売りの予約注文: 指値売り 604.85（現在値比 +19.9%） [2]
4. **注意点**: 特になし

（AMDの質問文が8,000文字を超えたため、数値データのうち 2026-10-21 より前の大きな値動きの行と決算の中身の表を外し、テーマの状態（2節）から2倍ETFの局面の行・バックテストの参考の説明・良いニュースの見出しの行を外し、テーマ全体のニュースは「テーマ全体の下げの原因」の節（輸出規制・市場全体の行を除く）だけにして送った回答。AMDのニュースは全文を渡した）

# スキャン（数値と事実）


- 監視銘柄 87（判定できたのは 87）。
- この一覧は数値と事実だけ。売買の判断は著者のノートブックが行う。

## 1. テーマ（グループ）の強さ

| グループ | 銘柄数 | 1週 | 1カ月 | 3カ月 | 3カ月の順位 | 50日線より上の銘柄の割合 | グループ指数の30週線の局面（線との乖離、4週前からの線の傾き） |
|---|---|---|---|---|---|---|---|
| 半導体 | 16 | -2.1% | -4.6% | -12.1% | 4位 | 25% | 横ばい（-14.0%、+4.5%） |
| 半導体製造装置・材料・設計ソフト・計測 | 9 | -5.5% | -13.8% | -21.9% | 5位 | 0% | 横ばい（-18.4%、+0.8%） |
| AIサーバー・ストレージ・メモリ・端末 | 9 | -2.0% | -15.5% | -31.5% | 7位 | 11% | 横ばい（-15.2%、+6.0%） |
| 光・通信・ネットワーク | 9 | -4.2% | -12.7% | -27.0% | 6位 | 11% | 横ばい（-18.6%、+0.7%） |
| データセンターの電力・冷却・部品・受託製造・建設 | 19 | -3.1% | -8.0% | -11.7% | 3位 | 16% | 横ばい（-11.0%、+0.2%） |
| AIプラットフォーム・クラウド | 11 | -1.5% | -7.1% | -0.7% | 2位 | 36% | 横ばい（-7.2%、+1.3%） |
| AIソフト・セキュリティ・ITサービス | 14 | -0.1% | -1.8% | +0.8% | 1位 | 43% | 上昇（+4.5%、+4.8%） |

## 2. テーマ全体の状態と早めの警告

- 市場全体の30週線による局面: S&P500指数 **横ばい**／NASDAQ100指数 **横ばい**（急落の底で買うルールは、過去の検証で下落相場で特に強く、横ばいの相場では負けていた）
- **2倍ETFを使う局面（案1、2026-10-13 採用）: S&P500の20週線（100日線）で 横ばい** → 新しく買う銘柄は、2倍ETFのある銘柄も元の株で買う（保有中のETFはそのまま）（SPY 739.95、100日線 759.25、20日前の線 756.03。上昇＝線より上かつ線が上向き）
- **テーマ全体の急落（S2、記録だけ。売買のルールは変えない）: あり（S2）**（SOX 9610.65、直近60取引日の最高値 13217.82 から -27.3%。S2＝最高値から−10%以上）。S2のときに「順張りの新しい買いだけ止める」形を記録で比べる（2026-10-14 ユーザー決定。バックテストでは年率は上がったが2つの期間ではどちらも少し下回ったため、記録してから採用を決める。`バックテスト結果/テーマ全体の急落を検知して手じまう・買いを止める.md`）
- **グループごとの悪いニュースの流れ（記録だけ。売買のルールは変えない。2026-11-03〜2026-11-16）**: 会社の名前と悪い言葉（格下げ・目標株価の引き下げ・見通しの引き下げ・予想未達・急落・信用・訴訟・輸出規制など）の両方がある見出しの数（Googleニュース、`tools/news_headlines.py`）。10取引日の1銘柄あたりが一番多いグループに印。2026年7〜11月の確かめでは、印のグループの合図は10月は成績が悪かった（1回平均 −10.6%、ほか −5.6%）が、7〜9月は逆に良かった（+11.6%、ほか +6.7%）（`バックテスト結果/実際の運用の期間の確認_2026-10-23/グループの悪いニュースの流れ.md`。2026-11-04）

| グループ | 悪いニュース 直近5取引日 | その前の5取引日 | 10取引日の1銘柄あたり | 良いニュース 10取引日（1銘柄あたり） | 印 |
|---|---|---|---|---|---|
| 半導体（16） | 48件 | 5件 | 3.3 | 14件（0.9） | **悪いニュースが続いている** |
| 光・通信・ネットワーク（9） | 7件 | 11件 | 2.0 | 7件（0.8） |  |
| AIサーバー・ストレージ・メモリ・端末（9） | 11件 | 6件 | 1.9 | 20件（2.2） | **良いニュースが多い** |
| AIプラットフォーム・クラウド（11） | 9件 | 2件 | 1.0 | 2件（0.2） |  |
| データセンターの電力・冷却・部品・受託製造・建設（19） | 2件 | 1件 | 0.2 | 13件（0.7） |  |
| 半導体製造装置・材料・設計ソフト・計測（9） | 0件 | 1件 | 0.1 | 5件（0.6） |  |
| AIソフト・セキュリティ・ITサービス（14） | 0件 | 1件 | 0.1 | 11件（0.8） |  |

印のグループ（半導体）の最近の見出し: 2026-11-16 Today's Analyst Rating | UBS Cuts Its Price Target Cut on NVIDIA to $240, SpaceX Price Target Raised to $280 by Citi（富途牛牛）／2026-11-16 Broadcom (AVGO) Downgraded As Wall Street Questions Its AI Financing Model（Yahoo! Finance Canada）／2026-11-16 Broadcom Stocks Slide 4.76% as Downgrade Keeps AI Financing Fears in Focus（TradingView）

良いニュースが多いグループ（AIサーバー・ストレージ・メモリ・端末）の最近の見出し: 2026-11-16 Your Apple TV 4K just got a surprising free upgrade（Pocket-lint）／2026-11-16 Apple's iPhone Duo 2 Face ID upgrade faces a tight deadline, report says（Business Upturn）

- **特殊な下げ（記録だけ。売買のルールは変えない）: あり（特殊な下げ）**（2026-10-16から）。SOX は直近60取引日の最高値から -27.3%（−15%以下が条件）、●A 前の1年の上げ +104.0%（+80%以上）、・B 雇用の伸び 137千人/月（2026-10まで。10万人未満）、●C 物価 4.0%（2026-09。3か月前 3.7%。3.5%以上で再加速）＝2つ（2つ以上が条件）。1995年〜でSOXが−15%以下かつ条件2つ以上の日は、120日後にSOXが下だったのが69%・250日後が70%（中央値 −33%）、AI以外の8業種の平均は250日後 −7%。ただし条件は過去を見て選んだもの（条件が2つ以上の局面は約5回）で、2026年7〜9月にこの間テーマを買わないと、その後の戻りを逃して2026年の成績は下がった（`バックテスト結果/実際の運用の期間の確認_2026-10-23/特殊な下げと過去の似た下げ.md`。2026-11-03）
- テーマ指数（監視銘柄の等金額平均）の30週線による局面: **横ばい**（上昇＝線より上かつ上向き、下落＝線より下かつ下向き、それ以外＝横ばい。ワインスタインのステージの近似）
- テーマ指数と50日線: 50日線より下（乖離 -11.4%）
- S&P500に対する相対的な強さ: 50日平均より下（S&P500より弱い）
- 監視銘柄のうち50日線より上の割合: 22%
- 警告（割合が40%未満かつテーマ指数が50日線より下）: **出ている**
- 参考（バックテスト）: 30週線の「下落」は高値から10〜33%下げた後に出る遅い判定。50日線・割合・相対的な強さは高値から2〜8%で出るが、誤報が年15回以上ある。警告中に新しい買いを止めると、押し目買い（ボリンジャーIII）の成績は大きく下がった（`バックテスト結果/テーマ監視銘柄・直近3年.md` 11・12節）。

## 3. ヒートマップ（Finviz、全米の業種別の騰落率）

3カ月の騰落率の上位15業種（テーマの外で強くなっている業種の確認用）:

| 順位 | 業種 | 1週 | 1カ月 | 3カ月 | 6カ月 | 1年 |
|---|---|---|---|---|---|---|
| 1 | Advertising Agencies | +1.4% | +39.1% | +24.1% | -7.7% | -19.3% |
| 2 | Medical Distribution | +3.5% | +8.5% | +20.4% | +39.4% | +21.1% |
| 3 | Health Information Services | -4.6% | +4.0% | +19.4% | +56.2% | +11.2% |
| 4 | Paper & Paper Products | -1.1% | +12.7% | +17.7% | +13.4% | +3.1% |
| 5 | Lodging | +1.8% | +9.7% | +16.0% | +17.5% | +38.6% |
| 6 | Insurance - Diversified | +3.1% | +10.0% | +15.4% | +19.0% | +14.9% |
| 7 | Household & Personal Products | +1.7% | +6.8% | +15.0% | +20.3% | +15.0% |
| 8 | Consumer Electronics | +0.6% | +2.9% | +13.8% | +18.4% | +27.1% |
| 9 | Medical Care Facilities | +0.3% | +8.6% | +13.6% | +22.3% | +22.4% |
| 10 | Real Estate - Diversified | -4.5% | +9.9% | +13.5% | +15.8% | +8.8% |
| 11 | Diagnostics & Research | -4.3% | -0.1% | +13.5% | +48.1% | +19.1% |
| 12 | Consulting Services | +3.2% | +14.4% | +13.4% | +21.9% | -1.2% |
| 13 | Insurance - Reinsurance | +2.9% | +4.9% | +12.9% | +21.3% | +36.3% |
| 14 | Discount Stores | +2.5% | +9.1% | +12.5% | +1.0% | +25.6% |
| 15 | REIT - Hotel & Motel | +1.3% | +8.9% | +12.3% | +27.7% | +52.1% |

テーマの業種の順位（3カ月、全144業種中）: Semiconductors 133位、Semiconductor Equipment & Materials 142位、Computer Hardware 143位、Communication Equipment 128位、Electronic Components 130位、Software - Infrastructure 57位、Software - Application 61位、Internet Content & Information 109位

## 4. 急騰・急落した銘柄（前日比±5%以上、または出来高が50日平均の2倍以上）

原因のニュースをサブエージェントが調べ、候補・保有銘柄の判定材料として著者に渡す。急騰・急落そのものは売買の合図にしない（後知恵のないS&P500全体のバックテストでは、急騰の翌日に買うルールは年率7%、急落の翌日に買うルールは年率9〜10%で、採用した3つのルールより優れていなかった）。

| 銘柄 | グループ | 前日比 | 出来高（50日平均の倍） | 終値 | 50日線 | RS | 局面 |
|---|---|---|---|---|---|---|---|
| ALAB | 半導体 | -8.8% | 1.0倍 | 202.34 | 下 | 51 | 下げ |
| SNDK | AIサーバー・ストレージ・メモリ・端末 | -8.6% | 1.2倍 | 809.11 | 下 | 89 | 下げ |
| LITE | 光・通信・ネットワーク | -8.5% | 0.8倍 | 546.00 | 下 | 44 | 下げ |
| CIEN | 光・通信・ネットワーク | -8.2% | 1.1倍 | 257.56 | 下 | 6 | 下落相場 |
| ARM | 半導体 | -8.1% | 0.9倍 | 175.05 | 下 | 26 | 下げ |
| MU | 半導体 | -7.6% | 0.9倍 | 719.02 | 下 | 97 | 下げ |
| NBIS | AIプラットフォーム・クラウド | -7.6% | 1.4倍 | 107.13 | 下 | 3 | 下げ |
| MRVL | 半導体 | -7.3% | 0.9倍 | 145.36 | 下 | 71 | 下げ |
| TER | 半導体製造装置・材料・設計ソフト・計測 | -7.1% | 1.0倍 | 231.90 | 下 | 7 | 下落相場 |
| INTC | 半導体 | -7.0% | 0.8倍 | 55.47 | 下 | 14 | 下げ |
| DELL | AIサーバー・ストレージ・メモリ・端末 | -7.0% | 1.1倍 | 320.55 | 下 | 98 | 下げ |
| GLW | 光・通信・ネットワーク | -6.9% | 0.9倍 | 106.17 | 下 | 8 | 下落相場 |
| SMCI | AIサーバー・ストレージ・メモリ・端末 | -6.9% | 0.8倍 | 25.02 | 下 | 3 | 下げ |
| COHR | 光・通信・ネットワーク | -6.7% | 0.9倍 | 203.43 | 下 | 11 | 下落相場 |
| LRCX | 半導体製造装置・材料・設計ソフト・計測 | -6.7% | 1.1倍 | 210.83 | 下 | 12 | 下落相場 |
| VRT | データセンターの電力・冷却・部品・受託製造・建設 | -6.6% | 1.1倍 | 188.67 | 下 | 5 | 下落相場 |
| DDOG | AIソフト・セキュリティ・ITサービス | -6.1% | 0.9倍 | 172.86 | 下 | 19 | 下げ |
| CRWV | AIプラットフォーム・クラウド | -6.1% | 1.0倍 | 49.88 | 下 | 0 | 下落相場 |
| ASML | 半導体製造装置・材料・設計ソフト・計測 | -5.9% | 1.0倍 | 1406.79 | 下 | 30 | 下げ |
| RDDT | AIソフト・セキュリティ・ITサービス | -5.7% | 0.8倍 | 92.87 | 下 | 1 | 下落相場 |
| AMD | 半導体 | -5.6% | 1.3倍 | 504.28 | 下 | 98 | 下げ |
| STX | AIサーバー・ストレージ・メモリ・端末 | -5.5% | 0.9倍 | 499.00 | 下 | 29 | 下げ |
| MPWR | 半導体 | -5.5% | 1.0倍 | 1314.00 | 上 | 57 | 上げ |
| KLAC | 半導体製造装置・材料・設計ソフト・計測 | -5.5% | 0.9倍 | 143.96 | 下 | 18 | 下落相場 |
| AMAT | 半導体製造装置・材料・設計ソフト・計測 | -5.5% | 1.0倍 | 350.25 | 下 | 24 | 下落相場 |
| ANET | 光・通信・ネットワーク | -5.2% | 1.1倍 | 187.02 | 下 | 81 | 下げ |
| NVDA | 半導体 | -4.1% | 2.2倍 | 156.14 | 下 | 4 | 下げ |

- 局面（判定式はClaudeが置いたもの）: **上昇相場**＝終値 > 50日線 > 200日線、50日線が20取引日前より2%以上高い、ADX(14) ≧ 20／**下落相場**＝終値 < 50日線 < 200日線、50日線が20取引日前より2%以上低い、ADX(14) ≧ 20／**上げ**＝それ以外で終値が50日線より上、かつ50日線が10取引日前より上か20日線が5取引日前より上／**下げ**＝それ以外で終値が50日線より下、かつ50日線が10取引日前より下か20日線が5取引日前より下（急な下げの初めは50日線がまだ上向きのため20日線でも見る）／**レンジ**＝どれにも当たらない（2026-11-05 から5つ。それまでは上昇相場とレンジの2つだけで、下げている銘柄もレンジと出ていた）。

## 4-2. 監視外の注目銘柄（S&P500・NASDAQ100のうち監視銘柄に入っていない銘柄）

条件: 流動性（株価5ドル以上・50日平均出来高25万株以上）があり、(a) 前日比+8%以上かつ出来高が50日平均の2倍以上、または (b) 終値が直前1年の最高値（終値）を上回り、RS≧90。RSの高い順に5銘柄（ニュースを調べる）。監視銘柄に入れるかはユーザーが決める。

| 銘柄 | 種類 | 前日比 | 出来高（50日平均の倍） | RS | 終値 |
|---|---|---|---|---|---|
| HUM | 1年の高値更新 | +2.5% | 0.9倍 | 99 | 461.25 |
| WST | 1年の高値更新 | +0.3% | 0.8倍 | 96 | 417.80 |
| LH | 1年の高値更新 | +0.5% | 0.7倍 | 93 | 372.46 |
| ADP | 1年の高値更新 | +1.1% | 1.2倍 | 93 | 313.43 |
| CAH | 1年の高値更新 | +1.0% | 0.8倍 | 93 | 283.85 |

- ほかに5銘柄: AIZ（1年の高値更新、RS 92）、MCK（1年の高値更新、RS 91）、CBOE（1年の高値更新、RS 90）、VLTO（1年の高値更新、RS 90）、TSN（急騰、RS 59）

## 5. 保有銘柄の手じまい条件（`新分析ツール/保有銘柄.md`）

| 銘柄 | ルール | 買った日 | 買値 | 終値 | 損益 | 損切り価格（買値の15%下、逆指値） | ルールの手じまい条件 | 出来高2倍の大陰線（買った後の直近5日） | 次回決算予定日 |
|---|---|---|---|---|---|---|---|---|---|
| SNDK | ルール外（ユーザーの判断。この日はどのルールの合図もなし） | 2026-10-21 | 1371.30 | 809.11 | -41.0% | 1165.61 | **損切り価格を下回った** ルールが不明（保有銘柄.md の「ルール」を確認） | なし | 2026-10-29 |
| AMD | ボリンジャーIII | 2026-10-21 | 549.97 | 504.28 | -8.3% | 467.47 | **出来高2倍の大陰線が 2026-11-05 に出た**（まだ持っていれば、次の寄り付きで全部売る） 売りの指値: 上部バンド 604.85（今夜この値に置き直す。届いた日に売れる）（2倍ETF AMUU で持っている場合も、判定は元の株 AMD の値段） | なし | 2027-02-02 |

- 出来高2倍の大陰線: 実体（始値−終値）が前日までのATR(14)の1.5倍以上、終値がその日の値幅の下25%以内、出来高が前日までの50日平均の2倍以上の日。**押し目（ボリンジャーIII）・急落の底の保有では売りのルール**: 出たら翌日の寄り付きで全部売り、空いた枠で次の合図を買う（2026-10-02 ユーザー決定。`バックテスト結果/やり直し_売りの合図の組み合わせ.md`。乱数3組とも年率が約+2ポイント、最大下落率もやや下がった）。ミネルヴィニ・新高値V2の保有では事実の表示（順張りに足しても良くならなかった）。

- 半分売りの合図（ミネルヴィニ・新高値V2の保有だけ）: 反転のローソク足（かぶせ線・弱気の包み足・宵の明星・流れ星）＋出来高が50日平均の1.5倍以上＋RSI(14)が前日か当日に70以上。買った後に最初に出た日の翌日の寄り付きで半分売り、残り半分は50日線割れ・損切り15%まで持つ（2026-10-01 ユーザー決定。`バックテスト結果/半分だけ売るとオニールの空き枠.md`）。

- かぶせ線（ミネルヴィニ・新高値V2の保有だけ）: 上昇中の陽線の翌日に、前日の高値より上で寄り付き、前日の陽線の真ん中より下（前日の始値より上）で引けた日。翌日の寄り付きで全部売り、空いた枠で次の合図を買う。半分売りより優先する（2026-10-01 ユーザー決定。`バックテスト結果/2倍ETFで売って買い直す.md`。順張りの売買の25%で出て、1回平均+2.0%、年率 21.4%→26.4%）。

## 5-2. 前日（2026-11-13の引け）の【買い（予約）】の確認

前日の【買い（予約）】はなし。

## 6. 候補（採用したルールの条件が成立＝A。予約（B）は2026-10-25から注文せず、節6-3に参考の表示だけ）

建玉の目安: 同時保有4銘柄まで、1銘柄に資金の25%（資金÷4）、損切りは買値の15%下（ユーザー決定 2026-09-29）。

本日は該当なし（著者への送信は不要）。


## 6-3. 参考: 条件の成立が目前の銘柄（予約は注文しない・著者には送らない）

2026-10-25 ユーザー決定: 予約（逆指値・指値）の注文はやめ、参考の表示だけにする。毎朝のツールと同じ条件・値段で予約の約定をバックテストに入れると、どの形も年率が下がった（後知恵なし 35.7%→30.7〜34.2%、87銘柄 45.6%→34.2〜42.6%。`バックテスト結果/点検_2026-10-25/`）。引けで条件がそろえば、翌朝の節6に買いの候補（A）として出る。各ルールでRSの高い順に2件まで。

| 参考の銘柄 | グループ | 種類 | 終値 | 前日比 | RS | 当てはまった条件 | 条件がそろう目安の価格（注文はしない） |
|---|---|---|---|---|---|---|---|
| PLTR | AIプラットフォーム・クラウド | ボリンジャー メソッドIII（%bが0.05未満に近い） | 160.39 | -4.5% | 45 | %b=0.160（0.05まであと少し）、21日II%=+0.059（>0） | 153.84（この値より下で引けると翌朝の買いの候補（A）。目安） |
| IBM | AIプラットフォーム・クラウド | ボリンジャー メソッドIII（%bが0.05未満に近い） | 242.51 | -1.9% | 33 | %b=0.155（0.05まであと少し）、21日II%=+0.219（>0） | 240.71（この値より下で引けると翌朝の買いの候補（A）。目安） |


# ニュース（サブエージェントの調査）

# ニュース調査（2026-11-16 の引け時点）

事実のみ。出典の「見出し」は headlines.md の見出し（中身は未確認）、「検索」はWeb検索で確かめたもの。

## テーマ全体の下げの原因
- きっかけ: NVIDIA が 11/12 付の発表で、ジェンスン・フアン氏が社長・CEO・取締役を即日辞任、CFOのコレット・クレス氏が暫定CEO、ハーベイ・ジョーンズ氏が初の取締役会議長と公表。辞任の理由は記載なし。後任は社内外から探す（SEC 8-K、検索）。11/9 時点では取締役会の調査と退任の可能性が報じられていた（Fortune 11/9、検索）。
- 11/16: 「NY株739ドル安 エヌビディア混乱でリスク回避」（時事 11/16）、「Nasdaq Falls 626 Points to Start Nvidia-Anthropic Week」（Kiplinger 11/16）、「Stocks Fall Before Nvidia Earnings, Anthropic IPO」（Bloomberg 11/16）、「Bessent Presses Nvidia…」（Benzinga 11/16。見出しが途中で切れており、発言の中身は取得不可）。NVDA の決算は 11/17 の引け後（8-K）。
- 広がった先: 装置（「ASML Stocks Fall as NVIDIA Shake-Up Spills Into Chip Equipment」TradingView 11/13）、メモリ（Yahoo Finance 11/16）、ネオクラウド（「CoreWeave, Oracle and Nebius Plunge as Nvidia Fallout」GuruFocus 11/16）。
- 輸出規制: 「Micron stock tumbles as Trump admin. cuts a loophole allowing China access to advanced chips」（Boise Dev 11/16）。規制の中身は検索（"Trump administration closes loophole China advanced chips Micron"）で確認できず、取得不可。
- 信用: 「Broadcom (AVGO) Downgraded As Wall Street Questions Its AI Financing Model」（Yahoo Finance Canada 11/16）、AVGO −4.76%（TradingView 11/16）、「Meta… Borrowing Is Becoming More Expensive」（MarketBeat 11/16）。11/16 の社債利回り・CDSの数字は取得不可（検索 "Broadcom downgrade AI financing CoreWeave bonds" は8〜10月の記事のみ）。
- 市場全体: 新興国の株・通貨も下落（Bloomberg 11/16）。VIX・ハイイールド債の数字は取得不可。「〇〇ショック」の呼び名は見つからなかった（見出しは取得できず）。

## 引け後・時間外の材料
- SNDK: 時間外 +0.5%。新しい材料の見出しは見つからなかった。
- AMD: 時間外 −0.0%。新しい材料の見出しは見つからなかった。
- 時間外に±5%以上動いた監視銘柄はなし（headlines.md 0節）。

## SNDK（保有）
- 11/16: 「SanDisk Falls 7% as AI Chip Selloff Hits Memory Stocks Despite Evercore's $2,500 Target; Micron and Western Digital Drop 6%」（Yahoo Finance）。
- 11/16: 「SK Hynix Is Down 16% in a Month」（24/7 Wall St.）。
- 悪材料: あり（メモリ株全体の売り。会社固有の悪材料は確認できず）

## AMD（保有）
- 11/16: World Labs の買収（82億ドル）を完了、フェイフェイ・リー氏がEVP兼チーフサイエンティストに（Yahoo Finance、TechPowerUp）。
- 11/13: 「Why Advanced Micro Devices Stock Is Down Today」（Yahoo Finance）、11/14「AMD Stock Sinks 9%」（Moomoo）。11/16「AMD, Nvidia, Micron Lead AI Trade Lower」（IBD）。
- 悪材料: あり（NVIDIAのCEO辞任後の半導体全体の売り。会社固有の悪材料は確認できず）

## NVDA
- 上の「テーマ全体の下げの原因」のとおり（CEO辞任 11/12、決算 11/17 引け後）。11/16「UBS Cuts Its Price Target on NVIDIA to $240」（富途牛牛）。
- 悪材料: あり（CEO辞任、目標株価の引き下げ）

## MU
- 11/16: 上の輸出規制の見出し（Boise Dev）。メモリ株の売りで約−6%（Yahoo Finance 11/16）。
- 悪材料: あり（輸出規制の見出し。中身は取得不可）

## ALAB
- 11/16: 「Sink 6.95% Despite Guiding Revenue Up 26% Next Quarter」（TradingView）、「Chip Selloff and Post-Earnings Profit-Taking」（Quiver Quantitative）。
- 悪材料: 確認できず（会社固有）

## LITE／MRVL
- 11/16: 「Lumentum Stocks Sink 8.32% as Marvell Slide Shrinks Deal Value Below $660」（GuruFocus）。全額株式の買収（821億ドル、Simply Wall St 11/15）のため、MRVL の下げで LITE の受け取り額が減る。
- MRVL 11/16: 「falls 6% as chip selloff deepens after Nvidia CEO exit」（Crypto Briefing）、Penguin Solutions とAIデータセンターの契約（GuruFocus）。
- 悪材料: 確認できず（会社固有）

## ARM
- 11/13: 「Arm Stock Tumbles 6% as Nvidia Board Courts CEO Rene Haas to Replace Jensen Huang」（BigGo Finance）。11/16 の固有の見出しは見つからなかった。
- 悪材料: あり（CEOがNVIDIAの後任候補と報道）

## NBIS／CRWV
- NBIS 11/12: 決算後に−16%。設備投資の増額と弱い見通し、売上の遅れ（CNBC、Barron's）。11/16: BofAが目標株価を310→265ドルに（Blockspace）。
- CRWV 11/16: 「CoreWeave, Oracle and Nebius Plunge as Nvidia Fallout Rattles AI Stocks」（GuruFocus）。
- 悪材料: あり（NBISの見通し・目標株価引き下げ）

## ASML
- 11/13: 「ASML Stocks Fall as NVIDIA Shake-Up Spills Into Chip Equipment」（TradingView）。11/16 の固有の見出しは見つからなかった。

## そのほかの急落銘柄（AMAT ANET CIEN COHR DDOG DELL GLW INTC KLAC LRCX MPWR RDDT SMCI STX TER VRT）
- 銘柄ごとの原因となるニュースは見つからなかった（headlines.md に見出しなし、または取得できず。個別の検索はしていない）。同じ日にテーマの26銘柄が−5%以下で、上の全体の材料と同じ日の下げ。

## 監視外の注目銘柄
- HUM（医療保険）: 11/6 に2026年通期の調整後EPS見通しを「9.50ドル以上」に引き上げ、10/9 にBairdが格上げ（Trefis、検索）。11/10 に52週高値（24/7 Wall St.）。
- CAH（医薬品卸）: 11/6 時点で52週高値、1週+8.5%（Trefis、検索）。直近の原因の記事の日付は確認できず。
- WST（注射剤の容器・部品）: 第2四半期に通期見通しを引き上げ（2回連続）。11月の材料は取得不可。
- LH（臨床検査）: 11月の高値更新の原因は取得不可。
- ADP（給与計算）: 11月の高値更新の原因は取得不可。

## テーマ全体のニュース（直近1週間）
- 11/17 引け後に NVIDIA 決算（暫定CEOのもとで初）。今週 Anthropic のIPO（Bloomberg 11/16）。
- 11/11: CoreWeave の見通しでAI投資の懸念が和らぎ MU +13%（Benzinga）。
- 11/16: Microsoft が Anthropic に10億ドル（GuruFocus）。

# ニュースの見出し（プログラムが自動で取得）

- Googleニュース（日付を指定）とYahooファイナンスの見出しを `tools/news_headlines.py` が自動で並べたもの。日付は米国東部時間の配信日（引け後の記事は翌日付）。原因の判断・売買の判断はしていない。
- 調べた銘柄の選び方: ①保有 ②今日の候補 ③時間外に±5%以上動いた監視銘柄 は全部、④引けまでに大きく動いた銘柄（1週で±5%のグループの上位3・1日で±7%）は合計12銘柄まで。
- 1週で−5%以下のグループ: 半導体製造装置・材料・設計ソフト・計測（-5.5%）
- 1週で+5%以上のグループ: なし

## 0. 時間外（引け後）の値動き（2026-11-16 の引けから、Yahoo。±3%以上の監視銘柄と、保有・候補は全部）

| 銘柄 | 区分 | 引け | 時間外 | 騰落率 |
|---|---|---|---|---|
| SNDK | 保有 | 808.93 | 813.39（17:19 ET） | +0.5% |
| AMD | 保有 | 504.37 | 504.29（17:19 ET） | -0.0% |

## 1. 市場全体（2026-11-16）

### 市場全体（英語のまとめ記事）
検索語: `stocks Wall Street close Nasdaq`
- 11/16 Kiplinger | Nasdaq Falls 626 Points to Start Nvidia-Anthropic Week: Stock Market Today
- 11/16 The Motley Fool | Stock Market Midday, Nov. 16: Nasdaq Tumbles as Wall Street Braces for Nvidia Earnings and Bitcoin Slides
- 11/16 24/7 Wall St. | Stock Market Today: Nasdaq-100 Sinks 1% as Nvidia Faces Its First Earnings Without Jensen Huang
- 11/16 Benzinga | Stock Market Today: Dow Jones, S&P 500, Nasdaq 100 Futures Trade Fall as Scott Bessent Presses Nvidia Ove
- 11/16 Yahoo Finance | Prediction: A Stock Market Crash Is Coming Eventually. Here's What Investors Should Do Based on What Happened in the Last 3 Crashes.

### 市場全体（Stock Market Today）
検索語: `"stock market today"`
- 11/16 Bloomberg.com | Stocks Fall Before Nvidia Earnings, Anthropic IPO: Markets Wrap
- 11/16 Eurasia Business News | U.S. Stock Market Today, November 16, 2026: Nvidia Earnings Loom as Oil Slips and Gold Struggles

### 市場全体（日本語のまとめ記事）
検索語: `米国株式市場 OR NY株`
- 11/16 Yahoo!ニュース | NY株大幅反落 ハイテク株に売り
- 11/16 時事ドットコム | ＮＹ株大幅反落、７３９ドル安 エヌビディア混乱でリスク回避
- 11/16 沖縄タイムス社 | ＮＹ株大幅反落、７３９ドル安
- 11/16 ニューズウィーク日本版 | 米国株式市場＝大幅安、ＡＩ懸念で エヌビディア決算に注目

### 半導体・AI株（英語）
検索語: `chip stocks OR semiconductor stocks OR AI stocks`
- （取得できなかった）

### 信用（社債・借金）
検索語: `AI debt OR bonds OR credit spreads OR CDS`
- 11/16 Invesco | Asia Fixed Income Investment Outlook – Quarterly Update
- 11/16 www.trendingtopics.eu | A.I. Stocks After the Sell-Off: What Generali Investments, Morgan Stanley and TS Lombard Advise Investors Now
- 11/16 MarketBeat | Meta's Access to Capital Remains Strong, But Borrowing Is Becoming More Expensive
- 11/16 Global Finance Magazine | Will a December Rate Hike Spur Corporate Debt Refinancing?
- 11/16 Bloomberg.com | Emerging-Market Stocks, Currencies Fall as AI Concerns Persist

### 「〇〇ショック」の呼び名（日本語）
検索語: `ショック 株`
- （取得できなかった）

### 引け後・時間外の動き（英語）
検索語: `"after hours" OR "after the bell" OR "extended trading" stocks`
- 11/16 TradingView | Stem shares sink 18% after-hours post $10M Athena IP sale to Voltus
- 11/16 Yahoo Finance | JPMorgan and DBS customers can now move tokenized dollars after hours
- 11/16 ChartMill | Unusual Volume Market Movers for November 16, 2026
- 11/16 BigGo Finance | Nvidia Leadership Turmoil Persists: AI Stocks Broadly Sold Off, Nasdaq Opens Down 1.4%
- 11/16 Benzinga | Tyson Foods, Aramark and 3 Stocks to Watch Heading Into Monday
- 11/16 ChartMill | Top US Stock Movers in Today's Session: OPENL Up 106.0%, FCUV Down 38.7%
- 11/16 TradingKey | Apple Sets a Record Close at $356.27 as Tech Sells Off, and AAPL Now Eyes $363.34
- 11/16 24/7 Wall St. | 3 Industrial Dividend Stocks Built to Keep Raising Their Payouts

### 引け後・時間外の動き（日本語）
検索語: `時間外 決算 株`
- （取得できなかった）

### 買収・合併（英語）
検索語: `acquisition OR acquire OR merger OR takeover chip OR semiconductor OR AI OR optical`
- 11/16 Yahoo Finance | AMD finalizes $8.2 billion World Labs acquisition, adds 'godmother of AI' as EVP and chief scientist
- 11/16 citybiz | AMD Completes World Labs Acquisition, Names Fei-Fei Li Chief Scientist
- 11/16 The Information | OpenAI Explored $5 Billion–Plus Acquisition of Startup That Decodes How AI ‘Thinks’
- 11/16 TradingView | GPRO: Revenue fell sharply and losses widened as the Starman Optical merger moved forward
- 11/16 TechPowerUp | AMD Completes Acquisition of World Labs
- 11/16 The Manila Times | Valor Energy Inc. Closes Acquisition of 18MW Computing Center in Youngstown, Ohio, Accelerating AI Data Center Expansion
- 11/16 Unite.AI | AMD Closes World Labs Acquisition and Names Fei-Fei Li Chief Scientist

## 2. 保有・候補・時間外で大きく動いた銘柄（2026-11-10〜2026-11-16 の見出し）

### SNDK（Sandisk Corporation、保有、AIサーバー・ストレージ・メモリ・端末、前日比 -8.6%、1週 -8.7%、時間外 +0.5%）

#### Googleニュース
検索語: `Sandisk stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/12 The Motley Fool | Sandisk Stock Is Back Above the $900 Price I Set for Buying It. Here's Why I'm Holding Off.
- 11/13 Trefis | SanDisk Stock At $937: Why So Cheap?
- 11/16 Yahoo Finance | SanDisk Falls 7% as AI Chip Selloff Hits Memory Stocks Despite Evercore’s $2,500 Target; Micron and Western Digital Drop 6%
- 11/16 Investing.com | Why is SanDisk stock sliding today?

#### Yahooファイナンス
検索語: `SNDK`
- 11/16 24/7 Wall St. | SK Hynix Is Down 16% in a Month. What Will It Take to Get SKHY Stock Back to $150?
- 11/16 Barrons.com | AI Trade Is Tanking the S&P 500, But Average Stock Sees Monthly Gains
- 11/16 Barrons.com | Nvidia, Sandisk, SpaceX, L3Harris, Strategy, Tyson, and More Stocks That Explain Today’s Market

### AMD（Advanced Micro Devices, Inc.、保有、半導体、前日比 -5.6%、1週 -0.8%、時間外 -0.0%）

#### Googleニュース
検索語: `Advanced Micro Devices stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/11 The Motley Fool | Why Advanced Micro Devices Stock Popped Today
- 11/13 Yahoo Finance | Why Advanced Micro Devices Stock Is Down Today
- 11/14 Moomoo | Advanced Micro Devices (AMD) Stock Sinks 9%: What the Options Flow and Dark Pools Say Now
- 11/16 Trefis | Why Did AMD Stock Fall Nearly 9%?

#### Yahooファイナンス
検索語: `AMD`
- 11/16 GuruFocus.com | David Tepper's Top Q3 2026 Move: Space Exploration Technologies Corp at a 6.93% Portfolio Impact
- 11/16 GuruFocus.com | Microsoft Stocks Move Lower as $1 Billion Anthropic Bet Precedes Ignite
- 11/16 Investor's Business Daily | Dow Jones Futures: AMD, Nvidia, Micron Lead AI Trade Lower With Nvidia Earnings On Deck

## 3. 引けまでに大きく下げた銘柄（2026-11-10〜2026-11-16 の見出し）

### Q（Qnity Electronics, Inc.、半導体製造装置・材料・設計ソフト・計測、前日比 -2.9%、1週 -8.1%、時間外 -0.0%）

#### Googleニュース
検索語: `Qnity Electronics stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- （取得できなかった）

#### Yahooファイナンス
検索語: `Q`
- （新しい見出しなし）

### CDNS（Cadence Design Systems, Inc.、半導体製造装置・材料・設計ソフト・計測、前日比 -4.2%、1週 -8.1%、時間外 -1.4%）

#### Googleニュース
検索語: `Cadence Design Systems stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- （取得できなかった）

#### Yahooファイナンス
検索語: `CDNS`
- 11/11 Simply Wall St. | Cadence Design Systems (CDNS) Launches OrCAD Xplore, Is It Trading At A Discount?
- 11/11 Simply Wall St. | Cadence Design Systems (CDNS) Stock Could Be Overvalued On Fresh AI Design Platform News
- 11/11 Zacks | Wall Street Analysts Think Cadence (CDNS) Is a Good Investment: Is It?

### ASML（ASML Holding N.V.、半導体製造装置・材料・設計ソフト・計測、前日比 -5.9%、1週 -7.0%、時間外 +0.2%）

#### Googleニュース
検索語: `ASML stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/13 TradingView | ASML Stocks Fall as NVIDIA Shake-Up Spills Into Chip Equipment
- 11/13 Stocktwits | ASML Holding NV (ASML) News, Articles, Events & Latest Updates
- 11/13 Yahoo Finance | XNDU Stock Fell From $42 to $2.80. GlobalFoundries and ASML May Explain the Bounce Case
- 11/14 TIKR.com | ASML Soars 10% in a Week as Chip Stocks Bounce and Musk’s Terafab Eyes a Million Wafers

#### Yahooファイナンス
検索語: `ASML`
- 11/14 Motley Fool | Prediction: ASML Will Join the $800 Billion Club in 2029

### ALAB（Astera Labs, Inc.、半導体、前日比 -8.8%、1週 -6.7%、時間外 +0.2%）

#### Googleニュース
検索語: `Astera Labs stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/13 Yahoo Finance | What Would A Short Seller Say About Astera Labs?
- 11/14 TIKR.com | Astera Labs Soars 16% in a Week as Chips Rebound: Scorpio X Eyes a $1 Billion Run Rate
- 11/16 TradingView | Astera Labs Stocks Sink 6.95% Despite Guiding Revenue Up 26% Next Quarter
- 11/16 Quiver Quantitative | Astera Labs Slides as Chip Selloff and Post-Earnings Profit-Taking Weigh on Shares

#### Yahooファイナンス
検索語: `ALAB`
- 11/14 Simply Wall St. | Astera Labs (ALAB) Stock May Be 21% Below Fair Value Despite Strong Q4 Guidance
- 11/14 TIKR | A $13 Billion Hedge Fund Dumps These 3 Stocks

### LITE（Lumentum Holdings Inc.、光・通信・ネットワーク、前日比 -8.5%、1週 -8.4%、時間外 +0.1%）

#### Googleニュース
検索語: `Lumentum stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- （取得できなかった）

#### Yahooファイナンス
検索語: `LITE`
- 11/15 Motley Fool | Marvell’s Trillion-Dollar Target
- 11/15 Simply Wall St. | Lumentum Holdings (LITE) Heads Into An $82.1 Billion All Stock Takeover

### CIEN（Ciena Corporation、光・通信・ネットワーク、前日比 -8.2%、1週 -4.4%、時間外 -0.3%）

#### Googleニュース
検索語: `Ciena stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- （取得できなかった）

#### Yahooファイナンス
検索語: `CIEN`
- 11/13 Zacks | Is Nokia Attractive as AI Growth Meets Valuation and Execution Risks?
- 11/14 Simply Wall St. | Is Ciena (CIEN) Too Expensive After Its 7x Run?
- 11/14 Simply Wall St. | Is Ciena (CIEN) Undervalued Going Into Its December 10 Earnings?

### ARM（Arm Holdings plc、半導体、前日比 -8.1%、1週 -6.0%、時間外 -0.1%）

#### Googleニュース
検索語: `Arm stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/10 Yahoo Finance | Don’t Chase the Arm Stock Dip Yet. What Patient Investors Should Wait for Before They Buy.
- 11/13 Traders Union | ARM slides over 5% as the stock trades below key moving averages and faces ongoing selling pressure
- 11/13 BigGo Finance | Arm Stock Tumbles 6% as Nvidia Board Courts CEO Rene Haas to Replace Jensen Huang
- 11/16 24/7 Wall St. | Arm Stock Could Be Worth Much More if These 3 Catalysts Materialize

#### Yahooファイナンス
検索語: `ARM`
- 11/15 Benzinga | Jensen Huang Could Return to Nvidia as Silicon Valley Plans ‘War Room,’ While Anthony Scaramucci Says ‘Not Happening’

### MU（Micron Technology, Inc.、半導体、前日比 -7.6%、1週 -1.9%、時間外 +0.2%）

#### Googleニュース
検索語: `Micron stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/10 Barron's | Micron Stock Drops Again. The Case for It Soaring 148%.
- 11/11 Yahoo Finance | Why Micron Stock Popped Today
- 11/11 Benzinga | Micron Stock Jumps 13% as CoreWeave Outlook Eases AI Spending Fears
- 11/16 Boise Dev | Micron stock tumbles as Trump admin. cuts a loophole allowing China access to advanced chips

#### Yahooファイナンス
検索語: `MU`
- 11/16 Insider Monkey | 5 Unstoppable Stocks to Buy According to Analysts

### NBIS（Nebius Group N.V.、AIプラットフォーム・クラウド、前日比 -7.6%、1週 -24.3%、時間外 +0.9%）

#### Googleニュース
検索語: `Nebius stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/12 Barron's | Nebius Stock Plummets After Earnings as CEO Warns of Revenue Delay
- 11/12 CNBC | Nebius falls 16% as company expects increased 2026 capex spend, issues weak outlook
- 11/12 Yahoo Finance | Nebius shares fall despite beating Q3 estimates
- 11/13 The Motley Fool | Why Nebius Group Stock Plunged (Again) Today

#### Yahooファイナンス
検索語: `NBIS`
- 11/16 24/7 Wall St. | A 64-Year-Old Bought Nebius at Its Peak and Lost $29,721. The IRS Lets Her Use It Before Dec. 31
- 11/16 Barrons.com | Nebius Has a Spending Problem. Demand Isn’t an Issue, Say Analysts.
- 11/16 Blockspace | BofA cuts Nebius price target to $265 from $310 on capacity delays, keeps Buy

### MRVL（Marvell Technology, Inc.、半導体、前日比 -7.3%、1週 -6.0%、時間外 +0.0%）

#### Googleニュース
検索語: `Marvell stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/11 The Motley Fool | Why Is Marvell Stock Crashing, and is it a Buying Opportunity?
- 11/13 24/7 Wall St. | Marvell Stock Could Have a Bigger AI Opportunity Than Investors Realize
- 11/16 Crypto Briefing | Marvell Technology stock falls 6% as chip selloff deepens after Nvidia CEO exit

#### Yahooファイナンス
検索語: `MRVL`
- 11/16 GuruFocus.com | CoreWeave, Oracle and Nebius Plunge as Nvidia Fallout Rattles AI Stocks
- 11/16 GuruFocus.com | Lumentum Stocks Sink 8.32% as Marvell Slide Shrinks Deal Value Below $660
- 11/16 GuruFocus.com | Marvell Stock in Focus After New AI Data Center Deal With Penguin Solutions
