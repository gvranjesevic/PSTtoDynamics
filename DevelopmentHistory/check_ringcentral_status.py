#!/usr/bin/env python3
"""
Check status of RingCentral emails - Active vs Closed
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

def check_email_status():
    """Check status of RingCentral emails."""
    headers = get_auth_headers()
    if not headers:
        return
    
    # Get RingCentral contact ID
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
    
    contact_id = contacts[0]['contactid']
    contact_name = contacts[0]['fullname']
    print(f"Found contact: {contact_name}")
    
    # Get emails with status information
    print("\nChecking email status...")
    email_url = f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {contact_id}&$select=subject,statecode,statuscode,createdon&$orderby=createdon desc&$top=20"
    email_response = requests.get(email_url, headers=headers)
    
    if email_response.status_code != 200:
        print(f"Failed to get emails: {email_response.status_code}")
        return
    
    emails = email_response.json().get('value', [])
    
    print(f"\nEmail Status Analysis (showing recent 20 emails):")
    print(f"Total emails checked: {len(emails)}")
    
    active_count = 0
    closed_count = 0
    
    print(f"\nDetailed Status:")
    for i, email in enumerate(emails):
        subject = email.get('subject', 'No Subject')[:50]
        statecode = email.get('statecode', 'Unknown')
        statuscode = email.get('statuscode', 'Unknown')
        created = email.get('createdon', 'Unknown')[:19]  # Remove timezone info
        
        # Interpret status codes
        if statecode == 0:
            status_text = "Active"
            active_count += 1
        elif statecode == 1:
            status_text = "Closed"
            closed_count += 1
        else:
            status_text = f"Unknown({statecode})"
        
        print(f"  {i+1:2d}. {subject}")
        print(f"      Status: {status_text} (State: {statecode}, Code: {statuscode})")
        print(f"      Created: {created}")
        print()
    
    print(f"\nSummary:")
    print(f"  Active emails: {active_count}")
    print(f"  Closed emails: {closed_count}")
    print(f"  Total checked: {len(emails)}")
    
    if active_count > 0:
        print(f"\n⚠️  Found {active_count} Active emails that should be Closed!")
        print("These are likely historical emails that need status correction.")
    else:
        print(f"\n✅ All emails are properly Closed!")

if __name__ == "__main__":
    check_email_status() 