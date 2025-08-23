#!/usr/bin/env python3
"""
Unified Migration Management Script for Postfix Manager

This script allows you to:
1. Generate migrations for all database types simultaneously
2. Apply migrations to all database types
3. Manage migrations across SQLite, MySQL/MariaDB, and PostgreSQL

Usage:
    python3 scripts/migrate_all.py generate -m "Migration message"
    python3 scripts/migrate_all.py upgrade [database_type]
    python3 scripts/migrate_all.py downgrade [database_type] [revision]
    python3 scripts/migrate_all.py current [database_type]
    python3 scripts/migrate_all.py history [database_type]
    python3 scripts/migrate_all.py stamp [database_type] [revision]
    python3 scripts/migrate_all.py show [database_type]
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from typing import List, Optional

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Database types supported
DATABASE_TYPES = ['sqlite', 'mysql', 'postgresql']

class MigrationManager:
    """Manages migrations across all database types."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.migrations_dir = self.project_root / 'app' / 'data' / 'migrations'
        
    def get_migration_dir(self, db_type: str) -> Path:
        """Get the migration directory for a specific database type."""
        return self.migrations_dir / db_type
    
    def validate_database_type(self, db_type: str) -> bool:
        """Validate that the database type is supported."""
        if db_type not in DATABASE_TYPES:
            print(f"❌ Unsupported database type: {db_type}")
            print(f"   Supported types: {', '.join(DATABASE_TYPES)}")
            return False
        return True
    
    def check_migration_dir(self, db_type: str) -> bool:
        """Check if migration directory exists and is properly configured."""
        migration_dir = self.get_migration_dir(db_type)
        
        if not migration_dir.exists():
            print(f"❌ Migration directory not found: {migration_dir}")
            return False
        
        env_file = migration_dir / 'env.py'
        if not env_file.exists():
            print(f"❌ Migration environment file not found: {env_file}")
            return False
        
        versions_dir = migration_dir / 'versions'
        if not versions_dir.exists():
            print(f"❌ Migration versions directory not found: {versions_dir}")
            return False
        
        return True
    
    def run_alembic_command(self, db_type: str, command: str, args: List[str] = None) -> bool:
        """Run an Alembic command for a specific database type."""
        if not self.validate_database_type(db_type):
            return False
        
        if not self.check_migration_dir(db_type):
            return False
        
        migration_dir = self.get_migration_dir(db_type)
        cmd = ['alembic', command] + (args or [])
        
        print(f"🔄 Running Alembic command for {db_type}: {' '.join(cmd)}")
        
        # Set environment variables for Alembic
        env = os.environ.copy()
        env['PYTHONPATH'] = str(self.project_root)
        env['FLASK_APP'] = 'run.py'
        env['FLASK_ENV'] = 'development'
        
        try:
            result = subprocess.run(
                cmd,
                cwd=migration_dir,  # Run from the migration directory
                env=env,  # Pass the environment with PYTHONPATH
                capture_output=True,
                text=True,
                check=True
            )
            
            if result.stdout:
                print(f"✅ {db_type} - {command} completed successfully")
                if result.stdout.strip():
                    print(f"   Output: {result.stdout.strip()}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ {db_type} - {command} failed with exit code {e.returncode}")
            if e.stdout:
                print(f"   Stdout: {e.stdout.strip()}")
            if e.stderr:
                print(f"   Stderr: {e.stderr.strip()}")
            return False
    
    def generate_migration(self, message: str) -> bool:
        """Generate a new migration for all database types."""
        print(f"🚀 Generating migration: {message}")
        print("=" * 50)
        
        success_count = 0
        total_count = len(DATABASE_TYPES)
        
        for db_type in DATABASE_TYPES:
            print(f"\n📊 Processing {db_type}...")
            
            if self.run_alembic_command(db_type, 'revision', ['--autogenerate', '-m', message]):
                success_count += 1
                print(f"✅ Migration generated for {db_type}")
            else:
                print(f"❌ Failed to generate migration for {db_type}")
        
        print(f"\n📊 Migration Generation Summary:")
        print(f"   Successful: {success_count}/{total_count}")
        print(f"   Failed: {total_count - success_count}/{total_count}")
        
        if success_count == total_count:
            print("🎉 All migrations generated successfully!")
            print("\n📋 Next steps:")
            print("   1. Review generated migration files in migrations/[type]/versions/")
            print("   2. Edit if needed (add custom logic, fix issues)")
            print("   3. Run: python3 scripts/migrate_all.py upgrade [database_type]")
            print("   4. Or upgrade all: python3 scripts/migrate_all.py upgrade all")
        else:
            print("⚠️  Some migrations failed. Please check the errors above.")
        
        return success_count == total_count
    
    def upgrade_database(self, db_type: str) -> bool:
        """Upgrade a specific database to the latest migration."""
        if db_type == 'all':
            return self.upgrade_all_databases()
        
        if not self.validate_database_type(db_type):
            return False
        
        print(f"🔄 Upgrading {db_type} database...")
        return self.run_alembic_command(db_type, 'upgrade', ['head'])
    
    def upgrade_all_databases(self) -> bool:
        """Upgrade all databases to the latest migration."""
        print("🚀 Upgrading all databases to latest migration")
        print("=" * 50)
        
        success_count = 0
        total_count = len(DATABASE_TYPES)
        
        for db_type in DATABASE_TYPES:
            print(f"\n📊 Upgrading {db_type}...")
            
            if self.upgrade_database(db_type):
                success_count += 1
            else:
                print(f"❌ Failed to upgrade {db_type}")
        
        print(f"\n📊 Upgrade Summary:")
        print(f"   Successful: {success_count}/{total_count}")
        print(f"   Failed: {total_count - success_count}/{total_count}")
        
        return success_count == total_count
    
    def downgrade_database(self, db_type: str, revision: str) -> bool:
        """Downgrade a specific database to a specific revision."""
        if not self.validate_database_type(db_type):
            return False
        
        print(f"🔄 Downgrading {db_type} database to revision: {revision}")
        return self.run_alembic_command(db_type, 'downgrade', [revision])
    
    def show_current(self, db_type: str) -> bool:
        """Show current migration version for a database."""
        if not self.validate_database_type(db_type):
            return False
        
        print(f"📊 Current migration version for {db_type}:")
        return self.run_alembic_command(db_type, 'current')
    
    def show_history(self, db_type: str) -> bool:
        """Show migration history for a database."""
        if not self.validate_database_type(db_type):
            return False
        
        print(f"📊 Migration history for {db_type}:")
        return self.run_alembic_command(db_type, 'history')
    
    def stamp_database(self, db_type: str, revision: str) -> bool:
        """Stamp a database with a specific revision without running migrations."""
        if not self.validate_database_type(db_type):
            return False
        
        print(f"🏷️  Stamping {db_type} database with revision: {revision}")
        return self.run_alembic_command(db_type, 'stamp', [revision])
    
    def show_migration_info(self, db_type: str) -> bool:
        """Show detailed information about a migration."""
        if not self.validate_database_type(db_type):
            return False
        
        print(f"📊 Migration information for {db_type}:")
        return self.run_alembic_command(db_type, 'show', ['head'])
    
    def list_databases(self):
        """List all supported database types."""
        print("📊 Supported Database Types:")
        print("=" * 30)
        
        for db_type in DATABASE_TYPES:
            migration_dir = self.get_migration_dir(db_type)
            status = "✅ Configured" if self.check_migration_dir(db_type) else "❌ Not Configured"
            print(f"   {db_type:12} - {status}")
        
        print(f"\n📁 Migration directories:")
        for db_type in DATABASE_TYPES:
            migration_dir = self.get_migration_dir(db_type)
            print(f"   {db_type:12} - {migration_dir}")
    
    def check_environment(self):
        """Check if the environment is properly configured for migrations."""
        print("🔍 Checking migration environment...")
        print("=" * 40)
        
        # Check if we're in the right directory
        if not (self.project_root / 'run.py').exists():
            print("❌ Not in project root directory")
            return False
        
        # Check if migrations directory exists
        if not self.migrations_dir.exists():
            print("❌ Migrations directory not found")
            return False
        
        # Check each database type
        for db_type in DATABASE_TYPES:
            print(f"\n📊 Checking {db_type}...")
            
            if self.check_migration_dir(db_type):
                print(f"   ✅ {db_type} migration directory configured")
                
                # Check if there are any migration files
                versions_dir = self.get_migration_dir(db_type) / 'versions'
                migration_files = list(versions_dir.glob('*.py'))
                print(f"   📁 Migration files: {len(migration_files)}")
                
                if migration_files:
                    print(f"   📋 Latest: {max(migration_files, key=lambda x: x.stat().st_mtime).name}")
            else:
                print(f"   ❌ {db_type} migration directory not configured")
        
        return True

def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Unified Migration Management for Postfix Manager',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate migrations for all database types
  python3 scripts/migrate_all.py generate -m "Add users table"
  
  # Upgrade specific database
  python3 scripts/migrate_all.py upgrade sqlite
  
  # Upgrade all databases
  python3 scripts/migrate_all.py upgrade all
  
  # Show current version for all databases
  python3 scripts/migrate_all.py current all
  
  # Check environment
  python3 scripts/migrate_all.py check
        """
    )
    
    parser.add_argument('command', choices=[
        'generate', 'upgrade', 'downgrade', 'current', 'history',
        'stamp', 'show', 'list', 'check'
    ], help='Migration command to execute')
    
    parser.add_argument('database_type', nargs='?', 
                       choices=DATABASE_TYPES + ['all'],
                       help='Database type (or "all" for upgrade)')
    
    parser.add_argument('revision', nargs='?', 
                       help='Revision for downgrade/stamp commands')
    
    parser.add_argument('-m', '--message', 
                       help='Migration message (for generate command)')
    
    args = parser.parse_args()
    
    # Initialize migration manager
    manager = MigrationManager()
    
    # Set environment variables
    os.environ['FLASK_APP'] = 'run.py'
    os.environ['FLASK_ENV'] = 'development'
    
    print("🚀 Postfix Manager - Unified Migration Manager")
    print("=" * 50)
    
    try:
        if args.command == 'check':
            manager.check_environment()
            
        elif args.command == 'list':
            manager.list_databases()
            
        elif args.command == 'generate':
            if not args.message:
                print("❌ Migration message is required for generate command")
                print("Usage: python3 scripts/migrate_all.py generate -m 'Migration message'")
                return
            manager.generate_migration(args.message)
            
        elif args.command == 'upgrade':
            if not args.database_type:
                print("❌ Database type is required for upgrade command")
                print("Usage: python3 scripts/migrate_all.py upgrade [database_type|all]")
                return
            manager.upgrade_database(args.database_type)
            
        elif args.command == 'downgrade':
            if not args.database_type or not args.revision:
                print("❌ Database type and revision are required for downgrade command")
                print("Usage: python3 scripts/migrate_all.py downgrade [database_type] [revision]")
                return
            manager.downgrade_database(args.database_type, args.revision)
            
        elif args.command == 'current':
            if not args.database_type:
                print("❌ Database type is required for current command")
                print("Usage: python3 scripts/migrate_all.py current [database_type]")
                return
            if args.database_type == 'all':
                for db_type in DATABASE_TYPES:
                    print(f"\n📊 {db_type.upper()}:")
                    manager.show_current(db_type)
            else:
                manager.show_current(args.database_type)
                
        elif args.command == 'history':
            if not args.database_type:
                print("❌ Database type is required for history command")
                print("Usage: python3 scripts/migrate_all.py history [database_type]")
                return
            manager.show_history(args.database_type)
            
        elif args.command == 'stamp':
            if not args.database_type or not args.revision:
                print("❌ Database type and revision are required for stamp command")
                print("Usage: python3 scripts/migrate_all.py stamp [database_type] [revision]")
                return
            manager.stamp_database(args.database_type, args.revision)
            
        elif args.command == 'show':
            if not args.database_type:
                print("❌ Database type is required for show command")
                print("Usage: python3 scripts/migrate_all.py show [database_type]")
                return
            manager.show_migration_info(args.database_type)
            
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
