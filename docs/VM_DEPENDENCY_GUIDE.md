# VM Dependency Management Guide

This guide covers how to install and fix dependencies on your Ubuntu VM for Postfix-Manager.

## Quick Fix for python-ldap Error

If you're getting this error:
```
error: command '/usr/bin/x86_64-linux-gnu-gcc' failed with exit code 1
Failed to build wheel for python-ldap
```

### Option 1: Quick Fix (Recommended)
```bash
# On your Ubuntu VM
make vm-fix-deps
```

### Option 2: Manual Fix
```bash
# SSH into your VM
ssh root@192.168.1.15

# Install dependencies
sudo apt-get update
sudo apt-get install -y python3-dev libldap2-dev libsasl2-dev libssl-dev gcc g++ make

# Try installing again
cd /opt/postfix-manager
source venv/bin/activate
pip install python-ldap
pip install -r requirements.txt
```

## Full Dependency Installation

For a complete system setup:

```bash
# On your Ubuntu VM
make vm-deps
```

This installs:
- Python development tools
- OpenLDAP development libraries
- SSL development libraries
- Build tools (gcc, make, etc.)
- Additional system utilities

## Supported Operating Systems

The dependency scripts support:

| OS | Package Manager | Script |
|----|----------------|---------|
| Ubuntu/Debian | apt | `install_vm_dependencies.sh` |
| RedHat/CentOS | yum/dnf | `install_vm_dependencies.sh` |
| macOS | Homebrew | `install_vm_dependencies.sh` |
| FreeBSD | pkg | `install_vm_dependencies.sh` |

## Common Issues and Solutions

### 1. Permission Denied
```bash
# Make sure you have sudo access
sudo whoami
# Should return: root
```

### 2. Package Not Found
```bash
# Update package lists
sudo apt-get update  # Ubuntu/Debian
sudo yum update      # RedHat/CentOS
```

### 3. Python Version Issues
```bash
# Check Python version
python3 --version

# Should be 3.8+ for Postfix-Manager
```

### 4. Virtual Environment Issues
```bash
# Remove and recreate venv
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
```

## Verification Commands

After installation, verify everything works:

```bash
# Check Python
python3 --version

# Check pip
pip --version

# Check system libraries
ldconfig -p | grep ldap
ldconfig -p | grep ssl

# Test Python imports
python3 -c "import ldap; print('✅ LDAP works')"
python3 -c "import ssl; print('✅ SSL works')"
```

## Troubleshooting

### Still Getting python-ldap Errors?

1. **Check system libraries**:
   ```bash
   ldconfig -p | grep ldap
   ldconfig -p | grep ssl
   ```

2. **Verify Python path**:
   ```bash
   python3 -c "import sys; print(sys.path)"
   ```

3. **Check system logs**:
   ```bash
   sudo journalctl -xe
   ```

4. **Try alternative installation**:
   ```bash
   # Use pre-compiled wheel
   pip install --only-binary=all python-ldap
   ```

### Network Issues

If you can't download packages:

1. **Check internet connectivity**:
   ```bash
   ping 8.8.8.8
   ```

2. **Check DNS**:
   ```bash
   nslookup google.com
   ```

3. **Check proxy settings** (if applicable):
   ```bash
   echo $http_proxy
   echo $https_proxy
   ```

## Next Steps

After fixing dependencies:

1. **Test the application**:
   ```bash
   python -c "from app import create_app; print('✅ App works!')"
   ```

2. **Initialize database**:
   ```bash
   python scripts/init_db.py
   ```

3. **Create admin user**:
   ```bash
   python scripts/create_admin.py
   ```

4. **Run the application**:
   ```bash
   python run.py
   ```

## Support

If you continue to have issues:

1. Check the error messages carefully
2. Verify your Ubuntu version: `lsb_release -a`
3. Check available Python versions: `ls /usr/bin/python*`
4. Review system logs: `sudo journalctl -xe`
5. Check disk space: `df -h`

## Quick Reference

```bash
# Fix python-ldap issue
make vm-fix-deps

# Install all dependencies
make vm-deps

# Deploy to VM
make deploy-vm

# Sync changes
make sync-vm

# Check VM status
make vm-status
```
