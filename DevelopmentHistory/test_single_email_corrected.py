#!/usr/bin/env python3
"""
Test script to create ONE properly formatted email using the corrected Activity Party solution.
This implements the fix documented in SOLUTION_TO_EMAIL_FROM_PROBLEM.md
"""

import requests
import msal
from datetime import datetime

# --- Configuration ---
username = "gvranjesevic@dynamique.com"
password = "#SanDiegoChicago77"
tenant_domain = "dynamique.com"
crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"

# Known IDs from our previous work
RINGCENTRAL_CONTACT_ID = "6a219814-dc41-f011-b4cb-7c1e52168e20"
SYSTEM_USER_ID = "5794f83f-9b37-f011-8c4e-000d3a9c4367"

def get_auth_headers():
    """Authenticates and returns headers for API requests."""
    print("🔐 Authenticating to Dynamics 365...")
    app = msal.PublicClientApplication(client_id, authority=f"https://login.microsoftonline.com/{tenant_domain}")
    result = app.acquire_token_by_username_password(username, password, scopes=["https://dynglobal.crm.dynamics.com/.default"])
    
    if "access_token" not in result:
        print(f"❌ Authentication failed: {result}")
        return None
    
    print("✅ Authentication successful!")
    return {
        'Authorization': f'Bearer {result["access_token"]}',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'OData-MaxVersion': '4.0',
        'OData-Version': '4.0'
    }

def create_test_email(headers):
    """Creates a single test email using the corrected Activity Party approach."""
    print("\n📧 Creating test email with correct Activity Party relationships...")
    
    # Email payload with correct email_activity_parties structure
    email_payload = {
        "subject": "✅ CORRECTED TEST: April 2025 RingCentral Email Import",
        "description": "This is a test email created using the corrected Activity Party solution.<br><br>" +
                      "Key improvements:<br>" +
                      "• Proper sender display using email_activity_parties<br>" +
                      "• HTML formatting with &lt;br&gt; tags<br>" +
                      "• Two-step process: CREATE then UPDATE status<br><br>" +
                      "This email should display 'Email from: RingCentral' correctly in the timeline.",
        
        # Link to RingCentral contact
        "regardingobjectid_contact@odata.bind": f"/contacts({RINGCENTRAL_CONTACT_ID})",
        
        # Email direction and timing
        "directioncode": False,  # Incoming email
        "actualstart": "2025-04-15T14:30:00Z",
        "actualend": "2025-04-15T14:30:00Z", 
        "senton": "2025-04-15T14:30:00Z",
        
        # CRITICAL: Activity Party relationships (this is the fix!)
        "email_activity_parties": [
            {
                # Sender (From): RingCentral Contact
                "partyid_contact@odata.bind": f"/contacts({RINGCENTRAL_CONTACT_ID})",
                "participationtypemask": 1  # 1 = From/Sender
            },
            {
                # Recipient (To): System User
                "partyid_systemuser@odata.bind": f"/systemusers({SYSTEM_USER_ID})",
                "participationtypemask": 2  # 2 = To/Recipient
            }
        ]
    }
    
    # Step 1: Create the email
    create_url = f"{crm_base_url}/emails"
    print(f"   📤 POST request to: {create_url}")
    print(f"   📄 Payload includes email_activity_parties with participationtypemask values")
    
    response = requests.post(create_url, json=email_payload, headers=headers)
    
    if response.status_code == 204:
        # Get the new email ID from the Location header
        location_header = response.headers.get('OData-EntityId', '')
        if location_header:
            email_id = location_header.split('(')[1].split(')')[0]
            print(f"   ✅ Email created successfully! ID: {email_id}")
            return email_id
        else:
            print(f"   ⚠️ Email created but couldn't extract ID from headers")
            return None
    else:
        print(f"   ❌ Failed to create email: {response.status_code}")
        print(f"   📄 Response: {response.text}")
        return None

def update_email_status(headers, email_id):
    """Updates the email status to 'Closed' - this is step 2 of the process."""
    print(f"\n📝 Updating email status to 'Closed'...")
    
    # Step 2: Update status to Closed
    status_payload = {
        "statecode": 1,      # Completed
        "statuscode": 4      # Received
    }
    
    update_url = f"{crm_base_url}/emails({email_id})"
    print(f"   📤 PATCH request to: {update_url}")
    
    response = requests.patch(update_url, json=status_payload, headers=headers)
    
    if response.status_code in [200, 204]:
        print(f"   ✅ Email status updated to 'Closed' successfully!")
        return True
    else:
        print(f"   ❌ Failed to update status: {response.status_code}")
        print(f"   📄 Response: {response.text}")
        return False

def verify_email(headers, email_id):
    """Retrieves and displays the created email for verification."""
    print(f"\n🔍 Verifying created email...")
    
    verify_url = f"{crm_base_url}/emails({email_id})?$select=activityid,subject,statecode,statuscode,createdon,senton&$expand=email_activity_parties($select=participationtypemask,partyid)"
    
    response = requests.get(verify_url, headers=headers)
    
    if response.status_code == 200:
        email_data = response.json()
        print(f"   📧 Subject: {email_data.get('subject', 'N/A')}")
        print(f"   📅 Created: {email_data.get('createdon', 'N/A')}")
        print(f"   📅 Sent: {email_data.get('senton', 'N/A')}")
        print(f"   📊 State: {email_data.get('statecode', 'N/A')} (0=Open, 1=Completed)")
        print(f"   📊 Status: {email_data.get('statuscode', 'N/A')} (4=Received)")
        
        # Show activity parties
        parties = email_data.get('email_activity_parties', [])
        print(f"   👥 Activity Parties: {len(parties)} found")
        for party in parties:
            mask = party.get('participationtypemask', 'Unknown')
            role = {1: 'From/Sender', 2: 'To/Recipient', 3: 'CC', 4: 'BCC'}.get(mask, f'Unknown({mask})')
            print(f"      • {role} (mask: {mask})")
        
        return True
    else:
        print(f"   ❌ Failed to verify email: {response.status_code}")
        return False

if __name__ == "__main__":
    print("🧪 Single Email Test - Corrected Activity Party Solution")
    print("=" * 60)
    print("This script implements the fix from SOLUTION_TO_EMAIL_FROM_PROBLEM.md")
    print()
    
    # Authenticate
    headers = get_auth_headers()
    if not headers:
        exit(1)
    
    # Step 1: Create email with correct Activity Party relationships
    email_id = create_test_email(headers)
    if not email_id:
        print("\n❌ Test failed at email creation step.")
        exit(1)
    
    # Step 2: Update status to Closed
    status_updated = update_email_status(headers, email_id)
    if not status_updated:
        print("\n⚠️ Email created but status update failed.")
    
    # Step 3: Verify the result
    verification_success = verify_email(headers, email_id)
    
    print("\n" + "=" * 60)
    if verification_success and status_updated:
        print("🎉 SUCCESS! Test email created with corrected Activity Party solution.")
        print(f"📧 Email ID: {email_id}")
        print()
        print("✅ What to check in your Dynamics 365 timeline:")
        print("   • Email should show 'Email from: RingCentral' (not 'Email from: Closed')")
        print("   • Status should be 'Closed'")
        print("   • HTML formatting should display properly")
        print("   • Subject should start with '✅ CORRECTED TEST:'")
        print()
        print("📸 Please take a screenshot of this email in the timeline for review!")
    else:
        print("❌ Test completed with some issues. Check the output above.")
    
    print("=" * 60) 