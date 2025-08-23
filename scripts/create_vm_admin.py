#!/usr/bin/env python3
"""
Create Initial Admin User for Postfix Manager on VM

This script creates the first admin user for the Postfix Manager application.
It's designed to work on the VM with proper database paths.

Usage:
    python3 scripts/create_vm_admin.py
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def create_vm_admin():
    """Create admin user on VM with proper database paths."""
    try:
        print("🚀 Postfix Manager - Create Initial User")
        print("=" * 50)
        print()
        
        # Set VM-appropriate database path
        db_path = "/opt/postfix-manager/instance/postfix_manager.db"
        os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'
        
        print(f"🔧 Using database: {db_path}")
        
        # Import required modules
        from app import create_app
        from app.extensions import db
        from app.models import User, UserRole
        
        # Create Flask app
        app = create_app()
        
        with app.app_context():
            # Check if admin user already exists
            admin = User.query.filter_by(username='admin').first()
            if admin:
                print("ℹ️  Admin user already exists:")
                print(f"   Username: {admin.username}")
                print(f"   Email: {admin.email}")
                print(f"   Role: {admin.role.value if admin.role else 'No role'}")
                print(f"   Active: {admin.is_active}")
                return True
            
            # Get user input
            print("📝 Creating new admin user...")
            username = input("Enter username: ").strip()
            email = input("Enter email address: ").strip()
            password = input("Enter password: ").strip()
            confirm_password = input("Confirm password: ").strip()
            
            # Validate input
            if not username or not email or not password:
                print("❌ Username, email, and password are required")
                return False
            
            if password != confirm_password:
                print("❌ Passwords do not match")
                return False
            
            if len(password) < 8:
                print("❌ Password must be at least 8 characters long")
                return False
            
            # Check if user already exists
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                print(f"❌ User '{username}' already exists")
                return False
            
            existing_email = User.query.filter_by(email=email).first()
            if existing_email:
                print(f"❌ Email '{email}' already exists")
                return False
            
            # Create user
            print()
            print("Creating user with the following details:")
            print(f"   Username: {username}")
            print(f"   Email: {email}")
            print(f"   Role: {UserRole.ADMIN.value}")
            
            proceed = input("Proceed with user creation? (y/N): ").strip().lower()
            if proceed != 'y':
                print("❌ User creation cancelled")
                return False
            
            # Create user with admin role (UserRole is an enum, not a model)
            from app.extensions import bcrypt
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            
            user = User(
                username=username,
                email=email,
                password_hash=hashed_password,
                role=UserRole.ADMIN,  # Use enum value directly
                is_active=True
            )
            
            db.session.add(user)
            db.session.commit()
            
            print()
            print("✅ Successfully created admin user:")
            print(f"   Username: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Role: {user.role.value}")
            print(f"   Active: {user.is_active}")
            print()
            print("You can now log in to the system using these credentials.")
            
            return True
            
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        print()
        print("🔍 Troubleshooting:")
        print(f"1. Check database path: {db_path}")
        print(f"2. Check database exists: ls -la {db_path}")
        print(f"3. Check permissions: ls -la {os.path.dirname(db_path)}")
        print(f"4. Check Python path: {sys.path}")
        return False


def main():
    """Main function to create admin user."""
    success = create_vm_admin()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
