"""
Template Context Extension
Handle template context processors and global variables
"""

from flask import g, request
from flask_login import current_user
from datetime import datetime

def init_template_context(app):
    """Register template context processors for Jinja2 templates."""
    
    @app.context_processor
    def inject_globals():
        """Inject global variables into all templates"""
        return {
            'current_year': datetime.now().year,
            'app_name': 'Postfix Manager',
            'current_user': current_user,
            'request': request,
        }
    
    @app.context_processor
    def inject_navigation_utils():
        """Inject navigation utility functions into templates"""
        def get_breadcrumbs():
            """Generate breadcrumbs based on current route"""
            breadcrumbs = []
            path_parts = request.path.strip('/').split('/')
            
            # Always start with home
            breadcrumbs.append(('Home', '/'))
            
            # Build breadcrumbs from path
            current_path = ''
            for part in path_parts:
                if part:
                    current_path += f'/{part}'
                    # Convert part to title case and make it readable
                    title = part.replace('-', ' ').replace('_', ' ').title()
                    breadcrumbs.append((title, current_path))
            
            return breadcrumbs
        
        def is_active_route(route_path):
            """Check if a route is currently active"""
            return request.path.startswith(route_path)
        
        def get_nav_class(route_path):
            """Get CSS class for navigation items"""
            if is_active_route(route_path):
                return 'bg-blue-700 text-white'
            return 'text-gray-300 hover:bg-gray-700 hover:text-white'
        
        return {
            'get_breadcrumbs': get_breadcrumbs,
            'is_active_route': is_active_route,
            'get_nav_class': get_nav_class,
        }
    
    app.logger.info("Template context processors initialized successfully")

def init_request_context(app):
    """Register a before_request handler to set up request context for logging and user/session info."""
    
    @app.before_request
    def setup_request_context():
        """Set up request context for logging and user/session info"""
        if current_user.is_authenticated:
            g.user_id = current_user.id
        else:
            g.user_id = None
        
        g.session_id = request.cookies.get('session') if request else None
    
    app.logger.info("Request context setup initialized successfully")
