"""
Main window view for the Py-Fusion application.

This module defines the main application window and its UI components.
"""

import os
import qtawesome as qta
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QFileDialog, QTabWidget, QSplitter, QProgressBar,
    QStatusBar, QToolBar, QMenu, QMenuBar, QMessageBox, QDialog,
    QDialogButtonBox, QCheckBox, QComboBox, QGroupBox, QRadioButton,
    QSpinBox, QLineEdit, QTextEdit, QScrollArea, QSizePolicy, QFrame,
    QToolButton
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QSettings, QTimer
from PyQt6.QtGui import QIcon, QFont, QPixmap
from py_fusion_gui.utils.temp_folder_manager import TempFolderManager
from py_fusion_gui.views.cached_folders_dialog import CachedFoldersDialog

class MainWindow(QMainWindow):
    """Main application window."""

    # Signals
    source_folders_changed = pyqtSignal(list)
    destination_folder_changed = pyqtSignal(str)
    analyze_requested = pyqtSignal()
    merge_requested = pyqtSignal(bool)  # bool: simulate
    cancel_requested = pyqtSignal()

    def __init__(self):
        """Initialize the main window."""
        super().__init__()

        # Set window properties
        self.setWindowTitle("Py-Fusion")
        self.setMinimumSize(900, 600)

        # Initialize UI components
        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface."""
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Create toolbar
        self._create_toolbar()

        # Create menu bar
        self._create_menu()

        # Create main content area
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(content_splitter)

        # Left panel: Folder selection
        left_panel = self._create_folder_panel()
        content_splitter.addWidget(left_panel)

        # Right panel: Results and preview
        right_panel = self._create_results_panel()
        content_splitter.addWidget(right_panel)

        # Set initial splitter sizes (40% left, 60% right)
        content_splitter.setSizes([400, 600])

        # Bottom panel: Progress and status
        bottom_panel = self._create_bottom_panel()
        main_layout.addWidget(bottom_panel)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def _create_toolbar(self):
        """Create the application toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        # Analyze action
        analyze_action = QAction(
            qta.icon('fa5s.search', color='#2196F3'),
            "Analyze", self
        )
        analyze_action.triggered.connect(self._on_analyze_clicked)
        toolbar.addAction(analyze_action)

        # Merge action
        merge_action = QAction(
            qta.icon('fa5s.play', color='#4CAF50'),
            "Merge", self
        )
        merge_action.triggered.connect(lambda: self._on_merge_clicked(False))
        toolbar.addAction(merge_action)

        # Simulate action
        simulate_action = QAction(
            qta.icon('fa5s.flask', color='#FF9800'),
            "Simulate", self
        )
        simulate_action.triggered.connect(lambda: self._on_merge_clicked(True))
        toolbar.addAction(simulate_action)

        # Separator
        toolbar.addSeparator()

        # Cancel action
        self.cancel_action = QAction(
            qta.icon('fa5s.stop', color='#F44336'),
            "Cancel", self
        )
        self.cancel_action.triggered.connect(self._on_cancel_clicked)
        self.cancel_action.setEnabled(False)
        toolbar.addAction(self.cancel_action)

        self.addToolBar(toolbar)
        self.toolbar = toolbar

    def _create_menu(self):
        """Create the application menu."""
        menu_bar = QMenuBar()

        # File menu
        file_menu = QMenu("&File", self)

        # Add source folder action
        add_source_action = QAction(
            qta.icon('fa5s.folder-plus', color='#2196F3'),
            "Add Source Folder", self
        )
        add_source_action.triggered.connect(self._on_add_source_clicked)
        file_menu.addAction(add_source_action)

        # Set destination folder action
        set_dest_action = QAction(
            qta.icon('fa5s.folder', color='#4CAF50'),
            "Set Destination Folder", self
        )
        set_dest_action.triggered.connect(self._on_set_destination_clicked)
        file_menu.addAction(set_dest_action)

        file_menu.addSeparator()

        # Exit action
        exit_action = QAction(
            qta.icon('fa5s.sign-out-alt', color='#F44336'),
            "Exit", self
        )
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = QMenu("&Edit", self)

        # Clear source folders action
        clear_sources_action = QAction(
            qta.icon('fa5s.trash-alt', color='#F44336'),
            "Clear Source Folders", self
        )
        clear_sources_action.triggered.connect(self._on_clear_sources_clicked)
        edit_menu.addAction(clear_sources_action)

        # Clear destination folder action
        clear_dest_action = QAction(
            qta.icon('fa5s.trash-alt', color='#F44336'),
            "Clear Destination Folder", self
        )
        clear_dest_action.triggered.connect(self._on_clear_destination_clicked)
        edit_menu.addAction(clear_dest_action)

        # Manage cached folders action
        cached_folders_action = QAction(
            qta.icon('fa5s.folder-open', color='#2196F3'),
            "Manage Cached Empty Folders", self
        )
        cached_folders_action.triggered.connect(self._on_manage_cached_folders_clicked)
        edit_menu.addAction(cached_folders_action)

        edit_menu.addSeparator()

        # Preferences action
        preferences_action = QAction(
            qta.icon('fa5s.cog', color='#9E9E9E'),
            "Preferences", self
        )
        preferences_action.triggered.connect(self._on_preferences_clicked)
        edit_menu.addAction(preferences_action)

        # Help menu
        help_menu = QMenu("&Help", self)

        # About action
        about_action = QAction(
            qta.icon('fa5s.info-circle', color='#2196F3'),
            "About Py-Fusion", self
        )
        about_action.triggered.connect(self._on_about_clicked)
        help_menu.addAction(about_action)

        # Add menus to menu bar
        menu_bar.addMenu(file_menu)
        menu_bar.addMenu(edit_menu)
        menu_bar.addMenu(help_menu)

        self.setMenuBar(menu_bar)

    def _create_folder_panel(self):
        """Create the folder selection panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Source folders section
        source_group = QGroupBox("Source Folders")
        source_layout = QVBoxLayout(source_group)

        # Source list
        self.source_list = QListWidget()
        self.source_list.setAlternatingRowColors(True)
        self.source_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        source_layout.addWidget(self.source_list)

        # Source buttons
        source_buttons_layout = QHBoxLayout()

        add_source_btn = QPushButton(qta.icon('fa5s.folder-plus'), "Add")
        add_source_btn.clicked.connect(self._on_add_source_clicked)
        source_buttons_layout.addWidget(add_source_btn)

        remove_source_btn = QPushButton(qta.icon('fa5s.trash-alt'), "Remove")
        remove_source_btn.clicked.connect(self._on_remove_source_clicked)
        source_buttons_layout.addWidget(remove_source_btn)

        clear_sources_btn = QPushButton(qta.icon('fa5s.times'), "Clear All")
        clear_sources_btn.clicked.connect(self._on_clear_sources_clicked)
        source_buttons_layout.addWidget(clear_sources_btn)

        source_layout.addLayout(source_buttons_layout)

        # Destination folder section
        dest_group = QGroupBox("Destination Folder")
        dest_layout = QVBoxLayout(dest_group)

        # Destination path display
        dest_layout_h = QHBoxLayout()
        self.dest_path_label = QLabel("No folder selected")
        self.dest_path_label.setWordWrap(True)
        self.dest_path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        dest_layout_h.addWidget(self.dest_path_label)

        # Browse button
        browse_dest_btn = QPushButton(qta.icon('fa5s.folder-open'), "Browse")
        browse_dest_btn.clicked.connect(self._on_set_destination_clicked)
        browse_dest_btn.setMaximumWidth(100)
        dest_layout_h.addWidget(browse_dest_btn)

        dest_layout.addLayout(dest_layout_h)

        # Add sections to panel
        layout.addWidget(source_group, 7)  # 70% of space
        layout.addWidget(dest_group, 3)    # 30% of space

        return panel

    def _create_results_panel(self):
        """Create the results and preview panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        # Tab widget for different views
        self.results_tabs = QTabWidget()

        # Summary tab
        summary_tab = QWidget()
        summary_layout = QVBoxLayout(summary_tab)

        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        summary_layout.addWidget(self.summary_text)

        # Details tab
        details_tab = QWidget()
        details_layout = QVBoxLayout(details_tab)

        self.details_list = QListWidget()
        self.details_list.setAlternatingRowColors(True)
        details_layout.addWidget(self.details_list)

        # Add tabs
        self.results_tabs.addTab(summary_tab, "Summary")
        self.results_tabs.addTab(details_tab, "Details")

        layout.addWidget(self.results_tabs)

        return panel

    def _create_bottom_panel(self):
        """Create the bottom panel with progress bar and buttons."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Action buttons
        buttons_layout = QHBoxLayout()

        self.analyze_btn = QPushButton(qta.icon('fa5s.search'), "Analyze")
        self.analyze_btn.clicked.connect(self._on_analyze_clicked)
        buttons_layout.addWidget(self.analyze_btn)

        self.merge_btn = QPushButton(qta.icon('fa5s.play'), "Merge")
        self.merge_btn.clicked.connect(lambda: self._on_merge_clicked(False))
        buttons_layout.addWidget(self.merge_btn)

        self.simulate_btn = QPushButton(qta.icon('fa5s.flask'), "Simulate")
        self.simulate_btn.clicked.connect(lambda: self._on_merge_clicked(True))
        buttons_layout.addWidget(self.simulate_btn)

        buttons_layout.addStretch()

        self.cancel_btn = QPushButton(qta.icon('fa5s.stop'), "Cancel")
        self.cancel_btn.clicked.connect(self._on_cancel_clicked)
        self.cancel_btn.setEnabled(False)
        buttons_layout.addWidget(self.cancel_btn)

        layout.addLayout(buttons_layout)

        return panel

    # Event handlers
    def _on_add_source_clicked(self):
        """Handle add source folder button click."""
        folder = QFileDialog.getExistingDirectory(
            self, "Select Source Folder", os.path.expanduser("~")
        )

        if folder:
            # Check if folder is already in the list
            items = [self.source_list.item(i).text() for i in range(self.source_list.count())]
            if folder not in items:
                self.source_list.addItem(folder)
                self._update_source_folders()

    def _on_remove_source_clicked(self):
        """Handle remove source folder button click."""
        selected_items = self.source_list.selectedItems()
        if not selected_items:
            return

        for item in selected_items:
            self.source_list.takeItem(self.source_list.row(item))

        self._update_source_folders()

    def _on_clear_sources_clicked(self):
        """Handle clear all source folders button click."""
        self.source_list.clear()
        self._update_source_folders()

    def _on_set_destination_clicked(self):
        """Handle set destination folder button click."""
        folder = QFileDialog.getExistingDirectory(
            self, "Select Destination Folder", os.path.expanduser("~")
        )

        if folder:
            self.dest_path_label.setText(folder)
            self.destination_folder_changed.emit(folder)

    def _on_clear_destination_clicked(self):
        """Handle clear destination folder button click."""
        self.dest_path_label.setText("No folder selected")
        self.destination_folder_changed.emit("")

    def _on_analyze_clicked(self):
        """Handle analyze button click."""
        if not self._validate_folders():
            return

        self.analyze_requested.emit()

    def _on_merge_clicked(self, simulate):
        """Handle merge or simulate button click."""
        if not self._validate_folders():
            return

        # Confirm before proceeding
        if not simulate:
            reply = QMessageBox.question(
                self, "Confirm Merge",
                "Are you sure you want to merge the folders? This operation cannot be undone.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.No:
                return

        self.merge_requested.emit(simulate)

    def _on_cancel_clicked(self):
        """Handle cancel button click."""
        reply = QMessageBox.question(
            self, "Confirm Cancel",
            "Are you sure you want to cancel the current operation?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.cancel_requested.emit()

    def _on_preferences_clicked(self):
        """Handle preferences button click."""
        # This will be implemented in a separate preferences dialog
        pass

    def _on_manage_cached_folders_clicked(self):
        """Handle manage cached folders button click."""
        dialog = CachedFoldersDialog(self)
        dialog.exec()

    def _on_about_clicked(self):
        """Handle about button click."""
        QMessageBox.about(
            self,
            "About Py-Fusion",
            "<h1>Py-Fusion</h1>"
            "<p>Version 1.0.0</p>"
            "<p>A modern tool for merging multiple folders intelligently.</p>"
            "<p>Copyright © 2023</p>"
        )

    def _update_source_folders(self):
        """Update the list of source folders and emit signal."""
        folders = [self.source_list.item(i).text() for i in range(self.source_list.count())]
        self.source_folders_changed.emit(folders)

    def _validate_folders(self):
        """Validate that source and destination folders are selected."""
        # Check if source folders are selected
        if self.source_list.count() == 0:
            QMessageBox.warning(
                self,
                "No Source Folders",
                "Please select at least one source folder."
            )
            return False

        # Check if destination folder is selected
        if self.dest_path_label.text() == "No folder selected":
            QMessageBox.warning(
                self,
                "No Destination Folder",
                "Please select a destination folder."
            )
            return False

        return True

    # Public methods
    def set_source_folders(self, folders):
        """Set the list of source folders.

        Args:
            folders: List of folder paths
        """
        self.source_list.clear()
        for folder in folders:
            self.source_list.addItem(folder)

    def set_destination_folder(self, folder):
        """Set the destination folder.

        Args:
            folder: Destination folder path
        """
        if folder:
            self.dest_path_label.setText(folder)
        else:
            self.dest_path_label.setText("No folder selected")

    def set_progress(self, value, maximum=100):
        """Set the progress bar value.

        Args:
            value: Current progress value
            maximum: Maximum progress value
        """
        self.progress_bar.setMaximum(maximum)
        self.progress_bar.setValue(value)

    def set_status_message(self, message):
        """Set the status bar message.

        Args:
            message: Status message to display
        """
        self.status_bar.showMessage(message)

    def set_summary_text(self, text):
        """Set the summary text.

        Args:
            text: HTML-formatted summary text
        """
        self.summary_text.setHtml(text)

    def clear_details_list(self):
        """Clear the details list."""
        self.details_list.clear()

    def add_detail_item(self, text, icon=None):
        """Add an item to the details list.

        Args:
            text: Item text
            icon: Optional icon for the item
        """
        item = QListWidgetItem(text)
        if icon:
            item.setIcon(icon)
        self.details_list.addItem(item)

    def set_operation_in_progress(self, in_progress):
        """Set the UI state based on whether an operation is in progress.

        Args:
            in_progress: Whether an operation is in progress
        """
        # Enable/disable buttons
        self.analyze_btn.setEnabled(not in_progress)
        self.merge_btn.setEnabled(not in_progress)
        self.simulate_btn.setEnabled(not in_progress)
        self.cancel_btn.setEnabled(in_progress)

        # Enable/disable toolbar actions
        for action in self.toolbar.actions():
            if action == self.cancel_action:
                action.setEnabled(in_progress)
            else:
                action.setEnabled(not in_progress)

        # Enable/disable folder selection
        self.source_list.setEnabled(not in_progress)

        # Show/hide progress bar
        if in_progress:
            self.progress_bar.setVisible(True)
        else:
            self.progress_bar.setVisible(True)  # Keep visible but reset
            self.progress_bar.setValue(0)
