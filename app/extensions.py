"""
Flask Extensions
Central place to initialize Flask extensions (SQLAlchemy, Bcrypt, etc.)
"""

import os
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
csrf = CSRFProtect()
migrate = Migrate()

def get_default_limits():
    """Get default rate limits from environment variables."""
    day = os.getenv('RATE_LIMIT_DEFAULT_DAY', '200')
    hour = os.getenv('RATE_LIMIT_DEFAULT_HOUR', '50')
    minute = os.getenv('RATE_LIMIT_DEFAULT_MINUTE', '100')
    limits = []
    if day:
        limits.append(f"{day} per day")
    if hour:
        limits.append(f"{hour} per hour")
    if minute:
        limits.append(f"{minute} per minute")
    return limits

# Rate limiting configuration
RATE_LIMIT_ENABLED = os.getenv('FLASK_LIMITER_ENABLED', 'True').lower() == 'true'
RATE_LIMIT_STORAGE = os.getenv('RATE_LIMIT_STORAGE', 'memory')

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=get_default_limits() if RATE_LIMIT_ENABLED else [],
    storage_uri=os.getenv('RATE_LIMIT_REDIS_URL') if RATE_LIMIT_STORAGE == 'redis' else None
) if RATE_LIMIT_ENABLED else None

def construct_db_uri():
    """Construct database URI based on environment variables"""
    db_type = os.getenv("DB_TYPE", "sqlite")
    db_name = os.getenv("DB_NAME", "postfix_manager.db")
    db_user = os.getenv("DB_USER", "")
    db_pass = os.getenv("DB_PASSWORD", "")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "")
    
    if db_type == "sqlite":
        # Use appropriate path for development vs production
        if os.environ.get('FLASK_ENV') == 'production' or os.environ.get('ENV') == 'production':
            db_path = f'/opt/postfix-manager/app/data/db/{db_name}'
        else:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            db_path = os.path.join(project_root, 'app', 'data', 'db', db_name)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        return f"sqlite:///{db_path}"
    elif db_type == "postgresql":
        port = db_port or "5432"
        return f"postgresql://{db_user}:{db_pass}@{db_host}:{port}/{db_name}"
    elif db_type == "mysql":
        port = db_port or "3306"
        return f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{port}/{db_name}"
    else:
        raise ValueError(f"Unsupported DB_TYPE: {db_type}")

def init_config(app):
    """Set up core Flask app configuration from environment variables."""
    # Load environment files
    from dotenv import load_dotenv
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # Load .env files
    load_dotenv(os.path.join(project_root, '.env'))
    load_dotenv(os.path.join(project_root, '.env.local'))
    
    # Mode-specific
    mode = os.environ.get('FLASK_ENV') or os.environ.get('ENV') or 'development'
    load_dotenv(os.path.join(project_root, f'.env.{mode}'))
    
    # Basic Flask settings
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['DEBUG'] = mode == 'development'
    app.config['TESTING'] = False
    
    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = construct_db_uri()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 3600,
    }

def init_mail_config(app):
    """Initialize mail server configuration."""
    app.config['POSTFIX_CONFIG_DIR'] = os.getenv('POSTFIX_CONFIG_DIR', '/etc/postfix')
    app.config['DOVECOT_CONFIG_DIR'] = os.getenv('DOVECOT_CONFIG_DIR', '/etc/dovecot')
    app.config['LDAP_CONFIG_DIR'] = os.getenv('LDAP_CONFIG_DIR', '/etc/ldap')
    app.config['VMAIL_HOME'] = os.getenv('VMAIL_HOME', '/home/vmail')

def init_ldap_config(app):
    """Initialize LDAP configuration."""
    app.config['LDAP_SERVER_URI'] = os.getenv('LDAP_SERVER_URI', 'ldap://localhost:389')
    app.config['LDAP_BIND_DN'] = os.getenv('LDAP_BIND_DN', 'cn=admin,dc=example,dc=com')
    app.config['LDAP_BIND_PASSWORD'] = os.getenv('LDAP_BIND_PASSWORD', '')
    app.config['LDAP_BASE_DN'] = os.getenv('LDAP_BASE_DN', 'dc=example,dc=com')

def init_csrf_config(app):
    """Initialize CSRF configuration."""
    app.config['WTF_CSRF_ENABLED'] = os.getenv('CSRF_ENABLED', 'True').lower() == 'true'
    app.config['WTF_CSRF_TIME_LIMIT'] = int(os.getenv('CSRF_TIME_LIMIT', 3600))
    app.config['WTF_CSRF_SSL_STRICT'] = os.getenv('CSRF_SSL_STRICT', 'False').lower() == 'true'

def init_session_config(app):
    """Initialize session configuration."""
    # Session configuration
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_FILE_DIR'] = os.path.join(os.path.dirname(__file__), 'data', 'sessions')
    app.config['SESSION_COOKIE_SECURE'] = app.config['DEBUG'] is False
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = int(os.getenv('SESSION_LIFETIME', 3600))
    
    # Ensure session directory exists
    os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)

def init_logging_config(app):
    """Initialize logging configuration."""
    import logging
    from logging.handlers import RotatingFileHandler
    
    # Ensure logs directory exists
    log_dir = os.path.join(os.path.dirname(__file__), 'data', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Set log level
    log_level = getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper())
    app.logger.setLevel(log_level)
    
    # File handler
    if not app.debug:
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, 'app.log'),
            maxBytes=10240000,
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(log_level)
        app.logger.addHandler(file_handler)

def init_data_directories(app):
    """Ensure all data directories exist."""
    data_dirs = [
        'data/archive',
        'data/backups', 
        'data/cache',
        'data/db',
        'data/logs',
        'data/seeds',
        'data/sessions'
    ]
    
    base_dir = os.path.dirname(__file__)
    for dir_path in data_dirs:
        full_path = os.path.join(base_dir, dir_path)
        os.makedirs(full_path, exist_ok=True)
        
        # Create .gitkeep files
        gitkeep_file = os.path.join(full_path, '.gitkeep')
        if not os.path.exists(gitkeep_file):
            with open(gitkeep_file, 'w') as f:
                f.write('')

def register_blueprints(app):
    """Import and register all blueprints with the app."""
    # Main blueprints
    from app.main import bp as main_bp
    from app.modules.auth import bp as auth_bp
    from app.modules.mail import bp as mail_bp
    from app.modules.ldap import bp as ldap_bp
    from app.modules.dashboard import bp as dashboard_bp
    from app.modules.errors import bp as errors_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(mail_bp, url_prefix='/mail')
    app.register_blueprint(ldap_bp, url_prefix='/ldap')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(errors_bp, url_prefix='/error')

def init_error_handlers(app):
    """Initialize error handlers."""
    from flask import render_template, request, jsonify
    
    @app.errorhandler(404)
    def not_found_error(error):
        if request.is_xhr or request.path.startswith('/api/'):
            return jsonify({'error': 'Not Found'}), 404
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        if request.is_xhr or request.path.startswith('/api/'):
            return jsonify({'error': 'Internal Server Error'}), 500
        return render_template('errors/500.html'), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        if request.is_xhr or request.path.startswith('/api/'):
            return jsonify({'error': 'Forbidden'}), 403
        return render_template('errors/403.html'), 403

def init_extensions(app):
    """Initialize all Flask extensions with the app"""
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Initialize rate limiting if enabled
    if RATE_LIMIT_ENABLED and limiter:
        limiter.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

def init_user_loader(app):
    """Initialize user loader for Flask-Login."""
    from app.models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.query.get(int(user_id))
        except Exception:
            db.session.rollback()
            return None

def init_template_context(app):
    """Register template context processors for Jinja2 templates."""
    from flask import g
    from flask_login import current_user
    
    @app.context_processor
    def inject_global_vars():
        """Make global variables available to templates."""
        return {
            'current_year': 2025,
            'app_name': 'Postfix Manager'
        }
    
    @app.before_request
    def setup_request_context():
        """Set up request context for logging and user info."""
        if current_user.is_authenticated:
            g.user_id = current_user.id
        else:
            g.user_id = None
