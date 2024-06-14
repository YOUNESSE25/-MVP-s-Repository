#!/usr/bin/python3
import os
import sys
import unshare
import subprocess
import argparse
from extractor import extract_img


def net_namespace(args):

    # unshare.unshare(unshare.CLONE_NEWNET)

    subprocess.run(
        ["ip", "link", "add", "zogo", "type", "veth", "peer", "name", "zaga"]
    )

    # Bring up zogo in the main namespace
    subprocess.run(["ip", "link", "set", "zogo", "up"])

    # Assign IP address to zogo in the main namespace
    subprocess.run(["ip", "addr", "add", "192.168.1.1/24", "dev", "zogo"])

    unshare.unshare(unshare.CLONE_NEWNET)

    command = "lsns | grep 'dl-run.py' | grep 'net' | awk '{print $4}'"

    result = subprocess.run(
        command, shell=True, check=True, stdout=subprocess.PIPE, text=True
    )

    net_pid = result.stdout.strip()

    # Move zaga to net namespace
    subprocess.run(["ip", "link", "set", "zaga", "netns", f"{net_pid}"])

    # Bring up loopback interface in mynamespace namespace
    subprocess.run(
        [
            "ip",
            "netns",
            "exec",
            f"{net_pid}",
            "ip",
            "link",
            "set",
            "dev",
            "lo",
            "up",
        ]
    )

    # Bring up zaga in mynamespace namespace
    subprocess.run(
        [
            "ip",
            "netns",
            "exec",
            f"{net_pid}",
            "ip",
            "link",
            "set",
            "dev",
            "zaga",
            "up",
        ]
    )

    # Assign IP address to zaga in mynamespace namespace
    subprocess.run(
        [
            "ip",
            "netns",
            "exec",
            f"{net_pid}",
            "ip",
            "addr",
            "add",
            "{}/24".format(args.ip_addr),
            "dev",
            "zaga",
        ]
    )

    pass


def uts_namespace(args):
    unshare.unshare(unshare.CLONE_NEWUTS)
    os.system("hostname {}".format(args.hostname))
    pass


def mnt_namespace(args):
    unshare.unshare(unshare.CLONE_NEWNS)
    pass


def pid_namespace(args):
    unshare.unshare(unshare.CLONE_NEWPID)
    pass


def cpu_cgroup(args, or_pid):
    if args.mem_size != "max":
        os.system("echo " + str(or_pid) + " > /sys/fs/cgroup/mycgrp/cgroup.procs")
        os.system(
            "echo" + str(args.cpu_num) + " 100000" + " > sys/fs/cgroup/mycgrp/cpu.max"
        )
    pass


def mem_cgroup(args, or_pid):
    if args.mem_size != "max":
        os.system("echo " + str(or_pid) + " > /sys/fs/cgroup/mycgrp/cgroup.procs")
        os.system("echo {}M > /sys/fs/cgroup/mycgrp/memory.max ".format(args.mem_size))
    pass


def pid_cgroup(args, or_pid):
    if args.mem_size != "max":
        print(or_pid)
        os.system("echo " + str(or_pid) + " > /sys/fs/cgroup/mycgrp/cgroup.procs")
        os.system("echo {} > /sys/fs/cgroup/mycgrp/pids.max ".format(args.pids_num))
    pass


def exe_bash(args):
    run_dest = "/etc/DL/runc"
    os.makedirs(run_dest, exist_ok=True)
    extract_img(args.img_name, run_dest)
    root_path = f"{run_dest}/{args.img_name[:-4]}"
    newpid = os.fork()
    if newpid == 0:
        os.chdir(root_path)
        os.chroot(".")
        os.system("mount -t proc proc /proc")
        os.system("mount -t sysfs sys /sys")
        os.system("mount --bind /dev /dev")
        if args.cmnd == "":
            os.execle("/bin/sh", "/bin/sh", "./startpoint.sh", os.environ)
        else:
            os.execle("/bin/sh", args.cmnd, os.environ)
    else:
        os.wait()
    pass


if __name__ == "__main__":

    print("*  welcome to DL *")

    parser = argparse.ArgumentParser(description="This is a docker like (DL).")
    run_dest = "/etc/DL/runc"
    os.makedirs(run_dest, exist_ok=True)
    if not os.path.exists("/sys/fs/cgroup/mycgrp"):
        os.makedirs("/sys/fs/cgroup/mycgrp")

    parser.add_argument(
        "--hostname",
        action="store",
        dest="hostname",
        type=str,
        default="DLIKE",
        help="set the container's hostname",
    )

    parser.add_argument(
        "--ip_addr",
        action="store",
        dest="ip_addr",
        type=str,
        default="192.168.1.2",
        help="set the container's ip address",
    )

    parser.add_argument(
        "--mem",
        action="store",
        dest="mem_size",
        type=str,
        default="max",
        help="set the container's memory size (MB)",
    )

    parser.add_argument(
        "--cpu",
        action="store",
        dest="cpu_num",
        type=str,
        default="max",
        help="set the container's cpu number",
    )
    parser.add_argument(
        "--pids",
        action="store",
        dest="pids_num",
        type=str,
        default="max",
        help="set the container's cpu number",
    )

    parser.add_argument(
        "--image",
        action="store",
        dest="img_name",
        type=str,
        default="run",
        help="give the name of image in working directory to run it",
    )
    parser.add_argument(
        "--command",
        action="store",
        dest="cmnd",
        type=str,
        default="",
        help="set the command to execute it in the container ",
    )

    args = parser.parse_args()

    or_pid = os.getpid()

    # create hostname namespace
    uts_namespace(args)
    # create network namespace
    # net_namespace(args)
    # create filesystem namespace
    mnt_namespace(args)
    # create pid namespace
    pid_namespace(args)
    # create cpu cgoup
    cpu_cgroup(args, or_pid)
    # create memory cgroup
    mem_cgroup(args, or_pid)
    # create pids cgroup
    pid_cgroup(args, or_pid)
    # execute the sh process "/bin/sh"
    exe_bash(args)
