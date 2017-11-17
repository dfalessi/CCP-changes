import json
from collections import OrderedDict


def dump():
    data = json.load(open("./Dataset/apache-project.json",
                          encoding="utf8"), object_pairs_hook=OrderedDict)
    d = {d: False for d in data}
    with open("./Dataset/project-names.json", 'w') as f:
        json.dump(d, f, indent=4, sort_keys=True)
        f.close()


def updateProjectStatus(projectName):
    projectData = None
    with open("./Dataset/project-status.json", 'r+') as outfile:
        projectData = json.load(outfile)
        outfile.seek(0)
        outfile.truncate()
        projectData["activemq"] = projectData["allura"] = projectData["ant-antuit"] = "NoJIRA"
        projectData["ant-compress"] = projectData["ant-dotent"] = projectData["ant"] = "NoJIRA"
        projectData["ace"] = "NoGit"
        json.dump(projectData, outfile, indent=4, sort_keys=True)
        outfile.close()


updateProjectStatus("")
