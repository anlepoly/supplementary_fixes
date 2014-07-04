Requirement
-----------
1. Python 2.7
2. R 3.1
3. MySQL

How to use the script
---------------------
1. Run "output_data.py" to show statistical results in each project and output metrics in csv
2. Before lanching the script "output_data.py", you should set your database's host, user and password (in line 45 of "extract_data.py")
3. In "output_data.py", you can switch project in line 90. If the project has no sql file, you should set the variable "hasDB" to False.
4. The R code and metrics files are in the folder "csv_data": 
   - "prediction.R" allows you to predict bug reopening with GLM, C5.0, ctree, cforest and randomForest; 
   - "chisq+fisher.R" allows you to check significance between single and multi reopening.
5. If you use a new git project:
   - you should output its commit log by this command "git log --pretty=format:'%H, %an, %ai, %s' -—shortstat > your_file_path"
   - its commit log file should leave the first line as blank; 

Data description
----------------
1. "commit_log" folder contains commit logs for all five studied projects
2. "bugzilla_metrics" only contains Webkit's Bugzilla metrics extracted from Bugzilla website (because we don't have Webkit's Bugzilla database)

Tips
—---
- As we will continue updating and improving the script, the results may be slightly different in the paper (which is written in June 2014).
- For any question and bugs, please send email to le.an@polymtl.ca

