import config
import gitInfo # import here for testing
import jiraInfo # import here for testing
import jiraInfoRepository # import here for testing
import csvGenerator
from jira import JIRA
import sys
import json

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
  main()