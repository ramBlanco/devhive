from setuptools import setup, find_packages

setup(
    name="devhive-mcp",
    version="0.1.6",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "devhive_mcp=mcp_server.server:main",
            "devhive=mcp_server.cli:main",
        ],
    },
    install_requires=[
        # "mcp",  # Assumed to be available in the environment
    ],
)
