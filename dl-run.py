#!/usr/bin/python3
import os
import sys
import unshare
import argparse
from extractor import extract_img


def net_namespace(args):
    unshare.unshare(unshare.CLONE_NEWNET)
    os.system("modprobe dummy")
    os.system("ip link add dummy1 type dummy")
    os.system("ip link set name eth1 dev dummy1")
    os.system("ip addr add {} dev eth1 ".format(args.ip_addr))
    os.system("ip link set eth1 up")
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


def cpu_cgroup(args):
    os.system("echo " + str(os.getpid()) + " > /sys/fs/cgroup/mycgrp/cgroup.procs")
    os.system(f"echo {args.cpu_num} 100000 > sys/fs/cgroup/mycgrp/cpu.max")
    pass


def mem_cgroup(args):
    os.system("echo " + str(os.getpid()) + " > /sys/fs/cgroup/mycgrp/cgroup.procs")
    os.system("echo {}M > /sys/fs/cgroup/mycgrp/memory.max ".format(args.mem_size))
    pass


def pid_cgroup(args):
    os.system("echo " + str(os.getpid()) + " > /sys/fs/cgroup/mycgrp/cgroup.procs")
    os.system("echo {} > /sys/fs/cgroup/mycgrp/pids.max ".format(args.pids_num))
    pass


def exe_bash(args):
    run_dest = "/etc/DL/runc"
    os.makedirs(run_dest, exist_ok=True)
    extract_img(args.img_name, run_dest)
    root_path = f"{run_dest}/{args.img_name[:-4]}"
    newpid = os.fork()
    if newpid == 0:
        # print(root_path)
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
        default="10.0.0.1",
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
        default="20000",
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

    # create hostname namespace
    uts_namespace(args)
    # create network namespace
    net_namespace(args)
    # create filesystem namespace
    mnt_namespace(args)
    # create pid namespace
    pid_namespace(args)
    # create cpu cgoup
    cpu_cgroup(args)
    # create memory cgroup
    mem_cgroup(args)
    # create pids cgroup
    pid_cgroup(args)
    # execute the sh process "/bin/sh"
    exe_bash(args)
