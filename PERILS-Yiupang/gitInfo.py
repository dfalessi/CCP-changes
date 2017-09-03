import git
import re
from datetime import datetime
from datetime import date
import config

###################### PUBLIC APIs ######################
'''
Goal: A public function exposed to other scripts
'''
def getGitDeveloperForThisReq(reqName):
  return _getGitLogInfo(reqName, _getGitDeveloperForThisReq)

'''
Goal: A public function exposed to other scripts
'''
def getCommitsDatesForThisReq(reqName):
  return _getGitLogInfo(reqName, _getCommitsDatesForThisReq)

'''
Goal: Compare two dates in the format of "YYYY-mm-dd"
'''
def gitDateComparator(date1, date2):
  return datetime.strptime(date1, config.GIT_JIRA_DATE_FORMAT) >= datetime.strptime(date2, config.GIT_JIRA_DATE_FORMAT)

###################### PRIVATE FUNCTIONS ######################
'''
Goal: The parent of getting git's logInfo
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
  developers = re.findall(AUTHOR_REGEX, logInfo)
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
