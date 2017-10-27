import json
import traceback
import Git
from urllib.request import Request, urlopen


STATE_STR = "status"
OPEN_STR = "Open"
IN_PROGRESS_STR = "In Progress"
REOPENED_STR = "Reopened"
RESOLVED_STR = "Resolved"
CLOSED_STR = "Closed"
STATUSES = [OPEN_STR, IN_PROGRESS_STR, REOPENED_STR, RESOLVED_STR, CLOSED_STR]

'''
It returns a dictionary that has all possible transitions of status in JIRA.
'''
def getAllPossibleTransitions():
    transitions = {}
    for indx, val in enumerate(STATUSES):
        for indx2, val2 in enumerate(STATUSES):
            if indx != indx2:
                transitions[val + "|" + val2] = [val, val2]
    return transitions

'''
Convert String of a JSON from the git api to a dictionary.
'''
def convertDictStringToDict(dictStr):
  return json.loads(dictStr.decode("utf-8"))

def prettyPrintJSON(dict):
    try:
        print (json.dumps(dict.decode("utf-8"), indent=2))
    except:
        print ("Failed on dump ", dict)

def getCurrentRateLimit():
    rateLimitURL = "https://api.github.com/rate_limit"
    try:
        request = Request(rateLimitURL)
        request.add_header("Authorization", "token %s" % Git.credentials.personal_access_token)
        response = urlopen(request)
        return response.read()
    except:
        print("Failed on reading ", rateLimitURL)
        traceback.print_exc()

def getGoodWindowFileName(projectName):
    invalidCharForFile = ['/', '\\', ':', '*', '?', '\', '"', '<', '>', '|'"]
    goodGitProjectName = None
    for c in invalidCharForFile:
        goodGitProjectName = projectName.replace(c, "-")
    return goodGitProjectName
