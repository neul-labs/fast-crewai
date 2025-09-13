"""
Setup script for the CrewAI Rust integration package.

This script handles the build process for the Rust components
and ensures proper installation of the Python package.
"""

from setuptools import setup, find_packages
import os

# Read the README file for the long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

# Check if we're in a development environment with Rust source
def has_rust_source():
    lib_path = os.path.join(os.path.dirname(__file__), "..", "src", "lib.rs")
    return os.path.exists(lib_path)

# Determine which extras to include
extras_require = {
    "dev": [
        "maturin>=1.0,<2.0",
        "pytest>=6.0",
        "pytest-asyncio>=0.14.0",
    ],
}

# If we have Rust source, we can build the extension
if has_rust_source():
    # In a development environment with Rust source, we'll use maturin
    # The actual build is handled by maturin, not setuptools
    setup_requirements = ["maturin>=1.0,<2.0"]
else:
    # In a distribution environment, we expect the extension to be pre-built
    setup_requirements = []

setup(
    name="crewai-rust",
    version="0.1.0",
    author="CrewAI",
    author_email="info@crewai.com",
    description="High-performance Rust implementations for CrewAI components",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/crewAI/crewai",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Rust",
    ],
    python_requires=">=3.8",
    install_requires=[
        # Minimal requirements - the package is designed to work
        # with or without the Rust components
    ],
    extras_require=extras_require,
    setup_requires=setup_requirements,
    entry_points={
        "console_scripts": [
            "crewai-rust=crewai_rust.__main__:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)