# VM Development Workflow

This document describes how to develop Postfix-Manager on your Mac and test it on a local Ubuntu VM.

## Overview

- **Development**: Mac (your local machine)
- **Testing**: Ubuntu VM running in VirtualBox
- **Deployment**: Automated scripts for syncing code and managing the VM

## Prerequisites

### On Mac (Development Machine)
- Git
- Python 3.8+
- rsync (`brew install rsync`)
- SSH key configured for VM access

### On Ubuntu VM (Testing Machine)
- Python 3.8+
- SSH server enabled
- Your SSH public key added to `~/.ssh/authorized_keys`

## Initial Setup

### 1. Configure VM Connection

Set environment variables for your VM:

```bash
# Add to your ~/.zshrc or ~/.bash_profile
export VM_HOST="192.168.1.100"  # Your VM's IP address
export VM_USER="ubuntu"          # Your VM username
export VM_APP_DIR="/home/ubuntu/postfix-manager"  # App directory on VM
```

### 2. First-Time Deployment

```bash
# Full deployment to VM (creates environment, installs dependencies)
make deploy-vm
```

This will:
- Create the app directory on VM
- Set up Python virtual environment
- Install dependencies
- Initialize database
- Test the application

## Daily Development Workflow

### 1. Develop on Mac

Make your code changes locally on Mac. The app will run in development mode with:
- Hot reloading enabled
- Debug mode on
- Local database

### 2. Sync to VM

```bash
# Quick sync (just code changes)
make sync-vm

# Or use the script directly
./scripts/sync_to_vm.sh
```

### 3. Test on VM

```bash
# Check VM status
make vm-status

# Start app on VM
make vm-run

# View logs
make vm-logs
```

### 4. Access VM App

Open your browser and go to: `http://YOUR_VM_IP:5000`

## Available Make Commands

```bash
# VM Operations
make deploy-vm      # Full deployment to VM
make sync-vm        # Quick code sync to VM
make vm-status      # Check VM connectivity
make vm-run         # Start app on VM
make vm-logs        # View VM logs

# Local Development
make run            # Run locally in development mode
make run-prod       # Run locally in production mode
make test           # Run tests
make lint           # Code linting
make format         # Code formatting
```

## Security Considerations

### What's Safe to Commit
- Configuration examples (`env.conf.example`)
- Development and production configs
- Scripts and documentation
- Application code

### What's NOT Safe to Commit
- `.env` files with real secrets
- Database files
- Log files
- Instance-specific configurations
- SSL certificates and keys

### Environment Variables

Create a `.env` file locally (never commit this):

```bash
# Copy the example
cp env.conf.example .env

# Edit with your actual values
nano .env
```

## Troubleshooting

### SSH Connection Issues
```bash
# Test SSH connection
ssh -o ConnectTimeout=5 $VM_USER@$VM_HOST "echo 'Connection successful'"

# Check SSH key setup
ssh-copy-id $VM_USER@$VM_HOST
```

### VM App Issues
```bash
# Check VM status
make vm-status

# View VM logs
make vm-logs

# Restart app on VM
ssh $VM_USER@$VM_HOST "cd $VM_APP_DIR && pkill -f run.py && source venv/bin/activate && python run.py &"
```

### Sync Issues
```bash
# Check rsync availability
which rsync

# Manual sync test
rsync -avz --dry-run ./ $VM_USER@$VM_HOST:$VM_APP_DIR/
```

## Performance Tips

### Fast Development Cycle
1. Use `make sync-vm` for quick code changes
2. Keep VM running between syncs
3. Use `make vm-logs` to monitor in real-time

### VM Optimization
- Allocate sufficient RAM (4GB+ recommended)
- Use SSD storage if possible
- Enable virtualization in BIOS
- Use bridged networking for better performance

## Advanced Usage

### Custom VM Configuration
```bash
# Override default settings
VM_HOST="192.168.1.101" VM_USER="admin" make deploy-vm
```

### Multiple VMs
```bash
# Deploy to different VMs
VM_HOST="192.168.1.100" make deploy-vm
VM_HOST="192.168.1.101" make deploy-vm
```

### Continuous Development
```bash
# Watch for changes and auto-sync
fswatch -o . | xargs -n1 -I{} make sync-vm
```

## File Synchronization Details

The sync scripts exclude these directories/files:
- `.git/` - Git repository
- `venv/` - Python virtual environment
- `instance/` - Instance-specific data
- `logs/` - Log files
- `.env` - Environment secrets
- `*.pyc` - Python cache files
- `__pycache__/` - Python cache directories
- `*.db` - Database files
- `backups/` - Backup files

## Best Practices

1. **Always test on VM** before committing major changes
2. **Use environment variables** for configuration
3. **Keep secrets out of version control**
4. **Regular VM backups** of important data
5. **Monitor VM resources** during development
6. **Use meaningful commit messages** for easier debugging

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify VM connectivity with `make vm-status`
3. Check VM logs with `make vm-logs`
4. Ensure all prerequisites are met
5. Verify environment variables are set correctly
