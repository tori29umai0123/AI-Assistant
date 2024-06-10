import gradio as gr
from PIL import Image

from AI_Assistant_modules.output_image_gui import OutputImage
from AI_Assistant_modules.prompt_analysis import PromptAnalysis
from utils.prompt_utils import prepare_prompt
from utils.request_api import upscale_and_save_images

LANCZOS = (Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.LANCZOS)


class ImageResize:
    def __init__(self, app_config):
        self.app_config = app_config
        self.input_image = None
        self.output = None

    def layout(self, transfer_target_lang_key=None):
        lang_util = self.app_config.lang_util
        with gr.Row() as self.block:
            with gr.Column():
                with gr.Row():
                    with gr.Column():
                        self.input_image = gr.Image(label=lang_util.get_text("input_image"), tool="editor",
                                                    source="upload",
                                                    type='filepath', interactive=True)
                    with gr.Column():
                        pass
                with gr.Row():
                    [prompt, nega] = PromptAnalysis(self.app_config).layout(lang_util, self.input_image)
                with gr.Row():
                    max_length_scale = gr.Slider(minimum=1600, maximum=2880, step=1, interactive=True,
                                                 label=lang_util.get_text("max_length"))
                with gr.Row():
                    generate_button = gr.Button(lang_util.get_text("generate"), interactive=False)
            with gr.Column():
                self.output = OutputImage(transfer_target_lang_key)
                output_image = self.output.layout(lang_util)

        self.input_image.change(lambda x: gr.update(interactive=x is not None), inputs=[self.input_image], outputs=[generate_button])

        generate_button.click(self._process, inputs=[
            self.input_image,
            prompt,
            nega,
            max_length_scale,
        ], outputs=[output_image])

    def _process(self, input_image_path, prompt_text, negative_prompt_text, max_length_scale):
        prompt = "masterpiece, best quality " + prompt_text.strip()
        execute_tags = []
        prompt = prepare_prompt(execute_tags, prompt)
        nega = negative_prompt_text.strip()
        base_pil = Image.open(input_image_path).convert("RGBA")
        white_bg = Image.new("RGBA", base_pil.size, "WHITE")
        white_bg.paste(base_pil, mask=base_pil)
        base_pil = white_bg.convert("RGB")
        max_length = float(max_length_scale)
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
        resize_output_path = self.app_config.make_output_path()
        output_pil = upscale_and_save_images(self.app_config.fastapi_url, prompt, nega, base_pil, resize_output_path,
                                             image_size)
        return output_pil
