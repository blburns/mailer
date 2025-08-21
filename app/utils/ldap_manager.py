"""
LDAP Management Utility
"""

import os
import subprocess
import logging
from typing import Dict, List, Optional
from ldap3 import Server, Connection, ALL, SUBTREE, MODIFY_REPLACE

logger = logging.getLogger(__name__)


class LDAPManager:
    """Manages OpenLDAP server configuration and operations."""
    
    def __init__(self, server_uri: str = "ldap://127.0.0.1", 
                 admin_dn: str = "cn=admin,dc=example,dc=tld",
                 admin_password: str = ""):
        self.server_uri = server_uri
        self.admin_dn = admin_dn
        self.admin_password = admin_password
        self.server = Server(server_uri, get_info=ALL)
    
    @staticmethod
    def get_status() -> Dict:
        """Get OpenLDAP service status."""
        try:
            result = subprocess.run(['systemctl', 'is-active', 'slapd'], 
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
            logger.error(f"Error getting LDAP status: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def restart_service(self) -> bool:
        """Restart OpenLDAP service."""
        try:
            result = subprocess.run(['systemctl', 'restart', 'slapd'], 
                                  capture_output=True, text=True, timeout=30)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error restarting LDAP: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test LDAP connection."""
        try:
            with Connection(self.server, self.admin_dn, self.admin_password) as conn:
                return conn.bind()
        except Exception as e:
            logger.error(f"Error testing LDAP connection: {e}")
            return False
    
    def search(self, base_dn: str, search_filter: str = "(objectClass=*)", 
               attributes: List[str] = None) -> List[Dict]:
        """Search LDAP directory."""
        try:
            with Connection(self.server, self.admin_dn, self.admin_password) as conn:
                if not conn.bind():
                    logger.error("Failed to bind to LDAP")
                    return []
                
                conn.search(base_dn, search_filter, SUBTREE, attributes=attributes or ['*'])
                results = []
                
                for entry in conn.entries:
                    result = {}
                    for attr in entry.entry_attributes:
                        values = entry[attr].values
                        if len(values) == 1:
                            result[attr] = values[0]
                        else:
                            result[attr] = values
                    results.append(result)
                
                return results
        except Exception as e:
            logger.error(f"Error searching LDAP: {e}")
            return []
    
    def add_entry(self, dn: str, attributes: Dict) -> bool:
        """Add a new LDAP entry."""
        try:
            with Connection(self.server, self.admin_dn, self.admin_password) as conn:
                if not conn.bind():
                    logger.error("Failed to bind to LDAP")
                    return False
                
                # Convert attributes to LDAP format
                ldap_attributes = {}
                for key, value in attributes.items():
                    if isinstance(value, list):
                        ldap_attributes[key] = value
                    else:
                        ldap_attributes[key] = [value]
                
                return conn.add(dn, ldap_attributes)
        except Exception as e:
            logger.error(f"Error adding LDAP entry: {e}")
            return False
    
    def modify_entry(self, dn: str, changes: Dict) -> bool:
        """Modify an existing LDAP entry."""
        try:
            with Connection(self.server, self.admin_dn, self.admin_password) as conn:
                if not conn.bind():
                    logger.error("Failed to bind to LDAP")
                    return False
                
                # Convert changes to LDAP format
                ldap_changes = []
                for key, value in changes.items():
                    if isinstance(value, list):
                        ldap_changes.append(MODIFY_REPLACE(key, value))
                    else:
                        ldap_changes.append(MODIFY_REPLACE(key, [value]))
                
                return conn.modify(dn, ldap_changes)
        except Exception as e:
            logger.error(f"Error modifying LDAP entry: {e}")
            return False
    
    def delete_entry(self, dn: str) -> bool:
        """Delete an LDAP entry."""
        try:
            with Connection(self.server, self.admin_dn, self.admin_password) as conn:
                if not conn.bind():
                    logger.error("Failed to bind to LDAP")
                    return False
                
                return conn.delete(dn)
        except Exception as e:
            logger.error(f"Error deleting LDAP entry: {e}")
            return False
    
    def create_mail_domain(self, domain: str, base_dn: str = None) -> bool:
        """Create LDAP structure for a mail domain."""
        try:
            if not base_dn:
                base_dn = f"dc={domain.split('.')[0]},dc={domain.split('.')[1]}"
            
            # Create domain entry
            domain_attrs = {
                'objectClass': ['dcObject', 'organization'],
                'dc': domain.split('.')[0],
                'o': domain
            }
            
            if not self.add_entry(base_dn, domain_attrs):
                return False
            
            # Create hosting organization
            hosting_dn = f"o=hosting,{base_dn}"
            hosting_attrs = {
                'objectClass': ['organization', 'top'],
                'o': 'hosting',
                'description': 'Hosting Organization'
            }
            
            if not self.add_entry(hosting_dn, hosting_attrs):
                return False
            
            # Create mail server entry
            mailserver_dn = f"ou=MailServer,{hosting_dn}"
            mailserver_attrs = {
                'objectClass': ['organizationalUnit', 'top'],
                'ou': 'MailServer'
            }
            
            if not self.add_entry(mailserver_dn, mailserver_attrs):
                return False
            
            # Create mail domains entry
            maildomains_dn = f"ou=MailDomains,{mailserver_dn}"
            maildomains_attrs = {
                'objectClass': ['organizationalUnit', 'top'],
                'ou': 'MailDomains'
            }
            
            if not self.add_entry(maildomains_dn, maildomains_attrs):
                return False
            
            # Create domain entry
            domain_entry_dn = f"vd={domain},{maildomains_dn}"
            domain_entry_attrs = {
                'objectClass': ['top', 'VirtualMailDomain'],
                'vd': domain,
                'description': f'Virtual mail domain: {domain}'
            }
            
            if not self.add_entry(domain_entry_dn, domain_entry_attrs):
                return False
            
            # Create mailboxes entry
            mailboxes_dn = f"ou=Mailboxes,{domain_entry_dn}"
            mailboxes_attrs = {
                'objectClass': ['organizationalUnit', 'top'],
                'ou': 'Mailboxes'
            }
            
            return self.add_entry(mailboxes_dn, mailboxes_attrs)
            
        except Exception as e:
            logger.error(f"Error creating mail domain {domain}: {e}")
            return False
    
    def create_mail_user(self, username: str, domain: str, password: str, 
                        base_dn: str = None) -> bool:
        """Create LDAP entry for a mail user."""
        try:
            if not base_dn:
                base_dn = f"dc={domain.split('.')[0]},dc={domain.split('.')[1]}"
            
            # Find the mailboxes DN
            mailboxes_dn = f"ou=Mailboxes,vd={domain},ou=MailDomains,ou=MailServer,o=hosting,{base_dn}"
            
            # Create user entry
            user_dn = f"mail={username},{mailboxes_dn}"
            user_attrs = {
                'objectClass': ['top', 'VirtualMailAccount', 'posixAccount'],
                'mail': username,
                'uid': username,
                'uidNumber': '1000',
                'gidNumber': '1000',
                'homeDirectory': f"/home/vmail/domains/{domain}/{username}",
                'userPassword': password,
                'cn': username,
                'sn': username,
                'mailbox': f"/home/vmail/domains/{domain}/{username}/Maildir/"
            }
            
            return self.add_entry(user_dn, user_attrs)
            
        except Exception as e:
            logger.error(f"Error creating mail user {username}@{domain}: {e}")
            return False
    
    def delete_mail_user(self, username: str, domain: str, base_dn: str = None) -> bool:
        """Delete LDAP entry for a mail user."""
        try:
            if not base_dn:
                base_dn = f"dc={domain.split('.')[0]},dc={domain.split('.')[1]}"
            
            user_dn = f"mail={username},ou=Mailboxes,vd={domain},ou=MailDomains,ou=MailServer,o=hosting,{base_dn}"
            return self.delete_entry(user_dn)
            
        except Exception as e:
            logger.error(f"Error deleting mail user {username}@{domain}: {e}")
            return False
    
    def get_mail_users(self, domain: str, base_dn: str = None) -> List[Dict]:
        """Get all mail users for a domain."""
        try:
            if not base_dn:
                base_dn = f"dc={domain.split('.')[0]},dc={domain.split('.')[1]}"
            
            mailboxes_dn = f"ou=Mailboxes,vd={domain},ou=MailDomains,ou=MailServer,o=hosting,{base_dn}"
            search_filter = "(objectClass=VirtualMailAccount)"
            
            return self.search(mailboxes_dn, search_filter, ['mail', 'cn', 'uidNumber', 'homeDirectory'])
            
        except Exception as e:
            logger.error(f"Error getting mail users for {domain}: {e}")
            return []
    
    def backup_database(self, backup_path: str) -> bool:
        """Backup LDAP database."""
        try:
            result = subprocess.run(['slapcat', '-n', '0', '-l', backup_path], 
                                  capture_output=True, text=True, timeout=300)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error backing up LDAP database: {e}")
            return False
    
    def restore_database(self, backup_path: str) -> bool:
        """Restore LDAP database from backup."""
        try:
            # Stop slapd
            subprocess.run(['systemctl', 'stop', 'slapd'], 
                          capture_output=True, text=True, timeout=30)
            
            # Restore database
            result = subprocess.run(['slapadd', '-n', '0', '-l', backup_path], 
                                  capture_output=True, text=True, timeout=300)
            
            # Start slapd
            subprocess.run(['systemctl', 'start', 'slapd'], 
                          capture_output=True, text=True, timeout=30)
            
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error restoring LDAP database: {e}")
            # Try to start slapd anyway
            subprocess.run(['systemctl', 'start', 'slapd'], 
                          capture_output=True, text=True, timeout=30)
            return False
