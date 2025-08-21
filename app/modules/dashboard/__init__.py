"""
Dashboard Blueprint
"""

from flask import Blueprint

bp = Blueprint('dashboard', __name__)

from app.modules.dashboard import routes
