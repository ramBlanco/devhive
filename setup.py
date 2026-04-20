from setuptools import setup, find_packages

setup(
    name="devhive",
    version="0.1.21",
    packages=find_packages(),
    package_data={
        "devhive": ["skills/*.md", "skills/*/*.md"],
    },
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "devhive_mcp=devhive.server:main",
            "devhive=devhive.cli:main",
        ],
    },
    install_requires=[
        "mcp",
        "tiktoken>=0.5.0"
    ],
)
