#!/usr/bin/python3
import os
import subprocess

todo = []
cmnd = {"FROM": "img", "COPY": "cp", "MKDIR": "mkdir", "CMD": "edit"}


class run_cmd:
    def img(self, line=None):
        lst_line = line.split()
        lst_line = lst_line.split(":")
        subprocess.run(
            [
                f"curl -o {lst_line[1]}.tar curl -o imageName.tar.gz https://hub.docker.com/{lst_line[1]}"
            ]
        )
        subprocess.run([f"tar -xzf {lst_line[1]}.tar"])
        os.chroot(f"./{lst_line[1]}")
        subprocess.run([f"tar -xzf {lst_line[1]}.tar"])

        pass

    def cp(self, line=None):
        lst_line = line.split()
        subprocess.run(["cp"] + lst_line[1:])

    def mkdir(self, line=None):
        lst_line = line.split()
        subprocess.run([f"mkdir {lst_line[1]}"])
        pass

    def edit(self, line=None):

        pass


with open("DLfile", "r") as f:
    for line in f:
        todo = line.split()
        if todo[0] in cmnd:
            cls = run_cmd()
            method = getattr(cls, cmnd[todo[0]])
            method(line)
