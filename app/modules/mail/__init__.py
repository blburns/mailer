"""
Mail Management Blueprint
"""

from flask import Blueprint

bp = Blueprint('mail', __name__)

from app.modules.mail import routes
