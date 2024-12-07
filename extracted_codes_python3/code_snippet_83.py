#!/usr/bin/env python3
import sys
import os
import subprocess
import shutil
import pathlib

IS_WINDOWS = (sys.platform == "win32")
EXE_EXT = ".exe" if IS_WINDOWS else ""

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(SCRIPT_DIR, "out")
ZIG_OUT_DIR = os.path.join(SCRIPT_DIR, "zig-out")
UF2_REPO = os.path.join(SCRIPT_DIR, "dep", "uf2")
UF2_SAMDX1_REPO = os.path.join(SCRIPT_DIR, "dep", "uf2-samdx1")

def main():
    tc_path_config = os.path.join(SCRIPT_DIR, "toolchain_path")
    if not os.path.exists(tc_path_config):
        sys.exit(f"error: missing toolchain_path with the path to the arm-none-eabi toolchain")
    with open(tc_path_config, "r") as f:
        tc_path = f.read().strip()

    if not os.path.exists(tc_path):
        sys.exit(f"error: toolchain_path '{tc_path}' does not exist")

    TC_BIN = os.path.join(tc_path, "bin")
    OBJCOPY = os.path.join(TC_BIN, "arm-none-eabi-objcopy" + EXE_EXT)

    uf2conv = os.path.join(UF2_REPO, "utils", "uf2conv.py")

    run(["zig", "build"])

    if os.path.exists(OUT_DIR):
        for base in os.listdir(OUT_DIR):
            entry = os.path.join(OUT_DIR, base)
            if os.path.isdir(entry):
                shutil.rmtree(entry)
            else:
                os.remove(entry)
    else:
        os.mkdir(OUT_DIR)

    build_blink_zig(OBJCOPY, uf2conv)

def build_blink_zig(OBJCOPY, uf2conv):
    elf = os.path.join(ZIG_OUT_DIR, "bin", "blink")
    bin = os.path.join(OUT_DIR, "blink.bin")
    uf2 = os.path.join(OUT_DIR, "blink.uf2")

    blink_openocd = os.path.join(SCRIPT_DIR, "atsamd51", "blink-openocd")
    samd51 = os.path.join(blink_openocd, "samd51")

    #run([os.path.join(SCRIPT_DIR, "uf2", "zig-out", "bin", "elf2uf2"),
    run([OBJCOPY, "-O", "binary", elf, bin])
    #run([sys.executable, os.path.join(SCRIPT_DIR, "touf2"), bin, uf2])
    run([
        sys.executable,
        uf2conv,
        "--convert",
        "-o", uf2,
        "-b", "0x4000",
        "--family", "0x55114460",
        bin,
    ])
    # check the uf2 file
    run([
        os.path.join(SCRIPT_DIR, "zig-out", "bin", "readuf2" + EXE_EXT),
        uf2
    ])
    log(f"Success created {uf2}")

def log(msg):
    print("[buildstep.py] " + msg, file=sys.stderr)
    sys.stderr.flush()

def run(cmd):
    log("[RUN] {}".format(subprocess.list2cmdline(cmd)))
    subprocess.run(cmd, check=True)

main()
