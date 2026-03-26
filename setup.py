from setuptools import setup, find_packages

setup(
    name="devhive",
    version="0.1.12",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "devhive_mcp=devhive.server:main",
            "devhive=devhive.cli:main",
        ],
    },
    install_requires=[
        "mcp",
    ],
)
