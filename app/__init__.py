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
        # Import and initialize everything using consolidated extension system
        from app.extensions import init_extensions
        
        # Initialize all extensions in the correct order
        init_extensions(app)

    return app


if __name__ == '__main__':
    # Create the application instance for CLI
    app = create_app()
    app.run(
        debug=os.getenv('FLASK_DEBUG', 'False') == 'True',
        host=os.getenv('FLASK_RUN_HOST', '127.0.0.1'),
        port=int(os.getenv('FLASK_RUN_PORT', 5000)),
    )
