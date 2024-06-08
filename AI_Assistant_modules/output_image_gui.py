import gradio as gr

javascript = """
function copyToClipboard() {
    var img = Array.from(document.querySelectorAll('.output-image img') || []).filter(img => img.offsetParent)[0];
    if (!img) {
        return;
    }
    fetch(img.src)
    .then(response => response.blob())
    .then(blob => {
        const item = new ClipboardItem({ "image/png": blob });
        navigator.clipboard.write([item]);
    })
    .catch(console.error);
}
"""


class OutputImage:
    def __init__(self, transfer_target_lang_key=None):
        self.transfer_button = None
        self.output_image = None
        self.output_image_path = None
        self.transfer_target_lang_key = transfer_target_lang_key

    def layout(self, lang_util):
        output_image = gr.Image(label=lang_util.get_text("output_image"), interactive=False, type="filepath",
                                elem_classes=["output-image"])
        output_image.change(self._set_output_image, inputs=[output_image])
        clipboard_button = gr.Button("" + lang_util.get_text("clipboard"), elem_classes=["clipboard"])
        clipboard_button.click(self._notify, _js=javascript, queue=True)
        if self.transfer_target_lang_key is not None:
            self.transfer_button = gr.Button(lang_util.get_text(self.transfer_target_lang_key))
        self.output_image = output_image
        return output_image

    def _set_output_image(self, output_image_path):
        self.output_image_path = output_image_path

    def _notify(self):
        if self.output_image_path is None:
            gr.Warning("Please Image Select")
        else:
            gr.Info("Image Copied to Clipboard")
