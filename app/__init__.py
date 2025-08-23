"""
Postfix Mail Server Management Application
A comprehensive web interface for managing Postfix, Dovecot, and OpenLDAP
"""

import os
from flask import Flask

from app.extensions import init_extensions


def create_app() -> Flask:
    """Application factory function."""
    app = Flask(__name__)
    app.url_map.strict_slashes = False

    with app.app_context():
        # Initialize all extensions in the correct order
        init_extensions(app)

    return app


# Create the application instance for WSGI/CLI
app = create_app()

if __name__ == '__main__':
    app.run(
        debug=os.getenv('FLASK_DEBUG', 'False') == 'True',
        host=os.getenv('FLASK_RUN_HOST', '127.0.0.1'),
        port=int(os.getenv('FLASK_RUN_PORT', 5000)),
    )
