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

## Requirements

- Python 3.6 or higher

## Installation

No special installation required, simply clone or download this repository:

```bash
git clone https://github.com/mateoltd/py-fusion.git
cd py-fusion
```

## Usage

### Basic Usage

```bash
python index.py
```

This will merge the default folders (RESOURCES 2, RESOURCES 3, etc.) into the "RESOURCES" folder.

### Available Options

```bash
python index.py --help
```

Shows all available options:

```
usage: index.py [-h] [--dest DEST] [--source SOURCE [SOURCE ...]]
                [--simulate] [--verbose] [--pattern PATTERN]

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

## Contributing

Contributions are welcome. Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
