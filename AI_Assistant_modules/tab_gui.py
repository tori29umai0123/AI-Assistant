import gradio as gr

from AI_Assistant_modules.actions.i2i import Img2Img
from AI_Assistant_modules.actions.line_drawing import LineDrawing


# class base_gui:
#  def layout(self, lang_util, transfer_target=None):
#  def accept_transfer(self, image):


def gradio_tab_gui(app_config):
    lang_util = app_config.lang_util
    with gr.Blocks() as main_tab:
        with gr.Tabs():
            with gr.TabItem(lang_util.get_text("img2img")):
                Img2Img(app_config).layout(lang_util)
            with gr.TabItem(lang_util.get_text("lineart")):
                LineDrawing(app_config).layout(lang_util)
            with gr.TabItem(lang_util.get_text("lineart2")):
                gr.Markdown("Under construction")
            with gr.TabItem(lang_util.get_text("normalmap")):
                gr.Markdown("Under construction")
            with gr.TabItem(lang_util.get_text("lighting")):
                gr.Markdown("Under construction")
            with gr.TabItem(lang_util.get_text("anime_shadow")):
                gr.Markdown("Under construction")
            with gr.TabItem(lang_util.get_text("resize")):
                gr.Markdown("Under construction")
    return main_tab
