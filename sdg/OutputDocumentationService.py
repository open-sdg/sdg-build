import os
import shutil
import sdg
import pandas as pd
from slugify import slugify
from sdg.Loggable import Loggable
import humanize

class OutputDocumentationService(Loggable):
    """HTML generation to document outputs built with this library.

    Note that this is meant to document particular builds, not the library in
    general. The idea is that each time this library is used to build/convert
    some SDG-related data, this class can be used to generate human-friendly
    HTML pages documenting the specifics of the build (such as endpoint URLs).
    """

    def __init__(self, outputs, folder='_site', branding='Build docs',
                 languages=None, intro='', translations=None, indicator_url=None,
                 subfolder=None, baseurl='', extra_disaggregations=None,
                 translate_disaggregations=False, translate_metadata=False, logging=None,
                 metadata_fields=None):
        """Constructor for the OutputDocumentationService class.
        Parameters
        ----------
        outputs : list
            Required list of objects inheriting from OutputBase. Each output
            will receive its own documentation page (or pages).
        folder : string
            Optional folder in which to create the documentation pages. Defaults
            to the "_site" folder.
        subfolder : string
            Optional subfolder (beneath the "folder" parameter) in which to
            create the documentation pages.
        branding : string
            Optional title/heading to use on all documentation pages. Defaults
            to "Build docs".
        languages : list
            Optional list of language codes. If more than one language is
            provided, any languages beyond the first will display as translations
            in additional columns. Defaults to ['en'].
        intro : string
            Optionl chunk of text to display at the top of the front page.
        translations : list
            Optional list of objects inheriting from TranslationInputBase. If
            provided these will be used to translate the output.
        indicator_url : string
            Optional URL pattern to use for linking to indicators. If provided,
            the "[id]" will be replaced with the indicator id (dash-delimited).
            For example, "https://example.com/[id].html" will be replaced with
            "https://example.com/4-1-1.html".
        baseurl : string
            An optional path that all absolute URLs in the data repository start with.
        extra_disaggregations : list
            An optional list of columns to include in the disaggregation report,
            which would otherwise not be included. Common options are units of
            measurement and series.
        translate_disaggregations : boolean
            Whether or not to include translation columns in the
            disaggregation report.
        metadata_fields : list
            Metadata fields to include in a metadata report.
        """
        Loggable.__init__(self, logging=logging)
        self.outputs = outputs
        self.folder = self.fix_folder(folder, subfolder)
        self.branding = branding
        self.intro = intro
        self.indicator_url = indicator_url
        self.data_baseurl = self.get_data_baseurl(baseurl)
        self.docs_baseurl = self.get_docs_baseurl(baseurl, subfolder)
        self.slugs = []
        self.languages = ['en'] if languages is None else languages
        if translations is not None:
            self.translation_helper = sdg.translations.TranslationHelper(translations)
        else:
            self.translation_helper = None
        self.disaggregation_report_service = sdg.DisaggregationReportService(
            self.outputs,
            languages = self.languages if translate_disaggregations else [],
            translation_helper = self.translation_helper,
            indicator_url = self.indicator_url,
            extra_disaggregations = extra_disaggregations,
        )
        self.metadata_report_service = None
        if metadata_fields is not None and len(metadata_fields) > 0:
            self.metadata_report_service = sdg.MetadataReportService(
                self.outputs,
                languages = self.languages if translate_metadata else [],
                translation_helper = self.translation_helper,
                indicator_url = self.indicator_url,
                metadata_fields = metadata_fields,
            )



    def fix_folder(self, folder, subfolder):
        fixed = '_site'
        if folder is not None:
            fixed = folder
        if subfolder is not None and subfolder != '':
            fixed = os.path.join(fixed, subfolder)
        return fixed


    def get_data_baseurl(self, baseurl):
        fixed = ''
        if baseurl is None or baseurl == '':
            # All links will be relative.
            return ''
        fixed = baseurl
        # Make sure the baseurl starts and ends with a slash.
        if not fixed.startswith('/'):
            fixed = '/' + fixed
        if not fixed.endswith('/'):
            fixed = fixed + '/'
        return fixed


    def get_docs_baseurl(self, baseurl, subfolder):
        fixed = ''
        if baseurl is None or baseurl == '':
            # All links will be relative.
            return ''
        fixed = baseurl
        # Make sure the baseurl starts and ends with a slash.
        if not fixed.startswith('/'):
            fixed = '/' + fixed
        if not fixed.endswith('/'):
            fixed = fixed + '/'
        if subfolder is not None and subfolder != '':
            fixed = fixed + subfolder
        if not fixed.endswith('/'):
            fixed = fixed + '/'
        return fixed


    def generate_documentation(self):
        """Generate the HTML pages for documentation of all of the outputs."""
        pages = []
        for output in self.outputs:
            title = output.get_documentation_title()
            pages.append({
                'title': title,
                'filename': self.create_filename(title),
                'content': output.get_documentation_content(self.languages, self.data_baseurl),
                'description': output.get_documentation_description()
            })
            extras = output.get_documentation_extras()
            pages.extend(extras)

        os.makedirs(self.folder, exist_ok=True)

        for page in pages:
            self.write_documentation(page)

        self.write_index(pages)
        self.write_disaggregation_report()
        self.write_metadata_report()

        # If it exists, copy over the public folder.
        if os.path.isdir('public'):
            shutil.copytree('public', self.folder, dirs_exist_ok=True)

    def create_filename(self, title):
        """Convert a title into a unique filename.

        Parameters
        ----------
        title : string
            A title representing the output

        Returns
        -------
        string
            The title converted into a unique *.html filename
        """
        slug = slugify(title)
        if slug in self.slugs:
            slug = slug + '_'
        if len(slug) > 100:
            slug = slug[0:100]
        self.slugs.append(slug)
        return slug + '.html'


    def write_documentation(self, page):
        """Write a documentation page.

        Parameters
        ----------
        page : dict
            A dict containing "title", "filename", and "content"
        """
        html = self.get_html(page['title'], page['content'])
        self.write_page(page['filename'], html)


    def write_index(self, pages):
        """Write the index page.
        Parameters
        ----------
        pages : list
            A list of dicts containing "title", "filename", and "content"
        """
        html = '<p>' + self.intro + '</p>'

        row_start = '<div class="row">'
        row_end = '</div>'

        # Add all of the output pages.
        card_number = 0
        for page in pages:
            if card_number % 3 == 0:
                html += row_start
            html += self.get_index_card_template().format(
                title=page['title'],
                description=page['description'],
                destination=page['filename'],
                call_to_action='See examples of ' + page['title']
            )
            card_number += 1
            if card_number % 3 == 0:
                html += row_end

        # Add the disaggregation report.
        if card_number % 3 == 0:
            html += row_start
        html += self.get_index_card_template().format(
            title='Disaggregation report',
            description='These tables show information about all the disaggregations used in the data.',
            destination='disaggregations.html',
            call_to_action='See disaggregation report'
        )
        card_number += 1
        if card_number % 3 == 0:
            html += row_end

        # Add the metadata report.
        if self.metadata_report_service is not None and self.metadata_report_service.validate_field_config():
            if card_number % 3 == 0:
                html += row_start
            html += self.get_index_card_template().format(
                title='Metadata report',
                description='These tables show information about the indicators.',
                destination='metadata.html',
                call_to_action='See metadata report'
            )
            card_number += 1
            if card_number % 3 != 0:
                html += row_end

        page_html = self.get_html('Overview', html)
        self.write_page('index.html', page_html)


    def get_index_card_template(self):
        return """
        <div class="col-sm mt-4">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">{title}</h5>
                    <p class="card-text">{description}</p>
                    <a href="{destination}" class="btn btn-primary">{call_to_action}</a>
                </div>
            </div>
        </div>
        """


    def write_disaggregation_report(self):
        service = self.disaggregation_report_service
        store = self.disaggregation_report_service.get_disaggregation_store()

        disaggregation_df = service.get_disaggregations_dataframe()
        disaggregation_table = self.html_from_dataframe(disaggregation_df, table_id='disaggregation-table')
        disaggregation_download_label = 'Download CSV of disaggregations'
        disaggregation_download_file = 'disaggregation-report.csv'
        disaggregation_download = self.get_csv_download(disaggregation_df, disaggregation_download_file, label=disaggregation_download_label)

        indicator_df = service.get_indicators_dataframe()
        indicator_table = self.html_from_dataframe(indicator_df, table_id='indicator-table')
        indicator_download_label = 'Download CSV of indicators'
        indicator_download_file = 'disaggregation-by-indicator-report.csv'
        indicator_download = self.get_csv_download(indicator_df, indicator_download_file, label=indicator_download_label)

        report_html = self.get_html('Disaggregation report', service.get_disaggregation_report_template().format(
            disaggregation_download=disaggregation_download,
            disaggregation_table=disaggregation_table,
            indicator_download=indicator_download,
            indicator_table=indicator_table
        ))
        self.write_page('disaggregations.html', report_html)

        for disaggregation in store:
            self.write_disaggregation_detail_page(store[disaggregation])
            for disaggregation_value in store[disaggregation]['values']:
                self.write_disaggregation_value_detail_page(store[disaggregation]['values'][disaggregation_value])


    def write_disaggregation_detail_page(self, info):
        service = self.disaggregation_report_service
        disaggregation = info['name']
        filename = info['filename']

        values_df = service.get_disaggregation_dataframe(info)
        values_download_label = 'Download CSV of values used in this disaggregation'
        values_download_file = 'values--' + filename.replace('.html', '.csv')
        values_download = self.get_csv_download(values_df, values_download_file, label=values_download_label)
        values_table = self.html_from_dataframe(values_df, table_id='values-table')

        indicators_df = service.get_disaggregation_indicator_dataframe(info)
        indicators_download_label = 'Download CSV of indicators using this disaggregation'
        indicators_download_file = 'indicators--' + filename.replace('.html', '.csv')
        indicators_download = self.get_csv_download(indicators_df, indicators_download_file, label=indicators_download_label)
        indicators_table = self.html_from_dataframe(indicators_df, table_id='indicators-table')

        detail_html = self.get_html('Disaggregation: ' + disaggregation, service.get_disaggregation_detail_template().format(
            values_download=values_download,
            values_table=values_table,
            indicators_download=indicators_download,
            indicators_table=indicators_table
        ))
        self.write_page(filename, detail_html)


    def write_disaggregation_value_detail_page(self, info):
        service = self.disaggregation_report_service
        disaggregation = str(info['disaggregation'])
        disaggregation_value = str(info['name'])
        filename = info['filename']

        df = service.get_disaggregation_value_dataframe(info)
        download_label = 'Download CSV of indicators using this disaggregation value'
        download_file = filename.replace('.html', '.csv')
        download = self.get_csv_download(df, download_file, label=download_label)
        table = self.html_from_dataframe(df, table_id='disaggregation-value-table')

        html = self.get_html(disaggregation + ': ' + disaggregation_value, service.get_disaggregation_value_detail_template().format(
            download=download,
            table=table
        ))
        self.write_page(filename, html)


    def get_csv_filesize(self, filepath):
        st = os.stat(filepath)
        return humanize.naturalsize(st.st_size)


    def get_csv_download(self, df, filename, label='Download CSV'):
        csv_path = os.path.join(self.folder, filename)
        df = self.disaggregation_report_service.remove_links_from_dataframe(df)
        df.to_csv(csv_path, index=False)
        filesize = self.get_csv_filesize(csv_path)
        fileid = filename.split('.')[0]
        return self.get_download_button_template().format(
            filename=filename,
            filesize=filesize,
            label=label,
            fileid=fileid
        )


    def get_download_button_template(self):
        return """
        <div class="my-3">
            <a href="{filename}" role="button" class="btn btn-primary" aria-describedby="{fileid}">{label}</a>
            <div id="{fileid}" class="download-info">Size: {filesize}</div>
        </div>
        """


    def get_html(self, title, content):
        template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="viewport" content="width=device-width, initial-scale=1">

            <title>{title} - {branding}</title>

            <script defer src="https://use.fontawesome.com/releases/v5.15.1/js/all.js"></script>
            <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/open-sdg/open-sdg-table@0.4.0/open-sdg-table.min.css">
            <style>
                .btn-primary {{
                    background-color: #00703c;
                    padding: 8px 10px 7px;
                    border: 2px solid transparent;
                    border-radius: 0;
                    color: #fff;
                    box-shadow: 0 2px 0 #002d18;
                    text-decoration: none;
                }}
                .btn-primary:visited {{
                    color: #fff;
                }}
                .btn-primary:hover, .btn-primary:not(:disabled):not(.disabled):active {{
                    background-color: #005a30;
                    text-decoration: none;
                    border: 2px solid transparent;
                }}
                .btn-primary:focus:not(:active):not(:hover) {{
                    border-color: #fd0;
                    color: #0b0c0c;
                    background-color: #fd0;
                    box-shadow: 0 2px 0 #0b0c0c;
                }}
                a {{
                    color: #1D70B8;
                    text-decoration: underline;
                }}
                a:hover {{
                    color: #003078;
                }}
                a:visited {{
                    color: #4c2c92;
                }}
                .download-info {{
                    margin-left: 12px;
                }}
                .table-striped tbody tr:nth-of-type(2n+1) {{
                    background-color: #f3f2f1;
                }}
                #skiplink {{
                    position: absolute;
                    top: 0;
                    left: 50%;
                    z-index: 10000;
                    width: 250px;
                    margin-left: -125px;
                    padding: 10px;
                    background: white;
                    text-align: center;
                    border: 1px solid #0b0c0c;
                    color: #0b0c0c;
                    display: block;
                }}
                .sr-only-focusable:not(:focus):not(:focus-within) {{
                    position: absolute !important;
                    width: 1px !important;
                    height: 1px !important;
                    padding: 0 !important;
                    margin: -1px !important;
                    overflow: hidden !important;
                    clip: rect(0, 0, 0, 0) !important;
                    white-space: nowrap !important;
                    border: 0 !important;
                }}
            </style>
        </head>
        <body>
            <a class="sr-only-focusable" id="skiplink" href="#main-content" tabindex="0">Skip to main content</a>
            <nav class="navbar navbar-expand-lg navbar-light bg-light">
                <div class="container">
                    <a class="navbar-brand" href="{baseurl}index.html">{branding}</a>
                </div>
            </nav>
            <main id="main-content" role="main">
                <div class="container">
                    <h1 style="margin:20px 0">{title}</h1>
                    <div>
                        {content}
                    </div>
                </div>
            </div>
            <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
            <script src="https://cdn.datatables.net/1.10.23/js/jquery.dataTables.min.js"></script>
            <script src="https://cdn.jsdelivr.net/gh/open-sdg/open-sdg-table@0.4.0/open-sdg-table.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js" integrity="sha384-Q6E9RHvbIyZFJoft+2mJbHaEWldlvI9IOYy5n3zV9zzTtmI3UksdQRVvoxMfooAo" crossorigin="anonymous"></script>
            <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js" integrity="sha384-wfSDF2E50Y2D1uUdj0O3uMBJnjuUD4Ih7YwaYd1iqfktj0Uod8GCExl3Og8ifwB6" crossorigin="anonymous"></script>
            <script>
            if (typeof sdgBuild !== 'undefined' && sdgBuild.tables) {{
                var tableIds = Object.keys(sdgBuild.tables);
                for (var i = 0; i < tableIds.length; i++) {{
                    var tableId = tableIds[i];
                    $('#' + tableId).openSdgTable(sdgBuild.tables[tableId]).find('td').each(function() {{
                        if (!isNaN($(this).text())) {{
                            $(this).css('text-align', 'right');
                        }}
                    }})
                }}
            }}
            </script>
        </html>
        """
        return template.format(branding=self.branding, title=title, content=content, baseurl=self.docs_baseurl)


    def html_from_dataframe(self, df, table_id='docs-table', escape=False, total=True):
        """Generate an HTML table from a DataFrame.

        Paramters
        ---------
        df : DataFrame
            The dataframe itself.
        table_id : string
            An identifier for the table, which should be unique on this web page.
        escape : boolean
            Whether or not to escape content. If the cells need to contain
            HTML, this should be False. Defaults to False.
        total : boolean
            Whether or not to display a "Total rows" count above the table.
            Defaults to True.
        """
        html = ''
        if total:
            html += """
                <div class="total-rows">
                    Total rows: <span class="total">{}</span>
                </div>
                """.format(len(df))
        html += df.to_html(escape=escape, index=False, classes='table table-striped table-bordered', table_id=table_id)
        html += self.javascript_from_dataframe(df, table_id)
        return html


    def javascript_from_dataframe(self, df, table_id):
        return """
            <script type="text/javascript">
            var sdgBuild = sdgBuild || {{}};
            sdgBuild.tables = sdgBuild.tables || {{}};
            sdgBuild.tables['{}'] = {};
            </script>
            """.format(table_id, df.to_json(orient='records'))


    def write_page(self, filename, html):
        """Write a page.

        Parameters
        ----------
        filename : string
            The path on disk to write the file to
        html : string
            The HTML to write to file
        """
        filepath = os.path.join(self.folder, filename)
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(html)

    def write_metadata_report(self):
        service = self.metadata_report_service

        if service is None or not service.validate_field_config():
            return

        store = self.metadata_report_service.get_metadata_field_store()

        metadata_field_df = service.get_metadata_fields_dataframe()
        metadata_field_table = self.html_from_dataframe(metadata_field_df, table_id='metadata-field-table')
        metadata_field_download_label = 'Download CSV of disaggregations'
        metadata_field_download_file = 'metadata_field-report.csv'
        metadata_field_download = self.get_csv_download(metadata_field_df, metadata_field_download_file, label=metadata_field_download_label)

        indicator_df = service.get_indicators_dataframe()
        indicator_table = self.html_from_dataframe(indicator_df, table_id='indicator-table')
        indicator_download_label = 'Download CSV of indicators'
        indicator_download_file = 'metadata_field-by-indicator-report.csv'
        indicator_download = self.get_csv_download(indicator_df, indicator_download_file, label=indicator_download_label)

        report_html = self.get_html('Metadata report', service.get_metadata_field_report_template().format(
            metadata_field_download=metadata_field_download,
            metadata_field_table=metadata_field_table,
            indicator_download=indicator_download,
            indicator_table=indicator_table
        ))
        self.write_page('metadata.html', report_html)

        for metadata_field in store:
            self.write_metadata_field_detail_page(store[metadata_field])
            for metadata_field_value in store[metadata_field]['values']:
                self.write_metadata_field_value_detail_page(store[metadata_field]['values'][metadata_field_value])

    def write_metadata_field_detail_page(self, info):
        service = self.metadata_report_service
        metadata_field = info['name']
        filename = info['filename']
        label = info['label']

        values_df = service.get_metadata_field_dataframe(info)
        values_download_label = 'Download CSV of values used in this metadata field'
        values_download_file = 'values--' + filename.replace('.html', '.csv')
        values_download = self.get_csv_download(values_df, values_download_file, label=values_download_label)
        values_table = self.html_from_dataframe(values_df, table_id='values-table')

        indicators_df = service.get_metadata_field_indicator_dataframe(info)
        indicators_download_label = 'Download CSV of indicators using this metadata field'
        indicators_download_file = 'indicators--' + filename.replace('.html', '.csv')
        indicators_download = self.get_csv_download(indicators_df, indicators_download_file, label=indicators_download_label)
        indicators_table = self.html_from_dataframe(indicators_df, table_id='indicators-table')

        detail_html = self.get_html('Metadata field: ' + label, service.get_metadata_field_detail_template().format(
            values_download=values_download,
            values_table=values_table,
            indicators_download=indicators_download,
            indicators_table=indicators_table
        ))
        self.write_page(filename, detail_html)

    def write_metadata_field_value_detail_page(self, info):
        service = self.metadata_report_service
        metadata_field = str(info['field'])
        metadata_field_value = str(info['name'])
        field_label = info['field_label']
        filename = info['filename']

        df = service.get_metadata_field_value_dataframe(info)
        download_label = 'Download CSV of indicators using this metadata field value'
        download_file = filename.replace('.html', '.csv')
        download = self.get_csv_download(df, download_file, label=download_label)
        table = self.html_from_dataframe(df, table_id='metadata-field-value-table')

        html = self.get_html(field_label + ': ' + metadata_field_value, service.get_metadata_field_value_detail_template().format(
            download=download,
            table=table
        ))
        self.write_page(filename, html)
