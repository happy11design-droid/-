# テーマ監視 2026-10-26

# 判定のまとめ（ルールの判定と著者の判定を分けて表示）

- **ルールの判定**: 採用した売買ルール（スクリプト）が数値で決めたもの。損切りは買値の15%下の逆指値（日中に届けばその場で売れる）。
- **著者の判定**: ノートブックの著者の回答。買いは注文を止める理由があるときだけ【様子見】、保有はルールより早く手じまう理由があるときだけ【売り】。根拠は下の「著者の回答（全文）」。
- 2つが食い違うときに、どちらに従うかはユーザーが決める。

- **テーマ全体の急落（S2・記録だけ）: あり（S2）**（SOXが直近60取引日の最高値から -16.1%）。S2の日の順張りの候補には「S2なら見送る形」と付ける（売買のルールは変えない。記録してから採用を決める。2026-10-14）

## 保有銘柄

| 銘柄 | ルール | 損益 | ルールの判定 | ルールの判定の理由 | 著者の判定 |
|---|---|---|---|---|---|
| SNDK | ルール外（ユーザーの判断。この日はどのルールの合図もなし） | -8.4% | 保有継続 | 損切り 1165.61（終値から -7.2%） | **【未判定】（）** |
| AMD | ボリンジャーIII | -3.4% | 保有継続 | 損切り 467.47（終値から -12.0%） | **【未判定】（）** |

## 候補の判定（並びは上の「買う順番」の表と同じ）

候補なし

# 著者の回答（全文）

## 0_テーマの局面_ワインスタイン

1. **テーマ全体の局面**: 【ステージ2】（テーマ指数が30週移動平均線の上で、線自体も上向きのため。第2章・第8章）

2. **グループごとの局面**:
- 半導体｜ステージ2｜30週線の上かつ線が上昇（第2章）
- 半導体製造装置・材料・設計ソフト・計測｜ステージ3｜30週線の下かつ線が横ばい（第2章）
- AIサーバー・ストレージ・メモリ・端末｜ステージ2｜30週線の上かつ線が上昇（第2章）
- 光・通信・ネットワーク｜ステージ3｜30週線の下かつ線が横ばい（第2章）
- データセンターの電力・冷却・部品・受託製造・建設｜ステージ3｜30週線の下かつ線が横ばい（第2章）
- AIプラットフォーム・クラウド｜ステージ3｜30週線の下かつ線が横ばい（第2章）
- AIソフト・セキュリティ・ITサービス｜ステージ2｜30週線の上かつ線が上昇（第2章）

3. **転換の兆し**:
出ている。7グループ中4グループの株価が30週線を割って横ばい（ステージ3化）している点、対S&P500の相対的強さ（RS）低下、50日線割れは、上昇モメンタム鈍化と内部乖離を示す天井の兆候（第4章・第8章）。（※割合40%等の数値閾値はマニュアルに規定なし）

4. **テーマの外**:
判定不能（ヒートマップデータ省略のため）

（全体の版が空の応答だったため、1〜2節だけの短い版で送り直した回答。ヒートマップ・急騰急落・ニュースは渡していない）

# スキャン（数値と事実）


- 監視銘柄 87（判定できたのは 86、取得不可: Q）。
- この一覧は数値と事実だけ。売買の判断は著者のノートブックが行う。

## 1. テーマ（グループ）の強さ

| グループ | 銘柄数 | 1週 | 1カ月 | 3カ月 | 3カ月の順位 | 50日線より上の銘柄の割合 | グループ指数の30週線の局面（線との乖離、4週前からの線の傾き） |
|---|---|---|---|---|---|---|---|
| 半導体 | 16 | -0.1% | -6.7% | +8.1% | 3位 | 38% | 上昇（+1.6%、+6.4%） |
| 半導体製造装置・材料・設計ソフト・計測 | 8 | -3.4% | -10.0% | -3.6% | 6位 | 25% | 横ばい（-9.6%、+3.0%） |
| AIサーバー・ストレージ・メモリ・端末 | 9 | +1.8% | -16.9% | +14.9% | 2位 | 33% | 上昇（+11.4%、+9.4%） |
| 光・通信・ネットワーク | 9 | -2.0% | -13.1% | +1.6% | 5位 | 33% | 横ばい（-4.7%、+3.2%） |
| データセンターの電力・冷却・部品・受託製造・建設 | 19 | -2.3% | -4.0% | -4.7% | 7位 | 21% | 横ばい（-8.1%、+0.9%） |
| AIプラットフォーム・クラウド | 11 | -3.1% | -7.7% | +6.3% | 4位 | 36% | 横ばい（-4.2%、+2.0%） |
| AIソフト・セキュリティ・ITサービス | 14 | +6.8% | +10.1% | +22.4% | 1位 | 93% | 上昇（+26.6%、+5.1%） |

## 2. テーマ全体の状態と早めの警告

- 市場全体の30週線による局面: S&P500指数 **上昇**／NASDAQ100指数 **上昇**（急落の底で買うルールは、過去の検証で下落相場で特に強く、横ばいの相場では負けていた）
- **2倍ETFを使う局面（案1、2026-10-13 採用）: S&P500の20週線（100日線）で 上昇** → 2倍ETFのある銘柄は2倍ETFで買う（SPY 765.37、100日線 756.70、20日前の線 750.89。上昇＝線より上かつ線が上向き）
- **テーマ全体の急落（S2、記録だけ。売買のルールは変えない）: あり（S2）**（SOX 11083.47、直近60取引日の最高値 13217.82 から -16.1%。S2＝最高値から−10%以上）。S2のときに「順張りの新しい買いだけ止める」形を記録で比べる（2026-10-14 ユーザー決定。バックテストでは年率は上がったが2つの期間ではどちらも少し下回ったため、記録してから採用を決める。`バックテスト結果/テーマ全体の急落を検知して手じまう・買いを止める.md`）
- テーマ指数（監視銘柄の等金額平均）の30週線による局面: **上昇**（上昇＝線より上かつ上向き、下落＝線より下かつ下向き、それ以外＝横ばい。ワインスタインのステージの近似）
- テーマ指数と50日線: 50日線より下（乖離 -3.3%）
- S&P500に対する相対的な強さ: 50日平均より下（S&P500より弱い）
- 監視銘柄のうち50日線より上の割合: 41%
- 警告（割合が40%未満かつテーマ指数が50日線より下）: **出ていない**
- 参考（バックテスト）: 30週線の「下落」は高値から10〜33%下げた後に出る遅い判定。50日線・割合・相対的な強さは高値から2〜8%で出るが、誤報が年15回以上ある。警告中に新しい買いを止めると、押し目買い（ボリンジャーIII）の成績は大きく下がった（`バックテスト結果/テーマ監視銘柄・直近3年.md` 11・12節）。

## 3. ヒートマップ（Finviz、全米の業種別の騰落率）

3カ月の騰落率の上位15業種（テーマの外で強くなっている業種の確認用）:

| 順位 | 業種 | 1週 | 1カ月 | 3カ月 | 6カ月 | 1年 |
|---|---|---|---|---|---|---|
| 1 | Oil & Gas Refining & Marketing | -1.0% | +13.0% | +39.9% | +78.5% | +118.1% |
| 2 | Health Information Services | +2.7% | +7.7% | +30.6% | +53.9% | +2.1% |
| 3 | Software - Infrastructure | +1.8% | +2.2% | +30.2% | +26.9% | +1.7% |
| 4 | Oil & Gas Drilling | +7.0% | +13.1% | +24.7% | -6.9% | +50.0% |
| 5 | Oil & Gas Integrated | +1.9% | +12.0% | +20.4% | +19.6% | +57.8% |
| 6 | Oil & Gas E&P | +2.6% | +14.1% | +19.8% | +12.4% | +49.1% |
| 7 | Diagnostics & Research | +3.4% | +3.0% | +19.5% | +46.1% | +23.8% |
| 8 | Software - Application | +3.6% | +9.7% | +18.5% | +28.5% | -13.4% |
| 9 | Auto Manufacturers | +4.4% | +3.2% | +17.1% | +1.4% | -12.2% |
| 10 | Information Technology Services | +5.5% | +14.9% | +12.9% | +9.8% | -17.5% |
| 11 | Medical Instruments & Supplies | +3.5% | +7.1% | +11.4% | +5.5% | -3.6% |
| 12 | Gold | -6.3% | -12.3% | +10.9% | -12.8% | +11.8% |
| 13 | Shell Companies | +1.2% | +6.5% | +10.8% | +20.4% | +16.8% |
| 14 | Marine Shipping | +2.6% | +3.2% | +10.2% | +12.1% | +76.4% |
| 15 | Grocery Stores | +5.2% | +12.7% | +8.9% | -1.1% | -11.3% |

テーマの業種の順位（3カ月、全144業種中）: Semiconductors 24位、Semiconductor Equipment & Materials 112位、Computer Hardware 45位、Communication Equipment 42位、Electronic Components 84位、Software - Infrastructure 3位、Software - Application 8位、Internet Content & Information 68位

## 4. 急騰・急落した銘柄（前日比±5%以上、または出来高が50日平均の2倍以上）

原因のニュースをサブエージェントが調べ、候補・保有銘柄の判定材料として著者に渡す。急騰・急落そのものは売買の合図にしない（後知恵のないS&P500全体のバックテストでは、急騰の翌日に買うルールは年率7%、急落の翌日に買うルールは年率9〜10%で、採用した3つのルールより優れていなかった）。

| 銘柄 | グループ | 前日比 | 出来高（50日平均の倍） | 終値 | 50日線 | RS | 局面 |
|---|---|---|---|---|---|---|---|
| LITE | 光・通信・ネットワーク | +8.2% | 1.3倍 | 818.10 | 下 | 98 | レンジ |
| ARM | 半導体 | +6.2% | 1.0倍 | 223.35 | 下 | 85 | レンジ |
| COHR | 光・通信・ネットワーク | +5.8% | 1.1倍 | 221.50 | 下 | 63 | レンジ |
| SNPS | 半導体製造装置・材料・設計ソフト・計測 | +5.6% | 1.3倍 | 454.33 | 上 | 48 | レンジ |
| AKAM | 光・通信・ネットワーク | +5.3% | 1.2倍 | 98.50 | 下 | 44 | レンジ |
| TSLA | AIプラットフォーム・クラウド | +5.2% | 1.4倍 | 391.62 | 上 | 59 | レンジ |

- 局面: 終値 > 50日線 > 200日線、50日線が20取引日前より2%以上高い、ADX(14) ≧ 20 をすべて満たせば上昇相場、それ以外はレンジ（判定式はClaudeが置いたもの）。

## 4-2. 監視外の注目銘柄（S&P500・NASDAQ100のうち監視銘柄に入っていない銘柄）

条件: 流動性（株価5ドル以上・50日平均出来高25万株以上）があり、(a) 前日比+8%以上かつ出来高が50日平均の2倍以上、または (b) 終値が直前1年の最高値（終値）を上回り、RS≧90。RSの高い順に5銘柄（ニュースを調べる）。監視銘柄に入れるかはユーザーが決める。

| 銘柄 | 種類 | 前日比 | 出来高（50日平均の倍） | RS | 終値 |
|---|---|---|---|---|---|
| CRL | 1年の高値更新 | +3.4% | 1.2倍 | 96 | 357.27 |
| RVTY | 1年の高値更新 | +1.0% | 0.6倍 | 96 | 160.39 |
| COP | 1年の高値更新 | +0.4% | 0.8倍 | 94 | 151.37 |
| TRGP | 1年の高値更新 | +0.8% | 0.7倍 | 94 | 304.68 |
| EOG | 1年の高値更新 | +0.4% | 0.7倍 | 93 | 163.68 |

- ほかに3銘柄: XOM（1年の高値更新、RS 92）、HAS（1年の高値更新、RS 92）、WST（1年の高値更新、RS 91）

## 5. 保有銘柄の手じまい条件（`新分析ツール/保有銘柄.md`）

| 銘柄 | ルール | 買った日 | 買値 | 終値 | 損益 | 損切り価格（買値の15%下、逆指値） | ルールの手じまい条件 | 出来高2倍の大陰線（買った後の直近5日） | 次回決算予定日 |
|---|---|---|---|---|---|---|---|---|---|
| SNDK | ルール外（ユーザーの判断。この日はどのルールの合図もなし） | 2026-10-21 | 1371.30 | 1255.58 | -8.4% | 1165.61 | ルールが不明（保有銘柄.md の「ルール」を確認） | なし | 2026-10-29 |
| AMD | ボリンジャーIII | 2026-10-21 | 549.97 | 531.28 | -3.4% | 467.47 | 売りの指値: 上部バンド 672.83（今夜この値に置き直す。届いた日に売れる）（2倍ETF AMUU で持っている場合も、判定は元の株 AMD の値段） | なし | 2026-11-03 |

- 出来高2倍の大陰線: 実体（始値−終値）が前日までのATR(14)の1.5倍以上、終値がその日の値幅の下25%以内、出来高が前日までの50日平均の2倍以上の日。**押し目（ボリンジャーIII）・急落の底の保有では売りのルール**: 出たら翌日の寄り付きで全部売り、空いた枠で次の合図を買う（2026-10-02 ユーザー決定。`バックテスト結果/やり直し_売りの合図の組み合わせ.md`。乱数3組とも年率が約+2ポイント、最大下落率もやや下がった）。ミネルヴィニ・新高値V2の保有では事実の表示（順張りに足しても良くならなかった）。

- 半分売りの合図（ミネルヴィニ・新高値V2の保有だけ）: 反転のローソク足（かぶせ線・弱気の包み足・宵の明星・流れ星）＋出来高が50日平均の1.5倍以上＋RSI(14)が前日か当日に70以上。買った後に最初に出た日の翌日の寄り付きで半分売り、残り半分は50日線割れ・損切り15%まで持つ（2026-10-01 ユーザー決定。`バックテスト結果/半分だけ売るとオニールの空き枠.md`）。

- かぶせ線（ミネルヴィニ・新高値V2の保有だけ）: 上昇中の陽線の翌日に、前日の高値より上で寄り付き、前日の陽線の真ん中より下（前日の始値より上）で引けた日。翌日の寄り付きで全部売り、空いた枠で次の合図を買う。半分売りより優先する（2026-10-01 ユーザー決定。`バックテスト結果/2倍ETFで売って買い直す.md`。順張りの売買の25%で出て、1回平均+2.0%、年率 21.4%→26.4%）。

## 5-2. 前日（2026-10-22の引け）の【買い（予約）】の確認

約定したかどうかは、ユーザーの `保有銘柄.md`・`売買記録.md` に記録があるかで判断する（価格が届いても、記録がなければ約定していないものとして扱う）。約定していない銘柄は、今日の条件で改めてエントリーを探す（節6）。

| 銘柄 | 種類 | 予約の価格 | 今日の高値／安値 | 価格は届いたか | ユーザーの約定の記録 | 扱い |
|---|---|---|---|---|---|---|
| STX | 予約: ボリンジャー メソッドIII（%bが0.05未満に近い） | 604.60 | 665.55／621.65 | 届かず | なし | 約定の記録なし → 今日の条件では候補なし（新しいエントリーの条件がそろうまで待つ） |
| CSCO | 予約: ボリンジャー メソッドIII（%bが0.05未満に近い） | 102.76 | 111.01／107.50 | 届かず | なし | 約定の記録なし → 今日の条件では候補なし（新しいエントリーの条件がそろうまで待つ） |
| CIEN | 予約: ボリンジャー メソッドIII（%bが0.05未満に近い） | 308.86 | 345.48／318.77 | 届かず | なし | 約定の記録なし → 今日の条件では候補なし（新しいエントリーの条件がそろうまで待つ） |
| TT | 予約: ボリンジャー メソッドIII（%bが0.05未満に近い） | 447.89 | 458.12／448.63 | 届かず | なし | 約定の記録なし → 今日の条件では候補なし（新しいエントリーの条件がそろうまで待つ） |

## 6. 候補（採用したルールの条件が成立＝A。予約（B）は2026-10-25から注文せず、節6-3に参考の表示だけ）

建玉の目安: 同時保有4銘柄まで、1銘柄に資金の25%（資金÷4）、損切りは買値の15%下（ユーザー決定 2026-09-29）。

本日は該当なし（著者への送信は不要）。


## 6-3. 参考: 条件の成立が目前の銘柄（予約は注文しない・著者には送らない）

2026-10-25 ユーザー決定: 予約（逆指値・指値）の注文はやめ、参考の表示だけにする。毎朝のツールと同じ条件・値段で予約の約定をバックテストに入れると、どの形も年率が下がった（後知恵なし 35.7%→30.7〜34.2%、87銘柄 45.6%→34.2〜42.6%。`バックテスト結果/点検_2026-10-25/`）。引けで条件がそろえば、翌朝の節6に買いの候補（A）として出る。各ルールでRSの高い順に2件まで。

| 参考の銘柄 | グループ | 種類 | 終値 | 前日比 | RS | 当てはまった条件 | 条件がそろう目安の価格（注文はしない） |
|---|---|---|---|---|---|---|---|
| KEYS | 半導体製造装置・材料・設計ソフト・計測 | ボリンジャー メソッドIII（%bが0.05未満に近い） | 326.04 | +3.6% | 91 | %b=0.184（0.05まであと少し）、21日II%=+0.009（>0） | 312.93（この値より下で引けると翌朝の買いの候補（A）。目安） |
| MSI | 光・通信・ネットワーク | ミネルヴィニ（ピボットの手前） | 485.62 | +0.8% | 71 | ピボット（ベースの高値、2026-09-01）493.57まで1.6%、ベース38日・調整幅11% | 493.57（この値を上回って引け、ほかの条件もそろうと翌朝の買いの候補（A）。目安） |
| GLW | 光・通信・ネットワーク | ボリンジャー メソッドIII（%bが0.05未満に近い） | 127.74 | +3.3% | 71 | %b=0.177（0.05まであと少し）、21日II%=+0.020（>0） | 120.53（この値より下で引けると翌朝の買いの候補（A）。目安） |


# ニュース（サブエージェントの調査）

# ニュース調査（2026-10-27 JST、米国10/26引け）
出典は headlines.md の見出し（媒体・日付）。WebSearchは見出しで分からない点のみ。

## テーマ全体の下げの原因（S2: SOXが高値から-16.1%）
- 10/26は反発日（S&P500・NASDAQは上げ）。scan.md 4節で前日比-5%以下の監視銘柄はなし、1週-5%以下のグループもなし。ただしS2のため5観点を確認。
- (1) 一番下げた銘柄: 当日下げ銘柄なし。1週で下げたのは製造装置系(-3.4%)・AIプラットフォーム(-3.1%)。見出し(10/26 Infoseek/Yahoo!ファイナンス(ロイター))「ネオクラウド関連株下落、マスク氏が業界の『再編・破綻』予測」。個別銘柄名での検索は、下げた銘柄が特定できないため省略。
- (2) 信用: 10/26 Bloomberg「Morgan Stanley Expects Data-Center ABS Spreads to Widen Further」、10/26 Semafor「AI fears add a 200-basis-point premium to SpaceX's debt」、10/26 IDNFinancials「Blackstone targets high-yield debt as credit spreads widen」、10/26 BeInCrypto「ゴールドマン、AI市場ショック対策のヘッジ取引提示」。信用の警戒は続いている（具体的な数値は見出しのみ、本文未確認）。
- (3) 他業界: 10/26 24/7 Wall St.「BTCがAI投資への疑念で下落」。ソフト・セキュリティは上昇（AIソフト群1週+6.8%）。
- (4) 経済指標・決算: 10/26 Benzinga「トランプ氏がイラン攻撃を否定、先物上昇」、Bloomberg「原油下落、ハイテク決算前に株上昇」。今週はAmazon・Alphabet・Microsoft決算（10/26 IBD）、IntelとSandisk決算（10/26 IBD「Chip Stocks Find Support Before Key Reports From Intel, Sandisk」）。
- (5) 呼び名: 「〇〇ショック」と名付けた報道は見出しになし（検索語「ショック 株」。10/26 ゴールドマンの「AI市場ショック」ヘッジの記事のみ）。半導体は10/26 Motley Fool「Chip Stocks to Buy After Their Worst Day Since June」、Quartz「Morgan Stanley warned chip stocks could fall up to 15% more before bottoming」の見出し。Quartz本文はWebSearchで確認できず（Morgan Stanleyが「SOXが2週間で約14%下落」「半導体より大手クラウドを選好」と述べた別の記事はあるが日付不明）。
- 市場全体: 10/26 Reuters・産経「NY株反発146ドル高、アンソロピック上場申請でAI株に買い」、Yahoo Finance「Equities end higher as Anthropic's IPO filing buoys AI stocks」。S&P500・VIX・ハイイールド債の数値は見出しになく未確認。

## 引け後・時間外の材料
- 10/26 CNBC/Investing.com/Nacionale: Celestica(CLS)が時間外+約10%（AI需要で売上+83%）、Amkor(AMKR)が時間外+約4%（Q3は売上未達、EPS等の詳細は未確認）、JetBlue+15%。
- 監視銘柄の時間外の動きは見出しになし。

## 大きく上げた銘柄（テーマ上げの材料）
- AIソフト群(1週+6.8%): CRWD 10/23「Soars 20%」(IBD)、PANW 10/23「+7.2%、AI security demand」(Stocks Down Under)。NOWはArmis買収($77.5億)の件、10/28に何か発表予定(10/24 TIKR)。
- 10/26の上げの共通材料: Anthropicの上場申請報道（上記）。

## LITE（+8.2%）
- 10/26 24/7 Wall St.: StoneXがカバレッジ開始、目標株価$1,200。Applied Optoelectronics・Coherentも+6%。
- 10/26 TheStreet: 「Nvidia-backed Lumentumが10%上昇」。10/26 GuruFocus: LITEとCOHRが+3%（StoneXの目標株価）。
- 10/22 Investing.com: 下落（理由は見出しのみ）。
- 悪材料: 確認できず。

## COHR（+5.8%）
- 10/26 24/7 Wall St./GuruFocus: StoneXの新規カバレッジ（目標株価）でLITEと連動。
- 悪材料: 確認できず。

## ARM（+6.2%）
- 見出しにARM個別の原因なし。WebSearch（「Arm Holdings stock jumps October 26 2026」）でも10/26付の記事は見つからなかった。原因となるニュースは見つからなかった（同日の半導体・AI全体の反発と同時）。
- 悪材料: 確認できず。

## SNPS（+5.6%）
- 見出しになし。WebSearchでも10/26付の記事なし。原因となるニュースは見つからなかった。
- 悪材料: 確認できず。

## AKAM（+5.3%）
- 見出しになし。WebSearchでも10/26付の記事なし。原因となるニュースは見つからなかった。
- 悪材料: 確認できず。

## TSLA（+5.2%）
- 10/26 IBD: 「Dow Futures: Elon Musk-Led Tesla Leads Market Higher; Amazon, Alphabet, Microsoft Earnings On Deck」。先物でTeslaが市場を牽引。上げの具体的材料は見出しからは不明、WebSearchでも10/26付は見つからなかった。
- 悪材料: 確認できず。

## SNDK（保有・ルール外、10/29決算予定）
- 10/26 IBD: 「Chip Stocks Find Support Before Key Reports From Intel, Sandisk」（決算前の注目）。
- WebSearchでは決算日が2026-11-09と出た（earnings-calendar系、信頼度低）。scan.mdは10/29。公式発表は未確認。
- 直近1週間の個別の悪材料は見つからなかった。
- 悪材料: 確認できず。

## AMD（候補・保有、10/21買い、決算11/3）
- 10/14: -5.7%（$570.82）。CoreWeaveの社債急落でAI投資への懸念（Barron's経由、heygotrade 10/15付）。
- 10/19: +1.8%（$538.05）。TD Cowenが評価を維持（StockStory経由）。52週高値$658.52から-18%。決算は11/3（heygotrade）。
- 10/26付のAMD個別の見出しなし。
- 悪材料: 確認できず（10/14のAI信用不安による下げは上記）。

## 監視外の注目銘柄（CRL, RVTY, COP, TRGP, EOG）
- 見出しにこれらの個別ニュースなし。時間とクエリを絞るため追加検索せず。「原因となるニュースは見つからなかった」（未調査に近い）。
- 参考: 3節ヒートマップで石油・ガス(Refining/E&P/Integrated)が3カ月上位（+20〜40%）。COP・EOG・TRGPはエネルギー、CRL(Diagnostics & Research)・RVTYはヘルスケア系。10/26の原油は下落（Bloomberg）。
- 悪材料: 確認できず（未調査）。

## テーマ全体の大きなニュース（直近1週間）
- Anthropic上場申請（10/26 Reuters他）、ネオクラウドへのマスク氏の発言、データセンターABSスプレッド拡大の見通し（Morgan Stanley）、Intel・Sandisk・Amazon・Alphabet・Microsoft決算の週。
- 輸出規制・設備投資計画の新しい見出しは今回なし。

# ニュースの見出し（プログラムが自動で取得）

- Googleニュース（日付を指定）とYahooファイナンスの見出しを `tools/news_headlines.py` が自動で並べたもの。日付は米国東部時間の配信日（引け後の記事は翌日付）。原因の判断・売買の判断はしていない。
- 調べた銘柄の選び方: 1週の騰落率（中央値）が−5%以下のグループごとに下げの大きい3銘柄＋1日で−7%以下の銘柄（最大12）と、+5%以上のグループごとに上げの大きい3銘柄＋1日で+7%以上の銘柄（最大6）。
- 1週で−5%以下のグループ: なし
- 1週で+5%以上のグループ: AIソフト・セキュリティ・ITサービス（+6.8%）

## 1. 市場全体（2026-10-26）

### 市場全体（英語のまとめ記事）
検索語: `stocks Wall Street close Nasdaq`
- 10/26 Yahoo Finance | Equities end higher as Anthropic's IPO filing buoys AI stocks
- 10/26 24/7 Wall St. | Bitcoin Analysis: BTC Is Falling on Doubts About AI Spending. Is It Trading Like a Tech Stock Now?
- 10/26 Benzinga | Stock Market Today: Dow Jones, S&P 500, Nasdaq 100 Futures Rise After Trump Rules Out Iran Strike — ITUB
- 10/26 Arab News | Closing Bell: Saudi stock market rises 3.4%
- 10/26 TradingView | Stock market outlook today, 26 Oct: Sensex, Nifty prediction - DJIA, S&P, NASDAQ, GIFT Nifty, Kospi, Nikkei cues

### 市場全体（Stock Market Today）
検索語: `"stock market today"`
- 10/26 Bloomberg.com | Stocks Gain Before Tech Earnings as Oil Declines: Markets Wrap
- 10/26 Kiplinger | Stocks Start a Big Week With Solid Gains: Stock Market Today
- 10/26 The Motley Fool | Stock Market Today, Oct. 26: AI Optimism Lifts Nasdaq as Tech Stocks Rebound
- 10/26 Investopedia | 5 Things to Know Before the Stock Market Opens on Monday
- 10/26 Investor's Business Daily | Dow Jones Futures: Elon Musk-Led Tesla Leads Market Higher; Amazon, Alphabet, Microsoft Earnings On Deck

### 市場全体（日本語のまとめ記事）
検索語: `米国株式市場 OR NY株`
- 10/26 Reuters | 米国株式市場＝反発、アンソロピック上場申請でＡＩ株に買い
- 10/26 Yahoo!ファイナンス | 米国株式市場は反発、ハイテクが支援（26日）(フィスコ)
- 10/26 産経ニュース | NY株反発、146ドル高 アンソロピック新規株式公開申請を受けてAI関連株に買い優勢
- 10/26 OANDA証券 | ＮＹ株反発、１４６ドル高

### 半導体・AI株（英語）
検索語: `chip stocks OR semiconductor stocks OR AI stocks`
- 10/26 Investor's Business Daily | Chip Stocks Find Support Before Key Reports From Intel, Sandisk
- 10/26 Quartz | Morgan Stanley warned chip stocks could fall up to 15% more before bottoming
- 10/26 Yahoo Finance | Brazil markets battered after Lula win, AI in focus elsewhere
- 10/26 Investing.com | How crowded are hardware and chip stocks into Q4?
- 10/26 The Motley Fool | Chip Stocks to Buy After Their Worst Day Since June

### 信用（社債・借金）
検索語: `AI debt OR bonds OR credit spreads OR CDS`
- 10/26 Bloomberg.com | Morgan Stanley Expects Data-Center ABS Spreads to Widen Further
- 10/26 Semafor | View / AI fears add a 200-basis-point premium to SpaceX’s debt
- 10/26 IDNFinancials | Blackstone targets high-yield debt as credit spreads widen
- 10/26 The Dark Side Of The Boom | The AI Boom Meets the Bond Market's Breaking Point: Credit Is Sending a Warning
- 10/26 Asset Securitization Report | Portfolio managers expect spike in defaults, wider spreads

### 「〇〇ショック」の呼び名（日本語）
検索語: `ショック 株`
- 10/26 BeInCrypto | ゴールドマン、AI市場ショック対策のヘッジ取引提示
- 10/26 Infoseek | ネオクラウド関連株下落、マスク氏が業界の「再編・破綻」予測｜Infoseekニュース
- 10/26 フランクリン・テンプルトン | 米国株の上昇再開に向けた条件は整うか 金利・決算・中間選挙から探る今後の市場展望
- 10/26 Yahoo!ファイナンス | ネオクラウド関連株下落、マスク氏が業界の「再編・破綻」予測(ロイター)
- 10/26 Yahoo!ファイナンス | 今夜の海外イベント・スケジュール(26日)(株探ニュース)

### 引け後・時間外の動き（英語）
検索語: `"after hours" OR "after the bell" OR "extended trading" stocks`
- 10/26 CNBC | Stocks making the biggest moves after hours: Whirlpool, JetBlue, Celestica & more
- 10/26 Seeking Alpha | Stocks to watch after hours: WELL, PSA, and WHR
- 10/26 Investing.com | Amkor Technology stock rises 4% after hours despite Q3 earnings, revenue miss
- 10/26 Nacionale | Celestica (CLS) stock jumps 10% after hours as AI demand lifts revenue 83%
- 10/26 AskTraders.com | JetBlue Shares Jump 15% After Hours as Q3 Revenue Holds Up

### 引け後・時間外の動き（日本語）
検索語: `時間外 決算 株`
- 10/26 Investing.com - FX | 株式市場 | ファイナンス | 金融ニュース | ニュコア株が時間外取引で下落した理由 執筆
- 10/26 みんかぶ FX/為替 | ベライゾンが決算 携帯電話契約の純増数が５年ぶりの高水準 株価は下落＝米国株個別 -
- 10/26 BigGo ファイナンス | 米ハワイ銀行、第3四半期決算が予想未達 時間外取引で7.5%下落
- 10/26 Investing.com - FX | 株式市場 | ファイナンス | 金融ニュース | アムコー・テクノロジー株が時間外取引で急騰した理由 執筆
- 10/26 Investing.com - FX | 株式市場 | ファイナンス | 金融ニュース | セレスティカ株が時間外取引で急騰した理由とは 執筆

## 3. 大きく上げた銘柄（2026-10-20〜2026-10-26 の見出し）

### CRWD（CrowdStrike Holdings, Inc.、AIソフト・セキュリティ・ITサービス、前日比 +1.7%、1週 +14.8%）

#### Googleニュース
検索語: `CrowdStrike stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 10/20 Yahoo Finance | Another CrowdStrike Stock Bull Signal Now Flashing
- 10/23 Investor's Business Daily | CrowdStrike Soars 20%, Secures A Spot Among 11 Newcomers To Best Stock Lists
- 10/23 Investing.com | Why is CrowdStrike stock surging today?
- 10/25 CNN | CRWD Stock Quote Price and Forecast

#### Yahooファイナンス
検索語: `CRWD`
- 10/26 Insider Monkey | Why Burke Wealth Trimmed CrowdStrike Holdings (CRWD) Despite Its Strong AI Security Outlook
- 10/26 Simply Wall St. | Is CrowdStrike Holdings (CRWD) Expensive As Nvidia Deal Fuels Its AI Security Story?

### PANW（Palo Alto Networks, Inc.、AIソフト・セキュリティ・ITサービス、前日比 +2.6%、1週 +12.5%）

#### Googleニュース
検索語: `Palo Alto Networks stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 10/20 Yahoo Finance | Palo Alto Networks (PANW) Stock Dips While Market Gains: Key Facts
- 10/23 Investing.com | Why is Palo Alto Networks stock surging today?
- 10/23 Stocks Down Under | Why Is Palo Alto Networks (NASDAQ:PANW) Stock Surging 7.2%? AI Security Demand Fuels Rally
- 10/26 TradingKey | Palo Alto Networks Stock Forecast: PANW Jumps 7% Toward $387.09 as the Growth Math Gets Harder

#### Yahooファイナンス
検索語: `PANW`
- 10/26 GlobeNewswire | Neo Appoints Scott Stout as Chief Revenue Officer
- 10/26 Simply Wall St. | Palo Alto Networks (PANW) Jumped, What Is Behind The Fresh Attention?
- 10/26 TIKR | CrowdStrike CEO Competes on Model Pricing: “Ours Is Like Three Cents”

### NOW（ServiceNow, Inc.、AIソフト・セキュリティ・ITサービス、前日比 -0.5%、1週 +8.8%）

#### Googleニュース
検索語: `ServiceNow stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 10/21 Yahoo Finance | Here is What to Know Beyond Why ServiceNow, Inc. (NOW) is a Trending Stock
- 10/22 Yahoo Finance | ServiceNow (NOW) Ascends While Market Falls: Some Facts to Note
- 10/22 Forbes | ServiceNow | NOW Stock Price, Company Overview & News
- 10/23 StockInvest.us | Servicenow Stock Price Forecast. Should You Buy NOW?

#### Yahooファイナンス
検索語: `NOW`
- 10/24 TIKR | ServiceNow Wants to Be No. 1 in Security. Here’s What Its $7.75 Billion Armis Bet Must Show on October 28
- 10/25 Forkast News | The Enterprise Agent Price Nobody Will Show You
- 10/26 GlobeNewswire | Information Technology (IT) Resilience Orchestration Market 2026-2030 | Capitalize on 14.2% CAGR as Microsoft, IBM, Broadcom and ServiceNow Scale AI and Hybrid Cloud

### LITE（Lumentum Holdings Inc.、光・通信・ネットワーク、前日比 +8.2%、1週 -2.0%）

#### Googleニュース
検索語: `Lumentum stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 10/22 Trefis | Should You Buy The Dip In Lumentum Stock?
- 10/22 Investing.com | Why is Lumentum stock sliding today?
- 10/26 TheStreet | Nvidia-backed Lumentum stock surges 10% as Wall Street sees more upside
- 10/26 AOL.com | Why Lumentum Holdings Stock Soared 8.2% Today

#### Yahooファイナンス
検索語: `LITE`
- 10/26 24/7 Wall St. | 3 Catalysts That Could Ignite AXTI Stock on Oct. 29 (And 1 Huge Risk)
- 10/26 24/7 Wall St. | Lumentum Jumps 8% as StoneX Starts Coverage With $1,200 Target; Applied Optoelectronics and Coherent Climb 6%
- 10/26 GuruFocus.com | Lumentum and Coherent Stocks Jump 3% as StoneX Unveils Bold Price Targets


# 補完: 保有の著者の判定（2026-10-28 夜にユーザーの指示で追加）

10/27朝のRoutineでは保有の判定が【未判定】だったため、10/26の引けまでのデータだけで、保有銘柄をボリンジャーに送り直した回答。ニュース調査なし。SNDKはルール外の保有のため著者には送っていない。

## AMD
1. **投資判断**: 【保有継続】（早期手じまいの理由なし）
2. **止める理由の確認**:
   - 本が禁じる形・状況｜なし｜危険な反転形等なし（第14・20章）
   - 避けるべき時期（決算など）｜なし｜決算前の手じまい規定なし（マニュアルに規定なし）
   - 悪材料｜判定不能｜ニュース調査なし
3. **現状パターンと価格**:
   - 保有中: `売りの予約注文: 指値 672.83（現在値比 +26.6%）`
4. **注意点**: 11/3決算前だが本のルールに従い上部バンド等の手じまい条件を継続監視。

