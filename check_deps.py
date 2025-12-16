#!/usr/bin/env python3
"""
Dependency verification script
"""

import sys
import subprocess

REQUIRED_PACKAGES = [
    ("Pillow", "PIL"),
    ("psutil", "psutil"),
    ("colorama", "colorama"),
    ("loguru", "loguru"),
]

def check_package(package_name, import_name):
    """Check if a package is installed and importable"""
    try:
        __import__(import_name)
        return True, f"✓ {package_name}"
    except ImportError:
        return False, f"✗ {package_name} (missing)"

def main():
    print("Checking dependencies...\n")
    
    all_ok = True
    for package_name, import_name in REQUIRED_PACKAGES:
        ok, message = check_package(package_name, import_name)
        print(message)
        if not ok:
            all_ok = False
    
    print("\n" + "="*50)
    
    if all_ok:
        print("✓ All dependencies are installed!")
        print("\nYou can run the application with:")
        print("  python main.py")
        return 0
    else:
        print("✗ Some dependencies are missing.")
        print("\nInstall missing dependencies with:")
        print("  pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
