from __future__ import division
import os
import re
import dateutil.parser
import pytz
import csv
import MySQLdb
import math

class BugAnalysis():
    def __init__(self, name, hasDB):
        self.projectname = name
        self.revision_list = list()
        self.bugDic = dict()
        self.suppleDic = dict()
        self.singleReopened = set()
        self.reporterExpDic = dict()
        self.assigneeExpDic = dict()
        self.reopeningSet = set()
        self.comitterNumber = set()
        self.invalidSet = set()     #   invalid ID set
        self.multiInvalid = set()   #   invalid report set 
        self.singleInvalid = set()  #   invalid report set
        self.csv_writer = csv.writer(open('csv_data/stat/' + name + '_stat' +'.csv', 'wb'))
        if(hasDB):
            self.cursor = self.init_db()
        else:
            self.cursor = None
            self.metrics = dict()   #   bugzilla metrics (for project without database)
            self.init_metrics()
        return
    
    #   Init database cursor
    def init_db(self):
        if(self.projectname == 'jdt' or self.projectname == 'swt'):
            dbname = 'Eclipse_Bugzilla'
        elif(self.projectname == 'mozilla'):
            dbname = 'Mozilla_Bugzilla'
        elif(self.projectname == 'netbeans'):
            dbname = 'Netbeans_Bugzilla'
        #   Please set the database host, user and password here
        database = MySQLdb.connect(host = 'localhost', user = 'root', passwd = 'your_passwd', db = dbname, port = 3306)
        return database.cursor()
    
    
    #   Read bugzilla metrics from file if no database provided
    def init_metrics(self):
        print 'Init bugzilla metrics ...'
        pathname = os.getcwd()
        i = 0
        with open(pathname + '/bugzilla_metrics/' + self.projectname + '_metrics.csv', 'r') as csvfile:    
            rows = csv.reader(csvfile)
            for item in rows:
                if(i > 0):
                    self.metrics[item[0]] = item[1:]
                i += 1
        return


    #   Read VCS File into a string
    def readFile(self):
        pathname = os.getcwd()
        with open(pathname + '/commit_log/' + self.projectname + '_log.txt', 'r') as f:
        	raw_string = f.read()
        f.close()
        return raw_string
    
    #   Parse time string
    def parseTime(self, timeStr):
        d = dateutil.parser.parse(timeStr)
        return d.astimezone(pytz.utc)
        #return d

    #   Parse the string from Hg (Mozilla & Netbeans) into a list (revision_list)
    def parseHg(self, strToParse):
        raw_array = strToParse.split('\n')
        for oneLine in raw_array:
            if(oneLine.startswith('changeset:')):
                tokens = re.findall('\w+', oneLine)
                aChangeset = {'number': tokens[1], 'alias' :tokens[2]}
                self.revision_list.append(aChangeset)
            elif(oneLine.startswith('user:')):
                lastChangeset = self.revision_list[-1]
                lastChangeset['user'] = re.sub(r'user:\s+', '', oneLine)
            elif(oneLine.startswith('date:')):
                lastChangeset = self.revision_list[-1]
                dateStr = re.sub(r'date:\s+', '', oneLine)
                lastChangeset['date'] = dateStr
                lastChangeset['time'] = self.parseTime(dateStr)
            elif(oneLine.startswith('summary:')):
                lastChangeset = self.revision_list[-1]
                commentTxt = re.sub(r'summary:\s+', '', oneLine)
                lastChangeset['comment'] = commentTxt
                bugID = self.parseBugID(commentTxt)
                if(not(bugID is None)):
                    lastChangeset['bug'] = bugID.strip()
            elif(oneLine.startswith(' ')):
                lastChangeset = self.revision_list[-1]
                sect = oneLine.split(',')
                for oneElem in sect:
                    if(re.search('\s+\w+\sfile', oneElem)):
                        lastChangeset['changedFile'] = re.sub(r'\s+file\w{,1}\schanged', '', oneElem).strip() # r'someting' means raw string
                    elif(re.search('\s+\w+\sinsertion', oneElem)):
                        lastChangeset['insertion'] = re.sub(r'\s+insertion\w{,1}\(\+\)', '', oneElem).strip()
                    elif(re.search('\s+\w+\sdeletion', oneElem)):
                        lastChangeset['deletion'] = re.sub(r'\s+deletion\w{,1}\(\-\)', '', oneElem).strip()
        return

    #   Parse the string from Git (Eclipse JDT & SWT) into a list (revision_list)
    def parseGit(self, strToParse):
        raw_array = strToParse.split('\n')
        for oneLine in raw_array:
            if(oneLine == ''):
                aChangeset = {}
                self.revision_list.append(aChangeset)
            elif(not(oneLine.startswith(' '))):
                lastChangeset = self.revision_list[-1]
                tokens = oneLine.split(', ')
                lastChangeset['number'] = tokens[0]
                lastChangeset['user'] = tokens[1]
                dateStr = tokens[2]
                lastChangeset['date'] = dateStr
                lastChangeset['time'] = self.parseTime(dateStr)
                lastChangeset['comment'] = tokens[3]
                bugID = self.parseBugID(tokens[3])
                if(not(bugID is None)):
                    lastChangeset['bug'] = bugID.strip()
                    #print bugID
            elif(oneLine.startswith(' ')):
                self.lastChangeset = self.revision_list[-1]
                sect = oneLine.split(',')
                for oneElem in sect:
                    if(re.search('\s+\w+\sfile', oneElem)):
                        lastChangeset['changedFile'] = re.sub(r'\s+file\w{,1}\schanged', '', oneElem).strip()
                    elif(re.search('\s+\w+\sinsertion', oneElem)):
                        lastChangeset['insertion'] = re.sub(r'\s+insertion\w{,1}\(\+\)', '', oneElem).strip()
                    elif(re.search('\s+\w+\sdeletion', oneElem)):
                        lastChangeset['deletion'] = re.sub(r'\s+deletion\w{,1}\(\-\)', '', oneElem).strip()
        return

    #   Identify a bug-ID from a comment (summary), using regular expressions
    def parseBugID(self, commentTxt):
        regex1 = re.search(r'(bug|issue)[:#\s_]*[0-9]+', commentTxt, re.IGNORECASE)
        regex2 = re.search(r'(b=|#)[0-9]+', commentTxt)
        regex3 = re.search(r'[0-9]+\b', commentTxt, re.IGNORECASE)
        regex4 = re.search(r'\b[0-9]+', commentTxt)
        #other = re.search(r'[0-9]+', commentTxt)
        if(regex1):
            bugID = re.sub(r'[^0-9]+', r'', regex1.group(0))
            return str(int(bugID))
        elif(regex2):
            bugID = re.sub(r'[^0-9]+', r'', regex2.group(0))
            return str(int(bugID))
        elif(regex3):
            bugID = re.sub(r'[^0-9]+', r'', regex3.group(0))
            return str(int(bugID))
        elif(regex4):
            bugID = re.sub(r'[^0-9]+', r'', regex4.group(0))
            return str(int(bugID))
        #elif(other):
        #    print commentTxt
        else:
            return None


    #   Parse committers and reporters experience
    def parseExperience(self):
        print 'Computing experience ...'
        self.parseCommitterExp()
        self.parseReporterAssigneeExp()
        return
    
    #   Parse committers' experience
    def parseCommitterExp(self):
        committerDict = dict()
        for v in reversed(self.revision_list):
            if('bug' in v):
                v['committer_exp'] = self.computeExperience(committerDict, v['user'])
        return
    
    #   Parse reporters' and assignees' experience
    def parseReporterAssigneeExp(self):
        reporterDict, assigneeDict = dict(), dict()
        bugList = sorted(self.bugDic.keys())
        if(self.cursor):
            for bugID in bugList:
                self.cursor.execute('SELECT reporter, assigned_to FROM bugs WHERE bug_id = ' + bugID)
                results = self.cursor.fetchall()
                reporter = results[0][0]
                assignee = results[0][1]
                reporterExp = self.computeExperience(reporterDict, reporter)
                assigneeExp = self.computeExperience(assigneeDict, assignee)
                self.reporterExpDic[bugID] = (reporter, reporterExp)
                self.assigneeExpDic[bugID] = (assignee, assigneeExp)
        else:
            for bugID in bugList:
                reporter = self.metrics[bugID][0]
                assignee = self.metrics[bugID][1]
                reporterExp = self.computeExperience(reporterDict, reporter)
                assigneeExp = self.computeExperience(assigneeDict, assignee)
                self.reporterExpDic[bugID] = (reporter, reporterExp)
                self.assigneeExpDic[bugID] = (assignee, assigneeExp)
        return
            
    #   Compute the experience of developers by the number of bug fixes before
    def computeExperience(self, userDict, thisUser):
        if(thisUser in userDict):
            currentExp = userDict[thisUser] + 1
            userDict[thisUser] = currentExp
            return currentExp
        else:
            userDict[thisUser] = 1
            return 1
        
    #   Put all reopening bugs into a dictionary (eliminate the repeted IDs)
    def parseReopening(self):
        'Parsing bug reopening ...'
        for bugID in self.bugDic:
            self.cursor.execute('SELECT added FROM bugs_activity WHERE bug_id = ' + bugID + ' ORDER BY bug_when')
            results = self.cursor.fetchall()
            for r in results:
                if(r[0] == 'REOPENED'):
                    self.reopeningSet.add(bugID)
                    if(not(bugID in self.suppleDic)):
                        self.singleReopened.add(bugID)
                    break
        return
    
    #   Remove invalid bug ID
    def removeInvalidID(self):
        if(self.cursor):
            for bugID in self.bugDic:
                self.cursor.execute('SELECT * FROM bugs WHERE bug_id = ' + bugID)
                results = self.cursor.fetchall()
                if(len(results) == 0):
                    self.invalidSet.add(bugID)
        else:
            for bugID in self.bugDic:
                if(not (bugID in self.metrics)):
                    self.invalidSet.add(bugID)
        for key in self.invalidSet:
            del self.bugDic[key]        
        return

    #   Put all bugs in to a dictionary, ie. the construction of bugDic
    def buildBugDict(self, isHg):
        revisionDic, aliasMatched = dict(), False
        #   Map an alias number and a bug-ID
        if(isHg):
            for v in self.revision_list:
                if('bug' in v):
                    revisionDic[v['alias']] = v['bug']
        #   Build the bug dictionary
        for v in reversed(self.revision_list):
            if('bug' in v):
                if(not(v['bug'] in self.bugDic)):
                    self.bugDic[v['bug']] = [v]
                else:
                    #   map a revision number to a bug (with alias number)
                    if(isHg):
                        ref = re.search(r'\b\w{12}\b', v['comment'], re.IGNORECASE)
                        if(ref):
                            aliasID = ref.group(0)
                            if(aliasID in revisionDic):
                                aliasMatched = True
                                bugID = revisionDic[aliasID]
                                v['bug'] = bugID
                                if(not(bugID in self.bugDic)):
                                    self.bugDic[bugID] = [v]
                                else:
                                    vlist = self.bugDic[bugID]
                                    vlist.append(v)
                    #   if no revision number (alias) matched
                    if(aliasMatched == False):
                        bugID = v['bug']
                        vlist = self.bugDic[bugID]
                        vlist.append(v)                       
        #   Revmove invalid IDs
        self.removeInvalidID()   
        return self.bugDic

    #   Count bugs and supplementary fixes in total
    def countBugs(self):
        type1Cnt, type2Cnt = 0, 0
        for bugID in self.bugDic:
            if(len(self.bugDic[bugID]) == 1):
                type1Cnt += 1
            else:
                #bugCnt += len(self.bugDic[bugID])
                type2Cnt += len(self.bugDic[bugID])
        return (type1Cnt, type2Cnt)

    #   Put all supplementary fixes into a dictionary
    def supplFixes(self):
        for bugID in self.bugDic:
            if(len(self.bugDic[bugID]) > 1):
                self.suppleDic[bugID] = self.bugDic[bugID]
        return
    
    #   Parse invalid report
    def parseInvalidReport(self):
        for bugID in self.bugDic:
            if(bugID in self.reopeningSet):
                self.cursor.execute('SELECT added FROM bugs_activity WHERE bug_id = ' + bugID + ' ORDER BY bug_when')
                results = self.cursor.fetchall()
                for r in results:
                    if(r[0] == 'INVALID' or r[0] == 'WONTFIX' or r[0] == 'WORKSFORME' or r[0] == 'DUPLICATE'):
                        if(len(self.bugDic[bugID]) > 1):
                            self.multiInvalid.add(bugID)
                        else:
                            self.singleInvalid.add(bugID)
                        break
        return
        
    #   Parse reopened and invalid if no database provided
    def parseReopenedInvalid(self):
        for bugID in self.bugDic:
            item = self.metrics[bugID]
            if(item[-1] == 'YES'):
                self.reopeningSet.add(bugID)
                if(not(bugID in self.suppleDic)):
                    self.singleReopened.add(bugID)
            if(item[2] != 'NO'):
                if(bugID in self.suppleDic):
                    self.multiInvalid.add(bugID)
                else:
                    self.singleInvalid.add(bugID)
        return
                

    #   Computer interval by hour
    def computeInterval(self, vlist):
        minTime = vlist[0]['time']
        maxTime = vlist[0]['time']
        for v in vlist:
            if(v['time'] < minTime):
                minTime = v['time']
            if(v['time'] > maxTime):
                maxTime = v['time']
        return (maxTime - minTime).total_seconds()/3600
        #return (time.mktime(maxTime) - time.mktime(minTime)) / 3600


    #   Time interval statistics
    def intervalStatistics(self):
        shorttimeDic, longtimeDic = dict(), dict()
        maxDay = 0
        dayList = list()
        for bugID in self.bugDic:
            vlist = self.bugDic[bugID]
            if(len(vlist) > 1):
                minTime = vlist[0]['time']
                maxTime = vlist[0]['time']
                for v in vlist:
                    if(v['time'] < minTime):
                        minTime = v['time']
                    if(v['time'] > maxTime):
                        maxTime = v['time']
                interval = self.computeInterval(vlist)
                day = int(interval/24)
                dayList.append(day)
                if(day > maxDay):
                    maxDay = day
                if(interval < 24):
                    shorttimeDic[bugID] = v
                else:
                    longtimeDic[bugID] = v
    
        shortReopening = longReopening = 0
        for bugID in shorttimeDic:
            if(bugID in self.reopeningSet):
                shortReopening += 1
        for bugID in longtimeDic:
            if(bugID in self.reopeningSet):
                longReopening += 1
        
        print ''
        statSet = set(dayList)
        for item in statSet:
            print item, showPercentage(dayList.count(item), len(dayList))        
        print 'max fixing day', maxDay
        print len(shorttimeDic), 'suppl. fixes within 24hrs, where', shortReopening, 'reopened bugs', showPercentage(shortReopening, len(shorttimeDic))
        print len(longtimeDic), 'suppl. fixes more than 24hrs, where', longReopening, 'reopened bugs', showPercentage(longReopening, len(longtimeDic))
                
        return (shorttimeDic, longtimeDic)


    #   Commit times statistics
    def commitStatistics(self):
        fewDic ,manyDic = dict(), dict()
        fewReopening = manyReopening = 0
        maxCommitCnt = 0
        statList = list()
        for bugID in self.bugDic:
            vlist = self.bugDic[bugID]
            statList.append(len(vlist))
            if(len(vlist) > maxCommitCnt):
                maxCommitCnt = len(vlist)
            if(len(vlist) < 4):
                fewDic[bugID] = True
                if(bugID in self.reopeningSet):
                    fewReopening += 1
            else:
                manyDic[bugID] = True
                if(bugID in self.reopeningSet):
                    manyReopening += 1
        print ''
        statSet = set(statList)
        for item in statSet:
            print item, showPercentage(statList.count(item), len(statList))
        print 'the max number of commit', maxCommitCnt
        print len(fewDic), 'fixes within 3 times, where', fewReopening, 'reopened bugs', showPercentage(fewReopening, len(fewDic))
        print len(manyDic), 'fixes more than 3 times, where', manyReopening, 'reopened bugs', showPercentage(manyReopening ,len(manyDic))
        return

    #   User statistics
    def userStatistics(self):
        fewSet, manySet = set(), set()
        fewReopening = manyReopening = 0
        maxUserCnt = 0
        statList = list()
        for bugID in self.bugDic:
            vlist = self.bugDic[bugID]
            userSet = set()
            for v in vlist:
                userSet.add(v['user'])
            userCnt = len(userSet)
            statList.append(userCnt)
            if(userCnt > maxUserCnt):
                maxUserCnt = userCnt
            if(userCnt > 1):
                manySet.add(bugID)
                if(bugID in self.reopeningSet):
                    manyReopening += 1
            else:
                fewSet.add(bugID)
                if(bugID in self.reopeningSet):
                    fewReopening += 1
        print ''
        statSet = set(statList)
        for item in statSet:
            print item, showPercentage(statList.count(item), len(statList))
        print 'max user count', maxUserCnt
        print len(fewSet), 'fixed by 1 committer, where', fewReopening, 'reopened bugs, i.e.', '%.1f' %(fewReopening/len(fewSet)*100)+'%'
        print len(manySet), 'fixed by more than 1 committer, where', manyReopening, 'reopened bugs, i.e.', '%.1f' %(manyReopening/len(manySet)*100)+'%'   
        return

    #   Count supplementary fixes and reopening bugs which belong to supplementary fixes
    def countSuppl(self):
        supplCnt = 0
        reopenedSupplCnt = 0
        suspectCnt = 0
        for bugID in self.bugDic:
            if(len(self.bugDic[bugID]) > 1):
                supplCnt += 1
                if(bugID in self.reopeningSet):
                    reopenedSupplCnt += 1
                    #print(bugID)
            elif(len(self.bugDic[bugID]) == 1):
                if(bugID in self.reopeningSet):
                    #print(bugID)
                    suspectCnt += 1
        return (supplCnt, reopenedSupplCnt)
    
    #   Whether commit a message contains some keyword
    def hasKeyword(self, message):
        keywords = ['bug', 'control', 'background', 'debugging', 'breakpoint', 'blocked', 'platform', 'crash', 'fix', \
                    'severity', 'performance', 'risk', 'error', 'incorrect', 'improve', 'breakpoint', 'warn', 'inconsistent']
        for kw in keywords:
            if(kw in message.lower()):
                return 'YES'
        return 'NO'
    
    #   Extract metrics from bugzilla
    def bugzillaMetrics(self, bugID):
        if(self.cursor == None):
            item = self.metrics[bugID]
            if(item[2] == 'NO'):
                invalidTime = None
            else:
                invalidTime = self.parseTime(item[2] + ' +0000').replace(tzinfo=None)               
            return item[3:8] + [invalidTime]
        else:
            invalidTime = None       
            self.cursor.execute('SELECT bug_when, added FROM bugs_activity WHERE bug_id = ' + bugID + ' ORDER BY bug_when')
            results = self.cursor.fetchall()
            for r in results:
                if(r[1] == 'INVALID' or r[1] == 'WONTFIX' or r[1] == 'WORKSFORME' or r[1] == 'DUPLICATE'):
                    invalidTime = r[0]
                    break
       
            self.cursor.execute('SELECT bug_severity, priority, rep_platform, short_desc FROM bugs WHERE bug_id = ' + bugID)
            results = self.cursor.fetchall()
            if(len(results)):
                tpl = results[0]
                title_size = len(tpl[-1].split())
                self.cursor.execute('SELECT COUNT(DISTINCT who) FROM cc WHERE bug_id = ' + bugID)
                cc_result = self.cursor.fetchall()
                cc_cnt = 0
                if(len(cc_result)):
                    cc_cnt = cc_result[0][0]
                return [tpl[0], tpl[1], tpl[2], title_size, cc_cnt, invalidTime]
            else:
                return None
    
    #   Write metrics into csv
    def formattingCSV(self, flag, v, attemptCnt, fixTime, userCnt, bugzilla_metrics, invalidStatus):        
        #   bug ID
        bugID = v['bug']
       
        #   commit time
        tm = v['time']
        month = tm.strftime('%b')
        day = int(tm.strftime('%d'))
        hour = int(tm.strftime('%H'))
        week = tm.strftime('%a')
        yearday = int(tm.strftime('%j'))

        #   comment length
        commitSize = len(v['comment'].split())
        
        #   churn
        insInt = delInt = 0
        if('insertion' in v):
            insInt = int(v['insertion'])
        if('deletion' in v):
            delInt = int(v['deletion'])
        churn = insInt + delInt

        #   keywords
        keyword = self.hasKeyword(v['comment'])
        
        #   experience
        committerExp = v['committer_exp']
        reporterExp = self.reporterExpDic[bugID][1]
        assigneeExp = self.assigneeExpDic[bugID][1]
        
        #   changed files
        changedFiles = 0
        if('changedFile' in v):
            changedFiles = int(v['changedFile'])
            
        #   write one row if the bug is in the database period
        if('bug' in v):
            self.csv_writer.writerow([bugID, week, month, yearday, hour, day, commitSize, changedFiles, churn, 
                committerExp, reporterExp, assigneeExp, keyword, fixTime, \
                invalidStatus] + bugzilla_metrics + [flag])                
        return
    
    #   Sort dictionaries by time
    def sortTime(self, v):
        return v['time']
    
    #   Prepare output .arff file for reopened bugs in order to be analysed by WEKA
    def outputReopenedCSV(self, attempt, day):        
        print 'Writing metrics to csv file ...'
        self.csv_writer.writerow(['bugID', 'week', 'month', 'yearday', 'hour', 'day', 'commit_size', 'changed_file', 'churn', \
            'committer_exp', 'reporter_exp', 'assignee_exp', 'keyword', 'fix_time', 'invalid_status', \
            'severity', 'priority', 'platform', 'title_size', 'cc_count', 'reopened'])
        
        for bugID in self.suppleDic:
            vlist = self.bugDic[bugID]
            
            if(len(vlist) == 1):
                print bugID
        
            #   bugzilla metrics
            bugzilla_metrics = self.bugzillaMetrics(bugID)                  
            if(bugzilla_metrics):
                #  each revision of a type-II bug,  except the last fix
                userSet = set()
                attemptCnt = 1
                sortedList = sorted(vlist, key = self.sortTime) 
                                
                for v in sortedList[:-1]:
                    if(v['bug'] in self.reopeningSet):
                        flag = 'YES'
                    else:
                        flag = 'NO'
                    try:
                        fixTime = round(math.log((v['time'] - sortedList[0]['time']).total_seconds()/3600 + 1, 2), 1)
                    except:
                        print 'error value:', str((v['time'] - sortedList[-1]['time']).total_seconds()/3600)     
                    userSet.add(v['user'])
                    userCnt = len(userSet)
                    
                    invalidStatus = 'NO'
                    invalidTime = bugzilla_metrics[-1]
                    if(invalidTime and invalidTime <= v['time'].replace(tzinfo=None)):
                        invalidStatus = 'YES'
                          
                    self.formattingCSV(flag, v, attemptCnt, fixTime, userCnt, bugzilla_metrics[:-1], invalidStatus) 
                    attemptCnt += 1
        return

    #   Show invalid-single reopening's number and percentage 
    def invalidSingleReopened(self):
        invalidSingleCnt = 0
        for bugID in self.bugDic:
            if(bugID in self.singleReopened and bugID in self.singleInvalid):
                invalidSingleCnt += 1
        print 'invalid single reopened bugs:', invalidSingleCnt, showPercentage(invalidSingleCnt, len(self.singleReopened))
        return

#   Show percentage        
def showPercentage(a, b):
    return '(' + str(round(a/b*100, 3)) + '%' + ')'
