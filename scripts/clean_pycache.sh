#!/bin/bash

# Clean Python Cache Script for Postfix Manager
# This script removes Python cache files, compiled files, and temporary files

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧹 Cleaning Python Cache for Postfix Manager${NC}"
echo "This script will remove Python cache files and temporary files"
echo ""

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo -e "${BLUE}📁 Project root: ${PROJECT_ROOT}${NC}"
echo ""

# Function to calculate directory size
get_dir_size() {
    local dir="$1"
    if [ -d "$dir" ]; then
        du -sh "$dir" 2>/dev/null | cut -f1 || echo "0B"
    else
        echo "0B"
    fi
}

# Function to count files
count_files() {
    local pattern="$1"
    find "$PROJECT_ROOT" -name "$pattern" -type f 2>/dev/null | wc -l
}

# Function to clean specific file types
clean_file_type() {
    local pattern="$1"
    local description="$2"
    
    echo -e "${YELLOW}🧹 Cleaning ${description}...${NC}"
    
    # Count files before cleaning
    local count_before=$(count_files "$pattern")
    
    if [ "$count_before" -gt 0 ]; then
        # Find and remove files
        find "$PROJECT_ROOT" -name "$pattern" -type f -delete 2>/dev/null || true
        echo -e "${GREEN}✅ Removed ${count_before} ${description}${NC}"
    else
        echo -e "${BLUE}ℹ️  No ${description} found${NC}"
    fi
}

# Function to clean specific directories
clean_directory() {
    local dir_pattern="$1"
    local description="$2"
    
    echo -e "${YELLOW}🧹 Cleaning ${description}...${NC}"
    
    # Find and remove directories
    local dirs_found=0
    local total_size="0B"
    
    # Use find with -print0 and read to handle paths with spaces
    while IFS= read -r -d '' dir; do
        if [ -d "$dir" ]; then
            local size=$(get_dir_size "$dir")
            echo -e "${YELLOW}  Removing: ${dir} (${size})${NC}"
            rm -rf "$dir" 2>/dev/null || true
            echo -e "${GREEN}    ✅ Removed${NC}"
            ((dirs_found++))
        fi
    done < <(find "$PROJECT_ROOT" -name "$dir_pattern" -type d -print0 2>/dev/null)
    
    if [ "$dirs_found" -eq 0 ]; then
        echo -e "${BLUE}ℹ️  No ${description} found${NC}"
    else
        echo -e "${GREEN}✅ Removed ${dirs_found} ${description}${NC}"
    fi
}

# Main cleaning logic
main() {
    echo -e "${YELLOW}🔧 Starting cleanup process...${NC}"
    echo ""
    
    # Store initial project size
    local initial_size=$(get_dir_size "$PROJECT_ROOT")
    echo -e "${BLUE}📊 Initial project size: ${initial_size}${NC}"
    echo ""
    
    # Clean Python cache files
    echo -e "${BLUE}🐍 Cleaning Python cache files...${NC}"
    clean_file_type "*.pyc" "Python compiled files"
    clean_file_type "*.pyo" "Python optimized files"
    clean_file_type "*.pyd" "Python DLL files"
    
    # Clean Python cache directories
    clean_directory "__pycache__" "Python cache directories"
    
    # Clean specific cache directories
    echo -e "${YELLOW}🧹 Cleaning specific cache directories...${NC}"
    
    # Mypy cache
    if [ -d "$PROJECT_ROOT/.mypy_cache" ]; then
        local size=$(get_dir_size "$PROJECT_ROOT/.mypy_cache")
        rm -rf "$PROJECT_ROOT/.mypy_cache"
        echo -e "${GREEN}✅ Removed mypy cache (${size})${NC}"
    fi
    
    # Pytest cache
    if [ -d "$PROJECT_ROOT/.pytest_cache" ]; then
        local size=$(get_dir_size "$PROJECT_ROOT/.pytest_cache")
        rm -rf "$PROJECT_ROOT/.pytest_cache"
        echo -e "${GREEN}✅ Removed pytest cache (${size})${NC}"
    fi
    
    # Coverage cache
    if [ -d "$PROJECT_ROOT/htmlcov" ]; then
        local size=$(get_dir_size "$PROJECT_ROOT/htmlcov")
        rm -rf "$PROJECT_ROOT/htmlcov"
        echo -e "${GREEN}✅ Removed coverage cache (${size})${NC}"
    fi
    
    # Tox cache
    if [ -d "$PROJECT_ROOT/.tox" ]; then
        local size=$(get_dir_size "$PROJECT_ROOT/.tox")
        rm -rf "$PROJECT_ROOT/.tox"
        echo -e "${GREEN}✅ Removed tox cache (${size})${NC}"
    fi
    
    # Clean temporary files
    echo ""
    echo -e "${BLUE}🗑️  Cleaning temporary files...${NC}"
    clean_file_type "*.tmp" "temporary files"
    clean_file_type "*.temp" "temporary files"
    clean_file_type "*.swp" "Vim swap files"
    clean_file_type "*.swo" "Vim swap files"
    clean_file_type "*~" "backup files"
    clean_file_type "*.bak" "backup files"
    clean_file_type "*.orig" "original files"
    
    # Clean build artifacts
    echo ""
    echo -e "${BLUE}🏗️  Cleaning build artifacts...${NC}"
    
    # Python build directories
    if [ -d "$PROJECT_ROOT/build" ]; then
        local size=$(get_dir_size "$PROJECT_ROOT/build")
        rm -rf "$PROJECT_ROOT/build"
        echo -e "${GREEN}✅ Removed build directory (${size})${NC}"
    fi
    
    if [ -d "$PROJECT_ROOT/dist" ]; then
        local size=$(get_dir_size "$PROJECT_ROOT/dist")
        rm -rf "$PROJECT_ROOT/dist"
        echo -e "${GREEN}✅ Removed dist directory (${size})${NC}"
    fi
    
    # Python egg info
    find "$PROJECT_ROOT" -name "*.egg-info" -type d -exec rm -rf {} + 2>/dev/null || true
    echo -e "${GREEN}✅ Removed egg-info directories${NC}"
    
    # Clean IDE-specific files
    echo ""
    echo -e "${BLUE}💻 Cleaning IDE files...${NC}"
    
    # VS Code
    if [ -d "$PROJECT_ROOT/.vscode" ]; then
        local size=$(get_dir_size "$PROJECT_ROOT/.vscode")
        rm -rf "$PROJECT_ROOT/.vscode"
        echo -e "${GREEN}✅ Removed VS Code settings (${size})${NC}"
    fi
    
    # PyCharm
    if [ -d "$PROJECT_ROOT/.idea" ]; then
        local size=$(get_dir_size "$PROJECT_ROOT/.idea")
        rm -rf "$PROJECT_ROOT/.idea"
        echo -e "${GREEN}✅ Removed PyCharm settings (${size})${NC}"
    fi
    
    # Clean macOS specific files
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo ""
        echo -e "${BLUE}🍎 Cleaning macOS specific files...${NC}"
        clean_file_type ".DS_Store" "macOS .DS_Store files"
        clean_file_type "._*" "macOS resource fork files"
    fi
    
    # Clean logs (optional)
    echo ""
    echo -e "${YELLOW}📝 Log files cleanup (optional)...${NC}"
    read -p "Remove log files? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [ -d "$PROJECT_ROOT/logs" ]; then
            find "$PROJECT_ROOT/logs" -name "*.log" -type f -delete 2>/dev/null || true
            echo -e "${GREEN}✅ Removed log files${NC}"
        fi
    else
        echo -e "${BLUE}ℹ️  Log files preserved${NC}"
    fi
    
    # Final project size
    local final_size=$(get_dir_size "$PROJECT_ROOT")
    local saved_space=$(echo "$initial_size" | sed 's/[^0-9.]//g')
    
    echo ""
    echo -e "${GREEN}✅ Cleanup completed successfully!${NC}"
    echo ""
    echo -e "${BLUE}📊 Cleanup Summary:${NC}"
    echo "• Initial size: ${initial_size}"
    echo "• Final size: ${final_size}"
    echo "• Python cache files removed"
    echo "• Build artifacts removed"
    echo "• Temporary files removed"
    echo "• IDE settings removed (if found)"
    echo ""
    echo -e "${BLUE}💡 Next steps:${NC}"
    echo "1. Test your application: make run"
    echo "2. If running on VM, sync changes: make sync-vm"
    echo "3. Consider running: make fix-permissions"
}

# Run main function
main "$@"
