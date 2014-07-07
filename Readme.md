#Requirement
- Python 2.7
- R 3.1
- MySQL

#How to use the script
- First of all, you should set your database's host, user and password (in line 45 of "extract_data.py")
- Run "output_data.py" to show statistical results in each project and output metrics to csv files
- In "output_data.py", you can switch project in line 90. If the project has no sql file, you should set the variable "hasDB" to False.
- The R code and metrics files are in the folder "csv_data": 
   "prediction.R" allows you to predict bug reopening with GLM, C5.0, ctree, cforest and randomForest; 
   "chisq+fisher.R" allows you to check significance between single and multi reopening.
- If you analyse a new project, you should put its commit log file in the "commit_log" folder
   
#Data format
Our statistical script can only handle data with the format in our examples, i.e.:
- If you use a new git project:    
   you should output its commit log by this command:  
   *git log --pretty=format:'%H, %an, %ai, %s' -—shortstat > your_file_path*   
   the commit log file should leave the first line as blank
- If you use a new mercurial project:   
   you should output churn and changed files information    
   the commit log file should not contain any blank line

#Data description
- "commit_log" folder contains commit logs for all five studied projects
- "bugzilla_metrics" only contains Webkit's Bugzilla metrics extracted from Bugzilla website (because we don't have Webkit's Bugzilla database)

#For any questions
Please send email to le.an@polymtl.ca

