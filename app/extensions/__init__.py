"""
Flask Extensions Initialization
"""

import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
csrf = CSRFProtect()
login_manager = LoginManager()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)


def init_extensions(app):
    """Initialize Flask extensions."""
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))


def init_mail_config(app):
    """Initialize mail configuration."""
    # Mail configuration will be handled by the mail management module
    pass


def init_logging_config(app):
    """Initialize logging configuration."""
    if not app.debug:
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/postfix-manager.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Postfix Manager startup')


def init_csrf_config(app):
    """Initialize CSRF protection."""
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['WTF_CSRF_TIME_LIMIT'] = 3600
    app.config['WTF_CSRF_HEADERS'] = ['X-CSRFToken']
    app.config['WTF_CSRF_SSL_STRICT'] = False


def init_config(app):
    """Initialize application configuration."""
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    # Get the absolute path to the database file
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'db', 'postfix_manager.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Postfix Manager specific config
    app.config['POSTFIX_CONFIG_DIR'] = os.environ.get('POSTFIX_CONFIG_DIR') or '/etc/postfix'
    app.config['DOVECOT_CONFIG_DIR'] = os.environ.get('DOVECOT_CONFIG_DIR') or '/etc/dovecot'
    app.config['LDAP_CONFIG_DIR'] = os.environ.get('LDAP_CONFIG_DIR') or '/etc/ldap'
    app.config['VMAIL_HOME'] = os.environ.get('VMAIL_HOME') or '/home/vmail'


def init_migrations(app):
    """Initialize database migrations."""
    # Migrations will be handled by Flask-Migrate
    pass


def init_template_context(app):
    """Initialize template context variables."""
    @app.context_processor
    def inject_template_vars():
        return {
            'current_year': 2025,
            'app_name': 'Postfix Manager'
        }
    
    # Register navigation template functions
    @app.context_processor
    def inject_navigation_functions():
        from app.utils.navigation import (
            get_breadcrumbs,
            get_current_module,
            is_active_route,
            is_active_module
        )
        return {
            'get_breadcrumbs': get_breadcrumbs,
            'get_current_module': get_current_module,
            'is_active_route': is_active_route,
            'is_active_module': is_active_module
        }


def register_blueprints(app):
    """Register Flask blueprints."""
    from app.main import bp as main_bp
    from app.modules.auth import bp as auth_bp
    from app.modules.mail import bp as mail_bp
    from app.modules.ldap import bp as ldap_bp
    from app.modules.dashboard import bp as dashboard_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(mail_bp, url_prefix='/mail')
    app.register_blueprint(ldap_bp, url_prefix='/ldap')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
