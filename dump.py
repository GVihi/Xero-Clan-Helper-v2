import requests
from bs4 import BeautifulSoup
import json
import credentials

r = requests.get("https://xero.gg/api/self/social/clan", headers={"x-api-access-key-id" : credentials.key, "x-api-secret-access-key": credentials.secret})
doc = BeautifulSoup(r.text, "html.parser")

#print(doc)

doc = str(doc)

data = json.loads(doc)

#Dump JSON object into file, for easier condition programming (eg. if online == true)
with open("json_dumps/myclan.json", 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

data = json.dumps(data, indent=4)
data = json.loads(data)

print(data)
#print(data['clan']['members'][0]['name'])

#for x in data['clan']['members']:
#    print(x['name'])

#names = ""
#for x in data['clan']['members']:
#    names+= x['name'] + "\n"


#print(names)
#print(f"Number of members: {len(data['clan']['members'])}")