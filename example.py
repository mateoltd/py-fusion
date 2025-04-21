#!/usr/bin/env python3
"""
Example of using py-fusion as an imported module.

This script shows how to use py-fusion functions
by importing them as a module in another script.
"""

import os
from index import merge_folders, show_statistics

def create_example_structure():
    """
    Creates an example directory and file structure
    to demonstrate how py-fusion works.
    """
    # Create example directories
    directories = [
        "example_source1/subdir1",
        "example_source1/subdir2",
        "example_source2/subdir1",
        "example_source2/subdir3",
        "example_destination"
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)

    # Create example files
    files = [
        ("example_source1/file1.txt", "Content of file 1"),
        ("example_source1/file2.txt", "Content of file 2"),
        ("example_source1/subdir1/file3.txt", "Content of file 3"),
        ("example_source1/subdir2/file4.txt", "Content of file 4"),
        ("example_source2/file1.txt", "Content of file 1"),  # Identical duplicate
        ("example_source2/file2.txt", "Different content"),   # Same name, different content
        ("example_source2/subdir1/file5.txt", "Content of file 5"),
        ("example_source2/subdir3/file6.txt", "Content of file 6"),
    ]

    for path, content in files:
        with open(path, 'w') as f:
            f.write(content)

    print("Example structure created successfully.")

def main():
    """
    Main function that demonstrates using py-fusion as a module.
    """
    print("Example of using py-fusion as an imported module")
    print("=" * 50)

    # Create example structure
    create_example_structure()

    # Define source and destination folders
    source_folders = ["example_source1", "example_source2"]
    destination_folder = "example_destination"

    print(f"\nMerging folders {', '.join(source_folders)} into {destination_folder}...")

    # Call the merge function
    merge_folders(destination_folder, source_folders, simulate=False)

    # Show statistics
    show_statistics()

    print("\nExample completed. Check the 'example_destination' folder to see the result.")

if __name__ == "__main__":
    main()
