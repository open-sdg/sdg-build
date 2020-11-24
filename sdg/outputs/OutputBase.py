import os
from sdg.IndicatorOptions import IndicatorOptions
from sdg.translations import TranslationInputBase
from sdg.translations import TranslationHelper

class OutputBase:
    """Base class for destinations of SDG data/metadata."""


    def __init__(self, inputs, schema, output_folder='_site', translations=None,
                 indicator_options=None):
        """Constructor for OutputBase.

        inputs: list
            A list of InputBase (or descendent) classes.
        schema: SchemaInputBase
            An instance of SchemaInputBase (or descendant).
        output_folder: string
            The path to where the output files should be created.
        translations: list
            A list of TranslationInputBase (or descendant) classes.
        indicator_options: IndicatorOptions
            Optional options that are passed into each Indicator object.
            Allows particular outputs to affect the data/metadata of indicators.
        """
        if translations is None:
            translations = []
        self.indicator_options = IndicatorOptions() if indicator_options is None else indicator_options

        self.indicators = self.merge_inputs(inputs)
        self.schema = schema
        self.output_folder = output_folder
        self.translations = translations
        # Safety code to ensure translations are a list of inputs.
        if isinstance(self.translations, TranslationInputBase):
            self.translations = [translations]
        # Create a translation helper.
        self.translation_helper = TranslationHelper(self.translations)


    def execute(self, language=None):
        """Write the SDG output to disk.

        Parameters
        ----------
        language : string
            If specified, a particular language that this build is using. If
            not specified, it is assumed the build is not translated.
        """
        # Keep a backup of the output folder.
        original_output_folder = self.output_folder

        if language == 'untranslated':
            self.output_folder = os.path.join(original_output_folder, 'untranslated')
            language = None

        if language:
            # Temporarily change the output folder.
            self.output_folder = os.path.join(original_output_folder, language)
            # Translate each indicator.
            for inid in self.indicators:
                self.indicators[inid].translate(language, self.translation_helper)

        # Now perform the build.
        status = self.build(language)

        # Cleanup afterwards.
        self.output_folder = original_output_folder

        return status


    def build(self, language=None):
        """Write the SDG output to disk.

        Parameters
        ----------
        language : string
            If specified, a particular language that this build is using. If
            not specified, it is assumed the build is not translated.
        """
        raise NotImplementedError


    def merge_inputs(self, inputs):
        """Take the results of many inputs and merge into a single dict of indicators."""
        merged_indicators = {}
        for input in inputs:
            # Fetch the input.
            input.execute(self.indicator_options)
            # Merge the results.
            for inid in input.indicators:
                if inid not in merged_indicators:
                    # If this indicator is new, simply use it.
                    merged_indicators[inid] = input.indicators[inid]
                else:
                    # Otherwise if this indicator was already there, it needs to
                    # be "merged" in. To do this, we manually set data, metadata,
                    # and name. Note that all of these "set" methods abort if
                    # the value is None, so we don't need to check for None here.
                    merged_indicators[inid].set_data(input.indicators[inid].data)
                    merged_indicators[inid].set_meta(input.indicators[inid].meta)
                    merged_indicators[inid].set_name(input.indicators[inid].name)

        for inid in merged_indicators:
            # Now that everything has been merged, we have to make sure that
            # minimum data and metadata is set.
            merged_indicators[inid].require_data()
            merged_indicators[inid].require_meta(self.minimum_metadata(merged_indicators[inid]))
            # And because this may affect data, we have to re-do headlines and
            # edges.
            merged_indicators[inid].set_headline()
            merged_indicators[inid].set_edges()

        return merged_indicators


    def validate(self):
        """Validate the data and metadata for the indicators."""

        status = True
        for inid in self.indicators:
            status = status & self.schema.validate(self.indicators[inid])

        return status


    def execute_per_language(self, languages):
        """This helper triggers calls to execute() for each language."""
        # Make sure we keep a copy of the originals before doing any translations.
        status = True
        for language in languages:
            status = status & self.execute(language)

        return status


    def minimum_metadata(self, indicator):
        """Each subclass can specify it's own minimum viable metadata values.

        Parameters
        ----------
        indicator : Indicator
            The indicator instance to set minimum metadata for

        Returns
        -------
        dict
            Key/value pairs for minimum required metadata
        """
        return {}


    def get_indicator_ids(self):
        """Get a list of all the indicator ids that are included in this output."""
        return self.indicators.keys()


    def get_indicator_by_id(self, indicator_id):
        """Get one specific Indicator object, by its id.

        Parameters
        ----------
        indicator_id : str
            The indicator id of the Indicator object being sought.

        Returns
        -------
        Indicator
            An instance of the Indicator class.
        """
        if indicator_id in self.indicators:
            return self.indicators[indicator_id]
        else:
            raise KeyError('The indicator "' + indicator_id + '" could not be found in this output.')


    def get_documentation_title(self):
        """Get a descriptive title for this output, for documentation purposes.

        Returns
        -------
        string
            The descriptive title for this output.
        """
        # This should be overridden, but fallback to the name of the class.
        return type(self).__name__


    def get_documentation_content(self, languages=None, baseurl=''):
        """Get detailed content for this output, for documentation purposes.

        Parameters
        ----------
        languages : list or None
            A list of languages, in the case of translated builds, or None otherwise

        Returns
        -------
        string
            The detailed content for this output, in HTML format.
        """
        # This should be overridden, but fallback to generic text.
        return '<p>Documentation unavailable - must be provided by get_documentation_content().</p>'


    def get_documentation_indicator_ids(self):
        """Get a list of indicator ids to use as examples in the documentation.

        Returns
        -------
        list
            The list of dash-delimited indicators ids. (1-1-1, 1-2-1, etc)
        """
        return list(self.get_indicator_ids())[:2]


    def get_documentation_description(self):
        """Get a description of this output, for documentation purposes.

        Returns
        -------
        string
            The description for this output.
        """
        return 'Description unavailable - must be provided by get_documentation_description().'


    def get_documentation_extras(self):
        """Get any additional pages necessary for documentation.

        Returns
        -------
        list
            List of dicts containing three strings: title, path, and HTML content.
            For example:
            [
                {
                    'title': 'My hello world page',
                    'path': 'my-subfolder/hello-world.html',
                    'content': '<p>Hello world</p>'),
                },
                {
                    'title': 'My other stuff page',
                    'path': 'my-subfolder/other-stuff.html',
                    'content': '<p>Other stuff</p>'),
                }
            ]
        """
        return []
