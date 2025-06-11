#!/usr/bin/env python3
"""Investigate all email fields to understand how to fix sender display"""

import requests
import msal
import json

# Configuration
username = "gvranjesevic@dynamique.com"
password = "#SanDiegoChicago77"
tenant_domain = "dynamique.com"
crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"

print("🔍 INVESTIGATING EMAIL FIELDS")
print("="*40)

# Authenticate
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
headers = {
    'Authorization': f'Bearer {access_token}',
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'OData-MaxVersion': '4.0',
    'OData-Version': '4.0'
}

print("✅ Authentication successful!")

# Get the service@ringcentral.com contact
contact_response = requests.get(
    f"{crm_base_url}/contacts?$filter=emailaddress1 eq 'service@ringcentral.com'&$select=contactid,fullname", 
    headers=headers
)

contact = contact_response.json()['value'][0]
contact_id = contact['contactid']
print(f"✅ Contact: {contact['fullname']} ({contact_id})")

# Get one April email for investigation
print("\n🔍 Getting sample April email...")
email_response = requests.get(
    f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {contact_id} and actualstart ge 2025-04-01T00:00:00Z and actualstart le 2025-04-30T23:59:59Z&$top=1",
    headers=headers
)

if email_response.status_code != 200:
    print(f"❌ Error: {email_response.status_code}")
    exit(1)

emails = email_response.json()['value']
if not emails:
    print("❌ No emails found")
    exit(1)

email_id = emails[0]['activityid']
print(f"📧 Investigating email: {email_id}")

# Get complete email details
print("\n🔍 Getting all email fields...")
complete_email_response = requests.get(
    f"{crm_base_url}/emails({email_id})",
    headers=headers
)

if complete_email_response.status_code != 200:
    print(f"❌ Error getting complete email: {complete_email_response.status_code}")
    exit(1)

email_data = complete_email_response.json()

print(f"\n📝 ALL EMAIL FIELDS:")
print("="*50)

# Sort and display all fields
for field in sorted(email_data.keys()):
    value = email_data[field]
    if isinstance(value, str) and len(value) > 100:
        value = value[:100] + "..."
    print(f"{field}: {value}")

print(f"\n🔍 SENDER-RELATED FIELDS:")
print("="*30)
sender_keywords = ['from', 'send', 'email', 'to', 'cc', 'bcc']
sender_fields = []

for field in email_data.keys():
    for keyword in sender_keywords:
        if keyword in field.lower():
            sender_fields.append(field)
            break

for field in sorted(set(sender_fields)):
    value = email_data[field]
    if isinstance(value, str) and len(value) > 100:
        value = value[:100] + "..."
    print(f"   {field}: {value}")

print(f"\n🔍 STATUS/STATE FIELDS:")
print("="*25)
status_keywords = ['state', 'status', 'active', 'closed']
status_fields = []

for field in email_data.keys():
    for keyword in status_keywords:
        if keyword in field.lower():
            status_fields.append(field)
            break

for field in sorted(set(status_fields)):
    value = email_data[field]
    print(f"   {field}: {value}")

# Now let's compare with an original email (if available)
print(f"\n🔍 COMPARING WITH ORIGINAL RINGCENTRAL EMAIL...")

# Try to get an original RingCentral email from the notify@ringcentral.com contact
notify_contact_response = requests.get(
    f"{crm_base_url}/contacts?$filter=emailaddress1 eq 'notify@ringcentral.com'&$select=contactid", 
    headers=headers
)

if notify_contact_response.status_code == 200:
    notify_contacts = notify_contact_response.json().get('value', [])
    if notify_contacts:
        notify_contact_id = notify_contacts[0]['contactid']
        
        # Get an original email from notify contact
        original_email_response = requests.get(
            f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {notify_contact_id}&$top=1",
            headers=headers
        )
        
        if original_email_response.status_code == 200:
            original_emails = original_email_response.json().get('value', [])
            if original_emails:
                original_email_id = original_emails[0]['activityid']
                
                # Get complete original email
                original_complete_response = requests.get(
                    f"{crm_base_url}/emails({original_email_id})",
                    headers=headers
                )
                
                if original_complete_response.status_code == 200:
                    original_data = original_complete_response.json()
                    
                    print(f"\n📧 ORIGINAL EMAIL SENDER FIELDS:")
                    print("="*35)
                    
                    for field in sorted(set(sender_fields)):
                        our_value = email_data.get(field, 'None')
                        original_value = original_data.get(field, 'None')
                        
                        if isinstance(our_value, str) and len(our_value) > 50:
                            our_value = our_value[:50] + "..."
                        if isinstance(original_value, str) and len(original_value) > 50:
                            original_value = original_value[:50] + "..."
                            
                        print(f"   {field}:")
                        print(f"      Our email: {our_value}")
                        print(f"      Original:  {original_value}")
                        print()

print(f"\n💡 ANALYSIS:")
print("="*15)
print("1. Look for fields where 'Original' has values but 'Our email' is None")
print("2. These are the fields we need to set to fix the 'Email from: Active' issue")
print("3. Common fields to check: from, sender, emailsender, sendername")
print("4. The field that controls the 'Email from:' display needs to be identified and set") 