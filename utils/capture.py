import os
import sys
import tkinter as tk
from PIL import ImageGrab
from pynput import mouse

if getattr(sys, 'frozen', False):
    # PyInstaller でビルドされた場合
    dpath = os.path.dirname(sys.executable)
else:
    # 通常の Python スクリプトとして実行された場合
    dpath = os.path.dirname(sys.argv[0])

class ScreenCapture:
    def __init__(self):
        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.5)
        self.root.configure(bg='white')
        self.root.bind('<Return>', self.finalize_capture)

        self.start_position = None
        self.end_position = None
        self.selection = None
        self.capture_image = None
        self.capture_complete = False
        self.image_path = None  # スクリーンショットの保存パスを保持する変数

    def on_click(self, x, y, button, pressed):
        if pressed:
            self.start_position = (x, y)
            self.selection = tk.Canvas(self.root, cursor="cross", bg='black', bd=0, highlightthickness=0)
            self.selection.place(x=x, y=y, width=1, height=1)
        else:
            if self.selection:
                self.end_position = (x, y)
                self.selection.place_configure(width=max(1, x - self.start_position[0]), height=max(1, y - self.start_position[1]))
                self.selection = None

    def on_drag(self, x, y):
        if self.start_position and self.selection:
            self.selection.place_configure(width=max(1, x - self.start_position[0]), height=max(1, y - self.start_position[1]))

    def finalize_capture(self, event):
        if self.start_position and self.end_position:
            self.root.withdraw()  # キャプチャ前にウィンドウを非表示にする
            self.capture_image = ImageGrab.grab(bbox=(self.start_position[0], self.start_position[1], self.end_position[0], self.end_position[1]))
            self.capture_complete = True
            self.exit_capture()

    def exit_capture(self):
        self.image_path = self.save_image()  # 保存してパスを更新
        self.cleanup()
        self.root.quit()  # 明示的にメインループを終了させる
        self.root.destroy()  # 完全にウィンドウを破棄する

    def cleanup(self):
        if self.selection:
            self.selection.destroy()
        self.root.unbind('<Return>')
        self.start_position = None
        self.end_position = None
        self.root.deiconify()  # ウィンドウを再表示する場合はここで
        self.root.attributes('-alpha', 1)  # 必要に応じて透明度を元に戻す

    def screenshot(self):
        return self.listen()  # キャプチャした画像のパスを返す

    def listen(self):
        with mouse.Listener(on_click=self.on_click, on_move=self.on_drag) as self.mouse_listener:
            self.root.mainloop()
            if self.capture_complete:  # キャプチャが完了したらループを終了する
                self.mouse_listener.stop()
        return self.image_path

    def save_image(self):
        if self.capture_image:
            tmp_dir = os.path.join(dpath, "tmp/")
            if not os.path.exists(tmp_dir):
                os.makedirs(tmp_dir)
            self.image_path = os.path.join(tmp_dir, "screenshot.png")
            self.capture_image.save(self.image_path)
            return self.image_path  # この行を追加
