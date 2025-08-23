# Postfix Manager Makefile
# Common development and deployment tasks

.PHONY: help install dev-install test lint format clean run run-prod build-package install-debian install-redhat

# Default target
help:
	@echo "Postfix Manager - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  install        Install production dependencies"
	@echo "  dev-install    Install development dependencies"
	@echo "  run            Run application in development mode"
	@echo "  run-prod       Run application in production mode"
	@echo "  test           Run tests"
	@echo "  lint           Run linting checks"
	@echo "  format         Format code with Black"
	@echo "  clean          Clean up temporary files"
	@echo "  clean-pycache  Advanced Python cache cleanup"
	@echo "  fix-permissions Fix file and directory permissions"
	@echo ""
	@echo "Installation:"
	@echo "  install-debian Install on Debian/Ubuntu systems"
	@echo "  install-redhat Install on RedHat/CentOS systems"
	@echo ""
	@echo "Packaging:"
	@echo "  build-package  Build distribution package"
	@echo ""
	@echo "Database:"
@echo "  db-init        Initialize database"
@echo "  db-migrate     Run database migrations"
@echo "  db-upgrade     Upgrade database schema"
@echo "  db-downgrade   Downgrade database schema"
@echo "  db-history     Show migration history"
@echo "  db-current     Show current revision"
@echo "  db-test        Test database connection"
@echo "  db-migrations-init Initialize migrations for current database"
	@echo ""
	@echo "VM Operations:"
	@echo "  deploy-vm      Deploy to Ubuntu VM"
	@echo "  sync-vm        Quick sync to VM"
	@echo "  vm-config      Show VM configuration"
	@echo "  vm-deps        Install VM dependencies"
	@echo "  vm-fix-deps    Fix VM dependencies (python-ldap)"
	@echo "  vm-troubleshoot Troubleshoot VM database issues"
	@echo "  vm-status      Check VM connectivity"
	@echo "  vm-run         Start app on VM"
	@echo "  vm-logs        View VM logs"

# Install production dependencies
install:
	@echo "Installing production dependencies..."
	pip install -r requirements.txt

# Install development dependencies
dev-install: install
	@echo "Installing development dependencies..."
	pip install -e .[dev]

# Run application in development mode
run:
	@echo "Starting Postfix Manager in development mode..."
	python run.py --web --port 5000

# Run application in production mode
run-prod:
	@echo "Starting Postfix Manager in production mode..."
	python run.py --web --mode production --port 5000

# Run tests
test:
	@echo "Running tests..."
	pytest

# Run tests with coverage
test-cov:
	@echo "Running tests with coverage..."
	pytest --cov=app --cov-report=html

# Run linting checks
lint:
	@echo "Running linting checks..."
	flake8 app/
	mypy app/

# Format code with Black
format:
	@echo "Formatting code with Black..."
	black app/

# Clean up temporary files
clean:
	@echo "Cleaning up temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	rm -rf build/ dist/ *.egg-info/

# Advanced cleanup and maintenance
clean-pycache:
	@echo "Cleaning Python cache and temporary files..."
	@chmod +x scripts/clean_pycache.sh
	@./scripts/clean_pycache.sh

fix-permissions:
	@echo "Fixing file and directory permissions..."
	@chmod +x scripts/fix_permissions.sh
	@./scripts/fix_permissions.sh

# Install on Debian/Ubuntu systems
install-debian:
	@echo "Installing on Debian/Ubuntu system..."
	@if [ "$$(id -u)" -ne 0 ]; then \
		echo "Error: This command must be run as root (use sudo)"; \
		exit 1; \
	fi
	@chmod +x installers/debian_install.sh
	@./installers/debian_install.sh

# Install on RedHat/CentOS systems
install-redhat:
	@echo "Installing on RedHat/CentOS system..."
	@if [ "$$(id -u)" -ne 0 ]; then \
		echo "Error: This command must be run as root (use sudo)"; \
		exit 1; \
	fi
	@chmod +x installers/redhat_install.sh
	@./installers/redhat_install.sh

# Build distribution package
build-package:
	@echo "Building distribution package..."
	python setup.py sdist bdist_wheel

# Initialize database
db-init:
	@echo "Initializing database..."
	@if [ -f "venv/bin/python" ]; then \
		venv/bin/python scripts/init_db.py; \
	else \
		python scripts/init_db.py; \
	fi

# Run database migrations
db-migrate:
	@echo "Running database migrations..."
	@if [ -f "venv/bin/flask" ]; then \
		venv/bin/flask db migrate -m "Auto-generated migration"; \
	else \
		flask db migrate -m "Auto-generated migration"; \
	fi

# Upgrade database schema
db-upgrade:
	@echo "Upgrading database schema..."
	@if [ -f "venv/bin/flask" ]; then \
		venv/bin/flask db upgrade; \
	else \
		flask db upgrade; \
	fi

# Downgrade database schema
db-downgrade:
	@echo "Downgrading database schema..."
	@if [ -f "venv/bin/flask" ]; then \
		venv/bin/flask db downgrade; \
	else \
		flask db downgrade; \
	fi

# Create admin user
create-admin:
	@echo "Creating admin user..."
	@if [ -f "venv/bin/python" ]; then \
		venv/bin/python -c "from app import create_app, db; from app.models import User, UserRole; from app.extensions import bcrypt; app = create_app(); app.app_context().push(); admin = User.query.filter_by(username='admin').first(); print('Admin user already exists' if admin else 'Admin user created successfully')"; \
	else \
		python -c "from app import create_app, db; from app.models import User, UserRole; from app.extensions import bcrypt; app = create_app(); app.app_context().push(); admin = User.query.filter_by(username='admin').first(); print('Admin user already exists' if admin else 'Admin user created successfully')"; \
	fi

# Check system requirements
check-requirements:
	@echo "Checking system requirements..."
	@echo "Python version: $$(python3 --version)"
	@echo "Pip version: $$(pip3 --version)"
	@echo "Virtual environment: $$(if [ -d "venv" ]; then echo "Found"; else echo "Not found"; fi)"
	@echo "Requirements file: $$(if [ -f "requirements.txt" ]; then echo "Found"; else echo "Not found"; fi)"

# Setup development environment
setup-dev: check-requirements
	@echo "Setting up development environment..."
	python3 -m venv venv
	venv/bin/pip install --upgrade pip
	venv/bin/pip install -r requirements.txt
	venv/bin/pip install -e .[dev]
	@echo "Development environment setup complete!"
	@echo "Activate with: source venv/bin/activate"

# Security check
security-check:
	@echo "Running security checks..."
	@if [ -f "venv/bin/safety" ]; then \
		venv/bin/safety check; \
	else \
		echo "Safety not installed. Install with: pip install safety"; \
	fi

# Docker operations
docker-build:
	@echo "Building Docker image..."
	docker build -t postfix-manager .

docker-run:
	@echo "Running Docker container..."
	docker run -p 5000:5000 postfix-manager

docker-stop:
	@echo "Stopping Docker containers..."
	docker stop $$(docker ps -q --filter ancestor=postfix-manager)

# Backup operations
backup:
	@echo "Creating backup..."
	@if [ -f "postfix_manager.db" ]; then \
		cp postfix_manager.db "postfix_manager.db.backup.$$(date +%Y%m%d_%H%M%S)"; \
		echo "Database backed up successfully"; \
	else \
		echo "No database file found to backup"; \
	fi

# Restore operations
restore:
	@echo "Restoring from backup..."
	@if [ -f "postfix_manager.db.backup.*" ]; then \
		LATEST_BACKUP=$$(ls -t postfix_manager.db.backup.* | head -1); \
		cp "$$LATEST_BACKUP" postfix_manager.db; \
		echo "Database restored from $$LATEST_BACKUP"; \
	else \
		echo "No backup files found"; \
	fi

# Show application status
status:
	@echo "Postfix Manager Status:"
	@echo "========================"
	@echo "Python: $$(python3 --version 2>/dev/null || echo 'Not found')"
	@echo "Flask: $$(python3 -c 'import flask; print(flask.__version__)' 2>/dev/null || echo 'Not found')"
	@echo "Database: $$(if [ -f "postfix_manager.db" ]; then echo "Found"; else echo "Not found"; fi)"
	@echo "Virtual Environment: $$(if [ -d "venv" ]; then echo "Active"; else echo "Not active'; fi)"
	@echo "Requirements: $$(if [ -f "requirements.txt" ]; then echo "Installed"; else echo "Not installed"; fi)"

# VM Development Operations
deploy-vm:
	@echo "Deploying to Ubuntu VM..."
	@chmod +x scripts/deploy_to_vm.sh
	@./scripts/deploy_to_vm.sh

sync-vm:
	@echo "Syncing code changes to VM..."
	@chmod +x scripts/sync_to_vm.sh
	@./scripts/sync_to_vm.sh

# VM Configuration (hardcoded for now)
VM_HOST ?= 192.168.1.15
VM_USER ?= root
VM_APP_DIR ?= /opt/postfix-manager

# Show VM configuration
vm-config:
	@echo "📋 VM Configuration:"
	@echo "VM_HOST: $(VM_HOST)"
	@echo "VM_USER: $(VM_USER)"
	@echo "VM_APP_DIR: $(VM_APP_DIR)"

# VM Dependency Management
vm-deps:
	@echo "Installing VM dependencies..."
	@chmod +x scripts/install_vm_dependencies.sh
	@./scripts/install_vm_dependencies.sh

vm-fix-deps:
	@echo "Fixing VM dependencies (python-ldap issue)..."
	@chmod +x scripts/fix_vm_dependencies.sh
	@./scripts/fix_vm_dependencies.sh

vm-troubleshoot:
	@echo "Troubleshooting VM database issues..."
	@chmod +x scripts/troubleshoot_vm_db.sh
	@./scripts/troubleshoot_vm_db.sh

vm-status:
	@echo "Checking VM status..."
	@chmod +x scripts/sync_to_vm.sh
	@./scripts/sync_to_vm.sh
	@if [ -n "$(VM_HOST)" ]; then \
		echo "VM Host: $(VM_HOST)"; \
		echo "VM User: $(VM_USER)"; \
		echo "VM App Dir: $(VM_APP_DIR)"; \
		ssh -o ConnectTimeout=5 "$(VM_USER)@$(VM_HOST)" "cd $(VM_APP_DIR) && echo 'VM accessible' && ls -la" 2>/dev/null || echo "VM not accessible"; \
	else \
		echo "VM_HOST environment variable not set"; \
		echo "Please check your .env file or run: make vm-troubleshoot"; \
	fi

vm-run:
	@echo "Starting app on VM..."
	@chmod +x scripts/sync_to_vm.sh
	@./scripts/sync_to_vm.sh
	@if [ -n "$(VM_HOST)" ]; then \
		ssh "$(VM_USER)@$(VM_HOST)" "cd $(VM_APP_DIR) && source venv/bin/activate && python run.py &"; \
		echo "App started on VM at http://$(VM_HOST):5000"; \
	else \
		echo "VM_HOST environment variable not set"; \
		echo "Please check your .env file or run: make vm-troubleshoot"; \
	fi

vm-logs:
	@echo "Showing VM logs..."
	@chmod +x scripts/sync_to_vm.sh
	@./scripts/sync_to_vm.sh
	@if [ -n "$(VM_HOST)" ]; then \
		ssh "$(VM_USER)@$(VM_HOST)" "cd $(VM_APP_DIR) && tail -f logs/postfix-manager.log"; \
	else \
		echo "VM_HOST environment variable not set"; \
		echo "Please check your .env file or run: make vm-troubleshoot"; \
	fi
