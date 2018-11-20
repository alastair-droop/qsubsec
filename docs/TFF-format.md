# Token File Format (TFF) Syntax

Token Files define the placeholder tokens used to generate qsubsec templates. The `qsubsec` script fills in the values of the tokens at submission time, yielding complete scripts for submission. The Token File Format (`TFF`) is a small language used to define a set of tokens.

## Basic Syntax

A TFF `file` contains at most one instruction per line. All whitespace at the beginning and end of a line is removed. Empty lines are ignored. Names and values can be quoted (with either single or double quotes, but start and end quotes must match). Unquoted names and values can only contain letters, numbers and the characters `.`, `-`, `_`, `{`, `}`, `/`, & `:`. Quoted names and values can contain any valid character.

### Comments

TFF files can contain comments. Comments are started using the hash sign (`#`). Any text after the comment sign is ignored. There is no support for multi-line comments.

### Token Assignment

A simple token assignment takes the form:

~~~python
NAME = VALUE
~~~

This statement will create a token with the name `NAME` and the value `VALUE`.

### Iterated Tokens

Tokens can be assigned multiple values (called *iterated tokens*). This is done by providing a comma-separated list of values instead of a single value:

~~~python
NAME = VALUE1, VALUE2
~~~

This statement will create a single token (`NAME`) with two values (`VALUE1` and `VALUE2`).

### Token Placeholders

Tokens placeholders are used to specify where the value of a token is to be filled in. Token placeholders are specified using the token name in parentheses (for example `{NAME}`). Placeholders can be used in all name and value fields in a TFF file. For example, a token name can be created using a placeholder, as can token values:

~~~python
PERSON = Alice
GREETING = "Good morning"
GREET_{PERSON} = "{GREETING}, {PERSON}!"
~~~

In the above code, three tokens are created: `PERSON`, `GREETING`, and `GREET_Alice`. If a token name contains a placeholder referring to an iterated token (or tokens), a new token is created **for each** combination of token values. Iterated tokens referred to in token values will yield multiple values for the token, rather than duplicating the token definition.

## Importing TFF Files

The entire contents of a secondary TFF file can be imported using the `IMPORT` function:

~~~python
# file_1.tff
A=1
IMPORT(file_2.tff)
~~~

~~~python
# file_2.tff:
A="new value"
B=2
C=3
~~~

After processing `file_1.tff`, three tokens will be present: `A`, `B`, and `C`. Furthermore, the value of token A will have been updated as it has been redefined. File names can contain token placeholders.

## Deleting Tokens

If a token is loaded and is no longer needed, it can be removed using the `REMOVE` function:

~~~python
A=1
REMOVE(A)
~~~

## Loading Token Values from File

Token values can be assigned form file. This is especially useful where large numbers of values are possible. Two possible methods exist for this: *normal* and *simple*. If a file is loaded normally, it is processed before loading:

* Empty lines are ignored
* Comments are ignored
* **NB:** quotes are **not** stripped from values before loading

Files loaded as simple are not processed, so empty and comments will be included in the output token values.

The function `FILE` reads data from a file normally, and the function `SFILE` loads data simply. For example:

~~~python
# names.txt:
Alice
Bob
Charlie
~~~

~~~python
NAME = FILE(names.txt)
~~~

The above TFF file generates a single token (`NAME`) containing the three names `Alice`, `Bob` & `Charlie`.

The `URL` and `SURL` functions perform identically to `FILE` and `SFILE` but load data from a URL rather than a local file. Both file names and URLs can contain tokens. Each loading function replaces the value fo the token, so if files or URLs contain placeholders referring to iterated tokens, only the contents of the last resolved location will be used.

**NB:** File and URL data are loaded as ASCII text.
