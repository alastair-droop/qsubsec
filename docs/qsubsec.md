# The qsubsec Template Formatter

The `qsubsec` utility processes qsubsec-formatted template files to generate code sections that can be submitted for execution (for example through the SGE scheduler). Before processing, template files are checked for token placeholders and these are filled in. The resulting Python code is then executed to generate a set of sections.

The stages in template processing are:

1. The template file and token file(s) are read;
2. Any token placeholders found in the template file are filled in using the tokens file(s) read;
3. The resulting Python code is executed to yield a set of sections;
4. Each section is output in turn

`qsubsec` reads either a template file (and optionally a set of tokens), or a processed job file in JSON format.

## Usage

~~~
usage: qsubsec [-h] [-v] [-V {error,warning,info,debug}] [-r] [-i] [-j]
               [-f {qsub,bash}] [--sub-exec exec] [--sub-timeout sec] [-p]
               [-l regex] [-t | -d | -c | -s]
               template [tokens [tokens ...]]

Expand QSUB section templates

positional arguments:
  template              template file or JSON-formatted section data
  tokens                Token definitions

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -V {error,warning,info,debug}, --verbose {error,warning,info,debug}
                        Set logging level (default warning)
  -r, --raise-errors    raise full errors when processing templates
  -i, --input-json      input JSON-formatted section data instead of template
                        file
  -j, --output-json     return data in JSON format

Submission options:
  -f {qsub,bash}, --sub-format {qsub,bash}
                        the submission format to use when using -s
  --sub-exec exec       override the default executable to use when submitting
                        with -s
  --sub-timeout sec     submission timeout in seconds when submitting with -s
                        (default none)
  -p, --purge-logs      purge section log files when submitting with -s
  -l regex, --filter-commands regex
                        only include commands whose names match the regular
                        expression regex. If regex is prefixed with ! then the
                        regular expression is inverted

Output actions:
  -t, --tokens          show the tokens referred to in the template file
  -d, --describe        describe the generated sections
  -c, --commands        show the commands to be executed
  -s, --submit          submit the commands
~~~

