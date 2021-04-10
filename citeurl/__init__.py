# python standard imports
import re
from pathlib import Path
from typing import Iterable

# external imports
from yaml import safe_load

# file with all the schemas to load by default
DEFAULT_YAML_PATH = Path(__file__).parent.absolute() / 'default-schemas.yaml'

# regex for "Id."-type citations that will be recognized for all schemas
GENERIC_ID = r"\b(Ib)?[Ii]d\.(<\/(i|em|u)>)?"

# regex to break chains of "Id."-type citations
DEFAULT_ID_BREAKS = 'L\. ?Rev\.|J\. ?Law|\. ?([Cc]ode|[Cc]onst)'

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
        schema: The schema which recognized this citation
        tokens: Dictionary of the named capture groups from the regex
            this citation matched. For "id." and "shortform" citations,
            this includes tokens carried over from the parent citation.
        processed_tokens: Dictionary of tokens after they have been
            modified via the schema's processes.
        URL: The URL where a user can read this citation online
    """
    def __init__(self, match: re.Match, schema):
        """
        For internal use. There should be no need to create citations
        by means other than a Citator or Schema object.
        """
        self.span: tuple = match.span()
        self.schema: Schema = schema
        self.text: str = match.group(0)
        # idForm and shortForm citations get values from parent citation
        # except where their regexes include space for those values
        if schema.parent_citation:
            self.tokens: dict = dict(schema.parent_citation.tokens)
            for key, val in match.groupdict().items():
                self.tokens[key] = val
        else:
            self.tokens: dict = match.groupdict()
        self.processed_tokens: dict = self.schema._process_tokens(self.tokens)
        self.URL: str = self._get_url()
    
    def __str__(self):
        return self.text
    
    def _get_url(self) -> str:
        """
        Processes tokens, feeds the results into the schema's
        URL template, and returns the resulting URL.
        
        Returns:
            A generated URL pointing to where to find the citation,
            or None.
        """
        if not hasattr(self.schema, 'URL'):
            return None
        # Process matched tokens (i.e. named regex capture groups)
        URL = """"""
        for part in self.schema.URL:
            for key, value in self.processed_tokens.items():
                if value is None: continue
                part = part.replace('{%s}' % key, value)
            missing_value = re.search('\{.+\}', part)
            if not missing_value:
                URL += part
        return URL
    
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
        while parent.schema.parent_citation:
            parent = parent.schema.parent_citation
        return parent
    
    def _child_schemas(self, is_id: bool):
        schemas = []
        regex_templates = (
            self.schema.idForms if is_id
            else self.schema.shortForms
        )
        # make a dictionary of the original tokens, or unique processed tokens
        template_fillers = {**self.processed_tokens, **self.tokens}
        for template in regex_templates:
            # Insert context values into template to make new regex
            regex = template
            for key, value in template_fillers.items():
                if not value: continue
                regex = regex.replace('{%s}' % key, value)
            schemas.append(Schema(
                name=self.schema.name,
                regexes=[regex],
                idForms=self.schema.idForms,
                URL=self.schema.URL if hasattr(self.schema, 'URL') else None,
                operations=self.schema.operations,
                parent_citation=self,
                is_id=is_id
            ))
        return schemas
    
    def _get_shortform_citations(self, text: str):
        schemas = self._child_schemas(False)
        for schema in schemas:
            for citation in schema.get_citations(text, span=(self.span[1], )):
                yield citation
            
    def _get_id_citations(self, text: str, end_point: int=None):
        schemas = self._child_schemas(True)
        id_citations = []
        scan_cites = [self]
        while len(scan_cites) > 0:
            citation = scan_cites.pop(0)
            if end_point:
                span = (citation.span[1], end_point)
            else:
                span = (citation.span[1],)
            potential_ids = []
            for schema in citation._child_schemas(True):
                match = schema.lookup(text, broad=False, span=span)
                if match:
                    potential_ids.append(match)
            if potential_ids:
                id_citation = sorted(potential_ids, key=_sort_key)[0]
                id_citations.append(id_citation)
                scan_cites.append(id_citation)
        return id_citations


class Authority:
    """
    A single source cited one or more times in a text.
    
    Attributes:
        defining_tokens: A dictionary of tokens that define this
            authority, such that any citations with incompatible
            token values will not match it. Note that this uses
            processed_tokens (those which have been modified by
            the schema's operations).
        schema: The schema which found all the citations to this
            authority
        citations: The list of all the citations that refer to
            this authority.
        base_citation: A citation object representing the hypothetical
            generic citation to this authority.
        name: The text of base_cite
    """
    def __init__(self, first_cite, allowed_differences: list=[]):
        """
        Define an authority by providing a single long-form citation,
        and the list of tokens which, if present in the citation, should
        be discarded from the definition of the authority.
        
        Generates a base_citation to represent the generic instance of
        this authority.
        
        Arguments:
            first_cite: A long-form citation object representing the
                first and archetypal citation to this authority. The
                first_cite will be added as the first entry in the
                authority's citation list, and it will be used as the
                basis to generate the authority's base_cite.
            allowed_differences: A list of tokens whose values can
                differ among citations to the same authority
        """
        long_cite = first_cite._original_cite()
        self.schema: Schema = long_cite.schema
        self.citations: list = [first_cite]
        # List the token values that distinguish this authority from
        # others in the same schema. This uses processed tokens, not
        # raw, so that a citation to "50 U.S. 5" will match
        # a citation to "50 U. S. 5", etc.
        self.defining_tokens: dict = {}
        for t in first_cite.processed_tokens:
            if (
                first_cite.processed_tokens[t] != None
                and t not in allowed_differences
            ):
                self.defining_tokens[t] = first_cite.processed_tokens[t]
        # Next, derive a base citation to represent this authority.
        # If the first_citation to this authority isn't a longform, use
        # whatever longform it's a child of.
        try:
            self.base_citation = self._derive_base_citation(long_cite)
        except TypeError:
            self.base_citation = first_cite
        # Set other instance variables
        self.name: str = self.base_citation.text
        self.URL: str = self.base_citation.URL
        # finally, give the first citation a reference to this authority
        first_cite.authority = self
    
    def include(self, citation):
        """Adds the citation to this schema's list of citations. Also,
        adds the `authority` tag to the citation, referring back to this
        authority."""
        self.citations.append(citation)
        citation.authority = self
    
    def matches(self, citation) -> bool:
        """
        Checks whether a given citation matches the schema and defining
        tokens of this authority.
        """
        if self.schema.name != citation.schema.name:
            return False
        for key, value in self.defining_tokens.items():
            if (key not in citation.processed_tokens
                or citation.processed_tokens[key] != value):
                return False
        return True
    
    def __str__(self):
        return str(self.base_citation)
    
    def _derive_base_citation(self, parent: Citation) -> Citation:
        replacement_tokens = {}
        for key, value in self.citations[0].tokens.items():
            if key in self.defining_tokens:
                replacement_tokens[key] = value
        # Check if the parent longform citation contains all the defining
        # tokens. If it doesn't, use the shortform that does.
        for key in replacement_tokens.keys():
            if key not in parent.tokens or parent.tokens[key] == None:
                parent = self.citations[0]
                break
        # Next, construct a regex pattern to pull out the defining
        # tokens, along with the non-token text preceding each one. The
        # non-token "prelude" text lets us replace the text of each
        # token only when they appear in context. 
        pattern = ''
        for token in replacement_tokens:
            regex = re.escape(parent.tokens[token])
            segment = f"""((?P<{token}_prelude>.*?)(?P<{token}>{regex}))?"""
            if pattern:
                pattern = pattern[:-2] + segment + ')?'
            else: pattern = segment
        match = re.match(pattern, parent.text)
        # Slice off all the text after the last defining token. This will
        # remove things like subsections, etc. It assumes that optional
        # tokens are always after the mandatory ones.
        base_cite_text = parent.text[:match.span(token)[1]]
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
        base_cite = self.schema.lookup(base_cite_text, broad=False)
        if not base_cite:
            base_cite = self.schema.lookup(base_cite_text, broad=True)
        if not base_cite:
            base_cite = self.citations[0]
        return base_cite


class Citator:
    """
    CiteURL's main feature: a collection of schemas, and the tools
    to apply them to text, to find all kinds of citations in a text.
    
    Attributes:
        schemas: A list of schema objects that this citator will try to
            match against.
        generic_id: A common regex the citator will append to each
            schema when it is loaded, to recognize a simple citation to
            the most-recently cited source.
    """
    def __init__(
        self,
        yaml_paths: list[str]=[],
        defaults: bool=True,
        generic_id: str=GENERIC_ID
    ):
        """
        Calls load_yaml one or more times, to load the citator with
        schemas.
        
        Arguments:
            defaults: Whether to load CiteURL's default schemas
            yaml_paths: paths to additional YAML files with schemas that
                should be loaded to supplement or replace the defaults.
            generic_id: a common regex to append to all schemas, to
                recognize a simple citation to the most-recently cited
                source. Detects "id." or "ibid." by default. To
                disable, set to None.
        """
        self.generic_id: str = generic_id
        self.schemas: list = []
        if defaults:
            self.load_yaml(DEFAULT_YAML_PATH)
        for path in yaml_paths:
            self.load_yaml(path)
    
    def load_yaml(self, path: str, use_generic_id: bool=True):
        """
        Import schemas from the specified YAML file into the citator.
        
        Arguments:
            path: path to the YAML file to load
            use_generic_id: Whether to append the citator's generic_id
            citation format to the loaded schemas.
        """
        yaml_text = Path(path).read_text()
        yaml_dict = safe_load(yaml_text)
        
        # read each item in the YAML into a new schema
        for schema_name, schema_data in yaml_dict.items():
            # if regex is specified in singular form, convert it to a
            # list with one item, for sake of consistency with multiple-
            # regex schemas.
            for key in ['regex', 'broadRegex']:
                if key in schema_data:
                  schema_data[key + 'es'] = [schema_data.pop(key)]
            
            # unrelated: if an individual regex is given as a list of
            # strings (convenient for reusing YAML anchors), concatenate
            # it to one string.
            for key in ['regexes', 'broadRegexes', 'idForms', 'shortForms']:
                if key not in schema_data:
                    continue
                for i, regex in enumerate(schema_data[key]):
                    if type(regex) is list:
                        schema_data[key][i] = ''.join(regex)
                        
            # make the schema and add it to the citator, adding the
            # generic id-form citation if applicable
            new_schema = Schema(name=schema_name, **schema_data)
            if use_generic_id and self.generic_id:
                new_schema.idForms.append(self.generic_id)
            self.schemas.append(new_schema)
    
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
            id_forms: Whether to detect citations like
            "Id." and "Id. at 30."
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
        for schema in self.schemas:
            citations += schema.get_citations(text)
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
        matching schema, or None.
        
        This is meant for cases where false positives are not an issue,
        so it uses broadRegex and case-insensitive matching by default.
        
        Arguments:
            broad: Whether to use case-insensitive regex matching and,
                if available, each schema's broadRegex.
            query: The text to scan for a citation
        Returns:
            A single citation object, or None
        """
        for schema in self.schemas:
            citation = next(schema.get_citations(query, broad=broad), None)
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
        return str(self.schemas)


class Schema:
    """
    A pattern to recognize a single kind of citation and generate
    URLs from matches.
    
    In most cases, it is more useful to use the Citator class to load
    schemas from YAML files and apply them en masse, rather than use
    the Schema class directly.
    """
    def __init__(self,
        name: str,
        regexes: list[str],
        URL=None,
        broadRegexes: list[str]=None,
        idForms: list[str]=[],
        shortForms: list[str]=[],
        defaults: dict={},
        operations: list[dict]=[],
        parent_citation=None,
        is_id=False
    ):
        """
        Schema constructor. Primarily meant for use in loading YAML
        files and dynamically generating shortform schemas, but can be
        run directly if needed.
        
        Arguments:
            name: The name of this schema
            
            regexes: A list of one or more regexes that this schema will
                match. Each regex should be provided as a string, and
                should include one or more named capture groups
                (i.e. "tokens") that will be used to generate the URL.
            
            URL: The template by which to generate URLs from citation
                matches. Placeholders in {curly braces} will be replaced
                by the value of the token with the same name, after that
                token has been processed by the schema
                
                The URL template can be provided either as as a string
                or as a list of strings to concatenate. In the latter
                case, if a list item contains a placeholder for which
                no value is set, the list item will be skipped.
            
            defaults: A dictionary of tokens and corresponding default
                values which should be set if the token's value is not
                otherwise set by a regex capture group.
            
            operations: A list of operations to perform on the tokens,
                in sequence, to transform them from `captured_tokens` to
                `processed_tokens`, the tokens that are used for URL
                generation.
                
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
                entire schema match will retroactively fail.
                `optionalLookup` works the same way, except that failed
                lookups will not cause the schema to fail, and will
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
                citation. So if a schema detects a longform citation to
                "372 U.S. 335" and has a shortform `{volume} {reporter}
                at (?P<pincite>\d+)`, it will generate the following
                regex: `372 U.S. at (?P<pincite>\d+)`.
                
            idForms: Think "id.", not ID. Identical to shortForms,
                except that these regexes will only match until the
                next different citation or other interruption.
                
            parent_citation: The citation, if any, that this schema
                was created as a shortform of. This argument is
                for dynamically-generated schemas, and there is usually
                no need to use it manually.
                
            is_id: Whether this schema represents an immediate repeat
                shortform citation like "id." or "id. at 30". Really
                only relevant for procedurally-generated schemas.
        """
        # Basic values
        self.name: str = name
        self.regexes: str = regexes
        self.is_id: bool = is_id
        if URL:
            self.URL: str = URL if type(URL) is list else [URL]
        # Supplemental regexes
        self.broadRegexes: str = broadRegexes
        self.idForms: list = idForms
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
            regex_list = list(map(lambda x: r'(\b|^)' + x, regex_list))
        
        # dictionaries of compiled regexes
        self._compiled_regexes: dict = {}
        self._compiled_broadRegexes: dict = {}
        
    def __str__(self):
        return self.name
    
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
                and, if available, the schema's broadRegex.
            span: A tuple of one or two values determining
                the start and end index of where in the text to search
                for citations. Defaults to (0,) to scan the entire text.
        Returns:
            The first citation this schema finds in the scanned text,
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
        Generator to return all citations the schema finds in text.
        
        Arguments:
            text: The text to scan for a citation
            broad: Whether to use case-insensitive regex matching and,
                if available, the schema's broadRegex.
            span: A tuple of one or two values determining
                the start and end index of where in the text to search
                for citations. Defaults to (0,) to scan the entire text.
        Returns:
            Generator that yields each citation the schema finds in the
                text, or None.
        """
        matches = []
        for index in range(len(self.regexes)):
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
            compiled = self.__dict__['_compiled_broadRegexes']
            regex_source = (
                self.broadRegexes if self.broadRegexes
                and len(self.broadRegexes) > index
                else self.regexes
            )
            kwargs = {'flags':re.I}
        else:
            compiled = self.__dict__['_compiled_regexes']
            regex_source = self.regexes
            kwargs= {}
        # only compile regex if it's not already present
        if index not in compiled:
            try:
                compiled[index] = re.compile(regex_source[index], **kwargs)
            except re.error as e:
                if not self.parent_citation:
                    raise SyntaxError(
                        "CiteURL schema for %s has an invalid %s: %s"
                        % (self.name, 'broadRegex' if broad else 'regex', e)
                    )
                else:
                    raise SyntaxError(
                        ("CiteURL schema for %s has an error in one of its"
                        + " shortForms or idForms: %s")
                        % (self.parent_citation.schema.name, e)
                    )
        return compiled[index]

    def _process_tokens(self, tokens: dict):
        """
        Returns a copy of the given set of tokens, after applying the
        schema's defaults and processing operations
        """
        processed_tokens = dict(tokens)
        for key, val in self.defaults.items():
            if key not in processed_tokens or processed_tokens[key] is None:
                processed_tokens[key] = val
        
        # perform each operation in series
        for operation in self.operations:
            # skip any operation that requires a nonexistent token
            if processed_tokens[operation['token']] is None:
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
        if not citation.URL and not url_optional:
            continue
        if citation.schema.is_id:
            if citation.schema._compiled_re().groupindex:
                if not link_detailed_ids:
                    continue
            elif not link_plain_ids:
                continue
        link = citation.get_link(attrs=attrs)
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
        unimportant_tokens: A list of tokens whose values may 
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

