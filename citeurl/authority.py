import re
from typing import Union
from functools import cached_property
from copy import copy

from .citator import list_cites
from .citation import Citation

class Authority:
    def __init__(
        self,
        model_cite: Citation,
        ignored_tokens = ['subsection', 'clause', 'pincite', 'paragraph'],
    ):
        self.template = model_cite.template
        self.ignored_tokens = ignored_tokens
        self.tokens = {}
        for key, value in model_cite.tokens.items():
            if key in ignored_tokens:
                break
            else:
                self.tokens[key] = value
        self.citations = [model_cite]
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return (
            f'{self.name} ({len(self.citations)} '
            f'cite{"s" if len(self.citations) > 1 else ""})'
        )
    
    def __contains__(self, cite: Citation):
        if cite.template.name != self.template.name:
            return False
        for key, value in self.tokens.items():
            if value and cite.tokens.get(key) != value:
                if (
                    self.template.tokens[key].severable
                    and cite.tokens[key]
                    and cite.tokens[key].startswith(value)
                ):
                    continue
                else:
                    return False
        else:
            return True
    
    @cached_property
    def name(self):
        # build a name the proper way if a name_builder is defined
        if self.template.name_builder:
            return self.template.name_builder(self.tokens)
        
        # otherwise use horrible regex magic to reverse-engineer a name.
        # first find a longform citation to use as a starting point
        base_cite = self.citations[0]
        while base_cite.parent:
            base_cite = base_cite.parent
        
        # next construct a regex pattern to pull out the relevant
        # tokens, along with the non-token text preceding each one.
        # the non-token "prelude" text lets us replace the text of each
        # token only when it appears in the proper context
        pattern = ''
        for token in self.tokens:
            regex = re.escape(base_cite.tokens[token])
            segment = f"""((?P<{token}_prelude>.*?)(?P<{token}>{regex}))?"""
            if pattern:
                pattern = pattern[:-2] + segment + ')?'
            else:
                pattern = segment
        
        match = re.match(pattern, base_cite.text)
        
        # slice off all the text after the last relevant token. This is
        # to remove thingsl like subsections, etc. It assumes that all
        # the optional tokens (subsection, pincite, etc) appear *after*
        # all the mandatory ones.
        base_cite_text = base_cite.text[:match.span(token)[1]]
        
        # for each token, replace the value from the longform citation
        # with the corresponding value for *this* authority
        for token in self.tokens:
            if not match.group(token):
                continue
            prelude = str(match.group(f'{token}_prelude'))
            old_value = prelude + match.group(token)
            new_value = prelude + self.tokens[token]
            base_cite_text = base_cite_text.replace(old_value, new_value)
        return base_cite_text
    
    @cached_property
    def URL(self):
        if self.template.URL_builder:
            url =  self.template.URL_builder(self.tokens)
            if url:
                url = url.replace(' ', '%20')
        else:
            url = None
        return url
        

def list_authorities(
    source: Union[list[Citation], str],
    ignored_tokens = ['subsection', 'clause', 'pincite', 'paragraph'],
) -> list[Authority]:
    """
    Get a list of all the authorities that appear in the given list of
    citations. An authority represents a distinct section of law or
    court case. Two citations to the same authority can have different
    tokens, as long as those tokens are in the list of ignored_tokens
    """
    authorities = []
    if type(source) is str:
        source = list_cites(source)
    for cite in source:
        for authority in authorities:
            if cite in authority:
                authority.citations.append(cite)
                break
        else:
            authorities.append(Authority(cite, ignored_tokens))
    authorities.sort(key=lambda x: -len(x.citations))
    return authorities
