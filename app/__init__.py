"""
Postfix Mail Server Management Application
A comprehensive web interface for managing Postfix, Dovecot, and OpenLDAP
"""

import os
import subprocess
from flask import Flask
from dotenv import load_dotenv

# Load environment variables early with layered files
def _load_env_layers():
    """Load .env, .env.local, and .env.<mode> plus system app.conf"""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    # Base
    load_dotenv(os.path.join(project_root, '.env'))
    # Local overrides (gitignored)
    load_dotenv(os.path.join(project_root, '.env.local'))
    # Mode-specific
    mode = os.environ.get('FLASK_ENV') or os.environ.get('ENV') or 'development'
    load_dotenv(os.path.join(project_root, f'.env.{mode}'))
    # Production system config (highest precedence)
    try:
        if os.path.exists('/etc/postfix-manager/app.conf'):
            load_dotenv('/etc/postfix-manager/app.conf', override=True)
    except Exception:
        pass

_load_env_layers()

from app.extensions import (
    init_extensions,
    init_mail_config,
    init_logging_config,
    init_csrf_config,
    register_blueprints,
    init_config,
    init_migrations,
    init_template_context,
)


def create_app() -> Flask:
    """Application factory function."""
    app = Flask(__name__)
    app.url_map.strict_slashes = False

    with app.app_context():
        # Core configuration and mail
        init_config(app)
        init_mail_config(app)

        # Logging and CSRF
        init_logging_config(app)
        init_csrf_config(app)

        # Extensions and migrations
        init_extensions(app)
        init_migrations(app)

        # Blueprints
        register_blueprints(app)

        # Template context (current_year, config, etc.)
        init_template_context(app)

        # Optional background health monitor
        try:
            from app.utils import monitoring
            monitoring.health_checker.app = app
            monitoring.health_checker._start_background_monitoring()
        except Exception:
            pass

    return app


# Create the application instance for WSGI/CLI
app = create_app()

if __name__ == '__main__':
    app.run(
        debug=os.getenv('FLASK_DEBUG', 'False') == 'True',
        host=os.getenv('FLASK_RUN_HOST', '127.0.0.1'),
        port=int(os.getenv('FLASK_RUN_PORT', 5000)),
    )
