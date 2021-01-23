# Getting Started

CiteURL is a tool to process legal citations in text. You can throw a court case at it and get a list of every citation in it, from `42 U.S.C. § 1983` to `Id. at § 1988(b) `. You can also use it to look up a URL to view the citation online, or insert those URLs as hyperlinks in the text.

To use CiteURL, you'll need to import the [Citator](classes#citator) class, which contains most of the important features. Then, instantiate a citator to recognize citations:

```python
from citeurl import Citator
citator = Citator()
```

After that, you can feed text to the citator to return [Citation](classes#citation) objects:

```python
text = """
Federal law provides that courts should award prevailing civil
rights plaintiffs reasonable attorneys fees, see 42 USC § 1988(b),
and, by discretion, expert fees, see id. at (c). This is because
the importance of civil rights litigation cannot be measured by a
damages judgment. See Riverside v. Rivera, 477 U.S. 561 (1986).
But Evans v. Jeff D. upheld a settlement where the plaintiffs got
everything they wanted, on the condition that they waive attorneys
fees. 475 U.S. 717 (1986). This ruling lets savvy defendants
create a wedge between plaintiffs and their attorneys, discouraging
civil rights suits and undermining the court's logic in Riverside,
477 U.S. at 574-78.
"""
citations = citator.list_citations(text)
```

Once you have a list of citations, you can get information about them:

```python
for citation in citations:
    print(citation.text + ' --- ' + str(citation.schema) + ' --- ' + citation.URL
    
# 42 USC § 1988(b) --- United States Code --- https://www.law.cornell.edu/uscode/text/42/1988#b
# id. at (c) --- United States Code --- https://www.law.cornell.edu/uscode/text/42/1988#c
# 477 U.S. 561 --- Caselaw Access Project --- https://cite.case.law/us/477/561
# 475 U.S. 717 --- Caselaw Access Project --- https://cite.case.law/us/475/717
# 477 U.S. at 574-78 --- Caselaw Access Project --- https://cite.case.law/us/477/561#p574
```

You can also use [insert_links()](functions#insert_links) to insert the citations back into the source text as hyperlinks:

```python
from citeurl import insert_links

output = insert_links(citations, text)
print(output)
# Federal law provides that courts should award prevailing civil
# rights plaintiffs reasonable attorneys fees, see <a class="citation" 
# href="https://www.law.cornell.edu/uscode/text/42/1988#b">42 USC § 1988(b)</a>,
# and, by discretion, expert fees, see <a class="citation" 
# href="https://www.law.cornell.edu/uscode/text/42/1988#c">id. at (c)</a>.
# This is because the importance of civil rights litigation cannot be
# measured by a damages judgment. See Riverside v. Rivera, <a class="citation" 
# href="https://cite.case.law/us/477/561">477 U.S. 561</a> (1986).
# But Evans v. Jeff D. upheld a settlement where the plaintiffs got
# everything they wanted, on the condition that they waive attorneys
# fees. <a class="citation" href="https://cite.case.law/us/475/717">475 U.S.
# 717</a> (1986). This ruling lets savvy defendants create a wedge between
# plaintiffs and their attorneys, discouraging civil rights suits and
# undermining the court's logic in Riverside, <a class="citation" 
# href="https://cite.case.law/us/477/561#p574">477 U.S. at 574-78</a>.
```

Or, you can use [list_authorities](functions#list_authorities) to combine the citations into a list of authorities cited in the text, and see how often each one is cited:

```python
from citeurl import list_authorities

authorities = list_authorities(citations)
for authority in authorities:
    print(authority)
    print(len(authority.citations))
# 42 USC § 1988
# 2
# 477 U.S. 561
# 2
# 475 U.S. 717
# 1
```

If you want to use CiteURL to recognize citations that aren't supported by its default library, you can create [custom citation schemas in YAML files](schema-yamls).