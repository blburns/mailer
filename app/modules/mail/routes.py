"""
Mail Management Routes
"""

from flask import render_template, request, jsonify, flash, current_app
from flask_login import login_required, current_user
from app.modules.mail import bp
from app.models import AuditLog
from app.extensions import db
from app.utils.mail_manager import PostfixManager, DovecotManager
import json
import logging
import time
import os

logger = logging.getLogger(__name__)


@bp.route('/')
@login_required
def index():
    """Mail management dashboard."""
    return render_template('modules/mail/index.html', title='Mail Management')


@bp.route('/postfix')
@login_required
def postfix():
    """Postfix management."""
    return render_template('modules/mail/postfix.html', title='Postfix Management')


@bp.route('/postfix/management')
@login_required
def postfix_management():
    """Postfix management page."""
    return render_template('modules/mail/postfix.html', title='Postfix Management')


@bp.route('/dovecot')
@login_required
def dovecot():
    """Dovecot management."""
    return render_template('modules/mail/dovecot.html', title='Dovecot Management')


@bp.route('/dovecot/management')
@login_required
def dovecot_management():
    """Dovecot management page."""
    return render_template('modules/mail/dovecot.html', title='Dovecot Management')


@bp.route('/postfix/status')
@login_required
def postfix_status():
    """Get Postfix service status."""
    try:
        status = PostfixManager.get_status()
        return jsonify({
            'success': True,
            'status': status
        })
    except Exception as e:
        logger.error(f"Error getting Postfix status: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/postfix/restart', methods=['POST'])
@login_required
def postfix_restart():
    """Restart Postfix service."""
    try:
        logger.info(f"Postfix restart requested by user {current_user.id}")
        
        postfix_manager = PostfixManager()
        success = postfix_manager.restart_service()
        
        if success:
            # Log the action
            try:
                audit_log = AuditLog(
                    user_id=current_user.id,
                    action='restart_postfix',
                    resource_type='postfix_service',
                    resource_id='service',
                    details='Restarted Postfix service',
                    ip_address=request.remote_addr
                )
                db.session.add(audit_log)
                db.session.commit()
                logger.info(f"Audit log created for Postfix restart by user {current_user.id}")
            except Exception as db_error:
                logger.error(f"Failed to create audit log: {db_error}")
                # Don't fail the operation if audit logging fails
            
            return jsonify({
                'success': True,
                'message': 'Postfix service restarted successfully'
            })
        else:
            logger.warning(f"Postfix restart failed for user {current_user.id}")
            return jsonify({
                'success': False,
                'message': 'Failed to restart Postfix service'
            }), 500
    except Exception as e:
        logger.error(f"Error in postfix_restart: {e}")
        return jsonify({
            'success': False,
            'message': f'Error restarting Postfix: {str(e)}'
        }), 500


@bp.route('/postfix/reload', methods=['POST'])
@login_required
def postfix_reload():
    """Reload Postfix configuration."""
    try:
        logger.info(f"Postfix reload requested by user {current_user.id}")
        
        postfix_manager = PostfixManager()
        success = postfix_manager.reload_config()
        
        if success:
            # Log the action
            try:
                audit_log = AuditLog(
                    user_id=current_user.id,
                    action='reload_postfix_config',
                    resource_type='postfix_config',
                    resource_id='config',
                    details='Reloaded Postfix configuration',
                    ip_address=request.remote_addr
                )
                db.session.add(audit_log)
                db.session.commit()
                logger.info(f"Audit log created for Postfix reload by user {current_user.id}")
            except Exception as db_error:
                logger.error(f"Failed to create audit log: {db_error}")
                # Don't fail the operation if audit logging fails
            
            return jsonify({
                'success': True,
                'message': 'Postfix configuration reloaded successfully'
            })
        else:
            logger.warning(f"Postfix reload failed for user {current_user.id}")
            return jsonify({
                'success': False,
                'message': 'Failed to reload Postfix configuration'
            }), 500
    except Exception as e:
        logger.error(f"Error in postfix_reload: {e}")
        return jsonify({
            'success': False,
            'message': f'Error reloading Postfix: {str(e)}'
        }), 500


@bp.route('/postfix/check-config', methods=['POST'])
@login_required
def postfix_check_config():
    """Check Postfix configuration syntax."""
    try:
        logger.info(f"Postfix config check requested by user {current_user.id}")
        
        postfix_manager = PostfixManager()
        result = postfix_manager.check_config()
        
        return jsonify({
            'success': True,
            'result': result
        })
    except Exception as e:
        logger.error(f"Error in postfix_check_config: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/postfix/queue')
@login_required
def postfix_queue():
    """Get Postfix queue information."""
    try:
        postfix_manager = PostfixManager()
        
        # Get query parameters
        queue_type = request.args.get('queue', 'all')
        limit = int(request.args.get('limit', 100))
        
        # Get detailed queue information
        queue_info = postfix_manager.get_detailed_queue_info(queue_type, limit)
        
        return jsonify({
            'success': True,
            'queue': queue_info
        })
    except Exception as e:
        logger.error(f"Error in postfix_queue: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/postfix/queue/performance')
@login_required
def postfix_queue_performance():
    """Get Postfix queue performance metrics."""
    try:
        postfix_manager = PostfixManager()
        metrics = postfix_manager.get_queue_performance_metrics()
        
        return jsonify({
            'success': True,
            'metrics': metrics
        })
    except Exception as e:
        logger.error(f"Error in postfix_queue_performance: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/postfix/queue/message/<message_id>/delete', methods=['POST'])
@login_required
def postfix_delete_message(message_id):
    """Delete a specific message from the queue."""
    try:
        logger.info(f"Message deletion requested by user {current_user.id}: {message_id}")
        
        postfix_manager = PostfixManager()
        success = postfix_manager.delete_message(message_id)
        
        if success:
            # Log the action
            try:
                audit_log = AuditLog(
                    user_id=current_user.id,
                    action='delete_queue_message',
                    resource_type='postfix_queue',
                    resource_id=message_id,
                    details=f'Deleted message from queue: {message_id}',
                    ip_address=request.remote_addr
                )
                db.session.add(audit_log)
                db.session.commit()
            except Exception as db_error:
                logger.error(f"Failed to create audit log: {db_error}")
            
            return jsonify({
                'success': True,
                'message': f'Message {message_id} deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Failed to delete message {message_id}'
            }), 500
    except Exception as e:
        logger.error(f"Error in postfix_delete_message: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/postfix/queue/message/<message_id>/hold', methods=['POST'])
@login_required
def postfix_hold_message(message_id):
    """Hold a specific message in the queue."""
    try:
        logger.info(f"Message hold requested by user {current_user.id}: {message_id}")
        
        postfix_manager = PostfixManager()
        success = postfix_manager.hold_message(message_id)
        
        if success:
            # Log the action
            try:
                audit_log = AuditLog(
                    user_id=current_user.id,
                    action='hold_queue_message',
                    resource_type='postfix_queue',
                    resource_id=message_id,
                    details=f'Held message in queue: {message_id}',
                    ip_address=request.remote_addr
                )
                db.session.add(audit_log)
                db.session.commit()
            except Exception as db_error:
                logger.error(f"Failed to create audit log: {db_error}")
            
            return jsonify({
                'success': True,
                'message': f'Message {message_id} held successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Failed to hold message {message_id}'
            }), 500
    except Exception as e:
        logger.error(f"Error in postfix_hold_message: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/postfix/queue/message/<message_id>/release', methods=['POST'])
@login_required
def postfix_release_message(message_id):
    """Release a held message from the queue."""
    try:
        logger.info(f"Message release requested by user {current_user.id}: {message_id}")
        
        postfix_manager = PostfixManager()
        success = postfix_manager.release_message(message_id)
        
        if success:
            # Log the action
            try:
                audit_log = AuditLog(
                    user_id=current_user.id,
                    action='release_queue_message',
                    resource_type='postfix_queue',
                    resource_id=message_id,
                    details=f'Released message from queue: {message_id}',
                    ip_address=request.remote_addr
                )
                db.session.add(audit_log)
                db.session.commit()
            except Exception as db_error:
                logger.error(f"Failed to create audit log: {db_error}")
            
            return jsonify({
                'success': True,
                'message': f'Message {message_id} released successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Failed to release message {message_id}'
            }), 500
    except Exception as e:
        logger.error(f"Error in postfix_release_message: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/postfix/queue/deferred/flush', methods=['POST'])
@login_required
def postfix_flush_deferred():
    """Flush the deferred queue."""
    try:
        logger.info(f"Deferred queue flush requested by user {current_user.id}")
        
        postfix_manager = PostfixManager()
        success = postfix_manager.flush_deferred_queue()
        
        if success:
            # Log the action
            try:
                audit_log = AuditLog(
                    user_id=current_user.id,
                    action='flush_deferred_queue',
                    resource_type='postfix_queue',
                    resource_id='deferred',
                    details='Flushed deferred queue',
                    ip_address=request.remote_addr
                )
                db.session.add(audit_log)
                db.session.commit()
            except Exception as db_error:
                logger.error(f"Failed to create audit log: {db_error}")
            
            return jsonify({
                'success': True,
                'message': 'Deferred queue flushed successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to flush deferred queue'
            }), 500
    except Exception as e:
        logger.error(f"Error in postfix_flush_deferred: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/postfix/queue/hold/flush', methods=['POST'])
@login_required
def postfix_flush_hold():
    """Flush the hold queue."""
    try:
        logger.info(f"Hold queue flush requested by user {current_user.id}")
        
        postfix_manager = PostfixManager()
        success = postfix_manager.flush_hold_queue()
        
        if success:
            # Log the action
            try:
                audit_log = AuditLog(
                    user_id=current_user.id,
                    action='flush_hold_queue',
                    resource_type='postfix_queue',
                    resource_id='hold',
                    details='Flushed hold queue',
                    ip_address=request.remote_addr
                )
                db.session.add(audit_log)
                db.session.commit()
            except Exception as db_error:
                logger.error(f"Failed to create audit log: {db_error}")
            
            return jsonify({
                'success': True,
                'message': 'Hold queue flushed successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to flush hold queue'
            }), 500
    except Exception as e:
        logger.error(f"Error in postfix_flush_hold: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/postfix/queue/cleanup', methods=['POST'])
@login_required
def postfix_cleanup_queue():
    """Clean up expired messages from the queue."""
    try:
        logger.info(f"Queue cleanup requested by user {current_user.id}")
        
        postfix_manager = PostfixManager()
        success = postfix_manager.cleanup_expired_messages()
        
        if success:
            # Log the action
            try:
                audit_log = AuditLog(
                    user_id=current_user.id,
                    action='cleanup_queue',
                    resource_type='postfix_queue',
                    resource_id='cleanup',
                    details='Cleaned up expired messages from queue',
                    ip_address=request.remote_addr
                )
                db.session.add(audit_log)
                db.session.commit()
            except Exception as db_error:
                logger.error(f"Failed to create audit log: {db_error}")
            
            return jsonify({
                'success': True,
                'message': 'Queue cleanup completed successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to cleanup queue'
            }), 500
    except Exception as e:
        logger.error(f"Error in postfix_cleanup_queue: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/postfix/queue/rebuild', methods=['POST'])
@login_required
def postfix_rebuild_queue():
    """Rebuild the queue index."""
    try:
        logger.info(f"Queue rebuild requested by user {current_user.id}")
        
        postfix_manager = PostfixManager()
        success = postfix_manager.rebuild_queue_index()
        
        if success:
            # Log the action
            try:
                audit_log = AuditLog(
                    user_id=current_user.id,
                    action='rebuild_queue',
                    resource_type='postfix_queue',
                    resource_id='rebuild',
                    details='Rebuilt queue index',
                    ip_address=request.remote_addr
                )
                db.session.add(audit_log)
                db.session.commit()
            except Exception as db_error:
                logger.error(f"Failed to create audit log: {db_error}")
            
            return jsonify({
                'success': True,
                'message': 'Queue index rebuilt successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to rebuild queue index'
            }), 500
    except Exception as e:
        logger.error(f"Error in postfix_rebuild_queue: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/postfix/queue/integrity', methods=['POST'])
@login_required
def postfix_check_queue_integrity():
    """Check queue integrity."""
    try:
        logger.info(f"Queue integrity check requested by user {current_user.id}")
        
        postfix_manager = PostfixManager()
        result = postfix_manager.check_queue_integrity()
        
        return jsonify({
            'success': True,
            'result': result
        })
    except Exception as e:
        logger.error(f"Error in postfix_check_queue_integrity: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/queue')
@login_required
def queue_management():
    """Mail queue management page."""
    return render_template('modules/mail/queue.html', title='Mail Queue Management')


@bp.route('/postfix/flush-queue', methods=['POST'])
@login_required
def postfix_flush_queue():
    """Flush Postfix mail queue."""
    try:
        logger.info(f"Postfix queue flush requested by user {current_user.id}")
        
        postfix_manager = PostfixManager()
        success = postfix_manager.flush_queue()
        
        if success:
            # Log the action
            try:
                audit_log = AuditLog(
                    user_id=current_user.id,
                    action='flush_postfix_queue',
                    resource_type='postfix_queue',
                    resource_id='queue',
                    details='Flushed Postfix mail queue',
                    ip_address=request.remote_addr
                )
                db.session.add(audit_log)
                db.session.commit()
                logger.info(f"Audit log created for queue flush by user {current_user.id}")
            except Exception as db_error:
                logger.error(f"Failed to create audit log: {db_error}")
                # Don't fail the operation if audit logging fails
            
            return jsonify({
                'success': True,
                'message': 'Mail queue flushed successfully'
            })
        else:
            logger.warning(f"Postfix queue flush failed for user {current_user.id}")
            return jsonify({
                'success': False,
                'message': 'Failed to flush mail queue'
            }), 500
    except Exception as e:
        logger.error(f"Error in postfix_flush_queue: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/postfix/add-domain', methods=['POST'])
@login_required
def postfix_add_domain():
    """Add domain to Postfix virtual domains."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No JSON data provided'
            }), 400
        
        domain = data.get('domain', '').strip()
        
        if not domain:
            return jsonify({
                'success': False,
                'message': 'Domain name is required'
            }), 400
        
        logger.info(f"Adding domain {domain} to Postfix by user {current_user.id}")
        
        postfix_manager = PostfixManager()
        success = postfix_manager.add_domain(domain)
        
        if success:
            # Log the action
            try:
                audit_log = AuditLog(
                    user_id=current_user.id,
                    action='add_postfix_domain',
                    resource_type='postfix_domain',
                    resource_id=domain,
                    details=f'Added domain to Postfix: {domain}',
                    ip_address=request.remote_addr
                )
                db.session.add(audit_log)
                db.session.commit()
                logger.info(f"Audit log created for domain addition by user {current_user.id}")
            except Exception as db_error:
                logger.error(f"Failed to create audit log: {db_error}")
                # Don't fail the operation if audit logging fails
            
            return jsonify({
                'success': True,
                'message': f'Domain {domain} added to Postfix successfully'
            })
        else:
            logger.warning(f"Failed to add domain {domain} to Postfix by user {current_user.id}")
            return jsonify({
                'success': False,
                'message': f'Failed to add domain {domain} to Postfix'
            }), 500
    except Exception as e:
        logger.error(f"Error in postfix_add_domain: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/postfix/remove-domain', methods=['POST'])
@login_required
def postfix_remove_domain():
    """Remove domain from Postfix virtual domains."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No JSON data provided'
            }), 400
        
        domain = data.get('domain', '').strip()
        
        if not domain:
            return jsonify({
                'success': False,
                'message': 'Domain name is required'
            }), 400
        
        logger.info(f"Removing domain {domain} from Postfix by user {current_user.id}")
        
        postfix_manager = PostfixManager()
        success = postfix_manager.remove_domain(domain)
        
        if success:
            # Log the action
            try:
                audit_log = AuditLog(
                    user_id=current_user.id,
                    action='remove_postfix_domain',
                    resource_type='postfix_domain',
                    resource_id=domain,
                    details=f'Removed domain from Postfix: {domain}',
                    ip_address=request.remote_addr
                )
                db.session.add(audit_log)
                db.session.commit()
                logger.info(f"Audit log created for domain removal by user {current_user.id}")
            except Exception as db_error:
                logger.error(f"Failed to create audit log: {db_error}")
                # Don't fail the operation if audit logging fails
            
            return jsonify({
                'success': True,
                'message': f'Domain {domain} removed from Postfix successfully'
            })
        else:
            logger.warning(f"Failed to remove domain {domain} from Postfix by user {current_user.id}")
            return jsonify({
                'success': False,
                'message': f'Failed to remove domain {domain} from Postfix'
            }), 500
    except Exception as e:
        logger.error(f"Error in postfix_remove_domain: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/postfix/domains')
@login_required
def postfix_get_domains():
    """Get list of Postfix virtual domains."""
    try:
        postfix_manager = PostfixManager()
        domains = postfix_manager.get_virtual_domains()
        
        return jsonify({
            'success': True,
            'domains': domains
        })
    except Exception as e:
        logger.error(f"Error in postfix_get_domains: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/dovecot/status')
@login_required
def dovecot_status():
    """Get Dovecot service status."""
    try:
        status = PostfixManager.get_dovecot_status()
        return jsonify({
            'success': True,
            'status': status
        })
    except Exception as e:
        logger.error(f"Error in dovecot_status: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/dovecot/restart', methods=['POST'])
@login_required
def dovecot_restart():
    """Restart Dovecot service."""
    try:
        logger.info(f"Dovecot restart requested by user {current_user.id}")
        
        dovecot_manager = DovecotManager()
        success = dovecot_manager.restart_service()
        
        if success:
            # Log the action
            try:
                audit_log = AuditLog(
                    user_id=current_user.id,
                    action='restart_dovecot',
                    resource_type='dovecot_service',
                    resource_id='service',
                    details='Restarted Dovecot service',
                    ip_address=request.remote_addr
                )
                db.session.add(audit_log)
                db.session.commit()
                logger.info(f"Audit log created for Dovecot restart by user {current_user.id}")
            except Exception as db_error:
                logger.error(f"Failed to create audit log: {db_error}")
                # Don't fail the operation if audit logging fails
            
            return jsonify({
                'success': True,
                'message': 'Dovecot service restarted successfully'
            })
        else:
            logger.warning(f"Dovecot restart failed for user {current_user.id}")
            return jsonify({
                'success': False,
                'message': 'Failed to restart Dovecot service'
            }), 500
    except Exception as e:
        logger.error(f"Error in dovecot_restart: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/dovecot/reload', methods=['POST'])
@login_required
def dovecot_reload():
    """Reload Dovecot configuration."""
    try:
        logger.info(f"Dovecot reload requested by user {current_user.id}")
        
        dovecot_manager = DovecotManager()
        success = dovecot_manager.reload_config()
        
        if success:
            # Log the action
            try:
                audit_log = AuditLog(
                    user_id=current_user.id,
                    action='reload_dovecot_config',
                    resource_type='dovecot_config',
                    resource_id='config',
                    details='Reloaded Dovecot configuration',
                    ip_address=request.remote_addr
                )
                db.session.add(audit_log)
                db.session.commit()
                logger.info(f"Audit log created for Dovecot reload by user {current_user.id}")
            except Exception as db_error:
                logger.error(f"Failed to create audit log: {db_error}")
                # Don't fail the operation if audit logging fails
            
            return jsonify({
                'success': True,
                'message': 'Dovecot configuration reloaded successfully'
            })
        else:
            logger.warning(f"Dovecot reload failed for user {current_user.id}")
            return jsonify({
                'success': False,
                'message': 'Failed to reload Dovecot configuration'
            }), 500
    except Exception as e:
        logger.error(f"Error in dovecot_reload: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/dovecot/check-config', methods=['POST'])
@login_required
def dovecot_check_config():
    """Check Dovecot configuration syntax."""
    try:
        logger.info(f"Dovecot config check requested by user {current_user.id}")
        
        dovecot_manager = DovecotManager()
        result = dovecot_manager.check_config()
        
        return jsonify({
            'success': True,
            'result': result
        })
    except Exception as e:
        logger.error(f"Error in dovecot_check_config: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/dovecot/user-info/<username>/<domain>')
@login_required
def dovecot_user_info(username, domain):
    """Get Dovecot user information."""
    try:
        dovecot_manager = DovecotManager()
        user_info = dovecot_manager.get_user_info(username, domain)
        
        return jsonify({
            'success': True,
            'user_info': user_info
        })
    except Exception as e:
        logger.error(f"Error in dovecot_user_info: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/statistics')
@login_required
def mail_statistics():
    """Get comprehensive mail statistics."""
    try:
        postfix_manager = PostfixManager()
        dovecot_manager = DovecotManager()
        
        # Get basic service status
        postfix_status = postfix_manager.get_status()
        dovecot_status = postfix_manager.get_dovecot_status()
        
        # Get queue information
        queue_info = postfix_manager.get_queue_info()
        
        # Get domain information
        domains = postfix_manager.get_virtual_domains()
        
        # Calculate statistics
        stats = {
            'services': {
                'postfix': postfix_status,
                'dovecot': dovecot_status
            },
            'queue': queue_info,
            'domains': {
                'total': len(domains),
                'list': domains
            },
            'system': {
                'timestamp': time.time(),
                'uptime': _get_system_uptime()
            }
        }
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        logger.error(f"Error in mail_statistics: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/system/monitoring')
@login_required
def system_monitoring():
    """Get system monitoring data."""
    try:
        import psutil
        
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Get network statistics
        network = psutil.net_io_counters()
        
        # Get process information for mail services
        mail_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                if proc.info['name'] in ['postfix', 'dovecot', 'master', 'qmgr']:
                    mail_processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        monitoring_data = {
            'cpu': {
                'percent': cpu_percent,
                'count': psutil.cpu_count(),
                'frequency': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
            },
            'memory': {
                'total': memory.total,
                'available': memory.available,
                'percent': memory.percent,
                'used': memory.used
            },
            'disk': {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': (disk.used / disk.total) * 100
            },
            'network': {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv
            },
            'mail_processes': mail_processes,
            'timestamp': time.time()
        }
        
        return jsonify({
            'success': True,
            'monitoring': monitoring_data
        })
    except ImportError:
        return jsonify({
            'success': False,
            'message': 'psutil library not available for system monitoring'
        }), 500
    except Exception as e:
        logger.error(f"Error in system_monitoring: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/postfix/logs')
@login_required
def postfix_logs():
    """Get recent Postfix logs."""
    try:
        import subprocess
        
        # Get recent Postfix logs (last 100 lines)
        try:
            result = subprocess.run(['journalctl', '-u', 'postfix', '-n', '100', '--no-pager'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                logs = result.stdout
            else:
                # Fallback to log file
                result = subprocess.run(['tail', '-n', '100', '/var/log/mail.log'], 
                                      capture_output=True, text=True, timeout=30)
                logs = result.stdout if result.returncode == 0 else "Unable to retrieve logs"
        except:
            logs = "Log retrieval not available on this system"
        
        return jsonify({
            'success': True,
            'logs': logs
        })
    except Exception as e:
        logger.error(f"Error in postfix_logs: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/dovecot/logs')
@login_required
def dovecot_logs():
    """Get recent Dovecot logs."""
    try:
        import subprocess
        
        # Get recent Dovecot logs (last 100 lines)
        try:
            result = subprocess.run(['journalctl', '-u', 'dovecot', '-n', '100', '--no-pager'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                logs = result.stdout
            else:
                # Fallback to log file
                result = subprocess.run(['tail', '-n', '100', '/var/log/dovecot.log'], 
                                      capture_output=True, text=True, timeout=30)
                logs = result.stdout if result.returncode == 0 else "Unable to retrieve logs"
        except:
            logs = "Log retrieval not available on this system"
        
        return jsonify({
            'success': True,
            'logs': logs
        })
    except Exception as e:
        logger.error(f"Error in dovecot_logs: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/dovecot/config/info')
@login_required
def dovecot_config_info():
    """Get Dovecot configuration information."""
    try:
        dovecot_manager = DovecotManager()
        config_info = dovecot_manager.get_config_info()
        
        return jsonify({
            'success': True,
            'config': config_info
        })
    except Exception as e:
        logger.error(f"Error in dovecot_config_info: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/dovecot/config/backup', methods=['POST'])
@login_required
def dovecot_backup_config():
    """Create a backup of Dovecot configuration."""
    try:
        logger.info(f"Dovecot config backup requested by user {current_user.id}")
        
        dovecot_manager = DovecotManager()
        result = dovecot_manager.backup_config()
        
        if result.get('success'):
            # Log the action
            try:
                audit_log = AuditLog(
                    user_id=current_user.id,
                    action='backup_dovecot_config',
                    resource_type='dovecot_config',
                    resource_id='backup',
                    details=f'Created Dovecot configuration backup: {result.get("backup_file")}',
                    ip_address=request.remote_addr
                )
                db.session.add(audit_log)
                db.session.commit()
            except Exception as db_error:
                logger.error(f"Failed to create audit log: {db_error}")
            
            return jsonify({
                'success': True,
                'message': 'Configuration backup created successfully',
                'backup_file': result.get('backup_file')
            })
        else:
            return jsonify({
                'success': False,
                'message': result.get('error', 'Failed to create backup')
            }), 500
    except Exception as e:
        logger.error(f"Error in dovecot_backup_config: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/dovecot/users/statistics')
@login_required
def dovecot_user_statistics():
    """Get Dovecot user statistics."""
    try:
        dovecot_manager = DovecotManager()
        stats = dovecot_manager.get_user_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        logger.error(f"Error in dovecot_user_statistics: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/dovecot/protocols/status')
@login_required
def dovecot_protocol_status():
    """Get Dovecot protocol status."""
    try:
        dovecot_manager = DovecotManager()
        status = dovecot_manager.get_protocol_status()
        
        return jsonify({
            'success': True,
            'protocols': status
        })
    except Exception as e:
        logger.error(f"Error in dovecot_protocol_status: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/postfix/config/backup', methods=['POST'])
@login_required
def backup_postfix_config():
    """Create a backup of Postfix configuration."""
    try:
        import shutil
        import datetime
        
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = f"/tmp/postfix_backup_{timestamp}"
        
        # Create backup directory
        os.makedirs(backup_dir, exist_ok=True)
        
        # Copy configuration files
        config_files = ['/etc/postfix/main.cf', '/etc/postfix/master.cf']
        for config_file in config_files:
            if os.path.exists(config_file):
                shutil.copy2(config_file, backup_dir)
        
        # Create archive
        archive_name = f"/tmp/postfix_config_backup_{timestamp}.tar.gz"
        shutil.make_archive(archive_name.replace('.tar.gz', ''), 'gztar', backup_dir)
        
        # Clean up temporary directory
        shutil.rmtree(backup_dir)
        
        # Log the action
        try:
            audit_log = AuditLog(
                user_id=current_user.id,
                action='backup_postfix_config',
                resource_type='postfix_config',
                resource_id='backup',
                details=f'Created Postfix configuration backup: {archive_name}',
                ip_address=request.remote_addr
            )
            db.session.add(audit_log)
            db.session.commit()
            logger.info(f"Audit log created for config backup by user {current_user.id}")
        except Exception as db_error:
            logger.error(f"Failed to create audit log: {db_error}")
        
        return jsonify({
            'success': True,
            'message': f'Configuration backup created: {archive_name}',
            'backup_file': archive_name
        })
    except Exception as e:
        logger.error(f"Error in backup_postfix_config: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


def _get_system_uptime():
    """Get system uptime information."""
    try:
        import subprocess
        result = subprocess.run(['uptime', '-p'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return "Unknown"
    except:
        return "Unknown"
