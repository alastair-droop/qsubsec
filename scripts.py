# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import tokens as qstokens
from sections import SectionList, Limits, CommandType
from templates import Template
from sectionSubmitter import outputSubmitterProc, outputSubmitterShell
from collections import OrderedDict
import sectionFormatter
import os.path
from os import remove
import logging
import argparse
import json
import subprocess
from math import floor, log10
from sys import exit, stdin, stdout, exc_info
import re
from signal import signal, SIGPIPE, SIG_DFL
from pyparsing import *
from urllib.parse import urlparse

# Get the version:
version = {}
with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'version.py')) as f: exec(f.read(), version)

# A function to quit with an error:
def error(log, msg, exit_code=1):
    log.error(msg)
    exit(exit_code)

# A function to set up logging:
def setupLog(verbosity):
    log = logging.getLogger()
    log_handler = logging.StreamHandler()
    log.default_msec_format = ''
    log_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    log.setLevel(verbosity.upper())
    log.addHandler(log_handler)
    return log

# A function to determine if a string should be treated as a file or a URL:
# NB: This is based on whether a URL scheme is present
def isURL(s):
    if urlparse(s).scheme != '': return True
    return False
    
def qsubsec():
    # Define the defaults:
    defaults = {'verbosity_level':'warning', 'submission_format':'qsub', 'submission_timeout':None, 'url_encoding':'UTF-8'}
    # Create the command line interface:
    parser = argparse.ArgumentParser(description='Expand QSUB section templates')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s {0}'.format(version['__version__']))
    parser.add_argument('-V', '--verbose', dest='verbosity_level', default=defaults['verbosity_level'], choices=['error', 'warning', 'info', 'debug'], help='Set logging level (default {verbosity_level})'.format(**defaults))
    parser.add_argument('-r', '--raise-errors', dest='raise_errors', action='store_true', default=False, help='raise full errors when processing templates')
    parser.add_argument('-i', '--input-json', dest='input_json', action='store_true', default=False, help='input JSON-formatted section data instead of template file')
    parser.add_argument('-j', '--output-json', dest='output_json', action='store_true', default=False, help='return data in JSON format')
    parser.add_argument('-e', '--url-encoding', dest='url_encoding', metavar='enc', default=defaults['url_encoding'], help='encoding to use when reading data from URLs (default {url_encoding})'.format(**defaults))
    # Submission options:
    submission_group = parser.add_argument_group('Submission options')
    submission_group.add_argument('-f', '--sub-format', dest='submission_format', default=defaults['submission_format'], choices=['qsub', 'bash', 'pbash', 'bsub'], help='the submission format to use when using -s (default {submission_format})'.format(**defaults))
    submission_group.add_argument('--sub-exec', dest='submission_exec', metavar='exec', default=None, help='override the default executable to use when submitting with -s')
    submission_group.add_argument('--sub-timeout', dest='submission_timeout', metavar='sec', default=defaults['submission_timeout'], type=int, help='submission timeout in seconds when submitting with -s (default {submission_timeout})'.format(**defaults))
    submission_group.add_argument('-p', '--purge-logs', dest='purge_logs', action='store_true', default=False, help='purge section log files when submitting with -s')
    submission_group.add_argument('-l', '--filter-commands', dest='filter_commands', metavar='regex', default=None, help='only include commands whose names match the regular expression regex. If regex is prefixed with ! then the regular expression is inverted')
    # Output actions:
    output_group = parser.add_argument_group('Output actions')
    output_excl = output_group.add_mutually_exclusive_group()
    output_excl.add_argument('-t', '--tokens', dest='show_tokens', action='store_true', default=False, help='show the tokens referred to in the template file')
    output_excl.add_argument('-d', '--describe', dest='show_sections', action='store_true', default=False, help='describe the generated sections')
    output_excl.add_argument('-c', '--commands', dest='show_commands', action='store_true', default=False, help='show the commands to be executed')
    output_excl.add_argument('-s', '--submit', dest='submit', action='store_true', default=False, help='submit the commands')
    # Inputs:
    parser.add_argument(metavar='template', dest='template_file', help='template file or JSON-formatted section data')
    parser.add_argument(dest='tokens', nargs='*', default=None, help='Token definitions')
    args = parser.parse_args()

    # A function to print an object in JSON fomat:
    def printJSON(x): print(json.dumps(x, indent='\t'))

    # Set up logging based on the verbosity level set by the command line arguments:
    log = setupLog(args.verbosity_level)

    # Check for illegal option combinations:
    if (args.input_json is True) and (args.show_tokens is True): error(log, 'Can not show tokens when reading processed JSON')

    # If requested, load the sections from JSON:
    if args.input_json is True:
        log.info('reading JSON from file "{}"'.format(args.template_file))
        try: sections = SectionList.fromJSONFile(args.template_file)
        except: error(log, 'failed to read JSON section data from "{}"'.format(args.template_file))
    else:
        # Read & process the template file
        log.info('reading template file "{}"'.format(args.template_file))
    
        # Load the tokens:
        tsp = qstokens.TFFParser(encoding=args.url_encoding)
        tokens = qstokens.TokenSet()
        try:
            if isURL(args.template_file):
                log.info('reading template file from URL using encoding "{}"'.format(args.url_encoding))
                template = Template.fromURL(args.template_file, encoding=args.url_encoding)
            else:
                template = Template.fromFile(args.template_file)
        except: error(log, 'failed to read template file from "{}"'.format(args.template_file))
        
        # If requested, print out the tokens in the template file
        if args.show_tokens is True:
            log.info('returning template tokens')
            template_tokens = list(template.tokens)
            if args.output_json is True: printJSON(template_tokens)
            else: print('\n'.join(template_tokens))
            exit(0)

        # Load the tokens (from multiple possible sources):
        for t in args.tokens:
            try:
                if t == '-':
                    # Read from stdin:
                    log.info('reading tokens from stdin')
                    ts_new = tsp.parseHandle(stdin)
                elif isURL(t):
                    log.info('reading tokens from URL {}'.format(t))
                    ts_new = tsp.parseURL(t)
                elif os.path.exists(t):
                    f_path = os.path.realpath(t)
                    log.info('reading tokens from file {}'.format(f_path))
                    ts_new = tsp.parse(f_path)
                else:
                    log.info('reading tokens from command line "{}"'.format(t))
                    ts_new = tsp.parseString(t)
                tokens.extend(ts_new)
            except qstokens.MissingTokenError as err: error(log, 'missing tokens "{}" in file "{}"'.format('", "'.join(err.tokens), f_path))
            except BaseException as err: error(log, str(err))

        # Execute the template to yield the sections:
        log.info('executing template')
        try: template.execute(tokens)
        except qstokens.MissingTokenError as err:
            if args.raise_errors is True: raise
            missing = err.tokens
            if len(missing) == 1: error(log, 'missing token {}'.format(list(missing)[0]))
            else: error(log, 'missing tokens {}'.format(', '.join(missing)))
        except qstokens.CyclicTokenDependencyError as err: error(log, 'cyclic dependencies ({})'.format(', '.join(err.tokens)))    
        except BaseException as err:
            if args.raise_errors is True: raise
            error(log, str(err))
    
        # Extract the section data from the template:
        sections = template.sections

    # Limit to matching commands:
    if args.filter_commands is not None:
        # compile the regular expression:
        try:
            if args.filter_commands.startswith('!'):
                args.filter_commands = args.filter_commands.lstrip('!')
                log.info('inverting regular expression "{}"'.format(args.filter_commands))
                invert = True
            else: invert = False
            log.info('filtering commands with regular expression "{}"'.format(args.filter_commands))
            command_re = re.compile(args.filter_commands)
        except: error(log, 'failed to parse the regular expression ({})'.format(args.filter_commands))
        # Iterate through all commands (in reverse order per section) and remove those that do not match:
        for section in sections:
            for command_i in reversed(range(len(section.commands))):
                command_name = section.commands[command_i].name
                match = command_re.match(command_name)
                # if there is a match, then include them:
                if ((match is None) and (invert is True)) or ((match is not None) and (invert is False)):
                    log.debug('including matching command "{}"'.format(command_name))
                else:
                    log.debug('excluding non-matching command "{}"'.format(command_name))
                    del(section.commands[command_i])

    # If requested, print out the section descriptions:
    if args.show_sections is True:
        log.info('returning section descriptions')
        section_data = []
        for section in sections:
            s = OrderedDict()
            s['name'] = section.name
            s['description'] = section.description
            section_data.append(s)
        if args.output_json is True: printJSON(section_data)
        else:
            name_len = 0
            for i in section_data: name_len = max(name_len, len(i['name']))
            print('\n'.join(['{{name:{}}}\t{{description}}'.format(name_len).format(**i) for i in section_data]))
        exit(0)

    # If requested, print out the commands:
    if args.show_commands is True:
        log.info('returning commands')
        for section in sections:
            for command in section.commands:
                if command.cmdtype != CommandType.command: continue
                print('{} :: {}:\t{}'.format(section.name, command.name, command.command))
        exit(0)

    # If requested, print out the commands in JSON format:
    if args.output_json is True:
        log.info('returning JSON data')
        print(sections.asJSON(indent='\t'))
        exit(0)
    
    # Process the commands through the specified output formatter:
    if args.submission_format == 'qsub': formatter = sectionFormatter.QSUBFormatter
    elif args.submission_format == 'bsub': formatter = sectionFormatter.LSFFormatter
    elif args.submission_format == 'bash': formatter = sectionFormatter.BashFormatter
    elif args.submission_format == 'pbash': formatter = sectionFormatter.BashFormatter    
    else: error(log, 'no formatter for submission format {}'.format(args.submission_format))
    log.info('submission format is {}'.format(args.submission_format))
    if args.submit is False:    
        # Print the formatted data, rather than submitting it:
        log.info('writing formatted data to stdout')
        if len(sections) > 1: log.warning('concatenating multiple sections')
        for section in sections: print(formatter.newline.join(formatter.format(section)))
    else:
        # Submit the formatted data:
        info_str = '[{{:{0}}}/{{:{0}}}]: submitting section {{}}'.format(floor(log10(len(sections))))
        submission_exec = args.submission_exec
        if submission_exec is None:
            if args.submission_format == 'qsub': submission_exec = 'qsub'
            elif args.submission_format == 'bash': submission_exec = 'bash'
            elif args.submission_format == 'pbash': submission_exec = 'bash'
            else: error(log, 'no submission executable set for format {}'.format(args.submission_format))
        # Determine how to submit:
        if args.submission_format == 'qsub': submission_method = outputSubmitterProc
        elif args.submission_format == 'bash': submission_method = outputSubmitterProc
        elif args.submission_format == 'pbash': submission_method = outputSubmitterShell
        else: submission_method = outputSubmitterProc
        log.info('submitting {} formatted sections using executable "{}"'.format(len(sections), submission_exec))
        submission_exec = submission_exec.split()
        for i in range(len(sections)):
            section_data = formatter.newline.join(formatter.format(sections[i]))
            section_name = sections[i].name
            if args.purge_logs is True:
                sec_files = OrderedDict()
                sec_files['output'] = sections[i].outfile.getFilename(section_name)
                sec_files['error'] = sections[i].errfile.getFilename(section_name)
                for file_type in sec_files.keys():
                    try:
                        log.info('purging section {} file "{}"'.format(file_type, sec_files[file_type]))
                        remove(sec_files[file_type])
                    except FileNotFoundError: pass
                    except: log.warning('failed to purge section {} file "{}"'.format(file_type, sec_files[file_type]))
            #Attempt to spawn the subprocess:
            try:
                print(info_str.format(i + 1, len(sections), section_name), file=stdout)
                stdout.flush()
                submission_method.spawn(proc_exec=submission_exec, data=section_data, timeout=args.submission_timeout)
            except Exception as err: error(log, 'failed to submit job "{}"'.format(' '.join(submission_exec)))

def parseTFF():
    # Define the defaults:
    defaults = {'verbosity_level':'warning', 'output_format':'TFF', 'url_encoding':'UTF-8'}
    # Create the command line interface:
    parser = argparse.ArgumentParser(description='Parse qsubsec token TFF files')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s {0}'.format(version['__version__']))
    parser.add_argument('-V', '--verbose', dest='verbosity_level', default=defaults['verbosity_level'], choices=['error', 'warning', 'info', 'debug'], help='Set logging level (default {verbosity_level})'.format(**defaults))
    parser.add_argument('-o', '--output-format', dest='output_format', choices={'JSON', 'TFF', 'dict'}, default=defaults['output_format'], help='output format for single resolved token sets (default {output_format})'.format(**defaults))
    parser.add_argument('-e', '--url-encoding', dest='url_encoding', metavar='enc', default=defaults['url_encoding'], help='encoding to use when reading data from URLs (default {url_encoding})'.format(**defaults))
    output_types = parser.add_mutually_exclusive_group(required=False)
    output_types.add_argument('-q', '--quiet', dest='quiet', action='store_true', default=False, help='do not print output')
    output_types.add_argument('-a', '--print-all', dest='print_all', action='store_true', default=False, help='output multiple resolved token sets in long format')
    output_types.add_argument('-i', '--print-input', dest='print_input', action='store_true', default=False, help='output combined parsed input before resolution')
    output_types.add_argument('-g', '--print-graph', dest='print_graph', action='store_true', default=False, help='output dependency graph in DOT format')
    output_types.add_argument('-s', '--string', dest='parse_string', metavar='str', action='append', default=[], help='input TFF string(s) to parse')
    parser.add_argument(metavar='file', dest='input_files', nargs='*', default=[], help='TFF input(s) to parse')
    args = parser.parse_args()
    
    # Handle broken pipes:
    signal(SIGPIPE, SIG_DFL) 
    
    # A function to print a single token set in long format:
    def longFormat(x):
        if args.output_format == 'JSON': return x.asJSON()
        if args.output_format == 'dict': return x.asDict()
        return x.asTFF()

    # Set up logging based on the verbosity level set by the command line arguments:
    log = setupLog(args.verbosity_level)

    # Initialise the TFF parser:
    tsp = qstokens.TFFParser(encoding=args.url_encoding)
    ts = qstokens.TokenSet()

    # Parse input source in turn:
    for t in args.input_files:
        try:
            if t == '-':
                # Read from stdin:
                log.info('reading tokens from stdin')
                ts_new = tsp.parseHandle(stdin)
            elif isURL(t):
                log.info('reading tokens from URL {}'.format(t))
                ts_new = tsp.parseURL(t)
                log.info('done reading URL') # REWMOVE THIS!
            elif os.path.exists(t):
                f_path = os.path.realpath(t)
                log.info('reading tokens from file {}'.format(f_path))
                ts_new = tsp.parse(f_path)
            else:
                log.info('reading tokens from command line "{}"'.format(t))
                ts_new = tsp.parseString(t)
            ts.extend(ts_new)
        except qstokens.MissingTokenError as err: error(log, 'missing tokens "{}" in file "{}"'.format('", "'.join(err.tokens), f_path))
        except BaseException as err: error(log, str(err))

    # Parse a specific string, if requested:
    for parse_string in args.parse_string:
        log.info('parsing string "{}"'.format(parse_string))
        try:
            ts_new = tsp.parseString(parse_string)
            ts.extend(ts_new)
        except qstokens.CyclicTokenDependencyError as err: error(log, 'cyclic dependencies: "{}"'.format('", "'.join(err.tokens)))
        except qstokens.MissingTokenError as err: error(log, 'missing tokens "{}"'.format('", "'.join(err.tokens)))
        except BaseException as err: error(log, str(err))

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
    except qstokens.CyclicTokenDependencyError as err: error(log, 'cyclic dependencies: "{}"'.format('", "'.join(err.tokens)))
    except qstokens.MissingTokenError as err: error(log, 'missing tokens "{}"'.format('", "'.join(err.tokens)))
    except BaseException as err: error(log, str(err))
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

def updateTemplate():
    # Create the command line interface:
    parser = argparse.ArgumentParser(description='Update qsubsec2 template files to qsubsec3 format')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s {0}'.format(version['__version__']))
    parser.add_argument('-V', '--verbose', dest='verbosity_level', default='warning', choices=['error', 'warning', 'info', 'debug'], help='Set logging level (default warning)')
    parser.add_argument(metavar='template', dest='template_file', default='-', help='template file to update')
    args = parser.parse_args()
    
    # Handle broken pipes:
    signal(SIGPIPE, SIG_DFL) 
    
    # Set up logging based on the verbosity level set by the command line arguments:
    log = setupLog(args.verbosity_level)
        
    # Open the old template file:
    try:
        if args.template_file == '-':
            # Read from stdin:
            log.info('reading template from stdin')
            template = stdin
        else:
            log.info('reading template from file {}'.format(args.template_file))
            template = open(args.template_file, 'r')    
    except: error(log, 'failed to open template file {}'.format(args.template_file))
    
    # Define the replacement regular expressions:
    limits_re = re.compile('^(.*)limits\((.*)\)(.*)$')
    options_re = re.compile('^(.*)options\(\[(.*)\]\)(.*)$')
    requirement_re = re.compile('^(?P<pre>.*)require\((?P<req>(?P<qa>[\'\"])(?:.*)(?P=qa))\s*,\s*(?P<type>(?P<qb>[\'\"])(?:.*)(?P=qb))\)(?P<post>.*)$')
    
    #Iterate through the old template file:
    for line in template.readlines():
        # Update the limits:
        match = limits_re.match(line)
        if match != None:
            log.debug('updating limits "{}"'.format(match.group(0)))
            res = match.group(2)
            for o, n in [('time', 'h_rt'), ('vmem', 'h_vmem')]:
                res = res.replace('{}='.format(o), '{}='.format(n))
            print('{}limits({}){}'.format(match.group(1), res, match.group(3)))
            continue
        # Update the options:
        match = options_re.match(line)
        if match != None:
            log.debug('updating options "{}"'.format(match.group(0)))
            print('{}options({}){}'.format(match.group(1), match.group(2), match.group(3)))
            continue
        #Update the requirments:
        match = requirement_re.match(line)
        if match != None:
            log.debug('updating requirement "{}"'.format(match.group(0)))
            res = match.groupdict()
            res['type'] = res['type'].upper()
            print('{pre}require({req}, {type}){post}'.format(**res))
            continue
        # Line does not match, so print the line back:
        print(line, end='')
