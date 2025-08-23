"""
Errors Blueprint
Provides manual access to error pages for testing and development
"""

from flask import Blueprint

bp = Blueprint('errors', __name__, url_prefix='/error')

from app.modules.errors import routes
