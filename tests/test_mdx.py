from markdown import Markdown

input_1 = """Federal law provides that courts should award prevailing civil rights plaintiffs reasonable attorneys fees, 42 USC § 1988(b), and, by discretion, expert fees, *id.* at (c). This is because the importance of civil rights litigation cannot be measured by a damages judgment. See *Riverside v. Rivera*, 477 U.S. 561 (1986). But *Evans v. Jeff D.* upheld a settlement where the plaintiffs got everything they wanted, on condition that they waive attorneys' fees. 475 U.S. 717 (1986). This ruling lets savvy defendants create a wedge between plaintiffs and their attorneys, discouraging civil rights suits and undermining the court's logic in *Riverside*, 477 U.S. at 574-78."""

expected_output_1 = """<p>Federal law provides that courts should award prevailing civil rights plaintiffs reasonable attorneys fees, <a class="citation" href="https://www.law.cornell.edu/uscode/text/42/1988#b">42 USC § 1988(b)</a>, and, by discretion, expert fees, <em><a class="citation" href="https://www.law.cornell.edu/uscode/text/42/1988#c">id.</em> at (c)</a>. This is because the importance of civil rights litigation cannot be measured by a damages judgment. See <em>Riverside v. Rivera</em>, <a class="citation" href="https://cite.case.law/us/477/561">477 U.S. 561</a> (1986). But <em>Evans v. Jeff D.</em> upheld a settlement where the plaintiffs got everything they wanted, on condition that they waive attorneys' fees. <a class="citation" href="https://cite.case.law/us/475/717">475 U.S. 717</a> (1986). This ruling lets savvy defendants create a wedge between plaintiffs and their attorneys, discouraging civil rights suits and undermining the court's logic in <em>Riverside</em>, <a class="citation" href="https://cite.case.law/us/477/561#p574">477 U.S. at 574-78</a>.</p>"""

input_2 = """*In rem* jurisdiction has spawned a number of lawsuits with delightfully absurd names. See, e.g., *United States v. An Article Consisting of Boxes of Clacker Balls*, 413 F. Supp. 1281 (1976). The defendant in that case was "50,000 cardboard boxes, more or less, each containing one pair of clacker balls." *Id.*

## Interrupting Heading

Because there is a second-level header, the next citation should not be hyperlinked. Don't see *Id.*"""

expected_output_2 = """<p><em>In rem</em> jurisdiction has spawned a number of lawsuits with delightfully absurd names. See, e.g., <em>United States v. An Article Consisting of Boxes of Clacker Balls</em>, <a class="cite" rel="external" href="https://cite.case.law/f-supp/413/1281">413 F. Supp. 1281</a> (1976). The defendant in that case was "50,000 cardboard boxes, more or less, each containing one pair of clacker balls." <em><a class="cite" rel="external" href="https://cite.case.law/f-supp/413/1281">Id.</em></a></p>
<h2>Interrupting Heading</h2>
<p>Because there is a second-level header, the next citation should not be hyperlinked. Don't see <em>Id.</em></p>"""

def test_configured_mdx():
    parser = Markdown(extensions=['citeurl'], extension_configs={
        'citeurl': {
            'attributes': {'class': 'cite', 'rel': 'external'},
            'break_id_on_regex': '<h2>',
            'link_plain_ids': True
        }
    })
    output = parser.convert(input_2)
    print(output)
    assert output == expected_output_2

def test_default_mdx():
    parser = Markdown(extensions=['citeurl'])
    output = parser.convert(input_1)
    print(output)
    assert output == expected_output_1


