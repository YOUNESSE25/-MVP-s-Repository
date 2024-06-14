import tarfile
import os
import subprocess
import shutil


def extract_img(img_name, extract_path):

    # Check if the image exists
    file_path = os.path.join(os.getcwd(), img_name)
    if not os.path.exists(file_path):
        print(f"The image {img_name} does not exist.")
        return

    # Check if the extract path exists, if not, create it
    if not os.path.exists(extract_path):
        os.makedirs(extract_path, exist_ok=True)
        print(f"Created directory {extract_path}")

    try:
        with tarfile.open(file_path, "r:tar") as tar:
            print()
            # root_path = os.path.join(extract_img, img_name)
            root_path = f"{extract_path}/{img_name[:-4]}"
            print()
            print(root_path)
            tar.extractall(path=root_path)
            print(f" {img_name} is ready")
            return root_path
    except tarfile.TarError as e:
        print(f"Error {img_name}: {e}")


if __name__ == "__main__":
    # Path to the tar file
    img_name = "/home/azarus/ALX-Project/imge.tar"

    # Directory where you want to extract the tar file
    extract_path = "/home/extract"

    extract_img(img_name, extract_path)
