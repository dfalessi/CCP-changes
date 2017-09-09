import config
import csv
import gitInfo
import jiraInfo

COLUMNS_NAMES = [
    'numOpenRequirements',
    'numInProgressRequirements', 
    'ticket',
    ### PERILS-6 ###
    'numDevelopers',
    ### PERILS-12 ###
    'numDevelopedRequirementsBeforeThisInProgress',
    ### PERILS-11 ###
    'numDescOpen',
    'numDescInProgress',
    'numDescResolved',
    'numDescReopened',
    'numDescClosed',
    ### PERILS-3 ###
    "numCommitsOpen",
    "numCommitsInProgress",
    "numCommitsResolved",
    "numCommitsReopened",
    "numCommitsClosed",
    ### PERILS-16 ###
    "numOpenWhileThisOpen",
    "numInProgressWhileThisOpen",
    "numResolvedWhileThisOpen",
    "numReopenedWhileThisOpen",
    "numClosedWhileThisOpen",
    ### PERILS-7 ###
    "numOpenWhenInProgress",
    "numInProgressWhenInProgress",
    "numReopenedWhenInProgress",
    "numResolvedWhenInProgress",
    "numClosedWhenInProgress"]

ROW = {
  'ticket': None,
  'numDevelopedRequirementsBeforeThisInProgress': None,
  'numDevelopers': None,
  "numOpenWhileThisOpen": None,
  "numInProgressWhileThisOpen": None,
  "numResolvedWhileThisOpen": None,
  "numReopenedWhileThisOpen": None,
  "numClosedWhileThisOpen": None,
  'numOpenWhenInProgress': None,
  "numInProgressWhenInProgress": None,
  "numReopenedWhenInProgress": None,
  "numResolvedWhenInProgress": None,
  "numClosedWhenInProgress": None
}

GENERAL_INFO_ROW = {
  "numOpenRequirements": None,
  "numInProgressRequirements": None
}

'''
Goal: Write headers to csv
'''
def _initHeadersForTransitions(csvfile, writer):
   # PERILS-2
  for key in config.TRANSITIONS:
    COLUMNS_NAMES.append(key)
  writer.writeheader()

'''
Goal: Loop all the issues of TIKA to compute the matrixes and output them to a csv file.
'''
def outputCSVFile(jira, limit):
  with open(config.CSV_FILE, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=COLUMNS_NAMES)
    _initHeadersForTransitions(csvfile, writer)

    GENERAL_INFO_ROW['numOpenRequirements'] = jiraInfo.getNumOpenFeatures(jira)
    GENERAL_INFO_ROW['numInProgressRequirements'] = jiraInfo.getNumInProgressFeatures(jira)
    writer.writerow(GENERAL_INFO_ROW)

    ### A loop where all the tickets are resolved ###
    for indx, req in enumerate(jiraInfo.getAllRequirenments(jira)):
      if limit != None and indx == limit: # limit the search result for debugging purpose.
        break
      print ('{0} {1}'.format("Writing", req.key))
      results = jiraInfo.getJIRAItemHistory(jira, req.key)
      ROW["ticket"] = req.key
      ROW["numDevelopedRequirementsBeforeThisInProgress"] = results["numDevelopedRequirementsBeforeThisInProgress"]
      ROW["numDevelopers"] = gitInfo.getNumUniqueDevelopers(req.key)
      ROW["numOpenWhileThisOpen"] = results['numOpenWhileThisOpen']
      ROW["numInProgressWhileThisOpen"] = results['numInProgressWhileThisOpen']
      ROW["numResolvedWhileThisOpen"] = results['numResolvedWhileThisOpen']
      ROW["numReopenedWhileThisOpen"] = results['numReopenedWhileThisOpen']
      ROW["numClosedWhileThisOpen"] = results['numClosedWhileThisOpen']
      ROW["numOpenWhenInProgress"] = results['numOpenWhenInProgress']
      ROW["numInProgressWhenInProgress"] = results["numInProgressWhenInProgress"]
      ROW["numReopenedWhenInProgress"] = results["numReopenedWhenInProgress"]
      ROW["numResolvedWhenInProgress"] = results["numResolvedWhenInProgress"]
      ROW["numClosedWhenInProgress"] = results["numClosedWhenInProgress"]
      for key in results["numDescChangedCounters"]:
        ROW["numDesc" + key.replace(" ", "")] = results["numDescChangedCounters"][key]
      for key in results["transitionCounters"]:
        ROW[key] = results["transitionCounters"][key]
      for key in results["numCommitsEachStatus"]:
        ROW["numCommits" + key.replace(" ", "")] = results["numCommitsEachStatus"][key]

      writer.writerow(ROW)