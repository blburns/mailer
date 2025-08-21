"""
LDAP Management Blueprint
"""

from flask import Blueprint

bp = Blueprint('ldap', __name__)

from app.modules.ldap import routes
