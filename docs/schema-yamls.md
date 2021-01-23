# Writing Your Own Schemas

CiteURL supports a number of citation formats out-of-the box, and I try to add more when I can. However, it will never support every possible kind of citation, and you might want to treat certain citations differently than CiteURL does by default.

Schemas [can be created at runtime](classes/#citeurl.Schema.__init__), but it is more practical to write a list of them in a YAML file, and load them when instantiating the [Citator](classes#citator). 

Before you proceed, make sure you are fairly familiar with [Python Regular Expressions](https://docs.python.org/3/howto/regex.html), because schemas rely on them heavily.

If you want more examples of schemas after reading this, look at [CiteURL's built-in schemas](https://github.com/raindrum/citeurl/blob/main/citeurl/default-schemas.yaml).

## The Basic Schema Format

Here is a simplified example of a schema in YAML format:

```yaml
- name: United States Code
  regex: (?P<title>\d+) USC § (?P<section>\d+)
  URL: https://www.law.cornell.edu/uscode/text/{title}/{section}
```

This schema recognizes any series of one or more digits, followed by " USC § ", followed by another series of digits. It knows that the first string of digits are something called a "title" and the second is a "section". We will call these stored values `tokens`. Finally, the schema contains a template to generate a URL based on the recognized citation. It does this by replacing the placeholders in {curly braces} with the values from the captured tokens.

Note that any regex, including idForms and shortForms, can be provided as **either as a string or a list of strings**. In the latter case, they will be concatenated (without any separator) to create the actual regex. There is no functional difference between using strings and lists, except that providing them in list form allows you to reuse common regex parts using [YAML anchors](https://medium.com/@kinghuang/docker-compose-anchors-aliases-extensions-a1e4105d70bd).

URLs can also be specified in list form, but this serves a functional role: If a list item contains a placeholder for which no value is set, that whole list item will be omitted from the final URL. 

## idForms and shortForms

The example schema above does not have any way recognize subsequent shortform citations. The schema will recognize "42 USC § 1983", but it will not know that a subsequent "Id. at § 1988" is referring to 42 USC § 1988. For that, you can add a list of `idForms` to the schema, to recognize a reference to the immediately-preceding citation:

```yaml
  idForms:
    - Id\. at § (?P<section>\d+)
```

With this field present, the parser will know that when it sees "Id. at § 1988" shortly after a full citation to 42 USC § 1983, this is a child citation, which will retain all the tokens from the parent citation except those which are present in the idForm regex.

While it's not relevant to the example above, you can also define `shortForms`. These work the same as `idForms`, except that they match text *anywhere* after the original long-form citation, whereas `idForms` will only match until the next different citation (or until a different interruptor defined in [Citator.list_citations()](classes/#citeurl.Citator.list_citations)).

Another feature of `idForms` and `shortForms` is that, like URL templates, they can contain placeholders in {curly braces}. These placeholders will be replaced with the text from the long-form citation so that you can ensure that they only match citations where those tokens are unchanged. For instance, you could write a schema to recognize court cases:

```yaml
- name: Caselaw
  regex: (?P<volume>\d+) (?P<reporter>.{3,15}?) (?P<page>\d+)(, (?P<pincite>\d+))?
  shortForms:
    - {volume} {reporter} at (?P<pincite>\d+)
```

This schema will recognize long-form citations like 372 U.S. 335 (optionally with a pincite citation afterwards). After that long-form citation is recognized, it will generate the regex `372 U\.S\. at (?P<pincite>\d+)`, to recognize later citations to different pincites in the same case.

### broadRegex

`broadRegex` is an optional alternative regex which, if present, will be used instead of `regex` in methods like [lookup()](classes/#citeurl.Schema.lookup), where false-positives are not a problem.

## Token Processing

What if the captured tokens don't directly correspond to the values that need to be inserted into the URL? For these situations, you'll need to use some combination of `defaults`, `mutations`, and `substitutions` to process the tokens before inserting them into the URL.

### mutations

`mutations` is a list of dictionaries, each one representing a string manipulation that should be performed on a token before it is inserted into the URL template. Each mutation must contain a key called `token`, representing the token to affect.

The supported mutations are `case`, `omit`, and the combination of `splitter` and `joiner`.

- `case` forces the token to the specified capitalization, either 'upper' or 'lower'.

- `omit` is a string, parsed as regex, all occurrences of which will be removed from the token.
- `splitter` and `joiner` must be used together if at all. The former is a string, parsed as regex, which will split the token at each occurrence. The `joiner` string will be placed between the pieces.

The following example uses a mutation to convert subsection strings like "(a)(1)(B)" into "a_1_B", the format used on [the Cornell website](https://www.law.cornell.edu/):

```yaml
- Name: United States Code
  regex: (?P<title>\d+) USC § (?P<section>\d+)(?P<subsection>(\(\w+\))+)?
  mutations:
    - token: subsection
      splitter: \W
      joiner: _
```

### substitutions

`substitutions` is a list of dictionaries, each one representing a lookup operation to modify the value of a token. Each dict must contain 'token', a string representing the input token for the lookup. It must also contain `index`, a dict of input values and their corresponding outputs.

By default, the value of `token` will be changed to the value of the lookup. Alternatively, if you specify an `outputToken`, that token will be set instead, leaving the input token unchanged. Note that `outputToken` does not need to exist in the original regex.

If the `inputToken` does not match a key in the index, the citation match fails, unless the substitution specifies that `allowUnmatched` is True, in which case a failed substitution simply won't change any values.

You can also include `useRegex: true` to make the dictionary lookup use regex matching rather than normal string matching, but this feature is experimental and likely buggy.

The following example uses substitutions to convert citations to the National Labor Relations Act into URLs pointing to the corresponding sections of the U.S. Code:

```yaml
- name: National Labor Relations Act
  regex: NLRA § (?P<section>\d+)
  substitutions:
    - inputToken: section
      index: {'1':'151', '2':'152', '3':'153', '4':'154', '5':'155', '6':'156', '7':'157', '8':'158', '9':'159', '10':'160', '11':'161', '12':'162', '13':'163', '14':'164', '15':'165', '16':'166', '17':'167', '18':'168', '19':'169'}
  URL: https://www.law.cornell.edu/uscode/text/8/{section}
```

### defaults

`defaults` is a dictionary of tokens whose values will be set to specified values, if they are not set by the regex:

```yaml
- name: Demo
  regex: If no number here, assume 3:( (?P<number>\d+))?
  defaults: {'number': '3'}
```