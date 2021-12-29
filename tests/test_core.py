"""
tests of CiteURL's core functions:
recognizing long and shortform citations, inserting links into text,
and aggregating citations into authorities
"""

from citeurl import Citator, insert_links, list_cites, cite

TEXT = """Federal law provides that courts should award prevailing civil rights plaintiffs reasonable attorneys fees, 42 USC § 1988(b), and, by discretion, expert fees, id. at (c). This is because the importance of civil rights litigation cannot be measured by a damages judgment. See Riverside v. Rivera, 477 U.S. 561 (1986). But Evans v. Jeff D. upheld a settlement where the plaintiffs got everything they wanted, on condition that they waive attorneys' fees. 475 U.S. 717 (1986). This ruling lets savvy defendants create a wedge between plaintiffs and their attorneys, discouraging civil rights suits and undermining the court's logic in Riverside, 477 U.S. at 574-78."""

def test_init_citator():
    Citator()
    
def test_list_citations():
    citations = list_cites(TEXT)
    
    assert str(citations[0]) == '42 USC § 1988(b)'
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
    citations = list_cites(TEXT)
    output = insert_links(TEXT)
    assert output == """Federal law provides that courts should award prevailing civil rights plaintiffs reasonable attorneys fees, <a class="citation" href="https://www.law.cornell.edu/uscode/text/42/1988#b" title="42 U.S.C. § 1988(b)">42 USC § 1988(b)</a>, and, by discretion, expert fees, <a class="citation" href="https://www.law.cornell.edu/uscode/text/42/1988#c" title="42 U.S.C. § 1988(c)">id. at (c)</a>. This is because the importance of civil rights litigation cannot be measured by a damages judgment. See Riverside v. Rivera, <a class="citation" href="https://cite.case.law/us/477/561" title="477 U.S. 561">477 U.S. 561</a> (1986). But Evans v. Jeff D. upheld a settlement where the plaintiffs got everything they wanted, on condition that they waive attorneys\' fees. <a class="citation" href="https://cite.case.law/us/475/717" title="475 U.S. 717">475 U.S. 717</a> (1986). This ruling lets savvy defendants create a wedge between plaintiffs and their attorneys, discouraging civil rights suits and undermining the court\'s logic in Riverside, <a class="citation" href="https://cite.case.law/us/477/561#p574" title="477 U.S. 561, 574">477 U.S. at 574</a>-78."""

#def test_list_authorities():
#    citations = Citator().list_cites(TEXT)
#    authorities = list_authorities(citations)
#    assert str(authorities[0]) == '42 USC § 1988'
#    assert str(authorities[1]) == '477 U.S. 561'
#    assert len(authorities[1].citations) == 2

def test_lookup():
    citation = cite('42 usc 1983')
    assert citation is not None

def test_redundant_links():
    text = '42 U.S.C. § 1983. Id.'
    cites = list_cites(text)
    output = insert_links(text, redundant_links=True)
    assert 'Id.</a>' in output

def test_require_wordbreaks_after_tokens():
    text = """
    Initial cite: Cal. Const. Art. I § 7.
    Intervening cite: 56 U.S. 365.
    False shortform: Section 778a."""
    assert len(list_cites(text)) == 2

def test_ignore_markup():
    text = '42 <strong>USC</strong> § 1983. <i>Id.</i> at (b)'
    output = insert_links(text)
    assert '(b)</a>' in output
