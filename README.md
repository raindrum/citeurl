<p align="center"><a href="https://www.citation.link"><img src="https://raw.githubusercontent.com/raindrum/citeurl/main/citeurl/web/logo.svg" alt="CiteURL Logo" width=200px></a></p>
<p align="center"><a href="https://github.com/raindrum/citeurl/actions/workflows/pytest.yml"><img src="https://github.com/raindrum/citeurl/actions/workflows/pytest.yml/badge.svg" alt="pytest" /></a> <a href="https://github.com/raindrum/citeurl/issues"><img src="https://img.shields.io/github/issues/raindrum/citeurl" alt="GitHub issues" /></a> <a href="https://github.com/raindrum/citeurl/blob/main/LICENSE.md"><img src="https://img.shields.io/github/license/raindrum/citeurl" alt="GitHub license" /></a> <a href="https://pypi.org/project/citeurl/"><img src="https://img.shields.io/pypi/v/citeurl" alt="PyPI" /></a></p>

CiteURL is an extensible tool that parses legal citations and makes links to websites where you can read the cited language for free. It can be used to quickly look up a reference, or to insert a hyperlink for every long- or short-form citation in a longer text.

If you want to quickly try it out, it's available as a web app at [citation.link](https://www.citation.link).

---

Here's a sample of the links CiteURL can make:

> Federal law provides that courts should award prevailing civil rights plaintiffs reasonable attorneys fees, <a class="citation" href="https://www.law.cornell.edu/uscode/text/42/1988#b" title="42 U.S.C. § 1988(b)">42 USC § 1988(b)</a>, and, by discretion, expert fees, <a class="citation" href="https://www.law.cornell.edu/uscode/text/42/1988#c" title="42 U.S.C. § 1988(c)">id. at (c)</a>. This is because the importance of civil rights litigation cannot be measured by a damages judgment. See Riverside v. Rivera, <a class="citation" href="https://cite.case.law/us/477/561" title="477 U.S. 561">477 U.S. 561</a> (1986). But Evans v. Jeff D. upheld a settlement where the plaintiffs got everything they wanted, on condition that they waive attorneys' fees. <a class="citation" href="https://cite.case.law/us/475/717" title="475 U.S. 717">475 U.S. 717</a> (1986). This ruling lets savvy defendants create a wedge between plaintiffs and their attorneys, discouraging civil rights suits and undermining the court's logic in Riverside, <a class="citation" href="https://cite.case.law/us/477/561#p574" title="477 U.S. 561, 574">477 U.S. at 574</a>-78.

---

By default, CiteURL supports Bluebook-style citations to [over 130 sources](https://github.com/raindrum/citeurl/blob/main/citeurl/templates) of U.S. law, including:

- most state and federal court cases
- the U.S. Code and Code of Federal Regulations
- the U.S. Constitution and all state constitutions
- the codified laws for every state and territory except Arkansas, Georgia, Guam, and Puerto Rico.

You can also add more sources of law by [writing your own citation templates](https://raindrum.github.io/citeurl/template-yamls/) in YAML format.

## Installation

```bash
python3 -m pip install citeurl
```

## Usage

CiteURL provides four command-line tools:

- `citeurl process`: Parse a text and insert an HTML hyperlink for every citation it contains, including shortform citations.
- `citeurl lookup`: Look up a single citation and display information about it.
- `citeurl host`: Host an instance of CiteURL as a web app like [citation.link](https://www.citation.link).
- `citeurl makejs`: Export an instance of CiteURL's lookup feature as JavaScript or a static web page. More info is available [here](https://raindrum.github.io/citeurl/frontends#javascript).

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

CiteURL is also available in a few other forms besides the command-line tool: 

- [citation.link](https://www.citation.link), the web app
- [a flexible Python library](https://raindrum.github.io/citeurl/library)
- [an extension](https://raindrum.github.io/citeurl/frontends#markdown-extension) to [Python-Markdown](https://python-markdown.github.io/)
- [a desktop search provider](https://extensions.gnome.org/extension/4225/gnome-citeurl-search-provider/) for Linux users with the GNOME shell

## Credits

Many thanks to these websites, which CiteURL's default templates frequently link to:

- Harvard's [Caselaw Access Project](https://cite.case.law/) - for most court cases
- [CourtListener](https://www.courtlistener.com/) - for other court cases
- Cornell's [Legal Information Institute](https://www.law.cornell.edu/) - for the U.S. Code and many federal rules
- [Ballotpedia](https://ballotpedia.org) - for the vast majority of state constitutions
- [LawServer.com](https://www.lawserver.com/tools/laws) - for statutes in about a dozen states and territories whose websites don't have a compatible URL scheme
