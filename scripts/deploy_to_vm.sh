#!/bin/bash

# Deploy Postfix-Manager to Ubuntu VM for testing
# This script syncs your local development code to the VM

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
    set +a
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

echo -e "${BLUE}🚀 Deploying Postfix-Manager to VM...${NC}"
echo -e "${BLUE}VM: ${VM_USER}@${VM_HOST}:${VM_APP_DIR}${NC}"
echo -e "${BLUE}Local: ${LOCAL_DIR}${NC}"
echo ""

# Check if rsync is available
if ! command -v rsync &> /dev/null; then
    echo -e "${RED}❌ rsync is not installed. Please install it first.${NC}"
    echo "On macOS: brew install rsync"
    echo "On Ubuntu: sudo apt-get install rsync"
    exit 1
fi

# Test SSH connection
echo -e "${YELLOW}🔍 Testing SSH connection to VM...${NC}"
if ! ssh -o ConnectTimeout=5 -o BatchMode=yes "${VM_USER}@${VM_HOST}" "echo 'SSH connection successful'" 2>/dev/null; then
    echo -e "${RED}❌ Cannot connect to VM via SSH${NC}"
    echo "Please ensure:"
    echo "1. VM is running and accessible"
    echo "2. SSH is enabled on VM"
    echo "3. Your SSH key is added to VM"
    echo "4. VM_HOST, VM_USER are correctly set"
    exit 1
fi

echo -e "${GREEN}✅ SSH connection successful${NC}"

# Create app directory on VM if it doesn't exist
echo -e "${YELLOW}📁 Creating app directory on VM...${NC}"
ssh "${VM_USER}@${VM_HOST}" "mkdir -p ${VM_APP_DIR}"

# Sync code to VM (excluding sensitive files)
echo -e "${YELLOW}📤 Syncing code to VM...${NC}"
rsync -avz --delete \
    --exclude='.git/' \
    --exclude='venv/' \
    --exclude='instance/' \
    --exclude='logs/' \
    --exclude='.env' \
    --exclude='*.pyc' \
    --exclude='__pycache__/' \
    --exclude='.DS_Store' \
    --exclude='*.log' \
    --exclude='*.db' \
    --exclude='*.sqlite' \
    --exclude='*.sqlite3' \
    --exclude='backups/' \
    --exclude='restore/' \
    "${LOCAL_DIR}/" \
    "${VM_USER}@${VM_HOST}:${VM_APP_DIR}/"

echo -e "${GREEN}✅ Code synced successfully${NC}"

# Set up Python environment on VM
echo -e "${YELLOW}🐍 Setting up Python environment on VM...${NC}"
ssh "${VM_USER}@${VM_HOST}" "cd ${VM_APP_DIR} && \
    if [ ! -d 'venv' ]; then \
        python3 -m venv venv; \
    fi && \
    source venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt"

echo -e "${GREEN}✅ Python environment set up${NC}"

# Create necessary directories on VM
echo -e "${YELLOW}📁 Creating necessary directories on VM...${NC}"
ssh "${VM_USER}@${VM_HOST}" "cd ${VM_APP_DIR} && \
    mkdir -p instance logs data/backups data/cache"

# Set up environment file on VM
echo -e "${YELLOW}⚙️  Setting up environment configuration on VM...${NC}"
ssh "${VM_USER}@${VM_HOST}" "cd ${VM_APP_DIR} && \
    if [ ! -f '.env' ]; then \
        cp env.conf.example .env; \
        echo 'VM_HOST=${VM_HOST}' >> .env; \
        echo 'VM_USER=${VM_USER}' >> .env; \
        echo 'VM_APP_DIR=${VM_APP_DIR}' >> .env; \
        echo 'FLASK_ENV=production' >> .env; \
        echo 'DEBUG=False' >> .env; \
    fi"

echo -e "${GREEN}✅ Environment configured${NC}"

# Initialize database on VM
echo -e "${YELLOW}🗄️  Initializing database on VM...${NC}"
ssh "${VM_USER}@${VM_HOST}" "cd ${VM_APP_DIR} && \
    source venv/bin/activate && \
    python scripts/init_vm_db.py"

echo -e "${GREEN}✅ Database initialized${NC}"

# Test the application
echo -e "${YELLOW}🧪 Testing application on VM...${NC}"
ssh "${VM_USER}@${VM_HOST}" "cd ${VM_APP_DIR} && \
    source venv/bin/activate && \
    python -c \"from app import create_app; app = create_app(); print('✅ App imports successfully')\""

# Create admin user
echo -e "${YELLOW}👤 Creating admin user on VM...${NC}"
ssh "${VM_USER}@${VM_HOST}" "cd ${VM_APP_DIR} && \
    source venv/bin/activate && \
    python scripts/create_vm_admin.py"

echo -e "${GREEN}✅ Application test passed${NC}"

# Show deployment summary
echo ""
echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. SSH to VM: ssh ${VM_USER}@${VM_HOST}"
echo "2. Navigate to app: cd ${VM_APP_DIR}"
echo "3. Activate environment: source venv/bin/activate"
echo "4. Run the app: python run.py"
echo ""
echo -e "${BLUE}Or run directly:${NC}"
echo "ssh ${VM_USER}@${VM_HOST} 'cd ${VM_APP_DIR} && source venv/bin/activate && python run.py'"
echo ""
echo -e "${BLUE}To monitor logs:${NC}"
echo "ssh ${VM_USER}@${VM_HOST} 'cd ${VM_APP_DIR} && tail -f logs/postfix-manager.log'"
