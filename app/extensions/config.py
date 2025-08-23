"""
Configuration Extension
Handle application configuration and environment setup
"""

import os
from dotenv import load_dotenv
from pathlib import Path
from .database import DbConfig

def _load_env_layers():
    """Load .env, .env.local, and .env.<mode> plus system app.conf"""
    project_root = Path(__file__).parent.parent.parent
    
    # Base
    load_dotenv(project_root / '.env')
    
    # Local overrides (gitignored)
    load_dotenv(project_root / '.env.local')
    
    # Mode-specific
    mode = os.environ.get('FLASK_ENV') or os.environ.get('ENV') or 'development'
    load_dotenv(project_root / f'.env.{mode}')
    
    # Production system config (highest precedence)
    try:
        if (Path('/etc/postfix-manager') / 'app.conf').exists():
            load_dotenv('/etc/postfix-manager/app.conf', override=True)
    except Exception:
        pass

def init_config(app):
    """Set up core Flask app configuration from environment variables."""
    _load_env_layers()  # Load environment variables first
    
    # Determine the environment
    env = os.environ.get('FLASK_ENV') or os.environ.get('ENV') or 'development'
    
    # Load the appropriate configuration class
    if env == 'production':
        from app.config.production import ProductionConfig
        app.config.from_object(ProductionConfig)
    else:
        from app.config.development import DevelopmentConfig
        app.config.from_object(DevelopmentConfig)
    
    # Override with environment variables
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', app.config.get('SECRET_KEY'))
    
    # Database configuration using robust DbConfig class
    db_config = DbConfig()
    app.config['SQLALCHEMY_DATABASE_URI'] = db_config.get_db_uri()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', 'False').lower() == 'true'
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'echo': os.getenv('SQLALCHEMY_ECHO', 'false').lower() == 'true',
        'pool_size': int(os.getenv('DB_POOL_SIZE', '10')),
        'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', '20')),
        'pool_pre_ping': os.getenv('DB_POOL_PRE_PING', 'True').lower() == 'true',
        'pool_recycle': int(os.getenv('DB_POOL_RECYCLE', '3600')),
        'pool_timeout': int(os.getenv('DB_POOL_TIMEOUT', '30'))
    }
    
    # Store db_config for later use
    app.config['DB_CONFIG'] = db_config
    
    app.logger.info("Configuration initialized successfully")

def init_mail_config(app):
    """Initialize mail server configuration."""
    app.config['POSTFIX_CONFIG_DIR'] = os.getenv('POSTFIX_CONFIG_DIR', '/etc/postfix')
    app.config['DOVECOT_CONFIG_DIR'] = os.getenv('DOVECOT_CONFIG_DIR', '/etc/dovecot')
    app.config['SMTP_SERVER'] = os.getenv('SMTP_SERVER', 'localhost')
    app.config['SMTP_PORT'] = int(os.getenv('SMTP_PORT', 587))
    app.config['SMTP_USERNAME'] = os.getenv('SMTP_USERNAME')
    app.config['SMTP_PASSWORD'] = os.getenv('SMTP_PASSWORD')
    app.config['FROM_EMAIL'] = os.getenv('FROM_EMAIL', 'noreply@postfix-manager.com')
    app.config['MAILGUN_API_KEY'] = os.getenv('MAILGUN_API_KEY')
    app.config['MAILGUN_DOMAIN'] = os.getenv('MAILGUN_DOMAIN')
    app.config['MAILJET_API_KEY'] = os.getenv('MAILJET_API_KEY')
    app.config['MAILJET_API_SECRET'] = os.getenv('MAILJET_API_SECRET')
    app.config['SMTP_USE_TLS'] = os.getenv('SMTP_USE_TLS', 'False').lower() == 'true'
    app.config['SMTP_USE_SSL'] = os.getenv('SMTP_USE_SSL', 'False').lower() == 'true'
    
    app.logger.info("Mail configuration initialized")

def init_ldap_config(app):
    """Initialize LDAP configuration."""
    app.config['LDAP_SERVER_URI'] = os.getenv('LDAP_SERVER_URI', 'ldap://localhost:389')
    app.config['LDAP_BIND_DN'] = os.getenv('LDAP_BIND_DN', 'cn=admin,dc=example,dc=com')
    app.config['LDAP_BIND_PASSWORD'] = os.getenv('LDAP_BIND_PASSWORD', '')
    app.config['LDAP_BASE_DN'] = os.getenv('LDAP_BASE_DN', 'dc=example,dc=com')
    app.config['LDAP_CONFIG_DIR'] = os.getenv('LDAP_CONFIG_DIR', '/etc/ldap')
    
    app.logger.info("LDAP configuration initialized")

def init_csrf_config(app):
    """Initialize CSRF configuration."""
    app.config['WTF_CSRF_ENABLED'] = os.getenv('CSRF_ENABLED', 'True').lower() == 'true'
    app.config['WTF_CSRF_TIME_LIMIT'] = int(os.getenv('CSRF_TIME_LIMIT', 3600))
    app.config['WTF_CSRF_SSL_STRICT'] = os.getenv('CSRF_SSL_STRICT', 'False').lower() == 'true'
    
    app.logger.info("CSRF configuration initialized")
