import copy
import json
import sdg
import pandas as pd
import numpy as np
import collections.abc
from sdg.translations import TranslationHelper
from sdg.Loggable import Loggable

class Indicator(Loggable):
    """Data model for SDG indicators."""

    def __init__(self, inid, name=None, data=None, meta=None, options=None, logging=None):
        """Constructor for the SDG indicator instances.

        Parameters
        ----------
        inid : string
            The three-part dash-delimited ID (eg, 1-1-1).
        name : string
            The name of the indicator.
        data : Dataframe
            Dataframe of all data, with at least "Year" and "Value" columns.
        meta : dict
            Dict of fielded metadata.
        options : IndicatorOptions
            Output-specific options provided by the OutputBase class.
        """
        Loggable.__init__(self, logging=logging)
        self.inid = inid
        self.name = name
        self.data = data
        self.meta = meta
        self.options = sdg.IndicatorOptions() if options is None else options
        self.set_headline()
        self.set_edges()
        self.translations = {}
        self.serieses = {}
        self.data_matching_schema = {}


    def has_name(self):
        """Check to see if the indicator has a name.

        Returns
        -------
        boolean
            True if the indicator has a name.
        """
        return self.name is not None


    def get_name(self):
        """Get the name of the indicator if known, or otherwise the id.

        Returns
        -------
        string
            The name (or id) of the indicator.
        """
        return self.name if self.name is not None else self.inid


    def set_name(self, name=None):
        """Set the name of the indicator."""
        if name is not None:
            self.name = name


    def has_data(self):
        """Check to see if this indicator has data.

        Returns
        -------
        boolean
            True if the indicator has data.
        """
        if self.data is None:
            # If data has not been set yet, return False.
            return False
        # Otherwise return False if there are no rows in the dataframe.
        return False if len(self.data) < 1 else True


    def has_meta(self):
        """Check to see if this indicator has metadata.

        Returns
        -------
        boolean
            True if the indicator has metadata.
        """
        return False if self.meta is None else True


    def set_data(self, val):
        """Set the indicator data if a value is passed.

        Parameters
        ----------
        val : Dataframe or None
        """
        # If empty or None, do nothing.
        if val is None or not isinstance(val, pd.DataFrame) or val.empty:
            return

        self.data = val
        self.set_headline()
        self.set_edges()


    def set_meta(self, val):
        """Set the indicator metadata if a value is passed.

        Parameters
        ----------
        val : Dict or None
        """
        if val is not None and val:
            if self.has_meta():
                self.meta = self.deepUpdate(self.meta, val)
            else:
                self.meta = val


    def deepUpdate(self, d, u):
        """Recursive utility method for merging nested dicts."""
        for k, v in u.items():
            if isinstance(v, collections.abc.Mapping):
                d[k] = self.deepUpdate(d.get(k, {}), v)
            else:
                d[k] = v
        return d


    def set_headline(self):
        """Calculate and set the headline for this indicator."""
        self.require_data()
        non_disaggregation_columns = self.options.get_non_disaggregation_columns()
        self.headline = sdg.data.filter_headline(self.data, non_disaggregation_columns)


    def has_headline(self):
        """Report whether this indicator has a headline."""
        return hasattr(self, 'headline') and not self.headline.empty


    def set_edges(self):
        """Calculate and set the edges for this indicator."""
        self.require_data()
        non_disaggregation_columns = self.options.get_non_disaggregation_columns()
        self.edges = sdg.edges.edge_detection(self.inid, self.data, non_disaggregation_columns)


    def has_edges(self):
        """Report whether this indicator has edges."""
        return hasattr(self, 'edges') and not self.edges.empty


    def get_goal_id(self):
        """Get the goal number for this indicator.

        Returns
        -------
        string
            The number of the goal.
        """
        return self.inid if self.is_standalone() else self.inid.split('-')[0]


    def get_target_id(self):
        """Get the target id for this indicator.

        Returns
        -------
        string
            The target id, dot-delimited.
        """
        return self.inid if self.is_standalone() else '.'.join(self.inid.split('-')[0:2])


    def get_indicator_id(self):
        """Get the indicator id for this indicator (dot-delimited version).

        Returns
        -------
        string
            The indicator id, dot-delimited.
        """
        return self.inid if self.is_standalone() else self.inid.replace('-', '.')


    def require_meta(self, minimum_metadata=None):
        """Ensure the metadata for this indicator has minimum necessary values.

        Parameters
        ----------
        minimum_metadata : Dict
            Key/value pairs of minimum metadata for this indicator.
        """
        if minimum_metadata is None:
            minimum_metadata = {}

        if self.meta is None:
            self.meta = minimum_metadata
        else:
            for key in minimum_metadata:
                if key not in self.meta:
                    self.meta[key] = minimum_metadata[key]


    def require_data(self):
        """Ensure at least an empty dataset for this indicator."""
        if self.data is None:
            df = pd.DataFrame({'Year':[], 'Value':[]})
            # Enforce the order of columns.
            cols = ['Year', 'Value']
            df = df[cols]
            self.data = df


    def language(self, language=None):
        """Return a translated copy of this indicator.

        Requires that the translate() method be run first.
        """
        if language is None:
            return self
        if language in self.translations:
            return self.translations[language]
        raise ValueError('Language ' + language + ' has not been translated.')


    def translate(self, language, translation_helper):
        """Translate the entire indicator into a particular language.

        Parameters
        ----------
        language : string
            The language code to translate into.
        translation_helper : TranslationHelper
            The instance of TranslationHelper to perform the translations.
        """
        # Already done? Abort now.
        if language in self.translations:
            return

        # Start with an empty indicator.
        indicator = Indicator(inid=self.inid, options=self.options)

        # Translation callbacks for below.
        def translate_meta(text):
            # Recursively handle lists.
            if isinstance(text, list):
                return [translate_meta(value) for value in text]
            # Recursively handle dicts.
            if isinstance(text, dict):
                return {key: translate_meta(value) for (key, value) in text.items()}
            # Otherwise treat as a string.
            return translation_helper.translate(text, language, default_group='data')
        def translate_data(text, column):
            return translation_helper.translate(text, language, default_group=[column, 'data'])
        def translate_data_columns(text):
            # We only want to translate disaggregation columns, for the most part. However,
            # a special case is the COMPOSITE_BREAKDOWN disaggregation, often found in SDMX.
            # We assume that this will be altered at the presentation layer, so we do not
            # translated it here.
            special_columns = self.options.get_non_disaggregation_columns() + ['COMPOSITE_BREAKDOWN']
            if text in special_columns:
                return text
            return translation_helper.translate(text, language, default_group=[text, 'data'])

        # Translate the name.
        indicator.set_name(translate_meta(self.name))

        # Translate the metadata.
        meta_copy = copy.deepcopy(self.meta)
        # But first do overrides of "subfolder" metadata.
        if language in meta_copy and isinstance(meta_copy[language], dict):
            meta_copy.update(meta_copy[language])
            del meta_copy[language]
        # Now we can actually translate.
        for key in meta_copy:
            meta_copy[key] = translate_meta(meta_copy[key])
        indicator.set_meta(meta_copy)

        # Translate the data cells and headers.
        data_copy = copy.deepcopy(self.data)
        for column in data_copy:
            data_copy[column] = data_copy[column].apply(lambda x: translate_data(x, column))
        data_copy.rename(mapper=translate_data_columns, axis='columns', inplace=True)
        indicator.set_data(data_copy)

        # Finally place the translation for later access.
        self.translations[language] = indicator


    def is_complete(self):
        """Decide whether this indicator can be considered "complete".

        Returns
        -------
        boolean
            True if the indicator can be considered "complete", False otherwise.
        """
        # First, check for an open-sdg-style "reporting_status" metadata field,
        # for a value of "complete".
        reporting_status = self.get_meta_field_value('reporting_status')
        if reporting_status is not None and reporting_status == 'complete':
            return True
        # If there was some other reporting status, assume not complete.
        elif reporting_status is not None:
            return False
        # Otherwise fall back to whether the indicator has data and metadata.
        else:
            return self.has_data() and self.has_meta()


    def is_statistical(self):
        """Decide whether this indicator can be considered "statistical".

        Returns
        -------
        boolean
            True if the indicator can be considered statistical, False otherwise.
        """
        # First, check for an open-sdg-style "data_non_statistical" metadata field.
        non_statistical = self.get_meta_field_value('data_non_statistical')
        if non_statistical is None or non_statistical == False:
            return True
        # If the the indicator was explicitly non-statistical, return False.
        elif non_statistical == True:
            return False
        # Otherwise fall back to whether the indicator has data.
        else:
            return self.has_data()


    def is_standalone(self):
        """Decide whether this indicator is standalone - ie, not part of the SDGs.

        Returns
        -------
        boolean
            True if the indicator should be considered standalone, False otherwise.
        """
        standalone = self.get_meta_field_value('standalone')
        if standalone is None or standalone == False:
            return False
        else:
            return True


    def get_meta_field_value(self, field):
        """Get the value for a metadata field.

        Parameters
        ----------
        field : string
            The key of the metadata field.

        Return : string or None
            The value of the specified field or just None if the field could not
            be found.
        """

        if not self.has_meta():
            return None

        if field not in self.meta:
            return None

        return self.meta[field]


    def get_all_series(self, use_cache=True, language=None):
        """Get all of the series present in this indicator's data.

        Parameters
        ----------
        use_cache : boolean
            Whether to cache the results of the function.
        language: string
            The caching system can consider this optional language.

        Returns
        -------
        list
            List of Series objects.
        """
        # Safety code for empty dataframes.
        if self.data.empty:
            return []
        # Cache for efficiency.
        if language is None:
            language = ''
        if language in self.serieses and use_cache:
            return self.serieses[language]

        # Assume "disaggregations" are everything except 'Year' and 'Value'.
        aggregating_columns = ['Year', 'Value']
        grouping_columns = [column for column in self.data.columns if column not in aggregating_columns]

        if len(grouping_columns) == 0:
            series = sdg.Series({}, self.get_indicator_id(), logging=self.logging)
            for index, row in self.data.iterrows():
                series.add_value(row['Year'], row['Value'])
            return [series]

        def row_to_series(row):
            disaggregations = row[grouping_columns].to_dict()
            series = sdg.Series(disaggregations, self.get_indicator_id(), logging=self.logging)
            for year, value in zip(row['Year'], row['Value']):
                series.add_value(year, value)
            return series

        # NaN must be replaced with '' so that it can be grouped by.
        grouped = self.data.replace(np.nan, '', regex=True)
        # Group by disaggreations to get each unique combination.
        grouped = grouped.groupby(grouping_columns, as_index=False)[aggregating_columns].agg(lambda x: list(x))
        # Convert to a list of Series objects.
        grouped['series_objects'] = grouped.apply(row_to_series, axis=1)
        self.serieses[language] = grouped['series_objects'].tolist()
        return self.serieses[language]


    def get_data_matching_schema(self, data_schema, data=None, use_cache=True, language=None):
        if data is None:
            data = self.data
        # Safety code for empty dataframes.
        if data.empty:
            return data
        # Cache for efficiency.
        if language is None:
            language = ''
        schema = data_schema.get_schema_for_indicator(self)
        cache_key = language + str(schema.to_dict())
        if use_cache and cache_key in self.data_matching_schema:
            return self.data_matching_schema[cache_key]

        columns_in_data = data.columns.to_list()
        columns_in_schema = [field.name for field in schema.fields]

        def row_matches_schema(row):
            matches = True
            for col in columns_in_data:
                schema_field = schema.get_field(col) if col in columns_in_schema else None
                there_is_data = not pd.isna(row[col])
                if schema_field is None and there_is_data:
                    matches = False
                elif schema_field is not None and 'enum' in schema_field.constraints:
                    allowed_values = schema_field.constraints['enum']
                    if row[col] not in allowed_values and there_is_data:
                        matches = False
            return matches

        mask = data.apply(row_matches_schema, axis=1)
        df = data[mask]

        self.data_matching_schema[cache_key] = df
        return df
