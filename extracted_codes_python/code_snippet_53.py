#!/usr/bin/env python
from i import I
import argparse
from i import VERSION

__version__ = VERSION

i = I(file="/Users/llamicron/.i")

parser = argparse.ArgumentParser(description="Connect to servers")
parser.add_argument(
    "command",
    action="store",
    choices=["list", "connect", "add", "remove"],
    type=str,
    help="Command to run. Options are ['list', 'connect', 'add', 'remove']",
    metavar="command"
)
parser.add_argument(
    "-f",
    help="Find a server",
    dest="find",
    metavar="find"
)
parser.add_argument(
    "-n",
    help="Name of a server, eg. 'i connect -n [server_name]'",
    dest="server_name",
    metavar="server name"
)
parser.add_argument('-v', '--version', action='version',
                    version="%(prog)s (" + __version__ + ")")
args = parser.parse_args()

if args.command == "list":
    if args.find:
        print(i.find(args.find).table)
    else:
        print(i.server_table().table)

if args.command == "connect":
    if args.server_name:
        server_name = args.server_name
    else:
        server_name = raw_input("Server name: ")
    i.connect(server_name)

if args.command == "add":
    server = i.ask_for_server_info()
    i.add(server)
    print("Added")

if args.command == "remove":
    if args.server_name:
        server_name = args.server_name
    else:
        server_name = raw_input("Server name: ")

    i.remove(server_name)
    print("Removed")
