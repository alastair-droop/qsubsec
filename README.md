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
git clone https://github.com/alastair-droop/qsubsec.git
cd qsubsec
python setup.py install
~~~

You will need python3 (>=3.3) to use qsubsec.

If you do not have admin privileges, you can install this locally using `python setup.py install --user`.

After installation, you can verify that you have the correct version using `qsubsec -v`.

Although `qsubsec` can be run on most machines, the qsub executable must be available and functional for automatic qsub submission to work (using the `-s` argument with the qsub format).

## Licence

These tools are released under the [GNU General Public License version 3](http://www.gnu.org/licenses/gpl.html).

## Reference

If you use qsubsec for any published work, please reference the [original paper](https://doi.org/10.1093/bioinformatics/btv698) as:

Alastair P. Droop; "qsubsec: a lightweight template system for defining sun grid engine workflows", *Bioinformatics*, Volume **32**, Issue 8, 15 April 2016, Pages 1267–1268, `https://doi.org/10.1093/bioinformatics/btv698`


BibTex:

~~~latex
@article{doi:10.1093/bioinformatics/btv698,
author = {Droop, Alastair P.},
title = {qsubsec: a lightweight template system for defining sun grid engine workflows},
journal = {Bioinformatics},
volume = {32},
number = {8},
pages = {1267-1268},
year = {2016},
doi = {10.1093/bioinformatics/btv698},
URL = { + http://dx.doi.org/10.1093/bioinformatics/btv698},
eprint = {/oup/backfile/content_public/journal/bioinformatics/32/8/10.1093_bioinformatics_btv698/3/btv698.pdf}
}
~~~

