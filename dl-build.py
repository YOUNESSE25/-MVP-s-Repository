#!/usr/bin/python3
import os
import subprocess
from uuid import uuid4
from img_dn import download_docker_image, extract_image_layers


todo = []
cmnd = {"FROM": "img", "COPY": "cp", "MKDIR": "mkdir", "CMD": "edit", "CD": "cd"}
downld_dest = "/etc/DL/builder/downloaded_images"


class RunCmd:

    def __init__(self):
        self.image_id = str(uuid4())
        os.makedirs(downld_dest, exist_ok=True)

    def img(self, line=None):
        lst_line = line.split()[1].split(":")
        image_name = lst_line[0]
        os.makedirs(downld_dest, exist_ok=True)

        # Download image
        download_docker_image(image_name, "latest", downld_dest)

        # Extract image
        extract_image_layers(downld_dest, image_name, "latest")

        # Fork process
        pid = os.fork()
        if pid == 0:
            os.chroot(downld_dest)
            with open("/etc/resolv.conf", "w") as resolv_conf:
                resolv_conf.write("nameserver 1.1.1.1")
            subprocess.run(["apk", "upgrade"])
            subprocess.run(["apk", "update"])
            subprocess.run(["apk", "add", image_name])
        else:
            os.wait()
        print("Image is ready")

    def cp(self, line=None):
        lst_line = line.split()
        cmd_2 = os.path.join(downld_dest, lst_line[2])
        subprocess.run(["cp", lst_line[1], cmd_2])

    def mkdir(self, line=None):
        lst_line = line.split()
        new_dir = os.path.join(downld_dest, lst_line[1])
        os.makedirs(new_dir, exist_ok=True)

    def cd(self, line=None):
        global downld_dest
        lst_line = line.split()
        downld_dest = os.path.join(downld_dest, lst_line[1])

    def edit(self, line=None):
        """Edit function that builds a shell script"""
        lst_line = line.split()
        cmd = " ".join(lst_line[1:])

        with open("startpoint.sh", "w") as f:
            f.write("#!/bin/sh\n")
            f.write(cmd + "\n")

        subprocess.run(["chmod", "+x", "startpoint.sh"])
        subprocess.run(["cp", "startpoint.sh", downld_dest])

        os.chdir(downld_dest)

        # Check if there are files to be archived
        if os.listdir(downld_dest):
            subprocess.run(["tar", "-cf", f"image_{self.image_id}.tar", "*"])
            subprocess.run(
                [
                    "cp",
                    os.path.join(downld_dest, f"image_{self.image_id}.tar"),
                    "/home/azarus/ALX-Project",
                ]
            )
        else:
            print("No files to archive in the directory.")


with open("DLfile", "r") as f:
    for line in f:
        todo = line.split()
        if todo[0] in cmnd:
            cls = RunCmd()
            method = getattr(cls, cmnd[todo[0]])
            method(line)
