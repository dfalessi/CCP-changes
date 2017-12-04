import itertools
import sys
import time
from git import *

class CurLoc:
    
    def __init__(self, repoPath):
        self.files = dict()
        self.setup(repoPath)
    
    def setup(self, repoPath):
        repo = Repo(repoPath)
        assert not repo.bare
        commits = list(reversed(list(repo.iter_commits('master'))))
        for i in range (len(commits)):
            stat = commits[i].stats
            commitFiles = stat.files
            for fileName, stats in commitFiles.items():
                if fileName not in self.files:
                    self.addNew(fileName, stats, i)
                else:
                    self.updateFile(fileName, stats, i)
        #return begLoc;

    def addNew(self, fileName, stats, i):
        locs = [0] * (i + 1)
        locs += [stats['insertions']]
        self.files.update({fileName : locs})
    
    def updateFile(self, fileName, stats, i):
        locs = self.files[fileName]
        #print type(locs)
        entry = locs[len(locs) - 1]
        current = entry + stats['insertions'] - stats['deletions']
        locs += [entry] * (i - len(locs) + 1)
        locs += [current]
        '''
        if fileName == "tikaJira.py":
            print locs;
        '''
        # entry += [(i, stats['insertions'] - stats['deletions'])]
    
    def test(self):
        locs = self.files['tikaJira.py']
        #entry = locs[15]
        #locs += [current] * (i - len(locs) + 1)
        '''
        for i in range(0, 20):
            print i, locs[i]
        '''