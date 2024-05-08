import os
import configparser

class Lang_Util:
    def __init__(self, language_code='en'):
        self.language_code = language_code
        self.config = configparser.ConfigParser()
        self.load_language()

    def load_language(self):
        try:
            language_file = os.path.join(os.path.dirname(__file__), '..', 'languages',
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
