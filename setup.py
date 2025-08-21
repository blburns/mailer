#!/usr/bin/env python3
"""
Postfix Manager Setup
Setup configuration for the Postfix Manager application
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text() if (this_directory / "README.md").exists() else ""

# Read requirements
requirements = []
if (this_directory / "requirements.txt").exists():
    with open(this_directory / "requirements.txt") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="postfix-manager",
    version="1.0.0",
    author="DreamlikeLabs",
    author_email="info@dreamlikelabs.com",
    description="A comprehensive web interface for managing Postfix, Dovecot, and OpenLDAP mail servers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dreamlikelabs/postfix-manager",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Communications :: Email :: Mail Transport Agents",
        "Topic :: System :: Systems Administration",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    python_requires=">=3.8,<3.13",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "production": [
            "gunicorn>=20.0",
            "supervisor>=4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "postfix-manager=run:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="postfix dovecot ldap mail server management web interface",
    project_urls={
        "Bug Reports": "https://github.com/dreamlikelabs/postfix-manager/issues",
        "Source": "https://github.com/dreamlikelabs/postfix-manager",
        "Documentation": "https://github.com/dreamlikelabs/postfix-manager/wiki",
    },
)
