from __future__ import division
from extract_data import *

def revisionlist(myBugAnalysis):
    print 'Parsing commit logs ...'
    raw_string = myBugAnalysis.readFile()
    if(myBugAnalysis.projectname == 'mozilla' or myBugAnalysis.projectname == 'netbeans'):
        myBugAnalysis.parseHg(raw_string)
    else:
        myBugAnalysis.parseGit(raw_string)
    return
    
def bugdict(myBugAnalysis):
    print 'Building bug dictionary ...'
    if(myBugAnalysis.projectname == 'mozilla' or myBugAnalysis.projectname == 'netbeans'):
        myBugAnalysis.buildBugDict(True)
    else:
        myBugAnalysis.buildBugDict(False)
    return
    
def extractdata(myBugAnalysis):
    revisionlist(myBugAnalysis)
        
    #   Build different metrics dictionaries
    bugdict(myBugAnalysis)
    myBugAnalysis.supplFixes()
    myBugAnalysis.parseExperience()
    if(myBugAnalysis.cursor):
        myBugAnalysis.parseReopening()
        myBugAnalysis.parseInvalidReport()
    else:
        myBugAnalysis.parseReopenedInvalid( )
    return

def optionalOutputData(myBugAnalysis):
    '''outputsingle(projectname, bugDic, experienceDic)'''

    (shorttimeDic, longtimeDic) = myBugAnalysis.intervalStatistics()
    myBugAnalysis.commitStatistics()
    myBugAnalysis.userStatistics()
    return 

def showPercentage(a, b):
    return '(' + str(round(a/b*100, 1)) + '%' + ')'
 
def outputdata(myBugAnalysis):
    ###   Result outputing  ###
    revisionCnt = len(myBugAnalysis.revision_list)
    fixTpl = myBugAnalysis.countBugs()
    type1Cnt = fixTpl[0]
    type2Cnt = fixTpl[1]
    fixCnt = type1Cnt + type2Cnt
    
    bugReport = len(myBugAnalysis.bugDic)
    type2Report = len(myBugAnalysis.suppleDic)
    reopenedReport = len(myBugAnalysis.reopeningSet)
    singleReopened = len(myBugAnalysis.singleReopened)
    singleInvalid = len(myBugAnalysis.singleInvalid)
    multiInvalid = len(myBugAnalysis.multiInvalid)
    
    print '\n-', revisionCnt, 'revisions'
    print '-', fixCnt, 'detected bug fixes'
    print '-', type1Cnt, 'type I fixes', showPercentage(type1Cnt, bugReport)
    print '-', type2Cnt, 'type II fixes', showPercentage(type2Cnt, fixCnt)
    
    print '\n-', bugReport, 'bugs reports'
    print '-', type2Report, 'type-II bug reports', showPercentage(type2Report, bugReport)
    print '-', reopenedReport, 'reopening bug reports', showPercentage(reopenedReport, bugReport) 
    print '-', singleReopened, 'single re-opened reports'
    print '\n-', singleInvalid, 'single invalid reports'
    print '-', multiInvalid, 'multi invalid reports'
    
    myBugAnalysis.invalidSingleReopened()

    return
        

def outputCSV():
    # Output result of reopened over supplementary    
    myBugAnalysis.outputReopenedCSV(0, 0)  
    return


if(__name__ == '__main__'):
    #   Switch project here
    project, hasDB = 'netbeans', True
    
    print 'Analysed project:', project, '\n'    
    myBugAnalysis = BugAnalysis(project, hasDB)    
    
    #   Extract data
    dataTuple = extractdata(myBugAnalysis)

    #   Output optional data
    #optionalOutputData(myBugAnalysis)
    
    #   Output result
    outputCSV()
    outputdata(myBugAnalysis)
