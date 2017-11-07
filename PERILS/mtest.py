from Git import GitOperations
import re

o = GitOperations.executeGitShellCommand("./CCP-REPOS/tika", ["git branch -a | grep \'remote\' | wc -l"])
if re.sub(r'\s+', '', o) == int(o):
  print (o)

if 0 == int("0"):
  print ("hi")
