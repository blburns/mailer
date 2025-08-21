#!/bin/bash
# Create Initial Admin User Script for Postfix Manager
# This script creates the first admin user account for the Postfix Manager system.

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "app/__init__.py" ]; then
    print_error "This script must be run from the project root directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_warning "Virtual environment not found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Check if database exists, if not create it
if [ ! -f "postfix_manager.db" ]; then
    print_status "Database not found. Initializing database..."
    python3 -c "
from app import create_app
from app.extensions import db
app = create_app()
with app.app_context():
    db.create_all()
    print('Database initialized successfully')
"
fi

print_status "Running admin user creation script..."
python3 scripts/create_admin.py "$@"

if [ $? -eq 0 ]; then
    print_success "Admin user creation completed successfully!"
    print_status "You can now log in to the Postfix Manager system."
else
    print_error "Failed to create admin user. Please check the error messages above."
    exit 1
fi
