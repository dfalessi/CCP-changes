import git
import config
import os

gitNames = config.PROJECT_NAMES
apache_git = "git@github.com:apache/{}.git"
for i in range(0, len(gitNames)):
   repoDir = config.CSL_LOCAL_REPO + gitNames[i]
   if not os.path.isdir(repoDir) and not os.path.exists(repoDir):
      git.Git().clone(apache_git.format(gitNames[i]), repoDir)
   git.cmd.Git(repoDir).pull()
