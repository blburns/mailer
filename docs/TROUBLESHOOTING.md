# Troubleshooting Guide

This guide covers common issues and their solutions for Postfix Manager.

## Table of Contents

- [Database Issues](#database-issues)
- [Authentication Issues](#authentication-issues)
- [Permission Issues](#permission-issues)
- [Migration Issues](#migration-issues)
- [Connection Issues](#connection-issues)
- [Common Error Messages](#common-error-messages)

## Database Issues

### Database Completely Gone

**Symptoms**: Cannot login, "relation does not exist" errors

**Solution**:
```bash
# Quick recovery using migrations
make migrate-upgrade-pg      # For PostgreSQL
make migrate-upgrade-mysql   # For MySQL
make migrate-upgrade-sqlite  # For SQLite

# Then create admin user
python scripts/create_admin.py
```

**Alternative Solution**:
```bash
# Complete reset (WARNING: deletes all data)
make db-reset
make migrate-upgrade-pg
python scripts/create_admin.py
```

### Migration History Mismatch

**Symptoms**: "Can't locate revision" errors

**Solution**:
```bash
# Stamp database to correct revision
cd app/data/migrations/postgresql
alembic stamp head

# Or from project root
python scripts/migrate_all.py stamp postgresql head
```

### Tables Exist But Migration Fails

**Symptoms**: "relation already exists" errors

**Solution**:
```bash
# Mark migration as complete
cd app/data/migrations/postgresql
alembic stamp head
```

## Authentication Issues

### Cannot Login After Database Reset

**Solution**:
```bash
# 1. Ensure database is created
make migrate-upgrade-pg

# 2. Create admin user
python scripts/create_admin.py

# 3. Use the credentials from the script output
```

### User Account Locked

**Solution**:
```bash
# Check user status in database
psql -U postfix_manager -d postfix_manager -c "SELECT username, is_active FROM users;"

# Reactivate user if needed
psql -U postfix_manager -d postfix_manager -c "UPDATE users SET is_active = true WHERE username = 'your_username';"
```

## Permission Issues

### Permission Denied on VM

**Symptoms**: "Permission denied" errors, cannot run scripts

**Solution**:
```bash
# Fix permissions automatically
make sync-vm

# Or manually fix virtual environment
chmod +x venv/bin/*
chmod 755 venv/bin
chmod 755 venv/lib
chmod 755 venv/include
```

### Cannot Access Data Directories

**Solution**:
```bash
# Set proper ownership
sudo chown -R www-data:www-data app/data/

# Set proper permissions
chmod 700 app/data/db app/data/sessions
chmod 755 app/data/logs app/data/cache app/data/backups
```

## Migration Issues

### Alembic Import Errors

**Symptoms**: "ModuleNotFoundError: No module named 'app'"

**Solution**:
```bash
# Set PYTHONPATH correctly
export PYTHONPATH=/path/to/project
export FLASK_APP=/path/to/project/run.py

# Run from migration directory
cd app/data/migrations/postgresql
alembic upgrade head
```

### Migration Configuration Errors

**Symptoms**: "configparser.InterpolationSyntaxError"

**Solution**:
```bash
# Check alembic.ini files for proper escaping
# Version format should be: version_num_format = %%04d
# Not: version_num_format = %04d
```

## Connection Issues

### Database Connection Failed

**Symptoms**: "connection refused" or "authentication failed"

**Solution**:
```bash
# 1. Check database service status
sudo systemctl status postgresql
sudo systemctl status mysql

# 2. Verify connection details in .env.vm
cat .env.vm

# 3. Test connection manually
psql -h localhost -U postfix_manager -d postfix_manager
```

### Connection Pool Errors

**Symptoms**: "Invalid argument(s) 'pool_size' sent to create_engine()"

**Solution**:
```bash
# This is fixed in the code - ensure you're using latest version
make sync-vm

# Or check that SQLAlchemy engine options are database-specific
```

## Common Error Messages

### "ERROR: Unexpected error: cannot import name 'init_csrf_config'"

**Solution**: Extension system issue - fixed in code
```bash
make sync-vm  # Update to latest version
```

### "ERROR: Unexpected error: 'StreamHandler' object has no attribute 'baseFilename'"

**Solution**: Logging configuration issue - fixed in code
```bash
make sync-vm  # Update to latest version
```

### "ERROR: Unexpected error: No module named 'app.mail'"

**Solution**: Blueprint import issue - fixed in code
```bash
make sync-vm  # Update to latest version
```

### "ERROR: Unexpected error: The name 'main' is already registered for this blueprint"

**Solution**: Duplicate blueprint registration - fixed in code
```bash
make sync-vm  # Update to latest version
```

### "ERROR: Could not find a version that satisfies the requirement"

**Solution**: Package version constraint issue - fixed in requirements.txt
```bash
# Update requirements
pip install -r requirements.txt --upgrade

# Or recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Quick Recovery Commands

### Complete System Recovery
```bash
# 1. Stop application
pkill -f run.py

# 2. Sync latest code
make sync-vm

# 3. Recreate database
make migrate-upgrade-pg

# 4. Create admin user
python scripts/create_admin.py

# 5. Restart application
python run.py &
```

### Database Recovery
```bash
# Check status
make migrate-current

# Recreate if needed
make migrate-upgrade-pg

# Test connection
make db-test
```

### Permission Recovery
```bash
# Fix all permissions
make sync-vm

# Or manually
chmod +x scripts/*.sh scripts/*.py run.py
chmod 700 app/data/db app/data/sessions
chmod 755 app/data/logs app/data/cache app/data/backups
```

## Getting Help

### 1. Check Logs
```bash
# Application logs
tail -f app/data/logs/app.log

# Error logs
tail -f app/data/logs/error.log

# Database logs
sudo tail -f /var/log/postgresql/postgresql-*.log
sudo tail -f /var/log/mysql/error.log
```

### 2. Verify Configuration
```bash
# Environment variables
cat .env.vm

# Database connection
make db-test

# Migration status
make migrate-current
```

### 3. Check Documentation
- [Database Management Guide](DATABASE_MANAGEMENT.md)
- [Main README](../README.md)
- [API Documentation](API_ENDPOINTS.md)

### 4. Common Commands Reference
```bash
# Database management
make migrate-upgrade-pg      # Recreate PostgreSQL
make migrate-current         # Check migration status
make db-test                # Test database connection

# System management
make sync-vm                # Sync code and fix permissions
make clean                  # Clean Python cache
make install                # Install dependencies

# Development
make run                    # Run development server
make test                   # Run tests
```

## Prevention Tips

### 1. Regular Backups
```bash
# Create regular backups
make db-backup

# Or set up automated backups
crontab -e
# Add: 0 2 * * * cd /opt/postfix-manager && make db-backup
```

### 2. Monitor System Health
```bash
# Regular health checks
make db-test
make migrate-current

# Check logs regularly
tail -n 100 app/data/logs/app.log
```

### 3. Test Changes in Development
```bash
# Always test migrations on SQLite first
make migrate-upgrade-sqlite

# Then apply to production
make migrate-upgrade-pg
```

### 4. Keep System Updated
```bash
# Regular updates
make sync-vm
pip install -r requirements.txt --upgrade
```

For additional help, check the main [README.md](../README.md) or create an issue in the project repository.
