"""
Session Extensions
Handles Flask session configuration and management
"""

import os
from pathlib import Path


def init_session_config(app):
    """Initialize session configuration with data directory storage."""
    # Ensure sessions directory exists
    sessions_dir = Path(__file__).parent.parent / 'data' / 'sessions'
    sessions_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure session storage
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_FILE_DIR'] = str(sessions_dir)
    app.config['SESSION_FILE_THRESHOLD'] = 500  # Number of sessions stored in memory
    app.config['SESSION_FILE_MODE'] = 0o600  # Secure file permissions
    
    # Session security settings
    app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour in seconds
    
    # Session key settings
    app.config['SESSION_KEY_PREFIX'] = 'postfix_manager_'
    
    app.logger.info(f"Session storage configured: {sessions_dir}")


def get_session_info(app):
    """Get information about current session configuration."""
    sessions_dir = Path(__file__).parent.parent / 'data' / 'sessions'
    
    return {
        'session_type': app.config.get('SESSION_TYPE', 'filesystem'),
        'session_directory': str(sessions_dir),
        'session_cookie_secure': app.config.get('SESSION_COOKIE_SECURE', False),
        'session_cookie_httponly': app.config.get('SESSION_COOKIE_HTTPONLY', True),
        'session_lifetime': app.config.get('PERMANENT_SESSION_LIFETIME', 3600),
        'session_files_count': len(list(sessions_dir.glob('*'))) if sessions_dir.exists() else 0
    }


def cleanup_expired_sessions(app):
    """Clean up expired session files."""
    try:
        from datetime import datetime, timedelta
        import time
        
        sessions_dir = Path(app.config.get('SESSION_FILE_DIR', ''))
        if not sessions_dir.exists():
            return
        
        # Get session lifetime
        lifetime = app.config.get('PERMANENT_SESSION_LIFETIME', 3600)
        cutoff_time = time.time() - lifetime
        
        cleaned_count = 0
        for session_file in sessions_dir.glob('*'):
            if session_file.is_file():
                # Check if file is older than session lifetime
                if session_file.stat().st_mtime < cutoff_time:
                    session_file.unlink()
                    cleaned_count += 1
        
        if cleaned_count > 0:
            app.logger.info(f"Cleaned up {cleaned_count} expired session files")
            
    except Exception as e:
        app.logger.error(f"Failed to cleanup expired sessions: {e}")


def get_session_stats(app):
    """Get statistics about current sessions."""
    try:
        sessions_dir = Path(app.config.get('SESSION_FILE_DIR', ''))
        if not sessions_dir.exists():
            return {'total_sessions': 0, 'session_files': []}
        
        session_files = list(sessions_dir.glob('*'))
        total_sessions = len(session_files)
        
        # Get file sizes and modification times
        session_info = []
        for session_file in session_files:
            if session_file.is_file():
                stat = session_file.stat()
                session_info.append({
                    'filename': session_file.name,
                    'size_bytes': stat.st_size,
                    'modified': stat.st_mtime,
                    'age_seconds': time.time() - stat.st_mtime
                })
        
        return {
            'total_sessions': total_sessions,
            'session_files': session_info,
            'total_size_bytes': sum(info['size_bytes'] for info in session_info)
        }
        
    except Exception as e:
        app.logger.error(f"Failed to get session stats: {e}")
        return {'error': str(e)}
