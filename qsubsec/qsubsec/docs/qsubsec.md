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

After token replacement, section files are executed as Python code. However, several extra builtin functions are present. These are outlined below

### `section(name, description=None, check=True, log=True)`

This function adds a new section to the sections list. If present, the description is used to provide a brief overview of the section purpose.

If `check` is `True`, the resulting section will attempt to catch SIGUSR1 and SIGUSR2 messages (which are sent by SGE before a job is killed) and log a suitable message before job termination.

If `log` is `True`, section start and completion logs are written.

### limits
### options
### hold
### require
### outputFile
### errorFile
### outputs
### command
### message
### error

### __sections__
