"""
Backup manager for the Py-Fusion application.

This module handles the creation and restoration of backup files
that allow undoing merge operations.
"""

import os
import json
import time
import shutil
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import tempfile
from PyQt6.QtCore import QObject, pyqtSignal

class BackupManager(QObject):
    """Manager for creating and restoring backup files."""
    
    # Signals
    backup_created = pyqtSignal(str)  # Path to backup file
    backup_restored = pyqtSignal(str)  # Path to restored backup
    backup_failed = pyqtSignal(str)   # Error message
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super(BackupManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the backup manager."""
        QObject.__init__(self)
        self.backup_dir = os.path.join(tempfile.gettempdir(), "py_fusion_backups")
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Dictionary to track file operations for the current merge
        self.current_operations = []
        
        # Dictionary to store metadata about backups
        # {backup_path: {"timestamp": float, "source_folders": list, "destination_folder": str}}
        self.backup_metadata = {}
        
        print(f"Backup manager initialized. Backup directory: {self.backup_dir}")
    
    def start_backup(self, destination_folder: str, source_folders: List[str]) -> None:
        """Start tracking a new backup.
        
        Args:
            destination_folder: Path to the destination folder
            source_folders: List of source folder paths
        """
        self.current_operations = []
        self.current_destination = destination_folder
        self.current_sources = source_folders.copy()
        print(f"Started tracking backup for merge: {source_folders} -> {destination_folder}")
    
    def record_file_operation(self, operation_type: str, source_path: str, dest_path: str, 
                             success: bool = True, error: str = None) -> None:
        """Record a file operation for the current backup.
        
        Args:
            operation_type: Type of operation (move, rename, skip)
            source_path: Source file path
            dest_path: Destination file path
            success: Whether the operation was successful
            error: Error message if the operation failed
        """
        operation = {
            "type": operation_type,
            "source": source_path,
            "destination": dest_path,
            "success": success,
            "error": error,
            "timestamp": time.time()
        }
        self.current_operations.append(operation)
    
    def save_backup(self) -> Optional[str]:
        """Save the current backup to a file.
        
        Returns:
            str: Path to the backup file, or None if no operations were recorded
        """
        if not self.current_operations:
            print("No operations to backup")
            return None
        
        # Create a unique backup file name
        timestamp = time.time()
        date_str = datetime.fromtimestamp(timestamp).strftime("%Y%m%d_%H%M%S")
        backup_name = f"py_fusion_backup_{date_str}.json"
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        # Create the backup data
        backup_data = {
            "timestamp": timestamp,
            "destination_folder": self.current_destination,
            "source_folders": self.current_sources,
            "operations": self.current_operations
        }
        
        try:
            # Save the backup file
            with open(backup_path, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            # Store metadata
            self.backup_metadata[backup_path] = {
                "timestamp": timestamp,
                "destination_folder": self.current_destination,
                "source_folders": self.current_sources
            }
            
            print(f"Backup saved: {backup_path}")
            self.backup_created.emit(backup_path)
            return backup_path
        except Exception as e:
            print(f"Error saving backup: {str(e)}")
            self.backup_failed.emit(f"Failed to save backup: {str(e)}")
            return None
    
    def get_backups(self) -> List[Dict[str, Any]]:
        """Get a list of available backups.
        
        Returns:
            List[Dict]: List of backup information dictionaries
        """
        backups = []
        
        # Scan the backup directory for backup files
        if os.path.exists(self.backup_dir):
            for filename in os.listdir(self.backup_dir):
                if filename.startswith("py_fusion_backup_") and filename.endswith(".json"):
                    backup_path = os.path.join(self.backup_dir, filename)
                    
                    try:
                        # Load the backup file to get metadata
                        with open(backup_path, 'r') as f:
                            backup_data = json.load(f)
                        
                        # Extract metadata
                        timestamp = backup_data.get("timestamp", 0)
                        destination = backup_data.get("destination_folder", "Unknown")
                        sources = backup_data.get("source_folders", [])
                        
                        # Store in metadata cache
                        self.backup_metadata[backup_path] = {
                            "timestamp": timestamp,
                            "destination_folder": destination,
                            "source_folders": sources
                        }
                        
                        # Add to results
                        backups.append({
                            "path": backup_path,
                            "filename": filename,
                            "timestamp": timestamp,
                            "date": datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S"),
                            "destination_folder": destination,
                            "source_folders": sources
                        })
                    except Exception as e:
                        print(f"Error reading backup file {backup_path}: {str(e)}")
        
        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x["timestamp"], reverse=True)
        return backups
    
    def restore_backup(self, backup_path: str, simulate: bool = False) -> Tuple[bool, str]:
        """Restore a backup.
        
        Args:
            backup_path: Path to the backup file
            simulate: If True, only simulate the restoration without making changes
            
        Returns:
            Tuple[bool, str]: Success flag and message
        """
        if not os.path.exists(backup_path):
            message = f"Backup file not found: {backup_path}"
            print(message)
            self.backup_failed.emit(message)
            return False, message
        
        try:
            # Load the backup file
            with open(backup_path, 'r') as f:
                backup_data = json.load(f)
            
            # Extract operations
            operations = backup_data.get("operations", [])
            
            if not operations:
                message = "No operations found in backup file"
                print(message)
                self.backup_failed.emit(message)
                return False, message
            
            # Process operations in reverse order
            success_count = 0
            error_count = 0
            skipped_count = 0
            
            # First pass: check if all destination files still exist
            for op in reversed(operations):
                op_type = op.get("type")
                source = op.get("source")
                destination = op.get("destination")
                
                if op_type in ["move", "rename"]:
                    # For move/rename operations, check if the destination file exists
                    if not os.path.exists(destination):
                        error_count += 1
                        print(f"Warning: Destination file no longer exists: {destination}")
            
            if error_count > 0 and not simulate:
                message = f"Cannot restore backup: {error_count} destination files no longer exist"
                print(message)
                self.backup_failed.emit(message)
                return False, message
            
            # Second pass: perform the restoration
            for op in reversed(operations):
                op_type = op.get("type")
                source = op.get("source")
                destination = op.get("destination")
                
                if op_type == "move":
                    # Reverse a move operation: move the file back from destination to source
                    if os.path.exists(destination):
                        if not simulate:
                            # Create the source directory if it doesn't exist
                            os.makedirs(os.path.dirname(source), exist_ok=True)
                            
                            # Move the file back
                            shutil.move(destination, source)
                        
                        success_count += 1
                        print(f"{'[SIMULATION] ' if simulate else ''}Restored: {destination} -> {source}")
                    else:
                        error_count += 1
                        print(f"Error: Cannot restore {destination} (file not found)")
                
                elif op_type == "rename":
                    # Reverse a rename operation: rename the file back to its original name
                    if os.path.exists(destination):
                        if not simulate:
                            # Create the source directory if it doesn't exist
                            os.makedirs(os.path.dirname(source), exist_ok=True)
                            
                            # Rename the file back
                            shutil.move(destination, source)
                        
                        success_count += 1
                        print(f"{'[SIMULATION] ' if simulate else ''}Restored renamed file: {destination} -> {source}")
                    else:
                        error_count += 1
                        print(f"Error: Cannot restore renamed file {destination} (file not found)")
                
                elif op_type == "skip":
                    # Skip operations don't need to be reversed
                    skipped_count += 1
            
            # Generate result message
            if simulate:
                message = (f"Simulation completed: {success_count} operations would be restored, "
                          f"{error_count} errors would occur, {skipped_count} operations would be skipped")
            else:
                message = (f"Backup restored: {success_count} operations restored, "
                          f"{error_count} errors occurred, {skipped_count} operations skipped")
            
            print(message)
            
            if not simulate:
                self.backup_restored.emit(backup_path)
            
            return error_count == 0, message
            
        except Exception as e:
            message = f"Error restoring backup: {str(e)}"
            print(message)
            self.backup_failed.emit(message)
            return False, message
    
    def delete_backup(self, backup_path: str) -> bool:
        """Delete a backup file.
        
        Args:
            backup_path: Path to the backup file
            
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        if not os.path.exists(backup_path):
            print(f"Backup file not found: {backup_path}")
            return False
        
        try:
            os.remove(backup_path)
            
            # Remove from metadata cache
            if backup_path in self.backup_metadata:
                del self.backup_metadata[backup_path]
            
            print(f"Backup deleted: {backup_path}")
            return True
        except Exception as e:
            print(f"Error deleting backup: {str(e)}")
            return False
