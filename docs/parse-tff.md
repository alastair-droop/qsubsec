# The TFF Token file Parser

The `parse-tff` utility parses TFF-formatted token files. Although primarily a debugging tool, it can also simplify TFF files and standardise their formatting, as will as generating [DOT](https://graphviz.gitlab.io/_pages/doc/info/lang.html)-formatted token dependency graphs.

## Usage

~~~
usage: qsubsec.py [-h] [-v] [-V {error,warning,info,debug}] [-r] [-i] [-j]
                  [-f {qsub,bash}] [--sub-exec exec] [--sub-timeout sec] [-p]
                  [-t | -d | -c | -s]
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
                        (default 20 sec)
  -p, --purge-logs      purge section log files when submitting with -s

Output actions:
  -t, --tokens          show the tokens referred to in the template file
  -d, --describe        describe the generated sections
  -c, --commands        show the commands to be executed
  -s, --submit          submit the commands
~~~

