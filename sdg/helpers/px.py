import re
import functools


class Px:
    """
    Python port of JavaScript by Statistics Faroe Islands.
    More information: http://fod.github.io/px.js/
    """

    def __init__(self, px_string):
        self._ctor(px_string)


    def _array_of_zeroes(self, length):
        return [0] * length


    def keyword(self, k, lang=None):
        if lang is not None and lang != self.get_default_language():
            k = k + '[' + lang + ']'
        if k not in self.keywords():
            raise ValueError(f"'{k}' is not a valid KEYWORD")
 
        if 'TABLE' in self.metadata[k]:
            return self.metadata[k]['TABLE']
        else:
            return self.metadata[k]


    def title(self):
        return self.keyword('TITLE')


    def keywords(self):
        return list(self.metadata.keys())


    def variables(self, lang=None):
        suffix = ''
        if lang is not None and lang not in self.get_languages():
            raise ValueError(f"'{lang}' is not a valid LANGUAGE")
        if lang is not None and lang != self.get_default_language():
            suffix = '[' + lang + ']'
        stub = self.keyword('STUB' + suffix)
        heading = self.keyword('HEADING' + suffix)
        if not stub:
            stub = []
        if not heading:
            heading = []
        if not isinstance(stub, list):
            stub = [stub]
        if not isinstance(heading, list):
            heading = [heading]
        return stub + heading


    def variable(self, v, lang=None):
        vars = self.variables(lang)
        if isinstance(v, int):
            return vars[v]
        elif isinstance(v, str):
            if v in vars:
                return vars.index(v)
            elif v in self.variables():
                return self.variables().index(v)
            else:
                raise ValueError(f"'{v}' is not a valid VARIABLE")
        else:
            return None


    def variable_get_position_from_value(self, v, lang=None):
        vars = self.variables(lang)
        if v in vars:
            return vars.index(v)
        elif lang is not None:
            untranslated = self.variables()
            if v in untranslated:
                return untranslated.index(v)
        raise ValueError(f"'{v}' is not a valid VARIABLE")


    def variable_get_value_from_position(self, v, lang=None):
        vars = self.variables(lang)
        return vars[v]


    def variable_get_translation_from_value(self, v, lang):
        pos = self.variable_get_position_from_value(v, lang)
        return self.variable_get_value_from_position(pos, lang)


    def values(self, v, lang=None):
        var_name = self.variable(v, lang) if isinstance(v, int) else self.variables(lang)[self.variable(v, lang)]
        suffix = ''
        if lang is not None and lang not in self.get_languages():
            raise ValueError(f"'{lang}' is not a valid LANGUAGE")
        if lang is not None and lang != self.get_default_language():
            suffix = '[' + lang + ']'
        return self.keyword('VALUES' + suffix)[var_name]


    def get_languages(self):
        keywords = self.keywords()
        if 'LANGUAGES' in keywords:
            return self.keyword('LANGUAGES')
        if 'LANGUAGE' in keywords:
            return [self.keyword('LANGUAGE')]
        return None


    def get_default_language(self):
        keywords = self.keywords()
        if 'LANGUAGE' in keywords:
            return self.keyword('LANGUAGE')
        if 'LANGUAGES' in keywords:
            return self.keywords('LANGUAGES')[0]
        return None


    def codes(self, v):
        var_name = self.variable(v) if isinstance(v, int) else self.variables()[self.variable(v)]
        if not self.metadata.get('CODES') or not self.keyword('CODES')[var_name]:
            return self.keyword('VALUES')[var_name]
        else:
            return self.keyword('CODES')[var_name]


    def val_counts(self):
        return [len(self.values(i)) for i in range(len(self.variables()))]


    def value(self, code, variable, lang=None):
        idx = self.codes(variable).index(code)
        return self.values(variable, lang)[idx]


    def code(self, val, variable):
        idx = self.values(variable).index(val)
        return self.codes(variable)[idx]


    def datum(self, s, return_index=False):
        counts = self.val_counts()
        index = 0
        for i, length in enumerate(s[:-1]):
            index += s[i] * (reduce(lambda a, b: a * b, counts[i+1:]))
        index += s[-1]

        if return_index:
            return index
        else:
            return self.data[index].replace('"', '').replace("'", '')


    def data_col(self, s, return_indices=False):
        counts = self.val_counts()
        data_col = []
        grp_idx = s.index('*')
        a = s[:]

        for i in range(counts[grp_idx]):
            a[grp_idx] = i
            data_col.append(self.datum(a, return_indices))

        return data_col


    def data_dict(self, s):
        datadict = {}
        grp_idx = s.index('*')
        codes = self.codes(grp_idx)
        data_col = self.data_col(s)

        for i, d in enumerate(data_col):
            datadict[codes[i]] = d

        return datadict


    def datatable(self, s, return_indices=False):
        counts = self.val_counts()
        grp_idxs = [i for i, el in enumerate(s) if el == '*']
        grp_idx = grp_idxs[0]
        chg_idx = grp_idxs[-1]
        datatable = []

        for i in range(counts[chg_idx]):
            s[grp_idx] = '*'
            s[chg_idx] = i
            datatable.append(self.data_col(s, return_indices))

        return datatable


    def entries(self, use_codes=True):
        counts = self.val_counts()
        vars = self.variables()
        val_idx = self._array_of_zeroes(len(counts))
        last = len(val_idx) - 1
        multipliers = []
        dataset = []

        for i in range(len(counts) - 1):
            multipliers.append(functools.reduce(lambda a, b: a * b, counts[i+1:]))

        for i, d in enumerate(self.data):
            datum = {'num': d}
            for di, var in enumerate(vars):
                if use_codes:
                    datum[var] = self.codes(di)[val_idx[di]]
                else:
                    datum[var] = self.values(di)[val_idx[di]]
            dataset.append(datum)

            for mi in range(len(multipliers)):
                if (i + 1) % multipliers[mi] == 0:
                    val_idx[mi] = 0 if val_idx[mi] == counts[mi] - 1 else val_idx[mi] + 1

            val_idx[last] = 0 if val_idx[last] == counts[last] - 1 else val_idx[last] + 1

        return dataset


    def truncate(self, s):
        counts = self.val_counts()
        multipliers = []

        for i, d in enumerate(s):
            if d[0] == '*':
                s[i] = list(range(0, counts[i] - 1))

        for i in range(len(counts) - 1):
            multipliers.append(reduce(lambda a, b: a * b, counts[i+1:]))
        multipliers.append(1)

        for j, var in enumerate(s):
            self.metadata['VALUES'][self.variables()[j]] = [e for e, m in enumerate(self.metadata['VALUES'][self.variables()[j]]) if m in s[j]]

        keep_idxs = []
        def pattern(c, m, w, p=1):
            if len(c) > 1:
                count = c.pop()
                multiple = m.pop()
                want = w.pop()
                patt = [p if d in want else self._array_of_zeroes(multiple) for d in range(count)]
                pattern(c, m, w, patt)
            keep_idxs.append(p)

        pattern(counts, multipliers, s)
        keep_idxs = keep_idxs[0]

        indices = []
        for d in s[0]:
            start = d * multipliers[0]
            end = start + multipliers[0]
            indices.append([i for i, x in enumerate(range(start, end)) if keep_idxs[i] == 1])

        indices = [item for sublist in indices for item in sublist]
        self.data = [d for i, d in enumerate(self.data) if i in indices]


    def _ctor(self, px_string):
        metadata = {}
        data = []

        px_split = px_string.split('\nDATA=')

        px_metadata = px_split[0]
        px_metadata = re.sub(r';\s*(\r\n?|\n)', ';;', px_metadata)
        px_metadata = re.sub(r';;$', ';', px_metadata)
        px_metadata = re.sub(r'(\r\n?|\n)', '', px_metadata)
        px_metadata = re.sub(r'""', ' ', px_metadata)
        px_metadata = px_metadata.split(';;')

        px_data = px_split[1]

        for i in range(len(px_metadata)):
            key_opt_val = re.match(r"^(.+?)(?:\((.+?)\))?=(.+)$", px_metadata[i])

            group1 = key_opt_val.group(1)
            group2 = key_opt_val.group(2)
            group3 = key_opt_val.group(3)
            if not group2:
                group2 = 'TABLE'

            key = group1
            vals = re.sub(r'^"|"$', '', group3).split('","')
            opt = re.sub(r'"', '', group2)
            key_without_language = re.sub(r'\[.*\]$', '', key)

            if key not in metadata:
                metadata[key] = {}

            if key_without_language != 'VALUES' and key_without_language != 'CODES':
                metadata[key][opt] = vals[0] if len(vals) == 1 else vals
            else:
                metadata[key][opt] = vals

        data = re.sub(r'(\r\n|\r|\n)', '', px_data)
        data = re.sub(r';\s*', '', data)
        data = data.strip()
        data = re.split(r'\s+', data)

        if 'HEADING' not in metadata:
            metadata['HEADING'] = {'TABLE': []}

        self.metadata = metadata
        self.data = data


    def get_year_column_name(self):
        year = self.keyword('TIMEVAL')
        return list(year.keys())[0]


    def get_units_column_name(self):
        return self.keyword('CONTVARIABLE')


    def get_value_column_name(self):
        return 'num'
