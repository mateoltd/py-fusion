"""
Dialog for managing backup files.

This module provides a dialog for viewing and restoring backup files.
"""

import os
import time
from datetime import datetime
import qtawesome as qta
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QMessageBox, QSplitter,
    QWidget, QFrame, QCheckBox, QDialogButtonBox
)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QIcon
from py_fusion_gui.utils.backup_manager import BackupManager

class BackupDialog(QDialog):
    """Dialog for managing backup files."""
    
    def __init__(self, parent=None):
        """Initialize the dialog.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.setWindowTitle("Backup Manager")
        self.setMinimumSize(800, 500)
        
        # Get the backup manager
        self.backup_manager = BackupManager()
        
        # Initialize UI
        self._init_ui()
        
        # Connect signals
        self._connect_signals()
        
        # Load backups
        self._load_backups()
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Info label
        info_label = QLabel(
            "These backups can be used to undo merge operations. "
            "Select a backup to view details and restore files to their original locations."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Create splitter for backup list and details
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Left panel: Backup list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        self.backup_list = QListWidget()
        self.backup_list.setAlternatingRowColors(True)
        left_layout.addWidget(self.backup_list)
        
        splitter.addWidget(left_panel)
        
        # Right panel: Backup details
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        self.details_frame = QFrame()
        self.details_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.details_frame.setFrameShadow(QFrame.Shadow.Raised)
        
        details_layout = QVBoxLayout(self.details_frame)
        
        self.backup_name_label = QLabel("Select a backup to view details")
        self.backup_name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        details_layout.addWidget(self.backup_name_label)
        
        self.timestamp_label = QLabel("")
        details_layout.addWidget(self.timestamp_label)
        
        self.destination_label = QLabel("")
        details_layout.addWidget(self.destination_label)
        
        self.sources_label = QLabel("")
        self.sources_label.setWordWrap(True)
        details_layout.addWidget(self.sources_label)
        
        # Simulation checkbox
        self.simulate_checkbox = QCheckBox("Simulate restoration (preview without making changes)")
        self.simulate_checkbox.setChecked(True)
        details_layout.addWidget(self.simulate_checkbox)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        
        self.restore_btn = QPushButton(qta.icon('fa5s.undo'), "Restore")
        self.restore_btn.setEnabled(False)
        actions_layout.addWidget(self.restore_btn)
        
        self.delete_btn = QPushButton(qta.icon('fa5s.trash-alt'), "Delete")
        self.delete_btn.setEnabled(False)
        actions_layout.addWidget(self.delete_btn)
        
        details_layout.addLayout(actions_layout)
        details_layout.addStretch()
        
        right_layout.addWidget(self.details_frame)
        splitter.addWidget(right_panel)
        
        # Set initial splitter sizes (40% left, 60% right)
        splitter.setSizes([300, 500])
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _connect_signals(self):
        """Connect signals."""
        self.backup_list.currentItemChanged.connect(self._on_backup_selected)
        self.restore_btn.clicked.connect(self._on_restore_clicked)
        self.delete_btn.clicked.connect(self._on_delete_clicked)
    
    def _load_backups(self):
        """Load the list of backups."""
        self.backup_list.clear()
        
        backups = self.backup_manager.get_backups()
        
        if not backups:
            item = QListWidgetItem("No backups available")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
            self.backup_list.addItem(item)
            return
        
        for backup in backups:
            item_text = f"{backup['date']} - {os.path.basename(backup['destination_folder'])}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, backup)
            self.backup_list.addItem(item)
    
    @pyqtSlot(QListWidgetItem, QListWidgetItem)
    def _on_backup_selected(self, current, previous):
        """Handle backup selection.
        
        Args:
            current: Currently selected item
            previous: Previously selected item
        """
        if not current:
            self.backup_name_label.setText("Select a backup to view details")
            self.timestamp_label.setText("")
            self.destination_label.setText("")
            self.sources_label.setText("")
            self.restore_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
            return
        
        backup_info = current.data(Qt.ItemDataRole.UserRole)
        if not backup_info:
            return
        
        self.backup_name_label.setText(f"Backup: {backup_info['filename']}")
        self.timestamp_label.setText(f"Date: {backup_info['date']}")
        self.destination_label.setText(f"Destination: {backup_info['destination_folder']}")
        
        sources_text = "Source folders:\n"
        for source in backup_info['source_folders']:
            sources_text += f"• {source}\n"
        self.sources_label.setText(sources_text)
        
        self.restore_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)
    
    @pyqtSlot()
    def _on_restore_clicked(self):
        """Handle restore button click."""
        current_item = self.backup_list.currentItem()
        if not current_item:
            return
        
        backup_info = current_item.data(Qt.ItemDataRole.UserRole)
        if not backup_info:
            return
        
        simulate = self.simulate_checkbox.isChecked()
        
        # Confirm restore
        if not simulate:
            reply = QMessageBox.question(
                self,
                "Confirm Restore",
                f"Are you sure you want to restore files from this backup?\n\n"
                f"This will move files from the destination folder back to their original locations.\n\n"
                f"Backup date: {backup_info['date']}\n"
                f"Destination: {backup_info['destination_folder']}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.No:
                return
        
        # Perform restore
        success, message = self.backup_manager.restore_backup(backup_info['path'], simulate)
        
        # Show result
        if simulate:
            QMessageBox.information(
                self,
                "Simulation Result",
                f"{message}\n\n"
                f"Uncheck 'Simulate restoration' to perform the actual restoration."
            )
        else:
            if success:
                QMessageBox.information(
                    self,
                    "Restore Completed",
                    f"{message}"
                )
                # Reload the backup list
                self._load_backups()
            else:
                QMessageBox.critical(
                    self,
                    "Restore Failed",
                    f"{message}"
                )
    
    @pyqtSlot()
    def _on_delete_clicked(self):
        """Handle delete button click."""
        current_item = self.backup_list.currentItem()
        if not current_item:
            return
        
        backup_info = current_item.data(Qt.ItemDataRole.UserRole)
        if not backup_info:
            return
        
        # Confirm delete
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete this backup?\n\n"
            f"Backup date: {backup_info['date']}\n"
            f"Destination: {backup_info['destination_folder']}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.No:
            return
        
        # Delete the backup
        if self.backup_manager.delete_backup(backup_info['path']):
            # Reload the backup list
            self._load_backups()
            
            # Clear details
            self.backup_name_label.setText("Select a backup to view details")
            self.timestamp_label.setText("")
            self.destination_label.setText("")
            self.sources_label.setText("")
            self.restore_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
            
            QMessageBox.information(
                self,
                "Backup Deleted",
                "The backup has been deleted successfully."
            )
        else:
            QMessageBox.critical(
                self,
                "Delete Failed",
                "Failed to delete the backup file."
            )
