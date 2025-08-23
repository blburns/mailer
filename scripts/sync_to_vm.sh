#!/bin/bash

# Quick sync script for ongoing development
# This script just syncs code changes without full deployment

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
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔄 Quick sync to VM...${NC}"
echo -e "${BLUE}VM: ${VM_USER}@${VM_HOST}:${VM_APP_DIR}${NC}"
echo ""

# Quick sync (excluding sensitive files)
rsync -avz \
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
echo ""
echo -e "${BLUE}To restart the app on VM:${NC}"
echo "ssh ${VM_USER}@${VM_HOST} 'cd ${VM_APP_DIR} && source venv/bin/activate && pkill -f run.py && python run.py &'"
