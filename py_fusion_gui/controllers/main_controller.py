"""
Main controller for the Py-Fusion application.

This module connects the UI (view) with the application logic (models).
"""

import os
import qtawesome as qta
from PyQt6.QtCore import QObject, pyqtSlot, Qt
from PyQt6.QtWidgets import QMessageBox
from py_fusion_gui.models.merge_model import MergeModel
from py_fusion_gui.models.analysis_model import AnalysisModel, FileAction

class MainController(QObject):
    """Controller for the main application window."""

    def __init__(self, view, settings_model):
        """Initialize the main controller.

        Args:
            view: The main window view
            settings_model: The settings model
        """
        super().__init__()

        self.view = view
        self.settings_model = settings_model

        # Create models
        self.merge_model = MergeModel()
        self.analysis_model = AnalysisModel()

        # Current state
        self.source_folders = []
        self.destination_folder = ""
        self.operation_in_progress = False

        # Connect view signals
        self._connect_view_signals()

        # Connect model signals
        self._connect_model_signals()

        # Load initial settings
        self._load_settings()

    def _connect_view_signals(self):
        """Connect signals from the view."""
        # Folder selection signals
        self.view.source_folders_changed.connect(self._on_source_folders_changed)
        self.view.destination_folder_changed.connect(self._on_destination_folder_changed)

        # Operation signals
        self.view.analyze_requested.connect(self._on_analyze_requested)
        self.view.merge_requested.connect(self._on_merge_requested)
        self.view.cancel_requested.connect(self._on_cancel_requested)

    def _connect_model_signals(self):
        """Connect signals from the models."""
        # Analysis model signals
        self.analysis_model.progress_updated.connect(self._on_analysis_progress)
        self.analysis_model.analysis_started.connect(self._on_analysis_started)
        self.analysis_model.analysis_completed.connect(self._on_analysis_completed)
        self.analysis_model.analysis_failed.connect(self._on_analysis_failed)

        # Merge model signals
        self.merge_model.progress_updated.connect(self._on_merge_progress)
        self.merge_model.operation_started.connect(self._on_merge_started)
        self.merge_model.operation_completed.connect(self._on_merge_completed)
        self.merge_model.operation_failed.connect(self._on_merge_failed)

    def _load_settings(self):
        """Load settings and update the UI."""
        # Load recent source folders and validate they exist
        if self.settings_model.recent_sources:
            # Update the UI (this will filter out non-existent folders and emit the signal)
            self.view.set_source_folders(self.settings_model.recent_sources)

            # The source_folders_changed signal will be emitted by set_source_folders,
            # which will update self.source_folders and save the settings

        # Load recent destination folder and validate it exists
        if self.settings_model.recent_destinations:
            dest_folder = self.settings_model.recent_destinations[0]
            self.view.set_destination_folder(dest_folder)  # This will validate the folder

            # Update the controller's state based on what's shown in the UI
            if self.view.dest_path_label.text() != "No folder selected":
                self.destination_folder = self.view.dest_path_label.text()
            else:
                self.destination_folder = ""

                # Update settings model if needed
                if not os.path.exists(dest_folder):
                    if self.settings_model.recent_destinations:
                        self.settings_model.recent_destinations.pop(0)
                    self.settings_model.save_settings()

    # View signal handlers
    @pyqtSlot(list)
    def _on_source_folders_changed(self, folders):
        """Handle source folders changed signal.

        Args:
            folders: List of source folder paths
        """
        self.source_folders = folders

        # Save source folders to settings
        self.settings_model.recent_sources = folders.copy()  # Make a copy to avoid reference issues
        self.settings_model.save_settings()

        print(f"Source folders updated and saved: {folders}")

    @pyqtSlot(str)
    def _on_destination_folder_changed(self, folder):
        """Handle destination folder changed signal.

        Args:
            folder: Destination folder path
        """
        self.destination_folder = folder
        if folder:
            self.settings_model.add_recent_destination(folder)

    @pyqtSlot()
    def _on_analyze_requested(self):
        """Handle analyze requested signal."""
        if not self.source_folders or not self.destination_folder:
            return

        # Start analysis
        self.analysis_model.start_analysis(self.destination_folder, self.source_folders)

    @pyqtSlot(bool)
    def _on_merge_requested(self, simulate):
        """Handle merge requested signal.

        Args:
            simulate: Whether to run in simulation mode
        """
        if not self.source_folders or not self.destination_folder:
            return

        # Update recent folders
        # Save source folders directly to settings
        self.settings_model.recent_sources = self.source_folders.copy()  # Make a copy to avoid reference issues
        self.settings_model.save_settings()

        # Add destination folder
        self.settings_model.add_recent_destination(self.destination_folder)

        # Start merge
        self.merge_model.start_merge(self.destination_folder, self.source_folders, simulate)

    @pyqtSlot()
    def _on_cancel_requested(self):
        """Handle cancel requested signal."""
        if self.analysis_model.is_analysis_running():
            self.analysis_model.cancel_analysis()

        if self.merge_model.is_merge_running():
            self.merge_model.cancel_merge()

    # Analysis model signal handlers
    @pyqtSlot()
    def _on_analysis_started(self):
        """Handle analysis started signal."""
        self.operation_in_progress = True
        self.view.set_operation_in_progress(True)
        self.view.set_status_message("Analyzing folders...")
        self.view.clear_details_list()
        self.view.set_summary_text("<p>Analysis in progress...</p>")

    @pyqtSlot(int, int)
    def _on_analysis_progress(self, current, total):
        """Handle analysis progress signal.

        Args:
            current: Current progress value
            total: Maximum progress value
        """
        if total > 0:
            percentage = int((current / total) * 100)
            self.view.set_progress(percentage)
            self.view.set_status_message(f"Analyzing folders... {percentage}% ({current}/{total})")

    @pyqtSlot(list, dict)
    def _on_analysis_completed(self, actions, stats):
        """Handle analysis completed signal.

        Args:
            actions: List of FileAction objects
            stats: Dictionary with analysis statistics
        """
        self.operation_in_progress = False
        self.view.set_operation_in_progress(False)
        self.view.set_progress(100)
        self.view.set_status_message("Analysis completed")

        # Update summary
        empty_folders_info = ""
        if 'empty_source_folders' in stats and stats['empty_source_folders'] > 0:
            empty_folders_info = f"<li><b>{stats['empty_source_folders']}</b> empty source folders detected (will be cleaned up after merge)</li>"

        summary = f"""
        <h2>Analysis Results</h2>
        <p>The following actions will be performed:</p>
        <ul>
            <li><b>{stats['files_to_move']}</b> files will be moved</li>
            <li><b>{stats['files_to_skip']}</b> files will be skipped (identical)</li>
            <li><b>{stats['files_to_rename']}</b> files will be renamed</li>
            <li><b>{stats['directories_to_create']}</b> directories will be created</li>
            {empty_folders_info}
        </ul>
        <p>Total files: <b>{stats['total_files']}</b></p>
        """
        self.view.set_summary_text(summary)

        # Update details list
        self.view.clear_details_list()
        for action in actions:
            if action.action_type == FileAction.MOVE:
                icon = qta.icon('fa5s.arrow-right', color='#4CAF50')
                text = f"Move: {action.source_path} -> {action.dest_path}"
            elif action.action_type == FileAction.SKIP:
                icon = qta.icon('fa5s.ban', color='#9E9E9E')
                text = f"Skip: {action.source_path} ({action.reason})"
            elif action.action_type == FileAction.RENAME:
                icon = qta.icon('fa5s.edit', color='#FF9800')
                text = f"Rename: {action.source_path} -> {action.dest_path}"
            else:
                icon = qta.icon('fa5s.question', color='#F44336')
                text = str(action)

            self.view.add_detail_item(text, icon)

    @pyqtSlot(str)
    def _on_analysis_failed(self, error):
        """Handle analysis failed signal.

        Args:
            error: Error message
        """
        self.operation_in_progress = False
        self.view.set_operation_in_progress(False)
        self.view.set_status_message(f"Analysis failed: {error}")

        QMessageBox.critical(
            self.view,
            "Analysis Failed",
            f"The analysis operation failed:\n\n{error}"
        )

    # Merge model signal handlers
    @pyqtSlot(str)
    def _on_merge_started(self, message):
        """Handle merge started signal.

        Args:
            message: Start message
        """
        self.operation_in_progress = True
        self.view.set_operation_in_progress(True)
        self.view.set_status_message(message)
        self.view.clear_details_list()
        self.view.set_summary_text("<p>Merge operation in progress...</p>")

    @pyqtSlot(dict)
    def _on_merge_progress(self, stats):
        """Handle merge progress signal.

        Args:
            stats: Dictionary with current statistics
        """
        total = sum(stats.values())
        if total > 0:
            # We don't have a fixed total, so just update with current counts
            self.view.set_progress(total, total)
            self.view.set_status_message(
                f"Merging folders... "
                f"Moved: {stats['files_moved']}, "
                f"Skipped: {stats['files_skipped']}, "
                f"Renamed: {stats['files_renamed']}"
            )

    @pyqtSlot(dict)
    def _on_merge_completed(self, stats):
        """Handle merge completed signal.

        Args:
            stats: Dictionary with final statistics
        """
        self.operation_in_progress = False
        self.view.set_operation_in_progress(False)
        self.view.set_progress(100)
        self.view.set_status_message("Merge completed")

        # Update summary
        # Check for cached empty source folders
        from py_fusion_gui.utils.temp_folder_manager import TempFolderManager
        temp_manager = TempFolderManager()
        cached_folders = temp_manager.get_cached_folders_info()
        cached_folders_count = len(cached_folders)

        empty_folders_info = ""
        if cached_folders_count > 0:
            empty_folders_info = f"<li><b>{cached_folders_count}</b> empty source folders cached (available in Edit > Manage Cached Empty Folders)</li>"

        summary = f"""
        <h2>Merge Completed</h2>
        <p>The following actions were performed:</p>
        <ul>
            <li><b>{stats['files_moved']}</b> files moved</li>
            <li><b>{stats['files_skipped']}</b> files skipped (identical)</li>
            <li><b>{stats['files_renamed']}</b> files renamed</li>
            <li><b>{stats['directories_created']}</b> directories created</li>
            {empty_folders_info}
        </ul>
        <p>Errors: <b>{stats['errors']}</b></p>
        """
        self.view.set_summary_text(summary)

        # Show completion message
        empty_folders_msg = ""
        if cached_folders_count > 0:
            empty_folders_msg = f"\nEmpty source folders cached: {cached_folders_count} (available in Edit > Manage Cached Empty Folders)"

        QMessageBox.information(
            self.view,
            "Merge Completed",
            f"The merge operation has been completed successfully.\n\n"
            f"Files moved: {stats['files_moved']}\n"
            f"Files skipped: {stats['files_skipped']}\n"
            f"Files renamed: {stats['files_renamed']}\n"
            f"Directories created: {stats['directories_created']}\n"
            f"Errors: {stats['errors']}"
            f"{empty_folders_msg}"
        )

    @pyqtSlot(str)
    def _on_merge_failed(self, error):
        """Handle merge failed signal.

        Args:
            error: Error message
        """
        self.operation_in_progress = False
        self.view.set_operation_in_progress(False)
        self.view.set_status_message(f"Merge failed: {error}")

        QMessageBox.critical(
            self.view,
            "Merge Failed",
            f"The merge operation failed:\n\n{error}"
        )
