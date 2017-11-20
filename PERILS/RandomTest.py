import collections
from Git import GitOperations
from Git.GitApache import GitApache
from Utility import Utility
from jira import JIRA

import re


class Issue:
    histories = None
    END_TIME_STR = "endTime"
    START_TIME_STR = "startTime"
    TRANSITIONS = None  # a <transition>|<transition2> of dictionary
    descriptionChangedCounters = {}
    transitionCounters = {}
    startProgressTime = None
    openEndingTime = None  # PERILS-16
    statusTracking = None
    openTimeTracking = statusTracking = None  # PERILS-3
    isJustOpen = False  # PERILS-3
    dateRangeEachState = collections.OrderedDict()  # PERILS-3
    dateRangeEachState.clear()
    descriptionChangedCounters = None
    transitionCounters = None

    def __init__(self, reqName, jiraAPI, jiraProjectName):
        print("initializing issue = ", reqName)
        print("initializing jiraProjectName = ", jiraProjectName)
        self.reqName = reqName
        self.jiraAPI = jiraAPI
        self.jiraProjectName = jiraProjectName
        self.TRANSITIONS = Utility.getAllPossibleTransitions()

    '''
  To resolve PERILS-2: transitions
  '''

    def getNumEachTransition(self):
        self.__getHistoryItems(self.__initNumEachTransition)
        return self.transitionCounters

    def __initNumEachTransition(self, item, _):
        if item.toString in Utility.STATUSES:
            key = self.currentStatus + "|" + item.toString
            self.transitionCounters[key] += 1

    def __initCounters(self):
        self.descriptionChangedCounters = {}
        self.transitionCounters = {}
        self.startProgressTime = None
        self.openEndingTime = None  # PERILS-16
        self.openTimeTracking = self.statusTracking = None  # PERILS-3
        self.isJustOpen = False  # PERILS-3
        self.dateRangeEachState = collections.OrderedDict()  # PERILS-3
        self.dateRangeEachState.clear()
        self.descriptionChangedCounters = {key: 0 for key in Utility.STATUSES}
        self.transitionCounters = {key: 0 for key in self.TRANSITIONS}

    def __replaceNonPredefinedStatus(self, items):
        for item in items:
            if item.field == "status":
                if item.fromString not in Utility.STATUSES:
                    item.fromString = Utility.ANOTHER_STR
                if item.toString not in Utility.STATUSES:
                    item.toString = Utility.ANOTHER_STR
    '''
  A call to JIRA API to get the changelog
  '''

    def __initHistories(self):
        issue = self.jiraAPI.issue(self.reqName, expand='changelog')
        self.histories = issue.changelog.histories

    def __getHistoryItems(self, callback):
        self.__initHistories()
        self.__initCounters()
        result = {}
        self.currentStatus = Utility.OPEN_STR
        for history in self.histories:
            self.__replaceNonPredefinedStatus(history.items)
            createdTime = re.findall(
                '(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', history.created)[0]
            for indx, item in enumerate(history.items):
                if item.field == Utility.STATE_STR and self.currentStatus != item.toString:
                    result = callback(item, createdTime)
                if item.field == Utility.STATE_STR and item.toString in Utility.STATUSES:
                    self.currentStatus = item.toString
        return result


# oneIssue = Issue("TIKA-1699",
#                 JIRA({'server': 'https://issues.apache.org/jira'}),
#                 "tika")

qwe = "Merge branch 'master' of https://github.com/leopangchan/Cal-Poly-Courses"
# print (re.findall("(Merge branch 'master')", qwe))
# print (re.findall("(Merge branch 'master')", "    Tt 2017 11 001: Hearing List page"))

calpolyC = "/Users/yiupangchan/Documents/github/Cal-Poly-Courses"
shaC = "75811b9cbc5ceaae66f6b9d2b9e2fb373ec556c0"
shaC2 = "c6a12e6082dda6a9af903a1c7934e3bb39cfe143"
w = GitOperations.executeGitShellCommand(
    calpolyC, ["git when-merged -l {}".format(shaC2)])

dd = "/Users/yiupangchan/Documents/github/dd-TranscriptionTool-3.0"
shadd = "32eadf9b3a2dc07c549e154e44b2e1ac58b8ae0b"
#w = GitOperations.executeGitShellCommand(dd, ["git when-merged -l {}".format(shadd)])
'''
print (w)
from_master = len(re.findall("(master                      Commit is directly on this branch.)", w)) > 0 or len(re.findall("(Merge branch 'master')", w)) > 0
print (len(re.findall("(master                      Commit is directly on this branch.)", w)))
print (len(re.findall("(Merge branch 'master')", w)))
print (from_master)
'''

'''
In commit class
'''


def isCommittedThroughMaster(sha):
    consoleOutput = GitOperations.executeGitShellCommand(
        calpolyC, ["git when-merged -l {}".format(sha)])
    print(consoleOutput)
    isDirectCommit = len(re.findall(
        "(master                      Commit is directly on this branch.)", consoleOutput)) > 0
    isMergedMaster = len(re.findall(
        "(Merge branch 'master')", consoleOutput)) > 0
    print("isDirectCommit = ", isDirectCommit)
    print("isMergedMaster = ", isMergedMaster)
    return isDirectCommit or isMergedMaster


'''
In main
'''


def getPortionOfCommitsThroughMasterBranch():
    totalNumCommitOnMaster = int(GitOperations.executeGitShellCommand(
        calpolyC, ["git rev-list --count master"]))
    allShaOnMaster = GitOperations.executeGitShellCommand(
        calpolyC, ["git log --pretty=format:'%H'"]).split("\n")
    totalNumCommitThroughMaster = 0
    for sha in allShaOnMaster:
        if isCommittedThroughMaster(sha):
            totalNumCommitThroughMaster += 1
        else:
            print("not committed through master = ", sha)

    print("totalNumCommitOnMaster = ", totalNumCommitOnMaster)
    print("totalNumCommitThroughMaster = ", totalNumCommitThroughMaster)
    return 0


getPortionOfCommitsThroughMasterBranch()
