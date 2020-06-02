import os
import sdg
import numpy
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

        os.makedirs(self.folder, exist_ok=True)

        for page in pages:
            self.write_documentation(page)

        self.write_index(pages)


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

        html += '</div>'
        page_html = self.get_html('Overview', html)
        self.write_page('index.html', page_html)


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
