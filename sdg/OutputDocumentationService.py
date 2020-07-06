import os
import sdg
import pandas as pd
from slugify import slugify

class OutputDocumentationService:
    """HTML generation to document outputs built with this library.

    Note that this is meant to document particular builds, not the library in
    general. The idea is that each time this library is used to build/convert
    some SDG-related data, this class can be used to generate human-friendly
    HTML pages documenting the specifics of the build (such as endpoint URLs).
    """


    def __init__(self, outputs, folder='_site', branding='Build docs',
                 languages=None, intro='', translations=None, indicator_url=None):
        """Constructor for the OutputDocumentationService class.

        Parameters
        ----------
        outputs : list
            Required list of objects inheriting from OutputBase. Each output
            will receive its own documentation page (or pages).
        folder : string
            Optional folder in which to create the documentation pages. Defaults
            to the "_site" folder.
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
        """
        self.outputs = outputs
        self.folder = folder
        self.branding = branding
        self.intro = intro
        self.indicator_url = indicator_url
        self.slugs = []
        self.languages = ['en'] if languages is None else languages
        if translations is not None:
            self.translation_helper = sdg.translations.TranslationHelper(translations)
        else:
            self.translation_helper = None
        self.disaggregation_report_service = sdg.DisaggregationReportService(
            self.outputs,
            languages = self.languages,
            translation_helper = self.translation_helper,
            indicator_url = self.indicator_url
        )


    def generate_documentation(self):
        """Generate the HTML pages for documentation of all of the outputs."""
        pages = []
        for output in self.outputs:
            title = output.get_documentation_title()
            pages.append({
                'title': title,
                'filename': self.create_filename(title),
                'content': output.get_documentation_content(self.languages),
                'description': output.get_documentation_description()
            })
            extras = output.get_documentation_extras()
            pages.extend(extras)

        os.makedirs(self.folder, exist_ok=True)

        for page in pages:
            self.write_documentation(page)

        self.write_index(pages)
        self.write_disaggregation_report()


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
                call_to_action='See examples'
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
            destination='disaggregations',
            call_to_action='See report'
        )
        card_number += 1
        if card_number % 3 == 0:
            html += row_end

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
        os.makedirs(os.path.join(self.folder, 'disaggregations'), exist_ok=True)
        service = self.disaggregation_report_service
        store = self.disaggregation_report_service.get_disaggregation_store()

        disaggregation_df = service.get_disaggregations_dataframe()
        disaggregation_table = disaggregation_df.to_html(escape=False, index=False, classes="table table-striped table-bordered tablesorter")
        disaggregation_download = self.get_csv_download(disaggregation_df, 'disaggregations', 'disaggregation-report.csv')

        indicator_df = service.get_indicators_dataframe()
        indicator_table = indicator_df.to_html(escape=False, index=False, classes="table table-striped table-bordered tablesorter")
        indicator_download = self.get_csv_download(indicator_df, 'disaggregations', 'disaggregation-by-indicator-report.csv')

        report_html = self.get_html('Disaggregation report', service.get_disaggregation_report_template().format(
            disaggregation_download=disaggregation_download,
            disaggregation_table=disaggregation_table,
            indicator_download=indicator_download,
            indicator_table=indicator_table
        ))
        report_path = os.path.join('disaggregations', 'index.html')
        self.write_page(report_path, report_html)

        for disaggregation in store:
            self.write_disaggregation_detail_page(store[disaggregation], service)


    def write_disaggregation_detail_page(self, info, service):
        disaggregation = info['name']
        filename = info['filename']

        values_df = service.get_disaggregation_dataframe(info)
        values_download = self.get_csv_download(values_df, 'disaggregations', 'values--' + filename.replace('.html', '.csv'))
        values_table = values_df.to_html(index=False, classes="table table-striped table-bordered tablesorter")

        indicators_df = service.get_disaggregation_indicator_dataframe(info)
        indicators_download = self.get_csv_download(indicators_df, 'disaggregations', 'indicators--' + filename.replace('.html', '.csv'))
        indicators_table = indicators_df.to_html(escape=False, index=False, classes="table table-striped table-bordered tablesorter")

        detail_html = self.get_html('Disaggregation: ' + disaggregation, service.get_disaggregation_detail_template().format(
            values_download=values_download,
            values_table=values_table,
            indicators_download=indicators_download,
            indicators_table=indicators_table
        ))
        self.write_page(os.path.join('disaggregations', filename), detail_html)


    def get_csv_download(self, df, path, filename):
        csv_path = os.path.join(self.folder, path, filename)
        df = self.disaggregation_report_service.remove_links_from_dataframe(df)
        df.to_csv(csv_path, index=False)
        return self.get_download_button_template().format(filename=filename)


    def get_download_button_template(self):
        return """
        <div class="my-3">
            <a href="{filename}" class="btn btn-primary">Download CSV</a>
        </div>
        """


    def get_html(self, title, content):
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="viewport" content="width=device-width, initial-scale=1">

            <title>{branding} - {title}</title>

            <script defer src="https://use.fontawesome.com/releases/v5.0.2/js/all.js"></script>
            <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/jquery.tablesorter/2.31.3/css/theme.bootstrap_4.min.css" integrity="sha256-vFn0MM8utz2N3JoNzRxHXUtfCJLz5Pb9ygBY2exIaqg=" crossorigin="anonymous" />
        </head>
        <body>
            <nav class="navbar navbar-expand-lg navbar-light bg-light">
                <div class="container">
                    <a class="navbar-brand" href="index.html">{branding}</a>
                </div>
            </nav>
            <main role="main">
                <div class="container">
                    <h1 style="margin:20px 0">{title}</h1>
                    <div>
                        {content}
                    </div>
                </div>
            </div>
            <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
            <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery.tablesorter/2.31.3/js/jquery.tablesorter.min.js" integrity="sha256-dtGH1XcAyKopMui5x20KnPxuGuSx9Rs6piJB/4Oqu6I=" crossorigin="anonymous"></script>
            <script>$(".tablesorter").tablesorter({{
                theme: 'bootstrap'
            }});</script>
        </html>
        """
        return template.format(branding=self.branding, title=title, content=content)


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
