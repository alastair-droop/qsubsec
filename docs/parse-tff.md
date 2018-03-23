# The TFF Token file Parser

The `parse-tff` utility parses TFF-formatted token files. Although primarily a debugging tool, it can also simplify TFF files and standardise their formatting, as will as generating [DOT](https://graphviz.gitlab.io/_pages/doc/info/lang.html)-formatted token dependency graphs.

## Usage

~~~
usage: parse-tff [-h] [-v] [-V {error,warning,info,debug}]
                 [-o {TFF,JSON,dict}] [-q | -a | -i | -g | -s str]
                 [file [file ...]]

Parse qsubsec token TFF files

positional arguments:
  file                  input TFF file(s) to parse

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -V {error,warning,info,debug}, --verbose {error,warning,info,debug}
                        Set logging level (default warning)
  -o {TFF,JSON,dict}, --output-format {TFF,JSON,dict}
                        output format for single resolved token sets
  -q, --quiet           do not print output
  -a, --print-all       output multiple resolved token sets in long format
  -i, --print-input     output combined parsed input before resolution
  -g, --print-graph     output dependency graph in DOT format
  -s str, --string str  parse a specific string
~~~

