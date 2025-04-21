"""
Settings model for the Py-Fusion application.

This module handles application settings, including theme preferences,
recent folders, and other user preferences.
"""

import os
import json
from PyQt6.QtCore import QSettings, QDir
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor

class SettingsModel:
    """Model for managing application settings."""

    def __init__(self):
        """Initialize the settings model."""
        self.settings = QSettings()
        self.load_settings()

    def load_settings(self):
        """Load settings from QSettings."""
        # Theme settings
        self.theme = self.settings.value("theme", "system")  # system, light, dark

        # Recent source folders
        self.recent_sources = self.settings.value("recent_sources", [])
        if not isinstance(self.recent_sources, list):
            self.recent_sources = []

        # Recent destination folders
        self.recent_destinations = self.settings.value("recent_destinations", [])
        if not isinstance(self.recent_destinations, list):
            self.recent_destinations = []

        # Default settings
        self.simulate_by_default = self.settings.value("simulate_by_default", False, type=bool)
        self.confirm_before_merge = self.settings.value("confirm_before_merge", True, type=bool)
        self.show_advanced_options = self.settings.value("show_advanced_options", False, type=bool)

    def save_settings(self):
        """Save current settings to QSettings."""
        self.settings.setValue("theme", self.theme)
        self.settings.setValue("recent_sources", self.recent_sources)
        self.settings.setValue("recent_destinations", self.recent_destinations)
        self.settings.setValue("simulate_by_default", self.simulate_by_default)
        self.settings.setValue("confirm_before_merge", self.confirm_before_merge)
        self.settings.setValue("show_advanced_options", self.show_advanced_options)
        self.settings.sync()

    def add_recent_source(self, path):
        """Add a path to recent sources."""
        if path in self.recent_sources:
            self.recent_sources.remove(path)
        self.recent_sources.insert(0, path)
        # Keep only the 10 most recent
        self.recent_sources = self.recent_sources[:10]
        self.save_settings()

    def add_recent_destination(self, path):
        """Add a path to recent destinations."""
        if path in self.recent_destinations:
            self.recent_destinations.remove(path)
        self.recent_destinations.insert(0, path)
        # Keep only the 10 most recent
        self.recent_destinations = self.recent_destinations[:10]
        self.save_settings()

    def clear_recent_sources(self):
        """Clear the list of recent source folders."""
        self.recent_sources = []
        self.save_settings()

    def clear_recent_destinations(self):
        """Clear the list of recent destination folders."""
        self.recent_destinations = []
        self.save_settings()

    def set_theme(self, theme):
        """Set the application theme."""
        self.theme = theme
        self.save_settings()

    def apply_theme(self, app):
        """Apply the current theme to the application."""
        # Load the appropriate stylesheet based on theme
        stylesheet_path = ""

        if self.theme == "dark" or (self.theme == "system" and self._is_system_dark()):
            stylesheet_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "resources", "styles", "dark_theme.qss"
            )
        else:
            stylesheet_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "resources", "styles", "light_theme.qss"
            )

        # Apply the stylesheet if it exists
        if os.path.exists(stylesheet_path):
            with open(stylesheet_path, "r") as f:
                app.setStyleSheet(f.read())

    def _is_system_dark(self):
        """Check if the system is using a dark theme."""
        try:
            from py_fusion_gui.utils.platform_utils import is_dark_mode_enabled
            return is_dark_mode_enabled()
        except ImportError:
            # If the platform utils module is not available, default to light theme
            return False
