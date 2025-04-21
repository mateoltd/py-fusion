#!/usr/bin/env python3
"""
Py-Fusion GUI - A modern graphical interface for the Py-Fusion folder merging tool.

This application provides a user-friendly interface for merging multiple folders,
handling duplicates intelligently, and preserving directory structures.
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings
from py_fusion_gui.controllers.main_controller import MainController
from py_fusion_gui.views.main_window import MainWindow
from py_fusion_gui.models.settings_model import SettingsModel

def main():
    """Main entry point for the application."""
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Py-Fusion")
    app.setOrganizationName("Py-Fusion")
    app.setOrganizationDomain("py-fusion.com")

    # Set up application-wide settings
    settings = SettingsModel()

    # Apply theme based on settings
    settings.apply_theme(app)

    # Create main window
    main_window = MainWindow()

    # Create and set up controller
    controller = MainController(main_window, settings)

    # Show the main window
    main_window.show()

    # Start the event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
