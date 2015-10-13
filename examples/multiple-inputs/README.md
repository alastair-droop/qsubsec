Qsubsec Example: Multiple Input
===============================

Iterated Tokens
---------------

This example demonstrates how `qsubsec` can generate multiple submission scripts from a single template file. This uses *iterated tokens* (using the `-iTOKEN=VALUE` syntax), which provide a series of values to a token at submission time. All combinations of token values are submitted as individual scripts.

For example, a script with two tokens (`A` and `B`) submitted with the options `-iA=1,2,3 B=1` will yield three jobs:

* `A=1` & `B=1`
* `A=2` & `B=1`
* `A=3` & `B=1`

However, the same script submitted with the options `-iA=1,2,3 B=1,2,3` will yield 9 jobs:

* `A=1` & `B=1`
* `A=2` & `B=1`
* `A=3` & `B=1`
* `A=1` & `B=2`
* `A=2` & `B=2`
* `A=3` & `B=2`
* `A=1` & `B=3`
* `A=2` & `B=3`
* `A=3` & `B=3`

Values for iterated tokens can either be provided as a comma-separated list, or as a file name. If no comma is present in the iterated token value provided, the value is processed as a file name. If reading from a file, empty lines, and lines whose first non-whitespace character is `#` are ignored.

In this example, 10 data files (with random names) are processed using the template file `multiple-inputs.qsubsec`. This script calls a simple `R` script for each sample ID it is given.  Log files are written to ./logs and the mean of the data in each file is recorded to ./output. The sample IDs to process are given in the text file `samples.txt`. This is a very common situation (although usually the analysis for each script is more complex).

Invocation
----------

	qsubsec multiple-inputs.qsubsec BASE='.' -iID=./samples.txt

Template Code
-------------

    section('process-{ID}', description='Processes a sample set')
    limits(time='00:00:30', vmem='100M')
    options(['V', 'cwd', 'notify'])
    output('{BASE}/logs')
    error('{BASE}/logs')
    require('{BASE}/input/{ID}.txt', 'path_readable')
    require('{BASE}/output', 'path_writable')
    command('{BASE}/process-sample.R {BASE}/input/{ID}.txt > {BASE}/output/{ID}-mean.txt', name='process_{ID}', log=True, test=True)
