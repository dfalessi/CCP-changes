from jira import JIRA
import re

MAX_RESULTS = 1000
jira = None
TIKA_REQ_STR = "project=TIKA and issueType=\'New Feature\' AND "
'''
Statuses:
1. OPEN
2. IN PROGESS
3. REOPENED
4. RESOLVED
5. CLOSED
'''

'''
Goal: To resolve this question:
	how many requirements are already defined in Jira but their implementation has not started yet.
'''
def getOpenFeatures(jira):
	return jira.search_issues(TIKA_REQ_STR + "status=\'Open\'", maxResults=MAX_RESULTS)

'''
Goal: To resolve this question:
		for each requirement in Tika, compute how many requirements have been implemented (resolved or closed) 
	before this requirement started to be implemented (i.e., until it became in porgress).
'''
def getNumRequirementsBeforeThis(jira, reqName):
	startProgressDate = None
	# 1. get the time where the issue is changed to in progress
	issue = jira.issue(reqName, expand='changelog')
	changelog = issue.changelog
	for history in changelog.histories:
		for item in history.items:
			if item.field == 'status' and item.fromString == 'Open' and item.toString == 'In Progress':
				print ('[DEBUG] Date:' + history.created + ' From:' + item.fromString + ' To:' + item.toString)
				startProgressDate = re.findall('(\d{4}-\d{2}-\d{2})', history.created)[0]

	# 2. all the issues before that time with type of New Feature and status of RESOLVED or CLOSED
	allIssueBeforeThis = jira.search_issues(TIKA_REQ_STR + "status WAS IN (\'Resolved\', \'Closed\') BEFORE " + startProgressDate, maxResults=MAX_RESULTS)
	numIssueBeforeThis = len(allIssueBeforeThis)
	return numIssueBeforeThis

'''
Goal: To resolve this question:
	how many requirement have started to be implemented but are not completely implemented.
'''
def getOpenInProgressFeatures(jira):
	return jira.search_issues(TIKA_REQ_STR + "status=\'In Progress\'", maxResults=MAX_RESULTS)

'''
Goal: To resolve this question:
	number of commits for that requirement.
'''
def getCommitForARequirement(jira, reqName):

	return 0

def main():
	jira = JIRA({
		'server': 'https://issues.apache.org/jira'
	})

	print ("The number of open requirements: ", len(getOpenFeatures(jira)))
	print ("The number of requirements in progress: ", len(getOpenInProgressFeatures(jira)))
	print ("The number of closed or resolved issues before an issue has started being implemented: ", getNumRequirementsBeforeThis(jira, 'TIKA-2016'))
	
		''' Playing:
	  numTemp = jira.search_issues("project=TIKA and issueType=\'New Feature\' and status WAS NOT \'In Progress\' DURING (\'2017/01/01\', \'2017/8/7\')", maxResults=1000)
	  hihih = jira.search_issues("project=TIKA and issueType=\'New Feature\' AND status CHANGED FROM \'Open\' TO \'In Progress\'", maxResults=MAX_RESULTS)
	'''

if __name__ == "__main__":
	main()