import requests
import json

a = requests.Session()
b = a.get('https://knowledgedb-api.elmorelab.com/database/getNpc?alias=c1&minlevel=1&maxLevel=99&type=Monster')
# print(b.json())
with open('monsters1.json', 'w') as f:
    json.dump(b.json(), f, indent=2, ensure_ascii=False)
lst = dict()
with open('monsters1.json', 'r') as f:
    r = json.load(f)
    for i in r:
        if i['value']['acquireSp'] != 0 and i['isLocationExist']:
            lst.update({i['name']['name']: {'level': i['value']['level']}})
print(lst)
with open('monsters.json', 'r') as f:
    r = json.load(f)
    for name in r:
        print(name)
