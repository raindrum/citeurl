#!/usr/bin/python
"""
This is a tool to detect legal citations in text, and generate relevant hyperlinks. For more information, see https://github.com/raindrum/citeurl."""

# python standard imports
from sys import stdin
from argparse import ArgumentParser, SUPPRESS

# internal imports
from . import Schema_Set

def main():
    p = ArgumentParser(description=__doc__)
    p.add_argument(
        "text",
        help=(
            "a string containing legal citations. Can be omitted if -i is "
            + "specified, or if text is piped from stdin"
        ),
        nargs="*",
        default=(None if stdin.isatty() else [''.join(stdin.read()[0:-1])])
    )
    p.add_argument(
        "-i",
        "--input",
        help="the file to read from",
    )
    p.add_argument(
        "-o",
        "--output",
        help="the file to write to, rather than stdout",
    )
    p.add_argument(
        "-l",
        "--lookup",
        action="store_true",
        help=(
            "return URL for a single citation instead of inserting links"
            + " into a body of text. Uses broader regex if available"
        ),
    )
    p.add_argument(
        "-n",
        "--no-default-schemas",
        action="store_true",
        help="prevent loading the default set of schemas",
    )
    p.add_argument(
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
    p.add_argument(
        "-c",
        "--css-class",
        default='citation',
        help=(
            "the class each inserted <a> element will have. "
            + 'Defaults to "citation"'
        )
    )
    args = p.parse_args()
        
    # parse text or file input
    if args.input:
        with open(args.input, "r") as f:
            query = f.read()[0:-1]
    elif args.text:
        query = " ".join(args.text)
    else:
        p.print_help()
        return
    
    # load schemas
    defaults = not args.no_default_schemas
    if 'schema_file' in args:
        schemas = Schema_Set(args.schema_file, defaults)
    elif defaults:
        schemas = Schema_Set()
    else:
        raise SystemExit(
            "Can't use '-n' without specifying a custom schema file."
        )

    # print output to file or stdout
    if args.lookup:
        print(schemas.lookup_query(query))
    else:
        out_text = schemas.insert_links(query, css_class=args.css_class)
        if args.output:
            with open(args.output, 'w') as f:
                f.write(out_text)
        else:
            print(out_text)

if __name__ == "__main__":
    main()
