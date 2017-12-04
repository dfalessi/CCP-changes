# -*- coding: utf-8 -*-

import sys
from git import *
#from sortedcontainers import SortedList, SortedDict, SortedSet
#from files import Files
import files
reload(files)
import curloc
reload(curloc)

def printError():
    print "Invalid arguments. " \
        + "Format is \'python metrics.py [file name] "\
        + "[start index] [end index]\'"
    print "(Indexes represent the range of the commits you wish to view, \n" \
        + "with the starting index as the earlier commit \n" \
        + "and the ending index as the later commit.)"

def export(projID, f):
    with open('metrics.csv','wb') as file:
        file.write("Project ID," \
            "Class ID," \
            "Requirement ID," \
            "Size at beginning of release," \
            "LOC_touched," \
            "NR," \
            "Nfix," \
            "NAuth," \
            "LOC_added," \
            "MAX_LOC_added," \
            "AVG_LOC_added," \
            "Churn," \
            "MAX_Churn," \
            "AVG_Churn," \
            "ChgSetSize," \
            "MAX_ChgSet," \
            "AVG_ChgSet," \
            "Age," \
            "WeightedAge" \
            "\n"
            )
        items = f.files.iteritems()
        for fileName, stats in items:
            #items = stats.iteritems()
            file.write("%s,%s,%s" % (projID, fileName, "REQ_ID"))
            file.write(",%d" % (stats['size']))
            file.write(",%d" % (stats['LOC_touched']))
            file.write(",%d" % (stats['NR']))
            file.write(",%d" % (stats['Nfix']))
            file.write(",%s" % (stats['NAuth']))
            file.write(",%d" % (stats['LOC_added']))
            file.write(",%d" % (stats['MAX_LOC_added']))
            file.write(",%.2f" % (stats['AVG_LOC_added']))
            file.write(",%d" % (stats['Churn']))
            file.write(",%d" % (stats['MAX_Churn']))
            file.write(",%.2f" % (stats['AVG_Churn']))
            file.write(",%d" % (stats['ChgSetSize']))
            file.write(",%d" % (stats['MAX_ChgSet']))
            file.write(",%.2f" % (stats['AVG_ChgSet']))
            file.write(",%d" % (stats['Age']))
            file.write(",%d" % (stats['WeightedAge']))
            file.write("\n")

def main_old(argv):
    if (len(argv) != 4):
        printError()
    #repoPath = argv[1]
    '''repo = Repo(repoPath)
    assert not repo.bare
    commits = list(repo.iter_commits('master'))'''
    f = files.Files()
    '''for i in range (int(argv[2]), int(argv[3]) + 1):
        f.update(commits[i - 1])
    #print f.files'''
    f.updateCommits(argv[1], int(argv[2]), int(argv[3]))
    export("PROJ_ID", f)

def main(argv):
    test2(argv[1])

def setupCurLoc(repoPath):
    cl = curloc.CurLoc(repoPath)
    return cl;

def test2(repoPath):
    cl = setupCurLoc(repoPath)
    commits = repo = Repo(repoPath)
    assert not repo.bare
    commits = list(reversed(list(repo.iter_commits('master'))))
    l1 = [commits[18], commits[19], commits[20], commits[21], commits[22]]
    f = files.Files(cl)
    f.updateCommitsSmall(l1, 18)
    export("PROJ_ID", f)
    
def test1(repoPath):
    cl = curloc.CurLoc(repoPath)
    #cl.test()
    f = files.Files(cl)
    f.updateCommits2(repoPath, 15)
    export("PROJ_ID", f)

def test():
    repoPath = ".."
    repo = Repo(repoPath)
    assert not repo.bare
    commits = list(repo.iter_commits('master'))
    f = files.Files()
    f.update(commits[18])
    f.update(commits[17])
    print f.files

# =========================
if __name__ == '__main__':
    main(sys.argv)
    #test()