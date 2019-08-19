"""
Pattern of Life Analyser for SSID Historic Data
Developed by Alistair Robinson, July 2019
FCM library developed by M Puheim, used under open license
"""

# pylint: disable=function-redefined
# pylint: disable=invalid-name

import sys
import random
from pcapfile import savefile
from fcmlib import FCM

# Executed as: python3 authenticator.py -m maps/university.json -l 208 -s 500

def main():

    devices_old = {}
    devices_new = {}
    maps_old = {}
    ssids = set()
    dataset = []
    limit = 418
    size = 10
    verbose = False
    map_file = "maps/new.json"
    iterations = 60
    alpha = 6

    for arg in sys.argv:
        if arg == "-v":
            # Execute in verbose mode
            verbose = True
        if arg == "-l":
            # Specify number of files loaded
            limit = int(sys.argv[int(sys.argv.index("-l") + 1)])
        if arg == "-s":
            # Set maximum result set size
            size = int(sys.argv[int(sys.argv.index("-s") + 1)])
        if arg == "-a":
            # Set anomaly threshold alpha
            alpha = int(sys.argv[int(sys.argv.index("-a") + 1)])
        if arg == "-m":
            # Specify FCM template
            map_file = sys.argv[int(sys.argv.index("-m") + 1)]


    if verbose:
        print("\nLoading {} files...".format(limit * 2))

    # Load old dataset

    for i in range(0, limit):

        if verbose:
            print("\r\tLoading file {}...".format(i), end="")

        pcap = savefile.load_savefile(open('./data/probes-2013-03-28.pcap{}'.format(i), 'rb'))

        for packet in pcap.packets:

            # Source address
            # [56:68] University
            # [72:84] TheMall
            # [70:82] Vatican
            src = packet.raw().hex()[56:68]

            # Tag length
            # [86:88] University
            # [102:104] TheMall
            # [100:102] Vatican
            tag_length = packet.raw().hex()[86:88]

            if tag_length == "00":
                continue

            # SSID
            # [88:110] University
            # [104:126] TheMall
            # [102:124] Vatican
            ssid = bytes.fromhex(packet.raw().hex()[88:110]).decode('utf-8')
            ssids.add(ssid)

            if devices_old.get(src) is None:
                devices_old[src] = {ssid}
            else:
                devices_old.get(src).add(ssid)

    # Load new dataset

    for i in range(418 - limit, 418):

        if verbose:
            print("\r\tLoading file {}...".format(i), end="")

        pcap = savefile.load_savefile(open('./data/probes-2013-03-28.pcap{}'.format(i), 'rb'))

        for packet in pcap.packets:

            # Source address
            # [56:68] University
            # [72:84] TheMall
            # [70:82] Vatican
            src = packet.raw().hex()[56:68]

            # Tag length
            # [86:88] University
            # [102:104] TheMall
            # [100:102] Vatican
            tag_length = packet.raw().hex()[86:88]

            if tag_length == "00":
                continue

            # SSID
            # [88:110] University
            # [104:126] TheMall
            # [102:124] Vatican
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
            if len(devices_old[device]) >= alpha and len(devices_new[device]) >= alpha:
                # Only allow devices which appear in both datasets entry into the result set
                # And remove anomalous devices with less than 'alpha' saved SSIDs in either dataset
                dataset.append(device)

    for device in dataset:
        if verbose:
            print("\r\tConstructing device {}... ".format(device), end="")
        map = FCM(map_template)
        for ssid in devices_old[device]:
            map["I_{}".format(ssid)] = 1
            try:
                # Special case - new SSID with no a priori knowledge
                # In the case that the map doesn't have an output concept ready
                # Create one and add a relation FOR THIS DEVICE ONLY
                map["O_{}".format(ssid)]
            except:
                map["O_{}".format(ssid)] = 0
                map.connect("I_{}".format(ssid), "O_{}".format(ssid))
                map["O_{}".format(ssid)].relation.set("I_{}".format(ssid), 1)
        for i in range(iterations):
            map.update()
        maps_old[device] = map

    if verbose:
        print("\r\tSuccessfully constructed FCMs\n")

    for device in dataset:
        print(",{}".format(device), end="")

    for device_y in maps_old:
        print("\n{}".format(device_y), end="")
        for device_x in dataset:
            map_old = maps_old[device_y]
            trust = 0
            for ssid in ssids:
                i_concept = "I_{}".format(ssid)
                o_concept = "O_{}".format(ssid)
                if ssid in devices_new[device_x]:
                    try:
                        trust += map_old[o_concept].value + map_old[i_concept].value
                    except:
                        trust += 0
                else:
                    try:
                        trust += 1 - map_old[o_concept].value - map_old[i_concept].value
                    except:
                        trust += 1
            trust /= len(ssids)
            # Intersect can also computed as a debugging tool, use formatter.py to extract useful data from output
            intersect = len(devices_old[device_y].intersection(devices_new[device_x]))
            intersect /= (len(devices_old[device_y]) + len(devices_new[device_x]))/2
            # print(",{}/{}".format(trust, intersect), end="")
            print(",{}".format(trust), end="")

    if verbose:
        print("\nAuthentication complete\n")
        print("Program exiting...")

    return 0

if __name__ == "__main__":
    main()