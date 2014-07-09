#Requirements
- Python 2.7 or newer
- R 3.1 or newer
- MySQL

#How to use the script
- First of all, please set your database's host, user and password (**in line 41 of "extract_data.py"**).
- Run "output_data.py" to show statistical results in each project and output metrics to csv files.
- In "output_data.py", you can switch project **in line 85**. If the project has no sql file, you should set the variable "hasDB" to False.
- The R code and metrics files are in the folder "csv_data":    
   1. "prediction.R" allows you to predict bug reopening with GLM, C5.0, ctree, cforest and randomForest (**in line 5**, please set the random seed value before launching the script)   
   2. "chisq+fisher.R" allows you to check significance between single and multi reopening
- If you analyse a new project, please put its commit log file in the "commit_log" folder.
   
#Data format
Our statistical script can only handle data with the format in our examples (in the folder "commit_log"), i.e.:
- If you use a new git project:     
   1. please output its commit log by this command:  
      *git log --pretty=format:'%H, %an, %ai, %s' --shortstat > your_file_path*   
   2. the commit log file should leave the first line blank
- If you use a new mercurial project (see ):   
   1. please output churn and changed files information    
   2. the commit log file should not contain any blank line

#Folder description
- "commit_log" folder contains commit logs for all five studied projects.
- "bugzilla_metrics" folder only contains Webkit's Bugzilla metrics extracted from Bugzilla website (because we don't have Webkit's Bugzilla database).
- "csv_data" folder contains R code and prediction metrics.

#For any questions
Please send email to le.an@polymtl.ca