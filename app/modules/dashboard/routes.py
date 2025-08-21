"""
Dashboard Routes
"""

from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.modules.dashboard import bp
from app.models import MailDomain, MailUser, SystemConfig, AuditLog
from app.extensions import db
from app.utils.mail_manager import PostfixManager
from app.utils.ldap_manager import LDAPManager
from datetime import datetime
import json


@bp.route('/')
@login_required
def index():
    """Main dashboard."""
    # Get system statistics
    total_domains = MailDomain.query.count()
    total_users = MailUser.query.count()
    active_domains = MailDomain.query.filter_by(is_active=True).count()
    active_users = MailUser.query.filter_by(is_active=True).count()
    
    # Get recent audit logs
    recent_logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(10).all()
    
    # Get system status
    try:
        postfix_status = PostfixManager.get_status()
        dovecot_status = PostfixManager.get_dovecot_status()
        ldap_status = LDAPManager.get_status()
    except Exception as e:
        postfix_status = {'status': 'error', 'message': str(e)}
        dovecot_status = {'status': 'error', 'message': str(e)}
        ldap_status = {'status': 'error', 'message': str(e)}
    
    return render_template('modules/dashboard/index.html',
                         title='Dashboard',
                         total_domains=total_domains,
                         total_users=total_users,
                         active_domains=active_domains,
                         active_users=active_users,
                         recent_logs=recent_logs,
                         postfix_status=postfix_status,
                         dovecot_status=dovecot_status,
                         ldap_status=ldap_status)


@bp.route('/domains')
@login_required
def domains():
    """Mail domains management."""
    domains = MailDomain.query.all()
    return render_template('modules/dashboard/domains.html', title='Mail Domains', domains=domains)


@bp.route('/domains/new', methods=['GET', 'POST'])
@login_required
def new_domain():
    """Create new mail domain."""
    if request.method == 'POST':
        data = request.get_json()
        
        # Validate domain
        domain_name = data.get('domain', '').strip()
        if not domain_name:
            return jsonify({'success': False, 'message': 'Domain name is required'})
        
        # Check if domain already exists
        if MailDomain.query.filter_by(domain=domain_name).first():
            return jsonify({'success': False, 'message': 'Domain already exists'})
        
        # Create domain
        domain = MailDomain(
            domain=domain_name,
            ldap_base_dn=f"dc={domain_name.split('.')[0]},dc={domain_name.split('.')[1]}",
            ldap_admin_dn=f"cn=admin,dc={domain_name.split('.')[0]},dc={domain_name.split('.')[1]}"
        )
        
        try:
            db.session.add(domain)
            db.session.commit()
            
            # Log the action
            audit_log = AuditLog(
                user_id=current_user.id,
                action='create_domain',
                resource_type='mail_domain',
                resource_id=str(domain.id),
                details=f'Created domain: {domain_name}',
                ip_address=request.remote_addr
            )
            db.session.add(audit_log)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Domain created successfully'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Error creating domain: {str(e)}'})
    
    return render_template('modules/dashboard/new_domain.html', title='New Domain')


@bp.route('/domains/<int:domain_id>')
@login_required
def domain_detail(domain_id):
    """Domain detail view."""
    domain = MailDomain.query.get_or_404(domain_id)
    users = MailUser.query.filter_by(domain_id=domain_id).all()
    return render_template('modules/dashboard/domain_detail.html', title=f'Domain: {domain.domain}', domain=domain, users=users)


@bp.route('/users')
@login_required
def users():
    """Mail users management."""
    users = MailUser.query.join(MailDomain).all()
    return render_template('modules/dashboard/users.html', title='Mail Users', users=users)


@bp.route('/users/new', methods=['GET', 'POST'])
@login_required
def new_user():
    """Create new mail user."""
    if request.method == 'POST':
        data = request.get_json()
        
        username = data.get('username', '').strip()
        domain_id = data.get('domain_id')
        password = data.get('password')
        quota = data.get('quota', 0)
        
        if not username or not domain_id or not password:
            return jsonify({'success': False, 'message': 'All fields are required'})
        
        domain = MailDomain.query.get(domain_id)
        if not domain:
            return jsonify({'success': False, 'message': 'Invalid domain'})
        
        # Check if user already exists
        if MailUser.query.filter_by(username=username, domain_id=domain_id).first():
            return jsonify({'success': False, 'message': 'User already exists in this domain'})
        
        # Create user
        from app.extensions import bcrypt
        user = MailUser(
            username=username,
            domain_id=domain_id,
            password_hash=bcrypt.generate_password_hash(password).decode('utf-8'),
            quota=quota,
            home_dir=f"/home/vmail/domains/{domain.domain}/{username}"
        )
        
        try:
            db.session.add(user)
            db.session.commit()
            
            # Log the action
            audit_log = AuditLog(
                user_id=current_user.id,
                action='create_user',
                resource_type='mail_user',
                resource_id=str(user.id),
                details=f'Created user: {username}@{domain.domain}',
                ip_address=request.remote_addr
            )
            db.session.add(audit_log)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'User created successfully'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Error creating user: {str(e)}'})
    
    domains = MailDomain.query.filter_by(is_active=True).all()
    return render_template('modules/dashboard/new_user.html', title='New User', domains=domains)


@bp.route('/system')
@login_required
def system():
    """System configuration."""
    configs = SystemConfig.query.all()
    return render_template('modules/dashboard/system.html', title='System Configuration', configs=configs)


@bp.route('/logs')
@login_required
def logs():
    """Audit logs."""
    page = request.args.get('page', 1, type=int)
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).paginate(
        page=page, per_page=50, error_out=False)
    return render_template('modules/dashboard/logs.html', title='Audit Logs', logs=logs)
