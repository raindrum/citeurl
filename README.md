[![pytest](https://github.com/raindrum/citeurl/actions/workflows/pytest.yml/badge.svg)](https://github.com/raindrum/citeurl/actions/workflows/pytest.yml) [![GitHub issues](https://img.shields.io/github/issues/raindrum/citeurl)](https://github.com/raindrum/citeurl/issues) [![GitHub license](https://img.shields.io/github/license/raindrum/citeurl)](https://github.com/raindrum/citeurl/blob/main/LICENSE.md) [![PyPI](https://img.shields.io/pypi/v/citeurl)](https://pypi.org/project/citeurl/)

CiteURL is an extensible tool to process long and shortform legal citations in text and generate links to various websites where you can view the cited language for free. Here's an example of what it can do:

| Sample Input                                                 | Output                                                       |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| Federal law provides that courts should award prevailing civil rights plaintiffs reasonable attorneys fees, 42 USC § 1988(b), and, by discretion, expert fees, *id.* at (c). This is because the importance of civil rights litigation cannot be measured by a damages judgment. *See* *Riverside v. Rivera*, 477 U.S. 561 (1986). But *Evans v. Jeff D.* upheld a settlement where the plaintiffs got everything they wanted, on condition that they waive attorneys' fees. 475 U.S. 717 (1986). This ruling lets savvy defendants create a wedge between plaintiffs and their attorneys, discouraging civil rights suits and undermining the court's logic in *Riverside*, 477 U.S. at 574-78. | Federal law provides that courts should award prevailing civil rights plaintiffs reasonable attorneys fees, [42 USC § 1988(b)](https://www.law.cornell.edu/uscode/text/42/1988#b), and, by discretion, expert fees, [*id.* at (c)](https://www.law.cornell.edu/uscode/text/42/1988#c). This is because the importance of civil rights litigation cannot be measured by a damages judgment. *See* *Riverside v. Rivera*, [477 U.S. 561](https://cite.case.law/us/477/561) (1986). But *Evans v. Jeff D.* upheld a settlement where the plaintiffs got everything they wanted, on condition that they waive attorneys' fees. [475 U.S. 717](https://cite.case.law/us/475/717) (1986). This ruling lets savvy defendants create a wedge between plaintiffs and their attorneys, discouraging civil rights suits and undermining the court's logic in *Riverside*, [477 U.S. at 574-78](https://cite.case.law/us/477/561#p574). |

By default, CiteURL supports Bluebook-style citations to [over 130 sources](https://github.com/raindrum/citeurl/blob/main/citeurl/builtin-templates.yaml) of U.S. law, including:

- most state and federal court cases
- the U.S. Code and Code of Federal Regulations
- the U.S. Constitution and all state constitutions
- codified laws for every state and territory except Arkansas, Georgia, Guam, and Puerto Rico.

You can also customize CiteURL to support more sources of law by [writing your own citation templates](https://raindrum.github.io/citeurl/template-yamls/) in YAML format.

If you want to try out CiteURL's citation lookup features without installing anything, you can use [Law Search](https://raindrum.github.io/lawsearch), a JavaScript implementation of CiteURL I maintain on my website.

## Installation

CiteURL has been tested with Python version 3.9, but earlier versions probably work too. Install Python if you don't have it, then run this command:

```bash
python -m pip install citeurl
```

## Usage

CiteURL provides four command-line tools:

- `citeurl process`: Parse a text and insert an HTML hyperlink for every citation it contains, including shortform citations.
- `citeurl lookup`: Look up a single citation and display information about it.
- `citeurl host`: Host a citation lookup service via HTTP.
- `citeurl makejs`: Export an instance of CiteURL's lookup function as JavaScript that can be embedded in an HTML page. [Law Search](https://raindrum.github.io/lawsearch) is an example of this JavaScript. More info is available [here](https://raindrum.github.io/citeurl/frontends#javascript).

Each command has its own command-line arguments you can view with the `-h` option. They all share the `-t` option, which allows you to load a list of custom [citation templates](https://raindrum.github.io/citeurl/template-yamls/) in YAML form.

Here are a few common use cases:

```bash
# Process a court opinion and output a version where each citation is hyperlinked:
citeurl process -i INPUT_FILE.html -o OUTPUT_FILE.html
```

```bash
# Look up a single citation and open it directly in a browser
citeurl lookup "42 USC 1983" -b
```

```bash
# List the top ten authorities cited in a text, from most citations to least:
cat INPUT_FILE.html | citeurl process -a 10
```

```bash
# Host a lookup tool with custom templates, and serve it on the local network:
citeurl host -t PATH_TO_YOUR_TEMPLATES.YAML -s
```

Besides to the command-line interface, CiteURL can be used in a few other forms:

- [a flexible Python library](https://raindrum.github.io/citeurl/library)
- [an extension](https://raindrum.github.io/citeurl/frontends#markdown-extension) to [Python-Markdown](https://python-markdown.github.io/)
- [a search provider](https://extensions.gnome.org/extension/4225/gnome-citeurl-search-provider/) for Linux users with the GNOME shell

## Credits

Many thanks to these websites, which CiteURL's default templates frequently link to:

- Harvard's [Caselaw Access Project](https://cite.case.law/) - for court cases
- Cornell's [Legal Information Institute](https://www.law.cornell.edu/) - for the U.S. Code and many federal rules
- [Ballotpedia](https://ballotpedia.org) - for the vast majority of state constitutions
- [LawServer.com](https://www.lawserver.com/tools/laws) - for statutes in about a dozen states and territories whose websites don't have a compatible URL scheme