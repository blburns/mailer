"""
Pytest configuration and fixtures for Postfix Manager tests
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'app'))

from app import create_app
from app.extensions import db
from app.models import User, UserRole


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app('testing')
    
    # Configure the app for testing
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key'
    })
    
    # Create the database and load test data
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
    
    # Clean up the temporary database file
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


@pytest.fixture
def test_user(app):
    """Create a test user for authentication tests."""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash='test_hash',
            role=UserRole.ADMIN,
            is_active=True
        )
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def auth_headers(client, test_user):
    """Get authenticated headers for API requests."""
    # Mock the login process
    with patch('app.modules.auth.routes.login_user'):
        response = client.post('/auth/login', json={
            'username': 'testuser',
            'password': 'testpassword'
        })
        return {'Authorization': f'Bearer test_token'}


@pytest.fixture
def mock_postfix_manager():
    """Mock PostfixManager for testing."""
    with patch('app.utils.mail_manager.PostfixManager') as mock:
        manager = MagicMock()
        manager.get_status.return_value = {
            'status': 'running',
            'service': 'active',
            'queue_count': 0
        }
        manager.get_queue_info.return_value = {
            'active': 0,
            'deferred': 0,
            'hold': 0,
            'incoming': 0,
            'maildrop': 0
        }
        mock.return_value = manager
        yield mock


@pytest.fixture
def mock_dovecot_manager():
    """Mock DovecotManager for testing."""
    with patch('app.utils.mail_manager.DovecotManager') as mock:
        manager = MagicMock()
        manager.get_status.return_value = {
            'status': 'running',
            'service': 'active',
            'connections': 0
        }
        mock.return_value = manager
        yield mock


@pytest.fixture
def mock_ldap_manager():
    """Mock LDAPManager for testing."""
    with patch('app.utils.ldap_manager.LDAPManager') as mock:
        manager = MagicMock()
        manager.get_status.return_value = {
            'status': 'connected',
            'server': 'localhost',
            'port': 389
        }
        manager.search.return_value = []
        manager.get_directory_tree.return_value = []
        mock.return_value = manager
        yield mock


class TestConfig:
    """Test configuration class."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'
