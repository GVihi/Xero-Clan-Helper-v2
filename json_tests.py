import json

with open("user_ids.json", "r") as f:
    data = json.load(f)

data = json.dumps(data, indent=4)
data = json.loads(data)

rm_id = 305035767170990081

new_data = {
    "ids": [

    ]
}

for x in data['ids']:
    if x['id'] != rm_id:
        entry = {
            "id": x['id']
        }

        new_data["ids"].append(entry)

with open("user_ids.json", "w") as f:
    json.dump(new_data, f, indent=4)