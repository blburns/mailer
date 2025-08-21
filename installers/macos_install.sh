#!/bin/bash

# Postfix Manager - macOS Installation Script
# This script installs and configures the Postfix management application on macOS systems

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
APP_SERVICE="com.postfix-manager.service"

# Package manager selection
PACKAGE_MANAGER=""
PACKAGE_MANAGER_NAME=""

# Get the real user (not root when using sudo)
REAL_USER=${SUDO_USER:-$USER}
REAL_HOME=$(eval echo ~$REAL_USER)

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
        print_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

# Function to detect macOS version
detect_os() {
    if [[ "$OSTYPE" != "darwin"* ]]; then
        print_error "This script is designed for macOS systems only"
        exit 1
    fi
    
    # Get macOS version
    MACOS_VERSION=$(sw_vers -productVersion)
    MACOS_NAME=$(sw_vers -productName)
    
    print_status "Detected OS: $MACOS_NAME $MACOS_VERSION"
    
    # Check minimum macOS version (10.15 Catalina or later)
    if [[ $(echo "$MACOS_VERSION" | cut -d. -f1) -lt 10 ]] || \
       [[ $(echo "$MACOS_VERSION" | cut -d. -f1) -eq 10 && $(echo "$MACOS_VERSION" | cut -d. -f2) -lt 15 ]]; then
        print_error "macOS 10.15 (Catalina) or later is required"
        exit 1
    fi
}

# Function to detect available package managers
detect_package_managers() {
    print_status "Detecting available package managers..."
    
    HAS_HOMEBREW=false
    HAS_MACPORTS=false
    
    # Check Homebrew as real user with proper environment
    if sudo -u $REAL_USER bash -c 'command -v brew' &> /dev/null; then
        HAS_HOMEBREW=true
        BREW_VERSION=$(sudo -u $REAL_USER bash -c 'brew --version | head -n1')
        print_status "Homebrew detected: $BREW_VERSION"
    fi
    
    # Check MacPorts as real user
    if sudo -u $REAL_USER bash -c 'command -v port' &> /dev/null; then
        HAS_MACPORTS=true
        PORT_VERSION=$(sudo -u $REAL_USER bash -c 'port version | head -n1')
        print_status "MacPorts detected: $PORT_VERSION"
    fi
    
    if [[ "$HAS_HOMEBREW" == false && "$HAS_MACPORTS" == false ]]; then
        print_error "No package manager detected. Please install either Homebrew or MacPorts:"
        echo
        echo "Homebrew (recommended):"
        echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        echo
        echo "MacPorts:"
        echo "  Download from: https://www.macports.org/install.php"
        echo
        exit 1
    fi
}

# Function to select package manager
select_package_manager() {
    if [[ "$HAS_HOMEBREW" == true && "$HAS_MACPORTS" == true ]]; then
        echo
        echo "Both Homebrew and MacPorts are available. Please choose one:"
        echo "1) Homebrew (recommended - faster, more packages)"
        echo "2) MacPorts (more Unix-like, system integration)"
        echo
        read -p "Enter your choice (1 or 2): " choice
        
        case $choice in
            1)
                PACKAGE_MANAGER="brew"
                PACKAGE_MANAGER_NAME="Homebrew"
                print_status "Selected Homebrew as package manager"
                ;;
            2)
                PACKAGE_MANAGER="port"
                PACKAGE_MANAGER_NAME="MacPorts"
                print_status "Selected MacPorts as package manager"
                ;;
            *)
                print_error "Invalid choice. Defaulting to Homebrew."
                PACKAGE_MANAGER="brew"
                PACKAGE_MANAGER_NAME="Homebrew"
                ;;
        esac
    elif [[ "$HAS_HOMEBREW" == true ]]; then
        PACKAGE_MANAGER="brew"
        PACKAGE_MANAGER_NAME="Homebrew"
        print_status "Using Homebrew (only option available)"
    elif [[ "$HAS_MACPORTS" == true ]]; then
        PACKAGE_MANAGER="port"
        PACKAGE_MANAGER_NAME="MacPorts"
        print_status "Using MacPorts (only option available)"
    fi
}

# Function to update package manager
update_package_manager() {
    print_status "Updating $PACKAGE_MANAGER_NAME packages..."
    
    if [[ "$PACKAGE_MANAGER" == "brew" ]]; then
        # Use bash -c to ensure proper environment
        sudo -u $REAL_USER bash -c 'brew update'
        sudo -u $REAL_USER bash -c 'brew upgrade'
    elif [[ "$PACKAGE_MANAGER" == "port" ]]; then
        # MacPorts selfupdate and upgrade can be run as regular user
        sudo -u $REAL_USER bash -c 'port selfupdate'
        sudo -u $REAL_USER bash -c 'port upgrade outdated'
    fi
}

# Function to install required packages
install_packages() {
    print_status "Installing required packages via $PACKAGE_MANAGER_NAME..."
    
    if [[ "$PACKAGE_MANAGER" == "brew" ]]; then
        # Core packages
        sudo -u $REAL_USER bash -c 'brew install python@3.11'
        
        # System packages
        sudo -u $REAL_USER bash -c 'brew install nginx'
        
        # Mail server packages
        sudo -u $REAL_USER bash -c 'brew install postfix'
        
        # LDAP packages
        sudo -u $REAL_USER bash -c 'brew install openldap'
        
        # Additional dependencies
        sudo -u $REAL_USER bash -c 'brew install openssl readline sqlite3 xz zlib'
        
    elif [[ "$PACKAGE_MANAGER" == "port" ]]; then
        # Core packages - MacPorts install requires sudo but should be run as user
        sudo -u $REAL_USER bash -c 'sudo port install python311'
        
        # System packages
        sudo -u $REAL_USER bash -c 'sudo port install nginx'
        
        # Mail server packages
        sudo -u $REAL_USER bash -c 'sudo port install postfix'
        
        # LDAP packages
        sudo -u $REAL_USER bash -c 'sudo port install openldap2'
        
        # Additional dependencies
        sudo -u $REAL_USER bash -c 'sudo port install openssl3 readline sqlite3 xz zlib'
        
        # Create symlinks for MacPorts Python
        sudo ln -sf /opt/local/bin/python3.11 /opt/local/bin/python3
        sudo ln -sf /opt/local/bin/pip3.11 /opt/local/bin/pip3
    fi
    
    print_success "Required packages installed successfully"
}

# Function to get package paths based on package manager
get_package_paths() {
    if [[ "$PACKAGE_MANAGER" == "brew" ]]; then
        PYTHON_PATH="/usr/local/bin/python3"
        NGINX_CONFIG_DIR="/usr/local/etc/nginx"
        NGINX_BIN="/usr/local/bin/nginx"
        LDAP_CONFIG_DIR="/usr/local/etc/openldap"
        LDAP_DATA_DIR="/usr/local/var/openldap-data"
        LDAP_RUN_DIR="/usr/local/var/run"
    elif [[ "$PACKAGE_MANAGER" == "port" ]]; then
        PYTHON_PATH="/opt/local/bin/python3"
        NGINX_CONFIG_DIR="/opt/local/etc/nginx"
        NGINX_BIN="/opt/local/bin/nginx"
        LDAP_CONFIG_DIR="/opt/local/etc/openldap"
        LDAP_DATA_DIR="/opt/local/var/openldap-data"
        LDAP_RUN_DIR="/opt/local/var/run"
    fi
}

# Function to create application user and group
create_app_user() {
    print_status "Creating application user and group..."
    
    # Create group if it doesn't exist
    if ! dscl . -read /Groups/$APP_GROUP &> /dev/null; then
        dscl . -create /Groups/$APP_GROUP
        dscl . -create /Groups/$APP_GROUP PrimaryGroupID 501
    fi
    
    # Create user if it doesn't exist
    if ! dscl . -read /Users/$APP_USER &> /dev/null; then
        dscl . -create /Users/$APP_USER
        dscl . -create /Users/$APP_USER UserShell /bin/bash
        dscl . -create /Users/$APP_USER RealName "Postfix Manager"
        dscl . -create /Users/$APP_USER UniqueID 501
        dscl . -create /Users/$APP_USER PrimaryGroupID 501
        dscl . -create /Users/$APP_USER NFSHomeDirectory $APP_HOME
        dscl . -passwd /Users/$APP_USER ""
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
    mkdir -p $APP_HOME/data/db
    
    # Set ownership
    chown -R $APP_USER:$APP_GROUP $APP_HOME
    chown -R $APP_USER:$APP_GROUP $APP_CONFIG
    chown -R $APP_USER:$APP_GROUP $APP_LOG
    
    # Set permissions
    chmod 755 $APP_HOME
    chmod 755 $APP_CONFIG
    chmod 755 $APP_LOG
    chmod 755 $APP_HOME/logs
    chmod 755 $APP_HOME/data/db
    
    print_success "Application directories created successfully"
}

# Function to install Python application
install_python_app() {
    print_status "Installing Python application..."
    
    # Copy application files
    cp -r app $APP_HOME/
    cp -r requirements.txt $APP_HOME/
    cp -r run.py $APP_HOME/
    cp -r scripts $APP_HOME/
    
    # Create virtual environment
    cd $APP_HOME
    $PYTHON_PATH -m venv venv
    
    # Activate virtual environment and install dependencies
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    deactivate
    
    # Set ownership
    chown -R $APP_USER:$APP_GROUP $APP_HOME
    
    print_success "Python application installed successfully"
}

# Function to configure Postfix
configure_postfix() {
    print_status "Configuring Postfix..."
    
    # Backup original configuration
    if [[ -f /etc/postfix/main.cf ]]; then
        cp /etc/postfix/main.cf /etc/postfix/main.cf.backup.$(date +%Y%m%d_%H%M%S)
    fi
    
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
virtual_uid_maps = static:501
virtual_gid_maps = static:501
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

# Function to configure OpenLDAP
configure_ldap() {
    print_status "Configuring OpenLDAP..."
    
    # Create LDAP configuration directory
    mkdir -p $LDAP_CONFIG_DIR/slapd.d
    
    # Create basic LDAP configuration
    cat > $LDAP_CONFIG_DIR/slapd.conf << EOF
include $LDAP_CONFIG_DIR/schema/core.schema
include $LDAP_CONFIG_DIR/schema/cosine.schema
include $LDAP_CONFIG_DIR/schema/inetorgperson.schema

pidfile $LDAP_RUN_DIR/slapd.pid
argsfile $LDAP_RUN_DIR/slapd.args

database config
rootdn "cn=admin,cn=config"
rootpw admin

database monitor
rootdn "cn=admin,cn=config"
rootpw admin

database bdb
suffix "dc=example,dc=com"
rootdn "cn=admin,dc=example,dc=com"
rootpw admin
directory $LDAP_DATA_DIR
index objectClass eq
EOF
    
    # Create LDAP data directory
    mkdir -p $LDAP_DATA_DIR
    
    # Set permissions
    chown -R _ldap:_ldap $LDAP_DATA_DIR
    chmod 700 $LDAP_DATA_DIR
    
    print_success "OpenLDAP configured successfully"
}

# Function to create launchd service
create_service() {
    print_status "Creating launchd service..."
    
    cat > /Library/LaunchDaemons/$APP_SERVICE.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$APP_SERVICE</string>
    <key>ProgramArguments</key>
    <array>
        <string>$APP_HOME/venv/bin/python</string>
        <string>$APP_HOME/run.py</string>
        <string>--web</string>
        <string>--port</string>
        <string>5000</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$APP_LOG/postfix-manager.log</string>
    <key>StandardErrorPath</key>
    <string>$APP_LOG/postfix-manager.error.log</string>
    <key>WorkingDirectory</key>
    <string>$APP_HOME</string>
    <key>UserName</key>
    <string>$APP_USER</string>
    <key>GroupName</key>
    <string>$APP_GROUP</string>
</dict>
</plist>
EOF
    
    # Set permissions
    chown root:wheel /Library/LaunchDaemons/$APP_SERVICE.plist
    chmod 644 /Library/LaunchDaemons/$APP_SERVICE.plist
    
    # Load the service
    launchctl load /Library/LaunchDaemons/$APP_SERVICE.plist
    
    print_success "Launchd service created and loaded successfully"
}

# Function to configure Nginx
configure_nginx() {
    print_status "Configuring Nginx..."
    
    # Create Nginx configuration
    cat > $NGINX_CONFIG_DIR/servers/postfix-manager.conf << EOF
server {
    listen 80;
    server_name localhost;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF
    
    # Test Nginx configuration
    $NGINX_BIN -t
    
    # Reload Nginx
    if [[ "$PACKAGE_MANAGER" == "brew" ]]; then
        sudo -u $REAL_USER bash -c 'brew services restart nginx'
    elif [[ "$PACKAGE_MANAGER" == "port" ]]; then
        sudo -u $REAL_USER bash -c 'sudo port load nginx'
    fi
    
    print_success "Nginx configured successfully"
}

# Function to initialize database
initialize_database() {
    print_status "Initializing database..."
    
    cd $APP_HOME
    
    # Activate virtual environment and run init script
    source venv/bin/activate
    python scripts/init_db.py
    deactivate
    
    print_success "Database initialized successfully"
}

# Function to create admin user
create_admin_user() {
    print_status "Creating admin user..."
    
    cd $APP_HOME
    
    # Activate virtual environment and create admin user
    source venv/bin/activate
    python scripts/create_admin.py --username admin --email admin@example.com --password admin123 --non-interactive
    deactivate
    
    print_success "Admin user created successfully"
}

# Function to set up firewall rules
setup_firewall() {
    print_status "Setting up firewall rules..."
    
    # Allow HTTP and HTTPS
    /usr/libexec/ApplicationFirewall/socketfilterfw --add $NGINX_BIN
    /usr/libexec/ApplicationFirewall/socketfilterfw --add $PYTHON_PATH
    
    print_success "Firewall rules configured successfully"
}

# Function to display installation summary
display_summary() {
    print_success "Installation completed successfully!"
    echo
    echo "Postfix Manager has been installed with the following details:"
    echo "  - Package Manager: $PACKAGE_MANAGER_NAME"
    echo "  - Application Home: $APP_HOME"
    echo "  - Configuration: $APP_CONFIG"
    echo "  - Logs: $APP_LOG"
    echo "  - Service: $APP_SERVICE"
    echo
    echo "Access the application at: http://localhost:5000"
    echo "Default admin credentials: admin@example.com / admin123"
    echo
    echo "Useful commands:"
    echo "  - Start service: sudo launchctl load /Library/LaunchDaemons/$APP_SERVICE.plist"
    echo "  - Stop service: sudo launchctl unload /Library/LaunchDaemons/$APP_SERVICE.plist"
    echo "  - View logs: tail -f $APP_LOG/postfix-manager.log"
    if [[ "$PACKAGE_MANAGER" == "brew" ]]; then
        echo "  - Restart Nginx: brew services restart nginx"
    elif [[ "$PACKAGE_MANAGER" == "port" ]]; then
        echo "  - Restart Nginx: port reload nginx"
    fi
    echo
    echo "Please change the default admin password after first login!"
}

# Main installation function
main() {
    echo "=========================================="
    echo "Postfix Manager - macOS Installer"
    echo "=========================================="
    echo
    
    check_root
    detect_os
    detect_package_managers
    select_package_manager
    get_package_paths
    update_package_manager
    install_packages
    create_app_user
    create_directories
    install_python_app
    configure_postfix
    configure_ldap
    create_service
    configure_nginx
    initialize_database
    create_admin_user
    setup_firewall
    display_summary
}

# Run main function
main "$@"
