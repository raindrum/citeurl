# Python Library

This page documents how to include CiteURL in your Python programming projects.

The library revolves around the concept of a [Citator](#citator), which contains and applies all of the [Templates](#templates) that detect/create [Citation](#citation) objects in text. As such, the first step is to instantiate a Citator:

```python
from citeurl import Citator
citator = Citator()
```

After that, you can feed it text to return a list of [Citation](#citation) objects:

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

Once you have a list of citations, you can get information about each one:

```python
print(citations[0].text)
# 42 USC § 1988(b)
print(citations[0].tokens)
# {'title': '42', 'section': '1988', 'subsection': '(b)'}
print(citations[0].URL)
# https://www.law.cornell.edu/uscode/text/42/1988#b
```

You can also use [insert_links()](#insert_links) to insert the citations back into the source text as HTML hyperlinks:

```python
from citeurl import insert_links
output = insert_links(citations, text)
```

Or, you can use [list_authorities()](#list_authorities) to combine all the citations into a list of all the authorities cited in the text:

```python
from citeurl import list_authorities

authorities = list_authorities(citations)
for authority in authorities:
    auth_cites = authority.citations
    print(f"{authority} was cited {len(auth_cites)}}) time(s)")

# 42 USC § 1988 was cited 2 time(s)
# 477 U.S. 561 was cited 2 time(s)
# 475 U.S. 717 was cited 1 time(s)
```

## Citator

::: citeurl.Citator

## Template

::: citeurl.Template

## Citation

::: citeurl.Citation

## Authority

::: citeurl.Authority

## insert_links()

::: citeurl.insert_links

## list_authorities()

::: citeurl.list_authorities
