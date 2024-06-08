class ApplicationConfig:
    def __init__(self, lang_util, dpath):
        self.lang_util = lang_util
        self.fastapi_url = None
        self.dpath = dpath

    def set_fastapi_url(self, url):
        self.fastapi_url = url

