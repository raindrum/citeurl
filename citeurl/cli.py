#!/usr/bin/python
"""
This is a tool to detect legal citations in text, and
generate relevant hyperlinks. For more information, see
https://raindrum.github.io/citeurl."""

# NOTE: the commented-out imports are imported conditionally later on

# python standard imports
from sys import stdin
from argparse import ArgumentParser, SUPPRESS
# import webbrowser
# from tempfile import NamedTemporaryFile
# from time import sleep

# internal imports
from . import Citator
# from .web.server import serve, App
# from .web.makejs import makejs

def main():
    parser = ArgumentParser(
        description=__doc__,
        epilog=(
            "You must specify one of the four commands, e.g. 'citeurl "
            + "lookup'. You can find more info for each command by running "
            + "'citeurl <COMMAND> -h'."
        )
    )
    
    # common options
    shared_args = ArgumentParser(add_help=False)
    shared_args_grp = shared_args.add_argument_group(title='citator options')
    shared_args_grp.add_argument(
        '-t', '--template-file',
        metavar='FILE',
        action='append',
        default=SUPPRESS,
        help=(
            'path to a YAML file with extra citation templates for CiteURL '
            + 'to use. See https://raindrum.github.io/citeurl/template-yamls '
            + 'for help writing templates. The -t option can be used '
            + 'multiple times to load multiple files.'
        )
    )
    shared_args_grp.add_argument(
        '-n', '--no-default-templates',
        action='store_true',
        help="prevent loading CiteURL's default templates",
    )
    
    subparsers = parser.add_subparsers(
        dest='command',
        title='commands',
        required=False
    )
    
    ####################################################################
    # TEXT PROCESSOR OPTIONS
    ####################################################################
    
    process_parser = subparsers.add_parser(
        'process',
        aliases=['p'],
        parents=[shared_args],
        help='detect all citations in a block of text',
    )
    process_parser.add_argument(
        '-i',
        '--input',
        metavar='FILE',
        help='path to a file from which to read input text',
    )
    process_parser.add_argument(
        'text',
        help=(
            'a string containing legal citations. Can be omitted if -i is '
            + 'specified, or if text is piped from stdin'
        ),
        nargs='*',
        default=(None if stdin.isatty() else [''.join(stdin.read()[0:-1])])
    )
    process_parser.add_argument(
        '-I', '--link-ids',
        action='store',
        type=str,
        default='detailed',
        choices=['all', 'detailed', 'none'],
        help='which "id" citations to hyperlink. Options are "all", "none", '
            + 'and "detailed". Defaults to detailed, which links "id. at 35" '
            + 'but not "id."'
    )
    process_parser.add_argument(
        '-c', '--css-class',
        metavar='CLASS',
        default='citation',
        help=(
            'the class each inserted <a> element will have. '
            + 'Defaults to "citation"'
        )
    )
    output = process_parser.add_mutually_exclusive_group(required=False)
    
    output.add_argument(
        '-o', '--output',
        metavar='FILE',
        help='write hyperlinked text to a file instead of stdout',
    )
    output.add_argument(
        '-b', '--browse',
        action='store_true',
        help=(
            'make a temporary HTML file with the hyperlinked text, '
            + 'and open it in a browser.'
        )
    )
    output.add_argument(
        '-a', '--authorities',
        metavar='NUMBER',
        action='store',
        nargs='?',
        const=-1,
        type=int,
        help=(
            'return list of all the authorities cited in the text, '
            + 'with information about each one. If a number is given, '
            + 'return only the X authorities with the most citations.'
        )
    )
    
    ####################################################################
    # LOOKUP COMMAND OPTIONS
    ####################################################################
    
    lookup_parser = subparsers.add_parser(
        'lookup',
        aliases=['l'],
        parents=[shared_args],
        help='look up the URL or other information for a single citation',
    )
    lookup_parser.add_argument(
        'text',
        help=(
            'a string containing legal citations. Can be omitted if text is '
            + ' piped from stdin'
        ),
        nargs='*',
        default=(None if stdin.isatty() else [''.join(stdin.read()[0:-1])])
    )
    lookup_parser.add_argument(
        '-b', '--browse',
        action='store_true',
        help='open the resulting URL, if any, in a browser'
    )
    lookup_parser.add_argument(
        '-s', '--strict',
        action='store_true',
        help=(
            'match templates the same way the "process" command does: '
            + "use case-sensitive regex, and ignore templates' broadRegexes"
        )
    )
    
    ####################################################################
    # HOST COMMAND OPTIONS
    ####################################################################
    
    server_parser = subparsers.add_parser(
        'host',
        aliases=['h'],
        parents=[shared_args],
        help='host a citation lookup server via HTTP',
    )
    server_parser.add_argument(
        '-s', '--serve',
        action='store_true',
        help="make the server available to your local network"
    )
    server_parser.add_argument(
        '-p', '--port',
        action='store',
        default=53037,
        type=int,
        help=('the port to use for hosting. Defaults to 53037')
    )
    
    ####################################################################
    # MAKEJS COMMAND OPTIONS
    ####################################################################
    
    makejs_parser = subparsers.add_parser(
        'makejs',
        aliases=['m'],
        parents=[shared_args],
        help='export an instance of CiteURL as JavaScript',
    )
    
    makejs_parser.add_argument(
        '-e', '--entire-page',
        action='store_true',
        help='generate a full HTML page instead of just JavaScript',
    )
    makejs_parser.add_argument(
        '-s', '--sources-table',
        action='store_true',
        help=(
            'include a table listing all the supported sources of law. '
            + 'Implies --entire-page.'
        )
    )
    makejs_parser.add_argument(
        '-o', '--output',
        metavar='FILE',
        help='write output to a file instead of stdout',
    )
    
    ####################################################################
    # SETUP
    ####################################################################
    
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return
    
    # un-abbreviate command vars
    if args.command == 'l':
        args.command = 'lookup'
    elif args.command == 'p':
        args.command = 'process'
    elif args.command == 'h':
        args.command = 'host'
    elif args.command == 'm':
        args.command = 'makejs'
    
    # these commands share functionality for parsing input,
    # as well as the 'browse' option
    if args.command in ['process', 'lookup']:
        if args.browse:
            import webbrowser
        
        if 'input' in args and args.input:
            with open(args.input, 'r') as f:
                text = f.read()[0:-1]
        elif args.text:
            text = ' '.join(args.text)
        else:
            if args.command == 'process':
                process_parser.print_help()
            else:
                lookup_parser.print_help()
            return
        
    # create citator
    defaults = not args.no_default_templates
    citator = Citator(
        yaml_paths=args.template_file if 'template_file' in args else [],
        defaults=defaults
    )
    if not citator.templates:
        raise SystemExit("Can't use '-n' without specifying a template file.")
    
    ####################################################################
    # TEXT PROCESSOR COMMAND
    ####################################################################
    
    if args.command == 'process':
                  
        if args.authorities: # print list of
            authorities = citator.list_authorities(text)
            if args.authorities != -1:
                authorities = authorities[:args.authorities]
            outputs = []
            for authority in authorities:
                output = f"Authority:  {authority}"
                output += f"\nSource:     {authority.template}"
                if authority.URL:
                    output += "\nURL:        " + authority.URL
                output += f"\nReferences: {len(authority.citations)}"
                outputs.append(output)
            print('\n\n'.join(outputs))
        
        else:
            out_text = citator.insert_links(
                text,
                attrs={'class': args.css_class},
                link_detailed_ids=False if args.link_ids == 'none' else True,
                link_plain_ids=True if args.link_ids == 'all' else False
            )
        
            if args.output: #write processed text to file
                with open(args.output, 'w') as f:
                    f.write(out_text)
            
            elif args.browse: # write processed text to tempfile; open it
                from tempfile import NamedTemporaryFile
                from time import sleep
                with NamedTemporaryFile('r+', suffix='.html') as f:
                    f.write(out_text)
                    webbrowser.open('file://' + f.name)
                    f.seek(0)
                    sleep(2)

            else: # just print to stdout
                print(out_text)

    ####################################################################
    # LOOKUP COMMAND
    ####################################################################
    
    elif args.command == 'lookup':
        citation = citator.lookup(text, broad=False if args.strict else True)
        
        # cancel if no citation found
        if not citation:
            print("Couldn't recognize citation.")
            return
        
        # pretty-print citation information by indenting each bit of info
        # based on the length of the longest token name
        key_lengths = [
            len(k) for k in citation.processed_tokens.keys()
            if citation.processed_tokens[k]
        ]
        tab_width = max(key_lengths) + 2
        print('Source: '.ljust(tab_width) + str(citation.template))
        for key, value in citation.processed_tokens.items():
            if not value:
                continue
            print(
                f"{key.replace('_', ' ').title()}: ".ljust(tab_width)
                + value
            )
        print('URL: '.ljust(tab_width) + (citation.URL or 'Unavailable'))
        
        # open the URL in a browser if applicable
        if args.browse and citation.URL:
            webbrowser.open(citation.URL)
    
    ####################################################################
    # HOST COMMAND
    ####################################################################        

    elif args.command == 'host': # host a CiteURL server
        try:
            from .web.server import serve, App
            serve(
                App(citator),
                localhost=not args.serve,
                port=args.port,
            )
        except ModuleNotFoundError:
            print(
                'Server features depend on flask and gevent. You can '
                + 'probably install them with the following command:'
            )
            print('python3 -m pip install flask gevent')
    
    ####################################################################
    # MAKEJS COMMAND
    #################################################################### 
    
    elif args.command == 'makejs':
        from .web.makejs import makejs
        output = makejs(
            citator,
            entire_page=args.entire_page or args.sources_table,
            include_sources_table=args.sources_table,
        )

        # save or print output
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
        else:
            print(output)
