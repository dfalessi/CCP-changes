import credentials

### Local configurations ###
MAX_RESULTS = 1000
REQUIREMENT = 'TIKA-2232' # for testing purpose, TIKA-1699 has the most committs and TIKA-2016 or TIKA-2232 have the best transitions
CSV_FILE = 'TIKA-Table.csv'
TIKA_LOCAL_REPO = "C:/Users/yiupang/Documents/CCP-REPOS/tika-master"
PROJECT_URL = 'https://issues.apache.org/jira'
_TIKA_URL = "https://api.github.com/repos/apache/tika/pulls?state={}&per_page=100&page="
TIKA_PULL_REQUESTS_BY_PAGE = _TIKA_URL.format("all")
TIKA_CLOSED_PULL_REQUEST_BY_PAGE = _TIKA_URL.format("closed")

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
MASTER_REGEX = '(master)'
NO_SUCH_COMMIT_REGX = '(no such commit)'
IS_CHECKOUT_COMMAND_REGEX = '(HEAD is now at )([a-zA-Z0-9]+)'
MERGING_KEYWORDS_REGEX = '(?:merg|appl|pull|push|integrat)(?:ing|i?ed)'
CLOSING_KEYWORDS_REGEX = '(?:close|closes|closed|fix|fixes|fixed|resolve|resolves|resolved)'
CHECKOUT_COMMIT_SHA_REGEX = "(?:Note: checking out ')([A-Za-z0-9]+)(')"
# Note: checking out '4f920c7bc5fd262c2a83fe44a7fb7b7bcb2798b7'.

### Configurations for the csv file ###
# TODO