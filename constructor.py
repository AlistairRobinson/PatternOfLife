"""
Pattern of Life Analyser for SSID Historic Data
Developed by Alistair Robinson, July 2019
FCM library developed by M Puheim, used under open license
"""

# pylint: disable=function-redefined
# pylint: disable=invalid-name

import json
import sys
from pcapfile import savefile
from fcmlib import FCM

# Executed as: python3 constructor.py -s maps/university.json -l 208 -t 2

def main():

    devices = {}
    ssids = {}
    threshold = 0
    limit = 418
    verbose = False
    save_file = ""

    for arg in sys.argv:
        if arg == "-v":
            # Execute in verbose mode
            verbose = True
        if arg == "-l":
            # Specify number of files loaded
            limit = int(sys.argv[int(sys.argv.index("-l") + 1)])
        if arg == "-s":
            # Specify file to save FCM as"
            save_file = sys.argv[int(sys.argv.index("-s") + 1)]
        if arg == "-t":
            # Specify threshold at which to remove SSIDs and devices
            threshold = int(sys.argv[int(sys.argv.index("-t") + 1)])

    if verbose:
        print("\nLoading {} files...".format(limit))

    for i in range(0, limit):

        if verbose:
            print("\r\tLoading file {}... | {}%".format(i, int(i*100/limit)), end="")

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

            if devices.get(src) is None:
                devices[src] = {ssid}
            else:
                devices.get(src).add(ssid)

    if verbose:
        print("\r\tSuccessfully loaded {} files\t\n".format(limit))
        print("Populating SSID datastructures...")

    for device in list(devices.keys()):

        if len(devices.get(device)) < threshold:
            # Remove devices with only a single SSID
            del devices[device]

        for ssid in devices.get(device, []):
            if ssids.get(ssid) is None:
                ssids[ssid] = {device}
            else:
                ssids.get(ssid).add(device)

    for ssid in list(ssids.keys()):
        if len(ssids[ssid]) < threshold:
            # Remove SSIDs with only one saved device
            del ssids[ssid]

    if verbose:
        print("Sorting SSID datastructures...")

    sorted_ssids = sorted(ssids, key=lambda k: len(ssids[k]), reverse=True)

    if verbose:
        print("\nProcessing SSID weights...")

    weights = {}

    for ssid_a in sorted_ssids:
        if verbose:
            print("\r\tProcessing {}... | {}%".format(ssid_a,
                int(sorted_ssids.index(ssid_a)*100/len(sorted_ssids))), end="")
        weight_sum = 0
        weights[ssid_a] = {}
        for device in ssids[ssid_a]:
            for ssid_b in devices[device]:
                if ssid_a != ssid_b:
                    if ssid_b in weights[ssid_a].keys():
                        weights[ssid_a][ssid_b] += 1
                    else:
                        weights[ssid_a][ssid_b] = 1
                    weight_sum += 1
        for ssid_b in weights[ssid_a].keys():
            weights[ssid_a][ssid_b] /= weight_sum
        weights[ssid_a][ssid_a] = 1

    if verbose:
        print("\r\tSuccessfully processed SSID weights\t\n")
        print("Populating FCM...")

    map = FCM()

    for ssid in sorted_ssids:
        if verbose:
            print("\r\tAdding {}... | {}%".format(ssid,
                int(sorted_ssids.index(ssid)*100/len(sorted_ssids))), end="")
        map.add("I_" + ssid)
        map.add("O_" + ssid)

    if verbose:
        print("\r\tSuccessfully populated FCM\t\n")
        print("Connecting FCM...")

    for ssid_a in sorted_ssids:
        print("\r\tConnecting {}... | {}%".format(ssid_a,
            int(sorted_ssids.index(ssid_a)*100/len(sorted_ssids))), end="")
        for ssid_b in weights[ssid_a].keys():
            weight = weights[ssid_a][ssid_b]
            if weight > 0:
                map.connect("I_" + ssid_a, "O_" + ssid_b)
                map["O_" + ssid_b].relation.set("I_" + ssid_a, weight)

    if verbose:
        print("\r\tSuccessfully connected FCM\t\n")

    if save_file != "":
        if verbose:
            print("Saving FCM...")
        map.save(save_file)
        if verbose:
            print("Successfully saved FCM\n")

    print("Program exiting...")

    return 0

if __name__ == "__main__":
    main()