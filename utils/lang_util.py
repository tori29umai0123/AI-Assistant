import os
import configparser

import sys
# 'frozen' 状態に応じて適切なファイルパスを取得する関数
def get_appropriate_file_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable) 
    else:
        return os.path.dirname(os.path.dirname(__file__))
    
appropriate_file_path = get_appropriate_file_path()


class Lang_Util:
    def __init__(self, language_code='en'):
        self.language_code = language_code
        self.config = configparser.ConfigParser()
        self.load_language()

    def load_language(self):
        try:
            language_file = os.path.join(appropriate_file_path,  'languages',
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
