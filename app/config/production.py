"""
Production Configuration
Safe to commit to version control
"""

import os
from pathlib import Path

class ProductionConfig:
    """Production configuration."""
    
    # Basic Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'change-this-in-production'
    DEBUG = False
    TESTING = False
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + str(Path(__file__).parent.parent.parent / 'instance' / 'postfix_manager.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    
    # Rate limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = 'redis://localhost:6379/0'
    RATELIMIT_DEFAULT = '1000 per day;100 per hour;10 per minute'
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = '/var/log/postfix-manager/app.log'
    
    # Mail server paths
    POSTFIX_CONFIG_DIR = os.environ.get('POSTFIX_CONFIG_DIR', '/etc/postfix')
    DOVECOT_CONFIG_DIR = os.environ.get('DOVECOT_CONFIG_DIR', '/etc/dovecot')
    
    # LDAP settings
    LDAP_SERVER_URI = os.environ.get('LDAP_SERVER_URI', 'ldap://localhost:389')
    LDAP_BIND_DN = os.environ.get('LDAP_BIND_DN', 'cn=admin,dc=example,dc=com')
    LDAP_BIND_PASSWORD = os.environ.get('LDAP_BIND_PASSWORD', '')
    LDAP_BASE_DN = os.environ.get('LDAP_BASE_DN', 'dc=example,dc=com')
    
    # Production-specific settings
    DEVELOPMENT_MODE = False
    AUTO_RELOAD = False
    SHOW_DEBUG_TOOLBAR = False
    
    # Performance
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }
    
    # Monitoring
    ENABLE_MONITORING = True
    METRICS_ENDPOINT = '/metrics'
    
    # Backup settings
    BACKUP_ENABLED = True
    BACKUP_RETENTION_DAYS = 30
    BACKUP_PATH = '/var/backups/postfix-manager'
