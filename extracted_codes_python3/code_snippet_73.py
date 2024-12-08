#!/usr/bin/env python3

import os
import sys
from typing import List


Filename = str
MTime = float
SLEEP_TIME_SECS = 0.2


if not os.path.isfile("~/.oo"):
    os.system(f"cp {sys.path[0]}/default_black_list ~/.oo")


with open(f"{os.environ['HOME']}/.oo") as oo_config:
    BLACK_LIST = tuple(
        pat
        for pat in map(str.strip, oo_config)
        if not pat.startswith("#") and not pat.isspace()
    )


def blacklisted(path: str) -> bool:
    import fnmatch

    basename = os.path.basename(path)
    return any(
        fnmatch.fnmatch(basename, pat)
        for pat in map(str.strip, BLACK_LIST)
        if not pat.isspace()
    )


def get_all_relative_paths(root: str) -> List[Filename]:
    all_paths = [root + "/" + path for path in os.listdir(root)]

    valid_paths = [path for path in all_paths if not blacklisted(path)]

    for path in all_paths:
        if os.path.isdir(path) and not blacklisted(path):
            sub_files = get_all_relative_paths(root=path)
            valid_paths.extend(sub_files)

    return [p for p in valid_paths if os.path.isfile(p)]


def oo(cmd: str, root=".") -> None:
    import time

    old_mtimes = None

    while True:
        new_mtimes = {p: os.path.getmtime(p) for p in get_all_relative_paths(root)}

        if old_mtimes != new_mtimes:
            os.system("clear")
            os.system(cmd)
            old_mtimes = new_mtimes

        time.sleep(SLEEP_TIME_SECS)


def main():
    import argparse
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dir", default=".")
    parser.add_argument("cmd", nargs="*")
    args = parser.parse_args()
    cmd = " ".join(args.cmd)
    if not cmd.strip():
        parser.print_help()
        sys.exit()
    oo(cmd=cmd, root=args.dir)


if __name__ == "__main__":
    main()
