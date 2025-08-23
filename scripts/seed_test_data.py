#!/usr/bin/env python3
"""
Test Data Seeding Script for Postfix Manager

This script populates the database with realistic test data for development
and testing purposes. It creates domains, users, system configurations,
and audit logs to simulate a production-like environment.

Usage:
    python scripts/seed_test_data.py [--clear] [--verbose] [--count N]

Options:
    --clear     Clear existing data before seeding
    --verbose   Show detailed output
    --count N   Number of test records to create (default: 10)
"""

import os
import sys
import argparse
import random
import string
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Get the project root directory (parent of scripts directory)
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent

# Add the project root to Python path
sys.path.insert(0, str(PROJECT_ROOT))

# Also add the app directory specifically
sys.path.insert(0, str(PROJECT_ROOT / 'app'))

# Set environment variables for development
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_APP'] = 'app'
os.environ['ENV'] = 'development'

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


class TestDataSeeder:
    """Test data seeder for Postfix Manager."""
    
    def __init__(self, app, verbose=False):
        self.app = app
        self.verbose = verbose
        self.fake_data = self._generate_fake_data()
    
    def _generate_fake_data(self):
        """Generate fake data for seeding."""
        return {
            'domains': [
                'example.com',
                'testdomain.org',
                'mailserver.net',
                'corporate.biz',
                'startup.io',
                'enterprise.co.uk',
                'dev.local',
                'staging.test',
                'production.com',
                'backup.org'
            ],
            'usernames': [
                'admin', 'user1', 'user2', 'user3', 'user4', 'user5',
                'manager', 'developer', 'tester', 'support', 'sales',
                'marketing', 'hr', 'finance', 'legal', 'operations'
            ],
            'actions': [
                'create_domain', 'update_domain', 'delete_domain',
                'create_user', 'update_user', 'delete_user',
                'restart_postfix', 'reload_dovecot', 'backup_config',
                'restore_config', 'update_quota', 'change_password',
                'enable_service', 'disable_service', 'test_connection'
            ],
            'resource_types': [
                'mail_domain', 'mail_user', 'postfix_config',
                'dovecot_config', 'ldap_config', 'system_config',
                'backup', 'service', 'connection'
            ],
            'ip_addresses': [
                '192.168.1.100', '192.168.1.101', '192.168.1.102',
                '10.0.0.50', '10.0.0.51', '10.0.0.52',
                '172.16.0.10', '172.16.0.11', '172.16.0.12'
            ]
        }
    
    def _log(self, message):
        """Log message if verbose mode is enabled."""
        if self.verbose:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    
    def clear_existing_data(self):
        """Clear all existing data from the database."""
        self._log("Clearing existing data...")
        
        with self.app.app_context():
            # Delete in reverse order to avoid foreign key constraints
            AuditLog.query.delete()
            MailUser.query.delete()
            MailDomain.query.delete()
            SystemConfig.query.delete()
            User.query.delete()
            
            db.session.commit()
            self._log("Existing data cleared successfully")
    
    def seed_users(self, count=5):
        """Seed test users."""
        self._log(f"Seeding {count} test users...")
        
        with self.app.app_context():
            users_created = []
            user_data = []  # Store user data for later use
            
            for i in range(count):
                # Generate unique usernames and emails
                username = f"testuser{i+1}_{random.randint(1000, 9999)}"
                email = f"{username}@example{random.randint(1, 100)}.com"
                
                # Create user with different roles
                if i == 0:
                    role = UserRole.ADMIN
                elif i < 3:
                    role = UserRole.USER
                else:
                    role = UserRole.READONLY
                
                user = User(
                    username=username,
                    email=email,
                    password_hash=f"hashed_password_{i+1}_{random.randint(1000, 9999)}",
                    role=role,
                    is_active=random.choice([True, True, True, False]),  # 75% active
                    created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 365)),
                    last_login=datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 168))
                )
                
                db.session.add(user)
                users_created.append(user)
            
            db.session.commit()
            
            # Extract user data while still in session context
            for user in users_created:
                user_data.append({
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                })
            
            self._log(f"Created {len(users_created)} test users")
            return user_data
    
    def seed_domains(self, count=10):
        """Seed test mail domains."""
        self._log(f"Seeding {count} test domains...")
        
        with self.app.app_context():
            domains_created = []
            domain_data = []  # Store domain data for later use
            
            for i in range(count):
                if i < len(self.fake_data['domains']):
                    base_domain = self.fake_data['domains'][i]
                    # Add random suffix to make domain unique
                    domain_name = f"{base_domain.split('.')[0]}{random.randint(1, 1000)}.{base_domain.split('.', 1)[1]}"
                else:
                    domain_name = f"domain{i+1}_{random.randint(1000, 9999)}.test"
                
                # Generate LDAP configuration
                parts = domain_name.split('.')
                ldap_base_dn = ','.join([f'dc={part}' for part in parts])
                ldap_admin_dn = f'cn=admin,{ldap_base_dn}'
                
                domain = MailDomain(
                    domain=domain_name,
                    is_active=random.choice([True, True, True, False]),  # 75% active
                    postfix_enabled=random.choice([True, True, False]),  # 67% enabled
                    dovecot_enabled=random.choice([True, True, False]),  # 67% enabled
                    ldap_base_dn=ldap_base_dn,
                    ldap_admin_dn=ldap_admin_dn,
                    ldap_admin_password=f"admin_pass_{i+1}",
                    created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 365)),
                    updated_at=datetime.now(timezone.utc) - timedelta(days=random.randint(0, 30))
                )
                
                db.session.add(domain)
                domains_created.append(domain)
            
            db.session.commit()
            
            # Extract domain data while still in session context
            for domain in domains_created:
                domain_data.append({
                    'id': domain.id,
                    'domain': domain.domain,
                    'ldap_base_dn': domain.ldap_base_dn
                })
            
            self._log(f"Created {len(domains_created)} test domains")
            return domain_data
    
    def seed_mail_users(self, domain_ids, count=25):
        """Seed test mail users."""
        self._log(f"Seeding {count} test mail users...")
        
        with self.app.app_context():
            users_created = []
            
            # Refresh domains to ensure they're bound to the current session
            # domain_ids = [domain.id for domain in domains] # This line is removed as domain_ids are now passed directly
            refreshed_domains = MailDomain.query.filter(MailDomain.id.in_(domain_ids)).all()
            
            for i in range(count):
                if i < len(self.fake_data['usernames']):
                    base_username = self.fake_data['usernames'][i]
                    username = f"{base_username}_{random.randint(100, 999)}"
                else:
                    username = f"user{i+1}_{random.randint(1000, 9999)}"
                
                # Assign to random domain
                domain = random.choice(refreshed_domains)
                
                # Generate LDAP DN
                ldap_dn = f"uid={username},{domain.ldap_base_dn}"
                
                # Generate quota (0 = unlimited, otherwise random size)
                quota = random.choice([0, 0, 0, 1000000, 5000000, 1073741824])  # 0, 1MB, 5MB, 1GB
                
                user = MailUser(
                    username=username,
                    domain_id=domain.id,
                    password_hash=f"mail_hash_{i+1}",
                    is_active=random.choice([True, True, True, False]),  # 75% active
                    quota=quota,
                    home_dir=f"/home/{username}",
                    ldap_dn=ldap_dn,
                    created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 365)),
                    updated_at=datetime.now(timezone.utc) - timedelta(days=random.randint(0, 30))
                )
                
                db.session.add(user)
                users_created.append(user)
            
            db.session.commit()
            
            # Extract mail user data while still in session context
            mail_user_data = []
            for user in users_created:
                mail_user_data.append({
                    'id': user.id,
                    'username': user.username,
                    'domain_id': user.domain_id
                })
            
            self._log(f"Created {len(users_created)} test mail users")
            return mail_user_data
    
    def seed_system_configs(self, count=20):
        """Seed test system configurations."""
        self._log(f"Seeding {count} system configurations...")
        
        with self.app.app_context():
            configs_created = []
            
            # Common mail server configurations
            common_configs = [
                ('mail.max_message_size', '10485760', 'Maximum message size in bytes (10MB)'),
                ('mail.max_attachment_size', '5242880', 'Maximum attachment size in bytes (5MB)'),
                ('mail.default_quota', '1073741824', 'Default user quota in bytes (1GB)'),
                ('mail.smtp_port', '587', 'SMTP submission port'),
                ('mail.smtps_port', '465', 'SMTPS port'),
                ('mail.imap_port', '143', 'IMAP port'),
                ('mail.imaps_port', '993', 'IMAPS port'),
                ('mail.pop3_port', '110', 'POP3 port'),
                ('mail.pop3s_port', '995', 'POP3S port'),
                ('mail.ssl_enabled', 'true', 'Enable SSL/TLS'),
                ('mail.tls_enabled', 'true', 'Enable STARTTLS'),
                ('mail.auth_required', 'true', 'Require authentication'),
                ('mail.relay_allowed', 'false', 'Allow open relay'),
                ('mail.spam_protection', 'true', 'Enable spam protection'),
                ('mail.virus_scanning', 'true', 'Enable virus scanning'),
                ('ldap.server', 'localhost', 'LDAP server address'),
                ('ldap.port', '389', 'LDAP server port'),
                ('ldap.base_dn', 'dc=example,dc=com', 'LDAP base DN'),
                ('ldap.admin_dn', 'cn=admin,dc=example,dc=com', 'LDAP admin DN'),
                ('system.backup_enabled', 'true', 'Enable automatic backups'),
                ('system.backup_retention', '30', 'Backup retention in days'),
                ('system.monitoring_enabled', 'true', 'Enable system monitoring'),
                ('system.alert_email', 'admin@example.com', 'Alert notification email'),
                ('system.log_level', 'INFO', 'Application log level'),
                ('system.session_timeout', '3600', 'Session timeout in seconds')
            ]
            
            for i, (key, value, description) in enumerate(common_configs):
                if i >= count:
                    break
                
                config = SystemConfig(
                    key=key,
                    value=value,
                    description=description,
                    updated_at=datetime.now(timezone.utc) - timedelta(days=random.randint(0, 30))
                )
                
                db.session.add(config)
                configs_created.append(config)
            
            # Add some random custom configurations
            remaining_count = count - len(common_configs)
            for i in range(remaining_count):
                key = f"custom.setting_{i+1}"
                value = random.choice(['true', 'false', '100', '200', 'custom_value'])
                description = f"Custom configuration setting {i+1}"
                
                config = SystemConfig(
                    key=key,
                    value=value,
                    description=description,
                    updated_at=datetime.now(timezone.utc) - timedelta(days=random.randint(0, 30))
                )
                
                db.session.add(config)
                configs_created.append(config)
            
            db.session.commit()
            self._log(f"Created {len(configs_created)} system configurations")
            return configs_created
    
    def seed_audit_logs(self, users, domain_ids, domain_names, mail_users, count=100):
        """Seed test audit logs."""
        self._log(f"Seeding {count} audit log entries...")
        
        with self.app.app_context():
            logs_created = []
            
            # Get domain names for resource IDs
            # domains = MailDomain.query.filter(MailDomain.id.in_(domain_ids)).all() # This line is removed
            # domain_map = {domain.id: domain.domain for domain in domains} # This line is removed
            
            for i in range(count):
                # Random user (can be None for system actions)
                user_data = random.choice([None] + users) if random.random() < 0.9 else None
                
                # Random action and resource
                action = random.choice(self.fake_data['actions'])
                resource_type = random.choice(self.fake_data['resource_types'])
                
                # Generate resource ID based on type
                if resource_type == 'mail_domain':
                    domain_id = random.choice(domain_ids)
                    resource_id = domain_names[domain_ids.index(domain_id)] # Use domain_names list
                elif resource_type == 'mail_user':
                    resource_id = random.choice(mail_users)['username'] if mail_users else f"user_{i}"
                else:
                    resource_id = f"resource_{i+1}"
                
                # Generate realistic details
                details_map = {
                    'create_domain': f"Created new mail domain: {resource_id}",
                    'update_domain': f"Updated domain configuration: {resource_id}",
                    'delete_domain': f"Deleted domain: {resource_id}",
                    'create_user': f"Created new mail user: {resource_id}",
                    'update_user': f"Updated user configuration: {resource_id}",
                    'delete_user': f"Deleted user: {resource_id}",
                    'restart_postfix': "Restarted Postfix mail service",
                    'reload_dovecot': "Reloaded Dovecot configuration",
                    'backup_config': "Created configuration backup",
                    'restore_config': "Restored configuration from backup",
                    'update_quota': f"Updated quota for user: {resource_id}",
                    'change_password': f"Changed password for user: {resource_id}",
                    'enable_service': f"Enabled service: {resource_id}",
                    'disable_service': f"Disabled service: {resource_id}",
                    'test_connection': f"Tested connection to: {resource_id}"
                }
                
                details = details_map.get(action, f"Action: {action} on {resource_type}: {resource_id}")
                
                # Random IP address
                ip_address = random.choice(self.fake_data['ip_addresses'])
                
                # Random timestamp within last 30 days
                created_at = datetime.now(timezone.utc) - timedelta(
                    days=random.randint(0, 30),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )
                
                log = AuditLog(
                    user_id=user_data['id'] if user_data else None,
                    action=action,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    details=details,
                    ip_address=ip_address,
                    created_at=created_at
                )
                
                db.session.add(log)
                logs_created.append(log)
            
            db.session.commit()
            self._log(f"Created {len(logs_created)} audit log entries")
            return logs_created
    
    def seed_all_data(self, count=10, clear_existing=False):
        """Seed all types of test data."""
        self._log("Starting data seeding process...")
        
        with self.app.app_context():
            if clear_existing:
                self.clear_existing_data()
            
            try:
                # Seed in order to maintain referential integrity
                users = self.seed_users(min(count, 5))
                domains = self.seed_domains(count)
                
                # Get domain IDs immediately while still in session context
                domain_ids = []
                domain_names = []
                for domain in domains:
                    domain_ids.append(domain['id'])
                    domain_names.append(domain['domain'])
                
                self._log(f"Domain IDs collected: {domain_ids}")
                self._log(f"Domain names collected: {domain_names}")
                
                mail_users = self.seed_mail_users(domain_ids, min(count * 2, 25))
                system_configs = self.seed_system_configs(min(count * 2, 20))
                audit_logs = self.seed_audit_logs(users, domain_ids, domain_names, mail_users, min(count * 10, 100))
                
                total_records = len(users) + len(domains) + len(mail_users) + len(system_configs) + len(audit_logs)
                self._log(f"Data seeding completed successfully! Created {total_records} total records")
                
                return {
                    'users': users,
                    'domains': domains,
                    'mail_users': mail_users,
                    'system_configs': system_configs,
                    'audit_logs': audit_logs
                }
                
            except Exception as e:
                self._log(f"Error during data seeding: {e}")
                # Handle rollback within app context
                try:
                    db.session.rollback()
                except Exception as rollback_error:
                    self._log(f"Warning: Could not rollback session: {rollback_error}")
                raise


def main():
    """Main function to run the data seeder."""
    parser = argparse.ArgumentParser(description='Seed test data for Postfix Manager')
    parser.add_argument('--clear', action='store_true', help='Clear existing data before seeding')
    parser.add_argument('--verbose', action='store_true', help='Show detailed output')
    parser.add_argument('--count', type=int, default=10, help='Number of test records to create (default: 10)')
    
    args = parser.parse_args()
    
    try:
        print(f"🚀 Starting Postfix Manager test data seeder...")
        print(f"Project root: {PROJECT_ROOT}")
        print(f"Python path: {sys.path[:3]}...")  # Show first 3 paths
        
        # Create Flask app (no arguments needed)
        app = create_app()
        print("✅ Flask app created successfully")
        
        # Test database connection
        with app.app_context():
            try:
                # Test if we can access the database
                from sqlalchemy import text
                db.session.execute(text("SELECT 1"))
                print("✅ Database connection successful")
            except Exception as db_error:
                print(f"❌ Database connection failed: {db_error}")
                print("Please ensure the database is properly configured and accessible.")
                sys.exit(1)
        
        # Create seeder
        seeder = TestDataSeeder(app, verbose=args.verbose)
        
        # Seed data
        results = seeder.seed_all_data(count=args.count, clear_existing=args.clear)
        
        if args.verbose:
            print("\n" + "="*50)
            print("SEEDING SUMMARY")
            print("="*50)
            print(f"Users created: {len(results['users'])}")
            print(f"Domains created: {len(results['domains'])}")
            print(f"Mail users created: {len(results['mail_users'])}")
            print(f"System configs created: {len(results['system_configs'])}")
            print(f"Audit logs created: {len(results['audit_logs'])}")
            print(f"Total records: {sum(len(v) for v in results.values())}")
            print("="*50)
        
        print(f"✅ Successfully seeded test data! Created {sum(len(v) for v in results.values())} total records.")
        
    except Exception as e:
        print(f"❌ Error seeding test data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
