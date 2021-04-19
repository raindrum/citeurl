| Sample Input                                                 | Output                                                       |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| Federal law provides that courts should award prevailing civil rights plaintiffs reasonable attorneys fees, see 42 USC § 1988(b), and, by discretion, expert fees, see *id.* at (c). This is because the importance of civil rights litigation cannot be measured by a damages judgment. *See* *Riverside v. Rivera*, 477 U.S. 561 (1986). But *Evans v. Jeff D.*, upheld a settlement where the plaintiffs got everything they wanted, on condition that they waive attorneys fees. 475 U.S. 717 (1986). This ruling lets savvy defendants create a wedge between plaintiffs and their attorneys, discouraging civil rights suits and undermining the court's logic in *Riverside*, 477 U.S. at 574-78. | Federal law provides that courts should award prevailing civil rights plaintiffs reasonable attorneys fees, see [42 USC § 1988(b)](https://www.law.cornell.edu/uscode/text/42/1988#b), and, by discretion, expert fees, see [*id.* at (c)](https://www.law.cornell.edu/uscode/text/42/1988#c). This is because the importance of civil rights litigation cannot be measured by a damages judgment. *See* *Riverside v. Rivera*, [477 U.S. 561](https://cite.case.law/us/477/561) (1986). But *Evans v. Jeff D.*, upheld a settlement where the plaintiffs got everything they wanted, on condition that they waive attorneys fees. [475 U.S. 717](https://cite.case.law/us/475/717) (1986). This ruling lets savvy defendants create a wedge between plaintiffs and their attorneys, discouraging civil rights suits and undermining the court's logic in *Riverside*, [477 U.S. at 574-78](https://cite.case.law/us/477/561#p574). |

CiteURL is an extensible tool to process legal citations in text and generate links to sites where you can view the cited language online. By default, it supports Bluebook-style citations to the following bodies of law, among others:

- most state and federal court cases
- the U.S. Code and Code of Federal Regulations
- the U.S. Constitution and all state constitutions
- codified laws for every state and territory except Arkansas, Georgia, Guam, and Puerto Rico

If you want to try out CiteURL's citation lookup features without installing anything, you can use [LawSearch](https://raindrum.github.io/lawsearch), a JavaScript implementation of CiteURL I maintain on my website. For more information, see the [CiteURL documentation](https://raindrum.github.io/citeurl/).

## Installation

CiteURL has been tested with Python version 3.9, but earlier versions probably work. Install Python if you don't have it, then run this command:

```bash
python -m pip install citeurl
```

## Usage

CiteURL provides a command-line tool called `citeurl`. You can pass text to CiteURL by opening a file with the `-i` option, or by piping text to the program, e.g. with `cat file.html | citeurl`. By default, CiteURL uses its built-in schemas to insert hyperlinks into the text, and outputs the result to stdout. You can redirect the output to a file with the `-o` option, or open the result in a browser with `-b`. To look up a single citation instead of processing a text, use `citeurl -l <citation>`. For more options, run `citeurl -h`.

Besides the command line tool, CiteURL can be loaded as a Python library or as an extension to [Python-Markdown](https://python-markdown.github.io/). It is also possible to generate custom JavaScript implementations of CiteURL using the `citeurl-makejs` command. Additionally, Linux users with the GNOME shell can install [CiteURL as a search provider](https://github.com/raindrum/gnome-citeurl-search-provider) available directly from their desktop.

More documentation is available [here](https://raindrum.github.io/citeurl/).

## Credits

Many thanks to these websites, which CiteURL's default schemas frequently link to:

- Harvard's [Caselaw Access Project](https://cite.case.law/) - for court cases
- Cornell's [Legal Information Institute](https://www.law.cornell.edu/) - for the U.S. Code and many federal rules
- [Ballotpedia](https://ballotpedia.org) - for the vast majority of state constitutions
- [LawServer.com](https://www.lawserver.com/tools/laws) - for statutes in about a dozen states and territories whose websites don't have a compatible URL scheme