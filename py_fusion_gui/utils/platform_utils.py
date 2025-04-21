"""
Platform-specific utilities for the Py-Fusion application.

This module provides functions to handle platform-specific behavior
and ensure cross-platform compatibility.
"""

import os
import sys
import platform

def get_platform():
    """Get the current platform.

    Returns:
        str: 'windows', 'macos', or 'linux'
    """
    system = platform.system().lower()
    if system == 'darwin':
        return 'macos'
    elif system == 'windows':
        return 'windows'
    else:
        return 'linux'

def is_dark_mode_enabled():
    """Check if the system is using dark mode.

    Returns:
        bool: True if dark mode is enabled, False otherwise
    """
    platform_name = get_platform()

    if platform_name == 'macos':
        try:
            # macOS dark mode detection
            import subprocess
            result = subprocess.run(
                ['defaults', 'read', '-g', 'AppleInterfaceStyle'],
                capture_output=True,
                text=True
            )
            return result.stdout.strip() == 'Dark'
        except Exception:
            return False
    elif platform_name == 'windows':
        try:
            # Windows dark mode detection
            import winreg
            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(registry, r'Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize')
            value, _ = winreg.QueryValueEx(key, 'AppsUseLightTheme')
            return value == 0
        except Exception:
            return False
    else:
        # Linux - harder to detect, would need to check specific desktop environments
        # For now, default to light mode
        return False

def get_home_directory():
    """Get the user's home directory.

    Returns:
        str: Path to the user's home directory
    """
    return os.path.expanduser('~')

def get_documents_directory():
    """Get the user's documents directory.

    Returns:
        str: Path to the user's documents directory
    """
    platform_name = get_platform()

    if platform_name == 'windows':
        # Windows
        import ctypes.wintypes
        CSIDL_PERSONAL = 5  # My Documents
        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(0, CSIDL_PERSONAL, 0, 0, buf)
        return buf.value
    elif platform_name == 'macos':
        # macOS
        return os.path.join(get_home_directory(), 'Documents')
    else:
        # Linux
        return os.path.join(get_home_directory(), 'Documents')

def fix_path_for_platform(path):
    """Fix a path for the current platform.

    Args:
        path: Path to fix

    Returns:
        str: Fixed path
    """
    # Replace forward slashes with backslashes on Windows
    if get_platform() == 'windows':
        return path.replace('/', '\\')
    return path

def is_hidden_file(path):
    """Check if a file or directory is hidden.

    This function checks if a file or directory is hidden based on the platform-specific
    criteria (dot prefix on Unix/macOS, hidden attribute on Windows).

    Args:
        path: Path to the file or directory

    Returns:
        bool: True if the file or directory is hidden, False otherwise
    """
    # Get the file/directory name without the path
    name = os.path.basename(path)

    # On Unix/macOS, hidden files start with a dot
    if get_platform() in ['macos', 'linux']:
        return name.startswith('.')

    # On Windows, use the hidden attribute
    elif get_platform() == 'windows':
        import stat
        try:
            return bool(os.stat(path).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)
        except (AttributeError, OSError):
            # Fall back to name-based check if attribute check fails
            return name.startswith('.')

    # Default fallback
    return name.startswith('.')

def get_multiple_directories(parent=None, title="Select Folders", directory=None):
    """Get multiple directories using the native file dialog.

    This function uses the native file dialog on macOS (NSOpenPanel) and falls back
    to the Qt dialog on other platforms.

    Args:
        parent: Parent widget
        title: Dialog title
        directory: Initial directory

    Returns:
        list: List of selected directory paths, or empty list if canceled
    """
    platform_name = get_platform()

    if platform_name == 'macos':
        try:
            # Try to use PyObjC to access the native macOS file dialog
            from AppKit import NSOpenPanel, NSApp
            from PyQt6.QtWidgets import QApplication

            # Create and configure the open panel
            panel = NSOpenPanel.openPanel()
            panel.setCanChooseDirectories_(True)
            panel.setCanChooseFiles_(False)
            panel.setAllowsMultipleSelection_(True)

            if title:
                panel.setTitle_(title)

            if directory:
                from Foundation import NSURL
                url = NSURL.fileURLWithPath_(directory)
                panel.setDirectoryURL_(url)

            # Run the panel
            if panel.runModal() == 1:  # NSModalResponseOK
                # Get the selected URLs and convert them to paths
                urls = panel.URLs()
                return [url.path() for url in urls]
            return []
        except ImportError:
            # PyObjC not available, fall back to Qt dialog
            print("PyObjC not available, falling back to Qt dialog")
            pass

    # For other platforms or if PyObjC failed, use the Qt dialog
    from PyQt6.QtWidgets import QFileDialog, QListView, QTreeView

    dialog = QFileDialog(parent)
    dialog.setFileMode(QFileDialog.FileMode.Directory)
    dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)  # Required for multiple selection
    dialog.setWindowTitle(title)

    if directory:
        dialog.setDirectory(directory)

    # Enable multiple selection
    listView = dialog.findChild(QListView, "listView")
    if listView:
        listView.setSelectionMode(QListView.SelectionMode.ExtendedSelection)
    treeView = dialog.findChild(QTreeView, "treeView")
    if treeView:
        treeView.setSelectionMode(QTreeView.SelectionMode.ExtendedSelection)

    # Show the dialog
    if dialog.exec():
        return dialog.selectedFiles()
    return []
