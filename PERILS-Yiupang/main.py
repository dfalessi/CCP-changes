import config
import jiraInfo # import here for testing
import csvGenerator
from jira import JIRA
import sys
import json
import gitInfo

def prettyPrintDict(dict):
  print (json.dumps(dict, indent=2))

def main():
  projectNames = config.PROJECT_NAMES
  for i in range(0, len(projectNames)):
    config.PROJECT_NAME = projectNames[i]
    jira = JIRA({
      'server': config.APACHE_JIRA_PROJECT_URL
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
    print ("The percentage of pull requests that are not merged through Github = ", gitInfo.getPortionOfUnmergedPullRequestOnGitHub())
    print ("The percentage of pull requests that are merged through h1 = ", gitInfo.getPercentageByH1())
    print ("The percentage of pull requests that are merged through h2 = ", gitInfo.getPercentageByH2())
    print ("The percentage of pull requests that are merged through h3 = ", gitInfo.getPercentageByH3())
    print ("The percentage of pull requests that are merged through h4 = ", gitInfo.getPercentageByH4())

	
if __name__ == "__main__":
  main()
