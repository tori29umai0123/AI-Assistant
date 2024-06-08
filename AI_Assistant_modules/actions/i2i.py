import PIL
import gradio as gr
from PIL.Image import Image

from AI_Assistant_modules.output_image_gui import OutputImage
from AI_Assistant_modules.prompt_analysis import PromptAnalysis
from utils.application import make_output_path
from utils.img_utils import make_base_pil, base_generation, mask_process
from utils.prompt_utils import remove_duplicates
from utils.request_api import create_and_save_images

LANCZOS = (PIL.Image.Resampling.LANCZOS if hasattr(PIL.Image, 'Resampling') else Image.LANCZOS)


class Img2Img:
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
                        input_image = gr.Image(label=lang_util.get_text("input_image"), tool="editor", source="upload",
                                               type='filepath', interactive=True)
                    with gr.Column():
                        with gr.Row():
                            mask_image = gr.Image(label=lang_util.get_text("mask_image"), type="pil")
                        with gr.Row():
                            mask_generate_button = gr.Button(lang_util.get_text("create"))
                with gr.Row():
                    [prompt, nega] = PromptAnalysis().layout(lang_util, input_image)
                with gr.Row():
                    fidelity = gr.Slider(minimum=0.0, maximum=0.9, value=0.35, step=0.01, interactive=True,
                                         label=lang_util.get_text("image_fidelity"))
                with gr.Row():
                    generate_button = gr.Button(lang_util.get_text("generate"))
            with gr.Column():
                self.output = OutputImage(transfer_target_lang_key)
                output_image = self.output.layout(lang_util)

        mask_generate_button.click(mask_process, inputs=[input_image],
                                   outputs=[mask_image])
        generate_button.click(self._process, inputs=[
            input_image,
            mask_image,
            prompt,
            nega,
            fidelity,
        ], outputs=[output_image])

    def _process(self, input_image_path, mask_image_pil, prompt_text, negative_prompt_text, fidelity):
        prompt = "masterpiece, best quality, " + prompt_text.strip()
        prompt_list = prompt.split(", ")
        # 重複を除去
        unique_tags = remove_duplicates(prompt_list)
        prompt = ", ".join(unique_tags)
        nega = negative_prompt_text.strip()
        base_pil = make_base_pil(input_image_path)
        image_size = base_pil.size
        canny_pil = None
        if mask_image_pil is None:
            mask_pil = base_generation(base_pil.size, (255, 255, 255, 255)).convert("RGB")
        else:
            mask_pil = mask_image_pil.resize(base_pil.size, LANCZOS).convert("RGB")
        image_fidelity = 1 - float(fidelity)
        lineart_fidelity = None
        img2img_output_path = make_output_path(self.app_config.dpath)
        mode = "i2i"
        output_pil = create_and_save_images(self.app_config.fastapi_url, prompt, nega, base_pil, canny_pil, mask_pil,
                                            image_size, img2img_output_path, mode, image_fidelity, lineart_fidelity)
        return output_pil
