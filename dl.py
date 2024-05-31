#!/usr/bin/python3
import unshare
import argparse
import os
import sys


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


def exe_bash(args):
    newpid = os.fork()
    if newpid == 0:
        os.chdir(args.root_path)
        os.chroot(".")
        os.system("mount -t proc proc /proc")
        os.system("mount -t sysfs sys /sys")
        os.system("mount --bind dev /dev")
        os.execle("/bin/sh", "/bin/sh", os.environ)
    else:
        os.wait()
    pass


if __name__ == "__main__":

    print("*  welcome to DL *")

    parser = argparse.ArgumentParser(description="This is a docker like(DL).")

    parser.add_argument(
        "--hostname",
        action="store",
        dest="hostname",
        type=str,
        default="administrator",
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
        type=int,
        default=10,
        help="set the container's memory size (MB)",
    )

    parser.add_argument(
        "--cpu",
        action="store",
        dest="cpu_num",
        type=int,
        default=1,
        help="set the container's cpu number",
    )

    parser.add_argument(
        "--root_path",
        action="store",
        dest="root_path",
        type=str,
        default="/home/azarus/project/cpro/environ",
        help="set the new root file system path of the container",
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
    # execute the bash process "/bin/bash"
    exe_bash(args)
