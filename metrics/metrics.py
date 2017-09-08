# -*- coding: utf-8 -*-

import sys
from git import *
#from sortedcontainers import SortedList, SortedDict, SortedSet
#from files import Files
import files
reload(files)

def printError():
    print "Invalid arguments. " \
        + "Format is \'python metrics.py [file name] "\
        + "[start index] [end index]\'"
    print "(Indexes represent the range of the commits you wish to view, \n" \
        + "with the starting index as the earlier commit \n" \
        + "and the ending index as the later commit.)"

def main(argv):
    if (len(argv) != 4):
        printError()
    repoPath = argv[1]
    repo = Repo(repoPath)
    assert not repo.bare
    commits = list(repo.iter_commits('master'))
    f = files.Files()
    for i in range (int(argv[2]), int(argv[3]) + 1):
        f.update(commits[i - 1])
    print f.files

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