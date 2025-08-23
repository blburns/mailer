#!/bin/bash

# Install VM Dependencies Script
# Supports Ubuntu/Debian, RedHat/CentOS, macOS, and FreeBSD
# This script installs system dependencies needed for Python packages

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 Installing System Dependencies${NC}"
echo "Detecting operating system and package manager..."
echo ""

# Function to detect OS and package manager
detect_system() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt-get &> /dev/null; then
            echo "debian"
        elif command -v yum &> /dev/null || command -v dnf &> /dev/null; then
            echo "redhat"
        else
            echo "unknown_linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "freebsd"* ]]; then
        echo "freebsd"
    else
        echo "unknown"
    fi
}

# Function to install dependencies for Debian/Ubuntu
install_debian_deps() {
    echo -e "${YELLOW}📦 Installing dependencies for Debian/Ubuntu (apt)...${NC}"
    
    # Update package list
    sudo apt-get update
    
    # Install system dependencies
    sudo apt-get install -y \
        python3-dev \
        python3-pip \
        python3-venv \
        libldap2-dev \
        libsasl2-dev \
        libssl-dev \
        libffi-dev \
        gcc \
        g++ \
        make \
        build-essential \
        libpcre3-dev \
        libxml2-dev \
        libxslt1-dev \
        libjpeg-dev \
        libpng-dev \
        libfreetype6-dev \
        libsqlite3-dev \
        libmysqlclient-dev \
        libpq-dev \
        curl \
        wget \
        git \
        rsync \
        vim \
        nano \
        htop \
        unzip \
        zip
    
    echo -e "${GREEN}✅ Debian/Ubuntu dependencies installed successfully${NC}"
}

# Function to install dependencies for RedHat/CentOS
install_redhat_deps() {
    echo -e "${YELLOW}📦 Installing dependencies for RedHat/CentOS (yum/dnf)...${NC}"
    
    # Determine package manager
    if command -v dnf &> /dev/null; then
        PKG_MGR="dnf"
    else
        PKG_MGR="yum"
    fi
    
    # Update package list
    sudo $PKG_MGR update -y
    
    # Install system dependencies
    sudo $PKG_MGR install -y \
        python3-devel \
        python3-pip \
        python3-virtualenv \
        openldap-devel \
        cyrus-sasl-devel \
        openssl-devel \
        libffi-devel \
        gcc \
        gcc-c++ \
        make \
        redhat-rpm-config \
        pcre-devel \
        libxml2-devel \
        libxslt-devel \
        libjpeg-turbo-devel \
        libpng-devel \
        freetype-devel \
        sqlite-devel \
        mysql-devel \
        postgresql-devel \
        curl \
        wget \
        git \
        rsync \
        vim \
        nano \
        htop \
        unzip \
        zip
    
    echo -e "${GREEN}✅ RedHat/CentOS dependencies installed successfully${NC}"
}

# Function to install dependencies for macOS
install_macos_deps() {
    echo -e "${YELLOW}📦 Installing dependencies for macOS (Homebrew)...${NC}"
    
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        echo -e "${YELLOW}🍺 Installing Homebrew...${NC}"
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        # Add Homebrew to PATH for M1 Macs
        if [[ $(uname -m) == "arm64" ]]; then
            echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
            eval "$(/opt/homebrew/bin/brew shellenv)"
        fi
    fi
    
    # Update Homebrew
    brew update
    
    # Install system dependencies
    brew install \
        python@3.11 \
        openldap \
        cyrus-sasl \
        openssl@3 \
        pcre \
        libxml2 \
        libxslt \
        jpeg \
        libpng \
        freetype \
        sqlite \
        mysql \
        postgresql \
        curl \
        wget \
        git \
        rsync \
        vim \
        nano \
        htop \
        unzip \
        zip
    
    echo -e "${GREEN}✅ macOS dependencies installed successfully${NC}"
}

# Function to install dependencies for FreeBSD
install_freebsd_deps() {
    echo -e "${YELLOW}📦 Installing dependencies for FreeBSD (pkg)...${NC}"
    
    # Update package list
    sudo pkg update
    
    # Install system dependencies
    sudo pkg install -y \
        python311 \
        py311-pip \
        py311-virtualenv \
        openldap24-client \
        cyrus-sasl \
        openssl \
        libffi \
        gcc \
        gmake \
        pcre \
        libxml2 \
        libxslt \
        jpeg \
        png \
        freetype2 \
        sqlite3 \
        mysql80-client \
        postgresql15-client \
        curl \
        wget \
        git \
        rsync \
        vim \
        nano \
        htop \
        unzip \
        zip
    
    echo -e "${GREEN}✅ FreeBSD dependencies installed successfully${NC}"
}

# Function to install Python packages
install_python_packages() {
    echo -e "${YELLOW}🐍 Installing Python packages...${NC}"
    
    # Check if virtual environment exists
    if [ -d "venv" ]; then
        echo "Activating existing virtual environment..."
        source venv/bin/activate
    else
        echo "Creating new virtual environment..."
        python3 -m venv venv
        source venv/bin/activate
    fi
    
    # Upgrade pip
    pip install --upgrade pip setuptools wheel
    
    # Install Python packages
    if [ -f "requirements.txt" ]; then
        echo "Installing requirements from requirements.txt..."
        pip install -r requirements.txt
    else
        echo "Installing core dependencies..."
        pip install \
            Flask \
            Flask-SQLAlchemy \
            Flask-Login \
            Flask-WTF \
            Flask-Bcrypt \
            Flask-Limiter \
            Flask-Migrate \
            python-dotenv \
            requests \
            psutil \
            cryptography
    fi
    
    echo -e "${GREEN}✅ Python packages installed successfully${NC}"
}

# Function to verify installation
verify_installation() {
    echo -e "${YELLOW}🔍 Verifying installation...${NC}"
    
    # Check Python
    if command -v python3 &> /dev/null; then
        echo -e "${GREEN}✅ Python3: $(python3 --version)${NC}"
    else
        echo -e "${RED}❌ Python3 not found${NC}"
        return 1
    fi
    
    # Check pip
    if command -v pip3 &> /dev/null; then
        echo -e "${GREEN}✅ pip3: $(pip3 --version)${NC}"
    else
        echo -e "${RED}❌ pip3 not found${NC}"
        return 1
    fi
    
    # Check virtual environment
    if [ -d "venv" ]; then
        echo -e "${GREEN}✅ Virtual environment created${NC}"
    else
        echo -e "${RED}❌ Virtual environment not created${NC}"
        return 1
    fi
    
    # Check key system libraries
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if ldconfig -p | grep -q "libldap"; then
            echo -e "${GREEN}✅ OpenLDAP libraries found${NC}"
        else
            echo -e "${YELLOW}⚠️  OpenLDAP libraries not found${NC}"
        fi
        
        if ldconfig -p | grep -q "libssl"; then
            echo -e "${GREEN}✅ OpenSSL libraries found${NC}"
        else
            echo -e "${YELLOW}⚠️  OpenSSL libraries not found${NC}"
        fi
    fi
    
    echo -e "${GREEN}✅ Installation verification complete${NC}"
}

# Main execution
main() {
    SYSTEM_TYPE=$(detect_system)
    
    echo -e "${BLUE}🖥️  Detected system: ${SYSTEM_TYPE}${NC}"
    echo ""
    
    case $SYSTEM_TYPE in
        "debian")
            install_debian_deps
            ;;
        "redhat")
            install_redhat_deps
            ;;
        "macos")
            install_macos_deps
            ;;
        "freebsd")
            install_freebsd_deps
            ;;
        *)
            echo -e "${RED}❌ Unsupported operating system: ${SYSTEM_TYPE}${NC}"
            echo "Supported systems: Ubuntu/Debian, RedHat/CentOS, macOS, FreeBSD"
            exit 1
            ;;
    esac
    
    echo ""
    echo -e "${YELLOW}🐍 Setting up Python environment...${NC}"
    install_python_packages
    
    echo ""
    echo -e "${YELLOW}🔍 Verifying installation...${NC}"
    verify_installation
    
    echo ""
    echo -e "${GREEN}🎉 All dependencies installed successfully!${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. Activate virtual environment: source venv/bin/activate"
    echo "2. Initialize database: python scripts/init_db.py"
    echo "3. Create admin user: python scripts/create_admin.py"
    echo "4. Run the application: python run.py"
    echo ""
    echo -e "${BLUE}For VM deployment:${NC}"
    echo "1. Ensure SSH access is configured"
    echo "2. Run: make deploy-vm"
}

# Run main function
main "$@"
