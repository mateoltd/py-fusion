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
