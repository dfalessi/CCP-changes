from jira import JIRA
import re


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
	return jira.search_issues("project=TIKA and issueType=\'New Feature\' and status=\'Open\'", maxResults=1000)

'''
Goal: To resolve this question:
		for each requirement in Tika, compute how many requirements have been implemented (resolved or closed) 
	before this requirement started to be implemented (i.e., until it became in porgress).
'''
def getNumRequirementsBeforeThis(jira, reqName):
	# 1. Get requirements until this requriement order by the completedTime.
	# 2. Count the number of the requirements.
	return None

'''
Goal: To resolve this question:
	how many requirement have started to be implemented but are not completely implemented.
'''
def getOpenInProgressFeatures(jira):
	return jira.search_issues("project=TIKA and issueType=\'New Feature\' and status=\'In Progress\'", maxResults=1000)

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
	# testing: print (jira.issue("TIKA-2232").fields.assignee)

if __name__ == "__main__":
	main()