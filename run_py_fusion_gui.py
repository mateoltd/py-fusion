#!/usr/bin/env python3
"""
Launcher script for Py-Fusion GUI.

This script launches the Py-Fusion GUI application.
"""

import sys
import os
import traceback

try:
    # Add the parent directory to sys.path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)

    # Import and run the main function
    from py_fusion_gui.main import main

    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("\nPlease make sure you have installed all required dependencies:")
    print("Using Conda: conda env create -f environment.yml && conda activate py-fusion")
    print("Using pip: pip install -r requirements.txt")
    print("\nDetailed error information:")
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    print("\nDetailed error information:")
    traceback.print_exc()
    sys.exit(1)
