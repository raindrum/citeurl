# CiteURL

CiteURL is a tool to detect legal citations in text, and generate relevant hyperlinks. It can be used as a command-line tool, a library, or as an extension to [Python-Markdown](https://python-markdown.github.io/).

By default, CiteURL generates links to federal laws, rules, and regulations on [the Cornell website](https://www.law.cornell.edu), and citations to court opinions are linked to Harvard's [Caselaw Access Project](https://lil.law.harvard.edu/projects/caselaw-access-project/), though this will likely switch to [CourtListener](https://www.courtlistener.com/) in the future. The full list of bodies of law that CiteURL recognizes is available [here](https://github.com/raindrum/citeurl/blob/master/citeurl/default-schemas.yml).

However, the program is also designed to be easily extended through [custom YAML files](#writing-your-own-schemas).

## Installation

CiteURL has been tested with Python version 3.9, but earlier versions probably work. Install Python if you don't have it, then run this command:

```bash
pip install citeurl
```

## Usage

### Command Line

You can use CiteURL via the `citeurl` command.

- To create a hyperlink for each citation in input.html, and save the result as output.html, use a command like this:
	```bash
	citeurl -i input.html -o output.html
	```

	Alternatively, on many operating systems you can pipe the output of another command into CiteURL. For instance:
	```bash
	cat input.html | citeurl -o output.html
	```

- To return the URL for a single citation instead of processing a block of text, use the `-l` option. For instance, the following command will print [this URL](https://www.law.cornell.edu/uscode/text/42/1983) in your terminal:
	```bash
	citeurl -l "42 USC 1983"
	```

- To provide a [custom set of citation schemas](#writing-your-own-schemas), use the `-s` option, followed by the path to a YAML file containing one or more schemas. You can specify the `-s` option multiple times to load multiple files.

	CiteURL will use [its default schemas](https://github.com/raindrum/citeurl/blob/master/citeurl/citation-schemas.yaml) in addition to your custom ones, unless you disable defaults with the `-n` option.

### Markdown Extension

In addition to a command-line tool, CiteURL is also an extension to [Python-Markdown](https://python-markdown.github.io/). The extension can simply be loaded as `citeurl`, and it supports the following options:

- `custom_schemas`: A list of paths to YAML files containing custom citation schemas. Defaults to none.

- `use_defaults`: A boolean representing whether CiteURL should load the [default schemas](https://github.com/raindrum/citeurl/blob/master/citeurl/default-schemas.yaml). Defaults to True.

- `css_class`: A string representing the class that inserted \<a> elements should have. Defaults to "citation".

Note that this extension will slow down Python-Markdown quite a bit, since it requires processing a long list of complicated regexes.

### Python Library

First, you'll need to load the library:

```python
from citeurl import Schema_Set
```

Next, create the set of citation schemas that will be used:

```python
# To simply load the built-in set of schemas, use this:
Schema_Set = Schema_Set()

# Or, to load a custom YAML in addition to the built-in schemas:
Schema_Set = Schema_Set('path/to/your/schemas.YAML')

# Or, to load three YAML files *instead* of the built-in schemas:
Schema_Set = Schema_Set('1.YAML', '2.YAML', '3.YAML', defaults=False)

# You can also load additional YAML files after-the-fact:
Schema_Set.load_yaml('path/to/more/schemas.YAML')
```

Now you can apply the schemas to text!

```python
# to look up a single citation (case-insensitively and using broader regex if available):
url = Schema_Set.lookup_query('Kinsman Transit Company, 338 F.2d 708, 715 (1964)')
# https://cite.case.law/f2d/338/708#p715

# or, to process a longer text with multiple citations, inserting a link or each:
input_text = "42 USC 1983 and NLRA § 8(b)(4) are both available on the Cornell website."
output_text = Schema_Set.insert_links(input_text, css_class='statute')
# <a href="https://www.law.cornell.edu/uscode/text/42/1983" class="statute">42 USC 1983</a> and <a href="https://www.law.cornell.edu/uscode/text/29/158#b_4" class="statute">NLRA § 8(b)(4)</a> are both available on the Cornell website.
```

The above examples should cover most use-cases. However, if your application need information about individual schemas, you can also match text schema-by-schema:

```python
for schema in self.Schema_Set.schemas:
    # to look up an indiviudal URL
    url = schema.url_from_query()
    if url:
        print('Matched schema: ' + schema.name)
    
    # or to insert links into a text:
    schema.insert_links(text, css_class: schema.name)
    
```



## Writing Your Own Schemas

CiteURL works based on a list of "citation schemas" that define how it should recognize each body of law, and how to generate URLs from the text.

The program comes with a number of schemas built in, which can recognize U.S. court cases and federal statutes, as well as some other bodies of law. However, it's also designed to be easily extended. You can create your own YAML file full of schemas, and use it to supplement (or replace) the default list.

Here's an example of a simple schema:

```yaml
- name: Federal Register
  regex: (?P<volume>\d+) (Fed\. ?Reg\.|F\.? ?R\.?) (?P<page>\d+)
  URL: https://www.federalregister.gov/documents/search?conditions[term]={volume}+FR+{page}
```

As the name suggests, this schema lets the program recognize citations to the Federal Register, and generate a link to view the relevant document online. It works like this:

1. First, it constructs a [regular expression](https://www.w3schools.com/python/python_regex.asp) from the text in the `regex` key, and checks whether a given piece of text matches that regular expression.
2. If the text matches the regex, the values in the named capture groups (here, the parts named `volume` and `page`) are pulled out for processing.
3. Finally, the program creates a URL from the schema's URL template by replacing every part in {curly braces} with the contents of the capture group of the same name.

Every schema must contain a `name`, `regex`, and a `URL` key, but they can also contain other keys, such as those that manipulate the values of regex capture groups before they are inserted into the URL.

You can find examples of more complicated schemas by looking through [CiteURL's built-in schemas file](https://github.com/raindrum/citeurl/blob/master/citeurl/default-schemas.yaml). Custom YAMLs can follow this format. For more information on the specific pieces of a schema, see below.

## Schema Components

### regex

A string representing the [Python Regular Expression](https://www.w3schools.com/python/python_regex.asp) to match a given body of law. The regex detects whether a given piece of text is a citation, and it simultaneously identifies the parts of the citation that the program needs in order to construct a URL.

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

### broadRegex

`broadRegex` is an optional alternative `regex` key. It is meant to let you define a more permissive regex that's useful for individual citation lookups, but which would create false-positives when processing longer text.

If present, `broadRegex` will be used instead of `regex` when the program tries to look up a single citation.

Its syntax is identical to the `regex` key.

### defaults

This is a dictionary representing placeholders that should be set to default values when the corresponding capture group is not set by the regex. The format looks like this:

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

Each mutation must specify a `key` that it operates on. This should be the name of the capture group.

In addition, a mutation can have any combination of the following 

- `case`: forces the string to the specified case, either "upper" or "lower"
- `omit`: a string (parsed as regex), all instance of which will be omitted from the output
- `splitter`: a string (parsed as regex), all instances of which will split the output. Must be paired with `joiner`.
- `joiner`: a string that will be inserted between parts split with `splitter`

Also note that mutations are applied before substitutions, so they can be used to normalize input.

Here's an example of a simple mutation and a more complex one:

```yaml
mutations:
  - key: quote
    case: upper
  - key: reporter
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
  - inputKey: section
    index: {'1':'151', '2':'152', '3':'153', '4':'154', '5':'155', '6':'156', '7':'157', '8':'158', '9':'159', '10':'160', '11':'161', '12':'162', '13':'163', '14':'164', '15':'165', '16':'166', '17':'167', '18':'168', '19':'169'}
```

This substitution takes the value of the `section` group from the regex as its input. If that value is '1', '2', or any of the other values in the `index` dictionary, the `section` group will be set to the corresponding from `index`. Alternatively, if you specify an `outputKey`, it will be modified instead of the `inputKey`.

If the value of `section` is outside the index, the schema match will fail as if the initial regex was never matched. You can prevent this behavior by adding `allowUnmatched: true` to the substitution, in which case failed substitutions will simply have no effect.