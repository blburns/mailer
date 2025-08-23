"""
Postfix Mail Server Management Application
A comprehensive web interface for managing Postfix, Dovecot, and OpenLDAP
"""

import os
from flask import Flask


def create_app() -> Flask:
    """Application factory function."""
    app = Flask(__name__)
    app.url_map.strict_slashes = False

    with app.app_context():
        # Import and initialize everything
        from app.extensions import (
            init_config, init_data_directories, init_mail_config, init_ldap_config,
            init_csrf_config, init_session_config, init_logging_config,
            init_extensions, init_user_loader, init_template_context,
            register_blueprints, init_error_handlers
        )
        
        # Initialize configuration first
        init_config(app)
        
        # Initialize data directories
        init_data_directories(app)
        
        # Initialize specific configurations
        init_mail_config(app)
        init_ldap_config(app)
        init_csrf_config(app)
        init_session_config(app)
        init_logging_config(app)
        
        # Initialize Flask extensions
        init_extensions(app)
        
        # Initialize user loader for Flask-Login
        init_user_loader(app)
        
        # Initialize template context
        init_template_context(app)
        
        # Register blueprints
        register_blueprints(app)
        
        # Initialize error handlers
        init_error_handlers(app)

    return app


# Create the application instance for WSGI/CLI
app = create_app()

if __name__ == '__main__':
    app.run(
        debug=os.getenv('FLASK_DEBUG', 'False') == 'True',
        host=os.getenv('FLASK_RUN_HOST', '127.0.0.1'),
        port=int(os.getenv('FLASK_RUN_PORT', 5000)),
    )
