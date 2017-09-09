
### Local configurations ###
MAX_RESULTS = 1000
REQUIREMENT = 'TIKA-2232' # for testing purpose, TIKA-1699 has the most committs and TIKA-2016 or TIKA-2232 have the best transitions
CSV_FILE = 'TIKA-Table.csv'
TIKA_LOCAL_REPO = r"C:\Users\yiupang\Documents\CCP-REPOS\tika-master"
PROJECT_URL = 'https://issues.apache.org/jira'

### A common query for a requirenment ###
PROJECT_NAME = "TIKA"
TIKA_REQ_STR = "project=" + PROJECT_NAME + " AND issueType=\'New Feature\'"
TIKA_REQ_STR_WHERE = TIKA_REQ_STR + " AND "

### For datetime library to parse time ###
GIT_JIRA_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'
GIT_DATE_FORMAT = "%a %b %d %H:%M:%S %Y"

### Statueses ###
'''
Goal: Get all possible transitions
'''
def getAllPossibleTransitions():
  transitions = {}
  for indx, val in enumerate(STATUSES):
    for indx2, val2 in enumerate(STATUSES):
      if indx != indx2:
        transitions[val+"|"+val2] = [val, val2]
  return transitions

STATE_STR = "status"
OPEN_STR = "Open"
IN_PROGRESS_STR = "In Progress"
REOPENED_STR = "Reopened"
RESOLVED_STR = "Resolved"
CLOSED_STR = "Closed"
STATUSES = [OPEN_STR, IN_PROGRESS_STR, REOPENED_STR, RESOLVED_STR, CLOSED_STR]
TRANSITIONS = getAllPossibleTransitions()#a <transition>|<transition2> of dictionary

### Strings used by dictionary ### 
END_TIME = "endTime"
START_TIME = "startTime"

### REGEX to parse dates in JIRA API and GitHub API ###
JIRA_DATE_TIME_REGEX = '(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})'
JIRA_DATE_REGEX = '(\d{4}-\d{2}-\d{2})'
COMMIT_DATE_REGEX = '(?<=Date:   )([A-Za-z0-9: ]+)'
AUTHOR_REGEX = '(?<=Author: )([a-zA-Z ]+)'


### Configurations for the csv file ###
# TODO