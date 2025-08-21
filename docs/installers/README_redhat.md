# Postfix Manager - RedHat/CentOS Installation Guide

This guide will help you install Postfix Manager on RedHat-based systems using the provided installer script.

## Prerequisites

### System Requirements
- **OS**: RedHat Enterprise Linux 7+, CentOS 7+, Rocky Linux 8+, AlmaLinux 8+, Fedora 30+
- **Architecture**: x86_64 or ARM64
- **RAM**: Minimum 2GB, recommended 4GB+
- **Disk Space**: At least 2GB free space
- **Package Manager**: DNF (RHEL 8+/CentOS 8+) or YUM (RHEL 7/CentOS 7)

### Required Software
- **Python**: 3.6+ (automatically installed)
- **System packages**: Will be installed automatically
- **SELinux**: Enabled by default (will be configured)

## Pre-Installation Setup

### 1. Update System
```bash
# For RHEL 8+/CentOS 8+ (DNF)
sudo dnf update -y

# For RHEL 7/CentOS 7 (YUM)
sudo yum update -y
```

### 2. Ensure root access
The installer requires root privileges to:
- Install system packages
- Create system users
- Configure system services
- Set up SELinux policies
- Configure firewall rules

### 3. Verify Package Manager
```bash
# Check if DNF is available (newer systems)
dnf --version

# Check if YUM is available (older systems)
yum --version
```

## Installation

### 1. Download the Installer
Make sure you have the `redhat_install.sh` script in your current directory.

### 2. Run the Installer
```bash
sudo ./redhat_install.sh
```

### 3. Installation Process
The installer will automatically:
- Detect your OS version and package manager
- Update system packages
- Install required dependencies (Python, Postfix, Dovecot, OpenLDAP, Nginx)
- Create application user and directories
- Configure Postfix for virtual hosting
- Set up Dovecot IMAP/POP3 server
- Configure OpenLDAP directory service
- Create systemd service for automatic startup
- Configure Nginx as reverse proxy
- Set up SELinux policies
- Configure firewall rules
- Initialize the database
- Create default admin user

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

# Check SELinux status
sudo sestatus
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

# Check service status
sudo systemctl status postfix-manager
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
- **Config Directory**: `/etc/openldap/slapd.d/`
- **Data Directory**: `/var/lib/ldap/`

### Nginx Configuration
- **Main Config**: `/etc/nginx/nginx.conf`
- **Site Config**: `/etc/nginx/conf.d/postfix-manager.conf`

### SELinux Configuration
- **Policies**: Custom SELinux policies for Postfix Manager
- **Contexts**: Proper file and port contexts

## Package Manager Differences

### DNF (RHEL 8+/CentOS 8+)
- **Update**: `dnf update -y`
- **Install**: `dnf install -y package_name`
- **Search**: `dnf search package_name`
- **Info**: `dnf info package_name`

### YUM (RHEL 7/CentOS 7)
- **Update**: `yum update -y`
- **Install**: `yum install -y package_name`
- **Search**: `yum search package_name`
- **Info**: `yum info package_name`

## SELinux Management

### Check SELinux Status
```bash
# Check overall status
sudo sestatus

# Check specific contexts
ls -Z /opt/postfix-manager
ls -Z /etc/postfix-manager
```

### SELinux Troubleshooting
```bash
# Check SELinux denials
sudo ausearch -m AVC -ts recent

# Check SELinux logs
sudo tail -f /var/log/audit/audit.log | grep AVC

# Temporarily disable SELinux (for testing only)
sudo setenforce 0

# Re-enable SELinux
sudo setenforce 1
```

### SELinux Port Contexts
```bash
# Check port contexts
sudo semanage port -l | grep -E "(5000|80|25|110|143|993|995)"

# Add custom port context if needed
sudo semanage port -a -t http_port_t -p tcp 5000
```

## Firewall Configuration

### Check Firewall Status
```bash
# For firewalld (RHEL 7+/CentOS 7+)
sudo firewall-cmd --state
sudo firewall-cmd --list-all

# For iptables (older systems)
sudo iptables -L -n
```

### Firewall Rules
The installer automatically configures:
- **HTTP (80)**: For Nginx web server
- **HTTPS (443)**: For secure web access
- **SMTP (25)**: For Postfix mail server
- **IMAP (143)**: For Dovecot IMAP
- **POP3 (110)**: For Dovecot POP3
- **IMAPS (993)**: For secure IMAP
- **POP3S (995)**: For secure POP3

### Add Custom Firewall Rules
```bash
# Add custom port
sudo firewall-cmd --permanent --add-port=8080/tcp

# Add custom service
sudo firewall-cmd --permanent --add-service=custom-service

# Reload firewall
sudo firewall-cmd --reload
```

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

# SELinux logs
sudo tail -f /var/log/audit/audit.log
```

### Common Issues and Solutions

#### 1. Port Already in Use
If port 5000 is already in use:
```bash
# Find what's using the port
sudo netstat -tlnp | grep :5000
sudo ss -tlnp | grep :5000

# Kill the process or change the port in the service file
```

#### 2. Permission Issues
If you encounter permission issues:
```bash
# Fix ownership
sudo chown -R postfix-manager:postfix-manager /opt/postfix-manager
sudo chown -R postfix-manager:postfix-manager /etc/postfix-manager
sudo chown -R postfix-manager:postfix-manager /var/log/postfix-manager

# Fix SELinux contexts
sudo restorecon -Rv /opt/postfix-manager
sudo restorecon -Rv /etc/postfix-manager
```

#### 3. SELinux Denials
If SELinux is blocking operations:
```bash
# Check denials
sudo ausearch -m AVC -ts recent

# Generate SELinux policy
sudo audit2allow -a -M postfix_manager_policy
sudo semodule -i postfix_manager_policy.pp
```

#### 4. Service Start Failures
Check service status and logs:
```bash
sudo systemctl status postfix-manager
sudo journalctl -u postfix-manager --no-pager -l
```

#### 5. Package Installation Issues
If packages fail to install:
```bash
# Update package cache
sudo dnf clean all && sudo dnf makecache
# or
sudo yum clean all && sudo yum makecache

# Check available packages
sudo dnf search package_name
# or
sudo yum search package_name
```

## Uninstallation

To completely remove Postfix Manager:

### 1. Stop Services
```bash
sudo systemctl stop postfix-manager
sudo systemctl disable postfix-manager
sudo systemctl stop nginx
sudo systemctl disable nginx
sudo systemctl stop postfix
sudo systemctl disable postfix
sudo systemctl stop dovecot
sudo systemctl disable dovecot
sudo systemctl stop slapd
sudo systemctl disable slapd
```

### 2. Remove Files
```bash
sudo rm -rf /opt/postfix-manager
sudo rm -rf /etc/postfix-manager
sudo rm -rf /var/log/postfix-manager
sudo rm /etc/systemd/system/postfix-manager.service
sudo rm /etc/nginx/conf.d/postfix-manager.conf
```

### 3. Remove User and Group
```bash
sudo userdel -r postfix-manager
sudo groupdel postfix-manager
```

### 4. Remove Packages (Optional)
```bash
# For DNF systems
sudo dnf remove postfix dovecot openldap-servers openldap-clients nginx python3-pip

# For YUM systems
sudo yum remove postfix dovecot openldap-servers openldap-clients nginx python3-pip

# Clean up
sudo dnf autoremove  # or sudo yum autoremove
```

### 5. Remove SELinux Policies
```bash
# Remove custom policies
sudo semodule -r postfix_manager_policy

# Reset contexts
sudo restorecon -Rv /
```

## Support

If you encounter issues during installation:

1. Check the logs for error messages
2. Verify all prerequisites are met
3. Ensure you're running the script with `sudo`
4. Check that required ports are available
5. Verify SELinux status and policies
6. Check firewall configuration
7. Ensure all services are running correctly

### Useful Commands for Troubleshooting
```bash
# Check system resources
free -h
df -h
top

# Check network connectivity
ping localhost
netstat -tlnp

# Check service dependencies
systemctl list-dependencies postfix-manager

# Check configuration syntax
nginx -t
postfix check
```

For additional support, please refer to the main project documentation or create an issue in the project repository.

## Security Notes

- The installer creates a system user with limited privileges
- Services run under dedicated user accounts
- SELinux policies are configured for security
- Firewall rules allow only necessary traffic
- Default passwords should be changed immediately
- All services are configured with secure defaults
- Regular security updates are recommended
- Consider enabling additional security modules (AppArmor, etc.)

## Performance Tuning

### System Optimization
```bash
# Increase file descriptor limits
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf

# Optimize kernel parameters
echo "net.core.somaxconn = 65536" >> /etc/sysctl.conf
echo "net.ipv4.tcp_max_syn_backlog = 65536" >> /etc/sysctl.conf
sysctl -p
```

### Service Optimization
```bash
# Optimize Nginx worker processes
# Edit /etc/nginx/nginx.conf and adjust worker_processes

# Optimize Postfix processes
# Edit /etc/postfix/main.cf and adjust process limits

# Optimize Dovecot processes
# Edit /etc/dovecot/dovecot.conf and adjust process limits
```
