"""
Temporary folder manager for the Py-Fusion application.

This module handles the caching and cleanup of empty source folders.
"""

import os
import shutil
import tempfile
import atexit
import time
from typing import List, Dict, Set, Tuple
from PyQt6.QtCore import QObject, pyqtSignal

class TempFolderManager(QObject):
    """Manager for temporary folders and cleanup operations."""
    
    # Signals
    cached_folders_changed = pyqtSignal(list)  # List of cached folder info
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super(TempFolderManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the temporary folder manager."""
        QObject.__init__(self)
        self.temp_dir = tempfile.mkdtemp(prefix="py_fusion_")
        self.cached_folders_dir = os.path.join(self.temp_dir, "cached_folders")
        os.makedirs(self.cached_folders_dir, exist_ok=True)
        
        # Dictionary to track cached folders: {original_path: cached_path}
        self.cached_folders = {}
        
        # Dictionary to store metadata about cached folders
        # {cached_path: {"original_path": str, "timestamp": float, "name": str}}
        self.cached_folders_metadata = {}
        
        # Register cleanup function to run when the application exits
        atexit.register(self.cleanup)
    
    def is_empty_folder(self, folder_path: str) -> bool:
        """Check if a folder is empty (no files, may have empty subdirectories).
        
        Args:
            folder_path: Path to the folder to check
            
        Returns:
            bool: True if the folder is empty, False otherwise
        """
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            return False
            
        # Check if the folder contains any files
        for root, dirs, files in os.walk(folder_path):
            if files:
                return False
        return True
    
    def cache_empty_folder(self, folder_path: str) -> str:
        """Cache an empty folder by moving it to a temporary location.
        
        Args:
            folder_path: Path to the empty folder
            
        Returns:
            str: Path to the cached folder, or None if not cached
        """
        if not self.is_empty_folder(folder_path):
            return None
            
        # Get absolute path
        abs_path = os.path.abspath(folder_path)
        
        # Check if already cached
        if abs_path in self.cached_folders:
            return self.cached_folders[abs_path]
            
        # Create a unique name for the cached folder
        folder_name = os.path.basename(abs_path)
        timestamp = time.time()
        unique_name = f"{folder_name}_{timestamp:.0f}"
        cached_path = os.path.join(self.cached_folders_dir, unique_name)
        
        try:
            # Move the folder to the cache location
            shutil.move(abs_path, cached_path)
            
            # Store the mapping
            self.cached_folders[abs_path] = cached_path
            
            # Store metadata
            self.cached_folders_metadata[cached_path] = {
                "original_path": abs_path,
                "timestamp": timestamp,
                "name": folder_name
            }
            
            print(f"Cached empty folder: {abs_path} -> {cached_path}")
            
            # Emit signal that cached folders have changed
            self.cached_folders_changed.emit(self.get_cached_folders_info())
            
            return cached_path
        except Exception as e:
            print(f"Error caching folder {abs_path}: {str(e)}")
            return None
    
    def restore_cached_folder(self, cached_path: str) -> bool:
        """Restore a cached folder to its original location.
        
        Args:
            cached_path: Path to the cached folder
            
        Returns:
            bool: True if restored successfully, False otherwise
        """
        if cached_path not in self.cached_folders_metadata:
            return False
            
        original_path = self.cached_folders_metadata[cached_path]["original_path"]
        
        try:
            # Check if original path exists
            if os.path.exists(original_path):
                # If it's an empty directory, remove it first
                if os.path.isdir(original_path) and self.is_empty_folder(original_path):
                    shutil.rmtree(original_path)
                else:
                    # Original path exists and is not an empty dir, can't restore
                    return False
            
            # Create parent directories if needed
            os.makedirs(os.path.dirname(original_path), exist_ok=True)
            
            # Move the folder back to its original location
            shutil.move(cached_path, original_path)
            
            # Update tracking
            for orig, cached in list(self.cached_folders.items()):
                if cached == cached_path:
                    del self.cached_folders[orig]
                    break
            
            if cached_path in self.cached_folders_metadata:
                del self.cached_folders_metadata[cached_path]
            
            print(f"Restored folder: {cached_path} -> {original_path}")
            
            # Emit signal that cached folders have changed
            self.cached_folders_changed.emit(self.get_cached_folders_info())
            
            return True
        except Exception as e:
            print(f"Error restoring folder {cached_path}: {str(e)}")
            return False
    
    def get_cached_folders_info(self) -> List[Dict]:
        """Get information about all cached folders.
        
        Returns:
            List[Dict]: List of dictionaries with cached folder information
        """
        result = []
        for cached_path, metadata in self.cached_folders_metadata.items():
            result.append({
                "cached_path": cached_path,
                "original_path": metadata["original_path"],
                "name": metadata["name"],
                "timestamp": metadata["timestamp"]
            })
        return result
    
    def save_cached_folder(self, cached_path: str, new_path: str = None) -> bool:
        """Save a cached folder to a new location or restore to original location.
        
        Args:
            cached_path: Path to the cached folder
            new_path: New path to save the folder to, or None to restore to original
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        if cached_path not in self.cached_folders_metadata:
            return False
            
        if new_path is None:
            # Restore to original location
            return self.restore_cached_folder(cached_path)
        
        try:
            # Check if new path exists
            if os.path.exists(new_path):
                # If it's an empty directory, remove it first
                if os.path.isdir(new_path) and self.is_empty_folder(new_path):
                    shutil.rmtree(new_path)
                else:
                    # New path exists and is not an empty dir, can't save
                    return False
            
            # Create parent directories if needed
            os.makedirs(os.path.dirname(new_path), exist_ok=True)
            
            # Copy the folder to the new location
            shutil.copytree(cached_path, new_path)
            
            print(f"Saved folder: {cached_path} -> {new_path}")
            return True
        except Exception as e:
            print(f"Error saving folder {cached_path}: {str(e)}")
            return False
    
    def delete_cached_folder(self, cached_path: str) -> bool:
        """Delete a cached folder.
        
        Args:
            cached_path: Path to the cached folder
            
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        if cached_path not in self.cached_folders_metadata:
            return False
            
        try:
            # Remove the folder
            if os.path.exists(cached_path):
                shutil.rmtree(cached_path)
            
            # Update tracking
            original_path = self.cached_folders_metadata[cached_path]["original_path"]
            if original_path in self.cached_folders:
                del self.cached_folders[original_path]
            
            if cached_path in self.cached_folders_metadata:
                del self.cached_folders_metadata[cached_path]
            
            print(f"Deleted cached folder: {cached_path}")
            
            # Emit signal that cached folders have changed
            self.cached_folders_changed.emit(self.get_cached_folders_info())
            
            return True
        except Exception as e:
            print(f"Error deleting folder {cached_path}: {str(e)}")
            return False
    
    def cleanup(self) -> None:
        """Clean up all cached folders and temporary directory on application exit."""
        # Delete all cached folders
        for cached_path in list(self.cached_folders_metadata.keys()):
            try:
                if os.path.exists(cached_path):
                    shutil.rmtree(cached_path)
                    print(f"Cleaned up cached folder: {cached_path}")
            except Exception as e:
                print(f"Error cleaning up folder {cached_path}: {str(e)}")
        
        # Clear tracking dictionaries
        self.cached_folders.clear()
        self.cached_folders_metadata.clear()
        
        # Remove temporary directory
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                print(f"Cleaned up temporary directory: {self.temp_dir}")
        except Exception as e:
            print(f"Error cleaning up temporary directory: {str(e)}")
