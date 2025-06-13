"""
Dynamics 365 Data Access Module
==============================

Handles data retrieval from and operations to Dynamics 365.
"""

import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import config
import auth


class DynamicsData:
    """Handles data operations with Dynamics 365."""
    
    def __init__(self):
        self.auth = auth.get_auth()
    
    def _get_headers(self) -> Optional[Dict[str, str]]:
        """Get authentication headers."""
        return self.auth.get_headers()
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Optional[Dict]:
        """
        Makes an authenticated request to Dynamics 365.
        
        Args:
            method: HTTP method (GET, POST, PATCH, etc.)
            endpoint: API endpoint (relative to base URL)
            data: Request body data
            params: Query parameters
            
        Returns:
            Response data or None if failed
        """
        headers = self._get_headers()
        if not headers:
            print("❌ Authentication failed")
            return None
        
        url = f"{config.CRM_BASE_URL}/{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=30)
            elif method.upper() == 'PATCH':
                response = requests.patch(url, headers=headers, json=data, timeout=30)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                print(f"❌ Unsupported HTTP method: {method}")
                return None
            
            # Handle successful responses
            if response.status_code in [200, 201, 204]:
                if response.status_code == 204:  # No content
                    return {"success": True}
                try:
                    return response.json()
                except (Exception, AttributeError, TypeError, ValueError):
                    return {"success": True, "status_code": response.status_code}
            else:
                print(f"❌ Request failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Request error: {e}")
            return None
    
    def get_contacts(self, email_filter: str = None) -> List[Dict]:
        """
        Retrieves contacts from Dynamics 365.
        
        Args:
            email_filter: Optional email address to filter by
            
        Returns:
            List of contact dictionaries
        """
        print("👥 Retrieving contacts from Dynamics 365...")
        
        params = {
            '$select': 'contactid,fullname,emailaddress1,emailaddress2,emailaddress3'
        }
        
        if email_filter:
            # Filter for specific email address
            params['$filter'] = f"emailaddress1 eq '{email_filter}' or emailaddress2 eq '{email_filter}' or emailaddress3 eq '{email_filter}'"
        
        result = self._make_request('GET', 'contacts', params=params)
        
        if result and 'value' in result:
            contacts = result['value']
            print(f"   ✅ Found {len(contacts)} contacts")
            return contacts
        else:
            print("   ❌ Failed to retrieve contacts")
            return []
    
    def get_contact_by_email(self, email: str) -> Optional[Dict]:
        """
        Finds a contact by email address.
        
        Args:
            email: Email address to search for
            
        Returns:
            Contact data or None if not found
        """
        contacts = self.get_contacts(email_filter=email)
        return contacts[0] if contacts else None
    
    def get_emails_for_contact(self, contact_id: str) -> List[Dict]:
        """
        Retrieves existing emails for a contact.
        
        Args:
            contact_id: Contact ID (GUID)
            
        Returns:
            List of email dictionaries
        """
        print(f"📧 Retrieving emails for contact {contact_id}...")
        
        params = {
            '$select': 'activityid,subject,description,createdon,actualstart,actualend,statecode,statuscode',
            '$filter': f"_regardingobjectid_value eq '{contact_id}' and activitytypecode eq 'email'",
            '$orderby': 'createdon desc'
        }
        
        result = self._make_request('GET', 'emails', params=params)
        
        if result and 'value' in result:
            emails = result['value']
            print(f"   ✅ Found {len(emails)} existing emails")
            return emails
        else:
            print("   ❌ Failed to retrieve emails")
            return []
    
    def create_email(self, email_data: Dict, contact_id: str) -> Optional[str]:
        """
        Creates an email in Dynamics 365 using Activity Party solution.
        
        Args:
            email_data: Email data from PST
            contact_id: Contact ID to associate with
            
        Returns:
            Created email ID or None if failed
        """
        try:
            # Convert datetime objects to ISO format
            sent_time = email_data.get('sent_time')
            if sent_time and hasattr(sent_time, 'isoformat'):
                sent_time_iso = sent_time.isoformat()
            else:
                sent_time_iso = datetime.now().isoformat()
            
            # Convert email body to HTML format for proper line breaks
            body_text = email_data.get('body', '')
            if body_text:
                # Convert line breaks to HTML <br> tags
                body_html = body_text.replace('\r\n', '<br>').replace('\n', '<br>').replace('\r', '<br>')
                # Replace multiple underscores with line breaks 
                body_html = body_html.replace('_' * 10, '<br>')  # Replace 10+ underscores with line breaks
            else:
                body_html = ''
            
            # Create the email payload with Activity Party solution
            payload = {
                "subject": email_data.get('subject', 'No Subject')[:200],  # Limit subject length
                "description": body_html[:100000],  # Use HTML formatted body
                "actualstart": sent_time_iso,
                "actualend": sent_time_iso,
                "prioritycode": 1,  # Normal priority
                "directioncode": True,  # Incoming
                "regardingobjectid_contact@odata.bind": f"/contacts({contact_id})",
                "ownerid@odata.bind": f"/systemusers({config.SYSTEM_USER_ID})",
                
                # Critical: Activity Party array for proper sender display
                "email_activity_parties": [
                    {
                        "participationtypemask": 1,  # From/Sender
                        "addressused": email_data.get('sender_email', ''),
                        "partyid_contact@odata.bind": f"/contacts({contact_id})"
                    },
                    {
                        "participationtypemask": 2,  # To/Recipient  
                        "addressused": config.USERNAME,
                        "partyid_systemuser@odata.bind": f"/systemusers({config.SYSTEM_USER_ID})"
                    }
                ]
            }
            
            print(f"   📧 Creating email: {email_data.get('subject', 'No Subject')[:50]}...")
            
            result = self._make_request('POST', 'emails', data=payload)
            
            if result and 'activityid' in result:
                email_id = result['activityid']
                print(f"   ✅ Email created with ID: {email_id}")
                return email_id
            else:
                print(f"   ❌ Failed to create email")
                return None
                
        except Exception as e:
            print(f"   ❌ Error creating email: {e}")
            return None
    
    def update_email_status(self, email_id: str, status: str = "Closed") -> bool:
        """
        Updates an email's status to Closed.
        
        Args:
            email_id: Email ID (GUID)
            status: Status to set (default: Closed)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if status.lower() == "closed":
                payload = {
                    "statecode": 1,  # Completed
                    "statuscode": 3  # Closed
                }
            else:
                payload = {
                    "statecode": 0,  # Open
                    "statuscode": 1  # Open
                }
            
            result = self._make_request('PATCH', f'emails({email_id})', data=payload)
            
            if result:
                print(f"   ✅ Email status updated to {status}")
                return True
            else:
                print(f"   ❌ Failed to update email status")
                return False
                
        except Exception as e:
            print(f"   ❌ Error updating email status: {e}")
            return False
    
    def is_email_duplicate(self, new_email: Dict, existing_emails: List[Dict]) -> bool:
        """
        Checks if an email is a duplicate of existing emails.
        
        Args:
            new_email: New email data to check
            existing_emails: List of existing emails
            
        Returns:
            True if duplicate found, False otherwise
        """
        new_subject = new_email.get('subject', '').strip().lower()
        new_time = new_email.get('sent_time')
        
        if not new_time:
            return False
        
        # Convert to datetime if it's not already
        if isinstance(new_time, str):
            try:
                new_time = datetime.fromisoformat(new_time.replace('Z', '+00:00'))
            except (Exception, AttributeError, TypeError, ValueError):
                return False
        elif hasattr(new_time, 'replace'):
            # It's already a datetime object, make sure it's timezone aware
            if new_time.tzinfo is None:
                new_time = new_time.replace(tzinfo=datetime.now().astimezone().tzinfo)
        
        for existing in existing_emails:
            existing_subject = existing.get('subject', '').strip().lower()
            existing_time = existing.get('createdon')
            
            if not existing_time:
                continue
                
            try:
                if isinstance(existing_time, str):
                    existing_time = datetime.fromisoformat(existing_time.replace('Z', '+00:00'))
                
                # Check if subjects match and times are close
                time_diff = abs((new_time - existing_time).total_seconds())
                threshold_seconds = config.DUPLICATE_THRESHOLD_HOURS * 3600
                
                if (new_subject == existing_subject and 
                    time_diff <= threshold_seconds):
                    return True
                    
            except Exception:
                continue
        
        return False
    
    def get_timeline_status(self, contact_id: str) -> Dict:
        """
        Gets the timeline status for a contact.
        
        Args:
            contact_id: Contact ID (GUID)
            
        Returns:
            Dictionary with timeline statistics
        """
        emails = self.get_emails_for_contact(contact_id)
        
        open_count = sum(1 for email in emails if email.get('statecode') == 0)
        closed_count = sum(1 for email in emails if email.get('statecode') == 1)
        
        return {
            'total_emails': len(emails),
            'open_emails': open_count,
            'closed_emails': closed_count,
            'emails': emails
        }


# Global instance
_dynamics_data = None

def get_dynamics_data() -> DynamicsData:
    """Returns the global Dynamics data instance."""
    global _dynamics_data
    if _dynamics_data is None:
        _dynamics_data = DynamicsData()
    return _dynamics_data 