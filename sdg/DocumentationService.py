import os
import sdg
from slugify import slugify
from jinja2 import Environment, PackageLoader
env = Environment(loader=PackageLoader('sdg', 'templates'))

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


    def write_page(self, filename, template_file, variables):
        """Write a page.

        Parameters
        ----------
        filename : string
            The path on disk to write the file to
        template : string
            Which file in the "templates" folder to use
        variables : dict
            A dict of variables to pass into the template
        """
        template = env.get_template(template_file)
        html = template.render(**variables)
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
        self.write_page(page['filename'], 'documentation.html', {
            'title': page['title'],
            'content': page['content'],
        })

    def write_index(self, pages):
        """Write the index page.

        Parameters
        ----------
        pages : list
            A list of dicts containing "title", "filename", and "content"
        """
        self.write_page('index.html', 'index.html', {
            'title': self.title,
            'intro': self.intro,
            'pages': pages,
        })


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
