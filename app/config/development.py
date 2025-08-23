"""
Development Configuration
Safe to commit to version control
"""

import os
from pathlib import Path

class DevelopmentConfig:
    """Development configuration."""
    
    # Basic Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = True
    TESTING = False
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + str(Path(__file__).parent.parent.parent / 'instance' / 'postfix_manager.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Rate limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = 'memory://'
    RATELIMIT_DEFAULT = '200 per day;50 per hour;1 per second'
    
    # Logging
    LOG_LEVEL = 'DEBUG'
    LOG_FILE = 'logs/postfix-manager.log'
    
    # Mail server paths (safe defaults for development)
    POSTFIX_CONFIG_DIR = os.environ.get('POSTFIX_CONFIG_DIR', '/etc/postfix')
    DOVECOT_CONFIG_DIR = os.environ.get('DOVECOT_CONFIG_DIR', '/etc/dovecot')
    
    # LDAP settings (safe defaults)
    LDAP_SERVER_URI = os.environ.get('LDAP_SERVER_URI', 'ldap://localhost:389')
    LDAP_BIND_DN = os.environ.get('LDAP_BIND_DN', 'cn=admin,dc=example,dc=com')
    LDAP_BIND_PASSWORD = os.environ.get('LDAP_BIND_PASSWORD', '')
    LDAP_BASE_DN = os.environ.get('LDAP_BASE_DN', 'dc=example,dc=com')
    
    # Development-specific settings
    DEVELOPMENT_MODE = True
    AUTO_RELOAD = True
    SHOW_DEBUG_TOOLBAR = True
    
    # VM development settings (safe defaults)
    VM_HOST = os.environ.get('VM_HOST', '192.168.1.100')
    VM_USER = os.environ.get('VM_USER', 'ubuntu')
    VM_APP_DIR = os.environ.get('VM_APP_DIR', '/home/ubuntu/postfix-manager')
