# SNDK等 株式チャート分析 — NotebookLM連携セットアップ記録

このドキュメントは、携帯（PC）からチャート画像を貼り付けるだけでNotebookLM経由の投資分析を実行できるようにするために行った構築作業の記録です。トラブル時の復旧や、将来の変更の際の参照用にまとめています。

## 全体構成

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
                 └─ 手順6: 複数ノートブックの回答を横断したClaudeの総合見解
```

## リポジトリ内のファイル

| ファイル | 役割 |
|---|---|
| `CLAUDE.md` | チャート分析依頼が来たら必ず`チャート分析.txt`の手順に従うよう指示。これがないとClaudeが自分で分析してしまう。 |
| `チャート分析.txt` | 分析の具体的な手順とNotebookLMへの送信プロンプト本体。 |
| `.claude/settings.json` | SessionStartフックの登録。 |
| `.claude/hooks/session-start.sh` | セッション開始時に自動でGo環境からnlm CLI (tmc/nlm) をインストールするスクリプト。実行権限(+x)が必須。 |

## 使っているツール: tmc/nlm

NotebookLMには公式APIが存在しないため、非公式のGo製CLI [tmc/nlm](https://github.com/tmc/nlm) を使用しています（`go install github.com/tmc/nlm/cmd/nlm@latest`）。ブラウザのログインセッション（Cookie）を利用してNotebookLMの内部APIを叩く仕組みです。

## セキュリティ設計: NotebookLM専用サブアカウント

nlmの認証情報（`NLM_AUTH_TOKEN` / `NLM_COOKIES`）は、GoogleアカウントのSID/HSID/SSID系Cookieを含み、これは本来Gmail・Driveなどアカウント全体に及ぶ強い権限を持ちます。そのため、**メインアカウント(happy11design@gmail.com)ではなく、NotebookLM専用に作成した別のGoogleアカウント（サブアカウント）**でNotebookLMを運用しています。万一クラウド環境の環境変数が漏洩しても、被害範囲はサブアカウント（チャート分析用ノートブックのみ）に限定されます。

チャート画像自体はメインアカウントのGoogle Drive等ではなく、**チャットへの直接添付**で渡す運用にしているため、Drive連携やサブアカウントとメインアカウントの混在は発生しません。

認証情報は claude.ai/code の環境「分析」の「環境変数」欄（`.env`形式）に保存しています。この欄は暗号化された秘密情報用の欄ではなく、この環境を使う全員に平文で見える欄である点に注意（現状は自分しか使っていないため実質問題なし）。

## 日常の使い方

1. claude.ai/code で環境「分析」の新しいセッションを開く（PC・携帯どちらでも可）
2. チャート画像をチャットに直接貼り付ける
3. 「SNDKで分析して」のように銘柄を指定して送信（証券コードなしでも可）
4. NotebookLM（複数ノートブックがあれば並行処理）の回答＋Claudeの総合見解が返ってくる

## 認証切れ時の復旧手順（重要）

NotebookLMのセッションCookieは**有効期限が短く、頻繁に失効します**。`nlm`が「authentication expired or invalid」を返したら、以下を**間を空けずに一気に**実行してください。

1. PCでChromeを完全終了（タスクマネージャーで確認）
2. 専用プロファイル・デバッグポート付きでChromeを起動
   ```
   "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\chrome-nlm-debug"
   ```
3. そのウィンドウでNotebookLM専用サブアカウントにログインし、`https://notebook.google.com` を開いて画面表示を確認
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

## 構築時に分かった注意点・ハマりどころ

- **`.claude/`配下の変更はClaude自身がコミットできない**（自己設定変更としてブロックされる仕組み）。GitHubのWeb UIから手動で追加する必要がある。
- **GitHubのWeb UIでファイル作成する際、現在いるフォルダの中に作成される**ため、パス指定を間違えるとネストした誤った場所に作られる（`.claude/hooks/.claude/settings.json`のような事故が起きた）。ファイル作成前に、目的のフォルダまでパンくずで移動してから「Create new file」を使うと安全。
- **GitHubのWeb UIで作成したファイルは実行権限(+x)が付かない**。シェルスクリプトは`chmod +x`してコミットし直す必要がある（付いていないとSessionStartフックが`Permission denied (exit 126)`で失敗する）。
- **新しいセッションは既定でmainブランチを見る**。作業ブランチだけにコミットしても、mainにマージしない限り新規セッションには反映されない。
- **環境の設定変更（環境変数・ネットワークアクセス等）は新しいセッションから適用される**。既存セッションには反映されない。
- **ネットワークアクセスが「Trusted」だと`notebook.google.com`への通信がブロックされる**。「Full」に変更する必要がある。
- **nlmの自動ブラウザ認証(`nlm auth login`)は、コピーしたプロファイルでの自動操作だとGoogleにログイン画面へリダイレクトされて失敗しやすい**。実際に動いたのは、Chromeを`--remote-debugging-port`付きで起動し、CDP接続(`nlm auth -cdp-url ws://localhost:9222`)で実ブラウザのセッションをそのまま使う方法。
- **環境変数欄に値を貼り付ける際、`nlm auth --print-env`の出力に含まれるシングルクォート`'`を値ごとコピーしてしまうと認証に失敗する**。クォートを含めず中身だけを貼り付けること。
