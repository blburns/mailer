#!/usr/bin/env python3
"""
Quick Test Data Script for Postfix Manager

This script creates minimal but realistic test data for quick testing.
It's designed to be fast and create just enough data to test the system.

Usage:
    python scripts/quick_test_data.py [--clear]
"""

import os
import sys
from pathlib import Path

# Get the project root directory (parent of scripts directory)
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent

# Add the project root to Python path
sys.path.insert(0, str(PROJECT_ROOT))

# Also add the app directory specifically
sys.path.insert(0, str(PROJECT_ROOT / 'app'))

# Set environment variables
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_APP'] = 'app'

try:
    from app import create_app
    from app.extensions import db
    from app.models import User, UserRole, MailDomain, MailUser, SystemConfig, AuditLog
except ImportError as e:
    print(f"❌ Import error: {e}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"App directory: {PROJECT_ROOT / 'app'}")
    print("Please run this script from the project root directory.")
    sys.exit(1)


def create_quick_test_data(app, clear_existing=False):
    """Create quick test data for development."""
    with app.app_context():
        if clear_existing:
            print("Clearing existing data...")
            AuditLog.query.delete()
            MailUser.query.delete()
            MailDomain.query.delete()
            SystemConfig.query.delete()
            User.query.delete()
            db.session.commit()
            print("Existing data cleared.")
        
        print("Creating test data...")
        
        # 1. Create test users
        admin_user = User(
            username='admin',
            email='admin@example.com',
            password_hash='admin_hash',
            role=UserRole.ADMIN,
            is_active=True
        )
        
        regular_user = User(
            username='user1',
            email='user1@example.com',
            password_hash='user_hash',
            role=UserRole.USER,
            is_active=True
        )
        
        readonly_user = User(
            username='readonly',
            email='readonly@example.com',
            password_hash='readonly_hash',
            role=UserRole.READONLY,
            is_active=True
        )
        
        db.session.add_all([admin_user, regular_user, readonly_user])
        db.session.commit()
        print("✓ Created 3 test users")
        
        # 2. Create test domains
        domain1 = MailDomain(
            domain='example.com',
            is_active=True,
            postfix_enabled=True,
            dovecot_enabled=True,
            ldap_base_dn='dc=example,dc=com',
            ldap_admin_dn='cn=admin,dc=example,dc=com'
        )
        
        domain2 = MailDomain(
            domain='testdomain.org',
            is_active=True,
            postfix_enabled=True,
            dovecot_enabled=False,
            ldap_base_dn='dc=testdomain,dc=org',
            ldap_admin_dn='cn=admin,dc=testdomain,dc=org'
        )
        
        domain3 = MailDomain(
            domain='inactive.net',
            is_active=False,
            postfix_enabled=False,
            dovecot_enabled=False,
            ldap_base_dn='dc=inactive,dc=net',
            ldap_admin_dn='cn=admin,dc=inactive,dc=net'
        )
        
        db.session.add_all([domain1, domain2, domain3])
        db.session.commit()
        print("✓ Created 3 test domains")
        
        # 3. Create test mail users
        mail_user1 = MailUser(
            username='john',
            domain_id=domain1.id,
            password_hash='john_hash',
            is_active=True,
            quota=1073741824,  # 1GB
            home_dir='/home/john',
            ldap_dn='uid=john,dc=example,dc=com'
        )
        
        mail_user2 = MailUser(
            username='jane',
            domain_id=domain1.id,
            password_hash='jane_hash',
            is_active=True,
            quota=0,  # Unlimited
            home_dir='/home/jane',
            ldap_dn='uid=jane,dc=example,dc=com'
        )
        
        mail_user3 = MailUser(
            username='bob',
            domain_id=domain2.id,
            password_hash='bob_hash',
            is_active=True,
            quota=524288000,  # 500MB
            home_dir='/home/bob',
            ldap_dn='uid=bob,dc=testdomain,dc=org'
        )
        
        mail_user4 = MailUser(
            username='alice',
            domain_id=domain1.id,
            password_hash='alice_hash',
            is_active=False,
            quota=209715200,  # 200MB
            home_dir='/home/alice',
            ldap_dn='uid=alice,dc=example,dc=com'
        )
        
        db.session.add_all([mail_user1, mail_user2, mail_user3, mail_user4])
        db.session.commit()
        print("✓ Created 4 test mail users")
        
        # 4. Create essential system configurations
        essential_configs = [
            ('mail.max_message_size', '10485760', 'Maximum message size (10MB)'),
            ('mail.default_quota', '1073741824', 'Default user quota (1GB)'),
            ('mail.smtp_port', '587', 'SMTP submission port'),
            ('mail.imap_port', '993', 'IMAPS port'),
            ('ldap.server', 'localhost', 'LDAP server address'),
            ('ldap.port', '389', 'LDAP server port'),
            ('system.backup_enabled', 'true', 'Enable automatic backups'),
            ('system.monitoring_enabled', 'true', 'Enable system monitoring')
        ]
        
        for key, value, description in essential_configs:
            config = SystemConfig(key=key, value=value, description=description)
            db.session.add(config)
        
        db.session.commit()
        print("✓ Created 8 system configurations")
        
        # 5. Create sample audit logs
        audit_actions = [
            ('create_domain', 'mail_domain', 'example.com', 'Created new mail domain'),
            ('create_user', 'mail_user', 'john', 'Created new mail user'),
            ('restart_postfix', 'service', 'postfix', 'Restarted Postfix service'),
            ('update_quota', 'mail_user', 'jane', 'Updated user quota to unlimited'),
            ('backup_config', 'backup', 'config_backup', 'Created configuration backup'),
            ('test_connection', 'connection', 'ldap', 'Tested LDAP connection'),
            ('enable_service', 'service', 'dovecot', 'Enabled Dovecot service'),
            ('update_domain', 'mail_domain', 'testdomain.org', 'Updated domain settings')
        ]
        
        for action, resource_type, resource_id, details in audit_actions:
            log = AuditLog(
                user_id=admin_user.id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                details=details,
                ip_address='192.168.1.100'
            )
            db.session.add(log)
        
        db.session.commit()
        print("✓ Created 8 audit log entries")
        
        print("\n🎉 Test data creation completed successfully!")
        print(f"Total records created: {3 + 3 + 4 + 8 + 8} = 26 records")


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Create quick test data for Postfix Manager')
    parser.add_argument('--clear', action='store_true', help='Clear existing data before creating test data')
    
    args = parser.parse_args()
    
    try:
        print(f"🚀 Starting Postfix Manager quick test data creator...")
        print(f"Project root: {PROJECT_ROOT}")
        
        # Create Flask app (no arguments needed)
        app = create_app()
        print("✅ Flask app created successfully")
        
        # Create test data
        create_quick_test_data(app, clear_existing=args.clear)
        
    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
