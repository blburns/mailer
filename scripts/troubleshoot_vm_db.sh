#!/bin/bash

# Troubleshoot VM Database Issues
# This script helps diagnose and fix common database problems on the VM

set -e

# Configuration - Load from environment files
LOCAL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Load environment variables from .env file if it exists
if [ -f "${LOCAL_DIR}/.env" ]; then
    echo "📋 Loading configuration from .env file..."
    # Source the .env file safely, handling comments and special characters
    set -a
    source "${LOCAL_DIR}/.env"
    set +a
elif [ -f "${LOCAL_DIR}/env.conf.example" ]; then
    echo "📋 Loading configuration from env.conf.example..."
    # Source the example file safely
    set -a
    source "${LOCAL_DIR}/env.conf.example"
    set +a
else
    echo "⚠️  No environment configuration found, using defaults"
fi

# Set defaults if not defined in environment files
VM_HOST="${VM_HOST:-192.168.1.15}"
VM_USER="${VM_USER:-root}"
VM_APP_DIR="${VM_APP_DIR:-/opt/postfix-manager}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Troubleshooting VM Database Issues${NC}"
echo "This script will help diagnose and fix database problems on your VM"
echo ""

# Check SSH connection
echo -e "${YELLOW}🔍 Testing SSH connection...${NC}"
if ! ssh -o ConnectTimeout=5 -o BatchMode=yes "${VM_USER}@${VM_HOST}" "echo 'SSH connection successful'" 2>/dev/null; then
    echo -e "${RED}❌ Cannot connect to VM via SSH${NC}"
    echo "Please check:"
    echo "1. VM is running and accessible"
    echo "2. SSH is enabled on VM"
    echo "3. Your SSH key is added to VM"
    echo "4. VM_HOST, VM_USER are correctly set"
    exit 1
fi

echo -e "${GREEN}✅ SSH connection successful${NC}"
echo ""

# Check VM directory structure
echo -e "${YELLOW}📁 Checking VM directory structure...${NC}"
ssh "${VM_USER}@${VM_HOST}" "cd ${VM_APP_DIR} && \
    echo 'Current directory:' && pwd && \
    echo 'Directory contents:' && ls -la && \
    echo 'Instance directory:' && ls -la instance/ 2>/dev/null || echo 'Instance directory not found' && \
    echo 'Data directory:' && ls -la data/ 2>/dev/null || echo 'Data directory not found'"

echo ""

# Check database file
echo -e "${YELLOW}🗄️  Checking database file...${NC}"
ssh "${VM_USER}@${VM_HOST}" "cd ${VM_APP_DIR} && \
    if [ -f 'instance/postfix_manager.db' ]; then \
        echo 'Database file exists:' && \
        ls -la instance/postfix_manager.db && \
        echo 'File size:' && du -h instance/postfix_manager.db; \
    else \
        echo 'Database file not found in instance/'; \
    fi && \
    if [ -f 'data/db/postfix_manager.db' ]; then \
        echo 'Database file exists in data/db/:' && \
        ls -la data/db/postfix_manager.db && \
        echo 'File size:' && du -h data/db/postfix_manager.db; \
    else \
        echo 'Database file not found in data/db/'; \
    fi"

echo ""

# Check Python environment
echo -e "${YELLOW}🐍 Checking Python environment...${NC}"
ssh "${VM_USER}@${VM_HOST}" "cd ${VM_APP_DIR} && \
    echo 'Python version:' && python3 --version && \
    echo 'Pip version:' && pip --version && \
    echo 'Virtual environment:' && ls -la venv/ 2>/dev/null || echo 'Virtual environment not found' && \
    echo 'Requirements file:' && ls -la requirements.txt 2>/dev/null || echo 'Requirements file not found'"

echo ""

# Check environment variables
echo -e "${YELLOW}⚙️  Checking environment variables...${NC}"
ssh "${VM_USER}@${VM_HOST}" "cd ${VM_APP_DIR} && \
    if [ -f '.env' ]; then \
        echo 'Environment file exists:' && \
        grep -E '^(DATABASE_URL|FLASK_APP|SECRET_KEY)' .env 2>/dev/null || echo 'No relevant env vars found'; \
    else \
        echo 'Environment file not found'; \
    fi"

echo ""

# Check disk space
echo -e "${YELLOW}💾 Checking disk space...${NC}"
ssh "${VM_USER}@${VM_HOST}" "df -h"

echo ""

# Check permissions
echo -e "${YELLOW}🔐 Checking permissions...${NC}"
ssh "${VM_USER}@${VM_HOST}" "cd ${VM_APP_DIR} && \
    echo 'Directory permissions:' && ls -ld . && \
    echo 'Instance directory permissions:' && ls -ld instance/ 2>/dev/null || echo 'Instance directory not found' && \
    echo 'Data directory permissions:' && ls -ld data/ 2>/dev/null || echo 'Data directory not found'"

echo ""

# Try to create database manually
echo -e "${YELLOW}🔧 Attempting to create database manually...${NC}"
ssh "${VM_USER}@${VM_HOST}" "cd ${VM_APP_DIR} && \
    mkdir -p instance && \
    mkdir -p data/db && \
    touch instance/postfix_manager.db && \
    touch data/db/postfix_manager.db && \
    chmod 644 instance/postfix_manager.db && \
    chmod 644 data/db/postfix_manager.db && \
    echo 'Database files created' && \
    ls -la instance/ && \
    ls -la data/db/"

echo ""

# Test Python import
echo -e "${YELLOW}🧪 Testing Python import...${NC}"
ssh "${VM_USER}@${VM_HOST}" "cd ${VM_APP_DIR} && \
    source venv/bin/activate && \
    python3 -c \"import sys; print('Python path:'); [print(p) for p in sys.path]\" 2>/dev/null || echo 'Python import failed'"

echo ""

# Provide solutions
echo -e "${BLUE}💡 Recommended Solutions:${NC}"
echo ""
echo "1. **Fix Dependencies First**:"
echo "   ssh ${VM_USER}@${VM_HOST}"
echo "   cd ${VM_APP_DIR}"
echo "   make vm-fix-deps"
echo ""
echo "2. **Initialize Database with VM Script**:"
echo "   ssh ${VM_USER}@${VM_HOST}"
echo "   cd ${VM_APP_DIR}"
echo "   source venv/bin/activate"
echo "   python scripts/init_vm_db.py"
echo ""
echo "3. **Create Admin User**:"
echo "   ssh ${VM_USER}@${VM_HOST}"
echo "   cd ${VM_APP_DIR}"
echo "   source venv/bin/activate"
echo "   python scripts/create_vm_admin.py"
echo ""
echo "4. **Test Application**:"
echo "   ssh ${VM_USER}@${VM_HOST}"
echo "   cd ${VM_APP_DIR}"
echo "   source venv/bin/activate"
echo "   python -c \"from app import create_app; app = create_app(); print('✅ App works!')\""
echo ""
echo "5. **Run Full Deployment**:"
echo "   make deploy-vm"
echo ""

echo -e "${GREEN}✅ Troubleshooting complete!${NC}"
echo "Follow the recommended solutions above to fix your database issues."
