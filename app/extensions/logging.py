"""
Logging Extensions
Handles comprehensive application logging configuration
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logger(name, log_file, level=logging.INFO, max_bytes=10485760, backup_count=5):
    """Set up a logger with file and console handlers."""
    # Create logs directory if it doesn't exist
    log_dir = Path(__file__).parent.parent / 'data' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s [%(name)s] %(levelname)s: %(message)s [%(filename)s:%(lineno)d]'
    )
    simple_formatter = logging.Formatter(
        '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
    )
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_dir / log_file,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(detailed_formatter)
    
    # Console handler (for development)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def init_logging_config(app):
    """Initialize comprehensive logging configuration for the entire application."""
    # Ensure logs directory exists
    log_dir = Path(__file__).parent.parent / 'data' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Set up main application logger
    app_logger = setup_logger('app', 'app.log', logging.INFO)
    app.logger = app_logger
    
    # Set up specialized loggers
    access_logger = setup_logger('access', 'access.log', logging.INFO)
    error_logger = setup_logger('error', 'error.log', logging.ERROR)
    security_logger = setup_logger('security', 'security.log', logging.WARNING)
    email_logger = setup_logger('email', 'email.log', logging.INFO)
    audit_logger = setup_logger('audit', 'audit.log', logging.INFO)
    
    # Store loggers in app config for access throughout the application
    app.config['LOGGERS'] = {
        'app': app_logger,
        'access': access_logger,
        'error': error_logger,
        'security': security_logger,
        'email': email_logger,
        'audit': audit_logger
    }
    
    # Set up Flask's default logger to use our app logger
    app.logger.handlers.clear()
    for handler in app_logger.handlers:
        app.logger.addHandler(handler)
    
    # Log startup
    app.logger.info('Postfix Manager logging system initialized')
    app.logger.info(f'Log files directory: {log_dir}')
    
    # Log the available loggers
    for logger_name, logger in app.config['LOGGERS'].items():
        app.logger.info(f'Logger "{logger_name}" configured: {logger.handlers[0].baseFilename}')
    
    return app.config['LOGGERS']


def get_logger(app, logger_name='app'):
    """Get a specific logger from the application context."""
    loggers = app.config.get('LOGGERS', {})
    return loggers.get(logger_name, app.logger)


def log_access(app, message, level=logging.INFO, **kwargs):
    """Log access-related information."""
    logger = get_logger(app, 'access')
    extra_info = ' '.join([f'{k}={v}' for k, v in kwargs.items()])
    full_message = f"{message} {extra_info}".strip()
    logger.log(level, full_message)


def log_error(app, message, error=None, **kwargs):
    """Log error information."""
    logger = get_logger(app, 'error')
    extra_info = ' '.join([f'{k}={v}' for k, v in kwargs.items()])
    
    if error:
        full_message = f"{message} - Error: {str(error)} {extra_info}".strip()
        logger.error(full_message, exc_info=True)
    else:
        full_message = f"{message} {extra_info}".strip()
        logger.error(full_message)


def log_security(app, message, level=logging.WARNING, **kwargs):
    """Log security-related information."""
    logger = get_logger(app, 'security')
    extra_info = ' '.join([f'{k}={v}' for k, v in kwargs.items()])
    full_message = f"{message} {extra_info}".strip()
    logger.log(level, full_message)


def log_email(app, message, level=logging.INFO, **kwargs):
    """Log email-related information."""
    logger = get_logger(app, 'email')
    extra_info = ' '.join([f'{k}={v}' for k, v in kwargs.items()])
    full_message = f"{message} {extra_info}".strip()
    logger.log(level, full_message)
