from jira import JIRA
from Jira.IssueApache import IssueApache
from Jira import JiraQuery


class JiraApache:
  jiraAPI = None
  jiraProjectName = None
  issuesApache = []

  '''
  jiraURL - to create an object of jiraAPI
  jiraProjectQuery - to select a project when executing queries
  '''
  def __init__(self, jiraProjectName):
    print("initializing jiraProjectName = ", jiraProjectName)
    self.jiraAPI = JIRA({
      'server': 'https://issues.apache.org/jira'
    })
    self.jiraProjectName = jiraProjectName
    self.__setAllIssuesApache()

  '''
  To resolve this question (No related ticket in JIRA):
    The number of requirenments that are in progress.
  '''
  def getNumInProgressFeatures(self):
    return JiraQuery.getNumIssueWhenInProgressByClause(self.jiraAPI, self.jiraProjectName)

  '''		
  To resolve this question (No related ticket in JIRA):
    how many requirements are already defined in Jira but their implementation has not started yet.		
  '''
  def getNumOpenFeatures(self):
    return JiraQuery.getNumIssueWhileOpenByClause(self.jiraAPI, self.jiraProjectName)

  '''
  Return all issues of in this jira
  '''
  def getAllIssuesApache(self):
    return self.issuesApache

  def __setAllIssuesApache(self):
    i = 0
    for req in JiraQuery.getAllIssues(self.jiraAPI, self.jiraProjectName):
      if (i == 1):
        break
      self.issuesApache.append(IssueApache(req.key, self.jiraAPI, self.jiraProjectName))
      i += 1
