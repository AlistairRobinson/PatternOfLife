"""
Pattern of Life Analyser for SSID Historic Data
Developed by Alistair Robinson, July 2019
FCM library developed by M Puheim, used under open license
"""

# pylint: disable=function-redefined
# pylint: disable=invalid-name

import sys

def main():

    target_file = ""
    index = 0
    pivot = False

    for arg in sys.argv:
        if arg == "-f":
            target_file = sys.argv[int(sys.argv.index("-f") + 1)]
        if arg == "-i":
            index = int(sys.argv[int(sys.argv.index("-i") + 1)])
        if arg == "-p":
            pivot = True

    with open(target_file, 'r') as f:
        file_data = f.read()
        f.close()

    if pivot:
        print("device,trust")
        i = 1
        for line in file_data.split('\n')[1:]:
            if line != "":
                print(line.split(',')[0], end=",")
                try:
                    print(line.split(',')[i].split('/')[index])
                except:
                    print(line.split(',')[i].split('/')[0])
                i += 1

    else:

        for line in file_data.split('\n'):
            for value in line.split(','):
                try:
                    print(value.split('/')[index], end = ",")
                except:
                    print(value.split('/')[0], end = ",")
            print()

if __name__ == "__main__":
    main()