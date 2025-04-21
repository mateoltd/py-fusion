# Py-Fusion

A tool for merging multiple resource folders into one, intelligently handling duplicate files and preserving directory structure.

## Features

- Merges multiple folders into a destination folder
- Intelligent handling of duplicate files:
  - Skips identical files
  - Automatically renames files with the same name but different content
- Preserves directory structure
- Simulation mode to preview changes without making them
- Detailed operation statistics
- Support for glob patterns to select source folders
- Automatic caching of empty source folders after merging (with ability to restore them later)

## Requirements

- Python 3.9 or higher
- PyQt6 6.5.0 or higher (for the GUI version)
- QtAwesome 1.2.3 or higher (for the GUI version)
- PyObjC 9.0.1 or higher (optional, for native macOS file dialogs)

## Installation

### Pre-built Binaries

You can download pre-built binaries for macOS, Linux, and Windows from the [Releases](https://github.com/mateoltd/py-fusion/releases) page.

#### macOS
- CLI Version: Download and make executable with `chmod +x py-fusion`
- GUI Version: Download the DMG file, open it, and drag the application to your Applications folder

#### Linux
- CLI Version: Download the tarball, extract it, and make the executable file executable with `chmod +x py-fusion`
- GUI Version: Download the AppImage, make it executable with `chmod +x Py-Fusion-x86_64.AppImage`, and run it

#### Windows
- CLI Version: Download the ZIP file, extract it, and run the executable
- GUI Version: Download the installer and run it

### Using Conda (Recommended for Development)

1. Clone or download this repository:

```bash
git clone https://github.com/mateoltd/py-fusion.git
cd py-fusion
```

2. Create and activate the Conda environment:

```bash
conda env create -f environment.yml
conda activate py-fusion
```

### Using pip

1. Clone or download this repository:

```bash
git clone https://github.com/mateoltd/py-fusion.git
cd py-fusion
```

2. Install the required packages:

```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

```bash
python index.py
```

This will merge the default folders (RESOURCES 2, RESOURCES 3, etc.) into the "RESOURCES" folder.

### Graphical User Interface

To launch the graphical user interface:

```bash
python run_py_fusion_gui.py
```

The GUI provides a more user-friendly way to:
- Select source and destination folders (with multiple folder selection support)
- Analyze the merge operation before executing it
- View detailed statistics and progress
- Use dark or light theme
- Manage cached empty folders

#### Cached Empty Folders

When a source folder becomes empty after merging (all files moved to destination), it is automatically cached in a temporary location. This allows you to:

- Restore the folder to its original location if needed
- Save the folder to a different location
- Delete the folder permanently

To manage cached folders, go to Edit > Manage Cached Empty Folders in the menu.

#### Hidden Files

By default, hidden files (like .DS_Store on macOS or files with the hidden attribute on Windows) are skipped during the merge operation. You can change this behavior in two ways:

- In the GUI: Toggle the "Include Hidden Files" option in the Options menu
- In the CLI: Use the `--include-hidden` flag when running the command

### Command Line Options

```bash
python index.py --help
```

Shows all available options:

```
usage: index.py [-h] [--dest DEST] [--source SOURCE [SOURCE ...]]
                [--simulate] [--verbose] [--pattern PATTERN]
                [--include-hidden]

Merge multiple resource folders into a destination folder.

optional arguments:
  -h, --help            show this help message and exit
  --dest DEST, -d DEST  Destination folder where resources will be merged
                        (default: RESOURCES)
  --source SOURCE [SOURCE ...], -s SOURCE [SOURCE ...]
                        List of source folders to merge. If not specified,
                        the folders RESOURCES 2, RESOURCES 3, etc. will be used
  --simulate, -S        Simulation mode: shows what actions would be performed
                        without making actual changes
  --verbose, -v         Verbose mode: shows additional information during
                        the process
  --pattern PATTERN, -p PATTERN
                        Glob pattern to find source folders (e.g.: "RESOURCES*")
```

### Examples

#### Specify destination folder and source folders

```bash
python index.py --dest MyDestFolder --source Folder1 Folder2 Folder3
```

#### Use a pattern to select source folders

```bash
python index.py --pattern "RESOURCES_*"
```

#### Simulation mode (no actual changes)

```bash
python index.py --simulate
```

#### Verbose mode (shows more information)

```bash
python index.py --verbose
```

#### Include hidden files

```bash
python index.py --include-hidden
```

## Troubleshooting

### Checking Dependencies

You can check if all required dependencies are installed by running:

```bash
python check_dependencies.py
```

This will show you which dependencies are installed and which are missing.

### Common Issues

#### ImportError: cannot import name 'QAction' from 'PyQt6.QtWidgets'

This error occurs when using an older version of PyQt6. In PyQt6 6.5.0 and later, `QAction` has been moved from `QtWidgets` to `QtGui`. Make sure you have PyQt6 6.5.0 or higher installed:

```bash
pip install --upgrade PyQt6 PyQt6-Qt6 PyQt6-sip
```

Or with Conda:

```bash
conda env update -f environment.yml
```

#### ModuleNotFoundError: No module named 'qtawesome'

This error occurs when the QtAwesome package is not installed. Install it with:

```bash
pip install qtawesome
```

Or with Conda:

```bash
conda install -c conda-forge qtawesome
```

#### AttributeError: type object 'QListWidget' has no attribute 'Item'

This error occurs when clicking the Analyze button. It's due to a bug in the code where `QListWidget.Item` is used instead of `QListWidgetItem`. If you encounter this error, update your code by running:

```bash
python -c "import re; f=open('py_fusion_gui/views/main_window.py', 'r'); content=f.read(); f.close(); content=re.sub('QListWidget.Item', 'QListWidgetItem', content); f=open('py_fusion_gui/views/main_window.py', 'w'); f.write(content); f.close(); print('Fixed QListWidgetItem issue')"
```

Or manually edit the file `py_fusion_gui/views/main_window.py` and change `QListWidget.Item` to `QListWidgetItem` on line 523.

## Building from Source

### Building with PyInstaller

1. Install PyInstaller:

```bash
pip install pyinstaller
```

2. Build the CLI version:

```bash
pyinstaller --name py-fusion --onefile index.py
```

3. Build the GUI version:

```bash
pyinstaller --name py-fusion-gui --onefile --windowed run_py_fusion_gui.py
```

The built executables will be in the `dist` directory.

### Building with GitHub Actions

This repository includes GitHub Actions workflows that automatically build the application for macOS, Linux, and Windows. To use them:

1. Fork this repository
2. Go to the Actions tab in your forked repository
3. Enable workflows if they are disabled
4. Run the "Build All Platforms" workflow manually, or push a tag starting with "v" (e.g., "v1.0.0")

The built applications will be available as artifacts in the workflow run, and also as assets in the GitHub Release if you pushed a tag.

## Contributing

Contributions are welcome. Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
