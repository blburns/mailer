"""
System Module

Handles system-wide functionality including:
- System configuration management
- Audit logging and monitoring
- System status and health checks
- Administrative functions
"""

from flask import Blueprint

bp = Blueprint('system', __name__, url_prefix='/system')

from app.modules.system import routes
