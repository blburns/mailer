"""
Navigation utilities for breadcrumbs and navigation context
"""

from typing import List, Dict, Optional
from flask import g, request


class Breadcrumb:
    """Represents a single breadcrumb item."""
    
    def __init__(self, text: str, url: str, active: bool = False):
        self.text = text
        self.url = url
        self.active = active


def set_breadcrumbs(breadcrumbs: List[Dict[str, str]]):
    """
    Set breadcrumbs for the current request.
    
    Args:
        breadcrumbs: List of dictionaries with 'text' and 'url' keys
        
    Example:
        set_breadcrumbs([
            {'text': 'Mail Management', 'url': url_for('mail.index')},
            {'text': 'Postfix', 'url': url_for('mail.postfix')}
        ])
    """
    g.breadcrumbs = breadcrumbs


def get_breadcrumbs() -> List[Breadcrumb]:
    """Get breadcrumbs for the current request."""
    breadcrumbs = getattr(g, 'breadcrumbs', [])
    return [Breadcrumb(**crumb) for crumb in breadcrumbs]


def add_breadcrumb(text: str, url: str, active: bool = False):
    """Add a single breadcrumb to the current request."""
    if not hasattr(g, 'breadcrumbs'):
        g.breadcrumbs = []
    
    g.breadcrumbs.append({
        'text': text,
        'url': url,
        'active': active
    })


def clear_breadcrumbs():
    """Clear breadcrumbs for the current request."""
    if hasattr(g, 'breadcrumbs'):
        del g.breadcrumbs


def get_page_title() -> str:
    """Get the current page title based on breadcrumbs."""
    breadcrumbs = get_breadcrumbs()
    if breadcrumbs:
        return breadcrumbs[-1].text
    return "Postfix Manager"


def get_navigation_context() -> Dict[str, any]:
    """Get navigation context for the current request."""
    return {
        'breadcrumbs': get_breadcrumbs(),
        'page_title': get_page_title(),
        'current_path': request.path,
        'current_module': get_current_module()
    }


def get_current_module() -> Optional[str]:
    """Get the current module based on the request path."""
    path = request.path.strip('/')
    if path.startswith('mail'):
        return 'mail'
    elif path.startswith('dashboard'):
        return 'dashboard'
    elif path.startswith('ldap'):
        return 'ldap'
    elif path.startswith('auth'):
        return 'auth'
    elif path.startswith('system'):
        return 'system'
    return None


def is_active_route(route_name: str) -> bool:
    """Check if the given route is currently active."""
    return request.endpoint == route_name


def is_active_module(module_name: str) -> bool:
    """Check if the given module is currently active."""
    return get_current_module() == module_name


# Common breadcrumb patterns
def set_mail_breadcrumbs(subsection: str = None, current_path: str = None):
    """Set breadcrumbs for mail management pages."""
    breadcrumbs = [
        {'text': 'Mail Management', 'url': '/mail'}
    ]
    
    if subsection:
        breadcrumbs.append({
            'text': subsection,
            'url': current_path or '/mail',
            'active': True
        })
    
    set_breadcrumbs(breadcrumbs)


def set_dashboard_breadcrumbs(subsection: str = None, current_path: str = None):
    """Set breadcrumbs for dashboard pages."""
    breadcrumbs = [
        {'text': 'Dashboard', 'url': '/dashboard'}
    ]
    
    if subsection:
        breadcrumbs.append({
            'text': subsection,
            'url': current_path or '/dashboard',
            'active': True
        })
    
    set_breadcrumbs(breadcrumbs)


def set_ldap_breadcrumbs(subsection: str = None, current_path: str = None):
    """Set breadcrumbs for LDAP pages."""
    breadcrumbs = [
        {'text': 'LDAP Management', 'url': '/ldap'}
    ]
    
    if subsection:
        breadcrumbs.append({
            'text': subsection,
            'url': current_path or '/ldap',
            'active': True
        })
    
    set_breadcrumbs(breadcrumbs)


def set_system_breadcrumbs(subsection: str = None, current_path: str = None):
    """Set breadcrumbs for system pages."""
    breadcrumbs = [
        {'text': 'System', 'url': '/system'}
    ]
    
    if subsection:
        breadcrumbs.append({
            'text': subsection,
            'url': current_path or '/system',
            'active': True
        })
    
    set_breadcrumbs(breadcrumbs)
