Requirement
-----------
1. Python 2.7
2. R 3.1
3. MySQL

How to use the script
---------------------
1. First of all, you should set your database's host, user and password (in line 45 of "extract_data.py")
2. Run "output_data.py" to show statistical results in each project and output metrics to csv files
3. In "output_data.py", you can switch project in line 90. If the project has no sql file, you should set the variable "hasDB" to False.
4. The R code and metrics files are in the folder "csv_data": 
   - "prediction.R" allows you to predict bug reopening with GLM, C5.0, ctree, cforest and randomForest; 
   - "chisq+fisher.R" allows you to check significance between single and multi reopening.
5. If you analyse a new project, you should put its commit log file in the "commit_log" folder
   
Data format
-----------
Our statistical script can only handle data with the format in our examples, i.e.
1. If you use a new git project:
   - you should output its commit log by this command "git log --pretty=format:'%H, %an, %ai, %s' -—shortstat > your_file_path"
   - its commit log file should leave the first line as blank
2. If you use a new mercurial project:
   - you should output churn and changed files information
   - its commit log file should not contain any blank line

Data description
----------------
1. "commit_log" folder contains commit logs for all five studied projects
2. "bugzilla_metrics" only contains Webkit's Bugzilla metrics extracted from Bugzilla website (because we don't have Webkit's Bugzilla database)

For any questions
-----------------
Please send email to le.an@polymtl.ca

