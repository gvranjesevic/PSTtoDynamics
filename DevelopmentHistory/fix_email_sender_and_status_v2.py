#!/usr/bin/env python3
"""Fix sender email address and status of imported service@ringcentral.com emails"""

import requests
import msal

# Configuration
username = "gvranjesevic@dynamique.com"
password = "#SanDiegoChicago77"
tenant_domain = "dynamique.com"
crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"

print("🔧 FIXING EMAIL SENDER AND STATUS")
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
print("🔍 Getting service@ringcentral.com contact...")
contact_response = requests.get(
    f"{crm_base_url}/contacts?$filter=emailaddress1 eq 'service@ringcentral.com'&$select=contactid,fullname", 
    headers=headers
)

if contact_response.status_code != 200:
    print(f"❌ Error getting contact: {contact_response.status_code}")
    exit(1)

contacts = contact_response.json().get('value', [])
if not contacts:
    print("❌ service@ringcentral.com contact not found")
    exit(1)

contact = contacts[0]
contact_id = contact['contactid']
print(f"✅ Contact: {contact['fullname']} ({contact_id})")

# Get April 2025 emails that need fixing - use basic fields first
print("\n🔍 Getting April 2025 emails...")
april_start = "2025-04-01T00:00:00Z"
april_end = "2025-04-30T23:59:59Z"

# Use a simpler query first to get the emails
email_response = requests.get(
    f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {contact_id} and actualstart ge {april_start} and actualstart le {april_end}&$select=activityid,subject,statecode,statuscode,actualstart&$orderby=actualstart asc&$top=100",
    headers=headers
)

if email_response.status_code != 200:
    print(f"❌ Error getting emails: {email_response.status_code}")
    print(f"Response: {email_response.text}")
    exit(1)

emails_to_fix = email_response.json().get('value', [])
print(f"📧 Found {len(emails_to_fix)} April emails")

if len(emails_to_fix) == 0:
    print("✅ No April emails found!")
    exit(0)

# Analyze what needs fixing
emails_need_status_fix = []

print(f"\n📝 Analyzing email statuses...")
for email in emails_to_fix:
    current_statecode = email.get('statecode', 0)
    current_statuscode = email.get('statuscode', 1)
    
    # Check if status needs fixing (should be closed: statecode=1, statuscode=3)
    if current_statecode != 1 or current_statuscode != 3:
        emails_need_status_fix.append(email)

print(f"📧 Emails needing status fix: {len(emails_need_status_fix)}")

# Show samples
if emails_need_status_fix:
    print(f"\n📝 Sample emails needing status fix:")
    for i, email in enumerate(emails_need_status_fix[:5]):
        actual_start = email.get('actualstart', '')[:19]
        subject = email.get('subject', 'No Subject')[:40]
        statecode = email.get('statecode', 0)
        statuscode = email.get('statuscode', 1)
        status_text = "Active" if statecode == 0 else "Closed"
        print(f"   {i+1}. {actual_start} - {subject}")
        print(f"      Current status: {status_text} (statecode={statecode}, statuscode={statuscode})")

if len(emails_need_status_fix) == 0:
    print("\n✅ All emails already have correct status!")
    
    # Now let's check sender information separately
    print("\n🔍 Checking sender information...")
    
    # Get one email to check available fields
    sample_response = requests.get(
        f"{crm_base_url}/emails({emails_to_fix[0]['activityid']})",
        headers=headers
    )
    
    if sample_response.status_code == 200:
        sample_email = sample_response.json()
        print(f"\n📝 Available fields for emails:")
        interesting_fields = ['from', 'sender', 'sendername', 'senderemailaddress', 'emailsender']
        for field in interesting_fields:
            if field in sample_email:
                print(f"   {field}: {sample_email[field]}")
    
    exit(0)

# Ask for confirmation
confirmation = input(f"\n🤔 Fix status for {len(emails_need_status_fix)} emails? (yes/no): ").strip().lower()
if confirmation not in ['yes', 'y']:
    print("❌ Fix cancelled")
    exit(0)

# Fix the email statuses
print(f"\n🔧 Starting status fixes...")
fixed_count = 0
error_count = 0

for i, email in enumerate(emails_need_status_fix):
    email_id = email['activityid']
    
    try:
        print(f"🔧 Fixing email {i+1}/{len(emails_need_status_fix)}...")
        
        # Set to closed status
        update_data = {
            'statecode': 1,  # Completed
            'statuscode': 3  # Sent
        }
        
        response = requests.patch(
            f"{crm_base_url}/emails({email_id})",
            json=update_data,
            headers=headers
        )
        
        if response.status_code in [200, 204]:
            fixed_count += 1
            print(f"   ✅ Status set to: Closed")
            if i % 10 == 0 and i > 0:
                print(f"   📊 Fixed {fixed_count} emails so far...")
        else:
            error_count += 1
            if error_count <= 3:
                print(f"   ❌ Error fixing email {i+1}: {response.status_code}")
                if error_count == 1:
                    print(f"       Details: {response.text[:200]}")
        
    except Exception as e:
        error_count += 1
        if error_count <= 3:
            print(f"   ❌ Exception fixing email {i+1}: {str(e)}")

print(f"\n🎯 STATUS FIX RESULTS:")
print(f"   ✅ Successfully fixed: {fixed_count} emails")
print(f"   ❌ Errors: {error_count} emails")

if fixed_count > 0:
    print(f"\n🎉 SUCCESS!")
    print(f"   📊 {fixed_count} emails now have 'Closed' status")
    print(f"   📅 Refresh Dynamics 365 to see the change from 'Active' to 'Closed'")
else:
    print(f"\n⚠️  No emails were updated.")

# Now let's investigate the sender field issue
print(f"\n🔍 Investigating sender field options...")
if emails_to_fix:
    sample_email_id = emails_to_fix[0]['activityid']
    sample_response = requests.get(
        f"{crm_base_url}/emails({sample_email_id})",
        headers=headers
    )
    
    if sample_response.status_code == 200:
        sample_email = sample_response.json()
        print(f"\n📝 Available sender-related fields:")
        sender_fields = [key for key in sample_email.keys() if 'from' in key.lower() or 'send' in key.lower() or 'email' in key.lower()]
        for field in sorted(sender_fields):
            value = sample_email.get(field, 'None')
            print(f"   {field}: {value}")
        
        print(f"\n💡 To fix the 'Email from: Active' issue, we need to identify the correct field.")
        print(f"   This requires setting the proper sender email address field.")
        print(f"   The investigation above shows which fields are available to update.") 