#!/bin/bash

# Fix VM Dependencies Script
# Specifically targets python-ldap compilation issues on Ubuntu/Debian VMs

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 Fixing VM Dependencies for python-ldap${NC}"
echo "This script fixes the common python-ldap compilation error"
echo ""

# Detect system
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if command -v apt-get &> /dev/null; then
        SYSTEM="debian"
    elif command -v yum &> /dev/null || command -v dnf &> /dev/null; then
        SYSTEM="redhat"
    else
        echo -e "${RED}❌ Unsupported Linux distribution${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ This script is designed for Linux VMs${NC}"
    exit 1
fi

echo -e "${BLUE}🖥️  Detected system: ${SYSTEM}${NC}"
echo ""

# Fix dependencies for Debian/Ubuntu
if [[ "$SYSTEM" == "debian" ]]; then
    echo -e "${YELLOW}📦 Installing dependencies for Debian/Ubuntu...${NC}"
    
    # Update package list
    sudo apt-get update
    
    # Install essential build dependencies
    sudo apt-get install -y \
        python3-dev \
        libldap2-dev \
        libsasl2-dev \
        libssl-dev \
        libffi-dev \
        gcc \
        g++ \
        make \
        build-essential
    
    echo -e "${GREEN}✅ Dependencies installed successfully${NC}"
    
elif [[ "$SYSTEM" == "redhat" ]]; then
    echo -e "${YELLOW}📦 Installing dependencies for RedHat/CentOS...${NC}"
    
    # Determine package manager
    if command -v dnf &> /dev/null; then
        PKG_MGR="dnf"
    else
        PKG_MGR="yum"
    fi
    
    # Update package list
    sudo $PKG_MGR update -y
    
    # Install essential build dependencies
    sudo $PKG_MGR install -y \
        python3-devel \
        openldap-devel \
        cyrus-sasl-devel \
        openssl-devel \
        libffi-devel \
        gcc \
        gcc-c++ \
        make
    
    echo -e "${GREEN}✅ Dependencies installed successfully${NC}"
fi

echo ""
echo -e "${YELLOW}🐍 Now trying to install Python packages...${NC}"

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ requirements.txt not found. Please run this from the project root.${NC}"
    exit 1
fi

# Try to install requirements again
if [ -d "venv" ]; then
    echo "Activating existing virtual environment..."
    source venv/bin/activate
else
    echo "Creating new virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Upgrade pip and install wheel
pip install --upgrade pip setuptools wheel

# Try to install python-ldap first (the problematic package)
echo "Installing python-ldap..."
pip install python-ldap

# Now install the rest
echo "Installing remaining requirements..."
pip install -r requirements.txt

echo ""
echo -e "${GREEN}🎉 Dependencies fixed successfully!${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Test the application: python -c 'from app import create_app; print(\"✅ App works!\")'"
echo "2. Initialize database: python scripts/init_db.py"
echo "3. Create admin user: python scripts/create_admin.py"
echo "4. Run the application: python run.py"
echo ""
echo -e "${BLUE}If you still have issues:${NC}"
echo "1. Check system logs: sudo journalctl -xe"
echo "2. Verify libraries: ldconfig -p | grep ldap"
echo "3. Check Python path: python3 -c 'import sys; print(sys.path)'"
