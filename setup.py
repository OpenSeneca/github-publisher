"""
GitHub Publisher v1.0.0
Setup configuration
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name='github-publisher',
    version='1.0.0',
    author='OpenSeneca',
    author_email='dev@openseneca.org',
    description='Automate building and publishing squad tools to GitHub and PyPI',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/OpenSeneca/github-publisher',
    py_modules=['github_publisher'],
    python_requires='>=3.8',
    install_requires=[
        'build>=0.10.0',
        'twine>=4.0.0',
    ],
    entry_points={
        'console_scripts': [
            'github-publisher=github_publisher:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
