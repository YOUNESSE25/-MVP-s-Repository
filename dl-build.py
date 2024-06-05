#!/usr/bin/python3
import os
import subprocess
from uuid import uuid4
from img_dn import download_docker_image, extract_image_layers


todo = []
cmnd = {"FROM": "img", "COPY": "cp", "MKDIR": "mkdir", "CMD": "edit", "CD": "cd"}
image_id = str(uuid4())
downld_dest = "/etc/DL/builder/downloaded_images"


class run_cmd:

    def __init__(self):
        image_id = str(uuid4())
        os.makedirs(downld_dest, exist_ok=True)
        pass

    def img(self, line=None):
        lst_line = line.split()[1].split(":")
        image_name = lst_line[1].strip()
        os.makedirs(downld_dest, exist_ok=True)

        # Download image
        # subprocess.run(
        #     ["curl", "-o", f"{image_name}.tar", f"https://hub.docker.com/{image_name}"]
        # )
        # print("Image downloaded")
        download_docker_image(image_name, "latest", downld_dest)

        # Extract image
        # subprocess.run(["tar", "-xzf", f"{image_name}.tar"])
        extract_image_layers(downld_dest, image_name, "latest")

        # Fork process
        pid = os.fork()
        if pid == 0:
            os.chroot(f"{downld_dest}")
            txt = "nameserver 1.1.1.1"
            with open("/etc/resolv.conf", "w") as resolv_conf:
                resolv_conf.write(txt)
            subprocess.run(["apk", "upgrade"])
            subprocess.run(["apk", "update"])
            subprocess.run(["apk", "add", lst_line[1]])
        else:
            os.wait()
        print("Image is ready")

    def cp(self, line=None):
        lst_line = line.split()
        subprocess.run(["cp"] + lst_line[1:])

    def mkdir(self, line=None):
        lst_line = line.split()
        subprocess.run(["mkdir", "-p", lst_line[1]])

    def cd(self, line=None):
        lst_line = line.split()
        downld_dest = os.path.join(downld_dest, lst_line)

    def edit(self, line=None):
        """edit function that build a shell script"""

        lst_line = line.split()
        cmd = " ".join(lst_line[1:])

        with open("startpoint.sh", "w") as f:
            f.write("#!/bin/sh\n")
            f.write(cmd + "\n")

        subprocess.run(["chmod", "+x", "startpoint.sh"])
        subprocess.run(["cp", "startpoint.sh", f"{downld_dest}"])
        pid = os.fork()
        if pid == 0:
            os.chroot(f"{downld_dest}")
            subprocess.run(["tar", "-cf", f"image_{image_id}.tar", "*"])
        else:
            os.wait()
            subprocess.run(["cp", f"{downld_dest}/image_{image_id}.tar", f"."])


with open("DLfile", "r") as f:
    for line in f:
        todo = line.split()
        if todo[0] in cmnd:
            cls = run_cmd()
            method = getattr(cls, cmnd[todo[0]])
            method(line)
