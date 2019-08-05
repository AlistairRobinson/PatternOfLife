"""
Pattern of Life Analyser for SSID Historic Data
Developed by Alistair Robinson, July 2019
FCM library developed by M Puheim, used under open license
"""

# pylint: disable=function-redefined
# pylint: disable=invalid-name

import json
import sys
import random
from pcapfile import savefile
from fcmlib import FCM
from math import sqrt

def main():

    devices_old = {}
    devices_new = {}
    maps_old = {}
    maps_new = {}
    ssids = set()
    dataset = []
    threshold = 0
    limit = 418
    size = 10
    verbose = False
    map_file = "maps/new.json"
    iterations = 60

    for arg in sys.argv:
        if arg == "-v":
            verbose = True
        if arg == "-l":
            limit = int(sys.argv[int(sys.argv.index("-l") + 1)])
        if arg == "-s":
            size = int(sys.argv[int(sys.argv.index("-s") + 1)])
        if arg == "-m":
            map_file = sys.argv[int(sys.argv.index("-m") + 1)]


    if verbose:
        print("\nLoading {} files...".format(limit * 2))

    for i in range(0, limit):

        if verbose:
            print("\r\tLoading file {}...".format(i), end="")

        pcap = savefile.load_savefile(open('./data/probes-2013-03-28.pcap{}'.format(i), 'rb'))

        for packet in pcap.packets:

            # Source address [56:68]
            src = packet.raw().hex()[56:68]

            # Tag length [86:88]
            tag_length = packet.raw().hex()[86:88]

            if tag_length == "00":
                continue

            # SSID [88:110]
            ssid = bytes.fromhex(packet.raw().hex()[88:110]).decode('utf-8')
            ssids.add(ssid)

            if devices_old.get(src) is None:
                devices_old[src] = {ssid}
            else:
                devices_old.get(src).add(ssid)

    for i in range(418 - limit, 418):

        if verbose:
            print("\r\tLoading file {}...".format(i), end="")

        pcap = savefile.load_savefile(open('./data/probes-2013-03-28.pcap{}'.format(i), 'rb'))

        for packet in pcap.packets:

            # Source address [56:68]
            src = packet.raw().hex()[56:68]

            # Tag length [86:88]
            tag_length = packet.raw().hex()[86:88]

            if tag_length == "00":
                continue

            # SSID [88:110]
            ssid = bytes.fromhex(packet.raw().hex()[88:110]).decode('utf-8')
            ssids.add(ssid)

            if devices_new.get(src) is None:
                devices_new[src] = {ssid}
            else:
                devices_new.get(src).add(ssid)

    if verbose:
        print("\r\tSuccessfully loaded {} files\n".format(limit * 2))
        print("Loading template FCM...")

    with open(map_file, 'r') as f:
        map_template = f.read()

    if verbose:
        print("\tSuccessfully loaded FCM {}\n".format(map_file))
        print("Constructing FCM for old devices...")

    for device in sorted(devices_old.keys(), key=lambda k: random.random()):
        if len(dataset) < size and device in devices_new:
            if len(devices_old[device]) > 5 and len(devices_new[device]) > 5:
                dataset.append(device)

    for device in dataset:
        if verbose:
            print("\r\tConstructing device {}... ".format(device), end="")
        map = FCM(map_template)
        for ssid in devices_old[device]:
            map["I_{}".format(ssid)] = 1
        for i in range(iterations):
            map.update()
        maps_old[device] = map

    if verbose:
        print("\r\tSuccessfully constructed FCMs\n")
        print("Constructing FCM for new devices...")
    """
    for device in dataset:
        if verbose:
            print("\r\tConstructing device {}... ".format(device), end="")
        map = FCM(map_template)
        for ssid in devices_new[device]:
            map["I_{}".format(ssid)] = 1
        for i in range(iterations):
            map.update()
        maps_new[device] = map
    """
    if verbose:
        print("\r\tSuccessfully constructed FCMs\n")

    for device in dataset:
        print(",{}".format(device), end="")

    for device_y in maps_old:
        print("\n{}".format(device_y), end="")
        for device_x in dataset:
            map_old = maps_old[device_y]
            #map_new = maps_new[device_x]
            list_old = map_old.list()
            #list_new = map_new.list()
            trust = 0
            for ssid in ssids:
                i_concept = "I_{}".format(ssid)
                o_concept = "O_{}".format(ssid)
                if ssid in devices_new[device_x]:
                    try:
                        trust += 1 - map_old[o_concept].value - map_old[i_concept].value
                    except:
                        trust += 1
                else:
                    try:
                        trust += map_old[o_concept].value + map_old[i_concept].value
                    except:
                        trust += 0
                """
                if o_concept in list_old and i_concept in list_new:
                    trust += abs(map_old[o_concept].value - map_new[i_concept].value)
                elif o_concept in list_old:
                    trust += abs(map_old[o_concept].value)
                elif i_concept in list_new:
                    trust += abs(map_new[i_concept].value)
                """
            trust = abs(((1 - trust / len(ssids)) - 0) / 1)
            intersect = len(devices_old[device_y].intersection(devices_new[device_x]))
            intersect /= (len(devices_old[device_y]) + len(devices_new[device_x]))/2
            #if intersect > 0.65 or intersect < 0.2:
            #    print(",{}/{}".format(intersect, intersect), end="")
            #else:
            #
            print(",{}/{}".format(trust, intersect), end="")

    if verbose:
        print("\nAuthentication complete\n")
        print("Program exiting...")

    return 0

if __name__ == "__main__":
    main()

"""
    for device in devices_old:
        if device not in devices_new:
            continue
        if verbose:
            print("\tAuthenticating device {}... ".format(device), end="")
        map_old = FCM(map_template)
        map_new = FCM(map_template)
        for ssid in devices_old[device]:
            map_old["I_{}".format(ssid)] = 1
        for ssid in devices_new[device]:
        #for ssid in devices_new[random.choice(list(devices_new))]:
            map_new["I_{}".format(ssid)] = 1
        for i in range(iterations):
            map_old.update()
            map_new.update()
        trust = 0
        for ssid in ssids:
            trust += abs(map_old["O_{}".format(ssid)].value - map_new["O_{}".format(ssid)].value)
        print(1 - 2 * trust / len(ssids))

"""