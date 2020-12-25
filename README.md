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

```python
#########################################
# Setup
#########################################
from citeurl import Schema_Set

# You can initialize the default set of citation schemas like this:
schemas = Schema_Set()

# Or initialize the default schemas along with your own custom set:
combined_schemas = Schema_Set('path/to/your/schemas.yaml')

# Or if you don't want the default schemas, you can prevent loading them:
my_schemas = Schema_Set('path/to/your/schemas.yaml', defaults=False)

# You can load as many sets of schemas as you want!
many_schemas = Schema_Set('set1.yaml', 'set2.yaml', 'set3.yaml', 'etcetera.yaml')


#########################################
# Usage
#########################################

url = schemas.lookup_query('Kinsman Transit Company, 338 F.2d 708, 715 (1964)')
print(url)
# https://cite.case.law/f2d/338/708#p715

input_text = "42 USC 1983 and NLRA § 8(b)(4) are both available on the Cornell website."
output_text = schemas.insert_links(input_text, css_class='statute')
print(output_text)
# <a href="https://www.law.cornell.edu/uscode/text/42/1983" class="statute">42 USC 1983</a> and <a href="https://www.law.cornell.edu/uscode/text/29/158#b_4" class="statute">NLRA § 8(b)(4)</a> are both available on the Cornell website.
```

## Writing Your Own Schemas

CiteURL works based on a list of "citation schemas" that define how it should recognize each body of law, and how to generate URLs from the text. The program comes with a number of schemas built in, which can recognize U.S. court cases and federal statutes, as well as some other bodies of law. However, it's also designed to be easily extended. You can create your own YAML file full of schemas, and use it to supplement (or replace) the default list.

For an idea of the general format of these files, look at [CiteURL's default set of schemas](https://github.com/raindrum/citeurl/blob/master/citeurl/default-schemas.yaml).

Every schema must have the following keys:

- `regexParts`: a list of strings that will be concatenated and then compiled into a regular expression used to recognize the schema. Values from named capture groups are inserted into URLParts.

	The generated regex will be case-sensitive when processing a block of text, but case-insensitive when looking up a single citation.

	The regex is defined in parts in the YAML, rather than as a single string, because this makes it possible to reuse frequently-recurring parts (like the various formats of a section sign) via YAML anchors.

- `URLParts`: a list of strings that will be concatenated to generate the URL. Any text in {curly braces} is a placeholder to be replaced by the corresponding value set by a regex capture group, default, or substitution.

	If a URLPart contains a placeholder for which there is no set value, the entire URLPart will be omitted from the generated URL, without error. This is useful to make URL hashes out of optional regex capture groups, because the hash will be omitted if the capture group is not set.

In addition to those keys, a schema may also have any combination of the following:

- `defaults`: a dictionary of placeholder names, with values they should default to if the corresponding key is not otherwise set.

	Defaults are applied prior to mutations and substitutions, so their values are available to those functions.

- `mutations`: a list of string operations (besides substitution) that will be performed on placeholder values before they are inserted into the URL.

	Each mutation must have a "key" matching the name of the regex capture group it processes. Each mutation may additionally have any combination of the following:

	- `case`: forces the string to the specified case, either "upper" or "lower"

	- `omit`: a string (parsed as regex), all instance of which will be omitted from the output

	- `splitter`: a string (parsed as regex), all instances of which will split the output. Must be paired with `joiner`.

	- `joiner`: a string that will be inserted between parts split with `splitter`

	Mutations are applied before substitutions, so they can be used to normalize input for them.

- `substitutions`: a list of string operations that involve setting a key to an arbitrary value based on looking up a value in an index. This is useful for redirecting from sections of a statute to the corresponding U.S. Code sections. Substitutions may contain the following:

	- `inputKey`: the key whose value will be looked up in the index. If no outputKey is specified, this is also the key whose value will be set based on the lookup.

	- `outputKey`: if this is specified, its value will be set based on the lookup, instead of modifying the inputKey. This is useful where, for instance, certain sections of a statute are codified under different U.S. code titles than others. In that situation, you could define a substitution to set the title based on the input section number, and then a separate substitution to set the output section number.

	- `index`: a dictionary listing the output value associated with each inputKey value

	- `allowUnmatched`: a boolean indicating that a URL should be generated even if the inputKey is not in the index. Defaults to false. If set to true, then failed lookups will have no effect, leaving all keys unmodified. 