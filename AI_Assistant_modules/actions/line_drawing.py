import gradio as gr
from PIL import Image

from AI_Assistant_modules.output_image_gui import OutputImage
from AI_Assistant_modules.prompt_analysis import PromptAnalysis
from utils.img_utils import make_base_pil, base_generation, canny_process
from utils.prompt_utils import prepare_prompt
from utils.request_api import create_and_save_images

LANCZOS = (Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.LANCZOS)


class LineDrawing:
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
                        with gr.Row():
                            canny_image = gr.Image(label=lang_util.get_text("canny_image"), type="pil",
                                                   interactive=False)
                        with gr.Row():
                            canny_threshold1 = gr.Slider(minimum=0, value=20, show_label=False)
                            gr.HTML(value="<span>/</span>", show_label=False)
                            canny_threshold2 = gr.Slider(minimum=0, value=120, show_label=False)
                            canny_generate_button = gr.Button(lang_util.get_text("generate"), interactive=False)
                with gr.Row():
                    [prompt, nega] = PromptAnalysis(self.app_config).layout(lang_util, self.input_image)
                with gr.Row():
                    fidelity = gr.Slider(minimum=0.75, maximum=1.5, value=1.0, step=0.01, interactive=True,
                                         label=lang_util.get_text("lineart_fidelity"))
                    bold = gr.Slider(minimum=0.0, maximum=1.0, value=0.0, step=0.01, interactive=True,
                                     label=lang_util.get_text("lineart_bold"))
                with gr.Row():
                    generate_button = gr.Button(lang_util.get_text("generate"), interactive=False)
            with gr.Column():
                self.output = OutputImage(transfer_target_lang_key)
                output_image = self.output.layout(lang_util)
        self.input_image.change(lambda x,y: gr.update(interactive=x is not None and y is not None), inputs=[self.input_image, canny_image], outputs=[generate_button])
        canny_image.change(lambda x,y: gr.update(interactive=x is not None and y is not None), inputs=[self.input_image, canny_image], outputs=[generate_button])
        self.input_image.change(lambda x: gr.update(interactive=x is not None), inputs=[self.input_image], outputs=[canny_generate_button])

        canny_generate_button.click(self._make_canny, inputs=[self.input_image, canny_threshold1, canny_threshold2],
                                    outputs=[canny_image])
        generate_button.click(self._process, inputs=[
            self.input_image,
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
        lineart_output_path = self.app_config.make_output_path()
        output_pil = create_and_save_images(self.app_config.fastapi_url,
                                            prompt, nega,
                                            white_base_pil, mask_pil, image_size,
                                            lineart_output_path,
                                            image_fidelity,
                                            self._make_cn_args(canny_pil, lineart_fidelity)
                                            )
        return output_pil

    def _make_canny(self, canny_img_path, canny_threshold1, canny_threshold2):
        threshold1 = int(canny_threshold1)
        threshold2 = int(canny_threshold2)
        return canny_process(canny_img_path, threshold1, threshold2)

    def _make_cn_args(self, canny_image_pil, lineart_fidelity):
        unit1 = {
            "image": canny_image_pil,
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
            "model": "control-lora-canny-rank256 [ec2dbbe4]",
            "save_detected_map": None,
            "hr_option": "Both"
        }
        unit2 = None
        return [unit1]
