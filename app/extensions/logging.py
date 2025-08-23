"""
Logging Extension
Configure comprehensive logging for the entire application
"""

import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

def setup_logger(name, log_file, level=logging.INFO):
    """Helper to set up a logger with file and console handlers."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False  # Prevent messages from being passed to the root logger
    
    log_dir = Path(__file__).parent.parent / 'data' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # File handler
    file_handler = RotatingFileHandler(log_dir / log_file, maxBytes=1024 * 1024 * 10, backupCount=5)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)
    
    # Console handler (for development)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    logger.addHandler(console_handler)
    
    return logger

def init_logging_config(app):
    """Initialize comprehensive logging configuration for the entire application."""
    log_dir = Path(__file__).parent.parent / 'data' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    
    app_logger = setup_logger('app', 'app.log', logging.INFO)
    app.logger = app_logger
    
    app.config['LOGGERS'] = {
        'app': app_logger,
        'access': setup_logger('access', 'access.log', logging.INFO),
        'error': setup_logger('error', 'error.log', logging.ERROR),
        'security': setup_logger('security', 'security.log', logging.WARNING),
        'email': setup_logger('email', 'email.log', logging.INFO),
        'audit': setup_logger('audit', 'audit.log', logging.INFO)
    }
    
    app.logger.info('Postfix Manager logging system initialized')
    app.logger.info(f'Log files directory: {log_dir}')
    
    for logger_name, logger_obj in app.config['LOGGERS'].items():
        if logger_obj.handlers:
            handler = logger_obj.handlers[0]
            if hasattr(handler, 'baseFilename'):
                app.logger.info(f'Logger "{logger_name}" configured: {handler.baseFilename}')
            else:
                app.logger.info(f'Logger "{logger_name}" configured: {type(handler).__name__}')
        else:
            app.logger.info(f'Logger "{logger_name}" configured: no handlers')
    
    app.logger.info("Logging configuration initialized successfully")
