"""
Blueprint Extensions
Handles Flask blueprint registration
"""


def register_blueprints(app):
    """Register Flask blueprints."""
    from app.main import bp as main_bp
    from app.modules.auth import bp as auth_bp
    from app.modules.mail import bp as mail_bp
    from app.modules.ldap import bp as ldap_bp
    from app.modules.dashboard import bp as dashboard_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(mail_bp, url_prefix='/mail')
    app.register_blueprint(ldap_bp, url_prefix='/ldap')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    
    app.logger.info("All blueprints registered successfully")
