import config
import jiraInfo # import here for testing
import csvGenerator
from jira import JIRA
import sys
import re
import json
import gitInfo
import git
from github import Github
import os
import subprocess

def prettyPrintDict(dict):
  print (json.dumps(dict, indent=2))

def main():
  jira = JIRA({
    'server': config.PROJECT_URL
  })

  if len(sys.argv) == 2:
    numTicket = sys.argv[1]
    print (numTicket)
    csvGenerator.outputCSVFile(jira, numTicket)
  elif len(sys.argv) == 3:
    if sys.argv[1] == "-r":
      prettyPrintDict (jiraInfo.getJIRAItemHistory(jira, sys.argv[2]))
  else:
    csvGenerator.outputCSVFile(jira, None)
  
	
if __name__ == "__main__":
  # gitKey = "f564b19dbef0aabc1e5950a38b25d2b913ca2f01"
  # count = 0
  # git = Github(gitKey)
  # org = git.get_organization("apache")
  # repoPyGitHub = org.get_repo("tika")
  # list = repoPyGitHub.get_pulls("all")
  # print (repoPyGitHub.get_pull(201).merged)
  # for pr in list:
  #  if pr.merged == True:
  #    count = count + 1
  # print(count)
  print(gitInfo.getPercentageByH1())
  # print (g)
  #repo = git.Repo(config.TIKA_LOCAL_REPO)
  #c = repo.commit("015c695c7d5a4549c26be247497559d03769f1e4")
  #print (c.author)
  # main()