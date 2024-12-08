#!/usr/bin/env python3
"""
This script uses the xcrun binary with Xcode 11 to configure the status bar
in Xcode simulators. This is primarily useful for creating clean screenshots.
"""
import json
import subprocess
from sys import argv


def _help():
    print("StatusBar Help")
    print("\nUsage: sb [--clear] [-t \"9:41 AM\"]")
    print("\t-t\tSpecifies the time. Default is 9:41 AM.\n\t\tCan also use ISO 8601-1 \"1970-01-01T09:41:00-0500\".")
    print("\t--clear\tResets status bar.")
    print("\nRunning without any arguments will prompt to select a running simulator")
    print("and then configure its status bar.")
    exit(0)

def termy(cmd):
    task = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = task.communicate()
    return(out, err)

if '-h' in argv or '--help' in argv:
    _help()

sb_time = '9:41 AM'
if '-t' in argv:
    i = argv.index('-t')
    sb_time = argv[i+1]

# get a list of all simulators
simulators, err = termy(['xcrun', 'simctl', 'list', '--json'])
sim_json = json.loads(simulators)

booted_sims = []

# get a list of booted simulators
for device in sim_json['devices']:
    for i in sim_json['devices'][device]:
        if i['state'] == 'Booted':
            # print(i['state'])
            # print(i['name'])
            # print(i['udid'])
            booted_sims.append(i)

# check if there's at least one simulator booted
if len(booted_sims) == 0:
    print("No simulators booted, exiting...")
    exit(0)


print("Please select a simulator:")
# print out each Simulator and it's index number
for sim in booted_sims:
    index = booted_sims.index(sim)
    print("\t{0}: {1}".format(index, sim['name']))

# prompt the user to select a simulator
try:
    selected_sim = input("\nType a number or press control+c to exit > ")
except KeyboardInterrupt:
    exit()

# attempt to get the details of the simulator
# fails if they didn't type a valid index number
try:
    sim = booted_sims[int(selected_sim)]
    sim_udid = sim['udid']
    sim_name = sim['name']
except:
    print("\nInvalid selection, exiting...")
    exit(0)

# checks if the --clear flag was input and clears the simulator's status bar
if '--clear' in argv:
    termy([
        '/usr/bin/xcrun',
        'simctl', 'status_bar',
        sim_udid, 'clear'
    ])
    print("Reset status bar {0}".format(sim_name))
else:
    termy([
        '/usr/bin/xcrun',
        'simctl', 'status_bar',
        sim_udid, 'override',
        '--time', sb_time,
        '--dataNetwork', 'wifi',
        '--wifiMode', 'active',
        '--wifiBars', '3',
        '--cellularMode', 'active',
        '--cellularBars', '4',
        '--batteryState', 'charged',
        '--batteryLevel', '100'
    ])
    print("Set status bar for {0}".format(sim_name))
