"""
Authentication Extensions
Handles Bcrypt, LoginManager, and CSRF protection
"""

from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager

# Initialize authentication extensions
bcrypt = Bcrypt()
csrf = CSRFProtect()
login_manager = LoginManager()


def init_auth(app):
    """Initialize authentication extensions."""
    bcrypt.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))


def init_csrf_config(app):
    """Initialize CSRF protection configuration."""
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['WTF_CSRF_TIME_LIMIT'] = 3600
    app.config['WTF_CSRF_HEADERS'] = ['X-CSRFToken']
    app.config['WTF_CSRF_SSL_STRICT'] = False
