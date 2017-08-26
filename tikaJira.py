from jira import JIRA
import git
import re
import csv
import requests
from datetime import datetime

MAX_RESULTS = 1000
TIKA_REQ_STR = "project=TIKA AND issueType=\'New Feature\' AND "
TIKA_LOCAL_REPO = r"C:\Users\yiupang\Documents\CCP-REPOS\tika-master"
REQUIREMENT = 'TIKA-2016' # for testing purpose, TIKA-1699 has the most committs and TIKA-2016 has the best transitions
CSV_FILE = 'TIKA-Table.csv'
DATE_REGEX = '(\d{4}-\d{2}-\d{2})'
AUTHOR_REGEX = '(?<=Author: )([a-zA-Z ]+)'
COMMIT_REGEX = '(?<=commit )([a-z-A-Z0-9]+)'
COMMIT_DATE_REGEX = '(?<=Date:   )([A-Za-z0-9: ]+)'
STATE_STR = "status"
OPEN_STR = "Open"
IN_PROGRESS_STR = "In Progress"
REOPENED_STR = "Reopened"
RESOLVED_STR = "Resolved"
CLOSED_STR = "Closed"
STATUSES = [OPEN_STR, IN_PROGRESS_STR, REOPENED_STR, RESOLVED_STR, CLOSED_STR]
'''
Goal: Get all possible transitions
'''
def getAllPossibleTransitions():
  transitions = {}
  for idx, val in enumerate(STATUSES):
    for idx2, val2 in enumerate(STATUSES):
      if idx != idx2:
        transitions[val+"|"+val2] = [val, val2]
  return transitions
TRANSITIONS = getAllPossibleTransitions()#a <transition>|<transition2> of dictionary

'''
Goal: To resolve this question:
  For each requirement compute how many times it was reopened.
'''
def getReopenTimes(jira, reqName):
  return jira.search_issues(TIKA_REQ_STR + "status WAS \'Reopened\' AND key = " + reqName, maxResults=MAX_RESULTS)

'''
Goal: To resolve this question:
  how many requirements are already defined in Jira but their implementation has not started yet.
'''
def getOpenFeatures(jira):
  return jira.search_issues(TIKA_REQ_STR + "status=\'Open\'", maxResults=MAX_RESULTS)

'''
Goal: A helper function
'''
def getHistories(jira, reqName):
  issue = jira.issue(reqName, expand='changelog')
  return issue.changelog.histories

'''
Goal: To resolve PERILS 3 -	JIRA Workflow compliance
  How many times a commit related to the requirement happened while the requirement was: open, in progress, closed, resolved, reopened.
'''


def initDataStatuesesOtherReqWhileOpen(jira, end, results):
  timeClause = ""
  if end != None: # the issue is in open status without activities
    timeClause = " BEFORE " + end
  results["numOpenWhileThisOpen"] = len(jira.search_issues(TIKA_REQ_STR + "status WAS \'Open\'" + timeClause, maxResults=MAX_RESULTS))
  results["numInProgressWhileThisOpen"] = len(jira.search_issues(TIKA_REQ_STR + "status WAS \'In Progress\'" + timeClause, maxResults=MAX_RESULTS))
  results["numReopenedWhileThisOpen"] = len(jira.search_issues(TIKA_REQ_STR + "status WAS \'Reopened\'" + timeClause, maxResults=MAX_RESULTS))
  results["numResolvedWhileThisOpen"] = len(jira.search_issues(TIKA_REQ_STR + "status WAS \'Resolved\'" + timeClause, maxResults=MAX_RESULTS))
  results["numClosedWhileThisOpen"] = len(jira.search_issues(TIKA_REQ_STR + "status WAS \'Closed\'" + timeClause, maxResults=MAX_RESULTS))

'''
Goal: To init data for PERILS-7 - Statuses of other existing requirements
'''
def initDataStatusesOtherReq(jira, startProgressTime, results):
  if(startProgressTime != None):
    timeClause = " ON " + startProgressTime
    results["numOpen"] = len(jira.search_issues(TIKA_REQ_STR + "status WAS \'Open\'" + timeClause, maxResults=MAX_RESULTS))
    results["numInProgress"] = len(jira.search_issues(TIKA_REQ_STR + "status WAS \'In Progress\'" + timeClause, maxResults=MAX_RESULTS))
    results["numReopened"] = len(jira.search_issues(TIKA_REQ_STR + "status WAS \'Reopened\'" + timeClause, maxResults=MAX_RESULTS))
    results["numResolved"] = len(jira.search_issues(TIKA_REQ_STR + "status WAS \'Resolved\'" + timeClause, maxResults=MAX_RESULTS))
    results["numClosed"] = len(jira.search_issues(TIKA_REQ_STR + "status WAS \'Closed\'" + timeClause, maxResults=MAX_RESULTS))
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
    allIssueBeforeThis = jira.search_issues(TIKA_REQ_STR + "status WAS IN (\'Resolved\', \'Closed\') BEFORE " + startProgressTime, maxResults=MAX_RESULTS)
    numIssueBeforeThis = len(allIssueBeforeThis)
    results["numDevelopedRequirementsBeforeThisInProgress"] = numIssueBeforeThis
  else:# this issue has no "In Progress" phase.
    results["numDevelopedRequirementsBeforeThisInProgress"] = "NA"

'''
Goal: 
1. To resolve PERILS-11 - Changed, Ans: Column F-J
2. To resolve PERILS-7 - Statuses of other existing requirements
3. To resolve this question:
    for each requirement in Tika, compute how many requirements have been implemented (resolved or closed) 
  before this requirement started to be implemented (i.e., until it became in porgress).
4. To resolve PERILS-2 - Transitions
5. To resolve PERILS-3 - Workflow compliance
6. To resolve PERILS-16 - Statuses of other requirements when open
'''
def getItemHistory(jira, reqName):
  results = {}
  transitionCounters = {}
  descChangedCounters = {}
  startProgressTime = None
  currentStatus = OPEN_STR
  numCommitsEachStatus = {}
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
      createdTime = re.findall(DATE_REGEX, history.created)[0]
      #if ndx == 0:
        #numCommitsEachStatus[OPEN_STR] = [{"startTime": createdTime}]
      if item.field == 'description':# Resolve #1
        descChangedCounters[currentStatus] += 1
      # print (history.created)
      if item.field == STATE_STR:# Resolve #2
        if (item.toString == IN_PROGRESS_STR):# Resolve #2 and #3
          startProgressTime = createdTime
      if item.field == STATE_STR and currentStatus != item.toString:# Resolve #4
        # fromString means one status starts, and toString means one status ends.
        print (item.toString)
        print (item.fromString)

        if statusTracking == item.fromString: # End one status
          numCommitsEachStatus[item.fromString].append({"endTime": createdTime})
        elif item.fromString == OPEN_STR and isJustOpen == False:# A newly open ticket has no transition so I have to record the endTime in a edge case. 
          numCommitsEachStatus[item.fromString] = [{"endTime": createdTime}]
          isJustOpen = True

        if item.toString not in numCommitsEachStatus:
          numCommitsEachStatus[item.toString] = [{"startTime": createdTime}] # start one new status
          statusTracking = item.toString
        else:
          numCommitsEachStatus[item.toString].append({"startTime": createdTime})
          statusTracking = item.toString


        key = currentStatus + "|" + item.toString
        transitionCounters[key] += 1
        if currentStatus == OPEN_STR and item.toString != OPEN_STR:# Resolved #6
          endOpenTime = createdTime
        currentStatus = item.toString

  results["numDescChangedCounters"] = descChangedCounters
  initDataStatusesOtherReq(jira, startProgressTime, results)
  initDataStatuesesOtherReqWhileOpen(jira, endOpenTime, results)
  initDataNumDeveloped(jira, results, startProgressTime)
  results["transitionCounters"] = transitionCounters
  results["numCommitsEachStatus"] = numCommitsEachStatus
  # numCommitsEachStatus["numCommits" + currentStatus.replace(" ", "")]

  return results

'''
Goal: To resolve this question:
  how many requirement have started to be implemented but are not completely implemented.
'''
def getOpenInProgressFeatures(jira):
  return jira.search_issues(TIKA_REQ_STR + "status=\'In Progress\'", maxResults=MAX_RESULTS)

'''
Goal: To resolve this question:
  developers for that requirement.
'''
def getGitCommitsForThisReq(reqName, isGetNumCommit):
  repo = git.Repo(TIKA_LOCAL_REPO)
  datesForAllCommits = []
  logInfo = repo.git.log("--all", "-i", "--grep=" + reqName)

  if(len(logInfo) == 0):
    return {"formattedDevelopers": [], "numCommits": 0}
  else:
    developers = re.findall(AUTHOR_REGEX, logInfo)
    formattedDevelopers = []
    if isGetNumCommit == True:
      dates = re.findall(COMMIT_DATE_REGEX, logInfo)
      for date in dates:
        datesForAllCommits.append(datetime.strptime(date[:-1], "%a %b %d %H:%M:%S %Y").strftime("%Y-%m-%d"))
    else:
      for dev in developers: #delete the last white space character detected by the regex
        formattedDevelopers.append(dev[:-1])
    return {"formattedDevelopers": formattedDevelopers, "datesForAllCommits": datesForAllCommits}

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
    developers = getUniqueDevelopers(getGitCommitsForThisReq(req.key, False)["formattedDevelopers"], req.key)
    print ("numDevelopers: ", len(developers))
    #print ("developers:", developers)
    print ("numDescChanged:", getNumDescChanged(jira, req.key))
    print ("\n\n\n")

'''
Goal: Loop all the issues of TIKA to compute the matrixes and output them to a csv file.
'''
def outputCSVFile(jira, limit):
  with open(CSV_FILE, 'w', newline='') as csvfile:
    fieldnames = [
       'numOpenRequirements',
       'numInProgressRequirements', 
       'ticket',
       'numDevelopedRequirementsBeforeThisInProgress',
       'numDevelopers',
       'numDescOpen',
       'numDescInProgress',
       'numDescResolved',
       'numDescReopened',
       'numDescClosed',
       "numCommitsOpen",
       "numCommitsInProgress",
       "numCommitsResolved",
       "numCommitsReopened",
       "numCommitsClosed",
       "numOpenWhileThisOpen",
       "numInProgressWhileThisOpen",
       "numResolvedWhileThisOpen",
       "numReopenedWhileThisOpen",
       "numClosedWhileThisOpen",
       "numOpen",
       "numInProgress",
       "numReopened",
       "numResolved",
       "numClosed"]
    for key in TRANSITIONS:
      fieldnames.append(key)

    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerow({'numOpenRequirements': len(getOpenFeatures(jira)), 
      'numInProgressRequirements': len(getOpenInProgressFeatures(jira))})
    for indx, req in enumerate(jira.search_issues("project=TIKA AND issueType=\'New Feature\'")):
      if limit != None and indx == limit:
        break
      results = getItemHistory(jira, req.key)
      row = {
        'ticket': req.key,
        'numDevelopedRequirementsBeforeThisInProgress': results["numDevelopedRequirementsBeforeThisInProgress"],
        'numDevelopers': len(getUniqueDevelopers(getGitCommitsForThisReq(req.key, False), req.key)),
        "numOpenWhileThisOpen": results['numOpenWhileThisOpen'],
        "numInProgressWhileThisOpen": results['numInProgressWhileThisOpen'],
        "numResolvedWhileThisOpen": results['numResolvedWhileThisOpen'],
        "numReopenedWhileThisOpen": results['numReopenedWhileThisOpen'],
        "numClosedWhileThisOpen": results['numClosedWhileThisOpen'],
        'numOpen': results['numOpen'],
        "numInProgress": results["numInProgress"],
        "numReopened": results["numReopened"],
        "numResolved": results["numResolved"],
        "numClosed": results["numClosed"],
      }
      for key in results["numDescChangedCounters"]:
        row["numDesc" + key.replace(" ", "")] = results["numDescChangedCounters"][key]
      for key in results["transitionCounters"]:
        row[key] = results["transitionCounters"][key]
      for key in results["numCommitsEachStatus"]:
        row[key] = results["numCommitsEachStatus"][key]
      writer.writerow(row)

def main():
  jira = JIRA({
    'server': 'https://issues.apache.org/jira'
  })
  # outputCSVFile(jira, 5)
  print (getItemHistory(jira, REQUIREMENT)["numCommitsEachStatus"])
  # print (datetime.strptime('Mon Aug 17', "%a %b %y"))

if __name__ == "__main__":
  main()