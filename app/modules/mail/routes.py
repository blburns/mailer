"""
Mail Management Routes
"""

from flask import render_template, request, jsonify, flash
from flask_login import login_required, current_user
from app.modules.mail import bp
from app.models import AuditLog
from app.extensions import db
from app.utils.mail_manager import PostfixManager, DovecotManager
import json


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
        return jsonify({
            'success': False,
            'message': str(e)
        })


@bp.route('/postfix/restart', methods=['POST'])
@login_required
def postfix_restart():
    """Restart Postfix service."""
    try:
        postfix_manager = PostfixManager()
        success = postfix_manager.restart_service()
        
        if success:
            # Log the action
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
            
            return jsonify({
                'success': True,
                'message': 'Postfix service restarted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to restart Postfix service'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })


@bp.route('/postfix/reload', methods=['POST'])
@login_required
def postfix_reload():
    """Reload Postfix configuration."""
    try:
        postfix_manager = PostfixManager()
        success = postfix_manager.reload_config()
        
        if success:
            # Log the action
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
            
            return jsonify({
                'success': True,
                'message': 'Postfix configuration reloaded successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to reload Postfix configuration'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })


@bp.route('/postfix/check-config', methods=['POST'])
@login_required
def postfix_check_config():
    """Check Postfix configuration syntax."""
    try:
        postfix_manager = PostfixManager()
        result = postfix_manager.check_config()
        
        return jsonify({
            'success': True,
            'result': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })


@bp.route('/postfix/queue')
@login_required
def postfix_queue():
    """Get Postfix queue information."""
    try:
        postfix_manager = PostfixManager()
        queue_info = postfix_manager.get_queue_info()
        
        return jsonify({
            'success': True,
            'queue': queue_info
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })


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
        postfix_manager = PostfixManager()
        success = postfix_manager.flush_queue()
        
        if success:
            # Log the action
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
            
            return jsonify({
                'success': True,
                'message': 'Mail queue flushed successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to flush mail queue'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })


@bp.route('/postfix/add-domain', methods=['POST'])
@login_required
def postfix_add_domain():
    """Add domain to Postfix virtual domains."""
    try:
        data = request.get_json()
        domain = data.get('domain', '').strip()
        
        if not domain:
            return jsonify({
                'success': False,
                'message': 'Domain name is required'
            })
        
        postfix_manager = PostfixManager()
        success = postfix_manager.add_domain(domain)
        
        if success:
            # Log the action
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
            
            return jsonify({
                'success': True,
                'message': f'Domain {domain} added to Postfix successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Failed to add domain {domain} to Postfix'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })


@bp.route('/postfix/remove-domain', methods=['POST'])
@login_required
def postfix_remove_domain():
    """Remove domain from Postfix virtual domains."""
    try:
        data = request.get_json()
        domain = data.get('domain', '').strip()
        
        if not domain:
            return jsonify({
                'success': False,
                'message': 'Domain name is required'
            })
        
        postfix_manager = PostfixManager()
        success = postfix_manager.remove_domain(domain)
        
        if success:
            # Log the action
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
            
            return jsonify({
                'success': True,
                'message': f'Domain {domain} removed from Postfix successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Failed to remove domain {domain} from Postfix'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })


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
        return jsonify({
            'success': False,
            'message': str(e)
        })


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
        return jsonify({
            'success': False,
            'message': str(e)
        })


@bp.route('/dovecot/restart', methods=['POST'])
@login_required
def dovecot_restart():
    """Restart Dovecot service."""
    try:
        dovecot_manager = DovecotManager()
        success = dovecot_manager.restart_service()
        
        if success:
            # Log the action
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
            
            return jsonify({
                'success': True,
                'message': 'Dovecot service restarted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to restart Dovecot service'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })


@bp.route('/dovecot/reload', methods=['POST'])
@login_required
def dovecot_reload():
    """Reload Dovecot configuration."""
    try:
        dovecot_manager = DovecotManager()
        success = dovecot_manager.reload_config()
        
        if success:
            # Log the action
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
            
            return jsonify({
                'success': True,
                'message': 'Dovecot configuration reloaded successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to reload Dovecot configuration'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })


@bp.route('/dovecot/check-config', methods=['POST'])
@login_required
def dovecot_check_config():
    """Check Dovecot configuration syntax."""
    try:
        dovecot_manager = DovecotManager()
        result = dovecot_manager.check_config()
        
        return jsonify({
            'success': True,
            'result': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })


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
        return jsonify({
            'success': False,
            'message': str(e)
        })
