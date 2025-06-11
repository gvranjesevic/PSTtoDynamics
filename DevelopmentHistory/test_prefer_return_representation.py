#!/usr/bin/env python3
"""
Test using Prefer: return=representation to get email ID back
"""

import requests
import msal
from datetime import datetime

# Configuration
username = "gvranjesevic@dynamique.com"
password = "#SanDiegoChicago77"
tenant_domain = "dynamique.com"
crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"
SYSTEM_USER_ID = "5794f83f-9b37-f011-8c4e-000d3a9c4367"

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
        'OData-Version': '4.0',
        'Prefer': 'return=representation'  # Force return of created object
    }

def test_with_prefer_header():
    """Test creating email with Prefer header to get ID back."""
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
    
    # Create test email with Prefer header
    print("\nCreating email with 'Prefer: return=representation' header...")
    
    current_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
    
    email_payload = {
        "subject": "TEST EMAIL - Prefer Header Test",
        "description": "Testing if Prefer header returns the email ID for status updates.<br><br>This should allow us to get the ID and update to Closed status.",
        "regardingobjectid_contact@odata.bind": f"/contacts({contact_id})",
        "directioncode": False,  # Incoming email
        "actualstart": current_time,
        "actualend": current_time,
        "senton": current_time,
        
        # Activity Party relationships
        "email_activity_parties": [
            {
                "partyid_contact@odata.bind": f"/contacts({contact_id})",
                "participationtypemask": 1  # From/Sender
            },
            {
                "partyid_systemuser@odata.bind": f"/systemusers({SYSTEM_USER_ID})",
                "participationtypemask": 2  # To/Recipient
            }
        ]
    }
    
    # Create the email
    create_url = f"{crm_base_url}/emails"
    response = requests.post(create_url, json=email_payload, headers=headers)
    
    print(f"Response Status: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    email_id = None
    if response.status_code in [200, 201]:
        try:
            response_data = response.json()
            email_id = response_data.get('activityid')
            print(f"✅ Email created with ID returned!")
            print(f"   Email ID: {email_id}")
            print(f"   Response keys: {list(response_data.keys())}")
        except:
            print(f"⚠️ Status {response.status_code} but couldn't parse JSON")
    elif response.status_code == 204:
        print(f"⚠️ Still getting 204 (No Content) even with Prefer header")
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return None
    
    # If we got an ID, try to update status
    if email_id:
        print(f"\nUpdating email status to Closed...")
        
        update_url = f"{crm_base_url}/emails({email_id})"
        update_payload = {
            "statecode": 1,  # Completed
            "statuscode": 3  # Closed
        }
        
        update_response = requests.patch(update_url, json=update_payload, headers=headers)
        
        if update_response.status_code == 204:
            print(f"✅ Email status updated to Closed!")
            print(f"\n📋 Please check the timeline - email should show as 'Closed'")
            return email_id
        else:
            print(f"❌ Status update failed: {update_response.status_code}")
            print(f"   Error: {update_response.text}")
    else:
        print(f"\n⚠️ No email ID received - cannot update status")
        print(f"📋 Email will show as 'Active' in timeline")
    
    return email_id

if __name__ == "__main__":
    print("🧪 Testing Prefer Header for Email ID Return")
    print("=" * 50)
    
    result = test_with_prefer_header()
    
    if result:
        print(f"\n🎉 Success! Email created and status updated.")
    else:
        print(f"\n⚠️ Partial success - email created but couldn't update status.") 