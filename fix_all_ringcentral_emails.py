#!/usr/bin/env python3
"""Fix formatting and Email from issues for ALL RingCentral emails"""

import requests
import msal

# Configuration
username = "gvranjesevic@dynamique.com"
password = "#SanDiegoChicago77"
tenant_domain = "dynamique.com"
crm_base_url = "https://dynglobal.crm.dynamics.com/api/data/v9.2"
client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"

print("🔧 FIXING ALL RINGCENTRAL EMAILS")
print("="*35)
print("1. Fix underscores → HTML line breaks")
print("2. Fix Email from display issues") 
print("3. Apply to ALL emails, not just April")
print("="*35)

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

# Get ALL emails for this contact (not just April)
print(f"\n🔍 Getting ALL emails for service@ringcentral.com...")

email_response = requests.get(
    f"{crm_base_url}/emails?$filter=_regardingobjectid_value eq {contact_id}&$select=activityid,subject,description,safedescription,actualstart,statuscode,directioncode&$orderby=actualstart desc",
    headers=headers
)

if email_response.status_code != 200:
    print(f"❌ Error getting emails: {email_response.status_code}")
    exit(1)

all_emails = email_response.json().get('value', [])
print(f"📧 Found {len(all_emails)} total emails for service@ringcentral.com")

if len(all_emails) == 0:
    print("✅ No emails found!")
    exit(0)

# Analyze issues in all emails
emails_needing_format_fix = []
emails_needing_status_fix = []

for email in all_emails:
    # Check for underscore formatting issues
    description = email.get('description', '')
    if '________________________________' in description:
        emails_needing_format_fix.append(email)
    
    # Check for status/direction issues (emails that might show "Closed" in Email from)
    statuscode = email.get('statuscode')
    directioncode = email.get('directioncode')
    
    # Received emails should be: statuscode=4 (received), directioncode=false (incoming)
    if statuscode != 4 or directioncode != False:
        emails_needing_status_fix.append(email)

print(f"\n📊 ANALYSIS RESULTS:")
print(f"   📧 Total emails: {len(all_emails)}")
print(f"   🔧 Need formatting fix: {len(emails_needing_format_fix)}")
print(f"   📮 Need status fix: {len(emails_needing_status_fix)}")

# Show samples
if len(emails_needing_format_fix) > 0:
    print(f"\n📝 Sample emails needing formatting fix:")
    for i, email in enumerate(emails_needing_format_fix[:3]):
        subject = email.get('subject', 'No Subject')[:50]
        date = email.get('actualstart', 'No Date')
        print(f"   {i+1}. {date}: {subject}")

if len(emails_needing_status_fix) > 0:
    print(f"\n📝 Sample emails needing status fix:")
    for i, email in enumerate(emails_needing_status_fix[:3]):
        subject = email.get('subject', 'No Subject')[:50]
        date = email.get('actualstart', 'No Date')
        status = email.get('statuscode')
        direction = email.get('directioncode')
        print(f"   {i+1}. {date}: {subject}")
        print(f"      Status: {status}, Direction: {direction}")

# Get user confirmation
print(f"\n🤔 PROPOSED FIXES:")
print("="*20)

if len(emails_needing_format_fix) > 0:
    print(f"1. Fix formatting (underscores → HTML breaks) for {len(emails_needing_format_fix)} emails")

if len(emails_needing_status_fix) > 0:
    print(f"2. Fix status/direction for {len(emails_needing_status_fix)} emails:")
    print(f"   - Set statuscode = 4 (Received)")  
    print(f"   - Set directioncode = false (Incoming)")

total_to_fix = len(set([email['activityid'] for email in emails_needing_format_fix + emails_needing_status_fix]))
print(f"\n📧 Total unique emails to fix: {total_to_fix}")

if total_to_fix == 0:
    print("✅ No emails need fixing!")
    exit(0)

confirmation = input(f"\n🤔 Apply these fixes to all affected emails? (yes/no): ").strip().lower()
if confirmation not in ['yes', 'y']:
    print("❌ Fix cancelled")
    exit(0)

# Apply fixes
print(f"\n🔧 Applying fixes...")

fixed_count = 0
error_count = 0

# Create a comprehensive update for each email
emails_to_fix = {}

# Add formatting fixes
for email in emails_needing_format_fix:
    email_id = email['activityid']
    if email_id not in emails_to_fix:
        emails_to_fix[email_id] = {}
    
    # Fix formatting
    current_desc = email.get('description', '')
    current_safe_desc = email.get('safedescription', '')
    
    new_desc = current_desc.replace('________________________________', '<br><br>')
    new_safe_desc = current_safe_desc.replace('________________________________', '<br><br>')
    
    emails_to_fix[email_id]['description'] = new_desc
    emails_to_fix[email_id]['safedescription'] = new_safe_desc

# Add status fixes
for email in emails_needing_status_fix:
    email_id = email['activityid']
    if email_id not in emails_to_fix:
        emails_to_fix[email_id] = {}
    
    # Fix status for received emails
    emails_to_fix[email_id]['statuscode'] = 4  # Received
    emails_to_fix[email_id]['directioncode'] = False  # Incoming

# Apply all fixes
print(f"🔧 Updating {len(emails_to_fix)} emails...")

for i, (email_id, update_data) in enumerate(emails_to_fix.items()):
    try:
        response = requests.patch(
            f"{crm_base_url}/emails({email_id})",
            json=update_data,
            headers=headers
        )
        
        if response.status_code in [200, 204]:
            fixed_count += 1
            if (i + 1) % 10 == 0:
                print(f"   ✅ Fixed {i + 1}/{len(emails_to_fix)} emails...")
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

print(f"\n🎯 FINAL RESULTS:")
print(f"   ✅ Successfully fixed: {fixed_count} emails")
print(f"   ❌ Errors: {error_count} emails")

if fixed_count > 0:
    print(f"\n🎉 SUCCESS!")
    print(f"   🔧 Fixed formatting: underscores → HTML line breaks")
    print(f"   📮 Fixed status: emails should show as properly received")
    print(f"   📅 Refresh Dynamics 365 to see the changes!")
    print(f"\n   🎯 ALL RingCentral emails should now display correctly!")
    
    if len(emails_needing_status_fix) > 0:
        print(f"\n   📧 The 'Email from:' display might now show correctly")
        print(f"   📧 If still showing 'Closed', this may be a system limitation")
else:
    print(f"\n⚠️  No emails were updated")
    print(f"   💡 The issues might be:")
    print(f"      - Already fixed")
    print(f"      - System-level restrictions") 
    print(f"      - Different root cause") 