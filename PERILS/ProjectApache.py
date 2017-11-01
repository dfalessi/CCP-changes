f
om Git.GitApache import GitApache
from Jira.JiraApache import JiraApache
from CSV import CSV
import re
from Utility import Utility
import sys

class ProjectApache:
  localRepos = None
  jiraApache = None
  gitsApache = []
  csv = None
  columns = None
  generalProjectInfo = None
  oldperils9 = None
  perils6 = None
  perils12 = None
  perils11 = None
  perils3 = None
  perils16 = None
  perils7 = None
  perils2 = None


  def __init__(self, jiraURL, gitURLs, csvURL, localRepos):
    print("initializing jiraURL in ProjectApache = ", jiraURL)
    print("initializing gitURLS in ProjectApache = ", gitURLs)
    print("initializing csvURL in ProjectApache = ", csvURL)
    print("initializing localRepos in ProjectApache = ", localRepos)
    self.generalProjectInfo = ["project",
                               "numOpenRequirements",
                               "numInProgressRequirements"]
    self.oldperils9 = ["PRMergedByNonGithub"]
    self.perils6 = ["numDevelopers"]
    self.perils12 = ["numDevelopedRequirementsBeforeThisInProgress"]
    self.perils11 = ["numDescOpen",
                     "numDescInProgress",
                     "numDescResolved",
                     "numDescReopened",
                     "numDescClosed"]
    self.perils3 = ["numCommitsOpen",
                    "numCommitsInProgress",
                    "numCommitsResolved",
                    "numCommitsReopened",
                    "numCommitsClosed"]
    self.perils16 = ["numOpenWhileThisOpen",
                     "numInProgressWhileThisOpen",
                     "numResolvedWhileThisOpen",
                     "numReopenedWhileThisOpen",
                     "numClosedWhileThisOpen"]
    self.perils7 = ["numOpenWhileThisOpen",
                    "numInProgressWhileThisOpen",
                    "numResolvedWhileThisOpen",
                    "numReopenedWhileThisOpen",
                    "numClosedWhileThisOpen"]
    self.perils2 = [key for key in Utility.getAllPossibleTransitions()]
    self.localRepos = localRepos
    self.columns = self.__initCSVHeaders()
    self.jiraApache = JiraApache(re.findall(".*/(.*)", jiraURL)[0])
    for index, gitUrl in enumerate(gitURLs):
      gitProjectName = re.findall(".*/(.*).git", gitUrl)[0]
      self.gitsApache.append(GitApache(gitUrl, localRepos[index], gitProjectName))
    self.csv = CSV.CSV(csvURL, self.__initCSVHeaders(), self.__initCSVRows())


  # it initializes a list of strings of the headers
  def __initCSVHeaders(self):
    columnsNames = []
    columnsNames += self.generalProjectInfo
    columnsNames += self.oldperils9
    columnsNames += self.perils6 + self.perils12 + self.perils11 + self.perils3
    columnsNames += self.perils16 + self.perils7 + self.perils2
    return columnsNames


  '''
    for each issue in issues of jiraApache
      row = columnsName
      perilsResults = issue.getJIRAItemsHistory()
      align all the columns in row in perilsResults
      row[numOpenRequirements] = jiraApache.getNumOpenFeatures
      row[numInProgressRequirements] = jiraApache.getNumInProgressFeatures
      row[numDevelopers] = self.gitsApache.getNumUniqueDevelopers(issue.reqNAme)
    return the row dict to al CSV project
  '''
  def __initCSVRows(self):
    count = 0
    perilsDataForAllIssues = []
    row = {key : None for key in self.__initCSVHeaders()}

    # initialize a dictionary for calculate portions
    for issue in self.jiraApache.getAllIssuesApache():
      #if (count == 3):
      #  break
      perilsForIssue = {key : None for key in self.__initCSVHeaders()}
      perilsResults = issue.getPerilsResults(self.localRepos)
      totalNumDevelopersInAllRepos = 0
      for gitApache in self.gitsApache:
        totalNumDevelopersInAllRepos += gitApache.getNumUniqueDevelopers(issue.reqName)
      print ("number of unique developers = ", totalNumDevelopersInAllRepos)
      perilsForIssue["numDevelopers"] = totalNumDevelopersInAllRepos
      perilsForIssue["numDevelopedRequirementsBeforeThisInProgress"] = perilsResults["numDevelopedRequirementsBeforeThisInProgress"]
      perilsForIssue["numOpenWhileThisOpen"] = perilsResults['numOpenWhileThisOpen']
      perilsForIssue["numInProgressWhileThisOpen"] = perilsResults['numInProgressWhileThisOpen']
      perilsForIssue["numResolvedWhileThisOpen"] = perilsResults['numResolvedWhileThisOpen']
      perilsForIssue["numReopenedWhileThisOpen"] = perilsResults['numReopenedWhileThisOpen']
      perilsForIssue["numClosedWhileThisOpen"] = perilsResults['numClosedWhileThisOpen']
      perilsForIssue["numOpenWhenInProgress"] = perilsResults['numOpenWhenInProgress']
      perilsForIssue["numInProgressWhenInProgress"] = perilsResults["numInProgressWhenInProgress"]
      perilsForIssue["numReopenedWhenInProgress"] = perilsResults["numReopenedWhenInProgress"]
      perilsForIssue["numResolvedWhenInProgress"] = perilsResults["numResolvedWhenInProgress"]
      perilsForIssue["numClosedWhenInProgress"] = perilsResults["numClosedWhenInProgress"]
      for key in perilsResults["numDescChangedCounters"]:
        perilsForIssue["numDesc{}".format(key.replace(" ", ""))] = perilsResults["numDescChangedCounters"][key]
      for key in perilsResults["transitionCounters"]:
        perilsForIssue[key] = perilsResults["transitionCounters"][key]
      for key in perilsResults["numCommitsEachStatus"]:
        perilsForIssue["numCommits{}".format(key.replace(" ", ""))] = perilsResults["numCommitsEachStatus"][key]
      perilsDataForAllIssues.append(perilsForIssue)

    # Calculates portion of each peril.
    for key in row:
      if key not in self.generalProjectInfo and not key in self.oldperils9: # generalProjectInfo have not sumed metrics
          row[key] = self.__getRatioForOneColumnOfPERIL(key,
                                                        self.__getPERILSList(key),
                                                        perilsDataForAllIssues) # getMappingFrom column to perils
    # Calculates metrics that don't need SUM.
    row["PRMergedByNonGithub"] = 0
    for gitApache in self.gitsApache:
      row["PRMergedByNonGithub"] += gitApache.getPercentageByH1() + gitApache.getPercentageByH2() +\
                                    gitApache.getPercentageByH3() + gitApache.getPercentageByH4()
    row["project"] = self.jiraApache.jiraProjectName
    row["numOpenRequirements"] = self.jiraApache.getNumOpenFeatures()
    row["numInProgressRequirements"] = self.jiraApache.getNumInProgressFeatures()

    return row


  '''
  It finds the peril that passed key belongs to.
  '''
  def __getPERILSList(self, key):
    if key in self.perils6:
      return self.perils6
    elif key in self.perils12:
      return self.perils12
    elif key in self.perils11:
      return self.perils11
    elif key in self.perils3:
      return self.perils3
    elif key in self.perils16:
      return self.perils16
    elif key in self.perils7:
      return self.perils7
    elif key in self.perils2:
      return self.perils2
    else:
      print (key, "is not found in any perils.")
      sys.exit()


  '''
  It calculates the sum of all values in a column for colName.
  @param colName - the name of a column for which the sum is calculated
  '''
  def __getColumnSum(self, colName, perilsDataForAllIssues):
    r = [item[colName] for item in perilsDataForAllIssues if isinstance(item[colName], int)]
    return sum(r)


  '''
  It loops a list of colName to the sum of values of columns for a peril. 
  @param colNames - a list of colNames for a peril
  '''
  def __getPERILSum(self, colNames, perilsDataForAllIssues):
    allColumnsSum = 0
    for colName in colNames:
      allColumnsSum += self.__getColumnSum(colName, perilsDataForAllIssues)
    return allColumnsSum


  '''
  Calculate the ratio of colName's sum / allColumnsSum
  @param colName - the column for which a ratio is calculated
  @param colNames - the columns of a peril that colName belongs to
  '''
  def __getRatioForOneColumnOfPERIL(self, colName, colNames, perilsDataForAllIssues):
    Utility.prettyPrintJSON(perilsDataForAllIssues);
    allColumnSum = self.__getPERILSum(colNames, perilsDataForAllIssues)
    allColumnFunc = self.__getColumnSum(colName, perilsDataForAllIssues) 
    if len(colNames) == 1: # handles perils6-numDevelopers and perils12-numDevelopedRequirementThisInProgress
      return allColumnFunc
    return 0 if allColumnSum == 0 else round(allColumnFunc / allColumnSum, 2)


  '''
  It output all metrics to a csv file.
  '''
  def toCSVFile(self):
    # fd = open('document.csv', 'a')
    # fd.write(myCsvrow)
    # fd.close()
    return self.csv.outputCSVFile()

