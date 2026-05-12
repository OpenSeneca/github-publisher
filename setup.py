#!/usr/bin/env python3
"""
Setup script for github-publisher
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="github-publisher",
    version="1.0.0",
    author="OpenSeneca Squad",
    description="CLI tool for publishing OpenSeneca tools to PyPI and GitHub",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/OpenSeneca/github-publisher",
    py_modules=["main"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "build>=0.10.0",
        "twine>=4.0.0",
    ],
    entry_points={
        "console_scripts": [
            "github-publisher=main:main",
        ],
    },
)
