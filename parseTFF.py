#!/usr/bin/env python3

import tokens
import os.path
import logging
import argparse
from sys import exit, stdin

version = '3.0a1 (2018-03-01)'

def main():
    # Create the command line interface:
    parser = argparse.ArgumentParser(description='Parse qsubsec token TFF files')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s {0}'.format(version))
    parser.add_argument('-V', '--verbose', dest='verbosity_level', default='warning', choices=['error', 'warning', 'info', 'debug'], help='Set logging level (default warning)')
    parser.add_argument('-o', '--output-format', dest='output_format', choices={'JSON', 'TFF', 'dict'}, default='TFF', help='output format for single resolved token sets')
    output_types = parser.add_mutually_exclusive_group(required=False)
    output_types.add_argument('-q', '--quiet', dest='quiet', action='store_true', default=False, help='do not print output')
    output_types.add_argument('-a', '--print-all', dest='print_all', action='store_true', default=False, help='output multiple resolved token sets in long format')
    output_types.add_argument('-i', '--print-input', dest='print_input', action='store_true', default=False, help='output combined parsed input before resolution')
    output_types.add_argument('-g', '--print-graph', dest='print_graph', action='store_true', default=False, help='output dependency graph in DOT format')
    output_types.add_argument('-s', '--string', dest='parse_string', metavar='str', default=None, help='parse a specific string')
    parser.add_argument(metavar='file', dest='input_files', nargs='*', default=[], help='input TFF file(s) to parse')
    args = parser.parse_args()

    # A function to quit with an error:
    def error(msg, exit_code=1):
        log.error(msg)
        exit(exit_code)

    # A function to print a single token set in long format:
    def longFormat(x):
        if args.output_format == 'JSON': return x.asJSON()
        if args.output_format == 'dict': return x.asDict()
        return x.asTFF()

    # Set up logging based on the verbosity level set by the command line arguments:
    log = logging.getLogger()
    log_handler = logging.StreamHandler()
    log.default_msec_format = ''
    log_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    log.setLevel(args.verbosity_level.upper())
    log.addHandler(log_handler)

    # Initialise the TFF parser:
    tsp = tokens.TFFParser()
    ts = tokens.TokenSet()

    # Run through each input file in turn:
    for f in args.input_files:
        if f == '-':
            # Read from stdin:
            f_path = stdin
            log.info('processing stdin')
        else:
            f_path = os.path.realpath(f)
            log.info('processing input file {}'.format(f_path))
        # Parse the file:
        try:
            ts_new = tsp.parse(f_path)
            ts.extend(ts_new)
        except tokens.MissingTokenError as err: error('missing tokens "{}" in file "{}"'.format('", "'.join(err.tokens), f_path))
        except BaseException as err: error(str(err))

    # Parse a specific string, if requested:
    if args.parse_string is not None:
        log.info('parsing string "{}"'.format(args.parse_string))
        try:
            ts_new = tsp.parseString(args.parse_string)
            ts.extend(ts_new)
        except tokens.CyclicTokenDependencyError as err: error('cyclic dependencies: "{}"'.format('", "'.join(err.tokens)))
        except tokens.MissingTokenError as err: error('missing tokens "{}"'.format('", "'.join(err.tokens)))
        except BaseException as err: error(str(err))

    # Print out the dependency graph, if requested:
    if args.print_graph is True:
        log.info('generating dependency graph')
        print(ts.asDot())
        exit(0)

    # Print out the complete input, if requested:
    if args.print_input is True:
        log.info('generating input token data')
        print(longFormat(ts))
        exit(0)

    # Resolve the complete token set:
    log.info('resolving tokens')
    try: res = ts.resolve()
    except tokens.CyclicTokenDependencyError as err: error('cyclic dependencies: "{}"'.format('", "'.join(err.tokens)))
    except tokens.MissingTokenError as err: error('missing tokens "{}"'.format('", "'.join(err.tokens)))
    except BaseException as err: error(str(err))
    res_n = len(res)

    # If quiet was requested, simply exit at this stage, as there were no errors:
    if args.quiet is True: exit(0)

    # If a single token set is generated, print it in long-hand format:
    if res_n == 1:
        log.info('1 resolved token set generated')
        print(longFormat(res[0]))
    else:
        log.info(format('{} resolved token sets generated:'.format(res_n)))
        for i in range(res_n):
            if args.print_all is True: print(longFormat(res[i]))
            else: print('[{}]: {}'.format(i, res[i].asDict()))

main()