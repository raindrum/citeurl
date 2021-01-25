| Sample Input                                                 | Output                                                       |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| Federal law provides that courts should award prevailing civil rights plaintiffs reasonable attorneys fees, see 42 USC § 1988(b), and, by discretion, expert fees, see *id.* at (c). This is because the importance of civil rights litigation cannot be measured by a damages judgment. *See* *Riverside v. Rivera*, 477 U.S. 561 (1986). But *Evans v. Jeff D.*, upheld a settlement where the plaintiffs got everything they wanted, on condition that they waive attorneys fees. 475 U.S. 717 (1986). This ruling lets savvy defendants create a wedge between plaintiffs and their attorneys, discouraging civil rights suits and undermining the court's logic in *Riverside*, 477 U.S. at 574-78. | Federal law provides that courts should award prevailing civil rights plaintiffs reasonable attorneys fees, see [42 USC § 1988(b)](https://www.law.cornell.edu/uscode/text/42/1988#b), and, by discretion, expert fees, see [*id.* at (c)](https://www.law.cornell.edu/uscode/text/42/1988#c). This is because the importance of civil rights litigation cannot be measured by a damages judgment. *See* *Riverside v. Rivera*, [477 U.S. 561](https://cite.case.law/us/477/561) (1986). But *Evans v. Jeff D.*, upheld a settlement where the plaintiffs got everything they wanted, on condition that they waive attorneys fees. [475 U.S. 717](https://cite.case.law/us/475/717) (1986). This ruling lets savvy defendants create a wedge between plaintiffs and their attorneys, discouraging civil rights suits and undermining the court's logic in *Riverside*, [477 U.S. at 574-78](https://cite.case.law/us/477/561#p574). |

CiteURL is an extensible tool to process legal citations in text. It recognizes longform and shortform citations, subsections and pincites, and it can generate links to view them online. It can also create a list of all the authorities cited in a document, in order of how many times each citation occurs in the text.

By default, CiteURL supports citations to U.S. court decisions, the U.S. Code and various other federal materials, plus California statutes. You can find the full list [here](https://github.com/raindrum/citeurl/blob/master/citeurl/default-schemas.yml). But you can also customize it to add support for more bodies of law by [writing your own citation schemas](https://raindrum.github.io/citeurl/#schema-yamls/) in YAML format.

For federal rules, regulations, and statutes, CiteURL's default set of schemas generates links to Cornell's [Legal Information Institute](https://www.law.cornell.edu/). For court cases, it uses Harvard's [Caselaw Access Project](https://cite.case.law/), though this will likely switch to [CourtListener](https://www.courtlistener.com/) in a future version.

## Installation

CiteURL has been tested with Python version 3.9, but earlier versions probably work. Install Python if you don't have it, then run this command:

```bash
python -m pip install citeurl
```

## Frontends

Most of the documentation on this site concerns CiteURL as a Python library you can use in your own projects. But there are a few built-in ways to use it as well. These interfaces are simpler, so their documentation is contained below:

### Command-Line Interface

The simplest way to use CiteURL is via the `citeurl` command.

To create a hyperlink for each citation in `input.html` and save the result as `output.html`, use a command like this:

```bash
citeurl -i input.html -o output.html
```

Alternatively, on many operating systems you can pipe the output of another command into CiteURL. For instance:

```bash
cat input.html | citeurl
```

If you want to look up a single citation instead of processing a block of text, use the `-l` option, like so:

```bash
citeurl -l "42 USC 1983"
```

If you want to return the top 10 authorities cited in a text, you can use this:

```bash
citeurl -i input.html -a 10
```

And if you want to use a [your own set of citation schemas](schema-yamls), you can use the `-s` option, followed by the path to a YAML file. If you want to prevent loading CiteURL's default set of schemas, use `-n`.

### Markdown Extension

CiteURL can also be used as an extension to [Python-Markdown](https://python-markdown.github.io/). You can load the extension as `citeurl`, and it supports the following options:

- `custom_schemas`: A list of paths to YAML files containing [custom citation schemas](schema-yamls). Defaults to none.
- `use_defaults`: Whether CiteURL should load the default citation schemas. Defaults to `True`.
- `attributes`: A dictionary of HTML attributes to give each hyperlink that CiteURL inserts into the text. Defaults to `{'class': 'citation'}`.
- `link_detailed_ids`: Whether to insert links for citations like `Id. at 305`. Defaults to `True`.
- `link_plain_ids`: Whether to insert links for citations like `Id.`. Defaults to `False`.

### GNOME Shell Search Provider

If you use the GNOME desktop environment, you can install [my other project](https://github.com/raindrum/gnome-citeurl-search-provider) to look up citations right from your desktop!

## Python Library

To use CiteURL as a Python library, you'll need to import the [Citator](classes#citator) class, which contains most of the important features. Then, instantiate a citator to recognize citations:

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

For more information, see the documentation on the CiteURL module's [classes](classes) and [module-level functions](functions).