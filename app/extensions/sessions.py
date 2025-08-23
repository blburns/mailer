"""
Session Management Extension
Handle user session configuration and data directory management
"""

import os
from pathlib import Path
from datetime import datetime

class DataDirectoryManager:
    """Manages all application data directories."""
    def __init__(self, app_root):
        self.app_root = Path(app_root)
        self.data_root = self.app_root / 'data'
        self.directories = {
            'archive': {'path': self.data_root / 'archive', 'description': 'Archived data and old records', 'mount_point': '/mnt/postfix-manager/archive', 'backup_frequency': 'weekly'},
            'backups': {'path': self.data_root / 'backups', 'description': 'Database and configuration backups', 'mount_point': '/mnt/postfix-manager/backups', 'backup_frequency': 'daily'},
            'cache': {'path': self.data_root / 'cache', 'description': 'Application cache and temporary files', 'mount_point': '/mnt/postfix-manager/cache', 'backup_frequency': 'never'},
            'db': {'path': self.data_root / 'db', 'description': 'Database files and migrations', 'mount_point': '/mnt/postfix-manager/db', 'backup_frequency': 'hourly'},
            'logs': {'path': self.data_root / 'logs', 'description': 'Application and system logs', 'mount_point': '/mnt/postfix-manager/logs', 'backup_frequency': 'daily'},
            'seeds': {'path': self.data_root / 'seeds', 'description': 'Database seed data and fixtures', 'mount_point': '/mnt/postfix-manager/seeds', 'backup_frequency': 'weekly'},
            'sessions': {'path': self.data_root / 'sessions', 'description': 'User session data', 'mount_point': '/mnt/postfix-manager/sessions', 'backup_frequency': 'never'}
        }
    
    def ensure_directories(self):
        """Create all data directories with proper permissions"""
        for dir_name, dir_info in self.directories.items():
            dir_path = dir_info['path']
            dir_path.mkdir(parents=True, exist_ok=True)
            if dir_name in ['sessions', 'db']:
                dir_path.chmod(0o700)
            elif dir_name in ['logs', 'cache']:
                dir_path.chmod(0o755)
            else:
                dir_path.chmod(0o755)
            gitkeep_file = dir_path / '.gitkeep'
            if not gitkeep_file.exists():
                gitkeep_file.touch()
                gitkeep_file.chmod(0o644)
    
    def get_directory_info(self):
        """Return information about all directories"""
        return self.directories

def init_data_directories(app):
    """Initialize all application data directories"""
    app_root = Path(app.root_path).parent
    manager = DataDirectoryManager(app_root)
    manager.ensure_directories()
    app.config['DATA_MANAGER'] = manager
    app.logger.info("Data directories initialized:")
    for dir_name, dir_info in manager.get_directory_info().items():
        app.logger.info(f"  {dir_name}: {dir_info['path']} ({dir_info['description']})")
    return manager

def init_session_config(app):
    """Initialize session configuration"""
    app.config['SESSION_TYPE'] = os.getenv('SESSION_TYPE', 'filesystem')
    app.config['SESSION_FILE_DIR'] = os.getenv('SESSION_FILE_DIR', str(Path(app.root_path).parent / 'data' / 'sessions'))
    app.config['SESSION_COOKIE_SECURE'] = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    app.config['SESSION_COOKIE_HTTPONLY'] = os.getenv('SESSION_COOKIE_HTTPONLY', 'True').lower() == 'true'
    app.config['SESSION_COOKIE_SAMESITE'] = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')
    app.config['PERMANENT_SESSION_LIFETIME'] = int(os.getenv('PERMANENT_SESSION_LIFETIME', 3600 * 24 * 7))  # 7 days
    
    # Ensure session directory exists
    Path(app.config['SESSION_FILE_DIR']).mkdir(parents=True, exist_ok=True)
    app.logger.info(f"Session storage configured: {app.config['SESSION_FILE_DIR']}")
    app.logger.info("Session configuration initialized successfully")
