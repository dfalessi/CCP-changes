import sys
import json
from CSV.CSV import CSV
import Perils
from Git import GitOperations
import re
from Utility import Utility
import config
from ProjectApache import ProjectApache
from collections import OrderedDict

_APACHE_GITHUB = "https://github.com/apache/{}"
_APACHE_GITHUB_GIT_CLONE = "git@github.com:apache/{}.git"

'''
This function handles three cases:

  1. Fixes bad url from the json provided by Apache.
  2. If a project uses svn, get mirror on Github. 
  3. Parses Apache.org's git url into Github's url

@return the url for cloning the project. If the project doesn't have a Github, return False.
'''
def __getValidGitRepo(eachRepo):
  print("Validating repo's url = ", eachRepo)
  gitUrlByRegex = re.findall("(:?.*)\/(.*).git", eachRepo)
  truncatedGitUrl = re.findall("(:?git:)(.*)", eachRepo)
  print ("gitUrlByRegx = ", gitUrlByRegex)
  print ("truncatedGitUrl = ", truncatedGitUrl)
  if len(truncatedGitUrl) > 0:
    # Valid git clone url, such as git://.*.
    return eachRepo
  elif len(gitUrlByRegex) > 0 and "git" in gitUrlByRegex[0][0]:
    # git clone url with https, such as https://.*.git
    # For example: https://git-wip-us.apache.org/repos/asf?p=ambari.git
    # gitUrlByRegex constains a array of tuple. gitUrlByRegex[0][0] = the originial url
    #                                           gitUrlByRegex[0][1] = the parsed git repo's name
    return _APACHE_GITHUB_GIT_CLONE.format(gitUrlByRegex[0][1])
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
Updates status of a project
'''
def updateProjectStatus(projectName, status):
  projectData = None
  with open ("./Dataset/project-status.json", 'r+') as outfile:
    projectData = json.load(outfile)
    outfile.seek(0)
    outfile.truncate()
    projectData[projectName] = status
    json.dump(projectData, outfile, indent=4, sort_keys=True)
    outfile.close()

'''
It loops all the projects in apache-project.json.
'''
def main():
  csvRows = []
  if (len(sys.argv) < 2):
    print ("Usage: python3 Main.py <project.json> <output.csv>")
    sys.exit(-1)
  with open(sys.argv[1], encoding="utf8") as dataFile:
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
      updateStatus = None
      # either of jira or git repo is not available.
      if urlInfo["jira"] is None:
        print("Missing JIRA database.")
        updateProjectStatus(projectName, "NoJIRA")
        continue
      elif len(urlInfo["repository"]) == 0:
        print("Missing Git repositories.")
        updateProjectStatus(projectName, "NoGit")
        continue
      updateProjectStatus(projectName, True)
      proj = ProjectApache(urlInfo["jira"], urlInfo["repository"], localRepos)
      csvRows.append(proj.csvRows)
      Utility.prettyPrintJSON(Utility.getCurrentRateLimit())

    finalTable = CSV(sys.argv[2], Perils.initCSVHeaders(), csvRows)
    finalTable.outputCSVFile()

if __name__ == "__main__":
  main()
