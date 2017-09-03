import config
import collections
import re
import gitInfo

### Global variables for storing data while loop history of a requirenment ###
HISTORIES = None
CURRENT_STATUS = None

### Global variables specific for tickets ###
DESCRIPTION_CHANGED_COUNTERS = None
START_PROGRESS_TIME = None # PERILS-7 && PERILS-12 && PERILS-16 
OPEN_END_TIME = None # PERILS-16
TRANSITION_COUNTERS = None # PERILS-2
OPEN_TIME_TRACKING = STATUS_TRACKING = None # PERILS-3
IS_JUST_OPEN = False # PERILS-3
DATE_RANGE_EACH_STATUS = collections.OrderedDict() # PERILS-3

###################### PUBLIC APIs ######################
def numIssueWhileOpenByClause(jira, clause=""):
  return len(jira.search_issues(config.TIKA_REQ_STR_WHERE + "status WAS \'Open\'" + clause, maxResults=config.MAX_RESULTS))

def numIssueWhileInProgressByClause(jira, clause=""):
  return len(jira.search_issues(config.TIKA_REQ_STR_WHERE + "status WAS \'In Progress\'" + clause, maxResults=config.MAX_RESULTS))

def numIssueWhileReopenedByClause(jira, clause=""):
  return len(jira.search_issues(config.TIKA_REQ_STR_WHERE + "status WAS \'Reopened\'" + clause, maxResults=config.MAX_RESULTS))

def numIssueWhileResolvedByClause(jira, clause=""):
  return len(jira.search_issues(config.TIKA_REQ_STR_WHERE + "status WAS \'Resolved\'" + clause, maxResults=config.MAX_RESULTS))

def numIssueWhileClosedByClause(jira, clause=""):
  return len(jira.search_issues(config.TIKA_REQ_STR_WHERE + "status WAS \'Closed\'" + clause, maxResults=config.MAX_RESULTS))

'''
Goal: To resolve PERILS-11 - Changed.
A public wrapper for _initNumDescriptionChangedCounter()
'''
def getNumDescriptionChanged(jira, reqName):
  return _getHistoryItems(jira, reqName, _initNumDescriptionChangedCounter)

'''
Goal: To init data for PERILS-7 - Statuses of other existing requirements
A public wrapper for _getStatuesOfOtherReqWhenThisInProgress()
'''
def getStatuesOfOtherReqWhenThisInProgress(jira, reqName):
  _getHistoryItems(jira, reqName, _initStartInProgressTime)
  result = {}
  if START_PROGRESS_TIME != None:
    timeClause = " ON " + START_PROGRESS_TIME
    result["numOpen"] = numIssueWhileOpenByClause(jira, timeClause)
    result["numInProgress"] = numIssueWhileInProgressByClause(jira, timeClause)
    result["numReopened"] = numIssueWhileReopenedByClause(jira, timeClause)
    result["numResolved"] = numIssueWhileResolvedByClause(jira, timeClause)
    result["numClosed"] = numIssueWhileClosedByClause(jira, timeClause)
  else:# The issue hasn't started being developed.
    result["numOpen"] = result["numReopened"] = result["numInProgress"] = "NA"
    result["numResolved"] = result["numClosed"] = "NA"
  return result

'''
Goal: To resolve PERILS-12:
    For each requirement in Tika, compute how many requirements have been implemented (resolved or closed) 
  before this requirement started to be implemented (i.e., until it became in porgress).
'''
def getStatuesOfOtherReqBeforeThisInProgress(jira, reqName):
  _getHistoryItems(jira, reqName, _initStartInProgressTime)
  result = {}
  if START_PROGRESS_TIME != None:
    allIssueBeforeThis = jira.search_issues(TIKA_REQ_STR_WHERE + "status WAS IN (\'Resolved\', \'Closed\') BEFORE " + START_PROGRESS_TIME, maxResults=MAX_RESULTS)
    numIssueBeforeThis = len(allIssueBeforeThis)
    result["numDevelopedRequirementsBeforeThisInProgress"] = numIssueBeforeThis
  else:# this issue has no "In Progress" phase.
    result["numDevelopedRequirementsBeforeThisInProgress"] = "NA"
  return result

'''
Goal: To resolve PERILS-2: transitions
'''
def getNumEachTransition(jira, reqName):
  return _getHistoryItems(jira, reqName, _initNumEachTransition)

'''
Goal: To resolve PERILS-16 - Statuses of other requirements when open
'''
def getOtherReqStatusesWhenThisOpen(jira, reqName):
  _getHistoryItems(jira, reqName, _initFinishedOpenStatusTime)
  result = {}
  timeClause = ""
  if START_PROGRESS_TIME != None: # the issue is in open status without activities
    timeClause = " BEFORE " + START_PROGRESS_TIME
  result["numOpenWhileThisOpen"] = numIssueWhileOpenByClause(jira, timeClause)
  result["numInProgressWhileThisOpen"] = numIssueWhileInProgressByClause(jira, timeClause)
  result["numReopenedWhileThisOpen"] = numIssueWhileReopenedByClause(jira, timeClause)
  result["numResolvedWhileThisOpen"] = numIssueWhileResolvedByClause(jira, timeClause)
  result["numClosedWhileThisOpen"] = numIssueWhileClosedByClause(jira,timeClause)
  return result

'''
Goal: To resolve PERILS-3 - Workflow compliance
  How many times a commit related to the requirement happened while the requirement was: 
    open, in progress, closed, resolved, reopened.
'''
def getNumCommitDuringEachReq(jira, reqName):
  _getHistoryItems(jira, reqName, _initDateRangeEachStatus)
  return _getNumCommittEachStatusByDateRange(DATE_RANGE_EACH_STATUS, gitInfo.getCommitsDatesForThisReq(reqName))


###################### PRIVATE FUNCTIONS ######################
'''
Goal: A template for looping the history of a requirenment.
'''
def _getHistoryItems(jira, reqName, callback):
  global CURRENT_STATUS
  _initHistories(jira, reqName)
  _initCounters()
  result = {}
  if CURRENT_STATUS == None:
    CURRENT_STATUS = config.OPEN_STR
  for history in HISTORIES:
    createdTime = re.findall(config.JIRA_DATE_REGEX, history.created)[0]
    for indx, item in enumerate(history.items):
      if item.field == config.STATE_STR and CURRENT_STATUS != item.toString:
        result = callback(item, createdTime)
        CURRENT_STATUS = item.toString
  return result

'''
Goal: To resolve PERILS-11 - Changed
'''
def _initNumDescriptionChangedCounter(item, _):
  if item.field == 'description':# Resolve #1
    DESCRIPTION_CHANGED_COUNTERS[CURRENT_STATUS] += 1
  
'''
Goal: To resolve PERILS-12
'''
def _initStartInProgressTime(item, createdTime):
  if item.field == config.STATE_STR:
    if (item.toString == config.IN_PROGRESS_STR):
      START_PROGRESS_TIME = createdTime

'''
Goal: To resolved PERILS-2
'''
def _initNumEachTransition(item, _):
  global TRANSITION_COUNTERS
  key = CURRENT_STATUS + "|" + item.toString
  TRANSITION_COUNTERS[key] += 1
  return TRANSITION_COUNTERS

'''
Goal: To resolve PERILS-16 - Statuses of other requirements when open
'''
def _initFinishedOpenStatusTime(item, createdTime):
  if CURRENT_STATUS == config.OPEN_STR and item.toString != config.OPEN_STR:# Resolved #6
    OPEN_END_TIME = createdTime

'''
Goal: To resolvde PERILS-3 - Work compliance
'''
def _initDateRangeEachStatus(item, createdTime):
  global STATUS_TRACKING
  global DATE_RANGE_EACH_STATUS
  global IS_JUST_OPEN
  # fromString means one status starts, and toString means one status ends.
  if STATUS_TRACKING == item.fromString: # End one status
    DATE_RANGE_EACH_STATUS[item.fromString].append({config.END_TIME: createdTime})
  elif item.fromString == config.OPEN_STR and IS_JUST_OPEN == False:# A newly open ticket has no transition so I have to record the endTime of "Open" in a edge case. 
    DATE_RANGE_EACH_STATUS[item.fromString] = [{config.END_TIME: createdTime}]
    IS_JUST_OPEN = True
  if item.toString not in DATE_RANGE_EACH_STATUS:
    DATE_RANGE_EACH_STATUS[item.toString] = [{config.START_TIME: createdTime}] # start one new status
    STATUS_TRACKING = item.toString
  else:
    DATE_RANGE_EACH_STATUS[item.toString].append({config.START_TIME: createdTime})
    STATUS_TRACKING = item.toString

'''
Goal: A call to JIRA API to get the changelog
'''
def _initHistories(jira, reqName):
  global HISTORIES
  if(HISTORIES == None):
    issue = jira.issue(reqName, expand='changelog')
    HISTORIES = issue.changelog.histories

'''
Goal: init all counter for each requirenment. 
'''
def _initCounters():
  global DESCRIPTION_CHANGED_COUNTERS
  global TRANSITION_COUNTERS
  DESCRIPTION_CHANGED_COUNTERS = {}
  TRANSITION_COUNTERS = {}
  for key in config.STATUSES:
    numCommitsStr = "numCommits" + key.replace(" ", "")
    DESCRIPTION_CHANGED_COUNTERS[key] = 0
  # initailize transitionCounters
  for key in config.TRANSITIONS:
    TRANSITION_COUNTERS[key] = 0

###################### PERILS-3 STARTS ######################
'''
Goal: To get all commits within the time ranges of a status
Restrains: Two statuses might share the same date, so one commit could count twice.

statusTimeRangeDict's format:
{"Open": {"startTime": "2017-09-23", "endTime": "2017-09-25"},
  "Resovled": {"StartTime: 2"}
}
'''
def _getNumCommittEachStatusByDateRange(statusTimeRangesDict, commitDates):
  # print (statusTimeRangesDict)
  # print (commitDates)
  numCommittEachStatus = {}
  hasRecordedDateDict = {}
  hasRecorded = False

  for key in config.STATUSES: # init the counter for each status
    numCommittEachStatus[key] = 0

  for commitNdx, commitDate in enumerate(commitDates):
    for key, timeList in statusTimeRangesDict.items():
      for oneDateRange in _formatTimeList(timeList):
        if commitNdx not in hasRecordedDateDict:
          if config.END_TIME not in oneDateRange and gitInfo.gitDateComparator(commitDate, oneDateRange[config.START_TIME]):# Example: a resolved issue that still have commits
            numCommittEachStatus[key] += 1
            hasRecordedDateDict[commitNdx] = True
          elif gitInfo.gitDateComparator(oneDateRange[config.END_TIME], commitDate):
            numCommittEachStatus[key] += 1
            hasRecordedDateDict[commitNdx] = True
          elif config.START_TIME not in oneDateRange and gitInfo.gitDateComparator(oneDateRange[config.END_TIME], commitDate):
            numCommittEachStatus[key] += 1
            hasRecordedDateDict[commitNdx] = True
  return numCommittEachStatus

'''
Goal: A helper for getNumCommittEachStatusByDateRange()
Format [{"startime": "2017-09-13"}, {"endTime": "2017-04-34"}] into {"startTime": "2017-09-13", "endTime": "2017-04-34"}
'''
def _formatTimeList(timeList):
  dateRanges = []
  oneDateRange = {}
  for ndx, val in enumerate(timeList): # formate a pair of startTime and endTime into one dict
    if config.START_TIME not in oneDateRange and config.START_TIME not in val:
      oneDateRange[config.END_TIME] = val[config.END_TIME]
    elif config.START_TIME not in oneDateRange:
      oneDateRange[config.START_TIME] = val[config.START_TIME]
    elif config.END_TIME not in oneDateRange:
      oneDateRange[config.END_TIME] = val[config.END_TIME]
    # print (oneDateRange)
    if (ndx + 1) % 2 == 0:
      dateRanges.append(oneDateRange)
      oneDateRange = {}
    elif ndx == (len(timeList) - 1):
      dateRanges.append(oneDateRange)
      oneDateRange = {}

  return dateRanges
