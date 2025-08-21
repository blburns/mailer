"""
Postfix and Dovecot Management Utility
"""

import os
import subprocess
import shutil
import re
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class PostfixManager:
    """Manages Postfix mail server configuration and operations."""
    
    def __init__(self, config_dir: str = "/etc/postfix"):
        self.config_dir = config_dir
        self.main_cf = os.path.join(config_dir, "main.cf")
        self.master_cf = os.path.join(config_dir, "master.cf")
    
    @staticmethod
    def get_status() -> Dict:
        """Get Postfix service status."""
        try:
            result = subprocess.run(['systemctl', 'is-active', 'postfix'], 
                                  capture_output=True, text=True, timeout=10)
            status = result.stdout.strip()
            
            if status == 'active':
                # Get additional info
                try:
                    queue_info = subprocess.run(['postqueue', '-p'], 
                                              capture_output=True, text=True, timeout=10)
                    queue_count = len([line for line in queue_info.stdout.split('\n') 
                                     if line.startswith('Mail queue is empty') == False and line.strip()])
                except:
                    queue_count = 0
                
                return {
                    'status': 'running',
                    'service': 'active',
                    'queue_count': max(0, queue_count - 1)  # Subtract header line
                }
            else:
                return {
                    'status': 'stopped',
                    'service': status,
                    'queue_count': 0
                }
        except Exception as e:
            logger.error(f"Error getting Postfix status: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    @staticmethod
    def get_dovecot_status() -> Dict:
        """Get Dovecot service status."""
        try:
            result = subprocess.run(['systemctl', 'is-active', 'dovecot'], 
                                  capture_output=True, text=True, timeout=10)
            status = result.stdout.strip()
            
            if status == 'active':
                return {
                    'status': 'running',
                    'service': 'active'
                }
            else:
                return {
                    'status': 'stopped',
                    'service': status
                }
        except Exception as e:
            logger.error(f"Error getting Dovecot status: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def restart_service(self) -> bool:
        """Restart Postfix service."""
        try:
            result = subprocess.run(['systemctl', 'restart', 'postfix'], 
                                  capture_output=True, text=True, timeout=30)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error restarting Postfix: {e}")
            return False
    
    def reload_config(self) -> bool:
        """Reload Postfix configuration."""
        try:
            result = subprocess.run(['postfix', 'reload'], 
                                  capture_output=True, text=True, timeout=30)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error reloading Postfix config: {e}")
            return False
    
    def check_config(self) -> Dict:
        """Check Postfix configuration syntax."""
        try:
            result = subprocess.run(['postfix', 'check'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return {'valid': True, 'message': 'Configuration is valid'}
            else:
                return {'valid': False, 'message': result.stderr}
        except Exception as e:
            logger.error(f"Error checking Postfix config: {e}")
            return {'valid': False, 'message': str(e)}
    
    def get_queue_info(self) -> Dict:
        """Get mail queue information."""
        try:
            result = subprocess.run(['postqueue', '-p'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                queue_count = len([line for line in lines 
                                 if line.startswith('Mail queue is empty') == False and line.strip()])
                
                return {
                    'count': max(0, queue_count - 1),
                    'details': result.stdout
                }
            else:
                return {'count': 0, 'details': result.stderr}
        except Exception as e:
            logger.error(f"Error getting queue info: {e}")
            return {'count': 0, 'details': str(e)}
    
    def flush_queue(self) -> bool:
        """Flush the mail queue."""
        try:
            result = subprocess.run(['postqueue', '-f'], 
                                  capture_output=True, text=True, timeout=60)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error flushing queue: {e}")
            return False
    
    def add_domain(self, domain: str) -> bool:
        """Add a domain to Postfix virtual domains."""
        try:
            # Read current virtual domains
            virtual_domains_file = os.path.join(self.config_dir, "virtual_domains")
            
            if os.path.exists(virtual_domains_file):
                with open(virtual_domains_file, 'r') as f:
                    domains = f.read().splitlines()
            else:
                domains = []
            
            # Add domain if not exists
            if domain not in domains:
                domains.append(domain)
                
                with open(virtual_domains_file, 'w') as f:
                    f.write('\n'.join(domains))
                
                # Update main.cf if needed
                self._update_main_cf_virtual_domains()
                
                # Reload configuration
                return self.reload_config()
            
            return True
        except Exception as e:
            logger.error(f"Error adding domain {domain}: {e}")
            return False
    
    def remove_domain(self, domain: str) -> bool:
        """Remove a domain from Postfix virtual domains."""
        try:
            virtual_domains_file = os.path.join(self.config_dir, "virtual_domains")
            
            if os.path.exists(virtual_domains_file):
                with open(virtual_domains_file, 'r') as f:
                    domains = f.read().splitlines()
                
                # Remove domain
                if domain in domains:
                    domains.remove(domain)
                    
                    with open(virtual_domains_file, 'w') as f:
                        f.write('\n'.join(domains))
                    
                    # Update main.cf if needed
                    self._update_main_cf_virtual_domains()
                    
                    # Reload configuration
                    return self.reload_config()
            
            return True
        except Exception as e:
            logger.error(f"Error removing domain {domain}: {e}")
            return False
    
    def _update_main_cf_virtual_domains(self):
        """Update main.cf to include virtual_domains file."""
        try:
            with open(self.main_cf, 'r') as f:
                content = f.read()
            
            # Check if virtual_domains is already included
            if 'virtual_domains' not in content:
                with open(self.main_cf, 'a') as f:
                    f.write('\n# Virtual domains\n')
                    f.write('virtual_domains = hash:/etc/postfix/virtual_domains\n')
                
                # Update hash table
                subprocess.run(['postmap', os.path.join(self.config_dir, "virtual_domains")], 
                             capture_output=True, timeout=30)
        except Exception as e:
            logger.error(f"Error updating main.cf: {e}")


class DovecotManager:
    """Manages Dovecot IMAP/POP3 server configuration and operations."""
    
    def __init__(self, config_dir: str = "/etc/dovecot"):
        self.config_dir = config_dir
        self.conf_d = os.path.join(config_dir, "conf.d")
    
    def restart_service(self) -> bool:
        """Restart Dovecot service."""
        try:
            result = subprocess.run(['systemctl', 'restart', 'dovecot'], 
                                  capture_output=True, text=True, timeout=30)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error restarting Dovecot: {e}")
            return False
    
    def reload_config(self) -> bool:
        """Reload Dovecot configuration."""
        try:
            result = subprocess.run(['systemctl', 'reload', 'dovecot'], 
                                  capture_output=True, text=True, timeout=30)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error reloading Dovecot config: {e}")
            return False
    
    def check_config(self) -> Dict:
        """Check Dovecot configuration syntax."""
        try:
            result = subprocess.run(['dovecot', '--config', self.config_dir], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return {'valid': True, 'message': 'Configuration is valid'}
            else:
                return {'valid': False, 'message': result.stderr}
        except Exception as e:
            logger.error(f"Error checking Dovecot config: {e}")
            return {'valid': False, 'message': str(e)}
    
    def get_user_info(self, username: str, domain: str) -> Dict:
        """Get user information from Dovecot."""
        try:
            # This would typically query the user database
            # For now, return basic info
            return {
                'username': username,
                'domain': domain,
                'home_dir': f"/home/vmail/domains/{domain}/{username}",
                'quota': self._get_user_quota(username, domain)
            }
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            return {}
    
    def _get_user_quota(self, username: str, domain: str) -> int:
        """Get user quota from Dovecot."""
        try:
            quota_file = f"/home/vmail/domains/{domain}/{username}/dovecot-quota"
            if os.path.exists(quota_file):
                with open(quota_file, 'r') as f:
                    return int(f.read().strip())
            return 0
        except:
            return 0
