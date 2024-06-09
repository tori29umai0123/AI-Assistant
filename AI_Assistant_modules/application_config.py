import datetime
import os


class ApplicationConfig:
    def __init__(self, lang_util, dpath):
        self.lang_util = lang_util
        self.fastapi_url = None
        self.dpath = dpath

    def set_fastapi_url(self, url):
        self.fastapi_url = url

    def make_output_path(self, filename=None):
        if filename is None:
            filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_dir = os.path.join(self.dpath, "output")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        return os.path.join(output_dir, filename + ".png")
