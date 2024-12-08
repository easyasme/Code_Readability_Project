#!/usr/bin/env python3

import os
import json
import tarfile
import urllib.request
from platform import machine, system
from subprocess import run
import argparse

os_family = system().lower()

usage = """
Usage: qe [images] (script options) (other qemu params)

Wrapper for qemu to simplify VM launching from command line
It provides automatic image type detection, enables UEFI and acceleration if possible and provides some additional niceties, see below

Script options:

-p             forward ssh and http ports
-i --make-iso  makes and mounts ISO from folder of file
-l --no-efi    run without UEFI (default tries to find OVMF.fd)
-s --snapshot  run VM in without saving any changes
-n             generate command and print without running

-u             select USB device (not implemented yet, TODO)
-f             FAT folder, read only (not implemented yet, TODO)

--help         display help message

You can also use all available qemu-system-x86_64 parameters
"""

formats = {
    "iso": "raw",
    "qcow": "qcow",
    "qcow2": "qcow2",
    "qed": "qed",
    "raw ": "raw ",
    "img": "raw",
    "vdi": "vdi",
    "vhd": "vpc",
    "vhdx": "vhdx",
    "vmdk": "vmdk",
    "ova": "vmdk",
    "vdi.vtoy": "vdi",
    "vhd.vtoy": "vpc",
}
config_folder = os.path.expanduser("~/.config/qe")
gl_defaults = {
    "memory": "3G",
    "cpu_cores": "2",
    "image_size_to_create": "40G",
    "ports_passthrough": {
        22: 9922,  # ssh
        80: 9980,  # http
        443: 9943,  # https
        21: 9921,  # ftp
        3389: 9989,  # rdp
    },
}
script_options_to_exclude_from_qemu_args = ["-u", "-f", "-n"]
# for UEFI and accelerator
os_families = {
    "linux": {
        "accel": ["-enable-kvm"],
        "bios_paths": [
            "/usr/share/ovmf/OVMF.fd",
            "/usr/share/ovmf/x64/OVMF.fd",
            "/usr/share/edk2/ovmf/OVMF_CODE.fd",
            "./OVMF.fd",
        ],
    },
    "windows": {"accel": ["--accel", "whpx"], "bios_paths": ["./OVMF.fd"]},
    "darwin": None,
}


def is_image(s: str) -> bool:
    return bool(sum((s.endswith(e) or s.startswith("/dev/")) for e in formats.keys()))


def invert_bools(func):
    def wrapper(*args, **kwargs):
        return not func(*args, **kwargs)

    return wrapper


is_not_image = invert_bools(is_image)


def set_defaults(defaults: dict) -> dict:
    # setting defaults
    config_path = config_folder + "/config.json"
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            defaults = json.load(f)
        # TODO - check if all fields set
    else:
        if not os.path.exists(config_folder):
            os.mkdir(config_folder)
        with open(config_path, "w") as f:
            f.write(json.dumps(defaults, indent=2))

    return defaults


def parse_args() -> tuple:
    # parsing arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--make-iso",
        type=str,
        help="Makes and mounts ISO from folder of file",
    )
    parser.add_argument(
        "--smb",
        type=str,
        help="Mounts folder as SMB drive (\\10.0.2.4\qemu)",
    )
    parser.add_argument(
        "-p",
        "--ports-passthrough",
        action="store_true",
        help="Enables port forwarding for ssh and http",
    )
    parser.add_argument(
        "-l",
        "--no-efi",
        "--legacy",
        action="store_true",
        help="Boot in legacy mode",
    )
    parser.add_argument(
        "-s",
        "--snapshot",
        action="store_true",
        help="Run VM in without saving any changes",
    )
    argparsed, not_argparsed = parser.parse_known_args()
    not_argparsed = [parser.prog] + not_argparsed

    return argparsed, not_argparsed


def get_mem_cpu(args: list, defaults: dict) -> tuple:
    # setting CPU count and memory amount
    if "-m" not in args:
        mem_amount = ["-m", defaults["memory"]]
    else:
        mem_amount = []
    if "-smp" not in args:
        cpu_count = ["-smp", defaults["cpu_cores"]]
    else:
        cpu_count = []
    return mem_amount, cpu_count


def mount_smb(folder: str) -> list:
    """
    Usage: smb = mount_smb(argparsed.smb)

    -nic user,id=nic0,smb=/path/to/share/directory
    """
    raise NotImplemented


def make_iso(to_pack, args: list) -> list:
    if to_pack:
        to_mount = to_pack + ".iso"
        if not os.path.exists(to_mount):
            # depends on genisoimage package, make sure to install it first
            run(
                [
                    "mkisofs",
                    "-r",
                    # "-output-charset",
                    # "utf-8",
                    "-jcharset",
                    "utf8",
                    "-o",
                    to_mount,
                    to_pack,
                    # "-V",
                    # to_pack,
                ]
            )
        args += [to_mount]
    return args


def add_ports(do: bool, defaults: dict) -> list:
    # ports passthrough
    if do:
        port_string = ",".join(
            [
                f"hostfwd=tcp:127.0.0.1:{dest}-0.0.0.0:{source}"
                for source, dest in defaults["ports_passthrough"].items()
            ]
        )
        port_fwd = ["-nic", port_string]
    else:
        port_fwd = []
    return port_fwd


def identify_image_types(disk_images: list, defaults: dict) -> tuple:
    sudo = []
    drive = []
    display = []
    for i, image in enumerate(disk_images):
        if (
            "w11" in image.lower()
            or "windows" in image.lower()
            # and "server" not in image.lower()
        ):
            display = ["-display", "sdl"]
        if image.startswith("/dev/"):
            sudo = ["sudo"]
        if image.endswith(".ova"):
            folder = ".".join(image.split(".")[:-1])
            with tarfile.TarFile(image, "r") as tf:
                tf.extractall(folder)
            os.rename(
                [f for f in os.listdir(folder) if f.endswith(".vmdk")][0],
                folder + ".vmdk",
            )
            os.unlink(folder)
        media = "cdrom" if image.endswith(".iso") else "disk"
        format = [e for k, e in formats.items() if image.endswith(k)][0]
        # creating image if not present
        if not os.path.exists(image):
            if image.endswith("vhd.vtoy"):
                subformat = ["-o", "subformat=fixed"]
            elif image.endswith("vdi.vtoy"):
                subformat = ["-o", "static=on"]
            else:
                subformat = []
            run(
                ["qemu-img", "create", "-f", format]
                + subformat
                + [image, defaults["image_size_to_create"]]
            )
        # image = os.path.abspath(image)
        drive += ["-drive", f"file={image},format={format},index={i},media={media}"]
    return sudo, drive, display


def get_bios_and_acceleration(os_families: dict) -> tuple:
    default_bios = None
    os_family_info = os_families.get(os_family, default_bios)

    if not os_family_info:
        raise NotImplementedError

    accel = os_family_info["accel"]
    bios = next(
        (path for path in os_family_info["bios_paths"] if os.path.isfile(path)),
        default_bios,
    )
    if not bios:
        ovmf_link = "https://github.com/clearlinux/common/raw/master/OVMF.fd"
        file_path = os.path.join(config_folder, "OVMF.fd")
        if not os.path.exists(file_path):
            with urllib.request.urlopen(ovmf_link) as response, open(
                file_path, "wb"
            ) as out_file:
                data = response.read()
                out_file.write(data)
        bios = file_path

    return bios, accel


def get_vfat(args: list) -> list:
    # TODO - vfat folder
    # currently doesn't work reliably
    if "-f" in args:
        vfat_index = args.index("-f")
        if vfat_index < len(args) - 1:
            vfat_folder = os.path.abspath(args[vfat_index + 1])
            vfat_drive = [
                "-drive",
                f"file=fat:ro:{vfat_folder},index=9,format=raw,media=disk,if=virtio",
            ]
        else:
            print("Missing folder path for -f option.")
            exit()
    else:
        vfat_drive = []
    return vfat_drive


def main():
    defaults = set_defaults(gl_defaults)
    argparsed, not_argparsed = parse_args()
    not_argparsed = make_iso(argparsed.make_iso, not_argparsed)
    sudo, drive, display = identify_image_types(
        list(filter(is_image, not_argparsed[1:])), defaults
    )
    port_fwd = add_ports(argparsed.ports_passthrough, defaults)

    vfat_drive = get_vfat(not_argparsed)
    bios, accel = get_bios_and_acceleration(os_families)
    if argparsed.no_efi:
        bios = None
    mem_amount, cpu_count = get_mem_cpu(not_argparsed, defaults)
    other_args = list(filter(is_not_image, not_argparsed[1:]))
    qemu_args = [
        e for e in other_args if e not in script_options_to_exclude_from_qemu_args
    ]

    # I assume you are using image with the same architecture as host
    archs = {
        "x86_64": "x86_64",
        "arm64": "aarch64",
        "aarch64": "aarch64",
        "i386": "i386",
    }
    arch = archs[machine()]

    # final command to run
    command = [
        sudo,
        [f"qemu-system-{arch}"],
        accel,
        cpu_count,
        mem_amount,
        [] if bios is None else ["-bios", bios],
        qemu_args,
        drive,
        port_fwd,
        vfat_drive,
        display,
        ["-snapshot"] if argparsed.snapshot else [],
    ]

    command = [item for sublist in command for item in sublist]

    print(*command)
    if "-n" not in not_argparsed:
        run(command)


if __name__ == "__main__":
    main()
