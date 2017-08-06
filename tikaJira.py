from jira import JIRA
import re

options = {
	'server': 'https://issues.apache.org/jira'
}

jira = JIRA(options)
allTIKAIssue = jira.search_issues("project=TIKA")

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
def getOpenFeature():
	unimplementedIssue = []
	for issue in allTIKAIssue:
		if str(issue.fields.status) == 'Open':
			unimplementedIssue.append(issue)
	return unimplementedIssue

print (len(allTIKAIssue))
print (getOpenFeature())