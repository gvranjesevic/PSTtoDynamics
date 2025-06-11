#!/usr/bin/env python3
"""Simple comparison to find Email from display field"""

import requests
import msal

# Configuration
username = "gvranjesevic@dynamique.com"
password = "#SanDiegoChicago77"
tenant_domain = "dynamique.com"
crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"

print("🔍 SIMPLE EMAIL COMPARISON")
print("="*26)

# Authenticate
print("\n🔐 Authenticating...")
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

# Get contact
contact_response = requests.get(
    f"{crm_base_url}/contacts?$filter=emailaddress1 eq 'service@ringcentral.com'&$select=contactid,fullname", 
    headers=headers
)

contact = contact_response.json()['value'][0]
contact_id = contact['contactid']
print(f"✅ Contact: {contact['fullname']} ({contact_id})")

# Get a few emails to analyze
print(f"\n📧 Getting recent emails...")

emails_response = requests.get(
    f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {contact_id}&$select=activityid,subject,sender,_emailsender_value,createdon&$orderby=createdon desc&$top=5",
    headers=headers
)

if emails_response.status_code != 200:
    print(f"❌ Error: {emails_response.status_code}")
    exit(1)

emails = emails_response.json().get('value', [])
print(f"📧 Found {len(emails)} emails")

# Separate our test emails from others
test_emails = []
other_emails = []

for email in emails:
    created = email.get('createdon', '')
    if '2025-06-11' in created:
        test_emails.append(email)
    else:
        other_emails.append(email)

print(f"\n📊 Analysis:")
print(f"   🧪 Our test emails: {len(test_emails)}")
print(f"   📧 Other emails: {len(other_emails)}")

# Show details
if test_emails:
    print(f"\n🧪 OUR TEST EMAILS (showing 'Closed'):")
    for i, email in enumerate(test_emails):
        subject = email.get('subject', '')[:50]
        sender = email.get('sender')
        emailsender = email.get('_emailsender_value')
        created = email.get('createdon', '')[:19]
        
        print(f"   {i+1}. {subject}")
        print(f"      Created: {created}")
        print(f"      sender: {sender}")
        print(f"      _emailsender_value: {emailsender}")

if other_emails:
    print(f"\n📧 OTHER EMAILS (might show properly):")
    for i, email in enumerate(other_emails):
        subject = email.get('subject', '')[:50]
        sender = email.get('sender')
        emailsender = email.get('_emailsender_value')
        created = email.get('createdon', '')[:19]
        
        print(f"   {i+1}. {subject}")
        print(f"      Created: {created}")
        print(f"      sender: {sender}")
        print(f"      _emailsender_value: {emailsender}")

# Based on our knowledge, let's try setting the key field
if test_emails:
    print(f"\n🔧 TRYING TO FIX THE FIRST TEST EMAIL...")
    
    test_email_id = test_emails[0]['activityid']
    
    # The key insight: emailsender_value should be the contact ID
    # But we need to set it properly via the relationship binding
    
    update_data = {
        'emailsender_contact@odata.bind': f'/contacts({contact_id})'
    }
    
    print(f"   📧 Updating email: {test_email_id}")
    print(f"   🔗 Setting emailsender_contact to: {contact_id}")
    
    response = requests.patch(
        f"{crm_base_url}/emails({test_email_id})",
        json=update_data,
        headers=headers
    )
    
    if response.status_code in [200, 204]:
        print(f"   ✅ Relationship updated successfully!")
        
        # Verify
        verify_response = requests.get(
            f"{crm_base_url}/emails({test_email_id})?$select=_emailsender_value",
            headers=headers
        )
        
        if verify_response.status_code == 200:
            verify_data = verify_response.json()
            new_emailsender = verify_data.get('_emailsender_value')
            print(f"   📊 _emailsender_value is now: {new_emailsender}")
            
            if new_emailsender == contact_id:
                print(f"   🎉 SUCCESS! EmailSender now points to contact!")
            else:
                print(f"   ⚠️  EmailSender value unexpected")
    else:
        print(f"   ❌ Update failed: {response.status_code}")
        try:
            error_detail = response.json()
            print(f"      Error: {error_detail}")
        except:
            print(f"      Error: {response.text[:200]}")

print(f"\n💡 THEORY:")
print(f"   🔑 The '_emailsender_value' field controls 'Email from:' display")
print(f"   📧 It should contain the contact ID: {contact_id}")
print(f"   🔗 Set via: emailsender_contact@odata.bind")
print(f"\n📅 Please refresh timeline and check if 'Email from:' is now fixed!")
print(f"   Expected: 'Email from: service@ringcentral.com'")
print(f"   Current:  'Email from: Closed'") 