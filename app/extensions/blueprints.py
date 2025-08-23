"""
Blueprint Registration Extension
Handle registration of all application blueprints
"""

def register_blueprints(app):
    """Import and register all blueprints with the app."""
    
    # Import blueprints
    from app.main.routes import bp as main_bp
    from app.modules.auth import bp as auth_bp
    from app.modules.mail import bp as mail_bp
    from app.modules.ldap import bp as ldap_bp
    from app.modules.dashboard import bp as dashboard_bp
    from app.modules.system import bp as system_bp
    from app.modules.errors import bp as errors_bp
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(mail_bp, url_prefix='/mail')
    app.register_blueprint(ldap_bp, url_prefix='/ldap')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(system_bp, url_prefix='/system')
    app.register_blueprint(errors_bp, url_prefix='/error')
    
    app.logger.info("All blueprints registered successfully")
