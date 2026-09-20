# SNDK等 株式チャート分析 — NotebookLM連携セットアップ記録

このドキュメントは、携帯（PC）からチャート画像を貼り付けるだけでNotebookLM経由の投資分析を実行できるようにするために行った構築作業の記録です。トラブル時の復旧や、将来の変更の際の参照用にまとめています。

**現在の状態（2026-09-20時点）: 方式A・方式Bともに動作確認済み。方式B（VPS完全自動化、PCの電源不要）はクラウドセッションからの実接続・NotebookLM認証情報の取得・`nlm notebook list`によるAPI疎通まで完全に成功した。**

---

## 方式A: 現在の運用方法（動作確認済み・実際に分析成功済み）

携帯・PCから claude.ai/code の環境「分析」を開き、都度PCでNotebookLMの再認証をしてから使う方式。**これは実際に最初から最後まで動作確認済み。**

### 全体構成

```
ユーザー（携帯 or PC）
  └─ claude.ai/code を開き、環境「分析」でセッションを開始
       └─ チャート画像をチャットに直接貼り付け + "SNDKで分析して" と入力
            └─ CLAUDE.md の指示により、チャート分析.txt の手順を実行
                 ├─ 手順1: 添付画像のパスを取得（Google Drive不要）
                 ├─ 手順2/3: 経済指標・銘柄ファンダメンタルズを並行Web検索
                 ├─ 手順4: nlm notebook list で対象ノートブック特定
                 ├─ 手順5: 各ノートブックへ並行して画像を送り nlm generate-chat
                 │        （NotebookLM専用サブアカウントで認証）
                 ├─ 手順6: 複数ノートブックの回答を横断したClaudeの総合見解
                 └─ 手順7: 結果をGoogle Drive経由でObsidian vaultへ自動保存
```

## 補足: Obsidianへの自動保存（Google Drive連携）

「第2の脳」vault（元は `C:\ファイル\Obsidian`）を丸ごと `G:\マイドライブ\Obsidian\第2の脳` へ移動し、Google Driveで同期される状態にした。これにより、Claude Codeのクラウドセッション（Google Drive連携ツールを使用）から直接ノートを書き込め、PC側のObsidianには同期を通じて自動反映される。

- 保存先フォルダ: `Obsidian/第2の脳/株式分析/日次記録/`（フォルダID: `1PbrnfdA7Oc8Ooa7wvWqVDQIbaIQ71ylo`）
- Google Drive連携の権限は当初「読み取り専用」だったため、claude.aiの設定画面でGoogle Driveコネクタを書き込み権限つきで再連携する必要があった。
- ファイル作成時は `disableConversionToGoogleType: true` を指定しないと、`.md`ファイルがGoogleドキュメントに自動変換されてしまうため注意。
- **注意点**: Obsidian公式はGoogle DriveのようなクラウドDriveでのvault同期を推奨していない（`.obsidian`設定フォルダ等で同期競合が起きるリスクがあるため）。今回は「日次記録に新規ファイルを追加するだけ」の運用に留めることでリスクを抑えている。PCのGoogle Driveアプリが起動していないと、書き込んだ内容はPC側にすぐには反映されない。

### リポジトリ内のファイル

| ファイル | 役割 |
|---|---|
| `CLAUDE.md` | チャート分析依頼が来たら必ず`チャート分析.txt`の手順に従うよう指示。これがないとClaudeが自分で分析してしまう。 |
| `チャート分析.txt` | 分析の具体的な手順とNotebookLMへの送信プロンプト本体。 |
| `.claude/settings.json` | SessionStartフックの登録。 |
| `.claude/hooks/session-start.sh` | セッション開始時に自動でGo環境からnlm CLI (tmc/nlm) をインストールするスクリプト。実行権限(+x)が必須。 |

### 使っているツール: tmc/nlm

NotebookLMには公式APIが存在しないため、非公式のGo製CLI [tmc/nlm](https://github.com/tmc/nlm) を使用（`go install github.com/tmc/nlm/cmd/nlm@latest`）。ブラウザのログインセッション（Cookie）を利用してNotebookLMの内部APIを叩く仕組み。

### セキュリティ設計: NotebookLM専用サブアカウント

nlmの認証情報（`NLM_AUTH_TOKEN` / `NLM_COOKIES`）は、GoogleアカウントのSID/HSID/SSID系Cookieを含み、これは本来Gmail・Driveなどアカウント全体に及ぶ強い権限を持つ。そのため、**メインアカウント(happy11design@gmail.com)ではなく、NotebookLM専用に作成した別のGoogleアカウント（サブアカウント: notebookbunseki@gmail.com）**でNotebookLMを運用している。万一クラウド環境の環境変数が漏洩しても、被害範囲はサブアカウント（チャート分析用ノートブックのみ）に限定される。

チャート画像自体はメインアカウントのGoogle Drive等ではなく、**チャットへの直接添付**で渡す運用のため、Drive連携やサブアカウントとメインアカウントの混在は発生しない。

現在、サブアカウントのノートブックは5件（すべて「Claude_」で始まるタイトル）:
- Claude_新高値ブレイク投資術
- Claude_株空売り 5つの戦術
- Claude_マット・ペトラリア氏
- Claude_ちょる子
- Claude_株価チャート分析

認証情報は claude.ai/code の環境「分析」の「環境変数」欄（`.env`形式）に保存。この欄は暗号化された秘密情報用の欄ではなく、この環境を使う全員に平文で見える欄である点に注意（現状は自分しか使っていないため実質問題なし）。より安全な「API認証情報」欄は、HTTP APIへのヘッダー注入専用の仕組みでシェル環境変数には使えないため不採用。

### 日常の使い方

1. claude.ai/code で環境「分析」の新しいセッションを開く（PC・携帯どちらでも可）
2. チャート画像をチャットに直接貼り付ける
3. 「SNDKで分析して」のように銘柄を指定して送信（証券コードなしでも可）
4. NotebookLM（複数ノートブックがあれば並行処理）の回答＋Claudeの総合見解が返ってくる

### 認証切れ時の復旧手順（重要・頻繁に必要）

NotebookLMのセッションCookieは**有効期限が短く、頻繁に失効する**（PC上でローカル実行してもすぐ切れることを確認済み。クラウド特有の問題ではない）。`nlm`が「authentication expired or invalid」を返したら、以下を**間を空けずに一気に**実行する。

1. PCでChromeを完全終了（タスクマネージャーで確認、プロセスが残っていないか確認）
2. 専用プロファイル・デバッグポート付きでChromeを起動
   ```
   "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\chrome-nlm-debug"
   ```
3. そのウィンドウでNotebookLM専用サブアカウント（notebookbunseki@gmail.com）にログインし、`https://notebook.google.com` を開いて画面表示を確認
4. 別のコマンドプロンプトで再認証
   ```
   C:\Users\a\go\bin\nlm.exe auth -cdp-url ws://localhost:9222
   ```
5. 環境変数用の値を出力
   ```
   C:\Users\a\go\bin\nlm.exe auth --print-env
   ```
6. 表示された値（**前後のクォート `'` は含めない**）を、claude.ai/codeの環境「分析」の「環境変数」欄に上書き貼り付け
   ```
   NLM_AUTH_TOKEN=（値）
   NLM_COOKIES=（値）
   ```
7. 「変更を保存」を押したら、**すぐに**新しいセッションで動作確認

---

## 方式B: VPS完全自動化（PCの電源すら不要） — 2026-09-20 完全動作確認済み

「PCを一切使わず、携帯だけで完結させたい」という目標のため、常時起動のクラウドサーバー（VPS）上でChromeを常時ログイン状態に維持し、Claude Codeのクラウド環境からそこへ直接接続する方式。**長期間「Claude Codeのクラウド環境からは外部サーバーに到達できないのではないか」という仮説のもとで保留していたが、実際には仮説が誤りで、VM側に3つの独立した設定不備が重なっていただけだった。すべて修正し、クラウドセッションから実際にNotebookLM専用サブアカウントの認証情報を取得し、`nlm notebook list`でノートブック一覧取得まで成功した。**

### 構築済みのインフラ

- **VPS**: Google Cloud Platform (GCP) 無料枠、インスタンス名 `nlm-server`
  - リージョン: `us-central1-a`、マシンタイプ: `e2-micro`（Always Free対象）
  - 外部IP: `34.133.108.107`（固定IPではない。VM再起動で変わる可能性あり）
  - OS: Debian GNU/Linux 13、ユーザー名: `happy11design`
  - GCPプロジェクト: `project-7a8501cc-0f70-4619-953`
  - 90日間の無料トライアル中（2026年9月19日開始）。90日以内に「フルアカウントへアップグレード」しないと自動削除される。
- **ドメイン**: `nlm-server-8823.com`（Porkbunで購入、2026-09-19、年更新$11.81）
  - DNS Aレコード: `34.133.108.107` を指す
- **VM上のソフトウェア構成**:
  - Chrome（サブアカウント notebookbunseki@gmail.com でログイン済み、`--remote-debugging-port=9222 --remote-allow-origins=* --disable-metrics --disable-metrics-reporting`）
  - Xvfb（仮想ディスプレイ）、`nlm-xvfb.service` / `nlm-chrome.service`（systemd、`Restart=always`）
  - nginx（リバースプロキシ、443番でTLS終端しCDPポート9222へ中継）
  - Let's Encrypt証明書（certbot、`nlm-server-8823.com`用、自動更新設定済み）
  - スワップファイル2GB（e2-microはメモリ1GBしかないため）
  - noVNC（`x11vnc` + `websockify`、6080番ポート、systemd化されていないため再起動時は手動起動が必要）

### 判明した3つの真因（「ゲートウェイが外部接続を一律ブロックしている」という当初の仮説は誤りだった）

過去のセッションでは「Anthropicのサンドボックス出口ゲートウェイが、この種のクラウド環境から任意の外部サーバーへの到達を一律ブロックしている」と結論づけていたが、これは誤診断だった。**実際にVM側の設定を1つずつ検証したところ、ゲートウェイは真のHTTPS/WebSocket通信を問題なく通していた。** 真因は以下の3つがすべて重なっていたこと：

1. **sshdが443番ポートを掴んでいた**: 過去のトラブルシュートで「SSHが22番で繋がらないので443番でも待ち受けさせる」設定 (`sshd_config`に`Port 443`) を追加していたが、これがnginxの443番バインドと競合していた。`systemctl status nginx`は一見正常に見えても、実際には443番のリッスンに失敗し続けており、`ss -tlnp`で確認するとsshdだけが443番を握っていた。TLSハンドシェイクをすると相手がSSHデーモンのため「wrong version number」エラーになる。
   → **対処**: `sshd_config`の`Port 443`をコメントアウトし、22番のみに戻す（現在のSSHはGCP IAPトンネル経由で22番を使っているため、443番を外しても切断されない。実際のSSH接続元は`echo $SSH_CONNECTION`と`ss -tnp | grep sshd`で確認できる）。
2. **Xvfbのクラッシュループ**: ディスク満杯時にXvfbが異常終了し、`/tmp/.X1-lock`ロックファイルが残ったまま、かつ手動起動していた古いXvfbプロセス（systemd管理外）がディスプレイ`:1`のソケットを握ったままになっていた。`nlm-xvfb.service`は「already active」「Cannot establish any listening sockets」で無限に再起動ループしており、Chromeもディスプレイ先を得られず数秒で落ち続けていた。
   → **対処**: `ps aux | grep -i xvfb`で systemd管理外の古いプロセスを特定して`kill -9`、`/tmp/.X1-lock`と`/tmp/.X11-unix/X1`を削除してから`systemctl start`。
3. **chromedpの`gobwas/ws`ライブラリはURLの`user:pass@host`形式を一切HTTPヘッダーに変換しない**: `curl -u`やブラウザは`wss://user:pass@host/...`形式のURLを自動的に`Authorization: Basic ...`ヘッダーに変換するが、`nlm`が内部で使っている生WebSocketクライアント（`github.com/gobwas/ws`）は**この変換を行わない**。そのためnginxの`auth_basic`（Basic認証）は、`curl`では通っても`nlm`の接続では常に401 Unauthorizedになっていた。加えて、chromedpの`RemoteAllocator`はデフォルトで`modifyURL`という処理を行い、平文HTTPで`/json/version`を取得し直し、接続先ホストをIPアドレスに書き換えてしまう（`forceIP`）。これによりTLS証明書（ドメイン名用）とIPアドレスが不一致になり検証エラーになる問題も別途あった。
   → **対処（2点）**:
   a. `nlm`（`tmc/nlm`）にパッチを適用: 接続先URLに`/devtools/browser/`が含まれる場合は`chromedp.NoModifyURL`オプションを使い、`modifyURL`処理（平文HTTP参照 + IPホスト書き換え）を完全にスキップする。パッチは本リポジトリの `tools/nlm-nomodifyurl.patch` に保存し、`.claude/hooks/session-start.sh`がセッション開始時に自動でクローン・パッチ適用・ビルドする。
   b. nginx側の認証方式をBasic認証から「秘密パスプレフィックス」方式に変更（`location /nlmcdp-<ランダム40文字hex>/ { rewrite ^/nlmcdp-<同じ文字列>/(.*)$ /$1 break; proxy_pass http://127.0.0.1:9222; ... }`）。パス・クエリは生WebSocket接続でも正しく送信されるため、どんなクライアントでも通る。

### 現在の接続方法

```bash
# 1. 現在のChromeのUUID（devtools/browser/のパス）を取得
curl -s "https://nlm-server-8823.com/nlmcdp-<秘密トークン>/json/version"
# → webSocketDebuggerUrl の "devtools/browser/<UUID>" 部分を使う

# 2. パッチ版nlmで認証情報を取得（session-start.shが自動ビルドしたものを使用）
nlm auth -cdp-url "wss://nlm-server-8823.com:443/nlmcdp-<秘密トークン>/devtools/browser/<UUID>"
# → 成功すると /root/.nlm/env に NLM_AUTH_TOKEN / NLM_COOKIES が書き込まれる

# 3. 動作確認
nlm notebook list
```

**秘密トークンの管理**: nginxの秘密パスは事実上「VMのChromeを丸ごと遠隔操作できる鍵」に相当するため、`チャート分析.txt`のような平文のリポジトリファイルに直接書き込むのではなく、claude.ai/codeの環境「分析」の環境変数欄に `NLM_VPS_CDP_BASE=wss://nlm-server-8823.com:443/nlmcdp-<秘密トークン>` として保存し、手順内では `$NLM_VPS_CDP_BASE` を参照する運用を推奨する。

### Googleセッション自体が切れた場合（nlmの認証情報とは別問題）

上記の接続方法はあくまで「VM上のChromeがログイン状態を維持している」前提での認証情報の取得・更新である。Googleアカウント自体のログインセッションが切れた場合（体感的に方式Aと同様、短時間で切れることがある）は、VM上のChromeへ実際にログイン操作をする必要があり、これはPCなしで携帯のブラウザからでも可能：

```bash
# VM側でnoVNCを起動（systemd化されていないため再起動時は手動実行が必要）
nohup x11vnc -display :1 -forever -shared -rfbport 5900 -nopw > /tmp/x11vnc.log 2>&1 &
nohup websockify --web=/usr/share/novnc/ 6080 localhost:5900 > /tmp/websockify.log 2>&1 &
```

携帯・PCのブラウザで `http://34.133.108.107:6080/vnc.html` を開き、NotebookLM専用サブアカウントで再ログインする（GCPファイアウォールで6080番へのアクセスが許可されている必要がある）。ログイン後は上記「現在の接続方法」の手順1からやり直す。

### 今後の改善候補（未着手）

- noVNC（x11vnc/websockify）もsystemdサービス化し、`Restart=always`にする（現状はVM再起動のたびに手動起動が必要）。
- Chromeの安定性確認のため、しばらく運用してcrashpad/ディスク使用量を定点観測する（`--disable-metrics`フラグ追加後の効果は未検証のまま今回の作業に入ったため）。
- `nlm-xvfb.service`に`ExecStartPre`で`/tmp/.X1-lock`等の自動クリーンアップを追加し、同種のクラッシュループの再発を防ぐ（今回は手動対処のみ）。

---

## 構築時に分かった注意点・ハマりどころ（総まとめ）

### Claude Code / GitHub関連
- **`.claude/`配下の変更はClaude自身がコミットできない**（自己設定変更としてブロックされる仕組み）。GitHubのWeb UIから手動で追加する必要がある。
- **GitHubのWeb UIでファイル作成する際、現在いるフォルダの中に作成される**ため、パス指定を間違えるとネストした誤った場所に作られる（`.claude/hooks/.claude/settings.json`のような事故が起きた）。ファイル作成前に、目的のフォルダまでパンくずで移動してから「Create new file」を使うと安全。
- **GitHubのWeb UIで作成したファイルは実行権限(+x)が付かない**。シェルスクリプトは`chmod +x`してコミットし直す必要がある（付いていないとSessionStartフックが`Permission denied (exit 126)`で失敗する）。
- **新しいセッションは既定でmainブランチを見る**。作業ブランチだけにコミットしても、mainにマージしない限り新規セッションには反映されない。
- **環境の設定変更（環境変数・ネットワークアクセス等）は新しいセッションから適用される**。既存セッションには反映されない。
- **ネットワークアクセスが「Trusted」だと`notebook.google.com`への通信がブロックされる**。「Full」に変更する必要がある。
- **Claude Codeのクラウド環境から、自前サーバーへのHTTPS/WebSocket接続自体は問題なく通る**（当初「ゲートウェイが一律ブロックしている」と誤診断していたが、実際はVM側の設定不備が原因だった。上記「方式B」の真因3点を参照）。ただし生のSSH（22番・443番問わず）は通らない。
- **`chromedp`（`nlm`が内部で使う）の`gobwas/ws`ライブラリは、URLの`user:pass@host`形式のBasic認証情報を一切HTTPヘッダーに変換しない**。`curl -u`やブラウザは自動変換するが、生WebSocketクライアントは一般にそうとは限らないため、nginx側で認証する場合はBasic認証ではなくURLパス（秘密プレフィックス等）を使う方が互換性が高い。
- **`chromedp.NewRemoteAllocator`はデフォルトで`modifyURL`処理を行い、平文HTTPで`/json/version`を取得し直し、接続先をIPアドレスに書き換える**。独自ドメイン+TLS証明書の構成では、この書き換えによりホスト名とIPが不一致になり証明書検証に失敗する。`/devtools/browser/<uuid>`まで含む完全なURLを渡した上で`chromedp.NoModifyURL`オプションを使えばこの処理を完全にスキップできる。

### NotebookLM / nlm CLI関連
- **nlmの自動ブラウザ認証(`nlm auth login`)は、コピーしたプロファイルでの自動操作だとGoogleにログイン画面へリダイレクトされて失敗しやすい**。実際に動いたのは、Chromeを`--remote-debugging-port`付きで起動し、CDP接続(`nlm auth -cdp-url ws://localhost:9222`)で実ブラウザのセッションをそのまま使う方法。
- **環境変数欄に値を貼り付ける際、`nlm auth --print-env`の出力に含まれるシングルクォート`'`を値ごとコピーしてしまうと認証に失敗する**。クォートを含めず中身だけを貼り付けること。
- **Chromeを`--remote-debugging-port`付きで2重起動しようとすると、同じユーザーデータディレクトリでは新しいインスタンスが立ち上がらない**（既存ウィンドウが開くだけでデバッグポートが有効にならない）。別の`--user-data-dir`を指定するか、既存プロセスを完全終了させてから起動し直す必要がある。

### GCP / VPS関連
- **`e2-micro`はメモリ1GBしかなく、Chrome+Xvfb+VNC関連プロセスを同時に動かすとすぐメモリ不足で固まる**。スワップファイルの追加が必須。
- **GCPのVMインスタンス作成画面のデフォルトはディスクが「バランス永続ディスク」（有料）になっている**。Always Free対象にするには「標準永続ディスク」に変更する必要がある。また、この画面の料金表示は無料枠割引を考慮しない定価表示のため、実際の請求とは異なる。
- **Let's Encrypt証明書の取得は、80番ポートを他のプロセス（nginx等）が使っていると`--standalone`モードで失敗する**。`certbot --nginx`プラグインを使うか、webroot方式で回避する。
