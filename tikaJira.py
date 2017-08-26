from jira import JIRA
import git
import re
import csv
import urllib.request

MAX_RESULTS = 1000
TIKA_REQ_STR = "project=TIKA AND issueType=\'New Feature\' AND "
TIKA_LOCAL_REPO = r"C:\Users\yiupang\Documents\CCP-REPOS\tika-master"
REQUIREMENT = 'TIKA-1016' # for testing purpose
CSV_FILE = 'TIKA-Table.csv'
DATE_REGEX = '(\d{4}-\d{2}-\d{2})'
STATUSES = ["Open", "In Progress", "Reopened", "Resolved", "Closed"]
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
TODO
Goal: To resolve PERILS 3 -	JIRA Workflow compliance
'''

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
'''
def getItemHistory(jira, reqName):
  results = {}
  transitionCounters = {}
  descChangedCounters = {}
  startProgressTime = None
  currentStatus = 'Open'
  numCommitsEachStatus = {}

  # initailize transitionCounters
  for key in TRANSITIONS:
    transitionCounters[key] = 0
  for key in STATUSES:
    numCommitsEachStatus[key] = 0
    descChangedCounters[key] = 0

  for history in getHistories(jira, reqName):
    for item in history.items:

      if item.field == 'description':# Resolve #1
        descChangedCounters[currentStatus] += 1

      if item.field == 'status':# Resolve #2
        if (item.toString == 'In Progress'):# Resolve #2 and #3
          startProgressTime = re.findall(DATE_REGEX, history.created)[0]

      if item.field == 'status' and currentStatus != item.toString:# Resolve #4
        key = currentStatus + "|" + item.toString
        transitionCounters[key] += 1
        currentStatus = item.toString

  results["numDescChangedCounters"] = descChangedCounters
  initDataStatusesOtherReq(jira, startProgressTime, results)
  initDataNumDeveloped(jira, results, startProgressTime)
  results["transitionCounters"] = transitionCounters

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
def getGitDevelopersForThisReq(reqName):
  repo = git.Repo(TIKA_LOCAL_REPO)
  logInfo = repo.git.log("--all", "-i", "--grep=" + reqName)
  if(len(logInfo) == 0):
    return []
  else:
    developers = re.findall('(?<=Author: )([a-zA-Z ]+)', logInfo)
    formattedDevelopers = []
    for dev in developers: #delete the last white space character detected by the regex
      formattedDevelopers.append(dev[:-1])
    return formattedDevelopers

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
    developers = getUniqueDevelopers(getGitDevelopersForThisReq(req.key), req.key)
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
        'numDevelopers': len(getUniqueDevelopers(getGitDevelopersForThisReq(req.key), req.key)),
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
      writer.writerow(row)

def main():
  jira = JIRA({
    'server': 'https://issues.apache.org/jira'
  })
  outputCSVFile(jira, 20)

if __name__ == "__main__":
  main()