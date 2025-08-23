#!/usr/bin/env python3
"""
VM Database Initialization Script for Postfix Manager

This script creates the database and initializes all tables on the VM.
It supports all database types: SQLite, MySQL/MariaDB, and PostgreSQL.
It uses the new database configuration system for flexibility.

Usage:
    python3 scripts/init_vm_db.py
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def init_vm_database():
    """Initialize the database on VM with proper paths for any database type."""
    try:
        print("🚀 Postfix Manager - VM Database Initialization")
        print("=" * 50)
        print()
        
        # Import the new database configuration system
        from app.extensions.database import DbConfig
        
        # Get database configuration
        db_config = DbConfig()
        db_type = db_config.db_type
        
        print(f"📊 Database Type: {db_type}")
        print(f"🔗 Database URI: {db_config.db_uri}")
        print()
        
        # Handle SQLite-specific setup
        if db_type == 'sqlite':
            # Set VM-appropriate database path
            db_path = "/opt/postfix-manager/app/data/db/postfix_manager.db"
            db_dir = os.path.dirname(db_path)
            
            print(f"📁 Database path: {db_path}")
            print(f"📁 Database directory: {db_dir}")
            
            # Create database directory if it doesn't exist
            if not os.path.exists(db_dir):
                print(f"📁 Creating database directory: {db_dir}")
                os.makedirs(db_dir, exist_ok=True)
            
            # Fix directory permissions
            print("🔐 Fixing directory permissions...")
            try:
                current_uid = os.getuid()
                current_gid = os.getgid()
                
                # Change directory ownership to current user
                os.chown(db_dir, current_uid, current_gid)
                print(f"✅ Changed directory ownership to UID:{current_uid} GID:{current_gid}")
                
                # Set directory permissions to 755 (rwxr-xr-x)
                os.chmod(db_dir, 0o755)
                print("✅ Set directory permissions to 755")
                
            except Exception as perm_error:
                print(f"⚠️  Warning: Could not fix directory permissions: {perm_error}")
            
            # Create empty database file if it doesn't exist
            if not os.path.exists(db_path):
                print(f"📄 Creating database file: {db_path}")
                with open(db_path, 'w') as f:
                    pass  # Create empty file
            
            # Fix permissions - ensure the database file is readable/writable by the app
            print("🔐 Fixing database permissions...")
            try:
                # Get the current user's UID and GID
                current_uid = os.getuid()
                current_gid = os.getgid()
                
                # Change ownership to current user
                os.chown(db_path, current_uid, current_gid)
                print(f"✅ Changed ownership to UID:{current_uid} GID:{current_gid}")
                
                # Set permissions to 644 (rw-r--r--)
                os.chmod(db_path, 0o644)
                print("✅ Set database file permissions to 644")
                
            except Exception as perm_error:
                print(f"⚠️  Warning: Could not fix permissions: {perm_error}")
                print("   This might cause issues if running as different user")
        
        elif db_type in ['mysql', 'mariadb']:
            print("🐬 MySQL/MariaDB detected")
            print("📋 Please ensure the following:")
            print(f"   • Database '{db_config.db_name}' exists")
            print(f"   • User '{db_config.db_username}' has proper permissions")
            print(f"   • Database server is running on {db_config.db_hostname}:{db_config.db_port}")
            print()
            
        elif db_type == 'postgresql':
            print("🐘 PostgreSQL detected")
            print("📋 Please ensure the following:")
            print(f"   • Database '{db_config.db_name}' exists")
            print(f"   • User '{db_config.db_username}' has proper permissions")
            print(f"   • Database server is running on {db_config.db_hostname}:{db_config.db_port}")
            print()
        
        else:
            print(f"⚠️  Unsupported database type: {db_type}")
            print("   Supported types: sqlite, mysql, mariadb, postgresql")
            return False
        
        # Now import and initialize the app
        print("📦 Importing application...")
        from app import create_app
        from app.extensions import db
        
        print("🔧 Creating Flask app...")
        app = create_app()
        
        with app.app_context():
            print("📊 Creating database tables...")
            
            # Create all tables
            db.create_all()
            
            print("✅ Database tables created successfully!")
            print()
            print("📋 Created tables:")
            
            # Get table names
            inspector = db.inspect(db.engine)
            table_names = inspector.get_table_names()
            
            for table_name in table_names:
                print(f"   • {table_name}")
            
            print()
            print("🎉 Database initialization complete!")
            print("You can now run the create_admin.py script to create your first user.")
            
            return True
            
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        print()
        print("🔍 Troubleshooting:")
        if db_type == 'sqlite':
            print(f"1. Check if directory exists: ls -la {db_dir}")
            print(f"2. Check if file exists: ls -la {db_path}")
            print(f"3. Check permissions: ls -la {db_dir}")
        else:
            print(f"1. Check database connection: {db_config.db_uri}")
            print(f"2. Verify database server is running")
            print(f"3. Check user credentials and permissions")
        print(f"4. Check disk space: df -h")
        print(f"5. Check Python path: {sys.path}")
        return False


def main():
    """Main function to initialize the database."""
    success = init_vm_database()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
