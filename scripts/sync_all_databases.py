#!/usr/bin/env python3
"""
Sync All Databases Script for Postfix Manager

This script allows you to manage all three database backends simultaneously:
- SQLite (development/testing)
- MySQL/MariaDB (production)
- PostgreSQL (production)

Keeps all databases in sync during development and testing.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class DatabaseManager:
    """Manages multiple database backends simultaneously."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.databases = {
            'sqlite': {
                'name': 'SQLite',
                'url': 'sqlite:///instance/postfix_manager.db',
                'migration_dir': 'migrations/sqlite',
                'env_file': '.env.sqlite'
            },
            'mysql': {
                'name': 'MySQL/MariaDB',
                'url': 'mysql://root:password@localhost:3306/postfix_manager',
                'migration_dir': 'migrations/mysql',
                'env_file': '.env.mysql'
            },
            'postgresql': {
                'name': 'PostgreSQL',
                'url': 'postgresql://postgres:password@localhost:5432/postfix_manager',
                'migration_dir': 'migrations/postgresql',
                'env_file': '.env.postgresql'
            }
        }
    
    def create_env_files(self):
        """Create environment files for each database type."""
        print("📁 Creating environment files for each database...")
        
        for db_type, config in self.databases.items():
            env_file = self.project_root / config['env_file']
            env_content = f"""# Environment configuration for {config['name']}
FLASK_APP=run.py
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=dev-secret-key-change-in-production
DATABASE_URL={config['url']}

# Database-specific settings
DB_TYPE={db_type}
"""
            
            with open(env_file, 'w') as f:
                f.write(env_content)
            
            print(f"   ✅ Created {config['env_file']}")
    
    def setup_migration_directories(self):
        """Set up migration directories for all database types."""
        print("\n📁 Setting up migration directories...")
        
        for db_type, config in self.databases.items():
            migration_dir = self.project_root / config['migration_dir']
            migration_dir.mkdir(parents=True, exist_ok=True)
            
            # Create versions directory
            versions_dir = migration_dir / 'versions'
            versions_dir.mkdir(exist_ok=True)
            
            print(f"   ✅ {config['name']}: {config['migration_dir']}")
    
    def init_migrations(self, db_type: str = None):
        """Initialize migrations for specified database or all databases."""
        if db_type:
            databases_to_init = {db_type: self.databases[db_type]}
        else:
            databases_to_init = self.databases
        
        print(f"\n🔄 Initializing migrations...")
        
        for db_type, config in databases_to_init.items():
            print(f"\n📊 {config['name']} ({db_type})")
            print("=" * 50)
            
            # Set environment variables
            env = os.environ.copy()
            env['DATABASE_URL'] = config['url']
            env['DB_TYPE'] = db_type
            env['FLASK_APP'] = 'run.py'
            env['PYTHONPATH'] = str(self.project_root)
            
            # Change to migration directory
            migration_dir = self.project_root / config['migration_dir']
            os.chdir(migration_dir)
            
            try:
                # Initialize Flask-Migrate
                result = subprocess.run(
                    ['flask', 'db', 'init'],
                    env=env,
                    capture_output=True,
                    text=True,
                    check=True
                )
                print("   ✅ Migrations initialized")
                print(result.stdout)
                
            except subprocess.CalledProcessError as e:
                print(f"   ❌ Failed to initialize migrations: {e}")
                print(f"   Error: {e.stderr}")
            
            finally:
                # Change back to project root
                os.chdir(self.project_root)
    
    def create_migration(self, message: str, db_type: str = None):
        """Create a migration for specified database or all databases."""
        if db_type:
            databases_to_migrate = {db_type: self.databases[db_type]}
        else:
            databases_to_migrate = self.databases
        
        print(f"\n🔄 Creating migration: '{message}'")
        
        for db_type, config in databases_to_migrate.items():
            print(f"\n📊 {config['name']} ({db_type})")
            print("=" * 50)
            
            # Set environment variables
            env = os.environ.copy()
            env['DATABASE_URL'] = config['url']
            env['DB_TYPE'] = db_type
            env['FLASK_APP'] = 'run.py'
            env['PYTHONPATH'] = str(self.project_root)
            
            # Change to migration directory
            migration_dir = self.project_root / config['migration_dir']
            os.chdir(migration_dir)
            
            try:
                # Create migration
                result = subprocess.run(
                    ['flask', 'db', 'migrate', '-m', message],
                    env=env,
                    capture_output=True,
                    text=True,
                    check=True
                )
                print("   ✅ Migration created")
                print(result.stdout)
                
            except subprocess.CalledProcessError as e:
                print(f"   ❌ Failed to create migration: {e}")
                print(f"   Error: {e.stderr}")
            
            finally:
                # Change back to project root
                os.chdir(self.project_root)
    
    def upgrade_databases(self, db_type: str = None):
        """Upgrade specified database or all databases."""
        if db_type:
            databases_to_upgrade = {db_type: self.databases[db_type]}
        else:
            databases_to_upgrade = self.databases
        
        print(f"\n🔄 Upgrading databases...")
        
        for db_type, config in databases_to_upgrade.items():
            print(f"\n📊 {config['name']} ({db_type})")
            print("=" * 50)
            
            # Set environment variables
            env = os.environ.copy()
            env['DATABASE_URL'] = config['url']
            env['DB_TYPE'] = db_type
            
            # Change to migration directory
            migration_dir = self.project_root / config['migration_dir']
            os.chdir(migration_dir)
            
            try:
                # Upgrade database
                result = subprocess.run(
                    ['flask', 'db', 'upgrade'],
                    env=env,
                    capture_output=True,
                    text=True,
                    check=True
                )
                print("   ✅ Database upgraded")
                print(result.stdout)
                
            except subprocess.CalledProcessError as e:
                print(f"   ❌ Failed to upgrade database: {e}")
                print(f"   Error: {e.stderr}")
            
            finally:
                # Change back to project root
                os.chdir(self.project_root)
    
    def show_status(self, db_type: str = None):
        """Show migration status for specified database or all databases."""
        if db_type:
            databases_to_check = {db_type: self.databases[db_type]}
        else:
            databases_to_check = self.databases
        
        print(f"\n📊 Database Migration Status")
        print("=" * 50)
        
        for db_type, config in databases_to_check.items():
            print(f"\n🔍 {config['name']} ({db_type})")
            print("-" * 30)
            
            # Set environment variables
            env = os.environ.copy()
            env['DATABASE_URL'] = config['url']
            env['DB_TYPE'] = db_type
            
            # Change to migration directory
            migration_dir = self.project_root / config['migration_dir']
            os.chdir(migration_dir)
            
            try:
                # Show current revision
                result = subprocess.run(
                    ['flask', 'db', 'current'],
                    env=env,
                    capture_output=True,
                    text=True,
                    check=True
                )
                print(f"   Current: {result.stdout.strip()}")
                
                # Show migration history
                result = subprocess.run(
                    ['flask', 'db', 'history'],
                    env=env,
                    capture_output=True,
                    text=True,
                    check=True
                )
                print(f"   History: {result.stdout.strip()}")
                
            except subprocess.CalledProcessError as e:
                print(f"   ❌ Error: {e}")
            
            finally:
                # Change back to project root
                os.chdir(self.project_root)
    
    def test_connections(self):
        """Test connections to all databases."""
        print(f"\n🧪 Testing database connections...")
        
        for db_type, config in self.databases.items():
            print(f"\n📊 {config['name']} ({db_type})")
            print("-" * 30)
            
            try:
                from app.config.database import test_database_connection
                result = test_database_connection(config['url'])
                
                if result['status'] == 'success':
                    print(f"   ✅ Connection successful")
                    print(f"   📝 {result['message']}")
                else:
                    print(f"   ❌ Connection failed")
                    print(f"   📝 {result['message']}")
                    
            except Exception as e:
                print(f"   ❌ Error testing connection: {e}")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Sync All Databases for Postfix Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Setup all databases and create initial migration
  python scripts/sync_all_databases.py setup
  
  # Create a new migration for all databases
  python scripts/sync_all_databases.py migrate "Add user table"
  
  # Upgrade all databases
  python scripts/sync_all_databases.py upgrade
  
  # Show status of all databases
  python scripts/sync_all_databases.py status
  
  # Test connections to all databases
  python scripts/sync_all_databases.py test
        """
    )
    
    parser.add_argument(
        'command',
        choices=['setup', 'migrate', 'upgrade', 'status', 'test'],
        help='Command to execute'
    )
    
    parser.add_argument(
        '--message', '-m',
        help='Migration message (for migrate command)'
    )
    
    parser.add_argument(
        '--database', '-d',
        choices=['sqlite', 'mysql', 'postgresql'],
        help='Specific database to operate on (default: all)'
    )
    
    args = parser.parse_args()
    
    print("🚀 Postfix Manager - Multi-Database Sync")
    print("=" * 50)
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    # Execute command
    if args.command == 'setup':
        print("🔧 Setting up all databases...")
        db_manager.create_env_files()
        db_manager.setup_migration_directories()
        db_manager.init_migrations(args.database)
        
    elif args.command == 'migrate':
        if not args.message:
            print("❌ Migration message required. Use --message or -m")
            return 1
        db_manager.create_migration(args.message, args.database)
        
    elif args.command == 'upgrade':
        db_manager.upgrade_databases(args.database)
        
    elif args.command == 'status':
        db_manager.show_status(args.database)
        
    elif args.command == 'test':
        db_manager.test_connections()
    
    print(f"\n✅ {args.command} completed successfully!")
    return 0

if __name__ == '__main__':
    import argparse
    sys.exit(main())
