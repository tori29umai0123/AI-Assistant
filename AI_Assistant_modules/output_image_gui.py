import gradio as gr


class OutputImage:
    def __init__(self, transfer_target=None):
        self.transfer_target = transfer_target

    def layout(self, lang_util):
        output_image = gr.Image(label=lang_util.get_text("output_image"), interactive=False, show_share_button=True)
        clipboard_button = gr.Button(""+lang_util.get_text("clipboard"))
        if self.transfer_target is not None:
            transfer_button = gr.Button(lang_util.get_text(self.transfer_target.lang_key))
            transfer_button.click(self.transfer_target.accept_transfer, inputs=[output_image])
        return output_image