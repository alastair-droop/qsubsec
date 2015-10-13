#! /usr/bin/env Rscript
args <- commandArgs(trailingOnly=TRUE)
x <- as.numeric(readLines(args[1]))
writeLines(sprintf('%0.4f', mean(x)))
