#!/usr/bin/env python3
"""
Create Initial Admin User Script for Postfix Manager

This script creates the first admin user account for the Postfix Manager system.
Run this script after initial installation to set up your first login account.

Usage:
    python3 scripts/create_admin.py
    python3 scripts/create_admin.py --username admin --email admin@example.com --password mypassword
"""

import os
import sys
import argparse
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import create_app
from app.extensions import db
from app.models import User, UserRole


def create_admin_user(username, email, password, role=UserRole.ADMIN):
    """Create an admin user in the database."""
    try:
        # Create Flask app context
        app = create_app()
        
        with app.app_context():
            # Check if user already exists
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                print(f"User '{username}' already exists!")
                return False
            
            existing_email = User.query.filter_by(email=email).first()
            if existing_email:
                print(f"Email '{email}' is already registered!")
                return False
            
            # Create new user
            from app.extensions import bcrypt
            password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
            
            new_user = User(
                username=username,
                email=email,
                password_hash=password_hash,
                role=role,
                is_active=True
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            print(f"✅ Successfully created {role.value} user:")
            print(f"   Username: {username}")
            print(f"   Email: {email}")
            print(f"   Role: {role.value}")
            print(f"   Status: Active")
            print()
            print("You can now log in to the system using these credentials.")
            
            return True
            
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return False


def main():
    """Main function to handle command line arguments and create user."""
    parser = argparse.ArgumentParser(
        description="Create initial admin user for Postfix Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Interactive mode (default)
    python3 scripts/create_admin.py
    
    # Command line mode
    python3 scripts/create_admin.py --username admin --email admin@example.com --password mypassword
    
    # Create a regular user
    python3 scripts/create_admin.py --username user1 --email user1@example.com --password userpass --role user
        """
    )
    
    parser.add_argument(
        '--username', 
        help='Username for the new account'
    )
    parser.add_argument(
        '--email', 
        help='Email address for the new account'
    )
    parser.add_argument(
        '--password', 
        help='Password for the new account'
    )
    parser.add_argument(
        '--role', 
        choices=['admin', 'user', 'readonly'],
        default='admin',
        help='User role (default: admin)'
    )
    parser.add_argument(
        '--non-interactive',
        action='store_true',
        help='Run in non-interactive mode (requires all arguments)'
    )
    
    args = parser.parse_args()
    
    # Convert role string to enum
    role_map = {
        'admin': UserRole.ADMIN,
        'user': UserRole.USER,
        'readonly': UserRole.READONLY
    }
    role = role_map[args.role]
    
    # Check if running in non-interactive mode
    if args.non_interactive:
        if not all([args.username, args.email, args.password]):
            print("❌ Error: In non-interactive mode, all arguments (--username, --email, --password) are required.")
            sys.exit(1)
        
        success = create_admin_user(args.username, args.email, args.password, role)
        sys.exit(0 if success else 1)
    
    # Interactive mode
    print("🚀 Postfix Manager - Create Initial User")
    print("=" * 50)
    print()
    
    # Get user input
    username = args.username
    if not username:
        username = input("Enter username: ").strip()
        if not username:
            print("❌ Username cannot be empty!")
            sys.exit(1)
    
    email = args.email
    if not email:
        email = input("Enter email address: ").strip()
        if not email:
            print("❌ Email cannot be empty!")
            sys.exit(1)
    
    password = args.password
    if not password:
        password = input("Enter password: ").strip()
        if not password:
            print("❌ Password cannot be empty!")
            sys.exit(1)
        
        # Confirm password
        confirm_password = input("Confirm password: ").strip()
        if password != confirm_password:
            print("❌ Passwords do not match!")
            sys.exit(1)
    
    # Validate password strength
    if len(password) < 8:
        print("❌ Password must be at least 8 characters long!")
        sys.exit(1)
    
    print()
    print("Creating user with the following details:")
    print(f"   Username: {username}")
    print(f"   Email: {email}")
    print(f"   Role: {role.value}")
    print()
    
    # Confirm creation
    confirm = input("Proceed with user creation? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("❌ User creation cancelled.")
        sys.exit(0)
    
    # Create the user
    success = create_admin_user(username, email, password, role)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
