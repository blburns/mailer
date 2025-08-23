"""
Rate Limiting Extensions
Handles Flask-Limiter for API rate limiting
"""

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)


def init_limiter(app):
    """Initialize rate limiting extensions."""
    limiter.init_app(app)
