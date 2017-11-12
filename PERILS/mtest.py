from Git import GitOperations
from Git.GitApache import GitApache
import re

o = GitOperations.executeGitShellCommand("./CCP-REPOS/tika", ["git branch -a | grep \'remote\' | wc -l"])
if re.sub(r'\s+', '', o) == int(o):
  print (o)

if 0 == int("0"):
  print ("hi")

git = GitApache("git@github.com:apache/tika.git", "./CCP-REPOS/tika", "")


g1 = git.getUniqueDevelopers("TIKA-2341")
g2 = git.getUniqueDevelopers("TIKA-2447")
g3 = git.getUniqueDevelopers("TIKA-2448")

print (g1 | g2 | g3)




