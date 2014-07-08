library(cvTools)
#	Set random seed 
set.seed(199)

#	Initialize variables
project = 'webkit'
model = 'randomForest'
doVIF = 'NO'
tree_number = 50

print(project)

#	Read data from the file
dataset <- as.data.frame(read.csv(file = sprintf('stat/%s_stat.csv', project), header = T))
#selectedset <- dataset[dataset[, 'invalid'] == 'YES', ]
selectedset <- dataset


#	Define modelling formula
xcol <- c('week', 'month', 'hour', 'day', 'commit_size', 'changed_file', 'churn', 'keyword', 'committer_exp', 'reporter_exp', 
	'assignee_exp', 'severity', 'priority', 'invalid_status', 'title_size', 'fix_time', 'cc_count', 'platform')
formula <- as.formula(paste('reopened ~ ', paste(xcol, collapse= '+')))


#	VIF analysis
if(doVIF == 'YES') {
	library(car)
	formula <- as.formula(paste('reopened ~ ', paste(xcol, collapse= '+')))
	fit <- glm(formula, data = selectedset, family = binomial())
	print(vif(fit))
}

#	Separate data into k folds
k <- 10 	
folds <- cvFolds(nrow(selectedset), K = 10, type = 'random')

#	Initialize result values
tp.sum = tn.sum = fp.sum = fn.sum <- 0

#	Iteratively run validation
for(i in 1:k) {
	trainIndex <- folds$subsets[folds$which != i]	# Extract training index
	testIndex <- folds$subsets[folds$which == i]	# Extract testing index
				
	trainset <- selectedset[trainIndex, ] 			# Set the training set
  	testset <- selectedset[testIndex, ] 			# Set the validation set	
	  
  	if(model == 'C50') {
		library(C50)
		fit <- C5.0(formula, data = trainset, rules = TRUE)
	  	testset[, 'predict'] <- predict(fit, newdata = testset, type = 'class')
	} else if(model == 'randomForest') {
		library(randomForest)		
		fit <- randomForest(formula, data = trainset, ntree = tree_number, mtry = 5, importance = TRUE)
	  	testset[, 'predict'] <- predict(fit, newdata = testset)
		#varImpPlot(fit, cex = 1, main = project, main.cex = 1)
	} else if(model == 'cforest') {
		library(party)
		data.controls <- cforest_unbiased(ntree = tree_number, mtry = 5)
		fit <- cforest(formula, data = trainset, controls = data.controls)
		testset[, 'predict'] <- predict(fit, newdata = testset)
	} else if(model == 'ctree') {
		library(party)
		data.controls <- ctree_control(maxsurrogate = 3)
		fit <- ctree(formula, data = trainset)
		testset[, 'predict'] <- predict(fit, newdata = testset)
	} else if(model == 'glm') {
		formula <- as.formula(paste('reopened ~ ', paste(xcol, collapse= '+')))
		fit <- glm(formula, data = trainset, family = 'binomial')
		testset[, 'predict'] <- predict(fit, newdata = testset)
	}
	t <- table(observed = testset[, 'reopened'], predicted = testset[, 'predict'])
	
	actualYES <- testset[testset['reopened'] == 'YES', ]
	actualNO <- testset[testset['reopened'] == 'NO', ]
	if(model == "glm"){
		threshold = 0.5
		tp <- nrow(actualYES[actualYES[,'predict'] > threshold,])
		tn <- nrow(actualNO[actualNO[, 'predict'] <= threshold,])
		fp <- nrow(actualNO[actualNO[, 'predict'] > threshold,])
		fn <-  nrow(actualYES[actualYES[,'predict'] <= threshold,])
	} else {
		tp <- nrow(actualYES[actualYES[,'predict'] == 'YES',])
		tn <- nrow(actualNO[actualNO[, 'predict'] == 'NO',])
		fp <- nrow(actualNO[actualNO[, 'predict'] == 'YES',])
		fn <- nrow(actualYES[actualYES[,'predict'] == 'NO',])
	}
	
	tp.sum <- tp.sum + tp
	tn.sum <- tn.sum + tn
	fp.sum <- fp.sum + fp
	fn.sum <- fn.sum + fn

	print(sprintf('Validation no. %d', i))
}

acc <- ((tn.sum+tp.sum)/(tn.sum+fp.sum+fn.sum+tp.sum))
re_pre <- (tp.sum/(tp.sum+fp.sum))
re_rec <- (tp.sum/(tp.sum+fn.sum))
re_fm <- (2 * re_pre * re_rec / (re_pre + re_rec))
nr_pre <- (tn.sum/(tn.sum+fn.sum))
nr_rec <- (tn.sum/(tn.sum+fp.sum))
nr_fm <- (2 * nr_pre * nr_rec / (nr_pre + nr_rec))

print(sprintf('accuracy: %.1f%%', acc * 100))
print(sprintf('reopened pre: %.1f%%', re_pre * 100))
print(sprintf('reopened rec: %.1f%%', re_rec * 100))
print(sprintf('reopened f-measure: %.1f%%', re_fm * 100))
print(sprintf('non reopened pre: %.1f%%', nr_pre * 100))
print(sprintf('non reopened rec: %.1f%%', nr_rec * 100))
print(sprintf('non reopened f-measure: %.1f%%', nr_fm * 100))
