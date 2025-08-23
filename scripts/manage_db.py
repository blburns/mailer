#!/usr/bin/env python3
"""
Database Management Script for Postfix Manager

Supports multiple database backends:
- SQLite (development/testing)
- MySQL/MariaDB (production)
- PostgreSQL (production)

Usage:
    python scripts/manage_db.py [command] [options]

Commands:
    init           - Initialize database and create first migration
    migrate        - Run pending migrations
    upgrade        - Upgrade to latest migration
    downgrade      - Downgrade to previous migration
    current        - Show current migration version
    history        - Show migration history
    create         - Create a new migration
    reset          - Reset database (drop all tables and recreate)
    seed           - Seed database with test data
    backup         - Create database backup
    restore        - Restore database from backup
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import create_app
from app.extensions import db, migrate
from app.models import User, AuditLog, MailDomain, MailUser, SystemConfig

def get_db_type():
    """Get database type from environment."""
    return os.environ.get('DB_TYPE', 'sqlite').lower()

def get_migration_dir():
    """Get migration directory based on database type."""
    db_type = get_db_type()
    return f'migrations/{db_type}'

def run_command(cmd, cwd=None):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def init_database():
    """Initialize the database."""
    print("🔧 Initializing database...")
    
    app = create_app()
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Database tables created successfully")
        
        # Create initial migration if using Flask-Migrate
        if get_db_type() != 'sqlite':
            migration_dir = get_migration_dir()
            if not os.path.exists(migration_dir):
                print(f"📁 Creating migration directory: {migration_dir}")
                os.makedirs(migration_dir, exist_ok=True)
                
                # Initialize Flask-Migrate
                cmd = f"flask db init --directory {migration_dir}"
                success, stdout, stderr = run_command(cmd)
                if success:
                    print("✅ Flask-Migrate initialized")
                else:
                    print(f"⚠️  Flask-Migrate init failed: {stderr}")
        
        print("✅ Database initialization complete")

def create_migration(message):
    """Create a new migration."""
    print(f"📝 Creating migration: {message}")
    
    migration_dir = get_migration_dir()
    if not os.path.exists(migration_dir):
        print(f"❌ Migration directory not found: {migration_dir}")
        print("Run 'init' command first")
        return
    
    cmd = f"flask db migrate --directory {migration_dir} -m '{message}'"
    success, stdout, stderr = run_command(cmd)
    
    if success:
        print("✅ Migration created successfully")
        print(stdout)
    else:
        print(f"❌ Migration creation failed: {stderr}")

def run_migrations():
    """Run pending migrations."""
    print("🔄 Running migrations...")
    
    migration_dir = get_migration_dir()
    if not os.path.exists(migration_dir):
        print(f"❌ Migration directory not found: {migration_dir}")
        print("Run 'init' command first")
        return
    
    cmd = f"flask db upgrade --directory {migration_dir}"
    success, stdout, stderr = run_command(cmd)
    
    if success:
        print("✅ Migrations completed successfully")
        print(stdout)
    else:
        print(f"❌ Migration failed: {stderr}")

def show_current_version():
    """Show current migration version."""
    print("📊 Current migration version:")
    
    migration_dir = get_migration_dir()
    if not os.path.exists(migration_dir):
        print(f"❌ Migration directory not found: {migration_dir}")
        return
    
    cmd = f"flask db current --directory {migration_dir}"
    success, stdout, stderr = run_command(cmd)
    
    if success:
        print(stdout)
    else:
        print(f"❌ Failed to get current version: {stderr}")

def show_migration_history():
    """Show migration history."""
    print("📚 Migration history:")
    
    migration_dir = get_migration_dir()
    if not os.path.exists(migration_dir):
        print(f"❌ Migration directory not found: {migration_dir}")
        return
    
    cmd = f"flask db history --directory {migration_dir}"
    success, stdout, stderr = run_command(cmd)
    
    if success:
        print(stdout)
    else:
        print(f"❌ Failed to get migration history: {stderr}")

def reset_database():
    """Reset the database (drop all tables and recreate)."""
    print("⚠️  WARNING: This will delete all data!")
    response = input("Are you sure you want to continue? (yes/no): ")
    
    if response.lower() != 'yes':
        print("❌ Operation cancelled")
        return
    
    print("🔄 Resetting database...")
    
    app = create_app()
    with app.app_context():
        # Drop all tables
        db.drop_all()
        print("✅ All tables dropped")
        
        # Recreate all tables
        db.create_all()
        print("✅ Tables recreated")
        
        print("✅ Database reset complete")

def seed_database():
    """Seed the database with test data."""
    print("🌱 Seeding database with test data...")
    
    app = create_app()
    with app.app_context():
        try:
            # Create admin user
            from app.utils.auth_utils import hash_password
            admin_user = User(
                username='admin',
                email='admin@example.com',
                password_hash=hash_password('admin123'),
                role='ADMIN',
                is_active=True
            )
            db.session.add(admin_user)
            
            # Create test domain
            test_domain = MailDomain(
                domain='example.com',
                ldap_base_dn='dc=example,dc=com',
                is_active=True
            )
            db.session.add(test_domain)
            
            # Create test mail user
            test_mail_user = MailUser(
                username='testuser',
                domain_id=1,
                email='testuser@example.com',
                quota_mb=100,
                is_active=True
            )
            db.session.add(test_mail_user)
            
            # Create system config
            system_config = SystemConfig(
                key='mail_server_name',
                value='mail.example.com',
                description='Primary mail server hostname'
            )
            db.session.add(system_config)
            
            db.session.commit()
            print("✅ Test data seeded successfully")
            
        except Exception as e:
            print(f"❌ Failed to seed database: {e}")
            db.session.rollback()

def backup_database():
    """Create a database backup."""
    print("💾 Creating database backup...")
    
    db_type = get_db_type()
    timestamp = subprocess.run(['date', '+%Y%m%d_%H%M%S'], capture_output=True, text=True).stdout.strip()
    
    if db_type == 'sqlite':
        # Use the new database configuration system
        from app.extensions.database import DbConfig
        db_config = DbConfig()
        db_path = db_config.db_uri.replace('sqlite:///', '')
        
        backup_path = f"{db_path}.backup.{timestamp}"
        cmd = f"cp {db_path} {backup_path}"
        
    elif db_type in ['mysql', 'mariadb']:
        db_name = os.environ.get('DB_NAME', 'postfix_manager')
        db_hostname = os.environ.get('DB_HOSTNAME', 'localhost')
        db_port = os.environ.get('DB_PORT', '3306')
        db_username = os.environ.get('DB_USERNAME', 'root')
        db_password = os.environ.get('DB_PASSWORD', '')
        
        backup_path = f"/tmp/postfix_manager_{timestamp}.sql"
        cmd = f"mysqldump -h{db_hostname} -P{db_port} -u{db_username} -p{db_password} {db_name} > {backup_path}"
        
    elif db_type == 'postgresql':
        db_name = os.environ.get('DB_NAME', 'postfix_manager')
        db_hostname = os.environ.get('DB_HOSTNAME', 'localhost')
        db_port = os.environ.get('DB_PORT', '5432')
        db_username = os.environ.get('DB_USERNAME', 'postgres')
        db_password = os.environ.get('DB_PASSWORD', '')
        
        backup_path = f"/tmp/postfix_manager_{timestamp}.sql"
        cmd = f"PGPASSWORD='{db_password}' pg_dump -h{db_hostname} -p{db_port} -U{db_username} {db_name} > {backup_path}"
    
    success, stdout, stderr = run_command(cmd)
    
    if success:
        print(f"✅ Database backup created: {backup_path}")
    else:
        print(f"❌ Backup failed: {stderr}")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Database Management Script for Postfix Manager')
    parser.add_argument('command', choices=[
        'init', 'migrate', 'upgrade', 'downgrade', 'current', 'history',
        'create', 'reset', 'seed', 'backup', 'restore'
    ], help='Command to execute')
    
    parser.add_argument('--message', '-m', help='Migration message (for create command)')
    
    args = parser.parse_args()
    
    # Set environment variables
    os.environ['FLASK_APP'] = 'run.py'
    os.environ['FLASK_ENV'] = 'development'
    
    print(f"🚀 Postfix Manager Database Manager")
    print(f"📊 Database Type: {get_db_type()}")
    print(f"📁 Migration Directory: {get_migration_dir()}")
    print()
    
    if args.command == 'init':
        init_database()
    elif args.command == 'create':
        if not args.message:
            print("❌ Migration message is required for create command")
            print("Usage: python scripts/manage_db.py create -m 'Add users table'")
            return
        create_migration(args.message)
    elif args.command == 'migrate':
        run_migrations()
    elif args.command == 'upgrade':
        run_migrations()
    elif args.command == 'current':
        show_current_version()
    elif args.command == 'history':
        show_migration_history()
    elif args.command == 'reset':
        reset_database()
    elif args.command == 'seed':
        seed_database()
    elif args.command == 'backup':
        backup_database()
    else:
        print(f"❌ Command '{args.command}' not implemented yet")

if __name__ == '__main__':
    main()
