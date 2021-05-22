# Writing Your Own Templates

CiteURL supports a number of citation formats out-of-the box, and I try to add more when I can. However, it can never support every possible kind of citation, especially for local laws and countries outside the United States. For that reason, CiteURL is designed to let you write your own citation templates in YAML format.

This page details how to write these template files. Before you proceed, make sure you're at least a little familiar with [Python regex](https://docs.python.org/3/howto/regex.html), because the templates rely heavily on it. You'll also need some basic knowledge of [YAML](https://www.w3schools.io/file/yaml-introduction/).

**Note**: [CiteURL's built-in templates](https://github.com/raindrum/citeurl/blob/main/citeurl/builtin-templates.yaml) are written in the same YAML format described on this page, so they can serve as a reference when you're writing your own.

## The Basic Template Format

Here is a simplified example of a template that you might write to recognize citations to the U.S. Code:

``` yaml
United States Code:
  regex: (?P<title>\d+) USC § (?P<section>\d+)
  URL: https://www.law.cornell.edu/uscode/text/{title}/{section}
```

Because of what's in the 'regex' key, this citation template recognizes any series of one or more digits, followed by " USC § ," followed by another series of digits. It knows that the first string of digits is something called a "title" and the second is a "section." We will call these stored values "tokens."

Any tokens that are captured in the regex can be used to fill placeholders (identified by curly braces) in the URL template, as shown above.

**Note** that although this example inserts tokens into the URL unmodified, it is also possible to process the tokens first using one or more [operations](#token-processing). Also note that this template only recognizes full, long-form citations to the U.S. Code, but you can add additional information to help it [recognize shortform citations](#recognizing-shortform-citations) that follow the original citation.

But before we get into that, it's important to know a bit more about how the regex and URL fields work:

### Regex Complications

In the example above, the template recognizes only one regex, and that regex is provided as a single string. This is perfectly valid, but CiteURL templates also allow for more complex regex definitions.

First, it's possible to provide a regex as a list rather than a single strings, so that the actual regex will be composed of each list entry combined together. string, like so:

```yaml
United States Code:
  regex:
    - &title '(?P<title>\d+)'
    - ' USC '
    - &section '§ (?P<section>\d+)'
  URL: https://www.law.cornell.edu/uscode/text/{title}/{section}
```

Functionally, this template works exactly like the last one. However, because the regex was broken up into a list of components, it was possible to define the `title` and `section` components as [YAML anchors](https://medium.com/@kinghuang/docker-compose-anchors-aliases-extensions-a1e4105d70bd) that can be reused later, by writing `*title` or `*section`, respectively. When writing a large number of templates, this can save a lot of time, as well as make them easier to maintain.

The second regex complication to know about is that it is possible to give a template *more than one* regex, such that the template will recognize a citation that matches any of its alternate regexes. Note that it is usually preferable to write a more flexible *single* regex. However, in some cases this is impossible due to regex limitations, such as the fact that named capture groups must appear in a fixed order.

To provide multiple regexes, replace the "regex" key with "regexes," as shown here:

```yaml
United States Code:
  regexes:
    - '(?P<title>\d+) USC § (?P<section>\d+)'
    - 'section (?P<section>\d+) of title (?P<title>\d+) of the U\.S\. Code'
  URL: https://www.law.cornell.edu/uscode/text/{title}/{section}
```

This template uses multiple regexes to make it possible to recognize U.S. Code citations no matter whether the title is specified before the section, or vice versa.

It's important to remember the difference between using multiple regexes and defining one regex in list form. In fact, it is possible to do both at once:

``` yaml
United States Code:
  regexes:
    - [&title '(?P<title>\d+)', ' USC ', &section '§ (?P<section>\d+)']
    - [*section, ' of Title ', *title, ' of the United States Code']
  URL: https://www.law.cornell.edu/uscode/text/{title}/{section}
```

This is functionally equivalent to the previous example, but because the individual regexes are provided in list form, it is possible to reuse the "title" and "section" pieces via YAML anchors, rather than write them twice.

### URL Complications

Another important feature is that a template's URL, like its regex(es), can be specified as a list of strings to concatenate. Unlike with regexes, splitting a URL into a list of strings makes it behave differently. Specifically, If a section of the URL contains a placeholder for which no value is set, that whole list item will be omitted from the final URL. For instance, the template below can generate links to specific subsections of the U.S. Code, but if no subsection is specified, it simply links to the overall page for the section itself:

``` yaml
United States Code:
  regex: (?P<title>\d+) USC § (?P<section>\d+)( \((?P<subsection>[a-z])\)?
  URL:
    - 'https://www.law.cornell.edu/uscode/text/{title}/{section}'
    - '#{subsection}'
```

## Token Processing

In many cases, the tokens matched in a citation won't directly correspond with the values that need to be inserted into the URL placeholder. For example, your template might detect a court reporter called "F. App'x." or "Pa. D. & C.4th", but [Case.Law](https://case.law/)'s URL scheme needs those reporters to be called "[f-appx](https://cite.case.law/f-appx/)" and "[pa-d-c4th](https://cite.case.law/pa-d-c4th/)," respectively.

To solve this problem, CiteURL templates can specify `operations` that will be performed on the dictionary of matched tokens to turn them into a new dictionary (i.e. `processed_tokens`) before using it to populate the URL.

This example template solves the problem by converting the `reporter` token to lowercase, deleting some common special characters from it, and then replacing spaces with dashes:

``` yaml
Caselaw Access Project (Simplified):
  regex: (?P<volume>\d+) (?P<reporter>(\D|\d(d|th|rd))+?) (?P<page>\d+)
  operations:
    - token: reporter
      case: lower
    - token: reporter
      sub: ["[.()&,']", '']
    - token: reporter
      sub: [' ', '-']
  URL: https://cite.case.law/{reporter}/{volume}/{page}
```

As shown above, a template's `operations` value is a list of operations that will be performed in sequence. Each operation is a dictionary that must specify a `token` to process, and the kind of operation to perform. Operations process a token in place by default, but if an `output` is specified, that token will be set or modified instead.

The above example shows two kinds of operation: case modification (`case`), and regex substitution (`sub`), but CiteURL supports others as well:

| Operation        | Description                                                  | Required Contents                    |
| ---------------- | ------------------------------------------------------------ | ------------------------------------ |
| `case`           | sets the input token to the specified capitalization         | `upper`, `lower`, or `title`         |
| `sub`            | replaces all instances of the provided regex pattern with the replacement string | `[PATTERN, REPL]`                    |
| `lookup`         | uses case-insensitive regex matching to check the token against each pattern until it fully matches one of them, in which case it outputs the corresponding replacement string. If no pattern is matched, it causes the entire template match to retroactively fail, as if there had never been a regex match in the first place. | `{PATTERN: REPL, PATTERN: REPL ...}` |
| `optionalLookup` | same as `lookup`, except that if the lookup fails, it simply proceeds without modifying any tokens | `{PATTERN: REPL, PATTERN: REPL ...}` |
| `lpad`           | adds zeros to the beginning of the token until it is the specified length | an integer                           |
| `numberFormat`   | assumes that the token is an integer in digit or roman numeral form, and converts it to the specified form, irrespective of which format it was originally in. The outputted roman numerals are capitalized. | `roman` or `digit`                   |

One final note: If an operation's input token has not been set (as distinct from being set to an empty string), the operation will be skipped.

## Recognizing Shortform Citations

Often, once a particular authority is cited once, subsequent references to it will take a shorter, more contextual format. CiteURL templates can account for these kinds of citations using the `shortForms` and `idForms` keys.

 Consider the following template:

```yaml
Federal Supplement:
  regex: '(?P<volume>\d+) F\. Supp\. (?P<page>\d+)(, (?P<pincite>\d+))?'
  idForms:
    - 'Id\. at (?P<pincite>\d+)'
  shortForms:
    - '{volume} F\. Supp\. at (?P<pincite>\d+)'
  URL:
    - 'https://cite.case.law/f-supp/{title}/{page}'
    - '#p{pincite}'
```

If a text cites *United States v. An Article Consisting of Boxes of Clacker Balls*, 413 F. Supp. 1281 (E.D. Wis. 1976), it CiteURL will recognize it as a full citation because it matches the regex for the Federal Supplement citation template.

When this occurs, it will dynamically generate a `shortForm` template to recognize citations like "413 F. Supp. at 1289" anywhere in the following text. It will also generate an `idForm` template that will recognize citations like "*Id.* at 1284," but which will be deactivated as soon as the text references a different authority.

The `idForms` and `shortForms` keys are like the `regexes` key in that they contain a list of regexes, and each regex may be given as a string or a list of strings. However, they differ from normal regexes in that, like the `URL` key, they may contain placeholders in curly braces, which will be filled in with the relevant tokens found in the longform citation.

Note that while the `URL` key uses the tokens after they have been [processed](#token-processing), the placeholders here use the values exactly as captured in the regex, *unless* the placeholder references a token that only exists after processing.

## Miscellaneous Keys

### defaults

`defaults` is a dictionary of tokens whose values will be set to specified values, if they are not set by a named capture group in the matched regex. Defaults are applied prior to any [operations](#token-processing).

For instance, the template below will match citations like "29 USC § 157" as well as citations like "§ 1983", but in the latter case, it assumes that the title is '42' by default.

``` yaml
U.S. Code, but especially Title 42:
  regex: ((?P<title>\d+) USC )?§ (?P<section>\d+)
  defaults: {'title': '42'}
```

### broadRegex

`broadRegex` and `broadRegexes` are identical in format to the `regex` and `regexes` keys. They allow you to specify extra regexes that will be used, in addition to the normal regex(es), in contexts like search engines where user convenience is more important than avoiding false positives. 

BroadRegexes are used by default in the [lookup()](../library/#citeurl.Template.lookup) method, as well as in [JavaScript implementations](../frontends#javascript), though if you are writing templates *exclusively* for these use cases rather than text processing, it is not important whether you use `regexes` or `broadRegexes`.