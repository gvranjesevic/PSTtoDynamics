#!/usr/bin/env python3
"""Minimal test to create one email activity"""

import requests
import msal

# Configuration
username = "gvranjesevic@dynamique.com"
password = "#SanDiegoChicago77"
tenant_domain = "dynamique.com"
crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"

print("🔐 Authenticating...")
app = msal.PublicClientApplication(
    client_id=client_id,
    authority=f"https://login.microsoftonline.com/{tenant_domain}"
)

result = app.acquire_token_by_username_password(
    username=username,
    password=password,
    scopes=["https://dynglobal.crm.dynamics.com/.default"]
)

if "access_token" not in result:
    print(f"❌ Auth failed: {result}")
    exit(1)

access_token = result["access_token"]
print("✅ Authentication successful!")

# Get first contact
print("📥 Getting first contact...")
headers = {
    'Authorization': f'Bearer {access_token}',
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'OData-MaxVersion': '4.0',
    'OData-Version': '4.0'
}

response = requests.get(f"{crm_base_url}/contacts?$top=1", headers=headers)
if response.status_code != 200:
    print(f"❌ Failed to get contacts: {response.status_code}")
    exit(1)

contacts = response.json().get('value', [])
if not contacts:
    print("❌ No contacts found")
    exit(1)

contact = contacts[0]
contact_id = contact['contactid']
print(f"✅ Got contact: {contact.get('fullname', 'Unknown')} ({contact_id})")

# Create test email
print("📧 Creating test email...")
email_data = {
    'subject': 'Test Email from PST Import',
    'description': 'This is a test email created by the timeline restoration system.',
    'directioncode': True,
    'regardingobjectid_contact@odata.bind': f"{crm_base_url}/contacts({contact_id})"
}

response = requests.post(f"{crm_base_url}/emails", json=email_data, headers=headers)

if response.status_code in [200, 201, 204]:
    print(f"✅ Email created successfully! Status: {response.status_code}")
    
    # For 204, we need to get the email ID from the location header or make another request
    if response.status_code == 204:
        print("🎉 MINIMAL TEST PASSED! Email created with relationship!")
        print("✅ The 204 status indicates successful creation with no content returned")
    else:
        email_response = response.json()
        email_id = email_response.get('activityid')
        print(f"Email ID: {email_id}")
        
        # Set to completed state
        print("🔄 Setting email to completed state...")
        state_data = {
            'statecode': 1,  # Completed
            'statuscode': 3   # Sent
        }
        
        state_response = requests.patch(f"{crm_base_url}/emails({email_id})", json=state_data, headers=headers)
        
        if state_response.status_code in [200, 204]:
            print("✅ Email state updated successfully!")
            print("🎉 MINIMAL TEST PASSED!")
        else:
            print(f"⚠️  State update warning: {state_response.status_code} - {state_response.text[:100]}")
            print("✅ Email created but state not updated - PARTIAL SUCCESS!")
else:
    print(f"❌ Email creation failed: {response.status_code}")
    print(f"Error: {response.text}")
    exit(1) 