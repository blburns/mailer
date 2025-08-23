#!/bin/bash
# Database Initialization Script for Postfix Manager
# Supports SQLite, MySQL/MariaDB, and PostgreSQL

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}📊 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to check if Python script exists
check_python_script() {
    if [ ! -f "scripts/init_db.py" ]; then
        print_error "init_db.py not found in scripts directory"
        exit 1
    fi
}

# Function to check environment file
check_env_file() {
    if [ ! -f ".env" ]; then
        print_warning ".env file not found"
        if [ -f "env.example" ]; then
            print_status "Copying env.example to .env..."
            cp env.example .env
            print_warning "Please edit .env with your actual database configuration"
        else
            print_error "No environment configuration found"
            exit 1
        fi
    fi
}

# Function to get database type from environment
get_db_type() {
    if [ -f ".env" ]; then
        # Source .env file and get DB_TYPE
        export $(grep -v '^#' .env | xargs)
        echo "${DB_TYPE:-sqlite}"
    else
        echo "sqlite"
    fi
}

# Function to validate database configuration
validate_db_config() {
    local db_type=$1
    
    case $db_type in
        sqlite)
            print_status "SQLite database detected"
            # SQLite doesn't need additional validation
            ;;
        mysql|mariadb)
            print_status "MySQL/MariaDB database detected"
            # Check if required variables are set
            if [ -z "$DB_HOSTNAME" ] || [ -z "$DB_USERNAME" ] || [ -z "$DB_PASSWORD" ] || [ -z "$DB_NAME" ]; then
                print_error "MySQL/MariaDB configuration incomplete. Please check .env file:"
                print_error "Required: DB_HOSTNAME, DB_USERNAME, DB_PASSWORD, DB_NAME"
                exit 1
            fi
            ;;
        postgresql)
            print_status "PostgreSQL database detected"
            # Check if required variables are set
            if [ -z "$DB_HOSTNAME" ] || [ -z "$DB_USERNAME" ] || [ -z "$DB_PASSWORD" ] || [ -z "$DB_NAME" ]; then
                print_error "PostgreSQL configuration incomplete. Please check .env file:"
                print_error "Required: DB_HOSTNAME, DB_USERNAME, DB_PASSWORD, DB_NAME"
                exit 1
            fi
            ;;
        *)
            print_error "Unsupported database type: $db_type"
            print_error "Supported types: sqlite, mysql, mariadb, postgresql"
            exit 1
            ;;
    esac
}

# Function to initialize database
init_database() {
    local db_type=$1
    
    print_status "Initializing $db_type database..."
    
    # Run the Python initialization script
    if python3 scripts/init_db.py; then
        print_success "Database initialization completed successfully!"
    else
        print_error "Database initialization failed"
        exit 1
    fi
}

# Main function
main() {
    echo "🚀 Postfix Manager - Database Initialization"
    echo "=========================================="
    echo ""
    
    # Check if we're in the right directory
    if [ ! -f "run.py" ]; then
        print_error "Please run this script from the project root directory"
        exit 1
    fi
    
    # Check prerequisites
    check_python_script
    check_env_file
    
    # Get database type
    local db_type=$(get_db_type)
    print_status "Database type: $db_type"
    
    # Validate configuration
    validate_db_config "$db_type"
    
    # Initialize database
    init_database "$db_type"
    
    echo ""
    print_success "Database initialization complete!"
    print_status "Next steps:"
    echo "  1. Run: python3 scripts/create_admin.py"
    echo "  2. Start the application: python3 run.py"
}

# Run main function
main "$@"
