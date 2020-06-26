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


    def __init__(self, outputs, folder='_site', branding='Build docs', languages=None, intro=''):
        """Constructor for the OutputDocumentationService class.

        Parameters
        ----------
        outputs : list
            List of objects inheriting from OutputBase
        """
        self.outputs = outputs
        self.folder = folder
        self.branding = branding
        self.intro = intro
        self.slugs = []
        self.languages = [] if languages is None else languages


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
        html += '<div class="container">'

        last_page = len(pages) - 1
        for num, page in enumerate(pages):
            if num % 3 == 0:
                html += '<div class="row">'
            title = '<h5 class="card-title">' + page['title'] + '</h5>'
            description = '<p class="card-text">' + page['description'] + '</p>'
            link = '<a href="' + page['filename'] + '" class="btn btn-primary">See examples</a>'
            html += '<div class="col-sm"><div class="card"><div class="card-body">' + title + description + link + '</div></div></div>'
            if (num % 3 == 0 and num > 0) or num == last_page:
                html += '</div>'

        html += """
                <div class="row">
                    <div class="col-sm">
                        <div class="card">
                            <div class="card-body">
                                <h5 class="card-title">Disaggregation report</h5>
                                <p class="card-text">These tables show information about all the disaggregations used in the data.</p>
                                <a href="disaggregations" class="btn btn-primary">See report</a>
                            </div>
                        </div>
                    </div>
                </div>
                """
        html += '</div>'


        page_html = self.get_html('Overview', html)
        self.write_page('index.html', page_html)


    def write_disaggregation_report(self):
        os.makedirs(os.path.join(self.folder, 'disaggregations'), exist_ok=True)
        # Get a full list of indicators by looking through all the outputs.
        indicators = {}
        for output in self.outputs:
            for indicator_id in output.get_indicator_ids():
                indicators[indicator_id] = output.get_indicator_by_id(indicator_id)

        all_disaggregations = {}
        for indicator_id in indicators:
            for series in indicators[indicator_id].get_all_series():
                disaggregations = series.get_disaggregations()
                for disaggregation in disaggregations:
                    if disaggregation not in all_disaggregations:
                        all_disaggregations[disaggregation] = {
                            'values': {},
                            'indicators': {},
                        }
                    value = disaggregations[disaggregation]
                    if pd.isna(value):
                        continue
                    if value not in all_disaggregations[disaggregation]['values']:
                        all_disaggregations[disaggregation]['values'][value] = 0
                    all_disaggregations[disaggregation]['values'][value] += 1
                    all_disaggregations[disaggregation]['indicators'][indicator_id] = True

        df_rows = []
        for disaggregation in all_disaggregations:
            detail_filename = self.create_filename(disaggregation)
            self.write_disaggregation_detail_page(disaggregation, detail_filename, all_disaggregations[disaggregation])
            df_rows.append({
                'Disaggregation': disaggregation,
                'Number of indicators': len(all_disaggregations[disaggregation]['indicators'].keys()),
                'Number of values': len(all_disaggregations[disaggregation]['values'].keys()),
                'Details': '<a href="' + detail_filename + '">Details</a>',
            })
        df = pd.DataFrame(df_rows)
        df.sort_values(by=['Disaggregation'], inplace=True)
        report_html = self.get_html('Disaggregation report', df.to_html(escape=False, index=False, classes="table table-striped"))
        report_path = os.path.join('disaggregations', 'index.html')
        self.write_page(report_path, report_html)


    def write_disaggregation_detail_page(self, disaggregation, filepath, info):
        values_rows = []
        for value in info['values']:
            values_rows.append({
                'Value': value,
                'Number of instances': info['values'][value],
            })
        values_df = pd.DataFrame(values_rows)
        values_df.sort_values(by=['Value'], inplace=True)
        values_html = '<h2>Values used in disaggregation</h2>' + values_df.to_html(index=False, classes="table table-striped")

        indicators_rows = []
        for indicator_id in info['indicators']:
            indicators_rows.append({
                'Indicator': indicator_id
            })
        indicators_df = pd.DataFrame(indicators_rows)
        indicators_df.sort_values(by=['Indicator'], inplace=True)
        indicators_html = '<h2>Indicators using disaggregation</h2>' + indicators_df.to_html(index=False, classes="table table-striped")

        detail_html = self.get_html('Disaggregation: ' + disaggregation, values_html + indicators_html)
        self.write_page(os.path.join('disaggregations', filepath), detail_html)


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
        </body>
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
