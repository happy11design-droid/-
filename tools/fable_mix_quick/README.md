# Fable 5.2 の「混ぜて持つ形」の試し計算（2026-11-15）

既にある結果のファイル（`~/.cache/stock_backtest/results/`。`python3 tools/backtest_cache.py restore` で戻る）を読んで数えるだけ。新しいバックテストはしない。全部で約5分。

| スクリプト | 読むファイル | 数えるもの |
|---|---|---|
| mixA.py | allforms_screen_*.json | 選ぶ側の上位K形を等しく混ぜたときの、選ぶ側→確かめる側（M1と同じ分け方） |
| mixB.py | st2roll_*.json | 本番の14形を等しく混ぜる・今のルールと半分ずつ・乱数の違う2口 |
| mixC.py | allforms_screen_*.json、v_noskip_*.json、troll_*.json | 両方の監視銘柄で選ぶ決まりでの上位K形、候補を見送らない形との差 |
| mixD.py | hold_eq_*.json | 保留の形と今のルールを口に分けて混ぜる（毎日の資金） |
| mixE.py・mixF.py | hold_eq_*.json | 87銘柄の口と全業種の口を混ぜる |
| mixG.py | st2roll_*.json | 空の枠から始めた1年で、監視銘柄を混ぜる・中身で選んだ5形を混ぜる |

出力は `新分析ツール/バックテスト結果/Fableの混ぜて持つ形の試し計算_2026-11-15/出力.txt`。
