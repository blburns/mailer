"""
Database Extensions
Handles SQLAlchemy and Flask-Migrate initialization
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize database extensions
db = SQLAlchemy()
migrate = Migrate()


def init_database(app):
    """Initialize database extensions."""
    db.init_app(app)
    migrate.init_app(app, db)


def init_migrations(app):
    """Initialize database migrations with enhanced configuration."""
    # Set migration directory based on database type
    db_type = app.config.get('DB_TYPE', 'sqlite').lower()
    migration_dir = f'migrations/{db_type}'
    
    # Ensure migration directory exists
    import os
    os.makedirs(migration_dir, exist_ok=True)
    
    # Configure migration settings
    app.config['MIGRATION_DIR'] = migration_dir
    app.config['MIGRATION_DB_TYPE'] = db_type
    
    # Set database-specific migration options
    if db_type == 'mysql':
        app.config['MIGRATION_COMPARE_TYPE'] = True
        app.config['MIGRATION_COMPARE_SERVER_DEFAULT'] = True
        app.config['MIGRATION_RENDER_AS_BATCH'] = True
    elif db_type == 'postgresql':
        app.config['MIGRATION_COMPARE_TYPE'] = True
        app.config['MIGRATION_COMPARE_SERVER_DEFAULT'] = True
        app.config['MIGRATION_RENDER_AS_BATCH'] = False
    else:  # sqlite
        app.config['MIGRATION_COMPARE_TYPE'] = False
        app.config['MIGRATION_COMPARE_SERVER_DEFAULT'] = False
        app.config['MIGRATION_RENDER_AS_BATCH'] = True
    
    # Log migration configuration
    app.logger.info(f"Migration system initialized for {db_type.upper()}")
    app.logger.info(f"Migration directory: {migration_dir}")
    
    return migration_dir


def get_migration_info(app):
    """Get current migration information."""
    try:
        from flask_migrate import current, history
        with app.app_context():
            current_rev = current()
            migration_history = history()
            return {
                'current_revision': current_rev,
                'migration_history': migration_history,
                'migration_dir': app.config.get('MIGRATION_DIR'),
                'db_type': app.config.get('MIGRATION_DB_TYPE')
            }
    except Exception as e:
        app.logger.error(f"Failed to get migration info: {e}")
        return None


def check_migration_status(app):
    """Check if migrations are up to date."""
    try:
        from flask_migrate import current, heads
        with app.app_context():
            current_rev = current()
            head_rev = heads()
            
            if current_rev == head_rev:
                return {
                    'status': 'up_to_date',
                    'current': current_rev,
                    'head': head_rev,
                    'message': 'Database is up to date'
                }
            else:
                return {
                    'status': 'pending',
                    'current': current_rev,
                    'head': head_rev,
                    'message': f'Database needs migration from {current_rev} to {head_rev}'
                }
    except Exception as e:
        app.logger.error(f"Failed to check migration status: {e}")
        return {
            'status': 'error',
            'error': str(e),
            'message': 'Failed to check migration status'
        }
