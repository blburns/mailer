#!/bin/bash

# Quick sync script for ongoing development
# This script syncs code changes and sets proper permissions on the VM

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

# Try to extract user/group from deploy configuration
DEPLOY_USER=""
DEPLOY_GROUP=""

# Check deploy/env.conf.example first
if [ -f "${LOCAL_DIR}/deploy/env.conf.example" ]; then
    echo "📋 Loading deploy configuration..."
    DEPLOY_USER=$(grep "^USER=" "${LOCAL_DIR}/deploy/env.conf.example" | cut -d'=' -f2 | tr -d '\r')
    DEPLOY_GROUP=$(grep "^GROUP=" "${LOCAL_DIR}/deploy/env.conf.example" | cut -d'=' -f2 | tr -d '\r')
fi

# Check deploy/app.conf.example as fallback
if [ -z "$DEPLOY_USER" ] && [ -f "${LOCAL_DIR}/deploy/app.conf.example" ]; then
    echo "📋 Loading app configuration..."
    # Try to extract from app.conf if available
    if grep -q "USER=" "${LOCAL_DIR}/deploy/app.conf.example"; then
        DEPLOY_USER=$(grep "^USER=" "${LOCAL_DIR}/deploy/app.conf.example" | cut -d'=' -f2 | tr -d '\r')
    fi
    if grep -q "GROUP=" "${LOCAL_DIR}/deploy/app.conf.example"; then
        DEPLOY_GROUP=$(grep "^GROUP=" "${LOCAL_DIR}/deploy/app.conf.example" | cut -d'=' -f2 | tr -d '\r')
    fi
fi

# Set defaults if still not found
DEPLOY_USER="${DEPLOY_USER:-www-data}"
DEPLOY_GROUP="${DEPLOY_GROUP:-www-data}"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔄 Quick sync to VM...${NC}"
echo -e "${BLUE}VM: ${VM_USER}@${VM_HOST}:${VM_APP_DIR}${NC}"
echo -e "${BLUE}Target User/Group: ${DEPLOY_USER}:${DEPLOY_GROUP}${NC}"
echo ""

# Quick sync (excluding sensitive files)
rsync -avz --delete \
    --exclude='.git/' \
    --exclude='venv/' \
    --exclude='app/data/logs/' \
    --exclude='app/data/db/*.db' \
    --exclude='app/data/db/*.sqlite' \
    --exclude='app/data/db/*.sqlite3' \
    --exclude='app/data/backups/' \
    --exclude='app/data/cache/' \
    --exclude='app/data/sessions/' \
    --exclude='.env' \
    --exclude='*.pyc' \
    --exclude='__pycache__/' \
    --exclude='.DS_Store' \
    --exclude='*.log' \
    --exclude='*.db' \
    --exclude='*.sqlite' \
    --exclude='*.sqlite3' \
    "${LOCAL_DIR}/" \
    "${VM_USER}@${VM_HOST}:${VM_APP_DIR}/"

echo -e "${GREEN}✅ Code synced successfully${NC}"

# Set proper permissions on the VM
echo -e "${YELLOW}🔐 Setting proper permissions on VM...${NC}"
ssh "${VM_USER}@${VM_HOST}" "cd ${VM_APP_DIR} && \
    echo 'Setting ownership to ${DEPLOY_USER}:${DEPLOY_GROUP}...' && \
    chown -R ${DEPLOY_USER}:${DEPLOY_GROUP} . && \
    echo 'Setting directory permissions...' && \
    find . -type d -exec chmod 755 {} \; && \
    echo 'Setting file permissions (excluding venv)...' && \
    find . -type f -not -path './venv/*' -exec chmod 644 {} \; && \
    echo 'Setting executable permissions for scripts...' && \
    chmod +x scripts/*.sh scripts/*.py && \
    echo 'Setting special permissions for data directories...' && \
    chmod 700 app/data/db app/data/sessions 2>/dev/null || true && \
    chmod 755 app/data/logs app/data/cache app/data/backups app/data/archive app/data/seeds 2>/dev/null || true && \
    echo 'Setting virtual environment permissions...' && \
    chmod +x venv/bin/* && \
    chmod 755 venv/bin && \
    chmod 755 venv/lib && \
    chmod 755 venv/include && \
    echo 'Permissions set successfully'"

echo -e "${GREEN}✅ Permissions set successfully${NC}"
echo ""
echo -e "${BLUE}To restart the app on VM:${NC}"
echo "ssh ${VM_USER}@${VM_HOST} 'cd ${VM_APP_DIR} && source venv/bin/activate && pkill -f run.py && python run.py &'"
