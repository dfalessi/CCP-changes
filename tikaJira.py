from jira import JIRA
import git
import re
import csv
import json
import urllib.request

MAX_RESULTS = 1000
TIKA_REQ_STR = "project=TIKA AND issueType=\'New Feature\' AND "
TIKA_LOCAL_REPO = r"C:\Users\yiupang\Documents\CCP-REPOS\tika-master"
REQUIREMENT = 'TIKA-2016' # for testing purpose
CSV_FILE = 'TIKA-Table.csv'

'''
Goal: To resolve this question:
	For each requirement compute how many times it was reopened.
'''
def getReopenTimes(jira, reqName):
	return jira.search_issues(TIKA_REQ_STR + "status WAS \'Reopened\' AND key = " + reqName, maxResults=MAX_RESULTS)
	#print (json.dumps(parsed, indent=4, sort_keys=True))

'''
Goal: To resolve this question:
	how many requirements are already defined in Jira but their implementation has not started yet.
'''
def getOpenFeatures(jira):
	return jira.search_issues(TIKA_REQ_STR + "status=\'Open\'", maxResults=MAX_RESULTS)

def getHistories(jira, reqName):
	issue = jira.issue(reqName, expand='changelog')
	return issue.changelog.histories

'''
Goal: To resolve PERILS-11 - Changed
'''
def getNumDescChanged(jira, reqName):
	counter = 0
	for history in getHistories(jira, reqName):
		for item in history.items:
			if(item.field == 'description'):
				counter += 1
	return counter

'''
Goal: To resolve this question:
		for each requirement in Tika, compute how many requirements have been implemented (resolved or closed) 
	before this requirement started to be implemented (i.e., until it became in porgress).

	Resolved vs Closed ?
	
'''
def getNumRequirementsBeforeThis(jira, reqName):
	startProgressDate = None
	for history in getHistories(jira, reqName):
		for item in history.items:
			if item.field == 'status' and item.toString == 'In Progress':
				# print ('[DEBUG] Date:' + history.created + ' From:' + item.fromString + ' To:' + item.toString)
				startProgressDate = re.findall('(\d{4}-\d{2}-\d{2})', history.created)[0]

	# 2. all the issues have type of New Feature and status of RESOLVED or CLOSED before that time.
	if startProgressDate != None:
		allIssueBeforeThis = jira.search_issues(TIKA_REQ_STR + "status WAS IN (\'Resolved\', \'Closed\') BEFORE " + startProgressDate, maxResults=MAX_RESULTS)
		numIssueBeforeThis = len(allIssueBeforeThis)
		return numIssueBeforeThis
	else:# this issue has no "In Progress" phase.
		return -1

'''
Goal: To resolve this question:
	how many requirement have started to be implemented but are not completely implemented.
'''
def getOpenInProgressFeatures(jira):
	return jira.search_issues(TIKA_REQ_STR + "status=\'In Progress\'", maxResults=MAX_RESULTS)

'''
Goal: To resolve this question:
	developers for that requirement.
'''
def getGitDevelopersForThisReq(reqName):
	repo = git.Repo(TIKA_LOCAL_REPO)
	logInfo = repo.git.log("--all", "-i", "--grep=" + reqName)
	if(len(logInfo) == 0):
		return []
	else:
		developers = re.findall('(?<=Author: )([a-zA-Z ]+)', logInfo)
		formattedDevelopers = []
		for dev in developers: #delete the last white space character detected by the regex
			formattedDevelopers.append(dev[:-1])
		return formattedDevelopers

'''
Goal: Multiple commits might be made by the same developer.
	 This function is to not print the same name multiple times.
'''
def getUniqueDevelopers(developers, reqName):
	seen = set()
	uniqueDevelopers = []
	for dev in developers:
		if dev not in seen:
			uniqueDevelopers.append(dev)
			seen.add(dev)
	return uniqueDevelopers

'''
Goal: Loop all the issues of TIKA to compute the following two matrixes:
	1. The number of closed or resolved issues before each requirement has started being implemented
	2. Developers for each requirement.
'''
def printTicketInfoForReqs(jira):
	requirements = jira.search_issues("project=TIKA AND issueType=\'New Feature\'")
	for req in requirements:
		print ("Ticket's id: " + req.key)
		print ("reqBeforeThis:", getNumRequirementsBeforeThis(jira, req.key))
		developers = getUniqueDevelopers(getGitDevelopersForThisReq(req.key), req.key)
		print ("numDevelopers: ", len(developers))
		#print ("developers:", developers)
		print ("numDescChanged:", getNumDescChanged(jira, req.key))
		print ("\n\n\n")

'''
Goal: Loop all the issues of TIKA to compute the following two matrixes and output them to a csv file.
'''
def outputCSVFile(jira):
	with open(CSV_FILE, 'w', newline='') as csvfile:
		fieldnames = ['numOpenRequirements', 'numInProgressRequirements', 'ticket', 'numRequirementsBeforeThis', 'numDevelopers', "numDescChanged"]
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		writer.writeheader()
		writer.writerow({'numOpenRequirements': len(getOpenFeatures(jira)), 
			'numInProgressRequirements': len(getOpenInProgressFeatures(jira))})
		for req in jira.search_issues("project=TIKA AND issueType=\'New Feature\'"):
			writer.writerow({'ticket': req.key,
				'numRequirementsBeforeThis': getNumRequirementsBeforeThis(jira, req.key),
				'numDevelopers': len(getUniqueDevelopers(getGitDevelopersForThisReq(req.key), req.key)),
				'numDescChanged': getNumDescChanged(jira, req.key)
			})


def main():
	jira = JIRA({
		'server': 'https://issues.apache.org/jira'
	})
	# print ("The number of open requirements: ", len(getOpenFeatures(jira)))
	# print ("The number of requirements in progress: ", len(getOpenInProgressFeatures(jira)))
	# printTicketInfoForReqs(jira)
	# testing: getGitDevelopersForThisReq(REQUIREMENT)
	outputCSVFile(jira)
	# print (getReopenTimes(jira, 'TIKA-1913'))

if __name__ == "__main__":
	main()