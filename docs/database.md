# Database Documentation

## Overview

Postfix Manager uses a relational database to store application data, user information, mail server configurations, and audit logs. The database is designed with a modular approach that supports the application's blueprint-based architecture.

## Database Technology

### Primary Database
- **Development**: SQLite3 (file-based, easy development)
- **Production**: PostgreSQL (scalable, enterprise-ready)

### ORM Framework
- **SQLAlchemy**: Python ORM for database operations
- **Flask-SQLAlchemy**: Flask integration for SQLAlchemy
- **Alembic**: Database migration management

## Database Schema

### Core Tables

#### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

**Fields**:
- `id`: Unique identifier for the user
- `username`: Unique username for authentication
- `email`: User's email address
- `password_hash`: Bcrypt-hashed password
- `role`: User role (admin, user, readonly)
- `status`: Account status (active, suspended, deleted)
- `created_at`: Account creation timestamp
- `updated_at`: Last update timestamp
- `last_login`: Last login timestamp
- `is_active`: Boolean flag for account status

#### Domains Table
```sql
CREATE TABLE domains (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) UNIQUE NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    quota_limit BIGINT DEFAULT 1073741824, -- 1GB in bytes
    quota_used BIGINT DEFAULT 0,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    FOREIGN KEY (created_by) REFERENCES users(id)
);
```

**Fields**:
- `id`: Unique identifier for the domain
- `name`: Domain name (e.g., example.com)
- `status`: Domain status (active, suspended, deleted)
- `quota_limit`: Total storage quota in bytes
- `quota_used`: Current storage usage in bytes
- `description`: Optional domain description
- `created_at`: Domain creation timestamp
- `updated_at`: Last update timestamp
- `created_by`: User who created the domain

#### Mailboxes Table
```sql
CREATE TABLE mailboxes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(255) UNIQUE NOT NULL,
    domain_id INTEGER NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    quota_limit BIGINT DEFAULT 1073741824, -- 1GB in bytes
    quota_used BIGINT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    created_by INTEGER,
    FOREIGN KEY (domain_id) REFERENCES domains(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);
```

**Fields**:
- `id`: Unique identifier for the mailbox
- `username`: Full email address (user@domain.com)
- `domain_id`: Reference to the domain
- `password_hash`: Bcrypt-hashed password
- `quota_limit`: Individual mailbox quota in bytes
- `quota_used`: Current mailbox usage in bytes
- `status`: Mailbox status (active, suspended, deleted)
- `created_at`: Mailbox creation timestamp
- `updated_at`: Last update timestamp
- `last_login`: Last login timestamp
- `created_by`: User who created the mailbox

#### Audit Logs Table
```sql
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id INTEGER,
    details TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

**Fields**:
- `id`: Unique identifier for the log entry
- `user_id`: User who performed the action
- `action`: Action performed (create, update, delete, login, etc.)
- `resource_type`: Type of resource affected (user, domain, mailbox, etc.)
- `resource_id`: ID of the affected resource
- `details`: Additional details about the action
- `ip_address`: IP address of the user
- `user_agent`: User's browser/client information
- `timestamp`: When the action occurred

### Configuration Tables

#### Mail Server Configs Table
```sql
CREATE TABLE mail_server_configs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_name VARCHAR(50) NOT NULL, -- postfix, dovecot
    config_file VARCHAR(255) NOT NULL,
    config_data TEXT NOT NULL, -- JSON or text configuration
    backup_file VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER,
    FOREIGN KEY (updated_by) REFERENCES users(id)
);
```

**Fields**:
- `id`: Unique identifier for the configuration
- `service_name`: Name of the mail service
- `config_file`: Path to the configuration file
- `config_data`: Configuration content
- `backup_file`: Path to backup file
- `is_active`: Whether this configuration is active
- `created_at`: Configuration creation timestamp
- `updated_at`: Last update timestamp
- `updated_by`: User who last updated the configuration

#### LDAP Configs Table
```sql
CREATE TABLE ldap_configs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    server_name VARCHAR(255) NOT NULL,
    host VARCHAR(255) NOT NULL,
    port INTEGER DEFAULT 389,
    use_ssl BOOLEAN DEFAULT FALSE,
    bind_dn VARCHAR(255),
    bind_password VARCHAR(255),
    base_dn VARCHAR(255) NOT NULL,
    user_search_base VARCHAR(255),
    group_search_base VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER,
    FOREIGN KEY (updated_by) REFERENCES users(id)
);
```

**Fields**:
- `id`: Unique identifier for the LDAP configuration
- `server_name`: Display name for the LDAP server
- `host`: LDAP server hostname or IP
- `port`: LDAP server port
- `use_ssl`: Whether to use SSL/TLS
- `bind_dn`: Bind DN for authentication
- `bind_password`: Bind password (encrypted)
- `base_dn`: Base distinguished name
- `user_search_base`: Base DN for user searches
- `group_search_base`: Base DN for group searches
- `is_active`: Whether this configuration is active
- `created_at`: Configuration creation timestamp
- `updated_at`: Last update timestamp
- `updated_by`: User who last updated the configuration

### Relationship Tables

#### User Domains Table
```sql
CREATE TABLE user_domains (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    domain_id INTEGER NOT NULL,
    permissions TEXT, -- JSON permissions
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (domain_id) REFERENCES domains(id),
    UNIQUE(user_id, domain_id)
);
```

**Fields**:
- `id`: Unique identifier for the relationship
- `user_id`: Reference to the user
- `domain_id`: Reference to the domain
- `permissions`: JSON string of user permissions for the domain
- `created_at`: Relationship creation timestamp

## Database Models

### User Model
```python
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    domains = db.relationship('Domain', backref='creator', lazy='dynamic')
    mailboxes = db.relationship('Mailbox', backref='creator', lazy='dynamic')
    audit_logs = db.relationship('AuditLog', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
```

### Domain Model
```python
class Domain(db.Model):
    __tablename__ = 'domains'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    status = db.Column(db.String(20), default='active')
    quota_limit = db.Column(db.BigInteger, default=1073741824)  # 1GB
    quota_used = db.Column(db.BigInteger, default=0)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    mailboxes = db.relationship('Mailbox', backref='domain', lazy='dynamic')
    users = db.relationship('User', secondary='user_domains', backref='accessible_domains')
    
    @property
    def quota_usage_percent(self):
        if self.quota_limit == 0:
            return 0
        return (self.quota_used / self.quota_limit) * 100
    
    def update_quota_used(self):
        """Update quota usage based on mailbox usage"""
        total_used = sum(mailbox.quota_used for mailbox in self.mailboxes)
        self.quota_used = total_used
        db.session.commit()
```

### Mailbox Model
```python
class Mailbox(db.Model):
    __tablename__ = 'mailboxes'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    domain_id = db.Column(db.Integer, db.ForeignKey('domains.id'), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    quota_limit = db.Column(db.BigInteger, default=1073741824)  # 1GB
    quota_used = db.Column(db.BigInteger, default=0)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    domain = db.relationship('Domain', backref='mailboxes')
    creator = db.relationship('User', backref='created_mailboxes')
    
    @property
    def email(self):
        return self.username
    
    @property
    def quota_usage_percent(self):
        if self.quota_limit == 0:
            return 0
        return (self.quota_used / self.quota_limit) * 100
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
```

### Audit Log Model
```python
class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(50))
    resource_id = db.Column(db.Integer)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='audit_logs')
    
    @classmethod
    def log_action(cls, user_id, action, resource_type=None, resource_id=None, 
                   details=None, ip_address=None, user_agent=None):
        """Convenience method to log an action"""
        log_entry = cls(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.session.add(log_entry)
        db.session.commit()
        return log_entry
```

## Database Operations

### Initialization
```python
def init_db(app):
    """Initialize the database"""
    with app.app_context():
        db.create_all()
        
        # Create admin user if none exists
        if not User.query.filter_by(role='admin').first():
            admin = User(
                username='admin',
                email='admin@example.com',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
```

### Common Queries

#### Get Users with Pagination
```python
def get_users(page=1, per_page=20, status=None):
    query = User.query
    
    if status and status != 'all':
        query = query.filter_by(status=status)
    
    return query.paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
```

#### Get Domains with Usage
```python
def get_domains_with_usage():
    return db.session.query(
        Domain,
        func.count(Mailbox.id).label('mailbox_count'),
        func.sum(Mailbox.quota_used).label('total_used')
    ).outerjoin(Mailbox).group_by(Domain.id).all()
```

#### Get Mailbox Statistics
```python
def get_mailbox_statistics():
    return db.session.query(
        func.count(Mailbox.id).label('total_mailboxes'),
        func.sum(Mailbox.quota_used).label('total_used'),
        func.sum(Mailbox.quota_limit).label('total_limit'),
        func.avg(Mailbox.quota_used).label('avg_used')
    ).first()
```

## Database Migrations

### Using Alembic
```bash
# Initialize migrations
flask db init

# Create a new migration
flask db migrate -m "Add new table"

# Apply migrations
flask db upgrade

# Rollback migration
flask db downgrade
```

### Migration Example
```python
"""Add user preferences table

Revision ID: 001_add_user_preferences
Revises: 
Create Date: 2025-08-22 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001_add_user_preferences'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('user_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('theme', sa.String(length=20), nullable=True),
        sa.Column('language', sa.String(length=10), nullable=True),
        sa.Column('timezone', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('user_preferences')
```

## Backup and Recovery

### Backup Strategy
```python
def backup_database(backup_path):
    """Create database backup"""
    if current_app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite'):
        # SQLite backup
        import shutil
        db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        shutil.copy2(db_path, backup_path)
    else:
        # PostgreSQL backup
        import subprocess
        db_url = current_app.config['SQLALCHEMY_DATABASE_URI']
        subprocess.run([
            'pg_dump', '-f', backup_path, db_url
        ])
```

### Recovery Strategy
```python
def restore_database(backup_path):
    """Restore database from backup"""
    if current_app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite'):
        # SQLite restore
        import shutil
        db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        shutil.copy2(backup_path, db_path)
    else:
        # PostgreSQL restore
        import subprocess
        db_url = current_app.config['SQLALCHEMY_DATABASE_URI']
        subprocess.run([
            'psql', '-f', backup_path, db_url
        ])
```

## Performance Considerations

### Indexing Strategy
```sql
-- User lookups
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_status ON users(status);

-- Domain lookups
CREATE INDEX idx_domains_name ON domains(name);
CREATE INDEX idx_domains_status ON domains(status);

-- Mailbox lookups
CREATE INDEX idx_mailboxes_username ON mailboxes(username);
CREATE INDEX idx_mailboxes_domain_id ON mailboxes(domain_id);
CREATE INDEX idx_mailboxes_status ON mailboxes(status);

-- Audit log lookups
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
```

### Query Optimization
- Use `lazy='dynamic'` for large relationships
- Implement pagination for large result sets
- Use database indexes for frequently queried fields
- Consider caching for frequently accessed data
- Use database views for complex queries

## Security Considerations

### Password Security
- All passwords are hashed using bcrypt
- Password complexity requirements enforced
- Account lockout after failed attempts
- Secure password reset procedures

### Data Encryption
- Sensitive configuration data encrypted at rest
- Database connections use SSL/TLS
- API communications secured with HTTPS
- Audit logs include IP addresses and user agents

### Access Control
- Role-based access control (RBAC)
- Resource-level permissions
- Audit logging for all operations
- Session management and timeout

## Monitoring and Maintenance

### Database Health Checks
```python
def check_database_health():
    """Check database connectivity and performance"""
    try:
        # Test connection
        db.session.execute('SELECT 1')
        
        # Check table sizes
        table_sizes = {}
        for table in ['users', 'domains', 'mailboxes', 'audit_logs']:
            result = db.session.execute(f'SELECT COUNT(*) FROM {table}')
            table_sizes[table] = result.scalar()
        
        return {
            'status': 'healthy',
            'table_sizes': table_sizes,
            'timestamp': datetime.utcnow()
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow()
        }
```

### Maintenance Tasks
- Regular database backups
- Log rotation and cleanup
- Index optimization
- Statistics updates
- Vacuum operations (SQLite)

This database design provides a solid foundation for the Postfix Manager application, supporting all the required functionality while maintaining performance, security, and scalability.
