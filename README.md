| Sample Input                                                 | Output                                                       |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| Federal law provides that courts should award prevailing civil rights plaintiffs reasonable attorneys fees, see 42 USC § 1988(b), and, by discretion, expert fees, see *id.* at (c). This is because the importance of civil rights litigation cannot be measured by a damages judgment. *See* *Riverside v. Rivera*, 477 U.S. 561 (1986). But *Evans v. Jeff D.*, upheld a settlement where the plaintiffs got everything they wanted, on condition that they waive attorneys fees. 475 U.S. 717 (1986). This ruling lets savvy defendants create a wedge between plaintiffs and their attorneys, discouraging civil rights suits and undermining the court's logic in *Riverside*, 477 U.S. at 574-78. | Federal law provides that courts should award prevailing civil rights plaintiffs reasonable attorneys fees, see [42 USC § 1988(b)](https://www.law.cornell.edu/uscode/text/42/1988#b), and, by discretion, expert fees, see [*id.* at (c)](https://www.law.cornell.edu/uscode/text/42/1988#c). This is because the importance of civil rights litigation cannot be measured by a damages judgment. *See* *Riverside v. Rivera*, [477 U.S. 561](https://cite.case.law/us/477/561) (1986). But *Evans v. Jeff D.*, upheld a settlement where the plaintiffs got everything they wanted, on condition that they waive attorneys fees. [475 U.S. 717](https://cite.case.law/us/475/717) (1986). This ruling lets savvy defendants create a wedge between plaintiffs and their attorneys, discouraging civil rights suits and undermining the court's logic in *Riverside*, [477 U.S. at 574-78](https://cite.case.law/us/477/561#p574). |

CiteURL is an extensible tool to process legal citations in text and generate links to sites where you can view the cited language online. By default, it supports Bluebook-style citations to the following bodies of law, among others:

- most state and federal court cases
- the U.S. Code and Code of Federal Regulations
- the U.S. Constitution and all state constitutions
- codified laws for every state and territory except Arkansas, Georgia, Guam, and Puerto Rico

The full list is available [here](https://github.com/raindrum/citeurl/blob/main/citeurl/default-schemas.yaml). You can also customize CiteURL to support more bodies of law by [writing your own citation schemas](https://raindrum.github.io/citeurl/#schema-yamls/) in YAML format.

In addition to longform citations, CiteURL can recognize subsequent shortform citations that appear. And in addition to generating hyperlinks, it can tally up all of the times that a text cites a particular authority.

If you want to try out the citation lookup features without installing anything, you can use [LawSearch](https://raindrum.github.io/lawsearch), a JavaScript implementation of CiteURL I maintain on my website.

## Installation

CiteURL has been tested with Python version 3.9, but earlier versions probably work. Install Python if you don't have it, then run this command:

```bash
python -m pip install citeurl
```

## Usage

To run CiteURL from command prompt, use the `citeurl -h` command to see the list of options. CiteURL can also be used as an extension to [Python-Markdown](https://python-markdown.github.io/), or as a Python library.

As mentioned above, a Javascript implementation of CiteURL's citation lookup features is available [on my website](https://raindrum.github.io/lawsearch). Linux users with the GNOME shell can also install [CiteURL as a search provider](https://github.com/raindrum/gnome-citeurl-search-provider) available directly from their desktop.

More detailed documentation for each of these use-cases is available [here](https://raindrum.github.io/citeurl/).

## Credits

Many thanks to these websites, which CiteURL's default schemas frequently link to:

- Harvard's [Caselaw Access Project](https://cite.case.law/) - for court cases
- Cornell's [Legal Information Institute](https://www.law.cornell.edu/) - for the U.S. Code and many federal rules
- [Ballotpedia](https://ballotpedia.org) - for the vast majority of state constitutions
- [LawServer.com](https://www.lawserver.com/tools/laws) - for statutes in about a dozen states and territories whose websites don't have a compatible URL scheme