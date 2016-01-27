Introduction
============

Qsubsec is a template language for generating script files for submission using the [SGE grid system](https://arc.liv.ac.uk/trac/SGE). By using this system, you can separate the logic of your qsub jobs from the data required for a specific run.

Requirements
============

* Python >= 3.3
* The argparse library (this is usually bundled with Python, but can be installed from [pypi](https://pypi.python.org/pypi/argparse) using `pip install argparse`)

Although qsubsec can be run on most machines, the qsub executable must be available and functional for automatic submission to work (using the `-s` argument).

Licence
=======

These tools are released under the [GNU General Public License version 3](http://www.gnu.org/licenses/gpl.html).

Usage
=====

    qsubsec [-h] [-v] [-w] [-e QSUB_EXEC] [-i ITERATED_TOKENS] [-d | -t | -c | -s] <filename>

    positional arguments:
      <filename>                                       The QSUB template file or URL

    optional arguments:
      -h, --help                                       Show the script help message and exit
      -v, --version                                    Show the program's version number and exit
      -w, --debug                                      Show extended Python debugging information
      -e QSUB_EXEC, --executable                       QSUB_EXEC remote qsub executable
      -i ITERATED_TOKENS, --iterate ITERATED_TOKENS    Comma-separated list or file of iterated values for token
      -d, --description                                Show the QSUB template description and exit
      -t, --tokens                                     Show the QSUB template tokens and exit
      -c, --show-code                                  Print the parsed QSUB section generator code and exit
      -s, --submit                                     Submit processed job to qsub

Reading Arguments from file
---------------------------

Basic usage simply requires the name of a template file and the values of any tokens in the form of `TOKEN=VALUE`. If the specified filename Sometimes (especially when there are many tokens to specify, or if a set of templates share the same token values) it is useful to keep some or all of the token definitions in a file rather than having to specify them all on the command line. In this case, a filename to process (one command argument per line) can be specified in the form `@<filename>`.

Iterated Tokens
---------------

Often, a set of related jobs must be submitted with different token values. For example, running an analysis for different parameter values, or processing multiple input files. Qsubsec can generate multiple submission scripts from a single template file using *iterated tokens* (using the form `-iTOKEN=VALUES`). Values for iterated tokens can either be provided as a comma-separated list, or as a file name. If no comma is present in the iterated token value provided, the value is processed as a file name. If reading from a file, empty lines, and lines whose first non-whitespace character is `#` are ignored. All combinations of token values are submitted as individual scripts. For example, a script with two tokens (`A` and `B`) submitted with the options `-iA=1,2,3 B=1` will yield three jobs. However, the same script submitted with the options `-iA=1,2,3 -iB=1,2,3` will yield 9 jobs.

Language Syntax
===============

Tokens
------
Tokens are very simple text placeholders. In templates, tokens are defined as an uppercase string surrounded by curly braces. Whitespace is not allowed in template names.

Commands
--------

**`section(name, description=None)`**  
Define the section. The name is character field that is used to identify a qsub job (using the `-N` option). If provided, the description is used to identify the template. Only a single section is possible per section file; only the last processed section command is used.

**`limits(time, vmem=None, nodes=None)`**  
Define the limits imposed by qsub on the submitted job. The time constraint is in the form ‘hh:mm:ss’, and is mandatory. The vmem constraint is a string defining the memory limit for the job, in the format speed by qsub (e.g. “1G”). The nodes constraint asks qsub for a whole node, and thus overrides the vmem constraint. The nodes parameter is an integer. **NB:** nodes is not a limit universal to all grid implementations. 

**`option(switch, argument=None, value=None)`**  
Pass further options to qsub. Options are in the form “-switch” (e.g. `-V`) “-switch argument” (e.g. `-m be`), or “-switch argument=value” (e.g. `-l cputype=amd`). Switches should be specified without the initial hyphen. In all cases, the arguments and values are treated as text.

**`options(options)`**  
Pass a list of options as simple strings. 

**`hold(hold_id)`**  
Add a hold constraint to the job. If provided, the hold_id is treated as a job ID, and the submitted job will wait until there is no job with the specified name in the queue before running.

**`require(value, flag)`**  
Add requirement checks to a qsub script. Requirements are implemented as blocks of bash code within the qsub script, so are checked once the job is running rather than at submission time. Possible flag strings are are:

    path_abse         The specified path must be absent  
    path_present      The specified path must be present  
    path_readable     The specified path must be readable  
    path_writable     The specified path must be writable  
    env_set           The specified environment variable must be set  
    env_unset         The specified environment variable must not be set  

**`output(base, file=None)`**  
Set the job output log file. By default, the output log is created in the current directory, and is named “output-N.log” where N is replaced by the name of the job.

**`error(base, file=None)`**  
Set the job error log file. By default, the error log is created in the current directory, and is named “error-N.log” where N is replaced by the name of the job.

**`command(cmd, name=None, test=True, log=True)`**  
Adds a command to the script. The command is specified by cmd. If name is specified, the command is named in the output logs, otherwise commands are given a number. If test is True, then script will test for successful completion of the command and generate an error if it failed. If log is True, logging text is produced in the output file.

Examples
========

The examples directory contains several example scripts.

Other Tools
===========
* `qslogs` is a wrapper script to view multiple qsub log files
* `qsjobs` is a wrapper around the `--xml` optupt generated by `qstat` to provide more intuitive output.

