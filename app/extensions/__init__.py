"""
Flask Extensions Initialization
Main entry point for all Flask extensions
"""

# Import all extension instances for external access
from .database import db, migrate
from .auth import bcrypt, csrf, login_manager
from .limiter import limiter

# Import all initialization functions
from .database import init_database, init_migrations, get_migration_info, check_migration_status
from .auth import init_auth, init_csrf_config
from .limiter import init_limiter
from .config import init_config, init_mail_config
from .logging import init_logging_config
from .templates import init_template_context
from .blueprints import register_blueprints
from .monitoring import init_health_monitor, get_health_status, start_background_monitoring, stop_background_monitoring
from .sessions import init_session_config, get_session_info, cleanup_expired_sessions, get_session_stats
from .data_dirs import init_data_directories, get_data_manager, cleanup_data_directories


def init_extensions(app):
    """Initialize all Flask extensions in the correct order."""
    # 1. Configuration first
    init_config(app)
    
    # 2. Data directories (must be created before other components)
    init_data_directories(app)
    
    # 3. Database and migrations
    init_database(app)
    init_migrations(app)
    
    # 4. Authentication and security
    init_auth(app)
    init_csrf_config(app)
    
    # 5. Session management
    init_session_config(app)
    
    # 6. Rate limiting
    init_limiter(app)
    
    # 7. Logging
    init_logging_config(app)
    
    # 8. Template context
    init_template_context(app)
    
    # 9. Blueprints (register after all extensions are initialized)
    register_blueprints(app)
    
    # 10. Health monitoring (optional, after all other extensions)
    init_health_monitor(app)
    
    app.logger.info("All extensions initialized successfully")


# Convenience function to get migration status
def get_migration_status(app):
    """Get comprehensive migration status information."""
    return check_migration_status(app)


# Convenience function to get all migration info
def get_all_migration_info(app):
    """Get detailed migration information."""
    return get_migration_info(app)


# Export all extension instances for external use
__all__ = [
    # Extension instances
    'db', 'migrate', 'bcrypt', 'csrf', 'login_manager', 'limiter',
    
    # Main initialization function
    'init_extensions',
    
    # Migration functions
    'init_migrations', 'get_migration_info', 'check_migration_status',
    'get_migration_status', 'get_all_migration_info',
    
    # Individual initialization functions
    'init_database', 'init_auth', 'init_limiter', 'init_config',
    'init_mail_config', 'init_logging_config', 'init_template_context',
    'register_blueprints',
    
    # Monitoring functions
    'init_health_monitor', 'get_health_status', 'start_background_monitoring', 'stop_background_monitoring',
    
    # Session management functions
    'init_session_config', 'get_session_info', 'cleanup_expired_sessions', 'get_session_stats',
    
    # Data directory management functions
    'init_data_directories', 'get_data_manager', 'cleanup_data_directories'
]
