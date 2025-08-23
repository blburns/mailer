# Database Initialization Scripts

## Overview

Postfix Manager provides multiple ways to initialize and manage databases, supporting SQLite, MySQL/MariaDB, and PostgreSQL. All scripts now use the new database configuration system for consistency and flexibility.

## Available Scripts

### 1. Python Scripts

#### `scripts/init_db.py` - Generic Database Initialization
**Purpose**: Initialize any database type using the new configuration system
**Supports**: SQLite, MySQL/MariaDB, PostgreSQL
**Usage**: `python3 scripts/init_db.py`

**Features**:
- Automatically detects database type from environment
- Uses new `DB_TYPE` configuration system
- Creates all database tables
- Works in any environment (development, staging, production)

#### `scripts/init_vm_db.py` - VM-Specific Database Initialization
**Purpose**: Initialize database on VM environments with proper paths and permissions
**Supports**: SQLite, MySQL/MariaDB, PostgreSQL
**Usage**: `python3 scripts/init_vm_db.py`

**Features**:
- VM-appropriate paths (`/opt/postfix-manager/app/data/db/`)
- Automatic permission fixing
- Database type detection and validation
- Comprehensive error handling and troubleshooting

### 2. Shell Scripts

#### `scripts/init_db.sh` - Generic Shell Script
**Purpose**: User-friendly shell script for database initialization
**Supports**: SQLite, MySQL/MariaDB, PostgreSQL
**Usage**: `./scripts/init_db.sh`

**Features**:
- Colored output for better readability
- Automatic environment file creation from examples
- Configuration validation before initialization
- Clear next steps guidance

#### `scripts/init_vm_db.sh` - VM Shell Script
**Purpose**: VM-optimized shell script with additional checks
**Supports**: SQLite, MySQL/MariaDB, PostgreSQL
**Usage**: `./scripts/init_vm_db.sh`

**Features**:
- VM environment setup (production mode, debug off)
- Database client installation (MySQL/PostgreSQL)
- Connection testing for remote databases
- Permission management for SQLite
- Comprehensive validation

### 3. Management Script

#### `scripts/manage_db.py` - Database Management Tool
**Purpose**: Comprehensive database management with multiple commands
**Supports**: All database types
**Usage**: `python3 scripts/manage_db.py [command]`

**Commands**:
- `init` - Initialize database and create tables
- `migrate` - Run pending migrations
- `upgrade` - Upgrade to latest migration
- `create` - Create new migration
- `backup` - Create database backup
- `seed` - Seed with test data
- `reset` - Reset database (drop and recreate)

## Database Type Support

### SQLite (Development/Testing)
```bash
# .env configuration
DB_TYPE=sqlite
DB_NAME=postfix_manager.db
DB_DIRECTORY=app/data/db
```

**Initialization**: 
- Creates database file automatically
- Sets proper permissions
- No external dependencies

### MySQL/MariaDB (Production)
```bash
# .env configuration
DB_TYPE=mysql
DB_HOSTNAME=localhost
DB_PORT=3306
DB_USERNAME=postfix_manager
DB_PASSWORD=secure_password
DB_NAME=postfix_manager
```

**Initialization**:
- Requires existing database
- Tests connection before proceeding
- Installs MySQL client if needed
- Creates all tables

### PostgreSQL (Production)
```bash
# .env configuration
DB_TYPE=postgresql
DB_HOSTNAME=localhost
DB_PORT=5432
DB_USERNAME=postfix_manager
DB_PASSWORD=secure_password
DB_NAME=postfix_manager
```

**Initialization**:
- Requires existing database
- Tests connection before proceeding
- Installs PostgreSQL client if needed
- Creates all tables

## Usage Examples

### Development Environment
```bash
# 1. Copy environment file
cp env.example .env

# 2. Edit .env (optional - SQLite works out of the box)
# DB_TYPE=sqlite (default)

# 3. Initialize database
./scripts/init_db.sh

# 4. Create admin user
python3 scripts/create_admin.py

# 5. Start application
python3 run.py
```

### Production VM with MySQL
```bash
# 1. Copy environment file
cp env.conf.example .env

# 2. Edit .env with MySQL credentials
DB_TYPE=mysql
DB_HOSTNAME=db.example.com
DB_PORT=3306
DB_USERNAME=postfix_manager
DB_PASSWORD=secure_password
DB_NAME=postfix_manager

# 3. Initialize database
./scripts/init_vm_db.sh

# 4. Create admin user
python3 scripts/create_admin.py

# 5. Start service
sudo systemctl start postfix-manager
```

### Production VM with PostgreSQL
```bash
# 1. Copy environment file
cp env.conf.example .env

# 2. Edit .env with PostgreSQL credentials
DB_TYPE=postgresql
DB_HOSTNAME=db.example.com
DB_PORT=5432
DB_USERNAME=postfix_manager
DB_PASSWORD=secure_password
DB_NAME=postfix_manager

# 3. Initialize database
./scripts/init_vm_db.sh

# 4. Create admin user
python3 scripts/create_admin.py

# 5. Start service
sudo systemctl start postfix-manager
```

## Migration Support

### Alembic Configuration
Each database type has its own migration directory:
```
migrations/
├── sqlite/          # SQLite migrations
├── mysql/           # MySQL/MariaDB migrations
└── postgresql/      # PostgreSQL migrations
```

### Creating Migrations
```bash
# Create migration for current database type
python3 scripts/manage_db.py create -m "Add new table"

# Run migrations
python3 scripts/manage_db.py upgrade
```

## Troubleshooting

### Common Issues

1. **Permission Denied**
   ```bash
   # Fix SQLite permissions
   sudo chown -R $(whoami):$(id -gn) /opt/postfix-manager/app/data/db
   sudo chmod 755 /opt/postfix-manager/app/data/db
   ```

2. **Database Connection Failed**
   - Verify database server is running
   - Check hostname, port, and credentials
   - Ensure database exists
   - Verify user permissions

3. **Missing Dependencies**
   ```bash
   # Install MySQL client
   sudo apt-get install mysql-client  # Ubuntu/Debian
   sudo yum install mysql             # RHEL/CentOS

   # Install PostgreSQL client
   sudo apt-get install postgresql-client  # Ubuntu/Debian
   sudo yum install postgresql             # RHEL/CentOS
   ```

### Debug Mode
Enable SQLAlchemy echo to see SQL statements:
```bash
# .env
SQLALCHEMY_ECHO=true
```

## Best Practices

1. **Environment Files**: Never commit `.env` files to version control
2. **Database Credentials**: Use strong passwords and limit user permissions
3. **Backups**: Regular backups before major changes
4. **Testing**: Test database changes in development first
5. **Monitoring**: Monitor database performance and connections

## File Locations

- **Scripts**: `scripts/` directory
- **Environment Examples**: `env.example`, `env.conf.example`
- **Documentation**: `docs/DATABASE_SCRIPTS.md`
- **Database Config**: `app/extensions/database.py`
- **Migrations**: `migrations/[database_type]/`
