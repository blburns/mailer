# Postfix Manager - macOS Installation Guide

This guide will help you install Postfix Manager on macOS systems using the provided installer script.

## Prerequisites

### System Requirements
- **macOS Version**: 10.15 (Catalina) or later
- **Architecture**: Intel (x86_64) or Apple Silicon (ARM64)
- **RAM**: Minimum 4GB, recommended 8GB+
- **Disk Space**: At least 2GB free space

### Required Software
- **Package Manager**: Either Homebrew OR MacPorts
- **Xcode Command Line Tools**: For compiling packages

## Pre-Installation Setup

### 1. Install Xcode Command Line Tools
```bash
xcode-select --install
```

### 2. Install a Package Manager

#### Option A: Homebrew (Recommended)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### Option B: MacPorts
Download and install from: https://www.macports.org/install.php

### 3. Verify Package Manager Installation
```bash
# For Homebrew
brew --version

# For MacPorts
port version
```

## Installation

### 1. Download the Installer
Make sure you have the `macos_install.sh` script in your current directory.

### 2. Run the Installer
```bash
sudo ./macos_install.sh
```

**Note**: The script must be run with `sudo` as it needs to:
- Create system users and groups
- Install packages system-wide
- Configure system services
- Set up firewall rules

### 3. Package Manager Selection
If both Homebrew and MacPorts are installed, the installer will prompt you to choose:
- **Homebrew**: Faster, more packages, better integration with macOS
- **MacPorts**: More Unix-like, better system integration

### 4. Installation Process
The installer will automatically:
- Detect your macOS version
- Detect available package managers
- Update package manager repositories
- Install required dependencies (Python, Postfix, OpenLDAP, Nginx)
- Create application user and directories
- Configure Postfix for virtual hosting
- Set up OpenLDAP directory service
- Create launchd service for automatic startup
- Configure Nginx as reverse proxy
- Initialize the database
- Create default admin user
- Configure firewall rules

## Post-Installation

### 1. Access the Application
Once installation is complete, you can access Postfix Manager at:
```
http://localhost:5000
```

### 2. Default Login Credentials
- **Username**: admin@example.com
- **Password**: admin123

**Important**: Change the default password immediately after first login!

### 3. Verify Services
Check if all services are running:
```bash
# Check Postfix Manager service
sudo launchctl list | grep postfix-manager

# Check Nginx
brew services list | grep nginx  # For Homebrew
sudo port installed | grep nginx # For MacPorts

# Check Postfix
sudo postfix status

# Check OpenLDAP
sudo launchctl list | grep slapd
```

## Service Management

### Start/Stop Postfix Manager
```bash
# Start service
sudo launchctl load /Library/LaunchDaemons/com.postfix-manager.service.plist

# Stop service
sudo launchctl unload /Library/LaunchDaemons/com.postfix-manager.service.plist

# Restart service
sudo launchctl unload /Library/LaunchDaemons/com.postfix-manager.service.plist
sudo launchctl load /Library/LaunchDaemons/com.postfix-manager.service.plist
```

### Start/Stop Nginx
```bash
# For Homebrew
brew services start nginx
brew services stop nginx
brew services restart nginx

# For MacPorts
sudo port load nginx
sudo port unload nginx
sudo port reload nginx
```

## Configuration Files

### Application Configuration
- **Application Home**: `/opt/postfix-manager`
- **Configuration**: `/etc/postfix-manager`
- **Logs**: `/var/log/postfix-manager`

### Postfix Configuration
- **Main Config**: `/etc/postfix/main.cf`
- **Virtual Domains**: `/etc/postfix/virtual_domains`
- **Virtual Mailbox Maps**: `/etc/postfix/virtual_mailbox_maps`

### OpenLDAP Configuration
- **Homebrew**: `/usr/local/etc/openldap/slapd.conf`
- **MacPorts**: `/opt/local/etc/openldap/slapd.conf`
- **Data Directory**: Varies by package manager

### Nginx Configuration
- **Homebrew**: `/usr/local/etc/nginx/nginx.conf`
- **MacPorts**: `/opt/local/etc/nginx/nginx.conf`
- **Site Config**: `servers/postfix-manager.conf`

## Package Manager Differences

### Homebrew
- **Installation Path**: `/usr/local/`
- **Python**: `python@3.11`
- **OpenLDAP**: `openldap`
- **Service Management**: `brew services`

### MacPorts
- **Installation Path**: `/opt/local/`
- **Python**: `python311`
- **OpenLDAP**: `openldap2`
- **Service Management**: `port load/unload`

## Logs and Troubleshooting

### View Application Logs
```bash
# Application logs
tail -f /var/log/postfix-manager/postfix-manager.log

# Error logs
tail -f /var/log/postfix-manager/postfix-manager.error.log
```

### View Service Logs
```bash
# System logs
sudo log show --predicate 'process == "postfix-manager"' --last 1h

# Launchd logs
sudo log show --predicate 'subsystem == "com.apple.launchd"' --last 1h
```

### Common Issues and Solutions

#### 1. Port Already in Use
If port 5000 is already in use:
```bash
# Find what's using the port
lsof -i :5000

# Kill the process or change the port in the service file
```

#### 2. Permission Issues
If you encounter permission issues:
```bash
# Fix ownership
sudo chown -R postfix-manager:postfix-manager /opt/postfix-manager
sudo chown -R postfix-manager:postfix-manager /etc/postfix-manager
sudo chown -R postfix-manager:postfix-manager /var/log/postfix-manager
```

#### 3. Package Manager Path Issues
If packages aren't found:

**Homebrew**:
```bash
# Add Homebrew to PATH
echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**MacPorts**:
```bash
# Add MacPorts to PATH
echo 'export PATH="/opt/local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

#### 4. Homebrew Root Access Error
If you see "Running Homebrew as root is extremely dangerous":
- The installer now handles this automatically by running Homebrew commands as the real user
- Make sure you're running the installer with `sudo` (not as root directly)

## Uninstallation

To completely remove Postfix Manager:

### 1. Stop Services
```bash
sudo launchctl unload /Library/LaunchDaemons/com.postfix-manager.service.plist

# For Homebrew
brew services stop nginx

# For MacPorts
sudo port unload nginx
```

### 2. Remove Files
```bash
sudo rm -rf /opt/postfix-manager
sudo rm -rf /etc/postfix-manager
sudo rm -rf /var/log/postfix-manager
sudo rm /Library/LaunchDaemons/com.postfix-manager.service.plist
```

### 3. Remove User and Group
```bash
sudo dscl . -delete /Users/postfix-manager
sudo dscl . -delete /Groups/postfix-manager
```

### 4. Remove Packages (Optional)
**Homebrew**:
```bash
brew uninstall postfix openldap nginx python@3.11
```

**MacPorts**:
```bash
sudo port uninstall postfix openldap2 nginx python311
```

## Support

If you encounter issues during installation:

1. Check the logs for error messages
2. Verify all prerequisites are met
3. Ensure you're running the script with `sudo`
4. Check that ports 80 and 5000 are available
5. Verify your package manager is working correctly

For additional support, please refer to the main project documentation or create an issue in the project repository.

## Security Notes

- The installer creates a system user with limited privileges
- Services run under dedicated user accounts
- Firewall rules are configured to allow only necessary traffic
- Default passwords should be changed immediately
- Consider enabling macOS firewall for additional security
- Homebrew commands are run as the real user (not root) for security
