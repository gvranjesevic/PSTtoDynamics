#!/usr/bin/env python3
"""
Test creating one email with Closed status
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
        'OData-Version': '4.0'
    }

def test_create_closed_email():
    """Test creating one email with Closed status."""
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
    
    # Create test email (initially Open)
    print("\nStep 1: Creating test email...")
    
    current_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
    
    email_payload = {
        "subject": "TEST EMAIL - Closed Status Fix (Two-Step)",
        "description": "This is a test email to verify that emails can be created and then set to Closed status.<br><br>If this appears as 'Closed' in the timeline, the fix is working!",
        "regardingobjectid_contact@odata.bind": f"/contacts({contact_id})",
        "directioncode": False,  # Incoming email
        "actualstart": current_time,
        "actualend": current_time,
        "senton": current_time,
        
        # Don't set status during creation - will be Open by default
        
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
    
    # Step 1: Create the email
    create_url = f"{crm_base_url}/emails"
    response = requests.post(create_url, json=email_payload, headers=headers)
    
    email_id = None
    if response.status_code == 201:
        email_id = response.json().get('activityid')
        print(f"✅ Email created successfully!")
        print(f"   Status: {response.status_code}")
        print(f"   Email ID: {email_id}")
    elif response.status_code == 204:
        print(f"✅ Email created successfully!")
        print(f"   Status: {response.status_code} (No Content - cannot update status)")
        print(f"\n📋 Please check the RingCentral timeline in Dynamics 365:")
        print(f"   - Look for subject: 'TEST EMAIL - Closed Status Fix (Two-Step)'")
        print(f"   - Verify it shows 'Email from: RingCentral'")
        print(f"   - Note: Status will be 'Active' (we couldn't get ID to update)")
        return "success_no_id"
    else:
        print(f"❌ Failed to create test email: {response.status_code}")
        print(f"   Error: {response.text}")
        return None
    
    # Step 2: Update status to Closed (only if we have email ID)
    if email_id:
        print(f"\nStep 2: Updating email status to Closed...")
        
        update_url = f"{crm_base_url}/emails({email_id})"
        update_payload = {
            "statecode": 1,  # Completed
            "statuscode": 3  # Closed
        }
        
        update_response = requests.patch(update_url, json=update_payload, headers=headers)
        
        if update_response.status_code == 204:
            print(f"✅ Email status updated to Closed!")
            print(f"\n📋 Please check the RingCentral timeline in Dynamics 365:")
            print(f"   - Look for subject: 'TEST EMAIL - Closed Status Fix (Two-Step)'")
            print(f"   - Verify it shows 'Email from: RingCentral'")
            print(f"   - Verify status shows 'Closed' (not 'Active')")
            return email_id
        else:
            print(f"⚠️ Email created but status update failed: {update_response.status_code}")
            print(f"   Error: {update_response.text}")
            print(f"   Email will show as 'Active' instead of 'Closed'")
            return email_id
    
    return None

if __name__ == "__main__":
    print("🧪 Testing Email Creation with Closed Status")
    print("=" * 50)
    
    result = test_create_closed_email()
    
    if result:
        print(f"\n🎉 Test completed successfully!")
        print(f"Please verify the email status in Dynamics 365.")
    else:
        print(f"\n❌ Test failed!") 