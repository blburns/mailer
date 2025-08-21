# Postfix Manager

A comprehensive web interface for managing Postfix, Dovecot, and OpenLDAP mail servers. This application provides an intuitive web-based management interface for system administrators to manage virtual mail hosting with LDAP backend.

## Features

- **Web-based Management Interface**: Modern, responsive web interface built with Flask and TailwindCSS
- **Postfix Management**: Configure and manage Postfix mail server settings
- **Dovecot Management**: Manage IMAP/POP3 server configuration
- **LDAP Directory Management**: Browse and manage LDAP directory structure
- **Virtual Mail Hosting**: Support for multiple domains and users
- **User Management**: Create and manage mail users with quotas
- **Audit Logging**: Comprehensive logging of all system changes
- **Multi-platform Support**: Install on Debian/Ubuntu and RedHat/CentOS systems

## System Requirements

- **Python**: 3.8 - 3.12 (Python 3.13+ not supported)
- **Operating System**: 
  - Debian/Ubuntu 18.04+
  - RedHat/CentOS 7+
  - Rocky Linux 8+
  - AlmaLinux 8+
- **Memory**: Minimum 2GB RAM
- **Disk Space**: Minimum 10GB available space
- **Network**: Internet access for package installation

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/dreamlikelabs/postfix-manager.git
cd postfix-manager
```

### 2. Run the Application

```bash
# Development mode (default)
python run.py

# Production mode
python run.py --web --mode production

# Custom port
python run.py --web --port 8080

# CLI mode
python run.py --cli
```

### 3. Access the Web Interface

Open your browser and navigate to:
- **Development**: http://localhost:5000
- **Production**: http://your-server-ip

Default login credentials:
- **Username**: admin
- **Password**: admin123

**Important**: Change the default password immediately after first login!

## Installation

### Automated Installation (Recommended)

#### Debian/Ubuntu Systems

```bash
# Download and run the installation script
curl -O https://raw.githubusercontent.com/dreamlikelabs/postfix-manager/main/installers/debian_install.sh
chmod +x debian_install.sh
sudo ./debian_install.sh
```

#### RedHat/CentOS Systems

```bash
# Download and run the installation script
curl -O https://raw.githubusercontent.com/dreamlikelabs/postfix-manager/main/installers/redhat_install.sh
chmod +x redhat_install.sh
sudo ./redhat_install.sh
```

### Manual Installation

#### 1. Install System Dependencies

**Debian/Ubuntu:**
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv python3-dev \
    postfix postfix-ldap dovecot-core dovecot-imapd dovecot-pop3d dovecot-ldap \
    slapd ldap-utils nginx build-essential libldap2-dev libsasl2-dev libssl-dev
```

**RedHat/CentOS:**
```bash
sudo yum update -y
sudo yum install -y python3 python3-pip python3-devel \
    postfix postfix-ldap dovecot dovecot-ldap \
    openldap-servers openldap-clients nginx gcc gcc-c++ make \
    openldap-devel cyrus-sasl-devel openssl-devel
```

#### 2. Create Application User

```bash
sudo useradd -r -d /opt/postfix-manager -s /bin/bash postfix-manager
sudo mkdir -p /opt/postfix-manager
sudo chown postfix-manager:postfix-manager /opt/postfix-manager
```

#### 3. Install Python Application

```bash
cd /opt/postfix-manager
sudo -u postfix-manager python3 -m venv venv
sudo -u postfix-manager venv/bin/pip install -r /path/to/requirements.txt
```

#### 4. Configure Services

The installation scripts handle all service configuration automatically. For manual configuration, refer to the individual service documentation.

## Configuration

### Environment Variables

Create a `.env` file in the application root:

```bash
# Application Configuration
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///postfix_manager.db

# Service Directories
POSTFIX_CONFIG_DIR=/etc/postfix
DOVECOT_CONFIG_DIR=/etc/dovecot
LDAP_CONFIG_DIR=/etc/ldap
VMAIL_HOME=/home/vmail

# Database Configuration (Optional)
# DATABASE_URL=postgresql://user:pass@localhost/dbname
# DATABASE_URL=mysql://user:pass@localhost/dbname
```

### Database Configuration

The application supports multiple database backends:

- **SQLite** (default): `sqlite:///postfix_manager.db`
- **PostgreSQL**: `postgresql://user:pass@localhost/dbname`
- **MySQL/MariaDB**: `mysql://user:pass@localhost/dbname`

### LDAP Configuration

The application automatically configures OpenLDAP with the following structure:

```
dc=example,dc=tld
├── cn=admin,dc=example,dc=tld
├── o=hosting,dc=example,dc=tld
    ├── ou=MailServer,o=hosting,dc=example,dc=tld
        ├── ou=MailDomains,ou=MailServer,o=hosting,dc=example,dc=tld
            ├── vd=yourdomain.com,ou=MailDomains,ou=MailServer,o=hosting,dc=example,dc=tld
                ├── ou=Mailboxes,vd=yourdomain.com,ou=MailDomains,ou=MailServer,o=hosting,dc=example,dc=tld
                    ├── mail=user1,ou=Mailboxes,vd=yourdomain.com,ou=MailDomains,ou=MailServer,o=hosting,dc=example,dc=tld
                    └── mail=user2,ou=Mailboxes,vd=yourdomain.com,ou=MailDomains,ou=MailServer,o=hosting,dc=example,dc=tld
```

## Usage

### Web Interface

1. **Dashboard**: Overview of system status and statistics
2. **Domains**: Manage mail domains and virtual hosting
3. **Users**: Create and manage mail users
4. **Mail Management**: Configure Postfix and Dovecot services
5. **LDAP Browser**: Browse and manage LDAP directory structure
6. **System**: View system configuration and audit logs

### CLI Interface

```bash
# Show system status
python run.py --cli --status

# List mail domains
python run.py --cli --domains

# List mail users
python run.py --cli --users
```

### API Endpoints

The application provides RESTful API endpoints for integration:

- `GET /api/status` - System status
- `GET /api/domains` - List mail domains
- `POST /api/domains` - Create new domain
- `GET /api/users` - List mail users
- `POST /api/users` - Create new user

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/dreamlikelabs/postfix-manager.git
cd postfix-manager

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install -e .[dev]

# Run the application
python run.py --web --port 5000
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py
```

### Code Quality

```bash
# Format code with Black
black app/

# Lint with flake8
flake8 app/

# Type checking with mypy
mypy app/
```

## Deployment

### Production Deployment

1. **Use Production Mode**: `python run.py --web --mode production`
2. **Configure Reverse Proxy**: Use Nginx or Apache as reverse proxy
3. **SSL/TLS**: Configure SSL certificates for HTTPS
4. **Database**: Use PostgreSQL or MySQL for production
5. **Monitoring**: Set up monitoring and logging
6. **Backup**: Regular backups of database and configuration

### Docker Deployment

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "run.py", "--web", "--mode", "production", "--host", "0.0.0.0"]
```

### Systemd Service

The installation scripts create a systemd service automatically. Manual creation:

```ini
[Unit]
Description=Postfix Manager Web Application
After=network.target postfix.service dovecot.service slapd.service

[Service]
Type=simple
User=postfix-manager
Group=postfix-manager
WorkingDirectory=/opt/postfix-manager
Environment=PATH=/opt/postfix-manager/venv/bin
ExecStart=/opt/postfix-manager/venv/bin/python run.py --web --mode production
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Troubleshooting

### Common Issues

1. **Permission Denied**: Ensure proper file permissions and user ownership
2. **Service Not Starting**: Check systemd logs with `journalctl -u postfix-manager`
3. **LDAP Connection Failed**: Verify LDAP service is running and credentials are correct
4. **Database Errors**: Check database connection and migration status

### Logs

- **Application Logs**: `/var/log/postfix-manager/`
- **System Logs**: `journalctl -u postfix-manager`
- **Service Logs**: `/var/log/syslog` or `/var/log/messages`

### Getting Help

1. Check the [documentation](https://github.com/dreamlikelabs/postfix-manager/wiki)
2. Search [existing issues](https://github.com/dreamlikelabs/postfix-manager/issues)
3. Create a [new issue](https://github.com/dreamlikelabs/postfix-manager/issues/new)

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [Wiki](https://github.com/dreamlikelabs/postfix-manager/wiki)
- **Issues**: [GitHub Issues](https://github.com/dreamlikelabs/postfix-manager/issues)
- **Discussions**: [GitHub Discussions](https://github.com/dreamlikelabs/postfix-manager/discussions)
- **Email**: info@dreamlikelabs.com

## Acknowledgments

- [Postfix](http://www.postfix.org/) - Mail Transfer Agent
- [Dovecot](https://dovecot.org/) - IMAP/POP3 Server
- [OpenLDAP](https://www.openldap.org/) - LDAP Directory Server
- [Flask](https://flask.palletsprojects.com/) - Web Framework
- [TailwindCSS](https://tailwindcss.com/) - CSS Framework

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes.

---

**Note**: This application is designed for system administrators and requires root access for installation and configuration. Always test in a development environment before deploying to production.
