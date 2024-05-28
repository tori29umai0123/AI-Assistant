import datetime
import os
import sys
import tkinter as tk
from io import BytesIO
from tkinter import ttk

import numpy as np
import torch
import win32clipboard
from PIL import Image, ImageTk
from tkinterdnd2 import DND_FILES, TkinterDnD
from torchvision.transforms.functional import to_tensor, to_pil_image

from utils.capture import ScreenCapture
from utils.img_utils import canny_process, invert_process, flatline_process, mask_process, multiply_images, \
    resize_image_aspect_ratio, base_generation, make_base_pil
from utils.lang_util import Lang_Util
from utils.prompt_utils import remove_duplicates, remove_color, prepare_prompt
from utils.request_api import create_and_save_images, upscale_and_save_images
from utils.tagger import modelLoad, analysis

if getattr(sys, 'frozen', False):
    # PyInstaller でビルドされた場合
    dpath = os.path.dirname(sys.executable)
else:
    # 通常の Python スクリプトとして実行された場合
    dpath = os.path.dirname(sys.argv[0])

model = None
fastapi_url = None

def get_language_argument(default='jp'):
    for arg in sys.argv:
        if arg.startswith('--lang='):
            return arg.split('=')[1]
    return default

lang_util = Lang_Util(get_language_argument())


def make_output_path(dpath, filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")):
    output_dir = os.path.join(dpath, "output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return os.path.join(output_dir, filename + ".png")


class Application(TkinterDnD.Tk):
    def __init__(self, fastapi_url=None):
        super().__init__()
        self.fastapi_url = fastapi_url
        self.title("AI-Assistant")
        self.geometry("1200x600")
        self.tab_control = ttk.Notebook(self)
        self.img2img_tab = tk.Frame(self.tab_control)
        self.lineart_tab = tk.Frame(self.tab_control)
        self.lineart2_tab = tk.Frame(self.tab_control)
        self.normalmap_tab = tk.Frame(self.tab_control)
        self.lighting_tab = tk.Frame(self.tab_control)
        self.anime_shadow_tab = tk.Frame(self.tab_control)
        self.resize_tab = tk.Frame(self.tab_control)
        self.tab_control.add(self.img2img_tab, text=lang_util.get_text('img2img'))
        self.tab_control.add(self.lineart_tab, text=lang_util.get_text('lineart'))
        self.tab_control.add(self.lineart2_tab, text=lang_util.get_text('lineart2'))       
        self.tab_control.add(self.normalmap_tab, text=lang_util.get_text('normalmap'))
        self.tab_control.add(self.lighting_tab, text=lang_util.get_text('lighting'))
        self.tab_control.add(self.anime_shadow_tab, text=lang_util.get_text('anime_shadow'))
        self.tab_control.add(self.resize_tab, text=lang_util.get_text('resize'))
        self.tab_control.pack(expand=1, fill="both")
        self.img2img_mask_pil=None
        self.setup_img2img_tab()
        self.setup_lineart_tab()
        self.setup_lineart2_tab()
        self.setup_normalmap_tab()
        self.setup_lighting_tab()
        self.setup_anime_shadow_tab()
        self.setup_resize_tab()

        
    def setup_img2img_tab(self):
        self.left_frame = tk.Frame(self.img2img_tab)
        self.left_frame.grid(row=0, column=0, sticky='nsew')
        self.right_frame = tk.Frame(self.img2img_tab)
        self.right_frame.grid(row=0, column=1, sticky='nsew')

        self.img2img_tab.grid_columnconfigure(0, weight=0)  # 左フレームに重みを付ける
        self.img2img_tab.grid_columnconfigure(1, weight=0)  # 右フレームに重みを付ける

        self.images_frame = tk.Frame(self.left_frame)
        self.images_frame.grid(row=0, column=0, sticky='nsew', padx=20, pady=10)
        self.left_frame.grid_rowconfigure(0, weight=0)

        self.input_image_label = tk.Label(self.images_frame, text=lang_util.get_text("input_image"))
        self.input_image_label.grid(row=0, column=0, padx=10, sticky='w')
        self.img2img_input_image = tk.Canvas(self.images_frame, bg='grey', width=200, height=200)
        self.img2img_input_image.grid(row=1, column=0, padx=10, sticky='w')

        # キャンバスの上にボタンを配置
        self.screenshot_button = tk.Button(self.img2img_input_image, text=lang_util.get_text("screenshot"), command=self.screenshot)
        self.screenshot_button.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-10)

        # キャンバスにテキストを追加
        self.img2img_input_image.create_text(
            100, 100,
            text=lang_util.get_text("drag_drop_image"),
            fill="white",
            font=("Helvetica", 8)
        )

        # キャンバスにD&D機能を追加
        self.img2img_input_image.drop_target_register(DND_FILES)
        self.img2img_input_image.dnd_bind('<<Drop>>', self.load_image)

        self.img2img_mask_image_label = tk.Label(self.images_frame, text=lang_util.get_text("mask_image"))
        self.img2img_mask_image_label.grid(row=0, column=2, padx=10, sticky='w')
        self.img2img_mask_image = tk.Canvas(self.images_frame, bg='grey', width=200, height=200)
        self.img2img_mask_image.grid(row=1, column=2, padx=10, sticky='w')

        # キャンバスにテキストを追加
        self.img2img_mask_image.create_text(
            100, 100,
            text=lang_util.get_text("drag_drop_image"),
            fill="white",
            font=("Helvetica", 8)
        )

        # キャンバスにD&D機能を追加
        self.img2img_mask_image.drop_target_register(DND_FILES)
        self.img2img_mask_image.dnd_bind('<<Drop>>', self.load_mask)

        # ボタン設定
        self.buttons_frame = tk.Frame(self.left_frame)
        self.buttons_frame.grid(row=1, column=0, sticky="ew", padx=25)
        self.buttons_frame.grid_columnconfigure(0, weight=0)
        self.buttons_frame.grid_columnconfigure(1, weight=0)

        # maskボタンフィールド
        self.mask_frame = tk.Frame(self.buttons_frame)
        self.mask_frame.grid(row=0, column=2, sticky='ew', padx=32)
        self.mask_frame.grid_columnconfigure(0, weight=0)
        self.mask_frame.grid_columnconfigure(0, weight=0)
        self.mask_frame.grid_columnconfigure(0, weight=0)

        self.mask_button = tk.Button(self.mask_frame, text=lang_util.get_text("create"), width=5, command=self.make_mask)
        self.mask_button.grid(row=0, column=1, padx=5, sticky='ew')
        
        self.mask_button = tk.Button(self.mask_frame, text=lang_util.get_text("save"), width=5, command=self.save_mask)
        self.mask_button.grid(row=0, column=2, padx=5, sticky='ew')

        self.mask_button = tk.Button(self.mask_frame, text=lang_util.get_text("delete"), width=5,command=lambda: self.clear_mask(self.img2img_mask_image))
        self.mask_button.grid(row=0, column=3, padx=5, sticky='ew')

        # プロンプト設定
        self.analyze_prompt_button = tk.Button(self.buttons_frame, text=lang_util.get_text("analyze_prompt"), command=self.analyze_prompt, width=26)
        self.analyze_prompt_button.grid(row=0, column=0, padx=10, sticky='ew')

        self.label_prompt = tk.Label(self.left_frame, text=lang_util.get_text("prompt"))
        self.label_prompt.grid(row=2, column=0, sticky='w', padx=20)

        self.img2img_prompt_text = tk.Text(self.left_frame, height=5, width=88)
        self.img2img_prompt_text.grid(row=3, column=0, sticky='w', padx=20)

        self.label_negative_prompt = tk.Label(self.left_frame, text=lang_util.get_text("negative_prompt"))
        self.label_negative_prompt.grid(row=4, column=0, sticky='w', padx=20)

        self.img2img_negative_prompt_text = tk.Text(self.left_frame, height=5, width=88)
        self.img2img_negative_prompt_text.grid(row=5, column=0, sticky='w', padx=20)
        negative = "lowres, error, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts,  blurry"
        self.img2img_negative_prompt_text.insert(tk.END, negative)

        option_frame = tk.Frame(self.left_frame)
        option_frame.grid(row=6, column=0, sticky='ew', padx=20, pady=10)

        self.label_image_fidelity = tk.Label(option_frame, text=lang_util.get_text("image_fidelity"))
        self.label_image_fidelity.grid(row=0, column=0, sticky='w')

        self.img2img_slider_image_fidelity = tk.Scale(option_frame, from_=0, to=0.9, resolution=0.05, orient=tk.HORIZONTAL, length=250)
        self.img2img_slider_image_fidelity.grid(row=0, column=1, sticky='w')
        self.img2img_slider_image_fidelity.set(0.35)

        self.generate_button = tk.Button(self.left_frame, text=lang_util.get_text("generate"), command=self.generate_image_i2i)
        self.generate_button.grid(row=7, column=0, sticky='w', padx=20)

        self.output_frame = tk.Frame(self.right_frame)
        self.output_frame.grid(row=0, column=0, sticky='nsew', padx=20, pady=10)
        self.right_frame.grid_rowconfigure(0, weight=1)

        self.label_output_image = tk.Label(self.output_frame, text=lang_util.get_text("output_image"))
        self.label_output_image.pack(anchor='w', padx=0)

        self.img2img_output_image = tk.Canvas(self.output_frame, bg='grey', width=400, height=400)
        self.img2img_output_image.pack(anchor='w', padx=0)

        self.transfer_output_to_input_button = tk.Button(self.img2img_output_image, text=lang_util.get_text("transfer_to_lineart"), command=self.transfer_output_to_input)
        self.transfer_output_to_input_button.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-10)

        self.clipboard_button = tk.Button(self.img2img_output_image, text=lang_util.get_text("clipboard"), command=self.clipboard)
        self.clipboard_button.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-40)

        self.destination_button = tk.Button(self.output_frame, text=lang_util.get_text("output_destination"), command=self.open_output_dir)
        self.destination_button.place(anchor='w', x=0, y=445)
        
    def setup_lineart_tab(self):
        # 左フレーム設定
        self.left_frame = tk.Frame(self.lineart_tab)
        self.left_frame.grid(row=0, column=0, sticky="nsew")

        # 右フレーム設定
        self.right_frame = tk.Frame(self.lineart_tab)
        self.right_frame.grid(row=0, column=1, sticky="nsew")

        # images_frameの設定
        self.images_frame = tk.Frame(self.left_frame)
        self.images_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=10)

        # images_frameにおけるグリッド設定
        self.images_frame.grid_columnconfigure(0, weight=0)
        self.images_frame.grid_columnconfigure(1, weight=0)
        self.images_frame.grid_rowconfigure(0, weight=0)
        self.images_frame.grid_rowconfigure(1, weight=0)

        # イメージラベルとキャンバス設定
        self.input_image_label = tk.Label(self.images_frame, text=lang_util.get_text("input_image"))
        self.input_image_label.grid(row=0, column=0, padx=10, sticky='w')
        self.lineart_input_image = tk.Canvas(self.images_frame, bg='grey', width=200, height=200)
        self.lineart_input_image.grid(row=1, column=0, padx=10, sticky='w')

        # キャンバスの上にボタンを配置
        self.screenshot_button = tk.Button(self.lineart_input_image, text=lang_util.get_text("screenshot"), command=self.screenshot)
        self.screenshot_button.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-10)

        # キャンバスにテキストを追加
        self.lineart_input_image.create_text(
            100, 100,
            text=lang_util.get_text("drag_drop_image"),
            fill="white",
            font=("Helvetica", 8)
        )

        # キャンバスにD&D機能を追加
        self.lineart_input_image.drop_target_register(DND_FILES)
        self.lineart_input_image.dnd_bind('<<Drop>>', self.load_image)

        self.canny_image_label = tk.Label(self.images_frame, text=lang_util.get_text("canny_image"))
        self.canny_image_label.grid(row=0, column=1, padx=10, sticky='w')
        self.lineart_canny_image = tk.Canvas(self.images_frame, bg='grey', width=200, height=200)
        self.lineart_canny_image.grid(row=1, column=1, padx=10, sticky='w')

        # キャンバスにテキストを追加
        self.lineart_canny_image.create_text(
            100, 100,
            text=lang_util.get_text("drag_drop_image"),
            fill="white",
            font=("Helvetica", 8)
        )

        # キャンバスにD&D機能を追加
        self.lineart_canny_image.drop_target_register(DND_FILES)
        self.lineart_canny_image.dnd_bind('<<Drop>>', self.load_canny)

        # ボタン設定
        self.buttons_frame = tk.Frame(self.left_frame)
        self.buttons_frame.grid(row=1, column=0, sticky="ew", padx=25)
        self.buttons_frame.grid_columnconfigure(0, weight=0)
        self.buttons_frame.grid_columnconfigure(1, weight=0)

        self.analyze_prompt_button = tk.Button(self.buttons_frame, text=lang_util.get_text("analyze_prompt"), command=self.analyze_prompt, width=26)
        self.analyze_prompt_button.grid(row=0, column=0, padx=10, sticky='ew')

        self.threshold_frame = tk.Frame(self.buttons_frame)
        self.threshold_frame.grid(row=0, column=1, sticky='ew', padx=34)
        self.threshold_frame.grid_columnconfigure(0, weight=0)
        self.threshold_frame.grid_columnconfigure(1, weight=0)
        self.threshold_frame.grid_columnconfigure(2, weight=0)
        self.threshold_frame.grid_columnconfigure(3, weight=0)

        # スレッショルド入力フィールド
        self.low_threshold_var = tk.StringVar(self.threshold_frame, value='20')
        self.lineart_low_threshold_entry = tk.Entry(self.threshold_frame, width=5, justify=tk.CENTER, textvariable=self.low_threshold_var)
        self.lineart_low_threshold_entry.grid(row=0, column=0, padx=0, sticky='ew')

        self.label_threshold = tk.Label(self.threshold_frame, text="/")
        self.label_threshold.grid(row=0, column=1, padx=0, sticky='ew')

        self.high_threshold_var = tk.StringVar(self.threshold_frame, value='120')
        self.lineart_high_threshold_entry = tk.Entry(self.threshold_frame, width=5, justify=tk.CENTER, textvariable=self.high_threshold_var)
        self.lineart_high_threshold_entry.grid(row=0, column=2, padx=0, sticky='ew')

        self.canny_button = tk.Button(self.threshold_frame, text=lang_util.get_text("canny_creation"), width=10, command=self.make_canny)
        self.canny_button.grid(row=0, column=3, padx=10, sticky='ew')


        # プロンプト設定
        self.label_prompt = tk.Label(self.left_frame, text="prompt")
        self.label_prompt.grid(row=2, column=0, sticky='w', padx=20)

        self.lineart_prompt_text = tk.Text(self.left_frame, height=5, width=88)
        self.lineart_prompt_text.grid(row=3, column=0, sticky='w', padx=20)

        self.label_negative_prompt = tk.Label(self.left_frame, text=lang_util.get_text("negative_prompt"))
        self.label_negative_prompt.grid(row=4, column=0, sticky='w', padx=20)

        self.lineart_negative_prompt_text = tk.Text(self.left_frame, height=5, width=88)
        self.lineart_negative_prompt_text.grid(row=5, column=0, sticky='w', padx=20)
        negative = "lowres, error, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts,  blurry"
        self.lineart_negative_prompt_text.insert(tk.END, negative)

        # フィデリティ設定フレーム
        option_frame = tk.Frame(self.left_frame)
        option_frame.grid(row=6, column=0, sticky="ew", padx=20, pady=10)
        option_frame.grid_columnconfigure(0, weight=0)
        option_frame.grid_columnconfigure(1, weight=0)

        self.label_lineart_fidelity = tk.Label(option_frame, text=lang_util.get_text("lineart_fidelity"))
        self.label_lineart_fidelity.grid(row=0, column=0, sticky='w')

        self.lineart_slider_lineart_fidelity = tk.Scale(option_frame, from_=0.75, to=1.5, resolution=0.05, orient=tk.HORIZONTAL, length=250)
        self.lineart_slider_lineart_fidelity.grid(row=0, column=1, sticky='w', pady=0)
        self.lineart_slider_lineart_fidelity.set(1.0)

        self.label_lineart_bold = tk.Label(option_frame, text=lang_util.get_text("lineart_bold"))
        self.label_lineart_bold.grid(row=0, column=2, sticky='w')

        self.lineart_slider_lineart_bold = tk.Scale(option_frame, from_=0, to=1.0, resolution=0.05, orient=tk.HORIZONTAL, length=250)
        self.lineart_slider_lineart_bold.grid(row=0, column=3, sticky='w', pady=0)
        self.lineart_slider_lineart_bold.set(0)
       
        self.generate_button = tk.Button(self.left_frame, text=lang_util.get_text("generate"), command=self.generate_image_lineart)
        self.generate_button.grid(row=7, column=0, sticky='w', padx=20)

        self.output_frame = tk.Frame(self.right_frame)
        self.output_frame.grid(row=0, column=0, sticky='nsew', padx=20, pady=10)
        self.right_frame.grid_rowconfigure(0, weight=1)

        self.label_output_image = tk.Label(self.output_frame, text=lang_util.get_text("output_image"))
        self.label_output_image.pack(anchor='w', padx=0)

        self.lineart_output_image = tk.Canvas(self.output_frame, bg='grey', width=400, height=400)
        self.lineart_output_image.pack(anchor='w', padx=0)

        self.transfer_output_to_input_button = tk.Button(self.lineart_output_image, text=lang_util.get_text("transfer_to_normalmap"), command=self.transfer_output_to_input)
        self.transfer_output_to_input_button.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-10)

        self.clipboard_button = tk.Button(self.lineart_output_image, text=lang_util.get_text("clipboard"), command=self.clipboard)
        self.clipboard_button.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-40)

        self.destination_button = tk.Button(self.output_frame, text=lang_util.get_text("output_destination"), command=self.open_output_dir)
        self.destination_button.place(anchor='w', x=0, y=445)
        

    def setup_lineart2_tab(self):
        # 左フレーム設定
        self.left_frame = tk.Frame(self.lineart2_tab)
        self.left_frame.grid(row=0, column=0, sticky="nsew")

        # 右フレーム設定
        self.right_frame = tk.Frame(self.lineart2_tab)
        self.right_frame.grid(row=0, column=1, sticky="nsew")

        # images_frameの設定
        self.images_frame = tk.Frame(self.left_frame)
        self.images_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=10)

        # images_frameにおけるグリッド設定
        self.images_frame.grid_columnconfigure(0, weight=0)
        self.images_frame.grid_columnconfigure(1, weight=0)
        self.images_frame.grid_rowconfigure(0, weight=0)
        self.images_frame.grid_rowconfigure(1, weight=0)

        # イメージラベルとキャンバス設定
        self.input_image_label = tk.Label(self.images_frame, text=lang_util.get_text("input_image"))
        self.input_image_label.grid(row=0, column=0, padx=10, sticky='w')
        self.lineart2_input_image = tk.Canvas(self.images_frame, bg='grey', width=200, height=200)
        self.lineart2_input_image.grid(row=1, column=0, padx=10, sticky='w')

        # キャンバスの上にボタンを配置
        self.screenshot_button = tk.Button(self.lineart2_input_image, text=lang_util.get_text("screenshot"), command=self.screenshot)
        self.screenshot_button.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-10)

        # キャンバスにテキストを追加
        self.lineart2_input_image.create_text(
            100, 100,
            text=lang_util.get_text("drag_drop_image"),
            fill="white",
            font=("Helvetica", 8)
        )

        # キャンバスにD&D機能を追加
        self.lineart2_input_image.drop_target_register(DND_FILES)
        self.lineart2_input_image.dnd_bind('<<Drop>>', self.load_image)

        # ボタン設定
        self.buttons_frame = tk.Frame(self.left_frame)
        self.buttons_frame.grid(row=1, column=0, sticky="ew", padx=25)
        self.buttons_frame.grid_columnconfigure(0, weight=0)
        self.buttons_frame.grid_columnconfigure(1, weight=0)

        self.analyze_prompt_button = tk.Button(self.buttons_frame, text=lang_util.get_text("analyze_prompt"), command=self.analyze_prompt, width=26)
        self.analyze_prompt_button.grid(row=0, column=0, padx=10, sticky='ew')

        # プロンプト設定
        self.label_prompt = tk.Label(self.left_frame, text="prompt")
        self.label_prompt.grid(row=2, column=0, sticky='w', padx=20)

        self.lineart2_prompt_text = tk.Text(self.left_frame, height=5, width=88)
        self.lineart2_prompt_text.grid(row=3, column=0, sticky='w', padx=20)

        self.label_negative_prompt = tk.Label(self.left_frame, text=lang_util.get_text("negative_prompt"))
        self.label_negative_prompt.grid(row=4, column=0, sticky='w', padx=20)

        self.lineart2_negative_prompt_text = tk.Text(self.left_frame, height=5, width=88)
        self.lineart2_negative_prompt_text.grid(row=5, column=0, sticky='w', padx=20)
        negative = "lowres, error, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, blurry"
        self.lineart2_negative_prompt_text.insert(tk.END, negative)

        # フィデリティ設定フレーム
        option_frame = tk.Frame(self.left_frame)
        option_frame.grid(row=6, column=0, sticky="ew", padx=20, pady=10)
        option_frame.grid_columnconfigure(0, weight=0)
        option_frame.grid_columnconfigure(1, weight=0)

        self.label_lineart2_fidelity = tk.Label(option_frame, text=lang_util.get_text("lineart_fidelity"))
        self.label_lineart2_fidelity.grid(row=0, column=0, sticky='w')

        self.lineart2_slider_lineart_fidelity = tk.Scale(option_frame, from_=0.75, to=1.5, resolution=0.05, orient=tk.HORIZONTAL, length=250)
        self.lineart2_slider_lineart_fidelity.grid(row=0, column=1, sticky='w', pady=0)
        self.lineart2_slider_lineart_fidelity.set(1.0)

        self.label_lineart2_bold = tk.Label(option_frame, text=lang_util.get_text("lineart_bold"))
        self.label_lineart2_bold.grid(row=0, column=2, sticky='w')

        self.lineart2_slider_lineart_bold = tk.Scale(option_frame, from_=0, to=1.0, resolution=0.05, orient=tk.HORIZONTAL, length=250)
        self.lineart2_slider_lineart_bold.grid(row=0, column=3, sticky='w', pady=0)
        self.lineart2_slider_lineart_bold.set(0)
   
        self.generate_button = tk.Button(self.left_frame, text=lang_util.get_text("generate"), command=self.generate_image_lineart2)
        self.generate_button.grid(row=7, column=0, sticky='w', padx=20)

        self.output_frame = tk.Frame(self.right_frame)
        self.output_frame.grid(row=0, column=0, sticky='nsew', padx=20, pady=10)
        self.right_frame.grid_rowconfigure(0, weight=1)

        self.label_output_image = tk.Label(self.output_frame, text=lang_util.get_text("output_image"))
        self.label_output_image.pack(anchor='w', padx=0)

        self.lineart2_output_image = tk.Canvas(self.output_frame, bg='grey', width=400, height=400)
        self.lineart2_output_image.pack(anchor='w', padx=0)

        self.transfer_output_to_input_button = tk.Button(self.lineart2_output_image, text=lang_util.get_text("transfer_to_normalmap"), command=self.transfer_output_to_input)
        self.transfer_output_to_input_button.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-10)

        self.clipboard_button = tk.Button(self.lineart2_output_image, text=lang_util.get_text("clipboard"), command=self.clipboard)
        self.clipboard_button.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-40)

        self.destination_button = tk.Button(self.output_frame, text=lang_util.get_text("output_destination"), command=self.open_output_dir)
        self.destination_button.place(anchor='w', x=0, y=445)




    def setup_normalmap_tab(self):
        # 左フレーム設定
        self.left_frame = tk.Frame(self.normalmap_tab)
        self.left_frame.grid(row=0, column=0, sticky="nsew")

        # 右フレーム設定
        self.right_frame = tk.Frame(self.normalmap_tab)
        self.right_frame.grid(row=0, column=1, sticky="nsew")

        # images_frameの設定
        self.images_frame = tk.Frame(self.left_frame)
        self.images_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=10)

        # images_frameにおけるグリッド設定
        self.images_frame.grid_columnconfigure(0, weight=0)
        self.images_frame.grid_columnconfigure(1, weight=0)
        self.images_frame.grid_rowconfigure(0, weight=0)
        self.images_frame.grid_rowconfigure(1, weight=0)

        # イメージラベルとキャンバス設定
        self.input_image_label = tk.Label(self.images_frame, text=lang_util.get_text("input_lineart"))
        self.input_image_label.grid(row=0, column=0, padx=10, sticky='w')
        self.normalmap_input_image = tk.Canvas(self.images_frame, bg='grey', width=200, height=200)
        self.normalmap_input_image.grid(row=1, column=0, padx=10, sticky='w')

        # キャンバスの上にボタンを配置
        self.screenshot_button = tk.Button(self.normalmap_input_image, text=lang_util.get_text("screenshot"), command=self.screenshot)
        self.screenshot_button.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-10)

        # キャンバスにテキストを追加
        self.normalmap_input_image.create_text(
            100, 100,
            text=lang_util.get_text("drag_drop_image"),
            fill="white",
            font=("Helvetica", 8)
        )

        # キャンバスにD&D機能を追加
        self.normalmap_input_image.drop_target_register(DND_FILES)
        self.normalmap_input_image.dnd_bind('<<Drop>>', self.load_image)


        # ボタン設定
        self.buttons_frame = tk.Frame(self.left_frame)
        self.buttons_frame.grid(row=1, column=0, sticky="ew", padx=25)
        self.buttons_frame.grid_columnconfigure(0, weight=0)
        self.buttons_frame.grid_columnconfigure(1, weight=0)

        self.analyze_prompt_button = tk.Button(self.buttons_frame, text=lang_util.get_text("analyze_prompt"), command=self.analyze_prompt, width=26)
        self.analyze_prompt_button.grid(row=0, column=0, padx=10, sticky='ew')


        # プロンプト設定
        self.label_prompt = tk.Label(self.left_frame, text=lang_util.get_text("prompt"))
        self.label_prompt.grid(row=2, column=0, sticky='w', padx=20)

        self.normalmap_prompt_text = tk.Text(self.left_frame, height=5, width=88)
        self.normalmap_prompt_text.grid(row=3, column=0, sticky='w', padx=20)

        self.label_negative_prompt = tk.Label(self.left_frame, text=lang_util.get_text("negative_prompt"))
        self.label_negative_prompt.grid(row=4, column=0, sticky='w', padx=20)

        self.normalmap_negative_prompt_text = tk.Text(self.left_frame, height=5, width=88)
        self.normalmap_negative_prompt_text.grid(row=5, column=0, sticky='w', padx=20)
        negative = "lowres, error, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts,  blurry"
        self.normalmap_negative_prompt_text.insert(tk.END, negative)

        # フィデリティ設定フレーム
        option_frame = tk.Frame(self.left_frame)
        option_frame.grid(row=6, column=0, sticky="ew", padx=20, pady=10)
        option_frame.grid_columnconfigure(0, weight=0)
        option_frame.grid_columnconfigure(1, weight=0)

        self.label_lineart_fidelity = tk.Label(option_frame, text=lang_util.get_text("lineart_fidelity"))
        self.label_lineart_fidelity.grid(row=0, column=0, sticky='w')

        self.normalmap_slider_lineart_fidelity = tk.Scale(option_frame, from_=1.0, to=1.5, resolution=0.05, orient=tk.HORIZONTAL, length=250)
        self.normalmap_slider_lineart_fidelity.grid(row=0, column=1, sticky='w', pady=0)
        self.normalmap_slider_lineart_fidelity.set(1.25)

        self.generate_button = tk.Button(self.left_frame, text=lang_util.get_text("generate"), command=self.generate_image_normalmap)
        self.generate_button.grid(row=7, column=0, sticky='w', padx=20)

        self.output_frame = tk.Frame(self.right_frame)
        self.output_frame.grid(row=0, column=0, sticky='nsew', padx=20, pady=10)
        self.right_frame.grid_rowconfigure(0, weight=1)

        self.label_output_image = tk.Label(self.output_frame, text=lang_util.get_text("output_image"))
        self.label_output_image.pack(anchor='w', padx=0)

        self.normalmap_output_image = tk.Canvas(self.output_frame, bg='grey', width=400, height=400)
        self.normalmap_output_image.pack(anchor='w', padx=0)

        self.transfer = tk.Button(self.normalmap_output_image, text=lang_util.get_text("transfer_to_lighting"), command=self.transfer_output_to_input)
        self.transfer.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-10)

        self.clipboard_button = tk.Button(self.normalmap_output_image, text=lang_util.get_text("clipboard"), command=self.clipboard)
        self.clipboard_button.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-40)

        self.destination_button = tk.Button(self.output_frame, text=lang_util.get_text("output_destination"), command=self.open_output_dir)
        self.destination_button.place(anchor='w', x=0, y=445)

    def setup_lighting_tab(self):
        # 左フレームの設定
        self.left_frame = tk.Frame(self.lighting_tab)
        self.left_frame.grid(row=0, column=0, sticky="nsew")

        # 右フレームの設定
        self.right_frame = tk.Frame(self.lighting_tab)
        self.right_frame.grid(row=0, column=1, sticky="nsew")

        # images_frameの設定
        self.images_frame = tk.Frame(self.left_frame)
        self.images_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=10)

        # 画像ラベルとキャンバスの設定
        self.input_image_label = tk.Label(self.images_frame, text=lang_util.get_text("input_image"))
        self.input_image_label.grid(row=0, column=0, padx=10, sticky='w')
        self.lighting_input_image = tk.Canvas(self.images_frame, bg='grey', width=200, height=200)
        self.lighting_input_image.grid(row=1, column=0, padx=10, sticky='w')

        # キャンバスへのテキスト追加
        self.lighting_input_image.create_text(
            100, 100,
            text=lang_util.get_text("drag_drop_image"),
            fill="white",
            font=("Helvetica", 8)
        )

        # キャンバスへのD&D機能追加
        self.lighting_input_image.drop_target_register(DND_FILES)
        self.lighting_input_image.dnd_bind('<<Drop>>', self.load_image)

        # ボタン設定
        self.buttons_frame = tk.Frame(self.left_frame)
        self.buttons_frame.grid(row=1, column=0, sticky="ew", padx=25)
        self.buttons_frame.grid_columnconfigure(0, weight=0)
        self.buttons_frame.grid_columnconfigure(1, weight=0)

        # スライダーとラベルの設定
        controls = [
            ("Light Yaw", -180, 180, 60),
            ("Light Pitch", -90, 90, -60),
            ("Specular Power", 10, 100, 30),
            ("Normal Diffuse Strength", 0, 5.0, 1.00),
            ("Specular Highlights Strength", 0, 5.0, 0.80),
            ("Total Gain", 0, 1.0, 0.60)
        ]

        self.sliders = {}
        for idx, (label, frm, to, initial) in enumerate(controls):
            tk.Label(self.buttons_frame, text=label).grid(row=idx, column=0, sticky='w', padx=10)
            slider = tk.Scale(self.buttons_frame, from_=frm, to=to, resolution=-1 if frm < 0 else 0.01, orient='horizontal', length=400)
            slider.set(initial)
            slider.grid(row=idx, column=1, sticky='ew', padx=10)
            slider.bind("<ButtonRelease-1>", self.update_image_processing) 
            self.sliders[label] = slider
        
        # 画像保存ボタン
        self.save_button = tk.Button(self.buttons_frame, text=lang_util.get_text("save_image"), command=self.output_save)
        self.save_button.grid(row=len(controls), column=0, sticky='ew', padx=10, pady=10)

        # 出力画像の表示エリア設定
        self.output_frame = tk.Frame(self.right_frame)
        self.output_frame.grid(row=0, column=0, sticky="nsew", padx=115, pady=10)
        self.right_frame.grid_rowconfigure(0, weight=1)

        self.label_output_image = tk.Label(self.output_frame, text=lang_util.get_text("output_image"))
        self.label_output_image.pack(anchor='w', padx=0)
        
        # 光源オプションのドロップダウンメニューを追加します。
        self.lighting_options = [
            lang_util.get_text("light_source_directly_above"),
            lang_util.get_text("light_source_upper_left_diagonal"),
            lang_util.get_text("light_source_upper_right_diagonal"),
            lang_util.get_text("light_source_directly_left"),
            lang_util.get_text("light_source_directly_right"),
            lang_util.get_text("light_source_directly_below")
        ]
        self.selected_lighting = tk.StringVar(self.output_frame)
        self.selected_lighting.set(self.lighting_options[0])  # デフォルト値
        self.lighting_menu = tk.OptionMenu(self.output_frame, self.selected_lighting, *self.lighting_options, command=self.update_lighting)
        self.lighting_menu.pack(anchor='w', padx=1)

        self.lighting_output_image = tk.Canvas(self.output_frame, bg='grey', width=400, height=400)
        self.lighting_output_image.pack(anchor='w', padx=0)

        # 追加のUI要素
        self.transfer_output_to_input_button = tk.Button(self.lighting_output_image, text=lang_util.get_text("anime_shadow_tab_transfer"), command=self.transfer_output_to_input)
        self.transfer_output_to_input_button.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-10)

        self.clipboard_button = tk.Button(self.lighting_output_image, text=lang_util.get_text("clipboard"), command=self.clipboard)
        self.clipboard_button.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-40)

        self.destination_button = tk.Button(self.output_frame, text=lang_util.get_text("output_destination"), command=self.open_output_dir)
        self.destination_button.place(anchor='w', x=0, y=475)  


            
        
    def setup_anime_shadow_tab(self):
        # 左フレームの設定
        self.left_frame = tk.Frame(self.anime_shadow_tab)
        self.left_frame.grid(row=0, column=0, sticky="nsew")

        # 右フレームの設定
        self.right_frame = tk.Frame(self.anime_shadow_tab)
        self.right_frame.grid(row=0, column=1, sticky="nsew")

        # images_frameの設定
        self.images_frame = tk.Frame(self.left_frame)
        self.images_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=10)

        # images_frameでのグリッド設定
        self.images_frame.grid_columnconfigure(0, weight=0)
        self.images_frame.grid_columnconfigure(1, weight=0)
        self.images_frame.grid_rowconfigure(0, weight=0)
        self.images_frame.grid_rowconfigure(1, weight=0)

        # 画像ラベルとキャンバスの設定
        self.input_image_label = tk.Label(self.images_frame, text=lang_util.get_text("anime_shadow_input_image"))
        self.input_image_label.grid(row=0, column=0, padx=10, sticky='w')
        self.anime_shadow_input_image = tk.Canvas(self.images_frame, bg='grey', width=200, height=200)
        self.anime_shadow_input_image.grid(row=1, column=0, padx=10, sticky='w')

        # キャンバスへのテキスト追加
        self.anime_shadow_input_image.create_text(
            100, 100,
            text=lang_util.get_text("drag_drop_image"),
            fill="white",
            font=("Helvetica", 8)
        )

        # キャンバスへのD&D機能追加
        self.anime_shadow_input_image.drop_target_register(DND_FILES)
        self.anime_shadow_input_image.dnd_bind('<<Drop>>', self.load_image)

        # 画像ラベルとキャンバスの設定
        self.shadow_image_label = tk.Label(self.images_frame, text=lang_util.get_text("shadow_image"))
        self.shadow_image_label.grid(row=0, column=1, padx=10, sticky='w')
        self.shadow_image = tk.Canvas(self.images_frame, bg='grey', width=200, height=200)
        self.shadow_image.grid(row=1, column=1, padx=10, sticky='w')


        # 陰影キャンバスへのテキスト追加
        self.shadow_image.create_text(
            100, 100,
            text=lang_util.get_text("drag_drop_image"),
            fill="white",
            font=("Helvetica", 8)
        )

        # 陰影キャンバスへのD&D機能追加
        self.shadow_image.drop_target_register(DND_FILES)
        self.shadow_image.dnd_bind('<<Drop>>', self.load_shadow)

        # ボタン設定
        self.buttons_frame = tk.Frame(self.left_frame)
        self.buttons_frame.grid(row=1, column=0, sticky="ew", padx=25)
        self.buttons_frame.grid_columnconfigure(0, weight=0)
        self.buttons_frame.grid_columnconfigure(1, weight=0)

        self.analyze_prompt_button = tk.Button(self.buttons_frame, text=lang_util.get_text("analyze_prompt"), command=self.analyze_prompt, width=26)
        self.analyze_prompt_button.grid(row=0, column=0, padx=10, sticky='ew')

        # プロンプト設定
        self.label_prompt = tk.Label(self.left_frame, text=lang_util.get_text("prompt"))
        self.label_prompt.grid(row=2, column=0, sticky='w', padx=20)

        self.anime_shadow_prompt_text = tk.Text(self.left_frame, height=5, width=88)
        self.anime_shadow_prompt_text.grid(row=3, column=0, sticky='w', padx=20)

        self.label_negative_prompt = tk.Label(self.left_frame, text=lang_util.get_text("negative_prompt"))
        self.label_negative_prompt.grid(row=4, column=0, sticky='w', padx=20)

        self.anime_shadow_negative_prompt_text = tk.Text(self.left_frame, height=5, width=88)
        self.anime_shadow_negative_prompt_text.grid(row=5, column=0, sticky='w', padx=20)
        negative = "lowres, error, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, blurry"
        self.anime_shadow_negative_prompt_text.insert(tk.END, negative)

        # オプション設定フレーム
        option_frame = tk.Frame(self.left_frame)
        option_frame.grid(row=6, column=0, sticky="ew", padx=20, pady=10)
        option_frame.grid_columnconfigure(0, weight=0)
        option_frame.grid_columnconfigure(1, weight=0)

        self.label_shadow_choices = tk.Label(option_frame, text=lang_util.get_text("shadow_choices"))
        self.label_shadow_choices.grid(row=0, column=0, sticky='w')

        # プルダウンメニューを設定
        self.shadow_var = tk.StringVar(value='anime01')  # anime01をデフォルト値として設定
        shadow_choices = ['anime01', 'anime02']
        shadow_dropdown = ttk.Combobox(option_frame, textvariable=self.shadow_var, values=shadow_choices)
        shadow_dropdown.grid(row=0, column=0, padx=5, pady=5)
        shadow_dropdown.current(0)  # anime00 をデフォルト値として設定
       
        self.generate_button = tk.Button(self.left_frame, text=lang_util.get_text("generate"), command=self.generate_image_anime_shadow)
        self.generate_button.grid(row=7, column=0, sticky='w', padx=20)

        self.output_frame = tk.Frame(self.right_frame)
        self.output_frame.grid(row=0, column=0, sticky='nsew', padx=20, pady=10)
        self.right_frame.grid_rowconfigure(0, weight=1)

        self.label_output_image = tk.Label(self.output_frame, text=lang_util.get_text("output_image"))
        self.label_output_image.pack(anchor='w', padx=0)

        self.anime_shadow_output_image = tk.Canvas(self.output_frame, bg='grey', width=400, height=400)
        self.anime_shadow_output_image.pack(anchor='w', padx=0)

        self.clipboard_button = tk.Button(self.anime_shadow_output_image, text=lang_util.get_text("clipboard"), command=self.clipboard)
        self.clipboard_button.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-10)

        self.destination_button = tk.Button(self.output_frame, text=lang_util.get_text("output_destination"), command=self.open_output_dir)
        self.destination_button.place(anchor='w', x=0, y=445)


    def setup_resize_tab(self):
        # 左フレームの設定
        self.left_frame = tk.Frame(self.resize_tab)
        self.left_frame.grid(row=0, column=0, sticky="nsew")

        # 右フレームの設定
        self.right_frame = tk.Frame(self.resize_tab)
        self.right_frame.grid(row=0, column=1, sticky="nsew")

        # images_frameの設定
        self.images_frame = tk.Frame(self.left_frame)
        self.images_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=10)

        # images_frameでのグリッド設定
        self.images_frame.grid_columnconfigure(0, weight=0)
        self.images_frame.grid_columnconfigure(1, weight=0)
        self.images_frame.grid_rowconfigure(0, weight=0)
        self.images_frame.grid_rowconfigure(1, weight=0)

        # 画像ラベルとキャンバスの設定
        self.input_image_label = tk.Label(self.images_frame, text=lang_util.get_text("input_image"))
        self.input_image_label.grid(row=0, column=0, padx=10, sticky='w')
        self.resize_input_image = tk.Canvas(self.images_frame, bg='grey', width=200, height=200)
        self.resize_input_image.grid(row=1, column=0, padx=10, sticky='w')

        # キャンバスへのテキスト追加
        self.resize_input_image.create_text(
            100, 100,
            text=lang_util.get_text("drag_drop_image"),
            fill="white",
            font=("Helvetica", 8)
        )

        # キャンバスへのD&D機能追加
        self.resize_input_image.drop_target_register(DND_FILES)
        self.resize_input_image.dnd_bind('<<Drop>>', self.load_image)

        # ボタン設定
        self.buttons_frame = tk.Frame(self.left_frame)
        self.buttons_frame.grid(row=1, column=0, sticky="ew", padx=25)
        self.buttons_frame.grid_columnconfigure(0, weight=0)
        self.buttons_frame.grid_columnconfigure(1, weight=0)

        self.analyze_prompt_button = tk.Button(self.buttons_frame, text=lang_util.get_text("analyze_prompt"), command=self.analyze_prompt, width=26)
        self.analyze_prompt_button.grid(row=0, column=0, padx=10, sticky='ew')


        # プロンプト設定
        self.label_prompt = tk.Label(self.left_frame, text=lang_util.get_text("prompt"))
        self.label_prompt.grid(row=2, column=0, sticky='w', padx=20)

        self.resize_prompt_text = tk.Text(self.left_frame, height=5, width=88)
        self.resize_prompt_text.grid(row=3, column=0, sticky='w', padx=20)

        self.label_negative_prompt = tk.Label(self.left_frame, text=lang_util.get_text("negative_prompt"))
        self.label_negative_prompt.grid(row=4, column=0, sticky='w', padx=20)

        self.resize_negative_prompt_text = tk.Text(self.left_frame, height=5, width=88)
        self.resize_negative_prompt_text.grid(row=5, column=0, sticky='w', padx=20)
        negative = "lowres, error, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, blurry"
        self.resize_negative_prompt_text.insert(tk.END, negative)

        # リサイズ長辺設定フレーム
        max_length_frame = tk.Frame(self.left_frame)
        max_length_frame.grid(row=6, column=0, sticky="ew", padx=20, pady=10)
        max_length_frame.grid_columnconfigure(0, weight=0)
        max_length_frame.grid_columnconfigure(1, weight=0)

        self.label_max_length = tk.Label(max_length_frame, text=lang_util.get_text("max_length"))
        self.label_max_length.grid(row=0, column=0, sticky='w')

        self.max_length_entry_var = tk.StringVar()
        self.max_length_entry_var.set('1600')  # デフォルト値を設定

        # Entryウィジェットの作成
        self.max_length_entry = tk.Entry(max_length_frame, textvariable=self.max_length_entry_var, width=5)
        self.max_length_entry.grid(row=0, column=1, sticky='w', pady=0)

        # スケールウィジェットの作成
        self.max_length_scale = tk.Scale(max_length_frame, from_=1600, to=2880, resolution=1, orient=tk.HORIZONTAL, length=250)
        self.max_length_scale.grid(row=0, column=2, sticky='w', pady=0)
        self.max_length_scale.set(1600)

        # Entryウィジェットの内容が変更されたときに実行されるイベントバインディング
        self.max_length_entry.bind("<Return>", self.update_max_length_entry)

        #スケールウィジェットの内容が変更されたときに実行されるイベントバインディング
        self.max_length_scale.bind("<ButtonRelease-1>", self.update_max_length_scale)

        self.generate_button = tk.Button(self.left_frame, text=lang_util.get_text("generate"), command=self.generate_image_resize)
        self.generate_button.grid(row=7, column=0, sticky='w', padx=20)

        self.output_frame = tk.Frame(self.right_frame)
        self.output_frame.grid(row=0, column=0, sticky='nsew', padx=20, pady=10)
        self.right_frame.grid_rowconfigure(0, weight=1)

        self.label_output_image = tk.Label(self.output_frame, text=lang_util.get_text("output_image"))
        self.label_output_image.pack(anchor='w', padx=0)

        self.resize_output_image = tk.Canvas(self.output_frame, bg='grey', width=400, height=400)
        self.resize_output_image.pack(anchor='w', padx=0)

        self.clipboard_button = tk.Button(self.resize_output_image, text=lang_util.get_text("clipboard"), command=self.clipboard)
        self.clipboard_button.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-10)

        self.destination_button = tk.Button(self.output_frame, text=lang_util.get_text("output_destination"), command=self.open_output_dir)
        self.destination_button.place(anchor='w', x=0, y=445)



    def load_image(self, event):
        # 現在選択されているタブのインデックスを取得
        current_tab = self.tab_control.index(self.tab_control.select())

        # タブに応じて適切なキャンバスに画像をロード
        if current_tab == 0:  # img2imgタブと仮定
            self.img2img_image_path = event.data
            self.update_image(self.img2img_input_image, self.img2img_image_path)
        elif current_tab == 1:  # lineartタブと仮定
            self.lineart_image_path = event.data
            self.update_image(self.lineart_input_image, self.lineart_image_path)
        elif current_tab == 2:  # lineart2タブと仮定
            self.lineart2_image_path = event.data
            self.update_image(self.lineart2_input_image, self.lineart2_image_path)
        elif current_tab == 3:  # normalmapタブと仮定
            self.normalmap_image_path = event.data
            self.update_image(self.normalmap_input_image, self.normalmap_image_path)
        elif current_tab == 4:  # lightingタブと仮定
            self.lighting_image_path = event.data
            self.update_image(self.lighting_input_image, self.lighting_image_path)
            self.current_image_tensor = to_tensor(Image.open(self.lighting_image_path))
        elif current_tab == 5:  # anime_shadowタブと仮定
            self.anime_shadow_image_path = event.data
            self.update_image(self.anime_shadow_input_image, self.anime_shadow_image_path)
        elif current_tab == 6:  # resizeタブと仮定
            self.resize_image_path = event.data
            self.update_image(self.resize_input_image, self.resize_image_path)


    def load_mask(self, event):
        # 現在選択されているタブのインデックスを取得
        current_tab = self.tab_control.index(self.tab_control.select())

        # タブに応じて適切なキャンバスに画像をロード
        if current_tab == 0:  #img2imgタブと仮定
            self.img2img_mask_path = event.data
            self.img2img_mask_pil = Image.open(self.img2img_mask_path)
            self.update_image(self.img2img_mask_image, self.img2img_mask_path)
            

    def load_canny(self, event):
        # 現在選択されているタブのインデックスを取得
        current_tab = self.tab_control.index(self.tab_control.select())

        # タブに応じて適切なキャンバスに画像をロード
        if current_tab == 1:  # lineartタブと仮定
            self.lineart_canny_path = event.data
            self.update_image(self.lineart_canny_image, self.lineart_canny_path)
 

    def load_shadow(self, event):
        # 現在選択されているタブのインデックスを取得
        current_tab = self.tab_control.index(self.tab_control.select())

        # タブに応じて適切なキャンバスに画像をロード
        if current_tab == 5:  # anime_shadowタブと仮定
            self.anime_shadow_path = event.data
            self.update_image(self.shadow_image, self.anime_shadow_path)

    def update_image(self, canvas, image_path):
        if image_path:
            # 画像をRGB形式で開く (透過部分を考慮)
            img = Image.open(image_path)
            img = img.convert("RGBA")  # RGBAに変換して透過情報を保持

            width, height = img.size
            max_size = (200, 200)

            # 画像サイズを調整
            if width > height:
                new_width = 200
                new_height = int(height * (200 / width))
            else:
                new_height = 200
                new_width = int(width * (200 / height))

            img = img.resize((new_width, new_height), Image.LANCZOS)

            # 透過部分を白色で塗りつぶすキャンバスを作成
            canvas_image = Image.new('RGBA', max_size, (255, 255, 255, 255))
            # 画像を中央に配置
            canvas_image.paste(img, ((max_size[0] - new_width) // 2, (max_size[1] - new_height) // 2), img)
            # RGBAからRGBに変換し、透過部分を白色にする
            img = canvas_image.convert("RGB")

            # Tkinterで使用できる形式に変換
            photo = ImageTk.PhotoImage(img)
            # 画像をキャンバスに描画
            canvas.create_image(100, 100, image=photo, anchor='center')
            # ガベージコレクションを防ぐために画像の参照を保持
            canvas.image = photo

 
    def update_image_processing(self, event=None):
        # 現在の画像テンソルが存在するか確認します
        if not hasattr(self, 'current_image_tensor'):
            return  # 画像がロードされていなければ何もしない

        # スライダーから値を取得
        light_yaw = self.sliders["Light Yaw"].get()  # ライトのYaw値
        light_pitch = self.sliders["Light Pitch"].get()  # ライトのPitch値
        specular_power = self.sliders["Specular Power"].get()  # スペキュラーの強さ
        normal_diffuse_strength = self.sliders["Normal Diffuse Strength"].get()  # 拡散の強さ
        specular_highlights_strength = self.sliders["Specular Highlights Strength"].get()  # ハイライトの強さ
        total_gain = self.sliders["Total Gain"].get()  # 全体の輝度調整

        # ライティング効果を適用するために関数を呼び出します
        output_tensor = self.apply_lighting_effects(
            self.current_image_tensor, 
            light_yaw, 
            light_pitch, 
            specular_power, 
            normal_diffuse_strength, 
            specular_highlights_strength, 
            total_gain
        )

        # テンソルから画像へ変換
        self.lightinged_pil = self.convert_tensor_to_image(output_tensor)

        # 出力画像を表示
        self.display_output_image(self.lightinged_pil)

    def update_lighting(self, selection):
        # 光源オプションに対応する Yaw と Pitch の値
        lighting_settings = {
            "光源：真上": {"Light Yaw": 60, "Light Pitch": -60},
            "光源：左斜め上": {"Light Yaw": 40, "Light Pitch": -60},
            "光源：右斜め上": {"Light Yaw": 60, "Light Pitch": -40},
            "光源：左横": {"Light Yaw": 0, "Light Pitch": 0},
            "光源：右横": {"Light Yaw": 90, "Light Pitch": 0},
            "光源：真下": {"Light Yaw": 45, "Light Pitch": 0}
        }

        # 現在選択されているオプションに基づいてスライダー値を更新
        if selection in lighting_settings:
            settings = lighting_settings[selection]
            self.sliders["Light Yaw"].set(settings["Light Yaw"])
            self.sliders["Light Pitch"].set(settings["Light Pitch"])

            # 画像処理の更新関数を呼び出す
            dummy_event = None
            self.update_image_processing(dummy_event)
        
    def apply_lighting_effects(self, input_tensor, light_yaw, light_pitch, specular_power, normal_diffuse_strength, specular_highlights_strength, total_gain):
        # 元の次元数を記録する
        original_dim = input_tensor.dim()

        # 入力テンソルが最低でも4次元であることを保証する（バッチ次元がなければ追加する）
        if original_dim == 3:
            input_tensor = input_tensor.unsqueeze(0)  # バッチ次元を追加

        # 入力テンソルに3つ以上のチャンネルがある場合、追加のチャンネルをアルファと仮定し削除する
        if input_tensor.shape[1] > 3:
            input_tensor = input_tensor[:, :3, :, :]  # 最初の3チャンネルのみを保持

        # 入力テンソルを正規化して法線ベクトルを取得する
        normal_tensor = torch.nn.functional.normalize(input_tensor, dim=1)  # チャンネル次元に沿って正規化

        # 光の方向ベクトルを計算する
        light_direction = self.euler_to_vector(light_yaw, light_pitch, 0)
        light_direction = light_direction.to(input_tensor.device)  # 同じデバイスを保証する

        # 光の方向とカメラの方向を入力テンソルの次元に合わせて拡張する
        batch_size, _, height, width = input_tensor.shape
        light_direction = light_direction.view(1, 3, 1, 1).expand(batch_size, -1, height, width)
        camera_direction = torch.tensor([0, 0, 1], dtype=torch.float32, device=input_tensor.device)
        camera_direction = camera_direction.view(1, 3, 1, 1).expand(batch_size, -1, height, width)

        # 拡散成分を計算する
        diffuse = torch.sum(normal_tensor * light_direction, dim=1, keepdim=True)
        diffuse = torch.clamp(diffuse, 0, 1)

        # 鏡面成分を計算する
        half_vector = torch.nn.functional.normalize(light_direction + camera_direction, dim=1)
        specular = torch.sum(normal_tensor * half_vector, dim=1, keepdim=True)
        specular = torch.pow(torch.clamp(specular, 0, 1), specular_power)

        # 拡散成分と鏡面成分を組み合わせて、強度とゲインを適用する
        output_tensor = (diffuse * normal_diffuse_strength + specular * specular_highlights_strength) * total_gain
        output_tensor = output_tensor.squeeze(1)  # keepdim=Trueで追加されたチャンネル次元を削除

        # 初めに追加されたバッチ次元があれば削除する
        if original_dim == 3:
            output_tensor = output_tensor.squeeze(0)

        return output_tensor


    def convert_tensor_to_image(self, tensor):
        # テンソルから画像への変換
        image = to_pil_image(tensor.squeeze(0))
        return image            

    def euler_to_vector(self, yaw, pitch, roll):
        # オイラー角から方向ベクトルを計算
        yaw_rad = np.radians(yaw)
        pitch_rad = np.radians(pitch)
        roll_rad = np.radians(roll)
        
        cos_pitch = np.cos(pitch_rad)
        sin_pitch = np.sin(pitch_rad)
        cos_yaw = np.cos(yaw_rad)
        sin_yaw = np.sin(yaw_rad)
        
        direction = np.array([
            sin_yaw * cos_pitch,
            -sin_pitch,
            cos_yaw * cos_pitch
        ])
        return torch.from_numpy(direction).float()

    def update_max_length_entry(self, event):
        # Entryからの入力値を取得し、整数に変換
        new_value = int(self.max_length_entry.get())
        # スケールの値を更新
        self.max_length_scale.set(new_value)
        
    def update_max_length_scale(self, event):
        # スケールからの入力値を取得し、整数に変換
        new_value = int(self.max_length_scale.get())
        # Entryの値を更新
        # スケールからの入力値を取得し、整数に変換して Entry の値を更新
        self.max_length_entry_var.set(new_value)


    def output_save(self):
        dpath = os.getcwd()
        dt_now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_path = make_output_path(dpath, f"output_image_{dt_now}.png")

        if hasattr(self, 'lightinged_pil'):
            self.lightinged_pil.save(file_path)
            print(f"Image saved successfully at {file_path}")
        else:
            print("No image available to save. Check if the image is being set correctly.")

    


    def make_mask(self):
        # 現在選択されているタブのインデックスを取得
        current_tab = self.tab_control.index(self.tab_control.select())

        # タブに応じて適切なキャンバスに画像をロード
        if current_tab == 0:  # img2imgタブと仮定
            image_path = self.img2img_image_path
            mask_img = self.img2img_mask_image
            mask = mask_process(image_path)
            self.img2img_mask_pil = mask        

        width, height = mask.size
        max_size = (200, 200)

        # アスペクト比を保ちつつ、長い方の辺を200に収める
        if width > height:
            new_width = 200
            new_height = int(height * (200 / width))
        else:
            new_height = 200
            new_width = int(width * (200 / height))
        
        mask = mask.resize((new_width, new_height), Image.LANCZOS)
        canvas = Image.new('RGBA', max_size, (0, 0, 0, 255))  # 黒背景のキャンバスを作成
        canvas.paste(mask, ((max_size[0] - new_width) // 2, (max_size[1] - new_height) // 2))
        mask = canvas.convert("RGB")  # 最終的な画像をRGB形式に変換

        photo = ImageTk.PhotoImage(mask)
        # 以前の画像があれば削除
        if hasattr(self, 'image_on_canvas'):
            mask_img.delete(self.image_on_canvas)
        # Canvasに画像を配置
        self.image_on_canvas = mask_img.create_image(0, 0, image=photo, anchor='nw')
        mask_img.image = photo  # この行は画像参照を保持するために重要



    def make_canny(self):
        # 現在選択されているタブのインデックスを取得
        current_tab = self.tab_control.index(self.tab_control.select())

        # タブに応じて適切なキャンバスに画像をロード
        if current_tab == 1:  # lineartタブと仮定
            image_path = self.lineart_image_path
            threshold1 = int(self.lineart_low_threshold_entry.get())
            threshold2 = int(self.lineart_high_threshold_entry.get())
            canny_img = self.lineart_canny_image
            canny = canny_process(image_path, threshold1, threshold2)
            self.lineart_canny_pil = canny
            
        width, height = canny.size
        max_size = (200, 200)

        # アスペクト比を保ちつつ、長い方の辺を200に収める
        if width > height:
            new_width = 200
            new_height = int(height * (200 / width))
        else:
            new_height = 200
            new_width = int(width * (200 / height))
        
        canny = canny.resize((new_width, new_height), Image.LANCZOS)
        canvas = Image.new('RGBA', max_size, (0, 0, 0, 255))  # 黒背景のキャンバスを作成
        canvas.paste(canny, ((max_size[0] - new_width) // 2, (max_size[1] - new_height) // 2))
        canny = canvas.convert("RGB")  # 最終的な画像をRGB形式に変換

        photo = ImageTk.PhotoImage(canny)
        # 以前の画像があれば削除
        if hasattr(self, 'image_on_canvas'):
            canny_img.delete(self.image_on_canvas)
        # Canvasに画像を配置
        self.image_on_canvas = canny_img.create_image(0, 0, image=photo, anchor='nw')
        canny_img.image = photo  # この行は画像参照を保持するために重要

    def clipboard(self):
        # 現在選択されているタブのインデックスを取得
        current_tab = self.tab_control.index(self.tab_control.select())

        # タブに応じて適切なキャンバスに画像をロード
        if current_tab == 0:  # img2imgタブと仮定
            output_path = self.img2img_output_path
        elif current_tab == 1:  # lineartタブと仮定
            output_path = self.lineart_output_path
        elif current_tab == 2:  # lineart2タブと仮定
            output_path = self.lineart2_output_path
        elif current_tab == 3:  # normalmapタブと仮定
            output_path = self.normalmap_output_path
        elif current_tab == 4:  # lightingタブと仮定
            self.lighting_output_path = make_output_path(dpath, "lighting.png")
            if hasattr(self, 'lightinged_pil'):
                self.lightinged_pil.save(self.lighting_output_path)
                output_path = self.lighting_output_path
        elif current_tab == 5:  # anime_shadowタブと仮定
            output_path = self.anime_shadow_output_path
        elif current_tab == 6:  # resizeタブと仮定
            output_path = self.resize_output_path
        
        image = Image.open(output_path)
        output = BytesIO()
        image.convert("RGB").save(output, "BMP")
        data = output.getvalue()[14:] 
    
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard() 
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()
        output.close()



    def display_output_image(self, output_pil):
        width, height = output_pil.size
        max_size = (400, 400)

        if width > height:
            new_width = 400
            new_height = int(height * (400 / width))
        else:
            new_height = 400
            new_width = int(width * (400 / height))
        
        img = output_pil.resize((new_width, new_height), Image.LANCZOS)
        canvas_image = Image.new('RGBA', max_size, (255, 255, 255, 255))
        canvas_image.paste(img, ((max_size[0] - new_width) // 2, (max_size[1] - new_height) // 2))
        img = canvas_image.convert("RGB")
        photo = ImageTk.PhotoImage(img)

        # 現在選択されているタブのインデックスを取得
        current_tab = self.tab_control.index(self.tab_control.select())

        # タブに応じて適切なキャンバスに画像を更新
        if current_tab == 0:  # img2imgタブと仮定
            self.img2img_output_image.create_image(0, 0, image=photo, anchor='nw')
            self.img2img_output_image.image = photo
        elif current_tab == 1:  # lineartタブと仮定
            self.lineart_output_image.create_image(0, 0, image=photo, anchor='nw')
            self.lineart_output_image.image = photo
        elif current_tab == 2:  # lineart2タブと仮定
            self.lineart2_output_image.create_image(0, 0, image=photo, anchor='nw')
            self.lineart2_output_image.image = photo
        elif current_tab == 3:  # normalmapタブと仮定
            self.normalmap_output_image.create_image(0, 0, image=photo, anchor='nw')
            self.normalmap_output_image.image = photo
        elif current_tab == 4: 
            self.lighting_output_image.create_image(0, 0, image=photo, anchor='nw')
            self.lighting_output_image.image = photo
        elif current_tab == 5:  # anime_shadowタブと仮定
            self.anime_shadow_output_image.create_image(0, 0, image=photo, anchor='nw')
            self.anime_shadow_output_image.image = photo
        elif current_tab == 6:  # resizeタブと仮定
            self.resize_output_image.create_image(0, 0, image=photo, anchor='nw')
            self.resize_output_image.image = photo


    def open_output_dir(self):
        output_dir = os.path.join(dpath, "output")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        os.startfile(output_dir)

    def apply_mask(self):
        # 現在選択されているタブのインデックスを取得
        current_tab = self.tab_control.index(self.tab_control.select())

        # タブに応じて適切なキャンバスに画像をロード
        if current_tab == 0:  # img2imgタブと仮定
            image_path = self.img2img_image_path

        mask = mask_process(image_path)
        self.show_processed_image(mask)

    def save_mask(self):
        # 現在選択されているタブのインデックスを取得
        current_tab = self.tab_control.index(self.tab_control.select())

        # タブに応じて適切なキャンバスに画像をロード
        if current_tab == 0:  # img2imgタブと仮定
            image_path = self.img2img_image_path

        masks_dir = os.path.join(dpath, "output")
        if not os.path.exists(masks_dir):
            os.makedirs(masks_dir)
        img_name = os.path.splitext(os.path.basename(image_path))[0]
        mask_path = os.path.join(masks_dir, img_name + "_mask" + ".png")

        # 現在選択されているタブのインデックスを取得
        current_tab = self.tab_control.index(self.tab_control.select())
        # タブに応じて適切なキャンバスに画像をロード
        if current_tab == 0:  # img2imgタブと仮定
           mask_pil = self.img2img_mask_pil
        mask_pil.save(mask_path)
        
    def clear_mask(self, canvas):
        current_tab = self.tab_control.index(self.tab_control.select())
        if current_tab == 0:  # img2imgタブと仮定
            self.img2img_mask_pil = None

        # 既存のキャンバスをクリア
        canvas.delete("all")  # キャンバス上のすべてのアイテムを削除
        # キャンバスにテキストを再追加
        canvas.create_text(
            100, 100,
            text="画像をここにドラッグ＆ドロップ",
            fill="white",
            font=("Helvetica", 8)
        )
       
    def screenshot(self):
        sc = ScreenCapture()
        image_path = sc.listen()
        # 現在選択されているタブのインデックスを取得
        current_tab = self.tab_control.index(self.tab_control.select())

        # タブに応じて適切なキャンバスに画像をロード
        if current_tab == 0:  # img2imgタブと仮定
            self.img2img_image_path = image_path
            self.update_image(self.img2img_input_image, self.img2img_image_path)
        elif current_tab == 1:  # lineartタブと仮定
            self.lineart_image_path = image_path
            self.update_image(self.lineart_input_image, self.lineart_image_path)
        elif current_tab == 2:  # lineart2タブと仮定
            self.lineart2_image_path = image_path
            self.update_image(self.lineart2_input_image, self.lineart2_image_path)
        elif current_tab == 3:  # normalmapタブと仮定
            self.normalmap_image_path = image_path
            self.update_image(self.normalmap_input_image, self.normalmap_image_path)

        
    def transfer_output_to_input(self):
        # 現在選択されているタブのインデックスを取得
        current_tab = self.tab_control.index(self.tab_control.select())

        # タブに応じて適切なキャンバスに画像をロード
        if current_tab == 0:  # img2imgタブと仮定
            self.lineart_image_path = self.img2img_output_path
            self.update_image(self.lineart_input_image, self.lineart_image_path)
        elif current_tab == 1:  # lineartタブと仮定
            self.normalmap_image_path = self.lineart_output_path
            self.update_image(self.normalmap_input_image, self.normalmap_image_path)
        elif current_tab == 2:  # lineart2タブと仮定
            self.normalmap_image_path = self.lineart2_output_path
            self.update_image(self.normalmap_input_image, self.normalmap_image_path)
        elif current_tab == 3:  # normalmapタブと仮定
            self.lighting_image_path = self.normalmap_output_path
            self.update_image(self.lighting_input_image, self.lighting_image_path)
            self.current_image_tensor = to_tensor(Image.open(self.lighting_image_path))
        elif current_tab == 4:  # lightingタブと仮定
            lighting_output_path = make_output_path(dpath, "lighting.png")

            if hasattr(self, 'lightinged_pil'):
                self.lightinged_pil.save(lighting_output_path)

            self.update_image(self.shadow_image, lighting_output_path)
            self.anime_shadow_path = lighting_output_path

    def analyze_prompt(self):
        # 現在選択されているタブのインデックスを取得
        current_tab = self.tab_control.index(self.tab_control.select())

        # タブに応じて適切なキャンバスに画像をロード
        if current_tab == 0:  # img2imgタブと仮定
            image_path = self.img2img_image_path
            prompt_text = self.img2img_prompt_text
        elif current_tab == 1:  # lineartタブと仮定
            image_path = self.lineart_image_path
            prompt_text = self.lineart_prompt_text
        elif current_tab == 2:  # lineart2タブと仮定
            image_path = self.lineart2_image_path
            prompt_text = self.lineart2_prompt_text
        elif current_tab == 3:  # normalmapタブと仮定
            image_path = self.normalmap_image_path
            prompt_text = self.normalmap_prompt_text
        elif current_tab == 5:  # anime_shadowタブと仮定
            image_path = self.anime_shadow_image_path
            prompt_text = self.anime_shadow_prompt_text
        elif current_tab == 6:  # resizeタブと仮定
            image_path = self.resize_image_path
            prompt_text = self.resize_prompt_text

        global model
        model_dir = os.path.join(dpath, 'models/tagger')
        if model is None:
            model = modelLoad(model_dir)
        tags = analysis(image_path, model_dir, model)

        # タグの処理
        tags_list = tags.split(", ")
        if current_tab not in [0, 6]:
            tags_list = remove_color(tags_list)
            tags_list = remove_duplicates(tags_list)
        tags_joined = ", ".join(tags_list)

        prompt_text.delete("1.0", tk.END)
        prompt_text.insert("1.0", tags_joined)

    def generate_image_i2i(self):
        prompt = "masterpiece, best quality, " + self.img2img_prompt_text.get("1.0", tk.END).strip()
        prompt_list = prompt.split(", ")
        # 重複を除去
        unique_tags = remove_duplicates(prompt_list)
        prompt = ", ".join(unique_tags)
        nega = self.img2img_negative_prompt_text.get("1.0", tk.END).strip()
        base_pil = Image.open(self.img2img_image_path).convert("RGBA")
        image_size = base_pil.size
        base_pil = resize_image_aspect_ratio(base_pil)
        white_bg = Image.new("RGBA", base_pil.size, "WHITE")
        white_bg.paste(base_pil, mask=base_pil)
        base_pil = resize_image_aspect_ratio(white_bg).convert("RGB")
        canny_pil = None
        if self.img2img_mask_pil is None:
            mask_pil =base_generation(base_pil.size, (255, 255, 255, 255)).convert("RGB")
        else:
            mask_pil =self.img2img_mask_pil.resize(base_pil.size, Image.LANCZOS).convert("RGB")         
        image_fidelity = 1 - float(self.img2img_slider_image_fidelity.get())
        lineart_fidelity = None
        self.img2img_output_path = make_output_path(dpath)
        mode = "i2i"
        output_pil = create_and_save_images(self.fastapi_url, prompt, nega, base_pil, canny_pil, mask_pil, image_size, self.img2img_output_path, mode, image_fidelity, lineart_fidelity)
        self.display_output_image(output_pil)


    def generate_image_lineart(self):
        lineart_bold = float(self.lineart_slider_lineart_bold.get())
        lineart = 1 - lineart_bold
        prompt = "masterpiece, best quality, <lora:sdxl_BWLine:" + str(lineart) + ">, <lora:sdxl_BW_bold_Line:" + str(lineart_bold) + ">, monochrome, lineart, white background, " + self.lineart_prompt_text.get("1.0", tk.END).strip()
        execute_tags = ["sketch"]
        prompt = prepare_prompt(execute_tags, prompt)
        nega = self.lineart_negative_prompt_text.get("1.0", tk.END).strip()
        base_pil = Image.open(self.lineart_image_path).convert("RGBA")
        image_size = base_pil.size
        base_pil = resize_image_aspect_ratio(base_pil)
        white_bg = Image.new("RGBA", base_pil.size, "WHITE")
        white_bg.paste(base_pil, mask=base_pil)
        base_pil = resize_image_aspect_ratio(white_bg).convert("RGB")
        canny_pil = self.lineart_canny_pil.resize(base_pil.size, Image.LANCZOS).convert("RGB")
        mask_pil = base_generation(base_pil.size, (255, 255, 255, 255)).convert("RGB")
        white_base_pil = base_generation(base_pil.size, (255, 255, 255, 255)).convert("RGB") 
        image_fidelity = 1.0
        lineart_fidelity = float(self.lineart_slider_lineart_fidelity.get())
        self.lineart_output_path  = make_output_path(dpath)
        mode = "lineart"
        output_pil = create_and_save_images(self.fastapi_url, prompt, nega, white_base_pil, canny_pil, mask_pil, image_size, self.lineart_output_path, mode, image_fidelity, lineart_fidelity)
        self.display_output_image(output_pil)

    def generate_image_lineart2(self):
        lineart2_bold = float(self.lineart2_slider_lineart_bold.get())
        lineart2 = 1 - lineart2_bold
        prompt = "masterpiece, best quality, <lora:sdxl_BWLine:" + str(lineart2) + ">, <lora:sdxl_BW_bold_Line:" + str(lineart2_bold) + ">, monochrome, lineart2, white background, " + self.lineart2_prompt_text.get("1.0", tk.END).strip()
        execute_tags = ["sketch"]
        prompt = prepare_prompt(execute_tags, prompt)
        nega = self.lineart2_negative_prompt_text.get("1.0", tk.END).strip()
        base_pil = Image.open(self.lineart2_image_path).convert("RGBA")
        image_size = base_pil.size
        base_pil = resize_image_aspect_ratio(base_pil)
        white_bg = Image.new("RGBA", base_pil.size, "WHITE")
        white_bg.paste(base_pil, mask=base_pil)
        base_pil = resize_image_aspect_ratio(white_bg).convert("RGB")
        flatLine_pil = flatline_process(self.lineart2_image_path).resize(base_pil.size, Image.LANCZOS).convert("RGB")
        mask_pil = base_generation(base_pil.size, (255, 255, 255, 255)).convert("RGB")
        white_base_pil = base_generation(base_pil.size, (255, 255, 255, 255)).convert("RGB") 
        image_fidelity = 1.0
        lineart2_fidelity = float(self.lineart2_slider_lineart_fidelity.get())
        self.lineart2_output_path  = make_output_path(dpath)
        mode = "lineart2"
        output_pil = create_and_save_images(self.fastapi_url, prompt, nega, white_base_pil, flatLine_pil, mask_pil, image_size, self.lineart2_output_path, mode, image_fidelity, lineart2_fidelity)
        self.display_output_image(output_pil)

    def generate_image_normalmap(self):
        prompt = "masterpiece, best quality, normal map, <lora:sdxl-testlora-normalmap_04b_dim32:1.2>" + self.normalmap_prompt_text.get("1.0", tk.END).strip()
        execute_tags = ["monochrome", "greyscale", "lineart", "white background", "sketch"]
        prompt = prepare_prompt(execute_tags, prompt)
        nega = self.normalmap_negative_prompt_text.get("1.0", tk.END).strip()
        base_pil = Image.open(self.normalmap_image_path).convert("RGBA")
        image_size = base_pil.size
        base_pil = resize_image_aspect_ratio(base_pil)
        base_pil = base_generation(base_pil.size, (150, 110, 255, 255)).convert("RGB")         
        invert_pil = invert_process(self.normalmap_image_path).resize(base_pil.size, Image.LANCZOS).convert("RGB")
        mask_pil =base_generation(base_pil.size, (255, 255, 255, 255)).convert("RGB")
        image_fidelity = 1.0
        lineart_fidelity = float(self.normalmap_slider_lineart_fidelity.get())
        self.normalmap_output_path = make_output_path(dpath)
        mode = "normalmap"
        output_pil = create_and_save_images(self.fastapi_url, prompt, nega, base_pil, invert_pil, mask_pil, image_size, self.normalmap_output_path, mode, image_fidelity, lineart_fidelity)
        self.display_output_image(output_pil)
          
    def generate_image_anime_shadow(self):
        shadow_choice = self.shadow_var.get()
        prompt = f"masterpiece, best quality, <lora:{shadow_choice}:1>, monochrome, greyscale, " + self.anime_shadow_prompt_text.get("1.0", tk.END).strip()
        execute_tags = ["lineart", "sketch"]
        prompt = prepare_prompt(execute_tags, prompt)
        nega = self.anime_shadow_negative_prompt_text.get("1.0", tk.END).strip()
        base_pil = Image.open(self.anime_shadow_image_path).convert("RGBA")
        image_size = base_pil.size
        base_pil = resize_image_aspect_ratio(base_pil)
        white_bg = Image.new("RGBA", base_pil.size, "WHITE")
        white_bg.paste(base_pil, mask=base_pil)
        base_pil = resize_image_aspect_ratio(white_bg).convert("RGB")
        invert_pil = invert_process(self.anime_shadow_image_path).convert("RGB")
        shadow_pil = Image.open(self.anime_shadow_path).convert("RGBA").resize(base_pil.size, Image.LANCZOS)
        shadow_line_pil = multiply_images(base_pil, shadow_pil).convert("RGB")
        image_fidelity = 1.0
        lineart_fidelity = 1.0
        self.anime_shadow_output_path = make_output_path(dpath)
        mode = "anime_shadow"     
        output_pil = create_and_save_images(self.fastapi_url, prompt, nega, shadow_pil, invert_pil, shadow_line_pil, image_size, self.anime_shadow_output_path, mode, image_fidelity, lineart_fidelity)

        self.display_output_image(output_pil)


    def generate_image_resize(self):
        prompt = "masterpiece, best quality " + self.resize_prompt_text.get("1.0", tk.END).strip()
        execute_tags = []
        prompt = prepare_prompt(execute_tags, prompt)
        nega = self.resize_negative_prompt_text.get("1.0", tk.END).strip()
        base_pil = Image.open(self.resize_image_path).convert("RGBA")
        white_bg = Image.new("RGBA", base_pil.size, "WHITE")
        white_bg.paste(base_pil, mask=base_pil)
        base_pil = white_bg.convert("RGB")
        max_length = float(self.max_length_scale.get())
        # 元の画像サイズを取得
        original_width, original_height = base_pil.size
        # アスペクト比を計算
        aspect_ratio = original_width / original_height
        # 長辺がmax_lengthになるように新しいサイズを計算
        if original_width > original_height:
            new_width = int(max_length)
            new_height = int(round(max_length / aspect_ratio))
        else:
            new_height = int(max_length)
            new_width = int(round(max_length * aspect_ratio))
        image_size = [new_width, new_height]
        self.resize_output_path = make_output_path(dpath)
        output_pil = upscale_and_save_images(self.fastapi_url, prompt, nega, base_pil, self.resize_output_path, image_size)

        self.display_output_image(output_pil)

def start(fastapi_url):
    app = Application(fastapi_url)
    app.mainloop()

