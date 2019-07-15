from fcmlib import FCM
import json
import sys

print("Initialising FCM")

if len(sys.argv) < 9:
    print("Insufficient arguments")
    exit(0)

w = [0, 0, 0, 0, 0, 0, 0, 0]
r = [9, 9, 1, 3, 3, 3, 1, 1]

for i in range(0, 8):
    w[i] = int(sys.argv[i + 1]) * r[i]

s = sum(w)

for i in range(0, 8):
    w[i] /= s

map=FCM(I_EMPLOYMENT=w[0], I_EDUCATION=w[1], I_COMMERCIAL=w[2], I_VOLUNTEERING=w[3], I_RESIDENTIAL=w[4], I_SPORTS=w[5], I_CULTURAL=w[6], I_TRAVEL=w[7], 
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
    map.save("./maps/experiment.json")
    map=FCM("./maps/experiment.json")

print(map)

trusted = FCM("./maps/trusted.json")
s = 0

for o in o_concepts:
    s += abs(trusted[o].value - map[o].value)

print("Trust = {}".format((1 - s/8)**2))