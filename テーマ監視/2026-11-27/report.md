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
| SNDK | ルール外（ユーザーの判断。この日はどのルールの合図もなし） |  | +4.3% | 保有継続 |  | **【未判定】（）** |
| AMD | ボリンジャーIII | -26.2% | +1.7% | **売り** | 終値 406.03 が損切り価格 467.47 以下 | 【未判定】（） |

## 候補の判定（並びは上の「買う順番」の表と同じ）

候補なし

- 時間外: 前の取引日の引けから、引け後（米国東部時間16〜20時）の最後の値までの騰落率（Yahoo。±5%以上は太字）。寄り付きの値段は、表の注文の目安（前日の終値で計算）から大きくずれることがある。原因の見出しは「ニュースの見出し」の節。

# 著者の回答（全文）

## 0_テーマの局面_ワインスタイン

1. **テーマ全体の局面**: 【ステージ3】（急騰後に30週移動平均線が横ばい化し天井圏を形成、第2章 [1]）。

2. **グループごとの局面**:
- 半導体｜ステージ3｜30週線横ばい [1]
- 半導体製造装置・材料・設計ソフト・計測｜ステージ4｜30週線下降・下 [2]
- AIサーバー・ストレージ・メモリ・端末｜ステージ3｜30週線横ばい [1]
- 光・通信・ネットワーク｜ステージ4｜30週線下降・下 [2]
- データセンターの電力・冷却・部品・受託製造・建設｜ステージ4｜30週線下降・下 [2]
- AIプラットフォーム・クラウド｜ステージ3｜30週線横ばい [1]
- AIソフト・セキュリティ・ITサービス｜ステージ3｜30週線横ばい [1]

3. **転換の兆し**: 出ている。30週線の水平化と下抜け（乖離-13.9%）[1, 2]、RSの弱気化 [3]、内部で3グループが第4ステージ転落 [4]。※「早めの警告」「50日線」「S2」「特殊な下げ」「ニュース件数」はマニュアルに規定なし。

4. **テーマの外**: 判定不能（ヒートマップが省略されデータから読み取れないため）。

（全体の版が空の応答だったため、1〜2節だけの短い版で送り直した回答。ヒートマップ・急騰急落・ニュースは渡していない）

# スキャン（数値と事実）


- 監視銘柄 87（判定できたのは 86、取得不可: SNDK）。
- この一覧は数値と事実だけ。売買の判断は著者のノートブックが行う。

## 1. テーマ（グループ）の強さ

| グループ | 銘柄数 | 1週 | 1カ月 | 3カ月 | 3カ月の順位 | 50日線より上の銘柄の割合 | グループ指数の30週線の局面（線との乖離、4週前からの線の傾き） |
|---|---|---|---|---|---|---|---|
| 半導体 | 16 | -7.6% | -21.7% | -16.5% | 4位 | 0% | 横ばい（-20.6%、+2.8%） |
| 半導体製造装置・材料・設計ソフト・計測 | 9 | -6.7% | -20.3% | -24.8% | 7位 | 0% | 下落（-24.3%、-0.3%） |
| AIサーバー・ストレージ・メモリ・端末 | 8 | -4.3% | -28.5% | -24.8% | 6位 | 25% | 横ばい（-15.5%、+4.3%） |
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
| 半導体（16） | 63件 | 9件 | 4.5 | 43件（2.7） | **悪いニュースが続いている** |
| AIサーバー・ストレージ・メモリ・端末（9） | 21件 | 5件 | 2.9 | 29件（3.2） | **良いニュースが多い** |
| AIプラットフォーム・クラウド（11） | 9件 | 10件 | 1.7 | 1件（0.1） |  |
| 光・通信・ネットワーク（9） | 1件 | 7件 | 0.9 | 8件（0.9） |  |
| 半導体製造装置・材料・設計ソフト・計測（9） | 3件 | 1件 | 0.4 | 9件（1.0） |  |
| データセンターの電力・冷却・部品・受託製造・建設（19） | 3件 | 3件 | 0.3 | 2件（0.1） |  |
| AIソフト・セキュリティ・ITサービス（14） | 1件 | 1件 | 0.1 | 13件（0.9） |  |

印のグループ（半導体）の最近の見出し: 2026-11-26 Despite Huang's Return, S&P Warns of NVIDIA Credit Rating Downgrade（파이낸셜뉴스）／2026-11-26 S&P Reviews NVIDIA Credit Downgrade: Governance, CEO Return（조선일보）／2026-11-26 S&P Warns of Nvidia Credit Downgrade as Governance Risks Mount（kaohoon international）

良いニュースが多いグループ（AIサーバー・ストレージ・メモリ・端末）の最近の見出し: 2026-11-26 HP Inc. Surges Over 11% Following Earnings Beat and Software Push : 기업주식정보 : JKN（재경일보）／2026-11-26 Should You Upgrade the 2017 Apple TV 4K to the New Model（Geeky Gadgets）

- **特殊な下げ（記録だけ。売買のルールは変えない）: あり（特殊な下げ）**（2026-10-16から）。SOX は直近60取引日の最高値から -33.6%（−15%以下が条件）、●A 前の1年の上げ +101.8%（+80%以上）、・B 雇用の伸び 137千人/月（2026-10まで。10万人未満）、●C 物価 4.1%（2026-10。3か月前 3.5%。3.5%以上で再加速）＝2つ（2つ以上が条件）。1995年〜でSOXが−15%以下かつ条件2つ以上の日は、120日後にSOXが下だったのが69%・250日後が70%（中央値 −33%）、AI以外の8業種の平均は250日後 −7%。ただし条件は過去を見て選んだもの（条件が2つ以上の局面は約5回）で、2026年7〜9月にこの間テーマを買わないと、その後の戻りを逃して2026年の成績は下がった（`バックテスト結果/実際の運用の期間の確認_2026-10-23/特殊な下げと過去の似た下げ.md`。2026-11-03）
- テーマ指数（監視銘柄の等金額平均）の30週線による局面: **横ばい**（上昇＝線より上かつ上向き、下落＝線より下かつ下向き、それ以外＝横ばい。ワインスタインのステージの近似）
- テーマ指数と50日線: 50日線より下（乖離 -13.9%）
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
| HPQ | AIサーバー・ストレージ・メモリ・端末 | +11.5% | 2.9倍 | 31.15 | 上 | 94 | レンジ |
| CDW | AIソフト・セキュリティ・ITサービス | +7.0% | 1.0倍 | 174.97 | 上 | 96 | 上昇相場 |
| ADI | 半導体 | +6.4% | 2.1倍 | 333.11 | 下 | 34 | 下げ |
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
| SNDK | ルール外（ユーザーの判断。この日はどのルールの合図もなし） | 2026-10-21 | 171.4125 | 取得不可 | | | | | |
| AMD | ボリンジャーIII | 2026-10-21 | 549.97 | 406.03 | -26.2% | 467.47 | **損切り価格を下回った**（2026-11-02 の安値 466.07。逆指値なら約定済み。まだ持っていれば次の寄り付きで売る） **成立（出来高2倍の大陰線が 2026-11-05 に出た → まだ持っていれば次の寄り付きで全部売る）** 売りの指値: 上部バンド 591.36（今夜この値に置き直す。届いた日に売れる）（2倍ETF AMUU で持っている場合も、判定は元の株 AMD の値段） | なし | 2027-02-02 |

- 出来高2倍の大陰線: 実体（始値−終値）が前日までのATR(14)の1.5倍以上、終値がその日の値幅の下25%以内、出来高が前日までの50日平均の2倍以上の日。**押し目（ボリンジャーIII）・急落の底の保有では売りのルール**: 出たら翌日の寄り付きで全部売り、空いた枠で次の合図を買う（2026-10-02 ユーザー決定。`バックテスト結果/やり直し_売りの合図の組み合わせ.md`。乱数3組とも年率が約+2ポイント、最大下落率もやや下がった）。ミネルヴィニ・新高値V2の保有では事実の表示（順張りに足しても良くならなかった）。

- 半分売りの合図（ミネルヴィニ・新高値V2の保有だけ）: 反転のローソク足（かぶせ線・弱気の包み足・宵の明星・流れ星）＋出来高が50日平均の1.5倍以上＋RSI(14)が前日か当日に70以上。買った後に最初に出た日の翌日の寄り付きで半分売り、残り半分は50日線割れ・損切り15%まで持つ（2026-10-01 ユーザー決定。`バックテスト結果/半分だけ売るとオニールの空き枠.md`）。

- かぶせ線（ミネルヴィニ・新高値V2の保有だけ）: 上昇中の陽線の翌日に、前日の高値より上で寄り付き、前日の陽線の真ん中より下（前日の始値より上）で引けた日。翌日の寄り付きで全部売り、空いた枠で次の合図を買う。半分売りより優先する（2026-10-01 ユーザー決定。`バックテスト結果/2倍ETFで売って買い直す.md`。順張りの売買の25%で出て、1回平均+2.0%、年率 21.4%→26.4%）。

## 5-2. 前日（2026-11-25の引け）の【買い（予約）】の確認

前日の【買い（予約）】はなし。

## 6. 候補（採用したルールの条件が成立＝A。予約（B）は2026-10-25から注文せず、節6-3に参考の表示だけ）

建玉の目安: 同時保有4銘柄まで、1銘柄に資金の25%（資金÷4）、損切りは買値の15%下（ユーザー決定 2026-09-29）。

本日は該当なし（著者への送信は不要）。


## 6-3. 参考: 条件の成立が目前の銘柄（予約は注文しない・著者には送らない）

2026-10-25 ユーザー決定: 予約（逆指値・指値）の注文はやめ、参考の表示だけにする。毎朝のツールと同じ条件・値段で予約の約定をバックテストに入れると、どの形も年率が下がった（後知恵なし 35.7%→30.7〜34.2%、87銘柄 45.6%→34.2〜42.6%。`バックテスト結果/点検_2026-10-25/`）。引けで条件がそろえば、翌朝の節6に買いの候補（A）として出る。各ルールでRSの高い順に2件まで。

| 参考の銘柄 | グループ | 種類 | 終値 | 前日比 | RS | 当てはまった条件 | 条件がそろう目安の価格（注文はしない） |
|---|---|---|---|---|---|---|---|
| CDNS | 半導体製造装置・材料・設計ソフト・計測 | ボリンジャー メソッドIII（%bが0.05未満に近い） | 294.89 | -0.6% | 17 | %b=0.148（0.05まであと少し）、21日II%=+0.004（>0） | 288.73（この値より下で引けると翌朝の買いの候補（A）。目安） |
| CEG | データセンターの電力・冷却・部品・受託製造・建設 | ボリンジャー メソッドIII（%bが0.05未満に近い） | 235.28 | -3.9% | 7 | %b=0.075（0.05まであと少し）、21日II%=+0.003（>0） | 233.88（この値より下で引けると翌朝の買いの候補（A）。目安） |


# ニュース（サブエージェントの調査）

# ニュース調査（2026-11-25 米国引け時点。見出しは headlines.md、不足分のみWeb検索）

## テーマ全体の下げの原因
当たる日（2グループの1週が-5%以下、早めの警告あり、S2あり）。確かめた先: headlines.md 1節の見出し（市場全体・半導体AI・信用・ショックの呼び名）と、Web検索3件（ADI・ORCL・NVIDIA）。
- きっかけ（連鎖）: NVIDIAのCEO（Jensen Huang）辞任（Moody's「credit negative」、11/18引け後に格付Aa1確認・見通しを積極的→安定へ。24/7 Wall St 11/19）。11/17にNVIDIAが米承認済みHopperチップの中国向け出荷停止（暫定CEOのKress氏。Yahoo Finance／Fox Business 11/18頃）。11/20 Google がBroadcom向けAIチップ計画を削減との報道でAVGO -12%（Barron's／24/7 Wall St 11/20）。同日ANET -12%・CIEN -9〜10%（Seeking Alpha 11/20）。11/19 AMDは空売りレポート（中国との関係、CNBC／Bloomberg 11/19）で急落。
- 11/24〜25: MUはBNPパリバ格下げで-11%（FinanceFeeds 11/25）、「将来の供給過剰」警告（MarketWatch 11/24）。LITE・COHR・AAOIなど光関連が-9〜13%（24/7 Wall St／Seeking Alpha 11/25）。LRCX・AMATは「AIけん引のチップ売り」で-10%前後の記述（GuruFocus 11/25）。11/25にS&PがNVIDIAの格下げ見直しを警告（見出し11/26 파이낸셜뉴스ほか）。
- 信用: AIのCDSスプレッドが拡大。OracleとCoreWeaveのCDSが過去最高水準（TradingView／Merced Sun-Star 11/25）。「Jensen Huang's second coming offers little relief to AI credits」（Yahoo Finance 11/25）。DoubleLineは3つの大手クラウド債について弱気から強気に転換（BigGo 11/25）。社債利回り・ハイイールド債の具体数値は取得不可。
- 市場全体: 11/25 S&P500・NASDAQは続落したが押し目買いで下げ幅縮小（Reuters 11/25）。ダウは164ドル高で、一時1,100ドル超下落（時事 11/25）。VIX・ハイイールド債スプレッドの数値は取得不可。ソフトウェア株は下げを免れたとの記事（FT 11/26）。
- 呼び名: 「エヌビディア・ショック」（トウシル 11/25）。「AI selloff」（24/7 Wall St 11/25）。
- 当日の材料: 経済指標・金利・要人発言は見出しからは確認できず。決算はHPQ上げ・DEREの通期見通し未達（時間外）。TSMC・ASML・大手クラウドの当日の決算は確認できず。感謝祭で11/26は休場。

## 引け後・時間外の材料
- SNDK: 時間外 +4.3%。原因の見出しは見つからなかった（11/24 Yahoo Financeに「急落」「15%上昇」の見出しあり、時間外の原因ではない）。
- NBIS: 時間外 +3.9%。原因の見出しは見つからなかった。
- PANW: 時間外 -3.7%。原因の見出しは見つからなかった。
- ALAB: 時間外 +3.4%。原因の見出しは見つからなかった。
- COHR: 時間外 +3.2%。原因の見出しは見つからなかった（11/25 取締役が約1,520万ドルを購入との報道あり。TIKR／24/7 Wall St 11/25）。
- AMD: 時間外 +1.7%。11/26 Simply Wall StにTaalas買収の完了の見出し。
- 時間外に±5%以上の監視銘柄はなし。DELLは決算後に時間外-5%（Yahoo!ファイナンス／株探 11/25。「好決算も」）、HPQは決算後に時間外で上昇（株探 11/25）。
- DEREは通期見通しが予想を下回り時間外で下落（BigGo／株探 11/25）。監視外。

## SNDK（保有）
- 時間外 +4.3%（引け73.51→76.68）。原因の見出しは見つからなかった。
- 11/24 Yahoo Finance「Why Sandisk Stock Plunged Today」、11/25 Benzinga「Why Is Sandisk Stock Trading Lower on Wednesday?」。1カ月で44%下落（Zacks 11/24）。
- 11/24 TradingView「15%上昇、ウォール街は192%の上値余地」（アナリストの目標株価の記事）。
- 悪材料: 確認できず（個別の不祥事・下方修正・売り出しの見出しなし）。※scan.mdは終値取得不可。

## AMD（保有）
- 11/19 空売り筋のレポートで中国との関係を指摘され急落（CNBC・Bloomberg・Yahoo Finance 11/19、Forbes 11/20）。1週 -23.4%。
- 11/26 24/7 Wall St: Tepper氏がBroadcomとAMDを手放した（保有削減）との記事。
- 11/26 Simply Wall St: Taalas買収の完了。
- 悪材料: あり（空売りレポートの中国関連の指摘。会社側の反論の有無は取得不可）。次回決算 2027-02-02。

## ADI（+6.4%、出来高2.1倍）
- 検索しても2026-11-25の原因は見つからなかった。2026年11月24日の決算発表予定との記載が1件ある（決算の結果は取得不可）。見出しにも原因なし。
- 半導体全体が下げる中での上げ。同日の他グループとの共通の動きは確認できなかった。

## LRCX（-5.7%、出来高1.8倍）
- 11/25 GuruFocus「LRCXは本日-10.6%、AI主導のチップ売り」。同日 AMAT・TERも同記事群。
- 11/25 Yahoo Finance: AMATはアナリストの目標引き下げで評価額が下がった（AMAT側）。
- 個別の原因（決算・格下げ）は見出しでは見つからなかった。業界全体の売りと同時。

## ORCL（-5.1%）
- 11/25 OracleのCDSスプレッドが過去最高水準（TradingView／Merced Sun-Star 11/25）。信用不安が背景。
- 11/26 24/7 Wall St: Tepper氏はOracleとMicronを買い増し。
- 当日の個別の決算・格付け変更は確認できず。

## DELL（+0.6%、出来高3.3倍）
- 決算発表（11/25引け後）。「好決算も時間外で5%安」（Yahoo!ファイナンス／株探 11/25）。ガイダンスの数値・Beat/Missの詳細は取得不可（検索は前年の記事のみ）。

## HPQ（+11.5%、出来高2.9倍）
- 決算（11/25）で関税の追い風もあり予想を上回った。「関税の追い風でBeat」（Quantisnow 11/25）、「約15%上昇」（Yahoo Finance 11/25）。チップ株が下げる中で上昇。ソフトウェア面の強化も報じられた（JKN 11/26）。
- 11/24 HPE（別会社）が16%下落（Motley Fool 11/24）。

## CDW（+7.0%）
- 原因となる直接の見出しは見つからなかった。11/19 DevRevとの提携（OpenAIモデル使用、Business Wire）。11/26 Yahoo Finance「決算のBeat」。11/23 Barclaysが目標株価を引き上げ。

## 監視外の注目銘柄（1年の高値更新。テーマ外）
- BDX、AIZ、ADP、EG、MAS: 原因の見出しは取得しておらず（headlines.mdに見出しなし）、検索もしていない。「原因となるニュースは確認できず（未調査）」。テーマ外の業種（医療機器・保険・給与処理・再保険・建材）。
- 3カ月の業種順位ではテーマが下位（半導体134位など）、上位はDiscount Stores・Medical Distribution等（scan.md 3節）。

## テーマ全体に関わる大きなニュース（直近1週間）
- NVIDIA: CEO辞任（11/中旬）、Moody's見通し変更（11/18）、S&Pの格下げ見直し警告（11/25〜26）、中国向けHopper出荷停止（11/17）。
- Google→Broadcom AIチップ計画削減の報道（11/20）。
- SK hynixが次世代DRAMを公表（24/7 Wall St 11/26）。
- トム・リー氏「米株はすでに底入れ、VIX急騰は2018年と類似」（BigGo 11/26）。
- 米国株市場は11/26感謝祭で休場、11/27は短縮取引。

# ニュースの見出し（プログラムが自動で取得）

- Googleニュース（日付を指定）とYahooファイナンスの見出しを `tools/news_headlines.py` が自動で並べたもの。日付は米国東部時間の配信日（引け後の記事は翌日付）。原因の判断・売買の判断はしていない。
- 調べた銘柄の選び方: ①保有 ②今日の候補 ③時間外に±5%以上動いた監視銘柄 は全部、④引けまでに大きく動いた銘柄（1週で±5%のグループの上位3・1日で±7%）は合計12銘柄まで。
- 1週で−5%以下のグループ: 半導体（-7.6%）、光・通信・ネットワーク（-7.3%）、半導体製造装置・材料・設計ソフト・計測（-6.7%）
- 1週で+5%以上のグループ: なし

## 0. 時間外（引け後）の値動き（2026-11-25 の引けから、Yahoo。±3%以上の監視銘柄と、保有・候補は全部）

| 銘柄 | 区分 | 引け | 時間外 | 騰落率 |
|---|---|---|---|---|
| SNDK | 保有 | 73.51 | 76.68（19:59 ET） | +4.3% |
| NBIS | 監視 | 84.97 | 88.24（19:59 ET） | +3.9% |
| PANW | 監視 | 356.19 | 342.87（19:59 ET） | -3.7% |
| ALAB | 監視 | 190.07 | 196.50（19:54 ET） | +3.4% |
| COHR | 監視 | 196.19 | 202.42（19:59 ET） | +3.2% |
| AMD | 保有 | 406.83 | 413.81（19:59 ET） | +1.7% |

## 1. 市場全体（2026-11-25）

### 市場全体（英語のまとめ記事）
検索語: `stocks Wall Street close Nasdaq`
- 11/25 Reuters | Nasdaq, S&P 500 end down, but well off lows as investors buy bargains
- 11/26 Detroit Free Press | Is the stock market closed? Thanksgiving, Black Friday trading hours
- 11/26 Barron's | Is the Stock Market Open Today? Here Are the Trading Hours for Thanksgiving.
- 11/26 Investor's Business Daily | Stock Market Trading Hours For Thanksgiving And Black Friday
- 11/26 NJ.com | Is the stock market open on Black Friday 2026?

### 市場全体（Stock Market Today）
検索語: `"stock market today"`
- 11/25 Investor's Business Daily | Stock Market Today: Stock Market News And Analysis
- 11/26 Barron's | Stock Futures Rise as Dow’s Rebound Goes Global. It Bodes Well for Black Friday Trading.
- 11/26 Bloomberg | Stocks, Nasdaq Futures Climb as AI Trade Rebounds: Markets Wrap
- 11/26 Investor's Business Daily | Dow Jones Futures Rise With U.S. Markets Shut; Look For This Bullish Signal

### 市場全体（日本語のまとめ記事）
検索語: `米国株式市場 OR NY株`
- 11/25 時事ドットコム | ＮＹ株続伸、１６４ドル高 一時１１００ドル超下落：時事ドットコム
- 11/25 Reuters | 米国株式市場＝ナスダック・Ｓ＆Ｐ続落、押し目買いで下げ幅は縮小
- 11/25 大分合同新聞 | ＮＹ株続伸、１６４ドル高
- 11/26 外為どっとコム | 【見通し】NY株見通しー今晩のNY株式市場は休場（感謝祭）
- 11/26 Yahoo!ファイナンス | お知らせ＝「今晩のＮＹ株の読み筋」は感謝祭で休場のため休みます(ウエルスアドバイザー)

### 半導体・AI株（英語）
検索語: `chip stocks OR semiconductor stocks OR AI stocks`
- 11/26 Yahoo Finance | Micronics Japan And 2 More AI Chip Stocks To Watch
- 11/26 Axios | The economy is hot, but stocks are not.
- 11/26 CNBC | Semiconductor chips are the new oil. Here's why
- 11/26 Financial Times | Software stocks spared in tech rout as AI narrative shifts
- 11/26 CoinDesk | Nvidia shipment halt threatens to stall the AI rally

### 信用（社債・借金）
検索語: `AI debt OR bonds OR credit spreads OR CDS`
- 11/25 Yahoo Finance | Jensen Huang's second coming offers little relief to AI credits
- 11/25 Merced Sun-Star | AI credit default swap spreads widen on unease over cash flow
- 11/25 BigGo Finance | AI Bonds Fall Out of Favor? DoubleLine Credit Chief Flips From Bearish to Bullish, Names Three Cloud Giants' Bonds
- 11/25 TradingView | AI credit risk mounts as CDS spreads for Oracle, CoreWeave hit record levels
- 11/26 Crypto Briefing | Investors boost CDS use amid AI corporate debt concerns

### 「〇〇ショック」の呼び名（日本語）
検索語: `ショック 株`
- 11/25 トウシル | エヌビディア・ショック後もドル円は冷静。米感謝祭を前に年内は手じまい優先か
- 11/25 日本経済新聞 | アドバンテストよりソニー、「割高」でもエンタメに流れる資金 ヴェリタスEYE（11月25日） - 日経ヴェリタス
- 11/26 日本経済新聞 | JTの「ロシアショック」、株価急落も個人は逆張りの買い
- 11/26 日本経済新聞 | 日本株相場、一本足打法から全員野球へ 年末高に期待
- 11/26 BigGo ファイナンス | トム・リー氏、米株はすでに底入れと主張－VIX急騰は2018年と類似

### 引け後・時間外の動き（英語）
検索語: `"after hours" OR "after the bell" OR "extended trading" stocks`
- 11/25 TradingView | Beyond Meat (BYND) Stock Is Trending in After-Hours Trading: Here's What You Should Know
- 11/25 ChartMill | After-Hours Movers: Nov. 25, 2026 Gainers and Losers
- 11/25 Benzinga | Beyond Meat Shares Fall 1.12% After Hours Following 20% Rally - Beyond Meat (NASDAQ:BYND)
- 11/26 Yahoo Finance | Vera Therapeutics Stock Soars After Hours as the FDA Delays Vertex’s Rival Kidney Drug
- 11/26 Benzinga | Blue Gold Stock Plunges 19% After Hours: What's Happening?
- 11/26 Benzinga | Healthcare Triangle Stock Plunges After Hours: What's Happening?
- 11/26 TradingView | Nexus Advanced Technologies (NXAT) Stock Jumps Over 27% After Hours as Company Names New Co-CEO

### 引け後・時間外の動き（日本語）
検索語: `時間外 決算 株`
- 11/25 SBI証券 | 米国株『23時間取引』で何が変わる？ 広がる投資機会と時間外取引の注意点
- 11/25 株探 | ＨＰ、決算受け時間外で上昇＝米国株個別
- 11/25 BigGo ファイナンス | ディア、通期見通しが予想を大きく下回る 時間外で5%急落後に反発し乱高下
- 11/25 Yahoo!ファイナンス | ディア、決算受け時間外で下落＝米国株個別(株探ニュース)
- 11/25 株探 | ディア、決算受け時間外で下落＝米国株個別
- 11/25 Yahoo!ファイナンス | デル、好決算も時間外で５％安＝米国株個別(株探ニュース)
- 11/25 株探 | 【市況】 NY原油：続伸で83.97ドル、フーシ派のサウジ製油所へのドローン攻撃で供給ひっ迫懸念強まる
- 11/25 FinanceFeeds | MU株価 629.79ドル: BNPパリバ格下げで11%下落

### 買収・合併（英語）
検索語: `acquisition OR acquire OR merger OR takeover chip OR semiconductor OR AI OR optical`
- 11/25 WorkBoat | Saab completes acquisition of maritime autonomy developer Mythos AI
- 11/25 PYMNTS.com | OpenAI Says Most Users Won’t Hit Limits Faster After Merger of Chat and Work
- 11/25 CASRAI | WA Suspends Deloitte Over AI-Flawed Merger Report
- 11/26 BigGo Finance | Paul Christiano's 10% AI Takeover Odds Collide With Nvidia's $1 Trillion Moat — What the Debate Missed
- 11/26 Dealroom | Provoke rebrands as Ponteva in merger targeting NZ's AI skills gap
- 11/26 TradingView | Envision Greenwise: Revenue surged on metals trading and AI-computing expansion, alongside sizable acquisition commitments
- 11/26 Simply Wall St | Advanced Micro Devices (AMD) Completes Taalas Acquisition
- 11/26 MarTech Cube | Five9 Announced the Acquisition of Level AI

## 2. 保有・候補・時間外で大きく動いた銘柄（2026-11-19〜2026-11-25 の見出し）

### SNDK（Sandisk Corporation、保有、時間外 +4.3%）

#### Googleニュース
検索語: `Sandisk stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/24 Yahoo Finance | Why Sandisk Stock Plunged Today
- 11/24 Zacks Investment Research | Sandisk Plunges 44% in a Month: Buy, Sell or Hold the Stock?
- 11/24 TradingView | Sandisk Stock Jumps 15% as Wall Street Sees 192% Upside
- 11/25 Benzinga | Why Is Sandisk Stock Trading Lower on Wednesday?

#### Yahooファイナンス
検索語: `SNDK`
- 11/26 24/7 Wall St. | This AI Investing Prodigy Lost 65% in a Single Quarter and Is Still Up 88.5% in 2026. Here’s the Lesson for Investors.
- 11/26 GuruFocus.com | ETFs Are Buying SanDisk (SNDK) on Nov. 24
- 11/26 GuruFocus.com | Micron and Sandisk Are Two of the Cheapest AI Chip Stocks to Own

### AMD（Advanced Micro Devices, Inc.、保有、半導体、前日比 -1.8%、1週 -23.4%、時間外 +1.7%）

#### Googleニュース
検索語: `Advanced Micro Devices stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/19 Yahoo Finance | Why AMD Stock Was Plunging on Thursday
- 11/19 CNBC | AMD dives on short seller report of alleged China exposure
- 11/19 Bloomberg.com | AMD Shares Slump After Shortseller Raises China Concerns
- 11/20 Forbes | Nvidia Rival AMD’s Stock Slides Sharply In Premarket After Report Alleges China Ties

#### Yahooファイナンス
検索語: `AMD`
- 11/26 24/7 Wall St. | NVIDIA Just Dropped 31% in a Month. Will NVDA Stock Hit $125 or $200 First?
- 11/26 24/7 Wall St. | S&P’s NVIDIA Warning is Backward Looking Governance Theater That Gives Everyone an Opportunity to Buy at $150
- 11/26 24/7 Wall St. | Tepper Trims Alphabet by ~46% and Dumps Broadcom & AMD While Backing Micron and Oracle

## 3. 引けまでに大きく下げた銘柄（2026-11-19〜2026-11-25 の見出し）

### AVGO（Broadcom Inc.、半導体、前日比 -0.1%、1週 -15.0%、時間外 +1.2%）

#### Googleニュース
検索語: `Broadcom stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/20 Barron's | Broadcom Stock Falls on Report Google is Cutting AI Chip Shipments
- 11/20 24/7 Wall St. | Broadcom Stock Plunges 12% and Loses $191 Billion After a Report That Google Cut Its Plans for Broadcom AI Chips
- 11/22 Yahoo Finance | Why Broadcom Stock Could Double by 2030
- 11/23 Trefis | Why Did Broadcom Stock Drop On Friday?

#### Yahooファイナンス
検索語: `AVGO`
- 11/26 24/7 Wall St. | 3 AI Infrastructure Stocks That Pay You While You Wait
- 11/26 24/7 Wall St. | Heading Into FY27: How to Trade Broadcom’s ~$115B AI Target Against Nvidia’s Multiple Reset

### MU（Micron Technology, Inc.、半導体、前日比 -4.5%、1週 -14.7%、時間外 +1.8%）

#### Googleニュース
検索語: `Micron stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/21 Yahoo Finance | Micron Stock Fell More Than 40% From Its June Record. History Says What It Did After Its 5 Other Drops This Deep.
- 11/23 Barron's | Micron Stock Jumps 19%. Why the Rally Has Legs.
- 11/24 MarketWatch | Micron’s stock falls as an analyst warns about a future supply glut

#### Yahooファイナンス
検索語: `MU`
- 11/26 24/7 Wall St. | Jim Cramer Says Micron Stock Is “Comically Cheap” at About 3 Times Earnings
- 11/26 24/7 Wall St. | SK Hynix Just Revealed the Next Generation of DRAM. Can It Beat Micron in the Next Memory Supercycle?

### ANET（Arista Networks, Inc.、光・通信・ネットワーク、前日比 -2.7%、1週 -15.4%、時間外 +1.9%）

#### Googleニュース
検索語: `Arista Networks stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/20 Benzinga | Why Is Arista Networks Stock Plunging Friday?
- 11/20 Traders Union | Arista Networks stock falls amid weak momentum and downward price move
- 11/20 Seeking Alpha | Arista Networks sinks 12% amid tech and AI selloff (ANET:NYSE)
- 11/23 Yahoo Finance | What Moved Arista Networks Stock?

#### Yahooファイナンス
検索語: `ANET`
- 11/25 MT Newswires | Arista Networks Insider Sold Shares Worth $1,735,582, According to a Recent SEC Filing
- 11/25 TIKR | 104% Upside for Broadcom? Bernstein Thinks So, and Here’s How

### LITE（Lumentum Holdings Inc.、光・通信・ネットワーク、前日比 -2.2%、1週 -13.5%、時間外 +2.7%）

#### Googleニュース
検索語: `Lumentum stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/23 AOL.com | Why Lumentum Holdings Stock Trounced the Market Today
- 11/24 Investing.com | Why is Lumentum stock sliding today?
- 11/24 Yahoo Finance | Lumentum (LITE) Stock Looks Richly Priced As Its Three Year Run Continues
- 11/25 Seeking Alpha | Lumentum Holdings loses 9% as tech falls (LITE:NASDAQ)

#### Yahooファイナンス
検索語: `LITE`
- 11/25 24/7 Wall St. | Coherent Sinks 10% Despite $15 Million Director Buy, Applied Optoelectronics Plunges 12% as AI Selloff Deepens; Lumentum Tumbles 10%
- 11/25 24/7 Wall St. | Coherent’s Director Bought $15 Million of Stock as It Plunged 13%
- 11/25 TIKR | Coherent Director Stephen Pagliuca Just Bought $15.2 Million of Stock at Less Than Half Its June High

### CIEN（Ciena Corporation、光・通信・ネットワーク、前日比 +1.5%、1週 -8.9%、時間外 +1.9%）

#### Googleニュース
検索語: `Ciena stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/20 Seeking Alpha | Ciena slides 9% amid broad tech weakness (CIEN:NYSE)
- 11/20 AlphaStreet | Ciena Drops 8.6% Amid Sector-Wide Selling
- 11/20 Global Banking & Finance Review | Ciena falls 10.76% in Friday's session
- 11/25 StockStory | Ciena, Nokia, Infleqtion, BigBear.ai, and Fabrinet shares plummet, what you need to know

#### Yahooファイナンス
検索語: `CIEN`
- 11/22 Insider Monkey | Missed the First AI Rally? 5 Oversold Stocks With 50%+ Upside Potential
- 11/23 GuruFocus.com | Belden (BDC) Stock Is Up 9.4% Today: Nvidia Rally Lifts AI Hardware Stocks
- 11/23 GuruFocus.com | Harmonic Stock Jumps 10.4% in Tech Rally, No Company News on Monday

### LRCX（Lam Research Corporation、半導体製造装置・材料・設計ソフト・計測、前日比 -5.7%、1週 -12.6%、時間外 +2.2%）

#### Googleニュース
検索語: `Lam Research stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/20 Yahoo Finance | Why Is Lam Research (LRCX) Down 11.5% Since Last Earnings Report?
- 11/23 Trefis | What Is Driving Lam Research Stock?
- 11/23 Investing.com | Why is Lam Research stock surging today?
- 11/23 StockInvest.us | Lam Research Stock Price Forecast. Should You Buy LRCX?

#### Yahooファイナンス
検索語: `LRCX`
- 11/25 24/7 Wall St. | Why My Analysis Points to Nearly 40% Semiconductor Equipment Growth in 2026
- 11/25 Barrons.com | Anthropic, Nvidia, Micron, HP Inc., Dell, Deere, and More Stocks That Explain Today’s Market
- 11/25 Insider Monkey | Memory Makers Are Spending Again. Will Lam Research (LRCX) Cash In?

### AMAT（Applied Materials, Inc.、半導体製造装置・材料・設計ソフト・計測、前日比 -3.9%、1週 -11.5%、時間外 +1.1%）

#### Googleニュース
検索語: `Applied Materials stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/19 24/7 Wall St. | Applied Materials Is Still Up 35% This Year. Will AMAT Stock Hit $300 or $400 First?
- 11/23 Trefis | What Triggered The Fall In Applied Materials Stock?
- 11/23 Investing.com | Why is Applied Materials stock surging today?
- 11/25 Yahoo Finance | Applied Materials (AMAT) Stock Sees Fair Value Cut As Analysts Trim Targets

#### Yahooファイナンス
検索語: `AMAT`
- 11/25 Insider Monkey | Applied Materials (AMAT) Supplies Almost Every Fab. Is That Enough?
- 11/25 Simply Wall St. | Applied Materials (AMAT) Falls In Chip Selloff, Is It 44% Undervalued?

### TER（Teradyne, Inc.、半導体製造装置・材料・設計ソフト・計測、前日比 -0.5%、1週 -9.7%、時間外 +2.2%）

#### Googleニュース
検索語: `Teradyne stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/19 Yahoo Finance | Is Teradyne (TER) a Solid Growth Stock? 3 Reasons to Think "Yes"
- 11/20 TradingView | FormFactor, Amkor, Himax, Teradyne, and Entegris shares are falling, what you need to know
- 11/22 Yahoo Finance | Teradyne (TER) Falls 36% Despite 70% Revenue Growth: Is a Recovery Ahead?
- 11/23 Simply Wall St | Teradyne (Nasdaq:TER) - Stock Analysis

#### Yahooファイナンス
検索語: `TER`
- 11/25 GuruFocus.com | Lam Research (LRCX) Stock Is Down 10.6% Today: AI-Led Chip Selloff
- 11/25 GuruFocus.com | Why Applied Materials (AMAT) Stock Is Falling Today: AI-Led Chip Selloff
- 11/25 Simply Wall St. | Learn Why The Bull Case For Teradyne Stock Could Change Following Built In AI Vision

## 4. 引けまでに大きく上げた銘柄（2026-11-19〜2026-11-25 の見出し）

### HPQ（HP Inc.、AIサーバー・ストレージ・メモリ・端末、前日比 +11.5%、1週 +8.7%、時間外 +0.4%）

#### Googleニュース
検索語: `HP stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/24 The Motley Fool | Why Hewlett Packard Enterprise Stock Fell 16% Today
- 11/25 Yahoo Finance | Why HP Inc. Stock Jumped Nearly 15% Today
- 11/25 TradingView | Why is HP stock one of the top performing stocks in today's session?
- 11/25 Quantisnow | HP Inc. jumps 11.4% after a tariff-aided beat while chip stocks fall

#### Yahooファイナンス
検索語: `HPQ`
- 11/25 Investing.com | HPQ earnings analysis: questions answered and next catalysts
- 11/25 Kiplinger | Stocks Rally Off Lows Despite Inflation and AI Gloom: Stock Market Today

### CDW（CDW Corporation、AIソフト・セキュリティ・ITサービス、前日比 +7.0%、1週 +4.0%、時間外 -0.0%）

#### Googleニュース
検索語: `CDW stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/19 Traders Union | CDW Corp forms new alliance with DevRev using OpenAI models as stock edges lower
- 11/23 TradingView | Weekly Recap: CDW-DevRev AI alliance and Barclays raises target to $164
- 11/24 MarketWatch | CDW Corp. stock underperforms Tuesday when compared to competitors
- 11/26 Yahoo Finance | CDW Stock Earnings Beat Has The Bull Case Changed?

#### Yahooファイナンス
検索語: `CDW`
- 11/19 Business Wire | CDW Expands AI Ecosystem Through New DevRev Alliance Built Using OpenAI Models
- 11/19 MT Newswires | CDW, DevRev Partner to Bring OpenAI Models to Enterprise AI Services
- 11/20 Business Wire | CDW Canada Named an IDC CIO Awards Canada 2026 Winner
