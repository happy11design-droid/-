# テーマ監視 2026-11-12

# 判定のまとめ（ルールの判定と著者の判定を分けて表示）

- **ルールの判定**: 採用した売買ルール（スクリプト）が数値で決めたもの。損切りは買値の15%下の逆指値（日中に届けばその場で売れる）。
- **著者の判定**: ノートブックの著者の回答。買いは注文を止める理由があるときだけ【様子見】、保有はルールより早く手じまう理由があるときだけ【売り】。根拠は下の「著者の回答（全文）」。
- 2つが食い違うときに、どちらに従うかはユーザーが決める。

- **テーマ全体の急落（S2・記録だけ）: あり（S2）**（SOXが直近60取引日の最高値から -20.5%）。S2の日の順張りの候補には「S2なら見送る形」と付ける（売買のルールは変えない。記録してから採用を決める。2026-10-14）

- **特殊な下げ（記録だけ）: あり（特殊な下げ）**（2026-10-16から）（SOXが直近60取引日の最高値から -20.5%、前の1年の大きな上げ・雇用の弱さ・物価の再加速のうち 2つ）。1995年〜では、この形の後にSOXの下げが長引くことが多かった（後知恵を含む）。売買のルールは変えない（2026-11-03）

## 保有銘柄

| 銘柄 | ルール | 損益 | 時間外 | ルールの判定 | ルールの判定の理由 | 著者の判定 |
|---|---|---|---|---|---|---|
| SNDK | ルール外（ユーザーの判断。この日はどのルールの合図もなし） | -31.6% | +0.0% | **売り** | 終値 937.46 が損切り価格 1165.61 以下 | 【未判定】（） |
| AMD | ボリンジャーIII | +6.4% | -1.1% | 保有継続 | 損切り 467.47（終値から -20.1%） | 【保有継続】（ボリンジャー） |

## 候補の判定（並びは上の「買う順番」の表と同じ）

- 並びは上の「買う順番」の表と同じ（RSの高い順。勝率の高い順ではない）。注文の値段・株数・逆指値は上の表を見る。勝率・1回平均は、そのルールの過去の成績（後知恵なしの監視銘柄・2015年〜の全部の合図）。
- 空き枠: 3（同時保有4銘柄まで。保有2、うちルールの売り1）。著者が【様子見】の候補を見送るかはユーザーが決める。

| 順 | 銘柄 | ルール | 過去の勝率 | 過去の1回平均 | RS | 時間外 | ルールの判定 | 著者の判定 |
|---|---|---|---|---|---|---|---|---|
| 1 | NVDA（エヌビディア） | 逆張り: ボリンジャー メソッドIII | 68% | +1.5% | 6 | -0.1% | 買い（翌日の寄り付き） | 【買い】（ボリンジャー） |

- 時間外: 前の取引日の引けから、引け後（米国東部時間16〜20時）の最後の値までの騰落率（Yahoo。±5%以上は太字）。寄り付きの値段は、表の注文の目安（前日の終値で計算）から大きくずれることがある。原因の見出しは「ニュースの見出し」の節。

# 著者の回答（全文）

## 0_テーマの局面_ワインスタイン

1. **テーマ全体の局面**: 【ステージ3】（第2ステージの大幅上昇を経て30週移動平均線が水平化し、指数が線を下回って天井圏の保ち合いを形成しているため、第2章 [1]）

2. **グループごとの局面**:
- 半導体｜ステージ3｜30週線横ばい・下振れ（第2章 [1]）
- 半導体製造装置・材料・設計ソフト・計測｜ステージ3｜30週線横ばい・線の下（第2章 [1]）
- AIサーバー・ストレージ・メモリ・端末｜ステージ3｜30週線横ばい・下振れ（第2章 [1]）
- 光・通信・ネットワーク｜ステージ3｜30週線横ばい・線の下（第2章 [1]）
- データセンターの電力・冷却・部品・受託製造・建設｜ステージ3｜30週線横ばい・下振れ（第2章 [1]）
- AIプラットフォーム・クラウド｜ステージ3｜30週線横ばい・保ち合い（第2章 [1]）
- AIソフト・セキュリティ・ITサービス｜ステージ2｜30週線上昇・線の上を維持（第2章 [2]）

3. **転換の兆し**: 出ている [1]。30週線の水平化 [1]、指数の移動平均線割れ（乖離-6.0%〜-11.8%） [1]、対S&P500の相対的な強さ（RS）の悪化 [3, 4] が第3ステージ天井形成および第4ステージ突入警戒の基準に合致する（第2章、第4章、第6章 [1, 3, 5]）。なお、50日線警告、急落S2、特殊な下げ、ニュース分析はマニュアルに規定なし [6]。

4. **テーマの外**: 判定不能（データ省略のため事実を創作せず判定不能とする）。

（全体の版が空の応答だったため、1〜2節だけの短い版で送り直した回答。ヒートマップ・急騰急落・ニュースは渡していない）

## 1_ボリンジャー_prompt_1

## AMD
1. **投資判断**: 【保有継続】（ルールより早く手じまう根拠なし）
2. **止める理由の確認**:
   - 本が禁じる形・状況｜なし｜M型トップ等の天井パターンは未発生（第13章、第20章） [1, 2]
   - 避けるべき時期（決算など）｜なし｜次回決算2027-02-02で遠く、時期規定もなし（マニュアルに規定なし） [3, 4]
   - 悪材料｜なし｜資金流入で逆行高しており早期手じまいの悪材料なし（用語集、11/12） [3]
3. **現状パターンと価格**:
   - `現状パターン: なし（保有中）`
   - `売りの予約注文: 〈指値売り〉606.35（現在値比 +3.6%）`
4. **注意点**: メソッドIIIの目標である上部バンド（606.35）到達時のタグと指標動向に注目すること [1, 5]。

## 1_ボリンジャー_prompt_2

## NVDA
1. **投資判断**: 【買い】（メソッドIIIの条件成立）
2. **止める理由の確認**:
   - 本が禁じる形・状況｜なし｜第20章（%b<0.05かつ21日II%>0は正当な買いセットアップ [1, 2]）
   - 避けるべき時期（決算など）｜なし｜マニュアルに規定なし [3]
   - 悪材料｜なし｜マニュアルに規定なし（第15章でニュースは触媒とされるのみ [4]）
3. **現状パターンと価格**:
   - `現状パターン: A（メソッドIII条件成立）`
   - A: `本日の発注: 翌日の寄り付きで成行`
4. **注意点**: 直近安値付近に損切りを置き、上部バンド到達を利食い目標とする（第20章）[5]。

# スキャン（数値と事実）


- 監視銘柄 87（判定できたのは 87）。
- この一覧は数値と事実だけ。売買の判断は著者のノートブックが行う。

## 1. テーマ（グループ）の強さ

| グループ | 銘柄数 | 1週 | 1カ月 | 3カ月 | 3カ月の順位 | 50日線より上の銘柄の割合 | グループ指数の30週線の局面（線との乖離、4週前からの線の傾き） |
|---|---|---|---|---|---|---|---|
| 半導体 | 16 | +17.1% | +1.4% | -7.1% | 3位 | 44% | 横ばい（-6.0%、+4.8%） |
| 半導体製造装置・材料・設計ソフト・計測 | 9 | +16.7% | -12.0% | -18.7% | 5位 | 33% | 横ばい（-11.8%、+1.1%） |
| AIサーバー・ストレージ・メモリ・端末 | 9 | +13.6% | -20.5% | -24.3% | 6位 | 11% | 横ばい（-8.1%、+6.4%） |
| 光・通信・ネットワーク | 9 | +15.5% | -11.9% | -27.9% | 7位 | 22% | 横ばい（-11.6%、+1.0%） |
| データセンターの電力・冷却・部品・受託製造・建設 | 19 | +8.4% | -5.9% | -11.5% | 4位 | 26% | 横ばい（-7.2%、+0.4%） |
| AIプラットフォーム・クラウド | 11 | +6.9% | -2.6% | +1.8% | 1位 | 45% | 横ばい（-2.6%、+1.4%） |
| AIソフト・セキュリティ・ITサービス | 14 | +2.1% | -7.8% | -4.0% | 2位 | 29% | 上昇（+6.5%、+4.9%） |

## 2. テーマ全体の状態と早めの警告

- 市場全体の30週線による局面: S&P500指数 **上昇**／NASDAQ100指数 **横ばい**（急落の底で買うルールは、過去の検証で下落相場で特に強く、横ばいの相場では負けていた）
- **2倍ETFを使う局面（案1、2026-10-13 採用）: S&P500の20週線（100日線）で 横ばい** → 新しく買う銘柄は、2倍ETFのある銘柄も元の株で買う（保有中のETFはそのまま）（SPY 757.12、100日線 758.95、20日前の線 755.67。上昇＝線より上かつ線が上向き）
- **テーマ全体の急落（S2、記録だけ。売買のルールは変えない）: あり（S2）**（SOX 10506.67、直近60取引日の最高値 13217.82 から -20.5%。S2＝最高値から−10%以上）。S2のときに「順張りの新しい買いだけ止める」形を記録で比べる（2026-10-14 ユーザー決定。バックテストでは年率は上がったが2つの期間ではどちらも少し下回ったため、記録してから採用を決める。`バックテスト結果/テーマ全体の急落を検知して手じまう・買いを止める.md`）
- **グループごとの悪いニュースの流れ（記録だけ。売買のルールは変えない。2026-10-30〜2026-11-12）**: 会社の名前と悪い言葉（格下げ・目標株価の引き下げ・見通しの引き下げ・予想未達・急落・信用・訴訟・輸出規制など）の両方がある見出しの数（Googleニュース、`tools/news_headlines.py`）。10取引日の1銘柄あたりが一番多いグループに印。2026年7〜11月の確かめでは、印のグループの合図は10月は成績が悪かった（1回平均 −10.6%、ほか −5.6%）が、7〜9月は逆に良かった（+11.6%、ほか +6.7%）（`バックテスト結果/実際の運用の期間の確認_2026-10-23/グループの悪いニュースの流れ.md`。2026-11-04）

| グループ | 悪いニュース 直近5取引日 | その前の5取引日 | 10取引日の1銘柄あたり | 良いニュース 10取引日（1銘柄あたり） | 印 |
|---|---|---|---|---|---|
| 半導体（16） | 51件 | 12件 | 3.9 | 25件（1.6） | **悪いニュースが続いている** |
| 光・通信・ネットワーク（9） | 10件 | 15件 | 2.8 | 10件（1.1） |  |
| AIサーバー・ストレージ・メモリ・端末（9） | 4件 | 5件 | 1.0 | 42件（4.7） | **良いニュースが多い** |
| AIプラットフォーム・クラウド（11） | 3件 | 5件 | 0.7 | 2件（0.2） |  |
| AIソフト・セキュリティ・ITサービス（14） | 1件 | 4件 | 0.4 | 10件（0.7） |  |
| データセンターの電力・冷却・部品・受託製造・建設（19） | 0件 | 5件 | 0.3 | 15件（0.8） |  |
| 半導体製造装置・材料・設計ソフト・計測（9） | 0件 | 2件 | 0.2 | 3件（0.3） |  |

印のグループ（半導体）の最近の見出し: 2026-11-12 Nvidia Price Target Cut to $230.00/Share From $330.00 by RBC Capital（富途牛牛）／2026-11-12 NVIDIA Corporation Stock 12‑Month Price Target Cut to $309.21, Implies 78% Upside（TradingView）／2026-11-12 NVIDIA Corporation Stock 12‑Month Price Target Cut to $300.13, Implies 73% Upside（TradingView）

良いニュースが多いグループ（AIサーバー・ストレージ・メモリ・端末）の最近の見出し: 2026-11-12 Apple TV 4K review: The best streamer for Apple fans, but I wouldn’t rush to upgrade（ZDNET）／2026-11-12 Apple supplier Foxconn posts record profit, raises outlook（Yahoo Finance Singapore）

- **特殊な下げ（記録だけ。売買のルールは変えない）: あり（特殊な下げ）**（2026-10-16から）。SOX は直近60取引日の最高値から -20.5%（−15%以下が条件）、●A 前の1年の上げ +108.5%（+80%以上）、・B 雇用の伸び 137千人/月（2026-10まで。10万人未満）、●C 物価 4.0%（2026-09。3か月前 3.7%。3.5%以上で再加速）＝2つ（2つ以上が条件）。1995年〜でSOXが−15%以下かつ条件2つ以上の日は、120日後にSOXが下だったのが69%・250日後が70%（中央値 −33%）、AI以外の8業種の平均は250日後 −7%。ただし条件は過去を見て選んだもの（条件が2つ以上の局面は約5回）で、2026年7〜9月にこの間テーマを買わないと、その後の戻りを逃して2026年の成績は下がった（`バックテスト結果/実際の運用の期間の確認_2026-10-23/特殊な下げと過去の似た下げ.md`。2026-11-03）
- テーマ指数（監視銘柄の等金額平均）の30週線による局面: **横ばい**（上昇＝線より上かつ上向き、下落＝線より下かつ下向き、それ以外＝横ばい。ワインスタインのステージの近似）
- テーマ指数と50日線: 50日線より下（乖離 -6.5%）
- S&P500に対する相対的な強さ: 50日平均より下（S&P500より弱い）
- 監視銘柄のうち50日線より上の割合: 31%
- 警告（割合が40%未満かつテーマ指数が50日線より下）: **出ている**
- 参考（バックテスト）: 30週線の「下落」は高値から10〜33%下げた後に出る遅い判定。50日線・割合・相対的な強さは高値から2〜8%で出るが、誤報が年15回以上ある。警告中に新しい買いを止めると、押し目買い（ボリンジャーIII）の成績は大きく下がった（`バックテスト結果/テーマ監視銘柄・直近3年.md` 11・12節）。

## 3. ヒートマップ（Finviz、全米の業種別の騰落率）

3カ月の騰落率の上位15業種（テーマの外で強くなっている業種の確認用）:

| 順位 | 業種 | 1週 | 1カ月 | 3カ月 | 6カ月 | 1年 |
|---|---|---|---|---|---|---|
| 1 | Health Information Services | +1.2% | +7.8% | +21.5% | +60.9% | +10.6% |
| 2 | Medical Distribution | +1.9% | +8.6% | +17.9% | +39.9% | +18.1% |
| 3 | Paper & Paper Products | +4.6% | +14.3% | +16.8% | +12.8% | +6.1% |
| 4 | Advertising Agencies | +8.1% | +35.8% | +16.0% | -9.6% | -27.0% |
| 5 | Consumer Electronics | +2.9% | +3.6% | +15.7% | +18.9% | +26.5% |
| 6 | Insurance - Diversified | +3.0% | +11.4% | +15.6% | +20.4% | +18.3% |
| 7 | Diagnostics & Research | +1.8% | +3.0% | +15.6% | +50.5% | +20.7% |
| 8 | Lodging | +1.3% | +13.6% | +15.4% | +17.1% | +35.1% |
| 9 | Real Estate - Diversified | +3.9% | +13.7% | +13.6% | +16.8% | +7.2% |
| 10 | Drug Manufacturers - General | +2.0% | +10.4% | +12.9% | +24.7% | +31.4% |
| 11 | Medical Care Facilities | -1.5% | +6.1% | +12.5% | +18.9% | +20.7% |
| 12 | REIT - Hotel & Motel | +4.0% | +12.0% | +11.8% | +28.4% | +48.3% |
| 13 | Financial Data & Stock Exchanges | +0.4% | +11.7% | +11.5% | +11.3% | +3.7% |
| 14 | Household & Personal Products | -0.3% | +6.9% | +11.2% | +17.4% | +11.8% |
| 15 | Auto Manufacturers | +9.7% | +7.5% | +11.1% | -7.8% | -9.5% |

テーマの業種の順位（3カ月、全144業種中）: Semiconductors 127位、Semiconductor Equipment & Materials 140位、Computer Hardware 143位、Communication Equipment 120位、Electronic Components 131位、Software - Infrastructure 62位、Software - Application 64位、Internet Content & Information 108位

## 4. 急騰・急落した銘柄（前日比±5%以上、または出来高が50日平均の2倍以上）

原因のニュースをサブエージェントが調べ、候補・保有銘柄の判定材料として著者に渡す。急騰・急落そのものは売買の合図にしない（後知恵のないS&P500全体のバックテストでは、急騰の翌日に買うルールは年率7%、急落の翌日に買うルールは年率9〜10%で、採用した3つのルールより優れていなかった）。

| 銘柄 | グループ | 前日比 | 出来高（50日平均の倍） | 終値 | 50日線 | RS | 局面 |
|---|---|---|---|---|---|---|---|
| NBIS | AIプラットフォーム・クラウド | -16.8% | 3.4倍 | 128.64 | 下 | 8 | 下げ |
| SMCI | AIサーバー・ストレージ・メモリ・端末 | -11.3% | 2.9倍 | 26.99 | 下 | 3 | 下げ |
| CRWV | AIプラットフォーム・クラウド | -6.9% | 2.2倍 | 56.60 | 下 | 0 | 下落相場 |
| AMD | 半導体 | +5.9% | 2.2倍 | 585.30 | 上 | 99 | 上昇相場 |
| RDDT | AIソフト・セキュリティ・ITサービス | -5.8% | 1.0倍 | 99.55 | 下 | 1 | 下落相場 |
| AVGO | 半導体 | +5.5% | 1.7倍 | 364.36 | 上 | 27 | レンジ |
| ANET | 光・通信・ネットワーク | +5.1% | 1.5倍 | 206.63 | 上 | 92 | レンジ |
| NVDA | 半導体 | -4.3% | 5.6倍 | 166.19 | 下 | 6 | 下げ |

- 局面（判定式はClaudeが置いたもの）: **上昇相場**＝終値 > 50日線 > 200日線、50日線が20取引日前より2%以上高い、ADX(14) ≧ 20／**下落相場**＝終値 < 50日線 < 200日線、50日線が20取引日前より2%以上低い、ADX(14) ≧ 20／**上げ**＝それ以外で終値が50日線より上、かつ50日線が10取引日前より上か20日線が5取引日前より上／**下げ**＝それ以外で終値が50日線より下、かつ50日線が10取引日前より下か20日線が5取引日前より下（急な下げの初めは50日線がまだ上向きのため20日線でも見る）／**レンジ**＝どれにも当たらない（2026-11-05 から5つ。それまでは上昇相場とレンジの2つだけで、下げている銘柄もレンジと出ていた）。

## 4-2. 監視外の注目銘柄（S&P500・NASDAQ100のうち監視銘柄に入っていない銘柄）

条件: 流動性（株価5ドル以上・50日平均出来高25万株以上）があり、(a) 前日比+8%以上かつ出来高が50日平均の2倍以上、または (b) 終値が直前1年の最高値（終値）を上回り、RS≧90。RSの高い順に5銘柄（ニュースを調べる）。監視銘柄に入れるかはユーザーが決める。

| 銘柄 | 種類 | 前日比 | 出来高（50日平均の倍） | RS | 終値 |
|---|---|---|---|---|---|
| BDX | 1年の高値更新 | +0.6% | 1.0倍 | 93 | 215.71 |
| LH | 1年の高値更新 | +0.0% | 0.7倍 | 93 | 372.32 |
| CAH | 1年の高値更新 | +0.2% | 0.7倍 | 91 | 278.14 |

## 5. 保有銘柄の手じまい条件（`新分析ツール/保有銘柄.md`）

| 銘柄 | ルール | 買った日 | 買値 | 終値 | 損益 | 損切り価格（買値の15%下、逆指値） | ルールの手じまい条件 | 出来高2倍の大陰線（買った後の直近5日） | 次回決算予定日 |
|---|---|---|---|---|---|---|---|---|---|
| SNDK | ルール外（ユーザーの判断。この日はどのルールの合図もなし） | 2026-10-21 | 1371.30 | 937.46 | -31.6% | 1165.61 | **損切り価格を下回った** ルールが不明（保有銘柄.md の「ルール」を確認） | なし | 2026-10-29 |
| AMD | ボリンジャーIII | 2026-10-21 | 549.97 | 585.30 | +6.4% | 467.47 | **出来高2倍の大陰線が 2026-11-05 に出た**（まだ持っていれば、次の寄り付きで全部売る） 売りの指値: 上部バンド 606.35（今夜この値に置き直す。届いた日に売れる）（2倍ETF AMUU で持っている場合も、判定は元の株 AMD の値段） | なし | 2027-02-02 |

- 出来高2倍の大陰線: 実体（始値−終値）が前日までのATR(14)の1.5倍以上、終値がその日の値幅の下25%以内、出来高が前日までの50日平均の2倍以上の日。**押し目（ボリンジャーIII）・急落の底の保有では売りのルール**: 出たら翌日の寄り付きで全部売り、空いた枠で次の合図を買う（2026-10-02 ユーザー決定。`バックテスト結果/やり直し_売りの合図の組み合わせ.md`。乱数3組とも年率が約+2ポイント、最大下落率もやや下がった）。ミネルヴィニ・新高値V2の保有では事実の表示（順張りに足しても良くならなかった）。

- 半分売りの合図（ミネルヴィニ・新高値V2の保有だけ）: 反転のローソク足（かぶせ線・弱気の包み足・宵の明星・流れ星）＋出来高が50日平均の1.5倍以上＋RSI(14)が前日か当日に70以上。買った後に最初に出た日の翌日の寄り付きで半分売り、残り半分は50日線割れ・損切り15%まで持つ（2026-10-01 ユーザー決定。`バックテスト結果/半分だけ売るとオニールの空き枠.md`）。

- かぶせ線（ミネルヴィニ・新高値V2の保有だけ）: 上昇中の陽線の翌日に、前日の高値より上で寄り付き、前日の陽線の真ん中より下（前日の始値より上）で引けた日。翌日の寄り付きで全部売り、空いた枠で次の合図を買う。半分売りより優先する（2026-10-01 ユーザー決定。`バックテスト結果/2倍ETFで売って買い直す.md`。順張りの売買の25%で出て、1回平均+2.0%、年率 21.4%→26.4%）。

## 5-2. 前日（2026-11-11の引け）の【買い（予約）】の確認

前日の【買い（予約）】はなし。

## 6. 候補（採用したルールの条件が成立＝A。予約（B）は2026-10-25から注文せず、節6-3に参考の表示だけ）

建玉の目安: 同時保有4銘柄まで、1銘柄に資金の25%（資金÷4）、損切りは買値の15%下（ユーザー決定 2026-09-29）。

**急落の底の指値に届いた銘柄（注文していれば約定。保有銘柄.md に買った日・値段を記録する。今日の候補には出さない）**: NVDA（2026-11-10の合図、指値 165.51、2026-11-12の安値 148.80。寄り付き 150.99 が指値より下だったので寄り付きで約定）

パターン: A＝最新の足で採用ルールの条件が成立（押し目・ミネルヴィニ・新高値V2は翌日の寄り付きで成行、急落の底は合図の日の終値の2%下に指値で3取引日待つ。2026-11-03 ユーザー採用）。条件の成立が目前の銘柄（B）は、予約の注文をやめたので節6-3に参考として出す（2026-10-25 ユーザー決定）。

| 銘柄 | グループ | パターン | 種類 | ルールの過去の成績 | 終値 | 前日比 | RS | 50日線の傾き | 局面 | 当てはまった条件 | 次回決算予定日 | 注文の目安 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| NVDA | 半導体 | A | 逆張り: ボリンジャー メソッドIII | 3位（勝率68%・1回平均+1.5%） | 166.19 | -4.3% | 6 | -3.2% | 下げ | %b=0.007（<0.05）、21日II%=+0.009（>0） | 2026-11-17（5日後）**決算が近い** | 翌日の寄り付きで買い。損切り: 買値の15%下。手じまい: 買った日の夜から、売りの指値をその日の上部バンド（今日 236.83）に置き、毎晩その日の値に置き直す。**元の株で買う**（2倍ETF NVDU のある銘柄だが、S&P500が20週線で「横ばい」の局面のため。案1）。**株数の目安: 14株**（2,384ドル÷166.19。今日の終値。寄り付きの値段で変わる）、購入金額 約2,327ドル |

- 局面（判定式はClaudeが置いたもの）: **上昇相場**＝終値 > 50日線 > 200日線、50日線が20取引日前より2%以上高い、ADX(14) ≧ 20／**下落相場**＝終値 < 50日線 < 200日線、50日線が20取引日前より2%以上低い、ADX(14) ≧ 20／**上げ**＝それ以外で終値が50日線より上、かつ50日線が10取引日前より上か20日線が5取引日前より上／**下げ**＝それ以外で終値が50日線より下、かつ50日線が10取引日前より下か20日線が5取引日前より下（急な下げの初めは50日線がまだ上向きのため20日線でも見る）／**レンジ**＝どれにも当たらない（2026-11-05 から5つ。それまでは上昇相場とレンジの2つだけで、下げている銘柄もレンジと出ていた）。

- 2倍ETF: 2倍ETFがある銘柄（ユーザーがムームー証券で買えることを確認した38銘柄のうち、目減りが年15%未満のもの）は、株の代わりに2倍ETFを買う（2026-10-04 ユーザー決定。`バックテスト結果/2倍ETFを使う決まり.md`。年率 約27%→約33%、確定した損益だけの最大下落率 約30%→約31%、含み損込みは約33%→約45%）。買う金額は株と同じ（資金の25%）。合図・損切り（元の株の買値の15%下＝ETFでは約30%下）・手じまいはすべて元の株の値段で判定する。指値・逆指値はETFの値段に直して置く。どのETFかは `新分析ツール/2倍ETFの対応表.json`（売買代金が1日500万ドル以上で、直近1年の目減りが一番小さいもの）。**2倍ETFで買うのは、S&P500が20週線（100日線）で「上昇」の局面のときだけ。横ばい・下落の局面では元の株で買う**（案1、2026-10-13 ユーザー採用。買う日に決め、買った後は局面が変わってもそのまま持つ。`バックテスト結果/流れ（市場の局面）を使う形.md`）。

- ルールの過去の成績: 今の売りのルールで、後知恵なしの監視銘柄・2015年〜の全部の合図の1回ごとの成績（2026-10-02計算、`新分析ツール/バックテスト結果/ルールごとの成績.md`）。順位は1回平均（1回の売買で平均いくら増えるか）の順。表はパターン（A→B）ごとに、この順位の良い順に並べた（表示の順番だけ。買う順番・件数の上限は変えていない。候補の選び方を変えても成績は変わらなかったため。2026-10-02 ユーザーの指示）。著者には渡さない。

- 悪いニュースが続いているグループ（半導体）の候補（記録だけ。売買のルールは変えない。著者には渡さない）: NVDA

- 候補の数: 空き枠3（同時保有4銘柄まで。保有2、うち今日ルールの売りが成立1）＋予備2件まで表に出した（2026-10-25 ユーザー決定）。省いた候補はない。

- テーマの外の候補（グループが「テーマの外」）: 監視銘柄の候補で枠が埋まらないときに使う（監視銘柄の候補を先に買う）。S&P500の今の構成銘柄のうち監視銘柄でない銘柄から、RS≧90・30週線が上向きで終値がその上・業種の3カ月の強さが上位20%の20銘柄を調べ、空き枠2つ分まで出した。バックテストでは、テーマの外の強い銘柄で空き枠を埋めると、テーマが弱い時期の成績が支えられた（`バックテスト結果/半導体・AIに特化した場合.md`。2026-10-01 ユーザー決定）。

- RS≧80の押し目（ボリンジャーIII）は、バックテストで成績がより安定していた（PF3.27、最大下落20%）。

## 6-3. 参考: 条件の成立が目前の銘柄（予約は注文しない・著者には送らない）

2026-10-25 ユーザー決定: 予約（逆指値・指値）の注文はやめ、参考の表示だけにする。毎朝のツールと同じ条件・値段で予約の約定をバックテストに入れると、どの形も年率が下がった（後知恵なし 35.7%→30.7〜34.2%、87銘柄 45.6%→34.2〜42.6%。`バックテスト結果/点検_2026-10-25/`）。引けで条件がそろえば、翌朝の節6に買いの候補（A）として出る。各ルールでRSの高い順に2件まで。

| 参考の銘柄 | グループ | 種類 | 終値 | 前日比 | RS | 当てはまった条件 | 条件がそろう目安の価格（注文はしない） |
|---|---|---|---|---|---|---|---|
| SWKS | 半導体 | ミネルヴィニ（ピボットの手前） | 90.03 | +2.7% | 95 | ピボット（ベースの高値、2026-09-23）92.80まで3.1%、ベース36日・調整幅21% | 92.80（この値を上回って引け、ほかの条件もそろうと翌朝の買いの候補（A）。目安） |
| ANET | 光・通信・ネットワーク | ミネルヴィニ（ピボットの手前） | 206.63 | +5.1% | 92 | ピボット（ベースの高値、2026-10-09）217.41まで5.2%、ベース24日・調整幅27% | 217.41（この値を上回って引け、ほかの条件もそろうと翌朝の買いの候補（A）。目安） |
| WDAY | AIソフト・セキュリティ・ITサービス | ボリンジャー メソッドIII（%bが0.05未満に近い） | 190.64 | -0.3% | 70 | %b=0.195（0.05まであと少し）、21日II%=+0.028（>0） | 186.77（この値より下で引けると翌朝の買いの候補（A）。目安） |
| SHOP | AIソフト・セキュリティ・ITサービス | ボリンジャー メソッドIII（%bが0.05未満に近い） | 146.78 | -1.7% | 68 | %b=0.199（0.05まであと少し）、21日II%=+0.040（>0） | 140.46（この値より下で引けると翌朝の買いの候補（A）。目安） |


# ニュース（サブエージェントの調査）

# ニュース調査（2026-11-12 の米国引けまで／作成 2026-11-13 JST）

## テーマ全体の下げの原因
- 当たる条件: 4節で監視銘柄4銘柄が−5%以下（NBIS・SMCI・CRWV・RDDT）、早めの警告とS2が出ている。
- きっかけ: NVIDIAのジェンスン・フアンCEOが辞任した（中国のスパイとされる人物との不倫問題。CFOのクレス氏が暫定CEO）（AFP・CBS News・NBC News 11/12、BigGo 11/12）。11/9から調査の報道で下げていた（CNN・NYT 11/9、CNBC 11/10）。報道の呼び名は「ジェンソン・ファン・ショック」（毎日経済 11/12）、「エヌビディアショック」（YouTube 11/12）。
- 広がった先: メモリ（Micron・Sandisk・SK Hynixが約3%安。Barron's・24/7 Wall St. 11/12）、ネオクラウド（NBISは自社の決算、SMCIは司法省の調査が重なった。CRWVはBarron's 11/12「Nvidia Danger Zone」の記事に名前あり）。アリババが香港で6.8%安（BigGo 11/12）。
- 反対に上げた銘柄: AMD・Broadcomは上げた（investingLive・Mitrade 11/12「AI trade changed hands」）。
- 市場全体: NYダウは189ドル安、ナスダックも下げた（Reuters・京都新聞 11/12）。トランプ大統領がイランへの軍事作戦を示唆して原油が上がったことと、利回りの急上昇も重なった（毎日経済・IBD 11/12）。VIX・ハイイールド債の数値は取得不可。
- 信用: 見出しは「BofA、信用市場はすでに瞬きした」（The Dark Side Of The Boom 11/12）、「半導体のCDS上乗せ幅が上昇」（Moomoo 11/12）、「AI債務の破綻がETFの材料に」（Advisor Perspectives 11/12）。CoreWeaveの社債利回りが15〜16%台という報道は10月のもの（CNBC・Reuters）。11/12時点の社債・CDSの数値は取得不可（検索語: 「CoreWeave bonds yield Nvidia Huang November 2026」）。
- 経済指標: 米CPIでエネルギー・サービスの物価が粘っているという記事あり（Moomoo 11/12）。数値は取得不可。

## 引け後・時間外の材料
- 監視銘柄で時間外に±5%以上動いた銘柄はない（headlines 0節）。保有・候補はAMD −1.1%、NVDA −0.1%、SNDK +0.0%。
- 引け後の決算: Fortinetなどサイバーセキュリティ株が時間外に下げた（Benzinga 11/12）。Cisco（CSCO）の名前が引け後の注目銘柄に出ている（Seeking Alpha 11/12）。内容は取得不可。
- 買収: Marvellが光通信の会社を1,150億ドルの株式交換で買収することに合意した（Crypto Briefing・GuruFocus 11/12）。買収先の名前は見出しからは取得不可。

## NVDA（候補）
- 11/12 フアンCEOが辞任し、クレスCFOが暫定CEOになった（AFP・BigGo 11/12）。時価総額が約5,000億ドル減った（CBS News 11/12）。
- 11/9〜10 CEOの調査の報道で、2日続けて売られた（CNN 11/9、CNBC 11/10）。
- 目標株価の引き下げ: RBCが330→230ドル（富途牛牛 11/12）。格下げの報道あり（Motley Fool 11/12）。
- 決算: 決算発表が近い（IBD 11/12）。11/17という日付の公式発表は確認できず。
- 悪材料: あり（CEOの辞任・スパイの疑い・目標株価の引き下げ）

## AMD（保有）
- 11/9 Google Cloudとの契約と格上げで上げた（IBD 11/9）。11/11も上げた（Yahoo Finance 11/11）。
- 11/12 +5.9%。NVDAが売られた分の資金がAMD・Broadcomに移った（investingLive・Mitrade 11/12）。
- 悪材料: 確認できず

## AVGO
- 11/12 +5.5%。理由はAMDと同じ（investingLive 11/12）。11/9にも、NVIDIAの騒動の勝ち組として上げた（MarketWatch 11/9）。
- 悪材料: 確認できず

## ANET
- 11/3 第3四半期の決算: 売上は前年比+58.5%の36.6億ドルで、予想を上回った。2027年の売上見通しは約185億ドル。JPMorganが目標株価を270ドルに上げた（Finviz・XTB 11/4）。11/5は−10.8%（Trefis 11/7）。
- 11/12 +5.1% の原因となるニュースは見つからなかった（半導体の反発と同じ日）。
- 悪材料: 確認できず

## NBIS
- 11/12 −16.8%。決算を受けて下げた。データセンターの容量が遅れ、売上が2027年にずれる。2026年の設備投資が増え、見通しが弱い（CNBC・Barron's・Yahoo Finance 11/12）。売上は約6倍に増えた（Barchart 11/12）。
- 悪材料: あり（売上の先送り・設備投資の増加）

## SMCI
- 11/12 −11.3%。司法省が密輸の疑いを調べている（Barron's 11/12）。1四半期の売上は199億ドル（GuruFocus 11/12）。共同創業者らが3月に起訴された件の続き（Fortune・Al Jazeera 2026-03）。
- 悪材料: あり（司法省の調査）

## CRWV
- 11/12 −6.9%。Barron's（11/12）が「NVIDIAの危険地帯にある銘柄」の1つに挙げた。CRWVだけの原因となるニュースは見つからなかった（検索語: 「CoreWeave stock falls November 12 2026」）。
- 悪材料: 確認できず（社債利回りが高いのは10月から）

## RDDT
- 11/12 −5.8%。原因となるニュースは見つからなかった（検索語: 「Reddit stock RDDT falls November 12 2026」）。
- 悪材料: 確認できず

## SNDK（保有）
- 11/6 −9%（世界の債券利回りが急上昇した日。Moomoo 11/6）。11/7 株式分割の前に下げた（Benzinga 11/7）。11/10も下げた（Motley Fool 11/10）。
- 11/12 −4.1%。NVIDIAの騒動でメモリ株が下げた（24/7 Wall St.・Barron's 11/12）。
- 悪材料: 確認できず（会社固有のものはない。メモリ株全体の下げ）

## 監視外の注目銘柄（BDX・LH・CAH）
- 3銘柄ともヘルスケア（BDXは医療機器、LHは臨床検査、CAHは医薬品の卸）で、AIテーマの外。Finvizの3カ月の上位業種（Medical Distribution 2位、Diagnostics & Research 7位）と同じ業種。
- CAH: 11/6に1年の高値の一覧に載った（Trefis 11/7）。1年で+39.4%。
- BDX・LH: 1年の高値を更新した原因のニュースは見つからなかった。

# ニュースの見出し（プログラムが自動で取得）

- Googleニュース（日付を指定）とYahooファイナンスの見出しを `tools/news_headlines.py` が自動で並べたもの。日付は米国東部時間の配信日（引け後の記事は翌日付）。原因の判断・売買の判断はしていない。
- 調べた銘柄の選び方: ①保有 ②今日の候補 ③時間外に±5%以上動いた監視銘柄 は全部、④引けまでに大きく動いた銘柄（1週で±5%のグループの上位3・1日で±7%）は合計12銘柄まで。
- 1週で−5%以下のグループ: なし
- 1週で+5%以上のグループ: 半導体（+17.1%）、半導体製造装置・材料・設計ソフト・計測（+16.7%）、光・通信・ネットワーク（+15.5%）、AIサーバー・ストレージ・メモリ・端末（+13.6%）、データセンターの電力・冷却・部品・受託製造・建設（+8.4%）、AIプラットフォーム・クラウド（+6.9%）

## 0. 時間外（引け後）の値動き（2026-11-12 の引けから、Yahoo。±3%以上の監視銘柄と、保有・候補は全部）

| 銘柄 | 区分 | 引け | 時間外 | 騰落率 |
|---|---|---|---|---|
| AMD | 保有 | 585.58 | 579.19（17:18 ET） | -1.1% |
| NVDA | 候補 | 166.04 | 165.82（17:18 ET） | -0.1% |
| SNDK | 保有 | 937.14 | 937.23（17:18 ET） | +0.0% |

## 1. 市場全体（2026-11-12）

### 市場全体（英語のまとめ記事）
検索語: `stocks Wall Street close Nasdaq`
- 11/12 Reuters | Equities close lower as Nvidia drop outweighs energy gains
- 11/12 Kiplinger | Stocks Slip as Wall Street Weighs Nvidia's CEO Crisis: Stock Market Today
- 11/12 Benzinga | Stock Market Today: Nvidia Rout Sinks Nasdaq, S&P 500 Futures as Board Weighs Jensen Huang’s Future — CRW
- 11/12 Benzinga | Rocket Lab Stock Surges 50% Despite Wall Street Cuts - Rocket Lab (NASDAQ:RKLB)

### 市場全体（Stock Market Today）
検索語: `"stock market today"`
- 11/12 Eurasia Business News | Stock Market Today, November 12, 2026 : Nvidia Stock Tumbles After Jensen Huang Exit; AI Shares Face Leadership Shock
- 11/12 Bloomberg.com | Stocks Slide on Nvidia Troubles, Oil Edges Lower: Markets Wrap
- 11/12 Investor's Business Daily | Tech Futures Fall; Nvidia Dives As It Mulls Ousting CEO Huang
- 11/12 Yahoo Finance | Stock Market Crash: What History Says Comes Next After the Market's Big Single-Day Dip.
- 11/12 Yahoo Finance | Retail investors are buying Nvidia’s stock crash like never before — history urges patience

### 市場全体（日本語のまとめ記事）
検索語: `米国株式市場 OR NY株`
- 11/12 Reuters | 米国株式市場＝反落、エヌビディア株の下落がエネルギー株高を相殺
- 11/12 BigGo ファイナンス | エヌビディアCEO辞任でNY株反落、ダウ189ドル安 原油高が重し
- 11/12 京都新聞デジタル | ＮＹ株反落、１８９ドル安
- 11/12 Yahoo!ファイナンス | 米国株式市場は反落、ハイテクが重し（12日）(フィスコ)

### 半導体・AI株（英語）
検索語: `chip stocks OR semiconductor stocks OR AI stocks`
- 11/12 Reuters | AI stocks pare losses as investors assess fallout of Nvidia CEO's exit
- 11/12 Barron's | Micron, Other Memory Chip Stocks Fall on Nvidia Shakeup. Why They’re at Risk.
- 11/12 ETF Database | AI Stocks Face a 2028 Test After Chip Sell-Off
- 11/12 The Motley Fool | 2 Chip Stocks to Buy Instead of Nvidia Right Now

### 信用（社債・借金）
検索語: `AI debt OR bonds OR credit spreads OR CDS`
- 11/12 Advisor Perspectives | AI Debt Blowups Become Fodder for ETFs Aimed at Retail Investors
- 11/12 The Dark Side Of The Boom | The Credit Market Has Already Blinked: BofA Warns AI Equity Volatility Is Living on Borrowed Time
- 11/12 Moomoo | Chips Are Priced Riskier by Bond Markets. Is the CDS Premium Wrong?
- 11/12 Financial Times | The AI megatrade’s mounting portfolio concentration risk problem
- 11/12 The Motley Fool | Forget Nvidia CEO Jensen Huang's Affair Scandal -- There Are Far Bigger Issues With the AI Trade

### 「〇〇ショック」の呼び名（日本語）
検索語: `ショック 株`
- 11/12 매일경제 | NVIDIA「ジェンソン·ファン·ショック」で米証券市場が技術株を中心に一斉に下落した。 ドナルド·トランプ大統領が再び対イラン軍事作戦を示唆し、国際原油価格が急騰したことも投資心理を弱化させた。12..
- 11/12 Moomoo | ネビウス神決算🔥｜第2次エロビディアショックを吹き飛ばせ🕺🏻
- 11/12 YouTube | 【リクルート純利益66%増】AI活用で6期連続最高益！エヌビディアショックや半導体株急落の中で買われる「実需AI＆商社株」の強み
- 11/12 Moomoo | 米CPIがFRBに警鐘：エネルギーショックの波及、粘着性の高いサービスインフレ、AIブームが追加圧力
- 11/12 トウシル | ［動画］みずほ証券コラボ┃【日米株、大幅調整のその先は？需給と節目から読み解く年末相場】中島三養子│みずほマンスリーVIEW 11月のテクニカル

### 引け後・時間外の動き（英語）
検索語: `"after hours" OR "after the bell" OR "extended trading" stocks`
- 11/12 Seeking Alpha | Stocks to watch on Thursday after hours: CSCO, NMAX, CBRS (CSCO:NASDAQ)
- 11/12 Benzinga | Cybersecurity Stocks Drop After Hours: Here's Why - Fortinet (NASDAQ:FTNT)
- 11/12 Mitrade | Nvidia slid 7.7% after hours while AMD and Broadcom rose — the AI trade changed hands, it didn't break
- 11/12 investingLive | Nvidia stock plunges 8.6%, but AMD and Broadcom rally. Which chip stocks are worth buying?
- 11/12 BigGo Finance | Inlif Stock Drops 22% After Hours as $30M Supply Deal Carries No Minimum Order Guarantee
- 11/12 Benzinga | Inlif (INLF) Shares Fall 22% After-Hours: Here's Why
- 11/12 Benzinga | Children's Place Shares Jump 257.63% After Hours Following Chapter 11 Bankruptcy Filing - Children's Plac
- 11/12 Benzinga | OptimizeRx Shares Tumble 20% After-Hours: Here's Why

### 引け後・時間外の動き（日本語）
検索語: `時間外 決算 株`
- 11/12 BigGo ファイナンス | Bit Digitalの第3四半期決算は明暗分かれる、売上高が目標未達で時間外株価が9%超下落
- 11/12 BigGo ファイナンス | ジェンスン・フアン氏がNVIDIA CEOを電撃辞任 時間外株価が10%急落、クレス氏が暫定CEOに
- 11/12 Investing.com - FX | 株式市場 | ファイナンス | 金融ニュース | インテュイティブ・マシーンズ株、決算好調と強気見通しで11%急騰
- 11/12 BigGo ファイナンス | アリババ株、香港で6.8%下落 エヌビディア混乱でチップ調達懸念が再燃
- 11/12 BigGo ファイナンス | エヌビディアCEOのジェンスン・フアン氏が辞任、CFOのクレス氏が緊急登板、株価は時間外で10%超下落

### 買収・合併（英語）
検索語: `acquisition OR acquire OR merger OR takeover chip OR semiconductor OR AI OR optical`
- 11/12 GrepBeat | Billionaire-Backed Worker.ai Launches in Raleigh with Acquisition of DeltaGen
- 11/12 Gizmodo | OpenAI Board Member Warns AI Takeover Could Be Months Away
- 11/12 Unite.AI | BlueMatrix Acquires Aiera for Governed Research Delivery to AI Systems
- 11/12 Crypto Briefing | Marvell agrees to acquire optical networking company in $115 billion all-stock deal
- 11/12 Yahoo Finance | Siemens to acquire German chip tools firm Lauterbach
- 11/12 Barron's | Why Salesforce Is One of the Dow’s Worst Stocks Today
- 11/12 FinTech Global | Amdocs moves into InsurTech with $340m EIS acquisition
- 11/12 Politico | NYC-DSA’s plan for a City Council takeover — presented by AI?

## 2. 保有・候補・時間外で大きく動いた銘柄（2026-11-06〜2026-11-12 の見出し）

### SNDK（Sandisk Corporation、保有、AIサーバー・ストレージ・メモリ・端末、前日比 -4.1%、1週 +16.2%、時間外 +0.0%）

#### Googleニュース
検索語: `Sandisk stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/6 Moomoo | Overnight US Stocks | Global Bond Yields Surge; S&P 500 Falls for Third Consecutive Day; SanDisk (SNDK.US) Drops 9%
- 11/7 Benzinga | SanDisk Stock Drops Ahead of Split as Wall Street Analysts Weigh In
- 11/10 The Motley Fool | Why Sandisk Stock Dropped Again on Tuesday
- 11/10 CNN | SNDK Stock Quote Price and Forecast

#### Yahooファイナンス
検索語: `SNDK`
- 11/12 24/7 Wall St. | Micron Is Back Above $800 After Its Best Day Since July
- 11/12 24/7 Wall St. | Sandisk, Micron, and SK Hynix Slide 3% as NVIDIA Shake-Up Hits Memory Stocks

### AMD（Advanced Micro Devices, Inc.、保有、半導体、前日比 +5.9%、1週 +44.7%、時間外 -1.1%）

#### Googleニュース
検索語: `Advanced Micro Devices stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/9 Benzinga | Advanced Micro Devices Inc (AMD) Stock Price, Quote, News & History
- 11/9 Investor's Business Daily | AMD Stock Rises On Google Cloud Deal, Wall Street Upgrade
- 11/11 Yahoo Finance | Why Advanced Micro Devices Stock Popped Today

#### Yahooファイナンス
検索語: `AMD`
- 11/12 BeInCrypto | S&P 500 Recovered $1 Trillion in 90 Minutes Despite Wider Market Crash
- 11/12 Investor's Business Daily | Dow Jones Futures: Market Weathers Nvidia CEO Huang's Exit, Surging Yields; SpaceX-Tesla Merger Deal Close
- 11/12 Motley Fool | Nvidia Stock Just Got Downgraded After Jensen Huang's Exit. Should You Sell?

### NVDA（NVIDIA Corporation、候補、半導体、前日比 -4.3%、1週 -8.5%、時間外 -0.1%）

#### Googleニュース
検索語: `NVIDIA stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/9 CNN | Nvidia stock falls after investigation into CEO, bucking market rally
- 11/9 The New York Times | Nvidia Stock Drops Even as Broader Market Rallies
- 11/10 CNBC | Nvidia sells off for second day in fallout from Jensen Huang’s affair with alleged spy
- 11/12 NBC News | Nvidia stock falls after Huang resigns, weighing on broader market

#### Yahooファイナンス
検索語: `NVDA`
- 11/12 24/7 Wall St. | Same Nvidia Selloff, Opposite Bets. Here’s How Two 2× ETFs Fared
- 11/12 AFP | Nvidia CEO Huang quits after affair with suspected China spy
- 11/12 CBS News | Nvidia sheds almost $500 billion in value as Jensen Huang resigns

## 3. 引けまでに大きく下げた銘柄（2026-11-06〜2026-11-12 の見出し）

### NBIS（Nebius Group N.V.、AIプラットフォーム・クラウド、前日比 -16.8%、1週 +6.9%、時間外 -0.5%）

#### Googleニュース
検索語: `Nebius stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/12 Yahoo Finance | Nebius Stock Falls as Capacity Delays Push Revenue Into 2027
- 11/12 Barron's | Nebius Stock Plummets After Earnings as CEO Warns of Revenue Delay
- 11/12 CNBC | Nebius falls 16% as company expects increased 2026 capex spend, issues weak outlook
- 11/12 Barchart.com | Nebius Says Revenue Jumped Nearly Sixfold. Why That’s Still Not Enough to Avoid a Selloff in NBIS Stock.

#### Yahooファイナンス
検索語: `NBIS`
- 11/12 Investing.com | CoreWeave vs Nebius: valuation, balance sheet, and catalysts compared
- 11/12 Investing.com | Nebius Group earnings analysis: questions answered and next catalysts
- 11/12 Investor's Business Daily | Stock Market Today: Nasdaq Drops; Nvidia Slumps After CEO's Exit With Earnings Report On Tap

### SMCI（Super Micro Computer, Inc.、AIサーバー・ストレージ・メモリ・端末、前日比 -11.3%、1週 -0.3%、時間外 +0.7%）

#### Googleニュース
検索語: `Super Micro Computer stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/10 Yahoo Finance UK | META_TITLE_QUOTE
- 11/12 Barron's | Super Micro Stock Falls as DOJ Probes Smuggling Allegations
- 11/12 Investing.com | Why is Super Micro Computer stock sliding today?
- 11/12 Benzinga | What's Going On With Super Micro Computer Stock Thursday?

#### Yahooファイナンス
検索語: `SMCI`
- 11/12 Barrons.com | CoreWeave and These Other Stocks Are in the Nvidia Danger Zone
- 11/12 GuruFocus.com | Super Micro stock sinks 5% despite $19.9 billion quarter

## 4. 引けまでに大きく上げた銘柄（2026-11-06〜2026-11-12 の見出し）

### MPWR（Monolithic Power Systems, Inc.、半導体、前日比 -2.1%、1週 +27.9%、時間外 +0.0%）

#### Googleニュース
検索語: `Monolithic Power Systems stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/7 Trefis | Can Monolithic Power Systems Stock Fall 30%?
- 11/9 Yahoo Finance | Monolithic Power Systems and Photronics shares skyrocket, what you need to know
- 11/9 The Globe and Mail | Semtech, Entegris, Monolithic Power Systems, Broadcom, and Applied Materials shares are soaring, what you need to know
- 11/9 MarketBeat | Monolithic Power Systems (NASDAQ:MPWR) Shares Up 13.3% - Here's Why

#### Yahooファイナンス
検索語: `MPWR`
- 11/10 24/7 Wall St. | The Nasdaq-100 Just Had Its Best Day Since March Without Nvidia’s Help
- 11/10 MT Newswires | Arete Adjusts Price Target on Monolithic Power Systems to $2,163 From $2,013
- 11/10 Simply Wall St. | 3 AI Infrastructure Stocks Riding The Next Data Center Spending Wave

### ALAB（Astera Labs, Inc.、半導体、前日比 -1.4%、1週 +26.9%、時間外 -0.2%）

#### Googleニュース
検索語: `Astera Labs stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/7 Yahoo Finance | Astera Labs Just Crushed Earnings—So Why Are Analysts Cutting Price Targets?
- 11/9 Moomoo | Astera Labs Jumps as Investors Reassess Strong Q3 Results and Outlook
- 11/9 TIKR.com | Astera Labs Stock Drops 26% in a Week Despite Strong Earnings. Is It a Buy Now?
- 11/9 Quantisnow | The Trade Desk's jump came before its earnings report

#### Yahooファイナンス
検索語: `ALAB`
- 11/9 Simply Wall St. | 3 US AI Chip Stocks Beyond Nvidia Stock Key Person Risk
- 11/9 TIKR | Seagate Soars 10% in AI Rebound as Morgan Stanley Sees “Strong Fundamentals and Weak Sentiment”
- 11/10 GlobeNewswire | Astera Labs Announces Upcoming Financial Conference Participation

### LRCX（Lam Research Corporation、半導体製造装置・材料・設計ソフト・計測、前日比 -0.9%、1週 +26.2%、時間外 -0.1%）

#### Googleニュース
検索語: `Lam Research stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/6 Barron's | Lam Research Sure Picked a Good Time to Buy Back Its Own Stock
- 11/6 Benzinga | Why Is Lam Research Stock Soaring Friday? - Lam Research (NASDAQ:LRCX)
- 11/7 Yahoo Finance | What Just Lifted Lam Research Stock?
- 11/9 24/7 Wall St. | Applied Materials Jumps 11% Ahead of Earnings; Lam Research Surges 9%, ASML Rises 6%

#### Yahooファイナンス
検索語: `LRCX`
- 11/11 TIKR | Lam Research Sinks 16%, Applied Materials 15% in a Week. Lam Responds With $25 Billion Buyback
- 11/12 GuruFocus.com | Marvell makes major board move ahead of $115 billion AI deal
- 11/12 Investing.com | U.S., Europe chip stocks dip as Nvidia board reportedly weighs ousting Huang

### TER（Teradyne, Inc.、半導体製造装置・材料・設計ソフト・計測、前日比 -0.8%、1週 +24.0%、時間外 +0.0%）

#### Googleニュース
検索語: `Teradyne stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/6 Traders Union | Why is Teradyne stock up 7.5% today?
- 11/11 Barron's | Teradyne Stock Jumps. Jefferies Sees a $2 Billion Nvidia Opportunity.
- 11/11 Yahoo Finance Singapore | Why Teradyne Stock Is Getting Attention After Edge AI Test Platform Launch
- 11/11 24/7 Wall St. | Wall Street's Newest Teradyne Bull Just Sent a $2 Billion Signal That the Stock's 56% Crash Went Too Far

#### Yahooファイナンス
検索語: `TER`
- 11/11 Barrons.com | Nvidia, CoreWeave, Nebius, Teradyne, Riskified, and More Stocks That Explain Today’s Market
- 11/11 Investor's Business Daily | Teradyne Stock Surges On Fresh Buy Rating, Called AI Play

### KLAC（KLA Corporation、半導体製造装置・材料・設計ソフト・計測、前日比 -2.3%、1週 +21.2%、時間外 -0.4%）

#### Googleニュース
検索語: `KLA stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/6 Yahoo Finance | Earnings Beat Tests The Case For KLA Stock
- 11/6 StreetInsider | KLA Corporation stock jumps as buyers return after selloff
- 11/9 MarketWatch | KLA Corp. stock underperforms Monday when compared to competitors despite daily gains
- 11/10 Trefis | Can KLA Stock Rally 50% After This Dip?

#### Yahooファイナンス
検索語: `KLAC`
- 11/12 Simply Wall St. | Applied Materials And 2 Top AI Chip Stocks
- 11/12 Simply Wall St. | Our Pick Of The Best AI Chip Stocks In November 2026
- 11/12 Trefis | How Low Can KLA Stock Go?

# 実行メモ

- 実行環境に matplotlib・Pillow がなく、候補・保有銘柄（AMD・NVDA・SNDK）の数値データの取得が最初に失敗した。入れ直して取り直した。
- 個別銘柄のプロンプトが8,000文字を超え（テーマの状態の節が長いため）送信できなかった。著者（ボリンジャー）へは、テーマの状態の節から「グループごとの悪いニュースの流れ（記録だけ）」の表と見出しを外して（scan_short.md）送り直した。ニュースは文字数の上限まで縮めた（2026-11-11・11-12 と同じ対応）。
- ワインスタイン（テーマの局面）は全体の版が空の応答だったため、1〜2節だけの短い版で回答を得た。
