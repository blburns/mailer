"""
System Management Routes

Handles system-wide functionality including configuration, logging, and monitoring.
"""

from flask import render_template, request, jsonify
from flask_login import login_required, current_user
from app.modules.system import bp
from app.models import SystemConfig, AuditLog
from app.extensions import db
from app.utils.navigation import set_system_breadcrumbs
from app.utils.mail_manager import PostfixManager
from app.utils.ldap_manager import LDAPManager
import json
from datetime import datetime


@bp.route('/')
@login_required
def index():
    """System management dashboard."""
    set_system_breadcrumbs('System', request.path)
    
    # Get system status
    try:
        postfix_status = PostfixManager.get_status()
        dovecot_status = PostfixManager.get_dovecot_status()
        ldap_status = LDAPManager.get_status()
    except Exception as e:
        postfix_status = {'status': 'error', 'message': str(e)}
        dovecot_status = {'status': 'error', 'message': str(e)}
        ldap_status = {'status': 'error', 'message': str(e)}
    
    # Get system statistics
    total_configs = SystemConfig.query.count()
    recent_logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(5).all()
    
    return render_template('modules/system/index.html',
                         title='System Management',
                         postfix_status=postfix_status,
                         dovecot_status=dovecot_status,
                         ldap_status=ldap_status,
                         total_configs=total_configs,
                         recent_logs=recent_logs)


@bp.route('/configuration')
@login_required
def configuration():
    """System configuration management."""
    set_system_breadcrumbs('Configuration', request.path)
    configs = SystemConfig.query.all()
    return render_template('modules/system/configuration.html', title='System Configuration', configs=configs)


@bp.route('/configuration/new', methods=['GET', 'POST'])
@login_required
def new_config():
    """Create new system configuration."""
    set_system_breadcrumbs('New Configuration', request.path)
    
    if request.method == 'POST':
        data = request.get_json()
        
        key = data.get('key', '').strip()
        value = data.get('value', '').strip()
        description = data.get('description', '').strip()
        
        if not key or not value:
            return jsonify({'success': False, 'message': 'Key and value are required'})
        
        # Check if config already exists
        if SystemConfig.query.filter_by(key=key).first():
            return jsonify({'success': False, 'message': 'Configuration key already exists'})
        
        # Create configuration
        config = SystemConfig(
            key=key,
            value=value,
            description=description
        )
        
        try:
            db.session.add(config)
            db.session.commit()
            
            # Log the action
            audit_log = AuditLog(
                user_id=current_user.id,
                action='create_config',
                resource_type='system_config',
                resource_id=str(config.id),
                details=f'Created configuration: {key} = {value}',
                ip_address=request.remote_addr
            )
            db.session.add(audit_log)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Configuration created successfully'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Error creating configuration: {str(e)}'})
    
    return render_template('modules/system/new_config.html', title='New Configuration')


@bp.route('/configuration/<int:config_id>', methods=['GET', 'POST', 'DELETE'])
@login_required
def config_detail(config_id):
    """View and edit system configuration."""
    config = SystemConfig.query.get_or_404(config_id)
    
    if request.method == 'POST':
        data = request.get_json()
        action = data.get('action')
        
        if action == 'update':
            new_value = data.get('value', '').strip()
            new_description = data.get('description', '').strip()
            
            if not new_value:
                return jsonify({'success': False, 'message': 'Value is required'})
            
            old_value = config.value
            config.value = new_value
            config.description = new_description
            
            try:
                db.session.commit()
                
                # Log the action
                audit_log = AuditLog(
                    user_id=current_user.id,
                    action='update_config',
                    resource_type='system_config',
                    resource_id=str(config.id),
                    details=f'Updated configuration: {config.key} from "{old_value}" to "{new_value}"',
                    ip_address=request.remote_addr
                )
                db.session.add(audit_log)
                db.session.commit()
                
                return jsonify({'success': True, 'message': 'Configuration updated successfully'})
            except Exception as e:
                db.session.rollback()
                return jsonify({'success': False, 'message': f'Error updating configuration: {str(e)}'})
        
        elif action == 'delete':
            try:
                key_name = config.key
                db.session.delete(config)
                db.session.commit()
                
                # Log the action
                audit_log = AuditLog(
                    user_id=current_user.id,
                    action='delete_config',
                    resource_type='system_config',
                    resource_id=str(config_id),
                    details=f'Deleted configuration: {key_name}',
                    ip_address=request.remote_addr
                )
                db.session.add(audit_log)
                db.session.commit()
                
                return jsonify({'success': True, 'message': 'Configuration deleted successfully'})
            except Exception as e:
                db.session.rollback()
                return jsonify({'success': False, 'message': f'Error deleting configuration: {str(e)}'})
    
    set_system_breadcrumbs('Configuration Detail', request.path)
    return render_template('modules/system/config_detail.html', title=f'Configuration: {config.key}', config=config)


@bp.route('/logs')
@login_required
def logs():
    """Audit logs management."""
    set_system_breadcrumbs('Audit Logs', request.path)
    page = request.args.get('page', 1, type=int)
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).paginate(
        page=page, per_page=50, error_out=False)
    return render_template('modules/system/logs.html', title='Audit Logs', logs=logs)


@bp.route('/logs/<int:log_id>')
@login_required
def log_detail(log_id):
    """View audit log details."""
    log = AuditLog.query.get_or_404(log_id)
    set_system_breadcrumbs('Log Detail', request.path)
    return render_template('modules/system/log_detail.html', title='Audit Log Detail', log=log)


@bp.route('/status')
@login_required
def status():
    """System status and health checks."""
    set_system_breadcrumbs('System Status', request.path)
    
    # Get comprehensive system status
    try:
        postfix_status = PostfixManager.get_status()
        dovecot_status = PostfixManager.get_dovecot_status()
        ldap_status = LDAPManager.get_status()
        
        # Additional system checks could be added here
        system_status = {
            'database': 'healthy',  # Placeholder for actual DB health check
            'disk_space': 'healthy',  # Placeholder for disk space check
            'memory': 'healthy',      # Placeholder for memory check
        }
        
    except Exception as e:
        postfix_status = {'status': 'error', 'message': str(e)}
        dovecot_status = {'status': 'error', 'message': str(e)}
        ldap_status = {'status': 'error', 'message': str(e)}
        system_status = {'status': 'error', 'message': str(e)}
    
    return render_template('modules/system/status.html', 
                         title='System Status',
                         postfix_status=postfix_status,
                         dovecot_status=dovecot_status,
                         ldap_status=ldap_status,
                         system_status=system_status)


@bp.route('/api/status')
@login_required
def api_status():
    """API endpoint for system status."""
    try:
        postfix_status = PostfixManager.get_status()
        dovecot_status = PostfixManager.get_dovecot_status()
        ldap_status = LDAPManager.get_status()
        
        return jsonify({
            'success': True,
            'status': {
                'postfix': postfix_status,
                'dovecot': dovecot_status,
                'ldap': ldap_status,
                'timestamp': datetime.utcnow().isoformat()
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
