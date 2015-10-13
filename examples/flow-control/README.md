Qsubsec Example: Basic Flow Control
===================================

Introduction
------------

This example demonstrates how template files can submit other templates, passing tokens, and using flag files. An SGE job can wait until another job terminates, but it can not easity see whether that job has completed successfully. An easy way around this is for the first script to write a flag file as its last action, and for the subsequent script to test for the existance of this flag. This is easily accomplished using the `qsubsec` language.

In this example, an initialisation template creates most of the required directories, and submits a set of sectionA and sectionB scripts. Each sectionB script waits for its associated sectionA script to terminate before running, and checks that the previous script completed (using the presence of a flag). A third section (C) requires that all the sectionB jobs are complete, thus it is submitted by the initialisation template with multiple holds. The first command in section C checks that the correct number of flags have been set (i.e. that all the section B jobs completed successfully).

The initialisation script submits all the jobs, as we need all of the scripts referred to in the holds to be present in the queue, otherwise the holds will not be honoured.

The logic to test if there are the correct number of section B flags relies on a simple bash test to check that the number of flag files is equal to the value stored in the `sample-number` file.

Invocation
----------

    qsubsec -s start.qsubsec BASE=. IDFILE=samples.txt

Note that in this case, we do not pass the `samples.txt` sample file to qsubsec as an iterated token. This is because we only want to run `start.qsubsec` once.
