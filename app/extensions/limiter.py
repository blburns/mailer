"""
Rate Limiting Extension
Configure and manage Flask-Limiter for API rate limiting
"""

import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

def get_default_limits():
    """Get default rate limits from environment variables"""
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

def create_limiter():
    """Create and configure the rate limiter"""
    rate_limit_enabled = os.getenv('FLASK_LIMITER_ENABLED', 'True').lower() == 'true'
    rate_limit_storage = os.getenv('RATELIMIT_STORAGE_URL', 'memory://')
    
    if not rate_limit_enabled:
        return None
    
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=get_default_limits(),
        storage_uri=rate_limit_storage
    )
    
    return limiter

def init_limiter(app, limiter):
    """Initialize rate limiter with the app"""
    if limiter:
        limiter.init_app(app)
        app.logger.info("Rate limiting initialized")
    else:
        app.logger.info("Rate limiting disabled")
