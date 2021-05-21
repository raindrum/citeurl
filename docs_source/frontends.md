# CiteURL Frontends

CiteURL can be used in a few forms besides the [command-line tool](../index#usage) and [the Python library](../library). Here's what they are:

## CiteURL Server

If you just want to use CiteURL from your web browser, it's hosted as a web app at [citation.link](https://www.citation.link).

You can also host your own instance of it on your local network or beyond. This is useful if you want to add support for your own [custom citation templates](template-yamls). The simplest way is to run this command:

```citeurl
citeurl host -st PATH_TO_YOUR_TEMPLATES.YAML
```

Or, if you're using a hosting provider like [pythonanywhere.com](https://pythonanywhere.com), you can give it direct access to CiteURL as a Flask application:

```python
from citeurl.web.server import App
from citeurl import Citator

APP = App(Citator(yaml_paths=['PATH_TO_YOUR_TEMPLATES.YAML']))
```

## JavaScript

Although CiteURL is primarily a Python program, you can also use it to generate a JavaScript implementation of its citation lookup functionality, including any extra citation templates you've written. This allows it to be hosted on a static website (like [mine](https://raindrum.github.io/lawsearch), for example), or distributed as an HTML file that people can save to their own computers and bookmark as a [custom search engine](https://www.howtogeek.com/114176/HOW-TO-EASILY-CREATE-SEARCH-PLUGINS-ADD-ANY-SEARCH-ENGINE-TO-YOUR-BROWSER/).

To make a JavaScript implementation, first [make a YAML file](template-yamls) with any custom citation templates you'd like to support. Next, open a command line and run the following command:

``` bash
citeurl makejs -e -o output.html -t PATH_TO_YOUR_TEMPLATES.YAML
```

Alternatively, to omit CiteURL's default templates, include the `-n` option in that command. For more info, run `citeurl makejs -h`.

## Markdown Extension

CiteURL can also be used as an extension to [Python-Markdown](https://python-markdown.github.io/). You can load the extension as `citeurl`, and it supports the following options:

- `custom_templates`: A list of paths to YAML files containing [custom citation templates](../template-yamls). Defaults to none.
- `use_defaults`: Whether CiteURL should load the default citation templates. Defaults to `True`.
- `attributes`: A dictionary of HTML attributes to give each hyperlink that CiteURL inserts into the text. Defaults to `{'class': 'citation'}`.
- `link_detailed_ids`: Whether to insert links for citations like `Id. at 305`. Defaults to `True`.
- `link_plain_ids`: Whether to insert links for citations like `Id.`. Defaults to `False`.
- `break_id_on_regex`: Anywhere this string (parsed as regex) appears in the text, chains of citations like `id.` will be interrupted. Note that this is based on the output HTML, *not* the original Markdown text. Defaults to `L\. ?Rev\.|J\. ?Law|\. ?([Cc]ode|[Cc]onst)`

## GNOME Shell Search Provider

If you use the GNOME desktop environment, you can install [my other project](https://extensions.gnome.org/extension/4225/gnome-citeurl-search-provider/) to look up citations directly from your desktop!
