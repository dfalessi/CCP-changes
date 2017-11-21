import Perils
from Git.GitApache import GitApache
from Jira.JiraApache import JiraApache
from CSV import CSV
import re
from Utility import Utility
import sys
from Jira import JiraQuery

from Git import GitOperations

import git
from jira import JIRA

class ProjectApache:
    csvRows = None
    localRepos = None
    jiraApache = None
    gitsApache = []
    generalProjectInfo = None

    def __init__(self, jiraURL, gitURLs, localRepos):
        print("initializing jiraURL in ProjectApache = ", jiraURL)
        print("initializing gitURLS in ProjectApache = ", gitURLs)
        print("initializing localRepos in ProjectApache = ", localRepos)
        self.localRepos = localRepos
        self.jiraApache = JiraApache(re.findall(".*/(.*)", jiraURL)[0])
        for index, gitUrl in enumerate(gitURLs):
            gitProjectName = re.findall(".*/(.*).git", gitUrl)[0]
            self.gitsApache.append(
                GitApache(gitUrl, localRepos[index], gitProjectName))
        self.csvRows = self.__initCSVRows()

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
        perilsDataForAllIssues = []
        row = {key: None for key in Perils.initCSVHeaders()}

        # initialize a dictionary for calculate portions
        for issue in self.jiraApache.getAllIssuesApache():
            perilsForIssue = {key: None for key in Perils.initCSVHeaders()}
            perilsResults = issue.getPerilsResults(self.localRepos)
            allDevelopersInAllRepos = set()
            for gitApache in self.gitsApache:
                each = gitApache.getUniqueDevelopers(issue.reqName)
                print("developers for each issue = ", each)
                allDevelopersInAllRepos = allDevelopersInAllRepos | each
                print("allDeveloeprsInAllRepos after developers for each issue = ", each)
            print("allDevelopersInAllRepos = ", allDevelopersInAllRepos)
            perilsForIssue["numDevelopers"] = len(allDevelopersInAllRepos)
            perilsForIssue["numDevelopedRequirementsBeforeThisInProgress"] = perilsResults["numDevelopedRequirementsBeforeThisInProgress"]
            perilsForIssue["portionOpenWhileThisOpen"] = perilsResults['portionOpenWhileThisOpen']
            perilsForIssue["portionInProgressWhileThisOpen"] = perilsResults['portionInProgressWhileThisOpen']
            perilsForIssue["portionResolvedWhileThisOpen"] = perilsResults['portionResolvedWhileThisOpen']
            perilsForIssue["portionReopenedWhileThisOpen"] = perilsResults['portionReopenedWhileThisOpen']
            perilsForIssue["portionClosedWhileThisOpen"] = perilsResults['portionClosedWhileThisOpen']
            perilsForIssue["portionOpenWhenThisInProgress"] = perilsResults['portionOpenWhenThisInProgress']
            perilsForIssue["portionInProgressWhenThisInProgress"] = perilsResults["portionInProgressWhenThisInProgress"]
            perilsForIssue["portionReopenedWhenThisInProgress"] = perilsResults["portionReopenedWhenThisInProgress"]
            perilsForIssue["portionResolvedWhenThisInProgress"] = perilsResults["portionResolvedWhenThisInProgress"]
            perilsForIssue["portionClosedWhenThisInProgress"] = perilsResults["portionClosedWhenThisInProgress"]
            for key in perilsResults["numDescChangedCounters"]:
                perilsForIssue["numDesc{}".format(key.replace(
                    " ", ""))] = perilsResults["numDescChangedCounters"][key]
            for key in perilsResults["transitionCounters"]:
                perilsForIssue[key] = perilsResults["transitionCounters"][key]
            for key in perilsResults["numCommitsEachStatus"]:
                perilsForIssue["numCommits{}".format(key.replace(
                    " ", ""))] = perilsResults["numCommitsEachStatus"][key]
            perilsDataForAllIssues.append(perilsForIssue)

        # Calculates portion of each peril.
        for key in row:
            # generalProjectInfo have not sumed metrics
            if key not in Perils.generalProjectInfo and not key in Perils.oldperils9:
                row[key] = self.__getRatioForOneColumnOfPERIL(key,
                                                              self.__getPERILSList(
                                                                  key),
                                                              perilsDataForAllIssues)  # getMappingFrom column to perils
        # Calculates metrics that don't need SUM.
        row["PRMergedByNonGithub"] = 0
        h1 = gitApache.getPercentageByH1()
        h2 = gitApache.getPercentageByH2()
        h3 = gitApache.getPercentageByH3()
        h4 = gitApache.getPercentageByH4()
        print("h1 = ", h1)
        print("h2 = ", h2)
        print("h3 = ", h3)
        print("h4 = ", h4)
        for gitApache in self.gitsApache:
            row["PRMergedByNonGithub"] += h1 + h2 + h3 + h4
        row["project"] = self.jiraApache.jiraProjectName
        row["numOpenRequirements"] = self.jiraApache.getNumOpenFeatures()
        row["numInProgressRequirements"] = self.jiraApache.getNumInProgressFeatures()
        row["portionOfCommitsWithUnassignedTask"] = self.getPortionOfCommitsWithUnassignedTask()
        row["numBranches"] = 0
        for gitApache in self.gitsApache:
            row["numBranches"] += gitApache.getNumberBranches()

        print("perilsForIssue = ", perilsForIssue)
        return row


    '''
    Get the percentage of commits with unassigned tasks
    PERILS-30
    '''
    def getPortionOfCommitsWithUnassignedTask(self):
        totalNumCommits = 0
        numUnassignedTaskWithCommits = 0

        unassignedIssues = JiraQuery.getUnassignedIssues(JIRA({
                'server': 'https://issues.apache.org/jira'
            }), self.jiraApache.jiraProjectName)

        for localRepo in self.localRepos:
            allSha = GitOperations.executeGitShellCommand(
                localRepo, ["git log --all --pretty=format:'%H' | wc -l"])
            totalNumCommits += int (allSha.replace(" ", ""))

        for localRepo in self.localRepos:
            repo = git.Repo(localRepo)
            for issue in unassignedIssues:
                logInfo = repo.git.log("--all", "-i", "--grep=" + issue)
                if logInfo != "":
                    numUnassignedTaskWithCommits += 1
        print ("numUnassignedTaskWithCommits = ", numUnassignedTaskWithCommits)
        print ("totalNumCommits = ", totalNumCommits)
        return round(numUnassignedTaskWithCommits / totalNumCommits, 2)


    '''
  It finds the peril that passed key belongs to.
  '''

    def __getPERILSList(self, key):
        if key in Perils.perils6:
            return Perils.perils6
        elif key in Perils.perils12:
            return Perils.perils12
        elif key in Perils.perils11:
            return Perils.perils11
        elif key in Perils.perils3:
            return Perils.perils3
        elif key in Perils.perils16:
            return Perils.perils16
        elif key in Perils.perils7:
            return Perils.perils7
        elif key in Perils.perils2:
            return Perils.perils2
        elif key in Perils.perils27:
            return Perils.perils27
        elif key in Perils.perils30:
            return Perils.perils30
        else:
            print(key, "is not found in any perils.")
            sys.exit()

    '''
  It calculates the sum of all values in a column for colName.
  @param colName - the name of a column for which the sum is calculated
  '''

    def __getColumnSum(self, colName, perilsDataForAllIssues):
        r = [item[colName]
             for item in perilsDataForAllIssues if isinstance(item[colName], int)]
        return sum(r)

    '''
  It loops a list of colName to the sum of values of columns for a peril. 
  @param colNames - a list of colNames for a peril
  '''

    def __getPERILSum(self, colNames, perilsDataForAllIssues):
        allColumnsSum = 0
        for colName in colNames:
            allColumnsSum += self.__getColumnSum(colName,
                                                 perilsDataForAllIssues)
        return allColumnsSum

    '''
  Calculate the ratio of colName's sum / allColumnsSum
  @param colName - the column for which a ratio is calculated
  @param colNames - the columns of a peril that colName belongs to
  '''

    def __getRatioForOneColumnOfPERIL(self, colName, colNames, perilsDataForAllIssues):
        allColumnSum = self.__getPERILSum(colNames, perilsDataForAllIssues)
        allColumnFunc = self.__getColumnSum(colName, perilsDataForAllIssues)
        if len(colNames) == 1:  # handles perils6-numDevelopers and perils12-numDevelopedRequirementThisInProgress
            return allColumnFunc
        return 0 if allColumnSum == 0 else round(allColumnFunc / allColumnSum, 2)
