# Token File Format (TFF)

TFF files describe the tokens used to process a qsubsec file.

# Basic Token Definition

Tokens are defined using the follwoing syntax:

~~~
TOKEN = VALUE
~~~

If necessary, both the token name and value can be quoted (with either single or double quotes):

~~~
"TOKEN1" = "VALUE"
'TOKEN2' = "VALUE"
~~~

If unquoted, token names and values must contain only letters, numbers and underscores. Quoted names and values can contain any printable characters.

Any token name or value can contain a placeholder as long as the placeholder resolves to a valid token name by the time it is processed. For example, the following is valid:

~~~
KEY=A
"TOKEN_{KEY}"="Hello"
~~~

This will result in two tokens: `KEY`="A", and `TOKEN_A`="Hello". However, if the token `KEY` is not defined before it is needed, the assignment will fail:

~~~
# Invalid:
"TOKEN_{KEY}"="Hello"
KEY=A
~~~

# Multiple Token Values

Tokens with multipole values can be defined as:

~~~
TOKEN = VALUE1, VALUE2, VALUE3
~~~

As above quotes are optional.

# Including other TFF files

A new TFF file can be included using the `IMPORT` statement:

~~~
IMPORT("file.tff")
~~~

The new TFF file will be processed and included into the current document.

# Importing Token Values from File

Token values can be read from file or URL in two forms: normal or simple. In normal mode, comment characters and empty lines are stripped


