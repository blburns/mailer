"""
Configuration Extensions
Handles application configuration and environment setup
"""

import os
from dotenv import load_dotenv


def _load_env_layers():
    """Load .env, .env.local, and .env.<mode> plus system app.conf"""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    
    # Base
    load_dotenv(os.path.join(project_root, '.env'))
    
    # Local overrides (gitignored)
    load_dotenv(os.path.join(project_root, '.env.local'))
    
    # Mode-specific
    mode = os.environ.get('FLASK_ENV') or os.environ.get('ENV') or 'development'
    load_dotenv(os.path.join(project_root, f'.env.{mode}'))
    
    # Production system config (highest precedence)
    try:
        if os.path.exists('/etc/postfix-manager/app.conf'):
            load_dotenv('/etc/postfix-manager/app.conf', override=True)
    except Exception:
        pass


def init_config(app):
    """Initialize application configuration."""
    # Load environment layers first
    _load_env_layers()
    
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Postfix Manager specific config
    app.config['POSTFIX_CONFIG_DIR'] = os.environ.get('POSTFIX_CONFIG_DIR') or '/etc/postfix'
    app.config['DOVECOT_CONFIG_DIR'] = os.environ.get('DOVECOT_CONFIG_DIR') or '/etc/dovecot'
    app.config['LDAP_CONFIG_DIR'] = os.environ.get('LDAP_CONFIG_DIR') or '/etc/ldap'
    app.config['VMAIL_HOME'] = os.environ.get('VMAIL_HOME') or '/home/vmail'


def init_mail_config(app):
    """Initialize mail configuration."""
    # Mail configuration will be handled by the mail management module
    pass
