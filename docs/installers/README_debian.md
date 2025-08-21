# Postfix Manager - Debian/Ubuntu Installation Guide

This guide will help you install Postfix Manager on Debian-based systems using the provided installer script.

## Prerequisites

### System Requirements
- **OS**: Debian 10+ or Ubuntu 18.04+ (LTS recommended)
- **Architecture**: x86_64 or ARM64
- **RAM**: Minimum 2GB, recommended 4GB+
- **Disk Space**: At least 2GB free space

### Required Software
- **Python**: 3.8+ (automatically installed)
- **System packages**: Will be installed automatically

## Pre-Installation Setup

### 1. Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Ensure root access
The installer requires root privileges to:
- Install system packages
- Create system users
- Configure system services
- Set up firewall rules

## Installation

### 1. Download the Installer
Make sure you have the `debian_install.sh` script in your current directory.

### 2. Run the Installer
```bash
sudo ./debian_install.sh
```

### 3. Installation Process
The installer will automatically:
- Detect your OS version
- Update system packages
- Install required dependencies (Python, Postfix, Dovecot, OpenLDAP, Nginx)
- Create application user and directories
- Configure Postfix for virtual hosting
- Set up Dovecot IMAP/POP3 server
- Configure OpenLDAP directory service
- Create systemd service for automatic startup
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
sudo systemctl status postfix-manager

# Check Nginx
sudo systemctl status nginx

# Check Postfix
sudo systemctl status postfix

# Check Dovecot
sudo systemctl status dovecot

# Check OpenLDAP
sudo systemctl status slapd
```

## Service Management

### Start/Stop Postfix Manager
```bash
# Start service
sudo systemctl start postfix-manager

# Stop service
sudo systemctl stop postfix-manager

# Restart service
sudo systemctl restart postfix-manager

# Enable auto-start
sudo systemctl enable postfix-manager
```

### Start/Stop Other Services
```bash
# Nginx
sudo systemctl start/stop/restart nginx
sudo systemctl enable nginx

# Postfix
sudo systemctl start/stop/restart postfix
sudo systemctl enable postfix

# Dovecot
sudo systemctl start/stop/restart dovecot
sudo systemctl enable dovecot

# OpenLDAP
sudo systemctl start/stop/restart slapd
sudo systemctl enable slapd
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

### Dovecot Configuration
- **Main Config**: `/etc/dovecot/dovecot.conf`
- **LDAP Config**: `/etc/dovecot/conf.d/10-auth.conf`

### OpenLDAP Configuration
- **Config Directory**: `/etc/ldap/slapd.d/`
- **Data Directory**: `/var/lib/ldap/`

### Nginx Configuration
- **Main Config**: `/etc/nginx/nginx.conf`
- **Site Config**: `/etc/nginx/sites-available/postfix-manager`

## Logs and Troubleshooting

### View Application Logs
```bash
# Application logs
sudo tail -f /var/log/postfix-manager/postfix-manager.log

# Error logs
sudo tail -f /var/log/postfix-manager/postfix-manager.error.log
```

### View Service Logs
```bash
# System logs
sudo journalctl -u postfix-manager -f
sudo journalctl -u nginx -f
sudo journalctl -u postfix -f
sudo journalctl -u dovecot -f
sudo journalctl -u slapd -f
```

### Common Issues and Solutions

#### 1. Port Already in Use
If port 5000 is already in use:
```bash
# Find what's using the port
sudo netstat -tlnp | grep :5000

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

#### 3. Service Start Failures
Check service status and logs:
```bash
sudo systemctl status postfix-manager
sudo journalctl -u postfix-manager --no-pager -l
```

## Uninstallation

To completely remove Postfix Manager:

### 1. Stop Services
```bash
sudo systemctl stop postfix-manager
sudo systemctl disable postfix-manager
sudo systemctl stop nginx
sudo systemctl disable nginx
```

### 2. Remove Files
```bash
sudo rm -rf /opt/postfix-manager
sudo rm -rf /etc/postfix-manager
sudo rm -rf /var/log/postfix-manager
sudo rm /etc/systemd/system/postfix-manager.service
```

### 3. Remove User and Group
```bash
sudo userdel -r postfix-manager
sudo groupdel postfix-manager
```

### 4. Remove Packages (Optional)
```bash
sudo apt remove --purge postfix dovecot-core dovecot-imapd dovecot-pop3d dovecot-ldap slapd ldap-utils nginx
sudo apt autoremove
```

## Support

If you encounter issues during installation:

1. Check the logs for error messages
2. Verify all prerequisites are met
3. Ensure you're running the script with `sudo`
4. Check that ports 80 and 5000 are available
5. Verify all services are running correctly

For additional support, please refer to the main project documentation or create an issue in the project repository.

## Security Notes

- The installer creates a system user with limited privileges
- Services run under dedicated user accounts
- Firewall rules are configured to allow only necessary traffic
- Default passwords should be changed immediately
- Consider enabling UFW firewall for additional security
- All services are configured with secure defaults
