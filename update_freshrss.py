# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "requests",
#     "typer",
# ]
# ///
import platform
import re
import subprocess
import zipfile
from pathlib import Path
from xml.etree import ElementTree

import requests
import typer


def check_version(version: str):
    pattern = re.compile(r"\d+\.\d+\.\d+")
    if not re.match(pattern, version):
        raise ValueError(f"The version number does not match the pattern 'major.minor.patch'.")


def get_zip_file_path(version: str):
    return Path.home() / "Downloads" / f"FreshRSS-{version}.zip"


def download_version(version: str):
    """Downloads the source code zip file for given version of FreshRSS from GitHub:

    How to download a file with Python:
    https://stackoverflow.com/questions/67833450/how-to-download-a-file-using-requests
    """
    check_version(version)
    response = requests.request(
        method="GET",
        url=f"https://github.com/FreshRSS/FreshRSS/archive/refs/tags/{version}.zip"
    )
    with open(get_zip_file_path(version), mode="wb") as fh:
        fh.write(response.content)


def extract_version(version: str):
    """Extracts a previously downloaded zip file that contains the FreshRSS source code:

    How to unzip files with Python:
    https://stackoverflow.com/questions/3451111/unzipping-files-in-python
    """
    zip_file_path = get_zip_file_path(version)
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(path=zip_file_path.parent)


def prepend_xml_info(ffs_file: Path):
    old_content = ffs_file.read_text(encoding="utf-8")
    ffs_file.write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n' +
        old_content
    )


def create_ffs_config(version: str):
    """Loads the FreeFileSync template and adds the version number to the left path:

    How to modify XML files:
    https://docs.python.org/3/library/xml.etree.elementtree.html#modifying-an-xml-file
    """
    ffs_template = Path.home() / "Dokumente" / "FreshRSS-Update-Template.ffs_gui"
    et = ElementTree.parse(ffs_template)
    folder_pair = et.find("FolderPairs")
    pair = folder_pair.find("Pair")
    left = pair.find("Left")
    path_template = left.text
    left.text = path_template.format(version=version)
    ffs_output = Path.home() / "Downloads" / f"FreshRSS-{version} Update.ffs_gui"
    et.write(ffs_output)
    prepend_xml_info(ffs_output)


def start_ffs(version: str):
    """Open FreeFileSync with the new configuration file:

    The script continues when FreeFileSync is closed.

    How to run a subprocess:
    https://docs.python.org/3/library/subprocess.html#using-the-subprocess-module
    """
    ffs_output = Path.home() / "Downloads" / f"FreshRSS-{version} Update.ffs_gui"
    if platform.system() == "Windows":
        ffs_exe = Path(r"C:\Program Files\FreeFileSync\FreeFileSync.exe")
        subprocess.run([ffs_exe, ffs_output])
    elif platform.system() == "Linux":
        subprocess.run(["flatpak", "run", "org.freefilesync.FreeFileSync", ffs_output])
    else:
        print("Unsupported operating system.")


def open_website():
    """Opens https://rss-reader.eu with the default webbrowser:

    The PowerShell Command Start-Process is used to open the URL.

    How to open a URL with the default webbrowser
    https://stackoverflow.com/questions/66392447/powershell-open-url-and-login
    """
    url = "https://rss-reader.eu"
    if platform.system() == "Windows":
        subprocess.run(["pwsh", "-Command", "Start-Process", url])
    elif platform.system() == "Linux":
        subprocess.run(["xdg-open", url])
    else:
        print("Unsupported operating system.")


def main(version: str):
    # TODO: use a class with methods
    download_version(version)
    extract_version(version)
    create_ffs_config(version)
    start_ffs(version)
    open_website()


if __name__ == "__main__":
    typer.run(main)
