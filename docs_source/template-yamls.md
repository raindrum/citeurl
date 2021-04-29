# Writing Your Own Templates

CiteURL supports a number of citation formats out-of-the box, and I try to add more when I can. However, it will never support every possible kind of citation, and you might want to treat certain citations differently than CiteURL's built-in templates do.

Templates [can be created at runtime](../library#citeurl.Template.__init__), but it is often more practical to write a list of them in a YAML file, and load them when instantiating a [Citator](../library#citator). As such, all of [CiteURL's built-in templates](https://github.com/raindrum/citeurl/blob/main/citeurl/builtin-templates.yaml), and the templates described on this page, are in YAML format.

Before you proceed, make sure you're fairly familiar with [Python Regular Expressions](https://docs.python.org/3/howto/regex.html), because the templates rely on them heavily. You'll also need some basic knowledge of [YAML](https://www.w3schools.io/file/yaml-introduction/).

## The Basic Template Format

Here is a simplified example of a template that you might write to recognize citations to the U.S. Code:

``` yaml
United States Code:
  regex: (?P<title>\d+) USC § (?P<section>\d+)
  URL: https://www.law.cornell.edu/uscode/text/{title}/{section}
```

This citation template recognizes any series of one or more digits, followed by " USC § ", followed by another series of digits. It knows that the first string of digits is something called a "title" and the second is a "section". We will call these stored values `tokens`.

Finally, the template also has a pattern to generate a URL based on the recognized citation. It does this by replacing the placeholders (i.e. the parts in curly braces) with the values from the captured tokens. Although this template does not have any, it could also define [operations](#token-processing) to perform on the captured tokens before inserting them into the URL.

### Regex Complications

In the example above, the regex is provided as a single string. This is perfectly valid, but templates' regexes can be much more complicated than this, for two reasons:

1. A regex can be provided either as a string (as shown above), *or* as a list of strings. In the latter case, they will be concatenated (with no spaces) to create the actual regex. There is no functional difference between using strings and lists, except that providing them in list form allows you to reuse common regex parts using [YAML anchors](https://medium.com/@kinghuang/docker-compose-anchors-aliases-extensions-a1e4105d70bd).
2. Independent of the first reason, it is possible to give a template *multiple* regexes to match, by using the `regexes` key instead of `regex`. Normally, this will not be necessary, because the usual solution is to just write one regex to recognize multiple citation formats. However, regexes are limited in that capture groups cannot be rearranged.

The example template above can be rewritten to take advantage of these two features, like so:

``` yaml
United States Code
  regexes:
    - [&title '(?P<title>\d+)', ' USC ', &section '(Section|§) (?P<section>\d+)']
    - [*section, ' of Title ', *title, ' of the United States Code']
  URL: https://www.law.cornell.edu/uscode/text/{title}/{section}
```

The above template looks unwieldy, and it is; it is a list of lists. However, it provides two advantages over the first template: First, it is possible to recognize both "42 USC § 1983" and "Section 1983 of Title 42 of the United States Code," which would be impossible with a single regex, since `title` and `section` are in a different order. Second, by using YAML anchors it is possible to reuse common pieces of regex, like `*section`, which can recognize either the word "Section" or a section sign ("§"). This can make it much easier to write and maintain large libraries of templates.

### URL Complications

Another important feature is that a template's URL, like its regex(es), can be specified as a list of strings to concatenate. However, this serves a functional purpose: If a list item contains a placeholder for which no value is set, that whole list item will be omitted from the final URL. For instance, the template below can generate anchor links to subsections of the U.S. Code, but if no subsection is provided, it simply links to the overall page for the section itself:

``` yaml
United States Code
  regex: (?P<title>\d+) USC § (?P<section>\d+)( \((?P<subsection>[a-z])\)?
  URL:
    - 'https://www.law.cornell.edu/uscode/text/{title}/{section}''
    - '#{subsection}'
```

## Token Processing

In many cases, the tokens matched in a citation won't directly correspond with the values that need to be inserted into the URL placeholder. For example, your template might detect a court reporter called "F. App'x." or "Pa. D. & C.4th", but [Case.Law](https://case.law/)'s URL scheme needs those reporters to be called "[f-appx](https://cite.case.law/f-appx/)" and "[pa-d-c4th](https://cite.case.law/pa-d-c4th/)", respectively.

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
| `lookup`         | uses case-insensitive regex matching to check the token against each pattern until it fully matches, in which case it outputs the corresponding replacement string. If no pattern is matched, it causes the entire template match to retroactively fail. | `{PATTERN: REPL, PATTERN: REPL ...}` |
| `optionalLookup` | same as `lookup`, except that if the lookup fails, it simply proceeds without modifying any tokens | `{PATTERN: REPL, PATTERN: REPL ...}` |
| `lpad`           | adds zeros to the beginning of the token until it is the specified length | an integer                           |
| `numberFormat`   | assumes that the token is an integer in digit or roman numeral form, and converts it to the specified form, irrespective of which format it was originally in. The outputted roman numerals are capitalized. | `roman` or `digit`                   |

One final note: If an operation's input token has not been set (as distinct from being set to an empty string), the operation will be skipped.

## Recognizing Shortform Citations

Often, once a particular authority is cited once, subsequent references to it will take a shorter, more contextual format. For example, if a text cites *United States v. An Article Consisting of Boxes of Clacker Balls*, 413 F. Supp. 1281 (1976), then immediately cites a specific page of it, the citation might look something like "*Id*. at 1284." Later, once another authority has been cited, the same citation might be referred back to with a citation like "413 F. Supp. at 1289."

To address this, CiteURL can essentially generate new templates on the fly, whenever it detects a citation. These templates can be of two forms: `shortForms` and `idForms`. In each case, the template is only applied to text after the original long-form citation. The difference is that `shortForms` are applied to *all* of the remaining text, whereas `idForms` are only matched against the text in between one citation and the next. The [Citator.list_citations()](../library/#citeurl.Citator.list_citations) function also accepts an interruption regex, all occurrences of which will break chains of "id." citations.

Like URL templates, `idForms` and `shortForms` may contain placeholders in curly braces. These placeholders will be replaced with the corresponding token matched in the long-form citation, so that you can ensure that they only match citations where those tokens are unchanged. For instance, you could write a template to recognize court cases:

``` yaml
Caselaw Access Project (Simplified):
  regex: (?P<volume>\d+) (?P<reporter>(\D|\d(d|th|rd))+?) (?P<page>\d+)(, (?P<pincite>\d+))?
  idForms:
    - Id\. at (?P<pincite>\d+)
  shortForms:
    - {volume} {reporter} at (?P<pincite>\d+)
```

This template will recognize long-form citations like 372 U.S. 335 (optionally with a pincite citation afterwards). After that long-form citation is recognized, it will generate the regex `372 U\.S\. at (?P<pincite>\d+)`, to recognize later citations to different pincites in the same case.

To be precise, placeholders are replaced by the text *as originally matched* in the original regex capture group, before any [operations](#token-processing) are applied. This is normally the desired behavior, since operations often turn a token into something that would never be recognized. An exception applies where the placeholder refers to a token that only exists after operations are applied. In those cases, the processed token is used.

This exception is useful in a few situations. For instance, a California court opinion might reference "California Civil Code § 1946.2" once early on, but then shift to a format like "CIV § 1946.2" in later citations. This poses a problem because the new form drops reference to California, so it's too generic to be its own long-form citation, while at the same time it doesn't match the "Civil Code" token, either. But this can be solved by using a substitution to recognize "Civil Code" and, from it, generate a new token "CIV", then generating a short citation form from that:

``` yaml
California Codes:
  regex: California (?P<code>Civil Code|Penal Code) § (?P<section>\d+)
  operations:
    - token: code
      output: abbreviatedCode
      lookup: {'Civil Code':'CIV', 'Penal Code':'PEN'}
  shortForms:
    - {abbreviatedCode} § (?P<section>\d+)
    - {code} § (?P<section>\d+)
```

Using the example template above, CiteURL will be able to recognize a longform citation to "California Civil Code § 1946.2", and then recognize subsequent citations *either* to "Civil Code" sections *or* "CIV" sections.

One last note: Unlike a template's `regex`, `shortForms` and `idForms` are inherently lists, since they are designed to allow multiple alternative regexes. However, like the `regex` entry, individual list items can optionally be lists of strings, to accommodate YAML anchors. For instance, the following template is functionally identical to the Caselaw Access Project example above; the only difference is that I structured it so that I would only need to write `(?P<pincite>\d+)` once:

``` yaml
Caselaw Access Project (Simplified):
  regex:
    - '(?P<volume>\d+) (?P<reporter>(\D|\d(d|th|rd))+?) (?P<page>\d+)(, '
    - &pin '(?P<pincite>\d+)'
    - ')?'
  idForms:
    - ['Id\. at ', *pin]
  shortForms:
    - ['{volume} {reporter} at ', *pin]
```

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

BroadRegexes are used by default in the [lookup()](../library/#citeurl.Template.lookup) method, as well as in JavaScript implementations generated through the `citeurl-makejs` command.
