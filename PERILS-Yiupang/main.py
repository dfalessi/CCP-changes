import config
import gitInfo # import here for testing
import jiraInfo # import here for testing
import csvGenerator
from jira import JIRA

def main():
  jira = JIRA({
    'server': config.PROJECT_URL
  })
  # outputCSVFile(jira, 5)
  # getItemHistory(jira, REQUIREMENT)
  # print (datetime.strptime('Mon Aug 17', "%a %b %y"))
  print (gitInfo.getGitDeveloperForThisReq(config.REQUIREMENT))
  csvGenerator.outputCSVFile(jira, 2)
	
if __name__ == "__main__":
  main()