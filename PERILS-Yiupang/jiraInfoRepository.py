import config

HISTORIES = None
DESCRIPTION_CHANGED_COUNTERS = None

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
  return len(jira.search_issues(config.TIKA_REQ_STR_WHERE + "status WAS \'Closed\'" + Clause, maxResults=config.MAX_RESULTS))

'''
Goal: To resolve PERILS-11 - Changed.
A public wrapper for _getNumDescriptionChanged()
'''
def getNumDescriptionChanged(jira, reqName):
  return _getHistoryItems(jira, reqName, _getNumDescriptionChanged)


'''
Goal: To init data for PERILS-7 - Statuses of other existing requirements
A public wrapper for _getStatuesOfOtherReqWhenThisInProgress()
'''
def getStatuesOfOtherReqWhenThisInProgress(jira, reqName):
  _getHistoryItems(jira, reqName, _getStatuesOfOtherReqWhenThisInProgress)
  result = {}
  if START_PROGRESS_TIME != None:
    timeClause = " ON " + START_PROGRESS_TIME
    results["numOpen"] = numIssueWhileOpenByClause(jira, timeClause)
    results["numInProgress"] = numIssueWhileInProgressByClause(jira, timeClause)
    results["numReopened"] = numIssueWhileReopenedByClause(jira, timeClause)
    results["numResolved"] = numIssueWhileResolvedByClause(jira, timeClause)
    results["numClosed"] = numIssueWhileClosedByClause(jira, timeClause)
  else:# The issue hasn't started being developed.
    results["numOpen"] = results["numReopened"] = results["numInProgress"] = "NA"
    results["numResolved"] = results["numClosed"] = "NA"
  return result


'''
Goal: To resolve PERILS-12:
    For each requirement in Tika, compute how many requirements have been implemented (resolved or closed) 
  before this requirement started to be implemented (i.e., until it became in porgress).
'''
def getStatuesOfOtherReqBeforeThisInProgress(jira, reqName):
  _getHistoryItems(jira, reqName, _getStatuesOfOtherReqBeforeThisInProgress)
  result = {}
  if START_PROGRESS_TIME != None:
    allIssueBeforeThis = jira.search_issues(TIKA_REQ_STR_WHERE + "status WAS IN (\'Resolved\', \'Closed\') BEFORE " + START_PROGRESS_TIME, maxResults=MAX_RESULTS)
    numIssueBeforeThis = len(allIssueBeforeThis)
    results["numDevelopedRequirementsBeforeThisInProgress"] = numIssueBeforeThis
  else:# this issue has no "In Progress" phase.
    results["numDevelopedRequirementsBeforeThisInProgress"] = "NA"
  return result

'''
Goal: To resolve PERILS-2: transitions
'''
def getNumEachTransition(jira, reqName):
  return _getHistoryItems(jira, reqName, _getNumEachTransition)

'''
Goal: To resolve PERILS-16 - Statuses of other requirements when open
'''
def getOtherReqStatusesWhenThisOpen(jira, reqName):
  _getHistoryItems(jira, reqName, _getOtherReqStatusesWhenThisOpen)
  result = {}
  timeClause = ""
  if START_PROGRESS_TIME != None: # the issue is in open status without activities
    timeClause = " BEFORE " + START_PROGRESS_TIME
  results["numOpenWhileThisOpen"] = numIssueWhileOpenByClause(jira, timeClause)
  results["numInProgressWhileThisOpen"] = numIssueWhileInProgressByClause(jira, timeClause)
  results["numReopenedWhileThisOpen"] = numIssueWhileReopenedByClause(jira, timeClause)
  results["numResolvedWhileThisOpen"] = numIssueWhileResolvedByClause(jira, timeClause)
  results["numClosedWhileThisOpen"] = numIssueWhileClosedByClause(jira,timeClause)
  return result


###################### PRIVATE FUNCTIONS ######################
CURRENT_STATUS = OPEN_STR
START_PROGRESS_TIME = None
OPEN_END_TIME = None
TRANSITION_COUNTERS = None

def _getHistoryItems(jira, reqName, callback):
  _initHistories(jira, reqName)
  _initCounters()
  for history in HISTORIES:
    createdTime = re.findall(JIRA_DATE_REGEX, history.created)[0]
    for indx, item in enumerate(HISTORIES.items):
      if item.field == STATE_STR and CURRENT_STATUS != item.toString:
        result = callback(item, createdTime)
  return result

'''
Goal: To resolve PERILS-11 - Changed
'''
def _getNumDescriptionChanged(item):
  if item.field == 'description':# Resolve #1
    DESCRIPTION_CHANGED_COUNTERS[CURRENT_STATUS] += 1
  CURRENT_STATUS = item.toString
  return DESCRIPTION_CHANGED_COUNTERS

'''
Goal: To resolve PERILS-7
'''
def _getStatuesOfOtherReqWhenThisInProgress(item, createdTime):
  if item.field == config.STATE_STR:
    if (item.toString == config.IN_PROGRESS_STR):
      START_PROGRESS_TIME = createdTime

'''
Goal: To resolve PERILS-12
'''
def _getStatuesOfOtherReqBeforeThisInProgress(item, createdTime):
  if item.field == config.STATE_STR:
    if (item.toString == config.IN_PROGRESS_STR):
      START_PROGRESS_TIME = createdTime

'''
Goal: To resolved PERILS-2
'''
def _getNumEachTransition(item):
  key = CURRENT_STATUS + "|" + item.toString
  TRANSITION_COUNTERS[key] += 1
  return TRANSITION_COUNTERS

'''
Goal: To resolve PERILS-16 - Statuses of other requirements when open
'''
def _getOtherReqStatusesWhenThisOpen(item, createdTime):
  if CURRENT_STATUS == OPEN_STR and item.toString != OPEN_STR:# Resolved #6
    OPEN_END_TIME = createdTime

'''
Goal: A helper function
'''
def _initHistories(jira, reqName):
  if(HISTORIES != None):
    issue = jira.issue(reqName, expand='changelog')
    HISTORIES = issue.changelog.histories

'''
Goal: init all counter for each requirenment. 
'''
def _initCounters():
  DESCRIPTION_CHANGED_COUNTERS = {}
  TRANSITION_COUNTERS = {}
  for key in config.STATUSES:
    numCommitsStr = "numCommits" + key.replace(" ", "")
    DESCRIPTION_CHANGED_COUNTERS[key] = 0
  # initailize transitionCounters
  for key in TRANSITIONS:
    TRANSITION_COUNTERS[key] = 0

