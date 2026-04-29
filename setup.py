import os
from setuptools import setup, find_packages

# Read the README for the long_description in PyPI
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="devhive",
    version="0.1.30",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "devhive=devhive_cli.main:cli",
        ],
    },
    description="CLI to manage DevHive skills and autonomous AI agents for OpenCode.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="ramBlanco",
    url="https://github.com/ramBlanco/devhive",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
