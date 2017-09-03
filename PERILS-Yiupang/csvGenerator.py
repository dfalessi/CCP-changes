import config
import csv
import gitInfo
import jiraInfo
import jiraInfoRepository # TODO Bad idea!!! csvGenerator should only interact with jiraInfo

COLUMNS_NAMES = [
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

ROW = {
  'ticket': None,
  'numDevelopedRequirementsBeforeThisInProgress': None,
  'numDevelopers': None,
  "numOpenWhileThisOpen": None,
  "numInProgressWhileThisOpen": None,
  "numResolvedWhileThisOpen": None,
  "numReopenedWhileThisOpen": None,
  "numClosedWhileThisOpen": None,
  'numOpen': None,
  "numInProgress": None,
  "numReopened": None,
  "numResolved": None,
  "numClosed": None
}

'''
Goal: Write headers to csv
'''
def _initColumnsNamesForTransitions(csvfile, writer):
  for key in config.TRANSITIONS:
    COLUMNS_NAMES.append(key)
  writer.writeheader()

'''
Goal: Loop all the issues of TIKA to compute the matrixes and output them to a csv file.
'''
def outputCSVFile(jira, limit):
  with open(config.CSV_FILE, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=COLUMNS_NAMES)
    _initColumnsNamesForTransitions(csvfile, writer)
    writer.writerow({'numOpenRequirements': jiraInfo.getNumOpenFeatures(jira), 'numInProgressRequirements': jiraInfo.getOpenInProgressFeatures(jira)})
    for indx, req in enumerate(jira.search_issues(config.TIKA_REQ_STR)):
      if limit != None and indx == limit: # limit the search result for debugging purpose.
        break
      print ('{0} {1}'.format("Writing", req.key))
      results = jiraInfo.getItemHistory(jira, req.key)
      ROW["ticket"] = req.key
      ROW["numDevelopedRequirementsBeforeThisInProgress"] = results["numDevelopedRequirementsBeforeThisInProgress"]
      ROW["numDevelopers"] = jiraInfo.getNumUniqueDevelopers(gitInfo.getGitDeveloperForThisReq(req.key), req.key)
      ROW["numOpenWhileThisOpen"] = results['numOpenWhileThisOpen']
      ROW["numInProgressWhileThisOpen"] = results['numInProgressWhileThisOpen']
      ROW["numResolvedWhileThisOpen"] = results['numResolvedWhileThisOpen']
      ROW["numReopenedWhileThisOpen"] = results['numReopenedWhileThisOpen']
      ROW["numClosedWhileThisOpen"] = results['numClosedWhileThisOpen']
      ROW["numOpen"] = results['numOpen']
      ROW["numInProgress"] = results["numInProgress"]
      ROW["numReopened"] = results["numReopened"]
      ROW["numResolved"] = results["numResolved"]
      ROW["numClosed"] = results["numClosed"]

      for key in results["numDescChangedCounters"]:
        ROW["numDesc" + key.replace(" ", "")] = results["numDescChangedCounters"][key]
      for key in results["transitionCounters"]:
        ROW[key] = results["transitionCounters"][key]
      for key in results["numCommitsEachStatus"]:
        ROW["numCommits" + key.replace(" ", "")] = results["numCommitsEachStatus"][key]
      writer.writerow(ROW)