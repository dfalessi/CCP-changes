#from git import Repo
#from git import SymbolicReference as sr
#from git.test.lib import TestBase
#from git.test.lib.helper import with_rw_directory
from git import *
#import os
#import os.path as osp

#join = osp.join

# rorepo is a Repo instance pointing to the git-python repository.
# For all you know, the first argument to Repo is a path to the repository
# you want to work with
repoPath = ".."
repo = Repo(repoPath)
assert not repo.bare
print repo.working_dir
#sR = sr(repo, "")
#print sR.log()

#head = repo.head            # the head points to the active branch/ref
#master = head.reference     # retrieve the reference the head points to
#master.commit               # from here you use it as any other reference

#log = master.log()
#print log[0]                      # first (i.e. oldest) reflog entry
#print log[0]                     # last (i.e. most recent) reflog entry
'''for entry in log:
    print entry'''

#c = Commit('master')
'''
c = repo.commit('origin/master')
s = c.stats
print s.total # full-stat-dict
print s.files # dict( filepath : stat-dict )
'''

commits = list(repo.iter_commits('master'))
for i in range (len(commits)):
    print ("commit #%d" % (i))
    c = commits[i]
    s = c.stats
    print s.files
    print "\n"
#print len(commits)

#commits = list(repo.iter_commits('master'))
#commits = repo.commit('master')
#print commits
