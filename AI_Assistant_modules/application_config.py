import datetime
import os
import sys

from gradio.utils import colab_check, is_zero_gpu_space


class ApplicationConfig:
    def __init__(self, lang_util, dpath):
        self.lang_util = lang_util
        self.fastapi_url = None
        self.dpath = dpath
        self.output_dir = os.path.join(dpath, "output")
        self.exui = False

        device_mapping = {
            'darwin': 'mac',
            'linux': 'linux',
            'win32': 'windows'
        }
        if colab_check() or is_zero_gpu_space() or os.environ.get("GRADIO_CLOUD") == "1":
            self.device = "cloud"
        elif os.path.exists('/.dockerenv'):
            self.device = "docker"
        else:
            self.device = device_mapping.get(sys.platform.split()[0], 'unknown')

    def set_fastapi_url(self, url):
        self.fastapi_url = url

    def make_output_path(self, filename=None):
        if filename is None:
            filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        return os.path.join(self.output_dir, filename + ".png")
