import gradio as gr
from PIL import Image

from AI_Assistant_modules.output_image_gui import OutputImage
from AI_Assistant_modules.prompt_analysis import PromptAnalysis
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

    def layout(self, transfer_target_lang_key=None):
        lang_util = self.app_config.lang_util
        with gr.Row():
            with gr.Column():
                with gr.Row():
                    with gr.Column():
                        input_image = gr.Image(label=lang_util.get_text("anime_shadow_input_image"), tool='editor',
                                               source='upload',
                                               type='filepath', interactive=True)
                    with gr.Column():
                        shadow_image = gr.Image(label=lang_util.get_text("shadow_image"), type='pil', interactive=True)
                        # ライティングタブからの転送先
                        self.input_image = shadow_image
                with gr.Row():
                    [prompt, nega] = PromptAnalysis(self.app_config).layout(lang_util, input_image)
                with gr.Row():
                    shadow_choice = gr.Dropdown(label=lang_util.get_text('shadow_choices'), value='anime01',
                                                choices=['anime01', 'anime02'], interactive=True)
                with gr.Row():
                    generate_button = gr.Button(lang_util.get_text('generate'), interactive=False)
            with gr.Column():
                self.output = OutputImage(transfer_target_lang_key)
                output_image = self.output.layout(lang_util)

        input_image.change(lambda x,y: gr.update(interactive=x is not None and y is not None), inputs=[input_image, shadow_image], outputs=[generate_button])
        shadow_image.change(lambda x,y: gr.update(interactive=x is not None and y is not None), inputs=[input_image, shadow_image], outputs=[generate_button])

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
        anime_shadow_output_path = self.app_config.make_output_path()
        cn_args = self._make_cn_args(base_pil, invert_pil, lineart_fidelity)
        output_pil = create_and_save_images(self.app_config.fastapi_url, prompt, nega, shadow_pil, shadow_line_pil,
                                            image_size, anime_shadow_output_path, image_fidelity, cn_args)

        return output_pil

    def _make_cn_args(self, base_pil, invert_pil, lineart_fidelity):
        unit1 = {
            "image": base_pil,
            "mask_image": None,
            "control_mode": "Balanced",
            "enabled": True,
            "guidance_end": 0.35,
            "guidance_start": 0,
            "pixel_perfect": True,
            "processor_res": 512,
            "resize_mode": "Just Resize",
            "weight": 0.5,
            "module": "blur_gaussian",
            "threshold_a": 9.0,
            "model": "controlnet852AClone_v10 [808807b2]",
            "save_detected_map": None,
            "hr_option": "Both"
        }
        unit2 = {
            "image": invert_pil,
            "mask_image": None,
            "control_mode": "Balanced",
            "enabled": True,
            "guidance_end": 1,
            "guidance_start": 0,
            "pixel_perfect": True,
            "processor_res": 512,
            "resize_mode": "Just Resize",
            "weight": lineart_fidelity,
            "module": "None",
            "model": "Kataragi_lineartXL-lora128 [0598262f]",
            "save_detected_map": None,
            "hr_option": "Both"
        }
        return [unit1, unit2]
