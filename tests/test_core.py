"""
tests of CiteURL's core functions:
recognizing long and shortform citations, inserting links into text,
and aggregating citations into authorities
"""

from citeurl import Citator, list_authorities

TEXT = """Federal law provides that courts should award prevailing civil rights plaintiffs reasonable attorneys fees, 42 USC § 1988(b), and, by discretion, expert fees, id. at (c). This is because the importance of civil rights litigation cannot be measured by a damages judgment. See Riverside v. Rivera, 477 U.S. 561 (1986). But Evans v. Jeff D. upheld a settlement where the plaintiffs got everything they wanted, on condition that they waive attorneys' fees. 475 U.S. 717 (1986). This ruling lets savvy defendants create a wedge between plaintiffs and their attorneys, discouraging civil rights suits and undermining the court's logic in Riverside, 477 U.S. at 574-78."""

def test_init_citator():
    Citator()
    
def test_list_citations():
    citations = Citator().list_citations(TEXT)
    
    assert citations[0].text == '42 USC § 1988(b)'
    assert citations[0].tokens == {
        'title': '42',
        'section': '1988',
        'subsection': '(b)'
    }
    assert citations[0].URL == (
        'https://www.law.cornell.edu/uscode/text/42/1988#b'
    )
    assert citations[1].tokens == {
        'title': '42',
        'section': '1988',
        'subsection': '(c)'
    }

def test_insert_links():
    output = Citator().insert_links(TEXT)
    assert output == """Federal law provides that courts should award prevailing civil rights plaintiffs reasonable attorneys fees, <a class="citation" href="https://www.law.cornell.edu/uscode/text/42/1988#b">42 USC § 1988(b)</a>, and, by discretion, expert fees, <a class="citation" href="https://www.law.cornell.edu/uscode/text/42/1988#c">id. at (c)</a>. This is because the importance of civil rights litigation cannot be measured by a damages judgment. See Riverside v. Rivera, <a class="citation" href="https://cite.case.law/us/477/561">477 U.S. 561</a> (1986). But Evans v. Jeff D. upheld a settlement where the plaintiffs got everything they wanted, on condition that they waive attorneys' fees. <a class="citation" href="https://cite.case.law/us/475/717">475 U.S. 717</a> (1986). This ruling lets savvy defendants create a wedge between plaintiffs and their attorneys, discouraging civil rights suits and undermining the court's logic in Riverside, <a class="citation" href="https://cite.case.law/us/477/561#p574">477 U.S. at 574-78</a>."""

def test_list_authorities():
    citations = Citator().list_citations(TEXT)
    authorities = list_authorities(citations)
    assert authorities[0].name == '42 USC § 1988'
    assert authorities[1].name == '477 U.S. 561'
    assert len(authorities[1].citations) == 2

def test_lookup():
    assert Citator().lookup('42 usc 1983')

def test_link_plain_ids():
    c = Citator()
    output = c.insert_links('42 U.S.C. § 1983. Id.', link_plain_ids=True)
    assert 'Id.</a>' in output
