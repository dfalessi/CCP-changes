import config
import gitInfo # import here for testing
import jiraInfo # import here for testing
import jiraInfoRepository # import here for testing
import csvGenerator
from jira import JIRA
import json

def main():
  jira = JIRA({
    'server': config.PROJECT_URL
  })
  # outputCSVFile(jira, 5)
  # print (json.dumps(jiraInfo.getItemHistory(jira, config.REQUIREMENT), indent=2))
  # print (datetime.strptime('Mon Aug 17', "%a %b %y"))
  csvGenerator.outputCSVFile(jira, None)
	
if __name__ == "__main__":
  main()