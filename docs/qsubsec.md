# The qsubsec Template Formatter

The `qsubsec` utility processes qsubsec-formatted template files to generate code sections that can be submitted for execution (for example through the SGE scheduler). Before processing, template files are checked for token placeholders and these are filled in. The resulting Python code is then executed to generate a set of sections.

The stages in template processing are:

1. The template file and token file(s) are read;
2. Any token placeholders found in the template file are filled in using the tokens file(s) read;
3. The resulting Python code is executed to yield a set of sections;
4. Each section is output in turn

`qsubsec` reads either a template file (and optionally a set of tokens), or a processed job file in JSON format.

If either of the template file or token files start with a well-formed URL scheme (for example `https://`), they will be treated as URLs. **NB**: Currently, URL processing is very  limited.

## Submission Formats

When using the `-s` flag to submit jobs, qsubsec will attempt to submit the generated template code using the specified format (specified using `-f`). Currently, there are three possible formats:

### `-f qsub`

When using `-f qsub` the generated code will be passed to `qsub`.

### `-f bash`

When using `-f bash`, each generated section is passed to a separate background shell subprocesses. `qsubsec` will not wait until one section completes before submitting the next. Thus, all sections will run concurrently. This allows for rapid execution of multiple templates, but runs the danger of filling up the local machine's resources.

**NB**: the entire command is passed to bash as a single command string.

### `-f sbash`

When using `-f sbash`, each generated section is run in the shell, but unlike `-f bash` then are run sequentially.

## Usage

~~~
usage: qsubsec [-h] [-v] [-V {error,warning,info,debug}] [-r] [-i] [-j]
               [-e enc] [-f {qsub,bash}] [--sub-exec exec] [--sub-timeout sec] [-p]
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
  -e enc, --url-encoding enc
                        encoding to use when reading data from URLs (default
                        UTF-8)

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

