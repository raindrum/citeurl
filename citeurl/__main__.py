#!/usr/bin/python
"""
This is a tool to detect legal citations in text, and generate relevant hyperlinks. For more information, see https://github.com/raindrum/citeurl."""

# python standard imports
from sys import stdin
from argparse import ArgumentParser, SUPPRESS

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
        "-l",
        "--lookup",
        action="store_true",
        help=(
            "return URL for a single citation instead of inserting links"
            + " into a body of text. Uses broader regex if available"
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
        "--no-link-ids",
        action="store_true",
        help="don't hyperlink citations like 'id. at 30'"
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
        citator = Citator(args.schema_file, defaults)
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
            print(citation.text)
            print("=" * len(citation.text))
            print('Source: %s' % citation.schema)
            for key, value in citation.tokens.items():
                if not value: continue
                print('%s: %s' % (key.title(), value))
            print('URL: %s' % citation.URL)
        else:
            print("Couldn't recognize citation.")
    elif args.authorities:
        authorities = citator.list_authorities(text)
        if args.authorities != '-1':
            authorities = authorities[:args.authorities]
        for authority in authorities:
            #print("Authority: %s" % authority)
            print(authority)
            print("=" * len(str(authority)))
            print("Citations: %s" % len(authority.citations))
            if authority.URL:
                print("URL: %s" % authority.URL)
            print()
    else:
        out_text = citator.insert_links(
            text,
            attrs={'class': args.css_class} if args.css_class else [],
            link_detailed_ids = not args.no_link_ids)
        if args.output:
            with open(args.output, 'w') as f:
                f.write(out_text)
        else:
            print(out_text)

if __name__ == "__main__":
    main()
