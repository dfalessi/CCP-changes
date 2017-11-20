from Utility import Utility

'''
It's bad practice :(. Global variables are evils.
it initializes a list of strings of the headers. It's used in Main.py and ProjectApache.py
'''
generalProjectInfo = ["project",
                      "numOpenRequirements", "numInProgressRequirements"]
oldperils9 = ["PRMergedByNonGithub"]
perils6 = ["numDevelopers"]
perils12 = ["numDevelopedRequirementsBeforeThisInProgress"]
perils11 = ["portionDescOpen",
            "portionDescInProgress",
            "portionDescResolved",
            "portionDescReopened",
            "portionDescClosed"]
perils3 = ["portionCommitsOpen",
           "portionCommitsInProgress",
           "portionCommitsResolved",
           "portionCommitsReopened",
           "portionCommitsClosed"]
perils16 = ["portionOpenWhileThisOpen",
            "portionInProgressWhileThisOpen",
            "portionResolvedWhileThisOpen",
            "portionReopenedWhileThisOpen",
            "portionClosedWhileThisOpen"]
perils7 = ["portionOpenWhenThisInProgress",
           "portionInProgressWhenThisInProgress",
           "portionResolvedWhenThisInProgress",
           "portionReopenedWhenThisInProgress",
           "portionClosedWhenThisInProgress"]
perils27 = ["numBranches"]
perils30 = ["getPortionOfCommitsWithUnassignedTask"]
perils2 = [key for key in Utility.getAllPossibleTransitions()]


def initCSVHeaders():
    columnsNames = []
    columnsNames += generalProjectInfo
    columnsNames += oldperils9
    columnsNames += perils6 + perils12 + perils11 + perils3
    columnsNames += perils16 + perils7 + perils2 + perils27 + perils30
    return columnsNames
