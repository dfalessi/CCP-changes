import git
from github import Github
import re
from datetime import datetime
import urllib.request
import config
import json
import os
import subprocess

###################### PUBLIC APIs ######################

repoPyGitHub = None
def _initRepoObject():
  global repoPyGitHub
  if repoPyGitHub == None:
    gitKey = "f564b19dbef0aabc1e5950a38b25d2b913ca2f01"
    git = Github(gitKey)
    org = git.get_organization("apache")
    repoPyGitHub = org.get_repo(config.PROJECT_NAME)
# _initRepoObject()
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

def _convertDictStringToDict(dictStr):
  return json.loads(dictStr.decode("utf-8"))

'''
Goal: Get all pull requests by paging
'''
def _getAllPullRequestsByPaging():
  page = 0
  allPullRequestDict = []
  while True:
    pullRequestsOnePageDict = _convertDictStringToDict(urllib.request.urlopen(config.TIKA_PULL_REQUESTS_BY_PAGE + str(page)).read())
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
    pullRequestsOnePageDict = _convertDictStringToDict(urllib.request.urlopen(config.TIKA_CLOSED_PULL_REQUEST_BY_PAGE + str(page)).read())
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

'''
TODO
Goal: 
  Get the percentage of pull requests merged by Heuristic 1
  H1 - At least one of the commits in the pull request appears in the target project’s master branch.
Idea:
  1. Get all the commits of a pull request
  2. Check if any one of the commits appears in the master
Pseudocode:
  # foreach closed and unmerged pull request
    # foreach commit in the closed and unmerged pull request
      # execute git-branch -a --contains <sha>
      # check if the commit is on master
      # add that pr as h1-merged
  # return h1-merged-list
@:return a list of pull requests that are merged and closed through H1
'''
def getPercentageByH1():
  h1Merged = []
  for pr in _getAllMergedAndClosedPullRequests():
    commitDict = _convertDictStringToDict(urllib.request.urlopen(pr["commits_url"]).read())
    for commit in commitDict:
      cmd = ["git", "branch", "--all", "--contains", commit["sha"]]
      pr = subprocess.Popen(cmd,
                            cwd=os.path.dirname("C:/Users/yiupang/Documents/CCP-REPOS/tika-master/"),
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
      (out, error) = pr.communicate()
      if len(re.findall(config.MASTER_REGEX, out.decode("utf-8"))) > 0:
        h1Merged.append(pr)
  return h1Merged

'''
H3: Use the message's attribute in the commit object.
'''

