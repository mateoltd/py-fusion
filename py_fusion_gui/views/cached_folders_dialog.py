"""
Dialog for managing cached empty folders.

This module provides a dialog for viewing, restoring, and saving cached empty folders.
"""

import os
import time
from datetime import datetime
import qtawesome as qta
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QFileDialog, QMessageBox,
    QDialogButtonBox, QSplitter, QWidget, QFrame
)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QIcon
from py_fusion_gui.utils.temp_folder_manager import TempFolderManager

class CachedFoldersDialog(QDialog):
    """Dialog for managing cached empty folders."""
    
    def __init__(self, parent=None):
        """Initialize the dialog.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.setWindowTitle("Cached Empty Folders")
        self.setMinimumSize(700, 400)
        
        # Get the temp folder manager
        self.temp_manager = TempFolderManager()
        
        # Initialize UI
        self._init_ui()
        
        # Connect signals
        self._connect_signals()
        
        # Load cached folders
        self._load_cached_folders()
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Info label
        info_label = QLabel(
            "These folders were empty after merging and have been cached. "
            "You can restore them to their original location or save them elsewhere."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Splitter for list and details
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Left panel: Folder list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        self.folder_list = QListWidget()
        self.folder_list.setAlternatingRowColors(True)
        left_layout.addWidget(self.folder_list)
        
        splitter.addWidget(left_panel)
        
        # Right panel: Folder details
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        self.details_frame = QFrame()
        self.details_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.details_frame.setFrameShadow(QFrame.Shadow.Raised)
        
        details_layout = QVBoxLayout(self.details_frame)
        
        self.folder_name_label = QLabel("Select a folder to view details")
        self.folder_name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        details_layout.addWidget(self.folder_name_label)
        
        self.original_path_label = QLabel("")
        details_layout.addWidget(self.original_path_label)
        
        self.cached_path_label = QLabel("")
        details_layout.addWidget(self.cached_path_label)
        
        self.timestamp_label = QLabel("")
        details_layout.addWidget(self.timestamp_label)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        
        self.restore_btn = QPushButton(qta.icon('fa5s.undo'), "Restore to Original")
        self.restore_btn.setEnabled(False)
        actions_layout.addWidget(self.restore_btn)
        
        self.save_as_btn = QPushButton(qta.icon('fa5s.save'), "Save As...")
        self.save_as_btn.setEnabled(False)
        actions_layout.addWidget(self.save_as_btn)
        
        self.delete_btn = QPushButton(qta.icon('fa5s.trash-alt'), "Delete")
        self.delete_btn.setEnabled(False)
        actions_layout.addWidget(self.delete_btn)
        
        details_layout.addLayout(actions_layout)
        details_layout.addStretch()
        
        right_layout.addWidget(self.details_frame)
        splitter.addWidget(right_panel)
        
        # Set initial splitter sizes (40% left, 60% right)
        splitter.setSizes([280, 420])
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _connect_signals(self):
        """Connect signals to slots."""
        self.folder_list.currentItemChanged.connect(self._on_folder_selected)
        self.restore_btn.clicked.connect(self._on_restore_clicked)
        self.save_as_btn.clicked.connect(self._on_save_as_clicked)
        self.delete_btn.clicked.connect(self._on_delete_clicked)
        self.temp_manager.cached_folders_changed.connect(self._on_cached_folders_changed)
    
    def _load_cached_folders(self):
        """Load the list of cached folders."""
        self.folder_list.clear()
        
        cached_folders = self.temp_manager.get_cached_folders_info()
        
        if not cached_folders:
            item = QListWidgetItem("No cached folders")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
            self.folder_list.addItem(item)
            return
        
        for folder_info in cached_folders:
            item = QListWidgetItem(folder_info["name"])
            item.setIcon(qta.icon('fa5s.folder'))
            item.setData(Qt.ItemDataRole.UserRole, folder_info)
            self.folder_list.addItem(item)
    
    @pyqtSlot(QListWidgetItem, QListWidgetItem)
    def _on_folder_selected(self, current, previous):
        """Handle folder selection change.
        
        Args:
            current: Current selected item
            previous: Previously selected item
        """
        if not current:
            self._clear_details()
            return
        
        folder_info = current.data(Qt.ItemDataRole.UserRole)
        if not folder_info:
            self._clear_details()
            return
        
        # Update details
        self.folder_name_label.setText(folder_info["name"])
        self.original_path_label.setText(f"Original path: {folder_info['original_path']}")
        self.cached_path_label.setText(f"Cached path: {folder_info['cached_path']}")
        
        # Format timestamp
        timestamp = folder_info["timestamp"]
        dt = datetime.fromtimestamp(timestamp)
        formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.setText(f"Cached on: {formatted_time}")
        
        # Enable buttons
        self.restore_btn.setEnabled(True)
        self.save_as_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)
    
    def _clear_details(self):
        """Clear the details panel."""
        self.folder_name_label.setText("Select a folder to view details")
        self.original_path_label.setText("")
        self.cached_path_label.setText("")
        self.timestamp_label.setText("")
        
        # Disable buttons
        self.restore_btn.setEnabled(False)
        self.save_as_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
    
    @pyqtSlot()
    def _on_restore_clicked(self):
        """Handle restore button click."""
        current_item = self.folder_list.currentItem()
        if not current_item:
            return
        
        folder_info = current_item.data(Qt.ItemDataRole.UserRole)
        if not folder_info:
            return
        
        # Confirm restore
        reply = QMessageBox.question(
            self,
            "Confirm Restore",
            f"Are you sure you want to restore the folder '{folder_info['name']}' to its original location?\n\n"
            f"Original path: {folder_info['original_path']}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Restore the folder
        success = self.temp_manager.restore_cached_folder(folder_info["cached_path"])
        
        if success:
            QMessageBox.information(
                self,
                "Folder Restored",
                f"The folder '{folder_info['name']}' has been restored to its original location."
            )
        else:
            QMessageBox.warning(
                self,
                "Restore Failed",
                f"Failed to restore the folder '{folder_info['name']}' to its original location.\n\n"
                "The original location may no longer be accessible or may contain files."
            )
    
    @pyqtSlot()
    def _on_save_as_clicked(self):
        """Handle save as button click."""
        current_item = self.folder_list.currentItem()
        if not current_item:
            return
        
        folder_info = current_item.data(Qt.ItemDataRole.UserRole)
        if not folder_info:
            return
        
        # Get save location
        save_path = QFileDialog.getExistingDirectory(
            self,
            "Select Save Location",
            os.path.expanduser("~")
        )
        
        if not save_path:
            return
        
        # Create full path including folder name
        full_save_path = os.path.join(save_path, folder_info["name"])
        
        # Check if path already exists
        if os.path.exists(full_save_path):
            reply = QMessageBox.question(
                self,
                "Path Exists",
                f"The path '{full_save_path}' already exists. Overwrite?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        # Save the folder
        success = self.temp_manager.save_cached_folder(folder_info["cached_path"], full_save_path)
        
        if success:
            QMessageBox.information(
                self,
                "Folder Saved",
                f"The folder '{folder_info['name']}' has been saved to '{full_save_path}'."
            )
        else:
            QMessageBox.warning(
                self,
                "Save Failed",
                f"Failed to save the folder '{folder_info['name']}' to '{full_save_path}'."
            )
    
    @pyqtSlot()
    def _on_delete_clicked(self):
        """Handle delete button click."""
        current_item = self.folder_list.currentItem()
        if not current_item:
            return
        
        folder_info = current_item.data(Qt.ItemDataRole.UserRole)
        if not folder_info:
            return
        
        # Confirm delete
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete the cached folder '{folder_info['name']}'?\n\n"
            "This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Delete the folder
        success = self.temp_manager.delete_cached_folder(folder_info["cached_path"])
        
        if success:
            QMessageBox.information(
                self,
                "Folder Deleted",
                f"The cached folder '{folder_info['name']}' has been deleted."
            )
        else:
            QMessageBox.warning(
                self,
                "Delete Failed",
                f"Failed to delete the cached folder '{folder_info['name']}'."
            )
    
    @pyqtSlot(list)
    def _on_cached_folders_changed(self, folders_info):
        """Handle cached folders changed signal.
        
        Args:
            folders_info: List of cached folder information
        """
        self._load_cached_folders()
