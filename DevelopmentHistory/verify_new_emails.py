#!/usr/bin/env python3
"""Verify the newest test emails have emailsender set correctly"""

import requests
import msal

# Configuration
username = "gvranjesevic@dynamique.com"
password = "#SanDiegoChicago77"
tenant_domain = "dynamique.com"
crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"

print("🔍 VERIFYING NEW TEST EMAILS")
print("="*28)

# Authenticate
app = msal.PublicClientApplication(
    client_id=client_id,
    authority=f"https://login.microsoftonline.com/{tenant_domain}"
)

result = app.acquire_token_by_username_password(
    username=username,
    password=password,
    scopes=["https://dynglobal.crm.dynamics.com/.default"]
)

access_token = result["access_token"]
headers = {
    'Authorization': f'Bearer {access_token}',
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'OData-MaxVersion': '4.0',
    'OData-Version': '4.0'
}

# Get contact
contact_response = requests.get(
    f"{crm_base_url}/contacts?$filter=emailaddress1 eq 'service@ringcentral.com'&$select=contactid,fullname", 
    headers=headers
)

contact = contact_response.json()['value'][0]
contact_id = contact['contactid']
print(f"✅ Contact: {contact['fullname']} ({contact_id})")

# Get the 3 newest emails (just created)
print(f"\n📧 Getting newest emails...")

newest_emails_response = requests.get(
    f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {contact_id}&$select=activityid,subject,_emailsender_value,sender,createdon&$orderby=createdon desc&$top=3",
    headers=headers
)

newest_emails = newest_emails_response.json().get('value', [])
print(f"📧 Found {len(newest_emails)} newest emails")

success_count = 0
for i, email in enumerate(newest_emails):
    subject = email.get('subject', '')[:50]
    emailsender = email.get('_emailsender_value')
    sender = email.get('sender')
    created = email.get('createdon', '')[:19]
    
    print(f"\n   📧 Email {i+1}: {subject}")
    print(f"      Created: {created}")
    print(f"      sender: {sender}")
    print(f"      _emailsender_value: {emailsender}")
    
    if emailsender == contact_id:
        print(f"      🎉 EmailSender correctly set!")
        success_count += 1
    else:
        print(f"      ❌ EmailSender not set correctly")

print(f"\n🎯 VERIFICATION RESULTS:")
print(f"   ✅ Correct emailsender: {success_count}/3")
print(f"   📧 Contact ID: {contact_id}")

if success_count == 3:
    print(f"\n🎉 PERFECT! All 3 emails have correct emailsender!")
    print(f"   📅 Refresh timeline - should show 'Email from: service@ringcentral.com'")
    print(f"   🚀 Strategy proven - ready for full 71 April email import!")
else:
    print(f"\n⚠️  Only {success_count}/3 emails have correct emailsender")
    print(f"   💡 May need to adjust the approach") 