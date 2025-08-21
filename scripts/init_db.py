#!/usr/bin/env python3
"""
Database Initialization Script for Postfix Manager

This script creates the database and initializes all tables.
Run this script before creating users or running the application.

Usage:
    python3 scripts/init_db.py
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import create_app
from app.extensions import db


def init_database():
    """Initialize the database and create all tables."""
    try:
        print("🚀 Postfix Manager - Database Initialization")
        print("=" * 50)
        print()
        
        # Create Flask app context
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
        return False


def main():
    """Main function to initialize the database."""
    success = init_database()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
