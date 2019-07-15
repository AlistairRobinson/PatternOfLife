from fcmlib import FCM
import json

print("Initialising FCM")
map=FCM(I_EMPLOYMENT=1, I_EDUCATION=-1, I_COMMERCIAL=-1, I_VOLUNTEERING=-1, I_RESIDENTIAL=-1, I_SPORTS=-1, I_CULTURAL=-1, I_TRAVEL=-1, 
        O_EMPLOYMENT=0, O_EDUCATION=0, O_COMMERCIAL=0, O_VOLUNTEERING=0, O_RESIDENTIAL=0, O_SPORTS=0, O_CULTURAL=0, O_TRAVEL=0)

i_concepts = ["I_EMPLOYMENT", "I_EDUCATION", "I_COMMERCIAL", "I_VOLUNTEERING", "I_RESIDENTIAL", "I_SPORTS", "I_CULTURAL", "I_TRAVEL"]
o_concepts = ["O_EMPLOYMENT", "O_EDUCATION", "O_COMMERCIAL", "O_VOLUNTEERING", "O_RESIDENTIAL", "O_SPORTS", "O_CULTURAL", "O_TRAVEL"]

for i in i_concepts:
    for o in o_concepts:
        map.connect(i, o)
        map[o].relation.set(i, 1)

data = json.loads(open('weights.json').read())['w']

for i in data:
    for k1 in i.keys():
        for j in i[k1]:
            for k2 in j.keys():
                if j[k2]['wp'] == 0:
                    map[k2].relation.set(k1, j[k2]['p'])
                else:
                    map[k2].relation.set(k1, j[k2]['wp'])

print(map)

print("Processing FCM:")

for i in range(1, 60):
    map.update()
    map.save("./maps/example.json")
    map=FCM("./maps/example.json")

print(map)