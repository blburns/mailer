"""
Test suite for Postfix Manager application
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'app'))

# Set test environment
os.environ['FLASK_ENV'] = 'testing'
os.environ['TESTING'] = 'True'
