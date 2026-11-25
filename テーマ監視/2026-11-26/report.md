# テーマ監視 2026-11-25

# 判定のまとめ（ルールの判定と著者の判定を分けて表示）

- **ルールの判定**: 採用した売買ルール（スクリプト）が数値で決めたもの。損切りは買値の15%下の逆指値（日中に届けばその場で売れる）。
- **著者の判定**: ノートブックの著者の回答。買いは注文を止める理由があるときだけ【様子見】、保有はルールより早く手じまう理由があるときだけ【売り】。根拠は下の「著者の回答（全文）」。
- 2つが食い違うときに、どちらに従うかはユーザーが決める。

- **テーマ全体の急落（S2・記録だけ）: あり（S2）**（SOXが直近60取引日の最高値から -33.6%）。S2の日の順張りの候補には「S2なら見送る形」と付ける（売買のルールは変えない。記録してから採用を決める。2026-10-14）

- **特殊な下げ（記録だけ）: あり（特殊な下げ）**（2026-10-16から）（SOXが直近60取引日の最高値から -33.6%、前の1年の大きな上げ・雇用の弱さ・物価の再加速のうち 2つ）。1995年〜では、この形の後にSOXの下げが長引くことが多かった（後知恵を含む）。売買のルールは変えない（2026-11-03）

## 保有銘柄

| 銘柄 | ルール | 損益 | 時間外 | ルールの判定 | ルールの判定の理由 | 著者の判定 |
|---|---|---|---|---|---|---|
| SNDK | ルール外（ユーザーの判断。この日はどのルールの合図もなし） | -57.1% | +0.3% | **売り** | 終値 73.61 が損切り価格 145.7 以下 | 【未判定】（） |
| AMD | ボリンジャーIII | -26.2% | -0.1% | **売り** | 終値 406.03 が損切り価格 467.47 以下 | 【保有継続】（ボリンジャー） |

## 候補の判定（並びは上の「買う順番」の表と同じ）

候補なし

- 時間外: 前の取引日の引けから、引け後（米国東部時間16〜20時）の最後の値までの騰落率（Yahoo。±5%以上は太字）。寄り付きの値段は、表の注文の目安（前日の終値で計算）から大きくずれることがある。原因の見出しは「ニュースの見出し」の節。

# 著者の回答（全文）

## 0_テーマの局面_ワインスタイン

1. **テーマ全体の局面**: 【ステージ3】（大上昇の後に30週線が上昇モメンタムを失い「横ばい」となっているため、第2章・第8章 [1, 2]）。
2. **グループごとの局面**:
- 半導体｜ステージ3｜30週線横ばい [1, 3]
- 半導体製造装置・材料・設計ソフト・計測｜ステージ4｜30週線下降・線の下 [3, 4]
- AIサーバー・ストレージ・メモリ・端末｜ステージ3｜30週線横ばい [1, 3]
- 光・通信・ネットワーク｜ステージ4｜30週線下降・線の下 [3, 4]
- データセンターの電力・冷却・部品・受託製造・建設｜ステージ4｜30週線下降・線の下 [3, 4]
- AIプラットフォーム・クラウド｜ステージ3｜30週線横ばい [1, 3]
- AIソフト・セキュリティ・ITサービス｜ステージ3｜30週線横ばい [1, 3]
3. **転換の兆し**: 出ている。30週線の水平化 [1]、市場対比のRS悪化 [5]、健全銘柄比率の崩壊（10%、第3章・第8章 [2, 6]）は天井・崩れの典型兆候である。なお50日線警告や急落S2等の独自指標はマニュアルに規定なし [7]。
4. **テーマの外**: なし（判定不能：ヒートマップ省略のため [7]）。

（全体の版が空の応答だったため、1〜2節だけの短い版で送り直した回答。ヒートマップ・急騰急落・ニュースは渡していない）

## 1_ボリンジャー_prompt_1

## AMD
1. **投資判断**: 【保有継続】（早期手じまいの根拠なし）
2. **止める理由の確認**:
- 本が禁じる形・状況｜なし｜上部バンド到達等の危険な手じまい形なし（第17・20章）
- 避けるべき時期（決算など）｜なし｜決算前回避はマニュアルに規定なし
- 悪材料｜判定不能｜ニュース省略のため判定不能
3. **現状パターンと価格**:
- 現状パターン: なし（保有中）
- 売りの予約注文: なし
4. **注意点**: ルール所定の手じまい条件の執行はスクリプトの判定に従うこと。

# スキャン（数値と事実）


- 監視銘柄 87（判定できたのは 87）。
- この一覧は数値と事実だけ。売買の判断は著者のノートブックが行う。

## 1. テーマ（グループ）の強さ

| グループ | 銘柄数 | 1週 | 1カ月 | 3カ月 | 3カ月の順位 | 50日線より上の銘柄の割合 | グループ指数の30週線の局面（線との乖離、4週前からの線の傾き） |
|---|---|---|---|---|---|---|---|
| 半導体 | 16 | -7.6% | -21.7% | -16.5% | 4位 | 0% | 横ばい（-20.6%、+2.8%） |
| 半導体製造装置・材料・設計ソフト・計測 | 9 | -6.7% | -20.3% | -24.8% | 6位 | 0% | 下落（-24.3%、-0.3%） |
| AIサーバー・ストレージ・メモリ・端末 | 9 | -5.1% | -29.3% | -37.0% | 7位 | 22% | 横ばい（-19.5%、+4.1%） |
| 光・通信・ネットワーク | 9 | -7.3% | -16.8% | -22.7% | 5位 | 11% | 下落（-20.7%、-0.4%） |
| データセンターの電力・冷却・部品・受託製造・建設 | 19 | -4.3% | -9.0% | -11.0% | 2位 | 0% | 下落（-14.2%、-0.6%） |
| AIプラットフォーム・クラウド | 11 | -3.3% | -7.6% | -4.6% | 1位 | 27% | 横ばい（-12.6%、+0.3%） |
| AIソフト・セキュリティ・ITサービス | 14 | +1.7% | -17.3% | -13.6% | 3位 | 21% | 横ばい（-0.6%、+3.7%） |

## 2. テーマ全体の状態と早めの警告

- 市場全体の30週線による局面: S&P500指数 **横ばい**／NASDAQ100指数 **横ばい**（急落の底で買うルールは、過去の検証で下落相場で特に強く、横ばいの相場では負けていた）
- **2倍ETFを使う局面（案1、2026-10-13 採用）: S&P500の20週線（100日線）で 横ばい** → 新しく買う銘柄は、2倍ETFのある銘柄も元の株で買う（保有中のETFはそのまま）（SPY 716.70、100日線 757.58、20日前の線 757.25。上昇＝線より上かつ線が上向き）
- **テーマ全体の急落（S2、記録だけ。売買のルールは変えない）: あり（S2）**（SOX 8774.86、直近60取引日の最高値 13217.82 から -33.6%。S2＝最高値から−10%以上）。S2のときに「順張りの新しい買いだけ止める」形を記録で比べる（2026-10-14 ユーザー決定。バックテストでは年率は上がったが2つの期間ではどちらも少し下回ったため、記録してから採用を決める。`バックテスト結果/テーマ全体の急落を検知して手じまう・買いを止める.md`）
- **グループごとの悪いニュースの流れ（記録だけ。売買のルールは変えない。2026-11-12〜2026-11-25）**: 会社の名前と悪い言葉（格下げ・目標株価の引き下げ・見通しの引き下げ・予想未達・急落・信用・訴訟・輸出規制など）の両方がある見出しの数（Googleニュース、`tools/news_headlines.py`）。10取引日の1銘柄あたりが一番多いグループに印。2026年7〜11月の確かめでは、印のグループの合図は10月は成績が悪かった（1回平均 −10.6%、ほか −5.6%）が、7〜9月は逆に良かった（+11.6%、ほか +6.7%）（`バックテスト結果/実際の運用の期間の確認_2026-10-23/グループの悪いニュースの流れ.md`。2026-11-04）

| グループ | 悪いニュース 直近5取引日 | その前の5取引日 | 10取引日の1銘柄あたり | 良いニュース 10取引日（1銘柄あたり） | 印 |
|---|---|---|---|---|---|
| AIプラットフォーム・クラウド（11） | 取得できず | 10件 | 0.9 | 取得できず（0.0） | **悪いニュースが続いている** |
| AIサーバー・ストレージ・メモリ・端末（9） | 取得できず | 8件 | 0.9 | 取得できず（0.0） |  |
| 光・通信・ネットワーク（9） | 取得できず | 7件 | 0.8 | 取得できず（0.0） |  |
| 半導体（16） | 取得できず | 9件 | 0.6 | 取得できず（0.0） |  |
| 半導体製造装置・材料・設計ソフト・計測（9） | 取得できず | 2件 | 0.2 | 取得できず（0.0） |  |
| データセンターの電力・冷却・部品・受託製造・建設（19） | 取得できず | 3件 | 0.2 | 取得できず（0.0） |  |
| AIソフト・セキュリティ・ITサービス（14） | 取得できず | 1件 | 0.1 | 取得できず（0.0） |  |

印のグループ（AIプラットフォーム・クラウド）の最近の見出し: 2026-11-16 Tesla: Wall Street Keeps Getting It Wrong, And The Price Is Still Too High (Rating Downgrade)（Seeking Alpha）／2026-11-16 Nebius: Get Your Head Out Of The Neoclouds (Rating Downgrade) (NASDAQ:NBIS)（Seeking Alpha）／2026-11-16 CoreWeave: Walking The Leverage Tightrope (Rating Downgrade) (NASDAQ:CRWV)（Seeking Alpha）

- **特殊な下げ（記録だけ。売買のルールは変えない）: あり（特殊な下げ）**（2026-10-16から）。SOX は直近60取引日の最高値から -33.6%（−15%以下が条件）、●A 前の1年の上げ +101.8%（+80%以上）、・B 雇用の伸び 137千人/月（2026-10まで。10万人未満）、●C 物価 4.1%（2026-10。3か月前 3.5%。3.5%以上で再加速）＝2つ（2つ以上が条件）。1995年〜でSOXが−15%以下かつ条件2つ以上の日は、120日後にSOXが下だったのが69%・250日後が70%（中央値 −33%）、AI以外の8業種の平均は250日後 −7%。ただし条件は過去を見て選んだもの（条件が2つ以上の局面は約5回）で、2026年7〜9月にこの間テーマを買わないと、その後の戻りを逃して2026年の成績は下がった（`バックテスト結果/実際の運用の期間の確認_2026-10-23/特殊な下げと過去の似た下げ.md`。2026-11-03）
- テーマ指数（監視銘柄の等金額平均）の30週線による局面: **横ばい**（上昇＝線より上かつ上向き、下落＝線より下かつ下向き、それ以外＝横ばい。ワインスタインのステージの近似）
- テーマ指数と50日線: 50日線より下（乖離 -14.3%）
- S&P500に対する相対的な強さ: 50日平均より下（S&P500より弱い）
- 監視銘柄のうち50日線より上の割合: 10%
- 警告（割合が40%未満かつテーマ指数が50日線より下）: **出ている**
- 参考（バックテスト）: 30週線の「下落」は高値から10〜33%下げた後に出る遅い判定。50日線・割合・相対的な強さは高値から2〜8%で出るが、誤報が年15回以上ある。警告中に新しい買いを止めると、押し目買い（ボリンジャーIII）の成績は大きく下がった（`バックテスト結果/テーマ監視銘柄・直近3年.md` 11・12節）。

## 3. ヒートマップ（Finviz、全米の業種別の騰落率）

3カ月の騰落率の上位15業種（テーマの外で強くなっている業種の確認用）:

| 順位 | 業種 | 1週 | 1カ月 | 3カ月 | 6カ月 | 1年 |
|---|---|---|---|---|---|---|
| 1 | Discount Stores | +3.0% | +11.4% | +23.8% | +13.1% | +29.3% |
| 2 | Medical Distribution | +0.6% | +11.2% | +16.9% | +38.0% | +16.6% |
| 3 | Advertising Agencies | -2.1% | +32.4% | +15.2% | -26.0% | -24.4% |
| 4 | Lodging | -2.0% | +7.1% | +13.4% | +8.4% | +33.1% |
| 5 | Consumer Electronics | +1.1% | +2.7% | +13.1% | +14.1% | +27.2% |
| 6 | Insurance - Diversified | +0.8% | +6.1% | +13.0% | +19.5% | +13.8% |
| 7 | Household & Personal Products | +2.1% | +6.7% | +12.7% | +17.2% | +15.4% |
| 8 | Waste Management | +2.5% | +4.0% | +11.8% | +19.4% | +12.9% |
| 9 | Insurance - Reinsurance | +2.6% | +6.2% | +10.8% | +28.4% | +40.9% |
| 10 | Home Improvement Retail | +6.7% | +14.7% | +10.8% | +11.1% | +5.8% |
| 11 | REIT - Hotel & Motel | -1.3% | +0.5% | +9.8% | +17.1% | +50.0% |
| 12 | Apparel Manufacturing | +1.7% | +7.1% | +9.6% | -1.4% | +11.9% |
| 13 | Medical Instruments & Supplies | +1.1% | +2.8% | +9.4% | +15.4% | -1.5% |
| 14 | Beverages - Wineries & Distilleries | +0.5% | +7.4% | +9.4% | -1.0% | -5.2% |
| 15 | Grocery Stores | +0.8% | +0.6% | +9.4% | -1.9% | -1.7% |

テーマの業種の順位（3カ月、全144業種中）: Semiconductors 134位、Semiconductor Equipment & Materials 138位、Computer Hardware 141位、Communication Equipment 125位、Electronic Components 126位、Software - Infrastructure 96位、Software - Application 120位、Internet Content & Information 110位

## 4. 急騰・急落した銘柄（前日比±5%以上、または出来高が50日平均の2倍以上）

原因のニュースをサブエージェントが調べ、候補・保有銘柄の判定材料として著者に渡す。急騰・急落そのものは売買の合図にしない（後知恵のないS&P500全体のバックテストでは、急騰の翌日に買うルールは年率7%、急落の翌日に買うルールは年率9〜10%で、採用した3つのルールより優れていなかった）。

| 銘柄 | グループ | 前日比 | 出来高（50日平均の倍） | 終値 | 50日線 | RS | 局面 |
|---|---|---|---|---|---|---|---|
| SNDK | AIサーバー・ストレージ・メモリ・端末 | -22.0% | 1.5倍 | 73.61 | 下 | 18 | 下げ |
| HPQ | AIサーバー・ストレージ・メモリ・端末 | +11.5% | 2.9倍 | 31.15 | 上 | 94 | レンジ |
| CDW | AIソフト・セキュリティ・ITサービス | +6.6% | 1.0倍 | 174.97 | 上 | 96 | 上昇相場 |
| ADI | 半導体 | +6.4% | 2.0倍 | 333.11 | 下 | 34 | 下げ |
| LRCX | 半導体製造装置・材料・設計ソフト・計測 | -5.7% | 1.8倍 | 185.01 | 下 | 6 | 下落相場 |
| ORCL | AIプラットフォーム・クラウド | -5.1% | 1.1倍 | 103.88 | 下 | 2 | 下げ |
| DELL | AIサーバー・ストレージ・メモリ・端末 | +0.6% | 3.3倍 | 297.06 | 下 | 98 | 下げ |

- 局面（判定式はClaudeが置いたもの）: **上昇相場**＝終値 > 50日線 > 200日線、50日線が20取引日前より2%以上高い、ADX(14) ≧ 20／**下落相場**＝終値 < 50日線 < 200日線、50日線が20取引日前より2%以上低い、ADX(14) ≧ 20／**上げ**＝それ以外で終値が50日線より上、かつ50日線が10取引日前より上か20日線が5取引日前より上／**下げ**＝それ以外で終値が50日線より下、かつ50日線が10取引日前より下か20日線が5取引日前より下（急な下げの初めは50日線がまだ上向きのため20日線でも見る）／**レンジ**＝どれにも当たらない（2026-11-05 から5つ。それまでは上昇相場とレンジの2つだけで、下げている銘柄もレンジと出ていた）。

## 4-2. 監視外の注目銘柄（S&P500・NASDAQ100のうち監視銘柄に入っていない銘柄）

条件: 流動性（株価5ドル以上・50日平均出来高25万株以上）があり、(a) 前日比+8%以上かつ出来高が50日平均の2倍以上、または (b) 終値が直前1年の最高値（終値）を上回り、RS≧90。RSの高い順に5銘柄（ニュースを調べる）。監視銘柄に入れるかはユーザーが決める。

| 銘柄 | 種類 | 前日比 | 出来高（50日平均の倍） | RS | 終値 |
|---|---|---|---|---|---|
| BDX | 1年の高値更新 | +0.6% | 0.7倍 | 96 | 221.24 |
| AIZ | 1年の高値更新 | +1.0% | 0.9倍 | 95 | 325.73 |
| ADP | 1年の高値更新 | +1.9% | 1.0倍 | 95 | 316.72 |
| EG | 1年の高値更新 | +1.4% | 1.2倍 | 93 | 433.64 |
| MAS | 1年の高値更新 | +2.2% | 0.9倍 | 92 | 86.93 |

- ほかに1銘柄: DGX（1年の高値更新、RS 91）

## 5. 保有銘柄の手じまい条件（`新分析ツール/保有銘柄.md`）

| 銘柄 | ルール | 買った日 | 買値 | 終値 | 損益 | 損切り価格（買値の15%下、逆指値） | ルールの手じまい条件 | 出来高2倍の大陰線（買った後の直近5日） | 次回決算予定日 |
|---|---|---|---|---|---|---|---|---|---|
| SNDK | ルール外（ユーザーの判断。この日はどのルールの合図もなし） | 2026-10-21 | 171.41（株式分割 1→8 に合わせて直した値。記録は 1371.30） | 73.61 | -57.1% | 145.70 | **損切り価格を下回った**（2026-10-30 の安値 139.40。逆指値なら約定済み。まだ持っていれば次の寄り付きで売る） ルールが不明（保有銘柄.md の「ルール」を確認） | なし | 2027-02-15 |
| AMD | ボリンジャーIII | 2026-10-21 | 549.97 | 406.03 | -26.2% | 467.47 | **損切り価格を下回った**（2026-11-02 の安値 466.07。逆指値なら約定済み。まだ持っていれば次の寄り付きで売る） **成立（出来高2倍の大陰線が 2026-11-05 に出た → まだ持っていれば次の寄り付きで全部売る）** 売りの指値: 上部バンド 591.36（今夜この値に置き直す。届いた日に売れる）（2倍ETF AMUU で持っている場合も、判定は元の株 AMD の値段） | なし | 2027-02-02 |

- 出来高2倍の大陰線: 実体（始値−終値）が前日までのATR(14)の1.5倍以上、終値がその日の値幅の下25%以内、出来高が前日までの50日平均の2倍以上の日。**押し目（ボリンジャーIII）・急落の底の保有では売りのルール**: 出たら翌日の寄り付きで全部売り、空いた枠で次の合図を買う（2026-10-02 ユーザー決定。`バックテスト結果/やり直し_売りの合図の組み合わせ.md`。乱数3組とも年率が約+2ポイント、最大下落率もやや下がった）。ミネルヴィニ・新高値V2の保有では事実の表示（順張りに足しても良くならなかった）。

- 半分売りの合図（ミネルヴィニ・新高値V2の保有だけ）: 反転のローソク足（かぶせ線・弱気の包み足・宵の明星・流れ星）＋出来高が50日平均の1.5倍以上＋RSI(14)が前日か当日に70以上。買った後に最初に出た日の翌日の寄り付きで半分売り、残り半分は50日線割れ・損切り15%まで持つ（2026-10-01 ユーザー決定。`バックテスト結果/半分だけ売るとオニールの空き枠.md`）。

- かぶせ線（ミネルヴィニ・新高値V2の保有だけ）: 上昇中の陽線の翌日に、前日の高値より上で寄り付き、前日の陽線の真ん中より下（前日の始値より上）で引けた日。翌日の寄り付きで全部売り、空いた枠で次の合図を買う。半分売りより優先する（2026-10-01 ユーザー決定。`バックテスト結果/2倍ETFで売って買い直す.md`。順張りの売買の25%で出て、1回平均+2.0%、年率 21.4%→26.4%）。

## 5-2. 前日（2026-11-24の引け）の【買い（予約）】の確認

前日の【買い（予約）】はなし。

## 6. 候補（採用したルールの条件が成立＝A。予約（B）は2026-10-25から注文せず、節6-3に参考の表示だけ）

建玉の目安: 同時保有4銘柄まで、1銘柄に資金の25%（資金÷4）、損切りは買値の15%下（ユーザー決定 2026-09-29）。

保有中のため候補から外した銘柄（合図は出ている）: SNDK

本日は該当なし（著者への送信は不要）。


## 6-3. 参考: 条件の成立が目前の銘柄（予約は注文しない・著者には送らない）

2026-10-25 ユーザー決定: 予約（逆指値・指値）の注文はやめ、参考の表示だけにする。毎朝のツールと同じ条件・値段で予約の約定をバックテストに入れると、どの形も年率が下がった（後知恵なし 35.7%→30.7〜34.2%、87銘柄 45.6%→34.2〜42.6%。`バックテスト結果/点検_2026-10-25/`）。引けで条件がそろえば、翌朝の節6に買いの候補（A）として出る。各ルールでRSの高い順に2件まで。

| 参考の銘柄 | グループ | 種類 | 終値 | 前日比 | RS | 当てはまった条件 | 条件がそろう目安の価格（注文はしない） |
|---|---|---|---|---|---|---|---|
| CDNS | 半導体製造装置・材料・設計ソフト・計測 | ボリンジャー メソッドIII（%bが0.05未満に近い） | 294.89 | -0.6% | 17 | %b=0.148（0.05まであと少し）、21日II%=+0.004（>0） | 288.73（この値より下で引けると翌朝の買いの候補（A）。目安） |
| CEG | データセンターの電力・冷却・部品・受託製造・建設 | ボリンジャー メソッドIII（%bが0.05未満に近い） | 235.28 | -3.9% | 7 | %b=0.075（0.05まであと少し）、21日II%=+0.003（>0） | 233.88（この値より下で引けると翌朝の買いの候補（A）。目安） |


# ニュース（サブエージェントの調査）

# ニュース調査（2026-11-25の引け時点。調査日 2026-11-26）

注: Googleニュースの取得が遮断され、headlines.md はYahooファイナンスの見出しだけ。WebSearchは11/25付の記事を返さなかった（11月の別日・他の月の記事のみ）。確認できた事実だけを書き、分からない項目は「取得不可」とした。

## テーマ全体の下げの原因
当たる日（2節の早めの警告・S2・複数グループの1週−5%以下）。5観点の確認結果:
- きっかけ（銘柄名）: 半導体製造装置はMATCH Act（中国向け装置輸出の規制法案）をめぐる売り。LRCX −7%・AMAT −6%・KLA小幅安（24/7 Wall St. 11/25）、AMAT −7.98%（GuruFocus 11/25 見出し「MATCH Act Fight Rattles Chip Toolmakers」）、LRCX −9.54%・売上の35%が中国（GuruFocus 11/25）。11/24にはFORM −12.4%・ICHR・AMBAなど装置・半導体の売り（GuruFocus 11/24）。
- 光通信: COHR −10%、AAOI −12%、LITE −10%「AI selloff deepens」（24/7 Wall St. 11/25）。
- メモリ: SNDK −12%「AI Memory Fears Deepen」（GuruFocus 11/25）、「Micron and Other Memory Plays Will Bear the Brunt of This AI Pain」（Barron's 11/25）。見出しの中身は未確認（本文取得不可）。
- 経済指標・政策: NVDA −3.9%、「強いPCEインフレ指標と新しい関税案」を市場が意識（Motley Fool 11/25）。半導体とiPhoneは新関税の対象外（Barron's 11/25）。Investing.com 11/25「AIへの支出が2027年に向けた最大の市場リスク」。
- 信用（社債・CDS・格付け・資金調達）: 見出しに該当なし。信用の材料は取得不可（検索語 `AI debt OR bonds OR credit spreads OR CDS` はGoogle遮断で結果なし）。Seeking Alpha 11/16に CRWV「Walking The Leverage Tightrope」（格下げ評価）の見出しあり（scan.md）。
- 「〇〇ショック」の呼び名: 見つからなかった（検索語 `ショック 株` は取得不可）。
- 市場全体（S&P500・VIX・ハイイールド債）への広がり: 取得不可（市場全体の見出しが取得できなかった）。
- 補足: Barron's 11/25「Anthropic, Nvidia, Micron, HP Inc., Dell, Deere, and More Stocks That Explain Today's Market」、Motley Fool 11/25「Anthropicのチップ選択がNvidiaの物語を変えうる」の見出しがあるが、中身は取得不可。

## 引け後・時間外の材料
- VST: 時間外 +7.2%（121.32→130.05）。原因の見出しは見つからなかった（Yahooは11/24付の記事のみ。WebSearchも該当なし）。
- PANW: 時間外 −4.5%（356.19→339.99）。±5%未満。11月の決算の記事は見つからなかった（直近の決算は2026-09-01発表の第4四半期、粗利率の懸念で時間外約−2%：SiliconANGLE 9/1）。原因は取得不可。
- SNDK（保有）: 時間外 +0.3%、AMD（保有）: −0.1%。材料なし。

## SNDK（保有）
- 時間外 +0.3%。±5%未満。
- 11/25: 前日比 −22.0%（scan.md）。見出し「Sandisk Stock Plunges 12% as AI Memory Fears Deepen」（GuruFocus 11/25）、「Memory Stock ... Bear the Brunt of This AI Pain」（Barron's 11/25）。個別の材料（決算・格下げ等）は見出しになし。
- 同日にメモリ・光通信・装置が同時に下げており、グループ共通の売りの一部。
- 悪材料: あり（グループ全体の下落。個別の不祥事は確認できず）

## AMD（保有）
- 時間外 −0.1%。
- 11/25 見出し: 「Dellの新しいAIサーバー受注の大半はNvidiaのVera Rubin向け」（24/7 Wall St.）、「データセンターの1件の遅れが付きまとう」（Barron's）、「AnthropicのチップがNvidiaに与える影響」（Motley Fool）。中身は取得不可。
- 悪材料: 確認できず（個別の悪材料は見つからず。1週 −23.4%の原因は取得不可）

## HPQ（急騰 +11.5%）
- 11/25: 決算発表。「メモリが1年でPCの部品コストの15%から40%に上昇」（24/7 Wall St. 11/25）。EPS・売上のBeat/Miss、ガイダンスは取得不可。
- 悪材料: 確認できず

## SNDK以外の急変動銘柄
- LRCX −5.7%: 上記のMATCH Act・中国規制の売り（GuruFocus・24/7 Wall St. 11/25）。
- ORCL −5.1%、ADI +6.4%、CDW +6.6%: 原因の見出しなし。取得不可（原因となるニュースは見つからなかった）。
- DELL +0.6%（出来高3.3倍）: 「新しいAIサーバー受注の大半がVera Rubin向け」（24/7 Wall St. 11/25）。

## 候補
- 本日は候補なし（scan.md 6節）。参考の CDNS・CEG は調査対象外のため取得不可。

## 監視外の注目銘柄（BDX・AIZ・ADP・EG・MAS）
- 見出し・検索とも取得できなかった。1年の高値更新の原因は取得不可。いずれもテーマ外の銘柄（scan.md 3節でテーマ外業種が上位）。

## 決算の評価（ミネルヴィニ・個別分析）
- 対象銘柄の指定なし（候補なし）。HPQの決算のみ上記。

## テーマ全体の大きなニュース（直近1週間）
- MATCH Actをめぐる中国向け装置規制の議論が再燃（見出し 11/25）。法案は4月に提出され、低温エッチング装置の国単位の全面禁止は修正で削除済み（Tom's Hardware、4月）。11月時点の進行状況は取得不可。
- 11/13: Nvidia CEOの退任をきっかけにAIハード株の売りが広がったとの記述（Motley Fool 11/13、検索結果の要約。原典の本文は未確認）。

# ニュースの見出し（プログラムが自動で取得）

- Googleニュース（日付を指定）とYahooファイナンスの見出しを `tools/news_headlines.py` が自動で並べたもの。日付は米国東部時間の配信日（引け後の記事は翌日付）。原因の判断・売買の判断はしていない。
- 調べた銘柄の選び方: ①保有 ②今日の候補 ③時間外に±5%以上動いた監視銘柄 は全部、④引けまでに大きく動いた銘柄（1週で±5%のグループの上位3・1日で±7%）は合計12銘柄まで。
- 1週で−5%以下のグループ: 半導体（-7.6%）、光・通信・ネットワーク（-7.3%）、半導体製造装置・材料・設計ソフト・計測（-6.7%）、AIサーバー・ストレージ・メモリ・端末（-5.1%）
- 1週で+5%以上のグループ: なし

## 0. 時間外（引け後）の値動き（2026-11-25 の引けから、Yahoo。±3%以上の監視銘柄と、保有・候補は全部）

| 銘柄 | 区分 | 引け | 時間外 | 騰落率 |
|---|---|---|---|---|
| VST | 監視 | 121.32 | 130.05（16:55 ET） | **+7.2%** |
| PANW | 監視 | 356.19 | 339.99（17:33 ET） | -4.5% |
| SNDK | 保有 | 73.51 | 73.73（17:33 ET） | +0.3% |
| AMD | 保有 | 406.83 | 406.24（17:33 ET） | -0.1% |

## 1. 市場全体（2026-11-25）

### 市場全体（英語のまとめ記事）
検索語: `stocks Wall Street close Nasdaq`
- （取得できなかった）

### 市場全体（Stock Market Today）
検索語: `"stock market today"`
- （取得できなかった）

### 市場全体（日本語のまとめ記事）
検索語: `米国株式市場 OR NY株`
- （取得できなかった）

### 半導体・AI株（英語）
検索語: `chip stocks OR semiconductor stocks OR AI stocks`
- （取得できなかった）

### 信用（社債・借金）
検索語: `AI debt OR bonds OR credit spreads OR CDS`
- （取得できなかった）

### 「〇〇ショック」の呼び名（日本語）
検索語: `ショック 株`
- （取得できなかった）

### 引け後・時間外の動き（英語）
検索語: `"after hours" OR "after the bell" OR "extended trading" stocks`
- （取得できなかった）

### 引け後・時間外の動き（日本語）
検索語: `時間外 決算 株`
- （取得できなかった）

### 買収・合併（英語）
検索語: `acquisition OR acquire OR merger OR takeover chip OR semiconductor OR AI OR optical`
- （取得できなかった）

## 2. 保有・候補・時間外で大きく動いた銘柄（2026-11-19〜2026-11-25 の見出し）

### SNDK（Sandisk Corporation、保有、AIサーバー・ストレージ・メモリ・端末、前日比 -22.0%、1週 -33.5%、時間外 +0.3%）

#### Googleニュース
検索語: `Sandisk stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- （取得できなかった）

#### Yahooファイナンス
検索語: `SNDK`
- 11/25 Barrons.com | Anthropic, Nvidia, Micron, HP Inc., Dell, Deere, and More Stocks That Explain Today’s Market
- 11/25 Barrons.com | Micron Stock and Other Memory Plays Will Bear the Brunt of This AI Pain
- 11/25 GuruFocus.com | Sandisk Stock Plunges 12% as AI Memory Fears Deepen

### AMD（Advanced Micro Devices, Inc.、保有、半導体、前日比 -1.8%、1週 -23.4%、時間外 -0.1%）

#### Googleニュース
検索語: `Advanced Micro Devices stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- （取得できなかった）

#### Yahooファイナンス
検索語: `AMD`
- 11/25 24/7 Wall St. | Most of Dell’s New AI Server Orders Are Now for Nvidia’s Vera Rubin
- 11/25 Barrons.com | Why a Single Data-Center Delay Keeps Dogging This Tech Stock
- 11/25 Motley Fool | Anthropic’s Chip Choices Could Change the Nvidia Story. Here’s How.

### VST（Vistra Corp.、データセンターの電力・冷却・部品・受託製造・建設、前日比 +0.5%、1週 -3.4%、時間外 +7.2%）

#### Googleニュース
検索語: `Vistra stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- （取得できなかった）

#### Yahooファイナンス
検索語: `VST`
- 11/24 Simply Wall St. | Is Vistra (VST) Still Below Fair Value After Data Center Clarity?
- 11/24 TIKR | George Soros and 10 Other Big Funds Sold Vistra Last Quarter, While 7 Bought. Who’s Right?
- 11/24 Trefis | How Has Vistra Stock's Story Changed?

## 3. 引けまでに大きく下げた銘柄（2026-11-19〜2026-11-25 の見出し）

### AVGO（Broadcom Inc.、半導体、前日比 -0.1%、1週 -15.0%、時間外 -0.1%）

#### Googleニュース
検索語: `Broadcom stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- （取得できなかった）

#### Yahooファイナンス
検索語: `AVGO`
- 11/25 Investing.com | AI spending leads the biggest market risks heading into 2027
- 11/25 Motley Fool | Not Micron. Not Broadcom. This Is My Top Oversold Artificial Intelligence (AI) Stock to Buy in December
- 11/25 Motley Fool | Stock Market Today, Nov. 25: Nvidia Slides 3.9% as the Market Considers Hot PCE Inflation Data and New Tariff Proposals

### MU（Micron Technology, Inc.、半導体、前日比 -4.5%、1週 -14.7%、時間外 -0.5%）

#### Googleニュース
検索語: `Micron stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- （取得できなかった）

#### Yahooファイナンス
検索語: `MU`
- 11/25 24/7 Wall St. | Berkshire Hathaway Is Up 15% in 2026 and Easily Beating the S&P 500. Is Berkshire Stock Better Than an Index Fund Now?
- 11/25 Barrons.com | Chips and iPhones Are Safe From New Tariffs. Here’s What Isn’t.

### ANET（Arista Networks, Inc.、光・通信・ネットワーク、前日比 -2.7%、1週 -15.4%、時間外 +0.0%）

#### Googleニュース
検索語: `Arista Networks stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- （取得できなかった）

#### Yahooファイナンス
検索語: `ANET`
- 11/24 TIKR | Could Meta Actually Climb 30%? Or Is J.P. Morgan Totally Wrong?
- 11/24 Trefis | Can Ciena Stock Hit $400?

### LITE（Lumentum Holdings Inc.、光・通信・ネットワーク、前日比 -2.2%、1週 -13.5%、時間外 +0.1%）

#### Googleニュース
検索語: `Lumentum stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- （取得できなかった）

#### Yahooファイナンス
検索語: `LITE`
- 11/24 24/7 Wall St. | Stephanie Link Says Marvell Could Earn $30 a Share by 2031. Is She Right?
- 11/24 Barrons.com | Review & Preview: Tech’s Rough Day
- 11/25 24/7 Wall St. | Coherent Sinks 10% Despite $15 Million Director Buy, Applied Optoelectronics Plunges 12% as AI Selloff Deepens; Lumentum Tumbles 10%

### CIEN（Ciena Corporation、光・通信・ネットワーク、前日比 +1.5%、1週 -8.9%、時間外 -0.3%）

#### Googleニュース
検索語: `Ciena stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- （取得できなかった）

#### Yahooファイナンス
検索語: `CIEN`
- 11/21 TIKR | A $10 Billion Fund Bought These 3 Stocks Last Quarter
- 11/22 Insider Monkey | Missed the First AI Rally? 5 Oversold Stocks With 50%+ Upside Potential
- 11/23 GuruFocus.com | Belden (BDC) Stock Is Up 9.4% Today: Nvidia Rally Lifts AI Hardware Stocks

### LRCX（Lam Research Corporation、半導体製造装置・材料・設計ソフト・計測、前日比 -5.7%、1週 -12.6%、時間外 +0.5%）

#### Googleニュース
検索語: `Lam Research stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- （取得できなかった）

#### Yahooファイナンス
検索語: `LRCX`
- 11/25 24/7 Wall St. | Applied Materials Falls 6% Despite UBS’s $575 Target as China Chip Curbs Hit Equipment Stocks; Lam Research Drops 7%, KLA Edges Lower
- 11/25 GuruFocus.com | Lam Research Stocks Plunge 9.54% With 35% of Sales Tied to China
- 11/25 MT Newswires | Top Midday Decliners

### AMAT（Applied Materials, Inc.、半導体製造装置・材料・設計ソフト・計測、前日比 -3.9%、1週 -11.5%、時間外 +0.2%）

#### Googleニュース
検索語: `Applied Materials stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- （取得できなかった）

#### Yahooファイナンス
検索語: `AMAT`
- 11/25 24/7 Wall St. | Billionaire Brad Gerstner’s Altimeter Opened a $680 Million Tesla Stake and Exited Qualcomm and Applied Materials
- 11/25 GuruFocus.com | Applied Materials Stocks Fall 7.98% as MATCH Act Fight Rattles Chip Toolmakers

### TER（Teradyne, Inc.、半導体製造装置・材料・設計ソフト・計測、前日比 -0.5%、1週 -9.7%、時間外 -1.9%）

#### Googleニュース
検索語: `Teradyne stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- （取得できなかった）

#### Yahooファイナンス
検索語: `TER`
- 11/24 GuruFocus.com | Why Ambarella (AMBA) Stock Is Down Today: Chip Stocks Sell Off
- 11/24 GuruFocus.com | Why FormFactor (FORM) Stock Is Down 12.4% Today: Semiconductor Selloff Hits Peers
- 11/24 GuruFocus.com | Why Ichor Holdings (ICHR) Stock Is Plunging Today: Semiconductor Equipment Selloff

## 4. 引けまでに大きく上げた銘柄（2026-11-19〜2026-11-25 の見出し）

### HPQ（HP Inc.、AIサーバー・ストレージ・メモリ・端末、前日比 +11.5%、1週 +8.7%、時間外 +0.3%）

#### Googleニュース
検索語: `HP stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- （取得できなかった）

#### Yahooファイナンス
検索語: `HPQ`
- 11/25 24/7 Wall St. | HP Earnings: Memory Went From 15% to 40% of a PC’s Parts Cost in a Year
