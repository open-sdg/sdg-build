import sdg
import json
from sdg.translations import TranslationInputBase

class TranslationInputSdgTranslations(TranslationInputBase):
    """A class for importing translations from SDG Translations."""


    def execute(self):
        #data = self.fetch_file(self.source)
        #json_data = json.loads(data)
        #for lang in json_data:
        #    for group in json_data[lang]:
        #        for key in json_data[lang][group]:
        #            value = json_data[lang][group][key]
        #            self.add_translation(lang, group, key, value)
        self.clone_repo(self.source)


        #print(self.translations)
