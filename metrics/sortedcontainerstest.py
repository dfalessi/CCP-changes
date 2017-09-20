# http://www.grantjenks.com/docs/sortedcontainers/
# https://github.com/gitpython-developers/GitPython

import sys
from git import *
from sortedcontainers import SortedList, SortedDict, SortedSet

def addToDict(commit, files):
    stat = commit.stats
    commitFiles = stat.files
    print commitFiles
    #print '\n'
    for fileName, stats in commitFiles.items():
        if fileName not in files:
            files.update({fileName : stats})
        else:
            updateFile(fileName, stats, files)

def updateFile(fileName, stats, files):
    files[fileName]['deletions'] += stats['deletions']
    files[fileName]['lines'] += stats['lines']
    files[fileName]['insertions'] += stats['insertions']

def printLocTouched(files):
    #print "-- LOC_touched --"
    printTitle("LOC_touched")
    for fileName, stats in files.items():
        print ("%30s: %6d" % (fileName, stats['lines']))
    print "\n"

def printTitle(title):
    print ("-- %s --\n" % (title))

def main(argv):
    files = SortedDict()

    # Setup GitHub repo
    repoPath = ".."
    if (len(argv) > 1):
        repoPath = argv[1]
    repo = Repo(repoPath)
    assert not repo.bare
    
    # get repo's commits
    commits = list(repo.iter_commits('master'))
    
    addToDict(commits[18], files)
    addToDict(commits[19], files)
    #print files
    printLocTouched(files)

# =========================
if __name__ == '__main__':
    main(sys.argv)
