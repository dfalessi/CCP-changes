import git
from github import Github
import re
from datetime import datetime
import config
import json
import subprocess
import httpRequest
import sys

###################### PUBLIC APIs ######################

'''
Multiple commits might be made by the same developer.
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
A public function exposed to other scripts
'''
def getCommitsDatesForThisReq(reqName):
  return _getGitLogInfo(reqName, _getCommitsDatesForThisReq)

'''
Compare two dates in the format of '%Y-%m-%dT%H:%M:%S'
'''
def gitDateComparator(date1, date2):
  return datetime.strptime(date1, config.GIT_JIRA_DATE_FORMAT) >= datetime.strptime(date2, config.GIT_JIRA_DATE_FORMAT)

'''
Get the percentage of pull requests closed through GitHub
'''
def getPortionOfUnmergedPullRequestOnGitHub():
  return len(_getAllUnmergedAndClosedPullRequests()) / len(_getAllPullRequestsByPaging())

'''
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
@return a list of pull requests that are merged and closed through H1
'''
def getPercentageByH1():
  h1Merged = []
  for pr in _getAllUnmergedAndClosedPullRequests():
    commitDict = _convertDictStringToDict(httpRequest.gitAPIRequest(pr["commits_url"]))
    for commit in commitDict:
      if _isInMasterBranch(commit["sha"]):
        h1Merged.append(pr)
  return h1Merged

'''

  Get the percentage of pull requests merged by Heuristic 2
  H2 - A commit closes the pull request using its log and that commit appears in the master branch.
      This means that the pull request commits were squashed onto one commit and this commit was merged.

Pseudocode:
  # foreach closed and unmerged pull request
    # foreach commit in the closed and unmerged pull request
      # cond1 = check if the commit is on master
      # cond2 = check if the commit has one of the keyword
      # if cond1 and cond2:
        # add that pr as h2-merged
  # return h2-merged-list
'''
def getPercentageByH2():
  h2Merged = []
  for pr in _getAllUnmergedAndClosedPullRequests():
    commitDict = _convertDictStringToDict(httpRequest.gitAPIRequest(pr["commits_url"]))
    for commit in commitDict:
      if _isInMasterBranch(commit["sha"]) and _hasClosingKeyword(commit["sha"]):
        h2Merged.append(pr)
  return h2Merged

'''

  Get the percentage of pull requests merged by Heuristic 3
  H3 - One of the last three discussion comments contain a commit unique identifier.
      This commit appears in the project's master branch, 
      and the corresponding comment can be matched by the following regular expression.
'''
def getPercentageByH3():
  commitCount = 0
  h3Merged = []
  for pr in _getAllUnmergedAndClosedPullRequests():
    commitDict = _convertDictStringToDict(httpRequest.gitAPIRequest(pr["commits_url"]))
    for commit in commitDict:
      if (_isInMasterBranch(commit["sha"]) and
          _hasMergedKeyword(commit["sha"])):
        h3Merged.append(pr)
      if commitCount == 2:
        break
  return h3Merged

'''

  Get the percentage of pull requests merged by Heuristic 4
  H4 - The latest comment (on the master) prior to closing the pull request matches the regular expression.
  
Pseudocode:
  # foreach closed and unmerged pull request
    # Get the closed time by accessing "closed_at" attribute
    # Find the latest commit before the closed date by using: git rev-list -1 --before="$DATE" master | xargs -Iz git checkout z
    # Reset the repo to master
    # Check the comment of the commit match one of the hasMergedKeywords
      # if yes:
        # return true
'''
def getPercentageByH4():
  mergedByH4 = []
  for pr in _getAllUnmergedAndClosedPullRequests():

    lastestCommitSha = re.findall(config.CHECKOUT_COMMIT_SHA_REGEX,
                                  _executeGitShellCommand(["git", "rev-list", "-1", "--before=" + pr["closed_at"],
                                                           "maser", "|", "xargs", "-Iz", "git", "checkout", "z"]))[0]
    # git checkout HEAD
    _executeGitShellCommand(["git", "checkout", "master"])
    if (_hasMergedKeyword(lastestCommitSha)):
      mergedByH4.append(pr)
  return mergedByH4



###################### PRIVATE FUNCTIONS ######################
'''
The parent of getting git's logInfo. 
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
Get developers for this requirement.
'''
def _getGitDeveloperForThisReq(logInfo):
  developers = re.findall(config.AUTHOR_REGEX, logInfo)
  formattedDevelopers = []
  for dev in developers: #delete the last white space character detected by the regex
    formattedDevelopers.append(dev[:-1])

  return {"formattedDevelopers": formattedDevelopers}

'''
Get all the commits' dates of this requirement.
'''
def _getCommitsDatesForThisReq(logInfo):
  dates = re.findall(config.COMMIT_DATE_REGEX, logInfo)
  datesForAllCommits = []
  for date in dates:
    datesForAllCommits.append(datetime.strptime(date[:-1],
                                                config.GIT_DATE_FORMAT).strftime(config.GIT_JIRA_DATE_FORMAT))

  return datesForAllCommits

'''
Convert String of a JSON from the git api to a dictionary.
'''
def _convertDictStringToDict(dictStr):
  return json.loads(dictStr.decode("utf-8"))

'''
Get all pull requests by paging
'''
def _getAllPullRequestsByPaging():
  page = 0
  allPullRequestDict = []
  while True:
    pullRequestsOnePageDict = _convertDictStringToDict(httpRequest.gitAPIRequest(config.TIKA_PULL_REQUESTS_BY_PAGE + str(page)))
    if(len(pullRequestsOnePageDict) == 0):
      break
    else:
      allPullRequestDict += pullRequestsOnePageDict
    page += 1

  return allPullRequestDict

'''
Get all the closed pull requests by paging
'''
def _getAllClosedPullRequestByPaging():
  page = 0
  allPullRequestDict = []
  while True:
    pullRequestsOnePageDict = _convertDictStringToDict(httpRequest.gitAPIRequest(config.TIKA_CLOSED_PULL_REQUEST_BY_PAGE + str(page)))
    if(len(pullRequestsOnePageDict) == 0):
      break
    else:
      allPullRequestDict += pullRequestsOnePageDict
    page += 1

  return allPullRequestDict

'''
Get merged pull requests
'''
def _getAllUnmergedAndClosedPullRequests():
  nonMergedPullRequest = []
  for pullRequest in _getAllClosedPullRequestByPaging():
    if(pullRequest["merged_at"] == None):
      nonMergedPullRequest.append(pullRequest)

  return nonMergedPullRequest

'''
Check if a commit is in the master branch

@return a boolean that indicates if a commit is on the master branch of tika
'''
def _isInMasterBranch(commitSha):
  return len(re.findall(config.MASTER_REGEX,
                        _executeGitShellCommand(["git", "branch", "--all", "--contains", commitSha]))) > 0

'''
A parent function for _hasClosingKeyword and _hasMergedKeyword
'''
def _hasKeywordInGitLogByRegex(commitSha, regex):
  repo = git.Repo(config.TIKA_LOCAL_REPO)
  return len(re.findall(repo.git.log("--forma=%B", "-n", "1", commitSha), regex)) > 0

'''
Check if the comment of a commit has one of the closing keywords
'''
def _hasClosingKeyword(commitSha):
  return _hasKeywordInGitLogByRegex(commitSha, config.CLOSING_KEYWORDS_REGEX)

'''
Check if the comment of a commit has one of the merging keywords.
'''
def _hasMergedKeyword(commitSha):
  return _hasKeywordInGitLogByRegex(commitSha, config.MERGING_KEYWORDS_REGEX)

def _executeGitShellCommand(commandList):
  pr = subprocess.Popen(commandList,
                        cwd=config.TIKA_LOCAL_REPO,
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
  out, err = pr.communicate()
  decodedErr = err.decode("utf-8")
  if(decodedErr != ""):
    sys.exit(decodedErr)

  return out.decode("utf-8")