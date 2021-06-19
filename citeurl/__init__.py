# python standard imports
import re
from pathlib import Path
from typing import Iterable
from copy import copy

# external imports
from yaml import safe_load, safe_dump

# file with all the templates to load by default
DEFAULT_YAML_PATH = Path(__file__).parent.absolute() / 'builtin-templates.yaml'

# regex for "Id."-type citations that will be recognized for all templates
GENERIC_ID = r"(Ib)?[Ii]d\.(<\/(i|em|u)>)?"

# regex to break chains of "Id."-type citations
DEFAULT_ID_BREAKS = r'L\. ?Rev\.|J\. ?Law|\. ?([Cc]ode|[Cc]onst)'

# these tokens can differ without being considered a different authority
NON_AUTHORITY_TOKENS = [
    'subsection',
    'subdivision',
    'clause',
    'pincite',
    'pincite_end',
    'footnote',
]

# for the number format operation
_ROMAN_NUMERALS = [
    (1000, 'M'),
    ( 900, 'CM'),
    ( 500, 'D'),
    ( 400, 'CD'),
    ( 100, 'C'),
    (  90, 'XC'),
    (  50, 'L'),
    (  40, 'XL'),
    (  10, 'X'),
    (   9, 'IX'),
    (   5, 'V'),
    (   4, 'IV'),
    (   1, 'I'),
]

class Citation:
    """
    A single citation found in text.
    
    Attributes:
        text: The text of the citation itself, like "42 USC § 1988(b)"
        span: The beginning and end positions of this citation in the
            source text.
        template: The template which recognized this citation
        tokens: Dictionary of the values that define this citation, such
            as its volume and page number, or its title, section, and
            subsection, etc.
            
            These are derived from the named capture
            groups in the citation template's regex, as modified by the
            template's operations. Tokens whose names start with
            underscores are used only to generate the URL and are
            otherwise discarded.
            
            For idForm and shortForm citations, tokens that are not
            explicitly overwritten will be retained from the parent
            citation.
        URL: The URL where a user can read this citation online
        authority: The Authority that this citation is a reference to.
            This attribute is not set until list_authorities() is run.
    """
    def __init__(self, match: re.Match, template):
        """
        For internal use. There should be no need to create citations
        by means other than a Citator or Template object.
        """
        self.span: tuple = match.span()
        self.template: Template = template
        self.text: str = match.group(0)
        # idForm and shortForm citations get values from parent citation
        # except where their regexes include space for those values
        if template.parent_citation:
            self._raw_tokens = dict(template.parent_citation._raw_tokens)
            for key, val in match.groupdict().items():
                self._raw_tokens[key] = val
        else:
            self._raw_tokens = match.groupdict()
        
        # get processed tokens and URL
        tokens = self.template._process_tokens(self._raw_tokens)
        self.tokens = {
            k:v for (k,v) in tokens.items() if v and not k.startswith('_')
        }
        if self.template.URL:
            URL = ''
            for part in self.template.URL:
                for key, value in tokens.items():
                    if value is None:
                        continue
                    part = part.replace('{%s}' % key, value)
                missing_value = re.search(r'\{.+\}', part)
                if not missing_value:
                    URL += part
            self.URL = URL
        else:
            self.URL = None
    
    def get_link(self, attrs: dict={'class': 'citation'}):
        """Return citation's link element, with given attributes"""
        if self.URL:
            attrs['href'] = self.URL
        else:
            del attrs['href']
        attr_str = ''
        for key, value in attrs.items():
            attr_str += ' %s="%s"' % (key, value)
        return '<a%s>%s</a>' % (attr_str, self.text)
    
    def _original_cite(self):
        """
        Get whichever citation this is an id. or shortform
        of. Returns self if this *is* the longform.
        """
        parent = self
        while parent.template.parent_citation:
            parent = parent.template.parent_citation
        return parent
    
    def _child_templates(self, is_id: bool):
        templates = []
        regex_templates = (
            self.template.idForms if is_id
            else self.template.shortForms
        )
        # make a dictionary of the original tokens, or unique processed tokens
        template_fillers = {**self.tokens, **self._raw_tokens}
        for template in regex_templates:
            # Insert context values into template to make new regex
            regex = template
            for key, value in template_fillers.items():
                if not value: continue
                regex = regex.replace('{%s}' % key, re.escape(value))
            templates.append(Template(
                name=self.template.name,
                regexes=[regex],
                idForms=self.template.idForms,
                URL=self.template.URL,
                operations=self.template.operations,
                defaults=self.template.defaults,
                parent_citation=self,
                _is_id=is_id
            ))
        return templates
    
    def _get_shortform_citations(self, text: str):
        templates = self._child_templates(False)
        for template in templates:
            for citation in template.get_citations(text, span=(self.span[1], )):
                yield citation
            
    def _get_id_citations(self, text: str, end_point: int=None):
        templates = self._child_templates(True)
        id_citations = []
        scan_cites = [self]
        while len(scan_cites) > 0:
            citation = scan_cites.pop(0)
            if end_point:
                span = (citation.span[1], end_point)
            else:
                span = (citation.span[1],)
            potential_ids = []
            for template in citation._child_templates(True):
                match = template.lookup(text, broad=False, span=span)
                if match:
                    potential_ids.append(match)
            if potential_ids:
                id_citation = sorted(potential_ids, key=_sort_key)[0]
                id_citations.append(id_citation)
                scan_cites.append(id_citation)
        return id_citations
    
    def __str__(self):
        return self.text
    
    def __repr__(self):
        # evaluating this will give the wrong value for citation.span
        # since the citation will be out of the document context,
        # but it should be accurate otherwise.
        return f'{object.__repr__(self.template)}.lookup("{self.text}")'
    
    def __eq__(self, other_citation):
        """
        Two citations are equal if they were matched by templates with
        the same name, and if they have the same tokens.
        """
        if (
            self.template.name == other_citation.template.name and
            self.tokens == other_citation.tokens
        ):
            return True
        else:
            return False

class Authority:
    """
    A single source, such as a case or a section of a statute, cited one
    or more times in a text. Two subtly-different citations may refer to
    the same authority, because an authority is defined by two things:
    
    1. The name of the template that a citation was matched by, e.g.
    "United States Code".
    2. All of the citation's tokens that contain an upper-case letter.
    Fully-lowercase tokens are discarded for this purpose, because they
    are intended for subsections, pincites, and other details that
    differentiate citations *within* an authority. 
    
    Attributes:
        tokens: A dictionary of tokens that define this authority, such
            that any citations with incompatible token values will not
            match it.
        template: The template which found all the citations to this
            authority
        citations: The list of all the citations that refer to
            this authority.
        name: The text of base_citation
    """
    def __init__(self, first_cite: Citation, include_first_cite: bool=True):
        """
        Define an authority by providing a single example of a long-form
        citation to that authority.
        
        Arguments:
            first_cite: A long-form citation object representing the
                first and archetypal citation to this authority. The
                first_cite will be added as the first entry in the
                authority's citation list, and it will be used as the
                basis to generate the authority's base_citation.
            include_first_cite: Whether to run include() on the provided
                citation.
        """
        long_cite = first_cite._original_cite()
        self.template: Template = long_cite.template
        self.citations: list = []
        # List the token values that distinguish this authority from
        # others in the same template. This uses processed tokens, not
        # raw, so that a citation to "50 U.S. 5" will match
        # a citation to "50 U. S. 5", etc.
        
        self.tokens = {
            k:v for k,v in first_cite.tokens.items()
            if not k.islower()
        }
        
        self._parent_citation = first_cite
        self._base_citation = None
        
        if include_first_cite:
            self.include(first_cite)
    
    def include(self, citation):
        """
        Adds the citation to this authority's list of citations. Also,
        adds the `authority` tag to the citation, referring back to this
        authority.
        """
        self.citations.append(citation)
        citation.authority = self
    
    def matches(self, citation) -> bool:
        """
        Checks whether a given citation matches the template and defining
        tokens of this authority.
        """
        if self.template.name != citation.template.name:
            return False
        for key, value in self.tokens.items():
            if citation.tokens.get(key) != value:
                return False
        return True
    
    def __str__(self):
        return str(self.base_citation())
    
    def __repr__(self):
        return (f'citeurl.Authority(first_cite={repr(self._parent_citation)}')
    
    def base_citation(self) -> Citation:
        """
        Return a citation object representing the hypothetical
        generic citation to this authority. This code is a mess, and
        will often give subpar results, but it's better than nothing.
        One alternative would be to define a canonical citation format
        for each template.
        """
        if self._base_citation:
            return self._base_citation
        
        longform = self._parent_citation._original_cite()
        
        replacement_tokens = {}
        for key, value in self._parent_citation._raw_tokens.items():
            if key in self.tokens:
                replacement_tokens[key] = value
        # Check if the parent longform citation contains all the defining
        # tokens. If it doesn't, use the shortform that does.
        for key in replacement_tokens.keys():
            if not longform.tokens.get(key):
                longform = self._parent_citation
                break
        # Next, construct a regex pattern to pull out the defining
        # tokens, along with the non-token text preceding each one. The
        # non-token "prelude" text lets us replace the text of each
        # token only when they appear in context. 
        pattern = ''
        for token in replacement_tokens:
            regex = re.escape(longform._raw_tokens[token])
            segment = f"""((?P<{token}_prelude>.*?)(?P<{token}>{regex}))?"""
            if pattern:
                pattern = pattern[:-2] + segment + ')?'
            else: pattern = segment
        match = re.match(pattern, longform.text)
        # Slice off all the text after the last defining token. This will
        # remove things like subsections, etc. It assumes that optional
        # tokens are always after the mandatory ones.
        base_cite_text = longform.text[:match.span(token)[1]]
        # For each token, replace the value from the longform citation
        # with the proper value for this authority.
        for token in replacement_tokens:
            if not match.group(token):
                continue
            prelude = str(match.group(token + '_prelude'))
            old_value = prelude + match.group(token)
            new_value = prelude + replacement_tokens[token]
            base_cite_text = base_cite_text.replace(old_value, new_value)
        # Default to strict matching, but fall back to broadRegex
        # if strict match doesn't exist. Don't default to broadRegex
        # because it might not capture the full text.
        # If that still fails, just use the shortform.
        base_cite = self.template.lookup(base_cite_text, broad=False)
        if not base_cite:
            base_cite = self.template.lookup(base_cite_text, broad=True)
        if not base_cite:
            base_cite = self.citations[0]
        return base_cite
    
    def get_URL(self):
        return self.base_citation().URL


class Citator:
    """
    CiteURL's main feature: a collection of templates, and the tools
    to apply them to text, to find all kinds of citations in a text.
    
    Attributes:
        templates: A dictionary of citation templates that this citator
            will try to match against.
    """
    def __init__(
        self,
        yaml_paths: list=[],
        defaults: bool=True,
    ):
        """
        Calls load_yaml one or more times, to load the citator with
        templates.
        
        Arguments:
            defaults: Whether to load CiteURL's default templates
            yaml_paths: paths to additional YAML files with templates that
        """
        self.templates: dict = {}
        if defaults:
            self.load_yaml(DEFAULT_YAML_PATH.read_text())
        for path in yaml_paths:
            self.load_yaml(Path(path).read_text())
    
    def load_yaml(self, yaml: str):
        """
        Import templates from the given YAML string into the citator.
        
        Arguments:
            path: path to the YAML file to load
        """
        for name, values in safe_load(yaml).items():
            self.templates[name] = Template.from_dict(name, values)
    
    def list_citations(self,
        text: str,
        id_forms: bool=True,
        id_break_regex: str=DEFAULT_ID_BREAKS,
        id_break_indices: list=[],
    ) -> list:
        """
        Scan a text and return a list of all citations in it, in
        order of appearance.
        
        Arguments:
            id_forms: Whether to detect citations like "Id." and
                "Id. at 30."
            id_break_regex: A pattern to look for in the text. Any
                occurrence of the pattern will interrupt a chain of
                "id." citations as if it were another citation.
            id_break_indices: A list of positions in the text
                where "id." citations should be interrupted
        Returns:
            A list of citation objects, in order of appearance in the
            text.
        """
        # First, get full citations:
        citations = []
        for template in self.templates.values():
            citations += template.get_citations(text)
        shortform_cites = []
        
        # Then, add shortforms
        for citation in citations:
            shortform_cites += citation._get_shortform_citations(text)
        citations += shortform_cites
        citations = _sort_and_remove_overlaps(citations)
        
        if not id_forms: # no need to proceed
            return citations
        
        # determine where to break chains of id. citations
        for citation in citations: # break at full or short citations
            id_break_indices.append(citation.span[0])
        if id_break_regex: #also break at specified regexes
            matches = re.compile(id_break_regex).finditer(text)
            for match in matches:
                id_break_indices.append(match.span()[0])
        id_break_indices = sorted(set(id_break_indices))
        
        # loop through all citations to find their id citations
        id_citations = []
        for citation in citations:
            # find the next id break point
            i = -1
            for index in id_break_indices:
                i += 1
                if index > citation.span[1]:
                    end_point = index
                    break
            else:
                end_point = None
            id_break_indices = id_break_indices[i:]
            # get each citation's id citations until the break point
            id_citations += citation._get_id_citations(
                text, end_point=end_point
            )
        return _sort_and_remove_overlaps(citations + id_citations)
    
    def lookup(self, query: str, broad: bool=True) -> Citation:
        """
        Convenience method to get the first citation from the first
        matching template, or None.
        
        This is meant for cases where false positives are not an issue,
        so it uses broadRegex and case-insensitive matching by default.
        
        Arguments:
            broad: Whether to use case-insensitive regex matching and,
                if available, each template's broadRegex.
            query: The text to scan for a citation
        Returns:
            A single citation object, or None
        """
        for template in self.templates.values():
            citation = next(template.get_citations(query, broad=broad), None)
            if citation:
                return citation
        return None
    
    def insert_links(
        self,
        text: str,
        attrs: dict={'class': 'citation'},
        url_optional: bool=False,
        link_detailed_ids: bool=True,
        link_plain_ids: bool=False,
        id_break_regex: str=DEFAULT_ID_BREAKS,
        id_break_indices: list=[]) -> str:
        """
        Convenience method to return a copy of the given text, with
        citation hyperlinks inserted.
        
        If you plan to do more than just insert links, it's better to
        get a list of citations with list_citations first, then insert
        those links with the module-wide insert_links function.
        """
        citations = self.list_citations(
            text,
            id_break_regex=id_break_regex,
            id_break_indices=id_break_indices
        )
        return insert_links(
            citations,
            text,
            attrs=attrs,
            link_detailed_ids=link_detailed_ids,
            link_plain_ids=link_plain_ids,
            url_optional=url_optional
        )
        
    def list_authorities(self, text: str) -> list:
        """
        Convenience method to list all the authorities cited in a
        given text.
        
        If you plan to do more than list authorities, it's better to
        get a list of citations with list_citations, then list the
        unique authorities with the module-wide list_authorities
        function.
        """
        citations = self.list_citations(text)
        return list_authorities(citations)
        
    def __str__(self):
        return str(self.templates)


class Template:
    """
    A pattern to recognize a single kind of citation and generate
    URLs from matches.
    
    In most cases, it is more useful to use the Citator class to load
    templates from YAML files and apply them en masse, rather than use
    the Template class directly.
    """
    def __init__(self,
        name: str,
        regexes: list,
        URL=None,
        broadRegexes: list=None,
        idForms: list=[],
        shortForms: list=[],
        defaults: dict={},
        operations: list=[],
        use_generic_id: bool=True,
        parent_citation: Citation=None,
        _is_id=False
    ):
        """
        Template constructor. Primarily meant for use in loading YAML
        files and dynamically generating shortform templates, but can be
        run directly if needed.
        
        Arguments:
            name: The name of this template
            
            regexes: A list of one or more regexes that this template will
                match. Each regex should be provided as a string, and
                should include one or more named capture groups
                (i.e. "tokens") that will be used to generate the URL.
            
            URL: The template by which to generate URLs from citation
                matches. Placeholders in {curly braces} will be replaced
                by the value of the token with the same name, after that
                token has been processed by the template
                
                The URL template can be provided either as as a string
                or as a list of strings to concatenate. In the latter
                case, if a list item contains a placeholder for which
                no value is set, the list item will be skipped.
            
            defaults: A dictionary of tokens and corresponding default
                values which should be set if the token's value is not
                otherwise set by a regex capture group.
            
            operations: A list of dicts, where each dict represents a
                string modification to perform on a value captured by
                a named capture group in the regex. Operations are
                performed in order, and the end result of all operations
                is saved as the citation's 'tokens' attribute.
                
                Each operation must specify a `token` for its input. It
                will also be used as the output of the operation, unless
                `output` is specified. If the specified input token is
                not set, the operation will be skipped.
                
                The supported operations are `case`, `sub`, `lookup`,
                `optionalLookup`, `lpad`, and `numberFormat`.
                
                The `case` operation outputs the input token, set to the
                specified capitalization, either 'upper', 'lower', or
                'title'.
                
                The `sub` operation performs a regex substitution. It
                requires a list of two strings; the first is the regex
                to match in the input token, and the second is the text
                to replace each match with.
                
                The `lookup` operation tries to match the input against
                a series of dictionary keys (using case-insensitive
                regex), and set the output to the corresponding value.
                If the dictionary does not contain a matching key, the
                entire template match will retroactively fail.
                `optionalLookup` works the same way, except that failed
                lookups will not cause the template to fail, and will
                simply leave tokens unmodified.
                
                The `numberFormat` operation assumes that the input
                token is a number, either in digit form or Roman
                numerals. It outputs the same number, converted to the
                specified number format, either 'roman' or 'digit'.
                
            shortForms: A list of regex templates to generate regexes
                that recognize short-forms of a parent long-form
                citation that has appeared earlier in the text.
                
                Any named section in {curly braces} will be replaced by
                the value of the corresponding token from the parent
                citation. So if a template detects a longform citation to
                "372 U.S. 335" and has a shortform `{volume} {reporter}
                at (?P<pincite>\\d+)`, it will generate the following
                regex: `372 U.S. at (?P<pincite>\d+)`.
                
            idForms: Think "id.", not ID. Identical to shortForms,
                except that these regexes will only match until the
                next different citation or other interruption.
            
            broadRegexes: Identical to regexes, except that they will
                only be matched in lookups where broad == True. In these
                cases, broadRegexes will be used in addition to normal
                regexes. This is meant to allow for very permissive
                regexes in contexts like a search engine, where user
                convenience is more important than avoiding false
                positives.
            
            use_generic_id: Whether this template should recognize the
                generic "id." citation defined in GENERIC_ID
            
            parent_citation: The citation, if any, that this template
                was created as a shortform of. This argument is
                for dynamically-generated templates, and there is usually
                no need to use it manually.
        """
        # Basic values
        self.name: str = name
        self.regexes: str = regexes
        self.is_id: bool = _is_id
        if URL:
            self.URL: str = URL if type(URL) is list else [URL]
        else:
            self.URL = None
        # Supplemental regexes
        self.broadRegexes: str = broadRegexes
        self.idForms: list = idForms
        if use_generic_id and GENERIC_ID not in self.idForms:
            self.idForms.append(GENERIC_ID)
        self.shortForms: list = shortForms
        # String operators
        self.defaults: dict = defaults
        self.operations: list = operations
        
        # Extra data for shortform citations
        self.parent_citation: Citation = parent_citation
        
        # hack: prevent all regexes from matching mid-word
        for key in ['regexes', 'broadRegexes', 'idForms', 'shortForms']:
            regex_list = self.__dict__[key]
            if not regex_list:
                continue
            regex_list = list(map(lambda x: fr'(?<!\w){x}(?!\w)', regex_list))
            self.__dict__[key] = regex_list
        
        # dictionaries of compiled regexes
        self._compiled_regexes: dict = {}
        self._compiled_broadRegexes: dict = {}
    
    @classmethod
    def from_dict(cls, name: str, values: dict):
        """
        Return a template from a dictionary of values, like a dictionary
        created by parsing a template from YAML format.
        """
        values = copy(values)
        # if regex is specified in singular form, convert it to a
        # list with one item, for sake of consistency with multiple-
        # regex templates.
        for key in ['regex', 'broadRegex']:
            if key in values:
              values[key + 'es'] = [values.pop(key)]
        
        # unrelated: if an individual regex is given as a list of
        # strings (convenient for reusing YAML anchors), concatenate
        # it to one string.
        for key in ['regexes', 'broadRegexes', 'idForms', 'shortForms']:
            if key not in values:
                continue
            for i, regex in enumerate(values[key]):
                if type(regex) is list:
                    values[key][i] = ''.join(regex)
        return cls(name=name, **values)
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        text = f'citeurl.Template(name="{self.name}", regexes={self.regexes}'
        
        for key in [
            'URL', 'broadRegexes', 'idForms',
            'shortForms', 'defaults', 'operations'
        ]:
            if self.__dict__[key]:
                text += f', {key}={self.__dict__[key]}'
        if self.parent_citation:
            # don't use the parent cite's actual __repr__ because this gets
            # very recursive very fast
            text += (
                ', parent_citation=' +
                object.__repr__(self.parent_citation)
            )
        if self.is_id:
            text += ', _is_id=True'
        return text + ')'
    
    def to_yaml(self) -> str:
        "Convert this template to a loadable yaml"
        values = {}
        
        # Save regex or, where multiple, regexes
        if len(self.regexes) > 1:
            values['regexes'] = self.regexes
        else:
            values['regex'] = self.regexes[0]
        
        if not self.broadRegexes:
            pass
        elif len(self.broadRegexes) > 1:
            values['broadRegexes'] = self.broadRegexes
        else:
            values['broadRegex'] = self.broadRegexes[0]
        
        # Save URL to string if it's only one value
        if not self.URL:
            pass
        elif len(self.URL) > 1:
            values['URL'] = self.URL
        else:
            values['URL'] = self.URL[0]
        
        # these values can just be copied over
        for key in ['operations', 'defaults', 'shortForms', 'idForms']:
            if self.__dict__[key]:
                values[key] = self.__dict__[key]
        
        return safe_dump(
            {self.name: values},
            sort_keys = False,
            allow_unicode = True,
        )
        
    def lookup(
        self,
        text: str,
        broad: bool=True,
        span: tuple=(0,)
    ) -> Citation:
        """
        Returns the first citation it finds in the text, or None.
        
        Arguments:
            text: The text to scan for a citation.
            broad: Whether to use case-insensitive regex matching
                and, if available, the template's broadRegex.
            span: A tuple of one or two values determining
                the start and end index of where in the text to search
                for citations. Defaults to (0,) to scan the entire text.
        Returns:
            The first citation this template finds in the scanned text,
            or None.
        """
        try:
            return next(self.get_citations(text, broad=broad, span=span))
        except:
            return None
    
    def get_citations(
        self,
        text: str,
        broad: bool=False,
        span: tuple=(0,)
    ) -> Iterable:
        """
        Generator to return all citations the template finds in text.
        
        Arguments:
            text: The text to scan for a citation
            broad: Whether to use case-insensitive regex matching and,
                if available, the template's broadRegex.
            span: A tuple of one or two values determining
                the start and end index of where in the text to search
                for citations. Defaults to (0,) to scan the entire text.
        Returns:
            Generator that yields each citation the template finds in the
                text, or None.
        """
        matches = []
        regex_count = len(self.regexes)
        if broad and self.broadRegexes:
            regex_count += len(self.broadRegexes)
        for index in range(regex_count):
            #print(f'scanning regex {index} for template {self}')
            matches += self._compiled_re(index, broad).finditer(text, *span)
            
        for match in matches:
            try:
                citation = Citation(match, self)
            # skip citations where lookup failed:
            except KeyError as e:
                citation = None
            if citation:
                yield citation
        return None
    
    def _compiled_re(self, index: int = 0, broad: bool = False) -> re.Pattern:
        """
        Gets the compiled broad or regular regex pattern for the
        given numbered regex, first compiling it if necessary.
        """
        if broad:
            if index < len(self.regexes):
                regex_str = self.regexes[index]
            else:
                regex_str = self.broadRegexes[index - len(self.regexes)]
            target = self._compiled_broadRegexes
            kwargs = {'flags':re.I}
        else:
            regex_str = self.regexes[index]
            kwargs = {}
            target = self._compiled_regexes
        
        # only compile regex if it's not already present
        if index not in target:
            try:
                target[index] = re.compile(regex_str, **kwargs)
            except re.error as e:
                if not self.parent_citation:
                    raise SyntaxError(
                        f'{self.name} citation template has a broken ' +
                        (
                            'broadRegex' if index > len(self.regexes)
                            else 'regex'
                        )
                        + f':\n{e}'
                    )
                # if there's a parent citation, error should refer to
                # the parent template, not this one
                else:
                    raise SyntaxError(
                        f'CiteURL template for {self.parent_citation.template}'
                        + f' has an error in a shortForm or idForm: {e}'
                    )
        return target[index]

    def _process_tokens(self, raw_tokens: dict):
        """
        Returns a copy of the given set of tokens, after applying the
        template's defaults and processing operations
        """
        processed_tokens = dict(raw_tokens)
        for key, val in self.defaults.items():
            if key not in processed_tokens or processed_tokens[key] is None:
                processed_tokens[key] = val
        
        # perform each operation in series
        for operation in self.operations:
            # skip any operation that requires a nonexistent token
            if (
                operation['token'] not in processed_tokens
                or processed_tokens[operation['token']] is None
            ):
                continue
            
            input_value = processed_tokens[operation['token']]
            
            if 'output' in operation:
                output = operation['output']
            else:
                output = operation['token']
            
            # handle case modification
            if 'case' in operation:
                case = operation['case']
                if case == 'upper':
                    processed_tokens[output] = input_value.upper()
                elif case == 'lower':
                    processed_tokens[output] = input_value.lower()
                elif case == 'title':
                    processed_tokens[output] = input_value.title()
            
            # handle regex substitution
            if 'sub' in operation:
                processed_tokens[output] = re.sub(
                    operation['sub'][0],
                    operation['sub'][1],
                    input_value,
                )
            
            # handle lookups, optional and otherwise
            def regex_lookup(op: str):
                output_val = None
                for regex, value in operation[op].items():
                    if re.fullmatch(regex, input_value, flags=re.I):
                        output_val = value
                        break
                return output_val
            for op in ['lookup', 'optionalLookup']:
                if op not in operation:
                    continue
                output_val = regex_lookup(op)
                if output_val is not None:
                    processed_tokens[output] = output_val
                elif op != 'optionalLookup':
                    raise KeyError(
                        f"lookup failed for {operation['token']}"
                        + " '{input_value}'"
                    )

            # change between digits and roman numerals
            if 'numberFormat' in operation:
                if operation['numberFormat'] == 'roman':
                    # convert to roman numerals if necessary
                    try:
                        number = int(input_value)
                        # credit to https://stackoverflow.com/a/47713392
                        result = ''
                        for (arabic, roman) in _ROMAN_NUMERALS:
                            (factor, number) = divmod(number, arabic)
                            result += roman * factor
                        processed_tokens[output] = result
                    except ValueError:
                        processed_tokens[output] = input_value
                
                elif operation['numberFormat'] == 'digit':
                    # convert to digits if necessary
                    if re.fullmatch('[MDCLXVI]+', input_value, flags=re.I):
                        # https://codereview.stackexchange.com/a/141413
                        translation = {v:k for k,v in _ROMAN_NUMERALS}
                        values = [translation[r] for r in input_value.upper()]
                        processed_tokens[output] = str(sum(
                            val if val >= next_val else -val
                            for val, next_val in zip(values[:-1], values[1:])
                        ) + values[-1])
                    else:
                        processed_tokens[output] = input_value
            
            # left pad with zeros
            if 'lpad' in operation:
                processed_tokens[output] = input_value.zfill(operation['lpad'])
        
        return processed_tokens


def insert_links(
    citations: list,
    text: str,
    attrs: dict={'class': 'citation'},
    link_detailed_ids: bool=True,
    link_plain_ids: bool=False,
    url_optional: bool=False
) -> str:
    """
    Given a text and a list of citations found in it, return a text
    with an HTML hyperlink inserted for each citation.
    
    Arguments:
        citations: A list of citation objects found in the text
        text: The text the citations were found in
        attrs: HTML tag attributes (like css class, rel, etc)
            to give each inserted hyperlink.
        link_detailed_ids: Whether to insert hyperlinks for citations
            like "Id. at 30."
        link_plain_ids: Whether to insert hyperlinks for simple repeat
            citations like "id."
        url_optional: Whether to insert link elements for citations that
            do not have an associated URL
    Returns:
        The input text, with HTML links inserted for each citation
    """
    offset = 0
    for citation in citations:
        # by default, skip citations without URLs
        if not citation.URL and not url_optional:
            continue
        
        if citation.template.is_id:
            # check whether the matched citation is from a template that
            # has any named capture groups. If it doesn't, it's a
            # "plain id." and should normally be skipped
            if not '(?P<' in citation.template._compiled_re().pattern:
                if not link_plain_ids:
                    continue
            elif not link_detailed_ids:
                continue
        
        link = citation.get_link(attrs=attrs)
        
        # insert each link into the proper place by offsetting later
        # citations by however many extra characters are added by each
        cite_start = citation.span[0] + offset
        cite_end = citation.span[1] + offset
        text = ''.join([text[:cite_start], link, text[cite_end:]])
        offset += len(link) - len(citation.text)
    
    return text


def _join_if_list(source):
    return source if type(source) is str else ''.join(source)


def _sort_and_remove_overlaps(citations: list):
    """Sorts citations by order of appearance; deletes overlaps."""
    sorted_citations = sorted(citations, key=_sort_key)
    index = 1 # to loop through citations while adding more
    while index < len(sorted_citations):
        current = sorted_citations[index]
        previous = sorted_citations[index - 1]
        # Skip to next section if there's no overlap
        if previous.span[1] < current.span[0]:
            index += 1
            continue
        # Delete whichever overlapping citation is shorter.
        # If they have the same length, delete the one that
        # was found earliest.
        if len(previous.text) > len(current.text):
            sorted_citations.pop(index)
        elif len(previous.text) < len(current.text):
            sorted_citations.pop(index - 1)
        elif citations.index(previous) > citations.index(current):
            sorted_citations.pop(index)
        else:
            sorted_citations.pop(index - 1)
    return sorted_citations


def _sort_key(citation):
    """Helper function to sort citations by order of appearance"""
    return citation.span[0]


def list_authorities(
    citations: list, 
    irrelevant_tokens: list=NON_AUTHORITY_TOKENS
) -> list:
    """
    Combine a list of citations into a list of authorities, each
    of which represents all the citations to a particular source.
    
    As a side-effect, this also gives each citation an `authority`
    attribute referring to the proper authority.
    
    Arguments:
        citations: The list of citations to combine
        irrelevant_tokens: A list of tokens whose values may 
            differ among citations to the same authority.
    Returns:
        A list of authority objects, sorted by the number of citations
        that refer to each, from most to least.
    """
    authorities = []
    for citation in citations:
        for authority in authorities:
            if authority.matches(citation):
                authority.include(citation)
                break
        else:
            authorities.append(Authority(citation, irrelevant_tokens))
    def authority_sort_key(authority):
        return 0 - len(authority.citations)
    return sorted(authorities, key=authority_sort_key)

