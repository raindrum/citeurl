# python standard imports
from typing import Iterable
import re

def process_pattern(
    pattern: str,
    replacements: dict[str, str],
    token_prefix: str=None,
    add_word_breaks: bool=False,
):
    """
    For a given regex pattern, find all the places that a key in the
    replacements dict appears, enclosed in curly braces. Replace each
    one with the corresponding value, enclosed in parentheses.
    
    If token_prefix is provided, it will only replace placeholders that
    that start with that prefix, e.g. the 'same' in "{same volume}" or
    "{same reporter}".
    
    If add_word_breaks is True, a mandatory word break will be added at
    the beginning and end of the pattern. 
    """
    
    for key, value in replacements.items():
        if not value:
            continue
        if token_prefix:
            marker = '{%s %s}' % (token_prefix, key)
        else:
            marker = '{%s}' % key
        if not (value.startswith('(') and value.endswith(')')):
            value = f'({value})'
        value = fr'{value}(?=\W|$)'
        pattern = pattern.replace(marker, value)
    if add_word_breaks:
        pattern = rf'(?<!\w){pattern}(?!=\w)'
    return pattern


def match_regexes(text: str, regexes: list, span: tuple=(0,)) -> Iterable:
    """
    For a given text and set of regex Pattern objects, generate each
    non-overlapping match found for any regex. Regexes earlier in
    the list take priority over later ones, such that a span of text
    that matches the first regex cannot also match the second.
    """
    start = span[0]
    if len(span) > 1:
        end = span[1]
    else:
        end = None
    
    keep_trying = True
    while keep_trying:
        span = (start, end) if end else (start,)
        matches = []
        for regex in regexes:
            match = regex.search(text, *span)
            if match:
                matches.append(match)
        if matches:
            matches.sort(key=lambda x: (x.span()[0], -len(x.group())))
            start = matches[0].span()[1]
            yield matches[0]
        else:
            keep_trying = False
