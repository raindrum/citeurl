from markdown import markdown

def test_default_mdx():
    output = markdown('413 F. Supp. 1281', extensions=['citeurl'])
    assert output == '<p><a class="citation" href="https://cite.case.law/f-supp/413/1281">413 F. Supp. 1281</a></p>'

def test_configured_mdx():
    output = markdown(
        '413 F. Supp. 1281',
        extensions=['citeurl'],
        extension_configs={'citeurl': {'attributes': {'class': 'cite'}}}
    )
    assert output == '<p><a class="cite" href="https://cite.case.law/f-supp/413/1281">413 F. Supp. 1281</a></p>'
