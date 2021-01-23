| Sample Input                                                 | Output                                                       |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| Federal law provides that courts should award prevailing civil rights plaintiffs reasonable attorneys fees, see 42 USC § 1988(b), and, by discretion, expert fees, see *id.* at (c). This is because the importance of civil rights litigation cannot be measured by a damages judgment. *See* *Riverside v. Rivera*, 477 U.S. 561 (1986). But *Evans v. Jeff D.*, upheld a settlement where the plaintiffs got everything they wanted, on condition that they waive attorneys fees. 475 U.S. 717 (1986). This ruling lets savvy defendants create a wedge between plaintiffs and their attorneys, discouraging civil rights suits and undermining the court's logic in *Riverside*, 477 U.S. at 574-78. | Federal law provides that courts should award prevailing civil rights plaintiffs reasonable attorneys fees, see [42 USC § 1988(b)](https://www.law.cornell.edu/uscode/text/42/1988#b), and, by discretion, expert fees, see [*id.* at (c)](https://www.law.cornell.edu/uscode/text/42/1988#c). This is because the importance of civil rights litigation cannot be measured by a damages judgment. *See* *Riverside v. Rivera*, [477 U.S. 561](https://cite.case.law/us/477/561) (1986). But *Evans v. Jeff D.*, upheld a settlement where the plaintiffs got everything they wanted, on condition that they waive attorneys fees. [475 U.S. 717](https://cite.case.law/us/475/717) (1986). This ruling lets savvy defendants create a wedge between plaintiffs and their attorneys, discouraging civil rights suits and undermining the court's logic in *Riverside*, [477 U.S. at 574-78](https://cite.case.law/us/477/561#p574). |

# CiteURL

CiteURL is an extensible tool to process legal citations in text. It recognizes longform and shortform citations, subsections and pincites, and it can generates links to view them online. It can also create a list of all the authorities cited in a document, in order of how many citation

By default, CiteURL supports citations to U.S. court decisions, the U.S. Code and various other federal materials, plus California statutes. You can find the full list [here](https://github.com/raindrum/citeurl/blob/master/citeurl/default-schemas.yml). But you can also customize it to add support for more bodies of law by [writing your own citation schemas](https://raindrum.github.io/citeurl/#schema-yamls/) in YAML format.

For federal rules, regulations, and statutes, CiteURL's default set of schemas generates links to Cornell's [Legal Information Institute](https://www.law.cornell.edu/). For court cases, it uses Harvard's [Caselaw Access Project](https://cite.case.law/), though this will likely switch to [CourtListener](https://www.courtlistener.com/) in a future version.

## Installation

CiteURL has been tested with Python version 3.9, but earlier versions probably work. Install Python if you don't have it, then run this command:

```bash
python -m pip install citeurl
```

## Usage

CiteURL can be used as a command-line tool, a Python library, or an extension to [Python-Markdown](https://python-markdown.github.io/).

### Command Line

The simplest way to use CiteURL is the `citeurl` command.

To create a hyperlink for each citation in input.html, and save the result as output.html, use a command like this:

```bash
citeurl -i input.html -o output.html
```

Alternatively, on many operating systems you can pipe the output of another command into CiteURL. For instance:
```bash
cat input.html | citeurl -o output.html
```

To return the URL for a single citation instead of processing a block of text, use the `-l` option. For instance, the following command will print [this URL](https://www.law.cornell.edu/uscode/text/42/1983) in your terminal:
```bash
citeurl -l "42 USC 1983"
```

To return the top 10 authorities cited in an opinion, use this:

```bash
citeurl -i path_to_opinion.html -a 10
```

To provide a custom set of citation schemas, use the `-s` option, followed by the path to a YAML file containing one or more schemas. You can specify the `-s` option multiple times to load multiple files. To prevent loading CiteURL's default schemas, use the `-n` option.

### Python Library

Most of CiteURL's more advanced features are best accessed through the Python library. Here's a quick setup guide:

```python
from citeurl import Citator

citator = Citator()
text = "People can sue the government for violating their rights. 42 U.S.C. § 1983. These lawsuits provide for attorneys fees. Id. at § 1988(b)."
for citation in citator.list_citations(text):
    print(citation.URL)
# https://www.law.cornell.edu/uscode/text/42/1983
# https://www.law.cornell.edu/uscode/text/42/1988#b
```

For more information, see the [CiteURL documentation](https://raindrum.github.io/citeurl/).

### Markdown Extension

In addition to a command-line tool, CiteURL can be used as a [Python-Markdown](https://python-markdown.github.io/) extension. The extension can simply be loaded as `citeurl`, and it supports the following options:

- `custom_schemas`: A list of paths to YAML files containing custom citation schemas. Defaults to none.
- `use_defaults`: A boolean representing whether CiteURL should load the [default schemas](https://github.com/raindrum/citeurl/blob/master/citeurl/default-schemas.yaml). Defaults to `True`.
- `attributes`: A dictionary of attributes (other than href) that inserted \<a> elements should have. Defaults to `{'class': 'citation'}`.
- `link_detailed_ids`: A boolean representing whether to insert links for citations like `Id. at 305.` Defaults to `True`.
- `link_plain_ids`: A boolean representing whether to insert links for citations like `Id.` Defaults to `False`.

Note that this extension will slow down Python-Markdown quite a bit, since it requires processing a long list of complicated regexes.
