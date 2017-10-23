import json
from Git import GitOperations
import re
from Utility import Utility
import config
from ProjectApache import ProjectApache
from collections import OrderedDict

_APACHE_GITHUB = "https://github.com/apache/{}"
_APACHE_GITHUB_GIT_CLONE = "git@github.com:apache/{}.git"

def __getValidGitRepo(eachRepo):
  print("Validating repo's url = ", eachRepo)
  gitUrlByRegex = re.findall("(:?.*)\/(.*).git", eachRepo)
  truncatedGitUrl = re.findall("(:?git:)(.*)", eachRepo)
  if len(truncatedGitUrl) > 0:
    # Valid git clone url, such as git://.*.
    return eachRepo
  elif len(gitUrlByRegex) > 0 and "git" in gitUrlByRegex[0]:
    # git clone url with https, such as https://.*.git
    return gitUrlByRegex[0]
  elif eachRepo.find("svn") > 0:
    # svn mirror, such as http://svn.apache.org/.*/trunk/, and "http://svn.apache.org/.*/"
    svnNameInASF = re.findall(".*/asf/(.*)(?:/)", eachRepo)
    svnNameInTrunk = re.findall("(?:.*)\/(.*)\/(?:trunk)", eachRepo)
    svnName = svnNameInASF[0] if svnNameInASF else svnNameInTrunk[0] if svnNameInTrunk else ""
    if svnName != "" and GitOperations.isValidGitCloneURL(_APACHE_GITHUB.format(svnName)):
      return _APACHE_GITHUB_GIT_CLONE.format(svnName)
    return False
  else:
    return False

'''
It loops all the projects in apache-project.json.
'''
def main():
  with open("./Dataset/tika-project.json", encoding="utf8") as dataFile:
    projectData = json.load(dataFile, object_pairs_hook=OrderedDict)
    # loop through all the projects in apache-project.json
    for projectName, info in projectData.items():
      urlInfo = {"repository":[], "jira":""}
      bugDatabase = info["bug-database"] if "bug-database" in info else ""  # get information about the bug database
      urlInfo["jira"] = bugDatabase if bugDatabase.find("jira") >= 0 else None
      repos = info["repository"] if "repository" in info else []  # get information about the repositories
      localRepos = []
      for eachRepo in repos:
        goodGitRepo = __getValidGitRepo(eachRepo)
        if goodGitRepo:
          print("Validated git repo in Main = ", goodGitRepo)
          urlInfo["repository"].append(goodGitRepo)
          localRepos.append(config.LOCAL_REPO.format(projectName))

      # either of jira or git repo is not available.
      if urlInfo["jira"] is None:
        print("Missing JIRA database.")
        continue
      elif len(urlInfo["repository"]) == 0:
        print("Missing Git repositories.")
        continue

      proj = ProjectApache(urlInfo["jira"], urlInfo["repository"], config.CSV_URL, localRepos)
      Utility.prettyPrintJSON(Utility.getCurrentRateLimit())
      proj.toCSVFile()
    dataFile.close()

if __name__ == "__main__":
  main()
