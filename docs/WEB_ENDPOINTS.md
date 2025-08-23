# Web Endpoints Overview

This document provides a comprehensive overview of all web pages, routes, and endpoints in the Postfix Manager application. It serves as a quick reference for developers and administrators to understand the application's structure and functionality.

## Table of Contents

- [Main Application Routes](#main-application-routes)
- [Authentication Routes](#authentication-routes)
- [Dashboard Routes](#dashboard-routes)
- [Mail Management Routes](#mail-management-routes)
- [LDAP Management Routes](#ldap-management-routes)
- [API Endpoints](#api-endpoints)
- [Static Assets](#static-assets)
- [Error Pages](#error-pages)
- [Route Status Legend](#route-status-legend)

---

## Main Application Routes

| Endpoint | Status | Module | Description | Authentication | Template |
|-----------|--------|--------|-------------|----------------|----------|
| `/` | ✅ Active | Main | Homepage - Main application entry point | Required | `modules/main/index.html` |
| `/about` | ✅ Active | Main | About page with project information | Required | `modules/main/about.html` |
| `/status` | ✅ Active | Main | System status overview page | Required | `modules/main/status.html` |

**Module**: `app.modules.main`
**Purpose**: Core application routes providing basic navigation and information pages.

---

## Authentication Routes

| Endpoint | Status | Module | Description | Authentication | Template |
|-----------|--------|--------|-------------|----------------|----------|
| `/auth/login` | ✅ Active | Auth | User login form and authentication | Not Required | `modules/auth/login.html` |
| `/auth/logout` | ✅ Active | Auth | User logout and session cleanup | Required | Redirect |
| `/auth/change-password` | ✅ Active | Auth | Password change form for authenticated users | Required | `modules/auth/change_password.html` |

**Module**: `app.modules.auth`
**Purpose**: User authentication, session management, and security-related functionality.

**Features**:
- CSRF protection on all forms
- Audit logging for login/logout events
- Remember me functionality
- Secure password change process

---

## Dashboard Routes

| Endpoint | Status | Module | Description | Authentication | Template |
|-----------|--------|--------|-------------|----------------|----------|
| `/dashboard/` | ✅ Active | Dashboard | Main dashboard with system overview | Required | `modules/dashboard/index.html` |
| `/dashboard/domains` | ✅ Active | Dashboard | Mail domains management interface | Required | `modules/dashboard/domains.html` |
| `/dashboard/domains/new` | ✅ Active | Dashboard | Create new mail domain form | Required | `modules/dashboard/domains.html` |
| `/dashboard/users` | ✅ Active | Dashboard | Mail users management interface | Required | `modules/dashboard/users.html` |
| `/dashboard/users/new` | ✅ Active | Dashboard | Create new mail user form | Required | `modules/dashboard/users.html` |
| `/dashboard/system` | ✅ Active | Dashboard | System configuration management | Required | `modules/dashboard/system.html` |
| `/dashboard/audit` | ✅ Active | Dashboard | Audit log viewing and management | Required | `modules/dashboard/audit.html` |

**Module**: `app.modules.dashboard`
**Purpose**: Centralized system management interface providing overview and control of all system components.

**Features**:
- Real-time system statistics
- Domain and user management
- System configuration interface
- Comprehensive audit logging
- Service status monitoring

---

## Mail Management Routes

### Postfix Management

| Endpoint | Status | Module | Description | Authentication | Type |
|-----------|--------|--------|-------------|----------------|------|
| `/mail/` | ✅ Active | Mail | Mail management dashboard | Required | Page |
| `/mail/postfix` | ✅ Active | Mail | Postfix service management page | Required | Page |
| `/mail/postfix/management` | ✅ Active | Mail | Postfix management interface | Required | Page |
| `/mail/postfix/status` | ✅ Active | Mail | Get Postfix service status | Required | API |
| `/mail/postfix/restart` | ✅ Active | Mail | Restart Postfix service | Required | API |
| `/mail/postfix/reload` | ✅ Active | Mail | Reload Postfix configuration | Required | API |
| `/mail/postfix/check-config` | ✅ Active | Mail | Validate Postfix configuration | Required | API |
| `/mail/postfix/logs` | ✅ Active | Mail | View recent Postfix logs | Required | API |
| `/mail/postfix/config/backup` | ✅ Active | Mail | Create configuration backup | Required | API |

### Dovecot Management

| Endpoint | Status | Module | Description | Authentication | Type |
|-----------|--------|--------|-------------|----------------|------|
| `/mail/dovecot` | ✅ Active | Mail | Dovecot service management page | Required | Page |
| `/mail/dovecot/management` | ✅ Active | Mail | Dovecot management interface | Required | Page |
| `/mail/dovecot/status` | ✅ Active | Mail | Get Dovecot service status | Required | API |
| `/mail/dovecot/restart` | ✅ Active | Mail | Restart Dovecot service | Required | API |
| `/mail/dovecot/reload` | ✅ Active | Mail | Reload Dovecot configuration | Required | API |
| `/mail/dovecot/check-config` | ✅ Active | Mail | Validate Dovecot configuration | Required | API |
| `/mail/dovecot/logs` | ✅ Active | Mail | View recent Dovecot logs | Required | API |

### Mail Queue Management

| Endpoint | Status | Module | Description | Authentication | Type |
|-----------|--------|--------|-------------|----------------|------|
| `/mail/queue` | ✅ Active | Mail | Mail queue management page | Required | Page |
| `/mail/queue/status` | ✅ Active | Mail | Get queue status and statistics | Required | API |
| `/mail/queue/flush` | ✅ Active | Mail | Flush all queued messages | Required | API |
| `/mail/queue/details` | ✅ Active | Mail | Get detailed queue information | Required | API |

### Mail Statistics & Monitoring

| Endpoint | Status | Module | Description | Authentication | Type |
|-----------|--------|--------|-------------|----------------|------|
| `/mail/statistics` | ✅ Active | Mail | Comprehensive mail statistics | Required | API |
| `/mail/system/monitoring` | ✅ Active | Mail | Real-time system monitoring | Required | API |
| `/mail/system/uptime` | ✅ Active | Mail | System uptime information | Required | API |

**Module**: `app.modules.mail`
**Purpose**: Complete management of Postfix and Dovecot mail services, including configuration, monitoring, and control.

**Features**:
- Service status monitoring
- Configuration management
- Log viewing and analysis
- Queue management
- Performance metrics
- System monitoring
- Configuration backup/restore

---

## LDAP Management Routes

### Directory Management

| Endpoint | Status | Module | Description | Authentication | Type |
|-----------|--------|--------|-------------|----------------|------|
| `/ldap/` | ✅ Active | LDAP | LDAP management dashboard | Required | Page |
| `/ldap/browser` | ✅ Active | LDAP | LDAP directory browser interface | Required | Page |
| `/ldap/search` | ✅ Active | LDAP | Search LDAP directory | Required | API |
| `/ldap/tree` | ✅ Active | LDAP | Get directory tree structure | Required | API |
| `/ldap/entry/<dn>` | ✅ Active | LDAP | Get specific LDAP entry details | Required | API |

### User Management

| Endpoint | Status | Module | Description | Authentication | Type |
|-----------|--------|--------|-------------|----------------|------|
| `/ldap/users` | ✅ Active | LDAP | LDAP user management interface | Required | Page |
| `/ldap/users/new` | ✅ Active | LDAP | Create new LDAP user | Required | API |
| `/ldap/users/<user_id>` | ✅ Active | LDAP | View/edit specific user | Required | API |
| `/ldap/users/<user_id>/delete` | ✅ Active | LDAP | Delete LDAP user | Required | API |

### Schema Management

| Endpoint | Status | Module | Description | Authentication | Type |
|-----------|--------|--------|-------------|----------------|------|
| `/ldap/schema` | ✅ Active | LDAP | LDAP schema editor interface | Required | Page |
| `/ldap/schema/attributes` | ✅ Active | LDAP | View/edit LDAP attributes | Required | API |
| `/ldap/schema/objectclasses` | ✅ Active | LDAP | View/edit LDAP object classes | Required | API |

**Module**: `app.modules.ldap`
**Purpose**: Complete LDAP directory management including browsing, searching, and schema management.

**Features**:
- Directory browser with tree view
- Advanced search functionality
- User and group management
- Schema editing capabilities
- LDAP connection management
- Directory structure visualization

---

## API Endpoints

### Authentication API

| Endpoint | Status | Module | Description | Authentication | Method |
|-----------|--------|--------|-------------|----------------|--------|
| `/api/auth/csrf-token` | ✅ Active | Auth | Get CSRF token for forms | Not Required | GET |
| `/api/auth/login` | ✅ Active | Auth | Authenticate user | Not Required | POST |
| `/api/auth/logout` | ✅ Active | Auth | Logout user | Required | POST |
| `/api/auth/change-password` | ✅ Active | Auth | Change user password | Required | POST |

### Dashboard API

| Endpoint | Status | Module | Description | Authentication | Method |
|-----------|--------|--------|-------------|----------------|--------|
| `/api/dashboard/stats` | ✅ Active | Dashboard | Get system statistics | Required | GET |
| `/api/dashboard/status` | ✅ Active | Dashboard | Get system status | Required | GET |
| `/api/dashboard/audit-logs` | ✅ Active | Dashboard | Get audit logs | Required | GET |

### Mail Management API

| Endpoint | Status | Module | Description | Authentication | Method |
|-----------|--------|--------|-------------|----------------|--------|
| `/api/mail/domains` | ✅ Active | Mail | Manage mail domains | Required | GET/POST/PUT/DELETE |
| `/api/mail/users` | ✅ Active | Mail | Manage mail users | Required | GET/POST/PUT/DELETE |
| `/api/mail/services/status` | ✅ Active | Mail | Get all service statuses | Required | GET |
| `/api/mail/queue/operations` | ✅ Active | Mail | Queue management operations | Required | POST |

### LDAP Management API

| Endpoint | Status | Module | Description | Authentication | Method |
|-----------|--------|--------|-------------|----------------|--------|
| `/api/ldap/connections` | ✅ Active | LDAP | Manage LDAP connections | Required | GET/POST/PUT/DELETE |
| `/api/ldap/entries` | ✅ Active | LDAP | CRUD operations on LDAP entries | Required | GET/POST/PUT/DELETE |
| `/api/ldap/schema` | ✅ Active | LDAP | Schema management operations | Required | GET/POST/PUT/DELETE |

---

## Static Assets

| Endpoint | Status | Module | Description | Authentication | Type |
|-----------|--------|--------|-------------|----------------|------|
| `/static/css/` | ✅ Active | Flask | CSS stylesheets and frameworks | Not Required | Static |
| `/static/js/` | ✅ Active | Flask | JavaScript files and libraries | Not Required | Static |
| `/static/images/` | ✅ Active | Flask | Application images and icons | Not Required | Static |
| `/static/fonts/` | ✅ Active | Flask | Custom fonts and typography | Not Required | Static |
| `/favicon.ico` | ✅ Active | Flask | Application favicon | Not Required | Static |

**Purpose**: Serve static assets including CSS, JavaScript, images, and other resources.

---

## Error Pages

| Endpoint | Status | Module | Description | Authentication | Template |
|-----------|--------|--------|-------------|----------------|----------|
| `/404` | ✅ Active | Flask | Page not found error | Not Required | `errors/404.html` |
| `/500` | ✅ Active | Flask | Internal server error | Not Required | `errors/500.html` |
| `/403` | ✅ Active | Flask | Forbidden access error | Not Required | `errors/403.html` |
| `/401` | ✅ Active | Flask | Unauthorized access error | Not Required | `errors/401.html` |

**Purpose**: Handle various HTTP error conditions with user-friendly error pages.

---

## Route Status Legend

| Status | Meaning | Description |
|--------|---------|-------------|
| ✅ Active | Fully Implemented | Route is implemented, tested, and ready for production use |
| 🚧 In Progress | Partially Implemented | Route is implemented but may need testing or refinement |
| 📋 Planned | Planned Feature | Route is planned but not yet implemented |
| ❌ Deprecated | No Longer Supported | Route exists but is deprecated and will be removed |
| 🔒 Restricted | Access Restricted | Route has special access restrictions or requirements |

---

## Module Organization

### Blueprint Structure

The application is organized into logical modules using Flask blueprints:

```python
# Main application routes
app.register_blueprint(main_bp)

# Authentication routes
app.register_blueprint(auth_bp, url_prefix='/auth')

# Mail management routes
app.register_blueprint(mail_bp, url_prefix='/mail')

# LDAP management routes
app.register_blueprint(ldap_bp, url_prefix='/ldap')

# Dashboard routes
app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
```

### URL Prefixes

- **Main Routes**: `/` (no prefix)
- **Authentication**: `/auth/*`
- **Mail Management**: `/mail/*`
- **LDAP Management**: `/ldap/*`
- **Dashboard**: `/dashboard/*`
- **API Endpoints**: `/api/*`

---

## Security Features

### Authentication Requirements

- **Public Routes**: Only basic information pages (login, about)
- **Protected Routes**: All management and administrative functions
- **Admin Routes**: Special administrative functions (marked in descriptions)

### Security Measures

- **CSRF Protection**: All forms and state-changing operations
- **Session Management**: Secure session handling with Flask-Login
- **Rate Limiting**: API endpoint protection against abuse
- **Audit Logging**: Comprehensive logging of all administrative actions
- **Input Validation**: Server-side validation of all user inputs

---

## Development Notes

### Adding New Routes

When adding new routes to the application:

1. **Choose the appropriate module** based on functionality
2. **Follow the established naming conventions**
3. **Add proper authentication decorators**
4. **Include comprehensive error handling**
5. **Add audit logging for administrative actions**
6. **Update this documentation**

### Route Naming Conventions

- **Page Routes**: Use descriptive names (e.g., `/domains`, `/users`)
- **API Routes**: Use RESTful conventions (e.g., `/api/domains`, `/api/users`)
- **Action Routes**: Use verb-based names (e.g., `/restart`, `/reload`)

### Template Organization

Templates are organized by module:
- `modules/main/` - Main application templates
- `modules/auth/` - Authentication templates
- `modules/dashboard/` - Dashboard templates
- `modules/mail/` - Mail management templates
- `modules/ldap/` - LDAP management templates

---

## Monitoring and Health

### Health Check Endpoints

| Endpoint | Purpose | Response |
|----------|---------|----------|
| `/health` | Basic health check | Application status |
| `/health/detailed` | Detailed health information | System metrics and status |
| `/metrics` | System metrics | Performance and resource usage |

### Status Monitoring

All major system components provide status endpoints:
- **Postfix**: `/mail/postfix/status`
- **Dovecot**: `/mail/dovecot/status`
- **LDAP**: `/ldap/status`
- **Database**: Built into dashboard routes

---

This document serves as a comprehensive reference for all web endpoints in the Postfix Manager application. For detailed API documentation, see [API_ENDPOINTS.md](API_ENDPOINTS.md).
