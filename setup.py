"""
GitHub Publisher for OpenSeneca Tools
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="github-publisher",
    version="1.0.0",
    author="OpenSeneca Squad",
    author_email="squad@openseneca.org",
    description="Package and publish OpenSeneca tools to PyPI and GitHub",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/OpenSeneca/github-publisher",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Version Control :: Git",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
    ],
    entry_points={
        "console_scripts": [
            "github-publisher=github_publisher:main",
        ],
    },
)
