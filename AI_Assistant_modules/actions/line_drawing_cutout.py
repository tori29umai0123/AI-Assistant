import gradio as gr
from PIL import Image

from AI_Assistant_modules.output_image_gui import OutputImage
from AI_Assistant_modules.prompt_analysis import PromptAnalysis
from utils.img_utils import make_base_pil, base_generation, flatline_process
from utils.prompt_utils import prepare_prompt
from utils.request_api import create_and_save_images

LANCZOS = (Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.LANCZOS)


class LineDrawingCutOut:
    def __init__(self, app_config):
        self.app_config = app_config
        self.input_image = None
        self.output = None

    def layout(self, lang_util, transfer_target_lang_key=None):
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
                    [prompt, nega] = PromptAnalysis().layout(lang_util, self.input_image)
                with gr.Row():
                    fidelity = gr.Slider(minimum=0.75, maximum=1.5, value=1.0, step=0.01, interactive=True,
                                         label=lang_util.get_text("lineart_fidelity"))
                    bold = gr.Slider(minimum=0.0, maximum=1.0, value=0.0, step=0.01, interactive=True,
                                     label=lang_util.get_text("lineart_bold"))
                with gr.Row():
                    generate_button = gr.Button(lang_util.get_text("generate"))
            with gr.Column():
                self.output = OutputImage(transfer_target_lang_key)
                output_image = self.output.layout(lang_util)

        generate_button.click(self._process, inputs=[
            self.input_image,
            prompt,
            nega,
            fidelity,
            bold,
        ], outputs=[output_image])

    def _process(self, input_image_path, prompt_text, negative_prompt_text, fidelity, bold):
        lineart2 = 1 - bold
        prompt = "masterpiece, best quality, <lora:sdxl_BWLine:" + str(lineart2) + ">, <lora:sdxl_BW_bold_Line:" + str(
            bold) + ">, monochrome, lineart2, white background, " + prompt_text.strip()
        execute_tags = ["sketch"]
        prompt = prepare_prompt(execute_tags, prompt)
        nega = negative_prompt_text.strip()
        base_pil = make_base_pil(input_image_path)
        image_size = base_pil.size
        flatLine_pil = flatline_process(input_image_path).resize(base_pil.size, Image.LANCZOS).convert("RGB")
        mask_pil = base_generation(base_pil.size, (255, 255, 255, 255)).convert("RGB")
        white_base_pil = base_generation(base_pil.size, (255, 255, 255, 255)).convert("RGB")
        image_fidelity = 1.0
        lineart2_fidelity = float(fidelity)
        lineart2_output_path = self.app_config.make_output_path()
        mode = "lineart2"
        output_pil = create_and_save_images(self.app_config.fastapi_url, prompt, nega, white_base_pil, flatLine_pil,
                                            mask_pil, image_size, lineart2_output_path, mode, image_fidelity,
                                            lineart2_fidelity)
        return output_pil
