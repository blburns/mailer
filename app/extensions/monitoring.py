"""
Monitoring Extensions
Handles health monitoring and background monitoring functionality
"""


def init_health_monitor(app):
    """Initialize the health monitoring system."""
    try:
        from app.utils import monitoring
        monitoring.health_checker.app = app
        monitoring.health_checker._start_background_monitoring()
        app.logger.info("Health monitoring system initialized successfully")
    except Exception as e:
        app.logger.warning(f"Health monitoring system not available: {e}")


def get_health_status(app):
    """Get current health status of the application."""
    try:
        from app.utils import monitoring
        return monitoring.health_checker.get_status()
    except Exception:
        return {
            'status': 'unknown',
            'message': 'Health monitoring not available',
            'timestamp': None
        }


def start_background_monitoring(app):
    """Start background monitoring if available."""
    try:
        from app.utils import monitoring
        monitoring.health_checker._start_background_monitoring()
        app.logger.info("Background monitoring started")
        return True
    except Exception as e:
        app.logger.warning(f"Failed to start background monitoring: {e}")
        return False


def stop_background_monitoring(app):
    """Stop background monitoring if available."""
    try:
        from app.utils import monitoring
        monitoring.health_checker._stop_background_monitoring()
        app.logger.info("Background monitoring stopped")
        return True
    except Exception as e:
        app.logger.warning(f"Failed to stop background monitoring: {e}")
        return False
