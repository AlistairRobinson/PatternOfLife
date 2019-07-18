"""
Pattern of Life Analyser for SSID Historic Data
Developed by Alistair Robinson, July 2019
FCM library developed by M Puheim, used under open license
"""

from fcmlib import FCM
import json
import sys

w = [0, 0, 0, 0, 0, 0, 0, 0]
r = [9, 9, 1, 3, 3, 3, 1, 1]

i_concepts = ["I_EMPLOYMENT", "I_EDUCATION", "I_COMMERCIAL", "I_VOLUNTEERING", "I_RESIDENTIAL", "I_SPORTS", "I_CULTURAL", "I_TRAVEL"]
o_concepts = ["O_EMPLOYMENT", "O_EDUCATION", "O_COMMERCIAL", "O_VOLUNTEERING", "O_RESIDENTIAL", "O_SPORTS", "O_CULTURAL", "O_TRAVEL"]

iterations = 60

def construct(l:list, weights:str="./weights.json") -> FCM:
    if len(l) < 8:
        return connect(FCM(
            I_EMPLOYMENT   = 0, 
            I_EDUCATION    = 0, 
            I_COMMERCIAL   = 0, 
            I_VOLUNTEERING = 0, 
            I_RESIDENTIAL  = 0, 
            I_SPORTS       = 0, 
            I_CULTURAL     = 0, 
            I_TRAVEL       = 0,
            O_EMPLOYMENT   = 0, 
            O_EDUCATION    = 0,
            O_COMMERCIAL   = 0,
            O_VOLUNTEERING = 0, 
            O_RESIDENTIAL  = 0,
            O_SPORTS       = 0,
            O_CULTURAL     = 0,
            O_TRAVEL       = 0
        ), weights)
    else:
        return connect(FCM(
            I_EMPLOYMENT   = l[0], 
            I_EDUCATION    = l[1], 
            I_COMMERCIAL   = l[2], 
            I_VOLUNTEERING = l[3], 
            I_RESIDENTIAL  = l[4], 
            I_SPORTS       = l[5], 
            I_CULTURAL     = l[6], 
            I_TRAVEL       = l[7],
            O_EMPLOYMENT   = 0, 
            O_EDUCATION    = 0,
            O_COMMERCIAL   = 0,
            O_VOLUNTEERING = 0, 
            O_RESIDENTIAL  = 0,
            O_SPORTS       = 0,
            O_CULTURAL     = 0,
            O_TRAVEL       = 0
        ), weights)

def construct(d:dict, weights:str="./weights.json") -> FCM:
    if set(d.keys()) != set(i_concepts):
        return connect(FCM(
            I_EMPLOYMENT   = 0, 
            I_EDUCATION    = 0, 
            I_COMMERCIAL   = 0, 
            I_VOLUNTEERING = 0, 
            I_RESIDENTIAL  = 0, 
            I_SPORTS       = 0, 
            I_CULTURAL     = 0, 
            I_TRAVEL       = 0,
            O_EMPLOYMENT   = 0, 
            O_EDUCATION    = 0,
            O_COMMERCIAL   = 0,
            O_VOLUNTEERING = 0, 
            O_RESIDENTIAL  = 0,
            O_SPORTS       = 0,
            O_CULTURAL     = 0,
            O_TRAVEL       = 0
        ), weights)
    else:
        s = 0
        for k in d.keys():
            s += d[k]

        return connect(FCM(
            I_EMPLOYMENT   = d['I_EMPLOYMENT']/s, 
            I_EDUCATION    = d['I_EDUCATION']/s, 
            I_COMMERCIAL   = d['I_COMMERCIAL']/s, 
            I_VOLUNTEERING = d['I_VOLUNTEERING']/s, 
            I_RESIDENTIAL  = d['I_RESIDENTIAL']/s, 
            I_SPORTS       = d['I_SPORTS']/s, 
            I_CULTURAL     = d['I_CULTURAL']/s, 
            I_TRAVEL       = d['I_TRAVEL']/s,
            O_EMPLOYMENT   = 0, 
            O_EDUCATION    = 0,
            O_COMMERCIAL   = 0,
            O_VOLUNTEERING = 0, 
            O_RESIDENTIAL  = 0,
            O_SPORTS       = 0,
            O_CULTURAL     = 0,
            O_TRAVEL       = 0
        ), weights)

def normalise(l:list) -> list:
    s = sum(l) + 1
    for i in range(0, len(l)):
        l[i] /= s
    return l

def trust(a:FCM, b:FCM) -> float:

    s = 0

    for i in i_concepts:
        s += abs(a[i].value - b[i].value)

    for o in o_concepts:
        s += abs(a[o].value - b[o].value)

    return (1 - s/16)

def connect(new:FCM, weights:str = "./weights.json") -> FCM:

    for i in i_concepts:
        for o in o_concepts:
            new.connect(i, o)
            new[o].relation.set(i, 1)

    data = json.loads(open(weights).read())['w']

    for i in data:
        for k1 in i.keys():
            for j in i[k1]:
                for k2 in j.keys():
                    if j[k2]['wp'] == 0:
                        new[k2].relation.set(k1, j[k2]['p'])
                    else:
                        new[k2].relation.set(k1, j[k2]['wp'])
    
    return new

def authenticate(new:FCM, trusted:FCM, file:str = "./maps/experiment.json", weights:str = "./weights.json", verbose:bool = False) -> float:
    
    for i in range(1, iterations):
        new.update()
        new.save(file)
        new = FCM(file)

    if verbose:
        print("Newly generated FCM: ")
        print(new)
        print("Trusted FCM: ")
        print(trusted)

    return trust(new, trusted)

def conformity(new:FCM, conformity:str="./maps/conformity.json"):

    return authenticate(inputs, FCM(conformity))

def save(new:FCM, file:str = "./maps/experiment.json", weights:str = "./weights.json", verbose:bool = False) -> bool:
    
    for i in range(1, iterations):
        new.update()
        new.save(file)
        new = FCM(file)

    if verbose:
        print(new)
        print("FCM saved to " + file + " successfully")

    return True 

def main():

    verbose = False

    def set_verbose():
        verbose = True

    opt = {
        "-v": set_verbose
    }

    if len(sys.argv) < 9:
        print("Insufficient arguments")
        exit(0)

    for i in range(0, 8):
        w[i] = int(sys.argv[i + 1]) * r[i]

    w = normalise(w)

    l = 9

    while l < len(sys.argv):
        opt[sys.argv[l]]()
        l += 1

    new = construct(w)

    if verbose:
        print("Initialised FCM:")
        print(new)
        print("Processing FCM for {} iterations:".format(iterations))

    for i in range(1, iterations):
        new.update()
        new.save("./maps/experiment.json")
        new = FCM("./maps/experiment.json")

    if verbose:
        print(new)

    trusted = FCM("./maps/trusted.json")

    print("Trust = {}".format(trust(new, trusted)))

if __name__ == "__main__":
    main()