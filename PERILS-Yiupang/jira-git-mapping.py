import json 
import pprint

projectData = None
parsedProjectDataDict = None

def getJiraAndRepoURLs(projectName):
   returnDict = {"repository":[], "jira":""}

   with open("apache-projects.json") as dataFile:
      projectData = json.load(dataFile)
      bugDatabase = projectData[projectName]["bug-database"]
      repo = projectData[projectName]["repository"]
      returnDict["jira"] = bugDatabase if bugDatabase.find("jira") >= 0 else None 
      for eachRepo in repo:
         if eachRepo.find("git") >= 0:
            returnDict["repository"].append(eachRepo)
         elif eachRepo.find("svn") >= 0:
            # TODO handle mirrored repo
            returnDict["repository"].append("")
      dataFile.close()
   return returnDict

pprint.pprint(getJiraAndRepoURLs("ace"))
