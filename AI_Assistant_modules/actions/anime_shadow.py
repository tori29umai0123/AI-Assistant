import gradio as gr
from PIL import Image

from AI_Assistant_modules.output_image_gui import OutputImage
from AI_Assistant_modules.prompt_analysis import PromptAnalysis
from utils.application import make_output_path
from utils.img_utils import make_base_pil, invert_process, multiply_images
from utils.prompt_utils import prepare_prompt
from utils.request_api import create_and_save_images

LANCZOS = (Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.LANCZOS)


class AnimeShadow:
    def __init__(self, app_config):
        self.app_config = app_config
        self.input_image = None
        self.output = None

    def accept_transfer(self, image):
        pass

    def layout(self, lang_util, transfer_target_lang_key=None):
        with gr.Row():
            with gr.Column():
                with gr.Row():
                    with gr.Column():
                        input_image = gr.Image(label=lang_util.get_text("anime_shadow_input_image"), tool='editor', source='upload',
                                               type='filepath', interactive=True)
                    with gr.Column():
                        shadow_image = gr.Image(label=lang_util.get_text("shadow_image"), type='pil', interactive=True)
                        # ライティングタブからの転送先
                        self.input_image = shadow_image
                with gr.Row():
                    [prompt, nega] = PromptAnalysis().layout(lang_util, input_image)
                with gr.Row():
                    shadow_choice = gr.Dropdown(label=lang_util.get_text('shadow_choices'), value='anime01',
                                                choices=['anime01', 'anime02'], interactive=True)
                with gr.Row():
                    generate_button = gr.Button(lang_util.get_text('generate'))
            with gr.Column():
                self.output = OutputImage(transfer_target_lang_key)
                output_image = self.output.layout(lang_util)
        generate_button.click(self._process, inputs=[
            input_image,
            shadow_image,
            prompt,
            nega,
            shadow_choice,
        ], outputs=[output_image])

    def _process(self, input_image_path, shadow_image_pil, prompt_text, negative_prompt_text, shadow_choice):
        prompt = f"masterpiece, best quality, <lora:{shadow_choice}:1>, monochrome, greyscale, " + prompt_text.strip()
        execute_tags = ["lineart", "sketch"]
        prompt = prepare_prompt(execute_tags, prompt)
        nega = negative_prompt_text.strip()
        base_pil = make_base_pil(input_image_path)
        image_size = base_pil.size
        invert_pil = invert_process(input_image_path).convert("RGB")
        shadow_pil = shadow_image_pil.resize(base_pil.size, LANCZOS)
        shadow_line_pil = multiply_images(base_pil, shadow_pil).convert("RGB")
        image_fidelity = 1.0
        lineart_fidelity = 1.0
        anime_shadow_output_path = make_output_path(self.app_config.dpath)
        mode = "anime_shadow"
        output_pil = create_and_save_images(self.app_config.fastapi_url, prompt, nega, shadow_pil, invert_pil,
                                            shadow_line_pil, image_size, anime_shadow_output_path, mode, image_fidelity,
                                            lineart_fidelity)

        return output_pil
