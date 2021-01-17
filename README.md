| Sample Input                                                 | Output                                                       |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| Federal law provides that courts should award prevailing civil rights plaintiffs reasonable attorneys fees, see 42 USC § 1988(b), and, by discretion, expert fees, see *id.* at (c). This is because the importance of civil rights litigation cannot be measured by a damages judgment. *See* *Riverside v. Rivera*, 477 U.S. 561 (1986). But *Evans v. Jeff D.*, upheld a settlement where the plaintiffs got everything they wanted, on condition that they waive attorneys fees. 475 U.S. 717 (1986). This ruling lets savvy defendants create a wedge between plaintiffs and their attorneys, discouraging civil rights suits and undermining the court's logic in *Riverside*, 477 U.S. at 574-78. | Federal law provides that courts should award prevailing civil rights plaintiffs reasonable attorneys fees, see [42 USC § 1988(b)](https://www.law.cornell.edu/uscode/text/42/1988#b), and, by discretion, expert fees, see [*id.* at (c)](https://www.law.cornell.edu/uscode/text/42/1988#c). This is because the importance of civil rights litigation cannot be measured by a damages judgment. *See* *Riverside v. Rivera*, [477 U.S. 561](https://cite.case.law/us/477/561) (1986). But *Evans v. Jeff D.*, upheld a settlement where the plaintiffs got everything they wanted, on condition that they waive attorneys fees. [475 U.S. 717](https://cite.case.law/us/475/717) (1986). This ruling lets savvy defendants create a wedge between plaintiffs and their attorneys, discouraging civil rights suits and undermining the court's logic in *Riverside*, [477 U.S. at 574-78](https://cite.case.law/us/477/561#p574). |

# CiteURL

CiteURL is a tool to recognize legal citations in text and generate hyperlinks to the cited sources. It supports short-form citations as well as direct citations to specific subsections of statutes, or individual pages of court opinions.

By default, CiteURL supports citations to U.S. court decisions, the U.S. Code and various other federal materials, plus California statutes. You can find the full list [here](https://github.com/raindrum/citeurl/blob/master/citeurl/default-schemas.yml). But you can also customize it to add support for more bodies of law by writing your own [custom YAML files](#writing-your-own-schemas).

For federal rules, regulations, and statutes, CiteURL's default set of schemas generates links to Cornell's [Legal Information Institute](https://www.law.cornell.edu/). For court cases, it uses Harvard's [Caselaw Access Project](https://cite.case.law/), though the latter will likely switch to [CourtListener](https://www.courtlistener.com/) in a future version.

## Installation

CiteURL has been tested with Python version 3.9, but earlier versions probably work. Install Python if you don't have it, then run this command:

```bash
python -m pip install citeurl
```

## Usage

CiteURL can be used as a command-line tool, a Python library, or an extension to [Python-Markdown](https://python-markdown.github.io/).

### Command Line

The simplest way to use CiteURL is via the `citeurl` command.

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

To provide a [custom set of citation schemas](#writing-your-own-schemas), use the `-s` option, followed by the path to a YAML file containing one or more schemas. You can specify the `-s` option multiple times to load multiple files.

CiteURL will use [its default schemas](https://github.com/raindrum/citeurl/blob/master/citeurl/citation-schemas.yaml) in addition to your custom ones, unless you disable defaults with the `-n` option.

### Markdown Extension

In addition to a command-line tool, CiteURL can be used as an [Python-Markdown](https://python-markdown.github.io/) extension. The extension can simply be loaded as `citeurl`, and it supports the following options:

- `custom_schemas`: A list of paths to YAML files containing custom citation schemas. Defaults to none.

- `use_defaults`: A boolean representing whether CiteURL should load the [default schemas](https://github.com/raindrum/citeurl/blob/master/citeurl/default-schemas.yaml). Defaults to True.

- `css_class`: A string representing the class that inserted \<a> elements should have. Defaults to "citation".

Note that this extension will slow down Python-Markdown quite a bit, since it requires processing a long list of complicated regexes.

### Python Library

The Citator object contains all of CiteURL's main functionality. It contains all of the schemas for supported bodies of law, as well as tools to match them against text. You'll need to create one before doing much else.

```python
from citeurl import Citator
citator = Citator()
```

If you want to load your own custom YAML files full of schemas, you can pass them as arguments when creating the citator, or you can load them after-the fact. If you don't want to use CiteURL's default schemas, set `defaults=False`.

```python
citator = Citator('path/to/your/schemas.YAML', defaults=False)

citator.load_yaml('even/more/schemas.YAML')
```

#### Insert links into text

To process a block of text with the citator and insert legal citations, you can use its `insert_links()` function:

```python
input_text = "42 USC 1983 and NLRA § 8(b)(4) are both available on the Cornell website."
output_text = citator.insert_links(input_text, css_class='statute')
print(output_text)
# <a href="https://www.law.cornell.edu/uscode/text/42/1983" class="statute">42 USC 1983</a> and <a href="https://www.law.cornell.edu/uscode/text/29/158#b_4" class="statute">NLRA § 8(b)(4)</a> are both available on the Cornell website.
```

#### List all citations in a block of text

```python
cites = citator.list_citations(text_of_court_opinion):
# or, to only scan between indices 56 and 123 in the text:
cites = citator.list_citations(text, span=(56, 123))
```

#### Look up a single citation

The citator and each schema within it each have a lookup() class designed to efficiently look up a single citation. It will return the first citation it finds, or None if it can't find any.

```python
cite = citator.lookup('42 USC 1983')
print(cite.schema)
# United States Code
```

By default, this uses more permissive regex matching than is used when processing text. Namely, it uses case-insensitive matching, and if a schema has a `broadRegex` key defined, it will be used instead of the default regex. You can disable this feature by using `lookup(query, broad=False)`

#### Get detailed info about a citation

```python
# to look up a single citation (case-insensitively and using broader regex if available):
citation = citator.lookup('Kinsman Transit Company, 338 F.2d 708, 715 (1964)')
print(citation) # 338 F.2d 708, 715
print(citation.tokens) # {'volume': '338', 'reporter': 'f2d', 'page': '708', 'pincite': '715'}
print(citation.URL) # https://cite.case.law/f2d/338/708#p715
print(citation.schema) # Caselaw Access Project
print(citation.match) # <re.Match object; span=(25, 42), match='338 F.2d 708, 715'>
```

### GNOME Shell Search

If you use the [GNOME](https://www.gnome.org/) desktop, you can also install a [CiteURL search provider](https://github.com/raindrum/gnome-citeurl-search-provider)!

## Writing Your Own Schemas

CiteURL works based on a list of "citation schemas" that define how it should recognize each body of law, and how to generate URLs from the text.

The program comes with a number of schemas built in, which can recognize U.S. court cases and federal statutes, as well as some other bodies of law. However, it's also designed to be easily extended. With a little regex knowledge, you can create your own YAML file full of schemas, and use it to supplement (or replace) the default list.

Here's an example of a simple schema:

```yaml
- name: Federal Register
  regex: (?P<volume>\d+) (Fed\. ?Reg\.|F\.? ?R\.?) (?P<page>\d+)
  URL: https://www.federalregister.gov/documents/search?conditions[term]={volume}+FR+{page}
```

As the name suggests, this schema lets the program recognize citations to the Federal Register, and generate a link to view the relevant document online. It works like this:

1. First, it constructs a [regular expression](https://www.w3schools.com/python/python_regex.asp) from the text in the `regex` key, and checks whether a given piece of text matches that regular expression.
2. If the text matches the regex, the tokens in the named capture groups (here, the parts named `volume` and `page`).
3. Finally, the program creates a URL from the schema's URL template by replacing every part in {curly braces} with the contents of the capture group of the same name.

Every schema must contain a `name`, `regex`, and a `URL` key, but they can also contain other keys, such as those that manipulate the values of regex capture groups before they are inserted into the URL.

You can find examples of more complicated schemas by looking through [CiteURL's built-in schemas file](https://github.com/raindrum/citeurl/blob/master/citeurl/default-schemas.yaml). Custom YAMLs follow the same format. For more information on the specific pieces of a schema, see below.

### regex

A string representing the [Python Regular Expression](https://www.w3schools.com/python/python_regex.asp) to match a given body of law. The regex detects whether a given piece of text is a citation, and it simultaneously identifies the parts of the citation ("tokens") that the program needs in order to construct a URL.

A schema's regex can be specified either as a single string, or as a list of strings. In the latter case, the strings will be concatenated into a single string, without any separator.

```yaml
# In other words, this:
regex:
  - (?P<title>)
  - ' U\.? ?S\.? ?C\.? ? '
  - (?P<section>)

# is functionally equivalent to this:
regex: (?P<title>) U\.? ?S\.? ?C\.? ? (?P<section>)
```

The advantage of specifying regexes in list form is that it allows you to reuse pieces of a regex across multiple schemas in the same YAML file, using [YAML anchors](https://medium.com/@kinghuang/docker-compose-anchors-aliases-extensions-a1e4105d70bd). For an example of this, see the many uses of the `*section` anchor in CiteURL's built-in schemas.

Some other things to know about CiteURL's regexes:

- The generated regex will be case-sensitive when processing a block of text, but case-insensitive when looking up a single citation. This is meant to allow for a flexible syntax when using CiteURL as a quick lookup tool, while avoiding false-positives when using it to detect citations in a longer text.
- Because of a limitation of the YAML format, no regex may contain a colon directly followed by a space (": "). Fortunately it's usually possible to write around this.

### URL

This is a template for the URL that the program generates from a recognized citation. Any section in {curly braces} is treated as a placeholder that must be replaced with the relevant value.

Like regexes, URL templates can be specified either as a single string, or as a list of strings to concatenate. If one of the strings in the list contains a placeholder for which no value is set, that whole string will be omitted from the generated URL. That's useful for making URL templates that include parts of a citation that may or may not be present, like this:

```yaml
URL:
  - https://www.law.cornell.edu/uscode/text/{title}/{section}
  - '#{subsection}'
```

This lets the program construct a URL that may or may not include an anchor link to a specific subsection. If a `subsection` value is set, it will be used. Otherwise, the whole line, including the "#", will be omitted.

Note that the second line of the URL is in quotes. The YAML parser can usually infer that text is text, even without quotes. Quotes are only necessary when the text begins with a special character like "#", as here, or where it begins or ends with whitespace.

### defaults

This is a dictionary of tokens that should be set to default values, when the corresponding capture group is not set by the regex. The format looks like this:

```yaml
# When setting only one default value, it's convenient to use a one-liner:
defaults: {'title': '29'}

# But when setting multiple defaults, multiple lines looks nicer:
defaults:
  title: '29'
  section: '101'
```

Default values are set before mutations and substitutions, and so can be processed by those operators. They essentially work just like if the given value had been set by the regex.

### mutations

This optional key contains a list of 'mutations' to manipulate the value of a capture group before inserting it into the URL.

Each mutation must specify a `token` that it operates on. This should be identical to the name of the relevant regex capture group.

In addition, a mutation can have any combination of the following 

- `case`: forces the string to the specified case, either "upper" or "lower"
- `omit`: a string (parsed as regex), all instance of which will be omitted from the output
- `splitter`: a string (parsed as regex), all instances of which will split the output. Must be paired with `joiner`.
- `joiner`: a string that will be inserted between parts split with `splitter`

Here's an example of a simple mutation and a more complex one:

```yaml
mutations:
  - token: quote
    case: upper
  - token: reporter
    case: lower
    omit: "[.()&,']"
    splitter: ' '
    joiner: '+'
```

In this example, the `quote` capture group, if present, will simply be converted to uppercase.

Meanwhile, the `reporter` group will be converted to lowercase. Periods, parentheses, ampersands, commas, and single-quotes will be removed. And each space (or series of spaces) will be replaced by a plus sign..

### substitutions

This optional key is meant for string operations that involve setting a capture group to an arbitrary value, based on looking up a value in an index.

This is useful for redirecting from sections of a statute to the corresponding U.S. Code section. See this example from the default National Labor Relations Act schema:

```yaml
substitutions:
  - inputToken: section
    index: {'1':'151', '2':'152', '3':'153', '4':'154', '5':'155', '6':'156', '7':'157', '8':'158', '9':'159', '10':'160', '11':'161', '12':'162', '13':'163', '14':'164', '15':'165', '16':'166', '17':'167', '18':'168', '19':'169'}
```

This substitution takes the value of the `section` group from the regex as its input. If that value is '1', '2', or any of the other values in the `index` dictionary, the `section` token will be set to the corresponding from `index`. Alternatively, if you specify an `outputToken`, it will be modified instead, leaving the input `token` unchanged.

If the value of `section` is outside the index, the schema match will fail as if the initial regex was never matched. You can prevent this behavior by adding `allowUnmatched: true` to the substitution, in which case failed substitutions will simply have no effect.

To look up values using regex citation matching instead of a normal dictionary lookup, add `useRegex: true` to the substitution.

### broadRegex

`broadRegex` is an optional alternative `regex` key. It is meant to let you define a more permissive regex that's  useful for individual citation lookups, but which would create  false-positives when processing longer text.

If present, `broadRegex` will be used instead of `regex` when the program tries to look up a single citation.

Its syntax is identical to the `regex` key.

### shortForms and idForms

When a schema finds a citation in the text, it will generate child schemas to recognize short forms of that same citation. These short citation forms come in two kinds:

- `idForms`  represent citations like "*id.*" or "*id. at 403*", which are only intelligible until the next (different) citation in the text.
- `shortForms` are citations like "372 U.S. at 361", which can be recognized anywhere in the text following their parent citation.

The `idForms` and `shortForms` keys should contain *lists of regular expression templates*. Each template works like the `regex` key (i.e. it can be specified as a string or a list of strings).

However, short citation forms have an additional feature that base regexes do not: They may contain placeholders in {curly braces}, and these placeholders will be replaced by the values from the original schema match.

```yaml
regex: (?P<volume>\d+) (?P<reporter>.{2,15}?) (?P<page>\d+)
shortForms:
  - {volume} {reporter} at (?P<pincite>\d+)
idForms:
  - [Ii]d\. at (?P<pincite>\d+)
  - [Ii]d\.
```

In the example above, when the base schema recognizes the citation "372 U.S. 335", it will generate a short form that matches *only* "372 U.S. at (?P<pincite\d+)", while remembering the `page` token from the parent citation.

`idForms` work the same way, except that they are only active until the next different citation.