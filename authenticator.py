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

def main():

    devices_old = {}
    devices_new = {}
    ssids = {}
    threshold = 0
    limit = 418
    verbose = False
    map_file = "maps/new.json"

    for arg in sys.argv:
        if arg == "-v":
            verbose = True
        if arg == "-l":
            limit = int(sys.argv[int(sys.argv.index("-l") + 1)])
        if arg == "-m":
            map_file = sys.argv[int(sys.argv.index("-m") + 1)]


    if verbose:
        print("\nLoading {} files...".format(limit))

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

            if i < limit / 2:
                if devices_old.get(src) is None:
                    devices_old[src] = {ssid}
                else:
                    devices_old.get(src).add(ssid)
            else:
                if devices_new.get(src) is None:
                    devices_new[src] = {ssid}
                else:
                    devices_new.get(src).add(ssid)

    if verbose:
        print("\r\tSuccessfully loaded {} files\n".format(limit))
        print("Loading template FCM...")

    map_old_template = FCM(map_file)
    map_new_template = FCM(map_file)

    if verbose:
        print("\tSuccessfully loaded FCM {}\n".format(map_file))
        print("Authenticating devices...")

    for device in devices_old:
        if device not in devices_new:
            continue
        if verbose:
            print("\tAuthenticating device {}... ".format(device), end="")
        map_old = FCM(map_old_template.serialize())
        map_new = FCM(map_new_template.serialize())
        for ssid in devices_old[device]:
            map_old["I_{}".format(ssid)] = 1
        for ssid in devices_new[device]:
            map_new["I_{}".format(ssid)] = 1
        for i in range(60):
            map_old.update()
            map_new.update()
        trust = 0
        for concept in map_old.list().split(";"):
            trust += abs(map_old[concept].value - map_new[concept].value)
        print(1 - trust / len(map_old.list()))


    if verbose:
        print("\r\tAuthentication complete\n")
        print("Program exiting...")

    return 0

if __name__ == "__main__":
    main()