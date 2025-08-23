"""
Logging Utilities
Provides easy-to-use logging functions for different application components
"""

import logging
from functools import wraps
from flask import current_app, request, g
from flask_login import current_user


def get_logger(logger_name='app'):
    """Get a logger from the current application context."""
    if current_app:
        return current_app.config.get('LOGGERS', {}).get(logger_name, current_app.logger)
    return logging.getLogger(logger_name)


def log_request_info(logger_name='access'):
    """Log information about the current request."""
    if not current_app:
        return
    
    logger = get_logger(logger_name)
    
    # Get request information
    user_id = current_user.id if current_user.is_authenticated else 'anonymous'
    ip_address = request.remote_addr
    user_agent = request.headers.get('User-Agent', 'Unknown')
    method = request.method
    url = request.url
    referrer = request.headers.get('Referer', 'No referrer')
    
    # Log the request
    logger.info(
        f"Request: {method} {url} - User: {user_id} - IP: {ip_address} - "
        f"Referrer: {referrer} - User-Agent: {user_agent}"
    )


def log_user_action(action, details=None, logger_name='access'):
    """Log user actions for audit purposes."""
    if not current_app:
        return
    
    logger = get_logger(logger_name)
    
    user_id = current_user.id if current_user.is_authenticated else 'anonymous'
    ip_address = request.remote_addr if request else 'unknown'
    
    message = f"User Action: {action} - User: {user_id} - IP: {ip_address}"
    if details:
        message += f" - Details: {details}"
    
    logger.info(message)


def log_security_event(event_type, details=None, severity='warning', logger_name='security'):
    """Log security-related events."""
    if not current_app:
        return
    
    logger = get_logger(logger_name)
    
    user_id = current_user.id if current_user.is_authenticated else 'anonymous'
    ip_address = request.remote_addr if request else 'unknown'
    
    message = f"Security Event: {event_type} - User: {user_id} - IP: {ip_address}"
    if details:
        message += f" - Details: {details}"
    
    # Map severity to logging level
    level_map = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }
    
    log_level = level_map.get(severity.lower(), logging.WARNING)
    logger.log(log_level, message)


def log_email_operation(operation, details=None, logger_name='email'):
    """Log email-related operations."""
    if not current_app:
        return
    
    logger = get_logger(logger_name)
    
    user_id = current_user.id if current_user.is_authenticated else 'anonymous'
    
    message = f"Email Operation: {operation} - User: {user_id}"
    if details:
        message += f" - Details: {details}"
    
    logger.info(message)


def log_audit_event(event_type, action, target=None, details=None, logger_name='audit'):
    """Log audit trail events for compliance and tracking."""
    if not current_app:
        return
    
    logger = get_logger(logger_name)
    
    user_id = current_user.id if current_user.is_authenticated else 'anonymous'
    ip_address = request.remote_addr if request else 'unknown'
    
    message = f"Audit Event: {event_type} - Action: {action} - User: {user_id} - IP: {ip_address}"
    if target:
        message += f" - Target: {target}"
    if details:
        message += f" - Details: {details}"
    
    logger.info(message)


def log_data_access(resource_type, resource_id, access_type, success=True, logger_name='audit'):
    """Log data access events for audit trails."""
    if not current_app:
        return
    
    logger = get_logger(logger_name)
    
    user_id = current_user.id if current_user.is_authenticated else 'anonymous'
    ip_address = request.remote_addr if request else 'unknown'
    
    status = "SUCCESS" if success else "FAILURE"
    message = f"Data Access: {resource_type} - ID: {resource_id} - Type: {access_type} - Status: {status} - User: {user_id} - IP: {ip_address}"
    
    logger.info(message)


def log_configuration_audit(setting_name, old_value, new_value, reason=None, logger_name='audit'):
    """Log configuration changes for audit compliance."""
    if not current_app:
        return
    
    logger = get_logger(logger_name)
    
    user_id = current_user.id if current_user.is_authenticated else 'anonymous'
    ip_address = request.remote_addr if request else 'unknown'
    
    message = f"Config Audit: {setting_name} - Old: {old_value} - New: {new_value} - User: {user_id} - IP: {ip_address}"
    if reason:
        message += f" - Reason: {reason}"
    
    logger.info(message)


def log_system_event(event_type, component, details=None, severity='info', logger_name='audit'):
    """Log system-level events for audit trails."""
    if not current_app:
        return
    
    logger = get_logger(logger_name)
    
    user_id = current_user.id if current_user.is_authenticated else 'anonymous'
    ip_address = request.remote_addr if request else 'unknown'
    
    message = f"System Event: {event_type} - Component: {component} - User: {user_id} - IP: {ip_address}"
    if details:
        message += f" - Details: {details}"
    
    # Map severity to logging level
    level_map = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }
    
    log_level = level_map.get(severity.lower(), logging.INFO)
    logger.log(log_level, message)


def log_error_with_context(error, context=None, logger_name='error'):
    """Log errors with additional context information."""
    if not current_app:
        return
    
    logger = get_logger(logger_name)
    
    user_id = current_user.id if current_user.is_authenticated else 'anonymous'
    ip_address = request.remote_addr if request else 'unknown'
    url = request.url if request else 'unknown'
    
    message = f"Error: {str(error)} - User: {user_id} - IP: {ip_address} - URL: {url}"
    if context:
        message += f" - Context: {context}"
    
    logger.error(message, exc_info=True)


def log_performance(operation, duration, details=None, logger_name='app'):
    """Log performance metrics."""
    if not current_app:
        return
    
    logger = get_logger(logger_name)
    
    user_id = current_user.id if current_user.is_authenticated else 'anonymous'
    
    message = f"Performance: {operation} - Duration: {duration:.3f}s - User: {user_id}"
    if details:
        message += f" - Details: {details}"
    
    logger.info(message)


def log_database_operation(operation, table=None, record_id=None, logger_name='app'):
    """Log database operations."""
    if not current_app:
        return
    
    logger = get_logger(logger_name)
    
    user_id = current_user.id if current_user.is_authenticated else 'anonymous'
    
    message = f"Database: {operation}"
    if table:
        message += f" - Table: {table}"
    if record_id:
        message += f" - Record ID: {record_id}"
    message += f" - User: {user_id}"
    
    logger.info(message)


def log_mail_server_operation(operation, server_type, details=None, logger_name='email'):
    """Log mail server operations (Postfix, Dovecot, etc.)."""
    if not current_app:
        return
    
    logger = get_logger(logger_name)
    
    user_id = current_user.id if current_user.is_authenticated else 'anonymous'
    
    message = f"Mail Server: {operation} - Server: {server_type} - User: {user_id}"
    if details:
        message += f" - Details: {details}"
    
    logger.info(message)


def log_ldap_operation(operation, details=None, logger_name='app'):
    """Log LDAP operations."""
    if not current_app:
        return
    
    logger = get_logger(logger_name)
    
    user_id = current_user.id if current_user.is_authenticated else 'anonymous'
    
    message = f"LDAP: {operation} - User: {user_id}"
    if details:
        message += f" - Details: {details}"
    
    logger.info(message)


def log_configuration_change(setting, old_value, new_value, logger_name='app'):
    """Log configuration changes."""
    if not current_app:
        return
    
    logger = get_logger(logger_name)
    
    user_id = current_user.id if current_user.is_authenticated else 'anonymous'
    
    message = f"Config Change: {setting} - Old: {old_value} - New: {new_value} - User: {user_id}"
    logger.info(message)


def log_authentication_event(event_type, success, details=None, logger_name='security'):
    """Log authentication events."""
    if not current_app:
        return
    
    logger = get_logger(logger_name)
    
    ip_address = request.remote_addr if request else 'unknown'
    user_agent = request.headers.get('User-Agent', 'Unknown') if request else 'Unknown'
    
    status = "SUCCESS" if success else "FAILURE"
    message = f"Authentication: {event_type} - Status: {status} - IP: {ip_address} - User-Agent: {user_agent}"
    if details:
        message += f" - Details: {details}"
    
    # Use warning level for failed authentication attempts
    log_level = logging.WARNING if not success else logging.INFO
    logger.log(log_level, message)


def log_request_decorator(logger_name='access'):
    """Decorator to automatically log request information."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Log request start
                log_request_info(logger_name)
                
                # Execute the function
                result = f(*args, **kwargs)
                
                # Log successful completion
                logger = get_logger(logger_name)
                logger.info(f"Request completed successfully: {f.__name__}")
                
                return result
            except Exception as e:
                # Log any errors
                log_error_with_context(e, f"Function: {f.__name__}")
                raise
        return decorated_function
    return decorator


def log_performance_decorator(operation_name=None, logger_name='app'):
    """Decorator to automatically log performance metrics."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            import time
            start_time = time.time()
            
            try:
                result = f(*args, **kwargs)
                
                # Calculate duration
                duration = time.time() - start_time
                
                # Log performance
                op_name = operation_name or f.__name__
                log_performance(op_name, duration)
                
                return result
            except Exception as e:
                # Log error with performance context
                duration = time.time() - start_time
                log_error_with_context(e, f"Function: {f.__name__} - Duration: {duration:.3f}s")
                raise
        return decorated_function
    return decorator
