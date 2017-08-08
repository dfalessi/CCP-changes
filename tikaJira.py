from jira import JIRA
import git
import re

MAX_RESULTS = 1000
TIKA_REQ_STR = "project=TIKA and issueType=\'New Feature\' AND "
TIKA_LOCAL_REPO = r"C:\Users\yiupang\Documents\CCP-REPOS\tika-master"
REQUIREMENT = 'TIKA-2016'

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
	# 1. get the time when the issue is changed to "in progress"
	issue = jira.issue(reqName, expand='changelog')
	changelog = issue.changelog
	for history in changelog.histories:
		for item in history.items:
			if item.field == 'status' and item.fromString == 'Open' and item.toString == 'In Progress':
				# print ('[DEBUG] Date:' + history.created + ' From:' + item.fromString + ' To:' + item.toString)
				startProgressDate = re.findall('(\d{4}-\d{2}-\d{2})', history.created)[0]

	# 2. all the issues have type of New Feature and status of RESOLVED or CLOSED before that time.
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
def getGitDevelopersForRequirement(reqName):
	repo = git.Repo(TIKA_LOCAL_REPO)
	logInfo = repo.git.log("--all", "-i", "--grep=" + reqName)
	if(len(logInfo) == 0):
		print ("[ERROR] No commit messages mentioned " + reqName)
	authors = re.findall('(?<=Author: )\w+', logInfo)
	# print ("[DEBUG] raw string of the logInfo: ", logInfo)
	return authors

'''
Goal: Multiple commits might be made by the same developer.
	 This function is to not print the same name multiple times.
'''
def printUniqueDevelopers(developers):
	print ("The developers worked on: " + REQUIREMENT)
	seen = set()
	uniqueDevelopers = []
	for dev in developers:
		if dev not in seen:
			uniqueDevelopers.append(dev)
			seen.add(dev)
			print ("\t" + dev)

def main():
	jira = JIRA({
		'server': 'https://issues.apache.org/jira'
	})

	print ("The number of open requirements: ", len(getOpenFeatures(jira)))
	print ("The number of requirements in progress: ", len(getOpenInProgressFeatures(jira)))
	print ("The number of closed or resolved issues before an issue has started being implemented: ", getNumRequirementsBeforeThis(jira, REQUIREMENT))
	printUniqueDevelopers(getGitDevelopersForRequirement(REQUIREMENT))

if __name__ == "__main__":
	main()