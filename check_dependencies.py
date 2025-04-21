#!/usr/bin/env python3
"""
Dependency checker for Py-Fusion.

This script checks if all required dependencies are installed.
"""

import sys
import importlib.util
import subprocess
import platform

def check_module(module_name):
    """Check if a module is installed.
    
    Args:
        module_name: Name of the module to check
        
    Returns:
        bool: True if the module is installed, False otherwise
    """
    return importlib.util.find_spec(module_name) is not None

def print_status(module_name, installed):
    """Print the installation status of a module.
    
    Args:
        module_name: Name of the module
        installed: Whether the module is installed
    """
    status = "✓ Installed" if installed else "✗ Not installed"
    print(f"{module_name.ljust(20)} {status}")

def main():
    """Check if all required dependencies are installed."""
    print("Checking dependencies for Py-Fusion...\n")
    
    # Check Python version
    python_version = platform.python_version()
    print(f"Python version: {python_version}")
    if tuple(map(int, python_version.split('.'))) < (3, 9):
        print("Warning: Py-Fusion requires Python 3.9 or higher.")
    print()
    
    # Required modules for the command-line version
    cli_modules = ['os', 'shutil', 'filecmp', 'argparse', 'logging', 'glob']
    
    # Required modules for the GUI version
    gui_modules = ['PyQt6', 'PyQt6.QtWidgets', 'PyQt6.QtCore', 'PyQt6.QtGui', 'qtawesome']
    
    # Check CLI modules
    print("Command-line dependencies:")
    cli_all_installed = True
    for module in cli_modules:
        installed = check_module(module)
        print_status(module, installed)
        cli_all_installed = cli_all_installed and installed
    
    # Check GUI modules
    print("\nGUI dependencies:")
    gui_all_installed = True
    for module in gui_modules:
        installed = check_module(module)
        print_status(module, installed)
        gui_all_installed = gui_all_installed and installed
    
    # Print summary
    print("\nSummary:")
    if cli_all_installed:
        print("✓ All command-line dependencies are installed.")
    else:
        print("✗ Some command-line dependencies are missing.")
    
    if gui_all_installed:
        print("✓ All GUI dependencies are installed.")
    else:
        print("✗ Some GUI dependencies are missing.")
    
    # Print installation instructions if needed
    if not cli_all_installed or not gui_all_installed:
        print("\nInstallation instructions:")
        print("Using Conda:")
        print("  conda env create -f environment.yml")
        print("  conda activate py-fusion")
        print("\nUsing pip:")
        print("  pip install -r requirements.txt")

if __name__ == "__main__":
    main()
