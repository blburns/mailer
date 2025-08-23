# Database Management Guide

This guide covers all aspects of database management for Postfix Manager, including setup, migrations, recovery, and troubleshooting.

## Table of Contents

- [Database Types](#database-types)
- [Initial Setup](#initial-setup)
- [Migration Management](#migration-management)
- [Database Recovery](#database-recovery)
- [Troubleshooting](#troubleshooting)
- [Make Commands](#make-commands)
- [Manual Commands](#manual-commands)
- [Recent Improvements](#recent-improvements)

## Recent Improvements

### Breadcrumb Navigation System

Postfix Manager now features an intelligent breadcrumb navigation system that provides:

- **Automatic Path-based Breadcrumbs**: Automatically generates breadcrumbs from URL paths
- **Programmatic Breadcrumbs**: Routes can set custom breadcrumbs for better user experience
- **Module-specific Breadcrumbs**: Each module (Mail, Dashboard, LDAP) has tailored breadcrumb patterns
- **Fallback System**: Seamlessly falls back to automatic breadcrumbs when custom ones aren't set

#### Breadcrumb Usage in Routes

```python
from app.utils.navigation import set_mail_breadcrumbs, set_dashboard_breadcrumbs

# Set breadcrumbs for mail management
@bp.route('/postfix')
@login_required
def postfix():
    set_mail_breadcrumbs('Postfix', request.path)
    return render_template('modules/mail/postfix.html')

# Set breadcrumbs for dashboard
@bp.route('/domains')
@login_required
def domains():
    set_dashboard_breadcrumbs('Domains', request.path)
    return render_template('modules/dashboard/domains.html')
```

### Enhanced Login Experience

The login page now features:

- **Minimal Navbar**: Clean, unobtrusive navbar with app branding
- **Theme Toggle**: Dark/light mode switch accessible before login
- **Seamless Integration**: Navbar blends with page background, no borders or background colors
- **Responsive Design**: Works perfectly on all device sizes

### Database Seeding Improvements

The database seeding system has been enhanced with:

- **Intelligent Duplicate Detection**: Won't fail on re-runs
- **Multi-database Support**: Works with SQLite, MySQL/MariaDB, and PostgreSQL
- **Better Error Handling**: Clear feedback and graceful fallbacks
- **Test Data Management**: Easy creation and management of test data

```bash
# Seed database with test data
DB_TYPE=postgresql make db-seed

# Or run directly
python3 scripts/manage_db.py seed
```

## Database Types

Postfix Manager supports multiple database types:

- **SQLite** (default, development)
- **MySQL/MariaDB** (production)
- **PostgreSQL** (production, recommended)

## Initial Setup

### 1. Environment Configuration

Create a `.env.vm` file on your VM with the appropriate database settings:

```bash
# For PostgreSQL (recommended)
DB_TYPE=postgresql
DB_HOSTNAME=localhost
DB_PORT=5432
DB_USERNAME=postfix_manager
DB_PASSWORD=your_secure_password
DB_NAME=postfix_manager

# For MySQL/MariaDB
DB_TYPE=mysql
DB_HOSTNAME=localhost
DB_PORT=3306
DB_USERNAME=postfix_manager
DB_PASSWORD=your_secure_password
DB_NAME=postfix_manager

# For SQLite (development)
DB_TYPE=sqlite
DB_NAME=postfix_manager.db
DB_DIRECTORY=app/data/db
```

### 2. Database Creation

#### PostgreSQL
```bash
# Connect as postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE postfix_manager;
CREATE USER postfix_manager WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE postfix_manager TO postfix_manager;
\q
```

#### MySQL/MariaDB
```bash
# Connect as root
mysql -u root -p

# Create database and user
CREATE DATABASE postfix_manager;
CREATE USER 'postfix_manager'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON postfix_manager.* TO 'postfix_manager'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

## Migration Management

### Overview

Postfix Manager uses Alembic for database migrations, with separate migration histories for each database type:

- `app/data/migrations/sqlite/` - SQLite migrations
- `app/data/migrations/mysql/` - MySQL/MariaDB migrations  
- `app/data/migrations/postgresql/` - PostgreSQL migrations

### Migration Commands

#### Generate New Migrations
```bash
# Generate migration for all database types
make migrate-generate MSG="Description of changes"

# Generate migration for specific database type
python scripts/migrate_all.py generate -m "Description of changes" sqlite
python scripts/migrate_all.py generate -m "Description of changes" mysql
python scripts/migrate_all.py generate -m "Description of changes" postgresql
```

#### Apply Migrations
```bash
# Upgrade all databases
make migrate-upgrade

# Upgrade specific database type
make migrate-upgrade-sqlite
make migrate-upgrade-mysql
make migrate-upgrade-pg
```

#### Check Migration Status
```bash
# Check all databases
make migrate-current

# Check specific database
python scripts/migrate_all.py current postgresql
```

#### View Migration History
```bash
# View history for all databases
make migrate-history

# View history for specific database
python scripts/migrate_all.py history postgresql
```

## Database Recovery

### Complete Database Loss

If your database is completely gone or corrupted:

#### Option 1: Migration Recovery (Recommended)
```bash
# This recreates all tables from migrations
make migrate-upgrade-pg      # For PostgreSQL
make migrate-upgrade-mysql   # For MySQL
make migrate-upgrade-sqlite  # For SQLite
```

#### Option 2: Manual Recovery
```bash
# 1. Ensure environment is configured
cat .env.vm

# 2. Recreate database schema
python scripts/migrate_all.py upgrade postgresql

# 3. Create admin user
python scripts/create_admin.py
```

#### Option 3: Complete Reset
```bash
# WARNING: This deletes all data
make db-reset
make migrate-upgrade-pg
```

### Partial Data Loss

If only some tables are missing:

```bash
# Check current migration status
make migrate-current

# Stamp database to specific revision if needed
cd app/data/migrations/postgresql
alembic stamp head

# Or upgrade to latest
alembic upgrade head
```

## Troubleshooting

### Common Issues

#### 1. "Can't locate revision" Error
**Problem**: Database has wrong migration history
**Solution**: 
```bash
# Stamp database to correct revision
cd app/data/migrations/postgresql
alembic stamp head
```

#### 2. "Relation already exists" Error
**Problem**: Tables exist but migration history is wrong
**Solution**:
```bash
# Mark migration as complete
cd app/data/migrations/postgresql
alembic stamp head
```

#### 3. Connection Pool Errors
**Problem**: SQLite pool settings applied to PostgreSQL
**Solution**: Fixed in code - ensure you're using latest version

#### 4. Permission Denied Errors
**Problem**: VM file permissions
**Solution**:
```bash
make sync-vm  # This fixes permissions automatically
```

### Database Connection Testing

```bash
# Test connection
make db-test

# Manual connection test
python -c "
from app import create_app
app = create_app()
with app.app_context():
    from app.extensions import db
    db.engine.execute('SELECT 1')
    print('Database connection successful!')
"
```

## Make Commands

### Database Management
```bash
make db-init          # Initialize database
make db-migrate       # Run migrations
make db-upgrade       # Upgrade schema
make db-downgrade     # Downgrade schema
make db-current       # Show current revision
make db-history       # Show migration history
make db-test          # Test database connection
make db-seed          # Seed with test data
make db-backup        # Create backup
make db-reset         # Reset database (WARNING: deletes all data)
make db-switch        # Switch database type
```

### Migration Management
```bash
make migrate-check        # Check migration environment
make migrate-generate     # Generate new migrations
make migrate-upgrade      # Upgrade all databases
make migrate-upgrade-sqlite   # Upgrade SQLite
make migrate-upgrade-mysql    # Upgrade MySQL
make migrate-upgrade-pg       # Upgrade PostgreSQL
make migrate-current      # Show current versions
make migrate-history      # Show migration history
```

### Development Setup
```bash
make dev-setup           # Complete development setup
make prod-setup          # Production setup
make sync-vm             # Sync code to VM
```

## Manual Commands

### Alembic Commands

#### From Project Root
```bash
# PostgreSQL
cd app/data/migrations/postgresql
PYTHONPATH=/path/to/project FLASK_APP=/path/to/project/run.py alembic upgrade head

# MySQL
cd app/data/migrations/mysql
PYTHONPATH=/path/to/project FLASK_APP=/path/to/project/run.py alembic upgrade head

# SQLite
cd app/data/migrations/sqlite
PYTHONPATH=/path/to/project FLASK_APP=/path/to/project/run.py alembic upgrade head
```

#### From Migration Directory
```bash
# Set environment variables
export PYTHONPATH=/path/to/project
export FLASK_APP=/path/to/project/run.py

# Run Alembic commands
alembic upgrade head
alembic current
alembic history
alembic stamp head
```

### Database Scripts

```bash
# Initialize database
python scripts/init_db.py

# Initialize VM database
python scripts/init_vm_db.py

# Create admin user
python scripts/create_admin.py

# Seed test data (now properly loads .env files)
python scripts/seed_test_data.py --verbose --count 10

# Manage migrations
python scripts/migrate_all.py upgrade postgresql
python scripts/migrate_all.py current all
python scripts/migrate_all.py history all
```

### Test Data Seeding

The `seed_test_data.py` script now properly loads environment variables from `.env` files:

```bash
# Basic seeding
python scripts/seed_test_data.py

# Verbose output with custom count
python scripts/seed_test_data.py --verbose --count 20

# Clear existing data before seeding
python scripts/seed_test_data.py --clear --count 15
```

**Note**: The script automatically detects your database type from `.env` files and connects to the appropriate database.

## Best Practices

### 1. Always Backup Before Major Changes
```bash
make db-backup
```

### 2. Test Migrations in Development First
```bash
# Test on SQLite first
make migrate-upgrade-sqlite
# Then on production database
make migrate-upgrade-pg
```

### 3. Use Environment-Specific Configs
- Development: `.env` (SQLite)
- Production: `.env.vm` (PostgreSQL/MySQL)

### 4. Monitor Migration Status
```bash
# Regular checks
make migrate-current
make db-test
```

### 5. Version Control Migrations
- Always commit migration files
- Never modify existing migrations
- Create new migrations for schema changes

## Emergency Recovery

### Complete System Recovery
```bash
# 1. Stop application
pkill -f run.py

# 2. Backup existing data (if any)
make db-backup

# 3. Reset database
make db-reset

# 4. Recreate schema
make migrate-upgrade-pg

# 5. Create admin user
python scripts/create_admin.py

# 6. Restart application
python run.py &
```

### Data Recovery from Backup
```bash
# Restore from backup
make db-restore BACKUP_FILE=backup_file.sql

# Or manually restore
psql -U postfix_manager -d postfix_manager < backup_file.sql
```

## Support

If you encounter issues not covered in this guide:

1. Check the application logs: `app/data/logs/`
2. Verify environment configuration: `.env.vm`
3. Test database connectivity: `make db-test`
4. Check migration status: `make migrate-current`
5. Review this documentation for similar issues

For additional help, check the main [README.md](../README.md) or create an issue in the project repository.
