# SNDK等 株式チャート分析 — NotebookLM連携セットアップ記録

このドキュメントは、携帯（PC）からチャート画像を貼り付けるだけでNotebookLM経由の投資分析を実行できるようにするために行った構築作業の記録です。トラブル時の復旧や、将来の変更の際の参照用にまとめています。

**現在の状態（2026-09-20時点）: 方式Aが稼働中。方式B（VPS完全自動化）は未解決の壁により保留中。**

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

## 方式B: VPS完全自動化（PCの電源すら不要にする試み） — 現在保留中

「PCを一切使わず、携帯だけで完結させたい」という目標のため、常時起動のクラウドサーバー（VPS）上でChromeを常時ログイン状態に維持し、Claude Codeのクラウド環境からそこへ直接接続する方式を試みた。**VM側の構築は完了・正常動作しているが、Claude Code環境からVMへの接続が最後の最後でブロックされ、原因未解明のまま保留中。**

### 構築済みのインフラ（すべて正常稼働中）

- **VPS**: Google Cloud Platform (GCP) 無料枠、インスタンス名 `nlm-server`
  - リージョン: `us-central1-a`、マシンタイプ: `e2-micro`（Always Free対象）
  - 外部IP: `34.133.108.107`（固定IPではない。VM再起動で変わる可能性あり）
  - OS: Debian GNU/Linux 13、ユーザー名: `happy11design`
  - GCPプロジェクト: `project-7a8501cc-0f70-4619-953`
  - **90日間の無料トライアル中（2026年9月19日開始）。90日以内に「フルアカウントへアップグレード」しないと自動削除される（課金はされない設計だが、アップグレードしないとインスタンスが消える）。**
- **ドメイン**: `nlm-server-8823.com`（Porkbunで購入、2026-09-19、年更新$11.81）
  - DNS Aレコード: `34.133.108.107` を指す
- **VM上のソフトウェア構成**:
  - Chrome（サブアカウント notebookbunseki@gmail.com でログイン済み、`--remote-debugging-port=9222 --remote-allow-origins=*`）
  - Xvfb（仮想ディスプレイ、Chromeを画面なしサーバーで動かすため）
  - nginx（リバースプロキシ、443番でTLS終端しCDPポート9222へ中継、Basic認証つき: ユーザー`nlm`）
  - Let's Encrypt証明書（certbot、`nlm-server-8823.com`用、自動更新設定済み）
  - スワップファイル2GB追加済み（e2-microはメモリ1GBしかなく、Chrome+VNC同時起動でメモリ不足になったため）
  - systemdサービス化済み（`nlm-xvfb.service`, `nlm-chrome.service`）でクラッシュ時自動再起動
  - SSH公開鍵をClaude Code用に登録済み（`~/.ssh/authorized_keys`、コメント`claude-code-nlm-vps`）
  - Basic認証パスワード: `/etc/nginx/.htpasswd`（ユーザー`nlm`）

### 突き当たった壁: Claude Code環境からVMへの接続がブロックされる

Claude Codeが動いているクラウドサンドボックス環境（`分析`環境、`anthropic_cloud`種別）の出口には、**Anthropicの検査用プロキシ（"sandbox-egress-gateway"）**が入っており、すべての外向き通信を一度TLS復号して検査している。この検査ゲートウェイの挙動を切り分けた結果、以下が判明：

1. **生のSSH（22番ポート）は通らない**（HTTPS以外のプロトコルはブロックされる）
2. **SSHを443番ポートに変更しても通らない**（ポート番号ではなく中身のプロトコルを見ている。HTTPを期待する応答が返ってきた）
3. **自己署名証明書や`nip.io`（IPアドレスを疑似ドメイン化する無料サービス）経由のTLSは、ゲートウェイに独自証明書で中間者化(MITM)された上で、最終的に「upstream connect error」で失敗**（`nip.io`が回避目的のドメインとしてブロック対象になっている可能性を疑った）
4. **正式に購入した独自ドメイン（`nlm-server-8823.com`）+ Let's Encrypt正規証明書 + nginx Basic認証という「本物のHTTPS」構成にしても、依然として同じ「upstream connect error / 503」で失敗**（VM側のnginx・Chromeは正常動作をVM上のローカル確認・curlで確認済み。ゲートウェイが実際の転送先へ到達できていないだけ）

**現時点の仮説（未検証）**: 購入したてで日が浅いドメインを、セキュリティゲートウェイが一時的に警戒・ブロックしている可能性（新規登録ドメインへのアクセス制限はフィッシング対策として一般的な手法のため）。24〜48時間程度おいてから再テストする必要があるが、少し時間を置いた程度（数時間）では改善が見られなかった。**恒久的な制約（Claude Codeのこの種のクラウド環境からは、そもそもユーザー自身の任意の外部サーバーに到達できない設計）である可能性も残っている。**

### 今後の検証・選択肢

1. **丸1日以上待ってから再テスト**（ドメインエイジングが原因なら解決する可能性）
2. **「自分のPCをセルフホスト環境としてClaude Codeに登録する」方式に切り替える**（以前検討したが保留していた案。この場合Anthropicのサンドボックスを経由しないため、今回のブロックの影響を受けない）
3. **方式Bを諦め、方式A（PCで都度認証）を継続する**

VM・ドメイン自体は方式B専用というわけではなく、**Claude Code以外（携帯やPCの通常ブラウザ）からは普通にアクセスできるはずなので、無駄にはなっていない**。将来的に上記2の「セルフホスト環境」に切り替えれば、このVM・ドメインをそのまま活用できる見込み。

### 接続確認用コマンド（次回検証時に使う）

Claude Code環境側から:
```bash
env -u https_proxy -u HTTPS_PROXY -u http_proxy -u HTTP_PROXY curl -v -u nlm:（Basic認証パスワード） https://nlm-server-8823.com/json/version
```

VM側（SSH接続後）:
```bash
curl -s http://127.0.0.1:9222/json/version   # Chromeが生きているか
sudo systemctl status nlm-chrome.service nlm-xvfb.service nginx --no-pager
```

---

## 構築時に分かった注意点・ハマりどころ（総まとめ）

### Claude Code / GitHub関連
- **`.claude/`配下の変更はClaude自身がコミットできない**（自己設定変更としてブロックされる仕組み）。GitHubのWeb UIから手動で追加する必要がある。
- **GitHubのWeb UIでファイル作成する際、現在いるフォルダの中に作成される**ため、パス指定を間違えるとネストした誤った場所に作られる（`.claude/hooks/.claude/settings.json`のような事故が起きた）。ファイル作成前に、目的のフォルダまでパンくずで移動してから「Create new file」を使うと安全。
- **GitHubのWeb UIで作成したファイルは実行権限(+x)が付かない**。シェルスクリプトは`chmod +x`してコミットし直す必要がある（付いていないとSessionStartフックが`Permission denied (exit 126)`で失敗する）。
- **新しいセッションは既定でmainブランチを見る**。作業ブランチだけにコミットしても、mainにマージしない限り新規セッションには反映されない。
- **環境の設定変更（環境変数・ネットワークアクセス等）は新しいセッションから適用される**。既存セッションには反映されない。
- **ネットワークアクセスが「Trusted」だと`notebook.google.com`への通信がブロックされる**。「Full」に変更する必要がある。
- **Claude Codeのクラウド環境から、SSHや自前サーバーへの直接接続は極めて困難**（上記「方式B」参照）。HTTPSであっても、Anthropicの検査ゲートウェイが実際に転送してくれるとは限らない。

### NotebookLM / nlm CLI関連
- **nlmの自動ブラウザ認証(`nlm auth login`)は、コピーしたプロファイルでの自動操作だとGoogleにログイン画面へリダイレクトされて失敗しやすい**。実際に動いたのは、Chromeを`--remote-debugging-port`付きで起動し、CDP接続(`nlm auth -cdp-url ws://localhost:9222`)で実ブラウザのセッションをそのまま使う方法。
- **環境変数欄に値を貼り付ける際、`nlm auth --print-env`の出力に含まれるシングルクォート`'`を値ごとコピーしてしまうと認証に失敗する**。クォートを含めず中身だけを貼り付けること。
- **Chromeを`--remote-debugging-port`付きで2重起動しようとすると、同じユーザーデータディレクトリでは新しいインスタンスが立ち上がらない**（既存ウィンドウが開くだけでデバッグポートが有効にならない）。別の`--user-data-dir`を指定するか、既存プロセスを完全終了させてから起動し直す必要がある。

### GCP / VPS関連
- **`e2-micro`はメモリ1GBしかなく、Chrome+Xvfb+VNC関連プロセスを同時に動かすとすぐメモリ不足で固まる**。スワップファイルの追加が必須。
- **GCPのVMインスタンス作成画面のデフォルトはディスクが「バランス永続ディスク」（有料）になっている**。Always Free対象にするには「標準永続ディスク」に変更する必要がある。また、この画面の料金表示は無料枠割引を考慮しない定価表示のため、実際の請求とは異なる。
- **Let's Encrypt証明書の取得は、80番ポートを他のプロセス（nginx等）が使っていると`--standalone`モードで失敗する**。`certbot --nginx`プラグインを使うか、webroot方式で回避する。
