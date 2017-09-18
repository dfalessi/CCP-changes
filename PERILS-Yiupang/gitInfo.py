import git
import re
from datetime import datetime
import urllib.request
import config
import json
import main

###################### PUBLIC APIs ######################

'''
Goal: Multiple commits might be made by the same developer.
   This function is to not print the same name multiple times.
'''
def getNumUniqueDevelopers(reqName):
  developers = _getGitLogInfo(reqName, _getGitDeveloperForThisReq)
  seen = set()
  uniqueDevelopers = []
  for dev in developers:
    if dev not in seen:
      uniqueDevelopers.append(dev)
      seen.add(dev)
  return len(uniqueDevelopers)

'''
Goal: A public function exposed to other scripts
'''
def getCommitsDatesForThisReq(reqName):
  return _getGitLogInfo(reqName, _getCommitsDatesForThisReq)

'''
Goal: Compare two dates in the format of '%Y-%m-%dT%H:%M:%S'
'''
def gitDateComparator(date1, date2):
  return datetime.strptime(date1, config.GIT_JIRA_DATE_FORMAT) >= datetime.strptime(date2, config.GIT_JIRA_DATE_FORMAT)


'''
Goal: Get the percentage of pull requests closed through GitHub
'''
def getPortionOfUnmergedPullRequestOnGitHub():
  return len(_getAllMergedAndClosedPullRequests()) / len(_getAllPullRequestsByPaging())

###################### PRIVATE FUNCTIONS ######################
'''
Goal: The parent of getting git's logInfo. 
      It gets logs of all commits that contain the string of the requirement.
'''
def _getGitLogInfo(reqName, callback):
  repo = git.Repo(config.TIKA_LOCAL_REPO)
  logInfo = repo.git.log("--all", "-i", "--grep=" + reqName)
  if(len(logInfo) == 0):
    return {"formattedDevelopers": [], "datesForAllCommits": [], "numCommits": 0}
  else:
    return callback(logInfo)

'''
Goal: Get developers for this requirement.
'''
def _getGitDeveloperForThisReq(logInfo):
  developers = re.findall(config.AUTHOR_REGEX, logInfo)
  formattedDevelopers = []
  for dev in developers: #delete the last white space character detected by the regex
    formattedDevelopers.append(dev[:-1])
  return {"formattedDevelopers": formattedDevelopers}

'''
Goal: Get all the commits' dates of this requirement.
'''
def _getCommitsDatesForThisReq(logInfo):
  dates = re.findall(config.COMMIT_DATE_REGEX, logInfo)
  datesForAllCommits = []
  for date in dates:
    datesForAllCommits.append(datetime.strptime(date[:-1], config.GIT_DATE_FORMAT).strftime(config.GIT_JIRA_DATE_FORMAT))
  return datesForAllCommits

def _convertPullRequestToDict(dictStr):
  return json.loads(dictStr.decode("utf-8"))

'''
Goal: The all pull requests by paging
'''
def _getAllPullRequestsByPaging():
  page = 0
  allPullRequestDict = []
  while True:
    pullRequestsOnePageDict = _convertPullRequestToDict(urllib.request.urlopen(config.TIKA_PULL_REQUESTS_BY_PAGE + str(page)).read())
    if(len(pullRequestsOnePageDict) == 0):
      break
    else:
      allPullRequestDict += pullRequestsOnePageDict
    page += 1
  return allPullRequestDict


'''
Goal: Get all the closed pull requests by paging
'''
def _getAllClosedPullRequest():
  page = 0
  allPullRequestDict = []
  while True:
    pullRequestsOnePageDict = _convertPullRequestToDict(urllib.request.urlopen(config.TIKA_CLOSED_PULL_REQUEST_BY_PAGE + str(page)).read())
    if(len(pullRequestsOnePageDict) == 0):
      break
    else:
      allPullRequestDict += pullRequestsOnePageDict
    page += 1
  return allPullRequestDict


'''
Goal: Get merged pull requests
'''
def _getAllMergedAndClosedPullRequests():
  nonMergedPullRequest = []
  for pullRequest in _getAllClosedPullRequest():
    if(pullRequest["merged_at"] == None):
      nonMergedPullRequest.append(pullRequest)

  return nonMergedPullRequest