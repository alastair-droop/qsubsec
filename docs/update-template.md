# Update Template Files

The `update-template` utility parses updates qsubsec2 formatted template files into the new qsubsec3 format. The modifications made are:

* `limits` time and vmem keywords are updated;
* `options` now takes individual keyword-value pairs, not a list; and
* `requirement` types are now uppercase.

## Usage

~~~
usage: update-template [-h] [-v] [-V {error,warning,info,debug}] template

Update qsubsec2 template files to qsubsec3 format

positional arguments:
  template              template file to update

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -V {error,warning,info,debug}, --verbose {error,warning,info,debug}
                        Set logging level (default warning)
~~~

