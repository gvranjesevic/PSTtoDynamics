"""
Contact Creator Module
=====================

Auto-creates missing contacts from PST email senders.
Extracts contact information from email metadata and creates proper Dynamics 365 contacts.

Author: AI Assistant
Phase: 2
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import config
import auth

class ContactCreator:
    """Creates missing contacts automatically from email sender information."""
    
    def __init__(self):
        """Initialize the contact creator."""
        self.dynamics_auth = auth.get_auth()
        self.base_url = f"{config.CRM_BASE_URL}/api/data/v9.2"
        self.logger = logging.getLogger(__name__)
        
        # Contact creation statistics
        self.stats = {
            'contacts_analyzed': 0,
            'contacts_created': 0,
            'contacts_skipped': 0,
            'contacts_failed': 0,
            'companies_created': 0
        }
    
    def analyze_missing_contacts(self, sender_list: List[str]) -> Dict:
        """
        Analyze which senders are missing from Dynamics 365.
        
        Args:
            sender_list: List of email addresses from PST
            
        Returns:
            Dict with missing contacts analysis
        """
        self.logger.info(f"🔍 Analyzing {len(sender_list)} senders for missing contacts...")
        
        # Get existing contacts from Dynamics
        existing_contacts = self._get_existing_contacts()
        existing_emails = {contact.get('emailaddress1', '').lower() for contact in existing_contacts}
        
        # Find missing contacts
        missing_contacts = []
        existing_found = []
        
        for sender in sender_list:
            sender_clean = sender.lower().strip()
            if sender_clean in existing_emails:
                existing_found.append(sender)
            else:
                missing_contacts.append(sender)
        
        analysis = {
            'total_senders': len(sender_list),
            'existing_contacts': len(existing_found),
            'missing_contacts': len(missing_contacts),
            'missing_contact_list': missing_contacts,
            'existing_contact_list': existing_found
        }
        
        self.logger.info(f"📊 Analysis complete: {len(missing_contacts)} missing, {len(existing_found)} existing")
        return analysis
    
    def create_missing_contacts(self, missing_senders: List[str], email_data_by_sender: Dict = None) -> Dict:
        """
        Create contacts for missing senders.
        
        Args:
            missing_senders: List of email addresses that need contacts
            email_data_by_sender: Optional dict with email data to extract contact info
            
        Returns:
            Dict with creation results
        """
        self.logger.info(f"🏗️ Creating {len(missing_senders)} missing contacts...")
        
        created_contacts = []
        failed_contacts = []
        
        for sender_email in missing_senders:
            try:
                self.stats['contacts_analyzed'] += 1
                
                # Extract contact information
                contact_info = self._extract_contact_info(sender_email, email_data_by_sender)
                
                # Validate contact data
                if not self._validate_contact_data(contact_info):
                    self.logger.warning(f"⚠️ Invalid contact data for {sender_email}, skipping")
                    self.stats['contacts_skipped'] += 1
                    continue
                
                # Create the contact
                contact_id = self._create_contact(contact_info)
                
                if contact_id:
                    created_contacts.append({
                        'email': sender_email,
                        'contact_id': contact_id,
                        'full_name': contact_info.get('fullname', 'Unknown')
                    })
                    self.stats['contacts_created'] += 1
                    self.logger.info(f"✅ Created contact: {contact_info.get('fullname')} ({sender_email})")
                else:
                    failed_contacts.append(sender_email)
                    self.stats['contacts_failed'] += 1
                    
            except Exception as e:
                self.logger.error(f"❌ Failed to create contact for {sender_email}: {e}")
                failed_contacts.append(sender_email)
                self.stats['contacts_failed'] += 1
        
        results = {
            'success': len(failed_contacts) == 0,
            'created_contacts': created_contacts,
            'failed_contacts': failed_contacts,
            'stats': self.stats.copy()
        }
        
        self.logger.info(f"📊 Contact creation complete: {len(created_contacts)} created, {len(failed_contacts)} failed")
        return results
    
    def _extract_contact_info(self, email_address: str, email_data_by_sender: Dict = None) -> Dict:
        """
        Extract contact information from email address and optional email data.
        
        Args:
            email_address: Email address to create contact for
            email_data_by_sender: Optional email data to extract additional info
            
        Returns:
            Dict with contact information
        """
        # Start with basic info from email address
        contact_info = {
            'emailaddress1': email_address.strip(),
            'fullname': self._extract_name_from_email(email_address),
            'firstname': '',
            'lastname': '',
            'jobtitle': '',
            'telephone1': '',
            'companyname': self._extract_company_from_email(email_address)
        }
        
        # Try to extract additional info from email data if available
        if email_data_by_sender and email_address in email_data_by_sender:
            sender_emails = email_data_by_sender[email_address]
            if sender_emails:
                # Use the first email to extract sender display name
                first_email = sender_emails[0]
                display_name = first_email.get('sender_name', '')
                
                if display_name and display_name != email_address:
                    contact_info['fullname'] = display_name
                    # Try to split into first/last name
                    name_parts = self._split_full_name(display_name)
                    contact_info.update(name_parts)
        
        # If no good full name found, generate from email
        if not contact_info['fullname'] or contact_info['fullname'] == email_address:
            contact_info['fullname'] = self._extract_name_from_email(email_address)
            name_parts = self._split_full_name(contact_info['fullname'])
            contact_info.update(name_parts)
        
        return contact_info
    
    def _extract_name_from_email(self, email_address: str) -> str:
        """Extract a reasonable name from an email address."""
        # Get the part before @
        local_part = email_address.split('@')[0]
        
        # Handle common patterns
        if '.' in local_part:
            # firstname.lastname@domain.com
            parts = local_part.split('.')
            name = ' '.join(part.title() for part in parts)
        elif '_' in local_part:
            # first_last@domain.com
            parts = local_part.split('_')
            name = ' '.join(part.title() for part in parts)
        else:
            # Single name or complex pattern
            name = local_part.title()
        
        # Clean up common service names
        service_patterns = ['service', 'noreply', 'no-reply', 'notify', 'support', 'admin']
        for pattern in service_patterns:
            if pattern in name.lower():
                # For service emails, use the domain name
                domain = email_address.split('@')[1].split('.')[0]
                return f"{domain.title()} Service"
        
        return name
    
    def _extract_company_from_email(self, email_address: str) -> str:
        """Extract company name from email domain."""
        try:
            domain = email_address.split('@')[1]
            company_part = domain.split('.')[0]
            
            # Clean up and format company name
            company_name = company_part.replace('-', ' ').replace('_', ' ').title()
            
            # Special handling for known domains
            if 'ringcentral' in company_part.lower():
                return 'RingCentral'
            elif 'protective' in company_part.lower():
                return 'Protective Insurance'
            elif 'dynamique' in company_part.lower():
                return 'Dynamique'
            
            return company_name
            
        except (Exception, AttributeError, TypeError, ValueError):
            return ''
    
    def _split_full_name(self, full_name: str) -> Dict:
        """Split full name into first and last name."""
        parts = full_name.strip().split()
        
        if len(parts) == 0:
            return {'firstname': '', 'lastname': ''}
        elif len(parts) == 1:
            return {'firstname': parts[0], 'lastname': ''}
        elif len(parts) == 2:
            return {'firstname': parts[0], 'lastname': parts[1]}
        else:
            # More than 2 parts, first word is firstname, rest is lastname
            return {'firstname': parts[0], 'lastname': ' '.join(parts[1:])}
    
    def _validate_contact_data(self, contact_info: Dict) -> bool:
        """Validate that contact data is sufficient for creation."""
        # Must have email address
        if not contact_info.get('emailaddress1'):
            return False
        
        # Must have some kind of name
        if not contact_info.get('fullname'):
            return False
        
        # Email must be valid format
        email = contact_info['emailaddress1']
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return False
        
        return True
    
    def _create_contact(self, contact_info: Dict) -> Optional[str]:
        """
        Create a single contact in Dynamics 365.
        
        Args:
            contact_info: Dict with contact information
            
        Returns:
            Contact ID if successful, None if failed
        """
        try:
            # Prepare contact data for Dynamics
            contact_data = {
                'emailaddress1': contact_info['emailaddress1'],
                'fullname': contact_info['fullname'][:100],  # Limit length
            }
            
            # Add optional fields if available
            if contact_info.get('firstname'):
                contact_data['firstname'] = contact_info['firstname'][:50]
            if contact_info.get('lastname'):
                contact_data['lastname'] = contact_info['lastname'][:50]
            if contact_info.get('companyname'):
                contact_data['companyname'] = contact_info['companyname'][:100]
            
            # Create the contact
            headers = self.dynamics_auth.get_headers()
            if not headers:
                self.logger.error("❌ Failed to get authentication headers")
                return None
            
            import requests
            response = requests.post(
                f"{self.base_url}/contacts",
                json=contact_data,
                headers=headers
            )
            
            if response.status_code in [200, 201]:
                contact_result = response.json()
                return contact_result.get('contactid')
            else:
                self.logger.error(f"❌ Failed to create contact: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Exception creating contact: {e}")
            return None
    
    def _get_existing_contacts(self) -> List[Dict]:
        """Get all existing contacts from Dynamics 365."""
        try:
            headers = self.dynamics_auth.get_headers()
            if not headers:
                self.logger.error("❌ Failed to get authentication headers")
                return []
            
            import requests
            response = requests.get(
                f"{self.base_url}/contacts?$select=contactid,emailaddress1,fullname",
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json().get('value', [])
            else:
                self.logger.error(f"❌ Failed to retrieve contacts: {response.status_code}")
                return []
                
        except Exception as e:
            self.logger.error(f"❌ Exception retrieving contacts: {e}")
            return []
    
    def get_creation_stats(self) -> Dict:
        """Get contact creation statistics."""
        return self.stats.copy()
    
    def reset_stats(self):
        """Reset creation statistics."""
        self.stats = {
            'contacts_analyzed': 0,
            'contacts_created': 0,
            'contacts_skipped': 0,
            'contacts_failed': 0,
            'companies_created': 0
        } 