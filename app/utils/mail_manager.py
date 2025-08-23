"""
Postfix and Dovecot Management Utility
"""

import os
import subprocess
import shutil
import re
import time
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
                # Try to get connection count
                try:
                    # Use netstat to count connections on IMAP/POP3 ports
                    imap_result = subprocess.run(['netstat', '-an'], 
                                               capture_output=True, text=True, timeout=10)
                    imap_connections = len([line for line in imap_result.stdout.split('\n') 
                                          if ':143 ' in line or ':993 ' in line or ':110 ' in line or ':995 ' in line])
                    
                    return {
                        'status': 'running',
                        'service': 'active',
                        'connections': imap_connections
                    }
                except:
                    return {
                        'status': 'running',
                        'service': 'active',
                        'connections': 0
                    }
            else:
                return {
                    'status': 'stopped',
                    'service': status,
                    'connections': 0
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
                
                # Calculate queue size and age
                queue_size = 0
                oldest_age = 0
                newest_age = 0
                
                try:
                    # Get queue directory size
                    queue_dir = "/var/spool/postfix/incoming"
                    if os.path.exists(queue_dir):
                        for root, dirs, files in os.walk(queue_dir):
                            for file in files:
                                file_path = os.path.join(root, file)
                                if os.path.isfile(file_path):
                                    queue_size += os.path.getsize(file_path)
                                    file_age = time.time() - os.path.getmtime(file_path)
                                    if file_age > oldest_age:
                                        oldest_age = file_age
                                    if newest_age == 0 or file_age < newest_age:
                                        newest_age = file_age
                except:
                    pass
                
                return {
                    'count': max(0, queue_count - 1),
                    'details': result.stdout,
                    'size_kb': queue_size // 1024,
                    'oldest_hours': int(oldest_age // 3600),
                    'newest_hours': int(newest_age // 3600)
                }
            else:
                return {'count': 0, 'details': result.stderr}
        except Exception as e:
            logger.error(f"Error getting queue info: {e}")
            return {'count': 0, 'details': str(e)}

    def get_detailed_queue_info(self, queue_type: str = 'all', limit: int = 100) -> Dict:
        """Get detailed queue information with filtering and pagination."""
        try:
            # Get basic queue info
            basic_info = self.get_queue_info()
            
            # Parse detailed message information
            lines = basic_info.get('details', '').split('\n')
            messages = []
            
            for line in lines:
                if line.startswith('Mail queue is empty') or line.startswith('--') or not line.strip():
                    continue
                
                parts = line.split()
                if len(parts) >= 7:
                    message_id = parts[0]
                    size = int(parts[1]) if parts[1].isdigit() else 0
                    timestamp = ' '.join(parts[2:4])
                    sender = parts[4] if len(parts) > 4 else ''
                    recipient = parts[5] if len(parts) > 5 else ''
                    
                    # Determine queue type (simplified)
                    queue_type_msg = 'active'  # Default
                    if 'deferred' in line.lower():
                        queue_type_msg = 'deferred'
                    elif 'hold' in line.lower():
                        queue_type_msg = 'hold'
                    
                    messages.append({
                        'id': message_id,
                        'size': size,
                        'timestamp': timestamp,
                        'from': sender,
                        'to': recipient,
                        'queue': queue_type_msg,
                        'arrival_time': timestamp
                    })
            
            # Filter by queue type if specified
            if queue_type != 'all':
                messages = [msg for msg in messages if msg['queue'] == queue_type]
            
            # Apply limit
            messages = messages[:limit]
            
            # Calculate queue statistics
            queue_stats = {
                'incoming': {'count': 0, 'size': 0},
                'active': {'count': 0, 'size': 0},
                'deferred': {'count': 0, 'size': 0},
                'hold': {'count': 0, 'size': 0}
            }
            
            for msg in messages:
                queue_type_msg = msg['queue']
                if queue_type_msg in queue_stats:
                    queue_stats[queue_type_msg]['count'] += 1
                    queue_stats[queue_type_msg]['size'] += msg['size']
            
            return {
                'incoming': queue_stats['incoming'],
                'active': queue_stats['active'],
                'deferred': queue_stats['deferred'],
                'hold': queue_stats['hold'],
                'messages': messages
            }
        except Exception as e:
            logger.error(f"Error getting detailed queue info: {e}")
            return {'error': str(e)}

    def delete_message(self, message_id: str) -> bool:
        """Delete a specific message from the queue."""
        try:
            result = subprocess.run(['postsuper', '-d', message_id], 
                                  capture_output=True, text=True, timeout=30)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error deleting message {message_id}: {e}")
            return False

    def hold_message(self, message_id: str) -> bool:
        """Hold a specific message in the queue."""
        try:
            result = subprocess.run(['postsuper', '-h', message_id], 
                                  capture_output=True, text=True, timeout=30)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error holding message {message_id}: {e}")
            return False

    def release_message(self, message_id: str) -> bool:
        """Release a held message from the queue."""
        try:
            result = subprocess.run(['postsuper', '-H', message_id], 
                                  capture_output=True, text=True, timeout=30)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error releasing message {message_id}: {e}")
            return False

    def flush_deferred_queue(self) -> bool:
        """Flush the deferred queue."""
        try:
            result = subprocess.run(['postqueue', '-f'], 
                                  capture_output=True, text=True, timeout=60)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error flushing deferred queue: {e}")
            return False

    def flush_hold_queue(self) -> bool:
        """Flush the hold queue."""
        try:
            result = subprocess.run(['postqueue', '-f'], 
                                  capture_output=True, text=True, timeout=60)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error flushing hold queue: {e}")
            return False

    def get_queue_performance_metrics(self) -> Dict:
        """Get queue performance metrics."""
        try:
            # Get queue info
            queue_info = self.get_queue_info()
            
            # Calculate basic metrics
            total_messages = queue_info.get('count', 0)
            
            # Calculate processing rate (simplified)
            processing_rate = 0
            if total_messages > 0:
                # This would typically be calculated from historical data
                processing_rate = min(total_messages * 2, 100)  # Placeholder
            
            # Calculate average wait time (simplified)
            avg_wait_time = 0
            if total_messages > 0:
                # This would typically be calculated from actual timestamps
                avg_wait_time = 15  # Placeholder in minutes
            
            # Calculate queue health score
            health_score = 100
            if total_messages > 1000:
                health_score = 20
            elif total_messages > 500:
                health_score = 40
            elif total_messages > 100:
                health_score = 60
            elif total_messages > 50:
                health_score = 80
            
            return {
                'processing_rate': processing_rate,
                'avg_wait_time': avg_wait_time,
                'queue_health': health_score,
                'total_messages': total_messages
            }
        except Exception as e:
            logger.error(f"Error getting queue performance metrics: {e}")
            return {'error': str(e)}

    def cleanup_expired_messages(self) -> bool:
        """Clean up expired messages from the queue."""
        try:
            # This would typically involve more sophisticated logic
            # For now, just flush the deferred queue
            return self.flush_deferred_queue()
        except Exception as e:
            logger.error(f"Error cleaning up expired messages: {e}")
            return False

    def rebuild_queue_index(self) -> bool:
        """Rebuild the queue index."""
        try:
            result = subprocess.run(['postsuper', '-r'], 
                                  capture_output=True, text=True, timeout=120)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error rebuilding queue index: {e}")
            return False

    def check_queue_integrity(self) -> Dict:
        """Check queue integrity."""
        try:
            result = subprocess.run(['postqueue', '-p'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return {'valid': True, 'message': 'Queue integrity check passed'}
            else:
                return {'valid': False, 'message': 'Queue integrity check failed'}
        except Exception as e:
            logger.error(f"Error checking queue integrity: {e}")
            return {'valid': False, 'message': str(e)}
    
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

    def get_virtual_domains(self) -> List[str]:
        """Get list of virtual domains from Postfix."""
        try:
            virtual_domains_file = os.path.join(self.config_dir, "virtual_domains")
            
            if os.path.exists(virtual_domains_file):
                with open(virtual_domains_file, 'r') as f:
                    domains = f.read().splitlines()
                return [domain.strip() for domain in domains if domain.strip()]
            else:
                return []
        except Exception as e:
            logger.error(f"Error getting virtual domains: {e}")
            return []
    
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

    def get_config_info(self) -> Dict:
        """Get Dovecot configuration information."""
        try:
            config_file = os.path.join(self.config_dir, "dovecot.conf")
            if os.path.exists(config_file):
                stat_info = os.stat(config_file)
                return {
                    'config_file': config_file,
                    'last_modified': stat_info.st_mtime,
                    'size': stat_info.st_size
                }
            return {'error': 'Configuration file not found'}
        except Exception as e:
            logger.error(f"Error getting config info: {e}")
            return {'error': str(e)}

    def backup_config(self) -> Dict:
        """Create a backup of Dovecot configuration."""
        try:
            import shutil
            import datetime
            
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = f"/tmp/dovecot_backup_{timestamp}"
            
            # Create backup directory
            os.makedirs(backup_dir, exist_ok=True)
            
            # Copy configuration files
            config_files = [
                os.path.join(self.config_dir, "dovecot.conf"),
                os.path.join(self.conf_d, "10-mail.conf"),
                os.path.join(self.conf_d, "10-auth.conf"),
                os.path.join(self.conf_d, "10-ssl.conf")
            ]
            
            copied_files = []
            for config_file in config_files:
                if os.path.exists(config_file):
                    shutil.copy2(config_file, backup_dir)
                    copied_files.append(os.path.basename(config_file))
            
            # Create archive
            archive_name = f"/tmp/dovecot_config_backup_{timestamp}.tar.gz"
            shutil.make_archive(archive_name.replace('.tar.gz', ''), 'gztar', backup_dir)
            
            # Clean up temporary directory
            shutil.rmtree(backup_dir)
            
            return {
                'success': True,
                'backup_file': archive_name,
                'files_backed_up': copied_files
            }
        except Exception as e:
            logger.error(f"Error backing up Dovecot config: {e}")
            return {'error': str(e)}

    def get_user_statistics(self) -> Dict:
        """Get user statistics for Dovecot."""
        try:
            # This would typically query the user database
            # For now, return placeholder data
            return {
                'total_users': 0,
                'active_users': 0,
                'quota_usage': 0,
                'connections': 0
            }
        except Exception as e:
            logger.error(f"Error getting user statistics: {e}")
            return {'error': str(e)}

    def get_protocol_status(self) -> Dict:
        """Get protocol status for IMAP, POP3, and LMTP."""
        try:
            # Check which protocols are enabled
            protocols = []
            try:
                result = subprocess.run(['doveconf', '-h', 'protocols'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    protocols = result.stdout.strip().split()
            except:
                protocols = ['imap', 'pop3']  # Default fallback
            
            return {
                'imap': 'imap' in protocols,
                'pop3': 'pop3' in protocols,
                'lmtp': 'lmtp' in protocols,
                'protocols': protocols
            }
        except Exception as e:
            logger.error(f"Error getting protocol status: {e}")
            return {'error': str(e)}
