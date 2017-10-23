import re

JIRA_REQ_WHERE_CLAUSE = "project={} AND issueType=\'New Feature\'"
JIRA_REQ_CONT_WHERE_CLAUSE = JIRA_REQ_WHERE_CLAUSE + " AND "
MAX_RESULTS = 1000

def getAllIssues(jira, jiraProjectName):
  return jira.search_issues(JIRA_REQ_WHERE_CLAUSE.format(jiraProjectName))

def getNumIssueWhileOpenByClause(jira, jiraProjectName, clause=""):
  return len(jira.search_issues(JIRA_REQ_CONT_WHERE_CLAUSE.format(jiraProjectName) + "status WAS \'Open\'" + clause,
                                maxResults=MAX_RESULTS))

def getNumIssueWhenInProgressByClause(jira, jiraProjectName, clause=""):
  return len(jira.search_issues(JIRA_REQ_CONT_WHERE_CLAUSE.format(jiraProjectName) + "status WAS \'In Progress\'" + clause,
                                maxResults=MAX_RESULTS))

def getNumIssueWhileReopenedByClause(jira, jiraProjectName, clause=""):
  return len(jira.search_issues(JIRA_REQ_CONT_WHERE_CLAUSE.format(jiraProjectName) + "status WAS \'Reopened\'" + clause,
                                maxResults=MAX_RESULTS))

def getNumIssueWhileResolvedByClause(jira, jiraProjectName, clause=""):
  return len(jira.search_issues(JIRA_REQ_CONT_WHERE_CLAUSE.format(jiraProjectName) + "status WAS \'Resolved\'" + clause,
                                maxResults=MAX_RESULTS))

def getNumIssueWhileClosedByClause(jira, jiraProjectName, clause=""):
  return len(jira.search_issues(JIRA_REQ_CONT_WHERE_CLAUSE.format(jiraProjectName) + "status WAS \'Closed\'" + clause,
                                maxResults=MAX_RESULTS))


def getAllFinishedIssueBeforeThisInProgress(jira, jiraProjectName, startProgressTime):
  return jira.search_issues(JIRA_REQ_CONT_WHERE_CLAUSE.format(jiraProjectName) +
                                                    "status WAS IN (\'Resolved\', \'Closed\') BEFORE " +
                                                    re.findall('(\d{4}-\d{2}-\d{2})', startProgressTime)[0],
                                                    maxResults=MAX_RESULTS)