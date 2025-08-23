"""
Error Routes
Provides manual access to error pages for testing and development
"""

from flask import render_template, abort
from app.modules.errors import bp


@bp.route('/400')
def bad_request():
    """Manual 400 Bad Request error page."""
    return render_template('errors/400.html', title='Bad Request'), 400


@bp.route('/401')
def unauthorized():
    """Manual 401 Unauthorized error page."""
    return render_template('errors/401.html', title='Unauthorized'), 401


@bp.route('/403')
def forbidden():
    """Manual 403 Forbidden error page."""
    return render_template('errors/403.html', title='Forbidden'), 403


@bp.route('/404')
def not_found():
    """Manual 404 Not Found error page."""
    return render_template('errors/404.html', title='Page Not Found'), 404


@bp.route('/405')
def method_not_allowed():
    """Manual 405 Method Not Allowed error page."""
    return render_template('errors/405.html', title='Method Not Allowed'), 405


@bp.route('/418')
def im_a_teapot():
    """Manual 418 I'm a Teapot error page."""
    return render_template('errors/418.html', title="I'm a Teapot"), 418


@bp.route('/422')
def unprocessable_entity():
    """Manual 422 Unprocessable Entity error page."""
    return render_template('errors/422.html', title='Unprocessable Entity'), 422


@bp.route('/429')
def too_many_requests():
    """Manual 429 Too Many Requests error page."""
    return render_template('errors/429.html', title='Too Many Requests'), 429


@bp.route('/500')
def internal_server_error():
    """Manual 500 Internal Server Error error page."""
    return render_template('errors/500.html', title='Internal Server Error'), 500


@bp.route('/502')
def bad_gateway():
    """Manual 502 Bad Gateway error page."""
    return render_template('errors/502.html', title='Bad Gateway'), 502


@bp.route('/503')
def service_unavailable():
    """Manual 503 Service Unavailable error page."""
    return render_template('errors/503.html', title='Service Unavailable'), 503


@bp.route('/504')
def gateway_timeout():
    """Manual 504 Gateway Timeout error page."""
    return render_template('errors/504.html', title='Gateway Timeout'), 504


@bp.route('/test')
def test_errors():
    """Test page showing all available error codes."""
    error_codes = [
        {'code': 400, 'name': 'Bad Request', 'description': 'The request could not be processed due to invalid syntax.'},
        {'code': 401, 'name': 'Unauthorized', 'description': 'Authentication is required to access this resource.'},
        {'code': 403, 'name': 'Forbidden', 'description': 'You do not have permission to access this resource.'},
        {'code': 404, 'name': 'Not Found', 'description': 'The requested resource was not found.'},
        {'code': 405, 'name': 'Method Not Allowed', 'description': 'The HTTP method is not allowed for this resource.'},
        {'code': 418, 'name': "I'm a Teapot", 'description': 'The server refuses to brew coffee because it is a teapot.'},
        {'code': 422, 'name': 'Unprocessable Entity', 'description': 'The request was well-formed but contains invalid data.'},
        {'code': 429, 'name': 'Too Many Requests', 'description': 'Rate limit exceeded. Please try again later.'},
        {'code': 500, 'name': 'Internal Server Error', 'description': 'An unexpected error occurred. Please try again later.'},
        {'code': 502, 'name': 'Bad Gateway', 'description': 'The server received an invalid response from an upstream server.'},
        {'code': 503, 'name': 'Service Unavailable', 'description': 'The service is temporarily unavailable. Please try again later.'},
        {'code': 504, 'name': 'Gateway Timeout', 'description': 'The server did not receive a timely response from an upstream server.'}
    ]
    
    return render_template('errors/test_errors.html', title='Error Testing', error_codes=error_codes)


@bp.route('/trigger/<int:code>')
def trigger_error(code):
    """Trigger a specific HTTP error code."""
    if code in [400, 401, 403, 404, 405, 418, 422, 429, 500, 502, 503, 504]:
        abort(code)
    else:
        abort(404)  # Invalid error code
