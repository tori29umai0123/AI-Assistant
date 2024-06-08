import PIL
import gradio as gr
from PIL.Image import Image

from AI_Assistant_modules.output_image_gui import OutputImage
from AI_Assistant_modules.prompt_analysis import PromptAnalysis
from utils.application import make_output_path
from utils.img_utils import make_base_pil, base_generation, canny_process
from utils.prompt_utils import prepare_prompt
from utils.request_api import create_and_save_images

LANCZOS = (PIL.Image.Resampling.LANCZOS if hasattr(PIL.Image, 'Resampling') else Image.LANCZOS)


class LineDrawing:
    def __init__(self, app_config):
        self.app_config = app_config

    def accept_transfer(self, image):
        pass

    def layout(self, lang_util, transfer_target=None):
        with gr.Row():
            with gr.Column():
                with gr.Row():
                    with gr.Column():
                        input_image = gr.Image(label=lang_util.get_text("input_image"), tool="editor", source="upload",
                                               type='filepath', interactive=True)
                    with gr.Column():
                        with gr.Row():
                            canny_image = gr.Image(label=lang_util.get_text("canny_image"), type="pil",
                                                   interactive=False)
                        with gr.Row():
                            canny_threshold1 = gr.Slider(minimum=0, value=20, show_label=False)
                            gr.HTML(value="<span>/</span>", show_label=False)
                            canny_threshold2 = gr.Slider(minimum=0, value=120, show_label=False)
                            canny_generate_button = gr.Button(lang_util.get_text("generate"))
                with gr.Row():
                    [prompt, nega] = PromptAnalysis().layout(lang_util, input_image)
                with gr.Row():
                    fidelity = gr.Slider(minimum=0.75, maximum=1.5, value=1.0, step=0.01, interactive=True,
                                         label=lang_util.get_text("lineart_fidelity"))
                    bold = gr.Slider(minimum=0.0, maximum=1.0, value=0.0, step=0.01, interactive=True,
                                     label=lang_util.get_text("lineart_bold"))
                with gr.Row():
                    generate_button = gr.Button(lang_util.get_text("generate"))
            with gr.Column():
                output_image = OutputImage(transfer_target).layout(lang_util)

        canny_generate_button.click(self._make_canny, inputs=[input_image, canny_threshold1, canny_threshold2],
                                    outputs=[canny_image])
        generate_button.click(self._process, inputs=[
            input_image,
            canny_image,
            prompt,
            nega,
            fidelity,
            bold,
        ], outputs=[output_image])

    def _process(self, input_image_path, canny_image_pil, prompt_text, negative_prompt_text, fidelity, bold):
        lineart_bold = float(bold)
        lineart = 1 - lineart_bold
        prompt = "masterpiece, best quality, <lora:sdxl_BWLine:" + str(lineart) + ">, <lora:sdxl_BW_bold_Line:" + str(
            lineart_bold) + ">, monochrome, lineart, white background, " + prompt_text.strip()
        execute_tags = ["sketch"]
        prompt = prepare_prompt(execute_tags, prompt)
        nega = negative_prompt_text.strip()
        base_pil = make_base_pil(input_image_path)
        image_size = base_pil.size
        canny_pil = canny_image_pil.resize(base_pil.size, LANCZOS).convert("RGB")
        mask_pil = base_generation(base_pil.size, (255, 255, 255, 255)).convert("RGB")
        white_base_pil = base_generation(base_pil.size, (255, 255, 255, 255)).convert("RGB")
        image_fidelity = 1.0
        lineart_fidelity = float(fidelity)
        lineart_output_path = make_output_path(self.app_config.dpath)
        mode = "lineart"
        output_pil = create_and_save_images(self.app_config.fastapi_url,
                                            prompt, nega,
                                            white_base_pil, canny_pil, mask_pil, image_size,
                                            lineart_output_path,
                                            mode,
                                            image_fidelity,
                                            lineart_fidelity
                                            )
        return output_pil

    def _make_canny(self, canny_img_path, canny_threshold1, canny_threshold2):
        threshold1 = int(canny_threshold1)
        threshold2 = int(canny_threshold2)
        return canny_process(canny_img_path, threshold1, threshold2)
