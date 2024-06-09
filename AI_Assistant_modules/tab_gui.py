import gradio as gr

from AI_Assistant_modules.actions.anime_shadow import AnimeShadow
from AI_Assistant_modules.actions.i2i import Img2Img
from AI_Assistant_modules.actions.lighting import Lighting
from AI_Assistant_modules.actions.line_drawing import LineDrawing
from AI_Assistant_modules.actions.line_drawing_cutout import LineDrawingCutOut
from AI_Assistant_modules.actions.normal_map import NormalMap
from AI_Assistant_modules.actions.resize import ImageResize


# class base_gui:
#  def layout(self, lang_util, transfer_target=None):

def _set_transfer_button(main_tab, target_tab_item, from_tab, transfer_target_tab):
    from_tab.output.transfer_button.click(fn=lambda x: [x, gr.Tabs.update(selected=target_tab_item.id)],
                                          inputs=[from_tab.output.output_image],
                                          outputs=[transfer_target_tab.input_image, main_tab])


def gradio_tab_gui(app_config):
    lang_util = app_config.lang_util

    with gr.Blocks() as main_block:
        with gr.Tabs() as main_tab:
            with gr.TabItem(lang_util.get_text("img2img")):
                img_2_img = Img2Img(app_config)
                img_2_img.layout(lang_util, "transfer_to_lineart")
            with gr.TabItem(lang_util.get_text("lineart"), id="lineart") as line_drawing_tab_item:
                line_drawing_tab = LineDrawing(app_config)
                line_drawing_tab.layout(lang_util, "transfer_to_normalmap")
            with gr.TabItem(lang_util.get_text("lineart2")):
                line_drawing_cutout_tab = LineDrawingCutOut(app_config)
                line_drawing_cutout_tab.layout(lang_util, "transfer_to_normalmap")
            with gr.TabItem(lang_util.get_text("normalmap"), id="normalmap") as normal_map_tab_item:
                normal_map = NormalMap(app_config)
                normal_map.layout(lang_util, "transfer_to_lighting")
            with gr.TabItem(lang_util.get_text("lighting"), id="lighting") as lighting_tab_item:
                lighting = Lighting(app_config)
                lighting.layout(lang_util, "anime_shadow_tab_transfer")
            with gr.TabItem(lang_util.get_text("anime_shadow"), id="anime_shadow") as anime_shadow_tab_item:
                anime_shadow = AnimeShadow(app_config)
                anime_shadow.layout(lang_util)
            with gr.TabItem(lang_util.get_text("resize")):
                ImageResize(app_config).layout(lang_util)

        # タブ間転送の動作設定
        _set_transfer_button(main_tab, line_drawing_tab_item, img_2_img, line_drawing_tab)
        _set_transfer_button(main_tab, normal_map_tab_item, line_drawing_tab, normal_map)
        _set_transfer_button(main_tab, normal_map_tab_item, line_drawing_cutout_tab, normal_map)
        _set_transfer_button(main_tab, lighting_tab_item, normal_map, lighting)
        _set_transfer_button(main_tab, anime_shadow_tab_item, lighting, anime_shadow)
    return main_block
