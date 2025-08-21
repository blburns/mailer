"""
Database Models for Postfix Manager
"""

from app.extensions import db
from datetime import datetime
import enum
from flask_login import UserMixin


class UserRole(enum.Enum):
    ADMIN = "admin"
    USER = "user"
    READONLY = "readonly"


class User(UserMixin, db.Model):
    """User model for authentication and authorization."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(UserRole), default=UserRole.USER)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<User {self.username}>'


class MailDomain(db.Model):
    """Mail domain configuration."""
    __tablename__ = 'mail_domains'
    
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(255), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Postfix configuration
    postfix_enabled = db.Column(db.Boolean, default=True)
    dovecot_enabled = db.Column(db.Boolean, default=True)
    
    # LDAP configuration
    ldap_base_dn = db.Column(db.String(255))
    ldap_admin_dn = db.Column(db.String(255))
    ldap_admin_password = db.Column(db.String(255))  # Encrypted
    
    def __repr__(self):
        return f'<MailDomain {self.domain}>'


class MailUser(db.Model):
    """Mail user configuration."""
    __tablename__ = 'mail_users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    domain_id = db.Column(db.Integer, db.ForeignKey('mail_domains.id'), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Mailbox configuration
    quota = db.Column(db.Integer, default=0)  # 0 = unlimited
    home_dir = db.Column(db.String(255))
    
    # LDAP attributes
    ldap_dn = db.Column(db.String(255))
    
    # Relationships
    domain = db.relationship('MailDomain', backref=db.backref('users', lazy=True))
    
    def __repr__(self):
        return f'<MailUser {self.username}@{self.domain.domain}>'


class SystemConfig(db.Model):
    """System configuration settings."""
    __tablename__ = 'system_config'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(255), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.String(500))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SystemConfig {self.key}>'


class AuditLog(db.Model):
    """Audit log for system changes."""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(255), nullable=False)
    resource_type = db.Column(db.String(100))
    resource_id = db.Column(db.String(100))
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('audit_logs', lazy=True))
    
    def __repr__(self):
        return f'<AuditLog {self.action} by {self.user_id}>'
