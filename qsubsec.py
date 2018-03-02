#!/usr/bin/env python3

import tokens as qstokens
from sections import SectionList, Limits, CommandType
from templates import Template
from collections import OrderedDict
import sectionFormatter
import os.path
from os import remove
import logging
import argparse
import json
import subprocess
from math import floor, log10
from sys import exit, stdin, exc_info

version = '3.0a1 (2018-03-01)'

def main():
    # Create the command line interface:
    parser = argparse.ArgumentParser(description='Expand QSUB section templates')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s {0}'.format(version))
    parser.add_argument('-V', '--verbose', dest='verbosity_level', default='warning', choices=['error', 'warning', 'info', 'debug'], help='Set logging level (default warning)')
    parser.add_argument('-r', '--raise-errors', dest='raise_errors', action='store_true', default=False, help='raise full errors when processing templates')
    parser.add_argument('-i', '--input-json', dest='input_json', action='store_true', default=False, help='input JSON-formatted section data instead of template file')
    parser.add_argument('-j', '--output-json', dest='output_json', action='store_true', default=False, help='return data in JSON format')
    # Submission options:
    submission_group = parser.add_argument_group('Submission options')
    submission_group.add_argument('-f', '--sub-format', dest='submission_format', default='qsub', choices=['qsub', 'bash'], help='the submission format to use when using -s')
    submission_group.add_argument('--sub-exec', dest='submission_exec', metavar='exec', default=None, help='override the default executable to use when submitting with -s')
    submission_group.add_argument('--sub-timeout', dest='submission_timeout', metavar='sec', default=20, type=int, help='submission timeout in seconds when submitting with -s (default 20s)')
    submission_group.add_argument('-p', '--purge-logs', dest='purge_logs', action='store_true', default=False, help='purge section log files when submitting with -s')
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

    # A function to quit with an error:
    def error(msg, exit_code=1):
        log.error(msg)
        exit(exit_code)

    # A function to print an object in JSON fomat:
    def printJSON(x): print(json.dumps(x, indent='\t'))

    # Set up logging based on the verbosity level set by the command line arguments:
    log = logging.getLogger()
    log_handler = logging.StreamHandler()
    log.default_msec_format = ''
    log_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    log.setLevel(args.verbosity_level.upper())
    log.addHandler(log_handler)

    # Check for illegal option combinations:
    if (args.input_json is True) and (args.show_tokens is True): error('Can not show tokens when reading processed JSON')

    # If requested, load the sections from JSON:
    if args.input_json is True:
        log.info('reading JSON from file "{}"'.format(args.template_file))
        try: sections = SectionList.fromJSONFile(args.template_file)
        except: error('failed to read JSON section data from "{}"'.format(args.template_file))
    else:
        # Read & process the template file
        log.info('reading template file "{}"'.format(args.template_file))
    
        # Load the tokens:
        tsp = qstokens.TFFParser()
        tokens = qstokens.TokenSet()

        template = Template.fromFile(args.template_file)

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
                elif os.path.exists(t):
                    f_path = os.path.realpath(t)
                    log.info('reading tokens from file {}'.format(f_path))
                    ts_new = tsp.parse(f_path)
                else:
                    log.info('reading tokens from command line "{}"'.format(t))
                    ts_new = tsp.parseString(t)
                tokens.extend(ts_new)
            except qstokens.MissingTokenError as err: error('missing tokens "{}" in file "{}"'.format('", "'.join(err.tokens), f_path))
            except BaseException as err: error(str(err))

        # Execute the template to yield the sections:
        log.info('executing template')
        try: template.execute(tokens)
        except qstokens.MissingTokenError as err:
            if args.raise_errors is True: raise
            missing = err.tokens
            if len(missing) == 1: error('missing token {}'.format(list(missing)[0]))
            else: error('missing tokens {}'.format(', '.join(missing)))
        except qstokens.CyclicTokenDependencyError as err: error('cyclic dependencies ({})'.format(', '.join(err.tokens)))    
        except BaseException as err:
            if args.raise_errors is True: raise
            error(str(err))
    
        # Extract the section data from the template:
        sections = template.sections

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
    elif args.submission_format == 'bash': formatter = sectionFormatter.BashFormatter
    else: error('no formatter for submission format {}'.format(args.submission_format))
    log.info('submission format is {}'.format(args.submission_format))
    if args.submit is False:    
        # Print the formatted data, rather than submitting it:
        log.info('writing formatted data to stdout')
        if len(sections) > 1: log.warning('concatenating multiple sections')
        for section in sections: print(formatter.newline.join(formatter.format(section)))
    else:
        # Submit the formatted data:
        info_str = '[{{:{0}}}/{{:{0}}}]: submitted section {{}}'.format(floor(log10(len(sections))))
        submission_exec = args.submission_exec
        if submission_exec is None:
            if args.submission_format == 'qsub': submission_exec = 'qsub'
            elif args.submission_format == 'bash': submission_exec = 'bash'
            else: error('no submission executable set for format {}'.format(args.submission_format))
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
            # Attempt to open the subprocess:
            try:
                log.info('spawning subprocess "{}"'.format(' '.join(submission_exec)))
                proc = subprocess.Popen(args=submission_exec, stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
            except FileNotFoundError: error('subprocess executable "{}" not found'.format(submission_exec[0]))
            except: error('failed to spawn subprocess "{}"'.format(' '.join(submission_exec)))
            # Attempt to communicate with the subprocess:
            try:
                output_data = proc.communicate(input=section_data, timeout=args.submission_timeout)
                log.info('submitted section {} of {} ({})'.format(i + 1, len(sections), section_name))
                if output_data[0] != None: log.info('submission stdout: "{}"'.format(output_data[0].strip()))
                if output_data[1] != None: log.info('submission stderr: "{}"'.format(output_data[1].strip()))
                print(info_str.format(i + 1, len(sections), section_name))
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.communicate()
                log.warning('submission to subprocess "{}" timed out'.format(' '.join(submission_exec)))
            except:
                proc.kill()
                proc.communicate()
                log.warning('failed to submit job to subprocess "{}"'.format(' '.join(submission_exec)))
