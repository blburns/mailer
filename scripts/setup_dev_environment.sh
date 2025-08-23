#!/bin/bash

# Setup development environment for Postfix-Manager
# This script helps configure your Mac + Ubuntu VM development setup

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Setting up Postfix-Manager development environment...${NC}"
echo ""

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${RED}❌ This script is designed for macOS${NC}"
    exit 1
fi

# Check prerequisites
echo -e "${YELLOW}🔍 Checking prerequisites...${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    echo "Install with: brew install python3"
    exit 1
fi

# Check rsync
if ! command -v rsync &> /dev/null; then
    echo -e "${YELLOW}⚠️  rsync not found, installing...${NC}"
    brew install rsync
fi

# Check SSH
if ! command -v ssh &> /dev/null; then
    echo -e "${RED}❌ SSH is not available${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}📝 Creating .env file...${NC}"
    if [ -f "env.conf.example" ]; then
        cp env.conf.example .env
        echo -e "${GREEN}✅ .env file created from example${NC}"
        echo -e "${YELLOW}⚠️  Please edit .env with your actual values${NC}"
    else
        echo -e "${YELLOW}⚠️  env.conf.example not found, creating basic .env${NC}"
        cat > .env << EOF
# Environment Configuration
FLASK_APP=run.py
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=dev-secret-key-change-in-production
DATABASE_URL=sqlite:///instance/postfix_manager.db
DEBUG=True
TESTING=False
EOF
        echo -e "${GREEN}✅ Basic .env file created${NC}"
    fi
else
    echo -e "${GREEN}✅ .env file already exists${NC}"
fi

# Setup Python virtual environment
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}🐍 Creating Python virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

# Activate virtual environment and install dependencies
echo -e "${YELLOW}📦 Installing dependencies...${NC}"
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✅ Dependencies installed${NC}"

# Create necessary directories
echo -e "${YELLOW}📁 Creating necessary directories...${NC}"
mkdir -p app/data/{logs,db,backups,cache,archive,seeds,sessions}
echo -e "${GREEN}✅ Directories created in app/data/${NC}"

# Initialize database
echo -e "${YELLOW}🗄️  Initializing database...${NC}"
if [ -f "scripts/init_db.py" ]; then
    python scripts/init_db.py
    echo -e "${GREEN}✅ Database initialized${NC}"
else
    echo -e "${YELLOW}⚠️  init_db.py not found, skipping database initialization${NC}"
fi

# Setup VM configuration
echo ""
echo -e "${BLUE}🔧 VM Configuration Setup${NC}"
echo "To complete your VM development setup, you need to:"
echo ""
echo "1. Set environment variables in your shell profile (~/.zshrc or ~/.bash_profile):"
echo "   export VM_HOST=\"YOUR_VM_IP_ADDRESS\""
echo "   export VM_USER=\"YOUR_VM_USERNAME\""
echo "   export VM_APP_DIR=\"/home/YOUR_VM_USERNAME/postfix-manager\""
echo ""
echo "2. Ensure SSH access to your VM:"
echo "   ssh-copy-id YOUR_VM_USERNAME@YOUR_VM_IP_ADDRESS"
echo ""
echo "3. Deploy to VM:"
echo "   make deploy-vm"
echo ""

# Test the application
echo -e "${YELLOW}🧪 Testing local application...${NC}"
if python -c "from app import create_app; app = create_app(); print('✅ App imports successfully')" 2>/dev/null; then
    echo -e "${GREEN}✅ Local application test passed${NC}"
else
    echo -e "${RED}❌ Local application test failed${NC}"
    echo "Check the error messages above"
fi

echo ""
echo -e "${GREEN}🎉 Development environment setup complete!${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Edit .env file with your configuration"
echo "2. Configure VM environment variables"
echo "3. Set up SSH access to your VM"
echo "4. Deploy to VM with: make deploy-vm"
echo ""
echo -e "${BLUE}Available commands:${NC}"
echo "make run            # Run locally"
echo "make deploy-vm      # Deploy to VM"
echo "make sync-vm        # Sync changes to VM"
echo "make help           # Show all available commands"
