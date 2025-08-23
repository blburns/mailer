"""
Flask Extensions Package
Central orchestrator for all Flask extensions
"""

# Import all extension modules
from .core import db, bcrypt, login_manager, csrf, migrate, init_core_extensions
from .limiter import create_limiter, init_limiter
from .config import init_config, init_mail_config, init_ldap_config, init_csrf_config
from .logging import init_logging_config
from .sessions import init_data_directories, init_session_config
from .error_handlers import init_error_handlers
from .templates import init_template_context, init_request_context
from .auth import init_user_loader
from .blueprints import register_blueprints

# Create rate limiter instance
limiter = create_limiter()

def init_extensions(app):
    """Initialize all Flask extensions in the correct order"""
    
    # 1. Configuration (must be first)
    init_config(app)
    
    # 2. Core extensions
    init_core_extensions(app)
    
    # 3. Rate limiter
    init_limiter(app, limiter)
    
    # 4. Logging (after config, before others)
    init_logging_config(app)
    
    # 5. Data directories and sessions
    init_data_directories(app)
    init_session_config(app)
    
    # 6. Mail and LDAP config
    init_mail_config(app)
    init_ldap_config(app)
    
    # 7. Template context and request context
    init_template_context(app)
    init_request_context(app)
    
    # 8. Error handlers
    init_error_handlers(app)
    
    # 9. User loader
    init_user_loader(app)
    
    # 10. Blueprint registration (must be last)
    register_blueprints(app)
    
    app.logger.info("All extensions initialized successfully")

# Export commonly used extensions
__all__ = [
    'db',
    'bcrypt', 
    'login_manager',
    'csrf',
    'migrate',
    'limiter',
    'init_extensions'
]
