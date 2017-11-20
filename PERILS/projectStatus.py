import json
from collections import OrderedDict

APACHE_PROJECT_JSON = "./Dataset/apache-project.json"
PROJECT_STATUS_JSON = "./Dataset/project-status.json"

"""
This script contains functions to manipulate project-status.json.
Four possible statuses:
1. NoGit - the project can't be analyzed due to missing Git.
2. NoJIRA - the project can't be analyzed due to missing JIRA.
3. True - the project has been analyzed.
4. False - the project hasn't been analyzed.
"""

"""
dump a JSON with all projects' names according to project-names.json. All 
projects' values are initialized to False.
"""
def dump():
    data = json.load(open(APACHE_PROJECT_JSON,
                          encoding="utf8"), object_pairs_hook=OrderedDict)
    d = {d: False for d in data}
    with open(PROJECT_STATUS_JSON, 'w') as f:
        json.dump(d, f, indent=4, sort_keys=True)
        f.close()

"""
It returns the number of projects that have been analyzed.
"""
def countNumFalse():
    i = 0
    total = 0
    with open(PROJECT_STATUS_JSON, 'r+') as outfile:
       prjData = json.load(outfile)
       for key, val in prjData.items():
         if val == False:
           i += 1
         total += 1
    return (i, total)

"""
Update the status of the passed projectName.
"""
def updateProjectStatus(projectName, status):
    projectData = None
    with open(PROJECT_STATUS_JSON, 'r+') as outfile:
        projectData = json.load(outfile)
        outfile.seek(0)
        outfile.truncate()
        projectData[projectName] = status
        json.dump(projectData, outfile, indent=4, sort_keys=True)
        outfile.close()

if __name__ == "__main__":
    print(countNumFalse())
