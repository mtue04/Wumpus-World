import sys
import subprocess
from importlib import metadata


def check_and_install_packages():
    """
    This function checks for required packages listed in requirements.txt and installs any that are missing.
    """
    # Read requirements.txt file to get required packages
    required_packages = []
    with open("src/requirements.txt", "r") as f:
        required_packages = [
            line.strip() for line in f if line.strip() and not line.startswith("#")
        ]

    missing_packages = []
    outdated_packages = []
    up_to_date_packages = []

    for package in required_packages:
        package_name, required_version = (
            package.split("==") if "==" in package else (package, None)
        )

        try:
            installed_version = metadata.version(package_name)
            if required_version and installed_version != required_version:
                outdated_packages.append(
                    (package_name, installed_version, required_version)
                )
            else:
                up_to_date_packages.append((package_name, installed_version))
        except metadata.PackageNotFoundError:
            missing_packages.append(package)

    if missing_packages:
        print("Installing missing packages...")
        for package in missing_packages:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

    if outdated_packages:
        print("Updating outdated packages...")
        for package, installed_version, required_version in outdated_packages:
            print(
                f"Updating {package} from {installed_version} to {required_version}..."
            )
            subprocess.check_call(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "--upgrade",
                    f"{package}=={required_version}",
                ]
            )

    # Show info about installed packages
    print("Status of required packages:")
    for package, version in up_to_date_packages:
        print(f"{package}: {version} (Installed)")
    for package, installed_version, required_version in outdated_packages:
        print(f"{package}: {installed_version} -> {required_version} (Updated)")
    for package in missing_packages:
        print(f"{package}: (Newly installed)")

    print("All required packages are installed and up-to-date.")
