#! /usr/bin/python3

import subprocess
import json
import os
import os.path
import shutil

limine_bin_url = "https://github.com/limine-bootloader/limine/archive/refs/heads/v8.x-binary.zip"

def main():
    # Build the kernel
    proc = subprocess.run(["cargo", "build"], check=True, cwd="./kernel")

    target_path = "target"
    rootfs_path = "target/rootfs"
    subprocess.run([ "mkdir", "-p", f"{rootfs_path}/boot" ], check=True)

    disk_image_path = "target/disk.img"
    disk_image_size = 20*1024*1024

    # Create the disk image file if it doesn't exist
    if not os.path.isfile(disk_image_path):
        with open(disk_image_path, "wb+") as file:
            file.write(bytearray(disk_image_size))
        partition_disk(disk_image_path)

    # Build and install limine bootloader
    build_limine(target_path, disk_image_path, rootfs_path)

    subprocess.run(
        f"cp -r skel/* {rootfs_path}",
        shell=True,
        check=True
    )
    
    copy_file("kernel/target/x86/debug/kernel", f"{rootfs_path}/boot/kernel32_dbg", True)
    copy_file("kernel/target/x86/release/kernel", f"{rootfs_path}/boot/kernel32")
    copy_file("kernel/target/x86_64/debug/kernel", f"{rootfs_path}/boot/kernel64_dbg")
    copy_file("kernel/target/x86_64/release/kernel", f"{rootfs_path}/boot/kernel64")

    subprocess.run(["tree", rootfs_path])

    # Format ext2 partition and copy files
    format_disk(disk_image_path, rootfs_path)

    subprocess.run([
        "qemu-system-i386", "-s",
        "-m", "256M",
        "-debugcon", "stdio",
        "-drive", f"format=raw,file={disk_image_path}"
    ])

def build_limine(target_path, disk_image_path, rootfs_path):
    version = "8.x"
    url = f"https://github.com/limine-bootloader/limine/archive/refs/heads/{version}-binary.zip"
    limine_path = target_path + f"/limine-{version}-binary"

    if not os.path.isdir(limine_path) or not os.path.isfile(f"{limine_path}/Makefile"):
        # subprocess.run([ "mkdir", "-p", limine_path ], check=True)

        print("Downloading Limine Bootloader")
        subprocess.run(
            [ "wget", "-q", url ],
            check=True,
            cwd=target_path
        )

        print("Extracting Limine Bootloader")
        subprocess.run(
            [ "unzip", f"{version}-binary.zip" ],
            check=True,
            cwd=target_path
        )
    
    assert os.path.isdir(limine_path) and os.path.isfile(f"{limine_path}/Makefile")

    subprocess.run(
        ["make"], check=True, cwd=limine_path
    )

    subprocess.run(
        [f"{limine_path}/limine", "bios-install", disk_image_path ],
        check=True,
    )

    copy_file(f"{limine_path}/limine-bios.sys", f"{rootfs_path}/boot/limine-bios.sys")

def check_command_available(possible_cmds):
    for cmd in possible_cmds:
        try:
            proc = subprocess.run([cmd, "-v"])
            return cmd
        except:
            pass
    return None

def copy_file(src, dest, must_exist=False):
    subprocess.run(["cp", src, dest], check=must_exist)

def partition_disk(disk_image_path):
    fdisk_path = check_command_available(["fdisk", "/sbin/fdisk"])
    if fdisk_path is None:
        print("Cannot find `fdisk`. Please install")
        exit(1)
    
    fmt_cmds = [
        "o", # clear the in memory partition table
        "n", # new partition
        "p", # primary partition
        "1", # partition number 1
        "",  # default - start at beginning of disk 
        "",  # default - use entire disk
        "a", # make the partition bootable
        "p", # print the in-memory partition table
        "w", # write the partition table
        "q"  # and we're done
    ]

    proc = subprocess.run(
        [fdisk_path, disk_image_path],
        input="\n".join(cmd for cmd in fmt_cmds) + "\n",
        encoding="ascii"
    )

    if proc.returncode != 0:
        print("Partitioning the disk image failed")
        exit(1)

def format_disk(disk_image_path, rootfs_dir):
    mkfs_path = check_command_available(["mkfs.ext2", "/sbin/mkfs.ext2"])
    if mkfs_path is None:
        print("Cannot find `mkfs.ext2`. Please install")
        exit(1)
    
    proc = subprocess.run([
        mkfs_path, disk_image_path,     # use our disk image
        "-E", f"offset={2048*512}",     # partition starts at sector 2048
        "-d", rootfs_dir,               # copy contents of this directory to the disk
        "-q"                            # quiet 
    ])
    if proc.returncode != 0:
        print("Formatting (ext2) the disk image failed")
        exit(1)

main()
