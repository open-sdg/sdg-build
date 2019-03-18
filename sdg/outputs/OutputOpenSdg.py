import os
import sdg
from sdg.outputs import OutputBase
from sdg.data import write_csv
from sdg.json import write_json, df_to_list_dict

class OutputOpenSdg(OutputBase):
    """Output SDG data/metadata in the formats expected by Open SDG."""

    def __init__(self, inputs, output_folder='', schema_path=''):
        """Constructor for OutputBase."""
        self.schema_path = schema_path
        OutputBase.__init__(self, inputs, output_folder)

    def write_output(self):
        """Write the JSON output expected by Open SDG."""

        status = True
        all_meta = dict()
        all_headline = dict()
        site_dir = self.output_folder

        # Write the schema.
        schema_file = os.path.basename(self.schema_path)
        schema_folder = os.path.dirname(self.schema_path)
        schema = sdg.schema.get_schema(prose_file=schema_file, src_dir=schema_folder)
        status = status & write_json('schema', schema, ftype='meta', gz=False, site_dir=site_dir)

        for inid in self.indicators:
            indicator = self.indicators[inid]
            # Output all the csvs
            status = status & write_csv(inid, indicator.data, ftype='data', site_dir=site_dir)
            status = status & write_csv(inid, indicator.edges, ftype='edges', site_dir=site_dir)
            status = status & write_csv(inid, indicator.headline, ftype='headline', site_dir=site_dir)
            # And JSON
            data_dict = df_to_list_dict(indicator.data, orient='list')
            edges_dict = df_to_list_dict(indicator.edges, orient='list')
            headline_dict = df_to_list_dict(indicator.headline, orient='records')

            status = status & write_json(inid, data_dict, ftype='data', gz=False, site_dir=site_dir)
            status = status & write_json(inid, edges_dict, ftype='edges', gz=False, site_dir=site_dir)
            status = status & write_json(inid, headline_dict, ftype='headline', gz=False, site_dir=site_dir)

            # combined
            comb = {'data': data_dict, 'edges': edges_dict}
            status = status & write_json(inid, comb, ftype='comb', gz=False, site_dir=site_dir)

            # Metadata
            status = status & sdg.json.write_json(inid, indicator.meta, ftype='meta', site_dir=site_dir)

            # Append to the build-time "all" output
            all_meta[inid] = indicator.meta
            all_headline[inid] = headline_dict

        status = status & sdg.json.write_json('all', all_meta, ftype='meta', site_dir=site_dir)
        status = status & sdg.json.write_json('all', all_headline, ftype='headline', site_dir=site_dir)

        return(status)
