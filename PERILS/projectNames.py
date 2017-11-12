import json
from collections import OrderedDict

def dump():
  data = json.load(open("./Dataset/apache-project.json", encoding="utf8"), object_pairs_hook=OrderedDict)
  d = {d : False for d in data}
  with open("./Dataset/project-names.json", 'w') as f:
    json.dump(d, f, indent=4, sort_keys=True)
    f.close()

