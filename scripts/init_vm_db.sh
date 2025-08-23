#!/bin/bash
# VM Database Initialization Script for Postfix Manager
# Supports SQLite, MySQL/MariaDB, and PostgreSQL on VM environments

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
    if [ ! -f "scripts/init_vm_db.py" ]; then
        print_error "init_vm_db.py not found in scripts directory"
        exit 1
    fi
}

# Function to check environment file
check_env_file() {
    if [ ! -f ".env" ]; then
        print_warning ".env file not found"
        if [ -f "env.conf.example" ]; then
            print_status "Copying env.conf.example to .env..."
            cp env.conf.example .env
            print_warning "Please edit .env with your actual database configuration"
        elif [ -f "env.example" ]; then
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
            # Check if we can write to the data directory
            local data_dir="/opt/postfix-manager/app/data/db"
            if [ ! -w "$data_dir" ] && [ ! -w "$(dirname "$data_dir")" ]; then
                print_warning "Cannot write to data directory: $data_dir"
                print_status "Attempting to create directory with proper permissions..."
                sudo mkdir -p "$data_dir"
                sudo chown "$(whoami):$(id -gn)" "$data_dir"
                sudo chmod 755 "$data_dir"
            fi
            ;;
        mysql|mariadb)
            print_status "MySQL/MariaDB database detected"
            # Check if required variables are set
            if [ -z "$DB_HOSTNAME" ] || [ -z "$DB_USERNAME" ] || [ -z "$DB_PASSWORD" ] || [ -z "$DB_NAME" ]; then
                print_error "MySQL/MariaDB configuration incomplete. Please check .env file:"
                print_error "Required: DB_HOSTNAME, DB_USERNAME, DB_PASSWORD, DB_NAME"
                exit 1
            fi
            
            # Check if MySQL client is available
            if ! command -v mysql &> /dev/null; then
                print_warning "MySQL client not found. Installing..."
                if command -v apt-get &> /dev/null; then
                    sudo apt-get update && sudo apt-get install -y mysql-client
                elif command -v yum &> /dev/null; then
                    sudo yum install -y mysql
                else
                    print_error "Cannot install MySQL client automatically"
                    print_error "Please install MySQL client manually"
                fi
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
            
            # Check if PostgreSQL client is available
            if ! command -v psql &> /dev/null; then
                print_warning "PostgreSQL client not found. Installing..."
                if command -v apt-get &> /dev/null; then
                    sudo apt-get update && sudo apt-get install -y postgresql-client
                elif command -v yum &> /dev/null; then
                    sudo yum install -y postgresql
                else
                    print_error "Cannot install PostgreSQL client automatically"
                    print_error "Please install PostgreSQL client manually"
                fi
            fi
            ;;
        *)
            print_error "Unsupported database type: $db_type"
            print_error "Supported types: sqlite, mysql, mariadb, postgresql"
            exit 1
            ;;
    esac
}

# Function to test database connection
test_db_connection() {
    local db_type=$1
    
    case $db_type in
        mysql|mariadb)
            print_status "Testing MySQL/MariaDB connection..."
            if mysql -h"$DB_HOSTNAME" -P"$DB_PORT" -u"$DB_USERNAME" -p"$DB_PASSWORD" -e "SELECT 1;" &> /dev/null; then
                print_success "MySQL/MariaDB connection successful"
            else
                print_error "MySQL/MariaDB connection failed"
                print_error "Please check your database configuration and ensure the server is running"
                exit 1
            fi
            ;;
        postgresql)
            print_status "Testing PostgreSQL connection..."
            if PGPASSWORD="$DB_PASSWORD" psql -h"$DB_HOSTNAME" -p"$DB_PORT" -U"$DB_USERNAME" -d"$DB_NAME" -c "SELECT 1;" &> /dev/null; then
                print_success "PostgreSQL connection successful"
            else
                print_error "PostgreSQL connection failed"
                print_error "Please check your database configuration and ensure the server is running"
                exit 1
            fi
            ;;
        sqlite)
            # SQLite doesn't need connection testing
            ;;
    esac
}

# Function to initialize database
init_database() {
    local db_type=$1
    
    print_status "Initializing $db_type database on VM..."
    
    # Run the Python initialization script
    if python3 scripts/init_vm_db.py; then
        print_success "Database initialization completed successfully!"
    else
        print_error "Database initialization failed"
        exit 1
    fi
}

# Function to set VM-specific environment
setup_vm_environment() {
    print_status "Setting up VM environment..."
    
    # Set VM-specific environment variables if not already set
    if [ -z "$FLASK_ENV" ]; then
        export FLASK_ENV=production
        print_status "Set FLASK_ENV=production"
    fi
    
    if [ -z "$DEBUG" ]; then
        export DEBUG=False
        print_status "Set DEBUG=False"
    fi
    
    # Ensure we're in the right directory
    if [ ! -f "run.py" ]; then
        print_error "Please run this script from the project root directory"
        exit 1
    fi
}

# Main function
main() {
    echo "🚀 Postfix Manager - VM Database Initialization"
    echo "=============================================="
    echo ""
    
    # Setup VM environment
    setup_vm_environment
    
    # Check prerequisites
    check_python_script
    check_env_file
    
    # Get database type
    local db_type=$(get_db_type)
    print_status "Database type: $db_type"
    
    # Validate configuration
    validate_db_config "$db_type"
    
    # Test database connection for remote databases
    test_db_connection "$db_type"
    
    # Initialize database
    init_database "$db_type"
    
    echo ""
    print_success "VM database initialization complete!"
    print_status "Next steps:"
    echo "  1. Run: python3 scripts/create_admin.py"
    echo "  2. Start the application: python3 run.py"
    echo "  3. Or use systemd service: sudo systemctl start postfix-manager"
}

# Run main function
main "$@"
