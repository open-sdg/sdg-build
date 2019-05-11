import os
import sdg
from sdg.outputs import OutputBase
from sdg.data import write_csv
from sdg.json import write_json, df_to_list_dict

class OutputOpenSdg(OutputBase):
    """Output SDG data/metadata in the formats expected by Open SDG."""


    def __init__(self, inputs, schema, output_folder=''):
        """Constructor for OutputBase."""
        self.schema = schema
        OutputBase.__init__(self, inputs, output_folder)


    def execute(self):
        """Write the JSON output expected by Open SDG."""
        status = True
        all_meta = dict()
        all_headline = dict()
        site_dir = self.output_folder

        # Write the schema.
        schema_output = sdg.schemas.SchemaOutputOpenSdg(schema=self.schema)
        schema_output_folder = os.path.join(site_dir, 'meta')
        schema_output.write_schema(output_folder=schema_output_folder, filename='schema.json')

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

        stats_reporting = sdg.stats.reporting_status(self.schema, all_meta)
        status = status & sdg.json.write_json('reporting', stats_reporting, ftype='stats', site_dir=site_dir)

        return(status)
