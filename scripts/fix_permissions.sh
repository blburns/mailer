#!/bin/bash

# Fix Permissions Script for Postfix Manager
# This script fixes file and directory permissions for proper operation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔐 Fixing Permissions for Postfix Manager${NC}"
echo "This script will fix file and directory permissions"
echo ""

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo -e "${BLUE}📁 Project root: ${PROJECT_ROOT}${NC}"
echo ""

# Function to check if running as root
check_root() {
    if [[ "$EUID" -eq 0 ]]; then
        echo -e "${YELLOW}⚠️  Running as root - be careful with permissions${NC}"
        return 0
    else
        echo -e "${GREEN}✅ Running as regular user${NC}"
        return 1
    fi
}

# Function to fix directory permissions
fix_directory_permissions() {
    local dir="$1"
    local perms="$2"
    
    if [ -d "$dir" ]; then
        echo -e "${YELLOW}📁 Fixing permissions for: ${dir}${NC}"
        chmod "$perms" "$dir"
        echo -e "${GREEN}✅ Set permissions ${perms} on ${dir}${NC}"
    else
        echo -e "${YELLOW}⚠️  Directory not found: ${dir}${NC}"
    fi
}

# Function to fix file permissions
fix_file_permissions() {
    local file="$1"
    local perms="$2"
    
    if [ -f "$file" ]; then
        echo -e "${YELLOW}📄 Fixing permissions for: ${file}${NC}"
        chmod "$perms" "$file"
        echo -e "${GREEN}✅ Set permissions ${perms} on ${file}${NC}"
    else
        echo -e "${YELLOW}⚠️  File not found: ${file}${NC}"
    fi
}

# Function to fix ownership (if running as root)
fix_ownership() {
    local path="$1"
    local user="$2"
    local group="$3"
    
    if [[ "$EUID" -eq 0 ]] && [ -e "$path" ]; then
        echo -e "${YELLOW}👤 Fixing ownership for: ${path}${NC}"
        chown "$user:$group" "$path"
        echo -e "${GREEN}✅ Set ownership ${user}:${group} on ${path}${NC}"
    fi
}

# Main permission fixing logic
main() {
    echo -e "${YELLOW}🔧 Starting permission fixes...${NC}"
    echo ""
    
    # Check if running as root
    is_root=$(check_root)
    
    # Fix script permissions (executable)
    echo -e "${BLUE}📜 Fixing script permissions...${NC}"
    find "$PROJECT_ROOT/scripts" -name "*.sh" -type f -exec chmod +x {} \;
    echo -e "${GREEN}✅ Scripts made executable${NC}"
    
    # Fix Python script permissions
    find "$PROJECT_ROOT/scripts" -name "*.py" -type f -exec chmod +x {} \;
    echo -e "${GREEN}✅ Python scripts made executable${NC}"
    
    # Fix directory permissions
    echo ""
    echo -e "${BLUE}📁 Fixing directory permissions...${NC}"
    
    # Main project directories
    fix_directory_permissions "$PROJECT_ROOT" "755"
    fix_directory_permissions "$PROJECT_ROOT/app" "755"
    fix_directory_permissions "$PROJECT_ROOT/app/modules" "755"
    fix_directory_permissions "$PROJECT_ROOT/app/config" "755"
    fix_directory_permissions "$PROJECT_ROOT/app/extensions" "755"
    fix_directory_permissions "$PROJECT_ROOT/app/models" "755"
    fix_directory_permissions "$PROJECT_ROOT/app/utils" "755"
    fix_directory_permissions "$PROJECT_ROOT/app/static" "755"
    fix_directory_permissions "$PROJECT_ROOT/app/templates" "755"
    
    # Data and instance directories
    fix_directory_permissions "$PROJECT_ROOT/instance" "755"
    fix_directory_permissions "$PROJECT_ROOT/data" "755"
    fix_directory_permissions "$PROJECT_ROOT/data/backups" "755"
    fix_directory_permissions "$PROJECT_ROOT/data/cache" "755"
    fix_directory_permissions "$PROJECT_ROOT/data/db" "755"
    
    # Logs directory
    fix_directory_permissions "$PROJECT_ROOT/logs" "755"
    
    # Scripts directory
    fix_directory_permissions "$PROJECT_ROOT/scripts" "755"
    
    # Fix file permissions
    echo ""
    echo -e "${BLUE}📄 Fixing file permissions...${NC}"
    
    # Configuration files
    fix_file_permissions "$PROJECT_ROOT/.env" "600"
    fix_file_permissions "$PROJECT_ROOT/env.conf.example" "644"
    fix_file_permissions "$PROJECT_ROOT/requirements.txt" "644"
    fix_file_permissions "$PROJECT_ROOT/setup.py" "644"
    fix_file_permissions "$PROJECT_ROOT/pyproject.toml" "644"
    fix_file_permissions "$PROJECT_ROOT/Makefile" "644"
    
    # Python files
    find "$PROJECT_ROOT" -name "*.py" -type f -exec chmod 644 {} \;
    echo -e "${GREEN}✅ Python files set to 644${NC}"
    
    # HTML and template files
    find "$PROJECT_ROOT" -name "*.html" -type f -exec chmod 644 {} \;
    find "$PROJECT_ROOT" -name "*.css" -type f -exec chmod 644 {} \;
    find "$PROJECT_ROOT" -name "*.js" -type f -exec chmod 644 {} \;
    echo -e "${GREEN}✅ Template files set to 644${NC}"
    
    # Documentation files
    find "$PROJECT_ROOT/docs" -name "*.md" -type f -exec chmod 644 {} \;
    echo -e "${GREEN}✅ Documentation files set to 644${NC}"
    
    # Fix ownership if running as root
    if [[ "$EUID" -eq 0 ]]; then
        echo ""
        echo -e "${BLUE}👤 Fixing ownership...${NC}"
        
        # Get current user from SUDO_USER or default to current user
        SUDO_USER="${SUDO_USER:-$(whoami)}"
        CURRENT_GROUP="$(id -gn "$SUDO_USER")"
        
        echo -e "${YELLOW}📋 Setting ownership to: ${SUDO_USER}:${CURRENT_GROUP}${NC}"
        
        # Fix ownership of main project
        fix_ownership "$PROJECT_ROOT" "$SUDO_USER" "$CURRENT_GROUP"
        
        # Fix ownership of specific directories
        fix_ownership "$PROJECT_ROOT/instance" "$SUDO_USER" "$CURRENT_GROUP"
        fix_ownership "$PROJECT_ROOT/data" "$SUDO_USER" "$CURRENT_GROUP"
        fix_ownership "$PROJECT_ROOT/logs" "$SUDO_USER" "$CURRENT_GROUP"
        
        # Fix ownership of configuration files
        fix_ownership "$PROJECT_ROOT/.env" "$SUDO_USER" "$CURRENT_GROUP"
    fi
    
    # Special permission fixes for sensitive files
    echo ""
    echo -e "${BLUE}🔒 Fixing sensitive file permissions...${NC}"
    
    # Database files should be readable/writable by owner only
    if [ -f "$PROJECT_ROOT/instance/postfix_manager.db" ]; then
        chmod 600 "$PROJECT_ROOT/instance/postfix_manager.db"
        echo -e "${GREEN}✅ Database file set to 600${NC}"
    fi
    
    # Log files should be readable/writable by owner only
    find "$PROJECT_ROOT/logs" -name "*.log" -type f -exec chmod 600 {} \; 2>/dev/null || true
    echo -e "${GREEN}✅ Log files set to 600${NC}"
    
    # Virtual environment permissions
    if [ -d "$PROJECT_ROOT/venv" ]; then
        echo -e "${YELLOW}🐍 Fixing virtual environment permissions...${NC}"
        chmod 755 "$PROJECT_ROOT/venv"
        find "$PROJECT_ROOT/venv/bin" -type f -exec chmod 755 {} \;
        echo -e "${GREEN}✅ Virtual environment permissions fixed${NC}"
    fi
    
    echo ""
    echo -e "${GREEN}✅ Permission fixes completed successfully!${NC}"
    echo ""
    echo -e "${BLUE}📋 Summary of permission changes:${NC}"
    echo "• Scripts: 755 (executable)"
    echo "• Directories: 755 (readable/executable by all, writable by owner)"
    echo "• Python files: 644 (readable by all, writable by owner)"
    echo "• Configuration files: 644 (readable by all, writable by owner)"
    echo "• Sensitive files (.env, database, logs): 600 (owner only)"
    echo "• Template files: 644 (readable by all, writable by owner)"
    echo ""
    echo -e "${BLUE}💡 Next steps:${NC}"
    echo "1. Test your application: make run"
    echo "2. Check if any permission errors are resolved"
    echo "3. If running on VM, sync changes: make sync-vm"
}

# Run main function
main "$@"
