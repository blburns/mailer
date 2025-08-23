"""
Database Configuration Module for Postfix Manager

Supports multiple database backends:
- SQLite (development/testing)
- MySQL/MariaDB (production)
- PostgreSQL (production)

Handles connection pooling, SSL, and database-specific optimizations.
"""

import os
import re
from typing import Dict, Any, Optional
from urllib.parse import urlparse, urlunparse


class DatabaseConfig:
    """Database configuration manager for multiple backends."""
    
    # Database type detection patterns
    DATABASE_PATTERNS = {
        'sqlite': r'^sqlite://',
        'mysql': r'^mysql://|^mariadb://',
        'postgresql': r'^postgresql://|^postgres://'
    }
    
    # Default connection pool settings
    DEFAULT_POOL_SETTINGS = {
        'sqlite': {
            'pool_size': 1,
            'max_overflow': 0,
            'pool_pre_ping': False,
            'pool_recycle': -1
        },
        'mysql': {
            'pool_size': 10,
            'max_overflow': 20,
            'pool_pre_ping': True,
            'pool_recycle': 3600,
            'pool_timeout': 30
        },
        'postgresql': {
            'pool_size': 10,
            'max_overflow': 20,
            'pool_pre_ping': True,
            'pool_recycle': 3600,
            'pool_timeout': 30
        }
    }
    
    @classmethod
    def detect_database_type(cls, database_url: str) -> str:
        """Detect database type from connection string."""
        for db_type, pattern in cls.DATABASE_PATTERNS.items():
            if re.match(pattern, database_url):
                return db_type
        return 'sqlite'  # Default fallback
    
    @classmethod
    def parse_database_url(cls, database_url: str) -> Dict[str, Any]:
        """Parse database URL and return connection parameters."""
        parsed = urlparse(database_url)
        
        config = {
            'scheme': parsed.scheme,
            'host': parsed.hostname,
            'port': parsed.port,
            'username': parsed.username,
            'password': parsed.password,
            'database': parsed.path.lstrip('/'),
            'query_params': dict(parsed.query.split('&')) if parsed.query else {}
        }
        
        # Handle SQLite special case
        if config['scheme'] == 'sqlite':
            config['database'] = parsed.path
            if parsed.path.startswith('///'):
                config['database'] = parsed.path[3:]  # Remove sqlite:///
            elif parsed.path.startswith('//'):
                config['database'] = parsed.path[2:]  # Remove sqlite://
        
        return config
    
    @classmethod
    def build_database_url(cls, db_type: str, **kwargs) -> str:
        """Build database URL from parameters."""
        if db_type == 'sqlite':
            path = kwargs.get('database', 'postfix_manager.db')
            return f"sqlite:///{path}"
        
        elif db_type in ['mysql', 'mariadb']:
            scheme = 'mysql'
            host = kwargs.get('host', 'localhost')
            port = kwargs.get('port', 3306)
            username = kwargs.get('username', '')
            password = kwargs.get('password', '')
            database = kwargs.get('database', 'postfix_manager')
            
            if username and password:
                auth = f"{username}:{password}@"
            elif username:
                auth = f"{username}@"
            else:
                auth = ""
            
            return f"{scheme}://{auth}{host}:{port}/{database}"
        
        elif db_type == 'postgresql':
            scheme = 'postgresql'
            host = kwargs.get('host', 'localhost')
            port = kwargs.get('port', 5432)
            username = kwargs.get('username', '')
            password = kwargs.get('password', '')
            database = kwargs.get('database', 'postfix_manager')
            
            if username and password:
                auth = f"{username}:{password}@"
            elif username:
                auth = f"{username}@"
            else:
                auth = ""
            
            return f"{scheme}://{auth}{host}:{port}/{database}"
        
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    @classmethod
    def get_connection_options(cls, database_url: str) -> Dict[str, Any]:
        """Get database-specific connection options."""
        db_type = cls.detect_database_type(database_url)
        base_options = cls.DEFAULT_POOL_SETTINGS.get(db_type, {}).copy()
        
        # Add database-specific options
        if db_type == 'mysql':
            base_options.update({
                'charset': 'utf8mb4',
                'sql_mode': 'STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO',
                'autocommit': False,
                'ssl': cls._get_ssl_options('mysql')
            })
        
        elif db_type == 'postgresql':
            base_options.update({
                'client_encoding': 'utf8',
                'sslmode': 'prefer',
                'ssl': cls._get_ssl_options('postgresql')
            })
        
        return base_options
    
    @classmethod
    def _get_ssl_options(cls, db_type: str) -> Optional[Dict[str, Any]]:
        """Get SSL configuration options."""
        ssl_ca = os.environ.get(f'{db_type.upper()}_SSL_CA')
        ssl_cert = os.environ.get(f'{db_type.upper()}_SSL_CERT')
        ssl_key = os.environ.get(f'{db_type.upper()}_SSL_KEY')
        
        if ssl_ca or ssl_cert or ssl_key:
            ssl_options = {}
            if ssl_ca:
                ssl_options['ca'] = ssl_ca
            if ssl_cert:
                ssl_options['cert'] = ssl_cert
            if ssl_key:
                ssl_options['key'] = ssl_key
            return ssl_options
        
        return None
    
    @classmethod
    def validate_database_url(cls, database_url: str) -> bool:
        """Validate database URL format."""
        try:
            db_type = cls.detect_database_type(database_url)
            parsed = cls.parse_database_url(database_url)
            
            if db_type == 'sqlite':
                return True  # SQLite URLs are always valid
            
            # Check required fields for client-server databases
            required_fields = ['host', 'database']
            return all(parsed.get(field) for field in required_fields)
            
        except Exception:
            return False
    
    @classmethod
    def get_database_info(cls, database_url: str) -> Dict[str, Any]:
        """Get database information for display/logging."""
        try:
            db_type = cls.detect_database_type(database_url)
            parsed = cls.parse_database_url(database_url)
            
            info = {
                'type': db_type,
                'scheme': parsed['scheme'],
                'host': parsed.get('host', 'N/A'),
                'port': parsed.get('port', 'N/A'),
                'database': parsed.get('database', 'N/A'),
                'username': parsed.get('username', 'N/A'),
                'ssl_enabled': bool(cls._get_ssl_options(db_type))
            }
            
            # Mask password for security
            if parsed.get('password'):
                info['password'] = '***'
            else:
                info['password'] = 'None'
            
            return info
            
        except Exception as e:
            return {
                'type': 'unknown',
                'error': str(e)
            }


def get_database_config(app) -> Dict[str, Any]:
    """Get database configuration for Flask app."""
    database_url = app.config.get('SQLALCHEMY_DATABASE_URI')
    
    if not database_url:
        raise ValueError("SQLALCHEMY_DATABASE_URI not configured")
    
    # Validate database URL
    if not DatabaseConfig.validate_database_url(database_url):
        raise ValueError(f"Invalid database URL: {database_url}")
    
    # Get database type and connection options
    db_type = DatabaseConfig.detect_database_type(database_url)
    connection_options = DatabaseConfig.get_connection_options(database_url)
    db_info = DatabaseConfig.get_database_info(database_url)
    
    config = {
        'database_url': database_url,
        'database_type': db_type,
        'connection_options': connection_options,
        'database_info': db_info,
        'ssl_enabled': db_info.get('ssl_enabled', False)
    }
    
    # Add database-specific configuration
    if db_type == 'mysql':
        config.update({
            'mysql_ssl_mode': 'REQUIRED' if db_info['ssl_enabled'] else 'PREFERRED',
            'mysql_auto_commit': False,
            'mysql_charset': 'utf8mb4'
        })
    
    elif db_type == 'postgresql':
        config.update({
            'postgresql_ssl_mode': 'require' if db_info['ssl_enabled'] else 'prefer',
            'postgresql_timezone': 'UTC'
        })
    
    return config


def test_database_connection(database_url: str) -> Dict[str, Any]:
    """Test database connection and return status."""
    try:
        db_type = DatabaseConfig.detect_database_type(database_url)
        parsed = DatabaseConfig.parse_database_url(database_url)
        
        if db_type == 'sqlite':
            import sqlite3
            db_path = parsed['database']
            conn = sqlite3.connect(db_path, timeout=10)
            conn.close()
            return {
                'status': 'success',
                'message': f'SQLite database accessible at {db_path}',
                'database_type': 'sqlite'
            }
        
        elif db_type == 'mysql':
            import pymysql
            conn = pymysql.connect(
                host=parsed['host'],
                port=parsed['port'] or 3306,
                user=parsed['username'],
                password=parsed['password'],
                database=parsed['database'],
                charset='utf8mb4',
                connect_timeout=10
            )
            conn.close()
            return {
                'status': 'success',
                'message': f'MySQL/MariaDB connection successful to {parsed["host"]}:{parsed["port"]}',
                'database_type': 'mysql'
            }
        
        elif db_type == 'postgresql':
            import psycopg2
            conn = psycopg2.connect(
                host=parsed['host'],
                port=parsed['port'] or 5432,
                user=parsed['username'],
                password=parsed['password'],
                database=parsed['database'],
                connect_timeout=10
            )
            conn.close()
            return {
                'status': 'success',
                'message': f'PostgreSQL connection successful to {parsed["host"]}:{parsed["port"]}',
                'database_type': 'postgresql'
            }
        
        else:
            return {
                'status': 'error',
                'message': f'Unsupported database type: {db_type}',
                'database_type': 'unknown'
            }
    
    except ImportError as e:
        return {
            'status': 'error',
            'message': f'Database driver not installed: {str(e)}',
            'database_type': db_type if 'db_type' in locals() else 'unknown'
        }
    
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Connection failed: {str(e)}',
            'database_type': db_type if 'db_type' in locals() else 'unknown'
        }
