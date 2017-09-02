

import requests
from datetime import datetime
from datetime import date
from gitInfo import *
import collections
from config import *

'''
Goal: To resolve this question:
  For each requirement compute how many times it was reopened.
'''
def getReopenTimes(jira, reqName):
  return jira.search_issues(TIKA_REQ_STR_WHERE + "status WAS \'Reopened\' AND key = " + reqName, maxResults=MAX_RESULTS)

'''
Goal: To resolve this question:
  how many requirements are already defined in Jira but their implementation has not started yet.
'''
def getOpenFeatures(jira):
  return jira.search_issues(TIKA_REQ_STR_WHERE + "status=\'Open\'", maxResults=MAX_RESULTS)

'''
Goal: A helper function
'''
def getHistories(jira, reqName):
  issue = jira.issue(reqName, expand='changelog')
  return issue.changelog.histories

def initDataStatuesesOtherReqWhileOpen(jira, end, results):
  timeClause = ""
  if end != None: # the issue is in open status without activities
    timeClause = " BEFORE " + end
  results["numOpenWhileThisOpen"] = len(jira.search_issues(TIKA_REQ_STR_WHERE + "status WAS \'Open\'" + timeClause, maxResults=MAX_RESULTS))
  results["numInProgressWhileThisOpen"] = len(jira.search_issues(TIKA_REQ_STR_WHERE + "status WAS \'In Progress\'" + timeClause, maxResults=MAX_RESULTS))
  results["numReopenedWhileThisOpen"] = len(jira.search_issues(TIKA_REQ_STR_WHERE + "status WAS \'Reopened\'" + timeClause, maxResults=MAX_RESULTS))
  results["numResolvedWhileThisOpen"] = len(jira.search_issues(TIKA_REQ_STR_WHERE + "status WAS \'Resolved\'" + timeClause, maxResults=MAX_RESULTS))
  results["numClosedWhileThisOpen"] = len(jira.search_issues(TIKA_REQ_STR_WHERE + "status WAS \'Closed\'" + timeClause, maxResults=MAX_RESULTS))

'''
Goal: To init data for PERILS-7 - Statuses of other existing requirements
'''
def initDataStatusesOtherReq(jira, startProgressTime, results):
  if(startProgressTime != None):
    timeClause = " ON " + startProgressTime
    results["numOpen"] = len(jira.search_issues(TIKA_REQ_STR_WHERE + "status WAS \'Open\'" + timeClause, maxResults=MAX_RESULTS))
    results["numInProgress"] = len(jira.search_issues(TIKA_REQ_STR_WHERE + "status WAS \'In Progress\'" + timeClause, maxResults=MAX_RESULTS))
    results["numReopened"] = len(jira.search_issues(TIKA_REQ_STR_WHERE + "status WAS \'Reopened\'" + timeClause, maxResults=MAX_RESULTS))
    results["numResolved"] = len(jira.search_issues(TIKA_REQ_STR_WHERE + "status WAS \'Resolved\'" + timeClause, maxResults=MAX_RESULTS))
    results["numClosed"] = len(jira.search_issues(TIKA_REQ_STR_WHERE + "status WAS \'Closed\'" + timeClause, maxResults=MAX_RESULTS))
  else:# The issue hasn't started being developed.
    results["numOpen"] = results["numReopened"] = results["numInProgress"] = "NA"
    results["numResolved"] = results["numClosed"] = "NA"

'''
Goal: To init data for this question:
    for each requirement in Tika, compute how many requirements have been implemented (resolved or closed) 
  before this requirement started to be implemented (i.e., until it became in porgress).
'''
def initDataNumDeveloped(jira, results, startProgressTime):
  if startProgressTime != None:
    allIssueBeforeThis = jira.search_issues(TIKA_REQ_STR_WHERE + "status WAS IN (\'Resolved\', \'Closed\') BEFORE " + startProgressTime, maxResults=MAX_RESULTS)
    numIssueBeforeThis = len(allIssueBeforeThis)
    results["numDevelopedRequirementsBeforeThisInProgress"] = numIssueBeforeThis
  else:# this issue has no "In Progress" phase.
    results["numDevelopedRequirementsBeforeThisInProgress"] = "NA"

'''
Goal: Format [{"startime": "2017-09-13"}, {"endTime": "2017-04-34"}] into {"startTime": "2017-09-13", "endTime": "2017-04-34"}
'''
def formatTimeList(timeList):
  oneDateRange = {}
  for ndx, val in enumerate(timeList): # formate a pair of startTime and endTime into one dict
    if START_TIME not in oneDateRange and START_TIME not in val:
      oneDateRange[END_TIME] = val[END_TIME]
    elif START_TIME not in oneDateRange:
      oneDateRange[START_TIME] = val[START_TIME]
    elif END_TIME not in oneDateRange:
      oneDateRange[END_TIME] = val[END_TIME]
  return oneDateRange

'''
Goal: To get all commits within the time ranges of a status
Restrains: Two statuses might share the same date, so one commit could count twice.

statusTimeRangeDict's format:
{"Open": {"startTime": "2017-09-23", "endTime": "2017-09-25"},
  "Resovled": {"StartTime: 2"}
}
'''
def getNumCommittEachStatusByDateRange(statusTimeRangesDict, commitDates):
  print (statusTimeRangesDict)
  print (commitDates)
  numCommittEachStatus = {}
  hasRecordedDateDict = {}
  hasRecorded = False

  for key in STATUSES: # init the counter for each status
    numCommittEachStatus[key] = 0

  for commitNdx, commitDate in enumerate(commitDates):
    for key, timeList in statusTimeRangesDict.items():
      oneDateRange = formatTimeList(timeList)
      if commitNdx not in hasRecordedDateDict:
        if END_TIME not in oneDateRange and gitInfo.gitDateComparator(oneDateRange[START_TIME], commitDate):# Example: a newly opened ticket.
          numCommittEachStatus[key] += 1
          hasRecordedDateDict[commitNdx] = True
        elif gitInfo.gitDateComparator(oneDateRange[END_TIME], commitDate):
          numCommittEachStatus[key] += 1
          hasRecordedDateDict[commitNdx] = True
          # break # To prevent this commitDate from being counted again for other statuses.
  return numCommittEachStatus

'''
Goal: 
1. To resolve PERILS-11 - Changed, Ans: Column F-J
2. To resolve PERILS-7 - Statuses of other existing requirements
3. To resolve this question:
    for each requirement in Tika, compute how many requirements have been implemented (resolved or closed) 
  before this requirement started to be implemented (i.e., until it became in porgress).
4. To resolve PERILS-2 - Transitions
5. To resolve PERILS-3 - Workflow compliance
  How many times a commit related to the requirement happened while the requirement was: open, in progress, closed, resolved, reopened.
6. To resolve PERILS-16 - Statuses of other requirements when open
'''
def getItemHistory(jira, reqName):
  results = {}
  transitionCounters = {}
  descChangedCounters = {}
  startProgressTime = None
  currentStatus = OPEN_STR
  dateRangeEachStatus = collections.OrderedDict()
  endOpenTime = None
  openTimeTracking = None
  endTimeTracking = None
  statusTracking = None
  isJustOpen = False

  # initailize transitionCounters
  for key in TRANSITIONS:
    transitionCounters[key] = 0
  for key in STATUSES:
    numCommitsStr = "numCommits" + key.replace(" ", "")
    descChangedCounters[key] = 0

  for history in getHistories(jira, reqName):
    for ndx, item in enumerate(history.items):
      print (re.findall(JIRA_DATE_REGEX, history.created))
      createdTime = re.findall(JIRA_DATE_REGEX, history.created)[0]
      if item.field == 'description':# Resolve #1
        descChangedCounters[currentStatus] += 1
      # print (history.created)
      if item.field == STATE_STR:# Resolve #2
        if (item.toString == IN_PROGRESS_STR):# Resolve #2 and #3
          startProgressTime = createdTime
      if item.field == STATE_STR and currentStatus != item.toString:# Resolve #4
        # fromString means one status starts, and toString means one status ends.
        if statusTracking == item.fromString: # End one status
          dateRangeEachStatus[item.fromString].append({END_TIME: createdTime})
        elif item.fromString == OPEN_STR and isJustOpen == False:# A newly open ticket has no transition so I have to record the endTime of "Open" in a edge case. 
          dateRangeEachStatus[item.fromString] = [{END_TIME: createdTime}]
          isJustOpen = True

        if item.toString not in dateRangeEachStatus:
          dateRangeEachStatus[item.toString] = [{START_TIME: createdTime}] # start one new status
          statusTracking = item.toString
        else:
          dateRangeEachStatus[item.toString].append({START_TIME: createdTime})
          statusTracking = item.toString

        key = currentStatus + "|" + item.toString
        transitionCounters[key] += 1
        if currentStatus == OPEN_STR and item.toString != OPEN_STR:# Resolved #6
          endOpenTime = createdTime
        currentStatus = item.toString

  ### Put data into dictionery ###
  results["numDescChangedCounters"] = descChangedCounters
  initDataStatusesOtherReq(jira, startProgressTime, results)
  initDataStatuesesOtherReqWhileOpen(jira, endOpenTime, results)
  initDataNumDeveloped(jira, results, startProgressTime)
  results["transitionCounters"] = transitionCounters
  commitDates = gitInfo.getGitDeveloperForThisReq(reqName)
  results["numCommitsEachStatus"] = getNumCommittEachStatusByDateRange(dateRangeEachStatus, commitDates["datesForAllCommits"])
  print (results["numCommitsEachStatus"])
  return results

'''
Goal: To resolve this question:
  how many requirement have started to be implemented but are not completely implemented.
'''
def getOpenInProgressFeatures(jira):
  return jira.search_issues(TIKA_REQ_STR_WHERE + "status=\'In Progress\'", maxResults=MAX_RESULTS)

'''
Goal: Multiple commits might be made by the same developer.
   This function is to not print the same name multiple times.
'''
def getUniqueDevelopers(developers, reqName):
  seen = set()
  uniqueDevelopers = []
  for dev in developers:
    if dev not in seen:
      uniqueDevelopers.append(dev)
      seen.add(dev)
  return uniqueDevelopers

'''
Goal: Loop all the issues of TIKA to compute the following two matrixes:
  1. The number of closed or resolved issues before each requirement has started being implemented
  2. Developers for each requirement.
'''
def printTicketInfoForReqs(jira):
  requirements = jira.search_issues("project=TIKA AND issueType=\'New Feature\'")
  for req in requirements:
    print ("Ticket's id: " + req.key)
    print ("reqBeforeThis:", getNumDevelopedRequirementsBeforeThisInProgress(jira, req.key))
    developers = getUniqueDevelopers(gitInfo.getGitDeveloperForThisReq(req.key)["formattedDevelopers"], req.key)
    print ("numDevelopers: ", len(developers))
    #print ("developers:", developers)
    print ("numDescChanged:", getNumDescChanged(jira, req.key))
    print ("\n\n\n")

