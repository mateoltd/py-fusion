"""
Analysis model for the Py-Fusion application.

This module handles pre-merge analysis to show the user what will happen
during the merge operation.
"""

import os
import filecmp
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from py_fusion_gui.utils.temp_folder_manager import TempFolderManager

class FileAction:
    """Represents a file action that will be performed during merge."""
    MOVE = "move"
    SKIP = "skip"
    RENAME = "rename"

    def __init__(self, action_type, source_path, dest_path, reason=None):
        """Initialize a file action.

        Args:
            action_type: Type of action (MOVE, SKIP, RENAME)
            source_path: Source file path
            dest_path: Destination file path
            reason: Reason for the action (e.g., "identical file")
        """
        self.action_type = action_type
        self.source_path = source_path
        self.dest_path = dest_path
        self.reason = reason

    def __str__(self):
        """Return a string representation of the action."""
        if self.action_type == FileAction.MOVE:
            return f"Move: {self.source_path} -> {self.dest_path}"
        elif self.action_type == FileAction.SKIP:
            return f"Skip: {self.source_path} ({self.reason})"
        elif self.action_type == FileAction.RENAME:
            return f"Rename: {self.source_path} -> {self.dest_path} ({self.reason})"
        return f"Unknown action: {self.action_type}"

class AnalysisWorker(QThread):
    """Worker thread for analyzing folder merge operations."""

    # Signals
    progress_updated = pyqtSignal(int, int)  # current, total
    analysis_started = pyqtSignal()
    analysis_completed = pyqtSignal(list, dict)  # actions, stats
    analysis_failed = pyqtSignal(str)

    def __init__(self, destination, sources):
        """Initialize the analysis worker.

        Args:
            destination: Path to the destination folder
            sources: List of source folder paths
        """
        super().__init__()
        self.destination = destination
        self.sources = sources
        self.is_cancelled = False

    def run(self):
        """Run the analysis in a separate thread."""
        try:
            self.analysis_started.emit()

            actions = []
            stats = {
                'files_to_move': 0,
                'files_to_skip': 0,
                'files_to_rename': 0,
                'directories_to_create': 0,
                'total_files': 0,
                'empty_source_folders': 0
            }

            # Check for empty source folders
            temp_manager = TempFolderManager()
            for source in self.sources:
                if temp_manager.is_empty_folder(source):
                    stats['empty_source_folders'] += 1

            # Count total files for progress reporting
            total_files = 0
            for source in self.sources:
                for root, _, files in os.walk(source):
                    total_files += len(files)

            # Initialize progress counter
            processed_files = 0

            # Analyze each source folder
            for source in self.sources:
                if self.is_cancelled:
                    break

                # Check if this folder might become empty after merge
                has_files = False
                for root, _, files in os.walk(source):
                    for file in files:
                        src_file = os.path.join(root, file)
                        rel_path = os.path.relpath(root, source)
                        if rel_path == '.':
                            rel_path = ''
                        dest_dir = os.path.join(self.destination, rel_path)
                        dest_file = os.path.join(dest_dir, file)

                        # If all files will be moved or skipped, the folder will be empty
                        has_files = True

                if not has_files:
                    # This folder is already empty
                    stats['empty_source_folders'] += 1

                for root, dirs, files in os.walk(source):
                    if self.is_cancelled:
                        break

                    # Calculate relative path from source root
                    rel_path = os.path.relpath(root, source)
                    if rel_path == '.':
                        rel_path = ''

                    # Check if destination directories exist
                    dest_dir = os.path.join(self.destination, rel_path)
                    if not os.path.exists(dest_dir):
                        stats['directories_to_create'] += 1

                    # Analyze each file
                    for file in files:
                        if self.is_cancelled:
                            break

                        src_file = os.path.join(root, file)
                        dest_file = os.path.join(dest_dir, file)

                        stats['total_files'] += 1

                        # Check if destination file exists
                        if os.path.exists(dest_file):
                            # Compare files
                            if filecmp.cmp(src_file, dest_file, shallow=False):
                                # Files are identical, skip
                                actions.append(FileAction(
                                    FileAction.SKIP,
                                    src_file,
                                    dest_file,
                                    "identical file"
                                ))
                                stats['files_to_skip'] += 1
                            else:
                                # Files are different, rename
                                base, ext = os.path.splitext(file)
                                count = 1
                                new_name = f"{base}_{count}{ext}"
                                new_dest = os.path.join(dest_dir, new_name)

                                # Find an available name
                                while os.path.exists(new_dest):
                                    if filecmp.cmp(src_file, new_dest, shallow=False):
                                        # Found an identical file with a different name
                                        actions.append(FileAction(
                                            FileAction.SKIP,
                                            src_file,
                                            new_dest,
                                            "identical file with different name"
                                        ))
                                        stats['files_to_skip'] += 1
                                        break
                                    count += 1
                                    new_name = f"{base}_{count}{ext}"
                                    new_dest = os.path.join(dest_dir, new_name)

                                # If we didn't break (no identical file found), add rename action
                                else:
                                    actions.append(FileAction(
                                        FileAction.RENAME,
                                        src_file,
                                        new_dest,
                                        "file with same name exists"
                                    ))
                                    stats['files_to_rename'] += 1
                        else:
                            # Destination file doesn't exist, move
                            actions.append(FileAction(
                                FileAction.MOVE,
                                src_file,
                                dest_file
                            ))
                            stats['files_to_move'] += 1

                        # Update progress
                        processed_files += 1
                        self.progress_updated.emit(processed_files, total_files)

            # Emit completion signal with results
            if not self.is_cancelled:
                self.analysis_completed.emit(actions, stats)

        except Exception as e:
            self.analysis_failed.emit(str(e))

    def cancel(self):
        """Cancel the analysis."""
        self.is_cancelled = True

class AnalysisModel(QObject):
    """Model for analyzing folder merge operations."""

    # Forward signals from the worker
    progress_updated = pyqtSignal(int, int)
    analysis_started = pyqtSignal()
    analysis_completed = pyqtSignal(list, dict)
    analysis_failed = pyqtSignal(str)

    def __init__(self):
        """Initialize the analysis model."""
        super().__init__()
        self.worker = None

    def start_analysis(self, destination, sources):
        """Start an analysis operation.

        Args:
            destination: Path to the destination folder
            sources: List of source folder paths
        """
        # Create and configure the worker
        self.worker = AnalysisWorker(destination, sources)

        # Connect signals
        self.worker.progress_updated.connect(self.progress_updated)
        self.worker.analysis_started.connect(self.analysis_started)
        self.worker.analysis_completed.connect(self.analysis_completed)
        self.worker.analysis_failed.connect(self.analysis_failed)

        # Start the worker thread
        self.worker.start()

    def cancel_analysis(self):
        """Cancel the current analysis operation."""
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.worker.wait()  # Wait for the thread to finish

    def is_analysis_running(self):
        """Check if an analysis operation is currently running."""
        return self.worker is not None and self.worker.isRunning()
