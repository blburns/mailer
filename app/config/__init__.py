"""
Configuration Module
Contains all application configuration modules and utilities.
"""

import os
from pathlib import Path

def get_database_config():
    """Get database configuration based on environment variables."""
    db_type = os.environ.get('DB_TYPE', 'sqlite').lower()
    
    if db_type == 'mysql':
        return {
            'SQLALCHEMY_DATABASE_URI': os.environ.get('DATABASE_URL') or \
                f"mysql://{os.environ.get('DB_USER', 'root')}:{os.environ.get('DB_PASSWORD', '')}@{os.environ.get('DB_HOST', 'localhost')}:{os.environ.get('DB_PORT', '3306')}/{os.environ.get('DB_NAME', 'postfix_manager')}",
            'SQLALCHEMY_ENGINE_OPTIONS': {
                'pool_size': int(os.environ.get('DB_POOL_SIZE', '10')),
                'max_overflow': int(os.environ.get('DB_MAX_OVERFLOW', '20')),
                'pool_pre_ping': True,
                'pool_recycle': int(os.environ.get('DB_POOL_RECYCLE', '3600')),
                'pool_timeout': int(os.environ.get('DB_POOL_TIMEOUT', '30'))
            }
        }
    
    elif db_type == 'postgresql':
        return {
            'SQLALCHEMY_DATABASE_URI': os.environ.get('DATABASE_URL') or \
                f"postgresql://{os.environ.get('DB_USER', 'postgres')}:{os.environ.get('DB_PASSWORD', '')}@{os.environ.get('DB_HOST', 'localhost')}:{os.environ.get('DB_PORT', '5432')}/{os.environ.get('DB_NAME', 'postfix_manager')}",
            'SQLALCHEMY_ENGINE_OPTIONS': {
                'pool_size': int(os.environ.get('DB_POOL_SIZE', '10')),
                'max_overflow': int(os.environ.get('DB_MAX_OVERFLOW', '20')),
                'pool_pre_ping': True,
                'pool_recycle': int(os.environ.get('DB_POOL_RECYCLE', '3600')),
                'pool_timeout': int(os.environ.get('DB_POOL_TIMEOUT', '30'))
            }
        }
    
    else:  # sqlite (default)
        # Use a more reliable path that works on both local and VM
        if os.environ.get('FLASK_ENV') == 'production' or os.environ.get('ENV') == 'production':
            # Production/VM path
            db_path = '/opt/postfix-manager/instance/postfix_manager.db'
        else:
            # Development path
            db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'instance', 'postfix_manager.db')
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        return {
            'SQLALCHEMY_DATABASE_URI': os.environ.get('DATABASE_URL') or f'sqlite:///{db_path}',
            'SQLALCHEMY_ENGINE_OPTIONS': {
                'pool_size': 1,
                'max_overflow': 0,
                'pool_pre_ping': False
            }
        }

def get_migration_config():
    """Get migration configuration based on database type."""
    db_type = os.environ.get('DB_TYPE', 'sqlite').lower()
    return {
        'MIGRATION_DIR': f'migrations/{db_type}',
        'DB_TYPE': db_type
    }


def get_sqlalchemy_config():
    """Get SQLAlchemy-specific configuration."""
    return {
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SQLALCHEMY_ENGINE_OPTIONS': {
            'echo': os.environ.get('SQLALCHEMY_ECHO', 'false').lower() == 'true',
        }
    }
