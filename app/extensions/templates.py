"""
Template Extensions
Handles template context variables and navigation functions
"""


def init_template_context(app):
    """Initialize template context variables."""
    @app.context_processor
    def inject_template_vars():
        return {
            'current_year': 2025,
            'app_name': 'Postfix Manager'
        }
    
    # Register navigation template functions
    @app.context_processor
    def inject_navigation_functions():
        from app.utils.navigation import (
            get_breadcrumbs,
            get_current_module,
            is_active_route,
            is_active_module
        )
        return {
            'get_breadcrumbs': get_breadcrumbs,
            'get_current_module': get_current_module,
            'is_active_route': is_active_route,
            'is_active_module': is_active_module
        }
