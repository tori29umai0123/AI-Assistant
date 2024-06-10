import configparser
import os
import sys


def _get_appropriate_file_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.dirname(__file__))


def get_language_argument(default='jp'):
    for arg in sys.argv:
        if arg.startswith('--lang='):
            return arg.split('=')[1]
    return default


class LangUtil:
    def __init__(self, language_code='en'):
        self.language_code = language_code
        self.config = configparser.ConfigParser()
        self.appropriate_file_path = _get_appropriate_file_path()
        self._load_language()

    def _load_language(self):
        try:
            language_file = os.path.join(self.appropriate_file_path, 'languages',
                                         f'language_{self.language_code}.properties')

            with open(language_file, 'r', encoding='utf-8') as f:
                self.config.read_file(f)
        except Exception as e:
            print(f"Error loading language file: {e}")

    def get_text(self, key):
        try:
            return self.config.get('LANGUAGE', key)
        except Exception as e:
            print(f"Error getting text: {e}")
            return key
