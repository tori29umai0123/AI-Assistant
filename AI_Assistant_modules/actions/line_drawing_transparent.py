import gradio as gr
from PIL import Image

from AI_Assistant_modules.output_image_gui import OutputImage
from utils.img_utils import transparent_process

LANCZOS = (Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.LANCZOS)


class LineDrawingTransparent:
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
                with gr.Row():
                    threshold = gr.Slider(minimum=1, maximum=100, value=70, step=1, interactive=True,
                                         label=lang_util.get_text("threshold"))
                with gr.Row():
                    generate_button = gr.Button(lang_util.get_text("generate"), interactive=False)
            with gr.Column():
                self.output = OutputImage(self.app_config, transfer_target_lang_key)
                output_image = self.output.layout()

        self.input_image.change(lambda x: gr.update(interactive=x is not None), inputs=[self.input_image],
                                outputs=[generate_button])

        generate_button.click(self._process, inputs=[
            self.input_image,
            threshold,
        ], outputs=[output_image])

    def _process(self, input_image_path, threshold):
        output_pil = transparent_process(input_image_path, threshold)

        return output_pil

