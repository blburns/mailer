"""
Authentication Extension
Handle user loading and authentication setup
"""

from flask_login import LoginManager
from .core import login_manager

def init_user_loader(app):
    """Initialize user loader for Flask-Login"""
    
    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID for Flask-Login"""
        try:
            from app.models import User
            return User.query.get(int(user_id))
        except Exception as e:
            app.logger.error(f"Error loading user {user_id}: {e}")
            return None
    
    app.logger.info("User loader initialized successfully")
