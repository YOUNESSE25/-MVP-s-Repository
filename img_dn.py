#!/usr/bin/python3


import subprocess
import os


def download_docker_image(image, tag, destination):
    # Construct the skopeo command
    skopeo_command = [
        "skopeo",
        "copy",
        f"docker://docker.io/library/{image}:{tag}",
        f"oci:{destination}/{image}",
    ]

    try:
        # Run the skopeo command
        result = subprocess.run(
            skopeo_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        print(f"Image {image}:{tag} downloaded successfully.")
        print(result.stdout.decode())
    except subprocess.CalledProcessError as e:
        print(f"Error downloading image {image}:{tag}: {e.stderr.decode()}")


def extract_image_layers(destination, image, tag):
    image_dir = os.path.join(destination, image)
    blobs_dir = os.path.join(image_dir, "blobs", "sha256")

    # Find all the .tar.gz layer files
    layer_files = [f for f in os.listdir(blobs_dir)]

    # Extract each layer
    for layer_file in layer_files:
        layer_path = os.path.join(blobs_dir, layer_file)
        extract_command = ["tar", "-xzf", layer_path, "-C", destination]

        try:
            subprocess.run(extract_command, check=True)
            print(f"Extracted layer {layer_file}")
        except subprocess.CalledProcessError as e:
            # print(f"Error extracting layer {layer_file}: {e.stderr.decode()}")
            pass


if __name__ == "__main__":
    image_name = "alpine"
    image_tag = "latest"
    downld_dest = "./downloaded_images"

    # Create the destination directory if it doesn't exist
    os.makedirs(downld_dest, exist_ok=True)

    # Download the Docker image
    download_docker_image(image_name, image_tag, downld_dest)

    # Extract the image layers
    extract_image_layers(downld_dest, image_name, image_tag)
