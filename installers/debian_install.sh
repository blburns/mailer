#!/bin/bash

# Postfix Manager - Debian/Ubuntu Installation Script
# This script installs and configures the Postfix management application on Debian-based systems

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration variables
APP_NAME="postfix-manager"
APP_USER="postfix-manager"
APP_GROUP="postfix-manager"
APP_HOME="/opt/postfix-manager"
APP_CONFIG="/etc/postfix-manager"
APP_LOG="/var/log/postfix-manager"
APP_SERVICE="postfix-manager"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root"
        exit 1
    fi
}

# Function to detect OS version
detect_os() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    else
        print_error "Cannot detect OS version"
        exit 1
    fi
    
    print_status "Detected OS: $OS $VER"
    
    # Check if it's a supported Debian-based system
    if [[ "$OS" != "Ubuntu" && "$OS" != "Debian GNU/Linux" ]]; then
        print_error "This script is designed for Debian/Ubuntu systems only"
        exit 1
    fi
}

# Function to update system packages
update_system() {
    print_status "Updating system packages..."
    apt update
    apt upgrade -y
}

# Function to install required packages
install_packages() {
    print_status "Installing required packages..."
    
    # Core packages
    apt install -y python3 python3-pip python3-venv python3-dev
    
    # System packages
    apt install -y nginx supervisor
    
    # Mail server packages
    apt install -y postfix postfix-ldap dovecot-core dovecot-imapd dovecot-pop3d dovecot-ldap
    
    # LDAP packages
    apt install -y slapd ldap-utils
    
    # Additional dependencies
    apt install -y build-essential libldap2-dev libsasl2-dev libssl-dev
    
    print_success "Required packages installed successfully"
}

# Function to create application user and group
create_app_user() {
    print_status "Creating application user and group..."
    
    if ! getent group $APP_GROUP > /dev/null 2>&1; then
        groupadd $APP_GROUP
    fi
    
    if ! getent passwd $APP_USER > /dev/null 2>&1; then
        useradd -r -g $APP_GROUP -d $APP_HOME -s /bin/bash $APP_USER
    fi
    
    print_success "Application user created successfully"
}

# Function to create application directories
create_directories() {
    print_status "Creating application directories..."
    
    mkdir -p $APP_HOME
    mkdir -p $APP_CONFIG
    mkdir -p $APP_LOG
    mkdir -p $APP_HOME/logs
    
    # Set ownership
    chown -R $APP_USER:$APP_GROUP $APP_HOME
    chown -R $APP_USER:$APP_GROUP $APP_CONFIG
    chown -R $APP_USER:$APP_GROUP $APP_LOG
    
    # Set permissions
    chmod 755 $APP_HOME
    chmod 755 $APP_CONFIG
    chmod 755 $APP_LOG
    chmod 755 $APP_HOME/logs
    
    print_success "Application directories created successfully"
}

# Function to install Python application
install_python_app() {
    print_status "Installing Python application..."
    
    # Copy application files
    cp -r app $APP_HOME/
    cp -r requirements.txt $APP_HOME/
    cp -r run.py $APP_HOME/
    
    # Create virtual environment
    cd $APP_HOME
    python3 -m venv venv
    source venv/bin/activate
    
    # Install Python dependencies
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Deactivate virtual environment
    deactivate
    
    # Set ownership
    chown -R $APP_USER:$APP_GROUP $APP_HOME
    
    print_success "Python application installed successfully"
}

# Function to configure Postfix
configure_postfix() {
    print_status "Configuring Postfix..."
    
    # Backup original configuration
    cp /etc/postfix/main.cf /etc/postfix/main.cf.backup.$(date +%Y%m%d_%H%M%S)
    
    # Create virtual domains file
    touch /etc/postfix/virtual_domains
    postmap /etc/postfix/virtual_domains
    
    # Update main.cf for virtual hosting
    cat >> /etc/postfix/main.cf << EOF

# Virtual hosting configuration
virtual_mailbox_domains = hash:/etc/postfix/virtual_domains
virtual_mailbox_base = /home/vmail
virtual_mailbox_maps = hash:/etc/postfix/virtual_mailbox_maps
virtual_minimum_uid = 100
virtual_uid_maps = static:5000
virtual_gid_maps = static:5000
virtual_transport = lmtp:unix:private/dovecot-lmtp
EOF
    
    # Create virtual mailbox maps
    touch /etc/postfix/virtual_mailbox_maps
    postmap /etc/postfix/virtual_mailbox_maps
    
    # Set permissions
    chown postfix:postfix /etc/postfix/virtual_domains*
    chmod 644 /etc/postfix/virtual_domains*
    
    print_success "Postfix configured successfully"
}

# Function to configure Dovecot
configure_dovecot() {
    print_status "Configuring Dovecot..."
    
    # Backup original configuration
    cp /etc/dovecot/dovecot.conf /etc/dovecot/dovecot.conf.backup.$(date +%Y%m%d_%H%M%S)
    
    # Create dovecot configuration
    cat > /etc/dovecot/dovecot.conf << EOF
# Dovecot configuration for virtual hosting
protocols = imap pop3 lmtp

# Listen on all interfaces
listen = *

# SSL configuration
ssl = no

# Authentication
disable_plaintext_auth = no
auth_mechanisms = plain login

# Mail location
mail_location = maildir:/home/vmail/domains/%d/%n/Maildir

# User and group
mail_uid = 5000
mail_gid = 5000

# LMTP configuration
service lmtp {
    inet_listener lmtp {
        port = 24
    }
}

# IMAP configuration
protocol imap {
    mail_plugins = quota
}

# POP3 configuration
protocol pop3 {
    mail_plugins = quota
}

# Authentication configuration
passdb {
    driver = ldap
    args = /etc/dovecot/dovecot-ldap.conf
}

userdb {
    driver = ldap
    args = /etc/dovecot/dovecot-ldap.conf
}
EOF
    
    # Create LDAP configuration
    cat > /etc/dovecot/dovecot-ldap.conf << EOF
# Dovecot LDAP configuration
hosts = 127.0.0.1
ldap_version = 3
auth_bind = yes
dn = cn=admin,dc=example,dc=tld
dnpass = secret
base = o=hosting,dc=example,dc=tld
user_attrs = uid=uid,homeDirectory=home,uidNumber=uidNumber,gidNumber=gidNumber
pass_attrs = uid=uid,userPassword=password
pass_filter = (&(objectClass=VirtualMailAccount)(uid=%u))
user_filter = (&(objectClass=VirtualMailAccount)(uid=%u))
EOF
    
    # Set permissions
    chown root:dovecot /etc/dovecot/dovecot-ldap.conf
    chmod 640 /etc/dovecot/dovecot-ldap.conf
    
    print_success "Dovecot configured successfully"
}

# Function to configure OpenLDAP
configure_ldap() {
    print_status "Configuring OpenLDAP..."
    
    # Set admin password
    ADMIN_PASSWORD="secret"
    HASHED_PASSWORD=$(slappasswd -h {MD5} -s "$ADMIN_PASSWORD")
    
    # Create base LDIF
    cat > /tmp/base.ldif << EOF
dn: dc=example,dc=tld
objectClass: dcObject
objectClass: organization
dc: example
o: Example Organization

dn: cn=admin,dc=example,dc=tld
objectClass: simpleSecurityObject
objectClass: organizationalRole
cn: admin
userPassword: $HASHED_PASSWORD
description: LDAP administrator

dn: o=hosting,dc=example,dc=tld
objectClass: organization
objectClass: top
o: hosting
description: Hosting Organization

dn: cn=vmail,o=hosting,dc=example,dc=tld
objectClass: simpleSecurityObject
objectClass: organizationalRole
cn: vmail
userPassword: {MD5}M267sheb6qc0Ck8WIPOvQA==
description: Read only account
EOF
    
    # Load base configuration
    ldapadd -Y EXTERNAL -H ldapi:/// -f /tmp/base.ldif
    
    # Clean up
    rm /tmp/base.ldif
    
    print_success "OpenLDAP configured successfully"
}

# Function to create systemd service
create_systemd_service() {
    print_status "Creating systemd service..."
    
    cat > /etc/systemd/system/$APP_SERVICE.service << EOF
[Unit]
Description=Postfix Manager Web Application
After=network.target postfix.service dovecot.service slapd.service

[Service]
Type=simple
User=$APP_USER
Group=$APP_GROUP
WorkingDirectory=$APP_HOME
Environment=PATH=$APP_HOME/venv/bin
ExecStart=$APP_HOME/venv/bin/python run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd and enable service
    systemctl daemon-reload
    systemctl enable $APP_SERVICE
    
    print_success "Systemd service created successfully"
}

# Function to configure Nginx
configure_nginx() {
    print_status "Configuring Nginx..."
    
    # Create Nginx configuration
    cat > /etc/nginx/sites-available/$APP_NAME << EOF
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /static {
        alias $APP_HOME/app/static;
        expires 30d;
    }
}
EOF
    
    # Enable site
    ln -sf /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/
    
    # Remove default site
    rm -f /etc/nginx/sites-enabled/default
    
    # Test configuration
    nginx -t
    
    print_success "Nginx configured successfully"
}

# Function to create vmail user and directories
setup_vmail() {
    print_status "Setting up vmail user and directories..."
    
    # Create vmail user
    if ! getent passwd vmail > /dev/null 2>&1; then
        useradd -r -d /home/vmail -s /bin/bash vmail
    fi
    
    # Create vmail directories
    mkdir -p /home/vmail/domains
    chown -R vmail:vmail /home/vmail
    
    print_success "Vmail setup completed successfully"
}

# Function to create application configuration
create_app_config() {
    print_status "Creating application configuration..."
    
    cat > $APP_CONFIG/app.conf << EOF
# Postfix Manager Configuration
FLASK_ENV=production
SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=sqlite:///$APP_HOME/postfix_manager.db
POSTFIX_CONFIG_DIR=/etc/postfix
DOVECOT_CONFIG_DIR=/etc/dovecot
LDAP_CONFIG_DIR=/etc/ldap
VMAIL_HOME=/home/vmail
EOF
    
    # Set permissions
    chown $APP_USER:$APP_GROUP $APP_CONFIG/app.conf
    chmod 600 $APP_CONFIG/app.conf
    
    print_success "Application configuration created successfully"
}

# Function to initialize database
initialize_database() {
    print_status "Initializing database..."
    
    cd $APP_HOME
    
    # Create admin user
    cat > create_admin.py << EOF
from app import create_app, db
from app.models import User, UserRole
from app.extensions import bcrypt

app = create_app()
with app.app_context():
    db.create_all()
    
    # Create admin user if it doesn't exist
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@example.com',
            password_hash=bcrypt.generate_password_hash('admin123').decode('utf-8'),
            role=UserRole.ADMIN
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin user created: admin/admin123")
    else:
        print("Admin user already exists")
EOF
    
    # Run database initialization
    source venv/bin/activate
    python create_admin.py
    deactivate
    
    # Clean up
    rm create_admin.py
    
    print_success "Database initialized successfully"
}

# Function to start services
start_services() {
    print_status "Starting services..."
    
    # Start and enable services
    systemctl start slapd
    systemctl enable slapd
    
    systemctl start postfix
    systemctl enable postfix
    
    systemctl start dovecot
    systemctl enable dovecot
    
    systemctl start nginx
    systemctl enable nginx
    
    systemctl start $APP_SERVICE
    systemctl enable $APP_SERVICE
    
    print_success "All services started successfully"
}

# Function to display installation summary
display_summary() {
    echo
    echo "=========================================="
    echo "           INSTALLATION COMPLETE          "
    echo "=========================================="
    echo
    echo "Postfix Manager has been installed successfully!"
    echo
    echo "Application Details:"
    echo "  - Home Directory: $APP_HOME"
    echo "  - Configuration: $APP_CONFIG"
    echo "  - Logs: $APP_LOG"
    echo "  - Service: $APP_SERVICE"
    echo
    echo "Access Information:"
    echo "  - Web Interface: http://$(hostname -I | awk '{print $1}')"
    echo "  - Default Admin: admin/admin123"
    echo
    echo "Services Status:"
    echo "  - Postfix: $(systemctl is-active postfix)"
    echo "  - Dovecot: $(systemctl is-active dovecot)"
    echo "  - OpenLDAP: $(systemctl is-active slapd)"
    echo "  - Web App: $(systemctl is-active $APP_SERVICE)"
    echo "  - Nginx: $(systemctl is-active nginx)"
    echo
    echo "Next Steps:"
    echo "  1. Change the default admin password"
    echo "  2. Configure your mail domains"
    echo "  3. Set up SSL certificates"
    echo "  4. Configure firewall rules"
    echo
    echo "For support, check the documentation or logs in $APP_LOG"
    echo
}

# Main installation function
main() {
    echo "=========================================="
    echo "      Postfix Manager Installation        "
    echo "           Debian/Ubuntu Edition          "
    echo "=========================================="
    echo
    
    check_root
    detect_os
    update_system
    install_packages
    create_app_user
    create_directories
    install_python_app
    configure_postfix
    configure_dovecot
    configure_ldap
    create_systemd_service
    configure_nginx
    setup_vmail
    create_app_config
    initialize_database
    start_services
    display_summary
}

# Run main function
main "$@"
