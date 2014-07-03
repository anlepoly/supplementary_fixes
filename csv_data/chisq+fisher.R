method = 'chisq'

# check significance for Mozilla between single and multi reopening
mozilla <- as.table(rbind(c(390, 1659-390), c(105, 1217-105)))
dimnames(mozilla) <- list(occurence = c('single', 'multi'), validity = c('invalid', 'valid'))

# check significance for Netbeans between single and multi reopening
netbeans <- as.table(rbind(c(1753, 4453-1753), c(278, 1228-278)))
dimnames(netbeans) <- list(occurence = c('single', 'multi'), validity = c('invalid', 'valid'))

# check significance for JDT Core between single and multi reopening
jdt.core <- as.table(rbind(c(153, 405-153), c(81, 302-81)))
dimnames(jdt.core) <- list(occurence = c('single', 'multi'), validity = c('invalid', 'valid'))

# check significance for Platform SWT between single and multi reopening
platform.swt <- as.table(rbind(c(177, 355-177), c(314, 359-91)))
dimnames(platform.swt) <- list(occurence = c('single', 'multi'), validity = c('invalid', 'valid'))

# check significance for Webkit between single and multi reopening
webkit <- as.table(rbind(c(880, 968-880), c(208, 1343-208)))
dimnames(webkit) <- list(occurence = c('single', 'multi'), validity = c('invalid', 'valid'))

if(method == 'fisher') {
	print(fisher.test(mozilla, alternative = "two.sided"))
	print(fisher.test(netbeans, alternative = "two.sided"))
	print(fisher.test(jdt.core, alternative = "two.sided"))
	print(fisher.test(platform.swt, alternative = "two.sided"))
	print(fisher.test(webkit, alternative = "two.sided"))
} else if(method == 'chisq') {
	print(chisq.test(mozilla, correct = TRUE))
	print(chisq.test(netbeans, correct = TRUE))
	print(chisq.test(jdt.core, correct = TRUE))
	print(chisq.test(platform.swt, correct = TRUE))
	print(chisq.test(webkit, correct = TRUE))
}