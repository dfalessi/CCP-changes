from datetime import datetime
from datetime import date
from gitInfo import *
import collections
import config
import jiraInfoRepository
from collections import Counter

'''
Goal: To resolve this question:
  For each requirement compute how many times it was reopened.
'''
def getNumReopenTimes(jira, reqName):
  return jiraInfoRepository.numIssueWhileReopenedByClause(jira, "key = " + reqName)

'''		
Goal: To resolve this question:		
  how many requirements are already defined in Jira but their implementation has not started yet.		
'''
def getNumOpenFeatures(jira):		
  return jiraInfoRepository.numIssueWhileOpenByClause(jira)

'''
Goal: To resolve this question:
  how many requirement have started to be implemented but are not completely implemented.
'''
def getOpenInProgressFeatures(jira):
  return jiraInfoRepository.numIssueWhileInProgressByClause(jira)

'''
Goal: Multiple commits might be made by the same developer.
   This function is to not print the same name multiple times.
'''
def getNumUniqueDevelopers(developers, reqName):
  seen = set()
  uniqueDevelopers = []
  for dev in developers:
    if dev not in seen:
      uniqueDevelopers.append(dev)
      seen.add(dev)
  return len(uniqueDevelopers)

'''
Goal: 
5. To resolve PERILS-3 - Workflow compliance
  How many times a commit related to the requirement happened while the requirement was: open, in progress, closed, resolved, reopened.
'''
def getItemHistory(jira, reqName):
  results = {}
  results.update(jiraInfoRepository.getStatuesOfOtherReqWhenThisInProgress(jira, reqName).items())
  results.update(jiraInfoRepository.getStatuesOfOtherReqBeforeThisInProgress(jira, reqName).items())
  results.update(jiraInfoRepository.getOtherReqStatusesWhenThisOpen(jira, reqName).items())
  results["transitionCounters"] = jiraInfoRepository.getNumEachTransition(jira, reqName)
  results["numDescChangedCounters"] = jiraInfoRepository.getNumDescriptionChanged(jira, reqName)
  results["numCommitsEachStatus"] = jiraInfoRepository.getNumCommitDuringEachReq(jira, reqName)
  return results