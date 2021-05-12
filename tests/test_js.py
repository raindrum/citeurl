"tests of CiteURL's ability to export JavaScript search engines"

from citeurl import Citator
from citeurl.web.makejs import makejs
from quickjs import Function

citator = Citator()

def test_makejs():
    "make sure the program can generate JavaScript without error"
    makejs(citator)

def test_js_search_function():
    "make sure the generated javascript actually works"
    getUrlForQuery = Function('getUrlForQuery', makejs(citator))
    URL = getUrlForQuery("42 USC § 1988(b)")
    assert URL == 'https://www.law.cornell.edu/uscode/text/42/1988#b'
