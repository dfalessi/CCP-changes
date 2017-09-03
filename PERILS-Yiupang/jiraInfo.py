import config
import jiraInfoRepository

'''
Goal: Get all requirenments for looping.
'''
def getAllRequirenments(jira):
  return jira.search_issues(config.TIKA_REQ_STR)

'''
Goal: To resolve this question (No related ticket in JIRA):
  The number of requirenments that are in progress.
'''
def getNumInProgressFeatures(jira):
  return jiraInfoRepository.numIssueWhenInProgressByClause(jira)

'''		
Goal: To resolve this question (No related ticket in JIRA):
  how many requirements are already defined in Jira but their implementation has not started yet.		
'''
def getNumOpenFeatures(jira):		
  return jiraInfoRepository.numIssueWhileOpenByClause(jira)

'''
Goal: To resolve multiple tickets in the following order:
  PERILS-12
  PERILS-11
  PERILS-3
  PERILS-16
  PERILS-7
  PERILS-2
'''
def getItemHistory(jira, reqName):
  results = {}
  results.update(jiraInfoRepository.getStatuesOfOtherReqBeforeThisInProgress(jira, reqName).items())
  results["numDescChangedCounters"] = jiraInfoRepository.getNumDescriptionChanged(jira, reqName)
  results["numCommitsEachStatus"] = jiraInfoRepository.getNumCommitDuringEachReq(jira, reqName)
  results.update(jiraInfoRepository.getOtherReqStatusesWhileThisOpen(jira, reqName).items())
  results.update(jiraInfoRepository.getStatuesOfOtherReqWhenThisInProgress(jira, reqName).items())
  results["transitionCounters"] = jiraInfoRepository.getNumEachTransition(jira, reqName)
  
  
  return results