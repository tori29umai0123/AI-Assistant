import gradio as gr
from PIL import Image

from AI_Assistant_modules.output_image_gui import OutputImage
from AI_Assistant_modules.prompt_analysis import PromptAnalysis
from utils.img_utils import make_base_pil, base_generation, mask_process
from utils.prompt_utils import execute_prompt, remove_duplicates
from utils.request_api import create_and_save_images, get_lora_model

LANCZOS = (Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.LANCZOS)

class Img2Img:
    def __init__(self, app_config):
        self.app_config = app_config
        self.input_image = None
        self.output = None


    def layout(self, transfer_target_lang_key=None):
        lang_util = self.app_config.lang_util
        exui = self.app_config.exui

        with gr.Row():
            with gr.Column():
                with gr.Row():
                    with gr.Column():
                        self.input_image = gr.Image(label=lang_util.get_text("input_image"), tool="editor", source="upload", type='filepath', interactive=True)
                    with gr.Column():
                        with gr.Row():
                            mask_image = gr.Image(label=lang_util.get_text("mask_image"), type="pil")
                        with gr.Row():
                            mask_generate_button = gr.Button(lang_util.get_text("create"), interactive=False)
                    with gr.Column():
                        with gr.Row():
                            anytest_image = gr.Image(label=lang_util.get_text("anytest_image"), type="pil")
                        with gr.Row():
                            anytest_choice_button = gr.Radio(["none", "anytestV3", "anytestV4"], value="none", label=lang_util.get_text("anytest_choice"))
                #exuiが有効な場合、以下の処理を行う
                if exui:
                    with gr.Row():
                        lora_model_dropdown = gr.Dropdown(label=lang_util.get_text("lora_models"), choices=[])
                        load_lora_models_button = gr.Button(lang_util.get_text("lora_update"))
                with gr.Row():
                    prompt_analysis = PromptAnalysis(app_config=self.app_config, post_filter=False)
                    [prompt, nega] = prompt_analysis.layout(lang_util=lang_util, input_image=self.input_image)
                with gr.Row():
                    fidelity = gr.Slider(minimum=0.0, maximum=0.9, value=0.35, step=0.01, interactive=True, label=lang_util.get_text("image_fidelity"))
                with gr.Row():
                    anytest_fidelity = gr.Slider(minimum=0.35, maximum=1.25, value=1.0, step=0.01, interactive=True, label=lang_util.get_text("anytest_fidelity"))
                with gr.Row():
                    generate_button = gr.Button(lang_util.get_text("generate"), interactive=False)
            with gr.Column():
                self.output = OutputImage(self.app_config, transfer_target_lang_key)
                output_image = self.output.layout()

        self.input_image.change(lambda x: gr.update(interactive=x is not None), inputs=[self.input_image], outputs=[generate_button])
        self.input_image.change(lambda x: gr.update(interactive=x is not None), inputs=[self.input_image], outputs=[mask_generate_button])

        mask_generate_button.click(mask_process, inputs=[self.input_image], outputs=[mask_image])

        if exui:
            load_lora_models_button.click(self.load_lora_models, inputs=[], outputs=[lora_model_dropdown])
            lora_model_dropdown.change(self.update_prompt_with_lora, inputs=[lora_model_dropdown, prompt], outputs=[prompt])

        generate_button.click(self._process, inputs=[
            self.input_image,
            mask_image,
            anytest_image,
            anytest_choice_button,
            anytest_fidelity,
            prompt,
            nega,
            fidelity,
        ], outputs=[output_image])

    def _process(self, input_image_path, mask_image_pil, anytest_image, anytest_choice_button, anytest_fidelity, prompt_text, negative_prompt_text, fidelity):
        prompt = "masterpiece, best quality, " + prompt_text.strip()
        execute_tags = ["transparent background"]
        prompt =execute_prompt(execute_tags, prompt)
        prompt = remove_duplicates(prompt)
        nega = negative_prompt_text.strip()
        base_pil = make_base_pil(input_image_path)
        image_size = base_pil.size
        if mask_image_pil is None:
            mask_pil = base_generation(base_pil.size, (255, 255, 255, 255)).convert("RGB")
        else:
            mask_pil = mask_image_pil.resize(base_pil.size, LANCZOS).convert("RGB")
        image_fidelity = 1 - float(fidelity)
        img2img_output_path = self.app_config.make_output_path()

        if anytest_choice_button == "none":
            output_pil = create_and_save_images(self.app_config.fastapi_url, prompt, nega, base_pil, mask_pil,
                                                image_size, img2img_output_path, image_fidelity, None, {
                                                    "mask": mask_pil,
                                                    "mask_blur": 4,
                                                    "inpainting_fill": 1,
                                                })
            return output_pil
        else:
            output_pil = create_and_save_images(self.app_config.fastapi_url, prompt, nega, base_pil, mask_pil,
                                    image_size, img2img_output_path, image_fidelity, self._make_cn_args(anytest_image, anytest_fidelity, anytest_choice_button), {
                                        "mask": mask_pil,
                                        "mask_blur": 4,
                                        "inpainting_fill": 1,
                                    })
            return output_pil

    def load_lora_models(self):
        model_names, model_aliases = get_lora_model(self.app_config.fastapi_url)
        model_options = [f"{name} ({alias})" for name, alias in zip(model_names, model_aliases)]
        return gr.Dropdown.update(choices=model_options, interactive=True)
    

    def update_prompt_with_lora(self, lora_model_selection, existing_prompt):
        if '(' in lora_model_selection and ')' in lora_model_selection:
            alias = lora_model_selection.split('(')[-1].split(')')[0].strip()
        else:
            alias = lora_model_selection
        
        lora_tag = f"<lora:{alias}:1.0>"
        updated_prompt = existing_prompt + ", " + lora_tag if existing_prompt else lora_tag
        return updated_prompt


    def _make_cn_args(self, anytest_image, anytest_fidelity, anytest_choice_button):
        if anytest_choice_button == "anytestV3":
            model = "CN-anytest_v3-50000_am_dim256 [dbecc0f9]"
        else:
            model = "CN-anytest_v4-marged_am_dim256 [49b6c950]"

        unit1 = {
            "image": anytest_image,
            "mask_image": None,
            "control_mode": "Balanced",
            "enabled": True,
            "guidance_end": 1,
            "guidance_start": 0,
            "pixel_perfect": True,
            "processor_res": 512,
            "resize_mode": "Just Resize",
            "weight": anytest_fidelity,
            "module": "None",
            "model": model,
            "save_detected_map": None,
            "hr_option": "Both"
        }
        unit2 = None
        return [unit1]
    
