# Directory Structure

## Project Root Structure

```shell
├── run.py                          # Entry point to run the Flask application
├── requirements.txt                # Python dependencies
├── pyproject.toml                 # Project configuration and metadata
├── setup.py                       # Package setup and distribution
├── Makefile                       # Build and deployment automation
├── .env                           # Environment variables (e.g., SECRET_KEY, DATABASE_URL)
├── .gitignore                     # Git ignore patterns
├── LICENSE                        # Apache 2.0 license file
├── CHANGELOG.md                   # Project changelog and version history
├── README.md                      # Project overview and quick start guide
├── app/                           # Main application package
├── docs/                          # Project documentation
├── installers/                    # Platform-specific installation scripts
├── deploy/                        # Deployment configuration files
├── scripts/                       # Utility and automation scripts
├── logs/                          # Application and system logs
├── instance/                      # Instance-specific configuration
└── venv/                          # Python virtual environment (development)
```

## Application Structure (`app/`)

```shell
app/
├── __init__.py                    # Initializes the Flask app, database, and registers blueprints
├── config/                        # Configuration settings for different environments
│   ├── __init__.py               # Configuration initialization
│   ├── development.py            # Development environment settings
│   ├── production.py             # Production environment settings
│   └── testing.py                # Testing environment settings
├── extensions/                    # Central place to initialize Flask extensions
│   ├── __init__.py               # Extensions initialization
│   ├── database.py               # Database connection and session management
│   ├── security.py               # Security extensions (bcrypt, limiter)
│   └── auth.py                   # Authentication extensions
├── models/                        # Database models and data structures
│   ├── __init__.py               # Models initialization
│   ├── user.py                   # User model and authentication
│   ├── domain.py                 # Mail domain model
│   ├── mailbox.py                # Mailbox and quota model
│   └── audit.py                  # Audit log model
├── modules/                       # Directory for all feature-specific modules (Blueprints)
│   ├── auth/                     # User authentication and session management
│   │   ├── __init__.py           # Blueprint definition for 'auth'
│   │   ├── models.py             # Authentication-specific models
│   │   ├── routes.py             # Login, logout, password management
│   │   └── forms.py              # Authentication forms
│   ├── dashboard/                # Main dashboard and system overview
│   │   ├── __init__.py           # Blueprint definition for 'dashboard'
│   │   ├── routes.py             # Dashboard routes and statistics
│   │   └── utils.py              # Dashboard utility functions
│   ├── mail/                     # Mail server management (Postfix, Dovecot)
│   │   ├── __init__.py           # Blueprint definition for 'mail'
│   │   ├── models.py             # Mail server configuration models
│   │   ├── routes.py             # Mail server management endpoints
│   │   ├── services.py           # Mail server interaction logic
│   │   └── forms.py              # Mail configuration forms
│   └── ldap/                     # LDAP directory management
│       ├── __init__.py           # Blueprint definition for 'ldap'
│       ├── models.py             # LDAP configuration models
│       ├── routes.py             # LDAP management endpoints
│       ├── services.py           # LDAP server interaction logic
│       └── forms.py              # LDAP configuration forms
├── templates/                     # HTML templates for rendered pages
│   ├── base.html                 # Base template with common layout
│   ├── macros/                   # Reusable Jinja2 macros
│   │   ├── page_heading.html     # Page heading macro with icons and buttons
│   │   ├── sidebar.html          # Sidebar navigation macro
│   │   ├── card.html             # Card component macro for forms and content
│   │   └── user_dropdown.html    # User dropdown menu macro
│   ├── layout/                   # Layout templates (headers, footers, sidebars)
│   │   ├── header.html           # Application header with navigation
│   │   ├── sidebar.html          # Main sidebar navigation
│   │   └── footer.html           # Application footer
│   ├── modules/                  # Module-specific templates
│   │   ├── auth/                 # Authentication interface templates
│   │   │   ├── login.html        # User login page
│   │   │   ├── profile.html      # User profile page
│   │   │   └── password.html     # Password change page
│   │   ├── dashboard/            # Dashboard interface templates
│   │   │   ├── index.html        # Main dashboard page
│   │   │   ├── system.html       # System status page
│   │   │   └── statistics.html   # Statistics and metrics page
│   │   ├── mail/                 # Mail management interface templates
│   │   │   ├── index.html        # Mail management overview
│   │   │   ├── postfix.html      # Postfix configuration page
│   │   │   ├── dovecot.html      # Dovecot configuration page
│   │   │   ├── domains.html      # Domain management page
│   │   │   ├── users.html        # User management page
│   │   │   └── queue.html        # Mail queue monitoring page
│   │   └── ldap/                 # LDAP management interface templates
│   │       ├── index.html        # LDAP management overview
│   │       ├── browse.html       # Directory browser page
│   │       ├── users.html        # LDAP user management page
│   │       └── groups.html       # LDAP group management page
│   └── errors/                   # Error page templates
│       ├── 404.html              # Page not found
│       ├── 500.html              # Internal server error
│       └── error.html            # Generic error page
├── static/                        # Static files (CSS, JavaScript, images)
│   ├── css/                      # Stylesheets
│   │   ├── tailwind.css          # TailwindCSS framework
│   │   ├── flowbite.css          # Flowbite component library
│   │   └── custom.css            # Custom application styles
│   ├── js/                       # JavaScript files
│   │   ├── sidebar.js            # Sidebar navigation functionality
│   │   ├── forms.js              # Form handling utilities
│   │   └── modules/              # Module-specific JavaScript
│   │       ├── auth/             # Authentication scripts
│   │       ├── dashboard/        # Dashboard scripts
│   │       ├── mail/             # Mail management scripts
│   │       └── ldap/             # LDAP management scripts
│   ├── fonts/                    # Font files (Material Icons, etc.)
│   └── img/                      # Image files and icons
├── utils/                         # Common utility functions
│   ├── __init__.py               # Utilities initialization
│   ├── security.py               # Security utilities (hashing, validation)
│   ├── mail.py                   # Mail server utilities
│   ├── ldap.py                   # LDAP utilities
│   └── helpers.py                # General helper functions
├── data/                          # Data storage and configuration
│   ├── config/                   # Application configuration files
│   ├── database/                  # Database files and migrations
│   └── logs/                     # Application log files
└── main/                          # Core application routes and functionality
    ├── __init__.py               # Main blueprint definition
    ├── routes.py                 # Core application routes
    └── utils.py                  # Main module utilities
```

## Documentation Structure (`docs/`)

```shell
docs/
├── Project_Overview.md            # Comprehensive project overview and concepts
├── directory_structure.md         # This file - project structure documentation
├── development_roadmap.md         # Development phases and milestones
├── development_roadmap_checklist.md # Detailed development task checklist
├── API_ENDPOINTS.md               # Complete API endpoint documentation
├── API_CHECKLIST.md               # API development and testing checklist
├── database.md                    # Database schema and models documentation
├── USER_ROLES_GROUPS_SYSTEM.md    # User management and permissions system
├── PRODUCTION_DEPLOYMENT.md       # Production deployment guide
├── TESTING_GUIDE.md               # Testing strategy and procedures
├── CHANGELOG.md                   # Detailed changelog with commit history
├── LICENSE                        # Apache 2.0 license file
├── installers/                    # Installation documentation
│   ├── README_debian.md          # Debian/Ubuntu installation guide
│   ├── README_redhat.md          # RedHat/CentOS installation guide
│   └── README_macos.md           # macOS installation guide
└── versioning/                    # Version management documentation
```

## Installation Scripts (`installers/`)

```shell
installers/
├── debian_install.sh              # Debian/Ubuntu automated installation script
├── redhat_install.sh              # RedHat/CentOS automated installation script
├── macos_install.sh               # macOS automated installation script
└── README_*.md                    # Platform-specific installation documentation
```

## Deployment Configuration (`deploy/`)

```shell
deploy/
├── apache/                        # Apache web server configuration
│   ├── dreamlikelabs.conf        # Apache mod_wsgi vhost configuration
│   └── dreamlikelabs-proxy.conf  # Apache reverse proxy configuration
├── nginx/                         # Nginx web server configuration
│   ├── nginx.conf                # Main nginx configuration
│   └── sites-available/          # Site-specific configurations
├── systemd/                       # Systemd service configuration
│   ├── postfix-manager.service   # Main application service
│   └── postfix-manager.socket    # Socket activation configuration
└── supervisor/                    # Supervisor process management
    └── postfix-manager.conf      # Supervisor configuration
```

## Utility Scripts (`scripts/`)

```shell
scripts/
├── push_all.sh                    # Multi-repo deployment script
├── create_admin.py                # Admin user creation script
├── backup.py                      # Database and configuration backup
├── restore.py                     # Database and configuration restore
└── maintenance.py                 # System maintenance utilities
```

## Key File Purposes

### Configuration Files
- **`pyproject.toml`**: Modern Python project configuration with dependencies and metadata
- **`setup.py`**: Package distribution and installation configuration
- **`.env`**: Environment-specific configuration variables
- **`Makefile`**: Build automation and common development tasks

### Application Files
- **`run.py`**: Application entry point with CLI and web server modes
- **`app/__init__.py`**: Flask application factory and initialization
- **`app/config/`**: Environment-specific configuration management
- **`app/extensions/`**: Flask extension initialization and configuration

### Module Organization
- **`app/modules/auth/`**: User authentication and session management
- **`app/modules/dashboard/`**: System overview and monitoring dashboard
- **`app/modules/mail/`**: Postfix and Dovecot server management
- **`app/modules/ldap/`**: OpenLDAP directory management

### Template System
- **`app/templates/base.html`**: Foundation template with common layout
- **`app/templates/macros/`**: Reusable UI components and macros
- **`app/templates/modules/`**: Module-specific page templates
- **`app/static/`**: CSS, JavaScript, and other static assets

This structure provides a clean separation of concerns, making the application easy to maintain, extend, and deploy across different environments.
