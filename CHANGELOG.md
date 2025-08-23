# Changelog

All notable changes to the Postfix Manager project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 2025-08-22

### Added
- **Mail Management Frontend**: Comprehensive mail management functionality with JSON parsing support
- **Enhanced UI Components**: Improved error badge styling for better readability
- **Navigation Improvements**: Sticky navbar with improved light mode styling
- **Icon Updates**: Updated Dashboard icon to more appropriate chart/dashboard icon
- **Navigation Reordering**: Reorganized navigation to user preference: Home | Dashboard (standalone) | Mail | LDAP | System
- **Functional Navigation**: Implemented functional grouping navigation (Option 1)
- **Authentication Enhancements**: Improved login form positioning and flash message display
- **Template Cleanup**: Cleaned up templates and enforced authentication

### Fixed
- **JSON Parsing**: Fixed JSON parsing errors in mail management frontend
- **Mail Management Routes**: Fixed mail management routes and added comprehensive functionality
- **UI Styling**: Fixed navbar button styling and appearance
- **Title Color**: Fixed Postfix Manager title color in light mode
- **Form Positioning**: Fixed login form positioning and flash message display

### Changed
- **Navigation Order**: Reordered navigation to user preference
- **UI Styling**: Updated error badge styling for better readability
- **Navbar Behavior**: Made navbar sticky with improved light mode styling

## [0.1.0] - 2025-08-21

### Added
- **Core Application Structure**: Complete Flask application foundation
- **Authentication System**: Flask-Login integration with user management
- **Database Models**: Comprehensive database models for Postfix Manager
- **Module Architecture**: Modular application structure with separate blueprints
- **Web Interface**: Modern, responsive web interface built with TailwindCSS/Flowbite
- **Dashboard Templates**: Comprehensive dashboard templates for domains, users, system config, and audit logs
- **Authentication Templates**: Login and password change forms
- **Base Templates**: Base template with TailwindCSS/Flowbite and main module templates
- **Mail Management Module**: Postfix and Dovecot management functionality
- **LDAP Management Module**: Directory operations and management
- **System Management**: Dashboard module for system management
- **Core Routes**: Main application module with core routes
- **Service Management**: Utility modules for service management
- **Installation Scripts**: Automated installation scripts for multiple platforms
- **Application Runner**: Main application runner with CLI and web modes
- **Deployment Configuration**: Comprehensive deployment configuration files
- **Data Directory Structure**: Deployment configuration and data directory structure
- **Database Initialization**: Database initialization and admin user creation scripts
- **Mail Server Templates**: Mail server and LDAP management templates

### Changed
- **Python Compatibility**: Updated Python version compatibility to 3.13
- **Application Structure**: Reorganized application structure with modules directory and separate main blueprint
- **Dependencies**: Added Flask-Login dependency and updated database models

### Platform Support
- **macOS**: Added macOS installer script and documentation
- **RedHat/CentOS**: Added comprehensive RedHat/CentOS installer documentation
- **Debian/Ubuntu**: Support for Debian/Ubuntu systems
- **Cross-Platform**: Multi-platform installation support

### Installation Improvements
- **macOS**: Fixed MacPorts privilege issues in macOS installer
- **Homebrew**: Fixed Homebrew root privilege issues and reorganized documentation
- **Automated Scripts**: Comprehensive installation automation for all supported platforms

## Project Information

### Development Status
- **Current Version**: 0.1.0 (Beta)
- **Python Support**: 3.8 - 3.12 (Python 3.13+ not supported)
- **License**: Apache 2.0
- **Maintainer**: DreamlikeLabs (info@dreamlikelabs.com)

### Supported Platforms
- Debian/Ubuntu 18.04+
- RedHat/CentOS 7+
- Rocky Linux 8+
- AlmaLinux 8+
- macOS (with Homebrew or MacPorts)

### Key Features
- Web-based management interface for Postfix, Dovecot, and OpenLDAP
- Virtual mail hosting with LDAP backend
- User and domain management
- Comprehensive audit logging
- Multi-platform installation support
- Modern responsive UI with TailwindCSS

---

## Version History

- **0.1.0** (2025-08-21): Initial beta release with core functionality
- **Unreleased**: Current development version with ongoing improvements

## Contributing

When contributing to this project, please ensure your commit messages follow the conventional commit format:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `style:` for formatting changes
- `refactor:` for code refactoring
- `test:` for adding tests
- `chore:` for maintenance tasks

## Notes

- This project was initiated on August 21, 2025
- Development is actively ongoing with regular commits
- The project follows modern Python development practices
- All changes are tracked in this changelog for transparency
