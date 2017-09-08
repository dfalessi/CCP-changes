# -*- coding: utf-8 -*-
# http://www.grantjenks.com/docs/sortedcontainers/
# https://github.com/gitpython-developers/GitPython

import sys
from git import *
#from sortedcontainers import SortedList, SortedDict, SortedSet

class Files:
    
    def __init__(self):
        self.files = dict()
    
    def update(self, commit):
        stat = commit.stats
        commitFiles = stat.files
        #print commitFiles
        #print '\n'
        for fileName, stats in commitFiles.items():
            if fileName not in self.files:
                self.addNew(fileName, stats, len(commitFiles) - 1)
            else:
                self.updateFile(fileName, stats, len(commitFiles) - 1)
    
    def addNew(self, fileName, stats, chgSetSize):
        entry = {
            'size' : -1,
            'LOC_touched' : stats['lines'],
            'NR' : 1,
            'Nfix' : -1,
            'NAuth' : None,
            'LOC_added' : stats['insertions'],
            'MAX_LOC_added' : stats['insertions'],
            'AVG_LOC_added' : stats['insertions'],
            'Churn' : stats['insertions'] - stats['deletions'],
            'MAX_Churn' : stats['insertions'] - stats['deletions'],
            'AVG_Churn' : stats['insertions'] - stats['deletions'],
            'ChgSetSize' : chgSetSize,
            'MAX_ChgSet' : chgSetSize,
            'AVG_ChgSet' : chgSetSize,
            'Age' : -1,
            'WeightedAge' : -1
        }
        self.files.update({fileName : entry})
    
    def updateFile(self, fileName, stats, chgSetSize):
        entry = self.files[fileName]
        entry['NR'] += 1
        entry['LOC_touched'] += stats['lines']
        self.update_loc_added(entry, stats)
        self.update_churn(entry, stats)
        self.update_chgSetSize(entry, stats, chgSetSize)
    
    def update_loc_added(self, entry, stats):
        entry['LOC_added'] += stats['insertions']
        if (stats['insertions'] > entry['MAX_LOC_added']):
            entry['MAX_LOC_added'] = stats['insertions']
        entry['AVG_LOC_added'] = float(entry['LOC_added']) / entry['NR']
    
    def update_churn(self, entry, stats):
        entry['Churn'] += (stats['insertions'] - stats['deletions'])
        if (entry['Churn'] > entry['MAX_Churn']):
            entry['MAX_Churn'] = entry['Churn']
        entry['AVG_Churn'] = float(entry['Churn']) / entry['NR']
    
    def update_chgSetSize(self, entry, stats, chgSetSize):
        entry['ChgSetSize'] += chgSetSize
        if (chgSetSize > entry['MAX_ChgSet']):
            entry['MAX_ChgSet'] = chgSetSize
        entry['AVG_ChgSet'] = float(entry['ChgSetSize']) / entry['NR']
        