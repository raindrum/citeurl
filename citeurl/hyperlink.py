from . import Citation

def insert_links(
    citations: list[Citation],
    text: str,
    attrs: dict = {'class': 'citation'},
    add_title: bool = True,
    URL_optional: bool = False,
    redundant_links: bool = True,
) -> str:
    """
    Add each citation back into the given text as HTML hyperlinks,
    placed via the spans where they were initially found.
    
    Arguments:
        citations: list of citation objects to insert back into the text
        text: the string where all the citations were found.
        attrs: various HTML link attributes to give each inserted link
        add_title: whether to use citation.name for link titles
        URL_optional: whether to insert a hyperlink even when the
            citation does not have an associated URL
        redundant_links: whether to insert a hyperlink if it would go to
            the same URL as the previous link
    
    Returns:
        text, with an HTML `a` element for each citation. 
    """    
    offset = 0
    last_URL = None
    for cite in citations:
        attrs['href'] = cite.URL
        
        if not cite.URL and not URL_optional:
            continue
        if not redundant_links and cite.URL == last_URL:
            continue
        
        if add_title:
            attrs['title'] = cite.name
        
        attr_str = ''.join([
            f' {k}="{v}"'
            for k, v in attrs.items() if v
        ])
        link = f'<a{attr_str}>{cite.text}</a>'
        
        span = (
            cite.span[0] + offset,
            cite.span[1] + offset,
        )
        text = text[:span[0]] + link + text[span[1]:]
        
        offset += len(link) - len(cite.text)
        last_URL = cite.URL
    return text
