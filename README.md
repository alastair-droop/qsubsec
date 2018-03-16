# A Simple SGE Template Preprocessor Engine


`qsubsec` is a template language for generating script files for submission using the [SGE grid system](https://arc.liv.ac.uk/trac/SGE). By using this system, you can separate the logic of your qsub jobs from the data required for a specific run.

## Overview

The qsubsec utility processes qsubsec-formatted template files to generate code sections that can be submitted for execution (for example through the SGE scheduler). Before processing, template files are checked for token placeholders and these are filled in. The resulting Python code is then executed to generate a set of sections.

The stages in template processing are:

* The template file and token file(s) are read;
* Any token placeholders found in the template file are filled in using the tokens file(s) read;
* The resulting Python code is executed to yield a set of sections;
* Each section is output in turn

Processed sections can be output in multiple formats (currently `bash` and `qsub`), allowing the same templates to be run on multiple different systems.

For more information on the TFF token definition syntax and the qsubsec template syntax, see the documentation directory.


## Installation

Installation should be as simple as:

~~~bash
git clone https://github.com/alastair-droop/qsubsec3.git
cd qsubsec3
python setup.py install
~~~

If you do not have admin privileges, you can install this locally using `python setup.py install --user`.

After installation, you can verify that you have the correct version using `qsubsec -v`.

Although `qsubsec` can be run on most machines, the qsub executable must be available and functional for automatic qsub submission to work (using the `-s` argument with the qsub format).

## Licence

These tools are released under the [GNU General Public License version 3](http://www.gnu.org/licenses/gpl.html).
