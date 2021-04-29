| Sample Input                                                 | Output                                                       |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| Federal law provides that courts should award prevailing civil rights plaintiffs reasonable attorneys fees, see 42 USC § 1988(b), and, by discretion, expert fees, see *id.* at (c). This is because the importance of civil rights litigation cannot be measured by a damages judgment. *See* *Riverside v. Rivera*, 477 U.S. 561 (1986). But *Evans v. Jeff D.*, upheld a settlement where the plaintiffs got everything they wanted, on condition that they waive attorneys fees. 475 U.S. 717 (1986). This ruling lets savvy defendants create a wedge between plaintiffs and their attorneys, discouraging civil rights suits and undermining the court's logic in *Riverside*, 477 U.S. at 574-78. | Federal law provides that courts should award prevailing civil rights plaintiffs reasonable attorneys fees, see [42 USC § 1988(b)](https://www.law.cornell.edu/uscode/text/42/1988#b), and, by discretion, expert fees, see [*id.* at (c)](https://www.law.cornell.edu/uscode/text/42/1988#c). This is because the importance of civil rights litigation cannot be measured by a damages judgment. *See* *Riverside v. Rivera*, [477 U.S. 561](https://cite.case.law/us/477/561) (1986). But *Evans v. Jeff D.*, upheld a settlement where the plaintiffs got everything they wanted, on condition that they waive attorneys fees. [475 U.S. 717](https://cite.case.law/us/475/717) (1986). This ruling lets savvy defendants create a wedge between plaintiffs and their attorneys, discouraging civil rights suits and undermining the court's logic in *Riverside*, [477 U.S. at 574-78](https://cite.case.law/us/477/561#p574). |

CiteURL is an extensible tool to process legal citations in text and generate links to sites where you can view the cited language online. By default, it supports Bluebook-style citations to these bodies of law, among others:

- most state and federal court cases
- the U.S. Code and Code of Federal Regulations
- the U.S. Constitution and all state constitutions
- codified laws for every state and territory except Arkansas, Georgia, Guam, and Puerto Rico

The full list is available [here](https://github.com/raindrum/citeurl/blob/main/citeurl/builtin-templates.yaml). You can also customize CiteURL to support more bodies of law by [writing your own citation templates](https://raindrum.github.io/citeurl/#template-yamls/) in YAML format.

If you want to try out CiteURL's citation lookup features without installing anything, you can use [Law Search](https://raindrum.github.io/lawsearch), a JavaScript implementation of CiteURL I maintain on my website.

## Installation

CiteURL has been tested with Python version 3.9, but earlier versions probably work too. Install Python if you don't have it, then run this command:

```bash
python -m pip install citeurl
```

## Usage

Look up a single citation and open it directly in a browser:

```bash
citeurl -lb "42 usc 1983"
```

Process a court opinion or other text, and output a version where every citation (long or shortform) is converted into an HTML hyperlink:

```bash
citeurl -i INPUT_FILE.html -o OUTPUT_FILE.html
```

Get a list of the top 10 authorities cited in a text, ordered by the number of citations to each, [including sources of law](https://raindrum.github.io/citeurl/#template-yamls/) that CiteURL doesn't even natively support:

```bash
cat INPUT_FILE.html | citeurl -a 10 -s YOUR_CUSTOM_TEMPLATES.YAML -o OUTPUT_FILE.html
```

For more options, run `citeurl -h`.

Besides to the command-line tool, CiteURL can be used in a few other forms:

- [a tool to generate](https://raindrum.github.io/citeurl/#frontends/#javascript-generator) embeddable JavaScript so you can make your own instance of [Law Search](https://raindrum.github.io/lawsearch) with custom sources of law
- [a flexible Python library](https://raindrum.github.io/citeurl/#library), albeit one that changes fairly often
- [an extension](https://raindrum.github.io/citeurl/#frontends/#markdown-extension) to [Python-Markdown](https://python-markdown.github.io/)
- for Linux users, a [GNOME desktop search provider](https://extensions.gnome.org/extension/4225/gnome-citeurl-search-provider/)

## Credits

Many thanks to these websites, which CiteURL's default templates frequently link to:

- Harvard's [Caselaw Access Project](https://cite.case.law/) - for court cases
- Cornell's [Legal Information Institute](https://www.law.cornell.edu/) - for the U.S. Code and many federal rules
- [Ballotpedia](https://ballotpedia.org) - for the vast majority of state constitutions
- [LawServer.com](https://www.lawserver.com/tools/laws) - for statutes in about a dozen states and territories whose websites don't have a compatible URL scheme
