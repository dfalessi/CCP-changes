

from datetime import datetime
from datetime import date
from gitInfo import *
import collections
from config import *
import jiraInfoRepositroy
from collections import Counter

'''
Goal: To resolve this question:
  For each requirement compute how many times it was reopened.
'''
def getReopenTimes(jira, reqName):
  return jiraInfoRepositroy.numIssueWhileReopenedByClause(jira, "key = " + reqName)


'''
Goal: 
5. To resolve PERILS-3 - Workflow compliance
  How many times a commit related to the requirement happened while the requirement was: open, in progress, closed, resolved, reopened.
'''
def getItemHistory(jira, reqName):
  results = {}
  currentStatus = OPEN_STR
  dateRangeEachStatus = collections.OrderedDict()
  openTimeTracking = endTimeTracking = statusTracking = isJustOpen = None

  for history in getHistories(jira, reqName):
    for ndx, item in enumerate(history.items):
      createdTime = re.findall(JIRA_DATE_REGEX, history.created)[0]
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
        currentStatus = item.toString

  ### Put data into dictionery ###
  results["numDescChangedCounters"] = jiraInfoRepositroy.getNumDescriptionChanged(jira, reqName)
  results = dict(jiraInfoRepositroy.getStatuesOfOtherReqWhenThisInProgress(jira, reqName), 
                 jiraInfoRepositroy.getStatuesOfOtherReqBeforeThisInProgress(jira, reqName),
                 jiraInfoRepositroy.getOtherReqStatusesWhenThisOpen(jira, reqName))
  results["transitionCounters"] = jiraInfoRepositroy.getNumEachTransition(jira, reqName)
  results["numCommitsEachStatus"] = getNumCommittEachStatusByDateRange(dateRangeEachStatus, gitInfo.getCommitsDatesForThisReq(reqName))
  return results

'''
Goal: To resolve this question:
  how many requirement have started to be implemented but are not completely implemented.
'''
def getOpenInProgressFeatures(jira):
  return jiraInfoRepositroy.numIssueWhileInProgressByClause(jira)

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


###################### PERILS-3 STARTS ######################
'''
Goal: A helper for getNumCommittEachStatusByDateRange()
Format [{"startime": "2017-09-13"}, {"endTime": "2017-04-34"}] into {"startTime": "2017-09-13", "endTime": "2017-04-34"}
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
  return numCommittEachStatus