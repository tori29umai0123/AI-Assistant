import gradio as gr
from PIL import Image, ImageOps

from AI_Assistant_modules.output_image_gui import OutputImage
from AI_Assistant_modules.prompt_analysis import PromptAnalysis
from utils.img_utils import make_base_pil, base_generation, resize_image_aspect_ratio, noline_process
from utils.prompt_utils import execute_prompt, remove_duplicates
from utils.request_api import create_and_save_images, get_lora_model

LANCZOS = (Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.LANCZOS)


class Stick2Body:
    def __init__(self, app_config):
        self.app_config = app_config
        self.input_image = None
        self.output = None

    def layout(self, transfer_target_lang_key=None):
        lang_util = self.app_config.lang_util
        exui = self.app_config.exui        
        with gr.Row() as self.block:
            with gr.Column():
                with gr.Row():
                    with gr.Column():
                        self.input_image = gr.Image(label=lang_util.get_text("pose_image"),
                                                    source="upload",
                                                    type='filepath', interactive=True)
                with gr.Row():
                    prompt_analysis = PromptAnalysis(app_config=self.app_config, post_filter=False)
                    [prompt, nega] = prompt_analysis.layout(lang_util=lang_util, input_image=self.input_image)
                with gr.Row():
                    fidelity = gr.Slider(minimum=0.5, maximum=2.0, value=1.04, step=0.01, interactive=True, label=lang_util.get_text("pose_fidelity"))
                with gr.Row():
                    generate_button = gr.Button(lang_util.get_text("generate"), interactive=False)
            with gr.Column():
                self.output = OutputImage(self.app_config, transfer_target_lang_key)
                output_image = self.output.layout()


        self.input_image.change(lambda x: gr.update(interactive=x is not None), inputs=[self.input_image],
                                outputs=[generate_button])



        generate_button.click(self._process, inputs=[
            self.input_image,
            prompt,
            nega,
            fidelity,
        ], outputs=[output_image])



    def _process(self, input_image_path, prompt_text, negative_prompt_text, fidelity, coloring_choice):
        prompt = "masterpiece, best quality, <lora:Fixhands_anime_bdsqlsz_V1:1>, simple background, white background, bald, nude, " + prompt_text.strip()        
        execute_tags = ["NSFW", "monochrome", "greyscale", "pokemon (creature)", "no humans", "lineart", "triangle"]
        prompt =execute_prompt(execute_tags, prompt)
        prompt = remove_duplicates(prompt)
        nega = "nsfw, nipples, bad anatomy, liquid fingers, low quality, worst quality, out of focus, ugly, error, jpeg artifacts, lowers, blurry, bokeh" + negative_prompt_text.strip()
        nega  = remove_duplicates(nega)
        base_pil = make_base_pil(input_image_path)
        base_pil = resize_image_aspect_ratio(base_pil)  
        image_size = Image.open(input_image_path).size
        noline_pil = noline_process(input_image_path).resize(base_pil.size, LANCZOS).convert("RGB")
        mask_pil = base_generation(base_pil.size, (255, 255, 255, 255)).convert("RGB")
        pose_fidelity = float(fidelity)
        image_fidelity = 1.0
        output_path = self.app_config.make_output_path()
        output_pil = create_and_save_images(self.app_config.fastapi_url, prompt, nega, noline_pil, mask_pil,
                                            image_size, output_path, image_fidelity,
                                            self._make_cn_args(base_pil, pose_fidelity))
        return output_pil
        

    def _make_cn_args(self, image_pil, pose_fidelity ):
        unit1 = {
            "image": image_pil,
            "mask_image": None,
            "control_mode": "ControlNet is more important",
            "enabled": True,
            "guidance_end": 0.4,
            "guidance_start": 0,
            "pixel_perfect": True,
            "processor_res": 512,
            "resize_mode": "Just Resize",
            "weight": pose_fidelity,
            "module": "None",
            "model": "CL_am31_pose3D_V7_marged_rank256 [af7c88a9]",
            "save_detected_map": None,
            "hr_option": "Both"
        }
        unit2 = None
        return [unit1]
