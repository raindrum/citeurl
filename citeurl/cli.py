#!/usr/bin/python
"""
This is a tool to detect legal citations in text, and generate relevant hyperlinks. For more information, see https://github.com/raindrum/citeurl."""

# python standard imports
from sys import stdin
from argparse import ArgumentParser, SUPPRESS
from tempfile import NamedTemporaryFile
import webbrowser
import time

# internal imports
from . import Citator

def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "-i",
        "--input",
        help="the file to read from",
    )
    parser.add_argument(
        "text",
        help=(
            "a string containing legal citations. Can be omitted if -i is "
            + "specified, or if text is piped from stdin"
        ),
        nargs="*",
        default=(None if stdin.isatty() else [''.join(stdin.read()[0:-1])])
    )
    action = parser.add_mutually_exclusive_group(required=False)
    action.add_argument(
        "-o",
        "--output",
        help="the file to write to, rather than stdout",
    )
    action.add_argument(
        "-l", "--lookup",
        action="store_true",
        help=(
            "look up first citation found in the text, instead of "
            + "inserting links. Uses broader regex if available."
        ),
    )
    action.add_argument(
        "-a",
        "--authorities",
        action="store",
        nargs="?",
        const=-1,
        type=int,
        help=(
            "return list of all the authorities cited in the text, "
            + "with information about each one. If a number is given, "
            + "return only the X authorities with the most citations."
        )
    )
    parser.add_argument(
        "-b", "--browse",
        action="store_true",
        help=(
            "open the result in a browser. If the '-l' option is used, "
            + "it will directly open the generated URL. Otherwise, it "
            + "makes a temporary HTML file with the hyperlinked text, "
            + "and opens that. Has no effect if paired with '-a'."
        )
    )
    parser.add_argument(
        "-n",
        "--no-default-schemas",
        action="store_true",
        help="prevent loading the default set of schemas",
    )
    parser.add_argument(
        "-s",
        "--schema-file",
        action="append",
        default=SUPPRESS,
        help=(
            "path to a YML file containing schemas to load. Can be "
            + "called multiple times to load multiple files. See "
            + "https://github.com/raindrum/citeurl#writing-your-own-schemas."
        )
    )
    parser.add_argument(
        "-c",
        "--css-class",
        default='citation',
        help=(
            "the class each inserted <a> element will have. "
            + 'Defaults to "citation"'
        )
    )
    parser.add_argument(
        "-I",
        "--link-ids",
        action="store",
        type=str,
        default='detailed',
        choices=['all', 'detailed', 'none'],
        help='which "id" citations to hyperlink. Options are "all", "none", '
            + 'and "detailed". Defaults to detailed, which links "id. at 35" '
            + 'but not "id."'
    )
    args = parser.parse_args()
        
    # parse text or file input
    if args.input:
        with open(args.input, 'r') as f:
            text = f.read()[0:-1]
    elif args.text:
        text = ' '.join(args.text)
    else:
        parser.print_help()
        return
    
    # load schemas
    defaults = not args.no_default_schemas
    if 'schema_file' in args:
        citator = Citator(yaml_paths=args.schema_file, defaults=defaults)
    elif defaults:
        citator = Citator()
    else:
        raise SystemExit(
            "Can't use '-n' without specifying a custom schema file."
        )

    # print output to file or stdout
    if args.lookup:
        citation = citator.lookup(text)
        if citation:
            key_lengths = [
                len(k) for k in citation.tokens.keys()
                if citation.tokens[k]
            ]
            tab_width = max(key_lengths) + 2
            print('Source: '.ljust(tab_width) + str(citation.schema))
            for key, value in citation.tokens.items():
                if not value:
                    continue
                print(f'{key.title()}: '.ljust(tab_width) + value)
            print('URL: '.ljust(tab_width) + (citation.URL or 'Unavailable'))
            if args.browse:
                webbrowser.open(citation.URL)
        else:
            print("Couldn't recognize citation.")
    elif args.authorities:
        authorities = citator.list_authorities(text)
        if args.authorities != -1:
            authorities = authorities[:args.authorities]
        outputs = []
        for authority in authorities:
            output = f"Authority:  {authority}"
            output += f"\nSource:     {authority.schema}"
            if authority.URL:
                output += "\nURL:        " + authority.URL
            output += f"\nReferences: {len(authority.citations)}"
            outputs.append(output)
        print('\n\n'.join(outputs))
    else:
        out_text = citator.insert_links(
            text,
            attrs={'class': args.css_class} if args.css_class else [],
            link_detailed_ids=False if args.link_ids == 'none' else True,
            link_plain_ids=True if args.link_ids == 'all' else False)
        if args.output:
            with open(args.output, 'w') as f:
                f.write(out_text)
        if args.browse:
            with NamedTemporaryFile('r+', suffix='.html') as f:
                f.write(out_text)
                webbrowser.open('file://' + f.name)
                f.seek(0)
                time.sleep(2)
        if not args.output and not args.browse:
            print(out_text)

if __name__ == "__main__":
    main()
