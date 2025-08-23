#!/usr/bin/env python3
"""
Postfix Manager Setup
Setup configuration for the Postfix Manager application
"""

import sys

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

# Fallback requirements if file doesn't exist
if not requirements:
    requirements = [
        "Flask>=2.0.0,<3.0.0",
        "Flask-Bcrypt>=1.0.1,<2.0.0",
        "Flask-Limiter>=3.0.0,<4.0.0",
        "Flask-Migrate>=3.0.0,<4.0.0",
        "Flask-SQLAlchemy>=2.5.0,<3.0.0",
        "Flask-WTF>=1.0.0,<2.0.0",
        "Flask-Login>=0.6.0,<1.0.0",
        "Jinja2>=3.0.0,<4.0.0",
        "SQLAlchemy>=1.4.0,<2.0.0",
        "python-dotenv>=1.0.0,<2.0.0",
        "python-json-logger>=2.0.0,<3.0.0",
        "waitress>=2.0.0,<3.0.0",
        "requests>=2.25.0,<3.0.0",
        "packaging>=20.0,<26.0",
        "ldap3>=2.9.0,<3.0.0",
        "psutil>=5.8.0,<6.0.0",
        "python-ldap>=3.3.0,<4.0.0",
        "cryptography>=3.4.0,<43.0.0",
    ]

# Version check
if sys.version_info < (3, 8):
    sys.exit("Postfix Manager requires Python 3.8 or higher")

setup(
    name="postfix-manager",
    version="0.1.0",
    author="DreamlikeLabs",
    author_email="contact-info@dreamlikelabs.com",
    description="A comprehensive web interface for managing Postfix, Dovecot, and OpenLDAP mail servers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dreamlikelabs/postfix-manager",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
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
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Networking :: Monitoring",
        "Topic :: System :: Systems Administration :: Authentication/Directory :: LDAP",
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
    package_data={
        "app": ["**/*.html", "**/*.css", "**/*.js", "**/*.py", "**/*.txt", "**/*.md"],
    },
    zip_safe=False,
    keywords="postfix dovecot ldap mail server management web interface flask",
    project_urls={
        "Bug Reports": "https://github.com/dreamlikelabs/postfix-manager/issues",
        "Source": "https://github.com/dreamlikelabs/postfix-manager",
        "Documentation": "https://github.com/dreamlikelabs/postfix-manager/wiki",
    },
)
