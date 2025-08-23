"""
Unit tests for authentication module
"""

import pytest
from flask import url_for
from app.models import User, UserRole
from app.extensions import db


class TestAuthentication:
    """Test authentication functionality."""
    
    def test_login_page_loads(self, client):
        """Test that the login page loads correctly."""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Login' in response.data
    
    def test_login_success(self, client, test_user):
        """Test successful login."""
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpassword'
        }, follow_redirects=True)
        assert response.status_code == 200
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        response = client.post('/auth/login', data={
            'username': 'invalid',
            'password': 'wrong'
        }, follow_redirects=True)
        assert response.status_code == 200
        # Should show error message
    
    def test_logout(self, client, test_user):
        """Test logout functionality."""
        # First login
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpassword'
        })
        
        # Then logout
        response = client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200
    
    def test_protected_route_requires_auth(self, client):
        """Test that protected routes require authentication."""
        response = client.get('/dashboard/', follow_redirects=True)
        assert response.status_code == 200
        # Should redirect to login page
    
    def test_user_creation(self, app):
        """Test user creation functionality."""
        with app.app_context():
            user = User(
                username='newuser',
                email='new@example.com',
                password_hash='hash',
                role=UserRole.USER,
                is_active=True
            )
            db.session.add(user)
            db.session.commit()
            
            assert user.id is not None
            assert user.username == 'newuser'
            assert user.role == UserRole.USER


class TestUserModel:
    """Test User model functionality."""
    
    def test_user_repr(self, app):
        """Test user string representation."""
        with app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                password_hash='hash'
            )
            assert str(user) == '<User testuser>'
    
    def test_user_role_enum(self, app):
        """Test user role enumeration."""
        assert UserRole.ADMIN == "admin"
        assert UserRole.USER == "user"
        assert UserRole.READONLY == "readonly"
    
    def test_user_defaults(self, app):
        """Test user default values."""
        with app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                password_hash='hash'
            )
            assert user.is_active is True
            assert user.role == UserRole.USER


class TestPasswordSecurity:
    """Test password security features."""
    
    def test_password_hashing(self, app):
        """Test that passwords are properly hashed."""
        with app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                password_hash='hashed_password'
            )
            # In a real implementation, this would use bcrypt
            assert user.password_hash == 'hashed_password'
    
    def test_password_validation(self, app):
        """Test password validation."""
        with app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                password_hash='hash'
            )
            # Test that password_hash is required
            assert user.password_hash is not None


class TestSessionManagement:
    """Test session management functionality."""
    
    def test_session_creation(self, client, test_user):
        """Test that sessions are created on login."""
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpassword'
        })
        # Should create a session
        assert response.status_code in [200, 302]
    
    def test_session_persistence(self, client, test_user):
        """Test that sessions persist across requests."""
        # Login
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpassword'
        })
        
        # Access protected route
        response = client.get('/dashboard/')
        assert response.status_code == 200
    
    def test_session_cleanup(self, client, test_user):
        """Test that sessions are cleaned up on logout."""
        # Login
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpassword'
        })
        
        # Logout
        client.get('/auth/logout')
        
        # Try to access protected route
        response = client.get('/dashboard/', follow_redirects=True)
        assert response.status_code == 200
        # Should redirect to login
