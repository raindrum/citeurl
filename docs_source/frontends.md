# CiteURL Frontends

CiteURL can be used in a few forms besides the [command-line tool](../index#usage) and [the Python library](../library). Here's what they are:

## JavaScript

Although CiteURL is primarily a Python program, it can also generate a JavaScript implementation of its citation lookup function, so that end users can look up citations in a web browser without having to install anything. [Law Search](https://raindrum.github.io/lawsearch) is one such instance that I maintain on my website.

You can use the `citeurl makejs` command to make your own custom instances that support arbitrary sources of law. Here's how:

1. [Write a YAML file](template-yamls) with one or more custom citation templates.
2. [Install CiteURL](../index#installation) if you have not done so already.
3. Open a command line and run the following:

``` bash
citeurl makejs -e -o output.html -t PATH_TO_YOUR_TEMPLATES.YAML
```

Alternatively, to omit the default templates, include the `-n` option in that command.

After exporting an HTML file, you can bookmark the local file as a [custom search engine](https://www.howtogeek.com/114176/HOW-TO-EASILY-CREATE-SEARCH-PLUGINS-ADD-ANY-SEARCH-ENGINE-TO-YOUR-BROWSER/).

Alternatively, if you have a web page you'd like to embed CiteURL functionality into, you can also generate the JavaScript by itself. To do that, omit the `-e` option and save the output as a `.js` file. All the citation lookup functionality is available via its `getUrlForQuery()` function, which takes a search query string as input, and returns the completed URL.

For more info, run `citeurl makejs -h`.

## Markdown Extension

CiteURL can also be used as an extension to [Python-Markdown](https://python-markdown.github.io/). You can load the extension as `citeurl`, and it supports the following options:

- `custom_templates`: A list of paths to YAML files containing [custom citation templates](../template-yamls). Defaults to none.
- `use_defaults`: Whether CiteURL should load the default citation templates. Defaults to `True`.
- `attributes`: A dictionary of HTML attributes to give each hyperlink that CiteURL inserts into the text. Defaults to `{'class': 'citation'}`.
- `link_detailed_ids`: Whether to insert links for citations like `Id. at 305`. Defaults to `True`.
- `link_plain_ids`: Whether to insert links for citations like `Id.`. Defaults to `False`.
- `break_id_on_regex`: Anywhere this string (parsed as regex) appears in the text, chains of citations like `id.` will be interrupted. Note that this is based on the output HTML, *not* the original Markdown text. Defaults to `L\. ?Rev\.|J\. ?Law|\. ?([Cc]ode|[Cc]onst)`

### GNOME Shell Search Provider

If you use the GNOME desktop environment, you can install [my other project](https://extensions.gnome.org/extension/4225/gnome-citeurl-search-provider/) to look up citations directly from your desktop!