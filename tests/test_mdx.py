"tests for CiteURL's extension to Python-Markdown"

from markdown import markdown

def test_default_mdx():
    "make sure the default markdown extension works"
    output = markdown('413 F. Supp. 1281', extensions=['citeurl'])
    assert output == '<p><a class="citation" href="https://case.law/caselaw/?reporter=f-supp&volume=413&case=1281-01" title="413 F. Supp. 1281">413 F. Supp. 1281</a></p>'

def test_configured_mdx():
    "make sure at least a few of the markdown config options work"
    output = markdown(
        '413 F. Supp. 1281',
        extensions=['citeurl'],
        extension_configs={'citeurl': {'attributes': {'class': 'cite'}}}
    )
    assert output == '<p><a class="cite" href="https://case.law/caselaw/?reporter=f-supp&volume=413&case=1281-01" title="413 F. Supp. 1281">413 F. Supp. 1281</a></p>'
