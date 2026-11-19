import io
import mammoth
from pyquery import PyQuery as pq
from sdg.inputs import InputBase
from sdg.inputs import InputWordMeta
from sdg import helpers
import yaml

class InputWordMetaRemote(InputWordMeta):
    """Sources of SDG metadata that are remote Word files using a standard
    template that is compliant with the SDMX MSD. This is coded to work with
    this template: https://github.com/sdmx-sdgs/metadata (currently v3.2) """

    def __init__(self,
        indicator_id_map=None,
        logging=None,
        request_params=None,
        indicator_id_conversions=None,
        metadata_mapping=None,
    ):
        """Constructor for InputWordMetaRemote."""
        InputWordMeta.__init__(self,
            logging=logging,
            indicator_id_conversions=indicator_id_conversions,
            metadata_mapping=metadata_mapping,
        )
        self.indicator_id_map = self.get_indicator_id_map(indicator_id_map)


    def get_indicator_id_map(self, source):
        if isinstance(source, dict):
            return source
        elif isinstance(source, str):
            with open(source) as file:
                return yaml.load(file, Loader=yaml.FullLoader)
        else:
            raise Exception("The indicator_id_map parameter is not configured correctly.")
        return {}

    def execute(self, indicator_options):
        for source, indicator_ids in self.indicator_id_map.items():
            with helpers.files.fetch_remote_file(source, self.request_params) as response:
                docx_bytes = response.read()
                result = mammoth.convert_to_html(io.BytesIO(docx_bytes), **self.get_mammoth_options())
                meta = self.get_meta_from_word(result, source)
                if not isinstance(indicator_ids, list):
                    indicator_ids = [indicator_ids]
                for inid in indicator_ids:
                    self.apply_metadata_mapping(meta)
                    self.fix_booleans(meta)
                    self.add_indicator(self.normalize_indicator_id(inid), meta=meta, options=indicator_options)
