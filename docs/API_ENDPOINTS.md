# API Endpoints Documentation

## Overview

The Postfix Manager API follows a modular structure with dedicated blueprints for each major module. Each module has its own API namespace with proper URL prefixes and comprehensive security features.

## Security Features

### CSRF Protection
All authentication and modification endpoints are protected with CSRF tokens to prevent cross-site request forgery attacks.

**CSRF Token Endpoint**:
- `GET /api/auth/csrf-token` - Get CSRF token for frontend use

**CSRF Token Usage**:
- Include CSRF token in request headers: `X-CSRFToken: <token>`
- Or include in JSON payload: `{"csrf_token": "<token>", ...}`
- Or include in form data: `csrf_token=<token>`

**Configuration**:
- `CSRF_ENABLED` - Enable/disable CSRF protection (default: True)
- `CSRF_TIME_LIMIT` - Token expiration time in seconds (default: 3600)
- `CSRF_SSL_STRICT` - Require HTTPS for CSRF (default: False)

### Rate Limiting
All endpoints are protected with configurable rate limiting to prevent abuse and brute force attacks.

**Global Rate Limits**:
- `RATE_LIMIT_DEFAULT_DAY` - Requests per day (default: 200)
- `RATE_LIMIT_DEFAULT_HOUR` - Requests per hour (default: 50)
- `RATE_LIMIT_DEFAULT_MINUTE` - Requests per minute (default: 100)

**Authentication-Specific Limits**:
- `RATE_LIMIT_LOGIN_PER_MINUTE` - Login attempts per minute (default: 5)
- `RATE_LIMIT_REGISTER_PER_HOUR` - Registration attempts per hour (default: 3)
- `RATE_LIMIT_PASSWORD_RESET_PER_HOUR` - Password reset attempts per hour (default: 3)
- `RATE_LIMIT_LOGOUT_PER_MINUTE` - Logout attempts per minute (default: 10)

**Rate Limit Response**:
```json
{
  "status": "error",
  "message": "Too many requests. Please try again later.",
  "retry_after": 60
}
```

**Configuration**:
- `RATE_LIMIT_ENABLED` - Enable/disable rate limiting (default: True)
- `RATE_LIMIT_STORAGE` - Storage backend: "memory" or "redis" (default: memory)
- `RATE_LIMIT_REDIS_URL` - Redis URL for rate limiting storage (optional)

## API Structure

### Base URL
All API endpoints are prefixed with `/api/`

### Module Organization
- **Auth API**: `/api/auth/*` - Authentication and user management
- **Dashboard API**: `/api/dashboard/*` - System overview and statistics
- **Mail API**: `/api/mail/*` - Postfix and Dovecot management
- **LDAP API**: `/api/ldap/*` - LDAP directory management
- **Admin API**: `/api/admin/*` - Administrative functions
- **Main API**: `/` - Application main routes

## Authentication Endpoints

### GET /api/auth/csrf-token
**Description**: Get CSRF token for frontend use

**Response**:
```json
{
  "status": "success",
  "data": {
    "csrf_token": "csrf_token_string"
  }
}
```

**Security**: No authentication required, exempt from CSRF protection

### POST /api/auth/login
**Description**: Authenticate user and create session

**Security**: 
- **CSRF Protection**: Required
- **Rate Limiting**: 5 attempts per minute (configurable)

**Request Headers**:
```
X-CSRFToken: <csrf_token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "username": "string",
  "password": "string"
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Login successful",
  "data": {
    "user": {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "role": "admin"
    }
  }
}
```

### POST /api/auth/logout
**Description**: Logout user and destroy session

**Security**: 
- **Authentication**: Required
- **CSRF Protection**: Required
- **Rate Limiting**: 10 attempts per minute

**Request Headers**:
```
X-CSRFToken: <csrf_token>
Authorization: Bearer <session_token>
```

**Response**:
```json
{
  "status": "success",
  "message": "Logout successful"
}
```

### POST /api/auth/change-password
**Description**: Change user password

**Security**: 
- **Authentication**: Required
- **CSRF Protection**: Required
- **Rate Limiting**: 5 attempts per hour

**Request Body**:
```json
{
  "csrf_token": "string",
  "current_password": "string",
  "new_password": "string",
  "confirm_password": "string"
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Password changed successfully"
}
```

## Dashboard API Endpoints

### GET /api/dashboard/overview
**Description**: Get system overview and statistics

**Security**: Authentication required

**Response**:
```json
{
  "status": "success",
  "data": {
    "system": {
      "hostname": "mail.example.com",
      "uptime": "2 days, 3 hours",
      "load_average": [0.5, 0.3, 0.2],
      "memory_usage": 65.2,
      "disk_usage": 45.8
    },
    "mail_services": {
      "postfix": "running",
      "dovecot": "running",
      "openldap": "running"
    },
    "statistics": {
      "total_users": 150,
      "total_domains": 25,
      "messages_today": 1250,
      "queue_size": 5
    }
  }
}
```

### GET /api/dashboard/system-status
**Description**: Get detailed system status information

**Security**: Authentication required

**Response**:
```json
{
  "status": "success",
  "data": {
    "cpu": {
      "usage_percent": 12.5,
      "temperature": 45.2,
      "frequency": 2400
    },
    "memory": {
      "total": 8589934592,
      "available": 3006477107,
      "used": 5583457485,
      "cached": 1234567890
    },
    "disk": {
      "total": 107374182400,
      "used": 48318382080,
      "free": 59055800320
    },
    "network": {
      "interfaces": [
        {
          "name": "eth0",
          "bytes_sent": 1234567890,
          "bytes_recv": 9876543210,
          "packets_sent": 12345,
          "packets_recv": 67890
        }
      ]
    }
  }
}
```

## Mail Management API Endpoints

### GET /api/mail/overview
**Description**: Get mail server overview and status

**Security**: Authentication required

**Response**:
```json
{
  "status": "success",
  "data": {
    "postfix": {
      "status": "running",
      "version": "3.5.13",
      "config_file": "/etc/postfix/main.cf",
      "queue_directory": "/var/spool/postfix"
    },
    "dovecot": {
      "status": "running",
      "version": "2.3.16",
      "config_file": "/etc/dovecot/dovecot.conf",
      "processes": 8
    },
    "domains": {
      "total": 25,
      "active": 23,
      "suspended": 2
    },
    "users": {
      "total": 150,
      "active": 148,
      "suspended": 2
    }
  }
}
```

### GET /api/mail/postfix/config
**Description**: Get Postfix configuration

**Security**: Authentication required

**Response**:
```json
{
  "status": "success",
  "data": {
    "config_file": "/etc/postfix/main.cf",
    "last_modified": "2025-08-22T10:30:00Z",
    "settings": {
      "myhostname": "mail.example.com",
      "mydomain": "example.com",
      "myorigin": "$mydomain",
      "inet_interfaces": "all",
      "inet_protocols": "ipv4",
      "mydestination": "$myhostname, localhost.$mydomain, localhost, $mydomain"
    }
  }
}
```

### POST /api/mail/postfix/config
**Description**: Update Postfix configuration

**Security**: 
- **Authentication**: Required
- **CSRF Protection**: Required
- **Authorization**: Admin role required

**Request Body**:
```json
{
  "csrf_token": "string",
  "settings": {
    "myhostname": "mail.example.com",
    "mydomain": "example.com",
    "myorigin": "$mydomain"
  }
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Configuration updated successfully",
  "data": {
    "backup_file": "/etc/postfix/main.cf.backup.20250822",
    "restart_required": true
  }
}
```

### GET /api/mail/postfix/queue
**Description**: Get Postfix queue information

**Security**: Authentication required

**Query Parameters**:
- `queue` - Queue type: incoming, active, deferred, hold (default: all)
- `limit` - Maximum number of messages to return (default: 100)

**Response**:
```json
{
  "status": "success",
  "data": {
    "incoming": {
      "count": 5,
      "size": 1024000
    },
    "active": {
      "count": 12,
      "size": 2048000
    },
    "deferred": {
      "count": 3,
      "size": 512000
    },
    "hold": {
      "count": 0,
      "size": 0
    },
    "messages": [
      {
        "id": "ABC123DEF456",
        "size": 256000,
        "from": "sender@example.com",
        "to": "recipient@example.com",
        "arrival_time": "2025-08-22T10:30:00Z",
        "queue": "active"
      }
    ]
  }
}
```

### POST /api/mail/postfix/queue/flush
**Description**: Flush deferred queue

**Security**: 
- **Authentication**: Required
- **CSRF Protection**: Required
- **Authorization**: Admin role required

**Request Body**:
```json
{
  "csrf_token": "string",
  "queue": "deferred"
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Queue flushed successfully",
  "data": {
    "messages_processed": 15,
    "queue": "deferred"
  }
}
```

### GET /api/mail/dovecot/config
**Description**: Get Dovecot configuration

**Security**: Authentication required

**Response**:
```json
{
  "status": "success",
  "data": {
    "config_file": "/etc/dovecot/dovecot.conf",
    "last_modified": "2025-08-22T10:30:00Z",
    "settings": {
      "protocols": "imap pop3",
      "listen": "*, ::",
      "ssl": "required",
      "ssl_cert": "</etc/ssl/certs/dovecot.pem",
      "ssl_key": "</etc/ssl/private/dovecot.key"
    }
  }
}
```

### POST /api/mail/dovecot/config
**Description**: Update Dovecot configuration

**Security**: 
- **Authentication**: Required
- **CSRF Protection**: Required
- **Authorization**: Admin role required

**Request Body**:
```json
{
  "csrf_token": "string",
  "settings": {
    "protocols": "imap pop3",
    "ssl": "required"
  }
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Configuration updated successfully",
  "data": {
    "backup_file": "/etc/dovecot/dovecot.conf.backup.20250822",
    "restart_required": true
  }
}
```

## Domain Management API Endpoints

### GET /api/mail/domains
**Description**: Get list of mail domains

**Security**: Authentication required

**Query Parameters**:
- `status` - Filter by status: active, suspended, all (default: all)
- `page` - Page number for pagination (default: 1)
- `per_page` - Items per page (default: 20)

**Response**:
```json
{
  "status": "success",
  "data": {
    "domains": [
      {
        "id": 1,
        "name": "example.com",
        "status": "active",
        "created_at": "2025-08-21T10:00:00Z",
        "user_count": 25,
        "quota_used": 1073741824,
        "quota_limit": 10737418240
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 25,
      "pages": 2
    }
  }
}
```

### POST /api/mail/domains
**Description**: Create new mail domain

**Security**: 
- **Authentication**: Required
- **CSRF Protection**: Required
- **Authorization**: Admin role required

**Request Body**:
```json
{
  "csrf_token": "string",
  "name": "newdomain.com",
  "quota_limit": 10737418240,
  "description": "New domain for company expansion"
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Domain created successfully",
  "data": {
    "domain": {
      "id": 26,
      "name": "newdomain.com",
      "status": "active",
      "created_at": "2025-08-22T11:00:00Z",
      "quota_limit": 10737418240
    }
  }
}
```

### PUT /api/mail/domains/{domain_id}
**Description**: Update mail domain

**Security**: 
- **Authentication**: Required
- **CSRF Protection**: Required
- **Authorization**: Admin role required

**Request Body**:
```json
{
  "csrf_token": "string",
  "quota_limit": 21474836480,
  "description": "Updated domain description"
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Domain updated successfully",
  "data": {
    "domain": {
      "id": 26,
      "name": "newdomain.com",
      "quota_limit": 21474836480,
      "description": "Updated domain description"
    }
  }
}
```

### DELETE /api/mail/domains/{domain_id}
**Description**: Delete mail domain

**Security**: 
- **Authentication**: Required
- **CSRF Protection**: Required
- **Authorization**: Admin role required

**Request Body**:
```json
{
  "csrf_token": "string",
  "force": false
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Domain deleted successfully",
  "data": {
    "deleted_at": "2025-08-22T11:30:00Z"
  }
}
```

## User Management API Endpoints

### GET /api/mail/users
**Description**: Get list of mail users

**Security**: Authentication required

**Query Parameters**:
- `domain_id` - Filter by domain ID
- `status` - Filter by status: active, suspended, all (default: all)
- `page` - Page number for pagination (default: 1)
- `per_page` - Items per page (default: 20)

**Response**:
```json
{
  "status": "success",
  "data": {
    "users": [
      {
        "id": 1,
        "username": "user@example.com",
        "domain_id": 1,
        "domain_name": "example.com",
        "status": "active",
        "quota_used": 1073741824,
        "quota_limit": 1073741824,
        "created_at": "2025-08-21T10:00:00Z",
        "last_login": "2025-08-22T09:30:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 150,
      "pages": 8
    }
  }
}
```

### POST /api/mail/users
**Description**: Create new mail user

**Security**: 
- **Authentication**: Required
- **CSRF Protection**: Required
- **Authorization**: Admin role required

**Request Body**:
```json
{
  "csrf_token": "string",
  "username": "newuser@example.com",
  "password": "secure_password",
  "quota_limit": 1073741824,
  "domain_id": 1
}
```

**Response**:
```json
{
  "status": "success",
  "message": "User created successfully",
  "data": {
    "user": {
      "id": 151,
      "username": "newuser@example.com",
      "domain_id": 1,
      "status": "active",
      "quota_limit": 1073741824,
      "created_at": "2025-08-22T12:00:00Z"
    }
  }
}
```

### PUT /api/mail/users/{user_id}
**Description**: Update mail user

**Security**: 
- **Authentication**: Required
- **CSRF Protection**: Required
- **Authorization**: Admin role required

**Request Body**:
```json
{
  "csrf_token": "string",
  "quota_limit": 2147483648,
  "status": "active"
}
```

**Response**:
```json
{
  "status": "success",
  "message": "User updated successfully",
  "data": {
    "user": {
      "id": 151,
      "quota_limit": 2147483648,
      "status": "active"
    }
  }
}
```

### DELETE /api/mail/users/{user_id}
**Description**: Delete mail user

**Security**: 
- **Authentication**: Required
- **CSRF Protection**: Required
- **Authorization**: Admin role required

**Request Body**:
```json
{
  "csrf_token": "string",
  "force": false
}
```

**Response**:
```json
{
  "status": "success",
  "message": "User deleted successfully",
  "data": {
    "deleted_at": "2025-08-22T12:30:00Z"
  }
}
```

## LDAP Management API Endpoints

### GET /api/ldap/overview
**Description**: Get LDAP server overview and status

**Security**: Authentication required

**Response**:
```json
{
  "status": "success",
  "data": {
    "server": {
      "status": "running",
      "version": "2.5.13",
      "config_file": "/etc/ldap/slapd.conf",
      "port": 389,
      "ssl_port": 636
    },
    "database": {
      "suffix": "dc=example,dc=com",
      "entries": 1250,
      "size": 1073741824
    },
    "connections": {
      "current": 5,
      "max": 100
    }
  }
}
```

### GET /api/ldap/browse
**Description**: Browse LDAP directory structure

**Security**: Authentication required

**Query Parameters**:
- `dn` - Distinguished name to browse (default: root)
- `scope` - Search scope: base, one, sub (default: sub)
- `filter` - LDAP filter string

**Response**:
```json
{
  "status": "success",
  "data": {
    "current_dn": "dc=example,dc=com",
    "entries": [
      {
        "dn": "ou=users,dc=example,dc=com",
        "objectClass": ["organizationalUnit"],
        "ou": ["users"],
        "description": ["User accounts"]
      },
      {
        "dn": "ou=groups,dc=example,dc=com",
        "objectClass": ["organizationalUnit"],
        "ou": ["groups"],
        "description": ["User groups"]
      }
    ]
  }
}
```

### GET /api/ldap/users
**Description**: Get LDAP users

**Security**: Authentication required

**Query Parameters**:
- `base_dn` - Base DN for search
- `filter` - LDAP filter string
- `attributes` - Comma-separated list of attributes
- `page` - Page number for pagination
- `per_page` - Items per page

**Response**:
```json
{
  "status": "success",
  "data": {
    "users": [
      {
        "dn": "uid=user1,ou=users,dc=example,dc=com",
        "uid": "user1",
        "cn": "User One",
        "mail": "user1@example.com",
        "objectClass": ["inetOrgPerson", "top"]
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 150,
      "pages": 8
    }
  }
}
```

### POST /api/ldap/users
**Description**: Create new LDAP user

**Security**: 
- **Authentication**: Required
- **CSRF Protection**: Required
- **Authorization**: Admin role required

**Request Body**:
```json
{
  "csrf_token": "string",
  "dn": "uid=newuser,ou=users,dc=example,dc=com",
  "attributes": {
    "uid": "newuser",
    "cn": "New User",
    "sn": "User",
    "mail": "newuser@example.com",
    "objectClass": ["inetOrgPerson", "top"]
  }
}
```

**Response**:
```json
{
  "status": "success",
  "message": "LDAP user created successfully",
  "data": {
    "dn": "uid=newuser,ou=users,dc=example,dc=com"
  }
}
```

## Service Control API Endpoints

### POST /api/mail/services/restart
**Description**: Restart mail services

**Security**: 
- **Authentication**: Required
- **CSRF Protection**: Required
- **Authorization**: Admin role required

**Request Body**:
```json
{
  "csrf_token": "string",
  "services": ["postfix", "dovecot"]
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Services restarted successfully",
  "data": {
    "restarted": ["postfix", "dovecot"],
    "timestamp": "2025-08-22T13:00:00Z"
  }
}
```

### GET /api/mail/services/status
**Description**: Get service status

**Security**: Authentication required

**Response**:
```json
{
  "status": "success",
  "data": {
    "postfix": {
      "status": "running",
      "pid": 1234,
      "uptime": "2 days, 3 hours",
      "memory": 52428800
    },
    "dovecot": {
      "status": "running",
      "pid": 1235,
      "uptime": "2 days, 3 hours",
      "memory": 104857600
    },
    "openldap": {
      "status": "running",
      "pid": 1236,
      "uptime": "2 days, 3 hours",
      "memory": 209715200
    }
  }
}
```

## Error Handling

### Standard Error Response Format
```json
{
  "status": "error",
  "message": "Error description",
  "error_code": "ERROR_CODE",
  "details": {
    "field": "Additional error details"
  }
}
```

### Common Error Codes
- `AUTHENTICATION_REQUIRED` - User must be authenticated
- `AUTHORIZATION_DENIED` - User lacks required permissions
- `VALIDATION_ERROR` - Input validation failed
- `RESOURCE_NOT_FOUND` - Requested resource not found
- `SERVICE_UNAVAILABLE` - Service temporarily unavailable
- `INTERNAL_ERROR` - Internal server error

### HTTP Status Codes
- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Access denied
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

## API Versioning

### Current Version
- **Version**: v1
- **Base URL**: `/api/v1/`
- **Status**: Active development

### Versioning Strategy
- URL-based versioning: `/api/v1/`, `/api/v2/`
- Backward compatibility maintained for at least 2 versions
- Deprecation notices provided 6 months in advance
- Breaking changes only in major version releases

## Rate Limiting Headers

### Response Headers
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
Retry-After: 60
```

### Rate Limit Information
- **Limit**: Maximum requests per time window
- **Remaining**: Remaining requests in current window
- **Reset**: Unix timestamp when limit resets
- **Retry-After**: Seconds to wait before retrying

## Testing and Development

### Test Endpoints
- `GET /api/test/health` - Health check endpoint
- `GET /api/test/status` - System status for testing
- `POST /api/test/reset` - Reset test data (development only)

### Development Tools
- **API Documentation**: Interactive documentation at `/api/docs`
- **Testing Interface**: Test endpoint at `/api/test`
- **Debug Mode**: Detailed error information in development

## Conclusion

This API provides comprehensive access to all Postfix Manager functionality while maintaining security and performance standards. The modular design allows for easy extension and maintenance, while the comprehensive security features ensure safe operation in production environments.

For additional information about specific endpoints or implementation details, refer to the individual module documentation or contact the development team.
