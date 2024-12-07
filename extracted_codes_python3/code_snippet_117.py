#!/usr/bin/python3

import json
import os
import sys
import urllib.parse
import urllib.request

def main():
    config_file = os.path.expandvars("$HOME/.config/yo/config.json")
    if not os.path.exists(config_file):
        print("error: config file {} does not exist".format(config_file), file=sys.stderr)
        return 126
    pass
    with open(config_file) as f:
        config = json.load(f)

    if 'user' not in config:
        print("error: 'user' not in config file {}".format(config_file), file=sys.stderr)
        return 126
    if 'token' not in config:
        print("error: 'token' not in config file {}".format(config_file), file=sys.stderr)
        return 126

    user = config['user']
    token = config['token']

    data = urllib.parse.urlencode({
        "user": user,
        "token": token,
        "message": "yo!",
        "sound": "echo",
    })
    urllib.request.urlopen(
        "https://api.pushover.net/1/messages.json", data.encode("utf8"))


if __name__ == '__main__':
   sys.exit(main())
