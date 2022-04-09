from fuzzywuzzy import process
from fuzzywuzzy import fuzz
import json
from typing import List
data = {}
def readJson(file_name) -> List[dict]:
    with open(file_name, "r") as f:
        data = json.load(f)
    return data

def writeJson(file_name, data):
    with open(file_name, "w") as f:
        json.dump(data, f)
for category in readJson('sm_categories.json'):
    data[category['name_en']] = category['id']
writeJson('sm_categories_id.json', data)
