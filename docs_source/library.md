# Library Reference

This page documents how to include CiteURL in your Python programming projects.

The first step is to instantiate a [Citator](#citator), which by default contains all of CiteURL's built-in [Templates](#templates):

``` python
from citeurl import Citator
citator = Citator()
```

After that, you can feed it text to return a list of [Citations](#citation) it finds:

``` python
text = """
Federal law provides that courts should award prevailing civil rights plaintiffs reasonable attorneys fees, 42 USC § 1988(b), and, by discretion, expert fees, id. at (c). This is because the importance of civil rights litigation cannot be measured by a damages judgment. See Riverside v. Rivera, 477 U.S. 561 (1986). But Evans v. Jeff D. upheld a settlement where the plaintiffs got everything they wanted, on condition that they waive attorneys' fees. 475 U.S. 717 (1986). This ruling lets savvy defendants create a wedge between plaintiffs and their attorneys, discouraging civil rights suits and undermining the court's logic in Riverside, 477 U.S. at 574-78.
"""
citations = citator.list_cites(text)
```

Once you have a list of citations, you can get information about each one:

```python
print(citations[0].text)
# 42 USC § 1988(b)
print(citations[0].tokens)
# {'Title': '42', 'Section': '1988', 'subsection': '(b)'}
print(citations[0].URL)
# https://www.law.cornell.edu/uscode/text/42/1988#b
```

You can also compare citations to one another, to determine whether they reference the same material or a subsection thereof:

```python
art_I = citator.cite('U.S. Const. Art. I')
also_art_I = citator.cite('Article I of the U.S. Constitution')
art_I_sec_3 = citator.cite('U.S. Const. Art. I, § 3')

assert art_I == also_art_I
assert art_I_sec_3 in art_I
```

If you don't want to bother with all the details, you can also just use [insert_links()](#insert_links) to turn all the citations in a text into hyperlinks:

```python
from citeurl import insert_links

text = "42 USC § 1988. <i>Id.</i> at (b)."
output = insert_links(text)

assert output == '<a class="citation" href="https://www.law.cornell.edu/uscode/text/42/1988" title="42 U.S.C. § 1988">42 USC § 1988</a>. <a class="citation" href="https://www.law.cornell.edu/uscode/text/42/1988#b" title="42 U.S.C. § 1988(b)"><i>Id.</i> at (b)</a>.'
```

## Citator

::: citeurl.Citator

## Citation

::: citeurl.Citation

## Template

::: citeurl.Template

## TokenType

::: citeurl.TokenType

## TokenOperation

::: citeurl.TokenOperation

## StringBuilder

::: citeurl.StringBuilder

## insert_links()

::: citeurl.insert_links

## cite()

::: citeurl.cite

## list_cites()

::: citeurl.list_cites

## DEFAULT_CITATOR

The [insert_links](#insert_links), [cite](#cite), and [list_cites](#list_cites) functions all make use of a built-in [citator](#Citator) that is not defined by the library user. By default, this is the citator that is returned when you run `Citator()`. However, it is possible to add additional templates to this default citator, by installing the wonderful [AppDirs](https://pypi.org/project/appdirs) library and placing the templates in one of the following directories:

Linux: `~/.config/citeurl`

Mac: `~/Library/Preferences/citeurl`

Windows 7+: `C:\Users\<username>\AppData\Local\raindrum\citeurl`
