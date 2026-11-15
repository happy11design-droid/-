# テーマ監視 2026-11-13

# 判定のまとめ（ルールの判定と著者の判定を分けて表示）

- **ルールの判定**: 採用した売買ルール（スクリプト）が数値で決めたもの。損切りは買値の15%下の逆指値（日中に届けばその場で売れる）。
- **著者の判定**: ノートブックの著者の回答。買いは注文を止める理由があるときだけ【様子見】、保有はルールより早く手じまう理由があるときだけ【売り】。根拠は下の「著者の回答（全文）」。
- 2つが食い違うときに、どちらに従うかはユーザーが決める。

- **テーマ全体の急落（S2・記録だけ）: あり（S2）**（SOXが直近60取引日の最高値から -23.2%）。S2の日の順張りの候補には「S2なら見送る形」と付ける（売買のルールは変えない。記録してから採用を決める。2026-10-14）

- **特殊な下げ（記録だけ）: あり（特殊な下げ）**（2026-10-16から）（SOXが直近60取引日の最高値から -23.2%、前の1年の大きな上げ・雇用の弱さ・物価の再加速のうち 2つ）。1995年〜では、この形の後にSOXの下げが長引くことが多かった（後知恵を含む）。売買のルールは変えない（2026-11-03）

## 保有銘柄

| 銘柄 | ルール | 損益 | 時間外 | ルールの判定 | ルールの判定の理由 | 著者の判定 |
|---|---|---|---|---|---|---|
| SNDK | ルール外（ユーザーの判断。この日はどのルールの合図もなし） | -35.5% | -2.2% | **売り** | 終値 885.01 が損切り価格 1165.61 以下 | 【未判定】（） |
| AMD | ボリンジャーIII | -2.9% | -2.4% | 保有継続 | 損切り 467.47（終値から -12.5%） | 【保有継続】（ボリンジャー） |

## 候補の判定（並びは上の「買う順番」の表と同じ）

候補なし

- 時間外: 前の取引日の引けから、引け後（米国東部時間16〜20時）の最後の値までの騰落率（Yahoo。±5%以上は太字）。寄り付きの値段は、表の注文の目安（前日の終値で計算）から大きくずれることがある。原因の見出しは「ニュースの見出し」の節。

# 著者の回答（全文）

## 0_テーマの局面_ワインスタイン

1. **テーマ全体の局面**: 【ステージ3】（過去1年の大幅上昇を経て30週移動平均線が横ばい化し、指数が線を下回っているため。第2章、第8章）

2. **グループごとの局面**:
- 半導体｜ステージ3｜30週線横ばい・線の下
- 半導体製造装置・材料・設計ソフト・計測｜ステージ3｜30週線横ばい・線の下
- AIサーバー・ストレージ・メモリ・端末｜ステージ3｜30週線横ばい・線の下
- 光・通信・ネットワーク｜ステージ3｜30週線横ばい・線の下
- データセンターの電力・冷却・部品・受託製造・建設｜ステージ3｜30週線横ばい・線の下
- AIプラットフォーム・クラウド｜ステージ3｜30週線横ばい・線の下
- AIソフト・セキュリティ・ITサービス｜ステージ2｜30週線上昇・線の上

3. **転換の兆し**:
出ている。30週線の水平化（第2章、第8章）と対S&P500のレラティブ・ストレングス悪化（第1章、第4章）が天井形成（ステージ3）の基準に合致する。なお、サポート下抜けによるステージ4入りは価格水準が不明なため判定不能。50日線・急落S2・特殊な下げ等はマニュアルに規定なし。

4. **テーマの外**: なし（ヒートマップのデータが省略されており判定不能のため）

（全体の版が空の応答だったため、1〜2節だけの短い版で送り直した回答。ヒートマップ・急騰急落・ニュースは渡していない）

## 1_ボリンジャー_prompt_1

## AMD
1. **投資判断**: 【保有継続】（早期手じまう理由なし）[1, 2]
2. **止める理由の確認**:
- 本が禁じる形・状況｜なし｜M型トップや指標の弱気乖離なし（第13章、第17章）[2, 3]
- 避けるべき時期（決算など）｜なし｜次回決算2027-02-02（マニュアルに規定なし）[4]
- 悪材料｜なし｜会社固有の悪材料なし（マニュアルに規定なし）[4]
3. **現状パターンと価格**:
- 保有中: `売りの予約注文: なし`
4. **注意点**: スクリプトの既存手じまいルール（上部バンド606.77指値・損切り467.47）を維持してください[2, 5]。

（AMDの質問文が8,000文字を超えたため、数値データのうち 2026-10-21 より前の大きな値動きの行と決算の中身の表を外し、テーマ全体のニュースを先頭113文字までに縮めて送った回答。AMDのニュースは全文を渡した）

# スキャン（数値と事実）


- 監視銘柄 87（判定できたのは 87）。
- この一覧は数値と事実だけ。売買の判断は著者のノートブックが行う。

## 1. テーマ（グループ）の強さ

| グループ | 銘柄数 | 1週 | 1カ月 | 3カ月 | 3カ月の順位 | 50日線より上の銘柄の割合 | グループ指数の30週線の局面（線との乖離、4週前からの線の傾き） |
|---|---|---|---|---|---|---|---|
| 半導体 | 16 | +9.5% | -3.6% | -11.4% | 3位 | 38% | 横ばい（-9.1%、+4.6%） |
| 半導体製造装置・材料・設計ソフト・計測 | 9 | +9.4% | -12.7% | -20.5% | 5位 | 22% | 横ばい（-14.2%、+1.0%） |
| AIサーバー・ストレージ・メモリ・端末 | 9 | +6.0% | -17.6% | -28.1% | 6位 | 11% | 横ばい（-10.8%、+6.2%） |
| 光・通信・ネットワーク | 9 | +7.7% | -12.9% | -30.6% | 7位 | 22% | 横ばい（-14.9%、+0.9%） |
| データセンターの電力・冷却・部品・受託製造・建設 | 19 | +4.5% | -5.6% | -11.9% | 4位 | 26% | 横ばい（-8.5%、+0.3%） |
| AIプラットフォーム・クラウド | 11 | +4.6% | -6.8% | +2.0% | 2位 | 45% | 横ばい（-3.9%、+1.4%） |
| AIソフト・セキュリティ・ITサービス | 14 | +2.0% | -7.3% | +2.3% | 1位 | 36% | 上昇（+6.6%、+4.8%） |

## 2. テーマ全体の状態と早めの警告

- 市場全体の30週線による局面: S&P500指数 **上昇**／NASDAQ100指数 **横ばい**（急落の底で買うルールは、過去の検証で下落相場で特に強く、横ばいの相場では負けていた）
- **2倍ETFを使う局面（案1、2026-10-13 採用）: S&P500の20週線（100日線）で 横ばい** → 新しく買う銘柄は、2倍ETFのある銘柄も元の株で買う（保有中のETFはそのまま）（SPY 754.37、100日線 759.18、20日前の線 755.84。上昇＝線より上かつ線が上向き）
- **テーマ全体の急落（S2、記録だけ。売買のルールは変えない）: あり（S2）**（SOX 10146.32、直近60取引日の最高値 13217.82 から -23.2%。S2＝最高値から−10%以上）。S2のときに「順張りの新しい買いだけ止める」形を記録で比べる（2026-10-14 ユーザー決定。バックテストでは年率は上がったが2つの期間ではどちらも少し下回ったため、記録してから採用を決める。`バックテスト結果/テーマ全体の急落を検知して手じまう・買いを止める.md`）
- **グループごとの悪いニュースの流れ（記録だけ。売買のルールは変えない。2026-11-02〜2026-11-13）**: 会社の名前と悪い言葉（格下げ・目標株価の引き下げ・見通しの引き下げ・予想未達・急落・信用・訴訟・輸出規制など）の両方がある見出しの数（Googleニュース、`tools/news_headlines.py`）。10取引日の1銘柄あたりが一番多いグループに印。2026年7〜11月の確かめでは、印のグループの合図は10月は成績が悪かった（1回平均 −10.6%、ほか −5.6%）が、7〜9月は逆に良かった（+11.6%、ほか +6.7%）（`バックテスト結果/実際の運用の期間の確認_2026-10-23/グループの悪いニュースの流れ.md`。2026-11-04）

| グループ | 悪いニュース 直近5取引日 | その前の5取引日 | 10取引日の1銘柄あたり | 良いニュース 10取引日（1銘柄あたり） | 印 |
|---|---|---|---|---|---|
| 半導体（16） | 58件 | 6件 | 4.0 | 17件（1.1） | **悪いニュースが続いている** |
| 光・通信・ネットワーク（9） | 5件 | 15件 | 2.2 | 9件（1.0） |  |
| AIサーバー・ストレージ・メモリ・端末（9） | 6件 | 3件 | 1.0 | 21件（2.3） | **良いニュースが多い** |
| AIプラットフォーム・クラウド（11） | 6件 | 4件 | 0.9 | 8件（0.7） |  |
| データセンターの電力・冷却・部品・受託製造・建設（19） | 0件 | 3件 | 0.2 | 13件（0.7） |  |
| 半導体製造装置・材料・設計ソフト・計測（9） | 0件 | 1件 | 0.1 | 5件（0.6） |  |
| AIソフト・セキュリティ・ITサービス（14） | 0件 | 1件 | 0.1 | 13件（0.9） |  |

印のグループ（半導体）の最近の見出し: 2026-11-14 HSBC Just Downgraded Nvidia and Cut Its Target to $170（24/7 Wall St.）／2026-11-13 Analysts Downgrade Nvidia and Tesla as Apple’s Premium Gets a Defense（www.tokenpost.com）／2026-11-13 Broadcom Shares Fall After Rothschild & Co Redburn Downgrade（marketscreener.com）

良いニュースが多いグループ（AIサーバー・ストレージ・メモリ・端末）の最近の見出し: 2026-11-14 Analysts Just Made A Massive Upgrade To Their Super Micro Computer, Inc. (NASDAQ:SMCI) Forecasts（Simply Wall St）／2026-11-13 3 reasons to upgrade to the ceramic Apple Watch 12, and 2 reasons to skip it（Tom's Guide）

- **特殊な下げ（記録だけ。売買のルールは変えない）: あり（特殊な下げ）**（2026-10-16から）。SOX は直近60取引日の最高値から -23.2%（−15%以下が条件）、●A 前の1年の上げ +110.6%（+80%以上）、・B 雇用の伸び 137千人/月（2026-10まで。10万人未満）、●C 物価 4.0%（2026-09。3か月前 3.7%。3.5%以上で再加速）＝2つ（2つ以上が条件）。1995年〜でSOXが−15%以下かつ条件2つ以上の日は、120日後にSOXが下だったのが69%・250日後が70%（中央値 −33%）、AI以外の8業種の平均は250日後 −7%。ただし条件は過去を見て選んだもの（条件が2つ以上の局面は約5回）で、2026年7〜9月にこの間テーマを買わないと、その後の戻りを逃して2026年の成績は下がった（`バックテスト結果/実際の運用の期間の確認_2026-10-23/特殊な下げと過去の似た下げ.md`。2026-11-03）
- テーマ指数（監視銘柄の等金額平均）の30週線による局面: **横ばい**（上昇＝線より上かつ上向き、下落＝線より下かつ下向き、それ以外＝横ばい。ワインスタインのステージの近似）
- テーマ指数と50日線: 50日線より下（乖離 -8.2%）
- S&P500に対する相対的な強さ: 50日平均より下（S&P500より弱い）
- 監視銘柄のうち50日線より上の割合: 30%
- 警告（割合が40%未満かつテーマ指数が50日線より下）: **出ている**
- 参考（バックテスト）: 30週線の「下落」は高値から10〜33%下げた後に出る遅い判定。50日線・割合・相対的な強さは高値から2〜8%で出るが、誤報が年15回以上ある。警告中に新しい買いを止めると、押し目買い（ボリンジャーIII）の成績は大きく下がった（`バックテスト結果/テーマ監視銘柄・直近3年.md` 11・12節）。

## 3. ヒートマップ（Finviz、全米の業種別の騰落率）

3カ月の騰落率の上位15業種（テーマの外で強くなっている業種の確認用）:

| 順位 | 業種 | 1週 | 1カ月 | 3カ月 | 6カ月 | 1年 |
|---|---|---|---|---|---|---|
| 1 | Advertising Agencies | +5.0% | +33.2% | +22.4% | -8.8% | -23.4% |
| 2 | Health Information Services | -0.5% | +2.3% | +21.6% | +59.5% | +9.2% |
| 3 | Medical Distribution | +4.5% | +8.6% | +20.9% | +41.9% | +21.7% |
| 4 | Paper & Paper Products | -0.2% | +14.9% | +19.1% | +15.6% | +2.3% |
| 5 | Insurance - Diversified | +3.8% | +11.9% | +17.4% | +21.4% | +17.3% |
| 6 | Consumer Electronics | +4.0% | +4.3% | +16.4% | +18.6% | +27.7% |
| 7 | Diagnostics & Research | +0.6% | +0.2% | +14.9% | +52.9% | +19.9% |
| 8 | Lodging | +1.1% | +9.3% | +14.9% | +17.3% | +34.9% |
| 9 | Consulting Services | +1.3% | +13.9% | +14.3% | +25.8% | -1.9% |
| 10 | Household & Personal Products | +2.1% | +6.8% | +14.1% | +19.9% | +13.1% |
| 11 | Real Estate - Diversified | +2.7% | +10.6% | +13.4% | +17.5% | +8.0% |
| 12 | Financial Data & Stock Exchanges | +2.0% | +8.8% | +13.3% | +12.7% | +4.1% |
| 13 | Drug Manufacturers - General | +2.7% | +9.3% | +13.2% | +27.0% | +30.1% |
| 14 | Discount Stores | +2.9% | +9.5% | +13.0% | +2.5% | +24.8% |
| 15 | Medical Care Facilities | +0.4% | +5.1% | +12.9% | +20.6% | +19.1% |

テーマの業種の順位（3カ月、全144業種中）: Semiconductors 132位、Semiconductor Equipment & Materials 142位、Computer Hardware 144位、Communication Equipment 130位、Electronic Components 134位、Software - Infrastructure 53位、Software - Application 55位、Internet Content & Information 102位

## 4. 急騰・急落した銘柄（前日比±5%以上、または出来高が50日平均の2倍以上）

原因のニュースをサブエージェントが調べ、候補・保有銘柄の判定材料として著者に渡す。急騰・急落そのものは売買の合図にしない（後知恵のないS&P500全体のバックテストでは、急騰の翌日に買うルールは年率7%、急落の翌日に買うルールは年率9〜10%で、採用した3つのルールより優れていなかった）。

| 銘柄 | グループ | 前日比 | 出来高（50日平均の倍） | 終値 | 50日線 | RS | 局面 |
|---|---|---|---|---|---|---|---|
| NBIS | AIプラットフォーム・クラウド | -9.9% | 2.3倍 | 115.88 | 下 | 4 | 下げ |
| AMD | 半導体 | -8.8% | 1.9倍 | 534.06 | 下 | 98 | 下げ |
| DELL | AIサーバー・ストレージ・メモリ・端末 | -7.2% | 1.2倍 | 344.53 | 下 | 99 | 下げ |
| CSCO | 光・通信・ネットワーク | -6.2% | 1.6倍 | 95.64 | 下 | 37 | 下げ |
| CRWV | AIプラットフォーム・クラウド | -6.1% | 1.6倍 | 53.13 | 下 | 0 | 下落相場 |
| COHR | 光・通信・ネットワーク | -6.0% | 1.2倍 | 218.15 | 下 | 9 | 下落相場 |
| SNDK | AIサーバー・ストレージ・メモリ・端末 | -5.6% | 1.2倍 | 885.01 | 下 | 83 | 下げ |
| TER | 半導体製造装置・材料・設計ソフト・計測 | -5.4% | 0.9倍 | 249.55 | 下 | 7 | 下落相場 |
| NVDA | 半導体 | -2.0% | 2.5倍 | 162.85 | 下 | 5 | 下げ |

- 局面（判定式はClaudeが置いたもの）: **上昇相場**＝終値 > 50日線 > 200日線、50日線が20取引日前より2%以上高い、ADX(14) ≧ 20／**下落相場**＝終値 < 50日線 < 200日線、50日線が20取引日前より2%以上低い、ADX(14) ≧ 20／**上げ**＝それ以外で終値が50日線より上、かつ50日線が10取引日前より上か20日線が5取引日前より上／**下げ**＝それ以外で終値が50日線より下、かつ50日線が10取引日前より下か20日線が5取引日前より下（急な下げの初めは50日線がまだ上向きのため20日線でも見る）／**レンジ**＝どれにも当たらない（2026-11-05 から5つ。それまでは上昇相場とレンジの2つだけで、下げている銘柄もレンジと出ていた）。

## 4-2. 監視外の注目銘柄（S&P500・NASDAQ100のうち監視銘柄に入っていない銘柄）

条件: 流動性（株価5ドル以上・50日平均出来高25万株以上）があり、(a) 前日比+8%以上かつ出来高が50日平均の2倍以上、または (b) 終値が直前1年の最高値（終値）を上回り、RS≧90。RSの高い順に5銘柄（ニュースを調べる）。監視銘柄に入れるかはユーザーが決める。

| 銘柄 | 種類 | 前日比 | 出来高（50日平均の倍） | RS | 終値 |
|---|---|---|---|---|---|
| HUM | 1年の高値更新 | +1.4% | 1.0倍 | 98 | 450.00 |
| WST | 1年の高値更新 | +1.2% | 0.7倍 | 96 | 416.42 |
| LLY | 1年の高値更新 | +1.3% | 0.8倍 | 94 | 1443.50 |
| BDX | 1年の高値更新 | +1.1% | 1.0倍 | 94 | 218.03 |
| CPAY | 1年の高値更新 | +1.4% | 0.6倍 | 94 | 462.22 |

- ほかに5銘柄: ADP（1年の高値更新、RS 93）、MCK（1年の高値更新、RS 92）、CAH（1年の高値更新、RS 91）、CBOE（1年の高値更新、RS 90）、ABBV（1年の高値更新、RS 90）

## 5. 保有銘柄の手じまい条件（`新分析ツール/保有銘柄.md`）

| 銘柄 | ルール | 買った日 | 買値 | 終値 | 損益 | 損切り価格（買値の15%下、逆指値） | ルールの手じまい条件 | 出来高2倍の大陰線（買った後の直近5日） | 次回決算予定日 |
|---|---|---|---|---|---|---|---|---|---|
| SNDK | ルール外（ユーザーの判断。この日はどのルールの合図もなし） | 2026-10-21 | 1371.30 | 885.01 | -35.5% | 1165.61 | **損切り価格を下回った** ルールが不明（保有銘柄.md の「ルール」を確認） | なし | 2026-10-29 |
| AMD | ボリンジャーIII | 2026-10-21 | 549.97 | 534.06 | -2.9% | 467.47 | **出来高2倍の大陰線が 2026-11-05 に出た**（まだ持っていれば、次の寄り付きで全部売る） 売りの指値: 上部バンド 606.77（今夜この値に置き直す。届いた日に売れる）（2倍ETF AMUU で持っている場合も、判定は元の株 AMD の値段） | なし | 2027-02-02 |

- 出来高2倍の大陰線: 実体（始値−終値）が前日までのATR(14)の1.5倍以上、終値がその日の値幅の下25%以内、出来高が前日までの50日平均の2倍以上の日。**押し目（ボリンジャーIII）・急落の底の保有では売りのルール**: 出たら翌日の寄り付きで全部売り、空いた枠で次の合図を買う（2026-10-02 ユーザー決定。`バックテスト結果/やり直し_売りの合図の組み合わせ.md`。乱数3組とも年率が約+2ポイント、最大下落率もやや下がった）。ミネルヴィニ・新高値V2の保有では事実の表示（順張りに足しても良くならなかった）。

- 半分売りの合図（ミネルヴィニ・新高値V2の保有だけ）: 反転のローソク足（かぶせ線・弱気の包み足・宵の明星・流れ星）＋出来高が50日平均の1.5倍以上＋RSI(14)が前日か当日に70以上。買った後に最初に出た日の翌日の寄り付きで半分売り、残り半分は50日線割れ・損切り15%まで持つ（2026-10-01 ユーザー決定。`バックテスト結果/半分だけ売るとオニールの空き枠.md`）。

- かぶせ線（ミネルヴィニ・新高値V2の保有だけ）: 上昇中の陽線の翌日に、前日の高値より上で寄り付き、前日の陽線の真ん中より下（前日の始値より上）で引けた日。翌日の寄り付きで全部売り、空いた枠で次の合図を買う。半分売りより優先する（2026-10-01 ユーザー決定。`バックテスト結果/2倍ETFで売って買い直す.md`。順張りの売買の25%で出て、1回平均+2.0%、年率 21.4%→26.4%）。

## 5-2. 前日（2026-11-12の引け）の【買い（予約）】の確認

前日の【買い（予約）】はなし。

## 6. 候補（採用したルールの条件が成立＝A。予約（B）は2026-10-25から注文せず、節6-3に参考の表示だけ）

建玉の目安: 同時保有4銘柄まで、1銘柄に資金の25%（資金÷4）、損切りは買値の15%下（ユーザー決定 2026-09-29）。

本日は該当なし（著者への送信は不要）。


## 6-2. 参考: ワインスタイン10週の合図（売買には使わない・著者には送らない）

後知恵なしのバックテストで、今の4つのルールに加えると年率が下がった（27.1%→22.9〜26.3%。`バックテスト結果/ワインスタイン10週を加えるか.md`）ため、2026-10-04 から参考の表示だけにした（ユーザー決定）。強い銘柄が10週の高値に近づいている、という事実として見る。

| 参考の銘柄 | グループ | パターン | 種類 | 終値 | 前日比 | RS | 当てはまった条件 |
|---|---|---|---|---|---|---|---|
（Bは監視銘柄を先に、RSの高い順に10件まで。ほかに11件）

| CDW | AIソフト・セキュリティ・ITサービス | B | 予約: ワインスタイン（10週の高値の手前） | 171.65 | -0.7% | 95 | 直前10週の高値172.47まで0.5%、10週線が上向き |
| SWKS | 半導体 | B | 予約: ワインスタイン（10週の高値の手前） | 89.94 | -0.1% | 95 | 直前10週の高値92.80まで3.2%、10週線が上向き |
| TXN | 半導体 | B | 予約: ワインスタイン（10週の高値の手前） | 303.60 | -2.8% | 91 | 直前10週の高値317.20まで4.5%、10週線が上向き |
| MSI | 光・通信・ネットワーク | B | 予約: ワインスタイン（10週の高値の手前） | 531.20 | +0.2% | 85 | 直前10週の高値548.29まで3.2%、10週線が上向き |
| EMR | データセンターの電力・冷却・部品・受託製造・建設 | B | 予約: ワインスタイン（10週の高値の手前） | 166.38 | +0.0% | 71 | 直前10週の高値171.39まで3.0%、10週線が上向き |
| NXPI | 半導体 | B | 予約: ワインスタイン（10週の高値の手前） | 265.09 | -0.8% | 64 | 直前10週の高値272.08まで2.6%、10週線が上向き |
| AMZN | AIプラットフォーム・クラウド | B | 予約: ワインスタイン（10週の高値の手前） | 266.66 | -0.3% | 58 | 直前10週の高値273.23まで2.5%、10週線が上向き |
| EQIX | データセンターの電力・冷却・部品・受託製造・建設 | B | 予約: ワインスタイン（10週の高値の手前） | 1053.79 | -1.8% | 53 | 直前10週の高値1068.33まで1.4%、10週線が上向き |
| IBM | AIプラットフォーム・クラウド | B | 予約: ワインスタイン（10週の高値の手前） | 247.13 | +1.0% | 37 | 直前10週の高値258.09まで4.4%、10週線が上向き |
| FDS | テーマの外（Financial Data & Stock Exchanges） | B | 予約: ワインスタイン（10週の高値の手前） | 332.69 | +0.3% | 96 | 直前10週の高値348.00まで4.6%、10週線が上向き |


# ニュース（サブエージェントの調査）

# ニュース調査（2026-11-13 の引け時点）

「見出し」＝headlines.md／scan.md、「検索」＝WebSearchで確認。

## テーマ全体の下げの原因
- きっかけ: エヌビディアのCEO交代。11/10 取締役会がフアン氏の不倫（相手の1人は中国のスパイの疑い）の調査を開始 → 11/11 引け後にWSJが「解任を準備」と報道、NVDA 時間外 −8.2%（検索: stockanalysis.com 11/11）→ 11/12 フアン氏が即日辞任、CFOのクレス氏が暫定CEO。理由の記載なし（検索: NVIDIAの8-K 11/12）。
- 広がった先: 11/13 フアン氏不在でAI関連を見直す売りが AMD など半導体に（見出し: MarketWatch・Forbes 11/13）。HSBCがNVDA、Rothschild RedburnがAVGOを格下げ（24/7 Wall St. 11/14、marketscreener 11/13）。
- 信用: CoreWeave が「40億ドルの融資の交渉」の報道で −6%（Motley Fool 11/13）。「債券市場がAI関連に背を向け、半導体株は2日で6,500億ドル超を失った」（Yahoo Finance 11/14）。大手4社の借入への懸念（TradingKey 11/14）。融資の相手・利回り・CDSの数字は取得不可（検索語: CoreWeave $4 billion loan talks／bond market turned on AI trade $650 billion）。
- 別の業界: AIサーバーは Super Micro の司法省の密輸調査の報道が2日続き DELL −8%、HPE −4%（24/7 Wall St. 11/13）。ネオクラウドは Nebius の決算（下記）。
- 市場全体: S&P500・ナスダック続落、ダウ −189ドル（Reuters・産経 11/13）。利上げ警戒感（フィスコ 11/13）、10月PPIは予想を下回った（株探 11/13）。週では指数は上昇（IBD 11/13）。VIX・ハイイールド債の数字は取得不可。
- 呼び名: 「Nvidiaショック」（Investing.com 日本語 11/13）。
- 背景: 11/5 に中間選挙の民主党勝利でAI規制の懸念から半導体が急落（検索: TIKR 11/5）。

## 1週の上げのきっかけ（4グループが1週 +5%以上）
- 11/9・11/11 に半導体・装置が反発（Globe and Mail 11/9、24/7 Wall St. 11/11）。11/11 以降はNVDAからAMD・AVGOへ資金が移った（Benzinga 11/11）。AMDはOppenheimerの格上げ（TIKR 11/14）、AMATは決算で「需要は供給よりずっと多い」（24/7 Wall St. 11/13）。

## 引け後・時間外の材料
- ±5%以上動いた監視銘柄はなし。
- AMD: 時間外 −2.4%。原因の見出しは見つからなかった。
- SNDK: 時間外 −2.2%。原因の見出しは見つからなかった。
- 参考: 全米の航空便の一時停止が時間外の重し（BigGo Finance 11/13）。Modine がサムスンとの交渉の報道で +29%（Gotrade 11/13）。

## AMD（保有、−8.8%）
- 11/13 フアン氏退任後のAI株の見直しで半導体と一緒に下落（MarketWatch 11/13）。記事の本文は取得不可。
- 11/11 は上昇（Motley Fool 11/11）。Oppenheimerの格上げで1週 +19%（TIKR 11/14）。
- 11/3 発表の7〜9月期は売上134億ドル（+45%）。11/5 は中間選挙後に急落（検索: Motley Fool 11/5）。
- 悪材料: 確認できず（会社固有のものはなし。下げは業界全体）

## SNDK（保有、−5.6%）
- 11/13 終値が900ドル割れ（Motley Fool 11/13）。当日の会社固有の原因となるニュースは見つからなかった。
- 11/7 株式分割を前に下落（Benzinga 11/7）、11/10 続落（Motley Fool 11/10）。1対8の分割は11/19（検索: 二次情報）。
- 11/2 equal-weight へ格下げ、11/5 は −22%（検索: heygotrade 11/6）。
- 次回決算日の公式発表: 取得不可。
- 悪材料: あり（11/2 の格下げ、メモリ価格の持続性への懸念。11/13 の新しいものは確認できず）

## NVDA（−2.0%、出来高2.5倍）
- CEO辞任（8-K 11/12）。HSBCが格下げ、目標株価170ドル（24/7 Wall St. 11/14）。決算は11/17 引け後（8-K）。

## NBIS（−9.9%）
- 11/12 決算後 −16%。設備投資の増加と弱い見通し、CEOが売上の遅れを警告（CNBC・Barron's 11/12）。11/13 続落（Yahoo 11/13）、内部者が約104万ドル売却（MT Newswires 11/13）。

## DELL（−7.2%）
- Super Micro の密輸調査の報道でAIサーバー株が売られた（24/7 Wall St. 11/13）。会社固有の発表は見つからなかった。

## CRWV（−6.1%）
- AIクラウドの売りと40億ドルの融資交渉の報道（Motley Fool 11/13）。中身は取得不可。

## CSCO（−6.2%）／COHR（−6.0%）
- どちらも原因となるニュースは見つからなかった（検索語: Cisco stock falls November 13 2026 earnings／Cisco fiscal first quarter 2027 results／Coherent COHR stock drops November 13 2026）。CSCOの決算発表の有無は取得不可。

## TER（−5.4%）
- 11/11 Jefferiesの買い推奨で急騰（Barron's 11/11）した後の下げ。11/12 ARKが残りを全部売却（Yahoo 11/12）。11/13 固有の原因は見つからなかった。

## 監視外の注目（HUM・WST・LLY・BDX・CPAY、1年の高値更新）
- 5銘柄とも原因となるニュースは見つからなかった（取得不可）。HUM＝医療保険、LLY＝製薬、WST・BDX＝医療機器・資材、CPAY＝法人決済。高値更新10銘柄のうち8つがヘルスケア（scan.md 4-2）。

## テーマ全体のニュース（直近1週）
- エヌビディア決算（11/17 引け後）と Anthropic のIPOが今週の焦点（株探 11/14）。
- AMAT決算は予想を上回ったが反応は鈍い（Barron's 11/13）。
- 輸出規制の新しい発表は確認できず。

# ニュースの見出し（プログラムが自動で取得）

- Googleニュース（日付を指定）とYahooファイナンスの見出しを `tools/news_headlines.py` が自動で並べたもの。日付は米国東部時間の配信日（引け後の記事は翌日付）。原因の判断・売買の判断はしていない。
- 調べた銘柄の選び方: ①保有 ②今日の候補 ③時間外に±5%以上動いた監視銘柄 は全部、④引けまでに大きく動いた銘柄（1週で±5%のグループの上位3・1日で±7%）は合計12銘柄まで。
- 1週で−5%以下のグループ: なし
- 1週で+5%以上のグループ: 半導体（+9.5%）、半導体製造装置・材料・設計ソフト・計測（+9.4%）、光・通信・ネットワーク（+7.7%）、AIサーバー・ストレージ・メモリ・端末（+6.0%）

## 0. 時間外（引け後）の値動き（2026-11-13 の引けから、Yahoo。±3%以上の監視銘柄と、保有・候補は全部）

| 銘柄 | 区分 | 引け | 時間外 | 騰落率 |
|---|---|---|---|---|
| ALAB | 監視 | 221.79 | 215.05（19:58 ET） | -3.0% |
| AMD | 保有 | 534.09 | 521.20（19:59 ET） | -2.4% |
| SNDK | 保有 | 884.50 | 865.23（19:59 ET） | -2.2% |

## 1. 市場全体（2026-11-13）

### 市場全体（英語のまとめ記事）
検索語: `stocks Wall Street close Nasdaq`
- 11/13 Reuters | S&P 500, Nasdaq end lower as Nvidia uncertainty weighs on tech shares
- 11/13 Nasdaq | Bell Ringing Ceremony
- 11/13 Investor's Business Daily | Stock Market Today: Stock Market News And Analysis
- 11/13 Benzinga | Stock Market Today: Dow Jones, S&P 500, Nasdaq 100 Futures Rise as Nvidia CEO Exit Remains in Focus— CSC
- 11/13 Eurasia Business News | Stock Market Today, November 13, 2026: Tech Stocks Fall as Nvidia Earnings and Anthropic IPO Loom

### 市場全体（Stock Market Today）
検索語: `"stock market today"`
- 11/13 The Motley Fool | Stock Market Today, Nov. 13: CoreWeave Falls Over 6% on AI-Cloud Selling and Reported $4 Billion Loan Talks
- 11/13 Investor's Business Daily | Stock Market Today: Indexes Trim Losses, Manage To Score Weekly Gains Despite Strong Volatility
- 11/13 Yahoo Finance | Stock Market: Will S&P 500 Open Up or Down Today?

### 市場全体（日本語のまとめ記事）
検索語: `米国株式市場 OR NY株`
- 11/13 野村證券 | エヌビディア、好決算でも時間外で株価下落 米国株式市場への影響と今後の注目点 野村證券・村山誠
- 11/13 Reuters | 米国株式市場＝Ｓ＆Ｐ・ナスダック続落、エヌビディア巡る不透明感が重し | ロイター
- 11/13 産経ニュース | NY株反落、189ドル安 エヌビディア大幅下落も影響は限定的
- 11/13 Yahoo!ファイナンス | 米国株式市場はまちまち、利上げ警戒感やハイテクが重し／海外市場動向(フィスコ)
- 11/14 株探 | 米国株式市場見通し：エヌビディア決算、アンソロピックIPOなどAI関連の動向焦点

### 半導体・AI株（英語）
検索語: `chip stocks OR semiconductor stocks OR AI stocks`
- 11/13 Forbes | AI Stocks Close Lower Friday As Markets Absorb Jensen Huang’s Exit From Nvidia
- 11/13 MarketWatch | AMD and other chip stocks slide as Wall Street rethinks the AI trade without Jensen Huang
- 11/13 Foundation for Defense of Democracies | Nvidia fallout prompts rotation in chip stocks
- 11/14 Yahoo Finance | 3 AI Chip Stocks Retail Investors May Be Missing Beyond Nvidia
- 11/14 Yahoo Finance | The bond market just turned on the AI trade — and chip stocks lost more than $650 billion in two days: Chart of the Day

### 信用（社債・借金）
検索語: `AI debt OR bonds OR credit spreads OR CDS`
- 11/13 24/7 Wall St. | Billionaire Jeffrey Gundlach Calls the Stock Market a 'Hollow Tree' as Weakness Spreads Beyond Big Tech
- 11/13 TradingView | Macro Bearish Divergence & "The Big Reset" Roadmap for TVC:SPX by osamaadi
- 11/14 TradingKey | AI Debt Risks Mount: Why Borrowing by Meta, Alphabet, Microsoft and Oracle Worries Investors
- 11/14 The Dark Side Of The Boom | After a Week of Market Mayhem: Six Ideas for a Run Into Year-End
- 11/14 Seeking Alpha | AI Jitters Creating Risks, But Also Opportunities In High Yield Bonds

### 「〇〇ショック」の呼び名（日本語）
検索語: `ショック 株`
- 11/13 トウシル | 日経平均暴落でも年初来高値も！ショック安に勝つ株、三つのポイント（茂木春輝）
- 11/13 みんかぶ（マガジン） | 日本株を襲った「ブルーウェーブ・ショック」…好決算でも売られる理由と、買い直すための条件
- 11/13 Investing.com - FX | 株式市場 | ファイナンス | 金融ニュース | Investing.comの今週の注目株：NvidiaショックがAI関連銘柄を揺るがす 執筆 Investing.com
- 11/13 野村證券 | 金利上昇懸念で不動産株が急落 行き過ぎ感も、銀行株には追い風期待 野村證券ストラテジストが解説
- 11/14 Unisba Media | 【アンソロピックショック！？】SaaS関連株BEST5【SaaSについても解説】 What Boxing Is On Tonight (9Nxx5Bgggs)

### 引け後・時間外の動き（英語）
検索語: `"after hours" OR "after the bell" OR "extended trading" stocks`
- 11/13 ChartMill | After-Hours Stock Movers: Top Gainers and Losers Following Today's US Close
- 11/13 Benzinga | Vertiv Shares Rise 3.36% After Hours - SOFTBANK GRP UNSP/ADR by Softbank Group Corp (OTC:SFTBY), JPMorgan
- 11/13 BigGo Finance | Nationwide Flight Grounding Briefly Halts U.S. Air Travel, Weighs on After-Hours Trading; Airline Stocks Slip, Cybersecurity Shares Buck the Trend
- 11/13 bloomingbit | U.S. Nationwide Flight Ground Stop Jolts After-Hours Trading
- 11/13 Gotrade | Modine Stock Jumps 29% After Hours on Samsung Talks Report
- 11/13 Benzinga | Candel Therapeutics Shares Tumble 39% After-Hours: Here's Why
- 11/13 TipRanks | Why Super Micro Stock Rebounded After Hours Following an 11% Drop amid DOJ Probe Reports
- 11/14 Yahoo Finance | Duffy Says an L3Harris Crew Was Working on the FAA Network When Flights Stopped. Its Stock Fell 4% After Hours

### 引け後・時間外の動き（日本語）
検索語: `時間外 決算 株`
- 11/13 Moomoo | 11月チャレンジ 16日目：第3四半期決算への反応とネビウス・グループ（NBIS）のリスクポジション 📊🛡️🚀
- 11/13 Investing.com - FX | 株式市場 | ファイナンス | 金融ニュース | Cineverse株が16%急騰、第2四半期決算が予想を上回る
- 11/13 株探 | 米国株時間外取引はPPIの伸びが予想を下回ったことで買いが優勢＝米国株
- 11/13 BigGo ファイナンス | 米株先物、10月PPI発表を前に小幅高 エヌビディアはフアン氏退任後に反発
- 11/13 Moomoo | エヌビディア（NVDA）の決算後反発を狙う
- 11/13 Moomoo | ザ・キャピタル・ブレイクダウン：2026年11月13日（金）
- 11/14 ｄメニューニュース | 国内株式市場見通し：エヌビディア決算やアンソロピックIPO受けてのAI関連株の動向が焦点に

### 買収・合併（英語）
検索語: `acquisition OR acquire OR merger OR takeover chip OR semiconductor OR AI OR optical`
- 11/13 Ars Technica | OpenAI board member worries an AI "takeover" of society could be months away
- 11/13 Yahoo Finance | Wolters Kluwer to acquire AI-powered clinical decision support platform AgileMD
- 11/13 Fast Company | OpenAI board member makes a terrifying prediction: You will probably die from an AI accident
- 11/13 Quartz | OpenAI's Paul Christiano warned AI takeover could come within months
- 11/13 The Motley Fool | SpaceX’s Big Day: A Historic Starship Launch, a Tesla Merger Under Scrutiny, and a $74 Billion AI Bet
- 11/13 Dealroom | AI security startup Tensor to take 90% of Nasdaq-listed RAIN in reverse merger
- 11/14 CASRAI | IBM announces AuthMind acquisition for AI agent identity security
- 11/14 Car Dealership Guy News | Hertz to close all Hertz Car Sales locations + Dealer panel notes role of AI in used vehicle acquisition

## 2. 保有・候補・時間外で大きく動いた銘柄（2026-11-07〜2026-11-13 の見出し）

### SNDK（Sandisk Corporation、保有、AIサーバー・ストレージ・メモリ・端末、前日比 -5.6%、1週 +6.0%、時間外 -2.2%）

#### Googleニュース
検索語: `Sandisk stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/7 Benzinga | SanDisk Stock Drops Ahead of Split as Wall Street Analysts Weigh In
- 11/10 The Motley Fool | Why Sandisk Stock Dropped Again on Tuesday
- 11/12 Yahoo Finance | What Is Going on With Sandisk Stock on Thursday?
- 11/13 Trefis | SanDisk Stock At $937: Why So Cheap?

#### Yahooファイナンス
検索語: `SNDK`
- 11/13 Insider Monkey | 5 Multibagger Stocks to Buy According to Wall Street
- 11/13 Insider Monkey | 5 Stocks With Insane Upside According to Reddit
- 11/13 Motley Fool | Sandisk Stock Fell Back Under $900 on Friday. I'd Start With a Small Position.

### AMD（Advanced Micro Devices, Inc.、保有、半導体、前日比 -8.8%、1週 +18.9%、時間外 -2.4%）

#### Googleニュース
検索語: `Advanced Micro Devices stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/11 The Motley Fool | Why Advanced Micro Devices Stock Popped Today
- 11/13 Yahoo Finance | Why Advanced Micro Devices Stock Is Down Today
- 11/14 Moomoo | Advanced Micro Devices (AMD) Stock Sinks 9%: What the Options Flow and Dark Pools Say Now

#### Yahooファイナンス
検索語: `AMD`
- 11/14 TIKR | AMD Soars 19% in a Week on Oppenheimer’s Upgrade and Nvidia’s Turmoil: “Demand Is Higher Than Supply”

## 3. 引けまでに大きく下げた銘柄（2026-11-07〜2026-11-13 の見出し）

### NBIS（Nebius Group N.V.、AIプラットフォーム・クラウド、前日比 -9.9%、1週 -10.5%、時間外 -2.6%）

#### Googleニュース
検索語: `Nebius stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/12 Barron's | Nebius Stock Plummets After Earnings as CEO Warns of Revenue Delay
- 11/12 CNBC | Nebius falls 16% as company expects increased 2026 capex spend, issues weak outlook
- 11/12 The Motley Fool | Nebius Revenue Jumped 571%, So Why Did the Stock Fall?
- 11/13 Yahoo Finance | Why Is Nebius Stock Falling Today?

#### Yahooファイナンス
検索語: `NBIS`
- 11/13 Insider Monkey | Why Management Is Cautious About One Nebius (NBIS) Number
- 11/13 MT Newswires | Nebius Group Insider Sold Shares Worth $1,035,790, According to a Recent SEC Filing

### DELL（Dell Technologies Inc.、AIサーバー・ストレージ・メモリ・端末、前日比 -7.2%、1週 +4.9%、時間外 -1.5%）

#### Googleニュース
検索語: `Dell stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/9 investingLive | Earnings losses are sticking, but Dell shows why not every pullback is a failure
- 11/10 MarketWatch | Dell Technologies Inc. Cl C stock falls Tuesday, underperforms market
- 11/11 24/7 Wall St. | Dell Jumps 11% as AI Server Stocks Rebound From a Rough Month; Super Micro Surges 8%, Hewlett Packard Enterprise Advances 6%
- 11/13 Trefis | Can Dell Stock Fall 40%?

#### Yahooファイナンス
検索語: `DELL`
- 11/13 24/7 Wall St. | DLLL 2X Dell ETF Plunges 16% as Dell Tumbles 8% in AI Hardware Selloff; Hewlett Packard Enterprise Falls 4%
- 11/13 24/7 Wall St. | Super Micro Slides 3% as Reported DOJ Smuggling Probe Weighs for a Second Day; Dell Sinks 8%, NVIDIA Retreats 4%
- 11/13 Barchart | SMCI Stock Alert: Super Micro Computer Slammed By Alice Huang-Linked Server Smuggling Probe

## 4. 引けまでに大きく上げた銘柄（2026-11-07〜2026-11-13 の見出し）

### AVGO（Broadcom Inc.、半導体、前日比 -4.8%、1週 +18.2%、時間外 -1.8%）

#### Googleニュース
検索語: `Broadcom stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/11 Benzinga | Nvidia Stock Sinks as Jensen Huang Ouster Report Sends Investors Toward AMD, Broadcom - Broadcom (NASDAQ
- 11/12 Yahoo Finance | Why Broadcom Stock Rallied Thursday Morning
- 11/12 Yahoo Finance | Nvidia, AMD, Broadcom: The AI Stock Winners and Losers After Jensen Huang’s Ousting
- 11/14 Opening Bell Daily | Stock market this week: Broadcom jumps 18.2%

#### Yahooファイナンス
検索語: `AVGO`
- 11/14 Motley Fool | Broadcom Jumped as Nvidia Fell. This Is What Has Investors Excited.
- 11/14 Simply Wall St. | Top 3 AI Stocks To Watch In November 2026

### MPWR（Monolithic Power Systems, Inc.、半導体、前日比 -3.9%、1週 +16.8%、時間外 -1.2%）

#### Googleニュース
検索語: `Monolithic Power Systems stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/7 Trefis | Can Monolithic Power Systems Stock Fall 30%?
- 11/9 The Globe and Mail | Semtech, Entegris, Monolithic Power Systems, Broadcom, and Applied Materials shares are soaring, what you need to know
- 11/10 Yahoo Finance | Why Is Monolithic Power Systems Stock Going Up?
- 11/11 StockInvest.us | Monolithic Power Systems Stock Price Forecast. Should You Buy MPWR?

#### Yahooファイナンス
検索語: `MPWR`
- 11/10 Simply Wall St. | 3 AI Infrastructure Stocks Riding The Next Data Center Spending Wave
- 11/10 Zacks | Monolithic Power (MPWR) Crossed Above the 200-Day Moving Average: What That Means for Investors

### TER（Teradyne, Inc.、半導体製造装置・材料・設計ソフト・計測、前日比 -5.4%、1週 +14.4%、時間外 -2.8%）

#### Googleニュース
検索語: `Teradyne stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/11 Barron's | Teradyne Stock Jumps. Jefferies Sees a $2 Billion Nvidia Opportunity.
- 11/11 24/7 Wall St. | Wall Street's Newest Teradyne Bull Just Sent a $2 Billion Signal That the Stock's 56% Crash Went Too Far
- 11/11 Investor's Business Daily | Teradyne Stock Surges On Fresh Buy Rating, Called AI Play
- 11/12 Yahoo Finance | Cathie Wood Dumps the Last of Teradyne From Her Flagship Fund

#### Yahooファイナンス
検索語: `TER`
- 11/12 Insider Monkey | Why Jefferies’ Dushyant Ailani Calls Teradyne (TER) a “Compute Test Company”
- 11/12 Simply Wall St. | 3 Robotics Stocks To Own In November 2026

### LRCX（Lam Research Corporation、半導体製造装置・材料・設計ソフト・計測、前日比 -3.4%、1週 +12.7%、時間外 -1.4%）

#### Googleニュース
検索語: `Lam Research stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/7 Yahoo Finance | What Just Lifted Lam Research Stock?
- 11/11 24/7 Wall St. | Applied Materials Rallies 8% Ahead of Earnings as Chip Stocks Rebound; Lam Research Jumps 9%, KLA Climbs 7%
- 11/12 Yahoo Finance | Lam Research (LRCX) Lost About 34% in a Month. Here’s Why Bernstein’s Rasgon Still Likes It
- 11/13 StockInvest.us | Lam Research Stock Price Forecast. Should You Buy LRCX?

#### Yahooファイナンス
検索語: `LRCX`
- 11/13 24/7 Wall St. | Applied Materials Says Chip Demand Remains “Much Higher Than Supply”
- 11/13 Barrons.com | Applied Materials’ Earnings Beat Gets Lukewarm Reception as Nvidia Fallout Lingers

### AMAT（Applied Materials, Inc.、半導体製造装置・材料・設計ソフト・計測、前日比 -2.7%、1週 +11.4%、時間外 -2.0%）

#### Googleニュース
検索語: `Applied Materials stock (falls OR drops OR slides OR plunges OR sinks OR tumbles OR jumps OR soars OR why)`
- 11/9 24/7 Wall St. | Applied Materials Jumps 11% Ahead of Earnings; Lam Research Surges 9%, ASML Rises 6%
- 11/11 Yahoo Finance | Ahead of Applied Materials Earnings, Here's What Barchart Data Says Comes Next for AMAT Stock
- 11/13 Proactive financial news | Applied Materials Inc Share Price - AMAT, RNS News, Articles, Quotes, & Charts (NASDAQ:AMAT)
- 11/14 TradingKey | Applied Materials Stock Breaks Wedge as Rising Fab Forecasts Put $493 in Focus

#### Yahooファイナンス
検索語: `AMAT`
- 11/13 24/7 Wall St. | Thierry Borgeat Says Chip Stocks Peak Every Two Years. His Chart Points to Another Top
- 11/13 Investing.com | Applied Materials earnings analysis: questions answered and next catalysts
- 11/13 Investing.com | Earnings week scorecard: beats rewarded selectively as AI-infrastructure names pull back
