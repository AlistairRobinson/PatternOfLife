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

devices = {}
ssids = {}
threshold = 0

for i in range(0, 418):

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

        if devices.get(src) is None:
            devices[src] = {ssid}
        else:
            devices.get(src).add(ssid)

for device in list(devices.keys()):

    if len(devices.get(device)) < threshold:
        del devices[device]

    for ssid in devices.get(device):
        if ssids.get(ssid) is None:
            ssids[ssid] = {device}
        else:
            ssids.get(ssid).add(device)

sorted_ssids = sorted(ssids, key=lambda k: len(ssids[k]), reverse=True)

#print(devices)
#print(len(devices))

print("Index, Name, Size")
index = 0

for ssid in sorted_ssids:
    print("{}, {}, {}".format(index, ssid, len(ssids.get(ssid))))
    index += 1