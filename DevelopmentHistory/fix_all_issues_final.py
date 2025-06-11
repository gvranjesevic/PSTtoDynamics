#!/usr/bin/env python3
"""Final comprehensive fix for both formatting and Email from display"""

import requests
import msal
import re

# Configuration
username = "gvranjesevic@dynamique.com"
password = "#SanDiegoChicago77"
tenant_domain = "dynamique.com"
crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"

print("🔧 FINAL COMPREHENSIVE FIX")
print("="*30)
print("1. Re-applying HTML formatting (underscores → line breaks)")
print("2. Final attempt at fixing 'Email from' display")
print("="*30)

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

# Get the service@ringcentral.com contact
contact_response = requests.get(
    f"{crm_base_url}/contacts?$filter=emailaddress1 eq 'service@ringcentral.com'&$select=contactid,fullname", 
    headers=headers
)

contact = contact_response.json()['value'][0]
contact_id = contact['contactid']
print(f"✅ Contact: {contact['fullname']} ({contact_id})")

# Get April 2025 emails
print(f"\n🔍 Getting April 2025 emails...")
april_start = "2025-04-01T00:00:00Z"
april_end = "2025-04-30T23:59:59Z"

email_response = requests.get(
    f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {contact_id} and actualstart ge {april_start} and actualstart le {april_end}&$select=activityid,subject,description,safedescription&$orderby=actualstart asc",
    headers=headers
)

if email_response.status_code != 200:
    print(f"❌ Error getting emails: {email_response.status_code}")
    exit(1)

emails = email_response.json().get('value', [])
print(f"📧 Found {len(emails)} April emails")

if len(emails) == 0:
    print("✅ No emails found!")
    exit(0)

# Check which emails have underscore formatting issues
emails_needing_format_fix = []

for email in emails:
    description = email.get('description', '')
    if '________________________________' in description:
        emails_needing_format_fix.append(email)

print(f"📧 Emails needing formatting fix: {len(emails_needing_format_fix)}")

if len(emails_needing_format_fix) > 0:
    print(f"\n📝 Sample emails with underscore issues:")
    for i, email in enumerate(emails_needing_format_fix[:3]):
        subject = email.get('subject', 'No Subject')[:50]
        print(f"   {i+1}. {subject}")

    # Ask for confirmation
    format_confirmation = input(f"\n🤔 Re-apply HTML formatting to fix underscores? (yes/no): ").strip().lower()
    if format_confirmation in ['yes', 'y']:
        print(f"\n🔧 Fixing formatting for {len(emails_needing_format_fix)} emails...")
        
        format_fixed_count = 0
        format_error_count = 0
        
        for i, email in enumerate(emails_needing_format_fix):
            email_id = email['activityid']
            
            try:
                # Get current description
                current_desc = email.get('description', '')
                current_safe_desc = email.get('safedescription', '')
                
                # Convert underscores to HTML breaks
                new_desc = current_desc.replace('________________________________', '<br><br>')
                new_safe_desc = current_safe_desc.replace('________________________________', '<br><br>')
                
                # Update the email
                update_data = {
                    'description': new_desc,
                    'safedescription': new_safe_desc
                }
                
                response = requests.patch(
                    f"{crm_base_url}/emails({email_id})",
                    json=update_data,
                    headers=headers
                )
                
                if response.status_code in [200, 204]:
                    format_fixed_count += 1
                    if (i + 1) % 10 == 0:
                        print(f"   ✅ Fixed formatting for {i + 1}/{len(emails_needing_format_fix)} emails...")
                else:
                    format_error_count += 1
                    if format_error_count <= 3:
                        print(f"   ❌ Error fixing email {i+1}: {response.status_code}")
                        
            except Exception as e:
                format_error_count += 1
                if format_error_count <= 3:
                    print(f"   ❌ Exception fixing email {i+1}: {str(e)}")
        
        print(f"\n📊 FORMATTING FIX RESULTS:")
        print(f"   ✅ Successfully fixed: {format_fixed_count} emails")
        print(f"   ❌ Errors: {format_error_count} emails")

# Now try final approaches for "Email from" issue
print(f"\n🎯 FINAL ATTEMPTS FOR 'EMAIL FROM' DISPLAY:")
print("="*45)

# Get one test email
test_email = emails[0]
test_email_id = test_email['activityid']

print(f"📧 Testing with: {test_email.get('subject', 'No Subject')[:50]}...")

# Final approaches to try
print(f"\n🧪 FINAL EXPERIMENT: Copying ALL fields from working email...")

# Get a working email from notify contact  
notify_contact_response = requests.get(
    f"{crm_base_url}/contacts?$filter=emailaddress1 eq 'notify@ringcentral.com'&$select=contactid", 
    headers=headers
)
notify_contact_id = notify_contact_response.json()['value'][0]['contactid']

working_email_response = requests.get(
    f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {notify_contact_id}&$top=1",
    headers=headers
)
working_email_id = working_email_response.json()['value'][0]['activityid']

# Get complete details of working email
working_complete = requests.get(f"{crm_base_url}/emails({working_email_id})", headers=headers).json()

# Fields to copy that might affect "Email from" display
fields_to_try = [
    'statuscode',
    'directioncode', 
    'correlationmethod',
    'deliveryprioritycode',
    'messageid',
    'baseconversationindexhash',
    'conversationindex'
]

print(f"🔧 Trying to copy key fields from working email...")

update_data = {}
for field in fields_to_try:
    working_value = working_complete.get(field)
    if working_value is not None:
        update_data[field] = working_value

# Also try setting correct statuscode (4 = Closed for received emails)
update_data['statuscode'] = 4  # Received/Closed
update_data['directioncode'] = False  # Incoming

if update_data:
    print(f"📝 Updating fields: {list(update_data.keys())}")
    
    response = requests.patch(
        f"{crm_base_url}/emails({test_email_id})",
        json=update_data,
        headers=headers
    )
    
    if response.status_code in [200, 204]:
        print(f"✅ Successfully updated test email!")
        print(f"📅 Please refresh Dynamics to check if 'Email from' display changed!")
        
        # If this works, offer to apply to all
        final_confirmation = input(f"\n🤔 If this worked, apply to all {len(emails)} emails? (yes/no): ").strip().lower()
        if final_confirmation in ['yes', 'y']:
            print(f"\n🔧 Applying final fix to all emails...")
            
            final_fixed_count = 0
            final_error_count = 0
            
            for i, email in enumerate(emails):
                email_id = email['activityid']
                
                try:
                    response = requests.patch(
                        f"{crm_base_url}/emails({email_id})",
                        json=update_data,
                        headers=headers
                    )
                    
                    if response.status_code in [200, 204]:
                        final_fixed_count += 1
                        if (i + 1) % 10 == 0:
                            print(f"   ✅ Updated {i + 1}/{len(emails)} emails...")
                    else:
                        final_error_count += 1
                        if final_error_count <= 3:
                            print(f"   ❌ Error on email {i+1}: {response.status_code}")
                            
                except Exception as e:
                    final_error_count += 1
                    if final_error_count <= 3:
                        print(f"   ❌ Exception on email {i+1}: {str(e)}")
            
            print(f"\n🎯 FINAL RESULTS:")
            print(f"   ✅ Successfully updated: {final_fixed_count} emails")
            print(f"   ❌ Errors: {final_error_count} emails")
    else:
        print(f"❌ Error updating test email: {response.status_code}")
        print(f"   Details: {response.text[:300]}")

print(f"\n💭 SUMMARY:")
print("="*15)
print("✅ HTML formatting should be restored (underscores → line breaks)")
print("❓ 'Email from' display might be:")
print("   - A read-only calculated field")
print("   - Dependent on email creation method, not updateable")
print("   - Controlled by system business logic")
print("   - Related to the original email sender authentication")
print("📅 Please refresh Dynamics to see the current state!")

if len(emails_needing_format_fix) == 0:
    print("\n✨ If no formatting issues were found, they may already be fixed!")
    print("   The main focus is now on the 'Email from' display issue.") 