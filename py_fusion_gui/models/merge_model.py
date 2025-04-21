"""
Merge model for the Py-Fusion application.

This module handles the core functionality of merging folders,
integrating with the existing merge logic from the index.py script.
"""

import os
import sys
import time
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from py_fusion_gui.utils.temp_folder_manager import TempFolderManager

# Add the parent directory to sys.path to import the original merge functions
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from index import merge_folders, STATS

class MergeWorker(QThread):
    """Worker thread for performing folder merges without blocking the UI."""

    # Signals for progress updates
    progress_updated = pyqtSignal(dict)
    operation_started = pyqtSignal(str)
    operation_completed = pyqtSignal(dict)
    operation_failed = pyqtSignal(str)

    def __init__(self, destination, sources, simulate=False, include_hidden=False):
        """Initialize the merge worker.

        Args:
            destination: Path to the destination folder
            sources: List of source folder paths
            simulate: Whether to run in simulation mode
            include_hidden: Whether to include hidden files in the merge
        """
        super().__init__()
        self.destination = destination
        self.sources = sources
        self.simulate = simulate
        self.include_hidden = include_hidden
        self.is_cancelled = False

    def run(self):
        """Run the merge operation in a separate thread."""
        try:
            self.operation_started.emit("Starting merge operation...")

            # Reset stats before starting
            for key in STATS:
                STATS[key] = 0

            # Hook into the merge process to emit progress signals
            self._hook_progress_updates()

            # Initialize temp folder manager
            temp_manager = TempFolderManager()

            # Perform the merge
            merge_folders(self.destination, self.sources, self.simulate, self.include_hidden)

            # Check for empty source folders after merge and cache them
            for source in self.sources:
                if os.path.exists(source) and temp_manager.is_empty_folder(source):
                    self.operation_started.emit(f"Caching empty source folder: {source}")
                    cached_path = temp_manager.cache_empty_folder(source)
                    if cached_path:
                        self.operation_started.emit(f"Cached empty source folder: {source} -> {cached_path}")

            # Emit completion signal with final stats
            self.operation_completed.emit(STATS.copy())

        except Exception as e:
            self.operation_failed.emit(str(e))

    def cancel(self):
        """Cancel the merge operation."""
        self.is_cancelled = True

    def _hook_progress_updates(self):
        """Hook into the merge process to provide progress updates.

        This is a bit of a hack since the original merge_folders function
        doesn't provide progress callbacks. We'll periodically check the
        STATS dictionary and emit progress signals.
        """
        # Create a timer to periodically check and emit progress
        self._original_move_or_rename = sys.modules['index'].move_or_rename

        def wrapped_move_or_rename(*args, **kwargs):
            # Check if operation was cancelled
            if self.is_cancelled:
                raise InterruptedError("Operation cancelled by user")

            # Call the original function
            result = self._original_move_or_rename(*args, **kwargs)

            # Emit progress signal
            self.progress_updated.emit(STATS.copy())

            # Small delay to allow UI updates and prevent flooding signals
            time.sleep(0.001)

            return result

        # Replace the original function with our wrapped version
        sys.modules['index'].move_or_rename = wrapped_move_or_rename

class MergeModel(QObject):
    """Model for managing folder merge operations."""

    # Forward signals from the worker
    progress_updated = pyqtSignal(dict)
    operation_started = pyqtSignal(str)
    operation_completed = pyqtSignal(dict)
    operation_failed = pyqtSignal(str)

    def __init__(self):
        """Initialize the merge model."""
        super().__init__()
        self.worker = None

    def start_merge(self, destination, sources, simulate=False, include_hidden=False):
        """Start a merge operation.

        Args:
            destination: Path to the destination folder
            sources: List of source folder paths
            simulate: Whether to run in simulation mode
            include_hidden: Whether to include hidden files in the merge
        """
        # Create and configure the worker
        self.worker = MergeWorker(destination, sources, simulate, include_hidden)

        # Connect signals
        self.worker.progress_updated.connect(self.progress_updated)
        self.worker.operation_started.connect(self.operation_started)
        self.worker.operation_completed.connect(self.operation_completed)
        self.worker.operation_failed.connect(self.operation_failed)

        # Start the worker thread
        self.worker.start()

    def cancel_merge(self):
        """Cancel the current merge operation."""
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.worker.wait()  # Wait for the thread to finish

    def is_merge_running(self):
        """Check if a merge operation is currently running."""
        return self.worker is not None and self.worker.isRunning()
