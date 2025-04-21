#!/usr/bin/env python3
"""
Py-Fusion: Tool for merging multiple resource folders

This script allows merging the content of several folders into a destination folder,
intelligently handling duplicate files and preserving the directory structure.

Usage examples:
    # Merge default folders (RESOURCES 2, RESOURCES 3, etc.) into RESOURCES
    python index.py

    # Specify destination folder and source folders
    python index.py --dest MyDestFolder --source Folder1 Folder2 Folder3

    # Simulation mode (no actual changes)
    python index.py --simulate

    # Verbose mode (shows more information)
    python index.py --verbose
"""

import os
import shutil
import filecmp
import argparse
import logging
import glob
from typing import List

# Logging system configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger('py-fusion')

# Global statistics
STATS = {
    'files_moved': 0,
    'files_skipped': 0,
    'files_renamed': 0,
    'directories_created': 0,
    'errors': 0
}

def setup_arguments() -> argparse.Namespace:
    """
    Configure and process command line arguments.

    Returns:
        argparse.Namespace: Object with processed arguments
    """
    parser = argparse.ArgumentParser(
        description='Merge multiple resource folders into a destination folder.',
        epilog='Developed as part of the py-fusion project.'
    )

    parser.add_argument('--dest', '-d', type=str, default='RESOURCES',
                        help='Destination folder where resources will be merged (default: RESOURCES)')

    parser.add_argument('--source', '-s', type=str, nargs='+',
                        help='List of source folders to merge. If not specified, '
                             'the folders RESOURCES 2, RESOURCES 3, etc. will be used')

    parser.add_argument('--simulate', '-S', action='store_true',
                        help='Simulation mode: shows what actions would be performed without making actual changes')

    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose mode: shows additional information during the process')

    parser.add_argument('--pattern', '-p', type=str, default=None,
                        help='Glob pattern to find source folders (e.g.: "RESOURCES*")')

    parser.add_argument('--include-hidden', '-H', action='store_true',
                        help='Include hidden files and folders in the merge (default: hidden files are skipped)')

    return parser.parse_args()

def move_or_rename(src_path: str, dst_path: str, simulate: bool = False) -> None:
    """
    Attempts to move a file from source to destination, handling duplicate cases.

    If the destination file already exists:
      - If it's identical to the source, the move is skipped.
      - If they're different, a numeric suffix is added until an available name is found.

    Args:
        src_path: Source file path
        dst_path: Destination file path
        simulate: If True, only simulates the operation without making actual changes
    """
    try:
        if os.path.exists(dst_path):
            # Compare files (exhaustive search)
            if filecmp.cmp(src_path, dst_path, shallow=False):
                logger.info(f"Skipped (identical duplicate): {src_path}")
                STATS['files_skipped'] += 1
                return
            else:
                # Find an available name by adding numeric suffix
                base, ext = os.path.splitext(os.path.basename(src_path))
                count = 1
                new_name = f"{base}_{count}{ext}"
                new_dst = os.path.join(os.path.dirname(dst_path), new_name)

                while os.path.exists(new_dst):
                    if filecmp.cmp(src_path, new_dst, shallow=False):
                        logger.info(f"Skipped (identical duplicate): {src_path}")
                        STATS['files_skipped'] += 1
                        return
                    count += 1
                    new_name = f"{base}_{count}{ext}"
                    new_dst = os.path.join(os.path.dirname(dst_path), new_name)

                dst_path = new_dst
                STATS['files_renamed'] += 1
                logger.debug(f"Renaming to: {new_name}")

        if not simulate:
            shutil.move(src_path, dst_path)

        logger.info(f"{'[SIMULATION] ' if simulate else ''}Moved: {src_path} -> {dst_path}")
        STATS['files_moved'] += 1

    except (PermissionError, OSError) as e:
        logger.error(f"Error moving {src_path}: {str(e)}")
        STATS['errors'] += 1

def merge_directories(source: str, destination: str, simulate: bool = False, include_hidden: bool = False) -> None:
    """
    Recursively merges the content of the 'source' folder into the 'destination' folder.

    Args:
        source: Source folder path
        destination: Destination folder path
        simulate: If True, only simulates the operation without making actual changes
        include_hidden: If True, hidden files will be included in the merge
    """
    try:
        if not os.path.exists(destination):
            if not simulate:
                os.makedirs(destination)
            logger.debug(f"{'[SIMULATION] ' if simulate else ''}Creating directory: {destination}")
            STATS['directories_created'] += 1

        for item in os.listdir(source):
            src_path = os.path.join(source, item)
            dst_path = os.path.join(destination, item)

            # Check if the item is hidden
            try:
                # Import the is_hidden_file function if available
                from py_fusion_gui.utils.platform_utils import is_hidden_file
                is_hidden = is_hidden_file(src_path)
            except ImportError:
                # Fall back to simple check if the function is not available
                is_hidden = item.startswith('.')

            # Skip hidden files unless include_hidden is True
            if is_hidden and not include_hidden:
                logger.debug(f"Skipped hidden item: {src_path}")
                STATS['files_skipped'] += 1
                continue

            if os.path.isdir(src_path):
                merge_directories(src_path, dst_path, simulate, include_hidden)
            else:
                move_or_rename(src_path, dst_path, simulate)

    except (PermissionError, OSError) as e:
        logger.error(f"Error processing directory {source}: {str(e)}")
        STATS['errors'] += 1

def get_source_folders(args: argparse.Namespace) -> List[str]:
    """
    Determines the source folders to merge based on the provided arguments.

    Args:
        args: Processed command line arguments

    Returns:
        List[str]: List of source folder paths
    """
    if args.source:
        return args.source
    elif args.pattern:
        return glob.glob(args.pattern)
    else:
        # Default folders
        return [
            "RESOURCES 2", "RESOURCES 3", "RESOURCES 4", "RESOURCES 5",
            "RESOURCES 6", "RESOURCES 7", "RESOURCES 8", "RESOURCES 9",
            "RESOURCES 10", "RESOURCES 11", "RESOURCES 12", "RESOURCES 13",
            "RESOURCES 15"
        ]

def merge_folders(destination: str, source_folders: List[str], simulate: bool = False, include_hidden: bool = False) -> None:
    """
    Merges multiple source folders into a destination folder.

    Args:
        destination: Destination folder path
        source_folders: List of source folder paths
        simulate: If True, only simulates the operation without making actual changes
        include_hidden: If True, hidden files will be included in the merge
    """
    try:
        if not os.path.exists(destination) and not simulate:
            logger.info(f"Creating destination folder: {destination}")
            os.makedirs(destination)
            STATS['directories_created'] += 1

        for folder in source_folders:
            if not os.path.exists(folder):
                logger.warning(f"Folder {folder} does not exist. Skipping.")
                continue

            logger.info(f"Processing folder merge: {folder}")
            for item in os.listdir(folder):
                src_item_path = os.path.join(folder, item)
                dst_item_path = os.path.join(destination, item)

                # Check if the item is hidden
                try:
                    # Import the is_hidden_file function if available
                    from py_fusion_gui.utils.platform_utils import is_hidden_file
                    is_hidden = is_hidden_file(src_item_path)
                except ImportError:
                    # Fall back to simple check if the function is not available
                    is_hidden = item.startswith('.')

                # Skip hidden files unless include_hidden is True
                if is_hidden and not include_hidden:
                    logger.debug(f"Skipped hidden item: {src_item_path}")
                    STATS['files_skipped'] += 1
                    continue

                if os.path.isdir(src_item_path):
                    merge_directories(src_item_path, dst_item_path, simulate, include_hidden)
                else:
                    move_or_rename(src_item_path, dst_item_path, simulate)

    except Exception as e:
        logger.error(f"Error during merge: {str(e)}")
        STATS['errors'] += 1

def show_statistics() -> None:
    """
    Shows a summary of the operation statistics.
    """
    logger.info("\nOperation Summary:")
    logger.info(f"  - Files moved: {STATS['files_moved']}")
    logger.info(f"  - Files skipped (duplicates): {STATS['files_skipped']}")
    logger.info(f"  - Files renamed: {STATS['files_renamed']}")
    logger.info(f"  - Directories created: {STATS['directories_created']}")
    logger.info(f"  - Errors encountered: {STATS['errors']}")

def main() -> None:
    """
    Main function that coordinates the folder merging process.
    """
    # Process command line arguments
    args = setup_arguments()

    # Configure logging level based on verbosity
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Show simulation mode if activated
    if args.simulate:
        logger.info("Running in SIMULATION mode (no actual changes will be made)")

    # Get source folders
    source_folders = get_source_folders(args)

    # Show configuration
    logger.info(f"Destination folder: {args.dest}")
    logger.info(f"Source folders: {', '.join(source_folders)}")

    # Show if hidden files will be included
    if args.include_hidden:
        logger.info("Hidden files and folders will be included in the merge")

    # Perform the merge
    merge_folders(args.dest, source_folders, args.simulate, args.include_hidden)

    # Show statistics
    show_statistics()

if __name__ == "__main__":
    main()
