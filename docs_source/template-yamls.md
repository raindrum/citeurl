# Writing Your Own Templates

CiteURL has built-in templates to support most of the major sources of U.S. state and federal law, but that's still a very small fraction of the universe of references a document might contain. Municipal ordinances, other countries' laws, and most subject-specific materials are simply outside the scope of what CiteURL's built-in templates can reasonably cover.

This page details how you can write your own citation templates to supplement or replace the built-in ones. Before you proceed, make sure you're a little familiar with [regular expressions](https://en.wikipedia.org/wiki/Regular_expression) (regex), because a citation template is essentially a bunch of them glued together. You'll also need some basic knowledge of [YAML](https://www.w3schools.io/file/yaml-introduction/), because that's the glue.

**Note**: CiteURL's [built-in templates](https://github.com/raindrum/citeurl/blob/main/citeurl/templates) are all written in the same format described on this page, so they're a helpful resource to learn and copy from when writing your own.

## Introduction

Essentially, a citation template does three things. First, it recognizes whether a given bit of text is a valid citation. Second, it extracts the relevant data from the citation, like the page or section numbers it references. Third, the template defines how to do useful things with that data, like turn it into a URL. Here's a simple template that does all of those things:

```yaml
U.S. Code:
  tokens:
    title:
      regex: \d+
    section:
      regex: \d+[A-Z]?
  pattern: '{title} U\.?S\.?C\.? ?§? {section}'
  URL builder:
    parts:
      - 'https://www.law.cornell.edu/uscode/text/{title}/{section}'
  name builder:
    parts:
      - '{title} U.S.C. § {section}'
```

First, the template defines two `tokens` that a U.S. code citation can contain. The first is something called "title", and the second is "section". The fact that title is listed before section in the tokens list is important; it indicates that titles contain sections.

Each token has its own `regex` that defines what inputs are valid for that part of the citation. Here, titles are just one or more digits, i.e. `\d+`, whereas section numbers can optionally have a single capital letter afterwards.

Next, the template provides a `pattern` for what citations need to look like. The pattern is a regular expression, except that any tokens listed in curly braces are replaced by a regex capture group matching the relevant regex. So, when CiteURL actually runs, the pattern is used to generate this regex:

```
(?P<title>\d+) U\.?S\.?C\.? §? ?(?P<section>\d+[A-Z]?)
```

That regex lets the template know that "42 U.S.C. § 1988" is a reference to section 1988 of Title 42 of the U.S. Code, and so are a few similar-looking things like "42 USC 1988".

Either way, "42" and "1988" will be stored as tokens and can be inserted into the `URL builder` to make [this link](https://www.law.cornell.edu/uscode/text/42/1988). The `name builder` works the same way. Regardless of any formatting differences in the text that was matched, the it lets CiteURL display that citation as "42 U.S.C. § 1988."

Now that you've got the basic concept, let's go over the parts in more detail.

## Tokens

Tokens are the discrete pieces of information found in a citation. They can represent anything from a page number to a named chapter of law. Each token must have a `regex` indicating what text is valid input for that token, and it may also have a list of [edits](#edits) used to process and normalize the token text as soon as it is matched.

Sometimes, like in the U.S. Code example above, it's as simple as storing whatever text is found in a particular part of the citation. No edits were needed, because "1988" would only be written in one specific way. Other times, however, it is necessary to perform various string processing operations to normalize the data. Consider the following example:

```yaml
U.S. Constitution:
  ...
  tokens:
    article:
      regex: [1-7]|[IV]{1,3}|One|Two|Three|Four|Five|Six|Seven
      edits:
        - number style: digit
  ...
```

Here, the `regex` can recognize a number between one and seven, no matter whether it is given as a digit, a Roman numeral, or a word. But it would not be useful to store this value without normalization---it is important that "3", "III", and "Three" are all treated as equivalent. To accomplish this, the template uses a `number style` edit to coerce the number into digit format. As a result, no matter whether the template matched "Article III", "Article 3", or "Article Three", the resulting citation will have an article value of "3".

### Edits

Edits are simple predefined string operations that can be performed on tokens. They are useful in two contexts. First, as described above, they can be included in the token definition in order to normalize its input. Second, they can be used in [string builders](#string-builders) in order to temporarily-modify tokens for the sole purpose of building the string. In either case, the following edits are available:

| Edit            | Description                                                  | Example                                                      |
| --------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| `case`          | Convert the given token to the specified capitalization, either `upper`, `lower`, or `title`. In the latter case, only the first letter of every word is capitalized. | `case: upper`                                                |
| `sub`           | Perform a regex substitution on the token, replacing each occurrences of the first listed string (treated as a regex) with the second listed string. | `sub: ['\W+', '-']`                                          |
| `lpad`          | Add zeroes to the left side of the token as necessary until it is the specified length. | `lpad: 3`                                                    |
| `lookup`*       | Use case-insensitive regex matching to check whether the token matches any of the keys in the given dictionary. If the token matches a key, it will be replaced with the associated value. | `lookup: {'[Pp]attern': 'replacement', '[Pp]otato': 'tomato'}` |
| `number style`* | Assume that the token is a number, and convert it to the specified format, which can be any of the following: `digit`, `roman numeral`, `cardinal`, or `ordinal`. The latter two options may be followed with `spaced` or `unspaced` to clarify how to handle words like "twenty-seven". The default is to use dashes. | `number style: cardinal`                                     |

#### Failed Edits

The `lookup` and `number style` edits are unique in that it is possible for them to fail. A token may fail a lookup if it does not match any of the provided regexes, while it may fail a number style edit if it cannot be recognized as a number. When this happens, the default behavior depends on whether the failed edit is part of a token definition, or instead part of a string builder.

If the edit is part of the token definition, it will cause the entire citation to fail as if it had never matched the template in the first place. On the other hand, if the token is being used in a string builder, failure will simply cause the affected token's value to be set to null for purposes of the string builder.

You can change the default behavior by adding the following tag to an edit: `mandatory: no`. If an edit with this tag fails, the edit will simply be ignored.

For instance, the following "reporter" token can be any string of up to ten characters, but if it is "F. Supp." or "P. 2d" it will be replaced with "F.Supp." or "P.2d", respectively. Because the lookup is tagged as not mandatory, tokens that don't match either of these strings will be unaffected. Without that tag, the entire citation would be discarded if it did not match either of those values.

```yaml
...
  tokens:
    reporter:
      regex: .{1,10}
      edits:
        - mandatory: no
          lookup:
            F\. ?Supp\.: F.Supp.
            P\. ?2d: P.2d
          
...
```

#### Chaining Multiple Edits

Edits can be chained, and they will take effect in the order they are listed. For instance, if you wanted to store the article numbers as lower-case Roman numerals, you could do this:

```yaml
  tokens:
    article:
      regex: [1-7]|[IV]{1,3}|One|Two|Three|Four|Five|Six|Seven
      edits:
        number style: roman
        case: lower
```

### Severability

Ordinarily, if two citations both have a token and that token differs between the two of them, the two citations are thought to be completely unrelated. For instance, "33 USC § 10" is a totally different law than "33 USC § 100", even though "100" starts with "10".

However, sometimes it *is* relevant that one token begins with the same value as another. For instance, the Code of Federal Regulations template has a "subsection" token that matches a sequence of one or more numbers or letters in parentheses. But ordinarily, CiteURL would treat "21 CFR § 820.1(a)" and "21 CFR § 820.1(a)(1)" as totally unrelated subsections since "(a)" is not the same as "(a)(1)". This is wrong, since the former citation encompasses the latter.

To handle these situations, tokens can be given the `severable: yes` tag, to indicate that when the only difference between two citations is that the second one has a severable token that extends longer than the first one's, the first citation is thought to include the second one.

```yaml
...
  tokens:
    subsection:
      regex: '(\(\w{1,4}\))+'
      severable: yes
...
```

Note that the `severable` tag is unnecessary when the difference is that one citation is simply *missing* a possible token. For instance, "U.S. Const. Article III" is known to include "U.S. Const. Article III, § 2" just because the U.S. Constitution template defines the article token before the section token.

### Default Values

Often a citation may be valid even if it does not contain all tokens that it possibly could. For instance, a citation to a court opinion may or may not have a pincite to a specific page. Normally, when such a token is omitted, its value is `None`. However, you can also specify a different default value if you wish:

```yaml
...
  tokens:
    section:
      regex: \d+
      default: '1'
...
```

## Patterns

Patterns are essentially the regular expressions that a template uses to detect overall citations. However, a pattern is not a pure regex---instead of including a regex for each token the pattern can recognize, the pattern simply contains a reference to the token itself. This is useful as a way to avoid redefining a token's regex when it is used in multiple patterns. As such.

A template's `patterns` are responsible for recognizing one or more formats of typical long-form citations to the given body of law. In addition to these, a template can also have `shortform patterns` and `idform patterns`, which are triggered once a longform citation has already been recognized. When this occurs, CiteURL looks for "idform" citations until it encounters a different intervening citation, and it looks for shortforms anywhere until the end of the document. In addition, a template can have `broad patterns`, which are exactly like longform patterns except that they are only used in search engine-like contexts, where user convenience is more important than avoiding false positives.

### Pattern Format

Regardless of the type of pattern, they share a few key points of formatting. First, it is possible to specify patterns either in singular form or in list form. For instance, either of these would be valid:

```yaml
...
  pattern: '{volume} USC § {section}'
...
```

```yaml
...
  patterns:
    - '{volume USC (§|[Ss]ec(tion|t?\.) {section}'
    - '(§|[Ss]ec(tion|t?\.) {section} of [Vv]olume {volume} of the U\.S\. Code'
...
```

This is not to be confused with another feature of patterns: An individual pattern can be provided either as a single string, or as a list of strings. This is useful so that you can take advantage of [YAML anchors](https://medium.com/@kinghuang/docker-compose-anchors-aliases-extensions-a1e4105d70bd) to avoid rewriting certain common bits of regex. Consider the following example:

```yaml
...
  patterns:
    - ['{volume} USC ', &sec_sign '(§|[Ss]ec(tion|t?\.)', ' {section}']
    - [*sec_sign, ' {section} of [Vv]olume {volume} of the U\.S\. Code']
...
```

The above example defines a YAML anchor called `sec_sign` to represent any string that is either "§", "Section", or various abbreviations thereof. Because it would be a pain to write that string repeatedly across a large number of templates, it's useful to reuse it as a YAML anchor. Although each pattern is broken into a list, it is functionally equivalent to the previous example.

### Shortforms and Idforms

These two types of patterns are intended to recognize contextual references to a citation that was found previously in the text. To facilitate this, they both share one special feature: Values from their parent longform citation can be inserted into the shortform pattern so as to only match when the specified value is the same. Consider the following example:

```yaml
U.S. Caselaw:
  tokens:
    reporter: {regex: .{3, 10}}
    volume: {regex: \d+}
    page: {regex: \d+}
    pincite: {regex: \d+}
  pattern: '{volume} {reporter} {page}(, {pincite})?'
  shortform pattern: '{same volume} {same reporter} at {pincite}'
  idform pattern: 'Id\. at {pincite}'
```

This template will recognize longform citations like "413 F. Supp. 1281". Once it has found such a citation, it can detect immediate repeat citations like "*Id.* at \<any number\>", because of its `idform pattern`. The `shortform pattern`, meanwhile, will match any subsequent occurrence of "413 F. Supp. \<any number\>" anywhere in the text.

## String Builders

The two kinds of string builder are a template's `name builder` and its `URL builder`, and they both work the same way. They use a citation's [tokens](#tokens) to fill placeholders in a pattern and output a uniform string representation of that citation. This is the source of each citation's `name` and `URL` properties.

A string builder is made up of one or more `parts`, and optionally a list of `edits`. The first value,`parts`, is a list of strings that will be concatenated to make the result. Each part can contain placeholder values in curly braces. The placeholders will be replaced with the corresponding token values or [metadata](#metadata) values. If a part references a blank token, that part will be omitted from the overall string.

`edits` is a list of token edits that will be performed on the tokens and metadata just before they are inserted into the string. They work just like the [token edits](#edits) described earlier, except for two differences.

First, whereas the edits described earlier serve to normalize tokens after they are matched in text, these ones are only used in order to build a string---they do not permanently modify the underlying tokens.

Second, because these edits are not listed by token, you must specify which token each one operates on, by giving it a `token` value. You can also optionally give it an `output` value, in which the result of the edit will be saved to the specified token instead of modifying the input.

Here's an example of each kind of string builder:

```yaml
U.S. Code:
  ...
  name builder:
    parts:
      - '{title} U.S.C. § {section}'
      - '{subsection}'
  URL builder:
    parts:
      - https://www.law.cornell.edu/uscode/text/{title}/{section}
      - '#{subsection}'
    edits:
      - token: subsection
        sub: ['\)\(', '_']
      - token: subsection
        sub: ['[()]', '']
```

If this template is given the citation, "42 usc 1988", the `name builder` will use the title and section numbers to write "42 U.S.C. § 1983". The '{subsection}' part is omitted because the citation has no subsection. Likewise, the `URL builder` will make [this URL](https://www.law.cornell.edu/uscode/text/42/1988), ignoring the blank token and the edits that rely on it.

Given the citation "29 USC § 158(b)(4)", however, the `URL builder` will take the subsection and subject it to two edits, first to change it from '(b)(4)' to '(b_4)', and then to change that to 'b_4'. Having done that, it can fill in the '#{subsection}' part, and create [this URL](https://www.law.cornell.edu/uscode/text/29/158#b_4).

## Miscellaneous

The following features aren't crucial to what a template is, or what it does, but they're nice to have when you're trying to write a whole lot of templates without reinventing the wheel too many times.

### Metadata

A template can have a `meta` attribute that contains a dictionary of values that will be accessible to the template's patterns and string builders just like a token is. Note that token edits in string builders can override metadata values using the `output` tag.

### Template Inheritance

A template can `inherit` any already-defined template, such that it will copy any characteristics of that template except for those that are expressly overwritten. This is useful when two templates are both very, very complicated, but they are largely similar in format.

For instance, citations to the Code of Federal Regulations are very similar to the U.S. code, so most of this horrible mess only needs to be written once:

```yaml
U.S. Code:
  meta:
    name regex: 'U\. ?S\. ?C(ode|\.)|USC|United States Code'
    abbreviation: U.S.C.
  tokens:
    title: {regex: \d+}
    section: {regex: '\d[\w.-]*\w|\d'}
    subsection:
      regex: '(\(\w{1,4}\))+'
      severable: yes
  patterns:
    - - &title ([Tt]itle )?{title}
      - ',? {name regex}(,? )?('
      - &section_sign ((&sect;|&#167|§){1,2}|[Ss]ec(tions?|t?s?\.))
      - ')? ?{section}'
      - &subsec '(((,? )?sub(sections?|divisions?|(sec|d(iv)?)?s?\.))? ?{subsection})?'
    - ['[Tt]itle {title},? (', *section_sign, ')? ?{section}', *subsec, ' of the {name regex}']
    - ['(', *section_sign, ')? ?{section}', *subsec, ' of [Tt]itle {title} of the {name regex}']
  idform patterns:
    - '[Ii]d\.( at)?( §§?)? ?{section}( ?{subsection})?'
    - '((&sect;|&#167|§){1,2}|[Ss]ec(tions?|t?s?\.)) {section}( ?{subsection})?(?! of)'
    - '[Ii]d\. at {subsection}'
  name builder:
    parts:
      - '{title} {abbreviation} § {section}'
      - '{subsection}'
  URL builder:
    parts:
      - https://www.law.cornell.edu/uscode/text/{title}/{section}
      - '#{subsection}'
    edits:
      - token: subsection
        sub: ['\)\(', '_']
      - token: subsection
        sub: ['[()]', '']


Code of Federal Regulations:
  inherit: U.S. Code
  meta:
    name regex: 'C\.? ?F\.? ?R\.?|Code of Federal Regulations'
    abbreviation: C.F.R.
  URL builder:
    parts:
      - 'https://ecfr.federalregister.gov/cfr-reference?cfr%5Bdate%5D=current&cfr%5Breference%5D={title} CFR {section}''
      - '#p-{section}{subsection}'
```

