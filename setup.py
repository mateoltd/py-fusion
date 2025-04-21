#!/usr/bin/env python3
"""
Setup script for Py-Fusion.

This script allows packaging Py-Fusion as a Python package.
"""

import os
from setuptools import setup, find_packages

# Read the content of README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="py-fusion",
    version="1.0.0",
    author="Mathéo",
    author_email="mateo@auraxgroup.com",
    description="A tool for merging multiple folders intelligently",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mateoltd/py-fusion",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "py_fusion_gui": ["resources/icons/*", "resources/styles/*"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "py-fusion=index:main",
        ],
        "gui_scripts": [
            "py-fusion-gui=py_fusion_gui.main:main",
        ],
    },
)
