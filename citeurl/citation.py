# python standard imports
from typing import Iterable
import re

# internal imports
from .regex_mods import process_pattern, match_regexes

BASIC_ID_REGEX = re.compile(r'(?<!\w)[Ii](bi)?d\.(?!=\w)')

class Citation:
    """
    A legal reference found in text.
    
    Attributes:
        tokens: dictionary of the values that define this citation, such
            as its volume and page number, or its title, section, and
            subsection, etc
        
        URL: the location, if any, where this citation can be found
            online, defined by the template's URL_builder
        
        name: a uniform, human-readable representation of this citation,
            written by the template's name_builder
        
        text: the actual text of this citation as found in the source
            text
        
        source_text: the full text that this citation was found in
        
        template: the template whose regexes found this citation or its
            parent
        
        parent: the earlier citation, if any, that this citation is a
            shortform or idform child of
        
        raw_tokens: dictionary of tokens as captured in the original
            regex match, before normalization. Note that for child
            citations, raw_tokens will include any raw_tokens inferred
            from the parent citation.
        
        idform_regexes: list of regex pattern objects to find child
            citations later in the text, valid until the next different
            citation appears.
        
        shortform_regexes: list of regex pattern objects to find
            child citations anywhere in the subsequent text
    """
    
    def __init__(
        self,
        match: re.match,
        template,
        parent = None,
    ):
        self.match = match
        self.text = match.group(0)
        self.source_text = match.string
        self.span = match.span()
        self.template = template
        self.parent = parent
        self.tokens = {}
        self.raw_tokens = match.groupdict()
        
        # copy raw_tokens (in order) from the parent citation, but
        # stop at the first one that the child citation overwrites
        if parent:
            merged_tokens = {}
            for k in template.tokens.keys():
                if self.raw_tokens.get(k):
                    merged_tokens.update(self.raw_tokens)
                    break
                else:
                    merged_tokens[k] = parent.raw_tokens.get(k)
            self.raw_tokens = merged_tokens
        
        # normalize raw_tokens to get consistent token values across
        # differently-formatted citations to the same source.
        # This will raise a SyntaxError if a mandatory edit fails
        for name, ttype in template.tokens.items():
            value = self.raw_tokens.get(name)
            self.tokens[name] = ttype.normalize(value)
        
        # Finally, compile the citation's idform and shortform regexes.
        # To avoid unneccessary work, first try to copy regexes from the
        # parent citation if applicable.
        
        if parent and parent.raw_tokens == self.raw_tokens:
        # then we can safely copy the parent's regexes to the child
            self.idform_regexes = parent.idform_regexes
            self.shortform_regexes = parent.shortform_regexes
            return
        
        # otherwise we'll need to compile new shortform regexes,
        # but we can still copy some of them from the parent
        
        kwargs = {
            'replacements': self.raw_tokens,
            'token_prefix': 'same',
        }
        if parent:
        # we can copy regexes, but only if they do not reference a
        # specific value from the citation, e.g. {same volume}.
            self.shortform_regexes = [
                (
                    re.compile(process_pattern(pattern, **kwargs))
                    if '{same ' in pattern else parent.shortform_regexes[i]
                )
                for i, pattern in enumerate(template._processed_shortforms)
            ]
            
            self.idform_regexes = [
                (
                    re.compile(process_pattern(pattern, **kwargs))
                    if '{same ' in pattern else parent.idform_regexes[i]
                )
                for i, pattern in enumerate(template._processed_idforms)
            ]
            
        else: # compile all-new idforms and shortforms
            self.shortform_regexes = [
                re.compile(process_pattern(pattern, **kwargs))
                for pattern in self.template._processed_shortforms
            ]
            self.idform_regexes = [
                re.compile(process_pattern(pattern, **kwargs))
                for pattern in self.template._processed_idforms
            ]
        self.idform_regexes.append(BASIC_ID_REGEX)
    
    @property
    def URL(self) -> str:
        if self.template.URL_builder:
            url =  self.template.URL_builder(self.tokens)
            if url:
                url = url.replace(' ', '%20')
        else:
            url = None
        return url
    
    @property
    def name(self) -> str:
        if self.template.name_builder:
            return self.template.name_builder(self.tokens)
        else:
            return None
    
    def get_shortform_cites(self) -> Iterable:
        keep_trying = True
        span_start = self.span[1]
        while keep_trying:
            try:
                match = next(match_regexes(
                    regexes=self.shortform_regexes,
                    text=self.source_text,
                    span=(span_start,),
                ))
                span_start = match.span()[1]
                try:
                    yield Citation(
                        match=match,
                        template=self.template,
                        parent=self,
                    )
                except SyntaxError: # it's an invalid citation
                    pass
            except StopIteration:
                keep_trying = False
    
    def get_idform_cite(self, until_index: int=None):
        try:
            match = next(match_regexes(
                regexes = self.idform_regexes,
                text = self.source_text,
                span = (self.span[1], until_index)
            ))
            return Citation(match=match, template=self.template, parent=self)
        except StopIteration:
            return None
        except SyntaxError:
            return None
    
    def get_next_child(self, span: tuple=None):
        try:
            match = next(match_regexes(
                regexes = self.shortform_regexes + self.idform_regexes,
                text = self.source_text,
                span = span if span else (self.span[1], ),
            ))
            return Citation(match=match, template=self.template, parent=self)
        except StopIteration:
            return None
    
    def __str__(self):
        return str(self.text)
    
    def __repr__(self):
        return (
            f'Citation(match={self.match}, template={repr(self.template)}'
            + (f', parent={repr(self.parent)}' if self.parent else '')
        )
    
    def __contains__(self, other_cite):
        """
        Returns True if both citations are from templates with the same
        name, and the only difference between their tokens is that the
        other one has a more specific (i.e. higher-indexed) token than
        any of this one's. Severable tokens are considered a match if
        the other token's value *starts with* this one's.
        """
        if (
            other_cite.template.name != self.template.name
            or other_cite.tokens == self.tokens
        ):
            return False
        for key, value in self.tokens.items():
            if value and other_cite.tokens.get(key) != value:
                if (
                    self.template.tokens[key].severable
                    and other_cite.tokens[key]
                    and other_cite.tokens[key].startswith(value)
                ):
                    continue
                else:
                    return False
        else:
            return True
    
    def __eq__(self, other_cite):
        """
        Returns True if both citations are from templates with the same
        name, and they have the exact same token values.
        """
        return (
            other_cite.template.name == self.template.name
            and other_cite.tokens == self.tokens
        )
    
    def __len__(self):
        return len(self.text)

