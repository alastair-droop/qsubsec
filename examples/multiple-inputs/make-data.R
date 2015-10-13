i <- c(LETTERS, letters, 0:9)

sample.data <- sapply(1:10, function(x){
	file.stem <- paste(sample(i, 10, replace=TRUE), collapse='')
	file.name <- file.path('.', 'input', sprintf('%s.txt', file.stem))
	values <- rnorm(25, mean=sample(c(0, 5, 10), 1), sd=runif(1, min=1, max=5))
	write.table(values, file=file.name, col.names=FALSE, row.names=FALSE, quote=FALSE)
	return(file.stem)
})
writeLines(sample.data, 'samples.txt')
