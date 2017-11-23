# PERILS

### Abstract
Github and JIRA have become the most important sources for software engineering researches. However, there are potential perils of mining data from them. We defined a set of perils in order to help people measure the validity of the data.

### Get Started
The project requires one for a local branch for each Apache project's Git repo. Please customizes it in config.py before use.

### Technologies Used
1. GitPython API - https://github.com/gitpython-developers/GitPython
The scripts use local repositories. Cloning is done automatically through cloneAndPull in GitOperations.py. 
Please make sure local branches exist in case of errors.
2. Github API - https://developer.github.com/v3/
The scripts use HTTP calls with authorization header in requestByGitAPIWithAuth in GitOperations.py.
3. JIRA API - https://developer.atlassian.com/jiradev/jira-apis/jira-rest-apis
The scripts execute JQL. All the JQLs are in JiraQuery.py.
4. git-when-merged - https://github.com/mhagger/git-when-merged
It's for PERIL-27
