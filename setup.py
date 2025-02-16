import setuptools
from setuptools import setup, find_packages
from setuptools.command.install import install
import subprocess
import sys
import os
import platform
import urllib.request
import tarfile
import zipfile

GITLEAKS_VERSION = "8.23.2"
GITLEAKS_LINUX_URL = f"https://github.com/gitleaks/gitleaks/releases/download/v{GITLEAKS_VERSION}/gitleaks_{GITLEAKS_VERSION}_linux_x64.tar.gz"
GITLEAKS_WINDOWS_URL = f"https://github.com/gitleaks/gitleaks/releases/download/v{GITLEAKS_VERSION}/gitleaks_{GITLEAKS_VERSION}_windows_x64.zip"
INSTALL_DIR = os.path.expanduser("~/.local/bin")


def is_gitleaks_installed():
    """
    Check if Gitleaks is installed by running gitleaks --version.
    """
    try:
        subprocess.run(["gitleaks", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print("✅ Gitleaks is already installed.")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def download_and_install_gitleaks():
    """
    Download and install Gitleaks based on the user's OS.
    """
    os_name = platform.system().lower()

    if os_name == "linux":
        url = GITLEAKS_LINUX_URL
        filename = "gitleaks_linux.tar.gz"
        extract_to = INSTALL_DIR
    elif os_name == "windows":
        url = GITLEAKS_WINDOWS_URL
        filename = "gitleaks_windows.zip"
        extract_to = INSTALL_DIR
    else:
        print(f"❌ Unsupported OS: {os_name}. Please install Gitleaks manually.")
        sys.exit(1)

    # Create the install directory if it does not exist
    os.makedirs(INSTALL_DIR, exist_ok=True)

    # Download Gitleaks
    print(f"⬇️ Downloading Gitleaks from {url} ...")
    file_path = os.path.join(INSTALL_DIR, filename)
    urllib.request.urlretrieve(url, file_path)
    print(f"✅ Downloaded Gitleaks to {file_path}")

    # Extract the downloaded archive
    if filename.endswith(".tar.gz"):
        with tarfile.open(file_path, "r:gz") as tar:
            tar.extractall(path=INSTALL_DIR)
    elif filename.endswith(".zip"):
        with zipfile.ZipFile(file_path, "r") as zip_ref:
            zip_ref.extractall(INSTALL_DIR)

    # Set executable permissions (for Linux/Mac)
    gitleaks_path = os.path.join(INSTALL_DIR, "gitleaks")
    if os_name == "linux":
        subprocess.run(["chmod", "+x", gitleaks_path], check=True)

    print(f"✅ Gitleaks installed successfully in {INSTALL_DIR}")
    print(f"🔍 Run `{gitleaks_path} --version` to verify the installation.")

    # Cleanup downloaded files
    os.remove(file_path)


class CustomInstallCommand(install):
    """
    Custom installation step to check for Gitleaks before proceeding.
    """
    def run(self):
        if not is_gitleaks_installed():
            print("⚠️ Gitleaks is not installed. Installing it now...")
            download_and_install_gitleaks()
        else:
            print("✅ Gitleaks is already installed.")
        install.run(self)


setup(
    name="RepoRecon",
    version="1.0.5",
    author="Your Name",
    author_email="your.email@example.com",
    description="A CLI tool to search GitHub repositories and integrate Gitleaks for scanning.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/RepoRecon",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "boto3>=1.28.0",
        "requests>=2.31.0",
        "pyfiglet>=0.8.post1",
        "rich>=13.5.2",
        "stripe>=5.12.1",
        "azure-identity==1.19.0",
        "azure-mgmt-resource==23.2.0",
        "azure-keyvault-secrets==4.9.0"
    ],
    entry_points={
        "console_scripts": [
            "RepoRecon=RepoRecon.main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.6",
    cmdclass={
        "install": CustomInstallCommand,
    },
)
