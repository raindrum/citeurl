from citeurl import Citator
from citeurl.makejs import makejs
from quickjs import Function

citator = Citator()

def test_makejs():
    makejs(citator)

def test_js_search_function():
    getUrlForQuery = Function('getUrlForQuery', makejs(citator))
    URL = getUrlForQuery("42 USC § 1988(b)")
    assert URL == 'https://www.law.cornell.edu/uscode/text/42/1988#b'
