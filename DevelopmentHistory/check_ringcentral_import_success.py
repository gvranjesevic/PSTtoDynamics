#!/usr/bin/env python3
"""
Quick verification: Check RingCentral emails in Dynamics 365
"""

import requests
import msal

# Configuration
username = "gvranjesevic@dynamique.com"
password = "#SanDiegoChicago77"
tenant_domain = "dynamique.com"
crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"

def get_auth_headers():
    """Authenticates and returns headers for API requests."""
    print("Authenticating to Dynamics 365...")
    app = msal.PublicClientApplication(client_id, authority=f"https://login.microsoftonline.com/{tenant_domain}")
    result = app.acquire_token_by_username_password(username, password, scopes=["https://dynglobal.crm.dynamics.com/.default"])
    
    if "access_token" not in result:
        print(f"Authentication failed: {result}")
        return None
    
    print("Authentication successful!")
    return {
        'Authorization': f'Bearer {result["access_token"]}',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'OData-MaxVersion': '4.0',
        'OData-Version': '4.0'
    }

def check_ringcentral_emails():
    """Check RingCentral emails in Dynamics 365."""
    headers = get_auth_headers()
    if not headers:
        return
    
    # First, get RingCentral contact ID
    print("\nFinding RingCentral contact...")
    contact_url = f"{crm_base_url}/contacts?$filter=emailaddress1 eq 'service@ringcentral.com'&$select=contactid,fullname"
    contact_response = requests.get(contact_url, headers=headers)
    
    if contact_response.status_code != 200:
        print(f"Failed to get contact: {contact_response.status_code}")
        return
    
    contacts = contact_response.json().get('value', [])
    if not contacts:
        print("RingCentral contact not found!")
        return
    
    contact = contacts[0]
    contact_id = contact['contactid']
    contact_name = contact['fullname']
    
    print(f"Found contact: {contact_name} (ID: {contact_id})")
    
    # Get all emails for this contact
    print("\nChecking emails for RingCentral contact...")
    email_url = f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {contact_id}&$select=subject,senton,createdon,modifiedon&$orderby=createdon desc"
    email_response = requests.get(email_url, headers=headers)
    
    if email_response.status_code != 200:
        print(f"Failed to get emails: {email_response.status_code}")
        return
    
    emails = email_response.json().get('value', [])
    
    print(f"\nRingCentral Email Summary:")
    print(f"  Total emails found: {len(emails)}")
    
    if emails:
        print(f"\nRecent emails (showing first 10):")
        for i, email in enumerate(emails[:10]):
            subject = email.get('subject', 'No Subject')
            created = email.get('createdon', 'Unknown')
            modified = email.get('modifiedon', 'Unknown')
            
            print(f"  {i+1:2d}. {subject[:60]}")
            print(f"      Created: {created}")
            print(f"      Modified: {modified}")
            print()
        
        # Check for recently created emails (likely from our import)
        from datetime import datetime, timedelta
        now = datetime.now()
        recent_cutoff = now - timedelta(hours=2)  # Emails created in last 2 hours
        
        recent_emails = []
        for email in emails:
            try:
                created_time = datetime.fromisoformat(email.get('createdon', '').replace('Z', '+00:00'))
                if created_time.replace(tzinfo=None) > recent_cutoff:
                    recent_emails.append(email)
            except:
                pass
        
        print(f"Recently imported emails (last 2 hours): {len(recent_emails)}")
        
        if recent_emails:
            print("Recent imports:")
            for email in recent_emails[:5]:
                subject = email.get('subject', 'No Subject')
                created = email.get('createdon', 'Unknown')
                print(f"  - {subject[:50]} (Created: {created})")
    else:
        print("  No emails found for RingCentral contact")

if __name__ == "__main__":
    check_ringcentral_emails() 