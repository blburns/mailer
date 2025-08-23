"""
Production Configuration
Contains sensitive information - DO NOT commit to version control
"""

import os
from . import get_database_config, get_migration_config, get_sqlalchemy_config

class ProductionConfig:
    """Production configuration."""
    
    # Basic Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DEBUG = False
    TESTING = False
    
    # Database configuration
    db_config = get_database_config()
    SQLALCHEMY_DATABASE_URI = db_config['SQLALCHEMY_DATABASE_URI']
    SQLALCHEMY_ENGINE_OPTIONS = db_config['SQLALCHEMY_ENGINE_OPTIONS']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Migration configuration
    migration_config = get_migration_config()
    MIGRATION_DIR = migration_config['MIGRATION_DIR']
    DB_TYPE = migration_config['DB_TYPE']
    
    # Security
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    
    # Rate limiting
RATELIMIT_ENABLED = True
RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL', 'redis://localhost:6379/0')
RATELIMIT_DEFAULT = '100 per day;20 per hour;1 per second'
FLASK_LIMITER_ENABLED = os.environ.get('FLASK_LIMITER_ENABLED', 'true').lower() == 'true'
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = '/var/log/postfix-manager/app.log'
    
    # Mail server paths
    POSTFIX_CONFIG_DIR = os.environ.get('POSTFIX_CONFIG_DIR', '/etc/postfix')
    DOVECOT_CONFIG_DIR = os.environ.get('DOVECOT_CONFIG_DIR', '/etc/dovecot')
    
    # LDAP settings
    LDAP_SERVER_URI = os.environ.get('LDAP_SERVER_URI')
    LDAP_BIND_DN = os.environ.get('LDAP_BIND_DN')
    LDAP_BIND_PASSWORD = os.environ.get('LDAP_BIND_PASSWORD')
    LDAP_BASE_DN = os.environ.get('LDAP_BASE_DN')
    
    # Production-specific settings
    DEVELOPMENT_MODE = False
    AUTO_RELOAD = False
    SHOW_DEBUG_TOOLBAR = False
    
    # Monitoring
    ENABLE_MONITORING = True
    METRICS_ENDPOINT = '/metrics'
    
    # Backup settings
    BACKUP_ENABLED = True
    BACKUP_RETENTION_DAYS = 30
    BACKUP_PATH = '/var/backups/postfix-manager'
