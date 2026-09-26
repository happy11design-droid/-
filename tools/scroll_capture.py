#!/usr/bin/env python3
"""スクロール連続スクリーンショット

指定した画面範囲を「スクショ → マウスホイール縦スクロール1クリック → スクショ …」
と繰り返して連番PNGで保存する。

※ 画面操作を行うため、クラウド環境ではなく手元のPC（Windows / macOS / Linuxデスクトップ）で実行する。

準備:
    pip install pyautogui mss pillow

使い方:
    # 範囲をマウスでドラッグして指定し、20枚撮影
    python tools/scroll_capture.py --count 20

    # 範囲を数値で指定（左上X, 左上Y, 幅, 高さ）
    python tools/scroll_capture.py --region 100,200,800,600 --count 10

主なオプション:
    --count N       撮影枚数（既定 10）
    --clicks N      1回あたりのスクロール量（ホイールのクリック数、既定 1）
    --wait 秒       スクロール後、描画を待つ時間（既定 0.8）
    --delay 秒      開始前のカウントダウン（既定 3）。この間に対象ウィンドウを前面へ
    --up            上方向にスクロールする（既定は下方向）
    --no-stop       前回と同じ画像になっても（=末尾に到達しても）止めない
    --out フォルダ  保存先（既定 screenshots/日時）

中断: マウスを画面の左上隅に素早く移動する（pyautogui のフェイルセーフ）か Ctrl+C。
"""

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path


def enable_dpi_awareness():
    """Windowsの表示スケーリング(125%等)で座標がずれないようにする。"""
    if sys.platform != "win32":
        return
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def select_region():
    """全画面の半透明オーバーレイ上でドラッグして範囲を選ぶ。(left, top, width, height) を返す。"""
    import tkinter as tk
    import mss

    with mss.mss() as sct:
        vs = sct.monitors[0]  # 全モニタを含む仮想スクリーン

    result = {}
    root = tk.Tk()
    root.overrideredirect(True)
    root.geometry(f"{vs['width']}x{vs['height']}+{vs['left']}+{vs['top']}")
    root.attributes("-topmost", True)
    try:
        root.attributes("-alpha", 0.3)
    except tk.TclError:
        pass
    canvas = tk.Canvas(root, cursor="cross", bg="gray", highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    canvas.create_text(
        vs["width"] // 2, 40, fill="white", font=("", 20, "bold"),
        text="撮影したい範囲をドラッグしてください（Escでキャンセル）",
    )
    state = {"x": 0, "y": 0, "rect": None}

    def on_press(e):
        state["x"], state["y"] = e.x, e.y
        state["rect"] = canvas.create_rectangle(e.x, e.y, e.x, e.y, outline="red", width=3)

    def on_drag(e):
        canvas.coords(state["rect"], state["x"], state["y"], e.x, e.y)

    def on_release(e):
        x1, x2 = sorted((state["x"], e.x))
        y1, y2 = sorted((state["y"], e.y))
        if x2 - x1 > 5 and y2 - y1 > 5:
            result["region"] = (x1 + vs["left"], y1 + vs["top"], x2 - x1, y2 - y1)
        root.destroy()

    canvas.bind("<ButtonPress-1>", on_press)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)
    root.bind("<Escape>", lambda e: root.destroy())
    root.focus_force()
    root.mainloop()
    return result.get("region")


def parse_region(text):
    try:
        vals = [int(v) for v in text.split(",")]
        if len(vals) != 4 or vals[2] <= 0 or vals[3] <= 0:
            raise ValueError
        return tuple(vals)
    except ValueError:
        raise argparse.ArgumentTypeError("--region は 左上X,左上Y,幅,高さ の形式で指定してください（例: 100,200,800,600）")


def main():
    ap = argparse.ArgumentParser(description="指定範囲をスクロールしながら連続スクリーンショット")
    ap.add_argument("--region", type=parse_region, help="左上X,左上Y,幅,高さ（省略時はドラッグで指定）")
    ap.add_argument("--count", type=int, default=10, help="撮影枚数（既定 10）")
    ap.add_argument("--clicks", type=int, default=1, help="1回のスクロール量＝ホイールのクリック数（既定 1）")
    ap.add_argument("--wait", type=float, default=0.8, help="スクロール後の待ち時間 秒（既定 0.8）")
    ap.add_argument("--delay", type=float, default=3, help="開始前のカウントダウン 秒（既定 3）")
    ap.add_argument("--up", action="store_true", help="上方向にスクロールする")
    ap.add_argument("--no-stop", action="store_true", help="画面が変化しなくなっても止めない")
    ap.add_argument("--out", type=Path, help="保存先フォルダ（既定 screenshots/日時）")
    args = ap.parse_args()

    if args.count < 1:
        ap.error("--count は1以上を指定してください")

    enable_dpi_awareness()
    try:
        import mss
        import mss.tools
        import pyautogui
    except ImportError:
        sys.exit("必要なライブラリがありません: pip install pyautogui mss pillow")

    region = args.region or select_region()
    if not region:
        sys.exit("範囲が指定されなかったため終了します。")
    left, top, width, height = region

    out = args.out or Path("screenshots") / datetime.now().strftime("%Y%m%d_%H%M%S")
    out.mkdir(parents=True, exist_ok=True)

    print(f"範囲: X={left} Y={top} 幅={width} 高さ={height} / {args.count}枚 / 保存先: {out}")
    for i in range(int(args.delay), 0, -1):
        print(f"  {i}秒後に開始します…（対象ウィンドウを前面に出してください）")
        time.sleep(1)
    time.sleep(args.delay - int(args.delay))

    pyautogui.FAILSAFE = True
    # スクロールは範囲の中央にマウスを置いて行う（その位置にあるウィンドウ/枠がスクロールされる）
    cx, cy = left + width // 2, top + height // 2
    step = args.clicks if args.up else -args.clicks
    monitor = {"left": left, "top": top, "width": width, "height": height}

    saved = 0
    prev = None
    try:
        with mss.mss() as sct:
            for n in range(1, args.count + 1):
                shot = sct.grab(monitor)
                if prev is not None and shot.rgb == prev and not args.no_stop:
                    print("画面が変化しなくなった（末尾に到達した）ため終了します。")
                    break
                path = out / f"{n:03d}.png"
                mss.tools.to_png(shot.rgb, shot.size, output=str(path))
                saved += 1
                prev = shot.rgb
                print(f"  [{n}/{args.count}] {path}")
                if n == args.count:
                    break
                pyautogui.moveTo(cx, cy)
                pyautogui.scroll(step)
                time.sleep(args.wait)
    except pyautogui.FailSafeException:
        print("フェイルセーフ（マウスが画面隅に移動）により中断しました。")
    except KeyboardInterrupt:
        print("Ctrl+C により中断しました。")

    print(f"完了: {saved}枚を {out.resolve()} に保存しました。")


if __name__ == "__main__":
    main()
