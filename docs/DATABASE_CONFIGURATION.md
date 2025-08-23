# Database Configuration Guide

## Overview

Postfix Manager now uses a new database configuration system that automatically generates database URIs from environment variables. This replaces the old `DATABASE_URL` system with a more flexible and secure approach.

## Environment Variables

### Core Database Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DB_TYPE` | Yes | `sqlite` | Database type: `sqlite`, `mysql`, `mariadb`, `postgresql` |
| `DB_NAME` | Yes | `postfix_manager.db` | Database name |
| `DB_DIRECTORY` | SQLite only | `app/data/db` | Directory for SQLite database files |

### MySQL/MariaDB Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DB_HOSTNAME` | Yes* | `localhost` | Database hostname |
| `DB_PORT` | Yes* | `3306` | Database port |
| `DB_USERNAME` | Yes* | `postfix_manager` | Database username |
| `DB_PASSWORD` | Yes* | `postfix_manager` | Database password |
| `DB_USE_UNIX_SOCKET` | No | `false` | Use Unix socket instead of TCP |
| `DB_UNIX_SOCKET` | No* | None | Unix socket path (if using socket) |

*Required only when `DB_TYPE` is `mysql` or `mariadb`

### PostgreSQL Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DB_HOSTNAME` | Yes* | `localhost` | Database hostname |
| `DB_PORT` | Yes* | `5432` | Database port |
| `DB_USERNAME` | Yes* | `postfix_manager` | Database username |
| `DB_PASSWORD` | Yes* | `postfix_manager` | Database password |

*Required only when `DB_TYPE` is `postgresql`

### Connection Pool Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_POOL_SIZE` | `10` | Connection pool size |
| `DB_MAX_OVERFLOW` | `20` | Maximum overflow connections |
| `DB_POOL_PRE_PING` | `true` | Test connections before use |
| `DB_POOL_RECYCLE` | `3600` | Connection recycle time (seconds) |
| `DB_POOL_TIMEOUT` | `30` | Connection timeout (seconds) |

### SQLAlchemy Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `SQLALCHEMY_TRACK_MODIFICATIONS` | `false` | Track modifications (deprecated) |
| `SQLALCHEMY_ECHO` | `false` | Echo SQL statements to console |

## Configuration Examples

### SQLite (Development)

```bash
# .env
DB_TYPE=sqlite
DB_NAME=postfix_manager.db
DB_DIRECTORY=app/data/db
```

### MySQL/MariaDB (Production)

```bash
# .env
DB_TYPE=mysql
DB_HOSTNAME=db.example.com
DB_PORT=3306
DB_USERNAME=postfix_manager
DB_PASSWORD=secure_password_here
DB_NAME=postfix_manager

# Connection pool settings
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_POOL_PRE_PING=true
DB_POOL_RECYCLE=3600
DB_POOL_TIMEOUT=30
```

### PostgreSQL (Production)

```bash
# .env
DB_TYPE=postgresql
DB_HOSTNAME=db.example.com
DB_PORT=5432
DB_USERNAME=postfix_manager
DB_PASSWORD=secure_password_here
DB_NAME=postfix_manager

# Connection pool settings
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_POOL_PRE_PING=true
DB_POOL_RECYCLE=3600
DB_POOL_TIMEOUT=30
```

### MySQL with Unix Socket

```bash
# .env
DB_TYPE=mysql
DB_NAME=postfix_manager
DB_USE_UNIX_SOCKET=true
DB_UNIX_SOCKET=/var/run/mysqld/mysqld.sock
```

## Migration from Old System

### Old System (DATABASE_URL)
```bash
# .env
DATABASE_URL=mysql://user:pass@localhost:3306/dbname
```

### New System
```bash
# .env
DB_TYPE=mysql
DB_HOSTNAME=localhost
DB_PORT=3306
DB_USERNAME=user
DB_PASSWORD=pass
DB_NAME=dbname
```

## Benefits of New System

1. **Security**: No database credentials in connection strings
2. **Flexibility**: Easy to switch between database types
3. **Environment-specific**: Different configs for dev/staging/prod
4. **Validation**: Automatic validation of required parameters
5. **Connection Pooling**: Built-in connection pool configuration
6. **Unix Socket Support**: Native MySQL Unix socket support

## Database Drivers

### Required (Core)
- **SQLite**: Built-in (no additional driver needed)
- **MySQL/MariaDB**: `PyMySQL`
- **PostgreSQL**: `psycopg2-binary`

### Optional (Advanced)
- **Oracle**: `cx_Oracle`
- **SQL Server**: `pyodbc` or `pymssql`
- **Firebird**: `fdb`
- **IBM DB2**: `ibm_db_sa`
- **Amazon Redshift**: `psycopg2-binary`

## Troubleshooting

### Common Issues

1. **Missing Environment Variables**: Check that all required variables for your database type are set
2. **Connection Refused**: Verify hostname, port, and firewall settings
3. **Authentication Failed**: Check username and password
4. **Database Not Found**: Ensure the database exists and user has access

### Debug Mode

Enable SQLAlchemy echo to see generated SQL:
```bash
# .env
SQLALCHEMY_ECHO=true
```

### Connection Testing

The system automatically validates database connections and provides detailed error messages for configuration issues.

## File Locations

- **Environment Examples**: `env.example`, `env.conf.example`
- **Database Configuration**: `app/extensions/database.py`
- **Documentation**: `docs/DATABASE_CONFIGURATION.md`
