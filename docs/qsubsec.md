# QSub Section File (qsubsec) Format

Qsub section template files are Python-based templates that are processed by the `qsubsec` command to generate code sections that can be submitted for execution (for example through the SGE scheduler). Before processing, template files are checked for token placeholders and these are filled in. The resulting Python code is then executed to generate a set of sections.

The stages in template processing are:

1. The template file and token file(s) are read;
2. Any token placeholders found in the template file are filled in using the tokens file(s) read;
3. The resulting Python code is executed to yield a set of sections;
4. Each section is output in turn

Token Files define the placeholder tokens used to generate qsubsec templates. The Token File Format (`TFF`) is a small language used to define a set of tokens.

## Token Placeholders

Tokens placeholders are used to specify where the value of a token is to be filled in. Token placeholders are specified using the token name in parentheses (for example `{NAME}`).

## Section File Format

After token replacement, section files are executed as Python code. However, several extra builtin functions are provided. These are outlined below.


**`section(name, description=None, check=True, log=True)`**

This function adds a new section to the sections list. All subsequent functions that modify a section will act upon the last section created.

* If present, the description is used to provide a brief overview of the section purpose.
* If `check` is `True`, the resulting section will attempt to catch SIGUSR1 and SIGUSR2 messages (which are sent by SGE before a job is killed) and log a suitable message before job termination.
* If `log` is `True`, section start and completion logs are written.

~~~python
section("PRINT_{VARIABLE}", "Outputs the value of the {VARIABLE} environment variable to log", check=False, log=False)
~~~

**`limits(**kwargs)`**

This function defines limits that are passed to the scheduler at submission time. Limits are specified as keyword-defined strings. For SGE, a minimum of time and memory specifications must be given. For example the code below will request a maximum run time of one minute and a maximum vmem of 10Mb. The limit types and values are neither enforced or checked by `qsubsec`. When outputting bash, the limits are ignored.

~~~python
limits(time='00:01:00', vmem='10M')
~~~

**`options(*args)`**

This function sets the options that are passed to the scheduler at submission time. Options are specified as strings. Options are not checked by `qsubsec`. The preceding hyphen should be omitted.

~~~python
options('V', 'cwd', 'notify')
~~~

### hold
### require
### outputFile
### errorFile
### outputs
### command
### message
### error

### __sections__
### __tokens__

## Example 1

The following section script writes the value of the PATH variable to its output log file.

~~~python
# example-1.qsubsec
section('PRINT_PATH', 'Outputs the value of the PATH environment variable to log')
limits(time='00:00:10', vmem='10M')
message('PATH is "$PATH"')
~~~

## Example 2

The following script generalises example 1 to use a token to specify the environment variable to show.

~~~python
# example-2.qsubsec
section('PRINT_{VARIABLE}', 'Outputs the value of the {VARIABLE} environment variable to log', check=False, log=False)
limits(time='00:00:10', vmem='10M')
message('{VARIABLE} is "${VARIABLE}"')
~~~


