#!/usr/bin/env python

# This file MUST NOT be named `ld`, otherwise Rust will try to outsmart us.

import shutil
import pprint
import sys
import os

spec = {
    # TODO: this crate should produce a relocatable, self-contained binary.
    "code": {
        "remove": [ ],
        "insert": [ ],
    },

    # This crate should produce a relocatable, self-contained binary
    # with a custom entry point. I **think** it is currently working.
    "shim": {
        "remove": [ "-Bdynamic" ],
        "insert": [ "-nostdlib" ],
    }
}

# Find the real compiler
cc = os.getenv('CC')
if cc is None:
    cc = shutil.which('cc')
assert(cc is not None)
argv = [cc] + sys.argv[1:]

crate = os.getenv("CARGO_PKG_NAME")
build = len([a for a in argv if "build_script_build" in a]) > 0

# Substitute flags
data = spec.get(crate, {})
if data and not build:
    for flag in data.get("remove", []):
        while flag in argv:
            argv.remove(flag)
    for flag in data.get("insert", []):
        argv.append(flag)

#with open("/dev/stderr", "w") as f:
#    pprint.pprint(os.getcwd(), f)
#    pprint.pprint(dict(os.environ), f)
#    pprint.pprint(argv, f)
#    pprint.pprint(build, f)

# Execute the real linker
#if crate == 'code':
#    sys.exit(1)
os.execvp(argv[0], argv)
