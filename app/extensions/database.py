"""
Database Configuration and Management
Handles database connection setup and configuration
"""

import os
from os import environ, path
from dotenv import load_dotenv
from flask import jsonify, Response

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
load_dotenv(path.join(BASE_DIR, ".env"))

# Supported database types for hostname-based configurations
HOSTNAME_DB_TYPES = [
    'mysql', 'postgresql', 'mssql', 'oracle', 'mariadb', 'redshift', 'firebird', 'db2'
]

class DbConfig:
    """
    Set the Database configuration variables from the .env file
    NOTE: Only SQLite, MySQL/MariaDB, & PostgreSQL are working currently
    NOTE: MySQL Unix Sockets is currently un-supported
    """

    def __init__(self):
        # General Database Variables (required)
        self.db_type: str = self._get_env_var('DB_TYPE', 'sqlite').lower()
        self.db_name: str = self._get_env_var('DB_NAME', 'postfix_manager.db')

        # SQLite Specific Variables (conditionally required)
        self.db_directory: str = self._get_env_var('DB_DIRECTORY', self._get_default_db_directory()) if self.db_type == 'sqlite' else None

        # MySQL & PostgreSQL Specific Variables (required for these types)
        if self.db_type in HOSTNAME_DB_TYPES:
            self.db_hostname: str = self._get_env_var('DB_HOSTNAME', 'localhost')
            self.db_username: str = self._get_env_var('DB_USERNAME', 'postfix_manager')
            self.db_password: str = self._get_env_var('DB_PASSWORD', 'postfix_manager')
            self.db_port: str = self._get_env_var('DB_PORT', self._get_default_port())

        # MySQL Specific Variables (optional)
        self.db_use_unix_socket: bool = os.getenv('DB_USE_UNIX_SOCKET', 'false').lower() == 'true'
        self.db_unix_socket: str = os.getenv('DB_UNIX_SOCKET') if self.db_use_unix_socket else None

        # Construct DB URI
        self.db_uri = self._build_db_uri()

    def _get_env_var(self, var_name: str, default: str = None) -> str:
        """
        Retrieve an environment variable with optional default value.
        """
        value = os.getenv(var_name, default)
        if not value and default is None:
            raise EnvironmentError(f"The required environment variable '{var_name}' is not set in the .env file.")
        return value

    def _get_default_db_directory(self) -> str:
        """Get the default database directory based on environment."""
        if os.environ.get('FLASK_ENV') == 'production' or os.environ.get('ENV') == 'production':
            return '/opt/postfix-manager/app/data/db'
        else:
            return os.path.join(BASE_DIR, 'app', 'data', 'db')

    def _get_default_port(self) -> str:
        """Get the default port for the database type."""
        if self.db_type in ['mysql', 'mariadb']:
            return '3306'
        elif self.db_type == 'postgresql':
            return '5432'
        elif self.db_type == 'mssql':
            return '1433'
        elif self.db_type == 'oracle':
            return '1521'
        else:
            return '5432'  # Default to PostgreSQL port

    def _build_db_uri(self) -> str:
        """
        Build the database URI based on the database type and provided environment variables.
        """

        """
        Database: SQLite (Required)
        URI Format: sqlite:///absolute/path/to/database.db
        """
        if self.db_type == 'sqlite':
            db_path = path.abspath(path.join(self.db_directory, self.db_name))
            # Ensure directory exists
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            return f'sqlite:///{db_path}'

        """
        Database: MySQL (Included)
        Driver: pymysql
        URI Format: mysql+pymysql://<username>:<password>@<hostname>:<port>/database
        """
        if self.db_type == 'mysql' or self.db_type == 'mariadb':
            if self.db_use_unix_socket:
                if not self.db_unix_socket:
                    raise ValueError("DB_UNIX_SOCKET must be set for MySQL Unix sockets.")
                return f'mysql+pymysql:///{self.db_name}?unix_socket={self.db_unix_socket}'
            return f'mysql+pymysql://{self.db_username}:{self.db_password}@{self.db_hostname}:{self.db_port}/{self.db_name}'

        """ 
        Database: Postgresql (Included)
        Driver: psycopg2 or psycopg2-bin
        URI Format: postgresql+psycopg2://<username>:<password>@<hostname>:<port>/database
        """
        if self.db_type == 'postgresql':
            return f'postgresql://{self.db_username}:{self.db_password}@{self.db_hostname}:{self.db_port}/{self.db_name}'

        """ 
        Database: SQLite In-Memory (Optional) 
        Driver: sqlite
        URI Format: sqlite:///:memory:
        """
        if self.db_type == 'sqlite_memory':
            return 'sqlite:///:memory:'

        """ 
        Microsoft SQL Server (Optional) 
        Driver: pyodbc or pymssql
        URI Format: mssql+pyodbc://<username>:<password>@<hostname>:<port>/<database>?driver=<driver_name>
        """
        if self.db_type == 'mssql':
            return f'mssql+pyodbc://{self.db_username}:{self.db_password}@{self.db_hostname}:{self.db_port}/{self.db_name}?driver=ODBC+Driver+17+for+SQL+Server'

        """
        Database: Oracle
        Driver: cx_Oracle
        URI Format: oracle+cx_oracle://<username>:<password>@<hostname>:<port>/<sid>
        """
        if self.db_type == 'oracle':
            return f'oracle+cx_oracle://{self.db_username}:{self.db_password}@{self.db_hostname}:{self.db_port}/{self.db_name}'

        """
        Database: Amazon Redshift (Optional)
        Driver: psycopg2 psycopg2-bin
        URI Format: postgresql+psycopg2://<username>:<password>@<redshift_endpoint>:<port>/<database>
        """
        if self.db_type == 'redshift':
            return f'postgresql+psycopg2://{self.db_username}:{self.db_password}@{self.db_hostname}:{self.db_port}/{self.db_name}'

        """
        Database: Firebird (Optional)
        Driver: fdb
        URI Format: firebird+fdb://<username>:<password>@<hostname>/<database_path>
        """
        if self.db_type == 'firebird':
            return f'firebird+fdb://{self.db_username}:{self.db_password}@{self.db_hostname}/{self.db_name}'

        """
        Database: IBM Db2 (Optional)
        Driver: ibm_db_sa
        URI Format: db2+ibm_db://<username>:<password>@<hostname>:<port>/<database>
        """
        if self.db_type == 'db2':
            return f'db2+ibm_db://{self.db_username}:{self.db_password}@{self.db_hostname}:{self.db_port}/{self.db_name}'

        raise ValueError(f"Unsupported database type: {self.db_type}")

    # Accessor Methods
    def get_db_uri(self) -> str:
        """
        Return the database URI as string.
        """
        return self.db_uri

    def get_db_config(self) -> dict:
        """
        Return all database configuration details as a dictionary.
        """
        return {
            'db_type': self.db_type,
            'db_directory': self.db_directory if hasattr(self, 'db_directory') and self.db_directory else None,
            'db_name': self.db_name,
            'db_hostname': getattr(self, 'db_hostname', None),
            'db_username': getattr(self, 'db_username', None),
            'db_password': getattr(self, 'db_password', None),
            'db_port': getattr(self, 'db_port', None),
            'db_use_unix_socket': self.db_use_unix_socket,
            'db_unix_socket': self.db_unix_socket if self.db_unix_socket else None,
            'db_uri': self.db_uri,
        }

    def get_db_uri_json(self):
        """
        Return the database URI in JSON format
        """
        return jsonify({'data': self.db_uri})

    def get_db_config_json(self) -> Response:
        """
        Return all database configuration details as a JSON response.
        """
        return jsonify({'data': self.get_db_config()})
