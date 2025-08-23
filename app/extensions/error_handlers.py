"""
Error Handlers Extension
Handle application-wide error handling and custom error pages
"""

from flask import g, request, render_template, jsonify

def init_error_handlers(app):
    """Initialize error handlers for the application."""
    
    @app.errorhandler(400)
    def bad_request(error):
        if request.is_xhr or request.path.startswith('/api/'):
            return jsonify({'error': 'Bad Request', 'message': 'The request could not be processed due to invalid syntax.', 'code': 400}), 400
        return render_template('errors/400.html', title='Bad Request'), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        if request.is_xhr or request.path.startswith('/api/'):
            return jsonify({'error': 'Unauthorized', 'message': 'Authentication is required to access this resource.', 'code': 401}), 401
        return render_template('errors/401.html', title='Unauthorized'), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        if request.is_xhr or request.path.startswith('/api/'):
            return jsonify({'error': 'Forbidden', 'message': 'You do not have permission to access this resource.', 'code': 403}), 403
        return render_template('errors/403.html', title='Forbidden'), 403
    
    @app.errorhandler(404)
    def not_found(error):
        if request.is_xhr or request.path.startswith('/api/'):
            return jsonify({'error': 'Not Found', 'message': 'The requested resource was not found.', 'code': 404}), 404
        return render_template('errors/404.html', title='Page Not Found'), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        if request.is_xhr or request.path.startswith('/api/'):
            return jsonify({'error': 'Method Not Allowed', 'message': 'The HTTP method is not allowed for this resource.', 'code': 405}), 405
        return render_template('errors/405.html', title='Method Not Allowed'), 405
    
    @app.errorhandler(418)
    def im_a_teapot(error):
        if request.is_xhr or request.path.startswith('/api/'):
            return jsonify({'error': "I'm a Teapot", 'message': 'The server refuses to brew coffee because it is, permanently, a teapot.', 'code': 418}), 418
        return render_template('errors/418.html', title="I'm a Teapot"), 418
    
    @app.errorhandler(422)
    def unprocessable_entity(error):
        if request.is_xhr or request.path.startswith('/api/'):
            return jsonify({'error': 'Unprocessable Entity', 'message': 'The request was well-formed but contains invalid data.', 'code': 422}), 422
        return render_template('errors/422.html', title='Unprocessable Entity'), 422
    
    @app.errorhandler(429)
    def too_many_requests(error):
        if request.is_xhr or request.path.startswith('/api/'):
            return jsonify({'error': 'Too Many Requests', 'message': 'Rate limit exceeded. Please try again later.', 'code': 429}), 429
        return render_template('errors/429.html', title='Too Many Requests'), 429
    
    @app.errorhandler(500)
    def internal_server_error(error):
        app.logger.error(f'Server Error: {error}')
        if request.is_xhr or request.path.startswith('/api/'):
            return jsonify({'error': 'Internal Server Error', 'message': 'An unexpected error occurred. Please try again later.', 'code': 500}), 500
        return render_template('errors/500.html', title='Internal Server Error'), 500
    
    @app.errorhandler(502)
    def bad_gateway(error):
        if request.is_xhr or request.path.startswith('/api/'):
            return jsonify({'error': 'Bad Gateway', 'message': 'The server received an invalid response from an upstream server.', 'code': 502}), 502
        return render_template('errors/502.html', title='Bad Gateway'), 502
    
    @app.errorhandler(503)
    def service_unavailable(error):
        if request.is_xhr or request.path.startswith('/api/'):
            return jsonify({'error': 'Service Unavailable', 'message': 'The service is temporarily unavailable. Please try again later.', 'code': 503}), 503
        return render_template('errors/503.html', title='Service Unavailable'), 503
    
    @app.errorhandler(504)
    def gateway_timeout(error):
        if request.is_xhr or request.path.startswith('/api/'):
            return jsonify({'error': 'Gateway Timeout', 'message': 'The server did not receive a timely response from an upstream server.', 'code': 504}), 504
        return render_template('errors/504.html', title='Gateway Timeout'), 504
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        app.logger.error(f'Unhandled Exception: {error}')
        if request.is_xhr or request.path.startswith('/api/'):
            return jsonify({'error': 'Internal Server Error', 'message': 'An unexpected error occurred. Please try again later.', 'code': 500}), 500
        return render_template('errors/500.html', title='Internal Server Error'), 500
    
    app.logger.info("Error handlers initialized successfully")
