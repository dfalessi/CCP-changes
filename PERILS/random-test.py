from Git import GitOperations
from Git.GitApache import GitApache
from Utility import Utility
from jira import JIRA
import collections
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
      print ("initializing issue = ", reqName)
      print ("initializing jiraProjectName = ", jiraProjectName)
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
      self.descriptionChangedCounters = {key : 0 for key in Utility.STATUSES}
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
          createdTime = re.findall('(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', history.created)[0]
          for indx, item in enumerate(history.items):
              if item.field == Utility.STATE_STR and self.currentStatus != item.toString:
                  result = callback(item, createdTime)
              if item.field == Utility.STATE_STR and item.field in Utility.STATUSES:
                  self.currentStatus = item.toString
      return result

oneIssue = Issue("TIKA-1699", 
  JIRA({'server': 'https://issues.apache.org/jira'}), 
  "tika")


print (oneIssue.getNumEachTransition())
