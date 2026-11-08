# バックテストのデータ（`tools/backtest_cache.py` が書くブランチ）

`cache/` は ~/.cache/stock_backtest/ の中身（株価・業種・決算日・指数の長い日足・ニュースの見出し・計算の結果）。戻すのは `python3 tools/backtest_cache.py restore`、保存は `save`（ブランチの中身に足す。ほかのセッションが保存したものは消さない）。手で編集しない。
