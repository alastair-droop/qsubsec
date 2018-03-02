# QSub Section File (qsubsec) Format

Qsub section template files are Python-based templates that are processed by the `qsubsec` command to generate code sections that can be submitted for execution (for example through the SGE scheduler). Before processing, template files are checked for token placeholders and these are filled in. The resulting Python code is then executed to generate a set of sections.

The stages in template processing are:

1. The template file and token file(s) are read;
2. Any token placeholders found in the template file are filled in using the tokens file(s) read;
3. The resulting Python code is executed to yield a set of sections;
4. Each section is output in turn

Token Files define the placeholder tokens used to generate qsubsec templates. The Token File Format (`TFF`) is a small language used to define a set of tokens.

**NB:** As the qsubsec engine uses braces (`{` and `}`) to define tokens, these symbols are not allowed in the file apart from when specifying tokens. For example, the dictionary definitions like `x={}` are not possible. Instead, the long-hand method `x=dict()` is required.

**NB:** As token substitution occurs before the template is executed, the system will process the entire file (including comments) for tokens. Thus, tokens referenced only in comments are still required.

## Token Placeholders

Tokens placeholders are used to specify where the value of a token is to be filled in. Token placeholders are specified using the token name in parentheses (for example `{NAME}`).

## Section File Format

After token replacement, section files are executed as Python code. However, several extra builtin functions are provided. These are outlined below.


### `section(name, description=None, check=True, log=True)`

This function adds a new section to the sections list. All subsequent functions that modify a section will act upon the last section created.

* If present, the description is used to provide a brief overview of the section purpose.
* If `check` is `True`, the resulting section will attempt to catch SIGUSR1 and SIGUSR2 messages (which are sent by SGE before a job is killed) and log a suitable message before job termination.
* If `log` is `True`, section start and completion logs are written.

~~~python
section("PRINT_{VARIABLE}", "Outputs the value of the {VARIABLE} environment variable to log", check=False, log=False)
~~~

### `limits(**kwargs)`

This function defines limits that are passed to the scheduler at submission time. Limits are specified as keyword-defined strings. For SGE, a minimum of time and memory specifications must be given. For example the code below will request a maximum run time of one minute and a maximum vmem of 10Mb. The limit types and values are neither enforced or checked by `qsubsec`. When outputting bash, the limits are ignored.

~~~python
limits(time="00:01:00", vmem="10M")
~~~

### `options(*args)`

This function sets the options that are passed to the scheduler at submission time. Options are specified as strings. Options are not checked by `qsubsec`. The preceding hyphen should be omitted.

~~~python
options("V", "cwd", "notify")
~~~

### `hold(*args)`

This function adds holds to the current section, ensuring that when submitted via a job scheduler that the job will not start before the previous job IDs. Job IDs or names are provided as strings. For example, the code below will ensure that the current section will not start before the job with name `PRIOR_JOB`:

~~~python
hold("PRIOR_JOB")
~~~

**NB:**

1. SGE does not test for successful completion of a preceding job; just that it is no longer running. Thus, jobs should check their inputs (using `require`) rather than relying solely on `hold`.
2. When submitting to bash, holds are ignored.

### `require(requirement, requirement_type)`

This function tests for specific requirements, and stops the job (with an appropriate message to the error file) if they are not met. The requirement types possible are:

* `"PATH_ABSENT"`: Ensures that the given path is not present
* `"PATH_PRESENT"`: Ensures that the given path is present
* `"PATH_READABLE"`: Ensures that the given path is readable
* `"PATH_WRITABLE"`: Ensures that the given path is writable
* `"ENV_SET"`: Ensures that the given environment variable is set
* `"ENV_UNSET"`: Ensures that the given environment variable is not set

For example, the code below will yield an error and stop the job if the environment variable `$NCPU` is unset or if the file `/path/to/input.txt` is readable:

~~~python
require("NCPU", "ENV_SET")
require("/path/to/input.txt", "PATH_READABLE")
~~~

### `outputFile(path, name=None)` & `errorFile(path, name=None)`

These functions set the output and error log files.

* The `path` argument sets the log file directory that the files will be written to.
* If specified and not `None`, the `name` argument will set the file name. If `None`, then the file name will be set by the name of the section. The default naming strategy is `output-{NAME}.log` (for output files) and `error-{NAME}.log` for error files, where `{NAME}` is the job ID as specified in the section function.

The code below sets the error log to the directory `/logs` with the default file name, and the output log to go into `/output/output.txt`:

~~~python
outputFile("/output", "output.txt")
errorFile("/logs")
~~~

### `outputs(path)`

This function sets both the output and error logs to write to the specified directory with their default file names.

* The `path` argument sets the log file directory that both the output and error files will be written to.

For example, the code below writes both logs to their default names in the `/logs` directory:

~~~python
outputs("/logs")
~~~

### `command(cmd, name=None, test=True, log=True)`

This function adds an executable command to the section.

* `cmd` specifies the command to run as a string. The command should be specified exactly as it would be run in the terminal. No argument checking is performed.
* The `name` argument specifies a name for the command. This is used when generating output log messages. If not specified, commands given default names.
* If specified, the `test` argument causes the job to check the exit code of the function and to stop the job (with a suitable error) if the command did not successfully complete. This checking is performed simply using bash exit code checking.
* If specified, the `log` argument will cause the job to print start and completion messages to the output log for the command.

For example, the code below will write the value of the `$PATH` environment variable to a file called `path.txt`:

~~~python
command("echo $PATH > path.txt", name="write_path")
~~~

The following code will be submitted:

~~~
echo "[`date`]: command write_path started"
echo $PATH > path.txt || { echo "[`date`]: command write_path failed"; exit 1; }
echo "[`date`]: command write_path completed"
~~~

If the command was submitted with `test=False`, the submitted code would be:

~~~
echo "[`date`]: command write_path started"
echo $PATH > path.txt
echo "[`date`]: command write_path completed"
~~~

### `message(message)` & `error(message)`

These two functions write a message to the output or error logs respectively.

For example, the following code writes the value of the $USER to the log:

~~~python
message("The current user is $USER")
~~~

## Global Variables

When processing qsubsec files, the list of defined sections and tokens are available as `__sections__` and `__tokens__` respectively. This allows template files to use (and modify) these on the fly.

## Examples

### Example 1

The following section script writes the value of the PATH variable to its output log file:

~~~python
section("PRINT_PATH", "Outputs the value of the PATH environment variable to log")
limits(time="00:00:10", vmem="10M")
message('PATH is "$PATH"')
~~~

### Example 2

The following script generalises example 1 to use a token to specify the environment variable to show:

~~~python
# example-2.qsubsec
section("PRINT_{VARIABLE}", "Outputs the value of the {VARIABLE} environment variable to log", check=False, log=False)
limits(time="00:00:10", vmem="10M")
message('{VARIABLE} is "${VARIABLE}"')
~~~

