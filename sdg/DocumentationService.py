import os
import sdg
from slugify import slugify
from jinja2 import Template

class DocumentationService:
    """HTML generation to document outputs built with this library.

    Note that this is meant to document particular builds, not the library in
    general. The idea is that each time this library is used to build/convert
    some SDG-related data, this class can be used to generate human-friendly
    HTML pages documenting the specifics of the build (such as endpoint URLs).
    """


    def __init__(self, outputs, folder='_site', title='Build docs', languages=None, intro=''):
        """Constructor for the DocumentationService class.

        Parameters
        ----------
        outputs : list
            List of objects inheriting from OutputBase
        """
        self.outputs = outputs
        self.folder = folder
        self.title = title
        self.intro = intro
        self.slugs = []
        self.languages = [] if languages is None else languages


    def generate_documentation(self):
        """Generate the HTML pages for documentation of all of the outputs."""
        pages = []
        for output in self.outputs:
            title = output.get_documentation_title()
            content = output.get_documentation_content(self.languages)
            pages.append({
                'title': title,
                'filename': self.create_filename(title),
                'content': content
            })

        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

        for page in pages:
            self.write_documentation(page)

        self.write_index(pages)


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


    def write_documentation(self, page):
        """Write a documentation page.

        Parameters
        ----------
        page : dict
            A dict containing "title", "filename", and "content"
        """
        html = self.get_html(self.title + ' - ' + page['title'], page['content'])
        self.write_page(page['filename'], html)


    def write_index(self, pages):
        """Write the index page.

        Parameters
        ----------
        pages : list
            A list of dicts containing "title", "filename", and "content"
        """
        index_template = Template("""
        <div>
            {{ intro }}
        </div>
        <ul>
            {% for page in pages %}
            <li><a href="{{ page.filename }}">{{ page.title }}</a></li>
            {% endfor %}
        </ul>
        """)
        index_html = index_template.render(intro=self.intro, pages=pages)
        page_html = self.get_html(self.title, index_html)
        self.write_page('index.html', page_html)


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


    def get_html(self, title, content):
        template = Template("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{{ title }}</title>
            <link rel="stylesheet" href="//fonts.googleapis.com/css?family=Roboto:300,300italic,700,700italic">
            <link rel="stylesheet" href="//cdnjs.cloudflare.com/ajax/libs/normalize/5.0.0/normalize.css">
            <link rel="stylesheet" href="//cdnjs.cloudflare.com/ajax/libs/milligram/1.3.0/milligram.css">
        </head>
        <body>
            <div class="container">
                <h1>{{ title }}</h1>
                {{ content }}
            </div>
        </body>
        </html>
        """)
        return template.render(title=title, content=content)
