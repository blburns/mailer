"""
LDAP Management Routes
"""

from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.modules.ldap import bp
from app.models import AuditLog
from app.extensions import db
from app.utils.ldap_manager import LDAPManager
from app.utils.mail_manager import PostfixManager
from app.utils.navigation import set_ldap_breadcrumbs
import json
import os


@bp.route('/')
@login_required
def index():
    """LDAP management dashboard."""
    set_ldap_breadcrumbs()
    return render_template('modules/ldap/index.html', title='LDAP Management')


@bp.route('/browser')
@login_required
def browser():
    """LDAP directory browser."""
    set_ldap_breadcrumbs('Directory Browser', request.path)
    return render_template('modules/ldap/browser.html', title='LDAP Browser')


@bp.route('/search', methods=['POST'])
@login_required
def search():
    """Search LDAP directory."""
    try:
        data = request.get_json()
        base_dn = data.get('base_dn', '')
        search_filter = data.get('filter', '(objectClass=*)')
        attributes = data.get('attributes', ['*'])
        
        # Initialize LDAP manager
        ldap_manager = LDAPManager()
        
        # Perform search
        results = ldap_manager.search(base_dn, search_filter, attributes)
        
        return jsonify({
            'success': True,
            'results': results,
            'count': len(results)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })


@bp.route('/tree')
@login_required
def get_tree():
    """Get LDAP directory tree structure."""
    try:
        data = request.get_json()
        base_dn = data.get('base_dn', 'dc=example,dc=tld')
        
        # Initialize LDAP manager
        ldap_manager = LDAPManager()
        
        # Get tree structure
        tree = ldap_manager.get_directory_tree(base_dn)
        
        return jsonify({
            'success': True,
            'tree': tree
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })


@bp.route('/entry/<path:dn>')
@login_required
def get_entry(dn):
    """Get LDAP entry details."""
    try:
        # Initialize LDAP manager
        ldap_manager = LDAPManager()
        
        # Search for the specific entry
        results = ldap_manager.search(dn, '(objectClass=*)', ['*'])
        
        if results:
            return jsonify({
                'success': True,
                'entry': results[0]
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Entry not found'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })


@bp.route('/entry/<path:dn>', methods=['PUT'])
@login_required
def update_entry(dn):
    """Update LDAP entry."""
    try:
        data = request.get_json()
        changes = data.get('changes', {})
        
        # Initialize LDAP manager
        ldap_manager = LDAPManager()
        
        # Update entry
        success = ldap_manager.modify_entry(dn, changes)
        
        if success:
            # Log the action
            audit_log = AuditLog(
                user_id=current_user.id,
                action='update_ldap_entry',
                resource_type='ldap_entry',
                resource_id=dn,
                details=f'Updated LDAP entry: {dn}',
                ip_address=request.remote_addr
            )
            db.session.add(audit_log)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Entry updated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to update entry'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })


@bp.route('/entry/<path:dn>', methods=['DELETE'])
@login_required
def delete_entry(dn):
    """Delete LDAP entry."""
    try:
        # Initialize LDAP manager
        ldap_manager = LDAPManager()
        
        # Delete entry
        success = ldap_manager.delete_entry(dn)
        
        if success:
            # Log the action
            audit_log = AuditLog(
                user_id=current_user.id,
                action='delete_ldap_entry',
                resource_type='ldap_entry',
                resource_id=dn,
                details=f'Deleted LDAP entry: {dn}',
                ip_address=request.remote_addr
            )
            db.session.add(audit_log)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Entry deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to delete entry'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })


@bp.route('/add-entry', methods=['POST'])
@login_required
def add_entry():
    """Add new LDAP entry."""
    try:
        data = request.get_json()
        parent_dn = data.get('parent_dn', '')
        attributes = data.get('attributes', {})
        
        # Calculate new DN
        rdn = attributes.get('cn', attributes.get('ou', attributes.get('dc', 'new')))
        new_dn = f"{rdn},{parent_dn}"
        
        # Initialize LDAP manager
        ldap_manager = LDAPManager()
        
        # Add entry
        success = ldap_manager.add_entry(new_dn, attributes)
        
        if success:
            # Log the action
            audit_log = AuditLog(
                user_id=current_user.id,
                action='add_ldap_entry',
                resource_type='ldap_entry',
                resource_id=new_dn,
                details=f'Added LDAP entry: {new_dn}',
                ip_address=request.remote_addr
            )
            db.session.add(audit_log)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Entry added successfully',
                'dn': new_dn
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to add entry'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })


@bp.route('/backup', methods=['POST'])
@login_required
def backup_database():
    """Backup LDAP database."""
    try:
        data = request.get_json()
        backup_path = data.get('backup_path', '/tmp/ldap_backup.ldif')
        
        # Initialize LDAP manager
        ldap_manager = LDAPManager()
        
        # Perform backup
        success = ldap_manager.backup_database(backup_path)
        
        if success:
            # Log the action
            audit_log = AuditLog(
                user_id=current_user.id,
                action='backup_ldap_database',
                resource_type='ldap_database',
                resource_id='backup',
                details=f'Backed up LDAP database to: {backup_path}',
                ip_address=request.remote_addr
            )
            db.session.add(audit_log)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Database backed up successfully',
                'backup_path': backup_path
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to backup database'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })


@bp.route('/restore', methods=['POST'])
@login_required
def restore_database():
    """Restore LDAP database from backup."""
    try:
        data = request.get_json()
        backup_path = data.get('backup_path', '')
        
        if not backup_path or not os.path.exists(backup_path):
            return jsonify({
                'success': False,
                'message': 'Backup file not found'
            })
        
        # Initialize LDAP manager
        ldap_manager = LDAPManager()
        
        # Perform restore
        success = ldap_manager.restore_database(backup_path)
        
        if success:
            # Log the action
            audit_log = AuditLog(
                user_id=current_user.id,
                action='restore_ldap_database',
                resource_type='ldap_database',
                resource_id='restore',
                details=f'Restored LDAP database from: {backup_path}',
                ip_address=request.remote_addr
            )
            db.session.add(audit_log)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Database restored successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to restore database'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })


@bp.route('/status')
@login_required
def status():
    """Get LDAP service status."""
    try:
        # Initialize LDAP manager
        ldap_manager = LDAPManager()
        
        # Get status
        status_info = ldap_manager.get_status()
        
        return jsonify({
            'success': True,
            'status': status_info
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })


@bp.route('/test-connection', methods=['POST'])
@login_required
def test_connection():
    """Test LDAP connection."""
    try:
        data = request.get_json()
        server_uri = data.get('server_uri', 'ldap://127.0.0.1')
        admin_dn = data.get('admin_dn', 'cn=admin,dc=example,dc=tld')
        admin_password = data.get('admin_password', '')
        
        # Initialize LDAP manager with custom parameters
        ldap_manager = LDAPManager(server_uri, admin_dn, admin_password)
        
        # Test connection
        success = ldap_manager.test_connection()
        
        return jsonify({
            'success': True,
            'connected': success,
            'message': 'Connection successful' if success else 'Connection failed'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })
