"""
Data Directory Management
Handles all application data directories for easy mounting to block/object storage
"""

import os
from pathlib import Path
import shutil


class DataDirectoryManager:
    """Manages all application data directories."""
    
    def __init__(self, app_root):
        self.app_root = Path(app_root)
        self.data_root = self.app_root / 'data'
        
        # Define all data directories with their purposes
        self.directories = {
            'archive': {
                'path': self.data_root / 'archive',
                'description': 'Archived data and old records',
                'mount_point': '/mnt/postfix-manager/archive',
                'backup_frequency': 'weekly'
            },
            'backups': {
                'path': self.data_root / 'backups',
                'description': 'Database and configuration backups',
                'mount_point': '/mnt/postfix-manager/backups',
                'backup_frequency': 'daily'
            },
            'cache': {
                'path': self.data_root / 'cache',
                'description': 'Application cache and temporary files',
                'mount_point': '/mnt/postfix-manager/cache',
                'backup_frequency': 'never'
            },
            'db': {
                'path': self.data_root / 'db',
                'description': 'Database files and migrations',
                'mount_point': '/mnt/postfix-manager/db',
                'backup_frequency': 'hourly'
            },
            'logs': {
                'path': self.data_root / 'logs',
                'description': 'Application and system logs',
                'mount_point': '/mnt/postfix-manager/logs',
                'backup_frequency': 'daily'
            },
            'seeds': {
                'path': self.data_root / 'seeds',
                'description': 'Database seed data and fixtures',
                'mount_point': '/mnt/postfix-manager/seeds',
                'backup_frequency': 'weekly'
            },
            'sessions': {
                'path': self.data_root / 'sessions',
                'description': 'User session data',
                'mount_point': '/mnt/postfix-manager/sessions',
                'backup_frequency': 'never'
            }
        }
    
    def ensure_directories(self):
        """Ensure all data directories exist with proper permissions."""
        for dir_name, dir_info in self.directories.items():
            dir_path = dir_info['path']
            dir_path.mkdir(parents=True, exist_ok=True)
            
            # Set appropriate permissions based on directory type
            if dir_name in ['sessions', 'db']:
                # Sensitive data - restrictive permissions
                dir_path.chmod(0o700)
            elif dir_name in ['logs', 'cache']:
                # Application data - moderate permissions
                dir_path.chmod(0o755)
            else:
                # General data - standard permissions
                dir_path.chmod(0o755)
            
            # Create .gitkeep files to ensure directories are tracked
            gitkeep_file = dir_path / '.gitkeep'
            if not gitkeep_file.exists():
                gitkeep_file.touch()
                gitkeep_file.chmod(0o644)
    
    def get_directory_info(self):
        """Get information about all data directories."""
        info = {}
        for dir_name, dir_info in self.directories.items():
            dir_path = dir_info['path']
            exists = dir_path.exists()
            
            info[dir_name] = {
                'path': str(dir_path),
                'exists': exists,
                'description': dir_info['description'],
                'mount_point': dir_info['mount_point'],
                'backup_frequency': dir_info['backup_frequency'],
                'size_bytes': self._get_directory_size(dir_path) if exists else 0,
                'file_count': len(list(dir_path.glob('*'))) if exists else 0,
                'permissions': oct(dir_path.stat().st_mode)[-3:] if exists else None
            }
        
        return info
    
    def _get_directory_size(self, dir_path):
        """Calculate the total size of a directory in bytes."""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(dir_path):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    if os.path.exists(file_path):
                        total_size += os.path.getsize(file_path)
        except (OSError, PermissionError):
            pass
        return total_size
    
    def cleanup_cache(self):
        """Clean up cache directory."""
        cache_dir = self.directories['cache']['path']
        if cache_dir.exists():
            try:
                # Remove all files but keep the directory
                for item in cache_dir.iterdir():
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
                
                # Recreate .gitkeep
                gitkeep_file = cache_dir / '.gitkeep'
                gitkeep_file.touch()
                gitkeep_file.chmod(0o644)
                
                return True
            except Exception as e:
                return False
        return False
    
    def cleanup_sessions(self):
        """Clean up expired session files."""
        sessions_dir = self.directories['sessions']['path']
        if not sessions_dir.exists():
            return 0
        
        try:
            import time
            cleaned_count = 0
            
            # Remove files older than 24 hours (default session cleanup)
            cutoff_time = time.time() - (24 * 3600)
            
            for session_file in sessions_dir.glob('*'):
                if session_file.is_file() and session_file.name != '.gitkeep':
                    if session_file.stat().st_mtime < cutoff_time:
                        session_file.unlink()
                        cleaned_count += 1
            
            return cleaned_count
        except Exception:
            return 0
    
    def get_storage_mount_info(self):
        """Get information for mounting data directories to external storage."""
        mount_info = {}
        for dir_name, dir_info in self.directories.items():
            mount_info[dir_name] = {
                'local_path': str(dir_info['path']),
                'mount_point': dir_info['mount_point'],
                'description': dir_info['description'],
                'backup_frequency': dir_info['backup_frequency'],
                'mount_example': f"mount -t nfs server:/path/to/{dir_name} {dir_info['mount_point']}"
            }
        
        return mount_info
    
    def create_backup_script(self, output_path=None):
        """Create a backup script for all data directories."""
        if output_path is None:
            output_path = self.app_root / 'scripts' / 'backup_data.sh'
        
        script_content = f"""#!/bin/bash
# Postfix Manager Data Backup Script
# Generated automatically - DO NOT EDIT

BACKUP_ROOT="/backup/postfix-manager/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_ROOT"

echo "Starting backup to: $BACKUP_ROOT"

# Backup each directory according to its frequency
"""
        
        for dir_name, dir_info in self.directories.items():
            if dir_info['backup_frequency'] != 'never':
                script_content += f"""
# Backup {dir_name} ({dir_info['description']})
if [ -d "{dir_info['path']}" ]; then
    echo "Backing up {dir_name}..."
    tar -czf "$BACKUP_ROOT/{dir_name}.tar.gz" -C "{dir_info['path']}" .
    echo "✓ {dir_name} backed up"
else
    echo "⚠ {dir_name} directory not found"
fi
"""
        
        script_content += """
echo "Backup completed: $BACKUP_ROOT"
echo "Backup size: $(du -sh "$BACKUP_ROOT" | cut -f1)"
"""
        
        # Write the script
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(script_content)
        
        # Make it executable
        output_path.chmod(0o755)
        
        return output_path
    
    def get_disk_usage(self):
        """Get disk usage information for all data directories."""
        usage_info = {}
        for dir_name, dir_info in self.directories.items():
            dir_path = dir_info['path']
            if dir_path.exists():
                try:
                    stat = dir_path.stat()
                    usage_info[dir_name] = {
                        'size_bytes': self._get_directory_size(dir_path),
                        'inode_count': stat.st_nlink,
                        'device_id': stat.st_dev,
                        'mount_point': self._get_mount_point(dir_path)
                    }
                except (OSError, PermissionError):
                    usage_info[dir_name] = {'error': 'Permission denied'}
            else:
                usage_info[dir_name] = {'error': 'Directory does not exist'}
        
        return usage_info
    
    def _get_mount_point(self, path):
        """Get the mount point for a given path."""
        try:
            import subprocess
            result = subprocess.run(['df', str(path)], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    parts = lines[1].split()
                    if len(parts) >= 6:
                        return parts[5]
        except Exception:
            pass
        return str(path)


def init_data_directories(app):
    """Initialize all data directories for the application."""
    app_root = Path(app.root_path).parent
    manager = DataDirectoryManager(app_root)
    
    # Ensure all directories exist
    manager.ensure_directories()
    
    # Store manager in app config for later use
    app.config['DATA_MANAGER'] = manager
    
    # Log directory information
    app.logger.info("Data directories initialized:")
    for dir_name, dir_info in manager.get_directory_info().items():
        app.logger.info(f"  {dir_name}: {dir_info['path']} ({dir_info['description']})")
    
    return manager


def get_data_manager(app):
    """Get the data directory manager from the application context."""
    return app.config.get('DATA_MANAGER')


def cleanup_data_directories(app):
    """Clean up temporary data in cache and sessions directories."""
    manager = get_data_manager(app)
    if manager:
        cache_cleaned = manager.cleanup_cache()
        sessions_cleaned = manager.cleanup_sessions()
        
        if cache_cleaned:
            app.logger.info("Cache directory cleaned")
        if sessions_cleaned > 0:
            app.logger.info(f"Cleaned up {sessions_cleaned} expired session files")
        
        return cache_cleaned, sessions_cleaned
    
    return False, 0
